"""Tiny pixel-art toolkit used to generate every Astralfall texture.

Everything is deterministic (seeded), so re-running the generators produces
byte-identical PNGs.
"""
import math
import random

import numpy as np
from PIL import Image


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))


def shade(c, f):
    """f > 1 brightens, f < 1 darkens."""
    if f >= 1:
        return tuple([int(min(255, c[i] + (255 - c[i]) * (f - 1))) for i in range(3)] + [c[3]])
    return tuple([int(c[i] * f) for i in range(3)] + [c[3]])


def ramp(colors, t):
    """Sample a multi-stop colour ramp at t in [0,1]."""
    t = max(0.0, min(0.9999, t))
    seg = t * (len(colors) - 1)
    i = int(seg)
    return lerp(colors[i], colors[i + 1], seg - i)


class Canvas:
    def __init__(self, w, h, fill=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), dtype=np.uint8)
        self.px[:, :] = fill

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            if len(c) == 4 and c[3] < 255 and c[3] > 0:
                base = self.px[y, x].astype(float)
                a = c[3] / 255.0
                out = [base[i] * (1 - a) + c[i] * a for i in range(3)]
                self.px[y, x] = (int(out[0]), int(out[1]), int(out[2]), max(int(base[3]), c[3]))
            else:
                self.px[y, x] = c

    def get(self, x, y):
        return tuple(int(v) for v in self.px[y % self.h, x % self.w])

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def fill_fn(self, x, y, w, h, fn):
        for yy in range(h):
            for xx in range(w):
                self.set(x + xx, y + yy, fn(xx, yy))

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def blit(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                c = tuple(int(v) for v in other.px[y, x])
                if c[3] > 0:
                    self.set(ox + x, oy + y, c)

    def outline(self, color, only_empty=True):
        """Draw a 1px outline around opaque pixels."""
        src = self.px.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src[y, x, 3] != 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny, nx, 3] > 0:
                        self.px[y, x] = color
                        break

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.fromarray(self.px, 'RGBA').save(path, optimize=True)


def value_noise(w, h, scale, seed, octaves=3, tile=True):
    """Tileable value noise in [0,1]."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp_total = 0
    amp = 1.0
    freq = scale
    for _ in range(octaves):
        gw, gh = max(1, int(w / freq)), max(1, int(h / freq))
        grid = rng.random((gh, gw))
        for y in range(h):
            for x in range(w):
                fx, fy = x / freq, y / freq
                x0, y0 = int(math.floor(fx)), int(math.floor(fy))
                tx, ty = fx - x0, fy - y0
                tx = tx * tx * (3 - 2 * tx)
                ty = ty * ty * (3 - 2 * ty)
                a = grid[y0 % gh, x0 % gw]
                b = grid[y0 % gh, (x0 + 1) % gw]
                c = grid[(y0 + 1) % gh, x0 % gw]
                d = grid[(y0 + 1) % gh, (x0 + 1) % gw]
                out[y, x] += amp * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        amp_total += amp
        amp *= 0.5
        freq = max(1, freq / 2)
    return out / amp_total


def sprite(rows, legend):
    """Build a canvas from ASCII art. '.' and ' ' are transparent."""
    h = len(rows)
    w = max(len(r) for r in rows)
    c = Canvas(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in '. ':
                continue
            col = legend.get(ch)
            if col is None:
                raise KeyError(f"no colour for '{ch}' in row {y}: {row}")
            c.set(x, y, col)
    return c


def star_points(cx, cy, r_out, r_in, n=4, rot=0.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + math.pi * i / n
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return pts


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def rng(seed):
    return random.Random(seed)
