#!/usr/bin/env python3
"""Linter de la traduccion (ES/EN) del guion principal.

Uso (desde la raiz del repo):  python scripts/lint_traduccion.py [--informe docs/informe_lint.md]

Comprueba, sobre assets/csv/guion_principal_{esp,eng}.csv + docs/guion_ordenado.csv:
  1. Signos y tildes (falta de ¿ ¡, 'Quien sabe', etc.)
  2. Parentesis de pensamiento que no coinciden con el original japones
  3. Terminos prohibidos / fuera del glosario
  4. Genero del hablante (ES): formas masculinas dichas por mujeres y viceversa
  5. Comparacion ES vs EN (parentesis y cifras)
  6. Cobertura de revision por bloque
Los avisos son pistas: hay falsos positivos; revisar a mano.
"""
import csv, re, sys, glob, collections, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    return list(csv.DictReader(open(os.path.join(ROOT, p), encoding='utf-8-sig', newline='')))

esp = {r['offset_hex']: r for r in rd('assets/csv/guion_principal_esp.csv')}
eng = {r['offset_hex']: r for r in rd('assets/csv/guion_principal_eng.csv')}
orden = rd('docs/guion_ordenado.csv')

FEM = {'Mizuki', 'Riko', 'Reika', 'Yukari', 'Arisa', 'Kana', 'Megumi', '?Yui', '?Nanaka', '?Mayuko'}
MASC = {'Masaki', 'Yuuta', 'Hasegawa', 'Sakuma'}
# formas autoreferentes (frase corta, sin ambiguedad): se aplican sobre el texto del hablante
MASC_EN_BOCA_FEM = re.compile(r'\b(estoy|me siento|soy|estaba|quedé|quede)\s+(solo|seguro|cansado|listo|nervioso|asustado|harto|curioso|sorprendido|preocupado)\b', re.I)
FEM_EN_BOCA_MASC = re.compile(r'\b(estoy|me siento|soy|estaba|quedé|quede)\s+(sola|segura|cansada|lista|nerviosa|asustada|harta|curiosa|sorprendida|preocupada)\b', re.I)
PEQ = re.compile(r'\bcuando (era|fui) (pequeño|niño)\b', re.I)

TERMINOS_ES = [
    (r'rueda de la fortuna', 'usar "noria"'),
    (r'\bosea\b', '"o sea"'),
    (r'Quien sabe', '"Quién sabe"'),
    (r'nirameko', 'usar "juego de miradas"'),
    (r'\bQue (será|sera|es|hacemos|fue|hay)\b', 'falta tilde/¿ en "qué"'),
    (r'\bPor que\b', '"Por qué"'),
]
TERMINOS_EN = [
    (r'\bchain mail\b', 'usar "chain email"'),
    (r'\bnirameko\b', 'usar "staring contest"'),
    (r'Ferris wheel', None),  # solo para recuento
]
CAR_OK = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñáéíóúüÁÉÍÓÚÜ0123456789 \n.,?!()-":\'<^*>/#¿¡')

avisos = collections.defaultdict(list)   # categoria -> [(bloque, idx, off, detalle, texto)]
def avisar(cat, tb, idx, off, det, txt):
    avisos[cat].append((tb, idx, off, det, txt.replace('\n', ' / ')))

# estado de ¿ ¡ abiertos entre filas consecutivas de un mismo bloque
abierto_q = {}
abierto_e = {}
por_bloque = collections.defaultdict(list)
for r in orden:
    por_bloque[r['tabla_hex']].append(r)

for tb, filas in por_bloque.items():
    filas.sort(key=lambda r: int(r['idx']))
    oq = oe = 0
    for r in filas:
        off, idx, hab = r['offset_hex'], r['idx'], r['hablante']
        e = esp.get(off, {}).get('traduccion', '')
        g = eng.get(off, {}).get('traduccion', '')
        jp = r['texto_jp']
        if not e:
            oq = oe = 0
            continue
        t = e.replace('\n', ' ')
        ts = re.sub(r'\?{2,}', '?', re.sub(r'!{2,}', '!', t))
        # 1. signos
        for ch in ts:
            if ch == '¿': oq += 1
            elif ch == '?':
                if oq <= 0: avisar('Falta ¿ en ES', tb, idx, off, '', e)
                else: oq -= 1
            elif ch == '¡': oe += 1
            elif ch == '!':
                if oe <= 0 and '¡' not in ts: avisar('Falta ¡ en ES', tb, idx, off, '', e)
                elif oe > 0: oe -= 1
        if re.search(r'[.!?…]\s*$', t) or re.search(r'^\W*$', t): oq = oe = 0
        # 2. parentesis
        jpo = '（' in jp or '(' in jp; jpc = '）' in jp or ')' in jp
        if (jpo or jpc) != ('(' in t or ')' in t):
            avisar('Parentesis ES vs JP (uno tiene y el otro no)', tb, idx, off, f'JP={jpo or jpc}', e)
        # 3. terminos
        for pat, msg in TERMINOS_ES:
            if re.search(pat, t): avisar('Termino ES', tb, idx, off, msg, e)
        for pat, msg in TERMINOS_EN:
            if msg and re.search(pat, g.replace('\n', ' ')): avisar('Termino EN', tb, idx, off, msg, g)
        for nombre, txt in (('ES', e), ('EN', g)):
            malos = sorted({c for c in txt if c not in CAR_OK})
            if malos: avisar('Caracter no soportado por la fuente', tb, idx, off, nombre + ' ' + repr(''.join(malos)), txt)
        if len(e.split('\n')) > 6: avisar('Mas de 6 lineas ES', tb, idx, off, str(len(e.split('\n'))), e)
        # 4. genero del hablante
        if hab in FEM and (MASC_EN_BOCA_FEM.search(t) or PEQ.search(t)):
            avisar('Genero: forma masculina dicha por mujer', tb, idx, off, hab, e)
        if hab in MASC and FEM_EN_BOCA_MASC.search(t):
            avisar('Genero: forma femenina dicha por hombre', tb, idx, off, hab, e)
        # 5. ES vs EN
        if g:
            gt = g.replace('\n', ' ')
            if re.findall(r'\d+', t) != re.findall(r'\d+', gt): avisar('ES/EN: cifras distintas', tb, idx, off, '', e + '  ||  ' + g)
            if ('(' in t) != ('(' in gt): avisar('ES/EN: parentesis distintos', tb, idx, off, '', e + '  ||  ' + g)

# 6. cobertura: lineas tocadas en las revisiones registradas en docs/revision_contexto
tocadas = set()
for f in glob.glob(os.path.join(ROOT, 'docs/revision_contexto/cambios_aplicados_*.csv')):
    if 'globales' in f or 'rewrap' in f: continue
    try:
        for row in csv.DictReader(open(f, encoding='utf-8-sig', newline='')):
            tocadas.add(row['offset_hex'])
    except Exception:
        pass

def main():
    informe = None
    if '--informe' in sys.argv:
        informe = sys.argv[sys.argv.index('--informe') + 1]
    out = []
    out.append('# Informe del linter de traduccion\n')
    out.append('Generado por `scripts/lint_traduccion.py`. Los avisos son pistas, no errores seguros.\n')
    out.append('## Resumen\n')
    for cat, lst in sorted(avisos.items(), key=lambda kv: -len(kv[1])):
        out.append(f'- {cat}: {len(lst)}')
    out.append('\n## Cobertura de correcciones por bloque (no mide lo revisado: casi todo se reviso, solo se registran las lineas que cambiaron)\n')
    out.append('| Bloque | Lineas | Con correcciones registradas | % |')
    out.append('|---|---|---|---|')
    for tb, filas in por_bloque.items():
        n = len(filas); k = sum(1 for r in filas if r['offset_hex'] in tocadas)
        out.append(f'| {tb} | {n} | {k} | {100*k//max(n,1)}% |')
    for cat, lst in sorted(avisos.items(), key=lambda kv: -len(kv[1])):
        out.append(f'\n## {cat} ({len(lst)})\n')
        for tb, idx, off, det, txt in lst[:60]:
            out.append(f'- `{tb}` idx {idx} ({off}) {det}: {txt}')
        if len(lst) > 60:
            out.append(f'- ... y {len(lst)-60} mas')
    texto = '\n'.join(out) + '\n'
    if informe:
        open(os.path.join(ROOT, informe), 'w', encoding='utf-8').write(texto)
        print('Informe escrito en', informe)
    for l in out:
        if l.startswith('\n## Cobertura'): break
        print(l)

if __name__ == '__main__':
    main()
