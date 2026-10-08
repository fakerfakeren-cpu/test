import os, sys, importlib
import numpy as np
from raster import render
tag = 'v3b' if os.environ.get('RIFLE_SLIM') == '1' else 'v3a'
m = importlib.import_module('model3d_v3')
T, K, _ = m.assembled()
S = int(sys.argv[1]) if len(sys.argv) > 1 else 8
for name, (yaw, pitch) in {'left': (90, 0), 'right': (-90, 0), 'q34': (125, 25), 'rear34': (-55, 25)}.items():
    im = render(T, K, yaw, pitch, S, ss=3 if S <= 8 else 2, margin=16); im.save(f'{tag}_{name}.png')
    a = np.array(im.convert('RGB')).astype(int); bg = (np.abs(a - 128).sum(2) < 6); dark = (a.max(2) < 0x60) & ~bg
    print(tag, name, im.size, 'dark %.1f%%' % (100 * dark.sum() / (~bg).sum()))
TE, KE = m.exploded({'Body': (0, 0, 0), 'Magazine': (0, -9, 0), 'Slide': (-7, 0, 0)})
im = render(TE, KE, 125, 25, S, ss=3 if S <= 8 else 2, margin=16); im.save(f'{tag}_exploded.png')
im = render(TE, KE, -55, 25, S, ss=3 if S <= 8 else 2, margin=16); im.save(f'{tag}_exploded_rear.png')
