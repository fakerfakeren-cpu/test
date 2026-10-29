"""The Legionary Revolution: Lukov's Legions take power and must keep marching (Revolutionary Momentum).
One late split: Lukov's Axis Crusade (east, with Berlin) / Tsankov's Imperium (south and west, against everyone)."""
from focus_core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    tt, F, swap, court, momentum, ai_flag, INTEGRATION, transfer_if_allied, \
    F_POL, F_STAB, F_WS, F_IND, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, F_MILCHAR, F_POLCHAR
from focus_opening import CHANCELLERY_RULES
from focus_path_helpers import wargoal_states, wargoal_annex

B = "fascist"
F("bfx_fas_legions_march", 34, 5, "The Legions March",
  "General Hristo Lukov's Union of Bulgarian National Legions fills Sofia with torches and green shirts. Requires Legion influence of 40 or more in the Tsar's Balance. Rules out the Tsar's own path.",
  "country_event = bfx_fas.1", "GFX_focus_bfx_legions_march", B, prereq=["bfx_hour_of_decision"], excl=["bfx_tsar_steps_forward"],
  available="check_variable = { bfx_inf_legion > 39 }",
  ai="factor = 10\nmodifier = { factor = 10 has_country_flag = bfx_ai_fascist }\nmodifier = { factor = 0 is_ai = yes has_country_flag = bfx_ai_tsar }",
  filters=(F_POL, F_POLCHAR))

# ---------------- row 6: three columns of the revolution
F("bfx_fas_legionary_state", 30, 6, "The Legionary State",
  "The Tsar reigns; the Legion rules. Ministries, schools and police answer to the movement, and Sofia's diplomats may sign whatever the Legion likes.",
  "add_ideas = bfx_legionary_state\nrecruit_character = bfx_BUL_ivan_dochev\n" + court(legion=20, palace=-15) + "\n" + CHANCELLERY_RULES,
  "GFX_focus_bfx_legionary_state", B, prereq=["bfx_fas_legions_march"], filters=(F_POL, F_POLCHAR))
F("bfx_fas_revolution_must_march", 34, 6, "The Revolution Must March",
  "A movement that stops moving dies. Lukov's Legion lives on victories, enemies and parades. Starts Revolutionary Momentum: it grows at war, decays in peace, and can be spent on offensives, levies and purges.",
  ded("""
  set_country_flag = bfx_momentum_active
  set_variable = { bfx_momentum = 30 }
  add_dynamic_modifier = { modifier = bfx_legion_momentum }
  bfx_momentum_recalc = yes
  unlock_decision_category_tooltip = bfx_momentum_category
  """) + "\n" + tt("bfx_tt_momentum_start", "Starts §YRevolutionary Momentum§! at §Y30§!: §G+3§! a month at war, §R-3§! a month at peace. High momentum boosts attack, war support and conscription; above §Y90§! the revolution turns on itself, below §Y15§! it falls apart."),
  "GFX_focus_bfx_revolution_must_march", B, prereq=["bfx_fas_legions_march"], filters=(F_POL, F_WS))
F("bfx_fas_dobruja_ultimatum", 38, 6, "The Dobruja Ultimatum",
  "Not a request: a deadline. The owner of Southern Dobruja is told to hand it over; refusal means a war goal.",
  "add_state_claim = 77\nif = { limit = { NOT = { owns_state = 77 } 77 = { owner = { save_event_target_as = bfx_dobruja_owner } } } event_target:bfx_dobruja_owner = { country_event = { id = bfx_dip.6 days = 2 } } }\n" + momentum(5),
  "GFX_focus_BUL_free_balkan_states", B, prereq=["bfx_fas_legions_march"], filters=(F_ANNEX,))

# ---------------- the movement (x 28-32)
F("bfx_fas_purge_the_palace", 28, 7, "Purge the Palace",
  "Courtiers, Masonic bankers and the Tsar's tame ministers are shown the door. The Crown keeps its title and loses its teeth.",
  "add_political_power = 75\n" + swap("bfx_partyless_regime", "bfx_legionary_state").replace("add_ideas = bfx_legionary_state", "add_political_power = 25") + "\n" + court(palace=-20, legion=10) + "\n" + momentum(5),
  "GFX_goal_generic_political_pressure", B, prereq=["bfx_fas_legionary_state"], filters=(F_POL,))
F("bfx_fas_legionary_militia", 30, 7, "The Legionary Militia",
  "Party battalions guard bridges, hunt partisans and march very loudly.",
  "add_ideas = bfx_legionary_militia\nadd_manpower = 10000", "GFX_goal_generic_allies_build_infantry", B,
  prereq=["bfx_fas_legionary_state"], filters=(F_MAN,))
F("bfx_fas_brannik", 32, 7, "Found the Brannik",
  "The youth organisation of 1940, made compulsory. Every boy learns to march, shoot and sing.",
  "add_ideas = bfx_brannik", "GFX_focus_BUL_found_the_brannik", B, prereq=["bfx_fas_legionary_state"], filters=(F_MAN, F_WS))
F("bfx_fas_legionary_courts", 28, 8, "Legionary Courts",
  "People's tribunals for speculators, communists and anyone who laughed at the parade. Unlocks Revolutionary Tribunals (spend momentum for political power).",
  "add_stability = 0.05\nset_country_flag = bfx_tribunals_open\n" + tt("bfx_tt_tribunals", "Unlocks the §YRevolutionary Tribunals§! decision.") + "\n" + court(legion=5, palace=-5),
  "GFX_goal_generic_secret_weapon", B, prereq=["bfx_fas_purge_the_palace"], filters=(F_STAB, F_POL))
F("bfx_fas_arms_drive", 30, 8, "The Legion Arms Drive",
  "Every Legionary family buys a rifle bond. The Kazanlak works go to three shifts.",
  mil(1) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 1500 }", "GFX_goal_generic_construct_mil_factory", B,
  prereq=["bfx_fas_legionary_militia"], filters=(F_IND, F_ARMY))
F("bfx_fas_youth_battalions", 32, 8, "Brannik Battalions",
  "The oldest Brannik boys are formed into reserve battalions. Their mothers are not consulted.",
  "add_manpower = 15000\n" + momentum(5), "GFX_goal_generic_axis_build_infantry", B, prereq=["bfx_fas_brannik"], filters=(F_MAN,))
F("bfx_fas_cult_of_the_fallen", 28, 9, "The Cult of the Fallen",
  "Every Legionary who dies is read out at roll call: \"Present!\" Funerals become rallies and rallies become recruiting drives.",
  "add_war_support = 0.05\n" + momentum(10), "GFX_goal_generic_propaganda", B, prereq=["bfx_fas_legionary_courts"], filters=(F_WS,))
F("bfx_fas_shock_divisions", 30, 9, "Legionary Shock Divisions",
  "Picked volunteers, the best rifles and the newest guns, sent where the line must break.",
  "add_ideas = bfx_shock_divisions\narmy_experience = 15", "GFX_goal_generic_special_forces", B,
  prereq=["bfx_fas_arms_drive"], filters=(F_ARMY,))
F("bfx_fas_legion_war_economy", 32, 9, "The Legion's War Economy",
  "Wages frozen, strikes banned, profits capped, and two new arsenals in the Rhodopes.",
  mil(2), "GFX_goal_generic_production", B, prereq=["bfx_fas_arms_drive", "bfx_fas_youth_battalions"], filters=(F_IND,), kind="stat")
F("bfx_fas_the_new_man", 29, 10, "The New Bulgarian Man",
  "Disciplined, hard, devout and twenty-one. The Legion's ideal is on every poster and in every school.",
  "add_stability = 0.05\nadd_war_support = 0.05\n" + court(legion=10), "GFX_goal_generic_national_unity", B,
  prereq=["bfx_fas_cult_of_the_fallen", "bfx_fas_shock_divisions"], filters=(F_STAB, F_WS))
F("bfx_fas_total_mobilisation", 32, 10, "Total Mobilisation",
  "Every factory for the front, every family with someone in it.",
  "add_ideas = bfx_total_mobilisation", "GFX_goal_generic_production", B, prereq=["bfx_fas_legion_war_economy"], filters=(F_IND, F_MAN))

# ---------------- the wars of the revolution (x 34-36)
F("bfx_fas_blitz_plan", 34, 7, "Plan Struma",
  "The General Staff has a plan for every neighbour. The Legion has chosen the order.",
  "army_experience = 25\n" + momentum(5), "GFX_goal_generic_army_doctrines", B, prereq=["bfx_fas_revolution_must_march"], filters=(F_ARMY,))
F("bfx_fas_border_incidents", 36, 7, "Border Incidents",
  "Shots at a frontier post, a burned customs house, a dead shepherd, and a furious radio. Claims on Vardar Macedonia and Western Thrace. Unlocks Manufacture an Incident (gain momentum).",
  claim_states(106, 184) + "\nset_country_flag = bfx_incidents_open\n" + tt("bfx_tt_incidents", "Unlocks the §YManufacture an Incident§! decision.") + "\n" + momentum(10),
  "GFX_goal_generic_occupy_start_war", B, prereq=["bfx_fas_revolution_must_march"], filters=(F_ANNEX, F_WS))
F("bfx_fas_war_on_yugoslavia", 34, 8, "March on Skopje",
  "The Legion's first war: Vardar Macedonia, taken by force. War goal on its owner.",
  wargoal_states(106, [106]) + "\n" + court(army=10) + "\n" + momentum(10), "GFX_goal_generic_major_war", B,
  prereq=["bfx_fas_blitz_plan"], filters=(F_ANNEX, F_WS))
F("bfx_fas_war_on_greece", 36, 8, "Down the Struma Valley",
  "To Kavala and Salonika. War goal on the owner of Western Thrace for Thrace and Central Macedonia.",
  wargoal_states(184, [184, 731]) + "\n" + momentum(10), "GFX_goal_generic_territory_or_war", B,
  prereq=["bfx_fas_border_incidents"], filters=(F_ANNEX, F_WS))
F("bfx_fas_legionary_macedonia", 34, 9, "Legionary Macedonia",
  "Skopje's Legion headquarters opens on the day the army arrives. Core on Vardar Macedonia; unlocks Integration.",
  core_if_owned(106) + "\n106 = { add_compliance = 20 }\n" + INTEGRATION + "\n" + momentum(10), "GFX_focus_BUL_bulgarian_administration_of_the_balkans", B,
  prereq=["bfx_fas_war_on_yugoslavia"], available="owns_state = 106", filters=(F_ANNEX,))
F("bfx_fas_legionary_thrace", 36, 9, "Legionary Thrace",
  "Kavala, Drama and Xanthi get Bulgarian mayors and Legion choirs. Core on Western Thrace; unlocks Integration.",
  core_if_owned(184) + "\n184 = { add_compliance = 20 }\n" + dock(1) + "\n" + INTEGRATION, "GFX_goal_generic_occupy_states_coastal", B,
  prereq=["bfx_fas_war_on_greece"], available="owns_state = 184", filters=(F_ANNEX, F_NAVY))
F("bfx_fas_victory_parades", 35, 10, "Victory Parades",
  "Lukov rides down Tsar Osvoboditel Boulevard past captured guns. The Legion wants more of this.",
  "add_political_power = 75\nadd_war_support = 0.05\n" + momentum(10), "GFX_goal_generic_propaganda", B,
  prereq=[["bfx_fas_legionary_macedonia", "bfx_fas_legionary_thrace"]], filters=(F_WS,))

# ---------------- the new provinces (x 38-40)
F("bfx_fas_dobrujan_legion", 38, 7, "The Dobrujan Legion",
  "Refugees of 1913 return to Silistra and Dobrich in uniform. Core on Southern Dobrudja.",
  core_if_owned(77) + "\n77 = { add_compliance = 20 }\nadd_manpower = 8000", "GFX_focus_bfx_bessarabian_bulgars", B,
  prereq=["bfx_fas_dobruja_ultimatum"], available="owns_state = 77", filters=(F_ANNEX, F_MAN))
F("bfx_fas_legionary_prefects", 40, 7, "Legionary Prefects",
  "Every conquered district gets a prefect from the movement, a gendarmerie company and a quota of Bulgarian schools.",
  "add_ideas = bfx_legionary_prefects", "GFX_goal_generic_occupy_states_ongoing_war", B,
  prereq=["bfx_fas_dobruja_ultimatum"], filters=(F_STAB, F_ANNEX))
F("bfx_fas_settlers", 39, 8, "Soldier-Settlers",
  "Veterans get land in the new provinces, a rifle and a duty to keep both.",
  "every_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 10 }\nadd_manpower = 5000", "GFX_goal_generic_construct_infrastructure", B,
  prereq=[["bfx_fas_dobrujan_legion", "bfx_fas_legionary_prefects"]], filters=(F_STAB, F_MAN))
F("bfx_fas_requisitions", 39, 9, "Legionary Requisitions",
  "Grain, horses and lorries from every occupied district. Unlocks the Requisitions decision (spend momentum for equipment).",
  "set_country_flag = bfx_requisitions_open\n" + tt("bfx_tt_requisitions", "Unlocks the §YLegionary Requisitions§! decision.") + "\nadd_equipment_to_stockpile = { type = support_equipment amount = 300 }",
  "GFX_goal_generic_trade", B, prereq=["bfx_fas_settlers"], filters=(F_IND,))
F("bfx_fas_compliance_drive", 39, 10, "The Bulgarisation Drive",
  "New names on the street signs, new teachers in the schools, new priests in the churches.",
  "every_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 15 }\nadd_stability = -0.03", "GFX_goal_generic_national_unity", B,
  prereq=["bfx_fas_requisitions"], filters=(F_STAB, F_ANNEX))

# ---------------- the Legion's choice
F("bfx_fas_legion_destiny", 34, 11, "The Legion's Destiny",
  "Macedonia or Thrace is home, the factories are humming and the Legion is restless. East with Berlin against Bolshevism, or south and west against everyone who stands between Bulgaria and three seas?",
  "add_political_power = 100\n" + momentum(10), "GFX_focus_bfx_legions_march", B,
  prereq=["bfx_fas_victory_parades", ["bfx_fas_the_new_man", "bfx_fas_total_mobilisation", "bfx_fas_compliance_drive"]], filters=(F_POL,))

# =====================================================================================
# (B1) Lukov's Axis Crusade: Berlin's ally, the war in the East, the Black Sea
# =====================================================================================
F("bfx_fas_into_the_axis", 30, 12, "Into the Axis",
  "Lukov does not walk between raindrops; he walks into Berlin. Germany is asked to admit Bulgaria as a full ally; failing that, the Legion founds a Balkan Axis. Rules out Tsankov's Imperium.",
  "if = { limit = { is_in_faction = no country_exists = GER GER = { is_faction_leader = yes } } GER = { country_event = { id = bfx_dip.8 days = 2 } } }\nelse_if = { limit = { is_in_faction = no } create_faction = bfx_faction_balkan_axis }\nadd_ideas = bfx_axis_junior_partner",
  "GFX_focus_bfx_into_the_axis", B, prereq=["bfx_fas_legion_destiny"], excl=["bfx_fas_national_social_state"],
  ai=ai_flag("bfx_ai_fascist_axis", 20), filters=(F_POL,))
F("bfx_fas_anti_comintern", 28, 13, "The Anti-Comintern Bulwark",
  "The red menace is the second most important thing in Bulgaria, after Macedonia.",
  "add_ideas = bfx_anti_comintern\nif = { limit = { country_exists = GER } GER = { add_opinion_modifier = { target = ROOT modifier = bfx_om_axis_courtship } } }",
  "GFX_goal_anti_comintern_pact", B, prereq=["bfx_fas_into_the_axis"], filters=(F_POL, F_WS))
F("bfx_fas_german_instructors", 30, 13, "German Instructors",
  "Wehrmacht officers teach the army to fight the German way.",
  "add_ideas = bfx_german_instructors\narmy_experience = 20", "GFX_goal_generic_army_doctrines", B,
  prereq=["bfx_fas_into_the_axis"], filters=(F_ARMY,))
F("bfx_fas_axis_air_bases", 32, 13, "Axis Air Bases",
  "Luftwaffe squadrons at Plovdiv and Vrazhdebna, and Bulgarian pilots learning from them.",
  "capital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }\nair_experience = 25",
  "GFX_goal_generic_build_airforce", B, prereq=["bfx_fas_into_the_axis"], filters=(F_AIR,))
F("bfx_fas_new_order", 29, 14, "The New Order in the Balkans",
  "Whatever the Axis holds of the Bulgarian lands passes to Bulgarian administration. Unlocks Integration.",
  transfer_if_allied(106, 184, 731, 77) + "\n" + core_if_owned(106, 184) + "\n" + INTEGRATION,
  "GFX_focus_BUL_the_fate_of_the_balkans", B, prereq=["bfx_fas_anti_comintern", "bfx_fas_german_instructors"],
  available="OR = { date > 1941.4.1 any_state = { OR = { state = 106 state = 184 state = 731 state = 77 } NOT = { is_owned_by = ROOT } controller = { is_in_faction_with = ROOT } } }",
  filters=(F_ANNEX,))
F("bfx_fas_panzers_for_sofia", 32, 14, "Panzers for Sofia",
  "Maybach T-IVs and Sturmgeschütze for the 1st Armoured Brigade, paid for in tobacco.",
  "add_equipment_to_stockpile = { type = support_equipment amount = 200 }\n" + tech("bfx_fas_panzers_for_sofia", "armor", 0.5, 2),
  "GFX_goal_generic_army_tanks", B, prereq=["bfx_fas_axis_air_bases"], filters=(F_ARMY,))
F("bfx_fas_crusade_east", 28, 15, "Crusade in the East",
  "Lukov sends the Legion where Boris never would: across the Danube against the Soviets. Momentum grows faster while we fight the USSR.",
  "add_ideas = bfx_eastern_crusade\nset_country_flag = bfx_crusade_declared\nif = { limit = { country_exists = SOV NOT = { has_war_with = SOV } } declare_war_on = { target = SOV type = annex_everything } }\n" + court(legion=10) + "\n" + momentum(15),
  "GFX_focus_bfx_crusade_east", B, prereq=["bfx_fas_new_order"], available="GER = { has_war_with = SOV } is_in_faction_with = GER", filters=(F_WS,))
F("bfx_fas_legionary_greater_bulgaria", 30, 15, "Legionary Greater Bulgaria",
  "Cores on Dobrudja, Macedonia and Thrace where held; the state is proclaimed the Legionary State of Greater Bulgaria.",
  core_if_owned(77, 106, 184) + "\nset_cosmetic_tag = bfx_legionary_bulgaria\nadd_war_support = 0.05",
  "GFX_focus_bfx_greater_bulgaria", B, prereq=["bfx_fas_new_order"], available="OR = { owns_state = 106 owns_state = 184 }", filters=(F_ANNEX,))
F("bfx_fas_black_sea_squadron", 32, 15, "The Black Sea Squadron",
  "Torpedo boats from Varna to Odessa, under German command for now.",
  dock(1) + "\nnavy_experience = 20", "GFX_goal_generic_build_navy", B, prereq=["bfx_fas_panzers_for_sofia"], filters=(F_NAVY,))
F("bfx_fas_budjak", 27, 16, "The Budjak Bulgarians",
  "Bolgrad's Bulgarians have waited a century. Claims on Bessarabia and Northern Dobruja.",
  claims_on_cores_of("MOL") + "\n" + claim_states(971), "GFX_focus_bfx_bessarabian_bulgars", B, prereq=["bfx_fas_crusade_east"], filters=(F_ANNEX,))
F("bfx_fas_odessa_corridor", 29, 16, "The Odessa Corridor",
  "A Bulgarian zone on the Black Sea's northern shore. Claims on the Ukrainian coast.",
  "every_state = { limit = { is_core_of = UKR is_coastal = yes NOT = { is_claimed_by = ROOT } } add_claim_by = ROOT }",
  "GFX_goal_generic_occupy_states_coastal", B, prereq=["bfx_fas_crusade_east"], filters=(F_ANNEX,))
F("bfx_fas_aegean_fleet", 31, 16, "The Aegean Fleet",
  "Kavala and Alexandroupolis become naval bases.",
  dock(1) + "\nnavy_experience = 15", "GFX_goal_generic_navy_cruiser", B, prereq=["bfx_fas_legionary_greater_bulgaria", "bfx_fas_black_sea_squadron"], filters=(F_NAVY,))
F("bfx_fas_legionary_empire", 29, 17, "The Legionary Empire",
  "From the Danube delta to the Aegean, under one movement.",
  "add_ideas = bfx_imperial_mandate\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 10 }",
  "GFX_focus_BUL_the_third_bulgarian_empire", B, prereq=[["bfx_fas_budjak", "bfx_fas_odessa_corridor"], "bfx_fas_aegean_fleet"],
  filters=(F_STAB, F_ANNEX))
F("bfx_fas_thrace_to_bosporus", 28, 18, "Thrace to the Bosporus",
  "Claims on Edirne and Istanbul and a war goal on their owner.",
  claim_states(341, 797) + "\n" + wargoal_states(341, [341, 797]) + "\n" + momentum(10), "GFX_focus_BUL_supremacy_on_the_bosporus", B,
  prereq=["bfx_fas_legionary_empire"], filters=(F_ANNEX, F_WS))
F("bfx_fas_legion_of_st_george", 30, 18, "The Legion of St George",
  "Veterans of every campaign, organised as a shock corps.",
  "army_experience = 50\nadd_manpower = 25000", "GFX_goal_generic_special_forces", B, prereq=["bfx_fas_legionary_empire"], filters=(F_ARMY, F_MAN))
F("bfx_fas_new_bulgarian_order", 29, 19, "The New Bulgarian Order",
  "The Legion's Bulgaria is complete: big, armed, loud and very tired.",
  "add_stability = 0.10\nadd_political_power = 150\n" + core_if_owned(341) + "\n" + court(legion=10),
  "GFX_focus_bfx_new_bulgarian_order", B, prereq=["bfx_fas_thrace_to_bosporus", "bfx_fas_legion_of_st_george"], filters=(F_STAB,))

# =====================================================================================
# (B2) Tsankov's Imperium: fascist, answering to nobody; Hungary, Italy, the Straits
# =====================================================================================
F("bfx_fas_national_social_state", 38, 12, "The National Social State",
  "Aleksandar Tsankov's movement merges with the Legion: corporations, discipline and no orders from abroad. Rules out joining the Axis.",
  "add_ideas = bfx_national_social_economy\nrecruit_character = bfx_BUL_aleksandar_tsankov", "GFX_focus_bfx_iron_imperium", B,
  prereq=["bfx_fas_legion_destiny"], excl=["bfx_fas_into_the_axis"], ai=ai_flag("bfx_ai_fascist_imperium", 20), filters=(F_POL, F_IND))
F("bfx_fas_corporatist_economy", 36, 13, "The Corporations",
  "One corporation per trade, one chairman per corporation.",
  civ(1) + "\n" + mil(1), "GFX_goal_generic_construct_military", B, prereq=["bfx_fas_national_social_state"], filters=(F_IND,), kind="stat")
F("bfx_fas_pact_of_iron", 38, 13, "The Pact of Iron",
  "Revisionists of Europe, unite. A faction under Sofia; Hungary is invited.",
  "add_ideas = bfx_pact_of_iron\nif = { limit = { is_in_faction = no } create_faction = bfx_faction_pact_of_iron }\nif = { limit = { country_exists = HUN HUN = { is_in_faction = no } } HUN = { country_event = { id = bfx_dip.5 days = 2 } } }",
  "GFX_goal_generic_alliance", B, prereq=["bfx_fas_national_social_state"], available="OR = { is_in_faction = no is_faction_leader = yes }", filters=(F_POL,))
F("bfx_fas_rival_to_rome", 40, 13, "A Rival to Rome",
  "Mussolini wants the Balkans as an Italian lake. Tsankov wants it more. Claims on Albania.",
  claims_on_cores_of("ALB") + "\n" + momentum(5), "GFX_goal_generic_demand_territory", B,
  prereq=["bfx_fas_national_social_state"], filters=(F_ANNEX,))
F("bfx_fas_imperium_army", 36, 14, "The Army of the Imperium",
  "Songs about Samuil, and a modern interest in artillery.",
  "add_ideas = bfx_imperium_army\n" + tech("bfx_fas_imperium_army", "artillery", 0.5, 1), "GFX_goal_generic_army_artillery", B,
  prereq=["bfx_fas_corporatist_economy"], filters=(F_ARMY,))
F("bfx_fas_budapest_axis", 38, 14, "The Budapest-Sofia Axis",
  "Two revisionists, one plan: Romania and Yugoslavia between them.",
  "if = { limit = { country_exists = HUN } HUN = { add_opinion_modifier = { target = ROOT modifier = bfx_om_revisionist_brothers } } }\nif = { limit = { country_exists = HUN NOT = { has_war_with = HUN } } HUN = { country_event = { id = bfx_dip.1 days = 2 } } }",
  "GFX_goal_generic_improve_relations", B, prereq=["bfx_fas_pact_of_iron"], filters=(F_POL,))
F("bfx_fas_adriatic_ambitions", 40, 14, "Adriatic Ambitions",
  "Claims on the Montenegrin coast and a port for the Imperium.",
  claims_on_cores_of("MNT") + "\nnavy_experience = 15", "GFX_goal_generic_occupy_states_coastal", B,
  prereq=["bfx_fas_rival_to_rome"], filters=(F_ANNEX, F_NAVY))
F("bfx_fas_war_for_the_straits", 36, 15, "The War for the Straits",
  "Edirne and Istanbul. War goal on their owner.", claim_states(341, 797) + "\n" + wargoal_states(341, [341, 797]) + "\n" + momentum(10),
  "GFX_focus_BUL_supremacy_on_the_bosporus", B, prereq=["bfx_fas_imperium_army"], filters=(F_ANNEX, F_WS))
F("bfx_fas_war_for_the_danube", 38, 15, "The War for the Danube",
  "Both Dobrujas, with Hungary taking Transylvania. War goal on their owner.", claim_states(77, 971) + "\n" + wargoal_states(77, [77, 971]) + "\n" + momentum(10),
  "GFX_goal_generic_occupy_start_war", B, prereq=["bfx_fas_budapest_axis"], filters=(F_ANNEX, F_WS))
F("bfx_fas_war_for_albania", 40, 15, "The War for Albania",
  "Whoever holds Tirana, Rome or Zog, is told to leave. War goal to conquer Albania, or on the Italians who hold it.",
  ded("""
  if = { limit = { country_exists = ALB ALB = { is_subject = no } } """ + wargoal_annex("ALB") + """ }
  else_if = { limit = { country_exists = ITA any_state = { is_core_of = ALB is_owned_by = ITA } NOT = { has_war_with = ITA } } create_wargoal = { type = take_state_focus target = ITA generator = { 44 } } }
  """) + "\n" + momentum(10), "GFX_goal_generic_major_war", B, prereq=["bfx_fas_adriatic_ambitions"], filters=(F_ANNEX, F_WS))
F("bfx_fas_bulgarian_imperium", 37, 16, "The Bulgarian Imperium",
  "Cores on Dobrudja, Macedonia, Thrace and Edirne where held; the state becomes the Bulgarian Imperium.",
  core_if_owned(77, 106, 184, 341) + "\nset_cosmetic_tag = bfx_bulgarian_imperium\nadd_war_support = 0.05",
  "GFX_focus_bfx_iron_imperium", B, prereq=[["bfx_fas_war_for_the_straits", "bfx_fas_war_for_the_danube"]],
  available="OR = { owns_state = 77 owns_state = 341 owns_state = 971 }", filters=(F_ANNEX,))
F("bfx_fas_imperial_navy", 40, 16, "The Imperial Navy",
  "Two seas need two squadrons.", dock(2) + "\nnavy_experience = 25", "GFX_goal_generic_navy_battleship", B,
  prereq=["bfx_fas_war_for_albania"], filters=(F_NAVY,))
F("bfx_fas_settle_new_provinces", 36, 17, "Settle the New Provinces",
  "Veterans' land grants, Bulgarian schools and very firm prefects.",
  "every_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 15 }\nadd_manpower = 10000",
  "GFX_goal_generic_occupy_states_ongoing_war", B, prereq=["bfx_fas_bulgarian_imperium"], filters=(F_STAB, F_MAN))
F("bfx_fas_legions_of_the_imperium", 38, 17, "Legions of the Imperium",
  "Divisions recruited from every province of the new state.",
  "army_experience = 50\nadd_manpower = 20000", "GFX_goal_generic_axis_build_infantry", B, prereq=["bfx_fas_bulgarian_imperium"], filters=(F_ARMY, F_MAN))
F("bfx_fas_mediterranean_window", 40, 17, "A Window on the Mediterranean",
  "Claims on the Aegean islands; from Kavala to Rhodes is only a short sail.",
  claim_states(187) + "\nnavy_experience = 15", "GFX_goal_generic_navy_cruiser", B, prereq=["bfx_fas_imperial_navy"], filters=(F_ANNEX, F_NAVY))
F("bfx_fas_tsardom_of_three_seas", 38, 18, "The Imperium on Three Seas",
  "Black Sea, Aegean, Adriatic. Tsankov's dream, Lukov's army.",
  "add_ideas = bfx_imperial_mandate\nadd_stability = 0.10\nadd_political_power = 150",
  "GFX_focus_bfx_tsar_three_seas", B, prereq=["bfx_fas_legions_of_the_imperium", "bfx_fas_mediterranean_window"], filters=(F_STAB,))
