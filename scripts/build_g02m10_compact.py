#!/usr/bin/env python3
"""
build_g02m10_compact.py - Reconstruye TITLE/G02M10.NCGR/.NCER con las N tarjetas
traducidas, eliminando los datos de tiles japoneses "muertos" (no referenciados)
y manteniendo la alineacion de 8 tiles requerida por tile_boundary_shift.

Uso: python3 build_g02m10_compact.py <lang> <N> <out_dir>
  lang: esp | eng
  N: cantidad de tarjetas traducidas (1-7)
  out_dir: carpeta de salida para G02M10.NCGR/.NCER + previews
"""
import struct
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from ncer_decode import (parse_container, decode_ncgr, decode_nclr, decode_ncer,
                          obj_geometry, compose_cell)
from PIL import Image

ORIG_BASE = "extraccion_rom/root/TITLE/G02M10"
CARD_BLOCK = 16384
ALIGN_TILES = 8


def read_ncer_raw(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    assert magic == b'RECN'
    cebk_off = next(off for off, bmagic, bsize in blocks if bmagic == b'KBEC')
    hdr_off = cebk_off + 8
    cell_count, cell_type = struct.unpack_from('<HH', data, hdr_off)
    boundary_code = struct.unpack_from('<I', data, hdr_off + 8)[0]
    tbs = boundary_code if boundary_code in (0, 1, 2, 3) else 0
    entry_size = 16 if (cell_type & 1) else 8
    cell_array_off = hdr_off + 24
    cells = []
    for i in range(cell_count):
        off = cell_array_off + i * entry_size
        obj_count, _pad = struct.unpack_from('<HH', data, off)
        obj_offset = struct.unpack_from('<I', data, off + 4)[0]
        cells.append((obj_count, obj_offset))
    obj_array_off = cell_array_off + cell_count * entry_size
    cell_objs = []
    for obj_count, obj_offset in cells:
        base = obj_array_off + obj_offset
        objs = []
        for j in range(obj_count):
            attr0, attr1, attr2 = struct.unpack_from('<HHH', data, base + j * 6)
            objs.append([attr0, attr1, attr2])
        cell_objs.append(objs)
    return data, tbs, cell_objs, entry_size, cell_array_off, obj_array_off, cebk_off


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "esp"
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    out_dir = sys.argv[3] if len(sys.argv) > 3 else f"_scratch_claude/{lang}_full{N}_clean"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "preview"), exist_ok=True)

    trans_base = f"assets/graficos/{lang}/TITLE_DISABLED/G02M10"

    orig_ncgr = decode_ncgr(ORIG_BASE + ".NCGR")
    orig_tile_data = orig_ncgr['tile_data']
    orig_tile_data_len = len(orig_tile_data)
    bpp = 4 if orig_ncgr['bitdepth'] == 3 else 8

    trans_ncgr = decode_ncgr(trans_base + ".NCGR")
    trans_tile_data = trans_ncgr['tile_data']

    orig_cells, tbs = decode_ncer(ORIG_BASE + ".NCER")

    (trans_data, trans_tbs, trans_cell_objs, entry_size,
     cell_array_off, obj_array_off, cebk_off) = read_ncer_raw(trans_base + ".NCER")
    assert trans_tbs == tbs

    replaced_cells = list(range(0, N)) + list(range(14, 14 + N))
    kept_cells = [c for c in range(len(orig_cells)) if c not in replaced_cells]

    needed = []
    seen = set()
    for ci in kept_cells:
        for o in orig_cells[ci]:
            g = obj_geometry(*o, tile_boundary_shift=tbs)
            wt, ht = g['w'] // 8, g['h'] // 8
            key = (g['tile_idx'], wt * ht)
            if key not in seen:
                seen.add(key)
                needed.append(key)
    needed.sort()

    new_tile_data = bytearray()
    remap = {}
    for (old_start, ntiles) in needed:
        cur_tiles = len(new_tile_data) // 32
        pad = (-cur_tiles) % ALIGN_TILES
        new_tile_data += bytes(pad * 32)
        new_start = len(new_tile_data) // 32
        remap[old_start] = new_start
        new_tile_data += orig_tile_data[old_start * 32: (old_start + ntiles) * 32]

    cur_tiles = len(new_tile_data) // 32
    pad = (-cur_tiles) % ALIGN_TILES
    new_tile_data += bytes(pad * 32)
    new_cards_tile_start = len(new_tile_data) // 32
    new_blocks = trans_tile_data[orig_tile_data_len: orig_tile_data_len + CARD_BLOCK * N]
    assert len(new_blocks) == CARD_BLOCK * N, f"faltan datos traducidos: {len(new_blocks)} != {CARD_BLOCK*N}"
    new_tile_data += new_blocks

    # Reconstruir NCER: para celdas reemplazadas, usar objs de la version traducida
    # remapeando tile_idx relativo a new_cards_tile_start; para celdas mantenidas,
    # usar objs originales remapeados via `remap`.
    final_cell_objs = []
    trans_cards_tile_start = orig_tile_data_len // 32  # offset donde empiezan las tarjetas en el trans ncgr
    for ci in range(len(orig_cells)):
        if ci in replaced_cells:
            objs = [list(o) for o in trans_cell_objs[ci]]
            for o in objs:
                g_tile_idx = (o[2] & 0x3FF) << tbs  # unidades reales de tile
                delta = g_tile_idx - trans_cards_tile_start  # offset real dentro del bloque de tarjeta
                new_real_tile_idx = new_cards_tile_start + delta  # unidades reales de tile
                # reconstruir attr2 preservando bits altos (palette)
                new_tile_idx_raw = new_real_tile_idx >> tbs if tbs else new_real_tile_idx
                o[2] = (o[2] & ~0x3FF) | (new_tile_idx_raw & 0x3FF)
            final_cell_objs.append(objs)
        else:
            objs = [list(o) for o in orig_cells[ci]]
            for o in objs:
                old_tile_idx = (o[2] & 0x3FF) << tbs
                new_tile_idx = remap[old_tile_idx]
                new_tile_idx_raw = new_tile_idx >> tbs if tbs else new_tile_idx
                o[2] = (o[2] & ~0x3FF) | (new_tile_idx_raw & 0x3FF)
            final_cell_objs.append(objs)

    # Serializar obj array + cell array
    obj_bytes = bytearray()
    cell_entries = []
    for objs in final_cell_objs:
        offset_into_objs = len(obj_bytes)
        cell_entries.append((len(objs), offset_into_objs))
        for (a0, a1, a2) in objs:
            obj_bytes += struct.pack('<HHH', a0, a1, a2)

    cell_array_bytes = bytearray()
    for (obj_count, obj_offset) in cell_entries:
        if entry_size == 16:
            cell_array_bytes += struct.pack('<HHIiiii', obj_count, 0, obj_offset, 0, 0, 0, 0)[:16]
        else:
            cell_array_bytes += struct.pack('<HHI', obj_count, 0, obj_offset)

    # Reconstruir bloque KBEC completo
    header_fixed = trans_data[cebk_off + 8: cell_array_off]  # 24 bytes: cellCount..res
    new_kbec_body = bytes(header_fixed) + bytes(cell_array_bytes) + bytes(obj_bytes)
    # los bloques Nitro se alinean a 4 bytes; el archivo original trae padding al
    # final del cuerpo de KBEC para esto (verificado: 145 objs*6 + 232 + 24 = 1126,
    # pero el bloque fuente declara 1128 de contenido -> 2 bytes de padding al final)
    pad_align = (-(8 + len(new_kbec_body))) % 4
    new_kbec_body += bytes(pad_align)
    new_kbec_size = 8 + len(new_kbec_body)
    new_kbec_block = b'KBEC' + struct.pack('<I', new_kbec_size) + new_kbec_body

    # Reunir el resto de bloques del NCER sin tocar (todo lo que no sea KBEC)
    _, all_blocks = parse_container(trans_data)
    out = bytearray()
    out += trans_data[0:16]  # header generico (magic, bom, ver, filesize, headersize, numblocks) - se corrige despues
    new_blocks_bytes = []
    for off, bmagic, bsize in all_blocks:
        if bmagic == b'KBEC':
            new_blocks_bytes.append(new_kbec_block)
        else:
            new_blocks_bytes.append(trans_data[off: off + bsize])
    body = b''.join(new_blocks_bytes)
    total_size = 16 + len(body)
    header = trans_data[0:4] + struct.pack('<HHIHH',
                                            struct.unpack_from('<H', trans_data, 4)[0],
                                            struct.unpack_from('<H', trans_data, 6)[0],
                                            total_size, 16, len(all_blocks))
    new_ncer_bytes = header + body

    # Reconstruir NCGR: reemplazar tile_data en el bloque RAHC
    _, ncgr_blocks = parse_container(trans_ncgr_full := open(trans_base + ".NCGR", 'rb').read())
    rahc_off = next(off for off, bmagic, bsize in ncgr_blocks if bmagic == b'RAHC')
    data_rel_off = struct.unpack_from('<I', trans_ncgr_full, rahc_off + 28)[0]
    tile_data_start = rahc_off + 8 + data_rel_off
    rahc_header = trans_ncgr_full[rahc_off + 8: tile_data_start]
    new_rahc_body = bytearray(rahc_header) + bytearray(new_tile_data)
    # actualizar tile_data_size (offset +24 relativo a rahc_off, o sea +16 en rahc_header)
    struct.pack_into('<I', new_rahc_body, 16, len(new_tile_data))
    new_rahc_size = 8 + len(new_rahc_body)
    new_rahc_block = b'RAHC' + struct.pack('<I', new_rahc_size) + bytes(new_rahc_body)

    ncgr_out_blocks = []
    for off, bmagic, bsize in ncgr_blocks:
        if bmagic == b'RAHC':
            ncgr_out_blocks.append(new_rahc_block)
        else:
            ncgr_out_blocks.append(trans_ncgr_full[off:off + bsize])
    ncgr_body = b''.join(ncgr_out_blocks)
    ncgr_total_size = 16 + len(ncgr_body)
    ncgr_header = trans_ncgr_full[0:4] + struct.pack('<HHIHH',
                                                      struct.unpack_from('<H', trans_ncgr_full, 4)[0],
                                                      struct.unpack_from('<H', trans_ncgr_full, 6)[0],
                                                      ncgr_total_size, 16, len(ncgr_blocks))
    new_ncgr_bytes = ncgr_header + ncgr_body

    out_ncgr_path = os.path.join(out_dir, "G02M10.NCGR")
    out_ncer_path = os.path.join(out_dir, "G02M10.NCER")
    open(out_ncgr_path, 'wb').write(new_ncgr_bytes)
    open(out_ncer_path, 'wb').write(new_ncer_bytes)

    print(f"lang={lang} N={N}")
    print(f"tile_data nuevo: {len(new_tile_data)} (orig={orig_tile_data_len}, trans_completo={len(trans_tile_data)})")
    print(f"NCGR: {len(new_ncgr_bytes)}  NCER: {len(new_ncer_bytes)}")

    # Verificacion: releer y chequear rangos fuera de rango, generar previews
    v_ncgr = decode_ncgr(out_ncgr_path)
    v_cells, v_tbs = decode_ncer(out_ncer_path)
    max_tile = len(v_ncgr['tile_data']) // 32
    fuera_de_rango = set()
    for ci, objs in enumerate(v_cells):
        for o in objs:
            g = obj_geometry(*o, tile_boundary_shift=v_tbs)
            wt, ht = g['w'] // 8, g['h'] // 8
            if g['tile_idx'] + wt * ht > max_tile:
                fuera_de_rango.add((ci, g['tile_idx'], wt * ht, max_tile))
    print("fuera de rango:", fuera_de_rango)

    nclr_path = ORIG_BASE + ".NCLR"
    colors = decode_nclr(nclr_path)
    interesting = list(range(0, N)) + [14, 20, 25, 28]
    for ci in interesting:
        if ci >= len(v_cells) or not v_cells[ci]:
            continue
        img = compose_cell(v_cells[ci], v_ncgr['tile_data'], colors, bpp,
                            tile_boundary_shift=v_tbs, force_palette_bank=2)
        bg = Image.new('RGB', img.size, (30, 20, 60))
        bg.paste(img, (0, 0), img)
        scale = 6
        bg = bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST)
        bg.save(os.path.join(out_dir, "preview", f"cell{ci}.png"))
    print("previews listas")


if __name__ == '__main__':
    main()
