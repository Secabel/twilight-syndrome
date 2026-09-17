"""
Extractor de texto para Twilight Syndrome: Kinjirareta Toshi Densetsu (NDS).

El guion vive como texto plano Shift-JIS embebido directo en arm9.bin, sin
comprimir: cada mensaje termina en 0x00, y los saltos de linea dentro de un
mismo mensaje usan 0x0A (\n).

Este script recorre arm9.bin completo, separa por 0x00, intenta decodificar
cada trozo como Shift-JIS, y se queda solo con los que tienen pinta real de
texto japones (filtra ruido de codigo binario que por casualidad decodifica
como SJIS valido).

Salida: CSV con offset (hex), longitud en bytes, y el texto original.

LIMITACION CONOCIDA (2026-09-17): el separado ingenuo por 0x00 no reconstruye
bien un pequeno numero de mensajes (~7 de 6858 confirmados, ver
docs/historia-proyecto.md entrada 2026-09-17) porque el offset donde arranca
el texto real no cae justo despues de un 0x00 (hay algo -- probablemente un
byte de control de otro campo del struct de puntero -- entre mensajes que
a veces se cuela). Esos casos YA estan correctamente catalogados a mano en
los CSV (fueron detectados en su momento cruzando la tabla de punteros, no
con este escaneo lineal) asi que no aparecen como "nuevos" ni se pierden,
pero si se regenerase el catalogo de offsets desde cero con este script
jamas los encontraria por si solo. Documentado para que quede claro que
"correr el extractor" no reemplaza la tabla de offsets ya curada -- sirve
para encontrar candidatos NUEVOS que agregar, no para regenerar todo el CSV.
"""
import csv
import sys

ARM9_PATH = "extraccion_rom/root/ftc/arm9.bin"
OUT_CSV = "docs/texto_extraido.csv"

# Rango real donde vive el texto del guion dentro de arm9.bin. Antes de
# 0xd118c es codigo ejecutable ARM (y alguna tabla de datos no relacionada);
# despues de 0x10b242 es la cola del binario (sin texto). Confirmado
# 2026-09-17 escaneando el arm9.bin COMPLETO (0x0-0x10b2d8) con el filtro de
# mas abajo: fuera de este rango salen ~150 "candidatos", todos de 2-4
# caracteres, kanji rebuscados sin ningun sentido ("溷\n", "大汎聰",
# "晏  晏"...) -- ruido estadistico de reinterpretar bytes de codigo/datos
# como SJIS, no texto real. Dentro del rango, el mismo filtro solo agrega
# lineas de dialogo genuinas. Por eso se restringe el escaneo a este rango:
# agranda la cobertura real (vs. el filtro viejo) sin reintroducir falsos
# positivos.
RANGO_TEXTO_INICIO = 0xd118c
RANGO_TEXTO_FIN = 0x10b242


def es_japones(ch):
    return '぀' <= ch <= 'ヿ' or '一' <= ch <= '鿿'


# FIX (2026-09-14, bug 2 - dialogos de MEGUMI sin traducir) + FIX 3
# (2026-09-17, bug 3 - dialogo de MIZUKI sin traducir, "１組…。"): las dos
# versiones anteriores de este filtro (ratio de caracteres japoneses sobre
# el total, con min_jp=2) fallaban en casos reales por motivos distintos:
# lineas cortas dominadas por puntuacion fullwidth quedaban bajo el umbral
# de ratio, lineas de puro silencio (jp=0) nunca pasaban min_jp, y lineas
# con un solo kanji real (jp=1, ej. "組" en "１組…。") tampoco. Se
# reemplazo todo el enfoque de ratio/conteo por una regla de charset
# cerrado: se acepta una linea si TODOS sus caracteres son japones
# (hiragana/katakana/kanji) o puntuacion/digitos/letras fullwidth conocidos
# del guion (ver PUNTUACION_VALIDA, construido empiricamente a partir de
# TODOS los caracteres no-japoneses que aparecen en las 6777 lineas ya
# traducidas del CSV), y ademas tiene al menos un caracter japones real.
# Casos especiales (ninguno tiene un caracter "japones" per se pero son
# dialogo real): lineas de puro silencio ("………。", solo "…", "。", "、")
# y lineas de solo digitos fullwidth (codigos/numeros que aparecen como
# mensaje propio, ej. "４７７１", "７７４").
#
# Validado 2026-09-17 sobre el arm9.bin completo (version reparada, ver
# nota de reparacion en docs/historia-proyecto.md): de las 6777 lineas ya
# catalogadas en el rango de texto, este filtro reencuentra 6770 (las 7
# restantes son la limitacion de offset documentada arriba); fuera de esas,
# encuentra exactamente 82 candidatos nuevos, los mismos ya agregados a
# ambos CSV en esta misma sesion. 0 falsos positivos detectados en revision
# manual.
PUNTUACION_VALIDA = set(
    '…。、\n？）（！　'  # … 。 、 \n ？ ） （ ！ 　(espacio fullwidth)
    '“”'                                          # “ ”
    '『』「」'                              # 『 』 「 」
    '〜々'                                          # 〜 々
    '−←→↓↑'                        # − ← → ↓ ↑
    '＜＞：＝'                              # ＜ ＞ ： ＝
)
DIGITOS_FULLWIDTH = set('０１２３４５６７８９')
PUNTUACION_VALIDA |= DIGITOS_FULLWIDTH
PUNTUACION_VALIDA |= set(chr(c) for c in range(0xFF21, 0xFF3B))  # Ａ-Ｚ fullwidth
PUNTUACION_VALIDA |= set(chr(c) for c in range(0xFF41, 0xFF5B))  # ａ-ｚ fullwidth

_SOLO_SILENCIO = set('…。、')  # … 。 、


def caracter_valido(ch):
    return es_japones(ch) or ch in PUNTUACION_VALIDA


def es_candidato(s, min_len=2):
    # Caso especial 1: puro silencio (jp=0 pero es dialogo real)
    if len(s) >= min_len and all(ch in _SOLO_SILENCIO for ch in s):
        return True
    # Caso especial 2: solo digitos fullwidth (codigo/numero como mensaje propio)
    if len(s) >= 1 and all(ch in DIGITOS_FULLWIDTH for ch in s):
        return True
    if len(s) < min_len:
        return False
    if not all(caracter_valido(ch) for ch in s):
        return False
    return any(es_japones(ch) for ch in s)


def main():
    with open(ARM9_PATH, "rb") as f:
        data = f.read()

    filas = []
    offset = 0
    for chunk in data.split(b"\x00"):
        largo = len(chunk)
        if RANGO_TEXTO_INICIO <= offset <= RANGO_TEXTO_FIN and largo >= 1:
            try:
                s = chunk.decode("shift_jis")
            except (UnicodeDecodeError, LookupError):
                s = None
            if s is not None and es_candidato(s):
                filas.append({
                    "offset_hex": hex(offset),
                    "largo_bytes": largo,
                    "texto_original": s,
                    "revisado": "",
                    "traduccion": "",
                })
        offset += largo + 1  # +1 por el 0x00 separador

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["offset_hex", "largo_bytes", "texto_original", "revisado", "traduccion"])
        writer.writeheader()
        writer.writerows(filas)

    print(f"Filas candidatas extraidas: {len(filas)}")
    print(f"Guardado en: {OUT_CSV}")


if __name__ == "__main__":
    main()
