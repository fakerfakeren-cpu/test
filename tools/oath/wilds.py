"""The places off the Path: seven sites in seven kinds of country (WildSketches.java draws them), their chest loot,
the Tales quests for finding them and felling their keepers, and their text.

data.py calls structures(), chests() and quests(); lang.py merges QUESTS and TEXT.
"""
from . import data as D

def I(*a, **k):
    return D.item(*a, **k)


def P(*a, **k):
    return D.pool(*a, **k)


# sketch id: (step, spacing, separation, salt, biomes)
STRUCTURES = {
    'grove_shrine': ('surface_structures', 44, 16, 81311401,
                     ['minecraft:flower_forest', 'minecraft:birch_forest', 'minecraft:old_growth_birch_forest', 'minecraft:forest',
                      'minecraft:cherry_grove']),
    'bog_hut': ('surface_structures', 40, 14, 81311403, ['minecraft:swamp', 'minecraft:mangrove_swamp']),
    'cinder_sanctum': ('surface_structures', 48, 16, 81311405,
                       ['minecraft:desert', 'minecraft:badlands', 'minecraft:eroded_badlands', 'minecraft:wooded_badlands']),
    'watchtower': ('surface_structures', 34, 12, 81311407,
                   ['minecraft:windswept_hills', 'minecraft:windswept_gravelly_hills', 'minecraft:windswept_forest', 'minecraft:meadow',
                    'minecraft:plains', 'minecraft:snowy_plains', 'minecraft:savanna_plateau']),
    'tideglass_grotto': ('surface_structures', 36, 12, 81311409, ['minecraft:beach', 'minecraft:stony_shore', 'minecraft:snowy_beach']),
    'lumenite_mine': ('underground_structures', 30, 10, 81311411,
                      ['#minecraft:is_forest', '#minecraft:is_taiga', '#minecraft:is_hill', 'minecraft:plains', 'minecraft:meadow',
                       'minecraft:savanna', 'minecraft:snowy_plains']),
    'shattered_observatory': ('surface_structures', 22, 8, 81311413, ['oathbound:gloaming']),
}


def structures():
    for sid, (step, spacing, sep, salt, biomes) in STRUCTURES.items():
        D.write(f'worldgen/structure/{sid}.json', {
            'type': 'oathbound:sketch', 'biomes': f'#oathbound:has_structure/{sid}', 'spawn_overrides': {},
            'step': step, 'terrain_adaptation': 'none', 'sketch': sid})
        D.write(f'worldgen/structure_set/{sid}.json', {
            'structures': [{'structure': f'oathbound:{sid}', 'weight': 1}],
            'placement': {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}})
        D.tag(f'worldgen/biome/has_structure/{sid}', biomes)
        D.tag(f'worldgen/structure/{sid}', [sid])


def chests():
    ENCH = D.ENCHANT_LEVELS
    return {
        'grove_offering': [P([I('glimmer_antler', 1, 2, 12), I('moonpetal', 2, 5, 14), I('dusk_lily', 2, 5, 14), I('minecraft:emerald', 2, 6, 12),
                              I('minecraft:golden_carrot', 2, 5, 10), I('raw_venison', 2, 4, 10), I('elixir_of_the_wayfarer', 1, 1, 6),
                              I('gloamwood_sapling', 1, 2, 4), I('minecraft:golden_apple', 1, 1, 3)], rolls=(4, 7))],
        'bog_hut_larder': [P([I('hag_eye', 1, 2, 10), I('gloam_essence', 1, 3, 12), I('minecraft:fermented_spider_eye', 1, 3, 12),
                              I('minecraft:glass_bottle', 2, 5, 14), I('minecraft:slime_ball', 1, 4, 10), I('minecraft:bone', 2, 6, 12),
                              I('elixir_of_shrouds', 1, 1, 5), I('duskwine', 1, 2, 8), I('minecraft:moss_block', 1, 3, 8)], rolls=(4, 7))],
        'cinder_sanctum_vault': [P([I('minecraft:gold_ingot', 3, 8, 14), I('gravegold_ingot', 1, 3, 10), I('ember_core', 1, 2, 10),
                                    I('minecraft:diamond', 1, 3, 6), I('minecraft:gold_block', 1, 1, 4), I('minecraft:book', 1, 1, 6, funcs=[ENCH]),
                                    I('elixir_of_valor', 1, 2, 6), I('minecraft:blaze_powder', 2, 5, 8)], rolls=(4, 7))],
        'cinder_sanctum_offerings': [P([I('minecraft:gold_nugget', 4, 12, 16), I('emberroot', 2, 5, 12), I('spiced_cider', 1, 2, 8),
                                        I('minecraft:coal', 3, 8, 12), I('minecraft:dried_kelp', 2, 6, 8), I('emberroot_stew', 1, 1, 6)],
                                      rolls=(3, 6))],
        'watchtower_armory': [P([I('minecraft:arrow', 8, 24, 16), I('minecraft:iron_ingot', 2, 5, 12), I('tidebronze_ingot', 2, 4, 12),
                                 I('minecraft:shield', 1, 1, 6), I('minecraft:crossbow', 1, 1, 4), I('tidebronze_gladius', 1, 1, 3),
                                 I('trail_rations', 1, 3, 10), I('minecraft:iron_sword', 1, 1, 5)], rolls=(3, 6))],
        'watchtower_lookout': [P([I('minecraft:spyglass', 1, 1, 6), I('minecraft:map', 1, 1, 8), I('trail_rations', 1, 2, 10),
                                  I('honeyed_mead', 1, 2, 10), I('minecraft:torch', 6, 16, 12), I('lumenite_shard', 1, 4, 12),
                                  I('huntsmans_horn', 1, 1, 2)], rolls=(3, 5))],
        'tideglass_hoard': [P([I('minecraft:prismarine_crystals', 2, 6, 14), I('minecraft:nautilus_shell', 1, 2, 8),
                               I('minecraft:heart_of_the_sea', 1, 1, 2), I('tidebronze_ingot', 2, 4, 12), I('elixir_of_tides', 1, 2, 8),
                               I('salted_cod', 2, 4, 10), I('minecraft:gold_ingot', 1, 4, 10), I('minecraft:book', 1, 1, 5, funcs=[ENCH])],
                             rolls=(4, 6))],
        'grotto_wreck': [P([I('salted_cod', 1, 3, 12), I('minecraft:string', 2, 6, 12), I('minecraft:emerald', 1, 4, 10),
                            I('minecraft:compass', 1, 1, 5), I('minecraft:gold_nugget', 3, 9, 12), I('minecraft:paper', 1, 4, 10),
                            I('minecraft:iron_nugget', 3, 9, 10)], rolls=(3, 6))],
        'mine_cache': [P([I('lumenite_shard', 2, 6, 16), I('minecraft:iron_ingot', 1, 4, 12), I('minecraft:coal', 4, 12, 14),
                          I('minecraft:torch', 8, 20, 12), I('minecraft:rail', 4, 12, 10), I('trail_rations', 1, 2, 8),
                          I('minecraft:iron_pickaxe', 1, 1, 4, funcs=[{'function': 'minecraft:set_damage',
                                                                         'damage': {'type': 'minecraft:uniform', 'min': 0.2, 'max': 0.7}}]),
                          I('lumenite_dust', 2, 6, 10)], rolls=(3, 6))],
        'mine_foreman': [P([I('lumenite_block', 1, 2, 6), I('runesilver_ingot', 1, 3, 10), I('minecraft:diamond', 1, 2, 6),
                            I('minecraft:gold_ingot', 2, 5, 10), I('oathsteel_ingot', 1, 3, 8), I('minecraft:tnt', 1, 3, 8),
                            I('minecraft:book', 1, 1, 4, funcs=[ENCH])], rolls=(3, 5))],
        'observatory_charts': [P([I('spellsilk', 1, 3, 12), I('luminous_dust', 2, 6, 14), I('runesilver_ingot', 1, 3, 10),
                                  I('duskiron_ingot', 1, 3, 10), I('minecraft:book', 1, 1, 8, funcs=[ENCH]), I('minecraft:spyglass', 1, 1, 6),
                                  I('heart_of_the_gloam', 1, 1, 2), I('minecraft:experience_bottle', 2, 6, 10)], rolls=(4, 6))],
    }


# lore found only at these sites (wares.py adds them to its PAGES and loot)
PAGES = [
    ('grove_king', 'The Stag in the Ring', [
        'The rangers left the old ring alone. Something in it had been king there before the Order,',
        'and would be king after. They left it salt and apples at midsummer, and walked round.']),
    ('bog_mother', 'The Bog Mother\'s Bargain', [
        'She will cure anything, the swamp-folk say, for the right bones. She has never said whose.',
        'Every hag in the mire is one of her daughters, and every one of them has her lanterns.']),
    ('sun_cult', 'Of the Sun-Cult', [
        'Before the Lanternguard carried the first dawn, the desert-folk worshipped the noon.',
        'They built a furnace that could walk, to carry their sun to war. It is still carrying it.']),
    ('last_watch', 'The Last Watch', [
        'Light the signal if the dead walk. Light it if the sea rises. Light it if you are afraid.',
        'The tower is empty now, but the fire is always laid. The stone warden sees to that.']),
    ('drowned_choir', 'The Drowned Choir', [
        'When the chapel went under, the choir went down still singing. Their hymn is in the grotto now,',
        'echoing off the crystal. Sailors who hear it at low tide say it is almost beautiful.']),
    ('lumenite_rush', 'The Lumenite Rush', [
        'For a summer everyone dug for lumenite. Then the mites came up out of the deep veins, eating',
        'the light from the lamps, and the miners came up out of the shafts in the dark.']),
    ('star_readers', 'The Star-Readers', [
        'They watched the sky for the Gloam\'s coming, and they saw it: every star going out, one by one,',
        'like lamps down a long street. The last entry in their chart is only a date.']),
]

# chest table -> [(ware, weight)]
LOOT = {
    'grove_offering': [('lore_page_grove_king', 6), ('elixir_of_the_wayfarer', 4), ('music_disc_wayshrine_nocturne', 1)],
    'bog_hut_larder': [('lore_page_bog_mother', 6), ('moonpetal_tea', 4), ('duskwine', 4)],
    'cinder_sanctum_vault': [('lore_page_sun_cult', 6), ('music_disc_crown_of_ash', 2), ('sunshard_talisman', 1)],
    'cinder_sanctum_offerings': [('lore_page_sun_cult', 3), ('emberroot_stew', 6)],
    'watchtower_lookout': [('lore_page_last_watch', 6), ('huntsmans_horn', 2), ('music_disc_lanternguard_hymn', 1)],
    'watchtower_armory': [('lanternguard_signet', 1), ('hearth_pie', 6)],
    'tideglass_hoard': [('lore_page_drowned_choir', 6), ('bell_of_the_drowned', 1), ('music_disc_chapel_tides', 2)],
    'grotto_wreck': [('salted_cod', 8), ('lore_page_drowned_choir', 2)],
    'mine_cache': [('lore_page_lumenite_rush', 5), ('trail_rations', 6)],
    'mine_foreman': [('lore_page_lumenite_rush', 6), ('elixir_of_the_wayfarer', 3)],
    'observatory_charts': [('lore_page_star_readers', 8), ('veyls_mirror', 1), ('elixir_of_shrouds', 4)],
}

# quest id: (frame, icon, criteria, English title, description, hint)
QUEST_TABLE = {
    'grove_king': ('challenge', 'grove_kings_crown', {'slain': D.impossible(), 'killed': D.killed('elderhorn')},
                   'The Grove King', 'Wake the Elderhorn in his ring of stones, and fell him.',
                   'A ring of runestones in the flowering woods. Sidestep his charge; strike hard while he kneels.'),
    'bog_mother': ('challenge', 'bog_mothers_lantern', {'slain': D.impossible(), 'killed': D.killed('bog_mother')},
                   'The Mother of Hags', 'Find the stilt-house in the swamp and put out the Bog Mother\'s lanterns.',
                   'Swamps. Kill her bone-children first: while they live, her lanterns shield her.'),
    'cinder_colossus': ('challenge', 'cinder_heart', {'slain': D.impossible(), 'killed': D.killed('cinder_colossus')},
                        'The Walking Furnace', 'Go down into the sun-cult\'s sanctum and quench the Cinder Colossus.',
                        'A stepped pyramid in the desert or the badlands. Water cracks it; its open core takes double harm.'),
    'last_watch': ('task', 'oathsteel_lantern', {'found': D.entered('watchtower')},
                   'The Last Watch', 'Climb a Lanternguard watchtower.',
                   'They stand on windy heights: hills, meadows and plains. A stonewarden keeps the door.'),
    'tideglass': ('task', 'barnacled_tidestone_bricks', {'found': D.entered('tideglass_grotto')},
                  'Crystal Under the Rocks', 'Find the drowned choir\'s grotto by the sea.',
                  'Beaches and stony shores. Listen for singing at the waterline.'),
    'delve': ('task', 'lumenite_ore', {'found': D.entered('lumenite_mine')},
              'The Lumenite Delve', 'Climb down an abandoned lumenite mine.',
              'Look for a timber headframe over a shaft in the forests and hills. Take spare lumenite: the mites drink lantern oil.'),
    'star_readers': ('task', 'gloamglass', {'found': D.entered('shattered_observatory')},
                     'Where the Stars Went Out', 'Find the star-readers\' shattered observatory in the Gloaming.',
                     'A broken glass dome on a Gloaming island. Shade wraiths nest in its gallery.'),
}


def quests(any_of):
    """Adds the Tales quests to data.quest_criteria's table (all hang off 'root')."""
    for qid, (frame, icon, crit, *_rest) in QUEST_TABLE.items():
        any_of(qid, frame, icon, **crit)


PARENTS = {q: 'root' for q in QUEST_TABLE}
QUESTS = {q: (t[3], t[4], t[5]) for q, t in QUEST_TABLE.items()}

TEXT = {
    'message.oathbound.elderhorn.bloom': 'The Grove King kneels to drink from the grove. Strike hard to break the trance!',
    'message.oathbound.bog_mother.brood': 'Her bone-children shield the Bog Mother. Kill the brood!',
    'message.oathbound.cinder_colossus.molten': 'The Colossus runs molten. Its every step scorches.',
    'title.oathbound.grove_king.slain': 'The Grove King Falls',
    'title.oathbound.grove_king.slain.sub': 'The old woods are quiet',
    'title.oathbound.bog_mother.slain': 'The Lanterns Go Out',
    'title.oathbound.bog_mother.slain.sub': 'The Bog Mother sinks into the mire',
    'title.oathbound.cinder_colossus.slain': 'The Furnace Is Quenched',
    'title.oathbound.cinder_colossus.slain.sub': 'The sun-cult\'s engine is still at last',
}
