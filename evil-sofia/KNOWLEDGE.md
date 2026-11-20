# Evil Sofia: everything known so far

A full brain dump from the first long chat, for any later session. `HANDOFF.md` is the short version (rules and
how to build); this file has the details, the history and the reasons. Read both.

---------------------------------------------------------------------------------------------------------------

## 1. The project

- A Hearts of Iron IV (version 1.19) total conversion mod called **Evil Sofia**. The map is Sofia, Bulgaria; each
  of the city's 24 districts is a country. The user plays it in multiplayer with friends.
- The user wants: realistic geography, organic borders (never squares or hexagons), real neighbourhood names, fun
  focus trees with the friends as leaders, a vanilla HOI4 look.
- Start date: **1 January 1936** (it was 2026 for a while; reverted so research years and the ahead-of-time
  penalty work like vanilla). End date is vanilla's.
- Repository: `fakerfakeren-cpu/test`, everything under `evil-sofia/`, work branch
  `claude/practical-hawking-chdtpz` (later sessions may only be allowed to push to their own `claude/...` branch).
- The user installs from a zip: `evil-sofia/` folder + `evil_sofia.mod` into `Documents/Paradox Interactive/
  Hearts of Iron IV/mod/`, deleting the old folder first.

## 2. The people (the friend group)

The user is **Victor Kolev** and plays **Sredets (SRD)**, the city centre. The friends and their districts:

| Tag | District | Leader | What we know / lore used |
|---|---|---|---|
| SRD | Sredets | **Victor Kolev** (the user) | Rules the centre: Largo, Party House, Vitosha Boulevard. Main focus tree. |
| OBR | Oborishte | **Anton Zafirov** | Three streets from the Party House, under Alexander Nevsky cathedral; undecided, can be allied or destroyed. |
| VIT | Vitosha | **Daniel-Henry Capel** ("Henry") | Rules Vitosha (Boyana is in it, but never place his mom there); **his mom** always said the people of the centre are "dirty communists". Henry has the trait **"Hates Communism"** (communism drift -0.20, acceptance -200, +5% war support). He hates Sredets once it goes red. |
| LOZ | Lozenets | **Georgi Yanchovichin** | Victor's **"day one"** (best friend from before everything). Lozenets lies between Sredets and Vitosha. |
| MLA | Mladost | **Georgi Poryazov** | Biggest housing estates, lots of manpower. |
| KRP | Krasna Polyana | **Stefan Kartunov** | Western quarters, West Park; poor, crowded, loyal. |
| TRD | Triaditsa | **Alexander Dimitrov** | Named after Sofia's medieval name; NDK, Ivan Vazov. |
| LYU | Lyulin | **GrimBoss** | Nickname only, nobody uses his real name; ten housing estates under the Lyulin mountain. |
| (SRD) | — | **Konstantin Ilchev** | Victor's **physics teacher**. In the authoritarian path he takes Sredets away from Victor. |

- **The Evil Gang**: the friends' Instagram group chat. Its profile picture (group on the steps of a theatre) is
  `tools/portraits/EVIL_GANG.png`.
- **The C Class Hools**: another group (school class C, "hools" = hooligans). Its profile picture (mirror selfie in
  a corridor, party hats) is `tools/portraits/C_CLASS.png`.
- The other 16 districts have generated Bulgarian leader names and no portraits.
- Tone: playful about the friends, never mean or personal. In-character district politics only.
- Leader portraits were supplied by the user as HOI4-style painted portraits.

- **Serdika** is led by **Khan Krum** (the Bulgar khan who took Serdica in 809, come back somehow; the user's
  painting, chain mail, skull cup). **Ivan Apostolov (IAP)** is a micro-state like Vatican City: one province, one
  state, between Mladost and Izgrev, carved after the districts snap to the neighbourhoods (`MICRO` in build_map.py:
  centre and radius in map pixels); flag after the user's logo (white sword, two peaks with yellow centres, the M,
  on green; `tools/flags/IAP.png`), leader Apostol Penev (a made-up headmaster).
- Full builds: `python3 tools/fetch_geodata.py` first in a new container; a build of unchanged code reproduces the
  map files exactly. Put every leader portrait in `tools/portraits/` before a full build (from the last zip's
  `gfx/leaders/*/*.dds` if the originals are not there), or the character files lose their portraits.

## 3. Rules the user gave (do not break)

1. **No portraits or photos on GitHub**, ever ("dont include it" / "Dont include any portraits"). They live in
   `evil-sofia/tools/portraits/` (git-ignored) and only go into the zip ("i want it in game"). Icons made from them
   go to `gfx/interface/goals/evil_sofia/people/` and portraits to `gfx/leaders/` (both git-ignored). Before every
   commit check: `git diff --cached --name-only | grep -ciE 'portraits/|gfx/leaders/|goals/evil_sofia/people/'`
   must be 0.
2. The rivers are fine; do not touch them.
3. Person focus icons (see section 7): the character **cut out** of the portrait, **black and white**, standing in
   a frame; swords/handshakes **in front of** him, not behind; **faces must be visible**; **different frames**
   for variety; never just a face filling a circle.
4. Not all icons should be person icons; the others are varied finished pack icons. No foreign-country-flag icons
   (Taiwan, UK, US, etc. were removed once).
5. Conquest: **cores only after you control all states of a group**; focuses give claims + war goals first.
6. AI answers to diplomatic events depend on **opinion** (and for Anton, Oborishte's communism %), so they can
   say no.
7. Focus lengths vary (3 to 12 weeks); every focus has **search filters**; branches separated by an empty column
   so labels do not touch (the Barricades focus once overlapped Destroy Anton).
8. The **Continuous Focuses** panel sits **below** the tree (`continuous_focus_position`), it covered the tree
   before.
9. Random events must be **rare** (mineral water event removed on request).
10. Communist flags only for countries that can actually go communist (Sredets, Oborishte and the Sofia states),
    hand-drawn and creative, not "just a star".
11. Texts: proper HOI4-style descriptions (the user called early ones "CHEEKS"), rooted in real Sofia places.
12. The user prefers short status updates while working, and doesn't want to wait long: give the zip as soon as
    it is built.

## 4. History of what was built (in order)

1. Map of Sofia from real data: districts, neighbourhoods (kvartali GeoJSON, Sofproekt 2019), organic province
   growth, rivers along real valleys, lakes, terrain from elevation. 460 land provinces, 118 states, 13 strategic
   regions. Multiple states per country with real neighbourhood names.
2. Placement audit; Yavorov moved into **Sredets** (user correction); Krastova Vada fix; Poduyane piece named Reduta.
3. Populations multiplied by a random 100–200 per state (realistic manpower).
4. District flags from the user's flag sheet ("Flags of Sofia and her regions"), `tools/flags/<TAG>.png`.
5. Leaders with portraits, one by one: Victor Kolev, Georgi Poryazov, Daniel-Henry Capel, Stefan Kartunov, then
   Anton, Georgi Yanchovichin, Alexander Dimitrov, GrimBoss.
6. Start screen: the 8 friends' countries are featured with descriptions; the other 16 are small flags at the
   bottom (they need a focus tree to show, hence the 13-focus starter tree); the "Other countries" tile removed.
7. Cores and Claims map mode (like Road to 56's): own core green, owned non-core yellow, core owned by another
   purple, claim blue, occupied orange. The user confirmed it works perfectly.
8. Sredets focus tree, communist path ("Henry's Mom Was Right"): Oborishte question (focuses + decisions + red
   coup), ally or destroy Anton, staged conquest of Sofia by district group, two endings (Union of North and South
   Sofia with Anton / Sofia Commune alone), Henry's branch, Party and economy branches. Later: more focuses,
   cleaner layout, varied lengths, filters, rewritten texts, cores-after-holding, Georgi as day-one ally.
9. Communist flags (`tools/red_flags.py`), red map colours and names via cosmetic tags.
10. World news events, random city events, generated event pictures; 3 advisors per country; leader descriptions.
11. Authoritarian path ("Order in the Centre") with four branches: alone / Evil Gang / C Class Hools / Ilchev.
12. The user is now making their own event pictures (vanilla style) from `tools/event_pictures/PICTURES.md`.

## 5. The Sredets focus tree (92 focuses)

Root choice (mutually exclusive): **Henry's Mom Was Right** (communism) at x=8, **Order in the Centre**
(authoritarian) at x=24.

### Communist path
- Sets communism, Victor becomes a leninist leader, cosmetic tag `SRD_RED` ("Sredets Commune", red), event to
  Henry (his reaction: hate, 20% chance he prepares war), world news.
- **Oborishte branch (x 0–4)**: Comrades in Oborishte (unlocks decision category "The Oborishte Question": Fund the
  Oborishte Communists 50 PP/30 days +5%, Rally at the Doctors' Garden 35 PP/45 days +4%, Red Coup in Oborishte
  100 PP when >55% communist) → Red Newspapers → **Ally Anton** (needs 40% communist; event, AI yes depends on
  communism and opinion) or **Anton Must Go** (war goal) → North-South Pact / Destroy Anton (needs all of OBR held).
- **Conquest by district group** (from the user's map of district types):
  - centre: VAZ (+OBR in the alone path)
  - old quarters (early 20th c.): KRS SRK POD SLA IZG LOZ TRD KRP ILN
  - socialist housing estates: NAD ISK MLA STU LYU
  - industry: KRE (Kremikovtsi)
  - outskirts: VIT OVK VRB NIS PNC BNK
  - With the pact: north half (SRK POD NAD VRB NIS KRE ILN KRP LYU BNK) goes to Oborishte, the rest to Sredets.
    Ending **The Union of North and South Sofia**: SRD → `SRD_SOUTH` "South Sofia", OBR → `OBR_NORTH` "North
    Sofia", faction recreated as "Sofia".
  - Alone: ending **The Sofia Commune**, SRD → `SRD_SOFIA` "Sofia".
  - Each stage: claims + war goals on the next group; opens when every state of the previous group is held (by us
    or a faction member); cores on the held states come with the next stage/ending.
- Between the paths: The People's Militia, Komsomol of the Housing Estates (manpower).
- **Party branch**: Party Takes the Largo, Red Guards of Vasil Levski Stadium (4 divisions via `load_oob`), Arm the
  Workers, Barricades on Vitosha Boulevard, Every Comrade Serves, Commissars in Every Unit, Red Wings over the
  Centre, The Shelters Beneath the Centre, Red Officer School, Tram Depot Tank Works.
- **Henry branch**: Red Leaflets over Vitosha → **The Road to Boyana** (Georgi of Lozenets is asked as Victor's day
  one to **join the fight** as an ally — not military access; skipped if LOZ is gone or already an ally; AI odds by
  opinion; refusal → choose war goal on Lozenets or let it go) → The Capel Question (war goal) → Red Flag over
  Boyana (needs all of Vitosha held).
- **Economy**: Collectivise Vitosha Boulevard, **Mimas Döner for the Workers** (Mimas is a real 24h döner place in
  the centre; spirit "Mimas Döner"), Party Arsenal, Red Tourism, Red University, Socialist Emulation, Five-Year Plan,
  Star on the Party House (research slot), Electrify the Districts.

### Authoritarian path (Order in the Centre)
- Curfew on the Largo + The Centre's Own Guard → **Who Stands with Sredets?** → four mutually exclusive branches:
  1. **A Free Sredets** (reworked twice on request: "focus on freedom, kinda like a democratic regime"; then "a bit
     larger and better organised", no elections, Victor stays, blue, new flag, last focus renames to "Free Centre of
     Sofia", peaceful offers to Anton, Georgi, Alexander that are "most likely to decline" but random, by opinion
     and democracy). Root at x=20: democracy (elections_allowed = no), Victor a liberalism leader, cosmetic tag
     `SRD_FREE` "Free Sredets" (blue), spirit with the no-faction rule. Third version (the user found a grid of four
     equal columns "robot like", wanted fewer focuses and lengths by importance, not all 70 days): 16 focuses,
     3-10 weeks. Speakers' Corner (3w) → Free Press (4w) → Friends of Freedom (4w, +15% democracy, +30 opinion in OBR,
     LOZ, TRD) → An Offer to Anton / An Offer to Georgi (3w each) → An Offer to Alexander (needs both); Speakers'
     Corner → Open Market on Vitosha (8w); Volunteers (5w) → Liberty Guard (7w) → Drills in Borisova Garden (4w);
     Workshops of the Free Centre (10w, needs the Market AND the Guard) → Liberate the Old Centre (6w, VAZ+OBR) →
     The Wider Centre (8w, needs Liberate AND the offer to Alexander; central states of TRD, LOZ, KRS, SRK in
     `WIDER_CENTRE`, `take_state_focus` war goals) → A Free Centre (5w, cores) → The Free Centre of Sofia (10w,
     cosmetic tag `SRD_FREE_CENTRE`, news 13). Offers: event srd.17, yes = peaceful annexation, AI odds
     `FREE_YES`/`FREE_NO` (base 5 vs 80, up with opinion and democracy). The offers use person icons (metalcircle,
     SilverStarFrame, SunStarFrame with handshakes), which need the portraits. The user was upset when they thought
     the friends' icons had been changed: tree renders made without portraits show pack fallbacks, say so up front.
     Flag (`red_flags.free`): blue with dawn rays, white disc with the red rhombuses in a silver laurel
     wreath, no band at the bottom (the user did not want it to look like the communist flags); the Free Centre's
     has the arms of Sofia in the disc and the rhombuses in white above. The rest of the authoritarian path moved
     4 columns right to make room.
  2. **Call the Evil Gang** (photo icon of the group): faction "The Evil Gang"; invite Anton, Georgi Y., Poryazov,
     Stefan, Alexander, GrimBoss, then "Even Henry?" (each a person icon with a handshake, different frame; AI odds
     by opinion, Georgi +25 as day one, Henry halved, communists unlikely); The Evil Gang Rules Sofia.
  3. **Unleash the C Class** (photo icon of the group): faction "The C Class Hools"; Ultras of the Stadium, Flares
     and Firecrackers, Away Day, Pitch Invasion, Recruit the Firms ("join or get hit" to every neighbour outside a
     faction; weaker ones accept more; refusal = war goal), Home Ground, Champions of Sofia.
  4. **The Physics Teacher Steps In**: Konstantin Ilchev becomes leader (character `SRD_ilchev`, portrait
     `tools/portraits/SRD_ilchev.png`); Newton's Laws of Government, Laboratory of the Nation, Homework for
     Everyone, Pop Quiz for the Army, E = mc², The Final Exam, Grades Are Final.
- The user originally mentioned fascism might become part of the authoritarian side later.

### Over time, not at once (user's rule)
- No `add_popularity`/`set_popularities` anywhere: timed spirits with `communism_drift`/`democratic_drift`
  (Red Agitation and The Curfew Lifted 0.4/day for 240 days on the two roots; Comrades from Sredets, Red Newspapers,
  Party money, Doctors' Garden rally, Red Leaflets, A Red Oborishte; Speakers' Corner, Newspapers from Sredets on
  every neighbour, Friends of Freedom, Mom Was Wrong). The government changes with a focus (the user asked for focuses at
  a percentage, 30%): Proclaim the Sredets Commune (8,1; communism > 0.3; the Oborishte and Party branches need it,
  the communist tree moved one row down) and Proclaim the Free Sredets (20,4; democratic > 0.3; Friends of Freedom
  and Liberate the Old Centre need it). They set government, leader role, flag and name, and send the news.
  An earlier "Road to Power" decision category for this was replaced by these focuses.
  The communist endings and the Free Centre of Sofia need the right government.
- Generic decisions for every district (`tools/decisions_world.py`): War Propaganda, Public Order Campaign, four
  ideology campaigns (one at a time), Recruitment Drive; at war: War Bonds, Call Up the Reserves, Rationing. All
  are timed spirits. Vanilla's decision files stay replaced (they are written for the world map).
- Prove Henry's Mom Wrong (free branch, needs Free Press AND Open Market): event srd.20 to Vitosha, his mother admits
  the centre is not communist; Henry +40 opinion of Sredets, Mom Was Wrong spirit; srd.21 back to Sredets.
- Henry's mother is never placed in Boyana (user's request); Henry's district is Vitosha.
- Prove Henry's Mom Wrong now sends world news 14 ("Henry's Mom Was Wrong"); the effects on Henry come with the focus.
- Offers: only Anton is asked to join whole (srd.17, annexation, "I need him all"); Georgi and Alexander get srd.20 and
  hand over only North Lozenets + Lozenets / Triaditsa (the states the formable needs); yes → srd.21, no → srd.19.
  The Wider Centre's war goals skip a district that no longer owns any of those states.
- Restructure (user's design): the authoritarian road (after Who Stands with Sredets?) is now A Free Sredets (x20),
  The Dream of a United Centre (x28, the "normal path") and Ilchev (x34, only from 1937: `date > 1937.1.1`, news 12
  says the people of Sredets waited long enough). United Centre: Order on the Boulevards, The Centre's Army,
  Workshops / Arsenal of the Centre, Unleash the C Class Hools (one focus for now; only without the Evil Gang;
  the old 7-focus C Class branch and its "join or get hit" events are gone), March on the Old Centre (VAZ),
  The Centre Takes Shape (cores held VAZ; claims/war goals on the central states), The Centre Is One (cores held),
  then a fork: Bring Anton In → The United Centre (annex OBR) or Anton at Our Side → The Centre and Oborishte
  (guarantee or faction); both send news 16. Cores at once here too (see the fixes below).
  The user will say more about the C Class later.
- Evil Gang = separate faction tree at x39-45 from y0 (any road except the free one; A Free Sredets is not
  possible once it exists): Propose the Evil Gang (focus id call_the_evil_gang, keeps the photo icon) creates the
  faction and sends letters to Georgi Poryazov now, Henry in 30 days, Stefan in 60 (event srd.11; a refusal sets
  SRD_refused_the_gang); Destroy Henry / Destroy Stefan (only after a refusal); The Vitosha Award (Vienna Award
  style, once Vitosha is gone: Simeonovo to MLA, Knyazhevo + Marchaevo to KRP, Dragalevtsi + Zlatni Mostove to LOZ,
  Karpuzitsa to TRD, if they are in the gang; Sredets keeps Vitosha; news 15); Invite Georgi Yanchovichin, then
  Alexander and Anton; The Evil Gang Rules Sofia. Dropped: the GrimBoss invitation and Even Henry?.
- Fixes after v33: Ilchev never became leader (his character had no role and was not recruited): the character
  now has a country_leader role (build_map.py EXTRA_CHARACTERS) and the focus does recruit_character +
  promote_character. Propose the Evil Gang needs Who Stands with Sredets? (so not on the communist road). The United
  Centre cores at once too (March on the Old Centre: VAZ, The Centre Takes Shape: central states, Bring Anton In:
  OBR). The Vitosha Award gives Sredets nothing: every state goes to the nearest friend in the gang (Vitosha and
  Karpuzitsa → TRD, Simeonovo → MLA, Marchaevo and Knyazhevo → KRP, Dragalevtsi and Zlatni Mostove → LOZ), with
  fallbacks in VITOSHA_SHARES when a friend is not in the gang.
- Authoritarian road rebuilt (v36): The Dream of a United Centre (x29) with four lines. The Grip on the Centre
  (new mechanic): variable SRD_grip 0-100 (flag SRD_grip_active), scripted effect SRD_update_grip keeps one of
  three spirits (loose <30, firm 30-69, iron 70+), monthly drift in common/on_actions/evil_sofia_srd_on_actions.txt
  (-2 at war with stability <40%, +1 with stability >60%), decision category SRD_grip (Patrol the Boulevards, Bread at
  the Women's Market, Night Raids, Parade on Tsar Osvoboditel, and the targeted decision Send an Ultimatum: Grip 50+,
  costs 15; target submits → puppet, refuses → war goal and Grip +5; events srd.22-24). Focuses: Order on the
  Boulevards, Checkpoints on the Bridges, The Night Watch, Informers in Every Café, Ultimatums from the Largo, The
  Iron Grip. Conquest: The Centre's Army, March on the Old Centre, The Centre Takes Shape, The Khan Must Fall (only
  while Khan Krum leads Serdika: has_country_leader SRK_leader) → Krum's Cup (news 18), The Centre Is One, Bring
  Anton In / Anton at Our Side, The United Centre / The Centre and Oborishte. C Class Hools (faction, only without
  the Evil Gang): Unleash, Call Alexander (TRD) and Call Georgi Poryazov (MLA) (event srd.25, AI says yes 90%),
  Away Days, Champions of Sofia. Formable: Proclaim the Directorate of Sofia (Grip 70+, centre held; cosmetic tag
  SRD_DIRECTORATE, flag red_flags.directorate, trait The Director, news 17), One Directorate (annex subjects, cores
  everywhere owned), Sofia Answers to the Director. The free road can turn evil: A Temporary Emergency (alternative
  to The Free Centre of Sofia; despotism again, Grip 50, ultimatums; news 19) also opens the Directorate.
  Workshops/Arsenal of the Centre were removed (the industry tree replaces them). Ilchev moved to x37-39, the Evil
  Gang to x43-49.
- Shared trees, open on every road: industry (x51-57, 15 focuses: factories, slots, a research slot, construction
  and factory output spirits) and military (x59-65, 16 focuses: tech bonuses for infantry weapons, artillery,
  armour, doctrine, air; army/air experience; anti-air and radar; spirits).
- The C Class Hools and the Evil Gang exclude each other both ways (Unleash needs no Evil Gang; Propose needs no
  C Class). Every country has five default military advisors (tools/military_advisors.py → common/characters/
  evil_sofia_military.txt): an army theorist (+0.1 army experience a day), an air theorist (+0.1 air experience),
  an artillery expert and an entrenchment expert (high command) and an air chief; custom traits, like the political
  advisors (untested in game).
- Watch for duplicate focus ids across branches (a new `one_centre` once collided with the communist one).
- Later tweaks: spirits on other districts cut to about a quarter (comrades 0.06, red newspapers 0.05, party money
  0.04, rally 0.05, leaflets 0.04, newspapers from Sredets 0.03, friends of freedom 0.06, mom was wrong 0.04, a red
  Oborishte 0.08); thresholds scaled with them (Ally Anton 20%, Red Coup 30%, AI odds in ANTON_YES/GEORGI_YES/
  FREE_YES). The democratic branch cores at once (Liberate the Old Centre: VAZ+OBR; The Wider Centre: the central
  states), and peaceful handovers are cored (srd.18, srd.21).
- Private events: no picture unless the user made one (user: "for the private ones you may not use pictures").
  The user makes world news pictures; done so far: news_1, srd_2.

## 6. Events

- `events/evil_sofia_srd.txt` (16): Henry's reaction, Anton's offer and replies, Henry hates us / prepares for war,
  Georgi's day-one call and replies, red coup, Evil Gang invitation and replies, C Class "join or get hit" and replies.
  Notification events always go back to Sredets so the player sees the answer.
- `events/evil_sofia_news.txt` (12, `major = yes`): Sredets red / order, the pact, Oborishte falls, Boyana falls,
  both endings, any district capitulating (from `on_capitulation`), the four authoritarian branches.
- `events/evil_sofia_flavour.txt` (9 random events, MTTH 3600–5400 days, once per country, 2-year cooldown): trams
  stop, Levski–CSKA derby, the big snow, the pothole committee, price of a döner, stray dogs, weddings, black
  market on the Women's Market, hikers on Cherni Vrah.
- Pictures: drawn by `tools/event_pictures.py` (flags waving over a Sofia skyline, mood: day/dusk/night/snow/rain/
  heat/fire, aged photo look) unless the user's own `tools/event_pictures/<event_key>.png` exists. The user said the
  drawn ones "don't match the hoi4 vibe" and is making real ones. Sizes: country 210x176, news 397x153.

## 7. How the icons are made

### Pack icons
- Two GFX packs, cloned read-only:
  - `https://github.com/DuoDex/hoi4GFX` → `/home/user/duodex/hoi4gfx` (finished focus icons in `goals/`,
    `focuses/`, `Grestin's Icon Pack/Completed Icons`; frames in `Focus Backgrounds/Even More Background/
    Backgrounds PNG/`). No licence stated.
  - `https://github.com/Globvs/Ultimate-HOI4-GFX` → `/home/user/globvs/ultimate-hoi4-gfx` (pieces in `Focus &
    National Spirits Pieces/`, `National Spirit Backgrounds/`; free to use with credit, `CREDITS.txt`).
- In `focus_sredets.py` an icon is `"duo:<name>"` (finished DuoDex icon by file name), `"person:<key>"`,
  `"photo:<key>"` or `"custom:<key>"`. Used pack icons are cached as PNG in `tools/icons/` (committed), so the packs
  are only needed for new icons.
- To choose icons: grep the pack's file names, render candidates on a contact sheet, look, pick; avoid flags of
  real countries.

### Person icons (`tools/focus_icons.py`, `PERSON_ICONS` in `focus_sredets.py`)
- Entry: `key: (portrait file in tools/portraits, frame file, front piece or None, rotation, options)`, options:
  `fill` (colour of an empty ring's middle), `front_width`, `front_y` (where the piece sits below the chin).
  Rendered with `bust_width=1.1, head_room=0.04`.
- `cutout()`: the portraits have plain painted backgrounds. Edge-based flood fill from the top corners and upper
  sides through smooth, background-coloured pixels; background colour per row (learned from the edges, refined in 2
  passes); extra cleanup only below the faces (y > 0.54h) and in the outer 28% of columns (shoulders); opening,
  keep the largest part, closing (chin leaks), fill holes, slight erosion (halo). OpenCV is not available
  (installing it was refused), so it is numpy/scipy/PIL only.
- `bust()` keeps head and shoulders; `black_and_white()` greyscale + autocontrast.
- `frame_parts()` finds the frame's inner circle (empty ring or dark middle); the person is clipped to it, the ring
  drawn over him, then the piece (handshake/sword/rifles/book) in front.
- Frames that work: RedWheatFrame, SpikyFrame, Kill_Frame, SilverStarFrame, CircleFrame, LeavedFrame, metalcircle,
  SunStarFrame. Grander_Star_Fcous_Frame does not (fill not detected).
- History of user feedback: Henry and Anton were first cut badly (only eyes/hair) → fixed; Stefan's chin was cut and
  bits of background stayed on the shoulders → fixed; handshake hid the face → piece moved lower; the user approved
  the result ("they are fire!!!").

### Photo icons (group photos)
- `photo_icon()`: crop box of the photo, black and white, filling the frame's inner area, ring on top.
  `PHOTO_ICONS = {"evil_gang": ("EVIL_GANG", "SpikyFrame.png", box, None), "c_class": ("C_CLASS",
  "LeavedFrame.png", box, None)}`.

### Custom icons
- Döner (bread + knife + fire in RedWheatFrame), stadium (soldiers in rows + red star in LeavedFrame), national
  spirit icons = a background from `National Spirit Backgrounds` + a piece.

### Flags
- District flags: `tools/flags/<TAG>.png` (cropped from the user's sheet), written as TGA 82x52, 41x26, 10x7.
- Communist flags (`tools/red_flags.py`, drawn at 4x and scaled down): Sredets = red, four gold rhombuses in a
  wheat wreath, star, white and gold stripe at the bottom; Oborishte = crimson, gold rings turned into a cog with the
  hammer and sickle, gold hoist band with three stars; Sofia = arms of Sofia (`tools/flags/SOFIA.png`) in a wreath
  on red; South/North Sofia = white band bottom/top.
- Ideology flag names: `TAG_communism.tga`; cosmetic tag flags `SRD_RED.tga` etc.

## 8. Technical knowledge (HOI4 modding, things learned the hard way)

- `map/definition.csv` needs **CRLF** line endings or the game drops the continent column and fails to load the map.
- The stock tutorial refers to vanilla states/provinces and crashes on this map: `tutorial/tutorial.txt` is replaced
  by a block that names nothing.
- A strategic region whose box centre falls outside its provinces exactly on the middle column crashes the game
  (divide by zero); the generator checks this.
- Province bounding boxes must stay under ~174 px tall ("TOO LARGE BOX").
- Vanilla on_actions, events, decisions, bookmarks, history are replaced (`replace_path` in `descriptor.mod`).
- Bookmark minors only show as small flags if they have a focus tree → starter tree for the 16 non-featured.
- Localisation in `localisation/english/replace/`, UTF-8 with BOM; **every key unique across files** (idea keys
  collided with focus keys twice: an idea must not be named `SRD_<focus id>`). Line breaks must be written as `\n`
  inside the quotes; the build escapes real newlines and quotes (`L()` in `build_focus.py`).
- Focus x spacing is tight: neighbours in adjacent columns on the same row have overlapping labels.
- `continuous_focus_position = { x = 50 y = ... }` moves the continuous focus panel.
- Cosmetic tags need colours in `common/countries/cosmetic.txt`.
- Leader description: `desc = "KEY"` inside `country_leader`.
- Advisors: characters with `advisor = { slot = political_advisor|army_chief idea_token = ... allowed = {
  original_tag = X } traits = { ... } cost = ... }`; custom traits in `common/country_leader/`.
- News: `news_event = { id = ... }` with `major = yes` in the event goes to everyone; FROM = the sender.
- MTTH events: `trigger` + `mean_time_to_happen = { days = N }`; once per country via a country flag; cooldown via
  `set_country_flag = { flag = X days = 730 }`.
- `NOT = { A B }` means neither A nor B.
- Uncompressed BGRA DDS (`write_dds_bgra` in build_map.py) works for every texture used.
- Start date was once moved with `NGame.START_DATE`/`END_DATE` defines; now vanilla again.
- Road to 56 compatibility: not compatible as a whole (it rewrites vanilla content); its core/claim map mode was
  rebuilt instead (scripted map modes in `common/map_modes/`, colours via temp variables red/green/blue/alpha).

## 9. Tools and environment used

- Claude Code cloud session; Python 3 with numpy, scipy, Pillow (no OpenCV). Bash, file tools, WebSearch.
- Blocked by the network: Overpass API, MapIt, Wikipedia, hoi4commands.com. GitHub works.
- Refused by the safety classifier (do not retry): installing OpenCV, curling the proxy status page.
- A fresh container needs `pip install numpy pillow scipy tifffile` before any build.
- Geodata: `tools/fetch_geodata.py` downloads the kvartali GeoJSON into `tools/geodata/` (git-ignored).
- Builds: full `tools/build_map.py` ~8 min; `tools/dev/build_focus_only.py` seconds; `tools/dev/validate_map.py .`
  must print `0 errors, 0 warnings`; `tools/dev/render_tree.py out.png` draws the built tree.
- Vanilla game files are not available in the container (could not shift tech years; dropped when the start date
  went back to 1936).

## 10. Open ideas / not done yet

- Focus trees for the other featured friends (only Sredets has one; the rest use the starter tree).
- Fascism possibly inside the authoritarian path.
- Event pictures from the user replacing the drawn ones (news 1 done). The user's pictures are treated like
  photos: git-ignored, only in the zip.
- Untested in game: advisor traits, the no-faction rule, `major = yes` news, `strength_ratio` odds,
  `[From.GetLeader]` in event titles.
