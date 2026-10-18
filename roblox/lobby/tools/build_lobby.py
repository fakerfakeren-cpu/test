"""Greybox lobby for the arena shooter: plaza, queue pads, practice range, spawn.

Usage: python3 build_lobby.py <out.rbxmx> [preview.png]
Style: flat matte colours (SmoothPlastic, no Neon), pixel font on the signs. Everything is anchored parts, no scripts.
Layout is in studs, floor top at Y0; the spawn faces the pads (-Z). Pads are grouped Pads/<mode>/<pad>, and
each pad's standing spots are named A1..An / B1..Bn so the queue code can read the team size from them.
"""
import math
import sys
import uuid
from xml.sax.saxutils import escape

import numpy as np

Y0 = 300.0                                   # floor top; high above the template's baseplate and test map
PIXEL_FONT = 'rbxasset://fonts/families/PressStart2P.json'

# ---- palette: flat, matte, no neon
FLOOR = [(205, 198, 182), (190, 183, 166)]
RANGE_FLOOR = [(150, 150, 155), (138, 138, 143)]
WALL, TRIM, POST = (125, 108, 94), (96, 82, 70), (60, 60, 66)
PAD_BASE, DIVIDER = (72, 76, 86), (235, 235, 235)
SIDE = {'A': (59, 130, 246), 'B': (239, 68, 68)}
MODE_COLOUR = {'1v1': (52, 120, 219), '2v2': (142, 68, 173), '3v3': (243, 156, 18), '4v4': (192, 57, 43),
               'Infection': (39, 174, 96)}
YELLOW, WHITE = (241, 196, 15), (230, 230, 230)


# ---------------------------------------------------------------- tiny rbxmx writer
def num(v):
    v = float(v)
    if abs(v) < 5e-13: v = 0.0
    r = repr(round(v, 6))
    return r[:-2] if r.endswith('.0') else r


def prop(name, kind, v):
    if kind == 'string': return f'<string name="{name}">{escape(v)}</string>'
    if kind == 'bool': return f'<bool name="{name}">{"true" if v else "false"}</bool>'
    if kind == 'float': return f'<float name="{name}">{num(v)}</float>'
    if kind == 'int': return f'<int name="{name}">{int(v)}</int>'
    if kind == 'token': return f'<token name="{name}">{int(v)}</token>'
    if kind == 'Vector3': return f'<Vector3 name="{name}"><X>{num(v[0])}</X><Y>{num(v[1])}</Y><Z>{num(v[2])}</Z></Vector3>'
    if kind == 'Color3uint8': return f'<Color3uint8 name="{name}">{0xFF000000 | (v[0] << 16) | (v[1] << 8) | v[2]}</Color3uint8>'
    if kind == 'Color3': return f'<Color3 name="{name}"><R>{num(v[0])}</R><G>{num(v[1])}</G><B>{num(v[2])}</B></Color3>'
    if kind == 'UDim2': return f'<UDim2 name="{name}"><XS>{num(v[0])}</XS><XO>{int(v[1])}</XO><YS>{num(v[2])}</YS><YO>{int(v[3])}</YO></UDim2>'
    if kind == 'Font':
        return (f'<Font name="{name}"><Family><url>{v}</url></Family><Weight>400</Weight><Style>Normal</Style></Font>')
    if kind == 'CFrame':
        p, R = v
        vals = [*p, *np.asarray(R).ravel()]
        tags = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
        return f'<CoordinateFrame name="{name}">' + ''.join(f'<{t}>{num(x)}</{t}>' for t, x in zip(tags, vals)) + '</CoordinateFrame>'
    raise ValueError(kind)


class Item:
    def __init__(self, cls, name, *props):
        self.cls, self.ref, self.name = cls, 'RBX' + uuid.uuid4().hex.upper(), name
        self.props, self.kids = [('Name', 'string', name), *props], []

    def add(self, item):
        self.kids.append(item); return item

    def xml(self, out, ind):
        t = '\t' * ind
        out.append(f'{t}<Item class="{self.cls}" referent="{self.ref}">')
        out.append(f'{t}\t<Properties>')
        out += [f'{t}\t\t' + prop(n, k, v) for n, k, v in self.props]
        out.append(f'{t}\t</Properties>')
        for c in self.kids: c.xml(out, ind + 1)
        out.append(f'{t}</Item>')


def ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


ROT_UP = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1.0]])   # Rz(90): a Cylinder's axis (X) points up -> flat disc

PREVIEW = []   # (kind, size, centre, R, colour) for the preview render
LABELS = []    # (text, world point) drawn on the preview


def part(name, size, pos, colour, R=np.eye(3), cls='Part', shape=1, collide=True, transparency=0.0, touch=False, query=True):
    it = Item(cls, name,
              ('Anchored', 'bool', True), ('CanCollide', 'bool', collide), ('CanTouch', 'bool', touch),
              ('CanQuery', 'bool', query), ('CastShadow', 'bool', transparency < 1), ('Locked', 'bool', False),
              ('CFrame', 'CFrame', (pos, R)), ('size', 'Vector3', size), ('Color3uint8', 'Color3uint8', colour),
              ('Material', 'token', 272), ('Transparency', 'float', transparency),
              ('TopSurface', 'token', 0), ('BottomSurface', 'token', 0), ('shape', 'token', shape))
    if transparency < 1:
        PREVIEW.append(('cyl' if shape == 2 else 'box', np.array(size, float), np.array(pos, float), R, colour))
    return it


def sign_text(board, face, title, sub=None, colour=(1, 1, 1)):
    """Pixel-font text on one face of a board part. face: NormalId (Back = 2 faces +Z, Top = 1)."""
    g = board.add(Item('SurfaceGui', 'Sign', ('Face', 'token', face), ('SizingMode', 'token', 1),
                       ('PixelsPerStud', 'float', 40), ('LightInfluence', 'float', 0), ('ClipsDescendants', 'bool', True),
                       ('ZIndexBehavior', 'token', 1)))
    common = [('BackgroundTransparency', 'float', 1), ('TextScaled', 'bool', True), ('FontFace', 'Font', PIXEL_FONT),
              ('TextStrokeTransparency', 'float', 0.3), ('TextStrokeColor3', 'Color3', (0, 0, 0))]
    if sub is None:
        g.add(Item('TextLabel', 'Title', ('Text', 'string', title), ('TextColor3', 'Color3', colour),
                   ('Size', 'UDim2', (0.9, 0, 0.7, 0)), ('Position', 'UDim2', (0.05, 0, 0.15, 0)), *common))
    else:
        g.add(Item('TextLabel', 'Title', ('Text', 'string', title), ('TextColor3', 'Color3', colour),
                   ('Size', 'UDim2', (0.9, 0, 0.5, 0)), ('Position', 'UDim2', (0.05, 0, 0.08, 0)), *common))
        g.add(Item('TextLabel', 'Count', ('Text', 'string', sub), ('TextColor3', 'Color3', (1, 0.86, 0.35)),
                   ('Size', 'UDim2', (0.9, 0, 0.3, 0)), ('Position', 'UDim2', (0.05, 0, 0.62, 0)), *common))


def wall(folder, name, x0, x1, z0, z1, h=10.0, trim=1.5):
    sx, sz = x1 - x0, z1 - z0
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    folder.add(part(name, (sx, h - trim, sz), (cx, Y0 + (h - trim) / 2, cz), WALL))
    folder.add(part(name + 'Trim', (sx + 0.4, trim, sz + 0.4), (cx, Y0 + h - trim / 2, cz), TRIM))


def tiles(folder, x0, x1, z0, z1, colours, step=10.0):
    for i, x in enumerate(np.arange(x0, x1, step)):
        for j, z in enumerate(np.arange(z0, z1, step)):
            folder.add(part('Tile', (step, 2, step), (x + step / 2, Y0 - 1, z + step / 2), colours[(i + j) % 2]))


def board_with_posts(parent, name, width, height, bottom, cx, z, colour, title, sub):
    parent.add(part(name, (width, height, 0.6), (cx, Y0 + bottom + height / 2, z), colour)).__class__
    b = parent.kids[-1]
    sign_text(b, 2, title, sub)
    for px in (cx - width / 2 + 0.8, cx + width / 2 - 0.8):
        parent.add(part('Post', (0.6, bottom, 0.6), (px, Y0 + bottom / 2, z), POST))
    LABELS.append((f'{title} {sub}', np.array([cx, Y0 + bottom + height / 2, z])))


def team_pad(mode_folder, mode, idx, n, cx, cz, high_sign):
    """A pad for n v n: side A spots on the left, side B on the right, a white line between them."""
    cols, rows = (1, n) if n <= 2 else (2, 2)
    W, D = 12 * cols + 4, 6 * rows + 2
    pad = mode_folder.add(Item('Model', f'Pad{idx}'))
    pad.add(part('Base', (W, 0.5, D), (cx, Y0 + 0.25, cz), PAD_BASE))
    pad.add(part('Divider', (0.6, 0.12, D - 1), (cx, Y0 + 0.56, cz), DIVIDER))
    cells = [(r, c) for r in range(rows) for c in range(cols)][:n]
    for k, (r, c) in enumerate(cells):
        z = cz - 3 * (rows - 1) + 6 * r
        xa = cx - 2 - 6 * cols + 3 + 6 * c
        xb = cx + 2 + 3 + 6 * (cols - 1 - c)
        pad.add(part(f'A{k + 1}', (0.3, 5, 5), (xa, Y0 + 0.65, z), SIDE['A'], ROT_UP, shape=2, touch=True))
        pad.add(part(f'B{k + 1}', (0.3, 5, 5), (xb, Y0 + 0.65, z), SIDE['B'], ROT_UP, shape=2, touch=True))
    z_sign = cz - D / 2 - 1.0
    if high_sign:
        board_with_posts(pad, 'SignBoard', W, 5, 13, cx, z_sign, MODE_COLOUR[mode], mode.upper(), f'0/{2 * n}')
    else:   # bottom at 6 studs: characters (about 5.2 tall) walk underneath
        board_with_posts(pad, 'SignBoard', W, 4, 6, cx, z_sign, MODE_COLOUR[mode], mode.upper(), f'0/{2 * n}')
    return pad


def build():
    lobby = Item('Model', 'Lobby')
    floor = lobby.add(Item('Folder', 'Floor'))
    walls = lobby.add(Item('Folder', 'Walls'))
    pads = lobby.add(Item('Folder', 'Pads'))
    rng = lobby.add(Item('Folder', 'Range'))

    # plaza 120 x 100, range 70 x 30 off the west side
    tiles(floor, -60, 60, -55, 45, FLOOR)
    tiles(floor, -130, -60, -15, 15, RANGE_FLOOR)
    wall(walls, 'North', -62, 62, -57, -55)
    wall(walls, 'South', -62, 62, 45, 47)
    wall(walls, 'East', 60, 62, -55, 45)
    wall(walls, 'WestN', -62, -60, -55, -15)
    wall(walls, 'WestS', -62, -60, 15, 45)
    wall(walls, 'RangeN', -132, -62, -17, -15)
    wall(walls, 'RangeS', -132, -62, 15, 17)
    wall(walls, 'RangeBack', -132, -130, -15, 15, h=14)

    # spawn: faces the pads
    lobby.add(part('LobbySpawn', (12, 1, 12), (0, Y0 + 0.5, 30), (230, 230, 230), cls='SpawnLocation'))
    sp = lobby.kids[-1]
    sp.props += [('Neutral', 'bool', True), ('Duration', 'int', 0), ('Enabled', 'bool', True),
                 ('AllowTeamChangeOnTouch', 'bool', False)]

    # queue pads: back row has tall signs so they read over the front row from the spawn
    m = {k: pads.add(Item('Folder', k)) for k in ('1v1', '2v2', '3v3', '4v4', 'Infection')}
    team_pad(m['4v4'], '4v4', 1, 4, -40, -42, True)
    team_pad(m['3v3'], '3v3', 1, 3, -6, -42, True)
    team_pad(m['2v2'], '2v2', 1, 2, -46, -14, False)
    team_pad(m['2v2'], '2v2', 2, 2, -24, -14, False)
    for i, x in enumerate((0, 22, 44)):
        team_pad(m['1v1'], '1v1', i + 1, 1, x, -14, False)
    inf = m['Infection'].add(Item('Model', 'Zone'))
    inf.add(part('Rim', (0.4, 23, 23), (34, Y0 + 0.2, -42), WHITE, ROT_UP, shape=2))
    inf.add(part('Circle', (0.5, 22, 22), (34, Y0 + 0.25, -42), MODE_COLOUR['Infection'], ROT_UP, shape=2, touch=True))
    board_with_posts(inf, 'SignBoard', 22, 5, 13, 34, -54, MODE_COLOUR['Infection'], 'INFECTION', '0/12')

    # practice range: shoot west; spots for target dummies at 15/30/45/60 studs from the line
    rng.add(part('ShootingLine', (0.8, 0.1, 30), (-64, Y0 + 0.05, 0), YELLOW))
    for d in (15, 30, 45, 60):
        x = -64 - d
        for z in (-7, 7):
            spot = rng.add(part(f'Target{d}', (4, 0.1, 4), (x, Y0 + 0.05, z), WHITE))
            sign_text(spot, 1, str(d), colour=(0.15, 0.15, 0.15))
    zone = rng.add(part('RangeZone', (70, 12, 30), (-95, Y0 + 6, 0), (255, 255, 255), collide=False, transparency=1,
                        touch=True, query=False))
    del zone
    b = rng.add(part('RangeSign', (30, 4, 0.6), (-60.7, Y0 + 12, 0), MODE_COLOUR['1v1'], ry(math.pi / 2)))
    sign_text(b, 2, 'RANGE')
    LABELS.append(('RANGE', np.array([-60.7, Y0 + 12, 0])))
    return lobby


def write(lobby, path):
    lines = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
             '\t<External>null</External>', '\t<External>nil</External>']
    lobby.xml(lines, 1)
    lines.append('</roblox>')
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def preview(path):
    import os
    from PIL import Image, ImageDraw
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'rifle', 'tools', 'viewmodel_v3'))
    from meshrender import box_tris, raster, shade

    def cyl_tris(size, n=20):
        h, r = size[0] / 2, size[1] / 2
        a = np.linspace(0, 2 * np.pi, n + 1)
        ring = lambda x: np.stack([np.full(n + 1, x), r * np.cos(a), r * np.sin(a)], 1)   # noqa: E731
        top, bot = ring(h), ring(-h); T = []
        for i in range(n):
            T += [[top[i], top[i + 1], [h, 0, 0]], [bot[i], [-h, 0, 0], bot[i + 1]], [top[i], bot[i], bot[i + 1]], [top[i], bot[i + 1], top[i + 1]]]
        return np.array(T)
    Ts, Cs = [], []
    for kind, size, c, R, col in PREVIEW:
        T = cyl_tris(size) if kind == 'cyl' else box_tris(size)
        Ts.append(T @ R.T + c); Cs.append(shade(T @ R.T, col))
    Tw, C = np.concatenate(Ts), np.concatenate(Cs)

    def cam(pos, look, up=(0, 1, 0)):
        f = np.asarray(look, float) - pos; f /= np.linalg.norm(f)
        r = np.cross(f, up); r /= np.linalg.norm(r); u = np.cross(r, f)
        return np.stack([r, u, -f]), np.asarray(pos, float)

    def render(Rc, pos, W, H, f, ortho):
        Tc = (Tw - pos) @ Rc.T
        img = Image.fromarray(raster(Tc, C, W * 2, H * 2, f * 2, ortho=ortho, bg=(150, 190, 230))).resize((W, H), Image.BOX)
        d = ImageDraw.Draw(img)
        for text, p in LABELS:
            q = Rc @ (p - pos)
            if ortho: sx, sy = W / 2 + q[0] * f, H / 2 - q[1] * f
            elif q[2] < -1: sx, sy = W / 2 + f * q[0] / -q[2], H / 2 - f * q[1] / -q[2]
            else: continue
            tw = 6 * len(text)
            d.rectangle([sx - tw / 2 - 2, sy - 6, sx + tw / 2 + 2, sy + 6], fill=(20, 20, 20)); d.text((sx - tw / 2, sy - 5), text, fill=(255, 255, 255))
        return img
    top = render(*cam((-35, Y0 + 300, -5.01), (-35, Y0, -5), up=(0, 0, -1)), 760, 460, 3.6, True)
    eye = render(*cam((0, Y0 + 5.5, 36), (0, Y0 + 4, -40)), 760, 460, 760 / 2 / math.tan(math.radians(35)), False)
    sheet = Image.new('RGB', (760, 920)); sheet.paste(top, (0, 0)); sheet.paste(eye, (0, 460))
    ImageDraw.Draw(sheet).text((6, 466), 'view from the spawn (FOV 70)', fill=(0, 0, 0))
    sheet.save(path)


if __name__ == '__main__':
    lobby = build()
    write(lobby, sys.argv[1])
    n = sum(1 for _ in PREVIEW)
    print('wrote', sys.argv[1], n, 'visible parts')
    if len(sys.argv) > 2:
        preview(sys.argv[2]); print('preview', sys.argv[2])
