"""Communist flags, drawn by hand: only for the countries that can go red (Sredets, Oborishte and the Sofia
states they form). Everything is drawn at four times the flag size and scaled down, so edges stay smooth.

Each flag keeps something of its district: Sredets' four rhombuses, Oborishte's golden rings (now a cog), and
the coat of arms of Sofia.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

S = 4
W, H = 246 * S, 156 * S
GOLD = (250, 200, 45)
GOLD_DARK = (205, 150, 30)
RED = (200, 25, 30)
CRIMSON = (150, 20, 45)
WHITE = (246, 244, 238)


def _rot(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def _paint(im, mask, colour):
    im.paste(Image.new("RGBA", im.size, colour + (255,)), (0, 0), mask)


def star(d, cx, cy, r, fill, rot=0.0, inner=0.382):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + rot + i * math.pi / 5
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def hammer_sickle(im, cx, cy, size, colour):
    """Hammer and sickle, about size wide, centred on (cx, cy)."""
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    R = size * 0.40
    ox, oy = cx + size * 0.03, cy - size * 0.06
    # the blade: three quarters of a ring, open at the lower right, thinning towards its tip on the right
    d.pieslice((ox - R, oy - R, ox + R, oy + R), 125, 378, fill=255)
    ri, sx, sy = R * 0.76, R * 0.13, R * 0.05
    d.ellipse((ox + sx - ri, oy + sy - ri, ox + sx + ri, oy + sy + ri), fill=0)
    # its handle, down and to the left from the bottom of the blade
    a = math.radians(128)
    hx, hy = ox + R * 0.80 * math.cos(a), oy + R * 0.80 * math.sin(a)
    d.polygon(_rot([(0, -R * 0.12), (R * 0.55, -R * 0.10), (R * 0.55, R * 0.10), (0, R * 0.12)], hx, hy,
                   math.radians(128)), fill=255)
    # the hammer: handle from the lower right to the upper left, the head across its upper end
    a = math.radians(-135)
    bx, by = cx + R * 0.95, cy + R * 0.95
    d.polygon(_rot([(0, -R * 0.09), (R * 1.75, -R * 0.09), (R * 1.75, R * 0.09), (0, R * 0.09)], bx, by, a), fill=255)
    tx, ty = bx + R * 1.75 * math.cos(a), by + R * 1.75 * math.sin(a)
    d.polygon(_rot([(-R * 0.42, -R * 0.17), (R * 0.30, -R * 0.17), (R * 0.30, R * 0.17), (-R * 0.42, R * 0.17)],
                   tx, ty, a + math.pi / 2), fill=255)
    _paint(im, m, colour)


def wheat_wreath(im, cx, cy, r, colour, dark, gap_top=50, ribbon=RED):
    """Two branches of wheat around (cx, cy), from the bottom up to near the top, tied with a ribbon."""
    d = ImageDraw.Draw(im)
    t0, t1 = 168, gap_top / 2 + 8          # degrees from the top of the circle: bottom end, top end
    for side in (-1, 1):
        def at(t):
            a = math.radians(t)
            return cx + side * r * math.sin(a), cy - r * math.cos(a)
        d.line([at(t) for t in np.linspace(t0, t1, 40)], fill=dark, width=max(2, int(r * 0.06)))
        steps = 8
        for i in range(steps):
            t = t0 - 6 - (t0 - 6 - t1) * i / (steps - 1)
            a = math.radians(t)
            px, py = at(t)
            up = math.atan2(-math.sin(a), -side * math.cos(a))      # along the branch, towards its top
            g = r * (0.30 - 0.09 * i / steps)
            for off, shade in ((-0.5, colour), (0.5, dark)):          # a grain on each side of the stem
                ang = up + off
                gx, gy = px + math.cos(ang) * g * 0.55, py + math.sin(ang) * g * 0.55
                d.polygon(_rot([(-g * 0.6, 0), (0, -g * 0.27), (g * 0.6, 0), (0, g * 0.27)], gx, gy, ang), fill=shade)
        tx, ty = at(t1)
        up = math.atan2(-math.sin(math.radians(t1)), -side * math.cos(math.radians(t1)))
        g = r * 0.2
        d.polygon(_rot([(-g * 0.2, 0), (0, -g * 0.2), (g * 0.75, 0), (0, g * 0.2)], tx, ty, up), fill=colour)
    by = cy + r * 0.98                       # ribbon where the branches meet
    d.polygon([(cx - r * 0.22, by - r * 0.09), (cx + r * 0.22, by - r * 0.09), (cx + r * 0.30, by + r * 0.09),
               (cx - r * 0.30, by + r * 0.09)], fill=colour)


def cog(im, cx, cy, r, colour, teeth=12, width=0.24):
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    for i in range(teeth):
        a = i * 2 * math.pi / teeth
        d.polygon(_rot([(r * 0.9, -r * 0.13), (r * 1.2, -r * 0.10), (r * 1.2, r * 0.10), (r * 0.9, r * 0.13)],
                       cx, cy, a), fill=255)
    ri = r * (1 - width)
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=0)
    _paint(im, m, colour)


def rhombus(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def _arms(root):
    """The coat of arms of Sofia, cut out of the light blue of tools/flags/SOFIA.png."""
    im = Image.open(os.path.join(root, "tools", "flags", "SOFIA.png")).convert("RGB")
    a = np.asarray(im).astype(np.int32)
    bg = np.median(np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3)]), 0)
    near = np.abs(a - bg).sum(-1) < 60
    lab, _ = ndi.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    back = np.isin(lab, edge[edge > 0])
    fig = ndi.binary_fill_holes(~back)
    ys, xs = np.nonzero(fig)
    alpha = Image.fromarray((fig * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def _finish(im):
    return im.resize((246, 156), Image.LANCZOS)


def sredets():
    """Red, with Sredets' four rhombuses in gold inside a wheat wreath, the red star above, a white and gold
    stripe along the bottom: the old white flag of the centre, pushed down by the revolution."""
    im = Image.new("RGBA", (W, H), RED + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, H * 0.84, W, H), fill=WHITE)
    d.rectangle((0, H * 0.84, W, H * 0.865), fill=GOLD)
    cx, cy, r = W * 0.5, H * 0.45, H * 0.33
    wheat_wreath(im, cx, cy, r, GOLD, GOLD_DARK)
    q = r * 0.25
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        rhombus(d, cx + dx * q * 1.25, cy + dy * q * 1.25, q * 0.95, GOLD)
    star(d, cx, cy - r * 1.0, r * 0.32, GOLD)
    return _finish(im)


def oborishte():
    """Crimson, the golden rings of Oborishte turned into a cog, with the hammer and sickle inside; a gold band
    at the hoist with three red stars."""
    im = Image.new("RGBA", (W, H), CRIMSON + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W * 0.16, H), fill=GOLD)
    for i in range(3):
        star(d, W * 0.08, H * (0.22 + 0.28 * i), W * 0.048, CRIMSON)
    cx, cy = W * 0.58, H * 0.5
    cog(im, cx, cy, H * 0.34, GOLD, width=0.2)
    hammer_sickle(im, cx, cy, H * 0.40, GOLD)
    return _finish(im)


def sofia(root, variant=""):
    """The coat of arms of Sofia on red, in a wheat wreath under the red star. South Sofia carries a white
    band at the bottom, North Sofia one at the top: put together, the two make one flag again."""
    field = CRIMSON if variant == "north" else RED
    im = Image.new("RGBA", (W, H), field + (255,))
    d = ImageDraw.Draw(im)
    cy = H * 0.5
    if variant == "south":
        d.rectangle((0, H * 0.78, W, H), fill=WHITE)
        d.rectangle((0, H * 0.78, W, H * 0.80), fill=GOLD)
        cy = H * 0.42
    elif variant == "north":
        d.rectangle((0, 0, W, H * 0.22), fill=WHITE)
        d.rectangle((0, H * 0.20, W, H * 0.22), fill=GOLD)
        cy = H * 0.60
    cx = W * (0.5 if not variant else 0.34)
    r = H * (0.34 if not variant else 0.28)
    wheat_wreath(im, cx, cy, r, GOLD, GOLD_DARK, ribbon=field)
    arms = _arms(root)
    ah = int(r * 1.62)
    arms = arms.resize((int(arms.width * ah / arms.height), ah), Image.LANCZOS)
    im.alpha_composite(arms, (int(cx - arms.width / 2), int(cy - ah / 2 + r * 0.05)))
    if variant:   # the star of the half city in the fly, its point towards the other half
        sx = W * 0.74
        star(d, sx, cy, r * 0.55, GOLD, rot=math.pi if variant == "north" else 0.0)
    else:
        star(d, cx, cy - r * 1.02, r * 0.30, GOLD)
    return _finish(im)


BLUE = (32, 78, 165)
BLUE_LIGHT = (44, 93, 184)
SILVER = (226, 230, 238)
SILVER_DARK = (170, 178, 194)
SRD_RED = (220, 35, 40)


def free(root, variant=""):
    """The free centre (democratic branch): blue for liberty, light rays of a dawn behind a white disc that holds
    the old emblem of Sredets (its four red rhombuses), in a silver laurel wreath. No band at the bottom, so it
    never looks like the communist flags. The Free Centre of Sofia puts the arms of Sofia in the
    disc and the four rhombuses, in white, above the wreath."""
    im = Image.new("RGBA", (W, H), BLUE + (255,))
    d = ImageDraw.Draw(im)
    cx, cy, r = W * 0.5, H * (0.53 if variant == "centre" else 0.5), H * 0.34
    for i in range(16):                               # dawn rays
        a0 = i * 2 * math.pi / 16
        d.polygon([(cx, cy), (cx + W * math.cos(a0), cy + W * math.sin(a0)),
                   (cx + W * math.cos(a0 + math.pi / 16), cy + W * math.sin(a0 + math.pi / 16))], fill=BLUE_LIGHT)
    rd = r * 0.70
    d.ellipse((cx - rd * 1.06, cy - rd * 1.06, cx + rd * 1.06, cy + rd * 1.06), fill=SILVER_DARK)
    d.ellipse((cx - rd, cy - rd, cx + rd, cy + rd), fill=WHITE)
    wheat_wreath(im, cx, cy, r, SILVER, SILVER_DARK, ribbon=BLUE)
    q = r * 0.25
    if variant == "centre":
        arms = _arms(root)
        ah = int(rd * 1.72)
        arms = arms.resize((int(arms.width * ah / arms.height), ah), Image.LANCZOS)
        im.alpha_composite(arms, (int(cx - arms.width / 2), int(cy - ah / 2)))
        qq, top = q * 0.42, cy - r * 1.02
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            rhombus(d, cx + dx * qq * 1.25, top + dy * qq * 1.25, qq * 0.95, WHITE)
    else:
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            rhombus(d, cx + dx * q * 1.25, cy + dy * q * 1.25, q * 0.95, SRD_RED)
    return _finish(im)


DARK = (26, 28, 40)


def directorate():
    """The Directorate of Sofia: a dark field between two gold bands, a gold sword upright behind Sredets' four
    rhombuses, framed by a gold square standing on its point: the centre held in one hand."""
    im = Image.new("RGBA", (W, H), DARK + (255,))
    d = ImageDraw.Draw(im)
    for y0 in (H * 0.08, H * 0.86):
        d.rectangle((0, y0, W, y0 + H * 0.06), fill=GOLD)
    cx, cy, r = W * 0.5, H * 0.5, H * 0.30
    # the sword, behind everything
    d.rectangle((cx - r * 0.06, cy - r * 1.30, cx + r * 0.06, cy + r * 1.05), fill=GOLD_DARK)
    d.polygon([(cx - r * 0.06, cy + r * 1.05), (cx + r * 0.06, cy + r * 1.05), (cx, cy + r * 1.25)], fill=GOLD_DARK)
    d.rectangle((cx - r * 0.45, cy - r * 1.02, cx + r * 0.45, cy - r * 0.92), fill=GOLD_DARK)
    d.ellipse((cx - r * 0.11, cy - r * 1.44, cx + r * 0.11, cy - r * 1.22), fill=GOLD_DARK)
    # the frame: a gold square on its point, dark inside
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD)
    k = 0.84
    d.polygon([(cx, cy - r * k), (cx + r * k, cy), (cx, cy + r * k), (cx - r * k, cy)], fill=DARK)
    q = r * 0.24
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        rhombus(d, cx + dx * q * 1.25, cy + dy * q * 1.25, q * 0.95, GOLD)
    return _finish(im)


def make(root, recipe, arg=""):
    if recipe == "directorate":
        return directorate()
    if recipe == "free":
        return free(root, arg)
    if recipe == "district":
        return {"SRD": sredets, "OBR": oborishte}[arg]()
    return sofia(root, arg)
