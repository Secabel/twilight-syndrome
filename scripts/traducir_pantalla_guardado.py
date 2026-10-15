#!/usr/bin/env python3
"""
traducir_pantalla_guardado.py - Traduce los textos sueltos de la pantalla de
guardar / cargar partida (SAVELOAD/M10 = guardar, SAVELOAD/M11 = cargar):

  celda 10      titulo 記録 / 再開      -> SALVAR / CARGAR   (SAVE / LOAD)
  celdas 12,13  boton 戻る (texto)      -> VOLVER            (BACK)
  celdas 26-31  numeros de casilla 一..六 -> 1..6

Parte de los NCGR/NCER que ya estan en assets/graficos/<idioma>/SAVELOAD/ (con
el はい/いいえ traducido) y los reescribe ahi mismo. Indices de color
(verificados en los mapas de pixeles originales): titulo tinta 10 / contorno 1;
texto de 戻る tinta 15 / contorno 13; numeros tinta 15 / contorno 13.

Uso: python3 scripts/traducir_pantalla_guardado.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import redibujar_ui_celular as R
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = R.ROOT
FONT_PATHS = ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
TEXTOS = {
    'esp': {'M10': ('SALVAR', 11), 'M11': ('CARGAR', 11), 'back': ('VOLVER', 8)},
    'eng': {'M10': ('SAVE', 14), 'M11': ('LOAD', 14), 'back': ('BACK', 9)},
}
_orig_read = R.read_original
LANG = None


def _read(path):
    """Prefiere el archivo ya parcheado de assets (conserva はい/いいえ)."""
    if LANG and path.startswith('SAVELOAD/M1') and path.endswith(('.NCGR', '.NCER')):
        p = os.path.join(ROOT, 'assets/graficos', LANG, path)
        if os.path.exists(p):
            return open(p, 'rb').read()
    return _orig_read(path)


R.read_original = _read


def fuente(size):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def mascara(texto, size, w, h, ancho_max=None, x0=0):
    """Mascara 1-bit (L 0/255) w x h con el texto centrado en [x0, x0+ancho_max),
    sin antialias; baja el tamano de letra hasta que entre (con 1 px de margen)."""
    ancho_max = ancho_max or w
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    for sz in range(size, 5, -1):
        f = fuente(sz)
        bb = d.textbbox((0, 0), texto, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw <= ancho_max - 2 and th <= h - 2:
            break
    d.text((x0 + (ancho_max - tw) // 2 - bb[0], (h - th) // 2 - bb[1]), texto, font=f, fill=255)
    return m


def capas(m, ink, out):
    """Devuelve {(x,y): indice} con tinta y contorno de 1 px."""
    ring = m.filter(ImageFilter.MaxFilter(3))
    pm, pr = m.load(), ring.load()
    res = {}
    for y in range(m.height):
        for x in range(m.width):
            if pm[x, y]:
                res[(x, y)] = ink
            elif pr[x, y]:
                res[(x, y)] = out
    return res


def editar_celda(s, ci, texto, size, ink, out):
    """Celda sin solapes (titulo, numeros): se borra entera y se pinta."""
    g = s.geoms(ci)
    ox, oy = s.origin(ci)
    W = max(x['x'] + x['w'] for x in g) - ox
    H = max(x['y'] + x['h'] for x in g) - oy
    pint = capas(mascara(texto, size, W, H, ancho_max=W - 2, x0=1), ink, out)

    def fn(im):
        for y in range(H):
            for x in range(W):
                im.set(x, y, pint.get((x, y), 0))
    s.edit(ci, fn)


def editar_obj(s, ci, k, texto, size, ink, out):
    """Reescribe entero el OBJ k de la celda (el texto de 戻る, sobre la capsula)."""
    s.privatize(ci, k)
    g = s.geoms(ci)[k]
    w, h = g['w'], g['h']
    pint = capas(mascara(texto, size, w, h, ancho_max=34, x0=-1), ink, out)
    wt = w // 8
    for ly in range(h):
        for lx in range(w):
            t = g['tile_idx'] + ((ly // 8) * wt + lx // 8) * s.u
            s.ncgr.set_px(t, lx % 8, ly % 8, pint.get((lx, ly), 0))


def main():
    global LANG
    previews = []
    for lang in ('esp', 'eng'):
        LANG = lang
        for f in ('M10', 'M11'):
            s = R.Sprite('SAVELOAD/' + f)
            tit, tsz = TEXTOS[lang][f]
            editar_celda(s, 10, tit, tsz, 10, 1)
            btxt, bsz = TEXTOS[lang]['back']
            for ci in (12, 13):
                editar_obj(s, ci, 0, btxt, bsz, 15, 13)
            for i, ci in enumerate(range(26, 32)):
                editar_celda(s, ci, str(i + 1), 9, 15, 13)
            s.save(lang)
            print(lang, f, 'ok')
            # vista previa aproximada (paleta del banco 4 de M11)
            pal = R.read_palette('SAVELOAD/M11.NCLR')[64:80]
            fila = []
            for ci in (10, 12, 13, 26, 27, 28, 29, 30, 31):
                im = s.compose(ci)
                rgb = Image.new('RGB', (im.w, im.h), (30, 20, 60))
                for y in range(im.h):
                    for x in range(im.w):
                        v = im.get(x, y)
                        if v:
                            rgb.putpixel((x, y), pal[v])
                fila.append(rgb)
            previews.append((lang, f, fila))
    out = os.path.join(ROOT, 'rea_analisis/botones_itm')
    os.makedirs(out, exist_ok=True)
    W = sum(i.width + 6 for i in previews[0][2]) + 4
    hoja = Image.new('RGB', (W, len(previews) * 30 + 4), (45, 45, 45))
    for r, (_, _, fila) in enumerate(previews):
        x = 2
        for im in fila:
            hoja.paste(im, (x, 2 + r * 30)); x += im.width + 6
    hoja.resize((hoja.width * 3, hoja.height * 3), Image.NEAREST).save(os.path.join(out, 'prev_guardado.png'))


if __name__ == '__main__':
    main()
