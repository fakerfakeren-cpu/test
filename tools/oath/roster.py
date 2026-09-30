"""The wider roster, wired end to end from one table: registrations, attributes and spawn rules, renderers, spawn
eggs, bestiary entries, loot, natural spawns and names. Models and skins live in fauna.py, voices in voices.py,
behaviour in the entity classes.

Run from the repository root:  python3 -m tools.oath.roster   (Java and assets; data.py and lang.py pull the rest)
"""
import os

from . import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JAVA = os.path.join(ROOT, 'src/main/java/com/oathbound')


def M(id, cls, en, category, size, rig, spawn, egg, chapter, bestiary, loot, biomes=None, weight=0, group=(1, 1), scale=1.0,
      shadow=0.5, extra='', gloaming=False, boss=False):
    return dict(id=id, cls=cls, en=en, category=category, size=size, rig=rig, spawn=spawn, egg=egg, chapter=chapter, bestiary=bestiary,
                loot=loot, biomes=biomes or [], weight=weight, group=group, scale=scale, shadow=shadow, extra=extra, gloaming=gloaming,
                boss=boss)


L = D.LOOTING
ROSTER = [
    M('glimmerfawn', 'GlimmerfawnEntity', 'Glimmerfawn', 'CREATURE', (0.9, 1.6), 'Quadruped(r, "glimmerfawn", 1.0f, false, 0.9f)', 'wild',
      ('#8a5a34', '#dce8ff'), 0,
      ('A slender deer of the old woods whose dapples and antler-tips shine like moonlight. It bolts from anyone who does '
       'not creep, and grazes wherever the Lanternguard once walked.', 'Creep up on one to see it; it leaves *venison* and, rarely, a glowing *antler*.'),
      [D.pool([D.item('raw_venison', 1, 2, funcs=[L])]), D.pool([D.item('glimmer_antler'), {**D.EMPTY, 'weight': 6}], conds=D.BY_PLAYER)],
      ['minecraft:forest', 'minecraft:birch_forest', 'minecraft:old_growth_birch_forest', 'minecraft:flower_forest', 'minecraft:dark_forest',
       'minecraft:meadow'], 6, (2, 3)),
    M('duskhare', 'DuskhareEntity', 'Duskhare', 'CREATURE', (0.45, 0.55), 'Quadruped(r, "duskhare", 1.0f, true, 0.3f)', 'wild',
      ('#4a3c5a', '#b8a8ff'), 0,
      ('A long-eared hare the colour of dusk. Its ear-tips catch the last light, which is usually the only part of it anyone sees.',
       'Swift and shy. Leaves *rabbit* and *rabbit hide*.'),
      [D.pool([D.item('minecraft:rabbit', 0, 1, funcs=[L])]), D.pool([D.item('minecraft:rabbit_hide', 0, 1)])],
      ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:savanna', 'minecraft:savanna_plateau'], 8, (1, 3), shadow=0.25),
    M('mossback_tortoise', 'MossbackTortoiseEntity', 'Mossback Tortoise', 'CREATURE', (1.2, 0.8), 'Quadruped(r, "mossback_tortoise", 0.6f, false, 0.7f)',
      'shore', ('#445a2a', '#b884ff'), 0,
      ('A great slow tortoise with a garden growing on its back. Struck, it draws into its shell and shrugs off most blows; '
       'the swamp-folk say they are older than the Order.', 'Its shed *mossback scute* goes into the Elixir of Wards.'),
      [D.pool([D.item('mossback_scute'), {**D.EMPTY, 'weight': 1}]), D.pool([D.item('minecraft:moss_block', 0, 1)])],
      ['minecraft:swamp', 'minecraft:mangrove_swamp', 'minecraft:river', 'minecraft:beach'], 4, (1, 1), shadow=0.7),
    M('lumen_beetle', 'LumenBeetleEntity', 'Lumen Beetle', 'AMBIENT', (0.35, 0.25), 'Crawler(r, "lumen_beetle")', 'cave',
      ('#1e2236', '#ffcb58'), 0,
      ('A thumb-sized beetle that carries its own lantern through the caves. Miners follow them: they gather where lumenite grows.',
       'Harmless. Leaves *luminous dust*.'),
      [D.pool([D.item('luminous_dust')])], ['#minecraft:is_overworld'], 10, (2, 4), shadow=0.15),
    M('tidewader', 'TidewaderEntity', 'Tidewader', 'CREATURE', (0.6, 1.4), 'Bird(r, "tidewader")', 'shore', ('#98a4b4', '#d8a430'), 0,
      ('A tall grey heron of the chapel shallows. It stands so still that fish forget it, then strikes.',
       'Leaves *feathers*; sometimes drops a fresh cod.'),
      [D.pool([D.item('minecraft:feather', 1, 2, funcs=[L])])],
      ['minecraft:beach', 'minecraft:river', 'minecraft:swamp', 'minecraft:mangrove_swamp', 'minecraft:stony_shore'], 6, (1, 2), shadow=0.35),
    M('thornback_boar', 'ThornbackBoarEntity', 'Thornback Boar', 'CREATURE', (1.0, 1.0), 'Quadruped(r, "thornback_boar", 1.1f, false, 0.45f)', 'wild',
      ('#4e3828', '#d8d0bc'), 0,
      ('A heavy forest boar with a ridge of black quills. Left alone it roots and grunts; struck, it lowers its tusks and charges, '
       'and the whole sounder charges with it.', 'Leaves *porkchops* and, sometimes, a *boar tusk*.'),
      [D.pool([D.item('minecraft:porkchop', 1, 3, funcs=[L])]), D.pool([D.item('boar_tusk'), {**D.EMPTY, 'weight': 2}], conds=D.BY_PLAYER)],
      ['minecraft:taiga', 'minecraft:old_growth_pine_taiga', 'minecraft:old_growth_spruce_taiga', 'minecraft:dark_forest', 'minecraft:snowy_taiga'],
      6, (2, 4), shadow=0.6),
    M('stonewarden', 'StonewardenEntity', 'Stonewarden', 'CREATURE', (1.4, 2.8), 'Biped(r, "stonewarden", 0.7f, 0.1f)', 'wild',
      ('#9c8f72', '#ffcb58'), 0,
      ('A sentinel of mossy wardstone the Lanternguard left to watch the roads. It still hunts anything of the night that comes near '
       'and ignores travellers, unless they strike it first.', 'An ally against monsters. Leaves *wardstone* and *lumenite*.'),
      [D.pool([D.item('wardstone', 2, 4)]), D.pool([D.item('lumenite_shard', 0, 2)]), D.pool([D.item('mossy_wardstone_bricks', 0, 1)])],
      ['minecraft:windswept_hills', 'minecraft:windswept_gravelly_hills', 'minecraft:meadow', 'minecraft:stony_peaks'], 1, (1, 1),
      scale=1.3, shadow=1.0),
    M('runewisp', 'RunewispEntity', 'Runewisp', 'AMBIENT', (0.5, 0.5), 'Floater(r, "runewisp")', 'wisp', ('#6f7cff', '#ffffff'), 2,
      ('A mote of written light that drifts through birch woods at night. The Arcanists believed they were stray glyphs that escaped '
       'their books. It minds its own business; strike it and it answers with runes.', 'Leaves *luminous dust* and, rarely, *spellsilk*.'),
      [D.pool([D.item('luminous_dust', 1, 2)]), D.pool([D.item('spellsilk'), {**D.EMPTY, 'weight': 11}], conds=D.BY_PLAYER)],
      ['minecraft:birch_forest', 'minecraft:old_growth_birch_forest', 'minecraft:flower_forest', 'minecraft:cherry_grove'], 8, (1, 2), shadow=0.0),
    M('drowned_choirmonk', 'DrownedChoirmonkEntity', 'Drowned Choirmonk', 'MONSTER', (0.6, 1.95), 'Biped(r, "drowned_choirmonk", 0.8f, 0.0f)', 'monster',
      ('#21463f', '#3fe0c0'), 1,
      ('A monk of the drowned chapel who never stopped singing the vespers. When it sees the living it raises its candle and sings, '
       'and the hymn weighs on every limb that hears it.', 'Its hymn slows you. Break line of sight or strike it mid-song.'),
      [D.pool([D.item('minecraft:prismarine_shard', 0, 2, funcs=[L])]), D.pool([D.item('minecraft:kelp', 0, 2)]),
       D.pool([D.item('lore_page_tide_knight'), {**D.EMPTY, 'weight': 30}], conds=D.BY_PLAYER)],
      ['minecraft:beach', 'minecraft:stony_shore', 'minecraft:swamp'], 20, (1, 1)),
    M('mire_hag', 'MireHagEntity', 'Mire Hag', 'MONSTER', (0.6, 1.9), 'Biped(r, "mire_hag", 0.8f, 0.35f)', 'monster', ('#465634', '#5ae05a'), 3,
      ('A swamp witch bent under her lantern, who trades curses for bones. She keeps her distance, flings green fire and, when a blade '
       'gets close, is simply somewhere else.', 'Leaves *gloam essence* and, sometimes, a *hag\'s eye*.'),
      [D.pool([D.item('gloam_essence', 0, 1, funcs=[L])]), D.pool([D.item('minecraft:glass_bottle', 0, 1)]),
       D.pool([D.item('hag_eye'), {**D.EMPTY, 'weight': 3}], conds=D.BY_PLAYER)],
      ['minecraft:swamp', 'minecraft:mangrove_swamp'], 12, (1, 1)),
    M('grave_crawler', 'GraveCrawlerEntity', 'Grave Crawler', 'MONSTER', (0.9, 0.6), 'Crawler(r, "grave_crawler")', 'monster', ('#948870', '#4fe0cf'), 3,
      ('A barrow\'s leftovers: a skull and a spine on too many arms. They come in knots at night, fast and low, and burn at dawn.',
       'Weak alone, dangerous together. Leaves *bones*.'),
      [D.pool([D.item('minecraft:bone', 1, 2, funcs=[L])]), D.pool([D.item('minecraft:rotten_flesh', 0, 1)])],
      ['minecraft:plains', 'minecraft:taiga', 'minecraft:meadow', 'minecraft:windswept_hills', 'minecraft:snowy_plains'], 25, (2, 4), shadow=0.5),
    M('gloam_stalker', 'GloamStalkerEntity', 'Gloam Stalker', 'MONSTER', (0.8, 0.9), 'Quadruped(r, "gloam_stalker", 1.2f, false, -0.2f)', 'monster',
      ('#16101f', '#b884ff'), 5,
      ('A long, low cat of the Gloaming. Until it is close it is only a shimmer at the edge of sight; then it is all at once, mid-leap.',
       'A lit lantern shows it plainly. Leaves *gloam essence* and, rarely, a *shadow fang*.'),
      [D.pool([D.item('gloam_essence', 1, 1, funcs=[L])]), D.pool([D.item('shadow_fang'), {**D.EMPTY, 'weight': 4}], conds=D.BY_PLAYER)],
      gloaming=True, weight=14, group=(1, 2)),
    M('shade_wraith', 'ShadeWraithEntity', 'Shade Wraith', 'MONSTER', (0.7, 2.0), 'Floater(r, "shade_wraith")', 'monster', ('#1e1830', '#d6b0ff'), 5,
      ('A hooded shade that drifts over the Gloaming\'s islands. It circles above its prey, then swoops through it and leaves the cold '
       'of the grave behind.', 'Strike it as it swoops. Leaves *gloam essence*.'),
      [D.pool([D.item('gloam_essence', 1, 2, funcs=[L])]), D.pool([D.item('minecraft:phantom_membrane', 0, 1)])],
      gloaming=True, weight=10, group=(1, 1), shadow=0.0),
    M('lumenite_mite', 'LumeniteMiteEntity', 'Lumenite Mite', 'MONSTER', (0.5, 0.35), 'Crawler(r, "lumenite_mite")', 'mite', ('#403220', '#ffcb58'), 0,
      ('A burrowing mite that eats light. Lumenite grows from its back like a crust of candle-flame, and its bite dims the eyes and drinks '
       'a lantern\'s oil.', 'Keep a spare shard for your lantern. Leaves *lumenite dust*.'),
      [D.pool([D.item('lumenite_dust', 1, 2, funcs=[L])])], ['#minecraft:is_overworld'], 12, (2, 3), shadow=0.25),
    M('ashen_revenant', 'AshenRevenantEntity', 'Ashen Revenant', 'MONSTER', (0.65, 1.95), 'Biped(r, "ashen_revenant", 1.0f, 0.0f)', 'monster',
      ('#302620', '#ffb040'), 4,
      ('A knight burned in the Sundering who never stopped burning. It walks the dry lands at night trailing sparks; its blade sets what it '
       'cuts alight, and water makes it hiss and falter.', 'Fight it in the rain. Leaves *coal*, *gold* and, sometimes, an *ember core*.'),
      [D.pool([D.item('minecraft:coal', 1, 2, funcs=[L])]), D.pool([D.item('minecraft:gold_nugget', 1, 3)]),
       D.pool([D.item('ember_core'), {**D.EMPTY, 'weight': 5}], conds=D.BY_PLAYER)],
      ['minecraft:desert', 'minecraft:badlands', 'minecraft:eroded_badlands', 'minecraft:wooded_badlands', 'minecraft:savanna_plateau'], 15, (1, 1),
      extra='.fireImmune()'),
    # ------------------------------------------------------------------ the wild keepers (minibosses; no natural spawns)
    M('elderhorn', 'ElderhornEntity', 'Elderhorn, the Grove King', 'MONSTER', (1.8, 3.4), 'Quadruped(r, "elderhorn", 0.8f, false, 0.75f)', None,
      ('#6a4a2c', '#b6f06a'), 1,
      ('The stag-king of the old groves, crowned with antlers that have grown runes. He sleeps in a ring of standing stones and wakes '
       'for anyone who draws steel there. He gores in a straight line, calls roots up out of the ground and bellows a storm of leaves; '
       'wounded, he kneels to drink from the grove and must be struck hard to break the trance.',
       'Sidestep the charge: if he runs into stone he staggers. Hit him hard while he kneels.'),
      [D.pool([D.item('grove_kings_crown')]), D.pool([D.item('glimmer_antler', 2, 4)]), D.pool([D.item('raw_venison', 3, 6)]),
       D.pool([D.item('minecraft:experience_bottle', 4, 8)]), D.pool([D.item('minecraft:emerald', 3, 7)])],
      scale=1.8, shadow=1.4, boss=True),
    M('bog_mother', 'BogMotherEntity', 'The Bog Mother', 'MONSTER', (0.9, 2.9), 'Biped(r, "bog_mother", 0.6f, 0.4f)', None,
      ('#2e3a24', '#5ae08a'), 2,
      ('The first and oldest of the mire hags, grown vast in her stilt-house over the black water. She fights at a distance with '
       'witch-fire and sucking bog, steps away through her own lanterns when a blade comes near, and calls her bone-children up out '
       'of the mud. While they live, her lanterns shield her.',
       'Kill the brood first. Break line of sight from her volleys. Leaves her *lantern* and *hag\'s eyes*.'),
      [D.pool([D.item('bog_mothers_lantern')]), D.pool([D.item('hag_eye', 2, 3)]), D.pool([D.item('gloam_essence', 2, 4)]),
       D.pool([D.item('elixir_of_shrouds')]), D.pool([D.item('minecraft:experience_bottle', 4, 8)])],
      scale=1.5, shadow=0.9, boss=True),
    M('cinder_colossus', 'CinderColossusEntity', 'The Cinder Colossus', 'MONSTER', (1.6, 4.3), 'Biped(r, "cinder_colossus", 0.55f, 0.0f)', None,
      ('#3a2a22', '#ff8a2e'), 3,
      ('A war-effigy of the old sun-cult with a furnace for a heart, still stoking itself in its sunken sanctum under the sands. Its '
       'blade cuts lines of fire into the ground and it can make the earth erupt beneath your feet. It opens its chest to vent, and '
       'that is when its heart can be struck.',
       'Bring water or wait for rain: wet, it cracks. Strike the open core. Leaves the *Cinder Heart*, *ember cores* and *gravegold*.'),
      [D.pool([D.item('cinder_heart')]), D.pool([D.item('ember_core', 2, 4)]), D.pool([D.item('gravegold_ingot', 3, 5)]),
       D.pool([D.item('minecraft:experience_bottle', 5, 9)]), D.pool([D.item('minecraft:gold_block', 1, 2)])],
      scale=2.2, shadow=1.5, boss=True, extra='.fireImmune()'),
    # ------------------------------------------------------------------ people of the roads
    M('lanternguard_pilgrim', 'LanternguardPilgrimEntity', 'Lanternguard Pilgrim', 'CREATURE', (0.6, 1.95),
      'Biped(r, "lanternguard_pilgrim", 0.7f, 0.1f)', None, ('#7e2a20', '#ffcb58'), 0,
      ('A pilgrim of the fallen Order, walking the old roads from wayshrine to wayshrine with a pack of its goods. It sells the '
       'Order\'s metals, elixirs and torn pages, sometimes a relic or a record, and it buys what the wilds give up.',
       'Kindle a wayshrine and one may come. It moves on after a day.'),
      [], shadow=0.5),
]

PLACEMENT = {
    'wild': ('SpawnPlacementTypes.ON_GROUND', 'WildAnimal::checkWildSpawn'),
    'shore': ('SpawnPlacementTypes.ON_GROUND', 'WildAnimal::checkShoreSpawn'),
    'cave': ('SpawnPlacementTypes.ON_GROUND', 'WildAnimal::checkCaveSpawn'),
    'wisp': ('SpawnPlacementTypes.NO_RESTRICTIONS', 'RunewispEntity::checkWispSpawn'),
    'monster': ('SpawnPlacementTypes.ON_GROUND', 'Monster::checkMonsterSpawnRules'),
    'mite': ('SpawnPlacementTypes.ON_GROUND', 'RosterRegistry::checkMiteSpawn'),
}


# ====================================================================== Java
def _region(path, begin, end, body, anchor):
    src = open(path).read()
    region = begin + body + end
    if begin in src:
        a = src.index(begin)
        z = src.index(end) + len(end)
        src = src[:a] + region + src[z:]
    else:
        assert anchor in src, (path, anchor)
        src = src.replace(anchor, region + anchor, 1)
    open(path, 'w').write(src)


def java():
    B, E = '    // ------------------------------------------------------------------ the wider roster (generated by tools/oath/roster.py)\n', \
           '    // ------------------------------------------------------------------ end of the wider roster\n'
    lines = []
    for m in ROSTER:
        w, h = m['size']
        lines.append(f'    public static final RegistryObject<EntityType<{m["cls"]}>> {m["id"].upper()} = reg("{m["id"]}", {m["cls"]}::new, MobCategory.{m["category"]},\n'
                     f'        b -> b.sized({w}f, {h}f).clientTrackingRange({12 if m["boss"] else 10}){m["extra"]});\n')
    _region(os.path.join(JAVA, 'registry/ModEntities.java'), B, E, ''.join(lines) + '\n',
            '    // ------------------------------------------------------------------ spell effects\n')
    # spawn eggs
    lines = [f'    public static final RegistryObject<Item> {m["id"].upper()}_SPAWN_EGG = egg("{m["id"]}_spawn_egg", () -> ModEntities.{m["id"].upper()}.get());\n'
             for m in ROSTER]
    _region(os.path.join(JAVA, 'registry/ModItems.java'), B, E, ''.join(lines),
            '    // ------------------------------------------------------------------ block items\n')
    # attributes and spawn rules
    attrs = ''.join(f'        event.put(ModEntities.{m["id"].upper()}.get(), {m["cls"]}.createAttributes().build());\n' for m in ROSTER)
    spawns = ''.join(f'        event.register(ModEntities.{m["id"].upper()}.get(), {PLACEMENT[m["spawn"]][0]}, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,\n'
                     f'            {PLACEMENT[m["spawn"]][1]}, SpawnPlacementRegisterEvent.Operation.REPLACE);\n' for m in ROSTER if m['spawn'])
    with open(os.path.join(JAVA, 'registry/RosterRegistry.java'), 'w') as f:
        f.write(f'''package com.oathbound.registry;

import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.*;
import com.oathbound.entity.npc.*;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;

/** GENERATED by tools/oath/roster.py: attributes and spawn rules for the wider roster. */
public final class RosterRegistry {{
    private RosterRegistry() {{}}

    public static void attributes(EntityAttributeCreationEvent event) {{
{attrs}    }}

    public static void spawnPlacements(SpawnPlacementRegisterEvent event) {{
{spawns}    }}

    /** Lumenite mites: monster rules, and only deep underground. */
    public static boolean checkMiteSpawn(EntityType<? extends Monster> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {{
        return pos.getY() < 40 && Monster.checkMonsterSpawnRules(type, level, reason, pos, random);
    }}
}}
''')
    # renderers
    rend = ''.join(f'        e.registerEntityRenderer(ModEntities.{m["id"].upper()}.get(), c -> new Renderers.Fauna<>(c, r -> new FaunaModels.{m["rig"]}, '
                   f'"{m["id"]}", {m["shadow"]}f, {m["scale"]}f));\n' for m in ROSTER)
    with open(os.path.join(JAVA, 'client/RosterRenderers.java'), 'w') as f:
        f.write(f'''package com.oathbound.client;

import com.oathbound.client.model.FaunaModels;
import com.oathbound.client.render.Renderers;
import com.oathbound.registry.ModEntities;
import net.minecraftforge.client.event.EntityRenderersEvent;

/** GENERATED by tools/oath/roster.py: renderers for the wider roster. */
public final class RosterRenderers {{
    private RosterRenderers() {{}}

    public static void register(EntityRenderersEvent.RegisterRenderers e) {{
{rend}    }}
}}
''')
    # bestiary
    beasts = ''.join(f',\n        new Entry("{m["id"]}", {m["chapter"]}, ModItems.{m["id"].upper()}_SPAWN_EGG)' for m in ROSTER)
    path = os.path.join(JAVA, 'client/screen/ChronicleScreen.java')
    src = open(path).read()
    tag = '        new Entry("morvane", 5, ModItems.MORVANE_SPAWN_EGG)'
    a = src.index(tag) + len(tag)
    z = src.index(');', a)
    src = src[:a] + beasts + src[z:]
    open(path, 'w').write(src)


# ====================================================================== data (called by data.py)
def loot():
    for m in ROSTER:
        D.write(f'loot_table/entities/{m["id"]}.json', D.table('entity', m['loot'], f'entities/{m["id"]}'))


def spawns():
    for m in ROSTER:
        if m['gloaming'] or not m['biomes']:
            continue
        D.tag(f'worldgen/biome/has_creature/{m["id"]}', m['biomes'])
        lo, hi = m['group']
        D.write(f'forge/biome_modifier/{m["id"]}_spawns.json', {'type': 'forge:add_spawns', 'biomes': f'#oathbound:has_creature/{m["id"]}',
                                                                  'spawners': [{'type': f'oathbound:{m["id"]}', 'weight': m['weight'],
                                                                                'minCount': lo, 'maxCount': hi}]})


def gloaming_spawners():
    return [{'type': f'oathbound:{m["id"]}', 'weight': m['weight'], 'minCount': m['group'][0], 'maxCount': m['group'][1]}
            for m in ROSTER if m['gloaming']]


def tags():
    undead = ['drowned_choirmonk', 'grave_crawler', 'ashen_revenant']
    D.tag('entity_type/undead', undead, 'minecraft')
    D.tag('entity_type/sensitive_to_smite', undead, 'minecraft')
    D.tag('entity_type/gloam_creatures', ['gloam_stalker', 'shade_wraith'])
    D.tag('entity_type/arthropod', ['lumen_beetle', 'lumenite_mite'], 'minecraft')
    D.tag('entity_type/sensitive_to_bane_of_arthropods', ['lumen_beetle', 'lumenite_mite'], 'minecraft')


# ====================================================================== text (for lang.py)
NAMES = {m['id']: m['en'] for m in ROSTER}
BESTIARY = {m['id']: (m['en'], m['bestiary'][0], m['bestiary'][1]) for m in ROSTER}
EGGS = {m['id']: m['egg'] for m in ROSTER}
BOSSES = [m['id'] for m in ROSTER if m['boss']]


def generate():
    java()
    print(len(ROSTER), 'creatures wired')


if __name__ == '__main__':
    generate()
