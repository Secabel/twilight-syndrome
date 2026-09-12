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
