"""English text for Oathbound: names, tooltips, the Chronicle's story, quests, boons, tablets, riddles,
puzzle messages, subtitles and commands. Writes assets/oathbound/lang/en_us.json and checks that every key
the Java code asks for exists.

Run from the repository root:  python3 -m tools.oath.lang

Markup inside Chronicle text: *gold* and _rubric_ (see ChronicleScreen.styled).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/main/resources/assets/oathbound/lang/en_us.json')

L = {}


def put(key, text):
    L[key] = text


def names(prefix, mapping):
    for k, v in mapping.items():
        put(f'{prefix}.oathbound.{k}', v)


# ====================================================================== items & blocks
ITEMS = {
    'lantern_chronicle': 'The Lantern Chronicle',
    'lumenite_shard': 'Lumenite Shard', 'lumenite_dust': 'Lumenite Dust', 'oathsteel_blend': 'Oathsteel Blend',
    'oathsteel_ingot': 'Oathsteel Ingot', 'oathsteel_nugget': 'Oathsteel Nugget', 'spellsilk': 'Spellsilk',
    'luminous_dust': 'Luminous Dust', 'gloam_essence': 'Gloam Essence', 'lanternguard_insignia': 'Lanternguard Insignia',
    'seal_of_valor': 'Seal of Valor', 'seal_of_wisdom': 'Seal of Wisdom', 'seal_of_sacrifice': 'Seal of Sacrifice',
    'oathkey': 'The Oathkey', 'everflame_ember': 'Everflame Ember',
    'wardens_lantern': "Warden's Lantern", 'everflame_lantern': 'The Everflame Lantern',
    'oathsteel_longsword': 'Oathsteel Longsword', 'wardens_halberd': "Warden's Halberd", 'drowned_anchor': 'The Drowned Anchor',
    'staff_of_veyl': 'Staff of Veyl', 'dawnstring_longbow': 'Dawnstring Longbow', 'housecarl_warhorn': "Housecarl's Warhorn",
    'shadowreap_sickle': 'Shadowreap Sickle', 'dawnbreaker': 'Dawnbreaker', 'lumen_flask': 'Lumen Flask',
    'oathsteel_pickaxe': 'Oathsteel Pickaxe', 'oathsteel_axe': 'Oathsteel Axe', 'oathsteel_shovel': 'Oathsteel Shovel',
    'oathsteel_helmet': 'Oathsteel Helm', 'oathsteel_chestplate': 'Oathsteel Cuirass', 'oathsteel_leggings': 'Oathsteel Greaves',
    'oathsteel_boots': 'Oathsteel Sabatons', 'arcanist_hood': 'Arcanist Hood', 'arcanist_robe': 'Arcanist Robe',
    'arcanist_leggings': 'Arcanist Breeches', 'arcanist_boots': 'Arcanist Slippers', 'hollow_crown': 'The Hollow Crown',
    'wayfarers_bread': "Wayfarer's Bread", 'honeyed_mead': 'Honeyed Mead', 'knights_stew': "Knight's Stew",
    'elixir_of_dawn': 'Elixir of Dawn',
}
for mob in ('lanternmoth', 'gloamling', 'forsworn_knight', 'barrow_wight', 'animated_tome', 'veilhound', 'spectral_housecarl',
            'sir_caldris', 'archmage_veyl', 'hrodgar', 'morvane'):
    pass

BLOCKS = {
    'lumenite_ore': 'Lumenite Ore', 'deepslate_lumenite_ore': 'Deepslate Lumenite Ore', 'lumenite_block': 'Block of Lumenite',
    'oathsteel_block': 'Block of Oathsteel', 'wardstone': 'Wardstone', 'wardstone_bricks': 'Wardstone Bricks',
    'cracked_wardstone_bricks': 'Cracked Wardstone Bricks', 'mossy_wardstone_bricks': 'Mossy Wardstone Bricks',
    'chiseled_wardstone': 'Chiseled Wardstone', 'wardstone_brick_stairs': 'Wardstone Brick Stairs',
    'wardstone_brick_slab': 'Wardstone Brick Slab', 'wardstone_pillar': 'Wardstone Pillar', 'gloamstone': 'Gloamstone',
    'gloam_moss': 'Gloam Moss', 'gloamstone_bricks': 'Gloamstone Bricks', 'gloamwood_log': 'Gloamwood Log',
    'gloamwood_planks': 'Gloamwood Planks', 'veilbloom': 'Veilbloom', 'lore_tablet': 'Lanternguard Tablet',
    'wayshrine_brazier': 'Wayshrine Brazier', 'chapel_bell': 'Chapel Bell', 'hymn_stone': 'Hymn Stone', 'rune_dial': 'Rune Dial',
    'cipher_lectern': "Archmage's Cipher", 'arcane_ward': 'Arcane Ward', 'sealed_grate': 'Sealed Grate', 'barrow_seal': 'Barrow Seal',
    'sarcophagus': "King's Sarcophagus", 'ward_lantern': 'Ward Lantern', 'sundered_keystone': 'Sundered Keystone',
    'gloam_veil': 'Gloam Veil', 'wisplight': 'Wisplight',
}

ENTITIES = {
    'lanternmoth': 'Lanternmoth', 'gloamling': 'Gloamling', 'forsworn_knight': 'Forsworn Knight', 'barrow_wight': 'Barrow Wight',
    'animated_tome': 'Animated Tome', 'veilhound': 'Veilhound', 'spectral_housecarl': 'Spectral Housecarl',
    'sir_caldris': 'Sir Caldris, the Drowned Knight', 'archmage_veyl': 'Archmage Veyl, the Hollow Magus',
    'hrodgar': 'Hrodgar, the Barrow-King', 'morvane': 'Morvane, the Hollow King', 'spell_mark': 'Spell Mark',
    'arcane_orb': 'Arcane Orb', 'glyph_bolt': 'Glyph Bolt', 'gloam_bolt': 'Gloam Bolt', 'crown_blade': 'Crown Blade',
    'anchor_hook': 'Drowned Anchor', 'sun_arrow': 'Sun-Arrow', 'lumen_flask': 'Lumen Flask',
}

# tooltip inscriptions: first line is grey italic flavour, the rest gold mechanics bullets
DESC = {
    'lantern_chronicle': ['The living book of the Lanternguard. It chose you.', 'Use to open. It remembers what you do.'],
    'lumenite_shard': ['Sunlight that fell into the stone and stayed.', 'Use with a Warden\'s Lantern in the other hand to refuel it.'],
    'lumenite_dust': ['It glitters even in a closed fist.'],
    'oathsteel_blend': ['Iron and lumenite, waiting for the fire.'],
    'spellsilk': ['Woven on looms that were never touched by hands.'],
    'luminous_dust': ['Shed by lanternmoths. It never quite stops glowing.'],
    'gloam_essence': ['A little of the grey country, cold to the touch.'],
    'lanternguard_insignia': ['A knight\'s badge: a lantern on a shield.', 'Four of these and an Everflame Ember remake the Order\'s lantern.'],
    'seal_of_valor': ['Given up by Sir Caldris of the Drowned Chapel.', 'One of the three seals of the Oathkey.'],
    'seal_of_wisdom': ['Given up by Archmage Veyl of the Hollow Spire.', 'One of the three seals of the Oathkey.'],
    'seal_of_sacrifice': ['Given up by Hrodgar, the Barrow-King.', 'One of the three seals of the Oathkey.'],
    'oathkey': ['Three oaths bound into one key.', 'Use on the Sundered Keystone to open the Gate.'],
    'everflame_ember': ['A coal of the first dawn, won back from the Hollow King.', 'Warm enough to kindle the Everflame Lantern.'],
    'wardens_lantern': ['The Lanternguard never walked in the dark.',
                        'Held: a wisplight follows you; lights Hymn Stones and Ward Lanterns.',
                        'Use to Seek where the Chronicle would have you go. Burns lumenite.'],
    'everflame_lantern': ['The Order\'s lantern, burning again.', 'Never gutters, never needs lumenite.',
                          'Seeks, lights and wards like a Warden\'s Lantern.'],
    'oathsteel_longsword': ['A knight\'s blade: patient, then sudden.', 'Riposte: damage you take in the last 3s is added to your next blow.'],
    'wardens_halberd': ['Reach first, then everything else.', '+1.5 reach. A sprinting strike thrusts through a whole line of foes.'],
    'drowned_anchor': ['It still drips, a long way from any sea.', 'Use to throw it on its chain:',
                       'hooks a creature and hauls it to you, or hauls you to the stone it bites.'],
    'staff_of_veyl': ['The Archmage never set it down.', 'Use to loose an Arcane Chain that leaps between up to five foes,',
                      'weaker with every leap.'],
    'dawnstring_longbow': ['Strung with light, and it remembers it.', 'Fully drawn: the arrow burns with dawn and pierces.',
                           'Targets struck are Sunmarked: they glow and take 30% more damage.'],
    'housecarl_warhorn': ['Hrodgar\'s guard still answers it.', 'Sound it to call two Spectral Housecarls to fight beside you for 40s.'],
    'shadowreap_sickle': ['It drinks the dark.', 'The darker the place, the harder it strikes and the more it heals you.'],
    'dawnbreaker': ['Forged to end the Hollow King.', 'Hold use to gather light; release for a Dawn Rite:',
                    'a burst of sunlight that strikes Gloam creatures and the undead threefold.'],
    'lumen_flask': ['Light, corked.', 'Throw to burst in blinding light that burns Gloam creatures and leaves wisplights.'],
    'hollow_crown': ['Morvane swore on it. Nothing wears it now.', 'Night vision. Gloam creatures leave you be unless struck.',
                     '+4 maximum health.'],
    'wayfarers_bread': ['Baked for long roads.'],
    'honeyed_mead': ['The Order\'s own. Regeneration and a golden warmth; mind the spinning.'],
    'knights_stew': ['A meal to march on: Resistance and Strength.'],
    'elixir_of_dawn': ['Drink the morning. Cures Gloamrot and grants Radiance for three minutes.'],
}

# ====================================================================== the Chronicle
CHAPTERS = ['I. The Last Squire', 'II. Where the Bells Drown', 'III. The Hollow Spire', 'IV. The Barrow of Kings',
            'V. The Sundered Gate', 'VI. The Hollow Crown', 'VII. Tales and Secrets']
LORE = [
    # I
    "You were a squire of the *Order of the Ember Lantern* for one night. Then the Order was gone, and only this book "
    "remained, warm in your hands as if someone had just been reading it.\n\n"
    "The _Lanternguard_ were knight-wizards who carried the *Everflame*, a fire kindled at the first dawn. For four hundred "
    "years they kept the night from coming too far into the world. Their towers are ruins now; their wayshrines are cold.\n\n"
    "Begin where they began. Find *lumenite* in the stone, where sunlight fell and stayed. Blend it with iron and forge "
    "*Oathsteel*. Build a _Warden's Lantern_ and carry it to a *Wayshrine*. Kindle the brazier. The Order will know you.",
    # II
    "The kindled wayshrine burned for a long time after you left it, and the Chronicle turned its own pages that night.\n\n"
    "_Sir Caldris_ was the Order's Tide-Knight, who swore that no tide would ever reach the chapel where the Order kept its "
    "vows. The sea came anyway. He is still there, beneath the water-dark nave, keeping the *Seal of Valor* for a war that "
    "ended four centuries ago.\n\n"
    "The drowned chapel has a *Hymn Stone*. It sings only to a Warden's light. Learn its hymn and ring the chapel bells in "
    "that order; the crypt will open. Mind his tower shield: Caldris does not turn his back.",
    # III
    "With the Seal of Valor in your pack the Chronicle wrote in a new hand, thin and precise.\n\n"
    "_Archmage Veyl_ taught the Order its wards. When the three bound the Hollow King, Veyl bound his own mind into the "
    "*Seal of Wisdom*, so the seal could never forget what it held. He has not forgotten. He has not slept, either.\n\n"
    "His spire answers only to those who solve his *Cipher*: four riddles, four glyphs, four dials. The ward before his "
    "sanctum will not so much as flicker for anyone who has not first proven their valor. Watch for the one of him whose "
    "staff burns gold.",
    # IV
    "The Chronicle's pages smell of earth now.\n\n"
    "_Hrodgar_ was the first of the Barrow-Kings, dead two hundred years before the Order fell. When the three needed a "
    "third oath, he returned from his tomb to give it, and the *Seal of Sacrifice* is sealed with his death as much as his life.\n\n"
    "Three other kings sleep in his barrow, and their epitaphs disagree. *Exactly one of them told the truth.* Kneel at the "
    "honest king's tomb and Hrodgar's hall will open. Kneel at a liar's, and the barrow will answer.",
    # V
    "Three seals. One key.\n\n"
    "The *Oathkey* is the three oaths bound into one: valor, wisdom and sacrifice. The *Sundered Citadel*, where the Order "
    "fell in a single night, still holds the gate the three used to shut Morvane out of the world.\n\n"
    "Find the citadel. Set the Oathkey into the *Sundered Keystone*. Then step through the veil, into the _Gloaming_: the "
    "grey country between dusk and night. Keep your lantern lit there. Those who walk the Gloaming without light begin to "
    "fade.",
    # VI
    "_Morvane_ was the Lord-Commander of the Order of the Ember Lantern. He feared death more than he loved anything, and "
    "in the Gloaming he found the *Hollow Crown*, which promised a reign without end to whoever swore upon it.\n\n"
    "He swore, and he lied, and the Gloam poured through him. He is not a man any more. He is armour with a void inside it, "
    "sitting a throne on the highest island of the grey country, ringed by four *Ward Lanterns*.\n\n"
    "When the lanterns gutter and the dark takes him, light them again. Nothing hides from the Everflame for long.",
    # VII
    "Not everything the Order left behind is on the road to the throne.\n\n"
    "Lanternguard knights hid their *insignia* in their strongholds, behind brickwork that looks a little too cracked. "
    "Their *tablets* still stand in the ruins, each carved with a piece of the Order's history. The creatures of the world "
    "have their own stories too.\n\n"
    "The Chronicle keeps all of it. Turn its pages when the road is quiet.",
]
EPILOGUE_TITLE = 'Epilogue: The First Light'
EPILOGUE = ("The Hollow Crown cracked, and light came out of it: four hundred years of stolen dawns, all at once.\n\n"
            "The Gloaming is still there, between dusk and night, but it is only grey now, not hungry. The veil will open for "
            "you whenever you wish. The Everflame is yours to rekindle, if you can gather the insignia of the Order you "
            "never got to join.\n\n"
            "The Chronicle has one page left, and it is blank. It is waiting for you to write the Order's next oath.")

# quests: id -> (title, description, hint)
QUESTS = {
    'root': ('The Lantern Chronicle', 'Open the Chronicle. Its pages will fill as you walk the Order\'s road.',
             'Right-click the Chronicle to open it.'),
    'lumenite': ('Sunlight in Stone', 'Mine Lumenite Ore, which glows faintly in the deep rock.',
                 'Lumenite is found from deep below up to about y 56. An iron pickaxe or better.'),
    'oathsteel': ('Forge Oathsteel', 'Blend iron with lumenite and smelt the blend into an Oathsteel Ingot.',
                  'Oathsteel Blend: 1 iron ingot + 2 lumenite shards, shapeless. Smelt it.'),
    'lantern': ("The Warden's Lantern", 'Craft the lantern every knight of the Order carried.',
                'Nuggets around a lumenite shard, on an oathsteel ingot.'),
    'wayshrine': ('Kindle a Wayshrine', 'Find one of the Order\'s roadside wayshrines and kindle its brazier with your lantern.',
                  'Use the lantern to Seek. Kindle the brazier with the lantern lit in your hand.'),
    'oathsteel_arms': ('Oath-Forged Arms', 'Forge an Oathsteel Longsword or a Warden\'s Halberd.', 'Both are made from oathsteel and sticks.'),
    'oathsteel_armor': ('The Knight\'s Harness', 'Forge any piece of Oathsteel armour.', 'The full set grants Steadfast.'),
    'chapel': ('Where the Bells Drown', 'Find a Drowned Chapel at the edge of a swamp, river or shore.',
               'Your lantern\'s Seek will point the way once the wayshrine is kindled.'),
    'hymn': ('The Hymn of the Tide', 'Learn the Hymn Stone\'s song by lantern-light, then ring the chapel bells in its order.',
             'Read the Hymn Stone with a lit lantern. A wrong note starts the hymn over.'),
    'caldris': ('The Drowned Knight', 'Defeat Sir Caldris and take back the Seal of Valor.',
                'His shield blocks everything from the front. Flank him, or break his guard with an axe.'),
    'anchor': ('Something to Hold On To', 'Claim the Drowned Anchor.', 'Sir Caldris carried it.'),
    'spire': ('The Hollow Spire', 'Find the Arcanist\'s Spire in the forests or the northern woods.', 'Seek with your lantern.'),
    'spellsilk': ('Woven Without Hands', 'Gather Spellsilk.', 'Animated Tomes shed it; the spire\'s shelves hold more.'),
    'cipher': ('The Archmage\'s Cipher', 'Solve Veyl\'s four riddles and set the four Rune Dials to match.',
               'Read the Cipher on its lectern. Dial I answers riddle I, and so on.'),
    'veyl': ('The Hollow Magus', 'Defeat Archmage Veyl and take back the Seal of Wisdom.',
             'Strike his orbs back at him. Of his mirror images, the real Veyl\'s staff burns gold.'),
    'arcanist': ('Regalia of the Spire', 'Sew any piece of Arcanist regalia.', 'The full set halves the cooldowns of the Order\'s arts.'),
    'dawnstring': ('Strung with Light', 'Craft the Dawnstring Longbow.', 'Spellsilk and lumenite.'),
    'barrow': ('The Barrow of Kings', 'Find the Barrow of Kings, a green mound on the open plains.', 'Seek with your lantern.'),
    'honest_king': ('One of Three Told the Truth', 'Read the three epitaphs and kneel at the tomb of the only king who told the truth.',
                    'Exactly one epitaph is true. Sneak and use the tomb to kneel. You must carry the Seal of Wisdom.'),
    'hrodgar': ('The Barrow-King', 'Defeat Hrodgar and take back the Seal of Sacrifice.',
                'Jump his flail\'s shockwaves. Break the tethers of his housecarls before you strike at him.'),
    'warhorn': ('The Housecarls\' Call', 'Claim Hrodgar\'s Warhorn.', 'Hrodgar carried it.'),
    'oathkey': ('Three Oaths, One Key', 'Bind the three seals into the Oathkey.', 'The three seals around an oathsteel ingot, over gold.'),
    'citadel': ('The Sundered Citadel', 'Find the ruin where the Order fell.', 'It is rare, and far. Seek with your lantern.'),
    'gate': ('Open the Sundered Gate', 'Set the Oathkey in the Sundered Keystone and open the Gate.',
             'Use the Oathkey on the keystone at the heart of the citadel.'),
    'gloaming': ('Into the Gloaming', 'Step through the veil into the grey country.', 'Keep a lantern lit, or drink an Elixir of Dawn.'),
    'sickle': ('It Drinks the Dark', 'Forge the Shadowreap Sickle.', 'Oathsteel, gloam essence and a stick.'),
    'veilhound': ('The Hounds of the Veil', 'Slay a Veilhound.', 'They circle before they strike. Keep your back to something.'),
    'throne': ('The Hollow Throne', 'Climb to the Hollow Throne and challenge the King.', 'The throne stands on the Gloaming\'s high island.'),
    'morvane': ('The Hollow King', 'Break the Hollow Crown. Defeat Morvane.',
                'When the lanterns go out, light them again. All four lit leaves him Unveiled.'),
    'dawnbreaker': ('The First Light, Forged', 'Claim Dawnbreaker.', 'Morvane\'s end is its beginning.'),
    'crown': ('Uneasy Lies the Head', 'Claim the Hollow Crown.', 'It will not hurt you. You never swore on it.'),
    'gloamling': ('Things that Giggle in the Dark', 'Slay a Gloamling.', 'Hold a lit lantern: they cannot hide in its light.'),
    'lanternmoth': ('Moths to a Lantern', 'Gather Luminous Dust from Lanternmoths.', 'They drift through woods at night, drawn to your light.'),
    'elixir': ('Drink the Morning', 'Brew an Elixir of Dawn.', 'A bottle, luminous dust, gloam essence and a golden carrot.'),
    'flask': ('Light, Corked', 'Make a Lumen Flask.', 'Glass around luminous dust.'),
    'forsworn': ('Rest for the Forsworn', 'Lay a Forsworn Knight to rest for good.',
                 'They rise again unless the last blow is oathsteel, fire or light.'),
    'insignia': ('A Knight\'s Badge', 'Find a Lanternguard Insignia.', 'Every stronghold hides one behind cracked brickwork.'),
    'loremaster': ('Keeper of the Chronicle', 'Read all ten Lanternguard Tablets.', 'They stand in the Order\'s ruins, one or two in each.'),
    'everflame': ('The Everflame Rekindled', 'Remake the Order\'s own lantern.', 'Four insignia around a Warden\'s Lantern, with Everflame Embers.'),
}

BOONS = {
    'squires_vigor': ("Squire's Vigor", '+2 hearts of maximum health.'),
    'lamplighters_thrift': ("Lamplighter's Thrift", 'Your lanterns burn half as much lumenite.'),
    'pilgrims_stride': ("Pilgrim's Stride", 'You walk 8% faster.'),
    'tidebound': ('Tidebound', 'In water you breathe freely and swim like the tide.'),
    'knights_guard': ("Knight's Guard", 'Blows struck at you up close deal 10% less.'),
    'long_reach': ('Long Reach', 'You reach one block further, for blows and for blocks.'),
    'arcane_insight': ('Arcane Insight', 'The Order\'s arts recover a quarter faster.'),
    'scholars_luck': ("Scholar's Luck", '+2 Luck: better fishing and better finds.'),
    'glyphskin': ('Glyphskin', 'Magic harms you 20% less.'),
    'oath_of_the_housecarl': ('Oath of the Housecarl', 'When you fall low, a Spectral Housecarl rises to guard you. Once every two minutes.'),
    'kingsblood': ('Kingsblood', '+2 armour and +2 armour toughness.'),
    'grave_sight': ('Grave Sight', 'Deep underground, you see in the dark.'),
    'veilwalker': ('Veilwalker', 'The Gloaming cannot rot you, lantern or no.'),
    'gatesworn': ('Gatesworn', 'Your blows strike 15% harder.'),
    'featherfall': ('Featherfall', 'You fall five blocks further before it hurts.'),
    'everflame_heart': ('Everflame Heart', 'Radiance burns in you always.'),
    'kingslayer': ('Kingslayer', 'You deal 20% more damage to keepers and kings.'),
    'dawnbound': ('Dawnbound', 'Under an open sky by day, you slowly heal.'),
}

# ten tablets: title + lines (line counts must match LoreTabletBlock.LINES = 4,4,4,5,4,5,4,5,4,4)
TABLETS = [
    ('The First Dawn', ["Before the first morning there was only the grey,", "and in the grey a single ember that would not go out.",
                        "The first knights carried it out into the world", "and called it the Everflame."]),
    ('The Order of the Ember Lantern', ["We swear to carry light where it is needed,", "to walk first into the dark,",
                                        "to keep no flame for ourselves alone.", "So swore every squire. So swore Morvane."]),
    ('On Wayshrines', ["Where the road is long, kindle a shrine.", "Where a shrine is kindled, the Order is fed.",
                       "A cold shrine is a knight who did not come home.", "Leave none of them cold."]),
    ('The Tide-Knight', ["Caldris swore the tide would not take the chapel.", "The tide came anyway.",
                         "He stood in the nave until the water closed over his helm,", "and he is standing there still.",
                         "Some oaths are kept past all reason."]),
    ("The Archmage's Maxim", ["A ward is a question the dark cannot answer.", "Ask it well, and ask it forever.",
                              "I have bound my own mind into this seal", "so that the question will never be forgotten."]),
    ('The Barrow-King', ["Hrodgar was two hundred years dead when we called him.", "He came, and he gave his oath,",
                         "and he lay down again under the green mound.", "His housecarls would not leave him.",
                         "They are there yet, and so is he."]),
    ('The Night of Ash', ["The Lord-Commander came back from the Gloaming wearing a crown.", "By midnight the lanterns were out.",
                          "By dawn there was no Order left to raise them.", "Only three of us still had our oaths."]),
    ('The Binding', ["Valor to hold the door.", "Wisdom to lock it.", "Sacrifice to pay for the lock.",
                     "Three seals, one key, and a gate that must never open", "unless the Order returns to close it for good."]),
    ('The Grey Country', ["Between dusk and night there is a country", "where nothing is born and nothing quite dies.",
                          "Carry light there, or it will take the colour out of you", "a little at a time."]),
    ('To the Last Squire', ["If you are reading this, the Chronicle has chosen.", "We are sorry to leave you so much work.",
                            "Kindle the shrines. Keep the oaths.", "Break the crown."]),
]

BESTIARY = {
    'lanternmoth': ('Lanternmoth', 'A gentle moth whose abdomen glows like a lantern-flame. They drift through woodland at night and '
                    'gather around anyone carrying a light. The Order took them as its heraldic beast.',
                    'They shed *Luminous Dust*, the heart of lumen flasks and the Elixir of Dawn.'),
    'gloamling': ('Gloamling', 'Imps of the dusk that seep out of the Gloaming at night. In darkness they are almost invisible; '
                  'only a lantern\'s light holds them to a shape. They strike and scatter, giggling.',
                  'They burn in daylight. Hold a lit lantern to see them clearly.'),
    'sir_caldris': ('Sir Caldris', 'The Tide-Knight of the Drowned Chapel, still standing his vigil beneath the water. His tower '
                    'shield turns every frontal blow. His anchor drags the unwary into his reach.',
                    'Flank him, or break his guard with an axe. At half strength he calls drowned squires.'),
    'animated_tome': ('Animated Tome', 'Grimoires of the Arcanist\'s Spire that learned to fly after their readers stopped reading. '
                      'They flit erratically and loose glyph bolts.', 'They shed *Spellsilk* from their bindings.'),
    'archmage_veyl': ('Archmage Veyl', 'The Order\'s master of wards, who bound his own mind into the Seal of Wisdom. He blinks, '
                      'he mirrors himself, and his gravity glyphs lift the ground from under you.',
                      'His orbs can be struck back at him. Of his reflections, only the real one\'s staff burns gold.'),
    'barrow_wight': ('Barrow Wight', 'Grave-spirits of the Barrow of Kings, drifting in the burial cloth they were laid out in. '
                     'Their touch carries the cold of the tomb.', 'Their Grave Chill slows you and dulls your pick.'),
    'spectral_housecarl': ('Spectral Housecarl', 'Hrodgar\'s oath-sworn guards, who would not leave their king even in death. They '
                           'fight for him still, and for whoever sounds his horn.', 'While tethered to Hrodgar, they shield him.'),
    'hrodgar': ('Hrodgar', 'The first Barrow-King, a giant who returned from the grave to give his oath. His flail breaks the '
                'earth into rings of force; his housecarls rise to shield him.',
                'Jump the shockwaves. At the end, he will try to devour his own guard to heal.'),
    'forsworn_knight': ('Forsworn Knight', 'Knights of the Order who followed Morvane into the dark. Their oaths are broken, but '
                        'their armour will not lie still: strike one down and it rises again.',
                        'Only oathsteel, fire or light lays them to rest.'),
    'veilhound': ('Veilhound', 'Pack-hunters of the Gloaming, darker than their own shadows. They circle, testing, and lunge '
                  'from several sides at once.', 'Keep a wall at your back.'),
    'morvane': ('Morvane', 'The Hollow King. Once Lord-Commander of the Order; now armour with a void inside it, crowned with '
                'a promise that was a lie. He duels, then sorcerers, then hides in the dark.',
                'When the Ward Lanterns go out, light all four again to Unveil him.'),
}

ARMORY = {
    'wardens_lantern': ("Warden's Lantern", 'The lantern every knight of the Order carried. Held, it keeps a wisplight burning '
                        'at your head, wakes Hymn Stones and relights Ward Lanterns. Used, it *Seeks* the next place the '
                        'Chronicle would send you.', 'Feed it lumenite shards when it runs low.'),
    'oathsteel_longsword': ('Oathsteel Longsword', 'A patient blade. Every wound you take in the three seconds before you swing '
                            'is added to the blow as a *Riposte*.', 'Oathsteel mends itself slowly in the sun.'),
    'wardens_halberd': ("Warden's Halberd", 'A long reach, and a sprinting strike that drives through every foe in a line.',
                        'Oathsteel mends itself slowly in the sun.'),
    'lumen_flask': ('Lumen Flask', 'A glass of light. Thrown, it bursts, blinding and burning Gloam creatures and leaving '
                    'wisplights hanging in the air.', 'Three from one measure of luminous dust.'),
    'drowned_anchor': ('The Drowned Anchor', 'Sir Caldris\'s anchor. Thrown on its chain it hooks a creature and hauls it to '
                       'you, or bites into stone and hauls you after it.', 'Also a brutal club.'),
    'staff_of_veyl': ('Staff of Veyl', 'The Archmage\'s staff. It looses an *Arcane Chain* that leaps from foe to foe, up to '
                      'five, weakening with every leap.', 'Arcanist regalia halves its cooldown.'),
    'dawnstring_longbow': ('Dawnstring Longbow', 'A bow strung with spellsilk and light. A full draw looses a sun-arrow that '
                           'pierces and *Sunmarks* what it strikes.', 'Sunmarked foes glow and take 30% more damage.'),
    'arcanist_robe': ('Arcanist Regalia', 'Robes of the Spire, sewn from spellsilk. The full regalia halves the cooldowns of the '
                      'Order\'s arts and lets you drift gently when you sneak mid-air.', 'Light, but not armour for a knight.'),
    'housecarl_warhorn': ("Housecarl's Warhorn", 'Hrodgar\'s horn. Sounded, it calls two Spectral Housecarls to fight beside '
                          'you for forty seconds.', 'They will not strike you, whatever you do.'),
    'oathkey': ('The Oathkey', 'The three seals bound into one key. It opens the Sundered Gate, and nothing else.',
                'Set it in the Sundered Keystone.'),
    'shadowreap_sickle': ('Shadowreap Sickle', 'A sickle that drinks the dark. The less light around what it strikes, the '
                          'harder the blow and the more of it returns to you as health.', 'In daylight it is only a sickle.'),
    'dawnbreaker': ('Dawnbreaker', 'The blade that ended the Hollow King. Hold it high to gather light, then let it go in a '
                    '*Dawn Rite* that strikes the Gloam and the undead threefold.', 'It never quite stops glowing.'),
    'hollow_crown': ('The Hollow Crown', 'Morvane\'s crown, empty now. It grants sight in the dark, a little more life, and '
                     'the Gloam\'s creatures will not trouble its wearer unless provoked.', 'You never swore on it. That is why it is safe.'),
    'everflame_lantern': ('The Everflame Lantern', 'The Order\'s own lantern, rekindled with an ember of the first dawn and the '
                          'insignia of its fallen knights. It never gutters.', 'Some oaths are worth keeping after all.'),
}

GLYPHS = ['the Lantern', 'the Crossing', 'the Seal', 'the Keep', 'the Eye', 'the Crown']
RIDDLES = {
    0: ["I am carried into the dark so that the dark may be carried out.", "I have a heart of fire and a body of iron, and I hang from a hand."],
    1: ["Two roads meet in me, and neither ends.", "I am where the sword and the oath cross."],
    2: ["Break me, and what I held is free.", "I am pressed in wax and in stone, and I keep what I close."],
    3: ["I have walls but no rooms, and I am the last to fall.", "Four towers, one heart; the siege ends when I do."],
    4: ["I see only what is lit, and I am the first thing a ward must fool.", "I open at dawn and close at dusk, and I weep."],
    5: ["I sat on the head of a man who lied, and I was empty.", "I have points but no edge, and a king under me."],
}
KINGS = ['Eadric Oakenhelm', 'Wulfstan the Sword-Oath', 'Aethelwin Shieldbearer']
TONES = ['blue', 'green', 'gold', 'red']
COMPASS = {'n': 'north', 'nne': 'north-northeast', 'ne': 'northeast', 'ene': 'east-northeast', 'e': 'east', 'ese': 'east-southeast',
           'se': 'southeast', 'sse': 'south-southeast', 's': 'south', 'ssw': 'south-southwest', 'sw': 'southwest',
           'wsw': 'west-southwest', 'w': 'west', 'wnw': 'west-northwest', 'nw': 'northwest', 'nnw': 'north-northwest'}
SEEK = {'wayshrine': 'a Wayshrine', 'chapel': 'the Drowned Chapel', 'spire': "the Arcanist's Spire", 'barrow': 'the Barrow of Kings',
        'citadel': 'the Sundered Citadel', 'throne': 'the Hollow Throne'}

MESSAGES = {
    'message.oathbound.welcome': 'The Lantern Chronicle has chosen you. Open it to begin.',
    'message.oathbound.lantern.empty': 'Your lantern has burned out. Feed it a lumenite shard.',
    'message.oathbound.lantern.out': 'Your lantern gutters and goes dark.',
    'message.oathbound.shard.refuel': 'The lantern drinks the light: %s%%',
    'message.oathbound.shard.no_lantern': 'Hold a Warden\'s Lantern in your other hand to refuel it.',
    'message.oathbound.seek.found': '%1$s lies %3$s blocks to the %2$s.',
    'message.oathbound.seek.far': 'The lantern strains toward %s, but it is too far to see.',
    'message.oathbound.seek.none': 'The lantern has nowhere left to lead you. Your road is your own.',
    'message.oathbound.wayshrine.kindled': 'The wayshrine takes the flame. Somewhere, the Order remembers.',
    'message.oathbound.wayshrine.blessing': 'The shrine\'s warmth settles on you.',
    'message.oathbound.wayshrine.hint': 'Kindle the brazier with a lit Warden\'s Lantern in your hand.',
    'message.oathbound.wayshrine.no_tithes': 'The Order owes you nothing yet.',
    'message.oathbound.hymn.title': '~ The Hymn of the Tide ~',
    'message.oathbound.hymn.verse': 'Five bells for the five waves that took the chapel. Ring them as the stone sings them.',
    'message.oathbound.hymn.instructions': 'Ring the chapel bells in this order. A wrong note starts the hymn over.',
    'message.oathbound.hymn.cold': 'The stone is cold and silent. It answers only a Warden\'s light.',
    'message.oathbound.hymn.cold_short': 'The bells are silent without a Warden\'s light.',
    'message.oathbound.hymn.progress': 'The hymn rises: %s of %s',
    'message.oathbound.hymn.discord': 'The bells clash. Something stirs in the flooded nave.',
    'message.oathbound.hymn.solved': 'The hymn is already sung.',
    'message.oathbound.hymn.opened': 'The last bell fades... and far below, the crypt grate lifts.',
    'message.oathbound.bell.rung': 'The %s bell tolls.',
    'message.oathbound.cipher.title': '~ The Archmage\'s Cipher ~',
    'message.oathbound.cipher.instructions': 'Set each numbered Rune Dial to the glyph its riddle names.',
    'message.oathbound.cipher.dark': 'The pages are blank. The cipher reveals itself only to one who holds the Seal of Valor.',
    'message.oathbound.cipher.solved': 'The dials lock. The ward before the sanctum shivers and dissolves.',
    'message.oathbound.cipher.opened': 'The cipher is solved. The sanctum stands open.',
    'message.oathbound.dial.shows': 'Dial %s shows %s.',
    'message.oathbound.dial.locked': 'The dial will not move. The cipher is solved.',
    'message.oathbound.dial.valor': 'The dial is frozen fast. Only one who holds the Seal of Valor may turn it.',
    'message.oathbound.ward.hint': 'An arcane ward. Somewhere in this place is the answer that dissolves it.',
    'message.oathbound.tomb.here_lies': 'Here lies %s. The epitaph reads:',
    'message.oathbound.tomb.kneel_hint': '(Sneak and use the tomb to kneel before this king.)',
    'message.oathbound.tomb.wisdom': 'You kneel, but the tomb does not know you. Return with the Seal of Wisdom.',
    'message.oathbound.tomb.honest': '%s told the truth. His tomb grinds open, and the way to Hrodgar\'s hall is clear.',
    'message.oathbound.tomb.liar': '%s lied, even in death. His barrow wakes!',
    'message.oathbound.tomb.open': 'The tomb of %s stands open.',
    'message.oathbound.gate.hint': 'A keystone with three empty settings. The Oathkey would fit it.',
    'message.oathbound.gate.open_hint': 'The Gate is open. The veil hangs in the arch.',
    'message.oathbound.gate.begin': 'You set the Oathkey into the keystone. The three oaths wake...',
    'message.oathbound.gate.already': 'The Gate is already open.',
    'message.oathbound.gloaming.missing': 'The veil will not open: the Gloaming is missing from this world. (Is the mod\'s data pack disabled?)',
    'message.oathbound.gloamrot': 'Without light, the Gloaming begins to take the colour out of you.',
    'message.oathbound.steadfast': 'Your harness holds. Steadfast!',
    'message.oathbound.forsworn.rest': 'The knight\'s armour falls still. At last.',
    'message.oathbound.hrodgar.tethered': 'Hrodgar\'s housecarls shield him. Break their tethers!',
    'message.oathbound.ward_lantern.hint': 'Light it with a lit Warden\'s Lantern or a lumenite shard.',
    'message.oathbound.morvane.wake': 'The lanterns gutter, one by one. On the throne, something that was a man lifts its head.',
    'message.oathbound.morvane.phase2': '"You carry his lantern. I carried it too." Morvane rises from the ground on wings of dusk.',
    'message.oathbound.morvane.phase3': 'The Ward Lanterns go out. The Hollow King becomes the dark itself. Light them!',
    'message.oathbound.morvane.hollow': 'The lanterns are out. Morvane cannot be touched in the dark.',
    'message.oathbound.morvane.unveiled': 'All four lanterns blaze! Morvane is UNVEILED.',
    'epitaph.oathbound.accuse': '%s, who lies beside me, never spoke a true word.',
    'epitaph.oathbound.vouch': 'Every word %s ever spoke was true.',
    'epitaph.oathbound.boast': 'Of all the kings who sleep in this barrow, I alone never lied.',
    'title.oathbound.gate': 'The Sundered Gate Opens',
    'title.oathbound.gate.sub': 'The veil to the Gloaming hangs in the arch',
    'title.oathbound.gloaming': 'The Gloaming',
    'title.oathbound.gloaming.sub': 'Between dusk and night',
    'title.oathbound.morvane.sub': 'The Hollow King',
    'title.oathbound.caldris.slain': 'The Seal of Valor',
    'title.oathbound.caldris.slain.sub': 'Sir Caldris lays down his vigil at last',
    'title.oathbound.veyl.slain': 'The Seal of Wisdom',
    'title.oathbound.veyl.slain.sub': 'Archmage Veyl finally sleeps',
    'title.oathbound.hrodgar.slain': 'The Seal of Sacrifice',
    'title.oathbound.hrodgar.slain.sub': 'Hrodgar returns to his rest',
    'title.oathbound.morvane.slain': 'The Hollow Crown Is Broken',
    'title.oathbound.morvane.slain.sub': 'Dawn comes to the Gloaming',
    'block.oathbound.sealed_grate.hint': 'The grate is sealed. Something in this place must open it.',
    'block.oathbound.barrow_seal.hint': 'The seal holds fast. It will open for the honest king.',
    'item.oathbound.wardens_lantern.fuel': 'Lumenite: %s%%',
    'itemGroup.oathbound': 'Oathbound',
    'effect.oathbound.radiance': 'Radiance',
    'effect.oathbound.gloamrot': 'Gloamrot',
    'effect.oathbound.sunmark': 'Sunmark',
    # the Chronicle's interface
    'chronicle.oathbound.tab.story': 'Chronicle',
    'chronicle.oathbound.tab.path': 'The Path',
    'chronicle.oathbound.tab.tithes': 'Tithes',
    'chronicle.oathbound.tab.bestiary': 'Bestiary',
    'chronicle.oathbound.tab.armory': 'Armory',
    'chronicle.oathbound.sealed': 'Sealed',
    'chronicle.oathbound.lore.sealed': 'These pages are sealed. Walk further along the Path and they will open.',
    'chronicle.oathbound.unknown': '???',
    'chronicle.oathbound.codex_locked': 'The Chronicle has not yet learned of this. Walk further along the Path.',
    'chronicle.oathbound.locked_quest': 'Finish the quest before this one to learn more.',
    'chronicle.oathbound.next': 'Next on the Path',
    'chronicle.oathbound.next.none': 'The Path is walked. The rest is yours.',
    'chronicle.oathbound.status.active': 'In progress',
    'chronicle.oathbound.status.owed': 'Tithe owed',
    'chronicle.oathbound.status.paid': 'Complete',
    'chronicle.oathbound.xp': '+%s experience',
    'chronicle.oathbound.tithe': 'Tithe',
    'chronicle.oathbound.tithe.paid': 'The wayshrine pays %s tithes. The flames bring them to you.',
    'chronicle.oathbound.tithes.title': 'The Order\'s Tithes',
    'chronicle.oathbound.tithes.how': 'The Order pays its knights at any kindled wayshrine. Warm your hands at one to collect everything you are owed.',
    'chronicle.oathbound.tithes.none': 'Nothing is owed. Walk the Path.',
    'chronicle.oathbound.tithes.owed': '%s tithes are waiting at the nearest kindled wayshrine.',
    'chronicle.oathbound.collect': 'Collect at a wayshrine',
    'chronicle.oathbound.boons.title': 'Oath Boons',
    'chronicle.oathbound.boons.about': 'Finish every main quest of a chapter and you may swear one of three permanent Oath Boons for it.',
    'chronicle.oathbound.boons.choose': 'Choose',
    'chronicle.oathbound.boons.prompt': 'Swear a boon for chapter %s:',
    'chronicle.oathbound.boons.once': 'You may swear only one. Choose well.',
    'chronicle.oathbound.boons.sealed': 'Finish this chapter\'s main quests to swear a boon.',
    'chronicle.oathbound.boon.sworn': 'You swear the oath of %s. The Chronicle records it.',
    'chronicle.oathbound.boon.already': 'You have already sworn a boon for this chapter.',
    'chronicle.oathbound.boon.locked': 'Finish the chapter\'s main quests first.',
    'chronicle.oathbound.boon.unknown': 'No such boon.',
    # commands
    'command.oathbound.unknown': 'Unknown option.',
    'command.oathbound.help.header': '— Oathbound admin commands (/oathbound ...) —',
    'command.oathbound.help.kit': 'kit — the gear of a knight who has walked the whole Path',
    'command.oathbound.help.build': 'build <structure> — build a structure at your feet',
    'command.oathbound.help.keeper': 'keeper <name> — summon a keeper or the Hollow King',
    'command.oathbound.help.stage': 'stage <1-7> — complete the Path up to a chapter',
    'command.oathbound.help.locate': 'locate — find the Chronicle\'s next destination',
    'command.oathbound.help.gate': 'gate — open the nearest Sundered Gate',
    'command.oathbound.help.gloaming': 'gloaming — travel to the Hollow Throne',
    'command.oathbound.help.home': 'home — return from the Gloaming',
    'command.oathbound.kit': 'You are equipped as a knight of the Order.',
    'command.oathbound.build': 'Built %s at %s, %s, %s.',
    'command.oathbound.keeper': 'Summoned %s.',
    'command.oathbound.stage': 'Completed the Path up to chapter %s (%s quests).',
    'command.oathbound.locate': '%s is at x %s, z %s (%s blocks away).',
    'command.oathbound.locate.none': 'Nothing to find within reach.',
    'command.oathbound.gate': 'Opened the gate (%s veil blocks).',
    'command.oathbound.gate.none': 'No Sundered Keystone nearby.',
}


def subtitles():
    try:
        from .sounds import SFX, STREAMS
    except Exception:
        return
    for name, (_, _, s) in SFX.items():
        put(f'subtitles.oathbound.{name}', s)
    for name, (_, s) in STREAMS.items():
        if s:
            put(f'subtitles.oathbound.{name}', s)


def build():
    from .building import NAMES as BUILDING
    from . import gear
    names('item', ITEMS)
    names('block', BLOCKS)
    names('block', BUILDING)
    names('item', gear.NAMES)
    from . import wares, roster
    names('entity', roster.NAMES)
    for mob, en in roster.NAMES.items():
        put(f'item.oathbound.{mob}_spawn_egg', f'{en} Spawn Egg')
    for k, (name, text, note) in roster.BESTIARY.items():
        put(f'bestiary.oathbound.{k}.name', name)
        put(f'bestiary.oathbound.{k}.text', text)
        put(f'bestiary.oathbound.{k}.note', note)
    names('item', wares.NAMES)
    for item, lines in wares.DESC.items():
        for i, l in enumerate(lines, 1):
            put(f'item.oathbound.{item}.desc.{i}', l)
    L.update(wares.LORE)
    for item, lines in gear.DESC.items():
        for i, l in enumerate(lines, 1):
            put(f'item.oathbound.{item}.desc.{i}', l)
    names('entity', ENTITIES)
    for mob in ('lanternmoth', 'gloamling', 'forsworn_knight', 'barrow_wight', 'animated_tome', 'veilhound', 'spectral_housecarl',
                'sir_caldris', 'archmage_veyl', 'hrodgar', 'morvane'):
        put(f'item.oathbound.{mob}_spawn_egg', f'{ENTITIES[mob].split(",")[0]} Spawn Egg')
    for item, lines in DESC.items():
        for i, l in enumerate(lines, 1):
            put(f'item.oathbound.{item}.desc.{i}', l)
    for i, t in enumerate(CHAPTERS):
        put(f'chronicle.oathbound.chapter.{i}', t)
        put(f'chronicle.oathbound.lore.{i}', LORE[i])
    put('chronicle.oathbound.chapter.epilogue', EPILOGUE_TITLE)
    put('chronicle.oathbound.lore.epilogue', EPILOGUE)
    for q, (title, desc, hint) in QUESTS.items():
        put(f'quest.oathbound.{q}.title', title)
        put(f'quest.oathbound.{q}.description', desc)
        put(f'quest.oathbound.{q}.hint', hint)
    for b, (title, desc) in BOONS.items():
        put(f'boon.oathbound.{b}.title', title)
        put(f'boon.oathbound.{b}.description', desc)
    for i, (title, lines) in enumerate(TABLETS):
        put(f'tablet.oathbound.{i}.title', title)
        for j, l in enumerate(lines, 1):
            put(f'tablet.oathbound.{i}.{j}', l)
    for kind, table in (('bestiary', BESTIARY), ('armory', ARMORY)):
        for k, (name, text, note) in table.items():
            put(f'{kind}.oathbound.{k}.name', name)
            put(f'{kind}.oathbound.{k}.text', text)
            put(f'{kind}.oathbound.{k}.note', note)
    for i, g in enumerate(GLYPHS):
        put(f'glyph.oathbound.{i}', g)
    for g, variants in RIDDLES.items():
        for v, text in enumerate(variants):
            put(f'riddle.oathbound.{g}.{v}', text)
    for i, k in enumerate(KINGS):
        put(f'king.oathbound.{i}', k)
    for i, t in enumerate(TONES):
        put(f'bell.oathbound.tone.{i}', t)
    names('compass', COMPASS)
    names('seek', SEEK)
    L.update(MESSAGES)
    subtitles()


def check():
    """Every literal key in the Java sources must exist; so must the known dynamic families."""
    missing = []
    src = ''
    for dirpath, _, files in os.walk(os.path.join(ROOT, 'src/main/java')):
        for f in files:
            if f.endswith('.java'):
                src += open(os.path.join(dirpath, f)).read()
    for key in set(re.findall(r'translatable\("([a-zA-Z]+\.oathbound\.[a-z0-9_.]+)"\)', src)) | \
            set(re.findall(r'translatable\("([a-zA-Z]+\.oathbound\.[a-z0-9_.]+)",', src)):
        if key.endswith('.'):
            continue
        if key not in L:
            missing.append(key)
    import sys
    sys.path.insert(0, ROOT)
    from tools.oath.data import quest_criteria, BOONS as DATA_BOONS
    for q in quest_criteria():
        for suffix in ('title', 'description', 'hint'):
            if f'quest.oathbound.{q}.{suffix}' not in L:
                missing.append(f'quest.oathbound.{q}.{suffix}')
    for b in DATA_BOONS:
        if f'boon.oathbound.{b}.title' not in L:
            missing.append(f'boon.oathbound.{b}.title')
    lines = [4, 4, 4, 5, 4, 5, 4, 5, 4, 4]
    for i, n in enumerate(lines):
        for j in range(1, n + 1):
            if f'tablet.oathbound.{i}.{j}' not in L:
                missing.append(f'tablet.oathbound.{i}.{j}')
    return missing


if __name__ == '__main__':
    build()
    miss = check()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(dict(sorted(L.items())), f, indent=2, ensure_ascii=False)
    print(len(L), 'keys;', 'missing:', miss)
