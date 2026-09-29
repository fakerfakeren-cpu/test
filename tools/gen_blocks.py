"""Block textures for Rimeheart (procedural, deterministic)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'rimeheart', 'textures', 'block')

RIMESTONE = [hexc('#34414f'), hexc('#4f6478'), hexc('#6a8196'), hexc('#8aa1b5'), hexc('#b0c4d4')]
STONE = [hexc('#4c4c4c'), hexc('#5f5f5f'), hexc('#707070'), hexc('#7f7f7f'), hexc('#8f8f8f')]
FROSTIRON = [hexc('#2b4054'), hexc('#4a6a86'), hexc('#7fa3bf'), hexc('#b7d3e6'), hexc('#eef7fc')]
RIME = [hexc('#154a66'), hexc('#2f93c2'), hexc('#6fcff0'), hexc('#b8eefc'), hexc('#f4fdff')]
PERMA = [hexc('#3b3f45'), hexc('#555c63'), hexc('#6f7a84'), hexc('#95a8b7'), hexc('#dfeaf1')]
MORTAR = hexc('#1c2733')
WHITE = hexc('#ffffff')


def noise_fill(pal, seed, scale=4, lo=0.0, hi=1.0):
    n = value_noise(16, 16, scale, seed, octaves=3)
    n2 = value_noise(16, 16, 2, seed + 7, octaves=2)
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            v = 0.6 * n[y, x] + 0.4 * n2[y, x]
            c.set(x, y, ramp(pal, lo + (hi - lo) * v))
    return c


def frost_specks(c, seed, count=7, color=None):
    r = rng(seed)
    for _ in range(count):
        x, y = r.randrange(16), r.randrange(16)
        c.set(x, y, color or lerp(c.get(x, y), WHITE, 0.6))
    return c


def ore_specks(c, seed, colors, clusters=5):
    r = rng(seed)
    for _ in range(clusters):
        x, y = r.randrange(1, 14), r.randrange(1, 14)
        shape = r.choice([[(0, 0), (1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (-1, 0), (0, 1)], [(0, 0), (1, 1), (0, 1)], [(0, 0), (1, 0), (1, 1), (2, 1)]])
        for i, (ox, oy) in enumerate(shape):
            c.set(x + ox, y + oy, colors[2] if i else colors[3])
        c.set(x + shape[-1][0] + 1, y + shape[-1][1], colors[1])
        c.set(x, y, colors[4])
    return c


def rimestone():
    return frost_specks(noise_fill(RIMESTONE, 11, lo=0.15, hi=0.95), 12, 8)


def permafrost():
    c = noise_fill(PERMA, 21, scale=3, lo=0.05, hi=0.75)
    m = value_noise(16, 16, 3, 22, octaves=2)
    for y in range(16):
        for x in range(16):
            if m[y, x] > 0.62:
                c.set(x, y, ramp([PERMA[3], PERMA[4], WHITE], (m[y, x] - 0.62) * 2.6))
    return c


def frostiron_ore():
    return ore_specks(noise_fill(STONE, 31, lo=0.2, hi=0.9), 33, FROSTIRON, 6)


def rime_crystal_ore():
    c = noise_fill(STONE, 41, lo=0.2, hi=0.9)
    r = rng(42)
    for _ in range(4):
        x, y = r.randrange(2, 13), r.randrange(2, 13)
        for i in range(r.randrange(3, 5)):
            c.set(x, y - i, RIME[3 if i < 2 else 4])
            c.set(x + 1, y - i, RIME[2])
        c.set(x - 1, y, RIME[1])
    return c


def rime_crystal_cluster():
    rows = [
        "................",
        ".......W........",
        "......WcQ.......",
        "......Wcq.......",
        "..V...ccqQ......",
        ".vpP..ccqQ...W..",
        ".vpP.WccqQ..WcQ.",
        ".vpP.Wccqq..Wcq.",
        "vvpPPWccqq..ccqQ",
        "vppPPcccqqV.ccqQ",
        "vppPPccqqQvpcqqQ",
        ".ppP.ccqqQvpcqQ.",
        ".vpPcccqqQvpPqQ.",
        "..pPcccqqQvpPq..",
        "..ppccqqqQvpP...",
        "...pcqqqQQppP...",
    ]
    leg = {'W': RIME[4], 'c': RIME[3], 'q': RIME[2], 'Q': RIME[1], 'V': WHITE, 'v': hexc('#d8eef8'), 'p': hexc('#9cc4dc'), 'P': hexc('#5f8fb0')}
    return sprite(rows, leg)


def frostiron_block():
    c = Canvas(16, 16)
    n = value_noise(16, 16, 3, 51, octaves=2)
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            t = 0.45 + 0.25 * n[y, x] + (0.15 if y < 8 else 0)
            if edge == 0:
                t = 0.95 if (x == 0 or y == 0) else 0.1
            c.set(x, y, ramp(FROSTIRON, t))
    for x in range(1, 15):
        c.set(x, 7, FROSTIRON[1])
        c.set(x, 8, FROSTIRON[3])
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        c.set(x, y, FROSTIRON[4])
        c.set(x + 1, y + 1, FROSTIRON[0])
    return c


def rime_crystal_block():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            f = ((x + y) // 3 + (x - y) // 4) % 4
            c.set(x, y, RIME[1 + f])
    for i in range(16):
        c.set(i, (i * 5) % 16, RIME[4])
    return frost_specks(c, 61, 6, WHITE)


def bricks(variant='plain'):
    n = value_noise(16, 16, 4, 71, octaves=2)
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            row = y // 4
            off = 4 if row % 2 else 0
            bx = (x + off) % 8
            if y % 4 == 3 or bx == 7:
                c.set(x, y, MORTAR)
                continue
            t = 0.4 + 0.35 * n[y, x] + (0.15 if y % 4 == 0 else 0) + (0.08 if bx == 0 else 0)
            c.set(x, y, ramp(RIMESTONE, t))
    r = rng(72)
    for _ in range(6):
        x, y = r.randrange(16), r.randrange(16)
        if c.get(x, y) != MORTAR:
            c.set(x, y, lerp(c.get(x, y), WHITE, 0.55))
    if variant == 'cracked':
        pts = [(3, 1), (4, 2), (4, 3), (5, 4), (5, 5), (6, 6), (11, 8), (11, 9), (12, 10), (12, 11), (13, 12), (9, 13), (8, 14)]
        for (x, y) in pts:
            c.set(x, y, MORTAR)
    return c


def snowflake(c, cx, cy, radius, colors):
    for k in range(6):
        a = k * math.pi / 3
        for i in range(radius + 1):
            x = int(round(cx + math.cos(a) * i))
            y = int(round(cy + math.sin(a) * i))
            c.set(x, y, colors[-1] if i < 2 else colors[-2])
            if i == radius - 1:
                for s in (-1, 1):
                    b = a + s * math.pi / 4
                    c.set(int(round(x + math.cos(b))), int(round(y + math.sin(b))), colors[-3])
    return c


def chiseled_bricks():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            c.set(x, y, ramp(RIMESTONE, 0.3 + 0.12 * min(edge, 3)))
    for i in range(16):
        c.set(i, 0, RIMESTONE[4]); c.set(0, i, RIMESTONE[4]); c.set(i, 15, RIMESTONE[0]); c.set(15, i, RIMESTONE[0])
    for y in range(16):
        for x in range(16):
            if 5.6 < math.hypot(x - 7.5, y - 7.5) < 6.6:
                c.set(x, y, RIME[1])
    return snowflake(c, 7.5, 7.5, 4, RIME)


def frost_lamp():
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            if d > 6.5:
                c.set(x, y, FROSTIRON[1] if (x + y) % 2 else FROSTIRON[2])
            else:
                c.set(x, y, ramp([RIME[2], RIME[3], RIME[4], WHITE], 1 - d / 7))
    for i in range(1, 15):
        c.set(i, 7, FROSTIRON[3]); c.set(7, i, FROSTIRON[3])
    return snowflake(c, 7.5, 7.5, 3, RIME)


def altar_top():
    c = chiseled_bricks()
    for i in range(16):
        c.set(i, 1, RIME[2]); c.set(i, 14, RIME[2]); c.set(1, i, RIME[2]); c.set(14, i, RIME[2])
    return c


def altar_side():
    c = bricks()
    for x in range(16):
        c.set(x, 0, FROSTIRON[3]); c.set(x, 1, FROSTIRON[2])
    for x in range(2, 14, 3):
        c.set(x, 6, RIME[4]); c.set(x + 1, 6, RIME[3]); c.set(x, 7, RIME[2])
    return c


BLOCKS = {
    'rimestone': rimestone,
    'permafrost': permafrost,
    'frostiron_ore': frostiron_ore,
    'rime_crystal_ore': rime_crystal_ore,
    'rime_crystal_cluster': rime_crystal_cluster,
    'frostiron_block': frostiron_block,
    'rime_crystal_block': rime_crystal_block,
    'rimestone_bricks': bricks,
    'cracked_rimestone_bricks': lambda: bricks('cracked'),
    'chiseled_rimestone_bricks': chiseled_bricks,
    'frost_lamp': frost_lamp,
    'glacial_altar_top': altar_top,
    'glacial_altar_side': altar_side,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in BLOCKS.items():
        fn().save(os.path.join(OUT, name + '.png'))
    print(f'wrote {len(BLOCKS)} block textures')


if __name__ == '__main__':
    main()
