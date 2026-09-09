# Investigación: ¿se puede traducir el texto de los objetos del inventario?

> Doc de traspaso para retomar este tema en un chat nuevo dentro del proyecto.
> Contexto general del proyecto (fuente v21, reglas operativas de save/CSV, etc.) está en
> `claude/historia-proyecto.md` y `claude/plan-tecnico.md` — no hace falta releerlos para
> este tema salvo que se necesite contexto de cómo se editan gráficos ya probados (ver abajo).

## Objetivo

Cuando abrís el inventario in-game, cada objeto tiene una pantalla de nombre + descripción.
Se sospecha (a confirmar) que el primer objeto (`I00`) es la linterna. Se quiere evaluar si
esas descripciones se pueden traducir, y si vale la pena hacerlo para los ~38 objetos o si
conviene dejarlo como deuda técnica.

## Confirmado

- **Es gráfico horneado, no texto.** Se hizo una búsqueda exhaustiva (`os.walk` sobre todo
  `extraccion_rom/`, incluyendo todas las copias/backups de `arm9*.bin`) de las frases
  candidatas de descripción (ej. "旧校舎の地図", "図書室に置いてあった") y no aparecen en
  ningún archivo como texto plano SJIS. Están dibujadas pixel a pixel en un NCGR.
- **Ubicación:** `extraccion_rom/root/ITM/2D/I{00-37}S10.NCGR` (+ `.NCLR`, `.NCER`, `.NANR`
  hermanos). Confirmado: exactamente **38 objetos** (I00 a I37).
- Además existe `extraccion_rom/root/ITM/3D/I{NN}a.nsbmd` (+ `I00.scn` etc.) — son los
  modelos 3D que rotan en el visor del objeto, no tienen que ver con el texto 2D.
- **No hay un template de tamaño fijo compartido entre objetos.** Se midió el conteo de
  tiles de varios NCGR: I00=240, I01=288, I05=276, I10=288, I20=292, I37=296. Como el
  tamaño varía, el gráfico de cada objeto parece estar ajustado al largo exacto de su texto
  japonés — esto descarta un script único que redibuje los 38 mecánicamente. Cada uno
  necesitaría trabajo individual (aunque la técnica de edición de tiles en sí es reusable,
  ver más abajo).
- **La técnica base ya está validada en este proyecto**, para los carteles de nombre de
  personaje (`SYS/G00M10.NCGR` y `SYS/G00M11.NCGR`), que sí se pudieron redibujar y están
  actualmente en la ROM final vía `GRAPHICS_PATCHES` en `generar_rom_eng.py` /
  `generar_rom_esp.py`. Esos carteles eran de tamaño fijo, que es lo que los hizo fáciles;
  los objetos no lo son.

## Bloqueado / no resuelto todavía

1. **El NCER (composición de celdas/sprites) de estos ítems no está decodificado.** Sin él
   no se sabe con certeza en qué orden/posición van los tiles en pantalla. Se intentó
   reconstruir la imagen de `I00S10` a mano probando 8 disposiciones de ancho×alto
   distintas (8x30, 30x8, 10x24, 24x10, 12x20, 20x12, 15x16, **16x15** — esta última fue la
   que se veía "legible"), pero es una **suposición**, no una lectura garantizada del NCER
   real.
2. **A esa resolución (glifos de 8x8px por tile) no se pudo transcribir el texto japonés
   con confianza**, ni siquiera con la disposición 16x15 que parecía correcta. Se intentó
   recortar y agrandar 10x la franja superior (primeras ~4 filas de tiles) — se ven trazos
   de kanji/kana pero no alcanza para leer con seguridad qué dice, y como el orden de
   lectura (punto 1) tampoco está confirmado, cualquier transcripción en este punto sería
   una adivinanza.
3. **No se confirmó si I00 es realmente la linterna.** Es la hipótesis del usuario
   ("creo que es el primero"), razonable porque suele ser el primer objeto que se obtiene
   en el juego, pero no verificada.

## Próximo paso recomendado (más confiable que seguir adivinando desde los tiles crudos)

Pedirle al usuario una **captura de pantalla in-game** (no del ROM extraído, sino del
emulador corriendo el juego real) del menú de inventario mostrando:
- El primer objeto (candidato a linterna).
- El objeto "del medio" que mencionó (candidato a mapa).

Esa imagen la compone el propio juego usando el NCER real, así que el texto sale con el
orden y posición correctos — mucho más confiable para transcribir que la reconstrucción
manual. A partir de ahí se puede:
1. Confirmar la identidad y leer el texto japonés real de 1-2 objetos.
2. Decodificar el NCER de esos mismos objetos comparando contra la captura, para entender
   el layout real (en vez de seguir probando anchos a ciegas).
3. Recién ahí evaluar el esfuerzo real de redibujar uno completo (nombre + descripción) y
   decidir si se escala a los 38 o se deja como deuda técnica (el usuario ya planteó que
   está bien dejarlo pendiente si resulta demasiado complejo).

## Notas técnicas de formato (por si se retoma la decodificación)

Parseo manual validado con `struct` (no se usó `ndspy.graphics2D`/`bncl` — su API no mapeaba
directo al formato necesario):

- **NCLR** (paleta): header de contenedor 16 bytes, luego bloque `TTLP`:
  `magic(4)+size(4)` seguido de `bitDepth(u32)+padding(u32)+dataSize(u32)+reserved(u32)`
  (16 bytes de sub-header), y a partir de ahí los colores: `dataSize//2` valores `u16` RGB555
  (`r=(c&0x1F)*8, g=((c>>5)&0x1F)*8, b=((c>>10)&0x1F)*8`).
- **NCGR** (tiles): header de contenedor 16 bytes, luego bloque `RAHC` en offset absoluto 16:
  `magic(4)+size(4)+tilesY(u16, frecuentemente 0xFFFF="sin especificar")+tilesX(u16, igual)
  +bitDepth(u32, 3=4bpp)+...+tileDataSize(u32, en offset relativo +24 desde el inicio de
  RAHC)`. Los píxeles empiezan en offset absoluto `16+0x20` (0x30); cada tile 4bpp son 32
  bytes = 64 píxeles (2 px/byte, nibble bajo primero).
- Paleta de `I00S10.NCLR` ya decodificada (16 colores, 4bpp): índice 0 = `(0,248,0)` verde
  (transparencia), índice 1 = negro (contorno), índice 3 = `(224,224,224)` blanco/gris claro
  (relleno del texto), el resto son tonos azul/gris oscuro (contenido no identificado, probablemente
  el fondo/icono debajo del texto).
- Carpeta de trabajo en el dispositivo del usuario para PNGs de debug:
  `$HOME/mnt/Twilight Syndrome Kinjirareta Toshi Densetsu/_scratch_claude/` (los PNG
  generados con `device_bash` no se pueden `device_stage_files` directo desde `/tmp`, por
  eso se guardan ahí antes de subirlos).

## Reglas operativas del proyecto (aplican también acá)

- Nunca reutilizar un savestate creado con una ROM build distinta a la que se está
  probando — arrancar de cero después de cada regeneración.
- Si en algún momento esto lleva a tocar CSVs de guion, hacer backup con fecha/hora antes
  de editar.
