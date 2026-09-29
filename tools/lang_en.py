"""English text for Rimeheart: names, tooltips, messages, the Warden's Journal and the quests."""

NAMES = {
    'block.rimeheart.rimestone': 'Rimestone',
    'block.rimeheart.permafrost': 'Permafrost',
    'block.rimeheart.frostiron_ore': 'Frostiron Ore',
    'block.rimeheart.rime_crystal_ore': 'Rime Crystal Ore',
    'block.rimeheart.rime_crystal_cluster': 'Rime Crystal Cluster',
    'block.rimeheart.frostiron_block': 'Block of Frostiron',
    'block.rimeheart.rime_crystal_block': 'Block of Rime Crystal',
    'block.rimeheart.rimestone_bricks': 'Rimestone Bricks',
    'block.rimeheart.cracked_rimestone_bricks': 'Cracked Rimestone Bricks',
    'block.rimeheart.chiseled_rimestone_bricks': 'Chiseled Rimestone Bricks',
    'block.rimeheart.hollow_rimestone_bricks': 'Rimestone Bricks',
    'block.rimeheart.frost_lamp': 'Frost Lamp',
    'block.rimeheart.glacial_altar': 'Glacial Altar',
    'item.rimeheart.wardens_journal': "Warden's Journal",
    'item.rimeheart.raw_frostiron': 'Raw Frostiron',
    'item.rimeheart.frostiron_ingot': 'Frostiron Ingot',
    'item.rimeheart.frostiron_nugget': 'Frostiron Nugget',
    'item.rimeheart.rime_shard': 'Rime Shard',
    'item.rimeheart.wraith_essence': 'Wraith Essence',
    'item.rimeheart.glacial_heart': 'Glacial Heart',
    'item.rimeheart.sovereign_core': "Sovereign's Core",
    'item.rimeheart.frostiron_sword': 'Frostiron Sword',
    'item.rimeheart.frostiron_pickaxe': 'Frostiron Pickaxe',
    'item.rimeheart.frostiron_axe': 'Frostiron Axe',
    'item.rimeheart.frostiron_shovel': 'Frostiron Shovel',
    'item.rimeheart.frostbite_blade': 'Frostbite Blade',
    'item.rimeheart.glacier_maul': 'Glacier Maul',
    'item.rimeheart.rimebow': 'Rimebow',
    'item.rimeheart.blizzard_staff': 'Blizzard Staff',
    'item.rimeheart.winterfang': 'Winterfang',
    'item.rimeheart.frost_charge': 'Frost Charge',
    'item.rimeheart.winter_horn': 'Winter Horn',
    'item.rimeheart.hearthfire_stew': 'Hearthfire Stew',
    'item.rimeheart.frostiron_helmet': 'Frostiron Helmet',
    'item.rimeheart.frostiron_chestplate': 'Frostiron Chestplate',
    'item.rimeheart.frostiron_leggings': 'Frostiron Leggings',
    'item.rimeheart.frostiron_boots': 'Frostiron Boots',
    'item.rimeheart.wraithweave_hood': 'Wraithweave Hood',
    'item.rimeheart.wraithweave_robe': 'Wraithweave Robe',
    'item.rimeheart.wraithweave_leggings': 'Wraithweave Leggings',
    'item.rimeheart.wraithweave_boots': 'Wraithweave Boots',
    'item.rimeheart.frost_wraith_spawn_egg': 'Frost Wraith Spawn Egg',
    'item.rimeheart.shardling_spawn_egg': 'Shardling Spawn Egg',
    'item.rimeheart.frost_sovereign_spawn_egg': 'Frost Sovereign Spawn Egg',
    'entity.rimeheart.frost_wraith': 'Frost Wraith',
    'entity.rimeheart.shardling': 'Shardling',
    'entity.rimeheart.frost_sovereign': 'The Frost Sovereign',
    'entity.rimeheart.ice_shard': 'Ice Shard',
    'entity.rimeheart.frost_charge': 'Frost Charge',
    'itemGroup.rimeheart': 'Rimeheart',
}

TOOLTIPS = {
    'item.rimeheart.rime_shard.desc.1': 'Cold enough to sting. Used in frost gear and charges.',
    'item.rimeheart.wraith_essence.desc.1': 'What remains of a Frost Wraith. Weaves into cloth.',
    'item.rimeheart.glacial_heart.desc.1': 'A heart of ice that never melts.',
    'item.rimeheart.glacial_heart.desc.2': 'Key to the Winter Horn.',
    'item.rimeheart.sovereign_core.desc.1': 'The frozen core of the Frost Sovereign.',
    'item.rimeheart.sovereign_core.desc.2': 'Reforges a Frostbite Blade into Winterfang.',
    'item.rimeheart.frostbite_blade.desc.1': 'Hits chill; frozen foes take +30% damage (Shatter).',
    'item.rimeheart.frostbite_blade.desc.2': 'Use: Cold Snap - chill every enemy within 4.5 blocks.',
    'item.rimeheart.frostbite_blade.desc.3': '12 second cooldown.',
    'item.rimeheart.glacier_maul.desc.1': 'Heavy and slow. Hits chill.',
    'item.rimeheart.glacier_maul.desc.2': 'Use on the ground: Permafrost Slam.',
    'item.rimeheart.glacier_maul.desc.3': 'Ice spikes launch and freeze nearby enemies. 5 s cooldown.',
    'item.rimeheart.rimebow.desc.1': 'Needs no arrows: fires icicles drawn from the air.',
    'item.rimeheart.rimebow.desc.2': 'Full draws hit harder and chill more.',
    'item.rimeheart.blizzard_staff.desc.1': 'Hold use to breathe a blizzard (up to 5 seconds).',
    'item.rimeheart.blizzard_staff.desc.2': 'Light damage, heavy chill, gentle push.',
    'item.rimeheart.winterfang.desc.1': 'Hits chill hard; frozen foes take +40% damage.',
    'item.rimeheart.winterfang.desc.2': 'Use: Absolute Zero - freeze everything within 8 blocks.',
    'item.rimeheart.winterfang.desc.3': '20 second cooldown.',
    'item.rimeheart.frost_charge.desc.1': 'Throw: a freezing burst that chills mobs',
    'item.rimeheart.frost_charge.desc.2': 'and skins nearby water with melting ice.',
    'item.rimeheart.winter_horn.desc.1': 'Sound it at a Glacial Altar',
    'item.rimeheart.winter_horn.desc.2': 'to wake the Frost Sovereign.',
    'item.rimeheart.hearthfire_stew.desc.1': 'Thaws you out instantly and grants Regeneration.',
}

MESSAGES = {
    'message.rimeheart.altar.hint': 'The altar is cold and silent. Sound a Winter Horn here to wake what sleeps below.',
    'message.rimeheart.altar.busy': 'The winter is already stirring.',
    'message.rimeheart.horn.echo': 'The note echoes over the snow... but nothing answers. Find a Glacial Altar.',
    'message.rimeheart.ritual.begin': 'The horn\'s note does not fade. A blizzard gathers around the altar...',
    'message.rimeheart.boss.phase2': 'The Frost Sovereign calls the Long Winter down upon you!',
    'title.rimeheart.ritual': 'The Long Winter Stirs',
    'title.rimeheart.ritual.sub': 'Something vast wakes beneath the ice',
    'title.rimeheart.sovereign.sub': 'Heart of the Long Winter',
    'title.rimeheart.victory': 'The Thaw',
    'title.rimeheart.victory.sub': 'The Frost Sovereign is shattered',
    'command.rimeheart.help.header': 'Rimeheart commands:',
    'command.rimeheart.help.kit': '/rimeheart kit - every weapon, armour set and gadget',
    'command.rimeheart.help.summon': '/rimeheart summon - start the Winter Horn ritual in front of you',
    'command.rimeheart.help.build': '/rimeheart build sanctum - build a Frozen Sanctum here',
    'command.rimeheart.help.locate': '/rimeheart locate sanctum - nearest naturally generated Sanctum',
    'command.rimeheart.kit': 'Rimeheart kit delivered.',
    'command.rimeheart.build': 'The Frozen Sanctum rises from the snow.',
    'command.rimeheart.locate': 'Nearest Frozen Sanctum: %s, %s (%s blocks away)',
    'command.rimeheart.locate.none': 'No Frozen Sanctum found nearby. They only form in snowy biomes.',
}

SUBTITLES = {
    'freeze': 'Something freezes solid', 'ice_shatter': 'Ice shatters', 'cold_snap': 'Cold snap',
    'glacier_slam': 'Glacier Maul slams', 'blizzard': 'Blizzard howls', 'icicle_shoot': 'Icicle flies',
    'wraith_ambient': 'Frost Wraith moans', 'wraith_hurt': 'Frost Wraith hurts', 'wraith_death': 'Frost Wraith fades',
    'shardling_chitter': 'Shardling chitters', 'winter_horn': 'Winter Horn sounds', 'sovereign_roar': 'Frost Sovereign roars',
    'sovereign_death': 'Frost Sovereign shatters',
}

# ---------------------------------------------------------------------------- quests (advancements)
# id, parent, icon, title, description, frame, criteria spec
QUESTS = [
    ('root', None, 'rimeheart:wardens_journal', "The Warden's Journal", 'The Long Winter has come. Open your journal.', 'task', ('tick',)),
    ('frostiron', 'root', 'rimeheart:raw_frostiron', 'Cold Iron', 'Mine Frostiron Ore', 'task', ('item', 'rimeheart:raw_frostiron')),
    ('ingot', 'frostiron', 'rimeheart:frostiron_ingot', 'Forged in the Frost', 'Smelt a Frostiron Ingot', 'task', ('item', 'rimeheart:frostiron_ingot')),
    ('pickaxe', 'ingot', 'rimeheart:frostiron_pickaxe', 'Deeper Still', 'Craft a Frostiron Pickaxe', 'task', ('item', 'rimeheart:frostiron_pickaxe')),
    ('frostiron_armor', 'ingot', 'rimeheart:frostiron_chestplate', 'Dressed for the Weather', 'Wear a full set of Frostiron armour', 'goal',
     ('all_items', ['rimeheart:frostiron_helmet', 'rimeheart:frostiron_chestplate', 'rimeheart:frostiron_leggings', 'rimeheart:frostiron_boots'])),
    ('hearthfire', 'root', 'rimeheart:hearthfire_stew', 'A Warm Meal', 'Cook a Hearthfire Stew', 'task', ('item', 'rimeheart:hearthfire_stew')),
    ('rime_shard', 'frostiron', 'rimeheart:rime_shard', 'Rime and Crystal', 'Collect a Rime Shard', 'task', ('item', 'rimeheart:rime_shard')),
    ('frost_charge', 'rime_shard', 'rimeheart:frost_charge', 'Snowball, Upgraded', 'Craft a Frost Charge', 'task', ('item', 'rimeheart:frost_charge')),
    ('rimebow', 'rime_shard', 'rimeheart:rimebow', 'No Arrows Required', 'Craft the Rimebow', 'task', ('item', 'rimeheart:rimebow')),
    ('glacier_maul', 'rime_shard', 'rimeheart:glacier_maul', 'Permafrost Slam', 'Craft the Glacier Maul', 'goal', ('item', 'rimeheart:glacier_maul')),
    ('wraith', 'frostiron', 'rimeheart:wraith_essence', 'Ghost of the Snow', 'Defeat a Frost Wraith', 'task', ('kill', 'rimeheart:frost_wraith')),
    ('shardling', 'rime_shard', 'rimeheart:rime_crystal_cluster', 'Something in the Crystal', 'Defeat a Shardling', 'task', ('kill', 'rimeheart:shardling')),
    ('frostbite_blade', 'wraith', 'rimeheart:frostbite_blade', 'Frostbite', 'Craft the Frostbite Blade', 'goal', ('item', 'rimeheart:frostbite_blade')),
    ('wraithweave', 'wraith', 'rimeheart:wraithweave_robe', 'Woven from Ghosts', 'Wear a full set of Wraithweave', 'goal',
     ('all_items', ['rimeheart:wraithweave_hood', 'rimeheart:wraithweave_robe', 'rimeheart:wraithweave_leggings', 'rimeheart:wraithweave_boots'])),
    ('blizzard_staff', 'wraith', 'rimeheart:blizzard_staff', 'Pocket Blizzard', 'Craft the Blizzard Staff', 'goal', ('item', 'rimeheart:blizzard_staff')),
    ('sanctum', 'frostiron', 'rimeheart:chiseled_rimestone_bricks', 'The Frozen Sanctum', 'Find a Frozen Sanctum', 'goal', ('structure', 'rimeheart:frozen_sanctum')),
    ('vault', 'sanctum', 'rimeheart:glacial_heart', 'A Heart of Ice', 'Obtain a Glacial Heart', 'challenge', ('item', 'rimeheart:glacial_heart')),
    ('winter_horn', 'vault', 'rimeheart:winter_horn', 'Call of Winter', 'Craft the Winter Horn', 'goal', ('item', 'rimeheart:winter_horn')),
    ('sovereign', 'winter_horn', 'rimeheart:sovereign_core', 'The Thaw', 'Defeat the Frost Sovereign', 'challenge', ('kill', 'rimeheart:frost_sovereign')),
    ('winterfang', 'sovereign', 'rimeheart:winterfang', 'Winterfang', 'Reforge the Frostbite Blade into Winterfang', 'challenge', ('item', 'rimeheart:winterfang')),
]

QUEST_HINTS = {
    'root': 'Quests unlock one after another. Finished quests glow blue until you claim their reward here.',
    'frostiron': 'Frostiron Ore only forms under snowy biomes (snowy plains, taiga, slopes, peaks, ice spikes). Bring an iron pickaxe.',
    'ingot': 'Smelt Raw Frostiron or Frostiron Ore in a furnace or blast furnace.',
    'pickaxe': 'Three Frostiron Ingots and two sticks. Frostiron sits between iron and diamond.',
    'frostiron_armor': 'Any Frostiron piece makes you immune to freezing. The full set freezes water underfoot and chills melee attackers.',
    'hearthfire': 'Bowl, Baked Potato, Carrot and Sweet Berries. It thaws you out instantly.',
    'rime_shard': 'Rime Crystal Ore glows faintly in cold stone. Crystal clusters in ruins drop shards too.',
    'frost_charge': 'Rime Shard, Snowball and Gunpowder make two. Throw one on water to cross it.',
    'rimebow': 'Two Frostiron Ingots, two Rime Shards and three string, shaped like a bow.',
    'glacier_maul': 'Block of Rime Crystal between two Frostiron Ingots, over two sticks.',
    'wraith': 'Frost Wraiths haunt snowy biomes at night and fade in sunlight. Hide from their ice volleys behind cover.',
    'shardling': 'Some crystal clusters are nests. Break one without Silk Touch and a Shardling may burst out.',
    'frostbite_blade': 'A Frostiron Sword wrapped in three Rime Shards and a Wraith Essence.',
    'wraithweave': 'Wraith Essence armour. The full set grants speed on snow and a vanishing escape at low health.',
    'blizzard_staff': 'A Block of Rime Crystal, Wraith Essence and a Frostiron Ingot on a diagonal.',
    'sanctum': 'Sanctums are buried under snowy plains and taiga. Look for a ring of broken pillars and a stairwell down.',
    'vault': 'The Sanctum hall hides more than its altar. One wall sounds hollow, where the bricks are cracked.',
    'winter_horn': 'Two Wraith Essence, four Frostiron Ingots and the Glacial Heart.',
    'sovereign': 'Sound the Winter Horn at a Glacial Altar. Bring stew, armour and room to dodge the telegraphed eruptions.',
    'winterfang': "Place the Sovereign's Core above a Frostbite Blade.",
}

JOURNAL_UI = {
    'journal.rimeheart.title': "Warden's Journal",
    'journal.rimeheart.tab.story': 'Story',
    'journal.rimeheart.tab.guide': 'Field Guide',
    'journal.rimeheart.tab.quests': 'Quests',
    'journal.rimeheart.progress': '%s / %s quests',
    'journal.rimeheart.chapter.0': 'First Frost',
    'journal.rimeheart.chapter.1': 'Rime and Crystal',
    'journal.rimeheart.chapter.2': 'Things in the Snow',
    'journal.rimeheart.chapter.3': 'The Frozen Sanctum',
    'journal.rimeheart.chapter.4': 'The Long Winter',
    'journal.rimeheart.status.locked': 'Locked. Finish "%s" first.',
    'journal.rimeheart.status.active': 'In progress',
    'journal.rimeheart.status.ready': 'Complete! Claim your reward.',
    'journal.rimeheart.status.claimed': 'Complete. Reward claimed.',
    'journal.rimeheart.locked_title': '? ? ?',
    'journal.rimeheart.rewards': 'Rewards',
    'journal.rimeheart.xp': '+%s XP',
    'journal.rimeheart.claim': 'Claim Reward',
    'journal.rimeheart.claimed': 'Claimed',
    'journal.rimeheart.page': 'Page %s / %s',
    'journal.rimeheart.claim.done': 'Reward claimed: %s',
    'journal.rimeheart.claim.not_ready': 'That quest is not complete yet.',
    'journal.rimeheart.claim.already': 'You already claimed that reward.',
    'journal.rimeheart.claim.unknown': 'Unknown quest.',
    'journal.rimeheart.story': (
        'The Last Warden\n\n'
        'Long ago the northern kingdoms kept a pact with winter. Their Wardens tended the Glacial Altars, and the cold '
        'stayed in the far north where it belonged.\n\n'
        'The kingdoms forgot. The altars froze over, the Wardens died out one by one, and deep beneath the ice the '
        'heart of winter itself, the Frost Sovereign, stopped sleeping.\n\n'
        'Now the Long Winter is waking. Frost Wraiths drift over the snow at night, the ghosts of those who froze in '
        'the old kingdoms. Crystal Shardlings nest in the rime. Stone turns to rimestone, and iron in the cold earth '
        'turns to Frostiron.\n\n'
        'I am the last Warden, and this journal is all I can leave you.\n\n'
        'Mine the cold iron. Learn how the chill works, because it will be your best weapon. Find a Frozen Sanctum, one '
        'of the buried temples of my order, and search it well: our greatest treasure was never kept in plain sight.\n\n'
        'When you hold a Glacial Heart, forge a Winter Horn and sound it at a Glacial Altar. The Sovereign will '
        'answer. Shatter it, and the thaw will come.\n\n'
        'The Quests tab will guide you, step by step. Every quest holds a reward, so return here often.'
    ),
}

GUIDE = [
    ('Quick Start',
     '§1§lQuick Start§r\n\n1. Travel to a §lsnowy biome§r.\n2. Mine §3Frostiron Ore§r and §3Rime Crystal Ore§r with an iron pickaxe.\n'
     '3. Smelt Frostiron. Craft tools and armour.\n4. Cook a §6Hearthfire Stew§r for the cold.\n5. Hunt §3Frost Wraiths§r at night.\n'
     '6. Find the §lFrozen Sanctum§r and its secret.\n7. Sound the §lWinter Horn§r at the Glacial Altar.\n\nOpen the Quests tab and claim rewards as you go.'),
    ('Chill and Freezing',
     '§1§lChill§r is the heart of Rimeheart.\n\nFrost weapons add chill to what they hit. It is the same freezing meter that powder snow fills: '
     'chilled creatures slow down, and once §lfully frozen§r they shiver, take freeze damage and move sluggishly.\n\n'
     'Frostbite Blade and Winterfang deal §lShatter§r damage: +30% / +40% against fully frozen targets.\n\n'
     'Chill wears off after a few seconds. Winter creatures are immune.\n\n'
     '§1Protection:§r wearing any Frostiron or Wraithweave piece makes you immune, just like leather. Hearthfire Stew thaws you instantly.'),
    ('Frostiron and Rime',
     '§1§lFrostiron§r generates only under snowy biomes, from deep underground up into the mountains. It needs an §liron pickaxe§r. '
     'Frostiron gear sits between iron and diamond.\n\n§1§lRime Crystal Ore§r gives Rime Shards. Four shards make a Block of Rime Crystal.\n\n'
     '§1§lRimestone§r forms large veins in cold stone. Craft it into bricks for building.\n\n'
     'Rime Crystal Clusters grow in ruins. Break them carefully: some are Shardling nests. Silk Touch keeps the nest asleep.'),
    ('Tools and Weapons',
     '§1Frostiron Sword, Pickaxe, Axe, Shovel§r: reliable mid-game tools.\n\n§1§lFrostbite Blade§r: hits chill. Use for §lCold Snap§r, which chills everything within 4.5 blocks.\n\n'
     '§1§lGlacier Maul§r: slow, heavy. Use on the ground for §lPermafrost Slam§r: a ring of ice spikes that launches and freezes enemies.\n\n'
     '§1§lRimebow§r: fires icicles without arrows. Full draws hit harder.\n\n§1§lBlizzard Staff§r: hold to breathe a cone of blizzard for five seconds.\n\n'
     '§1§lFrost Charge§r: throw it to freeze mobs and turn water into temporary ice.'),
    ('Armour',
     '§1§lFrostiron Armour§r\nAny piece: immune to freezing.\nFull set, §lGlacial Stride§r: water freezes beneath your feet, and melee attackers are chilled.\n\n'
     '§1§lWraithweave§r\nLighter, better enchantability.\nFull set, §lSpectral Step§r: speed on snow and ice.\nFull set, §lFade§r: below 30% health you vanish '
     '(Invisibility and Speed II for 5 seconds) and nearby monsters lose track of you. 90 second cooldown.'),
    ('Creatures',
     '§1§lFrost Wraith§r\nHooded spirits that drift over snowy biomes at night. They circle and cast volleys of ice shards. They fade in direct sunlight. '
     'Drop Wraith Essence and, rarely, a Glacial Heart.\n\n§1§lShardling§r\nSmall crystal crawlers that nest in rime clusters and cold caves. '
     'Their bite chills. Drop Rime Shards.\n\nBoth are immune to chill.'),
    ('The Frozen Sanctum',
     'Buried temples of the Wardens, found under snowy plains, taiga and slopes. Look for a ring of broken rimestone pillars on the '
     'surface and a stairwell leading down.\n\nThe hall below holds a §lGlacial Altar§r, supply chests and old guardians.\n\n'
     '§1§lA secret:§r the Wardens sealed their vault behind a wall that only looks solid. Look for cracked bricks, and a stretch of wall '
     'that crumbles at a touch.'),
    ('The Frost Sovereign',
     'Craft a §lWinter Horn§r from a Glacial Heart and sound it at a Glacial Altar.\n\n§1Attacks:§r\n- §lIcicle Barrage§r: homing shards\n'
     '- §lGlacial Eruption§r: rings of frost mark where spikes will burst. Step out!\n- §lFrost Breath§r: a slow-turning cone of blizzard\n'
     '- §lStomp§r when you get close\n\nAt half health it summons Frost Wraiths, erupts three times at once and attacks twice as often.\n\n'
     '§1Rewards:§r Sovereign\'s Core, a Glacial Heart, Frostiron and Rime Shards.'),
    ('Beyond the Winter',
     'Place the §lSovereign\'s Core§r above a Frostbite Blade to forge §1§lWinterfang§r: a blade on par with netherite, whose hits chill deeply '
     'and whose §lAbsolute Zero§r freezes every enemy within 8 blocks.\n\nThe Sovereign can be summoned again with another Glacial Heart.\n\n'
     'The winter is over... until next time.'),
]
