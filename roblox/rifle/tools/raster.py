"""Tiny unlit z-buffer rasterizer: flat colour per triangle, orthographic camera."""
import numpy as np
from PIL import Image

def look(yaw_deg, pitch_deg):
    """camera basis. yaw rotates around +Y, pitch tilts down. Returns (right, up, fwd) rows."""
    y=np.radians(yaw_deg); p=np.radians(pitch_deg)
    fwd=np.array([np.sin(y)*np.cos(p), -np.sin(p), -np.cos(y)*np.cos(p)])  # direction camera looks
    right=np.cross(fwd,[0,1,0]); right/=np.linalg.norm(right)
    up=np.cross(right,fwd)
    return right,up,fwd

def render(tris, cols, yaw, pitch, scale, bg=(128,128,128), margin=12, ss=3, size=None, center=None, backface=True):
    """tris: (N,3,3) world, cols: (N,3) uint8. scale = screen px per world unit (before ss)."""
    right,up,fwd=look(yaw,pitch)
    V=tris.reshape(-1,3)
    sx=V@right; sy=-(V@up); dz=V@fwd
    if center is None:
        c=np.array([(sx.min()+sx.max())/2,(sy.min()+sy.max())/2])
    else: c=center
    if size is None:
        w=int((sx.max()-sx.min())*scale)+2*margin; h=int((sy.max()-sy.min())*scale)+2*margin
    else: w,h=size
    S=scale*ss; W,H=w*ss,h*ss
    px=(sx-c[0])*S+W/2; py=(sy-c[1])*S+H/2
    P=np.stack([px,py,dz],1).reshape(-1,3,3)
    zb=np.full((H,W),np.inf); img=np.zeros((H,W,3),np.uint8); img[:]=bg
    for t,col in zip(P,cols):
        (x0,y0,z0),(x1,y1,z1),(x2,y2,z2)=t
        area=(x1-x0)*(y2-y0)-(x2-x0)*(y1-y0)
        if abs(area)<1e-9: continue
        if backface and area>0: pass
        minx=max(int(np.floor(min(x0,x1,x2))),0); maxx=min(int(np.ceil(max(x0,x1,x2))),W-1)
        miny=max(int(np.floor(min(y0,y1,y2))),0); maxy=min(int(np.ceil(max(y0,y1,y2))),H-1)
        if minx>maxx or miny>maxy: continue
        xs,ys=np.meshgrid(np.arange(minx,maxx+1)+0.5,np.arange(miny,maxy+1)+0.5)
        w0=((x1-xs)*(y2-ys)-(x2-xs)*(y1-ys))/area
        w1=((x2-xs)*(y0-ys)-(x0-xs)*(y2-ys))/area
        w2=1-w0-w1
        eps=-1e-6
        m=(w0>=eps)&(w1>=eps)&(w2>=eps)
        if not m.any(): continue
        z=w0*z0+w1*z1+w2*z2
        sub=zb[miny:maxy+1,minx:maxx+1]
        m&=z<sub-1e-7
        sub[m]=z[m]
        img[miny:maxy+1,minx:maxx+1][m]=col
    im=Image.fromarray(img)
    if ss>1: im=im.resize((w,h),Image.BOX)
    return im
