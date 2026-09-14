# Guia: como abordar un bug raro/dificil de encontrar en este proyecto

Este documento nace de la investigacion del freeze de la "puerta con
llave" (ver `docs/historia-proyecto.md`, entradas del 2026-09-11/12), que
tomo muchas horas de trabajo. La causa raiz termino siendo relativamente
simple (un bug de un byte en `find_pointer_locations`), pero encontrarla
tomo mucho mas de lo necesario. Esta guia resume que hizo que fuera
dificil, en que se perdio tiempo evitable, y que hacer distinto la
proxima vez que aparezca un bug raro.

## Por que este tipo de bug es genuinamente dificil (no es falta de
habilidad, es la naturaleza del problema)

1. **No hay ningun error, crash ni mensaje.** El juego simplemente deja
   de avanzar en silencio. Sin una excepcion o stack trace que marque
   "esto fallo aqui", no hay ancla desde donde empezar a retroceder --
   hay que reconstruir a mano, instruccion por instruccion, que
   "deberia" pasar y comparar contra que pasa realmente.
2. **El sintoma visible (texto que no aparece) no tiene por que estar
   relacionado con el area de codigo que lo causa.** En este caso el bug
   estaba en un subsistema completamente distinto (el interprete de
   bytecode que dirige las escenas), no en el renderizado de texto en si
   -- que es lo primero que cualquiera sospecharia en un proyecto de
   traduccion.
3. **Puede ser una coincidencia de memoria, no una regla determinista.**
   Este bug en particular no dependia de "el texto es muy largo" de forma
   directa -- dependia de que un numero calculado a partir de la suma
   acumulada de TODAS las traducciones anteriores en el archivo cayera,
   por casualidad, en un lugar de memoria que el juego interpretara como
   "listo" o no. Probar distintos largos de texto buscando un umbral sirve
   para bugs deterministas, pero puede dar resultados sin sentido (o "sin
   patron") si la causa real es este tipo de azar.
4. **Sin depurador confiable**, todo el rastreo depende de scripts hechos
   a mano sobre desensamblado ARM crudo (via Lua + DeSmuME), con
   limitaciones reales: el registro leido en un hook puede no
   corresponder exactamente a la instruccion que se cree estar viendo,
   los hooks de escritura no siempre capturan transferencias por DMA, y
   vigilar rangos de memoria muy amplios ralentiza el emulador al punto
   de generar falsos positivos de "se congelo" cuando en realidad solo
   iba lento.

## Errores de proceso que si se pudieron evitar

- **Actuar sobre una descripcion incompleta del sintoma.** Se asumio
  "cuelgue de CPU" durante gran parte de la investigacion, hasta que el
  usuario aclaro que en realidad era una animacion que se repite en
  bucle (el juego sigue corriendo con normalidad, solo que nunca avanza
  a la siguiente escena). Esa aclaracion cambio por completo el rumbo de
  la investigacion. **Leccion: cuando el sintoma reportado es ambiguo
  ("se congela", "no responde"), pedir una descripcion bien concreta de
  que se ve en pantalla ANTES de teorizar sobre el mecanismo (¿la
  animacion se repite? ¿la pantalla queda estatica? ¿el audio sigue
  sonando? ¿los inputs hacen algo visible?).**
- **Teorizar desde el desensamblado estatico sin confirmar en ejecucion.**
  Varias horas se fueron en hipotesis que "se veian razonables" leyendo
  el codigo ARM directamente, pero que resultaron ser callejones sin
  salida al verificarlas en vivo (una funcion que nunca se ejecutaba en
  este escenario, una tabla de saltos que llevaba a codigo sin relacion,
  etc.). **Leccion: cualquier hipotesis sobre "aqui esta el problema"
  debe confirmarse con un hook en vivo (leyendo registros/memoria reales
  durante la ejecucion) antes de invertir tiempo desarrollandola mas.
  El desensamblado estatico sirve para generar candidatos, no para
  confirmarlos.**
- **Perder tiempo en el mecanismo antes de tener el sintoma clasificado.**
  Se investigaron varias teorias de "por que pasa esto" (ancho de
  caracteres SJIS vs latino, desbordamiento de buffer, corrupcion del
  guion de escena) antes de tener claro DONDE exactamente ocurria la
  divergencia entre el caso que funciona y el que falla. **Leccion:
  primero acotar el PUNTO EXACTO de divergencia (con la tecnica de abajo),
  despues investigar el mecanismo -- no al reves.**

## La tecnica que si funciono (usar esta primero la proxima vez)

**Comparacion diferencial: correr el MISMO script de diagnostico contra
un caso que funciona y un caso que falla, en el mismo punto logico
exacto, y comparar linea por linea donde empiezan a diferir.**

Esto fue sugerido por el usuario a mitad de la investigacion y fue, por
lejos, la tecnica mas productiva de toda la sesion -- mucho mas que
cualquier teoria desarrollada de antemano. Concretamente:

1. Encontrar (o crear) un caso que SI funciona y uno que NO funciona,
   que sean lo mas parecidos posible entre si (mismo save state, mismo
   camino de juego, unica diferencia = el texto/dato que se sospecha).
2. Instrumentar el mismo punto de codigo en ambos casos (rango de
   direcciones, o mejor, un disparador por CONTENIDO en vez de por
   direccion de memoria fija -- las direcciones de buffers/structs se
   reutilizan para cualquier cosa, comparar el contenido real es mucho
   mas confiable).
3. Volcar los datos crudos (bytes, registros, direcciones ejecutadas) de
   ambos casos y diferenciarlos automaticamente (`diff`, o un script que
   compare byte a byte) para encontrar el PRIMER punto donde divergen.
4. Solo ahi, investigar el mecanismo de ESE punto especifico -- no antes.

Esto evita perder tiempo teorizando sobre partes del codigo que en
realidad se comportan identico en ambos casos.

## Trucos tecnicos especificos de este proyecto (DeSmuME + Lua)

- **Los hooks de ejecucion (`registerexec`) sobre rangos grandes
  (>10-15KB aprox.) ralentizan mucho el emulador.** Esto genera un
  problema serio: si se usa "avisame cuando se congele" como señal para
  pausar, con un rango grande activo el jugador tarda mas tiempo REAL en
  llegar al mismo punto de juego, lo cual se puede confundir facilmente
  con "ya se congelo" cuando en realidad el emulador solo iba lento.
  **Siempre verificar con `wc -l` + esperar unos segundos reales que el
  archivo de log genuinamente dejo de crecer antes de concluir que algo
  esta trabado.**
- **Usar un disparador automatico (hook en un evento conocido y estable,
  como la escritura de un flag especifico) en vez de pedirle al usuario
  que reaccione en un instante preciso.** Hay transiciones de juego
  (por ejemplo, el momento exacto en que termina una animacion y
  empieza un dialogo) que ocurren en 1-2 frames -- es fisicamente
  imposible para una persona reaccionar a tiempo. Si hace falta
  capturar ese instante, automatizar la deteccion (via un
  `registerwrite`/`registerexec` en la condicion que dispara la
  transicion) en vez de depender de "avisame cuando veas X".
- **Escalar en 2 etapas:** un hook angosto y barato corriendo todo el
  tiempo, que al llegar a un punto de interes activa un hook mas ancho
  SOLO desde ahi en adelante. Esto evita la lentitud de vigilar un rango
  grande desde el arranque del juego.
- **Preferir disparadores por CONTENIDO (comparar los bytes reales de un
  texto conocido) en vez de por direccion de memoria fija.** Las
  direcciones de buffers temporales se reutilizan constantemente para
  cualquier mensaje -- asumir que una direccion fija siempre corresponde
  al mismo dato lleva a falsos positivos.
- **`memory.getregister("lr")` puede fallar** en esta build de DeSmuME;
  probar primero `"r14"` (el registro real) y usar `"lr"` como
  respaldo.
- **Al leer LR/direcciones de retorno para identificar quien llama a una
  funcion**, es mucho mas confiable que buscar todas las instrucciones
  `bl` hacia esa direccion en el binario completo -- una busqueda
  estatica de todo el archivo puede fallar en encontrar coincidencias
  reales si el codigo tiene tramos en Thumb u otras cosas que
  desalinean el desensamblado lineal (nos paso: una busqueda de "quien
  llama a esta funcion" broadcast sobre todo el arm9.bin dio CERO
  resultados para una funcion que sabiamos, por ejecucion en vivo, que
  SI se llamaba).
- **Backups inmediatos.** Cada vez que un log/CSV/archivo importante
  termina de generarse, copiarlo a un `_BACKUP` (o nombre similar) ANTES
  de seguir analizando o pidiendo otra corrida. Se perdio informacion
  mas de una vez por analizar primero y guardar despues.

## Sobre este bug especifico: por que la busqueda de punteros
(`find_pointer_locations`) es un riesgo sistemico, no un caso aislado

El bug real (ver `historia-proyecto.md`) fue que `find_pointer_locations`
busca un patron de 4 bytes en TODO el arm9.bin sin verificar que la
coincidencia sea realmente una entrada de la tabla de punteros -- puede
coincidir por pura casualidad con datos de guion de escena de otras
lineas de dialogo. El fix aplicado (`filter_legit_pointer_locations`)
resuelve los casos donde hay ambiguedad Y exactamente una coincidencia
tiene la forma correcta (`flag1` con mitad alta `0x0002`, `flag2=0`).
**Pero si en el futuro aparece un caso con 0 coincidencias "limpias" o
mas de 1, el script cae de vuelta al comportamiento antiguo (repointear
todas) y solo imprime un aviso.** Revisar ese aviso cada vez que se
regenera una ROM despues de cambios grandes al CSV -- es la señal
temprana de que este mismo tipo de bug podria estar latente en otra
escena, esperando el numero "de mala suerte" para manifestarse.

## Leccion aparte (2026-09-13): un preview casero no reemplaza probar la ROM real

Al traducir el dialogo はい/いいえ a "SI/OK"+"NO" (ver `historia-proyecto.md`,
entrada "2026-09-13 (cierre)"), se ajusto varias veces el espaciado entre
las 2 letras de はい ("SI"/"OK") ajustando el relleno/centrado de cada
letra DENTRO de su propio sprite de 16x16. Cada vez que se generaba un
nuevo render en Python (compose manual de tiles), se veia mas junto y
"arreglado" -- pero en la ROM real, generada y probada en melonDS por el
usuario una y otra vez, el espaciado nunca cambiaba ni un pixel.

La causa real no tenia nada que ver con el contenido de los tiles: los 2
sprites de はい tienen sus posiciones X hardcodeadas en el `.NCER`
(atributo `attr1`) con un hueco de 16px sin usar entre ellos (mientras
que いいえ, que si se veia bien, tiene sus 3 sprites perfectamente
contiguos). Ningun ajuste de relleno interno podia cerrar un hueco que
estaba en la GEOMETRIA (posicion del sprite), no en el dibujo.

**Por que costo tanto notarlo:** el render de verificacion en Python
pegaba los tiles uno al lado del otro en un canvas continuo (sin modelar
la posicion X real de cada OBJ del NCER), asi que el "arreglo" siempre se
veia bien en el preview aunque el problema real seguia intacto en el
juego. El usuario insistio en volver a generar y probar la ROM real
varias veces en vez de aceptar el preview como prueba suficiente, y eso
fue lo que finalmente forzo a revisar los datos de posicion del NCER en
vez de seguir iterando sobre el contenido del tile.

**Regla a futuro:** un preview/decoder casero sirve para descartar
corrupcion de datos (bytes mal escritos, offsets mal calculados), pero
NO es prueba de que algo se vea bien en el juego real -- sobre todo para
cosas de geometria de sprites (posicion X/Y, tamaño, flip), que un script
de verificacion rapido facilmente no esta modelando. Si un cambio de
contenido no produce NINGUN cambio visible en la ROM real tras mas de un
intento, es señal de que el problema esta en otro campo de datos
(posicion/tamaño en el NCER), no en seguir puliendo el contenido del
tile.

## Patron: freeze/pantalla congelada por asset grafico traducido que supera el presupuesto de VRAM/DMA

**Caso real (2026-09-13):** `TITLE/G02M10.NCGR` (fichas del menu de
seleccion de historia). Sintoma: el juego no mostraba corrupcion grafica
evidente, sino un freeze en la pantalla final de la historia 1 y, en el
menu de "Nueva Partida", el cursor se movia (sonido) pero la ficha en
pantalla no cambiaba y no se podia seleccionar la historia 2. Ambos eran
el mismo bug de fondo.

**Como se detecto la causa:** aislando por ensayo y error que carpeta de
asset causaba el freeze (renombrando carpetas de `assets/graficos/esp/`
para que el build las ignore), se llego a `TITLE/G02M10`. Comparando el
tamaño del `.NCGR` traducido (182064 bytes) contra el original japones
(67376 bytes), la diferencia era demasiado grande para ser solo el texto
nuevo: el traducido arrastraba datos de tiles japoneses ya no
referenciados por ninguna celda (huerfanos/muertos), sumando peso inutil.

**Fix generico:** reconstruir el `.NCGR`/`.NCER` conservando solo los
tiles del original que TODAVIA son usados por celdas no traducidas, mas
los tiles nuevos de las celdas traducidas, respetando la alineacion de
tiles que exige `tile_boundary_shift` del NCER (los bloques reubicados
deben empezar en multiplos de `2**tile_boundary_shift`, tipicamente 8).
Implementado en `scripts/build_g02m10_compact.py` (generico por N de
celdas traducidas, reusable como plantilla para otros NCGR/NCER).

**Cuando sospechar este mismo patron:** un asset grafico traducido
(NCGR/NCER) causa freeze, cuelgue, o "no cambia nada en pantalla" sin
corrupcion visual obvia, especialmente si:
- el `.NCGR` traducido pesa notablemente mas que el original japones
  equivalente (mas alla de lo que explicaria solo el cambio de texto);
- un preview/decoder casero (Python) muestra el contenido correcto y
  sin corrupcion, pero en la ROM real la pantalla se congela o no
  reacciona — esto descarta corrupcion de datos y apunta a un limite de
  tamaño/VRAM/DMA que el decoder casero no modela.

En ese caso, antes de rediseñar el asset o el texto, probar primero
midiendo/eliminando datos muertos (tiles originales sin referencias) del
archivo traducido — como se hizo aqui — en vez de asumir que hay que
reducir visualmente el contenido.

**Auditoria preventiva ya hecha (2026-09-14) — no hace falta repetirla:**
se reviso la estructura de TODOS los graficos traducidos del proyecto
(esp/eng) buscando cuales tienen `.NCER` (condicion necesaria para este
patron: solo existe si el archivo mezcla celdas ya traducidas con celdas
que siguen apuntando a tiles originales del mismo archivo). Resultado:
`TITLE/G02M10` es el UNICO asset del proyecto con esa estructura (29
celdas, solo algunas traducidas). Los demas (`SAVELOAD/M10,M11` -- estos
si tienen `.NCER` pero son chicos y ya se revisaron por otro bug, sin este
patron --, `SAVELOAD/S00-S06`, `SYS/*`, `EV9/M16-M20`, `EV0/S00`, los 38
items de `ITM/2D`) son `.NCGR` sueltos, redibujados completos por idioma,
sin datos originales mezclados adentro. Conclusion: NO hace falta auditar
ni "limpiar" otros assets de forma preventiva salvo que en el futuro se
traduzca parcialmente algo que hoy es un redibujado completo (ahi si
recien aplicaria este mismo chequeo). Lo que SI sigue pendiente es
distinto: probar en juego las tarjetas 3-7 de este MISMO `G02M10` cuando
se pueda avanzar mas en el save (no es "revisar otros assets", es
"terminar de confirmar este mismo fix").
