"""Box-model toolkit: geometry specs, UV packing, skin painting, Java emission and a preview renderer.

A model is a tree of parts under a "hull" part. Each part has a pivot (relative to its parent), an optional
rest rotation and a list of cubes (origin and size relative to the pivot). Coordinates follow Minecraft's
model space: y grows downward and the creature faces -z.
"""
import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image

from .paint import Img
from .skins import SKINS, FEATURES


@dataclass
class Cube:
    origin: tuple
    size: tuple
    mat: str
    feat: object = None      # feature key (or list of keys) painted on `face`
    face: str = 'front'
    grow: float = 0.0
    uv: tuple = None


@dataclass
class Part:
    name: str
    pivot: tuple
    cubes: list = field(default_factory=list)
    kids: list = field(default_factory=list)
    rot: tuple = (0.0, 0.0, 0.0)


def C(x, y, z, w, h, d, mat, feat=None, face='front', grow=0.0):
    return Cube((x, y, z), (int(w), int(h), int(d)), mat, feat, face, grow)


def P(name, pivot, *cubes, kids=(), rot=(0.0, 0.0, 0.0)):
    return Part(name, pivot, list(cubes), list(kids), rot)


class Model:
    def __init__(self, name, width, parts, hull=(0.0, 24.0, 0.0), min_height=32):
        self.name = name
        self.width = width
        self.hull = Part('hull', hull, [], parts)
        self.min_height = min_height
        self.height = None

    # ------------------------------------------------------------------ traversal
    def walk(self, part=None, path=()):
        part = part or self.hull
        path = path + (part.name,)
        yield part, path
        for k in part.kids:
            yield from self.walk(k, path)

    def cubes(self):
        for part, _ in self.walk():
            for c in part.cubes:
                yield part, c

    # ------------------------------------------------------------------ UV packing (shelf packer)
    def pack(self):
        items = []
        for part, c in self.cubes():
            w, h, d = c.size
            rw, rh = max(1, 2 * (w + d)), max(1, h + d)
            items.append((rh, rw, c))
        items.sort(key=lambda t: (-t[0], -t[1]))
        x = y = shelf = 0
        for rh, rw, c in items:
            if rw > self.width:
                raise ValueError(f'{self.name}: cube {c.size} wider than texture')
            if x + rw > self.width:
                x = 0
                y += shelf
                shelf = 0
            c.uv = (x, y)
            x += rw
            shelf = max(shelf, rh)
        used = y + shelf
        hgt = self.min_height
        while hgt < used:
            hgt *= 2
        self.height = hgt

    # ------------------------------------------------------------------ painting
    def paint(self, seed=1):
        tex = Img(self.width, self.height)
        glow = Img(self.width, self.height)
        rng = np.random.default_rng(seed)
        for idx, (part, c) in enumerate(self.cubes()):
            skin = SKINS[c.mat]
            u, v = c.uv
            w, h, d = c.size
            regions = face_regions(u, v, w, h, d)
            cseed = seed * 7919 + idx * 131
            for face, (fx, fy, fw, fh) in regions.items():
                if fw <= 0 or fh <= 0:
                    continue
                r = np.random.default_rng(cseed + FACE_IDS[face] * 97)
                for yy in range(fh):
                    for xx in range(fw):
                        col, g = skin.paint(face, xx, yy, fw, fh, cseed, r)
                        tex.px[fy + yy, fx + xx] = col
                        if g is not None:
                            gc = np.asarray(g, dtype=float)
                            if len(gc) == 3:
                                gc = np.append(gc, 1.0)
                            glow.px[fy + yy, fx + xx] = gc
            feats = c.feat if isinstance(c.feat, (list, tuple)) else ([c.feat] if c.feat else [])
            faces = c.face if isinstance(c.face, (list, tuple)) else (c.face,)
            for f in feats:
                for face in faces:
                    fx, fy, fw, fh = regions[face]
                    FEATURES[f](tex, glow, fx, fy, fw, fh, np.random.default_rng(cseed + 5 + FACE_IDS[face]))
        return tex, glow

    # ------------------------------------------------------------------ Java
    def java(self, method):
        out = [f'    private static LayerDefinition {method}() {{',
               '        MeshDefinition mesh = new MeshDefinition();',
               '        PartDefinition root = mesh.getRoot();']
        names = {}

        def emit(part, parent_var):
            var = 'p_' + part.name
            n = names.get(var, 0)
            names[var] = n + 1
            if n:
                var += str(n)
            builder = 'CubeListBuilder.create()'
            for c in part.cubes:
                x, y, z = c.origin
                w, h, d = c.size
                builder += f'.texOffs({c.uv[0]}, {c.uv[1]})'
                if c.grow:
                    builder += f'.addBox({fl(x)}, {fl(y)}, {fl(z)}, {fl(w)}, {fl(h)}, {fl(d)}, new CubeDeformation({fl(c.grow)}))'
                else:
                    builder += f'.addBox({fl(x)}, {fl(y)}, {fl(z)}, {fl(w)}, {fl(h)}, {fl(d)})'
            px, py, pz = part.pivot
            rx, ry, rz = part.rot
            out.append(f'        PartDefinition {var} = {parent_var}.addOrReplaceChild("{part.name}", {builder}, '
                       f'PartPose.offsetAndRotation({fl(px)}, {fl(py)}, {fl(pz)}, {fl(rx)}, {fl(ry)}, {fl(rz)}));')
            for k in part.kids:
                emit(k, var)

        emit(self.hull, 'root')
        out.append(f'        return LayerDefinition.create(mesh, {self.width}, {self.height});')
        out.append('    }')
        return '\n'.join(out)

    def paths(self):
        for part, path in self.walk():
            if part.name != 'hull':
                yield part.name, path


FACE_IDS = {'top': 1, 'bottom': 2, 'right': 3, 'front': 4, 'left': 5, 'back': 6}


def fl(v):
    return f'{float(v):.4g}F' if not float(v).is_integer() else f'{float(v):.1f}F'


def face_regions(u, v, w, h, d):
    """Texture rectangles of each face in Minecraft's box layout (see the wrap-around order in the docs)."""
    return {
        'top': (u + d, v, w, d),
        'bottom': (u + d + w, v, w, d),
        'right': (u, v + d, d, h),          # -x side (the creature's right)
        'front': (u + d, v + d, w, h),      # -z side
        'left': (u + d + w, v + d, d, h),   # +x side
        'back': (u + 2 * d + w, v + d, w, h),
    }


# ====================================================================== preview renderer
def _rot(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return mz @ my @ mx


def world_faces(model, pose=None):
    """Yields (corners[4] world, uv[4], face) for every face, applying part pivots and rotations.

    `pose` maps part name -> (rx, ry, rz) overrides (added to the rest rotation)."""
    pose = pose or {}
    result = []

    def rec(part, M, T):
        rot = np.array(part.rot, dtype=float)
        if part.name in pose:
            rot = rot + np.array(pose[part.name])
        R = _rot(*rot)
        T2 = T + M @ np.array(part.pivot, dtype=float)
        M2 = M @ R
        for c in part.cubes:
            x0, y0, z0 = c.origin
            w, h, d = c.size
            g = c.grow
            X0, Y0, Z0 = x0 - g, y0 - g, z0 - g
            X1, Y1, Z1 = x0 + w + g, y0 + h + g, z0 + d + g
            u, v = c.uv
            # corners in (x, y, z) with matching texel coordinates, wrap-around order
            quads = {
                'front': ([(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0)],
                          [(u + d, v + d), (u + d + w, v + d), (u + d + w, v + d + h), (u + d, v + d + h)]),
                'left': ([(X1, Y0, Z0), (X1, Y0, Z1), (X1, Y1, Z1), (X1, Y1, Z0)],
                         [(u + d + w, v + d), (u + 2 * d + w, v + d), (u + 2 * d + w, v + d + h), (u + d + w, v + d + h)]),
                'back': ([(X1, Y0, Z1), (X0, Y0, Z1), (X0, Y1, Z1), (X1, Y1, Z1)],
                         [(u + 2 * d + w, v + d), (u + 2 * d + 2 * w, v + d), (u + 2 * d + 2 * w, v + d + h), (u + 2 * d + w, v + d + h)]),
                'right': ([(X0, Y0, Z1), (X0, Y0, Z0), (X0, Y1, Z0), (X0, Y1, Z1)],
                          [(u, v + d), (u + d, v + d), (u + d, v + d + h), (u, v + d + h)]),
                'top': ([(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y0, Z0), (X0, Y0, Z0)],
                        [(u + d, v), (u + d + w, v), (u + d + w, v + d), (u + d, v + d)]),
                'bottom': ([(X0, Y1, Z1), (X1, Y1, Z1), (X1, Y1, Z0), (X0, Y1, Z0)],
                           [(u + d + w, v), (u + d + 2 * w, v), (u + d + 2 * w, v + d), (u + d + w, v + d)]),
            }
            for face, (pts, uvs) in quads.items():
                a, b, c4 = (np.array(pts[i], dtype=float) for i in (0, 1, 3))
                if np.linalg.norm(np.cross(b - a, c4 - a)) < 1e-6:
                    continue                     # zero-area side of a flat plane
                wp = [T2 + M2 @ np.array(p, dtype=float) for p in pts]
                result.append((wp, uvs, face))
        for k in part.kids:
            rec(k, M2, T2)

    rec(model.hull, np.eye(3), np.zeros(3))
    return result


def render(model, tex, glow, yaw=-35, pitch=18, scale=8, size=None, pose=None, bg=(0, 0, 0, 0)):
    """Orthographic software render of the model (for previews and GUI portraits)."""
    faces = world_faces(model, pose)
    ya, pa = math.radians(yaw), math.radians(pitch)
    # view: flip y (model y is down), rotate about y then tilt about x
    def view(p):
        # model space -> world (the renderer's 180 degree turn about z), then turn to face the camera
        x, y, z = p[0], -p[1], -p[2]
        x, z = x * math.cos(ya) + z * math.sin(ya), -x * math.sin(ya) + z * math.cos(ya)
        y, z = y * math.cos(pa) - z * math.sin(pa), y * math.sin(pa) + z * math.cos(pa)
        return np.array([x, y, z])

    vf = [([view(p) for p in pts], uvs, face) for pts, uvs, face in faces]
    allp = np.array([p for pts, _, _ in vf for p in pts])
    minx, maxx = allp[:, 0].min(), allp[:, 0].max()
    miny, maxy = allp[:, 1].min(), allp[:, 1].max()
    pad = 2
    W = int((maxx - minx + 2 * pad) * scale) if size is None else size[0]
    H = int((maxy - miny + 2 * pad) * scale) if size is None else size[1]
    if size is not None:
        scale = min(W / (maxx - minx + 2 * pad), H / (maxy - miny + 2 * pad))
    cxm, cym = (minx + maxx) / 2, (miny + maxy) / 2
    img = np.zeros((H, W, 4))
    img[:, :] = np.array(bg) / 255.0
    zbuf = np.full((H, W), -1e9)
    T = tex.px
    G = glow.px if glow is not None else None
    th, tw = T.shape[0], T.shape[1]
    light = {'top': 1.0, 'front': 0.86, 'left': 0.7, 'right': 0.7, 'back': 0.6, 'bottom': 0.5}

    def to_screen(p):
        return np.array([W / 2 + (p[0] - cxm) * scale, H / 2 - (p[1] - cym) * scale, p[2]])

    for pts, uvs, face in vf:
        sp = [to_screen(p) for p in pts]
        shade = light[face]
        for tri in ((0, 1, 2), (0, 2, 3)):
            P0, P1, P2 = sp[tri[0]], sp[tri[1]], sp[tri[2]]
            U0, U1, U2 = [np.array(uvs[i], dtype=float) for i in tri]
            xs = [P0[0], P1[0], P2[0]]
            ys = [P0[1], P1[1], P2[1]]
            x0, x1 = max(0, int(math.floor(min(xs)))), min(W - 1, int(math.ceil(max(xs))))
            y0, y1 = max(0, int(math.floor(min(ys)))), min(H - 1, int(math.ceil(max(ys))))
            if x1 < x0 or y1 < y0:
                continue
            den = (P1[1] - P2[1]) * (P0[0] - P2[0]) + (P2[0] - P1[0]) * (P0[1] - P2[1])
            if abs(den) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l0 = ((P1[1] - P2[1]) * (gx - P2[0]) + (P2[0] - P1[0]) * (gy - P2[1])) / den
            l1 = ((P2[1] - P0[1]) * (gx - P2[0]) + (P0[0] - P2[0]) * (gy - P2[1])) / den
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not inside.any():
                continue
            z = l0 * P0[2] + l1 * P1[2] + l2 * P2[2]
            uu = l0 * U0[0] + l1 * U1[0] + l2 * U2[0]
            vv = l0 * U0[1] + l1 * U1[1] + l2 * U2[1]
            ti = np.clip(np.floor(uu - 1e-4).astype(int), 0, tw - 1)
            tj = np.clip(np.floor(vv - 1e-4).astype(int), 0, th - 1)
            col = T[tj, ti]
            ok = inside & (col[..., 3] > 0.1)
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            closer = ok & (z > sub)
            if not closer.any():
                continue
            rgb = col[..., :3] * shade
            if G is not None:
                gcol = G[tj, ti]
                rgb = np.clip(rgb + gcol[..., :3] * gcol[..., 3:4] * 0.9, 0, 1)
            region = img[y0:y1 + 1, x0:x1 + 1]
            region[closer, :3] = rgb[closer]
            region[closer, 3] = 1.0
            sub[closer] = z[closer]
    return img


def save_rgba(arr, path):
    Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(path)
