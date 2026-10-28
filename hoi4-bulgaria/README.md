# Bulgaria: Shackles of Neuilly (`bfx_bulgaria`) — HOI4 1.19 mod

A new 134-focus tree for Bulgaria with the **Shackles of Neuilly** rearmament mechanic, 4 political paths (8 sub-branches),
59 national spirits, 15 historical characters with new portraits, 35 events, 54 decisions and 10 formable identities, plus Imperial Integration decisions that can core land from the Adriatic to the Volga.
Base game only (no DLC needed). Works with or without Road to 56.

## Install
1. Unzip `bfx_bulgaria_v1.1.zip` into `Documents/Paradox Interactive/Hearts of Iron IV/mod/`.
   You should then have **both** `mod/bfx_bulgaria.mod` and the folder `mod/bfx_bulgaria/`.
2. Open the launcher, add **Bulgaria: Shackles of Neuilly** to your playset and enable it.
   If you use Road to 56, place this mod **below** Road to 56 (the descriptor declares a soft dependency on it so the launcher sorts it after R56 when both are on).
3. Start a new game (the mechanic is set up on game start, not on loaded saves).

## Test checklist (please report back)
1. Steam → HOI4 → Properties → Launch options: add `-debug`.
2. Start a 1936 game as **Bulgaria**. Check that the focus tree is *Bulgaria: Shackles of Neuilly*, that the
   **Shackles of Neuilly** and **Covert Rearmament** entries appear among the national spirits, and that the
   decision tab has the *Shackles of Neuilly* category showing both numbers.
3. Open the console (`~` key) and try:
   - `event bfx.1` (opening event), `event bfx_neuilly.13` (border crisis), `event bfx_alt.1` (Ferdinand)
   - `focus.autocomplete` then click through a path; `observe` to watch the AI play Bulgaria.
4. Open `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` and paste every line containing `bfx` back to me.
   Also note anything that looks wrong: blank icons, missing text, focuses that never become available.

## The paths
**The Tsardom (Boris III).** Boris drops the pretence of supra-party rule and muzzles the Military League. Then he chooses.
*San Stefano revanchism* courts Berlin, reclaims Southern Dobruja from Romania (by negotiation or war), liberates Vardar
Macedonia and Western Thrace, and finishes as **Greater Bulgaria on Three Seas** with claims reaching Albania and Montenegro.
*The Balkan Switzerland* fortifies the passes, courts the Balkan Entente, builds a **Balkan Concord** alliance, picks
London or a genuine third way, and can finish by peacefully uniting its allies in a **Danubian-Balkan Confederation**.

**The Coburg Restoration (alt-history).** If the cellars overflow (Covert Rearmament 80+ or the treaty torn up) and the
public is hungry for it, the old fox Ferdinand returns from exile, burns the treaty and pushes his son aside. He proclaims
the **Third Bulgarian Empire**, chases Simeon's borders to Wallachia and on to **Old Great Bulgaria** on the Ukrainian steppe.
Or he marches on **Tsargrad**, sings the liturgy in Hagia Sophia, restores the Byzantine themes and ends at the gates of the
**Exarchate of Ravenna**. The Tsargrad decisions core almost anything the empire once held.

**The Communists (BKP).** The outlawed party builds the Fatherland Front and seizes power on the Ninth of September:
peacefully if it is strong, by civil war if not. *Dimitrov* builds a Moscow-model People's Republic, joins the Comintern,
hands the Straits to Moscow and turns the Black Sea red. *Kolarov* goes his own way with a **Balkan Federation**: arming
Yugoslav, Greek, Albanian and Turkish partisans, ordering risings, integrating red neighbours, and growing it into a **Red
Danubian Federation** from Prague to the Bosporus.

**The Agrarians and Zveno.** Peasants and colonels try the 19th of May again. *Stamboliyski's heirs* restore democracy,
give land to the tiller, revive the Orange Guard and the **Green International**, then offer peaceful union to the peasant
democracies from the Aegean to the Baltic. *Zveno* installs a technocratic officers' state: fast modernisation, unstable
politics, the **Prussia of the Balkans**, and finally an **Anatolian Gambit** against Turkey.

## Coring everything
Every branch unlocks **Imperial Integration** halfway along. Its decisions core any land you hold, region by region,
across the whole Balkans and as far as Anatolia, the Caucasus, the Levant, Egypt, Italy, Central Europe, Ukraine, the
Baltic and the Volga. Hold Macedonia, Thrace, Dobrudja and Edirne to **Proclaim the Bulgarian Empire**; its name changes
with your ideology.

## Repository layout
- `mod/bfx_bulgaria/`, `mod/bfx_bulgaria.mod`: the mod (generated).
- `tools/build_mod.py` + `tools/build/*.py`: the generator (single source of truth for script and loc).
- `tools/make_portraits.py`: photo → HOI4 portrait pipeline. `tools/validate.py`: the static validator.
- `reference/`: game data used for checking (sprite catalogues, 1.19 script docs, state IDs).
- `DESIGN.md`, `CREDITS.md`.

Rebuild: `python3 tools/make_portraits.py && python3 tools/build_mod.py && python3 tools/validate.py`.
