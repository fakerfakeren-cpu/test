from PIL import Image, ImageDraw, ImageFont
from model3d import V
ims={n:Image.open(f'r3d_{n}.png') for n in ('left','q34','rear34','right')}
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)
fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
G=(128,128,128); pad=20
Wd=ims['left'].width+ims['q34'].width+pad*3
Hh=40+ims['left'].height+30+ims['rear34'].height+30+40+150
out=Image.new('RGB',(Wd,Hh),G); d=ImageDraw.Draw(out)
d.text((pad,10),'Rifle, step 2: voxel model, unlit/flat colours, 1 voxel = 8 px, neutral grey background',fill='black',font=fb)
y=44
d.text((pad,y),'LEFT VIEW (gun\'s left side, muzzle = -Z)',fill='black',font=f)
d.text((pad*2+ims['left'].width,y),'3/4 VIEW (front-left, from above)',fill='black',font=f)
out.paste(ims['left'],(pad,y+24)); out.paste(ims['q34'],(pad*2+ims['left'].width,y+24))
y2=y+24+max(ims['left'].height,ims['q34'].height)+16
d.text((pad,y2),'extra: right side (matches the approved sprite exactly)',fill='black',font=f)
d.text((pad*2+ims['left'].width,y2),'extra: 3/4 from rear-right',fill='black',font=f)
out.paste(ims['right'],(pad,y2+24)); out.paste(ims['rear34'],(pad*2+ims['left'].width,y2+24))
y3=y2+24+max(ims['right'].height,ims['rear34'].height)+14
xs=[v[0] for v in V]; ys=[v[1] for v in V]; zs=[v[2] for v in V]
lines=[
 f'Size: {max(zs)-min(zs)+1} long x {max(ys)-min(ys)+1} tall x 7 wide voxels (9 at the charging handle) = '
 f'{(max(zs)-min(zs)+1)*0.0531125:.3f} x {(max(ys)-min(ys)+1)*0.0531125:.3f} x {7*0.0531125:.3f} studs',
 'Widths (voxels, including the 1-voxel outline edge, like the pistol): stock 7, rubber butt pad 7, upper receiver + handguard 7, wood forend 7,',
 '  lower receiver 5, pistol grip 5, magazine 5, top rail 5, rear sight 5, front sight 3, trigger guard 3, barrel 3, muzzle device 5, trigger 1,',
 '  charging handle: 3x3 knob sticking 2 voxels out of the LEFT side.',
 'Parts for export: Body (everything else) | Magazine | Slide (charging handle) | Trigger',
]
for t,l in enumerate(lines): d.text((pad,y3+t*22),l,fill='black',font=fs)
out.save('step2_sheet.png'); print(out.size)
