"""Previews of the third-person animations: the R15 blocky rig as boxes plus the user's Scar meshes.

Usage: python -I render_char.py <Export.gltf> <out_dir> [check]
Writes <out_dir>/Idle.gif, Shoot.gif, Reload.gif (two views each); 'check' writes check.png only.
"""
import base64
import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'viewmodel_v3'))
import charcore as C  # noqa: E402
from meshrender import box_tris, raster, shade  # noqa: E402

SKIN, SHIRT, PANTS = (226, 190, 150), (70, 110, 160), (60, 64, 72)
COLOURS = {'Head': SKIN, 'UpperTorso': SHIRT, 'LowerTorso': PANTS}
for _s in ('Right', 'Left'):
    COLOURS.update({_s + 'UpperArm': SHIRT, _s + 'LowerArm': SKIN, _s + 'Hand': SKIN,
                    _s + 'UpperLeg': PANTS, _s + 'LowerLeg': PANTS, _s + 'Foot': PANTS})


def load_gun(path):
    d = json.load(open(path))

    def raw(bv):
        b = d['buffers'][bv['buffer']]['uri'].split(',', 1)[1]
        return base64.b64decode(b)[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]

    def acc(i):
        a = d['accessors'][i]
        dt = {5125: np.uint32, 5126: np.float32, 5121: np.uint8, 5123: np.uint16}[a['componentType']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        arr = np.frombuffer(raw(d['bufferViews'][a['bufferView']]), dt)
        return arr.reshape(-1, n) if n > 1 else arr

    def image(i):
        im = d['images'][i]
        data = raw(d['bufferViews'][im['bufferView']]) if 'bufferView' in im else base64.b64decode(im['uri'].split(',', 1)[1])
        return np.array(Image.open(io.BytesIO(data)).convert('RGB'))
    out = {}
    for n in d['nodes']:
        if n.get('name') not in ('Body', 'Magazine', 'Slide') or 'mesh' not in n: continue
        pr = d['meshes'][n['mesh']]['primitives'][0]
        P = acc(pr['attributes']['POSITION']).astype(float) * np.array(n.get('scale', [1, 1, 1]))
        I = acc(pr['indices']).reshape(-1, 3)
        pbr = d['materials'][pr['material']].get('pbrMetallicRoughness', {}) if 'material' in pr else {}
        if 'baseColorTexture' in pbr and 'TEXCOORD_0' in pr['attributes']:
            tex = image(d['textures'][pbr['baseColorTexture']['index']]['source']); th, tw = tex.shape[:2]
            uv = acc(pr['attributes']['TEXCOORD_0'])[I].mean(1)
            col = tex[np.clip((uv[:, 1] * th).astype(int), 0, th - 1), np.clip((uv[:, 0] * tw).astype(int), 0, tw - 1)]
        else:
            col = np.tile((np.array(pbr.get('baseColorFactor', [0.3, 0.3, 0.3, 1])[:3]) * 255).astype(np.uint8), (len(I), 1))
        out[n['name']] = (P[I], col.astype(np.uint8))
    return out


class Scene:
    def __init__(self, rig, gltf):
        self.rig, self.gun = rig, load_gun(gltf)
        self.boxes = {n: box_tris(np.asarray(s, float)) for n, s in rig.size.items()}
        self.cols = {n: shade(self.boxes[n], COLOURS[n]) for n in self.boxes}

    def tris(self, W, G):
        r = self.rig; Ts, Cs = [], []
        for n, B in self.boxes.items():
            M = W[n] if n in W else C.cf(p=r.centre[n])
            Ts.append(B @ M[:3, :3].T + M[:3, 3]); Cs.append(self.cols[n])
        for n, (Tm, col) in self.gun.items():
            M = G @ r.gun_parts[n]; Ts.append(Tm @ M[:3, :3].T + M[:3, 3]); Cs.append(col)
        return np.concatenate(Ts), np.concatenate(Cs)


def view(scene, W, G, yaw, pitch=12, scale=52, Wd=360, Hd=400, centre=(0.0, 2.9, -0.9), ss=2):
    Tw, Cc = scene.tris(W, G)
    y, p = np.radians(yaw), np.radians(pitch)
    fwd = np.array([np.sin(y) * np.cos(p), -np.sin(p), -np.cos(y) * np.cos(p)])   # yaw 0 = looking along -Z (from behind)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    Tc = (Tw - np.array(centre)) @ np.stack([right, up, -fwd]).T
    return Image.fromarray(raster(Tc, Cc, Wd * ss, Hd * ss, scale * ss, ortho=True, bg=(122, 134, 148))).resize((Wd, Hd), Image.BOX)


def label(img, text):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, 8 + 6 * len(text), 14], fill=(20, 20, 20)); d.text((4, 2), text, fill=(255, 255, 255))
    return img


VIEWS = [('front-right', -140, 12), ('right side', -90, 4)]

if __name__ == '__main__':
    gltf, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rig = C.Rig(gltf); P = C.Poser(rig); S = Scene(rig, gltf)
    if len(sys.argv) > 3 and sys.argv[3] == 'check':
        tiles = []
        fr = {a: P.sample(a) for a in ('Idle', 'Reload')}
        picks = [('Reload', t, 150, 12) for t in (0.16, 0.30, 0.46, 0.72, 0.83)]
        picks += [('Reload', t, -140, 12) for t in (0.92, 1.01, 1.07, 1.15, 1.30)]
        for a, t, yw, pt in picks:
            f = min(fr[a], key=lambda f: abs(f[0] - t))
            tiles.append(label(view(S, f[2], f[3], yw, pt, Wd=300, Hd=330, scale=48), f'{a} {f[0]:.2f}s yaw {yw}'))
        sheet = Image.new('RGB', (300 * 5, 330 * 2))
        for i, im in enumerate(tiles): sheet.paste(im, ((i % 5) * 300, (i // 5) * 330))
        sheet.save(os.path.join(out, 'check.png')); print('check.png')
        sys.exit()
    for a, (length, fps, loop, prio, fn) in C.ANIMS.items():
        frames = P.sample(a)
        step = max(1, fps // 30)
        imgs = []
        for t, Tm, W, G, lp in frames[::step]:
            row = [label(view(S, W, G, yw, pt), f'{a} {t:.2f}s  {name}') for name, yw, pt in VIEWS]
            im = Image.new('RGB', (360 * len(row), 400))
            for i, r_ in enumerate(row): im.paste(r_, (i * 360, 0))
            imgs.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
        dur = int(1000 / 30)
        hold = [dur] * len(imgs)
        if not loop: hold[-1] = 500
        imgs[0].save(os.path.join(out, a + '.gif'), save_all=True, append_images=imgs[1:], duration=hold, loop=0)
        print(a, len(imgs), 'frames')
