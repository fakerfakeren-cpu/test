# Tidecaller pistol (Roblox, box-style)

`python3 build_pistol.py && python3 render_previews.py` (needs numpy + pillow) regenerates everything in `out/`.

| File | What |
|---|---|
| `out/pistol.glb` | 4 objects (Body, Slide, Magazine, Trigger), studs, 1024 texture embedded |
| `out/pistol.obj` + `pistol.mtl` | same 4 objects, studs, uses `pistol_1024.png` |
| `out/pistol_128.png` | painted texture (1 texel = 1 model px) |
| `out/pistol_1024.png` | nearest-neighbour 8x upscale - upload this one to Roblox |
| `out/pistol.bbmodel` | Blockbench free-format project, px units, outlines as inverted mesh shells |
| `out/build_info.json` | origin, muzzle, slide travel, part bounding boxes |
| `out/previews/` | renders made from the exported GLB |

Axes: Y up, barrel along -Z, +X is the gun's right side; origin = centre of the grip. 16 px = 1 stud.

Key numbers (studs, relative to the origin):
- Muzzle tip (centre of compensator face): (0, 0.5727, -1.7522)
- Slide recoil: 0.3125 (5 px) along +Z
- Magazine drop direction: (0, -0.9659, 0.2588)
- Trigger pull: 0.0625 (1 px) along +Z
