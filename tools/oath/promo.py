"""Listing art for CurseForge and Modrinth: the square icon, the banner, and captioned gallery images made from the
CI client test's real screenshots.  Run:  python3 -m tools.oath.promo
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .effects import blur, sigil_oath
from .logo import font, hexrgb

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'promo')
SHOTS = os.path.join(ROOT, 'docs/oathbound/ci')


def icon(n=512):
    y, x = np.mgrid[0:n, 0:n] / n
    r = np.hypot(x - 0.5, y - 0.5)
    # a violet dusk vignette with an ember glow at the heart
    bg = hexrgb('#1a1030') * (1 - r[..., None] * 1.2) + hexrgb('#07050d') * (r[..., None] * 1.2)
    bg = np.clip(bg + np.exp(-(r / 0.22) ** 2)[..., None] * hexrgb('#6a2a1a') * 0.8, 0, 1)
    sig = np.clip(sigil_oath(int(n * 0.9)), 0, 1) ** 1.4
    full = np.zeros((n, n))
    o = (n - sig.shape[0]) // 2
    full[o:o + sig.shape[0], o:o + sig.shape[1]] = sig
    glow = np.clip(full * 0.9 + blur(full, n * 0.01) * 0.8 + blur(full, n * 0.04) * 0.5, 0, 1)
    img = np.clip(bg + glow[..., None] * hexrgb('#ffc85a') * 0.85, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    # the Hollow Crown, cracked, over a lantern-flame
    cx, cy, w = n / 2, n * 0.47, n * 0.26
    crown = [(cx - w, cy + w * 0.45), (cx - w, cy - w * 0.15), (cx - w * 0.55, cy + w * 0.12), (cx - w * 0.28, cy - w * 0.42),
             (cx, cy - w * 0.05), (cx + w * 0.28, cy - w * 0.42), (cx + w * 0.55, cy + w * 0.12), (cx + w, cy - w * 0.15), (cx + w, cy + w * 0.45)]
    shadow = Image.new('L', im.size, 0)
    ImageDraw.Draw(shadow).polygon(crown, fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(n * 0.02))
    im = Image.composite(Image.new('RGB', im.size, (10, 6, 4)), im, shadow.point(lambda v: int(v * 0.7)))
    d = ImageDraw.Draw(im)
    # shaded gold: a metallic ramp from top to bottom, lit from the left, a darker band and bright tips
    cm = np.asarray(_flame_mask(im.size, crown)).astype(float) / 255
    band = np.asarray(_flame_mask(im.size, [(cx - w, cy + w * 0.2), (cx + w, cy + w * 0.2), (cx + w, cy + w * 0.45),
                                            (cx - w, cy + w * 0.45)])).astype(float) / 255 * cm
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    k = np.clip((yy - (cy - w * 0.42)) / (w * 0.87), 0, 1)
    gold = np.stack([np.interp(k, [0, 0.35, 0.6, 1], [1.0, 0.96, 0.78, 0.6]),
                     np.interp(k, [0, 0.35, 0.6, 1], [0.9, 0.76, 0.55, 0.38]),
                     np.interp(k, [0, 0.35, 0.6, 1], [0.6, 0.38, 0.22, 0.14])], -1)
    gold *= (1.08 - 0.25 * np.clip((xx - (cx - w)) / (2 * w), 0, 1))[..., None]
    gold = gold * (1 - band[..., None] * 0.28)
    edge = np.clip(cm - np.asarray(Image.fromarray((cm * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(max(3, n // 128 * 2 + 1)))) / 255, 0, 1)
    gold = gold * (1 - edge[..., None]) + edge[..., None] * hexrgb('#4a2408')
    base = np.asarray(im).astype(float) / 255
    im = Image.fromarray((np.clip(base * (1 - cm[..., None]) + np.clip(gold, 0, 1) * cm[..., None], 0, 1) * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    for tx, ty in ((cx - w, cy - w * 0.15), (cx - w * 0.28, cy - w * 0.42), (cx + w * 0.28, cy - w * 0.42), (cx + w, cy - w * 0.15)):
        rr = n * 0.012
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=(255, 244, 200))
    d.line([(cx + w * 0.05, cy - w * 0.02), (cx - w * 0.08, cy + w * 0.2), (cx + w * 0.06, cy + w * 0.44)], fill=(50, 22, 8), width=max(2, n // 80))
    gm = np.zeros((n, n))
    for gx in (-0.55, 0, 0.55):
        gm += np.exp(-(((xx - (cx + gx * w)) ** 2 + (yy - (cy + w * 0.32)) ** 2) / (n * 0.03) ** 2))
    im = Image.fromarray((np.clip(np.asarray(im).astype(float) / 255 + gm[..., None] * hexrgb('#a050ff') * 0.6, 0, 1) * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    for gx in (-0.55, 0, 0.55):
        gx0, gy0, rr = cx + gx * w, cy + w * 0.32, n * 0.02
        d.ellipse([gx0 - rr, gy0 - rr, gx0 + rr, gy0 + rr], fill=(150, 70, 240), outline=(60, 20, 110))
        d.ellipse([gx0 - rr * 0.55, gy0 - rr * 0.6, gx0 - rr * 0.05, gy0 - rr * 0.1], fill=(230, 200, 255))
    fl = [(cx, cy + w * 0.55), (cx + w * 0.16, cy + w * 0.85), (cx + w * 0.1, cy + w * 1.05), (cx, cy + w * 1.12), (cx - w * 0.1, cy + w * 1.05),
          (cx - w * 0.16, cy + w * 0.85)]
    m = np.asarray(_flame_mask(im.size, fl)).astype(float) / 255
    lit = np.asarray(im).astype(float) / 255 + blur(m, n * 0.03)[..., None] * hexrgb('#ff9a3a') * 0.9
    im = Image.fromarray((np.clip(lit, 0, 1) * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    d.polygon(fl, fill=(255, 226, 150))
    # a rim
    d.ellipse([n * 0.02, n * 0.02, n * 0.98, n * 0.98], outline=(214, 160, 70), width=max(2, n // 64))
    return im


def _flame_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def gallery(name, title, subtitle, w=1920, h=1080):
    src = os.path.join(SHOTS, name + '.jpg')
    if not os.path.exists(src):
        return None
    im = Image.open(src).convert('RGB').resize((w, h), Image.LANCZOS)
    bar = Image.new('L', (w, h), 0)
    ImageDraw.Draw(bar).rectangle([0, int(h * 0.8), w, h], fill=255)
    bar = bar.filter(ImageFilter.GaussianBlur(h * 0.06))
    im = Image.composite(Image.new('RGB', (w, h), (8, 5, 12)), im, bar.point(lambda v: int(v * 0.82)))
    d = ImageDraw.Draw(im)
    tf, sf = font(int(h * 0.062)), font(int(h * 0.03))
    d.text((int(w * 0.04), int(h * 0.83)), title, font=tf, fill=(255, 214, 130))
    d.text((int(w * 0.04), int(h * 0.915)), subtitle, font=sf, fill=(226, 216, 244))
    d.text((int(w * 0.96), int(h * 0.93)), 'OATHBOUND', font=font(int(h * 0.028)), fill=(214, 160, 70), anchor='ra')
    return im


GALLERY = [
    ('morvane', 'The Hollow King', 'Three phases, a darkened arena and four lanterns to relight.'),
    ('drowned_chapel', 'The Drowned Chapel', 'Ring the bells in the hymn\'s order to open the crypt.'),
    ('sanctum_hall', 'The Cinder Sanctum', 'A buried hall of magma where a sun-cult war-engine still burns.'),
    ('tideglass_grotto', 'The Tideglass Grotto', 'A crystal-lit sea cave and the drowned choir\'s shrine.'),
    ('crystal_cave', 'Lumenite in the Deep', 'Glowing crystal clusters grow on cave walls across the world.'),
    ('the_gloaming', 'The Gloaming', 'A dusk that never ends, over islands of moss, ash and violet forest.'),
    ('wild_keepers', 'The Wild Keepers', 'The Elderhorn, the Bog Mother and the Cinder Colossus, each in its own lair.'),
    ('spellcraft', 'Spellcraft', 'Rune circles, pillars of light, shockwaves and beams.'),
    ('chronicle_path', 'The Lantern Chronicle', 'A living quest book: the story, the Path, tithes, a bestiary and an armory.'),
    ('gloaming_veilwood', 'The Veilwood', 'Violet groves of the Gloaming, where the Order hung its lanterns and never came back for them.'),
    ('masonry', 'Five Stone Families', 'Wardstone, gloamstone, tidestone, barrowstone and runestone, and more.'),
    ('cinder_sanctum', 'The Places off the Path', 'Seven sites in seven kinds of country, none like another.'),
]


def generate():
    os.makedirs(OUT, exist_ok=True)
    icon(512).save(os.path.join(OUT, 'icon.png'))
    icon(128).save(os.path.join(OUT, 'icon_128.png'))
    Image.open(os.path.join(ROOT, 'src/main/resources/oathbound_logo.png')).save(os.path.join(OUT, 'banner.png'))
    n = 0
    for i, (name, t, sub) in enumerate(GALLERY, 1):
        g = gallery(name, t, sub)
        if g is not None:
            g.save(os.path.join(OUT, f'gallery_{i:02d}_{name}.jpg'), quality=90)
            n += 1
    print('promo written:', n, 'gallery images')


if __name__ == '__main__':
    generate()
