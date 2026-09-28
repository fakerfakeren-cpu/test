"""Item sprites (16x16) for Astralfall, drawn as ASCII art with shared palettes."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'astralfall', 'textures', 'item')

# Shared legend. Upper/lowercase pairs are light/dark variants.
L = {
    'K': hexc('#0b0a14'),   # outline
    'k': hexc('#1d1a2c'),   # dark outline/shadow
    # starmetal (steel blue)
    'S': hexc('#eef5ff'), 's': hexc('#a9c1ea'), 'm': hexc('#6f86b6'), 'n': hexc('#46587f'), 'N': hexc('#28324d'),
    # gold
    'G': hexc('#ffe9a3'), 'g': hexc('#f2c14e'), 'h': hexc('#b9862a'), 'H': hexc('#6b4a12'),
    # cyan crystal
    'C': hexc('#effeff'), 'c': hexc('#9af3ff'), 'q': hexc('#3fc6e0'), 'Q': hexc('#1f7ea3'), 'w': hexc('#123e5c'),
    # violet / void
    'V': hexc('#f3e4ff'), 'v': hexc('#c998ff'), 'p': hexc('#9150e0'), 'P': hexc('#5a2394'), 'x': hexc('#2a0f4a'), 'X': hexc('#12061f'),
    # meteor / lava
    'R': hexc('#fff1c9'), 'r': hexc('#ffc56b'), 'o': hexc('#ff7a1f'), 'O': hexc('#b4380c'), 'e': hexc('#5a1606'),
    # rock
    'a': hexc('#4d4358'), 'b': hexc('#3d3446'), 'd': hexc('#2d2634'), 'D': hexc('#1f1a25'),
    # wood/leather
    'l': hexc('#8a5a34'), 'L': hexc('#5a3820'), 'u': hexc('#3a2414'),
    # navy
    'y': hexc('#4150a6'), 'Y': hexc('#2e3880'), 'z': hexc('#212962'), 'Z': hexc('#161b44'),
    # white/misc
    'W': hexc('#ffffff'), 'i': hexc('#d8d8e8'), 'I': hexc('#8a8aa0'),
    # eclipse (black sun + corona)
    'E': hexc('#07050c'), 'f': hexc('#ff5a36'), 'F': hexc('#ffd0a0'),
}

ITEMS = {}

def item(name):
    def deco(fn):
        ITEMS[name] = fn
        return fn
    return deco

def spr(rows):
    return sprite(rows, L)


@item('raw_starmetal')
def _():
    return spr([
        "................",
        "................",
        "................",
        "......KKKK......",
        "....KKmsSsK.....",
        "...KnmsSSsmK....",
        "..KnmmssSsmnK...",
        "..KnbmmsssmnK...",
        "..KNbamnmsmmnK..",
        "..KNdbamnmmmnK..",
        "...KNdbamnnnNK..",
        "...KNNddbnnNK...",
        "....KKNNNNNK....",
        "......KKKKK.....",
        "................",
        "................",
    ])


@item('starmetal_ingot')
def _():
    return spr([
        "................",
        "................",
        "................",
        "................",
        ".......KKKKK....",
        ".....KKSSSsmK...",
        "...KKSSSsssmnK..",
        "..KSSSssssmmnK..",
        "..KsssssmmmnnK..",
        "..KmmsgmmmnnK...",
        "..KnmmmmnnNK....",
        "..KNnnnnNKK.....",
        "...KKKKKK.......",
        "................",
        "................",
        "................",
    ])


@item('starmetal_nugget')
def _():
    return spr([
        "................",
        "................",
        "................",
        "................",
        "................",
        "......KKK.......",
        ".....KSsmK......",
        "....KSssmnK.KK..",
        "....KsmmnnKKsmK.",
        ".....KnnNKKsmnK.",
        "......KKK.KnnNK.",
        "...KKK.....KKK..",
        "..KsmnK.........",
        "..KmnNK.........",
        "...KKK..........",
        "................",
    ])


@item('skyshard')
def _():
    return spr([
        "................",
        ".........K......",
        "........KCK.....",
        ".......KCcqK....",
        ".......KccqK....",
        "......KCcqQK....",
        "......KccqQK....",
        ".....KCcqqQwK...",
        ".....KccqQQwK...",
        "....KCcqqQwK....",
        "....KccqQQwK....",
        "...KCcqQQwK.....",
        "...KcqqQwK......",
        "....KqQwK.......",
        ".....KKK........",
        "................",
    ])


@item('void_essence')
def _():
    return spr([
        "................",
        "................",
        ".......KK.......",
        "......KvpK......",
        ".....KvpPK......",
        "....KvpPPxK.....",
        "...KvpPxxXxK....",
        "...KpPxXXXxK....",
        "..KvpxXVXXxPK...",
        "..KpPxXXXxxPK...",
        "..KpPPxXxxPPK...",
        "...KpPPxxPPK....",
        "....KppPPpK.....",
        ".....KKKKK......",
        "................",
        "................",
    ])


@item('stardust')
def _():
    return spr([
        "................",
        "................",
        "....W...........",
        "...WcW......G...",
        "....W......GgG..",
        "...........hG...",
        ".......C........",
        "......CqC.......",
        ".....CqWqC......",
        "......CqC..v....",
        ".......C..vVv...",
        "...g.......v....",
        "..GgG...........",
        "...g......W.....",
        ".........WqW....",
        "..........W.....",
    ])


@item('fallen_star')
def _():
    return spr([
        "................",
        ".......KK.......",
        "......KWRK......",
        "......KRrK......",
        ".....KRrrrK.....",
        "KKKKKRWRrrrKKKKK",
        "KRRRWWWRRrrrroOK",
        ".KRRWWRRrrrooOK.",
        "..KKRRRrrrroKK..",
        "....KRrrrroK....",
        "...KRrrKKroOK...",
        "...KrrKK.KooK...",
        "..KrrK....KoOK..",
        "..KoK......KOK..",
        "..KK........KK..",
        "................",
    ])


@item('stellar_core')
def _():
    return spr([
        "................",
        "......KKKK......",
        "....KKgGGgKK....",
        "...KgGhhhhGgK...",
        "..KgGhqcCqhGgK..",
        "..KGhqcWWcqhGK..",
        ".KgGhcWWWWchGgK.",
        ".KgGhcWWWWchGgK.",
        ".KghhqcWWcqhhgK.",
        "..KghQqccqQhgK..",
        "..KHghhqqhhghK..",
        "...KHgghhggHK...",
        "....KKHHHHKK....",
        "......KKKK......",
        "................",
        "................",
    ])


@item('eclipse_sigil')
def _():
    return spr([
        "................",
        ".....KKKKKK.....",
        "...KKhgggghKK...",
        "..KhgFfFFfFghK..",
        "..KgFfKKKKfFgK..",
        ".KhgfKEEEEKfghK.",
        ".KgFKEEEEEEKFgK.",
        ".KgFKEEvvEEKFgK.",
        ".KgFKEEvvEEKFgK.",
        ".KgFKEEEEEEKFgK.",
        ".KhgfKEEEEKfghK.",
        "..KgFfKKKKfFgK..",
        "..KhgFfFFfFghK..",
        "...KKhgggghKK...",
        ".....KKKKKK.....",
        "................",
    ])


@item('astral_journal')
def _():
    return spr([
        "................",
        "..KKKKKKKKKKK...",
        "..KzyyyyyyyzKK..",
        "..KzYYYYYYYzKiK.",
        "..KzYYYgYYYzKiK.",
        "..KzYYgGgYYzKiK.",
        "..KzYgGWGgYzKiK.",
        "..KzYYgGgYYzKiK.",
        "..KzYYYgYYYzKiK.",
        "..KzYYYYYYYzKiK.",
        "..KzYvYYYqYzKiK.",
        "..KzYYYYYYYzKiK.",
        "..KzzzzzzzzzKiK.",
        "..KhgggggggggKK.",
        "...KKKKKKKKKKK..",
        "................",
    ])


# ---------------------------------------------------------------- weapons
@item('starblade')
def _():
    return spr([
        "..............KK",
        ".............KWK",
        "............KWcK",
        "...........KWcqK",
        "..........KWcqK.",
        ".........KWcqK..",
        "........KWcqK...",
        ".......KWcqK....",
        "..KK..KWcqK.....",
        "..KgKKWcqK......",
        "...KgKcqK.......",
        "....KgKK........",
        "...KLKgK........",
        "..KLKKKgK.......",
        ".KqKK..KK.......",
        ".KKK............",
    ])


@item('comet_maul')
def _():
    return spr([
        ".......KKKK.....",
        "......KoraaK....",
        ".....KorRabbK...",
        "....KoorraabdK..",
        "....KOoorabbdK..",
        "....KeOoabbddK..",
        ".....KeObbdDKK..",
        "......KeKdDLK...",
        ".......KKKLK....",
        "........KLK.....",
        ".......KLK......",
        "......KLK.......",
        ".....KLK........",
        "....KgK.........",
        "...KLK..........",
        "...KK...........",
    ])


@item('riftcaller')
def _():
    return spr([
        "......KKKKK.....",
        "....KKvVVVvK....",
        "...KvpPKKKpvK...",
        "..KvpKK...KKK...",
        "..KpK...........",
        "..KPK.......KK..",
        "...KK......KPK..",
        "..........KxK...",
        ".........KxK....",
        "........KuK.....",
        ".......KuK......",
        "......KuK.......",
        ".....KuK........",
        "....KvK.........",
        "...KuK..........",
        "...KK...........",
    ])


def bow(frame):
    base = [
        "..........KKKK..",
        "........KKsmmK..",
        "......KKsmK.KK..",
        ".....KsmK...CK..",
        "....KsmK...C.K..",
        "...KsmK...C..K..",
        "...KmK...C...K..",
        "..KgK...C....K..",
        "..KgK..C.....K..",
        "..KmK.C......K..",
        "..KmKC......K...",
        "...KC......K....",
        "...K......K.....",
        "..KK.....K......",
        "..K.....K.......",
        "..KKKKKK........",
    ]
    return base


@item('constellation_bow')
def _():
    return spr([
        "..........KKK...",
        "........KKsSK...",
        ".......KsmK.W...",
        "......KsmK..c...",
        ".....KsnK..W....",
        ".....KnK...c....",
        "....KgK...W.....",
        "....KGgK..c.....",
        "....KgK..W......",
        "....KnK..c......",
        ".....KnK.W......",
        ".....KsnKc......",
        "......KsmW......",
        ".......KKK......",
        "................",
        "................",
    ])


def bow_pull(n):
    arrow = ['W', 'c', 'q'][n]
    rows = [
        "..........KKK...",
        "........KKsSK...",
        ".......KsmK.W...",
        "......KsmK...c..",
        ".....KsnK.....W.",
        ".....KnK.....c..",
        "....KgK.....W...",
        "....KGgKCCCWc...",
        "....KgK.....W...",
        "....KnK.....c...",
        ".....KnK...W....",
        ".....KsnK.c.....",
        "......KsmW......",
        ".......KKK......",
        "................",
        "................",
    ]
    offs = [0, 1, 2][n]
    rows = [list(r) for r in rows]
    # string pulled back further each frame
    for y in range(2, 13):
        for x in range(16):
            if rows[y][x] in 'Wc' and x > 8:
                rows[y][x] = '.'
    pull_x = 11 + offs
    pts = [(2, 12), (3, 12), (4, 12 + offs // 2), (5, pull_x - 1), (6, pull_x), (7, pull_x + 1 if pull_x + 1 < 16 else 15), (8, pull_x), (9, pull_x - 1), (10, 11), (11, 10), (12, 9)]
    for (y, x) in pts:
        if 0 <= x < 16:
            rows[y][x] = 'W' if y % 2 == 0 else 'c'
    # arrow of starlight
    for x in range(8, min(16, pull_x + 1)):
        rows[7][x] = 'C'
    rows[7][8] = 'W'
    rows[6][9] = 'q'; rows[8][9] = 'q'
    return spr([''.join(r) for r in rows])


for _n in range(3):
    ITEMS[f'constellation_bow_pulling_{_n}'] = (lambda n=_n: bow_pull(n))


@item('eclipse_greatsword')
def _():
    return spr([
        ".............KKK",
        "............KFfK",
        "...........KFEfK",
        "..........KFEEKK",
        ".........KFEEK..",
        "........KFEEK...",
        ".......KFEEK....",
        "......KFEEK.....",
        ".KK..KFEEK......",
        ".KgKKFEEK.......",
        "..KgKfEK........",
        "...KgKK.........",
        "..KuKgKK........",
        ".KuKKKhgK.......",
        "KfKK...KK.......",
        "KKK.............",
    ])


@item('gravity_gauntlet')
def _():
    return spr([
        "................",
        "......K.K.K.....",
        ".....KsKsKsK....",
        ".....KmKmKmKK...",
        ".....KmKmKmKsK..",
        "....KKmmmmmKmK..",
        "...KsKmmmmmmmK..",
        "...KmKnvVvnmnK..",
        "...KmnnpVpnnnK..",
        "....KnnnvnnnNK..",
        ".....KNnnnnNK...",
        ".....KgggggK....",
        ".....KNnnnNK....",
        ".....KNNNNNK....",
        "......KKKKK.....",
        "................",
    ])


@item('singularity_grenade')
def _():
    return spr([
        "................",
        "................",
        "........K.......",
        ".......KgK......",
        "......KKKKK.....",
        ".....KsmmnnK....",
        "....KsmvvvnnK...",
        "....KmvXXXvnK...",
        "....KmvXVXvnK...",
        "....KmvXXXvnK...",
        "....KnnvvvnNK...",
        ".....KnnnnNK....",
        "......KKKKK.....",
        "................",
        "................",
        "................",
    ])


@item('astral_compass')
def _():
    return spr([
        "................",
        "......KKKK......",
        "....KKhgghKK....",
        "...KhgZZZZghK...",
        "..KhZZZWZZZZhK..",
        "..KgZZZcZZZZgK..",
        ".KhZZZZcZZZZZhK.",
        ".KgZqZcGcZvZZgK.",
        ".KgZZZZvZZZZZgK.",
        ".KhZZZZvZZZZZhK.",
        "..KgZZZZZZZZgK..",
        "..KhZZZZZZZZhK..",
        "...KhgZZZZghK...",
        "....KKhgghKK....",
        "......KKKK......",
        "................",
    ])


@item('starmetal_pickaxe')
def _():
    return spr([
        "................",
        "...KKKKKKK......",
        "..KSssmmmnKK....",
        "...KKKKKmmnnK...",
        "......KKLKnnK...",
        ".....KLK.KNnK...",
        "....KLK...KnK...",
        "...KLK....KNK...",
        "..KLK......K....",
        ".KLK............",
        "KgK.............",
        "KK..............",
        "................",
        "................",
        "................",
        "................",
    ])


def armor_icon(kind, pal):
    A, B, C, D = pal  # light, mid, dark, accent
    leg = {'1': A, '2': B, '3': C, '4': D, 'K': L['K']}
    shapes = {
        'helmet': [
            "................",
            "................",
            "................",
            "....KKKKKKKK....",
            "...K11122223K...",
            "..K1124422233K..",
            "..K1222222233K..",
            "..K12KKKKKK23K..",
            "..K13K....K33K..",
            "..KK4K....K4KK..",
            "...KK......KK...",
            "................",
            "................",
            "................",
            "................",
            "................",
        ],
        'chestplate': [
            "................",
            "..KKKK....KKKK..",
            ".K1112KKKK2233K.",
            ".K1122444422233K",
            ".KK12224422223KK",
            "..KK122442223K..",
            "...K122222233K..",
            "...K112222333K..",
            "...K122222233K..",
            "...K124444433K..",
            "...K122222233K..",
            "...KKKKKKKKKKK..",
            "................",
            "................",
            "................",
            "................",
        ],
        'leggings': [
            "................",
            "................",
            "...KKKKKKKKKK...",
            "...K44444444K...",
            "...K11222233K...",
            "...K12222233K...",
            "...K1223K233K...",
            "...K123KK233K...",
            "...K122K K23K...",
            "...K122K.K23K...",
            "...K123K.K33K...",
            "...K444K.K44K...",
            "...KKKKK.KKKK...",
            "................",
            "................",
            "................",
        ],
        'boots': [
            "................",
            "................",
            "................",
            "................",
            "................",
            "...KKKK..KKKK...",
            "...K12K..K23K...",
            "...K12K..K23K...",
            "...K12K..K23K...",
            "..KK122KK223KK..",
            ".K11222KK2223K..",
            ".K4444KK44444K..",
            ".KKKKKK.KKKKKK..",
            "................",
            "................",
            "................",
        ],
    }
    rows = [r.replace(' ', '.') for r in shapes[kind]]
    return sprite(rows, leg)


STARMETAL_PAL = (L['S'], L['s'], L['m'], L['g'])
VOID_PAL = (L['v'], L['p'], L['P'], L['c'])
for _kind in ('helmet', 'chestplate', 'leggings', 'boots'):
    ITEMS[f'starmetal_{_kind}'] = (lambda k=_kind: armor_icon(k, STARMETAL_PAL))
    ITEMS[f'voidwalker_{_kind}'] = (lambda k=_kind: armor_icon(k, VOID_PAL))


@item('crown_of_astraeus')
def _():
    return spr([
        "................",
        "................",
        "................",
        ".K.....K.....K..",
        "KWK...KWK...KWK.",
        "KgK..KGgK...KgK.",
        "KgK..KgGK..KgKK.",
        "KgGK.KgGK.KGgK..",
        "KhgGKGgcGKGghK..",
        "KhggGgcCcgGghK..",
        "KHhgggqcqgghHK..",
        "KHhhgggqgghhHK..",
        ".KHHhhhhhhHHK...",
        "..KKKKKKKKKK....",
        "................",
        "................",
    ])


@item('nebula_wings')
def _():
    return spr([
        "................",
        ".KK..........KK.",
        "KvpK........KpvK",
        "KvpPK......KPpvK",
        "KvpPxK....KxPpvK",
        "KvpqPxK..KxPqpvK",
        "KvWpPxKKKKxPpWvK",
        "KvpPqPxKKxPqPpvK",
        "KvppPPxKKxPPppvK",
        ".KvpqPxKKxPqpvK.",
        ".KvpPPxK.KxPPpvK",
        "..KvpPxK.KxPpvK.",
        "..KvpPK...KPpvK.",
        "...KvK.....KvK..",
        "...KK.......KK..",
        "................",
    ])


def spawn_egg(base, spots, spot_col):
    rows = [
        "................",
        "......KKKK......",
        ".....K1111K.....",
        "....K112211K....",
        "...K11222211K...",
        "...K12222222K...",
        "..K1222222222K..",
        "..K1222222222K..",
        "..K1222222223K..",
        "..K1222222223K..",
        "..K1222222233K..",
        "...K12222233K...",
        "...K12222333K...",
        "....K122333K....",
        ".....KK33KK.....",
        "......KKKK......",
    ]
    leg = {'1': shade(base, 1.3), '2': base, '3': shade(base, 0.7), 'K': L['K']}
    c = sprite(rows, leg)
    r = rng(hash(str(base)) % 1000)
    for (x, y) in spots:
        c.set(x, y, spot_col)
        c.set(x + 1, y, shade(spot_col, 0.8))
    return c


EGGS = {
    'astral_wisp_spawn_egg': (hexc('#3fc6e0'), [(6, 5), (9, 9), (5, 11)], hexc('#effeff')),
    'void_stalker_spawn_egg': (hexc('#1a0d2e'), [(6, 6), (9, 6)], hexc('#f3e4ff')),
    'meteorite_crawler_spawn_egg': (hexc('#2d2634'), [(5, 7), (9, 5), (8, 10), (6, 12)], hexc('#ff7a1f')),
    'void_gazer_spawn_egg': (hexc('#5a2394'), [(7, 7)], hexc('#ffe9a3')),
    'astraeus_spawn_egg': (hexc('#161b44'), [(6, 5), (9, 8), (5, 10), (8, 12)], hexc('#f2c14e')),
}
for _name, (_b, _s, _c) in EGGS.items():
    ITEMS[_name] = (lambda b=_b, s=_s, c=_c: spawn_egg(b, s, c))


def main():
    for name, fn in ITEMS.items():
        fn().save(os.path.join(OUT, name + '.png'))
    print(f'wrote {len(ITEMS)} item textures')


if __name__ == '__main__':
    main()
