# Bulgaria: The Tsar's Balance (`bfx_bulgaria` v2.0) — HOI4 1.19 mod

A 209-focus tree for Tsar Boris III's Bulgaria and the Legionary movement that wanted to replace it, plus a secret path.
Three mechanics: **Shackles of Neuilly** (covert rearmament against growing Balkan suspicion), **The Tsar's Balance**
(Crown, Army, Legions and IMRO competing for power, with coups, crises and Boris's death) and **The Macedonian Uprising**
(IMRO raises a real civil war in Yugoslav Macedonia that you feed, then absorb).
Base game only (no DLC needed). Works with or without Road to 56.

## Install
1. Unzip `bfx_bulgaria_v2.0.zip` into `Documents/Paradox Interactive/Hearts of Iron IV/mod/`, replacing any older
   `bfx_bulgaria` folder and `bfx_bulgaria.mod`. You should have **both** `mod/bfx_bulgaria.mod` and `mod/bfx_bulgaria/`.
2. Enable **Bulgaria: The Tsar's Balance** in the launcher playset, below Road to 56 if you use it.
3. Start a **new** game (the mechanics are set up on game start, not on old saves).

## Test checklist (please report back)
1. Steam → HOI4 → Properties → Launch options: add `-debug`.
2. Start 1936 as Bulgaria. Check:
   - the focus tree name;
   - the national spirits, including *Shackles of Neuilly*, *Covert Rearmament* and *The Tsar's Balance*;
   - the decision tabs *Shackles of Neuilly* and *The Tsar's Balance*, which should show live numbers.
3. Console (`~`):
   - `event bfx.1`
   - `event bfx_court.11` (Legion march)
   - `event bfx_court.20` (Boris dies; the secret branch should appear)
   - `focus.autocomplete`, then click through a path
   - `observe` to watch the AI.
4. **Uprising test**:
   1. Take *Tolerate IMRO*.
   2. Run the raid decisions until unrest reaches 70, or use the console to finish their timers.
   3. Click *Raise the Ilinden Banner*.
   4. Check that Yugoslavia gets a civil war and a red-lion *Independent State of Macedonia* appears.
5. **Formable colour test**: complete *Greater Bulgaria* (Tsar path) and see whether the map colour changes.
6. Paste every `bfx` line from `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` back to me.

## The paths
**Tsar Boris III.** Boris steps forward, muzzles the Military League and chooses how to be aggressive.
- *Walking Between the Raindrops*: the historical opportunist. A pact with Turkey, Southern Dobruja returned at Craiova, the Tripartite Pact,
  then the Axis Partition hands over Macedonia and Thrace. After that come the Western Outlands and the Bessarabian Bulgarians, the choice to stay out
  of the Eastern Front or join it, Greater Bulgaria, the Straits, and finally San Stefano.
- *The Balkan Hegemon*: no patrons. Your own Sofia Pact with Hungary, a pact with Moscow, an Albanian protectorate, then four war plans against
  Yugoslavia, Greece, Romania and Turkey, client kings and the Tsardom of the Balkans.

**The Legions.** Push the Legions' influence to 40, then march on Sofia: the Tsar appoints General Lukov, or the Palace Guard fights a civil war.
- *Lukov's Axis Legion*: full Axis partner, the Balkan Blitz, the New Order, the crusade in the East, Budjak and the Odessa corridor, and on to the Bosporus.
- *Tsankov's Imperium*: fascist but answering to nobody. The Pact of Iron with Hungary, rivalry with Rome over Albania, and wars for Macedonia,
  the Aegean, the Danube and the Straits, ending as the Bulgarian Imperium.

**Secret: the Coburg Restoration.** Hidden until Tsar Boris dies (from August 1943) or three letters arrive from Coburg. Old Ferdinand
returns. Proclaim the Third Bulgarian Empire and chase Simeon's borders to a coronation at Tarnovo, or march on Tsargrad, sing mass in Hagia Sophia,
restore the Byzantine themes and move the capital to Constantinople.

## Rebuilding
`python3 tools/make_portraits.py <names>` → `python3 tools/build_mod.py` → `python3 tools/validate.py` → `python3 tools/write_docs.py`.
See `DESIGN.md` for every focus, spirit, character and rule.
