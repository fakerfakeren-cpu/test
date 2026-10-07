import json,base64,numpy as np,sys,io
from PIL import Image
exec(open('readgltf.py').read().split('for n in d')[0])
im=Image.open(io.BytesIO(base64.b64decode(d['images'][0]['uri'].split(',',1)[1]))).convert('RGBA')
print(im.size); a=np.array(im)
row=a[2]
prev=None
for x in range(256):
    c=tuple(row[x])
    if c!=prev: print(x, (x+0.5)/256, '#%02x%02x%02x'%c[:3], c[3]); prev=c
im.resize((1024,64),Image.NEAREST).save('pistol_palette.png')
px=0.0531125069
allW=[]
for n in d['nodes']:
    if 'mesh' not in n or n['name']=='Muzzle_Att': continue
    p=d['meshes'][n['mesh']]['primitives'][0]
    W=acc(p['attributes']['POSITION'])*np.array(n['scale'])+np.array(n['translation'])
    allW.append(W)
    print(n['name'],'px min',((W.min(0))/px).round(2),'size px',((W.max(0)-W.min(0))/px).round(2))
W=np.vstack(allW); print('ALL size px',((W.max(0)-W.min(0))/px).round(2), 'studs',(W.max(0)-W.min(0)).round(4))
mz=d['nodes'][2]['translation']; print('muzzle att px',(np.array(mz)/px).round(2))
