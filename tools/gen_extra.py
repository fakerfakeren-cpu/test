"""Armour layers, wings, particles, compass frames, extra blocks and the mod logo."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

RES = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
T = os.path.join(RES, 'assets', 'rimeheart', 'textures')


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


def particles():
    out = os.path.join(T, 'particle')
    specs = {
        'frost_glint': ('star', (255, 255, 255)),
        'snow_puff': ('orb', (255, 255, 255)),
        'wraith_wisp': ('ember', (255, 255, 255)),
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


def logo():
    W, H = 256, 128
    c = Canvas(W, H)
    rs = rng(5)
    for y in range(H):
        for x in range(W):
            c.set(x, y, lerp(hexc('#07131f'), hexc('#1d4466'), y / H))
    for _ in range(220):
        x, y = rs.randrange(W), rs.randrange(H)
        c.set(x, y, lerp(hexc('#ffffff'), hexc('#9fe6ff'), rs.random()))
    # a large snowflake
    cx, cy = 128, 40
    for k in range(6):
        a = k * math.pi / 3
        for i in range(0, 26):
            x, y = cx + math.cos(a) * i, cy + math.sin(a) * i
            for w_ in (-1, 0, 1):
                c.set(int(x + w_ * math.sin(a)), int(y - w_ * math.cos(a)), ramp([hexc('#ffffff'), hexc('#b8eefc'), hexc('#6fcff0')], i / 26))
            if i in (10, 18):
                for s_ in (-1, 1):
                    b = a + s_ * math.pi / 4
                    for j in range(7):
                        c.set(int(x + math.cos(b) * j), int(y + math.sin(b) * j), hexc('#d8f6ff'))
    font = {
        'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
        'I': ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
        'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
        'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
        'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    }
    text = "RIMEHEART"
    scale = 3
    tw = len(text) * 6 * scale
    x0, y0 = (W - tw) // 2, 84
    for i, ch in enumerate(text):
        for ry, row in enumerate(font[ch]):
            for rx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            px, py = x0 + (i * 6 + rx) * scale + sx, y0 + ry * scale + sy
                            c.set(px, py, ramp([hexc('#ffffff'), hexc('#b8eefc'), hexc('#4fa8d8')], (ry * scale + sy) / (7 * scale)))
    c.save(os.path.join(RES, 'rimeheart_logo.png'))


def main():
    frost = [hexc('#304c64'), hexc('#56809f'), hexc('#86aecb'), hexc('#bcd8ec'), hexc('#f2f9ff')]
    ice = [hexc('#2f93c2'), hexc('#6fcff0'), hexc('#b8eefc'), hexc('#f4fdff')]
    wraith = [hexc('#062224'), hexc('#10474a'), hexc('#23847e'), hexc('#4fc4b4'), hexc('#9ff0e0')]
    for d in ('entity/equipment/humanoid', 'entity/equipment/humanoid_leggings', 'particle'):
        os.makedirs(os.path.join(T, d), exist_ok=True)
    armor_set('frostiron', frost, ice, ice)
    armor_set('wraithweave', wraith, [hexc('#10474a'), hexc('#4fc4b4'), hexc('#9ff0e0')], ice, glowy=True)
    particles()
    logo()
    print('extra textures written')


if __name__ == '__main__':
    main()
