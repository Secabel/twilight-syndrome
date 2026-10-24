#!/usr/bin/env python3
"""
traducir_saveload.py - Traduce y redibuja las 7 tarjetas de SAVELOAD/S00-S06
(NSCR 8bpp con textura granulada de fondo horneada + 2 columnas de texto
vertical: nombre del arco a la izquierda, "El N-esimo rumor" a la derecha).

A diferencia del menu de historias de EV9 (fondo negro liso), aca el fondo
tiene grano tipo VHS que hay que preservar: se copian tiles de una zona sin
texto sobre las columnas originales antes de dibujar el texto nuevo (que va
horizontal, no vertical - ver docs/hallazgos/inventario-graficos-completo.md
para el porque).

Uso: python3 scripts/traducir_saveload.py [eng] <numero_de_tarjeta ...]
"""
import struct
import sys
import os

sys.path.insert(0, 'scripts')
from inventario_completo import (decode_ncgr, decode_nclr, find_nclr, decode_nscr,
                                  render_nscr, parse_container)
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATHS = ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf']
ROOT = 'extraccion_rom/root'
W_TILES = 32
H_TILES = 24

# columnas originales de texto: el ancho real varia por tarjeta segun el
# largo del nombre del arco (verificado con deteccion de pixeles rojos en
# las 7 tarjetas: izquierda entre tx=2 y tx=11 segun el caso, derecha
# siempre tx=25-29). Se usan rangos con margen para cubrir el peor caso de
# las 7, y una zona de grano en el medio confirmada libre de rojo en todas.
LEFT_COL = range(0, 13)
RIGHT_COL = range(23, 32)
GRAIN_SRC_LEFT = range(14, 22)
GRAIN_SRC_RIGHT = range(14, 22)

TITLE_REGION = (1, 3, 30, 3)   # tx0,ty0,tw,th (en tiles) - nombre del arco
RUMOR_REGION = (1, 10, 30, 3)  # etiqueta "El N-esimo rumor"


def load_font(size):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_glow(text, w, h, font_size, core_value=230, blur=1.6, min_size=9):
    core = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(core)
    font = load_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    while (bbox[2] - bbox[0] > w - 8 or bbox[3] - bbox[1] > h - 2) and font_size > min_size:
        font_size -= 1
        font = load_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
    x = (w - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (h - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=core_value)
    glow = core.filter(ImageFilter.GaussianBlur(blur))
    out = Image.eval(glow, lambda v: v)
    pc = core.load()
    po = out.load()
    for yy in range(h):
        for xx in range(w):
            po[xx, yy] = max(po[xx, yy], pc[xx, yy])
    return out


def patch_card(base, title_text, rumor_text):
    gpath = base + '.NCGR'
    nclr = find_nclr(gpath)
    orig_ncgr_bytes = open(gpath, 'rb').read()
    ncgr = decode_ncgr(gpath)
    colors = decode_nclr(nclr)
    d = decode_nscr(base + '.NSCR')
    tile_data = bytearray(ncgr['tile_data'])
    entries = d['entries']

    def copy_tiles(dst_range, src_range):
        for ty in range(H_TILES):
            src = []
            for tx in src_range:
                tile_id, _, _, _ = entries[ty * W_TILES + tx]
                src.append(bytes(tile_data[tile_id * 64:tile_id * 64 + 64]))
            for j, tx in enumerate(dst_range):
                tile_id, _, _, _ = entries[ty * W_TILES + tx]
                off = tile_id * 64
                tile_data[off:off + 64] = src[j % len(src)]

    def paste_gray(gray, tx0, ty0, tw, th):
        px = gray.load()
        for ty in range(ty0, ty0 + th):
            for tx in range(tx0, tx0 + tw):
                tile_id, _, _, _ = entries[ty * W_TILES + tx]
                off = tile_id * 64
                for row in range(8):
                    for col in range(8):
                        gx = (tx - tx0) * 8 + col
                        gy = (ty - ty0) * 8 + row
                        v = px[gx, gy] if 0 <= gx < gray.width and 0 <= gy < gray.height else 0
                        if v > 0:
                            cur = tile_data[off + row * 8 + col]
                            tile_data[off + row * 8 + col] = max(cur, v)

    # 1) borrar ambas columnas originales preservando el grano de fondo
    copy_tiles(LEFT_COL, GRAIN_SRC_LEFT)
    copy_tiles(RIGHT_COL, GRAIN_SRC_RIGHT)

    # 2) dibujar el texto nuevo, horizontal, encima del grano
    tx0, ty0, tw, th = TITLE_REGION
    g1 = render_glow(title_text, tw * 8, th * 8, font_size=15, core_value=230)
    paste_gray(g1, tx0, ty0, tw, th)

    tx0, ty0, tw, th = RUMOR_REGION
    g2 = render_glow(rumor_text, tw * 8, th * 8, font_size=13, core_value=230)
    paste_gray(g2, tx0, ty0, tw, th)

    magic, blocks = parse_container(orig_ncgr_bytes)
    char_off = next(off for off, bmagic, bsize in blocks if bmagic == b'RAHC')
    data_rel_off = struct.unpack_from('<I', orig_ncgr_bytes, char_off + 28)[0]
    tile_data_start = char_off + 8 + data_rel_off
    new_bytes = bytearray(orig_ncgr_bytes)
    new_bytes[tile_data_start:tile_data_start + len(tile_data)] = tile_data
    assert len(new_bytes) == len(orig_ncgr_bytes)

    before_img = render_nscr(d, ncgr, colors)
    ncgr_patched = dict(ncgr)
    ncgr_patched['tile_data'] = bytes(tile_data)
    after_img = render_nscr(d, ncgr_patched, colors)
    return before_img, after_img, new_bytes


# (arco_es, rumor_es, arco_en, rumor_en) por tarjeta S00-S06
CARDS = {
    'S00': ('El Kokkuri-san del edificio viejo', 'El rumor inicial',
            'The Kokkuri-san of the Old Building', 'The Beginning Rumor'),
    'S01': ('Mail de desaparicion', 'El primer rumor',
            'Vanishing Mail', 'The First Rumor'),
    'S02': ('El anden fantasma', 'El segundo rumor',
            'The Phantom Platform', 'The Second Rumor'),
    'S03': ('Hitori Kakurenbo', 'El tercer rumor',
            'Hitori Kakurenbo', 'The Third Rumor'),
    'S04': ('El parque de diversiones de terror', 'El cuarto rumor',
            'The Scary Theme Park', 'The Fourth Rumor'),
    'S05': ('Las cien leyendas urbanas', 'El quinto rumor',
            'The Hundred Urban Legends', 'The Fifth Rumor'),
    'S06': ('Foto paranormal', 'El ultimo rumor',
            'Psychic Photograph', 'The Final Rumor'),
}


def main(idioma):
    out_root = f'assets/graficos/{idioma}/SAVELOAD'
    review_dir = '_scratch_claude/revision/lotes'
    os.makedirs(review_dir, exist_ok=True)

    thumbs = []
    for name, (title_es, rumor_es, title_en, rumor_en) in CARDS.items():
        title, rumor = (title_en, rumor_en) if idioma == 'eng' else (title_es, rumor_es)
        base = os.path.join(ROOT, 'SAVELOAD', name)
        before, after, new_bytes = patch_card(base, title, rumor)

        out_path = os.path.join(out_root, name + '.NCGR')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        open(out_path, 'wb').write(new_bytes)
        print(f'{name}: guardado -> {out_path}')
        thumbs.append((name, before, after))

    scale = 3
    cw, ch = 256 * scale, 192 * scale
    label_h = 16
    canvas = Image.new('RGB', (cw * 2 + 20, (ch + label_h + 10) * len(thumbs)), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    y = 0
    for name, before, after in thumbs:
        b = before.resize((cw, ch), Image.NEAREST)
        a = after.resize((cw, ch), Image.NEAREST)
        draw.text((5, y), name + ' - ANTES', fill=(255, 255, 0))
        draw.text((cw + 15, y), name + ' - DESPUES', fill=(255, 255, 0))
        canvas.paste(b, (0, y + label_h))
        canvas.paste(a, (cw + 20, y + label_h))
        y += ch + label_h + 10
    out_sheet = os.path.join(review_dir, f'saveload_{idioma}.png')
    canvas.save(out_sheet)
    print('hoja de revision guardada en', out_sheet)


if __name__ == '__main__':
    idioma = 'eng' if 'eng' in sys.argv[1:] else 'esp'
    main(idioma)
