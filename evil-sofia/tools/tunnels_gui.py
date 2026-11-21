"""The Underground of Serdica: a custom window (scripted GUI) for Sredets' authoritarian road.

A 9x7 grid of rock under Sofia. The middle tile is the chamber under the Largo; on the edges are the cellars of ten
districts, roughly where they lie. The player clicks a rock tile next to the tunnels to dig it (10 political power,
14 days, 28 in hard rock, a limited number of miners at a time). What is inside each tile is random every game and
hidden until it is dug: plain earth, Roman ruins (a reward), a smugglers' cache (rifles), groundwater (the tile
floods and blocks the way) or hard rock (slow). A tunnel can cave in. Digging into a cellar is a breakthrough: the
open cellar can be selected, and the side panel offers what the focuses have unlocked against that district, each
once per district: Agents from Below, Tunnel Strike, The Coup from Below. The grid is finite and the whole thing closes
when the Directorate of Sofia is proclaimed.

Writes: common/scripted_guis, interface (.gui and .gfx), the sprites, events/evil_sofia_tunnels.txt,
common/scripted_effects (the set-up), common/scripted_localisation and the texts.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

COLS, ROWS = 9, 7
TW, TH = 72, 60                      # tile size in px
LARGO = 3 * COLS + 4                 # the middle tile
# cellar tiles: tile index -> district tag (roughly where each district lies from Sredets)
CELLARS = {3 * COLS + 2: "VAZ", 3 * COLS + 6: "OBR", 5 * COLS + 4: "LOZ", 5 * COLS + 2: "TRD", 5 * COLS + 6: "IZG",
           4 * COLS + 8: "SLA", 0 * COLS + 4: "SRK", 0 * COLS + 7: "POD", 5 * COLS + 0: "KRS", 1 * COLS + 1: "ILN"}
# frames of the tile sprite (1-based)
ROCK, TUNNEL, DIGGING, RUINS, FLOODED, CACHE, CHAMBER, DOOR, OPEN, SEALED = range(1, 11)
PASSABLE = (TUNNEL, RUINS, CACHE, CHAMBER, OPEN)
# hidden contents of a rock tile: (weight, code); 0 earth, 1 Roman ruins, 2 water, 3 smugglers' cache, 4 hard rock
CONTENTS = [(56, 0), (14, 1), (12, 2), (8, 3), (10, 4)]
DIG_COST, DIG_DAYS, HARD_DAYS, CAVE_IN = 10, 14, 28, 10
GRID_X, GRID_Y = 24, 92
PANEL_X = GRID_X + COLS * TW + 18
WIN_W, WIN_H = PANEL_X + 196, GRID_Y + ROWS * TH + 70
ACTIONS = {  # name: (unlock flag, political power, label, tooltip, extra trigger on the target, effect on target)
    "agents": ("SRD_agents_unlocked", 40, "Agents from Below",
               "Agents come up through the cellar: the district loses 10% stability and 5% war support for four "
               "months. Once per district. Costs 40 political power.",
               "NOT = { has_idea = SRD_agents_below }", "add_timed_idea = { idea = SRD_agents_below days = 120 }"),
    "strike": ("SRD_strike_unlocked", 60, "Tunnel Strike",
               "The guard comes up behind their lines: for 45 days their army defends 15% worse with 10% less "
               "organisation, and ours attacks 10% better. Only at war with them. Once per district. Costs 60 "
               "political power.",
               "has_war_with = ROOT", "add_timed_idea = { idea = SRD_enemy_in_the_tunnels days = 45 }"),
    "coup": ("SRD_coup_unlocked", 120, "The Coup from Below",
             "Armed men climb out of the cellars of their district hall: the district becomes our subject. Needs "
             "them below 50% stability, at peace with us and without allies. Costs 120 political power.",
             "NOT = { has_war_with = ROOT } has_stability < 0.5 is_in_faction = no is_subject = no", None),
}


def neighbours(i):
    r, c = divmod(i, COLS)
    return [rr * COLS + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
            if 0 <= rr < ROWS and 0 <= cc < COLS]


def var(i):
    return f"SRD_tile_{i}"


def is_(i, *frames):
    return " ".join(f"check_variable = {{ {var(i)} = {f} }}" for f in frames)


# ---------------------------------------------------------------- sprites (drawn here, no pack art)
def _noise(w, h, seed, base, spread):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h, w))
    im = Image.fromarray(np.uint8(np.clip(128 + n * 40, 0, 255))).filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(im).astype(np.float32) / 255.0
    out = np.zeros((h, w, 4), np.uint8)
    for k in range(3):
        out[..., k] = np.clip(base[k] + (a - 0.5) * spread, 0, 255)
    out[..., 3] = 255
    return Image.fromarray(out, "RGBA")


def _frame(kind, seed):
    rock = _noise(TW, TH, seed, (92, 80, 66), 70)
    d = ImageDraw.Draw(rock)
    if kind == ROCK:
        for k in range(3):   # cracks
            x0 = 8 + 20 * k + seed % 7
            d.line([(x0, 6), (x0 + 6, 22), (x0 + 2, 40), (x0 + 9, 54)], fill=(58, 50, 42), width=1)
        return rock
    im = rock.copy()
    d = ImageDraw.Draw(im)
    if kind in (TUNNEL, DIGGING, RUINS, CACHE, CHAMBER, OPEN):   # the dug passage, with wooden props
        d.rectangle((6, 8, TW - 7, TH - 9), fill=(34, 28, 24))
        for x in (10, TW - 14):
            d.rectangle((x, 8, x + 4, TH - 9), fill=(120, 84, 46))
        d.rectangle((8, 8, TW - 9, 12), fill=(120, 84, 46))
    if kind == DIGGING:      # a lantern and a pickaxe
        d.ellipse((TW / 2 - 14, TH / 2 - 14, TW / 2 + 14, TH / 2 + 14), fill=(110, 84, 34))
        d.ellipse((TW / 2 - 6, TH / 2 - 6, TW / 2 + 6, TH / 2 + 6), fill=(250, 210, 110))
        d.line([(20, 46), (50, 18)], fill=(170, 130, 80), width=3)
        d.polygon([(44, 12), (58, 20), (52, 24)], fill=(190, 190, 200))
    elif kind == RUINS:      # a Roman column and a mosaic
        d.rectangle((30, 16, 42, 46), fill=(214, 204, 180))
        d.rectangle((26, 14, 46, 18), fill=(214, 204, 180))
        d.rectangle((26, 44, 46, 48), fill=(214, 204, 180))
        for k in range(4):
            d.rectangle((14 + 12 * k, 49, 22 + 12 * k, 52), fill=(160, 60, 40) if k % 2 else (40, 90, 140))
    elif kind == CACHE:      # crates
        for x, y in ((18, 30), (36, 30), (27, 16)):
            d.rectangle((x, y, x + 16, y + 14), fill=(140, 100, 52), outline=(70, 46, 22))
    elif kind == CHAMBER:    # the chamber under the Largo: lamps and Sredets' rhombuses
        d.rectangle((6, 8, TW - 7, TH - 9), fill=(60, 44, 30))
        cx, cy, q = TW / 2, TH / 2, 6
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            x, y = cx + dx * q * 1.3, cy + dy * q * 1.3
            d.polygon([(x, y - q), (x + q, y), (x, y + q), (x - q, y)], fill=(230, 50, 50))
    elif kind == FLOODED:
        d.rectangle((6, 8, TW - 7, TH - 9), fill=(30, 60, 92))
        for y in (20, 32, 44):
            d.arc((10, y - 6, 30, y + 6), 200, 340, fill=(120, 170, 210))
            d.arc((34, y - 6, 54, y + 6), 200, 340, fill=(120, 170, 210))
    elif kind in (DOOR, SEALED):
        d.rectangle((14, 6, TW - 15, TH - 5), fill=(70, 66, 62))
        d.rectangle((20, 10, TW - 21, TH - 5), fill=(96, 62, 34) if kind == DOOR else (110, 70, 56))
        if kind == DOOR:
            d.ellipse((TW - 30, TH / 2, TW - 25, TH / 2 + 5), fill=(220, 190, 90))
        else:                # bricked up: the district is gone
            for y in range(12, TH - 6, 7):
                for x in range(20 + (y // 7 % 2) * 6, TW - 21, 12):
                    d.rectangle((x, y, x + 10, y + 5), outline=(70, 40, 30))
    if kind == OPEN:         # the cellar door thrown open, light beyond
        d.rectangle((20, 10, TW - 21, TH - 9), fill=(240, 214, 140))
        d.polygon([(20, 10), (28, 14), (28, TH - 13), (20, TH - 9)], fill=(96, 62, 34))
    d.rectangle((0, 0, TW - 1, TH - 1), outline=(30, 26, 22))
    return im


def sprites():
    tiles = Image.new("RGBA", (TW * 10, TH), (0, 0, 0, 0))
    for f in range(1, 11):
        tiles.paste(_frame(f, f * 7), ((f - 1) * TW, 0))
    bg = _noise(WIN_W, WIN_H, 3, (40, 34, 30), 30)
    d = ImageDraw.Draw(bg)
    d.rectangle((0, 0, WIN_W - 1, WIN_H - 1), outline=(176, 140, 70), width=3)
    d.rectangle((6, 6, WIN_W - 7, 70), fill=(26, 22, 20))
    d.rectangle((GRID_X - 4, GRID_Y - 4, GRID_X + COLS * TW + 3, GRID_Y + ROWS * TH + 3), outline=(176, 140, 70), width=2)
    d.rectangle((PANEL_X, GRID_Y - 4, WIN_W - 14, GRID_Y + ROWS * TH + 3), fill=(28, 24, 22), outline=(176, 140, 70), width=2)
    clear = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    btn = Image.new("RGBA", (166, 34), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, 165, 33), 5, fill=(70, 50, 30), outline=(200, 160, 80), width=2)
    close = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
    dc = ImageDraw.Draw(close)
    dc.rounded_rectangle((0, 0, 27, 27), 4, fill=(90, 30, 26), outline=(200, 160, 80), width=2)
    dc.line([(8, 8), (20, 20)], fill=(240, 230, 210), width=3)
    dc.line([(20, 8), (8, 20)], fill=(240, 230, 210), width=3)
    return {"tunnel_tiles": tiles, "tunnels_bg": bg, "tunnel_clear": clear, "tunnels_btn": btn, "tunnels_close": close}


# ---------------------------------------------------------------- script
def build(write, write_dds, loc, L, names):
    """names: tag -> country name. loc: list to extend with localisation lines; L escapes a text."""
    for n, im in sprites().items():
        write_dds(f"gfx/interface/evil_sofia/{n}.dds", np.asarray(im))
    frames = {"tunnel_tiles": 10}
    write("interface/evil_sofia_tunnels.gfx", "spriteTypes = {\n" + "".join(
        f'\tspriteType = {{\n\t\tname = "GFX_SRD_{n}"\n\t\ttexturefile = "gfx/interface/evil_sofia/{n}.dds"\n'
        + (f"\t\tnoOfFrames = {frames[n]}\n" if n in frames else "") + "\t}\n"
        for n in ("tunnel_tiles", "tunnels_bg", "tunnel_clear", "tunnels_btn", "tunnels_close")) + "}\n")

    # the window
    els = [f'''\t\tinstantTextBoxType = {{ name = "title" position = {{ x = 24 y = 14 }} font = "hoi_20bs" text = "SRD_tunnels_title" maxWidth = 600 maxHeight = 28 format = left }}''',
           f'''\t\tinstantTextBoxType = {{ name = "stats" position = {{ x = 24 y = 44 }} font = "hoi_16mbs" text = "SRD_tunnels_stats" maxWidth = 700 maxHeight = 22 format = left }}''',
           f'''\t\tbuttonType = {{ name = "close" position = {{ x = {WIN_W - 44} y = 16 }} spriteType = "GFX_SRD_tunnels_close" pdx_tooltip = "SRD_tunnels_close_tt" }}''']
    for i in range(COLS * ROWS):
        r, c = divmod(i, COLS)
        x, y = GRID_X + c * TW, GRID_Y + r * TH
        tt = f"SRD_cellar_tt_{CELLARS[i]}" if i in CELLARS else ("SRD_largo_tt" if i == LARGO else "SRD_tile_tt")
        els.append(f'\t\ticonType = {{ name = "tile_{i}_icon" position = {{ x = {x} y = {y} }} spriteType = "GFX_SRD_tunnel_tiles" frame = 1 }}')
        els.append(f'\t\tbuttonType = {{ name = "tile_{i}" position = {{ x = {x} y = {y} }} spriteType = "GFX_SRD_tunnel_clear" pdx_tooltip = "{tt}" }}')
        if i in CELLARS:
            els.append(f'\t\tinstantTextBoxType = {{ name = "label_{i}" position = {{ x = {x} y = {y + TH - 15} }} font = "hoi_16mbs" '
                       f'text = "SRD_cellar_name_{CELLARS[i]}" maxWidth = {TW} maxHeight = 14 format = centre }}')
    els.append(f'\t\tinstantTextBoxType = {{ name = "panel_title" position = {{ x = {PANEL_X + 10} y = {GRID_Y + 6} }} font = "hoi_16mbs" text = "SRD_tunnels_selected" maxWidth = 170 maxHeight = 60 format = left }}')
    for k, a in enumerate(ACTIONS):
        els.append(f'\t\tbuttonType = {{ name = "{a}" position = {{ x = {PANEL_X + 8} y = {GRID_Y + 80 + 46 * k} }} spriteType = "GFX_SRD_tunnels_btn" '
                   f'buttonText = "SRD_tunnels_{a}" buttonFont = "hoi_16mbs" pdx_tooltip = "SRD_tunnels_{a}_tt" }}')
    els.append(f'\t\tinstantTextBoxType = {{ name = "help" position = {{ x = {PANEL_X + 10} y = {GRID_Y + 240} }} font = "hoi_16mbs" text = "SRD_tunnels_help" maxWidth = 168 maxHeight = 180 format = left }}')
    els.append(f'\t\tinstantTextBoxType = {{ name = "legend" position = {{ x = 24 y = {GRID_Y + ROWS * TH + 14} }} font = "hoi_16mbs" text = "SRD_tunnels_legend" maxWidth = {WIN_W - 48} maxHeight = 44 format = left }}')
    gui = f'''guiTypes = {{
\tcontainerWindowType = {{
\t\tname = "SRD_tunnels_window"
\t\tposition = {{ x = {-WIN_W // 2} y = {-WIN_H // 2} }}
\t\tsize = {{ width = {WIN_W} height = {WIN_H} }}
\t\torientation = center
\t\tmoveable = yes
\t\tbackground = {{ name = "bg" spriteType = "GFX_SRD_tunnels_bg" }}
{chr(10).join(els)}
\t}}
\tcontainerWindowType = {{
\t\tname = "SRD_tunnels_button_window"
\t\tposition = {{ x = -83 y = 78 }}
\t\tsize = {{ width = 166 height = 34 }}
\t\torientation = center_up
\t\tbuttonType = {{ name = "open" position = {{ x = 0 y = 0 }} spriteType = "GFX_SRD_tunnels_btn" buttonText = "SRD_tunnels_open" buttonFont = "hoi_16mbs" pdx_tooltip = "SRD_tunnels_open_tt" }}
\t}}
}}
'''
    write("interface/evil_sofia_tunnels.gui", gui)

    # the scripted GUIs: the button and the window
    props, effects, triggers = [], [], []
    for i in range(COLS * ROWS):
        props.append(f"\t\t\ttile_{i}_icon = {{ frame = {var(i)} }}")
        adj = " ".join(f"check_variable = {{ {var(j)} = {f} }}" for j in neighbours(i) for f in PASSABLE)
        exists = f"country_exists = {CELLARS[i]}" if i in CELLARS else ""
        triggers.append(f"""\t\t\ttile_{i}_click_enabled = {{
\t\t\t\tOR = {{
\t\t\t\t\t{is_(i, OPEN)}
\t\t\t\t\tAND = {{
\t\t\t\t\t\tOR = {{ {is_(i, ROCK, DOOR)} }}
\t\t\t\t\t\tOR = {{ {adj} }}
\t\t\t\t\t\tcheck_variable = {{ SRD_digging < SRD_dig_capacity }}
\t\t\t\t\t\thas_political_power > {DIG_COST - 1}
\t\t\t\t\t\t{exists}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}""")
        effects.append(f"""\t\t\ttile_{i}_click = {{
\t\t\t\tif = {{
\t\t\t\t\tlimit = {{ {is_(i, OPEN)} }}
\t\t\t\t\tset_variable = {{ SRD_selected = {i} }}
\t\t\t\t}}
\t\t\t\telse = {{
\t\t\t\t\tadd_political_power = -{DIG_COST}
\t\t\t\t\tset_variable = {{ {var(i)} = {DIGGING} }}
\t\t\t\t\tadd_to_variable = {{ SRD_digging = 1 }}
\t\t\t\t\tif = {{
\t\t\t\t\t\tlimit = {{ check_variable = {{ SRD_c_{i} = 4 }} }}
\t\t\t\t\t\tcountry_event = {{ id = evil_sofia_tunnels.{i + 1} days = {HARD_DAYS} }}
\t\t\t\t\t}}
\t\t\t\t\telse = {{ country_event = {{ id = evil_sofia_tunnels.{i + 1} days = {DIG_DAYS} }} }}
\t\t\t\t}}
\t\t\t}}""")
    for a, (flag, pp, label, tt, cond, eff) in ACTIONS.items():
        sel_ok = []
        for i, t in CELLARS.items():
            sel_ok.append(f"AND = {{ check_variable = {{ SRD_selected = {i} }} NOT = {{ has_country_flag = SRD_{a}_done_{t} }} "
                          f"{t} = {{ exists = yes {cond} }} }}")
        triggers.append(f"\t\t\t{a}_visible = {{ has_country_flag = {flag} }}")
        triggers.append(f"\t\t\t{a}_click_enabled = {{\n\t\t\t\thas_political_power > {pp - 1}\n\t\t\t\tOR = {{\n"
                        + "".join(f"\t\t\t\t\t{x}\n" for x in sel_ok) + "\t\t\t\t}\n\t\t\t}")
        branches = []
        for i, t in CELLARS.items():
            if a == "coup":
                act = (f"puppet = {t}\n{t} = {{ country_event = {{ id = evil_sofia_srd.24 }} "
                       f"news_event = {{ id = evil_sofia_news.20 hours = 6 }} }}")
            elif a == "strike":
                act = (f"{t} = {{ {eff} }}\nif = {{ limit = {{ NOT = {{ has_idea = SRD_through_the_tunnels }} }} "
                       f"add_timed_idea = {{ idea = SRD_through_the_tunnels days = 45 }} }}")
            else:
                act = f"{t} = {{ {eff} }}"
            branches.append(f"if = {{\n\tlimit = {{ check_variable = {{ SRD_selected = {i} }} }}\n\tset_country_flag = SRD_{a}_done_{t}\n"
                            + "".join(f"\t{ln}\n" for ln in act.split("\n")) + "}")
        body = f"add_political_power = -{pp}\n" + "\n".join(branches)
        effects.append(f"\t\t\t{a}_click = {{\n" + "".join(f"\t\t\t\t{ln}\n" for ln in body.split("\n")) + "\t\t\t}")
    gui_script = f"""scripted_gui = {{
\tSRD_tunnels_button = {{
\t\tcontext_type = player_context
\t\twindow_name = "SRD_tunnels_button_window"
\t\tvisible = {{ tag = SRD has_country_flag = SRD_tunnels_active }}
\t\teffects = {{
\t\t\topen_click = {{
\t\t\t\tif = {{ limit = {{ has_country_flag = SRD_tunnels_open }} clr_country_flag = SRD_tunnels_open }}
\t\t\t\telse = {{ set_country_flag = SRD_tunnels_open }}
\t\t\t}}
\t\t}}
\t}}
\tSRD_tunnels = {{
\t\tcontext_type = player_context
\t\twindow_name = "SRD_tunnels_window"
\t\tvisible = {{ tag = SRD has_country_flag = SRD_tunnels_active has_country_flag = SRD_tunnels_open }}
\t\tproperties = {{
{chr(10).join(props)}
\t\t}}
\t\teffects = {{
\t\t\tclose_click = {{ clr_country_flag = SRD_tunnels_open }}
{chr(10).join(effects)}
\t\t}}
\t\ttriggers = {{
{chr(10).join(triggers)}
\t\t}}
\t}}
}}
"""
    write("common/scripted_guis/evil_sofia_tunnels.txt", gui_script)

    # set-up: what lies in every tile (random each game), the chamber, the cellars
    setup = ["set_country_flag = SRD_tunnels_active", "set_variable = { SRD_digging = 0 }",
             "set_variable = { SRD_dug = 0 }", "set_variable = { SRD_breakthroughs = 0 }",
             "set_variable = { SRD_selected = -1 }",
             "if = { limit = { NOT = { has_variable = SRD_dig_capacity } } set_variable = { SRD_dig_capacity = 1 } }"]
    for i in range(COLS * ROWS):
        if i == LARGO:
            setup.append(f"set_variable = {{ {var(i)} = {CHAMBER} }}")
        elif i in CELLARS:
            setup.append(f"set_variable = {{ {var(i)} = {DOOR} }}")
        else:
            setup.append(f"set_variable = {{ {var(i)} = {ROCK} }}")
            setup.append("random_list = { " + " ".join(f"{w} = {{ set_variable = {{ SRD_c_{i} = {code} }} }}"
                                                        for w, code in CONTENTS) + " }")
    effects_file = "SRD_tunnels_setup = {\n" + "".join(f"\t{s}\n" for s in setup) + "}\n"

    # the events: one hidden event per tile finishes its digging; then the stories
    ev = ["add_namespace = evil_sofia_tunnels", ""]
    for i in range(COLS * ROWS):
        if i in CELLARS:
            t = CELLARS[i]
            body = f"""add_to_variable = {{ SRD_digging = -1 }}
if = {{
	limit = {{ country_exists = {t} }}
	set_variable = {{ {var(i)} = {OPEN} }}
	set_country_flag = SRD_tunnel_{t}
	add_to_variable = {{ SRD_breakthroughs = 1 }}
	set_variable = {{ SRD_last_break = {i} }}
	set_variable = {{ SRD_selected = {i} }}
	country_event = {{ id = evil_sofia_tunnels.101 }}
}}
else = {{ set_variable = {{ {var(i)} = {SEALED} }} }}"""
        elif i == LARGO:
            continue
        else:
            body = f"""add_to_variable = {{ SRD_digging = -1 }}
random_list = {{
	{CAVE_IN} = {{ set_variable = {{ {var(i)} = {ROCK} }} country_event = {{ id = evil_sofia_tunnels.100 }} }}
	{100 - CAVE_IN} = {{
		add_to_variable = {{ SRD_dug = 1 }}
		if = {{ limit = {{ check_variable = {{ SRD_c_{i} = 1 }} }} set_variable = {{ {var(i)} = {RUINS} }} country_event = {{ id = evil_sofia_tunnels.102 }} }}
		else_if = {{ limit = {{ check_variable = {{ SRD_c_{i} = 2 }} }} set_variable = {{ {var(i)} = {FLOODED} }} country_event = {{ id = evil_sofia_tunnels.103 }} }}
		else_if = {{ limit = {{ check_variable = {{ SRD_c_{i} = 3 }} }} set_variable = {{ {var(i)} = {CACHE} }} country_event = {{ id = evil_sofia_tunnels.104 }} }}
		else = {{ set_variable = {{ {var(i)} = {TUNNEL} }} }}
	}}
}}"""
        ev.append(f"country_event = {{\n\tid = evil_sofia_tunnels.{i + 1}\n\thidden = yes\n\tis_triggered_only = yes\n"
                  f"\timmediate = {{\n" + "".join(f"\t\t{ln}\n" for ln in body.split("\n")) + "\t}\n}\n")
    stories = {
        100: ("A Tunnel Caves In",
              "The props gave way at three in the morning. The new passage is full of earth again and a shift of miners "
              "is trapped behind it.",
              [("Dig them out, whatever it takes.", "add_manpower = -1000"), ("Seal the shaft and pay for new props.", "add_political_power = -25")]),
        101: ("Under [SRD_last_break_name]",
              "Our miners have broken through into a cellar: wine racks, coal sacks and nobody the wiser. We are under "
              "[SRD_last_break_name] now, and it does not know.\n\nSelect the open cellar in the Underground to see what "
              "we can do there.",
              [("Mark it on the map.", "")]),
        102: ("Roman Ruins",
              "The pickaxes hit marble: a street of Roman Serdica, a column still standing, a mosaic floor and a jar "
              "full of coins.",
              [("Sell the gold.", "add_political_power = 75"), ("Give it to the museum.", "add_stability = 0.03")]),
        103: ("The Tunnel Floods",
              "We hit an underground spring. By morning the new passage is under water, and it will stay that way. The "
              "miners will have to go around.",
              [("Go around it.", "")]),
        104: ("A Smugglers' Cache",
              "Behind a false wall: crates of rifles, left by smugglers in some earlier war and never collected.",
              [("Finders keepers.", "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1000 }")]),
    }
    for n, (title, desc, opts) in stories.items():
        loc.extend([f' evil_sofia_tunnels.{n}.t:0 "{L(title)}"', f' evil_sofia_tunnels.{n}.d:0 "{L(desc)}"'])
        o = []
        for k, (text, eff) in enumerate(opts):
            key = f"evil_sofia_tunnels.{n}.{'abc'[k]}"
            loc.append(f' {key}:0 "{L(text)}"')
            o.append(f"\toption = {{\n\t\tname = {key}\n" + (f"\t\t{eff}\n" if eff else "") + "\t}")
        ev.append(f"country_event = {{\n\tid = evil_sofia_tunnels.{n}\n\ttitle = evil_sofia_tunnels.{n}.t\n"
                  f"\tdesc = evil_sofia_tunnels.{n}.d\n\tis_triggered_only = yes\n" + "\n".join(o) + "\n}\n")
    write("events/evil_sofia_tunnels.txt", "\n".join(ev))

    # scripted localisation: the name of the selected and the last opened cellar
    def defined(name, varname, none):
        parts = [f"\ttext = {{ trigger = {{ check_variable = {{ {varname} = {i} }} }} localization_key = SRD_cellar_name_{t} }}"
                 for i, t in CELLARS.items()]
        return f"defined_text = {{\n\tname = {name}\n" + "\n".join(parts) + f"\n\ttext = {{ localization_key = {none} }}\n}}\n"
    sloc = defined("SRD_selected_name", "SRD_selected", "SRD_cellar_none") + defined("SRD_last_break_name", "SRD_last_break", "SRD_cellar_none")
    texts = {
        "SRD_tunnels_title": "The Underground of Serdica",
        "SRD_tunnels_stats": "Tunnels dug: [?SRD_dug|0]   Districts broken into: [?SRD_breakthroughs|0]   Miners at work: "
                             "[?SRD_digging|0] of [?SRD_dig_capacity|0]",
        "SRD_tunnels_selected": "Cellar: [SRD_selected_name]",
        "SRD_cellar_none": "none chosen",
        "SRD_tunnels_open": "The Underground",
        "SRD_tunnels_open_tt": "Open or close the Underground of Serdica: the tunnels under Sofia.",
        "SRD_tunnels_close_tt": "Close",
        "SRD_tile_tt": f"Rock. Click a rock next to our tunnels to dig it: {DIG_COST} political power, {DIG_DAYS} days "
                       f"({HARD_DAYS} in hard rock). Nobody knows what is inside until it is dug: earth, Roman ruins, a "
                       "smugglers' cache, or water that floods the way. Tunnels sometimes cave in.",
        "SRD_largo_tt": "The chamber under the Largo, among the ruins of Roman Serdica. Every tunnel starts here.",
        "SRD_tunnels_help": "Dig toward the cellar doors at the edges. Breaking into a cellar puts us under that "
                            "district; click the open cellar to choose it, then act. Each action works once per "
                            "district. Four districts broken into open The Ring under Sofia.",
        "SRD_tunnels_legend": "Rock (dig it)   Tunnel   Digging   Roman ruins   Flooded (blocked)   Smugglers' cache   "
                              "Cellar door (dig into it)   Open cellar (click it)   Bricked up (the district is gone)",
    }
    for a, (flag, pp, label, tt, cond, eff) in ACTIONS.items():
        texts[f"SRD_tunnels_{a}"] = label
        texts[f"SRD_tunnels_{a}_tt"] = tt
    for i, t in CELLARS.items():
        texts[f"SRD_cellar_name_{t}"] = names[t]
        texts[f"SRD_cellar_tt_{t}"] = (f"The cellars of {names[t]}. Dig into the door from a tunnel next to it to break "
                                       f"through ({DIG_COST} political power, {DIG_DAYS} days). Once it is open, click it "
                                       "to choose what to do there.")
    loc.extend(f' {k}:0 "{L(v)}"' for k, v in texts.items())
    return effects_file, sloc


def preview(path, names):
    """A picture of the window as it should look in the game, with a few tunnels dug (for the user)."""
    sp = sprites()
    win = sp["tunnels_bg"].copy()
    d = ImageDraw.Draw(win)
    tiles = sp["tunnel_tiles"]
    state = {i: ROCK for i in range(COLS * ROWS)}
    state[LARGO] = CHAMBER
    for i in CELLARS:
        state[i] = DOOR
    for i, f in {LARGO - 1: TUNNEL, LARGO + 1: TUNNEL, LARGO + COLS: RUINS, LARGO + 2 * COLS - 1: FLOODED,
                 LARGO - COLS: DIGGING, LARGO + COLS + 1: CACHE}.items():
        state[i] = f
    state[3 * COLS + 2] = OPEN
    for i, f in state.items():
        r, c = divmod(i, COLS)
        win.alpha_composite(tiles.crop(((f - 1) * TW, 0, f * TW, TH)), (GRID_X + c * TW, GRID_Y + r * TH))
        if i in CELLARS:
            d.text((GRID_X + c * TW + 4, GRID_Y + r * TH + TH - 14), names[CELLARS[i]][:11], fill=(250, 240, 210))
    d.text((24, 16), "The Underground of Serdica", fill=(240, 220, 170))
    d.text((24, 46), "Tunnels dug: 4   Districts broken into: 1   Miners at work: 1 of 2", fill=(220, 210, 190))
    d.text((PANEL_X + 10, GRID_Y + 8), "Cellar: Vazrazhdane", fill=(240, 220, 170))
    for k, a in enumerate(ACTIONS):
        win.alpha_composite(sp["tunnels_btn"], (PANEL_X + 8, GRID_Y + 80 + 46 * k))
        d.text((PANEL_X + 22, GRID_Y + 90 + 46 * k), ACTIONS[a][2], fill=(250, 240, 210))
    win.alpha_composite(sp["tunnels_close"], (WIN_W - 44, 16))
    win.save(path)
