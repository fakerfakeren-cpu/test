# CREDITS

## Portrait photographs
The build sandbox could read Wikimedia Commons file pages but was blocked by Wikimedia's robot policy from downloading
images, so the user downloaded each photo from the Commons page listed below and supplied it. Licences were read from those
pages automatically (shown as found) and should be double-checked before any public upload. The derived portraits (background removed with rembg,
recoloured, composited on a generated backdrop) are modifications of these works.

| Person | Mod files | Source page | Licence |
|---|---|---|---|
| Boris III | `bfx_boris_iii.dds`, `bfx_boris_iii_small.dds` | https://commons.wikimedia.org/wiki/File:BASA-3K-7-342-28-Boris_III_of_Bulgaria.jpeg | Public domain (PD-1923) |
| Ferdinand I | `bfx_ferdinand_i.dds`, `bfx_ferdinand_i_small.dds` | https://commons.wikimedia.org/wiki/File:Zar_Ferdinand_Bulgarien.jpg | Public domain (PD-anon-70-EU) |
| Kimon Georgiev | `bfx_kimon_georgiev.dds`, `bfx_kimon_georgiev_small.dds` | https://commons.wikimedia.org/wiki/File:KG_001.tif | Commons page shows CC BY-SA 4.0 (attribution and share-alike apply to the derived portrait) |
| Georgi Dimitrov | `bfx_georgi_dimitrov.dds`, `bfx_georgi_dimitrov_small.dds` | https://commons.wikimedia.org/wiki/File:Georgiy_Mihaylovich_Dimitrov_TASS_Portrait_Trim_Edit.jpg | Public domain (PD-Russia / PD-1996) |
| Vasil Kolarov | `bfx_vasil_kolarov.dds`, `bfx_vasil_kolarov_small.dds` | https://commons.wikimedia.org/wiki/File:V.kolarov.jpg | CC BY 2.5 BG |
| Bogdan Filov | `bfx_bogdan_filov.dds`, `bfx_bogdan_filov_small.dds` | https://commons.wikimedia.org/wiki/File:Богдан_Филов.jpg | CC BY-SA 2.5 |
| Hristo Lukov | `bfx_hristo_lukov.dds`, `bfx_hristo_lukov_small.dds` | https://commons.wikimedia.org/wiki/File:Hristo-lukov.jpg | Public domain (PD-Russia) |
| Nikola Mushanov | `bfx_nikola_mushanov.dds`, `bfx_nikola_mushanov_small.dds` | https://commons.wikimedia.org/wiki/File:N.mushanov.jpg | Public domain (PD-anon-70-EU) |
| Nikola Petkov | `bfx_nikola_petkov.dds`, `bfx_nikola_petkov_small.dds` | https://commons.wikimedia.org/wiki/File:Nikola_Petkov.jpg | Public domain (PD-anon-70-EU) |
| Nikola Zhekov | `bfx_nikola_zhekov.dds`, `bfx_nikola_zhekov_small.dds` | https://commons.wikimedia.org/wiki/File:Nikola_Todorov_Zhekov.jpg | Public domain (PD-EU-no) |
| Georgi Kyoseivanov | `bfx_georgi_kyoseivanov.dds`, `bfx_georgi_kyoseivanov_small.dds` | https://commons.wikimedia.org/wiki/File:Georgi_Kyoseivanov1.png | Public domain (PD-Poland) |
| Anton Yugov | `bfx_anton_yugov.dds`, `bfx_anton_yugov_small.dds` | https://commons.wikimedia.org/wiki/File:Anton_Yugov_in_1947.jpg | Public domain (PD-anon-70-EU) |
| Konstantin Muraviev | `bfx_konstantin_muraviev.dds`, `bfx_konstantin_muraviev_small.dds` | https://commons.wikimedia.org/wiki/File:Konstantin_Muraviev.jpg | CC BY 2.5 |
| Ivan Mihaylov | `bfx_ivan_mihaylov.dds`, `bfx_ivan_mihaylov_small.dds` | https://commons.wikimedia.org/wiki/File:Ivan_Mihaylov_comitaji.jpg | Commons page shows CC BY-SA 4.0 (verify; the image is a 1930s book plate) |
| Vladimir Zaimov | `bfx_vladimir_zaimov.dds`, `bfx_vladimir_zaimov_small.dds` | supplied by the user: an existing Hearts of Iron IV portrait (Paradox Interactive art), used unaltered at 156×210 and cropped for the small version | © Paradox Interactive; included only for use with the game. Replace it before any public Workshop upload if in doubt. |

CC BY / CC BY-SA attribution: the authors are as credited on the linked Commons pages.

## Icons (focus icons, spirit icons, flags, thumbnail)
Emblems are built from glyphs of **game-icons.net**, licensed **CC BY 3.0** (https://creativecommons.org/licenses/by/3.0/),
source https://github.com/game-icons/icons, taken from the npm package `@iconify-json/game-icons` 1.2.4.
The glyphs were recoloured, embossed, outlined and composited; the Bulgarian tricolour is drawn by the build script.
Glyph SVGs used are kept in `tools/assets/game-icons/`. Authors:

- **Caro Asercion**: mountain-climbing, water-mill
- **Delapouite (https://delapouite.com)**: black-sea, byzantin-temple, cargo-ship, coal-wagon, flying-beetle, hammer-sickle, horse-head, imperial-crown, scroll-quill
- **Lorc (http://lorcblog.blogspot.com)**: anchor, burning-book, butterfly, crossed-chains, crossed-swords, curled-leaf, dove, eagle-emblem, fist, fox-head, gears, globe, hammer-nails, linked-rings, lion, mountains, rose, scales, scroll-unfurled, scythe, waves, wheat
- **Quoting**: biplane
- **Sbed (http://opengameart.org/content/95-game-icons)**: rifle
- **Skoll**: allied-star, breaking-chain

## Vanilla assets referenced (not copied)
Most focus icons, some spirit pictures, the decision icons and the event pictures are vanilla HOI4 sprites referenced by name.
They are not redistributed.

## Tools
rembg (MIT) with the u2net / u2net_human_seg models, OpenCV (Apache 2.0), Pillow (HPND), CairoSVG (LGPL).
