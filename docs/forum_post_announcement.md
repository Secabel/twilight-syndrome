[ES→EN Fan Translation] Twilight Syndrome: Kinjirareta Toshi Densetsu (NDS)

Hey everyone,

I'm working on a Spanish (and eventually English) fan translation of **Twilight Syndrome: Kinjirareta Toshi Densetsu** for the Nintendo DS — the urban-legend/horror mystery game where high schoolers trade creepy stories about their town (Kokkuri-san, Kuchisake-onna, Hanako-san, and a bunch of original legends specific to this game). As far as I know it's never had an English or Spanish translation before, so figured I'd share progress here.

**Where things stand:**

- Full script extracted and dumped to CSV (6653 lines of dialogue).
- Spanish translation: **complete** — every line translated, with a glossary doc covering character names, location names, and lore-specific terminology for consistency.
- Custom Latin font built from scratch: the original font only has kanji/kana glyphs plus a handful of pre-existing Latin letters, so I had to design and inject a full A-Z/a-z/Ñ/ñ alphabet (plus punctuation the original never needed, since it only used full-width Japanese punctuation) into the NFTR font resource, matching the game's pixel style as closely as possible.
- Text reinsertion: solved the "translated text is longer than the original" problem — the game embeds the whole script directly in the ARM9 binary with hardcoded pointers and no length field, so overflowing text isn't a simple find-and-replace. Ended up relocating the translated lines into unused main RAM space (well past the game's actual .bss boundary, so nothing gets overwritten at boot) and repointing everything from there. First full-script test build is running now.
- Currently doing playtesting to make sure the new text holds up across different scenes/menus, not just a handful of sample lines.

**Next steps:** finish QA on the Spanish version, then look at accented characters (á é í ó ú, ¿ ¡) which aren't in yet, and start scoping an English translation using the same pipeline once the Spanish build is stable.

Happy to answer questions about the ROM-hacking side (font/NFTR structure, pointer tables, RAM layout) if anyone's curious or working on something similar. Screenshots to follow once I've got a clean testing pass done.

P.S. For anyone following my other projects: the Terrors (WonderSwan) translation is active and currently in QAT, and Terrors 2 is active but on pause for a while.
