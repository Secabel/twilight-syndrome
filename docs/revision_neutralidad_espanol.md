# Revisión: neutralizar argentinismos en la traducción (guion_principal.csv)

Al jugar la build actual se notaron expresiones marcadamente rioplatenses/argentinas en la traducción. El objetivo es pasar todo el guion (6646 líneas traducidas) a un español neutro, sin perder el tono coloquial/juvenil del original (son diálogos de estudiantes de secundaria, así que informal está bien — el problema es que sea *demasiado local* de una sola región).

## Casos ya detectados (vía búsqueda por palabras clave)

| offset_hex | texto actual | problema | sugerencia |
|---|---|---|---|
| 0xd6400 | "Dicen que es re grave." | "re" como intensificador | "Dicen que es muy grave." |
| 0xd6448 | "Eso tambien, un monton......" | "un montón" muy coloquial rioplatense | "Eso tambien, bastante......" |
| 0xd9a48 | "Volver asi nomas" | "nomás" | "Volver asi sin mas" / "Volver asi como asi" |
| 0xdabf0 | "Eeh, eso nomas?" | "nomás" | "Eeh, eso es todo?" / "Eeh, solo eso?" |
| 0xf4100 | "Eh? No puedo esperar afuera nomas?" | "nomás" | "Eh? No puedo esperar afuera y ya?" / "...simplemente afuera?" |
| 0x1039dc | "Crees que te voy a dar un dato tan jugoso asi nomas?" | "nomás" | "...asi como asi?" / "...tan facil?" |

Estas 6 son solo las que aparecieron con una búsqueda por palabra suelta (regex). Pueden faltar casos de **argentinismos de estructura** (no una palabra puntual, sino la construcción de la frase) que solo se detectan leyendo, por ejemplo:
- Uso de diminutivos o construcciones muy propias del Río de la Plata.
- Muletillas o formas de pregunta/exclamación muy locales.
- Cualquier "vos" + conjugación voseo que se haya colado (tenés, querés, sos, etc. — la búsqueda por palabra suelta dio 0 casos de "vos" explícito, pero convendría una relectura para verbos voseo sin el pronombre).

## Qué pedirle al chat de traducción

1. Releer las 6646 líneas traducidas (columna `traduccion` de `guion_principal.csv`) buscando específicamente:
   - Intensificadores/modismos marcados como argentinos ("re", "un montón", "nomás", "posta", "quilombo", "boludo", "che", "bardo", "zarpado", "groso", etc.)
   - Conjugación voseo (tenés, querés, podés, sos, vení, decí, mirá, andá, etc.) — cambiar a la forma "tú" neutra o a una forma que funcione para ambos (ej. "puedes" en vez de "podés"/"puedes tú").
   - Cualquier otra construcción que suene marcadamente de una sola región.
2. Reemplazar por una alternativa de **español neutro/panamericano**, manteniendo el registro informal/juvenil del diálogo original (no hace falta que sea "acartonado", solo evitar el sesgo regional).
3. Revisar también `docs/glosario_traduccion.md` por si el glosario de términos/lore quedó con alguna expresión regional que convenga ajustar para mantener consistencia.
4. Confirmar que el resultado sigue respetando las reglas de formato ya conocidas (sin tildes, sin ¿¡, saltos de línea `\n` dentro del presupuesto de ~220px por línea) — no debería cambiar nada de eso, pero conviene re-verificar después de editar texto.
5. Entregar el CSV actualizado con la columna `traduccion` corregida.

## Contexto técnico (por si se necesita)

El alfabeto disponible en el juego es: `A-Z a-z Ñ ñ 0-9 espacio . , ? ! ( ) - " : ' < ^` y `\n` manual. No hay tildes ni ¿¡ todavía. Esto no debería afectar la neutralización de modismos, pero cualquier palabra nueva que se use debe respetar ese set de caracteres.
