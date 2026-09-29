"""Item sprites (16x16) for Rimeheart, drawn as ASCII art with one shared frost palette."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'rimeheart', 'textures', 'item')

# Shared legend. Upper/lowercase pairs are light/dark variants.
L = {
    'K': hexc('#0a1119'), 'k': hexc('#1a2733'),
    # frostiron (pale steel blue)
    'S': hexc('#f2f9ff'), 's': hexc('#bcd8ec'), 'm': hexc('#86aecb'), 'n': hexc('#56809f'), 'N': hexc('#304c64'),
    # silver-ice accents
    'G': hexc('#e9fbff'), 'g': hexc('#a8e6fa'), 'h': hexc('#5fb6d8'), 'H': hexc('#2e6f8f'),
    # rime crystal
    'C': hexc('#f4fdff'), 'c': hexc('#b8eefc'), 'q': hexc('#6fcff0'), 'Q': hexc('#2f93c2'), 'w': hexc('#154a66'),
    # wraith (spectral teal)
    'V': hexc('#e2fff9'), 'v': hexc('#9ff0e0'), 'p': hexc('#4fc4b4'), 'P': hexc('#23847e'), 'x': hexc('#10474a'), 'X': hexc('#062224'),
    # hearth embers
    'R': hexc('#fff1c9'), 'r': hexc('#ffc56b'), 'o': hexc('#ff7a1f'), 'O': hexc('#b4380c'), 'e': hexc('#5a1606'),
    # rimestone
    'a': hexc('#8aa1b5'), 'b': hexc('#6a8196'), 'd': hexc('#4f6478'), 'D': hexc('#34414f'),
    # wood / leather
    'l': hexc('#8a5a34'), 'L': hexc('#5a3820'), 'u': hexc('#3a2414'),
    # glacier blue
    'y': hexc('#3f7fb0'), 'Y': hexc('#2b5f8a'), 'z': hexc('#1d4466'), 'Z': hexc('#122c45'),
    # white / misc
    'W': hexc('#ffffff'), 'i': hexc('#dde8f0'), 'I': hexc('#8a9aa8'),
    # winter core
    'E': hexc('#0b1d2c'), 'f': hexc('#9fe6ff'), 'F': hexc('#e6f9ff'),
}

SPRITES = {
 "raw_frostiron": [
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
  "................"
 ],
 "frostiron_ingot": [
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
  "................"
 ],
 "frostiron_nugget": [
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
  "................"
 ],
 "rime_shard": [
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
  "................"
 ],
 "wraith_essence": [
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
  "................"
 ],
 "sovereign_core": [
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
  "................"
 ],
 "frostbite_blade": [
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
  ".KKK............"
 ],
 "glacier_maul": [
  "....KKKKK.......",
  "..KKaqCcaKK.....",
  ".KbaqCCccabK....",
  ".KbaqcCccqabK...",
  "KdbaqqccqabdK...",
  "KdbbaqqqabbdK...",
  "KDdbbaqabbddK...",
  ".KDdbbabbddKK...",
  "..KDddbddDKLK...",
  "...KKDDDKKLK....",
  "......KKKLK.....",
  ".......KLK......",
  "......KLK.......",
  ".....KgK........",
  "....KLK.........",
  "....KK.........."
 ],
 "winterfang": [
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
  "KKK............."
 ],
 "frostiron_pickaxe": [
  "................",
  "....KKKKKK......",
  "..KKSSsmmnKK....",
  ".KSsmKKKKmnnK...",
  ".KsK....KLKnnK..",
  ".KK....KLK.KnK..",
  "......KLK..KnK..",
  ".....KLK....KNK.",
  "....KLK.....KNK.",
  "...KLK.......K..",
  "..KLK...........",
  ".KgK............",
  "KLK.............",
  "KK..............",
  "................",
  "................"
 ],
 "frost_charge": [
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
  "................"
 ],
 "wardens_journal": [
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
  "................"
 ],
 "rimebow": [
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
  "................"
 ],
 "frostiron_sword": [
  "................",
  ".............KK.",
  "............KSK.",
  "...........KSsK.",
  "..........KSsK..",
  ".........KSsK...",
  "........KSsK....",
  ".......KSsK.....",
  "......KSsK......",
  "..KK.KSsK.......",
  "..KmKSsK........",
  "...KmsK.........",
  "...KLKmK........",
  "..KLKKKmK.......",
  ".KuKK..KK.......",
  ".KKK............"
 ],
 "frostiron_axe": [
  "................",
  "......KKK.......",
  ".....KSSsKK.....",
  "....KSSsmmnK....",
  "....KSssmnNK....",
  ".....KsmKLKK....",
  "......KKLK......",
  ".......KLK......",
  "......KLK.......",
  ".....KLK........",
  "....KLK.........",
  "...KLK..........",
  "..KuK...........",
  "..KK............",
  "................",
  "................"
 ],
 "frostiron_shovel": [
  "................",
  "...........KKK..",
  "..........KSSsK.",
  ".........KSSsmK.",
  ".........KSsmnK.",
  "..........KmnK..",
  ".........KLKK...",
  "........KLK.....",
  ".......KLK......",
  "......KLK.......",
  ".....KLK........",
  "....KLK.........",
  "...KuK..........",
  "...KK...........",
  "................",
  "................"
 ],
 "blizzard_staff": [
  "..........K.K...",
  "...........C....",
  "........KKcCcKK.",
  ".........KcWcK..",
  "........KcWCWcK.",
  ".........KcWcK..",
  "........KKsCsKK.",
  "........KmKCKmK.",
  ".......KLKKmK...",
  "......KLK.......",
  ".....KLK........",
  "....KLK.........",
  "...KmK..........",
  "..KLK...........",
  ".KuK............",
  ".KK............."
 ],
 "winter_horn": [
  "................",
  "................",
  ".KK.............",
  "KiiK............",
  "KiWiK...........",
  ".KiiiKK.........",
  "..KiiiiKK.......",
  "...KgiiiiKKK....",
  "....KKgiiiiiKK..",
  "......KKggiiiiK.",
  "........KKgisiK.",
  "..........KssmK.",
  "..........KmsnK.",
  "...........KKK..",
  "................",
  "................"
 ],
 "hearthfire_stew": [
  "................",
  "................",
  "......r..o......",
  ".....o..r.......",
  "......r..o......",
  "...KKKKKKKKKK...",
  "..KOoorRroooOK..",
  "..KlOorRrooOlK..",
  "..KllOOOOOOllK..",
  "...KlllllllllK..",
  "...KLlllllllLK..",
  "....KLllllllK...",
  ".....KLLLLLK....",
  "......KKKKK.....",
  "................",
  "................"
 ],
 "glacial_heart": [
  "................",
  "................",
  "...KKK...KKK....",
  "..KCcqK.KcqQK...",
  ".KCWcqqKcqqQwK..",
  ".KCccqqqqqqQwK..",
  ".KcccqqqqqQQwK..",
  ".KccqqqqqqQQwK..",
  "..KcqqqqqQQwK...",
  "...KcqqqqQwK....",
  "....KcqqQwK.....",
  ".....KqQwK......",
  "......KwK.......",
  ".......K........",
  "................",
  "................"
 ]
}

def spr(rows):
    return sprite(rows, L)


ITEMS = {name: (lambda rows=rows: sprite(rows, L)) for name, rows in SPRITES.items()}


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


for _n in range(3):
    ITEMS[f'rimebow_pulling_{_n}'] = (lambda n=_n: bow_pull(n))

FROSTIRON_PAL = (L['S'], L['s'], L['m'], L['q'])
WRAITH_PAL = (L['v'], L['p'], L['P'], L['c'])
for _kind in ('helmet', 'chestplate', 'leggings', 'boots'):
    ITEMS[f'frostiron_{_kind}'] = (lambda k=_kind: armor_icon(k, FROSTIRON_PAL))
for _name, _kind in (('hood', 'helmet'), ('robe', 'chestplate'), ('leggings', 'leggings'), ('boots', 'boots')):
    ITEMS[f'wraithweave_{_name}'] = (lambda k=_kind: armor_icon(k, WRAITH_PAL))

EGGS = {
    'frost_wraith_spawn_egg': (hexc('#16324a'), [(6, 6), (9, 6)], hexc('#9fe6ff')),
    'shardling_spawn_egg': (hexc('#4aa3cf'), [(5, 7), (9, 5), (8, 10), (6, 12)], hexc('#f4fdff')),
    'frost_sovereign_spawn_egg': (hexc('#274466'), [(7, 5), (5, 9), (9, 10)], hexc('#d8f6ff')),
}
for _name, (_b, _s, _c) in EGGS.items():
    ITEMS[_name] = (lambda b=_b, s=_s, c=_c: spawn_egg(b, s, c))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in ITEMS.items():
        fn().save(os.path.join(OUT, name + '.png'))
    print(f'wrote {len(ITEMS)} item textures')


if __name__ == '__main__':
    main()
