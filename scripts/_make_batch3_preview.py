import os
from PIL import Image, ImageDraw, ImageFont
import ncer_decode as m

ROOT = "extraccion_rom/root/ITM/2D"
EDITED = "_scratch_claude/ncgr_editados"
ITEMS = ["I33S10","I34S10","I35S10","I36S10","I37S10"]

label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", 14)

rows = []
for name in ITEMS:
    base = os.path.join(ROOT, name)
    edited_ncgr_path = os.path.join(EDITED, name + ".NCGR")
    ncgr = m.decode_ncgr(edited_ncgr_path)
    colors = m.decode_nclr(base + ".NCLR")
    cells, tbs = m.decode_ncer(base + ".NCER")
    bpp = 4 if ncgr['bitdepth'] == 3 else 8

    # compose bg (cell2) + name text (cell0)
    name_bg = m.compose_cell(cells[2], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    name_txt = m.compose_cell(cells[0], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    name_canvas = Image.new('RGBA', name_bg.size, (0,0,0,0))
    name_canvas.paste(name_bg, (0,0), name_bg)
    name_canvas.paste(name_txt, (0,0), name_txt)

    desc_bg = m.compose_cell(cells[3], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    desc_txt = m.compose_cell(cells[1], ncgr['tile_data'], colors, bpp, tile_boundary_shift=tbs)
    desc_canvas = Image.new('RGBA', desc_bg.size, (0,0,0,0))
    desc_canvas.paste(desc_bg, (0,0), desc_bg)
    desc_canvas.paste(desc_txt, (0,0), desc_txt)

    scale = 3
    name_canvas = name_canvas.resize((name_canvas.width*scale, name_canvas.height*scale), Image.NEAREST)
    desc_canvas = desc_canvas.resize((desc_canvas.width*scale, desc_canvas.height*scale), Image.NEAREST)

    w = max(name_canvas.width, desc_canvas.width) + 140
    h = name_canvas.height + desc_canvas.height + 10
    row_img = Image.new('RGB', (w, h), (30,20,60))
    d = ImageDraw.Draw(row_img)
    d.text((5,5), name, font=label_font, fill=(255,255,0))
    row_img.paste(name_canvas, (130, 0), name_canvas)
    row_img.paste(desc_canvas, (130, name_canvas.height+10), desc_canvas)
    rows.append(row_img)

total_w = max(r.width for r in rows)
total_h = sum(r.height for r in rows) + 20*(len(rows)-1)
final = Image.new('RGB', (total_w, total_h), (10,10,10))
y = 0
for r in rows:
    final.paste(r, (0, y))
    y += r.height + 20

final.save("_scratch_claude/batch7_preview.png")
print("saved", final.size)
