# Twilight Syndrome: Kinjirareta Toshi Densetsu — Historia del proyecto

Traducción fan (japonés -> español/inglés) del juego de Nintendo DS "Twilight Syndrome:
Kinjirareta Toshi Densetsu" (XAX Entertainment, 2008). Entrega standalone de la saga
Twilight Syndrome, sin traducción previa conocida (a diferencia de Tansaku-hen/Kyuumei-hen
en PS1, que ya tienen proyectos activos de otros traductores).

Proyecto elegido como alternativa de menor volumen tras pausar Terrors 2 (WonderSwan),
que se volvió demasiado demandante después de 5 meses.

## 2026-09-06 — Día 1: setup y primer hallazgo

**Herramientas instaladas:**
- DeSmuME 0.9.13 x64 (emulador, para debugging/memory viewer)
- TinkeDSi v0.9.6 x64 (extracción de filesystem NDS)
- HxD (búsqueda hexadecimal en dumps de RAM)

**Plan para jugar en hardware real más adelante:** Nintendo 3DS con Luma CFW, vía
TWiLight Menu++ / nds-bootstrap (corre en el chip DS real de la 3DS, no emulación).

**Hallazgos:**
- El texto en RAM está en **Shift-JIS sin comprimir**. Confirmado buscando la frase
  "使わない方が" (bytes `8E 67 82 ED 82 C8 82 A2 95 FB 82 AA`) en un dump completo de
  RAM (Dump All del memory viewer) abierto en HxD — apareció en 4 direcciones distintas.
- Dirección de buffer de texto activo en RAM: **0x0212DB2C**. Confirmado visualmente
  que se reescribe cada vez que aparece una línea nueva de diálogo (viendo el memory
  viewer en vivo mientras se avanza el texto).
- Los breakpoints de lectura/escritura del memory viewer en DeSmuME 0.9.13 no son
  confiables — no se disparan de forma consistente. No usarlos como método principal.

**Pendiente / próximos pasos:**
- Rastrear en la ROM de dónde saca el juego el texto antes de copiarlo a ese buffer
  (posiblemente vía TinkeDSi, viendo el filesystem interno del .nds).
- Evaluar no$gba (versión debug) como alternativa para debugging más fino si DeSmuME
  se queda corto (breakpoints reales, disassembler más confiable).
- Confirmar si el texto vive suelto en algún archivo del filesystem o si está empaquetado
  junto con lógica de guion (overlay).

## Estructura de carpetas del proyecto
- `desmume-0.9.13-win64/` — emulador y ROM
- `TinkeDSi-v0.9.6-x64/` — extractor de filesystem NDS
- `dumps/` — volcados de RAM (dump.bin, etc.)
- `docs/` — este archivo y futuras notas de investigación
- `scripts/` — futuras herramientas (Python u otro) para extracción/reinserción de texto
- `saves/` — savestates de referencia

## 2026-09-06 — Hallazgo grande: texto sin comprimir en arm9.bin

Se extrajo el filesystem completo de la ROM con Tinke (carpeta `extraccion_rom/`).
Buscando los bytes SJIS de "使わない方が" en TODOS los archivos extraídos, apareció
un único match: `root/ftc/arm9.bin` (el binario ARM9, no un archivo de recursos NitroFS).

**Formato confirmado:**
- El guión completo del juego vive como texto plano Shift-JIS embebido directo en
  arm9.bin, sin compresión.
- Cada línea termina en `0x00` (null-terminated); los saltos de línea dentro de un
  mismo mensaje usan `0x0A`.
- Hay un bloque grande y contiguo de diálogos reales confirmado entre offsets
  ~0xD0000–0xE5000 (miles de líneas), y probablemente continúa más allá de ese rango.
- Las carpetas EV0-EV9/R01-R24 de la ROM (NitroFS) contienen solo gráficos
  (NCLR/NCGR/NSCR = paleta/tile/tilemap), no texto.

Esto es mucho más simple que el sistema de Terrors (no hace falta code cave ni
expansión de ROM para extraer/traducir) — el único desafío esperable es el largo de
las líneas si la traducción es más larga que el original en japonés.

**Próximo paso:** escribir un script en Python que recorra arm9.bin completo,
extraiga todos los mensajes reales (filtrando ruido de código binario que decodifica
como SJIS por casualidad) a un CSV con offset + texto original, similar al
`traducciones_horizontal.csv` de Terrors.

## 2026-09-06 — Script de extracción v1

Se armó `scripts/extraer_texto.py`: recorre arm9.bin completo, separa por 0x00,
decodifica cada trozo como Shift-JIS y filtra por heurística (mínimo de caracteres
japoneses reales). Salida: `docs/texto_extraido.csv` (offset, largo, texto original,
columnas vacías revisado/traduccion para llenar después, al estilo Terrors).

**Resultado:** 7514 filas candidatas. Al graficar por rango de offset, se ve un
bloque de texto real muy claro y contiguo entre **0xD0000 y 0x110000** (~256KB,
~6650 líneas, 88% del total) — ese es el guion completo del juego. El resto
(~860 filas dispersas en 0x0–0x70000) mezcla textos de sistema/menú reales
(mensajes de error, títulos de "noticias/rumores") con ruido de código binario
que decodifica como SJIS por casualidad.

**Próximo paso:** filtrar el CSV a ese rango principal como guion "oficial", y
hacer una pasada rápida a mano sobre las ~860 filas sueltas para separar lo real
(menús, UI) del ruido antes de empezar a traducir.

## 2026-09-06 — Filtrado del CSV: confirmado, no hay textos sueltos reales

Se separó `texto_extraido.csv` en dos archivos:
- `docs/guion_principal.csv` (6653 filas, offsets 0xD0000–0x110000) — guion completo
  del juego, INCLUYE diálogos, menús y mensajes de sistema (ej. "初期化に失敗しました…",
  "第１の噂", "初期化が完了しました" — todos caen dentro de este mismo rango,
  contrario a lo que se pensaba antes).
- `docs/textos_sueltos_revisar.csv` (861 filas fuera de ese rango) — se revisó una
  muestra al azar y con un heurístico de puntuación japonesa (。！？、…「」『』):
  0 de 861 parecen texto real. Es ruido de código binario que decodifica como SJIS
  por casualidad. **Se puede descartar por completo.**

Conclusión: todo el texto traducible del juego vive en un solo bloque limpio,
`guion_principal.csv`. No hace falta revisar textos sueltos aparte.

## 2026-09-06 — Tabla de punteros: CONFIRMADA

Se buscaron en `arm9.bin` los propios offsets de texto convertidos a dirección RAM
absoluta (RAM = 0x02000000 + offset_en_archivo) como valores de 4 bytes little-endian.
Aparecen literalmente referenciados en el propio arm9.bin — o sea, el código SÍ
apunta a estos strings vía punteros de 32 bits sin ningún truco (nada de offsets
relativos ni compresión de direcciones).

Ejemplo real (offset 0xd2780 en adelante): se ven 3 punteros juntos apuntando a
las 3 frases de ayuda del tutorial (guardar/fotografiar/grabar), pero NO en una
tabla plana simple — están mezclados con otros valores (otros punteros a zonas
distintas, y números que no parecen direcciones, tipo 0x80000, 0x151000 — podrían
ser offsets a datos gráficos u otros flags de una estructura más grande por
evento/menú).

**Conclusión:** hay tabla de punteros, son direcciones absolutas de 32 bits en
RAM (fáciles de ubicar y parchar con búsqueda de bytes, sin ingeniería rara), pero
la estructura completa por entrada (además del puntero al texto) todavía no está
mapeada — probablemente cada entrada es un mini-struct con puntero(s) + otros
campos. Eso se termina de mapear cuando se llegue a diseñar el script de
reinserción real.

## 2026-09-06 — Fuente: SÍ hace falta trabajo (confirmado)

Se exportó el mapa completo de caracteres de `Font/TWSFont.NFTR` con Tinke
(`docs/font_info.txt`, 1222 glyphs en total). Resultado:

- Solo 11 de 26 letras mayúsculas latinas (A B C F K L N O R S X) y 1 sola
  minúscula (w) existen como glifos — son letras sueltas usadas dentro de
  palabras japonesas (marcas, préstamos), no un alfabeto completo.
- 0 caracteres ASCII de ancho medio (solo existen espacio, /, \\ y n como
  casos sueltos de 1 byte).
- Los 10 dígitos sí están completos.
- Ningún acento ni Ñ/¿/¡ es representable ni siquiera en Shift-JIS estándar
  (no es solo que falte el glifo — el propio charset no tiene código para
  esos caracteres). Va a hacer falta el mismo truco que en Terrors: reusar
  code points sin uso para meter esos caracteres a mano.

**Conclusión:** confirmado que hay que diseñar fuente sí o sí — agregar ~15
mayúsculas, ~25 minúsculas, y definir code points custom para acentos/Ñ/¿/¡,
igual que se hizo con la sustitución de caracteres en Terrors (aunque acá,
en vez de sustituir palabras, se pueden agregar glifos nuevos de verdad).

## 2026-09-06 — Formato de la fuente descifrado

Se parseó `TWSFont.NFTR` a mano (sin documentación oficial, por prueba y error):
- Sección CGLP (glifos): celda de **16×17 píxeles**, **2 bits por píxel** (4 tonos
  de gris, para antialiasing), **68 bytes por glifo**, bits empaquetados
  MSB-primero dentro de cada byte.
- Se armó un decoder en Python (Pillow) y se generó una grilla de prueba con los
  primeros glifos — se ve perfecto: dígitos 0-9, luego A B C F K L N O R S X,
  luego "w" minúscula, luego empieza el hiragana. Coincide 100% con lo que
  reportaba `font_info.txt`.

Con el decoder funcionando, el siguiente paso es escribir el encoder inverso
(dibujar letra -> bytes de 68 en el mismo formato) para poder insertar los ~42
glifos que faltan (15 mayúsculas, 25 minúsculas, Ñ y ñ) respetando el mismo
estilo visual que ya tienen las letras existentes.

## 2026-09-06 — Primer set de glifos generado (borrador)

Se generaron por script (Python + Pillow, fuente Liberation Serif Bold, con
efecto de contorno/outline para imitar el estilo hueco de las letras que ya
existían en el juego) los ~40 caracteres faltantes: D E G H I J M P Q T U V Y Z
(mayúsculas), a-z completo salvo w (minúsculas), Ñ y ñ.

- Estilo: contorno gris (no relleno sólido), calibrado para que coincida
  visualmente con las letras de referencia (A B C F K L N O R S X, dígitos).
- Mayúsculas y minúsculas alineadas a una línea base común (fila 11 de 17),
  con descendentes (g j p q y) usando las filas libres de abajo.
- Ñ/ñ: requirió achicar un poco la letra y correr la línea base 2px hacia abajo
  para que la virgulilla (~) entre en el alto de celda disponible — pequeño
  desvío de alineación que probablemente sea imperceptible en juego.
- Es un borrador para aprobación antes de insertarlo de verdad en el NFTR —
  falta el paso de escribir estos glifos como bytes 2bpp reales y agregarlos
  al archivo (más las entradas de CMAP/CWDH correspondientes a los códigos
  0xA1-0xD6 definidos en el mapeo de caracteres).

## 2026-09-09 — Inventario visual completo (reconocimiento, sin editar nada)

Tarea de traspaso desde `docs/handoff-inventario-graficos.md`: barrer TODA la
ROM (no solo lo que ya se sabía) buscando gráficos con texto japonés horneado
en tiles que no pasa por el CSV. Resultado completo, con capturas y la
decisión final de qué traducir, en
**[docs/hallazgos/inventario-graficos-completo.md](hallazgos/inventario-graficos-completo.md)**.

Puntos que hay que saber para retomar esto en otro chat:

- Se escribió un script **nuevo**, `scripts/inventario_completo.py`, que NO
  existía antes de hoy. Decodifica NCGR/NCBR + NCLR + (NCER o NSCR) de
  cualquier carpeta y genera hojas de contacto en
  `_scratch_claude/inventario_completo/` (se regeneran corriendo el script,
  no hace falta conservarlas).
- Ahí mismo se implementó el **decoder de NSCR** (tilemap de fondo) que el
  handoff decía que faltaba — formato: header Nitro estándar + bloque `NRCS`
  (magic 4b + size 4b + width_px u16 + height_px u16 + unknown u32 +
  data_size u32), seguido de entradas u16 (tile_id 10 bits + hflip bit10 +
  vflip bit11 + palette bits12-15).
- Se descubrió que **`.NCBR` usa el mismo contenedor que `.NCGR`** (magic
  `RGCN`, mismo bloque `RAHC`) — son sprites de personaje/animación
  (referenciados por `.NANR`), no un formato aparte. `ncer_decode.py` y el
  resto de scripts de items NO lo contemplaban; si se vuelve a tocar ese
  código, agregar `.NCBR` como alias de `.NCGR`.
- Se encontró y corrigió un bug real de renderizado por NCER: el color
  transparente NO es el índice 0 absoluto de la paleta, es el índice 0
  **de cada banco de 16 colores usado por cada OBJ** (`colors[palette*16]`,
  o `colors[0]` si el OBJ está en modo 256 colores). Sin este fix, muchos
  renders salían con parches magenta/rotos. Sigue habiendo un problema menor
  sin resolver: algunos OBJs referencian `tile_idx` fuera de rango (LOGO
  disclaimer, TITLE tarjetas de capítulo, MBP íconos) — no bloqueó la
  clasificación pero si se quiere ver esos al 100% falta investigar por qué.
- **Decisión de esta sesión:** traducir el menú de "historias" (EV9/M16-M20 +
  SAVELOAD/S00-S07, 45 archivos / ~43 títulos en 6 arcos). El resto de
  hallazgos (cadenas de mail tipo "受信メール", el papel-puzzle con tabla
  silábica, la hoja de manual "アルミホイル") se dejan **deliberadamente sin
  traducir** — motivos detallados en la sección "Decisión final" del doc de
  hallazgos (contenido ya cubierto por el diálogo principal, riesgo de
  romper la lógica de un puzzle, o dificultad técnica de redibujado mucho
  mayor que la del menú).
- Próximo paso (no arrancado todavía): traducir y redibujar el menú de
  historias, empezando por una prueba con UNA sola tarjeta antes de hacer
  las 43, para validar cómo queda antes de comprometerse al lote completo.

## 2026-09-09 (cont.) — Menú de historias EV9 traducido, ESP+ENG completo

Prueba con una tarjeta aprobada, luego se tradujeron y redibujaron las
**45 tarjetas** de EV9/M16-M20 en ESP (5 lotes de a 10, el último de 5) y
después las mismas 45 en ENG. Script: `scripts/traducir_menu_historias.py`
(`LOTE_1`...`LOTE_5` en español, `LOTE_1_EN`...`LOTE_5_EN` en inglés; se
corre como `python3 scripts/traducir_menu_historias.py [eng] <lote>`).

Puntos clave para retomar esto:

- Técnica de redibujado: estas tarjetas son NSCR de **256 colores (8bpp)**
  con una **rampa de paleta negro→rojo→blanco** para el efecto de
  resplandor (no es texto plano de 1 color). El script genera el texto
  traducido en escala de grises (núcleo sólido + blur gaussiano para el
  glow) y usa el valor de gris DIRECTAMENTE como índice de paleta
  (`core_value≈195` cae en la zona roja pura para títulos, `255`=blanco
  para las pistas). Tiene auto-ajuste de tamaño de fuente si el texto no
  entra en la caja (`auto_fit=True` en `render_glow_text`).
- Geometría de la tarjeta (fija en las 45, verificada con varias muestras
  distintas incluyendo títulos largos y el símbolo 凶): título en las filas
  de tile 14-18, pista en las filas 19-23, ambas ocupando el ancho completo
  (32 tiles). El símbolo de fortuna (大吉/中吉/凶, filas ~7-12) y el "No.XX"
  **se redibujan juntos como una sola línea de título** (no se puede tocar
  el "No.XX" por separado sin dejar restos del texto original).
- El "No.XX" reinicia en cada uno de los 6 arcos de historia (神隠しメール,
  幻のホーム, ひとりかくれんぼ/Hitori Kakurenbo, こわいテーマパーク,
  都市伝説百物語, 旧校舎のコックリさん) - no es un error que se repita
  "No.01" varias veces, así es el original.
- Convención de nombres propios (de `docs/glosario_traduccion.md`):
  "Kokkuri-san" e "Hitori Kakurenbo" NO se traducen (se mantiene también en
  la version en ingles).
- **Bug real encontrado y corregido:** en el primer intento del lote 4, a
  la tarjeta EV9/M19/1 se le agregó una segunda línea de pista que en
  realidad pertenece a la tarjeta SIGUIENTE (M19/2) — error de transcripción
  manual detectado por el usuario a simple vista. Corregido y re-verificado
  pixel a pixel contra el original. **Lección aplicada después:** antes de
  traducir cada tarjeta, renderizar su original individual a resolución alta
  y leer el texto de ahí directamente, no confiar en una transcripción hecha
  de memoria de una hoja de contacto grande con muchas tarjetas juntas —
  así se detectó también que EV9/M20/4 NO tiene línea de pista (a diferencia
  de las demás "No.01").
- Salida: `assets/graficos/{esp,eng}/EV9/M16/`...`M20/`.
- **ROM de prueba generada y verificada por el usuario:** corrió
  `generar_rom_esp.py` y confirmó "86 gráficos aplicados" (41 preexistentes
  + 45 nuevas), 0 omitidos — funcionando de punta a punta.
- **Bug de infraestructura encontrado y corregido:** tanto
  `generar_rom_esp.py` como `generar_rom_eng.py` tenían una lista
  `GRAPHICS_PATCHES` con carga automática SOLO para `ITM/2D` (los ítems) —
  cualquier gráfico nuevo en otra carpeta (como `EV9/` o `SAVELOAD/`) se
  ignoraba en silencio, sin aparecer siquiera como "omitido". Se generalizó
  esa carga automática (`os.walk` sobre TODO `assets/graficos/<esp|eng>/`)
  para que cualquier `.NCGR`/`.NCER`/`.NCBR` guardado ahí, en la carpeta que
  sea, se detecte solo — no hace falta tocar más esos scripts al agregar
  gráficos nuevos.

## 2026-09-09 (cont.) — SAVELOAD/S00-S06 traducido, ESP+ENG completo

A pedido del usuario se revisó el menú duplicado de `SAVELOAD` que había
quedado pendiente. Son **7 archivos** (`S00`-`S06`, NO 6 como se pensó en un
primer momento — error de conteo corregido tras chequeo del usuario), cada
uno con **2 columnas de texto vertical**: nombre del arco (izquierda) +
etiqueta secuencial "El N-ésimo rumor" (derecha: `はじまりの噂`,
`第1の噂`...`第5の噂`, `最期の噂`). Reveló un **séptimo arco no visto en
EV9**: `心霊写真` (Foto paranormal / Psychic Photograph), en S06. Script:
`scripts/traducir_saveload.py` (`python3 scripts/traducir_saveload.py [eng]`).

Diferencias técnicas clave respecto al menú de EV9:

- **Formato distinto:** el fondo de estas tarjetas tiene una **textura de
  grano tipo VHS horneada en la misma imagen** (no es negro liso como EV9).
  Es sutil — no siempre se nota en una miniatura chica, pero se ve clara al
  hacer zoom real. Si se borra a negro plano queda un bloque feo y visible.
  Solución: copiar los tiles de una zona SIN texto de la misma tarjeta sobre
  la zona a borrar (`copy_tiles` en el script), así el grano queda continuo,
  y después pegar el texto nuevo encima con blend por máximo (misma técnica
  de escala de grises que EV9).
- **Cuidado con los rangos de columna:** el ancho real de la columna
  izquierda VARÍA por tarjeta según el largo del nombre del arco (verificado
  con detección de píxel rojo real, no gris de grano: entre tx=2 y tx=11
  según el caso). Un primer intento con rangos angostos (medidos solo sobre
  S00) dejó restos de texto original sin borrar en varias tarjetas — hubo
  que ensanchar el borrado con margen (`LEFT_COL` tx=0-12, `RIGHT_COL`
  tx=23-31) y usar `tx=14-22` como fuente de grano (confirmado limpio de
  rojo en las 7 tarjetas).
- **Texto original vertical → texto nuevo horizontal:** el japonés original
  está en columnas verticales (natural en ese idioma), pero para
  español/inglés se decidió con el usuario redibujar **horizontal y
  centrado** (dos líneas: título del arco arriba, "rumor" abajo) en vez de
  rotar el texto latino 90° (ilegible). Layout aprobado por el usuario antes
  de aplicar a las 7.
- Traducciones ESP/ENG completas en el diccionario `CARDS` del script.
  "Hitori Kakurenbo" se mantiene sin traducir (mismo criterio que en EV9).
- Salida: `assets/graficos/{esp,eng}/SAVELOAD/S00.NCGR`...`S06.NCGR`. Los
  generadores de ROM ya lo recogen automáticamente (ver fix de arriba).

**Pendiente / sin confirmar:** no se sabe todavía en qué pantalla del juego
aparece realmente este menú (el nombre de carpeta sugiere guardar/cargar,
pero no se verificó jugando) — no bloquea nada de lo hecho, es solo
curiosidad/confirmación pendiente.
