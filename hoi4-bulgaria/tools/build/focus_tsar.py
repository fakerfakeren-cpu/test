"""The Tsar's Way: Boris III. Diplomacy, proxies and the Bulgarian Auction; one late split (Kingmaker / Hegemon)."""
from focus_core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    wargoal_on_owner, tt, neuilly, F, swap, court, bid, ai_flag, INTEGRATION, transfer_if_allied, \
    F_POL, F_STAB, F_WS, F_IND, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_HIST, F_MILCHAR, F_POLCHAR
from focus_opening import CHANCELLERY_RULES

B = "tsar"
F("bfx_tsar_steps_forward", 17, 5, "The Tsar Steps Forward",
  "Boris stops pretending to be above politics and becomes politics. His weapons are patience, diplomacy and other people's armies. Rules out the Legionary path.",
  "retire_country_leader = yes\nrecruit_character = bfx_BUL_boris_iii\npromote_character = bfx_BUL_boris_iii\nset_country_flag = bfx_boris_rules\n" +
  swap("bfx_partyless_regime", "bfx_tsars_personal_regime") + "\n" + court(palace=15, legion=-10),
  "GFX_focus_bfx_tsar_steps_forward", B, prereq=["bfx_hour_of_decision"], excl=["bfx_fas_legions_march"],
  ai="factor = 10\nmodifier = { factor = 10 has_country_flag = bfx_ai_tsar }\nmodifier = { factor = 0 is_ai = yes has_country_flag = bfx_ai_fascist }",
  filters=(F_POL, F_POLCHAR, F_HIST))

# ---------------- the Court
F("bfx_tsar_muzzle_the_league", 10, 6, "Muzzle the Military League",
  "Two coups in eleven years is two too many. The League's officers are posted to frontier garrisons and old General Zhekov reminds the army whom it serves.",
  swap("bfx_military_league_intrigue", "bfx_army_loyal_to_crown") + "\nrecruit_character = bfx_BUL_nikola_zhekov\n" + court(palace=10, army=-15),
  "GFX_goal_generic_army_doctrines", B, prereq=["bfx_tsar_steps_forward"], filters=(F_STAB, F_MILCHAR))
F("bfx_tsar_heir_to_the_throne", 10, 7, "An Heir for the Throne",
  "16 June 1937: Prince Simeon is born, and 101 guns fire over Sofia. The dynasty has a future, and the Crown a new reason to be cautious.",
  "add_stability = 0.05\n" + court(palace=15), "GFX_focus_bfx_tsar_of_the_bulgarians", B, prereq=["bfx_tsar_muzzle_the_league"],
  available="date > 1937.6.1", filters=(F_STAB, F_HIST))
F("bfx_tsar_propaganda_directorate", 10, 8, "The Directorate of Propaganda",
  "A ministry for newsreels, posters and radio, all of them about the lost provinces.",
  "add_ideas = bfx_royal_propaganda\nrecruit_character = bfx_BUL_dobri_bozhilov\n" + court(palace=5, legion=-5),
  "GFX_goal_generic_propaganda", B, prereq=["bfx_tsar_heir_to_the_throne"], filters=(F_WS, F_POLCHAR))
F("bfx_tsar_the_tsars_men", 10, 9, "The Tsar's Men",
  "Filov the archaeologist, Bozhilov the banker, Kyoseivanov the diplomat: technicians, not politicians, and loyal to one man.",
  "recruit_character = bfx_BUL_bogdan_filov\nadd_political_power = 75\n" + court(palace=10), "GFX_goal_generic_political_pressure", B,
  prereq=["bfx_tsar_propaganda_directorate"], filters=(F_POL, F_POLCHAR))
F("bfx_tsar_royal_arbitration", 10, 10, "The Royal Arbitration",
  "Generals, Legionaries and Macedonians bring their quarrels to the Palace, and the Tsar settles them, slowly, in his own favour.",
  "add_stability = 0.05\n" + court(palace=10, army=-5, legion=-5, imro=-5), "GFX_focus_bfx_tsars_balance", B,
  prereq=["bfx_tsar_the_tsars_men"], filters=(F_STAB,))

# ---------------- the Bulgarian Auction
F("bfx_tsar_receive_the_envoys", 15, 6, "Receive the Envoys",
  "Berlin, London and Moscow all want Bulgaria: its army, its railways, its road to the Straits. Let them bid. Opens the Bulgarian Auction.",
  "set_country_flag = bfx_bidding_open\nunlock_decision_category_tooltip = bfx_auction_category\n" + bid(ger=10, eng=5, sov=5),
  "GFX_focus_bfx_auction", B, prereq=["bfx_tsar_steps_forward"], filters=(F_POL,))
F("bfx_tsar_german_offer", 13, 7, "The German Offer",
  "Arms on credit, the whole tobacco crop bought at a premium, and a promise: Macedonia and Thrace when Yugoslavia and Greece fall.",
  bid(ger=25) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 }", "GFX_goal_generic_military_deal", B,
  prereq=["bfx_tsar_receive_the_envoys"], filters=(F_POL, F_ARMY))
F("bfx_tsar_british_offer", 15, 7, "The British Offer",
  "London remembers 1915, when the Entente offered Bulgaria Eastern Thrace to stay out of the war. It offers again: Edirne, loans and a guarantee.",
  bid(eng=25) + "\nadd_political_power = 50", "GFX_goal_generic_improve_relations", B,
  prereq=["bfx_tsar_receive_the_envoys"], filters=(F_POL,))
F("bfx_tsar_soviet_offer", 17, 7, "The Sobolev Mission",
  "November 1940: Moscow offered Sofia a mutual-assistance pact, Southern Dobruja and an Aegean outlet. Boris said no. Perhaps he was hasty.",
  bid(sov=25) + "\n" + tech("bfx_tsar_soviet_offer", "artillery", 0.5, 1), "GFX_focus_bfx_handshake", B,
  prereq=["bfx_tsar_receive_the_envoys"], filters=(F_POL, F_HIST))
F("bfx_tsar_play_them_off", 15, 8, "Play Them Against Each Other",
  "Every envoy hears what the other two offered, slightly improved. Every offer goes up.",
  bid(ger=10, eng=10, sov=10) + "\nadd_political_power = 50", "GFX_goal_generic_dangerous_deal", B,
  prereq=[["bfx_tsar_german_offer", "bfx_tsar_british_offer", "bfx_tsar_soviet_offer"]], filters=(F_POL,))
F("bfx_tsar_turkish_pact", 14, 9, "The Turkish Non-Aggression Pact",
  "February 1941: Sofia and Ankara promise not to attack each other, which frees the army for the west and south. London approves.",
  "if = { limit = { country_exists = TUR NOT = { has_war_with = TUR } } TUR = { country_event = { id = bfx_dip.1 days = 2 } } }\n" + bid(eng=10),
  "GFX_focus_bfx_handshake", B, prereq=["bfx_tsar_play_them_off"], filters=(F_POL, F_HIST))
F("bfx_tsar_break_the_entente", 16, 9, "Break the Balkan Entente",
  "The Entente was built to contain Bulgaria. Whisper to Belgrade about Athens, to Bucharest about Belgrade, and watch it crack.",
  "every_country = { limit = { OR = { tag = GRE tag = YUG tag = TUR tag = ROM } } add_opinion_modifier = { target = ROOT modifier = bfx_om_balkan_courtship } }\n" + neuilly(0, -15) + "\n" + bid(ger=10),
  "GFX_goal_generic_political_pressure", B, prereq=["bfx_tsar_play_them_off"], filters=(F_POL,))
F("bfx_tsar_auction_closes", 15, 10, "The Auction Closes",
  "The bids are in. The highest bidder's first instalment arrives: German arms, British loans or Soviet guns.",
  ded("""
  set_country_flag = bfx_auction_closed
  if = { limit = { check_variable = { bfx_bid_ger > bfx_bid_eng } check_variable = { bfx_bid_ger > bfx_bid_sov } } set_country_flag = bfx_patron_ger add_equipment_to_stockpile = { type = infantry_equipment amount = 3000 } add_equipment_to_stockpile = { type = artillery_equipment amount = 100 } }
  else_if = { limit = { check_variable = { bfx_bid_eng > bfx_bid_sov } } set_country_flag = bfx_patron_eng """ + civ(2).replace("\n", " ") + """ }
  else = { set_country_flag = bfx_patron_sov army_experience = 30 add_equipment_to_stockpile = { type = artillery_equipment amount = 150 } }
  """) + "\n" + tt("bfx_tt_auction_closes", "The §Yhighest bidder§! becomes our patron: §YBerlin§! sends 3,000 rifles and 100 guns, §YLondon§! builds two civilian factories, §YMoscow§! sends instructors (30 army XP) and 150 guns."),
  "GFX_focus_bfx_auction", B, prereq=["bfx_tsar_turkish_pact", "bfx_tsar_break_the_entente"], filters=(F_POL, F_IND))

# ---------------- proxies: Macedonia
F("bfx_tsar_macedonian_committees", 19, 6, "The Macedonian Committees",
  "IMRO, tolerated, organised and pointed west. Unrest in Vardar Macedonia grows. Requires that IMRO was not crushed.",
  "set_country_flag = bfx_imro_tolerated\nunlock_decision_category_tooltip = bfx_imro_category\nadd_to_variable = { bfx_macedonia_unrest = 15 }\n" +
  tt("bfx_tt_unrest_focus_15", "Unrest in Vardar Macedonia: §R+15§!") + "\n" + court(imro=10),
  "GFX_focus_BUL_support_macedonian_organizations", B, prereq=["bfx_tsar_steps_forward"], available="NOT = { has_country_flag = bfx_imro_crushed }",
  filters=(F_POL,))
F("bfx_tsar_pirin_bases", 19, 7, "Bases in the Pirin",
  "Training camps above Melnik and supply dumps in the monasteries. The komitadji are ready.",
  "add_to_variable = { bfx_macedonia_unrest = 15 }\n" + tt("bfx_tt_unrest_focus_15", "Unrest in Vardar Macedonia: §R+15§!") + "\nadd_manpower = 3000",
  "GFX_focus_AFG_mountain_training", B, prereq=["bfx_tsar_macedonian_committees"], filters=(F_POL, F_MAN))
F("bfx_tsar_ilinden_preparations", 19, 8, "Ilinden Preparations",
  "The day is chosen, the bells are ready, and Ivan Mihaylov's men are in every village from Kumanovo to Ohrid.",
  "add_to_variable = { bfx_macedonia_unrest = 25 }\n" + tt("bfx_tt_unrest_focus_25", "Unrest in Vardar Macedonia: §R+25§!") + "\n" + court(imro=5),
  "GFX_goal_generic_special_forces", B, prereq=["bfx_tsar_pirin_bases"], filters=(F_POL,))
F("bfx_tsar_macedonia_rises", 19, 9, "Macedonia Rises",
  "If Yugoslavia still holds Macedonia and unrest is high enough (70+), the province rises at once. The rising can still be launched later from the decision.",
  "if = { limit = { check_variable = { bfx_macedonia_unrest > 69 } 106 = { is_owned_by = YUG } YUG = { has_civil_war = no } NOT = { has_country_flag = bfx_uprising_active } NOT = { has_country_flag = bfx_macedonia_free } } bfx_start_macedonian_uprising = yes }\n" +
  tt("bfx_tt_macedonia_rises", "If unrest is §Y70+§! and Yugoslavia holds Macedonia: the §YIndependent State of Macedonia§! rises in civil war.") + "\nadd_war_support = 0.05",
  "GFX_focus_BUL_the_fate_of_the_balkans", B, prereq=["bfx_tsar_ilinden_preparations"], filters=(F_POL, F_WS))
F("bfx_tsar_union_with_skopje", 19, 10, "Union with Skopje",
  "Whether Macedonia rose and won, or fell into our lap some other way, it is Bulgarian now. Core on Vardar Macedonia; unlocks Integration.",
  core_if_owned(106) + "\n106 = { add_compliance = 25 }\n" + INTEGRATION, "GFX_goal_generic_national_unity", B,
  prereq=["bfx_tsar_macedonia_rises"], available="owns_state = 106", filters=(F_ANNEX,))

# ---------------- proxies: Dobruja and the Aegean
F("bfx_tsar_lost_provinces_office", 22, 6, "The Lost Provinces Office",
  "A ministry with one job: maps, refugee associations, petitions to Geneva, and a list of everything Bulgaria was promised and did not get.",
  claim_states(77, 184) + "\nadd_war_support = 0.03", "GFX_goal_generic_more_territorial_claims", B,
  prereq=["bfx_tsar_steps_forward"], filters=(F_ANNEX,))
F("bfx_tsar_craiova_talks", 22, 7, "Towards Craiova",
  "In September 1940 Romania returned Southern Dobruja under German pressure. Bulgaria asks early. Berlin's or Moscow's backing makes a yes far likelier; a refusal gives us a war goal.",
  "if = { limit = { NOT = { owns_state = 77 } 77 = { owner = { save_event_target_as = bfx_dobruja_owner } } } event_target:bfx_dobruja_owner = { country_event = { id = bfx_dip.6 days = 2 } } }\n" + bid(ger=5, sov=5),
  "GFX_focus_BUL_free_balkan_states", B, prereq=["bfx_tsar_lost_provinces_office"], filters=(F_ANNEX, F_HIST))
F("bfx_tsar_dobruja_returned", 22, 8, "The Dobrujan Settlers",
  "Refugees from 1913 go home to Silistra and Dobrich. Core on Southern Dobrudja.",
  core_if_owned(77) + "\n77 = { add_compliance = 20 }\nadd_manpower = 8000", "GFX_focus_bfx_bessarabian_bulgars", B,
  prereq=["bfx_tsar_craiova_talks"], available="owns_state = 77", filters=(F_ANNEX, F_MAN))
F("bfx_tsar_thracian_question", 22, 9, "The Thracian Question",
  "Neuilly promised Bulgaria economic access to the Aegean and never delivered. Athens is asked to cede Western Thrace; a refusal gives us a war goal.",
  "if = { limit = { NOT = { owns_state = 184 } 184 = { owner = { save_event_target_as = bfx_ultimatum_target } } } event_target:bfx_ultimatum_target = { country_event = { id = bfx_dip.10 days = 2 } } }",
  "GFX_goal_generic_occupy_states_coastal", B, prereq=["bfx_tsar_dobruja_returned"], filters=(F_ANNEX,))
F("bfx_tsar_aegean_window", 22, 10, "The Aegean Window",
  "Kavala, Xanthi and Alexandroupolis: Bulgaria's window on the Aegean. Core on Western Thrace; unlocks Integration.",
  core_if_owned(184) + "\n184 = { add_compliance = 20 }\n" + dock(1) + "\n" + INTEGRATION, "GFX_goal_generic_construct_naval_dockyard", B,
  prereq=["bfx_tsar_thracian_question"], available="owns_state = 184", filters=(F_ANNEX, F_NAVY))

# ---------------- armed neutrality
F("bfx_tsar_armed_neutrality", 24, 6, "Armed Neutrality",
  "A neutral nobody fears is a corridor. Concrete goes into every border pass.",
  "every_owned_state = { limit = { is_controlled_by = ROOT any_neighbor_state = { NOT = { is_owned_by = ROOT } } } add_building_construction = { type = bunker level = 1 instant_build = yes province = { all_provinces = yes limit_to_border = yes } } }\narmy_experience = 10",
  "GFX_goal_generic_defence", B, prereq=["bfx_tsar_steps_forward"], filters=(F_ARMY,))
F("bfx_tsar_danube_line", 24, 7, "The Danube Line",
  "Concrete along the river from Vidin to Silistra.",
  "every_owned_state = { limit = { is_controlled_by = ROOT any_neighbor_state = { NOT = { is_owned_by = ROOT } } } add_building_construction = { type = bunker level = 1 instant_build = yes province = { all_provinces = yes limit_to_border = yes } } }",
  "GFX_goal_generic_fortify_city", B, prereq=["bfx_tsar_armed_neutrality"], filters=(F_ARMY,), kind="stat")
F("bfx_tsar_mobilisation_plan", 24, 8, "Mobilisation Plan Sofia",
  "Every reservist knows his depot and every depot its train.",
  "add_manpower = 15000\n" + court(army=5), "GFX_goal_generic_position_armies", B, prereq=["bfx_tsar_danube_line"], filters=(F_MAN,))
F("bfx_tsar_fortress_bulgaria", 24, 9, "Fortress Bulgaria",
  "Whoever comes, from whichever side, pays at the border.",
  "add_ideas = bfx_fortress_bulgaria", "GFX_focus_bfx_fortress_bulgaria", B, prereq=["bfx_tsar_mobilisation_plan"], filters=(F_ARMY,))

# ---------------- the crossroads
F("bfx_tsar_crossroads", 17, 11, "The Crossroads of 1941",
  "The auction is closed and the first provinces are home. Now Boris decides what kind of power Bulgaria will be: the Kingmaker who joins the strongest and collects, or the Hegemon who answers to nobody.",
  "add_political_power = 100\n" + court(palace=10), "GFX_focus_bfx_tsars_balance", B,
  prereq=["bfx_tsar_auction_closes", ["bfx_tsar_union_with_skopje", "bfx_tsar_aegean_window"]], filters=(F_POL,))

# ---------------- (A1) The Kingmaker
F("bfx_tsar_sign_with_the_bidder", 13, 12, "Sign with the Highest Bidder",
  "Bulgaria joins its patron's alliance: Berlin, London or Moscow, whoever bid most. Rules out the Hegemon.",
  ded("""
  if = { limit = { has_country_flag = bfx_patron_ger country_exists = GER } GER = { if = { limit = { is_faction_leader = yes } country_event = { id = bfx_dip.8 days = 2 } } else = { give_guarantee = ROOT } } }
  else_if = { limit = { has_country_flag = bfx_patron_eng country_exists = ENG } ENG = { if = { limit = { is_faction_leader = yes } country_event = { id = bfx_dip.8 days = 2 } } else = { give_guarantee = ROOT } } }
  else_if = { limit = { has_country_flag = bfx_patron_sov country_exists = SOV } SOV = { if = { limit = { is_faction_leader = yes } country_event = { id = bfx_dip.8 days = 2 } } else = { give_guarantee = ROOT } } }
  add_ideas = bfx_raindrops_diplomacy
  """) + "\n" + tt("bfx_tt_sign_bidder", "Our §Ypatron§! is asked to admit us to its faction (or, without one, guarantees us)."),
  "GFX_focus_bfx_tsar_raindrops", B, prereq=["bfx_tsar_crossroads"], excl=["bfx_tsar_stands_alone"], available="is_in_faction = no",
  ai=ai_flag("bfx_ai_tsar_kingmaker", 20), filters=(F_POL, F_HIST))
F("bfx_tsar_partition_dividend", 12, 13, "The Partition Dividend",
  "Our allies hand over what they hold of the Bulgarian lands, as the Axis did in April 1941: Macedonia, Thrace, Dobruja, Edirne.",
  transfer_if_allied(106, 184, 731, 77, 341) + "\n" + core_if_owned(106, 184, 77) + "\n" + INTEGRATION, "GFX_focus_BUL_the_fate_of_the_balkans", B,
  prereq=["bfx_tsar_sign_with_the_bidder"], available="OR = { date > 1941.4.1 any_state = { OR = { state = 106 state = 184 state = 731 state = 77 state = 341 } NOT = { is_owned_by = ROOT } controller = { is_in_faction_with = ROOT } } }",
  filters=(F_ANNEX, F_HIST))
F("bfx_tsar_patrons_credit", 14, 13, "The Patron's Credit",
  "Alliance has its privileges: factories built on our patron's money.",
  civ(1) + "\n" + mil(1), "GFX_goal_generic_construct_mil_factory", B, prereq=["bfx_tsar_sign_with_the_bidder"], filters=(F_IND,), kind="stat")
F("bfx_tsar_occupation_corps", 11, 14, "The Occupation Corps",
  "Gendarmes, schoolteachers and priests follow the army into the new provinces.",
  "add_ideas = bfx_occupation_corps\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 10 }",
  "GFX_goal_generic_occupy_states_ongoing_war", B, prereq=["bfx_tsar_partition_dividend"], filters=(F_STAB,))
F("bfx_tsar_western_outlands", 13, 14, "The Western Outlands",
  "Tsaribrod, Bosilegrad, Pirot, Vranje: Bulgarian towns just across the Yugoslav border. Claims on every Yugoslav state that borders us.",
  "every_state = { limit = { OR = { is_core_of = YUG is_core_of = SER } any_neighbor_state = { is_owned_by = ROOT } NOT = { is_owned_by = ROOT } NOT = { is_claimed_by = ROOT } } add_claim_by = ROOT }",
  "GFX_goal_generic_more_territorial_claims", B, prereq=["bfx_tsar_partition_dividend"], filters=(F_ANNEX,))
F("bfx_tsar_bessarabian_bulgars", 15, 14, "The Bulgarians of Bessarabia",
  "Bolgrad and the Budjak have been Bulgarian-speaking since the 1820s. Claims on Bessarabia and Northern Dobruja.",
  claims_on_cores_of("MOL") + "\n" + claim_states(971), "GFX_focus_bfx_bessarabian_bulgars", B,
  prereq=["bfx_tsar_patrons_credit"], filters=(F_ANNEX,))
F("bfx_tsar_no_eastern_front", 11, 15, "Not One Soldier for the Steppe",
  "Boris refused Hitler every time: Bulgarians would not fight Russians. Rules out the eastern crusade.",
  "add_ideas = bfx_no_eastern_front\n" + court(palace=10), "GFX_goal_generic_neutrality_focus", B,
  prereq=["bfx_tsar_occupation_corps"], excl=["bfx_tsar_crusade_east"], ai="factor = 20", filters=(F_STAB, F_HIST))
F("bfx_tsar_crusade_east", 13, 15, "The Crusade in the East",
  "The opposite choice: Bulgarian divisions cross the Danube with the Axis. Claims on the Ukrainian Black Sea coast. Rules out staying out.",
  "add_ideas = bfx_eastern_crusade\nif = { limit = { country_exists = SOV NOT = { has_war_with = SOV } } declare_war_on = { target = SOV type = annex_everything } }\n" +
  "every_state = { limit = { is_core_of = UKR is_coastal = yes NOT = { is_claimed_by = ROOT } } add_claim_by = ROOT }\n" + court(army=10, legion=10),
  "GFX_focus_bfx_crusade_east", B, prereq=["bfx_tsar_western_outlands"], excl=["bfx_tsar_no_eastern_front"],
  available="GER = { has_war_with = SOV } is_in_faction_with = GER", ai="factor = 5", filters=(F_WS, F_ANNEX))
F("bfx_tsar_change_sides_contingency", 15, 15, "The Contingency Plan",
  "September 1944: Bulgaria left the losing side and declared war on its former ally. Prepare that door now. Unlocks the Change Sides decision for when our patron is losing.",
  "set_country_flag = bfx_change_sides_ready\n" + tt("bfx_tt_change_sides", "Unlocks §YChange Sides§! (Bulgarian Auction): when our faction leader is losing, make peace with its enemies, leave the faction, join the other side and turn on the old patron."),
  "GFX_goal_generic_dangerous_deal", B, prereq=["bfx_tsar_bessarabian_bulgars"], filters=(F_POL, F_HIST))
F("bfx_tsar_greater_bulgaria", 12, 16, "Greater Bulgaria",
  "Dobrudja, Macedonia, Thrace: the map in every classroom is now simply a map. Cores where held; the state becomes Greater Bulgaria.",
  core_if_owned(77, 106, 184) + "\nset_cosmetic_tag = bfx_greater_bulgaria\n" + swap("bfx_tsars_personal_regime", "bfx_tsar_unifier"),
  "GFX_focus_bfx_greater_bulgaria", B, prereq=[["bfx_tsar_no_eastern_front", "bfx_tsar_crusade_east"]],
  available="OR = { owns_state = 106 owns_state = 184 }", filters=(F_ANNEX, F_STAB))
F("bfx_tsar_victors_table", 15, 16, "A Seat at the Victors' Table",
  "Whoever wins, Bulgaria will be on that side when the peace is signed. Claims on whatever our patron promised: Thrace and Edirne.",
  claim_states(184, 731, 341) + "\nadd_war_support = 0.05", "GFX_goal_generic_major_alliance", B,
  prereq=["bfx_tsar_change_sides_contingency"], filters=(F_ANNEX, F_POL))
F("bfx_tsar_straits_question", 11, 17, "The Straits Question",
  "Whoever holds Edirne is a day's march from the Bosporus. Claims on Edirne and Istanbul and a war goal on their owner.",
  claim_states(341, 797) + "\n" + wargoal_on_owner(341), "GFX_focus_BUL_supremacy_on_the_bosporus", B,
  prereq=["bfx_tsar_greater_bulgaria"], filters=(F_ANNEX, F_WS))
F("bfx_tsar_san_stefano", 13, 17, "The Map of San Stefano",
  "March 1878, restored. The state becomes San Stefano Bulgaria; every held, pacified state of the 1878 borders gains compliance.",
  "set_cosmetic_tag = bfx_san_stefano_bulgaria\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 15 }\nif = { limit = { owns_state = 731 731 = { compliance > 40 } } add_state_core = 731 }",
  "GFX_focus_bfx_san_stefano", B, prereq=["bfx_tsar_greater_bulgaria"], available="owns_state = 106 owns_state = 184 owns_state = 77",
  filters=(F_ANNEX, F_HIST))
F("bfx_tsar_of_the_bulgarians", 12, 18, "Tsar of All the Bulgarians",
  "Boris has done what Ferdinand failed to do twice. Every Bulgarian lives under the Bulgarian crown.",
  core_if_owned(341) + "\nadd_ideas = bfx_imperial_mandate\nadd_political_power = 150\narmy_experience = 50\n" + court(palace=20),
  "GFX_focus_bfx_tsar_of_the_bulgarians", B, prereq=["bfx_tsar_straits_question", "bfx_tsar_san_stefano"], filters=(F_STAB, F_POL))
F("bfx_tsar_the_kingmaker", 15, 18, "The Kingmaker",
  "Small kingdoms survive by choosing well. Bulgaria has chosen well every time, and has the provinces to prove it.",
  "add_stability = 0.10\nadd_political_power = 100\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 10 }",
  "GFX_focus_bfx_master_of_the_peninsula", B, prereq=["bfx_tsar_victors_table"], filters=(F_STAB,))

# ---------------- (A2) The Balkan Hegemon
F("bfx_tsar_stands_alone", 21, 12, "Bulgaria Stands Alone",
  "No patron in Berlin, London or Moscow. Bulgaria will be the patron and the neighbours its clients. Rules out the Kingmaker.",
  "add_ideas = bfx_balkan_hegemon\n" + court(army=10, palace=5), "GFX_focus_bfx_tsar_stands_alone", B,
  prereq=["bfx_tsar_crossroads"], excl=["bfx_tsar_sign_with_the_bidder"], ai=ai_flag("bfx_ai_tsar_hegemon", 20), filters=(F_POL, F_WS))
F("bfx_tsar_sofia_pact", 19, 13, "The Sofia Pact",
  "A Bulgarian-led alliance of the Balkan revisionists. Founds a faction with Sofia at its head.",
  CHANCELLERY_RULES + "\nif = { limit = { is_in_faction = no } create_faction = bfx_faction_sofia_pact }",
  "GFX_goal_generic_alliance", B, prereq=["bfx_tsar_stands_alone"], available="OR = { is_in_faction = no is_faction_leader = yes }", filters=(F_POL,))
F("bfx_tsar_everyones_money", 21, 13, "Take Everyone's Money",
  "The bidders keep paying in the hope Bulgaria will change its mind. It will not. Arms and factories scale with how much each power bid.",
  ded("""
  if = { limit = { check_variable = { bfx_bid_ger > 39 } } add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 } }
  if = { limit = { check_variable = { bfx_bid_sov > 39 } } add_equipment_to_stockpile = { type = artillery_equipment amount = 100 } }
  if = { limit = { check_variable = { bfx_bid_eng > 39 } } """ + civ(1).replace("\n", " ") + """ }
  """) + "\n" + tt("bfx_tt_everyones_money", "Each power that bid §Y40+§! pays: Berlin 2,000 rifles, Moscow 100 guns, London a civilian factory."),
  "GFX_goal_generic_trade", B, prereq=["bfx_tsar_stands_alone"], filters=(F_IND, F_ARMY))
F("bfx_tsar_albanian_protectorate", 23, 13, "The Albanian Protectorate",
  "King Zog needs a protector who is not Mussolini. Refusal gives us a war goal to make Albania our puppet.",
  "if = { limit = { country_exists = ALB ALB = { is_subject = no } NOT = { has_war_with = ALB } } ALB = { country_event = { id = bfx_dip.7 days = 2 } } }\nelse = { " + claims_on_cores_of("ALB") + " }",
  "GFX_goal_generic_military_sphere", B, prereq=["bfx_tsar_stands_alone"], filters=(F_POL, F_ANNEX))
F("bfx_tsar_revisionist_brothers", 19, 14, "Revisionist Brothers in Budapest",
  "Hungary lost two-thirds of itself at Trianon; Bulgaria lost its coast at Neuilly. Budapest is invited into the Sofia Pact.",
  "if = { limit = { country_exists = HUN } HUN = { add_opinion_modifier = { target = ROOT modifier = bfx_om_revisionist_brothers } } }\nif = { limit = { country_exists = HUN HUN = { is_in_faction = no } is_faction_leader = yes } HUN = { country_event = { id = bfx_dip.5 days = 2 } } }",
  "GFX_goal_generic_improve_relations", B, prereq=["bfx_tsar_sofia_pact"], filters=(F_POL,))
F("bfx_tsar_hegemon_army", 21, 14, "The Hegemon's Army",
  "Twelve divisions, then twenty-four, each trained for a different neighbour.",
  "add_ideas = bfx_hegemon_army\narmy_experience = 25", "GFX_focus_BUL_prussia_of_the_balkans", B, prereq=["bfx_tsar_everyones_money"], filters=(F_ARMY,))
F("bfx_tsar_durres_concession", 23, 14, "The Durrës Concession",
  "An Adriatic port for the Bulgarian navy.", "navy_experience = 20\n" + dock(1), "GFX_goal_generic_construct_naval_dockyard", B,
  prereq=["bfx_tsar_albanian_protectorate"], filters=(F_NAVY,))
F("bfx_tsar_ultimatum_belgrade", 19, 15, "The Ultimatum to Belgrade",
  "Cede Vardar Macedonia, or the army crosses the border. Belgrade has a week.",
  "add_state_claim = 106\nif = { limit = { NOT = { owns_state = 106 } 106 = { owner = { NOT = { is_in_faction_with = ROOT } } } } 106 = { owner = { country_event = { id = bfx_dip.11 days = 2 } } } }",
  "GFX_goal_generic_major_war", B, prereq=["bfx_tsar_revisionist_brothers"], filters=(F_ANNEX, F_WS))
F("bfx_tsar_ultimatum_athens", 21, 15, "The Ultimatum to Athens",
  "Cede Western Thrace and Central Macedonia, or the army marches down the Struma.",
  "add_state_claim = 184\nadd_state_claim = 731\nif = { limit = { NOT = { owns_state = 184 } 184 = { owner = { NOT = { is_in_faction_with = ROOT } } } } 184 = { owner = { country_event = { id = bfx_dip.10 days = 2 } } } }",
  "GFX_goal_generic_territory_or_war", B, prereq=["bfx_tsar_hegemon_army"], filters=(F_ANNEX, F_WS))
F("bfx_tsar_ultimatum_bucharest", 23, 15, "The Ultimatum to Bucharest",
  "Both Dobrujas, now. Romania has a week.",
  "add_state_claim = 77\nadd_state_claim = 971\nif = { limit = { NOT = { owns_state = 77 } 77 = { owner = { NOT = { is_in_faction_with = ROOT } } } } 77 = { owner = { country_event = { id = bfx_dip.6 days = 2 } } } }",
  "GFX_goal_generic_occupy_start_war", B, prereq=["bfx_tsar_durres_concession"], filters=(F_ANNEX, F_WS))
F("bfx_tsar_client_kings", 19, 16, "Client Kings",
  "Defeated neighbours keep their crowns and take their orders from Sofia. Cheaper puppets, cheaper annexations.",
  "add_ideas = bfx_client_kings", "GFX_goal_generic_military_sphere", B, prereq=["bfx_tsar_ultimatum_belgrade"], filters=(F_ANNEX,))
F("bfx_tsar_ultimatum_ankara", 21, 16, "The Ultimatum to Ankara",
  "Edirne and the Chataldzha line. Turkey is told politely, then less politely.",
  "add_state_claim = 341\nif = { limit = { NOT = { owns_state = 341 } 341 = { owner = { NOT = { is_in_faction_with = ROOT } } } } 341 = { owner = { country_event = { id = bfx_dip.12 days = 2 } } } }",
  "GFX_focus_BUL_supremacy_on_the_bosporus", B, prereq=["bfx_tsar_ultimatum_athens"], filters=(F_ANNEX, F_WS))
F("bfx_tsar_black_sea_dominion", 23, 16, "Dominion of the Black Sea",
  "Varna, Burgas and Constanța: three ports, one fleet.", dock(2) + "\nnavy_experience = 25", "GFX_goal_generic_build_navy", B,
  prereq=["bfx_tsar_ultimatum_bucharest"], filters=(F_NAVY,))
F("bfx_tsar_balkan_tsardom", 20, 17, "The Balkan Tsardom",
  "One crown over the peninsula's heart. Cores on the Bulgarian lands where held; the state becomes the Tsardom of the Balkans.",
  core_if_owned(77, 106, 184, 341) + "\nset_cosmetic_tag = bfx_balkan_tsardom\n" + swap("bfx_tsars_personal_regime", "bfx_tsar_unifier") + "\n" + INTEGRATION,
  "GFX_focus_bfx_balkan_tsardom", B, prereq=["bfx_tsar_client_kings", "bfx_tsar_ultimatum_ankara"],
  available="OR = { owns_state = 106 owns_state = 184 owns_state = 341 }", filters=(F_ANNEX, F_STAB))
F("bfx_tsar_master_of_the_peninsula", 21, 18, "Master of the Peninsula",
  "From the Danube to the Aegean, from the Adriatic to the Straits: one sovereign, and he drives his own train.",
  "add_ideas = bfx_imperial_mandate\nadd_stability = 0.10\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 15 }\n" + court(palace=20),
  "GFX_focus_bfx_master_of_the_peninsula", B, prereq=["bfx_tsar_balkan_tsardom", "bfx_tsar_black_sea_dominion"], filters=(F_STAB, F_ANNEX))
