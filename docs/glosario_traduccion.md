# Glosario y criterios de traduccion - Twilight Syndrome (guion_principal.csv)

## Nombres propios (se mantienen sin traducir)
- Kana, Mizuki, Megumi, Arisa, Reika: nombres de personajes (chicas de secundaria).
- Nanashi (ナナシ): aparece entre parentesis como "(...Nanashi...)" - posible nombre de
  entidad/espiritu sin nombre ("nanashi" = "sin nombre" en japones). OJO: si en filas
  futuras aparece mas seguido, revisar si es un personaje/fantasma recurrente y no un
  simple juego de palabras puntual.
- Kokkuri-san: nombre del juego de adivinacion tipo ouija, no se traduce.
- Bunjin-sama: nombre de una entidad/deidad invocada en el juego, no se traduce.
- Torii (鳥居): se mantiene el termino japones (portal/arco de santuario sintoista),
  se entiende en contexto de ritual.

## Tono y registro
- Tuteo informal neutro (no voseo chileno marcado, no "vos"). Dialogo natural de
  adolescentes, no rigido ni literal del japones.
- Frases de ritual (Kokkuri-san invocando/despidiendo al espiritu) usan un registro
  mas formal/ceremonial en japones (でございます, おいでください, etc.) -> se tradujo
  como "por favor, venga" / "vuelva a su lugar" / "las preguntas terminaron" para
  mantener ese tono ceremonial distinto del habla informal de las protagonistas.
- Interjecciones cortas (えっ, ひっ, あっ, うん) se adaptan a su equivalente natural en
  espanol (Eh, Hii, Ah, Si) en vez de traducirlas literalmente.

## Reglas de formato (recordatorio, ver guia_traduccion_csv.md)
- Sin tildes, sin ¿¡ de apertura.
- Maximo ~220px por linea (tabla de anchos letra por letra), verificado con script
  antes de guardar cada tanda.

## Progreso
- Filas 0-159: traducidas y verificadas (fila 0 marcada como no traducible/placeholder).
- Continua en fila 160 en adelante.

## Dudas abiertas para el traductor humano (revisar mas adelante)
- Fila 141 "(...Nanashi...)": confirmar si es nombre de personaje recurrente.
- Filas 130-159: bloque de fotos/textos misteriosos (この空洞, 何か写ってる, 文字はどう) -
  sin mas contexto de escena no se puede saber con certeza si hay continuidad narrativa
  estricta entre estas lineas o si son reacciones de distintos momentos del juego.

## Contexto real del juego (confirmado via Wikipedia JP, 2026-09-06)
- Protagonista: Hayakawa Mizuki (早川瑞希) - recien trasladada al instituto Kirizuka.
  OJO: en el CSV aparece "ミズキ" como nombre propio en dialogos - es la protagonista,
  asi que mantener "Mizuki" sin traducir es correcto.
- Izumi Reika (泉レイカ): companera, hija de una adivina, sensibilidad espiritual fuerte,
  personalidad serena, intenta proteger a Mizuki. Coincide con "Reika" ya usado.
- Kagami Riko (加賀美莉子): companera curiosa/despreocupada, empuja a Mizuki a investigar
  leyendas urbanas. (Nombre "Riko", distinto de "Kana" que aparece en el CSV - revisar si
  "Kana" es un personaje secundario propio del capitulo especifico de la vieja escuela/
  Kokkuri-san, ya que el juego es antologia de leyendas con casts que varian por capitulo.)
- Seno Masaki y Sakurai Yuuta: companeros varones, amigos de infancia de Riko.
- Hasegawa Yukari: profesora que da pistas.
- NANASHI (ナナシ): remitente misterioso de los correos en cadena (chain mail) que
  desencadenan las leyendas urbanas - es CENTRAL a la trama, no un personaje menor.
  Mantener "Nanashi" sin traducir en todas sus apariciones.
- Estructura narrativa: intro "Kokkuri-san del edificio viejo" + 5 leyendas urbanas
  (correo de desapariciones, anden fantasma del metro, escondidas tu sola, parque de
  diversiones que da miedo, cien historias de leyendas urbanas) + capitulo final sobre
  la profesora desaparecida. Cada capitulo puede tener final bueno/normal/malo.
- Esto confirma que las filas del CSV en orden de offset probablemente siguen bastante
  bien el orden de aparicion narrativa (por capitulo), pero pueden mezclar personajes
  secundarios distintos por capitulo (ej. Kana/Megumi/Arisa parecen ser del capitulo de
  introduccion con Kokkuri-san, no necesariamente del elenco principal).

Fuente: https://ja.wikipedia.org/wiki/%E3%83%88%E3%83%AF%E3%82%A4%E3%83%A9%E3%82%A4%E3%83%88%E3%82%B7%E3%83%B3%E3%83%89%E3%83%AD%E3%83%BC%E3%83%A0_%E7%A6%81%E3%81%98%E3%82%89%E3%82%8C%E3%81%9F%E9%83%BD%E5%B8%82%E4%BC%9D%E8%AA%AC

## Terminos recurrentes (actualizacion filas 190-219)
- 神隠し (kamikakushi, "desaparicion misteriosa/espiritada"): se traduce como
  "que se la lleven/llevaron los espiritus" en frases verbales, y como
  "una desaparicion misteriosa" cuando se usa como sustantivo/pregunta formal.
  Fila 196 es una excepcion: el personaje esta deletreando la palabra letra por
  letra al reconocerla, asi que ahi se dejo el romaji "ka-mi...ka-ku-shi" en vez
  de la traduccion, para mantener el efecto de "reconociendo la palabra".
- ヒトダマ (hitodama, bola de fuego espiritual/fantasma): se dejo como "hitodama"
  sin traducir (termino de folclore japones, como Kokkuri-san).

## Progreso
- Filas 0-219 traducidas y verificadas (fila 0 = placeholder no traducible).
- Continua en fila 220 en adelante.

## Confirmacion de personajes (filas 250-279)
- "Riko" (リコ) aparece confirmado en el dialogo (fila 262) junto con Kana - efectivamente
  es Kagami Riko, del elenco principal, compartiendo escenas con el grupo de Kana/Megumi.
- Kana aparece como remitente de un correo en cadena que sorprende a otras (fila 265-266).
- Nanashi confirmado explicitamente como figura que "aparece" si se ignora la cadena
  (fila 271: "ナナシが現れ、闇に落ちる" = "aparece Nanashi y caes en la oscuridad").

## Progreso
- Filas 0-279 traducidas y verificadas.
- Continua en fila 280 en adelante.

## Confirmacion de trama (filas 280-309)
- Arisa, Megumi y Kana son las 3 estudiantes desaparecidas mencionadas en el resumen de
  Wikipedia (companeras de Mizuki/Riko que hicieron Kokkuri-san en el edificio viejo).
- Folclore japones mencionado, se mantiene el nombre sin traducir (son juegos/canciones
  reales, como Kokkuri-san):
  - "Kagome Kagome": cancion/juego infantil usado en un rito con espejos enfrentados.
  - "kitsune no yomeiri" (bodas del zorro): fenomeno de lluvia con sol, asociado a zorros.
  - "Toryanse": cancion infantil usada como contra-ritual al ver muchos hitodama.
- ケンガイ (kengai, jerga de "圏外" = sin señal/fuera de cobertura): traducido como
  "perder la señal" para mantener naturalidad.

## Progreso
- Filas 0-309 traducidas y verificadas.
- Continua en fila 310 en adelante.

## Confirmacion adicional (filas 310-429)
- Nombres completos confirmados tal como aparecen en el CSV: "Kagami Riko" (fila 381),
  "Izumi Reika" (fila 411) - coinciden exactamente con Wikipedia.
- "Hanako-san" (花子さん): referencia al fantasma clasico japones "Hanako del baño"
  (leyenda urbana muy conocida de escuelas japonesas) - se mantiene el nombre sin
  traducir, como con Kokkuri-san.

## Progreso
- Filas 0-429 traducidas y verificadas.
- Continua en fila 430 en adelante.

## Confirmacion adicional (filas 430-519)
- "Kirizuka" (桐塚高等学校 = Colegio/Instituto Kirizuka): nombre del colegio, confirmado
  en fila 512, coincide con Wikipedia (instituto al que se transfirio Mizuki).
- Profesor "Hayashi" (ハヤシ) mencionado como profesor/tutor de curso (fila 498) - nombre
  propio, no traducir.

## Progreso
- Filas 0-519 traducidas y verificadas.
- Continua en fila 520 en adelante.

## Progreso
- Filas 0-639 traducidas y verificadas.
- Continua en fila 640 en adelante.

## Confirmacion adicional (filas 640-699)
- "Hitori Kakurenbo" (ひとりかくれんぼ, "escondidas tu sola"): confirmado el nombre del
  ritual/leyenda del capitulo 4. Se mantiene sin traducir, como Kokkuri-san.
- Kagami Riko confirmada explicitamente como "experta en historias de terror" (fila 678),
  coincide con su descripcion en Wikipedia.
- Variante de adivinacion con "Angel-san" y "Cupido-sama" (fila 687) - nombres de
  entidades invocadas, no traducir.
- IMPORTANTE - caracteres no disponibles: recordar que ni tildes NI la dieresis (u) estan
  disponibles. Palabras como "verguenza" que normalmente llevan u con dieresis
  (vergüenza) hay que evitarlas o reformular (se uso "vergonzoso" en su lugar).

## Progreso
- Filas 0-699 traducidas y verificadas.
- Continua en fila 700 en adelante.

## Progreso
- Filas 0-819 traducidas y verificadas.
- Continua en fila 820 en adelante.

## Progreso
- Filas 0-909 traducidas y verificadas.
- Continua en fila 910 en adelante.

## Progreso
- Filas 0-1059 traducidas y verificadas.
- Continua en fila 1060 en adelante.
- Se probaron tandas de 50 filas por vez (en vez de 30) sin problemas.

## Progreso
- Filas 0-1159 traducidas y verificadas.
- Continua en fila 1160 en adelante.

## Progreso
- Filas 0-1259 traducidas y verificadas.
- Continua en fila 1260 en adelante.

## Progreso
- Filas 0-1409 traducidas y verificadas. Continua en fila 1410 en adelante.

## Confirmacion adicional (filas 1410-1709)
- Izumi Reika: apellido de Reika confirmado (泉レイカ).
- Hayakawa Mizuki: apellido de Mizuki confirmado (２組のハヤカワ…ミズキ).
- 鬼門 (kimon, direccion/punto maldito en feng shui japones) se tradujo como
  "la direccion maldita" de forma consistente.
- Kirizuka (桐塚): nombre de lugar/barrio, no se traduce.
- Murasaki Kagami (ムラサキカガミ): leyenda urbana del "espejo purpura", nombre
  propio sin traducir (ver tambien Murasaki Babaa en filas anteriores).
- kamikakushi (神隠し, "desaparicion misteriosa/rapto por espiritus") se
  mantiene como termino japones, igual que otros terminos de folclore.

## Progreso
- Filas 0-1709 traducidas y verificadas. Continua en fila 1710 en adelante.

## CORRECCION IMPORTANTE - tabla de anchos (fila 1710 en adelante)
Se detecto que la tabla de anchos por letra usada en los scripts de verificacion de
los lotes anteriores (hasta fila 1709) no coincidia exactamente con la tabla oficial
de guia_traduccion_csv.md. La tabla oficial es mas chica por letra (ej. 'A' vale 10+1=11,
no 14 como se uso antes), asi que los lotes anteriores fueron MAS estrictos de lo
necesario (nunca se supero el limite real, solo se acorto de mas en algunos casos).
Desde la fila 1710 en adelante se usa la formula oficial exacta de la guia:
  anchos = {'A':10,'B':10,'C':10,'D':11,'E':9,'F':9,'G':11,'H':11,'I':5,'J':6,'K':11,'L':8,
  'M':14,'N':11,'O':12,'P':10,'Q':12,'R':10,'S':10,'T':9,'U':11,'V':10,'W':15,'X':10,'Y':10,
  'Z':10,'a':9,'b':10,'c':8,'d':10,'e':9,'f':6,'g':10,'h':10,'i':4,'j':5,'k':9,'l':4,'m':14,
  'n':10,'o':9,'p':10,'q':10,'r':7,'s':8,'t':6,'u':10,'v':9,'w':12,'x':9,'y':9,'z':8,'Ñ':9,'ñ':8}
  ancho_linea(linea) = suma de (6 si es espacio, sino anchos.get(ch,10)+1) por cada caracter.
  Limite seguro: <=220px por linea, sin limite de cantidad de lineas por texto.
- 2時すぎ…ウシミツドキ (fila 1800): "ushimitsudoki" (hora del buey, ~2-2:30am,
  tradicionalmente asociada a apariciones/rituales en Japon) se tradujo como
  "la hora del buey" (termino literal, se explica por contexto de horror).
- Sakurai Yuuta, Hayakawa Mizuki confirmados con apellido en dialogo.
- Masaki: nombre de otro companero de clase (sin apellido confirmado aun).

## Progreso
- Filas 0-1859 traducidas y verificadas. Continua en fila 1860 en adelante.

## Progreso
- Filas 0-2009 traducidas y verificadas. Continua en fila 2010 en adelante.

## Confirmacion adicional (filas 2010-2159)
- Kagami Riko: nombre completo confirmado (２年１組のカガミリコ = "Kagami Riko,
  de segundo grado clase uno"). Apellido Kagami, no confundir con la leyenda
  "Murasaki Kagami" (espejo, no persona).
- ウシミツドキ (ushimitsudoki, ~2-2:30am) se sigue traduciendo como "la hora del buey".
- Contexto historico revelado en dialogos: el edificio viejo (旧校舎) habria sido
  morgue/deposito de cadaveres durante la guerra (bombardeos de Tokio, gran
  terremoto de Kanto), con espiritus de esa epoca sin descansar en paz.

## Progreso
- Filas 0-2159 traducidas y verificadas. Continua en fila 2160 en adelante.

## Confirmacion adicional (filas 2160-2309)
- Seno Masaki: apellido de Masaki confirmado (セノマサキ, estrella del club de natacion).
- Takimoto Arisa: apellido de Arisa confirmado (タキモトアリサ).
- Toryanse (とおりゃんせ): otra cancion infantil japonesa con leyenda asociada
  (cantarla evita el kamikakushi), se mantiene sin traducir como nombre propio,
  igual que Kagome Kagome.
- anillo de Landolt (ランドルト環): referencia real (simbolo "C" de examenes de vista),
  se tradujo el termino tecnico real en vez de dejarlo en japones.

## Progreso
- Filas 0-2309 traducidas y verificadas. Continua en fila 2310 en adelante.

## Mejora de metodo (desde fila 2310)
Para oraciones largas, en vez de insertar los saltos de linea a mano (propenso a
errores de calculo), ahora se escribe la traduccion como una sola oracion en
espanol y se aplica un wrap automatico por palabras usando ancho_linea() (la
formula oficial de la guia) para cortar antes de superar 220px. Reduce
drasticamente los errores de "una linea se paso del limite".
Kirizuka (桐塚) confirmado tambien como nombre de la secundaria (桐塚高校 =
"secundaria Kirizuka"), ademas de nombre de barrio/lugar.

## Progreso
- Filas 0-2459 traducidas y verificadas. Continua en fila 2460 en adelante.

## Confirmacion adicional (filas 2460-2609) - nuevo capitulo
- Nuevo capitulo ambientado en Dream Park (parque de diversiones) y luego en un
  apartamento/edificio "Heights Kirizuka" (ハイツ桐塚).
- Kurata Yumiko (倉田裕見子): nombre de una victima/inquilina anterior del
  cuarto 103, ligada a una historia de asesinato.
- "Hitori Kakurenbo" (ひとりかくれんぼ, "escondidas tu solo"): ritual/leyenda
  urbana japonesa real, se mantiene sin traducir como nombre propio (igual que
  Kokkuri-san). Involucra un peluche, una taza con agua y palillos, papel de
  aluminio (protector) y un "oni" (demonio) que aparece si se hace mal.
- Filas 2470, 2471: texto con caracteres de control ilegibles (similar a la fila 0),
  marcadas como "[REVISAR ROM - texto ilegible/corrupto, posible efecto del
  juego]" en vez de traducidas — posiblemente sea un efecto intencional de
  "texto corrupto" del juego (tema recurrente de 文字化け/mojibake como
  fenomeno paranormal), no necesariamente un error de extraccion. Fila 2472
  tenia el mismo problema pero con un fragmento legible ("88-09"), se tradujo
  solo esa parte marcandola como [TEXTO PARCIAL].
- Minijuegos nuevos: montaña rusa/tren con freno de curva, apilar objetos,
  sujetar una puerta, girar una piedra con el lapiz tactil — instrucciones
  traducidas de forma literal/funcional (son textos de tutorial de UI, no dialogo).

## Progreso
- Filas 0-2609 traducidas y verificadas. Continua en fila 2610 en adelante.

## Confirmacion adicional (filas 2610-2759)
- "Nirameko" (にらめっこ, juego infantil de "a ver quien se rie primero" /
  concurso de miradas): se tradujo el sentido ("concurso de miradas") en vez de
  dejarlo en japones, ya que no es un nombre propio de leyenda sino un juego
  comun. La rima asociada "…わらうとまけよ" = "si te ries, pierdes".
- Juego de palabras con numeros de telefono (goroawase): 4219 = "shiniiku"
  ("voy a morir"), 4771 = "shinanai" ("no voy a morir"). Se dejaron los numeros
  y su lectura fonetica entre comillas tal como en el original.
- "Heights Kirizuka" (ハイツ桐塚): nombre del edificio/departamento, ligado a
  la leyenda urbana "El hombre debajo de la cama".

## Dudas abiertas para el traductor humano
- Filas 2641, 2643, 2644: "イオゴク", "テンゴク", "ジュウゴク" — parecen ser
  opciones de un menu/minijuego relacionado con los numeros telefonicos con
  juego de palabras (2643=テンゴク parece ser "Tengoku"=Cielo/天国, se tradujo
  como tal). Las otras dos (イオゴク, ジュウゴク) no se pudo determinar su
  significado con el contexto disponible — se dejaron sin traducir tal cual
  el japones original. Revisar si son variantes fallidas/incorrectas de
  "jigoku" (地獄, infierno) al marcar numeros mal.
- Fila 2669: contiene los mismos caracteres de control ilegibles que las filas
  2470-2471 y la fila 0 (posible efecto de "texto corrupto" del juego), se
  tradujo solo la parte legible entre parentesis.

## Progreso
- Filas 0-2759 traducidas y verificadas. Continua en fila 2760 en adelante.

## Confirmacion adicional (filas 2760-2909) - nuevo capitulo
- Nuevo capitulo: estacion de tren abandonada "Higashi-Kirizuka" (東桐塚駅,
  Estacion Higashi-Kirizuka) y un tren fantasma.
- Sakuma (サクマ): personaje nuevo, ex-empleado de la estacion ("元駅員さん"),
  habla con pronombre わし (tipico de hombre mayor) -> se tradujo su forma de
  hablar de manera neutra ("Yo soy Sakuma") sin marcador especial de "anciano"
  en espanol (el alfabeto disponible no permite matices como "servidor").

## Progreso
- Filas 0-2909 traducidas y verificadas. Continua en fila 2910 en adelante.

## Confirmacion adicional (filas 2910-3059)
- Nueva estacion mencionada: "Mitsuya Koen" (三ツ谷公園駅, estacion Mitsuya
  Koen), parte de la linea fantasma junto a Higashi-Kirizuka.
- Subtrama "bebe abandonado en un casillero" (コインロッカーベビー): una mujer
  relacionada con un bebe abandonado/muerto en un casillero de estacion.
- Pista de acertijo "ガクブチ　ノ　ウラ" traducida como "DETRAS DEL MARCO"
  (marco de fotografia).

## Progreso
- Filas 0-3059 traducidas y verificadas. Continua en fila 3060 en adelante.

## Confirmacion adicional (filas 3060-3359)
- Nanaka (ナナカ): nueva compañera de clase de las protagonistas, hospitalizada/
  en enfermeria tras un accidente en la estacion Higashi-Kirizuka.
- Se usa "Jizo" como nombre propio (no traducido) para 地蔵 (お地蔵さん), estatuas
  guardianas budistas encontradas en tuneles/santuarios del capitulo del tren.
- Confirmado nombre "linea Edogawa" (江戸川線) como la linea de tren del capitulo
  del tren fantasma, con su propia "maldicion" segun los personajes.
- Leyenda urbana nueva: "El padre eres tu" (『親はおまえだ！』) ligada a la
  subtrama del bebe abandonado en el casillero.

## Progreso
- Filas 0-3359 traducidas y verificadas. Continua en fila 3360 en adelante.

## Confirmacion adicional (filas 3360-3659)
- Nuevo capitulo/leyenda: "Yumiko" (ゆみこ/ユミコ), ligada a un juego de
  hitorikakurenbo/muñeca (見つけた／見いつけた = "Te encontre", frase ritual de
  la muñeca que busca; se tradujo siempre igual para mantener el eco de terror).
- ハヤカワさん traducido como "Senorita Hayakawa" (apellido ya confirmado:
  Hayakawa Mizuki).
- ユカリ先生 (profesora/maestra Yukari): personaje nuevo, docente mencionado.
- もしもし (saludo telefonico) traducido como "Alo..." (uso latinoamericano).

## Progreso
- Filas 0-3659 traducidas y verificadas. Continua en fila 3660 en adelante.

## Confirmacion adicional (filas 3660-3809)
- Confirmado nombre completo: Kurata Yumiko (倉田裕見子) — la "Yumiko/ゆみこ"
  del capitulo anterior, victima de asesinato.
- "Hitori Kakurenbo" (ヒトリカクレンボ) aparece explicito como nombre del
  ritual, se mantiene sin traducir (igual que Kokkuri-san).
- 次はあなたがオニ (juego de a las escondidas): "オニ" = quien busca/atrapa,
  traducido conceptualmente como "el que busca" en vez de literal "demonio".

## Progreso
- Filas 0-3809 traducidas y verificadas. Continua en fila 3810 en adelante.

## Confirmacion adicional (filas 3810-3959)
- Peluche/muñeco llamado "Kumazou" (クマゾウ), nombre propio mantenido.
- Subtrama del "acosador" (ストーカー) y su posible asesinato, ligada al
  capitulo de Yumiko/Hitori Kakurenbo.
- Menciones a "el dueño del edificio" (大家さん) y cuarto 103 (１０３号室).

## Progreso
- Filas 0-3959 traducidas y verificadas. Continua en fila 3960 en adelante.

## Progreso
- Filas 0-4109 traducidas y verificadas. Continua en fila 4110 en adelante.

## Progreso
- Filas 0-4259 traducidas y verificadas. Continua en fila 4260 en adelante.

## Confirmacion adicional (filas 4260-4409)
- Capitulo del ritual "Hitori Kakurenbo" con pasos numerados (2,4,5,6,7,9,13...)
  detallando el procedimiento con el peluche Kumazou, arroz, cuchillo, agua
  salada, television en estatica, etc. Se tradujeron los pasos en tono de
  instrucciones directas ("Hacer esto...").

## Progreso
- Filas 0-4409 traducidas y verificadas. Continua en fila 4410 en adelante.

## Confirmacion adicional (filas 4410-4559)
- Confirmado: Yumi-chan / ユミちゃん (diminutivo carinoso de Kurata Yumiko),
  vivia en el cuarto 103 del edificio "Heights Kirizuka", vecina/amiga de una
  de las protagonistas antes de morir.
- Profesor Yagi (八木先生) mencionado como docente del colegio/reunion de
  ex alumnos.
- Confirmado que el asesino de Yumiko era residente del mismo edificio y su
  ex pareja/acosador.

## Progreso
- Filas 0-4559 traducidas y verificadas. Continua en fila 4560 en adelante.

## Confirmacion adicional (filas 4560-4709)
- Cierre del capitulo "El hombre debajo de la cama" / leyenda urbana ligada
  al edificio de Kurata Yumiko: se revela que Yumiko (convertida en espiritu/
  posiblemente viva) fue quien realmente mato al acosador, y que ella misma
  se convirtio en el origen de la leyenda urbana.
- Fila 4698 "←広場" es una etiqueta de mapa/interfaz: traducida como "<- Plaza".
- Nuevo capitulo corto iniciando fila 4682 con interjecciones breves.

## Progreso
- Filas 0-4709 traducidas y verificadas. Continua en fila 4710 en adelante.

## Confirmacion adicional (filas 4710-4859)
- Nuevo capitulo: parque de diversiones abandonado ("el parque de diversiones
  de los suenos" / 夢の遊園地), con atracciones: rueda de la fortuna
  (観覧車), casa embrujada (お化け屋敷), casa de espejos (ミラーハウス),
  atraccion de guillotina.
- Personaje nuevo: Senor Hasegawa (ハセガワさん).
- Tema del "papa" (親父) fallecido de un personaje (probablemente Masaki o
  Yuuta), ligado al parque.

## Progreso
- Filas 0-4859 traducidas y verificadas. Continua en fila 4860 en adelante.

## Confirmacion adicional (filas 4860-5009)
- Hasegawa es hijo del dueno del parque "Dream Park" (ドリームパーク), cuyo
  padre (親父) fallecido dejaba bromas/acertijos por el parque (una caja
  fuerte, maquetas, etc). El payaso fantasma esta ligado a este padre.

## Progreso
- Filas 0-6652 traducidas y verificadas. TRADUCCION COMPLETA (6653/6653 filas, salvo fila 0 y filas 6651-6652 que son placeholders binarios no traducibles, marcados para revision de ROM).


## Confirmacion adicional (filas 5160-5459) - capitulo Dream Park
- Hasegawa es el hijo del dueno fallecido de Dream Park; su padre (親父, tratado como
  "mi viejo") tenia el lema de que "lo divertido, hacerlo aun mas divertido", y
  dejaba acertijos/bromas por el parque (modelos hechos a mano, caja fuerte,
  mensajes en la oscuridad, etc).
- El payaso fantasma esta ligado al espiritu del padre de Hasegawa; su obsesion con
  sorprender/asustar a la gente parece haberse manifestado en esa forma tras morir.
- "kimon" (鬼門, direccion asociada a mala suerte en la tradicion japonesa) se tradujo
  como "la direccion maldita" para mantener naturalidad sin usar terminologia oscura.
- Los letreros de direccion dentro del parque (flechas de navegacion tipo mapa) se
  adaptaron con guiones/simbolos ASCII ya que el juego no soporta caracteres de flecha.


## Confirmacion adicional (filas 5760-6059) - capitulo escolar/Nanashi/Kuchisake-onna
- Nuevo arco: cadena de mensajes de "Nanashi" (sin nombre) y el ritual de las
  "Cien historias de leyendas urbanas" (都市伝説百物語), relacionado con la
  desaparicion de Riko en la escuela de noche.
- 口裂け女 (Kuchisake-onna, la mujer de la boca rasgada) aparece como leyenda
  urbana clasica; se tradujo descriptivamente como "la mujer de la boca
  rasgada" en vez de dejar el termino en japones, ya que no es un nombre propio
  fijo sino una leyenda que se explica en el dialogo mismo.
- Yukari-sensei y Hayakawa (apellido de Mizuki) confirmados como personajes
  recurrentes en este capitulo.


## Confirmacion adicional (filas 6210-6359)
- Hanako-san (トイレの花子さん) aparece mencionada como la leyenda urbana clasica
  del fantasma del bano escolar; se mantiene como nombre propio ("Hanako-san").
- Jibakurei (地縛霊, espiritu atado a un lugar/terreno que no puede descansar en
  paz) se tradujo descriptivamente en vez de dejar el termino en japones.
- Hasegawa Yukari confirmada como nombre completo de Yukari-sensei (profesora
  de primer ano).


## Confirmacion adicional (filas 6510-6652) - cierre de la historia
- Ultimo tramo: revelacion sobre Yukari-sensei (Hasegawa Yukari), lista de
  nombres de companeros (Morimoto, Hara, Kurita, Arase, Kanzaki), y nombres de
  ubicaciones del juego (mapas de la escuela vieja/nueva, Dream Park, estacion
  Higashi-Kirizuka, estacion Mitsuya Koen, etc.) traducidos de forma
  descriptiva ("Pasillo sur del 2do piso del edificio nuevo", etc.) ya que
  son etiquetas de ubicacion en el menu/mapa del juego, no dialogo.
- Textos de sistema (guardar/cargar/inicializar partida) traducidos de forma
  estandar para un RPG/aventura.
- Filas 6651 y 6652 son bytes ilegibles/placeholder (igual que la fila 0) y
  se marcaron como "[REVISAR ROM - texto original ilegible/placeholder, no
  traducido]" en vez de traducirse.

## TRADUCCION COMPLETA
Las 6653 filas del guion han sido procesadas. Quedan pendientes de revision
manual unicamente las filas 0, 6651 y 6652 (placeholders binarios, no texto
de juego real).


## Revision de neutralidad del espanol (post-traduccion completa)
Se reviso todo el guion (6653 filas) buscando argentinismos/rioplatensismos
que se habian colado pese al criterio de tuteo neutro. Casos encontrados y
corregidos (11 filas):
- "re" como intensificador -> "muy" (fila indice 488).
- "un monton" -> "bastante" (fila 491).
- "nomas" (5 casos) -> "sin mas", "es todo", "nada mas", "y ya", "como
  asi" segun el contexto (filas 1067, 1311, 1456, 4140, 6133).
- "aca" -> "aqui" (3 casos, filas 175, 188, 5859).
- "viste" como muletilla de confirmacion al final de frase (rioplatense) ->
  se reemplazo por "no?" (fila 5280). Nota: otros usos de "viste" en el
  guion son la conjugacion correcta de "ver" en preterito para "tu" ("tu
  viste algo", "te viste envuelta") y NO son regionalismos, se dejaron
  intactos.
- Se revisaron ademas posibles conjugaciones voseo (tenes, queres, podes,
  sos, veni, deci, etc.) y palabras como quilombo, boludo, che, posta, bardo,
  zarpado, laburo, pibe/piba, guita, chabon, boliche, remera, plata, joda,
  careta, trucho, pavada, macana, mina, chamuyo, atorrante, zafar, bronca,
  garca, fijate: no se encontro ningun caso en las 6653 filas.
- Todas las correcciones se re-verificaron con el script de ancho de linea
  (ancho_linea/wrap, limite 220px): 0 problemas.
