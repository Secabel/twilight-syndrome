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
"""
import csv
import sys

ARM9_PATH = "extraccion_rom/root/ftc/arm9.bin"
OUT_CSV = "docs/texto_extraido.csv"

# Rangos unicode de hiragana/katakana/kanji para contar caracteres japoneses reales
def cuenta_japones(s):
    return sum(1 for ch in s if '぀' <= ch <= 'ヿ' or '一' <= ch <= '鿿')

def es_candidato(s, min_len=3, min_jp=2, min_ratio=0.3):
    if len(s) < min_len:
        return False
    jp = cuenta_japones(s)
    if jp < min_jp:
        return False
    # ratio de caracteres "japoneses" sobre el total (excluye basura con puros
    # simbolos/control chars mezclados)
    if jp / len(s) < min_ratio:
        return False
    return True

def main():
    with open(ARM9_PATH, "rb") as f:
        data = f.read()

    filas = []
    offset = 0
    for chunk in data.split(b"\x00"):
        largo = len(chunk)
        if largo >= 4:
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
