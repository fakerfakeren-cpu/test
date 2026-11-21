# Handoff: Evil Sofia

Read this, `KNOWLEDGE.md` (the full history and reasons) and `README.md` before changing anything. The README describes what the mod contains; this file
describes how the work is done and the rules the user has set.

## What it is

A Hearts of Iron IV (1.19) total conversion for multiplayer with friends: the map is Sofia, every one of the 24
districts is a country. Eight districts are led by the user's friends (real names, portraits): Sredets (SRD,
Victor Kolev, the user's own country), Oborishte (OBR, Anton Zafirov), Vitosha (VIT, Daniel-Henry Capel),
Mladost (MLA, Georgi Poryazov), Krasna Polyana (KRP, Stefan Kartunov), Lozenets (LOZ, Georgi Yanchovichin),
Triaditsa (TRD, Alexander Dimitrov), Lyulin (LYU, GrimBoss). Serdika (SRK) is led by Khan Krum (portrait
`tools/portraits/SRK.png`), and Ivan Apostolov (IAP) is a one-province micro-state between Mladost and Izgrev, capital Musagenitsa. The game starts on 1 January 1936.

## Rules from the user (keep them)

- **No portraits or photos in the repository, ever.** That includes the user's own event pictures:
  `tools/event_pictures/*.png` and their DDS in `gfx/event_pictures/evil_sofia/own/` are git-ignored. They live in `tools/portraits/` (git-ignored) and go only
  into the packaged zip. The icons made from them go to `gfx/interface/goals/evil_sofia/people/` and
  `gfx/leaders/` (both git-ignored). Before every commit, check that no staged path contains `portraits/`,
  `gfx/leaders/`, `goals/evil_sofia/people/`, `event_pictures/evil_sofia/own/` or a PNG in `tools/event_pictures/`.
- Person focus icons: the leader cut out of his portrait in black and white, standing inside a pack frame, with
  the sword or handshake **in front** of him, faces visible, a different frame for each. Other icons: finished
  pack icons, varied. No foreign-flag icons.
- Cores only after holding: conquest focuses give claims and war goals; cores come in the next focus, only for the
  states actually controlled (placeholders `{CLAIMS}`, `{WAR}`, `{HELD}`, `{COREHELD}`).
  Exception (user's request): the Free Sredets road and the United Centre road get cores on the centre at once
  (`{COREALL:T:A,B}`, `WIDER_CENTRE_COREALL`), and land handed over peacefully is cored too. The communist road
  still cores only what it holds.
- AI answers to diplomatic events depend on opinion (and, for Anton, Oborishte's communism), so they can say no.
- Focus lengths vary (3 to 12 weeks); every focus has search filters; no two focuses' labels may touch (leave an
  empty column between branches).
- Texts: HOI4-style descriptions, rooted in real Sofia places, playful about the friends but never mean.
- Random events stay rare.
- **No instant popularity changes**, and the spirits Sredets puts on other districts are small (0.03-0.08 drift;
  the user asked for them to be a lot smaller), with Ally Anton at 20% and the Red Coup at 30% communism; for us or anyone else: ideologies grow through timed spirits with a
  `*_drift` (`add_timed_idea`). The first focus of the communist and the democratic road starts the drift; the
  government changes with the focus Proclaim the Sredets Commune / Proclaim the Free Sredets, which needs the
  ideology above 30% (the user's number).
- Basic decisions for every district (`tools/decisions_world.py`: Political Actions, War Measures), vanilla-style,
  also over time.
- Henry's mother is never placed in Boyana.
- Event pictures: the user makes the world news pictures. Private (country) events have no picture unless the
  user made one (`tools/event_pictures/<event>.png`); the drawn flag pictures are only used for news.
- Peaceful offers of the free centre: Anton (OBR) joins whole (annexation); Georgi (LOZ) and Alexander (TRD) are only
  asked for the central states the Free Centre of Sofia needs (event srd.20, `transfer_state`).
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

The GFX packs (Ultimate HOI4 GFX is free to use with credit, see its `CREDITS.txt`; DuoDex hoi4GFX has no licence, so
ask DuoDex or credit them before publishing anywhere) are read from `/home/user/duodex/hoi4gfx` (DuoDex hoi4GFX) and `/home/user/globvs/ultimate-hoi4-gfx`
(Ultimate HOI4 GFX). Pack icons already used are cached in `tools/icons/`, so the build only needs the packs for
new icons and for person/photo icons (frames and pieces): clone them again if they are missing.

## Where things are

| File | What |
|---|---|
| `tools/build_map.py` | the whole map, states, countries, characters, advisors, starter focus tree, start screen; calls `build_focus.py` at the end |
| `tools/build_focus.py` | writes the Sredets tree, events, decisions, ideas, traits, flags, event pictures and their texts |
| `tools/focus_sredets.py` | the Sredets tree: focuses, filters, person/photo icons, ideas, decisions, events, factions |
| `tools/focus_vitosha.py` | the Vitosha tree (civil war, Henry or Yani), same format plus `NEWS`, `ON_STARTUP` and `extra_build` (Yani's character and portrait, the war armies) |
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
| `VIT_yani.png` | Yanislav Marazov (Yani), Vitosha's second leader |
| `SRK.png` | Khan Krum, leader of Serdika (painting; head and shoulders cropped from the user's full-length picture) |

The user's event pictures (`tools/event_pictures/<event>.png`, see `PICTURES.md`) also have to be sent again.
Made so far (all saved already cropped to the news shape): news 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 13, 14, 16, 17,
18, 19 and srd 2. Still drawn: news 8 (A District Falls), 12 (Ilchev) and 15 (The Vitosha Award).

Without them the build still works: leaders have no portrait and the person/photo icons fall back to pack icons.

## State of the work

- Sredets tree: 140 focuses (see KNOWLEDGE.md for the roads, the Grip, the Directorate and the shared trees). Communist path (Henry's Mom Was Right) finished and tuned by the user. Authoritarian
  path (Order in the Centre) just written: three mutually exclusive roads (see KNOWLEDGE.md, "Restructure"), A Free Sredets (democracy under Victor, no elections, alone, no factions, blue with its own
  flag `red_flags.free()`; 16 focuses, 3 to 10 weeks by weight, an uneven layout where some focuses need two others; peaceful
  offers to Anton, Georgi, Alexander (event srd.17, mostly no; person icons `offer_to_*`, made once the portraits are
  back); then takes the centre: VAZ and OBR
  whole, then the central states of TRD, LOZ, KRS and SRK, set in `WIDER_CENTRE`; ends as the Free Centre of Sofia), the Evil
  Gang (invite the friends one by one), the C Class Hools (join or get hit) and Konstantin Ilchev's takeover.
  Not yet played; expect tweaks.
- Vitosha tree: 181 focuses, laid out like vanilla's Spain. Two exclusive roots: Stand with Henry (left) or March
  with Yani (right). Each side has a prep chain (divisions in `history/units/VIT_henry_army.txt` / `VIT_yani_army.txt`,
  rifles, spirits) ending in the war: Crush the Student Movement (Yani's rebels, communist or fascist at random, take 5
  eastern states, size 0.3) or Yani Takes the Villa (Yani leads from Simeonovo, Henry's loyalists take 10 states, size
  0.6, with the stronger army). Support is split 40/40 between the side's two ideologies; then three branches per side:
  Henry: What the English Couldn't Do (democratic, UK-like, Mountain Entente, Commonwealth of the Mountain) / war branch /
  What Zevka Wanted (authoritarian, League of the Mountain, Tsardom of the Mountain); Yani: Red Plovdiv (Red Mountain,
  Thracian Commune) / war branch / The Seven Hills (Pact of the Seven Hills, New Philippopolis). The war branches remove
  The Mountain in Flames (3 tiers). Evil Gang, industry and army on the far right. 16 smaller states, region Boyana
  Slopes. Not yet played.
- The other districts have a 13-focus starter tree; the other featured friends have no tree of their own yet.
- Event pictures: the user is making their own in vanilla style; `tools/event_pictures/PICTURES.md` lists every
  file name, size and subject. A PNG with that name in `tools/event_pictures/` replaces the drawn picture.

## Untested in game
 (check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` if something is off)

- Vitosha: `promote_character = { character = VIT_yani ideology = fascism_ideology }` in The Seven Hills, `start_civil_war` with `states`, the rebels inheriting Yani/Henry as the party leader of their ideology, `load_oob` on the rebels, and how long the war takes on each side
- advisor traits (custom traits in `common/country_leader/`), and that advisors without portraits look fine
- the `rule = { can_create_factions = no can_join_factions = no }` block in the "Sredets Stands Alone" spirits
- news events with `major = yes` reaching every country, and `[From.GetLeader]` in event titles
- `strength_ratio` in the C Class invitation's AI odds
- A Free Sredets: switching to democracy with `set_politics` + a `liberalism` leader role for Victor, and the
  `take_state_focus` war goals (with `generator`) on the parts of Triaditsa, Lozenets, Krasno Selo and Serdika
