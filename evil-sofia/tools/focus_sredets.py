"""Sredets focus tree: the communist path, and the first focus of the authoritarian path.

Each focus: id, name, x, y, prerequisites (groups: all groups needed, any focus within a group), mutually
exclusive, weeks, icon, available (script or ""), reward (script), description.
Placeholders filled in by the build (tools/build_focus.py):
  {OBR_CAP} {VIT_CAP}   capital state ids
  {CORES:A,B}           add_state_core for every state the countries A, B own at the start
  {WAR:A,B}             war goals on A and B (if they still exist)
  {BEATEN:A,B}          trigger: A and B are gone or have capitulated
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
    south, north = half(group, False), half(group, True)
    lines = []
    if south:
        lines += [f"{{CORES:{south}}}", f"{{WAR:{south}}}"]
    if north:
        lines += ["OBR = {", f"\t{{CORES:{north}}}", f"\t{{WAR:{north}}}", "}"]
    return "\n".join(lines + ([sredets_extra] if sredets_extra else [])), (f"{{BEATEN:{','.join(prev)}}}" if prev else "")


def alone_stage(group, prev):
    return f"{{CORES:{','.join(group)}}}\n{{WAR:{','.join(group)}}}", (f"{{BEATEN:{','.join(prev)}}}" if prev else "")


P1, P1a = pact_stage(CENTRE, [])
P2, P2a = pact_stage(OLD_QUARTERS, CENTRE)
P3, P3a = pact_stage(HOUSING, OLD_QUARTERS)
P4, P4a = pact_stage(INDUSTRY, HOUSING, "add_political_power = 100")
P5, P5a = pact_stage(OUTSKIRTS, INDUSTRY)
A1, A1a = alone_stage(CENTRE, [])
A2, A2a = alone_stage(OLD_QUARTERS, CENTRE + ["OBR"])
A3, A3a = alone_stage(HOUSING, OLD_QUARTERS)
A4, A4a = alone_stage(INDUSTRY, HOUSING)
A5, A5a = alone_stage(OUTSKIRTS, INDUSTRY)
ALL_BUT_PACT = ",".join(OLD_QUARTERS + HOUSING + INDUSTRY + OUTSKIRTS + CENTRE)

FOCUSES = [
    ("henrys_mom_was_right", "Henry's Mom Was Right", 8, 0, [], ["order_in_the_centre"], 5,
     "duo:Communist_Discourse", "",
     """set_popularities = { communism = 65 neutrality = 35 democratic = 0 fascism = 0 }
set_politics = { ruling_party = communism elections_allowed = no }
add_country_leader_role = {
	character = SRD_leader
	country_leader = { ideology = leninism expire = "2100.1.1.1" }
	promote_leader = yes
}
set_cosmetic_tag = SRD_RED
add_war_support = 0.10
VIT = { country_event = { id = evil_sofia_srd.1 } }""",
     "For years Daniel-Henry's mom has called everyone from the centre a dirty communist. Fine. She was right."),
    ("order_in_the_centre", "Order in the Centre", 16, 0, [], ["henrys_mom_was_right"], 5,
     "duo:goal_authoritarian", "",
     "add_stability = 0.15\nadd_political_power = 100",
     "No parties, no slogans. Victor Kolev keeps the centre in order with his own hand."),
    # ------------------------------------------------------------------ Oborishte and Anton Zafirov
    ("comrades_in_oborishte", "Comrades in Oborishte", 2, 1, [["henrys_mom_was_right"]], [], 5,
     "duo:Generic_Communist_Propaganda", "",
     "OBR = { add_popularity = { ideology = communism popularity = 0.15 } }\nadd_political_power = 50",
     "Leaflets and meetings in the back rooms of Oborishte's cafés. Unlocks the decisions of the Oborishte Question."),
    ("red_newspapers_oborishte", "Red Newspapers in Oborishte", 2, 2, [["comrades_in_oborishte"]], [], 4,
     "duo:Generic_Communist_Propaganda02", "",
     "OBR = { add_popularity = { ideology = communism popularity = 0.10 } add_stability = -0.05 }",
     "Every kiosk in Oborishte sells our newspaper. Unlocks the decision 'Red Coup in Oborishte'."),
    ("ally_anton", "Ally Anton Zafirov", 1, 3, [["red_newspapers_oborishte"]], ["anton_must_go"], 7,
     "person:ally_anton", "OBR = { exists = yes OR = { has_government = communism communism > 0.4 } }",
     "OBR = { country_event = { id = evil_sofia_srd.2 } }",
     "Anton is one of us, or nearly. Offer him the hand of friendship: the centre will be red together. "
     "Needs Oborishte at least 40% communist."),
    ("anton_must_go", "Anton Must Go", 3, 3, [["red_newspapers_oborishte"]], ["ally_anton"], 6,
     "person:anton_must_go", "OBR = { exists = yes }",
     "create_wargoal = { type = annex_everything target = OBR }\nadd_war_support = 0.10",
     "Anton Zafirov will never share the centre. Then he will not have any of it."),
    ("north_south_pact", "The North-South Pact", 0, 4, [["ally_anton"]], [], 6,
     "duo:GAL_goal_divide_nation", "has_country_flag = SRD_anton_allied",
     "add_political_power = 100\nOBR = { add_political_power = 100 }",
     "Victor and Anton draw a line across the map of Sofia. The north for Oborishte, the centre and the south "
     "for Sredets. District by district, it will all be ours."),
    ("destroy_anton", "Destroy Anton Zafirov", 4, 4, [["ally_anton", "anton_must_go"]], [], 5,
     "person:destroy_anton", "controls_state = {OBR_CAP}\nNOT = { has_country_flag = SRD_anton_allied }",
     "{CORES:OBR}\nadd_political_power = 150\nadd_stability = 0.10",
     "Oborishte has fallen. Its streets belong to Sredets now, and Anton Zafirov is history."),
    # the pact: Sofia split between Sredets (south) and Oborishte (north), one group of districts at a time
    ("pact_centre", "The Red Centre", 0, 5, [["north_south_pact"]], [], 8, "duo:Generic_Redraw_Borders", P1a,
     P1, "First the centre itself: Vazrazhdane. Cores and war goals."),
    ("pact_old_quarters", "The Old Quarters", 0, 6, [["pact_centre"]], [], 10, "duo:SIA_Urban_Warfare_NF", P2a, P2,
     "The districts built before the war: Krasno Selo, Slatina, Izgrev, Lozenets and Triaditsa for us; Serdika, "
     "Poduyane, Krasna Polyana and Ilinden for Oborishte. Needs the centre beaten."),
    ("pact_housing_estates", "The Housing Estates", 0, 7, [["pact_old_quarters"]], [], 10,
     "duo:focus_collective_housing", P3a, P3,
     "The socialist housing estates: Iskar, Mladost and Studentski for us; Nadezhda and Lyulin for Oborishte. "
     "Needs the old quarters beaten."),
    ("pact_kremikovtsi", "The Steelworks of Kremikovtsi", 0, 8, [["pact_housing_estates"]], [], 7,
     "duo:goal_factory_complex", P4a, P4,
     "The industrial district goes to Oborishte; the steel goes to both. Needs the housing estates beaten."),
    ("pact_outskirts", "The Outskirts", 0, 9, [["pact_kremikovtsi"]], [], 10,
     "duo:goal_generic_territory_or_war", P5a, P5,
     "The villages and the mountains: Vitosha, Ovcha Kupel and Pancharevo for us; Vrabnitsa, Novi Iskar and Bankya "
     "for Oborishte. Needs Kremikovtsi beaten."),
    ("sofia_union", "The Union of North and South Sofia", 1, 10, [["pact_outskirts"]], [], 6,
     "duo:goal_generic_major_alliance", "{BEATEN:" + ",".join(OUTSKIRTS) + "}",
     """set_cosmetic_tag = SRD_SOUTH
OBR = { set_cosmetic_tag = OBR_NORTH }
dismantle_faction = yes
create_faction = EVIL_SOFIA_FACTION_SOFIA
add_to_faction = OBR
add_stability = 0.15
add_political_power = 200""",
     "Sofia is red from Boyana to Kremikovtsi. Sredets becomes South Sofia, Oborishte North Sofia, and the "
     "alliance takes the city's name: Sofia."),
    # alone: Sofia under Sredets alone, one group of districts at a time
    ("one_centre", "One Centre", 4, 5, [["destroy_anton"]], [], 8, "duo:Generic_Major_City", A1a, A1,
     "Vazrazhdane completes the centre. Cores and war goals."),
    ("united_old_quarters", "Take the Old Quarters", 4, 6, [["one_centre"]], [], 12, "duo:Generic_Urban_Warfare",
     A2a, A2, "Every district built before the war, from Krasno Selo to Ilinden. Needs the centre beaten."),
    ("united_housing_estates", "Take the Housing Estates", 4, 7, [["united_old_quarters"]], [], 12,
     "duo:goal_generic_build_housing", A3a, A3,
     "Nadezhda, Iskar, Mladost, Studentski and Lyulin. Needs the old quarters beaten."),
    ("united_kremikovtsi", "Take Kremikovtsi", 4, 8, [["united_housing_estates"]], [], 8, "duo:focus_generic_steel",
     A4a, A4 + "\nadd_political_power = 100", "The steelworks of Kremikovtsi. Needs the housing estates beaten."),
    ("united_outskirts", "Take the Outskirts", 4, 9, [["united_kremikovtsi"]], [], 12,
     "duo:goal_generic_more_territorial_claims", A5a, A5,
     "Vitosha, Ovcha Kupel, Vrabnitsa, Novi Iskar, Pancharevo and Bankya. Needs Kremikovtsi beaten."),
    ("sofia_commune", "The Sofia Commune", 3, 10, [["united_outskirts"]], [], 6, "duo:Generic_Hammer_Star",
     "{BEATEN:" + ",".join(OUTSKIRTS) + "}",
     "set_cosmetic_tag = SRD_SOFIA\nadd_stability = 0.20\nadd_political_power = 200",
     "One city, one party, one Victor Kolev. Sredets is now simply Sofia."),
    # the war at home, between both paths: manpower from the districts as they fall
    ("peoples_militia", "The People's Militia", 2, 6, [["pact_centre", "one_centre"]], [], 6,
     "duo:goal_integrate_the_militia", "",
     "add_ideas = SRD_peoples_militia\nadd_manpower = 15000",
     "Every block in the conquered districts sends ten men with red armbands. They will learn to shoot on the way."),
    ("komsomol_of_the_estates", "Komsomol of the Housing Estates", 2, 8,
     [["peoples_militia"], ["pact_housing_estates", "united_housing_estates"]], [], 7,
     "duo:SWI_Workers_Army", "",
     "add_ideas = SRD_komsomol\nadd_war_support = 0.05",
     "The kids of the panel blocks always wanted a reason to fight. Now they get badges as well."),
    # ------------------------------------------------------------------ the Party
    ("party_takes_the_largo", "The Party Takes the Largo", 7, 1, [["henrys_mom_was_right"]], [], 7,
     "duo:Generic_Revolutionary_Government", "",
     "add_political_power = 100\nadd_stability = 0.10",
     "The Party House on the Largo is ours again. The red flag goes up over the government quarter."),
    ("red_guards_of_the_stadium", "Red Guards of Vasil Levski Stadium", 6, 2, [["party_takes_the_largo"]], [], 9,
     "custom:stadium", "",
     'load_oob = "SRD_red_guards"\nadd_war_support = 0.05',
     "The national stadium becomes a drill ground. Four divisions of Red Guards march out of it."),
    ("arm_the_workers", "Arm the Workers", 6, 3, [["red_guards_of_the_stadium"]], [], 6,
     "duo:goal_integrate_workers_militia", "",
     """add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2000 }
add_tech_bonus = { name = SRD_arm_the_workers bonus = 0.5 uses = 1 category = infantry_weapons }""",
     "A rifle for every waiter, shop assistant and bus driver of the centre."),
    ("barricades_on_vitosha", "Barricades on Vitosha Boulevard", 6, 4, [["arm_the_workers"]], [], 10,
     "duo:Generic_Barricade", "",
     """capital_scope = {
	add_building_construction = { type = bunker level = 3 province = { all_provinces = yes limit_to_border = yes } instant_build = yes }
}""",
     "Café tables, tram rails and paving stones: Vitosha Boulevard becomes a fortress."),
    ("universal_service", "Every Comrade Serves", 8, 2, [["party_takes_the_largo"]], [], 5,
     "duo:goal_conscription", "",
     "add_ideas = SRD_universal_service\nadd_manpower = 25000",
     "From the Largo to the Lions' Bridge, every comrade between eighteen and sixty has a rifle number."),
    ("commissars_in_every_unit", "Commissars in Every Unit", 8, 3, [["universal_service"]], [], 8,
     "duo:Generic_Socialist_Soldier", "",
     "army_experience = 30\nadd_tech_bonus = { name = SRD_commissars_in_every_unit bonus = 1.0 uses = 1 category = land_doctrine }",
     "A Party man in every platoon, so the Red Guards never forget what they are fighting for."),
    ("red_air_over_the_centre", "Red Wings over the Centre", 8, 4, [["commissars_in_every_unit"]], [], 7,
     "duo:goal_air_red", "",
     """capital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }
air_experience = 25
add_tech_bonus = { name = SRD_red_air_over_the_centre bonus = 0.5 uses = 1 category = air_equipment }""",
     "Drones from the roof of TZUM, a runway down Tsar Osvoboditel Boulevard. The centre takes to the air."),
    ("metro_goes_to_war", "The Metro Goes to War", 7, 5, [["barricades_on_vitosha"], ["red_air_over_the_centre"]], [], 9,
     "duo:goal_anti_air", "",
     """capital_scope = {
	add_building_construction = { type = anti_air_building level = 3 instant_build = yes }
	add_building_construction = { type = infrastructure level = 1 instant_build = yes }
}
add_stability = 0.05""",
     "Serdika station becomes a shelter, the tunnels become supply lines, and anti-air guns go up on the roofs."),
    # ------------------------------------------------------------------ Daniel-Henry Capel
    ("red_leaflets", "Red Leaflets over Vitosha", 10, 1, [["henrys_mom_was_right"]], [], 3,
     "duo:Generic_Socialist_Propaganda", "VIT = { exists = yes }",
     "VIT = { add_stability = -0.10 add_popularity = { ideology = communism popularity = 0.15 } }",
     "Let Henry's mom find red leaflets in her own letterbox."),
    ("road_to_boyana", "The Road to Boyana", 10, 2, [["red_leaflets"]], [], 5,
     "duo:focus_generic_diplomatic_treaty", "LOZ = { exists = yes }",
     "LOZ = { country_event = { id = evil_sofia_srd.7 } }",
     "Sredets does not touch Vitosha, but Lozenets does. Lozenets will let our army through, or it will be "
     "the first to fall."),
    ("capel_question", "The Capel Question", 10, 3, [["road_to_boyana"]], [], 8,
     "person:capel_question", "VIT = { exists = yes }",
     "create_wargoal = { type = annex_everything target = VIT }\nadd_war_support = 0.05",
     "Daniel-Henry hates us. Daniel-Henry hates communism. Daniel-Henry has to go."),
    ("red_flag_over_boyana", "Red Flag over Boyana", 10, 4, [["capel_question"]], [], 4,
     "duo:goal_red_star_green_wreath", "controls_state = {VIT_CAP}",
     "{CORES:VIT}\nadd_political_power = 100\nadd_stability = 0.10",
     "The red flag flies over Boyana. Somewhere, Henry's mom is still saying she told everyone so."),
    # ------------------------------------------------------------------ the red economy of the centre
    ("collectivise_vitosha_boulevard", "Collectivise Vitosha Boulevard", 13, 1, [["henrys_mom_was_right"]], [], 10,
     "duo:Generic_Market_Socialism", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}""",
     "Every boutique on Vitosha Boulevard now belongs to the people. The people are very well dressed."),
    ("mimas_for_the_workers", "Mimas Döner for the Workers", 12, 2, [["collectivise_vitosha_boulevard"]], [], 4,
     "custom:doner", "", "add_ideas = SRD_mimas_doner",
     "Mimas never closes. Now it feeds the revolution, day and night."),
    ("party_arsenal", "The Party Arsenal", 14, 2, [["collectivise_vitosha_boulevard"]], [], 12,
     "duo:goal_generic_construct_mil_factory", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = arms_factory level = 2 instant_build = yes }
}""",
     "The back rooms of the centre's restaurants start making something other than food."),
    ("red_tourism", "Red Tourism", 12, 3, [["mimas_for_the_workers"]], [], 6, "duo:LEC_Passports", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}
add_political_power = 100""",
     "Tourists still come to the centre. Now they pay the Party."),
    ("red_university", "The Red University", 14, 3, [["party_arsenal"]], [], 9,
     "duo:focus_generic_socialist_science", "",
     "add_tech_bonus = { name = SRD_red_university bonus = 0.75 uses = 2 category = electronics }",
     "Sofia University stands in Sredets. Its professors now work for the Party, and the Party wants radios."),
    ("five_year_plan", "Five-Year Plan for the Centre", 13, 4, [["red_tourism"], ["red_university"]], [], 12,
     "duo:Generic_Factory_Planning", "",
     """capital_scope = {
	add_extra_state_shared_building_slots = 2
	add_building_construction = { type = industrial_complex level = 2 instant_build = yes }
}
add_tech_bonus = { name = SRD_five_year_plan bonus = 0.5 uses = 2 category = industry }""",
     "Five years, two more factories, and no more potholes. Probably."),
    ("star_on_the_party_house", "The Star on the Party House", 13, 5, [["five_year_plan"]], [], 10,
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

IDEAS = {  # key: (name, description, modifiers, icon: "custom:<key>" or (background, piece) from the GFX pack)
    "SRD_mimas_doner": ("Mimas Döner", "Mimas never closes. Nobody fights hungry in the centre.",
                        "stability_factor = 0.05\nwar_support_factor = 0.05\nconsumer_goods_factor = -0.05",
                        "custom:idea_doner"),
    "SRD_peoples_militia": ("The People's Militia", "Red armbands on every block of the conquered districts.",
                            "conscription = 0.01\narmy_defence_factor = 0.05", ("Army.png", "Rifles Crossed.png")),
    "SRD_komsomol": ("Komsomol of the Housing Estates", "The youth of the panel blocks marches for the Party.",
                     "conscription_factor = 0.10\npolitical_power_factor = 0.05", ("Rectangle.png", "Torch Gold.png")),
    "SRD_universal_service": ("Every Comrade Serves", "Every comrade between eighteen and sixty has a rifle number.",
                              "conscription = 0.02\nstability_factor = -0.02", ("Army.png", "Soldiers in Rows.png")),
}
RED_COUNTRIES = ["SRD", "OBR"]   # the countries that get a communist flag and a Commune name

OBR_GOES_RED = """set_popularities = { communism = 60 neutrality = 40 democratic = 0 fascism = 0 }
set_politics = { ruling_party = communism elections_allowed = no }
add_country_leader_role = {
	character = OBR_leader
	country_leader = { ideology = leninism expire = "2100.1.1.1" }
	promote_leader = yes
}
set_cosmetic_tag = OBR_RED"""

# The Oborishte Question: decisions for Sredets to push Oborishte's politics to the left.
DECISIONS = {
    "category": ("SRD_oborishte_question", "The Oborishte Question",
                 "Anton Zafirov's Oborishte stands between Sredets and a red centre. Push it to the left.",
                 "has_completed_focus = SRD_comrades_in_oborishte\nOBR = { exists = yes }"),
    "decisions": [
        ("SRD_fund_oborishte_communists", "Fund the Oborishte Communists", 50, 30,
         "OBR = { NOT = { has_government = communism } }",
         "OBR = { add_popularity = { ideology = communism popularity = 0.05 } }"),
        ("SRD_rally_at_the_doctors_garden", "Rally at the Doctor's Garden", 35, 45,
         "OBR = { NOT = { has_government = communism } }",
         "OBR = { add_popularity = { ideology = communism popularity = 0.04 } add_stability = -0.03 }"),
        ("SRD_red_coup_in_oborishte", "Red Coup in Oborishte", 100, 0,
         "has_completed_focus = SRD_red_newspapers_oborishte\nOBR = { NOT = { has_government = communism } communism > 0.55 }",
         "OBR = {\n" + "\n".join("\t" + ln for ln in OBR_GOES_RED.split("\n")) + "\n}\n"
         "OBR = { country_event = { id = evil_sofia_srd.8 } }"),
    ],
}

EVENTS = {
    "1": ("Henry's Mom Was Right",
          "Sredets has declared for communism. Daniel-Henry's mom has been saying it for years: the people of the "
          "centre are dirty communists. Daniel-Henry has never hated anyone as much as he hates Sredets now.",
          [("She was right all along. We will never forgive them.",
            "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }\n"
            "FROM = { country_event = { id = evil_sofia_srd.5 } }", 80),
           ("They must be stopped. Prepare for war!",
            "add_opinion_modifier = { target = FROM modifier = evil_sofia_dirty_communists }\n"
            "create_wargoal = { type = annex_everything target = FROM }\n"
            "FROM = { country_event = { id = evil_sofia_srd.6 } }", 20)]),
    "2": ("An Offer from Sredets",
          "Victor Kolev offers Anton Zafirov an alliance: a red centre, shared between Sredets and Oborishte. "
          "If Anton accepts, Oborishte turns communist and joins Sredets. If he refuses, Sredets will see it as war.",
          [("Comrades! The centre will be red together.",
            "if = {\n\tlimit = { NOT = { has_government = communism } }\n"
            + "\n".join("\t" + ln for ln in OBR_GOES_RED.split("\n")) + "\n}\n"
            "set_cosmetic_tag = OBR_RED\n"
            """FROM = {
	set_country_flag = SRD_anton_allied
	if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_RED_CENTRE }
	add_to_faction = OBR
	country_event = { id = evil_sofia_srd.3 }
}""", 70),
           ("Oborishte bows to no one.",
            "FROM = { create_wargoal = { type = annex_everything target = OBR } country_event = { id = evil_sofia_srd.4 } }",
            30)]),
    "3": ("Anton Says Yes",
          "Anton Zafirov has accepted. Oborishte is red, and it stands with Sredets. The North-South Pact can be drawn up.",
          [("Comrade Anton!", "", 1)]),
    "4": ("Anton Says No",
          "Anton Zafirov has refused our hand. So be it: Sredets now has a reason to march on Oborishte.",
          [("He will regret it.", "", 1)]),
    "5": ("Henry Hates Us",
          "Daniel-Henry Capel has heard the news. He hates Sredets, he hates communism, and his mom is telling "
          "everyone she was right.",
          [("Let him hate.", "", 1)]),
    "6": ("Henry Prepares for War",
          "Daniel-Henry Capel will not wait for the red flag to reach Boyana. Vitosha is preparing to attack us.",
          [("Let him come.", "add_war_support = 0.05", 1)]),
    "7": ("Sredets Asks for Passage",
          "Sredets wants to march its army through Lozenets to reach Vitosha. Refusing will make us its target.",
          [("Let them through.", "give_military_access = FROM\nFROM = { country_event = { id = evil_sofia_srd.9 } }", 60),
           ("Lozenets is not a road.",
            "FROM = { create_wargoal = { type = annex_everything target = LOZ } country_event = { id = evil_sofia_srd.10 } }",
            40)]),
    "8": ("A Red Coup in Oborishte",
          "Communists backed by Sredets have taken over Oborishte. Anton Zafirov now leads a red Oborishte.",
          [("Long live the revolution.", "", 1)]),
    "9": ("Lozenets Lets Us Through",
          "Lozenets has opened its streets to our army. The road to Boyana is open.",
          [("On to Boyana!", "", 1)]),
    "10": ("Lozenets Refuses",
           "Lozenets will not let our army through. Then the road to Boyana goes through Lozenets itself.",
           [("So be it.", "", 1)]),
}

TRAITS = {
    "evil_sofia_hates_communism": ("Hates Communism",
                                   "Daniel-Henry hates communism more than anything. His mom raised him well.",
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
FACTIONS = {"EVIL_SOFIA_RED_CENTRE": "The Red Centre", "EVIL_SOFIA_FACTION_SOFIA": "Sofia"}
