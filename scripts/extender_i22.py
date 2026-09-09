#!/usr/bin/env python3
"""
extender_i22.py - Extiende la celda 0 (nombre) de I22S10 de 16x16px (1 obj) a
48x16px (2 objs), copiando el layout de I21S10 (que tiene el mismo template de
caja pero con 2 objs). Agrega tiles nuevos (en blanco, listos para pintar) al
final del NCGR y ajusta el NCER (cell entry + obj array + tamanos de bloque).

Genera:
  I22S10.NCGR  (8064 -> 8320 bytes, +256 de tile data nuevo, en blanco)
  I22S10.NCER  (315 -> 321 bytes, cell0 pasa de 1 a 2 objs)

No toca NCLR ni NANR (no hace falta).
"""
import struct
import importlib.util
import os

spec = importlib.util.spec_from_file_location("ncer_decode", os.path.join(os.path.dirname(__file__), "ncer_decode.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ROOT = "extraccion_rom/root/ITM/2D"
OUT_DIR = "_scratch_claude/i22_extendido"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- 1. NCGR: agregar 256 bytes de tile data en blanco (indice 0) ----------
ncgr_path = f"{ROOT}/I22S10.NCGR"
ncgr_bytes = bytearray(open(ncgr_path, 'rb').read())

magic, blocks = m.parse_container(bytes(ncgr_bytes))
assert magic == b'RGCN'
rahc_off, rahc_magic, rahc_size = next(b for b in blocks if b[1] == b'RAHC')
tile_data_size_off = rahc_off + 24  # offset del campo tiledatasize (8=magic+size, 16=pad hasta tiledatasize)
old_tiledatasize = struct.unpack_from('<I', ncgr_bytes, tile_data_size_off)[0]
old_n_tiles = old_tiledatasize // 32
print("NCGR: old tiledatasize", old_tiledatasize, "old_n_tiles", old_n_tiles)
assert old_n_tiles % 4 == 0, "el tile index nuevo debe ser multiplo de 4 (tile_boundary_shift=2)"

NEW_TILES = 8  # 32x16px = 4 tiles de ancho x 2 de alto
new_tile_data = bytes(32 * NEW_TILES)  # todo en blanco (indice 0 = transparente)

assert len(ncgr_bytes) == rahc_off + rahc_size, "el bloque RAHC no es el ultimo del archivo, revisar"
ncgr_bytes.extend(new_tile_data)

new_tiledatasize = old_tiledatasize + len(new_tile_data)
new_rahc_size = rahc_size + len(new_tile_data)
new_filesize = len(ncgr_bytes)

struct.pack_into('<I', ncgr_bytes, tile_data_size_off, new_tiledatasize)
struct.pack_into('<I', ncgr_bytes, rahc_off + 4, new_rahc_size)
struct.pack_into('<I', ncgr_bytes, 8, new_filesize)

new_tile_idx = old_n_tiles
new_tile_idx_raw = new_tile_idx >> 2
print("NCGR: nuevo tile idx", new_tile_idx, "raw", new_tile_idx_raw)
print("NCGR: new tiledatasize", new_tiledatasize, "new filesize", new_filesize)

out_ncgr = os.path.join(OUT_DIR, "I22S10.NCGR")
open(out_ncgr, 'wb').write(ncgr_bytes)

# ---------- 2. NCER: extender celda 0 a 2 objs (layout copiado de I21) ----------
ncer_path = f"{ROOT}/I22S10.NCER"
ncer_bytes = bytearray(open(ncer_path, 'rb').read())

magic, blocks = m.parse_container(bytes(ncer_bytes))
assert magic == b'RECN'
kbec_off, kbec_magic, kbec_size = next(b for b in blocks if b[1] == b'KBEC')
hdr_off = kbec_off + 8
cell_count, cell_type = struct.unpack_from('<HH', ncer_bytes, hdr_off)
assert cell_count == 4 and cell_type == 0
cell_array_off = hdr_off + 24
entry_size = 8
obj_array_off = cell_array_off + cell_count * entry_size

cell_entries = []
for i in range(cell_count):
    off = cell_array_off + i * entry_size
    n, second, obj_off = struct.unpack_from('<HHI', ncer_bytes, off)
    cell_entries.append([n, second, obj_off])
print("cell entries antes:", cell_entries)

old_obj0_off = obj_array_off + cell_entries[0][2] * 6
old_attr0, old_attr1, old_attr2 = struct.unpack_from('<HHH', ncer_bytes, old_obj0_off)
g_before = m.obj_geometry(old_attr0, old_attr1, old_attr2, tile_boundary_shift=2)
print("obj existente antes:", g_before)

new_x = 8
new_attr1 = (old_attr1 & ~0x1FF) | (new_x & 0x1FF)
struct.pack_into('<H', ncer_bytes, old_obj0_off + 2, new_attr1)
g_after = m.obj_geometry(old_attr0, new_attr1, old_attr2, tile_boundary_shift=2)
print("obj existente despues (reposicionado):", g_after)

I21_obj0_attr0 = 0x40F8
I21_obj0_attr1_x = -24
new_obj_attr0 = I21_obj0_attr0
new_obj_attr1 = (0x8000) | (I21_obj0_attr1_x & 0x1FF)
new_obj_attr2 = (old_attr2 & 0xF000) | (new_tile_idx_raw & 0x3FF)

g_new = m.obj_geometry(new_obj_attr0, new_obj_attr1, new_obj_attr2, tile_boundary_shift=2)
print("obj nuevo:", g_new)
assert g_new['w'] == 32 and g_new['h'] == 16 and g_new['x'] == -24 and g_new['y'] == -8
assert g_after['x'] == 8 and g_after['w'] == 16 and g_after['h'] == 16

new_obj_bytes = struct.pack('<HHH', new_obj_attr0, new_obj_attr1, new_obj_attr2)

insert_at = old_obj0_off
new_ncer = bytearray(ncer_bytes[:insert_at]) + new_obj_bytes + bytearray(ncer_bytes[insert_at:])

DELTA = 6

cell0_second_field = 7
struct.pack_into('<HHI', new_ncer, cell_array_off + 0 * entry_size, 2, cell0_second_field, 0)
for i in (1, 2, 3):
    n, second, obj_off = cell_entries[i]
    struct.pack_into('<HHI', new_ncer, cell_array_off + i * entry_size, n, second, obj_off + DELTA)

struct.pack_into('<I', new_ncer, kbec_off + 4, kbec_size + DELTA)
old_ncer_filesize = struct.unpack_from('<I', new_ncer, 8)[0]
struct.pack_into('<I', new_ncer, 8, old_ncer_filesize + DELTA)

print("NCER: filesize", old_ncer_filesize, "->", old_ncer_filesize + DELTA)
print("NCER: tamano final archivo:", len(new_ncer), "(esperado:", len(ncer_bytes) + DELTA, ")")
assert len(new_ncer) == len(ncer_bytes) + DELTA

out_ncer = os.path.join(OUT_DIR, "I22S10.NCER")
open(out_ncer, 'wb').write(new_ncer)

print("\nListo. Archivos generados en", OUT_DIR)
