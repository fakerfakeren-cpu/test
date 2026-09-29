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
TEX = os.path.join(ROOT, 'src', 'main', 'resources', 'assets', 'rimeheart', 'textures', 'entity')
JAVA = os.path.join(ROOT, 'src', 'main', 'java', 'com', 'rimeheart', 'client', 'model', 'ModelDefs.java')


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
    'wraith_robe': dict(p=pal('#0e1f2e', '#16324a', '#1f4866', '#2b6184'), pattern='tatter'),
    'wraith_hood': dict(p=pal('#0a1622', '#12283b', '#1b3a55', '#25507a'), pattern='noise'),
    'wraith_tatter': dict(p=pal('#16324a', '#1f4866', '#4f8fb8', '#8fd0f0'), pattern='tatter', alpha=210),
    'ice_claw': dict(p=pal('#9fe6ff', '#d8f6ff', '#ffffff'), pattern='gradient', glow=True),
    'crystal_shell': dict(p=pal('#2c6f96', '#4aa3cf', '#8fd8f5', '#d8f6ff'), pattern='facets'),
    'rime_crystal': dict(p=pal('#5fc3ee', '#a8e8ff', '#e8fbff', '#ffffff'), pattern='facets', glow=True),
    'crystal_leg': dict(p=pal('#1d4a66', '#2c6f96', '#4aa3cf'), pattern='segments'),
    'sov_ice': dict(p=pal('#7fb8d8', '#a9d6ee', '#d2eefa', '#f2fbff'), pattern='noise'),
    'sov_armor': dict(p=pal('#1b2f4a', '#274466', '#365c85', '#4a78a6', '#6b98c4'), pattern='plates', trim=pal('#9fe6ff', '#d8f6ff', '#ffffff', '#ffffff')),
    'sov_robe': dict(p=pal('#0f2238', '#16304d', '#1f4266', '#2c5a88'), pattern='noise'),
    'sov_mist': dict(p=pal('#a9d6ee', '#d2eefa', '#ffffff'), pattern='gradient', glow=True, alpha=170),
}


# ------------------------------------------------------------------ model definitions
def frost_wraith():
    def arm(side):
        nm = 'left' if side > 0 else 'right'
        x = 0 if side > 0 else -3
        claw = Part(nm + '_claw', (x + 1.5, 11, 0), boxes=[Box(-1, 0, -1, 2, 3, 2, 'ice_claw')])
        return Part(nm + '_arm', (4.5 * side, 1, 0), rot=(-0.35, 0, -0.12 * side), boxes=[Box(x, 0, -1.5, 3, 11, 3, 'wraith_robe', mirror=side < 0)], children=[claw])
    head = Part('head', (0, 0, 0), boxes=[Box(-3.5, -8, -3.5, 7, 8, 7, 'wraith_hood', feature='wraith_face'),
                                          Box(-4, -8.5, -1, 8, 3, 5, 'wraith_hood')])
    tail2 = Part('tail2', (0, 6, 0), boxes=[Box(-2.5, 0, -1.5, 5, 6, 3, 'wraith_tatter')])
    tail = Part('tail', (0, 10, 0), boxes=[Box(-3.5, 0, -2, 7, 6, 4, 'wraith_tatter')], children=[tail2])
    body = Part('body', (0, 2, 0), boxes=[Box(-4, 0, -2.5, 8, 10, 5, 'wraith_robe', feature='wraith_chest')],
                children=[head, arm(1), arm(-1), tail])
    return Model('frost_wraith', 64, 64, [body])


def shardling():
    legs = []
    for i in range(6):
        side = 1 if i < 3 else -1
        z = (-2.5, 0, 2.5)[i % 3]
        x0 = 0 if side > 0 else -5
        legs.append(Part(f'leg{i}', (3.5 * side, -1, z), rot=(0, 0, 0.55 * side), boxes=[Box(x0, -0.5, -0.5, 5, 1, 1, 'crystal_leg')]))
    spikes = Part('spikes', (0, -3, 0), boxes=[Box(-1, -4, -2, 2, 4, 2, 'rime_crystal'), Box(-2.5, -3, 1, 2, 3, 2, 'rime_crystal'),
                                               Box(1, -3, 0, 2, 3, 2, 'rime_crystal'), Box(-0.5, -2, 2.5, 1, 2, 1, 'rime_crystal')])
    head = Part('head', (0, -1, -4), boxes=[Box(-2.5, -2, -3, 5, 3, 3, 'crystal_shell', feature='shardling_eyes')])
    body = Part('body', (0, 21, 0), boxes=[Box(-3.5, -3, -4, 7, 4, 8, 'crystal_shell')], children=[spikes, head] + legs)
    return Model('shardling', 64, 32, [body])


def frost_sovereign():
    def arm(side):
        nm = 'left' if side > 0 else 'right'
        claws = [Box(-3 + i * 2.2, 5, -2.5, 1.5, 4, 1.5, 'rime_crystal') for i in range(3)]
        hand = Part(nm + '_hand', (0, 12, 0), boxes=[Box(-3, 0, -3, 6, 5, 6, 'sov_ice')] + claws)
        fore = Part(nm + '_forearm', (0, 12, 0), boxes=[Box(-3.5, 0, -3.5, 7, 12, 7, 'sov_armor')], children=[hand])
        return Part(nm + '_arm', (11 * side, -12, 0), rot=(0, 0, -0.12 * side), boxes=[Box(-3, 0, -3, 6, 12, 6, 'sov_ice')], children=[fore])
    crown = [Box(-5, -15, -5, 2, 5, 2, 'rime_crystal'), Box(-1, -18, -5, 2, 8, 2, 'rime_crystal'), Box(3, -15, -5, 2, 5, 2, 'rime_crystal'),
             Box(-4, -14, 3, 2, 4, 2, 'rime_crystal'), Box(2, -14, 3, 2, 4, 2, 'rime_crystal'), Box(-5.5, -11, -5.5, 11, 1, 11, 'sov_armor')]
    head = Part('head', (0, -14, 0), boxes=[Box(-5, -10, -5, 10, 10, 10, 'sov_ice', feature='sov_face')] + crown)
    skirt3 = Part('skirt3', (0, 8, 0), boxes=[Box(-3, 0, -2, 6, 6, 4, 'sov_mist')])
    skirt2 = Part('skirt2', (0, 8, 0), boxes=[Box(-5, 0, -3, 10, 8, 6, 'sov_mist')], children=[skirt3])
    skirt = Part('skirt', (0, 6, 0), boxes=[Box(-7, 0, -4, 14, 8, 8, 'sov_robe')], children=[skirt2])
    body = Part('body', (0, -8, 0), boxes=[Box(-8, -14, -4.5, 16, 14, 9, 'sov_armor', feature='sov_chest'), Box(-6, 0, -3.5, 12, 6, 7, 'sov_robe')],
                children=[head, arm(1), arm(-1), skirt,
                          Part('left_pauldron', (10, -13, 0), boxes=[Box(-2, -4, -4, 8, 6, 8, 'sov_armor'), Box(1, -10, -1, 2, 6, 2, 'rime_crystal'), Box(4, -8, 1.5, 2, 4, 2, 'rime_crystal')]),
                          Part('right_pauldron', (-10, -13, 0), boxes=[Box(-6, -4, -4, 8, 6, 8, 'sov_armor'), Box(-3, -10, -1, 2, 6, 2, 'rime_crystal'), Box(-6, -8, 1.5, 2, 4, 2, 'rime_crystal')])])
    shards = []
    for i in range(6):
        a = i * math.pi / 3
        shards.append(Part(f'shard{i}', (round(math.cos(a) * 18, 1), round(math.sin(i * 1.7) * 3, 1), round(math.sin(a) * 18, 1)), boxes=[Box(-1, -4, -1, 2, 8, 2, 'rime_crystal')]))
    orbit = Part('orbit', (0, -18, 0), children=shards)
    return Model('frost_sovereign', 128, 128, [body, orbit])


MODELS = [frost_wraith(), shardling(), frost_sovereign()]


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


def fx_wraith_face(tex, glow, r, rects):
    x, y, w, h = r
    for yy in range(2, h - 1):
        for xx in range(1, w - 1):
            tex.set(x + xx, y + yy, hexc('#03070c'))
    for ex in (2, 4):
        tex.set(x + ex, y + 4, hexc('#bff4ff'))
        glow.set(x + ex, y + 4, hexc('#9fe6ff'))
        tex.set(x + ex, y + 5, hexc('#4fc3ee'))
        glow.set(x + ex, y + 5, hexc('#4fc3ee'))


def fx_wraith_chest(tex, glow, r, rects):
    x, y, w, h = r
    for i in range(4):
        tex.set(x + w // 2 - 1 + (i % 2), y + 2 + i, hexc('#8fd0f0'))
        glow.set(x + w // 2 - 1 + (i % 2), y + 2 + i, hexc('#8fd0f0'))


def fx_shardling_eyes(tex, glow, r, rects):
    x, y, w, h = r
    for (ex, ey) in ((1, 1), (3, 1), (0, 2), (4, 2)):
        if ex < w and ey < h:
            tex.set(x + ex, y + ey, hexc('#e8fbff'))
            glow.set(x + ex, y + ey, hexc('#9fe6ff'))


def fx_sov_face(tex, glow, r, rects):
    x, y, w, h = r
    for ex in (2, 6):
        for dx in (0, 1):
            tex.set(x + ex + dx, y + 4, hexc('#ffffff'))
            glow.set(x + ex + dx, y + 4, hexc('#9fe6ff'))
            tex.set(x + ex + dx, y + 5, hexc('#5fc3ee'))
            glow.set(x + ex + dx, y + 5, hexc('#5fc3ee'))
    for xx in range(3, w - 3):
        tex.set(x + xx, y + 8, hexc('#274466'))
    for yy in range(1, 4):
        tex.set(x + w // 2, y + yy, hexc('#d2eefa'))


def fx_sov_chest(tex, glow, r, rects):
    x, y, w, h = r
    cx, cy = w // 2, 6
    for yy in range(h):
        for xx in range(w):
            d = abs(xx - cx + 0.5) + abs(yy - cy)
            if d <= 3:
                c = hexc('#ffffff') if d <= 1 else hexc('#9fe6ff')
                tex.set(x + xx, y + yy, c)
                glow.set(x + xx, y + yy, c)
    for i in range(5):
        tex.set(x + 2 + i, y + 10 + i // 2, hexc('#9fe6ff'))
        glow.set(x + 2 + i, y + 10 + i // 2, hexc('#9fe6ff'))
        tex.set(x + w - 3 - i, y + 10 + i // 2, hexc('#9fe6ff'))
        glow.set(x + w - 3 - i, y + 10 + i // 2, hexc('#9fe6ff'))


FEATURES = {
    'wraith_face': fx_wraith_face, 'wraith_chest': fx_wraith_chest, 'shardling_eyes': fx_shardling_eyes,
    'sov_face': fx_sov_face, 'sov_chest': fx_sov_chest,
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
    out = ['package com.rimeheart.client.model;', '',
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
