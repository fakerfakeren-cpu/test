"""Generates every JSON resource for Rimeheart (assets + data)."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lang_en as L  # noqa

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
A = os.path.join(ROOT, 'assets', 'rimeheart')
D = os.path.join(ROOT, 'data', 'rimeheart')
M = 'rimeheart'


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def clean(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def m(n):
    return f'{M}:{n}'


CUBE_ALL = ['rimestone', 'permafrost', 'frostiron_ore', 'rime_crystal_ore', 'frostiron_block', 'rime_crystal_block', 'rimestone_bricks',
            'cracked_rimestone_bricks', 'chiseled_rimestone_bricks', 'frost_lamp']
HANDHELD = ['frostiron_sword', 'frostiron_pickaxe', 'frostiron_axe', 'frostiron_shovel', 'frostbite_blade', 'glacier_maul', 'blizzard_staff', 'winterfang']
GENERATED = ['wardens_journal', 'raw_frostiron', 'frostiron_ingot', 'frostiron_nugget', 'rime_shard', 'wraith_essence', 'glacial_heart', 'sovereign_core',
             'frost_charge', 'winter_horn', 'hearthfire_stew', 'frost_wraith_spawn_egg', 'shardling_spawn_egg', 'frost_sovereign_spawn_egg'] + \
            [f'frostiron_{p}' for p in ('helmet', 'chestplate', 'leggings', 'boots')] + [f'wraithweave_{p}' for p in ('hood', 'robe', 'leggings', 'boots')]


def item_def(name, model_ref):
    w(f'{A}/items/{name}.json', {'model': {'type': 'minecraft:model', 'model': model_ref}})


def gen_assets():
    for b in CUBE_ALL:
        w(f'{A}/models/block/{b}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': m(f'block/{b}')}})
    w(f'{A}/models/block/hollow_rimestone_bricks.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': m('block/rimestone_bricks')}})
    w(f'{A}/models/block/rime_crystal_cluster.json', {'parent': 'minecraft:block/cross', 'textures': {'cross': m('block/rime_crystal_cluster')}})
    w(f'{A}/models/block/glacial_altar.json', {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
        'top': m('block/glacial_altar_top'), 'side': m('block/glacial_altar_side'), 'bottom': m('block/rimestone')}})
    for b in CUBE_ALL + ['hollow_rimestone_bricks', 'rime_crystal_cluster', 'glacial_altar']:
        w(f'{A}/blockstates/{b}.json', {'variants': {'': {'model': m(f'block/{b}')}}})
        if b == 'rime_crystal_cluster':
            w(f'{A}/models/item/{b}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': m(f'block/{b}')}})
            item_def(b, m(f'item/{b}'))
        else:
            item_def(b, m(f'block/{b}'))
    for i in HANDHELD:
        w(f'{A}/models/item/{i}.json', {'parent': 'minecraft:item/handheld', 'textures': {'layer0': m(f'item/{i}')}})
        item_def(i, m(f'item/{i}'))
    for i in GENERATED:
        w(f'{A}/models/item/{i}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': m(f'item/{i}')}})
        item_def(i, m(f'item/{i}'))
    # rimebow with pull frames
    w(f'{A}/models/item/rimebow.json', {'parent': 'minecraft:item/bow', 'textures': {'layer0': m('item/rimebow')}})
    for n in range(3):
        w(f'{A}/models/item/rimebow_pulling_{n}.json', {'parent': 'minecraft:item/bow', 'textures': {'layer0': m(f'item/rimebow_pulling_{n}')}})
    w(f'{A}/items/rimebow.json', {'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:using_item',
        'on_false': {'type': 'minecraft:model', 'model': m('item/rimebow')},
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                    'entries': [{'threshold': 0.65, 'model': {'type': 'minecraft:model', 'model': m('item/rimebow_pulling_1')}},
                                {'threshold': 0.9, 'model': {'type': 'minecraft:model', 'model': m('item/rimebow_pulling_2')}}],
                    'fallback': {'type': 'minecraft:model', 'model': m('item/rimebow_pulling_0')}}}})
    for asset in ('frostiron', 'wraithweave'):
        w(f'{A}/equipment/{asset}.json', {'layers': {'humanoid': [{'texture': m(asset)}], 'humanoid_leggings': [{'texture': m(asset)}]}})
    for p in ('frost_glint', 'snow_puff', 'wraith_wisp'):
        w(f'{A}/particles/{p}.json', {'textures': [m(f'{p}_{i}') for i in range(4)]})
    sounds = {}
    files = sorted(f[:-4] for f in os.listdir(f'{A}/sounds') if f.endswith('.ogg'))
    for event in L.SUBTITLES:
        variants = [f for f in files if f == event or (f.startswith(event) and f[len(event):].isdigit())]
        sounds[event] = {'subtitle': f'subtitles.{M}.{event}', 'sounds': [{'name': m(v), 'volume': 1.0} for v in variants]}
        assert variants, event
    w(f'{A}/sounds.json', sounds)
    # language
    lang = {}
    lang.update(L.NAMES)
    lang.update(L.TOOLTIPS)
    lang.update(L.MESSAGES)
    for k, v in L.SUBTITLES.items():
        lang[f'subtitles.{M}.{k}'] = v
    for q in L.QUESTS:
        lang[f'quest.{M}.{q[0]}.title'] = q[3]
        lang[f'quest.{M}.{q[0]}.description'] = q[4]
        lang[f'quest.{M}.{q[0]}.hint'] = L.QUEST_HINTS[q[0]]
    lang.update(L.JOURNAL_UI)
    for i, (title, text) in enumerate(L.GUIDE):
        lang[f'guide.{M}.{i}.title'] = title
        lang[f'guide.{M}.{i}.text'] = text
    w(f'{A}/lang/en_us.json', lang)


# ============================================================================ data
def item_entry(name, count=None, fns=None, weight=None, conditions=None):
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
    if conditions:
        e['conditions'] = conditions
    return e


SILK = {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {'minecraft:enchantments': [{'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}
FORTUNE = {'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'}
DECAY = {'function': 'minecraft:explosion_decay'}
LOOTING = lambda lo, hi: {'function': 'minecraft:enchanted_count_increase', 'enchantment': 'minecraft:looting', 'count': {'type': 'minecraft:uniform', 'min': float(lo), 'max': float(hi)}}  # noqa


def table(path, kind, pools):
    w(f'{D}/loot_table/{path}.json', {'type': f'minecraft:{kind}', 'pools': pools, 'random_sequence': m(path)})


def gen_loot():
    for b in ['rimestone', 'permafrost', 'frostiron_block', 'rime_crystal_block', 'rimestone_bricks', 'cracked_rimestone_bricks',
              'chiseled_rimestone_bricks', 'frost_lamp', 'glacial_altar']:
        table(f'blocks/{b}', 'block', [{'rolls': 1.0, 'entries': [item_entry(m(b))], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}])
    table('blocks/frostiron_ore', 'block', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [
        item_entry(m('frostiron_ore'), conditions=[SILK]), item_entry(m('raw_frostiron'), fns=[FORTUNE, DECAY])]}]}])
    table('blocks/rime_crystal_ore', 'block', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [
        item_entry(m('rime_crystal_ore'), conditions=[SILK]), item_entry(m('rime_shard'), (1, 2), fns=[FORTUNE, DECAY])]}]}])
    table('blocks/rime_crystal_cluster', 'block', [{'rolls': 1.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [
        item_entry(m('rime_crystal_cluster'), conditions=[SILK]), item_entry(m('rime_shard'), (2, 4), fns=[FORTUNE, DECAY])]}]}])
    table('entities/frost_wraith', 'entity', [
        {'rolls': 1.0, 'entries': [item_entry(m('wraith_essence'), (0, 2), fns=[LOOTING(0, 1)])]},
        {'rolls': 1.0, 'entries': [item_entry(m('glacial_heart'))], 'conditions': [
            {'condition': 'minecraft:killed_by_player'},
            {'condition': 'minecraft:random_chance_with_enchanted_bonus', 'enchantment': 'minecraft:looting',
             'unenchanted_chance': 0.02, 'enchanted_chance': {'type': 'minecraft:linear', 'base': 0.03, 'per_level_above_first': 0.01}}]}])
    table('entities/shardling', 'entity', [{'rolls': 1.0, 'entries': [item_entry(m('rime_shard'), (1, 2), fns=[LOOTING(0, 1)])]}])
    table('entities/frost_sovereign', 'entity', [
        {'rolls': 1.0, 'entries': [item_entry(m('sovereign_core'))]},
        {'rolls': 1.0, 'entries': [item_entry(m('glacial_heart'))]},
        {'rolls': 1.0, 'entries': [item_entry(m('frostiron_ingot'), (8, 14))]},
        {'rolls': 1.0, 'entries': [item_entry(m('rime_shard'), (8, 16))]},
        {'rolls': 1.0, 'entries': [item_entry(m('frost_charge'), (4, 8))]}])
    common = [item_entry(m('frostiron_ingot'), (1, 4), weight=20), item_entry(m('raw_frostiron'), (2, 6), weight=20),
              item_entry(m('rime_shard'), (2, 6), weight=20), item_entry(m('frost_charge'), (1, 3), weight=10),
              item_entry(m('hearthfire_stew'), weight=8), item_entry(m('wraith_essence'), (1, 2), weight=8),
              item_entry('minecraft:bread', (2, 5), weight=10), item_entry('minecraft:golden_apple', weight=3),
              item_entry('minecraft:diamond', (1, 2), weight=3)]
    table('chests/sanctum_common', 'chest', [{'rolls': {'type': 'minecraft:uniform', 'min': 4.0, 'max': 7.0}, 'entries': common}])
    table('chests/sanctum_vault', 'chest', [
        {'rolls': 1.0, 'entries': [item_entry(m('glacial_heart'))]},
        {'rolls': 3.0, 'entries': [item_entry(m('frostiron_block'), weight=5), item_entry(m('frost_charge'), (4, 8), weight=10),
                                   item_entry('minecraft:golden_apple', (1, 2), weight=8), item_entry(m('wraith_essence'), (2, 4), weight=10),
                                   item_entry('minecraft:book', fns=[{'function': 'minecraft:enchant_randomly'}], weight=6),
                                   item_entry('minecraft:diamond', (2, 3), weight=4)]}])
    w(f'{D}/loot_table/quests/journal.json', {'type': 'minecraft:advancement_reward', 'pools': [{'rolls': 1.0, 'entries': [item_entry(m('wardens_journal'))]}]})


def shaped(name, pattern, key, result, count=1, category='misc'):
    w(f'{D}/recipe/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': category, 'pattern': pattern, 'key': key,
                                   'result': {'id': result, 'count': count}})


def shapeless(name, ingredients, result, count=1, category='misc'):
    w(f'{D}/recipe/{name}.json', {'type': 'minecraft:crafting_shapeless', 'category': category, 'ingredients': ingredients,
                                   'result': {'id': result, 'count': count}})


def cooking(name, kind, ingredient, result, xp):
    w(f'{D}/recipe/{name}.json', {'type': f'minecraft:{kind}', 'category': 'misc', 'ingredient': ingredient, 'result': {'id': result}, 'experience': xp})


def gen_recipes():
    I, S, R, W = m('frostiron_ingot'), 'minecraft:stick', m('rime_shard'), m('wraith_essence')
    for src in ('raw_frostiron', 'frostiron_ore'):
        cooking(f'frostiron_ingot_from_smelting_{src}', 'smelting', m(src), I, 0.8)
        cooking(f'frostiron_ingot_from_blasting_{src}', 'blasting', m(src), I, 0.8)
    shaped('frostiron_block', ['###', '###', '###'], {'#': I}, m('frostiron_block'), category='building')
    shapeless('frostiron_ingot_from_block', [m('frostiron_block')], I, 9)
    shaped('frostiron_ingot_from_nuggets', ['###', '###', '###'], {'#': m('frostiron_nugget')}, I)
    shapeless('frostiron_nugget', [I], m('frostiron_nugget'), 9)
    shaped('rime_crystal_block', ['##', '##'], {'#': R}, m('rime_crystal_block'), category='building')
    shaped('rimestone_bricks', ['##', '##'], {'#': m('rimestone')}, m('rimestone_bricks'), 4, 'building')
    shaped('chiseled_rimestone_bricks', ['#', '#'], {'#': m('rimestone_bricks')}, m('chiseled_rimestone_bricks'), 1, 'building')
    cooking('cracked_rimestone_bricks', 'smelting', m('rimestone_bricks'), m('cracked_rimestone_bricks'), 0.1)
    shaped('frost_lamp', [' R ', 'RGR', ' R '], {'R': R, 'G': 'minecraft:glowstone'}, m('frost_lamp'), category='building')
    shaped('glacial_altar', ['RCR', 'BBB', 'BBB'], {'R': R, 'C': m('rime_crystal_block'), 'B': m('chiseled_rimestone_bricks')}, m('glacial_altar'))
    shaped('frostiron_sword', ['#', '#', 'S'], {'#': I, 'S': S}, m('frostiron_sword'), category='equipment')
    shaped('frostiron_pickaxe', ['###', ' S ', ' S '], {'#': I, 'S': S}, m('frostiron_pickaxe'), category='equipment')
    shaped('frostiron_axe', ['##', '#S', ' S'], {'#': I, 'S': S}, m('frostiron_axe'), category='equipment')
    shaped('frostiron_shovel', ['#', 'S', 'S'], {'#': I, 'S': S}, m('frostiron_shovel'), category='equipment')
    shaped('frostiron_helmet', ['###', '# #'], {'#': I}, m('frostiron_helmet'), category='equipment')
    shaped('frostiron_chestplate', ['# #', '###', '###'], {'#': I}, m('frostiron_chestplate'), category='equipment')
    shaped('frostiron_leggings', ['###', '# #', '# #'], {'#': I}, m('frostiron_leggings'), category='equipment')
    shaped('frostiron_boots', ['# #', '# #'], {'#': I}, m('frostiron_boots'), category='equipment')
    shaped('wraithweave_hood', ['###', '# #'], {'#': W}, m('wraithweave_hood'), category='equipment')
    shaped('wraithweave_robe', ['# #', '###', '###'], {'#': W}, m('wraithweave_robe'), category='equipment')
    shaped('wraithweave_leggings', ['###', '# #', '# #'], {'#': W}, m('wraithweave_leggings'), category='equipment')
    shaped('wraithweave_boots', ['# #', '# #'], {'#': W}, m('wraithweave_boots'), category='equipment')
    shaped('frostbite_blade', [' R ', 'RBR', ' W '], {'R': R, 'B': m('frostiron_sword'), 'W': W}, m('frostbite_blade'), category='equipment')
    shaped('glacier_maul', ['ICI', ' S ', ' S '], {'I': I, 'C': m('rime_crystal_block'), 'S': S}, m('glacier_maul'), category='equipment')
    shaped('rimebow', [' IT', 'R T', ' IT'], {'I': I, 'R': R, 'T': 'minecraft:string'}, m('rimebow'), category='equipment')
    shaped('blizzard_staff', ['  C', ' W ', 'I  '], {'C': m('rime_crystal_block'), 'W': W, 'I': I}, m('blizzard_staff'), category='equipment')
    shaped('winterfang', ['C', 'B'], {'C': m('sovereign_core'), 'B': m('frostbite_blade')}, m('winterfang'), category='equipment')
    shapeless('frost_charge', [R, 'minecraft:snowball', 'minecraft:gunpowder'], m('frost_charge'), 2)
    shaped('winter_horn', ['W W', 'IGI', ' II'], {'W': W, 'I': I, 'G': m('glacial_heart')}, m('winter_horn'))
    shapeless('hearthfire_stew', ['minecraft:bowl', 'minecraft:baked_potato', 'minecraft:carrot', 'minecraft:sweet_berries'], m('hearthfire_stew'))
    shapeless('wardens_journal', ['minecraft:book', R], m('wardens_journal'))
    shapeless('wardens_journal_from_snowball', ['minecraft:book', 'minecraft:snowball'], m('wardens_journal'))


def tag(kind, ns, name, values, replace=False):
    w(os.path.join(ROOT, 'data', ns, 'tags', kind, name + '.json'), {'replace': replace, 'values': values})


FROZEN = ['minecraft:snowy_plains', 'minecraft:ice_spikes', 'minecraft:snowy_taiga', 'minecraft:snowy_slopes', 'minecraft:frozen_peaks',
          'minecraft:jagged_peaks', 'minecraft:grove', 'minecraft:frozen_river', 'minecraft:snowy_beach']


def gen_tags():
    tag('block', 'minecraft', 'mineable/pickaxe', [m(b) for b in ('rimestone', 'frostiron_ore', 'rime_crystal_ore', 'rime_crystal_cluster', 'frostiron_block',
        'rime_crystal_block', 'rimestone_bricks', 'cracked_rimestone_bricks', 'chiseled_rimestone_bricks', 'hollow_rimestone_bricks', 'frost_lamp', 'glacial_altar')])
    tag('block', 'minecraft', 'mineable/shovel', [m('permafrost')])
    tag('block', 'minecraft', 'needs_iron_tool', [m(b) for b in ('frostiron_ore', 'rime_crystal_ore', 'frostiron_block')])
    tag('block', 'minecraft', 'needs_stone_tool', [m(b) for b in ('glacial_altar',)])
    tag('item', M, 'frostiron_repair', [m('frostiron_ingot')])
    tag('item', M, 'wraithweave_repair', [m('wraith_essence')])
    armor = [m(f'frostiron_{p}') for p in ('helmet', 'chestplate', 'leggings', 'boots')] + [m(f'wraithweave_{p}') for p in ('hood', 'robe', 'leggings', 'boots')]
    tag('item', 'minecraft', 'freeze_immune_wearables', armor)
    tag('item', 'minecraft', 'swords', [m(n) for n in ('frostiron_sword', 'frostbite_blade', 'glacier_maul', 'winterfang')])
    tag('item', 'minecraft', 'pickaxes', [m('frostiron_pickaxe')])
    tag('item', 'minecraft', 'axes', [m('frostiron_axe')])
    tag('item', 'minecraft', 'shovels', [m('frostiron_shovel')])
    tag('item', 'minecraft', 'head_armor', [m('frostiron_helmet'), m('wraithweave_hood')])
    tag('item', 'minecraft', 'chest_armor', [m('frostiron_chestplate'), m('wraithweave_robe')])
    tag('item', 'minecraft', 'leg_armor', [m('frostiron_leggings'), m('wraithweave_leggings')])
    tag('item', 'minecraft', 'foot_armor', [m('frostiron_boots'), m('wraithweave_boots')])
    tag('item', 'minecraft', 'trimmable_armor', armor)
    tag('item', 'minecraft', 'enchantable/durability', [m('rimebow'), m('blizzard_staff')])
    tag('item', 'minecraft', 'enchantable/bow', [m('rimebow')])
    tag('entity_type', M, 'winter_creatures', [m('frost_wraith'), m('shardling'), m('frost_sovereign')])
    tag('entity_type', 'minecraft', 'freeze_immune_entity_types', [m('frost_wraith'), m('shardling'), m('frost_sovereign')])
    tag('worldgen/structure', M, 'frozen_sanctum', [m('frozen_sanctum')])
    tag('worldgen/biome', M, 'is_frozen', FROZEN)
    tag('worldgen/biome', M, 'has_structure/frozen_sanctum', ['minecraft:snowy_plains', 'minecraft:snowy_taiga', 'minecraft:ice_spikes', 'minecraft:grove', 'minecraft:snowy_slopes'])


def ore(name, block, size, count, lo, hi, shape='trapezoid'):
    w(f'{D}/worldgen/configured_feature/{name}.json', {'type': 'minecraft:ore', 'config': {
        'size': size, 'discard_chance_on_air_exposure': 0.0,
        'targets': [{'target': {'predicate_type': 'minecraft:tag_match', 'tag': 'minecraft:stone_ore_replaceables'}, 'state': {'Name': m(block)}}]}})
    w(f'{D}/worldgen/placed_feature/{name}.json', {'feature': m(name), 'placement': [
        {'type': 'minecraft:count', 'count': count}, {'type': 'minecraft:in_square'},
        {'type': 'minecraft:height_range', 'height': {'type': f'minecraft:{shape}', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}},
        {'type': 'minecraft:biome'}]})


def gen_worldgen():
    ore('frostiron_ore', 'frostiron_ore', 8, 12, -24, 112)
    ore('rime_crystal_ore', 'rime_crystal_ore', 5, 7, 0, 160)
    ore('rimestone_blob', 'rimestone', 48, 3, 0, 128, 'uniform')
    w(f'{D}/forge/biome_modifier/frozen_ores.json', {'type': 'forge:add_features', 'biomes': f'#{M}:is_frozen',
                                                     'features': [m('frostiron_ore'), m('rime_crystal_ore'), m('rimestone_blob')], 'step': 'underground_ores'})
    w(f'{D}/forge/biome_modifier/frozen_spawns.json', {'type': 'forge:add_spawns', 'biomes': f'#{M}:is_frozen', 'spawners': [
        {'type': m('frost_wraith'), 'weight': 15, 'minCount': 1, 'maxCount': 2},
        {'type': m('shardling'), 'weight': 12, 'minCount': 1, 'maxCount': 3}]})
    w(f'{D}/worldgen/structure/frozen_sanctum.json', {'type': m('blueprint'), 'biomes': f'#{M}:has_structure/frozen_sanctum', 'spawn_overrides': {},
                                                      'step': 'underground_structures', 'terrain_adaptation': 'none', 'blueprint': 'frozen_sanctum', 'y_offset': 0})
    w(f'{D}/worldgen/structure_set/frozen_sanctum.json', {'structures': [{'structure': m('frozen_sanctum'), 'weight': 1}],
                                                          'placement': {'type': 'minecraft:random_spread', 'spacing': 32, 'separation': 12, 'salt': 51223911}})


def criteria(spec):
    kind = spec[0]
    if kind == 'tick':
        return {'unlock': {'trigger': 'minecraft:tick'}}, [['unlock']]
    if kind == 'item':
        return {'got': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': spec[1]}]}}}, [['got']]
    if kind == 'all_items':
        c = {f'got_{i}': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': it}]}} for i, it in enumerate(spec[1])}
        return c, [[k] for k in c]
    if kind == 'kill':
        return {'kill': {'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:entity_type': spec[1]}}]}}}, [['kill']]
    if kind == 'structure':
        return {'found': {'trigger': 'minecraft:location', 'conditions': {'player': [
            {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:location': {'structures': spec[1]}}}]}}}, [['found']]
    raise ValueError(kind)


def gen_quests():
    for qid, parent, icon, title, desc, frame, spec in L.QUESTS:
        crit, req = criteria(spec)
        display = {'icon': {'id': icon}, 'title': {'translate': f'quest.{M}.{qid}.title'},
                   'description': {'translate': f'quest.{M}.{qid}.description'}, 'frame': frame,
                   'show_toast': True, 'announce_to_chat': qid != 'root', 'hidden': False}
        if parent is None:
            display['background'] = m('block/rimestone_bricks')
        adv = {'display': display, 'criteria': crit, 'requirements': req}
        if parent:
            adv['parent'] = m(f'quests/{parent}')
        else:
            # The root quest hands out the Warden's Journal on first join.
            adv['rewards'] = {'loot': [m('quests/journal')]}
        w(f'{D}/advancement/quests/{qid}.json', adv)
        # Hidden per-player marker, awarded when this quest's reward is claimed from the journal.
        w(f'{D}/advancement/claimed/{qid}.json', {'criteria': {'claimed': {'trigger': 'minecraft:impossible'}}, 'requirements': [['claimed']]})
    recipes = sorted(m(f[:-5]) for f in os.listdir(f'{D}/recipe') if f.endswith('.json'))
    w(f'{D}/advancement/recipes/unlock_all.json', {'criteria': {'joined': {'trigger': 'minecraft:tick'}}, 'requirements': [['joined']],
                                                   'rewards': {'recipes': recipes}})


def main():
    for d in ('blockstates', 'models', 'items', 'equipment', 'particles', 'lang'):
        clean(os.path.join(A, d))
    clean(D)
    gen_assets()
    gen_loot()
    gen_recipes()
    gen_tags()
    gen_worldgen()
    gen_quests()
    n = sum(len(f) for _, _, f in os.walk(A)) + sum(len(f) for _, _, f in os.walk(D))
    print('resources written; rimeheart files:', n)


if __name__ == '__main__':
    main()
