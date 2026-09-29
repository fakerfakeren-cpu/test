"""Block textures (16x16 pixel art).

Stone is built from quantised value noise with a light-from-the-upper-left bevel on every blob, bricks and
tiles get per-piece tone, highlight and shadow edges, and anything that should glow is painted into a
separate transparent "_glow" overlay that the block model draws with light_emission.
"""
import math

import numpy as np

from .paint import Img, Ramp, hexrgb, mix, noise, BAYER4

N = 16

# ------------------------------------------------------------------ palettes
P = {
    'ward': Ramp('#5e5343', '#7d7159', '#9c8f72', '#b8ab8b', '#d0c4a4', '#e4dabd', '#f1e9d3'),
    'ward_mortar': hexrgb('#4a4133'),
    'gloam': Ramp('#110c18', '#1a1424', '#251d32', '#312742', '#3e3253', '#4d3f66'),
    'gloam_mortar': hexrgb('#08060c'),
    'moss': Ramp('#24133a', '#321b52', '#46266e', '#5c348b', '#7747a8', '#9563c4', '#b487dc'),
    'moss_green': Ramp('#1f3317', '#2d4a1f', '#3e6128', '#517a31', '#67933c'),
    'bark': Ramp('#09070c', '#120e17', '#1b1522', '#251d2e', '#30263b', '#3c3049'),
    'plank': Ramp('#140e1b', '#1e1527', '#291d35', '#352642', '#42304f', '#50395e'),
    'ring': Ramp('#1d1526', '#2b2038', '#3a2c4b', '#4a3a5f', '#5b4a72'),
    'stone': Ramp('#4e4e4e', '#5f5f5f', '#6f6f6f', '#7d7d7d', '#8b8b8b', '#9b9b9b', '#ababab'),
    'deepslate': Ramp('#1f1f24', '#29292f', '#34343b', '#404048', '#4d4d56', '#5b5b65'),
    'lumen': Ramp('#6a4a14', '#9c6f22', '#cf9a34', '#f0c253', '#ffe08a', '#fff4c8', '#ffffff'),
    'steel': Ramp('#1f232b', '#2c323c', '#3b424f', '#4d5564', '#626b7b', '#7c8595', '#a1a9b6'),
    'gold': Ramp('#5a3d0e', '#8a6118', '#b88a28', '#dcae42', '#f4d072', '#fff0b4'),
    'brass': Ramp('#3a2a10', '#5c421a', '#806026', '#a88236', '#cca44e', '#e8c878'),
    'iron': Ramp('#1c1d22', '#2c2e35', '#3e414a', '#53575f', '#6c717b', '#8a8f99'),
    'barrow': Ramp('#2e2b26', '#3d3931', '#4d483e', '#5e584c', '#716a5b', '#857d6c'),
    'tide': Ramp('#10231f', '#173129', '#1f4136', '#2a5445', '#376956', '#4b8069'),
    'arcane': Ramp('#10142e', '#171d40', '#1f2754', '#29336a', '#354182', '#44529c'),
    'violet_glow': Ramp('#4a1f8a', '#7a3fe0', '#a35cff', '#d0a8ff', '#f4e8ff'),
    'amber_glow': Ramp('#8a4a10', '#d8842a', '#ffb84a', '#ffe08a', '#fff8e0'),
    'teal_glow': Ramp('#1b6f63', '#2fb8a8', '#58e8d4', '#b8fff4', '#ffffff'),
    'blue_glow': Ramp('#2a2a9c', '#4f6cff', '#8aa8ff', '#c8d8ff', '#ffffff'),
}


def img():
    return Img(N, N)


def rng(seed):
    return np.random.default_rng(seed)


def field(seed, cell=4, octaves=2):
    return noise(N, N, cell, seed, octaves=octaves)


def put(im, x, y, c):
    im.put(x % N, y % N, c)


# ------------------------------------------------------------------ base materials
def stone(ramp, seed, contrast=1.0, blotch=True, lo=0.15, hi=0.85):
    """Vanilla-flavoured stone: soft blobs of 4-5 tones, each blob lit on its upper-left rim."""
    im = img()
    f = field(seed, 4, 3)
    f = (f - f.min()) / (f.max() - f.min() + 1e-9)
    levels = np.clip((f - 0.5) * contrast + 0.5, 0, 1)
    q = np.floor(levels * 5) / 4.0
    for y in range(N):
        for x in range(N):
            t = lo + (hi - lo) * q[y, x]
            if blotch:
                # bevel: brighter where the tone above-left is lower, darker where below-right is lower
                up = q[(y - 1) % N, (x - 1) % N]
                dn = q[(y + 1) % N, (x + 1) % N]
                if q[y, x] > up:
                    t += 0.1
                if q[y, x] > dn:
                    t -= 0.08
            im.px[y, x] = ramp.smooth(t + BAYER4[y % 4, x % 4] * 0.04)
    return im


def speckle(im, ramp, seed, rate=0.06, t=0.9):
    r = rng(seed)
    for y in range(N):
        for x in range(N):
            if r.random() < rate:
                im.px[y, x] = ramp.smooth(t + r.random() * 0.1)
    return im


def bricks(ramp, mortar, seed, rows=4, width=8, offset=4, tone=0.5, spread=0.14, bevel=True, base=None):
    """Running-bond brickwork. Each brick has its own tone, a lit top/left edge and a shaded bottom/right."""
    im = img()
    r = rng(seed)
    h = N // rows
    f = field(seed + 11, 3, 2)
    for row in range(rows):
        off = (row * offset) % width
        for b in range(-1, N // width + 1):
            x0 = b * width + off
            t0 = tone + (r.random() - 0.5) * spread * 2
            for y in range(row * h, row * h + h):
                for x in range(x0, x0 + width):
                    xx = x % N
                    ly, lx = y - row * h, x - x0
                    if ly == h - 1 or lx == width - 1:
                        im.px[y, xx] = mortar
                        continue
                    t = t0 + (f[y, xx] - 0.5) * 0.25
                    if bevel:
                        if ly == 0 or lx == 0:
                            t += 0.13
                        elif ly == h - 2 or lx == width - 2:
                            t -= 0.12
                    im.px[y, xx] = ramp.smooth(t + BAYER4[y % 4, xx % 4] * 0.05)
    return im


def tiles(ramp, mortar, seed, size=8, tone=0.55):
    im = img()
    r = rng(seed)
    f = field(seed + 3, 4, 2)
    for ty in range(0, N, size):
        for tx in range(0, N, size):
            t0 = tone + (r.random() - 0.5) * 0.18
            for y in range(ty, ty + size):
                for x in range(tx, tx + size):
                    ly, lx = y - ty, x - tx
                    if ly == size - 1 or lx == size - 1:
                        im.px[y, x] = mortar
                        continue
                    t = t0 + (f[y, x] - 0.5) * 0.18
                    if ly == 0 or lx == 0:
                        t += 0.12
                    elif ly == size - 2 or lx == size - 2:
                        t -= 0.1
                    im.px[y, x] = ramp.smooth(t)
    return im


def cracks(im, seed, color, count=3, length=7):
    r = rng(seed)
    for _ in range(count):
        x, y = r.integers(0, N), r.integers(0, N)
        for _ in range(length):
            put(im, x, y, color)
            x += r.integers(-1, 2)
            y += r.integers(0, 2)
    return im


def moss_over(im, ramp, seed, amount=0.45, top_bias=True):
    f = field(seed, 5, 2)
    for y in range(N):
        for x in range(N):
            v = f[y, x] + ((1 - y / N) * 0.25 if top_bias else 0)
            if v > 1 - amount:
                t = 0.3 + (v - (1 - amount)) * 1.4
                im.px[y, x] = ramp.smooth(t + BAYER4[y % 4, x % 4] * 0.1)
    return im


# ------------------------------------------------------------------ wardstone (the Lanternguard's pale limestone)
def wardstone():
    return speckle(stone(P['ward'], 101, lo=0.25, hi=0.8), P['ward'], 102, 0.03, 0.85)


def wardstone_bricks(seed=110):
    return bricks(P['ward'], P['ward_mortar'], seed, tone=0.58)


def cracked_wardstone_bricks():
    im = wardstone_bricks(111)
    return cracks(im, 112, hexrgb('#3a3226'), count=4, length=8)


def mossy_wardstone_bricks():
    return moss_over(wardstone_bricks(113), P['moss_green'], 114, 0.4)


def polished_wardstone():
    im = img()
    f = field(120, 6, 2)
    for y in range(N):
        for x in range(N):
            t = 0.62 + (f[y, x] - 0.5) * 0.12
            if x in (0, N - 1) or y in (0, N - 1):
                t = 0.42 if (x == N - 1 or y == N - 1) else 0.8
            im.px[y, x] = P['ward'].smooth(t + BAYER4[y % 4, x % 4] * 0.04)
    return im


def wardstone_tiles():
    return tiles(P['ward'], P['ward_mortar'], 125)


def chiseled_wardstone():
    """A carved frame around the Lanternguard lantern; the flame is in the glow overlay."""
    im = polished_wardstone()
    dark, light = P['ward'].smooth(0.28), P['ward'].smooth(0.88)
    for i in range(2, 14):
        im.put(i, 2, dark)
        im.put(2, i, dark)
        im.put(i, 13, light)
        im.put(13, i, light)
    # lantern silhouette carved in
    lantern = [
        "......##......",
        ".....####.....",
        "....#....#....",
        "...########...",
        "...#......#...",
        "...#......#...",
        "...#......#...",
        "...#......#...",
        "...########...",
        "....######....",
    ]
    glow = img()
    for j, row in enumerate(lantern):
        for i, ch in enumerate(row):
            x, y = i + 1, j + 3
            if ch == '#':
                im.put(x, y, P['ward'].smooth(0.22))
    for y in range(7, 11):
        for x in range(5, 11):
            t = 0.5 + 0.5 * (1 - abs(x - 7.5) / 3) * (1 - abs(y - 8.5) / 2.5)
            im.put(x, y, P['amber_glow'].smooth(t * 0.8))
            glow.put(x, y, P['amber_glow'].smooth(t))
    return im, glow


def wardstone_pillar_side():
    im = img()
    f = field(130, 4, 2)
    for y in range(N):
        for x in range(N):
            flute = x % 4
            t = 0.62 + (f[y, x] - 0.5) * 0.15
            t += {0: -0.22, 1: 0.12, 2: 0.04, 3: -0.06}[flute]
            im.px[y, x] = P['ward'].smooth(t)
    for x in range(N):
        im.put(x, 0, P['ward'].smooth(0.85))
        im.put(x, 1, P['ward'].smooth(0.5))
        im.put(x, N - 2, P['ward'].smooth(0.75))
        im.put(x, N - 1, P['ward'].smooth(0.35))
    return im


def wardstone_pillar_top():
    im = img()
    f = field(131, 4, 2)
    for y in range(N):
        for x in range(N):
            d = max(abs(x - 7.5), abs(y - 7.5))
            t = 0.6 + (f[y, x] - 0.5) * 0.12
            if d > 6.5:
                t = 0.4
            elif d > 5.5:
                t = 0.82
            elif 2.5 < math.hypot(x - 7.5, y - 7.5) < 3.6:
                t = 0.42
            im.px[y, x] = P['ward'].smooth(t)
    return im


# ------------------------------------------------------------------ the Gloam
def gloamstone():
    im = stone(P['gloam'], 201, lo=0.2, hi=0.85)
    r = rng(202)
    glow = img()
    for _ in range(3):
        x, y = r.integers(1, 15), r.integers(1, 15)
        im.put(x, y, P['violet_glow'].smooth(0.55))
        glow.put(x, y, P['violet_glow'].smooth(0.5))
    return im, glow


def gloamstone_bricks(seed=210):
    return bricks(P['gloam'], P['gloam_mortar'], seed, tone=0.55, spread=0.12)


def polished_gloamstone():
    im = img()
    f = field(220, 6, 2)
    for y in range(N):
        for x in range(N):
            t = 0.55 + (f[y, x] - 0.5) * 0.12
            if x in (0, N - 1) or y in (0, N - 1):
                t = 0.3 if (x == N - 1 or y == N - 1) else 0.78
            im.px[y, x] = P['gloam'].smooth(t)
    return im


def chiseled_gloamstone():
    """An eye of the Gloam inside a broken ring; the iris glows."""
    im = polished_gloamstone()
    glow = img()
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.2 < d < 6.2 and (int(math.degrees(math.atan2(y - 7.5, x - 7.5))) // 30) % 3 != 0:
                im.put(x, y, P['gloam'].smooth(0.1))
            ex = abs(x - 7.5) / 4.2
            ey = abs(y - 7.5) / (2.2 * (1 - min(1, ex) ** 2) ** 0.5 + 0.01) if ex < 1 else 9
            if ex < 1 and ey < 1:
                im.put(x, y, P['gloam'].smooth(0.05))
            if d < 1.6:
                im.put(x, y, P['violet_glow'].smooth(0.8))
                glow.put(x, y, P['violet_glow'].smooth(0.75))
    return im, glow


def gloam_moss_top():
    im = img()
    f = field(230, 3, 3)
    r = rng(231)
    glow = img()
    for y in range(N):
        for x in range(N):
            t = 0.35 + f[y, x] * 0.5
            im.px[y, x] = P['moss'].smooth(t + BAYER4[y % 4, x % 4] * 0.12)
            if r.random() < 0.035:
                im.px[y, x] = P['teal_glow'].smooth(0.55)
                glow.px[y, x] = P['teal_glow'].smooth(0.45)
    return im, glow


def gloam_moss_side():
    base, _ = gloamstone()
    im = base.copy()
    f = field(232, 3, 2)
    top, _ = gloam_moss_top()
    for x in range(N):
        depth = 3 + int(f[0, x] * 4)
        for y in range(depth):
            im.px[y, x] = top.px[y, x]
        im.px[depth, x] = P['moss'].smooth(0.15)
    return im


def gloamwood_log_side():
    """Near-black bark in long plates, split by fissures that burn violet."""
    im = img()
    glow = img()
    f = field(240, 3, 2)
    for y in range(N):
        for x in range(N):
            plate = (x + (y // 5)) % 5
            t = 0.45 + (f[y, x] - 0.5) * 0.35 + (0.12 if plate == 1 else 0) - (0.2 if plate == 4 else 0)
            im.px[y, x] = P['bark'].smooth(t + BAYER4[y % 4, x % 4] * 0.08)
    r = rng(241)
    for _ in range(3):
        x = int(r.integers(0, N))
        y = int(r.integers(0, 6))
        for k in range(int(r.integers(5, 10))):
            im.put(x % N, (y + k) % N, P['violet_glow'].smooth(0.55 - k * 0.03))
            glow.put(x % N, (y + k) % N, P['violet_glow'].smooth(0.5 - k * 0.03))
            if r.random() < 0.3:
                x += int(r.integers(-1, 2))
    return im, glow


def gloamwood_log_top():
    im = img()
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 7.5, y - 7.5)
            if x in (0, N - 1) or y in (0, N - 1):
                t = 0.2
                im.px[y, x] = P['bark'].smooth(0.35)
                continue
            ring = 0.5 + 0.3 * math.sin(d * 2.1)
            im.px[y, x] = P['ring'].smooth(ring + BAYER4[y % 4, x % 4] * 0.08)
    im.put(7, 7, P['violet_glow'].smooth(0.4))
    im.put(8, 8, P['violet_glow'].smooth(0.3))
    return im


def gloamwood_planks():
    im = img()
    r = rng(250)
    f = field(251, 4, 2)
    for row in range(4):
        y0 = row * 4
        seam = int(r.integers(3, 13))
        t0 = 0.55 + (r.random() - 0.5) * 0.2
        for y in range(y0, y0 + 4):
            for x in range(N):
                ly = y - y0
                grain = math.sin((x + row * 5) * 0.9 + f[y, x] * 3) * 0.06
                t = t0 + grain + (f[y, x] - 0.5) * 0.12
                if ly == 3:
                    t = 0.05
                elif ly == 0:
                    t += 0.1
                if x == seam and ly < 3:
                    t = 0.12
                im.px[y, x] = P['plank'].smooth(t)
    return im


# ------------------------------------------------------------------ ores and metals
def crystals(im, glow, seed, count, ramp, glow_ramp, base_t=0.55):
    """Small faceted crystal clusters: a bright facet, a mid facet and a dark edge."""
    r = rng(seed)
    spots = []
    tries = 0
    while len(spots) < count and tries < 200:
        tries += 1
        x, y = int(r.integers(2, 14)), int(r.integers(2, 14))
        if all(abs(x - a) + abs(y - b) > 4 for a, b in spots):
            spots.append((x, y))
    for (x, y) in spots:
        shape = [(0, 0), (1, 0), (0, -1), (1, -1), (0, 1), (-1, 0), (1, 1)]
        for i, (dx, dy) in enumerate(shape[:int(r.integers(4, 8))]):
            t = base_t + (0.35 if (dx, dy) in ((0, -1), (0, 0)) else 0.0) + (-0.25 if dx + dy > 1 else 0.0)
            im.put(x + dx, y + dy, ramp.smooth(t))
            glow.put(x + dx, y + dy, glow_ramp.smooth(min(1.0, t + 0.1)))
        im.put(x - 1, y + 1, ramp.smooth(0.12))
        im.put(x + 2, y, ramp.smooth(0.18))
    return im, glow


def lumenite_ore():
    base = stone(P['stone'], 301, lo=0.2, hi=0.85)
    return crystals(base, img(), 302, 4, P['lumen'], P['amber_glow'])


def deepslate_lumenite_ore():
    base = img()
    f = field(311, 4, 2)
    for y in range(N):
        for x in range(N):
            layer = 0.1 * math.sin(y * 1.6 + f[y, x] * 2)
            base.px[y, x] = P['deepslate'].smooth(0.45 + layer + (f[y, x] - 0.5) * 0.4 + BAYER4[y % 4, x % 4] * 0.05)
    return crystals(base, img(), 312, 4, P['lumen'], P['amber_glow'])


def lumenite_block():
    im = img()
    glow = img()
    for y in range(N):
        for x in range(N):
            # large faceted gems in a 2x2 arrangement
            cx, cy = (x // 8) * 8 + 3.5, (y // 8) * 8 + 3.5
            dx, dy = x - cx, y - cy
            if abs(dx) + abs(dy) <= 4.5:
                t = 0.65 + (0.25 if dx < 0 and dy < 0 else 0) - (0.2 if dx > 0 and dy > 0 else 0)
                t += 0.1 if abs(dx) + abs(dy) < 1.6 else 0
            else:
                t = 0.35
            im.px[y, x] = P['lumen'].smooth(t)
            glow.px[y, x] = P['amber_glow'].smooth(t * 0.9)
    return im, glow


def oathsteel_block():
    im = img()
    f = field(320, 5, 2)
    for y in range(N):
        for x in range(N):
            t = 0.55 + (f[y, x] - 0.5) * 0.14
            if x in (0, N - 1) or y in (0, N - 1):
                t = 0.25
            elif x == 1 or y == 1:
                t = 0.85
            elif x == N - 2 or y == N - 2:
                t = 0.35
            im.px[y, x] = P['steel'].smooth(t)
    for (x, y) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        im.put(x, y, P['steel'].smooth(0.95))
        im.put(x + 1, y + 1, P['steel'].smooth(0.2))
    # a gold-inlaid oath chevron
    for i in range(5):
        im.put(5 + i, 6 + i // 2, P['gold'].smooth(0.8))
        im.put(10 - i, 6 + i // 2, P['gold'].smooth(0.8))
        im.put(7 + (i % 2), 10 - i // 3, P['gold'].smooth(0.6))
    return im


# ------------------------------------------------------------------ plants
def veilbloom():
    """Bell-shaped violet blooms on thin dark stems; petals glow."""
    im = img()
    glow = img()
    stem = hexrgb('#1c1426')
    for (x0, top) in ((4, 6), (8, 3), (11, 7)):
        for y in range(top + 2, N):
            im.put(x0 + (1 if y > 12 and x0 == 4 else 0), y, stem)
        for dy in range(3):
            for dx in range(-1 - (dy // 2), 2 + (dy // 2)):
                t = 0.45 + 0.3 * (1 - abs(dx) / 2) + (0.15 if dy == 0 else 0)
                im.put(x0 + dx, top + dy, P['violet_glow'].smooth(t))
                glow.put(x0 + dx, top + dy, P['violet_glow'].smooth(t * 0.9))
        im.put(x0, top + 3, P['violet_glow'].smooth(0.95))
        glow.put(x0, top + 3, P['violet_glow'].smooth(1.0))
    for (x, y) in ((6, 13), (10, 12), (3, 14)):
        im.put(x, y, hexrgb('#2e4a2a'))
        im.put(x + 1, y - 1, hexrgb('#3b5c33'))
    return im, glow


# ------------------------------------------------------------------ puzzle, rite and relic blocks
def lore_tablet_front():
    im = polished_wardstone()
    glow = img()
    r = rng(401)
    for row in range(3, 13, 2):
        x = 3
        while x < 13:
            w = int(r.integers(1, 4))
            for i in range(w):
                if x + i < 13:
                    im.put(x + i, row, P['ward'].smooth(0.2))
            x += w + 1
    for x in range(3, 13):
        im.put(x, 1, P['amber_glow'].smooth(0.4))
        glow.put(x, 1, P['amber_glow'].smooth(0.3))
    return im, glow


def hymn_stone(progress, solved):
    """A standing stone cut with five bars of a hymn; lit bars show how far the hymn has come."""
    base = tiles(P['tide'], hexrgb('#0a1714'), 410, size=16, tone=0.55)
    glow = img()
    for i in range(5):
        y = 3 + i * 2
        lit = solved or i < progress
        for x in range(3, 13):
            c = P['teal_glow'].smooth(0.55 if lit else 0.1) if lit else P['tide'].smooth(0.18)
            base.put(x, y, c)
            if lit:
                glow.put(x, y, P['teal_glow'].smooth(0.5))
        nx = 4 + (i * 3) % 8
        base.put(nx, y - 1, P['teal_glow'].smooth(0.8) if lit else P['tide'].smooth(0.12))
        if lit:
            glow.put(nx, y - 1, P['teal_glow'].smooth(0.8))
    return base, glow


RUNE_GLYPHS = [
    ["..#..", ".###.", "#.#.#", "..#..", "..#.."],   # 0 the lantern
    ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],   # 1 the crossing
    ["..#..", ".#.#.", "#...#", ".#.#.", "..#.."],   # 2 the seal
    ["#####", "#...#", "#.#.#", "#...#", "#####"],   # 3 the keep
    [".###.", "#...#", "#.#..", "#...#", ".###."],   # 4 the eye
    ["#.#.#", "#.#.#", "#####", "..#..", "..#.."],   # 5 the crown
]


def rune_dial(glyph):
    im = img()
    glow = img()
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 7.5, y - 7.5)
            t = 0.45 if d < 6.8 else 0.3
            if 6.0 < d < 6.8:
                t = 0.75
            im.px[y, x] = P['arcane'].smooth(t + BAYER4[y % 4, x % 4] * 0.08)
    for k in range(8):
        a = k * math.pi / 4
        x, y = int(round(7.5 + math.cos(a) * 7)), int(round(7.5 + math.sin(a) * 7))
        im.put(x, y, P['brass'].smooth(0.8))
    for j, row in enumerate(RUNE_GLYPHS[glyph]):
        for i, ch in enumerate(row):
            if ch == '#':
                im.put(5 + i, 5 + j, P['blue_glow'].smooth(0.75))
                glow.put(5 + i, 5 + j, P['blue_glow'].smooth(0.7))
    return im, glow


def sundered_keystone(active):
    im, _ = chiseled_gloamstone()
    glow = img()
    for y in range(N):
        for x in range(N):
            if (x + y) % 5 == 0 and abs(x - y) > 3:
                c = P['violet_glow'].smooth(0.7 if active else 0.2)
                im.put(x, y, c)
                if active:
                    glow.put(x, y, P['violet_glow'].smooth(0.65))
    for y in range(6, 10):
        for x in range(6, 10):
            c = P['violet_glow'].smooth(0.9 if active else 0.25)
            im.put(x, y, c)
            if active:
                glow.put(x, y, P['violet_glow'].smooth(0.9))
    return im, glow


def barrow_stone():
    return speckle(stone(P['barrow'], 501, lo=0.2, hi=0.8), P['barrow'], 502, 0.04, 0.2)


def barrow_seal():
    im = tiles(P['barrow'], hexrgb('#1e1c18'), 510, size=16)
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 7.5, y - 7.5)
            if 4.5 < d < 5.6:
                im.put(x, y, P['brass'].smooth(0.55))
    for i in range(-3, 4):
        im.put(7 + i, 7 + i, P['barrow'].smooth(0.1))
        im.put(8 - i, 7 + i, P['barrow'].smooth(0.1))
    return im


def sealed_grate():
    im = img()
    for y in range(N):
        for x in range(N):
            bar = x % 4 in (1, 2) or y % 8 in (0, 1)
            if bar:
                t = 0.55 + (0.2 if x % 4 == 1 or y % 8 == 0 else -0.1)
                im.px[y, x] = P['iron'].smooth(t)
    for (x, y) in ((1, 0), (5, 0), (9, 0), (13, 0), (1, 8), (5, 8), (9, 8), (13, 8)):
        im.put(x, y, P['iron'].smooth(0.95))
    return im


def arcane_ward():
    """A translucent lattice of blue light."""
    im = img()
    for y in range(N):
        for x in range(N):
            hexline = (x + y * 2) % 8 == 0 or (x - y * 2) % 8 == 0 or y % 8 == 0
            if hexline:
                im.px[y, x] = np.append(P['blue_glow'].smooth(0.8)[:3], 0.85)
            else:
                im.px[y, x] = np.append(P['blue_glow'].smooth(0.35)[:3], 0.28)
    return im


def veil_frames(frames=16):
    """The Gloaming seen through a tear in the world: slow violet smoke, animated."""
    out = []
    for i in range(frames):
        im = img()
        ph = i / frames * 2 * math.pi
        for y in range(N):
            for x in range(N):
                v = (math.sin(x * 0.7 + ph) + math.sin(y * 0.55 - ph * 2) + math.sin((x + y) * 0.4 + ph)) / 3
                t = 0.35 + v * 0.3
                c = P['violet_glow'].smooth(t)
                im.px[y, x] = np.append(c[:3], 0.75)
        out.append(im)
    return out


def flame_frames(ramp=None, frames=8, seed=601):
    """A tall lantern flame: a white core in a gold body, flickering."""
    ramp = ramp or P['amber_glow']
    out = []
    r = rng(seed)
    for i in range(frames):
        im = img()
        sway = math.sin(i / frames * 2 * math.pi) * 1.2
        for y in range(N):
            for x in range(N):
                h = (N - y) / N
                cx = 7.5 + sway * h
                width = 5.5 * (1 - h) ** 0.7 * (0.85 + 0.15 * math.sin(i + y))
                d = abs(x - cx)
                if d < width and h < 0.95:
                    t = 1 - d / (width + 0.01)
                    t = t * (1 - h * 0.5) + (0.15 if r.random() < 0.1 else 0)
                    c = ramp.smooth(min(1, t * 1.1))
                    im.px[y, x] = np.append(c[:3], 1.0 if t > 0.25 else 0.0)
        out.append(im)
    return out


def brazier_metal():
    im = img()
    f = field(610, 3, 2)
    for y in range(N):
        for x in range(N):
            t = 0.55 + (f[y, x] - 0.5) * 0.3 + (0.15 if y % 4 == 0 else 0)
            im.px[y, x] = P['brass'].smooth(t)
    return im


def brazier_coals(lit):
    im = img()
    glow = img()
    r = rng(611)
    for y in range(N):
        for x in range(N):
            if lit and r.random() < 0.35:
                c = P['amber_glow'].smooth(0.5 + r.random() * 0.4)
                im.px[y, x] = c
                glow.px[y, x] = c
            else:
                im.px[y, x] = mix(hexrgb('#1a1410'), hexrgb('#3a2c22'), r.random())
    return im, glow


def bell_metal(tint):
    ramp = Ramp(*tint)
    im = img()
    for y in range(N):
        for x in range(N):
            t = 0.55 + 0.25 * math.sin(x / N * math.pi) - (0.2 if y % 5 == 4 else 0)
            im.px[y, x] = ramp.smooth(t + BAYER4[y % 4, x % 4] * 0.05)
    return im


BELL_TINTS = [
    ('#10205a', '#1f3a90', '#3a60c8', '#7a9ae8', '#c8d8ff'),   # blue
    ('#1f4a10', '#3a7a1f', '#5ea83a', '#94d66a', '#d0f4b0'),   # lime
    ('#5a4210', '#90701f', '#c8a03a', '#e8c86a', '#fff0b0'),   # yellow
    ('#5a1010', '#901f1f', '#c83a3a', '#e87a6a', '#ffc8b8'),   # red
]


def lantern_frame():
    im = img()
    for y in range(N):
        for x in range(N):
            edge = x in (0, 1, 14, 15) or y in (0, 1, 14, 15)
            if edge:
                im.px[y, x] = P['iron'].smooth(0.45 + (0.25 if x in (0, 1) or y in (0, 1) else 0))
            else:
                im.px[y, x] = np.zeros(4)
    return im


def lantern_pane(lit):
    im = img()
    glow = img()
    for y in range(N):
        for x in range(N):
            if x in (0, 15) or y in (0, 15):
                im.px[y, x] = P['iron'].smooth(0.5)
                continue
            if lit:
                t = 0.55 + 0.4 * (1 - math.hypot(x - 7.5, y - 8.5) / 9)
                im.px[y, x] = P['amber_glow'].smooth(t)
                glow.px[y, x] = P['amber_glow'].smooth(t)
            else:
                im.px[y, x] = mix(hexrgb('#1a1810'), hexrgb('#302a1c'), (x + y) % 3 / 3)
    return im, glow


def sarcophagus_side(king):
    im = tiles(P['barrow'], hexrgb('#1e1c18'), 520 + king, size=16, tone=0.5)
    emblem = [
        ["#.#.#", "#####", "#...#", "#####", "....."],   # crown
        ["..#..", "..#..", ".###.", "..#..", "..#.."],   # sword
        [".###.", "#####", "#####", ".###.", "..#.."],   # shield
    ][king]
    for j, row in enumerate(emblem):
        for i, ch in enumerate(row):
            if ch == '#':
                im.put(5 + i + 1, 5 + j + 1, P['brass'].smooth(0.75))
    return im


def sarcophagus_top(open_):
    im = tiles(P['barrow'], hexrgb('#1e1c18'), 530, size=16, tone=0.55)
    for y in range(2, 14):
        im.put(7, y, P['barrow'].smooth(0.25))
        im.put(8, y, P['barrow'].smooth(0.75))
    for x in range(4, 12):
        im.put(x, 5, P['barrow'].smooth(0.25))
    return im


def cipher_book(solved):
    im = img()
    glow = img()
    for y in range(N):
        for x in range(N):
            page = 1 <= y <= 14 and 1 <= x <= 14
            if not page:
                im.px[y, x] = P['plank'].smooth(0.4)
                continue
            gutter = x in (7, 8)
            t = 0.75 - (0.25 if gutter else 0)
            im.px[y, x] = mix(hexrgb('#b39b6d'), hexrgb('#efe0b8'), t)
    r = rng(540)
    for row in range(3, 13, 2):
        for x in list(range(2, 7)) + list(range(9, 14)):
            if r.random() < 0.7:
                c = P['blue_glow'].smooth(0.7) if solved else hexrgb('#3a2a1a')
                im.put(x, row, c)
                if solved:
                    glow.put(x, row, P['blue_glow'].smooth(0.6))
    return im, glow


# ====================================================================== building families (second wave)
P.update({
    'tidestone': Ramp('#0f201c', '#16302a', '#1f4136', '#2b5546', '#3a6b58', '#4f846d'),
    'tide_mortar': hexrgb('#08120f'),
    'barrowstone': Ramp('#2a2722', '#38342d', '#48433a', '#59534a', '#6d665a', '#827a6b'),
    'barrow_mortar': hexrgb('#171512'),
    'runestone': Ramp('#10142e', '#171d40', '#1f2754', '#29336a', '#354182', '#44529c'),
    'rune_mortar': hexrgb('#080a18'),
    'stripped': Ramp('#2a1d36', '#382748', '#48335c', '#583f70', '#6a4c84'),
    'bone': Ramp('#6e6450', '#948870', '#b8ad92', '#d8cfb4', '#efe9d6'),
    'shell': Ramp('#6b6a5a', '#8f8c78', '#b4b09a', '#d6d2bc', '#f0ecd8'),
    'ember_glow': Ramp('#6a1a04', '#b83a0c', '#f06a1c', '#ffb040', '#fff0a0'),
    'moon_glow': Ramp('#3a4a8a', '#6a86d0', '#a8c0f0', '#dce8ff', '#ffffff'),
})


def tidestone():
    im = stone(P['tidestone'], 701, lo=0.2, hi=0.85)
    r = rng(702)
    for _ in range(6):
        x, y = int(r.integers(0, N)), int(r.integers(0, N))
        im.put(x, y, P['shell'].smooth(0.7))
        im.put((x + 1) % N, y, P['shell'].smooth(0.45))
    return im


def tidestone_bricks(seed=710):
    return bricks(P['tidestone'], P['tide_mortar'], seed, tone=0.55)


def barnacled_tidestone_bricks():
    im = tidestone_bricks(711)
    r = rng(712)
    for _ in range(9):
        x, y = int(r.integers(0, N)), int(r.integers(0, N))
        for dx, dy, t in ((0, 0, 0.8), (1, 0, 0.6), (0, 1, 0.55), (1, 1, 0.35)):
            im.put((x + dx) % N, (y + dy) % N, P['shell'].smooth(t))
        im.put(x, y, P['shell'].smooth(0.15))
    return moss_over(im, P['moss_green'], 713, 0.2, top_bias=False)


def chiseled_tidestone():
    im = tiles(P['tidestone'], P['tide_mortar'], 720, size=16, tone=0.55)
    glow = img()
    for x in range(2, 14):
        y = int(round(8 + math.sin(x * 0.8) * 2))
        for dy in (0, 1):
            im.put(x, y + dy, P['teal_glow'].smooth(0.55 if dy == 0 else 0.35))
            glow.put(x, y + dy, P['teal_glow'].smooth(0.5 if dy == 0 else 0.3))
    for x in range(1, 15):
        im.put(x, 2, P['tidestone'].smooth(0.85))
        im.put(x, 13, P['tidestone'].smooth(0.2))
    return im, glow


def barrowstone():
    return speckle(stone(P['barrowstone'], 730, lo=0.2, hi=0.8), P['barrowstone'], 731, 0.04, 0.15)


def barrowstone_bricks(seed=740):
    return bricks(P['barrowstone'], P['barrow_mortar'], seed, rows=4, width=8, tone=0.52)


def bone_inlaid_barrowstone():
    """Barrow masonry with a femur and skulls pressed into the mortar courses."""
    im = barrowstone_bricks(741)
    for x in range(3, 13):
        im.put(x, 7, P['bone'].smooth(0.75))
        im.put(x, 8, P['bone'].smooth(0.45))
    for (x, y) in ((2, 7), (2, 8), (13, 7), (13, 8)):
        im.put(x, y, P['bone'].smooth(0.9))
    for cx in (4, 11):
        for dx in range(3):
            im.put(cx - 1 + dx, 2, P['bone'].smooth(0.8))
            im.put(cx - 1 + dx, 3, P['bone'].smooth(0.6))
        im.put(cx - 1, 3, P['barrowstone'].smooth(0.05))
        im.put(cx + 1, 3, P['barrowstone'].smooth(0.05))
        im.put(cx, 4, P['bone'].smooth(0.5))
    return im


def runestone():
    return stone(P['runestone'], 750, lo=0.3, hi=0.8)


def runestone_bricks(seed=760):
    return bricks(P['runestone'], P['rune_mortar'], seed, rows=2, width=8, offset=4, tone=0.5)


def glyphed_runestone():
    im = tiles(P['runestone'], P['rune_mortar'], 770, size=16, tone=0.5)
    glow = img()
    glyph = RUNE_GLYPHS[4]
    for j, row in enumerate(glyph):
        for i, ch in enumerate(row):
            if ch == '#':
                for (ox, oy) in ((0, 0),):
                    x, y = 3 + i * 2 + ox, 3 + j * 2 + oy
                    for dx in range(2):
                        for dy in range(2):
                            im.put(x + dx, y + dy, P['blue_glow'].smooth(0.7))
                            glow.put(x + dx, y + dy, P['blue_glow'].smooth(0.65))
    return im, glow


def cracked_gloamstone_bricks():
    return cracks(gloamstone_bricks(211), 212, hexrgb('#050308'), count=4, length=8)


def gloamstone_tiles():
    return tiles(P['gloam'], P['gloam_mortar'], 213)


def stripped_gloamwood_side():
    im = img()
    f = field(780, 4, 2)
    for y in range(N):
        for x in range(N):
            t = 0.5 + 0.18 * math.sin(x * 1.3 + f[y, x] * 3) + (f[y, x] - 0.5) * 0.2
            im.px[y, x] = P['stripped'].smooth(t)
    return im


def stripped_gloamwood_top():
    im = img()
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 7.5, y - 7.5)
            t = 0.55 + 0.25 * math.sin(d * 2.1)
            if x in (0, N - 1) or y in (0, N - 1):
                t = 0.35
            im.px[y, x] = P['stripped'].smooth(t)
    return im


def gloamwood_door(top):
    """A heavy plank door with iron straps; the upper half has a small window of violet glass."""
    im = gloamwood_planks()
    for y in range(N):
        im.put(0, y, P['plank'].smooth(0.1))
        im.put(N - 1, y, P['plank'].smooth(0.1))
    strap_rows = (3, 12)
    for y in strap_rows:
        for x in range(1, N - 1):
            im.put(x, y, P['iron'].smooth(0.55))
            im.put(x, y + 1, P['iron'].smooth(0.3))
        im.put(3, y, P['iron'].smooth(0.9))
        im.put(12, y, P['iron'].smooth(0.9))
    if top:
        for y in range(5, 10):
            for x in range(5, 11):
                if x in (5, 10) or y in (5, 9):
                    im.put(x, y, P['iron'].smooth(0.4))
                else:
                    c = P['violet_glow'].smooth(0.3 + 0.1 * ((x + y) % 2))
                    c[3] = 0.75
                    im.px[y, x] = c
    else:
        im.put(12, 7, P['brass'].smooth(0.9))
        im.put(12, 8, P['brass'].smooth(0.6))
    return im


def gloamwood_trapdoor():
    im = gloamwood_planks()
    for x in range(N):
        for y in (0, N - 1):
            im.put(x, y, P['iron'].smooth(0.4))
    for y in range(N):
        for x in (0, N - 1):
            im.put(x, y, P['iron'].smooth(0.4))
    for y in range(4, 12):
        for x in range(4, 12):
            if (x + y) % 4 == 0:
                im.px[y, x] = np.zeros(4)
    return im


def lumenite_lamp(lit):
    im = img()
    glow = img()
    for y in range(N):
        for x in range(N):
            frame = x in (0, 1, 14, 15) or y in (0, 1, 14, 15)
            if frame:
                im.px[y, x] = P['brass'].smooth(0.35 + (0.3 if x in (0, 1) or y in (0, 1) else 0))
                continue
            cx, cy = (x // 4) * 4 + 1.5, (y // 4) * 4 + 1.5
            d = abs(x - cx) + abs(y - cy)
            t = 0.75 - d * 0.12
            if lit:
                im.px[y, x] = P['lumen'].smooth(t)
                glow.px[y, x] = P['amber_glow'].smooth(t)
            else:
                im.px[y, x] = mix(hexrgb('#3a2e1c'), hexrgb('#6a5634'), max(0, t))
    return im, glow


def tinted_glass(ramp, alpha=0.45, streak=0.3):
    im = img()
    for y in range(N):
        for x in range(N):
            edge = x in (0, N - 1) or y in (0, N - 1)
            if edge:
                c = ramp.smooth(0.3)
                c[3] = 0.95
            else:
                t = 0.55 + (streak if (x + y) % 7 == 0 and 3 < x < 12 else 0)
                c = ramp.smooth(t)
                c[3] = alpha
            im.px[y, x] = c
    return im


def oathsteel_bars():
    im = img()
    for y in range(N):
        for x in (7, 8):
            im.put(x, y, P['steel'].smooth(0.75 if x == 7 else 0.4))
    for y in (2, 13):
        for x in range(N):
            im.put(x, y, P['steel'].smooth(0.6))
    im.put(7, 2, P['gold'].smooth(0.8))
    im.put(8, 13, P['gold'].smooth(0.8))
    return im


def hanging_lantern(ramp, glow_ramp):
    """A lantern texture in vanilla's lantern layout (body 6x7 at the top-left, cap and chain beside it)."""
    im = img()
    glow = img()
    for y in range(9):
        for x in range(6):
            edge = x in (0, 5) or y in (0, 1, 8)
            if edge:
                im.put(x, y, P['iron'].smooth(0.5 + (0.2 if x == 0 else 0)))
            else:
                c = glow_ramp.smooth(0.55 + 0.3 * (1 - abs(x - 2.5) / 3))
                im.put(x, y, c)
                glow.put(x, y, c)
    for y in range(9, 11):
        for x in range(1, 5):
            im.put(x, y, P['iron'].smooth(0.6))
    for y in range(2):
        for x in range(1, 5):
            im.put(x, 12 + y, P['iron'].smooth(0.45))
    for y in range(N):
        im.put(11, y, P['iron'].smooth(0.5 if y % 2 else 0.8))
    return im, glow


def flower(kind):
    im = img()
    glow = img()
    stem = hexrgb('#1f3319')
    leaf = hexrgb('#35572a')
    if kind == 'dusk_lily':
        for y in range(7, N):
            im.put(8, y, stem)
        im.put(7, 12, leaf)
        im.put(6, 11, leaf)
        im.put(9, 13, leaf)
        petals = [(8, 3), (7, 4), (9, 4), (6, 5), (10, 5), (7, 5), (9, 5), (8, 5), (8, 4), (6, 6), (10, 6), (8, 6)]
        for (x, y) in petals:
            t = 0.35 + (0.3 if y <= 4 else 0) + (0.2 if x == 8 else 0)
            im.put(x, y, P['violet_glow'].smooth(t))
        im.put(8, 5, P['amber_glow'].smooth(0.9))
        glow.put(8, 5, P['amber_glow'].smooth(0.8))
    elif kind == 'emberroot':
        for (x0, top) in ((5, 7), (10, 5)):
            for y in range(top, N):
                im.put(x0 + (1 if y > 11 else 0), y, hexrgb('#3a1c10'))
            for dy in range(3):
                c = P['ember_glow'].smooth(0.5 + dy * 0.15)
                im.put(x0, top - dy, c)
                glow.put(x0, top - dy, c)
                if dy < 2:
                    im.put(x0 + 1, top - dy, P['ember_glow'].smooth(0.35))
        im.put(7, 14, leaf)
        im.put(8, 13, leaf)
    elif kind == 'moonpetal':
        for y in range(8, N):
            im.put(7, y, stem)
        for a in range(6):
            ang = a * math.pi / 3
            for rr in (1, 2, 3):
                x, y = int(round(7 + math.cos(ang) * rr)), int(round(5 + math.sin(ang) * rr * 0.8))
                c = P['moon_glow'].smooth(0.85 - rr * 0.15)
                im.put(x, y, c)
                glow.put(x, y, P['moon_glow'].smooth(0.6 - rr * 0.12))
        im.put(7, 5, P['amber_glow'].smooth(0.9))
        im.put(6, 11, leaf)
        im.put(8, 12, leaf)
    elif kind == 'gloam_fern':
        r = rng(790)
        for frond in range(5):
            x0 = 3 + frond * 2.4
            h = int(r.integers(8, 14))
            for k in range(h):
                x = int(round(x0 + math.sin(k * 0.4 + frond) * 1.2))
                y = N - 1 - k
                im.put(x, y, P['moss'].smooth(0.3 + k / h * 0.5))
                if k % 2 == 0 and k > 2:
                    im.put(x + 1, y, P['moss'].smooth(0.45 + k / h * 0.3))
            glow.put(int(round(x0)), N - h, P['teal_glow'].smooth(0.5))
            im.put(int(round(x0)), N - h, P['teal_glow'].smooth(0.6))
    return im, glow


def glimmer_moss():
    im, gl = gloam_moss_top()
    r = rng(795)
    for _ in range(8):
        x, y = int(r.integers(0, N)), int(r.integers(0, N))
        im.put(x, y, P['teal_glow'].smooth(0.7))
        gl.put(x, y, P['teal_glow'].smooth(0.6))
    return im, gl
