#!/usr/bin/env python3
"""
redibujar_items_prueba_eng.py - Version en INGLES de redibujar_items_prueba.py.
Reemplaza el texto (nombre + descripcion) de los 38 items por su traduccion al
ingles, manteniendo EXACTAMENTE el mismo layout de OBJs del NCER (misma
cantidad/posicion/tamano de tiles) - solo se repintan los pixeles de esos
mismos tiles. Genera copias parcheadas de los NCGR (no genera ROM por
defecto).
"""
import struct
import importlib.util
import io

spec = importlib.util.spec_from_file_location("ncer_decode", "ncer_decode.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
ROOT = "extraccion_rom/root/ITM/2D"
OUT_DIR = "_scratch_claude/ncgr_editados_eng"
import os
os.makedirs(OUT_DIR, exist_ok=True)

DESC_FONT_SIZE = 9  # tamano "peor caso" acordado (igual que en espanol)

ITEMS = {
    "I00S10": {"name_en": "Flashlight", "name_size": 9,
        "desc_en": "The flashlight Megumi brought."},
    "I01S10": {"name_en": "Map of the old building", "name_size": 8,
        "desc_en": "Map of Kirizuka's old building. It was in the library."},
    "I02S10": {"name_en": "Coin", "name_size": 9,
        "desc_en": "A common coin, like those in game centers."},
    "I03S10": {"name_en": "Megumi's phone", "name_size": 9,
        "desc_en": "Megumi's phone, which had fallen in the rooftop flowerbed."},
    "I04S10": {"name_en": "Old building key", "name_size": 9,
        "desc_en": "Key that opens rooms in Kirizuka's old building."},
    "I05S10": {"name_en": "Kokkuri-san paper", "name_size": 9,
        "desc_en": "Kokkuri-san paper found in the music room."},
    "I06S10": {"name_en": "Kana's phone", "name_size": 9,
        "desc_en": "Kana's phone, found in the classroom for some reason."},
    "I07S10": {"name_en": "Hand mirror", "name_size": 9,
        "desc_en": "Hand mirror found in the nurse's office desk drawer."},
    "I08S10": {"name_en": "Photo 1", "name_size": 9,
        "desc_en": "Wartime photo found in the archive room: people lying on the ground."},
    "I09S10": {"name_en": "Photo 2", "name_size": 9,
        "desc_en": "Wartime photo found in the archive room. It shows an air-raid shelter."},
    "I10S10": {"name_en": "Photo 3", "name_size": 9,
        "desc_en": "Wartime photo found in the archive room. Looks like a commemorative photo."},
    "I11S10": {"name_en": "Map of the station", "name_size": 9,
        "desc_en": "Map of the station closest to Kirizuka."},
    "I12S10": {"name_en": "Fragment", "name_size": 9,
        "desc_en": "Something is carved into it."},
    "I13S10": {"name_en": "Fragment", "name_size": 9, "desc_en": "Something is carved into it."},
    "I14S10": {"name_en": "Fragment", "name_size": 9, "desc_en": "Something is carved into it."},
    "I15S10": {"name_en": "Talisman", "name_size": 9, "desc_en": "Talisman stuck behind a poster."},
    "I16S10": {"name_en": "Pocket watch", "name_size": 9, "desc_en": "Pocket watch found in a hidden cave."},
    "I17S10": {"name_en": "Floor plan", "name_size": 9, "desc_en": "A real estate flyer with Mizuki's house floor plan."},
    "I18S10": {"name_en": "Videotape", "name_size": 9, "desc_en": "A videotape apparently left in front of Mizuki's house."},
    "I19S10": {"name_en": "Compass", "name_size": 9, "desc_en": "Looks like a compass, but seems to detect spiritual energy."},
    "I20S10": {"name_en": "Aluminum foil", "name_size": 9, "desc_en": "Aluminum foil piled up in the back of the kitchen."},
    "I21S10": {"name_en": "Bowl", "name_size": 9, "desc_en": "Bowl stored under the living room floor."},
    "I22S10": {"name_en": "Chopsticks", "name_size": 8, "desc_en": "Chopsticks stored under the living room floor."},
    "I23S10": {"name_en": "Knife", "name_size": 9, "desc_en": "The fruit knife Mizuki always uses."},
    "I24S10": {"name_en": "Glass", "name_size": 9, "desc_en": "A glass with saltwater."},
    "I25S10": {"name_en": "Stuffed toy", "name_size": 9, "desc_en": "A teddy bear Mizuki loved."},
    "I26S10": {"name_en": "Balloon (red)", "name_size": 9, "desc_en": "Red balloon found inside a safe."},
    "I27S10": {"name_en": "Balloon (yellow)", "name_size": 8, "desc_en": "Yellow balloon found in the mirror house."},
    "I28S10": {"name_en": "Balloon (blue)", "name_size": 9, "desc_en": "Blue balloon found at the roller coaster."},
    "I29S10": {"name_en": "Helium gas", "name_size": 9, "desc_en": "Helium gas, used to inflate something."},
    "I30S10": {"name_en": "Carousel model", "name_size": 9, "desc_en": "A model the Dream Park owner made himself."},
    "I31S10": {"name_en": "Dream Park map", "name_size": 9, "desc_en": "A guide map of Dream Park. Check it if you get lost."},
    "I32S10": {"name_en": "Owner's diary", "name_size": 9, "desc_en": "The owner's diary, found on the office desk."},
    "I33S10": {"name_en": "Note", "name_size": 9, "desc_en": "There's a drawing of a Ferris wheel."},
    "I34S10": {"name_en": "Flashlight", "name_size": 9, "desc_en": "A flashlight that was in Mizuki's house."},
    "I35S10": {"name_en": "Flashlight", "name_size": 9, "desc_en": "The flashlight Reika brought."},
    "I36S10": {"name_en": "Riko's phone", "name_size": 9, "desc_en": "Riko's phone, found by the poolside."},
    "I37S10": {"name_en": "Map of the new building", "name_size": 7, "desc_en": "Map of the new building, in the student handbook."},
}


def wrap_to_width(text, font, max_w):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        bb = font.getbbox(trial)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_to_widths(text, font, widths):
    """Como wrap_to_width pero con un ancho maximo distinto por linea
    (widths[i] para la linea i). Si el texto no entra en len(widths)
    lineas, la ultima linea se queda con el resto (se recorta despues)."""
    words = text.split(' ')
    lines = []
    cur = ''
    wi = 0
    for w in words:
        max_w = widths[min(wi, len(widths) - 1)]
        trial = (cur + ' ' + w).strip()
        bb = font.getbbox(trial)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            wi += 1
    if cur:
        lines.append(cur)
    return lines


def row_widths_for_cell(geoms, miny, maxy, minx, row_h=16):
    """Para una celda de texto cuyos OBJs pueden no formar un rectangulo
    perfecto (una linea mas larga que otra), calcula el ancho real
    disponible para cada franja horizontal de row_h px, mirando que
    objetos cubren esa franja en Y."""
    n_rows = max(1, round((maxy - miny) / row_h))
    widths = []
    for li in range(n_rows):
        y0 = miny + li * row_h
        y1 = y0 + row_h
        max_x = minx
        for g in geoms:
            if g['y'] < y1 and (g['y'] + g['h']) > y0:
                max_x = max(max_x, g['x'] + g['w'])
        widths.append(max_x - minx)
    return widths


def find_white_index(colors):
    best_i, best_d = None, 1e9
    for i, (r, g, b) in enumerate(colors[:16]):
        if i == 0:
            continue
        d = (255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def render_cell_mask(text_lines, w, h, font_size, n_lines_slot):
    font = ImageFont.truetype(FONT_PATH, font_size)
    img = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(img)
    ascent, descent = font.getmetrics()
    line_h = h // n_lines_slot
    pad_x = 0
    for i, line in enumerate(text_lines):
        bb = font.getbbox(line)
        x = pad_x - bb[0]
        y = i * line_h + max(0, (line_h - (ascent + descent)) // 2)
        draw.text((x, y), line, font=font, fill=255)
    px = img.load()
    return [[1 if px[x, y] >= 128 else 0 for x in range(w)] for y in range(h)]


def pack_tile_4bpp(pix_rows, white_idx):
    out = bytearray(32)
    for row in range(8):
        for col4 in range(4):
            lo = white_idx if pix_rows[row][col4 * 2] else 0
            hi = white_idx if pix_rows[row][col4 * 2 + 1] else 0
            out[row * 4 + col4] = (lo & 0xF) | ((hi & 0xF) << 4)
    return bytes(out)


# I22S10: caja de nombre extendida de 16x16px a 48x16px (misma tecnica que en
# espanol - ver claude/investigacion-items-graficos.md). Usamos la misma base
# extendida ya generada (el NCLR no cambia, se sigue usando el original).
CUSTOM_BASE = {
    "I22S10": "_scratch_claude/i22_extendido/I22S10",
}


def patch_item(name, cfg):
    base = CUSTOM_BASE.get(name, f"{ROOT}/{name}")
    ncgr_path = base + ".NCGR"
    nclr_path = f"{ROOT}/{name}.NCLR"
    ncer_path = base + ".NCER"

    orig_ncgr_bytes = open(ncgr_path, 'rb').read()
    ncgr = m.decode_ncgr(ncgr_path)
    colors = m.decode_nclr(nclr_path)
    cells, tbs = m.decode_ncer(ncer_path)
    white_idx = find_white_index(colors)

    tile_data = bytearray(ncgr['tile_data'])

    def patch_cell(ci, text, font_size, n_lines_slot, max_lines):
        objs = cells[ci]
        geoms = [m.obj_geometry(*o, tile_boundary_shift=tbs) for o in objs]
        minx = min(g['x'] for g in geoms); miny = min(g['y'] for g in geoms)
        maxx = max(g['x'] + g['w'] for g in geoms); maxy = max(g['y'] + g['h'] for g in geoms)
        w, h = maxx - minx, maxy - miny
        font = ImageFont.truetype(FONT_PATH, font_size)
        if max_lines > 1:
            widths = row_widths_for_cell(geoms, miny, maxy, minx, row_h=h // max_lines)
            lines = wrap_to_widths(text, font, widths)
        else:
            lines = [text]
        lines = lines[:max_lines]
        mask = render_cell_mask(lines, w, h, font_size, n_lines_slot)
        for g in geoms:
            ox = g['x'] - minx
            oy = g['y'] - miny
            w_tiles = g['w'] // 8
            h_tiles = g['h'] // 8
            n = 0
            for ty in range(h_tiles):
                for tx in range(w_tiles):
                    t = g['tile_idx'] + n
                    n += 1
                    rows = []
                    for r in range(8):
                        row_pixels = []
                        for c in range(8):
                            px_x = ox + tx * 8 + c
                            px_y = oy + ty * 8 + r
                            if 0 <= px_y < len(mask) and 0 <= px_x < len(mask[0]):
                                row_pixels.append(mask[px_y][px_x])
                            else:
                                row_pixels.append(0)
                        rows.append(row_pixels)
                    tile_bytes = pack_tile_4bpp(rows, white_idx)
                    off = t * 32
                    tile_data[off:off + 32] = tile_bytes

    patch_cell(0, cfg["name_en"], cfg["name_size"], n_lines_slot=1, max_lines=1)
    patch_cell(1, cfg["desc_en"], DESC_FONT_SIZE, n_lines_slot=2, max_lines=2)

    magic, blocks = m.parse_container(orig_ncgr_bytes)
    char_off = next(off for off, bmagic, bsize in blocks if bmagic == b'RAHC')
    data_rel_off = struct.unpack_from('<I', orig_ncgr_bytes, char_off + 28)[0]
    tile_data_start = char_off + 8 + data_rel_off
    new_bytes = bytearray(orig_ncgr_bytes)
    new_bytes[tile_data_start:tile_data_start + len(tile_data)] = tile_data
    assert len(new_bytes) == len(orig_ncgr_bytes), "el tamano del NCGR no debe cambiar"

    out_path = os.path.join(OUT_DIR, name + ".NCGR")
    open(out_path, 'wb').write(new_bytes)
    print(f"{name}: parcheado -> {out_path} ({len(new_bytes)} bytes, white_idx={white_idx})")
    return orig_ncgr_bytes, bytes(new_bytes)


def main():
    for name, cfg in ITEMS.items():
        patch_item(name, cfg)


if __name__ == '__main__':
    main()
