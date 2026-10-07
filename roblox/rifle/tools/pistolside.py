import json,base64,numpy as np,io,sys
from PIL import Image,ImageDraw
d=json.load(open(sys.argv[1]))
def buf(i): return base64.b64decode(d['buffers'][i]['uri'].split(',',1)[1])
def acc(i):
    a=d['accessors'][i]; bv=d['bufferViews'][a['bufferView']]
    dt={5125:np.uint32,5126:np.float32,5121:np.uint8}[a['componentType']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    r=np.frombuffer(buf(bv['buffer']),dtype=dt); return r.reshape(-1,n) if n>1 else r
pal=np.array(Image.open(io.BytesIO(base64.b64decode(d['images'][0]['uri'].split(',',1)[1]))).convert('RGB'))[2]
px=0.0531125069; S=8
tris=[]
for n in d['nodes']:
    if 'mesh' not in n or n['name']=='Muzzle_Att': continue
    p=d['meshes'][n['mesh']]['primitives'][0]
    V=acc(p['attributes']['POSITION'])*np.array(n['scale'])+np.array(n['translation'])
    UV=acc(p['attributes']['TEXCOORD_0']); I=acc(p['indices']).reshape(-1,3)
    for t in I:
        a,b,c=V[t]; nrm=np.cross(b-a,c-a)
        if nrm[0]<=1e-9: continue           # faces pointing +X only
        col=pal[min(255,int(UV[t[0]][0]*256))]
        tris.append((V[t][:,0].max(),V[t],tuple(col)))
tris.sort(key=lambda t:t[0])
allv=np.vstack([t[1] for t in tris]); zmin,ymax=allv[:,2].min(),allv[:,1].max()
w=int(round((allv[:,2].max()-zmin)/px)); h=int(round((ymax-allv[:,1].min())/px))
im=Image.new('RGBA',(w*S,h*S),(128,128,128,255)); dr=ImageDraw.Draw(im)
for _,v,col in tris:
    dr.polygon([((z-zmin)/px*S,(ymax-y)/px*S) for x,y,z in v],fill=col)
im.save('pistol_side_8x.png'); print(w,h)
