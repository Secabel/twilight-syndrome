#!/usr/bin/env python3
"""
inventario_graficos.py - Decodifica todos los NCGR/NCLR de las carpetas de UI
(no las de modelos 3D de escenarios/personajes) y genera hojas de contacto
en PNG para revisar a simple vista cuales tienen texto japones dibujado.

Uso: python3 inventario_graficos.py
Genera: inventario_graficos/<carpeta>_contactsheet_N.png
"""
import struct
import os
import glob
from PIL import Image

ROOT = "extraccion_rom/root"
CARPETAS = ["SYS", "MBP", "ITM", "OPTION", "SAVELOAD", "TITLE", "LOGO", "STAFFROLL", "ERROR"]
OUT_DIR = "inventario_graficos"
os.makedirs(OUT_DIR, exist_ok=True)


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
    if magic != b'RGCN':
        return None
    char_off = None
    for off, bmagic, bsize in blocks:
        if bmagic == b'RAHC':
            char_off = off
            break
    if char_off is None:
        return None
    bitdepth = struct.unpack_from('<I', data, char_off + 12)[0]
    tile_data_size = struct.unpack_from('<I', data, char_off + 24)[0]
    data_rel_off = struct.unpack_from('<I', data, char_off + 28)[0]
    tile_data_start = char_off + 8 + data_rel_off
    tile_data = data[tile_data_start: tile_data_start + tile_data_size]
    return {'tile_data': tile_data, 'bitdepth': bitdepth}


def decode_nclr(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    if magic != b'RLCN':
        return None
    pal_off = None
    for off, bmagic, bsize in blocks:
        if bmagic == b'TTLP':
            pal_off = off
            break
    if pal_off is None:
        return None
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


def render_ncgr(ncgr_path, nclr_path):
    ncgr = decode_ncgr(ncgr_path)
    colors = decode_nclr(nclr_path)
    if ncgr is None or colors is None:
        return None
    tile_data = ncgr['tile_data']
    bitdepth = ncgr['bitdepth']
    bpp = 4 if bitdepth == 3 else 8
    tile_bytes = 32 if bpp == 4 else 64
    n_tiles = len(tile_data) // tile_bytes
    if n_tiles == 0:
        return None
    cols = min(16, n_tiles)
    rows = (n_tiles + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 8, rows * 8), (40, 40, 40))
    for t in range(n_tiles):
        tb = tile_data[t * tile_bytes:(t + 1) * tile_bytes]
        timg = Image.new('RGB', (8, 8))
        if bpp == 4:
            for row in range(8):
                for col4 in range(4):
                    if row * 4 + col4 >= len(tb):
                        continue
                    byte = tb[row * 4 + col4]
                    lo = byte & 0xF
                    hi = (byte >> 4) & 0xF
                    timg.putpixel((col4 * 2, row), colors[lo])
                    timg.putpixel((col4 * 2 + 1, row), colors[hi])
        else:
            for row in range(8):
                for col in range(8):
                    idx = row * 8 + col
                    if idx >= len(tb):
                        continue
                    timg.putpixel((col, row), colors[tb[idx]])
        x = (t % cols) * 8
        y = (t // cols) * 8
        sheet.paste(timg, (x, y))
    return sheet


def find_nclr_for(ncgr_path):
    d = os.path.dirname(ncgr_path)
    base = os.path.splitext(os.path.basename(ncgr_path))[0]
    candidate = os.path.join(d, base + '.NCLR')
    if os.path.isfile(candidate):
        return candidate
    others = glob.glob(os.path.join(d, '*.NCLR'))
    return others[0] if others else None


def main():
    all_ncgr = []
    for carpeta in CARPETAS:
        base = os.path.join(ROOT, carpeta)
        if not os.path.isdir(base):
            continue
        for path in sorted(glob.glob(os.path.join(base, '**', '*.NCGR'), recursive=True)):
            all_ncgr.append((carpeta, path))

    print(f"total NCGR candidatos: {len(all_ncgr)}")

    thumbs = []
    for carpeta, path in all_ncgr:
        nclr = find_nclr_for(path)
        if not nclr:
            continue
        try:
            sheet = render_ncgr(path, nclr)
        except Exception as e:
            print("ERROR", path, e)
            continue
        if sheet is None:
            continue
        label = f"{carpeta}/{os.path.basename(path)}"
        thumbs.append((label, sheet))

    print(f"decodificados con exito: {len(thumbs)}")

    # armar hojas de contacto: cada miniatura con su nombre, varias por imagen
    PAD = 4
    LABEL_H = 12
    MAX_W = 900
    per_sheet = 30
    for sheet_idx in range(0, len(thumbs), per_sheet):
        batch = thumbs[sheet_idx:sheet_idx + per_sheet]
        cell_w = 260
        cell_h = 90
        cols = 3
        rows = (len(batch) + cols - 1) // cols
        canvas = Image.new('RGB', (cols * cell_w, rows * cell_h), (20, 20, 20))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(canvas)
        for i, (label, img) in enumerate(batch):
            cx = (i % cols) * cell_w
            cy = (i // cols) * cell_h
            scale = min((cell_w - 10) / img.width, (cell_h - LABEL_H - 10) / img.height)
            scale = max(1, scale)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            resized = img.resize((new_w, new_h), Image.NEAREST)
            canvas.paste(resized, (cx + 5, cy + LABEL_H + 2))
            draw.text((cx + 5, cy + 1), label, fill=(255, 255, 0))
        out_path = os.path.join(OUT_DIR, f"contactsheet_{sheet_idx//per_sheet:02d}.png")
        canvas.save(out_path)
        print("guardado", out_path)


if __name__ == '__main__':
    main()
