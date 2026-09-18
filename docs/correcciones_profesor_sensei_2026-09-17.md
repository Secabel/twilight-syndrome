# Correcciones adicionales: consistencia profesor/sensei — 2026-09-17 (segunda ronda)

Encontradas cruzando `docs/guia_traducida_con_offsets.md` (guia con contexto narrativo) contra el CSV, a pedido del usuario de usar ese contexto para detectar mas inconsistencias.

## guion_principal_esp.csv — 5 correcciones

先生 solo (sin nombre) se traducia mayormente "profesor/profesora" (24 instancias) pero 5 decian "sensei" sin traducir. Se dejo intacto "Yukari-sensei" (nombre+honorifico, 11 instancias, estilo consistente y valido).

| Offset | Antes | Ahora |
|---|---|---|
| `0x100038` | Sensei? | Profesor? |
| `0x1005b0` | ......Sensei. | ......Profesor. |
| `0x100ff4` | ...Por favor, sensei. | ...Por favor, profesor. |
| `0x101864` | ...Sensei... ayudeme... | ...Profesor... ayudeme... |
| `0x102d74` | Eh? Es que ahora, con el sensei... | Eh? Es que ahora, con el profesor... |

## guion_principal_eng.csv — 7 correcciones

Dos problemas encontrados:

1. Una instancia de "sensei" en minuscula que el fix anterior (regex `\bSensei\b`, case-sensitive) no capturo: `0x100ff4` -> "teacher".

2. Split de estilo para "Yukari" + 先生: "Ms. Yukari" en 6 lineas (offsets < 0x100000) vs "Yukari-sensei" en 11 lineas (offsets >= 0x100000) -- mismo patron de dos sesiones de traduccion sin reconciliar que ya se habia encontrado y corregido para 先生 solo. Se unifico a "Yukari-sensei" (mayoria, y coincide con el estilo ya aceptado en el CSV espanol).

| Offset | Antes | Ahora |
|---|---|---|
| `0x100ff4` | ...Please, sensei. | ...Please, teacher. |
| `0xda90c` | Ah, Ms. Yukari... | Ah, Yukari-sensei... |
| `0xe9a0c` | If I tell Ms. Yukari or Reika, they'll probably scold me, but... | If I tell Yukari-sensei or Reika, they'll probably scold me, but... |
| `0xeae1c` | Ms. Yukari...!? | Yukari-sensei...!? |
| `0xeaf10` | (No way! Ms. Yukari is everywhere...) | (No way! Yukari-sensei is everywhere...) |
| `0xf10a4` | ...Ms. Yukari... | ...Yukari-sensei... |
| `0xf3f80` | (That's what Ms. Yukari said...) | (That's what Yukari-sensei said...) |

## Metodo usado

Se leyeron completos `docs/guia_traducida_con_offsets.md` y se empezo a cruzar `docs/mapeo_guia_gamefaqs.md` (guias de GameFAQs traducidas y cruzadas con offsets del CSV), que dan orden narrativo real y contexto de personaje/escena que el CSV plano (ordenado por offset) no tiene. Esto permitio confirmar con certeza que 先生 solo vs "Yukari"+先生 son dos casos distintos, y que la inconsistencia profesor/sensei no era aleatoria sino un corte limpio en el offset 0x100000 (dos sesiones de traduccion). Queda pendiente seguir cruzando el resto de `mapeo_guia_gamefaqs.md` (175 lineas, se leyeron ~30) por mas inconsistencias de este tipo.
