#!/usr/bin/env python3
"""
traducir_botones_itm.py - Traduce los botones del menu de objetos
(ITM/2D/G04M10.NCBR, celdas 13-24 y 27-30): B 戻る / X 使う / A 調べる /
B 閉じる / Y 拡大 / Y 縮小, cada uno en 3 variantes de color (bancos 8, 9, 10).

El NCBR guarda cada OBJ como bitmap lineal 4bpp a partir de tile_idx*32. El
circulo con la letra del boton (B, X, A, Y) queda intacto: solo se borra el
texto japones (x >= 19, filas 0-18; la barra inferior se conserva) y se dibuja
el nuevo con una fuente compacta 3x5 (unos 28 px de ancho util), con el mismo
contorno de dos capas del original (tinta 12, aro 9, aro 10).

Uso: python3 scripts/traducir_botones_itm.py [--out DIR]
Por defecto escribe en rea_analisis/botones_itm/{esp,eng}/ITM/2D/G04M10.NCBR
Para instalarlo: copiar a assets/graficos/{esp,eng}/ITM/2D/.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import ncer_decode as n
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
BASE = os.path.join(ROOT, 'extraccion_rom/root/ITM/2D/G04M10')

# (celdas por banco 8/9/10, texto ES, texto EN)
BOTONES = [
    ((13, 14, 15), 'VOLVER', 'BACK'),     # B 戻る
    ((16, 17, 18), 'USAR', 'USE'),        # X 使う
    ((19, 20, 21), 'MIRAR', 'LOOK'),      # A 調べる
    ((22, 23, 24), 'CERRAR', 'CLOSE'),    # B 閉じる
    ((None, 27, 28), 'ZOOM+', 'ZOOM+'),  # Y 拡大
    ((None, 29, 30), 'ZOOM-', 'ZOOM-'),   # Y 縮小
]

FONT = {
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': [".##", "#..", "#..", "#..", ".##"],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'E': ["###", "#..", "##.", "#..", "###"],
    'G': [".##", "#..", "#.#", "#.#", ".##"],
    'H': ["#.#", "#.#", "###", "#.#", "#.#"],
    'I': ["#", "#", "#", "#", "#"],
    'K': ["#.#", "#.#", "##.", "#.#", "#.#"],
    'L': ["#..", "#..", "#..", "#..", "###"],
    'M': ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
    'O': [".#.", "#.#", "#.#", "#.#", ".#."],
    'P': ["##.", "#.#", "##.", "#..", "#.."],
    'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'S': [".##", "#..", ".#.", "..#", "##."],
    'U': ["#.#", "#.#", "#.#", "#.#", "###"],
    'Z': ["###", "..#", ".#.", "#..", "###"],
    '+': ["...", ".#.", "###", ".#.", "..."],
    '-': ["...", "...", "###", "...", "..."],
    'V': ["#.#", "#.#", "#.#", "#.#", ".#."],
}
TINTA, ARO1, ARO2 = 12, 9, 10
X0_BORRAR, Y1_BORRAR = 19, 18      # se borra x >= 19, filas 0..18
X_TEXTO, Y_TEXTO = 22, 11          # esquina sup. izq. del texto en la celda


def ancho(t):
    return sum(len(FONT[c][0]) for c in t) + (len(t) - 1)


class Ncbr:
    def __init__(self, path):
        self.raw = bytearray(open(path, 'rb').read())
        _, bl = n.parse_container(bytes(self.raw))
        off = bl[0][0]
        size = struct.unpack_from('<I', self.raw, off + 24)[0]
        rel = struct.unpack_from('<I', self.raw, off + 28)[0]
        self.start = off + 8 + rel
        self.size = size

    def get(self, base, i):
        b = self.raw[self.start + base + i // 2]
        return (b >> 4) if i % 2 else b & 15

    def set(self, base, i, v):
        p = self.start + base + i // 2
        b = self.raw[p]
        self.raw[p] = ((b & 0x0F) | (v << 4)) if i % 2 else ((b & 0xF0) | v)


class Celda:
    def __init__(self, ncbr, objs, tbs):
        self.nb = ncbr
        self.gs = [n.obj_geometry(*o, tile_boundary_shift=tbs) for o in objs]
        self.x0 = min(g['x'] for g in self.gs)
        self.y0 = min(g['y'] for g in self.gs)
        self.W = max(g['x'] + g['w'] for g in self.gs) - self.x0
        self.H = max(g['y'] + g['h'] for g in self.gs) - self.y0

    def _loc(self, x, y):
        for g in self.gs:  # OBJ de menor indice arriba
            gx, gy = x + self.x0 - g['x'], y + self.y0 - g['y']
            if 0 <= gx < g['w'] and 0 <= gy < g['h']:
                return g['tile_idx'] * 32, gy * g['w'] + gx
        return None

    def get(self, x, y):
        loc = self._loc(x, y)
        return self.nb.get(*loc) if loc else 0

    def put(self, x, y, v):
        loc = self._loc(x, y)
        if loc:
            self.nb.set(loc[0], loc[1], v)


def traducir_celda(c, texto):
    """Borra el texto japones y dibuja una capsula solida (borde 10, relleno 9,
    como los bloques del original) con el texto nuevo en tinta 12."""
    for y in range(0, 20):
        for x in range(X0_BORRAR, c.W):
            c.put(x, y, 0)
    w = ancho(texto)
    xe = min(c.W - 2, X_TEXTO + w + 1)       # ultima columna de la capsula
    # barra inferior (sombra de base): solo hasta la capsula, con punta
    for y, ini in ((20, 0), (21, 0)):
        for x in range(X0_BORRAR, c.W):
            c.put(x, y, (c.get(x, y) if x <= xe + (1 if y == 20 else 0) else 0))
    # capsula: filas 6..19, esquinas redondeadas
    for y in range(6, 20):
        for x in range(X0_BORRAR, xe + 1):
            borde = y in (6, 19) or x in (X0_BORRAR, xe)
            esquina = (y in (6, 19)) and (x in (X0_BORRAR, xe))
            if esquina:
                continue
            c.put(x, y, ARO2 if borde else ARO1)
    x = X_TEXTO
    for ch in texto:
        for yy, row in enumerate(FONT[ch]):
            for xx, p in enumerate(row):
                if p == '#':
                    c.put(x + xx, Y_TEXTO + yy, TINTA)
        x += len(FONT[ch][0]) + 1
    assert xe <= c.W - 2 and X_TEXTO + w <= xe, f'{texto}: no entra'


def render_celda(c, col, banco):
    im = Image.new('RGB', (c.W, c.H), (30, 20, 60))
    for y in range(c.H):
        for x in range(c.W):
            v = c.get(x, y)
            if v:
                im.putpixel((x, y), col[banco * 16 + v])
    return im


def main():
    args = sys.argv[1:]
    out = os.path.join(ROOT, 'rea_analisis/botones_itm')
    if '--out' in args:
        out = args[args.index('--out') + 1]
    cells, tbs = n.decode_ncer(BASE + '.NCER')
    col = n.decode_nclr(BASE + '.NCLR')
    for idioma, k in (('esp', 1), ('eng', 2)):
        nb = Ncbr(BASE + '.NCBR')
        orig_len = len(nb.raw)
        previews = []
        for celdas, es, en in BOTONES:
            texto = (es, en)[k - 1]
            for banco, ci in zip((8, 9, 10), celdas):
                if ci is None:
                    continue
                c = Celda(nb, cells[ci], tbs)
                traducir_celda(c, texto)
                previews.append(render_celda(c, col, banco))
        assert len(nb.raw) == orig_len
        carpeta = os.path.join(out, idioma, 'ITM', '2D')
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, 'G04M10.NCBR'), 'wb').write(bytes(nb.raw))
        # hoja de vista previa x4
        w = max(p.width for p in previews)
        hoja = Image.new('RGB', (w * 3 + 20, (previews[0].height + 4) * 6 + 4), (45, 45, 45))
        for i, p in enumerate(previews):
            hoja.paste(p, ((i % 3) * (w + 6), (i // 3) * (p.height + 4)))
        hoja = hoja.resize((hoja.width * 4, hoja.height * 4), Image.NEAREST)
        hoja.save(os.path.join(out, f'prev_{idioma}.png'))
        print(idioma, 'ok', len(previews), 'celdas')


if __name__ == '__main__':
    main()
