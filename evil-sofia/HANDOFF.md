# Handoff: Evil Sofia

Read this, `KNOWLEDGE.md` (everything known so far, in detail) and `README.md` before changing anything. The README describes what the mod contains; this file
describes how the work is done and the rules the user has set.

## What it is

A Hearts of Iron IV (1.19) total conversion for multiplayer with friends: the map is Sofia, every one of the 24
districts is a country. Eight districts are led by the user's friends (real names, portraits): Sredets (SRD,
Victor Kolev, the user's own country), Oborishte (OBR, Anton Zafirov), Vitosha (VIT, Daniel-Henry Capel),
Mladost (MLA, Georgi Poryazov), Krasna Polyana (KRP, Stefan Kartunov), Lozenets (LOZ, Georgi Yanchovichin),
Triaditsa (TRD, Alexander Dimitrov), Lyulin (LYU, GrimBoss). The game starts on 1 January 1936.

## Rules from the user (keep them)

- **No portraits or photos in the repository, ever.** They live in `tools/portraits/` (git-ignored) and go only
  into the packaged zip. The icons made from them go to `gfx/interface/goals/evil_sofia/people/` and
  `gfx/leaders/` (both git-ignored). Before every commit, check that no staged path contains `portraits/`,
  `gfx/leaders/` or `goals/evil_sofia/people/`.
- Person focus icons: the leader cut out of his portrait in black and white, standing inside a pack frame, with
  the sword or handshake **in front** of him, faces visible, a different frame for each. Other icons: finished
  pack icons, varied. No foreign-flag icons.
- Cores only after holding: conquest focuses give claims and war goals; cores come in the next focus, only for the
  states actually controlled (placeholders `{CLAIMS}`, `{WAR}`, `{HELD}`, `{COREHELD}`).
- AI answers to diplomatic events depend on opinion (and, for Anton, Oborishte's communism), so they can say no.
- Focus lengths vary (3 to 12 weeks); every focus has search filters; no two focuses' labels may touch (leave an
  empty column between branches).
- Texts: HOI4-style descriptions, rooted in real Sofia places, playful about the friends but never mean.
- Random events stay rare.
- Leave the rivers alone ("the rivers are fine").

## Building

```
cd evil-sofia
python3 tools/build_map.py            # everything: map, countries, focus trees, events (about 8 minutes)
python3 tools/dev/build_focus_only.py # only focus trees, events, ideas, flags, texts; needs a built map (seconds)
python3 tools/dev/validate_map.py .   # map checker: must say "0 errors, 0 warnings"
python3 tools/dev/render_tree.py out.png   # picture of the Sredets focus tree as it was built
```

`build_focus_only.py` does not rewrite characters, leaders or the start screen (those are in `build_map.py`).
Run the full build before packaging.

Packaging (what the user installs): copy `evil-sofia/` without `tools/`, `preview/` and `design/` into
`dist/pkg/evil-sofia/`, write `dist/pkg/evil_sofia.mod` = `path="mod/evil-sofia"` + `descriptor.mod` without its
`path=` line, zip both as `dist/evil-sofia.zip` and send it. The user deletes the old folder before copying.

The GFX packs are read from `/home/user/duodex/hoi4gfx` (DuoDex hoi4GFX) and `/home/user/globvs/ultimate-hoi4-gfx`
(Ultimate HOI4 GFX). Pack icons already used are cached in `tools/icons/`, so the build only needs the packs for
new icons and for person/photo icons (frames and pieces): clone them again if they are missing.

## Where things are

| File | What |
|---|---|
| `tools/build_map.py` | the whole map, states, countries, characters, advisors, starter focus tree, start screen; calls `build_focus.py` at the end |
| `tools/build_focus.py` | writes the Sredets tree, events, decisions, ideas, traits, flags, event pictures and their texts |
| `tools/focus_sredets.py` | the Sredets tree: focuses, filters, person/photo icons, ideas, decisions, events, factions |
| `tools/events_world.py` | news events (everyone sees them) and random city events |
| `tools/texts.py` | start screen and leader descriptions, advisors and their traits, Ilchev |
| `tools/picture_briefs.py` | what each event picture should show; the build writes `tools/event_pictures/PICTURES.md` |
| `tools/event_pictures.py` | drawn event pictures (flags over a skyline) and fitting of the user's own pictures |
| `tools/red_flags.py` | hand-drawn communist flags (Sredets, Oborishte, Sofia, South and North Sofia) |
| `tools/focus_icons.py` | portrait cut-out, person icons, group photo icons |
| `tools/flags/` | district flags; `tools/portraits/` (git-ignored) portraits and photos |

## Pictures to upload again in a new session

The user has to send these again (they are not in git); save each as PNG under `tools/portraits/`:

| File | Who |
|---|---|
| `SRD.png` | Victor Kolev |
| `OBR.png` | Anton Zafirov |
| `VIT.png` | Daniel-Henry Capel |
| `MLA.png` | Georgi Poryazov |
| `KRP.png` | Stefan Kartunov |
| `LOZ.png` | Georgi Yanchovichin |
| `TRD.png` | Alexander Dimitrov |
| `LYU.png` | GrimBoss |
| `SRD_ilchev.png` | Konstantin Ilchev (Victor's physics teacher) |
| `EVIL_GANG.png` | the Evil Gang group photo (on the steps, 1080x1080) |
| `C_CLASS.png` | the C Class Hools group photo (mirror selfie, 1080x1080) |

Without them the build still works: leaders have no portrait and the person/photo icons fall back to pack icons.

## State of the work

- Sredets tree: 81 focuses. Communist path (Henry's Mom Was Right) finished and tuned by the user. Authoritarian
  path (Order in the Centre) just written: four mutually exclusive branches, Sredets alone (no factions), the Evil
  Gang (invite the friends one by one), the C Class Hools (join or get hit) and Konstantin Ilchev's takeover.
  Not yet played; expect tweaks.
- The other districts have a 13-focus starter tree; the featured friends have no tree of their own yet.
- Event pictures: the user is making their own in vanilla style; `tools/event_pictures/PICTURES.md` lists every
  file name, size and subject. A PNG with that name in `tools/event_pictures/` replaces the drawn picture.

## Untested in game (check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` if something is off)

- advisor traits (custom traits in `common/country_leader/`), and that advisors without portraits look fine
- the `rule = { can_create_factions = no can_join_factions = no }` block in the "Sredets Stands Alone" spirits
- news events with `major = yes` reaching every country, and `[From.GetLeader]` in event titles
- `strength_ratio` in the C Class invitation's AI odds
