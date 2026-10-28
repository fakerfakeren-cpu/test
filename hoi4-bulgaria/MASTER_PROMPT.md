# Master Prompt — Bulgaria Focus Tree Mod (HOI4)

Copy everything below the line into a new Claude Code session on this repo.
First do the "Before you paste" steps; without them the result will be guesswork.

## Before you paste (5 minutes, required)

Claude cannot see your HOI4 install or Steam Workshop. Copy these into
`hoi4-bulgaria/reference/` in this repo and push them (or upload them in the chat):

1. **Game version**: `launcher-settings.json` from your HOI4 install folder
   (Steam → right-click HOI4 → Manage → Browse local files).
2. **Vanilla files** from the same install:
   - `common/national_focus/bulgaria.txt` (and any other file containing `BUL` in that folder)
   - `history/countries/BUL - Bulgaria.txt`
   - `common/characters/BUL.txt`
   - `interface/goals.gfx` and `interface/ideas.gfx`
   - `common/ideas/_economic.txt` and `common/ideas/_manpower.txt`
   - `history/states/` → only the files for Bulgaria and its neighbours (or the whole folder zipped)
3. **Road to 56** from `Steam/steamapps/workshop/content/394360/820260968/`:
   - its `descriptor.mod`
   - everything in its `common/national_focus/` that mentions `BUL`
   - its `common/characters/BUL.txt` and `history/countries/BUL*.txt` if they exist

---

## THE PROMPT

You are building a complete, playable Hearts of Iron IV mod that gives
Bulgaria a new, fun, original focus tree. Work autonomously in one go: plan,
build, check and deliver without stopping for approval. Ask me something only
if you are truly blocked (for example, missing reference files). In that case,
ask everything at once at the start, not partway through.

### 0. Hard constraints

- **Target the newest HOI4 version.** Read the version from
  `hoi4-bulgaria/reference/launcher-settings.json`. Put it in
  `supported_version` with a wildcard patch (e.g. `"1.xx.*"`). Use only syntax
  that this version's vanilla files use. If a vanilla file and your memory
  disagree, the vanilla file is right.
- **No DLC required.** Do not use any `has_dlc` gated content: Balance of Power,
  MIOs, special projects, raids, faction upgrades, or government-in-exile. It must
  run on the base game. Vanilla scripted GUI, decisions, dynamic modifiers,
  ideas, events and characters are all fine.
- **Compatible with Road to 56, and works without it.**
  - Never override a vanilla or R56 file by name. Use only new, prefixed file
    names (`bfx_` prefix, e.g. `common/national_focus/bfx_bulgaria.txt`). No
    `replace_path`.
  - Prefix every new ID with `bfx_`: focuses, ideas, events namespace, flags,
    variables, sprites, characters, decisions and loc keys.
  - The tree must win the tree selection over both vanilla and R56. Read R56's
    and vanilla's BUL tree `factor` values from the reference files and use a
    clearly higher one (e.g. `factor = 0` + `modifier = { add = 1000 tag = BUL }`).
  - Do not reference R56-only content (its ideas, techs, equipment, characters)
    unless it is guarded so nothing breaks without R56 loaded. Prefer generic
    effects that exist in both: `add_tech_bonus` with vanilla categories,
    `add_ideas` with your own ideas, `add_research_slot`, buildings, `army_experience`, etc.
  - Add `dependencies = { "Road to 56" }` to the descriptor so the launcher
    loads it after R56 when both are on. Check that this is a soft dependency
    that does not break when R56 is off. If it is not soft, drop it and
    document the load order instead.
  - Existing BUL characters may differ between vanilla and R56. Create your
    own `bfx_` characters for anyone the tree promotes, and do not change
    existing ones.
- **No in-game testing is possible for you.** Make up for it with the static
  validator in section 5. Be honest in the final report about what could not
  be checked.

### 1. Design (write `hoi4-bulgaria/DESIGN.md` first, then build from it)

Theme: Bulgaria in 1936. It is a "twice-defeated" nation under the Treaty of
Neuilly, hungry for San Stefano Bulgaria, and torn between Tsar Boris III,
the outlawed communists, the Agrarians, the Zveno officers and IMRO.

Size: **120–140 focuses.** Not 150+. Breadth is not the goal; every focus
must do something you would notice.

Structure:

1. **Shared opening (~15):** the 1936 political crisis, IMRO crackdown or
   tolerance, the Salonika Agreement 1938 (lifting Neuilly limits).
2. **Economy & industry (~20):** tobacco and rose oil exports, Pernik coal,
   railways, the German clearing-trade trap vs. diversification. Include at
   least one real trade-off choice.
3. **Military (~20):** army (mountain warfare, Balkan doctrine flavour), a
   small navy branch on the Black Sea, the Air Force rebuilding after the
   Neuilly ban.
4. **Political paths (~70 across 4 paths, each with 2 sub-branches):**
   - **Tsardom (Boris III):** (a) Axis San Stefano revanchism: Southern
     Dobruja, Macedonia, Thrace/Aegean access. (b) Armed neutrality, "the
     Balkan Switzerland", leading to an Allied/independent alignment.
   - **Communist (BKP / Dimitrov):** (a) Soviet-aligned People's Republic.
     (b) Independent Balkan Communist Federation with Yugoslav and Greek
     partisans; possible formable or federation core claims.
   - **Agrarian / Zveno:** (a) Stamboliyski's revived Agrarian democracy and
     the "Green International" Balkan peasant union. (b) Zveno military
     technocracy, a coup regime with fast modernisation and less stability.
   - **Wild alt-history (late unlock, needs a specific condition):** Tsar
     Ferdinand returns / the Third Bulgarian Empire, "Tsargrad" claim on
     Constantinople, Byzantine-flavoured ambitions. This one should be fun
     and a bit absurd, but still mechanically coherent.
5. **Unique mechanic: "Shackles of Neuilly"** (simple, but felt every game):
   - A scripted-GUI or decision-category panel. It shows a **Covert
     Rearmament** level (0–100) and **Balkan Suspicion** (0–100).
   - Bulgaria starts with a national spirit that gives army/air/navy
     penalties. Covert decisions (hidden officer schools, "civilian" flying
     clubs, Škoda/Rheinmetall purchases through fronts) raise Rearmament
     and reduce the penalties through a dynamic modifier. They also raise
     Suspicion.
   - Suspicion thresholds trigger Balkan Pact events: Yugoslavia, Greece,
     Turkey and Romania protest, guarantee each other, impose embargoes, and
     at the top a border-incident crisis.
   - The Salonika Agreement focus (or breaking the treaty openly) ends the
     mechanic. Each political path ends it differently (e.g. communists
     denounce it, the Tsardom negotiates it, alt-history tears it up loudly).
   - Make it readable: every number shown in the UI, every threshold in
     the tooltip.
6. **National spirits and advisors:** at least 12 unique ideas (each
   evolving through focuses, not static) and 8+ new characters (advisors,
   leaders per path, 2–3 generals). Use real people where they fit (Kimon
   Georgiev, Damyan Velchev, Georgi Dimitrov, Vasil Kolarov, Bogdan Filov,
   Hristo Lukov, Nikola Mushanov, etc.) and check their biographies.
7. **Events:** about 30. At least 1 per sub-branch, the Neuilly mechanic
   events, and 3–5 random flavour events. Every event option must have a
   tooltip-visible effect. No "OK" options that do nothing, except purely
   narrative ones.
8. **Decisions:** the Neuilly category, plus one path-specific category per
   political path (e.g. IMRO operations in Macedonia, partisan support,
   peasant cooperatives, Tsargrad propaganda).

Design rules:

- Use `mutually_exclusive` for every real choice, with the reason written
  in the description.
- No more than about 15% of focuses may be plain stat bumps. The rest must
  unlock ideas, decisions, events, claims, wargoals, characters, the
  mechanic, or make choices.
- Give every focus an `ai_will_do`. Each political path needs AI weights
  that make it pick historical behaviour by default (with game rule–free
  logic, e.g. a small randomness).
- Use `search_filters` on every focus.
- Balance: compare rewards to vanilla BtB Bulgaria and R56 Bulgaria. Nothing
  should be more than ~1.5× the power of a comparable vanilla focus.
- Write all text yourself: names, descriptions in a historical, slightly
  witty tone. No lorem ipsum, no empty `_desc` keys.

### 2. Graphics

- **Portraits:** for real people, download public-domain photos from
  Wikimedia Commons. Check the licence on each file page. Pre-1950
  Bulgarian state photos are usually PD. Remove the background with `rembg`
  (install it via pip; if the model download is blocked, use a GrabCut
  crop as a fallback). Then put the person on a background in the vanilla
  HOI4 portrait style: a grey-blue gradient with subtle texture. Generate
  it yourself rather than copying a vanilla file. Apply mild
  colourisation/grain so they sit next to vanilla portraits.
  - Sizes: large leader portrait **156×210**, small advisor portrait
    **65×67**.
- **Focus icons:** for most focuses, reuse existing vanilla `GFX_goal_*`
  sprites that are confirmed to exist in `reference/goals.gfx`. Make **20–30
  custom icons** for the signature focuses (path starts, path ends, the
  mechanic, Tsargrad, etc.): **95×85**, in the vanilla style (a central
  emblem on a transparent background with a soft drop shadow). Build them
  from PD flags, coats of arms and symbols from Wikimedia. Do not take
  Steam Workshop icon packs or other mods' art unless the licence explicitly
  allows reuse.
- **National spirit icons:** 64×64 (use the same rules as focus icons).
  **Event pictures:** 210×176.
- **Format:** `.dds`. Write them with Pillow or ImageMagick as uncompressed
  BGRA8 or DXT5, then read them back to verify that the size and alpha are
  correct. Register every sprite in `interface/bfx_*.gfx`. Add the
  `_shine` variant entries for focus icons in the same way vanilla does.
- Write `hoi4-bulgaria/CREDITS.md` with source URL + licence for every
  downloaded image.
- If network access to Wikimedia is blocked, say so, use vanilla sprites
  for everything, and list what you would have made.

### 3. Mod layout

Build the mod at `hoi4-bulgaria/mod/bfx_bulgaria/` with the normal HOI4
structure (`common/`, `events/`, `gfx/`, `interface/`, `localisation/english/`,
`descriptor.mod`, `thumbnail.png` 1:1 ≤ 1MB). Also create
`hoi4-bulgaria/mod/bfx_bulgaria.mod`, the launcher file with
`path="mod/bfx_bulgaria"`.

- Localisation: `localisation/english/bfx_*_l_english.yml`, **UTF-8 with
  BOM**, header `l_english:`, keys indented with one space, `:0` versioning
  not required.
- Use `relative_position_id` + coordinates so branches move as blocks.

### 4. Build order

1. Read every reference file. Note: game version, the exact focus/idea/
   effect syntax, R56's BUL tree factor and IDs, available GFX keys and
   state IDs for the claims.
2. Write `DESIGN.md`: a full focus list (ID, name, prerequisites,
   exclusives, reward in one line, x/y), the mechanic spec, events, ideas,
   characters.
3. Write the validator (section 5) **before** the script files, so you can
   run it after each file.
4. Build in this order: ideas & characters → focus tree → mechanic
   (variables, dynamic modifier, decisions, GUI) → events → decisions →
   localisation → graphics. Run the validator after each step.
5. Re-read the whole tree once as a player. Is every branch fun to click
   through? Fix boring stretches.

### 5. Static validator (must pass with 0 errors)

Write `hoi4-bulgaria/tools/validate.py` that checks:

- Balanced braces and quotes in every `.txt`/`.gfx`/`.gui` file.
- Unique focus IDs. Every `prerequisite`/`mutually_exclusive`/
  `relative_position_id` points to an existing focus.
- No two focuses in the same absolute (x, y) spot. Prerequisites sit
  above their children. No focus line crosses another focus (best effort).
- Every focus, idea, event, decision, character and option has a
  localisation key. No loc key is unused or duplicated. The `.yml` files
  have a BOM.
- Every `icon`/`picture`/`GFX_` reference is either defined in your `.gfx`
  files or exists in `reference/goals.gfx`/`ideas.gfx`. Every texture file
  path exists and has the right pixel size.
- Every event ID that is fired exists. Every flag/variable that is
  checked is also set somewhere.
- Every `bfx_` ID has the prefix. No file name collides with a vanilla or
  R56 file name.
- Every state ID used for claims/cores exists in the reference states.

Print a summary. Fix everything, and re-run until it is clean.

### 6. Deliverable — the folder I drop in and play

- Zip `bfx_bulgaria/` + `bfx_bulgaria.mod` as
  `hoi4-bulgaria/bfx_bulgaria_vX.Y.zip`. Commit and push to this branch,
  and send me the zip directly with SendUserFile.
- `hoi4-bulgaria/README.md` with:
  - **Install:** unzip into
    `Documents/Paradox Interactive/Hearts of Iron IV/mod/`, so that both
    `bfx_bulgaria.mod` and the `bfx_bulgaria/` folder are there. Then enable
    it in the launcher playset, **below Road to 56** if used.
  - **Test checklist** for me: launch with `-debug` (Steam launch
    options). Play as BUL. Use the console with `focus.autocomplete`,
    `observe`, and `event bfx.1`. Check
    `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` and
    paste any `bfx` lines back to you.
  - A one-paragraph overview of each path, for players.
- Final report in chat: focus/event/idea/character counts, what the
  validator could not check, all known risks, and what to test first.
