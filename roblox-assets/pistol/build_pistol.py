#!/usr/bin/env python3
"""
Box-built pixel-art pistol ("Tealback") for Roblox.

Everything is generated from the BOX TABLE below:
  * 128x128 hand-shaded texture (1 texel = 1 model unit on every face) + 1024 nearest upscale
  * per-part inverted-hull outline shells, UV-mapped to a black block in the same texture
  * pistol.glb (1024 texture embedded), pistol.obj/.mtl, pistol.bbmodel
  * preview renders (side/top/front/3-4, with and without outlines, plus an action pose)

Units: 1 px = 1 model unit. Exported meshes are in studs (16 px = 1 stud).
Axes: +Y up, barrel along -Z, +X = shooter's right. Origin = centre of the grip.

Run:  python3 build_pistol.py      (needs numpy + pillow)
"""
import base64
import json
import math
import os
import struct
import uuid

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
PREV = os.path.join(HERE, "previews")

PX_PER_STUD = 16.0
TEX = 128            # painted texture size
UPSCALE = 1024       # nearest-neighbour upload size for Roblox
OUTLINE = 0.5        # inverted-hull inflation, in px
RAKE_DEG = -15.0     # grip rotation about X (negative = bottom of grip goes back, toward +Z)
SEED = 7

# ----------------------------------------------------------------------------
# Palette: 4 shades per material  (highlight, base, shadow, dark)
# ----------------------------------------------------------------------------
HL, BASE, SH, DK = 0, 1, 2, 3
PAL = {
    "teal":   [(126, 246, 226), (24, 196, 182), (12, 128, 136), (8, 62, 78)],
    "char":   [(104, 110, 128), (66, 70, 84), (42, 45, 56), (22, 23, 31)],
    "orange": [(255, 206, 92), (255, 132, 18), (206, 78, 8), (128, 38, 6)],
}
MATS = list(PAL)
BLACK = (0, 0, 0)

# ----------------------------------------------------------------------------
# Frames.  "world": design coords (x, y, z) with z = -f (f = distance forward
# from the slide's rear face).  "grip": local coords rotated RAKE_DEG about X and
# placed at GRIP_PIVOT.  Final coords = design - ORIGIN.
# ----------------------------------------------------------------------------
GRIP_PIVOT = np.array([0.0, -2.0, -7.0])
ORIGIN = np.array([0.0, -6.5, -6.0])     # centre of the grip where the hand holds it


def rot_x(deg):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


R_GRIP = rot_x(RAKE_DEG)
FRAMES = {
    "world": (np.zeros(3), np.eye(3)),
    "grip": (GRIP_PIVOT, R_GRIP),
}


def to_world(frame, p):
    piv, R = FRAMES[frame]
    return piv + np.asarray(p) @ R.T


# ----------------------------------------------------------------------------
# BOX TABLE
#   world boxes: x=(x0,x1) y=(y0,y1) f=(f0,f1)  (f = forward distance)
#   grip boxes : x, y, z in grip-local coords (local -z = forward)
# ----------------------------------------------------------------------------
class Box:
    def __init__(self, name, part, mat, x, y, z, frame="world", paint=None):
        self.name, self.part, self.mat, self.frame, self.paint = name, part, mat, frame, paint
        self.lo = np.array([x[0], y[0], z[0]], float)
        self.hi = np.array([x[1], y[1], z[1]], float)
        assert np.all(self.hi > self.lo), name
        assert np.allclose(np.round((self.hi - self.lo)), self.hi - self.lo), f"{name}: non-integer size"

    def contains_world(self, p, eps=1e-6):
        piv, R = FRAMES[self.frame]
        q = (np.asarray(p) - piv) @ R      # world -> local
        return bool(np.all(q >= self.lo - eps) and np.all(q <= self.hi + eps))


def W(name, part, mat, x, y, f, paint=None):
    return Box(name, part, mat, x, y, (-f[1], -f[0]), "world", paint)


def G(name, part, mat, x, y, z, paint=None):
    return Box(name, part, mat, x, y, z, "grip", paint)


# ---------------- painters: fn(face, pts, mat, shade) mutate mat/shade grids ----
# pts[r, c] = design-space (x, y, z) of the texel centre; f = -z.

def p_slide(face, P, M, S):
    x, y, f = P[..., 0], P[..., 1], -P[..., 2]
    if face in ("east", "west"):
        # rear serrations: 3 dark grooves
        m = (f > 1) & (f < 7) & (np.floor(f) % 2 == 1) & (y > 1) & (y < 5)
        S[m] = DK
        # 3 vents per side near the muzzle
        for f0 in (17, 20, 23):
            v = (f > f0) & (f < f0 + 2) & (y > 1) & (y < 4)
            S[v] = DK
            S[v & (y < 2)] = SH
    elif face == "north":            # slide front (seen when the slide is back)
        S[(np.abs(x) < 2) & (y > 0) & (y < 6)] = DK
    elif face == "south":            # rear plate: striker slot
        S[(np.abs(x) < 0.6) & (y > 2) & (y < 4)] = DK
    elif face == "up":
        # base-coloured strip beside the rib so the rib reads as raised
        S[(np.abs(x) > 1.4) & (np.abs(x) < 2.1)] = BASE


def p_rib(face, P, M, S):
    f = -P[..., 2]
    if face == "up":
        S[(np.floor(f) % 2 == 0) & (np.abs(P[..., 0]) < 0.6)] = BASE   # anti-glare dashes


def p_rear_sight(face, P, M, S):
    x, y = P[..., 0], P[..., 1]
    if face in ("south", "up", "north"):
        S[np.abs(x) < 0.6] = DK                                       # U notch
    if face == "south":
        S[(np.abs(x) > 0.6) & (np.abs(x) < 1.6) & (y < 7)] = BASE


def p_front_sight(face, P, M, S):
    x, y = P[..., 0], P[..., 1]
    if face == "south":                                               # bright dot facing the shooter
        S[:] = BASE
        S[(np.abs(x) < 0.6) & (y > 8)] = HL


def p_comp(face, P, M, S):
    x, y, f = P[..., 0], P[..., 1], -P[..., 2]
    if face == "north":                                               # oversized muzzle
        S[(np.abs(x) < 2.5) & (y > 0) & (y < 6)] = SH
        S[(np.abs(x) < 1.5) & (y > 1) & (y < 5)] = DK
    elif face == "up":                                                # 2 top ports
        for f0 in (28, 30):
            S[(f > f0) & (f < f0 + 1) & (np.abs(x) < 2.5)] = DK
    elif face in ("east", "west"):
        S[(f > 27) & (f < 28) & (y > 0) & (y < 6)] = DK              # seam to slide
        for f0 in (29, 31):
            S[(f > f0) & (f < f0 + 1) & (y > 2) & (y < 5)] = DK      # side ports


def p_dustcover(face, P, M, S):
    x, y, f = P[..., 0], P[..., 1], -P[..., 2]
    if face in ("east", "west"):
        S[(f > 15) & (f < 16) & (y > -2) & (y < -1)] = DK             # takedown pin
        S[(f > 16) & (f < 17) & (y > -2) & (y < -1)] = HL
    if face == "north":
        S[(y > -1)] = SH


def p_receiver(face, P, M, S):
    x, y, f = P[..., 0], P[..., 1], -P[..., 2]
    if face in ("east", "west"):
        S[(f > 9) & (f < 12) & (y > -2) & (y < -1)] = DK               # slide stop lever
        S[(f > 9) & (f < 12) & (y > -1) & (y < 0)] = BASE
        S[(f > 3) & (f < 4) & (y > -2) & (y < -1)] = DK                # pin
        S[(f > 4) & (f < 5) & (y > -2) & (y < -1)] = HL


def p_rail(face, P, M, S):
    f = -P[..., 2]
    if face in ("east", "west", "down"):
        S[(np.floor(f) % 2 == 0) & (S != HL)] = DK                     # rail slots


def p_grip(face, P, M, S, local=None):
    # cross-hatch on the grip panels, painted in texel space
    h, w = S.shape
    r, c = np.mgrid[0:h, 0:w]
    if face in ("east", "west", "north", "south"):
        a, b = (r + c) % 4 == 0, (r - c) % 4 == 0
        inner = (r >= 1) & (r <= h - 2) & (c >= 1) & (c <= w - 2)
        S[inner] = BASE
        S[inner & (a | b)] = SH
        S[inner & a & b] = DK


def p_flare(face, P, M, S):
    if face == "down":                                                # magwell opening
        x, z = P[..., 0], P[..., 2]
        loc = (P - GRIP_PIVOT) @ R_GRIP
        lx, lz = loc[..., 0], loc[..., 2]
        S[(np.abs(lx) < 2.5) & (np.abs(lz) < 4)] = SH
        S[(np.abs(lx) < 2) & (np.abs(lz) < 3.5)] = DK


def p_mag_body(face, P, M, S):
    h, w = S.shape
    if face in ("east", "west"):
        r, c = np.mgrid[0:h, 0:w]
        S[(c == w // 2) & (r % 2 == 1) & (r > 0) & (r < h - 1)] = DK  # witness holes
    if face == "up":
        S[:] = DK
        M[1:-1, 1:-1] = MATS.index("orange")                        # top round
        S[1:-1, 1:-1] = SH


def p_trigger(face, P, M, S):
    x = P[..., 0]
    h, w = S.shape
    if face == "north":
        S[1:h - 1, :][np.abs(x[1:h - 1, :]) < 0.6] = DK              # trigger safety blade


BOXES = [
    # ---------------- Slide (teal + orange front sight) -------------------
    W("slide_main",  "Slide", "teal",   (-3.5, 3.5), (0, 6), (0, 27), p_slide),
    W("slide_rib",   "Slide", "teal",   (-1.5, 1.5), (6, 7), (3, 25), p_rib),
    W("rear_sight",  "Slide", "teal",   (-2.5, 2.5), (6, 8), (1, 3), p_rear_sight),
    W("front_sight", "Slide", "orange", (-1.5, 1.5), (7, 9), (22, 24), p_front_sight),
    # ---------------- Body: frame, barrel/compensator, grip --------------
    W("receiver",    "Body", "char", (-4.5, 4.5), (-4, 0), (-1, 13), p_receiver),
    W("dust_cover",  "Body", "char", (-3.5, 3.5), (-4, 0), (13, 27), p_dustcover),
    W("rail",        "Body", "char", (-2.5, 2.5), (-6, -4), (22, 27), p_rail),
    W("guard_front", "Body", "char", (-2.5, 2.5), (-8, -4), (18, 20)),
    W("guard_bottom", "Body", "char", (-2.5, 2.5), (-10, -8), (9, 20)),
    W("barrel",      "Body", "teal", (-1.5, 1.5), (1, 5), (19, 27)),
    W("compensator", "Body", "teal", (-4.5, 4.5), (-1, 7), (27, 33), p_comp),
    G("grip",        "Body", "char", (-3.5, 3.5), (-7.5, 0.5), (-5, 5), p_grip),
    G("magwell",     "Body", "char", (-4.5, 4.5), (-9.5, -7.5), (-5, 6), p_flare),
    # ---------------- Magazine (in grip frame, drops along grip axis) ----
    G("mag_body",    "Magazine", "char",   (-2, 2), (-9.5, -0.5), (-3.5, 3.5), p_mag_body),
    G("mag_base",    "Magazine", "orange", (-3, 3), (-11.5, -9.5), (-5, 5)),
    # ---------------- Trigger ---------------------------------------------
    W("trigger",     "Trigger", "orange", (-1.5, 1.5), (-7, -3), (14, 16), p_trigger),
]
PARTS = ["Body", "Slide", "Magazine", "Trigger"]

# ----------------------------------------------------------------------------
# Faces in Blockbench convention: corners TL, TR, BL, BR as seen from outside,
# texture-up = +Y for side faces, up: top=-Z, down: top=+Z.  (Matches
# THREE.BoxGeometry/Blockbench cube UV layout, so the .bbmodel lines up.)
# ----------------------------------------------------------------------------
FACE_NAMES = ["east", "west", "up", "down", "south", "north"]


def face_corners(lo, hi, face):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    return {
        "east":  [(x1, y1, z1), (x1, y1, z0), (x1, y0, z1), (x1, y0, z0)],
        "west":  [(x0, y1, z0), (x0, y1, z1), (x0, y0, z0), (x0, y0, z1)],
        "up":    [(x0, y1, z0), (x1, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "down":  [(x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x0, y0, z1), (x1, y0, z1)],
        "north": [(x1, y1, z0), (x0, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    }[face]


class Face:
    pass


def build_faces():
    faces = []
    for b in BOXES:
        for fn in FACE_NAMES:
            loc = np.array(face_corners(b.lo, b.hi, fn), float)
            wc = np.array([to_world(b.frame, p) for p in loc])
            w = int(round(np.linalg.norm(loc[1] - loc[0])))
            h = int(round(np.linalg.norm(loc[2] - loc[0])))
            n = np.cross(wc[2] - wc[0], wc[3] - wc[0])
            n /= np.linalg.norm(n)
            centre = to_world(b.frame, (b.lo + b.hi) / 2)
            assert np.dot(n, wc.mean(0) - centre) > 0, (b.name, fn)
            # texel centres in world space
            cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
            pts = (wc[0][None, None] + (cc[..., None] / w) * (wc[1] - wc[0])
                   + (rr[..., None] / h) * (wc[2] - wc[0]))
            # hidden if every texel (nudged outward) is inside another box of the same part
            probe = pts + n * 0.05
            others = [o for o in BOXES if o is not b and o.part == b.part]
            hidden = all(any(o.contains_world(p) for o in others) for p in probe.reshape(-1, 3))
            if hidden:
                continue
            fc = Face()
            fc.box, fc.name, fc.w, fc.h, fc.world, fc.normal, fc.pts = b, fn, w, h, wc, n, pts
            faces.append(fc)
    return faces


# ----------------------------------------------------------------------------
# Texture painting
# ----------------------------------------------------------------------------
def paint_face(fc, rng):
    w, h = fc.w, fc.h
    M = np.full((h, w), MATS.index(fc.box.mat), int)
    ny = fc.normal[1]
    if ny > 0.7:
        kind = "top"
        S = np.full((h, w), HL, int)
    elif ny < -0.7:
        kind = "bottom"
        S = np.full((h, w), SH, int)
    else:
        kind = "side"
        S = np.full((h, w), BASE, int)
        if h >= 2:
            S[0, :] = HL           # 1-px highlight along the top edge
            S[-1, :] = SH          # 1-px shadow along the bottom edge
    # subtle pixel noise on big flat areas (interior only)
    if w * h >= 40 and min(w, h) >= 5:
        inner = np.zeros((h, w), bool)
        inner[1:-1, 1:-1] = True
        noise = rng.random((h, w)) < 0.035
        to = {"top": BASE, "side": SH, "bottom": DK}[kind]
        S[inner & noise] = to
    if fc.box.paint:
        fc.box.paint(fc.name, fc.pts, M, S)
    img = np.zeros((h, w, 3), np.uint8)
    for mi, m in enumerate(MATS):
        for si in range(4):
            img[(M == mi) & (S == si)] = PAL[m][si]
    fc.kind = kind
    return img


def pack(faces, black_size=8):
    """Shelf-pack each face island with a 1-px pad on every side."""
    items = [(f.h + 2, f.w + 2, i) for i, f in enumerate(faces)]
    items.append((black_size + 2, black_size + 2, -1))
    items.sort(key=lambda t: (-t[0], -t[1]))
    x = y = shelf_h = 0
    pos = {}
    for hh, ww, i in items:
        if x + ww > TEX:
            x, y = 0, y + shelf_h
            shelf_h = 0
        pos[i] = (x + 1, y + 1)
        x += ww
        shelf_h = max(shelf_h, hh)
    assert y + shelf_h <= TEX, f"texture overflow ({y + shelf_h} > {TEX})"
    return pos, y + shelf_h


def build_texture(faces):
    rng = np.random.default_rng(SEED)
    pos, used_h = pack(faces)
    tex = np.zeros((TEX, TEX, 3), np.uint8)    # unused space = black
    for i, fc in enumerate(faces):
        img = paint_face(fc, rng)
        u, v = pos[i]
        fc.uv0 = (u, v)
        padded = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode="edge")  # pad = edge colour
        tex[v - 1:v + fc.h + 1, u - 1:u + fc.w + 1] = padded
    bu, bv = pos[-1]
    tex[bv - 1:bv + 9, bu - 1:bu + 9] = BLACK
    black_uv = ((bu + 4) / TEX, (bv + 4) / TEX)
    return tex, black_uv, used_h


# ----------------------------------------------------------------------------
# Inverted hull: union of the part's boxes inflated by OUTLINE (exact on a 0.5 grid),
# greedy-meshed, normals pointing inward.  One union per frame (world / grip).
# ----------------------------------------------------------------------------
def greedy(mask):
    m = mask.copy()
    out = []
    H, Wd = m.shape
    for i in range(H):
        j = 0
        while j < Wd:
            if m[i, j]:
                w = 1
                while j + w < Wd and m[i, j + w]:
                    w += 1
                h = 1
                while i + h < H and m[i + h, j:j + w].all():
                    h += 1
                m[i:i + h, j:j + w] = False
                out.append((i, j, h, w))
                j += w
            else:
                j += 1
    return out


def hull_quads(boxes, infl=OUTLINE, step=0.5):
    lo = np.min([b.lo for b in boxes], 0) - infl - step
    hi = np.max([b.hi for b in boxes], 0) + infl + step
    dims = np.round((hi - lo) / step).astype(int)
    vox = np.zeros(dims, bool)
    for b in boxes:
        a = np.round((b.lo - infl - lo) / step).astype(int)
        c = np.round((b.hi + infl - lo) / step).astype(int)
        vox[a[0]:c[0], a[1]:c[1], a[2]:c[2]] = True
    quads = []   # (4 corners local, outward normal local)
    for ax in range(3):
        b1, b2 = [a for a in range(3) if a != ax]
        v = np.moveaxis(vox, ax, 0)
        pad = np.concatenate([np.zeros((1,) + v.shape[1:], bool), v, np.zeros((1,) + v.shape[1:], bool)])
        for k in range(pad.shape[0] - 1):
            below, above = pad[k], pad[k + 1]
            for sign, mask in ((+1, below & ~above), (-1, above & ~below)):
                if not mask.any():
                    continue
                for i, j, h, w in greedy(mask):
                    corners = []
                    for di, dj in ((0, 0), (h, 0), (h, w), (0, w)):
                        p = np.zeros(3)
                        p[ax] = lo[ax] + k * step
                        p[b1] = lo[b1] + (i + di) * step
                        p[b2] = lo[b2] + (j + dj) * step
                        corners.append(p)
                    n = np.zeros(3)
                    n[ax] = sign
                    quads.append((np.array(corners), n))
    return quads


# ----------------------------------------------------------------------------
# Mesh assembly
# ----------------------------------------------------------------------------
def build_meshes(faces, black_uv):
    meshes = {}
    for part in PARTS:
        P, N, UV, T = [], [], [], []
        Pn, Nn, UVn, Tn = [], [], [], []    # without hull, for previews
        for fc in [f for f in faces if f.box.part == part]:
            u, v = fc.uv0
            uvs = [(u, v), (u + fc.w, v), (u, v + fc.h), (u + fc.w, v + fc.h)]
            for (PP, NN, UU, TT) in ((P, N, UV, T), (Pn, Nn, UVn, Tn)):
                base = len(PP)
                for c, t in zip(fc.world, uvs):
                    PP.append(c - ORIGIN)
                    NN.append(fc.normal)
                    UU.append((t[0] / TEX, t[1] / TEX))
                TT += [(base, base + 2, base + 3), (base, base + 3, base + 1)]
        nreal = len(T)
        for frame in ("world", "grip"):
            group = [b for b in BOXES if b.part == part and b.frame == frame]
            if not group:
                continue
            piv, R = FRAMES[frame]
            for corners, n in hull_quads(group):
                wc = np.array([to_world(frame, c) for c in corners]) - ORIGIN
                inward = -(R @ n)
                # order so the geometric normal faces inward (flipped hull)
                if np.dot(np.cross(wc[1] - wc[0], wc[2] - wc[0]), inward) < 0:
                    wc = wc[::-1]
                base = len(P)
                for c in wc:
                    P.append(c)
                    N.append(inward)
                    UV.append(black_uv)
                T += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
        meshes[part] = {
            "pos": np.array(P, np.float32), "nrm": np.array(N, np.float32),
            "uv": np.array(UV, np.float32), "tri": np.array(T, np.uint32), "nreal": nreal,
            "plain": {"pos": np.array(Pn, np.float32), "nrm": np.array(Nn, np.float32),
                      "uv": np.array(UVn, np.float32), "tri": np.array(Tn, np.uint32)},
        }
    return meshes


# ----------------------------------------------------------------------------
# Exporters
# ----------------------------------------------------------------------------
def write_glb(path, meshes, png_bytes):
    bin_ = bytearray()
    views, accessors, gl_meshes, nodes = [], [], [], []

    def add_view(data, target=None):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(data)
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target:
            v["target"] = target
        views.append(v)
        return len(views) - 1

    def add_acc(arr, comp, typ, target, minmax=False):
        vi = add_view(arr.tobytes(), target)
        a = {"bufferView": vi, "componentType": comp, "count": int(arr.shape[0]), "type": typ}
        if minmax:
            a["min"] = arr.min(0).tolist()
            a["max"] = arr.max(0).tolist()
        accessors.append(a)
        return len(accessors) - 1

    for part in PARTS:
        m = meshes[part]
        pos = (m["pos"] / PX_PER_STUD).astype(np.float32)
        ip = add_acc(pos, 5126, "VEC3", 34962, True)
        inn = add_acc(m["nrm"].astype(np.float32), 5126, "VEC3", 34962)
        iu = add_acc(m["uv"].astype(np.float32), 5126, "VEC2", 34962)
        ii = add_acc(m["tri"].reshape(-1).astype(np.uint32), 5125, "SCALAR", 34963)
        gl_meshes.append({"name": part, "primitives": [{
            "attributes": {"POSITION": ip, "NORMAL": inn, "TEXCOORD_0": iu},
            "indices": ii, "material": 0, "mode": 4}]})
        nodes.append({"name": part, "mesh": len(gl_meshes) - 1})
    img_view = add_view(png_bytes)
    gltf = {
        "asset": {"version": "2.0", "generator": "build_pistol.py"},
        "scene": 0,
        "scenes": [{"name": "Pistol", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gl_meshes,
        "materials": [{"name": "PistolMat", "doubleSided": False,
                       "pbrMetallicRoughness": {"baseColorTexture": {"index": 0},
                                                "metallicFactor": 0.0, "roughnessFactor": 1.0}}],
        "textures": [{"sampler": 0, "source": 0}],
        "samplers": [{"magFilter": 9728, "minFilter": 9984, "wrapS": 33071, "wrapT": 33071}],
        "images": [{"name": "pistol_1024", "mimeType": "image/png", "bufferView": img_view}],
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": 0}],
    }
    while len(bin_) % 4:
        bin_.append(0)
    gltf["buffers"][0]["byteLength"] = len(bin_)
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, total))
        fh.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        fh.write(struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_))


def write_obj(path, mtl_path, meshes, tex_name):
    lines = ["# Tealback pistol - units: studs (16 px = 1 stud), +Y up, barrel -Z",
             f"mtllib {os.path.basename(mtl_path)}"]
    off = 1
    for part in PARTS:
        m = meshes[part]
        lines.append(f"o {part}")
        lines.append(f"g {part}")
        for p in m["pos"] / PX_PER_STUD:
            lines.append("v %.6f %.6f %.6f" % tuple(p))
        for t in m["uv"]:
            lines.append("vt %.6f %.6f" % (t[0], 1.0 - t[1]))
        for n in m["nrm"]:
            lines.append("vn %.6f %.6f %.6f" % tuple(n))
        lines.append("usemtl PistolMat")
        lines.append("s off")
        for a, b, c in m["tri"] + off:
            lines.append(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}")
        off += len(m["pos"])
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(mtl_path, "w") as fh:
        fh.write("newmtl PistolMat\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nNs 0\nd 1\nillum 1\n"
                 f"map_Kd {tex_name}\n")


def write_bbmodel(path, faces, png128_bytes):
    def uid():
        return str(uuid.uuid4())
    by_box = {}
    for fc in faces:
        by_box.setdefault(fc.box.name, {})[fc.name] = fc
    elements, groups = [], {p: [] for p in PARTS}
    for b in BOXES:
        piv, R = FRAMES[b.frame]
        if b.frame == "world":
            frm, to, origin, rot = b.lo - ORIGIN, b.hi - ORIGIN, [0, 0, 0], [0, 0, 0]
        else:
            frm, to = piv + b.lo - ORIGIN, piv + b.hi - ORIGIN
            origin, rot = (piv - ORIGIN).tolist(), [RAKE_DEG, 0, 0]
        fdict = {}
        for fn in FACE_NAMES:
            fc = by_box.get(b.name, {}).get(fn)
            if fc is None:   # hidden face: no texture
                fdict[fn] = {"uv": [0, 0, 0, 0], "texture": None}
            else:
                u, v = fc.uv0
                fdict[fn] = {"uv": [u, v, u + fc.w, v + fc.h], "texture": 0}
        e = {"name": b.name, "box_uv": False, "rescale": False, "locked": False,
             "render_order": "default", "allow_mirror_modeling": True,
             "from": [float(x) for x in frm], "to": [float(x) for x in to],
             "autouv": 0, "color": PARTS.index(b.part), "origin": [float(x) for x in origin],
             "rotation": [float(x) for x in rot], "faces": fdict, "type": "cube", "uuid": uid()}
        elements.append(e)
        groups[b.part].append(e["uuid"])
    outliner = []
    for part in PARTS:
        outliner.append({"name": part, "origin": [0, 0, 0], "color": PARTS.index(part), "uuid": uid(),
                         "export": True, "mirror_uv": False, "isOpen": True, "locked": False,
                         "visibility": True, "autouv": 0, "children": groups[part]})
    model = {
        "meta": {"format_version": "4.10", "model_format": "free", "box_uv": False},
        "name": "tealback_pistol",
        "model_identifier": "",
        "visible_box": [1, 1, 0],
        "variable_placeholders": "",
        "variable_placeholder_buttons": [],
        "timeline_setups": [],
        "unhandled_root_fields": {},
        "resolution": {"width": TEX, "height": TEX},
        "elements": elements,
        "outliner": outliner,
        "textures": [{
            "path": "", "name": "pistol_128.png", "folder": "", "namespace": "", "id": "0",
            "group": "", "width": TEX, "height": TEX, "uv_width": TEX, "uv_height": TEX,
            "particle": False, "use_as_default": True, "layers_enabled": False,
            "sync_to_project": "", "render_mode": "default", "render_sides": "auto",
            "frame_time": 1, "frame_order_type": "loop", "frame_order": "", "frame_interpolate": False,
            "visible": True, "internal": True, "saved": True, "uuid": uid(),
            "source": "data:image/png;base64," + base64.b64encode(png128_bytes).decode(),
        }],
        "animations": [],
    }
    with open(path, "w") as fh:
        json.dump(model, fh, indent=1)


# ----------------------------------------------------------------------------
# Software preview renderer (orthographic, back-face culled, nearest texture)
# ----------------------------------------------------------------------------
def look_basis(yaw, pitch):
    """Camera looking at the origin. yaw/pitch in degrees; yaw=90 -> looking from +X."""
    y, p = math.radians(yaw), math.radians(pitch)
    eye = np.array([math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)])
    fwd = -eye
    up0 = np.array([0, 1.0, 0]) if abs(p) < math.radians(89) else np.array([0, 0, -1.0])
    right = np.cross(fwd, up0)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd


def render(mesh_list, tex, basis, size=(900, 640), bg=(205, 214, 224), scale=None, ss=2):
    right, up, fwd = basis
    W_, H_ = size[0] * ss, size[1] * ss
    allp = np.concatenate([m["pos"] for m in mesh_list])
    sx, sy = allp @ right, allp @ up
    if scale is None:
        scale = 0.80 * min(W_ / (np.ptp(sx) + 1e-6), H_ / (np.ptp(sy) + 1e-6))
    else:
        scale *= ss
    cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2
    img = np.zeros((H_, W_, 3), np.uint8)
    img[:] = bg
    zbuf = np.full((H_, W_), np.inf)
    th, tw = tex.shape[:2]
    for m in mesh_list:
        P = m["pos"]
        X = (P @ right - cx) * scale + W_ / 2
        Y = H_ / 2 - (P @ up - cy) * scale
        Z = P @ fwd
        for a, b, c in m["tri"]:
            # back-face cull in screen space (CCW from the camera = front)
            x0, y0, x1, y1, x2, y2 = X[a], Y[a], X[b], Y[b], X[c], Y[c]
            area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
            if area >= -1e-9:   # screen y is flipped, so front faces have negative area
                continue
            minx, maxx = int(max(0, math.floor(min(x0, x1, x2)))), int(min(W_ - 1, math.ceil(max(x0, x1, x2))))
            miny, maxy = int(max(0, math.floor(min(y0, y1, y2)))), int(min(H_ - 1, math.ceil(max(y0, y1, y2))))
            if minx > maxx or miny > maxy:
                continue
            gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            w0 = ((x1 - gx) * (y2 - gy) - (x2 - gx) * (y1 - gy)) / area
            w1 = ((x2 - gx) * (y0 - gy) - (x0 - gx) * (y2 - gy)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
            if not inside.any():
                continue
            z = w0 * Z[a] + w1 * Z[b] + w2 * Z[c]
            sub = zbuf[miny:maxy + 1, minx:maxx + 1]
            vis = inside & (z < sub - 1e-7)
            if not vis.any():
                continue
            uv = m["uv"]
            u = w0 * uv[a, 0] + w1 * uv[b, 0] + w2 * uv[c, 0]
            v = w0 * uv[a, 1] + w1 * uv[b, 1] + w2 * uv[c, 1]
            ti = np.clip((v * th).astype(int), 0, th - 1)
            tj = np.clip((u * tw).astype(int), 0, tw - 1)
            col = tex[ti, tj]
            sub[vis] = z[vis]
            img[miny:maxy + 1, minx:maxx + 1][vis] = col[vis]
    im = Image.fromarray(img).resize(size, Image.LANCZOS)
    return im, scale / ss


def label(im, text):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 * len(text) + 12, 22], fill=(30, 32, 40))
    d.text((6, 5), text, fill=(255, 255, 255))
    return im


def offset_mesh(m, d):
    q = dict(m)
    q["pos"] = m["pos"] + np.asarray(d, np.float32)
    return q


# ----------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    faces = build_faces()
    tex, black_uv, used_h = build_texture(faces)
    meshes = build_meshes(faces, black_uv)

    t128 = Image.fromarray(tex)
    t128.save(os.path.join(OUT, "pistol_128.png"))
    t1024 = t128.resize((UPSCALE, UPSCALE), Image.NEAREST)
    t1024.save(os.path.join(OUT, "pistol_1024.png"))
    import io
    b1024, b128 = io.BytesIO(), io.BytesIO()
    t1024.save(b1024, "PNG")
    t128.save(b128, "PNG")

    write_glb(os.path.join(OUT, "pistol.glb"), meshes, b1024.getvalue())
    write_obj(os.path.join(OUT, "pistol.obj"), os.path.join(OUT, "pistol.mtl"), meshes, "pistol_1024.png")
    write_bbmodel(os.path.join(OUT, "pistol.bbmodel"), faces, b128.getvalue())

    # ---------------- previews ----------------
    views = [("side (right, +X)", look_basis(90, 0)), ("top", look_basis(0, 90)),
             ("front (muzzle)", look_basis(180, 0)), ("3/4", look_basis(135, 25))]
    full = [meshes[p] for p in PARTS]
    plain = [meshes[p]["plain"] for p in PARTS]
    allpos = np.concatenate([m["pos"] for m in full])
    for tag, ml in (("outline", full), ("no_outline", plain)):
        tiles = []
        for name, basis in views:
            im, _ = render(ml, tex, basis, size=(640, 480))
            tiles.append(label(im, f"{name} - {tag.replace('_', ' ')}"))
            im.save(os.path.join(PREV, f"{tag}_{name.split()[0].replace('/', '-')}.png"))
        sheet = Image.new("RGB", (1280, 960))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 2) * 640, (i // 2) * 480))
        sheet.save(os.path.join(PREV, f"sheet_{tag}.png"))

    # action pose: slide back, trigger back, magazine dropping along the grip axis
    drop = R_GRIP @ np.array([0, -1.0, 0])
    act = [meshes["Body"], offset_mesh(meshes["Slide"], (0, 0, SLIDE_TRAVEL)),
           offset_mesh(meshes["Trigger"], (0, 0, 1)), offset_mesh(meshes["Magazine"], drop * 10)]
    im, _ = render(act, tex, look_basis(120, 15), size=(900, 640))
    label(im, f"action pose: slide +{SLIDE_TRAVEL}px, trigger +1px, mag 10px down grip axis").save(
        os.path.join(PREV, "action_pose.png"))
    Image.fromarray(tex).resize((512, 512), Image.NEAREST).save(os.path.join(PREV, "texture_512.png"))

    # ---------------- report ----------------
    mn, mx = allpos.min(0), allpos.max(0)
    real = np.concatenate([meshes[p]["plain"]["pos"] for p in PARTS])
    rmn, rmx = real.min(0), real.max(0)
    body = meshes["Body"]["pos"]
    bcen = (body.min(0) + body.max(0)) / 2
    muzzle = np.array([0, 3.0, -33.0]) - ORIGIN
    info = {
        "texture_rows_used": int(used_h),
        "triangles": {p: int(len(meshes[p]["tri"])) for p in PARTS},
        "real_geometry_size_px": (rmx - rmn).round(2).tolist(),
        "size_with_outline_px": (mx - mn).round(2).tolist(),
        "muzzle_tip_studs": (muzzle / PX_PER_STUD).round(4).tolist(),
        "muzzle_from_body_bbox_centre_studs": ((muzzle - bcen) / PX_PER_STUD).round(4).tolist(),
        "slide_travel_studs": SLIDE_TRAVEL / PX_PER_STUD,
        "mag_drop_dir": drop.round(4).tolist(),
        "body_bbox_centre_studs": (bcen / PX_PER_STUD).round(4).tolist(),
        "tool_grip_pos_studs": (-bcen / PX_PER_STUD).round(4).tolist(),
        "part_bbox_centres_studs": {p: (((meshes[p]["pos"].min(0) + meshes[p]["pos"].max(0)) / 2)
                                        / PX_PER_STUD).round(4).tolist() for p in PARTS},
        "part_sizes_studs": {p: ((meshes[p]["pos"].max(0) - meshes[p]["pos"].min(0))
                                 / PX_PER_STUD).round(4).tolist() for p in PARTS},
    }
    with open(os.path.join(OUT, "build_info.json"), "w") as fh:
        json.dump(info, fh, indent=2)
    print(json.dumps(info, indent=2))


SLIDE_TRAVEL = 5  # px

if __name__ == "__main__":
    main()
