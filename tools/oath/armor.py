"""Worn armour (equipment layers), equipment assets and spawn eggs.

Humanoid armour textures are 64x32 in vanilla's layout: head at (0,0), body at (16,16), arm at (40,16) and
leg at (0,16). Layer "humanoid" carries helmet, chestplate (body + arms) and boots (the lower leg); layer
"humanoid_leggings" carries the waist and the legs.

Run from the repository root:  python3 -m tools.oath.armor
"""
import json
import math
import os

import numpy as np

from .paint import Img, Ramp, hexrgb, BAYER4, noise
from .model import face_regions
from . import itemart as I

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')

HEAD = (0, 0, 8, 8, 8)
BODY = (16, 16, 8, 12, 4)
ARM = (40, 16, 4, 12, 4)
LEG = (0, 16, 4, 12, 4)


class Style:
    def __init__(self, ramp, trim, accent=None, seam=4, cloth=False, glow=None):
        self.ramp, self.trim, self.accent, self.seam, self.cloth, self.glow = ramp, trim, accent, seam, cloth, glow


def paint_box(img, box, style, rows=None, part='body', seed=1):
    u, v, w, h, d = box
    f = noise(32, 32, 4, seed, octaves=2)
    for face, (fx, fy, fw, fh) in face_regions(u, v, w, h, d).items():
        for y in range(fh):
            if rows is not None and face not in ('top', 'bottom') and not (rows[0] <= y < rows[1]):
                continue
            if rows is not None and face in ('top', 'bottom') and part != 'head' and face == 'top' and rows[0] > 0:
                continue
            for x in range(fw):
                n = f[(y * 3 + seed) % 32, (x * 3 + seed * 5) % 32]
                t = 0.5 + (n - 0.5) * 0.3
                if style.cloth:
                    t += 0.18 * math.sin(x * 1.7 + n * 2) - (y / max(1, fh)) * 0.1
                else:
                    if style.seam and y % style.seam == 0 and fh > 5:
                        t -= 0.22
                    elif style.seam and y % style.seam == 1 and fh > 5:
                        t += 0.16
                light = {'top': 1.12, 'bottom': 0.7, 'front': 1.0, 'back': 0.85, 'left': 0.9, 'right': 0.9}[face]
                t = t * light + BAYER4[y % 4, x % 4] * 0.08
                c = style.ramp.smooth(t)
                edge = x == 0 or x == fw - 1 or y == fh - 1
                if edge and fw > 2:
                    c[:3] *= 0.7
                img.px[fy + y, fx + x] = c
    return img


def trim_row(img, box, y_rel, style, faces=('front', 'back', 'left', 'right')):
    u, v, w, h, d = box
    for face, (fx, fy, fw, fh) in face_regions(u, v, w, h, d).items():
        if face not in faces or not (0 <= y_rel < fh):
            continue
        for x in range(fw):
            img.px[fy + y_rel, fx + x] = style.trim.smooth(0.55 + (0.25 if x % 3 == 0 else 0))


def emblem(img, box, style, pattern, oy=2):
    u, v, w, h, d = box
    fx, fy, fw, fh = face_regions(u, v, w, h, d)['front']
    ox = (fw - len(pattern[0])) // 2
    for j, row in enumerate(pattern):
        for i, ch in enumerate(row):
            if ch == '#':
                img.px[fy + oy + j, fx + ox + i] = (style.accent or style.trim).smooth(0.8)


def oathsteel():
    s = Style(Ramp('#1e2530', '#34404f', '#4f5e70', '#71839a', '#9fb2c6', '#dbe7f2'), Ramp('#6a4a12', '#b0801f', '#dcae3c', '#f6d670'),
              Ramp('#6a1016', '#b02a30', '#e05a50'))
    a = Img(64, 32)
    paint_box(a, HEAD, s, part='head', seed=3)
    # helm: eye slit and a gold crest
    fx, fy, fw, fh = face_regions(*HEAD)['front']
    for x in range(1, 7):
        a.px[fy + 3, fx + x] = hexrgb('#0a0c10')
    a.px[fy + 4, fx + 3] = hexrgb('#0a0c10')
    a.px[fy + 4, fx + 4] = hexrgb('#0a0c10')
    for face in ('front', 'back', 'left', 'right'):
        trim_row(a, HEAD, 0, s, (face,))
    tx, ty, tw, th = face_regions(*HEAD)['top']
    for y in range(th):
        a.px[ty + y, tx + 3] = s.trim.smooth(0.8)
        a.px[ty + y, tx + 4] = s.trim.smooth(0.6)
    paint_box(a, BODY, s, seed=5)
    trim_row(a, BODY, 0, s)
    trim_row(a, BODY, 11, s)
    emblem(a, BODY, s, [".#.", "###", ".#.", ".#."], 2)
    paint_box(a, ARM, s, seed=7)
    trim_row(a, ARM, 0, s)
    trim_row(a, ARM, 11, s)
    # boots: only the lower third of the leg
    paint_box(a, LEG, s, rows=(8, 12), seed=9)
    trim_row(a, LEG, 8, s)
    b = Img(64, 32)
    paint_box(b, BODY, s, rows=(8, 12), seed=11)
    trim_row(b, BODY, 8, s)
    paint_box(b, LEG, s, rows=(0, 10), seed=13)
    trim_row(b, LEG, 4, s)
    return a, b


def arcanist():
    s = Style(Ramp('#0b0f24', '#141c3d', '#1f2b5c', '#2e3f80', '#4658a8', '#6a80cc'), Ramp('#6a7288', '#9aa3b8', '#c8cfe0', '#f0f3fa'),
              Ramp('#3a2a9c', '#6f7cff', '#b0c4ff'), seam=0, cloth=True)
    a = Img(64, 32)
    paint_box(a, HEAD, s, part='head', seed=21)
    fx, fy, fw, fh = face_regions(*HEAD)['front']
    for y in range(2, 8):
        for x in range(1, 7):
            a.px[fy + y, fx + x] = np.zeros(4)     # the hood's opening shows the face
    for y in range(fh):
        a.px[fy + y, fx + 0] = s.trim.smooth(0.6)
        a.px[fy + y, fx + 7] = s.trim.smooth(0.6)
    paint_box(a, BODY, s, seed=23)
    trim_row(a, BODY, 0, s)
    for y in range(12):
        bx, by, bw, bh = face_regions(*BODY)['front']
        a.px[by + y, bx + 3] = s.trim.smooth(0.5)
        a.px[by + y, bx + 4] = s.trim.smooth(0.7)
    emblem(a, BODY, s, ["#.#", ".#.", "#.#"], 3)
    paint_box(a, ARM, s, seed=25)
    trim_row(a, ARM, 10, s)
    trim_row(a, ARM, 11, s)
    paint_box(a, LEG, s, rows=(9, 12), seed=27)
    trim_row(a, LEG, 9, s)
    b = Img(64, 32)
    paint_box(b, BODY, s, rows=(7, 12), seed=29)
    trim_row(b, BODY, 7, s)
    paint_box(b, LEG, s, rows=(0, 11), seed=31)
    return a, b


def hollow_crown():
    """A crown on the head layer only: a black-gold band with five spikes and a violet gem."""
    gold = Ramp('#2e2410', '#4a3a16', '#6e5620', '#9a7a30', '#c8a448', '#f0d070')
    a = Img(64, 32)
    for face, (fx, fy, fw, fh) in face_regions(0, 0, 8, 8, 8).items():
        if face in ('top', 'bottom'):
            continue
        for x in range(fw):
            for y in range(0, 3):
                a.px[fy + y, fx + x] = gold.smooth(0.55 + (0.25 if y == 0 else 0) + (0.1 if x % 2 else 0))
    # spikes stand on the hat layer (the 'overlay' box at 32,0), which is drawn a little larger than the head
    for face, (fx, fy, fw, fh) in face_regions(32, 0, 8, 8, 8).items():
        if face in ('top', 'bottom'):
            continue
        for x in range(fw):
            if x % 3 == 1:
                a.px[fy + 0, fx + x] = gold.smooth(0.9)
                a.px[fy + 1, fx + x] = gold.smooth(0.7)
    fx, fy, fw, fh = face_regions(0, 0, 8, 8, 8)['front']
    a.px[fy + 1, fx + 3] = hexrgb('#d9a8ff')
    a.px[fy + 1, fx + 4] = hexrgb('#a35cff')
    return a


EGGS = {
    'lanternmoth': ('#9a6d34', '#ffe08a'), 'gloamling': ('#2a1840', '#ffe066'), 'forsworn_knight': ('#3a3f48', '#b02a30'),
    'barrow_wight': ('#44686b', '#9ffff0'), 'animated_tome': ('#5e361d', '#efe0b8'), 'veilhound': ('#221a33', '#b884ff'),
    'spectral_housecarl': ('#7fd6cf', '#e9fffc'), 'sir_caldris': ('#2f5a4b', '#3fe0c0'), 'archmage_veyl': ('#1f2b5c', '#c8cfe0'),
    'hrodgar': ('#b6aa8e', '#3b3d46'), 'morvane': ('#1c1924', '#a35cff'),
}


def ramp_of(h):
    c = hexrgb(h)
    stops = []
    for k in (0.35, 0.55, 0.75, 0.9, 1.05, 1.25):
        cc = np.clip(c[:3] * k + (0.05 if k > 1 else 0), 0, 1)
        stops.append('#%02x%02x%02x' % tuple(int(v * 255) for v in cc))
    return Ramp(*stops)


def write(rel, obj):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def generate():
    eq = os.path.join(ASSETS, 'textures/entity/equipment')
    a, b = oathsteel()
    a.save(os.path.join(eq, 'humanoid/oathsteel.png'))
    b.save(os.path.join(eq, 'humanoid_leggings/oathsteel.png'))
    a, b = arcanist()
    a.save(os.path.join(eq, 'humanoid/arcanist.png'))
    b.save(os.path.join(eq, 'humanoid_leggings/arcanist.png'))
    hollow_crown().save(os.path.join(eq, 'humanoid/hollow_crown.png'))
    write('equipment/oathsteel.json', {'layers': {'humanoid': [{'texture': 'oathbound:oathsteel'}],
                                                  'humanoid_leggings': [{'texture': 'oathbound:oathsteel'}]}})
    write('equipment/arcanist.json', {'layers': {'humanoid': [{'texture': 'oathbound:arcanist'}],
                                                 'humanoid_leggings': [{'texture': 'oathbound:arcanist'}]}})
    write('equipment/hollow_crown.json', {'layers': {'humanoid': [{'texture': 'oathbound:hollow_crown'}]}})
    for i, (mob, (base, spots)) in enumerate(EGGS.items()):
        name = f'{mob}_spawn_egg'
        I.spawn_egg(ramp_of(base), ramp_of(spots), 400 + i).save(os.path.join(ASSETS, 'textures/item', name + '.png'))
        write(f'models/item/{name}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'oathbound:item/{name}'}})
        write(f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': f'oathbound:item/{name}'}})
    print('armour, equipment and spawn eggs written')


if __name__ == '__main__':
    generate()
