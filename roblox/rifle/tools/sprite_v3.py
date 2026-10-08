"""Rifle sprite v3: v1 design with black outlines 'everywhere' (every component boundary, panel, slot, groove),
detachable parts carry their own outline. build(slim) -> (P, C, CS): part grid, colours with the charging-handle
knob drawn (left side), colours without it (right side). slim=True gives the thinner muzzle device option."""
import numpy as np
from PIL import Image
W, H = 80, 30
PAL = {
 'O': '#1c1c1c',
 'Mh': '#d4ecfc', 'Ml': '#bcd4dc', 'Mm': '#a0b4c0', 'Md': '#7c8c94', 'Mp': '#5c6870',
 'Wl': '#9c5434', 'Wm': '#84341c', 'Wd': '#742c24', 'Wp': '#54241c',
 'Dl': '#4a5258', 'Dm': '#3a4046', 'Dd': '#2c3236',
 'Yh': '#f6e486', 'Yl': '#ecd062', 'Ym': '#dcbc46', 'Yd': '#bf9c36', 'Yp': '#8e7228',
}
FAMILY = {'guard': 'lower', 'sight': 'rail', 'butt': 'butt'}     # components that join without a black seam
def fam(p): return FAMILY.get(p, p)

def build(slim=False, knob=True):
    P = np.full((H, W), '', dtype=object); C = np.full((H, W), '', dtype=object)
    def box(part, x0, x1, y0, y1): P[y0:y1 + 1, x0:x1 + 1] = part
    def clear(x, y): P[y, x] = ''
    # ---------------- silhouette (v1) ----------------
    for x in range(1, 24):
        box('stock', x, x, 6, 13 + min(5, (23 - x) // 4))
    box('butt', 1, 2, 6, 18)
    box('upper', 24, 62, 5, 8); box('upper', 24, 52, 9, 11)
    box('forend', 53, 62, 9, 12); clear(61, 12); clear(62, 12)
    box('rail', 28, 58, 3, 4)
    box('sight', 29, 32, 1, 2); box('sight', 55, 57, 1, 2)
    box('barrel', 63, 70, 7, 9)
    if slim:
        box('muzzle', 71, 78, 6, 10)                               # option B: 5 tall instead of 7
    else:
        box('muzzle', 71, 78, 5, 11); clear(78, 5); clear(78, 11)
    box('lower', 25, 51, 12, 15); clear(50, 15); clear(51, 15)
    box('guard', 31, 41, 22, 22); box('guard', 41, 41, 16, 21)
    box('mag', 42, 49, 16, 26); box('mag', 41, 50, 27, 27)
    for r, y in enumerate(range(16, 28)):
        o = r // 2; box('grip', 28 - o, 33 - o, y, y)
    clear(23, 27); clear(28, 27)
    box('trigger', 36, 37, 16, 17); box('trigger', 37, 37, 18, 19)
    if knob: box('charge', 47, 51, 6, 9)                          # 5x4 knob incl. its own outline ring
    def isp(y, x, part): return 0 <= y < H and 0 <= x < W and P[y, x] == part
    def solid(y, x): return 0 <= y < H and 0 <= x < W and P[y, x] != ''
    # ---------------- base shading (v1 ramp; seams with other components are now black) -----
    def ramp(part, R):
        hi, lt, md, dk, dp = R
        for y in range(H):
            for x in range(W):
                if P[y, x] != part: continue
                up = solid(y - 1, x) and not isp(y - 1, x, part)
                if not isp(y - 1, x, part): c = md if up else hi
                elif not isp(y - 2, x, part) and not (solid(y - 2, x) and not isp(y - 2, x, part)): c = lt
                elif not isp(y + 1, x, part):
                    c = ('O' if fam(P[y + 1, x]) != fam(part) else dk) if solid(y + 1, x) else dk
                else: c = md
                if not isp(y, x - 1, part) and c == md: c = lt
                C[y, x] = c
    Y = ('Yh', 'Yl', 'Ym', 'Yd', 'Yp'); M = ('Mh', 'Ml', 'Mm', 'Md', 'Mp')
    for p in ('stock', 'upper', 'lower', 'guard'): ramp(p, Y)
    for p in ('rail', 'sight', 'barrel', 'muzzle', 'mag', 'trigger'): ramp(p, M)
    def put(c, pts):
        for x, y in pts: C[y, x] = c
    def hline(c, x0, x1, y): put(c, [(x, y) for x in range(x0, x1 + 1)])
    def vline(c, x, y0, y1): put(c, [(x, y) for y in range(y0, y1 + 1)])
    def panel(R, x0, x1, y0, y1, stripe=None):
        """inset panel: BLACK ring, lighter inside, bright stripe"""
        hi, lt, md, dk, dp = R
        hline('O', x0, x1, y0); hline('O', x0, x1, y1); vline('O', x0, y0, y1); vline('O', x1, y0, y1)
        for y in range(y0 + 1, y1):
            hline(lt, x0 + 1, x1 - 1, y); put(md, [(x0 + 1, y)])
        hline(hi, x0 + 2, x1 - 2, stripe if stripe is not None else y0 + 1)
    # ---------------- stock ----------------
    vline('O', 23, 6, 13); put('Yl', [(23, 8)]); put('Yd', [(23, 10)])     # hinge seam + knuckle
    panel(Y, 5, 19, 8, 11, stripe=9)                                        # cheek panel
    for x in range(1, 3):
        for y in range(6, 19):
            C[y, x] = 'Dl' if (y == 6 or (x == 1 and y % 3 == 0)) else ('Dd' if y == 18 or x == 2 and y % 3 == 2 else 'Dm')
    vline('O', 3, 6, 17)                                                    # butt pad seam
    # ---------------- upper / handguard ----------------
    panel(Y, 31, 42, 6, 8)                                                  # ejection port
    hline('O', 44, 52, 7)                                                   # charging-handle slot
    put('O', [(27, 7), (27, 9)])                                            # pins
    vline('O', 53, 5, 8)                                                    # receiver | handguard seam
    for y in range(9, 13):                                                  # wood forend
        for x in range(53, 63):
            if P[y, x] != 'forend': continue
            C[y, x] = {9: 'Wm', 10: 'Wm', 11: 'Wm', 12: 'Wd'}[y]
        C[y, 53] = 'O'                                                      # seam continues down
    put('Wl', [(54, 9), (56, 9), (59, 9), (61, 9), (62, 9), (55, 10), (61, 10), (62, 10), (57, 11)])
    for x in (55, 58):
        put('O', [(x, 11), (x, 12)]); put('Wd', [(x, 10)])                  # grooves
    # ---------------- lower ----------------
    put('Ml', [(29, 13)]); put('Md', [(30, 13)]); put('O', [(28, 13), (31, 13)])   # selector lever
    put('Ml', [(40, 13)]); put('O', [(39, 13)])                                     # mag release
    # ---------------- rail + sights ----------------
    for x in range(28, 59):
        C[3, x] = 'Mh' if (x - 28) % 3 != 2 else 'O'                        # teeth
        C[4, x] = 'O'                                                       # rail | receiver seam
    put('O', [(30, 1), (31, 1)])                                            # rear aperture notch
    # ---------------- barrel / muzzle ----------------
    if slim:
        vline('O', 71, 6, 10)                                               # collar seam
        for x in (73, 76): vline('O', x, 7, 9)                              # vent slots
        put('Ml', [(74, 6), (77, 6)])
    else:
        vline('O', 71, 6, 10)
        for x in (73, 76): vline('O', x, 6, 10)
        put('Ml', [(74, 6), (77, 6)])
    # ---------------- magazine (carries its own outline: top row + seam to the guard) ------
    hline('O', 42, 49, 16)                                                  # top edge
    vline('O', 42, 16, 26)                                                  # front of guard | mag
    panel(M, 44, 48, 18, 24, stripe=19)
    hline('O', 42, 49, 26)                                                  # body | base plate
    hline('Mm', 41, 50, 27); put('Mh', [(41, 27), (50, 27)])
    # ---------------- grip ----------------
    for y in range(H):
        xs = [x for x in range(W) if P[y, x] == 'grip']
        if not xs: continue
        a, b = min(xs), max(xs)
        for x in xs: C[y, x] = 'Wl' if x == b else 'Wd' if x == a else 'Wm'
    put('Wl', [(31, 17), (29, 19), (31, 20), (28, 22), (29, 24), (26, 25), (27, 27)])
    put('Wd', [(32, 18), (30, 21), (28, 24), (27, 26)])
    # ---------------- charging-handle knob (left side only) ----------------
    if knob:
        hline('O', 47, 51, 6); hline('O', 47, 51, 9); vline('O', 47, 6, 9); vline('O', 51, 6, 9)
        put('Mh', [(48, 7), (49, 7)]); put('Ml', [(50, 7), (48, 8)]); put('Mm', [(49, 8)]); put('Md', [(50, 8)])
    # ---------------- silhouette outline ----------------
    for y in range(H):
        for x in range(W):
            if P[y, x] == '' and any(solid(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                C[y, x] = 'O'
    return P, C

def render(C, scale=8, bg=None):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0) if bg is None else bg); px = im.load()
    for y in range(H):
        for x in range(W):
            if C[y, x]:
                h = PAL[C[y, x]]; px[x, y] = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    return im.resize((W * scale, H * scale), Image.NEAREST)

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    import sprite as v1
    rows = [('v1 (current)', v1.render(8, (128, 128, 128, 255)))]
    for slim in (False, True):
        P, C = build(slim)
        rows.append((f'v3 outlined{" + slim muzzle" if slim else ""}', render(C, 8, (128, 128, 128, 255))))
        render(C, 1).save(f'v3_sprite{"_slim" if slim else ""}_1x.png')
    out = Image.new('RGB', (640 + 40, sum(r[1].height + 40 for r in rows) + 10), (60, 60, 60))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(out); f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    y = 10
    for name, im in rows:
        d.text((20, y), name, fill='white', font=f); out.paste(im, (20, y + 24)); y += im.height + 40
    out.save('v3_sprites.png'); print(out.size)
