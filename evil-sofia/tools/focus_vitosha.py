"""Vitosha focus tree: Daniel-Henry Capel or Yanislav Marazov, a civil war like vanilla's Spanish one.

Before the war, Henry chooses his road (the English Way: democratic; Zevka's Dream: authoritarian) and Yani's
movement from Plovdiv grows (Red Plovdiv: communist; the Black Shirts of Plovdiv: fascist). Both camps prepare:
their focuses bank divisions, equipment and spirits for the side that will fight. The Mountain Splits sets the two
ideologies to roughly equal support; then the player picks a side:
  Stand with Henry   Vitosha stays Henry's; Yani's rebels take the east (5 states). Winnable in about a year.
  March with Yani    Vitosha becomes Yani's; Henry's loyalists take the west and Boyana (10 states). Hard.
Both sides start the war under The Mountain in Flames (three tiers, taken down by focuses). After the war each of the
four leader/ideology pairs has its own branch and formable; the Evil Gang, industry and army branches are open to all.

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


# the two camps' land in the war
YANI_EAST = ["Simeonovo", "Malinova Dolina Villas", "Dragalevtsi", "Dragalevtsi Lift", "Orehite"]
HENRY_WEST = ["Vitosha", "Kopitoto", "Karpuzitsa", "Knyazhevo", "Priplat Villas", "Vladaya Villas", "Vladaya",
              "Marchaevo", "Marchaevo Woods", "Marchaevo Hills"]

LEADER = '"1965.1.1.1"'


def henry_role(ideology, promote):
    return (f"add_country_leader_role = {{\n\tcharacter = VIT_leader\n\tcountry_leader = {{ ideology = {ideology} "
            f"expire = {LEADER} }}\n" + ("\tpromote_leader = yes\n" if promote else "") + "}")


def yani_role(ideology, promote):
    return (f"add_country_leader_role = {{\n\tcharacter = VIT_yani\n\tcountry_leader = {{ desc = \"VIT_yani_desc\" "
            f"ideology = {ideology} expire = {LEADER} traits = {{ evil_sofia_plovdiv_born }} }}\n"
            + ("\tpromote_leader = yes\n" if promote else "") + "}")


def ifc(cond, body, kw="if"):
    return f"{kw} = {{\n\tlimit = {{ {cond} }}\n" + "".join(f"\t{ln}\n" for ln in body.split("\n")) + "}"


def war(ideology, size, capital, states):
    return (f"start_civil_war = {{\n\tideology = {ideology}\n\tsize = {size}\n\tcapital = {S(capital)}\n"
            f"\tstates = {{ {' '.join(S(n) for n in states)} }}\n}}")


HENRY_PREP = "\n".join([
    ifc("ROOT = { has_completed_focus = VIT_the_boyana_garrison }", 'load_oob = "VIT_henry_army"'),
    ifc("ROOT = { has_completed_focus = VIT_mothers_savings }",
        "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2500 }"),
    ifc("ROOT = { has_completed_focus = VIT_the_mountain_rangers }", "add_ideas = VIT_mountain_rangers"),
    ifc("ROOT = { has_completed_focus = VIT_henrys_officers }", "army_experience = 30\nadd_ideas = VIT_henrys_officers_idea")])
YANI_PREP = "\n".join([
    ifc("ROOT = { has_completed_focus = VIT_cells_in_simeonovo }", 'load_oob = "VIT_yani_army"'),
    ifc("ROOT = { has_completed_focus = VIT_students_from_plovdiv }", "add_manpower = 20000\nadd_ideas = VIT_plovdiv_students"),
    ifc("ROOT = { has_completed_focus = VIT_arms_from_plovdiv }",
        "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 2500 }")])
REBELS = "every_other_country = {\n\tlimit = { original_tag = VIT has_civil_war = yes }\n"


def rebels(body):
    return REBELS + "".join(f"\t{ln}\n" for ln in body.split("\n")) + "}"


STAND_WITH_HENRY = "\n".join([
    ifc("has_completed_focus = VIT_the_english_way",
        "set_politics = { ruling_party = democratic elections_allowed = no }\n" + henry_role("conservatism", True)),
    "recruit_character = VIT_yani",
    ifc("has_completed_focus = VIT_red_plovdiv_rises", yani_role("leninism", False) + "\n" + war("communism", 0.3, "Simeonovo", YANI_EAST)),
    "else = {\n" + "".join(f"\t{ln}\n" for ln in (yani_role("fascism_ideology", False) + "\n" + war("fascism", 0.3, "Simeonovo", YANI_EAST)).split("\n")) + "}",
    "add_ideas = VIT_mountain_in_flames_3", HENRY_PREP,
    rebels("add_timed_idea = { idea = VIT_mountain_in_flames_rebels days = 365 }\n" + YANI_PREP),
    "set_country_flag = VIT_henry_side", "set_country_flag = VIT_war_started",
    "news_event = { id = evil_sofia_vit_news.1 hours = 6 }"])
MARCH_WITH_YANI = "\n".join([
    "recruit_character = VIT_yani",
    f"set_capital = {{ state = {S('Simeonovo')} }}",
    ifc("has_completed_focus = VIT_red_plovdiv_rises",
        "set_politics = { ruling_party = communism elections_allowed = no }\n" + yani_role("leninism", True)),
    "else = {\n" + "".join(f"\t{ln}\n" for ln in ("set_politics = { ruling_party = fascism elections_allowed = no }\n" + yani_role("fascism_ideology", True)).split("\n")) + "}",
    ifc("has_completed_focus = VIT_the_english_way", henry_role("conservatism", False) + "\n" + war("democratic", 0.6, "Vitosha", HENRY_WEST)),
    "else = {\n" + "".join(f"\t{ln}\n" for ln in war("neutrality", 0.6, "Vitosha", HENRY_WEST).split("\n")) + "}",
    "add_ideas = VIT_mountain_in_flames_3", YANI_PREP,
    rebels("add_timed_idea = { idea = VIT_mountain_in_flames_rebels days = 365 }\n" + HENRY_PREP),
    "set_country_flag = VIT_yani_side", "set_country_flag = VIT_war_started",
    "news_event = { id = evil_sofia_vit_news.1 hours = 6 }"])
SPLIT_POPULARITY = "\n".join([
    ifc("has_completed_focus = VIT_the_english_way has_completed_focus = VIT_red_plovdiv_rises",
        "set_popularities = { democratic = 45 communism = 45 neutrality = 10 fascism = 0 }"),
    ifc("has_completed_focus = VIT_the_english_way has_completed_focus = VIT_black_shirts_of_plovdiv",
        "set_popularities = { democratic = 45 fascism = 45 neutrality = 10 communism = 0 }", "else_if"),
    ifc("has_completed_focus = VIT_zevkas_dream has_completed_focus = VIT_red_plovdiv_rises",
        "set_popularities = { neutrality = 45 communism = 45 democratic = 10 fascism = 0 }", "else_if"),
    "else = { set_popularities = { neutrality = 45 fascism = 45 democratic = 10 communism = 0 } }"])
FLAMES_DOWN = "\n".join([
    ifc("has_idea = VIT_mountain_in_flames_3", "swap_ideas = { remove_idea = VIT_mountain_in_flames_3 add_idea = VIT_mountain_in_flames_2 }"),
    ifc("has_idea = VIT_mountain_in_flames_2", "swap_ideas = { remove_idea = VIT_mountain_in_flames_2 add_idea = VIT_mountain_in_flames_1 }", "else_if"),
    ifc("has_idea = VIT_mountain_in_flames_1", "remove_ideas = VIT_mountain_in_flames_1", "else_if")])
FLAMES_OUT = "\n".join(f"if = {{ limit = {{ has_idea = VIT_mountain_in_flames_{i} }} remove_ideas = VIT_mountain_in_flames_{i} }}"
                       for i in (1, 2, 3))
HENRY_DEM = "has_country_flag = VIT_henry_side\nhas_completed_focus = VIT_the_english_way"
HENRY_AUT = "has_country_flag = VIT_henry_side\nhas_completed_focus = VIT_zevkas_dream"
YANI_COM = "has_country_flag = VIT_yani_side\nhas_completed_focus = VIT_red_plovdiv_rises"
YANI_FAS = "has_country_flag = VIT_yani_side\nhas_completed_focus = VIT_black_shirts_of_plovdiv"
FLAMES_TT = "\n\nTakes The Mountain in Flames down one step."

# ================================================================== before the war
F("the_house_on_the_hill", "The House on the Hill", 12, 0, [], [], 5, "duo:Generic_Castle", "",
  "add_political_power = 50\narmy_experience = 10",
  "Daniel-Henry Capel rules Vitosha from a villa on the hill, with the forest at his back and the whole of Sofia "
  "spread out below. Half English, half Bulgarian and entirely sure of himself, he has the strongest guard of any "
  "district. He also has a problem: a student from Plovdiv called Yanislav Marazov, and the people who listen to him.",
  ["POLITICAL"])
F("the_english_way", "The English Way", 3, 1, [["the_house_on_the_hill"]], ["zevkas_dream"], 7, "duo:Generic_Conservatism", "",
  "add_timed_idea = { idea = VIT_english_way_drift days = 240 }\nadd_stability = 0.03",
  "Henry's father's side of the family drinks tea at five, believes in parliaments and never raises its voice. Henry "
  "decides that Vitosha will be governed the English way: properly, politely and with a vote now and then.\\n\\n"
  "Henry's road is democratic. Democracy grows in Vitosha for eight months.", ["POLITICAL"])
F("zevkas_dream", "Zevka's Dream", 7, 1, [["the_house_on_the_hill"]], ["the_english_way"], 7, "duo:Generic_Orthodoxy", "",
  "add_timed_idea = { idea = VIT_zevkas_drift days = 240 }\nadd_stability = 0.03",
  "Henry's Bulgarian grandmother Zevka had firm views on everything: the church on Sunday, dinner at seven, the land "
  "in the family and a strong hand at the top. She never lived to see Vitosha run properly. Henry will see to it.\\n\\n"
  "Henry's road is authoritarian: Vitosha stays under one hand.", ["POLITICAL"])
F("the_boyana_garrison", "The Boyana Garrison", 4, 2, [["the_english_way", "zevkas_dream"]], [], 8, "duo:Generic_Soldiers_Defense", "",
  "army_experience = 10",
  "The guard battalions in Boyana are given new barracks, new rifles and officers who are loyal to Henry first.\\n\\n"
  "When the war comes, Henry's side gets four more divisions in Boyana.", ["MANPOWER"])
F("mothers_savings", "Mother's Savings", 6, 2, [["the_english_way", "zevkas_dream"]], [], 6, "duo:Generic_Loadsamoney", "",
  "add_political_power = 50",
  "Henry's mother has been putting money aside for years, against exactly this kind of day. She opens the tin.\\n\\n"
  "When the war comes, Henry's side gets 2,500 rifles.", ["INDUSTRY"])
F("the_mountain_rangers", "The Mountain Rangers", 4, 3, [["the_boyana_garrison"]], [], 9, "duo:Generic_Mountain_Warfare", "",
  "army_experience = 10",
  "Hunters, foresters and mountain guides who know every path from Boyana to Cherni Vrah.\\n\\nWhen the war comes, "
  "Henry's side gets the spirit Mountain Rangers (better defence and less attrition).", ["ARMY_XP"])
F("henrys_officers", "Henry's Officers", 6, 3, [["mothers_savings"]], [], 8, "duo:Generic_Command_Power", "",
  "add_political_power = 25",
  "Henry quietly replaces every officer he is not sure of with one he is.\\n\\nWhen the war comes, Henry's side gets "
  "30 army experience and the spirit Henry's Officers (better organisation).", ["ARMY_XP"])
F("a_student_from_plovdiv", "A Student from Plovdiv", 18, 1, [["the_house_on_the_hill"]], [], 6,
  "person:a_student_from_plovdiv", "",
  "add_political_power = 25",
  "Yanislav Marazov came to Sofia from Plovdiv to study and never went home. In the cafés of Simeonovo and "
  "Dragalevtsi he talks, and more people listen every week. Henry's guards have a file on him. It is getting thick.",
  ["POLITICAL"])
F("red_plovdiv_rises", "Red Plovdiv", 16, 2, [["a_student_from_plovdiv"]], ["black_shirts_of_plovdiv"], 7, "duo:Generic_Marxism", "",
  "add_timed_idea = { idea = VIT_red_plovdiv_drift days = 240 }",
  "Yani grew up among the tobacco workers of Plovdiv and their strikes. He preaches what they preached: the land to "
  "the villages, the villas to the people, the hill to the workers.\\n\\nYani's movement is communist. Communism grows "
  "in Vitosha for eight months.", ["POLITICAL"])
F("black_shirts_of_plovdiv", "The Black Shirts of Plovdiv", 20, 2, [["a_student_from_plovdiv"]], ["red_plovdiv_rises"], 7,
  "duo:Generic_Fascist_Guy", "",
  "add_timed_idea = { idea = VIT_black_shirts_drift days = 240 }",
  "Plovdiv is older than Rome, older than Athens, and Yani has never let anyone forget it. Order, glory and the city "
  "of Philip of Macedon: his followers wear black shirts and march in step.\\n\\nYani's movement is fascist. Fascism "
  "grows in Vitosha for eight months.", ["POLITICAL"])
F("cells_in_simeonovo", "Cells in Simeonovo", 16, 3, [["red_plovdiv_rises", "black_shirts_of_plovdiv"]], [], 8,
  "duo:Generic_Espionage", "", "add_political_power = 25",
  "Rifles hidden under floorboards, a printing press in a garage and a list of names.\\n\\nWhen the war comes, Yani's "
  "side gets four more divisions in Simeonovo.", ["MANPOWER"])
F("students_from_plovdiv", "Students from Plovdiv", 18, 3, [["red_plovdiv_rises", "black_shirts_of_plovdiv"]], [], 7,
  "duo:Generic_Volunteer_Corps", "", "add_political_power = 25",
  "Every train from Plovdiv brings a few more of Yani's old classmates, with a suitcase and an address in Simeonovo.\\n\\n"
  "When the war comes, Yani's side gets 20,000 manpower and the spirit Students from Plovdiv (more recruits).", ["MANPOWER"])
F("arms_from_plovdiv", "Arms from Plovdiv", 20, 3, [["red_plovdiv_rises", "black_shirts_of_plovdiv"]], [], 6,
  "duo:Generic_Shady_Deal", "", "add_political_power = 25",
  "Tobacco crates from Plovdiv are heavier than tobacco.\\n\\nWhen the war comes, Yani's side gets 2,500 rifles.",
  ["INDUSTRY"])
F("the_mountain_splits", "The Mountain Splits", 12, 4,
  [["the_english_way", "zevkas_dream"], ["red_plovdiv_rises", "black_shirts_of_plovdiv"]], [], 8,
  "duo:Generic_Factionalism", "", SPLIT_POPULARITY + "\nadd_stability = -0.10",
  "Henry's guard and Yani's followers no longer pass each other in the street without a fight. Half of Vitosha stands "
  "with the villa on the hill, half with the student from Plovdiv. Something has to give.\\n\\nSupport is split almost "
  "evenly: 45% for Henry's ideology, 45% for Yani's. Then choose whom to follow.", ["POLITICAL"])
F("stand_with_henry", "Stand with Henry", 10, 5, [["the_mountain_splits"]], ["march_with_yani"], 5,
  "person:stand_with_henry", "", STAND_WITH_HENRY,
  "Henry holds the villa, the guard and the west of the mountain. Yani holds the east, the students and the anger. "
  "We stand with Henry.\\n\\nThe civil war begins: Yani's rebels take the five eastern states of Vitosha (Simeonovo, "
  "Malinova Dolina, Dragalevtsi, Dragalevtsi Lift, Orehite). Everything Henry's camp prepared joins us; everything "
  "Yani's camp prepared joins them. We start the war under The Mountain in Flames.", ["POLITICAL", "WAR_SUPPORT"])
F("march_with_yani", "March with Yani", 14, 5, [["the_mountain_splits"]], ["stand_with_henry"], 5,
  "person:march_with_yani", "", MARCH_WITH_YANI,
  "The future belongs to the student from Plovdiv, not to the villa on the hill. We march with Yani.\\n\\nYani becomes "
  "the leader of Vitosha and the civil war begins: Henry's loyalists take Boyana and the west, ten states in all. "
  "Everything Yani's camp prepared joins us; everything Henry's camp prepared joins them. We start the war under "
  "The Mountain in Flames. It will be hard.", ["POLITICAL", "WAR_SUPPORT"])
# the war: the Mountain in Flames comes down step by step
F("restore_the_chain_of_command", "Restore the Chain of Command", 10, 6, [["stand_with_henry", "march_with_yani"]], [], 7,
  "duo:Generic_Radio_Operator", "has_country_flag = VIT_war_started", FLAMES_DOWN + "\narmy_experience = 15",
  "Half the officers have changed sides, the other half are not answering the telephone. A field telephone line, "
  "a list of who is still loyal and a lot of shouting." + FLAMES_TT, ["ARMY_XP", "STABILITY"])
F("requisition_the_workshops", "Requisition the Workshops", 12, 6, [["stand_with_henry", "march_with_yani"]], [], 8,
  "duo:Generic_Underground_Factories", "has_country_flag = VIT_war_started", FLAMES_DOWN,
  "Every workshop on our side of the mountain now makes one thing: what the front needs." + FLAMES_TT,
  ["INDUSTRY", "STABILITY"])
F("martial_law_on_the_slopes", "Martial Law on the Slopes", 14, 6, [["stand_with_henry", "march_with_yani"]], [], 8,
  "duo:Generic_Arrests", "has_country_flag = VIT_war_started", FLAMES_DOWN + "\nadd_war_support = 0.05",
  "Curfews, checkpoints and courts that sit at night. The villages behind the front stop arguing." + FLAMES_TT,
  ["STABILITY", "WAR_SUPPORT"])
F("volunteers_from_the_city", "Volunteers from the City", 11, 7, [["restore_the_chain_of_command"], ["martial_law_on_the_slopes"]], [], 6,
  "duo:Generic_Morale_Bonus_Focus", "", "add_manpower = 15000\nadd_war_support = 0.05",
  "Young men from all over Sofia take the tram to the end of the line and walk up the mountain to join us.", ["MANPOWER"])
F("the_mountain_artillery", "Guns on the Ridges", 13, 7, [["requisition_the_workshops"]], [], 7,
  "duo:Generic_Artillery_Barrel", "",
  "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }\n"
  "add_tech_bonus = { name = VIT_guns_on_the_ridges bonus = 1.0 uses = 1 category = artillery }",
  "Every ridge of Vitosha looks down on the other side's villages. A gun on each of them settles a lot of arguments.",
  ["INDUSTRY", "RESEARCH"])
F("the_mountain_is_ours", "The Mountain Is Ours", 12, 8, [["volunteers_from_the_city"], ["the_mountain_artillery"]], [], 6,
  "duo:Generic_Memories_of_the_War", "has_country_flag = VIT_war_started\nhas_civil_war = no",
  FLAMES_OUT + f"\nif = {{ limit = {{ {S('Vitosha')} = {{ is_controlled_by = ROOT }} }} set_capital = {{ state = {S('Vitosha')} }} }}" + "\nadd_stability = 0.15\nadd_political_power = 100\nset_country_flag = VIT_war_over\n"
  + ifc("has_country_flag = VIT_henry_side", "news_event = { id = evil_sofia_vit_news.2 hours = 6 }")
  + "\nelse = { news_event = { id = evil_sofia_vit_news.3 hours = 6 } }",
  "The last shots echo across the forest and the mountain is quiet. Vitosha is one district again, and it knows "
  "who won.\\n\\nNeeds the civil war won. Removes what is left of The Mountain in Flames.", ["STABILITY"])

# ================================================================== Henry, the English Way (UK-like)
F("god_save_the_mountain", "God Save the Mountain", 3, 10, [["the_mountain_is_ours"]], [], 7, "duo:Generic_Big_Ben02", HENRY_DEM,
  "add_ideas = VIT_half_english\nadd_country_leader_trait = evil_sofia_half_english",
  "Henry won his war the English way: with patience, nerve and a cup of tea at the right moment. Now Vitosha will "
  "be governed like an English shire, if an English shire had a mountain and an army.\\n\\nOnly for Henry on the "
  "English Way.", ["POLITICAL", "STABILITY"])
F("tea_at_five", "Tea at Five", 1, 11, [["god_save_the_mountain"]], [], 5, "duo:Generic_Tea_Farming", "",
  "add_stability = 0.05\nadd_political_power = 50",
  "Whatever happens at the front, the whole district stops for tea at five. Somehow this calms everyone down.", ["STABILITY"])
F("parliament_in_boyana", "The Parliament in Boyana", 3, 11, [["god_save_the_mountain"]], [], 9, "duo:Generic_Parliament_Box", "",
  "add_political_power = 100\nadd_stability = 0.03",
  "Forty seats in the old church hall in Boyana, a speaker with a wig he made himself and very long debates.",
  ["POLITICAL"])
F("the_home_guard", "The Home Guard", 5, 11, [["god_save_the_mountain"]], [], 8, "duo:focus_generic_home_defense", "",
  "add_ideas = VIT_home_guard\nadd_manpower = 10000",
  "Every man too old or too young for the army gets an armband and a rifle and guards his own street.", ["MANPOWER"])
F("radio_vitosha_calling", "Radio Vitosha Calling", 0, 12, [["tea_at_five"]], [], 6, "duo:Generic_Radio_Broadcast", "",
  "every_neighbor_country = { add_timed_idea = { idea = VIT_radio_vitosha days = 180 } }",
  "This is Radio Vitosha. Every evening, news from the free mountain for every district of Sofia.\\n\\nDemocracy slowly "
  "grows in every neighbour for six months.", ["POLITICAL"])
F("the_mountain_conference", "The Mountain Conference", 2, 12, [["parliament_in_boyana"]], [], 8,
  "duo:focus_generic_little_entente", "is_in_faction = no",
  "create_faction = EVIL_SOFIA_FACTION_MOUNTAIN_ENTENTE\nadd_political_power = 50",
  "Henry invites the free districts of Sofia to a conference at the villa: three days of speeches, two of lunch and "
  "one alliance.\\n\\nCreates the faction The Mountain Entente.", ["POLITICAL"])
F("fighters_over_vitosha", "Fighters over Vitosha", 4, 12, [["parliament_in_boyana"]], [], 8, "duo:Generic_Pilots", "",
  "air_experience = 25\nadd_tech_bonus = { name = VIT_fighters bonus = 1.0 uses = 1 category = air_equipment }",
  "Never in the history of Sofia has so much been owed by so many to so few pilots.", ["AIR_XP", "RESEARCH"])
F("rule_the_reservoirs", "Rule the Reservoirs", 6, 12, [["the_home_guard"]], [], 8, "duo:Generic_Maritime", "",
  "{CLAIMS:PNC}\n{WAR:PNC}",
  "England ruled the waves. Vitosha will rule the Pancharevo lake, which is a start.\\n\\nClaims and war goals on "
  "Pancharevo.", ["ANNEXATION"])
F("guarantees_for_the_small", "Guarantees for the Small", 1, 13, [["radio_vitosha_calling"], ["the_mountain_conference"]], [], 6,
  "duo:focus_generic_treaty", "",
  "every_neighbor_country = {\n\tlimit = { is_in_faction = no NOT = { has_war_with = ROOT } }\n\tROOT = { give_guarantee = PREV }\n}",
  "No small district bordering Vitosha will be swallowed while Henry has anything to say about it.\\n\\nWe guarantee "
  "every neighbour outside a faction.", ["POLITICAL"])
F("invite_the_free_districts", "Invite the Free Districts", 3, 13, [["the_mountain_conference"]], [], 7,
  "duo:Generic_Mutual_Cooperation", "",
  "every_country = {\n\tlimit = { NOT = { tag = ROOT } is_in_faction = no OR = { has_government = democratic is_neighbor_of = ROOT } }\n"
  "\tcountry_event = { id = evil_sofia_vit.7 }\n}",
  "A letter to every democratic district in Sofia and every neighbour of the mountain: join the Mountain Entente.\\n\\n"
  "Each is more likely to join the more democratic it is and the better it thinks of us.", ["POLITICAL"])
F("lend_lease", "Lend to Our Friends", 5, 13, [["fighters_over_vitosha"], ["rule_the_reservoirs"]], [], 6,
  "duo:Generic_Outside_Aid", "",
  "every_other_country = {\n\tlimit = { is_in_faction_with = ROOT }\n\tadd_equipment_to_stockpile = { type = infantry_equipment_1 amount = 500 }\n}",
  "Rifles from the mountain for every friend who needs them. They can pay us back later.\\n\\nEvery member of our "
  "faction gets 500 rifles.", ["INDUSTRY"])
F("fight_on_the_slopes", "We Shall Fight on the Slopes", 2, 14, [["guarantees_for_the_small"], ["invite_the_free_districts"]], [], 9,
  "duo:Generic_Soldier_Aiming", "", "add_ideas = VIT_fight_on_the_slopes",
  "We shall fight in the villas, we shall fight in the forests, we shall fight on the ski runs. We shall never "
  "surrender.", ["WAR_SUPPORT", "ARMY_XP"])
F("dominion_status", "Dominion Status", 5, 14, [["lend_lease"]], [], 8, "duo:Generic_Redraw_Borders", "",
  "{CLAIMS:OVK}\n{WAR:OVK}",
  "Ovcha Kupel lies at the foot of the mountain and would make an excellent dominion.\\n\\nClaims and war goals on Ovcha "
  "Kupel.", ["ANNEXATION"])
F("commonwealth_of_the_mountain", "The Commonwealth of the Mountain", 3, 15, [["fight_on_the_slopes"], ["dominion_status"]], [], 12,
  "duo:focus_generic_bastion_of_democracy", "{HELD:VIT,OVK,PNC}\nis_faction_leader = yes",
  "{COREHELD:VIT:OVK,PNC}\nset_cosmetic_tag = VIT_COMMONWEALTH\nswap_ideas = { remove_idea = VIT_half_english add_idea = VIT_commonwealth }\n"
  "add_research_slot = 1\nnews_event = { id = evil_sofia_vit_news.4 hours = 6 }",
  "From the lake at Pancharevo to the fields of Ovcha Kupel, the mountain and its dominions form one Commonwealth, with "
  "Henry at its head and a faction behind him.\\n\\nNeeds Vitosha, Ovcha Kupel and Pancharevo held and our own faction. "
  "Vitosha becomes the Commonwealth of the Mountain.", ["POLITICAL", "RESEARCH"])
F("finest_hour", "Our Finest Hour", 2, 16, [["commonwealth_of_the_mountain"]], [], 10, "duo:Generic_War_Propaganda02", "",
  "add_ideas = VIT_finest_hour",
  "If the Commonwealth lasts for a thousand years, people will still say: this was its finest hour.", ["WAR_SUPPORT", "STABILITY"])
F("the_sun_never_sets", "The Sun Never Sets on the Mountain", 4, 16, [["commonwealth_of_the_mountain"]], [], 10,
  "duo:Generic_Global_Hegemony", "",
  "every_neighbor_country = {\n\tlimit = { NOT = { is_in_faction_with = ROOT has_government = democratic } }\n"
  "\tROOT = { create_wargoal = { type = annex_everything target = PREV } }\n}",
  "There is always somewhere on the Commonwealth where the sun is shining. Usually it is the top of the mountain.\\n\\n"
  "War goals on every neighbour that is neither our ally nor a democracy.", ["ANNEXATION"])

# ================================================================== Henry, Zevka's Dream (authoritarian)
F("what_zevka_wanted", "What Zevka Wanted", 11, 10, [["the_mountain_is_ours"]], [], 7, "duo:Generic_Family", HENRY_AUT,
  "add_ideas = VIT_grandmas_rules",
  "Zevka always said the mountain needed three things: God, the land and a firm hand. Henry has won his war. Now he "
  "will give the mountain what his grandmother wanted for it.\\n\\nOnly for Henry on Zevka's Dream.", ["POLITICAL", "STABILITY"])
F("bells_of_boyana_church", "The Bells of Boyana Church", 9, 11, [["what_zevka_wanted"]], [], 6, "duo:Generic_Bell_Tolls", "",
  "add_stability = 0.05\nadd_political_power = 50",
  "The little medieval church at Boyana rings its bells again on Sunday, and the whole district goes.", ["STABILITY"])
F("grandmas_table", "Dinner at Seven", 11, 11, [["what_zevka_wanted"]], [], 5, "duo:Generic_Nuclear_Family", "",
  "add_political_power = 75",
  "Zevka's rule was simple: the family eats together at seven, and nobody leaves the table angry. It works for "
  "ministers too.", ["POLITICAL"])
F("the_mountain_militia", "The Mountain Militia", 13, 11, [["what_zevka_wanted"]], [], 8, "duo:Generic_Partisan", "",
  "add_manpower = 15000\narmy_experience = 15",
  "Every village on the slopes raises a company of its own, under its own priest and its own mayor.", ["MANPOWER"])
F("monks_of_dragalevtsi", "The Monks of Dragalevtsi", 8, 12, [["bells_of_boyana_church"]], [], 7, "duo:Generic_Piety", "",
  "add_ideas = VIT_monks_of_dragalevtsi",
  "The monastery above Dragalevtsi has hidden rebels and saints for five hundred years. Now it blesses Henry's "
  "banners.", ["STABILITY", "WAR_SUPPORT"])
F("land_for_the_villages", "Land for the Villages", 10, 12, [["grandmas_table"]], [], 8, "duo:Generic_Land_Reform", "",
  "add_political_power = 50\nadd_manpower = 5000\nadd_stability = 0.03",
  "The fields the rebels took are given back to the families who worked them, as Zevka would have wanted.", ["STABILITY"])
F("the_old_officers", "The Old Officers", 12, 12, [["the_mountain_militia"]], [], 8, "duo:Generic_Imperial_Army", "",
  "add_tech_bonus = { name = VIT_old_officers bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 20",
  "Grey moustaches, old medals and a very clear idea of how a war should be fought.", ["ARMY_XP", "RESEARCH"])
F("bunkers_on_kopitoto", "Bunkers on Kopitoto", 14, 12, [["the_mountain_militia"]], [], 8, "duo:focus_generic_coastal_fort", "",
  "capital_scope = { add_building_construction = { type = bunker level = 2 province = { all_provinces = yes limit_to_border = yes } instant_build = yes } }",
  "Kopitoto looks down on all of Sofia. Concrete on its top makes sure it stays that way.", ["INDUSTRY"])
F("a_crown_in_the_attic", "A Crown in the Attic", 9, 13, [["monks_of_dragalevtsi"], ["land_for_the_villages"]], [], 9,
  "duo:Generic_Crown_Box", "", "add_political_power = 100",
  "Clearing out Zevka's attic, Henry finds a box. In the box is a crown, an old one, and a letter in his grandmother's "
  "hand: for when the mountain is ready.", ["POLITICAL"])
F("regent_of_the_mountain", "Regent of the Mountain", 9, 14, [["a_crown_in_the_attic"]], [], 8, "duo:Generic_Divine_Right", "",
  "add_country_leader_trait = evil_sofia_regent\nadd_stability = 0.05",
  "Henry does not put on the crown. Not yet. He governs as regent, in the crown's name, until the mountain is whole.",
  ["POLITICAL", "STABILITY"])
F("the_lowlands_below", "The Lowlands Below", 13, 13, [["the_old_officers"], ["bunkers_on_kopitoto"]], [], 8,
  "duo:Generic_Revanchism", "", "{CLAIMS:OVK,PNC}\n{WAR:OVK,PNC}",
  "Every village at the foot of the mountain once paid its tithe to the monasteries on its slopes. Zevka never forgot "
  "it.\\n\\nClaims and war goals on Ovcha Kupel and Pancharevo.", ["ANNEXATION"])
F("the_tsars_army", "The Crown's Army", 9, 15, [["regent_of_the_mountain"]], [], 10, "duo:Generic_Ultranationalist_Monarchy", "",
  "add_ideas = VIT_crowns_army",
  "Every soldier of Vitosha now swears to the crown in the attic, whoever wears it one day.", ["ARMY_XP"])
F("march_into_the_valley", "March into the Valley", 13, 14, [["the_lowlands_below"]], [], 9, "duo:Generic_Invasion", "",
  "{CLAIMS:LOZ,TRD}\n{WAR:LOZ,TRD}",
  "Below the lowlands lies the city itself. Lozenets and Triaditsa are the first streets of Sofia that climb toward "
  "the mountain.\\n\\nClaims and war goals on Lozenets and Triaditsa.", ["ANNEXATION"])
F("tsardom_of_the_mountain", "The Tsardom of the Mountain", 11, 16, [["the_tsars_army"], ["march_into_the_valley"]], [], 12,
  "duo:Generic_Imperial_Eagle", "{HELD:VIT,OVK,PNC}",
  "{COREHELD:VIT:OVK,PNC}\nset_cosmetic_tag = VIT_TSARDOM\nadd_country_leader_trait = evil_sofia_tsar_of_the_mountain\n"
  "swap_ideas = { remove_idea = VIT_grandmas_rules add_idea = VIT_zevka_proud }\nadd_research_slot = 1\n"
  "news_event = { id = evil_sofia_vit_news.5 hours = 6 }",
  "In Boyana Church, under frescoes seven hundred years old, the crown from the attic is placed on Henry's head. "
  "Zevka's dream has come true: the Tsardom of the Mountain.\\n\\nNeeds Vitosha, Ovcha Kupel and Pancharevo held. "
  "Vitosha becomes the Tsardom of the Mountain and Henry its tsar.", ["POLITICAL", "RESEARCH"])
F("zevka_would_be_proud", "Zevka Would Be Proud", 10, 17, [["tsardom_of_the_mountain"]], [], 8, "duo:Generic_Angel", "",
  "add_stability = 0.10\nadd_political_power = 150",
  "Henry visits her grave in Boyana every Sunday, with flowers and the news. He is sure she approves.", ["STABILITY"])
F("the_throne_expands", "The Mountain Throne Expands", 12, 17, [["tsardom_of_the_mountain"]], [], 10,
  "duo:Generic_Unchecked_Expansionism", "",
  "every_neighbor_country = {\n\tlimit = { NOT = { is_in_faction_with = ROOT } }\n\tROOT = { create_wargoal = { type = annex_everything target = PREV } }\n}",
  "A tsardom needs subjects. Sofia is full of them.\\n\\nWar goals on every neighbour outside our faction.", ["ANNEXATION"])

# ================================================================== Yani, Red Plovdiv (communist)
F("comrade_yani", "Comrade Yani", 19, 10, [["the_mountain_is_ours"]], [], 7, "duo:Generic_Hammer_Star", YANI_COM,
  "add_ideas = VIT_vitosha_soviet\nadd_political_power = 50",
  "The student from Plovdiv has won. The villa on the hill is a workers' rest home, the guard wears red armbands, "
  "and Yani governs from a desk in the old stables.\\n\\nOnly for Yani on Red Plovdiv.", ["POLITICAL"])
F("the_tobacco_workers", "The Tobacco Workers", 17, 11, [["comrade_yani"]], [], 8, "duo:Generic_Tobacco_Farming", "",
  "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
  "Yani brings the tobacco workers of Plovdiv to the mountain: the best organised, most stubborn workers in Bulgaria.",
  ["INDUSTRY"])
F("the_red_mountain_guard", "The Red Mountain Guard", 19, 11, [["comrade_yani"]], [], 8, "duo:Generic_Socialist_Soldier", "",
  "army_experience = 20\nadd_manpower = 15000",
  "The old guard is gone. The new one learned its trade in the war and its politics in Yani's cafés.", ["ARMY_XP", "MANPOWER"])
F("lectures_in_kapana", "Lectures in Kapana", 21, 11, [["comrade_yani"]], [], 9, "duo:focus_generic_socialist_science", "",
  "add_research_slot = 1",
  "Kapana, the Trap, is Plovdiv's maze of craftsmen's streets. Yani builds a new one on the mountain, full of "
  "workshops and lecture halls.", ["RESEARCH"])
F("the_orchards_of_orehite", "The Orchards of Orehite", 16, 12, [["the_tobacco_workers"]], [], 7, "duo:Generic_Farming", "",
  "add_stability = 0.05\nadd_political_power = 50",
  "The orchards of Orehite belonged to six families. Now they belong to everyone, and the apples are just as good.",
  ["STABILITY"])
F("the_plovdiv_fair", "The Plovdiv Fair", 18, 12, [["the_tobacco_workers"]], [], 8, "duo:Generic_Market_Socialism", "",
  "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
  "Plovdiv has held a great fair every year since the last century. Yani holds one on the mountain: tractors, lathes "
  "and very long speeches.", ["INDUSTRY"])
F("partisans_of_vitosha", "The Partisans of Vitosha", 20, 12, [["the_red_mountain_guard"]], [], 8, "duo:Generic_Female_Partisans", "",
  "add_ideas = VIT_partisans",
  "Every path, cave and hut on the mountain has a partisan who knows it. No enemy army will cross Vitosha in peace.",
  ["ARMY_XP"])
F("comrades_in_the_city", "Comrades in the City", 22, 12, [["lectures_in_kapana"]], [], 6, "duo:Generic_Communist_Propaganda", "",
  "every_neighbor_country = { add_timed_idea = { idea = VIT_comrades_from_vitosha days = 180 } }",
  "Students go down the mountain with leaflets in their satchels.\\n\\nCommunism slowly grows in every neighbour for six "
  "months.", ["POLITICAL"])
F("the_thracian_dream", "The Thracian Dream", 17, 13, [["the_orchards_of_orehite"], ["the_plovdiv_fair"]], [], 8,
  "duo:Generic_Red_Liberation", "", "{CLAIMS:PNC}\n{WAR:PNC}",
  "Plovdiv is the heart of Thrace, and the road to Thrace runs south-east past the lake at Pancharevo.\\n\\nClaims and "
  "war goals on Pancharevo.", ["ANNEXATION"])
F("the_red_army_of_the_mountain", "The Red Army of the Mountain", 20, 13, [["partisans_of_vitosha"]], [], 10,
  "duo:Generic_Army_Focus_Red02", "", "add_ideas = VIT_red_army\narmy_experience = 20",
  "Commissars, red stars and a doctrine written in a café in Simeonovo.", ["ARMY_XP"])
F("the_road_to_plovdiv", "The Road to Plovdiv", 18, 14, [["the_thracian_dream"]], [], 9, "duo:Generic_Train", "",
  "{CLAIMS:ISK}\n{WAR:ISK}",
  "The old road to Plovdiv leaves Sofia through Iskar. Whoever holds it holds the way home.\\n\\nClaims and war goals on "
  "Iskar.", ["ANNEXATION"])
F("five_year_plan_of_the_mountain", "The Mountain Five-Year Plan", 20, 14, [["the_red_army_of_the_mountain"], ["comrades_in_the_city"]], [], 12,
  "duo:Generic_State_Socialism", "",
  "capital_scope = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = { type = arms_factory level = 2 instant_build = yes }\n}",
  "Five years, five targets, and a red banner for every factory that meets them.", ["INDUSTRY"])
F("thracian_commune", "The Thracian Commune", 19, 15, [["the_road_to_plovdiv"], ["five_year_plan_of_the_mountain"]], [], 12,
  "duo:Generic_Socialist_Revolution", "{HELD:VIT,PNC,ISK}",
  "{COREHELD:VIT:PNC,ISK}\nset_cosmetic_tag = VIT_THRACIA\nswap_ideas = { remove_idea = VIT_vitosha_soviet add_idea = VIT_thracian_commune }\n"
  "news_event = { id = evil_sofia_vit_news.6 hours = 6 }",
  "From the top of Vitosha to the road to Plovdiv, one commune: the first step to the red Thrace Yani dreamed of in the "
  "tobacco warehouses.\\n\\nNeeds Vitosha, Pancharevo and Iskar held. Vitosha becomes the Thracian Commune.",
  ["POLITICAL", "ANNEXATION"])
F("all_roads_lead_to_plovdiv", "All Roads Lead to Plovdiv", 18, 16, [["thracian_commune"]], [], 10, "duo:Generic_Internationalism", "",
  "every_neighbor_country = {\n\tlimit = { NOT = { is_in_faction_with = ROOT has_government = communism } }\n"
  "\tROOT = { create_wargoal = { type = annex_everything target = PREV } }\n}",
  "Rome had its roads. Plovdiv had them first.\\n\\nWar goals on every neighbour that is neither our ally nor communist.",
  ["ANNEXATION"])
F("the_red_hill", "The Red Hill", 20, 16, [["thracian_commune"]], [], 10, "duo:Generic_Red_Atomic", "",
  "add_ideas = VIT_red_hill",
  "Yani renames the mountain's highest hut after the tobacco strike of his childhood. The workers climb up to see it "
  "every May Day.", ["RESEARCH", "STABILITY"])

# ================================================================== Yani, the Seven Hills (fascist)
HILLS = [("nebet_tepe", "Nebet Tepe", "LOZ", "Lozenets", 24, 12), ("dzhambaz_tepe", "Dzhambaz Tepe", "TRD", "Triaditsa", 26, 12),
         ("taksim_tepe", "Taksim Tepe", "OVK", "Ovcha Kupel", 28, 12), ("sahat_tepe", "Sahat Tepe", "PNC", "Pancharevo", 30, 12),
         ("bunardzhika", "Bunardzhika", "STU", "Studentski", 25, 13), ("dzhendem_tepe", "Dzhendem Tepe", "KRS", "Krasno Selo", 27, 13),
         ("markovo_tepe", "Markovo Tepe", "MLA", "Mladost", 29, 13)]
F("yanis_march", "Yani's March", 27, 10, [["the_mountain_is_ours"]], [], 7, "duo:Generic_Ultranationalist_Government", YANI_FAS,
  "add_ideas = VIT_black_shirts\nadd_war_support = 0.05",
  "The student from Plovdiv has won, and his black shirts march down the mountain road with torches. Yani speaks of "
  "Philippopolis, the city of Philip of Macedon, and of its seven hills.\\n\\nOnly for Yani on the Black Shirts of "
  "Plovdiv.", ["POLITICAL", "WAR_SUPPORT"])
F("the_legacy_of_philip", "The Legacy of Philip", 25, 11, [["yanis_march"]], [], 8, "duo:Generic_Caesar", "",
  "add_ideas = VIT_legacy_of_philip",
  "Philip of Macedon took a Thracian town and named it after himself. His son conquered the world. Yani has read both "
  "of their biographies twice.", ["ARMY_XP"])
F("seven_hills_seven_districts", "Seven Hills, Seven Districts", 27, 11, [["yanis_march"]], [], 6, "duo:Generic_Chess_Move", "",
  "add_political_power = 75",
  "Plovdiv was built on seven hills. Yani's new Philippopolis will be built on seven districts, one for every hill.\\n\\n"
  "Each of the seven hill focuses claims a district; holding all seven opens New Philippopolis.", ["POLITICAL", "ANNEXATION"])
F("torchlight_on_the_slopes", "Torchlight on the Slopes", 29, 11, [["yanis_march"]], [], 7, "duo:Generic_War_Propaganda03", "",
  "add_ideas = VIT_torchlight",
  "Every Saturday night a column of torches climbs from Simeonovo to Aleko. From the city it looks like a river of "
  "fire running uphill.", ["WAR_SUPPORT", "STABILITY"])
HILL_ICONS = ["duo:Generic_Pawns", "duo:Generic_Invasion2", "duo:Generic_Conquistador", "duo:Generic_Molotov_Cocktail",
              "duo:Generic_Helmet_Knife", "duo:Generic_Urban_Warfare", "duo:Generic_Sniper_Assassin"]
for (hid, hname, htag, hdistrict, hx, hy), hicon in zip(HILLS, HILL_ICONS):
    pre = [["seven_hills_seven_districts"]] if hy == 12 else [[HILLS[[h[0] for h in HILLS].index(hid) - 4][0], HILLS[[h[0] for h in HILLS].index(hid) - 3][0]]]
    F(hid, f"{hname}: {hdistrict}", hx, hy, pre, [], 7, hicon, "",
      "{CLAIMS:%s}\n{WAR:%s}" % (htag, htag),
      f"{hname} is one of the seven hills of Plovdiv. In Yani's new Philippopolis, its name goes to {hdistrict}.\\n\\n"
      f"Claims and war goals on {hdistrict}.", ["ANNEXATION"])
F("the_trimontium_guard", "The Trimontium Guard", 25, 14, [["bunardzhika"]], [], 9, "duo:Generic_Rearmament", "",
  "army_experience = 25\nadd_tech_bonus = { name = VIT_trimontium bonus = 1.0 uses = 1 category = land_doctrine }",
  "The Romans called Plovdiv Trimontium, the city of three hills. Yani's guard takes the name and the doctrine.",
  ["ARMY_XP", "RESEARCH"])
F("new_philippopolis", "New Philippopolis", 27, 14, [["bunardzhika", "dzhendem_tepe", "markovo_tepe"]], [], 12,
  "duo:Generic_Ultranat_Eagle", "{HELD:VIT,LOZ,TRD,OVK,PNC,STU,KRS,MLA}",
  "{COREHELD:VIT:LOZ,TRD,OVK,PNC,STU,KRS,MLA}\nset_cosmetic_tag = VIT_PHILIPPOPOLIS\n"
  "swap_ideas = { remove_idea = VIT_black_shirts add_idea = VIT_philippopolis }\nadd_research_slot = 1\n"
  "news_event = { id = evil_sofia_vit_news.7 hours = 6 }",
  "Seven districts, seven hills, one city: New Philippopolis rises at the foot of Vitosha, and the student from Plovdiv "
  "rules it.\\n\\nNeeds Vitosha and all seven hill districts held (Lozenets, Triaditsa, Ovcha Kupel, Pancharevo, "
  "Studentski, Krasno Selo, Mladost). Vitosha becomes New Philippopolis.", ["POLITICAL", "ANNEXATION"])
F("the_eighth_hill", "The Eighth Hill", 29, 14, [["markovo_tepe"]], [], 10, "duo:Generic_Revanchism02", "",
  "add_ideas = VIT_eighth_hill",
  "Plovdiv has seven hills. Philippopolis has eight: the eighth is Vitosha, and it is the tallest.", ["ARMY_XP", "STABILITY"])
F("philippopolis_rules_sofia", "Philippopolis Rules Sofia", 27, 15, [["new_philippopolis"]], [], 10, "duo:Generic_Checkmate", "",
  "every_neighbor_country = {\n\tlimit = { NOT = { is_in_faction_with = ROOT } }\n\tROOT = { create_wargoal = { type = annex_everything target = PREV } }\n}",
  "Sofia was once a Thracian town too. It can be one again, under Philippopolis.\\n\\nWar goals on every neighbour "
  "outside our faction.", ["ANNEXATION"])

# ================================================================== the Evil Gang (for Henry and for Yani)
GANG_FRIENDS = [("SRD", "Victor Kolev", 34, 2), ("LOZ", "Georgi Yanchovichin", 36, 2), ("KRP", "Stefan Kartunov", 38, 2),
                ("MLA", "Georgi Poryazov", 34, 3), ("TRD", "Alexander Dimitrov", 36, 3), ("OBR", "Anton Zafirov", 38, 3),
                ("LYU", "GrimBoss", 36, 4)]
F("the_group_chat_pings", "The Group Chat Pings", 36, 0, [], [], 5, "duo:Generic_Meeting",
  "has_country_flag = VIT_war_over", "add_political_power = 50",
  "The war on the mountain is over, and the phone has not stopped buzzing. The old group chat, the Evil Gang, wants to "
  "know if Vitosha is still one of them.", ["POLITICAL"])
VICTOR_GANG = "SRD = { exists = yes is_faction_leader = yes has_completed_focus = SRD_call_the_evil_gang }"
F("join_victors_gang", "Join Victor's Gang", 35, 1, [["the_group_chat_pings"]], ["found_the_mountain_gang"], 4,
  "duo:Generic_Coalition_Army", f"is_in_faction = no\n{VICTOR_GANG}",
  "SRD = { country_event = { id = evil_sofia_vit.4 } }",
  "Victor has already brought the Evil Gang back together. Vitosha asks to join.\\n\\nOnly if Sredets leads the Evil "
  "Gang. Victor decides; the better he thinks of us, the likelier he says yes.", ["POLITICAL"])
F("found_the_mountain_gang", "The Gang on the Mountain", 37, 1, [["the_group_chat_pings"]], ["join_victors_gang"], 5,
  "duo:Generic_Party_Bottle", f"is_in_faction = no\nNOT = {{ {VICTOR_GANG} }}",
  "create_faction = EVIL_SOFIA_FACTION_EVIL_GANG\nadd_political_power = 25",
  "Nobody has brought the gang back together yet, so Vitosha will. The first meeting is at the villa, and there is "
  "plenty of food.\\n\\nCreates the faction The Evil Gang with Vitosha at its head. Not possible if Sredets already "
  "leads it.", ["POLITICAL"])
for gtag, gname, gx, gy in GANG_FRIENDS:
    pre = [["found_the_mountain_gang"]] if gy == 2 else ([["vit_invite_SRD", "vit_invite_LOZ"]] if gx == 34 else [["vit_invite_LOZ"]] if gx == 36 and gy == 3 else [["vit_invite_KRP"]] if gy == 3 else [["vit_invite_MLA", "vit_invite_TRD", "vit_invite_OBR"]])
    F(f"vit_invite_{gtag}", f"Invite {gname}", gx, gy, pre, [], 5, f"person:vit_invite_{gtag}", "",
      f"if = {{\n\tlimit = {{ country_exists = {gtag} NOT = {{ has_war_with = {gtag} is_in_faction_with = {gtag} }} {gtag} = {{ is_in_faction = no }} }}\n"
      f"\t{gtag} = {{ country_event = {{ id = evil_sofia_vit.1 }} }}\n}}",
      f"A message in the group chat, addressed to {gname} by name: the gang is meeting on the mountain, and there is a "
      f"seat for him.\\n\\n{gname} is invited to the Evil Gang. The better he thinks of us, the likelier he says yes.",
      ["POLITICAL"])
F("the_gang_rules_the_mountain", "The Gang Rules the Mountain", 36, 5, [["vit_invite_LYU"]], [], 8, "duo:Generic_Hedonism", "",
  "add_ideas = SRD_evil_gang\nevery_other_country = {\n\tlimit = { is_in_faction_with = ROOT }\n\tif = { limit = { NOT = { has_idea = SRD_evil_gang } } add_ideas = SRD_evil_gang }\n}",
  "The gang meets every Friday at the villa, and everyone outside it is a little more nervous on Saturdays.\\n\\nEvery "
  "member of our faction gets the Evil Gang spirit.", ["POLITICAL", "WAR_SUPPORT"])

# ================================================================== industry of the mountain (everyone)
IND = [
    ("the_quarries_of_vitosha", "The Quarries of Vitosha", 45, 0, [], 7, "duo:Generic_Mining",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
     "The granite of Vitosha built half the pavements of Sofia. The quarries open again."),
    ("the_boyana_workshops", "The Workshops of Boyana", 43, 1, [["the_quarries_of_vitosha"]], 10, "duo:Generic_Factory_Planning",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n}",
     "Garages behind the villas become workshops, and the workshops get bigger every month."),
    ("the_arsenal_in_the_rock", "The Arsenal in the Rock", 47, 1, [["the_quarries_of_vitosha"]], 10, "duo:Generic_Barrels",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = arms_factory level = 1 instant_build = yes }\n}",
     "An old quarry tunnel is safe from any shell in Sofia. It makes rifles now."),
    ("the_road_to_aleko", "The Road to Aleko", 42, 2, [["the_boyana_workshops"]], 6, "duo:Generic_Electrification",
     "capital_scope = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }",
     "A proper road up the mountain to the Aleko hut, with electric light all the way."),
    ("knyazhevo_springs", "The Springs of Knyazhevo", 44, 2, [["the_boyana_workshops"]], 7, "duo:Generic_Medicine",
     "add_stability = 0.05\nadd_political_power = 50",
     "The mineral springs of Knyazhevo are bottled and sold all over Sofia. Everyone feels a little healthier, and the "
     "treasury feels a lot healthier."),
    ("arms_from_the_quarries", "Arms from the Quarries", 46, 2, [["the_arsenal_in_the_rock"]], 10, "duo:Generic_Industry02",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 1\n\tadd_building_construction = { type = arms_factory level = 1 instant_build = yes }\n}",
     "The quarry railways carry stone in the morning and shells in the afternoon."),
    ("the_mountain_laboratory", "The Mountain Laboratory", 48, 2, [["the_arsenal_in_the_rock"]], 10, "duo:Generic_Brain_Force_Plus",
     "add_research_slot = 1",
     "Clear air, no distractions and a view of the whole city: the perfect place to think."),
    ("factories_in_the_valley", "Factories in the Valley", 43, 3, [["the_road_to_aleko"], ["knyazhevo_springs"]], 12,
     "duo:Generic_Industrial_Complexes",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = { type = industrial_complex level = 2 instant_build = yes }\n}",
     "Down in the valley, where the road from the mountain meets the city, the big factories go up."),
    ("war_workshops_of_knyazhevo", "The War Workshops of Knyazhevo", 47, 3, [["arms_from_the_quarries"]], 12,
     "duo:Generic_Factory_Complex",
     "capital_scope = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = { type = arms_factory level = 2 instant_build = yes }\n}",
     "Knyazhevo's tram depot builds armoured cars, and its foundry builds what goes on them."),
    ("the_industrial_mountain", "The Industrial Mountain", 45, 4, [["factories_in_the_valley"], ["war_workshops_of_knyazhevo"]], 10,
     "duo:Generic_Industrialization", "add_ideas = VIT_industrial_mountain",
     "Smoke on the slopes and sirens in the valleys: the mountain works."),
]
for fid, name, x, y, pre, w, icon, rew, desc in IND:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc, ["INDUSTRY"] + (["RESEARCH"] if "research" in rew else []))
ARMY = [
    ("the_mountain_army", "The Mountain Army", 54, 0, [], 6, "duo:Generic_Winter_Warfare", "army_experience = 25",
     "The strongest guard in Sofia needs to become an army."),
    ("mountaineers_of_cherni_vrah", "Mountaineers of Cherni Vrah", 51, 1, [["the_mountain_army"]], 7, "duo:Generic_Outpost",
     "add_tech_bonus = { name = VIT_mountaineers bonus = 1.0 uses = 1 category = land_doctrine }",
     "Men who climb Cherni Vrah in winter for fun make very good soldiers."),
    ("rifles_of_the_slopes", "Rifles of the Slopes", 54, 1, [["the_mountain_army"]], 6, "duo:Generic_Crouched_Soldier",
     "add_tech_bonus = { name = VIT_rifles bonus = 1.0 uses = 1 category = infantry_weapons }\n"
     "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 }",
     "Every hunter on the mountain has a rifle. Now every soldier has a better one."),
    ("planes_over_the_peak", "Planes over the Peak", 57, 1, [["the_mountain_army"]], 7, "duo:Generic_Jet_Fighters",
     "air_experience = 25\ncapital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }",
     "A grass strip in the meadows below Aleko, and a few aeroplanes that can just about clear the trees."),
    ("artillery_on_the_ridges", "Artillery on the Ridges", 50, 2, [["mountaineers_of_cherni_vrah"]], 6, "duo:Generic_Bombs",
     "add_tech_bonus = { name = VIT_artillery bonus = 1.0 uses = 1 category = artillery }",
     "A gun on a ridge of Vitosha can reach half of Sofia."),
    ("ski_troops", "Ski Troops", 52, 2, [["mountaineers_of_cherni_vrah"]], 7, "duo:Generic_Scouts", "add_ideas = VIT_ski_troops",
     "In winter the fastest way down the mountain is on skis. The guard learns."),
    ("the_mountain_academy", "The Mountain Academy", 55, 2, [["rifles_of_the_slopes"]], 8, "duo:focus_generic_military_academy",
     "add_tech_bonus = { name = VIT_academy bonus = 1.0 uses = 1 category = land_doctrine }\narmy_experience = 15",
     "An officers' school in an old monastery, with a parade ground cut into the forest."),
    ("fighters_over_the_slopes", "Fighters over the Slopes", 57, 2, [["planes_over_the_peak"]], 7, "duo:Generic_Industry_Planes",
     "add_tech_bonus = { name = VIT_fighters_slopes bonus = 1.0 uses = 1 category = air_equipment }",
     "Better aeroplanes for the meadow airfield, and pilots who have stopped crashing into the trees."),
    ("armoured_cars_on_the_mountain_road", "Armoured Cars on the Mountain Road", 51, 3, [["artillery_on_the_ridges"], ["ski_troops"]], 9,
     "duo:Generic_Refit_Tanks", "add_tech_bonus = { name = VIT_armour bonus = 1.0 uses = 1 category = armor }",
     "Steel plates on lorries, and lorries on the mountain road. It is not much of a tank, but it is a start."),
    ("the_mountain_staff", "The Mountain Staff", 54, 3, [["the_mountain_academy"]], 9, "duo:Generic_Draw_Up_Plans",
     "add_ideas = VIT_mountain_staff\narmy_experience = 20",
     "Maps of every path, every ridge and every village, and officers who know them by heart."),
    ("anti_air_on_kopitoto", "Anti-Air on Kopitoto", 57, 3, [["fighters_over_the_slopes"]], 7, "duo:focus_generic_air_defense2",
     "capital_scope = {\n\tadd_building_construction = { type = anti_air_building level = 2 instant_build = yes }\n\tadd_building_construction = { type = radar_station level = 1 instant_build = yes }\n}",
     "Guns and a radar on the top of Kopitoto: nothing flies over Sofia without the mountain seeing it."),
    ("the_army_of_the_mountain", "The Army of the Mountain", 54, 4, [["armoured_cars_on_the_mountain_road"], ["the_mountain_staff"]], 12,
     "duo:focus_generic_combined_arms", "add_ideas = VIT_army_of_the_mountain",
     "Rangers, skiers, guns on the ridges and armour on the roads: the best mountain army in Sofia."),
]
for fid, name, x, y, pre, w, icon, rew, desc in ARMY:
    F(fid, name, x, y, pre, [], w, icon, "", rew, desc, ["ARMY_XP", "RESEARCH"] if "tech_bonus" in rew else ["ARMY_XP"])

UNLOCK_TOOLTIPS = {
    "the_mountain_splits": "Afterwards choose a side: §YStand with Henry§! (Yani's rebels get 5 states) or §YMarch with Yani§! "
                           "(Henry's loyalists get 10 states).",
    "stand_with_henry": "§YThe civil war begins.§! Henry's preparations join us, Yani's join the rebels. We get §RThe Mountain in "
                        "Flames§! (three steps), which the war focuses take down.",
    "march_with_yani": "§YThe civil war begins.§! Yani becomes our leader. Yani's preparations join us, Henry's join the loyalists. "
                       "We get §RThe Mountain in Flames§! (three steps), which the war focuses take down.",
}

# ================================================================== portraits for person icons
PERSON_ICONS = {
    "a_student_from_plovdiv": ("VIT_yani", "CircleFrame.png", "Book Open.png", 0, dict(fill=(36, 36, 30), front_width=0.38, front_y=1.1)),
    "stand_with_henry": ("VIT", "SunStarFrame.png", "Sword.png", -90, dict(fill=(30, 40, 60), front_width=0.72, front_y=0.95)),
    "march_with_yani": ("VIT_yani", "SpikyFrame.png", "Rifles Crossed.png", 0, dict(fill=(50, 30, 26), front_width=0.46, front_y=1.1)),
}
_GANG_FRAMES = ["metalcircle.png", "RedWheatFrame.png", "SilverStarFrame.png", "SunStarFrame.png", "LeavedFrame.png",
                "SpikyFrame.png", "CircleFrame.png"]
_GANG_HANDS = ["Hands Shaking.png", "Hands Shaking2.png", "Hands Shaking3.png", "Hands Shaking.png", "Hands Shaking3.png",
               "Hands Shaking2.png", "Hands Shaking.png"]
for (gtag, *_), frame, hands in zip(GANG_FRIENDS, _GANG_FRAMES, _GANG_HANDS):
    PERSON_ICONS[f"vit_invite_{gtag}"] = (gtag, frame, hands, 0, dict(fill=(34, 34, 40), front_width=0.44, front_y=0.85))
PERSON_FALLBACK = {k: "goal_ANQ_patriotic_protests" for k in PERSON_ICONS}
PERSON_FALLBACK.update({"stand_with_henry": "Generic_Conservatism", "march_with_yani": "Generic_Revolutionary_Republic",
                        "a_student_from_plovdiv": "Generic_Socialist_Man"})
PHOTO_ICONS, PHOTO_FALLBACK = {}, {}

# ================================================================== spirits
IDEAS = {
    "VIT_english_way_drift": ("The English Way", "Parliaments, tea and polite argument.", "democratic_drift = 0.3",
                              ("Shield Blue.png", "Ballot.png")),
    "VIT_zevkas_drift": ("Zevka's Dream", "God, the land and a firm hand.", "neutrality_drift = 0.3", ("Shield.png", "Crown.png")),
    "VIT_red_plovdiv_drift": ("Red Plovdiv", "Yani's cafés are full every night.", "communism_drift = 0.3",
                              ("Soviet.png", "Hammer and Sickle.png")),
    "VIT_black_shirts_drift": ("The Black Shirts of Plovdiv", "Torches and marching songs in Simeonovo.", "fascism_drift = 0.3",
                               ("Rectangle.png", "Torch.png")),
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
    "VIT_grandmas_rules": ("Grandma's Rules", "Church on Sunday, dinner at seven, nobody leaves the table angry.",
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
FACTIONS = {"EVIL_SOFIA_FACTION_MOUNTAIN_ENTENTE": "The Mountain Entente"}

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
