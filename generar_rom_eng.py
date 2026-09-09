#!/usr/bin/env python3
"""
generar_rom.py - Genera una ROM parcheada de Twilight Syndrome: Kinjirareta
Toshi Densetsu (NDS) a partir de un guion traducido en CSV.

Uso: editar las 3 lineas de CONFIGURACION de mas abajo (CSV, ROM base, ROM
de salida) y correr:

    python3 generar_rom.py

No pide nada por consola. Para tener varias versiones (ESP/ENG) al mismo
tiempo, se puede duplicar este archivo (ej. generar_rom_esp.py,
generar_rom_eng.py) con cada uno apuntando a su propio CSV/salida.
"""

import csv
import struct
import os

# =========================== CONFIGURACION =================================
# Todo lo que este script necesita (menos la ROM base y el arm9 original)
# vive en assets/ dentro del proyecto: assets/csv, assets/font, assets/graficos.
CSV_PATH = "assets/csv/guion_principal_eng.csv"
BASE_ROM = "Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds"
ROM_OUT  = "Twilight Syndrome - ENG.nds"

ARM9_PRISTINO = "extraccion_rom/root/ftc/arm9.bin"  # SIEMPRE el original sin parchear
FONT_PATH = "assets/font/TWSFont_v21.NFTR"
MAX_WIDTH_PX = 220   # presupuesto de ancho por linea antes de avisar
MARGIN = 0x40000     # colchon en bytes despues de bss_end (256KB)

# Graficos editados a mano (carteles de nombre, etc.) que se inyectan tal cual
# en la ROM de salida. Cada entrada es (carpeta_en_la_rom, nombre_archivo, ruta_local).
GRAPHICS_PATCHES = [
    ("SYS", "G00M10.NCGR", "assets/graficos/G00M10.NCGR"),
    ("SYS", "G00M11.NCGR", "assets/graficos/G00M11.NCGR"),
    # I22 (palillos): layout de celdas EXTENDIDO (caja de nombre 16x16 -> 48x16px,
    # ver claude/investigacion-items-graficos.md). El NCER es compartido entre
    # ESP y ENG porque solo define geometria/tiles-de-layout, no texto -- el
    # texto en si vive en el .NCGR de cada idioma (ver bloque ITM/2D mas abajo).
    ("ITM/2D", "I22S10.NCER", "assets/graficos/I22S10.NCER"),
]

# Graficos horneados por idioma (items, menu de historias, etc.): el texto
# esta pintado directamente en los pixeles (no hay CSV/fuente involucrados),
# asi que cada idioma tiene su propio arbol assets/graficos/eng/<misma ruta
# que en extraccion_rom/root>/archivo.NCGR (o .NCER). Se recorre TODO ese
# arbol automaticamente y se agrega cada archivo encontrado -- no hace falta
# tocar esta lista a mano al agregar/actualizar graficos de ningun tipo
# (items, tarjetas del menu de historias, etc.), alcanza con guardarlos en
# la carpeta con la ruta correcta.
_GRAPHICS_LANG_DIR = "assets/graficos/eng"
if os.path.isdir(_GRAPHICS_LANG_DIR):
    for _dirpath, _dirnames, _fnames in os.walk(_GRAPHICS_LANG_DIR):
        for _fname in sorted(_fnames):
            if _fname.upper().endswith((".NCGR", ".NCER", ".NCBR")):
                _local_path = os.path.join(_dirpath, _fname)
                _rel = os.path.relpath(_dirpath, _GRAPHICS_LANG_DIR).replace(os.sep, "/")
                _rom_folder = "" if _rel == "." else _rel
                GRAPHICS_PATCHES.append((_rom_folder, _fname, _local_path))

# Titulo que se muestra en el menu del sistema / TWiLight Menu++ (metadata del
# banner del ROM, no tiene relacion con la fuente ni el guion). None = dejar
# el original japones sin tocar. Maximo recomendado ~18 caracteres por linea.
BANNER_TITLE_EN = "Twilight Syndrome\nToshi Densetsu\n(English)"
# ============================================================================

BASE_RAM = 0x02000000
BSS_END = 0x02119320  # confirmado via desensamblado del crt0 (loop de limpieza de bss)

# --- Alfabeto disponible en la fuente TWSFont_v20.NFTR --------------------
# 54 letras (A-Z a-z Ñ ñ) + 9 signos de puntuacion basicos = 63, en 0xA1-0xDF
# (rango de un solo byte en SJIS, sin riesgo). Generado con build_nftr_v19.py.
#
# IMPORTANTE (bug encontrado y corregido el 2026-09-08): los 7 caracteres
# ' < ^ * > / # NO pueden vivir en 0xE0+ porque ese rango es "primer byte de
# caracter de 2 bytes" en Shift-JIS real -- el motor del juego se comia la
# letra siguiente (ej. "It's" -> "It  s" perdiendo la mitad). Se movieron a
# sus propios codigos ASCII (de un solo byte garantizado), agregando 3 bloques
# CMAP nuevos a la fuente (v20) que apuntan a los MISMOS glifos ya dibujados
# en v19 (no hizo falta redibujar nada, solo remapear el codigo de entrada).
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"
_PUNCT_SEGURO = list('.,?!()-":')
_ASCII_DIRECTO = "'<^*>/#"  # se codifican con su propio valor ASCII, no con BYTE_MAP
_FULL_CHARS = list(_ALPHABET) + _PUNCT_SEGURO
assert len(_FULL_CHARS) == 63
BYTE_MAP = {ch: 0xA1 + i for i, ch in enumerate(_FULL_CHARS)}
for ch in _ASCII_DIRECTO:
    BYTE_MAP[ch] = ord(ch)

# anchos de avance en pixeles (glyphWidth+1), usados solo para el chequeo de wrap
ANCHOS = {
    'A':10,'B':10,'C':10,'D':11,'E':9,'F':9,'G':11,'H':11,'I':5,'J':6,'K':11,'L':8,
    'M':14,'N':11,'O':12,'P':10,'Q':12,'R':10,'S':10,'T':9,'U':11,'V':10,'W':15,
    'X':10,'Y':10,'Z':10,'a':9,'b':10,'c':8,'d':10,'e':9,'f':6,'g':10,'h':10,'i':4,
    'j':5,'k':9,'l':4,'m':14,'n':10,'o':9,'p':10,'q':10,'r':7,'s':8,'t':6,'u':10,
    'v':9,'w':12,'x':9,'y':9,'z':8,'Ñ':9,'ñ':8,
    '.':5,',':5,'?':8,'!':6,'(':6,')':6,'-':6,'"':7,':':5,"'":4,'<':11,'^':11,
    '*':7,'>':11,'/':5,'#':11,
}
SPACE_WIDTH = 6

PLACEHOLDER_MARKERS = ('[REVISAR', '[TEXTO PARCIAL]', '[CHECK ROM', '[PARTIAL TEXT]')


def line_width(line):
    total = 0
    for ch in line:
        total += SPACE_WIDTH if ch == ' ' else ANCHOS.get(ch, 10) + 1
    return total


def encode_text(text):
    out = bytearray()
    for ch in text:
        if ch in BYTE_MAP:
            out.append(BYTE_MAP[ch])
        elif ch == '\n':
            out.append(0x0A)
        elif ch == ' ':
            out.append(0x20)
        elif ch in '0123456789':
            out.append(ord(ch))
        else:
            raise ValueError(f"caracter no soportado: {ch!r} en {text!r}")
    out.append(0x00)
    return bytes(out)


def _crc16(data, crc=0xFFFF):
    """CRC16 usado por Nintendo para el banner del ROM (poly 0xA001, init 0xFFFF)."""
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc & 0xFFFF


def set_banner_title(icon_banner, lang_index, text):
    """Reemplaza el titulo de un idioma del banner (0=JP,1=EN,2=FR,3=DE,4=IT,5=ES)
    y recalcula el CRC16 (offset 0x02) para que el banner quede valido."""
    icon_banner = bytearray(icon_banner)
    encoded = text.encode('utf-16-le')
    slot = bytearray(0x100)
    slot[:len(encoded)] = encoded  # se corta solo si excede 127 caracteres + nulo
    off = 0x240 + 0x100 * lang_index
    icon_banner[off:off + 0x100] = slot
    new_crc = _crc16(bytes(icon_banner[0x20:0x840]))
    struct.pack_into('<H', icon_banner, 0x02, new_crc)
    return bytes(icon_banner)


def find_pointer_locations(data, text_offset):
    ram = BASE_RAM + text_offset
    pattern = struct.pack('<I', ram)
    locs = []
    start = 0
    while True:
        idx = data.find(pattern, start)
        if idx == -1:
            break
        locs.append(idx)
        start = idx + 1
    return locs


def main():
    if not os.path.isfile(BASE_ROM):
        print(f"ERROR: no se encontro la ROM base: {BASE_ROM}")
        return
    if not os.path.isfile(ARM9_PRISTINO):
        print(f"ERROR: no se encontro {ARM9_PRISTINO}")
        return
    if not os.path.isfile(FONT_PATH):
        print(f"ERROR: no se encontro {FONT_PATH}")
        return
    if not os.path.isfile(CSV_PATH):
        print(f"ERROR: no se encontro el CSV {CSV_PATH}")
        return

    try:
        from ndspy.rom import NintendoDSRom
    except ImportError:
        print("ERROR: falta ndspy. Instalalo con: pip install ndspy")
        return

    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    data = bytearray(open(ARM9_PRISTINO, 'rb').read())
    orig_len = len(data)

    new_block_offset = (BSS_END + MARGIN) - BASE_RAM
    if len(data) < new_block_offset:
        data += bytes(new_block_offset - len(data))

    cursor = len(data)
    n_written = 0
    n_skipped = 0
    n_pointers = 0
    wide_lines = []
    errors = []
    missing_pointers = []

    for r in rows:
        t = r.get('traduccion', '')
        if not t or t.strip() == '' or any(m in t for m in PLACEHOLDER_MARKERS):
            n_skipped += 1
            continue

        for linea in t.split('\n'):
            w = line_width(linea)
            if w > MAX_WIDTH_PX:
                wide_lines.append((r['offset_hex'], w, linea))

        try:
            encoded = encode_text(t)
        except ValueError as e:
            errors.append((r['offset_hex'], str(e)))
            continue

        text_offset = int(r['offset_hex'], 16)
        locs = find_pointer_locations(data, text_offset)
        if not locs:
            missing_pointers.append(r['offset_hex'])
            continue

        new_ram = BASE_RAM + cursor
        for loc in locs:
            struct.pack_into('<I', data, loc, new_ram)
        data += encoded
        cursor += len(encoded)
        n_written += 1
        n_pointers += len(locs)

    print(f"lineas escritas: {n_written}")
    print(f"lineas salteadas (vacias/placeholder): {n_skipped}")
    print(f"punteros repointeados: {n_pointers}")
    print(f"tamano arm9: {orig_len} -> {len(data)} (+{len(data)-orig_len} bytes, ~{(len(data)-orig_len)/1024:.1f} KB)")

    if errors:
        print(f"\n!! {len(errors)} lineas con caracteres NO soportados por la fuente (no se insertaron, quedo el original):")
        for off, msg in errors[:30]:
            print("   ", off, msg)
        if len(errors) > 30:
            print(f"   ... y {len(errors)-30} mas")

    if missing_pointers:
        print(f"\n!! {len(missing_pointers)} offsets del CSV sin puntero encontrado en arm9 (revisar):")
        print("   ", missing_pointers[:30])

    if wide_lines:
        print(f"\n!! {len(wide_lines)} lineas superan el presupuesto de {MAX_WIDTH_PX}px (podrian cortarse en pantalla):")
        for off, w, linea in wide_lines[:30]:
            print(f"    {off}  ({w}px)  {linea!r}")
        if len(wide_lines) > 30:
            print(f"    ... y {len(wide_lines)-30} mas")

    rom = NintendoDSRom.fromFile(BASE_ROM)
    rom.arm9 = bytes(data)
    font_id = rom.filenames.idOf('Font/TWSFont.NFTR')
    rom.files[font_id] = open(FONT_PATH, 'rb').read()

    if BANNER_TITLE_EN is not None:
        # Se escribe en los 6 slots de idioma (JP,EN,FR,DE,IT,ES): la consola
        # muestra el que corresponde al idioma del firmware, no siempre el
        # en, asi que hay que cubrir todos para que se vea bien siempre.
        banner = rom.iconBanner
        for lang_index in range(6):
            banner = set_banner_title(banner, lang_index, BANNER_TITLE_EN)
        rom.iconBanner = banner
        print(f"titulo de banner (EN, los 6 idiomas) actualizado: {BANNER_TITLE_EN!r}")

    def find_folder(folder, path_parts):
        if not path_parts:
            return folder
        for name, sub in folder.folders:
            if name == path_parts[0]:
                return find_folder(sub, path_parts[1:])
        return None

    aplicados = 0
    omitidos = 0
    for rom_folder, rom_filename, local_path in GRAPHICS_PATCHES:
        if not os.path.isfile(local_path):
            print(f"!! grafico no encontrado, se omite: {local_path}")
            omitidos += 1
            continue
        folder = find_folder(rom.filenames, rom_folder.split('/'))
        if folder is None:
            print(f"!! carpeta {rom_folder} no existe en la rom, se omite {rom_filename}")
            omitidos += 1
            continue
        file_id = folder.idOf(rom_filename)
        rom.files[file_id] = open(local_path, 'rb').read()
        print(f"grafico aplicado: {rom_folder}/{rom_filename}")
        aplicados += 1

    total = len(GRAPHICS_PATCHES)
    print(f"\nGraficos: {aplicados}/{total} aplicados" + (f", {omitidos} omitidos" if omitidos else ""))

    rom.saveToFile(ROM_OUT)
    print(f"ROM generada: {ROM_OUT}")


if __name__ == '__main__':
    main()
