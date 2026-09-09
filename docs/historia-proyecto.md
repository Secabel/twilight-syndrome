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
