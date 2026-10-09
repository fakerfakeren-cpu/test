"""Render player frames (in-game hip camera + outside view side by side), GIF previews and a manifest.

Usage: python -I render_player.py <frames.json> <gltf> <player_dir> <gif_dir>
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render2 import Scene, view, outside  # noqa: E402
from vmcore import from_list  # noqa: E402

frames_path, gltf, PDIR, GDIR = sys.argv[1:5]
os.makedirs(f'{PDIR}/frames', exist_ok=True); os.makedirs(GDIR, exist_ok=True)
F = json.load(open(frames_path))
scene = Scene(gltf, F['sizes']['RightArm'])
META = {
    'Idle':   dict(key='idle', fps=15, loop=True, priority='Idle'),
    'Equip':  dict(key='equip', fps=60, loop=False, priority='Action'),
    'Shoot':  dict(key='shoot', fps=60, loop=False, priority='Action2'),
    'Reload': dict(key='reload', fps=30, loop=False, priority='Action3'),
}
manifest = []
for anim in ('Idle', 'Equip', 'Shoot', 'Reload'):
    m = META[anim]
    frs = F['frames'][anim]
    times = [f['t'] for f in frs]
    src_fps = round(1 / (times[1] - times[0]))
    step = max(1, round(src_fps / m['fps']))
    idx = list(range(0, len(frs), step))
    if idx[-1] != len(frs) - 1:
        idx.append(len(frs) - 1)
    gif = []
    for n, i in enumerate(idx):
        W = {k: from_list(v) for k, v in frs[i]['W'].items()}
        a = view(scene, W, Wd=480, Hd=270)
        b = outside(scene, W, Wd=480, Hd=270, scale=88, centre=(0.0, 0.25, -1.25))
        im = Image.new('RGB', (960, 270)); im.paste(a, (0, 0)); im.paste(b, (480, 0))
        im.quantize(colors=160, method=Image.Quantize.MEDIANCUT).save(f'{PDIR}/frames/{m["key"]}_{n:03d}.png', optimize=True)
        gif.append(im)
    dur = int(round(1000 * (times[idx[1]] - times[idx[0]])))
    gif[0].save(f'{GDIR}/Scar_{anim}.gif', save_all=True, append_images=gif[1:], duration=dur, loop=0, optimize=True)
    manifest.append(dict(name='Scar_' + anim, key=m['key'], label=anim, fps=m['fps'], loop=m['loop'], priority=m['priority'],
                         length=round(times[-1], 4), frames=len(idx), times=[round(times[i], 4) for i in idx],
                         markers=[[round(t, 4), n_, v] for t, n_, v in F['markers'][anim]]))
    print(anim, len(idx), 'frames', flush=True)
json.dump(manifest, open(f'{PDIR}/manifest.json', 'w'))
