#!/usr/bin/env python3
"""
traducir_menu_historias.py - Traduce y redibuja en lote las tarjetas del menu
de "historias" (EV9/M16-M20, formato NSCR/8bpp con rampa negro->rojo->blanco).
Guarda los NCGR parcheados en assets/graficos/<idioma>/<misma ruta que en la
ROM>, y arma una hoja de contacto antes/despues por lote para revisar antes
de aplicar el siguiente.

Uso: python3 scripts/traducir_menu_historias.py
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
TITLE_REGION = (0, 14, 32, 5)
HINT_REGION = (0, 19, 32, 5)


def load_font(size):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_glow_text(text, w, h, font_size, blur_radius=1.6, y_offset=0, core_value=255, align='center',
                      auto_fit=True, min_size=9, pad=6):
    core = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(core)
    font = load_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    if auto_fit:
        while (bbox[2] - bbox[0] > w - pad * 2 or bbox[3] - bbox[1] > h - 2) and font_size > min_size:
            font_size -= 1
            font = load_font(font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if align == 'center':
        x = max(0, (w - tw) // 2) - bbox[0]
    else:
        x = 4 - bbox[0]
    y = max(0, (h - th) // 2) - bbox[1] + y_offset
    draw.text((x, y), text, font=font, fill=core_value, align=('center' if align == 'center' else 'left'))
    glow = core.filter(ImageFilter.GaussianBlur(blur_radius))
    out = Image.eval(glow, lambda v: v)
    px_core = core.load()
    px_out = out.load()
    for yy in range(h):
        for xx in range(w):
            px_out[xx, yy] = max(px_out[xx, yy], px_core[xx, yy])
    return out


def gray_to_tiles(gray_img, ncgr_tile_data, nscr_entries, w_tiles_screen, tx0, ty0, tw_tiles, th_tiles):
    px = gray_img.load()
    for ty in range(ty0, ty0 + th_tiles):
        for tx in range(tx0, tx0 + tw_tiles):
            entry_idx = ty * w_tiles_screen + tx
            tile_id, hflip, vflip, pal = nscr_entries[entry_idx]
            off = tile_id * 64
            for row in range(8):
                for col in range(8):
                    gx = (tx - tx0) * 8 + col
                    gy = (ty - ty0) * 8 + row
                    v = px[gx, gy] if 0 <= gx < gray_img.width and 0 <= gy < gray_img.height else 0
                    idx = 1 if v == 0 else v
                    ncgr_tile_data[off + row * 8 + col] = idx


def patch_card(base, title_es, hint_es, title_size=15, hint_size=16):
    gpath = base + '.NCGR'
    nclr = find_nclr(gpath)
    orig_ncgr_bytes = open(gpath, 'rb').read()
    ncgr = decode_ncgr(gpath)
    colors = decode_nclr(nclr)
    d = decode_nscr(base + '.NSCR')
    w_tiles = d['width_px'] // 8
    tile_data = bytearray(ncgr['tile_data'])

    tx0, ty0, tw, th = TITLE_REGION
    gray = render_glow_text(title_es, tw * 8, th * 8, font_size=title_size, blur_radius=1.8,
                             core_value=195, align='center')
    gray_to_tiles(gray, tile_data, d['entries'], w_tiles, tx0, ty0, tw, th)

    tx0, ty0, tw, th = HINT_REGION
    gray = render_glow_text(hint_es, tw * 8, th * 8, font_size=hint_size, blur_radius=1.4,
                             core_value=255, align='center')
    gray_to_tiles(gray, tile_data, d['entries'], w_tiles, tx0, ty0, tw, th)

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


def wrap2(text, width):
    """Corta un texto en como maximo 2 lineas, partiendo en el espacio mas
    cercano a la mitad si hace falta."""
    if len(text) <= width:
        return text
    words = text.split(' ')
    l1, l2 = [], []
    cur = l1
    total = 0
    for w in words:
        if cur is l1 and total + len(w) > width and l2 == [] and len(' '.join(l1)) > 0:
            cur = l2
            total = 0
        cur.append(w)
        total += len(w) + 1
    return '\n'.join([' '.join(l1), ' '.join(l2)]) if l2 else ' '.join(l1)


# ---- LOTE 1: EV9/M16/0 - M16/9 (ESP) ----
LOTE_1 = [
    ('EV9/M16/0', 'No.01  Mail de desaparicion',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M16/1', 'No.02  Falta uno mas',
     'Donde hiciste el\n"Kokkuri-san"?'),
    ('EV9/M16/2', 'No.03  El misterio del zorro',
     'Revisaste bien la foto\nque encontraste?'),
    ('EV9/M16/3', 'No.04  El error de Reika',
     'No te equivocaste\nen la cancion?'),
    ('EV9/M16/4', 'No.05  Paradero desconocido',
     'Si hubieras hablado\ncon el espiritu...'),
    ('EV9/M16/5', 'No.06  Hacia la oscuridad',
     'Donde hiciste el\n"Kokkuri-san"?'),
    ('EV9/M16/6', 'No.07  Nuestro futuro',
     'Si hubieras hablado con el espiritu...\nEn el Kokkuri-san, concentrate en el dedo'),
    ('EV9/M16/7', 'No.08  El profesor de guardia',
     'Si llegaste hasta\naca, no dudes'),
    ('EV9/M16/8', 'No.01  El anden fantasma',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M16/9', 'No.02  Un pesar sin resolver',
     'Hablaste bien con tu amiga?\nHiciste lo correcto en el santuario?'),
]

# ---- LOTE 2: EV9/M17/0 - M17/9 (ESP) ----
LOTE_2 = [
    ('EV9/M17/0', 'No.03  Y quede atras',
     'Escuchaste al anciano\nhasta el final?'),
    ('EV9/M17/1', 'No.04  La puerta abierta',
     'No soltaste la mano\ndel casillero?'),
    ('EV9/M17/2', 'No.05  La verdad que no pude contar',
     'No te quedes\nen el tren'),
    ('EV9/M17/3', 'No.06  Me rendi',
     'Escuchaste\nal anciano?'),
    ('EV9/M17/4', 'No.01  Hitori Kakurenbo',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M17/5', 'No.02  Logre escapar, pero...',
     'Respetaste las reglas\ndel escondite?'),
    ('EV9/M17/6', 'No.03  Juntos hasta el amanecer',
     'Si hubieras confiado\nmas en tu amiga...'),
    ('EV9/M17/7', 'No.04  Fui salvada',
     'Si hubieras resistido\nun poco mas...'),
    ('EV9/M17/8', 'No.05  Una noche divertida',
     'Respetaste las reglas\ndel escondite?'),
    ('EV9/M17/9', 'No.06  El misterio sin resolver',
     'El escondite todavia\nno termino'),
]

# ---- LOTE 3: EV9/M18/0 - M18/9 (ESP) ----
LOTE_3 = [
    ('EV9/M18/0', 'No.07  Quemados juntos',
     'Que habia\nen el video...?'),
    ('EV9/M18/1', 'No.08  Gana "yo"',
     'Total, tu rival\nes un "espiritu"...'),
    ('EV9/M18/2', 'No.09  Un grito desde el techo',
     'Si hubieras confiado mas en tu amiga...\nRevisaste el contenido del video?'),
    ('EV9/M18/3', 'No.10  Sin poder resistir',
     'Que habia en el video...?\nResisti hasta el final'),
    ('EV9/M18/4', 'No.11  La garganta desgarrada',
     'Actuaste con calma,\nsin asustarte?'),
    ('EV9/M18/5', 'No.12  El modelo de la leyenda',
     'No olvides lo que\ndijo el profesor'),
    ('EV9/M18/6', 'No.13  Segui los pasos, pero...',
     'Hiciste el escondite\nrealmente sola?'),
    ('EV9/M18/7', 'No.14  Gana el oni',
     'Respetaste las reglas\ndel escondite?'),
    ('EV9/M18/8', 'No.15  Kokkuri-san, Kokkuri-san',
     'Sin depender\ndel Kokkuri-san...'),
    ('EV9/M18/9', 'No.16  Bajo la cama',
     'Asustarse demasiado\ntambien trae desgracia'),
]

# ---- LOTE 4: EV9/M19/0 - M19/9 (ESP) ----
LOTE_4 = [
    ('EV9/M19/0', 'No.11  La garganta desgarrada',
     'Actuaste con calma,\nsin asustarte?'),
    ('EV9/M19/1', 'No.01  El parque de diversiones de terror',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M19/2', 'No.02  El fin del sueno',
     'Elegi con cuidado\nInvitaste a tu amiga?'),
    ('EV9/M19/3', 'No.03  Igual que en el sueno',
     'Revisaste todo el parque a fondo?\nElegi con cuidado'),
    ('EV9/M19/4', 'No.04  El sueno del que no despierto',
     'Cuidado con\nel payaso'),
    ('EV9/M19/5', 'No.05  Que el sueno siga siendo sueno',
     'Confiaste en el consejo\nde tu amiga?'),
    ('EV9/M19/6', 'No.01  Las cien leyendas urbanas',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M19/7', 'No.02  El fin de las cien historias',
     'Miraste bien el arbol del cruce?\nRecorriste todo el edificio escolar?'),
    ('EV9/M19/8', 'No.03  El deseo no se cumplio',
     'No olvides el\njuego de palabras'),
    ('EV9/M19/9', 'No.04  Poseida',
     'Si hubieras resistido\nun poco mas...'),
]

# ---- LOTE 5: EV9/M20/0 - M20/4 (ESP) ----
LOTE_5 = [
    ('EV9/M20/0', 'No.05  Nadie en la azotea',
     'Estara bien\nmi amiga?'),
    ('EV9/M20/1', 'No.06  Con el amanecer',
     'No olvides las\npalabras de tu amiga'),
    ('EV9/M20/2', 'No.07  Hanako-san del bano',
     'Responde a los golpes con cuidado\nRecorriste todo el edificio escolar?'),
    ('EV9/M20/3', 'No.01  El Kokkuri-san del edificio viejo',
     'Si conviertes todas las\nhistorias en "Gran fortuna"...'),
    ('EV9/M20/4', 'No.01  Las cien leyendas urbanas',
     ''),
]

# ===================== VERSION INGLESA (ENG) =====================
# Mismas 45 tarjetas, mismo contenido en ingles - misma tecnica de render
# (paleta, glow, tipografia, tamano) via el parametro idioma='eng'.

LOTE_1_EN = [
    ('EV9/M16/0', 'No.01  Vanishing Mail',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M16/1', 'No.02  One Person Short',
     'Where did you do the\n"Kokkuri-san"?'),
    ('EV9/M16/2', 'No.03  The Fox\'s Mystery',
     'Did you check the photo\nyou found carefully?'),
    ('EV9/M16/3', 'No.04  Reika\'s Mistake',
     'Didn\'t you get\nthe song wrong?'),
    ('EV9/M16/4', 'No.05  Unknown Whereabouts',
     'If only you had talked\nwith the spirit...'),
    ('EV9/M16/5', 'No.06  Into the Darkness',
     'Where did you do the\n"Kokkuri-san"?'),
    ('EV9/M16/6', 'No.07  Our Future',
     'If only you had talked with the spirit...\nDuring Kokkuri-san, focus on your finger'),
    ('EV9/M16/7', 'No.08  The Patrolling Teacher',
     'If you\'ve come this\nfar, don\'t hesitate'),
    ('EV9/M16/8', 'No.01  The Phantom Platform',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M16/9', 'No.02  An Unresolved Regret',
     'Did you talk properly with your friend?\nDid you act right at the shrine?'),
]

LOTE_2_EN = [
    ('EV9/M17/0', 'No.03  Left Behind',
     'Did you listen to the old\nman\'s story to the end?'),
    ('EV9/M17/1', 'No.04  The Opened Door',
     'Didn\'t you let go\nof the locker?'),
    ('EV9/M17/2', 'No.05  A Truth Untold',
     'Don\'t stay\non the train'),
    ('EV9/M17/3', 'No.06  I Gave Up',
     'Did you listen\nto the old man?'),
    ('EV9/M17/4', 'No.01  Hitori Kakurenbo',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M17/5', 'No.02  I Escaped, But...',
     'Did you follow the rules\nof hide and seek?'),
    ('EV9/M17/6', 'No.03  Together Until Dawn',
     'If only you had trusted\nyour friend more...'),
    ('EV9/M17/7', 'No.04  I Was Saved',
     'If only you had\nendured a bit longer...'),
    ('EV9/M17/8', 'No.05  A Fun Night',
     'Did you follow the rules\nof hide and seek?'),
    ('EV9/M17/9', 'No.06  The Unsolved Mystery',
     'The hide and seek\nisn\'t over yet'),
]

LOTE_3_EN = [
    ('EV9/M18/0', 'No.07  Burned Together',
     'What was really\nin the video...?'),
    ('EV9/M18/1', 'No.08  "I" Win',
     'After all, your opponent\nis a "spirit"...'),
    ('EV9/M18/2', 'No.09  A Scream From the Roof',
     'If only you had trusted your friend more...\nDid you check what was in the video?'),
    ('EV9/M18/3', 'No.10  Unable to Endure',
     'What was really in the video...?\nI endured until the end'),
    ('EV9/M18/4', 'No.11  A Torn Throat',
     'Did you stay calm\ninstead of scared?'),
    ('EV9/M18/5', 'No.12  The Model for the Legend',
     'Don\'t forget what\nthe teacher said'),
    ('EV9/M18/6', 'No.13  I Followed the Steps, But...',
     'Did you really do the\nhide and seek alone?'),
    ('EV9/M18/7', 'No.14  The Oni Wins',
     'Did you follow the rules\nof hide and seek?'),
    ('EV9/M18/8', 'No.15  Kokkuri-san, Kokkuri-san',
     'Without relying\non Kokkuri-san...'),
    ('EV9/M18/9', 'No.16  Under the Bed',
     'Being too scared\nbrings bad luck too'),
]

LOTE_4_EN = [
    ('EV9/M19/0', 'No.11  A Torn Throat',
     'Did you stay calm\ninstead of scared?'),
    ('EV9/M19/1', 'No.01  The Scary Theme Park',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M19/2', 'No.02  The End of the Dream',
     'Choose carefully\nDid you invite your friend?'),
    ('EV9/M19/3', 'No.03  Same as the Dream',
     'Did you search the whole park?\nChoose carefully'),
    ('EV9/M19/4', 'No.04  The Dream I Can\'t Wake From',
     'Watch out\nfor the clown'),
    ('EV9/M19/5', 'No.05  Let the Dream Stay a Dream',
     'Did you trust your\nfriend\'s advice?'),
    ('EV9/M19/6', 'No.01  The Hundred Urban Legends',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M19/7', 'No.02  The End of the Hundred Tales',
     'Did you look closely at the crossing tree?\nDid you search the whole school building?'),
    ('EV9/M19/8', 'No.03  The Wish Wasn\'t Granted',
     'Don\'t forget\nthe wordplay'),
    ('EV9/M19/9', 'No.04  Possessed',
     'If only you had\nendured a bit longer...'),
]

LOTE_5_EN = [
    ('EV9/M20/0', 'No.05  Nobody on the Rooftop',
     'I wonder if my\nfriend is safe'),
    ('EV9/M20/1', 'No.06  With the Dawn',
     'Don\'t forget your\nfriend\'s words'),
    ('EV9/M20/2', 'No.07  Hanako-san of the Bathroom',
     'Answer the knock carefully\nDid you search the whole school building?'),
    ('EV9/M20/3', 'No.01  The Kokkuri-san of the Old Building',
     'If you turn every story\ninto "Great Fortune"...'),
    ('EV9/M20/4', 'No.01  The Hundred Urban Legends',
     ''),
]


def run_lote(lote, nombre_hoja, idioma='esp'):
    out_root = f'assets/graficos/{idioma}'
    review_dir = '_scratch_claude/revision/lotes'
    os.makedirs(review_dir, exist_ok=True)

    thumbs = []
    for rel, title_es, hint_es in lote:
        base = os.path.join(ROOT, rel)
        before, after, new_bytes = patch_card(base, title_es, hint_es)

        out_path = os.path.join(out_root, rel + '.NCGR')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        open(out_path, 'wb').write(new_bytes)
        print(f'{rel}: guardado -> {out_path}')

        thumbs.append((rel, before, after))

    # hoja de revision: 2 columnas (antes | despues) por fila
    scale = 3
    cw, ch = 256 * scale, 192 * scale
    label_h = 16
    canvas = Image.new('RGB', (cw * 2 + 20, (ch + label_h + 10) * len(thumbs)), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    y = 0
    for rel, before, after in thumbs:
        b = before.resize((cw, ch), Image.NEAREST)
        a = after.resize((cw, ch), Image.NEAREST)
        draw.text((5, y), rel + ' - ANTES', fill=(255, 255, 0))
        draw.text((cw + 15, y), rel + ' - DESPUES', fill=(255, 255, 0))
        canvas.paste(b, (0, y + label_h))
        canvas.paste(a, (cw + 20, y + label_h))
        y += ch + label_h + 10
    out_sheet = os.path.join(review_dir, nombre_hoja)
    canvas.save(out_sheet)
    print('hoja de revision guardada en', out_sheet)


if __name__ == '__main__':
    import sys as _sys
    lotes_esp = {'1': (LOTE_1, 'lote1_EV9_M16.png'), '2': (LOTE_2, 'lote2_EV9_M17.png'),
                 '3': (LOTE_3, 'lote3_EV9_M18.png'), '4': (LOTE_4, 'lote4_EV9_M19.png'),
                 '5': (LOTE_5, 'lote5_EV9_M20.png')}
    lotes_eng = {'1': (LOTE_1_EN, 'eng_lote1_EV9_M16.png'), '2': (LOTE_2_EN, 'eng_lote2_EV9_M17.png'),
                 '3': (LOTE_3_EN, 'eng_lote3_EV9_M18.png'), '4': (LOTE_4_EN, 'eng_lote4_EV9_M19.png'),
                 '5': (LOTE_5_EN, 'eng_lote5_EV9_M20.png')}
    # uso: python3 traducir_menu_historias.py [eng] <numero_de_lote> [<numero_de_lote> ...]
    args = _sys.argv[1:]
    idioma = 'esp'
    if args and args[0] == 'eng':
        idioma = 'eng'
        args = args[1:]
    lotes = lotes_eng if idioma == 'eng' else lotes_esp
    nums = args or ['1']
    for n in nums:
        lote, nombre = lotes[n]
        print(f'--- procesando lote {n} ({idioma}) ---')
        run_lote(lote, nombre, idioma=idioma)
