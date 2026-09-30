"""Paintings of the Oathbound story, placeable like vanilla's.

Each is drawn at eight times its final size with soft shapes and light, then reduced to 16 pixels per block and a
limited palette so it sits beside the vanilla paintings. data.py calls data(); lang.py reads TEXT.
Run directly to write the textures:  python3 -m tools.oath.paintings
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/main/resources/assets/oathbound/textures/painting')
S = 8   # supersampling


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def sky(w, h, stops, seed=1, stars=0):
    y = np.linspace(0, 1, h)[:, None, None]
    img = np.zeros((h, w, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = ((y >= t0) & (y <= t1)).astype(float)
        k = np.clip((y - t0) / max(1e-6, t1 - t0), 0, 1)
        img += m * (np.array(rgb(c0)) * (1 - k) + np.array(rgb(c1)) * k)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    if stars:
        d = ImageDraw.Draw(im)
        r = np.random.default_rng(seed)
        for _ in range(stars):
            x, yy = r.integers(0, w), r.integers(0, int(h * 0.6))
            s = S * (0.35 + 0.35 * r.random())
            b = int(150 + 105 * r.random())
            d.ellipse([x - s, yy - s, x + s, yy + s], fill=(b, b, int(b * 0.92)))
    return im


def glow(im, xy, radius, colour, strength=1.0):
    layer = Image.new('RGB', im.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=colour)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.6))
    a = np.asarray(im).astype(float) + np.asarray(layer).astype(float) * strength
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB')


def hills(d, w, h, base, amp, colour, seed, freq=0.004):
    r = np.random.default_rng(seed)
    p1, p2 = r.random() * 6, r.random() * 6
    pts = [(0, h)]
    for x in range(0, w + S, S):
        pts.append((x, base + amp * math.sin(x * freq + p1) + amp * 0.5 * math.sin(x * freq * 2.7 + p2)))
    pts.append((w, h))
    d.polygon(pts, fill=colour)


def finish(im, blocks_w, blocks_h, colours=28):
    small = im.resize((blocks_w * 16, blocks_h * 16), Image.LANCZOS)
    q = small.quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    return q


# ====================================================================== the paintings
def last_squire(W, H):
    im = sky(W, H, [(0, '#1a1430'), (0.55, '#5a3060'), (0.8, '#d0703a'), (1, '#f0b060')], 3, 30)
    d = ImageDraw.Draw(im)
    hills(d, W, H, H * 0.78, H * 0.04, (30, 22, 30), 5)
    # the squire on the hill, cloak blowing, lantern raised
    cx, gy = W * 0.45, H * 0.8
    ink = (18, 12, 20)
    d.polygon([(cx - W * 0.09, gy), (cx - W * 0.05, gy - H * 0.32), (cx + W * 0.04, gy - H * 0.32), (cx + W * 0.07, gy)], fill=ink)
    d.polygon([(cx - W * 0.05, gy - H * 0.3), (cx - W * 0.2, gy - H * 0.12), (cx - W * 0.14, gy - H * 0.08), (cx - W * 0.06, gy - H * 0.2)], fill=ink)
    d.ellipse([cx - W * 0.045, gy - H * 0.42, cx + W * 0.035, gy - H * 0.31], fill=ink)
    d.line([(cx + W * 0.03, gy - H * 0.27), (cx + W * 0.14, gy - H * 0.4)], fill=ink, width=int(W * 0.025))
    d.line([(cx + W * 0.14, gy - H * 0.4), (cx + W * 0.16, gy - H * 0.36)], fill=ink, width=S)
    lx, ly = cx + W * 0.16, gy - H * 0.33
    d.rectangle([lx - W * 0.02, ly - H * 0.025, lx + W * 0.02, ly + H * 0.035], fill=(255, 214, 130))
    return glow(im, (lx, ly), W * 0.14, (255, 170, 80), 1.4)


def fall_of_the_order(W, H):
    im = sky(W, H, [(0, '#0c0818'), (0.5, '#3a1850'), (0.75, '#8a2a30'), (1, '#e06a2a')], 7, 20)
    for x, r in ((0.3, 0.12), (0.62, 0.16), (0.8, 0.1)):
        im = glow(im, (W * x, H * 0.8), W * r, (255, 110, 40), 0.9)
    d = ImageDraw.Draw(im)
    base = H * 0.82
    ink = (14, 8, 16)
    for cx, h, w in ((0.18, 0.42, 0.06), (0.3, 0.3, 0.05), (0.45, 0.55, 0.08), (0.6, 0.36, 0.05), (0.74, 0.48, 0.07), (0.88, 0.25, 0.05)):
        x0, x1 = W * (cx - w / 2), W * (cx + w / 2)
        top = base - H * h
        d.rectangle([x0, top, x1, H], fill=ink)
        for m in range(int(x0), int(x1), S * 3):
            d.rectangle([m, top - S * 2, m + S * 1.5, top], fill=ink)
        # a broken top on some
        if h > 0.4:
            d.polygon([(x0, top), (x0 + (x1 - x0) * 0.4, top - H * 0.05), (x1, top + H * 0.03), (x1, top)], fill=(8, 4, 10))
    hills(d, W, H, base, H * 0.02, ink, 9)
    # the Gloam pouring from the sky
    im = glow(im, (W * 0.45, H * 0.1), W * 0.16, (160, 80, 255), 0.8)
    return im


def drowned_chapel(W, H):
    im = sky(W, H, [(0, '#0a1c24'), (0.5, '#1e4a52'), (0.62, '#3a8a86'), (1, '#07161c')], 11, 12)
    d = ImageDraw.Draw(im)
    water = H * 0.62
    d.rectangle([0, water, W, H], fill=(12, 40, 48))
    # the chapel, half under the tide
    cx = W * 0.5
    d.rectangle([cx - W * 0.2, water - H * 0.18, cx + W * 0.2, water + H * 0.05], fill=(30, 44, 48))
    d.polygon([(cx - W * 0.24, water - H * 0.18), (cx, water - H * 0.42), (cx + W * 0.24, water - H * 0.18)], fill=(24, 34, 38))
    d.rectangle([cx - W * 0.03, water - H * 0.56, cx + W * 0.03, water - H * 0.36], fill=(24, 34, 38))
    d.polygon([(cx - W * 0.05, water - H * 0.56), (cx, water - H * 0.66), (cx + W * 0.05, water - H * 0.56)], fill=(24, 34, 38))
    for k in (-1, 1):
        d.rectangle([cx + k * W * 0.1 - S, water - H * 0.12, cx + k * W * 0.1 + S, water - H * 0.04], fill=(120, 220, 200))
    # the bell's glow and its reflection
    im = glow(im, (cx, water - H * 0.46), W * 0.08, (120, 240, 210), 1.2)
    im = glow(im, (cx, water + H * 0.12), W * 0.1, (60, 160, 150), 0.7)
    d = ImageDraw.Draw(im)
    for i in range(6):
        y = water + H * (0.05 + i * 0.05)
        d.line([(W * 0.2 + i * S * 2, y), (W * 0.8 - i * S * 2, y)], fill=(40, 110, 110), width=S // 2)
    return im


def hollow_throne(W, H):
    im = sky(W, H, [(0, '#07050e'), (0.6, '#241638'), (1, '#120a1c')], 13, 0)
    im = glow(im, (W * 0.5, H * 0.3), W * 0.45, (130, 70, 220), 0.9)
    d = ImageDraw.Draw(im)
    ink = (10, 6, 14)
    cx = W * 0.5
    d.rectangle([cx - W * 0.3, H * 0.84, cx + W * 0.3, H], fill=(28, 20, 36))
    d.rectangle([cx - W * 0.2, H * 0.44, cx + W * 0.2, H * 0.84], fill=ink)
    d.polygon([(cx - W * 0.2, H * 0.44), (cx - W * 0.14, H * 0.2), (cx, H * 0.3), (cx + W * 0.14, H * 0.2), (cx + W * 0.2, H * 0.44)], fill=ink)
    d.rectangle([cx - W * 0.12, H * 0.6, cx + W * 0.12, H * 0.66], fill=(40, 30, 50))
    # the crown, cracked and glowing
    cy = H * 0.52
    d.polygon([(cx - W * 0.09, cy + H * 0.04), (cx - W * 0.09, cy - H * 0.02), (cx - W * 0.05, cy + H * 0.01), (cx, cy - H * 0.04),
               (cx + W * 0.05, cy + H * 0.01), (cx + W * 0.09, cy - H * 0.02), (cx + W * 0.09, cy + H * 0.04)], fill=(220, 180, 90))
    im = glow(im, (cx, cy), W * 0.14, (255, 200, 110), 1.0)
    for x in (0.12, 0.88):
        im = glow(im, (W * x, H * 0.7), W * 0.06, (255, 190, 90), 1.1)
    return im


def grove_king(W, H):
    im = sky(W, H, [(0, '#0a1420'), (0.6, '#1e3a3c'), (1, '#0c1a12')], 17, 26)
    im = glow(im, (W * 0.75, H * 0.2), W * 0.1, (230, 240, 210), 1.2)
    d = ImageDraw.Draw(im)
    ink = (10, 16, 12)
    hills(d, W, H, H * 0.8, H * 0.03, ink, 19)
    # the stag, head high
    cx, gy = W * 0.45, H * 0.8
    d.ellipse([cx - W * 0.16, gy - H * 0.3, cx + W * 0.12, gy - H * 0.16], fill=ink)
    for lx in (-0.12, -0.08, 0.05, 0.09):
        d.rectangle([cx + W * lx, gy - H * 0.2, cx + W * lx + S * 2, gy], fill=ink)
    d.polygon([(cx + W * 0.08, gy - H * 0.26), (cx + W * 0.14, gy - H * 0.44), (cx + W * 0.2, gy - H * 0.42), (cx + W * 0.12, gy - H * 0.22)], fill=ink)
    hx, hy = cx + W * 0.17, gy - H * 0.44
    d.ellipse([hx - S * 3, hy - S * 3, hx + S * 5, hy + S * 2], fill=ink)
    # antlers of light
    for side in (-1, 1):
        pts = [(hx, hy - S * 2)]
        for k in range(1, 6):
            pts.append((hx + side * k * S * 3.5, hy - k * S * 4 - (k % 2) * S * 3))
        d.line(pts, fill=(200, 255, 170), width=S)
        for (px, py) in pts[1::2]:
            d.line([(px, py), (px + side * S * 2, py - S * 5)], fill=(200, 255, 170), width=S // 2 + 1)
    return glow(im, (hx, hy - S * 14), W * 0.12, (150, 240, 120), 0.9)


def star_readers(W, H):
    im = sky(W, H, [(0, '#05040c'), (0.7, '#1c1030'), (1, '#2a1a3a')], 23, 120)
    d = ImageDraw.Draw(im)
    # the stars going out: a dark band sweeping across the sky
    band = Image.new('L', im.size, 0)
    ImageDraw.Draw(band).polygon([(W * 0.55, 0), (W, 0), (W, H * 0.45), (W * 0.7, H * 0.2)], fill=200)
    band = band.filter(ImageFilter.GaussianBlur(W * 0.04))
    im = Image.composite(Image.new('RGB', im.size, (6, 4, 10)), im, band)
    d = ImageDraw.Draw(im)
    ink = (12, 8, 18)
    hills(d, W, H, H * 0.85, H * 0.02, ink, 29)
    cx = W * 0.3
    d.rectangle([cx - W * 0.08, H * 0.6, cx + W * 0.08, H * 0.86], fill=ink)
    d.pieslice([cx - W * 0.09, H * 0.5, cx + W * 0.09, H * 0.7], 180, 360, fill=(40, 30, 60))
    d.line([(cx, H * 0.58), (cx + W * 0.14, H * 0.42)], fill=(170, 130, 70), width=S * 2)
    return glow(im, (cx, H * 0.64), W * 0.05, (180, 120, 255), 0.8)


def lantern_vigil(W, H):
    im = sky(W, H, [(0, '#06050a'), (1, '#140e1a')], 31, 8)
    d = ImageDraw.Draw(im)
    cx = W * 0.5
    d.rectangle([cx - S, H * 0.3, cx + S, H], fill=(20, 14, 18))
    d.line([(cx, H * 0.3), (cx + W * 0.2, H * 0.3)], fill=(20, 14, 18), width=S)
    lx, ly = cx + W * 0.2, H * 0.38
    d.rectangle([lx - S * 2, ly - S * 2, lx + S * 2, ly + S * 3], fill=(255, 210, 120))
    im = glow(im, (lx, ly), W * 0.5, (255, 160, 70), 1.2)
    d = ImageDraw.Draw(im)
    d.rectangle([0, H * 0.9, W, H], fill=(16, 12, 14))
    return im


# id: (painter, width, height, English title)
PAINTINGS = {
    'last_squire': (last_squire, 2, 2, 'The Last Squire'),
    'fall_of_the_order': (fall_of_the_order, 4, 2, 'The Night the Order Fell'),
    'drowned_chapel': (drowned_chapel, 2, 2, 'The Bells Beneath'),
    'hollow_throne': (hollow_throne, 2, 3, 'The Hollow Throne'),
    'grove_king': (grove_king, 2, 2, 'The Grove King'),
    'star_readers': (star_readers, 4, 3, 'Where the Stars Went Out'),
    'lantern_vigil': (lantern_vigil, 1, 2, 'Vigil'),
}


def textures():
    os.makedirs(OUT, exist_ok=True)
    for pid, (fn, w, h, _) in PAINTINGS.items():
        big = fn(w * 16 * S, h * 16 * S)
        finish(big, w, h).save(os.path.join(OUT, pid + '.png'))
    print(len(PAINTINGS), 'paintings written')


def data():
    for pid, (_, w, h, _) in PAINTINGS.items():
        D.write(f'painting_variant/{pid}.json', {
            'asset_id': f'oathbound:{pid}', 'width': w, 'height': h,
            'title': {'translate': f'painting.oathbound.{pid}.title', 'color': 'yellow'},
            'author': {'translate': f'painting.oathbound.{pid}.author', 'color': 'gray'}})
    D.tag('painting_variant/placeable', list(PAINTINGS), 'minecraft')


TEXT = {}
for _pid, (_, _, _, _title) in PAINTINGS.items():
    TEXT[f'painting.oathbound.{_pid}.title'] = _title
    TEXT[f'painting.oathbound.{_pid}.author'] = 'A Lanternguard hand'


if __name__ == '__main__':
    textures()
