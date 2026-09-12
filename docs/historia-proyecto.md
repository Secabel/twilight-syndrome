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
- `scripts/` — herramientas Python para extracción/reinserción de texto y edición de
  gráficos (ver nota del 2026-09-08 más abajo: todo lo que no sean los dos generadores
  de ROM vive acá)
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

## 2026-09-06 — Fuente: proceso largo de prueba y error, y decisión final

Insertar los ~42 glifos latinos faltantes terminó siendo mucho más largo de lo
esperado — vale la pena dejar registrado todo lo que se probó y por qué, para no
repetir los mismos callejones sin salida si se retoma el tema.

**Estructura técnica del NFTR (confirmada y validada en juego):**
- Contenedor: header `RTFN` + secciones `FNIF`/`PLGC`(CGLP)/`HDWC`(CWDH)/`PAMC`(CMAP,
  puede haber varias encadenadas). Cada puntero interno (FINF, `next` de CMAP) vale
  `offset_absoluto_de_la_sección + 8` (el +8 salta el propio magic+size de 8 bytes).
- CGLP: tile de 16×17px, 2 bits/píxel, 68 bytes/glifo, MSB-primero, 4 bytes por fila.
- CWDH: 3 bytes por índice de glifo: `(bearingX:s8, glyphWidth:u8, charAdvance:u8)`.
- CMAP: lista enlazada de bloques; método 1 = tabla plana de índices u16 para un
  rango chico de códigos, método 2 = catch-all (todo el rango 0x0000-0xFFFF) al
  final de la cadena — **hay que preservarlo al insertar un bloque nuevo** (insertar
  ANTES del catch-all, nunca reemplazarlo, o se pierden los glifos por defecto de
  todo el resto de la fuente).
- Paleta de color real (encontrada por prueba empírica, la paleta NCLR del font está
  vacía/sin usar — el mapeo real vive en el motor de render): de los 4 valores de
  2 bits, el orden de brillo real en pantalla es **0=negro (fondo) < 3=gris oscuro
  (~RGB 48) < 2=gris medio < 1=blanco (~RGB 227, el más brillante)** — NO es orden
  ascendente ingenuo. Confirmado por: (a) test de bloque sólido value=3 se vio gris
  no blanco; (b) test de alfabeto completo con value=1 se vio blanco correcto en
  DeSmuME 0.9.13 Y en melonDS 1.1 (dos emuladores distintos, descarta bug de un
  solo emulador); (c) muestreo directo de píxeles RGB de una captura real del juego
  con `Counter` de Python confirmó exactamente esos dos extremos.
- Estilo real de las letras: relleno sólido antialiaseado normal (no hueco/outline
  como se pensó en un momento intermedio) — un trazo recto típico tiene 3px de ancho
  con perfil "gris medio - blanco brillante - gris medio" (comprobado decodificando
  directamente los tiles reales de A, B, N con un script Python, sin intermediarios).
- Estrategia de inserción usada: sacrificar 42 slots de kanji poco/nada usados
  (índices 60-101) para los glifos latinos nuevos, en vez de agregar índices nuevos
  al final (**el enfoque de append con índices ≥1229 falló en juego con glitches
  gráficos**, sospecha de límite de VRAM/tiles hardcodeado en el ARM9, nunca
  confirmado ni descartado del todo — se abandonó esa vía por completo). Los
  índices 60-101 se sacrifican sin problema porque, una vez traducido el guion
  completo, ya no queda japonés que los necesite.
- Un nuevo bloque CMAP (método 1, códigos `0xA1`-`0xD6`, 54 entradas) mapea el
  abecedario completo a esos índices; se insertó en la cadena justo ANTES del
  bloque catch-all existente (ver arriba).

**Intentos de estilo que NO funcionaron (en orden cronológico):**
1. Serif Bold con contorno/erosión — demasiado grueso, la erosión fallaba en bordes
   pegados a la izquierda (columna 0) y en trazos gruesos.
2. Serif Regular con erosión + padding — quedó fino en aislado pero no coincidía
   en juego ("mucho más gruesas las originales").
3. DejaVu Sans ExtraLight (esqueleto fino) con solo 2 niveles de gris (blanco/negro)
   — visualmente parecido en preview estático, pero en juego se veía "pálido"/débil
   al lado de las letras reales, y la interpretación de "hueco" resultó estar mal
   (ver paleta de color arriba).
4. DejaVu Sans Regular con 3 niveles de gris ya bien mapeados — mejora real pero
   seguía viéndose "más fino" que las letras originales al lado.
5. **Reconstrucción por "cirugía de píxeles"**: en vez de renderizar con una fuente
   externa, se armaron las 42 letras faltantes recortando y recombinando literalmente
   los píxeles reales de las 12 letras que sí existían en el juego (ej. la P sale
   del arco superior de la B real, la D del óvalo de la O real + un palo, etc.).
   Conceptualmente sólido (son píxeles reales, no aproximación), pero en la práctica
   generó errores de construcción letra por letra (una J que se veía como nota
   musical, una M con un fragmento flotante, solapamientos de columna en H/K) que
   tomó varias vueltas de corregir, y aun corregido el resultado se sentía
   inconsistente: 12 letras "de verdad" mezcladas con 42 aproximaciones notoriamente
   distintas al lado. **Fue la causa real de que el parche se viera mal**, no que
   las letras individuales estuvieran rotas.

**Decisión final (aceptada por el usuario):** en vez de mezclar 12 glifos originales
con 42 nuevos, se reemplazaron **las 54 letras (A-Z, a-z, Ñ, ñ) con una sola fuente
generada de forma uniforme** — incluyendo redibujar las 12 que ya andaban bien.
Se usó una búsqueda numérica real (no a ojo): se renderizaron ~14 fuentes candidatas
del sistema (DejaVu, Liberation, FreeSans, TeX Gyre Heros, Poppins) en un rango de
tamaños, y se comparó cada una píxel por píxel (con un score de distancia de brillo)
contra los 12 glifos reales conocidos. Ganó **DejaVu Sans Condensed Bold, tamaño 15px**
(error promedio más bajo). El resultado se ve parejo en todo el alfabeto — se pierde
fidelidad al arte original del juego, pero se gana consistencia interna, que era lo
que realmente rompía la ilusión en los intentos anteriores. Aceptado en juego
(ROM de prueba "PRUEBA FUENTE 9.nds") el 2026-09-06.

**Lección para el futuro:** si se vuelve a tocar la fuente (por ejemplo para afinar
el parecido con el arte original), NO mezclar glifos de dos fuentes/técnicas
distintas dentro del mismo alfabeto — la inconsistencia interna es más notoria y
molesta que el parecido imperfecto con el original.

## 2026-09-07 — Reinserción completa del guion, fuente v18/v19, y gráficos de nombre

Resumen de una sesión larga que llevó el proyecto de "fuente resuelta pero sin
guion insertado" a **dos ROMs jugables completas (ESP y ENG)**.

### El bloqueo real: por qué texto más largo que el original corrompía el juego

Las primeras pruebas de reinserción (agregar el texto traducido al final de
`arm9.bin` y repuntar) corrompían el juego apenas la traducción era más larga
que el original. La causa NO era el repunteo en sí, sino el **loop de limpieza
de bss del crt0**: el ARM9 real tiene un loop (offset de archivo 0x8a8-0x8cc)
que lee `bss_start=0x0210af40` y `bss_end=0x02119320` desde una tabla de
secciones (offset de archivo 0xb9c) y **pisa con ceros todo ese rango en RAM al
arrancar** — incluyendo cualquier texto nuevo que hubiéramos agregado ahí.

**Solución (validada en juego con capturas reales):** nunca tocar
`bss_start`/`bss_end` (se usan como direcciones de variables globales reales en
otras partes del código, moverlos es riesgoso). En cambio, colocar todo el texto
traducido en una "zona segura" bien por encima de `bss_end`, con un colchón de
seguridad: `RAM = bss_end + 0x40000` (offset de archivo `0x159320`), rellenando
`arm9.bin` con ceros hasta ese punto y appendeando ahí todo el texto codificado,
secuencialmente, repunteando cada entrada a su nueva dirección. Esto escala sin
límite (no hay que buscar huecos vacíos por pantalla ni nada por el estilo) y
quedó demostrado insertando el guion completo (6654 líneas) sin un solo error.

### Ancho seguro de línea

No hay word-wrap automático en el motor — todos los saltos de línea son
manuales (`\n`). Presupuesto de ancho confirmado por prueba real en juego para
la caja de diálogo normal: **≤220px** por línea (242px cortó texto a mitad de
palabra en una prueba). Ver más abajo (2026-09-07, sesión de banner/caja angosta)
por el descubrimiento de que este límite NO aplica a todas las cajas de texto del
juego.

### Fuente: v18 y v19 (extensión de la v17 ya validada)

La v17 (54 letras) no cubría signos de puntuación ni algunos símbolos que
aparecen en el guion real. Se fueron agregando a medida que la propia
herramienta de reinserción los detectaba como "carácter no soportado":

- **v18**: +12 signos `. , ? ! ( ) - " : ' < ^` (66 glifos totales).
- **v19**: +4 más `* > / #` (70 glifos totales, códigos `0xA1`-`0xE6`).

Mismo mecanismo que la v17: sacrificar índices de kanji sin uso (60 en
adelante) y encadenar un bloque CMAP nuevo antes del catch-all existente.

(Nota: la v19 quedó reemplazada por v20 y luego por **v21** el 2026-09-08 —
ver la sección del bug de bytes líder Shift-JIS más abajo para el detalle
completo de por qué v20 no fue la versión final.)

### Herramienta de reinserción reusable

Se armaron `generar_rom_esp.py` y `generar_rom_eng.py`: scripts sin argumentos,
doble-click-and-run, que toman el CSV correspondiente + la fuente + la ROM base
y generan la ROM parcheada completa, con validación propia (caracteres no
soportados, líneas que superan el ancho seguro, offsets sin puntero encontrado).
Última corrida limpia: **6654 líneas escritas, 7 salteadas (vacías/placeholder),
6677 punteros repunteados, 0 errores**, tanto en ESP como en ENG.

### 8 líneas adicionales encontradas

Se hizo una pasada de verificación cruzada (CSV original vs. escaneo directo de
`arm9.bin` buscando patrones de puntero no cubiertos) y aparecieron 8 líneas
reales que la extracción original no había capturado (diálogos cortos, números
de teléfono/clave, un nombre de lugar). Se tradujeron directo en el chat y se
mezclaron a ambos CSV.

### Investigación de gráficos con texto: qué es editable y qué no

A raíz de una pregunta del usuario sobre si el recuadro de nombre de personaje
(caja de color con letras japonesas debajo de cada diálogo) era texto o
gráfico, se hizo una inventariado sistemático de todos los archivos NCGR/NCLR
(gráficos de tiles) del filesystem de la ROM:

- **Confirmado como gráfico puro (texto horneado en los tiles, no reinsertable
  vía el CSV/fuente)**: las ~38 pantallas de descripción de ítems del
  inventario, el texto del menú de guardado (はい/いいえ/記録/戻る y el título
  rojo tipo leyenda urbana), título, logo, mensajes de error, créditos finales.
  **Decisión del usuario en ese momento: no se van a editar** — no eran
  necesarios para poder jugar/entender el juego (evaluación hecha sin saber
  todavía que el menú de objetos era relevante para resolver puzzles/progresar
  en la historia; **ver revisión de esta decisión el 2026-09-08 más abajo**).
- **Cartel de nombre de personaje (SYS/G00M10.NCGR + G00M11.NCGR, con su
  NCLR/NCER)**: identificado como el único gráfico de texto que SÍ vale la pena
  tocar, porque aparece en cada línea de diálogo. `G00M11` resultó tener el
  elenco completo pre-armado: レイカ, カナ, メグミ, アリサ, ミズキ, リコ,
  マサキ, ユウタ, ナナカ, ユイ, マユコ, ユカリ (cada nombre es un sprite de
  40×16px ya compuesto, con su propio color de fondo). Se editaron los tiles
  (redibujando solo los píxeles del texto, blanco sobre el mismo fondo/color
  original) para mostrar los nombres romanizados (REIKA, KANA, MEGUMI, ARISA,
  MIZUKI, RIKO, MASAKI, YUUTA, NANAKA, YUI, MAYUKO, YUKARI). Validado en juego.
  **Este gráfico es compartido entre ESP y ENG** (misma romanización en los dos
  idiomas) — a diferencia de los ítems (ver sección del 2026-09-08 más abajo),
  por eso vive plano en `assets/graficos/`, no separado por idioma.

**Criterio acordado en ese momento para el resto de los gráficos con texto:** no
se tocan salvo que aparezca algo cuyo texto NO tenga equivalente en el CSV (o
sea, que la única forma de leerlo sea ese gráfico) y que además bloquee
entender/jugar el juego — no por completitud estética. El menú de guardado,
ítems, etc. quedaban como estaban. **Esto se revisó el 2026-09-08, ver abajo.**

### Reorganización del proyecto

Se creó `assets/` en la raíz del proyecto (en la máquina del usuario) para que
`generar_rom_esp.py`/`generar_rom_eng.py` lean todo desde un solo lugar
ordenado, en vez de archivos sueltos en la raíz:

- `assets/csv/guion_principal_esp.csv`, `guion_principal_eng.csv`
- `assets/font/TWSFont_v19.NFTR`
- `assets/graficos/G00M10.NCGR`, `G00M11.NCGR` (carteles de nombre editados)

Los scripts se actualizaron para leer de ahí y aplicar automáticamente los
gráficos editados al generar la ROM. Se borraron los duplicados viejos que
habían quedado sueltos en la raíz y dentro de `extraccion_rom/`.

### Estado al cierre de esta sesión

Dos ROMs completas y jugables: `Twilight Syndrome - ESP.nds` y
`Twilight Syndrome - ENG.nds`, con guion completo, fuente v19, y nombres de
personaje traducidos. Pendiente: revisión de neutralidad del español
(argentinismos encontrados, ver doc de revisión aparte) y cualquier ajuste que
salga de seguir jugando/probando.

## 2026-09-07/08 — Título del banner del ROM (metadata del menú)

A pedido del usuario, se agregó edición del "banner" del ROM (bloque de icono +
título que lee el menú del sistema / TWiLight Menu++, separado del guion y del
arm9): función `set_banner_title()` agregada a `generar_rom_eng.py`/`_esp.py`,
que reemplaza el título de un idioma del banner (offsets `0x240 + 0x100*lang_index`,
lang_index 0=JP,1=EN,2=FR,3=DE,4=IT,5=ES) y recalcula el CRC16 (`poly 0xA001,
init 0xFFFF`, verificado contra el CRC original del banner pristino — coincide).

**Detalle importante encontrado en pruebas:** la consola muestra el título del
idioma que corresponde al firmware del sistema (no necesariamente inglés/español
según la versión de ROM) — un New 3DS con firmware en español lee el slot 5 (ES)
aunque se esté jugando la ROM "ENG". Solución: escribir el mismo título nuevo en
los 6 slots de idioma, no solo en el "propio" del idioma de esa ROM.

**Nota operativa:** los cambios a los scripts se hicieron primero en el entorno
de trabajo de Claude y no llegaron a la carpeta real del proyecto en la PC del
usuario — hubo que re-aplicar el parche directamente ahí con `device_bash`
después de que el usuario reportara que no había tenido efecto. Para cualquier
cambio futuro a estos scripts, confirmar que se está editando el archivo real
del proyecto (en la carpeta del usuario), no una copia en otro lado.

## 2026-09-08 — Caja de texto angosta (mensajes de tutorial/pista) corta palabras

El usuario notó que ciertas pantallas cortan palabras a mitad de camino aunque
la línea mida menos de 220px (el límite ya confirmado para diálogo normal). Se
investigó a fondo vía desensamblado real del ARM9 (capstone, `CS_ARCH_ARM,
CS_MODE_ARM`), no por heurística de contenido:

**Hallazgo:** existe una función de renderizado distinta, `0x0203E75C`, usada
solo para mensajes de tutorial/pista (no diálogo de personajes). Se encontraron
sus **3 únicos sitios de llamada en todo el arm9.bin** (decodificando instrucción
por instrucción, alineado a 4 bytes — el disassembly en stream desde el inicio
del binario desincroniza y da falsos negativos, hay que decodificar cada
posición de 4 bytes por separado):
- `0x28168` y `0x28bec` (grupo "control", 9 mensajes) — arreglo en `0xe67a4`,
  offsets: `0xe668c, 0xe6640, 0xe6728, 0xe66c0, 0xe65f8, 0xe6664, 0xe6760,
  0xe66f4, 0xe6550`.
- `0x2c458` (grupo "teléfono/tutorial email", 6 mensajes) — arreglo en
  `0xd3654`, offsets: `0xd3a00, 0xd3a54, 0xd3920, 0xd3944, 0xd3b30, 0xd3b5c`.
- Un tercer grupo ("consejos generales": guardar partida / fotografiar
  espíritus / grabar sonido), 3 mensajes — offsets: `0xd2c40, 0xd2c74, 0xd2c14`.

Total: **18 líneas** usan esta caja angosta, identificadas por code tracing
(no por palabras clave en el texto).

**Ancho real de la caja:** contrastando screenshots reales (dónde se corta cada
palabra) contra `line_width()`, se determinó que el límite real es más chico
que 220px y **no es uniforme entre los 3 grupos** (ej. "Control Megumi with th"
a 201px entra completo, pero "screen is on the bottom," a 210px y "Head to the
music room" a 204px se cortan a mitad de la última letra) — probablemente cada
sitio de llamada configura su propio ancho de caja aunque compartan la función
de dibujado. Se optó por un límite conservador único de **180px** para las 18
líneas. Aplicado a las 18 líneas en ambos idiomas (ESP/ENG). **Este fix quedó
confirmado como real y correcto** (ver sección de savestates más abajo: es el
único de los dos bugs de texto de esta etapa que era genuino).

## 2026-09-08 — Líneas de diálogo real que se escaparon de la extracción original

A raíz de un glitch visual (dos letras "Z" apareciendo en medio de una línea en
japonés sin traducir), se investigó y se encontró que **el bug real no era la
fuente sino que a la línea nunca se le habia hecho traducción**: 4 líneas de
diálogo real, con puntero válido y usadas en juego, que la extracción original
(`extraer_texto.py`, split por `0x00`) nunca capturó — típicamente porque el
texto empieza inmediatamente después de un arreglo de punteros (sin un `0x00`
limpio justo antes), lo que rompe el supuesto de "todo texto real está entre
dos separadores 0x00" del extractor.

Se hizo un escaneo sistemático de "huecos" entre los offsets ya cubiertos por el
CSV dentro del rango 0xD0000-0x110000, decodificando cada hueco como SJIS y
filtrando por densidad de caracteres japoneses reales. Encontró exactamente 4
líneas reales perdidas (todas confirmadas con puntero real en arm9.bin):

- `0xd366c` — "今さら、コックリさん…？" (puntero en `0x820cc`)
- `0xea67c` — "（７７４……ナナシ…？）" (puntero en `0x9d550`)
- `0xf46e0` — "９月……？\n９月……く…月……。" (puntero en `0xa8320`)
- `0x101e60` — "あ………う……っ……。" (puntero en `0xbaf10`)

Traducidas y agregadas a ambos CSV (ESP/ENG), ROMs regeneradas — CSV pasó de
6654 a 6658 líneas, 0 errores. (El detalle de por qué el glifo mostraba
específicamente "Z" —el índice de glifo 74, reasignado a la letra Z al armar
la fuente, resultó ser el que originalmente usaba el hiragana さ— es una
curiosidad de diagnóstico, no la causa raíz real ni algo que importe una vez
que todo el guion está traducido: como el juego nunca vuelve a mostrar texto
japonés original, no hay riesgo de colisión de glifos en la práctica.)

**Lección para el futuro:** si aparece cualquier texto en japonés sin traducir
en juego, buscar primero si el offset está en el CSV — si no está, es un caso
de este mismo bug de extracción (texto pegado a una tabla de punteros u otra
estructura sin separador limpio), y conviene re-correr un escaneo de huecos
como el de arriba para ver si hay más casos parecidos en zonas del guion que
todavía no se jugaron/revisaron.

## 2026-09-08 — Bug sistémico: apóstrofe y otros 6 símbolos "se comían" la letra siguiente

El usuario reportó una letra faltante en "phone's" (se veía como "phone s") en
una captura real. Se investigó a fondo en vez de simplemente re-wrappear esa
línea, porque el patrón (falta justo la letra después de un signo) olía a un
problema de codificación, no de ancho.

**Causa raíz confirmada:** en la v18/v19 de la fuente, los 7 caracteres
`' < ^ * > / #` habían quedado asignados a los códigos `0xE0`-`0xE6` (siguiendo
la misma lógica que el resto del alfabeto custom en `0xA1`+). El problema es
que **`0xE0`-`0xFC` es un rango real de "primer byte de un carácter de 2 bytes"
en Shift-JIS** — cualquier motor de texto que avance por el string interpretando
SJIS real (como hace este juego) toma el byte en `0xE0`+ como el inicio de un
carácter de 2 bytes y **se come el siguiente byte completo**, sin importar qué
diga el CMAP de la fuente sobre ese código. Confirmado de forma reproducible:
`bytes([0xE0, 0x73]).decode('shift_jis')` da un solo carácter (`'灣'`), probando
el comportamiento de "devorar" el byte siguiente.

Esto afectaba a **~2450 líneas en inglés y 12 en español** (cualquier línea con
apóstrofe u otro de esos 6 símbolos), perdiendo la letra inmediatamente después
del símbolo en cada caso (ej. "It's" → "It  s", "won't" → "won  t").

**Primer intento de fix (v20) — NO funcionó en juego:** se creó `TWSFont_v20.NFTR`
agregando **3 bloques CMAP nuevos** (`0x22-0x2F`, `0x3C-0x3F`, `0x5E-0x5F`) de
una sola vez, insertados antes del catch-all. Estructuralmente se veía perfecto
(verificado por recorrido de la cadena CMAP: los 7 códigos resolvían al glifo
correcto), pero en juego el problema seguía igual. Causa probable: el patrón
que sí estaba validado en v17→v18→v19 siempre agregó **exactamente 1 bloque
PAMC por revisión** — v20 agregó 3 de una vez, rompiendo probablemente algún
límite fijo de bloques que lee el motor del juego al cargar la fuente (nunca
confirmado con certeza absoluta, pero coincide con la evidencia: v20 no
funcionaba, y un rediseño que vuelve a "+1 bloque" sí).

**Fix final (v21) — validado:** en vez de 3 bloques nuevos, se construyó **un
solo bloque combinado** que reemplaza al bloque viejo (`0xA1-0xE6`) en la
cadena, ampliando su rango a `0x22-0xE7` (mismo conteo total de bloques PAMC
que v19, solo que uno de ellos es más ancho). Mapea los 63 caracteres seguros
igual que antes, más los 7 símbolos reasignados a sus códigos ASCII propios
(`'`=0x27,`<`=0x3C,`^`=0x5E,`*`=0x2A,`>`=0x3E,`/`=0x2F,`#`=0x23 → glifos 111-117).
`generar_rom_eng.py`/`_esp.py` actualizados a `FONT_PATH = "assets/font/TWSFont_v21.NFTR"`
en ambos, y el `BYTE_MAP` codifica esos 7 caracteres directo con su valor ASCII
(`_ASCII_DIRECTO`), en vez de con el esquema genérico `0xA1+i`.

**Lección para el futuro (dos partes):**
1. Al asignar códigos custom a caracteres nuevos en esta fuente, nunca usar el
   rango `0xE0-0xFC` para un carácter de un solo byte — es territorio de
   lead-byte SJIS real. El rango seguro es `0xA1-0xDF` más los códigos ASCII
   imprimibles normales (`<0x80`).
2. Si se necesita agregar más de un bloque CMAP nuevo a la vez, preferir
   **consolidarlos en un solo bloque** (ampliando el rango) en vez de encadenar
   varios bloques nuevos de una sola vez — el patrón de "+1 bloque por
   revisión" es el que está validado en juego; agregar varios de golpe no lo
   está y en la práctica falló.

## 2026-09-08 — Falso bug de "4 líneas / cuadro sin dibujar": era el savestate, no el texto

Después de aplicar el fix de la fuente (v21), al probar en melonDS varias
pantallas de las 18 de la caja angosta parecían mostrar 4 líneas en vez de 3 y,
en algunos casos, **sin el cuadro de fondo alrededor del texto**. Se investigó
durante un buen rato como si fuera un bug real de ancho/wrap (se llegó a acortar
la redacción de 15 de las 18 líneas para intentar forzarlas a 3 líneas), sin
éxito — el "bug" persistía igual sin importar qué se le cambiara al texto.

**Causa real, encontrada por el usuario:** las pruebas fallidas se hicieron
cargando un **savestate creado con una versión anterior del ROM** (de antes del
fix de la fuente). Al probar la MISMA rom pero arrancando de cero (sin
savestate), el mismo texto —sin ningún acortado— se vio perfecto: 3 líneas, con
su cuadro. Confirmado además retomando una traducción que ya tenía el ancho
correcto (algunas de las líneas "rotas" ni siquiera habían sido tocadas en esta
sesión, solo se les movió el salto de línea sin cambiar palabras — si fuera un
bug de wrap real, mover el salto no debería haber cambiado nada, y efectivamente
no cambió nada en pantalla, lo cual en su momento se malinterpretó como
evidencia de un motor que "ignora los saltos manuales", cuando en realidad el
savestate viejo estaba mostrando memoria vieja, ajena al contenido real del
archivo .nds).

**Mecanismo:** un savestate es una foto completa de la RAM en ese instante,
incluyendo variables internas (anchos de caja, posiblemente texto ya cacheado)
que el juego calculó para la versión del ROM con la que se generó el
savestate. Al cargarlo sobre una ROM regenerada (con el texto en otro
tamaño/posición dentro de `arm9.bin`), esas variables quedan desincronizadas y
el resultado es corrupción visual arbitraria — no relacionada con el contenido
real del texto ni con la fuente.

**Se revirtieron** las 15 líneas que se habían acortado innecesariamente (6 en
ENG: `0xe6728, 0xe66c0, 0xe6760, 0xe66f4, 0xd2c40, 0xd3b30`; 9 en ESP:
`0xe668c, 0xe66c0, 0xe6760, 0xe66f4, 0xd2c40, 0xd2c14, 0xd3a54, 0xd3920,
0xd3944`) a su versión de antes de este episodio (que era la correcta). El
único fix de texto real que sigue en pie de esta etapa es el rewrap a 180px de
ayer (2026-09-08, sección de la caja angosta) — ese sí era un bug genuino.

**Guardado in-game vs. savestate:** un guardado hecho desde el menú del propio
juego (SRAM/flash, no el savestate F1/F2 del emulador) debería ser seguro de
reusar entre versiones del ROM, porque solo contiene los datos que el juego
mismo decide persistir a través de su propia rutina de guardado (posición,
progreso, flags), no una foto cruda de la RAM — no incluye cachés de
renderizado ni depende de dónde quedó el texto en el `arm9.bin` de esa build
específica. Es una inferencia lógica, todavía sin confirmar en juego; ver
`plan-tecnico.md` para las reglas operativas derivadas de este episodio
(nunca reusar un savestate entre builds; backup de CSV antes de editar).

## 2026-09-08 — Revisión de la decisión sobre los gráficos de ítems: SÍ vale la pena traducirlos

El criterio original de "no editar el menú de ítems" (ver sección del
2026-09-07 más arriba) se tomó sin saber que el juego tiene un menú de objetos
del inventario cuyo examen es relevante para resolver puzzles y progresar en la
historia — no era solo un elemento estético/de sabor. Una vez que el usuario
notó esto, se revirtió la decisión: **sí vale la pena traducir las 38
descripciones de ítems.**

En paralelo se resolvió el bloqueo técnico que había dejado el tema pendiente
(el NCER no estaba decodificado — ver `claude/investigacion-items-graficos.md`
para el detalle completo del formato, el bug de `tileBoundaryCode` que lo
resolvió, y el script `ncer_decode.py` ya funcional y probado en 5 ítems).

**Aclaración importante sobre la dificultad de redibujar (distinto al caso del
guion/CSV):** como esto es gráfico horneado y no texto renderizado por el motor
de fuente (NFTR), el tamaño de letra y el quiebre de líneas se pueden ajustar
libremente por ítem — no hay una única fuente global de por medio como en el
guion principal. El único límite real es que la caja decorativa de fondo
(fondo violeta/textura, celda 2/3 del NCER) tiene una altura fija por ítem
(1 o 2 líneas, la que ya usaba el japonés); si la traducción entra en esa
misma cantidad de líneas con una fuente más chica, el reemplazo es solo pintar
tiles nuevos (mecánico); si necesita una línea más, hay que además agrandar la
caja de fondo editando el NCER (más trabajo, pero ya no hay incógnita técnica
de por medio).

**Próximo paso acordado:** extraer el texto japonés de los 38 ítems con
`ncer_decode.py` para tener el panorama completo antes de traducir/redibujar
ninguno.

## 2026-09-08 — Ítems: 37/38 redibujados, integrados al pipeline separados por idioma

Trabajando en tandas de 5 (con revisión visual — PNG de contacto — antes de cada
regeneración de ROM, ya que la mayoría de los ítems no estaban desbloqueados en
la partida del usuario), se completó el redibujado de **37 de los 38 ítems**.
Solo quedó pendiente **I22 (palillos, 箸)**: su caja de nombre mide apenas 16×16px
(un solo tile), heredado de que el japonés original es un único carácter muy
angosto — ninguna palabra española entra ahí ni en fuente mínima. El usuario
decidió explícitamente dejarlo pendiente por ahora y seguir con el resto.
Ver `claude/investigacion-items-graficos.md` para el detalle completo (los 3
bugs de redibujado resueltos, la tabla completa de las 38 traducciones, y el
estado de cada tanda).

**Integración al pipeline de build (a pedido del usuario, separada por idioma):**
los 37 NCGR editados se movieron de la carpeta de trabajo (`_scratch_claude/`) a
`assets/graficos/esp/ITM/2D/`, y `generar_rom_esp.py`/`generar_rom_eng.py` se
actualizaron para levantar automáticamente cualquier `.NCGR` que encuentren en
`assets/graficos/<idioma>/ITM/2D/` (sin tocar la lista `GRAPHICS_PATCHES` a
mano). A diferencia de `G00M10`/`G00M11` (compartidos entre ESP/ENG porque son
nombres romanizados, iguales en los dos idiomas), el texto de los ítems es una
oración completa en español — no sirve para ENG, así que cada idioma tiene su
propia carpeta. `assets/graficos/eng/ITM/2D/` se creó vacía (todavía no hay
traducción al inglés de los ítems); mientras esté vacía, `generar_rom_eng.py`
simplemente no toca esos gráficos y quedan en japonés en la ROM ENG, igual que
antes de este trabajo.

**Corrección a una suposición anterior:** el pipeline de `generar_rom_esp.py`
usa `ndspy` (reempaqueta la ROM completa, incluyendo el FAT del NitroFS), no el
parcheo manual de bytes in-place que se usó para las pruebas rápidas de cada
tanda. Esto significa que un NCGR de tamaño distinto al original (por ejemplo,
si se decide extender el NCER de I22 para poder traducirlo) **no requiere tocar
el FAT a mano** — `ndspy` ya lo maneja. La ROM de prueba generada durante el
trabajo por tandas (parcheo manual, solo con I00-I02) queda obsoleta; la próxima
ROM se genera corriendo `generar_rom_esp.py` normalmente.

## 2026-09-08 (cierre) — Ítems: 38/38 completos en ESP e ENG, I22 resuelto extendiendo el NCER

La sección anterior quedó en "37/38, I22 pendiente" — se cierra acá con el
estado final: **los 38 ítems están completos en español e inglés**, integrados
al pipeline de build.

I22 (palillos/箸) tenía una caja de nombre de apenas 16×16px (un solo tile), sin
espacio para ninguna traducción. Se resolvió **extendiendo el NCER** (agregando
un OBJ/8 tiles nuevos a la celda 0, copiando el layout de I21 "Cuenco" como
plantilla) — la caja pasó a 48×16px, suficiente para "Palillos" (33px) y
"Chopsticks" (44px a 8px). El NCER extendido quedó como archivo compartido
(`assets/graficos/I22S10.NCER`, mismo criterio que `G00M10`/`G00M11`) porque la
geometría no depende del idioma, solo el contenido de los tiles. Detalle técnico
completo (formato exacto de la cell-entry del NCER, el bug encontrado al calcular
offsets de bloque, etc.) en `claude/investigacion-items-graficos.md`.

La traducción al inglés de los 38 ítems se hizo en otro chat/cuenta (siguiendo un
doc de traspaso, `handoff-traduccion-items-eng.md`) en paralelo a este trabajo de
extensión del NCER; ambos se integraron al terminar. ROMs `Twilight Syndrome -
ESP.nds` y `Twilight Syndrome - ENG.nds` regeneradas 2026-09-08 con los 38 ítems
completos en cada una.

**Reorganización de scripts:** todos los scripts de Python del proyecto excepto
`generar_rom_esp.py`/`generar_rom_eng.py` se movieron de la raíz a `scripts/`
(que ya existía desde el día 1 del proyecto, con `extraer_texto.py`). Los
scripts siguen usando rutas relativas a la raíz del proyecto, así que hay que
correrlos desde ahí: `python3 scripts/nombre.py`, no desde dentro de `scripts/`.
También se agregó un resumen (`Graficos: N/N aplicados`) al final de
`generar_rom_esp.py`/`generar_rom_eng.py` para no tener que contar líneas de
consola a mano.

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
  **Importante: esto es un límite del script de inventario, de solo lectura
  — no se editó ni se tocó ningún archivo de LOGO/TITLE/MBP, solo se intentó
  generar una vista previa de esos gráficos y el decoder no logra dibujar el
  100% del tile.**
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

## 2026-09-11/12 — Bug de freeze en mensaje corto ("puerta con llave"): investigado a fondo, SIN resolver

**Sintoma:** en la puerta de la enfermeria (evento en el ARM9, offset del
texto japones `0xd6084`, japones `鍵がかかってる。` = "esta con llave"), si
la traduccion al espanol tiene el mismo largo en caracteres que el japones
original (ej. `"Con llave......"`, padeado a 16 bytes) el juego queda
congelado de forma "blanda": no crashea, pero el dialogo nunca aparece en
pantalla y no se puede avanzar. Con una traduccion mas corta (`"Con
llave."`, 10 caracteres) funciona bien. La ROM en ingles tambien funciona
(su traduccion para esa linea es mas corta). Se probo tambien exactamente
16 bytes con contenido distinto (`"Esta con llave."`) en las otras 4
apariciones del mismo texto japones en el juego (offsets `0xd60d4`,
`0xd60fc`, `0xd6138`, `0xda63c`) - **sin confirmar si esas tambien se
cuelgan**, no se llego a probar antes de parar la investigacion.

**Lo que se descarto, con evidencia real (no son la causa):**
- Bug de overflow de buffer en la funcion que escribe caracteres uno por
  uno (`0x02011F74` en RAM, ver detalle tecnico abajo) - existe un bug real
  ahi (el puntero de escritura sigue avanzando aunque el espacio se agote y
  deje de escribir), pero se confirmo con logs reales que el buffer NUNCA
  llega a agotarse en este caso especifico (capacidad minima observada: 16
  de un buffer de 32/128/256, nunca 0). No es la causa de este freeze en
  particular (aunque sigue siendo un bug real del motor, dormante).
- Que el juego nunca intente mostrar el mensaje: FALSO, se confirmo con
  logs que la funcion motora (`0x02012050`) y la de escribir caracter
  (`0x02011F74`) SI se llaman, las 16 veces esperadas (una por caracter de
  "Con llave......"), y la funcion termina y retorna limpio en todos los
  niveles rastreados (incluyendo la funcion especifica que llama al mensaje
  de la puerta, en `0x02040E48`).
- Teorias de "es un tipo de mensaje distinto (sistema vs dialogo)", "el
  problema es la cantidad de caracteres vs. el japones", "flag1 determina
  el comportamiento": ninguna se pudo confirmar ni descartar del todo con
  evidencia solida - quedan como hipotesis sueltas, no conclusiones.

**Conclusion real a la que se llego:** el texto se escribe COMPLETO y
CORRECTO en el buffer de RAM (confirmado leyendo el contenido real
caracter por caracter con un hook de memoria), pero **nunca se dibuja en
pantalla**. Esto apunta a que el bug esta en la rutina de renderizado/copia
a VRAM (que corre aparte, probablemente una vez por cuadro, no como parte
directa de la cadena que llena el texto) - un area del codigo que NO se
llego a investigar todavia.

**Cadena de llamadas mapeada (util para retomar esto, direcciones RAM en
el arm9.bin pristino):**
```
evento puerta (0x02040E48, bl)
  -> 0x02018894 (armado generico de argumentos con flag1/flag2 del
     struct de puntero - funcion usada desde ~150 lugares del juego,
     no sirve para identificar el evento por si sola)
  -> 0x02006168 (trampolin: salta a 0x02012050 via literal en el pool)
  -> 0x02012050 (motor tipo printf: parsea %, flags, ancho, precision,
     %d/%s/%c - para texto sin '%' solo hace scan simple)
  -> 0x02011F74 (escribe UN caracter: struct en r0 = {espacio_restante,
     puntero_escritura} - BUG REAL encontrado aca, ver arriba, pero no es
     la causa de este freeze)
```
Return limpio confirmado en todos los niveles hasta 0x02040E7C.

**Herramientas y tecnica que SI funcionaron (usar de base si se retoma):**
- `Test/active_buffer_watch.lua`: hookea escrituras al buffer de texto fijo
  del motor (`0x0212DB2C`, documentado en plan-tecnico.md) - direccion
  ESTABLE que no depende de donde se reubico el string traducido (a
  diferencia de intentos anteriores con la direccion del string, que
  fallaban porque esa direccion cambia cada vez que se edita el CSV antes
  de esa linea). Con esto se puede reconstruir el texto real caracter por
  caracter (¡usar el mapeo de bytes de `generar_rom_esp.py`, NO ascii
  plano, para decodificar! los bytes son 0xA1+indice para letras).
- `Test/call_watch.lua` y `Test/caller_watch.lua`: hookear ejecucion de una
  direccion de codigo puntual (no un rango ancho) y leer registros
  (`memory.getregister("r0")`, `"r14"` para LR - "lr" solo no funciona en
  esta build, hay que probar "r14" primero) es confiable. Leer el registro
  LR en la entrada de una funcion generica identifica exactamente CUAL
  llamador la invoco, sin tener que buscar entre decenas de candidatos.
- **Evitar rangos anchos de `memory.registerexec`** (ej. 64KB): agarran
  codigo no relacionado que se ejecuta todo el tiempo (se encontro un
  "loop" que en realidad era un contador/timer de animacion ejecutandose
  una vez por cuadro, sin relacion con el bug) y saturan el log sin dar
  señal util. Mejor apuntar a direcciones puntuales de a una.
- Los save states del usuario (en `Test/`) permiten probar cambios sin
  rejugar el replay completo desde el principio - usarlos desde el
  principio la proxima vez, no solo cuando ya se perdio mucha paciencia.

**Parche practico vigente (no es un arreglo real):** la linea del CSV en
`0xd6084` usa `"Con llave."` (10 caracteres), confirmado que funciona. No
se sabe el limite exacto ni si aplica a otras lineas - es prudencia, no
garantia.

## 2026-09-12 — Continuacion de la investigacion del freeze: reencuadre completo, sin resolver aun

Sesion larga (nocturna) de seguimiento a lo de arriba, usando la build de
debug (`Twilight Syndrome - ESP - DEBUG.nds`, generada por
`generar_rom_esp_debug.py` desde
`assets/csv/backups/guion_principal_esp_20260911_131333.csv`, que tiene
`"Esta con llave."` = 15 caracteres/bytes para offset `0xd6084`) mas save
states en `Test/` cerca de la puerta. **Confirmado por el usuario: el bug
es 100% reproducible siempre, tanto jugando en vivo como con la misma
secuencia via replay - no es sensible a timing de input.**

### Hallazgo principal: NO es un cuelgue de CPU

Se penso durante buena parte de esta sesion que era un cuelgue real de CPU
(instruccion trabada), pero el usuario aclaro el sintoma real: el
personaje llega a la puerta, se reproduce la animacion de "tirar de la
puerta", **la animacion nunca termina** (se repite en bucle) y el cuadro
"esta cerrada" nunca aparece. El juego sigue corriendo a 60fps con
total normalidad (confirmado con `Test/instr_trace6.lua` y sucesores: el
frame counter sigue avanzando, un rango de codigo vigilado simplemente
deja de recibir ejecuciones porque el flujo del juego esta en OTRA parte
del codigo, no porque la CPU este atascada). Esto invalida cualquier
conclusion anterior de "se cuelga en la instruccion X" - esas eran
simplemente el ultimo punto que un hook de rango angosto alcanzaba a ver
antes de que el juego siguiera por otro lado.

### Cadena de causalidad confirmada (con comparacion directa ROM buena vs
ROM debug, mismo save state, mismo punto)

1. El mensaje anterior al de la puerta (el de la enfermeria) se procesa
   **identico** en ambas ROMs: mismo puntero de texto (`0x0215BDE0`),
   misma secuencia de ejecucion.
2. Ese mensaje **SI llega a terminar correctamente** en ambas ROMs: el
   flag de "mensaje terminado" en el widget de dialogo activo
   (direccion estable `0x0212C668 + 0x549`) pasa a `1` en ambos casos,
   confirmado con `Test/flag549_watch.lua` (hook de escritura en esa
   direccion exacta).
3. Sin embargo, el evento que deberia arrancar el mensaje de la puerta
   (confirmado que pasa por una funcion "arrancadora" en `0x0203E664`,
   que setea el campo de estado del widget `[self+0x558]=2` y dispara
   todo el flujo de mostrar el mensaje) **nunca se vuelve a ejecutar** en
   la ROM debug (confirmado con `Test/dispatch_watch.lua`: se ve 1 sola
   vez en debug vs 3 veces en la ROM buena, para los 3 mensajes de la
   secuencia).
4. El motor del juego resulto ser un **interprete de bytecode/script de
   escena** (una tabla de ~90 punteros a manejadores en
   `0x02028A00-0x02028B60`, cada "opcode" de tamano variable, leido
   secuencialmente por un puntero que avanza por una zona de RAM
   alrededor de `0x02086Cxx` en las pruebas hechas). Confirmado con
   `Test/eventid2_watch.lua`: **la secuencia de opcodes ejecutados es
   IDENTICA en ambas ROMs hasta un punto exacto** (mismos IDs: 11, 11,
   11, 11, 14, y una entrada de "relleno"/padding en la posicion 6) - la
   ROM buena sigue avanzando el script despues de ese punto (3+ opcodes
   mas, IDs 14, 12, 11...), la ROM debug se detiene ahi para siempre y no
   vuelve a tocar esa zona de codigo.
5. **No confirmado todavia:** cual opcode exacto es el que no logra
   avanzar, ni por que su condicion de avance depende del largo del
   texto. La hipotesis mas fuerte (no verificada): el opcode que "espera
   a que el mensaje actual termine de mostrarse" usa alguna cuenta de
   "lineas/paginas" o "ancho" del texto (ver el bug de raiz mas abajo)
   para decidir cuando esta listo, y ese calculo sale mal para textos
   largos en la codificacion custom.

### Pista de fondo, aun sin confirmar como causa directa pero muy
plausible dado todo lo demas encontrado

La funcion que mide el ancho de un texto para layout (`0x02040E80`,
clasificador de "cuantos bytes ocupa este caracter") esta escrita
asumiendo Shift-JIS real: un byte en rango `0x81-0x9F` o `0xE0-0xEF` se
trata como el primer byte de un caracter de 2 bytes (1 "unidad de ancho"
por cada 2 bytes consumidos). La codificacion custom del proyecto
(`BYTE_MAP` en `generar_rom_esp.py`, letras en `0xA1-0xDF`) queda FUERA de
ese rango a proposito (para evitar que el motor se coma la letra
siguiente, bug ya documentado y corregido en 2026-09-08) - pero eso
significa que el motor cuenta CADA byte latino como su propia unidad de
ancho completa. Resultado: para el MISMO largo en bytes (16), el japones
original cuenta ~8 unidades de ancho pero la traduccion en espanol cuenta
~15-16 unidades - casi el doble. Si algun limite/calculo aguas arriba
(candidato: el opcode del script que "espera el mensaje", o el conteo de
paginas via `strstr` que se encontro en `0x0203E75C` pero que no se logro
confirmar en ejecucion para este caso especifico) esta dimensionado para
la mitad de unidades (porque nunca hizo falta mas para japones), un texto
latino del mismo largo en bytes podria desbordarlo silenciosamente sin
tocar el tamano visual del cuadro (el cuadro es de tamano fijo, esto no
es una teoria de "la caja necesita ser mas ancha" - es sobre un contador
interno que se confunde, no sobre el layout visual).

### Herramientas/tecnicas que funcionaron bien esta sesion (usar de base
al retomar)

- **Comparacion directa ROM buena vs ROM debug en el mismo punto exacto**
  fue, por lejos, la tecnica mas productiva de toda la sesion (idea del
  usuario). Siempre correr el MISMO script Lua contra ambas ROMs y diffear
  los logs (por PC ejecutado, ignorando columnas de frame/registros que
  varian por ruido de timing) en vez de analizar una sola corrida aislada.
- **Disparadores por CONTENIDO, no por direccion de memoria:** las
  direcciones de buffers/structs se reutilizan para cualquier mensaje;
  comparar los bytes reales del texto conocido (`BYTE_MAP` de
  `generar_rom_esp.py`) en el puntero es mucho mas confiable que asumir
  que una direccion fija siempre corresponde al mismo mensaje.
- **Escalado en 2 etapas** (hook angosto y barato corriendo todo el
  tiempo -> al llegar a un disparador conocido, activar un hook mas ancho
  solo desde ahi) evita la lentitud severa de vigilar rangos grandes
  desde el arranque, y evita que el usuario tenga que adivinar el
  instante exacto de pausar manualmente.
- **Auto-disparo por escritura a un flag conocido** (`registerwrite` en
  vez de pedirle al usuario que pause en un instante impreciso) es mucho
  mas confiable que pedir "avisame cuando se trabe" - la transicion
  animacion-a-dialogo es demasiado rapida para que una persona reaccione
  a tiempo.
- Direcciones estables confirmadas entre sesiones (reusar sin
  reverificar): widget de dialogo activo `0x0212C668` y `0x0212C638`
  (objeto de interaccion/animacion, distinto del widget de texto),
  campo "mensaje terminado" en offset `+0x549`, campo "estado principal"
  en `+0x558`, campo "flags de evento entrante" en `+0x24` del objeto de
  interaccion.
- **Evitar registrar EXEC en rangos de mas de ~8-16KB sin gate**: mas
  alla de eso el emulador se vuelve notablemente mas lento y desincroniza
  la nocion de "cuanto tiempo real corresponde a cuantos frames", lo que
  genera falsos positivos de "se congelo" cuando en realidad solo iba
  lento. Siempre confirmar con `wc -l` + esperar unos segundos reales
  que el archivo genuinamente dejo de crecer antes de concluir que algo
  esta atascado.

### Siguiente paso concreto para retomar

Diferenciar `[r6+0]` (opcode) de `[r6+2]` (parametro) en cada paso del
interprete de bytecode (`0x02028A00` en adelante) - el script anterior
(`Test/eventid2_watch.lua`) solo capturo `[r6+2]` sin saber que opcode
estaba activo en cada punto, lo cual probablemente llevo a una lectura
erronea justo en el punto de divergencia (la entrada "de relleno" en la
posicion 6 de la secuencia). Con eso identificado, desensamblar el
manejador de ESE opcode especifico (los ~90 manejadores estan listados en
la tabla de saltos en `0x02028A00-0x02028B60`, cada entrada de 4 bytes
= `b <direccion>`) deberia mostrar la condicion exacta que nunca se
cumple.

## 2026-09-12 (continuacion) — CAUSA RAIZ ENCONTRADA Y CORREGIDA: bug real en `find_pointer_locations`, no en el motor del juego

Siguiendo el hilo de arriba hasta el final: el despachador maestro real
del interprete de bytecode esta en `0x02028974`
(`ldrb r1,[r6,#1]; cmp r1,#0x79; addls pc,pc,r1,lsl#2` - el opcode real es
el byte en `[r6+1]`, no `[r6]`; la tabla de saltos empieza en `0x02028980`).
Vigilando esa instruccion directamente (`Test/maindispatch_watch.lua`) se
confirmo que el interprete se queda trabado procesando para siempre el
mismo **opcode tipo 1** en la posicion exacta `0x02086C44`.

El manejador del opcode tipo 1 (`0x02028B64`) lee un "ID de mensaje" de 2
bytes (`ldrh r2,[r6,#2]`), lo multiplica por 12 y lo usa como indice en
la tabla de punteros `{pointer:u32, flag1:u32, flag2:u32}` para buscar el
mensaje a mostrar (`bl 0x202a684`). Si esa busqueda no encuentra un
resultado "listo", el interprete reintenta el MISMO opcode en el
siguiente frame, para siempre, sin avanzar nunca al opcode que arranca el
mensaje de la puerta.

**La causa real:** en el arm9.bin pristino (japones, sin ninguna
traduccion), esa posicion exacta tiene los bytes `00 00 10 02` - el ID de
mensaje real es `0x0000` (un indice valido y normal), y los siguientes 2
bytes (`10 02`) son simplemente el inicio de la SIGUIENTE instruccion del
guion (que no tiene nada que ver). Pero esos mismos 4 bytes, leidos como
un numero de 32 bits, forman exactamente `0x02100000` - que es tambien,
por pura coincidencia, la direccion RAM original del texto japones de
OTRA linea de dialogo totalmente distinta ("Que?", CSV offset `0x100000`).

`find_pointer_locations()` en `generar_rom_esp.py` busca ese patron de 4
bytes en TODO el arm9.bin para saber donde "repointear" el puntero de esa
linea a su nueva ubicacion traducida - y lo encuentra en **10 lugares
distintos**, pero **solo 1 de esos 10 es realmente la entrada de tabla de
"Que?"** (confirmado por su forma: `flag1` con la mitad alta `0x0002` y
`flag2=0`, patron consistente en las ~15 filas del CSV con multiples
coincidencias). **Los otros 9 son coincidencias accidentales dentro de
datos de guion de OTRAS 9 escenas** (cada una con su propio opcode tipo 1
apuntando, por diseño original del juego, a un simple "ID=0" que
accidentalmente comparte los mismos 4 bytes que el puntero de "Que?").

Antes del fix, el script repointeaba las 10 coincidencias por igual,
sobreescribiendo el ID=0 legitimo de esas 9 escenas con la nueva direccion
reubicada de "Que?" (un numero de 5 cifras, ej. `0x6C34`). Eso rompe el
lookup del opcode tipo 1 en ESAS escenas especificamente - una de ellas
resulta ser la escena de la puerta con llave de la enfermeria.

**Por que dependia del largo del texto traducido:** la direccion final
donde queda reubicado el texto de "Que?" depende de cuanto espacio ocupen
TODAS las traducciones anteriores en el archivo (el cursor de escritura
es acumulativo). Cambiar el largo de CUALQUIER linea anterior en el CSV
- incluida esta misma linea de la puerta - desplaza esa direccion, lo
cual cambia el numero exacto que termina sobreescribiendo el ID=0 de las
escenas afectadas. Si por pura casualidad ese numero, multiplicado por 12
y usado como indice, cae en un lugar de memoria que el juego interpreta
como "listo" (aunque sea basura), el bug no se manifiesta. No es una
regla de "el texto no puede ser mas largo que el japones" - es una
loteria de memoria causada por un bug real en nuestra herramienta de
parcheo, disparada indirectamente por cualquier cambio de longitud en el
CSV.

**El fix** (aplicado en `generar_rom_esp.py`, `generar_rom_esp_debug.py`
y `generar_rom_eng.py`, funcion nueva `filter_legit_pointer_locations`):
cuando `find_pointer_locations` encuentra mas de 1 coincidencia para un
mismo offset, se queda solo con las que tengan la forma real de una
entrada de tabla (`flag1` con mitad alta `0x0002`, `flag2=0`). Si
exactamente una coincidencia cumple ese patron, se usa solo esa. Si
ninguna o mas de una lo cumplen (caso ambiguo no verificado), no se
filtra nada - se repointean todas como antes y se imprime un aviso para
revision manual (no ocurrio ningun caso ambiguo al regenerar con el CSV
actual).

**Verificado:** se regenero `Twilight Syndrome - ESP - DEBUG.nds` (con el
CSV de respaldo que tiene `"Esta con llave."`, 15 caracteres, el texto
que siempre causaba el freeze) usando el script ya corregido, y el bug
**desaparecio por completo** jugando desde el replay desde el inicio (no
sirve reutilizar un save state hecho con la ROM vieja - el save state
contiene una foto de la RAM ya cargada con los datos corruptos de la ROM
anterior, hace falta que la escena se cargue de nuevo desde el arm9.bin
corregido).

**Cambios en el CSV de produccion:** se restauro `"Esta con llave."`
(el texto largo original, igual de largo que el japones) en las 5
apariciones de `鍵がかかってる。` (offsets `0xd6084`, `0xd60d4`, `0xd60fc`,
`0xd6138`, `0xda63c`), reemplazando el parche temporal `"Con llave."` que
se habia dejado como precaucion. El CSV en ingles ya tenia `"It's
locked."` (corto) en esas mismas lineas y no necesito cambios.

**Prueba de stress adicional:** se genero una ROM aparte (no para
distribuir, solo para validar) con un texto deliberadamente mas largo
todavia para esta linea, confirmando que el motor ahora tolera cualquier
largo razonable sin trabarse.

### 2026-09-12 (otra sesión, continuación 2) — Las 7 tarjetas de `TITLE/G02M10` terminadas y verificadas en juego real, en español e inglés

**Validación en melonDS confirmó dos problemas de la primera versión, corregidos:**
1. El texto salía corrido hacia la derecha/abajo respecto al centro de la
   pantalla. Causa: los objetos nuevos se armaron con `rot_scale=1` +
   `double_size=1` (copiando el modo del original), y ese modo dibuja el
   contenido centrado dentro de una caja del DOBLE de tamaño que la nominal
   — es decir, el contenido real queda desplazado +32,+32 respecto a las
   coordenadas x,y que uno define. Se corrigió restando ese offset de
   entrada: la esquina del bloque de 256x128 pasó de `x0,y0=(-128,-64)` a
   `x0,y0=(-160,-96)`.
2. La tipografía era demasiado grande para el espacio disponible (la línea
   "El rumor inicial" llegaba casi al borde de la caja). Se achicó el
   tamaño de fuente y se agregó más margen vertical/horizontal.

Confirmado por el usuario jugando la ROM real (melonDS) después del ajuste:
"ahora se ve bien".

**Con la técnica ya validada, se generaron las 6 tarjetas restantes** (mismo
procedimiento de extensión de celda que la primera, compartiendo tiles entre
la celda normal y la seleccionada) reusando el texto ya definido en
`scripts/traducir_saveload.py`:

| Celda | Arco (JP) | ES | EN |
|---|---|---|---|
| 0 | 旧校舎のコックリさん / はじまりの噂 | El Kokkuri-san del edificio viejo / El rumor inicial | The Kokkuri-san of the Old Building / The Beginning Rumor |
| 1 | 神隠しメール | Mail de desaparición / El primer rumor | Vanishing Mail / The First Rumor |
| 2 | 幻のホーム | El andén fantasma / El segundo rumor | The Phantom Platform / The Second Rumor |
| 3 | ひとりかくれんぼ | Hitori Kakurenbo / El tercer rumor | Hitori Kakurenbo / The Third Rumor |
| 4 | こわいテーマパーク | El parque de diversiones de terror / El cuarto rumor | The Scary Theme Park / The Fourth Rumor |
| 5 | 都市伝説百物語 | Las cien leyendas urbanas / El quinto rumor | The Hundred Urban Legends / The Fifth Rumor |
| 6 | 最期の噂 / 心霊写真 | Foto paranormal / El último rumor | Psychic Photograph / The Final Rumor |

(la celda 6 en japonés se confirmó por render directo: decía 心霊写真, no
"心霊写...呉" como se había transcripto a ojo en la entrada anterior — 呉 no
existe, era una lectura equivocada de un tile pequeño de apoyo.)

**Se hizo lo mismo para inglés** (`assets/graficos/eng/TITLE/`), con el
mismo ajuste de posición/tamaño ya validado, sin tener que repetir la
verificación en juego (mismo archivo, mismo mecanismo, solo cambia el
texto).

**Archivos finales entregados y ya copiados directamente al proyecto del
usuario vía el bridge de dispositivo conectado** (esta sesión tenía la PC
del usuario conectada, así que se escribieron directo, no quedaron solo
como descarga):
- `assets/graficos/esp/TITLE/G02M10.NCGR` + `.NCER`
- `assets/graficos/eng/TITLE/G02M10.NCGR` + `.NCER`

El pipeline automático de `generar_rom_esp.py`/`generar_rom_eng.py` (el que
recorre `assets/graficos/<idioma>/` recursivamente) los toma solos, sin
tocar `GRAPHICS_PATCHES`. **Falta que el usuario genere ambas ROMs y
verifique las 6 tarjetas nuevas en juego** (solo la primera fue confirmada
visualmente en melonDS; las otras 6 comparten técnica y no deberían tener
sorpresas, pero no están confirmadas una por una todavía).

**Detalle técnico para la próxima vez que haga falta extender una celda de
`G02M10` (o un NCER parecido) con `tileBoundaryCode>0` y modo
rotate/scale+double-size:**
- El offset de bytes de un tile es `tile_idx_ya_shifteado * 32` (unidad base
  fija de 32 bytes), NUNCA `tile_idx * tile_bytes_del_bpp` — ver hallazgo de
  la entrada anterior de esta sesión (más abajo en este mismo doc / en el
  chat original si no está también acá).
- Si se copia el modo `rot_scale=1`+`double_size=1` del objeto original (por
  las dudas, para no romper el parámetro de matriz de afinidad que pueda
  estar seteado en runtime), hay que restar la mitad del ancho/alto del
  bloque nuevo a las coordenadas x,y de diseño para que el resultado
  aparezca centrado donde uno espera — si no, sale desplazado +mitad del
  tamaño hacia abajo/derecha.
- Cuando una celda comparte tiles entre dos variantes de color (normal /
  seleccionada) solo hace falta generar los píxeles UNA vez — las dos celdas
  apuntan al mismo rango de tiles, solo cambia el campo `palette` de cada
  OBJ (y el motor del juego decide en tiempo de ejecución qué banco de
  paleta real corresponde a cada valor de `palette`, algo que no hace falta
  entender para redibujar, solo para elegir qué banco mirar al armar la
  vista previa).

**Fuente y estilo usados en `TITLE/G02M10` (para replicar exacto si hay que
corregir una tarjeta o agregar una que falte):**
- Texto renderizado con PIL (`ImageDraw` + `ImageFont.truetype` +
  `ImageFilter.GaussianBlur`) sobre un canvas `L` (escala de grises) de
  256x128px por tarjeta (grilla de 4x2 tiles de 64x64px).
- **Fuente usada en esta sesión: DejaVu Sans Bold** (`DejaVuSans-Bold.ttf`,
  la que trae instalada el entorno de nube donde se hizo el render).
  ⚠️ **Discrepancia a tener en cuenta:** `scripts/traducir_saveload.py`
  (SAVELOAD/S00-S06, el texto que se reusó acá) usa fuentes de Windows —
  `C:/Windows/Fonts/segoeuib.ttf` o, si no está, `arialbd.ttf` — NO DejaVu.
  Es decir, las tarjetas de `G02M10` quedaron con una tipografía
  ligeramente distinta a las de `SAVELOAD` aunque el texto sea el mismo.
  No debería notarse mucho a esta resolución (son todas sans-serif bold),
  pero si se nota un desajuste de estilo entre ambas pantallas en el juego,
  esta es la causa. Para una corrección futura 100% consistente con
  `SAVELOAD`, regenerar usando `segoeuib.ttf`/`arialbd.ttf` (correr en una
  máquina Windows, o subir esas fuentes al entorno de render) en vez de
  DejaVu.
- **Tamaños:** título en una sola línea, tamaño inicial 20pt, con
  auto-reducción hasta un mínimo de 12pt si no entra en `ancho_canvas-28`px;
  si no entra ni a 13pt, se parte en dos líneas (cortando por la palabra más
  cercana a la mitad del texto), cada mitad a tamaño inicial 18pt con mínimo
  10pt, centradas en y=14 e y=38. La línea de "El N-ésimo rumor" siempre va
  en una sola línea, tamaño inicial 20pt con mínimo 11pt, centrada en y=92.
  Ancho máximo de texto: 228px (256-28).
- **Efecto glow:** se dibuja el texto "core" en gris claro (fill=255) con
  antialiasing normal de PIL, se aplica `GaussianBlur(radius≈1.2)` a una
  copia, y se combina tomando el máximo por píxel entre el blur y el core
  nítido (mismo criterio que `render_glow()` de `traducir_saveload.py` pero
  con radio distinto: acá 1.2, SAVELOAD usa 1.6).
- **Color:** los valores de gris (0-255) se cuantizan a índices de paleta
  1-15 con `indice = 1 + round((valor/255)*14)` (0 queda reservado como
  transparente). El color real en pantalla lo decide el juego en runtime
  (no el archivo), pero para las vistas previas/verificación se usó el
  **banco 2** de `TITLE/G02M10.NCLR` (gradiente rojo oscuro→rojo brillante
  puro, sin blancos ni grises — confirmado pixel a pixel contra una captura
  real del usuario). El banco 0 del mismo archivo tiene un gradiente
  rojo→BLANCO que NO corresponde a esta pantalla — fue una confusión inicial
  de esta sesión (ver el bug de abajo).

**Bug encontrado y corregido esta sesión — banco de paleta incorrecto:**
El primer render de la celda 0 usó el banco 0 de `G02M10.NCLR` (rojo→blanco),
lo que dio un resultado con núcleo blanco que el usuario señaló que no
coincidía con su captura real ("NI LA TIPOGRAFIA NI EL COLOR DE LA LETRA
COINCIDE"). Se hizo un análisis pixel a pixel de la captura real del usuario
(color más brillante encontrado: RGB `(203,32,48)`, sin blanco en ningún
punto) y se comparó contra los 8 bancos de paleta del archivo — el banco 2
(rojo puro, sin blanco) fue el que coincidió. El campo `palette` de los OBJ
de esta celda declara `palette=0` en los atributos OAM, pero el color real
mostrado en pantalla viene del banco 2 — el mecanismo exacto por el cual el
juego selecciona ese banco en runtime no se identificó (no hace falta para
redibujar, solo importa el contenido de los tiles).

### Pendiente (actualizado)

1. **Generar `Twilight Syndrome - ESP.nds` y `Twilight Syndrome - ENG.nds`**
   y confirmar en juego las 6 tarjetas nuevas de `TITLE/G02M10` (solo la
   primera fue probada en melonDS).
2. **`TITLE/G01M10`** — menú principal de la pantalla de título, todavía sin
   texto en español/inglés decidido.
3. Confirmar el banco de paleta real del estado "seleccionado" de
   `G02M10` (se usó el banco 1 sin verificar contra una captura real del
   juego).
4. Portar el fix del decoder NCER (offset de tile = `tile_idx*32`, no
   `tile_idx*tile_bytes`; soporte de paletas multi-banco) a
   `scripts/ncer_decode.py`/`scripts/inventario_completo.py` del repo real.
5. Si se quiere consistencia tipográfica perfecta entre `G02M10` y
   `SAVELOAD`, regenerar los renders de `G02M10` con `segoeuib.ttf`/
   `arialbd.ttf` en vez de DejaVu Sans Bold (ver nota de fuente arriba) — no
   se hizo en esta sesión porque el entorno de render no tenía esas fuentes
   de Windows disponibles.

### 2026-09-12 (misma sesión, continuación 3) — `TITLE/G01M10` (menú principal): layout confirmado contra captura real del usuario

Se decodificó celda por celda el NCER completo de `TITLE/G01M10` (28 celdas)
y luego el usuario confirmó el resultado con dos capturas reales de melonDS
(pantalla principal y submenú de galería). **Coincide exactamente** con lo
decodificado — queda confirmado dónde aparece cada texto y el criterio de
color de estado:

**Pantalla principal (debajo del logo/copyright):**
- `シナリオをえらぶ` — "Elegir escenario" (equivalente a Nueva Partida)
- `つづきから` — "Continuar"
- `鑑賞` (dos celdas separadas, una por kanji: 鑑 + 賞) — "Ver/Apreciar",
  lleva al submenú de galería. Confirmado por captura real que el juego
  arma esta palabra pegando dos objetos de un solo kanji cada uno.

**Submenú de galería (al elegir 鑑賞):**
- `写真一覧` — "Lista/Galería de fotos"
- `音声一覧` — "Lista/Galería de sonidos"
- `結末一覧` — "Lista de finales"
- `戻る` (abajo a la derecha) — "Volver"

**Criterio de color confirmado (al revés de lo que se había asumido sin
verificar):** la opción con el cursor encima (resaltada) se dibuja en
**naranja/amarillo**, las opciones normales en **cian**. En la captura del
submenú, `写真一覧` aparece en naranja (primera opción, cursor por defecto)
y el resto en cian.

**Mapeo a celdas del NCER** (`decode_ncer` sobre `G01M10.NCER`, 28 celdas
totales, cada celda 1 objeto salvo un grupo de celdas de 4 objetos):
- Celdas 0-10: el cartel "画面をタッチしてください" (Toque la pantalla),
  un kanji/kana por celda — pantalla de arranque previa al menú, no
  fotografiada todavía por el usuario en esta sesión.
- Celda 11: `戻る` variante suelta.
- Celdas 12-18 y 19-25 (dos bloques de 7): mismo contenido en dos paletas
  distintas — probablemente normal vs. resaltado para cada opción del
  submenú de galería (`鑑`+`賞` como 2 celdas, `写真一覧`, `音声一覧`,
  `結末一覧`, `戻る`).
- Celda 26: `つづきから` en gris — variante "sin partida guardada"
  (deshabilitado), no confirmada aún en juego.
- Celda 27: una pequeña flecha/marca "下" (abajo), función exacta no
  confirmada.

Sigue sin decidirse la traducción — esto solo documenta dónde aparece y qué
dice cada texto, para cuando el usuario decida si vale la pena traducirlo.

### 2026-09-12 (misma sesión, continuación 4) — `TITLE/G01M10` (menú principal): traducido completo en ESP/ENG y verificado en juego

Con el layout ya confirmado contra las capturas reales del usuario (ver
entrada anterior), se tradujeron las 7 etiquetas del menú y se verificaron
en melonDS, en español e inglés:

| Celda(s) NCER | Japonés | ES final | EN final |
|---|---|---|---|
| 12/19 | シナリオをえらぶ | Elegir escenario | Choose Scenario |
| 13/20/26(gris) | つづきから | Continuar | Continue |
| 14/21 | 鑑賞 | Galería | Gallery |
| 15/22 | 写真一覧 | Fotos | Photos |
| 16/23 | 音声一覧 | Sonidos | Sounds |
| 17/24 | 結末一覧 | Finales | Endings |
| 11/18/25 | 戻る | Volver | Back |

**Confirmado en juego por el usuario:** "ahora se ve bien" tras dos rondas
de ajuste (ver bugs abajo).

**Diferencia clave con el redibujado de `G02M10` — mucho más simple, no
hizo falta tocar el `.NCER` para nada:**
- Cada etiqueta de este menú YA tenía tiles fijos de sobra para texto latino
  (el japonés original ocupaba menos espacio del disponible), así que solo
  se sobrescribió el contenido de los tiles existentes — sin extender el
  NCGR ni tocar el NCER en absoluto.
- El bloque de cada opción de la fila central (シナリオをえらぶ, つづきから,
  鑑賞, 写真一覧, 音声一覧, 結末一覧) es un canvas de **144x64px**, armado
  con 4 objetos NCER: dos de 64x64 + dos de 16x32 (posiciones fijas,
  documentadas en el script). `戻る` es un solo objeto de **64x32px**.
- **El estado normal (cian) y resaltado (naranja) usan LOS MISMOS
  `tile_idx`** — solo cambia el campo `palette` del objeto (0=normal,
  1=resaltado) y, para la fila central, además usan geometría con
  `rot_scale`+`double_size` en el estado resaltado (mismo mecanismo de
  offset que `G02M10`, pero acá no hubo que tocarlo porque no se cambiaron
  coordenadas, solo el contenido de los tiles). **Confirmado en este NCLR
  que el campo `palette` del OBJ SÍ corresponde directo al banco real**
  (banco 0 = cian `(200,224,224)`, banco 1 = naranja `(168,168,80)`,
  verificado pixel a pixel contra captura real) — a diferencia de
  `G02M10`, donde el campo `palette` NO correspondía al banco real. Cada
  NCGR puede comportarse distinto en esto, no asumir un caso a partir del
  otro.
- `つづikara`/Continuar tiene además una **tercera variante gris** (celda
  26, banco de paleta 2) para el estado "sin partida guardada" —
  comparte los mismos `tile_idx` que la celda 13, así que se tradujo sola al
  traducir esa etiqueta, sin trabajo extra.
- **La celda mide 144x64px pero tiene grano/textura de fondo horneado
  DENTRO del mismo bloque de tiles** (a diferencia de `G02M10`, donde el
  fondo era una capa aparte detrás del NCER) — la paleta de este NCGR usa
  índice 0=transparente, 1=texto núcleo, 2-3=halo del texto, **4-15=el
  degradé rojo del grano decorativo**. Técnica usada (igual principio que
  `traducir_saveload.py` pero aplicada tile a tile en vez de por columnas):
  se leen los píxeles actuales, se **borran a transparente los que sean
  índice 1/2/3** (el glifo japonés viejo) y se preserva todo lo demás
  (índices 4-15, el grano) sin tocarlo; después se dibuja el texto nuevo
  encima, también solo en índices 1/2/3.

**Bug 1 — corte por el borde real de la pantalla en `戻る`:** el primer
intento centró "Volver" dentro del bloque completo de 64px, igual que se
había hecho con los textos centrados de la fila de arriba. Pero este botón
en particular está anclado muy cerca del borde derecho FÍSICO de la
pantalla de la NDS (unos 15-20px del bloque de 64px caen fuera del área
visible de 256px de ancho) — el original "戻る" (32px de ancho real) entraba
justo, pero "Volver" centrado (57px) se extendía hacia esa zona invisible y
salía cortado ("Volve" + una "r" fuera de cuadro). **Fix:** en vez de
centrar, el texto de esta celda puntual se alinea a la **izquierda** con
margen de 3px y límite duro de ancho hasta x=50 dentro del bloque de 64px
(el original llegaba hasta x=47) — nunca centrar un texto reemplazo sin
antes confirmar cuánto del bloque es realmente visible en pantalla,
sobre todo en elementos ubicados cerca de un borde. Las opciones de la fila
central (más al centro de la pantalla) no tuvieron este problema.

**Bug 2 — tamaño de fuente inconsistente entre etiquetas:** al auto-ajustar
el tamaño de fuente de forma independiente por etiqueta (achicando solo
hasta que el texto entre en su propio ancho disponible), las palabras más
cortas (Continuar, Galería, Fotos, Sonidos, Finales) quedaron visiblemente
más grandes que la más larga (Elegir escenario/Choose Scenario, que
necesitaba un tamaño menor para entrar). El usuario lo notó de inmediato en
la captura in-game. **Fix:** en vez de auto-ajustar cada etiqueta por
separado, se calculó el tamaño mínimo necesario para la etiqueta MÁS LARGA
del conjunto y ese mismo tamaño fijo se aplicó a las demás — **regla a
seguir siempre que se traduzca un conjunto de opciones de un mismo menú:
usar un tamaño de fuente único para todas, nunca auto-ajuste independiente
por ítem**, aunque signifique que las etiquetas cortas queden con más
margen vacío del que técnicamente necesitarían.

**Fuente y estilo usados en `TITLE/G01M10` (para replicar si hace falta
corregir o traducir alguna celda más de este mismo archivo, ej. el cartel
"画面をタッチしてください" de las celdas 0-10, todavía sin traducir):**
- Misma fuente que el resto de esta sesión: **DejaVu Sans Bold**
  (`DejaVuSans-Bold.ttf`) — con la misma discrepancia ya anotada respecto a
  `SAVELOAD` (que usa fuentes de Windows). Acá el estilo de letra es más
  "bloque"/pixelado por el bajo bitdepth (solo 3 niveles de gris para el
  texto: núcleo + 2 de halo), no el degradé suave de 15 niveles usado en
  `G02M10`.
- **Tamaño fijo, no auto-ajuste por ítem** (ver Bug 2): en español, 14pt
  para las 6 etiquetas de la fila central (calculado como el tamaño mínimo
  que necesita "Elegir escenario" para entrar en ~90% del ancho de 144px) y
  13pt para "Volver" (bloque de 64px, alineado a la izquierda, ver Bug 1);
  en inglés, 13pt para la fila central ("Choose Scenario" es la más larga)
  y 12pt para "Back".
- **Glow de 3 niveles** (no 15 como en `G02M10`, por el límite de paleta de
  este NCGR): se renderiza el texto núcleo en blanco puro (255) sobre negro,
  se aplica `GaussianBlur(radio 0.7 para "Volver"/"Back", 0.9 para las
  etiquetas centradas)`, y se cuantiza a 3 índices: núcleo (valor>128) →
  índice 1, halo medio (blur>60) → índice 2, halo tenue (blur>15) → índice
  3, resto → 0 (transparente, preserva el grano de fondo).
- **Color:** igual que siempre, el índice de paleta no fija el color — el
  banco de paleta sí importa acá (confirmado banco 0=cian, banco 1=naranja,
  banco 2=gris para "sin partida guardada"), pero es automático: no hace
  falta elegir nada al redibujar, el juego aplica el banco según el estado
  del botón.
- Archivos finales: `assets/graficos/esp/TITLE/G01M10.NCGR` y
  `assets/graficos/eng/TITLE/G01M10.NCGR` (sin `.NCER`, no se tocó).

### Pendiente (actualizado)

1. **Generar `Twilight Syndrome - ESP.nds` y `Twilight Syndrome - ENG.nds`**
   y confirmar en juego las 6 tarjetas nuevas de `TITLE/G02M10` (solo la
   primera fue probada en melonDS) — sigue pendiente, no relacionado a
   `G01M10`.
2. **`TITLE/G01M10` — cartel "画面をタッチしてください"** (celdas 0-10 del
   mismo NCER, la pantalla previa al menú, un kanji/kana por celda): todavía
   sin traducir, no se decidió si vale la pena (es solo un "toque la
   pantalla para continuar").
3. Confirmar el banco de paleta real del estado "seleccionado" de las
   tarjetas de `G02M10` (sigue sin verificar, no relacionado a `G01M10`).
4. Portar el fix del decoder NCER (offset de tile = `tile_idx*32`; soporte
   de paletas multi-banco) a `scripts/ncer_decode.py`/
   `scripts/inventario_completo.py` del repo real.
5. Si se quiere consistencia tipográfica perfecta entre estos gráficos y
   `SAVELOAD`, regenerar con `segoeuib.ttf`/`arialbd.ttf` en vez de DejaVu
   Sans Bold — no se hizo en esta sesión por no tener esas fuentes de
   Windows disponibles en el entorno de render.

### 2026-09-12 (misma sesión, continuación 5) — Fix del decoder NCER portado a `scripts/ncer_decode.py`

Se aplicaron directo al script real del repo los dos hallazgos de esta
sesión sobre el formato NCER:

1. **Offset de tile corregido en `render_tile()`:** ahora usa siempre
   `tile_idx*32` como base fija (más `n*tile_bytes` por cada tile
   siguiente), en vez de `tile_idx*tile_bytes`. El bug anterior rompía la
   posición de los tiles en cualquier NCER con `tileBoundaryCode>0` (como
   `TITLE/G02M10` y `TITLE/G01M10`) — no afectaba a los ítems del inventario
   porque esos usan `tileBoundaryCode=2` pero con objetos todos del mismo
   tamaño, donde el bug no se notaba tan fácil.
2. **Soporte para forzar un banco de paleta** vía el nuevo parámetro
   `force_palette_bank` de `compose_cell()` y el flag `--bank N` desde
   consola — para verificar rápido cuál banco corresponde al color real en
   pantalla cuando el campo `palette` del OBJ no coincide (caso real:
   `G02M10`).

**Verificado sin regresión:** se corrió contra `I00S10` (linterna, ya
validado en sesiones anteriores) y sigue decodificando igual de bien
("懐中電灯" legible, celdas de fondo intactas).

### 2026-09-12 (misma sesión, continuación 6) — Fix del decoder NCER portado también a `scripts/inventario_completo.py`

Mismo bug/fix que la entrada anterior, aplicado a `render_tile_block()` en
`scripts/inventario_completo.py` (el script de barrido exhaustivo de toda
la ROM, distinto del `ncer_decode.py` usado para ítems/gráficos
individuales): el offset de cada tile ahora usa `tile_idx*32 + n*tile_bytes`
en vez de `(tile_idx+n)*tile_bytes`. No se agregó `force_palette_bank`
acá (ese script es de solo lectura/inventario, no hace falta forzar
bancos para verificar una traducción). Verificado que el archivo sigue
compilando sin errores de sintaxis.

`inventario_graficos.py` (distinto de `inventario_completo.py`) NO se
tocó — no decodifica NCER, solo vuelca tiles NCGR en orden secuencial,
así que el bug no le aplicaba.

### 2026-09-12 (misma sesión, continuación 7) — Freeze de la puerta con llave: scripts subidos a GitHub, y sincronización completa del repo

Se subieron a `Secabel/twilight-syndrome` (rama `main`) todos los cambios
de esta sesión que todavía vivían solo en la PC del usuario:
`generar_rom_esp.py`/`generar_rom_eng.py` con el fix de
`filter_legit_pointer_locations`, `scripts/ncer_decode.py` y
`scripts/inventario_completo.py` con el fix de offset de tile, y este
mismo doc actualizado junto con el nuevo `docs/guia-debugging-bugs-dificiles.md`.
Los 6 archivos binarios nuevos (`TITLE/G02M10.NCGR`+`.NCER` y
`TITLE/G01M10.NCGR`, esp+eng) quedan para un commit aparte por su
naturaleza binaria — ver el resto de esta sesión para el detalle de cómo
se subieron.
