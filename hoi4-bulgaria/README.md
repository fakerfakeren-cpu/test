# Bulgaria: The Tsar's Balance (`bfx_bulgaria` v3.1) — HOI4 1.19 mod

A 250-focus tree for Tsar Boris III's Bulgaria, built as **two big paths that each split once**, plus a secret path:
- **The Tsar's Way** expands by diplomacy, proxies and selling Bulgaria's alliance to the highest bidder (*the Bulgarian Auction*).
- **The Legionary Revolution** expands by war, and needs war to survive (*Revolutionary Momentum*).

Shared mechanics: **Shackles of Neuilly** (covert rearmament against growing Balkan suspicion), **The Tsar's Balance**
(Crown, Army, Legions and IMRO competing for power) and **The Macedonian Uprising** (IMRO raises a real civil war in Yugoslav Macedonia).
Base game only (no DLC needed). The descriptor lists Road to 56 as a dependency, but the mod overrides no vanilla or R56 files.

## Install
1. Unzip `bfx_bulgaria_v3.1.zip` into `Documents/Paradox Interactive/Hearts of Iron IV/mod/`, replacing any older
   `bfx_bulgaria` folder and `bfx_bulgaria.mod`. You should have **both** `mod/bfx_bulgaria.mod` and `mod/bfx_bulgaria/`.
2. Enable **Bulgaria: The Tsar's Balance** in the launcher playset, below Road to 56 if you use it.
3. Start a **new** game (the mechanics are set up on game start, not on old saves).

## The paths
**The Tsar's Way** (*The Tsar Steps Forward*). Five trunk columns side by side: the Court, the Bulgarian Auction, Macedonia by proxy
(IMRO and the uprising), Dobruja and the Aegean (Craiova, the Thracian ultimatum), and armed neutrality (Fortress Bulgaria). They meet at
*The Crossroads of 1941*:
- *The Kingmaker*: join the highest bidder, collect the partition dividend, and keep a door open to **change sides** when your patron starts losing.
- *The Balkan Hegemon*: no patron. Run your own Sofia Pact, take everyone's money, and send **ultimatums** to Belgrade, Athens, Bucharest and Ankara:
  cede the province, or face a war goal.

**The Legionary Revolution** (*The Legions March*, needs Legion influence 40+). The trunk takes power, mobilises and fights the first wars for
Macedonia and Thrace. From *The Revolution Must March*, **Momentum** rises at war and decays in peace: spend it on storm offensives, levies and
purges, or the movement fractures (below 15) or devours itself (above 90). It splits at *The Legion's Destiny*:
- *Lukov's Axis Crusade*: Berlin's ally. The New Order, Panzers for Sofia, the war in the East, Budjak and Odessa, the Black Sea, and the Bosporus.
- *Tsankov's Imperium*: answers to nobody. The Pact of Iron with Hungary, wars for the Straits, the Danube and Albania (against Italy if it holds it), and three seas.

**Secret: the Coburg Restoration.** It appears on the far left when Tsar Boris dies (from August 1943, Tsar's Way only) or when the third
*Letter from Coburg* arrives. The letters are a random event, about 7% a month from 1937; after the first one, the decision
*Answer the Letter from Coburg* speeds them up. The secret path is closed once the Legions march. Old Ferdinand returns:
proclaim the Third Bulgarian Empire, or march on Tsargrad.

## Test checklist (please report back)
1. Steam → HOI4 → Properties → Launch options: add `-debug`.
2. Start 1936 as Bulgaria. Check the tree name, the spirits (*Shackles of Neuilly*, *Covert Rearmament*, *The Tsar's Balance*) and the decision tabs.
3. **Tsar test**:
   1. Use `focus.autocomplete` up to *Receive the Envoys*.
   2. The *Bulgarian Auction* tab should show three live numbers. Flirt with Berlin and check the numbers move.
   3. Complete *The Auction Closes* and check you get the right patron's reward.
4. **Change Sides test**:
   1. Take the Kingmaker branch, join Germany, and complete *The Contingency Plan*.
   2. In 1944, or once Germany's surrender progress passes 25%, click *Change Sides*.
   3. Report what happens: do you leave the Axis, get peace, get an invitation, and end up at war with Germany?
5. **Legion test**:
   1. Raise the Legions to 40: pick "Let the Legions march" in *The Shadow Parties* event (+15) and use *Patronise the Legions* (+10 each). Then take *The Legions March*.
   2. After *The Revolution Must March*, the *Revolutionary Momentum* tab and the modifier should appear.
   3. Watch momentum fall at peace and rise at war.
6. **Uprising test**:
   1. Take *Tolerate IMRO* (opening) and then *The Macedonian Committees* (Tsar).
   2. Push unrest to 70, then click *Raise the Ilinden Banner*.
   3. Check that Yugoslavia gets a civil war and a red-lion *Independent State of Macedonia* appears.
7. **Secret test**: run `event bfx_court.20` (Boris dies). *The Old Fox Returns* should appear on the far left.
8. **Formable colour test**: complete *Greater Bulgaria* (Kingmaker) or *The Balkan Tsardom* (Hegemon) and see whether the map colour changes.
9. Paste every `bfx` line from `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` back to me.

## Rebuilding
`python3 tools/make_portraits.py <names>` → `python3 tools/build_mod.py` → `python3 tools/validate.py` → `python3 tools/write_docs.py`.
The generator is `tools/build/*.py` (one module per path: `focus_opening`, `focus_tsar`, `focus_legion`, `focus_secret`, `focus_eco_mil`).
See `DESIGN.md` for every focus, spirit, character and rule.
