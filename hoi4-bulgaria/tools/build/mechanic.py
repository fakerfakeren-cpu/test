"""Mechanics (v2):
  * Shackles of Neuilly  - suspicion grows every month (faster the more you rearm), rearmament rusts away
  * The Tsar's Balance   - four power blocs (Crown, Army, Legions, IMRO) driving a live modifier, coups and crises
  * The Macedonian Uprising - IMRO raises a real civil war in Yugoslav Macedonia that Bulgaria feeds and later absorbs
  * Diplomacy, compliance-gated Integration, the secret Coburg decisions, cosmetic tags and their colours
"""
from core import add_file, loc, ded, neuilly, civ
from focus_core import court, bid, momentum

THRESHOLDS = [(25, "bfx_neuilly.10", 10), (50, "bfx_neuilly.11", 35), (75, "bfx_neuilly.12", 60), (100, "bfx_neuilly.13", 85)]
COURT_BLOCS = [("palace", "Crown", 50), ("army", "Army", 45), ("legion", "Legions", 20), ("imro", "IMRO", 35)]


def _num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def scripted_effects():
    thr = []
    for t, e, reset in THRESHOLDS:
        thr.append(f"if = {{ limit = {{ check_variable = {{ bfx_suspicion > {t - 0.01} }} NOT = {{ has_country_flag = bfx_susp_{t} }} }} set_country_flag = bfx_susp_{t} country_event = {{ id = {e} days = 1 }} }}")
        thr.append(f"if = {{ limit = {{ check_variable = {{ bfx_suspicion < {reset} }} has_country_flag = bfx_susp_{t} }} clr_country_flag = bfx_susp_{t} }}")
    court_thr = [
        ("army", ">", 79, 64, "bfx_court.10", "bfx_court_army_high"),
        ("legion", ">", 79, 64, "bfx_court.11", "bfx_court_legion_high"),
        ("imro", ">", 79, 64, "bfx_court.12", "bfx_court_imro_high"),
        ("palace", "<", 21, 35, "bfx_court.13", "bfx_court_palace_low"),
        ("army", "<", 16, 30, "bfx_court.14", "bfx_court_army_low"),
    ]
    cthr = []
    for var, op, t, reset, ev, flag in court_thr:
        back = "<" if op == ">" else ">"
        cthr.append(f"if = {{ limit = {{ check_variable = {{ bfx_inf_{var} {op} {t} }} NOT = {{ has_country_flag = {flag} }} }} set_country_flag = {flag} country_event = {{ id = {ev} days = 2 }} }}")
        cthr.append(f"if = {{ limit = {{ check_variable = {{ bfx_inf_{var} {back} {reset} }} has_country_flag = {flag} }} clr_country_flag = {flag} }}")
    s = ded("""
    # ---------------------------------------------------------------- Neuilly
    bfx_neuilly_recalc = {
    	clamp_variable = { var = bfx_rearm min = 0 max = 100 }
    	clamp_variable = { var = bfx_suspicion min = 0 max = 100 }
    	set_variable = { bfx_dm_cons = bfx_rearm }
    	multiply_variable = { bfx_dm_cons = 0.003 }
    	set_variable = { bfx_dm_org = bfx_rearm }
    	multiply_variable = { bfx_dm_org = 0.001 }
    	set_variable = { bfx_dm_train = bfx_rearm }
    	multiply_variable = { bfx_dm_train = -0.0025 }
    	set_variable = { bfx_dm_air = bfx_rearm }
    	multiply_variable = { bfx_dm_air = -0.005 }
    	set_variable = { bfx_dm_dock = bfx_rearm }
    	multiply_variable = { bfx_dm_dock = 0.0025 }
    	set_variable = { bfx_susp_growth = bfx_rearm }
    	divide_variable = { bfx_susp_growth = 25 }
    	add_to_variable = { bfx_susp_growth = 1 }
    	if = { limit = { has_country_flag = bfx_hidden_arsenals } set_variable = { bfx_rearm_decay = 0 } }
    	else = { set_variable = { bfx_rearm_decay = 1 } }
    	force_update_dynamic_modifier = yes
    	if = {
    		limit = { NOT = { has_country_flag = bfx_neuilly_ended } }
    __THR__
    	}
    }

    bfx_end_neuilly_common = {
    	set_country_flag = bfx_neuilly_ended
    	if = { limit = { has_idea = bfx_neuilly_shackles } remove_ideas = bfx_neuilly_shackles }
    	if = { limit = { has_dynamic_modifier = { modifier = bfx_covert_rearmament } } remove_dynamic_modifier = { modifier = bfx_covert_rearmament } }
    	add_ideas = bfx_salonika_freedom
    	set_variable = { bfx_suspicion = 0 }
    }

    bfx_end_neuilly_negotiated = {
    	if = {
    		limit = { NOT = { has_country_flag = bfx_neuilly_ended } }
    		custom_effect_tooltip = bfx_tt_end_negotiated
    		if = { limit = { check_variable = { bfx_rearm > 74 } } army_experience = 30 }
    		else_if = { limit = { check_variable = { bfx_rearm > 39 } } army_experience = 20 }
    		else = { army_experience = 10 }
    		every_country = {
    			limit = { OR = { tag = GRE tag = YUG tag = TUR tag = ROM } }
    			add_opinion_modifier = { target = ROOT modifier = bfx_om_neuilly_honoured }
    			country_event = { id = bfx_neuilly.20 days = 1 }
    		}
    		set_country_flag = bfx_neuilly_negotiated
    		bfx_end_neuilly_common = yes
    	}
    }

    bfx_end_neuilly_torn = {
    	if = {
    		limit = { NOT = { has_country_flag = bfx_neuilly_ended } }
    		custom_effect_tooltip = bfx_tt_end_torn
    		add_war_support = 0.10
    		army_experience = 25
    		add_named_threat = { threat = 3 name = bfx_threat_neuilly_torn }
    		every_country = {
    			limit = { OR = { tag = GRE tag = YUG tag = TUR tag = ROM } }
    			add_opinion_modifier = { target = ROOT modifier = bfx_om_neuilly_torn }
    			country_event = { id = bfx_neuilly.21 days = 1 }
    		}
    		add_timed_idea = { idea = bfx_balkan_embargo days = 180 }
    		set_country_flag = bfx_neuilly_torn
    		bfx_end_neuilly_common = yes
    		country_event = { id = bfx_neuilly.13 days = 3 }
    	}
    }

    # ---------------------------------------------------------------- The Tsar's Balance
    bfx_court_recalc = {
    	clamp_variable = { var = bfx_inf_palace min = 0 max = 100 }
    	clamp_variable = { var = bfx_inf_army min = 0 max = 100 }
    	clamp_variable = { var = bfx_inf_legion min = 0 max = 100 }
    	clamp_variable = { var = bfx_inf_imro min = 0 max = 100 }
    	# Crown: stability (-10%..+10%, minus IMRO violence) and political power (0..+20%)
    	set_variable = { bfx_cb_stab = bfx_inf_palace }
    	subtract_from_variable = { bfx_cb_stab = 50 }
    	multiply_variable = { bfx_cb_stab = 0.002 }
    	set_temp_variable = { bfx_tmp = bfx_inf_imro }
    	multiply_temp_variable = { bfx_tmp = 0.0005 }
    	subtract_from_variable = { bfx_cb_stab = bfx_tmp }
    	set_variable = { bfx_cb_pp = bfx_inf_palace }
    	multiply_variable = { bfx_cb_pp = 0.002 }
    	# Army: organisation (0..+8%) and army experience gain (0..+20%)
    	set_variable = { bfx_cb_org = bfx_inf_army }
    	multiply_variable = { bfx_cb_org = 0.0008 }
    	set_variable = { bfx_cb_xp = bfx_inf_army }
    	multiply_variable = { bfx_cb_xp = 0.002 }
    	# Legions: war support (-5%..+15%) and conscription (0..+10%)
    	set_variable = { bfx_cb_ws = bfx_inf_legion }
    	subtract_from_variable = { bfx_cb_ws = 25 }
    	multiply_variable = { bfx_cb_ws = 0.002 }
    	set_variable = { bfx_cb_cons = bfx_inf_legion }
    	multiply_variable = { bfx_cb_cons = 0.001 }
    	# IMRO: faster war justification (0..-30%)
    	set_variable = { bfx_cb_justify = bfx_inf_imro }
    	multiply_variable = { bfx_cb_justify = -0.003 }
    	force_update_dynamic_modifier = yes
    __CTHR__
    }

    bfx_startup = {
    	set_variable = { bfx_rearm = 0 }
    	set_variable = { bfx_suspicion = 15 }
    	set_variable = { bfx_tsargrad_fervour = 0 }
    	set_variable = { bfx_macedonia_unrest = 0 }
    	set_variable = { bfx_coburg_letters = 0 }
    	set_variable = { bfx_uprising_months = 0 }
    	set_variable = { bfx_inf_palace = 50 }
    	set_variable = { bfx_inf_army = 45 }
    	set_variable = { bfx_inf_legion = 20 }
    	set_variable = { bfx_inf_imro = 35 }
    	set_variable = { bfx_bid_ger = 15 }
    	set_variable = { bfx_bid_eng = 10 }
    	set_variable = { bfx_bid_sov = 5 }
    	set_variable = { bfx_momentum = 0 }
    	add_ideas = { bfx_neuilly_shackles bfx_imro_state_within_state bfx_military_league_intrigue bfx_tobacco_monoculture }
    	add_dynamic_modifier = { modifier = bfx_covert_rearmament }
    	add_dynamic_modifier = { modifier = bfx_court_balance }
    	bfx_neuilly_recalc = yes
    	bfx_court_recalc = yes
    	if = {
    		limit = { is_ai = yes }
    		random_list = {
    			72 = { set_country_flag = bfx_ai_tsar random_list = { 70 = { set_country_flag = bfx_ai_tsar_kingmaker } 30 = { set_country_flag = bfx_ai_tsar_hegemon } } }
    			28 = { set_country_flag = bfx_ai_fascist random_list = { 60 = { set_country_flag = bfx_ai_fascist_axis } 40 = { set_country_flag = bfx_ai_fascist_imperium } } }
    		}
    		random_list = {
    			30 = { set_country_flag = bfx_ai_secret random_list = { 50 = { set_country_flag = bfx_ai_secret_empire } 50 = { set_country_flag = bfx_ai_secret_byz } } }
    			70 = { }
    		}
    	}
    }

    bfx_monthly = {
    	# Neuilly: suspicion grows by 1 + rearmament/25 per month; rearmament rusts by 1 (0 with Hidden Arsenals)
    	if = {
    		limit = { NOT = { has_country_flag = bfx_neuilly_ended } }
    		add_to_variable = { bfx_suspicion = bfx_susp_growth }
    		subtract_from_variable = { bfx_rearm = bfx_rearm_decay }
    		bfx_neuilly_recalc = yes
    	}
    	# The Tsar's Balance: monthly drift
    	subtract_from_variable = { bfx_inf_palace = 1 }
    	if = { limit = { has_stability > 0.6 } add_to_variable = { bfx_inf_palace = 1 } }
    	if = { limit = { OR = { has_war = yes check_variable = { bfx_rearm > 50 } } } add_to_variable = { bfx_inf_army = 1 } }
    	if = { limit = { has_war_support > 0.5 } add_to_variable = { bfx_inf_legion = 1 } }
    	if = { limit = { fascism > 0.15 } add_to_variable = { bfx_inf_legion = 1 } }
    	if = { limit = { has_country_flag = bfx_boris_rules } subtract_from_variable = { bfx_inf_legion = 1 } }
    	if = { limit = { has_country_flag = bfx_imro_tolerated } add_to_variable = { bfx_inf_imro = 1 } }
    	if = { limit = { has_country_flag = bfx_imro_crushed } subtract_from_variable = { bfx_inf_imro = 2 } }
    	bfx_court_recalc = yes
    	# The Bulgarian Auction: interest fades while the auction is open
    	if = {
    		limit = { has_country_flag = bfx_bidding_open NOT = { has_country_flag = bfx_auction_closed } }
    		subtract_from_variable = { bfx_bid_ger = 1 }
    		subtract_from_variable = { bfx_bid_eng = 1 }
    		subtract_from_variable = { bfx_bid_sov = 1 }
    		bfx_bids_recalc = yes
    	}
    	# Revolutionary Momentum: +3 a month at war (+1 more on the crusade against the USSR), -3 at peace
    	if = {
    		limit = { has_country_flag = bfx_momentum_active }
    		if = {
    			limit = { has_war = yes }
    			add_to_variable = { bfx_momentum = 3 }
    			if = { limit = { has_country_flag = bfx_crusade_declared has_war_with = SOV } add_to_variable = { bfx_momentum = 1 } }
    		}
    		else = { subtract_from_variable = { bfx_momentum = 3 } }
    		bfx_momentum_recalc = yes
    	}
    	# The death of Tsar Boris (historically 28 August 1943)
    	if = {
    		limit = { has_country_flag = bfx_boris_rules date > 1943.8.1 NOT = { has_country_flag = bfx_boris_dead } }
    		random_list = { 25 = { country_event = bfx_court.20 } 75 = { } }
    	}
    	# Letters from Coburg (the secret path)
    	if = {
    		limit = { date > 1937.1.1 check_variable = { bfx_coburg_letters < 3 } NOT = { has_country_flag = bfx_secret_unlocked } NOT = { has_completed_focus = bfx_fas_legions_march } }
    		random_list = { 7 = { country_event = bfx_secret.1 } 93 = { } }
    	}
    	# Lukov's fate (historically assassinated 13 February 1943)
    	if = {
    		limit = { has_completed_focus = bfx_fas_legions_march date > 1943.2.1 NOT = { has_country_flag = bfx_lukov_attempt } }
    		random_list = { 20 = { country_event = bfx_fas.2 } 80 = { } }
    	}
    	# The Macedonian uprising
    	if = { limit = { has_country_flag = bfx_uprising_active } bfx_uprising_monthly = yes }
    	if = {
    		limit = { has_country_flag = bfx_macedonia_free NOT = { has_country_flag = bfx_macedonia_union_asked } }
    		add_to_variable = { bfx_uprising_months = 1 }
    		if = {
    			limit = { check_variable = { bfx_uprising_months > 5 } }
    			set_country_flag = bfx_macedonia_union_asked
    			every_country = { limit = { has_country_flag = bfx_imro_rebel_state } ROOT = { country_event = { id = bfx_imro.30 days = 1 } } }
    		}
    	}
    	# Flavour
    	random_list = {
    		90 = { }
    		2 = { country_event = bfx_flav.1 }
    		2 = { country_event = bfx_flav.2 }
    		2 = { country_event = bfx_flav.3 }
    		2 = { country_event = bfx_flav.4 }
    		2 = { country_event = bfx_flav.5 }
    	}
    }

    # ---------------------------------------------------------------- the Bulgarian Auction (Tsar's Way)
    bfx_bids_recalc = {
    	clamp_variable = { var = bfx_bid_ger min = 0 max = 100 }
    	clamp_variable = { var = bfx_bid_eng min = 0 max = 100 }
    	clamp_variable = { var = bfx_bid_sov min = 0 max = 100 }
    }

    # ---------------------------------------------------------------- Revolutionary Momentum (Legionary Revolution)
    bfx_momentum_recalc = {
    	clamp_variable = { var = bfx_momentum min = 0 max = 100 }
    	# attack 0..+10%, war support -6%..+14%, conscription 0..+8%, political power -9%..+21%
    	set_variable = { bfx_mm_attack = bfx_momentum }
    	multiply_variable = { bfx_mm_attack = 0.001 }
    	set_variable = { bfx_mm_ws = bfx_momentum }
    	subtract_from_variable = { bfx_mm_ws = 30 }
    	multiply_variable = { bfx_mm_ws = 0.002 }
    	set_variable = { bfx_mm_cons = bfx_momentum }
    	multiply_variable = { bfx_mm_cons = 0.0008 }
    	set_variable = { bfx_mm_pp = bfx_momentum }
    	subtract_from_variable = { bfx_mm_pp = 30 }
    	multiply_variable = { bfx_mm_pp = 0.003 }
    	force_update_dynamic_modifier = yes
    	if = { limit = { check_variable = { bfx_momentum < 15 } NOT = { has_country_flag = bfx_momentum_low } } set_country_flag = bfx_momentum_low country_event = { id = bfx_fas.10 days = 2 } }
    	if = { limit = { check_variable = { bfx_momentum > 25 } has_country_flag = bfx_momentum_low } clr_country_flag = bfx_momentum_low }
    	if = { limit = { check_variable = { bfx_momentum > 89 } NOT = { has_country_flag = bfx_momentum_high } } set_country_flag = bfx_momentum_high country_event = { id = bfx_fas.11 days = 2 } }
    	if = { limit = { check_variable = { bfx_momentum < 75 } has_country_flag = bfx_momentum_high } clr_country_flag = bfx_momentum_high }
    }

    # ---------------------------------------------------------------- the Macedonian uprising
    bfx_start_macedonian_uprising = {
    	106 = { owner = { save_event_target_as = bfx_uprising_target } }
    	event_target:bfx_uprising_target = {
    		if = { limit = { has_government = fascism } start_civil_war = { ideology = neutrality size = 0.25 states = { 106 } } }
    		else = { start_civil_war = { ideology = fascism size = 0.25 states = { 106 } } }
    	}
    	106 = {
    		owner = {
    			set_country_flag = bfx_imro_rebel_state
    			set_cosmetic_tag = bfx_independent_macedonia
    			add_ideas = bfx_imro_fervour
    			add_manpower = 15000
    			add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }
    			# a civil-war country cannot recruit predefined characters, so Mihaylov is created inside it
    			if = { limit = { has_government = fascism } create_country_leader = { name = "Ivan Mihaylov" desc = bfx_mac_mihaylov_desc picture = "gfx/leaders/BUL/bfx_ivan_mihaylov.dds" expire = "1965.1.1" ideology = fascism_ideology traits = { bfx_trait_imro_vozhd } } }
    			else = { create_country_leader = { name = "Ivan Mihaylov" desc = bfx_mac_mihaylov_desc picture = "gfx/leaders/BUL/bfx_ivan_mihaylov.dds" expire = "1965.1.1" ideology = despotism traits = { bfx_trait_imro_vozhd } } }
    		}
    	}
    	# Mihaylov leaves Sofia to lead the rising
    	if = { limit = { has_character = bfx_BUL_ivan_mihaylov } retire_character = bfx_BUL_ivan_mihaylov }
    	set_country_flag = bfx_uprising_active
    	set_variable = { bfx_uprising_months = 0 }
    	set_variable = { bfx_macedonia_unrest = 0 }
    	news_event = { id = bfx_imro.1 days = 1 }
    }

    bfx_uprising_monthly = {
    	add_to_variable = { bfx_uprising_months = 1 }
    	if = {
    		limit = { NOT = { any_country = { has_country_flag = bfx_imro_rebel_state } } }
    		clr_country_flag = bfx_uprising_active
    		set_country_flag = bfx_uprising_crushed
    		country_event = { id = bfx_imro.20 days = 1 }
    	}
    	else_if = {
    		limit = {
    			OR = {
    				check_variable = { bfx_uprising_months > 7 }
    				YUG = { surrender_progress > 0.2 }
    				YUG = { has_capitulated = yes }
    			}
    		}
    		every_country = {
    			limit = { has_country_flag = bfx_imro_rebel_state }
    			white_peace = { tag = YUG }
    		}
    		clr_country_flag = bfx_uprising_active
    		set_country_flag = bfx_macedonia_free
    		set_variable = { bfx_uprising_months = 0 }
    		country_event = { id = bfx_imro.10 days = 1 }
    	}
    }
    """).replace("__THR__", "\n\t\t".join(thr)).replace("__CTHR__", "\n\t".join(cthr))
    add_file("common/scripted_effects/bfx_scripted_effects.txt", s + "\n")
    for k, v in {
        "bfx_tt_end_negotiated": "§GThe Shackles of Neuilly are lifted by agreement§!: penalties removed, rearmament converted into army experience, the Balkan Entente is pleased.",
        "bfx_tt_end_torn": "§RThe Shackles of Neuilly are torn up§!: penalties removed, but the Balkan Entente embargoes us and a border crisis follows.",
        "bfx_threat_neuilly_torn": "Bulgaria tears up Neuilly",
    }.items():
        loc(k, v, "neuilly")


def dynamic_modifiers():
    add_file("common/dynamic_modifiers/bfx_dynamic_modifiers.txt", ded("""
    bfx_covert_rearmament = {
    	icon = GFX_idea_bfx_covert_rearmament
    	enable = { always = yes }
    	remove_trigger = { has_country_flag = bfx_neuilly_ended }
    	conscription_factor = bfx_dm_cons
    	army_org_factor = bfx_dm_org
    	training_time_army_factor = bfx_dm_train
    	air_accidents_factor = bfx_dm_air
    	production_speed_dockyard_factor = bfx_dm_dock
    }

    bfx_court_balance = {
    	icon = GFX_idea_bfx_court_balance
    	enable = { always = yes }
    	stability_factor = bfx_cb_stab
    	political_power_factor = bfx_cb_pp
    	army_org_factor = bfx_cb_org
    	experience_gain_army_factor = bfx_cb_xp
    	war_support_factor = bfx_cb_ws
    	conscription_factor = bfx_cb_cons
    	justify_war_goal_time = bfx_cb_justify
    }

    bfx_legion_momentum = {
    	icon = GFX_idea_bfx_momentum
    	enable = { always = yes }
    	remove_trigger = { NOT = { has_country_flag = bfx_momentum_active } }
    	army_attack_factor = bfx_mm_attack
    	war_support_factor = bfx_mm_ws
    	conscription_factor = bfx_mm_cons
    	political_power_factor = bfx_mm_pp
    }
    """) + "\n")
    loc("bfx_legion_momentum", "Revolutionary Momentum", "court")
    loc("bfx_mac_mihaylov_desc", "IMRO leader 1924–1934. In 1944 Germany offered him an independent Macedonia and he refused. This time he accepts.", "characters")
    loc("bfx_legion_momentum_desc", "Momentum [?bfx_momentum|0]/100. Grows at war, decays in peace. Spend it in the Revolutionary Momentum decisions.", "court")
    loc("bfx_covert_rearmament", "Covert Rearmament", "neuilly")
    loc("bfx_covert_rearmament_desc", "Offsets the Shackles of Neuilly in proportion to Covert Rearmament ([?bfx_rearm|0]/100). At 100 every penalty is cancelled.", "neuilly")
    loc("bfx_court_balance", "The Tsar's Balance", "court")
    loc("bfx_court_balance_desc", "Crown [?bfx_inf_palace|0], Army [?bfx_inf_army|0], Legions [?bfx_inf_legion|0], IMRO [?bfx_inf_imro|0]. See the decision tab for what each bloc does.", "court")


def on_actions():
    add_file("common/on_actions/bfx_on_actions.txt", ded("""
    on_actions = {
    	on_startup = {
    		effect = {
    			if = { limit = { country_exists = BUL } BUL = { bfx_startup = yes } }
    		}
    	}
    	on_monthly_BUL = {
    		effect = { bfx_monthly = yes }
    	}
    }
    """) + "\n")


# ------------------------------------------------------------------ decisions
CATS = []
DECS = {}


def cat(id, icon, picture, visible, name, desc, priority=100):
    CATS.append(ded(f"""
    {id} = {{
    	icon = {icon}
    	picture = {picture}
    	allowed = {{ original_tag = BUL }}
    	visible = {{ {visible} }}
    	priority = {priority}
    }}"""))
    loc(id, name, "decisions")
    loc(id + "_desc", desc, "decisions")


def dec(category, id, name, desc, icon, cost, effect, visible="always = yes", available="always = yes",
        days_re_enable=None, fire_once=False, ai="factor = 1"):
    body = [f"{id} = {{", f"\ticon = {icon}", f"\tcost = {cost}"]
    if fire_once:
        body.append("\tfire_only_once = yes")
    if days_re_enable:
        body.append(f"\tdays_re_enable = {days_re_enable}")
    body.append(f"\tvisible = {{ {visible} }}")
    body.append(f"\tavailable = {{ {available} }}")
    body.append("\tcomplete_effect = {")
    body += ["\t\t" + l if l.strip() else l for l in ded(effect).split("\n")]
    body.append("\t}")
    body.append(f"\tai_will_do = {{ {ai} }}")
    body.append("}")
    DECS.setdefault(category, []).append("\n".join(body))
    loc(id, name, "decisions")
    loc(id + "_desc", desc, "decisions")


def decisions():
    # ---------------- Neuilly ----------------
    cat("bfx_neuilly_category", "military_operation", "GFX_decision_cat_picture_reforming_our_armed_forces",
        "NOT = { has_country_flag = bfx_neuilly_ended }", "Shackles of Neuilly",
        "§YCovert Rearmament§!: [?bfx_rearm|0] / 100  (each point cancels 1% of every Neuilly penalty)\n"
        "  rusts by §R[?bfx_rearm_decay|0]§! per month (0 with Hidden Arsenals)\n"
        "§YBalkan Suspicion§!: [?bfx_suspicion|0] / 100\n"
        "  grows by §R[?bfx_susp_growth|1]§! per month (1 + Rearmament / 25)\n\n"
        "Every time Suspicion climbs past a threshold:\n"
        " §Y25§! notes of protest\n §Y50§! the Entente guarantees each other against us\n"
        " §Y75§! a Balkan trade embargo\n §Y100§! the Petrich border crisis\n"
        "A threshold can fire again once Suspicion has dropped 15 points below it.\n\n"
        "Ends with the §YSalonika Agreement§! or by §YTearing Up Neuilly§!.")
    N = "bfx_neuilly_category"
    na = "NOT = { has_country_flag = bfx_neuilly_ended }"
    dec(N, "bfx_officer_schools", "Hidden Officer Schools",
        "The Military Academy is officially a school of gymnastics and surveying. It has a curious amount of artillery.",
        "generic_military", 40, neuilly(10, 7), available=na, days_re_enable=90, ai="factor = 5")
    dec(N, "bfx_flying_clubs", "\"Civilian\" Flying Clubs",
        "Gliding is a healthy sport for young men. So is formation flying, apparently.",
        "generic_air", 35, neuilly(8, 6) + "\nair_experience = 5", available=na, days_re_enable=90, ai="factor = 4")
    dec(N, "bfx_skoda_fronts", "Škoda Rifles via Swiss Fronts",
        "A Zurich trading house buys Czech rifles for an Ecuadorian police force that does not exist. The crates are unloaded in Burgas.",
        "generic_army_support", 50, neuilly(12, 9) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 1500 }",
        visible="has_country_flag = bfx_arms_fronts_open", available=na, days_re_enable=120, ai="factor = 4")
    dec(N, "bfx_rheinmetall_shells", "Rheinmetall Guns via a Dutch Shell Company",
        "Rheinmetall builds them at its Swiss works in Solothurn, a Rotterdam firm invoices them as mining equipment, and the War Ministry pays in tobacco.",
        "generic_tank", 50, neuilly(12, 10) + "\nadd_equipment_to_stockpile = { type = artillery_equipment amount = 120 }",
        visible="has_country_flag = bfx_arms_fronts_open", available=na, days_re_enable=120, ai="factor = 4")
    dec(N, "bfx_labour_service", "Expand the Labour Service",
        "The Trudova Povinnost is permitted by treaty. It is not the treaty's fault that labour battalions march in step.",
        "generic_construction", 30, neuilly(8, 5) + "\nadd_manpower = 3000", available=na, days_re_enable=90, ai="factor = 3")
    dec(N, "bfx_reassure_capitals", "Reassure the Balkan Capitals",
        "Kind words in Athens, a decoration for a Yugoslav minister and a very public inspection of a disarmed regiment.",
        "generic_political_discourse", 50, neuilly(0, -12), available=na, days_re_enable=60,
        ai="factor = 1\nmodifier = { factor = 6 check_variable = { bfx_suspicion > 40 } }")
    dec(N, "bfx_league_observers", "Wine and Dine the League Observers",
        "Geneva sends observers. Sofia sends them to the Black Sea resorts, and they write very positive reports.",
        "generic_political_address", 80, neuilly(0, -20), available=na, days_re_enable=180,
        ai="factor = 1\nmodifier = { factor = 10 check_variable = { bfx_suspicion > 65 } }")

    # ---------------- The Tsar's Balance ----------------
    cat("bfx_court_category", "generic_political_actions", "GFX_decision_cat_picture_plot_against_boris", "always = yes",
        "The Tsar's Balance",
        "Boris rules by balancing four blocs. Each one's influence (0-100) shapes the country through the §YTsar's Balance§! modifier:\n\n"
        "§YCrown§! [?bfx_inf_palace|0]: stability (above 50 helps, below hurts) and political power. Falls by 1 a month unless stability is above 60%.\n"
        "§YArmy§! [?bfx_inf_army|0]: organisation and army experience. Grows at war or when rearmament is above 50.\n"
        "§YLegions§! [?bfx_inf_legion|0]: war support and conscription. Grows with war support and fascist popularity; the Tsar's rule wears it down. §Y40§! is needed for the Legionary path.\n"
        "§YIMRO§! [?bfx_inf_imro|0]: faster war goals, but it costs stability. Grows while IMRO is tolerated.\n\n"
        "§RDanger§!: Army, Legions or IMRO above §Y80§!, the Crown below §Y20§! or the Army below §Y15§! each trigger a crisis.")
    C = "bfx_court_category"
    dec(C, "bfx_court_royal_audience", "Royal Audience", "The Tsar receives ministers, mayors and metropolitans, one at a time, and remembers every name.",
        "generic_political_address", 30, court(palace=8), days_re_enable=60, ai="factor = 2\nmodifier = { factor = 5 check_variable = { bfx_inf_palace < 35 } }")
    dec(C, "bfx_court_promote_generals", "Promote the General Staff", "New stars for the generals, new budgets for their divisions.",
        "generic_military", 40, court(army=10, palace=-5), days_re_enable=90, ai="factor = 1\nmodifier = { factor = 4 check_variable = { bfx_inf_army < 30 } }")
    dec(C, "bfx_court_purge_league", "Retire the Plotters", "The Military League's ringleaders are given early pensions and very distant postings.",
        "generic_arrest", 50, court(army=-20, palace=5) + "\nadd_stability = -0.02", days_re_enable=180,
        ai="factor = 0\nmodifier = { add = 5 check_variable = { bfx_inf_army > 70 } }")
    dec(C, "bfx_court_patronise_legions", "Patronise the Legions", "Ministers attend Legion rallies; Legion men are given police commissions.",
        "generic_political_rally", 35, court(legion=10) + "\nadd_war_support = 0.02", days_re_enable=60,
        ai="factor = 1\nmodifier = { factor = 15 has_country_flag = bfx_ai_fascist check_variable = { bfx_inf_legion < 45 } }")
    dec(C, "bfx_court_ban_rallies", "Ban the Torchlight Rallies", "No uniforms, no torches, no marching after dark.",
        "generic_police_action", 40, court(legion=-15) + "\nadd_war_support = -0.02", days_re_enable=120,
        ai="factor = 0\nmodifier = { add = 5 check_variable = { bfx_inf_legion > 70 } has_country_flag = bfx_boris_rules }")
    dec(C, "bfx_court_subsidise_committees", "Subsidise the Macedonian Committees", "Money for schools, newspapers and, discreetly, rifles.",
        "generic_nationalism", 30, court(imro=10), days_re_enable=90, ai="factor = 1")
    dec(C, "bfx_court_arrest_gunmen", "Arrest the IMRO Gunmen", "The Sofia police raid the Macedonian cafés.",
        "generic_arrest", 50, court(imro=-20) + "\nadd_stability = 0.02", days_re_enable=120,
        ai="factor = 0\nmodifier = { add = 5 check_variable = { bfx_inf_imro > 70 } }")
    dec(C, "bfx_court_metropolitan_blessing", "The Metropolitan's Blessing", "Metropolitan Stefan of Sofia blesses the Crown, the army and, after some negotiation, the budget.",
        "generic_welfare", 50, court(palace=5) + "\nadd_stability = 0.03", days_re_enable=180, ai="factor = 1")
    dec(C, "bfx_court_answer_coburg", "Answer the Letter from Coburg", "Ferdinand writes again. A reply will bring the next letter sooner.",
        "generic_monarchy", 75, "add_to_variable = { bfx_coburg_letters = 1 }\ncustom_effect_tooltip = bfx_tt_coburg_letter\nif = { limit = { check_variable = { bfx_coburg_letters > 2 } } set_country_flag = bfx_secret_unlocked mark_focus_tree_layout_dirty = yes }",
        visible="check_variable = { bfx_coburg_letters > 0 } check_variable = { bfx_coburg_letters < 3 } NOT = { has_country_flag = bfx_secret_unlocked }",
        days_re_enable=120, ai="factor = 1\nmodifier = { factor = 5 has_country_flag = bfx_ai_secret }")
    loc("bfx_tt_coburg_letter", "Letters from Coburg: §Y+1§! (at 3 a secret path is revealed)", "decisions")

    # ---------------- The Bulgarian Auction (Tsar's Way) ----------------
    cat("bfx_auction_category", "generic_foreign_policy", "GFX_decision_cat_picture_balkan_faction",
        "OR = { has_country_flag = bfx_bidding_open has_country_flag = bfx_change_sides_ready }", "The Bulgarian Auction",
        "Three powers are bidding for Bulgaria. Current offers:\n"
        "§YBerlin§! [?bfx_bid_ger|0]   §YLondon§! [?bfx_bid_eng|0]   §YMoscow§! [?bfx_bid_sov|0]\n\n"
        "While the auction is open every offer falls by §R1§! a month. Flirting with one power raises its offer and annoys the other two. "
        "An offer can also be §Ycashed in§! now for an instalment, at the cost of lowering it.\n\n"
        "When §YThe Auction Closes§! (focus), the highest bidder becomes our patron: §YBerlin§! pays in arms, §YLondon§! in factories, §YMoscow§! in guns and instructors. "
        "The Kingmaker joins the patron's alliance; the Hegemon keeps everyone's money instead.\n\n"
        "§YChange Sides§! (after The Contingency Plan): when our faction leader is losing, make peace with its enemies, leave, and turn on it.")
    A = "bfx_auction_category"
    open_ = "has_country_flag = bfx_bidding_open NOT = { has_country_flag = bfx_auction_closed }"
    for key, nm, g, e, so in (("ger", "Berlin", 12, -4, -4), ("eng", "London", -4, 12, -4), ("sov", "Moscow", -4, -4, 12)):
        dec(A, f"bfx_auction_flirt_{key}", f"Flirt with {nm}",
            f"A state visit, a medal for the ambassador and a newspaper campaign about {nm}'s many virtues.", "generic_political_discourse", 25,
            bid(ger=g, eng=e, sov=so), visible=open_, days_re_enable=60,
            ai="factor = 2" + {"ger": "\nmodifier = { factor = 3 has_country_flag = bfx_ai_tsar_kingmaker }", "eng": "", "sov": ""}[key])
    dec(A, "bfx_auction_leak", "Leak the Rival Offers",
        "Each embassy receives, by accident, a copy of the other two offers. Each raises its own.", "generic_operation", 50,
        bid(ger=5, eng=5, sov=5), visible=open_, days_re_enable=120, ai="factor = 2")
    dec(A, "bfx_auction_cash_ger", "Cash Berlin's Instalment", "German rifles now, in exchange for a little less German enthusiasm later.",
        "generic_army_support", 10, bid(ger=-15) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 1200 }\nadd_equipment_to_stockpile = { type = artillery_equipment amount = 24 }",
        visible=open_, available="check_variable = { bfx_bid_ger > 14 }", days_re_enable=120, ai="factor = 1")
    dec(A, "bfx_auction_cash_eng", "Cash London's Loan", "A sterling loan for a new factory. London's interest cools slightly.",
        "generic_construction", 10, bid(eng=-20) + "\n" + civ(1), visible=open_, available="check_variable = { bfx_bid_eng > 19 }",
        days_re_enable=180, ai="factor = 1")
    dec(A, "bfx_auction_cash_sov", "Cash Moscow's Instalment", "Soviet guns and a few instructors who ask a lot of questions.",
        "generic_tank", 10, bid(sov=-15) + "\narmy_experience = 15\nadd_equipment_to_stockpile = { type = artillery_equipment amount = 40 }",
        visible=open_, available="check_variable = { bfx_bid_sov > 14 }", days_re_enable=120, ai="factor = 1")
    dec(A, "bfx_change_sides", "Change Sides",
        "September 1944, early. Our patron is losing: make peace with its enemies, leave its alliance, ask the strongest of them to take us in, and declare war on the old patron.",
        "generic_break_treaty", 75, ded("""
        random_country = { limit = { is_faction_leader = yes is_in_faction_with = ROOT } save_event_target_as = bfx_old_patron }
        random_country = { limit = { is_faction_leader = yes has_war_with = ROOT } save_event_target_as = bfx_new_patron }
        every_country = { limit = { has_war_with = ROOT } white_peace = { tag = ROOT } }
        leave_faction = yes
        if = { limit = { has_event_target = bfx_new_patron } event_target:bfx_new_patron = { country_event = { id = bfx_dip.8 days = 1 } } }
        if = { limit = { has_event_target = bfx_old_patron } declare_war_on = { target = event_target:bfx_old_patron type = annex_everything } }
        add_stability = -0.05
        set_country_flag = bfx_changed_sides
        """) + "\ncustom_effect_tooltip = bfx_tt_change_sides_effect",
        visible="has_country_flag = bfx_change_sides_ready is_in_faction = yes is_faction_leader = no NOT = { has_country_flag = bfx_changed_sides }",
        available="has_war = yes any_country = { is_faction_leader = yes is_in_faction_with = ROOT surrender_progress > 0.25 }",
        fire_once=True, ai="factor = 1\nmodifier = { factor = 20 any_country = { is_faction_leader = yes is_in_faction_with = ROOT surrender_progress > 0.4 } }")
    loc("bfx_tt_change_sides_effect", "We leave our faction, make §Ywhite peace§! with every enemy, ask the strongest enemy faction leader to admit us, and §Rdeclare war on our old faction leader§!.", "decisions")

    # ---------------- Revolutionary Momentum (Legionary Revolution) ----------------
    cat("bfx_momentum_category", "military_operation", "GFX_decision_cat_picture_reforming_our_armed_forces",
        "has_country_flag = bfx_momentum_active", "Revolutionary Momentum",
        "§YMomentum§!: [?bfx_momentum|0] / 100\n\n"
        "The Legion lives on victories. Momentum grows by §G3§! a month at war (§G4§! on the crusade against the USSR) and falls by §R3§! a month at peace.\n"
        "It drives the §YRevolutionary Momentum§! modifier: attack (up to +10%), war support (-6% to +14%), conscription (up to +8%) and political power (-9% to +21%).\n\n"
        "§RBelow 15§! the movement fractures. §RAbove 90§! the revolution turns on its own generals. Spend it before that happens.")
    MO = "bfx_momentum_category"
    dec(MO, "bfx_mom_storm_offensive", "Storm Offensive",
        "Every Legion company goes over the top at dawn. Sixty days of fury.", "generic_military", 25,
        momentum(-25) + "\nadd_timed_idea = { idea = bfx_storm_offensive days = 60 }",
        available="has_war = yes check_variable = { bfx_momentum > 24 }", days_re_enable=90,
        ai="factor = 5\nmodifier = { factor = 3 check_variable = { bfx_momentum > 70 } }")
    dec(MO, "bfx_mom_mass_levy", "The Mass Levy", "The Legion's lists of volunteers become the army's lists of conscripts.",
        "generic_army_support", 25, momentum(-20) + "\nadd_manpower = 25000", available="check_variable = { bfx_momentum > 19 }",
        days_re_enable=120, ai="factor = 2\nmodifier = { factor = 4 check_variable = { bfx_momentum > 75 } }")
    dec(MO, "bfx_mom_tribunals", "Revolutionary Tribunals", "Show trials for the defeatists. The ministries become very obedient.",
        "generic_arrest", 0, momentum(-15) + "\nadd_political_power = 75\nadd_stability = -0.02",
        visible="has_country_flag = bfx_tribunals_open", available="check_variable = { bfx_momentum > 14 }", days_re_enable=90,
        ai="factor = 1\nmodifier = { factor = 5 check_variable = { bfx_momentum > 80 } }")
    dec(MO, "bfx_mom_requisitions", "Legionary Requisitions", "Grain, horses, lorries and rifles from every occupied district.",
        "generic_industry", 10, momentum(-15) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }\nadd_equipment_to_stockpile = { type = support_equipment amount = 100 }",
        visible="has_country_flag = bfx_requisitions_open", available="check_variable = { bfx_momentum > 14 }", days_re_enable=90,
        ai="factor = 1\nmodifier = { factor = 5 check_variable = { bfx_momentum > 80 } }")
    dec(MO, "bfx_mom_torchlight", "Torchlight Rallies", "Ten thousand torches on Alexander Nevsky Square. Peace is no excuse for sitting still.",
        "generic_political_rally", 30, momentum(8) + "\nadd_war_support = 0.02", available="has_war = no", days_re_enable=60,
        ai="factor = 2\nmodifier = { factor = 5 check_variable = { bfx_momentum < 25 } }")
    dec(MO, "bfx_mom_incident", "Manufacture an Incident", "A shot at a frontier post, a burned customs house and a furious radio.",
        "generic_assassination", 40, momentum(15) + "\nadd_named_threat = { threat = 2 name = bfx_threat_incident }\nadd_war_support = 0.03",
        visible="has_country_flag = bfx_incidents_open", days_re_enable=120,
        ai="factor = 2\nmodifier = { factor = 5 check_variable = { bfx_momentum < 25 } }")
    loc("bfx_threat_incident", "Bulgarian border incident", "decisions")
    loc("bfx_tt_intervene_guarantors", "§RCountries that guarantee Yugoslavia join the war against us§! (its faction allies may too). When Belgrade gives up, we can make peace with all of them at once.", "decisions")

    # ---------------- Diplomacy ----------------
    cat("bfx_diplomacy_category", "generic_foreign_policy", "GFX_decision_cat_picture_balkan_faction",
        "has_country_flag = bfx_chancelleries_open", "The Sofia Chancellery",
        "Non-aggression pacts, guarantees, alliances and demands. Each proposal is sent as an event; the other side may refuse.")
    D = "bfx_diplomacy_category"
    names = {"TUR": "Turkey", "ROM": "Romania", "GRE": "Greece", "YUG": "Yugoslavia", "SOV": "the Soviet Union", "HUN": "Hungary",
             "ITA": "Italy", "GER": "Germany", "ENG": "Britain", "FRA": "France", "ALB": "Albania"}
    for t in ("TUR", "ROM", "GRE", "YUG", "SOV", "HUN", "ITA"):
        dec(D, f"bfx_dip_nap_{t.lower()}", f"Propose a Pact to {names[t]}",
            f"A non-aggression pact with {names[t]}: one frontier fewer to watch.", "generic_political_discourse", 25,
            f"{t} = {{ country_event = {{ id = bfx_dip.1 days = 2 }} }}",
            visible=f"country_exists = {t} NOT = {{ is_in_faction_with = {t} }}", available=f"NOT = {{ has_war_with = {t} }}",
            days_re_enable=180, ai="factor = 1")
    for t in ("GER", "ITA", "ENG", "FRA"):
        dec(D, f"bfx_dip_guarantee_{t.lower()}", f"Ask {names[t]} for a Guarantee",
            f"A great-power guarantee makes a small kingdom expensive to invade.", "generic_political_address", 25,
            f"{t} = {{ country_event = {{ id = bfx_dip.4 days = 2 }} }}",
            visible=f"country_exists = {t}", available=f"NOT = {{ has_war_with = {t} }}", days_re_enable=180, ai="factor = 1")
    for t in ("HUN", "ROM", "GRE", "YUG", "TUR", "ALB"):
        dec(D, f"bfx_dip_invite_{t.lower()}", f"Invite {names[t]} to Our Alliance",
            f"{names[t]} is invited to join our faction.", "generic_form_nation", 25,
            f"{t} = {{ country_event = {{ id = bfx_dip.5 days = 2 }} }}",
            visible=f"is_faction_leader = yes country_exists = {t}", available=f"{t} = {{ is_in_faction = no }} NOT = {{ has_war_with = {t} }}",
            days_re_enable=180, ai="factor = 2")
    for t in ("ALB", "HUN", "GRE", "ROM", "YUG"):
        dec(D, f"bfx_dip_give_guarantee_{t.lower()}", f"Guarantee {names[t]}",
            f"Bulgaria promises to defend {names[t]}, and expects gratitude.", "generic_protection", 15, f"give_guarantee = {t}",
            visible=f"country_exists = {t}", available=f"NOT = {{ has_war_with = {t} }}", fire_once=True, ai="factor = 0")
    dec(D, "bfx_dip_demand_dobruja", "Demand Southern Dobruja", "Ask, firmly, for the Quadrilateral. A refusal gives us a war goal.",
        "generic_break_treaty", 50, "add_state_claim = 77\n77 = { owner = { country_event = { id = bfx_dip.6 days = 2 } } }",
        visible="NOT = { owns_state = 77 }", available="77 = { owner = { NOT = { is_in_faction_with = ROOT } NOT = { has_war_with = ROOT } } }",
        days_re_enable=365, ai="factor = 2")

    # ---------------- IMRO and the Macedonian uprising ----------------
    cat("bfx_imro_category", "generic_political_actions", "GFX_decision_cat_picture_macedonian_organizations",
        "has_country_flag = bfx_imro_tolerated", "The Macedonian Uprising",
        "§YUnrest in Vardar Macedonia§!: [?bfx_macedonia_unrest|0] / 100. At §Y70§! IMRO can raise the §YIlinden banner§!: the province rises as the §YIndependent State of Macedonia§!, splitting off part of the Yugoslav army in a civil war.\n"
        "Feed the rising with volunteers, rifles and officers. If it survives §Y8 months§!, or Yugoslavia starts to collapse, Belgrade lets it go. "
        "Half a year after independence Skopje asks to join Bulgaria.\n\nUprising months: [?bfx_uprising_months|0]")
    M = "bfx_imro_category"
    no_rising = "NOT = { has_country_flag = bfx_uprising_active } NOT = { has_country_flag = bfx_macedonia_free } NOT = { owns_state = 106 } 106 = { is_owned_by = YUG }"

    def unrest(n):
        key = f"bfx_tt_unrest_{n}"
        loc(key, f"Unrest in Vardar Macedonia: §R+{n}§!", "decisions")
        return f"add_to_variable = {{ bfx_macedonia_unrest = {n} }}\nclamp_variable = {{ var = bfx_macedonia_unrest min = 0 max = 100 }}\ncustom_effect_tooltip = {key}"
    dec(M, "bfx_imro_cheta_raids", "Cheta Raids into Vardar",
        "Small bands cross at night, burn a gendarmerie post and leave leaflets.", "generic_assassination", 40,
        unrest(15) + "\nYUG = { add_stability = -0.02 }\n" + neuilly(0, 5), visible="always = yes", available=no_rising,
        days_re_enable=60, ai="factor = 3")
    dec(M, "bfx_imro_newspapers", "Print the Macedonian Newspapers", "Pamphlets, calendars and songbooks for every village from Kumanovo to Ohrid.",
        "generic_speech", 20, unrest(8), available=no_rising, days_re_enable=45, ai="factor = 3")
    dec(M, "bfx_imro_arms_caches", "Hide Arms Caches", "Rifles buried under church floors and in beehives.",
        "generic_army_support", 25, unrest(10) + "\nadd_equipment_to_stockpile = { type = infantry_equipment amount = -500 }",
        available=no_rising, days_re_enable=60, ai="factor = 3")
    dec(M, "bfx_imro_ilinden", "Raise the Ilinden Banner",
        "St Elijah's Day, 1903: IMRO rose and was crushed. This time Bulgaria is waiting across the border. Vardar Macedonia rises as the Independent State of Macedonia.",
        "generic_ignite_civil_war", 100, "bfx_start_macedonian_uprising = yes\n" + court(imro=10) + "\n" + neuilly(0, 20),
        available=no_rising + " check_variable = { bfx_macedonia_unrest > 69 } YUG = { has_civil_war = no }",
        days_re_enable=365, ai="factor = 10")
    rebel = "any_country = { has_country_flag = bfx_imro_rebel_state }"
    act = f"has_country_flag = bfx_uprising_active {rebel}"
    dec(M, "bfx_uprising_volunteers", "Send Komitadji Volunteers", "Young men from the emigration cross the Osogovo passes.",
        "generic_army_support", 25, "add_manpower = -8000\nevery_country = { limit = { has_country_flag = bfx_imro_rebel_state } add_manpower = 8000 }",
        visible=act, days_re_enable=30, ai="factor = 5")
    dec(M, "bfx_uprising_rifles", "Rifles over the Osogovo", "Pack mules, moonless nights and very understanding border guards.",
        "generic_army_support", 15, "add_equipment_to_stockpile = { type = infantry_equipment amount = -1500 }\nevery_country = { limit = { has_country_flag = bfx_imro_rebel_state } add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 } }",
        visible=act, days_re_enable=30, ai="factor = 5")
    dec(M, "bfx_uprising_guns", "Mountain Guns for Skopje", "Pack howitzers, broken down onto mules and reassembled in the hills.",
        "generic_tank", 25, "add_equipment_to_stockpile = { type = artillery_equipment amount = -60 }\nevery_country = { limit = { has_country_flag = bfx_imro_rebel_state } add_equipment_to_stockpile = { type = artillery_equipment amount = 60 } }",
        visible=act, days_re_enable=60, ai="factor = 3")
    dec(M, "bfx_uprising_officers", "Officers on Leave", "Bulgarian officers take unpaid leave, grow beards and turn up in Skopje.",
        "generic_military", 50, "army_experience = -10\nevery_country = { limit = { has_country_flag = bfx_imro_rebel_state } add_ideas = bfx_imro_bulgarian_officers }",
        visible=act, fire_once=True, ai="factor = 5")
    dec(M, "bfx_uprising_recognise", "Recognise the Independent State", "Sofia recognises Skopje and guarantees it. Belgrade will not forgive this.",
        "generic_independence", 40, "every_country = { limit = { has_country_flag = bfx_imro_rebel_state } ROOT = { give_guarantee = PREV } }\nYUG = { add_opinion_modifier = { target = ROOT modifier = bfx_om_bulgarian_threat } }\n" + neuilly(0, 15),
        visible=act, fire_once=True, ai="factor = 2")
    dec(M, "bfx_uprising_intervene", "Intervene Openly", "The army crosses the border to help our brothers. This means war with Yugoslavia.",
        "generic_break_treaty", 50, "every_country = { limit = { has_country_flag = bfx_imro_rebel_state } ROOT = { add_to_war = { targeted_alliance = PREV enemy = YUG } } }\n"
        "every_country = { limit = { has_guaranteed = YUG NOT = { tag = ROOT } NOT = { has_war_with = ROOT } NOT = { is_in_faction_with = ROOT } } add_to_war = { targeted_alliance = YUG enemy = ROOT } }\n"
        "custom_effect_tooltip = bfx_tt_intervene_guarantors",
        visible=act, available="NOT = { has_war_with = YUG }", fire_once=True, ai="factor = 1\nmodifier = { factor = 5 has_country_flag = bfx_ai_tsar_hegemon }")

    # ---------------- Integration (compliance-gated cores) ----------------
    cat("bfx_integration_category", "generic_formable_nations", "GFX_decision_cat_generic_byzantine_empire",
        "has_country_flag = bfx_integration_unlocked", "Integration",
        "Conquered lands become core lands only once they accept Bulgarian rule. Each decision cores every §Yheld§! state of its region whose §Ycompliance§! is high enough; historically Bulgarian lands need less. Repeat as compliance rises.")
    I = "bfx_integration_category"
    regions = [
        ("bulgarian_lands", "the Bulgarian Lands", "OR = { state = 106 state = 184 state = 77 state = 341 state = 731 state = 971 is_core_of = MAC }", 35),
        ("serbia", "Serbia and Montenegro", "OR = { is_core_of = YUG is_core_of = SER is_core_of = MNT is_core_of = CRO is_core_of = SLV is_core_of = BOS }", 65),
        ("greece", "Greece", "is_core_of = GRE", 60),
        ("albania", "Albania", "is_core_of = ALB", 60),
        ("romania", "Romania and Bessarabia", "OR = { is_core_of = ROM is_core_of = MOL }", 65),
        ("anatolia", "Thrace and Anatolia", "is_core_of = TUR", 70),
        ("pontic_coast", "the Pontic Coast", "is_core_of = UKR", 75),
    ]
    for key, nm, lim, comp in regions:
        dec(I, f"bfx_integrate_{key}", f"Integrate {nm}",
            f"Governors, schoolteachers, a census and a new flag over the town hall. Cores on every held state of {nm} with compliance above {comp}%.",
            "generic_form_nation", 50, ded(f"""
            every_owned_state = {{ limit = {{ {lim} NOT = {{ is_core_of = ROOT }} compliance > {comp} }} add_core_of = ROOT }}
            add_stability = -0.01
            """), available=f"any_owned_state = {{ {lim} NOT = {{ is_core_of = ROOT }} compliance > {comp} }}",
            days_re_enable=60, ai="factor = 10")
    dec(I, "bfx_proclaim_bulgarian_empire", "Proclaim the Bulgarian Empire",
        "Macedonia, Thrace, Dobrudja and Edirne are ours. Whatever the regime calls itself, it now rules an empire. Every held non-core state gains compliance.",
        "generic_form_nation", 150, ded("""
        set_cosmetic_tag = bfx_bulgarian_empire
        every_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 20 }
        add_ideas = bfx_imperial_mandate
        """), available="owns_state = 106 owns_state = 184 owns_state = 77 owns_state = 341", fire_once=True, ai="factor = 50")

    # ---------------- the secret path: Tsargrad propaganda ----------------
    cat("bfx_tsargrad_category", "generic_monarchism", "GFX_decision_cat_generic_byzantine_empire",
        "has_completed_focus = bfx_alt_old_fox_stirs", "Tsargrad Propaganda",
        "Imperial fervour: §Y[?bfx_tsargrad_fervour|0]§! / 100. Fervour speeds the empire's integration: at §Y50§! the §YTheme§! decisions core held lands at far lower compliance than normal.")
    T = "bfx_tsargrad_category"

    def fervour(n):
        key = f"bfx_tt_fervour_{n}".replace("-", "m")
        loc(key, f"Imperial fervour: §{'G' if n > 0 else 'R'}{n:+d}§!", "decisions")
        return f"add_to_variable = {{ bfx_tsargrad_fervour = {n} }}\nclamp_variable = {{ var = bfx_tsargrad_fervour min = 0 max = 100 }}\ncustom_effect_tooltip = {key}"
    dec(T, "bfx_tsargrad_radio_hour", "The Tsargrad Radio Hour",
        "Byzantine chant, Simeon's letters and the dinner menu of the Imperial household, every evening.", "generic_speech", 30,
        fervour(10) + "\nadd_war_support = 0.02", days_re_enable=45, ai="factor = 3")
    dec(T, "bfx_tsargrad_regalia", "Commission the Imperial Regalia",
        "A crown modelled on Simeon's, a sceptre modelled on Justinian's.", "generic_monarchy", 50,
        fervour(15) + "\nadd_stability = 0.05", fire_once=True, ai="factor = 3")
    dec(T, "bfx_tsargrad_orthodox_missions", "Orthodox Missions",
        "Bulgarian priests visit every Orthodox village from Odessa to Antioch with icons, bread and maps.", "generic_nationalism", 40,
        fervour(15), days_re_enable=120, ai="factor = 2")
    themes = [("thrace", "Thrace", "OR = { is_core_of = TUR is_core_of = GRE }"), ("illyricum", "Illyricum", "OR = { is_core_of = YUG is_core_of = SER is_core_of = ALB is_core_of = MNT }"),
              ("paristrion", "Paristrion", "OR = { is_core_of = ROM is_core_of = MOL }")]
    for key, nm, lim in themes:
        dec(T, f"bfx_theme_{key}", f"Restore the Theme of {nm}",
            f"A strategos is appointed and the land written into the Imperial register. Cores on every held state of the theme with compliance above 40%.",
            "generic_form_nation", 75, ded(f"""
            every_owned_state = {{ limit = {{ {lim} NOT = {{ is_core_of = ROOT }} compliance > 40 }} add_core_of = ROOT }}
            """) + "\n" + fervour(-30),
            available=f"check_variable = {{ bfx_tsargrad_fervour > 49 }} any_owned_state = {{ {lim} NOT = {{ is_core_of = ROOT }} compliance > 40 }}",
            days_re_enable=60, ai="factor = 10")

    add_file("common/decisions/categories/bfx_decision_categories.txt", "\n\n".join(CATS) + "\n")
    out = []
    for c, ds in DECS.items():
        out.append(f"{c} = {{")
        for d in ds:
            out.append("\n".join("\t" + l if l.strip() else l for l in d.split("\n")))
        out.append("}\n")
    add_file("common/decisions/bfx_decisions.txt", "\n".join(out))


# name, def, adj, map colour
COSMETIC = {
    "bfx_greater_bulgaria": ("Greater Bulgaria", "Greater Bulgaria", "Bulgarian", (34, 128, 76)),
    "bfx_san_stefano_bulgaria": ("San Stefano Bulgaria", "San Stefano Bulgaria", "Bulgarian", (20, 150, 100)),
    "bfx_balkan_tsardom": ("Tsardom of the Balkans", "the Tsardom of the Balkans", "Balkan", (150, 32, 44)),
    "bfx_legionary_bulgaria": ("Legionary State of Greater Bulgaria", "the Legionary State of Greater Bulgaria", "Legionary", (70, 96, 40)),
    "bfx_bulgarian_imperium": ("Bulgarian Imperium", "the Bulgarian Imperium", "Imperial", (96, 34, 30)),
    "bfx_third_empire": ("Third Bulgarian Empire", "the Third Bulgarian Empire", "Imperial Bulgarian", (122, 22, 64)),
    "bfx_byzantium": ("Empire of the Romans and Bulgars", "the Empire of the Romans and Bulgars", "Romaic", (112, 24, 112)),
    "bfx_independent_macedonia": ("Independent State of Macedonia", "the Independent State of Macedonia", "Macedonian", (196, 52, 40)),
    "bfx_bulgarian_empire": ("Bulgarian Empire", "the Bulgarian Empire", "Imperial Bulgarian", (60, 110, 60)),
}
COSMETIC_IDEOLOGY_NAMES = {
    "bfx_bulgarian_empire": {"fascism": ("Legionary Empire of Bulgaria", "the Legionary Empire of Bulgaria", "Legionary")},
}


def cosmetic():
    colours = []
    for tag, (name, df, adj, rgb) in COSMETIC.items():
        loc(tag, name, "cosmetic")
        loc(tag + "_DEF", df, "cosmetic")
        loc(tag + "_ADJ", adj, "cosmetic")
        for ideo in ("neutrality", "fascism", "communism", "democratic"):
            n2, d2, a2 = COSMETIC_IDEOLOGY_NAMES.get(tag, {}).get(ideo, (name, df, adj))
            loc(f"{tag}_{ideo}", n2, "cosmetic")
            loc(f"{tag}_{ideo}_DEF", d2, "cosmetic")
            loc(f"{tag}_{ideo}_ADJ", a2, "cosmetic")
        r, g, b = rgb
        ur, ug, ub = (min(255, int(c * 1.3) + 10) for c in rgb)
        colours.append(f"{tag} = {{\n\tcolor = rgb {{ {r} {g} {b} }}\n\tcolor_ui = rgb {{ {ur} {ug} {ub} }}\n}}")
    add_file("common/countries/bfx_cosmetic.txt", "\n".join(colours) + "\n")
    for fac, nm in [("bfx_faction_balkan_axis", "Balkan Axis"), ("bfx_faction_sofia_pact", "The Sofia Pact"),
                    ("bfx_faction_pact_of_iron", "The Pact of Iron")]:
        loc(fac, nm, "misc")


def generate():
    scripted_effects()
    dynamic_modifiers()
    on_actions()
    decisions()
    cosmetic()
