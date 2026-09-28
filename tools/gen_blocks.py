"""Block textures for Astralfall."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'astralfall', 'textures', 'block')

ROCK = [hexc('#120f16'), hexc('#1f1a25'), hexc('#2d2634'), hexc('#3d3446'), hexc('#4d4358')]
LAVA = [hexc('#5a1606'), hexc('#b4380c'), hexc('#ff7a1f'), hexc('#ffc56b'), hexc('#fff1c9')]
NAVY = [hexc('#0c0f2a'), hexc('#161b44'), hexc('#212962'), hexc('#2e3880'), hexc('#4150a6')]
GOLD = [hexc('#6b4a12'), hexc('#b9862a'), hexc('#f2c14e'), hexc('#ffe9a3')]
CYAN = [hexc('#123e5c'), hexc('#1f7ea3'), hexc('#3fc6e0'), hexc('#9af3ff'), hexc('#effeff')]
VIOLET = [hexc('#2a0f4a'), hexc('#5a2394'), hexc('#9150e0'), hexc('#c998ff'), hexc('#f3e4ff')]
STEEL = [hexc('#28324d'), hexc('#46587f'), hexc('#6f86b6'), hexc('#a9c1ea'), hexc('#eef5ff')]


def rock_base(seed, dark=0.0):
    n = value_noise(16, 16, 4, seed, octaves=3)
    n2 = value_noise(16, 16, 2, seed + 7, octaves=2)
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            v = 0.55 * n[y, x] + 0.45 * n2[y, x] - dark
            c.set(x, y, ramp(ROCK, v * 1.1))
    # pits
    r = rng(seed)
    for _ in range(6):
        x, y = r.randrange(16), r.randrange(16)
        c.set(x, y, ROCK[0])
        c.set((x + 1) % 16, y, ROCK[1])
    return c


def cracks(c, seed, count, colors, glow=True):
    r = rng(seed)
    pts = []
    for _ in range(count):
        x, y = r.randrange(16), r.randrange(16)
        length = r.randrange(5, 11)
        dx, dy = r.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
        for i in range(length):
            pts.append((x % 16, y % 16, i / max(1, length - 1)))
            if r.random() < 0.45:
                dx, dy = r.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 1)])
            x += dx
            y += dy
    if glow:
        for (x, y, _) in pts:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                base = c.get(x + ox, y + oy)
                c.set((x + ox) % 16, (y + oy) % 16, lerp(base, colors[1], 0.35))
    for (x, y, t) in pts:
        v = 1 - abs(t - 0.5) * 1.2
        c.set(x, y, ramp(colors, 0.35 + 0.6 * v))
    return c


def meteorite_rock():
    c = rock_base(11)
    cracks(c, 12, 3, LAVA)
    return c


def meteorite_rock_cool():
    """Cooled meteorite used in older craters and the vessel."""
    c = rock_base(21)
    cracks(c, 22, 2, VIOLET)
    return c


def ore_specks(c, seed, colors, clusters=5):
    r = rng(seed)
    for _ in range(clusters):
        x, y = r.randrange(1, 15), r.randrange(1, 15)
        shape = r.choice([[(0, 0), (1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (-1, 0), (0, 1)], [(0, 0), (1, 1), (0, 1)], [(0, 0), (1, 0), (1, 1), (2, 1)]])
        for i, (ox, oy) in enumerate(shape):
            col = colors[2] if i else colors[3]
            c.set(x + ox, y + oy, col)
        c.set(x + shape[-1][0] + 1, y + shape[-1][1], colors[1])
        c.set(x, y, colors[4])
    return c


def starmetal_ore():
    c = rock_base(31)
    cracks(c, 32, 1, LAVA)
    ore_specks(c, 33, STEEL, 6)
    return c


def raw_starmetal_block():
    n = value_noise(16, 16, 3, 41, octaves=3)
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            c.set(x, y, ramp(STEEL[:4], 0.15 + n[y, x] * 0.8))
    r = rng(42)
    for _ in range(10):
        x, y = r.randrange(16), r.randrange(16)
        c.set(x, y, STEEL[4])
    cracks(c, 43, 2, [ROCK[1], ROCK[2], ROCK[3], ROCK[3], ROCK[4]], glow=False)
    return c


def starmetal_block():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            t = 0.45 + 0.35 * ((15 - y) / 15) * 0.6 + 0.2 * (x / 15) * 0.3
            c.set(x, y, ramp(STEEL, t))
    # plate borders
    for i in range(16):
        c.set(i, 0, STEEL[4]); c.set(0, i, STEEL[4])
        c.set(i, 15, STEEL[0]); c.set(15, i, STEEL[0])
        c.set(i, 7, STEEL[1]); c.set(i, 8, STEEL[3])
    # central star emblem (gold)
    poly = star_points(7.5, 7.5, 5.2, 1.7, 4)
    for y in range(16):
        for x in range(16):
            if point_in_poly(x + 0.5, y + 0.5, poly):
                d = math.hypot(x - 7.5, y - 7.5)
                c.set(x, y, ramp(GOLD, 1 - d / 6))
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        c.set(x, y, STEEL[4]); c.set(x + 1, y + 1, STEEL[1])
    return c


def skyshard_block():
    c = Canvas(16, 16)
    # faceted crystal: diagonal bands alternating cyan and violet
    for y in range(16):
        for x in range(16):
            u = (x + y) % 16
            v = (x - y) % 16
            facet = (u // 4 + v // 4) % 3
            base = [CYAN, VIOLET, CYAN][facet]
            t = 0.35 + 0.5 * ((u % 4) / 3.0) * 0.5 + 0.25 * (1 - (v % 4) / 3.0)
            c.set(x, y, ramp(base, t))
    r = rng(51)
    for _ in range(7):
        x, y = r.randrange(16), r.randrange(16)
        c.set(x, y, CYAN[4])
    for i in range(16):
        if i % 4 == 0:
            c.line(i, 0, 0, i, lerp(CYAN[4], VIOLET[3], 0.3))
    return c


def skyshard_cluster():
    c = Canvas(16, 16)
    crystals = [(7, 15, 2, 12, CYAN), (4, 15, 1, 7, VIOLET), (11, 15, 1, 8, VIOLET), (9, 15, 1, 10, CYAN), (5, 15, 1, 5, CYAN), (12, 15, 1, 5, CYAN)]
    for (cx, base_y, half, height, pal) in crystals:
        for dy in range(height):
            y = base_y - dy
            w = half if dy < height - 2 else max(0, half - 1)
            if dy == height - 1:
                c.set(cx, y, pal[4])
                continue
            for dx in range(-w, w + 1):
                t = 0.3 + 0.55 * (dy / height) + (0.15 if dx < 0 else 0)
                col = ramp(pal, t)
                if dx == -w:
                    col = shade(col, 1.25)
                if dx == w and w > 0:
                    col = shade(col, 0.75)
                c.set(cx + dx, y, col)
    return c


def astral_bricks(variant='plain'):
    n = value_noise(16, 16, 4, 61, octaves=2)
    c = Canvas(16, 16)
    mortar = hexc('#090b1f')
    for y in range(16):
        for x in range(16):
            row = y // 4
            off = 4 if row % 2 else 0
            bx = (x + off) % 8
            if y % 4 == 3 or bx == 7:
                c.set(x, y, mortar)
                continue
            t = 0.35 + 0.35 * n[y, x]
            if y % 4 == 0:
                t += 0.15
            if bx == 0:
                t += 0.08
            c.set(x, y, ramp(NAVY, t))
    r = rng(62)
    for _ in range(5):
        x, y = r.randrange(16), r.randrange(16)
        if c.get(x, y) != mortar:
            c.set(x, y, lerp(GOLD[3], NAVY[4], 0.3))
    if variant == 'cracked':
        cracks(c, 63, 2, [mortar, mortar, hexc('#05060f'), hexc('#05060f'), mortar], glow=False)
        for _ in range(3):
            x, y = r.randrange(16), r.randrange(16)
            c.set(x, y, VIOLET[2])
    if variant == 'mossy':
        m = value_noise(16, 16, 3, 64, octaves=2)
        for y in range(16):
            for x in range(16):
                if m[y, x] > 0.62:
                    c.set(x, y, ramp(VIOLET[:3], m[y, x]))
    return c


def chiseled_astral_bricks():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            t = 0.25 + 0.1 * min(edge, 3)
            c.set(x, y, ramp(NAVY, t))
    for i in range(16):
        c.set(i, 0, NAVY[4]); c.set(0, i, NAVY[4]); c.set(i, 15, NAVY[0]); c.set(15, i, NAVY[0])
    # ring
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.6 < d < 6.5:
                c.set(x, y, GOLD[1])
    poly = star_points(7.5, 7.5, 5.0, 1.5, 4)
    poly2 = star_points(7.5, 7.5, 3.2, 1.2, 4, rot=math.pi / 4)
    for y in range(16):
        for x in range(16):
            if point_in_poly(x + 0.5, y + 0.5, poly) or point_in_poly(x + 0.5, y + 0.5, poly2):
                d = math.hypot(x - 7.5, y - 7.5)
                c.set(x, y, ramp(GOLD, 1.0 - d / 6.0))
    c.set(7, 7, GOLD[3]); c.set(8, 8, GOLD[3]); c.set(7, 8, hexc('#ffffff')); c.set(8, 7, hexc('#ffffff'))
    return c


def astral_glass():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            c.set(x, y, (20, 24, 70, 90))
    for i in range(16):
        c.set(i, 0, NAVY[4]); c.set(0, i, NAVY[4]); c.set(i, 15, NAVY[2]); c.set(15, i, NAVY[2])
    r = rng(71)
    for _ in range(9):
        x, y = r.randrange(2, 14), r.randrange(2, 14)
        c.set(x, y, (255, 255, 255, 230))
    for (x, y) in ((4, 5), (11, 10)):
        c.set(x, y, GOLD[3]); c.set(x - 1, y, (255, 233, 163, 150)); c.set(x + 1, y, (255, 233, 163, 150))
        c.set(x, y - 1, (255, 233, 163, 150)); c.set(x, y + 1, (255, 233, 163, 150))
    c.line(3, 5, 11, 10, (200, 220, 255, 60))
    return c


def star_lock(active=False):
    c = chiseled_astral_bricks()
    # carve keyhole socket in the middle
    for y in range(4, 12):
        for x in range(4, 12):
            d = math.hypot(x - 7.5, y - 7.5)
            if d < 3.6:
                c.set(x, y, hexc('#05040c') if not active else ramp(CYAN, 1 - d / 4))
    if not active:
        c.set(7, 6, VIOLET[2]); c.set(8, 9, VIOLET[2])
    return c


def altar_top():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            c.set(x, y, ramp(NAVY, 0.25 + 0.1 * ((x + y) % 2)))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 6.2 < d < 7.3 or 3.3 < d < 4.0:
                c.set(x, y, GOLD[2])
    # constellation points and lines
    pts = [(7, 2), (12, 6), (10, 12), (4, 12), (2, 6)]
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 2) % len(pts)]
        c.line(a[0], a[1], b[0], b[1], VIOLET[2])
    for (x, y) in pts:
        c.set(x, y, hexc('#ffffff'))
    c.rect(7, 7, 2, 2, CYAN[3])
    return c


def altar_side():
    c = astral_bricks()
    for x in range(16):
        c.set(x, 0, GOLD[2]); c.set(x, 1, GOLD[1]); c.set(x, 14, GOLD[1]); c.set(x, 15, GOLD[0])
    for (x, y) in ((3, 7), (8, 6), (12, 8)):
        c.set(x, y, CYAN[3]); c.set(x, y + 1, CYAN[2])
    return c


def altar_bottom():
    c = astral_bricks()
    return c


def star_jar():
    """Texture sheet for the star jar model: glass (0-7), lid (8-15 top row), star (bottom right)."""
    c = Canvas(16, 16)
    # glass side 6x8 at (0,0)
    for y in range(8):
        for x in range(6):
            c.set(x, y, (180, 220, 255, 70))
        c.set(0, y, (220, 240, 255, 150)); c.set(5, y, (140, 170, 220, 120))
    for x in range(6):
        c.set(x, 7, (200, 230, 255, 140))
    # lid 6x6 at (8,0) + lid side 6x2 at (8,6)
    for y in range(6):
        for x in range(6):
            c.set(8 + x, y, ramp(GOLD, 0.3 + 0.1 * ((x + y) % 3)))
    for x in range(6):
        c.set(8 + x, 6, GOLD[2]); c.set(8 + x, 7, GOLD[1])
    # star 4x4 at (0,8)
    star = [" w  ", "wYYw", " Yw ", "  w "]
    for y in range(4):
        for x in range(4):
            ch = star[y][x]
            if ch == 'w':
                c.set(x, 8 + y, hexc('#ffffff'))
            elif ch == 'Y':
                c.set(x, 8 + y, GOLD[3])
    c.rect(0, 8, 4, 4, GOLD[3])
    c.set(1, 9, hexc('#ffffff')); c.set(2, 10, hexc('#ffffff')); c.set(1, 10, hexc('#ffffff')); c.set(2, 9, hexc('#ffffff'))
    # glass top 6x6 at (8,8)
    for y in range(6):
        for x in range(6):
            c.set(8 + x, 8 + y, (190, 225, 255, 60))
    return c


def fallen_star():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            c.set(x, y, ramp([hexc('#ffffff'), hexc('#fff3b8'), hexc('#ffd35c'), hexc('#f08a24')], d / 10.0))
    poly = star_points(7.5, 7.5, 7.5, 2.4, 4)
    for y in range(16):
        for x in range(16):
            if point_in_poly(x + 0.5, y + 0.5, poly):
                c.set(x, y, lerp(c.get(x, y), hexc('#ffffff'), 0.6))
    return c


def gravity_rune(active=False):
    c = astral_bricks()
    col = VIOLET if not active else CYAN
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.0 < d < 6.0:
                c.set(x, y, col[2])
    # arrow up rune
    arrow = ["   X   ", "  XXX  ", " X X X ", "   X   ", "   X   ", "  X X  "]
    for y, row in enumerate(arrow):
        for x, ch in enumerate(row):
            if ch == 'X':
                c.set(4 + x, 5 + y, col[3])
    return c


def starfire_vent_top(active=False):
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            c.set(x, y, ramp(ROCK, 0.35 + 0.1 * ((x * 7 + y * 3) % 4) / 3))
    for y in range(3, 13):
        for x in range(3, 13):
            if (x + y) % 3 == 0 or x in (3, 12) or y in (3, 12):
                c.set(x, y, ROCK[3])
            else:
                d = math.hypot(x - 7.5, y - 7.5)
                c.set(x, y, ramp(LAVA, (0.9 if active else 0.55) - d / 10))
    return c


def starfire_vent_side():
    c = rock_base(81)
    for x in range(16):
        c.set(x, 0, ROCK[4]); c.set(x, 1, ROCK[3])
    cracks(c, 82, 1, LAVA)
    return c


def void_stone():
    n = value_noise(16, 16, 4, 91, octaves=3)
    c = Canvas(16, 16)
    V = [hexc('#05030a'), hexc('#0e0719'), hexc('#1a0d2e'), hexc('#2a1548'), hexc('#46236e')]
    for y in range(16):
        for x in range(16):
            c.set(x, y, ramp(V, n[y, x]))
    r = rng(92)
    for _ in range(4):
        c.set(r.randrange(16), r.randrange(16), VIOLET[3])
    return c


def meteorite_bricks():
    c = Canvas(16, 16)
    mortar = ROCK[0]
    n = value_noise(16, 16, 4, 101, octaves=2)
    for y in range(16):
        for x in range(16):
            row = y // 8
            off = 4 if row % 2 else 0
            bx = (x + off) % 8
            if y % 8 == 7 or bx == 7:
                c.set(x, y, mortar)
                continue
            t = 0.35 + 0.4 * n[y, x] + (0.15 if y % 8 == 0 else 0)
            c.set(x, y, ramp(ROCK, t))
    c.set(3, 3, LAVA[2]); c.set(11, 11, LAVA[2]); c.set(12, 11, LAVA[1])
    return c


BLOCKS = {
    'meteorite_rock': meteorite_rock,
    'cooled_meteorite': meteorite_rock_cool,
    'starmetal_ore': starmetal_ore,
    'raw_starmetal_block': raw_starmetal_block,
    'starmetal_block': starmetal_block,
    'skyshard_block': skyshard_block,
    'skyshard_cluster': skyshard_cluster,
    'astral_bricks': astral_bricks,
    'cracked_astral_bricks': lambda: astral_bricks('cracked'),
    'overgrown_astral_bricks': lambda: astral_bricks('mossy'),
    'chiseled_astral_bricks': chiseled_astral_bricks,
    'astral_glass': astral_glass,
    'star_lock': star_lock,
    'star_lock_open': lambda: star_lock(True),
    'astral_altar_top': altar_top,
    'astral_altar_side': altar_side,
    'astral_altar_bottom': altar_bottom,
    'star_jar': star_jar,
    'fallen_star': fallen_star,
    'gravity_rune': gravity_rune,
    'gravity_rune_active': lambda: gravity_rune(True),
    'starfire_vent_top': starfire_vent_top,
    'starfire_vent_top_active': lambda: starfire_vent_top(True),
    'starfire_vent_side': starfire_vent_side,
    'void_stone': void_stone,
    'meteorite_bricks': meteorite_bricks,
}


def main():
    for name, fn in BLOCKS.items():
        fn().save(os.path.join(OUT, name + '.png'))
    print(f'wrote {len(BLOCKS)} block textures')


if __name__ == '__main__':
    main()
