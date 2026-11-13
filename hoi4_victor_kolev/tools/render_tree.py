"""Render a schematic PNG of the focus tree layout (for previewing outside the game)."""
import sys, textwrap
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build_mod as b
from PIL import Image, ImageDraw, ImageFont

b.validate()
CW, CH, BW, BH = 70, 120, 128, 62
fs = b.FOCUSES
W = (max(f["x"] for f in fs) + 2) * CW
H = (max(f["y"] for f in fs) + 1) * CH + 40
img = Image.new("RGB", (W, H), (34, 30, 26))
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except OSError:
    font = ImageFont.load_default()
pos = {f["id"]: (f["x"] * CW + CW, f["y"] * CH + 40) for f in fs}
for f in fs:
    x, y = pos[f["id"]]
    for grp in f["pre"]:
        for p in grp:
            px, py = pos[p]
            d.line([(px, py + BH // 2), (x, y - BH // 2)],
                   fill=(200, 170, 90) if len(grp) == 1 else (120, 160, 200), width=2)
for f in fs:
    x, y = pos[f["id"]]
    col = (120, 50, 50) if f["mx"] else (70, 64, 52)
    d.rectangle([x - BW // 2, y - BH // 2, x + BW // 2, y + BH // 2], fill=col, outline=(210, 190, 140))
    d.multiline_text((x, y), "\n".join(textwrap.wrap(f["name"], 20)), font=font, fill=(240, 235, 220),
                     anchor="mm", align="center")
d.text((10, 10), f"Victor Kolev - Bulgaria focus tree ({len(fs)} focuses). Red = mutually exclusive, blue lines = 'any of'",
       font=font, fill=(240, 235, 220))
img.save(sys.argv[1] if len(sys.argv) > 1 else "focus_tree_preview.png")
