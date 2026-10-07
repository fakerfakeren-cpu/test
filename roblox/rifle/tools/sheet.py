from sprite import *
from PIL import Image, ImageDraw, ImageFont
sg=Image.open('../../images/1.webp').convert('RGBA')
pis=Image.open('pistol_side_8x.png').transpose(Image.FLIP_LEFT_RIGHT)
r8=render(8,(252,176,0,255)); r8g=render(8,(128,128,128,255))
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',13)
except: f=fs=ImageFont.load_default()
pad=24; Wd=544+pad*3+r8.width
out=Image.new('RGBA',(Wd,860),(36,36,36,255)); d=ImageDraw.Draw(out)
out.paste(sg,(pad,pad+20)); d.text((pad,pad-4),'Reference: shotgun (other artist)',fill='white',font=f)
x0=544+pad*2
d.text((x0,pad-4),'Rifle sprite, 80x29 px, shown 8x nearest-neighbour',fill='white',font=f)
out.paste(r8,(x0,pad+20)); out.paste(r8g,(x0,pad+40+r8.height))
y=pad+60+2*r8.height
d.text((x0,y),'Scale check at the same 8x: your pistol (30x18 px, flat render of the .gltf)',fill='white',font=f)
out.paste(pis,(x0,y+24))
# palette
py=600; d.text((pad,py),'Palette (hex)',fill='white',font=f)
rows=[('Outline',['O']),('Metal  hi/lt/mid/dk/seam',['Mh','Ml','Mm','Md','Mp']),('Wood   lt/mid/dk/deep',['Wl','Wm','Wd','Wp']),
      ('Yellow hi/lt/mid/dk/seam',['Yh','Yl','Ym','Yd','Yp']),('Rubber lt/mid/dk',['Dl','Dm','Dd'])]
for i,(name,keys) in enumerate(rows):
    yy=py+28+i*44; d.text((pad,yy+8),name,fill='white',font=fs)
    for j,k in enumerate(keys):
        xx=pad+220+j*120; d.rectangle([xx,yy,xx+32,yy+32],fill=PAL[k],outline='#000')
        d.text((xx+38,yy+9),PAL[k],fill='white',font=fs)
out.save('step1_sheet.png')
render(1).save('Rifle_sprite_1x.png'); render(8).save('Rifle_sprite_8x.png')
