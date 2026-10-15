Fan translation of Twilight Syndrome: Kinjirareta Toshi Densetsu (Nintendo DS) into Spanish and English. The full script, menus, inventory, name tags, phone mails and phone screens are translated in both languages, and 1.4 now also covers most of the remaining menu graphics.

## What's new in 1.4
Spanish and English (both patches are updated):

- Translated the 7 story intro posters shown before each story (arc name and rumor label), which were vertical Japanese text baked into the image.
- Translated the item menu buttons: Back / Use / Look / Close / Zoom +/-.
- Translated the save / load screen: title (Save / Load), Back button and slot numbers 1-6.
- Translated the collectibles menu: about 100 place-name and rumor text bars ("Rumor N No.XX" with Great / Fair / Bad luck) and its Back button.

## Download
- `Twilight.Syndrome.ESP.v1.4.bps` - Spanish patch
- `Twilight.Syndrome.ENG.v1.4.bps` - English patch

## How to apply
1. Get the original ROM and check it matches:
   - File: `Twilight Syndrome - Kinjirareta Toshi Densetsu (Japan).nds`
   - Size: 134,217,728 bytes
   - CRC32: `76F1DB67`
   - SHA-1: `129880d90ecc1b322255e56d4968b259a3e1aa15`
2. Apply the `.bps` patch to it with any BPS patcher (for example Flips or Rom Patcher JS). Flips may warn that the original ROM is larger than the result: that is expected, because the original dump contains padding that the patched ROM does not keep.
3. Expected checksums:

| Patch | Result | Size | CRC32 | SHA-1 |
|---|---|---|---|---|
| `Twilight.Syndrome.ESP.v1.4.bps` | Spanish | 116,321,480 bytes | `D4725F27` | `46d1efcc3f5763d7ff82dcf0a4396f3b26dd089b` |
| `Twilight.Syndrome.ENG.v1.4.bps` | English | 116,265,160 bytes | `BDD95BB6` | `8b562fc9318e506acf88c4ca4056ec189df02bbe` |

Tested in melonDS.

**Updating from an earlier version:** your in-game save (`.sav`) keeps working, but do **not** load emulator savestates made with an older ROM: a savestate stores the graphics and text already loaded in memory, so old text can reappear.

## Known issues
- On the save / load list, the text of each save card (the rumor name and place) is cut off at the right edge.
- Mail photos inside some cutscenes keep their Japanese text; the same mails can be read translated on the phone.
- Left untranslated on purpose: the "touch the bottom screen" prompt on the title screen, the labels printed on the phone's physical keys, the staff credits and a few props with text drawn into the background art.
- Not every route has been re-tested after every change, so some typos or inconsistencies may remain.

## Source
The scripts, translation files and tools used to build the patches are in this repository (see the README). No game data is included: the patches only contain the differences from the original ROM, which you must supply yourself.

Translation and ROM hacking: Talion.
