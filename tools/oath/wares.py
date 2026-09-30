"""Wares of the old kingdom: relics, hearth food, elixirs, torn pages of the Order's history and music discs.

Writes the item registrations (a generated region of ModItems.java), icons, jukebox songs, and hands recipes,
chest loot, names and texts to data.py and lang.py.

Run from the repository root:  python3 -m tools.oath.wares
"""
import json
import os

from . import itemart as I
from . import data as D
from .music import DISCS
from .paint import Ramp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')
MODITEMS = os.path.join(ROOT, 'src/main/java/com/oathbound/registry/ModItems.java')
M = I.M

# ====================================================================== the tables
# relic id, English, Kind, rarity, description lines
RELICS = [
    ('bell_of_the_drowned', 'Bell of the Drowned', 'BELL', 'RARE',
     ['Cast for the drowned chapel; it still rings with the sea.', 'Use: a tolling wave hurls back and reveals every foe within 7 blocks.']),
    ('veyls_mirror', "Veyl's Mirror", 'MIRROR', 'RARE',
     ['The Archmage looked into it until it looked back.', 'Use: step through the glass up to 8 blocks ahead.']),
    ('barrow_censer', 'Barrow Censer', 'CENSER', 'RARE',
     ['Grave-smoke from the barrow kings\' own rites.', 'Use: heals you and your companions and hardens their skin.']),
    ('lanternguard_signet', 'Lanternguard Signet', 'SIGNET', 'RARE',
     ['Worn by the Order\'s captains. It is warm when it is needed.', 'Use: strength and swiftness for everyone near you.']),
    ('heart_of_the_gloam', 'Heart of the Gloam', 'HEART', 'EPIC',
     ['A shard of dusk that beats slowly in the hand.', 'Use: the dusk wraps you; whatever hunted you forgets you.']),
    ('sunshard_talisman', 'Sunshard Talisman', 'SUNSHARD', 'EPIC',
     ['A splinter of the first dawn, freed when the Hollow Crown broke.', 'Use: a flash of dawn burns the Gloam and the dead.']),
    ('huntsmans_horn', "Huntsman's Horn", 'HORN', 'UNCOMMON',
     ['The wayshrine wardens\' horn, for calling out what hides.', 'Use: every foe within 32 blocks is outlined in light.']),
    ('grove_kings_crown', "Grove King's Crown", 'GROVE', 'EPIC',
     ['A tine of the Elderhorn\'s antlers, still putting out leaves.', 'Use: roots burst up under every foe near you, and the grove mends you.']),
    ('bog_mothers_lantern', "Bog Mother's Lantern", 'MIRE', 'EPIC',
     ['Its green flame burns without oil and without warmth.', 'Use: snuff it to step ten blocks ahead, leaving a cloud of marsh-gas behind.']),
    ('cinder_heart', 'Cinder Heart', 'CINDER', 'EPIC',
     ['The furnace that walked the sands, small enough to hold.', 'Use: the ground erupts under every foe around you. Fire cannot touch you for a while.']),
]

E = 'MobEffects.'
# id, English, nutrition, saturation, always edible, kind (food/drink), container, stack, effects [(effect, seconds, amp)], line
FOODS = [
    ('hearth_pie', 'Hearth Pie', 10, 0.8, False, 'food', None, 16, [], 'A pie of meat and egg under a thick crust, as the barracks cooks made it.'),
    ('honeycake', 'Honeycake', 6, 0.6, False, 'food', None, 16, [('ABSORPTION', 30, 0)], 'Soft, sweet and still warm from somewhere.'),
    ('salted_cod', 'Salted Cod', 6, 0.7, False, 'food', None, 64, [], 'The chapel fishers\' winter fare.'),
    ('apple_tart', 'Apple Tart', 7, 0.6, False, 'food', None, 16, [], 'A wayfarer\'s favourite.'),
    ('trail_rations', 'Trail Rations', 8, 0.8, False, 'food', None, 16, [], 'Dried meat, hard bread and an apple, wrapped in waxed cloth. Quick to eat.'),
    ('emberroot_stew', 'Emberroot Stew', 7, 0.8, False, 'stew', 'BOWL', 1, [('FIRE_RESISTANCE', 60, 0)], 'Hot enough that fire seems mild after it.'),
    ('moonpetal_tea', 'Moonpetal Tea', 2, 0.3, True, 'drink', 'GLASS_BOTTLE', 16, [('REGENERATION', 10, 0), ('NIGHT_VISION', 60, 0)], 'Pale and fragrant; the night seems kinder after a cup.'),
    ('duskwine', 'Duskwine', 3, 0.4, True, 'drink', 'GLASS_BOTTLE', 16, [('NIGHT_VISION', 180, 0), ('NAUSEA', 6, 0)], 'Pressed from dusk lilies. Strong.'),
    ('spiced_cider', 'Spiced Cider', 4, 0.5, True, 'drink', 'GLASS_BOTTLE', 16, [('HASTE', 120, 0)], 'Apples and emberroot. It puts a spring in any work.'),
]
ELIXIRS = [
    ('elixir_of_tides', 'Elixir of Tides', [('WATER_BREATHING', 480, 0), ('DOLPHINS_GRACE', 180, 0)], 'tide', 'Breathe the sea and swim it like a seal.'),
    ('elixir_of_wards', 'Elixir of Wards', [('RESISTANCE', 180, 0), ('ABSORPTION', 60, 1)], 'arcane', 'Veyl\'s wards, bottled.'),
    ('elixir_of_shrouds', 'Elixir of Shrouds', [('INVISIBILITY', 180, 0), ('NIGHT_VISION', 180, 0)], 'gloam', 'See in the dark, and be the dark.'),
    ('elixir_of_the_wayfarer', 'Elixir of the Wayfarer', [('SPEED', 180, 1), ('JUMP_BOOST', 180, 0)], 'moss', 'For the long road home.'),
    ('elixir_of_valor', 'Elixir of Valor', [('STRENGTH', 90, 1), ('HASTE', 90, 0)], 'blood', 'Sir Caldris\' squires drank it before battle.'),
]

# creature drops (roster.py): id, English, description, rarity
DROPS = [
    ('raw_venison', 'Raw Venison', 'Lean meat from a glimmerfawn. Better cooked.', 'COMMON'),
    ('cooked_venison', 'Venison Steak', 'Rich and filling; a hunter\'s supper.', 'COMMON'),
    ('glimmer_antler', 'Glimmer Antler', 'The tip still holds a little moonlight. Grind it into luminous dust.', 'UNCOMMON'),
    ('mossback_scute', 'Mossback Scute', 'A shed plate of tortoise shell, green with moss. It turns blows aside.', 'UNCOMMON'),
    ('boar_tusk', 'Boar Tusk', 'Yellowed and sharp. Huntsmen carve horns from them.', 'COMMON'),
    ('hag_eye', "Hag's Eye", 'It is not a real eye. It still blinks.', 'UNCOMMON'),
    ('shadow_fang', 'Shadow Fang', 'A stalker\'s fang, cold and hard to see even in the hand.', 'RARE'),
    ('ember_core', 'Ember Core', 'The heart of a revenant, still burning after four hundred years.', 'UNCOMMON'),
]

# page slug, title, lines
PAGES = [
    ('first_lantern', 'The First Lantern', [
        'Before the Order there was only the Lantern: a fire someone carried out of the first dawn,',
        'and refused to let go out. The first knights were only the people who took turns carrying it.']),
    ('oath_of_ember', 'The Oath of the Ember', [
        '"I will keep the light when I cannot see it. I will keep it when it burns my hands.',
        'I will keep it until someone is there to take it from me." Every squire said it once, at dawn.']),
    ('tide_knight', 'The Tide-Knight\'s Vow', [
        'Caldris swore no tide would reach the chapel. When the sea rose he did not leave;',
        'he held the doors shut from the inside. The chapel bells still ring on the ebb.']),
    ('four_riddles', 'On the Four Riddles', [
        'Veyl hid the Seal of Wisdom behind riddles he answered himself, every morning, for a century.',
        'His apprentices said he did it to remember. Veyl said he did it so he would not.']),
    ('honest_king', 'Of the Honest King', [
        'Three kings sleep beside Hrodgar, and each wrote an epitaph about the others.',
        'Only one of them never lied. The barrow opens for whoever can tell which.']),
    ('lord_commander', 'The Lord-Commander', [
        'Morvane was the best of us. He led the Order for forty years and lost no one he could have saved.',
        'He could not save himself from growing old, and that was the thing he could not forgive.']),
    ('the_gloaming', 'Of the Grey Country', [
        'Between dusk and night there is a country. It is always just about to be dark there.',
        'Things that are almost gone go there: echoes, lost oaths, and people who will not die.']),
    ('hollow_crown', 'The Hollow Crown', [
        'It promised a reign without end to whoever swore on it. It did not say what would reign.',
        'Morvane swore. The crown kept its word. What sits the throne now is the crown\'s, not his.']),
    ('sundering', 'The Night of Sundering', [
        'The citadel fell in one night. The Lanterns went out one by one, from the gate inward.',
        'By dawn three keepers had shut the Gloam out, and the Order was gone.']),
    ('three_seals', 'The Three Seals', [
        'Valor, wisdom and sacrifice: three oaths bound three keepers to three seals,',
        'and the seals bound the gate. Break none of them, and the Hollow King sleeps forever.']),
    ('everflame', 'On the Everflame', [
        'The Everflame is not hot. It is only certain. Steel quenched in it remembers dawn',
        'for as long as it lasts; the Order called that steel Dawnsteel, and made very little of it.']),
    ('last_squire', 'To Whoever Finds This', [
        'If you are reading this, the Lantern has chosen again. It has never chosen wrong.',
        'Carry it. It will be heavy. It is supposed to be.']),
]


# ====================================================================== Java
BEGIN = '    // ------------------------------------------------------------------ wares (generated by tools/oath/wares.py)\n'
END = '    // ------------------------------------------------------------------ end of wares\n'


def _effects(effects):
    inst = [f'new MobEffectInstance({E}{e}, {s * 20}, {a})' for e, s, a in effects]
    if len(inst) == 1:
        return f'new ApplyStatusEffectsConsumeEffect({inst[0]})'
    return f'new ApplyStatusEffectsConsumeEffect(java.util.List.of({", ".join(inst)}))'


def java():
    L = [BEGIN]
    for rid, _, kind, rarity, _ in RELICS:
        L.append(f'    public static final RegistryObject<Item> {rid.upper()} = reg("{rid}", p -> new RelicItem(p, RelicItem.Kind.{kind}), '
                 f'() -> new Item.Properties().stacksTo(1).rarity(Rarity.{rarity}));\n')
    for fid, _, nut, sat, always, kind, cont, stack, effects, _ in FOODS:
        base = 'Consumables.defaultDrink()' if kind == 'drink' else 'Consumables.defaultFood()'
        if fid == 'trail_rations':
            base += '.consumeSeconds(0.8f)'
        cons = base + ''.join(f'.onConsume({_effects([e])})' for e in effects) + '.build()'
        props = f'new Item.Properties().stacksTo({stack}).food(new FoodProperties({nut}, {sat}f, {str(always).lower()}), {cons})'
        if cont:
            props += f'.usingConvertsTo(net.minecraft.world.item.Items.{cont})'
        L.append(f'    public static final RegistryObject<Item> {fid.upper()} = reg("{fid}", p -> new InscribedItem(p, 1, false), () -> {props});\n')
    for eid, _, effects, _, _ in ELIXIRS:
        cons = 'Consumables.defaultDrink()' + f'.onConsume({_effects(effects)})' + '.build()'
        props = (f'new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), {cons})'
                 f'.usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE)')
        L.append(f'    public static final RegistryObject<Item> {eid.upper()} = reg("{eid}", p -> new InscribedItem(p, 1, true), () -> {props});\n')
    for did, _, _, rarity in DROPS:
        props = f'new Item.Properties().rarity(Rarity.{rarity})'
        if did == 'raw_venison':
            props += '.food(new FoodProperties(3, 0.3f, false))'
        elif did == 'cooked_venison':
            props += '.food(new FoodProperties(8, 0.9f, false))'
        elif did == 'ember_core':
            props += '.fireResistant()'
        L.append(f'    public static final RegistryObject<Item> {did.upper()} = reg("{did}", p -> new InscribedItem(p, 1, false), () -> {props});\n')
    for slug, _, lines in PAGES:
        L.append(f'    public static final RegistryObject<Item> LORE_PAGE_{slug.upper()} = reg("lore_page_{slug}", p -> new LorePageItem(p, "{slug}", {len(lines)}), '
                 f'() -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));\n')
    for sid in DISCS:
        name = 'music_' + sid
        L.append(f'    public static final RegistryObject<Item> {name.upper()} = reg("{name}", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE)'
                 f'.jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "{sid[5:]}"))));\n')
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
    for imp in ('import net.minecraft.world.effect.MobEffectInstance;', 'import net.minecraft.world.effect.MobEffects;',
                'import net.minecraft.world.item.component.Consumables;',
                'import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;'):
        if imp not in src:
            src = src.replace('import net.minecraft.world.food.FoodProperties;', 'import net.minecraft.world.food.FoodProperties;\n' + imp)
    open(MODITEMS, 'w').write(src)


# ====================================================================== icons
BELL = [
    "................",
    ".......KK.......",
    "......K44K......",
    ".......KK.......",
    "......K54K......",
    ".....K5443K.....",
    "....K554332K....",
    "....K544332K....",
    "....K543322K....",
    "...K5443322K....",
    "...K5433221K....",
    "..K544332221K...",
    "..KaaaaaaaaaK...",
    "...KKK.b.KKK....",
    "......KbK.......",
    ".......K........",
]
MIRROR = [
    "................",
    ".....KKKKK......",
    "....KaaaaaK.....",
    "...Kab554baK....",
    "...Ka55443aK....",
    "...Ka54432aK....",
    "...Ka54322aK....",
    "...Kab4322aK....",
    "....KabbbaK.....",
    ".....KKaKK......",
    "......KaK.......",
    "......KaK.......",
    "......KbK.......",
    "......KaK.......",
    "......KaK.......",
    ".......K........",
]
CENSER = [
    ".......s........",
    "......s.s.......",
    ".......s........",
    "......sKs.......",
    ".......K........",
    ".......K........",
    "......KaK.......",
    ".....K5a4K......",
    "....K5.4.3K.....",
    "...K55444332K...",
    "...K54433221K...",
    "...Kbbbbbbbb....",
    "....K433221K....",
    ".....K3221K.....",
    "......KKKK......",
    "................",
]
SIGNET = [
    "................",
    "................",
    "......KKKK......",
    ".....KrrrrK.....",
    "....KrwrrrrK....",
    "....KrrrrrrK....",
    ".....KrrrrK.....",
    "....K5KKKK4K....",
    "...K5K....K3K...",
    "...K4K....K3K...",
    "...K4K....K2K...",
    "...K43K..K22K...",
    "....K433221K....",
    ".....KKKKKK.....",
    "................",
    "................",
]
HEART = [
    "................",
    "................",
    "...KKK...KKK....",
    "..K554K.K543K...",
    ".K55544K54432K..",
    ".K5w54443433K...",
    ".K55444433332K..",
    ".K54444333322K..",
    "..K444333322K...",
    "...K4433322K....",
    "....K43322K.....",
    ".....K322K......",
    "......K2K.......",
    ".......K........",
    "................",
    "................",
]
SUNSHARD = [
    "........b.......",
    ".......b........",
    "......b.........",
    ".....K..........",
    "...K.K.K........",
    "....K5K.........",
    "..KK555KK.......",
    ".K5555544K..K...",
    "..K5554433K.....",
    ".KK55w4433KK....",
    "...K443322K.....",
    "..K.K4332K.K....",
    ".....K32K.......",
    "....K..K..K.....",
    "................",
    "................",
]
PIE = [
    "................",
    "................",
    "................",
    "................",
    "....KKKKKKKK....",
    "..KK55445544KK..",
    ".K554y44y4433K..",
    ".K5444444433321K",
    "K54y444y4433y21K",
    "K444444443333221",
    "KaaaaaaaaaaaaaaK",
    ".KbbbbbbbbbbbbK.",
    "..KKKKKKKKKKKK..",
    "................",
    "................",
    "................",
]
CAKE = [
    "................",
    "................",
    "................",
    "................",
    "........KK......",
    "......KK55K.....",
    "....KK5555yK....",
    "..KK55555yyyK...",
    ".K5555yyyyyyyK..",
    ".KaaaaaaaaaaaaK.",
    ".K444444433333K.",
    ".Kaaaaaaaaaaaa2K",
    ".K444444433333K.",
    ".KKKKKKKKKKKKKK.",
    "................",
    "................",
]
FISH = [
    "................",
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "...KK544443KK.K.",
    "..K5w4444433KK3K",
    ".K55444w443332K.",
    ".K5444444w33322K",
    "..K544433322KK2K",
    "...KK333322K..K.",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
    "................",
]
TART = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "....KKKKKKKK....",
    "..KKaarrraaaKK..",
    ".KaarrrrrrraaaK.",
    ".KarrrgrrrrraaK.",
    ".KaarrrrrrraaaK.",
    ".K4aaaaaaaaaa3K.",
    "..K443333322KK..",
    "...KKKKKKKKKK...",
    "................",
    "................",
    "................",
]
RATIONS = [
    "................",
    "................",
    "................",
    "....KKKKKKKK....",
    "...K55545544K...",
    "..K5544a54443K..",
    "..K5444a44433K..",
    ".KaaaaaaaaaaaaK.",
    ".K54444a444332K.",
    ".K44444a443322K.",
    ".K4444aaa33322K.",
    "..KK44a3a3322K..",
    "....KKaKaKKKK...",
    "......a.a.......",
    "................",
    "................",
]
ELIXIR = [
    "................",
    "......KKKK......",
    "......KaaK......",
    ".......KK.......",
    "......K55K......",
    "......K54K......",
    ".....K5yyyK.....",
    "....K5yyyyyK....",
    "...K5yywyyyyK...",
    "...Kyywyyyyy3K..",
    "...Kyyyyyyyy3K..",
    "...Kyyyyyyy33K..",
    "....Kyyyyy33K...",
    ".....KK333KK....",
    ".......KKK......",
    "................",
]
PAGE = [
    "................",
    "...KKKKKKKKK....",
    "...K5555544K....",
    "...K5a5a5a4KK...",
    "...K5555544K4K..",
    "...K5a5a5a4443K.",
    "...K555554444K..",
    "...K5a5a5a443K..",
    "...K5555544K3K..",
    "...K5a5a4444K...",
    "...K55554rr3K...",
    "...K5554rrrr3K..",
    "...K55444rr33K..",
    "...KKK444433KK..",
    "......KKKKKK....",
    "................",
]
DISC = [
    "................",
    ".....KKKKKK.....",
    "...KK222222KK...",
    "..K2233333322K..",
    "..K2333aa33332K.",
    ".K233aaaaaa3322K",
    ".K23aaaKKaaa332K",
    ".K23aaKKKKaa332K",
    ".K23aaKKKKaa332K",
    ".K23aaaKKaaa332K",
    ".K233aaaaaa3322K",
    "..K2333aa33332K.",
    "..K2233333322K..",
    "...KK222222KK...",
    ".....KKKKKK.....",
    "................",
]
VENISON = [
    "................",
    "................",
    "................",
    ".....KKKKK......",
    "...KK54443KK....",
    "..K5544443332K..",
    ".K554w44433322K.",
    ".K5444w4433322K.",
    ".K54444w333221K.",
    "..K444433332aaK.",
    "...KK4333221aK..",
    ".....KKK2221K...",
    "........KKK.....",
    "................",
    "................",
    "................",
]
ANTLER = [
    "................",
    "..y.......y.....",
    "..K4.....K4.....",
    "...K4...K4..y...",
    "...K4K.K4..K4...",
    "....K4K4..K4....",
    "....K44K.K4.....",
    ".....K44K4......",
    "......K444K.....",
    "......K443K.....",
    ".......K43K.....",
    ".......K43K.....",
    "........K3K.....",
    "........K3K.....",
    ".........K......",
    "................",
]
SCUTE = [
    "................",
    "................",
    ".....KKKKKK.....",
    "...KKaabaaaKK...",
    "..Kaab5554baaK..",
    "..Kab554443baK..",
    ".Kab55444433baK.",
    ".Ka554444333baK.",
    ".Kab4444333322K.",
    "..K44443333222K.",
    "..K4443332221K..",
    "...KK33322211K..",
    ".....KKKKKKK....",
    "................",
    "................",
    "................",
]
TUSK = [
    "................",
    "................",
    "............K...",
    "...........K5K..",
    "..........K54K..",
    ".........K543K..",
    "........K5432K..",
    ".......K5433K...",
    "......K5432K....",
    ".....K5432K.....",
    "....K543KK......",
    "...Kaa3K........",
    "..KbaaK.........",
    "..KbbK..........",
    "...KK...........",
    "................",
]
EYE = [
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "...KK555554KK...",
    "..K554yyy4443K..",
    ".K54yyKKyy4332K.",
    ".K54yKwwKy4332K.",
    ".K54yKwKKy4332K.",
    ".K544yyyy44321K.",
    "..K5444444332K..",
    "...KK333322KK...",
    ".....KKKKKK.....",
    "................",
    "................",
    "................",
]
FANG = [
    "................",
    "....KKK.........",
    "...K554K........",
    "...K5443K.......",
    "....K5443K......",
    "....K54432K.....",
    ".....K5443K.....",
    ".....K54432K....",
    "......K5432K....",
    "......K5432K....",
    ".......K532K....",
    ".......K542K....",
    "........K4K.....",
    "........K3K.....",
    ".........K......",
    "................",
]
CORE = [
    "................",
    "................",
    ".......K........",
    "......K5K.......",
    ".....K555K......",
    "...KK55w54KK....",
    "..K5555w5544K...",
    ".K555ww44443K...",
    "..K554444332K...",
    "...KK443332K....",
    ".....K4332K.....",
    "......K32K......",
    ".......KK.......",
    "................",
    "................",
    "................",
]
CROWN_OF_TINES = [
    "................",
    ".g..........g...",
    ".K4...g....K4...",
    "..K4.K4...K4.g..",
    "..K4K4..g.K4K4..",
    "...K4..K4K4K4...",
    "...K44K4.K44....",
    "....K444K44K....",
    ".....K4444K.....",
    ".....K43w3K.....",
    "....KaaaaaaK....",
    "...Kab5b5baK....",
    "...KaaaaaaaK....",
    "....KKKKKKK.....",
    "................",
    "................",
]
HAG_LANTERN = [
    "................",
    "......KKKK......",
    ".....K5..5K.....",
    ".....KK..KK.....",
    "....KaaaaaaK....",
    "....K4aaaa3K....",
    "....Kb.gg.bK....",
    "....KbgwwgbK....",
    "....KbgwwgbK....",
    "....Kb.gg.bK....",
    "....Kb....bK....",
    "....KaaaaaaK....",
    "....K433322K....",
    ".....KKKKKK.....",
    "................",
    "................",
]
CINDER_HEART = [
    "................",
    "......b..b......",
    ".....KbKKbK.....",
    "....K55K555K....",
    "...K5b55b554K...",
    "...K55w5544bK...",
    "...Kb5ww54b4K...",
    "...K5544444bK...",
    "....K4b44b3K....",
    ".....K4433K.....",
    "......Kb3K......",
    ".......KK.......",
    "................",
    "................",
    "................",
    "................",
]
DISC_LABELS = {'disc_lanternguard_hymn': 'gold', 'disc_wayshrine_nocturne': 'ember', 'disc_chapel_tides': 'tide',
               'disc_crown_of_ash': 'blood'}


def icons():
    out = {}
    G = M
    out['bell_of_the_drowned'] = I.sprite(BELL, G['verdigris'], G['gold'])
    out['veyls_mirror'] = I.sprite(MIRROR, G['arcane'], G['silver'])
    out['barrow_censer'] = I.sprite(CENSER, G['bone'], G['gold'], {'s': (G['teal'], 4)})
    out['lanternguard_signet'] = I.sprite(SIGNET, G['gold'], None, {'r': (G['blood'], 4), 'w': (G['white'], 5)})
    out['heart_of_the_gloam'] = I.sprite(HEART, G['violet'], None, {'w': (G['white'], 5)})
    out['sunshard_talisman'] = I.sprite(SUNSHARD, G['dawn'], G['leather'], {'w': (G['white'], 5)})
    out['huntsmans_horn'] = I.sprite(I.HORN, G['wood'], G['gold'])
    out['grove_kings_crown'] = I.sprite(CROWN_OF_TINES, G['bone'], G['moss'], {'g': (G['moss'], 5), 'w': (G['white'], 5)})
    out['bog_mothers_lantern'] = I.sprite(HAG_LANTERN, G['rust'], G['moss'], {'g': (G['moss'], 5), 'w': (G['white'], 5)})
    out['cinder_heart'] = I.sprite(CINDER_HEART, G['ember'], G['iron'], {'w': (G['white'], 5)})
    out['hearth_pie'] = I.sprite(PIE, G['bread'], G['stew'], {'y': (G['blood'], 3)})
    out['honeycake'] = I.sprite(CAKE, G['bread'], G['honey'], {'y': (G['honey'], 5)})
    out['salted_cod'] = I.sprite(FISH, Ramp('#4a3a2a', '#7a6248', '#a88c6a', '#c8b08e', '#e4d6bc', '#fbf4e6'), None, {'w': (G['white'], 5)})
    out['apple_tart'] = I.sprite(TART, G['bread'], G['bread'], {'r': (G['blood'], 4), 'g': (G['moss'], 4)})
    out['trail_rations'] = I.sprite(RATIONS, G['paper'], G['rust'])
    out['emberroot_stew'] = I.sprite(I.BOWL, G['ember'], G['wood'], {'y': (G['honey'], 4)})
    out['moonpetal_tea'] = I.sprite(I.BOTTLE, G['glass'], G['leather'], {'y': (G['tide'], 5), 'w': (G['white'], 5)})
    out['duskwine'] = I.sprite(I.BOTTLE, G['glass'], G['leather'], {'y': (G['violet'], 2), 'w': (G['white'], 5)})
    out['spiced_cider'] = I.sprite(I.BOTTLE, G['glass'], G['leather'], {'y': (G['honey'], 3), 'w': (G['white'], 5)})
    for eid, _, _, colour, _ in ELIXIRS:
        out[eid] = I.sprite(ELIXIR, G['glass'], G['gold'], {'y': (G[colour], 4), 'w': (G['white'], 5)})
    for i, (slug, _, _) in enumerate(PAGES):
        seal = ('blood', 'gold', 'tide', 'arcane', 'bone', 'gloam')[i % 6]
        out[f'lore_page_{slug}'] = I.sprite(PAGE, G['paper'], G['stew'], {'r': (G[seal], 3)})
    out['raw_venison'] = I.sprite(VENISON, G['blood'], G['bone'], {'w': (G['white'], 4)})
    out['cooked_venison'] = I.sprite(VENISON, G['stew'], G['bone'], {'w': (G['bread'], 5)})
    out['glimmer_antler'] = I.sprite(ANTLER, G['bone'], None, {'y': (G['white'], 5)})
    out['mossback_scute'] = I.sprite(SCUTE, G['rust'], G['moss'])
    out['boar_tusk'] = I.sprite(TUSK, G['bone'], G['leather'])
    out['hag_eye'] = I.sprite(EYE, G['moss'], None, {'y': (G['honey'], 5), 'w': (G['white'], 5)})
    out['shadow_fang'] = I.sprite(FANG, G['gloam'])
    out['ember_core'] = I.sprite(CORE, G['ember'], None, {'w': (G['white'], 5)})
    for sid, colour in DISC_LABELS.items():
        out['music_' + sid] = I.sprite(DISC, M['hollow'], G[colour])
    return out


def write_json(rel, obj):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def assets():
    for name, im in icons().items():
        im.save(os.path.join(ASSETS, 'textures/item', name + '.png'))
        write_json(f'models/item/{name}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'oathbound:item/{name}'}})
        write_json(f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': f'oathbound:item/{name}'}})


from . import wilds as _wilds
PAGES += _wilds.PAGES

# ====================================================================== text (for lang.py)
NAMES = {}
DESC = {}
LORE = {}
for _r in RELICS:
    NAMES[_r[0]] = _r[1]
    DESC[_r[0]] = _r[4]
for _f in FOODS:
    NAMES[_f[0]] = _f[1]
    DESC[_f[0]] = [_f[9]]
for _e in ELIXIRS:
    NAMES[_e[0]] = _e[1]
    DESC[_e[0]] = [_e[4]]
for _d in DROPS:
    NAMES[_d[0]] = _d[1]
    DESC[_d[0]] = [_d[2]]
for _slug, _title, _lines in PAGES:
    NAMES[f'lore_page_{_slug}'] = 'Torn Page'
    LORE[f'lore.oathbound.{_slug}.title'] = _title
    for _i, _l in enumerate(_lines, 1):
        LORE[f'lore.oathbound.{_slug}.{_i}'] = _l
for _sid, (_, _title, _) in DISCS.items():
    NAMES['music_' + _sid] = 'Music Disc'
    LORE[f'jukebox_song.oathbound.{_sid[5:]}'] = f'Oathbound - {_title}'
LORE['item.oathbound.lore_page.hint'] = 'Use to read.'
LORE['message.oathbound.horn'] = '%s foes answer the horn'
LORE['message.oathbound.relic.no_room'] = 'There is no room to step there'


# ====================================================================== data (called by data.py)
def recipes():
    F = 'misc'   # crafting recipes accept building, redstone, equipment and misc only
    D.shapeless('hearth_pie', ['minecraft:cooked_beef', 'minecraft:wheat', 'minecraft:egg', 'minecraft:wheat'], 'hearth_pie', category=F)
    D.shapeless('hearth_pie_from_pork', ['minecraft:cooked_porkchop', 'minecraft:wheat', 'minecraft:egg', 'minecraft:wheat'], 'hearth_pie', category=F)
    D.shapeless('honeycake', ['minecraft:honey_bottle', 'minecraft:wheat', 'minecraft:sugar', 'minecraft:egg'], 'honeycake', 2, category=F)
    D.shapeless('salted_cod', ['minecraft:cooked_cod', 'minecraft:dried_kelp'], 'salted_cod', category=F)
    D.shapeless('apple_tart', ['minecraft:apple', 'minecraft:wheat', 'minecraft:sugar'], 'apple_tart', category=F)
    D.shapeless('trail_rations', ['minecraft:cooked_beef', 'minecraft:bread', 'minecraft:apple', 'minecraft:paper'], 'trail_rations', 3, category=F)
    D.shapeless('emberroot_stew', ['minecraft:bowl', 'emberroot', 'minecraft:baked_potato', 'minecraft:carrot'], 'emberroot_stew', category=F)
    D.shapeless('moonpetal_tea', ['minecraft:glass_bottle', 'moonpetal', 'minecraft:honey_bottle'], 'moonpetal_tea', category=F)
    D.shapeless('duskwine', ['minecraft:glass_bottle', 'dusk_lily', 'dusk_lily', 'minecraft:sugar'], 'duskwine', category=F)
    D.shapeless('spiced_cider', ['minecraft:glass_bottle', 'minecraft:apple', 'minecraft:sugar', 'emberroot'], 'spiced_cider', category=F)
    D.shapeless('elixir_of_tides', ['minecraft:glass_bottle', 'minecraft:pufferfish', 'minecraft:prismarine_crystals', 'luminous_dust'], 'elixir_of_tides', category=F)
    D.shapeless('elixir_of_wards', ['minecraft:glass_bottle', 'spellsilk', 'minecraft:golden_carrot', 'luminous_dust'], 'elixir_of_wards', category=F)
    D.shapeless('elixir_of_shrouds', ['minecraft:glass_bottle', 'gloam_essence', 'minecraft:fermented_spider_eye', 'dusk_lily'], 'elixir_of_shrouds', category=F)
    D.shapeless('elixir_of_the_wayfarer', ['minecraft:glass_bottle', 'minecraft:rabbit_foot', 'minecraft:sugar', 'luminous_dust'], 'elixir_of_the_wayfarer', category=F)
    D.cooking('cooked_venison', 'smelting', 'raw_venison', 'cooked_venison', 0.35, 200)
    D.cooking('cooked_venison_smoking', 'smoking', 'raw_venison', 'cooked_venison', 0.35, 100)
    D.cooking('cooked_venison_campfire', 'campfire_cooking', 'raw_venison', 'cooked_venison', 0.35, 600)
    D.shapeless('luminous_dust_from_antler', ['glimmer_antler'], 'luminous_dust', 4)
    D.shapeless('elixir_of_wards_from_scute', ['minecraft:glass_bottle', 'mossback_scute', 'minecraft:golden_carrot', 'luminous_dust'], 'elixir_of_wards', category=F)
    D.shapeless('elixir_of_shrouds_from_eye', ['minecraft:glass_bottle', 'hag_eye', 'gloam_essence'], 'elixir_of_shrouds', category=F)
    D.shapeless('elixir_of_valor_from_core', ['minecraft:glass_bottle', 'ember_core', 'luminous_dust'], 'elixir_of_valor', category=F)
    D.shaped('huntsmans_horn', ['T  ', 'TT ', ' GT'], {'T': 'boar_tusk', 'G': 'minecraft:gold_ingot'}, 'huntsmans_horn', category='equipment')
    D.shaped('heart_of_the_gloam', ['FEF', 'ESE', 'FEF'], {'F': 'shadow_fang', 'E': 'gloam_essence', 'S': 'lumenite_shard'}, 'heart_of_the_gloam', category='equipment')
    D.shapeless('gloam_essence_from_fang', ['shadow_fang'], 'gloam_essence', 2)
    D.shapeless('elixir_of_valor', ['minecraft:glass_bottle', 'minecraft:blaze_powder', 'emberroot', 'luminous_dust'], 'elixir_of_valor', category=F)


# where each ware can be found: chest table -> [(item, weight)]
LOOT = {
    'chapel_reliquary': [('bell_of_the_drowned', 3), ('lore_page_tide_knight', 5), ('elixir_of_tides', 6), ('salted_cod', 8)],
    'chapel_nave': [('salted_cod', 10), ('lore_page_first_lantern', 3), ('music_disc_chapel_tides', 2)],
    'spire_sanctum': [('veyls_mirror', 3), ('lore_page_four_riddles', 5), ('elixir_of_wards', 6)],
    'spire_library': [('lore_page_oath_of_ember', 4), ('lore_page_three_seals', 4), ('lore_page_everflame', 3), ('moonpetal_tea', 6)],
    'spire_alchemy': [('elixir_of_shrouds', 5), ('elixir_of_the_wayfarer', 5), ('elixir_of_valor', 4), ('duskwine', 6)],
    'barrow_hoard': [('barrow_censer', 3), ('lore_page_honest_king', 5), ('music_disc_crown_of_ash', 2)],
    'barrow_tomb': [('trail_rations', 8), ('lore_page_sundering', 3)],
    'citadel_armory': [('lanternguard_signet', 3), ('elixir_of_valor', 5), ('lore_page_lord_commander', 4)],
    'citadel_barracks': [('hearth_pie', 8), ('honeycake', 6), ('spiced_cider', 6), ('music_disc_lanternguard_hymn', 2)],
    'citadel_secret': [('lore_page_hollow_crown', 10)],
    'wayshrine_cache': [('huntsmans_horn', 2), ('apple_tart', 8), ('trail_rations', 8), ('lore_page_last_squire', 3),
                        ('music_disc_wayshrine_nocturne', 2)],
}


for _t, _entries in _wilds.LOOT.items():
    LOOT.setdefault(_t, []).extend(_entries)


def loot_pools():
    """One extra roll per chest over its wares, with a chance of nothing."""
    out = {}
    for table, entries in LOOT.items():
        total = sum(w for _, w in entries)
        out[table] = D.pool([D.item(n, weight=w) for n, w in entries] + [{**D.EMPTY, 'weight': max(10, total)}])
    return out


def jukebox():
    import soundfile as sf
    for sid, (_, _, comparator) in DISCS.items():
        info = sf.info(os.path.join(ASSETS, 'sounds', sid + '.ogg'))
        D.write(f'jukebox_song/{sid[5:]}.json', {'sound_event': f'oathbound:{sid}', 'description': {'translate': f'jukebox_song.oathbound.{sid[5:]}'},
                                                  'length_in_seconds': round(info.duration, 1), 'comparator_output': comparator})


def tags():
    D.tag('item/creeper_drop_music_discs', ['music_' + s for s in DISCS], 'minecraft')


def generate():
    java()
    assets()
    print(len(RELICS) + len(FOODS) + len(ELIXIRS) + len(DROPS) + len(PAGES) + len(DISCS), 'wares written')


if __name__ == '__main__':
    generate()
