"""Item icons (16x16 pixel art).

Two techniques:
  * blades are generated along the 45-degree diagonal (p = x - y runs along the blade, q = x + y across it),
    so every sword, dagger and greatsword shares consistent lighting and outlines;
  * everything else is a hand-authored mask: digits 1-5 are shades of the item's primary ramp (5 lightest),
    letters a-e shades of its secondary ramp, other letters named colours, '.' empty, 'K' outline.
Outlines are coloured from the darkest shade of the neighbouring material, as vanilla items are.
"""
import numpy as np

from .paint import Img, Ramp, hexrgb, mix

N = 16

# ------------------------------------------------------------------ material ramps (dark -> light)
M = {
    'oathsteel': Ramp('#1e2530', '#34404f', '#4f5e70', '#71839a', '#9fb2c6', '#dbe7f2'),
    'gold': Ramp('#4a3108', '#7a5512', '#b0801f', '#dcae3c', '#f6d670', '#fff4c0'),
    'lumen': Ramp('#6a4a14', '#a8761f', '#e0a83a', '#ffd46a', '#fff0b0', '#ffffff'),
    'leather': Ramp('#2a160a', '#472611', '#673a1b', '#8a5228', '#ad6d3a', '#c98c55'),
    'wood': Ramp('#2b1a0e', '#452a16', '#62401f', '#80582b', '#9c7038', '#b68a4c'),
    'gloamwood': Ramp('#0e0a14', '#1b1426', '#2a1f3a', '#3a2c4f', '#4c3b66', '#62507e'),
    'iron': Ramp('#1f2126', '#3a3d45', '#5a5e68', '#80858f', '#a9aeb7', '#d8dce2'),
    'rust': Ramp('#2a170e', '#4a2616', '#6e3a20', '#8f522c', '#b06e3e', '#c98c58'),
    'verdigris': Ramp('#0f2a24', '#1c4a3e', '#2c6b58', '#3f9077', '#62b89a', '#9ee0c4'),
    'tide': Ramp('#0b2a33', '#12475a', '#1a6d85', '#2c9ab0', '#58c8d4', '#b0f2f0'),
    'arcane': Ramp('#10133a', '#1d2766', '#2f3f99', '#4a61c8', '#7a92ec', '#c0d0ff'),
    'silk': Ramp('#1a1f4a', '#28357a', '#3a52aa', '#5577d0', '#83a3ec', '#c4d6ff'),
    'silver': Ramp('#3c4152', '#5e6478', '#858ca0', '#aeb4c6', '#d4d9e6', '#f4f6fb'),
    'bone': Ramp('#4a4234', '#6e6450', '#948870', '#b8ad92', '#d8cfb4', '#f2ecdc'),
    'gloam': Ramp('#140a22', '#2a1446', '#44226e', '#653598', '#8e54c4', '#c49cf0'),
    'violet': Ramp('#3a1470', '#5a24a8', '#7f3fe0', '#a468ff', '#caa4ff', '#f0e2ff'),
    'dawn': Ramp('#7a3a08', '#b8661a', '#e8962e', '#ffc24a', '#ffe68a', '#fffbe0'),
    'hollow': Ramp('#08060c', '#14101c', '#221b2e', '#332942', '#473a5a', '#5f4f76'),
    'blood': Ramp('#2a0608', '#4e0e12', '#7a1a1e', '#a82a2c', '#d2493e', '#f0806a'),
    'bread': Ramp('#4a2a0e', '#7a4a18', '#a86e2a', '#cf9444', '#e8b868', '#f8dca0'),
    'glass': Ramp('#3a4a52', '#5a7280', '#86a2ae', '#b4ccd4', '#dcecf0', '#ffffff'),
    'honey': Ramp('#6a3a06', '#9c5c0e', '#cc8a1c', '#eeb236', '#ffd866', '#fff0b4'),
    'stew': Ramp('#3a1e0e', '#5c3218', '#7e4a24', '#a06636', '#c0864c', '#dca66a'),
    'teal': Ramp('#0e3a34', '#16605a', '#20887e', '#3cb4a6', '#76dccc', '#c0fff4'),
    'ember': Ramp('#4a1004', '#8a2408', '#c84a10', '#f07a1c', '#ffb040', '#fff0a0'),
    'moss': Ramp('#1c2a12', '#2e4a1c', '#446a28', '#5c8a36', '#7aa84a', '#a2cc6c'),
    'paper': Ramp('#6e5a3a', '#948058', '#b8a47a', '#d8c69c', '#efe2c0', '#fcf6e4'),
    'white': Ramp('#8a8a90', '#a8a8b0', '#c4c4cc', '#dcdce2', '#f0f0f4', '#ffffff'),
}


def shade(ramp, k):
    """Shade k in 1..5 (ramps have six stops; 0 is reserved for outlines)."""
    return ramp.cols[max(0, min(len(ramp.cols) - 1, k))].copy()


def outline_of(ramp):
    c = ramp.cols[0].copy()
    c[:3] *= 0.55
    return c


# ------------------------------------------------------------------ mask renderer
def sprite(rows, primary, secondary=None, named=None, auto_outline=False):
    """Paints a mask. Digits use `primary`, letters a-e `secondary`, anything in `named` its colour."""
    assert len(rows) == N and all(len(r) == N for r in rows), [len(r) for r in rows]
    im = Img(N, N)
    owner = [[None] * N for _ in range(N)]
    named = named or {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            if ch in named:
                c = named[ch]
                col = c if not isinstance(c, tuple) else shade(c[0], c[1])
                im.px[y, x] = col
                owner[y][x] = c[0] if isinstance(c, tuple) else None
            elif ch.isdigit():
                im.px[y, x] = shade(primary, int(ch))
                owner[y][x] = primary
            elif ch in 'abcde' and secondary is not None:
                im.px[y, x] = shade(secondary, 'abcde'.index(ch) + 1)
                owner[y][x] = secondary
            elif ch == 'K':
                owner[y][x] = 'K'
    # explicit outlines take the colour of whichever material they border
    for y in range(N):
        for x in range(N):
            if owner[y][x] != 'K':
                continue
            ramp = None
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and isinstance(owner[ny][nx], Ramp):
                    ramp = owner[ny][nx]
                    break
            im.px[y, x] = outline_of(ramp or primary)
    if auto_outline:
        add_outline(im, owner, primary)
    return im


def add_outline(im, owner=None, fallback=None):
    a = im.px[:, :, 3] > 0.01
    src = im.px.copy()
    for y in range(N):
        for x in range(N):
            if a[y, x]:
                continue
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and a[ny, nx]:
                    c = src[ny, nx].copy()
                    c[:3] *= 0.35
                    c[3] = 1.0
                    im.px[y, x] = c
                    break
    return im


# ------------------------------------------------------------------ blades along the diagonal
def blade(tip=13, guard=-3, grip=-11, width=(14, 16), blade_ramp=None, guard_ramp=None, grip_ramp=None,
          pommel_ramp=None, guard_span=3, taper=3, curve=0.0, gem=None, fuller=True, serrate=False):
    """A sword on the anti-diagonal. p = x - y runs from the grip (negative) to the tip (positive);
    q = x + y runs across (15 is the centre line)."""
    blade_ramp = blade_ramp or M['oathsteel']
    guard_ramp = guard_ramp or M['gold']
    grip_ramp = grip_ramp or M['leather']
    pommel_ramp = pommel_ramp or guard_ramp
    im = Img(N, N)
    owner = np.full((N, N), None, dtype=object)
    q0, q1 = width
    for y in range(N):
        for x in range(N):
            p, q = x - y, x + y
            bend = curve * ((p - guard) / max(1, tip - guard)) ** 2 if p > guard else 0
            qq = q - bend
            # blade
            if guard < p <= tip:
                rem = tip - p
                lo, hi = q0, q1
                if rem < taper:
                    shrink = taper - rem
                    lo = q0 + shrink * 0.5
                    hi = q1 - shrink * 0.5
                if lo - 0.01 <= qq <= hi + 0.01:
                    if qq <= lo + 0.6:
                        k = 5
                    elif fuller and abs(qq - (lo + hi) / 2) < 0.6 and hi - lo >= 2:
                        k = 3
                    elif qq >= hi - 0.6:
                        k = 2
                    else:
                        k = 4
                    if serrate and qq >= hi - 0.6 and p % 3 == 0:
                        continue
                    im.px[y, x] = shade(blade_ramp, k)
                    owner[y, x] = blade_ramp
                    continue
            # guard
            if guard - 1 <= p <= guard and abs(q - 15.5) <= guard_span + 0.6:
                k = 4 if q < 15.5 else 2
                im.px[y, x] = shade(guard_ramp, k)
                owner[y, x] = guard_ramp
                continue
            # grip
            if grip < p < guard - 1 and 15 <= q <= 16:
                k = 3 if (p % 2 == 0) else 2
                if q == 15:
                    k += 1
                im.px[y, x] = shade(grip_ramp, k)
                owner[y, x] = grip_ramp
                continue
            # pommel
            if grip - 2 <= p <= grip and 14 <= q <= 17:
                k = 4 if q <= 15 else 2
                im.px[y, x] = shade(pommel_ramp, k)
                owner[y, x] = pommel_ramp
    if gem is not None:
        for y in range(N):
            for x in range(N):
                p, q = x - y, x + y
                if guard - 1 <= p <= guard and 15 <= q <= 16:
                    im.px[y, x] = gem
    return outline(im, owner)


def outline(im, owner=None):
    a = im.px[:, :, 3] > 0.01
    src = im.px.copy()
    for y in range(N):
        for x in range(N):
            if a[y, x]:
                continue
            best = None
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and a[ny, nx]:
                    r = owner[ny, nx] if owner is not None else None
                    best = outline_of(r) if isinstance(r, Ramp) else src[ny, nx] * np.array([0.35, 0.35, 0.35, 1])
                    break
            if best is not None:
                im.px[y, x] = best
    return im


# ------------------------------------------------------------------ tool masks (h = handle shades via secondary)
PICKAXE = [
    "................",
    "....KKKKK.......",
    "...K55554KK.....",
    "....KKKK443K....",
    "........KK43K...",
    ".......KcKK32K..",
    "......KcbK.K32K.",
    ".....KcbK..K32K.",
    "....KcbK....K2K.",
    "...KcbK.....K2K.",
    "..KcbK......KK..",
    ".KcbK...........",
    ".KbK............",
    ".KK.............",
    "................",
    "................",
]

AXE = [
    "................",
    "........KKK.....",
    ".......K543K....",
    "......K55432K...",
    ".....K5544432K..",
    "......K54KKc32K.",
    ".......KKKcbK2K.",
    "........KcbK.KK.",
    ".......KcbK.....",
    "......KcbK......",
    ".....KcbK.......",
    "....KcbK........",
    "...KcbK.........",
    "..KcbK..........",
    "..KbK...........",
    "..KK............",
]

SHOVEL = [
    "................",
    "...........KKK..",
    "..........K553K.",
    ".........K55432K",
    ".........K54432K",
    "..........K432K.",
    ".........KcKKK..",
    "........KcbK....",
    ".......KcbK.....",
    "......KcbK......",
    ".....KcbK.......",
    "....KcbK........",
    "...KcbK.........",
    "..KcbK..........",
    "..KbK...........",
    "..KK............",
]

HOE = [
    "................",
    "......KKKKK.....",
    ".....K55543K....",
    "......KKKc32K...",
    ".........KcK2K..",
    "........KcbK.K..",
    ".......KcbK.....",
    "......KcbK......",
    ".....KcbK.......",
    "....KcbK........",
    "...KcbK.........",
    "..KcbK..........",
    "..KbK...........",
    "..KK............",
    "................",
    "................",
]

# ------------------------------------------------------------------ armour masks (t = trim via secondary)
HELMET = [
    "................",
    "................",
    "................",
    "....KKKKKKKK....",
    "...K54444433K...",
    "..K5433333322K..",
    "..K4dcccccc22K..",
    "..K43KKKKKK22K..",
    "..K42K....K21K..",
    "..K32K....K21K..",
    "..KKK......KKK..",
    "................",
    "................",
    "................",
    "................",
    "................",
]

CHESTPLATE = [
    "................",
    "..KKKK....KKKK..",
    ".K5444K..K4332K.",
    ".K44433KK33322K.",
    ".K4433ccdc3322K.",
    ".KKK433cdc332KK.",
    "...K4433c3322K..",
    "...K4433c3322K..",
    "...K443ccc322K..",
    "...K4433c3322K..",
    "...K4433c3222K..",
    "...K3333c2221K..",
    "...KddddddddcK..",
    "...KKKKKKKKKKK..",
    "................",
    "................",
]

LEGGINGS = [
    "................",
    "................",
    "...KKKKKKKKKK...",
    "...KddddddddK...",
    "...K44433322K...",
    "...K443KK322K...",
    "...K443KK322K...",
    "...K443KK322K...",
    "...K433KK322K...",
    "...K433KK222K...",
    "...K433KK221K...",
    "...Kdd3KKcddK...",
    "...K333KK221K...",
    "...KKKKKKKKKK...",
    "................",
    "................",
]

BOOTS = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "..KKKK....KKKK..",
    "..K44K....K33K..",
    "..K43K....K32K..",
    "..Kd3K....Kc2K..",
    "..K43K....K32K..",
    ".K443K...K332K..",
    "K5443K..K4322K..",
    "K4433K..K3322K..",
    "KddddK..KccccK..",
    "KKKKKK..KKKKKK..",
    "................",
]

INGOT = [
    "................",
    "................",
    "................",
    "................",
    "................",
    ".....KKKKKKKK...",
    "....K55555544K..",
    "...K5544444433K.",
    "..K544444443322K",
    "..K4433333332221",
    "..K33222222221K.",
    "...KKKKKKKKKKK..",
    "................",
    "................",
    "................",
    "................",
]

NUGGET = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "......KKK.......",
    ".....K554K......",
    "....K54432K.....",
    "....K4332K......",
    ".....KKKK.......",
    "................",
    "................",
    "................",
    "................",
    "................",
]

SHARD = [
    "................",
    "..........KK....",
    ".........K5K....",
    "........K554K...",
    ".......K5543K...",
    "......K55432K...",
    ".....K554332K...",
    "....K5543322K...",
    "...K55433221K...",
    "...K5443321K....",
    "...K443321K.....",
    "...K43321K......",
    "...K3321K.......",
    "....K21K........",
    ".....KK.........",
    "................",
]

DUST = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "......5....4....",
    "..4.......5.....",
    "......KKKK...5..",
    "....KK5544KK....",
    "...K55544433K...",
    "..K5544433332K..",
    ".K444433332221K.",
    ".KKKKKKKKKKKKKK.",
    "................",
    "................",
    "................",
]

EGG = [
    "................",
    "................",
    "......KKKK......",
    ".....K5544K.....",
    "....K555444K....",
    "....K5544433K...",
    "...K55444433K...",
    "...K54444333K...",
    "...K44443333K...",
    "...K44433332K...",
    "...K44333322K...",
    "....K333322K....",
    "....K3332221K...",
    ".....KK2211K....",
    ".......KKKK.....",
    "................",
]


def tool(mask, head, handle):
    return sprite(mask, head, handle)


def armor(mask, body, trim):
    return sprite(mask, body, trim)


def spawn_egg(base, spots, seed):
    im = sprite(EGG, base)
    r = np.random.default_rng(seed)
    a = im.px[:, :, 3] > 0.01
    for _ in range(8):
        x, y = int(r.integers(4, 12)), int(r.integers(3, 13))
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            if a[y + dy, x + dx] and not is_outline(im, x + dx, y + dy):
                im.px[y + dy, x + dx] = shade(spots, 4 - dy)
    return im


def is_outline(im, x, y):
    return im.px[y, x, :3].sum() < 0.35


# ------------------------------------------------------------------ unique items (hand-authored masks)
CHRONICLE = [
    "................",
    "..KKKKKKKKKKK...",
    ".K5444444443aK..",
    ".K4gggggggg3aK..",
    ".K4g33333g33aK..",
    ".K43333w3333aK..",
    ".K4333wyw333aK..",
    ".K433wyyyw33aK..",
    ".K4333wyw333aK..",
    ".K43333w3333aK..",
    ".K4g33333g33aK..",
    ".K4gggggggg3aK..",
    ".K3222222221aK..",
    "..KKKKKKKKKKbb..",
    "...Kbbbbbbbbb...",
    "................",
]

LANTERN = [
    "......KKKK......",
    ".....K5445K.....",
    "......KKKK......",
    ".....K5443K.....",
    "....KKKKKKKK....",
    "....K4yyyy2K....",
    "....K4ywwy2K....",
    "....K4ywwy2K....",
    "....K4yyyy2K....",
    "....K4yyyy2K....",
    "....KKKKKKKK....",
    "....K544332K....",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
]

KEY = [
    "................",
    ".KKKK...........",
    "K5y4K...........",
    "K4K3K...........",
    "K3y2K...........",
    ".KK4KK..........",
    "...K43K.........",
    "....K43K........",
    ".....K43K.......",
    "......K43KKK....",
    ".......K4332K...",
    "........K4KK3K..",
    ".........KK.K2K.",
    ".............KK.",
    "................",
    "................",
]

MEDALLION = [
    "................",
    "................",
    ".....KKKKKK.....",
    "....K554443K....",
    "...K54cccc32K...",
    "..K54c5dd5c32K..",
    "..K4cdeeeedc2K..",
    "..K4cdeeeedc2K..",
    "..K4cdeeeedc2K..",
    "..K4cc5dd5cc2K..",
    "...K43cccc21K...",
    "....K332221K....",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
]

FLASK = [
    "................",
    "......KKKK......",
    "......KaaK......",
    "......KbbK......",
    ".....KKbbKK.....",
    "....K444433K....",
    "...K4wyyyy32K...",
    "...K4yyyyyy2K...",
    "...K4yyyyyy2K...",
    "...K3yyyyyy2K...",
    "....K3yyyy2K....",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
    "................",
]

BREAD = [
    "................",
    "................",
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "...KK555444KK...",
    "..K5545454433K..",
    ".K554433443322K.",
    ".K444444333322K.",
    ".K333333322221K.",
    "..KK22222111KK..",
    "....KKKKKKKK....",
    "................",
    "................",
    "................",
]

BOWL = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "...KKKKKKKKKK...",
    "..K5445y45443K..",
    "..Kc4454y4432K..",
    "..KdccccccccdK..",
    "...KdccccccdK...",
    "....KddccddK....",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
]

BOTTLE = [
    "................",
    "......KKKK......",
    "......KbbK......",
    "......KKKK......",
    "......K54K......",
    ".....K5443K.....",
    "....K544432K....",
    "....K4yyyy2K....",
    "....K4ywyy2K....",
    "....K4yyyy2K....",
    "....K4yyyy2K....",
    "....K3yyyy1K....",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
]

HORN = [
    "................",
    "................",
    "..KK............",
    ".K54K...........",
    ".K543K..........",
    "..K543KK........",
    "..K4432aKK......",
    "...K4332aaKKK...",
    "....K43322bb5K..",
    ".....KK3221b43K.",
    ".......KKK2b32K.",
    "..........Kb32K.",
    "...........K2K..",
    "............K...",
    "................",
    "................",
]

EMBER = [
    "................",
    "................",
    "........K.......",
    ".......K5K......",
    "......K545K.....",
    ".....K54w45K....",
    "....K54www45K...",
    "....K4wwyww4K...",
    "....K45yyy54K...",
    "....K34yyy43K...",
    ".....K34443K....",
    "......KKKKK.....",
    "................",
    "................",
    "................",
    "................",
]

ESSENCE = [
    "................",
    "........KK......",
    ".......K55K.....",
    "......K5445K....",
    "......K4w43K....",
    ".....K54w432K...",
    "....K5443w32K...",
    "....K4432w21K...",
    ".....K43w21K....",
    "......K3w2K.....",
    "......K32K......",
    ".......KK.......",
    "................",
    "................",
    "................",
    "................",
]

SILK = [
    "................",
    "................",
    "................",
    "...KKKKKKKKKK...",
    "..K5544554433K..",
    "..K4ww4444w32K..",
    "..K4443333322K..",
    "..K3w333333w2K..",
    "..K4443333322K..",
    "..K3322222211K..",
    "...KKKKKKKKKK...",
    ".........K2K....",
    "..........K1K...",
    "...........KK...",
    "................",
    "................",
]

INSIGNIA = [
    "................",
    "....KKKKKKKK....",
    "...K55444433K...",
    "...K5aaaaaa3K...",
    "...K4a.yy.a3K...",
    "...K4a.yy.a3K...",
    "...K4ayyyya3K...",
    "...K4ayyyya2K...",
    "...K4aaaaaa2K...",
    "....K443322K....",
    ".....K4322K.....",
    "......K32K......",
    ".......KK.......",
    "................",
    "................",
    "................",
]


def colour(h):
    return hexrgb(h)


def gen_items():
    """Returns {name: Img} for every item icon (block items with flat icons included)."""
    out = {}
    G = M
    # ---------------------------------------------------------- the Chronicle
    out['lantern_chronicle'] = sprite(CHRONICLE, G['leather'], G['paper'],
                                      {'g': (G['gold'], 3), 'w': (G['lumen'], 4), 'y': (G['lumen'], 5)})
    # ---------------------------------------------------------- materials
    out['lumenite_shard'] = sprite(SHARD, G['lumen'])
    out['lumenite_dust'] = sprite(DUST, G['lumen'])
    out['oathsteel_blend'] = sprite(DUST, Ramp('#2c3440', '#4a5566', '#6c7a8e', '#9aa6b6', '#d8b45a', '#ffe08a'))
    out['oathsteel_ingot'] = sprite(INGOT, G['oathsteel'])
    out['oathsteel_nugget'] = sprite(NUGGET, G['oathsteel'])
    out['spellsilk'] = sprite(SILK, G['silk'], named={'w': (G['silver'], 5)})
    out['luminous_dust'] = sprite(DUST, Ramp('#6a6040', '#a89a64', '#e0d49a', '#fff4c8', '#ffffff', '#ffffff'))
    out['gloam_essence'] = sprite(ESSENCE, G['gloam'], named={'w': (G['violet'], 5)})
    out['lanternguard_insignia'] = sprite(INSIGNIA, G['gold'], G['blood'], {'y': (G['lumen'], 5)})
    out['seal_of_valor'] = sprite(MEDALLION, G['verdigris'], G['tide'])
    out['seal_of_wisdom'] = sprite(MEDALLION, G['silver'], G['arcane'])
    out['seal_of_sacrifice'] = sprite(MEDALLION, G['bone'], G['gold'])
    out['oathkey'] = sprite(KEY, G['gold'], named={'y': (G['violet'], 5)})
    out['everflame_ember'] = sprite(EMBER, G['dawn'], named={'w': (G['white'], 5), 'y': (G['lumen'], 5)})
    # ---------------------------------------------------------- lanterns
    out['wardens_lantern'] = sprite(LANTERN, G['iron'], named={'y': (G['lumen'], 3), 'w': (G['lumen'], 5)})
    out['everflame_lantern'] = sprite(LANTERN, G['gold'], named={'y': (G['dawn'], 4), 'w': (G['white'], 5)})
    # ---------------------------------------------------------- weapons
    out['oathsteel_longsword'] = blade(tip=13, guard=-4, grip=-10, width=(14, 16), blade_ramp=G['oathsteel'],
                                       guard_ramp=G['gold'], grip_ramp=G['leather'], gem=shade(G['blood'], 4))
    out['shadowreap_sickle'] = blade(tip=11, guard=-5, grip=-11, width=(14, 16), blade_ramp=G['gloam'],
                                     guard_ramp=G['hollow'], grip_ramp=G['gloamwood'], curve=-4.0, fuller=False)
    out['dawnbreaker'] = blade(tip=14, guard=-5, grip=-11, width=(13, 17), blade_ramp=G['dawn'], guard_ramp=G['gold'],
                               grip_ramp=G['leather'], guard_span=4, gem=shade(G['white'], 5))
    out['oathsteel_pickaxe'] = tool(PICKAXE, G['oathsteel'], G['wood'])
    out['oathsteel_axe'] = tool(AXE, G['oathsteel'], G['wood'])
    out['oathsteel_shovel'] = tool(SHOVEL, G['oathsteel'], G['wood'])
    out['wardens_halberd'] = halberd(G['oathsteel'], G['wood'], G['gold'])
    out['drowned_anchor'] = anchor(G['verdigris'], G['rust'])
    out['staff_of_veyl'] = staff(G['gloamwood'], G['arcane'])
    for i, im in enumerate(bow_frames(G['wood'], G['dawn'])):
        out['dawnstring_longbow' + ('' if i == 0 else f'_pulling_{i - 1}')] = im
    out['housecarl_warhorn'] = sprite(HORN, G['bone'], G['teal'])
    out['lumen_flask'] = sprite(FLASK, G['glass'], G['leather'], {'y': (G['lumen'], 4), 'w': (G['white'], 5)})
    # ---------------------------------------------------------- armour
    for piece, mask in (('helmet', HELMET), ('chestplate', CHESTPLATE), ('leggings', LEGGINGS), ('boots', BOOTS)):
        out[f'oathsteel_{piece}'] = armor(mask, G['oathsteel'], G['gold'])
    out['arcanist_hood'] = armor(HELMET, G['silk'], G['silver'])
    out['arcanist_robe'] = armor(CHESTPLATE, G['silk'], G['silver'])
    out['arcanist_leggings'] = armor(LEGGINGS, G['silk'], G['silver'])
    out['arcanist_boots'] = armor(BOOTS, G['silk'], G['silver'])
    out['hollow_crown'] = crown(G['hollow'], G['gold'], G['violet'])
    # ---------------------------------------------------------- food & drink
    out['wayfarers_bread'] = sprite(BREAD, G['bread'])
    out['honeyed_mead'] = sprite(BOTTLE, G['glass'], G['leather'], {'y': (G['honey'], 4), 'w': (G['white'], 5)})
    out['knights_stew'] = sprite(BOWL, G['stew'], G['wood'], {'y': (G['moss'], 4)})
    out['elixir_of_dawn'] = sprite(BOTTLE, G['glass'], G['gold'], {'y': (G['dawn'], 4), 'w': (G['white'], 5)})
    return out


# ------------------------------------------------------------------ composite items
def shaft(im, owner, ramp, p0, p1, q=(15, 16)):
    for y in range(N):
        for x in range(N):
            p, qq = x - y, x + y
            if p0 <= p <= p1 and q[0] <= qq <= q[1]:
                im.px[y, x] = shade(ramp, 3 if qq == q[0] else 2)
                owner[y, x] = ramp


def paint_mask(im, owner, rows, ox, oy, ramp, named=None):
    named = named or {}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            x, y = ox + i, oy + j
            if not (0 <= x < N and 0 <= y < N) or ch == '.':
                continue
            if ch in named:
                im.px[y, x] = shade(*named[ch])
                owner[y, x] = named[ch][0]
            elif ch.isdigit():
                im.px[y, x] = shade(ramp, int(ch))
                owner[y, x] = ramp


def halberd(head, haft, trim):
    im = Img(N, N)
    owner = np.full((N, N), None, dtype=object)
    shaft(im, owner, haft, -14, 9)
    paint_mask(im, owner, [
        "..5....",
        ".554...",
        "55443..",
        ".54432.",
        "..4332.",
        "...33..",
        "..t2...",
    ], 8, 0, head, {'t': (trim, 4)})
    paint_mask(im, owner, ["5543", "4432", ".32."], 5, 4, head)
    return outline(im, owner)


def anchor(metal, chain):
    rows = [
        "......KKK.......",
        ".....K4.4K......",
        "......KKK.......",
        "...KKK.5K.KKK...",
        "...K5444433c2K..",
        "...KKK.4K.KKK...",
        "......K43K......",
        "......K43K......",
        "......K43K......",
        "......K43K......",
        ".KK...K43K...KK.",
        "K54K..K43K..K32K",
        "K543KK4432KK432K",
        ".K5444443333322K",
        "..KK44433333KK..",
        "....KKKKKKKK....",
    ]
    return sprite(rows, metal, chain)


def staff(wood, crystal):
    im = Img(N, N)
    owner = np.full((N, N), None, dtype=object)
    shaft(im, owner, wood, -14, 6)
    paint_mask(im, owner, [
        ".c...c.",
        "..c5c..",
        ".c545c.",
        "..c4c..",
        ".c...c.",
    ], 8, 1, crystal, {'c': (wood, 4)})
    return outline(im, owner)


def crown(metal, gold, gem):
    rows = [
        "................",
        "................",
        "................",
        "..K...K..K...K..",
        ".K5K.K5KK5K.K4K.",
        ".K54K545545K43K.",
        ".K5444y44y4433K.",
        ".K5444444443332K",
        ".KaaaaaaaaaaaaK.",
        ".KabbbbbbbbbbaK.",
        ".KKKKKKKKKKKKKK.",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]
    return sprite(rows, gold, metal, {'y': (gem, 5)})


def bow_frames(wood, string):
    """Rest pose and three draws. The limb is a curve; the string pulls back toward the lower left."""
    frames = []
    for draw in (0, 1, 2, 3):
        im = Img(N, N)
        owner = np.full((N, N), None, dtype=object)
        pull = draw * 1.2
        pts = []
        for i in range(29):
            t = i / 28
            # limb from top (upper right) to bottom (lower left), bowed outwards to the upper left
            x = 13 - t * 11
            y = 2 + t * 11
            bow = 3.2 * (1 - (2 * t - 1) ** 2) + pull * 0.4
            x -= bow * 0.7
            y -= bow * 0.7
            pts.append((x, y))
        for (x, y) in pts:
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < N and 0 <= yi < N:
                im.px[yi, xi] = shade(wood, 3)
                owner[yi, xi] = wood
        # grip wrap at the middle
        mx, my = pts[14]
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            x, y = int(round(mx)) + dx, int(round(my)) + dy
            im.px[y, x] = shade(M['gold'], 4)
            owner[y, x] = M['gold']
        # string from tip to tip, pulled toward the lower right
        a, b = pts[0], pts[-1]
        for i in range(21):
            t = i / 20
            x = a[0] + (b[0] - a[0]) * t + pull * 1.3 * (1 - (2 * t - 1) ** 2)
            y = a[1] + (b[1] - a[1]) * t + pull * 1.3 * (1 - (2 * t - 1) ** 2)
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < N and 0 <= yi < N and owner[yi, xi] is None:
                im.px[yi, xi] = shade(string, 4)
                owner[yi, xi] = string
        if draw:
            # the nocked sun-arrow
            sx = a[0] + (b[0] - a[0]) * 0.5 + pull * 1.3
            sy = a[1] + (b[1] - a[1]) * 0.5 + pull * 1.3
            for k in range(8):
                x, y = int(round(sx - k * 0.95)), int(round(sy - k * 0.95))
                if 0 <= x < N and 0 <= y < N:
                    im.px[y, x] = shade(M['dawn'], 5 if k > 5 else 3)
                    owner[y, x] = M['dawn']
        frames.append(outline(im, owner))
    return frames
