"""Spark-9: an original blocky pixel-style pistol.

Every voxel is one "pixel", so the gun reads as pixel art from any angle.
Run `python3 gen_spark_pistol.py` (needs numpy + Pillow) to regenerate:

  spark_pistol.vox          MagicaVoxel source, open it to edit the design
  spark_pistol.obj/.mtl     game-ready mesh (greedy-meshed quads, Y up, barrel along +X)
  spark_pistol_palette.png  texture for the .obj, use point/nearest filtering
  spark_pistol_icon.png     32x32 side-view sprite for inventory/UI
  preview_*.png             renders for a quick look

Everything is deterministic, so re-running gives identical files.
"""
import os
import random
import struct

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# One voxel = 1/128 unit, so the gun is about 0.25 units (25 cm) long.
VOXEL_SIZE = 1 / 128
# Pivot sits in the grip where the hand closes, so it drops straight onto a hand bone.
PIVOT = (8.0, 8.0, 3.0)


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


C = {
    'slide': hexc('4c5466'),
    'slide_top': hexc('646d82'),
    'serration': hexc('2c313c'),
    'frame': hexc('383d4a'),
    'rail': hexc('262a33'),
    'steel': hexc('9aa4b8'),
    'steel_dark': hexc('6b7387'),
    'muzzle': hexc('101216'),
    'port': hexc('1a1d23'),
    'brass': hexc('e0b84a'),
    'glow': hexc('ff8a1f'),
    'glow_hot': hexc('ffd166'),
    'grip': hexc('8a5a34'),
    'grip_dark': hexc('6a4226'),
    'grip_edge': hexc('4e3020'),
    'sight': hexc('1c1f26'),
}
GLOWING = {C['glow'], C['glow_hot'], C['brass']}

vox = {}


def box(x0, x1, y0, y1, z0, z1, col):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox[(x, y, z)] = col


def build():
    # Grip: raked back one voxel every three rows, 6 long and 6 wide.
    for y in range(0, 13):
        off = (12 - y) // 3
        x0, x1 = 7 - off, 12 - off
        if y <= 10:
            box(x0, x1, y, y, 0, 5, C['grip_edge'])
            # checkered panels on both sides, framed by a darker border
            for x in range(x0 + 1, x1):
                if 2 <= y <= 9:
                    col = C['grip'] if (x + y) % 2 else C['grip_dark']
                    vox[(x, y, 0)] = col
                    vox[(x, y, 5)] = col
            # front and back straps stay frame-coloured
            box(x0, x0, y, y, 1, 4, C['frame'])
            box(x1, x1, y, y, 1, 4, C['frame'])
        else:
            box(x0, x1, y, y, 1, 4, C['frame'])
    # Magazine base plate, glowing like the slide stripe
    box(3, 9, 0, 0, 0, 5, C['glow'])
    box(3, 8, -1, -1, 1, 4, C['frame'])

    # Frame under the slide, with rail grooves on the dust cover
    box(6, 26, 10, 12, 1, 4, C['frame'])
    box(4, 6, 12, 12, 1, 4, C['frame'])  # beavertail
    for x in range(20, 27, 2):
        box(x, x, 10, 10, 1, 4, C['rail'])

    # Trigger guard and trigger
    box(10, 19, 6, 6, 2, 3, C['frame'])
    box(19, 20, 6, 9, 2, 3, C['frame'])
    box(15, 15, 8, 9, 2, 3, C['steel'])
    box(14, 14, 7, 7, 2, 3, C['steel'])

    # Slide
    box(6, 27, 13, 17, 0, 5, C['slide'])
    box(6, 27, 17, 17, 1, 4, C['slide_top'])
    for x in (6, 27):  # bevel the top corners
        for z in (0, 5):
            vox.pop((x, 17, z), None)
    for x in range(7, 12):  # rear serrations
        if x % 2:
            for z in (0, 5):
                box(x, x, 13, 16, z, z, C['serration'])
    # Energy stripe along both sides, hottest near the muzzle
    for x in range(13, 26):
        col = C['glow_hot'] if x >= 23 else C['glow']
        vox[(x, 14, 0)] = col
        vox[(x, 14, 5)] = col
    # Ejection port on the right side with a brass case peeking out
    box(15, 18, 16, 16, 5, 5, C['port'])
    vox[(16, 16, 5)] = C['brass']

    # Chunky barrel shroud and muzzle
    box(28, 30, 13, 16, 1, 4, C['steel'])
    box(29, 29, 13, 16, 1, 4, C['steel_dark'])
    box(30, 30, 14, 15, 2, 3, C['muzzle'])

    # Hammer
    box(4, 5, 15, 17, 2, 3, C['steel_dark'])
    box(3, 3, 17, 18, 2, 3, C['steel_dark'])

    # Sights: notched rear, front post with a glowing dot
    box(7, 8, 18, 18, 1, 1, C['sight'])
    box(7, 8, 18, 18, 4, 4, C['sight'])
    box(25, 26, 18, 18, 2, 3, C['sight'])
    vox[(26, 18, 2)] = C['glow_hot']
    vox[(26, 18, 3)] = C['glow_hot']


def bake_shading():
    """Lighten top edges, darken bottom edges, add a little pixel noise."""
    rng = random.Random(9)
    out = {}
    for p in sorted(vox):
        col = vox[p]
        if col in GLOWING:
            out[p] = col
            continue
        x, y, z = p
        f = 1.0
        if (x, y + 1, z) not in vox:
            f *= 1.12
        if (x, y - 1, z) not in vox:
            f *= 0.86
        f *= rng.choice((0.96, 1.0, 1.0, 1.04))  # few levels so faces still merge
        out[p] = tuple(max(0, min(255, int(round(c * f)))) for c in col)
    vox.clear()
    vox.update(out)


def palette():
    cols = sorted(set(vox.values()))
    assert len(cols) <= 255, len(cols)
    return cols, {c: i for i, c in enumerate(cols)}


# ---------------------------------------------------------------- exporters

def write_vox(path, cols, index):
    xs, ys, zs = zip(*vox)
    mn = (min(xs), min(ys), min(zs))
    size = (max(xs) - mn[0] + 1, max(zs) - mn[2] + 1, max(ys) - mn[1] + 1)

    def chunk(cid, content, children=b''):
        return cid + struct.pack('<ii', len(content), len(children)) + content + children

    # MagicaVoxel is Z-up: vox (x, y, z) = ours (x, z, y)
    xyzi = struct.pack('<i', len(vox)) + b''.join(
        struct.pack('<BBBB', x - mn[0], z - mn[2], y - mn[1], index[c] + 1)
        for (x, y, z), c in sorted(vox.items()))
    rgba = b''.join(struct.pack('<BBBB', *c, 255) for c in cols)
    rgba += b'\0\0\0\0' * (256 - len(cols))
    children = chunk(b'SIZE', struct.pack('<iii', *size)) + chunk(b'XYZI', xyzi) + chunk(b'RGBA', rgba)
    with open(path, 'wb') as f:
        f.write(b'VOX ' + struct.pack('<i', 150) + chunk(b'MAIN', b'', children))


CELL = 4  # each palette colour is a 4x4 block so bilinear filtering/mips can't bleed


def write_palette(path, cols):
    per_row = 16
    rows = (len(cols) + per_row - 1) // per_row
    img = Image.new('RGBA', (per_row * CELL, max(rows, 1) * CELL), (0, 0, 0, 0))
    px = img.load()
    for i, c in enumerate(cols):
        cx, cy = (i % per_row) * CELL, (i // per_row) * CELL
        for dx in range(CELL):
            for dy in range(CELL):
                px[cx + dx, cy + dy] = (*c, 255)
    img.save(path)
    return img.size


def greedy_quads():
    """Merge exposed faces of the same colour into rectangles."""
    quads = []  # (corners[4], normal, colour)
    pts = np.array(list(vox))
    mn, mx = pts.min(0), pts.max(0)
    for d in range(3):
        u, v = (d + 1) % 3, (d + 2) % 3
        for sign in (1, -1):
            for s in range(mn[d], mx[d] + 1):
                mask = {}
                for p, c in vox.items():
                    if p[d] != s:
                        continue
                    q = list(p)
                    q[d] += sign
                    if tuple(q) not in vox:
                        mask[(p[u], p[v])] = c
                done = set()
                for a in range(mn[u], mx[u] + 1):
                    for b in range(mn[v], mx[v] + 1):
                        c = mask.get((a, b))
                        if c is None or (a, b) in done:
                            continue
                        w = 1
                        while mask.get((a + w, b)) == c and (a + w, b) not in done:
                            w += 1
                        h = 1
                        while all(mask.get((a + i, b + h)) == c and (a + i, b + h) not in done
                                  for i in range(w)):
                            h += 1
                        for i in range(w):
                            for j in range(h):
                                done.add((a + i, b + j))
                        plane = s + (1 if sign > 0 else 0)
                        corners = []
                        for du, dv in ((0, 0), (w, 0), (w, h), (0, h)):
                            pt = [0, 0, 0]
                            pt[d], pt[u], pt[v] = plane, a + du, b + dv
                            corners.append(tuple(pt))
                        if sign < 0:
                            corners.reverse()
                        n = [0, 0, 0]
                        n[d] = sign
                        quads.append((corners, tuple(n), c))
    return quads


def write_obj(path_obj, path_mtl, tex_name, cols, index, tex_size):
    quads = greedy_quads()
    verts, vidx = [], {}
    normals, nidx = [], {}
    uvs, uidx = [], {}
    faces = []
    for corners, n, c in quads:
        if n not in nidx:
            nidx[n] = len(normals) + 1
            normals.append(n)
        i = index[c]
        uv = (((i % 16) * CELL + CELL / 2) / tex_size[0],
              1 - ((i // 16) * CELL + CELL / 2) / tex_size[1])
        if uv not in uidx:
            uidx[uv] = len(uvs) + 1
            uvs.append(uv)
        ids = []
        for p in corners:
            if p not in vidx:
                vidx[p] = len(verts) + 1
                verts.append(p)
            ids.append(vidx[p])
        faces.append((ids, uidx[uv], nidx[n]))
    with open(path_mtl, 'w') as f:
        f.write('newmtl spark_pistol\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nd 1\nillum 1\n'
                f'map_Kd {tex_name}\n')
    with open(path_obj, 'w') as f:
        f.write('# Spark-9 blocky pistol, generated by gen_spark_pistol.py\n'
                f'# {len(verts)} vertices, {len(faces)} quads. Y up, barrel along +X.\n'
                f'mtllib {os.path.basename(path_mtl)}\no spark_pistol\n')
        for p in verts:
            f.write('v %.6f %.6f %.6f\n' % tuple((p[k] - PIVOT[k]) * VOXEL_SIZE for k in range(3)))
        for uv in uvs:
            f.write('vt %.6f %.6f\n' % uv)
        for n in normals:
            f.write('vn %d %d %d\n' % n)
        f.write('usemtl spark_pistol\ns off\n')
        for ids, t, n in faces:
            f.write('f ' + ' '.join(f'{i}/{t}/{n}' for i in ids) + '\n')
    return len(verts), len(faces)


# ---------------------------------------------------------------- previews

FACE_LIGHT = {(0, 1, 0): 1.0, (0, -1, 0): 0.5, (1, 0, 0): 0.78, (-1, 0, 0): 0.7,
              (0, 0, 1): 0.88, (0, 0, -1): 0.88}


def render(path, yaw, pitch, scale, bg=(214, 219, 228)):
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))

    def rot(p):
        x, y, z = p
        x, z = x * cy + z * sy, -x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z

    polys = []
    for (x, y, z), c in vox.items():
        for n, light in FACE_LIGHT.items():
            if (x + n[0], y + n[1], z + n[2]) in vox:
                continue
            if rot(n)[2] <= 0:
                continue
            d = n.index(1) if 1 in n else n.index(-1)
            u, v = (d + 1) % 3, (d + 2) % 3
            base = [x, y, z]
            if n[d] > 0:
                base[d] += 1
            corners = []
            for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                pt = list(base)
                pt[u] += du
                pt[v] += dv
                corners.append(rot(pt))
            depth = sum(p[2] for p in corners) / 4
            f = 1.0 if c in GLOWING else light
            col = tuple(int(min(255, ch * f)) for ch in c)
            polys.append((depth, [(p[0], -p[1]) for p in corners], col))
    allp = [pt for _, cs, _ in polys for pt in cs]
    minx, miny = min(p[0] for p in allp), min(p[1] for p in allp)
    maxx, maxy = max(p[0] for p in allp), max(p[1] for p in allp)
    pad = 40
    W, H = int((maxx - minx) * scale) + 2 * pad, int((maxy - miny) * scale) + 2 * pad
    img = Image.new('RGB', (W, H), bg)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(img)
    for _, cs, col in sorted(polys, key=lambda t: t[0]):
        dr.polygon([((px - minx) * scale + pad, (py - miny) * scale + pad) for px, py in cs],
                   fill=col, outline=col)
    img.save(path)


def write_icon(path, path_big):
    """Pixel-art sprite: the gun seen from its right side, one voxel per pixel, outlined."""
    xs, ys = [p[0] for p in vox], [p[1] for p in vox]
    mnx, mxy = min(xs), max(ys)
    w, h = max(xs) - mnx + 1, mxy - min(ys) + 1
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    px = img.load()
    ox, oy = (32 - w) // 2, (32 - h) // 2
    filled = {}
    for (x, y, z), c in vox.items():
        key = (x - mnx + ox, mxy - y + oy)
        if key not in filled or z > filled[key][0]:
            filled[key] = (z, c)
    for (ix, iy), (_, c) in filled.items():
        px[ix, iy] = (*c, 255)
    outline = (16, 18, 22, 255)
    for (ix, iy) in list(filled):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (ix + dx, iy + dy)
            if q not in filled and 0 <= q[0] < 32 and 0 <= q[1] < 32 and px[q][3] == 0:
                px[q] = outline
    img.save(path)
    img.resize((256, 256), Image.NEAREST).save(path_big)


def main():
    build()
    bake_shading()
    cols, index = palette()
    out = lambda n: os.path.join(HERE, n)
    write_vox(out('spark_pistol.vox'), cols, index)
    tex = write_palette(out('spark_pistol_palette.png'), cols)
    nv, nf = write_obj(out('spark_pistol.obj'), out('spark_pistol.mtl'), 'spark_pistol_palette.png',
                       cols, index, tex)
    render(out('preview_three_quarter.png'), yaw=-35, pitch=25, scale=18)
    render(out('preview_side.png'), yaw=0, pitch=0, scale=18)
    render(out('preview_left_rear.png'), yaw=145, pitch=20, scale=18)
    write_icon(out('spark_pistol_icon.png'), out('preview_icon_8x.png'))
    print(f'{len(vox)} voxels, {len(cols)} colours, {nv} vertices, {nf} quads')


if __name__ == '__main__':
    main()
