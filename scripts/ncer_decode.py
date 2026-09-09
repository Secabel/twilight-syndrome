#!/usr/bin/env python3
"""
ncer_decode.py - Decodifica NCER (cell bank) + NCGR (tiles) + NCLR (paleta)
usando el formato OAM estandar GBA/NDS (attr0/attr1/attr2) para componer la
imagen real (orden/posicion correctos) de un item del inventario.

Uso: python3 ncer_decode.py I00S10 I01S10 I02S10
"""
import struct
import sys
import os
from PIL import Image

ROOT = "extraccion_rom/root/ITM/2D"
OUT_DIR = "_scratch_claude"
os.makedirs(OUT_DIR, exist_ok=True)

SHAPE_SIZE_TABLE = {
    # (shape, size) -> (width, height)
    (0, 0): (8, 8),     (0, 1): (16, 16),  (0, 2): (32, 32),  (0, 3): (64, 64),
    (1, 0): (16, 8),    (1, 1): (32, 8),   (1, 2): (32, 16),  (1, 3): (64, 32),
    (2, 0): (8, 16),    (2, 1): (8, 32),   (2, 2): (16, 32),  (2, 3): (32, 64),
}


def parse_container(data):
    magic = data[0:4]
    bom, ver, filesize, headersize, numblocks = struct.unpack_from('<HHIHH', data, 4)
    pos = headersize
    blocks = []
    for i in range(numblocks):
        bmagic = data[pos:pos + 4]
        bsize = struct.unpack_from('<I', data, pos + 4)[0]
        blocks.append((pos, bmagic, bsize))
        pos += bsize
    return magic, blocks


def decode_ncgr(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    assert magic == b'RGCN', f"NCGR magic invalido: {magic}"
    char_off = next(off for off, bmagic, bsize in blocks if bmagic == b'RAHC')
    bitdepth = struct.unpack_from('<I', data, char_off + 12)[0]
    tile_data_size = struct.unpack_from('<I', data, char_off + 24)[0]
    data_rel_off = struct.unpack_from('<I', data, char_off + 28)[0]
    tile_data_start = char_off + 8 + data_rel_off
    tile_data = data[tile_data_start: tile_data_start + tile_data_size]
    return {'tile_data': tile_data, 'bitdepth': bitdepth}


def decode_nclr(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    assert magic == b'RLCN', f"NCLR magic invalido: {magic}"
    pal_off = next(off for off, bmagic, bsize in blocks if bmagic == b'TTLP')
    palsize = struct.unpack_from('<I', data, pal_off + 16)[0]
    pal_data_start = pal_off + 8 + 16
    pal_bytes = data[pal_data_start: pal_data_start + palsize]
    colors = []
    for i in range(0, len(pal_bytes), 2):
        if i + 1 >= len(pal_bytes):
            break
        v = struct.unpack_from('<H', pal_bytes, i)[0]
        r = (v & 0x1F) * 8
        g = ((v >> 5) & 0x1F) * 8
        b = ((v >> 10) & 0x1F) * 8
        colors.append((r, g, b))
    while len(colors) < 256:
        colors.append((255, 0, 255))
    return colors


def decode_ncer(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    assert magic == b'RECN', f"NCER magic invalido: {magic}"
    cebk_off = next(off for off, bmagic, bsize in blocks if bmagic == b'KBEC')
    # bloque KBEC: magic(4)+size(4) luego header fijo de 24 bytes:
    # cellCount(u16) cellType(u16) cellDataOffsetSelf(u32) boundary/mappingType(u32) res(u32) res(u32)
    hdr_off = cebk_off + 8
    cell_count, cell_type = struct.unpack_from('<HH', data, hdr_off)
    boundary_code = struct.unpack_from('<I', data, hdr_off + 8)[0]
    tile_boundary_shift = boundary_code if boundary_code in (0, 1, 2, 3) else 0
    entry_size = 16 if (cell_type & 1) else 8
    cell_array_off = hdr_off + 24
    cells = []
    for i in range(cell_count):
        off = cell_array_off + i * entry_size
        obj_count, _pad = struct.unpack_from('<HH', data, off)
        obj_offset = struct.unpack_from('<I', data, off + 4)[0]
        cells.append((obj_count, obj_offset))
    obj_array_off = cell_array_off + cell_count * entry_size
    all_cells_objs = []
    for obj_count, obj_offset in cells:
        objs = []
        base = obj_array_off + obj_offset
        for j in range(obj_count):
            attr0, attr1, attr2 = struct.unpack_from('<HHH', data, base + j * 6)
            objs.append((attr0, attr1, attr2))
        all_cells_objs.append(objs)
    return all_cells_objs, tile_boundary_shift


def obj_geometry(attr0, attr1, attr2, tile_boundary_shift=0):
    shape = (attr0 >> 14) & 0x3
    size = (attr1 >> 14) & 0x3
    w, h = SHAPE_SIZE_TABLE[(shape, size)]
    rot_scale = (attr0 >> 8) & 0x1
    double = bool(rot_scale and ((attr0 >> 9) & 0x1))
    y = attr0 & 0xFF
    if y >= 128:
        y -= 256
    x = attr1 & 0x1FF
    if x >= 256:
        x -= 512
    hflip = vflip = False
    if not rot_scale:
        hflip = bool((attr1 >> 12) & 0x1)
        vflip = bool((attr1 >> 13) & 0x1)
    tile_idx = (attr2 & 0x3FF) << tile_boundary_shift
    palette = (attr2 >> 12) & 0xF
    bitdepth_256 = bool((attr0 >> 13) & 0x1)
    return {
        'x': x, 'y': y, 'w': w, 'h': h, 'double': double,
        'hflip': hflip, 'vflip': vflip, 'tile_idx': tile_idx,
        'palette': palette, 'is256': bitdepth_256,
    }


def render_tile(tile_data, tile_idx, bpp, colors, w_tiles, h_tiles, palette_bank=0):
    """Renderiza un bloque de w_tiles x h_tiles tiles de 8x8 empezando en tile_idx,
    en orden de fila (estandar 'character mapping 1D')."""
    tile_bytes = 32 if bpp == 4 else 64
    img = Image.new('RGB', (w_tiles * 8, h_tiles * 8), (255, 0, 255))
    n = 0
    for ty in range(h_tiles):
        for tx in range(w_tiles):
            t = tile_idx + n
            n += 1
            off = t * tile_bytes
            tb = tile_data[off:off + tile_bytes]
            if len(tb) < tile_bytes:
                continue
            for row in range(8):
                if bpp == 4:
                    for col4 in range(4):
                        byte = tb[row * 4 + col4]
                        lo = byte & 0xF
                        hi = (byte >> 4) & 0xF
                        pidx_lo = palette_bank * 16 + lo
                        pidx_hi = palette_bank * 16 + hi
                        img.putpixel((tx * 8 + col4 * 2, ty * 8 + row), colors[pidx_lo])
                        img.putpixel((tx * 8 + col4 * 2 + 1, ty * 8 + row), colors[pidx_hi])
                else:
                    for col in range(8):
                        idx = tb[row * 8 + col]
                        img.putpixel((tx * 8 + col, ty * 8 + row), colors[idx])
    return img


def compose_cell(objs, tile_data, colors, bpp, tile_boundary_shift=0, transparent_idx=0):
    geoms = [obj_geometry(*o, tile_boundary_shift=tile_boundary_shift) for o in objs]
    xs0 = [g['x'] for g in geoms]
    ys0 = [g['y'] for g in geoms]
    xs1 = [g['x'] + g['w'] for g in geoms]
    ys1 = [g['y'] + g['h'] for g in geoms]
    minx, miny = min(xs0), min(ys0)
    maxx, maxy = max(xs1), max(ys1)
    canvas = Image.new('RGBA', (maxx - minx, maxy - miny), (0, 0, 0, 0))
    for g in geoms:
        w_tiles = g['w'] // 8
        h_tiles = g['h'] // 8
        tile_img = render_tile(tile_data, g['tile_idx'], bpp, colors, w_tiles, h_tiles, g['palette'] if g['is256'] is False else 0)
        if g['hflip']:
            tile_img = tile_img.transpose(Image.FLIP_LEFT_RIGHT)
        if g['vflip']:
            tile_img = tile_img.transpose(Image.FLIP_TOP_BOTTOM)
        rgba = tile_img.convert('RGBA')
        pixels = rgba.load()
        transp_color = colors[transparent_idx]
        for yy in range(rgba.height):
            for xx in range(rgba.width):
                if pixels[xx, yy][:3] == transp_color:
                    pixels[xx, yy] = (0, 0, 0, 0)
        canvas.paste(rgba, (g['x'] - minx, g['y'] - miny), rgba)
    return canvas


def main():
    names = sys.argv[1:] or ["I00S10", "I01S10", "I02S10"]
    for name in names:
        base = os.path.join(ROOT, name)
        ncgr = decode_ncgr(base + ".NCGR")
        colors = decode_nclr(base + ".NCLR")
        cells, tbs = decode_ncer(base + ".NCER")
        print(f"  tile_boundary_shift={tbs}")
        bpp = 4 if ncgr['bitdepth'] == 3 else 8
        print(f"{name}: {len(cells)} celdas")
        for ci, objs in enumerate(cells):
            print(f"  celda {ci}: {len(objs)} objs")
            for oi, o in enumerate(objs):
                g = obj_geometry(*o, tile_boundary_shift=tbs)
                print(f"    obj{oi}: x={g['x']} y={g['y']} w={g['w']} h={g['h']} "
                      f"tile={g['tile_idx']} pal={g['palette']} hflip={g['hflip']} vflip={g['vflip']}")
            if not objs:
                continue
            img = compose_cell(objs, ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
            # fondo oscuro tipo el del juego para poder comparar visualmente el texto
            bg = Image.new('RGB', img.size, (30, 20, 60))
            bg.paste(img, (0, 0), img)
            scale = 6
            bg = bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST)
            out_path = os.path.join(OUT_DIR, f"{name}_cell{ci}.png")
            bg.save(out_path)
            print(f"    -> {out_path} ({img.width}x{img.height})")


if __name__ == '__main__':
    main()
