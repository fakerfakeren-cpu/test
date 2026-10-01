"""Server data: quest advancements, loot tables, tags, recipes and worldgen (structures, ores, spawns and the
Gloaming dimension).

Run from the repository root:  python3 -m tools.oath.data
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'src/main/resources/data')
NS = 'oathbound'


def write(rel, obj, ns=NS):
    path = os.path.join(DATA, ns, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def o(name):
    return name if ':' in name else f'{NS}:{name}'


# ====================================================================== advancements
def has_item(*items):
    return {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': o(i) if ':' not in i else i} for i in items]}}


def killed(entity):
    return {'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': [
        {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:entity_type': o(entity)}}]}}


def entered(structure):
    return {'trigger': 'minecraft:location', 'conditions': {'player': [
        {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'minecraft:location': {'structures': o(structure)}}}]}}


def impossible():
    return {'trigger': 'minecraft:impossible'}


# quest id -> (criteria, requirements or None for "any one of them", frame, icon)
def quest_criteria():
    Q = {}

    def any_of(qid, frame, icon, **crit):
        Q[qid] = (crit, [list(crit)], frame, icon)

    def all_of(qid, frame, icon, **crit):
        Q[qid] = (crit, [[k] for k in crit], frame, icon)

    any_of('root', 'task', 'lantern_chronicle', chronicle=has_item('lantern_chronicle'))
    any_of('lumenite', 'task', 'lumenite_shard', shard=has_item('lumenite_shard'))
    any_of('oathsteel', 'task', 'oathsteel_ingot', ingot=has_item('oathsteel_ingot'))
    any_of('lantern', 'task', 'wardens_lantern', lantern=has_item('wardens_lantern'))
    any_of('wayshrine', 'goal', 'wayshrine_brazier', kindle=impossible())
    any_of('oathsteel_arms', 'task', 'oathsteel_longsword', longsword=has_item('oathsteel_longsword'), halberd=has_item('wardens_halberd'))
    any_of('oathsteel_armor', 'task', 'oathsteel_chestplate', **{p: has_item('oathsteel_' + p) for p in ('helmet', 'chestplate', 'leggings', 'boots')})
    any_of('chapel', 'task', 'chapel_bell', found=entered('drowned_chapel'))
    any_of('hymn', 'goal', 'hymn_stone', solved=impossible())
    any_of('caldris', 'challenge', 'seal_of_valor', slain=impossible(), killed=killed('sir_caldris'))
    any_of('anchor', 'task', 'drowned_anchor', anchor=has_item('drowned_anchor'))
    any_of('spire', 'task', 'rune_dial', found=entered('arcanist_spire'))
    any_of('spellsilk', 'task', 'spellsilk', silk=has_item('spellsilk'))
    any_of('cipher', 'goal', 'cipher_lectern', solved=impossible())
    any_of('veyl', 'challenge', 'seal_of_wisdom', slain=impossible(), killed=killed('archmage_veyl'))
    any_of('arcanist', 'task', 'arcanist_robe', **{p: has_item('arcanist_' + p) for p in ('hood', 'robe', 'leggings', 'boots')})
    any_of('dawnstring', 'task', 'dawnstring_longbow', bow=has_item('dawnstring_longbow'))
    any_of('barrow', 'task', 'sarcophagus', found=entered('barrow_of_kings'))
    any_of('honest_king', 'goal', 'barrow_seal', solved=impossible())
    any_of('hrodgar', 'challenge', 'seal_of_sacrifice', slain=impossible(), killed=killed('hrodgar'))
    any_of('warhorn', 'task', 'housecarl_warhorn', horn=has_item('housecarl_warhorn'))
    any_of('oathkey', 'goal', 'oathkey', key=has_item('oathkey'))
    any_of('citadel', 'task', 'sundered_keystone', found=entered('sundered_citadel'))
    any_of('gate', 'goal', 'wardstone_pillar', opened=impossible())
    any_of('gloaming', 'goal', 'gloam_moss', entered=impossible(),
           travelled={'trigger': 'minecraft:changed_dimension', 'conditions': {'to': 'oathbound:gloaming'}})
    any_of('sickle', 'task', 'shadowreap_sickle', sickle=has_item('shadowreap_sickle'))
    any_of('veilhound', 'task', 'gloam_essence', killed=killed('veilhound'))
    any_of('throne', 'goal', 'ward_lantern', challenged=impossible())
    any_of('morvane', 'challenge', 'everflame_ember', slain=impossible(), killed=killed('morvane'))
    any_of('dawnbreaker', 'task', 'dawnbreaker', blade=has_item('dawnbreaker'))
    any_of('crown', 'task', 'hollow_crown', crown=has_item('hollow_crown'))
    any_of('gloamling', 'task', 'gloam_essence', killed=killed('gloamling'))
    any_of('lanternmoth', 'task', 'luminous_dust', dust=has_item('luminous_dust'))
    any_of('elixir', 'task', 'elixir_of_dawn', elixir=has_item('elixir_of_dawn'))
    any_of('flask', 'task', 'lumen_flask', flask=has_item('lumen_flask'))
    any_of('forsworn', 'task', 'oathsteel_helmet', killed=killed('forsworn_knight'))
    any_of('insignia', 'task', 'lanternguard_insignia', insignia=has_item('lanternguard_insignia'))
    all_of('loremaster', 'challenge', 'lore_tablet', **{f'tablet_{i}': impossible() for i in range(10)})
    any_of('alchemist', 'task', 'elixir_of_valor', done=impossible())
    any_of('enchanter', 'task', 'oathsteel_ingot', done=impossible())
    any_of('relic_hunter', 'challenge', 'lanternguard_signet', done=impossible())
    any_of('everflame', 'challenge', 'everflame_lantern', lantern=has_item('everflame_lantern'))
    from . import wilds
    wilds.quests(any_of)
    return Q


PARENTS = {
    'root': None, 'lumenite': 'root', 'oathsteel': 'lumenite', 'lantern': 'oathsteel', 'wayshrine': 'lantern',
    'oathsteel_arms': 'oathsteel', 'oathsteel_armor': 'oathsteel', 'chapel': 'wayshrine', 'hymn': 'chapel',
    'caldris': 'hymn', 'anchor': 'caldris', 'spire': 'caldris', 'spellsilk': 'spire', 'cipher': 'spire', 'veyl': 'cipher',
    'arcanist': 'spellsilk', 'dawnstring': 'spellsilk', 'barrow': 'veyl', 'honest_king': 'barrow', 'hrodgar': 'honest_king',
    'warhorn': 'hrodgar', 'oathkey': 'hrodgar', 'citadel': 'oathkey', 'gate': 'citadel', 'gloaming': 'gate',
    'sickle': 'gloaming', 'veilhound': 'gloaming', 'throne': 'gloaming', 'morvane': 'throne', 'dawnbreaker': 'morvane',
    'crown': 'morvane', 'gloamling': 'root', 'lanternmoth': 'root', 'elixir': 'lanternmoth', 'flask': 'lanternmoth',
    'forsworn': 'root', 'insignia': 'root', 'loremaster': 'root', 'everflame': 'morvane',
    'alchemist': 'chapel', 'enchanter': 'spire', 'relic_hunter': 'barrow',
}

BOONS = ['squires_vigor', 'lamplighters_thrift', 'pilgrims_stride', 'tidebound', 'knights_guard', 'long_reach',
         'arcane_insight', 'scholars_luck', 'glyphskin', 'oath_of_the_housecarl', 'kingsblood', 'grave_sight',
         'veilwalker', 'gatesworn', 'featherfall', 'everflame_heart', 'kingslayer', 'dawnbound']


def advancements():
    Q = quest_criteria()
    from . import wilds
    PARENTS.update(wilds.PARENTS)
    assert set(Q) == set(PARENTS), set(Q) ^ set(PARENTS)
    for qid, (crit, req, frame, icon) in Q.items():
        display = {
            'icon': {'id': o(icon)},
            'title': {'translate': f'quest.oathbound.{qid}.title'},
            'description': {'translate': f'quest.oathbound.{qid}.description'},
            'frame': frame, 'show_toast': True, 'announce_to_chat': False, 'hidden': False,
        }
        adv = {'display': display, 'criteria': crit, 'requirements': req}
        if PARENTS[qid]:
            adv['parent'] = f'oathbound:quests/{PARENTS[qid]}'
        else:
            display['background'] = 'oathbound:block/wardstone_bricks'
        write(f'advancement/quests/{qid}.json', adv)
        write(f'advancement/claimed/{qid}.json', {'criteria': {'claimed': impossible()}, 'requirements': [['claimed']]})
    for b in BOONS:
        write(f'advancement/boons/{b}.json', {'criteria': {'sworn': impossible()}, 'requirements': [['sworn']]})
    # every recipe unlocks as soon as a player joins: the Chronicle teaches them
    write('advancement/recipes/unlock_all.json', {'criteria': {'joined': {'trigger': 'minecraft:tick'}},
                                                   'requirements': [['joined']], 'rewards': {'recipes': sorted(RECIPE_IDS)}})


# ====================================================================== loot tables
def item(name, lo=1, hi=None, weight=1, funcs=None, conds=None):
    e = {'type': 'minecraft:item', 'name': o(name) if ':' not in name else name, 'weight': weight}
    fs = list(funcs or [])
    if hi is not None and (lo != 1 or hi != 1):
        fs.insert(0, {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}})
    elif lo != 1:
        fs.insert(0, {'function': 'minecraft:set_count', 'count': lo})
    if fs:
        e['functions'] = fs
    if conds:
        e['conditions'] = conds
    return e


def pool(entries, rolls=1, bonus=0, conds=None):
    p = {'rolls': rolls if isinstance(rolls, (int, float)) else {'type': 'minecraft:uniform', 'min': rolls[0], 'max': rolls[1]},
         'entries': entries}
    if bonus:
        p['bonus_rolls'] = bonus
    if conds:
        p['conditions'] = conds
    return p


def table(kind, pools, name):
    return {'type': f'minecraft:{kind}', 'pools': pools, 'random_sequence': f'oathbound:{name}'}


LOOTING = {'function': 'minecraft:enchanted_count_increase', 'enchantment': 'minecraft:looting',
           'count': {'type': 'minecraft:uniform', 'min': 0, 'max': 1}}
BY_PLAYER = [{'condition': 'minecraft:killed_by_player'}]
ENCHANT = {'function': 'minecraft:enchant_randomly'}
ENCHANT_LEVELS = {'function': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': 15, 'max': 30}}
EMPTY = {'type': 'minecraft:empty', 'weight': 1}


def self_drop(block):
    return table('block', [pool([item(block)], conds=[{'condition': 'minecraft:survives_explosion'}])], f'blocks/{block}')


def silk_or(block, drop, lo, hi, fortune=True):
    silk = {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {'minecraft:enchantments': [
        {'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}
    fs = [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}}]
    if fortune:
        fs.append({'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'})
    fs.append({'function': 'minecraft:explosion_decay'})
    return table('block', [pool([{'type': 'minecraft:alternatives', 'children': [
        {'type': 'minecraft:item', 'name': o(block), 'conditions': [silk]},
        {'type': 'minecraft:item', 'name': o(drop) if ':' not in drop else drop, 'functions': fs}]}])], f'blocks/{block}')


def slab_drop(block):
    return table('block', [pool([{'type': 'minecraft:item', 'name': o(block), 'functions': [
        {'function': 'minecraft:set_count', 'count': 2, 'conditions': [{'condition': 'minecraft:block_state_property', 'block': o(block),
                                                                       'properties': {'type': 'double'}}]},
        {'function': 'minecraft:explosion_decay'}]}])], f'blocks/{block}')


SELF_DROPPING = ['lumenite_block', 'oathsteel_block', 'wardstone', 'wardstone_bricks', 'cracked_wardstone_bricks',
                 'mossy_wardstone_bricks', 'chiseled_wardstone', 'wardstone_brick_stairs', 'wardstone_pillar', 'gloamstone',
                 'gloamstone_bricks', 'gloamwood_log', 'gloamwood_planks', 'veilbloom', 'wayshrine_brazier']


def loot_tables():
    for b in SELF_DROPPING:
        write(f'loot_table/blocks/{b}.json', self_drop(b))
    write('loot_table/blocks/wardstone_brick_slab.json', slab_drop('wardstone_brick_slab'))
    write('loot_table/blocks/lumenite_ore.json', silk_or('lumenite_ore', 'lumenite_shard', 1, 2))
    write('loot_table/blocks/deepslate_lumenite_ore.json', silk_or('deepslate_lumenite_ore', 'lumenite_shard', 1, 3))
    write('loot_table/blocks/gloam_moss.json', silk_or('gloam_moss', 'gloamstone', 1, 1, fortune=False))

    # ------------------------------------------------------------ creatures
    E = {
        'gloamling': [pool([item('gloam_essence', 0, 1, funcs=[LOOTING])])],
        'veilhound': [pool([item('gloam_essence', 1, 2, funcs=[LOOTING])]), pool([item('minecraft:bone', 0, 2)])],
        'lanternmoth': [pool([item('luminous_dust', 1, 2, funcs=[LOOTING])])],
        'forsworn_knight': [pool([item('minecraft:iron_nugget', 1, 4, funcs=[LOOTING])]),
                            pool([item('oathsteel_nugget', 0, 2)]),
                            pool([item('oathsteel_helmet', funcs=[{'function': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': 0.2, 'max': 0.6}}]),
                                  item('oathsteel_boots', funcs=[{'function': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': 0.2, 'max': 0.6}}]),
                                  {**EMPTY, 'weight': 30}], conds=BY_PLAYER)],
        'barrow_wight': [pool([item('minecraft:bone', 0, 2, funcs=[LOOTING])]), pool([item('minecraft:gold_nugget', 0, 3)]),
                         pool([item('lanternguard_insignia'), {**EMPTY, 'weight': 60}], conds=BY_PLAYER)],
        'animated_tome': [pool([item('minecraft:paper', 1, 3)]), pool([item('spellsilk', funcs=[LOOTING]), {**EMPTY, 'weight': 3}]),
                          pool([item('minecraft:book'), {**EMPTY, 'weight': 6}])],
        'sir_caldris': [pool([item('seal_of_valor')]), pool([item('drowned_anchor')]), pool([item('oathsteel_ingot', 2, 4)]),
                        pool([item('minecraft:heart_of_the_sea'), {**EMPTY, 'weight': 3}])],
        'archmage_veyl': [pool([item('seal_of_wisdom')]), pool([item('staff_of_veyl')]), pool([item('spellsilk', 2, 4)]),
                          pool([item('minecraft:book', funcs=[ENCHANT_LEVELS])])],
        'hrodgar': [pool([item('seal_of_sacrifice')]), pool([item('housecarl_warhorn')]), pool([item('minecraft:gold_block', 1, 2)]),
                    pool([item('lanternguard_insignia')])],
        'morvane': [pool([item('everflame_ember', 4, 5)]), pool([item('dawnbreaker')]), pool([item('hollow_crown')]),
                    pool([item('minecraft:nether_star')])],
    }
    for name, pools in E.items():
        write(f'loot_table/entities/{name}.json', table('entity', pools, f'entities/{name}'))

    # ------------------------------------------------------------ chests
    C = {
        'wayshrine_cache': [pool([item('wayfarers_bread', 1, 3, 20), item('minecraft:torch', 4, 10, 20), item('lumenite_shard', 1, 3, 15),
                                  item('oathsteel_nugget', 2, 6, 12), item('honeyed_mead', 1, 1, 8), item('lumen_flask', 1, 1, 5),
                                  item('minecraft:iron_ingot', 1, 3, 12)], rolls=(3, 6))],
        'chapel_nave': [pool([item('minecraft:kelp', 2, 7, 15), item('minecraft:prismarine_shard', 1, 4, 12), item('minecraft:gold_nugget', 2, 8, 15),
                              item('minecraft:candle', 1, 3, 10), item('honeyed_mead', 1, 1, 8), item('minecraft:nautilus_shell', 1, 1, 3),
                              item('wayfarers_bread', 1, 2, 10)], rolls=(3, 6))],
        'chapel_reliquary': [pool([item('lumenite_shard', 2, 5, 15), item('oathsteel_ingot', 1, 3, 12), item('lumen_flask', 1, 2, 10),
                                   item('minecraft:golden_apple', 1, 1, 6), item('minecraft:book', 1, 1, 6, funcs=[ENCHANT_LEVELS]),
                                   item('minecraft:heart_of_the_sea', 1, 1, 2)], rolls=(4, 6))],
        'chapel_secret': [pool([item('lanternguard_insignia')]), pool([item('minecraft:gold_ingot', 2, 5)])],
        'spire_library': [pool([item('minecraft:book', 1, 3, 20), item('minecraft:paper', 2, 6, 15), item('minecraft:lapis_lazuli', 2, 6, 12),
                                item('spellsilk', 1, 1, 6), item('minecraft:experience_bottle', 1, 3, 8),
                                item('minecraft:book', 1, 1, 6, funcs=[ENCHANT_LEVELS])], rolls=(3, 6))],
        'spire_alchemy': [pool([item('minecraft:glass_bottle', 1, 4, 15), item('luminous_dust', 1, 3, 12), item('minecraft:glowstone_dust', 2, 6, 12),
                                item('minecraft:redstone', 2, 6, 10), item('elixir_of_dawn', 1, 1, 3), item('lumen_flask', 1, 2, 8)], rolls=(3, 6))],
        'spire_sanctum': [pool([item('spellsilk', 2, 3, 12), item('minecraft:diamond', 1, 2, 6), item('minecraft:book', 1, 1, 8, funcs=[ENCHANT_LEVELS]),
                                item('minecraft:experience_bottle', 3, 8, 10)], rolls=(3, 5))],
        'spire_secret': [pool([item('lanternguard_insignia')]), pool([item('minecraft:lapis_lazuli', 6, 12)])],
        'barrow_tomb': [pool([item('minecraft:bone', 2, 6, 15), item('minecraft:gold_nugget', 3, 9, 15), item('minecraft:iron_ingot', 1, 3, 10),
                              item('minecraft:gold_ingot', 1, 2, 8), item('wayfarers_bread', 1, 2, 8)], rolls=(3, 6))],
        'barrow_hoard': [pool([item('minecraft:gold_block', 1, 1, 6), item('minecraft:diamond', 1, 3, 8), item('minecraft:emerald', 2, 5, 10),
                               item('minecraft:golden_apple', 1, 1, 6), item('oathsteel_ingot', 2, 4, 10)], rolls=(4, 7))],
        'barrow_secret': [pool([item('lanternguard_insignia')]), pool([item('minecraft:emerald', 3, 7)])],
        'citadel_armory': [pool([item('oathsteel_ingot', 2, 5, 12), item('oathsteel_helmet', 1, 1, 3), item('oathsteel_chestplate', 1, 1, 2),
                                 item('oathsteel_leggings', 1, 1, 2), item('oathsteel_boots', 1, 1, 3), item('minecraft:arrow', 8, 20, 12),
                                 item('minecraft:shield', 1, 1, 5), item('minecraft:iron_ingot', 2, 6, 12)], rolls=(4, 7))],
        'citadel_barracks': [pool([item('wayfarers_bread', 2, 4, 15), item('knights_stew', 1, 1, 8), item('honeyed_mead', 1, 2, 10),
                                   item('minecraft:torch', 6, 16, 12), item('minecraft:arrow', 6, 14, 10)], rolls=(3, 6))],
        'citadel_secret': [pool([item('lanternguard_insignia')]), pool([item('elixir_of_dawn', 1, 2)])],
    }
    from . import wares, wilds
    C.update(wilds.chests())
    for name, extra in wares.loot_pools().items():
        C[name] = C[name] + [extra]
    for name, pools in C.items():
        write(f'loot_table/chests/{name}.json', table('chest', pools, f'chests/{name}'))


# ====================================================================== tags
_TAGS = {}


def tag(path, values, ns=NS, replace=False):
    """Collects a tag's values; several callers may add to the same tag. flush_tags() writes them all."""
    cur = _TAGS.setdefault((ns, path), [])
    for v in values:
        v = o(v) if ':' not in v and not v.startswith('#') else v
        if v not in cur:
            cur.append(v)


def flush_tags():
    for (ns, path), values in _TAGS.items():
        write(f'tags/{path}.json', {'replace': False, 'values': values}, ns)


PICKAXE_BLOCKS = ['lumenite_ore', 'deepslate_lumenite_ore', 'lumenite_block', 'oathsteel_block', 'wardstone', 'wardstone_bricks',
                  'cracked_wardstone_bricks', 'mossy_wardstone_bricks', 'chiseled_wardstone', 'wardstone_brick_stairs',
                  'wardstone_brick_slab', 'wardstone_pillar', 'gloamstone', 'gloam_moss', 'gloamstone_bricks', 'wayshrine_brazier']


def tags():
    tag('block/mineable/pickaxe', PICKAXE_BLOCKS, 'minecraft')
    tag('block/mineable/axe', ['gloamwood_log', 'gloamwood_planks'], 'minecraft')
    tag('block/needs_iron_tool', ['lumenite_ore', 'deepslate_lumenite_ore', 'lumenite_block', 'oathsteel_block'], 'minecraft')
    tag('block/stairs', ['wardstone_brick_stairs'], 'minecraft')
    tag('block/slabs', ['wardstone_brick_slab'], 'minecraft')
    tag('block/small_flowers', ['veilbloom'], 'minecraft')
    tag('block/logs', ['gloamwood_log'], 'minecraft')
    tag('block/planks', ['gloamwood_planks'], 'minecraft')
    tag('item/stairs', ['wardstone_brick_stairs'], 'minecraft')
    tag('item/slabs', ['wardstone_brick_slab'], 'minecraft')
    tag('item/small_flowers', ['veilbloom'], 'minecraft')
    tag('item/logs', ['gloamwood_log'], 'minecraft')
    tag('item/planks', ['gloamwood_planks'], 'minecraft')
    # common (c:) tags so modpacks see our materials
    tag('block/ores', ['lumenite_ore', 'deepslate_lumenite_ore'], 'c')
    tag('block/ores/lumenite', ['lumenite_ore', 'deepslate_lumenite_ore'], 'c')
    tag('item/ores', ['lumenite_ore', 'deepslate_lumenite_ore'], 'c')
    tag('item/ores/lumenite', ['lumenite_ore', 'deepslate_lumenite_ore'], 'c')
    tag('item/gems', ['lumenite_shard'], 'c')
    tag('item/gems/lumenite', ['lumenite_shard'], 'c')
    tag('item/ingots', ['oathsteel_ingot'], 'c')
    tag('item/ingots/oathsteel', ['oathsteel_ingot'], 'c')
    tag('item/nuggets', ['oathsteel_nugget'], 'c')
    tag('item/nuggets/oathsteel', ['oathsteel_nugget'], 'c')
    tag('item/storage_blocks/oathsteel', ['oathsteel_block'], 'c')
    tag('item/storage_blocks/lumenite', ['lumenite_block'], 'c')
    tag('block/storage_blocks/oathsteel', ['oathsteel_block'], 'c')
    tag('block/storage_blocks/lumenite', ['lumenite_block'], 'c')
    tag('item/dusts', ['lumenite_dust', 'luminous_dust'], 'c')
    # equipment classes (enchanting tables, anvils and smithing read these)
    swords = ['oathsteel_longsword', 'wardens_halberd', 'drowned_anchor', 'shadowreap_sickle', 'dawnbreaker']
    tag('item/swords', swords, 'minecraft')
    tag('item/pickaxes', ['oathsteel_pickaxe'], 'minecraft')
    tag('item/axes', ['oathsteel_axe'], 'minecraft')
    tag('item/shovels', ['oathsteel_shovel'], 'minecraft')
    tag('item/head_armor', ['oathsteel_helmet', 'arcanist_hood', 'hollow_crown'], 'minecraft')
    tag('item/chest_armor', ['oathsteel_chestplate', 'arcanist_robe'], 'minecraft')
    tag('item/leg_armor', ['oathsteel_leggings', 'arcanist_leggings'], 'minecraft')
    tag('item/foot_armor', ['oathsteel_boots', 'arcanist_boots'], 'minecraft')
    tag('item/trimmable_armor', ['oathsteel_helmet', 'oathsteel_chestplate', 'oathsteel_leggings', 'oathsteel_boots',
                                 'arcanist_hood', 'arcanist_robe', 'arcanist_leggings', 'arcanist_boots'], 'minecraft')
    tag('item/enchantable/bow', ['dawnstring_longbow'], 'minecraft')
    tag('item/enchantable/durability', ['dawnstring_longbow', 'staff_of_veyl', 'wardens_lantern'], 'minecraft')
    tag('item/enchantable/vanishing', ['dawnstring_longbow', 'staff_of_veyl'], 'minecraft')
    # our own
    tag('item/oathsteel_repair', ['oathsteel_ingot'])
    tag('item/spellsilk_repair', ['spellsilk'])
    tag('item/sunmended', ['oathsteel_pickaxe', 'oathsteel_axe', 'oathsteel_shovel', 'oathsteel_longsword', 'wardens_halberd'])
    tag('item/oath_forged', ['oathsteel_longsword', 'wardens_halberd', 'dawnbreaker', 'drowned_anchor', 'oathsteel_pickaxe',
                             'oathsteel_axe', 'oathsteel_shovel'])
    tag('entity_type/gloam_creatures', ['gloamling', 'veilhound', 'forsworn_knight', 'morvane'])
    tag('entity_type/undead', ['barrow_wight', 'forsworn_knight', 'hrodgar', 'spectral_housecarl', 'morvane'], 'minecraft')
    tag('entity_type/sensitive_to_smite', ['barrow_wight', 'forsworn_knight', 'hrodgar', 'spectral_housecarl', 'morvane'], 'minecraft')
    # structure tags the Lantern's Seek and the quests use
    for t, s in (('wayshrine', 'wayshrine'), ('drowned_chapel', 'drowned_chapel'), ('arcanist_spire', 'arcanist_spire'),
                 ('barrow', 'barrow_of_kings'), ('sundered_citadel', 'sundered_citadel')):
        tag(f'worldgen/structure/{t}', [s])
    # where each structure may appear (datapacks can retune these)
    tag('worldgen/biome/has_structure/wayshrine', ['#minecraft:is_forest', '#minecraft:is_taiga', 'minecraft:plains', 'minecraft:meadow',
                                                   'minecraft:sunflower_plains', 'minecraft:flower_forest', 'minecraft:cherry_grove',
                                                   'minecraft:savanna', 'minecraft:snowy_plains'])
    tag('worldgen/biome/has_structure/drowned_chapel', ['minecraft:swamp', 'minecraft:mangrove_swamp', '#minecraft:is_river',
                                                        '#minecraft:is_beach'])
    tag('worldgen/biome/has_structure/arcanist_spire', ['#minecraft:is_forest', '#minecraft:is_taiga', 'minecraft:meadow',
                                                        'minecraft:old_growth_birch_forest', 'minecraft:windswept_forest'])
    tag('worldgen/biome/has_structure/barrow_of_kings', ['minecraft:plains', 'minecraft:snowy_plains', '#minecraft:is_taiga',
                                                         'minecraft:windswept_hills', 'minecraft:meadow', 'minecraft:savanna'])
    tag('worldgen/biome/has_structure/sundered_citadel', ['minecraft:plains', 'minecraft:savanna', 'minecraft:meadow',
                                                          'minecraft:sunflower_plains', 'minecraft:snowy_plains', '#minecraft:is_taiga'])
    tag('worldgen/biome/has_lumenite', ['#minecraft:is_overworld'])
    tag('worldgen/biome/has_lanternmoths', ['#minecraft:is_forest', '#minecraft:is_taiga', 'minecraft:swamp', 'minecraft:meadow',
                                            'minecraft:cherry_grove', 'minecraft:flower_forest', 'minecraft:plains'])
    tag('worldgen/biome/has_gloamlings', ['#minecraft:is_overworld'])


# ====================================================================== worldgen
STRUCTURES = {
    # sketch id: (step, spacing, separation, salt)
    'wayshrine': ('surface_structures', 36, 12, 71211309),
    'drowned_chapel': ('surface_structures', 46, 16, 71211311),
    'arcanist_spire': ('surface_structures', 50, 18, 71211313),
    'barrow_of_kings': ('surface_structures', 52, 18, 71211317),
    'sundered_citadel': ('surface_structures', 64, 24, 71211319),
}


def worldgen():
    for sid, (step, spacing, sep, salt) in STRUCTURES.items():
        write(f'worldgen/structure/{sid}.json', {
            'type': 'oathbound:sketch', 'biomes': f'#oathbound:has_structure/{sid}', 'spawn_overrides': {},
            'step': step, 'terrain_adaptation': 'none', 'sketch': sid})
        write(f'worldgen/structure_set/{sid}.json', {
            'structures': [{'structure': f'oathbound:{sid}', 'weight': 1}],
            'placement': {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}})
    # lumenite ore
    for name, block, size, count, lo, hi, target in (
            ('ore_lumenite', 'lumenite_ore', 7, 9, -16, 64, 'minecraft:stone_ore_replaceables'),
            ('ore_lumenite_deep', 'deepslate_lumenite_ore', 8, 6, -64, 0, 'minecraft:deepslate_ore_replaceables')):
        write(f'worldgen/configured_feature/{name}.json', {'type': 'minecraft:ore', 'config': {
            'size': size, 'discard_chance_on_air_exposure': 0.0,
            'targets': [{'target': {'predicate_type': 'minecraft:tag_match', 'tag': target}, 'state': {'Name': o(block)}}]}})
        write(f'worldgen/placed_feature/{name}.json', {'feature': f'oathbound:{name}', 'placement': [
            {'type': 'minecraft:count', 'count': count}, {'type': 'minecraft:in_square'},
            {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:trapezoid', 'min_inclusive': {'absolute': lo},
                                                          'max_inclusive': {'absolute': hi}}},
            {'type': 'minecraft:biome'}]})
    write('forge/biome_modifier/lumenite_ores.json', {'type': 'forge:add_features', 'biomes': '#oathbound:has_lumenite',
                                                       'features': ['oathbound:ore_lumenite', 'oathbound:ore_lumenite_deep'],
                                                       'step': 'underground_ores'})
    write('forge/biome_modifier/lanternmoth_spawns.json', {'type': 'forge:add_spawns', 'biomes': '#oathbound:has_lanternmoths',
                                                            'spawners': [{'type': 'oathbound:lanternmoth', 'weight': 8, 'minCount': 2, 'maxCount': 4}]})
    write('forge/biome_modifier/gloamling_spawns.json', {'type': 'forge:add_spawns', 'biomes': '#oathbound:has_gloamlings',
                                                          'spawners': [{'type': 'oathbound:gloamling', 'weight': 14, 'minCount': 1, 'maxCount': 3}]})
    gloaming()
    from . import wilds
    wilds.structures()


FLOOR = {'type': 'minecraft:stone_depth', 'add_surface_depth': False, 'offset': 0, 'secondary_depth_range': 0, 'surface_type': 'floor'}


def gloaming():
    """The Gloaming: grey-violet floating islands under a starless dusk that never ends. Three countries share them:
    the mossy Gloaming itself, the burned Ashen Reach and the dense violet Veilwood."""
    write('dimension_type/gloaming.json', {
        'ambient_light': 0.12,
        'attributes': {
            'minecraft:audio/ambient_sounds': {'mood': {'block_search_extent': 8, 'offset': 2.0, 'sound': 'oathbound:gloaming_mood',
                                                        'tick_delay': 3000}},
            'minecraft:audio/background_music': {'default': {'max_delay': 9000, 'min_delay': 2400, 'replace_current_music': True,
                                                             'sound': 'oathbound:music_gloaming'}},
            'minecraft:gameplay/bed_rule': {'can_set_spawn': 'never', 'can_sleep': 'never', 'explodes': True},
            'minecraft:gameplay/respawn_anchor_works': False,
            'minecraft:visual/ambient_light_color': '#3a2f4a',
            'minecraft:visual/fog_color': '#2a2238',
            'minecraft:visual/sky_color': '#120e1c',
            'minecraft:visual/sky_light_color': '#8f6bd0',
            'minecraft:visual/sky_light_factor': 0.0,
        },
        'coordinate_scale': 1.0, 'default_clock': 'minecraft:the_end', 'has_ceiling': False, 'has_ender_dragon_fight': False,
        'has_fixed_time': True, 'has_skylight': True, 'height': 256, 'infiniburn': '#minecraft:infiniburn_end',
        'logical_height': 256, 'min_y': 0, 'monster_spawn_block_light_limit': 0, 'monster_spawn_light_level': 11,
        'skybox': 'end', 'timelines': '#minecraft:in_end'})
    write('worldgen/noise_settings/gloaming.json', {
        'aquifers_enabled': False, 'default_block': {'Name': 'oathbound:gloamstone'}, 'default_fluid': {'Name': 'minecraft:air'},
        'disable_mob_generation': False, 'legacy_random_source': True,
        'noise': {'height': 256, 'min_y': 0, 'size_horizontal': 2, 'size_vertical': 1},
        'noise_router': {
            'barrier': 0.0, 'continents': 0.0, 'depth': 0.0, 'erosion': 0.0,
            'final_density': {'type': 'minecraft:squeeze', 'argument': {'type': 'minecraft:interpolated', 'argument': {
                'type': 'minecraft:mul', 'argument1': 0.64, 'argument2': {'type': 'minecraft:blend_density', 'argument': {
                    'type': 'minecraft:add', 'argument1': -0.234375, 'argument2': {'type': 'minecraft:mul',
                        'argument1': {'type': 'minecraft:y_clamped_gradient', 'from_value': 0.0, 'from_y': 24, 'to_value': 1.0, 'to_y': 52},
                        'argument2': {'type': 'minecraft:add', 'argument1': 0.234375, 'argument2': {
                            'type': 'minecraft:add', 'argument1': -23.4375, 'argument2': {'type': 'minecraft:mul',
                                'argument1': {'type': 'minecraft:y_clamped_gradient', 'from_value': 1.0, 'from_y': 120, 'to_value': 0.0, 'to_y': 300},
                                'argument2': {'type': 'minecraft:add', 'argument1': 23.4375, 'argument2': 'minecraft:end/base_3d_noise'}}}}}}}}}},
            'fluid_level_floodedness': 0.0, 'fluid_level_spread': 0.0, 'lava': 0.0, 'preliminary_surface_level': 0.0, 'ridges': 0.0,
            # only the biome choice reads this: broad bands of ash, forest and moss across the islands
            'temperature': {'type': 'minecraft:noise', 'noise': 'minecraft:temperature', 'xz_scale': 0.6, 'y_scale': 0.0},
            'vegetation': 0.0, 'vein_gap': 0.0, 'vein_ridged': 0.0, 'vein_toggle': 0.0},
        'ore_veins_enabled': False, 'sea_level': 0, 'spawn_target': [],
        'surface_rule': {'type': 'minecraft:sequence', 'sequence': [
            {'type': 'minecraft:condition', 'if_true': {'type': 'minecraft:biome', 'biome_is': ['oathbound:ashen_reach']},
             'then_run': {'type': 'minecraft:condition', 'if_true': FLOOR, 'then_run': {'type': 'minecraft:block',
                                                                                         'result_state': {'Name': 'minecraft:blackstone'}}}},
            {'type': 'minecraft:condition', 'if_true': FLOOR,
             'then_run': {'type': 'minecraft:block', 'result_state': {'Name': 'oathbound:gloam_moss'}}},
            {'type': 'minecraft:block', 'result_state': {'Name': 'oathbound:gloamstone'}}]}})
    features = ['oathbound:gloam_fern_patch']   # written by building.worldgen()
    for fid, count, chance in (('gloamwood_tree', None, 3), ('gloam_ruin', None, 40), ('veilbloom_patch', 2, None)):
        write(f'worldgen/configured_feature/{fid}.json', {'type': f'oathbound:{fid}', 'config': {}})
        placement = []
        if count:
            placement.append({'type': 'minecraft:count', 'count': count})
        if chance:
            placement.append({'type': 'minecraft:rarity_filter', 'chance': chance})
        placement += [{'type': 'minecraft:in_square'}, {'type': 'minecraft:heightmap', 'heightmap': 'MOTION_BLOCKING'},
                      {'type': 'minecraft:biome'}]
        write(f'worldgen/placed_feature/{fid}.json', {'feature': f'oathbound:{fid}', 'placement': placement})
        features.append(f'oathbound:{fid}')
    # the Veilwood's close-set trees and the Ashen Reach's burned snags
    for pid, fid, count in (('veilwood_trees', 'gloamwood_tree', 3), ('veilwood_blooms', 'veilbloom_patch', 4), ('ashen_snags', 'ashen_snag', 2)):
        if fid == 'ashen_snag':
            write(f'worldgen/configured_feature/{fid}.json', {'type': f'oathbound:{fid}', 'config': {}})
        write(f'worldgen/placed_feature/{pid}.json', {'feature': f'oathbound:{fid}', 'placement': [
            {'type': 'minecraft:count', 'count': count}, {'type': 'minecraft:in_square'},
            {'type': 'minecraft:heightmap', 'heightmap': 'MOTION_BLOCKING'}, {'type': 'minecraft:biome'}]})
    roster_gloam = __import__('tools.oath.roster', fromlist=['x']).gloaming_spawners()

    def spawn(entity, weight, lo, hi):
        return {'type': f'oathbound:{entity}', 'weight': weight, 'minCount': lo, 'maxCount': hi}

    def biome(bid, fog, sky, water, grass, foliage, particles, feats, monsters):
        write(f'worldgen/biome/{bid}.json', {
            'attributes': {
                'minecraft:visual/fog_color': fog, 'minecraft:visual/sky_color': sky, 'minecraft:visual/water_fog_color': '#1a1426',
                'minecraft:visual/ambient_particles': [{'particle': {'type': f'oathbound:{p}'}, 'probability': pr} for p, pr in particles],
            },
            'carvers': [], 'downfall': 0.0, 'effects': {'water_color': water, 'grass_color': grass, 'foliage_color': foliage},
            'features': [[], [], [], [], [], [], ['oathbound:ore_duskiron'], [], [], [], feats],
            'has_precipitation': False, 'spawn_costs': {},
            'spawners': {'ambient': [], 'axolotls': [], 'creature': [], 'misc': [], 'underground_water_creature': [], 'water_ambient': [],
                         'water_creature': [], 'monster': monsters},
            'temperature': 0.5})

    biome('gloaming', '#2a2238', '#120e1c', '#3a2a5a', '#5a3a7a', '#4a2f66', (('gloam_wisp', 0.004), ('lumen_mote', 0.0015)), features,
          roster_gloam + [spawn('gloamling', 30, 2, 4), spawn('veilhound', 16, 2, 3), spawn('forsworn_knight', 8, 1, 1)])
    biome('veilwood', '#3a2458', '#160e24', '#3a2a6a', '#6a3a8a', '#5a2f7e', (('gloam_wisp', 0.012), ('lumen_mote', 0.004), ('spore', 0.002)),
          ['oathbound:gloam_fern_patch', 'oathbound:veilwood_trees', 'oathbound:veilwood_blooms', 'oathbound:gloam_ruin'],
          [spawn('shade_wraith', 18, 1, 1), spawn('veilhound', 20, 2, 3), spawn('gloam_stalker', 18, 1, 2), spawn('gloamling', 20, 2, 3)])
    biome('ashen_reach', '#3a2420', '#1a0e0c', '#4a2a22', '#4a3a36', '#3a2e2a', (('ash', 0.014), ('ember', 0.003)),
          ['oathbound:ashen_snags', 'oathbound:gloam_ruin'],
          [spawn('ashen_revenant', 22, 1, 2), spawn('forsworn_knight', 14, 1, 1), spawn('gloamling', 10, 1, 2), spawn('gloam_stalker', 8, 1, 1)])

    def point(t):
        return {'temperature': t, 'humidity': 0.0, 'continentalness': 0.0, 'erosion': 0.0, 'weirdness': 0.0, 'depth': 0.0, 'offset': 0.0}

    write('dimension/gloaming.json', {'type': 'oathbound:gloaming', 'generator': {
        'type': 'minecraft:noise', 'settings': 'oathbound:gloaming',
        'biome_source': {'type': 'minecraft:multi_noise', 'biomes': [
            {'biome': 'oathbound:gloaming', 'parameters': point(0.0)},
            {'biome': 'oathbound:ashen_reach', 'parameters': point(0.5)},
            {'biome': 'oathbound:veilwood', 'parameters': point(-0.5)}]}}})


# ====================================================================== recipes
RECIPE_IDS = set()


def recipe(name, obj):
    RECIPE_IDS.add(f'oathbound:{name}')
    write(f'recipe/{name}.json', obj)


def shaped(name, pattern, key, result, count=1, group=None, category='misc'):
    k = {c: (v if v.startswith('#') else o(v) if ':' not in v else v) for c, v in key.items()}
    obj = {'type': 'minecraft:crafting_shaped', 'category': category, 'pattern': pattern, 'key': k,
           'result': {'id': o(result) if ':' not in result else result, 'count': count}}
    if group:
        obj['group'] = group
    recipe(name, obj)


def shapeless(name, ingredients, result, count=1, category='misc'):
    ing = [(v if v.startswith('#') else o(v) if ':' not in v else v) for v in ingredients]
    recipe(name, {'type': 'minecraft:crafting_shapeless', 'category': category, 'ingredients': ing,
                  'result': {'id': o(result) if ':' not in result else result, 'count': count}})


def cooking(name, kind, ingredient, result, xp, time):
    recipe(name, {'type': f'minecraft:{kind}', 'category': 'misc', 'ingredient': o(ingredient) if ':' not in ingredient else ingredient,
                  'result': {'id': o(result)}, 'experience': xp, 'cookingtime': time})


def recipes():
    shaped('lantern_chronicle', ['LSL', 'SBS', 'LSL'], {'L': 'minecraft:leather', 'S': 'lumenite_shard', 'B': 'minecraft:book'}, 'lantern_chronicle')
    shapeless('lantern_chronicle_simple', ['minecraft:book', 'minecraft:torch'], 'lantern_chronicle')
    shapeless('oathsteel_blend', ['minecraft:iron_ingot', 'lumenite_shard', 'lumenite_shard'], 'oathsteel_blend')
    cooking('oathsteel_ingot', 'smelting', 'oathsteel_blend', 'oathsteel_ingot', 0.8, 200)
    cooking('oathsteel_ingot_blasting', 'blasting', 'oathsteel_blend', 'oathsteel_ingot', 0.8, 100)
    cooking('lumenite_shard_smelting', 'smelting', 'lumenite_ore', 'lumenite_shard', 0.7, 200)
    cooking('lumenite_shard_from_deepslate', 'smelting', 'deepslate_lumenite_ore', 'lumenite_shard', 0.7, 200)
    shapeless('lumenite_dust', ['lumenite_shard'], 'lumenite_dust', 2)
    shaped('oathsteel_block', ['III', 'III', 'III'], {'I': 'oathsteel_ingot'}, 'oathsteel_block', category='building')
    shapeless('oathsteel_ingot_from_block', ['oathsteel_block'], 'oathsteel_ingot', 9)
    shaped('oathsteel_ingot_from_nuggets', ['NNN', 'NNN', 'NNN'], {'N': 'oathsteel_nugget'}, 'oathsteel_ingot')
    shapeless('oathsteel_nugget', ['oathsteel_ingot'], 'oathsteel_nugget', 9)
    shaped('lumenite_block', ['SSS', 'SSS', 'SSS'], {'S': 'lumenite_shard'}, 'lumenite_block', category='building')
    shapeless('lumenite_shard_from_block', ['lumenite_block'], 'lumenite_shard', 9)
    shaped('wardens_lantern', [' N ', 'NSN', ' I '], {'N': 'oathsteel_nugget', 'S': 'lumenite_shard', 'I': 'oathsteel_ingot'}, 'wardens_lantern', category='equipment')
    shaped('everflame_lantern', ['IEI', 'IWI', 'IEI'], {'I': 'lanternguard_insignia', 'E': 'everflame_ember', 'W': 'wardens_lantern'}, 'everflame_lantern', category='equipment')
    shaped('oathkey', [' V ', 'WKS', ' G '], {'V': 'seal_of_valor', 'W': 'seal_of_wisdom', 'S': 'seal_of_sacrifice', 'K': 'oathsteel_ingot', 'G': 'minecraft:gold_ingot'}, 'oathkey')
    shaped('oathsteel_longsword', [' I ', ' I ', ' S '], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'oathsteel_longsword', category='equipment')
    shaped('wardens_halberd', [' II', ' SI', 'S  '], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'wardens_halberd', category='equipment')
    shaped('oathsteel_pickaxe', ['III', ' S ', ' S '], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'oathsteel_pickaxe', category='equipment')
    shaped('oathsteel_axe', ['II', 'IS', ' S'], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'oathsteel_axe', category='equipment')
    shaped('oathsteel_shovel', ['I', 'S', 'S'], {'I': 'oathsteel_ingot', 'S': 'minecraft:stick'}, 'oathsteel_shovel', category='equipment')
    shaped('oathsteel_helmet', ['III', 'I I'], {'I': 'oathsteel_ingot'}, 'oathsteel_helmet', category='equipment')
    shaped('oathsteel_chestplate', ['I I', 'III', 'III'], {'I': 'oathsteel_ingot'}, 'oathsteel_chestplate', category='equipment')
    shaped('oathsteel_leggings', ['III', 'I I', 'I I'], {'I': 'oathsteel_ingot'}, 'oathsteel_leggings', category='equipment')
    shaped('oathsteel_boots', ['I I', 'I I'], {'I': 'oathsteel_ingot'}, 'oathsteel_boots', category='equipment')
    shaped('arcanist_hood', ['SSS', 'S S'], {'S': 'spellsilk'}, 'arcanist_hood', category='equipment')
    shaped('arcanist_robe', ['S S', 'SSS', 'SSS'], {'S': 'spellsilk'}, 'arcanist_robe', category='equipment')
    shaped('arcanist_leggings', ['SSS', 'S S', 'S S'], {'S': 'spellsilk'}, 'arcanist_leggings', category='equipment')
    shaped('arcanist_boots', ['S S', 'S S'], {'S': 'spellsilk'}, 'arcanist_boots', category='equipment')
    shaped('dawnstring_longbow', [' SL', 'S L', ' SL'], {'S': 'spellsilk', 'L': 'lumenite_shard'}, 'dawnstring_longbow', category='equipment')
    shaped('shadowreap_sickle', [' II', '  E', ' S '], {'I': 'oathsteel_ingot', 'E': 'gloam_essence', 'S': 'minecraft:stick'}, 'shadowreap_sickle', category='equipment')
    shaped('lumen_flask', [' G ', 'GDG', ' G '], {'G': 'minecraft:glass', 'D': 'luminous_dust'}, 'lumen_flask', 3, category='equipment')
    shapeless('elixir_of_dawn', ['minecraft:glass_bottle', 'luminous_dust', 'gloam_essence', 'minecraft:golden_carrot'], 'elixir_of_dawn')
    shapeless('wayfarers_bread', ['minecraft:bread', 'minecraft:honey_bottle', 'minecraft:wheat'], 'wayfarers_bread', 2)
    shapeless('honeyed_mead', ['minecraft:honey_bottle', 'minecraft:wheat', 'minecraft:sugar'], 'honeyed_mead')
    shapeless('knights_stew', ['minecraft:bowl', 'minecraft:cooked_beef', 'minecraft:carrot', 'minecraft:baked_potato', 'minecraft:brown_mushroom'], 'knights_stew')
    # masonry
    shaped('wardstone_bricks', ['WW', 'WW'], {'W': 'wardstone'}, 'wardstone_bricks', 4, category='building')
    shaped('chiseled_wardstone', ['S', 'S'], {'S': 'wardstone_brick_slab'}, 'chiseled_wardstone', category='building')
    shaped('wardstone_pillar', ['W', 'W'], {'W': 'wardstone_bricks'}, 'wardstone_pillar', 2, category='building')
    shaped('wardstone_brick_stairs', ['W  ', 'WW ', 'WWW'], {'W': 'wardstone_bricks'}, 'wardstone_brick_stairs', 4, category='building')
    shaped('wardstone_brick_slab', ['WWW'], {'W': 'wardstone_bricks'}, 'wardstone_brick_slab', 6, category='building')
    shapeless('mossy_wardstone_bricks', ['wardstone_bricks', 'minecraft:moss_block'], 'mossy_wardstone_bricks', category='building')
    cooking('cracked_wardstone_bricks', 'smelting', 'wardstone_bricks', 'cracked_wardstone_bricks', 0.1, 200)
    shaped('wardstone', ['SC', 'CS'], {'S': 'minecraft:sandstone', 'C': 'minecraft:calcite'}, 'wardstone', 4, category='building')
    shaped('gloamstone_bricks', ['GG', 'GG'], {'G': 'gloamstone'}, 'gloamstone_bricks', 4, category='building')
    shapeless('gloamwood_planks', ['gloamwood_log'], 'gloamwood_planks', 4, category='building')
    shaped('wayshrine_brazier', ['LSL', ' G ', 'GGG'], {'L': 'minecraft:gold_ingot', 'S': 'lumenite_shard', 'G': 'wardstone_bricks'}, 'wayshrine_brazier')


def generate():
    from . import building, gear, wares, roster
    recipes()
    building.recipes()
    gear.recipes()
    wares.recipes()
    wares.jukebox()
    advancements()
    loot_tables()
    for b in building.TABLE:
        building.loot(b)
    roster.loot()
    tags()
    roster.tags()
    for path, values in building.TAGS.items():
        tag(path, values, 'minecraft')
    gear.tags()
    wares.tags()
    worldgen()
    roster.spawns()
    building.worldgen()
    gear.worldgen()
    from . import landmarks
    landmarks.worldgen()
    landmarks.loot()
    landmarks.tags()
    from . import paintings
    paintings.data()
    from . import enchantments
    enchantments.data()
    flush_tags()
    print('data written')


if __name__ == '__main__':
    # Run through the package module, not __main__: the helper modules import tools.oath.data, and their tags must
    # land in the same table that flush_tags() writes.
    from tools.oath import data as _data
    _data.generate()
