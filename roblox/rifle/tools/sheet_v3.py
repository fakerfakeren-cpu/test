import numpy as np, sys
sys.path.insert(0, '.')
from readglb import load
from raster import render
from PIL import Image, ImageDraw, ImageFont
PX = 0.0531125069; S = 10
def glb_tris(path, off=None):
    js, parts = load(path)
    off = off or {}
    T = np.concatenate([p[0] / PX + np.array(off.get(g, (0, 0, 0))) for g, p in parts.items()])
    C = np.concatenate([p[1] for p in parts.values()]).astype(np.uint8)
    return T, C
v1 = render(*glb_tris('Rifle.glb'), 125, 25, S, ss=2, margin=14)
a = render(*glb_tris('Rifle_v3.glb'), 125, 25, S, ss=2, margin=14)
b = render(*glb_tris('Rifle_v3_slim_muzzle.glb'), 125, 25, S, ss=2, margin=14)
sp = render(*glb_tris('Rifle_v3.glb', {'Magazine': (0, -9, 0), 'Slide': (-6, 13, 6)}), 125, 25, S, ss=2, margin=14)
la = render(*glb_tris('Rifle_v3.glb'), 90, 0, 7, ss=2, margin=14)
lb = render(*glb_tris('Rifle_v3_slim_muzzle.glb'), 90, 0, 7, ss=2, margin=14)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
pad = 20; cw = max(v1.width, a.width, b.width, sp.width, la.width)
rows = [(('v1 (what you imported)', v1), ('v3 option A: outlines everywhere, original muzzle', a)),
        (('v3 option B: same + thinner muzzle', b), ('v3 split: Magazine and Slide pulled off, each fully outlined', sp)),
        (('option A, left side', la), ('option B, left side', lb))]
Hh = 50 + sum(max(r[0][1].height, r[1][1].height) + 34 for r in rows) + pad
out = Image.new('RGB', (cw * 2 + pad * 3, Hh), (128, 128, 128)); d = ImageDraw.Draw(out)
d.text((pad, 12), 'Rifle v3: Trigger merged into Body, black outline on every part, seam, panel and slot (unlit, flat colours)', fill='black', font=fb)
y = 50
for (n1, i1), (n2, i2) in rows:
    d.text((pad, y), n1, fill='black', font=f); d.text((pad * 2 + cw, y), n2, fill='black', font=f)
    out.paste(i1, (pad, y + 26)); out.paste(i2, (pad * 2 + cw, y + 26))
    y += max(i1.height, i2.height) + 34
out.save('Rifle_v3_preview.png'); print(out.size)
