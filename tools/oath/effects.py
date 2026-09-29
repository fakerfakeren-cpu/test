"""Spell-effect and particle textures.

Effect textures are smooth, high-resolution intensity maps drawn with anti-aliased distance fields and a
bloom pass. They are white on transparent black with alpha equal to brightness, so they work under both
additive and alpha blending and take their colour from the vertex tint. Particle sprites are small
greyscale frames tinted by the particle's colour.

Run from the repository root:  python3 -m tools.oath.effects
"""
import json
import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')


class Field:
    """An intensity canvas in unit coordinates (-1..1 across) with anti-aliased primitives."""

    def __init__(self, n):
        self.n = n
        c = (np.arange(n) + 0.5) / n * 2 - 1
        self.x, self.y = np.meshgrid(c, c)
        self.r = np.hypot(self.x, self.y)
        self.a = np.arctan2(self.y, self.x)
        self.v = np.zeros((n, n))
        self.px = 2.0 / n

    def _ink(self, dist, width, strength=1.0):
        aa = self.px * 0.9
        ink = np.clip((width / 2 - dist) / aa + 0.5, 0, 1) * strength
        self.v = np.maximum(self.v, ink)

    def ring(self, radius, width, strength=1.0, gaps=None):
        d = np.abs(self.r - radius)
        if gaps is not None:
            n, frac, phase = gaps
            seg = ((self.a + math.pi + phase) / (2 * math.pi) * n) % 1.0
            d = np.where(seg < frac, 9.0, d)
        self._ink(d, width, strength)

    def segment(self, x0, y0, x1, y1, width, strength=1.0):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((self.x - x0) * dx + (self.y - y0) * dy) / L2, 0, 1)
        d = np.hypot(self.x - (x0 + t * dx), self.y - (y0 + t * dy))
        self._ink(d, width, strength)

    def polygon(self, pts, width, strength=1.0):
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            self.segment(a[0], a[1], b[0], b[1], width, strength)

    def dot(self, x, y, radius, strength=1.0):
        d = np.hypot(self.x - x, self.y - y)
        self._ink(d, radius * 2, strength)

    def arc(self, radius, a0, a1, width, strength=1.0):
        ang = (self.a - a0) % (2 * math.pi)
        span = (a1 - a0) % (2 * math.pi)
        d = np.where(ang <= span, np.abs(self.r - radius), 9.0)
        self._ink(d, width, strength)

    def bloom(self, radius_px, strength):
        return np.clip(self.v + blur(self.v, radius_px) * strength, 0, 1)


def blur(a, sigma):
    """Gaussian blur through the FFT (wraps, which is harmless for centred designs)."""
    n0, n1 = a.shape
    fy = np.fft.fftfreq(n0)[:, None]
    fx = np.fft.fftfreq(n1)[None, :]
    g = np.exp(-2 * (math.pi ** 2) * (sigma ** 2) * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def save_intensity(v, path, tint=(1.0, 1.0, 1.0)):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    v = np.clip(v, 0, 1)
    rgb = np.stack([v * tint[0], v * tint[1], v * tint[2]], -1)
    arr = np.concatenate([rgb, v[..., None]], -1)
    Image.fromarray((arr * 255 + 0.5).astype(np.uint8), 'RGBA').save(path, optimize=True)


# ------------------------------------------------------------------ rune alphabet
# Each rune is a handful of strokes in a unit cell (x across, y along the radius, both -1..1).
RUNES = [
    [(-0.6, -1, -0.6, 1), (-0.6, 0, 0.6, -0.8)],
    [(0, -1, 0, 1), (-0.6, -0.4, 0.6, 0.4)],
    [(-0.6, -1, 0, 1), (0, 1, 0.6, -1)],
    [(0, -1, 0, 1), (-0.6, 1, 0, 0.3), (0.6, 1, 0, 0.3)],
    [(-0.6, -1, -0.6, 1), (0.6, -1, 0.6, 1), (-0.6, 0, 0.6, 0)],
    [(-0.6, -1, 0.6, 1), (0.6, -1, -0.6, 1)],
    [(0, -1, 0, 1), (0, -1, 0.6, -0.5), (0, 0, 0.6, -0.5)],
    [(-0.6, 1, 0, -1), (0, -1, 0.6, 1), (-0.3, 0.2, 0.3, 0.2)],
    [(0, -1, 0, 0.2), (-0.6, 1, 0, 0.2), (0.6, 1, 0, 0.2)],
    [(-0.6, -1, 0.6, -1), (0, -1, 0, 1), (-0.6, 1, 0.6, 1)],
]


def rune_band(f, radius, height, count, seed, width):
    rng = np.random.default_rng(seed)
    for i in range(count):
        ang = (i + 0.5) / count * 2 * math.pi
        rune = RUNES[rng.integers(len(RUNES))]
        # local frame: t along the circle, n outward
        tx, ty = -math.sin(ang), math.cos(ang)
        nx, ny = math.cos(ang), math.sin(ang)
        cx, cy = nx * radius, ny * radius
        s = height / 2
        for (x0, y0, x1, y1) in rune:
            ax = cx + tx * x0 * s * 0.8 + nx * y0 * s
            ay = cy + ty * x0 * s * 0.8 + ny * y0 * s
            bx = cx + tx * x1 * s * 0.8 + nx * y1 * s
            by = cy + ty * x1 * s * 0.8 + ny * y1 * s
            f.segment(ax, ay, bx, by, width)


def star(points, radius, step, rot=0.0):
    pts = [(math.cos(rot + i * 2 * math.pi / points) * radius, math.sin(rot + i * 2 * math.pi / points) * radius) for i in range(points)]
    return [(pts[i], pts[(i + step) % points]) for i in range(points)]


# ------------------------------------------------------------------ the four sigils
def sigil_oath(n):
    """The Lanternguard's oath-circle: a double ring of runes around a hexagram and a lantern-flame at the heart."""
    f = Field(n)
    lw = 2.2 * f.px
    f.ring(0.96, lw * 1.4)
    f.ring(0.9, lw * 0.8)
    rune_band(f, 0.8, 0.13, 14, 7, lw * 0.85)
    f.ring(0.69, lw)
    for a, b in star(6, 0.66, 2, rot=math.pi / 2):
        f.segment(a[0], a[1], b[0], b[1], lw)
    f.ring(0.33, lw * 0.9)
    f.ring(0.26, lw * 0.6, gaps=(12, 0.4, 0.0))
    # a lantern-flame
    f.polygon([(0, -0.18), (0.08, 0.02), (0.05, 0.12), (0, 0.16), (-0.05, 0.12), (-0.08, 0.02)], lw * 0.9)
    f.dot(0, 0.04, 0.035)
    for i in range(6):
        a = math.pi / 2 + i * math.pi / 3
        f.dot(math.cos(a) * 0.66, math.sin(a) * 0.66, 0.03)
    return f.bloom(n * 0.012, 0.9)


def sigil_dawn(n):
    """A sunwheel: sixteen rays, a ring of beads and a watching eye."""
    f = Field(n)
    lw = 2.2 * f.px
    f.ring(0.95, lw)
    for i in range(16):
        a = i * 2 * math.pi / 16
        r0, r1 = 0.62, 0.9 if i % 2 == 0 else 0.8
        w = 0.07 if i % 2 == 0 else 0.045
        p0 = (math.cos(a - w) * r0, math.sin(a - w) * r0)
        p1 = (math.cos(a) * r1, math.sin(a) * r1)
        p2 = (math.cos(a + w) * r0, math.sin(a + w) * r0)
        f.polygon([p0, p1, p2], lw * 0.8)
    f.ring(0.58, lw * 1.3)
    for i in range(24):
        a = i * 2 * math.pi / 24
        f.dot(math.cos(a) * 0.5, math.sin(a) * 0.5, 0.017)
    f.ring(0.4, lw)
    # eye
    ex = np.linspace(-0.3, 0.3, 40)
    for sgn in (1, -1):
        for i in range(len(ex) - 1):
            y0 = sgn * 0.14 * (1 - (ex[i] / 0.3) ** 2)
            y1 = sgn * 0.14 * (1 - (ex[i + 1] / 0.3) ** 2)
            f.segment(ex[i], y0, ex[i + 1], y1, lw)
    f.ring(0.08, lw)
    f.dot(0, 0, 0.035)
    return f.bloom(n * 0.012, 0.9)


def sigil_arcane(n):
    """The Spire's lattice: three rings, two interlaced squares, orbiting nodes and a spiral of runes."""
    f = Field(n)
    lw = 2.0 * f.px
    f.ring(0.97, lw)
    f.ring(0.93, lw * 0.6, gaps=(48, 0.5, 0.0))
    rune_band(f, 0.84, 0.1, 18, 21, lw * 0.75)
    f.ring(0.75, lw)
    for rot in (0.0, math.pi / 4):
        pts = [(math.cos(rot + i * math.pi / 2) * 0.74, math.sin(rot + i * math.pi / 2) * 0.74) for i in range(4)]
        f.polygon(pts, lw)
    for i in range(8):
        a = i * math.pi / 4
        cx, cy = math.cos(a) * 0.74, math.sin(a) * 0.74
        d = np.abs(np.hypot(f.x - cx, f.y - cy) - 0.06)
        f._ink(d, lw * 0.8)
    f.ring(0.42, lw)
    for a, b in star(5, 0.4, 2, rot=-math.pi / 2):
        f.segment(a[0], a[1], b[0], b[1], lw * 0.9)
    f.ring(0.12, lw)
    f.dot(0, 0, 0.04)
    return f.bloom(n * 0.012, 0.9)


def sigil_veil(n):
    """The Gloaming's mark: a broken ring, three hooked arms spiralling in, and a scatter of motes."""
    f = Field(n)
    lw = 2.4 * f.px
    f.ring(0.94, lw * 1.2, gaps=(7, 0.18, 0.4))
    f.ring(0.86, lw * 0.6, gaps=(13, 0.35, 0.0))
    for k in range(3):
        base = k * 2 * math.pi / 3
        prev = None
        for i in range(60):
            t = i / 59
            r = 0.82 - t * 0.62
            a = base + t * 2.4
            p = (math.cos(a) * r, math.sin(a) * r)
            if prev:
                f.segment(prev[0], prev[1], p[0], p[1], lw * (1.3 - t * 0.6))
            prev = p
        f.dot(prev[0], prev[1], 0.03)
    f.ring(0.2, lw)
    rng = np.random.default_rng(3)
    for i in range(22):
        a = rng.random() * 2 * math.pi
        r = 0.3 + rng.random() * 0.55
        f.dot(math.cos(a) * r, math.sin(a) * r, 0.008 + rng.random() * 0.012, 0.8)
    return f.bloom(n * 0.014, 1.0)


# ------------------------------------------------------------------ strips and glows
def ring_strip(w, h):
    u = (np.arange(w) + 0.5) / w
    v = (np.arange(h) + 0.5) / h
    U, V = np.meshgrid(u, v)
    rng = np.random.default_rng(5)
    wob = np.zeros_like(U)
    for k in range(1, 6):
        wob += rng.random() * np.cos(2 * math.pi * k * 4 * U + rng.random() * 6.28) / k
    wob = (wob - wob.min()) / (wob.max() - wob.min())
    edge = np.exp(-((V - 0.8) / 0.07) ** 2)
    trail = 0.4 * np.exp(-((V - 0.55) / 0.2) ** 2) * (0.7 + 0.3 * wob)
    return np.clip(edge + trail, 0, 1)


def pillar_strip(w, h):
    u = (np.arange(w) + 0.5) / w
    v = (np.arange(h) + 0.5) / h
    U, V = np.meshgrid(u, v)
    rng = np.random.default_rng(9)
    streak = np.zeros_like(U)
    for k in range(1, 7):
        streak += rng.random() * np.cos(2 * math.pi * k * U + rng.random() * 6.28) / k
    streak = (streak - streak.min()) / (streak.max() - streak.min())
    fall = V ** 1.4                                        # v=0 at the top, 1 at the base
    base = np.exp(-((1 - V) / 0.08) ** 2)
    return np.clip((0.35 + 0.65 * streak) * fall + base * 0.6, 0, 1)


def beam_strip(w, h):
    u = (np.arange(w) + 0.5) / w
    v = (np.arange(h) + 0.5) / h
    U, V = np.meshgrid(u, v)
    rng = np.random.default_rng(13)
    flick = np.zeros_like(U)
    for k in range(1, 9):
        flick += rng.random() * np.cos(2 * math.pi * k * 3 * U + rng.random() * 6.28) / k
    flick = (flick - flick.min()) / (flick.max() - flick.min())
    core = np.exp(-((V - 0.5) / 0.1) ** 2)
    glow = 0.45 * np.exp(-((V - 0.5) / 0.28) ** 2) * (0.6 + 0.4 * flick)
    return np.clip(core + glow, 0, 1)


def glow_disc(n):
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, c)
    r = np.hypot(X, Y)
    return np.clip(np.exp(-(r / 0.42) ** 2) * 0.85 + np.exp(-(r / 0.1) ** 2) * 0.5, 0, 1) * (r < 1)


# ------------------------------------------------------------------ particle sprites
def sprite_frames(kind, frames=4, n=16):
    out = []
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, c)
    R = np.hypot(X, Y)
    A = np.arctan2(Y, X)
    for i in range(frames):
        k = i / max(1, frames - 1)
        if kind == 'ember':
            v = np.exp(-(R / (0.55 - 0.25 * k)) ** 2) + 0.6 * np.exp(-(R / 0.14) ** 2)
        elif kind == 'lumen_mote':
            cross = np.exp(-(np.abs(X) / 0.07) ** 2) * np.exp(-(np.abs(Y) / (0.9 - 0.3 * k)) ** 2) \
                + np.exp(-(np.abs(Y) / 0.07) ** 2) * np.exp(-(np.abs(X) / (0.9 - 0.3 * k)) ** 2)
            v = np.exp(-(R / 0.3) ** 2) + cross * 0.7
        elif kind == 'gloam_wisp':
            wob = 0.55 + 0.18 * np.sin(A * 3 + i * 1.7) + 0.1 * np.sin(A * 5 - i)
            v = np.clip(1 - R / (wob * (1 - 0.2 * k)), 0, 1) ** 1.5
        elif kind == 'arcane_glyph':
            f = Field(n * 4)
            rune = RUNES[(i * 3 + 1) % len(RUNES)]
            for (x0, y0, x1, y1) in rune:
                f.segment(x0 * 0.55, -y0 * 0.7, x1 * 0.55, -y1 * 0.7, 0.16)
            big = f.bloom(3, 0.6)
            v = big.reshape(n, 4, n, 4).mean(axis=(1, 3))
        elif kind == 'spirit':
            v = np.exp(-((R - (0.35 + 0.25 * k)) / 0.14) ** 2) + 0.5 * np.exp(-(R / 0.18) ** 2)
        elif kind == 'sunburst':
            spikes = np.abs(np.cos(A * 2)) ** 18
            v = np.exp(-(R / 0.18) ** 2) + spikes * np.exp(-(R / (0.95 - 0.35 * k)) ** 2) * 0.9
        elif kind == 'tide':
            v = np.exp(-((R - 0.5) / 0.1) ** 2) * 0.8 + np.exp(-((X + 0.2) ** 2 + (Y + 0.2) ** 2) / 0.02) * 0.7
            v *= (1 - 0.3 * k)
        else:
            v = np.exp(-(R / 0.5) ** 2)
        out.append(np.clip(v, 0, 1) * (R < 1.05))
    return out


PARTICLES = ['ember', 'lumen_mote', 'gloam_wisp', 'arcane_glyph', 'spirit', 'sunburst', 'tide']


def generate():
    fx = os.path.join(ASSETS, 'textures/effect')
    N = 256
    for i, fn in enumerate((sigil_oath, sigil_dawn, sigil_arcane, sigil_veil)):
        save_intensity(fn(N), os.path.join(fx, f'sigil_{i}.png'))
    save_intensity(ring_strip(256, 64), os.path.join(fx, 'ring.png'))
    save_intensity(pillar_strip(64, 256), os.path.join(fx, 'pillar.png'))
    save_intensity(beam_strip(256, 32), os.path.join(fx, 'beam.png'))
    save_intensity(glow_disc(64), os.path.join(fx, 'glow.png'))
    for kind in PARTICLES:
        names = []
        for i, v in enumerate(sprite_frames(kind)):
            save_intensity(v, os.path.join(ASSETS, 'textures/particle', f'{kind}_{i}.png'))
            names.append(f'oathbound:{kind}_{i}')
        os.makedirs(os.path.join(ASSETS, 'particles'), exist_ok=True)
        with open(os.path.join(ASSETS, 'particles', kind + '.json'), 'w') as f:
            json.dump({'textures': names}, f, indent=2)
    print('effects written')


if __name__ == '__main__':
    generate()
