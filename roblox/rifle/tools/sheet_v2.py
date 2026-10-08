import importlib
from raster import render
from PIL import Image, ImageDraw, ImageFont
m1 = importlib.import_module('model3d'); m2 = importlib.import_module('model3d_v2')
T1, K1, _ = m1.assembled(); T2, K2, _ = m2.assembled()
S = 11
a = render(T1, K1, 125, 25, S, ss=2, margin=14); b = render(T2, K2, 125, 25, S, ss=2, margin=14)
c = render(T2, K2, -55, 25, S, ss=2, margin=14)
fr = render(T2, K2, 160, 12, S, ss=2, margin=14)
lv = render(T2, K2, 90, 0, 8, ss=2, margin=14)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
pad = 20
Wd = a.width + b.width + pad * 3
Hh = 50 + max(a.height, b.height) + 40 + max(c.height, fr.height) + 40 + lv.height + pad
out = Image.new('RGB', (Wd, Hh), (128, 128, 128)); d = ImageDraw.Draw(out)
d.text((pad, 12), 'Rifle v1 vs v2: same silhouette, v2 varies the thickness (unlit, flat colours)', fill='black', font=fb)
y = 50
d.text((pad, y - 4), 'v1: uniform 7-voxel slab', fill='black', font=f); d.text((pad * 2 + a.width, y - 4), 'v2: stepped thicknesses', fill='black', font=f)
out.paste(a, (pad, y + 20)); out.paste(b, (pad * 2 + a.width, y + 20))
y += 20 + max(a.height, b.height) + 16
d.text((pad, y), 'v2 from rear-right', fill='black', font=f); d.text((pad * 2 + a.width, y), 'v2 from the front (muzzle end)', fill='black', font=f)
out.paste(c, (pad, y + 24)); out.paste(fr, (pad * 2 + a.width, y + 24))
y += 24 + max(c.height, fr.height) + 12
d.text((pad, y), 'v2 left view (identical to v1 and the approved sprite from the side)', fill='black', font=f)
out.paste(lv, (pad, y + 24))
out.save('v2_sheet.png'); print(out.size)
