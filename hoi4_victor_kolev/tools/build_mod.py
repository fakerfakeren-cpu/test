"""Generates the Victor Kolev (Bulgaria) HOI4 mod's focus tree, ideas, events,
characters, on_actions and English localisation, and validates the tree.

Run from anywhere:  python3 tools/build_mod.py
Output goes to ../mod/victor_kolev/
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "mod" / "victor_kolev"
TAG = "BUL"
LEADER = "BUL_victor_kolev"
P = "BUL_kv_"  # id prefix

# Vanilla states Bulgaria owns at the 1936 start (used only for resource deposits).
BUL_STATES = [48, 211, 212, 801]

# --------------------------------------------------------------------------
# Effect helpers
# --------------------------------------------------------------------------

def _build(btype, n, level=1, extra_limit="", slot=True, size=1):
    block = f"""random_owned_controlled_state = {{
\tlimit = {{ {extra_limit} free_building_slots = {{ building = {btype} size > {size} include_locked = yes }} }}
\t{"add_extra_state_shared_building_slots = 1" if slot else ""}
\tadd_building_construction = {{ type = {btype} level = {level} instant_build = yes }}
}}"""
    return "\n".join([block] * n)


def civ(n):
    return _build("industrial_complex", n)


def mil(n):
    return _build("arms_factory", n)


def dock(n):
    return _build("dockyard", n, extra_limit="is_coastal = yes")


def infra(n):
    return "\n".join([f"""random_owned_controlled_state = {{
\tlimit = {{ free_building_slots = {{ building = infrastructure size > 0 }} }}
\tadd_building_construction = {{ type = infrastructure level = 1 instant_build = yes }}
}}"""] * n)


def capital_build(btype, level):
    return f"capital_scope = {{ add_building_construction = {{ type = {btype} level = {level} instant_build = yes }} }}"


def tech(fid, category, uses=1, bonus=0.5):
    return f"add_tech_bonus = {{ name = {fid} bonus = {bonus} uses = {uses} category = {category} }}"


def resource(rtype, amount, state):
    return f"add_resource = {{ type = {rtype} amount = {amount} state = {state} }}"


def pp(n):
    return f"add_political_power = {n}"


def stab(v):
    return f"add_stability = {v}"


def ws(v):
    return f"add_war_support = {v}"


def pop(ideology, v):
    return f"add_popularity = {{ ideology = {ideology} popularity = {v} }}"


def idea(name):
    return f"add_ideas = {P}{name}"


def remove(name):
    return f"remove_ideas = {P}{name}"


def swap(old, new):
    return f"swap_ideas = {{ remove_idea = {P}{old} add_idea = {P}{new} }}"


def set_gov(ideology, elections):
    return (f"set_politics = {{ ruling_party = {ideology} elections_allowed = {elections} }}\n"
            f"promote_character = {LEADER}")


def join_faction_of(tag):
    return f"{tag} = {{ add_to_faction = ROOT }}"


def invite_neighbours(extra=""):
    return f"""every_neighbor_country = {{
\tlimit = {{ is_in_faction = no is_major = no {extra} }}
\tcountry_event = {{ id = kolev.20 days = 1 }}
}}"""


def friendship_neighbours():
    return """every_neighbor_country = {
\tadd_opinion_modifier = { target = ROOT modifier = BUL_kv_balkan_friendship }
\tROOT = { add_opinion_modifier = { target = PREV modifier = BUL_kv_balkan_friendship } }
}"""


CLAIM_EFFECT = """every_state = {
\tlimit = {
\t\tNOT = { is_owned_by = ROOT }
\t\tany_neighbor_state = { is_owned_by = ROOT }
\t\tOR = {
\t\t\tAND = { is_owned_by = ROM is_coastal = yes }
\t\t\tis_owned_by = GRE
\t\t\tAND = { is_owned_by = YUG any_neighbor_state = { is_owned_by = GRE } }
\t\t}
\t}
\tadd_claim_by = ROOT
}"""


def demand(target):
    return f"{target} = {{ country_event = {{ id = kolev.10 days = 1 }} }}"


def demand_available(target):
    return (f"country_exists = {target}\nhas_war = no\n"
            f"{target} = {{ any_owned_state = {{ is_claimed_by = ROOT }} }}")


def J(*parts):
    return "\n".join(p for p in parts if p)


# --------------------------------------------------------------------------
# Focus data
# --------------------------------------------------------------------------
FOCUSES = []


def F(fid, x, y, icon, name, desc, reward, pre=(), mx=(), cost=10, available="",
      bypass="", ai=1, filters=("FOCUS_FILTER_POLITICAL",), ai_mods=""):
    FOCUSES.append(dict(id=P + fid, x=x, y=y, icon="GFX_" + icon, name=name, desc=desc,
                        reward=reward, pre=[[P + p for p in grp] if isinstance(grp, (list, tuple))
                                            else [P + grp] for grp in pre],
                        mx=[P + m for m in mx], cost=cost, available=available,
                        bypass=bypass, ai=ai, filters=filters, ai_mods=ai_mods))


IND = ("FOCUS_FILTER_INDUSTRY",)
RES = ("FOCUS_FILTER_RESEARCH",)
ARMY = ("FOCUS_FILTER_ARMY_XP",)
AIR = ("FOCUS_FILTER_AIR_XP",)
NAVY = ("FOCUS_FILTER_NAVY_XP",)
STAB = ("FOCUS_FILTER_STABILITY",)
WS = ("FOCUS_FILTER_WAR_SUPPORT",)
ANNEX = ("FOCUS_FILTER_ANNEXATION",)
MP = ("FOCUS_FILTER_MANPOWER",)

# ======================= MILITARY: ARMY (x 0-6) ==========================
F("defy_neuilly", 4, 0, "goal_generic_army_doctrines", "Defy the Treaty of Neuilly",
  "The victors of the Great War chained our army with a treaty written in Paris. Chairman Kolev has made it clear: Bulgaria will no longer apologise for defending itself.",
  J(remove("shadow_of_neuilly"), ws(0.05), "army_experience = 10"), filters=WS)
F("shield_of_the_balkans", 2, 1, "goal_generic_small_arms", "Shield of the Balkans",
  "A modern rifle in the hands of every Bulgarian soldier.",
  tech(P + "shield_of_the_balkans", "infantry_weapons", 1, 0.5), pre=["defy_neuilly"], filters=RES)
F("danube_artillery", 5, 1, "goal_generic_army_artillery", "Danube Artillery Corps",
  "The guns of the Danube line must be able to answer any challenger across the river.",
  tech(P + "danube_artillery", "artillery", 1, 0.5), pre=["defy_neuilly"], filters=RES)
F("rhodope_mountaineers", 1, 2, "goal_generic_special_forces", "Rhodope Mountaineers",
  "Our southern mountains breed hardy men. Let them form the core of an elite mountain corps.",
  J("army_experience = 15", tech(P + "rhodope_mountaineers", "support_tech", 1, 0.5)),
  pre=["shield_of_the_balkans"], filters=ARMY)
F("rearm_the_army", 3, 2, "goal_generic_allies_build_infantry", "Rearm the Army",
  "The depots are half empty. The Chairman has ordered them filled.",
  J("add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2000 producer = BUL }",
    "add_equipment_to_stockpile = { type = support_equipment_1 amount = 200 producer = BUL }"),
  pre=["shield_of_the_balkans"], filters=ARMY)
F("motorize_the_army", 5, 2, "goal_generic_army_motorized", "Motorize the Army",
  "Horses and ox-carts will not win the next war.",
  tech(P + "motorize_the_army", "motorized_equipment", 1, 0.5), pre=["danube_artillery"], filters=RES)
F("lessons_of_the_balkan_wars", 2, 3, "goal_generic_army_doctrines", "Lessons of the Balkan Wars",
  "Twice in a generation we won battles and lost the peace. Our officers will study why.",
  tech(P + "lessons_of_the_balkan_wars", "land_doctrine", 1, 0.5),
  pre=[["rhodope_mountaineers", "rearm_the_army"]], filters=RES)
F("bulgarian_armour", 5, 3, "goal_generic_army_tanks", "Bulgarian Armour",
  "Even a small nation can field a fist of steel.",
  tech(P + "bulgarian_armour", "armor", 2, 0.5), pre=["motorize_the_army"], filters=RES)
F("conscription_reform", 1, 4, "goal_generic_allies_build_infantry", "Conscription Reform",
  "A fairer, wider draft that reaches every village from Vidin to Burgas.",
  idea("conscription_reform"), pre=["lessons_of_the_balkan_wars"], filters=MP)
F("officer_academy", 3, 4, "goal_generic_army_doctrines", "The Sofia Officer Academy",
  "Kolev wants officers who think, not just officers who obey.",
  idea("officer_academy"), pre=["lessons_of_the_balkan_wars"], filters=ARMY)
F("tank_school", 5, 4, "goal_generic_army_tanks", "The Tank School at Kazanlak",
  "Our first armoured crews will be trained in the Valley of Roses.",
  J(tech(P + "tank_school", "armor", 1, 0.5), "army_experience = 10"), pre=["bulgarian_armour"], filters=RES)
F("special_detachments", 0, 5, "goal_generic_special_forces", "Special Detachments",
  "Small, fast, deadly. The Chairman's raiders.",
  J(tech(P + "special_detachments", "support_tech", 1, 0.5), "army_experience = 10"),
  pre=["conscription_reform"], filters=RES)
F("border_fortifications", 2, 5, "goal_generic_defence", "Fortify the Frontiers",
  "Every pass and every river crossing will cost an invader dearly.",
  idea("border_forts"), pre=["conscription_reform"], filters=ARMY)
F("mechanized_divisions", 5, 5, "goal_generic_army_motorized", "Mechanized Divisions",
  "Infantry that keeps pace with the tanks.",
  J(tech(P + "mechanized_divisions", "motorized_equipment", 1, 0.5), tech(P + "mechanized_divisions", "armor", 1, 0.5)),
  pre=["tank_school"], filters=RES)
F("balkan_war_doctrine", 3, 6, "goal_generic_army_doctrines", "A Balkan Way of War",
  "Doctrine written for our mountains, our rivers and our means.",
  tech(P + "balkan_war_doctrine", "land_doctrine", 2, 0.5),
  pre=[["border_fortifications", "officer_academy"]], filters=RES)
F("concentrated_firepower", 5, 6, "goal_generic_army_artillery2", "Concentrated Firepower",
  "Mass the guns, break the line.",
  tech(P + "concentrated_firepower", "artillery", 2, 0.5), pre=["mechanized_divisions"], filters=RES)
F("army_of_the_chairman", 4, 7, "goal_generic_position_armies", "The Army of the Chairman",
  "A modern army, loyal to the nation and its Chairman. Bulgaria will never again be the battlefield of others.",
  J("army_experience = 25", ws(0.05), tech(P + "army_of_the_chairman", "land_doctrine", 1, 0.5)),
  pre=["balkan_war_doctrine", "concentrated_firepower"], filters=ARMY)

# ======================= MILITARY: AIR (x 7-9) ===========================
F("air_corps", 8, 0, "goal_generic_build_airforce", "The Bulgarian Air Corps",
  "Neuilly forbade us an air force. We are building one anyway.",
  J("air_experience = 25", capital_build("air_base", 2)), filters=AIR)
F("fighter_programme", 7, 1, "goal_generic_air_fighter", "Fighter Programme",
  "Guard the skies over Sofia.", tech(P + "fighter_programme", "air_equipment", 1, 0.5),
  pre=["air_corps"], filters=RES)
F("close_air_support", 9, 1, "goal_generic_air_bomber", "Close Air Support",
  "Aircraft that fight alongside our infantry.", tech(P + "close_air_support", "air_equipment", 1, 0.5),
  pre=["air_corps"], filters=RES)
F("bozhurishte_works", 8, 2, "goal_generic_air_production", "The Bozhurishte Aircraft Works",
  "Bulgarian aircraft, built by Bulgarian hands.",
  J(mil(1), tech(P + "bozhurishte_works", "air_equipment", 1, 0.5)),
  pre=[["fighter_programme", "close_air_support"]], filters=IND)
F("air_doctrine", 7, 3, "goal_generic_air_doctrine", "Doctrine of the Skies",
  "How a small air force punches above its weight.", tech(P + "air_doctrine", "air_doctrine", 2, 0.5),
  pre=["bozhurishte_works"], filters=RES)
F("radar_network", 9, 3, "goal_generic_radar", "Early Warning Network",
  "No bomber will reach Sofia unannounced.",
  J(tech(P + "radar_network", "electronics", 1, 0.5), capital_build("radar_station", 1)),
  pre=["bozhurishte_works"], filters=RES)
F("air_defence", 7, 4, "goal_generic_air_fighter", "Air Defence of the Cities",
  "Anti-aircraft batteries for our industrial centres.",
  J(capital_build("anti_air_building", 2), "air_experience = 10"), pre=["air_doctrine"], filters=AIR)
F("aces_of_the_balkans", 9, 4, "goal_generic_air_fighter", "Aces of the Balkans",
  "Every nation needs heroes in the sky.", "air_experience = 30", pre=["radar_network"], filters=AIR)
F("wings_over_sofia", 8, 5, "goal_generic_air_production", "Wings over Sofia",
  "Bulgaria has an air force worthy of the name.",
  J("air_experience = 25", tech(P + "wings_over_sofia", "air_equipment", 2, 0.5)),
  pre=["air_defence", "aces_of_the_balkans"], filters=AIR)

# ======================= MILITARY: NAVY (x 0-3, y 9+) ====================
F("black_sea_fleet", 2, 9, "goal_generic_build_navy", "The Black Sea Fleet",
  "Varna and Burgas are our windows to the world. They must be defended.",
  J("navy_experience = 25", dock(1)), filters=NAVY)
F("varna_shipyards", 1, 10, "goal_generic_construct_naval_dockyard", "The Varna Shipyards",
  "Expand the yards so we no longer buy our ships from foreigners.", dock(2),
  pre=["black_sea_fleet"], filters=IND)
F("submarine_flotilla", 3, 10, "goal_generic_navy_submarine", "Submarine Flotilla",
  "The Black Sea is narrow. Submarines make it narrower for our enemies.",
  tech(P + "submarine_flotilla", "naval_equipment", 1, 0.5), pre=["black_sea_fleet"], filters=RES)
F("coastal_defence", 1, 11, "goal_generic_navy_doctrines_tactics", "Coastal Defence Doctrine",
  "Mines, torpedo boats and shore guns.", tech(P + "coastal_defence", "naval_doctrine", 1, 0.5),
  pre=["varna_shipyards"], filters=RES)
F("torpedo_boats", 3, 11, "goal_generic_navy_cruiser", "Fast Torpedo Boats",
  "Cheap, quick and dangerous.", tech(P + "torpedo_boats", "naval_equipment", 1, 0.5),
  pre=["submarine_flotilla"], filters=RES)
F("masters_of_the_black_sea", 2, 12, "goal_generic_navy_battleship", "Masters of the Western Black Sea",
  "From the Danube delta to the Bosporus, no one sails without our leave.",
  J("navy_experience = 50", tech(P + "masters_of_the_black_sea", "naval_doctrine", 1, 0.5)),
  pre=["coastal_defence", "torpedo_boats"], filters=NAVY)

# ======================= ECONOMY (x 11-18) ===============================
F("economic_council", 15, 0, "goal_generic_production", "The Economic Council of Sofia",
  "Kolev's first decree: an economic council of engineers and economists, not courtiers.",
  pp(50), cost=5, filters=IND)
F("infrastructure_drive", 13, 1, "goal_generic_construct_infrastructure", "National Infrastructure Drive",
  "Roads and rails before anything else.", infra(2), pre=["economic_council"], filters=IND)
F("agrarian_reform", 17, 1, "goal_generic_consumer_goods", "Agrarian Reform",
  "Eight in ten Bulgarians work the land. Their lives must improve before anything else can.",
  swap("agrarian_economy", "agrarian_economy_2"), pre=["economic_council"], filters=IND)
F("sofia_industrial_zone", 12, 2, "goal_generic_construct_civ_factory", "The Sofia Industrial Zone",
  "A new industrial belt around the capital.", civ(2), pre=["infrastructure_drive"], filters=IND)
F("danube_railways", 14, 2, "goal_generic_construct_infrastructure", "Railways to the Danube",
  "Link Ruse and Vidin to the heart of the country.", J(infra(2), stab(0.02)),
  pre=["infrastructure_drive"], filters=IND)
F("cooperative_farms", 17, 2, "goal_generic_consumer_goods", "Cooperative Farms",
  "Pool land, tools and credit. Let the village feed the factory.", J(stab(0.03), "add_manpower = 5000"),
  pre=["agrarian_reform"], filters=STAB)
F("kazanlak_arms_works", 12, 3, "goal_generic_construct_mil_factory", "The Kazanlak Arms Works",
  "Expand the state arsenal at Kazanlak.", mil(2), pre=["sofia_industrial_zone"], filters=IND)
F("danube_ports", 14, 3, "goal_generic_construct_naval_dockyard", "The Danube Ports",
  "River trade is the cheapest trade.", J(dock(1), infra(1)), pre=["danube_railways"], filters=IND)
F("mechanized_agriculture", 17, 3, "goal_generic_production2", "Mechanized Agriculture",
  "Tractors free hands for the factories.", J(remove("agrarian_economy_2"), civ(1)),
  pre=["cooperative_farms"], filters=IND)
F("research_institute", 11, 4, "goal_generic_scientific_exchange", "The Bulgarian Academy of Technology",
  "The Chairman believes Bulgaria's future is decided in laboratories.",
  "add_research_slot = 1", pre=["sofia_industrial_zone"], filters=RES)
F("expand_the_arsenal", 13, 4, "goal_generic_construct_mil_factory", "Expand the Arsenal",
  "More rifles, more shells, more guns.", mil(2), pre=["kazanlak_arms_works"], filters=IND)
F("survey_the_rhodopes", 16, 4, "goal_generic_production2", "Survey the Rhodopes",
  "Geologists report the mountains are richer than anyone thought.",
  J(pp(25), tech(P + "survey_the_rhodopes", "industry", 1, 0.25)),
  pre=[["danube_ports", "mechanized_agriculture"]], filters=RES)
F("technical_schools", 11, 5, "goal_generic_research", "Technical Schools",
  "A generation of Bulgarian engineers.", tech(P + "technical_schools", "industry", 2, 0.5),
  pre=["research_institute"], filters=RES)
F("electrification", 13, 5, "goal_generic_radar", "Electrification of the Countryside",
  "Light in every village by 1945.", tech(P + "electrification", "electronics", 1, 0.5),
  pre=["expand_the_arsenal"], filters=RES)
F("rhodope_mines", 15, 5, "goal_generic_production", "Rhodope Chromium Mines",
  "Chromium for Bulgarian steel.", resource("chromium", 6, BUL_STATES[0]),
  pre=["survey_the_rhodopes"], filters=IND)
F("pernik_steel", 17, 5, "goal_generic_production", "Pernik Steel",
  "The coal of Pernik fires the furnaces of a new Bulgaria.", resource("steel", 8, BUL_STATES[3]),
  pre=["survey_the_rhodopes"], filters=IND)
F("first_kolev_plan", 12, 6, "goal_generic_construct_civ_factory", "The First Kolev Plan",
  "Five years. Concrete targets. No excuses.", civ(2),
  pre=["technical_schools", "electrification"], filters=IND)
F("synthetic_fuel", 15, 6, "goal_generic_secret_weapon", "Synthetic Fuel Programme",
  "We have no oil fields. Then we shall make our own oil.",
  J(tech(P + "synthetic_fuel", "synth_resources", 1, 0.75), resource("oil", 4, BUL_STATES[2])),
  pre=["rhodope_mines"], filters=RES)
F("tobacco_exports", 17, 6, "goal_generic_trade", "Bulgarian Tobacco Exports",
  "Bulgarian tobacco is smoked from Berlin to New York. Let it pay for our factories.",
  idea("tobacco_exports"), pre=["pernik_steel"], filters=IND)
F("sofia_university", 11, 7, "goal_generic_scientific_exchange", "Expand Sofia University",
  "Double the faculties, double the minds.", "add_research_slot = 1",
  pre=["first_kolev_plan"], filters=RES)
F("second_kolev_plan", 13, 7, "goal_generic_construct_mil_factory", "The Second Kolev Plan",
  "Heavy industry, at last.", J(mil(2), civ(1)), pre=["first_kolev_plan"], filters=IND)
F("construction_brigades", 16, 7, "goal_generic_construct_infrastructure", "Youth Construction Brigades",
  "Young Bulgarians building their own country.", idea("construction_brigades"),
  pre=[["synthetic_fuel", "tobacco_exports"]], filters=IND)
F("industrial_independence", 12, 8, "goal_generic_production2", "Industrial Independence",
  "Bulgaria no longer depends on foreign factories for its survival.", idea("industrial_independence"),
  pre=["sofia_university", "second_kolev_plan"], filters=IND)
F("radio_industry", 14, 8, "goal_generic_radar", "The Radio Industry",
  "Valves, transmitters, receivers - all made at home.",
  J(tech(P + "radio_industry", "electronics", 2, 0.5)), pre=["second_kolev_plan"], filters=RES)
F("balkan_tiger", 13, 9, "goal_generic_production", "The Balkan Tiger",
  "Once the poorest corner of Europe, Bulgaria has become its fastest-growing economy.",
  J(civ(2), mil(2)), pre=["industrial_independence", "radio_industry"], filters=IND)

# ======================= POLITICS (x 21-41) ==============================
F("new_chairman", 31, 0, "goal_generic_political_pressure", "A New Chairman",
  "Victor Kolev, not yet thirty, has been named Chairman of the Council. The old parties call him a boy. He intends to prove them wrong.",
  J(pp(50), stab(0.03)), cost=5, filters=STAB)
F("national_renewal", 29, 1, "goal_generic_propaganda", "Found the National Renewal Movement",
  "A movement above the quarrelling parties, loyal to Bulgaria alone.",
  J(f"set_party_name = {{ ideology = neutrality long_name = {P}party_long name = {P}party }}",
    pop("neutrality", 0.1), pp(50)), pre=["new_chairman"])
F("understanding_with_the_tsar", 33, 1, "goal_generic_neutrality_focus", "An Understanding with Tsar Boris",
  "The Tsar reigns, the Chairman governs. Both know the arrangement suits Bulgaria.",
  J(stab(0.05), ws(0.03)), pre=["new_chairman"], filters=STAB)
F("end_factional_strife", 31, 2, "goal_generic_national_unity", "End the Factional Strife",
  "Zveno, the Military League, the old parties - their era of coups is over.",
  J(remove("factional_strife"), stab(0.05)),
  pre=["national_renewal", "understanding_with_the_tsar"], filters=STAB)

PATHS = ["sofia_charter", "kolev_doctrine", "iron_chairman", "red_chairman"]


def path_mx(me):
    return [p for p in PATHS if p != me]


# ---- Democratic: The Sofia Charter (x 21-23) ----
F("sofia_charter", 22, 3, "goal_support_democracy", "The Sofia Charter",
  "Kolev drafts a charter of rights and promises the first truly free elections in Bulgarian history.",
  J(pop("democratic", 0.15), pp(50)), pre=["end_factional_strife"], mx=path_mx("sofia_charter"),
  ai=2)
F("free_elections", 22, 4, "goal_support_democracy", "Free Elections",
  "The people will choose. Kolev is confident they will choose him.",
  J(set_gov("democratic", "yes"), stab(0.05)), pre=["sofia_charter"])
F("balkan_entente_revival", 21, 5, "goal_generic_improve_relations", "Revive the Balkan Entente",
  "Our neighbours built a pact against us. We will join it on our own terms.",
  friendship_neighbours(), pre=["free_elections"])
F("civil_liberties", 23, 5, "goal_generic_propaganda", "Civil Liberties",
  "A free press, free unions, free speech.", J(stab(0.05), pop("democratic", 0.1)),
  pre=["free_elections"], filters=STAB)
F("western_investment", 21, 6, "goal_generic_construct_civ_factory", "Western Investment",
  "London and Paris bankers are finally interested in Bulgaria.", civ(2),
  pre=["balkan_entente_revival"], filters=IND)
F("rule_of_law", 23, 6, "goal_generic_national_unity", "The Rule of Law",
  "No one, not even the Chairman, stands above the law.", idea("rule_of_law"),
  pre=["civil_liberties"], filters=STAB)
F("join_the_allies", 21, 7, "goal_generic_major_alliance", "Join the Allies",
  "Stand with the democracies against tyranny.",
  join_faction_of("ENG"), pre=["western_investment"], mx=["balkan_commonwealth"],
  available="is_in_faction = no\nENG = { is_faction_leader = yes }")
F("balkan_commonwealth", 23, 7, "goal_generic_major_alliance", "The Balkan Commonwealth",
  "A free association of Balkan democracies, beholden to no great power.",
  f"create_faction = {P}faction_commonwealth", pre=["rule_of_law"], mx=["join_the_allies"],
  available="is_in_faction = no", ai=2)
F("commonwealth_invitations", 23, 8, "goal_generic_improve_relations", "Invitations to the Commonwealth",
  "Belgrade, Athens, Bucharest and Ankara receive the Chairman's letters.",
  invite_neighbours(), pre=["balkan_commonwealth"],
  available="is_faction_leader = yes")
F("arsenal_of_the_balkans", 22, 9, "goal_generic_construct_mil_factory", "Arsenal of Balkan Democracy",
  "Free nations must be able to defend their freedom.",
  J(mil(2), tech(P + "arsenal_of_the_balkans", "industry", 1, 0.5)),
  pre=[["join_the_allies", "commonwealth_invitations"]], filters=IND)

# ---- Non-aligned: The Kolev Doctrine (x 27-29) ----
F("kolev_doctrine", 28, 3, "goal_generic_neutrality_focus", "The Kolev Doctrine",
  "Neither Berlin, nor Moscow, nor London. Bulgaria will be strong enough that no one dares to choose for us.",
  J(pop("neutrality", 0.1), pp(75)), pre=["end_factional_strife"], mx=path_mx("kolev_doctrine"),
  ai=4)
F("armed_neutrality", 27, 4, "goal_generic_defence", "Armed Neutrality",
  "Peace through strength.", idea("armed_neutrality"), pre=["kolev_doctrine"], filters=WS)
F("chairmans_council", 29, 4, "goal_generic_political_pressure", "The Chairman's Council",
  "A cabinet of experts answerable to the Chairman alone.", J(idea("chairmans_rule")),
  pre=["kolev_doctrine"])
F("mountain_fortress", 27, 5, "goal_generic_fortify_city", "Bulgaria the Mountain Fortress",
  "The Balkan range is our citadel.", J("army_experience = 15", tech(P + "mountain_fortress", "land_doctrine", 1, 0.5)),
  pre=["armed_neutrality"], filters=ARMY)
F("plebiscite_of_trust", 29, 5, "goal_generic_propaganda", "Plebiscite of Trust",
  "Kolev asks the people a single question: do you trust me? Ninety-one percent say yes.",
  J(stab(0.08), pop("neutrality", 0.1)), pre=["chairmans_council"], filters=STAB)
F("balkan_accord", 28, 6, "goal_generic_major_alliance", "The Balkan Accord",
  "A league of the small nations of the peninsula, led from Sofia.",
  f"create_faction = {P}faction_accord", pre=["mountain_fortress", "plebiscite_of_trust"],
  available="is_in_faction = no")
F("accord_invitations", 27, 7, "goal_generic_improve_relations", "Envoys to the Neighbours",
  "Our envoys carry one message: together, we cannot be divided and ruled.",
  invite_neighbours(), pre=["balkan_accord"], available="is_faction_leader = yes")
F("guarantee_the_peninsula", 29, 7, "goal_generic_defence", "Guarantee the Peninsula",
  "An attack on any Balkan nation is an attack on Bulgaria.",
  """every_neighbor_country = {
\tlimit = { is_major = no }
\tROOT = { give_guarantee = PREV }
}""", pre=["balkan_accord"], filters=WS)
F("doctrine_fulfilled", 28, 8, "goal_generic_national_unity", "The Doctrine Fulfilled",
  "Bulgaria is armed, united and answerable to no one.",
  swap("armed_neutrality", "kolev_doctrine_idea"),
  pre=["accord_invitations", "guarantee_the_peninsula"], filters=STAB)
F("lion_of_the_balkans", 28, 9, "goal_generic_position_armies", "The Lion of the Balkans",
  "Our flag has a lion on it for a reason.",
  J("army_experience = 25", tech(P + "lion_of_the_balkans", "land_doctrine", 1, 0.5),
    tech(P + "lion_of_the_balkans", "infantry_weapons", 1, 0.5)),
  pre=["doctrine_fulfilled"], filters=ARMY)

# ---- Fascist: The Iron Chairman (x 33-35) ----
F("iron_chairman", 34, 3, "goal_support_fascism", "The Iron Chairman",
  "Democracy failed Bulgaria in 1913 and again in 1918. Kolev will not let it fail a third time.",
  J(pop("fascism", 0.15), ws(0.05)), pre=["end_factional_strife"], mx=path_mx("iron_chairman"),
  ai=2)
F("emergency_powers", 33, 4, "goal_support_fascism", "Seize Emergency Powers",
  "The assembly votes itself out of existence.", J(set_gov("fascism", "no"), stab(0.03)),
  pre=["iron_chairman"])
F("chairmans_legion", 35, 4, "goal_generic_propaganda", "The Chairman's Legion",
  "Uniformed volunteers loyal to Kolev personally.", idea("chairmans_legion"),
  pre=["iron_chairman"], filters=WS)
F("purge_zveno_officers", 33, 5, "goal_generic_political_pressure", "Purge the Zveno Officers",
  "Officers who staged coups before could stage them again.",
  J("army_experience = 15", stab(0.03)), pre=["emergency_powers"], filters=ARMY)
F("militarize_the_youth", 35, 5, "goal_generic_allies_build_infantry", "Militarize the Youth",
  "Every young Bulgarian a soldier in waiting.", J("add_manpower = 15000", ws(0.05)),
  pre=["chairmans_legion"], filters=MP)
F("san_stefano_rhetoric", 34, 6, "goal_generic_territory_or_war", "The Dream of San Stefano",
  "In 1878 Bulgaria stretched from the Danube to the Aegean. Kolev promises it will again.",
  J(ws(0.1), pop("fascism", 0.1)), pre=["purge_zveno_officers", "militarize_the_youth"], filters=WS)
F("join_the_axis", 33, 7, "goal_generic_major_alliance", "March with Berlin",
  "Germany too was betrayed by the peace. Together we will tear it up.",
  join_faction_of("GER"), pre=["san_stefano_rhetoric"], mx=["third_empire_alone"],
  available="is_in_faction = no\nGER = { is_faction_leader = yes }")
F("third_empire_alone", 35, 7, "goal_generic_major_alliance", "The Pact of San Stefano",
  "Bulgaria does not need a master in Berlin. Let others join us.",
  f"create_faction = {P}faction_san_stefano", pre=["san_stefano_rhetoric"], mx=["join_the_axis"],
  available="is_in_faction = no", ai=2)
F("war_production", 34, 8, "goal_generic_production", "Total Mobilization of Industry",
  "Every factory serves the front.", idea("war_production"),
  pre=[["join_the_axis", "third_empire_alone"]], filters=IND)
F("third_bulgarian_empire", 34, 9, "goal_generic_territory_or_war", "The Third Bulgarian Empire",
  "After Simeon and Asen comes Kolev.", idea("third_empire"), pre=["war_production"], filters=WS)

# ---- Communist: The Red Chairman (x 39-41) ----
F("red_chairman", 40, 3, "goal_support_communism", "The Red Chairman",
  "Kolev opens the prisons, legalises the Workers' Party and speaks of a Bulgaria for the toilers.",
  J(pop("communism", 0.15), pp(50)), pre=["end_factional_strife"], mx=path_mx("red_chairman"))
F("popular_front", 39, 4, "goal_support_communism", "The Popular Front",
  "A coalition of workers, peasants and the Chairman.", J(set_gov("communism", "no"), stab(0.03)),
  pre=["red_chairman"])
F("land_to_the_peasants", 41, 4, "goal_generic_consumer_goods", "Land to the Peasants",
  "The great estates are broken up.", J(stab(0.05), pop("communism", 0.1)), pre=["red_chairman"],
  filters=STAB)
F("red_five_year_plan", 39, 5, "goal_generic_production", "The Bulgarian Five-Year Plan",
  "Planned industry, planned prosperity.", J(civ(1), mil(1)), pre=["popular_front"], filters=IND)
F("peoples_army", 41, 5, "goal_generic_allies_build_infantry", "The People's Army",
  "An army of workers and peasants.", idea("peoples_army"), pre=["land_to_the_peasants"], filters=MP)
F("moscow_embassy", 40, 6, "goal_generic_improve_relations", "An Embassy in Moscow",
  "Slavic brothers, socialist comrades.",
  J("SOV = { add_opinion_modifier = { target = ROOT modifier = BUL_kv_balkan_friendship } }", pp(50)),
  pre=["red_five_year_plan", "peoples_army"], available="country_exists = SOV")
F("join_the_comintern", 39, 7, "goal_generic_major_alliance", "Join the Comintern",
  "Stand with the Soviet Union.", join_faction_of("SOV"), pre=["moscow_embassy"],
  mx=["balkan_soviet_union"], available="is_in_faction = no\nSOV = { is_faction_leader = yes }")
F("balkan_soviet_union", 41, 7, "goal_generic_major_alliance", "The Balkan Socialist Federation",
  "A federation of Balkan workers' republics - led from Sofia, not Moscow.",
  f"create_faction = {P}faction_balkan_soviet", pre=["moscow_embassy"], mx=["join_the_comintern"],
  available="is_in_faction = no")
F("export_the_revolution", 40, 8, "goal_support_communism", "Export the Revolution",
  "The workers of Belgrade and Bucharest are listening.",
  """every_neighbor_country = {
\tadd_popularity = { ideology = communism popularity = 0.1 }
}""", pre=[["join_the_comintern", "balkan_soviet_union"]])
F("red_heavy_industry", 40, 9, "goal_generic_construct_mil_factory", "Steel for the Revolution",
  "Heavy industry for a socialist Bulgaria.", mil(2), pre=["export_the_revolution"], filters=IND)

# ---- Convergence ----
F("chairmans_legacy", 31, 10, "goal_generic_national_unity", "The Chairman's Legacy",
  "Whatever road Bulgaria took, it took it under Victor Kolev. History will remember him.",
  J(stab(0.1), ws(0.05), pp(100)),
  pre=[["arsenal_of_the_balkans", "lion_of_the_balkans", "third_bulgarian_empire", "red_heavy_industry"]],
  filters=STAB)

# ======================= FOREIGN POLICY (x 44-50) ========================
F("chairmans_diplomacy", 47, 0, "goal_generic_improve_relations", "The Chairman's Diplomacy",
  "Kolev intends to run foreign policy himself.", pp(50), cost=5)
F("good_neighbour_policy", 45, 1, "goal_generic_improve_relations", "Good Neighbour Policy",
  "Bulgaria has fought every one of its neighbours. That ends now.",
  J(friendship_neighbours(), stab(0.03)), pre=["chairmans_diplomacy"], mx=["revisionist_agenda"], ai=2)
F("revisionist_agenda", 49, 1, "goal_generic_territory_or_war", "The Revisionist Agenda",
  "Neuilly stole Dobruja, Thrace and Macedonia. Bulgaria wants them back.",
  J(ws(0.05), pp(25)), pre=["chairmans_diplomacy"], mx=["good_neighbour_policy"], filters=WS)
F("yugoslav_rail_link", 44, 2, "goal_generic_trade", "The Belgrade Rail Link",
  "Trade, not war, with our western neighbour.", J(infra(1), civ(1)),
  pre=["good_neighbour_policy"], filters=IND)
F("turkish_friendship", 46, 2, "goal_generic_improve_relations", "Friendship with Ankara",
  "Old enemies, new partners.",
  J("if = { limit = { country_exists = TUR } TUR = { add_opinion_modifier = { target = ROOT modifier = BUL_kv_balkan_friendship } } }",
    stab(0.02)), pre=["good_neighbour_policy"])
F("non_aggression", 45, 3, "goal_generic_neutrality_focus", "A Web of Non-Aggression",
  "Signed in Sofia, ratified in every Balkan capital.", idea("good_neighbour"),
  pre=["yugoslav_rail_link", "turkish_friendship"], filters=STAB)
F("balkan_common_market", 45, 4, "goal_generic_trade", "The Balkan Common Market",
  "Tariffs fall, trade rises, everyone wins.", J(civ(1), tech(P + "balkan_common_market", "industry", 1, 0.5)),
  pre=["non_aggression"], filters=IND)
F("press_our_claims", 49, 2, "goal_generic_demand_territory", "Press Our Claims",
  "The maps in every Bulgarian classroom show what is ours.",
  CLAIM_EFFECT, pre=["revisionist_agenda"], filters=ANNEX)
F("demand_dobruja", 48, 3, "goal_generic_demand_territory", "Demand Southern Dobruja",
  "Bucharest will return the Dobruja - by treaty or otherwise.", demand("ROM"),
  pre=["press_our_claims"], available=demand_available("ROM"),
  bypass="NOT = { ROM = { any_owned_state = { is_claimed_by = ROOT } } }", filters=ANNEX)
F("demand_thrace", 50, 3, "goal_generic_demand_territory", "Demand Western Thrace",
  "Bulgaria needs its Aegean coast.", demand("GRE"),
  pre=["press_our_claims"], available=demand_available("GRE"),
  bypass="NOT = { GRE = { any_owned_state = { is_claimed_by = ROOT } } }", filters=ANNEX)
F("demand_macedonia", 49, 4, "goal_generic_demand_territory", "Demand Macedonia",
  "Ohrid, Skopje, Bitola - the cradle of Bulgarian letters.", demand("YUG"),
  pre=[["demand_dobruja", "demand_thrace"]], available=demand_available("YUG"),
  bypass="NOT = { YUG = { any_owned_state = { is_claimed_by = ROOT } } }", filters=ANNEX)
F("integrate_the_lands", 49, 5, "goal_generic_national_unity", "Integrate the Recovered Lands",
  "These lands were always Bulgarian. Now the law says so too.",
  """every_owned_state = {
\tlimit = { is_claimed_by = ROOT NOT = { is_core_of = ROOT } }
\tadd_core_of = ROOT
}""", pre=["demand_macedonia"],
  available="any_owned_state = { is_claimed_by = ROOT NOT = { is_core_of = ROOT } }", filters=ANNEX)

# --------------------------------------------------------------------------
# Ideas (national spirits)
# --------------------------------------------------------------------------
IDEAS = {
    # starting spirits
    "factional_strife": ("Factional Strife", "Zveno, the Military League and the old parties all believe they should be running Bulgaria instead of a young upstart Chairman.",
                         "stability_factor = -0.10\npolitical_power_factor = -0.15", "generic_political_instability"),
    "shadow_of_neuilly": ("Shadow of Neuilly", "The Treaty of Neuilly left our army small, our people bitter, and our officers humiliated.",
                          "war_support_factor = -0.10\narmy_org_factor = -0.05", "generic_disjointed_government"),
    "agrarian_economy": ("Agrarian Economy", "Bulgaria is a land of small farms, ox-carts and very few factories.",
                         "consumer_goods_factor = 0.05\nproduction_speed_buildings_factor = -0.10", "generic_agriculture"),
    "agrarian_economy_2": ("Modernizing Agriculture", "Reform has begun, but the countryside is still poor.",
                           "consumer_goods_factor = 0.02\nproduction_speed_buildings_factor = -0.05", "generic_agriculture"),
    # focus rewards
    "conscription_reform": ("Conscription Reform", "A wider, fairer draft.", "conscription = 0.01", "generic_manpower_bonus"),
    "officer_academy": ("Sofia Officer Academy", "Officers who think.", "army_org_factor = 0.05\nplanning_speed = 0.10", "generic_army_support"),
    "border_forts": ("Fortified Frontiers", "Every pass is a fortress.", "army_defence_factor = 0.05", "generic_fortify"),
    "tobacco_exports": ("Tobacco Exports", "Golden leaf, golden revenue.", "consumer_goods_factor = -0.03\npolitical_power_factor = 0.05", "generic_production_bonus"),
    "construction_brigades": ("Youth Construction Brigades", "Young hands building a young nation.", "production_speed_buildings_factor = 0.10", "generic_production_bonus"),
    "industrial_independence": ("Industrial Independence", "We make what we need.", "industrial_capacity_factory = 0.05\nproduction_factory_max_efficiency_factor = 0.05", "generic_production_bonus"),
    "rule_of_law": ("The Rule of Law", "No one above the law.", "stability_factor = 0.08\npolitical_power_factor = 0.05", "generic_democratic_drift_bonus"),
    "armed_neutrality": ("Armed Neutrality", "Peace through strength.", "army_defence_factor = 0.05\nwar_support_factor = 0.05", "generic_neutrality_drift_bonus"),
    "chairmans_rule": ("The Chairman's Council", "Experts, answerable to Kolev.", "political_power_factor = 0.15\nstability_factor = 0.03", "generic_pp_unity_bonus"),
    "kolev_doctrine_idea": ("The Kolev Doctrine", "Armed, united and answerable to no one.", "army_defence_factor = 0.10\nwar_support_factor = 0.10\nstability_factor = 0.05", "generic_neutrality_drift_bonus"),
    "chairmans_legion": ("The Chairman's Legion", "Uniformed loyalists.", "war_support_factor = 0.10\nconscription = 0.005", "generic_fascism_drift_bonus"),
    "war_production": ("Total Mobilization of Industry", "Every factory serves the front.", "production_factory_max_efficiency_factor = 0.05\nconsumer_goods_factor = -0.03", "generic_production_bonus"),
    "third_empire": ("The Third Bulgarian Empire", "After Simeon and Asen comes Kolev.", "army_attack_factor = 0.05\nwar_support_factor = 0.10", "generic_fascism_drift_bonus"),
    "peoples_army": ("The People's Army", "An army of workers and peasants.", "conscription = 0.015\narmy_org_factor = -0.03", "generic_communism_drift_bonus"),
    "good_neighbour": ("Balkan Non-Aggression", "Peace with our neighbours.", "stability_factor = 0.05\npolitical_power_factor = 0.05", "generic_pp_unity_bonus"),
}

STARTING_IDEAS = ["factional_strife", "shadow_of_neuilly", "agrarian_economy"]

TRAITS = {
    "young_chairman": ("The Young Chairman", "political_power_factor = 0.10\nstability_factor = 0.05"),
    "man_of_the_people": ("Man of the People", "stability_factor = 0.10"),
    "iron_will": ("Iron Will", "war_support_factor = 0.10\narmy_attack_factor = 0.03"),
    "red_reformer": ("Red Reformer", "production_speed_buildings_factor = 0.05\nstability_factor = 0.03"),
}

FACTIONS = {
    "faction_commonwealth": "Balkan Commonwealth",
    "faction_accord": "Balkan Accord",
    "faction_san_stefano": "Pact of San Stefano",
    "faction_balkan_soviet": "Balkan Socialist Federation",
}

# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate():
    ids = [f["id"] for f in FOCUSES]
    assert len(ids) == len(set(ids)), "duplicate focus ids"
    idset = set(ids)
    pos = {}
    by_id = {f["id"]: f for f in FOCUSES}
    for f in FOCUSES:
        key = (f["x"], f["y"])
        assert key not in pos, f"position clash {key}: {pos[key]} vs {f['id']}"
        pos[key] = f["id"]
        for grp in f["pre"]:
            for p in grp:
                assert p in idset, f"{f['id']}: unknown prerequisite {p}"
                assert by_id[p]["y"] < f["y"], f"{f['id']}: prerequisite {p} not above it"
        for m in f["mx"]:
            assert m in idset, f"{f['id']}: unknown mutually exclusive {m}"
    # make mutual exclusion symmetric
    for f in FOCUSES:
        for m in f["mx"]:
            other = by_id[m]
            if f["id"] not in other["mx"]:
                other["mx"].append(f["id"])
    # ideas referenced must exist
    import re
    text = "\n".join(f["reward"] for f in FOCUSES)
    for ref in re.findall(rf"(?:add_ideas|remove_ideas|remove_idea|add_idea) = ({P}\w+)", text):
        assert ref[len(P):] in IDEAS, f"unknown idea {ref}"
    assert len(FOCUSES) >= 100, f"only {len(FOCUSES)} focuses"
    return len(FOCUSES)


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------

def indent(text, n):
    pad = "\t" * n
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def write(path, text, bom=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(("﻿" if bom else "") + text, encoding="utf-8", newline="\n")


def focus_file():
    out = [f"""focus_tree = {{
\tid = {TAG}_kolev_focus_tree
\tcountry = {{
\t\tfactor = 0
\t\tmodifier = {{ add = 1000 tag = {TAG} }}
\t}}
\tdefault = no
\treset_on_civilwar = no
\tinitial_show_position = {{ focus = {P}new_chairman }}
\tcontinuous_focus_position = {{ x = 50 y = 1700 }}
"""]
    for f in FOCUSES:
        b = [f"focus = {{", f"\tid = {f['id']}", f"\ticon = {f['icon']}",
             f"\tx = {f['x']}", f"\ty = {f['y']}", f"\tcost = {f['cost']}"]
        for grp in f["pre"]:
            b.append("\tprerequisite = { " + " ".join(f"focus = {p}" for p in grp) + " }")
        if f["mx"]:
            b.append("\tmutually_exclusive = { " + " ".join(f"focus = {m}" for m in f["mx"]) + " }")
        if f["available"]:
            b += ["\tavailable = {", indent(f["available"], 2), "\t}"]
        if f["bypass"]:
            b += ["\tbypass = {", indent(f["bypass"], 2), "\t}"]
        b.append("\tsearch_filters = { " + " ".join(f["filters"]) + " }")
        b.append(f"\tai_will_do = {{ factor = {f['ai']} }}")
        b += ["\tcompletion_reward = {", indent(f["reward"], 2), "\t}", "}"]
        out.append(indent("\n".join(b), 1))
    out.append("}\n")
    return "\n".join(out)


def ideas_file():
    out = ["ideas = {", "\tcountry = {"]
    for key, (_, _, mods, pic) in IDEAS.items():
        out.append(f"""\t\t{P}{key} = {{
\t\t\tpicture = {pic}
\t\t\tallowed = {{ always = no }}
\t\t\tremoval_cost = -1
\t\t\tmodifier = {{
{indent(mods, 4)}
\t\t\t}}
\t\t}}""")
    out += ["\t}", "}", ""]
    return "\n".join(out)


def traits_file():
    out = ["leader_traits = {"]
    for key, (_, mods) in TRAITS.items():
        out.append(f"\t{P}{key} = {{\n\t\trandom = no\n{indent(mods, 2)}\n\t}}")
    out += ["}", ""]
    return "\n".join(out)


def characters_file():
    roles = [("despotism", "young_chairman"), ("liberalism", "man_of_the_people"),
             ("fascism_ideology", "iron_will"), ("leninism", "red_reformer")]
    blocks = "\n".join(f"""\t\tcountry_leader = {{
\t\t\tdesc = {LEADER}_desc
\t\t\tideology = {ideo}
\t\t\texpire = "1975.1.1.1"
\t\t\tid = -1
\t\t\ttraits = {{ {P}young_chairman{'' if trait == 'young_chairman' else ' ' + P + trait} }}
\t\t}}""" for ideo, trait in roles)
    return f"""characters = {{
\t{LEADER} = {{
\t\tname = {LEADER}
\t\tportraits = {{
\t\t\tcivilian = {{
\t\t\t\tlarge = "gfx/leaders/BUL/BUL_victor_kolev.dds"
\t\t\t\tsmall = "gfx/leaders/BUL/BUL_victor_kolev_small.dds"
\t\t\t}}
\t\t}}
{blocks}
\t}}
}}
"""


def on_actions_file():
    ideas = "\n".join(f"\t\t\t\t\tadd_ideas = {P}{i}" for i in STARTING_IDEAS)
    return f"""on_actions = {{
\ton_startup = {{
\t\teffect = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ has_global_flag = {P}initialised }} country_exists = {TAG} }}
\t\t\t\tset_global_flag = {P}initialised
\t\t\t\t{TAG} = {{
\t\t\t\t\trecruit_character = {LEADER}
\t\t\t\t\tpromote_character = {LEADER}
\t\t\t\t\tset_party_name = {{ ideology = neutrality long_name = {P}party_long name = {P}party }}
{ideas}
\t\t\t\t\tload_focus_tree = {{ tree = {TAG}_kolev_focus_tree keep_completed = no }}
\t\t\t\t\tcountry_event = {{ id = kolev.1 days = 1 }}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}}
}}
"""


EVENTS = r"""add_namespace = kolev

# Opening event
country_event = {
	id = kolev.1
	title = kolev.1.t
	desc = kolev.1.d
	picture = GFX_report_event_generic_rally_1
	is_triggered_only = yes
	option = {
		name = kolev.1.a
		add_political_power = 25
	}
}

# Territorial demand, received by the target. FROM = the demanding country.
country_event = {
	id = kolev.10
	title = kolev.10.t
	desc = kolev.10.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = kolev.10.a
		ai_chance = {
			base = 15
			modifier = { factor = 0 is_in_faction = yes }
			modifier = { factor = 3 FROM = { is_in_faction = yes } }
			modifier = { factor = 2 has_war = yes }
		}
		every_owned_state = {
			limit = { is_claimed_by = FROM }
			FROM = { transfer_state = PREV }
		}
		FROM = { country_event = { id = kolev.11 days = 1 } }
	}
	option = {
		name = kolev.10.b
		ai_chance = { base = 85 }
		add_war_support = 0.05
		FROM = { country_event = { id = kolev.12 days = 1 } }
	}
}

# They gave in
country_event = {
	id = kolev.11
	title = kolev.11.t
	desc = kolev.11.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = kolev.11.a
		add_stability = 0.05
		add_war_support = 0.05
	}
}

# They refused. FROM = the refusing country.
country_event = {
	id = kolev.12
	title = kolev.12.t
	desc = kolev.12.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = kolev.12.a
		ai_chance = { base = 70 }
		create_wargoal = { type = annex_everything target = FROM }
	}
	option = {
		name = kolev.12.b
		ai_chance = { base = 30 }
		add_stability = 0.03
		add_political_power = 50
	}
}

# Faction invitation, received by the invitee. FROM = the faction leader.
country_event = {
	id = kolev.20
	title = kolev.20.t
	desc = kolev.20.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = kolev.20.a
		ai_chance = {
			base = 35
			modifier = { factor = 0 is_in_faction = yes }
			modifier = { factor = 2 has_opinion = { target = FROM value > 40 } }
			modifier = { factor = 0.3 NOT = { has_government = FROM } }
		}
		trigger = { is_in_faction = no }
		FROM = { add_to_faction = ROOT }
		FROM = { country_event = { id = kolev.21 days = 1 } }
	}
	option = {
		name = kolev.20.b
		ai_chance = { base = 65 }
	}
}

country_event = {
	id = kolev.21
	title = kolev.21.t
	desc = kolev.21.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = kolev.21.a
	}
}
"""

EVENT_LOC = {
    "kolev.1.t": "Chairman Kolev Takes Office",
    "kolev.1.d": "Sofia, 1936. After a decade of coups, assassinations and failed governments, Tsar Boris III has handed the chairmanship of the Council of Ministers to Victor Kolev - an economist and organiser from Plovdiv who is not yet thirty. The generals of the Military League dismiss him as a schoolboy, the old party bosses expect him to fall within the year, and foreign embassies are not sure how to spell his name.\\n\\nKolev's first speech to the assembly lasted eleven minutes. 'Bulgaria has been the battlefield of other nations' ambitions for long enough,' he said. 'From today, we decide our own future.'",
    "kolev.1.a": "Let them underestimate him.",
    "kolev.10.t": "[FROM.GetName] Demands Our Territory",
    "kolev.10.d": "The government of [FROM.GetName], led by Chairman Victor Kolev, has formally demanded the return of lands it claims were taken from it under the Treaty of Neuilly. The note is polite but makes clear that a refusal will not be the end of the matter.",
    "kolev.10.a": "We cannot risk war. Cede the lands.",
    "kolev.10.b": "Not one village!",
    "kolev.11.t": "[FROM.GetName] Yields",
    "kolev.11.d": "[FROM.GetName] has accepted our demands. Bulgarian troops are crossing the old border to cheering crowds.",
    "kolev.11.a": "Bulgaria is whole again.",
    "kolev.12.t": "[FROM.GetName] Refuses",
    "kolev.12.d": "[FROM.GetName] has rejected our demands outright. The General Staff reports it is ready to settle the matter by force, if the Chairman gives the order.",
    "kolev.12.a": "Then we will take it.",
    "kolev.12.b": "Not yet. We will wait for a better moment.",
    "kolev.20.t": "An Invitation from Sofia",
    "kolev.20.d": "Chairman Victor Kolev of [FROM.GetName] has invited us to join the [FROM.GetFactionName], arguing that the small nations of the Balkans can only stay free if they stand together.",
    "kolev.20.a": "We accept.",
    "kolev.20.b": "We prefer to stand alone.",
    "kolev.21.t": "[FROM.GetName] Joins Us",
    "kolev.21.d": "[FROM.GetName] has accepted the Chairman's invitation and joined our alliance.",
    "kolev.21.a": "Excellent.",
}


def loc_file():
    lines = ["l_english:"]

    def add(k, v):
        lines.append(f' {k}:0 "{v}"')

    for f in FOCUSES:
        add(f["id"], f["name"])
        add(f["id"] + "_desc", f["desc"])
    for key, (name, desc, _, _) in IDEAS.items():
        add(P + key, name)
        add(P + key + "_desc", desc)
    for key, (name, _) in TRAITS.items():
        add(P + key, name)
    for key, name in FACTIONS.items():
        add(P + key, name)
    add(LEADER, "Victor Kolev")
    add(LEADER + "_desc",
        "Born in Plovdiv in 1909, Victor Kolev studied economics in Sofia and Vienna before making his name as an organiser of agricultural cooperatives. Sharp, impatient and fiercely patriotic, he rose to the chairmanship of the Council of Ministers in 1936 with the backing of a weary Tsar and a generation of young Bulgarians tired of coups and defeats.")
    add(P + "party", "National Renewal")
    add(P + "party_long", "National Renewal Movement")
    add("BUL_kv_balkan_friendship", "Balkan Friendship")
    for k, v in EVENT_LOC.items():
        add(k, v)
    lines.append("")
    return "\n".join(lines)


OPINION = """opinion_modifiers = {
	BUL_kv_balkan_friendship = {
		value = 30
	}
}
"""

DESCRIPTOR = """version="1.0.0"
tags={
	"National Focuses"
	"Alternative History"
	"Balance"
}
name="Victor Kolev: Chairman of Bulgaria"
supported_version="1.*"
"""


def main():
    n = validate()
    write(ROOT / "descriptor.mod", DESCRIPTOR)
    write(ROOT / "common/national_focus/BUL_kolev_focus.txt", focus_file())
    write(ROOT / "common/ideas/BUL_kolev_ideas.txt", ideas_file())
    write(ROOT / "common/country_leader/BUL_kolev_traits.txt", traits_file())
    write(ROOT / "common/characters/BUL_kolev_characters.txt", characters_file())
    write(ROOT / "common/on_actions/BUL_kolev_on_actions.txt", on_actions_file())
    write(ROOT / "common/opinion_modifiers/BUL_kolev_opinion.txt", OPINION)
    write(ROOT / "events/BUL_kolev_events.txt", EVENTS)
    write(ROOT / "localisation/english/BUL_kolev_l_english.yml", loc_file(), bom=True)
    # launcher stub for manual installs (copy next to the victor_kolev folder)
    write(ROOT.parent / "victor_kolev.mod", DESCRIPTOR + 'path="mod/victor_kolev"\n')
    print(f"OK: {n} focuses written to {ROOT}")


if __name__ == "__main__":
    main()
