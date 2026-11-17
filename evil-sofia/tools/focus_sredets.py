"""Sredets focus tree: the communist path, and the first focus of the authoritarian path.

Each focus: id, name, x, y, prerequisites (groups: all groups needed, any focus within a group), mutually
exclusive, weeks, icon, available (script or ""), reward (script), description.
Placeholders filled in by the build: {OBR_CAP} {VIT_CAP} (capital state ids), {OBR_CORES} {VIT_CORES}
(add_state_core lines), {NORTH_OR} {SOUTH_OR} (is_owned_by lists).
Icons: "duo:<name>" finished pack icon, "person:<key>" leader portrait icon (tools/focus_icons.py),
"custom:<key>" put together from pack frames and pieces.
"""

TAG = "SRD"
NORTH = ["SRK", "POD", "NAD", "VRB", "NIS", "KRE", "ILN", "KRP", "LYU", "BNK"]           # Oborishte's half
SOUTH = ["LOZ", "TRD", "IZG", "SLA", "ISK", "MLA", "STU", "VIT", "KRS", "OVK", "PNC"]    # Sredets' half

FOCUSES = [
    ("henrys_mom_was_right", "Henry's Mom Was Right", 5, 0, [], ["order_in_the_centre"], 10,
     "duo:Communist_Discourse", "",
     """set_popularities = { communism = 65 neutrality = 35 democratic = 0 fascism = 0 }
set_politics = { ruling_party = communism elections_allowed = no }
add_country_leader_role = {
	character = SRD_leader
	country_leader = { ideology = leninism expire = "2100.1.1.1" }
	promote_leader = yes
}
add_war_support = 0.10
VIT = { country_event = { id = evil_sofia_srd.1 } }""",
     "For years Daniel-Henry's mom has called everyone from the centre a dirty communist. Fine. She was right."),
    ("order_in_the_centre", "Order in the Centre", 12, 0, [], ["henrys_mom_was_right"], 10,
     "duo:goal_authoritarian", "",
     "add_stability = 0.15\nadd_political_power = 100",
     "No parties, no slogans. Victor Kolev keeps the centre in order with his own hand."),
    # ------------------------------------------------------------------ Oborishte and Anton Zafirov
    ("comrades_in_oborishte", "Comrades in Oborishte", 1, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Communist_Propaganda", "",
     "OBR = { add_popularity = { ideology = communism popularity = 0.20 } }\nadd_political_power = 50",
     "Leaflets, meetings in the back rooms of Oborishte's cafés, and a few friendly words for Anton Zafirov."),
    ("ally_anton", "Ally Anton Zafirov", 0, 2, [["comrades_in_oborishte"]], ["anton_must_go"], 10,
     "person:ally_anton", "OBR = { exists = yes OR = { has_government = communism communism > 0.4 } }",
     "OBR = { country_event = { id = evil_sofia_srd.2 } }",
     "Anton is one of us, or nearly. Offer him the hand of friendship: the centre will be red together."),
    ("anton_must_go", "Anton Must Go", 2, 2, [["comrades_in_oborishte"]], ["ally_anton"], 10,
     "person:anton_must_go", "OBR = { exists = yes }",
     "create_wargoal = { type = annex_everything target = OBR }\nadd_war_support = 0.10",
     "Anton Zafirov will never share the centre. Then he will not have any of it."),
    ("north_south_pact", "The North-South Pact", 0, 3, [["ally_anton"]], [], 10,
     "duo:GAL_goal_divide_nation", "has_country_flag = SRD_anton_allied",
     """every_state = {
	limit = { OR = { {SOUTH_OR} } }
	ROOT = { add_state_claim = PREV }
}
every_state = {
	limit = { OR = { {NORTH_OR} } }
	OBR = { add_state_claim = PREV }
}""",
     "Victor and Anton draw a line across the map of Sofia. The north for Oborishte, the centre and the south for "
     "Sredets."),
    ("destroy_anton", "Destroy Anton Zafirov", 2, 3, [["ally_anton", "anton_must_go"]], [], 5,
     "person:destroy_anton", "controls_state = {OBR_CAP}\nNOT = { has_country_flag = SRD_anton_allied }",
     "{OBR_CORES}\nadd_political_power = 150\nadd_stability = 0.10",
     "Oborishte has fallen. Its streets belong to Sredets now, and Anton Zafirov is history."),
    ("conquer_the_centre", "Conquer the Centre", 1, 4, [["north_south_pact", "destroy_anton"]], [], 10,
     "duo:Generic_Urban_Warfare", "",
     "create_wargoal = { type = annex_everything target = VAZ }\ncreate_wargoal = { type = annex_everything target = SRK }",
     "Vazrazhdane and Serdika: the rest of the old centre must be ours."),
    # ------------------------------------------------------------------ the Party
    ("party_takes_the_largo", "The Party Takes the Largo", 4, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Revolutionary_Government", "",
     "add_political_power = 100\nadd_stability = 0.10",
     "The Party House on the Largo is ours again. The red flag goes up over the government quarter."),
    ("red_guards_of_the_stadium", "Red Guards of Vasil Levski Stadium", 4, 2, [["party_takes_the_largo"]], [], 10,
     "custom:stadium", "",
     'load_oob = "SRD_red_guards"\nadd_war_support = 0.05',
     "The national stadium becomes a drill ground. Four divisions of Red Guards march out of it."),
    ("arm_the_workers", "Arm the Workers", 4, 3, [["red_guards_of_the_stadium"]], [], 10,
     "duo:goal_integrate_workers_militia", "",
     """add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2000 }
add_tech_bonus = { name = SRD_arm_the_workers bonus = 0.5 uses = 1 category = infantry_weapons }""",
     "A rifle for every waiter, shop assistant and bus driver of the centre."),
    ("barricades_on_vitosha", "Barricades on Vitosha Boulevard", 4, 4, [["arm_the_workers"]], [], 10,
     "duo:Generic_Barricade", "",
     """capital_scope = {
	add_building_construction = { type = bunker level = 3 province = { all_provinces = yes limit_to_border = yes } instant_build = yes }
}""",
     "Café tables, tram rails and paving stones: Vitosha Boulevard becomes a fortress."),
    # ------------------------------------------------------------------ Daniel-Henry Capel
    ("red_leaflets", "Red Leaflets over Vitosha", 7, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Socialist_Propaganda", "VIT = { exists = yes }",
     "VIT = { add_stability = -0.10 add_popularity = { ideology = communism popularity = 0.15 } }",
     "Let Henry's mom find red leaflets in her own letterbox."),
    ("capel_question", "The Capel Question", 7, 2, [["red_leaflets"]], [], 10,
     "person:capel_question", "VIT = { exists = yes }",
     "create_wargoal = { type = annex_everything target = VIT }\nadd_war_support = 0.05",
     "Daniel-Henry hates us. Daniel-Henry hates communism. Daniel-Henry has to go."),
    ("red_flag_over_boyana", "Red Flag over Boyana", 7, 3, [["capel_question"]], [], 10,
     "duo:goal_red_star_green_wreath", "controls_state = {VIT_CAP}",
     "{VIT_CORES}\nadd_political_power = 100\nadd_stability = 0.10",
     "The red flag flies over Boyana. Somewhere, Henry's mom is still saying she told everyone so."),
    ("one_sofia_one_party", "One Sofia, One Party", 6, 5, [["conquer_the_centre"], ["red_flag_over_boyana"]], [], 10,
     "duo:goal_commune_politics", "",
     """if = {
	limit = { has_country_flag = SRD_anton_allied }
	every_state = {
		limit = { OR = { {SOUTH_OR} } NOT = { is_owned_by = ROOT } }
		ROOT = { add_state_claim = PREV }
	}
}
else = {
	every_state = {
		limit = { NOT = { is_owned_by = ROOT } owner = { NOT = { is_in_faction_with = ROOT } } }
		ROOT = { add_state_claim = PREV }
	}
}
add_war_support = 0.20""",
     "One city, one party, one Victor Kolev."),
    # ------------------------------------------------------------------ the red economy of the centre
    ("collectivise_vitosha_boulevard", "Collectivise Vitosha Boulevard", 10, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Market_Socialism", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}""",
     "Every boutique on Vitosha Boulevard now belongs to the people. The people are very well dressed."),
    ("mimas_for_the_workers", "Mimas Döner for the Workers", 9, 2, [["collectivise_vitosha_boulevard"]], [], 10,
     "custom:doner", "", "add_ideas = SRD_mimas_doner",
     "Mimas never closes. Now it feeds the revolution, day and night."),
    ("party_arsenal", "The Party Arsenal", 11, 2, [["collectivise_vitosha_boulevard"]], [], 10,
     "duo:goal_generic_construct_mil_factory", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = arms_factory level = 2 instant_build = yes }
}""",
     "The back rooms of the centre's restaurants start making something other than food."),
    ("red_tourism", "Red Tourism", 9, 3, [["mimas_for_the_workers"]], [], 10, "duo:LEC_Passports", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}
add_political_power = 100""",
     "Tourists still come to the centre. Now they pay the Party."),
    ("five_year_plan", "Five-Year Plan for the Centre", 10, 4, [["red_tourism"], ["party_arsenal"]], [], 10,
     "duo:Generic_Factory_Planning", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}
add_tech_bonus = { name = SRD_five_year_plan bonus = 0.5 uses = 2 category = industry }""",
     "Five years, two more factories, and no more potholes. Probably."),
    ("star_on_the_party_house", "The Star on the Party House", 10, 5, [["five_year_plan"]], [], 10,
     "duo:goal_red_star_gold_wreath", "", "add_research_slot = 1",
     "The red star goes back on top of the Party House, and the Party's best minds go back to work."),
]

PERSON_ICONS = {  # key: (portrait tag, frame, piece in front, rotation, options)
    "ally_anton": ("OBR", "RedWheatFrame.png", "Hands Shaking.png", 0, dict(fill=(95, 22, 22), front_width=0.46, front_y=0.5)),
    "anton_must_go": ("OBR", "SpikyFrame.png", "Sword.png", -90, dict(fill=(32, 32, 40), front_width=0.72, front_y=0.72)),
    "destroy_anton": ("OBR", "Kill_Frame.png", None, 0, {}),
    "capel_question": ("VIT", "SilverStarFrame.png", "Rifles Crossed.png", 0, dict(fill=(40, 30, 30), front_width=0.6, front_y=0.88)),
}
PERSON_FALLBACK = {"ally_anton": "goal_generic_alliance", "anton_must_go": "goal_generic_demand_territory",
                   "destroy_anton": "goal_generic_attack_allies", "capel_question": "goal_generic_demand_territory"}

IDEAS = {
    "SRD_mimas_doner": ("Mimas Döner", "Mimas never closes. Nobody fights hungry in the centre.",
                        "stability_factor = 0.05\nwar_support_factor = 0.05\nconsumer_goods_factor = -0.05"),
}

EVENTS = {
    "1": ("Henry's Mom Was Right",
          "Sredets has declared for communism. Daniel-Henry's mom has been saying it for years: the people of the "
          "centre are dirty communists. Daniel-Henry has never hated anyone as much as he hates Sredets now.",
          [("She was right all along. We will never forgive them.", "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }", 80),
           ("They must be stopped. Prepare for war!", "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }\ncreate_wargoal = { type = annex_everything target = FROM }", 20)]),
    "2": ("An Offer from Sredets",
          "Victor Kolev offers Anton Zafirov an alliance: a red centre, shared between Sredets and Oborishte. "
          "If Anton accepts, Oborishte turns communist and joins Sredets. If he refuses, Sredets will see it as war.",
          [("Comrades! The centre will be red together.",
            """if = {
	limit = { NOT = { has_government = communism } }
	set_popularities = { communism = 60 neutrality = 40 democratic = 0 fascism = 0 }
	set_politics = { ruling_party = communism elections_allowed = no }
}
add_country_leader_role = {
	character = OBR_leader
	country_leader = { ideology = leninism expire = "2100.1.1.1" }
	promote_leader = yes
}
FROM = {
	set_country_flag = SRD_anton_allied
	if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_RED_CENTRE }
	add_to_faction = OBR
}""", 70),
           ("Oborishte bows to no one.", "FROM = { create_wargoal = { type = annex_everything target = OBR } }", 30)]),
}

TRAITS = {
    "evil_sofia_hates_communism": ("Hates Communism",
                                   "Daniel-Henry hates communism more than anything. His mom raised him well.",
                                   "communism_drift = -0.20\ncommunism_acceptance = -200\nwar_support_factor = 0.05"),
}
