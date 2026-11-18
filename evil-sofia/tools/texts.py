"""Texts of the districts: start screen descriptions, leader descriptions and starting advisors.

Leaders' descriptions show when hovering over the leader portrait. Advisors are three per country (two political
advisors and an army chief) with the traits below, written to common/country_leader/ by tools/build_focus.py.
"""

# Start screen: the eight featured countries.
FEATURED = {
    "SRD": "The heart of Sofia: Vitosha Boulevard, Borisova Gradina, the Largo and the Party House. Small, rich and "
           "surrounded on every side, Sredets has the money, the ministries and every one of its neighbours' "
           "attention.",
    "OBR": "The district of Alexander Nevsky Cathedral, the university quarter and the Doctors' Garden. Oborishte "
           "sits right next to the Party House and has not yet decided which way it leans.",
    "LOZ": "Green slopes and villas between the centre and Vitosha, from South Park to Hladilnika. Lozenets is the "
           "only road from the centre to the mountain, and everyone who wants to reach Boyana must deal with it.",
    "TRD": "Named after Triaditsa, the medieval name of Sofia: Ivan Vazov, Strelbishte and the National Palace of "
           "Culture. Old money, old names and an army of pensioners who remember everything.",
    "KRP": "The western quarters around West Park and Razsadnika. Crowded, poor and tough, Krasna Polyana has more "
           "people willing to fight than rifles to give them.",
    "MLA": "Four housing estates and Business Park: one of the largest districts of Sofia, built in concrete and "
           "glass. Mladost has the manpower to dominate the south-east of the city.",
    "LYU": "Ten housing estates beneath the Lyulin mountain, the biggest district of Sofia by population. Lyulin is "
           "a city of its own on the western edge, and it is ruled by a man nobody knows by his real name.",
    "VIT": "From Boyana up to Cherni Vrah: villas, monasteries, pine forests and the mountain that watches over the "
           "city. Vitosha is rich, proud and certain it is too high up for the centre's politics to reach.",
}

LEADER_DESCS = {
    "SRD": "Victor Kolev holds the most valuable square kilometre in Bulgaria: the Largo, the Party House and the "
           "boutiques of Vitosha Boulevard. He has more friends than any warlord in Sofia and more enemies, and he "
           "keeps a careful list of both.\\n\\nGeorgi Yanchovichin of Lozenets has been on the first list since "
           "before either of them ruled anything. Daniel-Henry Capel of Vitosha is at the top of the second.",
    "OBR": "Anton Zafirov rules Oborishte from a café table in the shadow of Alexander Nevsky. Students, professors "
           "and old families all want something from him, and so far he has given each of them just enough to keep "
           "them waiting.\\n\\nHe is three streets from the Party House, and he knows that whoever rules Sredets will "
           "come knocking sooner or later.",
    "VIT": "Daniel-Henry Capel grew up in a villa in Boyana, raised by a mother with very firm opinions about the "
           "people of the centre. He inherited every one of them.\\n\\nHenry rules Vitosha from the top of the city, "
           "with the forest at his back and the whole of Sofia spread out below him. He believes that is exactly where "
           "he belongs.",
    "MLA": "Georgi Poryazov governs four housing estates and a business park with the patience of a man who knows he "
           "has more people than anyone around him. Mladost does not need to hurry.\\n\\nWhen the other districts run "
           "out of soldiers, Poryazov will still be counting his.",
    "KRP": "Stefan Kartunov came up through the courtyards of Krasna Polyana, and he still knows every one of them by "
           "name. His district is poor, crowded and loyal.\\n\\nKartunov promises his people one thing: that this "
           "time the west of the city will not be the part everyone else forgets.",
    "LOZ": "Georgi Yanchovichin rules the green slopes between the centre and the mountain. Lozenets is quiet, "
           "wealthy and exactly in the way of anyone who wants to march from Sredets to Boyana.\\n\\nGeorgi and Victor "
           "Kolev of Sredets are day ones: they were friends before the city fell apart, and Georgi does not forget "
           "his friends.",
    "TRD": "Alexander Dimitrov rules the district that carries the old name of the city. Triaditsa has the National "
           "Palace of Culture, the best schools in Sofia and residents who will explain at length why things were "
           "better before.\\n\\nDimitrov listens to all of them, agrees with most of them and does what he likes.",
    "LYU": "Nobody in Lyulin uses his real name. To the ten housing estates beneath the mountain he is simply "
           "GrimBoss, and that is all anyone needs to know.\\n\\nHe rules the most populous district in Sofia from a "
           "flat on the top floor of a panel block, and when he looks east he sees the whole city lined up in front "
           "of him.",
    "VAZ": "The leader of Vazrazhdane grew up between the stalls of the Women's Market and the baths of Banya Bashi. "
           "The district is old, loud and full of traders, and its leader knows the price of everything, including "
           "loyalty.",
    "KRS": "Krasno Selo's leader governs the Hippodrome, Borovo and Lagera: tidy blocks, wide streets and residents "
           "who expect the trams to run on time whatever is happening to the rest of the city.",
    "SRK": "Serdika holds the Central Railway Station, and with it every train in and out of Sofia. Its leader is a "
           "former station master who believes, with some reason, that nothing in this war moves without his "
           "permission.",
    "POD": "Poduyane is railway yards, workshops and the long streets of Hadzhi Dimitar. Its leader is a union man "
           "who has spent his life arguing with managers and now finds himself in charge of an army.",
    "SLA": "The leader of Slatina governs Geo Milev, Reduta and the road to the airport. He has the only district in "
           "Sofia with planes nearby, and he reminds his neighbours of it at every opportunity.",
    "IZG": "Izgrev is the quarter of embassies and the villas of the old elite around Iztok. Its leader is a former "
           "diplomat who speaks five languages and has not yet found one in which the other warlords will listen.",
    "ILN": "Ilinden grew up around the old sugar factory, and its leader still runs the district like a factory "
           "floor: shifts, quotas and a whistle at six in the morning.",
    "NAD": "Nadezhda means hope, and its leader has built a career on promising it. The housing estates of the north "
           "are full of people who have heard such promises before.",
    "ISK": "Iskar's leader rules Druzhba and the banks of the river that gives the district its name. The Iskar "
           "has flooded the city before; its leader intends to do the same.",
    "STU": "Studentski is the city of the students, the Technical University and a hundred dormitories. Its "
           "leader was a lecturer until last month, and is now trying to turn a district of debating clubs into an "
           "army.",
    "KRE": "Kremikovtsi is the steelworks and the villages around them. Its leader is a former foreman who knows "
           "that every other warlord in Sofia will want his furnaces, and he means to charge them dearly.",
    "OVK": "Ovcha Kupel's leader rules the western estates and the mineral springs of Gorna Banya. A quiet district "
           "with a long memory, and a leader who would like it to stay quiet.",
    "VRB": "Vrabnitsa is Obelya, Moderno Predgradie and the villages on the northern edge of the city. Its leader "
           "is a practical man who will join whichever side is winning, as soon as he is sure which one that is.",
    "NIS": "Novi Iskar is a small town in the mouth of the Iskar gorge, a long way from the centre and happy to "
           "stay that way. Its mayor became its leader without anyone quite deciding he should.",
    "PNC": "Pancharevo is the lake, the rowing canal and a dozen villages climbing into the mountains. Its leader "
           "rules more land than half the districts of Sofia put together, and fewer people than any one of them.",
    "BNK": "Bankya is a spa town of mineral baths and sanatoriums on the far western edge of the city. Its leader "
           "has spent the war so far taking the waters and hoping nobody remembers Bankya exists.",
}

# Starting advisors: (slot, trait). Each country gets three, picked from these by district.
ADVISOR_TRAITS = {
    # key: (name, description, modifiers, slot)
    "evil_sofia_market_boss": ("Market Boss", "Knows every trader in the district, and what each of them owes.",
                               "production_speed_industrial_complex_factor = 0.10", "political_advisor"),
    "evil_sofia_garage_gunsmith": ("Garage Gunsmith", "Every garage can make rifles, if somebody shows it how.",
                                   "production_speed_arms_factory_factor = 0.10", "political_advisor"),
    "evil_sofia_block_organiser": ("Block Organiser", "A warden on every staircase, a meeting in every courtyard.",
                                   "stability_factor = 0.05\npolitical_power_factor = 0.05", "political_advisor"),
    "evil_sofia_loudspeaker": ("Voice of the District", "Loudspeakers on every lamp post, and his voice on all of them.",
                               "war_support_factor = 0.05\npolitical_power_factor = 0.05", "political_advisor"),
    "evil_sofia_municipal_engineer": ("Municipal Engineer", "Built half the district's roads and knows how to block "
                                      "all of them.",
                                      "production_speed_bunker_factor = 0.25\nproduction_speed_infrastructure_factor = 0.15",
                                      "political_advisor"),
    "evil_sofia_tax_collector": ("Tax Collector", "Nobody likes him. Everybody pays him.",
                                 "consumer_goods_factor = -0.03", "political_advisor"),
    "evil_sofia_professor": ("University Professor", "Thirty years of lectures, finally put to some use.",
                             "research_speed_factor = 0.03", "political_advisor"),
    "evil_sofia_recruiter": ("Neighbourhood Recruiter", "Knows which sons are home and which are hiding.",
                             "conscription_factor = 0.08", "political_advisor"),
    "evil_sofia_street_fighter": ("Street Fighter", "Learned war in the courtyards, and never forgot it.",
                                  "army_attack_factor = 0.05", "army_chief"),
    "evil_sofia_block_defender": ("Defender of the Blocks", "Every panel block is a fortress if you hold the stairs.",
                                  "army_defence_factor = 0.05", "army_chief"),
    "evil_sofia_drillmaster": ("Drillmaster", "Turns bus drivers into soldiers in half the time.",
                               "training_time_factor = -0.10", "army_chief"),
    "evil_sofia_quartermaster": ("Quartermaster", "There is always another crate in the basement.",
                                 "supply_consumption_factor = -0.05", "army_chief"),
    "evil_sofia_morale_officer": ("Morale Officer", "Songs, speeches and a hot meal before every attack.",
                                  "army_morale_factor = 0.05", "army_chief"),
}
# Per district: (economic advisor, political advisor, army chief)
ADVISORS = {
    "SRD": ("evil_sofia_market_boss", "evil_sofia_loudspeaker", "evil_sofia_block_defender"),
    "VAZ": ("evil_sofia_market_boss", "evil_sofia_tax_collector", "evil_sofia_quartermaster"),
    "OBR": ("evil_sofia_professor", "evil_sofia_block_organiser", "evil_sofia_morale_officer"),
    "KRS": ("evil_sofia_municipal_engineer", "evil_sofia_block_organiser", "evil_sofia_drillmaster"),
    "SRK": ("evil_sofia_municipal_engineer", "evil_sofia_tax_collector", "evil_sofia_quartermaster"),
    "POD": ("evil_sofia_garage_gunsmith", "evil_sofia_recruiter", "evil_sofia_street_fighter"),
    "SLA": ("evil_sofia_garage_gunsmith", "evil_sofia_loudspeaker", "evil_sofia_drillmaster"),
    "IZG": ("evil_sofia_professor", "evil_sofia_tax_collector", "evil_sofia_block_defender"),
    "LOZ": ("evil_sofia_market_boss", "evil_sofia_block_organiser", "evil_sofia_block_defender"),
    "TRD": ("evil_sofia_professor", "evil_sofia_loudspeaker", "evil_sofia_morale_officer"),
    "KRP": ("evil_sofia_garage_gunsmith", "evil_sofia_recruiter", "evil_sofia_street_fighter"),
    "ILN": ("evil_sofia_garage_gunsmith", "evil_sofia_block_organiser", "evil_sofia_quartermaster"),
    "NAD": ("evil_sofia_municipal_engineer", "evil_sofia_recruiter", "evil_sofia_block_defender"),
    "ISK": ("evil_sofia_market_boss", "evil_sofia_recruiter", "evil_sofia_drillmaster"),
    "MLA": ("evil_sofia_market_boss", "evil_sofia_recruiter", "evil_sofia_drillmaster"),
    "STU": ("evil_sofia_professor", "evil_sofia_loudspeaker", "evil_sofia_street_fighter"),
    "LYU": ("evil_sofia_garage_gunsmith", "evil_sofia_recruiter", "evil_sofia_street_fighter"),
    "KRE": ("evil_sofia_garage_gunsmith", "evil_sofia_tax_collector", "evil_sofia_quartermaster"),
    "VIT": ("evil_sofia_market_boss", "evil_sofia_loudspeaker", "evil_sofia_block_defender"),
    "OVK": ("evil_sofia_municipal_engineer", "evil_sofia_block_organiser", "evil_sofia_morale_officer"),
    "VRB": ("evil_sofia_municipal_engineer", "evil_sofia_recruiter", "evil_sofia_drillmaster"),
    "NIS": ("evil_sofia_garage_gunsmith", "evil_sofia_block_organiser", "evil_sofia_block_defender"),
    "PNC": ("evil_sofia_municipal_engineer", "evil_sofia_tax_collector", "evil_sofia_quartermaster"),
    "BNK": ("evil_sofia_tax_collector", "evil_sofia_block_organiser", "evil_sofia_morale_officer"),
}

# Characters that only take a role through focuses: tag: [(id, name, description)]; a portrait is used when
# tools/portraits/<id>.png exists.
EXTRA_CHARACTERS = {
    "SRD": [("SRD_ilchev", "Konstantin Ilchev",
             "Konstantin Ilchev taught physics to half the leaders of Sofia, Victor Kolev included, and remembers "
             "every one of their exam papers. He has watched his former students carve the city into twenty-four "
             "warring districts with growing irritation.\\n\\nHe believes in three things: the laws of physics, "
             "homework handed in on time, and the idea that a city can be run like a well-ordered laboratory. "
             "Sredets is about to become his experiment.")],
}
