# Master prompt for the event pictures

How to use it: start a new chat with your image generator. Paste **Part 1** once, upload your reference images and
label each one (see **Part 2**), then for every picture paste one line from **Part 3**. Save each result as the
file name given, in `evil-sofia/tools/event_pictures/`; the next build uses it.

---------------------------------------------------------------------------------------------------------------

## Part 1: the master prompt (paste once, at the start)

```
You are making event pictures for a Hearts of Iron IV mod set in Sofia, Bulgaria, in an alternate 1936 where the
city has split into 24 warring districts. Every picture must look exactly like a vanilla Hearts of Iron IV event
picture. I will upload reference images: use them as described below, then I will ask for pictures one by one.

STYLE (apply to every picture, no exceptions):
- A real-looking archival photograph from the 1930s-1940s, BLACK AND WHITE only: no colour, no sepia tint, no
  colour accents. Neutral grey tones, deep blacks, soft highlights.
- Old press-photo look: visible film grain, slightly soft focus, mild vignetting at the corners, gentle contrast,
  occasional faint dust or scratches. It must look like it was taken with a 1930s press camera, not like a modern
  photo with a filter.
- Documentary composition: people caught in the moment, not posing for a portrait (unless the scene says so),
  natural light, eye-level or slightly elevated viewpoint, a clear main subject in the CENTRE of the frame.
- Period-correct details: 1930s clothing (wool coats, flat caps, hats, uniforms with belts and boots), old cars,
  trams, horse carts, rifles and equipment of the 1930s. Nothing modern in focus: no phones, no modern cars, no
  neon, no plastic.
- No text, no captions, no borders, no frames, no watermarks, no logos, no signatures.
- No gore. War scenes are shown the way 1930s newspapers showed them: smoke, rubble, soldiers, crowds.

FORMAT:
- "COUNTRY" pictures: nearly square, about 6:5 (for example 1200x1000). The game shows them at 210x176.
- "NEWS" pictures: very wide, about 2.6:1 (for example 2080x800). The game shows them at 397x153.
- Keep everything important in the middle 80% of the picture: the edges may be cropped.

REFERENCES (how to use the images I upload):
- STYLE references (existing Hearts of Iron IV event pictures): copy their look exactly: grain, tones, softness,
  composition, the feeling of an old newspaper photograph. Never copy their content.
- PLACE references (photos of Sofia): keep the architecture recognisable (shapes of buildings, domes, squares,
  bridges, boulevards), but show it as it would have looked in a 1930s photograph.
- FLAG references: flags appear on poles, buildings or banners. Keep the design and the pattern exactly (shapes,
  stripes, emblems, how light and dark parts are arranged) so the flag is recognisable in black and white; convert
  the colours to the matching shades of grey. Flags hang and wave like real cloth.
- PEOPLE references (portraits of the characters): when a scene names a character, that person must be
  recognisable (face, hair, build), as a man of the 1930s in period clothing; keep his likeness, change only the
  clothes and the age of the photograph. Never put a character in a scene unless I name him.

When I ask for a picture I will give: the file name, COUNTRY or NEWS, the scene, and which references to use.
Make one picture per request. If a scene is unclear, choose the most dramatic, vanilla-Hearts-of-Iron-looking
version of it.
```

---------------------------------------------------------------------------------------------------------------

## Part 2: uploading the references

Upload them in the same chat, after Part 1, with a short label each, for example:

```
STYLE reference 1: a vanilla Hearts of Iron IV event picture.
PLACE reference "Largo": the Largo and the Party House in central Sofia.
FLAG reference "Sredets red": the communist flag of Sredets.
PERSON reference "Victor": Victor Kolev.
```

Suggested references (the names are used in Part 3):

| Kind | Name to use | What to upload |
|---|---|---|
| STYLE | style 1, 2, 3 | 2–3 vanilla HOI4 event pictures (screenshots from the game) |
| PLACE | Largo | the Largo / Party House |
| PLACE | Nevsky | Alexander Nevsky Cathedral (Oborishte) |
| PLACE | Boyana | Boyana / villas on the slopes of Vitosha, Boyana Church |
| PLACE | Vitosha Boulevard | Vitosha Boulevard with NDK at the end |
| PLACE | Eagles' Bridge | Eagles' Bridge (bronze eagles) |
| PLACE | stadium | Vasil Levski National Stadium |
| PLACE | panel blocks | Sofia housing estates (Mladost / Lyulin) |
| PLACE | Women's Market | Zhenski Pazar / Vazrazhdane market streets |
| PLACE | theatre steps | the steps from the Evil Gang photo (or any theatre steps) |
| FLAG | Sredets / Sredets red | `tools/flags/SRD.png` and the communist flag (from the game) |
| FLAG | Oborishte / Oborishte red | `tools/flags/OBR.png` and its communist flag |
| FLAG | Lozenets, Vitosha | `tools/flags/LOZ.png`, `tools/flags/VIT.png` |
| FLAG | Sofia, South Sofia, North Sofia | `tools/flags/SOFIA.png` and the red Sofia flags (from the game) |
| PERSON | Victor, Anton, Henry, Georgi Y | the leaders' portraits |
| PERSON | Henry's mom | (optional) a picture of an older woman to use |
| PERSON | Ilchev | Konstantin Ilchev's portrait |
| PERSON | the gang / the C Class | the two group photos |

Image generators often refuse to copy real people's faces. If that happens, leave the PERSON reference out
and describe the person instead ("a young man with short dark curly hair"), or show him from behind or far away.

---------------------------------------------------------------------------------------------------------------

## Part 3: one line per picture

Paste one line at a time.

### Sredets events (COUNTRY, 6:5)

```
evil_sofia_srd_1.png, COUNTRY: dusk, a huge crowd with flags fills the Largo, Victor speaks from the steps of the Party House. Refs: Largo, Sredets red flag, Victor, style.
evil_sofia_srd_2.png, COUNTRY: a man in a long coat waits alone in the hallway of an old apartment building, staircase behind him. Refs: Victor, style.
evil_sofia_srd_3.png, COUNTRY: two young men shake hands in front of the cathedral, a small crowd watching, red flags. Refs: Nevsky, Victor, Anton, Oborishte red flag, style.
evil_sofia_srd_4.png, COUNTRY: night, a man walks away alone down an empty street, the cathedral dome behind him. Refs: Nevsky, Victor, style.
evil_sofia_srd_5.png, COUNTRY: a young man tears up letters at a desk in a villa, an older woman stands behind him, arms crossed. Refs: Boyana, Henry, Henry's mom, style.
evil_sofia_srd_6.png, COUNTRY: trucks and armed militiamen moving down a forest road from the mountain. Refs: Boyana, Vitosha flag, style.
evil_sofia_srd_7.png, COUNTRY: night, a man on an old telephone at a desk, a lamp, a city map on the table. Refs: Victor, style.
evil_sofia_srd_8.png, COUNTRY: before dawn, soldiers open the gate of a barracks, a new flag on the district hall behind. Refs: Oborishte red flag, style.
evil_sofia_srd_9.png, COUNTRY: two friends embrace in a street, militiamen march past behind them. Refs: Victor, Georgi Y, Lozenets flag, style.
evil_sofia_srd_10.png, COUNTRY: a man hangs up a telephone, looking out of a rainy window. Refs: Victor, style.
evil_sofia_srd_11.png, COUNTRY: a young man reads a letter, a group photograph pinned to the wall behind him. Refs: the gang, style.
evil_sofia_srd_12.png, COUNTRY: a group of young men in coats laughing together on the steps of a theatre. Refs: theatre steps, the gang, style.
evil_sofia_srd_13.png, COUNTRY: an empty chair at a long table, a single glass left on it, dim light. Refs: style.
evil_sofia_srd_14.png, COUNTRY: a dozen young men in scarves outside a district hall, one holding a burning flare. Refs: the C Class, style.
evil_sofia_srd_15.png, COUNTRY: football fans with raised scarves marching together down a street. Refs: the C Class, style.
evil_sofia_srd_16.png, COUNTRY: night, a street brawl between two groups of young men, smoke from flares. Refs: the C Class, style.
```

### News (NEWS, 2.6:1)

```
evil_sofia_news_1.png, NEWS: red banners over the Largo, a vast crowd below the Party House. Refs: Largo, Sredets red flag, style.
evil_sofia_news_2.png, NEWS: armed police at a checkpoint on a bridge, a tram waiting behind them. Refs: Sredets flag, style.
evil_sofia_news_3.png, NEWS: two men signing a document over a large city map on a table, officials around them. Refs: Victor, Anton, style.
evil_sofia_news_4.png, NEWS: smoke over the domes of the cathedral, soldiers in the square in front of it. Refs: Nevsky, Sredets red flag, style.
evil_sofia_news_5.png, NEWS: soldiers in the garden of a hillside villa, pine forest and the mountain behind. Refs: Boyana, Sredets red flag, style.
evil_sofia_news_6.png, NEWS: a huge rally, a man speaking from a balcony hung with the flag of Sofia. Refs: Largo, Sofia flag, Victor, style.
evil_sofia_news_7.png, NEWS: two leaders shaking hands on a bridge with bronze eagles, photographers around them. Refs: Eagles' Bridge, Victor, Anton, South Sofia flag, North Sofia flag, style.
evil_sofia_news_8.png, NEWS: soldiers laying down rifles in a pile in a city street, civilians watching. Refs: style.
evil_sofia_news_9.png, NEWS: workers pouring concrete and stacking sandbags across a city bridge. Refs: Sredets flag, style.
evil_sofia_news_10.png, NEWS: a group of young men posing on the steps of a theatre, a newspaper photograph. Refs: theatre steps, the gang, style.
evil_sofia_news_11.png, NEWS: night march of young men with scarves and burning flares through the city centre. Refs: Vitosha Boulevard, the C Class, style.
evil_sofia_news_12.png, NEWS: a middle-aged teacher with a stack of papers walks past saluting guards into a government building. Refs: Largo, Ilchev, style.
```

### Random events (COUNTRY, 6:5)

```
evil_sofia_flavour_1.png, COUNTRY: trams standing still in a rainy street, the drivers gathered beside them. Refs: style.
evil_sofia_flavour_2.png, COUNTRY: a packed football stadium at night, two sets of fans with scarves. Refs: stadium, style.
evil_sofia_flavour_3.png, COUNTRY: people shovelling deep snow in a city street, a truck stuck in the drifts. Refs: style.
evil_sofia_flavour_4.png, COUNTRY: angry residents holding photographs at the door of a town hall, a broken road in front. Refs: style.
evil_sofia_flavour_5.png, COUNTRY: night, a queue outside a small street-food shop, soldiers in the queue. Refs: style.
evil_sofia_flavour_6.png, COUNTRY: a pack of stray dogs in a park, a soldier crouching to feed one. Refs: style.
evil_sofia_flavour_7.png, COUNTRY: a wedding with a brass band in the courtyard of an apartment block. Refs: panel blocks, style.
evil_sofia_flavour_8.png, COUNTRY: a crowded street market at night, crates handed over in the shadows. Refs: Women's Market, style.
evil_sofia_flavour_9.png, COUNTRY: hikers planting a flag on a snowy mountain summit. Refs: style.
```

---------------------------------------------------------------------------------------------------------------

## Checking a result

- Is it fully black and white (no colour or sepia tint)?
- Does it look like a 1930s newspaper photo next to the vanilla references (grain, softness, tones)?
- Is the subject in the middle, with nothing important at the edges?
- No text, frame, watermark or modern object?
- Are the flags recognisable from their pattern alone?

If one fails, answer with: "Again, but [the fix]", for example "Again, but fully black and white, more grain".
