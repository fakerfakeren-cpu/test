"""Helpers shared by the path modules."""
from focus_core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    cores_on_owned_cores_of, wargoal_on_owner, tt, neuilly, F, swap, court, ai_flag, ai_prefer, INTEGRATION, \
    transfer_if_allied, F_POL, F_STAB, F_WS, F_IND, F_RES, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, \
    F_MILCHAR, F_POLCHAR
from focus_opening import CHANCELLERY_RULES  # noqa: F401


def wargoal_states(anchor, states, wg="take_state_focus"):
    gen = " ".join(str(s) for s in states)
    return ded(f"""
    if = {{
    	limit = {{ {anchor} = {{ owner = {{ NOT = {{ tag = ROOT }} NOT = {{ is_in_faction_with = ROOT }} }} }} }}
    	{anchor} = {{ owner = {{ save_event_target_as = bfx_wg_target }} }}
    	create_wargoal = {{ type = {wg} target = event_target:bfx_wg_target generator = {{ {gen} }} }}
    }}""")


def wargoal_annex(tag):
    return f"if = {{ limit = {{ country_exists = {tag} NOT = {{ is_in_faction_with = {tag} }} NOT = {{ has_war_with = {tag} }} }} create_wargoal = {{ type = annex_everything target = {tag} }} }}"


