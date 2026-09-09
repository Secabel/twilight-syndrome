# Handoff: inventario visual completo de gráficos con texto japonés

> **RESUELTO (2026-09-09).** El inventario se completó y ya se tradujo y
> redibujó todo lo que se decidió que valía la pena. Resultado completo,
> capturas y la decisión final de qué traducir y qué no:
> [docs/hallazgos/inventario-graficos-completo.md](hallazgos/inventario-graficos-completo.md).
> Detalle técnico de cómo se hizo cada parte (scripts, formatos, bugs
> encontrados): buscar las entradas del 2026-09-09 en
> [docs/historia-proyecto.md](historia-proyecto.md). Este doc queda abajo
> tal cual como registro histórico de cómo arrancó la tarea.

> Doc de traspaso para continuar este trabajo en otro chat/cuenta (por límite de
> tokens en el chat original). Contexto general del proyecto — fuente v21, reglas
> operativas de save/CSV, formato NCGR/NCLR/NCER, etc. — está en
> `claude/historia-proyecto.md`, `claude/plan-tecnico.md` y
> `claude/investigacion-items-graficos.md` del Project de Claude
> "Twilight Syndrome Kinjirareta Toshi Densetsu". Leerlos antes de empezar.

## 0. Qué se pide

El proyecto de traducción está funcionalmente terminado (guion completo, fuente
custom, nombres de personaje, 38 ítems del inventario — todo en ESP y ENG). Lo
único que quedó explícitamente sin resolver es una duda abierta: **¿hay algún
otro gráfico del juego con texto japonés horneado en los tiles (no reinsertable
vía el CSV/fuente) que valga la pena traducir?**

Ya existe un inventario parcial, hecho a mano el 2026-09-07, que identificó
como "gráfico puro con texto" a: las ~38 pantallas de ítems (ya resueltas), el
menú de guardado (はい/いいえ/記録/戻る + un título rojo estilo leyenda
urbana), el título, el logo, mensajes de error, y los créditos finales. Ese
inventario **no fue exhaustivo** — se hizo mirando specíficamente los gráficos
relacionados a los ítems y al cartel de nombre, no recorriendo sistemáticamente
TODA la ROM. En particular, las carpetas `EV0-EV9` y `R01-R24` del filesystem
(gráficos de eventos/pantallas específicas) nunca se revisaron a fondo.

**Objetivo de esta tarea:** generar un volcado visual (PNG) de absolutamente
todos los gráficos de tiles de la ROM (todo archivo `.NCGR` con su `.NCLR`
correspondiente, y su `.NCER` si existe), armar una o más hojas de contacto
navegables, revisarlas, y entregar una lista de qué pantallas/elementos tienen
texto japonés visible, con una recomendación de cuáles valen la pena traducir
(criterio: ¿bloquea entender o progresar en el juego?, no completitud estética
pura — aunque el usuario puede decidir traducir algo aunque no sea estrictamente
necesario si el costo es bajo).

**Esto es un trabajo de reconocimiento/triage, NO de traducción ni edición.**
No hace falta escribir ni una sola línea de traducción ni tocar ningún NCGR en
esta tarea — solo generar las imágenes, mirarlas, y reportar.

## 1. Dónde está todo

Todo el trabajo real ocurre en la máquina Windows del usuario, vía el bridge de
`device_bash` (carpeta conectada — verificar el nombre exacto de la carpeta
disponible en la sesión, debería ser
`Twilight Syndrome Kinjirareta Toshi Densetsu`, montada en
`$HOME/mnt/Twilight Syndrome Kinjirareta Toshi Densetsu`). Estructura relevante
dentro de esa carpeta:

- `extraccion_rom/root/` — filesystem NitroFS completo extraído con Tinke.
  Contiene las carpetas `SYS/`, `ITM/2D/`, `ITM/3D/`, `EV0/`...`EV9/`,
  `R01/`...`R24/`, `Font/`, y probablemente otras — **listar con
  `device_list_dir`/`find` antes de asumir nada**, la lista completa de
  carpetas no está 100% documentada.
- `scripts/ncer_decode.py` — decoder ya validado y usado en toda la sesión
  anterior: dado un nombre base (ej. `I00S10`), decodifica `.NCGR`+`.NCLR` (y
  `.NCER` si existe) y guarda PNGs por celda en `_scratch_claude/`. Reutilizar
  su lógica (las funciones `parse_container`, `decode_nclr`, `decode_ncgr`,
  `decode_ncer`, `obj_geometry`) es el punto de partida — NO reinventar el
  parser desde cero.
- `scripts/inventario_graficos.py` — ya existe un script con este nombre del
  inventario parcial de 2026-09-07 (revisarlo primero, puede que ya tenga
  lógica reusable de recorrido de carpetas).
- `scripts/extraer_todos_items.py` — ejemplo de cómo se recorrió un conjunto
  completo de archivos (los 38 ítems) y se armaron hojas de contacto en lote —
  usar como plantilla para el recorrido masivo de esta tarea.
- Todos los scripts se corren desde la raíz del proyecto:
  `python3 scripts/nombre.py` (dependen de rutas relativas a la raíz).

## 2. Formato técnico (resumen — el detalle completo está en los docs del Project)

- **NCLR** (paleta): header contenedor 16 bytes + bloque `TTLP`
  (`magic+size` + `bitDepth(u32)+padding(u32)+dataSize(u32)+reserved(u32)`,
  16 bytes) + colores `u16` RGB555.
- **NCGR** (tiles): header contenedor 16 bytes + bloque `RAHC` en offset
  absoluto 16 (`magic+size` + `tilesY(u16)+tilesX(u16)+bitDepth(u32,
  3=4bpp)+pad+pad+tileDataSize(u32)+dataRelOffset(u32, normalmente 24)`).
  Ojo: **el campo `size` del bloque YA INCLUYE sus propios 8 bytes de
  magic+size** — el bloque ocupa `[RAHC_off, RAHC_off+RAHC_size)`, no
  `+8` de más (bug real encontrado y corregido en la sesión anterior al
  extender I22 — no repetirlo). Los tiles 4bpp son 32 bytes = 64 píxeles
  (2px/byte, nibble bajo primero).
- **NCER** (composición de sprites, cuando existe): define cuántos OBJs y en
  qué posición se dibuja cada tile del NCGR. No todos los gráficos tienen NCER
  — si no existe, el NCGR probablemente es un tilemap plano (buscar también
  archivos `.NSCR`, que son mapas de tiles para fondos — puede que haya texto
  ahí también, típico de menús). **Si aparece un `.NSCR` en alguna carpeta,
  investigar su formato aparte** — no se decodificó en este proyecto todavía,
  puede hacer falta un decoder nuevo (es un formato más simple que NCER,
  básicamente una grilla de índices de tile + flip/paleta por celda, estándar
  Nitro).
- **Paleta índice 0 = transparencia** en los gráficos de texto ya vistos
  (verde `(0,248,0)` en el caso de los ítems) — no asumir que siempre es así,
  verificar por archivo.

## 3. Plan sugerido (no es obligatorio seguirlo al pie de la letra, usar criterio)

1. Recorrer `extraccion_rom/root/` completo y listar TODOS los pares
   `.NCGR`+`.NCLR` (y marcar cuáles tienen `.NCER` y cuáles no), agrupados por
   carpeta. Esto da una idea del volumen total antes de decidir cómo priorizar.
2. Para cada archivo, generar un PNG:
   - Si tiene NCER: usar `decode_ncer`+`obj_geometry` como en `ncer_decode.py`
     para componer las celdas correctamente (igual que se hizo con los ítems).
   - Si NO tiene NCER: renderizar el NCGR como una grilla simple de tiles
     (tilesX × tilesY del sub-header RAHC, o si viene `0xFFFF` — "sin
     especificar" — probar como una tira lineal o cuadrada razonable; esto es
     solo para inspección visual, no hace falta que sea pixel-perfect).
3. Armar hojas de contacto en lote (grilla de N columnas, con el nombre de
   archivo como label debajo de cada imagen — igual criterio que
   `_make_full_contactsheet.py`), separadas por carpeta de origen para que no
   sea una sola imagen gigante inmanejable. Guardarlas en
   `_scratch_claude/inventario_completo/`.
4. Revisar visualmente cada hoja de contacto (usando la herramienta de lectura
   de imágenes disponible) y anotar cuáles gráficos tienen texto japonés
   legible (no ruido/textura/ícono).
5. Para cada gráfico con texto encontrado, anotar: carpeta/archivo, una
   descripción de qué pantalla/contexto parece ser (a partir del nombre de
   archivo y/o de dónde aparece en el juego si se puede inferir), una
   estimación de cuánto texto es (una palabra, una frase, un párrafo), y una
   recomendación tentativa de prioridad.
6. Entregar como resultado final:
   - Las hojas de contacto generadas (como referencia visual).
   - Una tabla/lista en markdown con todos los gráficos-con-texto encontrados,
     agrupados por relevancia estimada (alta/media/baja — o "no vale la pena"),
     con una breve justificación por qué.
   - Actualizar `claude/investigacion-items-graficos.md` o crear un nuevo doc
     de Project si el usuario decide que valga la pena registrar esto de forma
     permanente (a criterio del usuario, no asumir esto de entrada — puede que
     sea solo un reporte para que él decida, sin nada nuevo escrito en el
     Project todavía).

## 4. Cosas a NO hacer en esta tarea

- No traducir ni editar ningún NCGR/NCER todavía — es solo reconocimiento.
- No regenerar las ROMs (`generar_rom_esp.py`/`generar_rom_eng.py`) — no hay
  ningún cambio que aplicar todavía.
- No asumir que un gráfico "parece texto" solo por tener contraste alto — mirar
  la imagen real antes de reportarlo como candidato.
- Respetar las reglas operativas del proyecto igual (aunque acá no se toca
  ningún CSV de guion): si en algún momento esta tarea deriva en editar algo,
  hacer backup con fecha/hora antes.

## 5. Contexto de por qué esto importa ahora

El usuario recibió un pedido de otra persona (traduciendo el juego al francés)
para compartir las herramientas del proyecto — el usuario planea publicar todo
en GitHub (scripts + CSV + assets modificados, no la ROM original) cuando
termine la traducción, estimado en 1-2 semanas. Este inventario es parte de
"cerrar" el proyecto antes de esa publicación: confirmar que no queda ningún
gráfico relevante sin considerar, antes de dar por completo el trabajo.
