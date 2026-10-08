"""Export a voxel model (model3d-style module) to .glb: one closed, flat-shaded mesh per part,
colours from a 64x64 palette PNG (8x8-texel blocks, UVs at block centres, NEAREST sampler).
Lattice: voxel (i,j,k) spans [i,i+1]x[j,j+1]x[k,k+1]; world X=(a-0.5)*PX, Y=b*PX, Z=-c*PX (muzzle -Z)."""
import sys, json, struct, io, importlib
import numpy as np
from PIL import Image
PX = 0.0531125069
mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else 'model3d')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'Rifle'
V, PAL, MAT, group_of, paint_faces, DIRS = mod.V, mod.PAL, mod.MAT, mod.group_of, mod.paint_faces, mod.DIRS
add = mod.add
ORDER = ['Body', 'Magazine', 'Slide', 'Trigger']
DP = {'Y': 'Yp', 'M': 'Mp', 'W': 'Wp', 'D': 'Dd'}

assembled = paint_faces(set(V))
groups = {g: {v for v in V if group_of(V[v]['part']) == g} for g in ORDER}

def face_colour(v, dn, g):
    if (v, dn) in assembled: return assembled[(v, dn)]
    part = V[v]['part']                                 # interface face, hidden when assembled
    if g == 'Body': return DP[MAT[part]]
    return 'Mp' if part == 'charge' else 'Md'

# ---------- palette ----------
keys = sorted(PAL)
slot = {k: n for n, k in enumerate(keys)}
img = Image.new('RGB', (64, 64), (255, 0, 255))
for k, n in slot.items():
    c = tuple(int(PAL[k][t:t+2], 16) for t in (1, 3, 5))
    x0, y0 = (n % 8) * 8, (n // 8) * 8
    img.paste(c, (x0, y0, x0 + 8, y0 + 8))
img.save(f'{OUT}_palette.png')
def uv(k):
    n = slot[k]; return ((n % 8) * 8 + 4) / 64, ((n // 8) * 8 + 4) / 64

# ---------- greedy rectangles per plane ----------
AX = {'L': (0, -1), 'R': (0, 1), 'bottom': (1, -1), 'top': (1, 1), 'back': (2, -1), 'front': (2, 1)}
def rects_for(g):
    sol = groups[g]; planes = {}
    for v in sol:
        for dn, d in DIRS.items():
            if add(v, d) in sol: continue
            ax, s = AX[dn]
            plane = v[ax] + (1 if s > 0 else 0)          # lattice coordinate of the face plane
            u_ax, w_ax = [a for a in range(3) if a != ax]
            planes.setdefault((dn, plane), {})[(v[u_ax], v[w_ax])] = face_colour(v, dn, g)
    out = []
    for (dn, plane), cells in planes.items():
        ax, s = AX[dn]; u_ax, w_ax = [a for a in range(3) if a != ax]
        left = dict(cells)
        for (u, w) in sorted(cells):
            if (u, w) not in left: continue
            col = left[(u, w)]
            w1 = w
            while (u, w1 + 1) in left and left[(u, w1 + 1)] == col: w1 += 1
            u1 = u
            while all((u1 + 1, ww) in left and left[(u1 + 1, ww)] == col for ww in range(w, w1 + 1)): u1 += 1
            for uu in range(u, u1 + 1):
                for ww in range(w, w1 + 1): del left[(uu, ww)]
            out.append((dn, ax, plane, u_ax, w_ax, u, u1 + 1, w, w1 + 1, col))
    return out

def to_world(p):
    a, b, c = p
    return np.array([(a - 0.5) * PX, b * PX, -c * PX])
NORMAL = {'L': (-1, 0, 0), 'R': (1, 0, 0), 'bottom': (0, -1, 0), 'top': (0, 1, 0), 'back': (0, 0, 1), 'front': (0, 0, -1)}

def build(g):
    R = rects_for(g)
    # all lattice corner points, indexed per axis-aligned line, for T-junction splitting
    lines = {}
    def corners(r):
        dn, ax, plane, ua, wa, u0, u1, w0, w1, col = r
        pts = []
        for (u, w) in ((u0, w0), (u1, w0), (u1, w1), (u0, w1)):
            p = [0, 0, 0]; p[ax] = plane; p[ua] = u; p[wa] = w; pts.append(tuple(p))
        return pts
    allpts = set(pt for r in R for pt in corners(r))
    for pt in allpts:
        for ax in range(3):
            key = (ax,) + tuple(pt[a] for a in range(3) if a != ax)
            lines.setdefault(key, []).append(pt[ax])
    for k in lines: lines[k] = sorted(set(lines[k]))
    def between(p, q):
        ax = [a for a in range(3) if p[a] != q[a]][0]
        key = (ax,) + tuple(p[a] for a in range(3) if a != ax)
        lo, hi = sorted((p[ax], q[ax])); mids = [t for t in lines[key] if lo < t < hi]
        if p[ax] > q[ax]: mids = mids[::-1]
        res = []
        for t in mids:
            m = list(p); m[ax] = t; res.append(tuple(m))
        return res
    P, N, UV, I = [], [], [], []
    for r in R:
        dn, col = r[0], r[-1]
        c = corners(r)
        ring = []
        for e in range(4):
            ring.append(c[e]); ring += between(c[e], c[(e + 1) % 4])
        W = [to_world(p) for p in ring]
        n = np.array(NORMAL[dn], float)
        # orient ring counter-clockwise seen from outside
        area = sum(np.cross(W[t], W[(t + 1) % len(W)]) for t in range(len(W)))
        if np.dot(area, n) < 0: W = W[::-1]
        base = len(P); uvc = uv(col)
        if len(W) == 4:
            P += W; N += [n] * 4; UV += [uvc] * 4
            I += [base, base + 1, base + 2, base, base + 2, base + 3]
        else:                                           # fan from the centre: no slivers, no T-junctions
            cen = sum(to_world(p) for p in c) / 4          # true rectangle centre
            P += W + [cen]; N += [n] * (len(W) + 1); UV += [uvc] * (len(W) + 1)
            for t in range(len(W)): I += [base + len(W), base + t, base + (t + 1) % len(W)]
    return np.array(P, np.float64), np.array(N, np.float32), np.array(UV, np.float32), np.array(I, np.uint32)

def check(P, I):
    key = lambda p: tuple(np.round(p / PX * 2).astype(int))
    vid = {}; idx = np.array([vid.setdefault(key(p), len(vid)) for p in P])
    T = idx[I.reshape(-1, 3)]
    from collections import Counter
    de = Counter()
    for a, b, c in T: de[(a, b)] += 1; de[(b, c)] += 1; de[(c, a)] += 1
    open_e = sum(1 for (a, b), n in de.items() if de.get((b, a), 0) != n)
    nonman = sum(1 for (a, b), n in de.items() if n > 1)
    tri = P[I.reshape(-1, 3)]
    vol = np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6
    area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
    return dict(tris=len(T), open_edges=open_e, nonmanifold_directed=nonman,
                degenerate_tris=int((area < 1e-9).sum()), signed_volume=round(float(vol), 5))

meshes = {}
report = {}
for g in ORDER:
    P, N, UVa, I = build(g)
    lo, hi = P.min(0), P.max(0); centre = (lo + hi) / 2
    meshes[g] = (P - centre, N, UVa, I, centre, hi - lo)
    report[g] = check(P, I) | {'size_studs': (hi - lo).round(4).tolist(), 'centre': centre.round(4).tolist()}

# ---------- write .glb ----------
bin_ = bytearray(); views = []; accs = []
def push(arr, target=None):
    while len(bin_) % 4: bin_.append(0)
    off = len(bin_); b = arr.tobytes(); bin_.extend(b)
    v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(b)}
    if target: v['target'] = target
    views.append(v); return len(views) - 1
def acc(arr, typ, comp, target, minmax=False):
    bv = push(arr, target)
    a = {'bufferView': bv, 'componentType': comp, 'count': int(arr.shape[0]), 'type': typ}
    if minmax: a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
    accs.append(a); return len(accs) - 1
gm, nodes = [], []
for g in ORDER:
    P, N, UVa, I, centre, size = meshes[g]
    pa = acc(P.astype(np.float32), 'VEC3', 5126, 34962, True)
    na = acc(N, 'VEC3', 5126, 34962)
    ua = acc(UVa, 'VEC2', 5126, 34962)
    ia = acc(I, 'SCALAR', 5125, 34963)
    gm.append({'name': g, 'primitives': [{'attributes': {'POSITION': pa, 'NORMAL': na, 'TEXCOORD_0': ua}, 'indices': ia, 'material': 0}]})
    nodes.append({'name': g, 'mesh': len(gm) - 1, 'translation': centre.astype(float).tolist()})
buf = io.BytesIO(); img.save(buf, 'PNG'); png = buf.getvalue()
imgview = push(np.frombuffer(png, np.uint8))
gltf = {
    'asset': {'version': '2.0', 'generator': 'rifle voxel exporter'},
    'scene': 0, 'scenes': [{'nodes': [len(nodes)]}],
    'nodes': nodes + [{'name': OUT, 'children': list(range(len(nodes)))}],
    'meshes': gm,
    'materials': [{'name': f'{OUT}_palette', 'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0.0, 'roughnessFactor': 1.0}}],
    'textures': [{'sampler': 0, 'source': 0}],
    'samplers': [{'magFilter': 9728, 'minFilter': 9728, 'wrapS': 33071, 'wrapT': 33071}],
    'images': [{'name': f'{OUT}_palette', 'mimeType': 'image/png', 'bufferView': imgview}],
    'buffers': [{'byteLength': 0}], 'bufferViews': views, 'accessors': accs,
}
while len(bin_) % 4: bin_.append(0)
gltf['buffers'][0]['byteLength'] = len(bin_)
js = json.dumps(gltf, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(bin_), 0x004E4942) + bin_
open(f'{OUT}.glb', 'wb').write(glb)
json.dump(report, open(f'{OUT}_check.json', 'w'), indent=1, default=float)
for g, r in report.items(): print(g, r)
