# Twilight Syndrome: Kinjirareta Toshi Densetsu (DS) — Spanish and English Fan Translation

Fan translation of **Twilight Syndrome: Kinjirareta Toshi Densetsu**
(トワイライトシンドローム 禁じられた都市伝説, XAX Entertainment / Spike, 2008)
for the Nintendo DS into **Spanish** and **English**. It is an urban-legend
horror mystery game where high school girls chase the rumors spreading around
their town (Kokkuri-san, Hitori Kakurenbo, chain mails from a sender called
Nanashi, and several legends original to this game). As far as we know, it had
no previous English or Spanish translation.

**Spanish**

<p>
<img src="images/es_01_title_menu.png" width="200" alt="Spanish screenshot: title menu">
<img src="images/es_02_dialogue.png" width="200" alt="Spanish screenshot: dialogue">
<img src="images/es_03_inventory.png" width="200" alt="Spanish screenshot: inventory">
<img src="images/es_04_phone_mail.png" width="200" alt="Spanish screenshot: phone mail">
</p>

**English**

<p>
<img src="images/en_01_rumor_card.png" width="200" alt="English screenshot: rumor card">
<img src="images/en_02_dialogue.png" width="200" alt="English screenshot: dialogue">
<img src="images/en_03_dialogue.png" width="200" alt="English screenshot: dialogue">
<img src="images/en_04_phone_mail.png" width="200" alt="English screenshot: phone mail">
</p>

> **Version 1.3**
> This repository does **not** contain the game. You need your own copy of the original Japanese ROM.

## What is translated

- **Full script** (over 6,600 lines of dialogue, menus and system messages),
  reinserted with a pointer-relocation scheme: the engine stores the whole
  script inside the ARM9 binary with hardcoded pointers, so longer translated
  lines are moved to free space instead of being squeezed in place.
- **Custom Latin font**: the original font only has kanji/kana and a handful of
  Latin letters. A full A-Z/a-z alphabet with Ñ/ñ, digits and punctuation was
  designed from scratch in the game's pixel style. The Spanish version also
  has accented vowels and ¿ ¡ *(new in 1.2)*.
- **Character name tags** and the **38 inventory item screens**, whose text is
  drawn directly into the graphics (NCGR/NCER) and was redrawn per language.
- **Menus with text baked into the graphics**: title screen, story/ending
  selection menu (45 cards across 6 story arcs), save/load menu and the rumor
  cards shown when loading each story.
- **Phone mails** *(new in 1.1)*: the chain mails received on the in-game cell
  phone (around 24 different mails, including the "problem" riddles) are
  sprites, not script text. They were redrawn with a new phone font that
  imitates the original LCD style.
- **Phone screens** *(new in 1.3)*: camera / recorder / save menu, "Save?"
  prompts, sending a mail, contacts, call screens, call history, audio
  playback, the "no signal" icon, the web page and the OK button on the
  wallpapers, redrawn with the same phone font.
- **Startup notices and save data error messages** *(new in 1.3)*.

## Playing the translation (patch users)

1. Get the original ROM and check it matches:

   | File | Size | CRC32 | SHA-1 |
   |---|---|---|---|
   | `Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds` | 134,217,728 bytes | `76F1DB67` | `129880d90ecc1b322255e56d4968b259a3e1aa15` |

2. Download the `.bps` patch for your language from the [Releases](../../releases)
   page: `Twilight.Syndrome.ESP.v1.3.bps` (Spanish) or
   `Twilight.Syndrome.ENG.v1.3.bps` (English).
3. Apply it to the original ROM with any BPS patcher (for example
   [Flips](https://github.com/Alcaro/Flips) or
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)).
   Flips may warn that the original ROM is larger than the result: that is
   expected, because the original dump contains padding that the patched ROM
   does not keep.
4. Expected result:

   | Patch | Result | Size | CRC32 | SHA-1 |
   |---|---|---|---|---|
   | `Twilight.Syndrome.ESP.v1.3.bps` | Spanish | 116,256,968 bytes | `C547AD28` | `a7ba6b788a82030b1d5e594833d8925ccc285ad7` |
   | `Twilight.Syndrome.ENG.v1.3.bps` | English | 116,213,448 bytes | `E6C49839` | `b31cde8b17fc725b4a074432396a91e845dfb1a8` |

Tested in [melonDS](https://melonds.kuribo64.net/) and on a real New 3DS.

**Updating from an earlier version:** your in-game save (`.sav`) keeps working,
but do **not** load emulator savestates made with an older ROM: a savestate
stores the graphics and text already loaded in memory, so old text can reappear.

## Building the ROMs from source

This is only needed if you want to regenerate the ROMs yourself or modify the
translation. If you just want to play, use the patches above.

1. **Get this repository** (`git clone https://github.com/Secabel/twilight-syndrome.git`,
   or "Download ZIP" on GitHub and extract it). It already includes the
   translation CSVs, the font and all the redrawn graphics.
2. **Install the tools:** [Python 3](https://www.python.org/downloads/) and the
   packages `ndspy` and `Pillow`:

   ```
   pip install ndspy pillow
   ```

3. **Copy your original ROM** into the repository folder, named exactly
   `Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds` (see the
   checksums above).
4. **Run, from that folder:**

   ```
   python generar_rom_esp.py     # Spanish -> Twilight Syndrome - ESP.nds
   python generar_rom_eng.py     # English -> Twilight Syndrome - ENG.nds
   ```

The results should match the checksums listed above.

To edit a phone mail, change its text in `assets/csv/correos_celular.csv`,
run `python scripts/redibujar_correos.py` (it rebuilds
`assets/graficos/{esp,eng}/R08/` from the original ROM) and then the two
generators again. The rest of the phone screens, the startup notices and the
save error messages are rebuilt the same way with
`python scripts/redibujar_ui_celular.py` (texts are inside the script).

## Repository contents

| File / folder | What it is |
|---|---|
| `generar_rom_esp.py`, `generar_rom_eng.py` | Build the Spanish / English ROM from the original ROM and `assets/` |
| `assets/csv/guion_principal_esp.csv`, `assets/csv/guion_principal_eng.csv` | Main script: one row per line, with the ROM offset, the original Japanese text and the translation |
| `assets/csv/correos_celular.csv` | Phone mails: one row per sprite line (Japanese, Spanish, English) |
| `assets/font/TWSFont_v23.NFTR` | Game font used by the Spanish build: Latin glyphs plus á é í ó ú Á É Í Ó Ú ü ¿ ¡ |
| `assets/font/TWSFont_v22.NFTR` | Game font used by the English build (same Latin glyphs, without the Spanish accents) |
| `assets/graficos/esp/`, `assets/graficos/eng/` | Redrawn graphics per language (same folder structure as the ROM); the generators apply everything they find there |
| `assets/graficos/*.NCGR`, `assets/graficos/I22S10.NCER` | Graphics shared by both languages (character name tags, extended item cell) |
| `scripts/extraer_texto.py` | Extracts the script from the ARM9 binary to CSV |
| `scripts/extraer_todos_items.py` | Extracts the inventory item texts |
| `scripts/ncer_decode.py` | Decoder for DS tile graphics (NCGR/NCLR/NCER/NSCR) |
| `scripts/fuente_celular.py`, `scripts/redibujar_correos.py` | Phone font and the script that redraws the phone mails |
| `scripts/redibujar_ui_celular.py`, `scripts/nftr.py` | Redraws the other phone screens, the startup notices and the save error messages |
| `images/` | Screenshots used in this README |

The Japanese script is included in the main CSVs (`texto_original` column),
so the files can also be used as a starting point for a translation into
another language.

## Known issues

- **Mail photos inside some cutscenes** (blurry or tilted shots of the phone)
  keep their Japanese text; the same mails can be read translated on the phone.
- **Left untranslated on purpose:** the "touch the bottom screen" prompt on
  the title screen, the labels printed on the phone's physical keys, the staff
  credits, and a few props with text drawn into the background art
  (a puzzle sheet with a kana table, whose solution depends on the original
  characters, and a manual page that is not legible even in the original).
- With many routes and endings, not every route has been re-tested after
  every change. Some typos or inconsistencies may remain; reports are welcome
  in [Issues](../../issues).

## Version history

### 1.3
- Both languages updated; Spanish and English now share the same version
  number (English goes from 1.1 straight to 1.3).
- Translated the remaining phone screens: camera / recorder / save menu,
  "Save?" prompts and Yes/No, sending a mail and contact names, contact list,
  call screens, call history, number entry, audio playback, "no signal" icon,
  "page not found" web page and the OK button on the phone wallpapers.
- Translated the startup notices (work of fiction / headphones recommended)
  and the save data error messages.
- Fixed 7 dialogue lines that were still shown in Japanese.

### 1.2
- Spanish: added á é í ó ú Á É Í Ó Ú ü ¿ ¡ to the font, built from the existing
  letters so they match the original style.
- Spanish: reviewed the whole script (over 4,200 lines) to add accents, opening
  ¿ ¡ and some missing ñ; a few lines were rewrapped or slightly reworded to
  fit the text boxes.
- Spanish: fixed about 40 short lines that were still shown in Japanese in 1.1
  because they used characters the font didn't have.
- English: unchanged (the 1.1 patch is included again in the 1.2 release).

### 1.1
- Translated the phone mails: all 12 mailbox sets (around 24 different mails,
  including the chain mails from Nanashi and the "problem" riddles), redrawn
  with a new font that imitates the phone's LCD style.
- Added the tools used for it (`scripts/fuente_celular.py`,
  `scripts/redibujar_correos.py`) and the mail text (`assets/csv/correos_celular.csv`).

### 1.0
- Initial public release: full script, custom font, name tags, inventory,
  menus and rumor cards in Spanish and English.

## Credits

- Translation and ROM hacking: **Talion**.
- Inventory and name-tag text drawn with DejaVu Sans Condensed
  ([DejaVu fonts license](https://dejavu-fonts.github.io/License.html)).
- Tools: [melonDS](https://melonds.kuribo64.net/), [ndspy](https://github.com/RoadrunnerWMC/ndspy),
  [Flips](https://github.com/Alcaro/Flips), Python and Pillow.

## License

The scripts and translation files in this repository are released under the
[MIT License](LICENSE). The license does not cover the game itself (see below).

## Legal

This is an unofficial fan project, not affiliated with or endorsed by the
original developers or publishers. *Twilight Syndrome: Kinjirareta Toshi
Densetsu* and all related rights belong to their respective owners. No game
data is distributed here: the patches only contain the differences from the
original ROM, which you must supply yourself.
