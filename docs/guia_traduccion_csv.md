# Guía de traducción — Twilight Syndrome: Kinjirareta Toshi Densetsu (NDS)

Este documento es solo para el trabajo de TRADUCCIÓN del CSV (`guion_principal.csv`, 6653 filas). No hace falta saber nada de ROM hacking para usarlo — es información de contexto y reglas de formato para traducir del japonés al español respetando las limitaciones técnicas reales del juego.

## Contexto del juego

Twilight Syndrome: Kinjirareta Toshi Densetsu es un juego de misterio/horror para Nintendo DS centrado en leyendas urbanas japonesas (toshi densetsu) contadas por estudiantes de secundaria — historias de fantasmas, rumores escolares, lugares malditos, etc. Tono: juvenil, coloquial, con momentos de tensión/horror. Los diálogos son mayormente conversaciones informales entre adolescentes.

## Columnas del CSV

`offset_hex, largo_bytes, texto_original, revisado, traduccion`

- `texto_original`: el japonés tal como está en el ROM (referencia).
- `revisado`: (si existe) una versión corregida/aclarada del japonés, útil cuando el original es ambiguo o tiene errores de OCR/extracción.
- `traduccion`: **esta es la columna a completar**, en español.

## REGLAS DE FORMATO — muy importantes, no son solo estilo

### 1. Alfabeto disponible (limitación técnica real, no se puede traducir con más caracteres que estos por ahora)

Solo están disponibles: `A-Z`, `a-z`, `Ñ`, `ñ`, dígitos `0-9`, espacio, y salto de línea manual.

**NO usar tildes ni ¿ ¡ todavía** (á, é, í, ó, ú, ü no existen como glifo por ahora — están despriorizados, se agregarán después). Mientras tanto:
- Escribir sin tilde: "que" en vez de "qué" cuando technically debería llevar, "asi" en vez de "así", etc. (no hace falta reescribir la frase, solo omitir la tilde).
- Evitar signos de apertura ¿ ¡ — usar solo el de cierre `?` `!`, como en inglés: "Que haces?" en vez de "¿Qué haces?".
- Si una palabra sin tilde genera ambigüedad real (cambia el significado), se puede reformular la frase para evitarla, pero no es necesario en la mayoría de los casos.

### 2. Sin wrap automático — hay que cortar las líneas a mano con `\n`

El juego NO ajusta el texto solo. Si una línea no entra en el cuadro de texto, se corta y se pierde el resto (ya lo confirmamos en pruebas reales). Hay que insertar `\n` manualmente donde corresponda un salto de línea.

**Presupuesto de ancho real, ya confirmado en emulador:** una línea de ~242 píxeles de ancho de avance YA se corta (se probó con "Ese karaoke que esta frente", 242px, y se perdió la "e" final). Usar como límite seguro **≤ 220px por línea** hasta que se confirme el máximo exacto con más pruebas.

Tabla de ancho de avance por letra (píxeles), para calcular el ancho de una línea sumando letra por letra + 1px extra por espacio aprox:

```
A10 B10 C10 D11 E9 F9 G11 H11 I5 J6 K11 L8 M14 N11 O12 P10 Q12 R10 S10 T9 U11 V10 W15 X10 Y10 Z10
a9 b10 c8 d10 e9 f6 g10 h10 i4 j5 k9 l4 m14 n10 o9 p10 q10 r7 s8 t6 u10 v9 w12 x9 y9 z8
Ñ9 ñ8   espacio ≈ 6px
```

Ejemplo de cálculo (script en Python, para no tener que sumar a mano):
```python
anchos = {'A':10,'B':10,'C':10,'D':11,'E':9,'F':9,'G':11,'H':11,'I':5,'J':6,'K':11,'L':8,'M':14,
'N':11,'O':12,'P':10,'Q':12,'R':10,'S':10,'T':9,'U':11,'V':10,'W':15,'X':10,'Y':10,'Z':10,
'a':9,'b':10,'c':8,'d':10,'e':9,'f':6,'g':10,'h':10,'i':4,'j':5,'k':9,'l':4,'m':14,'n':10,
'o':9,'p':10,'q':10,'r':7,'s':8,'t':6,'u':10,'v':9,'w':12,'x':9,'y':9,'z':8,'Ñ':9,'ñ':8}

def ancho_linea(linea, limite=220):
    total = 0
    for ch in linea:
        total += 6 if ch == ' ' else anchos.get(ch, 10) + 1
    return total

# Al armar cada línea traducida, cortar con \n antes de superar 220px.
```

Si es posible, usar ese script (o uno similar) para verificar automáticamente cada línea de la traducción antes de darla por definitiva, en vez de estimar a ojo.

### 3. Longitud total del texto — SIN límite estricto de caracteres

A diferencia de una traducción típica de ROM hack antiguo, acá NO hay límite de bytes por línea de diálogo (ya se resolvió técnicameante el problema de espacio en RAM). Se puede traducir con la extensión natural del español aunque sea más largo que el japonés original — el único límite real es el ancho de pantalla por línea de texto visible (regla 2), no el tamaño total del string.

### 4. Mantener los saltos de línea ya existentes del original como pista de las pantallas

Si `texto_original` ya trae `\n`, generalmente indica dónde el juego mostraba un salto de página o cambio de cuadro (no necesariamente de línea visual) — revisar si corresponde antes de decidir el wrap final en español, pero no hay que copiar el mismo lugar de corte, hay que recalcularlo para el español según el ancho real de las palabras.

### 5. Estilo de traducción

- Tono coloquial, natural en español (de Chile/neutro, como decida el traductor), no rígido ni literal del japonés.
- Los nombres propios y honoríficos (-san, -kun, etc.) — decidir un criterio consistente: mantenerlos o quitarlos, pero aplicarlo igual en todo el guion.
- Las leyendas urbanas y diálogos de terror deben mantener el tono inquietante/misterioso del original, no volverse cómicos accidentalmente por una traducción muy literal.

## Flujo de trabajo sugerido para el chat de traducción

1. Subir este documento + `guion_principal.csv`.
2. Traducir en tandas (por ejemplo, de a 50-100 filas), llenando la columna `traduccion`.
3. Para cada línea, aplicar el corte de `\n` según el presupuesto de píxeles (regla 2) antes de darla por terminada.
4. Evitar tildes y ¿¡ (regla 1).
5. Exportar el CSV actualizado — ese archivo es el que después se usa para generar el script de inserción real en el ROM (eso sí requiere el otro documento técnico y se hace en otro chat/sesión con acceso al ROM).
