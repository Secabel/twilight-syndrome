#!/usr/bin/env python3
"""
extraer_todos_items.py - Corre ncer_decode sobre los 38 items (I00-I37) y arma
hojas de contacto (nombre + descripcion apilados, con label) para transcribir
el texto japones de una.
"""
import importlib.util
import os
spec = importlib.util.spec_from_file_location("ncer_decode", os.path.join(os.path.dirname(__file__), "ncer_decode.py"))
ncer_decode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncer_decode)

from PIL import Image, ImageDraw

ROOT = "extraccion_rom/root/ITM/2D"
OUT_DIR = "_scratch_claude"
os.makedirs(OUT_DIR, exist_ok=True)

def get_item_images(name):
    base = os.path.join(ROOT, name)
    ncgr = ncer_decode.decode_ncgr(base + ".NCGR")
    colors = ncer_decode.decode_nclr(base + ".NCLR")
    cells, tbs = ncer_decode.decode_ncer(base + ".NCER")
    bpp = 4 if ncgr['bitdepth'] == 3 else 8
    imgs = []
    for ci in (0, 1):
        objs = cells[ci]
        img = ncer_decode.compose_cell(objs, ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
        bg = Image.new('RGB', img.size, (30, 20, 60))
        bg.paste(img, (0, 0), img)
        imgs.append(bg)
    return imgs

items = [f"I{n:02d}S10" for n in range(38)]
per_sheet = 8
scale = 4
pad = 6
label_h = 14

for sheet_start in range(0, len(items), per_sheet):
    batch = items[sheet_start:sheet_start + per_sheet]
    rendered = []
    max_w = 0
    total_h = 0
    for name in batch:
        try:
            name_img, desc_img = get_item_images(name)
        except Exception as e:
            print("ERROR", name, e)
            continue
        name_img = name_img.resize((name_img.width * scale, name_img.height * scale), Image.NEAREST)
        desc_img = desc_img.resize((desc_img.width * scale, desc_img.height * scale), Image.NEAREST)
        w = max(name_img.width, desc_img.width)
        h = label_h + name_img.height + 2 + desc_img.height + pad
        rendered.append((name, name_img, desc_img, w, h))
        max_w = max(max_w, w)
        total_h += h

    canvas = Image.new('RGB', (max_w + pad * 2, total_h + pad), (15, 15, 15))
    draw = ImageDraw.Draw(canvas)
    y = pad
    for name, name_img, desc_img, w, h in rendered:
        draw.text((pad, y), name, fill=(255, 255, 0))
        canvas.paste(name_img, (pad, y + label_h))
        canvas.paste(desc_img, (pad, y + label_h + name_img.height + 2))
        y += h

    idx = sheet_start // per_sheet
    out_path = os.path.join(OUT_DIR, f"items_contactsheet_{idx:02d}.png")
    canvas.save(out_path)
    print("guardado", out_path, canvas.size)
