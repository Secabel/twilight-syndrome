#!/usr/bin/env python3
"""
traducir_opcion_listas.py - Traduce las barras de texto de las listas del menu
de coleccionables (OPTION/M10, M11, M12): nombres de lugares (M10, M11) y de
rumores "第N の噂 No.XX 大吉/中吉/凶" (M12), unas 100 barras de 144x16 px.

Cada barra es una celda NCER de varios OBJ de 32x16 (4bpp, banco 4) con el
texto horneado: tinta indice 4, contorno indice 5. Se borra la celda y se
dibuja el texto nuevo (misma tecnica que redibujar_ui_celular.py: Sprite.edit
da tiles propios a los OBJ compartidos y agrega OBJ 8x8 si el texto nuevo se
sale de los OBJ originales). Los "???" no se tocan.

Uso: python3 scripts/traducir_opcion_listas.py [--prev DIR]
Escribe en assets/graficos/{esp,eng}/OPTION/{M10,M11,M12}.{NCGR,NCER}.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import redibujar_ui_celular as R
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = ['C:/Windows/Fonts/segoeui.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf']
INK, OUT = 4, 5
MAXW = 140

M10 = {
    5: ('Edif. viejo 1F, guardia', 'Old Bldg 1F Night-Duty Rm'),
    6: ('Edif. viejo 1F, pasillo', 'Old Bldg 1F Hallway'),
    7: ('Edif. viejo 3F, aula', 'Old Bldg 3F Classroom'),
    8: ('Túnel', 'Tunnel'),
    9: ('Antigua est. Mitsuya Koen', 'Old Mitsuya Koen Station'),
    10: ('Cueva del Jizo', 'Jizo Cave'),
    11: ('Casa de Mizuki, armario', "Mizuki's House, Closet"),
    12: ('Edificio de deptos. 1F', 'Apartments 1F Corridor'),
    13: ('Casa de Mizuki, entrada', "Mizuki's House, Entrance"),
    14: ('Carrusel', 'Carousel'),
    15: ('Casa de espejos', 'Mirror House'),
    16: ('Montaña rusa', 'Roller Coaster'),
    17: ('Edif. nuevo 2F, pasillo', 'New Bldg 2F Hallway'),
    18: ('Edif. nuevo 2F, biblioteca', 'New Bldg 2F Library'),
    19: ('Edif. nuevo, piscina', 'New Bldg Pool'),
}
M11 = {
    5: ('Edif. viejo 2F, laboratorio', 'Old Bldg 2F Science Lab'),
    6: ('Edif. viejo 1F, bodega', 'Old Bldg 1F Storage Rm'),
    7: ('Edif. viejo 1F, entrada', 'Old Bldg 1F Entrance'),
    8: ('Est. Higashi-Kirizuka, andén', 'Higashi-Kirizuka Stn Platform'),
    9: ('Cueva', 'Cave'),
    10: ('Mitsuya Koen, torniquetes', 'Mitsuya Koen Ticket Gate'),
    11: ('Casa de Mizuki, sala', "Mizuki's House, Living Rm"),
    12: ('Casa de Mizuki, sala', "Mizuki's House, Living Rm"),
    13: ('Casa de Mizuki, baño', "Mizuki's House, Bathroom"),
    14: ('Casa embrujada', 'Haunted House'),
    15: ('Pasadizo subterráneo', 'Underground Passage'),
    16: ('Plaza', 'Plaza'),
    17: ('Edif. nuevo, piscina', 'New Bldg Pool'),
    18: ('Edif. nuevo 2F, baño h.', "New Bldg 2F Boys' Restroom"),
    19: ('Edif. nuevo, azotea', 'New Bldg Rooftop'),
}
# rumores: (numero de rumor, categorias de No.01 en adelante); D=大吉 C=中吉 K=凶
RUMORES = [(1, 'DCCCCKKK'), (2, 'DCKKKK'), (3, 'DCCCCCKKKKKKKKKK'),
           (4, 'DCKKK'), (5, 'DCKKKKK')]
CAT = {'D': ('Gran suerte', 'Great luck'), 'C': ('Suerte media', 'Fair luck'),
       'K': ('Mala suerte', 'Bad luck')}
M12 = {12: ('Rumor inicial', 'The Beginning Rumor')}
_c = 13
for n, cats in RUMORES:
    for i, k in enumerate(cats):
        M12[_c] = (f'Rumor {n} No.{i + 1:02d} {CAT[k][0]}', f'Rumor {n} No.{i + 1:02d} {CAT[k][1]}')
        _c += 1
M12[_c] = ('Último rumor', 'The Final Rumor')
assert _c == 55
TEXTOS = {'M10': M10, 'M11': M11, 'M12': M12}


def fuente(sz):
    for p in FONTS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def mascara(texto, w, h):
    probe = ImageDraw.Draw(Image.new('L', (400, 40)))
    probe.fontmode = '1'
    for sz in range(11, 6, -1):
        f = fuente(sz)
        bb = probe.textbbox((0, 0), texto, font=f)
        if bb[2] - bb[0] <= MAXW - 4:
            break
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((3 - bb[0], (h - (bb[3] - bb[1])) // 2 - bb[1]), texto, font=f, fill=255)
    return m


def vaciar(s, ci):
    """Deja en blanco todos los OBJ de la celda (con tiles propios), para que
    los OBJ que se solapan no dejen restos del texto japones."""
    for k in range(len(s.ncer.cells[ci]['objs'])):
        s.privatize(ci, k)
        g = s.geoms(ci)[k]
        wt = g['w'] // 8
        for ly in range(g['h']):
            for lx in range(g['w']):
                t = g['tile_idx'] + ((ly // 8) * wt + lx // 8) * s.u
                s.ncgr.set_px(t, lx % 8, ly % 8, 0)


def traducir(s, ci, texto):
    vaciar(s, ci)

    def fn(im):
        m = mascara(texto, im.w, im.h)
        ring = m.filter(ImageFilter.MaxFilter(3))
        pm, pr = m.load(), ring.load()
        for y in range(im.h):
            for x in range(im.w):
                im.set(x, y, INK if pm[x, y] else (OUT if pr[x, y] else 0))
    s.edit(ci, fn)


def main():
    prev = None
    if '--prev' in sys.argv:
        prev = sys.argv[sys.argv.index('--prev') + 1]
    pal = R.read_palette('OPTION/M10.NCLR')[64:80]
    for k, lang in enumerate(('esp', 'eng')):
        filas = []
        for f in ('M10', 'M11', 'M12'):
            s = R.Sprite('OPTION/' + f)
            orig = {ci: s.compose(ci) for ci in TEXTOS[f]}
            for ci, tx in TEXTOS[f].items():
                traducir(s, ci, tx[k])
            s.save(lang)
            for ci in TEXTOS[f]:
                filas.append((orig[ci], s.compose(ci)))
            print(lang, f, len(TEXTOS[f]), 'barras, NCGR', len(s.ncgr.d), 'bytes')
        if prev:
            os.makedirs(prev, exist_ok=True)
            n = len(filas)
            hoja = Image.new('RGB', (2 * 180 + 4, n * 17 + 2), (28, 18, 64))
            for i, (a, b) in enumerate(filas):
                for col, im in enumerate((a, b)):
                    for y in range(min(16, im.h)):
                        for x in range(min(176, im.w)):
                            v = im.get(x, y)
                            if v:
                                hoja.putpixel((col * 180 + x, 1 + i * 17 + y), pal[v])
            hoja.resize((hoja.width * 2, hoja.height * 2), Image.NEAREST).save(os.path.join(prev, f'prev_option_{lang}.png'))


if __name__ == '__main__':
    main()
