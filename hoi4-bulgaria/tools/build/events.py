"""All bfx events. Every option has a visible effect except where marked purely narrative (news)."""
from core import add_file, loc, ded, neuilly

EVENTS = {}  # namespace -> list of event text


def opt(name, effect="", ai=None, trigger=None):
    return dict(name=name, effect=ded(effect) if effect else "", ai=ai, trigger=ded(trigger) if trigger else None)


def E(eid, title, desc, picture, options, kind="country_event", trigger=None, immediate=None, major=False,
      triggered_only=True):
    ns = eid.split(".")[0]
    lines = [f"{kind} = {{", f"\tid = {eid}", f"\ttitle = {eid}.t", f"\tdesc = {eid}.d", f"\tpicture = {picture}"]
    if major:
        lines.append("\tmajor = yes")
    if triggered_only:
        lines.append("\tis_triggered_only = yes")
    if trigger:
        lines.append(f"\ttrigger = {{ {trigger} }}")
    if immediate:
        lines.append("\timmediate = {")
        lines += ["\t\t" + l for l in ded(immediate).split("\n")]
        lines.append("\t}")
    loc(f"{eid}.t", title, "events")
    loc(f"{eid}.d", desc, "events")
    for i, o in enumerate(options):
        key = f"{eid}.{'abcefg'[i]}"
        loc(key, o["name"], "events")
        lines.append("\toption = {")
        lines.append(f"\t\tname = {key}")
        if o["trigger"]:
            lines.append(f"\t\ttrigger = {{ {o['trigger']} }}")
        if o["ai"]:
            lines.append("\t\tai_chance = {")
            lines += ["\t\t\t" + l for l in ded(o["ai"]).split("\n")]
            lines.append("\t\t}")
        if o["effect"]:
            lines += ["\t\t" + l if l.strip() else l for l in o["effect"].split("\n")]
        lines.append("\t}")
    lines.append("}")
    EVENTS.setdefault(ns, []).append("\n".join(lines))


ENTENTE = "OR = { tag = GRE tag = YUG tag = TUR tag = ROM }"

from focus_core import court, momentum

# ---------------------------------------------------------------- opening
E("bfx.1", "The Tsar's Dilemma",
  "Sofia, spring 1936. The Zveno colonels who seized power in 1934 have been eased out; the parties they banned stay banned. Tsar Boris III governs through ministers he chooses and dismisses at will. He is cautious, clever, popular and deeply reluctant. His father lost two wars and a throne. Boris would prefer to lose neither.",
  "GFX_report_event_bul_boris_tour", [
      opt("Rule from the Palace, quietly.", "add_political_power = 75\n" + court(palace=5), "base = 50"),
      opt("Court the officers.", "army_experience = 10\n" + court(army=10, palace=-5), "base = 25"),
      opt("Let the young nationalists organise.", "add_war_support = 0.03\n" + court(legion=10, palace=-5),
          "base = 25\nmodifier = { factor = 4 has_country_flag = bfx_ai_fascist }"),
  ])
E("bfx.2", "The Velchev Trial",
  "Colonel Damyan Velchev, organiser of the 1923 and 1934 coups, was arrested after slipping back into the country. The military court has sentenced him to death. His officers are watching the Palace.",
  "GFX_report_event_bul_officers_burgas", [
      opt("Commute the sentence. Martyrs make bad neighbours.", "add_stability = 0.03\n" + court(army=5), "base = 70"),
      opt("Let the sentence stand.", "add_political_power = 50\nadd_stability = -0.03\n" + court(palace=10, army=-15), "base = 30"),
  ])
E("bfx.3", "The Partyless Elections",
  "Candidates must stand as individuals, without party labels. The Interior Ministry asks how honest the final count should be.",
  "GFX_report_event_bul_making_bricks_for_school", [
      opt("An honest count. More or less.", "add_stability = 0.05\n" + court(palace=5), "base = 30"),
      opt("Count it properly. Our way.", "add_political_power = 100\nadd_stability = -0.05", "base = 40"),
      opt("Make room for the Legionary candidates.", "add_popularity = { ideology = fascism popularity = 0.08 }\n" + court(legion=10),
          "base = 20\nmodifier = { factor = 5 has_country_flag = bfx_ai_fascist }"),
  ])
E("bfx.4", "The Shadow Parties",
  "Agrarians meet in taverns, Communists in tobacco warehouses and the Legionaries of General Lukov in school gymnasiums, in uniform. The police know all the addresses. The Palace decides whom they will not visit this year.",
  "GFX_report_event_bul_partisans_plovdiv", [
      opt("Let the Legions march.", "add_popularity = { ideology = fascism popularity = 0.10 }\n" + court(legion=15, palace=-5),
          "base = 20\nmodifier = { factor = 10 has_country_flag = bfx_ai_fascist }"),
      opt("Hunt the Communists, leave the rest.", "add_popularity = { ideology = communism popularity = -0.05 }\n" + court(army=5), "base = 30"),
      opt("Keep them all in the dark.", "add_stability = 0.03\n" + court(palace=10, legion=-5), "base = 40"),
  ])
E("bfx.10", "The Ledger of Trade",
  "The Finance Ministry has finished its review. Bulgarian trade is either chained to one buyer or spread across many, and the ministers want a decision.",
  "GFX_report_event_bul_italian_equipment", [
      opt("Break free of the clearing account.", "swap_ideas = { remove_idea = bfx_german_clearing add_idea = bfx_diversified_trade }\nadd_stability = -0.05",
          "base = 30", trigger="has_idea = bfx_german_clearing"),
      opt("Bind ourselves tighter to Berlin.", "swap_ideas = { remove_idea = bfx_german_clearing add_idea = bfx_german_clearing_deep }",
          "base = 70", trigger="has_idea = bfx_german_clearing"),
      opt("Open the markets to the world.", "swap_ideas = { remove_idea = bfx_diversified_trade add_idea = bfx_open_markets }",
          "base = 100", trigger="has_idea = bfx_diversified_trade"),
      opt("Balance the books and move on.", "add_political_power = 50", "base = 100",
          trigger="NOT = { has_idea = bfx_german_clearing } NOT = { has_idea = bfx_diversified_trade }"),
  ])

# ---------------------------------------------------------------- Neuilly
E("bfx_neuilly.10", "Notes of Protest",
  "Envoys from Athens, Belgrade, Ankara and Bucharest have delivered identical notes about irregularities in Bulgaria's compliance with Neuilly. (Balkan Suspicion has passed 25.)",
  "GFX_report_event_bul_muraviev_protest", [
      opt("Deny everything, politely.", "add_political_power = -40\n" + neuilly(0, -8), "base = 50"),
      opt("Let them protest.", "add_war_support = 0.03\nevery_country = { limit = { " + ENTENTE + " } add_opinion_modifier = { target = ROOT modifier = bfx_om_balkan_protest } }", "base = 50"),
  ])
GUAR = ded("""
custom_effect_tooltip = bfx_tt_entente_guarantees
hidden_effect = {
	every_country = {
		limit = { OR = { tag = GRE tag = YUG tag = TUR tag = ROM } NOT = { is_in_faction_with = ROOT } }
		save_event_target_as = bfx_guarantor
		every_country = {
			limit = { OR = { tag = GRE tag = YUG tag = TUR tag = ROM } NOT = { tag = PREV } NOT = { is_in_faction_with = ROOT } }
			event_target:bfx_guarantor = { give_guarantee = PREV }
		}
	}
}""")
loc("bfx_tt_entente_guarantees", "§YGreece, Yugoslavia, Turkey§! and §YRomania§! guarantee one another's independence against us.", "neuilly")
E("bfx_neuilly.11", "The Entente Closes Ranks",
  "The Balkan Entente has met in emergency session. Its members now guarantee each other against any Bulgarian adventure. (Balkan Suspicion has passed 50.)",
  "GFX_report_event_baltic_entente", [
      opt("They are afraid of us. Good.", GUAR + "\nadd_war_support = 0.05", "base = 50"),
      opt("Send reassurances to every capital.", GUAR + "\nadd_political_power = -60\n" + neuilly(0, -10), "base = 50"),
  ])
E("bfx_neuilly.12", "The Balkan Embargo",
  "Our neighbours have closed their markets to Bulgarian tobacco and their ports to anything heavier than a crate of roses. (Balkan Suspicion has passed 75.)",
  "GFX_report_event_bul_italian_equipment", [
      opt("Endure it.", "add_timed_idea = { idea = bfx_balkan_embargo days = 365 }", "base = 40"),
      opt("Smuggle everything through Romania.", "add_political_power = -100\nadd_timed_idea = { idea = bfx_balkan_embargo days = 180 }", "base = 60"),
  ])
loc("bfx_threat_petrich", "The Petrich Crisis", "neuilly")
E("bfx_neuilly.13", "Incident at Petrich",
  "A Greek sentry is shot on the border near Petrich, exactly as in 1925, when Greece invaded over a similar shooting. Troops are moving on both sides.",
  "GFX_report_event_bul_troops_macedonia", [
      opt("Back down. Pull the regiments back.", "add_stability = -0.05\n" + neuilly(-20, -40) + "\n" + court(palace=-5, army=-10), "base = 40"),
      opt("Stand firm.", "add_timed_idea = { idea = bfx_border_crisis days = 180 }\narmy_experience = 15\nadd_named_threat = { threat = 2 name = bfx_threat_petrich }\n" + court(army=10, legion=5), "base = 60"),
  ])
E("bfx_neuilly.20", "The Salonika Agreement",
  "In Thessaloniki the Balkan Entente has released Bulgaria from the military clauses of Neuilly, in exchange for a promise of non-aggression.",
  "GFX_report_event_baltic_entente_one", [opt("A reasonable arrangement.", "add_stability = 0.01", "base = 100")])
E("bfx_neuilly.21", "Bulgaria Tears Up Neuilly",
  "Sofia has announced that the Treaty of Neuilly no longer binds it. The Bulgarian minister delivered the note with a smile.",
  "GFX_report_event_bul_military_parade_vidin", [
      opt("Mobilise the border divisions.", "add_war_support = 0.03", "base = 70"),
      opt("Protest, then do nothing.", "add_political_power = 15", "base = 30"),
  ])

# ---------------------------------------------------------------- The Tsar's Balance
E("bfx_court.10", "The League Stirs",
  "Colonels meet at night in the officers' club. The Military League has decided the Tsar needs advice, and is prepared to give it with machine guns. (Army influence has passed 80.)",
  "GFX_report_event_bul_officers_burgas", [
      opt("Give the generals the War Ministry.", "army_experience = 25\nadd_stability = -0.05\n" + court(palace=-10, army=-10), "base = 50"),
      opt("Arrest the ringleaders.", "add_stability = -0.03\n" + court(army=-35, palace=10), "base = 50"),
  ])
E("bfx_court.11", "The Legions March on Sofia",
  "Forty thousand Legionaries in green shirts parade down Tsar Osvoboditel Boulevard with torches. Lukov demands ministries. (Legion influence has passed 80.)",
  "GFX_report_event_bul_partisans_plovdiv", [
      opt("Ban the Legions.", "add_stability = -0.05\nadd_war_support = -0.05\n" + court(legion=-40, palace=5), "base = 40",
          trigger="NOT = { has_completed_focus = bfx_fas_legions_march }"),
      opt("Give Lukov his ministries.", "add_popularity = { ideology = fascism popularity = 0.10 }\n" + court(legion=-10, palace=-15), "base = 60",
          trigger="NOT = { has_completed_focus = bfx_fas_legions_march }"),
      opt("The Legion is the State!", "add_war_support = 0.05\n" + court(legion=-10), "base = 100",
          trigger="has_completed_focus = bfx_fas_legions_march"),
  ])
E("bfx_court.12", "Murder in Sofia",
  "A deputy is shot dead outside the Sobranie at noon. The gunman shouts 'Long live free Macedonia!' and walks away. (IMRO influence has passed 80.)",
  "GFX_report_event_bul_imro_chieftain", [
      opt("Raid the Macedonian cafés.", "add_stability = -0.03\n" + court(imro=-30, palace=5), "base = 60"),
      opt("Let it pass.", "add_stability = -0.06\n" + court(imro=-5), "base = 40"),
  ])
E("bfx_court.13", "The Crown Totters",
  "Ministers resign, newspapers speculate about abdication and the Tsar has stopped sleeping. (Crown influence has fallen below 20.)",
  "GFX_report_event_bul_boris_tour", [
      opt("The Tsar appeals to the nation.", "add_political_power = -100\n" + court(palace=25), "base = 60"),
      opt("Rule through the generals.", "add_stability = -0.05\n" + court(palace=15, army=20), "base = 40"),
  ])
E("bfx_court.14", "The Army Sulks",
  "Unpaid officers, cancelled manoeuvres and a War Ministry nobody visits. (Army influence has fallen below 15.)",
  "GFX_report_event_bulgarian_soldiers", [
      opt("Pay them.", "add_political_power = -75\n" + court(army=20), "base = 60"),
      opt("They will do as they are told.", "army_experience = -15\n" + court(palace=5), "base = 40"),
  ])
E("bfx_court.20", "The Tsar Is Dead",
  "28 August 1943. Tsar Boris III has died, days after a stormy meeting with Hitler. Rumours of poison are everywhere. His son Simeon is six years old. A regency council of Prince Kiril, Professor Filov and General Mihov takes over. In Coburg, an old man reads the telegram twice.",
  "GFX_report_event_bul_boris_death", [
      opt("A Regency Council.", ded("""
      retire_country_leader = yes
      recruit_character = bfx_BUL_bogdan_filov
      promote_character = bfx_BUL_bogdan_filov
      clr_country_flag = bfx_boris_rules
      set_country_flag = bfx_boris_dead
      set_country_flag = bfx_secret_unlocked
      mark_focus_tree_layout_dirty = yes
      add_stability = -0.10
      """) + "\n" + court(palace=-25)),
  ], immediate="set_country_flag = bfx_boris_dead")

# ---------------------------------------------------------------- diplomacy (FROM = Bulgaria)
E("bfx_dip.1", "Bulgaria Proposes a Pact",
  "Sofia proposes a non-aggression pact: neither country will attack the other.",
  "GFX_report_event_baltic_entente_one", [
      opt("Sign the pact.", "diplomatic_relation = { country = FROM relation = non_aggression_pact active = yes }\nFROM = { country_event = { id = bfx_dip.2 days = 1 } }",
          "base = 50\nmodifier = { factor = 2 has_opinion = { target = FROM value > 24 } }\nmodifier = { factor = 0.2 any_owned_state = { is_claimed_by = FROM } }\nmodifier = { factor = 0.5 is_major = yes }"),
      opt("Decline.", "FROM = { country_event = { id = bfx_dip.3 days = 1 } }", "base = 50"),
  ])
E("bfx_dip.2", "Our Proposal Is Accepted",
  "[From.GetName] has accepted Sofia's proposal.", "GFX_report_event_baltic_entente_one",
  [opt("Excellent.", "add_political_power = 15")])
E("bfx_dip.3", "Our Proposal Is Refused",
  "[From.GetName] has turned Sofia down. The Foreign Ministry is writing a very polite reply, and the War Ministry a less polite plan.",
  "GFX_report_event_bul_muraviev_protest", [opt("We will remember this.", "add_war_support = 0.02")])
E("bfx_dip.4", "Bulgaria Asks for a Guarantee",
  "Sofia asks us to guarantee Bulgarian independence.", "GFX_report_event_bul_boris_military", [
      opt("Grant it.", "give_guarantee = FROM\nFROM = { country_event = { id = bfx_dip.2 days = 1 } }",
          "base = 40\nmodifier = { factor = 2 has_opinion = { target = FROM value > 24 } }"),
      opt("Decline.", "FROM = { country_event = { id = bfx_dip.3 days = 1 } }", "base = 60"),
  ])
E("bfx_dip.5", "Invitation from Sofia",
  "Bulgaria invites us to join its alliance.", "GFX_report_event_baltic_entente", [
      opt("Join.", "FROM = { add_to_faction = ROOT }\nFROM = { country_event = { id = bfx_dip.2 days = 1 } }",
          "base = 25\nmodifier = { factor = 3 has_opinion = { target = FROM value > 39 } }\nmodifier = { factor = 0 any_owned_state = { is_claimed_by = FROM } }"),
      opt("Decline.", "FROM = { country_event = { id = bfx_dip.3 days = 1 } }", "base = 60"),
  ])
E("bfx_dip.6", "Bulgaria Demands Southern Dobruja",
  "Sofia's minister asks for the return of the Quadrilateral, taken from Bulgaria in 1913. Berlin is said to support the request.",
  "GFX_report_event_bul_troops_dobrudja", [
      opt("Return the Quadrilateral.", "FROM = { transfer_state = 77 add_state_core = 77 country_event = { id = bfx_dip.2 days = 1 } }",
          "base = 15\nmodifier = { factor = 4 country_exists = GER FROM = { is_in_faction_with = GER } }\nmodifier = { factor = 3 is_in_faction_with = FROM }\nmodifier = { factor = 2 has_war = yes }"),
      opt("Not one furrow.", "FROM = { create_wargoal = { type = take_state_focus target = ROOT generator = { 77 } } country_event = { id = bfx_dip.3 days = 1 } }",
          "base = 70"),
  ])
E("bfx_dip.7", "Bulgaria Offers Protection",
  "Sofia offers to protect Albania: Bulgarian advisers, Bulgarian guarantees and Bulgarian foreign policy. Refusal, it is hinted, would be unwise.",
  "GFX_report_event_albanian_king_zog", [
      opt("Accept Bulgarian protection.", "FROM = { puppet = ROOT }",
          "base = 20\nmodifier = { factor = 3 has_opinion = { target = FROM value > 24 } }"),
      opt("Refuse.", "FROM = { create_wargoal = { type = puppet_wargoal_focus target = ROOT } country_event = { id = bfx_dip.3 days = 1 } }", "base = 80"),
  ])
E("bfx_dip.8", "Bulgaria Asks to Join",
  "The Bulgarian minister has formally requested admission to our alliance. Bulgaria offers its army, the Black Sea coast and a road to the Straits.",
  "GFX_report_event_bul_boris_with_hitler", [
      opt("Welcome them.", "add_to_faction = FROM\nFROM = { country_event = { id = bfx_dip.2 days = 1 } }", "base = 85"),
      opt("Not yet.", "FROM = { country_event = { id = bfx_dip.9 days = 1 } }", "base = 15"),
  ])
E("bfx_dip.9", "Our Request Is Declined",
  "[From.GetName] has declined, politely, to admit Bulgaria to its alliance. Then Bulgaria will lead an alliance of its own.",
  "GFX_report_event_bul_boris_with_hitler", [
      opt("Found our own alliance.", "set_rule = { can_create_factions = yes }\nif = { limit = { is_in_faction = no has_government = fascism } create_faction = bfx_faction_balkan_axis }\nelse_if = { limit = { is_in_faction = no } create_faction = bfx_faction_sofia_pact }\nadd_war_support = 0.03"),
  ])


def ultimatum(eid, title, desc, state, generator, yes, no):
    """Sent to the owner of `state` (FROM = Bulgaria): cede it, or Bulgaria gets a war goal."""
    gen = " ".join(str(g) for g in generator)
    E(eid, title, desc, "GFX_report_event_bul_troops_dobrudja", [
        opt(yes, f"FROM = {{ transfer_state = {state} country_event = {{ id = bfx_dip.2 days = 1 }} }}",
            "base = 10\nmodifier = { factor = 3 has_war = yes }\nmodifier = { factor = 3 is_in_faction = no FROM = { is_in_faction = yes } }\nmodifier = { factor = 2 FROM = { has_army_size = { size > 30 } } NOT = { has_army_size = { size > 20 } } }\nmodifier = { factor = 0 is_major = yes }"),
        opt(no, f"FROM = {{ create_wargoal = {{ type = take_state_focus target = ROOT generator = {{ {gen} }} }} country_event = {{ id = bfx_dip.3 days = 1 }} }}",
            "base = 90"),
    ])


ultimatum("bfx_dip.10", "Bulgaria Demands Western Thrace",
          "Sofia's note is short: Western Thrace was promised economic access to the Aegean at Neuilly and never received it. Cede the province within the week, or Bulgaria will take it.",
          184, (184, 731), "Cede Western Thrace.", "Not one stone. Let them come.")
ultimatum("bfx_dip.11", "Bulgaria Demands Vardar Macedonia",
          "The Bulgarian minister reads the note aloud: Vardar Macedonia, its people Bulgarian by language and church, is to be handed over. The army is already on the border.",
          106, (106,), "Hand over Macedonia.", "Belgrade does not bargain.")
ultimatum("bfx_dip.12", "Bulgaria Demands Edirne",
          "Adrianople, taken by Bulgaria in 1913 and lost the same year. Sofia wants it back, and the Chataldzha lines with it.",
          341, (341,), "Cede Edirne.", "The Republic gives up nothing.")

# ---------------------------------------------------------------- the Legions
E("bfx_fas.1", "The March on Sofia",
  "Legion columns converge on the capital from Plovdiv, Pleven and Ruse. If the Crown is weak (below 50) or the Legions strong (60 or more) the Tsar will appoint General Lukov; otherwise the Palace Guard fights.",
  "GFX_event_bfx_lukov_legion", [
      opt("The Tsar appoints General Lukov.", ded("""
      set_politics = { ruling_party = fascism elections_allowed = no }
      retire_country_leader = yes
      recruit_character = bfx_BUL_hristo_lukov
      promote_character = bfx_BUL_hristo_lukov
      set_country_flag = bfx_chancelleries_open
      """) + "\n" + court(legion=10, palace=-10),
          trigger="OR = { check_variable = { bfx_inf_palace < 50 } check_variable = { bfx_inf_legion > 59 } }"),
      opt("The Palace Guard resists: civil war!", ded("""
      set_politics = { ruling_party = fascism elections_allowed = no }
      retire_country_leader = yes
      recruit_character = bfx_BUL_hristo_lukov
      promote_character = bfx_BUL_hristo_lukov
      set_country_flag = bfx_chancelleries_open
      start_civil_war = { ideology = neutrality size = 0.3 }
      """) + "\n" + court(legion=15, palace=-30),
          trigger="NOT = { OR = { check_variable = { bfx_inf_palace < 50 } check_variable = { bfx_inf_legion > 59 } } }"),
  ])
E("bfx_fas.2", "Shots on Ivan Asen II Street",
  "February 1943: gunmen wait for General Lukov outside his home. This time he survives, wounded, and the Legion wants blood.",
  "GFX_report_event_bul_partisans_plovdiv", [
      opt("Hunt the assassins.", "add_popularity = { ideology = communism popularity = -0.05 }\nadd_stability = -0.02\n" + court(legion=5)),
      opt("A martyr's speech from the hospital bed.", "add_war_support = 0.05"),
  ], immediate="set_country_flag = bfx_lukov_attempt")

E("bfx_fas.10", "The Movement Fractures",
  "Without victories the Legion quarrels: Lukov's men against Tsankov's, the street-fighters against the ministers, and everyone against the Palace. Membership cards are being torn up in Plovdiv.",
  "GFX_report_event_bul_partisans_plovdiv", [
      opt("Find them an enemy.", "add_stability = -0.05\nadd_named_threat = { threat = 2 name = bfx_threat_incident }\n" + momentum(15)),
      opt("Buy peace with posts and pensions.", "add_stability = -0.03\nadd_political_power = -75\n" + momentum(10)),
      opt("Let them quarrel; the Palace is watching.", "add_stability = -0.05\n" + court(legion=-10, palace=10)),
  ])
E("bfx_fas.11", "The Revolution Devours Its Children",
  "The Legion has won too much, too fast. Commissars denounce generals for caution, street-fighters demand ministries, and the Legion's own courts have started trying Legionaries.",
  "GFX_event_bfx_lukov_legion", [
      opt("Purge the cautious generals.", "army_experience = -25\nadd_stability = -0.03\n" + court(army=-15, legion=5) + "\n" + momentum(-30)),
      opt("Unleash them on the enemy.", "add_timed_idea = { idea = bfx_storm_offensive days = 60 }\nadd_stability = -0.05\n" + momentum(-20)),
      opt("Lukov reins them in.", "add_political_power = -100\n" + momentum(-25)),
  ])

# ---------------------------------------------------------------- the Macedonian uprising
E("bfx_imro.1", "Ilinden Again: Macedonia Rises",
  "Church bells ring from Kumanovo to Ohrid. IMRO fighters seize Skopje's post office, Yugoslav garrisons are surrounded in their barracks, and Ivan Mihaylov proclaims the Independent State of Macedonia.",
  "GFX_news_event_bulgarian_partisans", [
      opt("Sofia is with you!", "add_war_support = 0.03", None, "tag = BUL"),
      opt("The Balkans are burning again.", "", None, "NOT = { tag = BUL }"),
  ], kind="news_event", major=True)
E("bfx_imro.10", "Belgrade Lets Macedonia Go",
  "Yugoslavia has given up. Its envoys sign a ceasefire in Kumanovo, and the Independent State of Macedonia stands on its own. In six months, they say, Skopje will decide its future.",
  "GFX_event_bfx_imro_uprising", [opt("Long live free Macedonia!", "add_stability = 0.05\nadd_war_support = 0.05\n" + court(imro=10))])
E("bfx_imro.20", "The Uprising Is Crushed",
  "The last bands have retreated into the Shar mountains. Skopje is Yugoslav again, the gallows are busy and the refugees are crossing into Bulgaria.",
  "GFX_report_event_bul_imro_chieftain", [
      opt("Mourn the fallen.", "add_stability = -0.05\n" + court(imro=-30)),
      opt("Next time.", "add_political_power = -50\n" + court(imro=-10)),
  ])
E("bfx_imro.30", "Skopje Asks for Union",
  "The government of the Independent State of Macedonia has voted, unanimously and with great emotion, to unite with Bulgaria.",
  "GFX_event_bfx_imro_uprising", [
      opt("Unite! One Bulgarian people.", "FROM = { every_owned_state = { add_core_of = ROOT } }\nannex_country = { target = FROM transfer_troops = yes }\nadd_stability = 0.05"),
      opt("Better as a loyal client state.", "puppet = FROM\nadd_political_power = 50"),
  ])

# ---------------------------------------------------------------- the secret path
E("bfx_secret.1", "A Letter from Coburg",
  "A thick envelope in a familiar hand, sealed with the old royal arms. Ferdinand, from exile, writes to the Palace about butterflies, the weather in Franconia and how a real Tsar would have handled Macedonia.",
  "GFX_event_bfx_ferdinand_returns", [
      opt("File it with the others.", ded("""
      add_to_variable = { bfx_coburg_letters = 1 }
      custom_effect_tooltip = bfx_tt_coburg_letter
      if = { limit = { check_variable = { bfx_coburg_letters > 2 } } set_country_flag = bfx_secret_unlocked mark_focus_tree_layout_dirty = yes }
      """)),
  ])
E("bfx_secret.10", "The Return of Ferdinand",
  "A special train from Coburg arrives at Sofia station: Ferdinand I, plumed, decorated and furious with everyone. He reminds the nation that he once nearly took Constantinople. By evening he is Tsar again.",
  "GFX_event_bfx_ferdinand_returns", [
      opt("Long live Tsar Ferdinand!", ded("""
      retire_country_leader = yes
      recruit_character = bfx_BUL_ferdinand_i
      promote_character = bfx_BUL_ferdinand_i
      clr_country_flag = bfx_boris_rules
      add_ideas = bfx_ferdinand_restoration
      unlock_decision_category_tooltip = bfx_tsargrad_category
      """) + "\n" + court(palace=30)),
  ])
E("bfx_secret.11", "Mass in Hagia Sophia",
  "For the first time since 1453 the Divine Liturgy has been sung under the great dome, by a Bulgarian exarch, in the presence of Ferdinand of Saxe-Coburg, now styling himself Basileus of the Romans and Bulgars.",
  "GFX_news_event_tsar_ferdinand_of_bulgaria", [
      opt("Ferdinand has outdone himself.", "", None, "tag = BUL"),
      opt("Is this really happening?", "", None, "NOT = { tag = BUL }"),
  ], kind="news_event", major=True)
E("bfx_secret.12", "The Coronation at Tarnovo",
  "Tsarevets hill is lit with torches and the bells of forty churches ring as Ferdinand is crowned Tsar of Bulgarians and Vlachs.",
  "GFX_event_bfx_ferdinand_returns", [
      opt("Feast for three days.", "add_stability = 0.03\nadd_political_power = -30"),
      opt("Coronation, then the front.", "add_war_support = 0.05\narmy_experience = 10"),
  ])

# ---------------------------------------------------------------- flavour
FLAV = [
    ("bfx_flav.1", "The Rose Harvest at Kazanlak",
     "Before dawn the women of the Valley pick the damask roses while the dew is still on them; it takes three thousand kilos of petals for one of attar.",
     "GFX_report_event_bul_making_bricks_for_school",
     [opt("Sell it all to Paris.", "add_political_power = 40"), opt("Hold the Rose Festival.", "add_stability = 0.03")]),
    ("bfx_flav.2", "Tobacco Strike in Plovdiv",
     "Twenty thousand tobacco workers have downed tools over pay. The warehouses are full and the buyers are waiting.",
     "GFX_report_event_bul_partisans_plovdiv",
     [opt("Meet their demands.", "add_stability = 0.02\nadd_political_power = -25"),
      opt("Send in the Legionaries.", "add_stability = -0.03\n" + court(legion=5))]),
    ("bfx_flav.3", "The Tsar Drives the Train",
     "The Sofia–Varna express arrived nine minutes early today. The driver, in overalls and goggles, was His Majesty Boris III.",
     "GFX_report_event_bul_boris_tour",
     [opt("The people love it.", "add_stability = 0.02\n" + court(palace=3)), opt("Insist on the regular driver.", "add_political_power = 15")]),
    ("bfx_flav.4", "The St Nedelya Anniversary",
     "On 16 April 1925 a bomb in Sofia's St Nedelya Cathedral killed over a hundred and fifty people at a general's funeral. The anniversary divides the city.",
     "GFX_report_event_bul_officers_burgas",
     [opt("A solemn memorial.", "add_war_support = 0.02"),
      opt("Hunt the last conspirators.", "add_popularity = { ideology = communism popularity = -0.03 }")]),
    ("bfx_flav.5", "Pilgrims to Rila",
     "Thousands walk to the Rila Monastery for the feast of St Ivan. The monks offer bread, the abbot a sermon and the library manuscripts nobody has read in four hundred years.",
     "GFX_report_event_bul_prince_simeon",
     [opt("Join the pilgrimage.", "add_stability = 0.03"), opt("Fund the library.", "add_political_power = 20")]),
]
for fid, t, d, pic, opts in FLAV:
    flag = fid.replace(".", "_") + "_done"
    E(fid, t, d, pic, opts, trigger=f"NOT = {{ has_country_flag = {flag} }}", immediate=f"set_country_flag = {flag}")


def generate():
    for ns, evs in EVENTS.items():
        add_file(f"events/{ns}_events.txt", f"add_namespace = {ns}\n\n" + "\n\n".join(evs) + "\n")
