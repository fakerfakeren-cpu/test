"""Regenerate DESIGN.md from the build data (run after build_mod.py)."""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "build"))
sys.path.insert(0, HERE)

import focus_spec, ideas, characters, events, mechanic, tree  # noqa: E401,E402

F = focus_spec.FOCUSES
blocks = Counter(f["block"] for f in F)
stat = sum(f["kind"] == "stat" for f in F)
n_events = sum(len(v) for v in events.EVENTS.values())
mechanic.decisions()
n_dec = sum(len(v) for v in mechanic.DECS.values())

idea_rows = "\n".join(f"| `{i[0]}` | {i[3]} | {', '.join(f'{k} {v:+g}' for k, v in i[2].items())} |" for i in ideas.IDEAS)
char_rows = "\n".join(f"| `{c[0]}` | {c[1]} | {', '.join(r['kind'] + (' (' + r.get('ideology', r.get('slot', '')) + ')' if r.get('ideology') or r.get('slot') else '') for r in c[3])} | {c[4]} |" for c in characters.CHARS)
cos_rows = "\n".join(f"| `{k}` | {v[0]} | rgb{v[3]} |" for k, v in mechanic.COSMETIC.items())

text = f"""# DESIGN — Bulgaria: The Tsar's Balance (`bfx_bulgaria` v2)

Target **Hearts of Iron IV 1.19.4** (`supported_version = "1.19.*"`), base game only, Road to 56 compatible.
Generated from `tools/build/*.py` by `tools/write_docs.py`. The mod itself comes from the same data.

## Scope (v2 rework)
The mod is about the Bulgaria that existed: **Tsar Boris III's non-aligned kingdom** and the **Legionary (fascist) movement**
that wanted to replace it, plus one **secret path**. The Communist and Agrarian/democratic paths from v1 were removed.

| Block | Focuses | What it does |
|---|---|---|
| Opening | {blocks['opening']} | 1936 crisis, Velchev trial, partyless regime, IMRO (crush or tolerate), Neuilly (Salonika vs. tear it up), the Italian Queen, **Open the Chancelleries** (factions, guarantees, volunteers and pacts for a non-aligned state) |
| Tsar Boris | {blocks['tsar']} | (a) *Walking Between the Raindrops*: Axis opportunist (Turkish pact, Craiova, Tripartite Pact, the Axis Partition, Outlands, Bessarabian Bulgarians, Eastern Front yes/no, Greater Bulgaria, Straits, San Stefano). (b) *The Balkan Hegemon*: own faction (Sofia Pact), Hungarian partner, Soviet pact, Albanian protectorate, four war plans (Yugoslavia, Greece, Romania, Turkey), client kings, Balkan Tsardom |
| The Legions | {blocks['fascist']} | Needs Legion influence 40. The March on Sofia (appointment or civil war). (a) *Lukov's Axis Legion*: Into the Axis, Balkan Blitz, New Order, Crusade in the East, Budjak, Odessa corridor, Thrace to the Bosporus. (b) *Tsankov's Imperium*: fascist but independent, Pact of Iron with Hungary, rival to Rome, wars for Macedonia, the Aegean, the Danube and the Straits, the Bulgarian Imperium |
| Secret: the Coburg Restoration | {blocks['secret']} | Hidden (`allow_branch`) until Boris dies (Aug 1943+, random) or three letters from Coburg arrive. Ferdinand returns. (a) Third Bulgarian Empire: Simeon's borders, Tsar of the Vlachs, Tarnovo coronation, Kaloyan's revenge. (b) Tsargrad: Basileus, Hagia Sophia, the Themes, the Varangian Guard, Orthodox crusade, capital moved to Constantinople |
| Industry | {blocks['eco']} | Tobacco and rose exports (3 stages), German clearing vs. diversification with a follow-up event, Pernik coal and Balkan iron, Kremikovtsi, Kazanlak and Sopot arsenals, electrification and the Iskar dams, railways, ports, roads, chemicals, Tyulenovo oil, synthetic fuel, fuel reserves, war economy. **Nuclear line**: Nadjakov's laboratory, Bukhovo uranium, Atomic Commission, reactor, the Kozloduy pile, the Rila device (date-gated 1938–1944) |
| Military | {blocks['mil']} | Army doctrine 12 (mountain warfare, Chataldzha lessons, staff academy, bayonet tradition, armoured brigade), equipment 8, **manpower 9** (reservists, emigration volunteers, Rhodope battalions, veterans, women's auxiliary, universal service, mobilisation law, national army), navy 10, air 11 (PZL and Avia purchases, Dornier bombers, paratroopers) |

Total **{len(F)} focuses**; plain stat bumps {stat} ({100 * stat // len(F)}%). Every exclusive choice says what it rules out.
Every focus has `search_filters` and `ai_will_do`.

## Realism and balance rules
* **Cores only on historically Bulgarian lands**: Southern Dobrudja (77), Vardar Macedonia (106), Western Thrace (184), Edirne (341),
  and Central Macedonia (731) once compliance passes 40%. Everything else is **claims and war goals**, which is where the aggression comes from.
* **Integration decisions** core other held land only once its *compliance* is high enough: Bulgarian lands 35%, Greece and Albania 60%,
  Serbia and Romania 65%, Anatolia 70%, the Pontic coast 75%. They cost political power and a little stability, and can be repeated as compliance rises.
* **Diplomacy works**: *Open the Chancelleries* (and the Legionary State) lift the non-aligned limits with `set_rule`. The *Sofia Chancellery*
  decisions propose non-aggression pacts (Turkey, Romania, Greece, Yugoslavia, USSR, Hungary, Italy), ask for guarantees (Germany, Italy, Britain, France),
  invite countries to your faction, give guarantees and demand Southern Dobruja. Several focuses do the same by event (Turkish pact 1941,
  Craiova 1940, the Sobolev mission 1940, the Albanian protectorate, joining the Axis).
* **Land by diplomacy**: Craiova returns Dobruja peacefully (much likelier with German backing). The Axis Partition hands over Macedonia and Thrace
  when allies hold them (as in April 1941). Skopje can ask to join after the uprising.
* Industry gives about one building per focus, two research slots at most in a playthrough, and the nuclear line is date-gated.

## Mechanic 1: Shackles of Neuilly (reworked)
* `bfx_rearm` (0–100) cancels the Neuilly penalties through the *Covert Rearmament* dynamic modifier. It **rusts by 1 a month**
  (0 after *Hidden Arsenals*).
* `bfx_suspicion` (0–100, starts at 15) **grows every month by 1 + rearmament/25**, so heavy rearmament is noticed fast.
* Thresholds 25 (protests), 50 (the Entente guarantees each other), 75 (embargo), 100 (the Petrich crisis) **re-arm** once suspicion
  falls 15 points below them, so penalties recur.
* Ends via the Salonika Agreement (negotiated: XP, good relations) or Tear Up Neuilly / Ferdinand burning the treaty (embargo and crisis).

## Mechanic 2: The Tsar's Balance (new)
Four blocs with influence 0–100, shown with their effects in the decision tab, driving the *Tsar's Balance* dynamic modifier:
* **Crown** → stability (−10%..+10%, minus IMRO violence) and political power (0..+20%). Drifts −1/month unless stability > 60%.
* **Army** → organisation (0..+8%) and army XP gain (0..+20%). Grows at war or with rearmament above 50.
* **Legions** → war support (−5%..+15%) and conscription (0..+10%). Grows with war support and fascist popularity; the Tsar's rule wears it down.
  **40 is required for the Legionary path.**
* **IMRO** → war-goal justification (0..−30%) at a stability cost. Grows while IMRO is tolerated.
* Crises (each re-arms after recovery): Army > 80 *The League Stirs*; Legions > 80 *The Legions March on Sofia*; IMRO > 80 *Murder in Sofia*;
  Crown < 20 *The Crown Totters*; Army < 15 *The Army Sulks*.
* **The death of Tsar Boris** (from August 1943, 25% a month while he rules): a regency under Filov, and the secret path is revealed.
* Nine court decisions: audiences, promotions, purges, patronage or bans for the Legions, subsidies or arrests for IMRO,
  the Metropolitan's blessing, and answering Ferdinand's letters.

## Mechanic 3: The Macedonian Uprising (new)
Tolerating IMRO unlocks raids, newspapers and arms caches that raise **unrest in Vardar Macedonia**. At 70 IMRO can raise the Ilinden banner:
Yugoslavia gets a **civil war** limited to Macedonia (25% of its forces defect). The rebels become the **Independent State of Macedonia**
(own name, flag and map colour, led by Ivan Mihaylov, with the *Ilinden Fervour* spirit). Bulgaria can send volunteers (manpower),
rifles, mountain guns and *Officers on Leave*, recognise and guarantee the state, or intervene openly. If the rising survives
8 months, or Yugoslavia starts to collapse, Belgrade makes peace. Six months later Skopje asks to join: annex it (cores) or keep it as a client.
If it is crushed, Bulgaria pays in stability and IMRO influence.

## Formables and colours
| Cosmetic tag | Name | Map colour |
|---|---|---|
{cos_rows}

Colours are in `common/countries/bfx_cosmetic.txt`. Every formable has its own generated flag.
*Proclaim the Bulgarian Empire* is open to every path that holds Macedonia, Thrace, Dobrudja and Edirne; its fascist name is the *Legionary Empire of Bulgaria*.

### Not done: new provinces and states
Splitting provinces or states (for example exact San Stefano borders) means editing the map definition, the province bitmap and the vanilla
`history/states` files. That overrides vanilla files and breaks Road to 56 and every other map-touching mod, which this mod's rules forbid.
Border realism therefore works at state level: historical cores, claims elsewhere, compliance-gated integration.

## Events ({n_events}) and decisions ({n_dec})
Events cover the opening, Neuilly thresholds, the court crises and Boris's death, diplomacy answers (pacts, guarantees, invitations,
Craiova, the Albanian protectorate, Axis entry), the March on Sofia and the attempt on Lukov, the uprising (news, peace, defeat, union),
the Coburg letters, Ferdinand's return, Hagia Sophia and Tarnovo, and five random flavour events.
Decision categories: Shackles of Neuilly, The Tsar's Balance, The Sofia Chancellery, The Macedonian Uprising, Integration, Tsargrad Propaganda.

## AI
On startup an AI Bulgaria rolls Tsar 72% (Raindrops 70% / Hegemon 30%) or Legions 28% (Axis 60% / Imperium 40%), and a 30% chance
to take the secret path if it is revealed. Fascist AIs patronise the Legions until they reach 40. No game rule needed.

## National spirits ({len(ideas.IDEAS)})
| ID | Name | Modifiers |
|---|---|---|
{idea_rows}

## Characters ({len(characters.CHARS)})
| ID | Name | Roles | Biography |
|---|---|---|---|
{char_rows}

## Full focus list
{tree.design_table()}
"""
with open(os.path.join(ROOT, "DESIGN.md"), "w") as fh:
    fh.write(text)
print("DESIGN.md", len(text))
