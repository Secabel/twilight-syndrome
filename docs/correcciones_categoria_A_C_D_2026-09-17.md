# Correcciones categorias A, C y D -- 2026-09-17

Registro auditable de las correcciones aplicadas a `assets/csv/guion_principal_esp.csv` tras terminar el mapeo completo de las categorias A-F (ver `docs/historia-proyecto.md` y el analisis de causas del proyecto). Cada fila: offset, texto japones, traduccion anterior, traduccion nueva, motivo.

Total de filas modificadas: **45** de 6859.

## Categoria A -- unificacion de inconsistencias (mismo texto japones, traduccion distinta segun el offset)

Se detectaron 35 grupos donde el mismo texto japones tenia mas de una traduccion distinta en el CSV. De esos 35, se corrigieron 32 (unificando a una sola traduccion). Los otros 3 grupos se dejaron sin tocar (ver tabla al final): al revisar el contexto de cada aparicion se vio que la diferencia de traduccion no es un error sino que responde a un sujeto gramatical distinto segun la escena -- forzar una sola traduccion ahi hubiera introducido un error nuevo.

| Offset | Texto original (JP) | Antes | Ahora |
|---|---|---|---|
| 0xd32ec | あぁ……。 | Aah..... | Ah...... |
| 0xd3474 | わかってるって。 | Ya se, ya se. | Ya lo se. |
| 0xd3920 | 中央のコインを触り続けて / ください。 | Por favor, sigan / tocando la moneda / del centro. | Por favor, sigan tocando / la moneda del centro. |
| 0xd3944 | 中央のコインを触り続けて / ください。 | Por favor, sigan / tocando la moneda / del centro. | Por favor, sigan tocando / la moneda del centro. |
| 0xd3f38 | そうなの？ | Es asi? | En serio? |
| 0xd3f68 | やめてよ。 | Basta. | Basta ya. |
| 0xd4bc8 | 調べたい場所をタッチ / してください。 | Toca el lugar que / quieras investigar. | Toca el lugar que quieras / revisar. |
| 0xd4bec | 調べたい場所をタッチ / してください。 | Toca el lugar que / quieras investigar. | Toca el lugar que quieras / revisar. |
| 0xd5194 | もし現れましたら、『はい』に / 進んでください。 | Si se presenta, / avance hacia el Si. | Si aparece, por favor / avance hacia el Si. |
| 0xd5974 | はっ！ | Ha! | Ah! |
| 0xd5a4c | はっ…。 | Ha... | Ah... |
| 0xd5cb4 | そうだね…。 | Es cierto... | Tienes razon... |
| 0xd8a2c | へえ。 | Ah. | Vaya. |
| 0xd8bc8 | …あれ？ | Eh? | ...Eh? |
| 0xd9e48 | そうなんだ…。 | Ah, ya veo... | Ya veo... |
| 0xda0c8 | そうこなきゃ。 | Asi se habla. | Asi se hace. |
| 0xda0d8 | そうなんだ…。 | Ah, ya veo... | Ya veo... |
| 0xda5c4 | …どういうこと？ | ...Que quieres / decir? | ...Que quieres decir? |
| 0xdac2c | それじゃないって。 | Te digo que no / es eso. | Te digo que no es eso. |
| 0xdaf68 | どうしたらいいの…。 | Que deberia / hacer... | Que deberia hacer... |
| 0xdb5f8 | …まさか……ナナシ？ | No sera... Nanashi? | ...No puede / ser......Nanashi? |
| 0xdb640 | 聞こえなくなった…。 | Ya no se oye / nada... | Deje de / escucharlo... |
| 0xe8ba8 | 次は…。 | Sigue... | Lo siguiente es... |
| 0xe8c90 | それじゃないって。 | Esa no es. | Te digo que no es eso. |
| 0xea4fc | （…どうしよう…） | (...que hago...) | (...Que hago...) |
| 0xeb854 | …えっ？ | Eh...? | ...Eh? |
| 0xebbdc | うーん……。 | Mmm... | Mmm...... |
| 0xeccbc | おい！わしの話を聞かんか！ | Oye! Acaso no vas a / escuchar lo que digo! | Oye! Escuchame cuando / hablo! |
| 0xf0848 | よかった。 | Que bueno. | Que alivio. |
| 0xfa444 | そうね。 | Es verdad. | Es cierto. |
| 0xfa474 | そうだね。 | Tienes razon. | Es cierto. |
| 0xfa4bc | そうだね。 | Tienes razon. | Es cierto. |
| 0x100088 | そう？ | Ah si? | En serio? |
| 0x1000f4 | ええっ。 | Eh?! | Eeh. |
| 0x10016c | 先生…。 | Sensei... | Profesor... |
| 0x100538 | それは…。 | Eso... | Eso es... |
| 0x1005e0 | そうなの？ | Ah si? | En serio? |
| 0x100628 | そうだね。 | Tienes razon. | Es cierto. |
| 0x10064c | そうだね。 | Tienes razon. | Es cierto. |
| 0x100b9c | どういうこと？ | Que significa esto? | Que quieres decir? |
| 0x107704 | …どういうこと？ | ...Que significa esto? | ...Que quieres decir? |

## Categorias C y D -- correcciones puntuales confirmadas

| Offset | Texto original (JP) | Antes | Ahora | Motivo |
|---|---|---|---|---|
| 0xd6b44 | …壁の…水道管…の音…？ | ...El sonido... / del cañeria / de la pared...? | ...El sonido... / de la cañeria / de la pared...? | C: concordancia de genero, "caneria" es femenino ("del" -> "de la") |
| 0xd6b60 | …壁の…水道管…の音…？ | ...El sonido... / del cañeria / de la pared...? | ...El sonido... / de la cañeria / de la pared...? | C: concordancia de genero, "caneria" es femenino ("del" -> "de la"), misma linea repetida en otro offset |
| 0xdcf68 | じゃ、先に図書室行ってるね。 | Bueno, yo me / adelanto a biblioteca. | Bueno, yo me / adelanto a la biblioteca. | C: faltaba el articulo "la" antes de "biblioteca" |
| 0xe4190 | （転校生だったわたしに、最初に / 　仲良くしてくれたっけ…） | (Fue la primera en ser / amable conmigo cuando / llegue nueva...) | (Fue la primera en ser / amable conmigo cuando / yo era la alumna nueva...) | D: calco de estructura ("llegue nueva" no es natural en espanol), reformulado |

## Casos de categoria A dejados sin tocar (no son errores reales)

| Texto japones | Traducciones distintas encontradas | Por que no se unifica |
|---|---|---|
| 大丈夫だって。| "Te digo que esta bien." / "Te digo que estoy bien." | Sujeto distinto segun quien habla en cada escena (el/ella vs yo) |
| どうしよう…。| "Que hacemos..." / "Que hago..." | Numero de hablantes distinto segun la escena (plural vs singular) |
| 発見されたんだって。| "Dicen que lo encontraron." / "Dicen que la encontraron." | Genero de a quien/que se refiere, distinto segun el contexto de cada escena |

