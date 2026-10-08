"""Render the replayed animations: first-person (perspective, near-plane clipped) and an outside 3/4 view."""
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loadexport import load

def parse(path):
    F = {}; sizes = {}; root = None
    for line in open(path):
        if line.startswith('F '):
            _, anim, t, part, *v = line.split()
            F.setdefault(anim, {}).setdefault(float(t), {})[part] = cf(list(map(float, v)))
        elif line.startswith('SIZE '):
            _, part, *v = line.split(); sizes[part] = np.array(list(map(float, v)))
        elif line.startswith('ROOT '):
            root = cf(list(map(float, line.split()[1:])))
    return F, sizes, root
def cf(v):
    M = np.eye(4); M[:3, 3] = v[:3]; M[:3, :3] = np.array(v[3:]).reshape(3, 3); return M

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

class Scene:
    def __init__(self, gltf, sizes):
        self.mesh = load(gltf)
        self.arm = box_tris(sizes['RightArm'])
        self.armcol = shade(self.arm, (163, 162, 165))
        # arm edges darker so the block reads in flat light
    def tris(self, pose):
        Ts, Cs = [], []
        for name, (T, C) in self.mesh.items():
            M = pose[name]; Ts.append(T @ M[:3, :3].T + M[:3, 3]); Cs.append(C)
        for name in ('RightArm', 'LeftArm'):
            M = pose[name]; Ts.append(self.arm @ M[:3, :3].T + M[:3, 3])
            Cs.append(self.armcol)
        return np.concatenate(Ts), np.concatenate(Cs)

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

def first_person(scene, pose, root, W=480, H=270, fov=70, cam_off=(0, 0, 0), ss=2):
    T, C = scene.tris(pose)
    cam = root.copy(); cam[:3, 3] = root[:3, :3] @ np.array(cam_off) + root[:3, 3]
    inv = np.linalg.inv(cam)
    Tc = T @ inv[:3, :3].T + inv[:3, 3]
    f = (H * ss / 2) / np.tan(np.radians(fov / 2))
    img = raster(Tc, C, W * ss, H * ss, f)
    return Image.fromarray(img).resize((W, H), Image.BOX)

def outside(scene, pose, root, yaw=118, pitch=18, scale=125, W=520, H=330, ss=2, centre=(0, 0.25, -1.45)):
    T, C = scene.tris(pose)
    y, p = np.radians(yaw), np.radians(pitch)
    fwd = np.array([np.sin(y) * np.cos(p), -np.sin(p), -np.cos(y) * np.cos(p)])
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    c = root[:3, :3] @ np.array(centre) + root[:3, 3]
    R = np.stack([right, up, -fwd])           # world -> camera axes
    Tc = (T - c) @ (root[:3, :3] @ R.T)       # camera axes defined in the viewmodel's frame
    img = raster(Tc, C, W * ss, H * ss, scale * ss, ortho=True)
    return Image.fromarray(img).resize((W, H), Image.BOX)

if __name__ == '__main__':
    F, sizes, root = parse(sys.argv[1]); scene = Scene(sys.argv[2], sizes)
    out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    cam_off = tuple(map(float, sys.argv[4].split(','))) if len(sys.argv) > 4 else (-0.6, 0.95, 0.5)
    only = sys.argv[5].split(',') if len(sys.argv) > 5 else None
    for anim, frames in F.items():
        if only and anim not in only: continue
        times = sorted(frames)
        step = max(1, round((times[1] - times[0]) ** -1 / (15 if 'Idle' in anim else 30))) if len(times) > 1 else 1
        sel = times[::step]
        if sel[-1] != times[-1]: sel.append(times[-1])
        fp = [first_person(scene, frames[t], root, cam_off=cam_off) for t in sel]
        ex = [outside(scene, frames[t], root) for t in sel]
        combo = [Image.fromarray(np.concatenate([np.array(a), np.array(b.resize((int(b.width * a.height / b.height), a.height)))], 1)) for a, b in zip(fp, ex)]
        dur = int(1000 * (sel[1] - sel[0])) if len(sel) > 1 else 100
        combo[0].save(f'{out}/{anim}.gif', save_all=True, append_images=combo[1:], duration=dur, loop=0)
        # contact sheet: 8 evenly spaced frames
        idx = np.linspace(0, len(combo) - 1, 8).round().astype(int)
        sheet = Image.new('RGB', (combo[0].width * 2, combo[0].height * 4), (30, 30, 30))
        for n, i in enumerate(idx):
            sheet.paste(combo[i], ((n % 2) * combo[0].width, (n // 2) * combo[0].height))
        sheet.save(f'{out}/{anim}_sheet.png')
        print(anim, len(sel), 'frames')
