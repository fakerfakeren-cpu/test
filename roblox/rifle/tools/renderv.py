import sys, importlib
from raster import render
from PIL import Image
import numpy as np
mod = importlib.import_module(sys.argv[1]); tag = sys.argv[2]
T, K, cols = mod.assembled()
views = {'left': (90, 0), 'right': (-90, 0), 'q34': (125, 25), 'rear34': (-55, 25), 'top': (90, 89.9)}
for name in (sys.argv[3:] or views):
    yaw, pitch = views[name]
    im = render(T, K, yaw, pitch, 8, ss=3, margin=16); im.save(f'{tag}_{name}.png')
    a = np.array(im.convert('RGB')).astype(int); bg = (np.abs(a - 128).sum(2) < 6); dark = (a.max(2) < 0x60) & ~bg
    print(name, im.size, 'dark share %.1f%%' % (100 * dark.sum() / (~bg).sum()))
