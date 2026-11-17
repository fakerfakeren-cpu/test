"""Sredets focus tree: the design, before it is built.

One entry per focus: (id, name, x, y, prerequisites, mutually exclusive, weeks, icon, effect).
- prerequisites: a list of groups; every group must be met, and a group is met by any one focus in it.
- icon: "duo:<name>" is a finished icon from the DuoDex hoi4GFX pack, "person:<TAG>:<thing>" a black-and-white
  portrait of that country's leader with <thing> behind it (to be made), "custom:<idea>" an icon to be put together
  from the Ultimate HOI4 GFX frames and pieces.
"""

BRANCHES = {  # name, first and last column
    "politics": ("Politics", 0, 12),
    "economy": ("The Heart of Sofia", 14, 18),
    "military": ("Guardians of the Centre", 20, 24),
}

FOCUSES = [
    # ------------------------------------------------------------------ politics: the first choice
    ("power_to_the_people", "Power to the People", 3, 0, [], ["order_in_the_centre"], 10,
     "duo:Focus_Guy_Raising_Hand_Propaganda",
     "+75 political power; +10% democratic and +10% communist popularity. Opens the Democracy and Communism paths."),
    ("order_in_the_centre", "Order in the Centre", 10, 0, [], ["power_to_the_people"], 10, "duo:goal_authority",
     "+75 political power; +5% stability; +5% war support. Opens the Authoritarian and Fascist paths."),
    ("free_elections", "Free Elections in Sredets", 1, 1, [["power_to_the_people"]], ["the_red_centre"], 10,
     "duo:goal_generic_elections",
     "Sredets becomes a democracy (elections every 4 years); Victor Kolev leads as a democrat; +10% stability."),
    ("the_red_centre", "The Red Centre", 5, 1, [["power_to_the_people"]], ["free_elections"], 10,
     "duo:goal_red_star_gold_wreath",
     "Sredets becomes communist; Victor Kolev leads as a communist; +10% war support."),
    ("the_iron_hand", "The Iron Hand", 9, 1, [["order_in_the_centre"]], ["the_black_centre"], 10,
     "duo:goal_authoritarian",
     "Sredets stays non-aligned under Victor Kolev; +15% stability; +100 political power."),
    ("the_black_centre", "The Black Centre", 12, 1, [["order_in_the_centre"]], ["the_iron_hand"], 10,
     "duo:Generic_Ultranationalist_Government",
     "Sredets becomes fascist; Victor Kolev leads as a fascist. (The rest of this path comes later.)"),
    # ------------------------------------------------------------------ democracy: the Evil Gang
    ("beacon_for_sofia", "A Beacon for Sofia", 0, 2, [["free_elections"]], [], 10, "duo:Generic_Blue_Democracy",
     "+10% democratic popularity in Oborishte, Lozenets, Triaditsa, Krasna Polyana, Mladost and Vitosha; "
     "+5% stability at home."),
    ("ballot_box_campaign", "The Ballot Box Campaign", 0, 3, [["beacon_for_sofia"]], [], 10,
     "duo:Generic_Parliament_Box",
     "A further +15% democratic popularity in those six; unlocks the decision 'Fund the Democrats of ...' "
     "for each of them."),
    ("found_the_evil_gang", "Found the Evil Gang", 2, 2, [["free_elections"]], [], 10,
     "duo:goal_generic_major_alliance", "Sredets founds the faction 'Evil Gang' and leads it."),
    ("invite_democratic_districts", "Invite the Democratic Districts", 2, 3, [["found_the_evil_gang"]], [], 5,
     "duo:goal_generic_join_faction",
     "Every democratic country among Oborishte, Lozenets, Triaditsa, Krasna Polyana, Mladost and Vitosha joins "
     "the Evil Gang. A decision invites the others the moment they turn democratic. Lyulin is never invited."),
    ("evil_gang_war_council", "Evil Gang War Council", 1, 4, [["ballot_box_campaign"], ["invite_democratic_districts"]],
     [], 10, "duo:goal_generic_intelligence_exchange",
     "The Evil Gang shares research (a technology-sharing group); +10 army experience."),
    ("sofia_must_be_one", "Sofia Must Be One", 1, 5, [["evil_gang_war_council"]], [], 10,
     "duo:goal_generic_demand_territory",
     "War goals against every neighbour that is not in the Evil Gang; +10% war support."),
    ("sofia_reunited", "Sofia Reunited", 1, 6, [["sofia_must_be_one"]], [], 10, "duo:BUL_star",
     "Available when the Evil Gang owns all of Sofia. Sredets becomes the Republic of Sofia (the Sofia flag). "
     "OPEN QUESTION: are the other members absorbed, or do they stay as partners?"),
    # ------------------------------------------------------------------ communism: Sofia under one rule
    ("comrades_in_oborishte", "Comrades in Oborishte", 4, 2, [["the_red_centre"]], [], 10,
     "duo:Generic_Communist_Propaganda",
     "+20% communist popularity in Oborishte. Anton Zafirov can lead Oborishte as a communist."),
    ("ally_anton", "Ally Anton Zafirov", 3, 3, [["comrades_in_oborishte"]], ["anton_must_go"], 10,
     "person:OBR:handshake",
     "Available if Oborishte is communist or 40%+ communist. Anton is offered an alliance: if he accepts, "
     "Oborishte turns communist and joins Sredets' faction; if he refuses, Sredets gets a war goal on him."),
    ("anton_must_go", "Anton Must Go", 5, 3, [["comrades_in_oborishte"]], ["ally_anton"], 10, "person:OBR:sword",
     "War goal on Oborishte; +10% war support."),
    ("north_south_pact", "The North-South Pact", 3, 4, [["ally_anton"]], [], 10, "duo:GAL_goal_divide_nation",
     "Sofia is split: the centre and the south go to Sredets, the north to Oborishte. Each gets claims on its half "
     "(north: Serdika's outskirts, Poduyane, Nadezhda, Vrabnitsa, Novi Iskar, Kremikovtsi, Ilinden, Krasna Polyana, "
     "Lyulin, Bankya; south: Lozenets, Triaditsa, Izgrev, Slatina, Iskar, Mladost, Studentski, Vitosha, "
     "Krasno Selo, Ovcha Kupel, Pancharevo)."),
    ("destroy_anton", "Destroy Anton Zafirov", 5, 4, [["anton_must_go"]], [], 5, "person:OBR:crossed_swords",
     "Available when Sredets holds Oborishte's capital. Cores on Oborishte's states; +150 political power; "
     "+10% stability."),
    ("dirty_communists", "'Dirty Communists', She Says", 7, 2, [["the_red_centre"]], [], 10,
     "duo:Communist_Discourse",
     "Daniel-Henry's mum keeps calling the people of the centre dirty communists. We wear it with pride: "
     "+10% war support; +10% communist popularity."),
    ("red_leaflets", "Red Leaflets over Vitosha", 7, 3, [["dirty_communists"]], [], 10,
     "duo:Generic_Socialist_Propaganda", "Vitosha: -10% stability, +15% communist popularity."),
    ("capel_question", "The Capel Question", 7, 4, [["red_leaflets"]], [], 10, "person:VIT:sword",
     "War goal on Vitosha (Daniel-Henry Capel)."),
    ("prove_her_right", "Prove Her Right", 7, 5, [["capel_question"]], [], 10, "duo:goal_red_star_green_wreath",
     "Available when Sredets holds Vitosha's capital. Cores on Vitosha's states; +100 political power; "
     "+10% stability."),
    ("conquer_the_centre", "Conquer the Centre", 4, 5, [["north_south_pact", "destroy_anton"]], [], 10,
     "duo:Generic_Urban_Warfare", "War goals on Vazrazhdane and Serdika."),
    ("one_sofia_one_party", "One Sofia, One Party", 5, 6, [["conquer_the_centre"], ["prove_her_right"]], [], 10,
     "duo:goal_commune_politics",
     "Claims on every state of Sofia outside Sredets' faction (only Sredets' half if the Pact holds); "
     "+20% war support."),
    # ------------------------------------------------------------------ authoritarian: the Centre
    ("march_on_the_old_town", "March on the Old Town", 9, 2, [["the_iron_hand"]], [], 10, "duo:goal_ITA_urban",
     "War goals on Oborishte and Vazrazhdane."),
    ("take_the_central_station", "Take the Central Station", 9, 3, [["march_on_the_old_town"]], [], 10,
     "duo:Generic_Train", "War goal on Serdika."),
    ("proclaim_the_centre", "Proclaim the Centre", 9, 4, [["take_the_central_station"]], [], 10,
     "duo:BUL_bulgarian_government",
     "Available when Sredets owns Sredets, Yavorov, Oborishte, Poduyane (Oborishte), Vazrazhdane, Zhenski Pazar, "
     "Serdika and North City Centre. Sredets becomes 'The Centre' (new name and flag) with cores on all eight; "
     "+15% stability."),
    ("greater_centre", "The Greater Centre", 8, 5, [["proclaim_the_centre"]], [], 10, "duo:Generic_Redraw_Borders",
     "Claims on the half-central states: North Lozenets, Triaditsa, Kriva Reka, Reduta, West Hadzhi Dimitar, Ilinden."),
    ("evil_gang_of_the_centre", "The Evil Gang", 10, 5, [["proclaim_the_centre"]], [], 10,
     "duo:goal_generic_alliance",
     "The Centre founds the Evil Gang and invites Lozenets, Triaditsa, Krasna Polyana, Mladost and Vitosha, "
     "whatever their politics. Lyulin is never invited."),
    ("sofia_under_the_centre", "Sofia Under the Centre", 9, 6, [["greater_centre"], ["evil_gang_of_the_centre"]], [],
     10, "duo:goal_generic_forceful_treaty",
     "War goals against every neighbour outside the Evil Gang; +10% war support."),
    # ------------------------------------------------------------------ economy: The Heart of Sofia
    ("heart_of_sofia", "The Heart of Sofia", 16, 0, [], [], 10, "duo:Generic_Major_City",
     "+1 civilian factory. National spirit 'The Heart of Sofia': +5% political power gain "
     "(the focuses below make it stronger)."),
    ("vitosha_boulevard", "Vitosha Boulevard Shops", 15, 1, [["heart_of_sofia"]], [], 10, "duo:Market Liberal",
     "+2 civilian factories."),
    ("restaurant_every_corner", "A Restaurant on Every Corner", 17, 1, [["heart_of_sofia"]], [], 10,
     "duo:Focus_Cake_and_Coffee", "+10% stability; The Heart of Sofia: +5% stability."),
    ("tourists_everywhere", "Tourists Everywhere", 15, 2, [["vitosha_boulevard"]], [], 10,
     "duo:LEC_Passports", "+1 civilian factory; +100 political power; The Heart of Sofia: +10% political power gain."),
    ("mimas_doner", "Mimas Döner Never Closes", 17, 2, [["restaurant_every_corner"]], [], 10, "custom:doner",
     "The Heart of Sofia: +5% war support (nobody fights hungry)."),
    ("shishman_street", "The Bars of Shishman Street", 18, 3, [["restaurant_every_corner"]], [], 5, "duo:goal_GEO_wine",
     "+5% stability; +5% war support."),
    ("live_in_the_centre", "Everyone Wants to Live in the Centre", 16, 3, [["tourists_everywhere", "mimas_doner"]], [],
     10, "duo:goal_generic_build_housing", "The Heart of Sofia: +20% monthly population, +1% recruitable population."),
    ("rent_is_due", "Rent Is Due", 15, 4, [["live_in_the_centre"]], [], 10, "duo:goal_bag_of_money",
     "+2 civilian factories."),
    ("the_largo", "The Largo", 17, 4, [["live_in_the_centre"]], [], 10, "duo:Generic_Revolutionary_Government",
     "The Heart of Sofia: +10% political power gain."),
    ("metro_hub", "The Metro Hub", 15, 5, [["rent_is_due"]], [], 10, "duo:Generic_Railroads",
     "+1 infrastructure in every state; +10% construction speed for infrastructure."),
    ("council_of_ministers", "Council of Ministers", 17, 5, [["the_largo"]], [], 10, "duo:goal_double_research",
     "+1 research slot."),
    ("centre_never_sleeps", "The Centre Never Sleeps", 16, 6, [["metro_hub"], ["council_of_ministers"]], [], 10,
     "duo:goal_factory_complex", "+1 research slot; 2 research bonuses of 50% for industry."),
    # ------------------------------------------------------------------ military: Guardians of the Centre
    ("guardians_of_the_centre", "Guardians of the Centre", 22, 0, [], [], 10, "duo:goal_army_guy",
     "+10 army experience. National spirit 'Guardians of the Centre': +5% war support (the focuses below make "
     "it stronger)."),
    ("vasil_levski_muster", "Muster at Vasil Levski Stadium", 21, 1, [["guardians_of_the_centre"]], [], 10,
     "custom:stadium", "4 new City Guard divisions appear at the stadium; +5% war support."),
    ("arsenal_of_the_centre", "Arsenal of the Centre", 23, 1, [["guardians_of_the_centre"]], [], 10,
     "duo:goal_generic_construct_mil_factory", "+2 military factories."),
    ("stadium_drill", "Stadium Drill Grounds", 20, 2, [["vasil_levski_muster"]], [], 10,
     "duo:goal_generic_army_training", "Guardians of the Centre: -20% division training time; 50% land doctrine bonus."),
    ("mimas_field_kitchens", "Mimas Field Kitchens", 22, 2, [["vasil_levski_muster", "arsenal_of_the_centre"]], [],
     10, "duo:PAL_Food_Import", "Guardians of the Centre: -15% supply consumption, +5% recovery rate."),
    ("guns_from_the_back_rooms", "Guns from the Back Rooms", 24, 2, [["arsenal_of_the_centre"]], [], 10,
     "duo:goal_arms_export", "+2000 infantry equipment; 50% infantry weapons research bonus."),
    ("guard_of_honour", "Guard of Honour", 20, 3, [["stadium_drill"]], [], 10, "duo:BUL_bulgarian_officer",
     "+10 army experience; 100% special forces research bonus."),
    ("barricades_on_vitosha", "Barricades on Vitosha Boulevard", 23, 3, [["guns_from_the_back_rooms"]], [], 10,
     "duo:Generic_Barricade", "Level 3 bunkers along every border of Sredets' capital state."),
    ("rooftop_snipers", "Rooftop Snipers", 20, 4, [["guard_of_honour"]], [], 10, "duo:Generic_Sniper_Assassin",
     "Guardians of the Centre: +5% division defence."),
    ("metro_tunnels", "The Metro Tunnels", 22, 4, [["mimas_field_kitchens"], ["barricades_on_vitosha"]], [], 10,
     "duo:goal_nested_fortifications", "Guardians of the Centre: +5% division defence, +5% recovery rate."),
    ("centre_air_defence", "Air Defence over the Centre", 24, 4, [["barricades_on_vitosha"]], [], 10,
     "duo:goal_anti_air", "+2 anti-air and a radar station in every state of Sredets."),
    ("tourists_with_rifles", "Tourists with Rifles", 21, 5, [["rooftop_snipers", "metro_tunnels"]], [], 10,
     "duo:Generic_Urban_Partisans", "Guardians of the Centre: +2% recruitable population."),
    ("fortress_centre", "The Fortress Centre", 22, 6, [["tourists_with_rifles"], ["centre_air_defence"]], [], 10,
     "duo:goal_generic_fortify_city",
     "Guardians of the Centre: +10% division defence; level 2 bunkers in every state of Sredets."),
]

ALSO = [
    "All eight custom leaders get a leader role for every ideology, so Victor Kolev, Anton Zafirov and the others "
    "stay in charge whichever way their country goes.",
    "'The Centre' needs a name and a flag (open question).",
    "Evil Gang members in the democratic path must be democratic; in the authoritarian path anyone except Lyulin.",
    "The fascist path is only its first focus for now.",
]
