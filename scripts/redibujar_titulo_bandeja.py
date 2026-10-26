#!/usr/bin/env python3
"""
redibujar_titulo_bandeja.py - Traduce el titulo 受信メール de la barra superior de la
bandeja de correos del celular (celda 0 = panel de R08/{A..M}_S10) a RECIBIDOS / INBOX.
Parte de los R08 ya traducidos en assets/graficos/<esp|eng>/R08 (no toca los correos).
Uso: python3 scripts/redibujar_titulo_bandeja.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import redibujar_ui_celular as R
from redibujar_correos import Ncer, Ncgr

GRUPOS = 'ABCDEFHIJKLM'
TITULO = {'esp': 'BANDEJA', 'eng': 'INBOX'}


def main():
    for lang in ('esp', 'eng'):
        for g in GRUPOS:
            s = R.Sprite(f'R08/{g}_S10')
            d = os.path.join(R.ROOT, 'assets/graficos', lang, 'R08')
            s.ncgr = Ncgr(open(f'{d}/{g}_S10.NCGR', 'rb').read())
            s.ncer = Ncer(open(f'{d}/{g}_S10.NCER', 'rb').read())
            antes = len(s.ncgr.d)
            def fn(im):
                R.erase(im, (14, 1, 90, 12), 100)           # kanji (el icono llega hasta x=13; la fila 1 es el borde, los kanji la rebasan)
                R.text(im, TITULO[lang], 17, 3, 1, 2)       # trazo = indice 1, sombra = indice 2
            s.edit(0, fn)
            s.save(lang)
            print(lang, g, antes, '->', len(s.ncgr.d))


if __name__ == '__main__':
    main()
