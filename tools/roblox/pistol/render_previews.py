"""Software-renders previews straight from out/pistol.glb (not from the build
script's internal data), so the previews double as a GLB round-trip test.

Unlit, nearest-neighbour, back-face culled - i.e. how the inverted-hull
outline actually behaves in Roblox.
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
PREV = os.path.join(OUT, 'previews')
BG = (206, 212, 222)


def load_glb(path):
    data = open(path, 'rb').read()
    magic, ver, total = struct.unpack_from('<III', data, 0)
    assert magic == 0x46546C67 and ver == 2 and total == len(data)
    jl, jt = struct.unpack_from('<II', data, 12)
    assert jt == 0x4E4F534A
    g = json.loads(data[20:20 + jl])
    bl, bt = struct.unpack_from('<II', data, 20 + jl)
    assert bt == 0x004E4942
    binc = data[28 + jl:28 + jl + bl]

    def acc(i):
        a = g['accessors'][i]
        v = g['bufferViews'][a['bufferView']]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a['componentType']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
        arr = np.frombuffer(binc, dt, a['count'] * n, v['byteOffset'])
        return arr.reshape(-1, n) if n > 1 else arr

    img_view = g['bufferViews'][g['images'][0]['bufferView']]
    import io
    tex = np.array(Image.open(io.BytesIO(binc[img_view['byteOffset']:img_view['byteOffset'] + img_view['byteLength']])).convert('RGB'))
    parts = {}
    for node in g['nodes']:
        prim = g['meshes'][node['mesh']]['primitives'][0]
        at = prim['attributes']
        parts[node['name']] = dict(pos=acc(at['POSITION']).astype(float) * 16.0,   # back to px
                                   uv=acc(at['TEXCOORD_0']).astype(float),
                                   idx=acc(prim['indices']).astype(int).reshape(-1, 3))
    return parts, tex


def is_outline_tri(uv, t):
    u = uv[t]
    return np.allclose(u[0], u[1]) and np.allclose(u[0], u[2])


def camera(back, up_hint=(0, 1, 0)):
    b = np.array(back, float)
    b /= np.linalg.norm(b)
    r = np.cross(np.array(up_hint, float), b)
    r /= np.linalg.norm(r)
    u = np.cross(b, r)
    return r, u, b


def render(parts, tex, cam, scale, outlines=True, offsets=None, size=None, pad=1.5):
    r, u, b = cam
    th, tw = tex.shape[:2]
    tris = []
    for name, P in parts.items():
        off = np.zeros(3) if not offsets or name not in offsets else np.array(offsets[name], float)
        pos = P['pos'] + off
        for t in P['idx']:
            if not outlines and is_outline_tri(P['uv'], t):
                continue
            tris.append((pos[t], P['uv'][t]))
    allp = np.concatenate([p for p, _ in tris])
    sx, sy = allp @ r, allp @ u
    minx, maxx, miny, maxy = sx.min() - pad, sx.max() + pad, sy.min() - pad, sy.max() + pad
    W = int(np.ceil((maxx - minx) * scale)) if size is None else size[0]
    Hh = int(np.ceil((maxy - miny) * scale)) if size is None else size[1]
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    img = np.zeros((Hh, W, 3), np.uint8)
    img[:] = BG
    zb = np.full((Hh, W), -np.inf)
    for pts, uvs in tris:
        X = (pts @ r - cx) * scale + W / 2
        Y = Hh / 2 - (pts @ u - cy) * scale
        Z = pts @ b
        area = (X[1] - X[0]) * (Y[2] - Y[0]) - (X[2] - X[0]) * (Y[1] - Y[0])
        if area >= -1e-9:      # screen y is down: front-facing CCW => negative
            continue
        x0, x1 = max(int(np.floor(X.min())), 0), min(int(np.ceil(X.max())), W - 1)
        y0, y1 = max(int(np.floor(Y.min())), 0), min(int(np.ceil(Y.max())), Hh - 1)
        if x0 > x1 or y0 > y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((X[1] - gx) * (Y[2] - gy) - (X[2] - gx) * (Y[1] - gy)) / area
        w1 = ((X[2] - gx) * (Y[0] - gy) - (X[0] - gx) * (Y[2] - gy)) / area
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * Z[0] + w1 * Z[1] + w2 * Z[2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m &= z > sub
        if not m.any():
            continue
        uu = w0 * uvs[0, 0] + w1 * uvs[1, 0] + w2 * uvs[2, 0]
        vv = w0 * uvs[0, 1] + w1 * uvs[1, 1] + w2 * uvs[2, 1]
        tx = np.clip((uu * tw).astype(int), 0, tw - 1)
        ty = np.clip((vv * th).astype(int), 0, th - 1)
        col = tex[ty, tx]
        sub[m] = z[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col[m]
    return Image.fromarray(img)


def label(im, text):
    font = ImageFont.load_default(size=18)
    out = Image.new('RGB', (im.width, im.height + 28), (240, 242, 246))
    out.paste(im, (0, 28))
    ImageDraw.Draw(out).text((8, 5), text, fill=(30, 30, 40), font=font)
    return out


def sheet(images, cols, path, title=None):
    w = max(i.width for i in images)
    h = max(i.height for i in images)
    rows = (len(images) + cols - 1) // cols
    top = 36 if title else 0
    s = Image.new('RGB', (cols * w + (cols + 1) * 8, top + rows * h + (rows + 1) * 8), (250, 250, 252))
    if title:
        ImageDraw.Draw(s).text((10, 8), title, fill=(20, 20, 30), font=ImageFont.load_default(size=22))
    for k, im in enumerate(images):
        x = 8 + (k % cols) * (w + 8)
        y = top + 8 + (k // cols) * (h + 8)
        s.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
    s.save(path)
    return s


VIEWS = {
    'side_right': ((1, 0, 0), (0, 1, 0)),
    'side_left': ((-1, 0, 0), (0, 1, 0)),
    'top': ((0, 1, 0), (-1, 0, 0)),
    'front': ((0, 0, -1), (0, 1, 0)),
    'back': ((0, 0, 1), (0, 1, 0)),
    'three_quarter_front': ((0.75, 0.5, -0.65), (0, 1, 0)),
    'three_quarter_back': ((-0.8, 0.45, 0.55), (0, 1, 0)),
    'three_quarter_below': ((0.8, -0.45, -0.5), (0, 1, 0)),
}


def main():
    os.makedirs(PREV, exist_ok=True)
    info = json.load(open(os.path.join(OUT, 'build_info.json')))
    parts, tex = load_glb(os.path.join(OUT, 'pistol.glb'))
    scale = 20
    for outlines in (True, False):
        tag = 'outline' if outlines else 'no_outline'
        ims = []
        for v, (bk, up) in VIEWS.items():
            im = render(parts, tex, camera(bk, up), scale, outlines)
            im.save(os.path.join(PREV, f'{v}_{tag}.png'))
            ims.append(label(im, v.replace('_', ' ')))
        sheet(ims, 4, os.path.join(PREV, f'sheet_{tag}.png'),
              f'Tidecaller pistol - {"with" if outlines else "without"} outlines (rendered from pistol.glb)')

    # animation poses: slide back, trigger pulled, magazine dropping along grip axis
    d = np.array(info['mag_drop_dir'])
    travel = info['slide_travel_px']
    poses = [
        ('rest', {}),
        (f'slide back {travel}px + trigger 1px', {'Slide': (0, 0, travel), 'Trigger': (0, 0, 1)}),
        ('magazine dropping (8px)', {'Magazine': tuple(d * 8)}),
        ('magazine out (20px)', {'Magazine': tuple(d * 20)}),
    ]
    ims = []
    for name, off in poses:
        im = render(parts, tex, camera((1, 0, 0)), 14, True, off, size=(700, 520))
        ims.append(label(im, name))
    for name, off in poses[1:3]:
        im = render(parts, tex, camera((0.75, 0.5, -0.65)), 14, True, off, size=(700, 520))
        ims.append(label(im, name + ' (3/4)'))
    sheet(ims, 3, os.path.join(PREV, 'sheet_parts_animation.png'), 'Part separation / animation check')

    # small-size readability: render tiny, then blow up nearest-neighbour
    smalls = []
    for v in ('side_right', 'three_quarter_front'):
        bk, up = VIEWS[v]
        for sc in (2, 3):
            im = render(parts, tex, camera(bk, up), sc, True)
            smalls.append(label(im.resize((im.width * 12 // sc, im.height * 12 // sc), Image.NEAREST),
                                f'{v} @ {sc} screen px per texel'))
    sheet(smalls, 2, os.path.join(PREV, 'sheet_small_size.png'), 'Readability at small on-screen size')

    # texture sheet
    t128 = Image.open(os.path.join(OUT, 'pistol_128.png'))
    t128.resize((768, 768), Image.NEAREST).save(os.path.join(PREV, 'texture_x6.png'))
    print('previews written to', PREV)


if __name__ == '__main__':
    main()
