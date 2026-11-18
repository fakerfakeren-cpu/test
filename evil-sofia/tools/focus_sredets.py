"""Sredets focus tree: the communist path, and the first focus of the authoritarian path.

Each focus: id, name, x, y, prerequisites (groups: all groups needed, any focus within a group), mutually
exclusive, weeks, icon, available (script or ""), reward (script), description.
Placeholders filled in by the build (tools/build_focus.py):
  {OBR_CAP} {VIT_CAP}   capital state ids
  {CLAIMS:A,B}          add_state_claim on every state the countries A, B own at the start
  {WAR:A,B}             war goals on A and B (if they still exist)
  {COREHELD:T:A,B}      T gets a core on every state of A, B (as at the start) that T controls
  {HELD:A,B}            trigger: every state of A, B (as at the start) is controlled by us or a faction member
Cores only come once a group of districts is held: each stage claims the next group and gives war goals on it,
and the stage after it (or the final focus) gives the cores on what was taken.
Icons: "duo:<name>" finished pack icon, "person:<key>" leader portrait icon (tools/focus_icons.py),
"custom:<key>" put together from pack frames and pieces.
"""

TAG = "SRD"
# The district groups of Sofia (the map of district types): conquered one group after the other.
CENTRE = ["VAZ"]                                                    # with Oborishte in the alone path
OLD_QUARTERS = ["KRS", "SRK", "POD", "SLA", "IZG", "LOZ", "TRD", "KRP", "ILN"]  # early to mid 20th century
HOUSING = ["NAD", "ISK", "MLA", "STU", "LYU"]                                   # socialist housing districts
INDUSTRY = ["KRE"]
OUTSKIRTS = ["VIT", "OVK", "VRB", "NIS", "PNC", "BNK"]                          # peripheral districts
NORTH = ["SRK", "POD", "NAD", "VRB", "NIS", "KRE", "ILN", "KRP", "LYU", "BNK"]   # Oborishte's half in the pact


def half(group, north):
    return ",".join(t for t in group if (t in NORTH) == north)


def pact_stage(group, prev, sredets_extra=""):
    """Sredets takes the south half of a group, Oborishte the north half; cores on the previous group."""
    south, north = half(group, False), half(group, True)
    lines = []
    if prev:
        ps, pn = half(prev, False), half(prev, True)
        lines += [f"{{COREHELD:SRD:{ps}}}"] if ps else []
        lines += [f"{{COREHELD:OBR:{pn}}}"] if pn else []
    if south:
        lines += [f"{{CLAIMS:{south}}}", f"{{WAR:{south}}}"]
    if north:
        lines += ["OBR = {", f"\t{{CLAIMS:{north}}}", f"\t{{WAR:{north}}}", "}"]
    return "\n".join(lines + ([sredets_extra] if sredets_extra else [])), (f"{{HELD:{','.join(prev)}}}" if prev else "")


def alone_stage(group, prev, extra=""):
    lines = ([f"{{COREHELD:SRD:{','.join(prev)}}}"] if prev else []) + [
        f"{{CLAIMS:{','.join(group)}}}", f"{{WAR:{','.join(group)}}}"] + ([extra] if extra else [])
    return "\n".join(lines), (f"{{HELD:{','.join(prev)}}}" if prev else "")


P1, P1a = pact_stage(CENTRE, [])
P2, P2a = pact_stage(OLD_QUARTERS, CENTRE)
P3, P3a = pact_stage(HOUSING, OLD_QUARTERS)
P4, P4a = pact_stage(INDUSTRY, HOUSING, "add_political_power = 100")
P5, P5a = pact_stage(OUTSKIRTS, INDUSTRY)
A1, A1a = alone_stage(CENTRE, [])
A2, A2a = alone_stage(OLD_QUARTERS, CENTRE + ["OBR"])
A3, A3a = alone_stage(HOUSING, OLD_QUARTERS)
A4, A4a = alone_stage(INDUSTRY, HOUSING, "add_political_power = 100")
A5, A5a = alone_stage(OUTSKIRTS, INDUSTRY)
EVERYTHING = CENTRE + OLD_QUARTERS + HOUSING + INDUSTRY + OUTSKIRTS
PACT_END = (f"{{COREHELD:SRD:{half(EVERYTHING, False)}}}\n{{COREHELD:OBR:{half(EVERYTHING, True)}}}", f"{{HELD:{','.join(OUTSKIRTS)}}}")
ALONE_END = (f"{{COREHELD:SRD:{','.join(EVERYTHING + ['OBR'])}}}", f"{{HELD:{','.join(OUTSKIRTS)}}}")

FOCUSES = [
    ("henrys_mom_was_right", "Henry's Mom Was Right", 8, 0, [], ["order_in_the_centre"], 5,
     "duo:Communist_Discourse", "",
     """set_popularities = { communism = 65 neutrality = 35 democratic = 0 fascism = 0 }
set_politics = { ruling_party = communism elections_allowed = no }
add_country_leader_role = {
	character = SRD_leader
	country_leader = { ideology = leninism expire = "1965.1.1.1" }
	promote_leader = yes
}
set_cosmetic_tag = SRD_RED
add_war_support = 0.10
VIT = { country_event = { id = evil_sofia_srd.1 } }
news_event = { id = evil_sofia_news.1 hours = 6 }""",
     "For years Daniel-Henry Capel's mother has stood at her window in Boyana and told anyone who would listen that "
     "the people of the centre are communists, every last one of them. Tonight Victor Kolev climbs onto the steps of "
     "the Party House, looks out over a Largo full of red flags, and decides that she was right.\\n\\nSredets becomes "
     "the Sredets Commune. Somewhere up the slopes of Vitosha, Henry is already furious."),
    ("order_in_the_centre", "Order in the Centre", 24, 0, [], ["henrys_mom_was_right"], 5,
     "duo:goal_authoritarian", "",
     "add_stability = 0.15\nadd_political_power = 100\nnews_event = { id = evil_sofia_news.2 hours = 6 }",
     "The council is gone and the city is a mess of checkpoints and rival flags. Sredets will not join the "
     "shouting. No parties, no slogans, no committees: Victor Kolev governs the centre himself, and the trams "
     "will run on time.\\n\\nOpens the four roads of order: Sredets alone, the Evil Gang, the C Class Hools, or "
     "Konstantin Ilchev."),
    # ------------------------------------------------------------------ Oborishte and Anton Zafirov
    ("comrades_in_oborishte", "Comrades in Oborishte", 2, 1, [["henrys_mom_was_right"]], [], 5,
     "duo:Generic_Communist_Propaganda", "",
     "OBR = { add_popularity = { ideology = communism popularity = 0.15 } }\nadd_political_power = 50",
     "Oborishte begins three streets east of the Party House, under the domes of Alexander Nevsky. Its cafés are "
     "full of students, its students are full of ideas, and Anton Zafirov has not yet decided which side he is on. "
     "Our people will help him decide.\\n\\nUnlocks the decisions of the Oborishte Question."),
    ("red_newspapers_oborishte", "Red Newspapers in Oborishte", 2, 2, [["comrades_in_oborishte"]], [], 4,
     "duo:Generic_Communist_Propaganda02", "",
     "OBR = { add_popularity = { ideology = communism popularity = 0.10 } add_stability = -0.05 }",
     "By morning every kiosk from Oborishte Street to the Doctors' Garden is selling the same paper, and it is "
     "printed in Sredets. Anton's police tear the posters down; by evening there are twice as many.\\n\\nUnlocks the "
     "decision Red Coup in Oborishte."),
    ("ally_anton", "Ally Anton Zafirov", 1, 3, [["red_newspapers_oborishte"]], ["anton_must_go"], 7,
     "person:ally_anton", "OBR = { exists = yes OR = { has_government = communism communism > 0.4 } }",
     "OBR = { country_event = { id = evil_sofia_srd.2 } }",
     "Anton is not our enemy. He is a man standing on the wrong side of a very short street. Victor will walk "
     "across it himself and offer him what nobody else in Sofia can: half of everything.\\n\\nNeeds Oborishte at "
     "least 40% communist. Anton is more likely to accept the more communist Oborishte is and the better he thinks "
     "of Sredets."),
    ("anton_must_go", "Anton Must Go", 3, 3, [["red_newspapers_oborishte"]], ["ally_anton"], 6,
     "person:anton_must_go", "OBR = { exists = yes }",
     "create_wargoal = { type = annex_everything target = OBR }\nadd_war_support = 0.10",
     "There is no room for two masters in the centre of Sofia. Anton Zafirov has had his chance to stand with the "
     "revolution, and he has spent it drinking coffee under the cathedral. The Red Guards are ready."),
    ("north_south_pact", "The North-South Pact", 0, 4, [["ally_anton"]], [], 6,
     "duo:GAL_goal_divide_nation", "has_country_flag = SRD_anton_allied",
     "add_political_power = 100\nOBR = { add_political_power = 100 }\nnews_event = { id = evil_sofia_news.3 hours = 6 }",
     "A map of Sofia is spread across a table in the Party House. Victor takes a red pencil and draws a line from "
     "Lyulin to Kremikovtsi: the north for Oborishte, the centre and the south for Sredets. Anton signs first. "
     "Neither of them mentions what happens after the last district falls."),
    ("destroy_anton", "Destroy Anton Zafirov", 4, 4, [["ally_anton", "anton_must_go"]], [], 5,
     "person:destroy_anton", "{HELD:OBR}\nNOT = { has_country_flag = SRD_anton_allied }",
     "{COREHELD:SRD:OBR}\nadd_political_power = 150\nadd_stability = 0.10\nnews_event = { id = evil_sofia_news.4 hours = 6 }",
     "The bells of Alexander Nevsky are silent and the red flag hangs from the Holy Synod. Every street of "
     "Oborishte is in our hands; Anton Zafirov's career is over, and his district is ours to keep.\\n\\nNeeds every "
     "state of Oborishte under our control."),
    # the pact: Sofia split between Sredets (south) and Oborishte (north), one group of districts at a time
    ("pact_centre", "The Red Centre", 0, 5, [["north_south_pact"]], [], 8, "duo:Generic_Redraw_Borders", P1a, P1,
     "The pact begins where the city began: Vazrazhdane, the old market streets around the Women's Market and Lion's "
     "Bridge. Whoever holds them holds the roads in and out of the centre.\\n\\nClaims and war goals on Vazrazhdane. "
     "Its cores come with the next stage, once it is held."),
    ("pact_old_quarters", "The Old Quarters", 0, 6, [["pact_centre"]], [], 10, "duo:SIA_Urban_Warfare_NF", P2a, P2,
     "The boulevards and villas built between the wars, where Sofia's middle class still lives behind lace "
     "curtains. Krasno Selo, Slatina, Izgrev, Lozenets and Triaditsa for us; Serdika, Poduyane, Krasna Polyana and "
     "Ilinden for Anton.\\n\\nCores on the centre. Claims and war goals on the old quarters. Needs every state of "
     "the centre held."),
    ("pact_housing_estates", "The Housing Estates", 0, 7, [["pact_old_quarters"]], [], 10,
     "duo:focus_collective_housing", P3a, P3,
     "Endless rows of panel blocks, ten floors high and a kilometre long. The estates were built for the workers; "
     "the workers will take them back. Iskar, Mladost and Studentski for us; Nadezhda and Lyulin for Oborishte."
     "\\n\\nCores on the old quarters. Claims and war goals on the housing estates. Needs every state of the old "
     "quarters held."),
    ("pact_kremikovtsi", "The Steelworks of Kremikovtsi", 0, 8, [["pact_housing_estates"]], [], 7,
     "duo:goal_factory_complex", P4a, P4,
     "Out past the airport, the chimneys of Kremikovtsi stand over the plain. The district goes to Oborishte; the "
     "steel goes to both of us, and nobody will ask what it is for.\\n\\nCores on the housing estates. War goals on "
     "Kremikovtsi. Needs every state of the housing estates held."),
    ("pact_outskirts", "The Outskirts", 0, 9, [["pact_kremikovtsi"]], [], 10,
     "duo:goal_generic_territory_or_war", P5a, P5,
     "Villages, orchards and the slopes of the mountains: the last of Sofia that is not red. Vitosha, Ovcha Kupel "
     "and Pancharevo for us; Vrabnitsa, Novi Iskar and Bankya for Anton.\\n\\nCores on Kremikovtsi. Claims and war "
     "goals on the outskirts. Needs every state of Kremikovtsi held."),
    ("sofia_union", "The Union of North and South Sofia", 1, 10, [["pact_outskirts"]], [], 6,
     "duo:goal_generic_major_alliance", PACT_END[1],
     PACT_END[0] + """
set_cosmetic_tag = SRD_SOUTH
OBR = { set_cosmetic_tag = OBR_NORTH }
dismantle_faction = yes
create_faction = EVIL_SOFIA_FACTION_SOFIA
add_to_faction = OBR
add_stability = 0.15
add_political_power = 200
news_event = { id = evil_sofia_news.7 hours = 6 }""",
     "From Boyana to Kremikovtsi the city is red. Victor and Anton meet on the Eagles' Bridge, exactly on the line "
     "they drew, and shake hands for the cameras. Sredets becomes South Sofia, Oborishte becomes North Sofia, and "
     "the alliance takes the only name big enough for it: Sofia.\\n\\nCores on everything each of us holds. Needs "
     "every state of the outskirts held."),
    # alone: Sofia under Sredets alone, one group of districts at a time
    ("one_centre", "One Centre", 4, 5, [["destroy_anton"]], [], 8, "duo:Generic_Major_City", A1a, A1,
     "With Oborishte gone, only Vazrazhdane stands between Sredets and a centre that answers to one man. Its market "
     "halls and tram depots will make a fine headquarters.\\n\\nClaims and war goals on Vazrazhdane."),
    ("united_old_quarters", "Take the Old Quarters", 4, 6, [["one_centre"]], [], 12, "duo:Generic_Urban_Warfare",
     A2a, A2,
     "Nine districts of boulevards, parks and pre-war villas, from Krasno Selo to Ilinden. Without allies this will "
     "be slow, street by street, but nothing we take will have to be shared.\\n\\nCores on the centre and "
     "Oborishte. Claims and war goals on the old quarters. Needs every state of the centre held."),
    ("united_housing_estates", "Take the Housing Estates", 4, 7, [["united_old_quarters"]], [], 12,
     "duo:goal_generic_build_housing", A3a, A3,
     "Nadezhda, Iskar, Mladost, Studentski and Lyulin: half of Sofia lives in these blocks, and half of our "
     "army will come from them.\\n\\nCores on the old quarters. Claims and war goals on the housing estates. Needs "
     "every state of the old quarters held."),
    ("united_kremikovtsi", "Take Kremikovtsi", 4, 8, [["united_housing_estates"]], [], 8, "duo:focus_generic_steel",
     A4a, A4,
     "The steelworks of Kremikovtsi are the only real industry this city has. Whoever holds them can arm every "
     "district they conquer.\\n\\nCores on the housing estates. War goals on Kremikovtsi. Needs every state of the "
     "housing estates held."),
    ("united_outskirts", "Take the Outskirts", 4, 9, [["united_kremikovtsi"]], [], 12,
     "duo:goal_generic_more_territorial_claims", A5a, A5,
     "Vitosha, Ovcha Kupel, Vrabnitsa, Novi Iskar, Pancharevo and Bankya. The villages on the edge of the city have "
     "always thought themselves safe from Sofia's politics. They were wrong.\\n\\nCores on Kremikovtsi. Claims and "
     "war goals on the outskirts. Needs every state of Kremikovtsi held."),
    ("sofia_commune", "The Sofia Commune", 3, 10, [["united_outskirts"]], [], 6, "duo:Generic_Hammer_Star",
     ALONE_END[1],
     ALONE_END[0] + "\nset_cosmetic_tag = SRD_SOFIA\nadd_stability = 0.20\nadd_political_power = 200"
     "\nnews_event = { id = evil_sofia_news.6 hours = 6 }",
     "Twenty-four districts, one flag. The Party House is no longer the seat of Sredets but of the whole city, and "
     "Victor Kolev speaks from its balcony to a Largo packed from wall to wall. Sredets is gone; there is only "
     "Sofia.\\n\\nCores on everything we hold. Needs every state of the outskirts held."),
    # the war at home, between both paths: manpower from the districts as they fall
    ("peoples_militia", "The People's Militia", 2, 6, [["pact_centre", "one_centre"]], [], 6,
     "duo:goal_integrate_the_militia", "",
     "add_ideas = SRD_militia_spirit\nadd_manpower = 15000",
     "Every block we take sends ten men to the district committee, and the committee gives them a red armband and "
     "a rifle. They will learn to shoot on the way to the front."),
    ("komsomol_of_the_estates", "Komsomol of the Housing Estates", 2, 8,
     [["peoples_militia"], ["pact_housing_estates", "united_housing_estates"]], [], 7,
     "duo:SWI_Workers_Army", "",
     "add_ideas = SRD_komsomol\nadd_war_support = 0.05",
     "The teenagers of the panel blocks have spent years hanging around bus stops with nothing to do. Now they "
     "have badges, marching songs, a youth hall in every estate, and a waiting list for the front."),
    # ------------------------------------------------------------------ the Party
    ("party_takes_the_largo", "The Party Takes the Largo", 7, 1, [["henrys_mom_was_right"]], [], 7,
     "duo:Generic_Revolutionary_Government", "",
     "add_political_power = 100\nadd_stability = 0.10",
     "The Largo was built to impress: three grand buildings around one square, with the Party House at its head. "
     "The ministries are emptied, the archives are sealed, and a red flag the size of a tram goes up over the "
     "government quarter."),
    ("red_guards_of_the_stadium", "Red Guards of Vasil Levski Stadium", 6, 2, [["party_takes_the_largo"]], [], 9,
     "custom:stadium", "",
     'load_oob = "SRD_red_guards"\nadd_war_support = 0.05',
     "The national stadium holds forty thousand people. On match days they come to shout; now they come to drill. "
     "Four divisions of Red Guards march out of the gates past Borisova Gradina."),
    ("arm_the_workers", "Arm the Workers", 6, 3, [["red_guards_of_the_stadium"]], [], 6,
     "duo:goal_integrate_workers_militia", "",
     """add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2000 }
add_tech_bonus = { name = SRD_arm_the_workers bonus = 0.5 uses = 1 category = infantry_weapons }""",
     "Waiters from the cafés on Rakovski Street, shop assistants from TZUM, conductors from the tram depots. Every "
     "worker of the centre gets a rifle, a cartridge belt and an address to report to."),
    ("barricades_on_vitosha", "Barricades on Vitosha Boulevard", 6, 4, [["arm_the_workers"]], [], 10,
     "duo:Generic_Barricade", "",
     """capital_scope = {
	add_building_construction = { type = bunker level = 3 province = { all_provinces = yes limit_to_border = yes } instant_build = yes }
}""",
     "Café tables, tram rails, paving stones and the shop windows of the most expensive street in the country. "
     "Vitosha Boulevard is turned into a fortress from the Palace of Justice to the National Palace of Culture."),
    ("red_officer_school", "The Red Officer School", 6, 6, [["metro_goes_to_war"]], [], 8,
     "duo:goal_officers", "",
     "army_experience = 25\nadd_tech_bonus = { name = SRD_red_officer_school bonus = 1.0 uses = 1 category = land_doctrine }",
     "The old Military Academy on Evlogi Georgiev Boulevard is given a new curriculum: street fighting, political "
     "education and the history of the Party. Its first graduates will lead our divisions."),
    ("tram_depot_tank_works", "The Tram Depot Tank Works", 8, 6, [["metro_goes_to_war"]], [], 10,
     "duo:focus_generic_tank_production", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = arms_factory level = 1 instant_build = yes }
}
add_tech_bonus = { name = SRD_tram_depot_tank_works bonus = 1.0 uses = 1 category = armor }""",
     "A tram is already a steel box on wheels. Add armour plate, swap the wheels for tracks and put a gun on top: "
     "the depot workers swear it will be the finest tank in the Balkans."),
    ("universal_service", "Every Comrade Serves", 8, 2, [["party_takes_the_largo"]], [], 5,
     "duo:goal_conscription", "",
     "add_ideas = SRD_universal_service_spirit\nadd_manpower = 25000",
     "From the Largo to the Lions' Bridge, every comrade between eighteen and sixty is given a rifle number and a "
     "unit to report to. Nobody in the centre will be able to say the revolution did not need them."),
    ("commissars_in_every_unit", "Commissars in Every Unit", 8, 3, [["universal_service"]], [], 8,
     "duo:Generic_Socialist_Soldier", "",
     "army_experience = 30\nadd_tech_bonus = { name = SRD_commissars_in_every_unit bonus = 1.0 uses = 1 category = land_doctrine }",
     "A Party man in every platoon: he reads the newspaper aloud, he writes the reports, and he makes sure that the "
     "Red Guards never forget what they are fighting for, or who they answer to."),
    ("red_air_over_the_centre", "Red Wings over the Centre", 8, 4, [["commissars_in_every_unit"]], [], 7,
     "duo:goal_air_red", "",
     """capital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }
air_experience = 25
add_tech_bonus = { name = SRD_red_air_over_the_centre bonus = 0.5 uses = 1 category = air_equipment }""",
     "Tsar Osvoboditel Boulevard is straight, wide and paved in yellow brick. With the lamp posts taken down it "
     "makes a perfectly good runway, and the Party's first squadron takes off over the Russian Church."),
    ("metro_goes_to_war", "The Shelters Beneath the Centre", 7, 5, [["barricades_on_vitosha"], ["red_air_over_the_centre"]], [], 9,
     "duo:goal_anti_air", "",
     """capital_scope = {
	add_building_construction = { type = anti_air_building level = 3 instant_build = yes }
	add_building_construction = { type = infrastructure level = 1 instant_build = yes }
}
add_stability = 0.05""",
     "Under the Largo lie the ruins of Roman Serdica, and under the ruins there is room for thousands. The cellars "
     "are linked into shelters and supply tunnels, and anti-aircraft guns go up on every rooftop around them."),
    # ------------------------------------------------------------------ Daniel-Henry Capel
    ("red_leaflets", "Red Leaflets over Vitosha", 10, 1, [["henrys_mom_was_right"]], [], 3,
     "duo:Generic_Socialist_Propaganda", "VIT = { exists = yes }",
     "VIT = { add_stability = -0.10 add_popularity = { ideology = communism popularity = 0.15 } }",
     "Henry's district is villas, pine forest and people who think the revolution is something that happens to "
     "other neighbourhoods. A few thousand leaflets in the letterboxes of Boyana should change that. One of them "
     "will land in his mother's."),
    ("road_to_boyana", "The Road to Boyana", 10, 2, [["red_leaflets"]], [], 5,
     "duo:focus_generic_diplomatic_treaty", "",
     """if = {
	limit = { OR = { NOT = { country_exists = LOZ } is_in_faction_with = LOZ } }
	set_country_flag = SRD_boyana_road_open
}
else = {
	LOZ = { country_event = { id = evil_sofia_srd.7 } }
}""",
     "Sredets does not touch Vitosha: Lozenets lies between us, and Lozenets belongs to Georgi Yanchovichin. Georgi "
     "and Victor go back further than any party or flag. They are day ones. Victor picks up the phone and asks him to "
     "stand with Sredets against Henry.\\n\\nGeorgi is more likely to say yes the better he thinks of Sredets. If "
     "Lozenets is already our ally or no longer exists, nobody needs to be asked."),
    ("capel_question", "The Capel Question", 10, 3, [["road_to_boyana"]], [], 8,
     "person:capel_question", "VIT = { exists = yes }",
     "create_wargoal = { type = annex_everything target = VIT }\nadd_war_support = 0.05",
     "Daniel-Henry Capel hates communism, hates Sredets and, above all, hates being proven wrong by his own mother. "
     "As long as he sits in Boyana, every red flag in Sofia has a rifle pointed at it from the mountain. It is "
     "time to answer the Capel Question."),
    ("red_flag_over_boyana", "Red Flag over Boyana", 10, 4, [["capel_question"]], [], 4,
     "duo:goal_red_star_green_wreath", "{HELD:VIT}",
     "{COREHELD:SRD:VIT}\nadd_political_power = 100\nadd_stability = 0.10\nnews_event = { id = evil_sofia_news.5 hours = 6 }",
     "The red flag flies over Boyana Church and the forest roads up to Dragalevtsi. Henry's villa has become a rest "
     "home for tired Red Guards. His mother has been heard telling the new tenants that she said this would "
     "happen.\\n\\nNeeds every state of Vitosha under our control."),
    # ------------------------------------------------------------------ the red economy of the centre
    ("collectivise_vitosha_boulevard", "Collectivise Vitosha Boulevard", 13, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Market_Socialism", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}""",
     "Gucci, Hugo Boss and a hundred smaller boutiques: the most expensive street in Bulgaria now belongs to the "
     "people. The tailors stay, the sewing machines stay, and the workshops behind the shop windows start working "
     "for the Party."),
    ("mimas_for_the_workers", "Mimas Döner for the Workers", 12, 2, [["collectivise_vitosha_boulevard"]], [], 4,
     "custom:doner", "", "add_ideas = SRD_mimas_doner",
     "Mimas on Graf Ignatiev has never closed, not for holidays, not for elections and not for revolutions. It "
     "is now the official canteen of the Sredets Commune, and the queue at four in the morning is the most "
     "united front in the city."),
    ("party_arsenal", "The Party Arsenal", 14, 2, [["collectivise_vitosha_boulevard"]], [], 12,
     "duo:goal_generic_construct_mil_factory", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = arms_factory level = 2 instant_build = yes }
}""",
     "Bakeries, print shops and car repair garages all over the centre are given new orders and new tools. The "
     "back rooms that used to smell of bread now smell of gun oil."),
    ("red_tourism", "Red Tourism", 12, 3, [["mimas_for_the_workers"]], [], 6, "duo:LEC_Passports", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}
add_political_power = 100""",
     "The tourists still come to photograph the cathedral and the yellow bricks. Now they buy their postcards from "
     "the Party, sleep in Party hotels and leave Party tips. Every lev goes into a new factory."),
    ("red_university", "The Red University", 14, 3, [["party_arsenal"]], [], 9,
     "duo:focus_generic_socialist_science", "",
     "add_tech_bonus = { name = SRD_red_university bonus = 0.75 uses = 2 category = electronics }",
     "Sofia University stands on Tsar Osvoboditel, two hundred metres from the Party House. Its physicists are "
     "moved into the laboratories of the Faculty of Physics and asked one question: how to build a better radio."),
    ("socialist_emulation", "Socialist Emulation", 15, 4, [["red_university"]], [], 7,
     "duo:goal_Workers_Paradise", "",
     "add_ideas = SRD_emulation_spirit",
     "Every factory in the commune now competes with every other. The winning shift gets its photograph in the "
     "newspaper, a red pennant on the wall and a free döner each. The losing shift gets the night shift."),
    ("five_year_plan", "Five-Year Plan for the Centre", 13, 4, [["red_tourism"], ["red_university"]], [], 12,
     "duo:Generic_Factory_Planning", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}
add_tech_bonus = { name = SRD_five_year_plan bonus = 0.5 uses = 2 category = industry }""",
     "Planners from the Party House count every factory, every tram and every pothole in the centre, then write "
     "a plan to double the first and fill the last. It will be completed in five years, or in four, if the "
     "workers love the Party enough."),
    ("star_on_the_party_house", "The Star on the Party House", 13, 5, [["five_year_plan"]], [], 10,
     "duo:goal_red_star_gold_wreath", "", "add_research_slot = 1",
     "A ruby star once crowned the spire of the Party House. The engineers who put it back up are rewarded with "
     "their own institute, and the Party's best minds go back to work beneath it."),
    ("electrify_the_districts", "Electrify the Districts", 13, 6, [["star_on_the_party_house"]], [], 9,
     "duo:Generic_Electrification", "",
     """every_owned_state = {
	limit = { is_core_of = ROOT free_building_slots = { building = infrastructure size > 0 } }
	add_building_construction = { type = infrastructure level = 1 instant_build = yes }
}
capital_scope = {
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}""",
     "Communism is the Party plus the electrification of the whole city. New lines run from the power station to "
     "every district we hold, and the street lamps of the commune burn all night."),
    # ================================================================== Order in the Centre: the authoritarian path
    ("curfew_on_the_largo", "Curfew on the Largo", 22, 1, [["order_in_the_centre"]], [], 5,
     "duo:Generic_Policeman", "",
     "add_stability = 0.10\nadd_political_power = 50",
     "From ten in the evening the Largo belongs to the patrols. The cafés close early, the trams stop at the "
     "bridges and anyone out after dark had better have a very good reason and the right stamp on their papers."),
    ("centres_own_guard", "The Centre's Own Guard", 26, 1, [["order_in_the_centre"]], [], 7,
     "duo:goal_enlist_the_police", "",
     "army_experience = 15\nadd_manpower = 10000\nadd_war_support = 0.05",
     "The district guard of Sredets is given new uniforms, new rifles and a single order: keep the centre "
     "quiet. Recruits are taken from the police, the fire brigade and the doormen of the ministries."),
    ("who_stands_with_sredets", "Who Stands with Sredets?", 24, 2, [["curfew_on_the_largo"], ["centres_own_guard"]], [], 5,
     "duo:Generic_Factionalism", "",
     "add_political_power = 75",
     "Order has returned to the centre. Now Victor must decide how to face the rest of the city: alone behind "
     "his own barricades, with the Evil Gang at his side, at the head of the C Class Hools, or not at all, "
     "if Konstantin Ilchev has anything to say about it."),
    # ------------------------------------------------------------------ alone
    ("sredets_stands_alone", "Sredets Stands Alone", 18, 3, [["who_stands_with_sredets"]],
     ["call_the_evil_gang", "unleash_the_c_class", "ilchevs_lesson"], 5,
     "duo:goal_generic_isolation", "",
     "add_ideas = SRD_stands_alone\nnews_event = { id = evil_sofia_news.9 hours = 6 }",
     "No alliances, no gangs, no favours owed. Every warlord in Sofia who ever shook Victor's hand did it with "
     "the other hand on a knife. Sredets will defend itself, feed itself and arm itself, and it will never "
     "again depend on anyone.\\n\\nSredets can no longer create or join factions."),
    ("no_friends_no_debts", "No Friends, No Debts", 17, 4, [["sredets_stands_alone"]], [], 5,
     "duo:goal_generic_neutrality_focus", "",
     "add_political_power = 120\nadd_stability = 0.05",
     "Sredets owes nothing to anyone, and nobody owes Sredets. Every lev the district used to spend on "
     "keeping its neighbours friendly now stays at home."),
    ("fortress_sredets", "Fortress Sredets", 19, 4, [["sredets_stands_alone"]], [], 9,
     "duo:goal_generic_fortify_city", "",
     """capital_scope = {
	add_building_construction = { type = bunker level = 3 province = { all_provinces = yes limit_to_border = yes } instant_build = yes }
	add_building_construction = { type = anti_air_building level = 2 instant_build = yes }
}""",
     "Concrete on every bridge, sandbags on every corner and machine guns in the windows of the ministries. "
     "If the rest of Sofia wants the centre, it will have to come and take it, one doorway at a time."),
    ("self_reliant_workshops", "Self-Reliant Workshops", 17, 5, [["no_friends_no_debts"]], [], 10,
     "duo:Generic_Underground_Factories", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
	add_building_construction = { type = arms_factory level = 1 instant_build = yes }
}""",
     "No imports, no help, no trade with anyone who might stop trading tomorrow. The cellars of the centre are "
     "turned into workshops that make everything Sredets needs, badly at first, then well."),
    ("every_citizen_a_soldier", "Every Citizen a Soldier", 19, 5, [["fortress_sredets"]], [], 7,
     "duo:goal_national_mobilization", "",
     "add_manpower = 20000\nadd_war_support = 0.05",
     "A fortress needs a garrison. Every man and woman of the centre learns to load a rifle, man a barricade "
     "and carry the wounded down the stairs of a panel block."),
    ("take_the_centre_alone", "Take the Centre Alone", 18, 6, [["self_reliant_workshops"], ["every_citizen_a_soldier"]], [], 8,
     "duo:Generic_Tank_through_Wall", "",
     "{CLAIMS:VAZ,OBR}\n{WAR:VAZ,OBR}",
     "Vazrazhdane and Oborishte sit on our doorstep, close enough to shell the Party House. Sredets cannot be a "
     "fortress with enemies inside its walls. They will be taken, by Sredets and by Sredets alone.\\n\\nClaims "
     "and war goals on Vazrazhdane and Oborishte."),
    ("one_hand_over_the_centre", "One Hand over the Centre", 18, 7, [["take_the_centre_alone"]], [], 6,
     "duo:Generic_Helmet_Knife", "{HELD:VAZ,OBR}",
     "{COREHELD:SRD:VAZ,OBR}\nadd_stability = 0.10",
     "The market halls of Vazrazhdane and the cathedral square of Oborishte answer to Victor now. The centre of "
     "Sofia is one district again, held by one hand.\\n\\nCores on the states held. Needs every state of "
     "Vazrazhdane and Oborishte held."),
    ("sredets_above_all", "Sredets Above All", 18, 8, [["one_hand_over_the_centre"]], [], 10,
     "duo:goal_skull_fortification", "",
     "swap_ideas = { remove_idea = SRD_stands_alone add_idea = SRD_above_all }\nadd_research_slot = 1",
     "Alone, Sredets has done what no alliance in Sofia could. Its people no longer think of themselves as "
     "citizens of a district, but of the only district that matters."),
    # ------------------------------------------------------------------ the Evil Gang
    ("call_the_evil_gang", "Call the Evil Gang", 22, 3, [["who_stands_with_sredets"]],
     ["sredets_stands_alone", "unleash_the_c_class", "ilchevs_lesson"], 5,
     "photo:evil_gang", "",
     """if = { limit = { is_in_faction = yes } leave_faction = yes }
create_faction = EVIL_SOFIA_FACTION_EVIL_GANG
add_political_power = 50
news_event = { id = evil_sofia_news.10 hours = 6 }""",
     "Long before the city fell apart, there was a group chat. It had a ridiculous name, a profile picture taken "
     "on the steps of a theatre and every one of the people who now rule half the districts of Sofia.\\n\\n"
     "Victor opens it again and types one message: the Evil Gang rides again. Then he starts inviting them, one "
     "by one."),
    ("invite_anton", "Invite Anton Zafirov", 21, 4, [["call_the_evil_gang"]], [], 5,
     "person:invite_anton", "", "{INVITE:OBR}",
     "Anton is three streets away and has never once missed a gang meeting. Whether he still remembers that "
     "depends on how he feels about Sredets these days.\\n\\nOborishte is invited to the Evil Gang. Anton is "
     "more likely to accept the better he thinks of Sredets."),
    ("invite_georgi", "Invite Georgi Yanchovichin", 23, 4, [["call_the_evil_gang"]], [], 4,
     "person:invite_georgi", "", "{INVITE:LOZ}",
     "Georgi does not need an invitation. He is a day one; he was in the chat before the chat had a name. Victor "
     "sends him one anyway, because that is how it is done.\\n\\nLozenets is invited to the Evil Gang. As "
     "Victor's day one, Georgi is the most likely of all to say yes."),
    ("invite_poryazov", "Invite Georgi Poryazov", 21, 5, [["invite_anton"]], [], 5,
     "person:invite_poryazov", "", "{INVITE:MLA}",
     "Georgi Poryazov has four housing estates and more men than he knows what to do with. In the gang he was "
     "always the one who arrived last and stayed the longest.\\n\\nMladost is invited to the Evil Gang."),
    ("invite_kartunov", "Invite Stefan Kartunov", 23, 5, [["invite_georgi"]], [], 5,
     "person:invite_kartunov", "", "{INVITE:KRP}",
     "Stefan rules the courtyards of Krasna Polyana and trusts nobody from the centre. Nobody, except the people "
     "who were in the gang with him.\\n\\nKrasna Polyana is invited to the Evil Gang."),
    ("invite_dimitrov", "Invite Alexander Dimitrov", 21, 6, [["invite_poryazov"]], [], 5,
     "person:invite_dimitrov", "", "{INVITE:TRD}",
     "Alexander will listen politely, agree with everything and then do what he likes. In the gang, that was "
     "exactly why everyone liked him.\\n\\nTriaditsa is invited to the Evil Gang."),
    ("invite_grimboss", "Invite GrimBoss", 23, 6, [["invite_kartunov"]], [], 5,
     "person:invite_grimboss", "", "{INVITE:LYU}",
     "Nobody has seen GrimBoss in daylight since the city fell. The message is read within a second. The reply "
     "will take as long as GrimBoss wants it to.\\n\\nLyulin is invited to the Evil Gang."),
    ("even_henry", "Even Henry?", 22, 7, [["invite_dimitrov", "invite_grimboss"]], [], 6,
     "person:even_henry", "", "{INVITE:VIT}",
     "He hates the centre. His mother hates the centre. But he was in the gang, and the gang does not leave "
     "anyone out. Victor swallows his pride and sends the last invitation to Boyana.\\n\\nVitosha is invited to "
     "the Evil Gang. Daniel-Henry will not make it easy."),
    ("the_evil_gang_rules_sofia", "The Evil Gang Rules Sofia", 22, 8, [["even_henry"]], [], 8,
     "duo:goal_generic_join_faction", "",
     """add_ideas = SRD_evil_gang
every_other_country = {
	limit = { is_in_faction_with = ROOT }
	add_ideas = SRD_evil_gang
}
every_neighbor_country = {
	limit = { NOT = { is_in_faction_with = ROOT } }
	ROOT = { create_wargoal = { type = annex_everything target = PREV } }
}""",
     "Whoever came, came. The Evil Gang is no longer a group chat, it is the strongest alliance in Sofia, and "
     "everyone outside it is about to find out what that means.\\n\\nEvery member of the Evil Gang gets the "
     "Evil Gang spirit. War goals on every neighbour outside the gang."),
    # ------------------------------------------------------------------ the C Class Hools
    ("unleash_the_c_class", "Unleash the C Class", 26, 3, [["who_stands_with_sredets"]],
     ["sredets_stands_alone", "call_the_evil_gang", "ilchevs_lesson"], 5,
     "photo:c_class", "",
     """if = { limit = { is_in_faction = yes } leave_faction = yes }
create_faction = EVIL_SOFIA_FACTION_C_CLASS
add_ideas = SRD_c_class_hools
news_event = { id = evil_sofia_news.11 hours = 6 }""",
     "Every school has a class like the C Class: loud, loyal, impossible to teach and absolutely fearless. Now "
     "they have grown up, they have a group chat of their own, and they have been waiting for a reason.\\n\\n"
     "Victor gives them one. The C Class Hools are on the streets."),
    ("ultras_of_the_stadium", "Ultras of the Stadium", 25, 4, [["unleash_the_c_class"]], [], 6,
     "duo:goal_balkan_fist", "",
     "add_manpower = 20000\nadd_war_support = 0.05",
     "The north stand of the national stadium has always had its own laws. Its ultras swap their scarves for "
     "armbands and march into the barracks of Sredets singing the same songs they sing on match days."),
    ("flares_and_firecrackers", "Flares and Firecrackers", 27, 4, [["unleash_the_c_class"]], [], 7,
     "duo:Generic_Firebombing", "",
     "add_tech_bonus = { name = SRD_flares_and_firecrackers bonus = 1.0 uses = 1 category = artillery }\n"
     "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1000 }",
     "Anyone who has stood in a stand with a lit flare knows a little about artillery already. The C Class's "
     "pyrotechnicians are put to work on something louder."),
    ("away_day", "Away Day", 25, 5, [["ultras_of_the_stadium"]], [], 7,
     "duo:Generic_Helmet_Knife", "",
     "{CLAIMS:VAZ,OBR}\n{WAR:VAZ,OBR}",
     "Every firm knows the rule: on away days you go to their ground. Vazrazhdane and Oborishte are the closest "
     "grounds there are.\\n\\nClaims and war goals on Vazrazhdane and Oborishte."),
    ("pitch_invasion", "Pitch Invasion", 27, 5, [["flares_and_firecrackers"]], [], 8,
     "duo:Generic_Violent_Coup", "",
     "army_experience = 30\nadd_tech_bonus = { name = SRD_pitch_invasion bonus = 1.0 uses = 1 category = land_doctrine }",
     "The fastest way across a football pitch is all at once, before the stewards can react. The C Class turns "
     "the pitch invasion into a doctrine."),
    ("recruit_the_firms", "Recruit the Firms", 26, 6, [["away_day"], ["pitch_invasion"]], [], 6,
     "duo:Generic_Juche_Gang", "",
     """every_neighbor_country = {
	limit = { is_in_faction = no NOT = { has_war_with = ROOT } }
	country_event = { id = evil_sofia_srd.14 }
}""",
     "Every district has its firm, and every firm has heard of the C Class. They are offered the same choice "
     "everyone gets on the street: join us, or get hit.\\n\\nEvery neighbour outside a faction is invited to "
     "join the C Class Hools. Weaker neighbours are more likely to say yes; those who refuse give us a war goal."),
    ("home_ground", "Home Ground", 26, 7, [["recruit_the_firms"]], [], 6,
     "duo:goal_generic_fortify_city", "{HELD:VAZ,OBR}",
     "{COREHELD:SRD:VAZ,OBR}\nadd_stability = 0.05",
     "The away grounds of the centre are home grounds now. The C Class paints its colours on every wall of "
     "Vazrazhdane and Oborishte.\\n\\nCores on the states held. Needs every state of Vazrazhdane and Oborishte "
     "held."),
    ("champions_of_sofia", "Champions of Sofia", 26, 8, [["home_ground"]], [], 9,
     "duo:goal_HOL_fires_of_revolution", "",
     "swap_ideas = { remove_idea = SRD_c_class_hools add_idea = SRD_champions_of_sofia }",
     "Every firm in Sofia now knows who the champions are. The C Class marches through the centre with flares "
     "lit and scarves held high, and nobody dares to look them in the eye."),
    # ------------------------------------------------------------------ Konstantin Ilchev
    ("ilchevs_lesson", "The Physics Teacher Steps In", 30, 3, [["who_stands_with_sredets"]],
     ["sredets_stands_alone", "call_the_evil_gang", "unleash_the_c_class"], 5,
     "person:ilchevs_lesson", "",
     """add_country_leader_role = {
	character = SRD_ilchev
	country_leader = { desc = "SRD_ilchev_desc" ideology = despotism expire = "1965.1.1.1" }
	promote_leader = yes
}
add_stability = -0.05
add_political_power = 100
news_event = { id = evil_sofia_news.12 hours = 6 }""",
     "Konstantin Ilchev has watched his former student run Sredets for long enough. One morning he walks into "
     "the Party House with a red pen and a stack of marked exam papers, and the guards, who all sat in his "
     "classes too, let him straight through.\\n\\nVictor Kolev is sent to detention. Ilchev leads Sredets now."),
    ("newtons_laws", "Newton's Laws of Government", 29, 4, [["ilchevs_lesson"]], [], 6,
     "duo:KTG_Bookstack", "",
     "add_stability = 0.15\nadd_political_power = 50",
     "First law: a district at rest stays at rest unless acted upon by Ilchev. Second law: the force of a decree "
     "equals the mass of paperwork times its acceleration. Third law: for every complaint there is an equal "
     "and opposite detention."),
    ("laboratory_of_the_nation", "Laboratory of the Nation", 31, 4, [["ilchevs_lesson"]], [], 10,
     "duo:goal_great_science", "",
     "add_research_slot = 1",
     "The ministries are turned into laboratories, and the laboratories into ministries. Every civil servant "
     "in Sredets now wears a white coat and keeps a lab notebook."),
    ("homework_for_everyone", "Homework for Everyone", 29, 5, [["newtons_laws"]], [], 7,
     "duo:Focus_Examine_Foreign_Science", "",
     "add_tech_bonus = { name = SRD_homework_for_everyone bonus = 0.5 uses = 2 category = industry }\n"
     "add_political_power = 50",
     "Every household of the centre receives a worksheet each Monday, due by Friday. Late submissions are not "
     "accepted. The factories have never been so well organised."),
    ("pop_quiz_for_the_army", "Pop Quiz for the Army", 31, 5, [["laboratory_of_the_nation"]], [], 7,
     "duo:goal_military_research", "",
     "army_experience = 25\nadd_tech_bonus = { name = SRD_pop_quiz_for_the_army bonus = 1.0 uses = 1 category = land_doctrine }",
     "Officers who cannot calculate a shell's trajectory on paper are sent back to the barracks to study. The "
     "officers who can are promoted. Ilchev marks every paper himself."),
    ("e_equals_mc2", "E = mc²", 30, 6, [["homework_for_everyone"], ["pop_quiz_for_the_army"]], [], 12,
     "duo:Generic_Red_Atomic", "",
     "add_ideas = SRD_laboratory\nadd_tech_bonus = { name = SRD_e_equals_mc2 bonus = 0.75 uses = 2 category = electronics }",
     "Energy equals mass times the speed of light squared. Ilchev writes it on the blackboard of the Council "
     "Chamber and explains, very slowly, what it could mean for a small district with enemies on every side."),
    ("the_final_exam", "The Final Exam", 30, 7, [["e_equals_mc2"]], [], 8,
     "duo:Generic_Coup02", "",
     "{CLAIMS:VAZ,OBR}\n{WAR:VAZ,OBR}",
     "Vazrazhdane and Oborishte have failed every test of good neighbourliness. Ilchev sets them one final exam, "
     "and he has already decided the grade.\\n\\nClaims and war goals on Vazrazhdane and Oborishte."),
    ("grades_are_final", "Grades Are Final", 30, 8, [["the_final_exam"]], [], 6,
     "duo:goal_nested_fortifications", "{HELD:VAZ,OBR}",
     "{COREHELD:SRD:VAZ,OBR}\nadd_stability = 0.05",
     "There will be no resits. The centre has been marked, graded and filed under Sredets.\\n\\nCores on the "
     "states held. Needs every state of Vazrazhdane and Oborishte held."),
]

FILTERS = {  # search filters for the focus tree's filter buttons
    "henrys_mom_was_right": ["POLITICAL", "WAR_SUPPORT"], "order_in_the_centre": ["POLITICAL", "STABILITY"],
    "comrades_in_oborishte": ["POLITICAL"], "red_newspapers_oborishte": ["POLITICAL"],
    "ally_anton": ["POLITICAL"], "anton_must_go": ["ANNEXATION", "WAR_SUPPORT"], "north_south_pact": ["POLITICAL"],
    "destroy_anton": ["ANNEXATION", "STABILITY"],
    "pact_centre": ["ANNEXATION"], "pact_old_quarters": ["ANNEXATION"], "pact_housing_estates": ["ANNEXATION"],
    "pact_kremikovtsi": ["ANNEXATION"], "pact_outskirts": ["ANNEXATION"], "sofia_union": ["ANNEXATION", "STABILITY"],
    "one_centre": ["ANNEXATION"], "united_old_quarters": ["ANNEXATION"], "united_housing_estates": ["ANNEXATION"],
    "united_kremikovtsi": ["ANNEXATION"], "united_outskirts": ["ANNEXATION"], "sofia_commune": ["ANNEXATION", "STABILITY"],
    "peoples_militia": ["MANPOWER"], "komsomol_of_the_estates": ["MANPOWER", "WAR_SUPPORT"],
    "party_takes_the_largo": ["POLITICAL", "STABILITY"], "red_guards_of_the_stadium": ["ARMY_XP", "WAR_SUPPORT"],
    "arm_the_workers": ["RESEARCH"], "barricades_on_vitosha": ["INDUSTRY"],
    "red_officer_school": ["ARMY_XP", "RESEARCH"], "tram_depot_tank_works": ["INDUSTRY", "RESEARCH"],
    "universal_service": ["MANPOWER"], "commissars_in_every_unit": ["ARMY_XP", "RESEARCH"],
    "red_air_over_the_centre": ["AIR_XP", "RESEARCH", "INDUSTRY"], "metro_goes_to_war": ["INDUSTRY", "STABILITY"],
    "red_leaflets": ["POLITICAL"], "road_to_boyana": ["POLITICAL"], "capel_question": ["WAR_SUPPORT", "ANNEXATION"],
    "red_flag_over_boyana": ["ANNEXATION", "STABILITY"],
    "collectivise_vitosha_boulevard": ["INDUSTRY"], "mimas_for_the_workers": ["STABILITY", "WAR_SUPPORT"],
    "party_arsenal": ["INDUSTRY"], "red_tourism": ["INDUSTRY", "POLITICAL"], "red_university": ["RESEARCH"],
    "socialist_emulation": ["INDUSTRY"], "five_year_plan": ["INDUSTRY", "RESEARCH"],
    "star_on_the_party_house": ["RESEARCH"], "electrify_the_districts": ["INDUSTRY"],
    "curfew_on_the_largo": ["STABILITY", "POLITICAL"], "centres_own_guard": ["ARMY_XP", "MANPOWER", "WAR_SUPPORT"],
    "who_stands_with_sredets": ["POLITICAL"],
    "sredets_stands_alone": ["POLITICAL", "STABILITY"], "no_friends_no_debts": ["POLITICAL", "STABILITY"],
    "fortress_sredets": ["INDUSTRY"], "self_reliant_workshops": ["INDUSTRY"],
    "every_citizen_a_soldier": ["MANPOWER", "WAR_SUPPORT"], "take_the_centre_alone": ["ANNEXATION"],
    "one_hand_over_the_centre": ["ANNEXATION", "STABILITY"], "sredets_above_all": ["RESEARCH", "STABILITY"],
    "call_the_evil_gang": ["POLITICAL"], "invite_anton": ["POLITICAL"], "invite_georgi": ["POLITICAL"],
    "invite_poryazov": ["POLITICAL"], "invite_kartunov": ["POLITICAL"], "invite_dimitrov": ["POLITICAL"],
    "invite_grimboss": ["POLITICAL"], "even_henry": ["POLITICAL"], "the_evil_gang_rules_sofia": ["ANNEXATION"],
    "unleash_the_c_class": ["POLITICAL", "WAR_SUPPORT"], "ultras_of_the_stadium": ["MANPOWER", "WAR_SUPPORT"],
    "flares_and_firecrackers": ["RESEARCH"], "away_day": ["ANNEXATION"], "pitch_invasion": ["ARMY_XP", "RESEARCH"],
    "recruit_the_firms": ["POLITICAL", "ANNEXATION"], "home_ground": ["ANNEXATION", "STABILITY"],
    "champions_of_sofia": ["WAR_SUPPORT"],
    "ilchevs_lesson": ["POLITICAL"], "newtons_laws": ["STABILITY", "POLITICAL"],
    "laboratory_of_the_nation": ["RESEARCH"], "homework_for_everyone": ["RESEARCH", "INDUSTRY"],
    "pop_quiz_for_the_army": ["ARMY_XP", "RESEARCH"], "e_equals_mc2": ["RESEARCH"],
    "the_final_exam": ["ANNEXATION"], "grades_are_final": ["ANNEXATION", "STABILITY"],
}

PERSON_ICONS = {  # key: (portrait tag, frame, piece in front, rotation, options)
    "ally_anton": ("OBR", "RedWheatFrame.png", "Hands Shaking.png", 0, dict(fill=(95, 22, 22), front_width=0.46, front_y=0.5)),
    "anton_must_go": ("OBR", "SpikyFrame.png", "Sword.png", -90, dict(fill=(32, 32, 40), front_width=0.72, front_y=0.72)),
    "destroy_anton": ("OBR", "Kill_Frame.png", None, 0, {}),
    "capel_question": ("VIT", "SilverStarFrame.png", "Rifles Crossed.png", 0, dict(fill=(40, 30, 30), front_width=0.6, front_y=0.88)),
    # the Evil Gang's invitations: each friend in a different frame, a handshake in front of him
    "invite_anton": ("OBR", "CircleFrame.png", "Hands Shaking2.png", 0, dict(fill=(34, 34, 40), front_width=0.46, front_y=0.5)),
    "invite_georgi": ("LOZ", "LeavedFrame.png", "Hands Shaking.png", 0, dict(fill=(30, 46, 34), front_width=0.46, front_y=0.5)),
    "invite_poryazov": ("MLA", "metalcircle.png", "Hands Shaking3.png", 0, dict(fill=(36, 36, 44), front_width=0.46, front_y=0.5)),
    "invite_kartunov": ("KRP", "SunStarFrame.png", "Hands Shaking2.png", 0, dict(fill=(44, 34, 24), front_width=0.42, front_y=0.5)),
    "invite_dimitrov": ("TRD", "SilverStarFrame.png", "Hands Shaking4.png", 0, dict(fill=(30, 30, 40), front_width=0.46, front_y=0.5)),
    "invite_grimboss": ("LYU", "SpikyFrame.png", "Hands Shaking3.png", 0, dict(fill=(24, 24, 28), front_width=0.46, front_y=0.5)),
    "even_henry": ("VIT", "RedWheatFrame.png", "Hands Shaking.png", 0, dict(fill=(60, 30, 30), front_width=0.46, front_y=0.5)),
    "ilchevs_lesson": ("SRD_ilchev", "LeavedFrame.png", "Book Open.png", 0, dict(fill=(36, 36, 30), front_width=0.5, front_y=0.62)),
}
# group photos in a frame, black and white: key: (photo in tools/portraits, frame, crop box, piece in front or None)
PHOTO_ICONS = {
    "evil_gang": ("EVIL_GANG", "SpikyFrame.png", (110, 130, 1010, 1030), None),
    "c_class": ("C_CLASS", "LeavedFrame.png", (250, 260, 1000, 1010), None),
}
PHOTO_FALLBACK = {"evil_gang": "goal_generic_join_faction", "c_class": "goal_balkan_fist"}
PERSON_FALLBACK = {"ally_anton": "goal_generic_alliance", "anton_must_go": "goal_generic_demand_territory",
                   "destroy_anton": "goal_generic_attack_allies", "capel_question": "goal_generic_demand_territory",
                   "ilchevs_lesson": "KTG_Bookstack"}
PERSON_FALLBACK.update({k: "goal_ANQ_patriotic_protests" for k in ("invite_anton", "invite_georgi", "invite_poryazov",
                        "invite_kartunov", "invite_dimitrov", "invite_grimboss", "even_henry")})

IDEAS = {  # key: (name, description, modifiers, icon: "custom:<key>" or (background, piece) from the GFX pack)
    "SRD_mimas_doner": ("Mimas Döner",
                        "Open day and night, through curfews and street fighting. A Red Guard coming off a night "
                        "patrol knows exactly where his next meal is, and so does everyone else in the centre.",
                        "stability_factor = 0.05\nwar_support_factor = 0.05\nconsumer_goods_factor = -0.05",
                        "custom:idea_doner"),
    "SRD_militia_spirit": ("The People's Militia",
                            "Red armbands on every block we take. Badly drilled, badly armed and absolutely "
                            "determined to hold the street they grew up on.",
                            "conscription = 0.01\narmy_defence_factor = 0.05", ("Army.png", "Rifles Crossed.png")),
    "SRD_komsomol": ("Komsomol of the Housing Estates",
                     "A youth hall in every estate, a marching song for every block and a waiting list for the front.",
                     "conscription_factor = 0.10\npolitical_power_factor = 0.05", ("Rectangle.png", "Torch Gold.png")),
    "SRD_universal_service_spirit": ("Every Comrade Serves",
                              "Every comrade between eighteen and sixty has a rifle number. The cafés are emptier, "
                              "the barracks are full.",
                              "conscription = 0.02\nstability_factor = -0.02", ("Army.png", "Soldiers in Rows.png")),
    "SRD_emulation_spirit": ("Socialist Emulation",
                                "Shift against shift, factory against factory. The winners get a pennant and a "
                                "photograph in the paper; everyone gets more work.",
                                "production_speed_buildings_factor = 0.05\nindustrial_capacity_factory = 0.05",
                                ("Rectangle.png", "Cog.png")),
}
_NO_FACTIONS = "rule = { can_create_factions = no can_join_factions = no }"
IDEAS.update({  # the authoritarian path; a fifth element is extra script for the idea (here: rules)
    "SRD_stands_alone": ("Sredets Stands Alone",
                         "No alliances, no gangs, no favours owed. Sredets defends itself, and only itself.",
                         "stability_factor = 0.10\narmy_defence_factor = 0.05\npolitical_power_factor = 0.10",
                         ("Shield.png", "Lion.png"), _NO_FACTIONS),
    "SRD_above_all": ("Sredets Above All",
                      "Alone, Sredets has done what no alliance in Sofia could.",
                      "stability_factor = 0.15\narmy_defence_factor = 0.10\narmy_attack_factor = 0.05\n"
                      "political_power_factor = 0.10", ("Pentagon.png", "Lion.png"), _NO_FACTIONS),
    "SRD_evil_gang": ("The Evil Gang",
                      "It started as a group chat. It ended as the strongest alliance in Sofia.",
                      "army_attack_factor = 0.05\narmy_defence_factor = 0.05\nstability_factor = 0.05",
                      ("Army.png", "Knives Crossed.png")),
    "SRD_c_class_hools": ("The C Class Hools",
                          "Loud, loyal, impossible to teach and absolutely fearless.",
                          "army_attack_factor = 0.08\nwar_support_factor = 0.10\nstability_factor = -0.05",
                          ("Rectangle.png", "Fire.png")),
    "SRD_champions_of_sofia": ("Champions of Sofia",
                               "Every firm in the city knows who the champions are.",
                               "army_attack_factor = 0.12\narmy_morale_factor = 0.10\nwar_support_factor = 0.15\n"
                               "stability_factor = -0.03", ("Pentagon.png", "Fire2.png")),
    "SRD_laboratory": ("The Laboratory of Sredets",
                       "Every ministry a laboratory, every civil servant in a white coat.",
                       "research_speed_factor = 0.07\nproduction_speed_buildings_factor = 0.05",
                       ("Rectangle.png", "Nuclear Atom.png")),
})
RED_COUNTRIES = ["SRD", "OBR"]   # the countries that get a communist flag and a Commune name

OBR_GOES_RED = """set_popularities = { communism = 60 neutrality = 40 democratic = 0 fascism = 0 }
set_politics = { ruling_party = communism elections_allowed = no }
add_country_leader_role = {
	character = OBR_leader
	country_leader = { ideology = leninism expire = "1965.1.1.1" }
	promote_leader = yes
}
set_cosmetic_tag = OBR_RED"""

# The Oborishte Question: decisions for Sredets to push Oborishte's politics to the left.
DECISIONS = {
    "category": ("SRD_oborishte_question", "The Oborishte Question",
                 "Anton Zafirov's Oborishte begins three streets from the Party House. A red Oborishte means a red "
                 "centre; an Oborishte that stays neutral means a front line in front of the cathedral. Money, "
                 "rallies and, when the moment comes, a coup can push Anton's district to the left.",
                 "has_completed_focus = SRD_comrades_in_oborishte\nOBR = { exists = yes }"),
    "decisions": [
        ("SRD_fund_oborishte_communists", "Fund the Oborishte Communists",
         "Envelopes of cash for the Oborishte party cell: printing presses, rented halls and a few police officers "
         "who look the other way.", 50, 30,
         "OBR = { NOT = { has_government = communism } }",
         "OBR = { add_popularity = { ideology = communism popularity = 0.05 } }"),
        ("SRD_rally_at_the_doctors_garden", "Rally at the Doctors' Garden",
         "Ten thousand people, red flags and loudspeakers in the park behind the National Library. Anton's police "
         "will not dare to clear it, and his ministers will not sleep that night.", 35, 45,
         "OBR = { NOT = { has_government = communism } }",
         "OBR = { add_popularity = { ideology = communism popularity = 0.04 } add_stability = -0.03 }"),
        ("SRD_red_coup_in_oborishte", "Red Coup in Oborishte",
         "The party cell is armed, the barracks on Shipka Street are with us and the district hall is guarded by "
         "three sleepy policemen. One night is all it takes. Anton stays in charge, but of a red Oborishte.\n\n"
         "Needs Red Newspapers in Oborishte and Oborishte more than 55% communist.", 100, 0,
         "has_completed_focus = SRD_red_newspapers_oborishte\nOBR = { NOT = { has_government = communism } communism > 0.55 }",
         "OBR = {\n" + "\n".join("\t" + ln for ln in OBR_GOES_RED.split("\n")) + "\n}\n"
         "OBR = { country_event = { id = evil_sofia_srd.8 } }"),
    ],
}

ANTON_YES = """base = 10
modifier = { add = 25 has_government = communism }
modifier = { add = 15 communism > 0.45 }
modifier = { add = 15 communism > 0.6 }
modifier = { add = 10 communism > 0.75 }
modifier = { add = 10 has_opinion = { target = FROM value > 0 } }
modifier = { add = 15 has_opinion = { target = FROM value > 40 } }
modifier = { add = 15 has_opinion = { target = FROM value > 80 } }
modifier = { factor = 0.5 has_opinion = { target = FROM value < -20 } }"""
ANTON_NO = """base = 50
modifier = { factor = 0.6 communism > 0.6 }
modifier = { factor = 0.5 has_government = communism }
modifier = { factor = 0.7 has_opinion = { target = FROM value > 40 } }
modifier = { add = 30 has_opinion = { target = FROM value < -20 } }"""
GEORGI_YES = """base = 35
modifier = { add = 15 has_opinion = { target = FROM value > 20 } }
modifier = { add = 15 has_opinion = { target = FROM value > 50 } }
modifier = { add = 10 has_opinion = { target = FROM value > 80 } }
modifier = { add = 10 communism > 0.2 }
modifier = { factor = 0.4 has_opinion = { target = FROM value < 0 } }
modifier = { factor = 0.5 is_in_faction = yes }"""
GEORGI_NO = """base = 35
modifier = { add = 20 has_opinion = { target = FROM value < 0 } }
modifier = { add = 20 has_opinion = { target = FROM value < -40 } }
modifier = { factor = 0.7 has_opinion = { target = FROM value > 50 } }"""

# Events of the Sredets tree: number: (title, description, options [(text, effect, AI chance)], picture)
EVENTS = {
    "1": ("Henry's Mom Was Right",
          "The news reaches Boyana before dinner. Sredets has declared for communism; there are red flags on the "
          "Largo and Victor Kolev is calling himself Chairman.\n\nDaniel-Henry Capel's mother puts down the "
          "telephone, turns to her son and says, very calmly, that she has been telling him this for years. The people "
          "of the centre were always communists. She just did not expect them to be so open about it.\n\nHenry has "
          "never hated anything as much as he hates Sredets tonight.",
          [("She was right. We will never forgive them.",
            "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }\n"
            "FROM = { country_event = { id = evil_sofia_srd.5 } }", 80),
           ("No more waiting. Prepare for war!",
            "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }\n"
            "create_wargoal = { type = annex_everything target = FROM }\n"
            "FROM = { country_event = { id = evil_sofia_srd.6 } }", 20)],
          "GFX_report_event_generic_rally"),
    "2": ("Victor at the Door",
          "Victor Kolev has walked the three streets from the Party House to Oborishte himself, with no guards and "
          "no flags, and he is waiting in the hall downstairs.\n\nHis offer is simple. Sredets and Oborishte go "
          "red together and take Sofia together: the north for Anton, the centre and the south for Victor. If Anton "
          "refuses, Victor will not walk here again. The Red Guards will.",
          [("Comrade Victor! The centre will be red together.",
            "if = {\n\tlimit = { NOT = { has_government = communism } }\n"
            + "\n".join("\t" + ln for ln in OBR_GOES_RED.split("\n")) + "\n}\n"
            "set_cosmetic_tag = OBR_RED\n"
            """FROM = {
	set_country_flag = SRD_anton_allied
	if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_RED_CENTRE }
	add_to_faction = OBR
	country_event = { id = evil_sofia_srd.3 }
}""", ANTON_YES),
           ("Oborishte bows to no one. Show him out.",
            "FROM = { create_wargoal = { type = annex_everything target = OBR } country_event = { id = evil_sofia_srd.4 } }",
            ANTON_NO)],
          "GFX_report_event_generic_sign_treaty1"),
    "3": ("Anton Says Yes",
          "Anton Zafirov came down the stairs himself and shook Victor's hand in front of the doorman. By midnight "
          "Oborishte's district hall was flying a red flag. The centre of Sofia is red from the Lions' Bridge to "
          "Eagles' Bridge, and the North-South Pact can be drawn up.",
          [("To Comrade Anton!", "", 1)], "GFX_report_event_generic_sign_treaty1"),
    "4": ("Anton Says No",
          "Victor waited in the hall for an hour. Then a secretary came down and told him that Mr Zafirov was busy. "
          "Victor walked home the long way, past the cathedral, counting the barricades Oborishte would need. It "
          "will need more than it has.",
          [("He will regret it.", "", 1)], "GFX_report_event_generic_read_write"),
    "5": ("Henry Hates Us",
          "Word comes from Boyana: Daniel-Henry Capel has torn up every letter Sredets ever sent him, and his mother "
          "is telling the whole street she was right about us all along. He is not marching yet. He is waiting.",
          [("Let him hate. Let him wait.", "", 1)], "GFX_report_event_generic_read_write"),
    "6": ("Henry Prepares for War",
          "Daniel-Henry Capel will not wait for the red flag to come up the mountain. Vitosha's guards are being "
          "called up and trucks are moving down the Boyana road. Henry has declared that he will save Sofia from "
          "communism himself.",
          [("Let him come down the mountain.", "add_war_support = 0.05", 1)], "GFX_report_event_generic_army"),
    "7": ("A Call from Victor",
          "The telephone rings late at night. It is Victor Kolev, and he is not calling as the Chairman of the "
          "Sredets Commune. He is calling as Victor, who has known Georgi since before either of them had a district "
          "to rule.\n\nHe is going after Daniel-Henry Capel, and Lozenets is the only road from Sredets to Boyana. "
          "He does not want passage. He wants Georgi beside him. Day ones, he says. Like always.",
          [("Day ones. Lozenets marches with Sredets.",
            """FROM = {
	if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_RED_CENTRE }
	add_to_faction = LOZ
	set_country_flag = SRD_boyana_road_open
	country_event = { id = evil_sofia_srd.9 }
}
add_opinion_modifier = { target = FROM modifier = evil_sofia_day_ones }
FROM = { add_opinion_modifier = { target = ROOT modifier = evil_sofia_day_ones } }""", GEORGI_YES),
           ("I'm sorry, Victor. Lozenets stays out of this.",
            "FROM = { country_event = { id = evil_sofia_srd.10 } }", GEORGI_NO)],
          "GFX_report_event_generic_sign_treaty1"),
    "8": ("A Red Coup in Oborishte",
          "At three in the morning the barracks on Shipka Street opened their gates, and by five the district hall "
          "had changed hands without a shot. Anton Zafirov woke up as the leader of a red Oborishte. He has decided "
          "to be grateful.",
          [("Long live the revolution.", "", 1)], "GFX_report_event_generic_rally"),
    "9": ("Georgi Is In",
          "Georgi did not even let Victor finish the sentence. Lozenets has joined us, its streets are open to the Red "
          "Guards, and its own guards are already moving towards the slopes below Boyana. Henry will not fight one "
          "district. He will fight two.",
          [("Day ones. Always.", "", 1)], "GFX_report_event_generic_sign_treaty1"),
    "10": ("Georgi Says No",
           "Georgi said it quietly, the way you say things to a friend: Lozenets will not go to war for the "
           "revolution, not even for Victor. Without Lozenets there is no road from Sredets to Boyana.",
           [("Then the road goes through Lozenets.",
             "create_wargoal = { type = annex_everything target = FROM }\nset_country_flag = SRD_boyana_road_open", 30),
            ("Friends are friends. We will find another way to Henry.", "add_political_power = 25", 70)],
           "GFX_report_event_generic_read_write"),
}

GANG_YES = """base = 30
modifier = { add = 20 has_opinion = { target = FROM value > 20 } }
modifier = { add = 20 has_opinion = { target = FROM value > 50 } }
modifier = { add = 25 tag = LOZ }
modifier = { factor = 0.4 has_opinion = { target = FROM value < 0 } }
modifier = { factor = 0.5 tag = VIT }
modifier = { factor = 0.3 has_government = communism }
modifier = { factor = 0.4 is_in_faction = yes }"""
GANG_NO = """base = 35
modifier = { add = 25 has_opinion = { target = FROM value < 0 } }
modifier = { add = 20 tag = VIT }
modifier = { factor = 0.6 has_opinion = { target = FROM value > 50 } }"""
FIRM_YES = """base = 15
modifier = { add = 25 strength_ratio = { tag = FROM ratio < 0.6 } }
modifier = { add = 20 strength_ratio = { tag = FROM ratio < 0.3 } }
modifier = { add = 15 has_opinion = { target = FROM value > 40 } }
modifier = { factor = 0.5 has_opinion = { target = FROM value < 0 } }"""
FIRM_NO = """base = 35
modifier = { add = 30 strength_ratio = { tag = FROM ratio > 1 } }
modifier = { add = 15 has_opinion = { target = FROM value < 0 } }"""
EVENTS.update({
    "11": ("An Invitation from the Evil Gang",
           "The old group chat has come back to life. After months of silence there is a new message from Victor "
           "Kolev, and it is addressed to [Root.GetLeader] by name.\n\nThe Evil Gang rides again, it says. The city "
           "is falling apart, the districts are at each other's throats, and the only people Victor has ever trusted "
           "were in this chat. He wants [Root.GetName] in the gang, as an ally, the way it always was.",
           [("Of course. The gang is the gang.",
             """FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_srd.12 } }
add_opinion_modifier = { target = FROM modifier = evil_sofia_gang }
FROM = { add_opinion_modifier = { target = ROOT modifier = evil_sofia_gang } }""", GANG_YES),
            ("Those days are over, Victor.", "FROM = { country_event = { id = evil_sofia_srd.13 } }", GANG_NO)],
           ""),
    "12": ("[From.GetLeader] Is In",
           "The reply came in less than an hour: [From.GetLeader] is in. [From.GetName] has joined the Evil Gang, "
           "and its guards will fight beside ours.",
           [("Welcome back.", "", 1)], ""),
    "13": ("[From.GetLeader] Says No",
           "[From.GetLeader] has read the message and declined. [From.GetName] will not join the Evil Gang. The chat "
           "is a little quieter tonight.",
           [("Their loss.", "", 1)], ""),
    "14": ("The C Class Comes Calling",
           "A delegation from Sredets has arrived at the district hall of [Root.GetName]: a dozen young men in scarves "
           "and hoods, a few of them carrying flares. Their leader explains the offer very simply. [Root.GetName] can "
           "join the C Class Hools, or [Root.GetName] can get hit.",
           [("We join. Nobody wants to get hit.",
             "FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_srd.15 } }", FIRM_YES),
            ("Tell them to come and try.",
             "FROM = { create_wargoal = { type = annex_everything target = ROOT } country_event = { id = evil_sofia_srd.16 } }",
             FIRM_NO)],
           ""),
    "15": ("[From.GetName] Joins the C Class",
           "[From.GetName] took one look at the flares and made its choice. Its guards now march with the C Class Hools.",
           [("One more firm for the C Class.", "", 1)], ""),
    "16": ("[From.GetName] Wants a Fight",
           "[From.GetName] has sent our delegation home with a message that cannot be printed. Fine. Away day it is.",
           [("We know where they live.", "", 1)], ""),
})

# pictures: (flags, mood) for tools/event_pictures.py; stored as (title, description, picture, options)
_PICTURES = {"1": (["SRD_RED"], "dusk"), "2": (["SRD_RED", "OBR"], "night"), "3": (["SRD_RED", "OBR_RED"], "day"),
             "4": (["OBR"], "rain"), "5": (["VIT"], "dusk"), "6": (["VIT"], "fire"), "7": (["SRD_RED", "LOZ"], "night"),
             "8": (["OBR_RED"], "night"), "9": (["SRD_RED", "LOZ"], "day"), "10": (["LOZ"], "rain"),
             "11": (["SRD"], "night"), "12": (["SRD", "LOZ"], "day"), "13": (["SRD"], "rain"),
             "14": (["SRD"], "fire"), "15": (["SRD", "SOFIA"], "dusk"), "16": (["SRD"], "fire")}
EVENTS = {k: (t, d, _PICTURES[k], o) for k, (t, d, o, _) in EVENTS.items()}

TRAITS = {
    "evil_sofia_hates_communism": ("Hates Communism",
                                   "Raised in Boyana on stories of the communists from the centre. His mother made "
                                   "sure he never forgot them.",
                                   "communism_drift = -0.20\ncommunism_acceptance = -200\nwar_support_factor = 0.05"),
}

# Names and colours a country can take (cosmetic tags): tag: (name, adjective, colour, flag recipe)
COSMETIC = {
    "SRD_RED": ("Sredets Commune", "Sredetsian", (200, 25, 30), ("district", "SRD")),
    "OBR_RED": ("Oborishte Commune", "Oborishtian", (150, 20, 45), ("district", "OBR")),
    "SRD_SOFIA": ("Sofia", "Sofian", (210, 20, 25), ("sofia", "")),
    "SRD_SOUTH": ("South Sofia", "South Sofian", (205, 30, 30), ("sofia", "south")),
    "OBR_NORTH": ("North Sofia", "North Sofian", (140, 15, 40), ("sofia", "north")),
}
FACTIONS = {"EVIL_SOFIA_RED_CENTRE": "The Red Centre", "EVIL_SOFIA_FACTION_SOFIA": "Sofia",
            "EVIL_SOFIA_FACTION_EVIL_GANG": "The Evil Gang", "EVIL_SOFIA_FACTION_C_CLASS": "The C Class Hools"}
