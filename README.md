# Twilight Syndrome: Kinjirareta Toshi Densetsu — Fan Translation

Spanish and English fan translation patch for **Twilight Syndrome: Kinjirareta
Toshi Densetsu** (トワイライトシンドローム 禁じられた都市伝説, XAX
Entertainment, 2008), a Nintendo DS urban-legend/horror mystery game where
high schoolers trade creepy stories about their town (Kokkuri-san, Hitori
Kakurenbo, Hanako-san, and several legends original to this game). As far as
we know, this is a standalone entry in the Twilight Syndrome series with no
prior English or Spanish translation (unlike Tansaku-hen/Kyuumei-hen on PS1,
which already have active translation projects elsewhere).

**Status: both Spanish and English translations are complete** — full script,
custom Latin font, character names, inventory item descriptions, and the
in-game menus that store text baked directly into image tiles (title screen,
story/ending selection menu, save/load menu) are all translated and
reinserted.

Prebuilt BPS patches (`Twilight Syndrome ESP.bps` / `Twilight Syndrome
ENG.bps`) are included in this repository, and are also listed on
[romhacking.net](https://www.romhacking.net/) once approved. Apply either one
with a BPS patcher (e.g. [Floating IPS](https://github.com/Alcaro/Flips))
over a clean Japanese ROM — or build your own patched ROM from source, see
below.

## What this covers

- **Full script** (6653 lines of dialogue) extracted, translated, and
  reinserted with a custom pointer-relocation scheme (the original engine
  embeds the whole script in the ARM9 binary with hardcoded pointers and no
  length field, so longer translated lines don't fit in place — relocated
  into unused RAM space instead).
- **Custom font**: the original NFTR font only ships kanji/kana glyphs plus a
  handful of pre-existing Latin letters. A full A-Z/a-z/Ñ/ñ alphabet plus
  accented characters (á é í ó ú ¿ ¡) and punctuation were designed from
  scratch and injected, matching the game's pixel style.
- **Inventory items** (38 item description screens) and **character name
  tags**: these are baked directly into tile graphics (NCGR/NCER), not part
  of the script CSV, so they're redrawn per language.
- **In-game menus with baked-in text**: the story/ending selection menu (45
  cards across 6 story arcs, with fortune results and gameplay hints) and the
  save/load menu (7 cards) also have Japanese text burned into the tile
  graphics rather than going through the normal font/script system — these
  were reverse-engineered and redrawn per language too.

## Repository layout

- `Twilight Syndrome ESP.bps` / `Twilight Syndrome ENG.bps` — ready-to-use
  BPS patches. Apply over a clean Japanese ROM with a BPS patcher.
- `scripts/` — Python tooling used to build the assets below from a clean
  Japanese ROM: `extraer_texto.py` (script/dialogue extraction to CSV),
  `extraer_todos_items.py` (inventory item text extraction), and
  `ncer_decode.py` (NCER/NCGR tile-graphics decoder).
- `assets/` — the actual translated assets (script CSV, custom font, redrawn
  graphics) that get patched into the ROM, split by language
  (`assets/graficos/esp/`, `assets/graficos/eng/`).
- `generar_rom_esp.py` / `generar_rom_eng.py` — build scripts that take a
  clean Japanese ROM + the assets above and produce a patched ROM.

## Building a patched ROM

You need your own legally-dumped copy of the original Japanese ROM — it is
**not** included in this repository. Clone this repository (it already
includes the translated `assets/` needed for the build), place the clean ROM
alongside the build scripts, then:

```bash
git clone https://github.com/Secabel/twilight-syndrome.git
cd twilight-syndrome
pip install ndspy
python3 generar_rom_esp.py   # or generar_rom_eng.py
```

## Contributing

If you're working on a translation into another language and want to reuse
the extraction/build pipeline (`scripts/`, `generar_rom_*.py`) as a starting
point, feel free to open an issue or PR.
