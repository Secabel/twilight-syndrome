#!/usr/bin/env python3
"""
redibujar_correos.py - Redibuja las lineas de los correos del celular
(R08/*_S10, sprites NCER: una celda = una linea) con la fuente del celular
(scripts/fuente_celular.py) y genera NCGR+NCER por idioma en
assets/graficos/<esp|eng>/R08/.

Uso:  python3 scripts/redibujar_correos.py [GRUPO[:celdas] ...]
  ej: python3 scripts/redibujar_correos.py A B I:5,7,8,9,10,11,12
Sin argumentos procesa todos los grupos y celdas traducibles del CSV.

Lee siempre los archivos ORIGINALES en japones: de extraccion_rom/root/R08
si existe, o si no directo de la ROM japonesa limpia (misma que usan los
generadores, en la raiz del repo). Nunca de una ROM ya parcheada. Textos: assets/csv/correos_celular.csv.

- Celdas CUERPO/DE: se borran los tiles de texto y se pinta la traduccion
  alineada a la izquierda donde empezaba la tinta original. DE conserva el
  icono (OBJ 16x16 de la izquierda).
- Celdas LETRA (animacion de letras sueltas, 16x16): letra centrada.
- Si la traduccion no entra, se agregan OBJs a la derecha (tiles nuevos al
  final del NCGR, alineados a 4 tiles por tile_boundary_shift=2) y se
  actualiza el radio de la celda en el NCER.
- Fechas, numeros, ---END---, Fw: y el texto corrupto (GLITCH) no se tocan.
"""
import csv, os, struct, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import ncer_decode as ic
import fuente_celular as F

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'extraccion_rom/root/R08')
CSV = os.path.join(ROOT, 'assets/csv/correos_celular.csv')
TIPOS = ('CUERPO', 'DE', 'LETRA')
MARGEN = 2  # px desde el borde izquierdo del area de texto
# shape/size -> attr0 shape bits, attr1 size bits (OBJ de 16 px de alto)
OBJ_16H = {32: (1, 2), 16: (0, 1), 8: (2, 0)}


BASE_ROM = os.path.join(ROOT, 'Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds')
_rom = None


def read_original(name):
    """Archivo original de R08 (ej. 'B_S10.NCGR')."""
    global _rom
    path = os.path.join(SRC, name)
    if os.path.exists(path):
        return open(path, 'rb').read()
    if _rom is None:
        import ndspy.rom
        _rom = ndspy.rom.NintendoDSRom.fromFile(BASE_ROM)
    return _rom.getFileByName('R08/' + name)


def load_csv():
    out = {}
    for r in csv.DictReader(open(CSV, encoding='utf-8-sig')):
        out.setdefault(r['grupo'], {})[int(r['celda'])] = r
    return out


class Ncer:
    def __init__(self, data):
        self.d = bytearray(data)
        magic, blocks = ic.parse_container(bytes(self.d))
        assert magic == b'RECN'
        self.kbec_off, _, self.kbec_size = next(b for b in blocks if b[1] == b'KBEC')
        h = self.kbec_off + 8
        self.count, ctype = struct.unpack_from('<HH', self.d, h)
        assert ctype == 0, 'solo celdas de 8 bytes'
        self.tbs = struct.unpack_from('<I', self.d, h + 8)[0]
        self.ca = h + 24
        self.oa = self.ca + self.count * 8
        self.cells = []
        for i in range(self.count):
            n, attr, off = struct.unpack_from('<HHI', self.d, self.ca + i * 8)
            objs = [list(struct.unpack_from('<HHH', self.d, self.oa + off + j * 6)) for j in range(n)]
            self.cells.append({'attr': attr, 'objs': objs})

    def build(self):
        objbytes = bytearray(); entries = bytearray()
        for c in self.cells:
            entries += struct.pack('<HHI', len(c['objs']), c['attr'], len(objbytes))
            for o in c['objs']:
                objbytes += struct.pack('<HHH', *o)
        old_end = self.kbec_off + self.kbec_size
        new_kbec = bytes(self.d[self.kbec_off:self.ca]) + bytes(entries) + bytes(objbytes)
        # conservar relleno que hubiera al final del KBEC original
        old_payload_end = self.oa + sum(len(c['objs']) for c in Ncer(self.d).cells) * 6
        new_kbec += bytes(self.d[old_payload_end:old_end])
        out = bytearray(self.d[:self.kbec_off]) + bytearray(new_kbec) + self.d[old_end:]
        struct.pack_into('<I', out, self.kbec_off + 4, len(new_kbec))
        struct.pack_into('<I', out, 8, len(out))
        return bytes(out)


class Ncgr:
    def __init__(self, data):
        self.d = bytearray(data)
        magic, blocks = ic.parse_container(bytes(self.d))
        self.rahc_off, _, self.rahc_size = next(b for b in blocks if b[1] == b'RAHC')
        assert self.rahc_off + self.rahc_size == len(self.d), 'RAHC debe ser el ultimo bloque'
        rel = struct.unpack_from('<I', self.d, self.rahc_off + 28)[0]
        self.px_off = self.rahc_off + 8 + rel

    def ntiles(self):
        return (len(self.d) - self.px_off) // 32

    def add_tiles(self, n):
        # alinear a 4 tiles (tile_boundary_shift = 2)
        pad = (-self.ntiles()) % 4
        first = self.ntiles() + pad
        self.d.extend(bytes(32 * (pad + n)))
        size = len(self.d) - self.px_off
        struct.pack_into('<I', self.d, self.rahc_off + 24, size)
        struct.pack_into('<I', self.d, self.rahc_off + 4, len(self.d) - self.rahc_off)
        struct.pack_into('<I', self.d, 8, len(self.d))
        return first

    def set_px(self, tile, lx, ly, v):
        off = self.px_off + tile * 32 + ly * 4 + lx // 2
        b = self.d[off]
        self.d[off] = (b & 0xF0) | v if lx % 2 == 0 else (b & 0x0F) | (v << 4)

    def get_px(self, tile, lx, ly):
        b = self.d[self.px_off + tile * 32 + ly * 4 + lx // 2]
        return b & 0xF if lx % 2 == 0 else b >> 4


def geom(o, tbs):
    return ic.obj_geometry(*o, tile_boundary_shift=tbs)


def obj_pixels(ncgr, g):
    """Itera (x, y, tile, lx, ly) en coordenadas de celda para un OBJ."""
    wt = g['w'] // 8
    for ly in range(g['h']):
        for lx in range(g['w']):
            t = g['tile_idx'] + (ly // 8) * wt + lx // 8
            yield g['x'] + lx, g['y'] + ly, t, lx % 8, ly % 8


def first_ink_x(ncgr, objs, tbs):
    xs = [x for o in objs for (x, y, t, lx, ly) in obj_pixels(ncgr, geom(o, tbs)) if ncgr.get_px(t, lx, ly)]
    return min(xs) if xs else None


def cell_radius(objs, tbs):
    r = 0
    for o in objs:
        g = geom(o, tbs)
        for x in (g['x'], g['x'] + g['w']):
            for y in (g['y'], g['y'] + g['h']):
                r = max(r, math.hypot(x, y))
    return math.ceil(r / 4)


def redraw_cell(ncgr, ncer, idx, text, tipo):
    cell = ncer.cells[idx]; tbs = ncer.tbs
    objs = cell['objs']
    if tipo == 'DE':
        # el icono es el OBJ 16x16 de mas a la izquierda
        icon = min(objs, key=lambda o: geom(o, tbs)['x'])
        text_objs = [o for o in objs if o is not icon]
    else:
        text_objs = list(objs)
    gs = [geom(o, tbs) for o in text_objs]
    for g in gs:
        assert g['h'] == 16 and g['y'] == -8, (idx, g)
    xs = min(g['x'] for g in gs); xe = max(g['x'] + g['w'] for g in gs)
    ink = first_ink_x(ncgr, text_objs, tbs)
    if tipo == 'LETRA':
        # animacion de letras sueltas: si no entra en la celda, sin espacio entre letras
        gap = None if F.width(text) <= xe - xs else 0
        m = F.render(text, gap=gap)
        w = F.width(text, gap)
        x0 = xs + (xe - xs - w) // 2
    else:
        x0 = xs + MARGEN   # margen fijo: todas las lineas alineadas
        if text.startswith(' '):
            # continuacion de una opcion de acertijo: alinear bajo el texto de "A "/"B "
            text = text.lstrip()
            x0 += F.width('A ')
        m = F.render(text)
        w = F.width(text)
    # borrar tiles de texto
    for g in gs:
        for (x, y, t, lx, ly) in obj_pixels(ncgr, g):
            ncgr.set_px(t, lx, ly, 0)
    # cubrir con OBJs todo el ancho del texto: huecos entre OBJs originales
    # (el japones dejaba espacios sin OBJ) y lo que sobresale a la derecha
    need_end = x0 + w
    extra = []
    def covered(x):
        return any(g['x'] <= x < g['x'] + g['w'] for g in gs)
    x = x0
    while x < need_end:
        if covered(x):
            x += 1; continue
        falta = need_end - x
        size = 32 if falta > 16 else (16 if falta > 8 else 8)
        shape, sz = OBJ_16H[size]
        t0 = ncgr.add_tiles(size // 8 * 2)
        pal = text_objs[0][2] & 0xF000
        o = [(shape << 14) | 0xF8, (sz << 14) | (x & 0x1FF), pal | ((t0 >> tbs) & 0x3FF)]
        extra.append(o); gs.append(geom(o, tbs))
        assert gs[-1]['w'] == size and gs[-1]['tile_idx'] == t0 and gs[-1]['x'] == x, gs[-1]
        x += size
    xe = max(g['x'] + g['w'] for g in gs)
    cell['objs'] = objs + extra
    if extra:
        cell['attr'] = (cell['attr'] & ~0x3F) | min(0x3F, cell_radius(cell['objs'], tbs))
    # pintar
    for g in gs:
        for (x, y, t, lx, ly) in obj_pixels(ncgr, g):
            c = x - x0; r = y + 8
            if 0 <= c < len(m[0]) and m[r][c]:
                ncgr.set_px(t, lx, ly, m[r][c])
    return len(extra), x0, xs, xe


def main():
    data = load_csv()
    sel = {}
    for a in sys.argv[1:]:
        g, _, cs = a.partition(':')
        sel[g] = set(int(c) for c in cs.split(',')) if cs else None
    if not sel:
        sel = {g: None for g in data}
    for lang, col in (('esp', 'traduccion_esp'), ('eng', 'traduccion_eng')):
        outdir = os.path.join(ROOT, 'assets/graficos', lang, 'R08')
        os.makedirs(outdir, exist_ok=True)
        for g, cells in sorted(sel.items()):
            ncgr = Ncgr(read_original(f'{g}_S10.NCGR'))
            ncer = Ncer(read_original(f'{g}_S10.NCER'))
            for idx, r in sorted(data[g].items()):
                if r['tipo'] not in TIPOS or (cells is not None and idx not in cells):
                    continue
                t = r[col].rstrip()  # conservar sangria inicial
                if not t.strip():
                    continue
                n_ext, x0, xs, xe = redraw_cell(ncgr, ncer, idx, t, r['tipo'])
                print(f'{lang} {g}{idx:<3} {r["tipo"]:<6} {t!r:<24} x0={x0} area={xs}..{xe}' + (f' +{n_ext} OBJ' if n_ext else ''))
            open(f'{outdir}/{g}_S10.NCGR', 'wb').write(ncgr.d)
            open(f'{outdir}/{g}_S10.NCER', 'wb').write(ncer.build())


if __name__ == '__main__':
    main()
