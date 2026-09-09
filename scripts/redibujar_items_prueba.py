#!/usr/bin/env python3
"""
redibujar_items_prueba.py - Prueba de redibujado: reemplaza el texto (nombre +
descripcion) de un set de items por su traduccion al espanol, manteniendo
EXACTAMENTE el mismo layout de OBJs del NCER (misma cantidad/posicion/tamano de
tiles) - solo se repintan los pixeles de esos mismos tiles. Genera copias
parcheadas de los NCGR y una ROM de prueba con los cambios aplicados.
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
OUT_DIR = "_scratch_claude/ncgr_editados"
import os
os.makedirs(OUT_DIR, exist_ok=True)

DESC_FONT_SIZE = 9  # tamano "peor caso" acordado (entra I08/I09 en 2 lineas)

ITEMS = {
    "I00S10": {
        "name_es": "Linterna", "name_size": 9,
        "desc_es": "La linterna que trajo Megumi.",
    },
    "I01S10": {
        "name_es": "Mapa del edificio viejo", "name_size": 8,
        "desc_es": "Plano del edificio viejo de Kirizuka. Estaba en la biblioteca.",
    },
    "I02S10": {
        "name_es": "Moneda", "name_size": 9,
        "desc_es": "Una moneda comun, como las de los game centers.",
    },
    "I03S10": {
        "name_es": "Celular de Megumi", "name_size": 9,
        "desc_es": "El celular de Megumi, que estaba caido en el jardin de la azotea.",
    },
    "I04S10": {
        "name_es": "Llave del edificio", "name_size": 9,
        "desc_es": "Llave que abre salas del edificio viejo de Kirizuka.",
    },
    "I05S10": {
        "name_es": "Papel de la Kokkuri-san", "name_size": 9,
        "desc_es": "Papel de la Kokkuri-san, caido en la sala de musica.",
    },
    "I06S10": {
        "name_es": "Celular de Kana", "name_size": 9,
        "desc_es": "El celular de Kana, caido por algun motivo en el salon.",
    },
    "I07S10": {
        "name_es": "Espejo de mano", "name_size": 8,
        "desc_es": "Espejo que estaba en el cajon del escritorio de la enfermeria.",
    },
    "I08S10": {
        "name_es": "Foto 1", "name_size": 9,
        "desc_es": "Foto de guerra hallada en la sala de material: gente tendida en el suelo.",
    },
    "I09S10": {
        "name_es": "Foto 2", "name_size": 9,
        "desc_es": "Foto de guerra encontrada en la sala de material. Es un refugio antiaereo.",
    },
    "I10S10": {
        "name_es": "Foto 3", "name_size": 9,
        "desc_es": "Foto de guerra encontrada en el material. Parece conmemorativa.",
    },
    "I11S10": {
        "name_es": "Mapa de la estacion", "name_size": 9,
        "desc_es": "Plano de la estacion, la mas cercana a Kirizuka.",
    },
    "I12S10": {
        "name_es": "Fragmento", "name_size": 9,
        "desc_es": "Tiene algo grabado.",
    },
    "I13S10": {"name_es": "Fragmento", "name_size": 9, "desc_es": "Tiene algo grabado."},
    "I14S10": {"name_es": "Fragmento", "name_size": 9, "desc_es": "Tiene algo grabado."},
    "I15S10": {"name_es": "Talisman", "name_size": 9, "desc_es": "Talisman pegado detras de un poster."},
    "I16S10": {"name_es": "Reloj", "name_size": 9, "desc_es": "Reloj caido en una cueva oculta."},
    "I17S10": {"name_es": "Plano de casa", "name_size": 8, "desc_es": "Folleto de una inmobiliaria. Tiene el plano de la casa de Mizuki."},
    "I18S10": {"name_es": "Cinta de video", "name_size": 9, "desc_es": "Cinta de video que, al parecer, estaba dejada frente a la casa de Mizuki."},
    "I19S10": {"name_es": "Brujula", "name_size": 9, "desc_es": "Parece una brujula, pero detecta energia espiritual."},
    "I20S10": {"name_es": "Papel aluminio", "name_size": 9, "desc_es": "Papel aluminio que, por algun motivo, estaba amontonado al fondo de la cocina."},
    "I21S10": {"name_es": "Cuenco", "name_size": 9, "desc_es": "Cuenco que estaba guardado bajo el piso del living."},
    "I22S10": {"name_es": "Palillos", "name_size": 9, "desc_es": "Palillos guardados bajo el piso del living."},
    "I23S10": {"name_es": "Cuchillo", "name_size": 9, "desc_es": "El cuchillo de fruta que Mizuki usa siempre."},
    "I24S10": {"name_es": "Vaso", "name_size": 9, "desc_es": "Vaso con agua salada."},
    "I25S10": {"name_es": "Peluche", "name_size": 9, "desc_es": "Peluche de oso que Mizuki queria mucho."},
    "I26S10": {"name_es": "Globo (rojo)", "name_size": 9, "desc_es": "Globo rojo dentro de una caja fuerte."},
    "I27S10": {"name_es": "Globo (amarillo)", "name_size": 8, "desc_es": "Globo amarillo, encontrado en la casa de espejos."},
    "I28S10": {"name_es": "Globo (azul)", "name_size": 9, "desc_es": "Globo azul caido en el anden de la montana rusa."},
    "I29S10": {"name_es": "Gas helio", "name_size": 9, "desc_es": "Gas helio, usado para inflar algo."},
    "I30S10": {"name_es": "Maqueta del carrusel", "name_size": 9, "desc_es": "Maqueta hecha por el propio dueno de Dream Park."},
    "I31S10": {"name_es": "Mapa de Dream Park", "name_size": 9, "desc_es": "Plano guia de Dream Park. Revisalo si te perdes."},
    "I32S10": {"name_es": "Diario del dueno", "name_size": 9, "desc_es": "Diario del dueno, encontrado en el escritorio de la oficina."},
    "I33S10": {"name_es": "Nota", "name_size": 9, "desc_es": "Tiene dibujada una noria."},
    "I34S10": {"name_es": "Linterna", "name_size": 9, "desc_es": "Linterna que habia en la casa de Mizuki."},
    "I35S10": {"name_es": "Linterna", "name_size": 9, "desc_es": "La linterna que trajo Reika."},
    "I36S10": {"name_es": "Celular de Riko", "name_size": 9, "desc_es": "El celular de Riko, caido junto a la pileta."},
    "I37S10": {"name_es": "Mapa del edificio nuevo", "name_size": 8, "desc_es": "Plano del edificio nuevo de Kirizuka, en la libreta de estudiante."},





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
            # el objeto cubre esta franja si se solapan en Y
            if g['y'] < y1 and (g['y'] + g['h']) > y0:
                max_x = max(max_x, g['x'] + g['w'])
        widths.append(max_x - minx)
    return widths


def find_white_index(colors):
    # el indice mas cercano a blanco puro, excluyendo el 0 (transparente)
    best_i, best_d = None, 1e9
    for i, (r, g, b) in enumerate(colors[:16]):
        if i == 0:
            continue
        d = (255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def render_cell_mask(text_lines, w, h, font_size, n_lines_slot):
    """Devuelve un array 2D de 0/1 (1=pintar) del tamano exacto w x h.
    Alinea cada linea a la izquierda (no centra en el ancho total del
    canvas) porque el ancho REAL disponible puede variar por linea
    (una fila con menos objetos que otra) - centrar en el ancho global
    puede empujar el texto fuera de la zona real de esa fila."""
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
    """pix_rows: lista de 8 filas de 8 valores 0/1. Devuelve 32 bytes 4bpp."""
    out = bytearray(32)
    for row in range(8):
        for col4 in range(4):
            lo = white_idx if pix_rows[row][col4 * 2] else 0
            hi = white_idx if pix_rows[row][col4 * 2 + 1] else 0
            out[row * 4 + col4] = (lo & 0xF) | ((hi & 0xF) << 4)
    return bytes(out)


# I22S10: caja de nombre extendida de 16x16px a 48x16px (ver
# claude/investigacion-items-graficos.md, seccion I22). El NCGR/NCER base para
# este item YA NO es el original de extraccion_rom/ (ese quedo con la caja
# chica) sino esta version extendida (con los tiles nuevos en blanco, listos
# para pintar). El NCLR (paleta) no cambia, se sigue usando el original.
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

    tile_data = bytearray(ncgr['tile_data'])  # copia mutable

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

    patch_cell(0, cfg["name_es"], cfg["name_size"], n_lines_slot=1, max_lines=1)
    patch_cell(1, cfg["desc_es"], DESC_FONT_SIZE, n_lines_slot=2, max_lines=2)

    # reconstruir el NCGR completo con el tile_data parcheado
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


def main(build_rom=False):
    patches = []
    for name, cfg in ITEMS.items():
        orig, new = patch_item(name, cfg)
        patches.append((name, orig, new))

    if not build_rom:
        print("(no se genero ROM - build_rom=False, solo se parchearon los NCGR)")
        return

    rom_path = "Twilight Syndrome - ESP.nds"
    print(f"leyendo {rom_path} ...")
    rom = bytearray(open(rom_path, 'rb').read())
    print(f"tamano ROM: {len(rom)} bytes")

    for name, orig, new in patches:
        idx = rom.find(orig)
        count = rom.count(orig)
        assert idx != -1, f"no se encontro {name} en la ROM"
        assert count == 1, f"{name} aparece {count} veces en la ROM, hace falta desambiguar"
        rom[idx:idx + len(orig)] = new
        print(f"{name}: parcheado en ROM en offset {hex(idx)}")

    out_rom = "Twilight Syndrome - ESP - PRUEBA ITEMS.nds"
    open(out_rom, 'wb').write(rom)
    print(f"ROM de prueba guardada: {out_rom}")


if __name__ == '__main__':
    import sys
    main(build_rom=('--rom' in sys.argv))
