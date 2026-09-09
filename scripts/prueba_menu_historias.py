#!/usr/bin/env python3
"""
prueba_menu_historias.py - PILOTO/HISTORICO: prueba de redibujado de UNA sola
tarjeta del menu de historias (EV9/M16-M20), usada para validar la tecnica
(paleta 8bpp negro->rojo->blanco, auto-fit de fuente) antes de comprometerse
al lote completo. YA SUPERADO por scripts/traducir_menu_historias.py, que es
el que realmente genero las 45 tarjetas en ESP/ENG - usar ese para cualquier
cosa real. Este archivo queda solo como referencia de como se llego ahi.

Uso: python3 scripts/prueba_menu_historias.py
"""
import struct
import sys
import os

sys.path.insert(0, 'scripts')
from inventario_completo import (decode_ncgr, decode_nclr, find_nclr, decode_nscr,
                                  render_nscr, parse_container)
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATHS = ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf']


def load_font(size):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_glow_text(text, w, h, font_size, blur_radius=2.2, y_offset=0, core_value=255,
                      align='center', x_pad=4):
    """Renderiza texto en un lienzo w x h de 8 bits (escala de grises), con
    nucleo solido (core_value) + resplandor por blur - coincide con la rampa
    de paleta negro->rojo->blanco de estas tarjetas. core_value controla el
    tono: ~190-200 cae en la zona roja pura de la rampa, 255 cae en blanco
    (usar 255 para el texto de pista, ~195 para titulos en rojo). align
    'left'/'center' controla el anclaje horizontal (el original suele ir
    pegado al margen izquierdo, no centrado)."""
    core = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(core)
    font = load_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if align == 'center':
        x = max(0, (w - tw) // 2) - bbox[0]
    else:
        x = x_pad - bbox[0]
    y = max(0, (h - th) // 2) - bbox[1] + y_offset
    draw.text((x, y), text, font=font, fill=core_value,
               align=('center' if align == 'center' else 'left'))
    glow = core.filter(ImageFilter.GaussianBlur(blur_radius))
    out = Image.eval(glow, lambda v: v)
    px_core = core.load()
    px_out = out.load()
    for yy in range(h):
        for xx in range(w):
            px_out[xx, yy] = max(px_out[xx, yy], px_core[xx, yy])
    return out


def gray_to_tiles(gray_img, ncgr_tile_data, nscr_entries, w_tiles_screen, tx0, ty0, tw_tiles, th_tiles):
    """Escribe gray_img (escala de grises, mismo tamano que la region en px)
    en los tiles del NSCR que caen dentro de [tx0,ty0)-[tx0+tw_tiles,ty0+th_tiles).
    Indice de paleta = valor de gris (0=negro real=indice 1, resto=valor directo)."""
    px = gray_img.load()
    touched = set()
    for ty in range(ty0, ty0 + th_tiles):
        for tx in range(tx0, tx0 + tw_tiles):
            entry_idx = ty * w_tiles_screen + tx
            tile_id, hflip, vflip, pal = nscr_entries[entry_idx]
            touched.add(tile_id)
            off = tile_id * 64
            for row in range(8):
                for col in range(8):
                    gx = (tx - tx0) * 8 + col
                    gy = (ty - ty0) * 8 + row
                    v = px[gx, gy] if 0 <= gx < gray_img.width and 0 <= gy < gray_img.height else 0
                    idx = 1 if v == 0 else v  # 0 -> negro real (indice 1), resto tal cual
                    ncgr_tile_data[off + row * 8 + col] = idx
    return touched


def patch_card(base, title_es, hint_es):
    gpath = base + '.NCGR'
    nclr = find_nclr(gpath)
    orig_ncgr_bytes = open(gpath, 'rb').read()
    ncgr = decode_ncgr(gpath)
    colors = decode_nclr(nclr)
    d = decode_nscr(base + '.NSCR')

    w_tiles = d['width_px'] // 8
    tile_data = bytearray(ncgr['tile_data'])

    # regiones en tiles, cubriendo el ANCHO TOTAL de la tarjeta (32 tiles)
    # para no dejar restos del texto original en los bordes:
    # titulo: filas 14-18 (5 tiles alto) - incluye el "No.XX" en el mismo redibujado
    # hint:   filas 19-22 (4 tiles alto)
    TITLE_REGION = (0, 14, w_tiles, 5)
    HINT_REGION = (0, 19, w_tiles, 5)  # fila 23 esta vacia en el original, se puede usar

    tx0, ty0, tw, th = TITLE_REGION
    gray = render_glow_text(title_es, tw * 8, th * 8, font_size=15, blur_radius=1.8,
                             core_value=195, align='center')
    gray_to_tiles(gray, tile_data, d['entries'], w_tiles, tx0, ty0, tw, th)

    tx0, ty0, tw, th = HINT_REGION
    gray = render_glow_text(hint_es, tw * 8, th * 8, font_size=16, blur_radius=1.4,
                             core_value=255, align='center')
    gray_to_tiles(gray, tile_data, d['entries'], w_tiles, tx0, ty0, tw, th)

    # reconstruir el NCGR completo con el tile_data parcheado
    magic, blocks = parse_container(orig_ncgr_bytes)
    char_off = next(off for off, bmagic, bsize in blocks if bmagic == b'RAHC')
    data_rel_off = struct.unpack_from('<I', orig_ncgr_bytes, char_off + 28)[0]
    tile_data_start = char_off + 8 + data_rel_off
    new_bytes = bytearray(orig_ncgr_bytes)
    new_bytes[tile_data_start:tile_data_start + len(tile_data)] = tile_data
    assert len(new_bytes) == len(orig_ncgr_bytes)

    # render antes/despues para comparar visualmente (sin tocar la ROM)
    before_img = render_nscr(d, ncgr, colors)
    ncgr_patched = dict(ncgr)
    ncgr_patched['tile_data'] = bytes(tile_data)
    after_img = render_nscr(d, ncgr_patched, colors)
    return before_img, after_img, new_bytes


if __name__ == '__main__':
    os.makedirs('_scratch_claude/revision', exist_ok=True)
    before, after, patched_bytes = patch_card(
        'extraccion_rom/root/EV9/M16/0',
        title_es='No.01  Mail de desaparicion',
        hint_es='Si conviertes todas las\nhistorias en "Gran fortuna"...',
    )
    scale = 5
    before_big = before.resize((before.width * scale, before.height * scale), Image.NEAREST)
    after_big = after.resize((after.width * scale, after.height * scale), Image.NEAREST)
    combo = Image.new('RGB', (before_big.width, before_big.height * 2 + 20), (40, 40, 40))
    combo.paste(before_big, (0, 0))
    combo.paste(after_big, (0, before_big.height + 20))
    combo.save('_scratch_claude/revision/prueba_menu_before_after.png')
    print('guardado _scratch_claude/revision/prueba_menu_before_after.png')
