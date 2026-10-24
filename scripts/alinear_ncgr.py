#!/usr/bin/env python3
"""
alinear_ncgr.py - Al crecer un NCGR de sprites, si su cantidad de unidades de
32 bytes de pixeles no es multiplo de 4 (128 B = granularidad del indice de
tile del OBJ, tile_boundary_shift=2), el juego carga el recurso siguiente
desalineado respecto de los indices de sus OBJ (iconos de estado rotos en la
pantalla del celular, medido en un savestate de la v1.5.2). Este script rellena
con ceros hasta multiplo de 4. No toca ningun pixel existente. Idempotente.
Solo actua si el original ya era multiplo de 4.
Uso: python3 scripts/alinear_ncgr.py
"""
import os, sys, glob, struct
sys.path.insert(0, os.path.dirname(__file__))
from redibujar_correos import Ncgr
ROOT = os.path.join(os.path.dirname(__file__), '..')
EXTR = os.path.join(ROOT, 'extraccion_rom/root')

def main():
    tot = 0
    for lang in ('esp', 'eng'):
        base = os.path.join(ROOT, 'assets/graficos', lang)
        for f in sorted(glob.glob(base + '/**/*.NCGR', recursive=True)):
            rel = os.path.relpath(f, base); o = os.path.join(EXTR, rel)
            if not os.path.exists(o):
                continue
            try:
                n = Ncgr(open(f, 'rb').read()); g = Ncgr(open(o, 'rb').read())
            except Exception:
                continue
            un, uo = n.ntiles(), g.ntiles()
            if un <= uo or uo % 4 or un % 4 == 0:
                continue
            pad = (-un) % 4
            n.d.extend(bytes(32 * pad))
            struct.pack_into('<I', n.d, n.rahc_off + 24, len(n.d) - n.px_off)
            struct.pack_into('<I', n.d, n.rahc_off + 4, len(n.d) - n.rahc_off)
            struct.pack_into('<I', n.d, 8, len(n.d))
            open(f, 'wb').write(n.d)
            print(f'{lang} {rel}: {un} -> {un + pad} unidades'); tot += 1
    print('archivos alineados:', tot)

if __name__ == '__main__':
    main()
