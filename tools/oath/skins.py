"""Entity skin painters.

A skin paints one face of one cube. Each skin gets the face name, its size, pixel position within the face
and a stable random source, and returns (colour, glow) where glow is None or an emissive colour. Face names
follow the Minecraft box layout: top, bottom, right, front, left, back.
"""
import math

import numpy as np

from .paint import Ramp, hexrgb, BAYER4, noise

FACE_LIGHT = {'top': 1.12, 'bottom': 0.62, 'front': 1.0, 'back': 0.86, 'left': 0.9, 'right': 0.9}
SIDES = ('front', 'back', 'left', 'right')


def _n(seed, w=32, h=32, cell=4):
    return noise(w, h, cell, seed, octaves=2)


class Skin:
    """Base skin: a ramp driven by value noise, with face-based light and darker borders."""

    def __init__(self, ramp, glow=None, grain=4, contrast=1.0, border=0.78, alpha=1.0):
        self.ramp = ramp
        self.glow_col = glow
        self.grain = grain
        self.contrast = contrast
        self.border = border
        self.alpha = alpha

    def base(self, face, x, y, w, h, n, r):
        t = 0.5 + (n - 0.5) * self.contrast
        return t

    def paint(self, face, x, y, w, h, seed, r):
        field = self.field(seed)
        n = field[(y * 3 + seed) % field.shape[0], (x * 3 + seed * 7) % field.shape[1]]
        t = self.base(face, x, y, w, h, n, r)
        t = t * FACE_LIGHT[face] + (0.08 if face == 'top' else 0.0)
        if face in SIDES and h > 3:
            t -= (y / (h - 1)) * 0.10          # a little occlusion toward the bottom of every side
        t += BAYER4[y % 4, x % 4] * 0.12
        c = self.ramp.smooth(t)
        if self.border and w > 2 and h > 2:
            if y == 0 and face in SIDES:
                c[:3] = np.clip(c[:3] * 1.12 + 0.02, 0, 1)   # top edges catch the light
            elif x == 0 or x == w - 1 or y == h - 1 or y == 0:
                c[:3] *= self.border
        c[3] = self.alpha
        return c, self.emit(face, x, y, w, h, t, r)

    def emit(self, face, x, y, w, h, t, r):
        return None

    _cache = {}

    def field(self, seed):
        key = (id(self), seed)
        if key not in Skin._cache:
            Skin._cache[key] = _n(seed % 9973, 48, 48, self.grain)
        return Skin._cache[key]


class Plate(Skin):
    """Armour plate: horizontal plate seams, rivets and a highlight ridge; optional glowing corruption veins."""

    def __init__(self, ramp, seam=5, rivets=True, veins=None, **kw):
        super().__init__(ramp, **kw)
        self.seam = seam
        self.rivets = rivets
        self.veins = veins

    def base(self, face, x, y, w, h, n, r):
        t = 0.45 + (n - 0.5) * 0.35
        if h > 6 and self.seam and y % self.seam == 0:
            t -= 0.25
        if h > 6 and self.seam and y % self.seam == 1:
            t += 0.18
        if self.rivets and self.seam and h > 6 and y % self.seam == 2 and x in (1, w - 2):
            t += 0.35
        return t

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        if self.veins is not None and face != 'top':
            key = ('veins', seed)
            if key not in Skin._cache:
                Skin._cache[key] = noise(48, 48, 7, seed % 7919 + 3, octaves=2)
            f = Skin._cache[key]
            n = f[(y * 2 + seed * 3) % 48, (x * 2 + seed * 5 + FACE_SHIFT[face]) % 48]
            if abs(n - 0.5) < 0.028:
                c = c.copy()
                c[:3] = c[:3] * 0.35 + np.asarray(self.veins)[:3] * 0.65
                g = self.veins
        return c, g


FACE_SHIFT = {'top': 0, 'bottom': 11, 'right': 23, 'front': 5, 'left': 31, 'back': 17}


class Cloth(Skin):
    """Hanging cloth: vertical folds, frayed/torn bottom edge (transparent), optional trim."""

    def __init__(self, ramp, trim=None, tatter=0.0, hem_glow=None, **kw):
        super().__init__(ramp, **kw)
        self.trim = trim
        self.tatter = tatter
        self.hem_glow = hem_glow

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        if self.trim is not None and (y == h - 2 or (face in ('front', 'back') and (x == 0 or x == w - 1))) and h > 4:
            c = self.trim.copy()
        if self.tatter and h > 4 and y >= h - 3:
            depth = (h - y) / 3.0
            if r.random() < self.tatter * (1.2 - depth):
                c = c.copy()
                c[3] = 0.0
        if self.hem_glow is not None and y == h - 1 and c[3] > 0 and x % 2 == 0:
            g = self.hem_glow
        return c, g

    def base(self, face, x, y, w, h, n, r):
        fold = 0.5 + 0.22 * math.sin(x * 1.9 + (n - 0.5) * 2)
        return fold + (n - 0.5) * 0.3 - (y / max(1, h)) * 0.12


class Hide(Skin):
    """Fur or hide: streaky noise along the body."""

    def base(self, face, x, y, w, h, n, r):
        streak = 0.5 + 0.25 * math.sin((x + y * 0.3) * 1.3 + n * 4)
        return streak * 0.6 + n * 0.4


class Bone(Skin):
    """Bone: pale, with cracks and darker joints."""

    def base(self, face, x, y, w, h, n, r):
        t = 0.62 + (n - 0.5) * 0.4
        if r.random() < 0.05:
            t -= 0.35
        if h > 6 and (y == 0 or y == h - 1):
            t -= 0.12
        return t


class Crystal(Skin):
    """Glowing facets."""

    def base(self, face, x, y, w, h, n, r):
        return 0.35 + ((x + y) % 4) / 5.0 + (n - 0.5) * 0.2

    def emit(self, face, x, y, w, h, t, r):
        return self.ramp.smooth(min(1, t + 0.1))


class EdgeLit(Skin):
    """A plain material whose top edges glow (fins, crests)."""

    def __init__(self, ramp, light, **kw):
        super().__init__(ramp, **kw)
        self.light = light

    def emit(self, face, x, y, w, h, t, r):
        if face == 'top' or (face in SIDES and y == 0):
            return self.light
        return None


class Emissive(Skin):
    """Entirely glowing material (magic, embers, spectral blades)."""

    def emit(self, face, x, y, w, h, t, r):
        return self.ramp.smooth(min(1, t + 0.05))


class Wing(Skin):
    """A moth wing on a flat plane. The span runs along x (root at the body), the chord along the face's rows.
    Oval, swept back, with veins fanning from the root, a pale cross-band, a darker dotted margin and, on the
    forewings, a lantern-spot that glows."""

    def __init__(self, ramp, mirror=False, spot=True, fringe=None, **kw):
        super().__init__(ramp, **kw)
        self.mirror = mirror
        self.spot = spot
        self.fringe = fringe

    def paint(self, face, x, y, w, h, seed, r):
        u = (x + 0.5) / w
        if self.mirror:
            u = 1 - u
        v = (h - 0.5 - y) / h                      # 0 at the leading (front) edge
        vc = 0.5 + 0.12 * u
        e = ((u - 0.45) / 0.6) ** 2 + ((v - vc) / 0.56) ** 2
        c = np.zeros(4)
        if e > 1.0 or u < 0:
            return c, None
        ang = math.atan2(v - 0.5, u + 0.05)
        vein = (abs((ang * 2.6) % 1.0 - 0.5) < 0.12) and u > 0.2
        t = 0.35 + 0.45 * math.sin(min(1.0, u * 1.4) * math.pi * 0.6) - 0.25 * e
        if 0.5 < u < 0.64:
            t += 0.22                              # pale cross-band
        if vein:
            t -= 0.2
        t += BAYER4[y % 4, x % 4] * 0.1
        c = self.ramp.smooth(t)
        g = None
        if e > 0.72:
            c[:3] *= 0.55                          # dark margin with pale dots
            if (x + y) % 2 == 0 and e < 0.9:
                c[:3] = self.ramp.smooth(0.9)[:3]
            if self.fringe is not None:
                g = self.fringe
        if self.spot and abs(u - 0.74) < 0.1 and abs(v - vc) < 0.16:
            c = hexrgb('#ffe9a0')
            g = hexrgb('#ffc94a')
        c[3] = 1.0
        return c, g


class Antenna(Skin):
    """A feathered antenna on a thin plane: a shaft with barbs on alternate rows, the rest cut away."""

    def __init__(self, ramp, mirror=False, **kw):
        super().__init__(ramp, **kw)
        self.mirror = mirror

    def paint(self, face, x, y, w, h, seed, r):
        shaft = (w - 1 - x) if self.mirror else x
        if shaft == 0 or y % 2 == 0:
            c = self.ramp.smooth(0.8 - y / (h * 2.0))
            c[3] = 1.0
            return c, None
        return np.zeros(4), None


class Veined(Hide):
    """Hide threaded with faintly glowing veins."""

    def __init__(self, ramp, vein, rate=0.05, **kw):
        super().__init__(ramp, **kw)
        self.vein = vein
        self.rate = rate

    def emit(self, face, x, y, w, h, t, r):
        if face != 'top' and r.random() < self.rate:
            return self.vein
        return None


class Disc(Skin):
    """A round plate on a flat box (shields): the broad faces are cut to a circle with a metal rim and painted
    quarters; the thin side faces keep only their middles, where the rim meets the box edge."""

    def __init__(self, ramp, rim, paint=None, **kw):
        super().__init__(ramp, **kw)
        self.rim = rim
        self.quarter = paint

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        c = c.copy()
        if face in ('front', 'back'):
            cx, cy = (w - 1) / 2, (h - 1) / 2
            rad = min(w, h) / 2
            d = math.hypot(x - cx, y - cy)
            if d > rad - 0.15:
                c[3] = 0.0
            elif d > rad - 1.35:
                c[:3] = self.rim.smooth(0.55 - (y / h) * 0.3 + BAYER4[y % 4, x % 4] * 0.1)[:3]
            else:
                if x % 3 == 0:
                    c[:3] *= 0.8                 # plank seams
                if self.quarter is not None and ((x < cx) != (y < cy)):
                    c[:3] = c[:3] * 0.55 + self.quarter[:3] * 0.45
        elif face in ('top', 'bottom'):
            if abs(x - (w - 1) / 2) > w * 0.28:
                c[3] = 0.0
            else:
                c[:3] = self.rim.smooth(0.5)[:3]
        else:
            if abs(y - (h - 1) / 2) > h * 0.28:
                c[3] = 0.0
            else:
                c[:3] = self.rim.smooth(0.4)[:3]
        return c, g


class RibCage(Bone):
    """Bone bands with the gaps cut out, so whatever burns inside the chest shows through."""

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        c = c.copy()
        if face == 'bottom':
            c[3] = 0.0
        elif face in SIDES:
            cx = (w - 1) / 2
            slope = int(abs(x - cx) * 0.5) if face in ('front', 'back') else 0
            gap = (y - slope) % 3 != 0 and y > 0 and y < h - 1
            if face == 'front' and abs(x - cx) < 1.0:
                gap = False                       # sternum
            if face == 'back' and abs(x - cx) < 1.0:
                gap = False                       # spine
            if gap:
                c[3] = 0.0
        return c, g


class HaloRing(Skin):
    """A ring of runes on a flat plane: everything outside the ring is cut away and the ring glows."""

    def paint(self, face, x, y, w, h, seed, r):
        cx, cy = (w - 1) / 2, (h - 1) / 2
        d = math.hypot(x - cx, y - cy)
        outer = min(w, h) / 2 - 0.4
        c = np.zeros(4)
        g = None
        a = math.atan2(y - cy, x - cx)
        seg = int((a + math.pi) / (2 * math.pi) * 16)
        if outer - 2.6 <= d <= outer:
            t = 0.3 + (0.15 if d > outer - 1.2 else 0.0)
            if seg % 2 == 0 and outer - 2.0 < d < outer - 0.6:
                t = 0.85                          # rune notches
            c = self.ramp.smooth(t)
            g = self.ramp.smooth(t) * np.array([0.8, 0.8, 0.8, 1.0])
        elif outer - 4.6 <= d <= outer - 3.9 and seg % 4 == 1:
            c = self.ramp.smooth(0.5)             # a broken inner circle
            g = self.ramp.smooth(0.5) * np.array([0.7, 0.7, 0.7, 1.0])
        return c, g


# ------------------------------------------------------------------ palettes
R = {
    'moth_fur': Ramp('#6b4a24', '#9a6d34', '#c99a4f', '#e8c47c', '#f6e2b0'),
    'moth_wing': Ramp('#3b2615', '#6e4a28', '#a8773f', '#d7a45c', '#f1cf8a'),
    'moth_glow': Ramp('#8a5a12', '#d8942a', '#ffcb58', '#fff0b0'),
    'gloam': Ramp('#0c0612', '#1a0f26', '#2a1840', '#3c245a', '#523477'),
    'gloam_glow': Ramp('#5a2aa0', '#9b5cff', '#d6b0ff', '#ffffff'),
    'horn': Ramp('#15101a', '#3a3040', '#6a5f72', '#9d93a4'),
    'steel_dark': Ramp('#15171c', '#262a31', '#3a3f48', '#555b66', '#7b828e'),
    'rust': Ramp('#2a1a12', '#4d2c1a', '#7a4424', '#a0623a'),
    'violet_vein': hexrgb('#b884ff'),
    'plume': Ramp('#0a060d', '#1b1022', '#301b3d', '#482a5a'),
    'cape_black': Ramp('#0d0a0c', '#1e1519', '#312229', '#46323b'),
    'crimson': hexrgb('#7a1c22'),
    'wight_cloth': Ramp('#1a2a2c', '#2c4447', '#44686b', '#6b9396', '#9fc4c3'),
    'wight_glow': Ramp('#1f8f86', '#4fe0cf', '#bffff6', '#ffffff'),
    'ivory': Ramp('#5d5446', '#8a7f69', '#b6aa8e', '#d8cfb4', '#efe9d6'),
    'grave_gold': Ramp('#3a2a0c', '#6b4d16', '#9c7424', '#c9a040', '#e8cc78'),
    'leather': Ramp('#22120a', '#3e2212', '#5e361d', '#83502c', '#a86d3e'),
    'parchment': Ramp('#8c7650', '#b39b6d', '#d6c092', '#efe0b8', '#fbf3dc'),
    'arcane_glow': Ramp('#3a2a9c', '#6f7cff', '#b0c4ff', '#ffffff'),
    'hound': Ramp('#08060c', '#140f1e', '#221a33', '#34294d', '#4a3a6b'),
    'spirit_metal': Ramp('#2c6d6a', '#4ea7a1', '#7fd6cf', '#b5f4ee', '#e9fffc'),
    'spirit_fur': Ramp('#3a7f78', '#5fb3aa', '#8fdcd3', '#c8fff8'),
    'spirit_wood': Ramp('#2d5c58', '#46807a', '#69a8a0'),
    'bronze_drowned': Ramp('#10231f', '#1d3b33', '#2f5a4b', '#4a806a', '#6fa889'),
    'verdigris': Ramp('#2b6b5d', '#43927e', '#6cc0a4', '#a3e3c8'),
    'kelp': Ramp('#0e1c10', '#1a3220', '#2a4d30', '#3f6b44', '#5c8c5a'),
    'tide_glow': Ramp('#1b8f7f', '#3fe0c0', '#b0fff0', '#ffffff'),
    'iron_rust': Ramp('#1c1512', '#3a2a22', '#5c4234', '#7d5c48'),
    'robe_blue': Ramp('#0b0f24', '#141c3d', '#1f2b5c', '#2e3f80', '#4658a8'),
    'silver': Ramp('#6a7288', '#9aa3b8', '#c8cfe0', '#f0f3fa'),
    'hood_void': Ramp('#06070d', '#0e1020', '#171a33', '#222746'),
    'wood_twist': Ramp('#1f140d', '#3a2616', '#5a3c22', '#7a5530'),
    'royal_purple': Ramp('#1c0d22', '#34173f', '#4f2460', '#6c3483', '#8c4aa6'),
    'chain_iron': Ramp('#1c1d22', '#3b3d46', '#62656f', '#8e919b'),
    'grave_iron': Ramp('#101116', '#1f2128', '#33363f', '#4b4f5a', '#6a6e7a'),
    'hollow_iron': Ramp('#07060a', '#110f16', '#1c1924', '#2a2536', '#3b344c'),
    'hollow_glow': Ramp('#6a2ad0', '#a35cff', '#e0c2ff', '#ffffff'),
    'crown_gold': Ramp('#4a3510', '#80601f', '#b58d36', '#e0bd5e', '#fbe7a4'),
    'blade_pale': Ramp('#4a4f5c', '#7c8392', '#b3bac8', '#e4e8f0', '#ffffff'),
    'moth_ruff': Ramp('#9c7644', '#c9a26a', '#e6c992', '#f8ecd0'),
    'moth_hind': Ramp('#4a2412', '#7a3c1a', '#b0602a', '#d88a3c', '#f0b060'),
    'gloam_belly': Ramp('#1a0f26', '#2a1840', '#40265e', '#5a3a80'),
    'gloam_ember': Ramp('#6a2aa0', '#b884ff', '#ffe9a0', '#ffffff'),
    'tarnished': Ramp('#2e2410', '#4f3d1a', '#735a28', '#9a7c3c', '#bda060'),
    'crimson_ribbon': Ramp('#3a0a0e', '#5e1218', '#861c24', '#b02a30'),
    'hound_mane': Ramp('#050308', '#0e0a16', '#1c1430', '#2e2150'),
    'spirit_leather': Ramp('#24504c', '#357470', '#4c9690', '#6cbab2'),
    'spirit_cloth': Ramp('#1e4a46', '#2c6660', '#40867e', '#5aa89e'),
    'barnacle': Ramp('#5b5a4c', '#8f8c78', '#b4b09a', '#d6d2bc'),
    'fin': Ramp('#1b6f63', '#2ea08a', '#58d0b4', '#a0f0dc'),
    'pale_skin': Ramp('#5e6270', '#8c909c', '#aeb2bc', '#ccd0d8'),
    'black_gold': Ramp('#1a1408', '#2e2410', '#4a3a16', '#6e5620', '#9a7a30'),
}

SKINS = {
    'moth_fur': Hide(R['moth_fur'], grain=3),
    'moth_abdomen': Emissive(R['moth_glow'], grain=2),
    'moth_wing_l': Wing(R['moth_wing']),
    'moth_wing_r': Wing(R['moth_wing'], mirror=True),
    'gloam_hide': Hide(R['gloam'], grain=3),
    'gloam_head': Hide(R['gloam'], grain=3),
    'horn': Skin(R['horn'], contrast=1.4),
    'gloam_claw': Emissive(R['gloam_glow']),
    'gloam_tail': Hide(R['gloam'], grain=2),
    'knight_plate': Plate(R['steel_dark'], seam=4, veins=hexrgb('#b884ff')),
    'knight_helm': Plate(R['steel_dark'], seam=0, rivets=False),
    'plume': Cloth(R['plume'], tatter=0.5),
    'tattered_cape': Cloth(R['cape_black'], trim=hexrgb('#5a1418'), tatter=0.6),
    'knight_blade': Skin(R['blade_pale'], contrast=0.6, border=0.9),
    'wight_robe': Cloth(R['wight_cloth'], alpha=0.95),
    'wight_hood': Cloth(R['wight_cloth']),
    'wight_tatter': Cloth(R['wight_cloth'], tatter=0.8, hem_glow=R['wight_glow'].smooth(0.6)),
    'bone': Bone(R['ivory'], grain=3),
    'grave_gold': Plate(R['grave_gold'], seam=3, rivets=False),
    'tome_cover': Skin(R['leather'], grain=3),
    'tome_pages': Skin(R['parchment'], grain=2, contrast=0.5),
    'tome_spine': Plate(R['leather'], seam=2, rivets=False),
    'hound_hide': Hide(R['hound'], grain=2),
    'hound_head': Hide(R['hound'], grain=2),
    'hound_jaw': Hide(R['hound'], grain=2),
    'hound_spines': Crystal(R['gloam_glow']),
    'hound_tail': Hide(R['hound'], grain=2),
    'spirit_mail': Plate(R['spirit_metal'], seam=3, alpha=0.9),
    'spirit_fur': Hide(R['spirit_fur'], alpha=0.9),
    'spirit_iron': Emissive(R['spirit_metal']),
    'spirit_wood': Skin(R['spirit_wood'], alpha=0.9),
    'drowned_plate': Plate(R['bronze_drowned'], seam=4, veins=hexrgb('#3fe0c0')),
    'drowned_helm': Plate(R['bronze_drowned'], seam=0, rivets=False),
    'kelp_cape': Cloth(R['kelp'], tatter=0.7, hem_glow=R['tide_glow'].smooth(0.3)),
    'tide_shield': Plate(R['verdigris'], seam=0, rivets=True),
    'anchor_iron': Skin(R['iron_rust'], contrast=1.3),
    'arcane_robe': Cloth(R['robe_blue'], trim=R['silver'].smooth(0.6)),
    'hood_deep': Cloth(R['robe_blue']),
    'robe_hem': Cloth(R['robe_blue'], tatter=0.3, hem_glow=R['arcane_glow'].smooth(0.5)),
    'halo_runes': Emissive(R['arcane_glow']),
    'staff_wood': Skin(R['wood_twist'], contrast=1.2),
    'staff_crystal': Crystal(R['arcane_glow']),
    'skull': Bone(R['ivory'], grain=2),
    'ribcage': Bone(R['ivory'], grain=2),
    'royal_cape': Cloth(R['royal_purple'], trim=R['grave_gold'].smooth(0.7), tatter=0.5),
    'chain': Plate(R['chain_iron'], seam=2, rivets=False),
    'grave_iron': Plate(R['grave_iron'], seam=3, rivets=True),
    'hollow_plate': Plate(R['hollow_iron'], seam=4, veins=hexrgb('#a35cff')),
    'hollow_helm': Plate(R['hollow_iron'], seam=0, rivets=False),
    'hollow_cape': Cloth(R['hollow_iron'], tatter=0.6, hem_glow=R['hollow_glow'].smooth(0.4)),
    'crown_gold': Plate(R['crown_gold'], seam=0, rivets=False),
    'oathblade': Skin(R['blade_pale'], contrast=0.6, border=0.9),
    'spectral_blade': Emissive(R['hollow_glow']),
    # lanternmoth
    'moth_ruff': Hide(R['moth_ruff'], grain=2),
    'moth_antenna_l': Antenna(R['moth_ruff']),
    'moth_antenna_r': Antenna(R['moth_ruff'], mirror=True),
    'moth_hindwing_l': Wing(R['moth_hind'], spot=False, fringe=hexrgb('#c8661c')),
    'moth_hindwing_r': Wing(R['moth_hind'], mirror=True, spot=False, fringe=hexrgb('#c8661c')),
    # gloamling
    'gloam_belly': Veined(R['gloam_belly'], hexrgb('#8a5ad8'), rate=0.06, grain=2),
    'gloam_ember': Emissive(R['gloam_ember']),
    # forsworn knight
    'knight_trim': Plate(R['tarnished'], seam=0, rivets=False),
    'knight_belt': Skin(R['leather'], grain=2),
    'knight_pauldron': Plate(R['steel_dark'], seam=3, veins=hexrgb('#b884ff')),
    'knight_gauntlet': Plate(R['steel_dark'], seam=2, rivets=False),
    'leather_grip': Plate(R['leather'], seam=2, rivets=False),
    # barrow wight
    'wight_claw': Emissive(R['wight_glow']),
    # tome
    'tome_ribbon': Cloth(R['crimson_ribbon'], border=0),
    # veilhound
    'hound_mane': Hide(R['hound_mane'], grain=2),
    'hound_paw': Skin(R['hound'], contrast=0.8),
    'hound_wisp': Emissive(R['gloam_glow']),
    # spectral housecarl
    'spirit_leather': Skin(R['spirit_leather'], alpha=0.9),
    'spirit_helm': Plate(R['spirit_metal'], seam=0, rivets=True, alpha=0.9),
    'spirit_beard': Hide(R['spirit_fur'], grain=2, alpha=0.9),
    'spirit_trousers': Cloth(R['spirit_cloth'], alpha=0.9),
    'spirit_shield': Disc(R['spirit_wood'], R['spirit_metal'], paint=hexrgb('#bffff6'), alpha=0.9),
    'spirit_axehead': Plate(R['spirit_metal'], seam=0, rivets=False, alpha=0.9),
    'spirit_edge': Emissive(R['spirit_metal']),
    # sir caldris
    'drowned_trim': Plate(R['verdigris'], seam=0, rivets=True),
    'drowned_pauldron': Plate(R['bronze_drowned'], seam=3, veins=hexrgb('#3fe0c0')),
    'drowned_fin': EdgeLit(R['fin'], hexrgb('#58d0b4')),
    'barnacle': Bone(R['barnacle'], grain=2),
    'kelp': Cloth(R['kelp'], tatter=0.35, border=0),
    # archmage veyl
    'arcane_mantle': Cloth(R['robe_blue'], trim=R['silver'].smooth(0.7)),
    'arcane_sash': Plate(R['silver'], seam=0, rivets=False),
    'arcane_cuff': Cloth(R['robe_blue'], trim=R['silver'].smooth(0.6), hem_glow=R['arcane_glow'].smooth(0.5)),
    'veyl_hand': Bone(R['pale_skin'], grain=2),
    'halo_ring': HaloRing(R['arcane_glow']),
    # hrodgar
    'soul_core': Emissive(R['wight_glow']),
    'royal_tabard': Cloth(R['royal_purple'], trim=R['grave_gold'].smooth(0.7), tatter=0.4),
    'rib_cage': RibCage(R['ivory'], grain=2),
    # morvane
    'hollow_trim': Plate(R['black_gold'], seam=0, rivets=True),
    'hollow_pauldron': Plate(R['hollow_iron'], seam=3, veins=hexrgb('#a35cff')),
    'crown_gem': Emissive(R['hollow_glow']),
    'soul_iron': Plate(R['chain_iron'], seam=0, rivets=True, veins=hexrgb('#4fe0cf')),
}


# ------------------------------------------------------------------ face features (painted on a cube's front face)
def _px(tex, glow, x, y, c, g=None):
    tex.put(x, y, c)
    if g is not None:
        glow.put(x, y, g)


def f_eyes(color, glow, spacing=2, row=None, size=1, dark=None):
    def paint(tex, gl, fx, fy, w, h, r):
        yy = row if row is not None else h // 2 - 1
        if dark is not None:
            for x in range(1, w - 1):
                for y in range(max(0, yy - 1), min(h, yy + size + 1)):
                    tex.put(fx + x, fy + y, dark)
        cx = w / 2
        for sx in (-1, 1):
            ex = int(round(cx + sx * spacing - (1 if sx < 0 else 0) - (size - 1) / 2 * (1 if sx > 0 else 0)))
            for dx in range(size):
                for dy in range(size):
                    _px(tex, gl, fx + ex + dx * (1 if sx > 0 else -1) * 0 + dx, fy + yy + dy, color, glow)
    return paint


def f_gloam_face(tex, gl, fx, fy, w, h, r):
    dark = hexrgb('#050208')
    for x in range(0, w):
        for y in range(1, h):
            tex.put(fx + x, fy + y, dark if (x + y) % 7 else hexrgb('#140a20'))
    eye, eyeg = hexrgb('#ffe066'), hexrgb('#ffc21a')
    for ex in (0, w - 2):
        _px(tex, gl, fx + ex, fy + 1, eye, eyeg)
        _px(tex, gl, fx + ex + 1, fy + 1, eye, eyeg)
        _px(tex, gl, fx + ex + (1 if ex == 0 else 0), fy + 2, hexrgb('#c678ff'), hexrgb('#9b5cff'))
        _px(tex, gl, fx + ex + (0 if ex == 0 else 1), fy + 2, eye, eyeg)
    for x in range(0, w):
        y = h - 1 if x % 2 == 0 else h - 2
        _px(tex, gl, fx + x, fy + y, hexrgb('#f2e6ff'), hexrgb('#c9a6ff'))


def f_visor(color, glowc):
    def paint(tex, gl, fx, fy, w, h, r):
        slit = h // 2 - 1
        for x in range(1, w - 1):
            tex.put(fx + x, fy + slit, hexrgb('#050407'))
            tex.put(fx + x, fy + slit + 1, hexrgb('#0c0a10'))
        for x in (w // 2 - 1, w // 2):
            tex.put(fx + x, fy + slit + 2, hexrgb('#050407'))
            tex.put(fx + x, fy + slit + 3, hexrgb('#050407'))
        for ex in (w // 2 - 3, w // 2 + 1):
            _px(tex, gl, fx + ex, fy + slit, color, glowc)
            _px(tex, gl, fx + ex + 1, fy + slit, color, glowc)
            _px(tex, gl, fx + ex + (1 if ex < w // 2 else 0), fy + slit + 1, glowc * np.array([0.7, 0.7, 0.7, 1]), glowc * np.array([0.6, 0.6, 0.6, 1]))
    return paint


def f_chest_sigil(color, glowc, broken=True):
    def paint(tex, gl, fx, fy, w, h, r):
        cx, cy = w // 2, h // 3 + 1
        pts = [(0, -2), (-1, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (0, 2), (-1, 2), (1, 2)]
        for dx, dy in pts:
            if broken and dx == 1 and dy >= 0:
                continue
            _px(tex, gl, fx + cx + dx, fy + cy + dy, color, glowc)
    return paint


def f_wight_face(tex, gl, fx, fy, w, h, r):
    void = hexrgb('#02060a')
    for x in range(1, w - 1):
        for y in range(2, h - 1):
            tex.put(fx + x, fy + y, void)
    for ex in (w // 2 - 2, w // 2 + 1):
        _px(tex, gl, fx + ex, fy + h // 2, hexrgb('#b8fff4'), hexrgb('#5ff0dc'))


def f_skull(tex, gl, fx, fy, w, h, r):
    sock = hexrgb('#0a0806')
    ey = h // 2 - 2
    for ex in (w // 2 - 3, w // 2 + 1):
        for dx in range(2):
            for dy in range(3):
                tex.put(fx + ex + dx, fy + ey + dy, sock)
        tex.put(fx + ex + (1 if ex < w // 2 else 0), fy + ey - 1, hexrgb('#8a7f69'))
        _px(tex, gl, fx + ex + (1 if ex < w // 2 else 0), fy + ey + 1, hexrgb('#b8fff6'), hexrgb('#4fe0cf'))
    nx = w // 2 - (1 if w % 2 == 0 else 0)
    tex.put(fx + nx, fy + ey + 3, sock)
    tex.put(fx + w // 2, fy + ey + 3, sock)
    tex.put(fx + nx, fy + ey + 4, hexrgb('#3a3226'))
    for x in range(1, w - 1):
        tex.put(fx + x, fy + h - 3, hexrgb('#5d5446'))
        tex.put(fx + x, fy + h - 2, sock if x % 2 == 0 else hexrgb('#efe9d6'))
    cx = int(r.integers(1, w - 2))
    for y in range(0, ey):
        tex.put(fx + cx + (y % 2), fy + y, hexrgb('#5d5446'))


def f_ribs(tex, gl, fx, fy, w, h, r):
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if y % 3 != 0 and abs(x - w / 2) > 1:
                tex.put(fx + x, fy + y, hexrgb('#0b1413'))
                if r.random() < 0.18:
                    _px(tex, gl, fx + x, fy + y, hexrgb('#4fe0cf'), hexrgb('#2fb8a8'))


def f_hollow_core(tex, gl, fx, fy, w, h, r):
    cx, cy = (w - 1) / 2, h * 0.38
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, (y - cy) * 1.1
            d = abs(dx) + abs(dy) * 0.9                 # a diamond-shaped wound
            if d < 1.3:
                tex.put(fx + x, fy + y, hexrgb('#000000'))
            elif d < 2.3:
                _px(tex, gl, fx + x, fy + y, hexrgb('#f0d8ff'), hexrgb('#d9a8ff'))
            elif d < 3.1:
                _px(tex, gl, fx + x, fy + y, hexrgb('#a35cff'), hexrgb('#7a3fe0'))
    for a in (0.5, 1.2, 2.0, 2.7, 3.6, 4.4, 5.3):
        x, y = cx, cy
        for k in range(8):
            x += math.cos(a) * 0.9 + (r.random() - 0.5) * 0.6
            y += math.sin(a) * 0.9 + (r.random() - 0.5) * 0.6
            xi, yi = int(round(x)), int(round(y))
            if abs(xi - cx) + abs(yi - cy) < 3.2:
                continue
            if 0 <= xi < w and 0 <= yi < h:
                fade = 1 - k / 8
                _px(tex, gl, fx + xi, fy + yi, np.array([0.55, 0.3, 0.9, 1.0]) * (0.5 + fade / 2) + np.array([0, 0, 0, 0.5 - fade / 2]),
                    hexrgb('#7a3fe0') if fade > 0.3 else None)


def f_veyl_face(tex, gl, fx, fy, w, h, r):
    void = hexrgb('#03040a')
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            tex.put(fx + x, fy + y, void)
    for ex in (w // 2 - 2, w // 2 + 1):
        _px(tex, gl, fx + ex, fy + h // 2 - 1, hexrgb('#ffffff'), hexrgb('#b0c4ff'))
    for x in range(2, w - 2):
        for y in range(h // 2 + 1, h):
            if (x + y) % 2 == 0 or r.random() < 0.5:
                tex.put(fx + x, fy + y, hexrgb('#d9dde8') if r.random() < 0.7 else hexrgb('#aab0c0'))


def f_tome_eye(tex, gl, fx, fy, w, h, r):
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            d = math.hypot((x + 0.5 - cx) / 1.6, y + 0.5 - cy)
            if d < 1.2:
                _px(tex, gl, fx + x, fy + y, hexrgb('#ffffff'), hexrgb('#b0c4ff'))
            elif d < 2.2:
                _px(tex, gl, fx + x, fy + y, hexrgb('#6f7cff'), hexrgb('#6f7cff'))
    for x in (0, w - 1):
        for y in (0, h - 1):
            tex.put(fx + x, fy + y, hexrgb('#c9a040'))


def f_runes(color):
    def paint(tex, gl, fx, fy, w, h, r):
        for y in range(1, h - 1, 2):
            for x in range(1, w - 1):
                if r.random() < 0.35:
                    _px(tex, gl, fx + x, fy + y, color, color)
    return paint


def f_hound_face(tex, gl, fx, fy, w, h, r):
    for ex in (1, w - 2):
        _px(tex, gl, fx + ex, fy + 1, hexrgb('#e8c8ff'), hexrgb('#b884ff'))
    for x in range(1, w - 1):
        tex.put(fx + x, fy + h - 1, hexrgb('#0a0610'))


def f_teeth(tex, gl, fx, fy, w, h, r):
    for x in range(w):
        if x % 2 == 0:
            tex.put(fx + x, fy, hexrgb('#efe6ff'))


def f_beard_helm(tex, gl, fx, fy, w, h, r):
    for x in range(1, w - 1):
        tex.put(fx + x, fy + 3, hexrgb('#0b2422'))
    tex.put(fx + w // 2, fy + 4, hexrgb('#7fd6cf'))
    for x in range(1, w - 1):
        for y in range(h - 3, h):
            tex.put(fx + x, fy + y, hexrgb('#9fe8e0') if (x + y) % 2 else hexrgb('#6fc8c0'))
    for ex in (w // 2 - 2, w // 2 + 1):
        _px(tex, gl, fx + ex, fy + 3, hexrgb('#e9fffc'), hexrgb('#7ff5e6'))


def f_wave_emblem(tex, gl, fx, fy, w, h, r):
    for x in range(1, w - 1):
        y = int(h / 2 + math.sin(x * 0.9) * 1.5)
        for dy in range(2):
            _px(tex, gl, fx + x, fy + y + dy, hexrgb('#b0fff0'), hexrgb('#3fe0c0') if dy == 0 else None)
    for x in range(0, w):
        tex.put(fx + x, fy, hexrgb('#1d3b33'))
        tex.put(fx + x, fy + h - 1, hexrgb('#1d3b33'))


def f_fangs(tex, gl, fx, fy, w, h, r):
    for x in range(w):
        if x % 2 == 1 or x in (0, w - 1):
            tex.put(fx + x, fy + h - 1, hexrgb('#efe6ff'))


def f_shield_emblem(tex0, gl0, fx, fy, w, h, r):
    """Caldris' tower shield: a verdigris border, a pale anchor, and a glowing tide along the foot. Painted
    upside down, because the face it sits on is turned over when the shield is raised."""
    class Flip:
        def __init__(self, img):
            self.img = img

        def put(self, x, y, c):
            self.img.put(x, fy + (h - 1) - (y - fy), c)
    tex, gl = Flip(tex0), Flip(gl0)
    trim = hexrgb('#1d3b33')
    for x in range(w):
        for y in range(h):
            if x in (0, w - 1) or y in (0, h - 1):
                tex.put(fx + x, fy + y, trim)
            elif x in (1, w - 2) or y in (1, h - 2):
                tex.put(fx + x, fy + y, hexrgb('#6cc0a4'))
    cx = w // 2
    pale = hexrgb('#d8e8d0')
    top = 3
    for y in range(top + 2, h - 6):
        tex.put(fx + cx, fy + y, pale)
        tex.put(fx + cx - 1, fy + y, hexrgb('#b4c8b0'))
    for x in range(cx - 3, cx + 3):
        tex.put(fx + x, fy + top + 3, pale)
    tex.put(fx + cx - 1, fy + top, pale)
    tex.put(fx + cx, fy + top, pale)
    tex.put(fx + cx - 2, fy + top + 1, pale)
    tex.put(fx + cx + 1, fy + top + 1, pale)
    tex.put(fx + cx - 1, fy + top + 2, pale)
    tex.put(fx + cx, fy + top + 2, pale)
    base = h - 7
    for i in range(0, 5):
        tex.put(fx + cx - 1 - i, fy + base - (i * i) // 4, pale)
        tex.put(fx + cx + i, fy + base - (i * i) // 4, pale)
    for x in range(2, w - 2):
        y = h - 4 + int(round(math.sin(x * 1.1) * 0.8))
        _px(tex, gl, fx + x, fy + y, hexrgb('#b0fff0'), hexrgb('#3fe0c0'))
        if x % 3 == 0:
            _px(tex, gl, fx + x, fy + y + 1, hexrgb('#3fe0c0'), hexrgb('#1b8f7f'))


FEATURES = {
    'gloam_face': f_gloam_face,
    'knight_visor': f_visor(hexrgb('#d8b0ff'), hexrgb('#a35cff')),
    'knight_chest': f_chest_sigil(hexrgb('#b02a30'), hexrgb('#6a1016')),
    'wight_face': f_wight_face,
    'tome_eye': f_tome_eye,
    'tome_runes': f_runes(hexrgb('#8a7cff')),
    'hound_face': f_hound_face,
    'teeth': f_teeth,
    'housecarl_face': f_beard_helm,
    'drowned_visor': f_visor(hexrgb('#c8fff0'), hexrgb('#3fe0c0')),
    'wave_emblem': f_wave_emblem,
    'veyl_face': f_veyl_face,
    'robe_runes': f_runes(hexrgb('#9fb4ff')),
    'skull_face': f_skull,
    'ribs': f_ribs,
    'hollow_visor': f_visor(hexrgb('#f0d8ff'), hexrgb('#c07aff')),
    'hollow_core': f_hollow_core,
    'moth_eyes': f_eyes(hexrgb('#1a0f06'), None, spacing=1),
    'blade_runes': f_runes(hexrgb('#c07aff')),
    'fangs': f_fangs,
    'shield_emblem': f_shield_emblem,
    'rib_glow': f_ribs,
}
