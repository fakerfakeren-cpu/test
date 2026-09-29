"""Pixel-art painting library for Oathbound.

Images are float RGBA numpy arrays (0..1). Shapes are rasterised at pixel centres, then shaded with
palette ramps, ordered dithering and a bevel light pass (light from the upper left) so sprites read as
hand-shaded pixel art rather than flat fills.
"""
import math
import os

import numpy as np
from PIL import Image

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)] + [a])


def mix(c1, c2, t):
    return np.asarray(c1) * (1 - t) + np.asarray(c2) * t


class Ramp:
    """An ordered list of colours from darkest to lightest."""

    def __init__(self, *hexes):
        self.cols = [hexrgb(h) for h in hexes]

    def __len__(self):
        return len(self.cols)

    def at(self, t, dither=0.0):
        t = min(0.9999, max(0.0, t + dither))
        i = int(t * len(self.cols))
        return self.cols[i].copy()

    def smooth(self, t):
        t = min(1.0, max(0.0, t)) * (len(self.cols) - 1)
        i = int(t)
        if i >= len(self.cols) - 1:
            return self.cols[-1].copy()
        return mix(self.cols[i], self.cols[i + 1], t - i)


class Img:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4))

    # ------------------------------------------------------------------ basics
    def copy(self):
        o = Img(self.w, self.h)
        o.px = self.px.copy()
        return o

    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, c, a=None):
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return
        c = np.asarray(c, dtype=float)
        if len(c) == 3:
            c = np.append(c, 1.0)
        if a is not None:
            c = c.copy()
            c[3] = a
        if c[3] >= 0.999:
            self.px[y, x] = c
        elif c[3] > 0:
            base = self.px[y, x]
            out_a = c[3] + base[3] * (1 - c[3])
            if out_a > 0:
                rgb = (c[:3] * c[3] + base[:3] * base[3] * (1 - c[3])) / out_a
                self.px[y, x] = np.append(rgb, out_a)

    def get(self, x, y):
        return self.px[int(y) % self.h, int(x) % self.w]

    def alpha(self, x, y):
        if not self.inside(x, y):
            return 0.0
        return self.px[int(y), int(x), 3]

    def fill(self, c):
        self.px[:, :] = np.asarray(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def blit(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                c = other.px[y, x]
                if c[3] > 0:
                    self.put(ox + x, oy + y, c)

    def save(self, path, scale=1):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        arr = (np.clip(self.px, 0, 1) * 255 + 0.5).astype(np.uint8)
        im = Image.fromarray(arr, 'RGBA')
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        im.save(path, optimize=True)

    # ------------------------------------------------------------------ masks & shapes
    def mask(self):
        return self.px[:, :, 3] > 0.01

    def line(self, x0, y0, x1, y1, c, width=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            if width <= 1:
                self.put(round(x), round(y), c)
            else:
                r = width / 2
                for dy in range(-int(r) - 1, int(r) + 2):
                    for dx in range(-int(r) - 1, int(r) + 2):
                        if dx * dx + dy * dy <= r * r:
                            self.put(round(x + dx), round(y + dy), c)

    def poly(self, pts, c):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys)) - 1), min(self.h, int(max(ys)) + 2)):
            for x in range(max(0, int(min(xs)) - 1), min(self.w, int(max(xs)) + 2)):
                if point_in_poly(x + 0.5, y + 0.5, pts):
                    self.put(x, y, c)

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    self.put(x, y, c)

    def ring(self, cx, cy, r0, r1, c):
        for y in range(int(cy - r1 - 1), int(cy + r1 + 2)):
            for x in range(int(cx - r1 - 1), int(cx + r1 + 2)):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if r0 <= d <= r1:
                    self.put(x, y, c)

    # ------------------------------------------------------------------ shading passes
    def shade_by(self, ramp, field, dither=0.12, mask=None):
        """Recolours masked pixels from a 0..1 field (array or function(x, y)) through a ramp with dithering."""
        m = self.mask() if mask is None else mask
        for y in range(self.h):
            for x in range(self.w):
                if not m[y, x]:
                    continue
                t = field(x, y) if callable(field) else field[y, x]
                a = self.px[y, x, 3]
                c = ramp.at(t, BAYER4[y % 4, x % 4] * dither)
                c[3] = a
                self.px[y, x] = c

    def bevel(self, light=1.25, dark=0.62, depth=1):
        """Classic pixel-art lighting: brighten edges facing up-left, darken edges facing down-right."""
        src = self.px.copy()
        a = src[:, :, 3] > 0.01
        for y in range(self.h):
            for x in range(self.w):
                if not a[y, x]:
                    continue
                up = y - depth < 0 or not a[y - depth, x]
                left = x - depth < 0 or not a[y, x - depth]
                down = y + depth >= self.h or not a[y + depth, x]
                right = x + depth >= self.w or not a[y, x + depth]
                c = src[y, x].copy()
                if up or left:
                    c[:3] = np.clip(c[:3] * light + (light - 1) * 0.15, 0, 1)
                if down or right:
                    c[:3] = c[:3] * dark
                self.px[y, x] = c

    def outline(self, c, diagonal=False):
        """1px outline around opaque pixels (drawn outside the shape)."""
        src = self.px[:, :, 3] > 0.01
        col = np.asarray(c)
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (-1, -1), (1, -1), (-1, 1)] if diagonal else [])
        for y in range(self.h):
            for x in range(self.w):
                if src[y, x]:
                    continue
                for dx, dy in nb:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny, nx]:
                        self.px[y, x] = col
                        break

    def inner_outline(self, factor=0.55):
        """Darkens the outermost ring of opaque pixels (a self-outline that keeps the silhouette size)."""
        src = self.px[:, :, 3] > 0.01
        for y in range(self.h):
            for x in range(self.w):
                if not src[y, x]:
                    continue
                edge = False
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.w and 0 <= ny < self.h) or not src[ny, nx]:
                        edge = True
                        break
                if edge:
                    self.px[y, x, :3] *= factor

    def glow(self, color, radius=2.0, strength=0.6):
        """Soft additive halo around opaque pixels (for magical items)."""
        src = self.px[:, :, 3] > 0.01
        col = np.asarray(color)[:3]
        out = self.px.copy()
        r = int(math.ceil(radius))
        for y in range(self.h):
            for x in range(self.w):
                if src[y, x]:
                    continue
                best = 0.0
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src[ny, nx]:
                            d = math.hypot(dx, dy)
                            if d <= radius:
                                best = max(best, 1 - d / (radius + 0.5))
                if best > 0:
                    a = best * strength
                    out[y, x] = np.append(col, a)
        self.px = out


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def noise(w, h, cell, seed, octaves=3, persistence=0.5):
    """Tileable fractal value noise in 0..1 (cosine-interpolated lattice)."""
    rng = np.random.default_rng(seed)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    c = cell
    for _ in range(octaves):
        gw, gh = max(1, round(w / c)), max(1, round(h / c))
        lat = rng.random((gh, gw))
        ys = (np.arange(h) / h) * gh
        xs = (np.arange(w) / w) * gw
        y0 = np.floor(ys).astype(int)
        x0 = np.floor(xs).astype(int)
        ty = (1 - np.cos((ys - y0) * math.pi)) / 2
        tx = (1 - np.cos((xs - x0) * math.pi)) / 2
        a = lat[np.ix_(y0 % gh, x0 % gw)]
        b = lat[np.ix_(y0 % gh, (x0 + 1) % gw)]
        cc = lat[np.ix_((y0 + 1) % gh, x0 % gw)]
        d = lat[np.ix_((y0 + 1) % gh, (x0 + 1) % gw)]
        top = a * (1 - tx) + b * tx
        bot = cc * (1 - tx) + d * tx
        total += amp * (top * (1 - ty[:, None]) + bot * ty[:, None])
        norm += amp
        amp *= persistence
        c = max(1, c / 2)
    return total / norm


def rng(seed):
    return np.random.default_rng(seed)
