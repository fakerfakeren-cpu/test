"""Generates every JSON resource for Astralfall (assets + data)."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lang_en as L  # noqa

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
A = os.path.join(ROOT, 'assets', 'astralfall')
D = os.path.join(ROOT, 'data', 'astralfall')
M = 'astralfall'


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def clean(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


# ============================================================================ blocks
CUBE_ALL = ['meteorite_rock', 'cooled_meteorite', 'meteorite_bricks', 'starmetal_ore', 'raw_starmetal_block', 'starmetal_block',
            'skyshard_block', 'void_stone', 'astral_bricks', 'cracked_astral_bricks', 'overgrown_astral_bricks',
            'chiseled_astral_bricks', 'sealed_astral_bricks', 'telescope_eyepiece']


def model(name, obj):
    w(f'{A}/models/block/{name}.json', obj)


def blockstate(name, obj):
    w(f'{A}/blockstates/{name}.json', obj)


def item_def(name, model_ref):
    w(f'{A}/items/{name}.json', {'model': {'type': 'minecraft:model', 'model': model_ref}})


def gen_blocks():
    for b in CUBE_ALL:
        model(b, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{M}:block/{b}'}})
        blockstate(b, {'variants': {'': {'model': f'{M}:block/{b}'}}})
        item_def(b, f'{M}:block/{b}')
    # glass: translucent via the sprite flag
    model('astral_glass', {'parent': 'minecraft:block/cube_all', 'textures': {'all': {'sprite': f'{M}:block/astral_glass', 'force_translucent': True}}})
    blockstate('astral_glass', {'variants': {'': {'model': f'{M}:block/astral_glass'}}})
    item_def('astral_glass', f'{M}:block/astral_glass')
    # skyshard cluster (cross)
    model('skyshard_cluster', {'parent': 'minecraft:block/cross', 'textures': {'cross': f'{M}:block/skyshard_cluster'}})
    blockstate('skyshard_cluster', {'variants': {'': {'model': f'{M}:block/skyshard_cluster'}}})
    w(f'{A}/models/item/skyshard_cluster.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{M}:block/skyshard_cluster'}})
    item_def('skyshard_cluster', f'{M}:item/skyshard_cluster')
    # stairs & slab
    tex = {'bottom': f'{M}:block/astral_bricks', 'side': f'{M}:block/astral_bricks', 'top': f'{M}:block/astral_bricks'}
    model('astral_brick_stairs', {'parent': 'minecraft:block/stairs', 'textures': tex})
    model('astral_brick_stairs_inner', {'parent': 'minecraft:block/inner_stairs', 'textures': tex})
    model('astral_brick_stairs_outer', {'parent': 'minecraft:block/outer_stairs', 'textures': tex})
    model('astral_brick_slab', {'parent': 'minecraft:block/slab', 'textures': tex})
    model('astral_brick_slab_top', {'parent': 'minecraft:block/slab_top', 'textures': tex})
    ref = json.load(open('/home/user/ref/26.2-assets-json/assets/minecraft/blockstates/stone_brick_stairs.json'))
    txt = json.dumps(ref).replace('minecraft:block/stone_brick_stairs', f'{M}:block/astral_brick_stairs')
    blockstate('astral_brick_stairs', json.loads(txt))
    blockstate('astral_brick_slab', {'variants': {'type=bottom': {'model': f'{M}:block/astral_brick_slab'},
                                                  'type=double': {'model': f'{M}:block/astral_bricks'},
                                                  'type=top': {'model': f'{M}:block/astral_brick_slab_top'}}})
    item_def('astral_brick_stairs', f'{M}:block/astral_brick_stairs')
    item_def('astral_brick_slab', f'{M}:block/astral_brick_slab')
    # star lock (open/closed)
    model('star_lock', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{M}:block/star_lock'}})
    model('star_lock_open', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{M}:block/star_lock_open'}})
    blockstate('star_lock', {'variants': {'open=false': {'model': f'{M}:block/star_lock'}, 'open=true': {'model': f'{M}:block/star_lock_open'}}})
    item_def('star_lock', f'{M}:block/star_lock')
    # altar
    model('astral_altar', {'parent': 'minecraft:block/cube_bottom_top', 'textures': {'top': f'{M}:block/astral_altar_top', 'side': f'{M}:block/astral_altar_side', 'bottom': f'{M}:block/astral_altar_bottom'}})
    blockstate('astral_altar', {'variants': {'': {'model': f'{M}:block/astral_altar'}}})
    item_def('astral_altar', f'{M}:block/astral_altar')
    # gravity rune & starfire vent (active states)
    for name, top, top_active, side in (('gravity_rune', 'gravity_rune', 'gravity_rune_active', 'astral_bricks'),
                                        ('starfire_vent', 'starfire_vent_top', 'starfire_vent_top_active', 'starfire_vent_side')):
        model(name, {'parent': 'minecraft:block/cube_bottom_top', 'textures': {'top': f'{M}:block/{top}', 'side': f'{M}:block/{side}', 'bottom': f'{M}:block/{side}'}})
        model(name + '_active', {'parent': 'minecraft:block/cube_bottom_top', 'textures': {'top': f'{M}:block/{top_active}', 'side': f'{M}:block/{side}', 'bottom': f'{M}:block/{side}'}})
        blockstate(name, {'variants': {'active=false': {'model': f'{M}:block/{name}'}, 'active=true': {'model': f'{M}:block/{name}_active'}}})
        item_def(name, f'{M}:block/{name}')
    # star jar (custom geometry)
    model('star_jar', {
        'parent': 'minecraft:block/block', 'ambientocclusion': False,
        'textures': {'jar': f'{M}:block/star_jar', 'particle': f'{M}:block/star_jar'},
        'elements': [
            {'from': [6.5, 1.5, 6.5], 'to': [9.5, 4.5, 9.5], 'light_emission': 15,
             'faces': {d: {'uv': [0, 8, 4, 12], 'texture': '#jar'} for d in ('north', 'south', 'east', 'west', 'up', 'down')}},
            {'from': [5, 0, 5], 'to': [11, 8, 11],
             'faces': {**{d: {'uv': [0, 0, 6, 8], 'texture': '#jar'} for d in ('north', 'south', 'east', 'west')},
                       'down': {'uv': [8, 8, 14, 14], 'texture': '#jar'}}},
            {'from': [5.5, 8, 5.5], 'to': [10.5, 10, 10.5],
             'faces': {**{d: {'uv': [8, 6, 13, 8], 'texture': '#jar'} for d in ('north', 'south', 'east', 'west')},
                       'up': {'uv': [8, 0, 13, 5], 'texture': '#jar'}, 'down': {'uv': [8, 0, 13, 5], 'texture': '#jar'}}},
        ]})
    blockstate('star_jar', {'variants': {'': {'model': f'{M}:block/star_jar'}}})
    item_def('star_jar', f'{M}:block/star_jar')
    # fallen star (glowing crystal star)
    fs = f'{M}:block/fallen_star'
    faces = {d: {'uv': [0, 0, 16, 16], 'texture': '#star'} for d in ('north', 'south', 'east', 'west', 'up', 'down')}
    model('fallen_star_block', {
        'parent': 'minecraft:block/block', 'ambientocclusion': False,
        'textures': {'star': fs, 'particle': fs},
        'elements': [
            {'from': [5, 0, 5], 'to': [11, 6, 11], 'light_emission': 15, 'faces': faces,
             'rotation': {'origin': [8, 3, 8], 'axis': 'y', 'angle': 45}},
            {'from': [7, 0, 4], 'to': [9, 9, 12], 'light_emission': 15, 'faces': faces,
             'rotation': {'origin': [8, 4, 8], 'axis': 'x', 'angle': 22.5}},
            {'from': [4, 1, 7], 'to': [12, 7, 9], 'light_emission': 15, 'faces': faces,
             'rotation': {'origin': [8, 4, 8], 'axis': 'z', 'angle': -22.5}},
        ]})
    blockstate('fallen_star_block', {'variants': {'': {'model': f'{M}:block/fallen_star_block'}}})
    item_def('fallen_star_block', f'{M}:block/fallen_star_block')


# ============================================================================ items
GENERATED = ['astral_journal', 'raw_starmetal', 'starmetal_ingot', 'starmetal_nugget', 'skyshard', 'stardust', 'void_essence',
             'fallen_star', 'stellar_core', 'eclipse_sigil', 'singularity_grenade', 'gravity_gauntlet',
             'starmetal_helmet', 'starmetal_chestplate', 'starmetal_leggings', 'starmetal_boots',
             'voidwalker_helmet', 'voidwalker_chestplate', 'voidwalker_leggings', 'voidwalker_boots',
             'crown_of_astraeus', 'nebula_wings',
             'astral_wisp_spawn_egg', 'void_stalker_spawn_egg', 'meteorite_crawler_spawn_egg', 'void_gazer_spawn_egg', 'astraeus_spawn_egg']
HANDHELD = ['starblade', 'comet_maul', 'riftcaller', 'eclipse_greatsword', 'starmetal_pickaxe']


def gen_items():
    for n in GENERATED:
        w(f'{A}/models/item/{n}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{M}:item/{n}'}})
        item_def(n, f'{M}:item/{n}')
    for n in HANDHELD:
        w(f'{A}/models/item/{n}.json', {'parent': 'minecraft:item/handheld', 'textures': {'layer0': f'{M}:item/{n}'}})
        item_def(n, f'{M}:item/{n}')
    # bow with pulling states
    bow_ref = json.load(open('/home/user/ref/26.2-assets-json/assets/minecraft/models/item/bow.json'))
    for suffix in ('', '_pulling_0', '_pulling_1', '_pulling_2'):
        obj = dict(bow_ref) if suffix == '' else {'parent': f'{M}:item/constellation_bow'}
        obj['textures'] = {'layer0': f'{M}:item/constellation_bow{suffix}'}
        w(f'{A}/models/item/constellation_bow{suffix}.json', obj)
    w(f'{A}/items/constellation_bow.json', {'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:using_item',
        'on_false': {'type': 'minecraft:model', 'model': f'{M}:item/constellation_bow'},
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                    'entries': [{'threshold': 0.65, 'model': {'type': 'minecraft:model', 'model': f'{M}:item/constellation_bow_pulling_1'}},
                                {'threshold': 0.9, 'model': {'type': 'minecraft:model', 'model': f'{M}:item/constellation_bow_pulling_2'}}],
                    'fallback': {'type': 'minecraft:model', 'model': f'{M}:item/constellation_bow_pulling_0'}}}})
    # compass: 32 needle frames, spins until it has a target
    entries = []
    for i in range(33):
        frame = (i + 16) % 32
        entries.append({'threshold': 0.0 if i == 0 else i - 0.5, 'model': {'type': 'minecraft:model', 'model': f'{M}:item/astral_compass_{frame:02d}'}})
    for i in range(32):
        w(f'{A}/models/item/astral_compass_{i:02d}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{M}:item/astral_compass_{i:02d}'}})
    w(f'{A}/items/astral_compass.json', {'model': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:compass', 'target': 'lodestone', 'scale': 32.0, 'entries': entries}})


def gen_equipment():
    w(f'{A}/equipment/starmetal.json', {'layers': {'humanoid': [{'texture': f'{M}:starmetal'}], 'humanoid_leggings': [{'texture': f'{M}:starmetal'}]}})
    w(f'{A}/equipment/voidwalker.json', {'layers': {'humanoid': [{'texture': f'{M}:voidwalker'}], 'humanoid_leggings': [{'texture': f'{M}:voidwalker'}]}})
    w(f'{A}/equipment/crown_of_astraeus.json', {'layers': {'humanoid': [{'texture': f'{M}:crown_of_astraeus'}]}})
    w(f'{A}/equipment/nebula_wings.json', {'layers': {'wings': [{'texture': f'{M}:nebula_wings'}]}})


PARTICLES = {'star_sparkle': 4, 'gold_sparkle': 4, 'void_mote': 4, 'comet_trail': 4}


def gen_particles():
    for n, frames in PARTICLES.items():
        w(f'{A}/particles/{n}.json', {'textures': [f'{M}:{n}_{i}' for i in range(frames)]})


SOUNDS = {  # event -> (files, volume)
    'meteor_incoming': (['meteor_incoming1', 'meteor_incoming2'], 1.0), 'meteor_impact': (['meteor_impact1', 'meteor_impact2'], 1.0),
    'star_chime': (['star_chime1', 'star_chime2', 'star_chime3'], 0.8), 'starstorm': (['starstorm'], 1.0),
    'wisp_ambient': (['wisp_ambient1', 'wisp_ambient2'], 0.6), 'wisp_hurt': (['wisp_hurt'], 0.8),
    'stalker_ambient': (['stalker_ambient1', 'stalker_ambient2'], 1.0), 'stalker_scream': (['stalker_scream'], 1.0),
    'stalker_blink': (['stalker_blink'], 1.0), 'crawler_roll': (['crawler_roll'], 1.0), 'crawler_hurt': (['crawler_hurt'], 1.0),
    'gazer_charge': (['gazer_charge'], 1.0), 'gazer_beam': (['gazer_beam'], 1.0), 'boss_roar': (['boss_roar1', 'boss_roar2'], 1.0),
    'boss_summon': (['boss_summon'], 1.0), 'boss_beam': (['boss_beam'], 1.0), 'boss_death': (['boss_death'], 1.0),
    'shockwave': (['shockwave'], 1.0), 'singularity_hum': (['singularity_hum'], 1.0), 'singularity_collapse': (['singularity_collapse'], 1.0),
    'star_slash': (['star_slash1', 'star_slash2'], 1.0), 'star_bolt': (['star_bolt'], 0.8), 'gravity_grab': (['gravity_grab'], 1.0),
    'gravity_throw': (['gravity_throw'], 1.0), 'void_blink': (['void_blink'], 1.0), 'eclipse_nova': (['eclipse_nova'], 1.0),
    'vault_open': (['vault_open'], 1.0),
}


def gen_sounds():
    out = {}
    for ev, (files, vol) in SOUNDS.items():
        out[ev] = {'subtitle': f'subtitles.{M}.{ev}', 'sounds': [{'name': f'{M}:{f}', 'volume': vol} for f in files]}
    w(f'{A}/sounds.json', out)


def gen_lang():
    lang = {}
    lang.update(L.NAMES)
    lang.update(L.TOOLTIPS)
    lang.update(L.MESSAGES)
    for k, v in L.SUBTITLES.items():
        lang[f'subtitles.{M}.{k}'] = v
    lang['book.astralfall.journal.title'] = 'ASTRAL JOURNAL'
    lang['book.astralfall.journal.toc_hint'] = 'Click a chapter to jump to it.'
    chapters = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
    for key, (title, page) in zip(chapters, L.TOC):
        lang[f'book.astralfall.journal.chapter.{key}'] = f'{title}  ({page})'
    lang['book.astralfall.journal.quickstart'] = (
        "§5§lQuick Start§r\n\n1. Survive to §lnight§r.\n2. Watch for §6falling stars§r.\n3. Mine the crater's glowing core.\n"
        "4. Smelt §9Starmetal§r.\n5. Forge a §bStarblade§r.\n6. Follow the quests: press §lL§r.")
    for i, page in enumerate(L.JOURNAL, start=1):
        lang[f'book.astralfall.journal.page{i}'] = page
    for q in L.QUESTS:
        lang[f'quest.astralfall.{q[0]}.title'] = q[3]
        lang[f'quest.astralfall.{q[0]}.description'] = q[4]
        lang[f'quest.astralfall.{q[0]}.hint'] = L.QUEST_HINTS[q[0]]
    lang.update(L.JOURNAL_UI)
    w(f'{A}/lang/en_us.json', lang)
    assert len(L.JOURNAL) == 29, len(L.JOURNAL)


# ============================================================================ data: loot
def item_entry(name, count=None, fns=None, weight=None):
    e = {'type': 'minecraft:item', 'name': name}
    f = list(fns or [])
    if count is not None:
        if isinstance(count, tuple):
            f.insert(0, {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': float(count[0]), 'max': float(count[1])}})
        else:
            f.insert(0, {'function': 'minecraft:set_count', 'count': float(count)})
    if f:
        e['functions'] = f
    if weight is not None:
        e['weight'] = weight
    return e


SILK = {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {'minecraft:enchantments': [{'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}


def block_loot(name, pools):
    w(f'{D}/loot_table/blocks/{name}.json', {'type': 'minecraft:block', 'pools': pools, 'random_sequence': f'{M}:blocks/{name}'})


def gen_loot():
    self_drop = ['meteorite_rock', 'cooled_meteorite', 'meteorite_bricks', 'raw_starmetal_block', 'starmetal_block', 'skyshard_block',
                 'void_stone', 'astral_bricks', 'cracked_astral_bricks', 'overgrown_astral_bricks', 'chiseled_astral_bricks',
                 'astral_brick_stairs', 'astral_altar', 'star_jar', 'gravity_rune', 'starfire_vent', 'telescope_eyepiece']
    for b in self_drop:
        block_loot(b, [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:{b}'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}])
    block_loot('astral_brick_slab', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:astral_brick_slab', 'functions': [
        {'function': 'minecraft:set_count', 'count': 2.0, 'add': False, 'conditions': [{'condition': 'minecraft:block_state_property', 'block': f'{M}:astral_brick_slab', 'properties': {'type': 'double'}}]},
        {'function': 'minecraft:explosion_decay'}]}]}])
    block_loot('astral_glass', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:astral_glass'}], 'conditions': [SILK]}])
    block_loot('starmetal_ore', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [
        {'type': 'minecraft:item', 'name': f'{M}:starmetal_ore', 'conditions': [SILK]},
        {'type': 'minecraft:item', 'name': f'{M}:raw_starmetal', 'functions': [
            {'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'},
            {'function': 'minecraft:explosion_decay'}]}]}]}])
    block_loot('skyshard_cluster', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [
        {'type': 'minecraft:item', 'name': f'{M}:skyshard_cluster', 'conditions': [SILK]},
        {'type': 'minecraft:item', 'name': f'{M}:skyshard', 'functions': [
            {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 2.0, 'max': 4.0}},
            {'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'},
            {'function': 'minecraft:explosion_decay'}]}]}]}])
    block_loot('fallen_star_block', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:fallen_star'}]},
                                     {'rolls': 1.0, 'entries': [item_entry(f'{M}:stardust', (2, 5))]}])

    def looting(lo, hi):
        return [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': float(lo), 'max': float(hi)}},
                {'function': 'minecraft:enchanted_count_increase', 'enchantment': 'minecraft:looting', 'count': {'type': 'minecraft:uniform', 'min': 0.0, 'max': 1.0}}]

    def ent(name, pools):
        w(f'{D}/loot_table/entities/{name}.json', {'type': 'minecraft:entity', 'pools': pools, 'random_sequence': f'{M}:entities/{name}'})

    kill = {'condition': 'minecraft:killed_by_player'}
    ent('astral_wisp', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:stardust', 'functions': looting(1, 3)}]}])
    ent('void_stalker', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:void_essence', 'functions': looting(1, 2)}]},
                         {'rolls': 1.0, 'conditions': [kill, {'condition': 'minecraft:random_chance', 'chance': 0.15}], 'entries': [{'type': 'minecraft:item', 'name': f'{M}:skyshard'}]}])
    ent('meteorite_crawler', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:raw_starmetal', 'functions': looting(1, 2)}]},
                              {'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:meteorite_rock', 'functions': looting(0, 2)}]}])
    ent('void_gazer', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:void_essence', 'functions': looting(0, 1)}]},
                       {'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': f'{M}:skyshard', 'functions': looting(1, 2)}]}])
    ent('astraeus', [
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:stellar_core')]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:eclipse_greatsword')]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:crown_of_astraeus')]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:starmetal_ingot', (8, 16))]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:skyshard', (8, 16))]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:fallen_star', (1, 2))]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:star_jar', 2)]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:void_essence', (4, 8))]},
    ])

    def chest(name, pools):
        w(f'{D}/loot_table/chests/{name}.json', {'type': 'minecraft:chest', 'pools': pools, 'random_sequence': f'{M}:chests/{name}'})

    common = [item_entry(f'{M}:starmetal_ingot', (1, 4), weight=15), item_entry(f'{M}:raw_starmetal', (2, 5), weight=15),
              item_entry(f'{M}:skyshard', (2, 6), weight=15), item_entry(f'{M}:stardust', (2, 8), weight=12),
              item_entry('minecraft:book', (1, 3), weight=10), item_entry('minecraft:bread', (2, 5), weight=10),
              item_entry('minecraft:ender_pearl', (1, 2), weight=5), item_entry(f'{M}:astral_compass', weight=4),
              item_entry(f'{M}:star_jar', weight=4), item_entry('minecraft:golden_apple', weight=3)]
    chest('observatory_common', [{'rolls': {'type': 'minecraft:uniform', 'min': 4.0, 'max': 7.0}, 'entries': common}])
    chest('observatory_library', [
        {'rolls': {'type': 'minecraft:uniform', 'min': 3.0, 'max': 6.0}, 'entries': common + [
            item_entry(f'{M}:void_essence', (1, 3), weight=12),
            item_entry('minecraft:book', 1, fns=[{'function': 'minecraft:enchant_randomly'}], weight=12),
            item_entry(f'{M}:singularity_grenade', (1, 3), weight=6)]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:astral_journal', weight=1), {'type': 'minecraft:empty', 'weight': 2}]}])
    chest('observatory_vault', [
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:constellation_bow')]},
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:fallen_star')]},
        {'rolls': {'type': 'minecraft:uniform', 'min': 3.0, 'max': 5.0}, 'entries': [
            item_entry(f'{M}:starmetal_ingot', (3, 8), weight=10), item_entry(f'{M}:void_essence', (2, 5), weight=10),
            item_entry(f'{M}:skyshard', (4, 10), weight=10), item_entry('minecraft:diamond', (1, 3), weight=6),
            item_entry(f'{M}:singularity_grenade', (2, 4), weight=6), item_entry('minecraft:enchanted_golden_apple', weight=1),
            item_entry(f'{M}:nebula_wings', weight=1), item_entry(f'{M}:voidwalker_helmet', weight=2), item_entry(f'{M}:voidwalker_boots', weight=2)]}])
    chest('fallen_vessel', [
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:gravity_gauntlet', weight=3), item_entry(f'{M}:singularity_grenade', (3, 6), weight=2)]},
        {'rolls': {'type': 'minecraft:uniform', 'min': 3.0, 'max': 6.0}, 'entries': [
            item_entry(f'{M}:starmetal_ingot', (2, 6), weight=15), item_entry(f'{M}:raw_starmetal', (3, 8), weight=15),
            item_entry(f'{M}:void_essence', (1, 3), weight=10), item_entry(f'{M}:skyshard', (2, 6), weight=10),
            item_entry('minecraft:iron_ingot', (3, 8), weight=10), item_entry('minecraft:redstone', (4, 12), weight=8),
            item_entry(f'{M}:singularity_grenade', (1, 3), weight=8), item_entry(f'{M}:comet_maul', weight=2)]}])
    chest('sky_shrine', [
        {'rolls': 1.0, 'entries': [item_entry(f'{M}:nebula_wings', weight=1), item_entry(f'{M}:fallen_star', weight=2), item_entry(f'{M}:eclipse_sigil', weight=1)]},
        {'rolls': {'type': 'minecraft:uniform', 'min': 3.0, 'max': 5.0}, 'entries': [
            item_entry(f'{M}:stardust', (4, 12), weight=15), item_entry(f'{M}:skyshard', (3, 8), weight=15),
            item_entry(f'{M}:star_jar', (1, 2), weight=8), item_entry('minecraft:golden_apple', (1, 2), weight=6),
            item_entry('minecraft:phantom_membrane', (1, 3), weight=8), item_entry(f'{M}:void_essence', (1, 4), weight=10)]}])

    def reward(name, entries):
        w(f'{D}/loot_table/quests/{name}.json', {'type': 'minecraft:advancement_reward', 'pools': [{'rolls': 1.0, 'entries': [e]} for e in entries]})

    reward('journal', [item_entry(f'{M}:astral_journal')])
    reward('first_light', [item_entry(f'{M}:stardust', 4), item_entry('minecraft:torch', 8)])
    reward('fallen_star', [item_entry(f'{M}:stardust', 8)])
    reward('observatory', [item_entry(f'{M}:singularity_grenade', 2)])


# ============================================================================ data: recipes
def shaped(name, pattern, key, result, count=1, category='misc'):
    w(f'{D}/recipe/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': category, 'pattern': pattern,
                                  'key': key, 'result': {'id': result, 'count': count}})


def shapeless(name, ingredients, result, count=1, category='misc'):
    w(f'{D}/recipe/{name}.json', {'type': 'minecraft:crafting_shapeless', 'category': category, 'ingredients': ingredients,
                                  'result': {'id': result, 'count': count}})


def cooking(name, kind, ingredient, result, xp):
    w(f'{D}/recipe/{name}.json', {'type': f'minecraft:{kind}', 'category': 'misc', 'ingredient': ingredient, 'result': {'id': result}, 'experience': xp})


def gen_recipes():
    m = lambda n: f'{M}:{n}'  # noqa
    for kind in ('smelting', 'blasting'):
        cooking(f'starmetal_ingot_from_{kind}_raw', kind, m('raw_starmetal'), m('starmetal_ingot'), 1.0)
        cooking(f'starmetal_ingot_from_{kind}_ore', kind, m('starmetal_ore'), m('starmetal_ingot'), 1.0)
    cooking('cracked_astral_bricks', 'smelting', m('astral_bricks'), m('cracked_astral_bricks'), 0.1)
    cooking('cooled_meteorite', 'smelting', m('meteorite_rock'), m('cooled_meteorite'), 0.1)
    shaped('starmetal_block', ['III', 'III', 'III'], {'I': m('starmetal_ingot')}, m('starmetal_block'), category='building')
    shapeless('starmetal_ingot_from_block', [m('starmetal_block')], m('starmetal_ingot'), 9)
    shaped('raw_starmetal_block', ['III', 'III', 'III'], {'I': m('raw_starmetal')}, m('raw_starmetal_block'), category='building')
    shapeless('raw_starmetal_from_block', [m('raw_starmetal_block')], m('raw_starmetal'), 9)
    shaped('starmetal_ingot_from_nuggets', ['NNN', 'NNN', 'NNN'], {'N': m('starmetal_nugget')}, m('starmetal_ingot'))
    shapeless('starmetal_nugget', [m('starmetal_ingot')], m('starmetal_nugget'), 9)
    shaped('skyshard_block', ['SS', 'SS'], {'S': m('skyshard')}, m('skyshard_block'), category='building')
    shapeless('stardust', [m('skyshard')], m('stardust'), 2)
    shaped('astral_bricks', ['BBB', 'BSB', 'BBB'], {'B': 'minecraft:stone_bricks', 'S': m('skyshard')}, m('astral_bricks'), 8, 'building')
    shaped('chiseled_astral_bricks', ['S', 'S'], {'S': m('astral_brick_slab')}, m('chiseled_astral_bricks'), category='building')
    shaped('astral_brick_stairs', ['B  ', 'BB ', 'BBB'], {'B': m('astral_bricks')}, m('astral_brick_stairs'), 4, 'building')
    shaped('astral_brick_slab', ['BBB'], {'B': m('astral_bricks')}, m('astral_brick_slab'), 6, 'building')
    shaped('overgrown_astral_bricks', ['BV'], {'B': m('astral_bricks'), 'V': 'minecraft:vine'}, m('overgrown_astral_bricks'), category='building')
    shaped('astral_glass', ['GGG', 'GSG', 'GGG'], {'G': 'minecraft:glass', 'S': m('skyshard')}, m('astral_glass'), 8, 'building')
    shaped('meteorite_bricks', ['MM', 'MM'], {'M': m('cooled_meteorite')}, m('meteorite_bricks'), 4, 'building')
    shapeless('void_stone', [m('cooled_meteorite'), m('cooled_meteorite'), m('cooled_meteorite'), m('cooled_meteorite'), m('void_essence')], m('void_stone'), 4)
    shaped('star_jar', [' N ', 'GSG', 'GGG'], {'N': 'minecraft:gold_nugget', 'G': 'minecraft:glass', 'S': m('stardust')}, m('star_jar'), category='building')
    shaped('astral_altar', ['K K', 'CBC', 'CCC'], {'K': m('skyshard'), 'C': m('chiseled_astral_bricks'), 'B': m('starmetal_block')}, m('astral_altar'), category='building')
    shaped('gravity_rune', ['V', 'B'], {'V': m('void_essence'), 'B': m('astral_bricks')}, m('gravity_rune'), 2, 'redstone')
    shaped('starfire_vent', ['F', 'M'], {'F': 'minecraft:fire_charge', 'M': m('meteorite_rock')}, m('starfire_vent'), 2, 'redstone')
    shaped('telescope_eyepiece', ['GKG', 'IBI'], {'G': 'minecraft:gold_ingot', 'K': m('astral_glass'), 'I': m('starmetal_ingot'), 'B': m('starmetal_block')}, m('telescope_eyepiece'), category='building')
    # tools and weapons
    eq = 'equipment'
    shaped('starblade', ['K', 'I', 'T'], {'K': m('skyshard'), 'I': m('starmetal_ingot'), 'T': 'minecraft:stick'}, m('starblade'), category=eq)
    shaped('comet_maul', ['MBM', ' T ', ' T '], {'M': m('meteorite_rock'), 'B': m('starmetal_block'), 'T': 'minecraft:stick'}, m('comet_maul'), category=eq)
    shaped('riftcaller', ['VVI', ' TV', 'T  '], {'V': m('void_essence'), 'I': m('starmetal_ingot'), 'T': 'minecraft:stick'}, m('riftcaller'), category=eq)
    shaped('constellation_bow', [' IS', 'K S', ' IS'], {'I': m('starmetal_ingot'), 'S': 'minecraft:string', 'K': m('skyshard_block')}, m('constellation_bow'), category=eq)
    shaped('starmetal_pickaxe', ['III', ' T ', ' T '], {'I': m('starmetal_ingot'), 'T': 'minecraft:stick'}, m('starmetal_pickaxe'), category=eq)
    shaped('eclipse_greatsword', ['F', 'C', 'S'], {'F': m('fallen_star'), 'C': m('stellar_core'), 'S': m('starblade')}, m('eclipse_greatsword'), category=eq)
    shaped('gravity_gauntlet', ['IVI', 'IKI', ' I '], {'I': m('starmetal_ingot'), 'V': m('void_essence'), 'K': m('skyshard')}, m('gravity_gauntlet'), category=eq)
    shaped('singularity_grenade', [' N ', 'NVN', ' G '], {'N': m('starmetal_nugget'), 'V': m('void_essence'), 'G': 'minecraft:gunpowder'}, m('singularity_grenade'), 2, eq)
    shaped('astral_compass', [' K ', 'KCK', ' K '], {'K': m('skyshard'), 'C': 'minecraft:compass'}, m('astral_compass'), category=eq)
    shaped('eclipse_sigil', ['VKV', 'KFK', 'VKV'], {'V': m('void_essence'), 'K': m('skyshard'), 'F': m('fallen_star')}, m('eclipse_sigil'))
    shaped('nebula_wings', ['VKV', 'PCP', 'V V'], {'V': m('void_essence'), 'K': m('skyshard'), 'P': 'minecraft:phantom_membrane', 'C': m('stellar_core')}, m('nebula_wings'), category=eq)
    shapeless('astral_journal', ['minecraft:book', 'minecraft:gold_nugget'], m('astral_journal'))
    shapeless('astral_journal_from_stardust', ['minecraft:book', m('stardust')], m('astral_journal'))
    # armour
    shapes = {'helmet': ['XXX', 'X X'], 'chestplate': ['X X', 'XXX', 'XXX'], 'leggings': ['XXX', 'X X', 'X X'], 'boots': ['X X', 'X X']}
    for piece, pat in shapes.items():
        shaped(f'starmetal_{piece}', pat, {'X': m('starmetal_ingot')}, m(f'starmetal_{piece}'), category=eq)
    shaped('voidwalker_helmet', ['VIV', 'V V'], {'V': m('void_essence'), 'I': m('starmetal_ingot')}, m('voidwalker_helmet'), category=eq)
    shaped('voidwalker_chestplate', ['V V', 'VIV', 'VVV'], {'V': m('void_essence'), 'I': m('starmetal_ingot')}, m('voidwalker_chestplate'), category=eq)
    shaped('voidwalker_leggings', ['VIV', 'V V', 'V V'], {'V': m('void_essence'), 'I': m('starmetal_ingot')}, m('voidwalker_leggings'), category=eq)
    shaped('voidwalker_boots', ['V V', 'I I'], {'V': m('void_essence'), 'I': m('starmetal_ingot')}, m('voidwalker_boots'), category=eq)


# ============================================================================ data: tags
def tag(kind, ns, name, values, replace=False):
    w(os.path.join(ROOT, 'data', ns, 'tags', kind, name + '.json'), {'replace': replace, 'values': values})


def gen_tags():
    m = lambda n: f'{M}:{n}'  # noqa
    pick = ['meteorite_rock', 'cooled_meteorite', 'meteorite_bricks', 'starmetal_ore', 'raw_starmetal_block', 'starmetal_block', 'skyshard_block',
            'skyshard_cluster', 'void_stone', 'astral_bricks', 'cracked_astral_bricks', 'overgrown_astral_bricks', 'chiseled_astral_bricks',
            'astral_brick_stairs', 'astral_brick_slab', 'astral_altar', 'gravity_rune', 'starfire_vent', 'telescope_eyepiece']
    tag('block', 'minecraft', 'mineable/pickaxe', [m(b) for b in pick])
    tag('block', 'minecraft', 'needs_iron_tool', [m(b) for b in ('meteorite_rock', 'starmetal_ore', 'raw_starmetal_block', 'starmetal_block', 'void_stone')])
    tag('block', 'minecraft', 'stairs', [m('astral_brick_stairs')])
    tag('block', 'minecraft', 'slabs', [m('astral_brick_slab')])
    tag('item', M, 'starmetal_repair', [m('starmetal_ingot')])
    tag('item', M, 'voidwalker_repair', [m('void_essence')])
    tag('item', 'minecraft', 'swords', [m(n) for n in ('starblade', 'comet_maul', 'riftcaller', 'eclipse_greatsword')])
    tag('item', 'minecraft', 'pickaxes', [m('starmetal_pickaxe')])
    tag('item', 'minecraft', 'head_armor', [m(n) for n in ('starmetal_helmet', 'voidwalker_helmet', 'crown_of_astraeus')])
    tag('item', 'minecraft', 'chest_armor', [m(n) for n in ('starmetal_chestplate', 'voidwalker_chestplate')])
    tag('item', 'minecraft', 'leg_armor', [m(n) for n in ('starmetal_leggings', 'voidwalker_leggings')])
    tag('item', 'minecraft', 'foot_armor', [m(n) for n in ('starmetal_boots', 'voidwalker_boots')])
    tag('item', 'minecraft', 'trimmable_armor', [m(f'{s}_{p}') for s in ('starmetal', 'voidwalker') for p in ('helmet', 'chestplate', 'leggings', 'boots')])
    tag('item', 'minecraft', 'enchantable/durability', [m(n) for n in ('constellation_bow', 'gravity_gauntlet', 'nebula_wings')])
    tag('item', 'minecraft', 'enchantable/equippable', [m('nebula_wings')])
    tag('item', 'minecraft', 'enchantable/bow', [m('constellation_bow')])
    tag('item', 'minecraft', 'stairs', [m('astral_brick_stairs')])
    tag('item', 'minecraft', 'slabs', [m('astral_brick_slab')])
    # Meteors only carve natural terrain, so craters never eat into player builds (pack makers can extend this).
    tag('block', M, 'meteor_carvable', ['#minecraft:overworld_carver_replaceables', '#minecraft:replaceable', '#minecraft:leaves',
        '#minecraft:flowers', '#minecraft:dirt', '#minecraft:sand', '#minecraft:base_stone_overworld', '#minecraft:terracotta',
        '#minecraft:snow', 'minecraft:gravel', 'minecraft:clay', 'minecraft:sandstone', 'minecraft:red_sandstone', 'minecraft:ice',
        'minecraft:packed_ice', 'minecraft:magma_block', 'minecraft:blackstone', 'minecraft:coarse_dirt', 'minecraft:sweet_berry_bush',
        'minecraft:cactus', 'minecraft:pumpkin', 'minecraft:melon']
        + [m(b) for b in ('meteorite_rock', 'cooled_meteorite', 'starmetal_ore', 'skyshard_cluster', 'void_stone')])
    tag('entity_type', M, 'void_creatures', [m('void_stalker'), m('void_gazer')])
    tag('worldgen/structure', M, 'observatory', [m('shattered_observatory')])
    tag('worldgen/structure', M, 'fallen_vessel', [m('fallen_vessel')])
    tag('worldgen/structure', M, 'sky_shrine', [m('sky_shrine')])
    open_land = ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:savanna', 'minecraft:savanna_plateau',
                 'minecraft:snowy_plains', 'minecraft:desert', 'minecraft:badlands', 'minecraft:eroded_badlands']
    tag('worldgen/biome', M, 'has_structure/observatory', open_land)
    tag('worldgen/biome', M, 'has_structure/fallen_vessel', open_land + ['minecraft:forest', 'minecraft:birch_forest', 'minecraft:taiga', 'minecraft:snowy_taiga', 'minecraft:wooded_badlands'])
    tag('worldgen/biome', M, 'has_structure/sky_shrine', ['#minecraft:is_overworld'])
    tag('worldgen/biome', M, 'has_impact_sites', open_land + ['minecraft:forest', 'minecraft:taiga', 'minecraft:snowy_taiga', 'minecraft:windswept_hills'])


# ============================================================================ data: worldgen
def gen_worldgen():
    structures = {  # name: (blueprint, biome tag, y_offset, spacing, separation, salt)
        'shattered_observatory': ('observatory', 'observatory', 0, 32, 12, 1946723),
        'fallen_vessel': ('fallen_vessel', 'fallen_vessel', -2, 28, 10, 88112201),
        'sky_shrine': ('sky_shrine', 'sky_shrine', 62, 34, 12, 5533117),
    }
    for name, (bp, biomes, yoff, spacing, sep, salt) in structures.items():
        w(f'{D}/worldgen/structure/{name}.json', {'type': f'{M}:blueprint', 'biomes': f'#{M}:has_structure/{biomes}',
                                                  'spawn_overrides': {}, 'step': 'surface_structures', 'terrain_adaptation': 'none',
                                                  'blueprint': bp, 'y_offset': yoff})
        w(f'{D}/worldgen/structure_set/{name}.json', {'structures': [{'structure': f'{M}:{name}', 'weight': 1}],
                                                      'placement': {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}})
    w(f'{D}/worldgen/configured_feature/impact_site.json', {'type': f'{M}:impact_site', 'config': {}})
    w(f'{D}/worldgen/placed_feature/impact_site.json', {'feature': f'{M}:impact_site', 'placement': [
        {'type': 'minecraft:rarity_filter', 'chance': 48},
        {'type': 'minecraft:in_square'},
        {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'},
        {'type': 'minecraft:biome'}]})
    bm = os.path.join(D, 'forge', 'biome_modifier')
    w(f'{bm}/impact_sites.json', {'type': 'forge:add_features', 'biomes': f'#{M}:has_impact_sites', 'features': f'{M}:impact_site', 'step': 'local_modifications'})
    w(f'{bm}/void_spawns.json', {'type': 'forge:add_spawns', 'biomes': '#minecraft:is_overworld', 'spawners': [
        {'type': f'{M}:void_stalker', 'weight': 12, 'minCount': 1, 'maxCount': 1},
        {'type': f'{M}:void_gazer', 'weight': 8, 'minCount': 1, 'maxCount': 2},
        {'type': f'{M}:meteorite_crawler', 'weight': 6, 'minCount': 1, 'maxCount': 1}]})
    w(f'{bm}/wisp_spawns.json', {'type': 'forge:add_spawns', 'biomes': f'#{M}:has_impact_sites', 'spawners': [
        {'type': f'{M}:astral_wisp', 'weight': 10, 'minCount': 1, 'maxCount': 3}]})


# ============================================================================ data: quests
def criteria(spec):
    kind = spec[0]
    if kind == 'tick':
        return {'unlock': {'trigger': 'minecraft:tick'}}, [['unlock']]
    if kind == 'item':
        return {'got': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': spec[1]}]}}}, [['got']]
    if kind == 'any_item':
        c = {f'got_{i}': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': it}]}} for i, it in enumerate(spec[1])}
        return c, [list(c.keys())]
    if kind == 'all_items':
        c = {f'got_{i}': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': it}]}} for i, it in enumerate(spec[1])}
        return c, [[k] for k in c]
    if kind == 'kill':
        return {'kill': {'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:entity_type': spec[1]}}]}}}, [['kill']]
    if kind == 'tame':
        return {'tame': {'trigger': 'minecraft:tame_animal', 'conditions': {'entity': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:entity_type': spec[1]}}]}}}, [['tame']]
    if kind == 'structure':
        return {'found': {'trigger': 'minecraft:location', 'conditions': {'player': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:location': {'structures': spec[1]}}}]}}}, [['found']]
    raise ValueError(kind)


def gen_quests():
    for qid, parent, icon, title, desc, frame, xp, loot, spec in L.QUESTS:
        crit, req = criteria(spec)
        display = {'icon': {'id': icon}, 'title': {'translate': f'quest.{M}.{qid}.title'},
                   'description': {'translate': f'quest.{M}.{qid}.description'}, 'frame': frame,
                   'show_toast': True, 'announce_to_chat': qid != 'root', 'hidden': False}
        if parent is None:
            display['background'] = f'{M}:block/astral_bricks'
        adv = {'display': display, 'criteria': crit, 'requirements': req}
        if parent:
            adv['parent'] = f'{M}:quests/{parent}'
        # Quest rewards (items + XP) are claimed from the Astral Journal (QuestLog.java); only the root
        # quest hands out the journal itself on first join.
        if parent is None:
            adv['rewards'] = {'loot': [f'{M}:quests/journal']}
        w(f'{D}/advancement/quests/{qid}.json', adv)
        # Hidden per-player marker the server awards when this quest's reward has been claimed.
        w(f'{D}/advancement/claimed/{qid}.json', {
            'criteria': {'claimed': {'trigger': 'minecraft:impossible'}},
            'requirements': [['claimed']]})
    # Hidden helper: unlock every Astralfall recipe in the recipe book on first join.
    recipes = sorted(f'{M}:' + f[:-5] for f in os.listdir(f'{D}/recipe') if f.endswith('.json'))
    w(f'{D}/advancement/recipes/unlock_all.json', {
        'criteria': {'joined': {'trigger': 'minecraft:tick'}},
        'requirements': [['joined']],
        'rewards': {'recipes': recipes}})


def main():
    for d in ('blockstates', 'models', 'items', 'equipment', 'particles', 'lang'):
        clean(os.path.join(A, d))
    for d in ('loot_table', 'recipe', 'tags', 'worldgen', 'forge', 'advancement'):
        clean(os.path.join(D, d))
    clean(os.path.join(ROOT, 'data', 'minecraft'))
    gen_blocks()
    gen_items()
    gen_equipment()
    gen_particles()
    gen_sounds()
    gen_lang()
    gen_loot()
    gen_recipes()
    gen_tags()
    gen_worldgen()
    gen_quests()
    n = sum(len(f) for _, _, f in os.walk(ROOT))
    print('resources written; total files under resources:', n)


if __name__ == '__main__':
    main()
