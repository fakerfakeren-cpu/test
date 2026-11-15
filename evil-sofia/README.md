# Evil Sofia (HOI4 total-conversion mod)

The map is Sofia, Bulgaria. Each of the 24 city districts is a country.
Every district is **one state** and one country, with a leader and a general. The districts are split
automatically into provinces of roughly equal size; each province has a city named after a real neighbourhood,
street or village. The splits are placeholders until they are redrawn along real neighbourhoods.

![terrain and cities](preview/terrain_preview.png)

## Install (for testing)

1. Copy this `evil-sofia` folder into `Documents/Paradox Interactive/Hearts of Iron IV/mod/`.
2. Copy `descriptor.mod` next to it, rename the copy to `evil_sofia.mod`, and add the line
   `path="mod/evil-sofia"` to it.
3. Turn the mod on in the launcher. While testing, add `-debug` to the game's launch options (Steam → Hearts of
   Iron IV → Properties → Launch options). **Without `-debug` the game never writes map errors to `error.log`**;
   it only shows "Failed to load the map". With it, the errors are logged and most of them stop being fatal.
4. Building positions in `map/buildings.txt` are rough placements; unit positions are left to the game.
   Fine-tune both in game with the `nudge` console command.

## Layout choices that keep the game happy

These follow a working 1.16 total-conversion map mod (MappaMundi) and engine rules measured in game on HOI4 1.19
by the Hoi4_world_map project (github.com/derprito64bit/Hoi4_world_map):
- The map is 2048x1024, so the whole city fits on screen when zoomed out. The vanilla ambient objects
  (map frame and decorations) are placed for the 5632x2048 world map, so `map/ambient_object.txt` is empty.
- Every province is at most 100 pixels across. The engine logs "TOO LARGE BOX" and misplaces unit models for
  provinces taller than about 174 px on the vanilla map (the limit may scale with the map size).
- `map/buildings.txt` uses the HOI4 1.19 building position types, in vanilla's numbers: per state 6 arms
  factories, 6 civilian factories, 3 anti-air, and one each of air base, refinery, radar, fuel silo,
  stronghold network, nuclear reactor and rocket site; per land province a bunker, a supply node and a
  special project facility. A state without an air base, rocket site or gun emplacement position is a fatal
  map error. `airports.txt` and `rocketsites.txt` no longer exist in 1.19 and are not generated.
- `map/unitstacks.txt` has a victory point (city) marker, type 38, in the middle of every land province.
- Every strategic region passes the engine's region-centre rule (a region whose averaged box centre falls
  outside all its provinces, exactly on the middle column, crashes the game with a divide-by-zero).
- Vanilla AI strategies point at real-world states, so `common/ai_strategy` is replaced with an empty folder.
- **Every file is written with Windows (CRLF) line endings.** With plain LF line endings, HOI4 drops the
  continent column of `map/definition.csv`, every land province fails the "must belong to a continent"
  map check, and starting a game stops with *"Failed to load the map"*. `.gitattributes` keeps git from
  converting them.
- Each district has several provinces with a named city (victory point) in each: neighbourhoods, streets
  and villages, with the biggest as the capital. The names and their rough coordinates are the `NAMES`
  table in `tools/build_map.py`; `preview/cities_preview.png` shows where they ended up.
- Terrain follows the real geography (tables `MOUNTAINS`, `PARKS`, `RIVERS` in `tools/build_map.py`):
  built-up areas are plains; parks (Borisova Gradina, South Park, West Park, ...) are forest; Vitosha, Lyulin,
  the Lozen mountain, Plana and the Balkan foothills in the north are mountains, forest and hills. A province's
  gameplay terrain is its roughest terrain covering at least 35 % of it. No city-building texture is used: it
  spawns thousands of house models and made the game lag.
- Rivers: the Iskar, Perlovska, Vladayska and Boyanska, 1 px wide and 4-connected, each with one source pixel;
  tributaries end in a flow-in pixel touching the river they join.
- Characters: `common/characters/<TAG>.txt` gives every country a leader (despotism) and a corps commander;
  `common/names/evil_sofia_names.txt` gives the game Bulgarian names for the characters it generates itself.

## How the map is made

`tools/districts_mask.png` is the source. It is grayscale, and each pixel's value is the district number (1–24); 0 means outside the city.
`tools/build_map.py` reads it and writes every map, state, country and localisation file:

```bash
pip install numpy pillow scipy
python3 tools/build_map.py
```

If a border is wrong, paint the mask with the correct value using any editor that keeps grayscale values exactly
(GIMP, Paint.NET; no anti-aliasing). Then run the script again.

| ID | Tag | District | ID | Tag | District |
|---|---|---|---|---|---|
| 1 | SRD | Sredets | 13 | NAD | Nadezhda |
| 2 | VAZ | Vazrazhdane | 14 | ISK | Iskar |
| 3 | OBR | Oborishte | 15 | MLA | Mladost |
| 4 | KRS | Krasno Selo | 16 | STU | Studentski |
| 5 | SRK | Serdika | 17 | LYU | Lyulin |
| 6 | POD | Poduyane | 18 | KRE | Kremikovtsi |
| 7 | SLA | Slatina | 19 | VIT | Vitosha |
| 8 | IZG | Izgrev | 20 | OVK | Ovcha Kupel |
| 9 | LOZ | Lozenets | 21 | VRB | Vrabnitsa |
| 10 | TRD | Triaditsa | 22 | NIS | Novi Iskar |
| 11 | KRP | Krasna Polyana | 23 | PNC | Pancharevo |
| 12 | ILN | Ilinden | 24 | BNK | Bankya |

State ID = district number. The provinces outside the city are impassable lakes ("The Void").
Sofia has no sea, so there are no navies.

## Known gaps

- No armies yet: countries have no divisions, technologies or equipment.
- `map/cities.bmp` is blank and there is no custom colour map, so the vanilla one is stretched over the city.
- Vanilla focus trees and events still refer to vanilla countries and states; they never fire for the districts.
- `supported_version` is `1.*`, so the launcher accepts any 1.x game version.
