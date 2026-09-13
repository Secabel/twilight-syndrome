#!/usr/bin/env python3
"""
inventario_completo.py - Barrido exhaustivo de TODOS los graficos de tiles
(NCGR/NCBR + NCLR, componiendo por NCER cuando existe o por NSCR cuando es un
tilemap de fondo) en las carpetas de UI/eventos/pantallas de la ROM, para
detectar texto japones horneado en tiles que no pasa por el CSV.

Uso: python3 scripts/inventario_completo.py
Genera: _scratch_claude/inventario_completo/<CARPETA>_sheet_NN.png
"""
import struct
import os
import glob
from PIL import Image, ImageDraw

ROOT = "extraccion_rom/root"
OUT_DIR = "_scratch_claude/inventario_completo"
THUMB_DIR = os.path.join(OUT_DIR, "_thumbs")
os.makedirs(THUMB_DIR, exist_ok=True)

# CHR/CLD/DEBUG/MAP/MNG/MOVIE/ftc/SOUND excluidas: 0 archivos NCGR/NCBR
# (son modelos 3D .nsbmd/.nsbca o audio). Font excluida: es el set de glifos
# ya usado via CSV/fuente custom, no "texto horneado" per se.
CARPETAS = [
    "ERROR", "EV0", "EV1", "EV2", "EV3", "EV4", "EV5", "EV6", "EV9",
    "ITM", "LOGO", "MBP", "OPTION", "SAVELOAD", "STAFFROLL", "SYS", "TITLE",
    "R01", "R02", "R03", "R04", "R07", "R08", "R09", "R10", "R15", "R17",
    "R21", "R22", "R23", "R24",
]

SHAPE_SIZE_TABLE = {
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
    if magic != b'RGCN':
        return None
    char_off = next((off for off, bmagic, bsize in blocks if bmagic == b'RAHC'), None)
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
    pal_off = next((off for off, bmagic, bsize in blocks if bmagic == b'TTLP'), None)
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
    while len(colors) < 4096:
        colors.append((255, 0, 255))
    return colors


def decode_ncer(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    if magic != b'RECN':
        return None, 0
    cebk_off = next((off for off, bmagic, bsize in blocks if bmagic == b'KBEC'), None)
    if cebk_off is None:
        return None, 0
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
    w, h = SHAPE_SIZE_TABLE.get((shape, size), (8, 8))
    rot_scale = (attr0 >> 8) & 0x1
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
        'x': x, 'y': y, 'w': w, 'h': h,
        'hflip': hflip, 'vflip': vflip, 'tile_idx': tile_idx,
        'palette': palette, 'is256': bitdepth_256,
    }


def render_tile_block(tile_data, tile_idx, bpp, colors, w_tiles, h_tiles, palette_bank=0):
    """FIX (2026-09-12, portado desde scripts/ncer_decode.py tras el trabajo de
    TITLE/G02M10 y TITLE/G01M10): el offset en bytes de cada tile siempre usa
    la unidad base FIJA de 32 bytes/tile (tile_idx*32 + n*tile_bytes), nunca
    tile_idx*tile_bytes. tile_idx ya viene multiplicado por 2**tileBoundaryCode
    desde obj_geometry() -- antes de este fix, en un NCER con
    tileBoundaryCode>0 los objetos vecinos se pisaban tile por tile y el
    contenido salia mezclado/ilegible. No afectaba a los items del inventario
    (tileBoundaryCode=2 pero objetos todos del mismo tamano, donde el bug no
    se notaba facil), pero si a graficos como TITLE/G02M10 y TITLE/G01M10."""
    tile_bytes = 32 if bpp == 4 else 64
    base_off = tile_idx * 32
    img = Image.new('RGB', (w_tiles * 8, h_tiles * 8), (255, 0, 255))
    n = 0
    for ty in range(h_tiles):
        for tx in range(w_tiles):
            off = base_off + n * tile_bytes
            n += 1
            tb = tile_data[off:off + tile_bytes]
            if len(tb) < tile_bytes:
                continue
            for row in range(8):
                if bpp == 4:
                    for col4 in range(4):
                        byte = tb[row * 4 + col4]
                        lo = byte & 0xF
                        hi = (byte >> 4) & 0xF
                        img.putpixel((tx * 8 + col4 * 2, ty * 8 + row), colors[palette_bank * 16 + lo])
                        img.putpixel((tx * 8 + col4 * 2 + 1, ty * 8 + row), colors[palette_bank * 16 + hi])
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
        w_tiles = max(1, g['w'] // 8)
        h_tiles = max(1, g['h'] // 8)
        pal_bank = g['palette'] if not g['is256'] else 0
        tile_img = render_tile_block(tile_data, g['tile_idx'], bpp, colors, w_tiles, h_tiles, pal_bank)
        if g['hflip']:
            tile_img = tile_img.transpose(Image.FLIP_LEFT_RIGHT)
        if g['vflip']:
            tile_img = tile_img.transpose(Image.FLIP_TOP_BOTTOM)
        rgba = tile_img.convert('RGBA')
        pixels = rgba.load()
        # indice 0 es transparente DENTRO del banco de paleta usado por este OBJ,
        # no necesariamente el indice 0 absoluto (cada banco de 16 colores tiene
        # su propio "color de fondo" en su posicion 0).
        transp_color = colors[0] if g['is256'] else colors[pal_bank * 16]
        for yy in range(rgba.height):
            for xx in range(rgba.width):
                if pixels[xx, yy][:3] == transp_color:
                    pixels[xx, yy] = (0, 0, 0, 0)
        canvas.paste(rgba, (g['x'] - minx, g['y'] - miny), rgba)
    return canvas


def decode_nscr(path):
    data = open(path, 'rb').read()
    magic, blocks = parse_container(data)
    if magic != b'RCSN':
        return None
    scrn_off = next((off for off, bmagic, bsize in blocks if bmagic == b'NRCS'), None)
    if scrn_off is None:
        return None
    width_px, height_px = struct.unpack_from('<HH', data, scrn_off + 8)
    data_size = struct.unpack_from('<I', data, scrn_off + 16)[0]
    tile_data_start = scrn_off + 20
    raw = data[tile_data_start: tile_data_start + data_size]
    entries = []
    for i in range(0, len(raw) - 1, 2):
        v = struct.unpack_from('<H', raw, i)[0]
        tile_id = v & 0x3FF
        hflip = bool((v >> 10) & 1)
        vflip = bool((v >> 11) & 1)
        pal = (v >> 12) & 0xF
        entries.append((tile_id, hflip, vflip, pal))
    if width_px == 0 or height_px == 0:
        return None
    return {'width_px': width_px, 'height_px': height_px, 'entries': entries}


def render_nscr(nscr, ncgr, colors):
    """FIX (2026-09-13, encontrado durante la traduccion de EV0/S00/1.NCGR):
    en el branch de 8bpp, el indice de tile debe leerse dentro del BANCO de
    paleta que indica el campo `pal` de la entrada del NSCR -- colors[pal*256
    + idx] -- no colors[idx] a secas. Los NCLR "extendidos" (multi-banco,
    ~8232 bytes / 4096 colores en vez de los 256/512 bytes de un NCLR de un
    solo banco) usan hasta 16 bancos de 256 colores para fondos NSCR de 8bpp,
    y sin este offset esas pantallas se renderizaban directo en negro solido
    (invisibles a cualquier barrido -- asi fue como EV0 entero quedo marcado
    como "sin hallazgos de texto" en el inventario original, un falso
    negativo). Es retrocompatible: en un NCLR de un solo banco (256 colores)
    el campo `pal` de estas entradas siempre viene en 0, asi que
    colors[0*256+idx] == colors[idx], igual que antes."""
    bpp = 4 if ncgr['bitdepth'] == 3 else 8
    tile_bytes = 32 if bpp == 4 else 64
    tile_data = ncgr['tile_data']
    w_tiles = nscr['width_px'] // 8
    h_tiles = nscr['height_px'] // 8
    img = Image.new('RGB', (nscr['width_px'], nscr['height_px']), (30, 20, 60))
    for i, (tile_id, hflip, vflip, pal) in enumerate(nscr['entries']):
        if i >= w_tiles * h_tiles:
            break
        tx = (i % w_tiles) * 8
        ty = (i // w_tiles) * 8
        off = tile_id * tile_bytes
        tb = tile_data[off:off + tile_bytes]
        if len(tb) < tile_bytes:
            continue
        tile_img = Image.new('RGB', (8, 8))
        if bpp == 4:
            for row in range(8):
                for col4 in range(4):
                    byte = tb[row * 4 + col4]
                    lo = byte & 0xF
                    hi = (byte >> 4) & 0xF
                    tile_img.putpixel((col4 * 2, row), colors[pal * 16 + lo])
                    tile_img.putpixel((col4 * 2 + 1, row), colors[pal * 16 + hi])
        else:
            for row in range(8):
                for col in range(8):
                    idx = tb[row * 8 + col]
                    tile_img.putpixel((col, row), colors[pal * 256 + idx])
        if hflip:
            tile_img = tile_img.transpose(Image.FLIP_LEFT_RIGHT)
        if vflip:
            tile_img = tile_img.transpose(Image.FLIP_TOP_BOTTOM)
        img.paste(tile_img, (tx, ty))
    return img


def render_raw_grid(ncgr, colors):
    tile_data = ncgr['tile_data']
    bpp = 4 if ncgr['bitdepth'] == 3 else 8
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


def find_companion(gpath, ext):
    d = os.path.dirname(gpath)
    base = os.path.splitext(os.path.basename(gpath))[0]
    candidate = os.path.join(d, base + ext)
    return candidate if os.path.isfile(candidate) else None


def find_nclr(gpath):
    c = find_companion(gpath, '.NCLR')
    if c:
        return c
    others = sorted(glob.glob(os.path.join(os.path.dirname(gpath), '*.NCLR')))
    return others[0] if others else None


def render_via_ncer(ncgr, colors, ncer_path):
    bpp = 4 if ncgr['bitdepth'] == 3 else 8
    cells, tbs = decode_ncer(ncer_path)
    if cells is None:
        return None
    cell_imgs = []
    for objs in cells:
        if not objs:
            continue
        img = compose_cell(objs, ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
        if img.width > 0 and img.height > 0:
            cell_imgs.append(img)
    if not cell_imgs:
        return None
    pad = 2
    total_w = sum(im.width for im in cell_imgs) + pad * (len(cell_imgs) + 1)
    max_h = max(im.height for im in cell_imgs)
    canvas = Image.new('RGB', (total_w, max_h + pad * 2), (30, 20, 60))
    x = pad
    for im in cell_imgs:
        canvas.paste(im, (x, pad), im)
        x += im.width + pad
    return canvas


def process_file(gpath):
    """Devuelve (label, PIL.Image o None, metodo)"""
    label = os.path.relpath(gpath, ROOT).replace('\\', '/')
    nclr = find_nclr(gpath)
    if not nclr:
        return label, None, 'sin-NCLR'
    try:
        ncgr = decode_ncgr(gpath)
        colors = decode_nclr(nclr)
    except Exception as e:
        return label, None, f'error:{e}'
    if ncgr is None or colors is None:
        return label, None, 'decode-fail'

    ncer = find_companion(gpath, '.NCER')
    nscr = find_companion(gpath, '.NSCR')
    try:
        if ncer:
            img = render_via_ncer(ncgr, colors, ncer)
            if img is not None:
                return label, img, 'NCER'
        if nscr:
            nscr_d = decode_nscr(nscr)
            if nscr_d is not None:
                img = render_nscr(nscr_d, ncgr, colors)
                return label, img, 'NSCR'
        img = render_raw_grid(ncgr, colors)
        return label, img, 'raw'
    except Exception as e:
        return label, None, f'error:{e}'


def make_contactsheets(carpeta, thumbs, per_sheet=40, cols=5):
    if not thumbs:
        return 0
    cell_w, cell_h, label_h = 300, 220, 14
    n_sheets = 0
    for start in range(0, len(thumbs), per_sheet):
        batch = thumbs[start:start + per_sheet]
        rows = (len(batch) + cols - 1) // cols
        canvas = Image.new('RGB', (cols * cell_w, rows * cell_h), (15, 15, 15))
        draw = ImageDraw.Draw(canvas)
        for i, (label, img, method) in enumerate(batch):
            cx = (i % cols) * cell_w
            cy = (i // cols) * cell_h
            if img is not None:
                avail_w, avail_h = cell_w - 10, cell_h - label_h - 10
                scale = min(avail_w / img.width, avail_h / img.height)
                scale = max(scale, 1) if scale >= 1 else scale
                new_w, new_h = max(1, int(img.width * scale)), max(1, int(img.height * scale))
                resized = img.convert('RGB').resize((new_w, new_h), Image.NEAREST)
                canvas.paste(resized, (cx + 5, cy + label_h + 2))
            draw.text((cx + 5, cy + 1), f"{label} [{method}]", fill=(255, 255, 0))
        out_path = os.path.join(OUT_DIR, f"{carpeta}_sheet_{n_sheets:02d}.png")
        canvas.save(out_path)
        print(f"  guardado {out_path} ({len(batch)} items)")
        n_sheets += 1
    return n_sheets


def main():
    summary = []
    for carpeta in CARPETAS:
        base = os.path.join(ROOT, carpeta)
        if not os.path.isdir(base):
            print(f"[{carpeta}] no existe, salteando")
            continue
        files = sorted(
            glob.glob(os.path.join(base, '**', '*.NCGR'), recursive=True) +
            glob.glob(os.path.join(base, '**', '*.NCBR'), recursive=True)
        )
        print(f"[{carpeta}] {len(files)} archivos NCGR/NCBR")
        thumbs = []
        methods_count = {}
        for gpath in files:
            label, img, method = process_file(gpath)
            thumbs.append((label, img, method))
            methods_count[method] = methods_count.get(method, 0) + 1
        n_sheets = make_contactsheets(carpeta, thumbs)
        summary.append((carpeta, len(files), methods_count, n_sheets))

    print("\n=== RESUMEN ===")
    for carpeta, n, methods, n_sheets in summary:
        print(f"{carpeta}: {n} archivos, {n_sheets} hojas, metodos={methods}")


if __name__ == '__main__':
    main()
