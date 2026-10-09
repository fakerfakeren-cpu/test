"""Mesh loading (Roblox glTF export) and a small z-buffer rasterizer used for the previews."""
import base64
import io
import json

import numpy as np
from PIL import Image


def load(path):
    d = json.load(open(path))
    def buf(i): return base64.b64decode(d['buffers'][i]['uri'].split(',', 1)[1])
    def acc(i):
        a = d['accessors'][i]; bv = d['bufferViews'][a['bufferView']]
        raw = buf(bv['buffer'])[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
        dt = {5125: np.uint32, 5126: np.float32, 5121: np.uint8, 5123: np.uint16}[a['componentType']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        arr = np.frombuffer(raw, dt)
        return arr.reshape(-1, n) if n > 1 else arr
    tex = np.array(Image.open(io.BytesIO(base64.b64decode(d['images'][0]['uri'].split(',', 1)[1]))).convert('RGB'))
    th, tw = tex.shape[:2]
    parts = {}
    for n in d['nodes']:
        if 'mesh' not in n or n['name'] not in ('Body', 'Magazine', 'Slide'): continue
        pr = d['meshes'][n['mesh']]['primitives'][0]
        P = acc(pr['attributes']['POSITION']).astype(float) * np.array(n.get('scale', [1, 1, 1]))
        UV = acc(pr['attributes']['TEXCOORD_0']); I = acc(pr['indices']).reshape(-1, 3)
        uvc = UV[I].mean(1)
        cols = tex[np.clip((uvc[:, 1] * th).astype(int), 0, th - 1), np.clip((uvc[:, 0] * tw).astype(int), 0, tw - 1)]
        parts[n['name']] = (P[I], cols.astype(np.uint8))
    return parts


def box_tris(size):
    sx, sy, sz = size / 2
    c = np.array([[x, y, z] for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)])
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    T = []
    for a, b, cc, d in faces: T += [c[[a, b, cc]], c[[a, cc, d]]]
    return np.array(T)


def shade(T, base, light=np.array([-0.35, 0.8, 0.5])):
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    l = light / np.linalg.norm(light)
    k = 0.62 + 0.38 * np.clip(np.abs(n @ l), 0, 1)
    return np.clip(np.array(base)[None, :] * k[:, None], 0, 255).astype(np.uint8)


def raster(Tc, C, W, H, f, ortho=False, bg=(118, 128, 140), near=0.05):
    """Tc: triangles in camera space (x right, y up, looking -z). f: focal length in px (persp) or px/stud (ortho)."""
    zb = np.full((H, W), np.inf); img = np.zeros((H, W, 3), np.uint8); img[:] = bg
    polys = []
    for t, col in zip(Tc, C):
        if ortho: polys.append((t, col)); continue
        inside = t[:, 2] < -near
        if inside.all(): polys.append((t, col)); continue
        if not inside.any(): continue
        # clip polygon against z = -near
        out = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]; ia, ib = a[2] < -near, b[2] < -near
            if ia: out.append(a)
            if ia != ib:
                s = (-near - a[2]) / (b[2] - a[2]); out.append(a + (b - a) * s)
        for k in range(1, len(out) - 1): polys.append((np.array([out[0], out[k], out[k + 1]]), col))
    for t, col in polys:
        if ortho:
            sx = W / 2 + t[:, 0] * f; sy = H / 2 - t[:, 1] * f; z = -t[:, 2]
        else:
            z = -t[:, 2]; sx = W / 2 + f * t[:, 0] / z; sy = H / 2 - f * t[:, 1] / z
        x0, x1 = int(max(np.floor(sx.min()), 0)), int(min(np.ceil(sx.max()), W - 1))
        y0, y1 = int(max(np.floor(sy.min()), 0)), int(min(np.ceil(sy.max()), H - 1))
        if x0 > x1 or y0 > y1: continue
        area = (sx[1] - sx[0]) * (sy[2] - sy[0]) - (sx[2] - sx[0]) * (sy[1] - sy[0])
        if abs(area) < 1e-9: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((sx[1] - xs) * (sy[2] - ys) - (sx[2] - xs) * (sy[1] - ys)) / area
        w1 = ((sx[2] - xs) * (sy[0] - ys) - (sx[0] - xs) * (sy[2] - ys)) / area
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any(): continue
        if ortho: zz = w0 * z[0] + w1 * z[1] + w2 * z[2]
        else: zz = 1 / (w0 / z[0] + w1 / z[1] + w2 / z[2])
        sub = zb[y0:y1 + 1, x0:x1 + 1]; m &= zz < sub - 1e-7
        sub[m] = zz[m]; img[y0:y1 + 1, x0:x1 + 1][m] = col
    return img
