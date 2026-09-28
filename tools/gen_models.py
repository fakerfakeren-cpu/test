"""Entity model generator.

Each model is described once here; this script emits
  * Java LayerDefinitions (src/main/java/com/astralfall/client/model/ModelDefs.java)
  * a matching texture and an emissive "glow" texture per model.
UVs are packed automatically so geometry and art can never drift apart.
"""
import math
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

ROOT = os.path.join(os.path.dirname(__file__), '..')
TEX = os.path.join(ROOT, 'src', 'main', 'resources', 'assets', 'astralfall', 'textures', 'entity')
JAVA = os.path.join(ROOT, 'src', 'main', 'java', 'com', 'astralfall', 'client', 'model', 'ModelDefs.java')


class Box:
    def __init__(self, x, y, z, w, h, d, mat, feature=None, inflate=0.0, mirror=False):
        self.x, self.y, self.z, self.w, self.h, self.d = x, y, z, w, h, d
        self.mat, self.feature, self.inflate, self.mirror = mat, feature, inflate, mirror
        self.u = self.v = 0

    @property
    def fw(self):
        return int(math.ceil(2 * (self.d + self.w)))

    @property
    def fh(self):
        return int(math.ceil(self.d + self.h))


class Part:
    def __init__(self, name, pivot=(0, 0, 0), rot=(0, 0, 0), boxes=(), children=()):
        self.name, self.pivot, self.rot = name, pivot, rot
        self.boxes, self.children = list(boxes), list(children)

    def all_boxes(self):
        for b in self.boxes:
            yield b
        for c in self.children:
            yield from c.all_boxes()


class Model:
    def __init__(self, name, tex_w, tex_h, parts):
        self.name, self.tw, self.th, self.parts = name, tex_w, tex_h, parts

    def boxes(self):
        for p in self.parts:
            yield from p.all_boxes()


# ------------------------------------------------------------------ materials
def pal(*hexes):
    return [hexc(h) for h in hexes]


MATS = {
    'wisp_core': dict(p=pal('#3fc6e0', '#9af3ff', '#effeff', '#ffffff'), glow=True, pattern='gradient'),
    'wisp_shell': dict(p=pal('#1f7ea3', '#3fc6e0', '#9af3ff'), glow=True, pattern='lattice', alpha=110),
    'wisp_wing': dict(p=pal('#9af3ff', '#effeff', '#c998ff'), glow=True, pattern='wing', alpha=150),
    'wisp_tail': dict(p=pal('#3fc6e0', '#9af3ff', '#effeff'), glow=True, pattern='gradient', alpha=190),
    'wisp_mote': dict(p=pal('#ffe9a3', '#fff6d0', '#ffffff'), glow=True, pattern='flat'),
    'void_skin': dict(p=pal('#07040f', '#120a1f', '#1d1030', '#2a1548'), pattern='noise'),
    'void_skin_light': dict(p=pal('#120a1f', '#241339', '#35205a', '#4a2c78'), pattern='noise'),
    'void_cloth': dict(p=pal('#05030a', '#100820', '#1c0f33'), pattern='tatter'),
    'void_claw': dict(p=pal('#d8c8f0', '#f3e4ff', '#ffffff'), pattern='flat', glow=True),
    'rock': dict(p=pal('#120f16', '#1f1a25', '#2d2634', '#3d3446', '#4d4358'), pattern='cracks', crack=pal('#5a1606', '#b4380c', '#ff7a1f', '#ffc56b')),
    'rock_dark': dict(p=pal('#0d0b10', '#17131c', '#221c29', '#2d2634'), pattern='noise'),
    'rock_leg': dict(p=pal('#17131c', '#221c29', '#2d2634', '#3d3446'), pattern='segments'),
    'ore_bump': dict(p=pal('#46587f', '#6f86b6', '#a9c1ea', '#eef5ff'), pattern='noise'),
    'mandible': dict(p=pal('#3d3446', '#5c5068', '#8a7aa0'), pattern='flat'),
    'eye_white': dict(p=pal('#b8a8d8', '#d8ccf0', '#f3eeff'), pattern='gradient'),
    'eye_lid': dict(p=pal('#1d1030', '#2a1548', '#3a1f60'), pattern='noise'),
    'tentacle': dict(p=pal('#1a0d2e', '#2a1548', '#46236e', '#6a3aa0'), pattern='rings'),
    'spike': dict(p=pal('#2a1548', '#46236e', '#9150e0'), pattern='gradient'),
    'titan_armor': dict(p=pal('#0c0f2a', '#161b44', '#212962', '#2e3880', '#4150a6'), pattern='plates', trim=pal('#6b4a12', '#b9862a', '#f2c14e', '#ffe9a3')),
    'titan_gold': dict(p=pal('#6b4a12', '#b9862a', '#f2c14e', '#ffe9a3'), pattern='gradient'),
    'titan_skin': dict(p=pal('#12061f', '#1d0c33', '#2a1248', '#3d1c66'), pattern='nebula'),
    'titan_nebula': dict(p=pal('#1d0c33', '#3d1c66', '#6a2ca0', '#a55cf0', '#e0b8ff'), pattern='nebula', glow=True, alpha=235),
    'titan_core': dict(p=pal('#ffd35c', '#fff1b0', '#ffffff'), pattern='star', glow=True),
    'titan_rune': dict(p=pal('#9af3ff', '#effeff'), pattern='flat', glow=True),
    'crystal': dict(p=pal('#1f7ea3', '#3fc6e0', '#9af3ff', '#effeff'), pattern='facets', glow=True),
    'meteor': dict(p=pal('#120f16', '#1f1a25', '#2d2634', '#3d3446'), pattern='cracks', crack=pal('#b4380c', '#ff7a1f', '#ffc56b', '#fff1c9'), glowcracks=True),
    'star_rock': dict(p=pal('#f08a24', '#ffd35c', '#fff3b8', '#ffffff'), pattern='gradient', glow=True),
    'void_core': dict(p=pal('#000000', '#02010a', '#060312'), pattern='flat'),
    'void_disk': dict(p=pal('#3a1560', '#6a2ca0', '#a55cf0', '#e0b8ff', '#ffffff'), pattern='disk', glow=True, alpha=220),
}


# ------------------------------------------------------------------ model definitions
def wisp():
    motes = Part('orbit', (0, 0, 0), boxes=[Box(6, -1, -1, 2, 2, 2, 'wisp_mote'), Box(-8, 0, -1, 2, 2, 2, 'wisp_mote'), Box(-1, -2, 6, 2, 2, 2, 'wisp_mote')])
    tail3 = Part('tail3', (0, 3, 0), boxes=[Box(-1, 0, -1, 2, 2, 2, 'wisp_tail')])
    tail2 = Part('tail2', (0, 3, 0), boxes=[Box(-1, 0, -1, 2, 3, 2, 'wisp_tail')], children=[tail3])
    tail1 = Part('tail1', (0, 3, 0), boxes=[Box(-2, 0, -2, 4, 3, 4, 'wisp_tail')], children=[tail2])
    body = Part('body', (0, 16, 0), boxes=[Box(-3, -3, -3, 6, 6, 6, 'wisp_core', feature='wisp_face'), Box(-4, -4, -4, 8, 8, 8, 'wisp_shell')],
                children=[Part('left_wing', (3, -1, 1), boxes=[Box(0, -4, 0, 7, 7, 0, 'wisp_wing')]),
                          Part('right_wing', (-3, -1, 1), boxes=[Box(-7, -4, 0, 7, 7, 0, 'wisp_wing', mirror=True)]),
                          tail1, motes])
    return Model('astral_wisp', 64, 64, [body])


def stalker():
    def arm(side):
        name = 'left' if side > 0 else 'right'
        x = 0 if side > 0 else -2
        claw = Part(name + '_claw', (x + 1 if side > 0 else x + 1, 21, 0), boxes=[
            Box(-1.5, 0, -1.5, 1, 5, 1, 'void_claw'), Box(0.5, 0, -1.5, 1, 6, 1, 'void_claw'), Box(-0.5, 0, 0.5, 1, 4, 1, 'void_claw')])
        return Part(name + '_arm', (4.5 * side, -11, 0), rot=(0, 0, -0.08 * side), boxes=[Box(x, -1, -1, 2, 22, 2, 'void_skin_light')], children=[claw])
    head = Part('head', (0, -12, 0), boxes=[Box(-3, -11, -3, 6, 11, 6, 'void_skin', feature='stalker_face')])
    cape = Part('cape', (0, -12, 1.6), boxes=[Box(-4, 0, 0, 8, 16, 0, 'void_cloth')])
    body = Part('body', (0, 8, 0), rot=(0.18, 0, 0), boxes=[Box(-3.5, -12, -1.5, 7, 12, 3, 'void_skin', feature='stalker_ribs')],
                children=[head, arm(1), arm(-1), cape])
    return Model('void_stalker', 64, 64, [body,
                                          Part('left_leg', (2, 8, 0), boxes=[Box(-1, 0, -1, 2, 16, 2, 'void_skin_light')]),
                                          Part('right_leg', (-2, 8, 0), boxes=[Box(-1, 0, -1, 2, 16, 2, 'void_skin_light', mirror=True)])])


def crawler():
    legs = []
    for side in (1, -1):
        for i, z in enumerate((-5, 0, 5)):
            nm = ('left' if side > 0 else 'right') + '_leg' + str(i)
            lower = Part(nm + '_lower', (8 * side, 0, 0), rot=(0, 0, -1.25 * side),
                         boxes=[Box(-1, 0, -1, 2, 9, 2, 'rock_leg')])
            upper = Part(nm, (6 * side, 2, z), rot=(0, (0.35 * (i - 1)) * side, 0.45 * side),
                         boxes=[Box(0 if side > 0 else -8, -1, -1, 8, 2, 2, 'rock_leg')], children=[lower])
            legs.append(upper)
    head = Part('head', (0, 1, -8), boxes=[Box(-4, -3, -6, 8, 6, 6, 'rock', feature='crawler_face')],
                children=[Part('left_mandible', (2.5, 2, -6), rot=(0, -0.3, 0), boxes=[Box(-1, -1, -4, 2, 2, 4, 'mandible')]),
                          Part('right_mandible', (-2.5, 2, -6), rot=(0, 0.3, 0), boxes=[Box(-1, -1, -4, 2, 2, 4, 'mandible')])])
    body = Part('body', (0, 15, 0), boxes=[Box(-7, -4, -8, 14, 8, 16, 'rock'),
                                           Box(-5, -7, -5, 10, 3, 10, 'rock_dark'),
                                           Box(-2, -9, -2, 4, 2, 4, 'ore_bump'),
                                           Box(3, -6, 4, 3, 2, 3, 'ore_bump'),
                                           Box(-6, -6, -6, 3, 2, 3, 'ore_bump')],
                children=[head] + legs)
    return Model('meteorite_crawler', 128, 64, [body])


def gazer():
    tentacles = []
    for i in range(6):
        a = i * math.pi / 3
        x, z = round(math.cos(a) * 3.5, 1), round(math.sin(a) * 3.5, 1)
        s3 = Part(f'tentacle{i}_c', (0, 5, 0), boxes=[Box(-0.5, 0, -0.5, 1, 5, 1, 'tentacle')])
        s2 = Part(f'tentacle{i}_b', (0, 5, 0), boxes=[Box(-1, 0, -1, 2, 5, 2, 'tentacle')], children=[s3])
        s1 = Part(f'tentacle{i}', (x, 5, z), boxes=[Box(-1, 0, -1, 2, 5, 2, 'tentacle')], children=[s2])
        tentacles.append(s1)
    spikes = [Box(-1, -9, -1, 2, 3, 2, 'spike'), Box(-5, -8, -3, 2, 2, 2, 'spike'), Box(3, -8, -3, 2, 2, 2, 'spike'),
              Box(-4, -8, 2, 2, 2, 2, 'spike'), Box(2, -8, 2, 2, 2, 2, 'spike')]
    body = Part('body', (0, 12, 0), boxes=[Box(-6, -6, -6, 12, 12, 12, 'eye_white', feature='gazer_eye'),
                                           Box(-5, -7, -5, 10, 1, 10, 'eye_lid'), Box(-5, 6, -5, 10, 1, 10, 'eye_lid')] + spikes,
                children=[Part('top_lid', (0, -6, -6.2), boxes=[Box(-6.5, 0, -1, 13, 6, 1, 'eye_lid')]),
                          Part('bottom_lid', (0, 6, -6.2), boxes=[Box(-6.5, -6, -1, 13, 6, 1, 'eye_lid')])] + tentacles)
    return Model('void_gazer', 128, 64, [body])


def astraeus():
    def arm(side):
        nm = 'left' if side > 0 else 'right'
        claws = [Box(-4 + i * 3, 5, -3.5, 2, 5, 2, 'titan_gold') for i in range(3)]
        hand = Part(nm + '_hand', (0, 13, 0), boxes=[Box(-4, 0, -4, 8, 6, 8, 'titan_armor')] + claws)
        fore = Part(nm + '_forearm', (0, 13, 0), boxes=[Box(-3.5, 0, -3.5, 7, 13, 7, 'titan_armor')], children=[hand])
        return Part(nm + '_arm', (15 * side, -12, 0), rot=(0, 0, -0.15 * side), boxes=[Box(-3, 0, -3, 6, 13, 6, 'titan_skin')], children=[fore])
    halo = Part('halo', (0, -6, 7), boxes=[Box(round(math.cos(i * math.pi / 6) * 10) - 1, round(math.sin(i * math.pi / 6) * 10) - 1, 0, 2, 2, 1, 'titan_rune') for i in range(12)])
    crown = [Box(-6, -15, -6, 2, 4, 2, 'titan_gold'), Box(-1, -18, -6, 2, 7, 2, 'titan_gold'), Box(4, -15, -6, 2, 4, 2, 'titan_gold'),
             Box(-6, -14, 3, 2, 3, 2, 'titan_gold'), Box(4, -14, 3, 2, 3, 2, 'titan_gold'), Box(-6, -12, -6, 12, 1, 12, 'titan_gold')]
    head = Part('head', (0, -16, 0), boxes=[Box(-6, -12, -6, 12, 12, 12, 'titan_armor', feature='titan_face')] + crown, children=[halo])
    tail4 = Part('tail4', (0, 8, 0), boxes=[Box(-1, 0, -1, 2, 6, 2, 'titan_nebula')])
    tail3 = Part('tail3', (0, 8, 0), boxes=[Box(-2, 0, -2, 4, 8, 4, 'titan_nebula')], children=[tail4])
    tail2 = Part('tail2', (0, 8, 0), boxes=[Box(-4, 0, -3, 8, 8, 6, 'titan_nebula')], children=[tail3])
    tail = Part('tail', (0, 6, 0), boxes=[Box(-6, 0, -4, 12, 8, 8, 'titan_nebula')], children=[tail2])
    torso = Part('torso', (0, -14, 0), boxes=[Box(-10, -16, -5, 20, 16, 10, 'titan_armor', feature='titan_chest'),
                                              Box(-3, -12, -6, 6, 6, 1, 'titan_core'),
                                              Box(-7, 0, -4, 14, 6, 8, 'titan_skin')],
                 children=[head, arm(1), arm(-1),
                           Part('left_pauldron', (12, -14, 0), boxes=[Box(-2, -3, -5, 10, 7, 10, 'titan_armor')]),
                           Part('right_pauldron', (-12, -14, 0), boxes=[Box(-8, -3, -5, 10, 7, 10, 'titan_armor')]),
                           tail])
    shards = []
    for i in range(6):
        a = i * math.pi / 3
        shards.append(Part(f'shard{i}', (round(math.cos(a) * 22, 1), 0, round(math.sin(a) * 22, 1)), boxes=[Box(-1, -5, -1, 2, 10, 2, 'crystal')]))
    orbit = Part('orbit', (0, -22, 0), children=shards)
    return Model('astraeus', 256, 128, [torso, orbit])


def meteor():
    boxes = [Box(-8, -8, -8, 16, 16, 16, 'meteor'),
             Box(-10, -5, -5, 2, 10, 10, 'meteor'), Box(8, -6, -4, 2, 9, 8, 'meteor'),
             Box(-5, -10, -6, 10, 2, 12, 'meteor'), Box(-6, 8, -5, 12, 2, 10, 'meteor'),
             Box(-5, -4, -10, 10, 9, 2, 'meteor'), Box(-4, -6, 8, 8, 10, 2, 'meteor')]
    return Model('meteor', 128, 128, [Part('rock', (0, 0, 0), boxes=boxes)])


def fallen_star_meteor():
    m = meteor()
    m.name = 'meteor_star'
    for b in m.boxes():
        b.mat = 'star_rock'
    return m


def singularity():
    core = Part('core', (0, 0, 0), boxes=[Box(-4, -4, -4, 8, 8, 8, 'void_core'), Box(-3, -5, -3, 6, 10, 6, 'void_core'),
                                          Box(-5, -3, -3, 10, 6, 6, 'void_core'), Box(-3, -3, -5, 6, 6, 10, 'void_core')])
    disk_boxes = []
    for i in range(16):
        a = i * math.pi / 8
        disk_boxes.append(Box(round(math.cos(a) * 8) - 2, 0, round(math.sin(a) * 8) - 2, 4, 1, 4, 'void_disk'))
    for i in range(12):
        a = i * math.pi / 6 + 0.2
        disk_boxes.append(Box(round(math.cos(a) * 11) - 1, 0, round(math.sin(a) * 11) - 1, 3, 1, 3, 'void_disk'))
    disk = Part('disk', (0, 0, 0), boxes=disk_boxes)
    return Model('singularity', 64, 64, [core, disk])


MODELS = [wisp(), stalker(), crawler(), gazer(), astraeus(), meteor(), fallen_star_meteor(), singularity()]


# ------------------------------------------------------------------ UV packing
def pack(model):
    x = y = 0
    row_h = 0
    for b in sorted(model.boxes(), key=lambda b: -b.fh):
        if x + b.fw > model.tw:
            x = 0
            y += row_h
            row_h = 0
        b.u, b.v = x, y
        x += b.fw
        row_h = max(row_h, b.fh)
    if y + row_h > model.th:
        raise ValueError(f'{model.name}: texture {model.tw}x{model.th} too small (needs {y + row_h})')


# ------------------------------------------------------------------ painting
def face_rects(b):
    u, v, w, h, d = b.u, b.v, int(math.ceil(b.w)), int(math.ceil(b.h)), int(math.ceil(b.d))
    return {
        'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
        'west': (u, v + d, d, h), 'north': (u + d, v + d, w, h),
        'east': (u + d + w, v + d, d, h), 'south': (u + d + w + d, v + d, w, h),
    }


FACE_SHADE = {'top': 1.15, 'bottom': 0.7, 'north': 1.0, 'south': 0.9, 'east': 0.85, 'west': 0.95}


def paint_box(tex, glow, b, seed):
    m = MATS[b.mat]
    p = m['p']
    r = rng(seed)
    alpha = m.get('alpha', 255)
    noise = value_noise(max(4, tex.w), max(4, tex.h), 3, seed, octaves=2) if m['pattern'] in ('noise', 'cracks', 'nebula', 'plates') else None
    for face, (fx, fy, fw, fh) in face_rects(b).items():
        if fw <= 0 or fh <= 0:
            continue
        fshade = FACE_SHADE[face]
        for yy in range(fh):
            for xx in range(fw):
                t = 0.5
                pat = m['pattern']
                if pat == 'gradient':
                    t = 1.0 - yy / max(1, fh - 1) * 0.8
                elif pat in ('noise', 'cracks', 'plates', 'nebula'):
                    t = noise[(fy + yy) % noise.shape[0], (fx + xx) % noise.shape[1]]
                elif pat == 'flat':
                    t = 0.6
                elif pat == 'lattice':
                    t = 0.8 if (xx + yy) % 3 == 0 else 0.3
                elif pat == 'wing':
                    t = 0.3 + 0.7 * (1 - abs(xx / max(1, fw - 1) - 0.5) * 2) * (1 - yy / max(1, fh))
                elif pat == 'segments':
                    t = 0.8 if yy % 3 == 0 else 0.35
                elif pat == 'rings':
                    t = 0.85 if yy % 2 == 0 else 0.35
                elif pat == 'facets':
                    t = ((xx + yy) % 4) / 3.0
                elif pat == 'star':
                    cx, cy = (fw - 1) / 2, (fh - 1) / 2
                    t = 1 - min(1, math.hypot(xx - cx, yy - cy) / max(1, max(fw, fh) / 2))
                elif pat == 'disk':
                    t = 0.2 + 0.8 * r.random()
                elif pat == 'tatter':
                    t = 0.4 + 0.3 * r.random()
                col = ramp(p, t)
                col = shade(col, fshade) if face != 'north' else col
                a = alpha
                if pat == 'lattice' and (xx + yy) % 3 != 0 and (xx - yy) % 3 != 0:
                    a = 0
                if pat == 'tatter' and (yy > fh * 0.6 and r.random() < (yy / fh - 0.5)):
                    a = 0
                if pat == 'wing' and (xx % 3 == 1 and yy % 2 == 0):
                    col = shade(col, 1.3)
                if pat == 'nebula' and r.random() < 0.05:
                    col = hexc('#ffffff')
                if pat == 'plates':
                    if xx == 0 or yy == 0 or (fh > 6 and yy % 6 == 0):
                        col = shade(col, 1.25)
                    if (fh > 6 and yy % 6 == 5) or xx == fw - 1 or yy == fh - 1:
                        col = shade(col, 0.7)
                    if 'trim' in m and (yy == 1 and fh > 4):
                        col = m['trim'][2]
                c = (col[0], col[1], col[2], a)
                tex.set(fx + xx, fy + yy, c) if a > 0 else None
                if m.get('glow'):
                    glow.set(fx + xx, fy + yy, (col[0], col[1], col[2], max(a, 1) if a else 0))
        # cracks
        if m['pattern'] == 'cracks' and fw >= 3 and fh >= 3:
            cp = m['crack']
            for _ in range(max(1, (fw * fh) // 40)):
                x0, y0 = r.randrange(fw), r.randrange(fh)
                for i in range(r.randrange(3, 8)):
                    if 0 <= x0 < fw and 0 <= y0 < fh:
                        cc = ramp(cp, 0.4 + 0.6 * r.random())
                        tex.set(fx + x0, fy + y0, cc)
                        if m.get('glowcracks', True):
                            glow.set(fx + x0, fy + y0, cc)
                    x0 += r.choice((-1, 0, 1))
                    y0 += r.choice((0, 1))
        # darker outline for readability
        if m['pattern'] not in ('lattice', 'wing', 'disk', 'tatter') and fw >= 4 and fh >= 4:
            for xx in range(fw):
                for yy in (0, fh - 1):
                    c0 = tex.get(fx + xx, fy + yy)
                    if c0[3]:
                        tex.set(fx + xx, fy + yy, shade(c0, 0.8))
    if b.feature:
        FEATURES[b.feature](tex, glow, face_rects(b)['north'], face_rects(b))


def fx_wisp_face(tex, glow, r, rects):
    x, y, w, h = r
    for (ex, ey) in ((1, 2), (4, 2)):
        tex.set(x + ex, y + ey, hexc('#123e5c'))
        tex.set(x + ex, y + ey + 1, hexc('#123e5c'))
    tex.set(x + 2, y + 4, hexc('#1f7ea3')); tex.set(x + 3, y + 4, hexc('#1f7ea3'))


def fx_stalker_face(tex, glow, r, rects):
    x, y, w, h = r
    for ex in (1, 4):
        for yy in (3, 4):
            tex.set(x + ex, y + yy, hexc('#ffffff'))
            glow.set(x + ex, y + yy, hexc('#e8e0ff'))
    for yy in range(6, 10):
        tex.set(x + 2 + (yy % 2), y + yy, hexc('#c998ff'))
        glow.set(x + 2 + (yy % 2), y + yy, hexc('#9150e0'))


def fx_stalker_ribs(tex, glow, r, rects):
    x, y, w, h = r
    for yy in range(2, h - 2, 2):
        for xx in range(1, w - 1):
            if xx != w // 2:
                tex.set(x + xx, y + yy, hexc('#35205a'))
    for yy in range(3, 6):
        tex.set(x + w // 2, y + yy, hexc('#9150e0'))
        glow.set(x + w // 2, y + yy, hexc('#9150e0'))


def fx_crawler_face(tex, glow, r, rects):
    x, y, w, h = r
    for (ex, ey) in ((1, 1), (5, 1), (2, 3), (4, 3)):
        tex.set(x + ex, y + ey, hexc('#ffc56b'))
        glow.set(x + ex, y + ey, hexc('#ff9a3c'))


def fx_gazer_eye(tex, glow, r, rects):
    x, y, w, h = r
    cx, cy = (w - 1) / 2, (h - 1) / 2
    for yy in range(h):
        for xx in range(w):
            d = math.hypot(xx - cx, yy - cy)
            if d < 4.6:
                col = ramp(pal('#3a1560', '#9150e0', '#9af3ff'), 1 - d / 4.6)
                tex.set(x + xx, y + yy, col)
                glow.set(x + xx, y + yy, col)
            if d < 1.8:
                tex.set(x + xx, y + yy, hexc('#05020a'))
                glow.set(x + xx, y + yy, (0, 0, 0, 0))
            if 4.6 <= d < 5.5:
                tex.set(x + xx, y + yy, hexc('#5a2394'))
    tex.set(x + int(cx) - 2, y + int(cy) - 2, hexc('#ffffff'))
    glow.set(x + int(cx) - 2, y + int(cy) - 2, hexc('#ffffff'))


def fx_titan_face(tex, glow, r, rects):
    x, y, w, h = r
    # visor slit
    for xx in range(2, w - 2):
        tex.set(x + xx, y + 5, hexc('#05030a'))
        tex.set(x + xx, y + 6, hexc('#05030a'))
    for ex in (3, 8):
        for dx in (0, 1):
            tex.set(x + ex + dx, y + 5, hexc('#ffe9a3'))
            glow.set(x + ex + dx, y + 5, hexc('#ffd35c'))
            tex.set(x + ex + dx, y + 6, hexc('#f2c14e'))
            glow.set(x + ex + dx, y + 6, hexc('#f2c14e'))
    for yy in range(8, 11):
        tex.set(x + w // 2 - 1, y + yy, hexc('#b9862a'))
        tex.set(x + w // 2, y + yy, hexc('#b9862a'))


def fx_titan_chest(tex, glow, r, rects):
    x, y, w, h = r
    cx = w // 2
    for yy in range(h):
        tex.set(x + cx, y + yy, hexc('#b9862a'))
        tex.set(x + cx - 1, y + yy, hexc('#6b4a12'))
    for xx in range(w):
        tex.set(x + xx, y + 1, hexc('#f2c14e'))
    for i in range(6):
        tex.set(x + 2 + i, y + 10 + i // 2, hexc('#9af3ff'))
        glow.set(x + 2 + i, y + 10 + i // 2, hexc('#9af3ff'))
        tex.set(x + w - 3 - i, y + 10 + i // 2, hexc('#9af3ff'))
        glow.set(x + w - 3 - i, y + 10 + i // 2, hexc('#9af3ff'))


FEATURES = {
    'wisp_face': fx_wisp_face, 'stalker_face': fx_stalker_face, 'stalker_ribs': fx_stalker_ribs,
    'crawler_face': fx_crawler_face, 'gazer_eye': fx_gazer_eye, 'titan_face': fx_titan_face, 'titan_chest': fx_titan_chest,
}


# ------------------------------------------------------------------ java emission
def jf(v):
    s = f'{float(v):.4f}'.rstrip('0').rstrip('.')
    if '.' not in s:
        s += '.0'
    return s + 'F'


def emit_part(lines, parent_var, part, depth):
    var = f'p_{part.name}'
    cube = 'CubeListBuilder.create()'
    for b in part.boxes:
        cube += f'.texOffs({b.u}, {b.v})'
        if b.mirror:
            cube += '.mirror()'
        if b.inflate:
            cube += f'.addBox({jf(b.x)}, {jf(b.y)}, {jf(b.z)}, {jf(b.w)}, {jf(b.h)}, {jf(b.d)}, new CubeDeformation({jf(b.inflate)}))'
        else:
            cube += f'.addBox({jf(b.x)}, {jf(b.y)}, {jf(b.z)}, {jf(b.w)}, {jf(b.h)}, {jf(b.d)})'
        if b.mirror:
            cube += '.mirror(false)'
    px, py, pz = part.pivot
    rx, ry, rz = part.rot
    pose = f'PartPose.offsetAndRotation({jf(px)}, {jf(py)}, {jf(pz)}, {jf(rx)}, {jf(ry)}, {jf(rz)})'
    lines.append(f'        PartDefinition {var} = {parent_var}.addOrReplaceChild("{part.name}", {cube}, {pose});')
    for c in part.children:
        emit_part(lines, var, c, depth + 1)


def emit_java(models):
    out = ['package com.astralfall.client.model;', '',
           'import net.minecraft.client.model.geom.PartPose;',
           'import net.minecraft.client.model.geom.builders.*;', '',
           '/** GENERATED by tools/gen_models.py — do not edit by hand. */',
           '@SuppressWarnings("unused")',
           'public final class ModelDefs {', '    private ModelDefs() {}', '']
    for m in models:
        method = ''.join(w.capitalize() for w in m.name.split('_'))
        out.append(f'    public static LayerDefinition create{method}() {{')
        out.append('        MeshDefinition mesh = new MeshDefinition();')
        out.append('        PartDefinition root = mesh.getRoot();')
        lines = []
        for p in m.parts:
            emit_part(lines, 'root', p, 0)
        out.extend(lines)
        out.append(f'        return LayerDefinition.create(mesh, {m.tw}, {m.th});')
        out.append('    }')
        out.append('')
    out.append('}')
    os.makedirs(os.path.dirname(JAVA), exist_ok=True)
    with open(JAVA, 'w') as f:
        f.write('\n'.join(out) + '\n')


def main():
    for m in MODELS:
        pack(m)
        tex = Canvas(m.tw, m.th)
        glow = Canvas(m.tw, m.th)
        for i, b in enumerate(m.boxes()):
            paint_box(tex, glow, b, zlib.crc32(f'{m.name}:{i}'.encode()) % 100000)
        tex.save(os.path.join(TEX, m.name + '.png'))
        glow.save(os.path.join(TEX, m.name + '_glow.png'))
    emit_java(MODELS)
    print('generated', len(MODELS), 'models')


if __name__ == '__main__':
    main()
