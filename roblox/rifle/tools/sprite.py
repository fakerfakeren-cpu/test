# Rifle side-view sprite, 1 px = 1 voxel. Muzzle to the right (+x), up = -y.
import numpy as np
from PIL import Image
W,H=80,30
PAL={
 'O':'#1c1c1c',
 'Mh':'#d4ecfc','Ml':'#bcd4dc','Mm':'#a0b4c0','Md':'#7c8c94','Mp':'#5c6870',
 'Wl':'#9c5434','Wm':'#84341c','Wd':'#742c24','Wp':'#54241c',
 'Dl':'#4a5258','Dm':'#3a4046','Dd':'#2c3236',
 'Yh':'#f6e486','Yl':'#ecd062','Ym':'#dcbc46','Yd':'#bf9c36','Yp':'#8e7228',
}
P=np.full((H,W),'',dtype=object)
C=np.full((H,W),'',dtype=object)
def box(part,x0,x1,y0,y1):
    P[y0:y1+1,x0:x1+1]=part
def clear(x,y): P[y,x]=''

# ---------------- silhouette ----------------
for x in range(1,24):                      # stock: bottom 1 up per 4 across
    box('stock',x,x,6,13+min(5,(23-x)//4))
box('upper',24,62,5,8); box('upper',24,52,9,11)
box('forend',53,62,9,12)                   # wood forend hangs below the handguard
clear(61,12); clear(62,12)                 # front chamfer, 1 up per 2 across
box('rail',28,58,3,4)
box('sight',29,32,1,2); box('sight',55,57,1,2)
box('barrel',63,70,7,9)
box('muzzle',71,78,5,11); clear(78,5); clear(78,11)
box('lower',25,51,12,15); clear(50,15); clear(51,15)
box('guard',31,41,22,22); box('guard',41,41,16,21)
box('mag',42,49,16,26); box('mag',41,50,27,27)
for r,y in enumerate(range(16,28)):        # grip, 1 back per 2 down
    o=r//2; box('grip',28-o,33-o,y,y)
clear(23,27); clear(28,27)
box('trigger',36,37,16,17); box('trigger',37,37,18,19)
box('charge',49,51,6,8)

def isp(y,x,part): return 0<=y<H and 0<=x<W and P[y,x]==part
def solid(y,x): return 0<=y<H and 0<=x<W and P[y,x]!=''

# ---------------- base shading ----------------
def ramp(part,R):
    hi,lt,md,dk,dp=R
    for y in range(H):
        for x in range(W):
            if P[y,x]!=part: continue
            up=solid(y-1,x) and not isp(y-1,x,part)   # something else above
            if not isp(y-1,x,part): c= md if up else hi
            elif not isp(y-2,x,part) and not (solid(y-2,x) and not isp(y-2,x,part)): c=lt
            elif not isp(y+1,x,part): c=dp if solid(y+1,x) else dk
            else: c=md
            if not isp(y,x-1,part) and c==md: c=lt          # rear edge catches light
            C[y,x]=c
Y=('Yh','Yl','Ym','Yd','Yp'); M=('Mh','Ml','Mm','Md','Mp')
for p in ('stock','upper','lower','guard'): ramp(p,Y)
for p in ('rail','sight','barrel','muzzle','mag','charge','trigger'): ramp(p,M)

def put(c,pts):
    for x,y in pts: C[y,x]=c
def hline(c,x0,x1,y): put(c,[(x,y) for x in range(x0,x1+1)])
def vline(c,x,y0,y1): put(c,[(x,y) for y in range(y0,y1+1)])
def panel(R,x0,x1,y0,y1,stripe=None):
    """outlined inset: ring in dark shade, lighter inside, bright stripe"""
    hi,lt,md,dk,dp=R
    hline(dk,x0,x1,y0); hline(dk,x0,x1,y1); vline(dk,x0,y0,y1); vline(dk,x1,y0,y1)
    for y in range(y0+1,y1):
        hline(lt,x0+1,x1-1,y)
        put(md,[(x0+1,y)])                                 # shadowed inner end
    sy=stripe if stripe is not None else y0+1
    hline(hi,x0+2,x1-2,sy)

# ---------------- stock ----------------
vline('Yp',23,6,13)                         # hinge seam to receiver
put('Yl',[(23,8)]); put('Yd',[(23,10)])     # hinge knuckle
panel(Y,5,19,8,11,stripe=9)                 # cheek panel
for x in range(1,3):                        # rubber butt pad
    for y in range(6,19):
        C[y,x]= 'Dl' if (y==6 or (x==1 and y%3==0)) else ('Dd' if y==18 or x==2 and y%3==2 else 'Dm')
vline('Yp',3,6,17)
# ---------------- upper / handguard ----------------
panel(Y,31,42,6,8)                          # ejection port
hline('Yp',44,52,7)                         # charging-handle channel
put('Yp',[(27,7),(27,9)])                   # pins
for y in range(9,13):                       # wood forend: speckled, grooved like the shotgun pump
    for x in range(53,63):
        if P[y,x]!='forend': continue
        C[y,x]={9:'Wm',10:'Wm',11:'Wm',12:'Wd'}[y]
    C[y,53]='Wd'
put('Wl',[(54,9),(56,9),(59,9),(61,9),(62,9),(55,10),(61,10),(62,10),(57,11)])
for x in (55,58):
    put('Wp',[(x,11),(x,12)]); put('Wd',[(x,10)])
# ---------------- lower ----------------

put('Ml',[(29,13)]); put('Md',[(30,13)])        # selector lever
put('Ml',[(40,13)])                         # mag release
# ---------------- rail ----------------
for x in range(28,59):
    C[3,x]='Mh' if (x-28)%3!=2 else 'Md'
    C[4,x]='Md'
# ---------------- sights ----------------
put('Md',[(30,1),(31,1)])                   # rear aperture notch
# ---------------- barrel / muzzle ----------------
vline('Md',71,6,10)                         # collar seam
for x in (73,76):                           # vent slots
    vline('Mp',x,6,10)
put('Ml',[(74,6),(77,6)])
# ---------------- magazine ----------------
panel(M,43,48,18,24,stripe=19)
vline('Md',42,16,26)
hline('Mp',41,50,27) if False else None
# ---------------- charging handle ----------------
put('Mh',[(49,6),(50,6)]); put('Ml',[(49,7)]); put('Mm',[(50,7)]); put('Md',[(51,6),(51,7),(49,8),(50,8),(51,8)])
# ---------------- grip (wood) ----------------
for y in range(H):
    xs=[x for x in range(W) if P[y,x]=='grip']
    if not xs: continue
    a,b=min(xs),max(xs)
    for x in xs:
        C[y,x]='Wl' if x==b else 'Wd' if x==a else 'Wm'
put('Wl',[(31,17),(29,19),(31,20),(28,22),(29,24),(26,25),(27,27)])
put('Wd',[(32,18),(30,21),(28,24),(27,26)])
hline('Wd',28,33,16)

# ---------------- outline ----------------
for y in range(H):
    for x in range(W):
        if P[y,x]=='' and any(solid(y+dy,x+dx) for dy in(-1,0,1) for dx in(-1,0,1)):
            C[y,x]='O'

def render(scale=8,bg=None):
    im=Image.new('RGBA',(W,H),(0,0,0,0) if bg is None else bg); px=im.load()
    for y in range(H):
        for x in range(W):
            if C[y,x]:
                h=PAL[C[y,x]]; px[x,y]=tuple(int(h[i:i+2],16) for i in (1,3,5))+(255,)
    return im.resize((W*scale,H*scale),Image.NEAREST)
if __name__=='__main__':
    render(1).save('rifle_1x.png'); render(8,(128,128,128,255)).save('rifle_8x.png')
