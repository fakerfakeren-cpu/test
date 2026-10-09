"""Render player frames (first-person + outside, side by side) for every animation, plus a manifest."""
import json, os, sys, numpy as np
from PIL import Image
from anim_render import parse, Scene, first_person, outside
F, sizes, root = parse(sys.argv[2] if len(sys.argv) > 2 else 'out_1.txt'); sc = Scene('../../in_view/ScarView.gltf', sizes)
OUT = sys.argv[1]; os.makedirs(f'{OUT}/frames', exist_ok=True)
META = {
    'Scar_Idle':   dict(key='idle',   label='Idle',   fps=15, loop=True,  priority='Idle'),
    'Scar_Equip':  dict(key='equip',  label='Equip',  fps=60, loop=False, priority='Action'),
    'Scar_Shoot':  dict(key='shoot',  label='Shoot',  fps=60, loop=False, priority='Action'),
    'Scar_Reload': dict(key='reload', label='Reload', fps=30, loop=False, priority='Action2'),
}
manifest = []
for anim in ('Scar_Idle', 'Scar_Equip', 'Scar_Shoot', 'Scar_Reload'):
    m = META[anim]; frames = F[anim]; times = sorted(frames)
    src_fps = round(1 / (times[1] - times[0]))
    step = max(1, round(src_fps / m['fps']))
    sel = times[::step]
    if sel[-1] != times[-1]: sel.append(times[-1])
    for i, t in enumerate(sel):
        a = first_person(sc, frames[t], root, cam_off=(-0.6, 0.95, 0.5), W=480, H=270)
        b = outside(sc, frames[t], root, W=480, H=270, scale=118, centre=(0, 0.25, -1.45))
        im = Image.new('RGB', (960, 270)); im.paste(a, (0, 0)); im.paste(b, (480, 0))
        im.quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(f'{OUT}/frames/{m["key"]}_{i:03d}.png', optimize=True)
    manifest.append(dict(name=anim, key=m['key'], label=m['label'], fps=m['fps'], loop=m['loop'], priority=m['priority'],
                         length=round(times[-1], 3), frames=len(sel), times=[round(t, 4) for t in sel]))
    print(anim, len(sel), 'frames', flush=True)
json.dump(manifest, open(f'{OUT}/manifest.json', 'w'))
