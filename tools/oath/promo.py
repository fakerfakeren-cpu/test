"""Listing art for CurseForge and Modrinth, after promo/ART_DIRECTION.md ("Lantern Liturgy"): the square icon, a banner
and a cover, and cinematic gallery frames graded from the CI client test's real screenshots.

Darkness is the canvas and light the only ink: violet shadows, gold highlights, bloom and falling light where the eye
should rest, motes of magic that gather with the light, letterbox bars and engraved type.
    python3 -m tools.oath.promo
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter

from .effects import sigil_oath
from .logo import hexrgb

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'promo')
SHOTS = os.path.join(ROOT, 'docs/oathbound/ci')
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# the duet: cold shadows, warm light, ivory for the few words
INDIGO = np.array([0.50, 0.40, 1.00])
GOLD = np.array([1.10, 0.98, 0.74])
GOLD_LIGHT = hexrgb('#ffd88a')
EMBER = hexrgb('#ff9a48')
VIOLET = hexrgb('#9c74ff')
IVORY = (238, 230, 212)
BAR = (6, 4, 10)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def lum(a):
    return a @ np.array([0.2126, 0.7152, 0.0722])


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB')


def to_arr(im):
    return np.asarray(im.convert('RGB')).astype(np.float64) / 255


def gblur(a, sigma):
    if a.ndim == 3:
        return np.stack([gaussian_filter(a[..., c], sigma) for c in range(a.shape[2])], -1)
    return gaussian_filter(a, sigma)


# ====================================================================== the grade
def grade(a, strength=1.0):
    """Split-tone (violet shadows, gold highlights), an S-curve and a little more colour."""
    L = lum(a)[..., None]
    tint = INDIGO * (1 - L) + GOLD * L
    a = a * (1 + (tint - 1) * 0.55 * strength)
    s = a * a * (3 - 2 * np.clip(a, 0, 1))
    a = a + (s - a) * 0.45 * strength
    L = lum(a)[..., None]
    return np.clip(L + (a - L) * (1 + 0.15 * strength), 0, 1)


def bloom(a, w, amount=1.0):
    L = lum(a)[..., None]
    bright = np.clip((L - 0.55) / 0.45, 0, 1) * a
    glow = gblur(bright, w * 0.004) * 0.55 + gblur(bright, w * 0.018) * 0.55 + gblur(bright, w * 0.05) * 0.35
    return a + glow * GOLD * amount


def light_rays(a, source, strength=0.5, steps=28):
    """Light falling through thick air: the bright parts of the frame smeared toward a light source."""
    h, w = a.shape[:2]
    L = lum(a)
    mask = Image.fromarray((np.clip((L - 0.5) / 0.5, 0, 1) * 255).astype(np.uint8))
    px, py = source
    acc = np.zeros((h, w))
    for k in range(steps):
        s = 1 - k * 0.022
        m = mask.transform((w, h), Image.AFFINE, (s, 0, px * (1 - s), 0, s, py * (1 - s)), Image.BILINEAR)
        acc += np.asarray(m).astype(np.float64) / 255 * (1 - k / steps)
    acc = gblur(acc / steps * 2.2, w * 0.002)
    return a + acc[..., None] * GOLD_LIGHT * strength


def haze(a, amount=0.12):
    h = a.shape[0]
    t = np.linspace(0, 1, h)[:, None, None] ** 2.2
    return a * (1 - t * amount) + t * amount * hexrgb('#3a2468')


def vignette(a, amount=0.55):
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    r = np.hypot((x - w / 2) / (w / 2), (y - h / 2) / (h / 2)) / math.sqrt(2)
    f = np.clip((r - 0.35) / 0.65, 0, 1)
    return a * (1 - amount * f * f * (3 - 2 * f))[..., None]


def grain(a, amount=0.012, seed=7):
    g = np.random.default_rng(seed).normal(0, amount, a.shape[:2])
    return a + g[..., None]


def motes(a, n, seed, light=None, bias_low=0.5, violet_share=0.3, scale=1.0):
    """Magic as matter: soft motes in three depths, a few bokeh discs, the brightest struck into four-point glints.
    They gather toward the light (if any) and toward the lower frame, and thin out at the edges."""
    h, w = a.shape[:2]
    r = np.random.default_rng(seed)
    layers = {s: np.zeros((h, w, 3)) for s in (0.8, 1.6, 3.2, 11.0)}
    glints = []
    for i in range(n):
        if light is not None and r.random() < 0.45:
            x = int(np.clip(r.normal(light[0], w * 0.16), 0, w - 1))
            y = int(np.clip(r.normal(light[1] + h * 0.1, h * 0.18), 0, h - 1))
        else:
            x = int(r.random() * w)
            y = int(h * (1 - r.random() ** (1 + bias_low)))
        depth = r.choice([0.8, 1.6, 3.2, 11.0], p=[0.45, 0.33, 0.17, 0.05])
        col = VIOLET if r.random() < violet_share else (GOLD_LIGHT if r.random() < 0.7 else EMBER)
        amp = r.uniform(0.6, 1.0) * {0.8: 9, 1.6: 22, 3.2: 70, 11.0: 260}[depth] * scale
        layers[depth][y, x] += col * amp
        if depth in (1.6, 3.2) and r.random() < 0.06:
            glints.append((x, y, col, r.uniform(0.6, 1.0)))
    out = a.copy()
    for s, layer in layers.items():
        out += gblur(layer, s * scale * (w / 1920)) * (0.5 if s > 10 else 1.0)
    # four-point glints, like struck metal
    star = np.zeros((h, w, 3))
    for x, y, col, k in glints:
        ln = int(w * 0.012 * k)
        for d in range(-ln, ln + 1):
            f = (1 - abs(d) / (ln + 1)) ** 3 * 1.2 * k
            if 0 <= x + d < w:
                star[y, x + d] += col * f
            if 0 <= y + d < h:
                star[y + d, x] += col * f
    return out + gblur(star, 0.8) * 1.4


# ====================================================================== type
def text_layer(size, draw_fn):
    m = Image.new('L', size, 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m).astype(np.float64) / 255


def engrave(a, mask, colour_top, colour_bottom=None, glow=0.8, glow_colour=None):
    """Lays type into the image: a soft glow beneath, then the letters in a vertical gradient."""
    h, w = a.shape[:2]
    gc = glow_colour if glow_colour is not None else colour_top
    # a soft shadow first, so letters always part from whatever lies behind them
    a = a * (1 - np.clip(gblur(mask, w * 0.006) * 1.6, 0, 0.75))[..., None]
    g = gblur(mask, w * 0.004) * 0.9 + gblur(mask, w * 0.014) * 0.6
    a = a + g[..., None] * gc * glow
    ys = np.nonzero(mask.max(1) > 0.1)[0]
    if colour_bottom is None or not len(ys):
        fill = np.broadcast_to(colour_top, a.shape)
    else:
        t = np.clip((np.arange(h) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)[:, None, None]
        fill = colour_top * (1 - t) + colour_bottom * t
    return a * (1 - mask[..., None]) + fill * mask[..., None]


def spaced(text, gap):
    return (' ' * gap).join(text)


# ====================================================================== gallery frames
GALLERY = [
    # shot, title, subtitle, light source (fraction of frame) or None, ray strength
    ('morvane', 'The Hollow King', 'Three phases in a darkened arena, and four lanterns to light again.', (0.5, 0.3), 0.55),
    ('sundered_gate', 'The Sundered Gate', 'Three seals, one key, and a veil torn open into the Gloaming.', (0.5, 0.35), 0.6),
    ('sanctum_hall', 'The Keeper\'s Hall', 'Each keeper sleeps behind a puzzle. Wake it, if you are ready.', (0.5, 0.45), 0.6),
    ('gloaming_veilwood', 'The Veilwood', 'Violet groves where the Order hung its lanterns and never came back.', (0.75, 0.2), 0.35),
    ('portrait_caldris', 'Sir Caldris, the Drowned Knight', 'His shield turns every blow from the front. Flank him.', (0.5, 0.42), 0.45),
    ('tideglass_grotto', 'The Tideglass Grotto', 'A crystal sea cave, and the drowned choir that sings in it.', (0.5, 0.4), 0.5),
    ('crystal_cave', 'Lumenite in the Deep', 'Crystal that drinks the dark, growing in caves across the world.', (0.5, 0.45), 0.55),
    ('shattered_observatory', 'Where the Stars Went Out', 'A broken dome on a Gloaming island, and the wraiths that nest in it.', (0.5, 0.3), 0.4),
    ('hollow_throne', 'The Hollow Throne', 'The last climb. The crown is empty; so is the king.', (0.5, 0.35), 0.5),
    ('bog_mothers_house', 'The Mother of Hags', 'A stilt-house in the swamp, and three optional keepers in the wild.', (0.62, 0.3), 0.35),
    ('drowned_chapel', 'The Drowned Chapel', 'Ring the bells in the hymn\'s order and the crypt opens.', (0.12, 0.22), 0.5),
    ('chronicle_path', 'The Lantern Chronicle', 'A living book: the story, the Path, recipes, a bestiary and an armory.', None, 0.0),
]


def gallery(name, title, subtitle, light, rays, w=1920, h=1080):
    src = os.path.join(SHOTS, name + '.jpg')
    if not os.path.exists(src):
        return None
    im = Image.open(src).convert('RGB').resize((w, h), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=60, threshold=2))
    a = to_arr(im)
    ui = light is None
    a = grade(a, 0.35 if ui else 1.0)
    if not ui:
        src_px = (light[0] * w, light[1] * h)
        a = light_rays(a, src_px, rays)
        a = bloom(a, w, 0.9)
        a = haze(a)
        a = motes(a, 260, seed=hash(name) & 0xffff, light=src_px)
    else:
        a = bloom(a, w, 0.25)
        a = motes(a, 90, seed=11, light=None, bias_low=1.2)
    a = vignette(a, 0.5 if not ui else 0.35)
    a = grain(a, 0.011, seed=len(name))
    # the reliquary: cinematic bars
    bar = int(h * 0.105)
    a[:bar] = np.array(BAR) / 255
    a[h - bar:] = np.array(BAR) / 255
    # top bar: the wordmark, small and wide, between two rules and two diamonds
    mark = spaced('OATHBOUND', 2)
    fm = font('ArsenalSC-Regular.ttf', int(h * 0.021))
    def top(d):
        tw = d.textlength(mark, font=fm)
        cy = bar // 2
        d.text((w / 2, cy), mark, font=fm, fill=255, anchor='mm')
        for side in (-1, 1):
            x0 = w / 2 + side * (tw / 2 + 22)
            x1 = w / 2 + side * (tw / 2 + 170)
            d.line([(x0, cy), (x1, cy)], fill=120, width=1)
            d.polygon([(x1 + side * 6, cy), (x1, cy - 4), (x1 - side * 6, cy), (x1, cy + 4)], fill=170)
    a = engrave(a, text_layer((w, h), top), GOLD_LIGHT * 0.85, glow=0.35)
    # bottom bar: the title engraved, a thin rule, the line beneath in italic
    ft = font('Gloock-Regular.ttf', int(h * 0.044))
    fs = font('CrimsonPro-Italic.ttf', int(h * 0.027))
    margin = int(w * 0.05)
    base = h - bar // 2

    def bottom_title(d):
        d.text((margin, base), title, font=ft, fill=255, anchor='lm')
    tl = text_layer((w, h), bottom_title)
    a = engrave(a, tl, hexrgb('#ffe9b0'), hexrgb('#e2a24c'), glow=0.55)
    tw = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(title, font=ft)

    def bottom_sub(d):
        x = margin + tw + 34
        d.line([(x, base - int(h * 0.018)), (x, base + int(h * 0.018))], fill=150, width=1)
        d.text((x + 26, base + 1), subtitle, font=fs, fill=255, anchor='lm')
    sl = text_layer((w, h), bottom_sub)
    a = a * (1 - sl[..., None] * 0.82) + np.array(IVORY) / 255 * sl[..., None] * 0.82
    return to_img(a)


# ====================================================================== the icon
def nebula(n, seed):
    r = np.random.default_rng(seed)
    acc = np.zeros((n, n))
    for octave, (sig, amp) in enumerate([(n * 0.18, 1.0), (n * 0.08, 0.6), (n * 0.035, 0.35), (n * 0.015, 0.2)]):
        acc += gaussian_filter(r.standard_normal((n, n)), sig) * amp * sig
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc


def icon(n=512):
    y, x = np.mgrid[0:n, 0:n] / n
    cx, cy = 0.5, 0.5
    r = np.hypot(x - cx, y - cy)
    theta = np.arctan2(y - cy, x - cx)
    # night: a deep indigo heart falling to black, nebula breathing violet and a little teal through it
    a = hexrgb('#24124a') * np.clip(1 - r * 1.6, 0, 1)[..., None] + hexrgb('#05030b') * np.clip(r * 1.6, 0, 1)[..., None]
    neb = nebula(n, 3) ** 2.2
    neb2 = nebula(n, 9) ** 3
    a += neb[..., None] * hexrgb('#5a2aa8') * 0.55 + neb2[..., None] * hexrgb('#1f6f86') * 0.25
    # stars
    rs = np.random.default_rng(5)
    stars = np.zeros((n, n))
    for _ in range(int(n * 0.5)):
        stars[rs.integers(0, n), rs.integers(0, n)] = rs.uniform(0.3, 1.0) ** 3
    a += gaussian_filter(stars, 0.6)[..., None] * 3.0 * hexrgb('#e8e0ff')
    # the radiance behind the crown: sixteen rays, every other one longer
    rays = (0.5 + 0.5 * np.cos(theta * 16)) ** 14 * (0.5 + 0.5 * (0.5 + 0.5 * np.cos(theta * 8)))
    fall = np.exp(-((r - 0.02) / 0.3) ** 2)
    a += (rays * fall)[..., None] * GOLD_LIGHT * 0.4
    a += np.exp(-(r / 0.2) ** 2)[..., None] * EMBER * 0.18
    # the oath-circle, gilded light
    sig = np.clip(sigil_oath(int(n * 0.92)), 0, 1) ** 1.3
    full = np.zeros((n, n))
    o = (n - sig.shape[0]) // 2
    full[o:o + sig.shape[0], o:o + sig.shape[1]] = sig
    a += (full * 0.7 + gaussian_filter(full, n * 0.006) * 0.7 + gaussian_filter(full, n * 0.025) * 0.35)[..., None] * GOLD_LIGHT * 0.6
    im = to_img(a)
    im = crown(im, n)
    a = to_arr(im)
    # the flame of the Order beneath, a soft teardrop of white-gold
    fy, fx = 0.7, 0.5
    d = np.hypot((x - fx) / 0.022, (y - fy) / np.where(y < fy, 0.05, 0.026))
    flame = np.exp(-d ** 2)
    a += flame[..., None] * np.array([0.95, 0.75, 0.42]) + gaussian_filter(flame, n * 0.02)[..., None] * EMBER * 0.9
    a = motes(a, int(n * 0.14), seed=21, light=(n * 0.5, n * 0.5), bias_low=0.2, violet_share=0.35, scale=n / 1920 * 2.4)
    a = bloom(a, n, 0.4)
    a = vignette(a, 0.6)
    return to_img(a)


def crown(im, n):
    """The Hollow Crown: five points of shaded gold with a rim of light, an empty dark heart where a head should be,
    a crack down the front and three amethysts; a halo above it."""
    cx, cy, w = n / 2, n * 0.47, n * 0.25
    pts = [(cx - w * 0.92, cy + w * 0.42), (cx - w * 1.0, cy - w * 0.16), (cx - w * 0.62, cy + w * 0.06), (cx - w * 0.38, cy - w * 0.42),
           (cx - w * 0.17, cy + w * 0.02), (cx, cy - w * 0.64), (cx + w * 0.17, cy + w * 0.02), (cx + w * 0.38, cy - w * 0.42),
           (cx + w * 0.62, cy + w * 0.06), (cx + w * 1.0, cy - w * 0.16), (cx + w * 0.92, cy + w * 0.42)]
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    m = np.asarray(mask).astype(np.float64) / 255
    a = to_arr(im)
    # a shadow for weight
    a *= (1 - gaussian_filter(m, n * 0.02) * 0.55)[..., None]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float64)
    k = np.clip((yy - (cy - w * 0.64)) / (w * 1.06), 0, 1)
    gold = np.stack([np.interp(k, [0, .3, .62, 1], [.98, .90, .70, .42]), np.interp(k, [0, .3, .62, 1], [.88, .70, .47, .25]),
                     np.interp(k, [0, .3, .62, 1], [.62, .36, .20, .10])], -1)
    gold *= (1.1 - 0.3 * np.clip((xx - (cx - w)) / (2 * w), 0, 1))[..., None]
    # the band: a darker, engraved strip along the bottom where the gems sit, with a bright bead above and below
    band = ((yy > cy + w * 0.17) & (yy < cy + w * 0.42)).astype(np.float64)
    gold = gold * (1 - band[..., None] * 0.35)
    for by in (cy + w * 0.17, cy + w * 0.42 - 2):
        bead = np.exp(-((yy - by) / (n * 0.0025)) ** 2) * m
        gold += bead[..., None] * np.array([0.5, 0.42, 0.25])
    # rim light along every edge, brightest on top
    edge = np.clip(m - gaussian_filter(m, 1.6), 0, 1) * 2.4
    gold += (edge * np.clip(1.2 - k, 0, 1))[..., None] * np.array([1.0, 0.9, 0.6])
    a = a * (1 - m[..., None]) + np.clip(gold, 0, 1.4) * m[..., None]
    im = to_img(a)
    a = to_arr(im)
    # amethysts with their own light
    for gx in (-0.56, 0, 0.56):
        gx0, gy0 = cx + gx * w, cy + w * 0.3
        dd = np.hypot(xx - gx0, yy - gy0) / (n * 0.017)
        gem = np.clip(1 - dd, 0, 1) ** 0.5
        a = a * (1 - gem[..., None]) + gem[..., None] * (hexrgb('#3a1478') * (1 - gem[..., None]) + hexrgb('#9b5cf0') * gem[..., None])
        a += np.exp(-dd ** 2 * 0.2)[..., None] * VIOLET * 0.25
        hl = np.exp(-(np.hypot(xx - (gx0 - n * 0.006), yy - (gy0 - n * 0.006)) / (n * 0.004)) ** 2)
        a += hl[..., None] * 0.9
    # glints on the five points
    for px, py in (pts[1], pts[3], pts[5], pts[7], pts[9]):
        for dd2 in range(-int(n * 0.03), int(n * 0.03) + 1):
            f = (1 - abs(dd2) / (n * 0.03)) ** 3
            yi, xi = int(py), int(px)
            if 0 <= xi + dd2 < n:
                a[yi, xi + dd2] += np.array([1.0, 0.95, 0.8]) * f
            if 0 <= yi + dd2 < n:
                a[yi + dd2, xi] += np.array([1.0, 0.95, 0.8]) * f
    # the halo: a thin gold ellipse above the points
    ring = np.abs(np.hypot((xx - cx) / (w * 0.5), (yy - (cy - w * 0.86)) / (w * 0.11)) - 1)
    halo = np.exp(-(ring / 0.06) ** 2)
    a += halo[..., None] * GOLD_LIGHT * 0.9 + gaussian_filter(halo, n * 0.01)[..., None] * GOLD_LIGHT * 0.9
    return to_img(a)


# ====================================================================== banner and cover
def title_card(w, h, shot, title_scale=1.0):
    src = os.path.join(SHOTS, shot + '.jpg')
    a = to_arr(Image.open(src).convert('RGB').resize((w, h), Image.LANCZOS))
    a = grade(a, 1.0) * 0.55
    a = light_rays(a, (w * 0.5, h * 0.18), 0.45)
    a = bloom(a, w, 0.7)
    a = haze(a, 0.25)
    # the oath-circle, faint behind the title
    s = int(h * 0.92)
    sig = np.clip(sigil_oath(s), 0, 1)
    full = np.zeros((h, w))
    oy, ox = (h - s) // 2, (w - s) // 2
    full[oy:oy + s, ox:ox + s] = sig
    a += (full * 0.16 + gaussian_filter(full, h * 0.01) * 0.22)[..., None] * GOLD_LIGHT
    a = motes(a, int(w * 0.16), seed=31, light=(w * 0.5, h * 0.45), scale=w / 1920 * 1.0 + 0.4)
    a = vignette(a, 0.6)
    ft = font('Gloock-Regular.ttf', int(h * 0.2 * title_scale))
    fs = font('ArsenalSC-Regular.ttf', int(h * 0.055 * title_scale))
    sub = spaced('THE HOLLOW CROWN', 1)

    def title(d):
        d.text((w / 2, h * 0.46), 'OATHBOUND', font=ft, fill=255, anchor='mm')
    a = engrave(a, text_layer((w, h), title), hexrgb('#fff0c8'), hexrgb('#d68a3a'), glow=1.0, glow_colour=EMBER)

    def subtitle(d):
        tw = d.textlength(sub, font=fs)
        y0 = h * 0.64
        d.text((w / 2, y0), sub, font=fs, fill=255, anchor='mm')
        for side in (-1, 1):
            x0, x1 = w / 2 + side * (tw / 2 + h * 0.04), w / 2 + side * (tw / 2 + h * 0.22)
            d.line([(x0, y0), (x1, y0)], fill=170, width=max(1, h // 400))
            d.polygon([(x1 + side * h * 0.012, y0), (x1, y0 - h * 0.008), (x1 - side * h * 0.012, y0), (x1, y0 + h * 0.008)], fill=200)
    sl = text_layer((w, h), subtitle)
    a = engrave(a, sl, np.array(IVORY) / 255, glow=0.3, glow_colour=GOLD_LIGHT)
    a = grain(a, 0.01, seed=3)
    return to_img(a)


def generate():
    os.makedirs(OUT, exist_ok=True)
    big = icon(1024)
    big.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, 'icon.png'))
    big.resize((128, 128), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1, 60, 2)).save(os.path.join(OUT, 'icon_128.png'))
    title_card(1024, 512, 'gloaming_veilwood').save(os.path.join(OUT, 'banner.png'))
    title_card(1920, 1080, 'gloaming_veilwood').save(os.path.join(OUT, 'cover.jpg'), quality=92)
    for f in os.listdir(OUT):
        if f.startswith('gallery_'):
            os.remove(os.path.join(OUT, f))
    n = 0
    for i, (name, t, sub, light, rays) in enumerate(GALLERY, 1):
        g = gallery(name, t, sub, light, rays)
        if g is not None:
            g.save(os.path.join(OUT, f'gallery_{i:02d}_{name}.jpg'), quality=92)
            n += 1
    print('promo written:', n, 'gallery images')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'icon':
        icon(1024).resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, 'icon.png'))
    else:
        generate()
