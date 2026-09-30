"""Gear tiers: five metals of the old kingdom, each with its own signature weapon, tools, armour and set bonus.

Tier     where it comes from                         signature weapon     full set
------   -----------------------------------------   ------------------   -------------------------------------------
Tidebronze  copper, prismarine and lumenite dust      Tidebronze Gladius   conduit power and dolphin's grace in water
Runesilver  iron, lapis and luminous dust             Runesilver Rapier    magic hurts 40% less
Gravegold   gold, bone and gloam essence              Gravegold Khopesh    the undead hurt you 30% less
Duskiron    ore mined from the Gloaming's gloamstone  Duskiron Glaive      speed and strength in darkness; sight in the Gloaming
Dawnsteel   oathsteel quenched in an Everflame ember  Dawnsteel Greatsword regeneration and fire resistance under the sun;
                                                                           immune to Gloamrot

From the table below this module writes the item registrations (a generated region of ModItems.java), icons,
worn-armour textures and equipment assets, and hands recipes, tags, names and descriptions to data.py and
lang.py. The abilities themselves live in com.oathbound.event.GearEvents.

Run from the repository root:  python3 -m tools.oath.gear
"""
import json
import os

import numpy as np

from . import itemart as I
from . import armor as AR
from . import data as D
from .paint import Img, Ramp
from .model import face_regions

ROOT = I.__dict__.get('ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')
MODITEMS = os.path.join(ROOT, 'src/main/java/com/oathbound/registry/ModItems.java')
N = 16

R = {
    'tidebronze': Ramp('#2a1a0c', '#5a3a18', '#8a5c2a', '#b8843e', '#d8b068', '#f0dca0'),
    'runesilver': Ramp('#2a3350', '#46557a', '#6a7ca4', '#98abcc', '#c8d6ec', '#f2f6ff'),
    'gravegold': Ramp('#1a140a', '#3a2a10', '#6a4c16', '#a07a24', '#d4a83c', '#f6dc84'),
    'duskiron': Ramp('#1c1828', '#2e2840', '#443c5e', '#5e5480', '#8478a8', '#b4a8dc'),
    'dawnsteel': Ramp('#7a4208', '#b8741c', '#e8a434', '#ffcc55', '#ffe89a', '#fff8e0'),
}

# name, English, material incorrect-for tag, durability, speed, damage bonus, enchantability,
# armour: durability multiplier, (boots, leggings, chest, helmet, body), enchantability, equip sound, toughness, knockback resistance
TIERS = [
    dict(id='tidebronze', en='Tidebronze', incorrect='INCORRECT_FOR_IRON_TOOL', dur=600, speed=7.0, dmg=2.0, ench=18,
         armor=(18, (2, 5, 6, 2, 7), 16, 'ARMOR_EQUIP_CHAIN', 0.0, 0.0), rarity='COMMON', handle='wood', accent='teal',
         weapon=('tidebronze_gladius', 'Tidebronze Gladius', 3.0, -2.0, None),
         source='tidebronze_blend', source_en='Tidebronze Blend'),
    dict(id='runesilver', en='Runesilver', incorrect='INCORRECT_FOR_IRON_TOOL', dur=820, speed=7.5, dmg=2.5, ench=28,
         armor=(22, (2, 5, 6, 2, 7), 28, 'ARMOR_EQUIP_CHAIN', 0.5, 0.0), rarity='UNCOMMON', handle='gloamwood', accent='arcane',
         weapon=('runesilver_rapier', 'Runesilver Rapier', 2.0, -1.6, 0.75),
         source='runesilver_blend', source_en='Runesilver Blend'),
    dict(id='gravegold', en='Gravegold', incorrect='INCORRECT_FOR_DIAMOND_TOOL', dur=1150, speed=8.0, dmg=3.0, ench=22,
         armor=(30, (3, 6, 7, 3, 9), 22, 'ARMOR_EQUIP_GOLD', 1.5, 0.0), rarity='UNCOMMON', handle='bone', accent='teal',
         weapon=('gravegold_khopesh', 'Gravegold Khopesh', 4.0, -2.6, None),
         source='gravegold_blend', source_en='Gravegold Blend'),
    dict(id='duskiron', en='Duskiron', incorrect='INCORRECT_FOR_DIAMOND_TOOL', dur=1800, speed=8.5, dmg=3.5, ench=14,
         armor=(35, (3, 6, 8, 3, 11), 12, 'ARMOR_EQUIP_NETHERITE', 2.5, 0.05), rarity='RARE', handle='gloamwood', accent='violet',
         weapon=('duskiron_glaive', 'Duskiron Glaive', 5.5, -3.0, 1.5),
         source='raw_duskiron', source_en='Raw Duskiron'),
    dict(id='dawnsteel', en='Dawnsteel', incorrect='INCORRECT_FOR_NETHERITE_TOOL', dur=2600, speed=9.5, dmg=4.5, ench=20,
         armor=(40, (3, 6, 8, 3, 11), 20, 'ARMOR_EQUIP_DIAMOND', 3.0, 0.1), rarity='EPIC', handle='gold', accent='dawn',
         weapon=('dawnsteel_greatsword', 'Dawnsteel Greatsword', 6.0, -3.0, 0.5),
         source=None, source_en=None),
]
PIECES = [('helmet', 'HELMET', 'Helm'), ('chestplate', 'CHESTPLATE', 'Cuirass'), ('leggings', 'LEGGINGS', 'Greaves'),
          ('boots', 'BOOTS', 'Sabatons')]
TOOLS = [('pickaxe', 'Pickaxe'), ('axe', 'Axe'), ('shovel', 'Shovel'), ('hoe', 'Hoe')]

SET_BONUS = {
    'tidebronze': 'Full set: conduit power and dolphin\'s grace while in water.',
    'runesilver': 'Full set: spells and magic hurt you 40% less.',
    'gravegold': 'Full set: the undead hurt you 30% less, and you strike them harder.',
    'duskiron': 'Full set: swift and strong in darkness; clear sight in the Gloaming.',
    'dawnsteel': 'Full set: regeneration and fire resistance under the open sun; immune to Gloamrot.',
}
WEAPON_DESC = {
    'tidebronze_gladius': ['A short sea-blade, green at the edges where the salt has kissed it.',
                           'Strikes half again as hard while you stand in water or rain.'],
    'runesilver_rapier': ['Its fuller is a line of runes that wake when it moves.',
                          'Every thrust carries a glyph: +4 magic damage. Reaches a little further.'],
    'gravegold_khopesh': ['The barrow kings were buried with these, and did not rest easy.',
                          'Deals 60% more damage to the undead.'],
    'duskiron_glaive': ['Forged of the Gloaming\'s iron; it drinks the light around it.',
                        'Long reach. Deals 30% more damage in darkness.'],
    'dawnsteel_greatsword': ['Quenched in the Everflame, it is warm to the touch and never dims.',
                             'Burns the Gloam and the undead for half again as much, and sets them alight.'],
}
MATERIAL_DESC = {
    'tidebronze_blend': 'Copper, sea-glass and lumenite, ready for the furnace.',
    'runesilver_blend': 'Iron ground with lapis and light, ready for the furnace.',
    'gravegold_blend': 'Gold, bone and a breath of the Gloam, ready for the furnace.',
    'raw_duskiron': 'Dark iron from the Gloaming. Smelt it.',
    'tidebronze_ingot': 'Bronze that remembers the tide.',
    'runesilver_ingot': 'Silver that hums with written light.',
    'gravegold_ingot': 'Gold from the barrows. It is cold even in the sun.',
    'duskiron_ingot': 'Iron that drinks the light around it.',
    'dawnsteel_ingot': 'Oathsteel reborn in the Everflame.',
}


def items_of(t):
    tid = t['id']
    out = []
    if t['source']:
        out.append(t['source'])
    out.append(f'{tid}_ingot')
    out.append(t['weapon'][0])
    out += [f'{tid}_{k}' for k, _ in TOOLS]
    out += [f'{tid}_{p}' for p, _, _ in PIECES]
    return out


NAMES = {}
DESC = {}
for _t in TIERS:
    if _t['source']:
        NAMES[_t['source']] = _t['source_en']
    NAMES[f'{_t["id"]}_ingot'] = f'{_t["en"]} Ingot'
    NAMES[_t['weapon'][0]] = _t['weapon'][1]
    for _k, _en in TOOLS:
        NAMES[f'{_t["id"]}_{_k}'] = f'{_t["en"]} {_en}'
    for _p, _, _en in PIECES:
        NAMES[f'{_t["id"]}_{_p}'] = f'{_t["en"]} {_en}'
        DESC[f'{_t["id"]}_{_p}'] = [SET_BONUS[_t['id']]]
    DESC[_t['weapon'][0]] = WEAPON_DESC[_t['weapon'][0]]
NAMES['oathsteel_hoe'] = 'Oathsteel Hoe'
for _k, _v in MATERIAL_DESC.items():
    DESC[_k] = [_v]


# ====================================================================== Java
BEGIN = '    // ------------------------------------------------------------------ gear tiers (generated by tools/oath/gear.py)\n'
END = '    // ------------------------------------------------------------------ end of gear tiers\n'


def java():
    L = [BEGIN]
    L.append('    public static final RegistryObject<Item> OATHSTEEL_HOE = reg("oathsteel_hoe", p -> new net.minecraft.world.item.HoeItem(OATHSTEEL_TOOL, -2.0f, -1.0f, p), Item.Properties::new);\n')
    for t in TIERS:
        tid, T = t['id'], t['id'].upper()
        fire = '.fireResistant()' if tid == 'dawnsteel' else ''
        rar = f'.rarity(Rarity.{t["rarity"]})'
        a = t['armor']
        L.append(f'    public static final net.minecraft.tags.TagKey<Item> {T}_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, '
                 f'Identifier.fromNamespaceAndPath(Oathbound.MODID, "{tid}_repair"));\n')
        L.append(f'    public static final ToolMaterial {T}_TOOL = new ToolMaterial(BlockTags.{t["incorrect"]}, {t["dur"]}, {t["speed"]}f, {t["dmg"]}f, {t["ench"]}, {T}_REPAIR);\n')
        L.append(f'    public static final ResourceKey<EquipmentAsset> {T}_ASSET = asset("{tid}");\n')
        b, l, c, h, body = a[1]
        L.append(f'    public static final ArmorMaterial {T}_ARMOR = new ArmorMaterial({a[0]}, Map.of(ArmorType.BOOTS, {b}, ArmorType.LEGGINGS, {l}, ArmorType.CHESTPLATE, {c}, '
                 f'ArmorType.HELMET, {h}, ArmorType.BODY, {body}), {a[2]}, SoundEvents.{a[3]}, {a[4]}f, {a[5]}f, {T}_REPAIR, {T}_ASSET);\n')
        if t['source']:
            L.append(f'    public static final RegistryObject<Item> {t["source"].upper()} = reg("{t["source"]}", p -> new InscribedItem(p, 1, false), () -> new Item.Properties(){fire});\n')
        L.append(f'    public static final RegistryObject<Item> {T}_INGOT = reg("{tid}_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties(){fire}{rar});\n')
        wid, _, wd, ws, reach = t['weapon']
        props = f'new Item.Properties().sword({T}_TOOL, {wd}f, {ws}f)'
        if reach:
            props += f'.attributes(weapon({wd + t["dmg"]}, {ws}, {reach}))'
        wr = {'COMMON': 'UNCOMMON', 'UNCOMMON': 'RARE', 'RARE': 'RARE', 'EPIC': 'EPIC'}[t['rarity']]
        L.append(f'    public static final RegistryObject<Item> {wid.upper()} = reg("{wid}", p -> new InscribedItem(p, 2, false), () -> {props}.rarity(Rarity.{wr}){fire});\n')
        hoe = {'tidebronze': (-2.0, -1.0), 'runesilver': (-2.0, -1.0), 'gravegold': (-3.0, 0.0), 'duskiron': (-3.0, 0.0), 'dawnsteel': (-4.0, 0.0)}[tid]
        L.append(f'    public static final RegistryObject<Item> {T}_PICKAXE = reg("{tid}_pickaxe", Item::new, () -> new Item.Properties().pickaxe({T}_TOOL, 1.0f, -2.8f){rar}{fire});\n')
        L.append(f'    public static final RegistryObject<Item> {T}_AXE = reg("{tid}_axe", p -> new AxeItem({T}_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties(){rar}{fire});\n')
        L.append(f'    public static final RegistryObject<Item> {T}_SHOVEL = reg("{tid}_shovel", p -> new ShovelItem({T}_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties(){rar}{fire});\n')
        L.append(f'    public static final RegistryObject<Item> {T}_HOE = reg("{tid}_hoe", p -> new net.minecraft.world.item.HoeItem({T}_TOOL, {hoe[0]}f, {hoe[1]}f, p), () -> new Item.Properties(){rar}{fire});\n')
        for p, TYPE, _ in PIECES:
            L.append(f'    public static final RegistryObject<Item> {T}_{p.upper()} = reg("{tid}_{p}", p -> new InscribedItem(p, 1, false), '
                     f'() -> new Item.Properties().humanoidArmor({T}_ARMOR, ArmorType.{TYPE}){rar}{fire});\n')
    L.append(END)
    region = ''.join(L)
    src = open(MODITEMS).read()
    if BEGIN in src:
        a = src.index(BEGIN)
        z = src.index(END) + len(END)
        src = src[:a] + region + src[z:]
    else:
        anchor = '    // ------------------------------------------------------------------ spawn eggs\n'
        src = src.replace(anchor, region + '\n' + anchor)
    open(MODITEMS, 'w').write(src)


# ====================================================================== icons
def ramp(name):
    return R.get(name) or I.M[name]


def glaive(head, haft, trim):
    """A long haft ending in a broad crescent blade with a back-spike."""
    im = Img(N, N)
    owner = np.full((N, N), None, dtype=object)
    I.shaft(im, owner, haft, -14, 4)
    I.paint_mask(im, owner, [
        "......555",
        "....55544",
        "...554443",
        "..55443..",
        ".5443t...",
        ".543t....",
        ".43t.....",
        "..t.3....",
        ".....3...",
    ], 7, 0, head, {'t': (trim, 4)})
    return I.outline(im, owner)


def weapon_icon(t):
    head = R[t['id']]
    handle = ramp(t['handle'])
    accent = ramp(t['accent'])
    wid = t['weapon'][0]
    if wid == 'tidebronze_gladius':
        return I.blade(tip=10, guard=-4, grip=-10, width=(13, 17), taper=4, blade_ramp=head, guard_ramp=accent, grip_ramp=I.M['leather'])
    if wid == 'runesilver_rapier':
        im = I.blade(tip=14, guard=-5, grip=-11, width=(15, 16), taper=2, guard_span=4, fuller=False, blade_ramp=head,
                     guard_ramp=I.M['silver'], grip_ramp=I.M['silk'], gem=I.shade(accent, 5))
        # a line of runes along the blade
        for p in range(-2, 12, 3):
            x = (p + 15) // 2 + 1
            y = x - p
            if 0 <= x < N and 0 <= y < N and im.px[y, x, 3] > 0:
                im.px[y, x] = I.shade(accent, 5)
        return im
    if wid == 'gravegold_khopesh':
        return I.blade(tip=12, guard=-4, grip=-11, width=(14, 17), taper=3, curve=-4.5, fuller=False, blade_ramp=head,
                       guard_ramp=I.M['bone'], grip_ramp=I.M['leather'], gem=I.shade(accent, 4))
    if wid == 'duskiron_glaive':
        return glaive(head, handle, accent)
    return I.blade(tip=15, guard=-3, grip=-11, width=(13, 18), taper=4, guard_span=5, blade_ramp=head, guard_ramp=I.M['gold'],
                   grip_ramp=I.M['leather'], gem=I.shade(I.M['white'], 5))


RAW = [
    "................",
    "................",
    "................",
    ".......KKK......",
    ".....KK544K.....",
    "....K5544432K...",
    "...K554443322K..",
    "...K54443K322K..",
    "..K5443K43221K..",
    "..K443K443321K..",
    "..K4433332211K..",
    "...K33322211K...",
    "....KK2211KK....",
    "......KKKK......",
    "................",
    "................",
]


def icons():
    out = {}
    out['oathsteel_hoe'] = I.tool(I.HOE, I.M['oathsteel'], I.M['wood'])
    for t in TIERS:
        tid = t['id']
        head, handle, accent = R[tid], ramp(t['handle']), ramp(t['accent'])
        if t['source'] == 'raw_duskiron':
            out['raw_duskiron'] = I.sprite(RAW, head)
        elif t['source']:
            mixed = Ramp(*['#%02x%02x%02x' % tuple(int(v * 255) for v in c[:3]) for c in (head.cols[:4] + accent.cols[3:5])])
            out[t['source']] = I.sprite(I.DUST, mixed)
        out[f'{tid}_ingot'] = I.sprite(I.INGOT, head)
        out[t['weapon'][0]] = weapon_icon(t)
        for k, mask in (('pickaxe', I.PICKAXE), ('axe', I.AXE), ('shovel', I.SHOVEL), ('hoe', I.HOE)):
            out[f'{tid}_{k}'] = I.tool(mask, head, handle)
        for p, mask in (('helmet', I.HELMET), ('chestplate', I.CHESTPLATE), ('leggings', I.LEGGINGS), ('boots', I.BOOTS)):
            out[f'{tid}_{p}'] = I.armor(mask, head, accent)
    return out


# ====================================================================== worn armour
HELM_STYLES = {'tidebronze': 'crest', 'runesilver': 'hood', 'gravegold': 'crown', 'duskiron': 'horns', 'dawnsteel': 'halo'}
EMBLEMS = {
    'tidebronze': [".#.#.", "#####", ".#.#."],
    'runesilver': ["#.#", ".#.", "#.#", ".#."],
    'gravegold': ["###", "#.#", "###"],
    'duskiron': ["#...#", ".#.#.", "..#.."],
    'dawnsteel': ["..#..", "#####", "..#..", ".#.#."],
}


def worn(t):
    tid = t['id']
    body = R[tid]
    trim = ramp(t['accent'])
    seed = sum(ord(c) for c in tid)
    s = AR.Style(body, trim, trim, seam=0 if tid == 'runesilver' else 4, cloth=(tid == 'runesilver'))
    a = Img(64, 32)
    AR.paint_box(a, AR.HEAD, s, part='head', seed=seed % 97)
    fx, fy, fw, fh = face_regions(*AR.HEAD)['front']
    style = HELM_STYLES[tid]
    if style == 'hood':
        for y in range(2, 8):
            for x in range(1, 7):
                a.px[fy + y, fx + x] = np.zeros(4)
    else:
        for x in range(1, 7):
            a.px[fy + 4, fx + x] = np.array([0.03, 0.03, 0.05, 1.0])
        a.px[fy + 5, fx + 3] = np.array([0.03, 0.03, 0.05, 1.0])
        a.px[fy + 5, fx + 4] = np.array([0.03, 0.03, 0.05, 1.0])
    for face in ('front', 'back', 'left', 'right'):
        AR.trim_row(a, AR.HEAD, 0, s, (face,))
    tx, ty, tw, th = face_regions(*AR.HEAD)['top']
    if style == 'crest':
        for y in range(th):
            a.px[ty + y, tx + 3] = trim.smooth(0.85)
            a.px[ty + y, tx + 4] = trim.smooth(0.6)
    # the hat layer carries the helm's silhouette pieces
    hx, hy, hw, hh = face_regions(32, 0, 8, 8, 8)['front']
    if style == 'crown':
        for face in ('front', 'back', 'left', 'right'):
            ox, oy, ow, oh = face_regions(32, 0, 8, 8, 8)[face]
            for x in range(ow):
                if x % 3 == 1:
                    a.px[oy, ox + x] = body.smooth(0.9)
                a.px[oy + 1, ox + x] = body.smooth(0.7)
    elif style == 'horns':
        for face in ('left', 'right'):
            ox, oy, ow, oh = face_regions(32, 0, 8, 8, 8)[face]
            for k in range(3):
                a.px[oy + 1 + k, ox + 2 + k] = trim.smooth(0.5 + k * 0.15)
    elif style == 'halo':
        for face in ('front', 'back', 'left', 'right'):
            ox, oy, ow, oh = face_regions(32, 0, 8, 8, 8)[face]
            for x in range(ow):
                a.px[oy, ox + x] = trim.smooth(0.9 if x % 2 else 0.7)
    AR.paint_box(a, AR.BODY, s, seed=seed % 89 + 3)
    AR.trim_row(a, AR.BODY, 0, s)
    AR.trim_row(a, AR.BODY, 11, s)
    AR.emblem(a, AR.BODY, s, EMBLEMS[tid], 2)
    AR.paint_box(a, AR.ARM, s, seed=seed % 83 + 5)
    AR.trim_row(a, AR.ARM, 0, s)
    AR.trim_row(a, AR.ARM, 11, s)
    AR.paint_box(a, AR.LEG, s, rows=(8, 12), seed=seed % 79 + 7)
    AR.trim_row(a, AR.LEG, 8, s)
    b = Img(64, 32)
    AR.paint_box(b, AR.BODY, s, rows=(8, 12), seed=seed % 73 + 9)
    AR.trim_row(b, AR.BODY, 8, s)
    AR.paint_box(b, AR.LEG, s, rows=(0, 10), seed=seed % 71 + 11)
    AR.trim_row(b, AR.LEG, 4, s)
    return a, b


def write_json(rel, obj):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def assets():
    for name, im in icons().items():
        im.save(os.path.join(ASSETS, 'textures/item', name + '.png'))
        write_json(f'models/item/{name}.json', {'parent': 'minecraft:item/handheld' if any(
            name.endswith(s) for s in ('_pickaxe', '_axe', '_shovel', '_hoe', '_gladius', '_rapier', '_khopesh', '_glaive', '_greatsword'))
            else 'minecraft:item/generated', 'textures': {'layer0': f'oathbound:item/{name}'}})
        write_json(f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': f'oathbound:item/{name}'}})
    eq = os.path.join(ASSETS, 'textures/entity/equipment')
    for t in TIERS:
        a, b = worn(t)
        a.save(os.path.join(eq, f'humanoid/{t["id"]}.png'))
        b.save(os.path.join(eq, f'humanoid_leggings/{t["id"]}.png'))
        write_json(f'equipment/{t["id"]}.json', {'layers': {'humanoid': [{'texture': f'oathbound:{t["id"]}'}],
                                                           'humanoid_leggings': [{'texture': f'oathbound:{t["id"]}'}]}})


# ====================================================================== data (called by data.py)
def recipes():
    E = 'equipment'
    D.shaped('oathsteel_hoe', ['II', ' S', ' S'], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'oathsteel_hoe', category=E)
    D.shapeless('tidebronze_blend', ['minecraft:copper_ingot', 'minecraft:copper_ingot', 'minecraft:prismarine_shard', 'lumenite_dust'], 'tidebronze_blend')
    D.shapeless('runesilver_blend', ['minecraft:iron_ingot', 'minecraft:lapis_lazuli', 'minecraft:lapis_lazuli', 'luminous_dust'], 'runesilver_blend')
    D.shapeless('gravegold_blend', ['minecraft:gold_ingot', 'minecraft:bone', 'gloam_essence'], 'gravegold_blend')
    for src, ingot in (('tidebronze_blend', 'tidebronze_ingot'), ('runesilver_blend', 'runesilver_ingot'),
                       ('gravegold_blend', 'gravegold_ingot'), ('raw_duskiron', 'duskiron_ingot')):
        D.cooking(ingot, 'smelting', src, ingot, 0.8, 200)
        D.cooking(f'{ingot}_blasting', 'blasting', src, ingot, 0.8, 100)
    D.cooking('duskiron_ingot_from_ore', 'smelting', 'duskiron_ore', 'duskiron_ingot', 1.0, 200)
    D.shaped('dawnsteel_ingot', ['III', 'IEI', 'III'], {'I': 'oathsteel_ingot', 'E': 'everflame_ember'}, 'dawnsteel_ingot', 8)
    for t in TIERS:
        tid = t['id']
        ing = f'{tid}_ingot'
        k = {'I': ing, 'S': 'minecraft:stick'}
        D.shaped(f'{tid}_pickaxe', ['III', ' S ', ' S '], k, f'{tid}_pickaxe', category=E)
        D.shaped(f'{tid}_axe', ['II', 'IS', ' S'], k, f'{tid}_axe', category=E)
        D.shaped(f'{tid}_shovel', ['I', 'S', 'S'], k, f'{tid}_shovel', category=E)
        D.shaped(f'{tid}_hoe', ['II', ' S', ' S'], k, f'{tid}_hoe', category=E)
        D.shaped(f'{tid}_helmet', ['III', 'I I'], {'I': ing}, f'{tid}_helmet', category=E)
        D.shaped(f'{tid}_chestplate', ['I I', 'III', 'III'], {'I': ing}, f'{tid}_chestplate', category=E)
        D.shaped(f'{tid}_leggings', ['III', 'I I', 'I I'], {'I': ing}, f'{tid}_leggings', category=E)
        D.shaped(f'{tid}_boots', ['I I', 'I I'], {'I': ing}, f'{tid}_boots', category=E)
        wid = t['weapon'][0]
        pattern = {'tidebronze_gladius': [' I', 'S '], 'runesilver_rapier': ['  I', ' I ', 'G  '],
                   'gravegold_khopesh': [' II', ' I ', 'S  '], 'duskiron_glaive': [' II', ' SI', 'S  '],
                   'dawnsteel_greatsword': [' I ', 'III', ' S ']}[wid]
        key = {'I': ing, 'S': 'minecraft:stick', 'G': 'minecraft:gold_ingot'}
        key = {c: v for c, v in key.items() if any(c in row for row in pattern)}
        D.shaped(wid, pattern, key, wid, category=E)
        D.shaped(f'{tid}_block', ['III', 'III', 'III'], {'I': ing}, f'{tid}_block', category='building')
        D.shapeless(f'{ing}_from_block', [f'{tid}_block'], ing, 9)


def tags():
    swords = [t['weapon'][0] for t in TIERS]
    by = lambda suffix: [f'{t["id"]}_{suffix}' for t in TIERS]
    T = {
        'item/swords': swords, 'item/pickaxes': by('pickaxe'), 'item/axes': by('axe'), 'item/shovels': by('shovel'),
        'item/hoes': by('hoe') + ['oathsteel_hoe'],
        'item/head_armor': by('helmet'), 'item/chest_armor': by('chestplate'), 'item/leg_armor': by('leggings'),
        'item/foot_armor': by('boots'),
        'item/trimmable_armor': by('helmet') + by('chestplate') + by('leggings') + by('boots'),
        'item/beacon_payment_items': by('ingot'),
        'block/beacon_base_blocks': by('block'),
    }
    for path, values in T.items():
        D.tag(path, values, 'minecraft')
    for t in TIERS:
        D.tag(f'item/{t["id"]}_repair', [f'{t["id"]}_ingot'])
        D.tag(f'item/ingots/{t["id"]}', [f'{t["id"]}_ingot'], 'c')
        D.tag('item/ingots', [f'{t["id"]}_ingot'], 'c')
        D.tag(f'item/storage_blocks/{t["id"]}', [f'{t["id"]}_block'], 'c')
        D.tag(f'block/storage_blocks/{t["id"]}', [f'{t["id"]}_block'], 'c')
    D.tag('item/raw_materials', ['raw_duskiron'], 'c')
    D.tag('item/raw_materials/duskiron', ['raw_duskiron'], 'c')
    D.tag('item/ores/duskiron', ['duskiron_ore'], 'c')
    D.tag('block/ores/duskiron', ['duskiron_ore'], 'c')
    dawn = [n for n in items_of(TIERS[-1]) if n != 'dawnsteel_ingot']
    D.tag('item/oath_forged', dawn)
    D.tag('item/sunmended', dawn)


def worldgen():
    """Duskiron seams in the Gloaming's gloamstone (the Gloaming lists the placed feature)."""
    D.write('worldgen/configured_feature/ore_duskiron.json', {'type': 'minecraft:ore', 'config': {
        'size': 6, 'discard_chance_on_air_exposure': 0.3,
        'targets': [{'target': {'predicate_type': 'minecraft:block_match', 'block': 'oathbound:gloamstone'},
                     'state': {'Name': 'oathbound:duskiron_ore'}}]}})
    D.write('worldgen/placed_feature/ore_duskiron.json', {'feature': 'oathbound:ore_duskiron', 'placement': [
        {'type': 'minecraft:count', 'count': 10}, {'type': 'minecraft:in_square'},
        {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': 10},
                                                      'max_inclusive': {'absolute': 120}}},
        {'type': 'minecraft:biome'}]})


def generate():
    java()
    assets()
    print(sum(len(items_of(t)) for t in TIERS) + 1, 'gear items written')


if __name__ == '__main__':
    generate()
