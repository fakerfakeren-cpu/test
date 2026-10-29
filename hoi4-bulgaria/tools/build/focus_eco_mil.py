"""Industry (incl. the nuclear programme) and the armed forces."""
from focus_core import ded, civ, mil, dock, tech, tt, neuilly, F, swap, court, INTEGRATION, \
    F_POL, F_STAB, F_WS, F_IND, F_RES, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, F_MILCHAR

NEUILLY_GONE = "has_country_flag = bfx_neuilly_ended"

# =====================================================================================
# INDUSTRY (42)
# =====================================================================================
B = "eco"
F("bfx_eco_rose_and_leaf", 48, 0, "The Rose and the Leaf",
  "Oriental tobacco from Plovdiv and rose oil from Kazanlak pay for almost everything Bulgaria imports. Two crops, one economy.",
  "add_political_power = 30\nset_country_flag = bfx_trade_question", "GFX_focus_bfx_eco_rose_and_leaf", B, cost=7, filters=(F_IND,), kind="stat")

F("bfx_eco_german_clearing", 42, 1, "The German Clearing Account",
  "Germany buys the whole crop, paid into a Berlin account that can only be spent in Germany. Strong, fast gains that tie the economy to Berlin. Rules out diversification.",
  "add_ideas = bfx_german_clearing\nif = { limit = { country_exists = GER } GER = { add_opinion_modifier = { target = ROOT modifier = bfx_om_axis_courtship } } }",
  "GFX_focus_bfx_eco_german_clearing", B, prereq=["bfx_eco_rose_and_leaf"], excl=["bfx_eco_diversify"], filters=(F_IND,),
  ai="factor = 20\nmodifier = { factor = 0.3 has_country_flag = bfx_ai_tsar_hegemon }")

F("bfx_eco_diversify", 44, 1, "Diversify the Buyers",
  "Sell to Britain, France, Czechoslovakia and anyone with hard currency. Slower, but nobody holds the purse strings. Rules out the German clearing.",
  "add_ideas = bfx_diversified_trade", "GFX_goal_generic_positive_trade_relations", B, prereq=["bfx_eco_rose_and_leaf"],
  excl=["bfx_eco_german_clearing"], filters=(F_IND, F_STAB), ai="factor = 10\nmodifier = { factor = 3 has_country_flag = bfx_ai_tsar_hegemon }")

F("bfx_eco_pernik_coal", 48, 1, "Pernik Coal",
  "The mines of Pernik heat Sofia, fuel the railways and feed the state steelworks.",
  "add_ideas = bfx_pernik_coal_works\ncapital_scope = { add_resource = { type = steel amount = 4 } }", "GFX_goal_generic_production", B,
  prereq=["bfx_eco_rose_and_leaf"], filters=(F_IND,))

F("bfx_eco_bdz", 52, 1, "Modernise the BDŽ",
  "The State Railways run on single track and the Tsar's enthusiasm. Every state gets better roads and rails.",
  "every_owned_state = { limit = { is_controlled_by = ROOT } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }\nadd_ideas = bfx_railway_age",
  "GFX_goal_generic_construct_infrastructure", B, prereq=["bfx_eco_rose_and_leaf"], filters=(F_IND,))

F("bfx_eco_sofia_university", 55, 1, "Sofia University Institutes",
  "Laboratories, scholarships and a new physics building.",
  tech("bfx_eco_sofia_university", "electronics", 0.5, 1) + "\n" + tech("bfx_eco_sofia_university_i", "industry", 0.5, 1),
  "GFX_goal_generic_scientific_exchange", B, prereq=["bfx_eco_rose_and_leaf"], filters=(F_RES,))

F("bfx_eco_tobacco_boom", 43, 2, "The Plovdiv Tobacco Boom",
  "Warehouses the size of cathedrals and a tobacco workers' union with opinions.",
  swap("bfx_tobacco_monoculture", "bfx_tobacco_and_rose_exports"), "GFX_goal_generic_trade", B,
  prereq=[["bfx_eco_german_clearing", "bfx_eco_diversify"]], filters=(F_IND, F_POL))

F("bfx_eco_balkan_iron", 47, 2, "Iron from the Balkan Range",
  "Poor ore near Kremikovtsi, but ours.",
  swap("bfx_pernik_coal_works", "bfx_pernik_coal_works_2") + "\ncapital_scope = { add_resource = { type = steel amount = 4 } }",
  "GFX_goal_generic_construct_military", B, prereq=["bfx_eco_pernik_coal"], filters=(F_IND,))

F("bfx_eco_electrification", 49, 2, "Electrify the Plain",
  "Power lines across Thrace. Factories that ran on daylight run on shifts.",
  "add_ideas = bfx_electrification\n" + civ(1), "GFX_goal_generic_construction2", B, prereq=["bfx_eco_pernik_coal"], filters=(F_IND,))

F("bfx_eco_main_line", 52, 2, "The Sofia–Varna Main Line",
  "Double track from the capital to the sea.",
  swap("bfx_railway_age", "bfx_railway_age_2") + "\n" + civ(1), "GFX_focus_NOR_build_the_northern_rail", B, prereq=["bfx_eco_bdz"], filters=(F_IND,))

F("bfx_eco_nadjakov_laboratory", 55, 2, "Nadjakov's Laboratory",
  "In 1937 Georgi Nadjakov discovered the photoelectret effect in Sofia. Give him a proper laboratory.",
  tech("bfx_eco_nadjakov_laboratory", "electronics", 0.5, 2), "GFX_focus_bfx_atom", B, prereq=["bfx_eco_sofia_university"], filters=(F_RES,))

F("bfx_eco_valley_of_roses", 43, 3, "The Valley of Roses",
  "Kazanlak supplies most of the world's attar of roses. Paris pays in gold.",
  swap("bfx_tobacco_and_rose_exports", "bfx_valley_of_roses") + "\nif = { limit = { country_exists = FRA } FRA = { add_opinion_modifier = { target = ROOT modifier = bfx_om_rose_trade } } }",
  "GFX_goal_generic_consumer_goods", B, prereq=["bfx_eco_tobacco_boom"], filters=(F_STAB, F_POL))

F("bfx_eco_kremikovtsi_steel", 47, 3, "The Kremikovtsi Steelworks",
  "Twenty years before the real one, and twice as smoky.",
  mil(1) + "\ncapital_scope = { add_resource = { type = steel amount = 4 } }", "GFX_goal_generic_construct_mil_factory", B,
  prereq=["bfx_eco_balkan_iron"], filters=(F_IND,))

F("bfx_eco_iskar_dams", 49, 3, "Dams on the Iskar",
  "Hydroelectric power from the gorge through the Balkan range.",
  swap("bfx_electrification", "bfx_iskar_hydro"), "GFX_goal_generic_construction", B, prereq=["bfx_eco_electrification"], filters=(F_IND,))

F("bfx_eco_danube_ports", 51, 3, "The Danube Ports",
  "Ruse, Svishtov and Lom: river ports for the barges of Central Europe.",
  civ(1) + "\n" + tech("bfx_eco_danube_ports", "industry", 0.3, 1), "GFX_goal_generic_trade", B, prereq=["bfx_eco_main_line"], filters=(F_IND,))

F("bfx_eco_black_sea_ports", 53, 3, "Ports of Varna and Burgas",
  "Deepen the harbours and add the slipways a navy will want.",
  dock(2), "GFX_goal_generic_construct_naval_dockyard", B, prereq=["bfx_eco_main_line"], filters=(F_IND, F_NAVY))

F("bfx_eco_bukhovo_uranium", 55, 3, "The Bukhovo Deposits",
  "Geologists have found uranium ore at Bukhovo, near Sofia. After 1945 the Soviets mined it for their own bomb. It could be ours first.",
  "capital_scope = { add_extra_state_shared_building_slots = 1 }\n" + tech("bfx_eco_bukhovo_uranium", "nuclear", 0.5, 1),
  "GFX_focus_bfx_bukhovo_uranium", B, prereq=["bfx_eco_nadjakov_laboratory"], available="date > 1938.1.1", filters=(F_RES,))

F("bfx_eco_hard_currency", 43, 4, "Hard Currency for Machines",
  "Rose gold and tobacco marks buy lathes from Pilsen and turbines from Zurich.",
  civ(1), "GFX_goal_generic_construct_civ_factory", B, prereq=["bfx_eco_valley_of_roses"], filters=(F_IND,), kind="stat")

F("bfx_eco_kazanlak_arsenal", 46, 4, "The Kazanlak Arsenal",
  "The State Military Factory has made shells and pretended to make tractors since 1924. It can stop pretending.",
  mil(1) + "\n" + tech("bfx_eco_kazanlak_arsenal", "artillery", 0.5, 1), "GFX_goal_generic_army_artillery2", B,
  prereq=["bfx_eco_kremikovtsi_steel"], filters=(F_IND,))

F("bfx_eco_sopot_works", 48, 4, "The Sopot Rifle Works",
  "A rifle works in the Valley of Roses, out of reach of any bomber's map.",
  mil(1) + "\n" + tech("bfx_eco_sopot_works", "infantry_weapons", 0.5, 1), "GFX_goal_generic_small_arms", B,
  prereq=["bfx_eco_kremikovtsi_steel"], filters=(F_IND,))

F("bfx_eco_hydro_grid", 50, 4, "The National Grid",
  "One grid from Vidin to Burgas, fed by the Iskar and the Arda.",
  civ(1) + "\nadd_tech_bonus = { name = bfx_eco_hydro_grid bonus = 0.5 uses = 1 category = industry }", "GFX_goal_generic_construction2", B,
  prereq=["bfx_eco_iskar_dams"], filters=(F_IND,))

F("bfx_eco_labour_brigades", 53, 4, "The Labour Service Brigades",
  "Stamboliyski's compulsory labour service: young men with shovels build roads, dams and, quietly, earthworks.",
  "add_ideas = bfx_trudovaks\n" + neuilly(6, 3), "GFX_goal_generic_construction", B, prereq=["bfx_eco_black_sea_ports"], filters=(F_IND, F_MAN))

F("bfx_eco_atomic_commission", 55, 4, "The Atomic Commission",
  "A committee, a budget, a guard at the door and a very short list of visitors.",
  "add_ideas = bfx_atomic_commission\n" + tech("bfx_eco_atomic_commission", "nuclear", 0.5, 1), "GFX_focus_bfx_atom", B,
  prereq=["bfx_eco_bukhovo_uranium"], available="date > 1940.1.1", filters=(F_RES,))

F("bfx_eco_ledger_of_trade", 43, 5, "The Ledger of Trade",
  "Settle accounts: break free of Berlin, bind tighter, or open the books to the world.",
  "country_event = bfx.10", "GFX_goal_generic_dangerous_deal", B, prereq=["bfx_eco_hard_currency"], filters=(F_IND, F_POL))

F("bfx_eco_state_arsenals", 47, 5, "The State Arsenals",
  "Kazanlak, Sopot and Bozhurishte under one directorate.",
  "add_ideas = bfx_state_arsenals", "GFX_goal_generic_production2", B, prereq=["bfx_eco_kazanlak_arsenal", "bfx_eco_sopot_works"], filters=(F_IND,))

F("bfx_eco_chemical_combine", 50, 5, "The Chemical Combine",
  "Fertiliser in peacetime, explosives in war, and a smell over Stara Zagora that never quite leaves.",
  "add_ideas = bfx_chemical_industry\n" + civ(1), "GFX_goal_generic_oil_refinery", B, prereq=["bfx_eco_hydro_grid"], filters=(F_IND,))

F("bfx_eco_road_network", 53, 5, "The Trans-Balkan Roads",
  "Paved passes through Shipka, Petrohan and the Rhodopes.",
  "every_owned_state = { limit = { is_controlled_by = ROOT is_core_of = ROOT } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }",
  "GFX_goal_generic_construct_infrastructure", B, prereq=["bfx_eco_labour_brigades"], filters=(F_IND,))

F("bfx_eco_reactor_project", 55, 5, "The Reactor Project",
  "Graphite, uranium and a great deal of optimism in a valley outside Sofia.",
  tech("bfx_eco_reactor_project", "nuclear", 1.0, 1), "GFX_focus_bfx_nuclear_plant", B,
  prereq=["bfx_eco_atomic_commission"], available="date > 1941.6.1", filters=(F_RES,))

F("bfx_eco_plovdiv_fair", 42, 6, "The Plovdiv International Fair",
  "Every September the world's salesmen come to Plovdiv. This year they bring patents.",
  tech("bfx_eco_plovdiv_fair", "industry", 0.5, 2), "GFX_goal_generic_scientific_exchange", B, prereq=["bfx_eco_ledger_of_trade"], filters=(F_RES,))

F("bfx_eco_export_drive", 44, 6, "The Export Drive",
  "Tobacco, roses, grain, wine and more tobacco: everything that sells, sold.",
  civ(1) + "\nadd_political_power = 50", "GFX_goal_generic_trade", B, prereq=["bfx_eco_ledger_of_trade"], filters=(F_IND,))

F("bfx_eco_war_economy", 47, 6, "The War Economy",
  "Quotas, ration cards and a War Production Board run by men who used to sell tobacco.",
  "add_ideas = bfx_war_economy\n" + mil(1), "GFX_goal_generic_production", B, prereq=["bfx_eco_state_arsenals"], filters=(F_IND,))

F("bfx_eco_tyulenovo_oil", 49, 6, "Petroleum at Tyulenovo",
  "There is oil on the Dobrujan coast, found for real in 1951. If we hold Dobrudja we find it now; if not, coal becomes fuel the hard way.",
  "if = { limit = { owns_state = 77 } 77 = { add_resource = { type = oil amount = 8 } } }\nelse = { capital_scope = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = synthetic_refinery level = 1 instant_build = yes } } }",
  "GFX_goal_generic_oil_refinery", B, prereq=["bfx_eco_chemical_combine"], filters=(F_IND,))

F("bfx_eco_synthetic_fuel", 51, 6, "Synthetic Fuel from Lignite",
  "Bulgarian lignite is poor coal but good enough to cook into petrol.",
  "capital_scope = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = synthetic_refinery level = 1 instant_build = yes } }\n" + tech("bfx_eco_synthetic_fuel", "synth_resources", 0.5, 1),
  "GFX_goal_generic_oil_refinery", B, prereq=["bfx_eco_chemical_combine"], filters=(F_IND,))

F("bfx_eco_kozloduy_reactor", 55, 6, "The Kozloduy Pile",
  "A reactor on the Danube, thirty years before the real Kozloduy.",
  "capital_scope = { add_building_construction = { type = nuclear_reactor level = 1 instant_build = yes } }",
  "GFX_focus_bfx_nuclear_plant", B, prereq=["bfx_eco_reactor_project"], available="date > 1942.1.1", filters=(F_RES, F_IND))

F("bfx_eco_national_bank", 43, 7, "Reform the National Bank",
  "Stabilise the lev, consolidate the debts and print enough money to pay for all this, but not too much.",
  "add_stability = 0.05\nadd_political_power = 75", "GFX_goal_generic_positive_trade_relations", B,
  prereq=["bfx_eco_plovdiv_fair", "bfx_eco_export_drive"], filters=(F_STAB,), kind="stat")

F("bfx_eco_industrial_ring", 46, 7, "The Sofia Industrial Ring",
  "Tram works, textile mills and assembly halls around the capital.",
  civ(2), "GFX_goal_generic_construct_civilian", B, prereq=["bfx_eco_war_economy"], filters=(F_IND,), kind="stat")

F("bfx_eco_dispersed_industry", 48, 7, "Dispersed Industry",
  "Workshops in the valleys, depots in the caves.",
  "add_ideas = bfx_dispersed_industry\n" + mil(1), "GFX_goal_generic_construct_mil_factory", B, prereq=["bfx_eco_war_economy"], filters=(F_IND,))

F("bfx_eco_fuel_reserves", 50, 7, "Strategic Fuel Reserves",
  "Tanks under the hills of Burgas for a war that will not wait for tankers.",
  "capital_scope = { add_building_construction = { type = fuel_silo level = 1 instant_build = yes } }\nadd_tech_bonus = { name = bfx_eco_fuel_reserves bonus = 0.5 uses = 1 category = synth_resources }",
  "GFX_goal_generic_oil_refinery", B, prereq=["bfx_eco_tyulenovo_oil", "bfx_eco_synthetic_fuel"], filters=(F_IND,))

F("bfx_eco_rila_device", 55, 7, "The Rila Device",
  "A bomb assembled in a monastery workshop under the Rila peaks. Nobody believes Bulgaria could build one. That is the point.",
  tech("bfx_eco_rila_device", "nuclear", 1.0, 2) + "\nadd_war_support = 0.05", "GFX_focus_bfx_rila_device", B,
  prereq=["bfx_eco_kozloduy_reactor"], available="date > 1944.1.1", filters=(F_RES,))

F("bfx_eco_academy_of_sciences", 44, 8, "The Academy of Sciences",
  "The Academy's institutes stop arguing about Old Church Slavonic long enough to study ballistics.",
  "add_research_slot = 1", "GFX_goal_generic_scientific_exchange", B, prereq=["bfx_eco_national_bank"],
  available="date > 1938.1.1", filters=(F_RES,))

F("bfx_eco_total_war_production", 47, 8, "Total War Production",
  "Every lathe in the kingdom turned to the war.",
  mil(2), "GFX_goal_generic_construct_military", B, prereq=["bfx_eco_industrial_ring", "bfx_eco_dispersed_industry"],
  available="has_war = yes", filters=(F_IND,), kind="stat")

# =====================================================================================
# MILITARY (50): army doctrine 11, equipment 8, manpower 9, navy 10, air 11 + root
# =====================================================================================
B = "mil"
F("bfx_mil_neuilly_army", 67, 0, "The Army Neuilly Built",
  "Twenty thousand volunteers, no conscripts, no tanks, no planes and one very bored General Staff.",
  "army_experience = 10\n" + neuilly(5, 2) + "\n" + court(army=5), "GFX_goal_generic_army_doctrines", B, cost=7, filters=(F_ARMY,))

# ---- doctrine
F("bfx_mil_rhodope_rangers", 58, 1, "Rhodope Rangers",
  "Mountain troops trained on Musala, Vihren and smugglers' paths.",
  "add_ideas = bfx_mountain_army\n" + tech("bfx_mil_rhodope_rangers", "mountaineers_tech", 0.75, 1), "GFX_focus_AFG_mountain_training", B,
  prereq=["bfx_mil_neuilly_army"], filters=(F_ARMY,))

F("bfx_mil_chataldzha_lessons", 60, 1, "Lessons of Chataldzha",
  "1912: the army charged entrenched Turks and lost a generation in an afternoon.",
  "add_mastery_bonus = { bonus = 0.20 days = 365 name = bfx_mil_chataldzha_lessons folder = land }\narmy_experience = 15",
  "GFX_goal_generic_army_doctrines", B, prereq=["bfx_mil_neuilly_army"], filters=(F_ARMY,))

F("bfx_mil_mountain_doctrine", 58, 2, "Balkan Mountain Doctrine",
  "Hold the passes, move along the ridges.", swap("bfx_mountain_army", "bfx_balkan_mountain_doctrine"),
  "GFX_goal_generic_special_forces", B, prereq=["bfx_mil_rhodope_rangers"], filters=(F_ARMY,))

F("bfx_mil_staff_academy", 60, 2, "The General Staff Academy",
  "Officers who can tell a staff map from a tobacco ledger. General Lukash takes the Chief of Staff's chair.",
  "add_ideas = bfx_general_staff_academy\nrecruit_character = bfx_BUL_konstantin_lukash", "GFX_goal_generic_position_armies", B,
  prereq=["bfx_mil_chataldzha_lessons"], filters=(F_ARMY, F_MILCHAR))

F("bfx_mil_mountain_brigades", 58, 3, "The Mountain Brigades",
  "Mule companies, pack artillery and radio sets that weigh less than a goat.",
  tech("bfx_mil_mountain_brigades", "mountaineers_tech", 0.5, 1) + "\narmy_experience = 15", "GFX_focus_AFG_mountain_training", B,
  prereq=["bfx_mil_mountain_doctrine"], filters=(F_ARMY,))

F("bfx_mil_bayonet_tradition", 60, 3, "The Bayonet Tradition",
  "Lozengrad, Bulair, Doiran: the infantry's reputation was made at bayonet point.",
  "add_ideas = bfx_bayonet_tradition", "GFX_goal_generic_small_arms", B, prereq=["bfx_mil_staff_academy"], filters=(F_ARMY,))

F("bfx_mil_balkan_war_plan", 59, 4, "The Balkan War Plan",
  "Five fronts, one army. The staff has planned for every neighbour, one at a time.",
  "army_experience = 25\nrecruit_character = bfx_BUL_teodosi_daskalov", "GFX_goal_generic_position_armies", B,
  prereq=["bfx_mil_mountain_brigades", "bfx_mil_bayonet_tradition"], filters=(F_ARMY, F_MILCHAR))

F("bfx_mil_officer_corps", 58, 5, "Expand the Officer Corps",
  "Reserve officers' schools in every garrison town.",
  "army_experience = 20\nrecruit_character = bfx_BUL_vladimir_zaimov", "GFX_goal_generic_army_doctrines", B,
  prereq=["bfx_mil_balkan_war_plan"], filters=(F_ARMY, F_MILCHAR))

F("bfx_mil_combined_arms", 60, 5, "Combined Arms",
  "Infantry, guns and the first tanks, trained to fight together.",
  "add_mastery_bonus = { bonus = 0.20 days = 365 name = bfx_mil_combined_arms folder = land }", "GFX_goal_generic_army_tanks", B,
  prereq=["bfx_mil_balkan_war_plan"], filters=(F_ARMY,))

F("bfx_mil_royal_guard", 58, 6, "The Royal Guard Division",
  "The Tsar's Guard, expanded into a full division and given the best of everything.",
  "add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 }\narmy_experience = 15\n" + court(palace=5, army=5),
  "GFX_goal_generic_special_forces", B, prereq=["bfx_mil_officer_corps"], filters=(F_ARMY,))

F("bfx_mil_armoured_brigade", 60, 6, "The Armoured Brigade",
  "Czech tanks in 1940, German ones in 1943: Bulgaria's first armoured brigade.",
  tech("bfx_mil_armoured_brigade", "armor", 0.5, 1) + "\n" + tech("bfx_mil_armoured_motor", "motorized_equipment", 0.5, 1),
  "GFX_goal_generic_build_tank", B, prereq=["bfx_mil_combined_arms"], available=NEUILLY_GONE, filters=(F_ARMY,))

F("bfx_mil_mountain_blitz", 59, 7, "Blitzkrieg in the Mountains",
  "Tanks on the valley roads, rangers on the ridges.",
  "add_mastery_bonus = { bonus = 0.25 days = 365 name = bfx_mil_mountain_blitz folder = land }\narmy_experience = 25",
  "GFX_goal_generic_army_motorized", B, prereq=["bfx_mil_royal_guard", "bfx_mil_armoured_brigade"], filters=(F_ARMY,))

# ---- equipment
F("bfx_mil_small_arms", 63, 1, "Small Arms Standardisation",
  "Mannlichers, Mausers, Berthiers and Mosins: four calibres is three too many.",
  tech("bfx_mil_small_arms", "infantry_weapons", 0.5, 1), "GFX_goal_generic_small_arms", B, prereq=["bfx_mil_neuilly_army"], filters=(F_ARMY,), kind="stat")

F("bfx_mil_mountain_guns", 62, 2, "Mountain Guns",
  "Skoda pack howitzers that break down onto four mules.",
  tech("bfx_mil_mountain_guns", "artillery", 0.5, 1), "GFX_goal_generic_army_artillery", B, prereq=["bfx_mil_small_arms"], filters=(F_ARMY,), kind="stat")

F("bfx_mil_machine_guns", 64, 2, "The Machine-Gun Companies",
  "A machine-gun company per battalion.",
  "add_equipment_to_stockpile = { type = infantry_equipment amount = 1000 }\n" + tech("bfx_mil_machine_guns", "infantry_weapons", 0.5, 1),
  "GFX_goal_generic_small_arms", B, prereq=["bfx_mil_small_arms"], filters=(F_ARMY,))

F("bfx_mil_rifle_contracts", 62, 3, "The Mauser Contracts",
  "Rifles from Oberndorf, paid in tobacco.",
  "add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }", "GFX_goal_generic_military_deal", B,
  prereq=["bfx_mil_mountain_guns"], filters=(F_ARMY,))

F("bfx_mil_anti_tank", 64, 3, "Anti-Tank Companies",
  "Every neighbour will have tanks. The infantry must be able to stop them.",
  tech("bfx_mil_anti_tank", "artillery", 0.5, 1) + "\narmy_experience = 10", "GFX_goal_generic_army_artillery2", B,
  prereq=["bfx_mil_machine_guns"], filters=(F_ARMY,))

F("bfx_mil_field_artillery", 63, 4, "The Field Artillery Regiments",
  "One regiment per division, horse-drawn but punctual.",
  "add_equipment_to_stockpile = { type = artillery_equipment amount = 150 }\n" + tech("bfx_mil_field_artillery", "artillery", 0.5, 1),
  "GFX_goal_generic_army_artillery", B, prereq=["bfx_mil_rifle_contracts", "bfx_mil_anti_tank"], filters=(F_ARMY,))

F("bfx_mil_support_companies", 63, 5, "Support Companies",
  "Engineers, signals and recon for every division.",
  tech("bfx_mil_support_companies", "support_tech", 0.5, 2), "GFX_goal_generic_army_doctrines", B, prereq=["bfx_mil_field_artillery"], filters=(F_ARMY,))

F("bfx_mil_supply_columns", 63, 6, "The Supply Columns",
  "Trucks, carts and mules, all numbered and all accounted for.",
  tech("bfx_mil_supply_columns", "motorized_equipment", 0.5, 1) + "\nadd_equipment_to_stockpile = { type = support_equipment amount = 300 }",
  "GFX_goal_generic_army_motorized", B, prereq=["bfx_mil_support_companies"], filters=(F_ARMY,))

# ---- manpower
F("bfx_mil_reservists", 67, 1, "The Reservist Associations",
  "Veterans' clubs keep rifles oiled and records current.",
  "add_ideas = bfx_reservist_associations\nadd_manpower = 5000\n" + neuilly(4, 2), "GFX_goal_generic_allies_build_infantry", B,
  prereq=["bfx_mil_neuilly_army"], filters=(F_MAN,))

F("bfx_mil_macedonian_emigration", 66, 2, "Volunteers of the Emigration",
  "Half a million Macedonian refugees live in Bulgaria. Their sons volunteer.",
  "add_manpower = 12000\n" + court(imro=5), "GFX_focus_BUL_support_macedonian_organizations", B, prereq=["bfx_mil_reservists"], filters=(F_MAN,), kind="stat")

F("bfx_mil_pomak_battalions", 68, 2, "The Rhodope Battalions",
  "Mountain villagers who know every path in the Rhodopes.",
  "add_manpower = 8000\n" + tech("bfx_mil_pomak_battalions", "mountaineers_tech", 0.25, 1), "GFX_goal_generic_special_forces", B,
  prereq=["bfx_mil_reservists"], filters=(F_MAN,))

F("bfx_mil_veterans_1912", 66, 3, "Veterans of the Balkan Wars",
  "The sergeants of Lozengrad train their grandsons.",
  "add_ideas = bfx_veterans_of_1912", "GFX_goal_generic_army_doctrines", B, prereq=["bfx_mil_macedonian_emigration"], filters=(F_ARMY,))

F("bfx_mil_womens_auxiliary", 68, 3, "The Women's Auxiliary",
  "Nurses, signallers and munitions workers.",
  "add_ideas = bfx_womens_auxiliary", "GFX_goal_generic_construct_civilian", B, prereq=["bfx_mil_pomak_battalions"], filters=(F_MAN, F_IND))

F("bfx_mil_universal_service", 67, 4, "Universal Service, Openly",
  "Conscription returns, legally and on the front page. Only possible once the military clauses of Neuilly are gone.",
  "add_manpower = 25000\nadd_ideas = bfx_open_conscription", "GFX_goal_generic_allies_build_infantry", B,
  prereq=["bfx_mil_veterans_1912", "bfx_mil_womens_auxiliary"], available=NEUILLY_GONE, filters=(F_MAN,))

F("bfx_mil_mobilisation_law", 66, 5, "The Mobilisation Law",
  "Every man knows his depot, his unit and his train.",
  "add_manpower = 15000\narmy_experience = 10", "GFX_goal_generic_position_armies", B, prereq=["bfx_mil_universal_service"], filters=(F_MAN,), kind="stat")

F("bfx_mil_training_camps", 68, 5, "Training Camps in the Rhodopes",
  "Six weeks of mountain marches, then the front.",
  tech("bfx_mil_training_camps", "infantry_weapons", 0.25, 1) + "\narmy_experience = 15\nadd_manpower = 5000",
  "GFX_goal_generic_special_forces", B, prereq=["bfx_mil_universal_service"], filters=(F_ARMY,))

F("bfx_mil_national_army", 67, 6, "The National Army",
  "Universal service, regional depots, standing reserves: the army Neuilly forbade, built in full.",
  "add_ideas = bfx_national_army", "GFX_goal_generic_axis_build_infantry", B, prereq=["bfx_mil_mobilisation_law", "bfx_mil_training_camps"], filters=(F_MAN, F_ARMY))

# ---- navy
F("bfx_nav_black_sea_flotilla", 71, 1, "The Black Sea Flotilla",
  "Four torpedo boats and some police launches. The commander has been told to think big.",
  "add_ideas = bfx_black_sea_flotilla\nnavy_experience = 10", "GFX_goal_generic_build_navy", B, prereq=["bfx_mil_neuilly_army"], filters=(F_NAVY,))

F("bfx_nav_varna_naval_school", 70, 2, "The Varna Naval School",
  "Officers for a navy that does not yet exist.", "navy_experience = 15\n" + dock(1), "GFX_goal_generic_navy_doctrines_tactics", B,
  prereq=["bfx_nav_black_sea_flotilla"], filters=(F_NAVY,))

F("bfx_nav_danube_flotilla", 72, 2, "The Danube Flotilla",
  "River monitors and patrol boats from Vidin to Silistra.", "navy_experience = 10\n" + dock(1), "GFX_goal_generic_navy_anti_submarine", B,
  prereq=["bfx_nav_black_sea_flotilla"], filters=(F_NAVY,))

F("bfx_nav_torpedo_squadrons", 70, 3, "Torpedo Boat Squadrons",
  "Small, fast and cheap: the only naval doctrine a poor Black Sea power can afford.",
  swap("bfx_black_sea_flotilla", "bfx_black_sea_fleet") + "\n" + neuilly(4, 3), "GFX_goal_generic_navy_submarine", B,
  prereq=["bfx_nav_varna_naval_school"], filters=(F_NAVY,))

F("bfx_nav_minelayers", 72, 3, "The Varna Minefields",
  "If Bulgaria cannot sink a battleship with guns, a mine will do.", "add_ideas = bfx_minefields", "GFX_goal_generic_navy_anti_submarine", B,
  prereq=["bfx_nav_danube_flotilla"], filters=(F_NAVY,))

F("bfx_nav_coastal_batteries", 70, 4, "Coastal Batteries at Galata",
  "Guns on the cliffs above Varna and Burgas.",
  "every_owned_state = { limit = { is_controlled_by = ROOT is_coastal = yes } add_building_construction = { type = coastal_bunker level = 2 instant_build = yes province = { all_provinces = yes limit_to_coastal = yes } } }",
  "GFX_goal_generic_defence", B, prereq=["bfx_nav_torpedo_squadrons"], filters=(F_NAVY,))

F("bfx_nav_naval_aviation", 72, 4, "Naval Aviation",
  "Seaplanes from Varna to watch the approaches.", "air_experience = 10\nnavy_experience = 10", "GFX_goal_generic_air_naval_bomber", B,
  prereq=["bfx_nav_minelayers"], filters=(F_NAVY, F_AIR))

F("bfx_nav_black_sea_raiders", 71, 5, "Black Sea Raiders",
  "Small boats, long nights and big torpedoes.", "add_ideas = bfx_black_sea_raiders\nnavy_experience = 20", "GFX_goal_generic_wolf_pack", B,
  prereq=["bfx_nav_coastal_batteries", "bfx_nav_naval_aviation"], filters=(F_NAVY,))

F("bfx_nav_submarine_flotilla", 70, 6, "The Submarine Flotilla",
  "Article 83 forbade submarines. Article 83 is no longer read.", dock(1) + "\nnavy_experience = 20", "GFX_goal_generic_navy_submarine", B,
  prereq=["bfx_nav_black_sea_raiders"], available=NEUILLY_GONE, filters=(F_NAVY,))

F("bfx_nav_destroyer_squadron", 72, 6, "The Destroyer Squadron",
  "Four modern destroyers ordered abroad: the Black Sea's smallest real navy.", dock(1) + "\nnavy_experience = 20", "GFX_goal_generic_navy_cruiser", B,
  prereq=["bfx_nav_black_sea_raiders"], available=NEUILLY_GONE, filters=(F_NAVY,))

# ---- air
F("bfx_air_aero_clubs", 75, 1, "Aero Clubs and Gliders",
  "Neuilly banned military aviation; nobody banned enthusiastic young men with gliders.",
  "add_ideas = bfx_clandestine_aviation\nair_experience = 10\n" + neuilly(6, 3), "GFX_focus_bfx_air_aero_clubs", B,
  prereq=["bfx_mil_neuilly_army"], filters=(F_AIR,))

F("bfx_air_dar_works", 74, 2, "The DAR Works at Bozhurishte",
  "The State Aircraft Workshops build trainers and things that are definitely not reconnaissance aircraft.",
  mil(1) + "\nair_experience = 10", "GFX_goal_generic_air_production", B, prereq=["bfx_air_aero_clubs"], filters=(F_AIR, F_IND))

F("bfx_air_polish_fighters", 76, 2, "PZL Fighters from Warsaw",
  "In 1937 Bulgaria bought Polish PZL P.24 fighters. A real air force needs real fighters.",
  "air_experience = 20", "GFX_goal_generic_air_fighter", B, prereq=["bfx_air_aero_clubs"], filters=(F_AIR,), kind="stat")

F("bfx_air_avia_biplanes", 74, 3, "Avia Biplanes from Prague",
  "Czech Avia B-534s, the best biplanes in Europe, bought cheaply in 1939.",
  "air_experience = 15", "GFX_goal_generic_air_fighter2", B, prereq=["bfx_air_dar_works"], filters=(F_AIR,), kind="stat")

F("bfx_air_foreign_instructors", 76, 3, "Foreign Instructors",
  "Germans, Italians and Poles teach formation flying.", "add_ideas = bfx_foreign_air_instructors\nair_experience = 15", "GFX_goal_generic_air_doctrine", B,
  prereq=["bfx_air_polish_fighters"], filters=(F_AIR,))

F("bfx_air_vazdushni_voyski", 75, 4, "Proclaim the Vazdushni Voyski",
  "His Majesty's Air Force exists, officially. Only possible once the military clauses of Neuilly are gone.",
  swap("bfx_clandestine_aviation", "bfx_vazdushni_voyski") + "\ncapital_scope = { add_building_construction = { type = air_base level = 3 instant_build = yes } }\nrecruit_character = bfx_BUL_stoyan_stoyanov",
  "GFX_goal_expand_the_luftwaffe", B, prereq=["bfx_air_avia_biplanes", "bfx_air_foreign_instructors"], available=NEUILLY_GONE, filters=(F_AIR,))

F("bfx_air_fighter_regiment", 74, 5, "The Fighter Regiment",
  "Defend Sofia's skies.", "add_ideas = bfx_sofia_air_defence\nair_experience = 15", "GFX_goal_generic_air_fighter", B,
  prereq=["bfx_air_vazdushni_voyski"], filters=(F_AIR,))

F("bfx_air_dornier_bombers", 76, 5, "Dornier Bombers",
  "Do 17s from Germany, the first Bulgarian bombers since 1918.", "air_experience = 20\n" + tech("bfx_air_dornier_bombers", "industry", 0.25, 1),
  "GFX_goal_generic_air_bomber", B, prereq=["bfx_air_vazdushni_voyski"], filters=(F_AIR,))

F("bfx_air_sofia_flak", 74, 6, "Flak over Sofia",
  "Guns on the hills around the capital.", "capital_scope = { add_building_construction = { type = anti_air_building level = 3 instant_build = yes } }",
  "GFX_goal_generic_radar", B, prereq=["bfx_air_fighter_regiment"], filters=(F_AIR,))

F("bfx_air_wings_over_mountains", 76, 6, "Wings over the Mountains",
  "Close air support where artillery cannot follow.", "add_ideas = bfx_wings_over_the_mountains", "GFX_goal_generic_CAS", B,
  prereq=["bfx_air_dornier_bombers"], filters=(F_AIR,))

F("bfx_air_paratroopers", 75, 7, "The Parachute Battalion",
  "Bulgaria's paratroopers, formed in 1943, jump into the mountains behind the enemy.",
  tech("bfx_air_paratroopers", "para_tech", 0.5, 1) + "\narmy_experience = 15", "GFX_focus_bfx_parachute", B,
  prereq=["bfx_air_sofia_flak", "bfx_air_wings_over_mountains"], filters=(F_AIR, F_ARMY))
