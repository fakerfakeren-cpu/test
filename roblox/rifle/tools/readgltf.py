import json,base64,numpy as np,sys
d=json.load(open(sys.argv[1]))
def buf(i): return base64.b64decode(d['buffers'][i]['uri'].split(',',1)[1])
def acc(i):
    a=d['accessors'][i]; bv=d['bufferViews'][a['bufferView']]
    raw=buf(bv['buffer'])
    dt={5125:np.uint32,5126:np.float32,5121:np.uint8}[a['componentType']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    return np.frombuffer(raw,dtype=dt).reshape(-1,n) if n>1 else np.frombuffer(raw,dtype=dt)
for n in d['nodes']:
    print(n['name'], {k:n[k] for k in n if k in('translation','scale')}, n.get('extras',{}).get('Color'), n.get('extras',{}).get('RobloxInstanceType'))
for m,node in [(d['meshes'][n['mesh']],n) for n in d['nodes'] if 'mesh' in n]:
    p=m['primitives'][0]; P=acc(p['attributes']['POSITION']).astype(np.float64)
    s=np.array(node.get('scale',[1,1,1]))
    W=P*s
    print('\n==',m['name'],'verts',len(P),'tris',len(acc(p['indices']))//3)
    print(' local min',P.min(0),'max',P.max(0))
    print(' scaled min',W.min(0).round(4),'max',W.max(0).round(4),'size',(W.max(0)-W.min(0)).round(4))
    for ax in range(3):
        u=np.unique(np.round(W[:,ax],4)); dd=np.diff(u)
        print(' axis',ax,'unique',len(u),'min step',dd[dd>1e-4].min() if len(dd) else None, 'steps', np.unique(np.round(dd,4))[:8])
    C=acc(p['attributes']['COLOR_0']); print(' colors',np.unique(C,axis=0)[:6])
    UV=acc(p['attributes']['TEXCOORD_0']); print(' uv u',np.unique(np.round(UV[:,0],4))[:20],' v',np.unique(np.round(UV[:,1],4)))
