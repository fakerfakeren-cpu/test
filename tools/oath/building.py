"""Building families: every decorative block set of Oathbound, generated from one table.

Each entry names a block, its shape (cube, stairs, slab, wall, door, lantern, flower...), the family whose
material it shares and its textures. From that table this module writes:

* the block registrations (the generated region of ModBlocks.java),
* textures, block models, blockstates and item definitions,
* loot tables, crafting and stonecutting recipes, and the flower worldgen,

and it hands its tags (TAGS) and English names (NAMES) to data.py and lang.py, which own those files.

Run from the repository root:  python3 -m tools.oath.building
"""
import json
import os
import re

from . import blockart as A
from . import blocks as K
from . import data as D

ROOT = K.ROOT
MODBLOCKS = os.path.join(ROOT, 'src/main/java/com/oathbound/registry/ModBlocks.java')
TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
ref = K.ref


def S(name, kind, fam, tex=None, **kw):
    return dict(name=name, kind=kind, fam=fam, tex=tex or name, **kw)


def stone_set(fam, stone, base_field, stairs=True, slab=True, wall=True):
    """Stairs, slab and wall cut from one stone."""
    out = []
    stem = re.sub(r'_bricks$', '_brick', stone)
    stem = re.sub(r'_tiles$', '_tile', stem)
    if stairs:
        out.append(S(f'{stem}_stairs', 'stairs', fam, stone, base=base_field, cut_from=stone))
    if slab:
        out.append(S(f'{stem}_slab', 'slab', fam, stone, double=stone, cut_from=stone))
    if wall:
        out.append(S(f'{stem}_wall', 'wall', fam, stone, cut_from=stone))
    return out


# ====================================================================== the table
TABLE = [
    # -------------------------------------------------------------- wardstone: the Lanternguard's pale masonry
    *stone_set('wardstone', 'wardstone', 'WARDSTONE'),
    S('wardstone_brick_wall', 'wall', 'wardstone', 'wardstone_bricks', cut_from='wardstone_bricks'),
    *stone_set('wardstone', 'mossy_wardstone_bricks', 'MOSSY_WARDSTONE_BRICKS'),
    S('polished_wardstone', 'cube', 'wardstone', paint=A.polished_wardstone, cut_from='wardstone'),
    *stone_set('wardstone', 'polished_wardstone', 'POLISHED_WARDSTONE', wall=False),
    S('wardstone_tiles', 'cube', 'wardstone', paint=A.wardstone_tiles, cut_from='polished_wardstone'),
    S('wardstone_button', 'button', 'wardstone', 'polished_wardstone', set='BlockSetType.STONE', ticks=20),
    S('wardstone_pressure_plate', 'plate', 'wardstone', 'polished_wardstone', set='BlockSetType.STONE'),
    # -------------------------------------------------------------- gloamstone: the Gloaming's bedrock
    *stone_set('gloamstone', 'gloamstone', 'GLOAMSTONE'),
    *stone_set('gloamstone', 'gloamstone_bricks', 'GLOAMSTONE_BRICKS'),
    S('cracked_gloamstone_bricks', 'cube', 'gloamstone', paint=A.cracked_gloamstone_bricks),
    S('polished_gloamstone', 'cube', 'gloamstone', paint=A.polished_gloamstone, cut_from='gloamstone'),
    *stone_set('gloamstone', 'polished_gloamstone', 'POLISHED_GLOAMSTONE', wall=False),
    S('chiseled_gloamstone', 'cube', 'gloamstone', paint=A.chiseled_gloamstone, light=7, cut_from='gloamstone'),
    S('gloamstone_tiles', 'cube', 'gloamstone', paint=A.gloamstone_tiles, cut_from='polished_gloamstone'),
    # -------------------------------------------------------------- gloamwood: dusk-grown timber that will not burn
    S('gloamwood', 'wood', 'gloamwood', 'gloamwood_log', stripped='STRIPPED_GLOAMWOOD'),
    S('stripped_gloamwood_log', 'log', 'gloamwood', 'stripped_gloamwood_log', end='stripped_gloamwood_log_top',
      paint=A.stripped_gloamwood_side, paint_end=A.stripped_gloamwood_top),
    S('stripped_gloamwood', 'log', 'gloamwood', 'stripped_gloamwood_log', end='stripped_gloamwood_log'),
    S('gloamwood_stairs', 'stairs', 'gloamwood', 'gloamwood_planks', base='GLOAMWOOD_PLANKS'),
    S('gloamwood_slab', 'slab', 'gloamwood', 'gloamwood_planks', double='gloamwood_planks'),
    S('gloamwood_fence', 'fence', 'gloamwood', 'gloamwood_planks'),
    S('gloamwood_fence_gate', 'fence_gate', 'gloamwood', 'gloamwood_planks'),
    S('gloamwood_door', 'door', 'gloamwood'),
    S('gloamwood_trapdoor', 'trapdoor', 'gloamwood', paint=A.gloamwood_trapdoor),
    S('gloamwood_button', 'button', 'gloamwood', 'gloamwood_planks', set='GLOAMWOOD_SET', ticks=30),
    S('gloamwood_pressure_plate', 'plate', 'gloamwood', 'gloamwood_planks', set='GLOAMWOOD_SET'),
    S('gloamwood_leaves', 'leaves', 'gloamwood', paint=A.leaves),
    S('gloamwood_sapling', 'sapling', 'gloamwood', paint=A.sapling),
    # -------------------------------------------------------------- tidestone: the Drowned Chapel's sea-green marble
    S('tidestone', 'cube', 'tidestone', paint=A.tidestone),
    S('tidestone_bricks', 'cube', 'tidestone', paint=A.tidestone_bricks, cut_from='tidestone'),
    S('barnacled_tidestone_bricks', 'cube', 'tidestone', paint=A.barnacled_tidestone_bricks),
    S('chiseled_tidestone', 'cube', 'tidestone', paint=A.chiseled_tidestone, light=6, cut_from='tidestone'),
    *stone_set('tidestone', 'tidestone_bricks', 'TIDESTONE_BRICKS'),
    # -------------------------------------------------------------- barrowstone: grave-grey stone of the barrow kings
    S('barrowstone', 'cube', 'barrowstone', paint=A.barrowstone),
    S('barrowstone_bricks', 'cube', 'barrowstone', paint=A.barrowstone_bricks, cut_from='barrowstone'),
    S('bone_inlaid_barrowstone', 'cube', 'barrowstone', paint=A.bone_inlaid_barrowstone),
    *stone_set('barrowstone', 'barrowstone_bricks', 'BARROWSTONE_BRICKS'),
    # -------------------------------------------------------------- runestone: the Arcanist Spire's deep-blue stone
    S('runestone', 'cube', 'runestone', paint=A.runestone),
    S('runestone_bricks', 'cube', 'runestone', paint=A.runestone_bricks, cut_from='runestone'),
    S('glyphed_runestone', 'cube', 'runestone', paint=A.glyphed_runestone, light=8, cut_from='runestone'),
    *stone_set('runestone', 'runestone_bricks', 'RUNESTONE_BRICKS'),
    # -------------------------------------------------------------- the gear tiers' metals (see gear.py)
    *[S(f'{t}_block', 'cube', 'metal', paint=(lambda t=t: A.metal_block(t)), light=4) for t in
      ('tidebronze', 'runesilver', 'gravegold', 'duskiron', 'dawnsteel')],
    S('duskiron_ore', 'ore', 'gloamstone', paint=A.duskiron_ore, light=3),
    # -------------------------------------------------------------- light, glass and metalwork
    S('lumenite_lamp', 'lamp', 'deco'),
    S('lanternglass', 'glass', 'deco', paint=lambda: A.tinted_glass(A.P['amber_glow'], 0.42), color='COLOR_ORANGE'),
    S('gloamglass', 'glass', 'deco', paint=lambda: A.tinted_glass(A.P['violet_glow'], 0.5), color='COLOR_PURPLE'),
    S('oathsteel_bars', 'bars', 'deco', paint=A.oathsteel_bars),
    S('oathsteel_lantern', 'lantern', 'deco', cage='steel', flame='amber_glow', light=15),
    S('gloam_lantern', 'lantern', 'deco', cage='iron', flame='violet_glow', light=12),
    S('glimmer_moss', 'carpet', 'deco', paint=A.glimmer_moss),
    # -------------------------------------------------------------- wildflowers
    S('dusk_lily', 'flower', 'plant', effect='NIGHT_VISION', secs=5, glint='DUSK', light=5, color='COLOR_PURPLE', dye='purple_dye'),
    S('emberroot', 'flower', 'plant', effect='FIRE_RESISTANCE', secs=4, glint='EMBER', light=6, color='COLOR_ORANGE', dye='orange_dye'),
    S('moonpetal', 'flower', 'plant', effect='REGENERATION', secs=6, glint='MOON', light=4, color='COLOR_LIGHT_BLUE', dye='light_blue_dye'),
    S('gloam_fern', 'flower', 'plant', effect='NIGHT_VISION', secs=3, glint='GLOAM', light=3, color='COLOR_PURPLE', fern=True),
    # -------------------------------------------------------------- potted plants
    S('potted_dusk_lily', 'pot', 'pot', plant='dusk_lily', light=5),
    S('potted_emberroot', 'pot', 'pot', plant='emberroot', light=6),
    S('potted_moonpetal', 'pot', 'pot', plant='moonpetal', light=4),
    S('potted_gloam_fern', 'pot', 'pot', plant='gloam_fern', light=3),
    S('potted_veilbloom', 'pot', 'pot', plant='veilbloom', light=7),
    S('potted_gloamwood_sapling', 'pot', 'pot', plant='gloamwood_sapling', light=0),
]
BY_NAME = {b['name']: b for b in TABLE}

FAMILY_PROPS = {
    'wardstone': 'wardstone()', 'gloamstone': 'gloamstone()', 'gloamwood': 'gloamwood()', 'tidestone': 'tidestone()',
    'barrowstone': 'barrowstone()', 'runestone': 'runestone()', 'metal': 'metal()',
}

# names that do not follow from the id
SPECIAL_NAMES = {
    'gloamwood': 'Gloamwood', 'stripped_gloamwood': 'Stripped Gloamwood', 'lanternglass': 'Lanternglass', 'gloamglass': 'Gloamglass',
    'glimmer_moss': 'Glimmer Moss Carpet', 'tidebronze_block': 'Block of Tidebronze', 'runesilver_block': 'Block of Runesilver',
    'gravegold_block': 'Block of Gravegold', 'duskiron_block': 'Block of Duskiron', 'dawnsteel_block': 'Block of Dawnsteel', 'potted_gloamwood_sapling': 'Potted Gloamwood Sapling', 'emberroot': 'Emberroot',
}


def english(name):
    if name in SPECIAL_NAMES:
        return SPECIAL_NAMES[name]
    return ' '.join(w.capitalize() for w in name.split('_'))


NAMES = {b['name']: english(b['name']) for b in TABLE}


# ====================================================================== Java
def java_line(b):
    n, k, fam = b['name'], b['kind'], b['fam']
    F = n.upper()
    P = FAMILY_PROPS.get(fam)
    light = b.get('light', 0)
    lit = f'.lightLevel(s -> {light})' if light else ''
    if k == 'cube':
        return f'reg("{n}", Block::new, () -> {P}{lit})'
    if k == 'ore':
        return f'reg("{n}", p -> new DropExperienceBlock(UniformInt.of(1, 4), p), () -> {P}.strength(3.5f, 6.0f){lit})'
    if k == 'wood':
        return f'reg("{n}", p -> new StrippableLogBlock(() -> ModBlocks.{b["stripped"]}.get(), p), () -> {P})'
    if k == 'log':
        return f'reg("{n}", RotatedPillarBlock::new, () -> {P})'
    if k == 'stairs':
        return f'reg("{n}", p -> new StairBlock(ModBlocks.{b["base"]}.get().defaultBlockState(), p), () -> {P})'
    if k == 'slab':
        return f'reg("{n}", SlabBlock::new, () -> {P})'
    if k == 'wall':
        return f'reg("{n}", WallBlock::new, () -> {P}.forceSolidOn())'
    if k == 'button':
        sound = 'SoundType.WOOD' if fam == 'gloamwood' else 'SoundType.STONE'
        return f'reg("{n}", p -> new ButtonBlock({b["set"]}, {b["ticks"]}, p), () -> button({sound}))'
    if k == 'plate':
        return f'reg("{n}", p -> new PressurePlateBlock({b["set"]}, p), () -> {P}.forceSolidOn().noCollision().strength(0.5f).pushReaction(PushReaction.DESTROY))'
    if k == 'door':
        return f'reg("{n}", p -> new DoorBlock(GLOAMWOOD_SET, p), () -> {P}.strength(3.0f).noOcclusion().pushReaction(PushReaction.DESTROY))'
    if k == 'trapdoor':
        return f'reg("{n}", p -> new TrapDoorBlock(GLOAMWOOD_SET, p), () -> {P}.strength(3.0f).noOcclusion().isValidSpawn((s, l, pos, t) -> false))'
    if k == 'fence':
        return f'reg("{n}", FenceBlock::new, () -> {P}.forceSolidOn())'
    if k == 'fence_gate':
        return f'reg("{n}", p -> new FenceGateBlock(GLOAMWOOD_TYPE, p), () -> {P}.forceSolidOn())'
    if k == 'leaves':
        return f'reg("{n}", GloamLeavesBlock::new, ModBlocks::leaves)'
    if k == 'sapling':
        return f'reg("{n}", GloamSaplingBlock::new, () -> plant(MapColor.COLOR_PURPLE).randomTicks().lightLevel(s -> 2))'
    if k == 'lamp':
        return (f'reg("{n}", RedstoneLampBlock::new, () -> BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(0.3f)'
                f'.sound(SoundType.GLASS).lightLevel(s -> s.getValue(RedstoneLampBlock.LIT) ? 15 : 0))')
    if k == 'glass':
        return f'reg("{n}", TransparentBlock::new, () -> glass(MapColor.{b["color"]}))'
    if k == 'bars':
        return (f'reg("{n}", IronBarsBlock::new, () -> BlockBehaviour.Properties.of().requiresCorrectToolForDrops().strength(5.0f, 6.0f)'
                f'.sound(SoundType.METAL).noOcclusion())')
    if k == 'lantern':
        return f'reg("{n}", LanternBlock::new, () -> lantern({light}))'
    if k == 'carpet':
        return (f'reg("{n}", CarpetBlock::new, () -> BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(0.1f)'
                f'.sound(SoundType.MOSS_CARPET).pushReaction(PushReaction.DESTROY).lightLevel(s -> 3))')
    if k == 'flower':
        return (f'reg("{n}", p -> new OathFlowerBlock(MobEffects.{b["effect"]}, {b["secs"]}f, OathFlowerBlock.Glint.{b["glint"]}, p), '
                f'() -> plant(MapColor.{b["color"]}).offsetType(BlockBehaviour.OffsetType.XZ){lit})')
    if k == 'pot':
        return (f'reg("{n}", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.{b["plant"].upper()}.get(), p), '
                f'() -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY){lit})')
    raise ValueError(k)


BEGIN = '    // ------------------------------------------------------------------ building families (generated by tools/oath/building.py)\n'
END = '    // ------------------------------------------------------------------ end of building families\n'


def write_java():
    src = open(MODBLOCKS).read()
    lines = [BEGIN]
    for b in TABLE:
        lines.append(f'    public static final RegistryObject<Block> {b["name"].upper()} = {java_line(b)};\n')
    lines.append(END)
    region = ''.join(lines)
    if BEGIN in src:
        a = src.index(BEGIN)
        z = src.index(END) + len(END)
        src = src[:a] + region + src[z:]
    else:
        anchor = '    private static BlockBehaviour.Properties wardstone() {'
        src = src.replace(anchor, region + '\n' + anchor)
    open(MODBLOCKS, 'w').write(src)


# ====================================================================== templates from vanilla's own blockstates
def template(vanilla, name):
    """Loads a vanilla blockstate kept in tools/oath/templates and points its models at ours."""
    s = open(os.path.join(TEMPLATES, vanilla + '.json')).read()
    s = s.replace(f'minecraft:block/{vanilla}', f'oathbound:block/{name}')
    return json.loads(s)


def state(name, obj):
    K.write(f'blockstates/{name}.json', obj)


def parented(name, parent, textures):
    K.model(name, {'parent': parent, 'textures': textures})


# ====================================================================== assets
def paint(b):
    """Paints a block's own textures, when it has a painter; returns True if it made a glow texture."""
    fn = b.get('paint')
    if not fn:
        return False
    r = fn()
    if isinstance(r, tuple):
        K.tex(b['tex'], r[0])
        K.tex(b['tex'] + '_glow', r[1])
        return True
    K.tex(b['tex'], r)
    return False


def cross_model(name, texture, glow=None, emission=12):
    els = K.cross('#cross')
    textures = {'particle': texture, 'cross': texture}
    if glow:
        textures['glow'] = glow
        els += K.cross('#glow', emission=emission)
    K.model(name, {'parent': 'minecraft:block/block', 'ambientocclusion': False, 'textures': textures, 'elements': els})


def pot_model(name, plant_tex, glow=None):
    """A flower pot with the plant standing in it; the plant's glow layer is kept."""
    f = {'texture': '#flowerpot'}
    els = [
        K.box([5, 0, 5], [6, 6, 11], {'down': {**f, 'uv': [5, 5, 6, 11], 'cullface': 'down'}, 'up': {**f, 'uv': [5, 5, 6, 11]},
                                     'north': {**f, 'uv': [10, 10, 11, 16]}, 'south': {**f, 'uv': [5, 10, 6, 16]},
                                     'west': {**f, 'uv': [5, 10, 11, 16]}, 'east': {**f, 'uv': [5, 10, 11, 16]}}),
        K.box([10, 0, 5], [11, 6, 11], {'down': {**f, 'uv': [10, 5, 11, 11], 'cullface': 'down'}, 'up': {**f, 'uv': [10, 5, 11, 11]},
                                       'north': {**f, 'uv': [5, 10, 6, 16]}, 'south': {**f, 'uv': [10, 10, 11, 16]},
                                       'west': {**f, 'uv': [5, 10, 11, 16]}, 'east': {**f, 'uv': [5, 10, 11, 16]}}),
        K.box([6, 0, 5], [10, 6, 6], {'down': {**f, 'uv': [6, 10, 10, 11], 'cullface': 'down'}, 'up': {**f, 'uv': [6, 5, 10, 6]},
                                     'north': {**f, 'uv': [6, 10, 10, 16]}, 'south': {**f, 'uv': [6, 10, 10, 16]}}),
        K.box([6, 0, 10], [10, 6, 11], {'down': {**f, 'uv': [6, 5, 10, 6], 'cullface': 'down'}, 'up': {**f, 'uv': [6, 10, 10, 11]},
                                       'north': {**f, 'uv': [6, 10, 10, 16]}, 'south': {**f, 'uv': [6, 10, 10, 16]}}),
        K.box([6, 0, 6], [10, 4, 10], {'down': {**f, 'uv': [6, 12, 10, 16], 'cullface': 'down'}, 'up': {'texture': '#dirt', 'uv': [6, 6, 10, 10]}}),
    ]
    textures = {'particle': 'minecraft:block/flower_pot', 'flowerpot': 'minecraft:block/flower_pot', 'dirt': 'minecraft:block/dirt',
                'plant': plant_tex}
    for rot in (45, -45):
        els.append({'from': [2.6, 4, 8], 'to': [13.4, 16, 8], 'shade': False,
                    'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': rot, 'rescale': True},
                    'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': '#plant'}, 'south': {'uv': [0, 0, 16, 16], 'texture': '#plant'}}})
    if glow:
        textures['glow'] = glow
        for rot in (45, -45):
            els.append({'from': [2.6, 4, 8], 'to': [13.4, 16, 8], 'shade': False, 'light_emission': 12,
                        'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': rot, 'rescale': True},
                        'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': '#glow'}, 'south': {'uv': [0, 0, 16, 16], 'texture': '#glow'}}})
    K.model(name, {'parent': 'minecraft:block/block', 'ambientocclusion': False, 'textures': textures, 'elements': els})


def lantern_icon(cage, flame):
    """Inventory icon for a lantern: handle, cap, glowing body and base."""
    im = A.img()
    for x in (6, 9):
        for y in (1, 2):
            im.put(x, y, cage.smooth(0.55))
    for x in range(6, 10):
        im.put(x, 0, cage.smooth(0.7))
        im.put(x, 3, cage.smooth(0.55))
        im.put(x, 4, cage.smooth(0.4))
    for y in range(5, 13):
        for x in range(4, 12):
            if x in (4, 11) or y in (5, 12):
                im.put(x, y, cage.smooth(0.35 + (0.3 if x == 4 or y == 5 else 0)))
            else:
                d = abs(x - 7.5) / 3.5 + max(0.0, (8 - y) / 4) * 0.5
                im.put(x, y, flame.smooth(0.95 - d * 0.45))
    for x in range(5, 11):
        im.put(x, 13, cage.smooth(0.3))
    return im


def assets(b):
    n, k, tex = b['name'], b['kind'], b['tex']
    glow = paint(b)
    if k in ('cube', 'ore'):
        if glow:
            K.glow_cube(n, ref(tex), ref(tex + '_glow'), emission=12)
        else:
            K.cube_all(n, ref(tex))
        K.simple_state(n)
        K.item_block(n)
    elif k == 'wood':
        textures = {'particle': ref('gloamwood_log'), 'side': ref('gloamwood_log'), 'glow': ref('gloamwood_log_glow')}
        sides = {f: '#side' for f in K.FACES}
        for suffix in ('', '_horizontal'):
            K.model(n + suffix, {'parent': 'minecraft:block/block', 'textures': textures, 'elements': [
                {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': K.cube_faces(sides)},
                {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 9, 'shade': False,
                 'faces': K.cube_faces({f: '#glow' for f in K.FACES})}]})
        K.axis_state(n)
        K.item_block(n)
    elif k == 'log':
        if b.get('paint_end'):
            K.tex(b['end'], b['paint_end']())
        K.column(n, ref(tex), ref(b['end']))
        K.axis_state(n)
        K.item_block(n)
    elif k == 'stairs':
        K.stairs(n, ref(tex))
    elif k == 'slab':
        K.slab(n, ref(tex), ref(b['double']))
    elif k == 'wall':
        t = {'wall': ref(tex)}
        parented(n + '_post', 'minecraft:block/template_wall_post', t)
        parented(n + '_side', 'minecraft:block/template_wall_side', t)
        parented(n + '_side_tall', 'minecraft:block/template_wall_side_tall', t)
        parented(n + '_inventory', 'minecraft:block/wall_inventory', t)
        state(n, template('cobblestone_wall', n))
        K.item_block(n, n + '_inventory')
    elif k == 'button':
        t = {'texture': ref(tex)}
        parented(n, 'minecraft:block/button', t)
        parented(n + '_pressed', 'minecraft:block/button_pressed', t)
        parented(n + '_inventory', 'minecraft:block/button_inventory', t)
        state(n, template('stone_button', n))
        K.item_block(n, n + '_inventory')
    elif k == 'plate':
        t = {'texture': ref(tex)}
        parented(n, 'minecraft:block/pressure_plate_up', t)
        parented(n + '_down', 'minecraft:block/pressure_plate_down', t)
        state(n, template('stone_pressure_plate', n))
        K.item_block(n)
    elif k == 'door':
        top, bottom = A.gloamwood_door(True), A.gloamwood_door(False)
        K.tex(n + '_top', top)
        K.tex(n + '_bottom', bottom)
        A.door_icon(top, bottom).save(os.path.join(K.ASSETS, 'textures/item', n + '.png'))
        t = {'top': ref(n + '_top'), 'bottom': ref(n + '_bottom')}
        for half in ('bottom', 'top'):
            for hinge in ('left', 'right'):
                for op in ('', '_open'):
                    parented(f'{n}_{half}_{hinge}{op}', f'minecraft:block/door_{half}_{hinge}{op}', t)
        state(n, template('oak_door', n))
        K.write(f'models/item/{n}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'oathbound:item/{n}'}})
        K.write(f'items/{n}.json', {'model': {'type': 'minecraft:model', 'model': f'oathbound:item/{n}'}})
    elif k == 'trapdoor':
        t = {'texture': ref(tex)}
        for part in ('bottom', 'top', 'open'):
            parented(f'{n}_{part}', f'minecraft:block/template_trapdoor_{part}', t)
        state(n, template('oak_trapdoor', n))
        K.item_block(n, n + '_bottom')
    elif k == 'fence':
        t = {'texture': ref(tex)}
        parented(n + '_post', 'minecraft:block/fence_post', t)
        parented(n + '_side', 'minecraft:block/fence_side', t)
        parented(n + '_inventory', 'minecraft:block/fence_inventory', t)
        state(n, template('oak_fence', n))
        K.item_block(n, n + '_inventory')
    elif k == 'fence_gate':
        t = {'texture': ref(tex)}
        for suffix in ('', '_open', '_wall', '_wall_open'):
            parented(n + suffix, f'minecraft:block/template_fence_gate{suffix}', t)
        state(n, template('oak_fence_gate', n))
        K.item_block(n)
    elif k == 'leaves':
        K.model(n, {'parent': 'minecraft:block/block', 'textures': {'particle': ref(tex), 'all': ref(tex), 'glow': ref(tex + '_glow')},
                    'elements': [
                        {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': K.cube_faces({f: '#all' for f in K.FACES})},
                        {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 10, 'shade': False,
                         'faces': K.cube_faces({f: '#glow' for f in K.FACES})}]})
        K.simple_state(n)
        K.item_block(n)
    elif k == 'sapling':
        cross_model(n, ref(tex), ref(tex + '_glow'))
        K.simple_state(n)
        K.item_flat(n, ref(tex))
    elif k == 'lamp':
        for lit in (False, True):
            im, gl = A.lumenite_lamp(lit)
            K.tex(n + ('_on' if lit else ''), im)
            if lit:
                K.tex(n + '_on_glow', gl)
        K.cube_all(n, ref(n))
        K.glow_cube(n + '_on', ref(n + '_on'), ref(n + '_on_glow'), emission=15)
        state(n, {'variants': {'lit=false': {'model': ref(n)}, 'lit=true': {'model': ref(n + '_on')}}})
        K.item_block(n)
    elif k == 'glass':
        K.cube_all(n, ref(tex))
        K.simple_state(n)
        K.item_block(n)
    elif k == 'bars':
        t = {'bars': ref(tex), 'edge': ref(tex)}
        for part in ('post_ends', 'post', 'cap', 'cap_alt', 'side', 'side_alt'):
            parented(f'{n}_{part}', f'minecraft:block/template_bars_{part}', t)
        state(n, template('iron_bars', n))
        K.item_flat(n, ref(tex))
    elif k == 'lantern':
        cage, flame = A.P[b['cage']], A.P[b['flame']]
        K.tex(n, A.lantern(cage, flame))
        lantern_icon(cage, flame).save(os.path.join(K.ASSETS, 'textures/item', n + '.png'))
        parented(n, 'minecraft:block/template_lantern', {'lantern': ref(n)})
        parented(n + '_hanging', 'minecraft:block/template_hanging_lantern', {'lantern': ref(n)})
        state(n, {'variants': {'hanging=false': {'model': ref(n)}, 'hanging=true': {'model': ref(n + '_hanging')}}})
        K.write(f'models/item/{n}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'oathbound:item/{n}'}})
        K.write(f'items/{n}.json', {'model': {'type': 'minecraft:model', 'model': f'oathbound:item/{n}'}})
    elif k == 'carpet':
        K.model(n, {'parent': 'minecraft:block/block', 'textures': {'particle': ref(tex), 'wool': ref(tex), 'glow': ref(tex + '_glow')},
                    'elements': [
                        {'from': [0, 0, 0], 'to': [16, 1, 16], 'faces': {
                            'down': {'uv': [0, 0, 16, 16], 'texture': '#wool', 'cullface': 'down'}, 'up': {'uv': [0, 0, 16, 16], 'texture': '#wool'},
                            'north': {'uv': [0, 15, 16, 16], 'texture': '#wool', 'cullface': 'north'},
                            'south': {'uv': [0, 15, 16, 16], 'texture': '#wool', 'cullface': 'south'},
                            'west': {'uv': [0, 15, 16, 16], 'texture': '#wool', 'cullface': 'west'},
                            'east': {'uv': [0, 15, 16, 16], 'texture': '#wool', 'cullface': 'east'}}},
                        {'from': [0, 1.01, 0], 'to': [16, 1.01, 16], 'light_emission': 9, 'shade': False,
                         'faces': {'up': {'uv': [0, 0, 16, 16], 'texture': '#glow'}}}]})
        K.simple_state(n)
        K.item_block(n)
    elif k == 'flower':
        im, gl = A.flower(n)
        K.tex(n, im)
        K.tex(n + '_glow', gl)
        cross_model(n, ref(n), ref(n + '_glow'))
        K.simple_state(n)
        K.item_flat(n, ref(n))
    elif k == 'pot':
        p = b['plant']
        pot_model(n, ref(p), ref(p + '_glow'))
        K.simple_state(n)
    else:
        raise ValueError(k)


# ====================================================================== loot
def door_loot(n):
    return D.table('block', [D.pool([{'type': 'minecraft:item', 'name': D.o(n), 'conditions': [
        {'condition': 'minecraft:block_state_property', 'block': D.o(n), 'properties': {'half': 'lower'}}]}],
        conds=[{'condition': 'minecraft:survives_explosion'}])], f'blocks/{n}')


SHEARS_OR_SILK = {'condition': 'minecraft:any_of', 'terms': [
    {'condition': 'minecraft:match_tool', 'predicate': {'items': 'minecraft:shears'}},
    {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {'minecraft:enchantments': [
        {'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}]}
SILK = {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {'minecraft:enchantments': [
    {'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}


def leaves_loot(n, sapling):
    return D.table('block', [
        D.pool([{'type': 'minecraft:alternatives', 'children': [
            {'type': 'minecraft:item', 'name': D.o(n), 'conditions': [SHEARS_OR_SILK]},
            {'type': 'minecraft:item', 'name': D.o(sapling), 'conditions': [
                {'condition': 'minecraft:survives_explosion'},
                {'condition': 'minecraft:table_bonus', 'enchantment': 'minecraft:fortune', 'chances': [0.05, 0.0625, 0.083333336, 0.1]}]}]}]),
        D.pool([{'type': 'minecraft:item', 'name': 'minecraft:stick', 'conditions': [
            {'condition': 'minecraft:table_bonus', 'enchantment': 'minecraft:fortune', 'chances': [0.02, 0.022222223, 0.025, 0.033333335, 0.1]}],
            'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 1, 'max': 2}},
                          {'function': 'minecraft:explosion_decay'}]}],
            conds=[{'condition': 'minecraft:inverted', 'term': SHEARS_OR_SILK}]),
        D.pool([{'type': 'minecraft:item', 'name': D.o('luminous_dust'), 'conditions': [
            {'condition': 'minecraft:survives_explosion'},
            {'condition': 'minecraft:table_bonus', 'enchantment': 'minecraft:fortune', 'chances': [0.02, 0.025, 0.03, 0.04, 0.08]}]}],
            conds=[{'condition': 'minecraft:inverted', 'term': SHEARS_OR_SILK}]),
    ], f'blocks/{n}')


def only_with(n, cond):
    return D.table('block', [D.pool([{'type': 'minecraft:item', 'name': D.o(n), 'conditions': [cond]}])], f'blocks/{n}')


def pot_loot(n, plant):
    return D.table('block', [D.pool([D.item('minecraft:flower_pot')], conds=[{'condition': 'minecraft:survives_explosion'}]),
                             D.pool([D.item(plant)], conds=[{'condition': 'minecraft:survives_explosion'}])], f'blocks/{n}')


def loot(b):
    n, k = b['name'], b['kind']
    if k == 'slab':
        t = D.slab_drop(n)
    elif k == 'door':
        t = door_loot(n)
    elif k == 'leaves':
        t = leaves_loot(n, 'gloamwood_sapling')
    elif k == 'glass':
        t = only_with(n, SILK)
    elif k == 'ore':
        t = D.silk_or(n, 'raw_duskiron', 1, 1)
    elif k == 'pot':
        t = pot_loot(n, b['plant'])
    elif k == 'flower' and b.get('fern'):
        t = only_with(n, SHEARS_OR_SILK)
    else:
        t = D.self_drop(n)
    D.write(f'loot_table/blocks/{n}.json', t)


# ====================================================================== recipes
def stonecut(result, ingredient, count=1):
    D.recipe(f'{result}_from_{ingredient}_stonecutting', {'type': 'minecraft:stonecutting', 'ingredient': D.o(ingredient),
                                                          'result': {'id': D.o(result), 'count': count}})


def recipes():
    B = 'building'
    for b in TABLE:
        n, k = b['name'], b['kind']
        src = b.get('cut_from') or b['tex']
        if k == 'stairs':
            D.shaped(n, ['#  ', '## ', '###'], {'#': src}, n, 4, category=B)
            if b['fam'] != 'gloamwood':
                stonecut(n, src)
        elif k == 'slab':
            D.shaped(n, ['###'], {'#': src}, n, 6, category=B)
            if b['fam'] != 'gloamwood':
                stonecut(n, src, 2)
        elif k == 'wall':
            D.shaped(n, ['###', '###'], {'#': src}, n, 6, category='misc')
            stonecut(n, src)
    # derived stones
    for n, src in (('polished_wardstone', 'wardstone'), ('wardstone_tiles', 'polished_wardstone'), ('polished_gloamstone', 'gloamstone'),
                   ('gloamstone_tiles', 'polished_gloamstone'), ('tidestone_bricks', 'tidestone'), ('barrowstone_bricks', 'barrowstone'),
                   ('runestone_bricks', 'runestone')):
        D.shaped(n, ['##', '##'], {'#': src}, n, 4, category=B)
        stonecut(n, src)
    for n, slab in (('chiseled_gloamstone', 'polished_gloamstone_slab'), ('chiseled_tidestone', 'tidestone_brick_slab')):
        D.shaped(n, ['#', '#'], {'#': slab}, n, category=B)
    stonecut('chiseled_gloamstone', 'gloamstone')
    stonecut('chiseled_tidestone', 'tidestone')
    stonecut('glyphed_runestone', 'runestone')
    D.cooking('cracked_gloamstone_bricks', 'smelting', 'gloamstone_bricks', 'cracked_gloamstone_bricks', 0.1, 200)
    D.shapeless('barnacled_tidestone_bricks', ['tidestone_bricks', 'minecraft:kelp'], 'barnacled_tidestone_bricks', category=B)
    D.shapeless('bone_inlaid_barrowstone', ['barrowstone_bricks', 'minecraft:bone'], 'bone_inlaid_barrowstone', category=B)
    D.shapeless('glyphed_runestone', ['runestone_bricks', 'lumenite_dust'], 'glyphed_runestone', category=B)
    # the three regional stones, for builders who never find their ruins
    D.shaped('tidestone', ['SP', 'PS'], {'S': 'minecraft:stone', 'P': 'minecraft:prismarine_shard'}, 'tidestone', 4, category=B)
    D.shaped('barrowstone', ['SB', 'BS'], {'S': 'minecraft:tuff', 'B': 'minecraft:bone_meal'}, 'barrowstone', 4, category=B)
    D.shaped('runestone', [' D ', 'DLD', ' D '], {'D': 'minecraft:cobbled_deepslate', 'L': 'minecraft:lapis_lazuli'}, 'runestone', 4, category=B)
    # buttons and plates
    D.shapeless('wardstone_button', ['polished_wardstone'], 'wardstone_button', category='redstone')
    D.shaped('wardstone_pressure_plate', ['##'], {'#': 'polished_wardstone'}, 'wardstone_pressure_plate', category='redstone')
    D.shapeless('gloamwood_button', ['gloamwood_planks'], 'gloamwood_button', category='redstone')
    D.shaped('gloamwood_pressure_plate', ['##'], {'#': 'gloamwood_planks'}, 'gloamwood_pressure_plate', category='redstone')
    # woodwork
    D.shaped('gloamwood', ['##', '##'], {'#': 'gloamwood_log'}, 'gloamwood', 3, category=B)
    D.shaped('stripped_gloamwood', ['##', '##'], {'#': 'stripped_gloamwood_log'}, 'stripped_gloamwood', 3, category=B)
    for log in ('gloamwood', 'stripped_gloamwood_log', 'stripped_gloamwood'):
        D.shapeless(f'gloamwood_planks_from_{log}', [log], 'gloamwood_planks', 4, category=B)
    D.shaped('gloamwood_door', ['##', '##', '##'], {'#': 'gloamwood_planks'}, 'gloamwood_door', 3, group='wooden_door', category='redstone')
    D.shaped('gloamwood_trapdoor', ['###', '###'], {'#': 'gloamwood_planks'}, 'gloamwood_trapdoor', 2, group='wooden_trapdoor', category='redstone')
    D.shaped('gloamwood_fence', ['W#W', 'W#W'], {'W': 'gloamwood_planks', '#': 'minecraft:stick'}, 'gloamwood_fence', 3, group='wooden_fence', category='misc')
    D.shaped('gloamwood_fence_gate', ['#W#', '#W#'], {'W': 'gloamwood_planks', '#': 'minecraft:stick'}, 'gloamwood_fence_gate', group='wooden_fence_gate', category='redstone')
    # light, glass and metal
    D.shaped('lumenite_lamp', ['NSN', 'SRS', 'NSN'], {'N': 'oathsteel_nugget', 'S': 'lumenite_shard', 'R': 'minecraft:redstone'}, 'lumenite_lamp', category='redstone')
    D.shaped('lanternglass', ['GGG', 'GDG', 'GGG'], {'G': 'minecraft:glass', 'D': 'lumenite_dust'}, 'lanternglass', 8, category=B)
    D.shaped('gloamglass', ['GGG', 'GDG', 'GGG'], {'G': 'minecraft:glass', 'D': 'gloam_essence'}, 'gloamglass', 8, category=B)
    D.shaped('oathsteel_bars', ['III', 'III'], {'I': 'oathsteel_ingot'}, 'oathsteel_bars', 16, category='misc')
    D.shaped('oathsteel_lantern', ['NNN', 'NSN', 'NNN'], {'N': 'oathsteel_nugget', 'S': 'lumenite_shard'}, 'oathsteel_lantern', category='misc')
    D.shaped('gloam_lantern', ['NNN', 'NSN', 'NNN'], {'N': 'oathsteel_nugget', 'S': 'gloam_essence'}, 'gloam_lantern', category='misc')
    D.shaped('glimmer_moss', ['##'], {'#': 'gloam_moss'}, 'glimmer_moss', 3, category='misc')
    # dyes from the wildflowers
    for b in TABLE:
        if b.get('dye'):
            D.shapeless(f'{b["dye"]}_from_{b["name"]}', [b['name']], f'minecraft:{b["dye"]}', category='misc')


# ====================================================================== worldgen: wildflower meadows
FLOWER_BIOMES = {
    'dusk_lily': ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:flower_forest', 'minecraft:cherry_grove'],
    'emberroot': ['#minecraft:is_savanna', '#minecraft:is_badlands', 'minecraft:windswept_savanna'],
    'moonpetal': ['#minecraft:is_taiga', 'minecraft:birch_forest', 'minecraft:old_growth_birch_forest', 'minecraft:dark_forest',
                  'minecraft:snowy_plains', 'minecraft:grove'],
}


def patch(name, block, tries, spread, rarity):
    D.write(f'worldgen/configured_feature/{name}.json', {'type': 'minecraft:flower', 'config': {
        'tries': tries, 'xz_spread': spread, 'y_spread': 3,
        'feature': {'feature': {'type': 'minecraft:simple_block', 'config': {
            'to_place': {'type': 'minecraft:simple_state_provider', 'state': {'Name': D.o(block)}}}},
            'placement': [{'type': 'minecraft:block_predicate_filter',
                           'predicate': {'type': 'minecraft:matching_blocks', 'blocks': 'minecraft:air'}}]}}})
    D.write(f'worldgen/placed_feature/{name}.json', {'feature': f'oathbound:{name}', 'placement': [
        {'type': 'minecraft:rarity_filter', 'chance': rarity}, {'type': 'minecraft:in_square'},
        {'type': 'minecraft:heightmap', 'heightmap': 'MOTION_BLOCKING'}, {'type': 'minecraft:biome'}]})


def worldgen():
    for flower, biomes in FLOWER_BIOMES.items():
        patch(f'{flower}_patch', flower, 48, 6, 10)
        D.tag(f'worldgen/biome/has_flower/{flower}', biomes)
        D.write(f'forge/biome_modifier/{flower}_patches.json', {'type': 'forge:add_features', 'biomes': f'#oathbound:has_flower/{flower}',
                                                                  'features': [f'oathbound:{flower}_patch'], 'step': 'vegetal_decoration'})
    # the Gloaming's undergrowth: data.py lists this among the Gloaming's features
    patch('gloam_fern_patch', 'gloam_fern', 40, 7, 2)


# ====================================================================== tags (handed to data.py)
def _names(*kinds, fam=None):
    return [b['name'] for b in TABLE if b['kind'] in kinds and (fam is None or b['fam'] == fam)]


STONE_FAMS = ('wardstone', 'gloamstone', 'tidestone', 'barrowstone', 'runestone', 'metal')
TAGS = {
    'block/mineable/pickaxe': [b['name'] for b in TABLE if b['fam'] in STONE_FAMS] + _names('lamp', 'bars', 'lantern'),
    'block/mineable/axe': [b['name'] for b in TABLE if b['fam'] == 'gloamwood' and b['kind'] not in ('leaves', 'sapling')],
    'block/mineable/hoe': _names('leaves', 'carpet'),
    'block/stairs': _names('stairs'), 'item/stairs': _names('stairs'),
    'block/slabs': _names('slab'), 'item/slabs': _names('slab'),
    'block/walls': _names('wall'), 'item/walls': _names('wall'),
    'block/wooden_stairs': _names('stairs', fam='gloamwood'), 'item/wooden_stairs': _names('stairs', fam='gloamwood'),
    'block/wooden_slabs': _names('slab', fam='gloamwood'), 'item/wooden_slabs': _names('slab', fam='gloamwood'),
    'block/wooden_fences': _names('fence'), 'item/wooden_fences': _names('fence'),
    'block/fence_gates': _names('fence_gate'), 'item/fence_gates': _names('fence_gate'),
    'block/wooden_doors': _names('door'), 'item/wooden_doors': _names('door'),
    'block/wooden_trapdoors': _names('trapdoor'), 'item/wooden_trapdoors': _names('trapdoor'),
    'block/wooden_buttons': _names('button', fam='gloamwood'), 'item/wooden_buttons': _names('button', fam='gloamwood'),
    'block/stone_buttons': _names('button', fam='wardstone'), 'item/stone_buttons': _names('button', fam='wardstone'),
    'block/wooden_pressure_plates': _names('plate', fam='gloamwood'), 'item/wooden_pressure_plates': _names('plate', fam='gloamwood'),
    'block/stone_pressure_plates': _names('plate', fam='wardstone'),
    'block/logs': ['gloamwood', 'stripped_gloamwood_log', 'stripped_gloamwood'],
    'item/logs': ['gloamwood', 'stripped_gloamwood_log', 'stripped_gloamwood'],
    'block/leaves': _names('leaves'), 'item/leaves': _names('leaves'),
    'block/saplings': _names('sapling'), 'item/saplings': _names('sapling'),
    'block/small_flowers': ['dusk_lily', 'emberroot', 'moonpetal'], 'item/small_flowers': ['dusk_lily', 'emberroot', 'moonpetal'],
    'block/flower_pots': _names('pot'),
    'block/impermeable': _names('glass'),
    'block/needs_iron_tool': ['duskiron_ore'] + [f'{t}_block' for t in ('tidebronze', 'runesilver', 'gravegold')],
    'block/needs_diamond_tool': ['duskiron_block', 'dawnsteel_block'],
}


def lang_names():
    return {k: v for k, v in NAMES.items()}


def generate():
    """Java and client assets. Loot, recipes, tags and worldgen are written by data.py, which owns those files."""
    write_java()
    for b in TABLE:
        assets(b)
    print(len(TABLE), 'building blocks written')


if __name__ == '__main__':
    generate()
