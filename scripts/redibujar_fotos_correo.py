#!/usr/bin/env python3
"""
redibujar_fotos_correo.py - Traduce las 2 fotos del celular con el correo que se
muestran de fondo mientras hablan Mayuko y Mizuki (historia 1):
  EV1/M08/8  correo #7 (Kokkuri-san, texto corrupto con KA MI KU SHI)
  EV1/M08/6  correo del edificio viejo
Fondos NSCR de 8bpp con el texto cocinado: se borra cada linea reponiendo el
degradado del panel y se pinta la traduccion con la fuente del celular.
Titulo 受信メール -> RECIBIDOS / INBOX; boton 決定 -> OK (trazo oscuro del original).
Uso: python3 scripts/redibujar_fotos_correo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import redibujar_ui_celular as R

L={'esp':0,'eng':1}
TXT={
 8:{'esp':['HORA DEL BUEY','EDIFICIO VIEJO','SALA DE MUSICA','HAZ KOKKURI-SAN'],'eng':['WITCHING HOUR','OLD BUILDING','MUSIC ROOM','DO KOKKURI-SAN']},
 6:{'esp':['EL EDIFICIO VIEJO','FUE MORGUE','DE GUERRA','ESPIRITUS SIN PAZ','TE ATACARAN Y','DESAPARECERAS'],'eng':['THE OLD BUILDING','WAS A','WARTIME MORGUE','RESTLESS SPIRITS','WILL ATTACK YOU','AND YOU VANISH']}}
BANDS={8:[41,55,67,81,93,107,120],6:[42,55,67,80,94,107]}
GL=True
HEAD={'esp':'BANDEJA','eng':'INBOX'}
def build(n,lang):
    sc=R.Screen(f'EV1/M08/{n}','EV1/M08/0.NCLR')
    def fn(im):
        lum=lambda v:sum(im.rgb(v))
        dark=min(range(256),key=lambda v:lum(v) if v in {im.get(x,y) for y in range(56,64) for x in range(52,120)} else 9999)
        def bgrow(y,x):
            a=im.rgb(im.get(50,y)); b=im.rgb(im.get(205,y)); t=(x-50)/155
            c=tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
            return min(range(256),key=lambda v:sum((p-q)**2 for p,q in zip(im.rgb(v),c)))
        def clear(y0,y1,x0=51,x1=204):
            for y in range(y0,y1+1):
                for x in range(x0,x1+1): im.set(x,y,bgrow(y,x))
        lines=TXT[n][lang]
        # borrar bandas de texto japones que se traducen
        nb=len(lines) if n==6 else 4
        for i in range(nb):
            b=BANDS[n][i]; clear(b-1,b+12)
        for i,s in enumerate(lines):
            R.text(im,s,52,BANDS[n][i]+1,dark)
        if n==8 and GL:
            def sub(b,x0,x1,ch,x):
                clear(b-1,b+12,x0,x1); R.text(im,ch,x,b+2,dark)
            sub(93,77,89,'K',79)
            sub(107,51,62,'M',52); sub(107,90,102,'K',92)
            clear(119,132,163,193); R.text(im,'KU',164,122,dark); R.text(im,'SHI',177,122,dark)
        # encabezado
        ys=[y for y in range(22,40)]
        hb=None
        # fondo amarillo por fila: muestrear x=205
        for y in range(24,38):
            for x in range(66,205): im.set(x,y,im.get(205,y))
        R.text(im,HEAD[lang],69,27,dark)
        # boton: como boton_ok pero con el trazo en el color mas oscuro del 決定 original
        box=(116,153,140,163); sx=114
        lum2=lambda v:sum(im.rgb(v))
        cols=[im.get(x,y) for y in range(box[1],box[3]+1) for x in range(box[0],box[2]+1) if im.get(x,y)!=im.get(sx,y)]
        oscuro=min(cols,key=lum2)
        R.erase(im,box,sx)
        R.text(im,'OK',0,154,oscuro,None,center=128)
    sc.edit(fn)
    sc.save(lang)


def main():
    for n in (8, 6):
        for lang in ('esp', 'eng'):
            build(n, lang)
    print('EV1/M08/6 y /8 generados (esp, eng)')


if __name__ == '__main__':
    main()
