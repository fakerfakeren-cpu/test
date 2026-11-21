import re, textwrap
from PIL import Image, ImageDraw, ImageFont
import sys
S = (sys.argv[1] if len(sys.argv) > 1 else "tree_preview.png")
TAG = sys.argv[2] if len(sys.argv) > 2 else "SRD"   # python3 tools/dev/render_tree.py out.png VIT
tree = open(f"common/national_focus/evil_sofia_{TAG}.txt").read()
loc = dict(re.findall(r'^ (\S+):0 "(.*)"', open("localisation/english/replace/evil_sofia_focus_l_english.yml", encoding="utf-8-sig").read(), re.M))
spr = dict(re.findall(r'name = "(GFX_\w+)"\s+texturefile = "([^"]+)"', open("interface/evil_sofia_goals.gfx" if TAG == "SRD" else f"interface/evil_sofia_goals_{TAG}.gfx").read()))
foc = []
for blk in re.split(r"\n\tfocus = \{", tree)[1:]:
    fid = re.search(r"id = (\S+)", blk).group(1)
    x, y = int(re.search(r"x = (\d+)", blk).group(1)), int(re.search(r"y = (\d+)", blk).group(1))
    pre = [re.findall(r"focus = (\S+)", m) for m in re.findall(r"prerequisite = \{([^}]*)\}", blk)]
    mx = re.findall(r"focus = (\S+)", " ".join(re.findall(r"mutually_exclusive = \{([^}]*)\}", blk)))
    foc.append((fid, x, y, pre, mx, re.search(r"icon = (\S+)", blk).group(1)))
CW, RH, TOP, L = 112, 160, 20, 20
W = L * 2 + (max(f[1] for f in foc) + 1) * CW; H = TOP + (max(f[2] for f in foc) + 1) * RH + 30
img = Image.new("RGBA", (W, H), (34, 36, 40, 255)); d = ImageDraw.Draw(img)
font = ImageFont.truetype("DejaVuSans.ttf", 11)
pos = {f[0]: (L + f[1] * CW + CW // 2, TOP + f[2] * RH) for f in foc}
for fid, x, y, pre, mx, icon in foc:
    cx, cy = pos[fid]
    for g in pre:
        for p in g:
            px, py = pos[p]; mid = (py + 118 + cy) / 2
            pts = [(px, py + 118), (px, mid), (cx, mid), (cx, cy + 4)]
            for a, b in zip(pts, pts[1:]):
                n = 12 if len(g) > 1 else 1
                for i in range(0, n, 2 if n > 1 else 1):
                    d.line([(a[0] + (b[0]-a[0]) * i / n, a[1] + (b[1]-a[1]) * i / n), (a[0] + (b[0]-a[0]) * (i+1) / n, a[1] + (b[1]-a[1]) * (i+1) / n)], fill=(190, 170, 120), width=3)
for fid, x, y, pre, mx, icon in foc:
    for o in mx:
        if fid < o:
            (ax, ay), (bx, by) = pos[fid], pos[o]
            d.line([(ax + 45, ay + 46), (bx - 45, by + 46)], fill=(200, 50, 40), width=4)
            m = ((ax + bx) / 2, ay + 46); d.ellipse([m[0]-10, m[1]-10, m[0]+10, m[1]+10], fill=(200, 50, 40)); d.text(m, "X", font=font, fill="white", anchor="mm")
for fid, x, y, pre, mx, icon in foc:
    cx, cy = pos[fid]
    ic = Image.open(spr[icon]).convert("RGBA"); ic.thumbnail((96, 88))
    img.alpha_composite(ic, (int(cx - ic.width / 2), int(cy + 4 + (88 - ic.height) / 2)))
    lines = textwrap.wrap(loc[fid], 17)[:3]; bh = 14 * len(lines) + 6
    d.rounded_rectangle([cx - 53, cy + 94, cx + 53, cy + 94 + bh], 4, fill=(20, 22, 26), outline=(120, 100, 60))
    for i, ln in enumerate(lines):
        d.text((cx, cy + 101 + 14 * i), ln, font=font, fill=(240, 232, 210), anchor="mt")
img.convert("RGB").save(S)
