"""The wider roster: fifteen creatures of the old kingdom's wilds, from grazing deer to the wraiths of the Gloaming.

Models follow creatures.py's conventions (the hull pivots at the feet, y grows downward, part names are the
contract with FaunaModels.java) and register their materials into skins.SKINS and skins.FEATURES.

Body plans (FaunaModels.java):
  Quadruped - body, head, jaw, tail, ear_l/ear_r, leg_fl/fr/bl/br
  Biped     - head, body, left/right_arm, left/right_leg, robe
  Crawler   - body, head, leg_0 .. leg_7 (even legs on the left)
  Floater   - body, head, cloak, left/right_arm, orbit_0 .. orbit_2
  Bird      - body, neck, head, left/right_wing, left/right_leg, tail
"""
import math

from .model import Model, P, C
from .paint import Ramp, hexrgb
from . import skins as S
from .skins import Skin, Hide, Plate, Cloth, Bone, Crystal, Emissive, EdgeLit, SIDES

# ====================================================================== materials
R = {
    'fawn': Ramp('#4a2e1c', '#6e4629', '#946238', '#b8834e', '#d8a86c'),
    'fawn_belly': Ramp('#8a7058', '#b09478', '#d0b89c', '#ecdcc4'),
    'antler': Ramp('#5a4a38', '#86745a', '#b4a484', '#dcd0b0'),
    'moon': Ramp('#6a86d0', '#a8c0f0', '#dce8ff', '#ffffff'),
    'hare': Ramp('#2e2438', '#4a3c5a', '#6a5a7e', '#8e80a0', '#b4a8c4'),
    'moss_shell': Ramp('#1c2a12', '#2e4a1c', '#446a28', '#5c8a36', '#7aa84a'),
    'shell_rim': Ramp('#2a2016', '#46382a', '#6a5840', '#8e7a5a'),
    'tortoise': Ramp('#2a3020', '#454e34', '#626e4a', '#848f66'),
    'beetle': Ramp('#10121c', '#1e2236', '#303852', '#46527a'),
    'lumen': Ramp('#8a5a12', '#d8942a', '#ffcb58', '#fff0b0'),
    'heron': Ramp('#4e5866', '#707c8c', '#98a4b4', '#c4ceda', '#eef2f8'),
    'heron_dark': Ramp('#1c2230', '#2e3648', '#445066'),
    'beak': Ramp('#6a4a10', '#a8781c', '#d8a430', '#f0cc60'),
    'boar': Ramp('#1e140e', '#34241a', '#4e3828', '#6a4e38', '#866650'),
    'bristle': Ramp('#0e0a08', '#1e1812', '#2e261c', '#40362a'),
    'tusk': Ramp('#8a8068', '#b4aa90', '#dcd4bc', '#f6f0e0'),
    'warden_stone': Ramp('#5e5343', '#7d7159', '#9c8f72', '#b8ab8b', '#d0c4a4'),
    'warden_moss': Ramp('#1f3317', '#2d4a1f', '#3e6128', '#517a31', '#67933c'),
    'rune_gold': Ramp('#8a5a12', '#d8942a', '#ffcb58', '#fff0b0'),
    'wisp': Ramp('#3a2a9c', '#6f7cff', '#b0c4ff', '#ffffff'),
    'monk_robe': Ramp('#0e1e1c', '#16302c', '#21463f', '#2f5e54', '#43806e'),
    'drowned_skin': Ramp('#2a4038', '#3c5a4e', '#527666', '#6c9280'),
    'candle': Ramp('#8a8068', '#b4aa90', '#dcd4bc', '#f6f0e0'),
    'flame': Ramp('#8a4a10', '#d8842a', '#ffb84a', '#fff8e0'),
    'hag_skin': Ramp('#2e3a22', '#465634', '#62744a', '#809464'),
    'hag_robe': Ramp('#14120c', '#262216', '#3a3422', '#504830'),
    'hag_hair': Ramp('#2a2a2e', '#4a4a50', '#6e6e76', '#9a9aa2'),
    'hag_glow': Ramp('#2a8a2a', '#5ae05a', '#b0ffb0', '#ffffff'),
    'bone_old': Ramp('#4a4234', '#6e6450', '#948870', '#b8ad92', '#d8cfb4'),
    'stalker': Ramp('#050308', '#0c0812', '#16101f', '#221a30', '#302444'),
    'wraith': Ramp('#08060c', '#120e1a', '#1e1830', '#2c2446', '#3c3260'),
    'mite': Ramp('#14100c', '#2a2016', '#403220', '#5a482e'),
    'ash': Ramp('#100c0a', '#1e1814', '#302620', '#443830', '#5c4c40'),
    'ember': Ramp('#6a1a04', '#b83a0c', '#f06a1c', '#ffb040', '#fff0a0'),
    'elder_hide': Ramp('#2e2438', '#4a3c5a', '#6a5a7e', '#8e80a0', '#b4a8c4'),
    'elder_mane': Ramp('#dcd8e8', '#eeeaf6', '#f8f6fc', '#ffffff'),
    'bog_moss': Ramp('#1c2a12', '#2a3e1a', '#3a5424', '#4e6c30', '#66883e'),
    'molten': Ramp('#8a2a04', '#e05a10', '#ffa030', '#ffe080', '#ffffff'),
    'pilgrim_robe': Ramp('#1a2230', '#2a3446', '#3e4a60', '#56647c', '#727f96'),
    'pilgrim_mantle': Ramp('#3a0e0e', '#5a1a16', '#7e2a20', '#a03e2c', '#bc5a3e'),
    'pilgrim_leather': Ramp('#2a1a0e', '#46301c', '#654a2c', '#86683e', '#a88852'),
    'stag': Ramp('#3a2416', '#5a3a22', '#7e5430', '#a2703e', '#c69256'),
}


class Spotted(Hide):
    """A hide with pale spots that glow faintly (the glimmerfawn's dapples)."""

    def __init__(self, ramp, spot, glow, rate=0.07, **kw):
        super().__init__(ramp, **kw)
        self.spot, self.spot_glow, self.rate = spot, glow, rate

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        if face in ('top', 'left', 'right') and (x * 7 + y * 13 + seed) % 11 == 0 and r.random() < 0.8:
            return self.spot.copy(), self.spot_glow
        return c, g


class Mossy(Skin):
    """A shell or stone under moss: moss on top faces and the upper rows of the sides, with a few flowers."""

    def __init__(self, ramp, moss, flower=None, **kw):
        super().__init__(ramp, **kw)
        self.moss, self.flower = moss, flower

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        mossy = face == 'top' or (face in SIDES and y < max(1, h // 3) and r.random() < 0.75)
        if mossy:
            c = self.moss.smooth(0.3 + r.random() * 0.6)
            if self.flower is not None and face == 'top' and r.random() < 0.04:
                return self.flower.copy(), self.flower
        return c, g


class Rune(Skin):
    """Carved stone with a glowing inscription running across it."""

    def __init__(self, ramp, glow, **kw):
        super().__init__(ramp, **kw)
        self.glow = glow

    def paint(self, face, x, y, w, h, seed, r):
        c, g = super().paint(face, x, y, w, h, seed, r)
        if face in SIDES and w > 3 and h > 3 and ((x + seed) % 4 == 1 and 1 <= y < h - 1 and (y * 5 + x) % 3 != 0):
            col = self.glow.smooth(0.7)
            return col, col
        return c, g


SKINS = {
    # minibosses
    'elder_hide': Spotted(R['elder_hide'], R['moon'].smooth(0.9), R['moon'].smooth(0.7), grain=3),
    'elder_mane': Hide(R['elder_mane'], grain=2, contrast=0.6),
    'elder_rune': Rune(R['elder_hide'], R['moon']),
    'bog_cloak': Mossy(R['hag_robe'], R['bog_moss'], hexrgb('#5ae05a')),
    'bog_skin': Hide(R['hag_skin'], grain=2),
    'colossus_plate': Plate(R['ash'], seam=3, veins=R['molten'].smooth(0.8)),
    'colossus_core': Emissive(R['molten']),
    # glimmerfawn
    'fawn_hide': Spotted(R['fawn'], R['moon'].smooth(0.8), R['moon'].smooth(0.6), grain=3),
    'fawn_head': Hide(R['fawn'], grain=3),
    'fawn_muzzle': Hide(R['fawn_belly'], grain=2),
    'fawn_leg': Hide(R['fawn'], grain=2),
    'fawn_tail': Hide(R['fawn_belly'], grain=2),
    'antler': Bone(R['antler'], grain=2),
    'antler_glow': Emissive(R['moon']),
    # duskhare
    'hare_fur': Hide(R['hare'], grain=2),
    'hare_ear': EdgeLit(R['hare'], R['moon'].smooth(0.4)),
    'hare_tail': Hide(R['fawn_belly'], grain=2),
    # mossback tortoise
    'shell_moss': Mossy(R['shell_rim'], R['moss_shell'], hexrgb('#b884ff')),
    'shell_rim': Plate(R['shell_rim'], seam=2, rivets=False),
    'tortoise_skin': Hide(R['tortoise'], grain=2),
    # lumen beetle
    'beetle_shell': Plate(R['beetle'], seam=0, rivets=False, contrast=1.3),
    'beetle_glow': Emissive(R['lumen']),
    # tidewader
    'heron_feather': Hide(R['heron'], grain=3),
    'heron_neck': Hide(R['heron'], grain=2),
    'heron_head': Hide(R['heron'], grain=2),
    'heron_beak': Skin(R['beak'], contrast=0.6),
    'heron_wing': Hide(R['heron_dark'], grain=2),
    'heron_leg': Skin(R['beak'], contrast=0.5),
    # thornback boar
    'boar_hide': Hide(R['boar'], grain=2),
    'boar_bristle': Hide(R['bristle'], grain=1, contrast=1.5),
    'boar_snout': Skin(Ramp('#5a3a30', '#7a5244', '#9a6a58', '#b88470'), contrast=0.6),
    'boar_leg': Hide(R['boar'], grain=2),
    'tusk': Bone(R['tusk'], grain=2),
    # stonewarden
    'warden_stone': Mossy(R['warden_stone'], R['warden_moss'], contrast=1.2),
    'warden_rune': Rune(R['warden_stone'], R['rune_gold']),
    'warden_moss': Hide(R['warden_moss'], grain=2),
    # runewisp
    'wisp_core': Emissive(R['wisp']),
    'wisp_rune': Crystal(R['wisp']),
    # drowned choirmonk
    'monk_robe': Cloth(R['monk_robe'], trim=S.R['verdigris'].smooth(0.5)),
    'monk_hem': Cloth(R['monk_robe'], tatter=0.6, hem_glow=S.R['tide_glow'].smooth(0.5)),
    'monk_hood': Cloth(R['monk_robe']),
    'drowned_skin': Hide(R['drowned_skin'], grain=2),
    'candle': Skin(R['candle'], contrast=0.4),
    'candle_flame': Emissive(R['flame']),
    'kelp_strand': Hide(S.R['kelp'], grain=1),
    # mire hag
    'hag_skin': Hide(R['hag_skin'], grain=2),
    'hag_robe': Cloth(R['hag_robe'], tatter=0.5),
    'hag_hair': Hide(R['hag_hair'], grain=1, contrast=1.4),
    'hag_staff': Skin(S.R['wood_twist'], contrast=1.2),
    'hag_lantern': Emissive(R['hag_glow']),
    # glimmerstag
    'stag_hide': Hide(R['stag'], grain=2),
    'saddle_leather': Hide(R['pilgrim_leather'], grain=1),
    'saddle_trim': Skin(S.R['crown_gold'], contrast=0.6),
    # lanternguard pilgrim
    'pilgrim_robe': Cloth(R['pilgrim_robe'], trim=S.R['crown_gold'].smooth(0.5)),
    'pilgrim_mantle': Cloth(R['pilgrim_mantle']),
    'pilgrim_hood': Cloth(R['pilgrim_mantle']),
    'pilgrim_pack': Hide(R['pilgrim_leather'], grain=2),
    'pilgrim_staff': Skin(S.R['wood_twist'], contrast=1.1),
    'pilgrim_lantern': Emissive(R['lumen']),
    # grave crawler
    'crawler_bone': Bone(R['bone_old'], grain=2),
    # gloam stalker
    'stalker_hide': Hide(R['stalker'], grain=2),
    'stalker_claw': Emissive(S.R['gloam_glow']),
    'stalker_wisp': Emissive(S.R['gloam_glow']),
    # shade wraith
    'wraith_robe': Cloth(R['wraith']),
    'wraith_hood': Cloth(R['wraith']),
    'wraith_tatter': Cloth(R['wraith'], tatter=0.8, hem_glow=S.R['gloam_glow'].smooth(0.5)),
    'wraith_arm': Hide(R['wraith'], grain=2),
    'wraith_claw': Emissive(S.R['gloam_glow']),
    # lumenite mite
    'mite_carapace': Plate(R['mite'], seam=2, rivets=False),
    'lumen_crystal': Crystal(R['lumen']),
    # ashen revenant
    'ash_plate': Plate(R['ash'], seam=4, veins=R['ember'].smooth(0.8)),
    'ash_helm': Plate(R['ash'], seam=0, rivets=False, veins=R['ember'].smooth(0.8)),
    'ember_plume': Emissive(R['ember']),
    'ember_blade': Emissive(R['ember']),
}


# ====================================================================== faces
def f_dark_hood(eye, eye_glow):
    """A hood's shadowed opening with two small burning eyes."""
    def paint(tex, gl, fx, fy, w, h, r):
        void = hexrgb('#040306')
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                tex.put(fx + x, fy + y, void)
        ey = h // 2 - 1
        for ex in (w // 2 - 2, w // 2 + 1):
            S._px(tex, gl, fx + ex, fy + ey, eye, eye_glow)
    return paint


def f_hag_face(tex, gl, fx, fy, w, h, r):
    green = hexrgb('#b0ffb0')
    for ex in (1, w - 2):
        S._px(tex, gl, fx + ex, fy + 2, green, hexrgb('#5ae05a'))
    for x in range(2, w - 2):
        tex.put(fx + x, fy + h - 2, hexrgb('#1a120c'))


def f_rune_eyes(tex, gl, fx, fy, w, h, r):
    gold = hexrgb('#ffcb58')
    for x in range(1, w - 1):
        S._px(tex, gl, fx + x, fy + 2, hexrgb('#403626') if x in (w // 2 - 1, w // 2) else gold, None if x in (w // 2 - 1, w // 2) else gold)
    for y in range(4, h - 1):
        tex.put(fx + w // 2, fy + y, hexrgb('#2a2418'))


def f_ember_slit(tex, gl, fx, fy, w, h, r):
    e = hexrgb('#ffb040')
    for x in range(1, w - 1):
        S._px(tex, gl, fx + x, fy + 3, e, e)
    S._px(tex, gl, fx + w // 2, fy + 4, e, e)


FEATURES = {
    'fawn_face': S.f_eyes(hexrgb('#0c0806'), None, spacing=1, row=1),
    'hare_face': S.f_eyes(hexrgb('#e8e0ff'), hexrgb('#b8a8ff'), spacing=1, row=0),
    'tortoise_face': S.f_eyes(hexrgb('#100c08'), None, spacing=1, row=0),
    'beetle_eyes': S.f_eyes(hexrgb('#ffe08a'), hexrgb('#ffcb58'), spacing=1, row=0),
    'heron_eye': S.f_eyes(hexrgb('#f0cc60'), None, spacing=1, row=0),
    'boar_face': S.f_eyes(hexrgb('#d04020'), None, spacing=2, row=1),
    'warden_face': f_rune_eyes,
    'hooded_face': f_dark_hood(hexrgb('#b0fff0'), hexrgb('#3fe0c0')),
    'hag_face': f_hag_face,
    'stalker_face': S.f_eyes(hexrgb('#e8c8ff'), hexrgb('#b884ff'), spacing=1, row=1),
    'wraith_face': f_dark_hood(hexrgb('#ffffff'), hexrgb('#d6b0ff')),
    'mite_eyes': S.f_eyes(hexrgb('#ffe08a'), hexrgb('#ffcb58'), spacing=1, row=0),
    'ash_visor': f_ember_slit,
}
S.SKINS.update(SKINS)
S.FEATURES.update(FEATURES)


# ====================================================================== models
def quad_leg(name, x, y, z, w, h, mat, foot=None):
    cubes = [C(-w / 2, 0, -w / 2, w, h, w, mat)]
    if foot:
        cubes.append(C(-w / 2, h - 1, -w / 2 - 0.5, w, 1, w + 0.5, foot))
    return P(name, (x, y, z), *cubes)


def glimmerfawn():
    """A slender deer whose dapples and antler-tips shine like moonlight."""
    return Model('glimmerfawn', 64, [
        P('body', (0, -13, 0),
          C(-3, -3, -7, 6, 6, 13, 'fawn_hide'),
          C(-2.5, 2.5, -6, 5, 1, 10, 'fawn_muzzle'),
          kids=[
              P('head', (0, -2, -6),
                C(-1.5, -8, -2, 3, 9, 3, 'fawn_hide'),
                C(-2, -11, -4, 4, 4, 5, 'fawn_head', 'fawn_face'),
                C(-1, -9.5, -7, 2, 2, 3, 'fawn_muzzle'),
                C(1, -17, -2, 1, 6, 1, 'antler'), C(1, -17, -2, 3, 1, 1, 'antler'), C(2, -20, -2, 1, 3, 1, 'antler'),
                C(-2, -17, -2, 1, 6, 1, 'antler'), C(-4, -17, -2, 3, 1, 1, 'antler'), C(-3, -20, -2, 1, 3, 1, 'antler'),
                C(3.5, -18, -2, 1, 1, 1, 'antler_glow'), C(-4.5, -18, -2, 1, 1, 1, 'antler_glow'),
                C(2, -21, -2, 1, 1, 1, 'antler_glow'), C(-3, -21, -2, 1, 1, 1, 'antler_glow'),
                kids=[P('ear_l', (2, -10, -1), C(0, -1, -0.5, 3, 2, 1, 'fawn_hide')),
                      P('ear_r', (-2, -10, -1), C(-3, -1, -0.5, 3, 2, 1, 'fawn_hide'))],
                rot=(-0.2, 0, 0)),
              quad_leg('leg_fl', 2, 3, -5, 2, 10, 'fawn_leg'), quad_leg('leg_fr', -2, 3, -5, 2, 10, 'fawn_leg'),
              quad_leg('leg_bl', 2, 3, 4.5, 2, 10, 'fawn_leg'), quad_leg('leg_br', -2, 3, 4.5, 2, 10, 'fawn_leg'),
              P('tail', (0, -2.5, 6), C(-1, -1, 0, 2, 2, 2, 'fawn_tail')),
          ]),
    ])


def duskhare():
    """A long-eared hare the colour of dusk; its ear-tips catch the light."""
    return Model('duskhare', 64, [
        P('body', (0, -4, 0),
          C(-2, -2, -3, 4, 4, 6, 'hare_fur'),
          kids=[
              P('head', (0, -2, -3), C(-1.5, -3, -3, 3, 3, 3, 'hare_fur', 'hare_face'),
                kids=[P('ear_l', (0.8, -3, -1.5), C(-0.5, -5, -0.5, 1, 5, 1, 'hare_ear')),
                      P('ear_r', (-0.8, -3, -1.5), C(-0.5, -5, -0.5, 1, 5, 1, 'hare_ear'))]),
              quad_leg('leg_fl', 1, 1, -2, 1, 3, 'hare_fur'), quad_leg('leg_fr', -1, 1, -2, 1, 3, 'hare_fur'),
              P('leg_bl', (1.3, 0, 2), C(-1, 0, -1.5, 2, 4, 3, 'hare_fur')),
              P('leg_br', (-1.3, 0, 2), C(-1, 0, -1.5, 2, 4, 3, 'hare_fur')),
              P('tail', (0, -1, 3), C(-1, -1, 0, 2, 2, 1, 'hare_tail')),
          ]),
    ])


def mossback_tortoise():
    """A great tortoise with a garden growing on its shell."""
    return Model('mossback_tortoise', 64, [
        P('body', (0, -5, 0),
          C(-5, -4, -6, 10, 4, 12, 'shell_moss'),
          C(-6, 0, -7, 12, 2, 14, 'shell_rim'),
          C(-4, -6, -4, 8, 2, 8, 'shell_moss'),
          C(-2, -7, -2, 4, 1, 4, 'shell_moss'),
          kids=[
              P('head', (0, 0.5, -7), C(-1.5, -1.5, -4, 3, 3, 4, 'tortoise_skin', 'tortoise_face')),
              quad_leg('leg_fl', 4, 1, -5, 3, 4, 'tortoise_skin'), quad_leg('leg_fr', -4, 1, -5, 3, 4, 'tortoise_skin'),
              quad_leg('leg_bl', 4, 1, 5, 3, 4, 'tortoise_skin'), quad_leg('leg_br', -4, 1, 5, 3, 4, 'tortoise_skin'),
              P('tail', (0, 1, 7), C(-0.5, -0.5, 0, 1, 1, 2, 'tortoise_skin')),
          ]),
    ])


def _crawler_legs(xs, zs, length, thick, mat, y=0.5):
    legs = []
    i = 0
    for z in zs:
        for side in (1, -1):
            x0 = 0 if side > 0 else -length
            legs.append(P(f'leg_{i}', (side * xs, y, z), C(x0, -thick / 2, -thick / 2, length, thick, thick, mat)))
            i += 1
    return legs


def lumen_beetle():
    """A thumb-sized beetle that carries a lantern of its own through the caves."""
    return Model('lumen_beetle', 64, [
        P('body', (0, -2, 0),
          C(-1.5, -1, -2, 3, 2, 4, 'beetle_shell'),
          C(-1, -0.8, 2, 2, 1.6, 2, 'beetle_glow'),
          kids=[P('head', (0, 0, -2), C(-1, -0.5, -1.5, 2, 1.5, 1.5, 'beetle_shell', 'beetle_eyes'))]
               + _crawler_legs(1.5, (-1, 0.5, 2), 2.5, 0.9, 'beetle_shell')),
    ])


def tidewader():
    """A tall grey heron of the chapel shallows."""
    def leg(name, x):
        return P(name, (x, 2, 0.5), C(-0.5, 0, -0.5, 1, 9, 1, 'heron_leg'), C(-1, 8.5, -2, 2, 0.5, 3, 'heron_leg'))
    return Model('tidewader', 64, [
        P('body', (0, -11, 0),
          C(-2, -2, -4, 4, 4, 7, 'heron_feather'),
          kids=[
              P('neck', (0, -1, -3.5), C(-0.75, -7, -0.75, 1.5, 7, 1.5, 'heron_neck'),
                kids=[P('head', (0, -7, 0), C(-1, -2, -1.5, 2, 2, 3, 'heron_head', 'heron_eye'),
                        C(-0.5, -1.5, -5.5, 1, 1, 4, 'heron_beak'), C(-0.25, -3, 0.5, 0.5, 1.5, 2, 'heron_wing'))]),
              P('left_wing', (2, -1.5, -2), C(0, 0, 0, 1, 3, 7, 'heron_wing')),
              P('right_wing', (-2, -1.5, -2), C(-1, 0, 0, 1, 3, 7, 'heron_wing')),
              leg('left_leg', 1), leg('right_leg', -1),
              P('tail', (0, -1, 3), C(-1.5, 0, 0, 3, 1, 3, 'heron_wing')),
          ]),
    ])


def thornback_boar():
    """A heavy forest boar with a ridge of black quills and yellowed tusks."""
    return Model('thornback_boar', 64, [
        P('body', (0, -10, 0),
          C(-4, -4, -7, 8, 8, 14, 'boar_hide'),
          C(-1, -6, -6, 2, 2, 11, 'boar_bristle'),
          C(-2, -5.5, -5, 1, 1.5, 8, 'boar_bristle'), C(1, -5.5, -5, 1, 1.5, 8, 'boar_bristle'),
          kids=[
              P('head', (0, -1, -7),
                C(-3.5, -3, -6, 7, 6, 6, 'boar_hide', 'boar_face'),
                C(-2, 0, -8, 4, 3, 2, 'boar_snout'),
                C(-3, 0.5, -8, 1, 3, 1, 'tusk'), C(2, 0.5, -8, 1, 3, 1, 'tusk'),
                C(-3, -1.5, -8.5, 1, 1, 1, 'tusk'), C(2, -1.5, -8.5, 1, 1, 1, 'tusk'),
                kids=[P('ear_l', (2.5, -3, -2), C(0, -2, 0, 2, 2, 1, 'boar_hide')),
                      P('ear_r', (-2.5, -3, -2), C(-2, -2, 0, 2, 2, 1, 'boar_hide'))]),
              quad_leg('leg_fl', 2.5, 4, -4.5, 3, 6, 'boar_leg'), quad_leg('leg_fr', -2.5, 4, -4.5, 3, 6, 'boar_leg'),
              quad_leg('leg_bl', 2.5, 4, 4.5, 3, 6, 'boar_leg'), quad_leg('leg_br', -2.5, 4, 4.5, 3, 6, 'boar_leg'),
              P('tail', (0, -2, 7), C(-0.5, 0, 0, 1, 3, 1, 'boar_hide')),
          ]),
    ])


def stonewarden():
    """A sentinel of mossy wardstone left by the Lanternguard; a rune still burns in its chest."""
    def leg(name, x):
        return P(name, (x, -12, 0), C(-3, 0, -3, 6, 12, 6, 'warden_stone'))

    def arm(name, x):
        return P(name, (x, -12, 0), C(-2.5, -1, -2.5, 5, 18, 5, 'warden_stone'),
                 C(-3, 13, -3, 6, 4, 6, 'warden_moss'))
    return Model('stonewarden', 128, [
        leg('left_leg', 3.5), leg('right_leg', -3.5),
        P('body', (0, -12, 0),
          C(-7, -14, -4, 14, 14, 8, 'warden_stone'),
          C(-3, -11, -4.5, 6, 6, 1, 'warden_rune'),
          C(-7.5, -15, -4.5, 15, 2, 9, 'warden_moss'),
          kids=[
              P('head', (0, -14, -1), C(-3.5, -7, -3.5, 7, 7, 7, 'warden_stone', 'warden_face'),
                C(-4, -8, -4, 8, 2, 8, 'warden_moss')),
              arm('left_arm', 9.5), arm('right_arm', -9.5),
          ]),
    ])


def runewisp():
    """A mote of written light that drifts through birch woods at night, trailing rings of runes."""
    def ring(name, radius, n, size):
        cubes = []
        for k in range(n):
            a = 2 * math.pi * k / n
            cubes.append(C(math.cos(a) * radius - size / 2, -size / 2, math.sin(a) * radius - size / 2, size, size, size, 'wisp_rune'))
        return P(name, (0, 0, 0), *cubes)
    return Model('runewisp', 64, [
        P('body', (0, -10, 0),
          C(-2, -2, -2, 4, 4, 4, 'wisp_core'),
          C(-1, -3, -1, 2, 6, 2, 'wisp_core'), C(-3, -1, -1, 6, 2, 2, 'wisp_core'), C(-1, -1, -3, 2, 2, 6, 'wisp_core'),
          kids=[ring('orbit_0', 4.5, 6, 1), ring('orbit_1', 6.0, 8, 0.8), ring('orbit_2', 3.0, 4, 1.2)]),
    ])


def _humanoid(name, width, robe_mat, head_cubes, arm_mat, legs_mat, body_mat, right_extra=(), left_extra=(), body_extra=(),
              robe=True, legs=True):
    parts = []
    if legs:
        parts += [P('left_leg', (1.9, -12, 0), C(-2, 0, -2, 4, 12, 4, legs_mat)),
                  P('right_leg', (-1.9, -12, 0), C(-2, 0, -2, 4, 12, 4, legs_mat))]
    kids = [P('head', (0, 0, 0), *head_cubes),
            P('left_arm', (5, 2, 0), C(-1, -2, -2, 3, 12, 4, arm_mat), *left_extra),
            P('right_arm', (-5, 2, 0), C(-2, -2, -2, 3, 12, 4, arm_mat), *right_extra)]
    if robe:
        kids.append(P('robe', (0, 12, 0), C(-4.5, 0, -3, 9, 11, 6, robe_mat)))
    parts.append(P('body', (0, -24, 0), C(-4, 0, -2, 8, 12, 4, body_mat), *body_extra, kids=kids))
    return Model(name, width, parts)


def drowned_choirmonk():
    """A monk of the drowned chapel, still singing the vespers under the water. Its hymn weighs on the living."""
    return _humanoid('drowned_choirmonk', 64, 'monk_hem',
                     [C(-4, -8, -4, 8, 8, 8, 'monk_hood', 'hooded_face'), C(-2, -10, -2, 4, 2, 4, 'monk_hood')],
                     'monk_robe', 'monk_robe', 'monk_robe',
                     right_extra=[C(-1.5, 9, -5, 2, 4, 2, 'candle'), C(-1, 7, -4.5, 1, 2, 1, 'candle_flame')],
                     body_extra=[C(-3, 2, 2.05, 1, 9, 0, 'kelp_strand'), C(1, 1, 2.05, 1, 11, 0, 'kelp_strand')])


def mire_hag():
    """A swamp witch bent double under her lantern, trading curses for bones."""
    return _humanoid('mire_hag', 64, 'hag_robe',
                     [C(-3.5, -7, -3.5, 7, 7, 7, 'hag_skin', 'hag_face'), C(-4, -8, -3, 8, 6, 7.5, 'hag_hair'),
                      C(-1, -4, -6, 2, 3, 2, 'hag_skin')],
                     'hag_robe', 'hag_robe', 'hag_robe',
                     right_extra=[C(-1, -8, -3, 1, 22, 1, 'hag_staff'), C(-2, -11, -4, 3, 3, 3, 'hag_lantern')])


def grave_crawler():
    """A barrow's leftover: a skull and a spine on too many arms, fast in the dark."""
    return Model('grave_crawler', 64, [
        P('body', (0, -4, 0),
          C(-3, -2, -5, 6, 4, 10, 'crawler_bone', 'rib_glow', face='top'),
          C(-1, -1.5, 5, 2, 2, 4, 'crawler_bone'),
          kids=[P('head', (0, -1, -5), C(-2.5, -2.5, -5, 5, 5, 5, 'crawler_bone', 'skull_face'))]
               + _crawler_legs(3, (-3, 0.5, 3.5), 6, 1, 'crawler_bone', y=0)),
    ])


def gloam_stalker():
    """A long, low cat of the Gloaming. It is nearly invisible until it is close enough to matter."""
    return Model('gloam_stalker', 64, [
        P('body', (0, -9, 0),
          C(-3, -3, -7, 6, 5, 14, 'stalker_hide'),
          C(-0.5, -4, -5, 1, 1, 10, 'stalker_claw'),
          kids=[
              P('head', (0, -1, -7), C(-2.5, -2.5, -5, 5, 5, 5, 'stalker_hide', 'stalker_face'),
                kids=[P('ear_l', (1.5, -2.5, -2), C(0, -2.5, 0, 1, 2.5, 1, 'stalker_hide')),
                      P('ear_r', (-1.5, -2.5, -2), C(-1, -2.5, 0, 1, 2.5, 1, 'stalker_hide')),
                      P('jaw', (0, 1.5, -3.5), C(-1.5, 0, -1.5, 3, 1, 2, 'stalker_hide'))]),
              quad_leg('leg_fl', 2, 2, -5, 2, 7, 'stalker_hide', 'stalker_claw'), quad_leg('leg_fr', -2, 2, -5, 2, 7, 'stalker_hide', 'stalker_claw'),
              quad_leg('leg_bl', 2, 2, 5, 2, 7, 'stalker_hide', 'stalker_claw'), quad_leg('leg_br', -2, 2, 5, 2, 7, 'stalker_hide', 'stalker_claw'),
              P('tail', (0, -2, 7), C(-0.5, -0.5, 0, 1, 1, 10, 'stalker_hide'), C(-1, -1, 10, 2, 2, 2, 'stalker_wisp')),
          ]),
    ])


def shade_wraith():
    """A hooded shade of the Gloaming with no legs and too-long arms."""
    return Model('shade_wraith', 64, [
        P('body', (0, -20, 0),
          C(-4, -2, -2.5, 8, 10, 5, 'wraith_robe'),
          kids=[
              P('head', (0, -2, 0), C(-3.5, -7, -3.5, 7, 7, 7, 'wraith_hood', 'wraith_face'), C(-2.5, -9, -1, 5, 2, 5, 'wraith_hood')),
              P('cloak', (0, 8, 0), C(-4.5, 0, -3, 9, 11, 6, 'wraith_tatter')),
              P('left_arm', (4.5, -1, 0), C(0, 0, -1, 2, 12, 2, 'wraith_arm'), C(-0.5, 11, -1.5, 3, 3, 3, 'wraith_claw')),
              P('right_arm', (-4.5, -1, 0), C(-2, 0, -1, 2, 12, 2, 'wraith_arm'), C(-2.5, 11, -1.5, 3, 3, 3, 'wraith_claw')),
          ]),
    ])


def lumenite_mite():
    """A burrowing mite that eats light: lumenite crystals grow from its back."""
    return Model('lumenite_mite', 64, [
        P('body', (0, -2.5, 0),
          C(-2, -1.5, -2.5, 4, 3, 5, 'mite_carapace'),
          C(-1, -3.5, -1, 2, 2, 2, 'lumen_crystal'), C(0.5, -3, 1, 1, 2, 1, 'lumen_crystal'), C(-1.5, -2.8, -2, 1, 1.5, 1, 'lumen_crystal'),
          kids=[P('head', (0, 0, -2.5), C(-1.5, -1, -2, 3, 2, 2, 'mite_carapace', 'mite_eyes'))]
               + _crawler_legs(2, (-1.5, 0.5, 2), 3, 1.0, 'mite_carapace', y=1)),
    ])


def ashen_revenant():
    """A knight burned in the Sundering who never stopped burning; its armour glows at every seam."""
    return _humanoid('ashen_revenant', 64, 'ash_plate',
                     [C(-4, -8, -4, 8, 8, 8, 'ash_helm', 'ash_visor'), C(-0.5, -13, -3, 1, 5, 6, 'ember_plume')],
                     'ash_plate', 'ash_plate', 'ash_plate', robe=False,
                     right_extra=[C(-1, 9, -11, 1, 2, 13, 'ember_blade'), C(-2.5, 8.5, -1.5, 4, 3, 1, 'ash_plate')])


def elderhorn():
    """Elderhorn, the Grove King: a stag the size of a cart, crowned with antlers of moonlight and runes on its flanks."""
    tines = []
    for side in (1, -1):
        x = 1.5 if side > 0 else -2.5
        tines += [C(x, -19, -2, 1, 8, 1, 'antler'), C(x + side * 1, -20, -2, 3 * side if side > 0 else 3, 1, 1, 'antler')]
        for k, (dx, dy, h) in enumerate(((2, -23, 4), (4, -22, 3), (6, -24, 5), (3, -26, 3))):
            xx = x + side * dx if side > 0 else x - dx
            tines.append(C(xx, dy, -2, 1, h, 1, 'antler'))
            tines.append(C(xx, dy - 1, -2, 1, 1, 1, 'antler_glow'))
    return Model('elderhorn', 128, [
        P('body', (0, -13, 0),
          C(-3.5, -3.5, -8, 7, 7, 15, 'elder_hide'),
          C(-3, -5, -8, 6, 3, 6, 'elder_mane'),
          C(-3.6, -2, -3, 0.1, 3, 8, 'elder_rune'), C(3.5, -2, -3, 0.1, 3, 8, 'elder_rune'),
          kids=[
              P('head', (0, -3, -7),
                C(-2, -9, -2.5, 4, 10, 4, 'elder_mane'),
                C(-2.5, -12, -5, 5, 4, 6, 'elder_hide', 'fawn_face'),
                C(-1.5, -10.5, -8, 3, 2, 3, 'fawn_muzzle'),
                *tines,
                kids=[P('ear_l', (2.5, -11, -1), C(0, -1, -0.5, 3, 2, 1, 'elder_hide')),
                      P('ear_r', (-2.5, -11, -1), C(-3, -1, -0.5, 3, 2, 1, 'elder_hide'))],
                rot=(-0.2, 0, 0)),
              quad_leg('leg_fl', 2.5, 3, -6, 2, 10, 'fawn_leg'), quad_leg('leg_fr', -2.5, 3, -6, 2, 10, 'fawn_leg'),
              quad_leg('leg_bl', 2.5, 3, 5, 2, 10, 'fawn_leg'), quad_leg('leg_br', -2.5, 3, 5, 2, 10, 'fawn_leg'),
              P('tail', (0, -3, 7), C(-1, -1, 0, 2, 2, 3, 'elder_mane')),
          ]),
    ])


def bog_mother():
    """The Bog Mother: the eldest hag, grown huge on bog-magic, draped in living moss, a lantern in each hand."""
    return _humanoid('bog_mother', 64, 'bog_cloak',
                     [C(-4, -8, -4, 8, 8, 8, 'bog_skin', 'hag_face'), C(-4.5, -9, -3.5, 9, 7, 8.5, 'hag_hair'),
                      C(-1, -5, -7, 2, 4, 3, 'bog_skin'), C(-3, -11, -2, 1, 3, 1, 'hag_staff'), C(2, -11, -2, 1, 3, 1, 'hag_staff')],
                     'bog_cloak', 'bog_cloak', 'bog_cloak',
                     right_extra=[C(-1, -8, -3, 1, 22, 1, 'hag_staff'), C(-2.5, -11.5, -4.5, 4, 4, 4, 'hag_lantern')],
                     left_extra=[C(-0.5, 10, -1.5, 3, 3, 3, 'hag_lantern')],
                     body_extra=[C(-4.5, -1, -2.5, 9, 6, 5.5, 'bog_cloak')])


def cinder_colossus():
    """The Cinder Colossus: the Order's great war-effigy, filled with the Sundering's fire and left to walk the sands."""
    return _humanoid('cinder_colossus', 128, 'colossus_plate',
                     [C(-4, -8, -4, 8, 8, 8, 'ash_helm', 'ash_visor'), C(-5, -10, -1, 2, 5, 2, 'colossus_plate'), C(3, -10, -1, 2, 5, 2, 'colossus_plate'),
                      C(-0.5, -14, -3, 1, 6, 7, 'ember_plume')],
                     'colossus_plate', 'colossus_plate', 'colossus_plate', robe=False,
                     right_extra=[C(-1.5, 9, -16, 2, 3, 18, 'ember_blade'), C(-3.5, 8.5, -1.5, 6, 4, 1, 'colossus_plate')],
                     left_extra=[C(-0.5, -3, -3, 4, 4, 6, 'colossus_plate')],
                     body_extra=[C(-2, 3, -2.5, 4, 5, 1, 'colossus_core'), C(-5, -1, -3, 10, 3, 6, 'colossus_plate')])


def glimmerstag():
    """A grown stag of the glimmer herds, strong enough to carry a knight: a crown of moonlit antlers, and a saddle
    once someone has earned the right to put one on it."""
    tines = []
    for side in (1, -1):
        x = 1 if side > 0 else -2
        tines += [C(x, -18, -2, 1, 7, 1, 'antler'), C(x + (1 if side > 0 else -3), -19, -2, 3, 1, 1, 'antler')]
        for dx, dy, h in ((3, -23, 5), (5, -22, 3), (2, -26, 3)):
            xx = x + dx if side > 0 else x - dx
            tines += [C(xx, dy, -2, 1, h, 1, 'antler'), C(xx, dy - 1, -2, 1, 1, 1, 'antler_glow')]
    return Model('glimmerstag', 64, [
        P('body', (0, -15, 0),
          C(-3.5, -3.5, -8, 7, 7, 15, 'stag_hide'),
          C(-3, 3, -7, 6, 1, 12, 'fawn_muzzle'),
          kids=[
              P('head', (0, -2.5, -7),
                C(-2, -9, -2.5, 4, 10, 4, 'stag_hide'),
                C(-2.5, -12, -5, 5, 4, 6, 'stag_hide', 'fawn_face'),
                C(-1.5, -10.5, -8, 3, 2, 3, 'fawn_muzzle'),
                *tines,
                kids=[P('ear_l', (2.5, -11, -1), C(0, -1, -0.5, 3, 2, 1, 'stag_hide')),
                      P('ear_r', (-2.5, -11, -1), C(-3, -1, -0.5, 3, 2, 1, 'stag_hide'))],
                rot=(-0.2, 0, 0)),
              P('saddle', (0, -3.5, 0),
                C(-4, -1, -4, 8, 2, 8, 'saddle_leather'), C(-4.2, -1.5, -4.2, 8.4, 1, 1, 'saddle_trim'),
                C(-4.2, -1.5, 3.2, 8.4, 1, 1, 'saddle_trim'), C(-4.6, 0, -1, 1, 6, 2, 'saddle_leather'),
                C(3.6, 0, -1, 1, 6, 2, 'saddle_leather')),
              quad_leg('leg_fl', 2.5, 3, -6, 2, 12, 'fawn_leg'), quad_leg('leg_fr', -2.5, 3, -6, 2, 12, 'fawn_leg'),
              quad_leg('leg_bl', 2.5, 3, 5.5, 2, 12, 'fawn_leg'), quad_leg('leg_br', -2.5, 3, 5.5, 2, 12, 'fawn_leg'),
              P('tail', (0, -3, 7), C(-1, -1, 0, 2, 2, 3, 'fawn_tail')),
          ]),
    ])


def lanternguard_pilgrim():
    """A pilgrim of the fallen Order, walking the old roads from wayshrine to wayshrine with a pack of its goods."""
    return _humanoid('lanternguard_pilgrim', 64, 'pilgrim_robe',
                     [C(-4, -8, -4, 8, 8, 8, 'pilgrim_hood', 'hooded_face'), C(-2, -10, -2, 4, 2, 4, 'pilgrim_hood')],
                     'pilgrim_robe', 'pilgrim_robe', 'pilgrim_robe',
                     right_extra=[C(-1, -10, -3, 1, 24, 1, 'pilgrim_staff'), C(-2.5, -13, -4.5, 4, 4, 4, 'pilgrim_lantern')],
                     body_extra=[C(-4.5, -0.5, -2.5, 9, 4, 5, 'pilgrim_mantle'), C(-3.5, 1, 2, 7, 8, 3, 'pilgrim_pack'),
                                 C(-4, 0, 5, 8, 2, 2, 'pilgrim_pack')])


MINIBOSSES = [elderhorn, bog_mother, cinder_colossus]

FAUNA = [glimmerfawn, duskhare, mossback_tortoise, lumen_beetle, tidewader, thornback_boar, stonewarden, runewisp,
         drowned_choirmonk, mire_hag, grave_crawler, gloam_stalker, shade_wraith, lumenite_mite, ashen_revenant] + MINIBOSSES + [lanternguard_pilgrim, glimmerstag]
