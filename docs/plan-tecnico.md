# Plan técnico — Twilight Syndrome: Kinjirareta Toshi Densetsu

Roadmap de lo que ya se sabe, lo que falta investigar y lo que hay que construir
para poder traducir este juego. Vivo: se actualiza a medida que avanza el proyecto.

## Confirmado

- El guion vive como texto plano **Shift-JIS sin comprimir**, embebido directo en
  `arm9.bin` (no en archivos de recursos NitroFS — esos folders solo tienen
  gráficos: NCLR/NCGR/NSCR).
- Cada mensaje termina en `0x00`; los saltos de línea internos usan `0x0A`.
- Bloque principal de guion: offsets **0xD0000–0x110000** dentro de `arm9.bin`
  (~6650 líneas, ~93.860 caracteres japoneses).
- Buffer de texto activo en RAM mientras se muestra un diálogo: `0x0212DB2C`
  (confirmado visualmente, se reescribe con cada línea nueva).
- El header de la ROM declara el largo de `arm9.bin` explícitamente (campo
  "ARM9 length"), lo que hace viable expandirlo si hace falta.
- Herramientas ya funcionando: DeSmuME 0.9.13 (memory viewer, sin breakpoints
  confiables en esta build), TinkeDSi 0.9.6 (extracción de filesystem), HxD
  (búsqueda hex en dumps de RAM).
- Script `scripts/extraer_texto.py` ya genera `docs/texto_extraido.csv` con todo
  el texto candidato (offset, largo, texto original).

## Por investigar

1. ~~Tabla de punteros~~ — **CONFIRMADA**: el código referencia cada string por
   dirección RAM absoluta de 32 bits (0x02000000 + offset en arm9.bin), sin
   compresión ni truco. Cada entrada parece ser un mini-struct (puntero + otros
   campos, no solo un array plano) — falta mapear la estructura completa antes
   de automatizar el repunteo. Conclusión práctica: SÍ hay que repuntar si una
   traducción queda más larga, pero es edición directa de enteros de 32 bits,
   nada exótico.
2. ~~Fuente (Font)~~ — **CONFIRMADO, falta trabajo real**: de 1222 glifos totales
   en `TWSFont.NFTR`, solo hay 11/26 mayúsculas y 1/26 minúsculas latinas (letras
   sueltas en préstamos japoneses, no un alfabeto). Cero acentos/Ñ/¿/¡ — ni
   siquiera son representables en Shift-JIS estándar. Hay que agregar glifos
   faltantes y definir code points custom para los acentos (mismo truco que la
   sustitución de caracteres en Terrors, pero acá se pueden agregar de verdad).
3. **Límites de ancho/caracteres por línea.** ¿El motor hace word-wrap automático
   o depende de saltos de línea manuales como en Terrors? Afecta cuánto se puede
   alargar una traducción sin romper el layout visual.
4. **Estructura de rutas/ramas.** ¿Es lineal o tiene rutas alternativas como
   Terrors (H1/H1B, etc.)? Revisar si hace falta un flowchart como en ese proyecto.
5. ~~Los ~860 textos sueltos fuera del bloque principal~~ — **RESUELTO**: se
   revisaron (heurística de puntuación japonesa + muestreo manual) y son 100%
   ruido de decodificación de código binario. Se descartan por completo. Todo
   el texto real (diálogos, menús, mensajes de sistema) vive en un único bloque
   limpio: `docs/guion_principal.csv` (6653 filas, offsets 0xD0000–0x110000).
6. **Confirmar si arm9.bin necesita expandirse** una vez que se tenga una muestra
   real de traducción — comparar largo en bytes original vs. traducido.

## Por construir

- Script de **reinserción**: tomar el CSV traducido y escribirlo de vuelta en
  `arm9.bin` (y actualizar la tabla de punteros si corresponde).
- Si hace falta expandir la ROM: script para mover `arm9.bin` a una zona con más
  espacio y actualizar el header.
- Editor/generador de **fuente** con los glifos latinos faltantes.
- Si el motor no hace word-wrap automático: lógica para partir líneas largas
  (similar al sistema de columnas de Terrors, pero probablemente mucho más simple).

## Próximos pasos sugeridos (en orden)

1. ~~Filtrar `texto_extraido.csv`~~ — **HECHO**: `docs/guion_principal.csv`
   (6653 filas) es el guion completo y limpio, listo para traducir.
2. Encontrar la tabla de punteros — probablemente vía debugging con no$gba
   (breakpoints más confiables que DeSmuME) rastreando qué código lee la
   dirección 0x0212DB2C hacia atrás.
3. Revisar la carpeta `Font` en Tinke para saber si hace falta editar glifos.
4. Con esas tres cosas resueltas, recién ahí decidir la arquitectura de
   inserción (directa vs. con repunteo) y empezar a traducir en serio.
