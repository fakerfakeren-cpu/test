# Oathbound: The Hollow Crown — design notes

Internal design reference. Player-facing docs live in the README and in-game in the Lantern Chronicle.

## Premise

The **Order of the Ember Lantern** (the Lanternguard) were knight-wizards who carried the **Everflame**, a fire
kindled at the first dawn. Their Lord-Commander **Morvane** feared death. In the Gloaming (the grey country
between dusk and night) he found the **Hollow Crown**, which promised a reign without end if he swore upon it.
He swore, and lied, and the Gloam poured through him. The Order fell in a single night.

Three of the Order's greatest sealed him beyond the **Sundered Gate**, each binding one of its three **Oath
Seals** with their own life: **Valor** (Sir Caldris, the Tide-Knight), **Wisdom** (Archmage Veyl) and
**Sacrifice** (Hrodgar, the first Barrow-King, who returned from his tomb to give his oath). The seals held
for four hundred years, but they hollowed their keepers. Now the Gloam leaks back into the world at night.

The player is the last squire. The Order's living book, the **Lantern Chronicle**, chooses them.

## Stages (progression gates)

| # | Chapter | Where | Gate | Unlocks |
|---|---|---|---|---|
| I | The Last Squire | Anywhere; **Wayshrine** | Mine Lumenite, forge Oathsteel, craft the **Warden's Lantern**, kindle a Wayshrine brazier | The Lantern's *Seek* guidance; Hymn Stones answer you |
| II | Where the Bells Drown | **Drowned Chapel** (swamp/river/beach) | Bell puzzle (**Hymn of the Tide**) needs a Warden's Lantern; miniboss **Sir Caldris** | **Seal of Valor**, Drowned Anchor |
| III | The Hollow Spire | **Arcanist's Spire** (forest/taiga/meadow) | Rune-dial cipher (riddles) needs the Seal of Valor; miniboss **Archmage Veyl** | **Seal of Wisdom**, Staff of Veyl, Spellsilk → Arcanist robes, Dawnstring Longbow |
| IV | The Barrow of Kings | **Barrow** (plains/taiga/hills, underground) | Epitaph logic puzzle (only one king told the truth) needs the Seal of Wisdom; miniboss **Hrodgar** | **Seal of Sacrifice**, Housecarl's Warhorn |
| V | The Sundered Gate | **Sundered Citadel** (rare) | Craft the **Oathkey** (three seals); open the Gate | The **Gloaming** dimension |
| VI | The Hollow Crown | **Gloaming** → Hollow Throne | Survive Gloamrot (lit lantern), reach the throne, defeat **Morvane** | Dawnbreaker, Hollow Crown, Everflame Embers |

Secrets: every structure hides a **Lanternguard Insignia** in a concealed cache (cracked brickwork). Four insignia
plus an Everflame Ember make the post-game **Everflame Lantern**.

## Materials and tiers
- Lumenite Ore / Deepslate Lumenite Ore (y -48..56) → Lumenite Shard. Lumenite Dust (craft).
- Oathsteel Blend (iron + 2 shards, shapeless) → smelt → **Oathsteel Ingot** (between iron and diamond).
- Spellsilk (Spire loot, Animated Tome drop) → Arcanist robes.
- Gloam Essence (Gloamlings, Veilhounds, Gloaming) → Shadowreap Sickle, Elixir of Dawn.
- Luminous Dust (Lanternmoth) → Elixir of Dawn, Lumen Flask.
- Seals (minibosses) → Oathkey. Everflame Ember (Morvane).

## Weapons (each a different idea)
1. **Oathsteel Longsword** — *Riposte*: damage you take in the last 3 s is stored (max 8) and added to your next hit.
2. **Warden's Halberd** — +1.5 reach; sprint-attack is a *Charge Thrust* that hits everything in a 4-block line.
3. **Drowned Anchor** (Caldris) — throw the anchor on a chain: yanks a creature to you, or grapples you to terrain.
4. **Staff of Veyl** (Veyl) — *Arcane Chain*: a bolt that leaps between up to 5 enemies.
5. **Dawnstring Longbow** — fully drawn shots apply *Sunmark* (glowing, +30% damage taken) and pierce.
6. **Housecarl's Warhorn** (Hrodgar) — summon two spectral housecarls that fight for you for 40 s.
7. **Shadowreap Sickle** — damage and life-steal grow with the darkness around the target.
8. **Dawnbreaker** (Morvane) — hold to raise it; release for a *Dawn Rite* sunburst (radius 7, triple vs Gloam/undead).
9. **Lumen Flask** — thrown: a burst of light that blinds, burns Gloam creatures and leaves glowing wisps.
Tools: Oathsteel pickaxe/axe/shovel — *Sunmended*: slowly repair in daylight.

## Armour
- **Oathsteel** (knight) — full set: *Steadfast* (knockback immunity; below 30% HP gain Resistance II for 6 s, 60 s cooldown).
- **Arcanist Robes** (wizard) — full set: magic/ability cooldowns halved, feather-fall while sneaking in the air.
- **Hollow Crown** (Morvane) — night vision, Gloam creatures ignore you unless attacked, +4 max health.

## Effects
- **Radiance** (Elixir of Dawn / Everflame Lantern): immune to Gloamrot, burns nearby Gloam creatures.
- **Gloamrot**: no natural regeneration and slow withering. Applied in the Gloaming without a lit lantern.
- **Sunmark**: glowing, +30% damage taken.

## Creatures
| Mob | Where | Idea |
|---|---|---|
| Lanternmoth | forests at night | passive glowing moth, drawn to lantern-bearers; Luminous Dust |
| Gloamling | overworld night, Gloaming | nearly invisible in darkness unless you carry a lit lantern; hit-and-run; burns in sunlight |
| Forsworn Knight | Citadel, Gloaming | falls into a heap of armour and rises again unless slain with Oathsteel/lumen/fire |
| Barrow Wight | Barrow | phasing ghost, *Grave Chill* (mining fatigue + slowness) |
| Animated Tome | Spire | erratic flying spellbook that fires glyph bolts |
| Veilhound | Gloaming | pack hunter that circles then lunges from several sides |
| Spectral Housecarl | summoned | axe warrior; Hrodgar's guard or your Warhorn allies |

## Minibosses
- **Sir Caldris, the Drowned Knight** — tower shield blocks every frontal blow (flank him or break the guard with an axe);
  Shield Charge; *Undertow* drags you in then slams; calls drowned squires at half health.
- **Archmage Veyl, the Hollow Magus** — hovers and blinks; *Arcane Orbs* can be struck back at him;
  *Mirror Images* (illusions pop in one hit; the real one's staff burns gold); *Gravity Glyph* lifts and drops you.
- **Hrodgar, the Barrow-King** — giant; flail sweeps send shockwave rings you jump over; raises Spectral Housecarls
  that are tethered to him and make him nearly invulnerable until they fall; at 30% devours them to heal.

## Final boss: Morvane, the Hollow King
Arena: the Hollow Throne on the Gloaming's central island, ringed by four **Ward Lanterns**.
Entrance: stepping into the ring seals it with a wall of veil; the lanterns gutter one by one; Morvane rises from the throne.
1. **Oathbreaker** (100–60%): three-hit sword combo, *Gloam Lunge* dash, *Oath of Ruin* stance (melee during it is countered; arrows break it).
2. **Hollow Sorcerer** (60–25%): levitates; *Crown of Blades* (six blades orbit then fire); *Eclipse Pillars* (marked ground erupts);
   *Call the Forsworn* (two knights).
3. **The Hollow** (25–0%): all Ward Lanterns snuff and the arena goes dark. Morvane is untouchable shadow.
   Relight the lanterns (use a lit Warden's Lantern or a lumenite shard on them). All four lit = he is *Unveiled*:
   stunned, and takes 50% more damage for 10 s. Then two lanterns go out again.
Death: the crown cracks, light pours out, the Gloaming brightens; a return veil opens.
