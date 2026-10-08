"""Rifle v3 voxel model: v1 shape and thicknesses, black outlines everywhere, Trigger merged into Body.
Variant chosen with env RIFLE_SLIM=1 (thinner muzzle device). Index space (i,j,k): i = width (-i = gun's left),
j = up, k = sprite x (muzzle at high k). World: X=i, Y=j, Z=-k."""
import os
import numpy as np
from sprite_v3 import build, PAL, W, H, fam
SLIM = os.environ.get('RIFLE_SLIM', '0') == '1'
P, C = build(SLIM, knob=True)
_, CS = build(SLIM, knob=False)            # side colours with no knob (right side, and under the knob)

WIDTH = {'stock': 7, 'butt': 7, 'upper': 7, 'forend': 7, 'rail': 5, 'barrel': 3, 'muzzle': 5,
         'lower': 5, 'guard': 3, 'grip': 5, 'mag': 5, 'trigger': 1}
def width_of(part, x):
    if part == 'sight': return 5 if x < 45 else 3
    return WIDTH[part]
MAT = {'stock': 'Y', 'upper': 'Y', 'lower': 'Y', 'guard': 'Y', 'butt': 'D', 'grip': 'W', 'forend': 'W',
       'rail': 'M', 'sight': 'M', 'barrel': 'M', 'muzzle': 'M', 'mag': 'M', 'trigger': 'M', 'charge': 'M'}
GROUP = {'mag': 'Magazine', 'charge': 'Slide'}             # trigger now lives in Body
def group_of(part): return GROUP.get(part, 'Body')

# ---- ring (silhouette outline) pixels: owned by the widest touching part; trigger keeps its own ring ----
OWN = np.full((H, W), '', dtype=object)
for y in range(H):
    for x in range(W):
        if P[y, x]: OWN[y, x] = 'upper' if P[y, x] == 'charge' else P[y, x]
for y in range(H):
    for x in range(W):
        if C[y, x] != 'O' or P[y, x]: continue
        def nb(n8):
            return [P[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dy, dx) != (0, 0) and (n8 or dy == 0 or dx == 0) and 0 <= y + dy < H and 0 <= x + dx < W
                    and P[y + dy, x + dx] and P[y + dy, x + dx] != 'charge']
        cand = nb(False) or nb(True)
        if 'trigger' in cand: OWN[y, x] = 'trigger'; continue
        OWN[y, x] = max(cand, key=lambda p: (width_of(p, x), p == 'mag'))

V = {}
for y in range(H):
    for x in range(W):
        p = OWN[y, x]
        if not p: continue
        w = width_of(p, x)
        for i in range(-(w // 2), w // 2 + 1):
            V[(i, H - 1 - y, x)] = dict(part=p, x=x, y=y, ring=not bool(P[y, x]))
for y in range(H):                                   # charging-handle knob, 2 voxels out of the LEFT side
    for x in range(W):
        if P[y, x] == 'charge':
            for i in (-4, -5): V[(i, H - 1 - y, x)] = dict(part='charge', x=x, y=y, ring=False)

DIRS = {'L': (-1, 0, 0), 'R': (1, 0, 0), 'top': (0, 1, 0), 'bottom': (0, -1, 0), 'front': (0, 0, 1), 'back': (0, 0, -1)}
FACE = {
 'Y': {'top': ('Yh', 'Yl'), 'back': ('Yh', 'Yl'), 'front': ('Ym', 'Yd'), 'bottom': ('Ym', 'Yd'), 'dk': 'Yd'},
 'M': {'top': ('Mh', 'Ml'), 'back': ('Mh', 'Ml'), 'front': ('Mm', 'Md'), 'bottom': ('Mm', 'Md'), 'dk': 'Md'},
 'W': {'top': ('Wl', 'Wm'), 'back': ('Wl', 'Wm'), 'front': ('Wm', 'Wd'), 'bottom': ('Wm', 'Wd'), 'dk': 'Wd'},
 'D': {'top': ('Dl', 'Dm'), 'back': ('Dl', 'Dm'), 'front': ('Dm', 'Dd'), 'bottom': ('Dm', 'Dd'), 'dk': 'Dd'},
}
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def inplane(d): return [e for e in DIRS.values() if all(e[t] * d[t] == 0 for t in range(3))]
def run(v, d, e, solid):
    n = 1
    for s in (1, -1):
        u = v
        while True:
            u = add(u, tuple(s * c for c in e))
            if u in solid and add(u, d) not in solid: n += 1
            else: break
    return n

def seam_pixel(x, y, horizontal):
    """is sprite (x,y) a black detail line inside a part (not the silhouette ring) running that way?"""
    if not (0 <= y < H and 0 <= x < W) or not P[y, x] or P[y, x] == 'charge' or C[y, x] != 'O': return False
    if horizontal:   # line runs along x: wraps onto front/back faces
        return any(0 <= y + dy < H and P[y + dy, x] and C[y + dy, x] != 'O' for dy in (-1, 1))
    return any(0 <= x + dx < W and P[y, x + dx] and C[y, x + dx] != 'O' for dx in (-1, 1))

def paint_faces(solid, keys, interface=False):
    out = {}; cls = {}
    for v, dn in keys:
        if dn in ('L', 'R'): continue
        d = DIRS[dn]; part = V[v]['part']; conv = seam = tiny = False
        for e in inplane(d):
            u = add(v, e); axis = tuple(abs(c) for c in e)
            if u not in solid:
                if run(v, d, axis, solid) >= 3: conv = True
                else: tiny = True
            elif add(u, d) in solid:
                if fam(V[add(u, d)]['part']) != fam(part): seam = True
            elif fam(V[u]['part']) != fam(part): seam = True
        cls[(v, dn)] = 'O' if (conv or seam) else ('tiny' if tiny else '')
    for v, dn in keys:
        info = V[v]; part = info['part']; x, y = info['x'], info['y']; i, j, k = v
        if dn in ('L', 'R'):
            if part == 'charge':
                out[(v, dn)] = C[y, x] if dn == 'L' else ('O' if interface else 'Mp')
            elif interface and part in ('mag',):
                out[(v, dn)] = C[y, x]
            else:
                out[(v, dn)] = CS[y, x]
            continue
        m = MAT[part]; F = FACE[m]; c = cls[(v, dn)]
        if c == 'O': out[(v, dn)] = 'O'; continue
        # black detail lines wrap around onto the top/bottom/front/back faces
        if part != 'charge':
            yy = y
            if info['ring']:                       # ring voxel: look at the part pixel next to it
                yy = y + 1 if dn == 'top' else y - 1 if dn == 'bottom' else y
            xx = x
            if info['ring'] and dn in ('front', 'back'):
                xx = x - 1 if dn == 'front' else x + 1
            if dn in ('top', 'bottom') and seam_pixel(x, yy, horizontal=False): out[(v, dn)] = 'O'; continue
            if dn in ('front', 'back') and seam_pixel(xx, y, horizontal=True): out[(v, dn)] = 'O'; continue
        if c == 'tiny': out[(v, dn)] = F['dk']; continue
        near = any(cls.get((add(v, e), dn)) == 'O' for e in inplane(DIRS[dn]) if add(v, e) in solid)
        rim, fill = F[dn]; col = rim if near else fill
        if part == 'muzzle' and dn == 'front':                                    # bore
            by = 8
            if (i, y) == (0, by): col = 'O'
            elif (abs(i), abs(y - by)) in ((1, 0), (0, 1)): col = 'Mp'
        if part == 'butt' and dn == 'back':
            col = 'Dd' if y % 3 == 2 else 'Dl' if y % 3 == 0 else 'Dm'
        if m == 'W' and not near:
            h = (i * 3 + j * 5 + k * 7) % 7
            if dn in ('top', 'back') and h == 0: col = 'Wl'
            if dn in ('top', 'back', 'front') and h == 3: col = 'Wd'
        out[(v, dn)] = col
    return out

def exposed_keys(solid):
    return [(v, dn) for v in solid for dn, d in DIRS.items() if add(v, d) not in solid]
ASSEMBLED = paint_faces(set(V), exposed_keys(set(V)))
def group_faces(gsol):
    keys = exposed_keys(gsol)
    out = {k: ASSEMBLED[k] for k in keys if k in ASSEMBLED}
    inter = [k for k in keys if k not in ASSEMBLED]
    if inter: out.update(paint_faces(gsol, inter, interface=True))
    return out

def quad(v, dn):
    i, j, k = v
    x0, x1, y0, y1, z0, z1 = i - 0.5, i + 0.5, j, j + 1, -k - 1, -k
    n = {'L': (-1, 0, 0), 'R': (1, 0, 0), 'top': (0, 1, 0), 'bottom': (0, -1, 0), 'front': (0, 0, -1), 'back': (0, 0, 1)}[dn]
    if n[0]: x = x1 if n[0] > 0 else x0; q = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    elif n[1]: y = y1 if n[1] > 0 else y0; q = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    else: z = z1 if n[2] > 0 else z0; q = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    q = np.array(q, float)
    if np.dot(np.cross(q[1] - q[0], q[2] - q[0]), n) < 0: q = q[::-1]
    return q
def hexrgb(h): return tuple(int(h[t:t + 2], 16) for t in (1, 3, 5))
def triangles(cols, offset=(0, 0, 0)):
    T = []; K = []
    for (v, dn), c in cols.items():
        q = quad(v, dn) + np.array(offset); rgb = hexrgb(PAL[c])
        T += [q[[0, 1, 2]], q[[0, 2, 3]]]; K += [rgb, rgb]
    return T, K
def assembled():
    T, K = triangles(ASSEMBLED)
    return np.array(T), np.array(K, np.uint8), ASSEMBLED
def exploded(offsets):
    T = []; K = []
    for g, off in offsets.items():
        gsol = {v for v in V if group_of(V[v]['part']) == g}
        t, k = triangles(group_faces(gsol), off); T += t; K += k
    return np.array(T), np.array(K, np.uint8)
