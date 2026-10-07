import json,base64,numpy as np,io,sys
from PIL import Image
sys.path.insert(0,'.')
from raster import render
d=json.load(open(sys.argv[1]))
def buf(i): return base64.b64decode(d['buffers'][i]['uri'].split(',',1)[1])
def acc(i):
    a=d['accessors'][i]; bv=d['bufferViews'][a['bufferView']]
    dt={5125:np.uint32,5126:np.float32,5121:np.uint8}[a['componentType']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    r=np.frombuffer(buf(bv['buffer']),dtype=dt); return r.reshape(-1,n) if n>1 else r
pal=np.array(Image.open(io.BytesIO(base64.b64decode(d['images'][0]['uri'].split(',',1)[1]))).convert('RGB'))[2]
px=0.0531125069
T=[];C=[]
for n in d['nodes']:
    if 'mesh' not in n or n['name']=='Muzzle_Att': continue
    p=d['meshes'][n['mesh']]['primitives'][0]
    V=acc(p['attributes']['POSITION'])*np.array(n['scale'])+np.array(n['translation'])
    UV=acc(p['attributes']['TEXCOORD_0']); I=acc(p['indices']).reshape(-1,3)
    for t in I:
        T.append(V[t]/px); C.append(pal[min(255,int(UV[t[0]][0]*256))])
T=np.array(T);C=np.array(C)
ims=[render(T,C,yaw,pitch,16) for yaw,pitch in [(90,0),(-90,0),(55,30),(-55,30),(0,0),(180,0),(30,-25)]]
W=sum(i.width for i in ims)+10*len(ims); H=max(i.height for i in ims)
out=Image.new('RGB',(W,H),(40,40,40)); x=0
for i in ims: out.paste(i,(x,0)); x+=i.width+10
out.save('pistol_views.png'); print(out.size)
