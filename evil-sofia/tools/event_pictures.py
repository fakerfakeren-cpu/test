"""Event pictures, drawn by the build: district flags waving over a skyline of Sofia (panel blocks, a few
domes and the Vitosha behind), in the light of the moment: day, dusk, night, snow, rain, heat or fire. Toned and
grained like the old photographs of vanilla's events.

Sizes: country events 210x176, news events 397x153 (vanilla's frames).
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZES = {"country": (210, 176), "news": (397, 153)}
MOODS = {   # sky top, sky bottom, mountain, city, tone (multiplied in), particles
    "day": ((96, 140, 190), (205, 214, 214), (92, 108, 120), (44, 48, 54), (1.0, 0.97, 0.88), None),
    "dusk": ((60, 46, 86), (232, 140, 80), (70, 52, 70), (30, 22, 30), (1.0, 0.9, 0.8), None),
    "night": ((10, 14, 32), (40, 50, 86), (26, 30, 48), (12, 12, 18), (0.85, 0.9, 1.05), "lights"),
    "snow": ((150, 160, 172), (222, 226, 230), (190, 196, 204), (70, 74, 82), (0.95, 0.98, 1.05), "snow"),
    "rain": ((70, 78, 88), (132, 140, 146), (84, 92, 98), (36, 40, 44), (0.92, 0.96, 1.0), "rain"),
    "heat": ((214, 160, 90), (246, 220, 160), (180, 130, 90), (70, 50, 36), (1.05, 0.95, 0.8), None),
    "fire": ((30, 20, 22), (190, 70, 30), (60, 30, 26), (20, 12, 12), (1.05, 0.88, 0.78), "embers"),
}


def _skyline(w, h, rng, colour, base):
    """Panel blocks, towers and a couple of domes along the bottom of the picture."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    x = -10
    while x < w:
        bw = rng.integers(w // 22, w // 8)
        bh = rng.integers(h // 9, h // 3)
        if rng.random() < 0.12:                                  # a dome with its cross
            r = bw // 2
            d.rectangle((x, base - bh // 2, x + bw, base), fill=255)
            d.ellipse((x, base - bh // 2 - r, x + bw, base - bh // 2 + r), fill=255)
            d.rectangle((x + r - 1, base - bh // 2 - r - 8, x + r + 1, base - bh // 2 - r), fill=255)
        else:
            d.rectangle((x, base - bh, x + bw, base), fill=255)
        x += bw + rng.integers(0, 4)
    d.rectangle((0, base, w, h), fill=255)
    return m, colour


def _waving(flag, fw, fh, phase):
    """The flag on a pole, bent by the wind and shaded along its folds."""
    src = np.asarray(flag.convert("RGB").resize((fw, fh), Image.LANCZOS)).astype(np.float64)
    amp = fh * 0.08
    pad = int(amp * 2) + 2
    out = np.zeros((fh + 2 * pad, fw, 4))
    for x in range(fw):
        t = x / fw
        dy = amp * t * math.sin(2 * math.pi * (t * 1.6) + phase)
        slope = math.cos(2 * math.pi * (t * 1.6) + phase) * t
        shade = 1.0 + 0.22 * slope
        y0 = int(round(pad + dy))
        out[y0:y0 + fh, x, :3] = np.clip(src[:, x] * shade, 0, 255)
        out[y0:y0 + fh, x, 3] = 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def picture(kind, flags, mood, seed=0):
    """kind: country or news; flags: list of flag images (PIL), one to three; mood: a key of MOODS."""
    W, H = SIZES[kind]
    S = 2                                                         # drawn at twice the size, scaled down
    w, h = W * S, H * S
    rng = np.random.default_rng(seed)
    top, bottom, mountain, city, tone, particles = MOODS[mood]
    yy = np.linspace(0, 1, h)[:, None, None]
    sky = (np.array(top) * (1 - yy) + np.array(bottom) * yy) * np.ones((1, w, 1))
    im = Image.fromarray(sky.astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    # Vitosha behind the city
    base = int(h * 0.80)
    pts = [(0, h)]
    for i in range(0, w + 20, 20):
        x = i
        y = h * 0.52 + h * 0.16 * (abs(x / w - 0.62) * 1.6) ** 1.3 + rng.normal(0, h * 0.01)
        pts.append((x, y))
    pts.append((w, h))
    d.polygon(pts, fill=mountain)
    if particles == "lights" or mood == "night":
        for _ in range(60):
            x, y = rng.integers(0, w), rng.integers(int(h * 0.05), int(h * 0.5))
            d.point((x, y), fill=(230, 230, 210))
    city_mask, _ = _skyline(w, h, rng, city, base)
    im.paste(Image.new("RGBA", (w, h), city + (255,)), (0, 0), city_mask)
    if particles == "lights":                                     # lit windows
        cm = np.asarray(city_mask) > 0
        for _ in range(500):
            x, y = rng.integers(0, w), rng.integers(int(h * 0.55), base)
            if cm[y, x]:
                d.rectangle((x, y, x + 2, y + 2), fill=(250, 210, 120))
    # the flags on their poles, in front of the city
    n = len(flags)
    fw = int(w * (0.42 if n == 1 else 0.34 if n == 2 else 0.26))
    fh = int(fw * 156 / 246)
    for i, fl in enumerate(flags):
        cx = w * (i + 1) / (n + 1)
        top_y = int(h * 0.12) + (i % 2) * int(h * 0.04)
        px = int(cx - fw / 2)
        d.rectangle((px - 5, top_y - 6, px, int(h * 0.97)), fill=(40, 36, 32))
        d.ellipse((px - 7, top_y - 12, px + 2, top_y - 3), fill=(190, 160, 70))
        wav = _waving(fl, fw, fh, phase=1.3 * i + rng.random())
        im.alpha_composite(wav, (px, top_y - int(fh * 0.16)))
    d = ImageDraw.Draw(im)
    if particles == "snow":
        for _ in range(900):
            x, y, r = rng.integers(0, w), rng.integers(0, h), rng.integers(1, 4)
            d.ellipse((x, y, x + r, y + r), fill=(250, 250, 252))
    if particles == "rain":
        for _ in range(500):
            x, y = rng.integers(0, w), rng.integers(0, h)
            d.line((x, y, x - 4, y + 14), fill=(200, 205, 214), width=1)
    if particles == "embers":
        for _ in range(250):
            x, y = rng.integers(0, w), rng.integers(0, h)
            d.ellipse((x, y, x + 3, y + 3), fill=(255, rng.integers(120, 200), 60))
    im = im.convert("RGB").resize((W, H), Image.LANCZOS)
    # old photograph: toned, soft, grainy, darker towards the corners
    a = np.asarray(im).astype(np.float64)
    grey = a.mean(-1, keepdims=True)
    a = a * 0.72 + grey * 0.28
    a *= np.array(tone)
    a += rng.normal(0, 7, a.shape[:2])[..., None]
    yv, xv = np.mgrid[0:H, 0:W]
    v = 1 - 0.45 * (((xv - W / 2) / (W / 2)) ** 2 + ((yv - H / 2) / (H / 2)) ** 2) ** 1.4
    a *= np.clip(v, 0.35, 1)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.35))
    return im.convert("RGBA")


def flag_image(root, name):
    """A flag by name: a district tag (tools/flags), a red flag (tools/red_flags.py recipe) or a plain colour."""
    import red_flags
    plain = {"LEVSKI": (20, 70, 160), "CSKA": (180, 20, 30), "WHITE": (240, 240, 236)}
    if name in plain:
        im = Image.new("RGB", (246, 156), plain[name])
        if name in ("LEVSKI", "CSKA"):
            ImageDraw.Draw(im).rectangle((0, 62, 246, 94), fill=(240, 240, 236))
        return im
    recipes = {"SRD_RED": ("district", "SRD"), "OBR_RED": ("district", "OBR"), "SRD_SOFIA": ("sofia", ""),
               "SRD_SOUTH": ("sofia", "south"), "OBR_NORTH": ("sofia", "north"),
               "SRD_FREE": ("free", ""), "SRD_FREE_CENTRE": ("free", "centre"),
               "SRD_DIRECTORATE": ("directorate", "")}
    if name in recipes:
        return red_flags.make(root, *recipes[name])
    return Image.open(os.path.join(root, "tools", "flags", f"{name}.png")).convert("RGB").resize((246, 156))


def fit(im, kind):
    """A picture made for an event, scaled and cropped from the middle to the frame's size."""
    W, H = SIZES[kind]
    im = im.convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * s)), max(H, round(im.height * s))), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((l, t, l + W, t + H)).convert("RGBA")
