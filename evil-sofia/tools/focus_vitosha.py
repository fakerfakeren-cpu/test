"""Vitosha focus tree: Daniel-Henry Capel or Yanislav Marazov, a civil war laid out like vanilla's Spanish tree.

Two mutually exclusive roots at the top: Stand with Henry (left half) or March with Yani (right half). Each side has
its own chain of preparations that ends in the civil war:
  Henry: Crush the Student Movement. Yani's rebels take the five eastern states (size 0.3). About a year to win.
  Yani:  Yani Takes the Villa. Yani becomes leader; Henry's loyalists take Boyana and the west (size 0.6). Hard.
What a side prepared (divisions, rifles, spirits) joins the player when the war starts; the enemy gets a fixed army.
At the start of the war support is split evenly between the side's two ideologies, and the side splits into three
branches like Spain's: two mutually exclusive ideology paths and a war branch that takes down The Mountain in
Flames. Henry: What the English Couldn't Do (democratic) or What Zevka Wanted (authoritarian). Yani: Red Plovdiv
(communist) or The Seven Hills (fascist). Each path has an alliance and a formable. The Evil Gang, industry and army
branches on the far right are open to both.

Same entry format as tools/focus_sredets.py. Placeholders ({STATE:...}, {CLAIMS:...}, {WAR:...}, {HELD:...},
{COREHELD:...}) are filled by tools/build_focus.py.
"""
import os
import re

import numpy as np
from PIL import Image

TAG = "VIT"
EVENT_NS = "evil_sofia_vit"
FOCUSES, FILTERS = [], {}


def F(fid, name, x, y, pre, mx, weeks, icon, avail, reward, desc, filters):
    FOCUSES.append((fid, name, x, y, pre, mx, weeks, icon, avail, reward, desc))
    FILTERS[fid] = filters


def S(name):
    return "{STATE:VIT:%s}" % name


YANI_EAST = ["Simeonovo", "Malinova Dolina Villas", "Dragalevtsi", "Dragalevtsi Lift", "Orehite"]
HENRY_WEST = ["Vitosha", "Kopitoto", "Karpuzitsa", "Knyazhevo", "Priplat Villas", "Vladaya Villas", "Vladaya",
              "Marchaevo", "Marchaevo Woods", "Marchaevo Hills"]
LEADER = '"1965.1.1.1"'
NOWAR = "has_civil_war = no"


def ind(body, n=1):
    return "".join("\t" * n + ln + "\n" for ln in body.split("\n"))


def henry_role(ideology, promote):
    return (f"add_country_leader_role = {{\n\tcharacter = VIT_leader\n\tcountry_leader = {{ ideology = {ideology} "
            f"expire = {LEADER} }}\n" + ("\tpromote_leader = yes\n" if promote else "") + "}")


def yani_role(ideology, promote):
    return (f"add_country_leader_role = {{\n\tcharacter = VIT_yani\n\tcountry_leader = {{ desc = \"VIT_yani_desc\" "
            f"ideology = {ideology} expire = {LEADER} traits = {{ evil_sofia_plovdiv_born }} }}\n"
            + ("\tpromote_leader = yes\n" if promote else "") + "}")


def ifc(cond, body, kw="if"):
    return f"{kw} = {{\n\tlimit = {{ {cond} }}\n" + ind(body) + "}"


def war(ideology, size, capital, states):
    return (f"start_civil_war = {{\n\tideology = {ideology}\n\tsize = {size}\n\tcapital = {S(capital)}\n"
            f"\tstates = {{ {' '.join(S(n) for n in states)} }}\n}}")


def rebels(body):
    return "every_other_country = {\n\tlimit = { original_tag = VIT has_civil_war = yes }\n" + ind(body) + "}"


def done(fid):
    return f"has_completed_focus = VIT_{fid}"


# what the player's side prepared, given when the war starts
HENRY_PREP = "\n".join([
    ifc(done("the_boyana_garrison"), 'load_oob = "VIT_henry_army"'),
    ifc(done("mothers_savings"), "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2500 }"),
    ifc(done("the_mountain_rangers"), "add_ideas = VIT_mountain_rangers"),
    ifc(done("henrys_officers"), "army_experience = 30\nadd_ideas = VIT_henrys_officers_idea")])
YANI_PREP = "\n".join([
    ifc(done("cells_in_simeonovo"), 'load_oob = "VIT_yani_army"'),
    ifc(done("students_from_plovdiv"), "add_manpower = 20000\nadd_ideas = VIT_plovdiv_students"),
    ifc(done("arms_from_plovdiv"), "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2500 }"),
    ifc(done("the_plovdiv_committee"), "add_war_support = 0.10\narmy_experience = 20")])
HENRY_PREP += "\n" + "\n".join([
    ifc(done("friends_at_the_gate"), 'load_oob = "VIT_friends_of_the_villa"'),
    ifc(done("guards_for_hire"), 'load_oob = "VIT_hired_guard"'),
    ifc(done("the_british_club"), 'load_oob = "VIT_club_volunteers"')])
YANI_PREP += "\n" + "\n".join([
    ifc(done("classmates_at_the_front"), 'load_oob = "VIT_classmates"'),
    ifc(done("caches_in_the_forest"), "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2000 }"),
    ifc(done("drills_in_the_woods"), "army_experience = 20"),
    ifc(done("barricades_in_simeonovo"),
        f"{S('Simeonovo')} = {{ add_building_construction = {{ type = bunker level = 3 province = {{ all_provinces = yes limit_to_border = yes }} instant_build = yes }} }}"),
    ifc(done("the_tobacco_column"), 'load_oob = "VIT_plovdiv_column"'),
    ifc(done("studentski_volunteers"), 'load_oob = "VIT_studentski_volunteers"')])
REBEL_FLAMES = "add_ideas = VIT_mountain_in_flames_2\nload_focus_tree = evil_sofia_VIT_focus\nset_country_flag = VIT_war_started"
REBELS_ARE_YANI = ("set_cosmetic_tag = VIT_YANI\nset_country_flag = VIT_yani_side\n"
                   "unlock_national_focus = VIT_march_with_yani\nunlock_national_focus = VIT_yani_takes_the_villa\n"
                   "country_event = { id = evil_sofia_vit.28 days = 1 }")
REBELS_ARE_HENRY = ("set_cosmetic_tag = VIT_HENRY\nset_country_flag = VIT_henry_side\n"
                    "unlock_national_focus = VIT_stand_with_henry\nunlock_national_focus = VIT_crush_the_student_movement\n"
                    "country_event = { id = evil_sofia_vit.27 days = 1 }")
YANI_BOTH_ROLES = yani_role("leninism", False) + "\n" + yani_role("fascism_ideology", False)

CRUSH = "\n".join([
    "recruit_character = VIT_yani", YANI_BOTH_ROLES,
    "set_popularities = { democratic = 40 neutrality = 40 communism = 10 fascism = 10 }",
    "random_list = {\n\t50 = {\n" + ind(war("communism", 0.3, "Simeonovo", YANI_EAST), 2) + "\t}\n"
    "\t50 = {\n" + ind(war("fascism", 0.3, "Simeonovo", YANI_EAST), 2) + "\t}\n}",
    "add_ideas = VIT_mountain_in_flames_3", HENRY_PREP,
    "set_cosmetic_tag = VIT_HENRY", "country_event = { id = evil_sofia_vit.27 days = 1 }",
    rebels(REBEL_FLAMES + "\n" + REBELS_ARE_YANI + '\nload_oob = "VIT_yani_army"\nadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }'),
    "set_country_flag = VIT_henry_side", "set_country_flag = VIT_war_started",
    "news_event = { id = evil_sofia_vit_news.1 hours = 6 }"])
TAKE_THE_VILLA = "\n".join([
    "recruit_character = VIT_yani", yani_role("leninism", True), yani_role("fascism_ideology", False),
    "set_politics = { ruling_party = communism elections_allowed = no }",
    "set_popularities = { communism = 40 fascism = 40 democratic = 10 neutrality = 10 }",
    henry_role("conservatism", False),
    f"set_capital = {{ state = {S('Simeonovo')} }}",
    "random_list = {\n\t50 = {\n" + ind(war("neutrality", 0.6, "Vitosha", HENRY_WEST), 2) + "\t}\n"
    "\t50 = {\n" + ind(war("democratic", 0.6, "Vitosha", HENRY_WEST), 2) + "\t}\n}",
    "add_ideas = VIT_mountain_in_flames_3", YANI_PREP,
    "set_cosmetic_tag = VIT_YANI", "country_event = { id = evil_sofia_vit.28 days = 1 }",
    rebels(REBEL_FLAMES + "\n" + REBELS_ARE_HENRY + '\nload_oob = "VIT_henry_army"\nadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2500 }\n'
           "army_experience = 25\nadd_ideas = VIT_mountain_rangers"),
    "set_country_flag = VIT_yani_side", "set_country_flag = VIT_war_started",
    "news_event = { id = evil_sofia_vit_news.1 hours = 6 }"])
FLAMES_DOWN = "\n".join([
    ifc("has_idea = VIT_mountain_in_flames_3", "swap_ideas = { remove_idea = VIT_mountain_in_flames_3 add_idea = VIT_mountain_in_flames_2 }"),
    ifc("has_idea = VIT_mountain_in_flames_2", "swap_ideas = { remove_idea = VIT_mountain_in_flames_2 add_idea = VIT_mountain_in_flames_1 }", "else_if"),
    ifc("has_idea = VIT_mountain_in_flames_1", "remove_ideas = VIT_mountain_in_flames_1", "else_if")])
FLAMES_OUT = "\n".join(f"if = {{ limit = {{ has_idea = VIT_mountain_in_flames_{i} }} remove_ideas = VIT_mountain_in_flames_{i} }}"
                       for i in (1, 2, 3))
SCARS_DOWN = "\n".join([
    ifc("has_idea = VIT_scars_of_war_2", "swap_ideas = { remove_idea = VIT_scars_of_war_2 add_idea = VIT_scars_of_war_1 }"),
    ifc("has_idea = VIT_scars_of_war_1", "remove_ideas = VIT_scars_of_war_1", "else_if")])
FLAMES_TT = "\\n\\nTakes The Mountain in Flames down one step."
CAPITAL_HOME = f"if = {{ limit = {{ {S('Vitosha')} = {{ is_controlled_by = ROOT }} }} set_capital = {{ state = {S('Vitosha')} }} }}"


def factory(kind, n=1, slots=None):
    return (f"capital_scope = {{\n\tadd_extra_state_shared_building_slots = {slots or n}\n"
            f"\tadd_building_construction = {{ type = {kind} level = {n} instant_build = yes }}\n}}")


def wargoals_on_neighbours(spare):
    return ("every_neighbor_country = {\n\tlimit = { NOT = { is_in_faction_with = ROOT" + (f" {spare}" if spare else "")
            + " } }\n\tROOT = { create_wargoal = { type = annex_everything target = PREV } }\n}")


def invite(event):
    return ("every_country = {\n\tlimit = { NOT = { tag = ROOT } is_in_faction = no exists = yes NOT = { has_war_with = ROOT } }\n"
            f"\tcountry_event = {{ id = evil_sofia_vit.{event} }}\n}}")


# ================================================================== the two roots and the two chains
F("stand_with_henry", "Stand with Henry", 29, 0, [], ["march_with_yani"], 5, "person:stand_with_henry", "NOT = { has_country_flag = VIT_war_started }",
  "add_political_power = 50\narmy_experience = 10",
  "Daniel-Henry Capel rules Vitosha from a villa on the hill, with the forest at his back and the whole of Sofia below. "
  "Half English, half Bulgarian and entirely sure of himself, he has the strongest guard of any district. A student "
  "from Plovdiv called Yanislav Marazov is stirring up the villages against him. We stand with Henry.\\n\\nThe left "
  "half of the tree: Henry prepares, crushes the student movement and fights the civil war as the government.",
  ["POLITICAL"])
F("march_with_yani", "March with Yani", 31, 0, [], ["stand_with_henry"], 5, "person:march_with_yani", "NOT = { has_country_flag = VIT_war_started }",
  "add_political_power = 50",
  "Yanislav Marazov came to Sofia from Plovdiv to study and never went home. In the cafés of Simeonovo and Dragalevtsi "
  "he talks, and more people listen every week. The future belongs to him, not to the villa on the hill. We march with "
  "Yani.\\n\\nThe right half of the tree: Yani's movement prepares, takes the villa and fights Henry's loyalists. "
  "It is the harder war.", ["POLITICAL"])

HCHAIN = [
    ("henry_holds_the_villa", "Henry Holds the Villa", 14, 1, [["stand_with_henry"]], 6, "duo:Generic_Castle",
     "add_political_power = 75\nadd_stability = 0.05",
     "Sandbags at the gate, guards on the roof and Henry's mother in charge of the kitchen. The villa will not fall."),
    ("the_boyana_garrison", "The Boyana Garrison", 14, 2, [["henry_holds_the_villa"]], 8, "duo:Generic_Soldiers_Defense",
     "army_experience = 10",
     "The guard battalions in Boyana get new barracks, new rifles and officers who are loyal to Henry first.\\n\\nWhen "
     "the war comes we get four more divisions in Boyana."),
    ("mothers_savings", "Mother's Savings", 13, 3, [["the_boyana_garrison"]], 6, "duo:Generic_Loadsamoney",
     "add_political_power = 50",
     "Henry's mother has been putting money aside for years, against exactly this kind of day. She opens the tin.\\n\\n"
     "When the war comes we get 2,500 rifles."),
    ("the_mountain_rangers", "The Mountain Rangers", 15, 3, [["the_boyana_garrison"]], 8, "duo:Generic_Mountain_Warfare",
     "army_experience = 10",
     "Hunters, foresters and mountain guides who know every path from Boyana to Cherni Vrah.\\n\\nWhen the war comes we "
     "get the spirit Mountain Rangers (better defence, less attrition)."),
    ("henrys_officers", "Henry's Officers", 14, 4, [["mothers_savings"], ["the_mountain_rangers"]], 8, "duo:Generic_Command_Power",
     "add_political_power = 25",
     "Henry quietly replaces every officer he is not sure of with one he is.\\n\\nWhen the war comes we get 30 army "
     "experience and the spirit Henry's Officers (better organisation)."),
]
for fid, name, x, y, pre, w, icon, rew, desc in HCHAIN:
    F(fid, name, x, y, pre, [], w, icon, "NOT = { has_country_flag = VIT_war_started }", rew, desc, ["MANPOWER", "ARMY_XP"] if "army" in rew else ["POLITICAL"])
F("crush_the_student_movement", "Crush the Student Movement", 14, 5, [["henrys_officers"]], [], 8, "duo:Generic_Arrests", "NOT = { has_country_flag = VIT_war_started }",
  CRUSH,
  "Henry's guard raids the cafés of Simeonovo at dawn. Yani is not there. By noon his followers hold the whole east of "
  "the mountain, and by evening it is war.\\n\\nThe civil war begins. Yani's rebels, communist or fascist, take Simeonovo, "
  "Malinova Dolina, Dragalevtsi, Dragalevtsi Lift and Orehite. Support is split evenly between democracy and Henry's "
  "authoritarian rule: then choose his road.", ["POLITICAL", "WAR_SUPPORT"])

YCHAIN = [
    ("the_cafes_of_simeonovo", "The Cafés of Simeonovo", 46, 1, [["march_with_yani"]], 6, "person:the_cafes_of_simeonovo",
     "add_political_power = 75",
     "Every evening, a table at the back, a pot of coffee and Yani talking. Every evening a few more chairs."),
    ("cells_in_simeonovo", "Cells in Simeonovo", 46, 2, [["the_cafes_of_simeonovo"]], 8, "duo:Generic_Espionage",
     "add_political_power = 25",
     "Rifles under the floorboards, a printing press in a garage and a list of names.\\n\\nWhen the war comes we get four "
     "more divisions in Simeonovo."),
    ("students_from_plovdiv", "Students from Plovdiv", 45, 3, [["cells_in_simeonovo"]], 7, "duo:Generic_Volunteer_Corps",
     "add_political_power = 25",
     "Every train from Plovdiv brings a few more of Yani's old classmates, with a suitcase and an address in Simeonovo."
     "\\n\\nWhen the war comes we get 20,000 manpower and the spirit Students from Plovdiv (more recruits)."),
    ("arms_from_plovdiv", "Arms from Plovdiv", 47, 3, [["cells_in_simeonovo"]], 6, "duo:Generic_Shady_Deal",
     "add_political_power = 25",
     "Tobacco crates from Plovdiv are heavier than tobacco.\\n\\nWhen the war comes we get 2,500 rifles."),
    ("the_plovdiv_committee", "The Plovdiv Committee", 46, 4, [["students_from_plovdiv"], ["arms_from_plovdiv"]], 8,
     "duo:Generic_Secret_Meeting", "add_political_power = 25",
     "Seven people in a back room, one map of the mountain and a date circled in red.\\n\\nWhen the war comes we get "
     "more war support and 20 army experience."),
]
for fid, name, x, y, pre, w, icon, rew, desc in YCHAIN:
    F(fid, name, x, y, pre, [], w, icon, "NOT = { has_country_flag = VIT_war_started }", rew, desc, ["POLITICAL"])
F("yani_takes_the_villa", "Yani Takes the Villa", 46, 5, [["the_plovdiv_committee"]], [], 8, "duo:Generic_Violent_Coup", "NOT = { has_country_flag = VIT_war_started }",
  TAKE_THE_VILLA,
  "At midnight Yani's people walk through the villa's gate. Henry walks out of the back door with his guard and his "
  "mother, and by morning he holds Boyana and the whole west of the mountain.\\n\\nYani becomes leader and the civil "
  "war begins: Henry's loyalists take Boyana and the west, ten states in all, with the stronger army. Our capital moves "
  "to Simeonovo. Support is split evenly between communism and fascism: then choose Yani's road.",
  ["POLITICAL", "WAR_SUPPORT"])


# ================================================================== the war branches (one per side, like Spain's middle trunks)
def war_trunk(p, cx, side_flag, heads, T, icons, news, push_idea, temp_templates):
    """The war branch of one side: it hangs under both of the side's ideology heads, takes down The Mountain in
    Flames during the war and repairs the scars of war afterwards. T: (name, desc) per slot; icons: one per slot."""
    k = ["head", "command", "workshops", "reserves", "line", "telephones", "factory", "volunteers", "patrols",
         "martial_law", "guns", "counter", "final_push", "won", "rebuild", "amnesty", "restored",
         "dig_in", "mortars", "trench_raids", "lorries", "repair_factories", "reequip", "railways", "retrain", "veterans"]
    i = {n: f"{p}_{n}" for n in k}
    lay = {"head": (cx, 7, [heads]),
           "command": (cx - 3, 8, [[i["head"]]]), "workshops": (cx, 8, [[i["head"]]]), "reserves": (cx + 3, 8, [[i["head"]]]),
           "line": (cx - 4, 9, [[i["command"]]]), "telephones": (cx - 2, 9, [[i["command"]]]), "factory": (cx, 9, [[i["workshops"]]]),
           "volunteers": (cx + 2, 9, [[i["reserves"]]]), "patrols": (cx + 4, 9, [[i["reserves"]]]),
           "martial_law": (cx - 3, 10, [[i["line"], i["telephones"]]]), "guns": (cx, 10, [[i["factory"]]]),
           "counter": (cx + 3, 10, [[i["volunteers"], i["patrols"]]]),
           "dig_in": (cx - 3, 11, [[i["martial_law"]]]), "final_push": (cx, 11, [[i["martial_law"], i["counter"]], [i["guns"]]]),
           "mortars": (cx + 3, 11, [[i["counter"]]]),
           "trench_raids": (cx - 4, 12, [[i["dig_in"]]]), "won": (cx, 12, [[i["final_push"]]]), "lorries": (cx + 4, 12, [[i["mortars"]]]),
           "repair_factories": (cx - 4, 13, [[i["won"]]]), "rebuild": (cx - 2, 13, [[i["won"]]]), "amnesty": (cx + 2, 13, [[i["won"]]]),
           "reequip": (cx + 4, 13, [[i["won"]]]),
           "railways": (cx - 3, 14, [[i["repair_factories"]]]), "restored": (cx, 14, [[i["rebuild"]], [i["amnesty"]]]),
           "retrain": (cx + 3, 14, [[i["reequip"]]]),
           "veterans": (cx, 15, [[i["railways"], i["restored"], i["retrain"]]])}
    delete_temps = "\n".join(f'delete_unit_template_and_units = {{ division_template = "{t}" }}' for t in temp_templates)
    rew = {
        "head": "add_war_support = 0.05\nadd_political_power = 50",
        "command": FLAMES_DOWN + "\narmy_experience = 15",
        "workshops": FLAMES_DOWN + "\nadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1000 }",
        "reserves": "add_manpower = 10000",
        "line": "capital_scope = { add_building_construction = { type = bunker level = 2 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
        "telephones": f"army_experience = 20\nadd_tech_bonus = {{ name = VIT_{p}_telephones bonus = 1.0 uses = 1 category = land_doctrine }}",
        "factory": factory("arms_factory"),
        "volunteers": "add_manpower = 15000\nadd_war_support = 0.05",
        "patrols": f"add_ideas = VIT_{p}_patrols",
        "martial_law": FLAMES_DOWN + "\nadd_stability = 0.05",
        "guns": f"add_tech_bonus = {{ name = VIT_{p}_guns bonus = 1.0 uses = 1 category = artillery }}\n"
                "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }",
        "counter": f"add_timed_idea = {{ idea = VIT_{p}_counter days = 180 }}",
        "dig_in": f"add_timed_idea = {{ idea = VIT_{p}_dig_in days = 180 }}",
        "mortars": f"add_tech_bonus = {{ name = VIT_{p}_mortars bonus = 1.0 uses = 1 category = support_tech }}\n"
                   "add_equipment_to_stockpile = { type = support_equipment_1 amount = 300 }",
        "final_push": f"add_timed_idea = {{ idea = {push_idea} days = 120 }}\narmy_experience = 25",
        "trench_raids": "army_experience = 20\nadd_war_support = 0.03",
        "lorries": "add_equipment_to_stockpile = { type = motorized_equipment_1 amount = 50 }\n"
                   f"add_tech_bonus = {{ name = VIT_{p}_lorries bonus = 1.0 uses = 1 category = motorized_equipment }}",
        "won": FLAMES_OUT + "\nif = { limit = { OR = { has_cosmetic_tag = VIT_HENRY has_cosmetic_tag = VIT_YANI } } drop_cosmetic_tag = yes }\n" + CAPITAL_HOME + "\n" + delete_temps + "\nadd_ideas = VIT_scars_of_war_2\n"
               "add_stability = 0.15\nadd_political_power = 100\nset_country_flag = VIT_war_over\n"
               f"news_event = {{ id = evil_sofia_vit_news.{news} hours = 6 }}",
        "repair_factories": SCARS_DOWN + "\n" + factory("industrial_complex"),
        "rebuild": "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }\n" + factory("industrial_complex"),
        "amnesty": "add_stability = 0.10\nadd_manpower = 10000",
        "reequip": SCARS_DOWN + "\nadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 3000 }\n"
                   "add_equipment_to_stockpile = { type = support_equipment_1 amount = 300 }",
        "railways": "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }\n" + factory("arms_factory"),
        "restored": "add_political_power = 150\nadd_stability = 0.05\nadd_research_slot = 1",
        "retrain": f"army_experience = 30\nadd_tech_bonus = {{ name = VIT_{p}_retrain bonus = 1.0 uses = 2 category = land_doctrine }}",
        "veterans": f"add_ideas = VIT_{p}_veterans",
    }
    filt = {"head": ["WAR_SUPPORT"], "command": ["ARMY_XP", "STABILITY"], "workshops": ["INDUSTRY", "STABILITY"],
            "reserves": ["MANPOWER"], "line": ["INDUSTRY"], "telephones": ["ARMY_XP", "RESEARCH"], "factory": ["INDUSTRY"],
            "volunteers": ["MANPOWER"], "patrols": ["ARMY_XP"], "martial_law": ["STABILITY"], "guns": ["RESEARCH", "INDUSTRY"],
            "counter": ["ARMY_XP"], "dig_in": ["ARMY_XP"], "mortars": ["RESEARCH"], "final_push": ["ARMY_XP"],
            "trench_raids": ["ARMY_XP", "WAR_SUPPORT"], "lorries": ["RESEARCH", "INDUSTRY"], "won": ["STABILITY"],
            "repair_factories": ["INDUSTRY"], "rebuild": ["INDUSTRY"], "amnesty": ["STABILITY", "MANPOWER"],
            "reequip": ["ARMY_XP", "INDUSTRY"], "railways": ["INDUSTRY"], "restored": ["POLITICAL", "RESEARCH"],
            "retrain": ["ARMY_XP", "RESEARCH"], "veterans": ["ARMY_XP"]}
    weeks = {"head": 5, "command": 7, "workshops": 8, "reserves": 6, "line": 7, "telephones": 7, "factory": 9, "volunteers": 6,
             "patrols": 7, "martial_law": 8, "guns": 8, "counter": 7, "dig_in": 6, "mortars": 7, "final_push": 9,
             "trench_raids": 6, "lorries": 8, "won": 6, "repair_factories": 9, "rebuild": 9, "amnesty": 7, "reequip": 8,
             "railways": 8, "restored": 10, "retrain": 8, "veterans": 10}
    for n in k:
        name, desc = T[n]
        if n in ("command", "workshops", "martial_law"):
            desc += FLAMES_TT
        if n in ("repair_factories", "reequip"):
            desc += "\\n\\nTakes the Scars of War down one step."
        avail = ""
        if n == "won":
            avail = "has_country_flag = VIT_war_started\nhas_civil_war = no"
            desc += ("\\n\\nNeeds the civil war won. Removes what is left of The Mountain in Flames, sends the hired and "
                     "volunteer divisions home and leaves the Scars of War, which the repair focuses heal.")
        elif n in ("dig_in", "trench_raids", "final_push", "counter"):
            avail = "has_civil_war = yes"
        F(i[n], name, lay[n][0], lay[n][1], lay[n][2], [], weeks[n], icons[n], avail, rew[n], desc, filt[n])


war_trunk("h", 14, "VIT_henry_side", ["what_the_english_couldnt_do", "what_zevka_wanted"], {
    "head": ("The Loyal Guard", "Whichever road Henry takes, the guard that held the villa becomes the army that will hold the mountain."),
    "command": ("Restore the Chain of Command", "Half the officers changed sides, the other half are not answering the telephone. A list of who is still loyal and a lot of shouting."),
    "workshops": ("Requisition the Villas", "Every garage in Boyana becomes a workshop. The owners are promised compensation after the war, in writing, on Henry's best paper."),
    "reserves": ("Call the Reserves", "Every man who ever wore the guard's uniform is called back to it."),
    "line": ("The Boyana Line", "Trenches across the slopes, concrete at the crossroads and barbed wire through the vineyards."),
    "telephones": ("Field Telephones", "A wire from the villa to every company on the front. Henry phones them all personally."),
    "factory": ("The Villa Workshops", "The biggest garage in Boyana makes rifles now."),
    "volunteers": ("Volunteers from the City", "Young men from all over Sofia take the tram to the end of the line and walk up the mountain to join Henry."),
    "patrols": ("The Ski Patrols", "In winter the fastest way across the front is on skis. The guard learns."),
    "martial_law": ("Martial Law on the Slopes", "Curfews, checkpoints and courts that sit at night. The villages behind the front stop arguing."),
    "guns": ("Guns on the Ridges", "Every ridge of Vitosha looks down on the rebels' villages. A gun on each of them settles a lot of arguments."),
    "counter": ("The Counteroffensive", "Henry has waited long enough. The guard goes over to the attack.\\n\\nOnly during the civil war."),
    "dig_in": ("Hold Every Ridge", "Not one metre of the mountain is given up without a fight.\\n\\nOnly during the civil war."),
    "mortars": ("Mortars in the Vineyards", "A mortar fits between two rows of vines and can reach the next village."),
    "final_push": ("Take Simeonovo", "The cafés where it all started. Henry wants to have a coffee there when it is over.\\n\\nOnly during the civil war."),
    "trench_raids": ("Trench Raids at Night", "Small parties with knives and grenades, back before dawn with prisoners and stories.\\n\\nOnly during the civil war."),
    "lorries": ("Lorries on the Mountain Road", "Every delivery lorry in Boyana now carries soldiers up and down the mountain."),
    "won": ("The Mountain Is Ours", "The last shots echo across the forest and the mountain is quiet. Henry has won his war."),
    "repair_factories": ("Repair the Factories", "Glass in the windows, roofs on the halls and the machines running again."),
    "rebuild": ("Rebuild the Slopes", "New roads, new roofs and a factory where the worst of the fighting was."),
    "amnesty": ("An Amnesty for the Students", "Henry forgives most of them. He keeps a list of the rest."),
    "reequip": ("Re-equip the Guard", "New rifles, new boots and new helmets for every man who fought."),
    "railways": ("Restore the Railways", "The little railway to Vladaya runs again, and so does the arms factory at the end of it."),
    "restored": ("The Mountain Restored", "The villa is repainted, the guard is back in its barracks and Henry's mother has taken down the sandbags. Mostly."),
    "retrain": ("Lessons of the Civil War", "Every officer writes down what went wrong. Henry reads all of it."),
    "veterans": ("Veterans of the Mountain", "The men who fought for the villa march past it every year, and the city below remembers them."),
}, {
    "head": "duo:goal_generic_special_forces", "command": "duo:Generic_Radio_Operator", "workshops": "duo:Generic_Underground_Factories",
    "reserves": "duo:focus_generic_commonwealth_build_infantry", "line": "duo:goal_generic_defence",
    "telephones": "duo:Generic_Radio_Communication", "factory": "duo:goal_generic_production", "volunteers": "duo:Generic_Morale_Bonus_Focus",
    "patrols": "duo:Generic_Lookout", "martial_law": "duo:goal_generic_imprison_people", "guns": "duo:Generic_Artillery_Barrel",
    "counter": "duo:goal_generic_position_armies", "dig_in": "duo:Generic_Crouched_Soldier_German", "mortars": "duo:goal_generic_army_artillery2",
    "final_push": "duo:goal_generic_occypy_start_war", "trench_raids": "duo:Generic_ENG_SAS", "lorries": "duo:Generic_Purchase_Tanks_Focus",
    "won": "duo:Generic_Memories_of_the_War", "repair_factories": "duo:goal_generic_german_construction",
    "rebuild": "duo:goal_generic_construction", "amnesty": "duo:Generic_Bread_and_Peace", "reequip": "duo:goal_generic_axis_build_infantry",
    "railways": "duo:goal_generic_railway_construction", "restored": "duo:goal_generic_stable_government",
    "retrain": "duo:goal_generic_army_doctrines", "veterans": "duo:Generic_War_Propaganda05",
}, 2, "VIT_h_push", ["Hired Guard", "Friends of the Villa", "Club Volunteers"])

war_trunk("y", 46, "VIT_yani_side", ["red_plovdiv", "the_seven_hills"], {
    "head": ("The Plovdiv Brigades", "Red or black, Yani's army is born in a week: students, tobacco workers and anyone else with a rifle."),
    "command": ("Officers from the Cafés", "Yani's best talkers become his first officers. Some of them are even good at it."),
    "workshops": ("Workshops of Simeonovo", "Every workshop on our side of the mountain now makes one thing: what the front needs."),
    "reserves": ("Every Village a Barracks", "Every village in the east sends its young men up the hill."),
    "line": ("Dig In at Dragalevtsi", "The monastery walls above Dragalevtsi have stopped armies before."),
    "telephones": ("Couriers on Bicycles", "No telephones, no radios, but every student owns a bicycle."),
    "factory": ("The Orehite Arsenal", "A fruit warehouse in Orehite makes grenades now. It still smells of apples."),
    "volunteers": ("Volunteers from the Lowlands", "Workers from Mladost and Pancharevo walk up the mountain road to join Yani."),
    "patrols": ("The Night Raids", "Henry's guard owns the day. Yani's people own the night."),
    "martial_law": ("Revolutionary Discipline", "Committees, curfews and a firing squad that is mostly a threat."),
    "guns": ("Guns from the Quarries", "Quarry explosives make very good shells, if you are not too fussy."),
    "counter": ("The Storm of Boyana", "Everything we have, at once, toward the villa.\\n\\nOnly during the civil war."),
    "dig_in": ("Not a Step Back", "Every house in Simeonovo is a fortress, and every fortress has a student in the window.\\n\\nOnly during the civil war."),
    "mortars": ("Mortars from the Workshops", "Drainpipes, a firing pin and a lot of courage."),
    "final_push": ("Take the Villa Back", "Henry's last stand is in his own house. Yani wants to sleep in it.\\n\\nOnly during the civil war."),
    "trench_raids": ("Partisans behind the Lines", "Yani's people know every path behind Henry's front.\\n\\nOnly during the civil war."),
    "lorries": ("The Fruit Lorries", "The orchard lorries of Orehite carry troops now, still smelling of apples."),
    "won": ("The Mountain Is Ours", "The last shots echo across the forest and the mountain is quiet. The student from Plovdiv has won his war."),
    "repair_factories": ("Repair the Workshops", "The workshops that made shells during the war make tractors and radios again."),
    "rebuild": ("Rebuild the Villages", "The east of the mountain did the fighting. It gets the new roads and the new factory."),
    "amnesty": ("Mercy for the Guard", "Henry's guardsmen are sent home, minus their rifles and their pride."),
    "reequip": ("Rifles for the New Army", "Henry's old arsenal, captured whole, equips the army that beat him."),
    "railways": ("The Mountain Railway", "A narrow railway from Simeonovo to Knyazhevo, built by the people who fought over it."),
    "restored": ("The Mountain Restored", "The villa becomes a rest home, the guard becomes a militia and Yani finally gets some sleep."),
    "retrain": ("The Staff College in the Villa", "Henry's dining room is now a lecture hall for Yani's officers."),
    "veterans": ("Heroes of Simeonovo", "Every street in Simeonovo is named after someone who fought for it."),
}, {
    "head": "duo:Generic_Revolutionary_Republic", "command": "duo:Generic_Socialist_Volunteers", "workshops": "duo:goal_generic_industry_reallocation",
    "reserves": "duo:Generic_Refugees", "line": "duo:goal_generic_home_defense_bel", "telephones": "duo:Generic_Railroads",
    "factory": "duo:goal_generic_production2", "volunteers": "duo:Generic_Urban_Partisans", "patrols": "duo:Generic_Disguise",
    "martial_law": "duo:Generic_Executions", "guns": "duo:goal_generic_build_tank", "counter": "duo:goal_generic_major_war",
    "dig_in": "duo:Generic_Russian_Soldier", "mortars": "duo:focus_generic_tank_destroyer", "final_push": "duo:goal_generic_attack_allies",
    "trench_raids": "duo:Generic_Russian_Partisan", "lorries": "duo:Generic_Industry_Tanks", "won": "duo:Generic_Cincinnatus",
    "repair_factories": "duo:goal_generic_workers_democracy", "rebuild": "duo:goal_generic_construct_public_housing",
    "amnesty": "duo:Generic_Red_Cross", "reequip": "duo:goal_generic_war_in_the_plate", "railways": "duo:focus_generic_aluminum",
    "restored": "duo:goal_generic_civilian_oversight", "retrain": "duo:goal_generic_army_tanks2", "veterans": "duo:Generic_Female_Commander",
}, 3, "VIT_y_push", ["Plovdiv Column", "Classmates", "Studentski Volunteers"])

# ================================================================== Henry: What the English Couldn't Do (democratic, like the UK)
HDEM = [
    ("what_the_english_couldnt_do", "What the English Couldn't Do", 4, 6, [["crush_the_student_movement"]], 8, "duo:Generic_Big_Ben02",
     "set_politics = { ruling_party = democratic elections_allowed = yes }\n" + henry_role("conservatism", True)
     + "\nadd_ideas = VIT_half_english\nadd_country_leader_trait = evil_sofia_half_english",
     "Henry's father's family has run things the English way for three hundred years: parliaments, tea at five and never "
     "raising your voice. Henry has watched them closely, and he is quite sure he can do it better. Westminster had "
     "centuries. Vitosha has Henry.\\n\\nVitosha becomes a democracy under Henry.", ["POLITICAL", "STABILITY"]),
    ("tea_at_five", "Tea at Five", 1, 7, [["what_the_english_couldnt_do"]], 5, "duo:Generic_Tea_Farming", "add_stability = 0.05\nadd_political_power = 50",
     "Whatever happens at the front, the whole district stops for tea at five. Somehow this calms everyone down.", ["STABILITY"]),
    ("parliament_in_boyana", "The Parliament in Boyana", 4, 7, [["what_the_english_couldnt_do"]], 9, "duo:Generic_Parliament_Box",
     "add_political_power = 100\nadd_stability = 0.03",
     "Forty seats in the old church hall in Boyana, a speaker with a wig he made himself and very long debates.", ["POLITICAL"]),
    ("the_home_guard", "The Home Guard", 7, 7, [["what_the_english_couldnt_do"]], 8, "duo:focus_generic_home_defense",
     "add_ideas = VIT_home_guard\nadd_manpower = 10000",
     "Every man too old or too young for the army gets an armband and a rifle and guards his own street.", ["MANPOWER"]),
    ("the_boyana_charter", "The Boyana Charter", 0, 8, [["tea_at_five"]], 7, "duo:Generic_Legislation", "add_stability = 0.05\nadd_political_power = 75",
     "England has Magna Carta. Vitosha has the Boyana Charter, written by Henry on the back of a menu, and it is shorter.", ["POLITICAL", "STABILITY"]),
    ("radio_vitosha_calling", "Radio Vitosha Calling", 2, 8, [["tea_at_five"]], 6, "duo:Generic_Radio_Broadcast",
     "every_neighbor_country = { add_timed_idea = { idea = VIT_radio_vitosha days = 180 } }",
     "This is Radio Vitosha. Every evening, news from the free mountain for every district of Sofia.\\n\\nDemocracy grows "
     "slowly in every neighbour for six months.", ["POLITICAL"]),
    ("the_mountain_conference", "The Mountain Conference", 4, 8, [["parliament_in_boyana"]], 8, "duo:focus_generic_little_entente",
     "OR = { is_in_faction = no is_faction_leader = yes }", "if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_FACTION_MOUNTAIN_ENTENTE }\nadd_political_power = 50",
     "Henry invites the free districts of Sofia to a conference at the villa: three days of speeches, two of lunch and "
     "one alliance.\\n\\nCreates the faction The Mountain Entente.", ["POLITICAL"]),
    ("fighters_over_vitosha", "Fighters over Vitosha", 6, 8, [["the_home_guard"]], 8, "duo:Generic_Pilots",
     "air_experience = 25\ncapital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }",
     "A grass strip in the meadows below Aleko and a few aeroplanes. Henry calls it the Royal Air Force of the Mountain.",
     ["AIR_XP"]),
    ("rule_the_reservoirs", "Rule the Reservoirs", 8, 8, [["the_home_guard"]], 8, "duo:Generic_Maritime", NOWAR, "{CLAIMS:PNC}\n{WAR:PNC}",
     "England ruled the waves. Vitosha will rule the lake at Pancharevo, which is a start.\\n\\nClaims and war goals on "
     "Pancharevo.", ["ANNEXATION"]),
    ("a_cabinet_of_all_talents", "A Cabinet of All Talents", 0, 9, [["the_boyana_charter"]], 7, "duo:Generic_Democracy",
     "add_ideas = VIT_cabinet_of_talents",
     "A minister from every village, including two who used to follow Yani. Henry keeps an eye on those two.", ["POLITICAL"]),
    ("guarantees_for_the_small", "Guarantees for the Small", 2, 9, [["radio_vitosha_calling"], ["the_mountain_conference"]], 6,
     "duo:focus_generic_treaty", "",
     "every_neighbor_country = {\n\tlimit = { is_in_faction = no NOT = { has_war_with = ROOT } }\n\tROOT = { give_guarantee = PREV }\n}",
     "No small district next to Vitosha will be swallowed while Henry has anything to say about it.\\n\\nWe guarantee "
     "every neighbour outside a faction.", ["POLITICAL"]),
    ("invite_the_free_districts", "Invite the Free Districts", 4, 9, [["the_mountain_conference"]], 7, "duo:Generic_Mutual_Cooperation",
     "is_faction_leader = yes", invite(7),
     "A letter to every district of Sofia that is not in an alliance: join the Mountain Entente.\\n\\nEach is likelier to "
     "join the more democratic it is and the better it thinks of us.", ["POLITICAL"]),
    ("radar_on_cherni_vrah", "Radar on Cherni Vrah", 6, 9, [["fighters_over_vitosha"]], 7, "duo:Generic_Radar_Station",
     "capital_scope = { add_building_construction = { type = radar_station level = 2 instant_build = yes } }",
     "From the top of Cherni Vrah you can see every aeroplane over Sofia. Now you can see them in the dark as well.", ["AIR_XP"]),
    ("the_thin_red_line", "The Thin Blue Line", 8, 9, [["rule_the_reservoirs"]], 8, "duo:Generic_Soldier_Aiming",
     "add_tech_bonus = { name = VIT_thin_line bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 20",
     "The English had a thin red line. Henry's guard wears blue, and its line is a little thicker.", ["ARMY_XP", "RESEARCH"]),
    ("the_special_relationship", "The Special Relationship", 1, 10, [["a_cabinet_of_all_talents"], ["guarantees_for_the_small"]], 7,
     "duo:goal_generic_improve_relations", "",
     "every_country = {\n\tlimit = { has_government = democratic NOT = { tag = ROOT } }\n"
     "\tadd_opinion_modifier = { target = ROOT modifier = evil_sofia_free_friends }\n}",
     "Henry writes a personal letter to every democratic leader in Sofia. He signs each of them 'your friend on the hill'."
     "\\n\\nEvery democracy thinks better of us.", ["POLITICAL"]),
    ("lend_lease", "Lend to Our Friends", 4, 10, [["invite_the_free_districts"]], 6, "duo:Generic_Outside_Aid", "",
     "every_other_country = {\n\tlimit = { is_in_faction_with = ROOT }\n\tadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 500 }\n}",
     "Rifles from the mountain for every friend who needs them. They can pay us back later.\\n\\nEvery member of our "
     "faction gets 500 rifles.", ["INDUSTRY"]),
    ("spitfires_of_the_mountain", "Spitfires of the Mountain", 6, 10, [["radar_on_cherni_vrah"]], 8, "duo:Generic_Female_Pilots",
     "add_tech_bonus = { name = VIT_spitfires bonus = 1.0 uses = 1 category = air_equipment }",
     "The best fighters in Sofia, built in a hangar in Knyazhevo and named after Henry's mother's temper.", ["AIR_XP", "RESEARCH"]),
    ("dominion_status", "Dominion Status", 8, 10, [["the_thin_red_line"]], 8, "duo:Generic_Redraw_Borders", NOWAR, "{CLAIMS:OVK}\n{WAR:OVK}",
     "Ovcha Kupel lies at the foot of the mountain and would make an excellent dominion.\\n\\nClaims and war goals on "
     "Ovcha Kupel.", ["ANNEXATION"]),
    ("fight_on_the_slopes", "We Shall Fight on the Slopes", 2, 11, [["the_special_relationship"], ["lend_lease"]], 9,
     "duo:Generic_British_Soldiers03", "", "add_ideas = VIT_fight_on_the_slopes",
     "We shall fight in the villas, we shall fight in the forests, we shall fight on the ski runs. We shall never surrender.",
     ["WAR_SUPPORT", "ARMY_XP"]),
    ("the_mountain_pound", "The Mountain Pound", 4, 11, [["lend_lease"]], 8, "duo:Generic_Monopoly", "",
     factory("industrial_complex") + "\nadd_political_power = 50",
     "A currency of our own, with Henry on the notes and the mountain on the coins. The banks of Sofia take it, mostly.",
     ["INDUSTRY"]),
    ("the_mountain_air_ministry", "The Mountain Air Ministry", 6, 11, [["spitfires_of_the_mountain"]], 8, "duo:goal_generic_air_production",
     factory("arms_factory") + "\nair_experience = 25",
     "A ministry for aeroplanes, with its own factory and a minister who is never seen on the ground.", ["AIR_XP", "INDUSTRY"]),
    ("commonwealth_of_the_mountain", "The Commonwealth of the Mountain", 5, 12, [["fight_on_the_slopes", "the_mountain_pound"], ["dominion_status"]], 12,
     "duo:focus_generic_bastion_of_democracy", "{HELD:VIT,OVK,PNC}\n" + NOWAR,
     "{COREHELD:VIT:OVK,PNC}\nset_cosmetic_tag = VIT_COMMONWEALTH\nswap_ideas = { remove_idea = VIT_half_english add_idea = VIT_commonwealth }\n"
     "add_research_slot = 1\nnews_event = { id = evil_sofia_vit_news.4 hours = 6 }",
     "From the lake at Pancharevo to the fields of Ovcha Kupel, the mountain and its dominions form one Commonwealth, with "
     "Henry at its head. Westminster never managed anything this tidy.\\n\\nNeeds Vitosha, Ovcha Kupel and Pancharevo "
     "held. Vitosha becomes the Commonwealth of the Mountain and cores the land it holds.", ["POLITICAL", "RESEARCH"]),
    ("finest_hour", "Our Finest Hour", 3, 13, [["commonwealth_of_the_mountain"]], 10, "duo:Generic_War_Propaganda02", "",
     "add_ideas = VIT_finest_hour",
     "If the Commonwealth lasts for a thousand years, people will still say: this was its finest hour.", ["WAR_SUPPORT", "STABILITY"]),
    ("the_vitosha_charter", "The Vitosha Charter", 5, 13, [["commonwealth_of_the_mountain"]], 9, "duo:goal_generic_support_democracy", "",
     "every_country = {\n\tlimit = { has_government = democratic NOT = { tag = ROOT } is_in_faction = no }\n\tcountry_event = { id = evil_sofia_vit.7 }\n}"
     "\nadd_political_power = 50",
     "Henry and his friends sign a charter on a ship. The ship is a rowing boat on the Pancharevo lake, but the charter "
     "is very grand.\\n\\nEvery democracy outside an alliance is invited to the Mountain Entente.", ["POLITICAL"]),
    ("the_sun_never_sets", "The Sun Never Sets on the Mountain", 7, 13, [["commonwealth_of_the_mountain"]], 10,
     "duo:Generic_Global_Hegemony", NOWAR, "\n".join(
         f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} is_in_faction_with = {t} }} }} "
         f"create_wargoal = {{ type = puppet_wargoal_focus target = {t} }} }}" for t in ("LOZ", "STU", "MLA")),
     "There is always somewhere on the Commonwealth where the sun is shining. Usually it is the top of the mountain. "
     "The districts below it do not have to be conquered: they can be dominions.\\n\\nWar goals to make Lozenets, "
     "Studentski and Mladost our dominions (puppets).", ["ANNEXATION"]),
    ("an_offer_of_dominion", "An Offer of Dominion", 3, 14, [["finest_hour"]], 8, "duo:Generic_Big_Blue_Blob", NOWAR,
     "every_neighbor_country = {\n\tlimit = { has_government = democratic is_in_faction = no is_subject = no NOT = { has_war_with = ROOT } }\n"
     "\tcountry_event = { id = evil_sofia_vit.26 }\n}",
     "Henry writes to every free district next to the mountain: join the Commonwealth as a dominion, keep your own "
     "parliament, and never worry about defence again.\\n\\nEvery democratic neighbour outside an alliance is offered "
     "dominion status. The weaker it is and the better it thinks of us, the likelier it says yes.", ["ANNEXATION", "POLITICAL"]),
    ("better_than_westminster", "Better Than Westminster", 5, 14, [["finest_hour", "the_vitosha_charter", "the_sun_never_sets"]], 12,
     "duo:Generic_Liberalism", "", "add_ideas = VIT_better_than_westminster\nadd_stability = 0.05",
     "A visiting English lord tours the villa, the parliament in Boyana and the meadow airfield, has his tea at five and "
     "admits, quietly, that they do it better on the mountain. Henry has the remark framed.", ["POLITICAL", "STABILITY"]),
]
# ================================================================== Henry: What Zevka Wanted (authoritarian)
HAUT = [
    ("what_zevka_wanted", "What Zevka Wanted", 24, 6, [["crush_the_student_movement"]], 8, "duo:Generic_Family", "add_ideas = VIT_grandmas_rules",
     "Henry's Bulgarian grandmother Zevka had firm views on everything: the church on Sunday, dinner at midnight, the land "
     "in the family and a strong hand at the top. She never lived to see the mountain run properly. Henry will see to it."
     "\\n\\nHenry keeps his authoritarian rule.", ["POLITICAL", "STABILITY"]),
    ("bells_of_boyana_church", "The Bells of Boyana Church", 21, 7, [["what_zevka_wanted"]], 6, "duo:Generic_Bell_Tolls",
     "add_stability = 0.05\nadd_political_power = 50",
     "The little medieval church at Boyana rings its bells again on Sunday, and the whole district goes.", ["STABILITY"]),
    ("dinner_at_midnight", "Dinner at Midnight", 24, 7, [["what_zevka_wanted"]], 5, "duo:Generic_Nuclear_Family", "add_political_power = 75",
     "Zevka's family never ate before midnight, and nobody left the table angry. Henry's ministers now dine with him at "
     "midnight. They are very tired, and very loyal.", ["POLITICAL"]),
    ("the_mountain_militia", "The Mountain Militia", 27, 7, [["what_zevka_wanted"]], 8, "duo:Generic_Partisan",
     "add_manpower = 15000\narmy_experience = 15",
     "Every village on the slopes raises a company of its own, under its own priest and its own mayor.", ["MANPOWER"]),
    ("monks_of_dragalevtsi", "The Monks of Dragalevtsi", 20, 8, [["bells_of_boyana_church"]], 7, "duo:Generic_Piety", "add_ideas = VIT_monks_of_dragalevtsi",
     "The monastery above Dragalevtsi has hidden rebels and saints for five hundred years. Now it blesses Henry's banners.",
     ["STABILITY", "WAR_SUPPORT"]),
    ("zevkas_catechism", "Zevka's Catechism", 22, 8, [["bells_of_boyana_church"]], 6, "duo:Generic_Christianity",
     "add_stability = 0.05\nadd_war_support = 0.03",
     "Every child on the mountain learns the same seven rules Zevka taught Henry. Rule four is about eating your soup.", ["STABILITY"]),
    ("land_for_the_villages", "Land for the Villages", 24, 8, [["dinner_at_midnight"]], 8, "duo:Generic_Land_Reform",
     "add_political_power = 50\nadd_manpower = 5000\nadd_stability = 0.03",
     "The fields the rebels took are given back to the families who worked them, as Zevka would have wanted.", ["STABILITY"]),
    ("the_old_officers", "The Old Officers", 26, 8, [["the_mountain_militia"]], 8, "duo:Generic_Imperial_Army",
     "add_tech_bonus = { name = VIT_old_officers bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 20",
     "Grey moustaches, old medals and a very clear idea of how a war should be fought.", ["ARMY_XP", "RESEARCH"]),
    ("bunkers_on_kopitoto", "Bunkers on Kopitoto", 28, 8, [["the_mountain_militia"]], 8, "duo:focus_generic_coastal_fort",
     "capital_scope = { add_building_construction = { type = bunker level = 2 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
     "Kopitoto looks down on all of Sofia. Concrete on its top makes sure it stays that way.", ["INDUSTRY"]),
    ("the_family_council", "The Family Council", 21, 9, [["monks_of_dragalevtsi", "zevkas_catechism"]], 7, "duo:goal_generic_controlled_board",
     "add_ideas = VIT_family_council",
     "Henry governs with a council of aunts, uncles and cousins. They argue all night, and then do what Henry says.", ["POLITICAL"]),
    ("grandmas_larder", "Grandma's Larder", 24, 9, [["land_for_the_villages"]], 7, "duo:Generic_Canned_Fish",
     "add_ideas = VIT_grandmas_larder",
     "Pickles, jam and lyutenitsa for every family on the mountain, in jars, for the winter. Nobody goes hungry while "
     "Zevka's recipes are in charge.", ["STABILITY", "INDUSTRY"]),
    ("the_mountain_gendarmerie", "The Mountain Gendarmerie", 27, 9, [["the_old_officers", "bunkers_on_kopitoto"]], 8,
     "duo:Generic_Orthodox_Defense", "add_stability = 0.05\nadd_ideas = VIT_gendarmerie",
     "Policemen on horses in every village, and a horse for every policeman.", ["STABILITY"]),
    ("a_crown_in_the_attic", "A Crown in the Attic", 21, 10, [["the_family_council"]], 9, "duo:Generic_Crown_Box", "add_political_power = 100",
     "Clearing out Zevka's attic, Henry finds a box. In the box is an old crown, and a letter in his grandmother's hand: "
     "for when the mountain is ready.", ["POLITICAL"]),
    ("the_villages_rebuilt", "The Villages Rebuilt", 24, 10, [["grandmas_larder"]], 9, "duo:goal_generic_construct_infrastructure",
     "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }\n" + factory("industrial_complex"),
     "Stone houses, a well in every square and a road to every village, as Zevka remembered them.", ["INDUSTRY"]),
    ("the_lowlands_below", "The Lowlands Below", 27, 10, [["the_mountain_gendarmerie"]], 8, "duo:Generic_Revanchism", NOWAR,
     "{CLAIMS:OVK,PNC}\n{WAR:OVK,PNC}",
     "Every village at the foot of the mountain once paid its tithe to the monasteries on its slopes. Zevka never forgot it."
     "\\n\\nClaims and war goals on Ovcha Kupel and Pancharevo.", ["ANNEXATION"]),
    ("regent_of_the_mountain", "Regent of the Mountain", 21, 11, [["a_crown_in_the_attic"]], 8, "duo:Generic_Divine_Right",
     "add_country_leader_trait = evil_sofia_regent\nadd_stability = 0.05",
     "Henry does not put on the crown. Not yet. He governs as regent, in the crown's name, until the mountain is whole.",
     ["POLITICAL", "STABILITY"]),
    ("the_estates_of_knyazhevo", "The Estates of Knyazhevo", 24, 11, [["the_villages_rebuilt"]], 9, "duo:Generic_Construction",
     factory("arms_factory"),
     "The old estates in Knyazhevo get a foundry, and the foundry gets the best workers on the mountain.", ["INDUSTRY"]),
    ("march_into_the_valley", "March into the Valley", 27, 11, [["the_lowlands_below"]], 9, "duo:Generic_Invasion", NOWAR,
     "{CLAIMS:LOZ,TRD}\n{WAR:LOZ,TRD}",
     "Below the lowlands lies the city itself. Lozenets and Triaditsa are the first streets of Sofia that climb toward the "
     "mountain.\\n\\nClaims and war goals on Lozenets and Triaditsa.", ["ANNEXATION"]),
    ("the_crowns_army", "The Crown's Army", 21, 12, [["regent_of_the_mountain"]], 10, "duo:Generic_Ultranationalist_Monarchy",
     "add_ideas = VIT_crowns_army", "Every soldier of Vitosha now swears to the crown in the attic, whoever wears it one day.",
     ["ARMY_XP"]),
    ("the_league_of_the_mountain", "The League of the Mountain", 27, 12, [["march_into_the_valley"]], 8, "duo:goal_generic_military_deal",
     "OR = { is_in_faction = no is_faction_leader = yes }", "if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_FACTION_MOUNTAIN_LEAGUE }\n" + invite(16),
     "Every district that still has a strong hand at the top is invited to dinner at the villa. At midnight, of course."
     "\\n\\nCreates the League of the Mountain and invites every district outside an alliance; authoritarian ones are "
     "likelier to say yes.", ["POLITICAL"]),
    ("tsardom_of_the_mountain", "The Tsardom of the Mountain", 24, 13, [["the_crowns_army"], ["the_estates_of_knyazhevo", "the_league_of_the_mountain"]], 12,
     "duo:Generic_Imperial_Eagle", "{HELD:VIT,OVK,PNC}\n" + NOWAR,
     "{COREHELD:VIT:OVK,PNC}\nset_cosmetic_tag = VIT_TSARDOM\nadd_country_leader_trait = evil_sofia_tsar_of_the_mountain\n"
     "swap_ideas = { remove_idea = VIT_grandmas_rules add_idea = VIT_zevka_proud }\nadd_research_slot = 1\n"
     "news_event = { id = evil_sofia_vit_news.5 hours = 6 }",
     "In Boyana Church, under frescoes seven hundred years old, the crown from the attic is placed on Henry's head. Zevka's "
     "dream has come true: the Tsardom of the Mountain.\\n\\nNeeds Vitosha, Ovcha Kupel and Pancharevo held. Vitosha "
     "becomes the Tsardom of the Mountain, Henry its tsar, and cores the land it holds.", ["POLITICAL", "RESEARCH"]),
    ("zevka_would_be_proud", "Zevka Would Be Proud", 22, 14, [["tsardom_of_the_mountain"]], 8, "duo:Generic_Angel",
     "add_stability = 0.10\nadd_political_power = 150",
     "Henry visits her grave in Boyana every Sunday, with flowers and the news. He is sure she approves.", ["STABILITY"]),
    ("the_court_at_boyana", "The Court at Boyana", 24, 14, [["tsardom_of_the_mountain"]], 9, "duo:Generic_Crown_Kaiser",
     "add_research_slot = 1\nadd_political_power = 50",
     "Painters, scholars and a court poet who rhymes everything with Vitosha. It is harder than it sounds.", ["RESEARCH"]),
    ("the_throne_expands", "The Mountain Throne Expands", 26, 14, [["tsardom_of_the_mountain"]], 10, "duo:Generic_Unchecked_Expansionism",
     NOWAR, "{CLAIMS:BNK,KRP,VRB,LYU}\n{WAR:BNK,KRP,VRB,LYU}",
     "West of the mountain lie the old villages: Bankya with its springs, Vrabnitsa, Lyulin and Krasna Polyana. Zevka "
     "said they were always the tsar's, whatever the maps say.\\n\\nClaims and war goals on Bankya, Krasna Polyana, "
     "Vrabnitsa and Lyulin.", ["ANNEXATION"]),
    ("bells_over_sofia", "Bells over Sofia", 24, 15, [["zevka_would_be_proud", "the_court_at_boyana", "the_throne_expands"]], 12,
     "duo:Generic_Religious_Unity", "", "add_ideas = VIT_bells_over_sofia",
     "On the tsar's name day every church bell in Sofia rings at once, and every district hears it.", ["STABILITY", "POLITICAL"]),
]
# ================================================================== Yani: Red Plovdiv (communist)
YCOM = [
    ("red_plovdiv", "Red Plovdiv", 36, 6, [["yani_takes_the_villa"]], 8, "duo:Generic_Marxism",
     "add_ideas = VIT_vitosha_soviet\nadd_political_power = 50",
     "Yani grew up among the tobacco workers of Plovdiv and their strikes. He gives the mountain what they wanted: the "
     "land to the villages, the villas to the people, the hill to the workers.\\n\\nYani stays communist.", ["POLITICAL"]),
    ("the_tobacco_workers", "The Tobacco Workers", 33, 7, [["red_plovdiv"]], 8, "duo:Generic_Tobacco_Farming", factory("industrial_complex"),
     "Yani brings the tobacco workers of Plovdiv to the mountain: the best organised, most stubborn workers in Bulgaria.", ["INDUSTRY"]),
    ("the_red_mountain_guard", "The Red Mountain Guard", 36, 7, [["red_plovdiv"]], 8, "duo:Generic_Socialist_Soldier",
     "army_experience = 20\nadd_manpower = 15000",
     "The old guard is gone. The new one learned its trade in the war and its politics in Yani's cafés.", ["ARMY_XP", "MANPOWER"]),
    ("lectures_in_kapana", "Lectures in Kapana", 39, 7, [["red_plovdiv"]], 9, "duo:focus_generic_socialist_science", "add_research_slot = 1",
     "Kapana, the Trap, is Plovdiv's maze of craftsmen's streets. Yani builds a new one on the mountain, full of workshops "
     "and lecture halls.", ["RESEARCH"]),
    ("the_orchards_of_orehite", "The Orchards of Orehite", 32, 8, [["the_tobacco_workers"]], 7, "duo:Generic_Farming",
     "add_stability = 0.05\nadd_political_power = 50",
     "The orchards of Orehite belonged to six families. Now they belong to everyone, and the apples are just as good.", ["STABILITY"]),
    ("the_plovdiv_fair", "The Plovdiv Fair", 34, 8, [["the_tobacco_workers"]], 8, "duo:Generic_Market_Socialism", factory("industrial_complex"),
     "Plovdiv has held a great fair every year since the last century. Yani holds one on the mountain: tractors, lathes "
     "and very long speeches.", ["INDUSTRY"]),
    ("commissars_of_the_slopes", "Commissars of the Slopes", 36, 8, [["the_red_mountain_guard"]], 7, "duo:Generic_Militant_Socialism",
     "add_ideas = VIT_commissars",
     "A commissar with every company, a pamphlet in every pack.", ["ARMY_XP"]),
    ("partisans_of_vitosha", "The Partisans of Vitosha", 38, 8, [["the_red_mountain_guard"]], 8, "duo:Generic_Female_Partisans",
     "add_ideas = VIT_partisans",
     "Every path, cave and hut on the mountain has a partisan who knows it. No enemy army will cross Vitosha in peace.", ["ARMY_XP"]),
    ("comrades_in_the_city", "Comrades in the City", 40, 8, [["lectures_in_kapana"]], 6, "duo:Generic_Communist_Propaganda",
     "every_neighbor_country = { add_timed_idea = { idea = VIT_comrades_from_vitosha days = 180 } }",
     "Students go down the mountain with leaflets in their satchels.\\n\\nCommunism grows slowly in every neighbour for six "
     "months.", ["POLITICAL"]),
    ("the_villas_to_the_people", "The Villas to the People", 33, 9, [["the_orchards_of_orehite", "the_plovdiv_fair"]], 8,
     "duo:goal_generic_soviet_construction", factory("industrial_complex") + "\nadd_stability = 0.03",
     "The villas of Boyana become schools, clinics and workers' hostels. Henry's old villa becomes all three.", ["INDUSTRY", "STABILITY"]),
    ("the_red_army_of_the_mountain", "The Red Army of the Mountain", 37, 9, [["commissars_of_the_slopes", "partisans_of_vitosha"]], 10,
     "duo:Generic_Army_Focus_Red02", "add_ideas = VIT_red_army\narmy_experience = 20",
     "Commissars, red stars and a doctrine written in a café in Simeonovo.", ["ARMY_XP"]),
    ("the_red_press", "The Red Press", 40, 9, [["comrades_in_the_city"]], 7, "duo:goal_generic_seize_press",
     "add_political_power = 75\nadd_war_support = 0.05",
     "One newspaper, one opinion, printed on the press from the garage in Simeonovo.", ["POLITICAL", "WAR_SUPPORT"]),
    ("the_thracian_dream", "The Thracian Dream", 32, 10, [["the_villas_to_the_people"]], 8, "duo:Generic_Red_Liberation", NOWAR,
     "{CLAIMS:PNC}\n{WAR:PNC}",
     "Plovdiv is the heart of Thrace, and the road to Thrace runs south-east past the lake at Pancharevo.\\n\\nClaims and "
     "war goals on Pancharevo.", ["ANNEXATION"]),
    ("the_five_year_plan", "The Mountain Five-Year Plan", 34, 10, [["the_villas_to_the_people"]], 12, "duo:Generic_State_Socialism",
     factory("arms_factory", 2),
     "Five years, five targets, and a red banner for every factory that meets them.", ["INDUSTRY"]),
    ("the_red_air_brigade", "The Red Air Brigade", 36, 10, [["the_red_army_of_the_mountain"]], 8, "duo:goal_generic_air_fighter2",
     "air_experience = 25\ncapital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }",
     "Three aeroplanes, painted red, flown by the bravest students in Simeonovo.", ["AIR_XP"]),
    ("the_mountain_committee", "The Committee for the Mountain", 38, 10, [["the_red_army_of_the_mountain"]], 7, "duo:Generic_Spy_Communist",
     "add_stability = 0.05\nadd_ideas = VIT_mountain_committee",
     "A committee that watches everyone, including the other committees.", ["STABILITY"]),
    ("the_red_mountain", "The Red Mountain", 40, 10, [["the_red_press"]], 8, "duo:focus_generic_join_comintern", "OR = { is_in_faction = no is_faction_leader = yes }",
     "if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_FACTION_RED_MOUNTAIN }\n" + invite(10),
     "Every worker in Sofia has a friend on the mountain now.\\n\\nCreates the faction The Red Mountain and invites every "
     "district outside an alliance; communist ones are likelier to say yes.", ["POLITICAL"]),
    ("the_road_to_plovdiv", "The Road to Plovdiv", 32, 11, [["the_thracian_dream"]], 9, "duo:Generic_Train", NOWAR,
     "{CLAIMS:ISK}\n{WAR:ISK}",
     "The old road to Plovdiv leaves Sofia through Iskar. Whoever holds it holds the way home.\\n\\nClaims and war goals on "
     "Iskar.", ["ANNEXATION"]),
    ("tractors_for_the_slopes", "Tractors for the Slopes", 34, 11, [["the_five_year_plan"]], 8, "duo:focus_generic_self_management",
     factory("industrial_complex", 2),
     "A tractor works in Simeonovo, built from the parts of Henry's motor cars.", ["INDUSTRY"]),
    ("workers_of_sofia_unite", "Workers of Sofia, Unite", 38, 11, [["the_mountain_committee", "the_red_mountain"]], 8,
     "duo:goal_generic_support_communism", "",
     "every_country = {\n\tlimit = { has_government = communism NOT = { tag = ROOT } }\n"
     "\tadd_opinion_modifier = { target = ROOT modifier = evil_sofia_free_friends }\n}\nadd_political_power = 50",
     "From Mladost to Lyulin, every communist in Sofia hears Yani's speech on the radio.\\n\\nEvery communist district thinks "
     "better of us.", ["POLITICAL"]),
    ("thracian_commune", "The Thracian Commune", 34, 12, [["the_road_to_plovdiv"], ["tractors_for_the_slopes", "the_red_air_brigade"]], 12,
     "duo:Generic_Socialist_Revolution", "{HELD:VIT,PNC,ISK}\n" + NOWAR,
     "{COREHELD:VIT:PNC,ISK}\nset_cosmetic_tag = VIT_THRACIA\nswap_ideas = { remove_idea = VIT_vitosha_soviet add_idea = VIT_thracian_commune }\n"
     "news_event = { id = evil_sofia_vit_news.6 hours = 6 }",
     "From the top of Vitosha to the road to Plovdiv, one commune: the first step to the red Thrace Yani dreamed of in the "
     "tobacco warehouses.\\n\\nNeeds Vitosha, Pancharevo and Iskar held. Vitosha becomes the Thracian Commune and cores "
     "the land it holds.", ["POLITICAL", "ANNEXATION"]),
    ("all_roads_lead_to_plovdiv", "All Roads Lead to Plovdiv", 32, 13, [["thracian_commune"]], 10, "duo:Generic_Internationalism",
     NOWAR, "{CLAIMS:KRE,NIS,SLA,IZG}\n{WAR:KRE,NIS,SLA,IZG}",
     "Rome had its roads. Plovdiv had them first, and the road home runs east, through the steelworks and the "
     "workers' districts of Kremikovtsi, Novi Iskar, Slatina and Izgrev.\\n\\nClaims and war goals on those four.",
     ["ANNEXATION"]),
    ("the_red_hill", "The Red Hill", 34, 13, [["thracian_commune"]], 10, "duo:Generic_Red_Atomic", "", "add_ideas = VIT_red_hill",
     "Yani renames the mountain's highest hut after the tobacco strike of his childhood. The workers climb up to see it "
     "every May Day.", ["RESEARCH", "STABILITY"]),
    ("the_soviet_of_sofia", "The Soviet of Sofia", 36, 13, [["thracian_commune"], ["workers_of_sofia_unite"]], 9, "duo:Generic_Workers_Democracy",
     "", "add_political_power = 100\nadd_stability = 0.05",
     "Delegates from every red district meet in Henry's old ballroom and vote, unanimously, for everything Yani proposes.",
     ["POLITICAL"]),
    ("may_day_on_cherni_vrah", "May Day on Cherni Vrah", 34, 14, [["all_roads_lead_to_plovdiv", "the_red_hill", "the_soviet_of_sofia"]], 12,
     "duo:Generic_Maoism", "", "add_ideas = VIT_may_day",
     "Ten thousand people climb to the top of the mountain with red flags, and Yani makes a speech that the whole city "
     "hears.", ["STABILITY", "WAR_SUPPORT"]),
]
# ================================================================== Yani: The Seven Hills (fascist)
YFAS = [
    ("the_seven_hills", "The Seven Hills", 56, 6, [["yani_takes_the_villa"]], 8, "duo:Generic_Fascist_Guy",
     "set_politics = { ruling_party = fascism elections_allowed = no }\npromote_character = { character = VIT_yani ideology = fascism_ideology }\n"
     "add_ideas = VIT_black_shirts\nadd_war_support = 0.05",
     "Plovdiv is older than Rome, older than Athens, and was built on seven hills. Yani's followers put on black shirts, "
     "light torches and march down the mountain road singing about Philip of Macedon.\\n\\nYani's movement turns fascist.",
     ["POLITICAL", "WAR_SUPPORT"]),
    ("the_legacy_of_philip", "The Legacy of Philip", 53, 7, [["the_seven_hills"]], 8, "duo:Generic_Caesar", "add_ideas = VIT_legacy_of_philip",
     "Philip of Macedon took a Thracian town and named it after himself. His son conquered the world. Yani has read both "
     "of their biographies twice.", ["ARMY_XP"]),
    ("seven_hills_seven_districts", "Seven Hills, Seven Districts", 56, 7, [["the_seven_hills"]], 6, "duo:Generic_Chess_Move",
     "add_political_power = 75",
     "Plovdiv was built on seven hills. Yani's new Philippopolis will be built on seven districts, one for every hill.\\n\\n"
     "Each hill focus claims a district; holding all seven opens New Philippopolis.", ["POLITICAL", "ANNEXATION"]),
    ("torchlight_on_the_slopes", "Torchlight on the Slopes", 59, 7, [["the_seven_hills"]], 7, "duo:Generic_War_Propaganda03",
     "add_ideas = VIT_torchlight",
     "Every Saturday night a column of torches climbs from Simeonovo to Aleko. From the city it looks like a river of fire "
     "running uphill.", ["WAR_SUPPORT", "STABILITY"]),
    ("the_macedonian_phalanx", "The Macedonian Phalanx", 52, 8, [["the_legacy_of_philip"]], 8, "duo:Generic_Gray_Fascists",
     "add_tech_bonus = { name = VIT_phalanx bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 20",
     "Long pikes worked for Philip. Yani settles for long bayonets.", ["ARMY_XP", "RESEARCH"]),
    ("philips_generals", "Philip's Generals", 54, 8, [["the_legacy_of_philip"]], 7, "duo:Generic_German_General",
     "army_experience = 25\nadd_war_support = 0.03",
     "Every one of Yani's generals is given the name of one of Philip's. Parmenion is very proud of it.", ["ARMY_XP"]),
    ("the_black_shirt_youth", "The Black Shirt Youth", 58, 8, [["torchlight_on_the_slopes"]], 7, "duo:Generic_Child_Soldiers",
     "add_manpower = 15000",
     "Every boy in Simeonovo wants a black shirt. Every mother in Simeonovo is worried about it.", ["MANPOWER"]),
    ("the_trimontium_radio", "Radio Trimontium", 60, 8, [["torchlight_on_the_slopes"]], 6, "duo:goal_generic_propaganda",
     "every_neighbor_country = { add_timed_idea = { idea = VIT_trimontium_radio days = 180 } }",
     "The Romans called Plovdiv Trimontium. So does Yani's radio station, every evening, on every wavelength.\\n\\n"
     "Fascism grows slowly in every neighbour for six months.", ["POLITICAL"]),
    ("the_trimontium_guard", "The Trimontium Guard", 53, 9, [["the_macedonian_phalanx", "philips_generals"]], 9, "duo:Generic_Rearmament",
     "add_ideas = VIT_trimontium_guard",
     "The Romans called Plovdiv the city of three hills. Yani's guard takes the name and the doctrine.", ["ARMY_XP"]),
    ("the_seven_hills_pact", "The Pact of the Seven Hills", 59, 9, [["the_black_shirt_youth", "the_trimontium_radio"]], 8,
     "duo:goal_generic_support_fascism", "OR = { is_in_faction = no is_faction_leader = yes }", "if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_FACTION_SEVEN_HILLS }\n" + invite(13),
     "Seven hills, seven seats at the table, and Yani at the head of it.\\n\\nCreates the faction The Pact of the Seven "
     "Hills and invites every district outside an alliance; fascist ones are likelier to say yes.", ["POLITICAL"]),
]
HILLS = [("nebet_tepe", "Nebet Tepe", "LOZ", "Lozenets", 56, 8), ("dzhambaz_tepe", "Dzhambaz Tepe", "TRD", "Triaditsa", 57, 9),
         ("taksim_tepe", "Taksim Tepe", "OVK", "Ovcha Kupel", 56, 10), ("sahat_tepe", "Sahat Tepe", "PNC", "Pancharevo", 58, 10),
         ("bunardzhika", "Bunardzhika", "STU", "Studentski", 56, 11), ("dzhendem_tepe", "Dzhendem Tepe", "KRS", "Krasno Selo", 58, 11),
         ("markovo_tepe", "Markovo Tepe", "MLA", "Mladost", 57, 12)]
HILL_PRE = {"nebet_tepe": [["seven_hills_seven_districts"]], "dzhambaz_tepe": [["nebet_tepe"]],
            "taksim_tepe": [["dzhambaz_tepe"]], "sahat_tepe": [["dzhambaz_tepe"]], "bunardzhika": [["taksim_tepe"]],
            "dzhendem_tepe": [["sahat_tepe"]], "markovo_tepe": [["bunardzhika", "dzhendem_tepe"]]}
HILL_ICONS = ["duo:Generic_Pawns", "duo:Generic_Invasion2", "duo:Generic_Conquistador", "duo:Generic_Molotov_Cocktail",
              "duo:Generic_Helmet_Knife", "duo:Generic_Urban_Warfare", "duo:Generic_Sniper_Assassin"]
for (hid, hname, htag, hdistrict, hx, hy), hicon in zip(HILLS, HILL_ICONS):
    YFAS.append((hid, f"{hname}: {hdistrict}", hx, hy, HILL_PRE[hid], 7, hicon, NOWAR, "{CLAIMS:%s}\n{WAR:%s}" % (htag, htag),
                 f"{hname} is one of the seven hills of Plovdiv. In Yani's new Philippopolis, its name goes to {hdistrict}.\\n\\n"
                 f"Claims and war goals on {hdistrict}.", ["ANNEXATION"]))
YFAS += [
    ("the_eighth_hill", "The Eighth Hill", 53, 10, [["the_trimontium_guard"]], 10, "duo:Generic_Revanchism02", "", "add_ideas = VIT_eighth_hill",
     "Plovdiv has seven hills. Philippopolis has eight: the eighth is Vitosha, and it is the tallest.", ["ARMY_XP", "STABILITY"]),
    ("the_mountain_arsenal", "The Black Arsenal", 53, 11, [["the_eighth_hill"]], 9, "duo:focus_generic_license_production",
     factory("arms_factory", 2), "Two new arms factories in the quarries, painted black, naturally.", ["INDUSTRY"]),
    ("the_torch_bearers", "The Torch Bearers", 60, 10, [["the_seven_hills_pact"]], 7, "duo:Generic_Ultranationalist_Volunteers",
     "add_stability = 0.05\nadd_political_power = 50",
     "The oldest of the black shirts carry the torches at the front of every march. It is the highest honour on the mountain.",
     ["STABILITY"]),
    ("the_roman_theatre", "The Roman Theatre", 60, 11, [["the_torch_bearers"]], 8, "duo:Generic_Cult_of_Reason",
     factory("industrial_complex") + "\nadd_war_support = 0.05",
     "Plovdiv has a Roman theatre. Yani builds one on the mountain, for speeches, with very good acoustics.", ["INDUSTRY", "WAR_SUPPORT"]),
    ("new_philippopolis", "New Philippopolis", 57, 13, [["markovo_tepe"]], 12, "duo:Generic_Ultranat_Eagle",
     "{HELD:VIT,LOZ,TRD,OVK,PNC,STU,KRS,MLA}\n" + NOWAR,
     "{COREHELD:VIT:LOZ,TRD,OVK,PNC,STU,KRS,MLA}\nset_cosmetic_tag = VIT_PHILIPPOPOLIS\n"
     "swap_ideas = { remove_idea = VIT_black_shirts add_idea = VIT_philippopolis }\nadd_research_slot = 1\n"
     "news_event = { id = evil_sofia_vit_news.7 hours = 6 }",
     "Seven districts, seven hills, one city: New Philippopolis rises at the foot of Vitosha, and the student from Plovdiv "
     "rules it.\\n\\nNeeds Vitosha and all seven hill districts held (Lozenets, Triaditsa, Ovcha Kupel, Pancharevo, "
     "Studentski, Krasno Selo, Mladost). Vitosha becomes New Philippopolis and cores the land it holds.",
     ["POLITICAL", "ANNEXATION"]),
    ("philippopolis_rules_sofia", "Philippopolis Rules Sofia", 55, 14, [["new_philippopolis"]], 10, "duo:Generic_Checkmate", NOWAR,
     "{CLAIMS:SRD,OBR,VAZ,SRK}\n{WAR:SRD,OBR,VAZ,SRK}",
     "Sofia was a Thracian town, Serdica, long before it was anything else. Its old heart belongs to the Thracians' "
     "heirs.\\n\\nClaims and war goals on the old centre: Sredets, Oborishte, Vazrazhdane and Serdika.", ["ANNEXATION"]),
    ("the_sun_of_vergina", "The Sun of Vergina", 59, 14, [["new_philippopolis"]], 12, "duo:Generic_Cult_of_the_Supreme_Being", "",
     "add_ideas = VIT_sun_of_vergina",
     "The golden sun of Philip's tomb flies over the mountain, and Yani has it embroidered on every black shirt.",
     ["ARMY_XP", "STABILITY"]),
]
for fid, name, x, y, pre, w, icon, avail, rew, desc, filt in [(e[0], e[1], e[2], e[3], e[4], e[5], e[6],
                                                               *((e[7], e[8], e[9], e[10]) if len(e) == 11 else ("", e[7], e[8], e[9])))
                                                              for e in HDEM + HAUT + YCOM + YFAS]:
    mx = {"what_the_english_couldnt_do": ["what_zevka_wanted"], "what_zevka_wanted": ["what_the_english_couldnt_do"],
          "red_plovdiv": ["the_seven_hills"], "the_seven_hills": ["red_plovdiv"]}.get(fid, [])
    F(fid, name, x, y, pre, mx, w, icon, avail, rew, desc, filt)

# ================================================================== the Evil Gang (for Henry and for Yani)
GANG_FRIENDS = [("SRD", "Victor Kolev", 63, 2), ("LOZ", "Georgi Yanchovichin", 65, 2), ("KRP", "Stefan Kartunov", 67, 2),
                ("MLA", "Georgi Poryazov", 63, 3), ("TRD", "Alexander Dimitrov", 65, 3), ("OBR", "Anton Zafirov", 67, 3)]
F("the_group_chat_pings", "The Group Chat Pings", 65, 0, [], [], 5, "duo:Generic_Meeting",
  "has_country_flag = VIT_war_over", "add_political_power = 50",
  "The war on the mountain is over, and the phone has not stopped buzzing. The old group chat, the Evil Gang, wants to "
  "know if Vitosha is still one of them.", ["POLITICAL"])
VICTOR_GANG = "SRD = { exists = yes is_faction_leader = yes has_completed_focus = SRD_call_the_evil_gang }"
F("join_victors_gang", "Join Victor's Gang", 64, 1, [["the_group_chat_pings"]], ["found_the_mountain_gang"], 4,
  "duo:Generic_Coalition_Army", f"is_in_faction = no\n{VICTOR_GANG}",
  "SRD = { country_event = { id = evil_sofia_vit.4 } }",
  "Victor has already brought the Evil Gang back together. Vitosha asks to join.\\n\\nOnly if Sredets leads the Evil "
  "Gang. Victor decides; the better he thinks of us, the likelier he says yes.", ["POLITICAL"])
F("found_the_mountain_gang", "The Gang on the Mountain", 66, 1, [["the_group_chat_pings"]], ["join_victors_gang"], 5,
  "duo:Generic_Party_Bottle", f"OR = {{ is_in_faction = no is_faction_leader = yes }}\nNOT = {{ {VICTOR_GANG} }}",
  "if = { limit = { is_in_faction = no } create_faction = EVIL_SOFIA_FACTION_EVIL_GANG }\nadd_political_power = 25",
  "Nobody has brought the gang back together yet, so Vitosha will. The first meeting is at the villa, and there is "
  "plenty of food.\\n\\nCreates the faction The Evil Gang with Vitosha at its head. Not possible if Sredets already "
  "leads it.", ["POLITICAL"])
for gtag, gname, gx, gy in GANG_FRIENDS:
    pre = [["found_the_mountain_gang"]] if gy == 2 else ([["vit_invite_SRD", "vit_invite_LOZ"]] if gx == 63 else [["vit_invite_LOZ"]] if gx == 65 and gy == 3 else [["vit_invite_KRP"]])
    F(f"vit_invite_{gtag}", f"Invite {gname}", gx, gy, pre, [], 5, f"person:vit_invite_{gtag}", "",
      f"if = {{\n\tlimit = {{ country_exists = {gtag} NOT = {{ has_war_with = {gtag} is_in_faction_with = {gtag} }} {gtag} = {{ is_in_faction = no }} }}\n"
      f"\t{gtag} = {{ country_event = {{ id = evil_sofia_vit.1 }} }}\n}}",
      f"A message in the group chat, addressed to {gname} by name: the gang is meeting on the mountain, and there is a "
      f"seat for him.\\n\\n{gname} is invited to the Evil Gang. The better he thinks of us, the likelier he says yes.",
      ["POLITICAL"])
F("the_gang_rules_the_mountain", "The Gang Rules the Mountain", 65, 4, [["vit_invite_MLA", "vit_invite_TRD", "vit_invite_OBR"]], [], 8, "duo:Generic_Hedonism", "",
  "add_ideas = SRD_evil_gang\nevery_other_country = {\n\tlimit = { is_in_faction_with = ROOT }\n\tif = { limit = { NOT = { has_idea = SRD_evil_gang } } add_ideas = SRD_evil_gang }\n}",
  "The gang meets every Friday at the villa, and everyone outside it is a little more nervous on Saturdays.\\n\\nEvery "
  "member of our faction gets the Evil Gang spirit.", ["POLITICAL", "WAR_SUPPORT"])

# ================================================================== industry of the mountain (everyone)
IND = [
    ("the_quarries_of_vitosha", "The Quarries of Vitosha", 73, 0, [], 7, "duo:Generic_Mining",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
     "The granite of Vitosha built half the pavements of Sofia. The quarries open again."),
    ("the_boyana_workshops", "The Workshops of Boyana", 71, 1, [["the_quarries_of_vitosha"]], 10, "duo:Generic_Factory_Planning",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
     "Garages behind the villas become workshops, and the workshops get bigger every month."),
    ("the_arsenal_in_the_rock", "The Arsenal in the Rock", 75, 1, [["the_quarries_of_vitosha"]], 10, "duo:Generic_Barrels",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = arms_factory level = 1 instant_build = yes }\n}",
     "An old quarry tunnel is safe from any shell in Sofia. It makes rifles now."),
    ("the_road_to_aleko", "The Road to Aleko", 70, 2, [["the_boyana_workshops"]], 6, "duo:Generic_Electrification",
     "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }",
     "A proper road up the mountain to the Aleko hut, with electric light all the way."),
    ("knyazhevo_springs", "The Springs of Knyazhevo", 72, 2, [["the_boyana_workshops"]], 7, "duo:Generic_Medicine",
     "add_stability = 0.05\nadd_political_power = 50",
     "The mineral springs of Knyazhevo are bottled and sold all over Sofia. Everyone feels a little healthier, and the "
     "treasury feels a lot healthier."),
    ("arms_from_the_quarries", "Arms from the Quarries", 74, 2, [["the_arsenal_in_the_rock"]], 10, "duo:Generic_Industry02",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = arms_factory level = 1 instant_build = yes }\n}",
     "The quarry railways carry stone in the morning and shells in the afternoon."),
    ("the_mountain_laboratory", "The Mountain Laboratory", 76, 2, [["the_arsenal_in_the_rock"]], 10, "duo:Generic_Brain_Force_Plus",
     "add_research_slot = 1",
     "Clear air, no distractions and a view of the whole city: the perfect place to think."),
    ("factories_in_the_valley", "Factories in the Valley", 71, 3, [["the_road_to_aleko"], ["knyazhevo_springs"]], 12,
     "duo:Generic_Industrial_Complexes",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = { type = industrial_complex level = 2 instant_build = yes }\n}",
     "Down in the valley, where the road from the mountain meets the city, the big factories go up."),
    ("war_workshops_of_knyazhevo", "The War Workshops of Knyazhevo", 75, 3, [["arms_from_the_quarries"]], 12,
     "duo:Generic_Factory_Complex",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = { type = arms_factory level = 2 instant_build = yes }\n}",
     "Knyazhevo's tram depot builds armoured cars, and its foundry builds what goes on them."),
    ("the_industrial_mountain", "The Industrial Mountain", 73, 4, [["factories_in_the_valley"], ["war_workshops_of_knyazhevo"]], 10,
     "duo:Generic_Industrialization", "add_ideas = VIT_industrial_mountain",
     "Smoke on the slopes and sirens in the valleys: the mountain works."),
]
for fid, name, x, y, pre, w, icon, rew, desc in IND:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc, ["INDUSTRY"] + (["RESEARCH"] if "research" in rew else []))
ARMY = [
    ("the_mountain_army", "The Mountain Army", 82, 0, [], 6, "duo:Generic_Winter_Warfare", "army_experience = 25",
     "The strongest guard in Sofia needs to become an army."),
    ("mountaineers_of_cherni_vrah", "Mountaineers of Cherni Vrah", 79, 1, [["the_mountain_army"]], 7, "duo:Generic_Outpost",
     "add_tech_bonus = { name = VIT_mountaineers bonus = 1.0 uses = 1 category = land_doctrine }",
     "Men who climb Cherni Vrah in winter for fun make very good soldiers."),
    ("rifles_of_the_slopes", "Rifles of the Slopes", 82, 1, [["the_mountain_army"]], 6, "duo:Generic_Crouched_Soldier",
     "add_tech_bonus = { name = VIT_rifles bonus = 1.0 uses = 1 category = infantry_weapons }\n"
     "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }",
     "Every hunter on the mountain has a rifle. Now every soldier has a better one."),
    ("planes_over_the_peak", "Planes over the Peak", 85, 1, [["the_mountain_army"]], 7, "duo:Generic_Jet_Fighters",
     "air_experience = 25\ncapital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }",
     "A grass strip in the meadows below Aleko, and a few aeroplanes that can just about clear the trees."),
    ("artillery_on_the_ridges", "Artillery on the Ridges", 78, 2, [["mountaineers_of_cherni_vrah"]], 6, "duo:Generic_Bombs",
     "add_tech_bonus = { name = VIT_artillery bonus = 1.0 uses = 1 category = artillery }",
     "A gun on a ridge of Vitosha can reach half of Sofia."),
    ("ski_troops", "Ski Troops", 80, 2, [["mountaineers_of_cherni_vrah"]], 7, "duo:Generic_Scouts", "add_ideas = VIT_ski_troops",
     "In winter the fastest way down the mountain is on skis. The guard learns."),
    ("the_mountain_academy", "The Mountain Academy", 83, 2, [["rifles_of_the_slopes"]], 8, "duo:focus_generic_military_academy",
     "add_tech_bonus = { name = VIT_academy bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 15",
     "An officers' school in an old monastery, with a parade ground cut into the forest."),
    ("fighters_over_the_slopes", "Fighters over the Slopes", 85, 2, [["planes_over_the_peak"]], 7, "duo:Generic_Industry_Planes",
     "add_tech_bonus = { name = VIT_fighters_slopes bonus = 1.0 uses = 1 category = air_equipment }",
     "Better aeroplanes for the meadow airfield, and pilots who have stopped crashing into the trees."),
    ("armoured_cars_on_the_mountain_road", "Armoured Cars on the Mountain Road", 79, 3, [["artillery_on_the_ridges"], ["ski_troops"]], 9,
     "duo:Generic_Refit_Tanks", "add_tech_bonus = { name = VIT_armour bonus = 1.0 uses = 1 category = armor }",
     "Steel plates on lorries, and lorries on the mountain road. It is not much of a tank, but it is a start."),
    ("the_mountain_staff", "The Mountain Staff", 82, 3, [["the_mountain_academy"]], 9, "duo:Generic_Draw_Up_Plans",
     "add_ideas = VIT_mountain_staff\narmy_experience = 20",
     "Maps of every path, every ridge and every village, and officers who know them by heart."),
    ("anti_air_on_kopitoto", "Anti-Air on Kopitoto", 85, 3, [["fighters_over_the_slopes"]], 7, "duo:focus_generic_air_defense2",
     "capital_scope = {\n\tadd_building_construction = { type = anti_air_building level = 2 instant_build = yes }\n\tadd_building_construction = { type = radar_station level = 1 instant_build = yes }\n}",
     "Guns and a radar on the top of Kopitoto: nothing flies over Sofia without the mountain seeing it."),
    ("the_army_of_the_mountain", "The Army of the Mountain", 82, 4, [["armoured_cars_on_the_mountain_road"], ["the_mountain_staff"]], 12,
     "duo:focus_generic_combined_arms", "add_ideas = VIT_army_of_the_mountain",
     "Rangers, skiers, guns on the ridges and armour on the roads: the best mountain army in Sofia."),
]
for fid, name, x, y, pre, w, icon, rew, desc in ARMY:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc, ["ARMY_XP", "RESEARCH"] if "tech_bonus" in rew else ["ARMY_XP"])



# ================================================================== before the war: friends, forts and hired help
PREWAR = "NOT = { has_country_flag = VIT_war_started }"


def call_friend(tag, event, extra=""):
    return (f"if = {{\n\tlimit = {{ is_in_faction = no }}\n\tcreate_faction = {FACTION_OF[event]}\n}}\n"
            f"if = {{\n\tlimit = {{ country_exists = {tag} {tag} = {{ is_in_faction = no }} NOT = {{ has_war_with = {tag} }} }}\n"
            f"\t{tag} = {{ country_event = {{ id = evil_sofia_vit.{event} }} }}\n}}")


FACTION_OF = {19: "EVIL_SOFIA_FACTION_VILLA_PACT", 22: "EVIL_SOFIA_FACTION_STUDENT_PACT"}
CAN_CALL = "OR = { is_in_faction = no is_faction_leader = yes }"
HFRIENDS = [("KRP", "Stefan Kartunov", 7), ("MLA", "Georgi Poryazov", 9), ("SRD", "Victor Kolev", 11)]
YFRIENDS = [("KRP", "Stefan Kartunov", 41), ("LOZ", "Georgi Yanchovichin", 43)]
F("old_friends_of_the_villa", "Old Friends of the Villa", 10, 2, [["henry_holds_the_villa"]], [], 5, "duo:goal_generic_dangerous_deal",
  PREWAR, "add_political_power = 50",
  "Henry has known some of the district leaders since school. A war is coming, and old friends can help, as long as "
  "they are not communists. Henry is very firm about that.", ["POLITICAL"])
for tag, name, x in HFRIENDS:
    F(f"henry_calls_{tag}", f"Call {name}", x, 3, [["old_friends_of_the_villa"]], [], 5, f"person:henry_calls_{tag}",
      f"{CAN_CALL}\n{tag} = {{ exists = yes NOT = {{ has_government = communism }} }}", call_friend(tag, 19),
      f"Henry telephones {name}: the villa needs friends, and {name} has always been one.\\n\\nIf we are not in an "
      f"alliance we found the Villa Pact. {name} is asked to join; he usually says yes. Not possible while {name} is "
      "communist.", ["POLITICAL"])
F("the_villa_pact", "The Villa Pact", 9, 4, [[f"henry_calls_{t}" for t, _, _ in HFRIENDS]], [], 6, "duo:goal_generic_government_deals", "",
  "add_ideas = VIT_villa_pact",
  "Dinner at the villa for every friend who answered the phone. Dinner is at midnight.", ["POLITICAL"])
F("friends_at_the_gate", "Friends at the Gate", 9, 5, [["the_villa_pact"]], [], 6, "duo:goal_generic_corporatism", PREWAR,
  "add_war_support = 0.03",
  "Henry's friends promise to send a few volunteers up the mountain the day the shooting starts. They will go home "
  "when it stops.", ["MANPOWER"])
F("fortify_boyana", "Fortify Boyana", 18, 2, [["henry_holds_the_villa"]], [], 6, "duo:Generic_Protectionist_Economics", PREWAR,
  "add_political_power = 25", "Sandbags, wire and concrete around the villas of Boyana, just in case.", ["INDUSTRY"])
F("ring_road_bunkers", "Bunkers on the Ring Road", 17, 3, [["fortify_boyana"]], [], 8, "duo:focus_generic_provoke_border_clashes", PREWAR,
  f"{S('Vitosha')} = {{ add_building_construction = {{ type = bunker level = 2 province = {{ all_provinces = yes limit_to_border = yes }} instant_build = yes }} }}",
  "Concrete pillboxes along the ring road, where the mountain meets the city.", ["INDUSTRY"])
F("trenches_in_knyazhevo", "Trenches in Knyazhevo", 19, 3, [["fortify_boyana"]], [], 7, "duo:Generic_Chemical_Warfare", PREWAR,
  f"{S('Knyazhevo')} = {{ add_building_construction = {{ type = bunker level = 2 province = {{ all_provinces = yes limit_to_border = yes }} instant_build = yes }} }}",
  "Trenches through the mineral springs park. The bathers are not pleased.", ["INDUSTRY"])
F("the_vitosha_line", "The Vitosha Line", 18, 4, [["ring_road_bunkers"], ["trenches_in_knyazhevo"]], [], 10, "duo:focus_generic_strike_at_democracy1", PREWAR,
  "every_owned_state = { add_building_construction = { type = bunker level = 1 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
  "A line of bunkers around the whole mountain. Whoever is inside it will be very hard to get out.", ["INDUSTRY"])
F("hired_help", "Hired Help", 22, 2, [["henry_holds_the_villa"]], [], 5, "duo:goal_generic_loans", PREWAR, "add_political_power = 25",
  "Henry's mother does not trust students. She does trust money.", ["MANPOWER"])
F("guards_for_hire", "Guards for Hire", 21, 3, [["hired_help"]], [], 7, "duo:Generic_Gunslinger", PREWAR, "add_political_power = 10",
  "Three companies of private guards from Lozenets, paid in advance, with their own rifles.", ["MANPOWER"])
F("the_british_club", "The British Club", 23, 3, [["hired_help"]], [], 7, "duo:Generic_British_Soldier", PREWAR, "add_political_power = 10",
  "The British Club in Sofia has a bar, a billiard room and a surprising number of retired officers.", ["MANPOWER"])

F("old_classmates", "Old Classmates", 42, 2, [["the_cafes_of_simeonovo"]], [], 5, "duo:Generic_Espionage04", PREWAR,
  "add_political_power = 50",
  "Yani went to school with half the district leaders of Sofia. Some of them still owe him homework.", ["POLITICAL"])
for tag, name, x in YFRIENDS:
    F(f"yani_calls_{tag}", f"Call {name}", x, 3, [["old_classmates"]], [], 5, f"person:yani_calls_{tag}", CAN_CALL,
      call_friend(tag, 22),
      f"{name} sat next to Yani for four years. Whatever either of them believes now, that still counts.\\n\\nIf we are "
      f"not in an alliance we found the Students' Pact. {name} is asked to join, and always says yes.", ["POLITICAL"])
F("the_students_pact", "The Students' Pact", 42, 4, [[f"yani_calls_{t}" for t, _, _ in YFRIENDS]], [], 6, "duo:goal_generic_intelligence_exchange", "",
  "add_ideas = VIT_students_pact", "A pact signed in a classroom, on a desk with all their names carved into it.", ["POLITICAL"])
F("classmates_at_the_front", "Classmates at the Front", 42, 5, [["the_students_pact"]], [], 6, "duo:Generic_War_Propaganda", PREWAR,
  "add_war_support = 0.03",
  "The classmates will send their own volunteers the day the war starts, and take them home when it ends.", ["MANPOWER"])
F("hidden_depots", "Hidden Depots", 50, 2, [["the_cafes_of_simeonovo"]], [], 6, "duo:Generic_Black_Market", PREWAR,
  "add_political_power = 25", "A barn, a cellar, a hole under a woodpile: the movement starts hiding things.", ["INDUSTRY"])
F("caches_in_the_forest", "Caches in the Forest", 49, 3, [["hidden_depots"]], [], 7, "duo:Generic_Jungle_Ghost", PREWAR, "add_political_power = 10",
  "Rifles wrapped in oilcloth, buried under the beeches above Simeonovo.", ["INDUSTRY"])
F("drills_in_the_woods", "Drills in the Woods", 51, 3, [["hidden_depots"]], [], 7, "duo:Generic_Jungle_Insurgency", PREWAR, "add_political_power = 10",
  "Every Sunday the students go for a long walk in the forest, and come back knowing how to strip a rifle.", ["ARMY_XP"])
F("barricades_in_simeonovo", "Barricades in Simeonovo", 50, 4, [["caches_in_the_forest"], ["drills_in_the_woods"]], [], 8,
  "duo:Generic_Enough", PREWAR, "add_political_power = 10",
  "Every street in Simeonovo knows where its barricade goes. The cobbles are already loose.", ["INDUSTRY"])
F("the_tobacco_column", "The Tobacco Column", 53, 3, [["hidden_depots"]], [], 7, "duo:Generic_Cotton_Farming", PREWAR, "add_political_power = 10",
  "Tobacco workers from Plovdiv, ready to take the train to Sofia the moment Yani calls.", ["MANPOWER"])
F("studentski_volunteers", "Studentski Volunteers", 55, 3, [["the_tobacco_column"]], [], 7, "duo:Generic_Revolutionary_Women", PREWAR,
  "add_political_power = 10",
  "The dormitories of Studentski Grad empty overnight when Yani needs them.", ["MANPOWER"])

# ================================================================== more for the political paths (armies, forts, cores)
MORE = [
    # Henry, the English way
    ("commandos_of_cherni_vrah", "Commandos of Cherni Vrah", 1, 12, [["fight_on_the_slopes"]], 8, "duo:focus_generic_paratrooper", "",
     "add_ideas = VIT_commandos", "Small teams that climb at night and strike at dawn. Henry insists they wear berets.", ["ARMY_XP"]),
    ("armoured_regiment_of_boyana", "The Armoured Regiment of Boyana", 8, 11, [["dominion_status"]], 9, "duo:goal_generic_army_tanks3", "",
     "add_tech_bonus = { name = VIT_boyana_armour bonus = 1.0 uses = 2 category = armor }",
     "A regiment of tanks, painted green and polished every morning.", ["RESEARCH"]),
    ("home_rule_for_the_dominions", "Home Rule for the Dominions", 7, 14, [["the_sun_never_sets"]], 8, "duo:Generic_Autonomy", "",
     "{COREHELD:VIT:LOZ,STU,MLA,TRD}\nadd_stability = 0.03",
     "Every district the Commonwealth takes gets its own little council, a portrait of Henry and the full rights of a "
     "citizen of the mountain.\\n\\nVitosha cores every state of Lozenets, Studentski, Mladost and Triaditsa it holds.", ["ANNEXATION", "STABILITY"]),
    # Henry, Zevka's dream
    ("mounted_gendarmes", "Mounted Gendarmes", 20, 13, [["the_crowns_army"]], 7, "duo:Generic_Imperial_Russian_Cossack", "",
     "add_tech_bonus = { name = VIT_mounted bonus = 1.0 uses = 1 category = motorized_equipment }\narmy_experience = 15",
     "On a mountain a horse still beats a lorry. The gendarmes ride.", ["ARMY_XP"]),
    ("the_iron_wall_of_kopitoto", "The Iron Wall of Kopitoto", 28, 13, [["the_league_of_the_mountain"]], 9, "duo:goal_generic_isolation", "",
     "every_owned_state = { add_building_construction = { type = bunker level = 1 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }\n"
     "capital_scope = { add_building_construction = { type = anti_air_building level = 2 instant_build = yes } }",
     "Concrete and guns from Kopitoto to Cherni Vrah. The Tsardom will not be taken.", ["INDUSTRY"]),
    ("lands_of_the_crown", "Lands of the Crown", 28, 15, [["the_throne_expands"]], 8, "duo:Generic_Orthodoxy", "",
     "{COREHELD:VIT:BNK,KRP,VRB,LYU,LOZ,TRD}",
     "Every village the tsar's army takes is told the same thing: it always belonged to the crown, it just did not "
     "know it.\\n\\nVitosha cores every state of Bankya, Krasna Polyana, Vrabnitsa, Lyulin, Lozenets and Triaditsa it holds.", ["ANNEXATION"]),
    # Yani, Red Plovdiv
    ("the_red_fortress", "The Red Fortress of Vitosha", 40, 11, [["the_red_mountain"]], 9, "duo:focus_generic_soviet_politics", "",
     "every_owned_state = { add_building_construction = { type = bunker level = 1 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
     "The revolution won the mountain. It will not give it back.", ["INDUSTRY"]),
    ("tank_brigades_of_simeonovo", "Tank Brigades of Simeonovo", 40, 12, [["the_red_fortress"]], 10, "duo:focus_generic_army_tanks2", "",
     "add_tech_bonus = { name = VIT_red_tanks bonus = 1.0 uses = 2 category = armor }",
     "The tractor works in Simeonovo also builds something with a gun on it.", ["RESEARCH"]),
    ("soviets_in_the_valley", "Soviets in the Valley", 32, 14, [["all_roads_lead_to_plovdiv"]], 8, "duo:Generic_Liberatian_Socialism", "",
     "{COREHELD:VIT:KRE,NIS,SLA,IZG,MLA,STU,OVK}",
     "Every district the Red Army of the Mountain reaches elects its own soviet, which joins the Thracian Commune by "
     "an overwhelming majority.\\n\\nVitosha cores every state of Kremikovtsi, Novi Iskar, Slatina, Izgrev, Mladost, Studentski and Ovcha Kupel it holds.", ["ANNEXATION"]),
    # Yani, the Seven Hills
    ("the_iron_phalanx", "The Iron Phalanx", 52, 12, [["the_mountain_arsenal"]], 10, "duo:Generic_Tank_with_Flags", "",
     "add_tech_bonus = { name = VIT_iron_phalanx bonus = 1.0 uses = 2 category = armor }",
     "Philip's phalanx had pikes. Yani's has armour plate.", ["RESEARCH"]),
    ("the_wall_of_philip", "The Wall of Philip", 60, 12, [["the_roman_theatre"]], 9, "duo:focus_generic_oppression", "",
     "every_owned_state = { add_building_construction = { type = bunker level = 1 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
     "Plovdiv had walls for three thousand years. Philippopolis gets new ones.", ["INDUSTRY"]),
    ("citizens_of_philippopolis", "Citizens of Philippopolis", 55, 15, [["philippopolis_rules_sofia"]], 8, "duo:Generic_Ultranationalist_Government", "",
     "{COREHELD:VIT:SRD,OBR,VAZ,SRK,ISK}",
     "Every district Philippopolis takes is given a hill's name, a torch and the honour of being Philippopolitan."
     "\\n\\nVitosha cores every state of Sredets, Oborishte, Vazrazhdane, Serdika and Iskar it holds.",
     ["ANNEXATION"]),
]
for fid, name, x, y, pre, w, icon, avail, rew, desc, filt in MORE:
    F(fid, name, x, y, pre, [], w, icon, avail, rew, desc, filt)

# ================================================================== more industry and army (everyone)
IND2 = [
    ("the_power_station_at_pancharevo", "The Power Station", 71, 5, [["the_industrial_mountain"]], 9, "duo:goal_generic_lightbulb",
     factory("industrial_complex"), "A dam, a turbine and electric light in every village on the mountain."),
    ("ski_lift_freight", "Freight on the Ski Lift", 75, 5, [["the_industrial_mountain"]], 7, "duo:goal_generic_trade",
     "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }",
     "The Dragalevtsi lift carries skiers in winter and crates of shells all year round."),
    ("the_granite_works", "The Granite Works", 70, 6, [["the_power_station_at_pancharevo"]], 9, "duo:goal_generic_coal_mining",
     factory("industrial_complex"), "Vitosha granite, cut and polished, for every new building in Sofia."),
    ("the_dispersed_workshops", "Dispersed Workshops", 72, 6, [["the_power_station_at_pancharevo"]], 8, "duo:focus_generic_rubber",
     "add_ideas = VIT_dispersed_workshops", "A workshop in every barn: no bomber can hit them all."),
    ("the_munitions_tunnels", "The Munitions Tunnels", 74, 6, [["ski_lift_freight"]], 10, "duo:focus_generic_tungsten",
     factory("arms_factory"), "The old quarry tunnels go deep into the mountain. Now they are full of shells."),
    ("the_cable_car_factory", "The Cable Car Factory", 76, 6, [["ski_lift_freight"]], 9, "duo:focus_generic_concessions",
     factory("arms_factory"), "Whoever can build a cable car can build an artillery tractor."),
    ("construction_effort", "The Mountain Builds", 71, 7, [["the_granite_works"], ["the_dispersed_workshops"]], 10, "duo:goal_generic_construct_civ_factory",
     "add_tech_bonus = { name = VIT_construction bonus = 1.0 uses = 2 category = construction_tech }\n" + factory("industrial_complex"),
     "Cranes on every slope."),
    ("the_mountain_radio_works", "The Radio Works", 73, 7, [["the_dispersed_workshops"]], 9, "duo:goal_generic_radar",
     "add_tech_bonus = { name = VIT_radio bonus = 1.0 uses = 2 category = electronics }",
     "Valves, wires and a factory full of students who build radios faster than they can listen to them."),
    ("the_shell_works", "The Shell Works", 75, 7, [["the_munitions_tunnels", "the_cable_car_factory"]], 11, "duo:goal_generic_construct_military",
     factory("arms_factory", 2), "Two new arms factories cut into the rock."),
    ("production_effort", "Every Machine Counts", 72, 8, [["construction_effort"]], 9, "duo:goal_generic_price_controls",
     "add_ideas = VIT_every_machine_counts", "Spare parts, shift bonuses and a foreman who never sleeps."),
    ("the_mountain_university", "The Mountain University", 74, 8, [["the_mountain_radio_works"], ["the_shell_works"]], 10, "duo:goal_generic_scientific_exchange",
     "add_research_slot = 1", "Lecture halls in the old hotels at Aleko, with the best view of any university in Europe."),
    ("the_workshop_of_sofia", "The Workshop of Sofia", 73, 9, [["production_effort"], ["the_mountain_university"]], 12, "duo:focus_generic_the_giant_wakes",
     "swap_ideas = { remove_idea = VIT_industrial_mountain add_idea = VIT_workshop_of_sofia }",
     "Half of what Sofia uses was made on the mountain. The other half was carried down it."),
]
ARMY2 = [
    ("mountain_divisions", "Mountain Divisions", 79, 5, [["the_army_of_the_mountain"]], 8, "duo:Generic_Desert_Warfare",
     "add_tech_bonus = { name = VIT_mountain_div bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 20",
     "Divisions built for the mountain: mules, light guns and very strong legs."),
    ("the_fortress_mountain", "The Fortress Mountain", 82, 5, [["the_army_of_the_mountain"]], 9, "duo:Generic_Reactionary",
     "every_owned_state = { add_building_construction = { type = bunker level = 1 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
     "Every pass, every path and every road on the mountain has a bunker on it."),
    ("the_mountain_air_corps", "The Mountain Air Corps", 85, 5, [["the_army_of_the_mountain"]], 8, "duo:goal_generic_air_doctrine",
     "air_experience = 25\nadd_tech_bonus = { name = VIT_air_doctrine bonus = 1.0 uses = 1 category = air_doctrine }",
     "Pilots who can land in a meadow and take off from a ski slope."),
    ("support_companies", "Support Companies", 78, 6, [["mountain_divisions"]], 7, "duo:Generic_Military_Women",
     "add_tech_bonus = { name = VIT_support bonus = 1.0 uses = 2 category = support_tech }",
     "Engineers, signallers and field hospitals for every division."),
    ("rangers_of_the_peak", "Rangers of the Peak", 80, 6, [["mountain_divisions"]], 8, "duo:Generic_Intelligence_Gathering",
     "add_ideas = VIT_rangers_of_the_peak", "The best shots on the mountain, trained to fight in snow and fog."),
    ("pillboxes_on_every_pass", "Pillboxes on Every Pass", 82, 6, [["the_fortress_mountain"]], 8, "duo:Generic_Protectionism",
     "capital_scope = { add_building_construction = { type = bunker level = 3 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
     "Concrete pillboxes on every mountain pass around the capital."),
    ("bombers_from_the_meadow", "Bombers from the Meadow", 84, 6, [["the_mountain_air_corps"]], 8, "duo:goal_generic_air_naval_bomber",
     "add_tech_bonus = { name = VIT_bombers bonus = 1.0 uses = 1 category = air_equipment }",
     "A few bombers, a long grass runway and a city spread out below like a map."),
    ("close_air_support", "Close Air Support", 86, 6, [["the_mountain_air_corps"]], 8, "duo:goal_generic_CAS",
     "add_tech_bonus = { name = VIT_cas bonus = 1.0 uses = 1 category = air_equipment }\nair_experience = 15",
     "Dive bombers that come down the mountain faster than any avalanche."),
    ("the_artillery_park", "The Artillery Park", 79, 7, [["support_companies"], ["rangers_of_the_peak"]], 9, "duo:Generic_Air_Defense",
     "add_tech_bonus = { name = VIT_artillery_park bonus = 1.0 uses = 2 category = artillery }",
     "Every gun on the mountain parked in one meadow, oiled and ready."),
    ("dig_in_doctrine", "Dig In Doctrine", 82, 7, [["pillboxes_on_every_pass"]], 9, "duo:Generic_Sun_Tzu",
     "add_ideas = VIT_dig_in_doctrine", "A soldier of the mountain digs before he eats."),
    ("air_superiority", "Air Superiority over Sofia", 85, 7, [["bombers_from_the_meadow", "close_air_support"]], 9, "duo:goal_generic_investigation",
     "air_experience = 25", "Nothing flies over the mountain without asking first."),
    ("the_mountain_reserve", "The Mountain Reserve", 80, 8, [["the_artillery_park"]], 9, "duo:Generic_Female_Soldier03",
     "add_ideas = VIT_mountain_reserve", "Every man who ever served is on a list, and the list is always up to date."),
    ("the_unbreakable_mountain", "The Unbreakable Mountain", 82, 9, [["the_mountain_reserve"], ["dig_in_doctrine"]], 12, "duo:Generic_Corporatism",
     "swap_ideas = { remove_idea = VIT_army_of_the_mountain add_idea = VIT_unbreakable_mountain }",
     "No army in Sofia has ever taken the mountain from someone who wanted to keep it. None ever will."),
]
for fid, name, x, y, pre, w, icon, rew, desc in IND2:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc, ["INDUSTRY"] + (["RESEARCH"] if "research" in rew or "tech_bonus" in rew else []))
for fid, name, x, y, pre, w, icon, rew, desc in ARMY2:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc,
      (["AIR_XP"] if "air" in rew else ["ARMY_XP"]) + (["RESEARCH"] if "tech_bonus" in rew else []))

UNLOCK_TOOLTIPS = {
    "crush_the_student_movement": "§YThe civil war begins.§! Everything Henry's chain prepared joins us. We get §RThe Mountain "
                                  "in Flames§! (three steps), which the war branch takes down. Then choose Henry's road.",
    "yani_takes_the_villa": "§YThe civil war begins.§! Yani becomes our leader; everything his chain prepared joins us. We get "
                            "§RThe Mountain in Flames§! (three steps), which the war branch takes down. Then choose Yani's road.",
    "the_mountain_conference": "Unlocks §YInvite the Free Districts§!.",
    "the_league_of_the_mountain": "Invitations go out to every district outside an alliance.",
}

# ================================================================== portraits for person icons
PERSON_ICONS = {
    "stand_with_henry": ("VIT", "SunStarFrame.png", "Sword.png", -90, dict(fill=(30, 40, 60), front_width=0.72, front_y=0.95)),
    "march_with_yani": ("VIT_yani", "SpikyFrame.png", "Rifles Crossed.png", 0, dict(fill=(50, 30, 26), front_width=0.46, front_y=1.1)),
    "the_cafes_of_simeonovo": ("VIT_yani", "CircleFrame.png", "Book Open.png", 0, dict(fill=(36, 36, 30), front_width=0.38, front_y=1.1)),
}
_GANG_FRAMES = ["metalcircle.png", "RedWheatFrame.png", "SilverStarFrame.png", "SunStarFrame.png", "LeavedFrame.png",
                "SpikyFrame.png", "CircleFrame.png"]
_GANG_HANDS = ["Hands Shaking.png", "Hands Shaking2.png", "Hands Shaking3.png", "Hands Shaking.png", "Hands Shaking3.png",
               "Hands Shaking2.png", "Hands Shaking.png"]
for (gtag, *_), frame, hands in zip(GANG_FRIENDS, _GANG_FRAMES, _GANG_HANDS):
    PERSON_ICONS[f"vit_invite_{gtag}"] = (gtag, frame, hands, 0, dict(fill=(34, 34, 40), front_width=0.44, front_y=0.85))
PERSON_FALLBACK = {k: "goal_ANQ_patriotic_protests" for k in PERSON_ICONS}
PERSON_FALLBACK.update({"stand_with_henry": "Generic_Conservatism", "march_with_yani": "Generic_Revolutionary_Republic",
                        "the_cafes_of_simeonovo": "Generic_Socialist_Man"})
PHOTO_ICONS, PHOTO_FALLBACK = {}, {}

# ================================================================== spirits
IDEAS = {
    "VIT_h_patrols": ("The Ski Patrols", "The fastest way across the front.", "attrition = -0.10\narmy_speed_factor = 0.05", ("Army.png", "Soldier.png")),
    "VIT_y_patrols": ("The Night Raids", "Yani's people own the night.", "army_attack_factor = 0.05\nattrition = -0.05", ("Rectangle.png", "Soldiers Charging.png")),
    "VIT_h_counter": ("The Counteroffensive", "The guard goes over to the attack.", "army_attack_factor = 0.10\narmy_org_factor = 0.05", ("Army.png", "Rifles Crossed.png")),
    "VIT_y_counter": ("The Storm of Boyana", "Everything we have, at once.", "army_attack_factor = 0.10\nwar_support_factor = 0.05", ("Rectangle.png", "Rifles Crossed.png")),
    "VIT_h_push": ("Take Simeonovo", "One last push.", "army_attack_factor = 0.10\nbreakthrough_factor = 0.10", ("Army.png", "Soldiers Charging.png")),
    "VIT_y_push": ("Take the Villa Back", "One last push.", "army_attack_factor = 0.10\nbreakthrough_factor = 0.10", ("Rectangle.png", "Fist.png")),
    "VIT_cabinet_of_talents": ("A Cabinet of All Talents", "A minister from every village.", "political_power_factor = 0.10\nstability_factor = 0.05", ("Shield Blue.png", "Documents.png")),
    "VIT_better_than_westminster": ("Better Than Westminster", "Even the English admit it.", "stability_factor = 0.10\npolitical_power_factor = 0.10\nresearch_speed_factor = 0.05\nindustrial_capacity_factory = 0.05", ("Pentagon.png", "Ballot.png")),
    "VIT_family_council": ("The Family Council", "Aunts, uncles, cousins, and then what Henry says.", "political_power_factor = 0.10", ("Shield.png", "Citizen.png")),
    "VIT_grandmas_larder": ("Grandma's Larder", "Pickles and jam for every winter.", "consumer_goods_factor = -0.05\nstability_factor = 0.03", ("Shield.png", "Bread.png")),
    "VIT_gendarmerie": ("The Mountain Gendarmerie", "A horse for every policeman.", "stability_factor = 0.05\nresistance_growth = -0.10", ("Shield.png", "Soldier Saluting.png")),
    "VIT_bells_over_sofia": ("Bells over Sofia", "Every church bell in Sofia at once.", "stability_factor = 0.10\nwar_support_factor = 0.05\npolitical_power_factor = 0.10", ("Pentagon.png", "Cross.png")),
    "VIT_commissars": ("Commissars of the Slopes", "A pamphlet in every pack.", "army_morale_factor = 0.10", ("Soviet.png", "Paper.png")),
    "VIT_mountain_committee": ("The Committee for the Mountain", "It watches the other committees too.", "stability_factor = 0.05\nresistance_growth = -0.10", ("Soviet.png", "Documents.png")),
    "VIT_may_day": ("May Day on Cherni Vrah", "Ten thousand red flags on the summit.", "stability_factor = 0.10\nwar_support_factor = 0.10\nindustrial_capacity_factory = 0.05", ("Soviet.png", "Star Red.png")),
    "VIT_trimontium_radio": ("Radio Trimontium", "Every evening, every wavelength.", "fascism_drift = 0.03", ("Rectangle.png", "Megaphone.png")),
    "VIT_trimontium_guard": ("The Trimontium Guard", "The city of three hills.", "army_org_factor = 0.05\narmy_defence_factor = 0.05", ("Army.png", "Helmet with Knife.png")),
    "VIT_sun_of_vergina": ("The Sun of Vergina", "Philip's golden sun on every black shirt.", "army_attack_factor = 0.10\nstability_factor = 0.05\nwar_support_factor = 0.05", ("Pentagon.png", "Torch Gold.png")),
    "VIT_mountain_in_flames_3": ("The Mountain in Flames", "Half the district is fighting the other half.",
                                 "stability_factor = -0.30\nindustrial_capacity_factory = -0.30\narmy_org_factor = -0.25\n"
                                 "war_support_factor = -0.10\nproduction_speed_buildings_factor = -0.30", ("Circle.png", "Fire.png")),
    "VIT_mountain_in_flames_2": ("The Mountain in Flames", "The front holds; the chaos behind it is easing.",
                                 "stability_factor = -0.20\nindustrial_capacity_factory = -0.20\narmy_org_factor = -0.15\n"
                                 "war_support_factor = -0.05\nproduction_speed_buildings_factor = -0.20", ("Circle.png", "Fire.png")),
    "VIT_mountain_in_flames_1": ("The Mountain in Flames", "The last embers of the chaos.",
                                 "stability_factor = -0.10\nindustrial_capacity_factory = -0.10\narmy_org_factor = -0.05\n"
                                 "production_speed_buildings_factor = -0.10", ("Circle.png", "Fire.png")),
    "VIT_mountain_in_flames_rebels": ("The Mountain in Flames", "Half the district is fighting the other half.",
                                      "stability_factor = -0.20\nindustrial_capacity_factory = -0.20\narmy_org_factor = -0.15",
                                      ("Circle.png", "Fire.png")),
    "VIT_mountain_rangers": ("Mountain Rangers", "Every path from Boyana to Cherni Vrah.",
                             "army_defence_factor = 0.10\nattrition = -0.10", ("Army.png", "Rifles Crossed.png")),
    "VIT_henrys_officers_idea": ("Henry's Officers", "Officers who are loyal to Henry first.", "army_org_factor = 0.10",
                                 ("Army.png", "Soldier Saluting.png")),
    "VIT_plovdiv_students": ("Students from Plovdiv", "Every train brings a few more.", "conscription_factor = 0.15",
                             ("Rectangle.png", "Book Open.png")),
    "VIT_half_english": ("Half English", "Tea at five and a stiff upper lip.",
                         "stability_factor = 0.10\npolitical_power_factor = 0.10", ("Shield Blue.png", "Lion.png")),
    "VIT_home_guard": ("The Home Guard", "An armband and a rifle for every street.", "army_defence_factor = 0.05\nconscription = 0.01",
                       ("Army.png", "Citizen.png")),
    "VIT_radio_vitosha": ("Radio Vitosha", "News from the free mountain every evening.", "democratic_drift = 0.03",
                          ("Rectangle.png", "Megaphone.png")),
    "VIT_fight_on_the_slopes": ("We Shall Fight on the Slopes", "We shall never surrender.",
                                "army_defence_factor = 0.10\nwar_support_factor = 0.10", ("Shield Blue.png", "Soldiers Charging.png")),
    "VIT_commonwealth": ("The Commonwealth of the Mountain", "The mountain and its dominions.",
                         "stability_factor = 0.15\npolitical_power_factor = 0.15\nresearch_speed_factor = 0.03",
                         ("Pentagon.png", "Lion.png")),
    "VIT_finest_hour": ("Our Finest Hour", "This was their finest hour.",
                        "stability_factor = 0.10\nwar_support_factor = 0.10\narmy_defence_factor = 0.10\narmy_attack_factor = 0.05",
                        ("Shield Blue.png", "Torch Gold.png")),
    "VIT_grandmas_rules": ("Grandma's Rules", "Church on Sunday, dinner at midnight, nobody leaves the table angry.",
                           "stability_factor = 0.10\npolitical_power_factor = 0.05", ("Shield.png", "Bread.png")),
    "VIT_monks_of_dragalevtsi": ("The Monks of Dragalevtsi", "The monastery blesses the banners.",
                                 "stability_factor = 0.05\nwar_support_factor = 0.05", ("Circle.png", "Cross.png")),
    "VIT_crowns_army": ("The Crown's Army", "Every soldier swears to the crown in the attic.",
                        "army_attack_factor = 0.05\narmy_defence_factor = 0.05\narmy_org_factor = 0.05", ("Army.png", "Crown.png")),
    "VIT_zevka_proud": ("Zevka Would Be Proud", "The Tsardom of the Mountain, as she dreamed it.",
                        "stability_factor = 0.15\npolitical_power_factor = 0.10\nresearch_speed_factor = 0.03",
                        ("Pentagon.png", "Crown.png")),
    "VIT_vitosha_soviet": ("The Vitosha Soviet", "The villa is a workers' rest home now.",
                           "political_power_factor = 0.10\nstability_factor = 0.05", ("Soviet.png", "Star Red.png")),
    "VIT_partisans": ("The Partisans of Vitosha", "Every path has a partisan who knows it.",
                      "army_defence_factor = 0.10\nattrition = -0.10", ("Soviet.png", "Rifles Crossed.png")),
    "VIT_comrades_from_vitosha": ("Comrades from Vitosha", "Students with leaflets in their satchels.", "communism_drift = 0.03",
                                  ("Rectangle.png", "Paper.png")),
    "VIT_red_army": ("The Red Army of the Mountain", "Commissars and red stars.", "army_org_factor = 0.05\narmy_attack_factor = 0.05",
                     ("Soviet.png", "Soldiers in Rows.png")),
    "VIT_thracian_commune": ("The Thracian Commune", "From the mountain to the road to Plovdiv.",
                             "political_power_factor = 0.15\nstability_factor = 0.10\nindustrial_capacity_factory = 0.05",
                             ("Soviet.png", "Hammer and Sickle.png")),
    "VIT_red_hill": ("The Red Hill", "May Day on the mountain.", "research_speed_factor = 0.05\narmy_attack_factor = 0.05",
                     ("Soviet.png", "Star Red2.png")),
    "VIT_black_shirts": ("Black Shirts", "Torches and marching songs.", "war_support_factor = 0.10\nconscription_factor = 0.10",
                         ("Rectangle.png", "Fist.png")),
    "VIT_legacy_of_philip": ("The Legacy of Philip", "Philip took a town and named it after himself.", "army_attack_factor = 0.10",
                             ("Army.png", "Helmet with Knife.png")),
    "VIT_torchlight": ("Torchlight on the Slopes", "A river of fire running uphill.",
                       "war_support_factor = 0.10\nstability_factor = 0.05", ("Rectangle.png", "Torch Gold.png")),
    "VIT_philippopolis": ("New Philippopolis", "Seven districts, seven hills, one city.",
                          "army_attack_factor = 0.10\nwar_support_factor = 0.10\npolitical_power_factor = 0.10",
                          ("Pentagon.png", "Torch.png")),
    "VIT_eighth_hill": ("The Eighth Hill", "Philippopolis has eight hills, and Vitosha is the tallest.",
                        "army_attack_factor = 0.05\narmy_defence_factor = 0.05\npolitical_power_factor = 0.10",
                        ("Pentagon.png", "Soldiers Charging.png")),
    "VIT_industrial_mountain": ("The Industrial Mountain", "Smoke on the slopes.",
                                "industrial_capacity_factory = 0.05\nproduction_speed_buildings_factor = 0.10",
                                ("Rectangle.png", "Cog.png")),
    "VIT_ski_troops": ("Ski Troops", "The fastest way down the mountain.", "army_attack_factor = 0.03\nattrition = -0.05",
                       ("Army.png", "Soldier.png")),
    "VIT_mountain_staff": ("The Mountain Staff", "Maps of every path.", "army_org_factor = 0.05\nexperience_gain_army_factor = 0.10",
                           ("Army.png", "Documents.png")),
    "VIT_army_of_the_mountain": ("The Army of the Mountain", "The best mountain army in Sofia.",
                                 "army_attack_factor = 0.05\narmy_defence_factor = 0.05", ("Pentagon.png", "Soldiers in Rows.png")),
}
TRAITS = {
    "evil_sofia_half_english": ("Half English", "Tea at five, a stiff upper lip and a mother who is never wrong.",
                                "stability_factor = 0.05\npolitical_power_factor = 0.05"),
    "evil_sofia_regent": ("Regent of the Mountain", "Governs in the name of the crown in the attic.",
                          "stability_factor = 0.05\npolitical_power_factor = 0.10"),
    "evil_sofia_tsar_of_the_mountain": ("Tsar of the Mountain", "Crowned in Boyana Church, as Zevka dreamed.",
                                        "stability_factor = 0.10\npolitical_power_factor = 0.10\narmy_org_factor = 0.05"),
    "evil_sofia_plovdiv_born": ("Born in Plovdiv", "Older than Rome, older than Athens, and never lets anyone forget it.",
                                "political_power_factor = 0.10\nwar_support_factor = 0.05"),
}
COSMETIC = {
    "VIT_COMMONWEALTH": ("Commonwealth of the Mountain", "Mountain", (40, 90, 160), ("mountain", "commonwealth")),
    "VIT_TSARDOM": ("Tsardom of the Mountain", "Mountain", (60, 120, 70), ("mountain", "tsardom")),
    "VIT_THRACIA": ("Thracian Commune", "Thracian", (190, 40, 40), ("mountain", "thracia")),
    "VIT_PHILIPPOPOLIS": ("New Philippopolis", "Philippopolitan", (60, 50, 40), ("mountain", "philippopolis")),
}
FACTIONS = {"EVIL_SOFIA_FACTION_MOUNTAIN_ENTENTE": "The Mountain Entente",
            "EVIL_SOFIA_FACTION_MOUNTAIN_LEAGUE": "The League of the Mountain",
            "EVIL_SOFIA_FACTION_RED_MOUNTAIN": "The Red Mountain",
            "EVIL_SOFIA_FACTION_SEVEN_HILLS": "The Pact of the Seven Hills"}

# ================================================================== events
GANG_YES = """base = 30
modifier = { add = 20 has_opinion = { target = FROM value > 20 } }
modifier = { add = 20 has_opinion = { target = FROM value > 50 } }
modifier = { factor = 0.4 has_opinion = { target = FROM value < 0 } }"""
GANG_NO = """base = 35
modifier = { add = 25 has_opinion = { target = FROM value < 0 } }"""
ENTENTE_YES = """base = 10
modifier = { add = 30 has_government = democratic }
modifier = { add = 15 democratic > 0.3 }
modifier = { add = 15 has_opinion = { target = FROM value > 30 } }"""
ENTENTE_NO = "base = 50"
_P = (["VIT"], "day")


def _alliance_events(first, name, gov, pitch, yes, no):
    """An invitation to one of the Vitosha alliances, its answer back to the inviter."""
    odds = (f"base = 10\nmodifier = {{ add = 35 has_government = {gov} }}\nmodifier = {{ add = 15 {gov} > 0.3 }}\n"
            "modifier = { add = 15 has_opinion = { target = FROM value > 30 } }")
    return {
        str(first): (name[0].upper() + name[1:], f"[From.GetLeader] of [From.GetName] invites [Root.GetName] to join {name}: {pitch}", _P,
                     [(yes, f"FROM = {{ add_to_faction = ROOT country_event = {{ id = evil_sofia_vit.{first + 1} }} }}", odds),
                      (no, f"FROM = {{ country_event = {{ id = evil_sofia_vit.{first + 2} }} }}", "base = 50")]),
        str(first + 1): (f"[From.GetName] Joins", f"[From.GetName] has joined {name}.", _P, [("Good.", "", 1)]),
        str(first + 2): ("[From.GetName] Declines", f"[From.GetName] will not join {name}.", _P, [("Their loss.", "", 1)]),
    }


EVENTS = {
    "1": ("An Invitation to the Evil Gang",
          "The old group chat lights up. [From.GetLeader] of [From.GetName] writes that the Evil Gang is meeting again, on "
          "the mountain this time, and that there is a seat for [Root.GetLeader].",
          _P, [("The gang is the gang.", "FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_vit.2 } }", GANG_YES),
               ("Not this time.", "FROM = { country_event = { id = evil_sofia_vit.3 } }", GANG_NO)]),
    "2": ("[From.GetLeader] Is In", "[From.GetName] has joined the Evil Gang.", _P, [("Welcome back.", "", 1)]),
    "3": ("[From.GetLeader] Says No", "[From.GetName] will not join the Evil Gang.", _P, [("Their loss.", "", 1)]),
    "4": ("Vitosha Wants In",
          "[From.GetLeader] of Vitosha has written to the group chat: the war on the mountain is over, and Vitosha wants to "
          "join the Evil Gang.",
          _P, [("Of course. The gang is the gang.", "add_to_faction = FROM\nFROM = { country_event = { id = evil_sofia_vit.5 } }", GANG_YES),
               ("Not after what happened.", "FROM = { country_event = { id = evil_sofia_vit.6 } }", GANG_NO)]),
    "5": ("Victor Says Yes", "Victor has welcomed us into the Evil Gang.", _P, [("The gang is whole again.", "", 1)]),
    "6": ("Victor Says No", "Victor will not have us in the Evil Gang.", _P, [("Then we will make our own.", "", 1)]),
    "7": ("The Mountain Entente",
          "[From.GetLeader] of Vitosha invites [Root.GetName] to join the Mountain Entente: an alliance of the free districts "
          "of Sofia, with tea.",
          _P, [("We join the Entente.", "FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_vit.8 } }", ENTENTE_YES),
               ("No, thank you.", "FROM = { country_event = { id = evil_sofia_vit.9 } }", ENTENTE_NO)]),
    "8": ("[From.GetName] Joins the Entente", "[From.GetName] has joined the Mountain Entente.", _P, [("Splendid.", "", 1)]),
    "9": ("[From.GetName] Declines", "[From.GetName] will not join the Mountain Entente.", _P, [("Pity.", "", 1)]),
    **_alliance_events(10, "the Red Mountain", "communism", "every worker in Sofia, with a friend on the mountain.",
                       "Workers of Sofia, unite.", "Not with them."),
    **_alliance_events(13, "the Pact of the Seven Hills", "fascism", "seven hills, seven seats, and Yani at the head of the table.",
                       "We take our seat.", "Not under Yani."),
    **_alliance_events(16, "the League of the Mountain", "neutrality", "districts with a strong hand at the top, and dinner at midnight.",
                       "We come to dinner.", "We eat at seven."),
}
NEWS = {
    "1": ("Civil War on Vitosha",
          "Vitosha has split in two. Daniel-Henry Capel's guard holds the villas and the west of the mountain; the followers "
          "of Yanislav Marazov, the student from Plovdiv, hold the east. Gunfire was heard from Dragalevtsi to Boyana last "
          "night, and the trams to the end of the line have stopped running.",
          (["VIT"], "fire"),
          [("The mountain will decide.", "", 1, "original_tag = VIT"), ("Keep the war on the mountain.", "", 1, "NOT = { original_tag = VIT }")]),
    "2": ("Henry Holds the Mountain",
          "The civil war on Vitosha is over, and Daniel-Henry Capel has won it. Yanislav Marazov's last followers have laid "
          "down their arms in Simeonovo. Henry's mother has told reporters that she never doubted it.",
          (["VIT"], "day"), [("The mountain is ours.", "", 1, "tag = VIT"), ("Henry stays.", "", 1, "NOT = { tag = VIT }")]),
    "3": ("Yani Takes the Mountain",
          "The civil war on Vitosha is over, and the student from Plovdiv has won it. Daniel-Henry Capel's villa in Boyana "
          "is in the hands of Yanislav Marazov's followers, and the city below is wondering what comes next.",
          (["VIT"], "dusk"), [("The mountain is ours.", "", 1, "tag = VIT"), ("A new master on the mountain.", "", 1, "NOT = { tag = VIT }")]),
    "4": ("The Commonwealth of the Mountain",
          "Daniel-Henry Capel has proclaimed the Commonwealth of the Mountain: Vitosha and its dominions at the foot of the "
          "mountain, under one parliament and one very English leader.",
          (["VIT_COMMONWEALTH"], "day"), [("God save the mountain.", "", 1, "tag = VIT"), ("Tea, anyone?", "", 1, "NOT = { tag = VIT }")]),
    "5": ("The Tsardom of the Mountain",
          "In Boyana Church, under its seven-hundred-year-old frescoes, Daniel-Henry Capel has been crowned Tsar of the "
          "Mountain with a crown his grandmother kept in the attic.",
          (["VIT_TSARDOM"], "dusk"), [("Long live the Tsar.", "", 1, "tag = VIT"), ("A tsar, on Vitosha?", "", 1, "NOT = { tag = VIT }")]),
    "6": ("The Thracian Commune",
          "Yanislav Marazov has proclaimed the Thracian Commune, from the top of Vitosha to the old road to Plovdiv.",
          (["VIT_THRACIA"], "day"), [("Forward, comrades.", "", 1, "tag = VIT"), ("Red on the mountain.", "", 1, "NOT = { tag = VIT }")]),
    "7": ("New Philippopolis",
          "Seven districts, seven hills: Yanislav Marazov has proclaimed New Philippopolis at the foot of Vitosha, and named "
          "each district after a hill of his native Plovdiv.",
          (["VIT_PHILIPPOPOLIS"], "night"), [("Philippopolis rises.", "", 1, "tag = VIT"), ("Seven hills of trouble.", "", 1, "NOT = { tag = VIT }")]),
}
ON_STARTUP = """if = {
	limit = { NOT = { has_global_flag = evil_sofia_vitosha_army } }
	set_global_flag = evil_sofia_vitosha_army
	VIT = {
		load_oob = "VIT_mountain_army"
		add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 4000 }
		army_experience = 25
	}
}"""


def _states_by_name(root, facts):
    """state name -> (id, provinces) for Vitosha's states."""
    out = {}
    for st in facts["states"]:
        if st["owner"] != TAG:
            continue
        path = next((os.path.join(root, "history", "states", f) for f in os.listdir(os.path.join(root, "history", "states"))
                     if f.startswith(f"{st['id']}-")), None)
        text = open(path, encoding="utf-8-sig").read()
        provs = [int(p) for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", text).group(1).split()]
        out[st["name"]] = (st["id"], provs)
    return out


def _oob(name, places):
    divs = []
    for i, prov in enumerate(places, 1):
        divs.append(f'\tdivision = {{\n\t\tname = "{i}{"st" if i == 1 else "nd" if i == 2 else "rd" if i == 3 else "th"} {name}"\n'
                    f'\t\tlocation = {prov}\n\t\tdivision_template = "City Guard"\n\t\tstart_experience_factor = 0.3\n'
                    f"\t\tstart_equipment_factor = 1.0\n\t}}")
    return "units = {\n" + "\n".join(divs) + "\n}\n"


def extra_build(root, facts, write, write_dds, loc, L):
    """Yani's character and portrait, and the armies loaded at the start and at the war."""
    st = _states_by_name(root, facts)
    write("history/units/VIT_mountain_army.txt", _oob("Mountain Guard", [st[n][1][0] for n in
          ("Vitosha", "Knyazhevo", "Marchaevo", "Dragalevtsi", "Simeonovo", "Kopitoto", "Vladaya", "Orehite")]))
    write("history/units/VIT_henry_army.txt", _oob("Boyana Loyalists", [st["Vitosha"][1][k % len(st["Vitosha"][1])] for k in range(4)]))
    write("history/units/VIT_yani_army.txt", _oob("Plovdiv Volunteers", [st["Simeonovo"][1][k % len(st["Simeonovo"][1])] for k in range(4)]))
    src = os.path.join(root, "tools", "portraits", "VIT_yani.png")
    portrait = ""
    if os.path.exists(src):
        face = Image.open(src).convert("RGBA")
        fw, fh = face.size
        if fw * 210 > fh * 156:
            nw = round(fh * 156 / 210)
            face = face.crop(((fw - nw) // 2, 0, (fw - nw) // 2 + nw, fh))
        elif fw * 210 < fh * 156:
            face = face.crop((0, 0, fw, round(fw * 210 / 156)))
        write_dds("gfx/leaders/VIT/VIT_yani.dds", np.asarray(face.resize((156, 210), Image.LANCZOS)))
        portrait = '\n\t\tportraits = {\n\t\t\tcivilian = {\n\t\t\t\tlarge = "gfx/leaders/VIT/VIT_yani.dds"\n\t\t\t}\n\t\t}'
    write("common/characters/evil_sofia_VIT_yani.txt", f"characters = {{\n\tVIT_yani = {{\n\t\tname = VIT_yani{portrait}\n\t}}\n}}\n")
    loc.extend([' VIT_yani:0 "Yanislav Marazov"',
                f' VIT_yani_desc:0 "{L("Yanislav Marazov came to Sofia from Plovdiv to study and stayed to change it. Everyone calls him Yani. He talks fast, remembers every name and never lets anyone forget that Plovdiv is older than Rome.")}"'])


# ================================================================== additions: spirits, events, alliances, tooltips, armies
IDEAS.update({
    "VIT_scars_of_war_2": ("Scars of War", "Broken factories, worn-out rifles and a lot of graves.",
                           "industrial_capacity_factory = -0.20\nproduction_speed_buildings_factor = -0.20\narmy_org_factor = -0.10\n"
                           "stability_factor = -0.10", ("Circle.png", "Skull.png")),
    "VIT_scars_of_war_1": ("Scars of War", "The worst is repaired. Not all of it.",
                           "industrial_capacity_factory = -0.10\nproduction_speed_buildings_factor = -0.10\narmy_org_factor = -0.05",
                           ("Circle.png", "Skull.png")),
    "VIT_h_dig_in": ("Hold Every Ridge", "Not one metre given up.", "army_defence_factor = 0.15\ndig_in_speed_factor = 0.25", ("Army.png", "Shovels Crossed.png")),
    "VIT_y_dig_in": ("Not a Step Back", "Every house a fortress.", "army_defence_factor = 0.15\ndig_in_speed_factor = 0.25", ("Rectangle.png", "Shovels Crossed.png")),
    "VIT_h_veterans": ("Veterans of the Mountain", "The men who held the villa.", "army_org_factor = 0.05\nexperience_gain_army_factor = 0.15", ("Army.png", "Soldier Saluting.png")),
    "VIT_y_veterans": ("Heroes of Simeonovo", "Every street named after one.", "army_morale_factor = 0.05\nexperience_gain_army_factor = 0.15", ("Rectangle.png", "Soldier Saluting.png")),
    "VIT_villa_pact": ("The Villa Pact", "Old friends, dinner at midnight.", "political_power_factor = 0.05\nwar_support_factor = 0.05", ("Shield Blue.png", "Hands Shaking.png")),
    "VIT_students_pact": ("The Students' Pact", "Signed on a school desk.", "political_power_factor = 0.05\nconscription_factor = 0.05", ("Rectangle.png", "Hands Shaking2.png")),
    "VIT_commandos": ("Commandos of Cherni Vrah", "They climb at night.", "special_forces_cap = 0.05\narmy_attack_factor = 0.03", ("Army.png", "Knife2.png")),
    "VIT_dispersed_workshops": ("Dispersed Workshops", "A workshop in every barn.", "industrial_capacity_factory = 0.05\nproduction_factory_efficiency_gain_factor = 0.05", ("Rectangle.png", "Cog.png")),
    "VIT_every_machine_counts": ("Every Machine Counts", "A foreman who never sleeps.", "production_factory_max_efficiency_factor = 0.05\nproduction_factory_efficiency_gain_factor = 0.10", ("Rectangle.png", "Wrench.png")),
    "VIT_workshop_of_sofia": ("The Workshop of Sofia", "Half of Sofia's goods were made on the mountain.",
                              "industrial_capacity_factory = 0.10\nproduction_speed_buildings_factor = 0.15\nresearch_speed_factor = 0.03", ("Pentagon.png", "Cog.png")),
    "VIT_rangers_of_the_peak": ("Rangers of the Peak", "Snow, fog and very good aim.", "army_attack_factor = 0.03\nattrition = -0.10", ("Army.png", "Rifles Crossed.png")),
    "VIT_dig_in_doctrine": ("Dig In Doctrine", "He digs before he eats.", "max_dig_in = 2\ndig_in_speed_factor = 0.20", ("Army.png", "Shovels Crossed.png")),
    "VIT_mountain_reserve": ("The Mountain Reserve", "The list is always up to date.", "conscription = 0.01\nmobilization_speed = 0.10", ("Army.png", "Documents.png")),
    "VIT_unbreakable_mountain": ("The Unbreakable Mountain", "Nobody ever took it from someone who wanted to keep it.",
                                 "army_attack_factor = 0.10\narmy_defence_factor = 0.10\narmy_org_factor = 0.05", ("Pentagon.png", "Soldiers in Rows.png")),
})
FACTIONS.update({"EVIL_SOFIA_FACTION_VILLA_PACT": "The Villa Pact", "EVIL_SOFIA_FACTION_STUDENT_PACT": "The Students' Pact"})
PERSON_ICONS.update({
    "henry_calls_KRP": ("KRP", "SunStarFrame.png", "Megaphone2.png", 0, dict(fill=(30, 40, 60), front_width=0.40, front_y=0.95)),
    "henry_calls_MLA": ("MLA", "LeavedFrame.png", "Megaphone2.png", 0, dict(fill=(30, 40, 60), front_width=0.40, front_y=0.95)),
    "henry_calls_SRD": ("SRD", "SilverStarFrame.png", "Megaphone2.png", 0, dict(fill=(30, 40, 60), front_width=0.40, front_y=0.95)),
    "yani_calls_KRP": ("KRP", "SpikyFrame.png", "Book Open.png", 0, dict(fill=(50, 30, 26), front_width=0.38, front_y=1.05)),
    "yani_calls_LOZ": ("LOZ", "RedWheatFrame.png", "Book Open.png", 0, dict(fill=(50, 30, 26), front_width=0.38, front_y=1.05)),
})
PERSON_FALLBACK.update({k: "goal_ANQ_patriotic_protests" for k in PERSON_ICONS if k not in PERSON_FALLBACK})

_CALL_HENRY = """base = 70
modifier = { add = 20 has_opinion = { target = FROM value > 20 } }
modifier = { factor = 0 has_government = communism }"""
EVENTS.update({
    "19": ("Henry Calls", "The telephone rings at midnight. It is Daniel-Henry Capel, from the villa on the hill: a war is "
           "coming to Vitosha, he says, and he would like his old friend [Root.GetLeader] on his side. There will be dinner.",
           _P, [("For old times' sake.", "FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_vit.20 } }", _CALL_HENRY),
                ("Not this time, Henry.", "FROM = { country_event = { id = evil_sofia_vit.21 } }", "base = 20")]),
    "20": ("[From.GetLeader] Answers", "[From.GetName] has joined us.", _P, [("A true friend.", "", 1)]),
    "21": ("[From.GetLeader] Hangs Up", "[From.GetName] will not join us.", _P, [("We will remember.", "", 1)]),
    "22": ("A Letter from Yani", "A letter in handwriting [Root.GetLeader] has not seen since school: Yanislav Marazov, "
           "the old classmate from Plovdiv, needs his friends. Whatever they believe now, a classmate is a classmate.",
           _P, [("A classmate is a classmate.", "FROM = { add_to_faction = ROOT country_event = { id = evil_sofia_vit.23 } }", 100),
                ("Not even for Yani.", "FROM = { country_event = { id = evil_sofia_vit.24 } }", 0)]),
    "23": ("[From.GetLeader] Is with Us", "[From.GetName] has joined us.", _P, [("Just like school.", "", 1)]),
    "24": ("[From.GetLeader] Says No", "[From.GetName] will not join us.", _P, [("Some classmate.", "", 1)]),
    "25": ("The Mountain Explodes",
           "Nobody chose the day. A brawl outside a café in Simeonovo, a shot, a second shot, and by nightfall the whole "
           "mountain is at war with itself. Whatever was ready is ready. Whatever was not, is not.",
           _P, "NOT = { has_country_flag = VIT_war_started }\nexists = yes",
           [("Then we fight.", ifc("has_completed_focus = VIT_march_with_yani",
                                   TAKE_THE_VILLA + "\nunlock_national_focus = VIT_yani_takes_the_villa")
             + "\nelse = {\n" + ind(CRUSH + "\nunlock_national_focus = VIT_crush_the_student_movement") + "}", 1)]),
    "26": ("An Offer of Dominion",
           "[From.GetLeader] of [From.GetName] offers [Root.GetName] a place in the Commonwealth of the Mountain: our own "
           "parliament, our own laws, and the mountain's army to defend us. In return, the mountain decides our foreign policy.",
           _P, [("We accept dominion status.", "FROM = { puppet = ROOT }", """base = 15
modifier = { add = 25 has_opinion = { target = FROM value > 30 } }
modifier = { add = 20 num_of_factories < 10 }"""),
                ("We stay independent.", "", "base = 60")]),
})
ON_STARTUP += """
if = {
	limit = { NOT = { has_global_flag = evil_sofia_vitosha_timer } }
	set_global_flag = evil_sofia_vitosha_timer
	VIT = { country_event = { id = evil_sofia_vit.25 days = 400 } }
}"""

_W = "§YWhen the civil war starts§!, if we are on this side: "
_TEMP = " They are §Rsent home§! when the war is won."
UNLOCK_TOOLTIPS.update({
    "the_boyana_garrison": _W + "§G+4 divisions§! in Boyana.",
    "mothers_savings": _W + "§G+2,500 rifles§!.",
    "the_mountain_rangers": _W + "the spirit §YMountain Rangers§!.",
    "henrys_officers": _W + "§G+30 army experience§! and the spirit §YHenry's Officers§!.",
    "friends_at_the_gate": _W + "§G+2 temporary divisions§! from Henry's friends." + _TEMP,
    "guards_for_hire": _W + "§G+3 temporary divisions§! of hired guards." + _TEMP,
    "the_british_club": _W + "§G+2 temporary divisions§! of British Club volunteers." + _TEMP,
    "cells_in_simeonovo": _W + "§G+4 divisions§! in Simeonovo.",
    "students_from_plovdiv": _W + "§G+20,000 manpower§! and the spirit §YStudents from Plovdiv§!.",
    "arms_from_plovdiv": _W + "§G+2,500 rifles§!.",
    "the_plovdiv_committee": _W + "§G+10% war support§! and §G+20 army experience§!.",
    "classmates_at_the_front": _W + "§G+2 temporary divisions§! from Yani's classmates." + _TEMP,
    "caches_in_the_forest": _W + "§G+2,000 rifles§!.",
    "drills_in_the_woods": _W + "§G+20 army experience§!.",
    "barricades_in_simeonovo": _W + "§Glevel 3 bunkers§! along Simeonovo's borders.",
    "the_tobacco_column": _W + "§G+3 temporary divisions§! of Plovdiv tobacco workers." + _TEMP,
    "studentski_volunteers": _W + "§G+2 temporary divisions§! of students." + _TEMP,
    "stand_with_henry": "If the war has not started after §Y400 days§!, it starts by itself on Henry's side, unless we "
                        "completed March with Yani. Only completed focuses give their bonuses.",
    "march_with_yani": "If the war has not started after §Y400 days§!, it starts by itself on Yani's side. Only completed "
                       "focuses give their bonuses.",
})

_extra_build_base = extra_build
TEMP_ARMIES = {"VIT_friends_of_the_villa": ("Friends of the Villa", "Vitosha", 2),
               "VIT_hired_guard": ("Hired Guard", "Vitosha", 3),
               "VIT_club_volunteers": ("Club Volunteers", "Vitosha", 2),
               "VIT_classmates": ("Classmates", "Simeonovo", 2),
               "VIT_plovdiv_column": ("Plovdiv Column", "Simeonovo", 3),
               "VIT_studentski_volunteers": ("Studentski Volunteers", "Simeonovo", 2)}
_ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def extra_build(root, facts, write, write_dds, loc, L):
    """As before, plus the temporary armies: each has its own template, so the war's end can delete them."""
    _extra_build_base(root, facts, write, write_dds, loc, L)
    st = _states_by_name(root, facts)
    for fname, (template, state, n) in TEMP_ARMIES.items():
        provs = st[state][1]
        tpl = (f'division_template = {{\n\tname = "{template}"\n\tregiments = {{\n\t\tinfantry = {{ x = 0 y = 0 }}\n'
               f'\t\tinfantry = {{ x = 0 y = 1 }}\n\t\tinfantry = {{ x = 1 y = 0 }}\n\t}}\n}}\n\n')
        divs = "\n".join(f'\tdivision = {{\n\t\tname = "{_ORD[k]} {template}"\n\t\tlocation = {provs[k % len(provs)]}\n'
                         f'\t\tdivision_template = "{template}"\n\t\tstart_experience_factor = 0.2\n\t\tstart_equipment_factor = 1.0\n\t}}'
                         for k in range(1, n + 1))
        write(f"history/units/{fname}.txt", tpl + "units = {\n" + divs + "\n}\n")


# ================================================================== the war names
COSMETIC.update({
    "VIT_HENRY": ("Henry's Vitosha", "Vitoshan", (40, 70, 150), ("mountain", "henry")),
    "VIT_YANI": ("Yani's Vitosha", "Vitoshan", (150, 30, 30), ("mountain", "yani")),
})
ON_ACTIONS = """	on_civil_war_end = {
		effect = {
			every_country = {
				limit = { OR = { has_cosmetic_tag = VIT_HENRY has_cosmetic_tag = VIT_YANI } }
				drop_cosmetic_tag = yes
			}
		}
	}
"""

# ================================================================== foreign aid: a focus on every path, then decisions
SAME = ("OR = { AND = { ROOT = { has_government = democratic } has_government = democratic } "
        "AND = { ROOT = { has_government = neutrality } has_government = neutrality } "
        "AND = { ROOT = { has_government = communism } has_government = communism } "
        "AND = { ROOT = { has_government = fascism } has_government = fascism } }")
DONOR = f"any_other_country = {{ exists = yes NOT = {{ original_tag = VIT }} {SAME} }}"
AID_FOCUSES = [
    ("friends_across_the_valley", "Friends Across the Valley", 0, 11, [["a_cabinet_of_all_talents"]], "duo:goal_generic_positive_trade_relations",
     "Every free district of Sofia has something to spare for the mountain, and Henry is very good at asking."),
    ("friends_of_the_crown", "Friends of the Crown", 25, 12, [["the_estates_of_knyazhevo"]], "duo:goal_generic_foreign_investments",
     "Every district with a strong hand at the top understands what Henry is doing, and some of them will help."),
    ("help_from_the_comrades", "Help from the Comrades", 36, 11, [["the_red_air_brigade"]], "duo:Generic_Bakuninist_Collectivism",
     "Every red district in Sofia owes the revolution something. Yani sends them the bill."),
    ("friends_of_the_torch", "Friends of the Torch", 53, 13, [["the_iron_phalanx"]], "duo:goal_generic_seize_money",
     "The black shirts of other districts send what they can: rifles, money and young men looking for a fight."),
]
for fid, name, x, y, pre, icon, desc in AID_FOCUSES:
    F(fid, name, x, y, pre, [], 6, icon, "", "set_country_flag = VIT_aid_open\nadd_political_power = 25",
      desc + "\\n\\nUnlocks the §YForeign Aid§! decisions: ask districts with the same ideology as ours for rifles, "
      "volunteers, aeroplanes, lorries and advisers.", ["POLITICAL"])
    UNLOCK_TOOLTIPS[fid] = "Unlocks the §YForeign Aid§! decisions (rifles, volunteers, aeroplanes, lorries, advisers)."
for i, (fid, *_rest) in enumerate(AID_FOCUSES):
    FILTERS[fid] = ["POLITICAL", "MANPOWER"]


def _aid(key, name, desc, cost, give, take):
    return dict(id=f"VIT_aid_{key}", name=name, desc=desc + "\n\nAsks a district with the same ideology as ours; it gives "
                "up what we receive.", cost=cost, cooldown=120, visible="", available=DONOR,
                effect=f"random_other_country = {{\n\tlimit = {{ exists = yes NOT = {{ original_tag = VIT }} {SAME} }}\n"
                       f"{ind(take)}}}\n{give}", ai="factor = 1", icon="generic_prepare_civil_war")


DECISION_CATS = [("VIT_foreign_aid", "Foreign Aid",
                  "Friends with the same ideology as ours can spare rifles, men and machines for the mountain.",
                  "original_tag = VIT", "has_country_flag = VIT_aid_open", [
    _aid("rifles", "Request Rifles", "Crates of rifles, sent up the mountain road by night.", 25,
         "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }",
         "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = -1500 }"),
    _aid("volunteers", "Request Volunteers", "Young men who want to fight for the mountain.", 50,
         "add_manpower = 8000", "add_manpower = -8000"),
    _aid("aeroplanes", "Request Aeroplanes", "A few aeroplanes and the pilots to fly them.", 75,
         "add_equipment_to_stockpile = { type = small_plane_airframe_1 amount = 10 }\nair_experience = 10",
         "add_equipment_to_stockpile = { type = small_plane_airframe_1 amount = -10 }"),
    _aid("lorries", "Request Lorries", "Lorries for the mountain road.", 40,
         "add_equipment_to_stockpile = { type = motorized_equipment_1 amount = 60 }",
         "add_equipment_to_stockpile = { type = motorized_equipment_1 amount = -60 }"),
    _aid("advisers", "Request Military Advisers", "Officers who have seen a real war, on loan.", 50,
         "army_experience = 20", "army_experience = -10"),
])]

# ================================================================== Henry's colonies: the mines on the other side of Sofia
COLONIES = [
    ("the_colonial_office", "The Colonial Office", 2, 15, [["an_offer_of_dominion"]], 7, "duo:goal_generic_globe", NOWAR,
     "add_political_power = 50",
     "England had an empire for its coal and its metals. The mountain is made of granite, but on the other side of "
     "Sofia there is iron at Kremikovtsi, the old mine at Buhovo and coal under Lyulin and Bankya, where the Pernik basin "
     "begins. Henry opens a Colonial Office.", ["POLITICAL", "ANNEXATION"]),
    ("the_kremikovtsi_company", "The Kremikovtsi Company", 1, 16, [["the_colonial_office"]], 9, "duo:Generic_More_OIL", NOWAR,
     "if = { limit = { country_exists = KRE NOT = { has_war_with = KRE is_in_faction_with = KRE } } "
     "create_wargoal = { type = puppet_wargoal_focus target = KRE } }\nadd_political_power = 25",
     "A chartered company for the iron ore and the steelworks of Kremikovtsi, and the Buhovo mine next to them. Every "
     "company needs a flag, and every flag needs a garrison.\\n\\nA war goal to make Kremikovtsi our colony (puppet).",
     ["ANNEXATION"]),
    ("the_lyulin_coal_concession", "The Lyulin Coal Concession", 3, 16, [["the_colonial_office"]], 9, "duo:Generic_Oil_Concern", NOWAR,
     "\n".join(f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} is_in_faction_with = {t} }} }} "
               f"create_wargoal = {{ type = puppet_wargoal_focus target = {t} }} }}" for t in ("LYU", "BNK")),
     "The coal seams of the Pernik basin run under Lyulin mountain and Bankya. Henry would like a concession, and a "
     "garrison to protect it.\\n\\nWar goals to make Lyulin and Bankya our colonies (puppets).", ["ANNEXATION"]),
    ("the_mountain_mining_company", "The Mountain Mining Company", 2, 17,
     [["the_kremikovtsi_company"], ["the_lyulin_coal_concession"]], 10, "duo:Generic_Oil_Production", "",
     "{RESOURCE:steel:4:KRE,LYU,BNK}\n{RESOURCE:tungsten:2:KRE}\n" + factory("industrial_complex"),
     "One company for every mine in the colonies: the ore goes up the mountain road, the money goes into the villa.\\n\\n"
     "Every state of Kremikovtsi, Lyulin and Bankya that we or our subjects hold gets more steel, and Kremikovtsi's "
     "more tungsten.", ["INDUSTRY"]),
]
for fid, name, x, y, pre, w, icon, avail, rew, desc, filt in COLONIES:
    F(fid, name, x, y, pre, [], w, icon, avail, rew, desc, filt)

EVENTS.update({
    "27": ("Henry's Road",
           "The guns are firing on the slopes, and the villa has to decide what it is fighting for. Henry's father's "
           "family would hold elections and win them. His grandmother Zevka would never have bothered.",
           _P, [("The English way: a parliament and a vote.", "complete_national_focus = VIT_what_the_english_couldnt_do", 50),
                ("Zevka's way: one firm hand.", "complete_national_focus = VIT_what_zevka_wanted", 50)]),
    "28": ("Yani's Road",
           "The student from Plovdiv has his war. Now his movement must decide what it is: the red Plovdiv of the "
           "tobacco strikes, or the black shirts and the seven hills.",
           _P, [("Red Plovdiv.", "complete_national_focus = VIT_red_plovdiv",
                 "base = 50\nmodifier = { add = 50 has_government = communism }\nmodifier = { factor = 0.2 has_government = fascism }"),
                ("The Seven Hills.", "complete_national_focus = VIT_the_seven_hills",
                 "base = 50\nmodifier = { add = 50 has_government = fascism }\nmodifier = { factor = 0.2 has_government = communism }")]),
})
UNLOCK_TOOLTIPS["crush_the_student_movement"] += " The next day, choose Henry's road at once by event."
UNLOCK_TOOLTIPS["yani_takes_the_villa"] += " The next day, choose Yani's road at once by event."
