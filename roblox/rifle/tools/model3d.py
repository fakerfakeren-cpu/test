"""Rifle voxel model built from the approved sprite.
Index space (i,j,k): i = width (-i = gun's LEFT), j = up, k = along the sprite x (muzzle at high k).
World (Roblox): X = i, Y = j, Z = -k  -> muzzle points -Z, +Y up, gun's right = +X.
Every voxel face gets one palette colour. Side faces (+-X) show the sprite; the other faces are
painted like little sprites: dark border on convex silhouette edges, bright rim inside it, fill colour."""
import numpy as np
from sprite import P as _P, C, PAL, W, H
P=_P.copy()
for _y in range(H):                        # rubber butt pad is paint-only in the sprite: give it its own part
    for _x in range(W):
        if str(C[_y,_x]).startswith('D'): P[_y,_x]='butt'

def width_of(part, x):
    if part == 'sight': return 5 if x < 45 else 3
    return {'stock':7,'butt':7,'upper':7,'forend':7,'rail':5,'barrel':3,'muzzle':5,
            'lower':5,'guard':3,'grip':5,'mag':5,'trigger':1}[part]
MAT = {'stock':'Y','upper':'Y','lower':'Y','guard':'Y','butt':'D','grip':'W','forend':'W',
       'rail':'M','sight':'M','barrel':'M','muzzle':'M','mag':'M','trigger':'M','charge':'M'}
GROUP = {'mag':'Magazine','trigger':'Trigger','charge':'Slide'}
def group_of(part): return GROUP.get(part,'Body')

# side-face colours: the sprite, but the receiver under the charging handle shows the bare channel
CS = C.copy()
for y in range(H):
    for x in range(W):
        if P[y,x]=='charge': CS[y,x]={6:'Yl',7:'Yp',8:'Ym'}[y]

# ---- who owns each pixel (part pixels + outline ring pixels) ----
OWN = np.full((H,W),'',dtype=object)
for y in range(H):
    for x in range(W):
        if P[y,x]: OWN[y,x] = 'upper' if P[y,x]=='charge' else P[y,x]
PRIO = {'trigger':3,'mag':2}
for y in range(H):
    for x in range(W):
        if C[y,x]!='O': continue
        cand=[P[y+dy,x+dx] for dy,dx in ((-1,0),(1,0),(0,-1),(0,1))
              if 0<=y+dy<H and 0<=x+dx<W and P[y+dy,x+dx] and P[y+dy,x+dx]!='charge']
        if not cand:
            cand=[P[y+dy,x+dx] for dy in (-1,0,1) for dx in (-1,0,1)
                  if 0<=y+dy<H and 0<=x+dx<W and P[y+dy,x+dx] and P[y+dy,x+dx]!='charge']
        if 'trigger' in cand: OWN[y,x]='trigger'; continue
        OWN[y,x]=max(cand,key=lambda p:(width_of(p,x),PRIO.get(p,0)))

# ---- voxels ----
V={}   # (i,j,k) -> dict
for y in range(H):
    for x in range(W):
        p=OWN[y,x]
        if not p: continue
        w=width_of(p,x)
        for i in range(-(w//2),w//2+1):
            V[(i,H-1-y,x)]=dict(part=p,x=x,y=y,ring=(C[y,x]=='O'))
for y in range(H):                        # charging handle knob sticks out of the LEFT side
    for x in range(W):
        if P[y,x]=='charge':
            for i in (-4,-5): V[(i,H-1-y,x)]=dict(part='charge',x=x,y=y,ring=False)

DIRS={'L':(-1,0,0),'R':(1,0,0),'top':(0,1,0),'bottom':(0,-1,0),'front':(0,0,1),'back':(0,0,-1)}
FACE={ # orientation -> (rim, fill)
 'Y':{'top':('Yh','Yl'),'back':('Yh','Yl'),'front':('Ym','Yd'),'bottom':('Ym','Yd'),'dk':'Yd','dp':'Yp'},
 'M':{'top':('Mh','Ml'),'back':('Mh','Ml'),'front':('Mm','Md'),'bottom':('Mm','Md'),'dk':'Md','dp':'Mp'},
 'W':{'top':('Wl','Wm'),'back':('Wl','Wm'),'front':('Wm','Wd'),'bottom':('Wm','Wd'),'dk':'Wd','dp':'Wp'},
 'D':{'top':('Dl','Dm'),'back':('Dl','Dm'),'front':('Dm','Dd'),'bottom':('Dm','Dd'),'dk':'Dd','dp':'Dd'},
}
def add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def inplane(d): return [e for e in DIRS.values() if all(e[t]*d[t]==0 for t in range(3))]

def exposed(v,d,solid): return add(v,d) not in solid
def run(v,d,e,solid):
    """length of the coplanar exposed strip through v along axis e"""
    n=1
    for s in (1,-1):
        u=v
        while True:
            u=add(u,tuple(s*c for c in e))
            if u in solid and exposed(u,d,solid): n+=1
            else: break
    return n

def paint_faces(solid, faces_of=None):
    """returns {(v,dname): colour}. solid = voxels used for exposure tests (assembled model)."""
    out={}; outline={}
    keys=[(v,dn) for v in V for dn,d in DIRS.items() if exposed(v,d,solid)] if faces_of is None else faces_of
    # pass 1: outline / seam classification
    cls={}
    for v,dn in keys:
        d=DIRS[dn]; info=V[v]
        if dn in ('L','R'): continue
        conv=False; seam=False; tiny=False
        for e in inplane(d):
            u=add(v,e)
            axis=tuple(abs(c) for c in e)
            if u not in solid:
                if run(v,d,axis,solid)>=3 and info['part']!='charge': conv=True
                else: tiny=True
            elif add(u,d) in solid:
                if V[add(u,d)]['part']!=info['part']: seam=True
            elif V[u]['part']!=info['part']: seam=True
        cls[(v,dn)]=('O' if conv else 'seam' if seam else 'tiny' if tiny else '')
    # pass 2: colours
    for v,dn in keys:
        info=V[v]; part=info['part']; x,y=info['x'],info['y']
        if dn in ('L','R'):
            if part=='charge': out[(v,dn)]= C[y,x] if dn=='L' else 'Mp'
            else: out[(v,dn)]=CS[y,x]
            continue
        m=MAT[part]; F=FACE[m]; c=cls[(v,dn)]; d=DIRS[dn]
        if c=='O': out[(v,dn)]='O'; continue
        if c=='seam': out[(v,dn)]=F['dp']; continue
        if c=='tiny': out[(v,dn)]=F['dk']; continue
        near=any(cls.get((add(v,e),dn))=='O' for e in inplane(d) if add(v,e) in solid)
        rim,fill=F[dn]
        col= rim if near else fill
        # ---- hand-placed decoration on non-side faces ----
        i,j,k=v
        if part=='rail' and dn=='top' and C[3,x]=='Md': col='Md'                 # rail cross-slots
        if part=='muzzle' and dn in('top','bottom') and x in (73,76): col='Mp'    # vent slots
        if part=='muzzle' and dn=='front':                                        # bore
            if (i,y)==(0,8): col='O'
            elif (abs(i),abs(y-8)) in ((1,0),(0,1)): col='Mp'
        if part=='butt' and dn=='back':                                           # rubber grooves
            col='Dd' if y%3==2 else 'Dl' if y%3==0 else 'Dm'
        if m=='W' and not near:                                                   # wood speckle
            h=(i*3+j*5+k*7)%7
            if dn in('top','back') and h==0: col='Wl'
            if dn in('top','back','front') and h==3: col='Wd'
        if part=='forend' and dn=='bottom' and x in (55,58): col='Wp'             # grooves wrap under
        out[(v,dn)]=col
    return out

def cell(v):
    i,j,k=v
    return (i-0.5,i+0.5),(j,j+1),(-k-1,-k)
def quad(v,dn):
    (x0,x1),(y0,y1),(z0,z1)=cell(v)
    n={'L':(-1,0,0),'R':(1,0,0),'top':(0,1,0),'bottom':(0,-1,0),'front':(0,0,-1),'back':(0,0,1)}[dn]
    if n[0]: x=x1 if n[0]>0 else x0; q=[(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]
    elif n[1]: y=y1 if n[1]>0 else y0; q=[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)]
    else: z=z1 if n[2]>0 else z0; q=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]
    q=np.array(q,float)
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),n)<0: q=q[::-1]
    return q,np.array(n)

def hexrgb(h): return tuple(int(h[t:t+2],16) for t in (1,3,5))
def assembled():
    solid=set(V)
    cols=paint_faces(solid)
    T=[];K=[]
    for (v,dn),c in cols.items():
        q,_=quad(v,dn); rgb=hexrgb(PAL[c])
        T+= [q[[0,1,2]],q[[0,2,3]]]; K+=[rgb,rgb]
    return np.array(T),np.array(K,np.uint8),cols
if __name__=='__main__':
    T,K,cols=assembled()
    print('voxels',len(V),'faces',len(cols),'tris',len(T))
