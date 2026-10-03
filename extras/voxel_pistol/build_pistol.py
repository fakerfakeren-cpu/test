"""Builds the "VX-9 Pocketbrick" voxel pistol.

An original blocky sidearm in a chunky voxel/pixel-gun style. Every voxel is
placed by code below, so tweaking the design means editing `build()` and
re-running:

    python3 build_pistol.py

Outputs (next to this script):
    vx9_pistol.vox          MagicaVoxel model (open, recolour, re-export)
    vx9_pistol.obj/.mtl     greedy-meshed mesh for Unity / Blender
    vx9_palette.png         palette texture the .obj samples (use Point filtering)
    preview.png             rendered from the exported .obj, not from the voxels

Axes: barrel points +X, up is +Y, the gun's right side is +Z.
"""
import os
import struct

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = 'vx9_pistol'

# 1 voxel in mesh units. 25 voxels long -> 0.5 units. Rescale freely on import.
VOXEL_SIZE = 0.02
# Mesh origin: centre of the grip, roughly where the hand holds it.
PIVOT = (5.5, 6.0, 2.5)

PALETTE = {
    'S': '#4b5a70',  # slide
    's': '#7186a3',  # slide top highlight
    'D': '#252b35',  # recesses, hammer, slide stop
    'F': '#33383f',  # frame and trigger guard
    'B': '#a9b3bf',  # barrel steel
    'K': '#0b0d10',  # bore and port shadow
    'E': '#2ef2d8',  # glow strip
    'O': '#ff8a1c',  # orange accents
    'G': '#272a30',  # grip body
    'P': '#1e7f74',  # grip panel
    'p': '#17655d',  # grip panel checker
    'T': '#1a1c20',  # trigger
}
KEYS = list(PALETTE)

WIDTH = 5  # z = 0..4, z = 4 is the right side


def build():
    v = {}

    def box(x0, x1, y0, y1, z0, z1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    v[(x, y, z)] = c

    def cut(x0, x1, y0, y1, z0, z1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    v.pop((x, y, z), None)

    def paint(x0, x1, y0, y1, z0, z1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if (x, y, z) in v:
                        v[(x, y, z)] = c

    # --- slide: x 1..23, y 11..15, bevelled top and chamfered ends
    box(1, 23, 11, 15, 0, 4, 'S')
    cut(1, 23, 15, 15, 0, 0)
    cut(1, 23, 15, 15, 4, 4)
    paint(1, 23, 15, 15, 1, 3, 's')
    cut(23, 23, 15, 15, 0, 4)          # front top chamfer
    cut(23, 23, 11, 11, 0, 4)          # front bottom chamfer
    cut(1, 1, 11, 11, 0, 4)            # rear bottom chamfer

    # rear grip grooves: two square cuts per side, dark floor
    for x in (3, 5):
        cut(x, x, 12, 14, 0, 0)
        cut(x, x, 12, 14, 4, 4)
        paint(x, x, 12, 14, 1, 1, 'D')
        paint(x, x, 12, 14, 3, 3, 'D')

    # glow strip along both sides of the slide nose
    paint(13, 22, 12, 12, 0, 0, 'E')
    paint(13, 22, 12, 12, 4, 4, 'E')

    # ejection port on the right side, barrel hood visible inside
    cut(8, 11, 13, 14, 4, 4)
    paint(8, 11, 13, 14, 3, 3, 'B')
    paint(8, 8, 13, 14, 3, 3, 'K')

    # --- muzzle: 3x3 barrel ring sticking out 1 voxel, bore recessed
    box(24, 24, 12, 14, 1, 3, 'B')
    cut(24, 24, 13, 13, 2, 2)
    paint(23, 23, 13, 13, 2, 2, 'K')

    # --- sights: notched rear blocks, single orange front post
    box(2, 3, 16, 16, 1, 1, 'F')
    box(2, 3, 16, 16, 3, 3, 'F')
    box(22, 22, 16, 16, 2, 2, 'O')

    # --- frame under the slide, hammer and beavertail at the back
    box(1, 22, 9, 10, 0, 4, 'F')
    box(0, 0, 10, 10, 1, 3, 'F')
    box(0, 0, 11, 12, 2, 2, 'D')
    paint(12, 15, 10, 10, 0, 0, 'D')   # slide stop lever, left side
    paint(22, 22, 9, 10, 0, 0, 'O')    # orange frame tips
    paint(22, 22, 9, 10, 4, 4, 'O')

    # --- trigger guard: squared, with a small forward hook
    box(16, 16, 5, 8, 1, 3, 'F')
    box(10, 16, 5, 5, 1, 3, 'F')
    box(17, 17, 5, 5, 1, 3, 'F')
    for x, y in ((13, 8), (13, 7), (13, 6), (14, 6)):
        v[(x, y, 2)] = 'T'

    # --- grip: raked back one voxel every three rows
    for y in range(0, 9):
        step = (8 - y) // 3
        rear, front = 2 - step, 10 - step
        box(rear, front, y, y, 0, 4, 'G')
        if 1 <= y <= 7:
            for x in range(rear + 1, front):
                c = 'P' if (x + y) % 2 == 0 else 'p'
                v[(x, y, 0)] = c
                v[(x, y, 4)] = c
    box(0, 8, 0, 0, 0, 4, 'O')         # magazine base plate
    v[(10, 8, 4)] = 'O'                # magazine release, right side

    return v


# ---------------------------------------------------------------- meshing

DIRS = [  # (axis, sign)
    (0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1),
]


def bounds(v):
    xs, ys, zs = zip(*v)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def greedy_mesh(v):
    """Merge coplanar same-colour faces into rectangles. Returns quads as
    (4 corners CCW from outside, normal, colour key)."""
    (lo, hi) = bounds(v)
    quads = []
    for axis, sign in DIRS:
        u, w = (axis + 1) % 3, (axis + 2) % 3
        for d in range(lo[axis], hi[axis] + 1):
            mask = {}
            for a in range(lo[u], hi[u] + 1):
                for b in range(lo[w], hi[w] + 1):
                    p = [0, 0, 0]
                    p[axis], p[u], p[w] = d, a, b
                    p = tuple(p)
                    if p not in v:
                        continue
                    n = list(p)
                    n[axis] += sign
                    if tuple(n) in v:
                        continue
                    mask[(a, b)] = v[p]
            done = set()
            for a in range(lo[u], hi[u] + 1):
                for b in range(lo[w], hi[w] + 1):
                    if (a, b) in done or (a, b) not in mask:
                        continue
                    c = mask[(a, b)]
                    bw = 1
                    while (a, b + bw) in mask and mask[(a, b + bw)] == c and (a, b + bw) not in done:
                        bw += 1
                    ah = 1
                    while all((a + ah, b + k) in mask and mask[(a + ah, b + k)] == c
                              and (a + ah, b + k) not in done for k in range(bw)):
                        ah += 1
                    for i in range(ah):
                        for k in range(bw):
                            done.add((a + i, b + k))
                    plane = d + (1 if sign > 0 else 0)

                    def pt(pa, pb):
                        q = [0, 0, 0]
                        q[axis], q[u], q[w] = plane, pa, pb
                        return tuple(q)

                    corners = [pt(a, b), pt(a + ah, b), pt(a + ah, b + bw), pt(a, b + bw)]
                    if sign < 0:
                        corners.reverse()
                    normal = [0, 0, 0]
                    normal[axis] = sign
                    quads.append((corners, tuple(normal), c))
    return quads


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- writers

def write_palette_png(path):
    img = Image.new('RGBA', (len(KEYS), 1))
    for i, k in enumerate(KEYS):
        img.putpixel((i, 0), hex_rgb(PALETTE[k]) + (255,))
    img.save(path)


def write_obj(quads, obj_path, mtl_path, tex_name):
    mtl_name = os.path.basename(mtl_path)
    with open(mtl_path, 'w', newline='\n') as f:
        f.write('newmtl vx9_palette\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nillum 1\n')
        f.write(f'map_Kd {tex_name}\n')

    verts, vidx = [], {}
    normals = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    faces = []
    for corners, normal, c in quads:
        ids = []
        for p in corners:
            if p not in vidx:
                vidx[p] = len(verts) + 1
                verts.append(p)
            ids.append(vidx[p])
        faces.append((ids, normals.index(normal) + 1, KEYS.index(c) + 1))

    with open(obj_path, 'w', newline='\n') as f:
        f.write('# VX-9 Pocketbrick voxel pistol, generated by build_pistol.py\n')
        f.write('# +X = barrel direction, +Y = up, +Z = right side\n')
        f.write(f'mtllib {mtl_name}\no {NAME}\n')
        for p in verts:
            x, y, z = ((p[i] - PIVOT[i]) * VOXEL_SIZE for i in range(3))
            f.write(f'v {x:.4f} {y:.4f} {z:.4f}\n')
        for i in range(len(KEYS)):
            f.write(f'vt {(i + 0.5) / len(KEYS):.6f} 0.5\n')
        for n in normals:
            f.write('vn %d %d %d\n' % n)
        f.write('usemtl vx9_palette\ns off\n')
        for ids, n, t in faces:
            f.write('f ' + ' '.join(f'{i}/{t}/{n}' for i in ids) + '\n')
    return len(verts), len(faces)


def write_vox(v, path):
    """MagicaVoxel .vox (version 150). MagicaVoxel is Z-up, so our (x, y, z)
    maps to (x, WIDTH-1-z, y) to keep the model un-mirrored."""
    (lo, hi) = bounds(v)
    size = (hi[0] - lo[0] + 1, WIDTH, hi[1] - lo[1] + 1)

    def chunk(cid, content, children=b''):
        return cid + struct.pack('<ii', len(content), len(children)) + content + children

    xyzi = struct.pack('<i', len(v))
    for (x, y, z), c in sorted(v.items()):
        xyzi += struct.pack('<BBBB', x - lo[0], WIDTH - 1 - z, y - lo[1], KEYS.index(c) + 1)
    rgba = b''
    for i in range(256):
        if i < len(KEYS):
            rgba += bytes(hex_rgb(PALETTE[KEYS[i]]) + (255,))
        else:
            rgba += bytes((0, 0, 0, 255))
    children = (chunk(b'SIZE', struct.pack('<iii', *size))
                + chunk(b'XYZI', xyzi)
                + chunk(b'RGBA', rgba))
    with open(path, 'wb') as f:
        f.write(b'VOX ' + struct.pack('<i', 150) + chunk(b'MAIN', b'', children))


# ---------------------------------------------------------------- preview
# Renders the written .obj back from disk with a z-buffer, so the preview
# doubles as a check that the exported mesh is what we think it is.

def read_obj(path, palette_png):
    pal = Image.open(palette_png).convert('RGB')
    vs, vts, vns, tris = [], [], [], []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                vs.append(tuple(map(float, parts[1:4])))
            elif parts[0] == 'vt':
                vts.append(float(parts[1]))
            elif parts[0] == 'vn':
                vns.append(tuple(map(float, parts[1:4])))
            elif parts[0] == 'f':
                idx = [tuple(int(k) for k in p.split('/')) for p in parts[1:]]
                col = pal.getpixel((int(vts[idx[0][1] - 1] * pal.width), 0))
                nrm = vns[idx[0][2] - 1]
                pts = [vs[i[0] - 1] for i in idx]
                for k in range(1, len(pts) - 1):
                    tris.append(((pts[0], pts[k], pts[k + 1]), nrm, col))
    return tris


def render(tris, yaw, pitch, size=(560, 360), scale=820):
    import math
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)

    def xf(p):
        x, y, z = p
        x, z = x * cy - z * sy, x * sy + z * cy      # yaw around Y
        y, z = y * cp - z * sp, y * sp + z * cp      # pitch around X
        return x, y, z

    light = (0.45, 0.8, 0.4)
    W, H = size
    pts = [xf(p) for t in tris for p in t[0]]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cyy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    zbuf = [[-1e9] * W for _ in range(H)]
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    px = img.load()
    for (a, b, c), n, col in tris:
        nv = xf(n)
        if nv[2] <= 1e-6:      # back-facing (camera looks down -Z)
            continue
        lum = 0.55 + 0.45 * max(0.0, n[0] * light[0] + n[1] * light[1] + n[2] * light[2])
        shaded = tuple(min(255, int(ch * lum)) for ch in col) + (255,)
        P = []
        for p in (a, b, c):
            x, y, z = xf(p)
            P.append((W / 2 + (x - cx) * scale, H / 2 - (y - cyy) * scale, z))
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = P
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        for yy in range(max(0, int(min(y0, y1, y2))), min(H, int(max(y0, y1, y2)) + 2)):
            for xx in range(max(0, int(min(x0, x1, x2))), min(W, int(max(x0, x1, x2)) + 2)):
                fx, fy = xx + 0.5, yy + 0.5
                l0 = ((y1 - y2) * (fx - x2) + (x2 - x1) * (fy - y2)) / den
                l1 = ((y2 - y0) * (fx - x2) + (x0 - x2) * (fy - y2)) / den
                l2 = 1 - l0 - l1
                if l0 < -1e-6 or l1 < -1e-6 or l2 < -1e-6:
                    continue
                z = l0 * z0 + l1 * z1 + l2 * z2
                if z > zbuf[yy][xx]:
                    zbuf[yy][xx] = z
                    px[xx, yy] = shaded
    return img


def preview(obj_path, palette_png, out_path):
    import math
    tris = read_obj(obj_path, palette_png)
    views = [
        ('3/4 right', math.radians(-35), math.radians(18)),
        ('3/4 left', math.radians(180 + 35), math.radians(18)),
        ('right side', 0.0, 0.0),
        ('left side', math.radians(180), 0.0),
    ]
    tile = (560, 360)
    sheet = Image.new('RGBA', (tile[0] * 2, tile[1] * 2), (58, 64, 78, 255))
    d = ImageDraw.Draw(sheet)
    for i, (label, yaw, pitch) in enumerate(views):
        ox, oy = (i % 2) * tile[0], (i // 2) * tile[1]
        sheet.alpha_composite(render(tris, yaw, pitch, tile), (ox, oy))
        d.text((ox + 10, oy + 8), label, fill=(220, 225, 235, 255))
    sheet.convert('RGB').save(out_path)


def main():
    v = build()
    quads = greedy_mesh(v)
    obj = os.path.join(HERE, NAME + '.obj')
    mtl = os.path.join(HERE, NAME + '.mtl')
    tex = 'vx9_palette.png'
    write_palette_png(os.path.join(HERE, tex))
    nv, nf = write_obj(quads, obj, mtl, tex)
    write_vox(v, os.path.join(HERE, NAME + '.vox'))
    preview(obj, os.path.join(HERE, tex), os.path.join(HERE, 'preview.png'))
    lo, hi = bounds(v)
    print(f'{len(v)} voxels, size {hi[0]-lo[0]+1}x{hi[1]-lo[1]+1}x{hi[2]-lo[2]+1}, '
          f'{nv} verts, {nf} quads ({2*nf} tris)')


if __name__ == '__main__':
    main()
