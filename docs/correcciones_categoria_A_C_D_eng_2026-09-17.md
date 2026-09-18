# Correcciones categoria A/C/D aplicadas a guion_principal_eng.csv — 2026-09-17

Mismo proceso ya aplicado al CSV en espanol (ver `correcciones_categoria_A_C_D_2026-09-17.md`), repetido de forma independiente sobre el CSV en ingles.

Total de filas modificadas: 42 de 6859.

## Unificaciones de categoria A (mismo texto JP, traduccion elegida = variante mas frecuente)

| Offset | Antes | Ahora |
|---|---|---|
| `0x1005bc` | Ah...... | Aah..... |
| `0x100b9c` | What does that mean? | What do you mean? |
| `0xd3474` | I know, I know. | I know that already. |
| `0xd3920` | Please keep / touching the center / coin. | Please keep touching the / center coin. |
| `0xd3944` | Please keep / touching the center / coin. | Please keep touching the / center coin. |
| `0xd3f14` | Are you okay? | You okay? |
| `0xd3f38` | Is that so? | Really? |
| `0xf0584` | Hmm... | Mmm... |
| `0xd3fa4` | It's no use... | It's no good... |
| `0x10099c` | Got it... | Understood... |
| `0xf1400` | Please come. | Please, come. |
| `0xd4bc8` | Touch the place you want / to investigate. | Touch the spot you want / to examine. |
| `0xd4bec` | Touch the place you want / to investigate. | Touch the spot you want / to examine. |
| `0xfa224` | Ah! | Ha! |
| `0xf0188` | Seriously? | Really? |
| `0xd5a4c` | Ha... | Ah... |
| `0xfa474` | You're right. | That's right. |
| `0xfa4bc` | You're right. | That's right. |
| `0x100628` | You're right. | That's right. |
| `0x10064c` | You're right. | That's right. |
| `0xf0848` | That's good. | What a relief. |
| `0xd5c74` | Mmm...... | Hmm...... |
| `0xebbdc` | Hmm... | Hmm...... |
| `0xd5cb4` | That's right... | You're right... |
| `0xf0180` | Wow. | Huh. |
| `0x100274` | ...Huh? | Huh? |
| `0x1000f4` | Huh?! | Ehh. |
| `0xd9e48` | Ah, I see... | I see... |
| `0xda0d8` | Ah, I see... | I see... |
| `0xf0f3c` | That's how it's done. | Now you're talking. |
| `0x107704` | ...What does that mean? | ...What do you mean? |
| `0xdac2c` | I told you, that's not it. | I told you that's not it. |
| `0xe8c90` | That's not it. | I told you that's not it. |
| `0xdb640` | I can't hear it anymore... | I stopped hearing it... |
| `0xdb5f8` | Could it be... Nanashi? | ...No way......Nanashi? |
| `0xf0248` | Next is... | Next up... |
| `0xf01ac` | Hmm. | Mmm. |
| `0xf1d4c` | (...What do I do...) | (...what do I do...) |
| `0xfa3fc` | Ah... | Ahh... |

## Correcciones puntuales (no solo mayoria de votos, verificadas con contexto)

| Offset | Antes | Ahora | Motivo |
|---|---|---|---|
| `0xf7064` | If you appear, please move towards Yes. | If it appears, please move towards Yes. | La linea gemela en 0xd5194 usa "if IT appears" (el espiritu/moneda), no "if YOU appear" (el jugador). Error de sujeto gramatical: el jugador no puede "aparecer" en un ritual de invocacion, quien aparece es el espiritu. |
| `0xeccbc` | Hey! Aren't you going to listen to what I'm saying! | Hey! Listen when I'm talking! | Mismo personaje (el viejo, primera persona "washi"), misma linea JP exacta repetida a pocas filas de distancia (0xecc14) durante la misma escena de la obra de expansion. Se unifico a la version mas corta y natural, ya usada en la otra instancia. |
| `0x100cbc` | What about / the / bathroom? (envuelto en 3 lineas) | What about / the bathroom? (envuelto en 2 lineas) | El salto de linea en 3 renglones dejaba la palabra "the" sola en su propia linea, un patron de wrap anomalo comparado con la instancia gemela en 0x100f4c que usa 2 lineas normales para el mismo texto exacto. |

## Casos NO unificados a proposito (dependen del contexto, no son errores)

| Texto JP | Variantes | Motivo |
|---|---|---|
| 大丈夫だって。 | I told you it's fine. / I'm telling you I'm fine. | Depende de quien habla (misma logica que la excepcion ya documentada en el CSV espanol para el mismo texto JP). |
| どうしよう…。 | What do we do... / What do I do... | Depende de si hay una o dos personas presentes en la escena (misma logica que la excepcion ya documentada en espanol). |
| ああ。 | Ah. / Yeah. | Interjeccion ambigua: "Yeah" cuando responde una pregunta de si/no, "Ah" cuando es una exclamacion suelta. Verificado en 3 contextos distintos, la variacion es funcional, no un error. |
| どうしたの？ | What's wrong? (22 instancias) / What's wrong with you? (4 instancias, agrupadas en una sola escena, offsets 0x1007ac-0x10092c) | Podria ser un tono deliberadamente mas tenso para esa escena especifica (contexto de un maniqui, ambiente inquietante) o una inconsistencia real. No se pudo determinar con certeza sin ver la escena jugada. PENDIENTE DE DECISION DEL USUARIO. |
| そんなこと…。 | That kind of thing... / That... | La version corta "That..." aparece justo despues de "...No way..." / "She is not here, is she?", podria ser una eleccion deliberada de ritmo mas entrecortado para ese momento emocional. Ambiguo, no se fuerza. PENDIENTE DE DECISION DEL USUARIO. |

## Hallazgo adicional: split de estilo "Teacher" vs "Sensei" (NO corregido, requiere decision del usuario)

先生 se traduce como "Teacher" en 5 lineas (offsets 0xd5d64, 0xdab50, 0xddd54, 0xe0890, 0xf023c — todas por debajo de offset 0x100000) y como "Sensei" en 4 lineas (offsets 0x100038, 0x10016c, 0x1005b0, 0x101864 — todas en o por encima de offset 0x100000). El corte es exacto en ese offset, lo que sugiere dos sesiones/pasadas de traduccion distintas que nunca se reconciliaron, en vez de una eleccion de estilo deliberada por personaje. Se deja sin tocar porque es una decision de estilo para el proyecto completo, no un error puntual.
