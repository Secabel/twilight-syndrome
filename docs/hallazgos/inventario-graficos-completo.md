# Inventario visual completo - hallazgos finales

> Sigue de [handoff-inventario-graficos.md](../handoff-inventario-graficos.md).
> El extractor usado es `scripts/inventario_completo.py`. Las hojas de
> contacto (imagenes de referencia) quedaron en
> `_scratch_claude/inventario_completo/` (41 PNGs) - se pueden volver a
> generar en cualquier momento corriendo el script de nuevo, asi que no pasa
> nada si se borran para liberar espacio.

Barrido de TODOS los .NCGR/.NCBR con texto japones horneado (no reinsertable
via CSV), cubriendo ERROR, EV0-EV6, EV9, ITM, LOGO, MBP, OPTION, SAVELOAD,
STAFFROLL, SYS, TITLE, R01-R24 (~700 archivos, 41 hojas de contacto en
`_scratch_claude/inventario_completo/`). CHR/CLD/DEBUG/MAP/MNG/MOVIE/ftc/SOUND
excluidas (0 archivos NCGR/NCBR - son modelos 3D o audio). Font excluida (es
el set de glifos ya usado via CSV).

Nota tecnica: se escribio un decoder NSCR nuevo (no existia) y se detecto que
NCBR usa el mismo contenedor que NCGR. Se encontro y corrigio un bug de
renderizado (color transparente por banco de paleta, no global) a mitad de
camino - la mayoria de hallazgos ya reflejan el render corregido; unos pocos
archivos (LOGO disclaimer, TITLE tarjetas de capitulo, MBP iconos) quedan
parcialmente cortados por un problema de rango de tile_idx no resuelto, pero
la porcion visible ya alcanza para clasificarlos.

## Decision final (2026-09-09)

Despues de revisar hallazgo por hallazgo con capturas, se decidio:

- **Traducir: solo el menu de "historias" (item 1)**. Es la unica pieza que
  es navegacion real de UI (el jugador la ve sin ningun dialogo que la
  traduzca) y tecnicamente es texto simple (brillo rojo sobre negro),
  parecido en dificultad a lo que ya se redibujo para el menu/nombres de
  personaje.
- **Cadenas de mail (item 2) - queda como esta.** Se confirmo en
  `glosario_traduccion.md` que el contenido ya esta cubierto por el dialogo
  principal ya traducido (ej. el ritual completo de "Hitori Kakurenbo" con
  sus pasos numerados ya esta traducido en el guion). Ademas redibujar el
  asset es mucho mas dificil que el menu: imita una pantalla de celular
  antiguo con degradado LCD y tipografia propia compuesta por multiples
  objetos NCER, no es texto plano.
- **Papel-puzzle con tabla silabica (item 3) - queda como esta,
  deliberadamente.** Si la solucion del puzzle depende de contar o mapear
  los caracteres originales, traducirlo mal podria arruinar el puzzle
  (hacerlo irresoluble o regalar la respuesta sin querer). Se prefiere no
  tocarlo antes que arriesgar la logica del juego.
- **Manual/hoja de instrucciones (item 4) - queda como esta.** Con zoom real
  (8x) solo se lee el titulo ("アルミホイル") y dos encabezados de seccion;
  el cuerpo del parrafo esta en la resolucion nativa de la textura del DS y
  no es legible de forma confiable ni ampliando mas. Es probable que sea
  decorativo/ambiental y que las instrucciones reales de crafteo, como con
  Hitori Kakurenbo, esten en el dialogo ya traducido.

Items 5-14 (prioridad media/baja) no se evaluaron a fondo para esta decision
- quedan documentados abajo por si se quiere retomar mas adelante.

## SAVELOAD - resuelto (2026-09-09)

**SAVELOAD/S00-S06 (7 archivos)** traducidos y redibujados en ESP y ENG.
Script: `scripts/traducir_saveload.py`. Detalle tecnico completo en la
entrada correspondiente de `docs/historia-proyecto.md`.

No se sabe todavia en que pantalla del juego aparece esto exactamente
(¿guardar/cargar? el nombre de la carpeta lo sugiere, pero no esta
confirmado jugando) - queda como dato pendiente de confirmar, no bloquea
nada de lo ya hecho.

## PRIORIDAD ALTA (bloquea comprension / contenido central) - A TRADUCIR

1. **Menu de "historias" (EV9/M16-M20 + SAVELOAD/S00-S07)** - un menu
   navegable real con **45 archivos / ~43 titulos unicos** de capitulo/final,
   resultado de fortuna (大吉/中吉/凶) y pistas de gameplay ("ヒント"),
   organizados en 6 arcos:
   - 神隠しメール (Mail de desaparicion) - No.01-No.08 (8 titulos)
   - 幻のホーム (Anden fantasma) - No.01-No.06 (6 titulos)
   - ひとりかくれんぼ (Escondite en solitario) - No.01-No.16 (16 titulos)
   - こわいテーマパーク (Parque de diversiones de terror) - No.01-No.05 (5 titulos)
   - 都市伝説百物語 (100 leyendas urbanas) - No.01-No.07 (7 titulos)
   - 2 tarjetas resumen sueltas (una por arco "extra": 旧校舎のコックリさん)
   Ejemplo de hint: "「コックリさん」をした場所はドコ?". Es UI de juego real
   (probablemente pantalla de guardado/galeria de finales), no decorativo.
   Repetido tambien parcialmente en TITLE (tarjetas de capitulo).
   Ver `_scratch_claude/revision/EV9_menu_historias_completo.png` (se puede
   regenerar con `_scratch_claude/tmp_render_menu.py` si hace falta).

## Evaluados y dejados sin traducir (ver razones en "Decision final")

2. **Serie de "cadenas de mail" / leyendas urbanas numeradas** - pantallas de
   celular "受信メール", **10 archivos que muestran 9 mensajes numerados
   distintos** (#8, #27, #41, #43, #44, #68, #98, #99, #100), encontradas en
   EV3/M06/7-8, EV5/M03/6, M08/4, M13/9, M14/0-4. Solo 3 (#43, #44, #100) se
   ven completos y nitidos; el resto son fotos borrosas/inclinadas donde solo
   se lee el numero. Contenido de los legibles: "El hombre bajo la cama nacio
   de un asesinato en Kiritsuka Heights" (#44), "Reenvia esto o el oni te
   vera en hitori-kakurenbo" (#43), "Ahora mismo hay algo detras tuyo" (#100).

3. **EV1/S06/0** - papel con mancha de sangre + kana y numeros en tabla
   silabica alrededor de un dedo/hueso - prop de puzzle/cifrado.

4. **EV3/M05/1** - pagina de manual/cuaderno "アルミホイル" (papel aluminio),
   titulo y encabezados legibles, cuerpo del parrafo no legible ni con zoom.

## PRIORIDAD MEDIA (contexto/pistas util, no bloqueante)

5. EV1/M06/0 - papel tapiz roto con kana parcial de fondo en escena de found-footage.
6. EV3/M02/0 - cinta VHS con etiqueta manuscrita (borrosa, necesita mas resolucion para confirmar).
7. EV3/M05/0, M05/2 - papeles/libreta con texto manuscrito (parcialmente legible).
8. EV6/M00/8, M01/0 - recorte de diario/noticia: "教師が校内で自殺で発見"
   (profesor hallado muerto por suicidio en el colegio) - prop narrativo.
9. R17/A_S00 - dial/medidor de maquina con etiquetas "加速"/"減速" (acelerar/desacelerar) - interaccion de puzzle.
10. R23/A_S00 - cartel de parque de diversiones listando atracciones: お化け屋敷,
    ジェットコースター, 観覧車, メリーゴーランド.
11. SYS/G00M10-16 - pestañas de seleccion de nombre de personaje horneadas
    (レイカ,カナ,メグミ,アリサ,ミズキ,リコ,マサキ,ナナカ,ユイ,ユカリ) -
    los nombres ya estan traducidos en el CSV pero esta UI especifica los
    tiene como imagen, necesitaria redibujarse aparte.
12. LOGO/P01M01-02 - disclaimer estandar "esta obra es ficcion..." (parcialmente cortado por limitacion tecnica de render).

## PRIORIDAD BAJA (cosmetico, opcional)

13. Carteles de habitacion en EV9 (理科室, 音楽室, 保健室, 倉庫, 資料室, "2-2") - señaletica ambiental, 1-2 palabras c/u.
14. STAFFROLL - creditos (nombres de empresas/departamentos, ej. "品質管理", "株式会社ゲームズ") - convencionalmente no se traducen.

## EV0 - revisado a fondo (2026-09-13), corrige el barrido original

El barrido original de esta pagina listaba **EV0 como "sin hallazgos de
texto"** - eso fue un falso negativo: `render_nscr()`/`render_tile_block()`
en ese momento no manejaban el modo de "paleta extendida" de los NSCR de 8bpp
(debian indexar `colors[pal*256+idx]` en vez de `colors[idx]`), asi que las
pantallas afectadas de EV0 se veian directamente negras y no se detectaban.
Se re-barrio EV0 completo (16 subcarpetas, 59 graficos, 49/59 decodificados
con exito) con un decoder corregido (`render_nscr_ext()`, ver
`docs/historia-proyecto.md` entrada 2026-09-13) y aparecieron 2 hallazgos:

- **EV0/S00/1.NCGR - "ね、知ってる？" ("Oye, ¿sabes?" / "Hey, you know?").**
  Fondo negro con NSCR 256x256, es la primera pantalla que aparece despues
  de elegir una partida nueva, justo antes de la imagen de la mano/telefono
  fantasmal (`EV0/S00/2.NCGR`). **Traducido y redibujado en ESP y ENG**
  (`assets/graficos/esp/EV0/S00/1.NCGR`, `assets/graficos/eng/EV0/S00/1.NCGR`),
  tipografia TeX Gyre Chorus (cursiva) para imitar el trazo manuscrito
  original. Detalle tecnico completo (iteraciones de fuente/tamano/glow) en
  `docs/historia-proyecto.md`.
- **EV0/S07/5.NCGR - minijuego de llamada telefonica** ("切断中" = "Colgando/
  Desconectando...", boton "決定" = "Confirmar"). **Decision: no se traduce
  por ahora** (pedido explicito del usuario, 2026-09-13) - queda documentado
  aca para retomarlo si se decide traducirlo mas adelante.

Los otros 10 archivos de EV0 que no se pudieron decodificar (M02/6,9;
M03/6,7,9; M04/5,6,9; S01/6,9) dan ruido/estatica con el decoder actual -
visualmente parecen no tener texto pero no esta confirmado al 100%, sería
necesario investigar mas a fondo su formato para descartarlo con certeza.

## Sin hallazgos de texto

EV2, EV4 (fotos/escenas puras, sin texto), R01-R04, R07-R10, R15, R21,
R22, R24 (retratos/animaciones de personajes o UI en blanco), MBP (barras de
progreso/iconos, sin texto legible), OPTION (fotos + fuente de digitos),
ERROR (el cartel de mensaje de error es solo el marco - el texto se dibuja
aparte via CSV/fuente, ya cubierto por el sistema existente).
