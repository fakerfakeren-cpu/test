"""Shared registry for the bfx_bulgaria generator.

Every content module registers files and localisation here; build_mod.py writes them.
Keeping loc next to the script that uses it is what keeps keys and IDs in sync.
"""
import os
import textwrap
from collections import OrderedDict

FILES = OrderedDict()          # relative path -> text
LOC = OrderedDict()            # group -> OrderedDict(key -> text)
BINARIES = OrderedDict()       # relative path -> callable(abs_path) that writes the file


def loc(key, text, group="misc"):
    g = LOC.setdefault(group, OrderedDict())
    for other, keys in LOC.items():
        if key in keys and other != group:
            raise ValueError(f"loc key {key} defined in {other} and {group}")
    if key in g and g[key] != text:
        raise ValueError(f"loc key {key} defined twice with different text")
    g[key] = text
    return key


def add_file(path, text):
    if path in FILES:
        raise ValueError(f"file {path} written twice")
    FILES[path] = text


def ded(s):
    return textwrap.dedent(s).strip("\n")


def indent(s, n):
    pad = "\t" * n
    return "\n".join(pad + line if line.strip() else line for line in ded(s).split("\n"))


# ---------- reusable script snippets ----------

def build(kind, count, level=1):
    """Build `count` buildings of a state-level type in owned states with free slots."""
    out = []
    for _ in range(count):
        out.append(ded(f"""
        random_owned_controlled_state = {{
        	limit = {{ free_building_slots = {{ building = {kind} size > 0 include_locked = yes }} }}
        	add_extra_state_shared_building_slots = 1
        	add_building_construction = {{ type = {kind} level = {level} instant_build = yes }}
        }}"""))
    return "\n".join(out)


def civ(n):
    return build("industrial_complex", n)


def mil(n):
    return build("arms_factory", n)


def dock(n):
    return ded(f"""
    random_owned_controlled_state = {{
    	limit = {{ is_coastal = yes free_building_slots = {{ building = dockyard size > 0 include_locked = yes }} }}
    	add_extra_state_shared_building_slots = 1
    	add_building_construction = {{ type = dockyard level = {n} instant_build = yes }}
    }}""")


def tech(name, cat, bonus=0.5, uses=1):
    return f"add_tech_bonus = {{ name = {name} bonus = {bonus} uses = {uses} category = {cat} }}"


def claim_states(*ids):
    return "\n".join(f"add_state_claim = {s}" for s in ids)


def core_if_owned(*ids):
    return "\n".join(f"if = {{ limit = {{ owns_state = {s} }} add_state_core = {s} }}" for s in ids)


def claims_on_cores_of(*tags):
    """Claim every state that is a core of the given tags (tag-driven, no hardcoded state IDs)."""
    lim = " ".join(f"is_core_of = {t}" for t in tags)
    return ded(f"""
    every_state = {{
    	limit = {{ OR = {{ {lim} }} NOT = {{ is_core_of = ROOT }} NOT = {{ is_claimed_by = ROOT }} }}
    	add_claim_by = ROOT
    }}""")


def cores_on_owned_cores_of(*tags):
    lim = " ".join(f"is_core_of = {t}" for t in tags)
    return ded(f"""
    every_owned_state = {{
    	limit = {{ OR = {{ {lim} }} NOT = {{ is_core_of = ROOT }} }}
    	add_core_of = ROOT
    }}""")


def wargoal_on_owner(state, wg="take_state_focus"):
    return ded(f"""
    if = {{
    	limit = {{ NOT = {{ owns_state = {state} }} }}
    	{state} = {{ owner = {{ save_event_target_as = bfx_wg_target }} }}
    	create_wargoal = {{ type = {wg} target = event_target:bfx_wg_target generator = {{ {state} }} }}
    }}""")


def tt(key, text, group="tooltips"):
    """custom_effect_tooltip with its loc in one call."""
    loc(key, text, group)
    return f"custom_effect_tooltip = {key}"


def neuilly(rearm=0, susp=0):
    """Change the mechanic's variables (no-op once the treaty is gone) with a readable tooltip."""
    parts = []
    if rearm:
        parts.append(f"add_to_variable = {{ bfx_rearm = {rearm} }}")
    if susp:
        parts.append(f"add_to_variable = {{ bfx_suspicion = {susp} }}")
    key = f"bfx_tt_neuilly_r{rearm}_s{susp}".replace("-", "m")
    txt = []
    if rearm:
        txt.append(f"Covert Rearmament: §{'G' if rearm > 0 else 'R'}{rearm:+d}§!")
    if susp:
        txt.append(f"Balkan Suspicion: §{'R' if susp > 0 else 'G'}{susp:+d}§!")
    loc(key, " | ".join(txt) + " §L(while the Shackles of Neuilly remain)§!", "neuilly")
    return ded(f"""
    if = {{
    	limit = {{ NOT = {{ has_country_flag = bfx_neuilly_ended }} }}
    	custom_effect_tooltip = {key}
    	hidden_effect = {{
    		{' '.join(parts)}
    		bfx_neuilly_recalc = yes
    	}}
    }}""")


def make_leader(char, name, trait):
    """Make `char` the country leader. In 1.19 the runtime recruit/promote did not always take (the next in line stayed
    leader), so if `char` is not ruling afterwards the leader who is ruling gets his name, portrait and trait instead."""
    return "\n" + ded(f"""
    retire_country_leader = yes
    recruit_character = {char}
    promote_character = {char}
    if = {{
    	limit = {{ NOT = {{ has_country_leader = {{ character = {char} ruling_only = yes }} }} }}
    	set_country_leader_name = {{ name = "{name}" }}
    	set_country_leader_portrait = {{ portrait = GFX_portrait_{char} }}
    	add_country_leader_trait = {trait}
    }}""") + "\n"
