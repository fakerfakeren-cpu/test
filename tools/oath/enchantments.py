"""The Order's enchantments, data-driven in the vanilla format: Gloambane, Dawnfire, Warding and Wayfarer.

data.py calls data(); lang.py reads TEXT.
"""
from . import data as D


def lin(base, per):
    return {'type': 'minecraft:linear', 'base': base, 'per_level_above_first': per}


def costs(min_base, min_per, max_base, max_per):
    return {'min_cost': {'base': min_base, 'per_level_above_first': min_per}, 'max_cost': {'base': max_base, 'per_level_above_first': max_per}}


def enchantment(eid, max_level, weight, anvil, supported, slots, effects, primary=None, exclusive=None, cost=(5, 8, 25, 8)):
    e = {'anvil_cost': anvil, 'description': {'translate': f'enchantment.oathbound.{eid}'}, 'effects': effects, 'max_level': max_level,
         'slots': slots, 'supported_items': supported, 'weight': weight, **costs(*cost)}
    if primary:
        e['primary_items'] = primary
    if exclusive:
        e['exclusive_set'] = exclusive
    D.write(f'enchantment/{eid}.json', e)


def data():
    enchantment('gloambane', 5, 5, 2, '#minecraft:enchantable/weapon', ['mainhand'], {
        'minecraft:damage': [{'effect': {'type': 'minecraft:add', 'value': lin(2.5, 2.5)},
                              'requirements': {'condition': 'minecraft:entity_properties', 'entity': 'this',
                                               'predicate': {'minecraft:entity_type': '#oathbound:gloam_creatures'}}}]},
        primary='#minecraft:enchantable/melee_weapon', exclusive='#minecraft:exclusive_set/damage')
    enchantment('dawnfire', 2, 1, 8, '#minecraft:enchantable/melee_weapon', ['mainhand'], {
        'minecraft:post_attack': [
            {'affected': 'victim', 'enchanted': 'attacker',
             'effect': {'type': 'minecraft:ignite', 'duration': lin(3.0, 3.0)},
             'requirements': {'condition': 'minecraft:all_of', 'terms': [
                 {'condition': 'minecraft:damage_source_properties', 'predicate': {'is_direct': True}},
                 {'condition': 'minecraft:any_of', 'terms': [
                     {'condition': 'minecraft:entity_properties', 'entity': 'this',
                      'predicate': {'minecraft:entity_type': '#minecraft:undead'}},
                     {'condition': 'minecraft:entity_properties', 'entity': 'this',
                      'predicate': {'minecraft:entity_type': '#oathbound:gloam_creatures'}}]}]}}]},
        cost=(15, 20, 65, 20))
    enchantment('warding', 4, 3, 2, '#minecraft:enchantable/armor', ['armor'], {
        'minecraft:damage_protection': [{'effect': {'type': 'minecraft:add', 'value': lin(2.0, 2.0)},
                                         'requirements': {'condition': 'minecraft:damage_source_properties',
                                                          'predicate': {'tags': [{'id': 'minecraft:witch_resistant_to', 'expected': True},
                                                                                 {'id': 'minecraft:bypasses_invulnerability', 'expected': False}]}}}]},
        exclusive='#minecraft:exclusive_set/armor', cost=(5, 8, 20, 8))
    enchantment('wayfarer', 3, 2, 4, '#minecraft:enchantable/foot_armor', ['feet'], {
        'minecraft:attributes': [{'id': 'oathbound:enchantment.wayfarer', 'attribute': 'minecraft:movement_speed',
                                  'amount': lin(0.04, 0.04), 'operation': 'add_multiplied_base'}]},
        cost=(10, 10, 40, 10))
    D.tag('enchantment/non_treasure', ['gloambane', 'warding', 'wayfarer'], 'minecraft')
    D.tag('enchantment/treasure', ['dawnfire'], 'minecraft')
    D.tag('enchantment/exclusive_set/damage', ['gloambane'], 'minecraft')
    D.tag('enchantment/exclusive_set/armor', ['warding'], 'minecraft')


TEXT = {
    'enchantment.oathbound.gloambane': 'Gloambane',
    'enchantment.oathbound.dawnfire': 'Dawnfire',
    'enchantment.oathbound.warding': 'Warding',
    'enchantment.oathbound.wayfarer': 'Wayfarer',
}
