"""Opening (1936 crisis, IMRO, Neuilly, diplomacy): shared by every path."""
from focus_core import *  # noqa: F401,F403
from focus_core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    cores_on_owned_cores_of, wargoal_on_owner, tt, neuilly, F, swap, court, ai_flag, ai_prefer, INTEGRATION, \
    transfer_if_allied, F_POL, F_STAB, F_WS, F_IND, F_RES, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, \
    F_MILCHAR, F_POLCHAR, loc

CHANCELLERY_RULES = "set_rule = { can_create_factions = yes can_join_factions = yes can_guarantee_other_ideologies = yes can_send_volunteers = yes can_only_justify_war_on_threat_country = no }"

# readable requirement tooltips (raw check_variable shows script names and hides the current value)
NEUILLY_IN_FORCE = "custom_trigger_tooltip = { tooltip = bfx_tt_req_neuilly_in_force NOT = { has_country_flag = bfx_neuilly_ended } }"
loc("bfx_tt_req_neuilly_in_force", "The §YShackles of Neuilly§! are still in force", "neuilly")
loc("bfx_tt_req_rearm_50", "§YCovert Rearmament§! is at least §Y50§! (now §Y[?bfx_rearm|0]§!)", "neuilly")
loc("bfx_tt_req_suspicion_50", "§YBalkan Suspicion§! is below §Y50§! (now §Y[?bfx_suspicion|0]§!)", "neuilly")

# =====================================================================================
# OPENING (20)
# =====================================================================================
B = "opening"
F("bfx_tsars_dilemma", 24, 0, "The Tsar's Dilemma",
  "May 1936. The Zveno colonels have been sent home, the parties are banned, and Tsar Boris III rules a kingdom that has lost two wars, a coastline and most of its army. He would rather be driving a locomotive. Instead he must decide what Bulgaria is for.",
  "country_event = bfx.1\nunlock_decision_category_tooltip = bfx_court_category\n" + court(palace=5),
  "GFX_focus_bfx_tsars_dilemma", B, cost=5, filters=(F_POL, F_HIST))

F("bfx_velchev_trial", 19, 1, "The Velchev Trial",
  "Colonel Damyan Velchev, father of the 1934 coup, crossed back into Bulgaria to try it again and was promptly arrested. The court wants a death sentence. The Tsar wants an argument he can win.",
  "country_event = bfx.2", "GFX_focus_BUL_destroy_the_zveno", B, prereq=["bfx_tsars_dilemma"], cost=7, filters=(F_POL, F_STAB))

F("bfx_neuilly_ledger", 22, 1, "The Neuilly Ledger",
  "Article 65: twenty thousand men. Article 81: no air force. Article 83: no submarines. Someone in the War Ministry has kept a second ledger, listing everything the first one forbids, and where it is hidden.",
  "unlock_decision_category_tooltip = bfx_neuilly_category\n" + neuilly(10, 4), "GFX_focus_bfx_neuilly_ledger", B,
  prereq=["bfx_tsars_dilemma"], cost=5, filters=(F_ARMY, F_POL))

F("bfx_eternal_friendship", 26, 1, "Eternal Friendship with Belgrade",
  "Nothing says eternal like a treaty signed in January 1937. Still, a pact with Yugoslavia cracks the Balkan Entente's ring around Sofia, and costs nothing but a few banquets.",
  "if = { limit = { country_exists = YUG } YUG = { add_opinion_modifier = { target = ROOT modifier = bfx_om_eternal_friendship } } add_opinion_modifier = { target = YUG modifier = bfx_om_eternal_friendship } }\n" + neuilly(0, -15),
  "GFX_goal_generic_improve_relations", B, prereq=["bfx_tsars_dilemma"], cost=7, filters=(F_POL,), ai="factor = 15")

F("bfx_macedonian_question", 29, 1, "The Macedonian Question",
  "Ivan Mihaylov's IMRO runs Petrich like a private principality, taxes it like a state and settles disputes with revolvers. Every government in Sofia has had to decide whether IMRO is a weapon or a wound.",
  "add_political_power = 25\nrecruit_character = bfx_BUL_ivan_mihaylov", "GFX_focus_BUL_support_macedonian_organizations", B,
  prereq=["bfx_tsars_dilemma"], cost=5, filters=(F_POL, F_POLCHAR))

F("bfx_kingdom_without_parties", 19, 2, "A Kingdom Without Parties",
  "The parties are banned, the newspapers are polite and the ministers are chosen by the Palace. Boris calls it supra-party government. Everyone else calls it the Tsar's waiting room.",
  "add_ideas = bfx_partyless_regime\n" + court(palace=10), "GFX_focus_BUL_power_to_the_tsar", B,
  prereq=["bfx_velchev_trial"], filters=(F_POL, F_STAB))

F("bfx_war_ministry_cellars", 21, 2, "Cellars of the War Ministry",
  "Rifles declared as agricultural implements, artillery listed as railway equipment, and a basement full of both.",
  "set_country_flag = bfx_arms_fronts_open\n" + tt("bfx_tt_arms_fronts", "Unlocks the §YŠkoda§! and §YRheinmetall§! purchase decisions in §YShackles of Neuilly§!.") + "\n" + neuilly(6, 3),
  "GFX_goal_generic_small_arms", B, prereq=["bfx_neuilly_ledger"], cost=7, filters=(F_ARMY,))

F("bfx_hidden_arsenals", 23, 2, "Hidden Arsenals",
  "Caves in the Rhodopes, monasteries with very large cellars and a railway siding that appears on no map. Weapons stored here do not rust and are not counted.",
  "set_country_flag = bfx_hidden_arsenals\n" + tt("bfx_tt_hidden_arsenals", "Covert Rearmament §Gno longer decays§! each month.") + "\n" + neuilly(5, 2),
  "GFX_goal_generic_defence", B, prereq=["bfx_neuilly_ledger"], cost=7, filters=(F_ARMY,))

F("bfx_kyoseivanov_cabinet", 26, 2, "The Kyoseivanov Cabinet",
  "A career diplomat as Prime Minister: Georgi Kyoseivanov smiles at Belgrade, bows to Athens and negotiates with everyone.",
  "recruit_character = bfx_BUL_georgi_kyoseivanov\nadd_stability = 0.03\n" + neuilly(0, -5), "GFX_goal_generic_neutrality_focus", B,
  prereq=["bfx_eternal_friendship"], filters=(F_POL, F_POLCHAR))

F("bfx_crush_imro", 28, 2, "Crush IMRO",
  "Send the gendarmes into Petrich, close the committees and give Belgrade the heads it keeps asking for. Rules out tolerating IMRO, and with it the Macedonian uprising.",
  swap("bfx_imro_state_within_state", "bfx_imro_crushed") + "\nset_country_flag = bfx_imro_crushed\n" +
  "if = { limit = { country_exists = YUG } YUG = { add_opinion_modifier = { target = ROOT modifier = bfx_om_imro_crackdown } } }\n" +
  court(palace=10, imro=-30) + "\n" + neuilly(0, -10),
  "GFX_focus_BUL_condemn_macedonian_organizations", B, prereq=["bfx_macedonian_question"], excl=["bfx_tolerate_imro"],
  filters=(F_POL, F_STAB), ai="factor = 5\nmodifier = { factor = 3 has_country_flag = bfx_ai_tsar_hegemon }")

F("bfx_tolerate_imro", 30, 2, "Tolerate IMRO",
  "Look the other way in Petrich. Mihaylov's men know every goat path into Vardar Macedonia. Unlocks the IMRO Uprising decisions; rules out crushing IMRO.",
  swap("bfx_imro_state_within_state", "bfx_imro_tolerated") + "\nset_country_flag = bfx_imro_tolerated\nunlock_decision_category_tooltip = bfx_imro_category\n" +
  court(imro=15) + "\n" + neuilly(0, 10),
  "GFX_focus_BUL_support_macedonian_organizations", B, prereq=["bfx_macedonian_question"], excl=["bfx_crush_imro"],
  filters=(F_POL, F_WS), ai="factor = 15")

F("bfx_elections_of_1938", 18, 3, "The Partyless Elections of 1938",
  "Candidates may not belong to parties, which has not stopped any of them from belonging to parties.",
  "country_event = bfx.3", "GFX_focus_generic_election", B, prereq=["bfx_kingdom_without_parties"], filters=(F_POL, F_STAB))

F("bfx_the_tsars_balance", 20, 3, "The Tsar's Balance",
  "Boris rules by playing the generals against the Legionaries, the Macedonians against the generals and everybody against the Communists. He might as well do it deliberately.",
  "add_political_power = 50\n" + court(palace=10) + "\nadd_ideas = bfx_royal_propaganda",
  "GFX_focus_bfx_tsars_balance", B, prereq=["bfx_kingdom_without_parties"], filters=(F_POL, F_STAB))

F("bfx_tear_up_neuilly", 22, 3, "Tear Up Neuilly",
  "Why ask permission? With enough rifles in the cellars, Bulgaria can simply announce that the treaty no longer applies and dare the Entente to march. Needs Covert Rearmament of 50. Rules out the negotiated Salonika route.",
  "bfx_end_neuilly_torn = yes", "GFX_focus_bfx_tear_up_neuilly", B, prereq=["bfx_war_ministry_cellars"], excl=["bfx_salonika_agreement"],
  available=NEUILLY_IN_FORCE + "\ncustom_trigger_tooltip = { tooltip = bfx_tt_req_rearm_50 check_variable = { bfx_rearm > 49 } }", filters=(F_WS, F_ARMY),
  ai="factor = 5\nmodifier = { factor = 4 has_country_flag = bfx_ai_fascist }")

F("bfx_salonika_agreement", 25, 3, "The Salonika Agreement",
  "July 1938, Thessaloniki: the Balkan Entente formally releases Bulgaria from the military clauses of Neuilly in exchange for a promise to behave. Available from June 1938, and only if Balkan Suspicion is below 50: nobody negotiates with a neighbour they fear. Rules out tearing the treaty up.",
  "bfx_end_neuilly_negotiated = yes", "GFX_focus_bfx_salonika_agreement", B, prereq=["bfx_kyoseivanov_cabinet"], excl=["bfx_tear_up_neuilly"],
  available=NEUILLY_IN_FORCE + "\ndate > 1938.6.1\ncustom_trigger_tooltip = { tooltip = bfx_tt_req_suspicion_50 check_variable = { bfx_suspicion < 50 } }",
  filters=(F_POL, F_ARMY, F_HIST), ai="factor = 20")

F("bfx_italian_queen", 27, 3, "The Italian Queen",
  "Boris married Giovanna of Savoy in 1930. Her father is King of Italy, which makes Rome the one great power with a reason to listen.",
  "if = { limit = { country_exists = ITA } ITA = { add_opinion_modifier = { target = ROOT modifier = bfx_om_royal_wedding } } add_opinion_modifier = { target = ITA modifier = bfx_om_royal_wedding } }\n" + court(palace=5),
  "GFX_goal_generic_improve_relations", B, prereq=["bfx_kyoseivanov_cabinet"], cost=7, filters=(F_POL,))

F("bfx_shadow_legions", 29, 3, "The Shadow Parties",
  "Banned is not gone. Agrarians meet in taverns, Communists in cellars, Lukov's Legionaries and Tsankov's National Socialists in gymnasiums. The Legions grow fastest of all.",
  "country_event = bfx.4", "GFX_focus_BUL_oppose_the_royal_dictatorship", B,
  prereq=[["bfx_crush_imro", "bfx_tolerate_imro"]], cost=7, filters=(F_POL,))

F("bfx_royal_tour", 20, 4, "The Royal Tour",
  "The Tsar visits every district by train, driving the engine himself for the last stretch into each station. Nothing does more for the Crown.",
  "add_stability = 0.05\n" + court(palace=10), "GFX_goal_generic_propaganda", B, prereq=["bfx_the_tsars_balance"], cost=7,
  filters=(F_STAB,), kind="stat")

F("bfx_hour_of_decision", 24, 4, "The Hour of Decision",
  "The elections are counted and the shadow parties have shown their hands. Bulgaria picks a master: the Crown, or the Legions. Taking the Legionary path needs Legion influence of at least 40 in the Tsar's Balance.",
  "add_political_power = 50\n" + tt("bfx_tt_hour_of_decision", "Unlocks §YThe Tsar Steps Forward§! and §YThe Legions March§! (mutually exclusive)."),
  "GFX_goal_generic_political_pressure", B, prereq=["bfx_elections_of_1938", "bfx_shadow_legions"], cost=5, filters=(F_POL,), kind="stat")

F("bfx_open_the_chancelleries", 27, 4, "Open the Chancelleries",
  "A small kingdom with no alliances is a corridor. Bulgaria will sign pacts, give and ask guarantees and build alliances like everyone else. Unlocks the Diplomacy decisions and lifts the non-aligned limits on factions, guarantees and volunteers.",
  CHANCELLERY_RULES + "\nadd_ideas = bfx_open_chancelleries\nunlock_decision_category_tooltip = bfx_diplomacy_category\nset_country_flag = bfx_chancelleries_open",
  "GFX_focus_bfx_open_the_chancelleries", B, prereq=["bfx_italian_queen"], filters=(F_POL,), ai="factor = 30")

