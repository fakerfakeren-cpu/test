"""Pixel-art PLAY button for a Roblox main menu.

Everything is drawn on the 64 x 24 base grid as flat colours and only ever
scaled with nearest-neighbour, so each base pixel is a solid 8 x 8 block in
the exported 512 x 192 PNGs (no antialiasing, no blur, no gradients).

Grid layout (y = row, 0 at the top):
  rows 0..21  button body (outline + face), stepped 2-px corners
  rows 22..23 hard drop shadow (the body silhouette shifted down 2 px)
Inside the body:
  row 0          outline
  rows 1..2      top highlight, row 1 carries the shine (3 px short of each end)
  rows 3..16     face fill (white 2x1 glint at x 2..3, row 4)
  row 17         crease line (one step darker than the bevel)
  rows 18..20    bottom bevel
  row 21         outline

  python3 make_button.py         step-2 state sheet into preview/, the 3 game PNGs into export/
  python3 make_button.py step1   re-renders the step-1 colour previews
"""
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 64, 24          # whole PNG on the base grid, shadow included
SHADOW = 2
BODY_H = H - SHADOW    # 22
CUT = 2                # staircase depth of each corner
SCALE = 8              # export scale -> 512 x 192

FACE_TOP, FACE_BOTTOM = 3, 16
GLINT = (4, 2)         # (row, first column) of the 2x1 glint


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


OUTLINE = hexc('#1B1F2A')
WHITE = hexc('#FFFFFF')
CLEAR = (0, 0, 0, 0)

SETS = {
    'A': dict(name='green', fill='#4CD137', hi='#7EE85A', shine='#C8FF9E', bevel='#2E9A22'),
    'B': dict(name='yellow', fill='#FFC21A', hi='#FFD95A', shine='#FFF2B0', bevel='#D18A00'),
    'C': dict(name='blue', fill='#2F9BFF', hi='#6BBBFF', shine='#C4E6FF', bevel='#1C63C9'),
}


def palette(key):
    """The spec colours plus the derived crease colour.

    The spec does not give the crease (face/bevel separator) a hex value, so it
    takes one more step down the set's own ramp: the per-channel ratio that maps
    fill -> bevel, applied again to the bevel.
    """
    s = SETS[key]
    p = {k: hexc(v) for k, v in s.items() if k != 'name'}
    f, b = p['fill'], p['bevel']
    p['crease'] = tuple(round(b[i] * b[i] / f[i]) if f[i] else 0 for i in range(3)) + (255,)
    p['text_shadow'] = p['bevel']
    p['name'] = s['name']
    return p


def to_hex(c):
    return '#%02X%02X%02X' % c[:3]


STATES = ('normal', 'hover', 'pressed')
PRESSED_DARKEN = 0.88


def state_palette(p, state):
    """Colours for one button state.

    hover:   fill and highlight go one step up the set's own ramp (fill takes the
             highlight colour, highlight takes the shine colour). The shine goes to
             white, otherwise it would match the new highlight and vanish.
    pressed: every face colour slightly darker (x0.88); outline, glint and the
             white text stay as they are.
    """
    q = dict(p)
    if state == 'hover':
        q.update(fill=p['hi'], hi=p['shine'], shine=WHITE)
    elif state == 'pressed':
        for k in ('fill', 'hi', 'shine', 'bevel', 'crease', 'text_shadow'):
            q[k] = tuple(round(v * PRESSED_DARKEN) for v in p[k][:3]) + (255,)
    return q


# --------------------------------------------------------------------------- masks

def stepped_mask(w, h, cut=CUT):
    """Rectangle with each corner cut as a staircase: the first row loses `cut`
    pixels at each end, the next loses cut-1, and so on."""
    m = np.ones((h, w), bool)
    for i in range(cut):
        n = cut - i
        for y in (i, h - 1 - i):
            m[y, :n] = False
            m[y, w - n:] = False
    return m


def edge(m):
    """Pixels of m that touch the outside through one of their 4 neighbours."""
    p = np.pad(m, 1)
    inner = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return m & ~inner


def shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = m[ys, xs]
    return out


def dilate(m, r=2):
    """Grow a mask by r pixels, leaving out the far corners so outlines get a
    one-step chamfer instead of square blobs."""
    out = np.zeros_like(m)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if r > 1 and abs(dx) == r and abs(dy) == r:
                continue
            out |= shift(m, dx, dy)
    return out


# --------------------------------------------------------------------------- glyphs

# Bold 7-row blocky caps: 2-px stems, 1-px bars.
GLYPHS = {
    'P': ['#####.',
          '##..##',
          '##..##',
          '#####.',
          '##....',
          '##....',
          '##....'],
    'L': ['##...',
          '##...',
          '##...',
          '##...',
          '##...',
          '##...',
          '#####'],
    'A': ['.####.',
          '##..##',
          '##..##',
          '######',
          '##..##',
          '##..##',
          '##..##'],
    'Y': ['##..##',
          '##..##',
          '##..##',
          '.####.',
          '..##..',
          '..##..',
          '..##..'],
    'O': ['.####.',
          '##..##',
          '##..##',
          '##..##',
          '##..##',
          '##..##',
          '.####.'],
    'U': ['##..##',
          '##..##',
          '##..##',
          '##..##',
          '##..##',
          '##..##',
          '.####.'],
    'R': ['#####.',
          '##..##',
          '##..##',
          '#####.',
          '##.##.',
          '##..##',
          '##..##'],
    'G': ['.####.',
          '##..##',
          '##....',
          '##.###',
          '##..##',
          '##..##',
          '.####.'],
    'M': ['##...##',
          '###.###',
          '#######',
          '##.#.##',
          '##...##',
          '##...##',
          '##...##'],
    'E': ['######',
          '##....',
          '##....',
          '#####.',
          '##....',
          '##....',
          '######'],
    ' ': ['...'] * 7,
}

# Play triangle, same height as the letters, 6 px wide (2-px steps, blunt tip).
PLAY_ICON = ['#.....',
             '###...',
             '#####.',
             '######',
             '#####.',
             '###...',
             '#.....']

GLYPH_H = 7
TRACKING = 1           # empty columns between letters
ICON_GAP = 6           # columns between the triangle and the P
TEXT_TOP = 6           # glyph top row on the body grid
TEXT_OUTLINE = 2


def bitmap(rows):
    return np.array([[c == '#' for c in r] for r in rows], bool)


def word_mask(text, tracking=TRACKING):
    parts = [bitmap(GLYPHS[c]) for c in text]
    w = sum(p.shape[1] for p in parts) + tracking * (len(parts) - 1)
    m = np.zeros((GLYPH_H, w), bool)
    x = 0
    for p in parts:
        m[:, x:x + p.shape[1]] = p
        x += p.shape[1] + tracking
    return m


def label_mask(icon=True):
    """PLAY (and optionally the triangle) as one mask, before outlining."""
    word = word_mask('PLAY')
    if not icon:
        return word
    tri = bitmap(PLAY_ICON)
    m = np.zeros((GLYPH_H, tri.shape[1] + ICON_GAP + word.shape[1]), bool)
    m[:, :tri.shape[1]] = tri
    m[:, tri.shape[1] + ICON_GAP:] = word
    return m


def stamp(canvas, mask, x, y, color):
    """Paint mask (placed with its top-left at x, y) onto an RGBA canvas."""
    h, w = mask.shape
    region = canvas[y:y + h, x:x + w]
    region[mask] = color


def outlined(mask, fill, outline, shadow, r=TEXT_OUTLINE):
    """Return an RGBA patch: fill-coloured mask, r-px outline, 1-px drop shadow
    under the outline. The patch is padded so nothing is clipped."""
    pad = r + 1
    m = np.pad(mask, pad)
    ring = dilate(m, r)
    under = shift(ring, 0, 1) & ~ring
    out = np.zeros(m.shape + (4,), np.uint8)
    out[under] = shadow
    out[ring] = outline
    out[m] = fill
    return out, pad


def paste(canvas, patch, x, y):
    a = patch[..., 3] > 0
    h, w = a.shape
    canvas[y:y + h, x:x + w][a] = patch[a]


# --------------------------------------------------------------------------- button

def body(p):
    m = stepped_mask(W, BODY_H)
    inside = m & ~edge(m)
    img = np.zeros((BODY_H, W, 4), np.uint8)
    img[m] = OUTLINE
    img[inside] = p['fill']
    for y in (1, 2):
        img[y][inside[y]] = p['hi']
    xs = np.flatnonzero(inside[1])
    img[1, xs[0] + 3:xs[-1] - 3 + 1] = p['shine']
    img[FACE_BOTTOM + 1][inside[FACE_BOTTOM + 1]] = p['crease']
    for y in range(FACE_BOTTOM + 2, BODY_H - 1):
        img[y][inside[y]] = p['bevel']
    gy, gx = GLINT
    img[gy, gx:gx + 2] = WHITE
    return img, m


def button(p, text=True, icon=True, state='normal'):
    """64 x 24 RGBA base-grid button. Pressed drops the face 2 px into where
    the shadow was, so the silhouette and canvas stay identical."""
    p = state_palette(p, state)
    pressed = state == 'pressed'
    canvas = np.zeros((H, W, 4), np.uint8)
    img, m = body(p)
    dy = SHADOW if pressed else 0
    if not pressed:
        sh = np.zeros((H, W), bool)
        sh[SHADOW:SHADOW + BODY_H] = m
        canvas[sh] = OUTLINE
    region = canvas[dy:dy + BODY_H]
    region[m] = img[m]
    if text:
        patch, pad = outlined(label_mask(icon), WHITE, OUTLINE, p['text_shadow'])
        lw = patch.shape[1] - 2 * pad
        paste(canvas, patch, (W - lw) // 2 - pad, TEXT_TOP - pad + dy)
    return canvas


def upscale(a, k=SCALE):
    return np.repeat(np.repeat(a, k, axis=0), k, axis=1)


def save(a, path, k=SCALE):
    Image.fromarray(upscale(a, k), 'RGBA').save(path, optimize=True)


# --------------------------------------------------------------------------- previews

FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def checker(w, h, cell=16, c1=(232, 234, 239, 255), c2=(214, 218, 226, 255)):
    yy, xx = np.mgrid[0:h, 0:w]
    a = np.empty((h, w, 4), np.uint8)
    a[:] = c1
    a[((yy // cell) + (xx // cell)) % 2 == 1] = c2
    return a


def side_by_side(path):
    """The three sets at export size (8x), with and without the icon, on a
    transparency checker so the silhouette and shadow read exactly."""
    gap, margin, head, row_label = 48, 56, 70, 40
    bw, bh = W * SCALE, H * SCALE
    rows = [('PLAY + icon', dict(text=True, icon=True)),
            ('PLAY only', dict(text=True, icon=False)),
            ('base for Roblox (no text)', dict(text=False))]
    cw = margin * 2 + bw * 3 + gap * 2
    ch = margin + head + len(rows) * (row_label + bh + gap) - gap + margin
    sheet = Image.new('RGBA', (cw, ch), (246, 247, 250, 255))
    d = ImageDraw.Draw(sheet)
    for i, key in enumerate('ABC'):
        p = palette(key)
        x = margin + i * (bw + gap)
        d.text((x, margin), f'{key}  {p["name"]}', font=font(34), fill=(27, 31, 42, 255))
        sw = ', '.join(to_hex(p[k]) for k in ('fill', 'hi', 'shine', 'bevel', 'crease'))
        d.text((x, margin + 42), sw, font=font(15), fill=(90, 96, 112, 255))
        for j, (label, kw) in enumerate(rows):
            y = margin + head + j * (row_label + bh + gap)
            if i == 0:
                d.text((x, y), label, font=font(20), fill=(90, 96, 112, 255))
            bg = Image.fromarray(checker(bw, bh), 'RGBA')
            art = Image.fromarray(upscale(button(p, **kw)), 'RGBA')
            bg.alpha_composite(art)
            sheet.paste(bg, (x, y + row_label))
    sheet.convert('RGB').save(path, optimize=True)


# Phone: iPhone 13/14 class, landscape, 844 x 390 pt. Roblox UI on iOS is laid
# out in points, so this is the GUI coordinate space the button lives in.
PHONE_PT = (844, 390)
PT_PER_PX = 4          # button drawn at 4 pt per base pixel -> 256 x 96 pt
SCENE = (PHONE_PT[0] // PT_PER_PX + 1, PHONE_PT[1] // PT_PER_PX + 1)   # 212 x 98 art px


def scene(p, seed=7):
    """Original dark pixel-art menu backdrop: banded night sky, stars, two
    layers of blocky skyline, ground, title placeholder, the PLAY button."""
    sw, sh = SCENE
    rnd = random.Random(seed)
    a = np.zeros((sh, sw, 4), np.uint8)
    bands = ['#090C15', '#0C1120', '#10172B', '#141E37', '#192643']
    edges = [0, 22, 40, 54, 66, sh]
    for i, c in enumerate(bands):
        a[edges[i]:edges[i + 1]] = hexc(c)
    for _ in range(70):
        x, y = rnd.randrange(sw), rnd.randrange(0, 62)
        a[y, x] = hexc(rnd.choice(['#2C3754', '#3A4870', '#56658E']))
    for _ in range(7):
        x, y = rnd.randrange(3, sw - 3), rnd.randrange(3, 50)
        c = hexc('#7F90BA')
        a[y, x - 1:x + 2] = c
        a[y - 1:y + 2, x] = c
        a[y, x] = hexc('#C4CFEA')
    # dim moon, top right
    yy, xx = np.mgrid[0:sh, 0:sw]
    mx, my, r = sw - 30, 16, 8
    moon = (xx - mx) ** 2 + (yy - my) ** 2 <= r * r
    a[moon] = hexc('#26324F')
    a[moon & ((xx - mx + 3) ** 2 + (yy - my + 2) ** 2 <= 4)] = hexc('#1F2944')
    a[moon & ((xx - mx - 3) ** 2 + (yy - my - 3) ** 2 <= 2)] = hexc('#1F2944')
    ground = 90

    def skyline(color, hmin, hmax, wmin, wmax, windows=None):
        x = -rnd.randrange(0, 6)
        while x < sw:
            bw, bh = rnd.randrange(wmin, wmax), rnd.randrange(hmin, hmax)
            x0, x1, y0 = max(0, x), min(sw, x + bw), ground - bh
            a[y0:ground, x0:x1] = hexc(color)
            if rnd.random() < 0.35 and x1 - x0 > 4:   # antenna / tank on the roof
                ax = x0 + rnd.randrange(1, x1 - x0 - 1)
                a[y0 - rnd.randrange(2, 5):y0, ax] = hexc(color)
            if windows:
                for wy in range(y0 + 2, ground - 2, 3):
                    for wx in range(x0 + 1, x1 - 1, 3):
                        if rnd.random() < windows[1]:
                            a[wy, wx] = hexc(windows[0])
            x += bw + rnd.randrange(0, 3)

    skyline('#111A2D', 22, 42, 8, 16)
    skyline('#0A0F1B', 10, 28, 6, 13, windows=('#2A3961', 0.18))
    a[ground:] = hexc('#0B101C')
    a[ground, :] = hexc('#1A2440')
    for x in range(rnd.randrange(4), sw, 9):   # paving seams
        a[ground + 2:, x] = hexc('#080C16')

    # title placeholder, glyphs at 2x so the pixel size stays on the same grid
    t = word_mask('YOUR GAME')
    t = np.repeat(np.repeat(t, 2, 0), 2, 1)
    patch, pad = outlined(t, WHITE, OUTLINE, hexc('#2A3554'), r=2)
    tw = t.shape[1]
    paste(a, patch, (sw - tw) // 2 - pad, 14 - pad)

    btn = button(p)
    bx, by = (sw - W) // 2, 54
    region = a[by:by + H, bx:bx + W]
    on = btn[..., 3] > 0
    region[on] = btn[on]
    return a


def screen(p, k):
    """The menu scene at k device pixels per point, cropped to the screen."""
    art = Image.fromarray(upscale(scene(p), PT_PER_PX * k), 'RGBA')
    return art.crop((0, 0, PHONE_PT[0] * k, PHONE_PT[1] * k))


def phone(p, k):
    """Scene in a phone frame, k device pixels per point."""
    art = screen(p, k)
    sw, sh = art.size
    bez = 18 * k
    fw, fh = sw + 2 * bez, sh + 2 * bez
    ss = 2   # supersample only the frame shapes, never the art
    frame = Image.new('RGBA', (fw * ss, fh * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((0, 0, fw * ss - 1, fh * ss - 1), radius=62 * k * ss, fill=(44, 46, 54, 255))
    d.rounded_rectangle((3 * k * ss, 3 * k * ss, fw * ss - 1 - 3 * k * ss, fh * ss - 1 - 3 * k * ss),
                        radius=59 * k * ss, fill=(10, 10, 12, 255))
    frame = frame.resize((fw, fh), Image.LANCZOS)
    mask = Image.new('L', (sw * ss, sh * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw * ss - 1, sh * ss - 1), radius=47 * k * ss, fill=255)
    mask = mask.resize((sw, sh), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)
    frame.paste(art, (bez, bez), mask)
    notch = Image.new('RGBA', (32 * k * ss, 210 * k * ss), (0, 0, 0, 0))
    ImageDraw.Draw(notch).rounded_rectangle((-40 * k * ss, 0, 32 * k * ss - 1, 210 * k * ss - 1),
                                            radius=20 * k * ss, fill=(10, 10, 12, 255))
    notch = notch.resize((32 * k, 210 * k), Image.LANCZOS)
    frame.alpha_composite(notch, (bez, bez + (sh - 210 * k) // 2))
    return frame


def overview(path):
    shots = [phone(palette(k), 1) for k in 'ABC']
    gap, margin, label = 28, 40, 44
    w = shots[0].width + 2 * margin
    h = margin + len(shots) * (label + shots[0].height + gap) - gap + margin
    sheet = Image.new('RGBA', (w, h), (246, 247, 250, 255))
    d = ImageDraw.Draw(sheet)
    for i, (key, s) in enumerate(zip('ABC', shots)):
        y = margin + i * (label + s.height + gap)
        d.text((margin, y), f'{key}  {palette(key)["name"]}  -  844 x 390 pt phone, button 256 x 96 pt',
               font=font(22), fill=(27, 31, 42, 255))
        sheet.alpha_composite(s, (margin, y + label))
    sheet.convert('RGB').save(path, optimize=True)


def step1():
    out = os.path.join(HERE, 'preview')
    os.makedirs(out, exist_ok=True)
    side_by_side(os.path.join(out, 'step1_side_by_side.png'))
    overview(os.path.join(out, 'step1_phones_overview.png'))
    for key in 'ABC':
        p = palette(key)
        # bare 2532 x 1170 screen: full-screen in landscape on an iPhone 13/14 = true size
        screen(p, 3).convert('RGB').save(os.path.join(out, f'step1_phone_{key}_{p["name"]}_3x.png'), optimize=True)
        save(button(p), os.path.join(out, f'step1_{key}_{p["name"]}_512x192.png'))


def states_sheet(p, path):
    """Normal / hover / pressed side by side: with text and without at export
    size, then at phone size (4 pt per pixel) over a dark and a light backdrop."""
    margin, gap, row_label = 56, 40, 36
    bw, bh = W * SCALE, H * SCALE
    small = PT_PER_PX * 2          # 2x device pixels per pt, so 8 px per art pixel too
    cw = margin * 2 + bw * 3 + gap * 2
    rows = [('with text', bh), ('no text (for Roblox 9-slice)', bh), ('phone size, dark backdrop', 0), ('phone size, light backdrop', 0)]
    strip_h = H * small + 32
    ch = margin + 80 + 2 * (row_label + bh + gap) + 2 * (row_label + strip_h + gap) + margin - gap
    sheet = Image.new('RGBA', (cw, ch), (246, 247, 250, 255))
    d = ImageDraw.Draw(sheet)
    d.text((margin, margin), f'A  {p["name"]}  -  states', font=font(34), fill=(27, 31, 42, 255))
    y = margin + 80
    for j, (label, _) in enumerate(rows):
        d.text((margin, y), label, font=font(20), fill=(90, 96, 112, 255))
        for i, st in enumerate(STATES):
            x = margin + i * (bw + gap)
            if j == 0:
                q = state_palette(p, st)
                d.text((x + bw - 300, y), f'{st}: {to_hex(q["fill"])} / {to_hex(q["hi"])} / {to_hex(q["shine"])}',
                       font=font(15), fill=(90, 96, 112, 255))
            if j < 2:
                bg = Image.fromarray(checker(bw, bh), 'RGBA')
                art = Image.fromarray(upscale(button(p, text=(j == 0), state=st)), 'RGBA')
                bg.alpha_composite(art)
                sheet.paste(bg, (x, y + row_label))
            else:
                back = (16, 23, 43, 255) if j == 2 else (140, 196, 236, 255)
                bg = Image.new('RGBA', (bw, strip_h), back)
                art = Image.fromarray(upscale(button(p, state=st), small // 2), 'RGBA')
                bg.alpha_composite(art, ((bw - art.width) // 2, (strip_h - art.height) // 2))
                sheet.paste(bg, (x, y + row_label))
        y += row_label + (bh if j < 2 else strip_h) + gap
    sheet.convert('RGB').save(path, optimize=True)


def step2(key='A'):
    p = palette(key)
    prev = os.path.join(HERE, 'preview')
    out = os.path.join(HERE, 'export')
    os.makedirs(prev, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    states_sheet(p, os.path.join(prev, 'step2_states.png'))
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    for st in STATES:   # the three images the game uses: PLAY + icon baked in
        save(button(p, text=True, state=st), os.path.join(out, f'play_{st}.png'))


if __name__ == '__main__':
    if 'step1' in sys.argv[1:]:
        step1()
    else:
        step2()
