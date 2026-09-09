# Mapeo de caracteres — alfabeto latino en códigos de 1 byte reciclados

Se reutiliza el rango 0xA1–0xDF (63 códigos, originalmente katakana de ancho
medio, confirmado sin uso en la fuente ni en el guion real) para el alfabeto
latino que necesita la traducción.

## Fase 1 (alcance inicial acordado)

| Código      | Caracter(es)              |
|-------------|---------------------------|
| 0xA1–0xBA   | A–Z (26 mayúsculas)       |
| 0xBB–0xD4   | a–z (26 minúsculas)       |
| 0xD5        | Ñ                         |
| 0xD6        | ñ                         |
| 0xD7–0xDF   | libres (9 códigos de reserva) |

Decisión: por ahora se traduce sin tildes (á→a, é→e, etc.), priorizando avanzar
rápido. Si más adelante se quiere agregar acentos, hay 9 códigos libres de
sobra en este mismo rango — no hace falta rediseñar nada, solo dibujar los
glifos que falten y sumarlos al mapeo.

Los dígitos 0-9 y los signos de puntuación básicos (. , ! ? etc.) ya existen
en la fuente original (zenkaku/JIS estándar) y no necesitan recodificarse —
se siguen usando tal cual.

**Nota sobre la Ñ:** falta confirmar cómo se ve el glifo a la resolución real
de la fuente del juego (probablemente ~10-16px de ancho) antes de darla por
buena — la virgulilla (~) puede perderse en tamaños muy chicos. Se revisa
al generar los glifos.
