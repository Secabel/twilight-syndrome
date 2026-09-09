# Twilight Syndrome: Kinjirareta Toshi Densetsu (NDS) — Dossier técnico de traducción

Este documento resume TODO lo investigado y resuelto hasta ahora, para poder seguir el proyecto en un chat nuevo sin perder contexto. Adjuntar junto con `guion_principal.csv`.

## Estado del proyecto

1. **Fuente (RESUELTO y aceptado):** 54 glifos latinos (A-Z, a-z, Ñ, ñ) generados desde DejaVu Sans Condensed Bold 15px, insertados en `TWSFont.NFTR` en los índices 42-53 (los 12 que ya existían) y 60-101 (sacrificando kanjis no usados post-traducción). Probado en juego, aceptado por el usuario.
2. **Mecanismo de reinserción de texto (RESUELTO, en verificación final):** confirmado que se puede insertar texto más largo que el original sin corromper el juego, usando una zona segura de RAM (ver abajo). Pendiente de que el usuario confirme la prueba "PRUEBA TEXTO 4.nds" (2 pantallas, sin corrupción y sin corte de línea).
3. **Word-wrap:** no hay wrap automático en el motor — hay que insertar `\n` manualmente calculando el ancho en píxeles con las tablas CWDH de la fuente.
4. **Traducción real del guion (6653 líneas):** NO iniciada todavía.

## 1. Formato de fuente NFTR (TWSFont.NFTR)

Contenedor: magic `RTFN`, BOM, version, filesize u32 @8, headerSize u16 @12, numBlocks u16 @14.
Secciones: `FNIF`(28 bytes) / `PLGC`=CGLP (tiles de glifos) / `HDWC`=CWDH (anchos) / `PAMC`=CMAP (mapeo char→índice, cadena enlazada).

- **CGLP**: datos de tiles empiezan en `section_offset+24`. Cada glifo: 16×17 px, 2 bits/pixel, 68 bytes, MSB-first, 4 bytes por fila × 17 filas.
  ```python
  def pack_tile(px):  # px = lista de 16*17 valores 0-3
      tile = bytearray(68)
      for row in range(17):
          for col4 in range(4):
              b = 0
              for k in range(4):
                  col = col4*4+k
                  v = px[row*16+col] if col<16 else 0
                  b = (b<<2)|(v&0b11)
              tile[row*4+col4] = b
      return bytes(tile)
  ```
- **Valores de color (confirmado en juego, orden NO es correlativo a brillo):** 0=negro(fondo) < 3=gris oscuro(antialiasing borde) < 2=gris medio < 1=blanco(núcleo/más brillante).
- **CWDH**: 3 bytes/glifo `(bearingX:s8, glyphWidth:u8, charAdvance:u8)`. Datos empiezan en `section_offset+16`. En el build se usó `struct.pack('<bBB', 0, w, w+1)`.
- **CMAP (PAMC), header de 20 bytes**: `magic(4) + size(4) + firstChar(u16) + lastChar(u16) + method(u16) + reserved(u16) + next(u32)`. `next` = offset_del_siguiente_bloque + 8 (0 = fin de cadena).
  - La ROM tiene 5 bloques CMAP reales; el último (method=2) es un catch-all 0x0000-0xFFFF con next=0 — **NUNCA debe quedar huérfano**. El bloque nuevo se debe insertar ANTES de ese catch-all (splice), no al final.
- **Índices usados:**
  - Ya existían (reusados): `{'A':42,'B':43,'C':44,'F':45,'K':46,'L':47,'N':48,'O':49,'R':50,'S':51,'X':52,'w':53}`
  - Nuevos (sacrificiales, kanjis sin uso post-traducción): 60 a 101 (42 glifos).
  - Nuevo bloque CMAP: method=1, rango 0xA1-0xD6 (54 códigos), mapeando en orden el string `"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"` a esos índices.
- **Fuente elegida por búsqueda numérica** (no a mano): se generaron ~14 fuentes candidatas × varios tamaños, se comparó pixel a pixel contra las 12 letras reales usando un ranking de brillo `RANK={0:0,3:1,2:2,1:3}`. Ganadora: **DejaVu Sans Condensed Bold, tamaño 15px** (error promedio 0.325 sobre máximo 3). TODAS las 54 letras se regeneraron parejo con esta fuente (no mezclar técnicas/fuentes distintas dentro del mismo alfabeto — eso fue la causa real de que versiones anteriores se vieran mal).
- Script de referencia: `build_nftr_v17.py` (splice de CMAP + overwrite de CGLP/CWDH para los 54 índices). Widths finales (`anchos`) quedaron guardados en `glifos_v17_full.pkl` junto a los glifos.

## 2. Estructura del script en arm9.bin

- `arm9.bin` (1,094,360 bytes) contiene TODO el guion en Shift-JIS plano, null-terminated, sin compresión, embebido directo.
- ROM header offset 0x20: `arm9Offset=0x4000`, `arm9EntryAddress=0x02000800`, `arm9RamAddress=0x02000000`, `arm9Size=0x10b2d8` (== largo exacto del archivo, sin padding).
- **Tabla de punteros dominante:** structs de 12 bytes `{pointer:u32, flag1:u32, flag2:u32}`. `pointer` = `0x02000000 + offset_en_arm9`. `flag1` parece bit-flags/enum (velocidad de texto, retrato, sonido). `flag2` casi siempre 0. **No hay ningún campo de longitud** — el motor confía 100% en el byte nulo (0x00) de terminación. Confirmado escaneando los ~6653 offsets del CSV contra todas las ocurrencias del patrón de puntero en el binario (6675 ocurrencias, 6650/6653 offsets cubiertos).
- También existe una tabla plana de punteros de 4 bytes (stride 4) en otra zona, probablemente para menús/mensajes de sistema.
- **Codificación de las 54 letras nuevas:** cada char se codifica como el byte `0xA1 + índice_en_alfabeto` (ver alphabet arriba). `\n`=0x0A, espacio=0x20, dígitos = su ASCII normal (ya existen como glifos). Acentos/¿/¡ TODAVÍA no están mapeados (decisión del usuario: no son prioridad ahora).

```python
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"
char_to_byte = {ch: 0xA1 + i for i, ch in enumerate(alphabet)}

def encode_text(text):
    out = bytearray()
    for ch in text:
        if ch in char_to_byte: out.append(char_to_byte[ch])
        elif ch == '\n': out.append(0x0A)
        elif ch == ' ': out.append(0x20)
        elif ch in '0123456789': out.append(ord(ch))
        else: raise ValueError(f"char sin mapear: {ch!r}")
    out.append(0x00)
    return bytes(out)

def find_pointer_locations(data, text_offset):
    import struct
    ram = 0x02000000 + text_offset
    pattern = struct.pack('<I', ram)
    locs, start = [], 0
    while True:
        idx = data.find(pattern, start)
        if idx == -1: break
        locs.append(idx); start = idx+1
    return locs
```

## 3. EL BUG CRÍTICO: por qué no se puede simplemente pegar texto al final de arm9.bin

Primer intento: agregar los strings traducidos al final de `arm9.bin` (creciendo el archivo) y re-apuntar los punteros ahí. **Resultado: cuadro de texto vacío + una línea NO tocada, adyacente, se corrompía con basura (kanjis mezclados con letras latinas).**

Diagnóstico (con evidencia, no adivinando):
- Diff byte a byte confirmó que el archivo parcheado solo cambiaba los bytes de los punteros esperados — no había bug de escritura.
- Se confirmó que `ndspy` sí recalcula bien el header de tamaño del ARM9 al guardar.
- Se encontró la rutina real de arranque (crt0) del juego, en `arm9.bin` offset **0x8a8-0x8cc** (RAM 0x020008a8):
  ```
  ldr r0, [pc, #0x90]     ; r0 = puntero a una tabla de secciones (offset 0xb9c)
  ldr r1, [r0, #0xc]       ; r1 = bss_start
  ldr r2, [r0, #0x10]      ; r2 = bss_end
  loop: cmp r1, r2; if r1<r2: *r1=0; r1+=4; goto loop
  ```
  Tabla real (arm9.bin offset 0xb9c): **bss_start = 0x0210af40**, **bss_end = 0x02119320**.
- Cualquier byte que se cargue en RAM dentro de `[0x0210af40, 0x02119320)` se pone en CERO apenas arranca el juego — sin importar qué contenía el archivo ahí. Como el final de `arm9.bin` (0x0210b2d8) cae DENTRO de ese rango, todo lo que se agregue pegado al final del archivo (o incluso el final real del archivo original, en menor medida) corre riesgo de terminar en zona "bss" y ser borrado al bootear. Esto explica el cuadro vacío.
- **Por qué no se puede simplemente correr el bss_start/bss_end:** la dirección 0x0210af40 también se usa directamente en otras 4 funciones del binario (manejadores de interrupción) como dirección de una variable global real. Correr el bss_start rompería la inicialización de esa variable, y mover todo el rango de 58KB implicaría reparchear cada referencia absoluta dentro de ese rango en TODO el binario — no es viable sin un mapa de símbolos real. **Esta vía se descartó por demasiado riesgosa.**

## 4. LA SOLUCIÓN (probándose ahora mismo, pendiente confirmación final)

La RAM principal de la NDS llega hasta `0x02400000` (4MB). El juego solo usa hasta `bss_end = 0x02119320`. Todo lo que quede en RAM entre `0x02119320` y `0x02400000` (≈2.87MB) está garantizado libre y el loop de limpieza de arranque NUNCA lo toca.

**Mecanismo:**
1. Elegir una dirección de RAM segura con margen: `NEW_BLOCK_RAM = bss_end + 0x40000` (256KB de colchón por si el juego usa heap dinámico) = `0x02159320`.
2. Eso equivale al offset de archivo `0x159320` (RAM - 0x02000000).
3. Rellenar `arm9.bin` con ceros desde su tamaño actual (0x10b2d8) hasta ese offset (≈312KB de padding, una sola vez).
4. A partir de ahí, ir escribiendo TODAS las cadenas traducidas, una tras otra (con su null terminator), y repuntar cada ocurrencia del puntero original hacia la nueva dirección.
5. `ndspy` recalcula automáticamente `arm9Size` al hacer `rom.arm9 = nuevo_bytes; rom.saveToFile(...)` — no hace falta tocar el header a mano.
6. Con esto NO se toca `bss_start`/`bss_end` para nada — se evita el problema de raíz sin arriesgar nada del resto del juego.

```python
import struct
BASE_RAM = 0x02000000
BSS_END  = 0x02119320
MARGIN   = 0x40000
NEW_BLOCK_OFFSET = (BSS_END + MARGIN) - BASE_RAM  # 0x159320

data = bytearray(open('arm9.bin','rb').read())
if len(data) < NEW_BLOCK_OFFSET:
    data += bytes(NEW_BLOCK_OFFSET - len(data))

cursor = len(data)  # a partir de la primera vez, cursor ya es >= NEW_BLOCK_OFFSET
for text_offset, spanish in translations.items():   # {offset_original: "texto traducido"}
    encoded = encode_text(spanish)
    new_ram = BASE_RAM + cursor
    for loc in find_pointer_locations(data, text_offset):
        struct.pack_into('<I', data, loc, new_ram)
    data += encoded
    cursor += len(encoded)

open('arm9_patched.bin', 'wb').write(data)
```

Repack con `ndspy`:
```python
from ndspy.rom import NintendoDSRom
rom = NintendoDSRom.fromFile('original.nds')
rom.arm9 = open('arm9_patched.bin','rb').read()
rom.files[rom.filenames.idOf('Font/TWSFont.NFTR')] = open('TWSFont_v17.NFTR','rb').read()
rom.saveToFile('nueva_prueba.nds')  # SIEMPRE nombre nuevo, evita locks de emuladores abiertos
```

**Prueba en curso:** 3 líneas de diálogo (offsets 0xd6fd0, 0xd7090, 0xd69a0) repuntadas a la zona segura. Primeras 2 pantallas confirmadas OK en emulador (melonDS) — sin corrupción, texto legible. Falta confirmar la 3ra.

## 5. Word-wrap (sin resolver del todo — próximo paso real)

- No hay wrap automático: el motor no corta líneas solo. 2322/6653 líneas del CSV original ya traen `\n` manual; ninguna sin `\n` supera ~20-27 caracteres.
- Hay que calcular el ancho en píxeles de cada línea candidata usando el `charAdvance` (ancho+1) de cada letra desde CWDH, y cortar antes de superar el ancho de la caja de texto (ronda los ~230-245px de presupuesto real, a confirmar con más pruebas — la prueba de "Ese karaoke que esta frente / a la estacion" mostró que 242px de avance ya se corta, hay que dejar margen).
- Los anchos por letra (`anchos` dict) están en `glifos_v17_full.pkl`, ej: `{'A':10,'B':10,...,'W':15,...,'ñ':8}` (avance real = ancho+1).

## 6. Pendientes para el chat nuevo

1. Confirmar la prueba de la zona segura de RAM (paso 4) con las 2-3 pantallas restantes.
2. Generalizar el script de inserción para procesar las 6653 filas del CSV completo: leer `offset_hex`, `traduccion` (o `revisado`), calcular wrap por presupuesto de píxeles, codificar, ubicar en la zona segura de RAM, repuntar.
3. Traducir el guion completo (todavía no iniciado).
4. Mapear acentos y ¿/¡ cuando se retome ese tema (explícitamente despriorizado por ahora).
5. Hay un string de prueba viejo sin revertir en el `arm9.bin` real del usuario en el offset 0xd6fd0 (un alfabeto de test A-Z en sjis custom) — inofensivo pero pendiente de limpiar cuando se haga la inserción real completa (se va a sobreescribir de todos modos al traducir esa línea).

## 7. Filosofía de trabajo del proyecto (importante para el chat nuevo)

- El usuario exige evidencia verificable en emulador real, no previews estáticos ni promesas.
- No mezclar técnicas/estilos dentro de un mismo conjunto de assets (la lección de la fuente).
- No proponer soluciones que no escalen a las 6653 líneas — siempre pensar en el CSV completo, no en casos de prueba aislados.
- Preferir diagnóstico basado en desensamblado/estructura real del binario antes que prueba y error a ciegas.
