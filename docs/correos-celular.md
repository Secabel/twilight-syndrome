# Correos y UI del celular: hallazgo y plan de traducción

*2026-09-28 (actualizado: paso 1 hecho). Origen: un jugador reportó que los correos y la pantalla del
teléfono siguen en japonés con el parche ENG.*

## Resumen

Los correos del celular **son sprites (celdas NCER)**, no texto del guion ni
fondos NSCR. Cada **línea** de un correo es **una celda NCER** independiente
(fuente katakana estilo LCD). El juego apila las celdas y las desplaza para
hacer el scroll.

- El texto **no existe como texto en la ROM**. Se buscó en arm9, en los 2780
  archivos del NitroFS, en todos los descomprimidos LZ10, y en SJIS
  (normal y half-width), UTF-16 y EUC-JP. Ni el CSV ni la fuente
  `TWSFont` sirven para esto.
- Hay que traducirlos con la **misma técnica que los ítems del inventario**:
  redibujar los tiles de cada celda.

## Dónde están: 12 grupos en `R08/`

`extraccion_rom/root/R08/{A,B,C,D,E,F,H,I,J,K,L,M}_S10` (`.NCGR` + `.NCER` +
`.NCLR` + `.NANR`). La paleta está en la misma carpeta, así que renderiza bien.

Cada grupo es un **estado de la bandeja de entrada** en un momento distinto de
la historia, por eso **se repiten líneas entre grupos**. Por ejemplo,
"６ニン ニ マワシテ クダサイ" aparece en casi todos.

Estructura común de celdas (en todos los grupos):

| Celda | Contenido |
|---|---|
| 0 | Panel de fondo del correo |
| 1 | Línea separadora |
| 2 | (vacía) |
| 3 | `---END---` |
| 4 | Ícono reloj + fecha (ej. 2008/9/10) |
| 5 | Ícono + remitente (ナナシ, カナ, ミズキ) |
| 6 | Ícono + asunto (vacío o "Fw:") |
| 7+ | Líneas del cuerpo, una por celda. Número del correo en línea aparte |

| Grupo | Celdas | Correos que contiene (aprox.) |
|---|---|---|
| A | 23 | #7 (Kokkuri-san en la sala de música, 9/10, ナナシ) + fechas/letras sueltas |
| B | 17 | #7 (igual que A, sin extras) |
| C | 17 | #7 reenviado por カナ ("Fw:", 9/11) |
| D | 12 | #24 (línea Edogawa, 9/17) |
| E | 31 | #5 (azotea / Kokkuri-san, 9/08), mail de ミズキ en hiragana (hombre bajo la cama, 9/18), #97 (9/25) |
| F | 27 | #98 (piscina / nirameko, 9/26), #72 (baño), #99 (álbum / muñeca) |
| H | 49 | #97, #88 (9/26 amanecer, terremoto en Tokio), #100 (luna llena / póster), #1 (ナナシ del otro mundo), texto "ツギハオマエダ" repetido |
| I | 64 | #7, texto corrupto a propósito (celdas 13-15), #1, #3 (edificio viejo / cadáver), acertijo モンダイ (A: kagome / B: kitsune), トオリャンセ, fwd de カナ, letras sueltas カ/ミ/ク/シ (animación) |
| J | 12 | Acertijo モンダイ (A: gakubuchi / B: coin locker baby, 9/17) |
| K | 23 | #43 (Hitori Kakurenbo), #44 (hombre bajo la cama), acertijo モンダイ (A: Kokkuri / B: Hitori Kakurenbo) |
| L | 20 | #81 (Dream Park, 9/22), acertijo モンダイ (A: crayón rojo / B: …) |
| M | 55 | Recopilatorio: #96 (Hayakawa Mizuki), #98, #72, #99, #97, #88, #100, #84 (4219 / goroawase), varias fechas |

**Estimado: ~22-24 correos únicos** (#1, #3, #5, #7, #24, #43, #44, #72, #81,
#84, #88, #96, #97, #98, #99, #100, fwd de Kana, mail de Mizuki, 4-5
acertijos, トオリャンセ). Falta la transcripción exacta (ver próximos pasos).

## Otra UI del celular (también sprites NCER)

| Archivo | Contenido |
|---|---|
| `R02/A_S10`, `R02/B_S10` | Enviar correo: 送信中 / 送信しました / 送信に失敗しました + nombres de contactos (ハルナ, マユコ, アツミ, ナツ, ミオ, ミズキ, ユミ, アヤ, ユウジ) |
| `R07/{A,B,C}_S10` | Pantalla "llamando" (solo íconos, sin texto aparente) |
| `R09/A_S10` | Historial de llamadas: 通話履歴 + nombres y fechas |
| `R10/A_S10` | Reproducción de audio: 再生中 / 再生終了 |
| `R24/A_S10` | Página web "Not Found / ページがみつかりません。…" |
| `EV0/S07/5` | Llamada: 切断中 + botón 決定 (NSCR) |
| `EV9/S00/2-9` | Fondos de pantalla del celular, solo el botón 決定 (NSCR) |

Fotos de correos dentro de escenas (NSCR 8bpp, **baja prioridad**):
`EV3/M06/7-8` (#44, #43, legibles), `EV5/M14/4` (#100), `EV5/M08/4`,
`EV5/M03/6`, `M13/9`, `M14/0-3` (borrosas/inclinadas, solo se lee el número).
Ojo: la paleta de varias NO está en el `0.NCLR` de su carpeta (banco faltante),
por ahora solo se pudieron renderizar en gris.

## Viabilidad

**Media-baja complejidad**, es el mismo pipeline de los ítems:

- **Fuente:** el juego ya trae glifos latinos en el estilo del celular:
  `END`, `Fw:`, `A`, `B`, `D`, `F`, números y fechas (se ven en R08/I celdas
  13-15 y en las fechas). Se usan como base y se dibuja a mano el resto del
  alfabeto a la misma altura. No hace falta buscar una fuente externa.
- **Ancho:** cada celda tiene solo los OBJs del japonés original. Hay que
  medir el ancho real por celda (`row_widths_for_cell()` ya existe) y
  acortar la traducción o extender la celda (técnica de I22).
- **Estilo:** el original es katakana "telegráfico" y entrecortado (efecto
  creepy). En la traducción conviene imitarlo en MAYÚSCULAS.
- **Repeticiones:** se traduce cada línea única una vez y se reutiliza en
  los 12 grupos.
- **Transparencia en render:** `compose_cell()` con la paleta real deja las
  celdas invisibles (el color de transparencia coincide con el texto). Para
  revisar se usó una paleta gris con índice 0 único. Tenerlo en cuenta al
  validar.

## Próximos pasos

1. ✅ **HECHO (2026-09-28, ver sección "Paso 1" abajo).** ~~**Transcribir** todas las celdas de texto de los 12 grupos a un CSV~~
   (`grupo, celda, texto_jp, ancho_px, traduccion_esp, traduccion_eng`),
   deduplicando líneas repetidas. Cruzar con `glosario_traduccion.md` y el
   guion (varios correos se citan en diálogos, mantener coherencia).
2. **Armar la fuente del celular:** extraer los glifos latinos existentes
   (END, Fw:, A, B, números) y completar A-Z, Ñ y los acentos a la misma
   altura y estilo.
3. **Prueba con un solo correo:** redibujar **#7 en `R08/B_S10`** (el más
   simple, 17 celdas) y validarlo en melonDS y 3DS **con ROM regenerada y sin
   savestates viejos**.
4. Si la prueba se ve bien, **aplicar a los 12 grupos** (ESP + ENG) en
   `assets/graficos/{esp,eng}/R08/`. El pipeline de `generar_rom_*.py` los
   toma solos.
5. **UI secundaria del celular** (R02, R09, R10, R24, EV0/S07/5, botón 決定
   de EV9/S00): pocas palabras, rápido una vez que exista la fuente.
6. **Opcional / último:** fotos de correos en EV3/EV5. Primero encontrar la
   paleta real (banco faltante). Alternativa provisoria: publicar mockups o
   una tabla de traducción de esos correos para los jugadores.
7. Actualizar README/post de GBAtemp: aclarar que correos y celular están
   pendientes y que no es un error de instalación.

## Paso 1: transcripción y primera traducción (2026-09-28)

Archivos nuevos en `docs/`:

- `correos_celular_celdas.csv`: las **350 celdas** de los 12 grupos, una fila por
  celda (`grupo, celda, tipo, texto_jp, ancho_px, traduccion_esp, traduccion_eng, nota`).
  Es el que va a leer el script de redibujo.
- `correos_celular_lineas.csv`: **139 líneas únicas** a redibujar (deduplicadas),
  con `ancho_min_px`, estimación de ancho de la traducción (8 px/letra),
  columna `extender` (ESP/ENG si no cabe en los OBJ originales) y `usos`
  (qué celdas comparten esa línea).
- `correos_celular_texto.md`: los correos reconstruidos completos (JP/ESP/ENG),
  para revisar la traducción leyendo el correo entero y no línea por línea.

Scripts y hojas de contacto en `_scratch_claude/mails/transcr/`
(`dump.py`, `transcripcion.py`, `traducciones.py`, `build_csv.py`, `sheet_0*.png`).
Para corregir una traducción: editar `traducciones.py` y correr `build_csv.py`
(regenera los CSV; luego copiarlos a `docs/`).

Tipos de celda usados: `PANEL, SEP, VACIA, END, FECHA, DE, ASUNTO, NUM, LETRA,
GLITCH, CUERPO`. **No se redibujan:** fechas, números de correo, `---END---`,
`Fw:` y el texto corrupto de `R08/I` 13-15 (ya son símbolos/latín).

Hallazgos de la transcripción:

- **Correos únicos confirmados:** #1, #3, #5, #7, #24, #43, #44, #67 (no estaba en
  la lista inicial: preparación de economía doméstica / ahorcado), #72, #81, #84,
  #88, #96, #97, #98, #99, #100, fwd de Kana, mail de Mizuki (hiragana),
  "オクジョウ デ マツ", "ヒトリ ジャナイヨ", トオリャンセ, bloque
  "ツギハオマエダ" y 4 acertijos モンダイ (I, J, K, L).
- El número del correo va **después** del cuerpo (cierra el correo).
- **Animaciones de letras:** `R08/A` 18-22 = オ・ソ・カ・ッ・タ ("llegaste tarde")
  → ESP **T·A·R·D·E**, ENG **L·A·T·E·!** (5 celdas, calza justo).
  `R08/I` 17-20 y 42-57 (4 frames cada una) = カ・ミ・ク・シ (カミカクシ, la カ se
  reutiliza) → **KA·MI·KU·SHI** en ambos idiomas (glosario deja "kamikakushi" en
  romaji). SHI ocupa 24 px en celdas de 16: hay que dibujarla angosta o extender.
- Remitentes: NANASHI / KANA / MIZUKI. NANASHI y MIZUKI no caben en el ancho
  del original (ícono 16 px + nombre); extender o fuente angosta.
- Mail de Mizuki en hiragana → se tradujo en **minúsculas** para mantener el
  contraste con el katakana de Nanashi. Implica dibujar también minúsculas
  (solo las de ese correo: a b c d e h j l m n o r s u + ENG: d i t).
- "ツギハオマエダ": ESP `LAPROXIMAERESTU` / ENG `YOUARENEXT` repetido sin
  espacios, cortado en 7 líneas de 20 letras, como el original.
- Se reutilizaron términos del guion (hora del buey, nirameko, Kagome Kagome,
  kitsune no yomeiri, Toryanse, Heights Kirizuka, "problema", Dream Park).

**Ojo con la fuente:** los glifos latinos que ya trae el juego (fechas, END)
miden ~9-10 px de ancho con paso de ~11-12 px y 12 px de alto. Con ese tamaño
solo caben ~13 letras en 160 px. Las traducciones asumen **≤ 8 px por letra**
(glifo de 6-7 px + 1-2 de espacio, 12 px de alto), o sea hasta 20 letras por
línea. Si al diseñar la fuente queda en 9 px, hay 14 líneas ESP y 9 ENG de más
de 17 letras que habría que acortar (se pueden filtrar por largo en el CSV).
Con 8 px: 38 líneas ESP y 30 ENG necesitan extender la celda (técnica I22);
ninguna pasa de 160 px.

## Referencias

- Renders de revisión: `_scratch_claude/mails/` (`cells/*_g.png` = todas las
  celdas por grupo; `pag_*.png` = hojas combinadas; `hoja_*.png` = fotos EV).
- Detalle cronológico: `historia-proyecto.md` (entrada 2026-09-28).
- Técnica de ítems reutilizable: `investigacion-items-graficos.md` (proyecto).

## 2026-09-28 — Fuente del celular aprobada (paso 2)

- `scripts/fuente_celular.py`: alfabeto completo diseñado desde cero en el
  estilo del juego (no se reutilizan glifos originales, para evitar el
  "frankenstein" que pasó con la fuente general). Mayúsculas 5x9 px (I = 3),
  dígitos, Ñ, puntuación y las minúsculas del mail de Mizuki.
- Mismo formato que los glifos originales: trazo = índice 1, sombra =
  índice 2 (1 px a la derecha), base en la fila 15 de la celda de 16 px.
  Paso = ancho + sombra + 1 px; espacio = 3 px.
- Fechas, número de correo, `---END---` y `Fw:` quedan con los glifos
  originales (celdas separadas, nunca se mezclan en una misma línea).
- Con esta fuente no caben en su celda original 11 líneas ESP y 9 ENG
  (ninguna > 160 px): se extienden como I22.
- Aprobada por el usuario con la maqueta del correo #7
  (`_scratch_claude/mails/fuente/ejemplo_mail7.png`).

## 2026-09-28 — Prueba en ROM: correo #7 (paso 3, pendiente de validar en juego)

- `scripts/redibujar_correos.py`: redibuja celdas de R08 desde los
  originales JP y escribe `assets/graficos/{esp,eng}/R08/<G>_S10.NCGR/.NCER`.
  Uso: `python3 scripts/redibujar_correos.py A B I:5,7,8,9,10,11,12`.
  Margen izquierdo fijo de 2 px; si no cabe agrega OBJs a la derecha (tiles
  nuevos al final del NCGR) y recalcula el radio de la celda (bits 0-5 del
  atributo). Verificado: reconstruir el NCER sin cambios da el mismo archivo.
- Redibujado el #7 en A, B e I (en I solo las celdas 5 y 7-12; 13-15 son el
  texto corrupto y no se tocan) + la animación TARDE / LATE! de A (18-22).
- Extendidas: remitente NANASHI (B5, I5) y HORA DEL BUEY / WITCHING HOUR
  (celda 9), +1 OBJ cada una.
- ROMs ESP/ENG regeneradas (113/113 gráficos). **Validado en juego por el usuario (2026-09-28): "se ve bastante bien".**

## 2026-09-28 — Paso 4: los 12 grupos redibujados (ESP + ENG)

- Revisión de traducciones contra el JP antes de aplicar (backup de CSV/MD en
  `docs/backups/`). Correcciones: アクリョウ = LOS MALOS ESPIRITUS (no
  "demonios"); トショシツ = EN LA BIBLIOTECA / IN THE LIBRARY; opción B del
  acertijo de I = BODAS DEL ZORRO / THE FOX WEDDING (el diálogo dice "la B es
  el zorro"); #43 = SERAS MALDITO / IF YOU SEE THE ONI - YOU WILL BE CURSED;
  #96 = SI TE ACERCAS / GET INVOLVED (el ENG repetía "AND"); #84 ENG usa
  NIRAMEKO como el resto. お札 se mantiene AMULETO / CHARM (igual que el guion).
- Bugs corregidos en `redibujar_correos.py`: (1) algunas celdas originales
  tienen HUECOS entre OBJs (donde el JP tenía un espacio) y la letra que caía
  ahí desaparecía ("A QUIEN LE GUST"); ahora se cubre con OBJs nuevos
  cualquier columna del texto sin OBJ. (2) Las líneas de continuación de los
  acertijos conservan la sangría (alineadas después de "A "/"B ").
  (3) Letras sueltas que no entran en 16 px (SHI) se dibujan sin espacio.
- Chequeo automático: las 464 celdas redibujadas (232 por idioma) tienen
  exactamente los píxeles esperados del texto. Máx. ancho de línea: 139 px
  (límite del panel: 156).
- ROMs ESP/ENG regeneradas: 131/131 gráficos. Pendiente: prueba en juego de
  otros correos además del #7.

## 2026-09-28 — Publicado como v1.1

- Release GitHub `v1.1` con `Twilight.Syndrome.ESP.v1.1.bps` /
  `Twilight.Syndrome.ENG.v1.1.bps` (verificados: aplicados sobre la ROM JP
  dan exactamente las ROMs ESP/ENG; SHA-1 c7bc19f5... / 79e12ec1...).
- README reescrito al estilo de Terrors (capturas en `images/`, checksums,
  historial, known issues) + `LICENSE` MIT. BPS v1.0 quitados del repo
  (copias locales en `parches/`).
- romhacking.net actualizado y aprobado; posts de GBAtemp/Reddit editados.
- Pendiente para una próxima versión: resto de la UI del teléfono (R02 enviar
  mail, R09 historial, R10 audio, R24 web, EV0/S07/5 llamada, botón 決定 de
  EV9/S00) y, opcional, las fotos de correos en escenas EV3/EV5.

## UI secundaria del celular (2026-10-07)

Traducida con `scripts/redibujar_ui_celular.py` (lee siempre los originales JP,
escribe `assets/graficos/{esp,eng}/...`; los generadores los aplican solos).

| Archivo | ESP | ENG |
|---|---|---|
| R02/A,B_S10 celdas 0/1 | ENVIADO / ERROR AL ENVIAR | SENT / SENDING FAILED |
| R02/A,B_S10 celdas 22-24 | ENVIANDO... | SENDING... |
| R02/A,B_S10 celdas 4-21 | HARUNA, MAYUKO, ATSUMI, NATSU, MIO, MIZUKI / YUMI, AYA, YUUJI, MIO, NATSU, ATSUMI | igual |
| R09/A_S10 | LLAMADAS + IZUMI REIKA / ENOMOTO MIO / WATANABE HARUNA | CALL LOG + igual |
| R10/A_S10 | TOCANDO (celdas 0-2) / TERMINADO (3) | PLAYING / FINISHED |
| R24/A_S10 | NO ENCONTRADA. / REVISA LA URL. | PAGE NOT FOUND. / CHECK THE URL. |
| EV0/S07/5 (NSCR) | CORTANDO + OK | HANGING UP + OK |
| EV9/S00/2-9 (NSCR) | boton OK | OK |

Detalles: corazon central de R02/A 22-24 reconstruido extendiendo su propia
punta en V (no copiando el vecino, tienen estilos distintos); en EV0/S07/5 se
quito la placa negra y se reconstruyeron las flechas (periodo 26 px); boton OK
toma los colores del 決定 original de cada fondo (texto claro con degradado ->
color por fila). Las celdas de contacto con texto mas ancho que el original
reciben OBJs 8x8 extra. Mockups aprobados: `_scratch_claude/auditoria/
mockup_celular.png`, `mockup_alternativas.png`; verificacion final:
`ui_celular_final.png`. Falta: probar en emulador (savestate nuevo).
