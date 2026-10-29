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

text = f"""# DESIGN — Bulgaria: The Tsar's Balance (`bfx_bulgaria` v3)

Target **Hearts of Iron IV 1.19.4** (`supported_version = "1.19.*"`), base game only, Road to 56 compatible.
Generated from `tools/build/*.py` by `tools/write_docs.py`. The mod itself comes from the same data.

## Scope (v3 restructure)
Two big political paths instead of many small ones, each with its **own mechanic** and **one late split**, plus the secret path.
v2 had four sub-branches that all marched on the same four neighbours; v3 makes the two paths differ in *how* Bulgaria expands:
the Tsar by diplomacy, proxies and auctioning his alliance; the Legion by war, which it needs in order to survive.

| Block | Focuses | What it does |
|---|---|---|
| Opening | {blocks['opening']} | 1936 crisis, Velchev trial, partyless regime, IMRO (crush or tolerate), Neuilly (Salonika vs. tear it up), the Italian Queen, **Open the Chancelleries** (factions, guarantees, volunteers and pacts for a non-aligned state) |
| The Tsar's Way | {blocks['tsar']} | **Trunk** (5 columns side by side): the Court (muzzle the League, Simeon's birth, propaganda, the Tsar's men, royal arbitration); **the Bulgarian Auction** (receive the envoys, the German, British and Soviet offers, play them off, the Turkish pact, break the Entente, the auction closes); Macedonia by proxy (IMRO committees, Pirin bases, Ilinden, Macedonia rises, union with Skopje); Dobruja and the Aegean (Craiova, settlers, the Thracian ultimatum, the Aegean window); armed neutrality (Danube line, mobilisation, Fortress Bulgaria). **Split at the Crossroads of 1941**: (A1) *The Kingmaker*: sign with the highest bidder, the partition dividend, Outlands, Bessarabia, Eastern Front yes/no, **the Contingency Plan (Change Sides)**, Greater Bulgaria, San Stefano, Tsar of All the Bulgarians. (A2) *The Balkan Hegemon*: stand alone, the Sofia Pact, take everyone's money, Albanian protectorate, Hungary, **four ultimatums** (Belgrade, Athens, Bucharest, Ankara: cede or face a war goal), client kings, Black Sea dominion, Balkan Tsardom |
| The Legionary Revolution | {blocks['fascist']} | Needs Legion influence 40. The March on Sofia (appointment or civil war). **Trunk**: the movement (purge the Palace, militia, Brannik, Legionary courts, arms drive, shock divisions, war economy, total mobilisation); **the Revolution Must March** (starts Revolutionary Momentum; Plan Struma, border incidents, the wars for Skopje and the Struma valley, Legionary Macedonia and Thrace, victory parades); the new provinces (Dobruja ultimatum, prefects, soldier-settlers, requisitions, Bulgarisation). **Split at the Legion's Destiny**: (B1) *Lukov's Axis Crusade*: into the Axis, German instructors, Panzers for Sofia, the New Order, Crusade in the East, Budjak, Odessa corridor, Black Sea and Aegean fleets, the Legionary Empire, Thrace to the Bosporus. (B2) *Tsankov's Imperium*: no orders from Berlin, the Pact of Iron with Hungary, rival to Rome, wars for the Straits, the Danube and **Albania (against Italy if it holds it)**, the Imperial navy, a window on the Mediterranean, the Imperium on Three Seas |
| Secret: the Coburg Restoration | {blocks['secret']} | Hidden (`allow_branch`) until Boris dies (Aug 1943+, random) or three letters from Coburg arrive. Ferdinand returns. (a) Third Bulgarian Empire: Simeon's borders, Tsar of the Vlachs, Tarnovo coronation, Kaloyan's revenge. (b) Tsargrad: Basileus, Hagia Sophia, the Themes, the Varangian Guard, Orthodox crusade, capital moved to Constantinople |
| Industry | {blocks['eco']} | Tobacco and rose exports (3 stages), German clearing vs. diversification with a follow-up event, Pernik coal and Balkan iron, Kremikovtsi, Kazanlak and Sopot arsenals, electrification and the Iskar dams, railways, ports, roads, chemicals, Tyulenovo oil, synthetic fuel, fuel reserves, war economy. **Nuclear line**: Nadjakov's laboratory, Bukhovo uranium, Atomic Commission, reactor, the Kozloduy pile, the Rila device (date-gated 1938–1944) |
| Military | {blocks['mil']} | Army doctrine 12 (mountain warfare, Chataldzha lessons, staff academy, bayonet tradition, armoured brigade), equipment 8, **manpower 9** (reservists, emigration volunteers, Rhodope battalions, veterans, women's auxiliary, universal service, mobilisation law, national army), navy 10, air 11 (PZL and Avia purchases, Dornier bombers, paratroopers) |

Total **{len(F)} focuses**; plain stat bumps {stat} ({100 * stat // len(F)}%). Every exclusive choice says what it rules out.
Every focus has `search_filters` and `ai_will_do`.

**Durations** (v3.1): 35 days for plain stat bumps, 49 days by default, 56 days for war goals, land transfers and two or more buildings, 70 days for path choices, formables and finales; the opening keeps its short 35/49-day focuses. Average {round(sum(f['cost'] for f in F) * 7 / len(F))} days per focus (v3.0: almost all 70).

## How to reach each path
* **Tsar's Way**: *The Hour of Decision* → *The Tsar Steps Forward*. Always available.
* **Legionary Revolution**: *The Hour of Decision* → *The Legions March*, which needs **Legion influence 40+** (start: 20). Raise it with
  *Patronise the Legions* (+10, every 60 days), the *Shadow Parties* opening focus (option "Let the Legions march", +15), the opening event option "Let the young nationalists organise" (+10),
  war support above 50% and fascist popularity above 15% (+1 a month each).
* **Secret (Coburg Restoration)**: appears on the left of the tree when `bfx_secret_unlocked` is set: either Tsar Boris dies (from August 1943,
  25% a month while he rules, i.e. on the Tsar's Way) or the third *Letter from Coburg* arrives (random event, about 7% a month from 1937 while
  not on the Legion path; after the first letter the decision *Answer the Letter from Coburg* adds one every 120 days). It is not available after
  *The Legions March*.

## Realism and balance rules
* **Cores only on historically Bulgarian lands**: Southern Dobrudja (77), Vardar Macedonia (106), Western Thrace (184), Edirne (341),
  and Central Macedonia (731) once compliance passes 40%. Everything else is **claims and war goals**, which is where the aggression comes from.
* **Integration decisions** core other held land only once its *compliance* is high enough: Bulgarian lands 35%, Greece and Albania 60%,
  Serbia and Romania 65%, Anatolia 70%, the Pontic coast 75%. They cost political power and a little stability, and can be repeated as compliance rises.
* **Diplomacy works**: *Open the Chancelleries* (and the Legionary State) lift the non-aligned limits with `set_rule`. The *Sofia Chancellery*
  decisions propose non-aggression pacts (Turkey, Romania, Greece, Yugoslavia, USSR, Hungary, Italy), ask for guarantees (Germany, Italy, Britain, France),
  invite countries to your faction, give guarantees and demand Southern Dobruja. Several focuses do the same by event (Turkish pact 1941,
  Craiova 1940, the Albanian protectorate, joining the patron's alliance or the Axis, the Pact of Iron).
* **Land by diplomacy**: Craiova returns Dobruja peacefully (much likelier with German backing). The Hegemon's ultimatums can win Macedonia,
  Thrace and Edirne without a shot when the target is weak or already at war; a refusal gives a war goal instead. *The Partition Dividend* and
  *The New Order* hand over Bulgarian lands that allies hold (as in April 1941). Skopje asks to join after a successful uprising.
* Industry gives about one building per focus, two research slots at most in a playthrough, and the nuclear line is date-gated.

## Mechanic 1: Shackles of Neuilly (reworked)
* `bfx_rearm` (0–100) cancels the Neuilly penalties through the *Covert Rearmament* dynamic modifier. It **rusts by 1 a month**
  (0 after *Hidden Arsenals*).
* `bfx_suspicion` (0–100, starts at 15) **grows every month by 1 + rearmament/25**, so heavy rearmament is noticed fast.
* Thresholds 25 (protests), 50 (the Entente guarantees each other), 75 (embargo), 100 (the Petrich crisis) **re-arm** once suspicion
  falls 15 points below them, so penalties recur.
* Ends via the **Salonika Agreement** (from June 1938, only with suspicion below 50; XP and good relations) or **Tear Up Neuilly**
  (needs rearmament 50; embargo and crisis), or Ferdinand burning the treaty on the secret path.

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
rifles, mountain guns and *Officers on Leave*, recognise and guarantee the state, or intervene openly. **Intervening openly** brings in every country that guarantees Yugoslavia (its faction allies may join on their own). Every week the rising is checked: once it has
survived 8 months, or Yugoslavia's surrender progress passes 15%, Vardar Macedonia becomes a **real independent state** (tag MAC): the rebels
hand it their army, the civil-war country is folded back into Yugoslavia (which closes the civil war with Yugoslavia intact), and Skopje gets a
one-year truce with Belgrade (and Bulgaria's guarantee, if it recognised the rising). Up to v3.3 the rising ended with a white peace that named the
rebels as winner; in a civil war the winner annexes the loser, so Yugoslavia was annexed. That white peace is gone. If Bulgaria is still at war with Yugoslavia then, it chooses:
**white peace** with Yugoslavia and everyone fighting for it as ally or guarantor, or **keep marching** (claims on every Yugoslav state bordering
Bulgaria or free Macedonia). Six months later Skopje asks to join: annex it (cores) or keep it as a client.
If it is crushed, Bulgaria pays in stability and IMRO influence. Mihaylov leaves the Bulgarian cabinet to lead the new state.

## Mechanic 4: The Bulgarian Auction (Tsar's Way)
* Berlin, London and Moscow each have a **bid** for Bulgaria (`bfx_bid_ger/eng/sov`, 0–100; start 15/10/5). *Receive the Envoys* opens the auction.
* Focuses raise bids (each power's offer +25, *Play Them Off* +10 to all, Craiova, the Turkish pact, breaking the Entente).
* Decisions: *Flirt with Berlin/London/Moscow* (+12 to one, −4 to the other two), *Leak the Rival Offers* (+5 to all),
  and **cash an instalment** now at the cost of the bid (Berlin: rifles and guns; London: a civilian factory; Moscow: army XP and guns).
* While open, every bid falls by 1 a month. *The Auction Closes* makes the highest bidder our **patron** and pays its first instalment.
* Kingmaker: *Sign with the Highest Bidder* joins the patron's faction (or gets its guarantee). *The Contingency Plan* unlocks **Change Sides**:
  when our faction leader's surrender progress passes 25%, white-peace its enemies, leave, ask the strongest enemy faction leader to admit us
  and declare war on the old patron (Bulgaria, September 1944).
* Hegemon: *Take Everyone's Money* pays out every bid of 40 or more.

## Mechanic 5: Revolutionary Momentum (Legionary Revolution)
* Starts at 30 with *The Revolution Must March*. **+3 a month at war** (+4 on the crusade against the USSR), **−3 a month at peace**.
* Drives the *Revolutionary Momentum* dynamic modifier: attack 0..+10%, war support −6..+14%, conscription 0..+8%, political power −9..+21%.
* **Below 15**: *The Movement Fractures* (stability loss; find an enemy, buy peace, or let the Palace regain ground).
  **Above 90**: *The Revolution Devours Its Children* (purge generals, unleash a storm offensive, or pay to rein it in). Both re-arm after recovery.
* Spend it: *Storm Offensive* (−25: +15% attack, +10% breakthrough for 60 days), *Mass Levy* (−20: 25k manpower),
  *Revolutionary Tribunals* (−15: 75 PP), *Legionary Requisitions* (−15: equipment). Gain it in peace: *Torchlight Rallies* (+8),
  *Manufacture an Incident* (+15, world tension). Many Legion focuses also add momentum.
* The point: the Legion cannot sit still. It needs a war roughly every year or it starts to come apart.

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
the Coburg letters, Ferdinand's return, Hagia Sophia and Tarnovo, the three ultimatums (Athens, Belgrade, Ankara), the two momentum crises, and five random flavour events.
Decision categories: Shackles of Neuilly, The Tsar's Balance, The Bulgarian Auction, Revolutionary Momentum, The Sofia Chancellery, The Macedonian Uprising, Integration, Tsargrad Propaganda.

## AI
On startup an AI Bulgaria rolls Tsar 72% (Kingmaker 70% / Hegemon 30%) or Legions 28% (Axis Crusade 60% / Imperium 40%), and a 30% chance
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
