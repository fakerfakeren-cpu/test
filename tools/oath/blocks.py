"""Block resources: textures, block models, blockstates and block-item definitions.

Run from the repository root:  python3 -m tools.oath.blocks
"""
import json
import os

from . import blockart as A

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')
NS = 'oathbound'


def write(rel, data):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def tex(name, im):
    im.save(os.path.join(ASSETS, 'textures/block', name + '.png'))


def animated(name, frames, frametime=2):
    """Stacks frames vertically and writes the .mcmeta that animates them."""
    from .paint import Img
    strip = Img(16, 16 * len(frames))
    for i, f in enumerate(frames):
        strip.px[i * 16:(i + 1) * 16] = f.px
    strip.save(os.path.join(ASSETS, 'textures/block', name + '.png'))
    with open(os.path.join(ASSETS, 'textures/block', name + '.png.mcmeta'), 'w') as f:
        json.dump({'animation': {'frametime': frametime, 'interpolate': True}}, f, indent=2)


def ref(name):
    return f'{NS}:block/{name}'


def model(name, data):
    write(f'models/block/{name}.json', data)


def item_block(name, model_name=None):
    write(f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': ref(model_name or name)}})


def item_flat(name, texture):
    write(f'models/item/{name}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': texture}})
    write(f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{name}'}})


def simple_state(name, model_name=None):
    write(f'blockstates/{name}.json', {'variants': {'': {'model': ref(model_name or name)}}})


FACES = ('down', 'up', 'north', 'south', 'west', 'east')
Y_ROT = {'north': 0, 'east': 90, 'south': 180, 'west': 270}


def cube_faces(textures, cull=True, uv=None):
    """textures: dict face -> texture variable ('#all' etc.)."""
    out = {}
    for f in FACES:
        t = textures.get(f)
        if t is None:
            continue
        d = {'texture': t}
        if cull:
            d['cullface'] = f
        if uv:
            d['uv'] = uv
        out[f] = d
    return out


def glow_cube(name, base_tex, glow_tex, faces=FACES, emission=12):
    """A full cube whose glow texture is laid over the chosen faces with light_emission."""
    elements = [
        {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces({f: '#all' for f in FACES})},
        {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': emission, 'shade': False,
         'faces': cube_faces({f: '#glow' for f in faces})},
    ]
    model(name, {'parent': 'minecraft:block/block', 'textures': {'particle': base_tex, 'all': base_tex, 'glow': glow_tex},
                 'elements': elements})


def cube_all(name, texture=None):
    model(name, {'parent': 'minecraft:block/cube_all', 'textures': {'all': texture or ref(name)}})


def column(name, side, end):
    model(name, {'parent': 'minecraft:block/cube_column', 'textures': {'side': side, 'end': end}})
    model(name + '_horizontal', {'parent': 'minecraft:block/cube_column_horizontal', 'textures': {'side': side, 'end': end}})


def axis_state(name, glow=False):
    write(f'blockstates/{name}.json', {'variants': {
        'axis=y': {'model': ref(name)},
        'axis=z': {'model': ref(name + '_horizontal'), 'x': 90},
        'axis=x': {'model': ref(name + '_horizontal'), 'x': 90, 'y': 90},
    }})


def facing_variants(model_for, extra=None):
    """Variants for a horizontal FACING property (model faces north by default)."""
    variants = {}
    for facing, y in Y_ROT.items():
        for key, mname in (extra or {'': None}).items():
            k = f'facing={facing}' + (',' + key if key else '')
            v = {'model': model_for(key)}
            if y:
                v['y'] = y
            variants[k] = v
    return variants


# ------------------------------------------------------------------ stairs and slabs (vanilla-shaped)
def stairs(name, texture):
    t = {'bottom': texture, 'top': texture, 'side': texture}
    model(name, {'parent': 'minecraft:block/stairs', 'textures': t})
    model(name + '_inner', {'parent': 'minecraft:block/inner_stairs', 'textures': t})
    model(name + '_outer', {'parent': 'minecraft:block/outer_stairs', 'textures': t})
    variants = {}
    base = {'east': 0, 'south': 90, 'west': 180, 'north': 270}
    for facing, fy in base.items():
        for half in ('bottom', 'top'):
            for shape in ('straight', 'inner_left', 'inner_right', 'outer_left', 'outer_right'):
                m = ref(name + ('' if shape == 'straight' else '_inner' if 'inner' in shape else '_outer'))
                y = fy
                if half == 'bottom' and shape.endswith('_left'):
                    y = (fy + 270) % 360
                if half == 'top' and shape.endswith('_right'):
                    y = (fy + 90) % 360
                v = {'model': m}
                if half == 'top':
                    v['x'] = 180
                if y:
                    v['y'] = y
                if 'x' in v or 'y' in v:
                    v['uvlock'] = True
                variants[f'facing={facing},half={half},shape={shape}'] = v
    write(f'blockstates/{name}.json', {'variants': variants})
    item_block(name)


def slab(name, texture, double_model):
    t = {'bottom': texture, 'top': texture, 'side': texture}
    model(name, {'parent': 'minecraft:block/slab', 'textures': t})
    model(name + '_top', {'parent': 'minecraft:block/slab_top', 'textures': t})
    write(f'blockstates/{name}.json', {'variants': {
        'type=bottom': {'model': ref(name)},
        'type=top': {'model': ref(name + '_top')},
        'type=double': {'model': double_model},
    }})
    item_block(name)


# ------------------------------------------------------------------ element helpers for shaped blocks
def box(frm, to, faces, **kw):
    e = {'from': list(frm), 'to': list(to), 'faces': faces}
    e.update(kw)
    return e


def all_faces(texture, cull=None, uv_fn=None):
    out = {}
    for f in FACES:
        d = {'texture': texture}
        if cull and f in cull:
            d['cullface'] = f
        out[f] = d
    return out


def generate():
    # ---------------------------------------------------------- textures
    tex('wardstone', A.wardstone())
    tex('wardstone_bricks', A.wardstone_bricks())
    tex('cracked_wardstone_bricks', A.cracked_wardstone_bricks())
    tex('mossy_wardstone_bricks', A.mossy_wardstone_bricks())
    tex('polished_wardstone', A.polished_wardstone())
    im, gl = A.chiseled_wardstone()
    tex('chiseled_wardstone', im)
    tex('chiseled_wardstone_glow', gl)
    tex('wardstone_pillar', A.wardstone_pillar_side())
    tex('wardstone_pillar_top', A.wardstone_pillar_top())
    im, gl = A.gloamstone()
    tex('gloamstone', im)
    tex('gloamstone_glow', gl)
    tex('gloamstone_bricks', A.gloamstone_bricks())
    im, gl = A.gloam_moss_top()
    tex('gloam_moss_top', im)
    tex('gloam_moss_top_glow', gl)
    tex('gloam_moss_side', A.gloam_moss_side())
    im, gl = A.gloamwood_log_side()
    tex('gloamwood_log', im)
    tex('gloamwood_log_glow', gl)
    tex('gloamwood_log_top', A.gloamwood_log_top())
    tex('gloamwood_planks', A.gloamwood_planks())
    im, gl = A.lumenite_ore()
    tex('lumenite_ore', im)
    tex('lumenite_ore_glow', gl)
    im, gl = A.deepslate_lumenite_ore()
    tex('deepslate_lumenite_ore', im)
    tex('deepslate_lumenite_ore_glow', gl)
    im, gl = A.lumenite_block()
    tex('lumenite_block', im)
    tex('lumenite_block_glow', gl)
    tex('oathsteel_block', A.oathsteel_block())
    im, gl = A.veilbloom()
    tex('veilbloom', im)
    tex('veilbloom_glow', gl)
    im, gl = A.lore_tablet_front()
    tex('lore_tablet', im)
    tex('lore_tablet_glow', gl)
    for p in range(6):
        im, gl = A.hymn_stone(p, False)
        tex(f'hymn_stone_{p}', im)
        tex(f'hymn_stone_{p}_glow', gl)
    im, gl = A.hymn_stone(5, True)
    tex('hymn_stone_solved', im)
    tex('hymn_stone_solved_glow', gl)
    tex('tidestone', A.tiles(A.P['tide'], A.hexrgb('#0a1714'), 409, size=16, tone=0.55))
    for g in range(6):
        for n in range(4):
            im, gl = A.rune_dial(g)
            for k in range(n + 1):
                im.put(6 + k, 1, A.P['brass'].smooth(0.9))
            tex(f'rune_dial_{g}_{n}', im)
            tex(f'rune_dial_{g}_glow', gl)
    tex('arcane_stone', A.stone(A.P['arcane'], 420, lo=0.3, hi=0.8))
    for solved in (False, True):
        im, gl = A.sundered_keystone(solved)
        s = '_active' if solved else ''
        tex('sundered_keystone' + s, im)
        if solved:
            tex('sundered_keystone_active_glow', gl)
    tex('barrow_stone', A.barrow_stone())
    tex('barrow_seal', A.barrow_seal())
    tex('sealed_grate', A.sealed_grate())
    tex('arcane_ward', A.arcane_ward())
    animated('gloam_veil', A.veil_frames(), 3)
    animated('everflame', A.flame_frames(), 2)
    tex('brazier_metal', A.brazier_metal())
    for lit in (False, True):
        im, gl = A.brazier_coals(lit)
        tex('brazier_coals' + ('_lit' if lit else ''), im)
        if lit:
            tex('brazier_coals_lit_glow', gl)
    for i, tint in enumerate(A.BELL_TINTS):
        tex(f'chapel_bell_{i}', A.bell_metal(tint))
    tex('lantern_frame', A.lantern_frame())
    for lit in (False, True):
        im, gl = A.lantern_pane(lit)
        tex('ward_lantern_pane' + ('_lit' if lit else ''), im)
        if lit:
            tex('ward_lantern_pane_lit_glow', gl)
    for k in range(3):
        tex(f'sarcophagus_{k}', A.sarcophagus_side(k))
    tex('sarcophagus_top', A.sarcophagus_top(False))
    for solved in (False, True):
        im, gl = A.cipher_book(solved)
        tex('cipher_book' + ('_solved' if solved else ''), im)
        if solved:
            tex('cipher_book_solved_glow', gl)

    # ---------------------------------------------------------- simple cubes
    for name in ('wardstone', 'wardstone_bricks', 'cracked_wardstone_bricks', 'mossy_wardstone_bricks',
                 'gloamstone_bricks', 'gloamwood_planks', 'oathsteel_block', 'barrow_seal'):
        cube_all(name)
        simple_state(name)
        item_block(name)
    model('sealed_grate', {'parent': 'minecraft:block/cube_all', 'textures': {'all': ref('sealed_grate')}})
    simple_state('sealed_grate')
    item_block('sealed_grate')

    glow_cube('gloamstone', ref('gloamstone'), ref('gloamstone_glow'), emission=6)
    simple_state('gloamstone')
    item_block('gloamstone')
    for ore in ('lumenite_ore', 'deepslate_lumenite_ore'):
        glow_cube(ore, ref(ore), ref(ore + '_glow'), emission=12)
        simple_state(ore)
        item_block(ore)
    glow_cube('lumenite_block', ref('lumenite_block'), ref('lumenite_block_glow'), emission=15)
    simple_state('lumenite_block')
    item_block('lumenite_block')
    glow_cube('chiseled_wardstone', ref('chiseled_wardstone'), ref('chiseled_wardstone_glow'), emission=10)
    simple_state('chiseled_wardstone')
    item_block('chiseled_wardstone')

    # arcane ward: translucent light
    model('arcane_ward', {'parent': 'minecraft:block/block',
                          'textures': {'particle': ref('arcane_ward'), 'all': {'sprite': ref('arcane_ward'), 'force_translucent': True}},
                          'elements': [{'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 10, 'shade': False,
                                        'faces': cube_faces({f: '#all' for f in FACES})}]})
    simple_state('arcane_ward')
    item_block('arcane_ward')

    # pillar and log
    column('wardstone_pillar', ref('wardstone_pillar'), ref('wardstone_pillar_top'))
    axis_state('wardstone_pillar')
    item_block('wardstone_pillar')
    log_textures = {'particle': ref('gloamwood_log'), 'side': ref('gloamwood_log'), 'end': ref('gloamwood_log_top'),
                    'glow': ref('gloamwood_log_glow')}
    side_faces = {'north': '#side', 'south': '#side', 'west': '#side', 'east': '#side', 'up': '#end', 'down': '#end'}
    glow_faces = {'north': '#glow', 'south': '#glow', 'west': '#glow', 'east': '#glow'}
    for suffix in ('', '_horizontal'):
        model('gloamwood_log' + suffix, {'parent': 'minecraft:block/block', 'textures': log_textures, 'elements': [
            {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces(side_faces)},
            {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 9, 'shade': False, 'faces': cube_faces(glow_faces)},
        ]})
    axis_state('gloamwood_log')
    item_block('gloamwood_log')

    # gloam moss: violet moss over gloamstone, glowing specks on top
    model('gloam_moss', {'parent': 'minecraft:block/block', 'textures': {
        'particle': ref('gloam_moss_side'), 'top': ref('gloam_moss_top'), 'side': ref('gloam_moss_side'),
        'bottom': ref('gloamstone'), 'glow': ref('gloam_moss_top_glow')}, 'elements': [
        {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces({'up': '#top', 'down': '#bottom', 'north': '#side', 'south': '#side', 'west': '#side', 'east': '#side'})},
        {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 8, 'shade': False, 'faces': cube_faces({'up': '#glow'})},
    ]})
    write('blockstates/gloam_moss.json', {'variants': {'': [
        {'model': ref('gloam_moss')}, {'model': ref('gloam_moss'), 'y': 90},
        {'model': ref('gloam_moss'), 'y': 180}, {'model': ref('gloam_moss'), 'y': 270}]}})
    item_block('gloam_moss')

    # stairs & slab
    stairs('wardstone_brick_stairs', ref('wardstone_bricks'))
    slab('wardstone_brick_slab', ref('wardstone_bricks'), ref('wardstone_bricks'))

    # veilbloom: a glowing cross
    model('veilbloom', {'parent': 'minecraft:block/block', 'ambientocclusion': False,
                        'textures': {'particle': ref('veilbloom'), 'cross': ref('veilbloom'), 'glow': ref('veilbloom_glow')},
                        'elements': cross('#cross') + cross('#glow', emission=12)})
    simple_state('veilbloom')
    item_flat('veilbloom', ref('veilbloom'))

    # ---------------------------------------------------------- shaped relic blocks
    # lore tablet: a carved face on polished wardstone
    model('lore_tablet', {'parent': 'minecraft:block/block', 'textures': {
        'particle': ref('polished_wardstone'), 'front': ref('lore_tablet'), 'side': ref('polished_wardstone'), 'glow': ref('lore_tablet_glow')},
        'elements': [
            {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces({'north': '#front', 'south': '#side', 'east': '#side', 'west': '#side', 'up': '#side', 'down': '#side'})},
            {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 8, 'shade': False, 'faces': cube_faces({'north': '#glow'})},
        ]})
    write('blockstates/lore_tablet.json', {'variants': facing_variants(lambda k: ref('lore_tablet'))})
    item_block('lore_tablet')
    cube_all('polished_wardstone')

    # hymn stone: five hymn bars that light as the hymn is sung
    for key in [str(p) for p in range(6)] + ['solved']:
        t = f'hymn_stone_{key}'
        model(t, {'parent': 'minecraft:block/block', 'textures': {
            'particle': ref(t), 'side': ref(t), 'end': ref('tidestone'), 'glow': ref(t + '_glow')},
            'elements': [
                {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces({'north': '#side', 'south': '#side', 'east': '#side', 'west': '#side', 'up': '#end', 'down': '#end'})},
                {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 11, 'shade': False,
                 'faces': cube_faces({'north': '#glow', 'south': '#glow', 'east': '#glow', 'west': '#glow'})},
            ]})
    variants = {'solved=true': {'model': ref('hymn_stone_solved')}}
    for p in range(6):
        variants[f'progress={p},solved=false'] = {'model': ref(f'hymn_stone_{p}')}
    write('blockstates/hymn_stone.json', {'variants': variants})
    item_block('hymn_stone', 'hymn_stone_0')

    # rune dial: the glyph on its face, the dial's numeral as notches above it
    variants = {}
    for g in range(6):
        for n in range(4):
            t = f'rune_dial_{g}_{n}'
            model(t, {'parent': 'minecraft:block/block', 'textures': {
                'particle': ref('arcane_stone'), 'front': ref(t), 'side': ref('arcane_stone'), 'glow': ref(f'rune_dial_{g}_glow')},
                'elements': [
                    {'from': [0, 0, 0], 'to': [16, 16, 16], 'faces': cube_faces({'north': '#front', 'south': '#side', 'east': '#side', 'west': '#side', 'up': '#side', 'down': '#side'})},
                    {'from': [0, 0, 0], 'to': [16, 16, 16], 'light_emission': 12, 'shade': False, 'faces': cube_faces({'north': '#glow'})},
                ]})
            for facing, y in Y_ROT.items():
                v = {'model': ref(t)}
                if y:
                    v['y'] = y
                variants[f'facing={facing},glyph={g},number={n}'] = v
    write('blockstates/rune_dial.json', {'variants': variants})
    item_block('rune_dial', 'rune_dial_0_0')

    # sundered keystone
    model('sundered_keystone', {'parent': 'minecraft:block/cube_all', 'textures': {'all': ref('sundered_keystone')}})
    glow_cube('sundered_keystone_active', ref('sundered_keystone_active'), ref('sundered_keystone_active_glow'), emission=15)
    write('blockstates/sundered_keystone.json', {'variants': {
        'active=false': {'model': ref('sundered_keystone')}, 'active=true': {'model': ref('sundered_keystone_active')}}})
    item_block('sundered_keystone')

    # barrow stone for the sarcophagus and the barrow
    cube_all('barrow_stone')

    # the wayshrine brazier: a brass bowl on a stand; lit, it holds the Everflame
    for lit in (False, True):
        name = 'wayshrine_brazier' + ('_lit' if lit else '')
        coal = ref('brazier_coals_lit' if lit else 'brazier_coals')
        els = [
            box([2, 0, 2], [14, 3, 14], all_faces('#metal', cull=('down',))),
            box([4, 3, 4], [12, 8, 12], all_faces('#metal')),
            box([1, 8, 1], [15, 12, 15], {f: {'texture': '#metal'} for f in ('north', 'south', 'east', 'west', 'down')}),
            box([2, 10.5, 2], [14, 10.5, 14], {'up': {'texture': '#coal'}}),
            box([1, 12, 1], [15, 12, 2], {'up': {'texture': '#metal'}}),
            box([1, 12, 14], [15, 12, 15], {'up': {'texture': '#metal'}}),
            box([1, 12, 2], [2, 12, 14], {'up': {'texture': '#metal'}}),
            box([14, 12, 2], [15, 12, 14], {'up': {'texture': '#metal'}}),
            # inner walls of the bowl
            box([2, 10.5, 2], [14, 12, 2], {'south': {'texture': '#metal'}}),
            box([2, 10.5, 14], [14, 12, 14], {'north': {'texture': '#metal'}}),
            box([2, 10.5, 2], [2, 12, 14], {'east': {'texture': '#metal'}}),
            box([14, 10.5, 2], [14, 12, 14], {'west': {'texture': '#metal'}}),
        ]
        textures = {'particle': ref('brazier_metal'), 'metal': ref('brazier_metal'), 'coal': coal}
        if lit:
            textures['coal_glow'] = ref('brazier_coals_lit_glow')
            textures['flame'] = ref('everflame')
            els.append(box([2, 10.6, 2], [14, 10.6, 14], {'up': {'texture': '#coal_glow'}}, light_emission=15, shade=False))
            els += flame_cross('#flame', 2.5, 10.5, 13.5, 26.5)
        model(name, {'parent': 'minecraft:block/block', 'textures': textures, 'elements': els})
    write('blockstates/wayshrine_brazier.json', {'variants': {
        'lit=false': {'model': ref('wayshrine_brazier')}, 'lit=true': {'model': ref('wayshrine_brazier_lit')}}})
    item_block('wayshrine_brazier')

    # the chapel bells: a bell on a brass cradle, one colour per tone
    for i in range(4):
        name = f'chapel_bell_{i}'
        model(name, {'parent': 'minecraft:block/block', 'textures': {
            'particle': ref(name), 'bell': ref(name), 'metal': ref('brazier_metal')}, 'elements': [
            box([3, 0, 3], [13, 2, 13], all_faces('#metal', cull=('down',))),
            box([4, 2, 4], [12, 3, 12], all_faces('#bell')),
            box([4.5, 3, 4.5], [11.5, 9, 11.5], all_faces('#bell')),
            box([5.5, 9, 5.5], [10.5, 11, 10.5], all_faces('#bell')),
            box([7, 11, 7], [9, 16, 9], all_faces('#metal', cull=('up',))),
        ]})
    write('blockstates/chapel_bell.json', {'variants': {f'tone={i}': {'model': ref(f'chapel_bell_{i}')} for i in range(4)}})
    item_block('chapel_bell', 'chapel_bell_0')

    # the ward lantern: an iron cage with amber panes that burn when lit
    for lit in (False, True):
        name = 'ward_lantern' + ('_lit' if lit else '')
        pane = ref('ward_lantern_pane_lit' if lit else 'ward_lantern_pane')
        textures = {'particle': ref('brazier_metal'), 'metal': ref('brazier_metal'), 'pane': pane}
        els = [
            box([3, 0, 3], [13, 2, 13], all_faces('#metal', cull=('down',))),
            box([4, 2, 4], [12, 13, 12], {f: {'texture': '#pane'} for f in ('north', 'south', 'east', 'west')}),
            box([4, 12.9, 4], [12, 13, 12], {'up': {'texture': '#metal'}, 'down': {'texture': '#metal'}}),
            box([3.5, 2, 3.5], [4.5, 13, 4.5], all_faces('#metal')),
            box([11.5, 2, 3.5], [12.5, 13, 4.5], all_faces('#metal')),
            box([3.5, 2, 11.5], [4.5, 13, 12.5], all_faces('#metal')),
            box([11.5, 2, 11.5], [12.5, 13, 12.5], all_faces('#metal')),
            box([5, 13, 5], [11, 15, 11], all_faces('#metal')),
            box([7, 15, 7], [9, 16, 9], all_faces('#metal', cull=('up',))),
        ]
        if lit:
            textures['glow'] = ref('ward_lantern_pane_lit_glow')
            els.append(box([4, 2, 4], [12, 13, 12], {f: {'texture': '#glow'} for f in ('north', 'south', 'east', 'west')},
                           light_emission=15, shade=False))
        model(name, {'parent': 'minecraft:block/block', 'textures': textures, 'elements': els})
    write('blockstates/ward_lantern.json', {'variants': {
        'lit=false': {'model': ref('ward_lantern')}, 'lit=true': {'model': ref('ward_lantern_lit')}}})
    item_block('ward_lantern', 'ward_lantern_lit')

    # the cipher lectern: a stone post and a slanted desk holding the cipher-book
    for solved in (False, True):
        name = 'cipher_lectern' + ('_solved' if solved else '')
        book = ref('cipher_book_solved' if solved else 'cipher_book')
        textures = {'particle': ref('arcane_stone'), 'stone': ref('arcane_stone'), 'book': book}
        els = [
            box([4, 0, 4], [12, 2, 12], all_faces('#stone', cull=('down',))),
            box([6, 2, 6], [10, 12, 10], all_faces('#stone')),
            box([1, 12, 1], [15, 15, 15], all_faces('#stone')),
            box([2, 15, 2.5], [14, 15.6, 13.5], {'up': {'texture': '#book'}, 'north': {'texture': '#book', 'uv': [0, 0, 16, 1]},
                                                  'south': {'texture': '#book', 'uv': [0, 15, 16, 16]}}),
        ]
        if solved:
            textures['glow'] = ref('cipher_book_solved_glow')
            els.append(box([2, 15.61, 2.5], [14, 15.61, 13.5], {'up': {'texture': '#glow'}}, light_emission=13, shade=False))
        model(name, {'parent': 'minecraft:block/block', 'textures': textures, 'elements': els})
    variants = {}
    for facing, y in Y_ROT.items():
        for solved in ('false', 'true'):
            v = {'model': ref('cipher_lectern' + ('_solved' if solved == 'true' else ''))}
            if y:
                v['y'] = y
            variants[f'facing={facing},solved={solved}'] = v
    write('blockstates/cipher_lectern.json', {'variants': variants})
    item_block('cipher_lectern')

    # the sarcophagi: carved stone coffins; open, the lid lies slid aside
    variants = {}
    for k in range(3):
        for open_ in (False, True):
            name = f'sarcophagus_{k}' + ('_open' if open_ else '')
            lid = [0, 10, 0], [16, 13, 16]
            els = [box([0, 0, 0], [16, 10, 16], {'north': {'texture': '#front', 'cullface': 'north'}, 'south': {'texture': '#side', 'cullface': 'south'},
                                                 'east': {'texture': '#side', 'cullface': 'east'}, 'west': {'texture': '#side', 'cullface': 'west'},
                                                 'down': {'texture': '#side', 'cullface': 'down'}, 'up': {'texture': '#inside'}})]
            if open_:
                els.append(box([5, 10, -2], [21, 12, 14], all_faces('#lid'), rotation={'origin': [8, 10, 8], 'axis': 'y', 'angle': 22.5}))
            else:
                els.append(box(lid[0], lid[1], all_faces('#lid', cull=('north', 'south', 'east', 'west'))))
            model(name, {'parent': 'minecraft:block/block', 'textures': {
                'particle': ref('barrow_stone'), 'front': ref(f'sarcophagus_{k}'), 'side': ref('barrow_stone'),
                'lid': ref('sarcophagus_top'), 'inside': ref('barrow_stone')}, 'elements': els})
            for facing, y in Y_ROT.items():
                v = {'model': ref(name)}
                if y:
                    v['y'] = y
                variants[f'facing={facing},king={k},open={"true" if open_ else "false"}'] = v
    write('blockstates/sarcophagus.json', {'variants': variants})
    item_block('sarcophagus', 'sarcophagus_0')

    # the Gloam veil: a sheet of the Gloaming hung in the gate
    model('gloam_veil', {'parent': 'minecraft:block/block', 'ambientocclusion': False, 'textures': {
        'particle': ref('gloam_veil'), 'veil': {'sprite': ref('gloam_veil'), 'force_translucent': True}},
        'elements': [box([0, 0, 7.5], [16, 16, 8.5], {'north': {'texture': '#veil'}, 'south': {'texture': '#veil'}},
                         light_emission=11, shade=False)]})
    simple_state('gloam_veil')

    # the wisplight: nothing to see
    model('wisplight', {'textures': {'particle': ref('lumenite_block')}})
    simple_state('wisplight')
    print('blocks written')


def cross(texture, emission=None):
    els = []
    for rot in (45, -45):
        e = {'from': [0.8, 0, 8], 'to': [15.2, 16, 8], 'shade': False,
             'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': rot, 'rescale': True},
             'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': texture}, 'south': {'uv': [0, 0, 16, 16], 'texture': texture}}}
        if emission:
            e['light_emission'] = emission
        els.append(e)
    return els


def flame_cross(texture, lo, y0, hi, y1):
    els = []
    mid = (lo + hi) / 2
    for rot in (45, -45):
        els.append({'from': [lo, y0, mid], 'to': [hi, y1, mid], 'shade': False, 'light_emission': 15,
                    'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': rot, 'rescale': False},
                    'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': texture}, 'south': {'uv': [0, 0, 16, 16], 'texture': texture}}})
    return els


if __name__ == '__main__':
    generate()
