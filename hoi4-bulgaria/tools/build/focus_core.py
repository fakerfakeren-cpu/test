"""Shared helpers for the focus spec modules. Coordinates are spec columns/rows; tree.py spreads them."""
from core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    cores_on_owned_cores_of, wargoal_on_owner, tt, loc, neuilly  # noqa: F401  (re-exported)

FOCUSES = []

F_POL, F_STAB, F_WS, F_IND, F_RES, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, F_MILCHAR, F_POLCHAR = (
    "FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_STABILITY", "FOCUS_FILTER_WAR_SUPPORT", "FOCUS_FILTER_INDUSTRY",
    "FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_ARMY_XP",
    "FOCUS_FILTER_NAVY_XP", "FOCUS_FILTER_AIR_XP", "FOCUS_FILTER_HISTORICAL", "FOCUS_FILTER_MILITARY_CHARACTER",
    "FOCUS_FILTER_POLITICAL_CHARACTER")


def F(id, x, y, name, desc, reward, icon, block, prereq=(), excl=(), cost=10, available=None, bypass=None,
      ai=None, filters=(F_POL,), kind="effect", war_with=(), select=None, allow_branch=None):
    """kind: 'stat' marks a plain stat bump (for the share-of-stat-bumps check)."""
    FOCUSES.append(dict(id=id, x=x, y=y, name=name, desc=desc, reward=ded(reward), icon=icon, block=block,
                        prereq=[list(p) if isinstance(p, (list, tuple)) else [p] for p in prereq],
                        excl=list(excl), cost=cost, available=ded(available) if available else None,
                        bypass=ded(bypass) if bypass else None, ai=ded(ai) if ai else "factor = 10",
                        filters=list(filters), kind=kind, war_with=list(war_with),
                        select=ded(select) if select else None,
                        allow_branch=ded(allow_branch) if allow_branch else None))


def swap(old, new):
    return f"if = {{ limit = {{ has_idea = {old} }} swap_ideas = {{ remove_idea = {old} add_idea = {new} }} }}\nelse = {{ add_ideas = {new} }}"


def court(palace=0, army=0, legion=0, imro=0):
    """Shift the Tsar's Balance with a readable tooltip."""
    parts, txt = [], []
    for var, val, label in (("palace", palace, "Crown"), ("army", army, "Army"), ("legion", legion, "Legions"), ("imro", imro, "IMRO")):
        if val:
            parts.append(f"add_to_variable = {{ bfx_inf_{var} = {val} }}")
            txt.append(f"{label} §{'G' if val > 0 else 'R'}{val:+d}§!")
    key = "bfx_tt_court_" + "_".join(f"{k[0]}{v}".replace("-", "m") for k, v in
                                      (("p", palace), ("a", army), ("l", legion), ("i", imro)) if v)
    loc(key, "The Tsar's Balance: " + ", ".join(txt), "court")
    return ded(f"""
    custom_effect_tooltip = {key}
    hidden_effect = {{
    	{' '.join(parts)}
    	bfx_court_recalc = yes
    }}""")


def ai_flag(flag, base=10):
    return f"factor = {base}\nmodifier = {{ factor = 0 is_ai = yes NOT = {{ has_country_flag = {flag} }} }}"


def ai_prefer(flag, base=10, mult=5):
    return f"factor = {base}\nmodifier = {{ factor = {mult} has_country_flag = {flag} }}"


INTEGRATION = "set_country_flag = bfx_integration_unlocked\nunlock_decision_category_tooltip = bfx_integration_category"


def transfer_if_allied(*states):
    """Axis-style award: states held by us or a faction partner are handed to Bulgaria."""
    return "\n".join(ded(f"""
    if = {{
    	limit = {{ {s} = {{ NOT = {{ is_owned_by = ROOT }} controller = {{ OR = {{ tag = ROOT is_in_faction_with = ROOT }} }} }} }}
    	transfer_state = {s}
    }}""") for s in states)


def bid(ger=0, eng=0, sov=0):
    """Shift the Great Powers' bids for Bulgaria (the Tsar's auction) with a readable tooltip."""
    parts, txt = [], []
    for var, val, label in (("ger", ger, "Berlin"), ("eng", eng, "London"), ("sov", sov, "Moscow")):
        if val:
            parts.append(f"add_to_variable = {{ bfx_bid_{var} = {val} }}")
            txt.append(f"{label} §{'G' if val > 0 else 'R'}{val:+d}§!")
    key = "bfx_tt_bid_" + "_".join(f"{k}{v}".replace("-", "m") for k, v in (("g", ger), ("e", eng), ("s", sov)) if v)
    loc(key, "The Bulgarian Auction, offers: " + ", ".join(txt), "court")
    return ded(f"""
    custom_effect_tooltip = {key}
    hidden_effect = {{
    	{' '.join(parts)}
    	bfx_bids_recalc = yes
    }}""")


def momentum(n):
    """Shift the Legion's Revolutionary Momentum with a readable tooltip."""
    key = f"bfx_tt_momentum_{n}".replace("-", "m")
    loc(key, f"Revolutionary Momentum: §{'G' if n > 0 else 'R'}{n:+d}§!", "court")
    return ded(f"""
    custom_effect_tooltip = {key}
    hidden_effect = {{
    	add_to_variable = {{ bfx_momentum = {n} }}
    	bfx_momentum_recalc = yes
    }}""")
