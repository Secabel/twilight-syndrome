#!/usr/bin/env python3
"""
traducir_carteles_ev9_m02.py - Traduce las 7 laminas de EV9/M02/0-6.NCGR
(pantalla previa a cada historia: nombre del arco a la izquierda y "N-esimo
rumor" a la derecha, texto vertical en rojo sobre grano tipo VHS).

Misma idea que traducir_saveload.py: se borra el texto japones copiando grano
de una zona limpia (misma fila, para conservar las rayas horizontales) y se
dibuja el texto nuevo horizontal con brillo rojo. Diferencia: la paleta es de
16 bancos de 256 colores (cada lamina usa uno) y NO es una rampa, asi que cada
pixel nuevo se cuantiza al color mas cercano del banco de esa lamina.

Los NSCR y la NCLR no se tocan: solo cambia el .NCGR (mismo tamano).

Uso: python3 scripts/traducir_carteles_ev9_m02.py [--out DIR] [--previews DIR]
Por defecto escribe en rea_analisis/carteles_ev9_m02/{esp,eng}/EV9/M02/N.NCGR.
Para instalarlas: copiar esos .NCGR a assets/graficos/{esp,eng}/EV9/M02/.
"""
import os
import struct
import sys

sys.path.insert(0, 'scripts')
from inventario_completo import (decode_ncgr, decode_nclr, decode_nscr,
                                 render_nscr, parse_container)
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = 'extraccion_rom/root/EV9/M02/'
FONT_PATHS = ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
W, H = 256, 192
TILES_X, TILES_Y = 32, 24

# (arco, etiqueta de rumor) por lamina 0-6
TEXTOS = {
    'esp': [
        ('El Kokkuri-san del edificio viejo', 'El rumor inicial'),
        ('Mail de desaparición', 'El primer rumor'),
        ('El andén fantasma', 'El segundo rumor'),
        ('Hitori Kakurenbo', 'El tercer rumor'),
        ('El parque de diversiones de terror', 'El cuarto rumor'),
        ('Las cien leyendas urbanas', 'El quinto rumor'),
        ('Foto paranormal', 'El último rumor'),
    ],
    'eng': [
        ('The Kokkuri-san of the Old Building', 'The Beginning Rumor'),
        ('Vanishing Mail', 'The First Rumor'),
        ('The Phantom Platform', 'The Second Rumor'),
        ('Hitori Kakurenbo', 'The Third Rumor'),
        ('The Scary Theme Park', 'The Fourth Rumor'),
        ('The Hundred Urban Legends', 'The Fifth Rumor'),
        ('Psychic Photograph', 'The Final Rumor'),
    ],
}

# zonas de texto nuevas (x, y, ancho, alto) en pixeles
ZONA_ARCO = (10, 30, 236, 64)
ZONA_RUMOR = (10, 108, 236, 30)


def load_font(size):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def es_rojo(c):
    r, g, b = c[:3]
    return r > 60 and r > g * 1.8 and r > b * 1.8


def ajustar(text, w, h, max_size, min_size=9, max_lines=2):
    """Devuelve (lineas, fuente) con la letra mas grande que entra en w x h."""
    probe = ImageDraw.Draw(Image.new('L', (4, 4)))
    words = text.split(' ')
    for size in range(max_size, min_size - 1, -1):
        font = load_font(size)
        cands = [[text]]
        if max_lines >= 2 and len(words) > 1:
            best = None
            for i in range(1, len(words)):
                a, b = ' '.join(words[:i]), ' '.join(words[i:])
                wa = probe.textlength(a, font=font)
                wb = probe.textlength(b, font=font)
                m = max(wa, wb)
                if best is None or m < best[0]:
                    best = (m, [a, b])
            cands.append(best[1])
        for lines in cands:
            lh = font.getbbox('Ag')[3] - font.getbbox('Ag')[1] + 3
            if (max(probe.textlength(l, font=font) for l in lines) <= w - 6
                    and lh * len(lines) <= h):
                return lines, font
    return [text], load_font(min_size)


def texto_glow(text, zona, size):
    """Mascara L (0-255) del tamano de la lamina con el texto centrado en zona."""
    x0, y0, w, h = zona
    lines, font = ajustar(text, w, h, size, min_size=size)
    core = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(core)
    lh = font.getbbox('Ag')[3] - font.getbbox('Ag')[1] + 3
    total = lh * len(lines)
    y = y0 + (h - total) // 2
    for l in lines:
        tw = d.textlength(l, font=font)
        d.text((x0 + (w - tw) / 2, y - font.getbbox('Ag')[1]), l, font=font, fill=255)
        y += lh
    glow = core.filter(ImageFilter.GaussianBlur(1.6)).point(lambda v: int(v * 0.75))
    out = Image.new('L', (W, H), 0)
    po, pc, pg = out.load(), core.load(), glow.load()
    for yy in range(H):
        for xx in range(W):
            po[xx, yy] = max(pc[xx, yy], pg[xx, yy])
    return out


def procesar(n, textos_idioma, tam):
    nclr = decode_nclr(ROOT + '0.NCLR')
    gpath = ROOT + f'{n}.NCGR'
    orig = open(gpath, 'rb').read()
    ncgr = decode_ncgr(gpath)
    d = decode_nscr(ROOT + f'{n}.NSCR')
    ent = d['entries']
    banks = {e[3] for e in ent}
    assert len(banks) == 1 and all(not e[1] and not e[2] for e in ent), 'NSCR no uniforme'
    assert len({e[0] for e in ent}) == len(ent), 'tiles compartidos'
    bank = banks.pop()
    pal = nclr[bank * 256:(bank + 1) * 256]
    td = bytearray(ncgr['tile_data'])

    def off(x, y):
        return ent[(y // 8) * TILES_X + x // 8][0] * 64 + (y % 8) * 8 + x % 8

    px = [[td[off(x, y)] for x in range(W)] for y in range(H)]

    # columnas de tiles con rojo (texto original)
    col_rojo = [0] * TILES_X
    for y in range(H):
        for x in range(W):
            if es_rojo(pal[px[y][x]]):
                col_rojo[x // 8] += 1
    umbral = 3
    rojas = [tx for tx in range(TILES_X) if col_rojo[tx] > umbral]
    izq = [tx for tx in rojas if tx < 16]
    der = [tx for tx in rojas if tx >= 16]
    l0, l1 = (max(0, min(izq) - 1), min(izq and max(izq) + 1, 31)) if izq else (0, -1)
    r0, r1 = (max(0, min(der) - 1), min(31, max(der) + 1)) if der else (32, 31)
    borrar = set(range(l0, l1 + 1)) | set(range(r0, r1 + 1))
    limpias = [tx for tx in range(TILES_X) if tx not in borrar and col_rojo[tx] <= umbral]
    # tramo contiguo mas largo de columnas limpias como origen de grano
    best, cur = [], []
    for tx in limpias:
        cur = cur + [tx] if cur and tx == cur[-1] + 1 else [tx]
        if len(cur) > len(best):
            best = cur[:]
    src = best
    assert len(src) >= 4, f'poco grano limpio en lamina {n}: {src}'
    # 1) borrar copiando la misma fila del grano limpio
    sx0 = src[0] * 8
    sw = len(src) * 8
    for tx in sorted(borrar):
        for y in range(H):
            for k in range(8):
                x = tx * 8 + k
                px[y][x] = px[y][sx0 + (x - tx * 8 + tx * 8) % sw]
    # 2) texto nuevo
    arco, rumor = textos_idioma[n]
    m1 = texto_glow(arco, ZONA_ARCO, tam[0])
    m2 = texto_glow(rumor, ZONA_RUMOR, tam[1])
    rojo_nucleo = ROJO   # un unico rojo para las 7 laminas (ver rojo_comun)
    cache = {}

    def cuantizar(rgb):
        if rgb not in cache:
            cache[rgb] = min(range(1, 256),
                             key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i][:3], rgb)))
        return cache[rgb]

    for m in (m1, m2):
        pm = m.load()
        for y in range(H):
            for x in range(W):
                v = pm[x, y]
                if v < 12:
                    continue
                t = v / 255.0
                fondo = pal[px[y][x]][:3]
                nuevo = tuple(int(max(f, f * (1 - t) + c * t)) for f, c in zip(fondo, rojo_nucleo))
                px[y][x] = cuantizar(nuevo)
    # 3) escribir de vuelta
    for y in range(H):
        for x in range(W):
            td[off(x, y)] = px[y][x]
    magic, blocks = parse_container(orig)
    char_off = next(o for o, bm, bs in blocks if bm == b'RAHC')
    start = char_off + 8 + struct.unpack_from('<I', orig, char_off + 28)[0]
    nuevo = bytearray(orig)
    nuevo[start:start + len(td)] = td
    assert len(nuevo) == len(orig)
    ncgr_p = dict(ncgr)
    ncgr_p['tile_data'] = bytes(td)
    return bytes(nuevo), render_nscr(d, ncgr, nclr), render_nscr(d, ncgr_p, nclr), (l0, l1, r0, r1, src[0], src[-1])


ROJO = None
TAM = {}


def rojo_comun():
    """Rojo unico: el que peor error de cuantizacion tiene lo menos posible
    en los 7 bancos de paleta (cada lamina usa un banco distinto)."""
    nclr = decode_nclr(ROOT + '0.NCLR')
    pals = []
    for n in range(7):
        b = decode_nscr(ROOT + f'{n}.NSCR')['entries'][0][3]
        pals.append(nclr[b * 256:(b + 1) * 256])
    cands = {c[:3] for p in pals for c in p[1:] if es_rojo(c) and c[0] >= 190}

    def peor(c):
        return max(min(sum((a - b) ** 2 for a, b in zip(q[:3], c)) for q in p[1:]) for p in pals)
    return min(cands, key=peor)


def calcular_tamanos():
    """Un solo tamano de letra para todos los arcos y otro para todas las
    etiquetas de rumor, por idioma: el mayor que entra en el caso mas largo."""
    for idioma, pares in TEXTOS.items():
        ta = min(ajustar(a, ZONA_ARCO[2], ZONA_ARCO[3], 22)[1].size for a, _ in pares)
        tr = min(ajustar(r, ZONA_RUMOR[2], ZONA_RUMOR[3], 16)[1].size for _, r in pares)
        tr = min(tr, ta - 3)   # la etiqueta siempre menor que el titulo
        TAM[idioma] = (ta, tr)


def main():
    global ROJO
    ROJO = rojo_comun()
    calcular_tamanos()
    print('rojo unico', ROJO, 'tamanos (arco, rumor)', TAM)
    args = sys.argv[1:]
    out = 'rea_analisis/carteles_ev9_m02'
    prev = None
    if '--out' in args:
        out = args[args.index('--out') + 1]
    if '--previews' in args:
        prev = args[args.index('--previews') + 1]
    prev = prev or out + '/previews'
    os.makedirs(prev, exist_ok=True)
    for idioma in ('esp', 'eng'):
        carpeta = os.path.join(out, idioma, 'EV9', 'M02')
        os.makedirs(carpeta, exist_ok=True)
        pares = []
        for n in range(7):
            data, antes, despues, info = procesar(n, TEXTOS[idioma], TAM[idioma])
            open(os.path.join(carpeta, f'{n}.NCGR'), 'wb').write(data)
            print(idioma, n, 'borrado tx izq', info[0:2], 'der', info[2:4], 'grano', info[4:6])
            pares.append((antes, despues))
        hoja = Image.new('RGB', (W * 2 + 12, (H + 6) * 7), (20, 20, 20))
        for i, (a, b) in enumerate(pares):
            hoja.paste(a.convert('RGB'), (0, i * (H + 6)))
            hoja.paste(b.convert('RGB'), (W + 12, i * (H + 6)))
        hoja.save(os.path.join(prev, f'antes_despues_{idioma}.png'))
        for i, (a, b) in enumerate(pares):
            b.convert('RGB').resize((W * 2, H * 2), Image.NEAREST).save(
                os.path.join(prev, f'{idioma}_{i}.png'))


if __name__ == '__main__':
    main()
