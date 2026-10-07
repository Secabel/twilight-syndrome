#!/usr/bin/env python3
"""
redibujar_ui_celular.py - Traduce la UI secundaria del celular (graficos
cocinados) con la fuente del celular (scripts/fuente_celular.py) y genera
los NCGR/NCER por idioma en assets/graficos/<esp|eng>/...

  R02/A_S10, R02/B_S10  enviar correo (Enviado / Error al enviar / Enviando...
                        + 9 contactos)
  R09/A_S10             historial de llamadas
  R10/A_S10             reproductor de audio (Tocando / Terminado)
  R24/A_S10             pagina web "Not Found"
  EV0/S07/5             llamada (切断中 -> Cortando, 決定 -> OK)  [NSCR]
  EV9/S00/2-9           fondos de pantalla, boton 決定 -> OK       [NSCR]

Uso: python3 scripts/redibujar_ui_celular.py
Lee siempre los originales japoneses (extraccion_rom/root o la ROM JP).

Sprites: se compone cada celda como imagen de indices, se edita (borrar
texto, reconstruir fondo, pintar traduccion) y se escriben de vuelta solo los
pixeles que cambiaron. Si un OBJ modificado comparte tiles con otro (o usa
flip) se le dan tiles propios al final del NCGR, para no ensuciar otras
celdas. Pixeles nuevos fuera de todo OBJ -> OBJ 8x8 extra.
NSCR (8bpp, 768 tiles unicos, sin flips): edicion directa de los tiles.
Mockup aprobado: _scratch_claude/auditoria/mockup_celular.png y
mockup_alternativas.png (2026-10-07).
"""
import os, sys, struct, math
sys.path.insert(0, os.path.dirname(__file__))
import ncer_decode as ic
import fuente_celular as F
from redibujar_correos import Ncer, Ncgr, cell_radius

ROOT = os.path.join(os.path.dirname(__file__), '..')
EXTR = os.path.join(ROOT, 'extraccion_rom/root')
BASE_ROM = os.path.join(ROOT, 'Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds')
_rom = None


def read_original(path):
    p = os.path.join(EXTR, path)
    if os.path.exists(p):
        return open(p, 'rb').read()
    global _rom
    if _rom is None:
        import ndspy.rom
        _rom = ndspy.rom.NintendoDSRom.fromFile(BASE_ROM)
    return _rom.getFileByName(path)


def read_palette(path, ncolors=None):
    data = read_original(path)
    magic, blocks = ic.parse_container(data)
    off = next(o for o, m, s in blocks if m == b'TTLP')
    size = struct.unpack_from('<I', data, off + 16)[0]
    raw = data[off + 24: off + 24 + size]
    cols = []
    for i in range(0, len(raw) - 1, 2):
        v = struct.unpack_from('<H', raw, i)[0]
        cols.append(((v & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8))
    return cols


# ---------------------------------------------------------------- imagen de indices
class Img:
    def __init__(self, w, h, pal, fill=0):
        self.w, self.h, self.pal = w, h, pal
        self.p = [[fill] * w for _ in range(h)]

    def copy(self):
        o = Img(self.w, self.h, self.pal); o.p = [r[:] for r in self.p]; return o

    def get(self, x, y): return self.p[y][x]

    def set(self, x, y, v):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = v

    def rgb(self, v): return self.pal[v]

    def idx(self, rgb, exact=True):
        if rgb in self.pal[1:]:
            return self.pal.index(rgb, 1)
        assert not exact, f'color {rgb} no esta en la paleta'
        return min(range(1, len(self.pal)), key=lambda i: sum((a - b) ** 2 for a, b in zip(self.pal[i], rgb)))


def erase(im, box, sx):
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        c = im.get(sx, y)
        for x in range(x0, x1 + 1):
            im.set(x, y, c)


def text(im, s, x, y, stroke, shadow=None, center=None, outline=None, thick=1, gap=None):
    m = F.render(s, top=0, cell_h=10, gap=gap); w = len(m[0])
    if center is not None:
        x = center - w // 2
    if outline is not None:
        for yy, row in enumerate(m):
            for xx, v in enumerate(row):
                if v == 1:
                    for dx in range(-thick, thick + 1):
                        for dy in range(-thick, thick + 1):
                            im.set(x + xx + dx, y + yy + dy, outline)
        shadow = None
    for yy, row in enumerate(m):
        for xx, v in enumerate(row):
            if v == 1:
                im.set(x + xx, y + yy, stroke)
            elif v == 2 and shadow is not None:
                im.set(x + xx, y + yy, shadow)


# ---------------------------------------------------------------- sprites (NCER)
class Ncgr8(Ncgr):
    """NCGR de 8bpp: el indice de tile sigue contando en unidades de 32 bytes
    (un tile 8x8 ocupa 2 unidades)."""
    def get_px(self, tile, lx, ly):
        return self.d[self.px_off + tile * 32 + ly * 8 + lx]

    def set_px(self, tile, lx, ly, v):
        self.d[self.px_off + tile * 32 + ly * 8 + lx] = v


def ncgr_bpp(data):
    magic, blocks = ic.parse_container(bytes(data))
    rahc = next(o for o, m, s in blocks if m == b'RAHC')
    return 8 if struct.unpack_from('<I', data, rahc + 12)[0] == 4 else 4


def obj_px(ncgr, g, u=1):
    """(cx, cy, tile, lx, ly) de cada pixel visible del OBJ (con flips).
    u = unidades de 32 bytes por tile (1 en 4bpp, 2 en 8bpp)."""
    wt = g['w'] // 8
    for oy in range(g['h']):
        for ox in range(g['w']):
            sx = g['w'] - 1 - ox if g['hflip'] else ox
            sy = g['h'] - 1 - oy if g['vflip'] else oy
            t = g['tile_idx'] + ((sy // 8) * wt + sx // 8) * u
            yield g['x'] + ox, g['y'] + oy, t, sx % 8, sy % 8


class Sprite:
    def __init__(self, base, nclr=None):
        self.base = base
        raw = read_original(base + '.NCGR')
        self.bpp = ncgr_bpp(raw)
        self.u = 2 if self.bpp == 8 else 1
        self.ncgr = (Ncgr8 if self.bpp == 8 else Ncgr)(raw)
        self.ncer = Ncer(read_original(base + '.NCER'))
        pal = read_palette(nclr or base + '.NCLR')
        self.pal = pal[:256] if self.bpp == 8 else pal[:16]
        self.tbs = self.ncer.tbs

    def geoms(self, ci):
        return [ic.obj_geometry(*o, tile_boundary_shift=self.tbs) for o in self.ncer.cells[ci]['objs']]

    def origin(self, ci):
        gs = self.geoms(ci)
        return min(g['x'] for g in gs), min(g['y'] for g in gs)

    def compose(self, ci, pad=0):
        gs = self.geoms(ci)
        ox, oy = self.origin(ci)
        W = max(g['x'] + g['w'] for g in gs) - ox + pad
        H = max(g['y'] + g['h'] for g in gs) - oy
        im = Img(W, H, self.pal)
        # OBJ con indice menor queda arriba: pintar en orden inverso
        for g in reversed(gs):
            for (x, y, t, lx, ly) in obj_px(self.ncgr, g, self.u):
                v = self.ncgr.get_px(t, lx, ly)
                if v:
                    im.set(x - ox, y - oy, v)
        return im

    def refcount(self):
        rc = {}
        for c in self.ncer.cells:
            for o in c['objs']:
                g = ic.obj_geometry(*o, tile_boundary_shift=self.tbs)
                for t in range(g['tile_idx'], g['tile_idx'] + g['w'] * g['h'] // 64 * self.u):
                    rc[t] = rc.get(t, 0) + 1
        return rc

    def privatize(self, ci, k):
        """Le da al OBJ k de la celda ci tiles propios (sin flip)."""
        o = self.ncer.cells[ci]['objs'][k]
        g = ic.obj_geometry(*o, tile_boundary_shift=self.tbs)
        n = g['w'] * g['h'] // 64 * self.u
        rc = self.refcount()
        unico = all(rc.get(t, 0) == 1 for t in range(g['tile_idx'], g['tile_idx'] + n))
        if unico and not g['hflip'] and not g['vflip']:
            return
        pix = [(x - g['x'], y - g['y'], self.ncgr.get_px(t, lx, ly)) for (x, y, t, lx, ly) in obj_px(self.ncgr, g, self.u)]
        # tiles usados solo por este OBJ pero con flip: se des-espejan en el
        # mismo lugar (no hace falta agrandar el NCGR)
        t0 = g['tile_idx'] if unico else self.ncgr.add_tiles(n)
        wt = g['w'] // 8
        for (ox, oy, v) in pix:
            self.ncgr.set_px(t0 + ((oy // 8) * wt + ox // 8) * self.u, ox % 8, oy % 8, v)
        o[1] &= ~0x3000                                    # sin flips
        o[2] = (o[2] & ~0x3FF) | ((t0 >> self.tbs) & 0x3FF)
        assert ic.obj_geometry(*o, tile_boundary_shift=self.tbs)['tile_idx'] == t0

    def write(self, ci, old, new):
        ox, oy = self.origin(ci)
        cell = self.ncer.cells[ci]
        changed = [(x, y) for y in range(new.h) for x in range(new.w) if new.get(x, y) != old.get(x, y)]
        if not changed:
            return 0
        gs = self.geoms(ci)
        owner = {}
        for (x, y) in changed:
            cx, cy = x + ox, y + oy
            k = next((k for k, g in enumerate(gs) if g['x'] <= cx < g['x'] + g['w'] and g['y'] <= cy < g['y'] + g['h']), None)
            owner[(x, y)] = k
        for k in sorted(set(v for v in owner.values() if v is not None)):
            self.privatize(ci, k)
        gs = self.geoms(ci)
        extra = 0
        pal_bits = cell['objs'][0][2] & 0xF000
        for (x, y), k in owner.items():
            v = new.get(x, y)
            cx, cy = x + ox, y + oy
            if k is None:
                if v == 0:
                    continue
                # OBJ 8x8 nuevo alineado a la grilla de 8 de la celda
                bx, by = ox + (x // 8) * 8, oy + (y // 8) * 8
                t0 = self.ncgr.add_tiles(self.u)
                o = [(by & 0xFF) | (0x2000 if self.bpp == 8 else 0), bx & 0x1FF, pal_bits | ((t0 >> self.tbs) & 0x3FF)]
                cell['objs'].append(o); gs.append(ic.obj_geometry(*o, tile_boundary_shift=self.tbs))
                for yy in range(8):
                    for xx in range(8):
                        q = (bx - ox + xx, by - oy + yy)
                        if 0 <= q[0] < new.w and 0 <= q[1] < new.h:
                            self.ncgr.set_px(t0, xx, yy, new.get(*q))
                for q in list(owner):
                    if owner[q] is None and bx <= q[0] + ox < bx + 8 and by <= q[1] + oy < by + 8:
                        owner[q] = len(gs) - 1
                extra += 1
                continue
            g = gs[k]
            lx, ly = cx - g['x'], cy - g['y']
            wt = g['w'] // 8
            self.ncgr.set_px(g['tile_idx'] + ((ly // 8) * wt + lx // 8) * self.u, lx % 8, ly % 8, v)
        if extra:
            cell['attr'] = (cell['attr'] & ~0x3F) | min(0x3F, cell_radius(cell['objs'], self.tbs))
        return len(changed)

    def edit(self, ci, fn):
        old = self.compose(ci, pad=32)   # margen por si el texto nuevo es mas ancho
        new = old.copy()
        fn(new)
        n = self.write(ci, old, new)
        # verificacion: la celda recompuesta debe ser igual a la editada
        chk = self.compose(ci, pad=64)
        assert chk.w >= new.w and all(chk.get(x, y) == new.get(x, y) for y in range(new.h) for x in range(new.w)), (self.base, ci)
        return n

    def save(self, lang, base=None):
        base = base or self.base
        out = os.path.join(ROOT, 'assets/graficos', lang, os.path.dirname(base))
        os.makedirs(out, exist_ok=True)
        name = os.path.basename(base)
        open(os.path.join(out, name + '.NCGR'), 'wb').write(bytes(self.ncgr.d))
        open(os.path.join(out, name + '.NCER'), 'wb').write(self.ncer.build())


# ---------------------------------------------------------------- fondos (NSCR 8bpp)
class Screen:
    def __init__(self, base, nclr):
        self.base = base
        self.ncgr = bytearray(read_original(base + '.NCGR'))
        magic, blocks = ic.parse_container(bytes(self.ncgr))
        rahc = next(o for o, m, s in blocks if m == b'RAHC')
        assert struct.unpack_from('<I', self.ncgr, rahc + 12)[0] == 4, '8bpp'
        self.px = rahc + 8 + struct.unpack_from('<I', self.ncgr, rahc + 28)[0]
        nscr = read_original(base + '.NSCR')
        magic, blocks = ic.parse_container(nscr)
        sc = next(o for o, m, s in blocks if m == b'NRCS')
        self.W, self.H = struct.unpack_from('<HH', nscr, sc + 8)
        n = struct.unpack_from('<I', nscr, sc + 16)[0] // 2
        self.ent = [struct.unpack_from('<H', nscr, sc + 20 + 2 * i)[0] for i in range(n)]
        assert all(not (e >> 10) & 3 for e in self.ent)
        bank = self.ent[0] >> 12
        assert all(e >> 12 == bank for e in self.ent)
        self.pal = read_palette(nclr)[bank * 256:(bank + 1) * 256]

    def off(self, x, y):
        t = self.ent[(y // 8) * (self.W // 8) + x // 8] & 0x3FF
        return self.px + t * 64 + (y % 8) * 8 + x % 8

    def edit(self, fn):
        im = Img(self.W, self.H, self.pal)
        for y in range(self.H):
            for x in range(self.W):
                im.p[y][x] = self.ncgr[self.off(x, y)]
        fn(im)
        for y in range(self.H):
            for x in range(self.W):
                self.ncgr[self.off(x, y)] = im.p[y][x]

    def save(self, lang):
        out = os.path.join(ROOT, 'assets/graficos', lang, os.path.dirname(self.base))
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, os.path.basename(self.base) + '.NCGR'), 'wb').write(bytes(self.ncgr))


# ---------------------------------------------------------------- textos
T = {
    'enviado':  ('ENVIADO', 'SENT'),
    'error':    ('ERROR AL ENVIAR', 'SENDING FAILED'),
    'enviando': ('ENVIANDO...', 'SENDING...'),
    'llamadas': ('LLAMADAS', 'CALL LOG'),
    'tocando':  ('TOCANDO', 'PLAYING'),
    'fin':      ('TERMINADO', 'FINISHED'),
    'web1':     ('NO ENCONTRADA.', 'PAGE NOT FOUND.'),
    'web2':     ('REVISA LA URL.', 'CHECK THE URL.'),
    'cortando': ('CORTANDO', 'HANGING UP'),
}
NOMBRES_A = ['HARUNA', 'MAYUKO', 'ATSUMI', 'NATSU', 'MIO', 'MIZUKI']   # celdas 4-21, de a 3
NOMBRES_B = ['YUMI', 'AYA', 'YUUJI', 'MIO', 'NATSU', 'ATSUMI']


def nombre(s, ci, name):
    """Celdas de contacto: el texto japones siempre empieza en x=-62 absoluto
    (OBJs de texto en -64..-16); en las variantes con icono, el icono es un
    OBJ aparte en -80. Se borra desde -64 y se pinta en -62 con los mismos
    indices (trazo = el mas usado, sombra = el segundo)."""
    ox, oy = s.origin(ci)
    def fn(im):
        reg = [(x, y) for y in range(im.h) for x in range(-64 - ox, im.w)]
        cnt = {}
        for (x, y) in reg:
            v = im.get(x, y)
            if v:
                cnt[v] = cnt.get(v, 0) + 1
        orden = sorted(cnt, key=lambda v: -cnt[v])
        stroke = orden[0]; shadow = orden[1] if len(orden) > 1 else None
        for (x, y) in reg:
            im.set(x, y, 0)
        assert F.width(name) <= 46, name
        text(im, name, -62 - ox, 4, stroke, shadow)
    return fn


def contactos(L):
    """Encabezado 電話帳一覧 (celda 3 de R02/A y B): fondo, trazo y sombra =
    los 3 indices mas usados en la franja del titulo."""
    def fn(im):
        cnt = {}
        for y in range(2, 14):
            for x in range(2, 70):
                v = im.get(x, y); cnt[v] = cnt.get(v, 0) + 1
        o = sorted(cnt, key=lambda v: -cnt[v])
        erase(im, (2, 2, 75, 14), 100)
        text(im, ('CONTACTOS', 'CONTACTS')[L], 3, 4, o[1], o[2])
    return fn


def r02a(lang):
    s = Sprite('R02/A_S10'); L = 0 if lang == 'esp' else 1
    def caja(t):
        def fn(im):
            erase(im, (7, 50, 153, 65), 7)
            text(im, t, 0, 53, im.idx((240, 240, 240)), im.idx((160, 32, 32)), center=80)
        return fn
    s.edit(0, caja(T['enviado'][L]))
    s.edit(1, caja(T['error'][L]))
    def corazon(im):
        ref = [im.get(x, 79) for x in range(im.w)]
        bg = im.idx((96, 0, 0))
        for y in range(80, 97):
            d = y - 79
            for x in range(56, 105):
                src = x - d if x <= 81 else x + d
                im.set(x, y, ref[src] if 53 <= src <= 110 else bg)
        text(im, T['enviando'][L], 0, 84, im.idx((240, 240, 240)), center=82, outline=im.idx((176, 0, 0)))
    for ci in (22, 23, 24):
        s.edit(ci, corazon)
    for i, n in enumerate(NOMBRES_A):
        for ci in range(4 + 3 * i, 7 + 3 * i):
            s.edit(ci, nombre(s, ci, n))
    s.edit(3, contactos(L))
    s.save(lang)


def r02b(lang):
    s = Sprite('R02/B_S10'); L = 0 if lang == 'esp' else 1
    def caja(im):
        erase(im, (6, 55, 154, 68), 6)
        text(im, T['enviado'][L], 0, 57, im.idx((96, 96, 96)), center=80)
    s.edit(0, caja)
    def flecha(im):
        erase(im, (59, 75, 102, 88), 57)
        text(im, T['enviando'][L], 0, 77, im.idx((8, 8, 8)), center=80)
    for ci in (22, 23, 24):
        s.edit(ci, flecha)
    for i, n in enumerate(NOMBRES_B):
        for ci in range(4 + 3 * i, 7 + 3 * i):
            s.edit(ci, nombre(s, ci, n))
    s.edit(3, contactos(L))
    s.save(lang)


def r09(lang):
    s = Sprite('R09/A_S10'); L = 0 if lang == 'esp' else 1
    def fn(im):
        # filas medidas sobre el original: titulo 4-15, nombres 30-39 / 62-71 / 94-103
        # (las fechas 19-26 / 50-57 / 80-87 no se tocan). Trazo/sombra = mismos indices.
        erase(im, (1, 3, 70, 15), 100); text(im, T['llamadas'][L], 3, 5, 2, 9)
        erase(im, (15, 28, 110, 40), 130); text(im, 'IZUMI REIKA', 18, 30, 15, 7)
        erase(im, (15, 59, 110, 73), 130); text(im, 'ENOMOTO MIO', 18, 62, 2, 9)
        erase(im, (15, 90, 125, 105), 140); text(im, 'WATANABE HARUNA', 18, 94, 2, 9)
    s.edit(0, fn)
    s.save(lang)


def r10(lang):
    s = Sprite('R10/A_S10'); L = 0 if lang == 'esp' else 1
    def fn_for(ci, t):
        def fn(im):
            txt = {im.idx((248, 232, 240)), im.idx((48, 48, 48)), im.idx((184, 192, 184))}
            x0, x1, y0, y1 = (8, 66, 40, 75) if ci < 3 else (21, 78, 54, 71)
            bg = {im.get(x, y) for y in range(im.h) for x in range(im.w)
                  if not (x0 <= x <= x1 and y0 <= y <= y1)} - txt
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if im.get(x, y) not in bg:
                        k = x - 1
                        while k > 0 and im.get(k, y) not in bg:
                            k -= 1
                        im.set(x, y, im.get(k, y))
            text(im, t, 24, 57, im.idx((248, 232, 240)), outline=im.idx((48, 48, 48)))
        return fn
    for ci in (0, 1, 2):
        s.edit(ci, fn_for(ci, T['tocando'][L]))
    s.edit(3, fn_for(3, T['fin'][L]))
    s.save(lang)


def r24(lang):
    s = Sprite('R24/A_S10'); L = 0 if lang == 'esp' else 1
    def fn(im):
        c = im.idx
        erase(im, (3, 14, 127, 46), 2)
        text(im, T['web1'][L], 5, 16, c((192, 24, 24)), c((72, 16, 16)))
        text(im, T['web2'][L], 5, 32, c((152, 24, 24)), c((72, 16, 16)))
    s.edit(1, fn)
    s.save(lang)


def boton_ok(box=(116, 153, 140, 163), sx=114, y=154, cx=128, ref=(114, 158)):
    """Boton 決定 -> OK. Los colores salen del texto original de cada pantalla:
    pixeles que difieren del fondo del boton (muestreado por fila en x=114).
    Texto oscuro -> trazo = color mas usado + sombra con el segundo.
    Texto claro (mas claro que el boton) -> relleno y borde por FILA, copiando
    el color mas claro / mas oscuro del original en esa fila (algunos botones
    tienen degradado en el texto)."""
    def fn(im):
        lum = lambda v: sum(im.rgb(v))
        cnt = {}; filas = {}
        for yy in range(box[1], box[3] + 1):
            bgc = im.get(sx, yy)
            difs = [im.get(x, yy) for x in range(box[0], box[2] + 1) if im.get(x, yy) != bgc]
            for v in difs:
                cnt[v] = cnt.get(v, 0) + 1
            if difs:
                filas[yy] = (max(difs, key=lum), min(difs, key=lum))
        orden = sorted(cnt, key=lambda v: -cnt[v])
        claro = lum(max(orden, key=lum)) > lum(im.get(*ref)) + 150
        erase(im, box, sx)
        if not claro:
            text(im, 'OK', 0, y, orden[0], orden[1] if len(orden) > 1 else None, center=cx)
            return
        gl_claro = max(orden, key=lum); gl_osc = min(orden, key=lum)
        umbral = lum(im.get(*ref)) + 150
        def fila(yy):
            k = min(filas, key=lambda f: abs(f - yy)); c, o = filas[k]
            return (c if lum(c) > umbral else gl_claro), o
        tmp = Img(im.w, im.h, im.pal, fill=-1)
        text(tmp, 'OK', 0, y, -2, center=cx, outline=-3)
        for yy in range(im.h):
            for x in range(im.w):
                v = tmp.get(x, yy)
                if v == -2: im.set(x, yy, fila(yy)[0])
                elif v == -3: im.set(x, yy, fila(yy)[1])
    return fn


def ev0(lang):
    L = 0 if lang == 'esp' else 1
    sc = Screen('EV0/S07/5', 'EV0/S07/0.NCLR')
    def fn(im):
        P = 26
        box = (98, 72, 152, 96)
        mask = lambda v: (lambda c: max(c) - min(c) < 40 or sum(c) < 250)(im.rgb(v))
        m = {(x, y) for y in range(box[1], box[3] + 1) for x in range(box[0], box[2] + 1) if mask(im.get(x, y))}
        for y in range(box[1], box[3] + 1):
            for x in range(box[0], box[2] + 1):
                if (x, y) in m:
                    im.set(x, y, im.get(x - P, y))
        text(im, T['cortando'][L], 0, 80, im.idx((248, 248, 248), False), center=125,
             outline=im.idx((24, 24, 24), False))
        boton_ok()(im)
    sc.edit(fn)
    sc.save(lang)


def ev9(lang):
    for n in range(2, 10):
        sc = Screen(f'EV9/S00/{n}', 'EV9/S00/0.NCLR')
        sc.edit(boton_ok())
        sc.save(lang)


# ------------------------------------------------------------- segunda pasada
# (2026-10-07; mockup aprobado: _scratch_claude/auditoria/mockup_celular2_parte*.png)
MENU = [('FOTO', 'PHOTO'), ('GRABAR', 'RECORD'), ('GUARDAR', 'SAVE')]
AVISOS = {2: ('GUARDANDO...', 'SAVING...'), 3: ('GRABANDO...', 'RECORDING...'),
          4: ('GUARDADO.', 'SAVED.'), 5: ('GRABADO.', 'RECORDED.'),
          6: ('¿GUARDAR?', 'SAVE?'), 7: ('BORRADO.', 'DELETED.'),
          28: ('GUARDANDO PARTIDA', 'SAVING GAME...'), 29: ('¿GUARDAR PARTIDA?', 'SAVE GAME?'),
          30: ('PARTIDA GUARDADA.', 'GAME SAVED.'), 31: ('ERROR.', 'FAILED.')}
SINO = {8: ('SI', 'YES'), 9: ('NO', 'NO'), 10: ('SI', 'YES'), 11: ('NO', 'NO')}
CELULARES = range(12, 20)   # MBP/G12..G19 (8 modelos de celular)


def gap_para(s, maxw):
    return None if F.width(s) <= maxw else 0


def mbp_menu(lang):
    """MBP/GxxS10: 撮影/録音/記録 (pares seleccionado/normal). Los 8 celulares
    tienen NCGR/NCER identicos: se edita una vez y se guarda con cada nombre."""
    L = 0 if lang == 'esp' else 1
    s = Sprite('MBP/G12S10')
    for k in range(6):
        t = MENU[k // 2][L]; st, sh = (3, 4) if k % 2 == 0 else (1, 2)
        def fn(im, t=t, st=st, sh=sh):
            erase(im, (7, 6, 104, 18), 10)
            text(im, t, 0, 8, st, sh, center=56)
        s.edit(k, fn)
    for n in CELULARES:
        s.save(lang, f'MBP/G{n}S10')


def mbp_avisos(lang):
    """MBP/GxxS11: avisos (guardar/grabar/borrar/partida) y Si/No. El NCER de
    G12 difiere del resto, asi que se procesa cada archivo por separado."""
    L = 0 if lang == 'esp' else 1
    for n in CELULARES:
        s = Sprite(f'MBP/G{n}S11', 'MBP/G12S10.NCLR')
        for ci, t in AVISOS.items():
            def fn(im, t=t[L]):
                erase(im, (5, 8, 121, 23), 6)
                text(im, t, 0, 12, 2, 3, center=64, gap=gap_para(t, 114))
            s.edit(ci, fn)
        for ci, t in SINO.items():
            def fn(im, t=t[L]):
                erase(im, (6, 8, 57, 23), 7)
                text(im, t, 0, 12, 2, 3, center=32)
            s.edit(ci, fn)
        s.save(lang)


MICRO = {
    'S': ["###", "#..", "###", "..#", "###"], 'I': ["###", ".#.", ".#.", ".#.", "###"],
    'N': ["#.#", "###", "###", "###", "#.#"], 'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'E': ["###", "#..", "##.", "#..", "###"], 'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'O': ["###", "#.#", "#.#", "#.#", "###"], 'V': ["#.#", "#.#", "#.#", "#.#", ".#."],
    'C': ["###", "#..", "#..", "#..", "###"],
}


def micro(im, s, cx, y, v):
    """Fuente 3x5 para el icono 圏外 (18 px de ancho util)."""
    x = cx - (len(s) * 4 - 1) // 2
    for i, ch in enumerate(s):
        for yy, row in enumerate(MICRO[ch]):
            for xx, c in enumerate(row):
                if c == '#':
                    im.set(x + i * 4 + xx, y + yy, v)


def sin_senal(lang):
    """EV9/T/xxS10 celda 13: 圏外 -> SIN/RED (NO/SVC), 10 celulares."""
    L = 0 if lang == 'esp' else 1
    a, b = (('SIN', 'RED'), ('NO', 'SVC'))[L]
    for n in range(12, 22):
        s = Sprite(f'EV9/T/{n}S10')
        def fn(im):
            for y in range(1, 15):
                vals = [im.get(x, y) for x in range(6, 23) if im.get(x, y) not in (0, 1)]
                bg = max(set(vals), key=vals.count) if vals else 13
                for x in range(6, 23):
                    im.set(x, y, bg)
            micro(im, a, 14, 2, 1); micro(im, b, 14, 8, 1)
        s.edit(13, fn)
        s.save(lang)


def r07(lang):
    """Pantallas de llamada: 呼び出し中 / 通話中 / 終了しました / 切断中."""
    L = 0 if lang == 'esp' else 1
    LLAMANDO = ('LLAMANDO...', 'CALLING...')[L]
    HABLANDO = ('EN LLAMADA', 'ON CALL')[L]
    def contorno(box, sx, cx, y, t):
        def fn(im):
            white = im.idx((240, 240, 240))
            erase(im, box, sx)
            text(im, t, 0, y, white, center=cx, outline=1)
        return fn
    s = Sprite('R07/A_S10')
    for ci in (0, 1, 2):
        s.edit(ci, contorno((44, 85, 116, 102), 40, 80, 90, LLAMANDO))
    def burbuja(im):
        for y in range(48, 65):
            for x in range(30, 92):
                if im.get(x, y) == 1:
                    im.set(x, y, 6)
        text(im, HABLANDO, 0, 52, 1, center=60, gap=gap_para(HABLANDO, 50))
    s.edit(3, burbuja)
    def terminada(im):
        for y in range(56, 69):
            for x in range(42, 121):
                im.set(x, y, 6)
        text(im, ('TERMINADA', 'CALL ENDED')[L], 0, 58, 1, 5, center=81)
    s.edit(4, terminada)
    s.save(lang)
    for x in ('B', 'C'):
        s = Sprite(f'R07/{x}_S10')
        for ci in (0, 1, 2):
            s.edit(ci, contorno((44, 30, 118, 47), 42, 80, 35, LLAMANDO))
        s.edit(4, contorno((72, 54, 121, 73), 70, 97, 59, HABLANDO))
        if x == 'C':
            s.edit(3, contorno((54, 30, 103, 47), 52, 80, 35, ('CORTANDO', 'HANGING UP')[L]))
        s.save(lang)


def r21(lang):
    """番号入力 -> MARCAR / DIAL."""
    L = 0 if lang == 'esp' else 1
    s = Sprite('R21/A_S10')
    def fn(im):
        erase(im, (22, 4, 75, 14), 100)
        text(im, ('MARCAR', 'DIAL')[L], 24, 4, 3, 4)
    s.edit(0, fn)
    s.save(lang)


def ev9_s01(lang):
    """Otros 2 fondos de pantalla con boton 決定 (EV9/S01/0-1)."""
    for n, box, sx, cx, ref in ((0, (114, 155, 141, 161), 113, 128, (116, 157)), (1, (113, 154, 145, 161), 113, 129, (115, 158))):
        sc = Screen(f'EV9/S01/{n}', 'EV9/S01/0.NCLR')
        sc.edit(boton_ok(box=box, sx=sx, y=154, cx=cx, ref=ref))
        sc.save(lang)


ERRORES = {0: (["NO SE PUDIERON LEER LOS DATOS.", "APAGA LA CONSOLA Y VUELVE A", "INSERTAR LA TARJETA DE JUEGO."],
               ["THE DATA COULD NOT BE READ.", "TURN THE POWER OFF AND", "REINSERT THE GAME CARD."]),
           1: (["LOS DATOS DE GUARDADO ESTABAN", "DAÑADOS Y SE REINICIARON.", "PULSA A PARA EMPEZAR EL JUEGO."],
               ["THE SAVE DATA WAS CORRUPTED,", "SO IT HAS BEEN RESET.", "PRESS A TO START THE GAME."])}


def errores(lang):
    """ERROR/ErrorMessage00: errores de la partida guardada. Fondo degradado
    por fila tomado del borde derecho (x 238-243, sin texto)."""
    L = 0 if lang == 'esp' else 1
    s = Sprite('ERROR/ErrorMessage00')
    for ci, lineas in ERRORES.items():
        def fn(im, lineas=lineas[L]):
            for y in range(4, 60):
                vals = [im.get(x, y) for x in range(238, 244)]
                bg = max(set(vals), key=vals.count)
                for x in range(12, 244):
                    im.set(x, y, bg)
            for i, line in enumerate(lineas):
                text(im, line, 18, 9 + 18 * i, 1, outline=14)
        s.edit(ci, fn)
    s.save(lang)


# --- avisos al encender (LOGO, 8bpp) con la fuente de dialogo TWSFont
from nftr import NFTR
import importlib.util


def _generador(lang):
    path = os.path.join(ROOT, 'generar_rom_%s.py' % lang)
    spec = importlib.util.spec_from_file_location('gen_' + lang, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def tws(im, s, x, y, lang, cols, center=None):
    """Dibuja s con TWSFont (la misma del dialogo del idioma) usando los
    indices cols[1..3] para los valores 2bpp del glifo."""
    G = _generador(lang); f = NFTR(open(os.path.join(ROOT, G.FONT_PATH), 'rb').read())
    gl = [None if c == 0x20 else f.lookup(c) for c in G.encode_text(s)[:-1]]
    w = sum(G.SPACE_WIDTH if g is None else f.width(g)[2] for g in gl)
    if center is not None:
        x = center - w // 2
    for g in gl:
        if g is None:
            x += G.SPACE_WIDTH; continue
        b, gw, adv = f.width(g)
        for yy, row in enumerate(f.glyph(g)):
            for xx, v in enumerate(row):
                if v:
                    im.set(x + b + xx, y + yy, cols[v])
        x += adv
    return w


AVISO_FICCION = (["Esta obra es ficción.", "No guarda relación con", "personas, grupos ni", "hechos reales.", "",
                  "Por favor, no imites", "nada de lo que ocurre", "en ella."],
                 ["This work is fiction.", "It has no relation to", "real people, groups", "or events.", "",
                  "Please do not imitate", "anything that happens", "in it."])
AVISO_AUDIFONOS = (("Usa audífonos", ["Este juego usa", "sonido 3D.", "Disfrútalo con", "audífonos estéreo."]),
                   ("Use headphones", ["This game uses", "3D sound.", "Enjoy it with", "stereo headphones."]))


def logo(lang):
    L = 0 if lang == 'esp' else 1
    for base, ficcion in (('LOGO/P01M01', True), ('LOGO/P01M02', False)):
        s = Sprite(base, 'LOGO/P01M01.NCLR')
        def fn(im):
            cnt = {}
            for y in range(192):
                for x in range(256):
                    v = im.get(x, y); cnt[v] = cnt.get(v, 0) + 1
            bg = max(cnt, key=cnt.get)
            cols = [None, im.idx((248, 248, 248), False), im.idx((60, 60, 60), False), im.idx((150, 150, 150), False)]
            if ficcion:
                for y in range(192):
                    for x in range(256):
                        im.set(x, y, bg)
                for i, line in enumerate(AVISO_FICCION[L]):
                    if line:
                        tws(im, line, 0, 26 + 17 * i, lang, cols, center=128)
            else:
                for y in range(36, 157):
                    for x in range(72, 256):
                        im.set(x, y, bg)
                tit, body = AVISO_AUDIFONOS[L]
                tws(im, tit, 0, 50, lang, cols, center=166)
                for i, line in enumerate(body):
                    tws(im, line, 84, 78 + 17 * i, lang, cols)
        s.edit(0, fn)
        s.save(lang)


def main():
    for lang in ('esp', 'eng'):
        for f in (r02a, r02b, r09, r10, r24, ev0, ev9,
                  mbp_menu, mbp_avisos, sin_senal, r07, r21, ev9_s01, errores, logo):
            f(lang)
            print(lang, f.__name__, 'ok')


if __name__ == '__main__':
    main()
