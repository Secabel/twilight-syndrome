# Traspaso: traducción al INGLÉS de los 38 gráficos de ítems del inventario — Twilight Syndrome: Kinjirareta Toshi Densetsu (NDS)

> Este documento es autocontenido. Está pensado para arrancar un chat nuevo (otra
> cuenta, por límite de tokens) y que continúe exactamente el mismo trabajo que ya
> se hizo para la versión en **español**, pero produciendo la versión en **inglés**
> de los mismos 38 gráficos. El resultado final debe ser indistinguible del build
> en español salvo por el idioma del texto: misma fuente, mismo tamaño, misma
> paleta, mismo layout de tiles, mismo pipeline de integración a la ROM.

## 0. Contexto del proyecto

Fan-translation de "Twilight Syndrome: Kinjirareta Toshi Densetsu" (Nintendo DS) al
español y al inglés, en paralelo, usando scripts propios en Python. El repo del
proyecto vive en la carpeta local `Twilight Syndrome Kinjirareta Toshi Densetsu`
(en Windows: `E:\Descargas\Parche\Twilight Syndrome Kinjirareta Toshi Densetsu`),
y ahí están todos los scripts y assets mencionados en este documento.

El proyecto tiene dos frentes de traducción de texto:

1. **El guion principal** (diálogos, menús, etc.) — vive en CSVs
   (`assets/csv/guion_principal_esp.csv` / `guion_principal_eng.csv`) y usa una
   fuente custom (`assets/font/TWSFont_v21.NFTR`) con un mapeo de caracteres
   propio para el alfabeto latino (ver `claude/mapeo-caracteres.md` del proyecto).
   **Esto NO es lo que trata este documento.**
2. **Los 38 gráficos de descripción de ítems del inventario** — este es el tema de
   este documento. Son imágenes horneadas (tiles NCGR), no texto por fuente/CSV. El
   texto está pintado directamente en los píxeles de la imagen. Por eso cada idioma
   necesita su propio set de archivos gráficos — no hay forma de reutilizar el
   mismo archivo entre ESP y ENG como si fuera texto con fuente.

## 1. Qué hay que producir

38 ítems, ID `I00` a `I37`. Cada uno tiene un archivo `I{NN}S10.NCGR` que contiene
los tiles de 4 celdas gráficas:

- **Celda 0** = nombre del ítem (una línea, caja angosta arriba).
- **Celda 1** = descripción del ítem (una o dos líneas, caja más grande abajo).
- **Celda 2** = fondo decorativo de la caja de nombre (textura repetida, SIN texto — no se toca).
- **Celda 3** = fondo decorativo de la caja de descripción (SIN texto — no se toca).

El trabajo es: tomar el nombre y la descripción en inglés de cada ítem (traducción
del japonés original, ver tabla en la sección 4) y "reescribirlos" en tiles pixel
por pixel, en el mismo lugar exacto donost donde estaba el japonés original, sin
tocar el layout de OBJs del NCER (mismo número/posición/tamaño de tiles — solo se
repintan los píxeles).

**37 de los 38 ítems ya están resueltos y validados en la versión en español**
(I00–I37 salvo I22). El ítem **I22** (palillos/chopsticks) quedó pendiente porque
su caja de nombre mide apenas 16×16px (un solo tile, el mínimo posible) — no entra
ninguna traducción corta ahí sin extender el NCER. Ese caso especial se está
resolviendo en el chat original (ver sección 7) y **no es parte de esta tarea** —
cuando se resuelva, la solución (extender NCER) se aplicará a ambos idiomas por
separado de todos modos, así que no bloquea nada de este trabajo. Tratar I22 igual
que los otros 37 por ahora: traducir el nombre lo más corto posible aunque no entre
todavía, y dejarlo documentado como pendiente igual que en español.

## 2. Especificación técnica EXACTA (debe ser igual a la versión en español)

- **Fuente:** DejaVu Sans Condensed Bold. Path validado en el dispositivo del
  usuario: `/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf`. Es la
  misma familia tipográfica ya usada para los carteles de nombre de personajes
  (`G00M10`/`G00M11`), pero a un tamaño más chico por el espacio disponible.
- **Tamaño de fuente:** 9px como default ("peor caso" acordado, validado en juego
  real en 3 ítems). Cuando el nombre no entra en el ancho real disponible a 9px,
  bajar a **8px** y, si hace falta, a **7px** — en ese orden, probando primero 9,
  después 8, después 7 (así se hizo en los 37 ítems en español; nunca hizo falta
  bajar de 7 salvo el caso límite de I22, que es un problema de ancho de caja, no
  de tamaño de fuente).
- **Render:** texto a **blanco puro sobre transparente**, SIN anti-aliasing —
  umbral binario (un píxel se pinta sí o no, no hay escala de grises). A este
  tamaño se ve más nítido así que con anti-aliasing.
  - El índice de color "blanco" a usar en la paleta 4bpp NO es necesariamente el
    índice 1: hay que calcularlo por NCLR con `find_white_index()` (busca el índice
    más cercano a RGB puro blanco, excluyendo el índice 0 que es transparencia). En
    la paleta de ejemplo (`I00S10.NCLR`) el índice 0 es verde `(0,248,0)`
    (transparencia), índice 1 es negro (contorno), índice 3 es
    `(224,224,224)` blanco/gris claro (el que se usa para pintar el texto) — pero
    el índice exacto puede variar por ítem, por eso siempre se calcula, nunca se
    hardcodea.
- **Alineación:** texto alineado a la **IZQUIERDA** dentro de cada línea, NUNCA
  centrado. Esto es importante: el ancho real disponible puede variar entre la
  línea 1 y la línea 2 de una misma celda (ver bug de ancho abajo), así que centrar
  usando el ancho total del bounding box combinado corta texto a mitad de palabra.
- **Padding:** `pad_x = 0` — sin margen izquierdo extra. Un padding de 2px causó
  bugs en la versión española (texto "justo al límite" perdía la última letra).
- **Paleta:** se reutiliza la paleta original del ítem (`.NCLR`), no se toca. Cada
  ítem ya trae su paleta de 16 colores 4bpp; el pipeline solo repinta tiles usando
  el índice de blanco calculado sobre esa paleta.
- **Layout de tiles (NCER):** NO se debe modificar. Se mide el bounding box real de
  cada celda (a partir de los OBJs que la componen) y se pinta el texto nuevo
  exactamente en esa área, tile por tile, sin agregar ni quitar OBJs. El tamaño del
  archivo `.NCGR` de salida debe ser IDÉNTICO al original (esto se verifica con un
  `assert` en el script).
- **Bug importante de ancho — leer con atención:** el ancho real disponible para el
  texto de una celda NO es el tamaño del panel completo. Cada ítem tiene su propia
  cantidad de OBJs de texto, recortada al largo del japonés original — items con
  texto corto en japonés tienen MENOS tiles asignados, aunque el fondo decorativo
  (celda 2/3) mida siempre lo mismo (208×24 nombre, 256×48 descripción, 2 líneas de
  24px) en los 38 ítems. Ejemplos reales medidos en la versión en español: I01
  descripción real 160px/192px por línea (no 256); I08 real 208px/192px; I15 nombre
  real solo 48px; I22 nombre real solo 16px (caso límite). Además, **cada línea
  dentro de una misma celda puede tener un ancho real DISTINTO** (si el japonés
  original tenía una línea más larga que la otra). La solución ya implementada:
  `row_widths_for_cell()` calcula el ancho real disponible por franja de 16px de
  alto mirando qué OBJs cubren esa franja en Y (no asume rectángulo uniforme), y
  `wrap_to_widths()` ajusta el texto línea por línea contra esos anchos reales
  (nunca asumir el ancho del panel completo).

## 3. Cómo generar los gráficos — pipeline paso a paso

Todo esto corre en el dispositivo del usuario (Windows, vía shell Linux), en la
raíz del proyecto.

1. **Archivos fuente sin tocar:** `extraccion_rom/root/ITM/2D/I{00-37}S10.NCGR`
   (+ `.NCLR`, `.NCER`, `.NANR` hermanos). Son 38 objetos, uno por ítem. Nunca se
   editan directamente — siempre se lee el original y se genera una COPIA
   parcheada en otro lado.
2. **Script principal a reutilizar/adaptar: `redibujar_items_prueba.py`** (ya
   existe en el repo, es el que se usó para español). Su lógica central:
   - Decodifica el NCGR/NCLR/NCER del ítem (usa el módulo `ncer_decode.py`, que ya
     tiene las funciones `decode_ncgr`, `decode_nclr`, `decode_ncer`,
     `obj_geometry`, `parse_container` — no hay que reimplementar nada de eso, ya
     está resuelto y validado).
   - Para la celda 0 (nombre): mide el bbox real vía los OBJs de esa celda, envuelve
     el texto (una sola línea) al ancho real, lo renderiza a máscara binaria y
     parchea los tiles 4bpp correspondientes en una copia del `tile_data` del NCGR.
   - Para la celda 1 (descripción): igual pero con `max_lines=2` y
     `row_widths_for_cell()` + `wrap_to_widths()` para repartir el texto en hasta 2
     líneas respetando el ancho real de cada una.
   - Reconstruye el NCGR completo (header + bloque RAHC sin tocar, solo el
     `tile_data` interno reemplazado) y verifica que el tamaño de archivo no haya
     cambiado.
   - Guarda cada NCGR parcheado en una carpeta de salida (en español fue
     `_scratch_claude/ncgr_editados/`).
   - **Para inglés:** conviene duplicar/adaptar este script a algo como
     `redibujar_items_prueba_eng.py`, con el mismo `FONT_PATH`, mismo
     `DESC_FONT_SIZE = 9`, y un dict `ITEMS` con `name_en`/`desc_en` en vez de
     `name_es`/`desc_es` (mismas claves `name_size`, ajustadas por ítem según haga
     falta, igual que en español). El resto de la lógica (medición de bbox real,
     wrap por ancho real, render, parcheo de tiles) se copia tal cual — ya está
     validada y no debería tocarse.
3. **Verificación visual sin ROM:** para cada ítem (o tanda de ítems), generar un
   PNG de preview componiendo celda 0 + celda 2 (nombre + su fondo) y celda 1 +
   celda 3 (descripción + su fondo), y revisar a ojo que el texto entra bien y se
   ve legible. En español se usó `_make_batch3_preview.py` (reutilizado por tanda,
   editando a mano la lista `ITEMS` y el nombre de archivo de salida) y al final
   `_make_full_contactsheet.py` (genera una única hoja de contacto con todos los
   ítems juntos, 2 columnas, para revisar el conjunto completo de una vez sin tener
   que desbloquear los ítems en el juego real). **Recomendado: generar el
   equivalente en inglés de esa hoja de contacto y compararla visualmente con
   `_scratch_claude/all_items_contactsheet.png`** (la de español) para confirmar
   que el layout, tamaño de fuente y estilo de render son visualmente idénticos
   salvo el idioma.
4. **Integración al pipeline de build:** una vez que los 37 (o 38, si I22 ya está
   resuelto para entonces) NCGR estén generados y verificados visualmente, copiarlos
   a **`assets/graficos/eng/ITM/2D/`** (carpeta ya creada, actualmente vacía —
   preparada exactamente para esto). **No hace falta tocar `generar_rom_eng.py`** —
   ya tiene un bloque de auto-discovery que agrega automáticamente cualquier
   `.NCGR` que encuentre en esa carpeta a `GRAPHICS_PATCHES` al generar la ROM. Solo
   hay que poner los archivos ahí con el nombre correcto (`I{NN}S10.NCGR`).
5. **Generar la ROM de prueba:** correr `generar_rom_eng.py` (ya existente, no
   requiere cambios) y validar que arranca en emulador (melonDS) antes de probar en
   hardware real.

## 4. Tabla completa: japonés original + traducción ya usada en español (referencia)

Usar esta tabla como fuente para traducir al inglés. La columna "Nombre (ES)" /
"Descripción (ES)" es la traducción española YA VALIDADA que entra en el espacio
real disponible a 9px (o 8/7px donde se indica) — es una referencia útil de
**longitud objetivo**, pero el inglés se debe medir de forma independiente (el
ancho real en píxeles de una palabra en inglés no es el mismo que en español, así
que puede entrar más holgado o más justo según el ítem — siempre volver a medir con
`row_widths_for_cell()`, nunca asumir que si entró en español entra igual en
inglés).

Notas de tamaño de fuente reducido cuando aplica: "(name@8)" o "(name@9)" al lado
del nombre en español indica el tamaño de fuente que se necesitó para esa celda en
particular (si no dice nada, es 9px). Repetir el mismo proceso de prueba
descendente (9→8→7) para inglés, independientemente de lo que haya hecho falta en
español.

| ID | Nombre (JP) | Nombre (ES) — referencia | Descripción (JP) | Descripción (ES) — referencia |
|---|---|---|---|---|
| I00 | 懐中電灯 | Linterna | メグミが持ってきた懐中電灯。 | La linterna que trajo Megumi. |
| I01 | 旧校舎の地図 | Mapa del edificio viejo (@8) | 図書室に置いてあった桐塚高校旧校舎の校内図。 | Plano del edificio viejo de Kirizuka. Estaba en la biblioteca. |
| I02 | コイン | Moneda | ゲームセンターによくあるコイン。 | Una moneda común, como las de los game centers. |
| I03 | メグミのケータイ | Celular de Megumi | 屋上の花壇に落ちていたメグミの携帯電話。 | El celular de Megumi, que estaba caído en el jardín de la azotea. |
| I04 | 旧校舎の鍵 | Llave del edificio | 桐塚高校旧校舎の様々な部屋を開ける鍵。 | Llave que abre salas del edificio viejo de Kirizuka. |
| I05 | コックリさんの紙 | Papel de la Kokkuri-san | 音楽室に落ちていたコックリさんの紙。 | Papel de la Kokkuri-san, caído en la sala de música. |
| I06 | カナのケータイ | Celular de Kana | 何故か教室に落ちていたカナの携帯電話。 | El celular de Kana, caído por algún motivo en el salón. |
| I07 | 手鏡 | Espejo de mano (@8) | 保健室の机の引き出しにあった手鏡。 | Espejo que estaba en el cajón del escritorio de la enfermería. |
| I08 | 写真1 | Foto 1 | 資料室で拾った戦時中の写真。大勢の人が横たわっている。 | Foto de guerra hallada en la sala de material: gente tendida en el suelo. |
| I09 | 写真2 | Foto 2 | 資料室で拾った戦時中の写真。防空壕の様子が写っている。 | Foto de guerra encontrada en la sala de material. Es un refugio antiaéreo. |
| I10 | 写真3 | Foto 3 | 資料室で拾った戦時中の写真。記念写真のようだ。 | Foto de guerra encontrada en el material. Parece conmemorativa. |
| I11 | 東桐塚駅の地図 | Mapa de la estación | 桐塚高校最寄りの東桐塚駅の構内図。 | Plano de la estación, la más cercana a Kirizuka. |
| I12 | 石のかけら | Fragmento | なにかが刻まれている。 | Tiene algo grabado. |
| I13 | 石のかけら | Fragmento | なにかが刻まれている。 | Tiene algo grabado. |
| I14 | 石のかけら | Fragmento | なにかが刻まれている。 | Tiene algo grabado. |
| I15 | お札 | Talismán | ポスターの裏に貼ってあったお札。 | Talismán pegado detrás de un póster. |
| I16 | 懐中時計 | Reloj | 隠された洞窟に落ちていた懐中時計。 | Reloj caído en una cueva oculta. |
| I17 | 間取り図 | Plano de casa (@8) | 不動産屋のチラシ。ミズキの家の間取りが載っている。 | Folleto de una inmobiliaria. Tiene el plano de la casa de Mizuki. |
| I18 | ビデオテープ | Cinta de video | ミズキの家の前に置いてあったらしいビデオテープ。 | Cinta de video que, al parecer, estaba dejada frente a la casa de Mizuki. |
| I19 | 方位磁針 | Brújula | 一見方位磁針だが霊力を探知できるらしい。 | Parece una brújula, pero detecta energía espiritual. |
| I20 | アルミホイル | Papel aluminio | 何故か台所の奥で山積みになっていたアルミホイル。 | Papel aluminio que, por algún motivo, estaba amontonado al fondo de la cocina. |
| I21 | 茶碗 | Cuenco | リビングの床下収納に入っていた茶碗。 | Cuenco que estaba guardado bajo el piso del living. |
| I22 | 箸 | (pendiente — caja de nombre 16×16px, ver sección 1) | リビングの床下収納に入っていた箸。 | Palillos guardados bajo el piso del living. |
| I23 | ナイフ | Cuchillo | いつもミズキが使っている果物ナイフ。 | El cuchillo de fruta que Mizuki usa siempre. |
| I24 | コップ | Vaso | 食塩水が入っているコップ。 | Vaso con agua salada. |
| I25 | ぬいぐるみ | Peluche | ミズキが可愛がっていたクマのぬいぐるみ。 | Peluche de oso que Mizuki quería mucho. |
| I26 | 風船（赤） | Globo (rojo) | 金庫に入っていた赤い風船。 | Globo rojo dentro de una caja fuerte. |
| I27 | 風船（黄） | Globo (amarillo) (@8) | ミラーハウスで見つけた黄色い風船。 | Globo amarillo, encontrado en la casa de espejos. |
| I28 | 風船（青） | Globo (azul) | ジェットコースター乗り場に落ちていた青い風船。 | Globo azul caído en el andén de la montaña rusa. |
| I29 | ヘリウムガス | Gas helio | 何かをふくらませるために使うヘリウムガス。 | Gas helio, usado para inflar algo. |
| I30 | メリーゴーラウンドの模型 | Maqueta del carrusel | ドリームパークのオーナーが自分で作った模型。 | Maqueta hecha por el propio dueño de Dream Park. |
| I31 | ドリームパークのマップ | Mapa de Dream Park | ドリームパークの案内図。迷ったら確認してみよう。 | Plano guía de Dream Park. Revisalo si te perdés. |
| I32 | オーナーの日記 | Diario del dueño | 事務所の机で見つけたオーナーの日記。 | Diario del dueño, encontrado en el escritorio de la oficina. |
| I33 | メモ | Nota | 観覧車の絵が描いてある。 | Tiene dibujada una noria. |
| I34 | 懐中電灯 | Linterna | ミズキの家にあった懐中電灯。 | Linterna que había en la casa de Mizuki. |
| I35 | 懐中電灯 | Linterna | レイカが持ってきた懐中電灯。 | La linterna que trajo Reika. |
| I36 | リコのケータイ | Celular de Riko | プールサイドに落ちていたリコの携帯電話。 | El celular de Riko, caído junto a la pileta. |
| I37 | 新校舎の地図 | Mapa del edificio nuevo (@8) | 生徒手帳に載っている桐塚高校新校舎の校内図。 | Plano del edificio nuevo de Kirizuka, en la libreta de estudiante. |

**Notas de contenido (aplican igual en inglés):**
- I12, I13, I14 comparten exactamente el mismo texto japonés (mismo "fragmento",
  repetido 3 veces — probablemente piezas de un mismo puzzle). En español se
  tradujeron los 3 igual ("Fragmento" / "Tiene algo grabado."). Se puede considerar
  diferenciarlos en inglés (ej. "Fragment 1/2/3") si el espacio real lo permite,
  pero no es obligatorio — en español no entraba y se dejaron iguales.
- I00, I34, I35 son las 3 "linternas" (flashlights) que traen distintos personajes.
- I21 (茶碗, cuenco/bowl) e I22 (箸, palillos/chopsticks) comparten la misma
  descripción japonesa literal.
- I26, I27, I28 son los 3 "globos" (balloon) rojo/amarillo/azul.
- I29–I32 son la sección de Dream Park (parque de diversiones): el nombre "Dream
  Park" se dejó sin traducir en español (es un nombre propio) — usar el mismo
  criterio en inglés (no traducir).
- **Nombres propios de personajes** (deben escribirse EXACTAMENTE igual que en el
  guion principal en inglés, `guion_principal_eng.csv`, para consistencia): Megumi,
  Kana, Mizuki, Reika, Riko. Verificar contra ese CSV antes de dar por buena la
  traducción final (en español esto quedó como tarea pendiente de revisión, no se
  verificó todavía — hacerlo para ambos idiomas cuando se audite esto).

## 5. Checklist de calidad para dar por buena la traducción de cada ítem

Para cada uno de los 38 (37 sin contar I22):

1. Medir el ancho real disponible (celda 0 y celda 1) con `row_widths_for_cell()` —
   nunca asumir el ancho del panel completo (208×24 / 256×48).
2. Probar la traducción en inglés a 9px. Si no entra en el ancho real de alguna
   línea, acortar/reformular el texto — probar antes de bajar el tamaño de fuente.
3. Si acortar no alcanza, bajar a 8px, después a 7px si hace falta, repitiendo el
   proceso de wrap.
4. Renderizar el preview (PNG) de esa celda y revisar a ojo que el texto no se vea
   cortado ni pegado al borde.
5. Confirmar que el archivo NCGR de salida tiene el mismo tamaño en bytes que el
   original (el script lo verifica con un `assert`, no debería fallar nunca si se
   usa el pipeline tal cual).
6. Al terminar todos, generar la hoja de contacto completa en inglés y compararla
   visualmente con la de español para confirmar consistencia de estilo.

## 6. Entregable esperado de este trabajo

- Carpeta `_scratch_claude/ncgr_editados_eng/` (o el nombre que se use) con los
  NCGR parcheados en inglés, tal como se hizo con `ncgr_editados/` en español.
- Copia final de esos archivos en `assets/graficos/eng/ITM/2D/` (la carpeta ya
  existe, vacía, lista para recibirlos).
- Un doc de traspaso análogo a este pero actualizado con progreso/decisiones
  tomadas durante la traducción al inglés (igual que se hizo con
  `claude/investigacion-items-graficos.md` en español) — si el proyecto de Claude
  al que se conecta el nuevo chat es el mismo, actualizar ESE doc directamente en
  vez de crear uno nuevo.

## 7. Qué NO es parte de esta tarea (contexto, no bloquea nada)

- El caso especial de **I22** (extender el NCER para que entre "chopsticks" o
  similar en una caja de nombre de 16×16px) se está evaluando en el chat/proyecto
  original, en paralelo. Cuando se resuelva ahí, la técnica (extender OBJs/tiles de
  la celda 0) se podrá aplicar después también al NCGR en inglés de I22 — no hace
  falta esperar a que se resuelva para avanzar con los otros 37 ítems en inglés.
- Generar la ROM ESP definitiva, revisión de neutralidad del español, y validación
  en juego de los ítems en español — son tareas del chat original, no de este.

## 8. Estado al 2026-09-08 (completado por el chat que arrancó desde este handoff)

**Los 37 ítems (I00–I37 salvo I22) quedaron traducidos, redibujados, verificados
visualmente e integrados al pipeline de build en inglés.**

- Traducción: los 37 nombres/descripciones en inglés se midieron contra el ancho
  real disponible de cada celda (no el panel completo) usando
  `_scratch_claude/measure_widths.py` → `_scratch_claude/cell_widths.json`
  (bbox real por OBJs, `row_widths_for_cell()`). El ajuste de tamaño de fuente se
  automatizó con `_scratch_claude/fit_check.py` (prueba 9→8→7px, igual criterio
  que en español). Resultado: 34 ítems entran a 9px, I01/I22(nombre)/I27 a 8px,
  I37 a 7px — todos por debajo de 7 no hizo falta en ningún caso.
- Script de redibujado: `redibujar_items_prueba_eng.py` (copia adaptada de
  `redibujar_items_prueba.py` con dict `ITEMS` usando `name_en`/`desc_en`/
  `name_size`). Reutiliza sin cambios `ncer_decode.py`, `wrap_to_widths()`,
  `row_widths_for_cell()`, `find_white_index()`, el render binario sin
  antialiasing y el `assert` de tamaño de archivo idéntico. Corrido contra los
  38 ítems (incluyendo I22 con la base extendida
  `_scratch_claude/i22_extendido/I22S10` que ya había generado el chat
  original) → 38 NCGR en `_scratch_claude/ncgr_editados_eng/`, todos con el
  mismo tamaño en bytes que sus pares en español (el `assert` no falló en
  ninguno).
- Verificación visual: `_make_full_contactsheet_eng.py` (adaptación de
  `_make_full_contactsheet.py`, con la corrección de usar el NCER de
  `CUSTOM_BASE` para I22 en vez del original de `extraccion_rom/` — el
  original tenía un bug ahí, usaba siempre el NCER de ROOT incluso para I22)
  → `_scratch_claude/all_items_contactsheet_eng.png`. Revisado ítem por ítem
  contra la hoja en español: mismo layout, mismo tamaño de fuente, mismo
  estilo de render, ningún texto cortado ni pegado al borde en ninguno de los
  38.
- Integración al pipeline: copiados 37 NCGR (todo salvo I22) a
  `assets/graficos/eng/ITM/2D/`. `generar_rom_eng.py` los toma automáticamente
  por auto-discovery, sin tocar el script.
- **I22 (palillos/chopsticks):** traducido ("Chopsticks", cabe a 8px en la caja
  extendida de 48×16px) y redibujado usando la misma base extendida
  `i22_extendido` que ya existía en el device (generada por el chat original,
  en paralelo, aparentemente resuelta después de escribirse este handoff — el
  NCGR con "Palillos" en español ya está en `_scratch_claude/ncgr_editados/`
  también). El NCGR en inglés de I22 se generó pero **NO se copió** a
  `assets/graficos/eng/ITM/2D/`: queda en
  `_scratch_claude/ncgr_editados_eng/I22S10_pending_not_in_build.NCGR`,
  porque `assets/graficos/esp/ITM/2D/` tampoco tiene todavía un I22S10.NCGR
  (el estado español no llegó a integrar la caja extendida al pipeline de
  ROM) — se mantiene la misma paridad ESP/ENG hasta que eso se resuelva en el
  chat/proyecto original, para no adelantarse con un layout de NCER que la
  ROM todavía no tiene actualizado en ninguno de los dos idiomas.
- **ROM de prueba (`generar_rom_eng.py --` / build completo): NO se corrió
  desde este chat.** El shell del dispositivo del usuario (vía el puente de
  Cowork) no tiene acceso a PyPI para instalar `ndspy` (egress bloqueado), y
  tampoco lo tiene el contenedor en la nube. El usuario confirmó que las ROMs
  `Twilight Syndrome - ESP.nds` / `- ENG.nds` ya existentes las generó él
  mismo, fuera de este puente (en su propia terminal con internet), así que
  no es un bloqueo real del proyecto — el usuario debe correr
  `generar_rom_eng.py` de la forma en que lo venía haciendo para obtener la
  ROM de prueba en inglés con estos 37 ítems, y validarla en melonDS.

**Entregable de este chat:** los 37 NCGR en `assets/graficos/eng/ITM/2D/`,
listos para el próximo build de `generar_rom_eng.py`. Nombres propios de
personajes (Megumi, Kana, Mizuki, Reika, Riko) verificados contra
`assets/csv/guion_principal_eng.csv` — coinciden exactamente en capitalización
con lo usado en las traducciones de ítems.
