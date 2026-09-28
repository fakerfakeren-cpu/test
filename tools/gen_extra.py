"""Armour layers, wings, particles, compass frames, extra blocks and the mod logo."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa
import gen_blocks as GB  # noqa

RES = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
T = os.path.join(RES, 'assets', 'astralfall', 'textures')


def box_faces(u, v, w, h, d):
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'west': (u, v + d, d, h), 'north': (u + d, v + d, w, h),
            'east': (u + d + w, v + d, d, h), 'south': (u + d + w + d, v + d, w, h)}


def paint(c, rect, fn):
    x, y, w, h = rect
    for yy in range(h):
        for xx in range(w):
            col = fn(xx, yy, w, h)
            if col is not None:
                c.set(x + xx, y + yy, col)


def armor_set(name, base, trim, accent, glowy=False):
    """Humanoid (helmet/chest/boots) and leggings layers in the standard 64x32 biped layout."""
    hum = Canvas(64, 32)
    leg = Canvas(64, 32)
    n = value_noise(64, 32, 3, __import__("zlib").crc32(name.encode()) % 1000, octaves=2)

    def metal(xx, yy, w, h, gx=0, gy=0):
        t = 0.35 + 0.45 * n[(gy + yy) % 32, (gx + xx) % 64]
        col = ramp(base, t)
        if yy == 0 or xx == 0:
            col = shade(col, 1.2)
        if yy == h - 1 or xx == w - 1:
            col = shade(col, 0.7)
        return col

    # helmet (head box 8x8x8 at 0,0)
    for face, r in box_faces(0, 0, 8, 8, 8).items():
        def f(xx, yy, w, h, face=face, r=r):
            if face == 'bottom':
                return None
            col = metal(xx, yy, w, h, r[0], r[1])
            if face == 'north':
                if 3 <= yy <= 4 and 1 <= xx <= 6:
                    return hexc('#0b0a14') if not glowy else accent[1]
                if yy == 0 or (xx == 3 or xx == 4) and yy < 3:
                    return trim[2]
            if face == 'top' and (xx == 3 or xx == 4):
                return trim[1]
            return col
        paint(hum, r, f)
    # chest (body box 8x12x4 at 16,16) + arms (4x12x4 at 40,16)
    for face, r in box_faces(16, 16, 8, 12, 4).items():
        def f(xx, yy, w, h, face=face, r=r):
            col = metal(xx, yy, w, h, r[0], r[1])
            if face in ('north', 'south'):
                if yy in (0, 1):
                    return trim[1]
                if face == 'north' and 3 <= yy <= 6 and 2 <= xx <= 5:
                    d = abs(xx - 3.5) + abs(yy - 4.5)
                    return accent[2] if d < 1.5 else accent[1] if d < 2.6 else col
                if yy == h - 1:
                    return trim[0]
            return col
        paint(hum, r, f)
    for face, r in box_faces(40, 16, 4, 12, 4).items():
        def f(xx, yy, w, h, face=face, r=r):
            if yy > 7 and face not in ('top',):
                return None
            col = metal(xx, yy, w, h, r[0], r[1])
            if yy < 2:
                return trim[1] if yy == 0 else col
            return col
        paint(hum, r, f)
    # boots on leg box (4x12x4 at 0,16): only lower third
    for face, r in box_faces(0, 16, 4, 12, 4).items():
        def f(xx, yy, w, h, face=face, r=r):
            if face in ('top',):
                return None
            if face != 'bottom' and yy < 8:
                return None
            col = metal(xx, yy, w, h, r[0], r[1])
            if yy == 8:
                return trim[1]
            return col
        paint(hum, r, f)
    # leggings layer: waist on body box and full legs
    for face, r in box_faces(16, 16, 8, 12, 4).items():
        def f(xx, yy, w, h, face=face, r=r):
            if face in ('north', 'south', 'east', 'west') and yy < 8:
                return None
            if face == 'top':
                return None
            col = metal(xx, yy, w, h, r[0], r[1])
            if yy == 8:
                return trim[1]
            return col
        paint(leg, r, f)
    for face, r in box_faces(0, 16, 4, 12, 4).items():
        def f(xx, yy, w, h, face=face, r=r):
            if face == 'bottom':
                return None
            col = metal(xx, yy, w, h, r[0], r[1])
            if yy > 9:
                return None
            if face == 'north' and yy == 5:
                return accent[1]
            return col
        paint(leg, r, f)
    hum.save(os.path.join(T, 'entity', 'equipment', 'humanoid', name + '.png'))
    leg.save(os.path.join(T, 'entity', 'equipment', 'humanoid_leggings', name + '.png'))


def crown():
    c = Canvas(64, 32)
    gold = [hexc('#6b4a12'), hexc('#b9862a'), hexc('#f2c14e'), hexc('#ffe9a3')]
    # crown band + spikes drawn on the head box sides (8x8x8 at 0,0), upper rows only
    for face, r in box_faces(0, 0, 8, 8, 8).items():
        if face in ('bottom', 'top'):
            continue
        def f(xx, yy, w, h):
            spike = (xx % 3 == 1)
            if yy >= 3 and yy <= 4:
                return gold[2] if xx % 2 else gold[1]
            if yy < 3 and spike:
                return gold[3] if yy == 0 else gold[2]
            if yy == 4 and xx == w // 2:
                return hexc('#9af3ff')
            return None
        paint(c, r, f)
    c.set(8 + 3, 8 + 3, hexc('#effeff'))
    c.set(8 + 4, 8 + 3, hexc('#9af3ff'))
    c.save(os.path.join(T, 'entity', 'equipment', 'humanoid', 'crown_of_astraeus.png'))


def wings():
    c = Canvas(64, 32)
    neb = [hexc('#12061f'), hexc('#2a1248'), hexc('#5a2394'), hexc('#9150e0'), hexc('#c998ff'), hexc('#f3e4ff')]
    n = value_noise(64, 32, 4, 777, octaves=3)
    r = rng(778)
    # elytra wing box: texOffs(22,0) size 10x20x2
    for face, rect in box_faces(22, 0, 10, 20, 2).items():
        def f(xx, yy, w, h):
            t = 0.2 + 0.7 * n[yy % 32, (xx + rect[0]) % 64] + 0.15 * (1 - yy / max(1, h))
            col = ramp(neb, t)
            if r.random() < 0.04:
                col = hexc('#ffffff')
            edge = xx == 0 or xx == w - 1 or yy == h - 1
            return shade(col, 1.25) if edge else col
        paint(c, rect, f)
    c.save(os.path.join(T, 'entity', 'equipment', 'wings', 'nebula_wings.png'))


def particles():
    out = os.path.join(T, 'particle')
    specs = {
        'star_sparkle': ('star', (255, 255, 255)),
        'gold_sparkle': ('star', (255, 255, 255)),
        'void_mote': ('orb', (255, 255, 255)),
        'comet_trail': ('ember', (255, 255, 255)),
    }
    for name, (shape, col) in specs.items():
        for i in range(4):
            c = Canvas(8, 8)
            size = [3.8, 3.0, 2.2, 1.4][i]
            for y in range(8):
                for x in range(8):
                    dx, dy = x - 3.5, y - 3.5
                    if shape == 'star':
                        d = min(abs(dx), abs(dy)) * 2.2 + max(abs(dx), abs(dy)) * 0.35
                        a = max(0.0, 1 - d / size)
                    elif shape == 'orb':
                        a = max(0.0, 1 - math.hypot(dx, dy) / (size * 0.95))
                    else:
                        a = max(0.0, 1 - math.hypot(dx * 1.2, dy) / size)
                    if a > 0.05:
                        v = int(255 * min(1, a * 1.4))
                        c.set(x, y, (col[0], col[1], col[2], v))
            c.save(os.path.join(out, f'{name}_{i}.png'))


def compass_frames():
    base = [
        "................",
        "......KKKK......",
        "....KKhgghKK....",
        "...KhgZZZZghK...",
        "..KhZZZZZZZZhK..",
        "..KgZZZZZZZZgK..",
        ".KhZZZZZZZZZZhK.",
        ".KgZZZZZZZZZZgK.",
        ".KgZZZZZZZZZZgK.",
        ".KhZZZZZZZZZZhK.",
        "..KgZZZZZZZZgK..",
        "..KhZZZZZZZZhK..",
        "...KhgZZZZghK...",
        "....KKhgghKK....",
        "......KKKK......",
        "................",
    ]
    leg = {'K': hexc('#0b0a14'), 'h': hexc('#b9862a'), 'g': hexc('#f2c14e'), 'Z': hexc('#161b44')}
    star_dots = [(5, 5), (10, 6), (6, 10), (9, 10)]
    for i in range(32):
        c = sprite(base, leg)
        for (x, y) in star_dots:
            c.set(x, y, hexc('#4150a6'))
        ang = i / 32 * math.pi * 2 + math.pi
        cx, cy = 7.5, 7.5
        for t in range(0, 11):
            d = t / 10 * 4.6
            x, y = int(round(cx + math.sin(ang) * d)), int(round(cy - math.cos(ang) * d))
            c.set(x, y, hexc('#9af3ff') if t > 5 else hexc('#effeff'))
        for t in range(0, 6):
            d = t / 5 * 2.5
            x, y = int(round(cx - math.sin(ang) * d)), int(round(cy + math.cos(ang) * d))
            c.set(x, y, hexc('#9150e0'))
        c.set(7, 7, hexc('#ffe9a3'))
        c.set(8, 8, hexc('#ffe9a3'))
        c.save(os.path.join(T, 'item', f'astral_compass_{i:02d}.png'))


def extra_blocks():
    c = GB.astral_bricks()
    r = rng(901)
    for (x, y) in ((3, 5), (4, 5), (5, 5), (11, 9), (12, 9), (10, 1)):
        c.set(x, y, lerp(c.get(x, y), hexc('#3fc6e0'), 0.45))
    c.save(os.path.join(T, 'block', 'sealed_astral_bricks.png'))
    e = GB.starmetal_block()
    for y in range(4, 12):
        for x in range(4, 12):
            d = math.hypot(x - 7.5, y - 7.5)
            if d < 3.8:
                e.set(x, y, ramp([hexc('#9af3ff'), hexc('#3fc6e0'), hexc('#123e5c'), hexc('#0b0a14')], d / 3.8))
            elif d < 4.6:
                e.set(x, y, hexc('#b9862a'))
    e.save(os.path.join(T, 'block', 'telescope_eyepiece.png'))


def logo():
    W, H = 256, 128
    c = Canvas(W, H)
    rs = rng(5)
    for y in range(H):
        for x in range(W):
            t = y / H
            c.set(x, y, lerp(hexc('#070617'), hexc('#1d1040'), t))
    for _ in range(160):
        x, y = rs.randrange(W), rs.randrange(H)
        c.set(x, y, lerp(hexc('#ffffff'), hexc('#9af3ff'), rs.random()))
    # meteor streak
    for i in range(90):
        x = 30 + i * 1.6
        y = 20 + i * 0.55
        for w_ in range(-2, 3):
            a = max(0, 1 - abs(w_) / 3) * (i / 90)
            c.set(int(x), int(y + w_), lerp(c.get(int(x), int(y + w_)), hexc('#ffc56b'), a))
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            d = math.hypot(dx, dy)
            if d < 5:
                c.set(int(30 + 90 * 1.6) + dx, int(20 + 90 * 0.55) + dy, ramp([hexc('#ffffff'), hexc('#ffd35c'), hexc('#ff7a1f')], d / 5))
    # title text "ASTRALFALL" in a 5x7 pixel font, scaled x3
    font = {
        'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
        'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
        'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
        'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
        'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    }
    text = "ASTRALFALL"
    scale = 3
    tw = len(text) * 6 * scale
    x0, y0 = (W - tw) // 2, 72
    for i, ch in enumerate(text):
        for ry, row in enumerate(font[ch]):
            for rx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            px, py = x0 + (i * 6 + rx) * scale + sx, y0 + ry * scale + sy
                            t = (ry * scale + sy) / (7 * scale)
                            c.set(px, py, ramp([hexc('#fff3b8'), hexc('#ffd35c'), hexc('#c998ff')], t))
                            c.set(px + 2, py + 2, c.get(px + 2, py + 2)) if False else None
    c.save(os.path.join(RES, 'astralfall_logo.png'))


def main():
    steel = [hexc('#28324d'), hexc('#46587f'), hexc('#6f86b6'), hexc('#a9c1ea'), hexc('#eef5ff')]
    gold = [hexc('#6b4a12'), hexc('#b9862a'), hexc('#f2c14e'), hexc('#ffe9a3')]
    violet = [hexc('#12061f'), hexc('#2a0f4a'), hexc('#5a2394'), hexc('#9150e0'), hexc('#c998ff')]
    cyan = [hexc('#1f7ea3'), hexc('#3fc6e0'), hexc('#9af3ff'), hexc('#effeff')]
    armor_set('starmetal', steel, gold, cyan)
    armor_set('voidwalker', violet, [hexc('#123e5c'), hexc('#3fc6e0'), hexc('#9af3ff')], cyan, glowy=True)
    crown()
    wings()
    particles()
    compass_frames()
    extra_blocks()
    logo()
    print('extra textures written')


if __name__ == '__main__':
    main()
