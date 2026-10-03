"""Builds the "Tidecaller" box-style pistol for Roblox.

Everything (geometry, pixel-art texture, GLB, OBJ/MTL, Blockbench .bbmodel)
is generated from the box list below, deterministically.

Model space while building = Blockbench space in pixels:
    +X = gun's right side, +Y = up, -Z = barrel direction (north).
At the end everything is shifted so the grip centre is the origin.
GLB/OBJ are written in studs (16 px = 1 stud); the .bbmodel stays in px.

Run:  python3 build_pistol.py      (needs numpy + pillow)
"""
import base64
import io
import json
import math
import os
import random
import struct
import uuid as uuidlib
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
NAME = 'pistol'
TEX = 128            # painted texture size
UPSCALE = 1024       # nearest-neighbour upload size
PX_PER_STUD = 16.0
OUTLINE = 0.5        # inverted-hull inflation, px
PART_ORDER = ['Body', 'Slide', 'Magazine', 'Trigger']

# ---------------------------------------------------------------- palette
# 4 shades per material: highlight, base, shadow, dark
PAL = {
    'teal':   [(127, 245, 230), (25, 199, 190), (14, 140, 145), (7, 80, 94)],
    'char':   [(112, 118, 136), (72, 77, 92), (48, 51, 64), (28, 30, 38)],
    'orange': [(255, 208, 106), (255, 138, 31), (210, 86, 14), (126, 44, 8)],
    'steel':  [(221, 227, 234), (163, 171, 184), (108, 116, 132), (58, 63, 76)],
}
H, B, S, D = range(4)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------- layout
# Side-view design numbers use f = distance forward from the gun's rear (px)
# and y = height above the lowest point (px). Z = -f.
GRIP_ANGLE = 15.0                 # grip rake, degrees (bottom swept back)
GRIP_PIVOT = (0.0, 10.7, -7.0)    # where the grip box hinges into the frame
SLIDE_TRAVEL = 5                  # px the slide moves back when firing


class Box:
    def __init__(self, name, part, mat, frm, to, paint=None, rot_x=0.0, pivot=None):
        self.name, self.part, self.mat = name, part, mat
        self.frm = np.array(frm, float)
        self.to = np.array(to, float)
        self.size = self.to - self.frm
        for v in self.size:
            assert abs(v - round(v)) < 1e-9 and v >= 1, (name, self.size)
        self.paint = paint
        self.rot_x = rot_x
        self.pivot = np.array(pivot if pivot is not None else (self.frm + self.to) / 2, float)


def side_box(name, part, mat, x, y, f, paint=None):
    """x=(x0,x1) y=(y0,y1) f=(f0,f1) forward distances -> Box."""
    return Box(name, part, mat, (x[0], y[0], -f[1]), (x[1], y[1], -f[0]), paint)


def grip_box(name, part, mat, x, v, u, paint=None):
    """Box in grip-local coords: v = up along the grip axis, u = forward,
    both relative to GRIP_PIVOT, then raked by GRIP_ANGLE."""
    px, py, pz = GRIP_PIVOT
    return Box(name, part, mat, (x[0], py + v[0], pz - u[1]), (x[1], py + v[1], pz - u[0]),
               paint, rot_x=-GRIP_ANGLE, pivot=GRIP_PIVOT)


# ---------------------------------------------------------------- painters
# A painter gets a context c and returns (mat, shade) to override the base
# shading, or None.  c.fl / c.yl / c.xl are integer pixel offsets from the
# box's rear / bottom / left edge, so details land in the same place on
# both sides of the gun.

def p_slide(c):
    if c.side and c.fk in ('east', 'west') and 1 <= c.j <= 5:
        if 1 <= c.fl <= 6:                       # rear cocking serrations
            return ('teal', S) if c.fl % 2 == 1 else ('teal', B)
        for k in range(3):                        # 3 vents per side
            a = 12 + 4 * k
            if a <= c.fl <= a + 2:
                if c.j in (2, 3):
                    return ('teal', D)
                if c.j == 4:
                    return ('teal', H)            # lit lower lip of the vent
    if c.fk == 'south' and c.xl == 3 and c.yl == 3:
        return ('teal', D)                        # striker hole
    return None


def p_rib(c):
    if c.fk == 'up':
        return ('teal', H) if c.fl % 2 else ('teal', B)   # anti-glare grooves
    return None


def p_rear_sight(c):
    if c.fk in ('up', 'south', 'north') and c.xl == 2:
        return ('char', D)                        # sight notch
    return None


def p_front_sight(c):
    if c.fk == 'south' and c.j == 0:
        return ('orange', H)
    return None


def p_comp(c):
    if c.fk in ('east', 'west') and c.fl in (2, 4) and 2 <= c.j <= 6:
        return ('char', D)
    if c.fk in ('east', 'west') and c.fl in (2, 4) and c.j == 7:
        return ('char', H)
    if c.fk == 'up' and c.fl in (2, 4) and 2 <= c.xl <= 5:
        return ('char', D)
    if c.fk == 'north':                           # muzzle face: bore
        if 3 <= c.xl <= 4 and 4 <= c.yl <= 5:
            return ('char', D)
        if 2 <= c.xl <= 5 and 3 <= c.yl <= 6:
            return ('char', S)
    return None


def p_frame(c):
    if c.fk in ('east', 'west') and c.j == 1:
        if c.fl == 11:
            return ('char', D)                    # takedown pin
        if c.fl == 12:
            return ('char', H)
    return None


def p_rail(c):
    if c.fk in ('east', 'west', 'down') and c.fl % 2 == 1:
        return ('char', D)                        # rail slots
    return None


def hatch(i, j):
    a, b = (i + j) % 4 == 1, (i - j) % 4 == 1
    if a and b:
        return D
    if a or b:
        return S
    if (i + j) % 4 == 3 and (i - j) % 4 == 3:
        return H                                  # raised diamond centre
    return None


def p_grip(c):
    if c.fk in ('east', 'west', 'south') and 0 < c.i < c.w - 1 and 0 < c.j < c.h - 1:
        s = hatch(c.i, c.j)                       # cross-hatch
        return ('char', s) if s is not None else ('char', B)
    if c.fk == 'north' and 0 < c.j < c.h - 1:     # front strap serrations
        return ('char', S) if c.j % 2 else ('char', B)
    return None


def p_trigger(c):
    if c.fk == 'north' and c.j in (2,):
        return ('orange', S)
    return None


def p_mag(c):
    if c.fk in ('east', 'west') and c.i == 1 and c.j in (2, 4, 6):
        return ('steel', D)                       # witness holes
    return None


# ---------------------------------------------------------------- boxes
X7, X6, X5, X3, X2 = (-3.5, 3.5), (-3, 3), (-2.5, 2.5), (-1.5, 1.5), (-1, 1)
BOXES = [
    # Slide (teal, moves back)
    side_box('slide', 'Slide', 'teal', X7, (13, 20), (2, 27), p_slide),
    side_box('rib', 'Slide', 'teal', X3, (20, 21), (6, 24), p_rib),
    side_box('rear_sight', 'Slide', 'char', X5, (20, 22), (3, 6), p_rear_sight),
    side_box('front_sight', 'Slide', 'orange', X2, (20, 22), (24, 26), p_front_sight),
    # Body: frame, barrel, compensator, rail, guard, tang, grip, magwell
    side_box('frame', 'Body', 'char', X6, (10, 13), (2, 27), p_frame),
    side_box('barrel', 'Body', 'steel', X3, (14.5, 17.5), (8, 28)),
    side_box('compensator', 'Body', 'char', (-4, 4), (11, 21), (27, 34), p_comp),
    side_box('rail', 'Body', 'char', X5, (8, 10), (19, 26), p_rail),
    side_box('guard_front', 'Body', 'char', X3, (6, 10), (16, 18)),
    side_box('guard_bottom', 'Body', 'char', X3, (4, 6), (8, 18)),
    side_box('tang', 'Body', 'char', X5, (10, 12), (0, 2)),
    grip_box('grip', 'Body', 'char', X7, (-8.5, 0.5), (-4, 4), p_grip),
    grip_box('magwell', 'Body', 'char', (-4, 4), (-9, -7), (-4.5, 4.5)),
    # Magazine (drops along the grip axis)
    grip_box('mag_body', 'Magazine', 'steel', (-2, 2), (-9, -1), (-2, 2), p_mag),
    grip_box('mag_base', 'Magazine', 'orange', X6, (-11, -9), (-3.5, 3.5)),
    # Trigger
    side_box('trigger', 'Trigger', 'orange', X2, (7, 11), (12.5, 14.5), p_trigger),
]


# ---------------------------------------------------------------- geometry
def rot_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


FACE_KEYS = ['north', 'east', 'south', 'west', 'up', 'down']


def face_corners(fk, f, t):
    """Blockbench vertex order: TL, TR, BL, BR (as seen from outside)."""
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        'east':  [(x1, y1, z1), (x1, y1, z0), (x1, y0, z1), (x1, y0, z0)],
        'west':  [(x0, y1, z0), (x0, y1, z1), (x0, y0, z0), (x0, y0, z1)],
        'up':    [(x0, y1, z0), (x1, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        'down':  [(x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (x1, y0, z0)],
        'south': [(x0, y1, z1), (x1, y1, z1), (x0, y0, z1), (x1, y0, z1)],
        'north': [(x1, y1, z0), (x0, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    }[fk]


NORMALS = {'east': (1, 0, 0), 'west': (-1, 0, 0), 'up': (0, 1, 0),
           'down': (0, -1, 0), 'south': (0, 0, 1), 'north': (0, 0, -1)}


def to_world(box, pts):
    pts = np.asarray(pts, float)
    if box.rot_x:
        return (pts - box.pivot) @ rot_x(box.rot_x).T + box.pivot
    return pts


# ---------------------------------------------------------------- texture
class Ctx:
    pass


def face_dims(box, fk):
    sx, sy, sz = (int(round(v)) for v in box.size)
    return {'north': (sx, sy), 'south': (sx, sy), 'east': (sz, sy), 'west': (sz, sy),
            'up': (sx, sz), 'down': (sx, sz)}[fk]


def paint_face(box, fk):
    w, h = face_dims(box, fk)
    tl, tr, bl, _ = (np.array(p) for p in face_corners(fk, box.frm, box.to))
    rdir, ddir = (tr - tl) / w, (bl - tl) / h
    kind = 'top' if fk == 'up' else 'bottom' if fk == 'down' else 'side'
    rng = random.Random(zlib.crc32(f'{box.name}:{fk}'.encode()))
    big = w >= 4 and h >= 4
    mats = np.empty((h, w), object)
    shades = np.zeros((h, w), int)
    for j in range(h):
        for i in range(w):
            if kind == 'top':
                s = H
                if big and rng.random() < 0.06:
                    s = B
            elif kind == 'bottom':
                s = S
                if big and rng.random() < 0.06:
                    s = D
            else:
                s = B
                if big and rng.random() < 0.04:
                    s = S
                if h >= 2 and j == 0:
                    s = H                     # 1-px highlight along top edge
                elif h >= 2 and j == h - 1:
                    s = S                     # 1-px shadow along bottom edge
            mats[j, i], shades[j, i] = box.mat, s
            if box.paint:
                p = tl + (i + 0.5) * rdir + (j + 0.5) * ddir
                c = Ctx()
                c.fk, c.i, c.j, c.w, c.h, c.side = fk, i, j, w, h, kind == 'side'
                c.fl = int(math.floor(box.to[2] - p[2]))
                c.yl = int(math.floor(p[1] - box.frm[1]))
                c.xl = int(math.floor(p[0] - box.frm[0]))
                r = box.paint(c)
                if r is not None:
                    mats[j, i], shades[j, i] = r
    img = np.zeros((h, w, 3), np.uint8)
    for j in range(h):
        for i in range(w):
            img[j, i] = PAL[mats[j, i]][shades[j, i]]
    return img


def build_atlas():
    """Shelf-pack every face (1-px edge padding) into a TEX x TEX atlas.
    Returns atlas image, {(box, face): (x, y, w, h)} and black block centre."""
    islands = []
    for b in BOXES:
        for fk in FACE_KEYS:
            img = paint_face(b, fk)
            islands.append((b.name, fk, img))
    atlas = np.zeros((TEX, TEX, 3), np.uint8)
    atlas[:] = (255, 0, 255)   # unused space: magenta, never sampled
    # reserved black outline block, top-left 4x4
    atlas[0:4, 0:4] = BLACK
    black_uv = (2.0, 2.0)
    rects = {}
    order = sorted(islands, key=lambda t: (-(t[2].shape[0] + 2), -(t[2].shape[1] + 2), t[0], t[1]))
    x, y, shelf_h = 4, 0, 4
    for name, fk, img in order:
        h, w = img.shape[:2]
        pw, ph = w + 2, h + 2
        if x + pw > TEX:
            x, y, shelf_h = 0, y + shelf_h, 0
        assert y + ph <= TEX, 'atlas overflow'
        atlas[y:y + ph, x:x + pw] = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode='edge')
        rects[(name, fk)] = (x + 1, y + 1, w, h)
        x += pw
        shelf_h = max(shelf_h, ph)
    used = y + shelf_h
    return atlas, rects, black_uv, used


# ---------------------------------------------------------------- meshes
def build_parts(rects, black_uv, origin):
    """Returns {part: dict(pos, nrm, uv, idx)} in px, origin-shifted.
    Each part = its boxes + inverted-hull shells (same mesh)."""
    parts = {p: {'pos': [], 'nrm': [], 'uv': [], 'idx': [], 'quads': []} for p in PART_ORDER}

    def add_quad(P, corners, normal, uvs, flip):
        base = len(P['pos'])
        tl, tr, bl, br = corners
        P['pos'] += [tl, tr, bl, br]
        P['nrm'] += [normal] * 4
        P['uv'] += uvs
        tris = [(0, 2, 3), (0, 3, 1)]      # CCW from outside
        if flip:
            tris = [(0, 3, 2), (0, 1, 3)]
        for t in tris:
            P['idx'] += [base + k for k in t]

    for b in BOXES:
        P = parts[b.part]
        R = rot_x(b.rot_x)
        for fk in FACE_KEYS:
            x, y, w, h = rects[(b.name, fk)]
            cs = to_world(b, face_corners(fk, b.frm, b.to)) - origin
            n = R @ np.array(NORMALS[fk], float)
            uvs = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
            add_quad(P, [tuple(c) for c in cs], tuple(n), uvs, False)
        # inverted hull: inflate, flip winding + normals, UV -> black block
        f2, t2 = b.frm - OUTLINE, b.to + OUTLINE
        for fk in FACE_KEYS:
            cs = to_world(b, face_corners(fk, f2, t2)) - origin
            n = -(R @ np.array(NORMALS[fk], float))
            add_quad(P, [tuple(c) for c in cs], tuple(n), [black_uv] * 4, True)
            P['quads'].append([tuple(c) for c in cs])
    return parts


def check_winding(parts):
    for name, P in parts.items():
        pos, nrm, idx = np.array(P['pos']), np.array(P['nrm']), np.array(P['idx']).reshape(-1, 3)
        for t in idx:
            a, b, c = pos[t]
            n = np.cross(b - a, c - a)
            assert np.dot(n, nrm[t[0]]) > 0, f'winding/normal mismatch in {name}'


def check_texel_density(parts):
    """Every textured triangle must map 1 texture px to 1 model px on both axes."""
    worst = 0.0
    for P in parts.values():
        pos, uv, idx = np.array(P['pos']), np.array(P['uv']), np.array(P['idx']).reshape(-1, 3)
        for t in idx:
            (a, b, c), (ua, ub, uc) = pos[t], uv[t]
            if np.allclose(ua, ub) and np.allclose(ua, uc):
                continue   # outline shell
            for p, q, up, uq in ((a, b, ua, ub), (b, c, ub, uc), (a, c, ua, uc)):
                ld, lu = np.linalg.norm(p - q), np.linalg.norm(up - uq)
                worst = max(worst, abs(ld - lu))
    assert worst < 1e-6, worst
    return worst


# ---------------------------------------------------------------- writers
def png_bytes(arr):
    bio = io.BytesIO()
    Image.fromarray(arr).save(bio, 'PNG', optimize=True)
    return bio.getvalue()


def write_glb(path, parts, tex_png):
    bin_ = bytearray()
    views, accessors, meshes, nodes = [], [], [], []

    def add_view(data, target=None):
        while len(bin_) % 4:
            bin_.append(0)
        v = {'buffer': 0, 'byteOffset': len(bin_), 'byteLength': len(data)}
        if target:
            v['target'] = target
        bin_.extend(data)
        views.append(v)
        return len(views) - 1

    for name in PART_ORDER:
        P = parts[name]
        pos = (np.array(P['pos'], np.float32) / PX_PER_STUD).astype(np.float32)
        nrm = np.array(P['nrm'], np.float32)
        uv = (np.array(P['uv'], np.float32) / TEX).astype(np.float32)
        idx = np.array(P['idx'], np.uint16)
        a_pos = len(accessors)
        accessors.append({'bufferView': add_view(pos.tobytes(), 34962), 'componentType': 5126,
                          'count': len(pos), 'type': 'VEC3',
                          'min': pos.min(0).tolist(), 'max': pos.max(0).tolist()})
        accessors.append({'bufferView': add_view(nrm.tobytes(), 34962), 'componentType': 5126,
                          'count': len(nrm), 'type': 'VEC3'})
        accessors.append({'bufferView': add_view(uv.tobytes(), 34962), 'componentType': 5126,
                          'count': len(uv), 'type': 'VEC2'})
        accessors.append({'bufferView': add_view(idx.tobytes(), 34963), 'componentType': 5123,
                          'count': len(idx), 'type': 'SCALAR'})
        meshes.append({'name': name, 'primitives': [{
            'attributes': {'POSITION': a_pos, 'NORMAL': a_pos + 1, 'TEXCOORD_0': a_pos + 2},
            'indices': a_pos + 3, 'material': 0}]})
        nodes.append({'name': name, 'mesh': len(meshes) - 1})
    img_view = add_view(tex_png)
    while len(bin_) % 4:
        bin_.append(0)
    gltf = {
        'asset': {'version': '2.0', 'generator': 'build_pistol.py'},
        'scene': 0,
        'scenes': [{'name': 'Pistol', 'nodes': list(range(len(nodes)))}],
        'nodes': nodes,
        'meshes': meshes,
        'materials': [{'name': 'PistolMat', 'doubleSided': False,
                       'pbrMetallicRoughness': {'baseColorTexture': {'index': 0},
                                                'metallicFactor': 0.0, 'roughnessFactor': 1.0}}],
        'textures': [{'sampler': 0, 'source': 0}],
        'samplers': [{'magFilter': 9728, 'minFilter': 9728, 'wrapS': 33071, 'wrapT': 33071}],
        'images': [{'name': f'{NAME}_1024', 'mimeType': 'image/png', 'bufferView': img_view}],
        'accessors': accessors,
        'bufferViews': views,
        'buffers': [{'byteLength': len(bin_)}],
    }
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
        f.write(struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_))


def write_obj(path, parts):
    mtl = os.path.splitext(os.path.basename(path))[0] + '.mtl'
    lines = ['# Tidecaller pistol - units: studs (16 px = 1 stud), Y up, barrel -Z',
             f'mtllib {mtl}']
    vo = 1
    for name in PART_ORDER:
        P = parts[name]
        lines.append(f'o {name}')
        lines.append(f'g {name}')
        for p in P['pos']:
            lines.append('v %.6f %.6f %.6f' % tuple(c / PX_PER_STUD for c in p))
        for u, v in P['uv']:
            lines.append('vt %.6f %.6f' % (u / TEX, 1 - v / TEX))
        for n in P['nrm']:
            lines.append('vn %.6f %.6f %.6f' % tuple(n))
        lines.append('usemtl PistolMat')
        lines.append('s off')
        idx = P['idx']
        for k in range(0, len(idx), 3):
            a, b, c = (vo + idx[k + m] for m in range(3))
            lines.append(f'f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}')
        vo += len(P['pos'])
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(os.path.dirname(path), mtl), 'w') as f:
        f.write('newmtl PistolMat\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nd 1\nillum 1\n'
                f'map_Kd {NAME}_1024.png\n')


def uid(seed):
    return str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, 'tidecaller/' + seed))


def write_bbmodel(path, rects, black_uv, origin, parts, tex_png):
    elements, groups = [], {p: [] for p in PART_ORDER}
    r6 = lambda v: [round(float(a), 6) for a in v]
    for b in BOXES:
        el = {
            'name': b.name, 'box_uv': False, 'rescale': False, 'locked': False,
            'render_order': 'default', 'allow_mirror_modeling': True,
            'from': r6(b.frm - origin), 'to': r6(b.to - origin), 'autouv': 0, 'color': 0,
            'origin': r6(b.pivot - origin), 'faces': {}, 'type': 'cube', 'uuid': uid(b.name),
        }
        if b.rot_x:
            el['rotation'] = [b.rot_x, 0, 0]
        for fk in FACE_KEYS:
            x, y, w, h = rects[(b.name, fk)]
            el['faces'][fk] = {'uv': [x, y, x + w, y + h], 'texture': 0}
        elements.append(el)
        groups[b.part].append(el['uuid'])
    # outline shells as meshes (reversed winding = inverted hull)
    for name in PART_ORDER:
        verts, faces = {}, {}
        for qi, (tl, tr, bl, br) in enumerate(parts[name]['quads']):
            keys = []
            for vi, p in enumerate((tl, bl, br, tr)):     # CCW from outside ...
                k = f'v{qi}_{vi}'
                verts[k] = r6(p)
                keys.append(k)
            keys = keys[::-1]                              # ... reversed -> faces inward
            faces[f'f{qi}'] = {'uv': {k: list(black_uv) for k in keys}, 'vertices': keys, 'texture': 0}
        el = {'name': f'{name}_outline', 'color': 0, 'origin': [0, 0, 0], 'rotation': [0, 0, 0],
              'export': True, 'visibility': True, 'locked': False, 'render_order': 'default',
              'allow_mirror_modeling': True, 'vertices': verts, 'faces': faces,
              'type': 'mesh', 'uuid': uid(name + '_outline')}
        elements.append(el)
        groups[name].append(el['uuid'])
    outliner = [{'name': p, 'origin': [0, 0, 0], 'color': 0, 'uuid': uid('group/' + p),
                 'export': True, 'mirror_uv': False, 'isOpen': True, 'locked': False,
                 'visibility': True, 'autouv': 0, 'children': groups[p]} for p in PART_ORDER]
    model = {
        'meta': {'format_version': '4.10', 'model_format': 'free', 'box_uv': False},
        'name': 'tidecaller_pistol', 'model_identifier': '', 'visible_box': [1, 1, 0],
        'variable_placeholders': '', 'variable_placeholder_buttons': [],
        'timeline_setups': [], 'unhandled_root_fields': {},
        'resolution': {'width': TEX, 'height': TEX},
        'elements': elements, 'outliner': outliner,
        'textures': [{'path': '', 'name': f'{NAME}_128.png', 'folder': '', 'namespace': '',
                      'id': '0', 'width': TEX, 'height': TEX, 'uv_width': TEX, 'uv_height': TEX,
                      'particle': False, 'render_mode': 'default', 'render_sides': 'front',
                      'frame_time': 1, 'frame_order_type': 'loop', 'frame_order': '',
                      'frame_interpolate': False, 'visible': True, 'internal': True,
                      'saved': True, 'uuid': uid('texture'),
                      'source': 'data:image/png;base64,' + base64.b64encode(tex_png).decode()}],
    }
    with open(path, 'w') as f:
        json.dump(model, f, indent=1)


# ---------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    atlas, rects, black_uv, used = build_atlas()
    # origin: centre of the grip where the hand sits (grip-local v=-4, u=0)
    origin = to_world(BOXES[[b.name for b in BOXES].index('grip')],
                      [np.array(GRIP_PIVOT) + (0, -4, 0)])[0]
    parts = build_parts(rects, black_uv, origin)
    check_winding(parts)
    check_texel_density(parts)

    tex128 = png_bytes(atlas)
    big = np.repeat(np.repeat(atlas, UPSCALE // TEX, 0), UPSCALE // TEX, 1)
    tex1024 = png_bytes(big)
    open(os.path.join(OUT, f'{NAME}_128.png'), 'wb').write(tex128)
    open(os.path.join(OUT, f'{NAME}_1024.png'), 'wb').write(tex1024)
    write_glb(os.path.join(OUT, f'{NAME}.glb'), parts, tex1024)
    write_obj(os.path.join(OUT, f'{NAME}.obj'), parts)
    write_bbmodel(os.path.join(OUT, f'{NAME}.bbmodel'), rects, black_uv, origin, parts, tex128)

    # ---- report numbers
    allpos = np.concatenate([np.array(parts[p]['pos']) for p in PART_ORDER])
    solid = []
    for b in BOXES:
        solid.append(to_world(b, [face_corners(fk, b.frm, b.to)[k] for fk in FACE_KEYS for k in range(4)]) - origin)
    solid = np.concatenate(solid)
    size = solid.max(0) - solid.min(0)
    comp = BOXES[[b.name for b in BOXES].index('compensator')]
    muzzle = np.array([0.0, (comp.frm[1] + comp.to[1]) / 2, comp.frm[2]]) - origin
    info = {
        'origin_in_build_space_px': origin.round(4).tolist(),
        'solid_size_px_xyz': size.round(3).tolist(),
        'with_outline_size_px_xyz': (allpos.max(0) - allpos.min(0)).round(3).tolist(),
        'muzzle_tip_px': muzzle.round(4).tolist(),
        'muzzle_tip_studs': (muzzle / PX_PER_STUD).round(4).tolist(),
        'slide_travel_px': SLIDE_TRAVEL,
        'slide_travel_studs': SLIDE_TRAVEL / PX_PER_STUD,
        'mag_drop_dir': (rot_x(-GRIP_ANGLE) @ np.array([0, -1.0, 0])).round(4).tolist(),
        'atlas_rows_used': int(used),
        'parts': {},
    }
    for p in PART_ORDER:
        pp = np.array(parts[p]['pos'])
        mn, mx = pp.min(0), pp.max(0)
        info['parts'][p] = {
            'bbox_center_studs': ((mn + mx) / 2 / PX_PER_STUD).round(4).tolist(),
            'bbox_size_studs': ((mx - mn) / PX_PER_STUD).round(4).tolist(),
            'triangles': len(parts[p]['idx']) // 3,
        }
    trig = BOXES[[b.name for b in BOXES].index('trigger')]
    info['trigger_pivot_studs'] = ((np.array([0, trig.to[1] - 1, (trig.frm[2] + trig.to[2]) / 2]) - origin)
                                   / PX_PER_STUD).round(4).tolist()
    with open(os.path.join(OUT, 'build_info.json'), 'w') as f:
        json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
