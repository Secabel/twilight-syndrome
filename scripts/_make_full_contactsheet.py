import os
from PIL import Image, ImageDraw, ImageFont
import ncer_decode as m
import redibujar_items_prueba as r

ROOT = "extraccion_rom/root/ITM/2D"
EDITED = "_scratch_claude/ncgr_editados"

names = list(r.ITEMS.keys())  # preserves insertion order I00..I37 minus I22
label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", 12)

cells = []
for name in names:
    base = os.path.join(ROOT, name)
    edited_ncgr_path = os.path.join(EDITED, name + ".NCGR")
    ncgr = m.decode_ncgr(edited_ncgr_path)
    colors = m.decode_nclr(base + ".NCLR")
    cell_objs, tbs = m.decode_ncer(base + ".NCER")
    bpp = 4 if ncgr['bitdepth'] == 3 else 8

    name_bg = m.compose_cell(cell_objs[2], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    name_txt = m.compose_cell(cell_objs[0], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    name_canvas = Image.new('RGBA', name_bg.size, (0,0,0,0))
    name_canvas.paste(name_bg, (0,0), name_bg)
    name_canvas.paste(name_txt, (0,0), name_txt)

    desc_bg = m.compose_cell(cell_objs[3], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    desc_txt = m.compose_cell(cell_objs[1], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    desc_canvas = Image.new('RGBA', desc_bg.size, (0,0,0,0))
    desc_canvas.paste(desc_bg, (0,0), desc_bg)
    desc_canvas.paste(desc_txt, (0,0), desc_txt)

    scale = 2
    name_canvas = name_canvas.resize((name_canvas.width*scale, name_canvas.height*scale), Image.NEAREST)
    desc_canvas = desc_canvas.resize((desc_canvas.width*scale, desc_canvas.height*scale), Image.NEAREST)

    w = max(name_canvas.width, desc_canvas.width) + 110
    h = name_canvas.height + desc_canvas.height + 8
    cell_img = Image.new('RGB', (w, h), (30,20,60))
    d = ImageDraw.Draw(cell_img)
    d.text((4,4), name, font=label_font, fill=(255,255,0))
    cell_img.paste(name_canvas, (100, 0), name_canvas)
    cell_img.paste(desc_canvas, (100, name_canvas.height+8), desc_canvas)
    cells.append(cell_img)

# grid: 2 columns
ncols = 2
nrows = (len(cells) + ncols - 1) // ncols
col_w = max(c.width for c in cells) + 10
row_heights = []
for i in range(nrows):
    row_cells = cells[i*ncols:(i+1)*ncols]
    row_heights.append(max(c.height for c in row_cells) + 10)

total_w = col_w * ncols
total_h = sum(row_heights)
final = Image.new('RGB', (total_w, total_h), (10,10,10))
y = 0
for i in range(nrows):
    row_cells = cells[i*ncols:(i+1)*ncols]
    x = 0
    for c in row_cells:
        final.paste(c, (x, y))
        x += col_w
    y += row_heights[i]

final.save("_scratch_claude/all_items_contactsheet.png")
print("saved", final.size, "items:", len(names))
