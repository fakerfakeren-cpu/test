# Tidecaller pistol (Roblox, box-style classic handgun)

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
- Muzzle tip (bore centre on the slide's front face): (0, 0.7168, -1.7738)
- Slide recoil: 0.375 (6 px) along +Z
- Magazine drop direction: (0, -0.9397, 0.3420)
- Tool.Grip position (Body is recentred on its bounding box by Roblox): (0, -0.2059, 0.6657)
- Trigger pull: 0.0625 (1 px) along +Z
