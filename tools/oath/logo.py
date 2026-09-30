"""The mod logo (mods list and CurseForge): a dusk sky over the Order's ruins, the oath-sigil burning behind the
title, and embers rising.

Run from the repository root:  python3 -m tools.oath.logo
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .effects import blur, sigil_oath

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/main/resources/oathbound_logo.png')
W, H = 1024, 512
FONTS = ['/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf']


def font(size):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return a + (b - a) * t


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float) / 255


def sky():
    y = np.linspace(0, 1, H)[:, None]
    stops = [(0.0, '#07060f'), (0.45, '#1c1234'), (0.72, '#40224e'), (0.88, '#8a3a2a'), (1.0, '#d9782e')]
    img = np.zeros((H, W, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = ((y >= t0) & (y <= t1)).astype(float)
        k = np.clip((y - t0) / (t1 - t0), 0, 1)
        img += m[..., None] * (hexrgb(c0) * (1 - k[..., None]) + hexrgb(c1) * k[..., None])
    rng = np.random.default_rng(11)
    img += (rng.random((H, W, 1)) - 0.5) * 0.02
    # stars, thinning toward the horizon
    for _ in range(260):
        x, yy = rng.integers(0, W), rng.integers(0, int(H * 0.6))
        b = rng.random() ** 3 * (1 - yy / (H * 0.6))
        img[yy, x] += b * 0.9
        if b > 0.4:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < W and 0 <= yy + dy < H:
                    img[yy + dy, x + dx] += b * 0.3
    return np.clip(img, 0, 1)


def ruins(draw):
    """The skyline: hills, the broken spire, the citadel's towers and the barrow mound, all in silhouette."""
    ink = (8, 6, 14)
    base = H - 70
    pts = [(0, H)]
    for x in range(0, W + 8, 8):
        h = base + 18 * math.sin(x * 0.006) + 10 * math.sin(x * 0.017 + 1.3)
        pts.append((x, h))
    pts.append((W, H))
    draw.polygon(pts, fill=ink)
    # the Arcanist's Spire, left, its top broken
    sx = 150
    draw.polygon([(sx - 22, base + 10), (sx - 16, base - 190), (sx - 4, base - 214), (sx + 6, base - 196), (sx + 12, base - 206),
                  (sx + 18, base - 180), (sx + 24, base + 10)], fill=ink)
    for k in range(4):
        y = base - 40 - k * 42
        draw.rectangle([sx - 3, y, sx + 3, y + 10], fill=(255, 190, 110) if k % 2 == 0 else (180, 120, 70))
    # the Sundered Citadel, right: towers with crenels and one lit window
    for cx, h, w in ((820, 150, 42), (880, 110, 34), (930, 175, 46), (990, 95, 30)):
        draw.rectangle([cx - w // 2, base - h, cx + w // 2, base + 20], fill=ink)
        for m in range(-w // 2, w // 2, 10):
            draw.rectangle([cx + m, base - h - 10, cx + m + 5, base - h], fill=ink)
    draw.rectangle([926, base - 120, 934, base - 104], fill=(255, 190, 110))
    draw.polygon([(700, base + 5), (760, base - 30), (800, base + 5)], fill=ink)
    # the barrow mound, centre-left
    draw.ellipse([300, base - 36, 470, base + 40], fill=ink)


def glow(layer, radius, strength):
    a = np.asarray(layer).astype(float) / 255
    out = a.copy()
    for ch in range(a.shape[2]):
        out[..., ch] = a[..., ch] + blur(a[..., ch], radius) * strength
    return np.clip(out, 0, 1)


def generate():
    img = sky()
    # the oath-sigil, burning gold behind the title
    full = np.zeros((H, W))
    ox, oy = W // 2 - 220, H // 2 - 250
    full[oy:oy + 440, ox:ox + 440] = np.clip(sigil_oath(440), 0, 1) ** 1.5
    s = np.clip(full * 0.5 + blur(full, 5) * 0.7 + blur(full, 22) * 0.5, 0, 1) * 0.6
    img = np.clip(img + s[..., None] * hexrgb('#ffc85a'), 0, 1)
    base = Image.fromarray((img * 255).astype(np.uint8), 'RGB')
    draw = ImageDraw.Draw(base)
    ruins(draw)
    # embers
    rng = np.random.default_rng(5)
    embers = Image.new('RGB', (W, H), (0, 0, 0))
    ed = ImageDraw.Draw(embers)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(int(H * 0.35), H)
        r = rng.random() * 2.2 + 0.6
        c = (255, int(120 + rng.random() * 110), int(40 + rng.random() * 40))
        ed.ellipse([x - r, y - r, x + r, y + r], fill=c)
    e = glow(embers, 4, 2.5)
    arr = np.clip(np.asarray(base).astype(float) / 255 + e * 0.8, 0, 1)
    base = Image.fromarray((arr * 255).astype(np.uint8), 'RGB')

    # the title, with a dark edge and a gold glow
    title, sub = 'OATHBOUND', 'THE  HOLLOW  CROWN'
    tf, sf = font(132), font(40)
    text = Image.new('L', (W, H), 0)
    td = ImageDraw.Draw(text)
    tw = td.textlength(title, font=tf)
    tx, ty = (W - tw) / 2, H // 2 - 110
    td.text((tx, ty), title, font=tf, fill=255)
    sw = td.textlength(sub, font=sf)
    sub_layer = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sub_layer).text(((W - sw) / 2, ty + 150), sub, font=sf, fill=255)
    t = np.asarray(text).astype(float) / 255
    su = np.asarray(sub_layer).astype(float) / 255
    arr = np.asarray(base).astype(float) / 255
    halo = np.clip(blur(t, 14) * 1.6 + blur(t, 40) * 0.8, 0, 1)
    arr = np.clip(arr + halo[..., None] * hexrgb('#ff9a3a') * 0.55, 0, 1)
    edge = np.clip(np.asarray(Image.fromarray((t * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))).astype(float) / 255, 0, 1)
    arr = arr * (1 - edge[..., None] * 0.85) + edge[..., None] * hexrgb('#140a06') * 0.85
    # gold, bright at the top of the letters and deep at the foot
    yy = np.linspace(0, 1, H)[:, None]
    k = np.clip((yy - ty / H) / (130 / H), 0, 1)
    fill = hexrgb('#fff3c4') * (1 - k[..., None]) + hexrgb('#d9892a') * k[..., None]
    arr = arr * (1 - t[..., None]) + fill * t[..., None]
    sedge = np.clip(np.asarray(sub_layer.filter(ImageFilter.MaxFilter(5))).astype(float) / 255, 0, 1)
    arr = arr * (1 - sedge[..., None] * 0.7) + sedge[..., None] * hexrgb('#100812') * 0.7
    arr = arr * (1 - su[..., None]) + hexrgb('#e8dcff') * su[..., None]
    # a rule either side of the subtitle
    out = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(out)
    ly = ty + 174
    for x0, x1 in (((W - sw) / 2 - 150, (W - sw) / 2 - 24), ((W + sw) / 2 + 24, (W + sw) / 2 + 150)):
        d.line([(x0, ly), (x1, ly)], fill=(232, 190, 110), width=2)
        cx = x1 if x0 < W / 2 else x0
        d.polygon([(cx, ly - 5), (cx + 5, ly), (cx, ly + 5), (cx - 5, ly)], fill=(255, 214, 120))
    out.save(OUT, optimize=True)
    print('logo written', OUT)


if __name__ == '__main__':
    generate()
