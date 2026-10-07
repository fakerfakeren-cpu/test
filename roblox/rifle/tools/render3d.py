import sys, time
from model3d import assembled
from raster import render
from PIL import Image
T,K,cols=assembled()
views={'left':(90,0),'right':(-90,0),'q34':(125,25)}
if len(sys.argv)>1: views={k:views[k] for k in sys.argv[1:]}
for name,(yaw,pitch) in views.items():
    t=time.time(); im=render(T,K,yaw,pitch,8,ss=3,margin=16); im.save(f'r3d_{name}.png'); print(name,im.size,round(time.time()-t,1),'s')

def dark_share(path):
    import numpy as np
    a=np.array(Image.open(path).convert('RGB')).astype(int)
    bg=(np.abs(a-128).sum(2)<6)
    dark=(a.max(2)<0x60)&~bg          # outline #1c1c1c + rubber #2c..#4a + AA blends into them
    return dark.sum()/(~bg).sum()
