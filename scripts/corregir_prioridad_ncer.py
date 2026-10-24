#!/usr/bin/env python3
"""
corregir_prioridad_ncer.py - Los OBJ 8x8 que agregan los redibujadores de
sprites (redibujar_ui_celular / redibujar_correos / traducir_opcion_listas)
deben heredar la PRIORIDAD (bits 10-11 del atributo 2) del resto de su celda.
Si no, quedan delante de los paneles y asoman fragmentos de letras (la "J" de
la pantalla ENVIANDO). Este script repara los NCER ya generados en
assets/graficos/{esp,eng} sin tocar ningun pixel: solo en celdas cuyo original
tenia prioridad uniforme, iguala la de los OBJ nuevos a la del primer OBJ.
Idempotente. Uso: python3 scripts/corregir_prioridad_ncer.py
"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
from redibujar_correos import Ncer
ROOT = os.path.join(os.path.dirname(__file__), '..')
EXTR = os.path.join(ROOT, 'extraccion_rom/root')
pr = lambda o: (o[2] >> 10) & 3

def main():
    total = 0
    for lang in ('esp', 'eng'):
        base = os.path.join(ROOT, 'assets/graficos', lang)
        for f in sorted(glob.glob(base + '/**/*.NCER', recursive=True)):
            rel = os.path.relpath(f, base)
            orig = os.path.join(EXTR, rel)
            if not os.path.exists(orig):
                continue
            try:
                n = Ncer(open(f, 'rb').read()); o = Ncer(open(orig, 'rb').read())
            except Exception:
                continue
            fix = 0
            for ci, c in enumerate(n.cells):
                if not c['objs'] or ci >= len(o.cells) or not o.cells[ci]['objs']:
                    continue
                oo = o.cells[ci]['objs']
                if len(set(pr(x) for x in oo)) != 1:
                    continue
                p = pr(oo[0])
                for x in c['objs']:
                    if pr(x) != p:
                        x[2] = (x[2] & ~0x0C00) | (p << 10); fix += 1
            if fix:
                open(f, 'wb').write(n.build())
                print(f'{lang} {rel}: {fix} OBJ')
                total += fix
    print('total OBJ corregidos:', total)

if __name__ == '__main__':
    main()
