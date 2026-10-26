#!/usr/bin/env python3
"""
redibujar_fotos_correo2.py - Traduce las otras 4 fotos del celular con un correo de fondo:
  EV5/M14/4  correo #100 (celular morado)        EV5/M15/5  correo #100 (pantalla rota)
  EV3/M06/7  correo #44                          EV3/M06/8  correo #43
Misma tecnica que redibujar_fotos_correo.py: se detecta el texto japones, se borra
rellenando cada pixel con el vecino limpio de su misma columna (conserva rayas y
grietas) y se pinta la traduccion con la fuente del celular.
Titulo 受信メール -> BANDEJA / INBOX; boton 決定 -> OK.
Uso: python3 scripts/redibujar_fotos_correo2.py [--prev]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import redibujar_ui_celular as R

HEAD = {'esp': 'BANDEJA', 'eng': 'INBOX'}
# base, nclr, banco de paleta (solo para mirar), (y0,y1) de cada linea, textos
CFG = {
 'EV5/M14/4': dict(nclr='EV5/M14/0.NCLR', pb=None, ref=None,
    bands=[(56,65),(68,78),(81,91),(94,104)],
    esp=['AHORA','ESTOY','DETRAS','DE TI'], eng=['NOW','I AM','BEHIND','YOU']),
 'EV5/M15/5': dict(nclr='EV5/M15/0.NCLR', pb=None, ref='EV5/M14/4',
    bands=[(56,65),(68,78),(81,91),(94,104)],
    esp=['AHORA','ESTOY','DETRAS','DE TI'], eng=['NOW','I AM','BEHIND','YOU']),
 'EV3/M06/7': dict(nclr='EV3/M06/0.NCLR', pb=1, ref=None,
    bands=[(43,60),(63,79),(81,98),(100,117),(120,136)],
    esp=['LEYENDA "EL HOMBRE','BAJO LA CAMA"','NACIO DE UN CRIMEN','EN HEIGHTS','KIRIZUKA'],
    eng=['URBAN LEGEND "THE','MAN UNDER THE BED"','WAS BORN FROM A','MURDER AT HEIGHTS','KIRIZUKA']),
 'EV3/M06/8': dict(nclr='EV3/M06/0.NCLR', pb=1, ref=None,
    bands=[(43,60),None,(81,98),(101,117),(120,136)],
    esp=['PASALO A 6 PERSONAS',None,'EN HITORI KAKURENBO','SI VES AL ONI','SERAS MALDITO'],
    eng=['SEND THIS TO 6 PEOPLE',None,'IN HITORI KAKURENBO','IF YOU SEE THE ONI','YOU WILL BE CURSED']),
}
X0, X1 = 51, 205
EV3 = dict(X=(16, 243), tx=18, tm=(42, 150), tx0=47, tthr=12, tyl=(17, 34), sc=1.5, bsc=1.5, boton=False, ylim=(36, 140))
EV5 = dict(X=(51, 205), tx=52, tm=(64, 126), tx0=66, tthr=60, tyl=(23, 36), sc=1.0, bsc=1.3, boton=True, ylim=(20, 146))


def text_sc(im, s, x, y, col, sc):
    if sc == 1.0:
        R.text(im, s, x, y, col); return
    m = R.F.render(s, top=0, cell_h=10)
    W = len(m[0]); H = len(m)
    for yy in range(int(H * sc)):
        for xx in range(int(W * sc)):
            if m[int(yy / sc)][int(xx / sc)] == 1:
                im.set(x + xx, y + yy, col)


def _mask(sc, im, y0, y1, x0, x1, thr):
    lum = lambda v: sum(sc.pal[v])
    m = set()
    for y in range(y0, y1 + 1):
        L = sorted(lum(im.p[y][x]) for x in range(x0, x1 + 1))
        med = L[len(L) // 2]
        for x in range(x0, x1 + 1):
            if lum(im.p[y][x]) < med - thr:
                m.add((x, y))
    return m


def _dilate(m, r=1):
    o = set(m)
    for (x, y) in m:
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                o.add((x + dx, y + dy))
    return o


def _fill(im, mask, ylim, xlim):
    """cada pixel enmascarado toma el del vecino limpio mas cercano en su columna
    (arriba/abajo); si no hay, el de la misma fila a la derecha."""
    new = {}
    for (x, y) in mask:
        up = down = None
        for d in range(1, 14):
            if up is None and (x, y - d) not in mask and y - d >= ylim[0]: up = (x, y - d)
            if down is None and (x, y + d) not in mask and y + d <= ylim[1]: down = (x, y + d)
            if up and down: break
        c = None
        if up and down:
            c = up if (y - up[1]) <= (down[1] - y) else down
        else:
            c = up or down
        if c is None:
            xx = x
            while (xx, y) in mask and xx < xlim[1]: xx += 1
            c = (xx, y)
        new[(x, y)] = im.p[c[1]][c[0]]
    for (x, y), v in new.items():
        im.p[y][x] = v


def _fill_row(im, mask, xlim):
    """cada pixel enmascarado toma el del vecino limpio mas cercano de su MISMA fila
    (conserva el tinte/ruido horizontal de la foto)."""
    new = {}
    for (x, y) in mask:
        c = None
        for d in range(1, 40):
            l, r = x - d, x + d
            if l >= xlim[0] and (l, y) not in mask: c = (l, y); break
            if r <= xlim[1] and (r, y) not in mask: c = (r, y); break
        if c is None: c = (x, y)
        new[(x, y)] = im.p[c[1]][c[0]]
    for (x, y), v in new.items():
        im.p[y][x] = v


def build(base, lang, screen_cache={}):
    c = CFG[base]
    P = EV3 if base.startswith('EV3') else EV5
    X0, X1 = P['X']
    sc = R.Screen(base, c['nclr'], c['pb'])
    refsc = R.Screen(c['ref'], CFG[c['ref']]['nclr'], CFG[c['ref']]['pb']) if c['ref'] else None

    def fn(im):
        lum = lambda v: sum(im.rgb(v))
        if refsc:
            ri = R.Img(refsc.W, refsc.H, refsc.pal)
            for y in range(refsc.H):
                for x in range(refsc.W): ri.p[y][x] = refsc.ncgr[refsc.off(x, y)]
            src = ri
        else:
            src = im
        slum = lambda v: sum(sc.pal[v]) if not refsc else sum(refsc.pal[v])
        # ---- cuerpo
        mask = set(); dark = None
        for b in c['bands']:
            if b is None: continue
            m = set()
            for y in range(b[0] - 1, b[1] + 2):
                L = sorted(slum(src.p[y][x]) for x in range(X0, X1 + 1))
                med = L[len(L) // 2]
                for x in range(X0, X1 + 1):
                    if slum(src.p[y][x]) < med - (120 if base.startswith('EV3') else 35): m.add((x, y))
            mask |= m
        dm = min(mask, key=lambda p: slum(src.p[p[1]][p[0]]))
        dark = src.p[dm[1]][dm[0]]
        if base.startswith('EV3'):
            _fill_row(im, _dilate(mask), (X0, X1))
        else:
            _fill(im, _dilate(mask), P['ylim'], (X0, X1))
        for b, s in zip(c['bands'], c[lang]):
            if b is None or s is None: continue
            y0 = (b[0] + b[1]) // 2 - int(4.5 * P['bsc'])
            text_sc(im, s, P['tx'], y0, dark, P['bsc'])
        # ---- titulo
        tm = _mask(sc if not refsc else refsc, src, 22, 38, P['tm'][0], P['tm'][1], P['tthr'])
        tdm = min(tm, key=lambda p: slum(src.p[p[1]][p[0]]))
        tdark = src.p[tdm[1]][tdm[0]]
        tm = {p for p in _dilate(tm, 2) if P['tyl'][0] <= p[1] <= P['tyl'][1]}
        if base.startswith('EV3'):
            for y in range(P['tyl'][0], P['tyl'][1] + 1):
                for x in range(P['tm'][0], P['tm'][1] + 1):
                    im.p[y][x] = im.p[y][P['tm'][1] + 2]
        else:
            _fill(im, tm, P['tyl'], (P['tm'][0], X1))
        ty = [y for _, y in tm]
        yc = (min(ty) + max(ty)) // 2
        text_sc(im, HEAD[lang], P['tx0'], yc - int(4.5 * P['sc']), tdark, P['sc'])
        if not P['boton']: return
        # ---- boton
        box = (116, 153, 140, 163); sx = 114
        cols = [im.get(x, y) for y in range(box[1], box[3] + 1) for x in range(box[0], box[2] + 1) if im.get(x, y) != im.get(sx, y)]
        oscuro = min(cols, key=lambda v: sum(im.rgb(v)))
        R.erase(im, box, sx)
        R.text(im, 'OK', 0, 154, oscuro, None, center=128)
    sc.edit(fn)
    sc.save(lang)
    return sc


def main():
    for base in CFG:
        for lang in ('esp', 'eng'):
            build(base, lang)
    print('fotos EV5/M14/4, EV5/M15/5, EV3/M06/7, EV3/M06/8 generadas (esp, eng)')


if __name__ == '__main__':
    main()
