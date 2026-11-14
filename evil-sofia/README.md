# Evil Sofia (HOI4 total-conversion mod)

The map is Sofia, Bulgaria. Each of the 24 city districts is a country.
Every district is **one state**. The bigger districts are split automatically into several provinces of
roughly equal size, because HOI4 has problems with very large provinces. These splits are placeholders; they will be replaced
with real neighbourhoods later.

![political preview](preview/political_preview.png)

## Install (for testing)

1. Copy this `evil-sofia` folder into `Documents/Paradox Interactive/Hearts of Iron IV/mod/`.
2. Copy `descriptor.mod` next to it, rename the copy to `evil_sofia.mod`, and add the line
   `path="mod/evil-sofia"` to it.
3. Turn the mod on in the launcher. The first time, start the game with `-debug` so errors show up.
4. In game, open the console and type `nudge`. Click **Generate** to create the
   building and unit positions (`map/buildings.txt` and `map/unitstacks.txt` only have rough placements), then save.

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

## Not tested in game yet

These files were generated without a copy of HOI4 to test against. The following parts are the most likely to need fixing:
- `map/terrain.bmp`, `map/trees.bmp` and `map/cities.bmp` are blank placeholders. Gameplay terrain is set in `definition.csv`; these files only change how the map looks.
- `map/world_normal.bmp` uses a guessed format. There is no custom colour map yet, so the vanilla one is stretched over the city.
- Vanilla focus trees, events and AI files still refer to vanilla countries and states. Expect a long `error.log`.
- `supported_version` is `1.*`, so the launcher accepts any 1.x game version.
