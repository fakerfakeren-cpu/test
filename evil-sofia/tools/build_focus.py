"""Write the Sredets focus tree and everything it needs: events, the opinion modifier, Henry's trait, the Mimas
national spirit, the Red Guard divisions, the icons and their sprite files, and the texts.

Called at the end of tools/build_map.py with facts about the generated map. Icons:
- finished pack icons and the made ones are kept in tools/icons/ (committed), so the build only needs the GFX
  packs (DuoDex hoi4GFX, Ultimate HOI4 GFX) the first time an icon is used;
- portrait icons are made from tools/portraits/ (git-ignored) into gfx/interface/goals/evil_sofia/people/
  (git-ignored as well); without the portrait a pack icon stands in.
"""
import importlib.util
import os
import re
import sys
import numpy as np
from PIL import Image

DUO = os.environ.get("HOI4GFX_DUODEX", "/home/user/duodex/hoi4gfx")
ULT = os.environ.get("HOI4GFX_ULTIMATE", "/home/user/globvs/ultimate-hoi4-gfx")
FRAMES = os.path.join(DUO, "Focus Backgrounds", "Even More Background", "Backgrounds PNG")
PIECES = os.path.join(ULT, "Focus & National Spirits Pieces")

SHINE = """	SpriteType = {{
		name = "{name}_shine"
		texturefile = "{tex}"
		effectFile = "gfx/FX/buttonstate.lua"
		animation = {{
			animationmaskfile = "{tex}"
			animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
			animationrotation = -90.0
			animationlooping = no
			animationtime = 0.75
			animationdelay = 0
			animationblendmode = "add"
			animationtype = "scrolling"
			animationrotationoffset = {{ x = 0.0 y = 0.0 }}
			animationtexturescale = {{ x = 1.0 y = 1.0 }}
		}}
		animation = {{
			animationmaskfile = "{tex}"
			animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
			animationrotation = 90.0
			animationlooping = no
			animationtime = 0.75
			animationdelay = 0
			animationblendmode = "add"
			animationtype = "scrolling"
			animationrotationoffset = {{ x = 0.0 y = 0.0 }}
			animationtexturescale = {{ x = 1.0 y = 1.0 }}
		}}
		legacy_lazy_load = no
	}}"""


def _pack_icon(name):
    for root in ("goals", "focuses", "Grestin's Icon Pack/Completed Icons"):
        for dp, dn, fn in os.walk(os.path.join(DUO, root)):
            for f in fn:
                if os.path.splitext(f)[0] == name and f.lower().endswith((".tga", ".dds", ".png")):
                    return Image.open(os.path.join(dp, f)).convert("RGBA")
    raise FileNotFoundError(f"icon {name} not in the DuoDex pack at {DUO}")


def _piece(name):
    return Image.open(os.path.join(PIECES, name)).convert("RGBA")


def _fit(im, w, h):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im


def _custom(key):
    """Icons put together from pack frames and pieces."""
    if key == "doner":       # a döner: bread, a knife and the fire, in a red ring
        frame = Image.open(os.path.join(FRAMES, "RedWheatFrame.png")).convert("RGBA")
        canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        disc = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(disc).ellipse((26, 18, 74, 66), fill=(70, 30, 16, 255))
        canvas.alpha_composite(disc)
        canvas.alpha_composite(frame)
        fire = _fit(_piece("Fire.png"), 40, 34)
        canvas.alpha_composite(fire, (50 - fire.width // 2, 44 - fire.height // 2))
        bread = _fit(_piece("Bread.png"), 44, 30)
        canvas.alpha_composite(bread, (50 - bread.width // 2, 40 - bread.height // 2))
        knife = _fit(_piece("Knife2.png").rotate(-30, expand=True), 34, 34)
        canvas.alpha_composite(knife, (58 - knife.width // 2, 34 - knife.height // 2))
        return canvas
    if key == "stadium":     # soldiers in rows in a laurel frame
        frame = Image.open(os.path.join(FRAMES, "LeavedFrame.png")).convert("RGBA")
        canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        from PIL import ImageDraw
        disc = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        ImageDraw.Draw(disc).ellipse((24, 14, 76, 66), fill=(120, 24, 24, 255))
        canvas.alpha_composite(disc)
        canvas.alpha_composite(frame)
        rows = _fit(_piece("Soldiers in Rows.png"), 50, 30)
        canvas.alpha_composite(rows, (50 - rows.width // 2, 44 - rows.height // 2))
        star = _fit(_piece("Star Red.png"), 18, 18)
        canvas.alpha_composite(star, (50 - star.width // 2, 20))
        return canvas
    if key == "idea_doner":  # national spirit icon
        from PIL import ImageDraw
        canvas = Image.new("RGBA", (60, 68), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).rounded_rectangle((2, 2, 57, 65), 6, fill=(80, 26, 16, 255), outline=(190, 150, 80, 255), width=2)
        fire = _fit(_piece("Fire.png"), 34, 30)
        canvas.alpha_composite(fire, (30 - fire.width // 2, 40 - fire.height // 2))
        bread = _fit(_piece("Bread.png"), 40, 28)
        canvas.alpha_composite(bread, (30 - bread.width // 2, 34 - bread.height // 2))
        return canvas
    raise KeyError(key)


def _idea_icon(background, piece):
    """National spirit icon: a pack background (60x68) with a piece in the middle."""
    bg = Image.open(os.path.join(ULT, "National Spirit Backgrounds", background)).convert("RGBA")
    canvas = Image.new("RGBA", (64, 68), (0, 0, 0, 0))
    canvas.alpha_composite(bg, ((64 - bg.width) // 2, (68 - bg.height) // 2))
    p = _fit(_piece(piece), 42, 42)
    canvas.alpha_composite(p, (32 - p.width // 2, 34 - p.height // 2))
    return canvas


def build(root, facts, write, write_dds):
    spec = importlib.util.spec_from_file_location("tree", os.path.join(root, "tools", "focus_sredets.py"))
    tree = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tree)
    sys.path.insert(0, os.path.join(root, "tools"))
    import focus_icons
    tag = tree.TAG
    states, capital = facts["states"], facts["capital_state"]

    def cores(t):
        return "\n".join(f"add_state_core = {s['id']}" for s in states if s["owner"] == t)

    def owned_or(tags):
        return " ".join(f"is_owned_by = {t}" for t in tags)

    fill = {"{OBR_CAP}": str(capital["OBR"]), "{VIT_CAP}": str(capital["VIT"])}

    def gone(t):
        return f"OR = {{ NOT = {{ country_exists = {t} }} {t} = {{ has_capitulated = yes }} }}"

    def filled(text):
        for k, v in fill.items():
            text = text.replace(k, v)
        text = re.sub(r"\{CORES:([A-Z,]+)\}", lambda m: "\n".join(cores(t) for t in m.group(1).split(",")), text)
        text = re.sub(r"\{WAR:([A-Z,]+)\}", lambda m: "\n".join(
            f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} }} "
            f"create_wargoal = {{ type = annex_everything target = {t} }} }}" for t in m.group(1).split(",")), text)
        text = re.sub(r"\{BEATEN:([A-Z,]+)\}", lambda m: "\n".join(gone(t) for t in m.group(1).split(",")), text)
        return text

    def indent(text, n):
        return "\n".join("\t" * n + ln if ln.strip() else ln for ln in text.split("\n"))

    # ---------------------------------------------------------------- icons
    cache = os.path.join(root, "tools", "icons")
    os.makedirs(cache, exist_ok=True)
    sprites, loc = [], ["l_english:"]
    for fid, name, x, y, pre, mx, weeks, icon, avail, reward, desc in tree.FOCUSES:
        kind, _, key = icon.partition(":")
        sprite = f"GFX_focus_{tag}_{fid}"
        if kind == "person":
            ptag, frame, piece, rot, opts = tree.PERSON_ICONS[key]
            portrait = os.path.join(root, "tools", "portraits", f"{ptag}.png")
            if os.path.exists(portrait) and os.path.isdir(FRAMES):
                pim = Image.open(portrait)
                if pim.width > 400:
                    pim = pim.resize((400, int(pim.height * 400 / pim.width)), Image.LANCZOS)
                front = _piece(piece) if piece else None
                if front is not None and rot:
                    front = front.rotate(rot, expand=True, resample=Image.BICUBIC)
                im = focus_icons.person_icon(Image.open(os.path.join(FRAMES, frame)), pim, front,
                                             bust_width=1.1, head_room=0.04, **opts)
                tex = f"gfx/interface/goals/evil_sofia/people/{tag}_{fid}.dds"
            else:
                kind, key = "duo", tree.PERSON_FALLBACK[key]
        if kind in ("duo", "custom"):
            cached = os.path.join(cache, f"{kind}_{key}.png".replace(" ", "_"))
            if os.path.exists(cached):
                im = Image.open(cached).convert("RGBA")
            else:
                im = _pack_icon(key) if kind == "duo" else _custom(key)
                im.save(cached)
            tex = f"gfx/interface/goals/evil_sofia/{tag}_{fid}.dds"
        write_dds(tex, np.asarray(im.convert("RGBA")))
        sprites.append((sprite, tex))
        loc += [f' {tag}_{fid}:0 "{name}"', f' {tag}_{fid}_desc:0 "{desc}"']
    write("interface/evil_sofia_goals.gfx", "spriteTypes = {\n" + "".join(
        f'\tspriteType = {{\n\t\tname = "{n}"\n\t\ttexturefile = "{t}"\n\t}}\n' for n, t in sprites) + "}\n")
    write("interface/evil_sofia_goals_shine.gfx", "spriteTypes = {\n" + "\n".join(
        SHINE.format(name=n, tex=t) for n, t in sprites) + "\n}\n")

    # ---------------------------------------------------------------- the focus tree
    blocks = []
    for fid, name, x, y, pre, mx, weeks, icon, avail, reward, desc in tree.FOCUSES:
        parts = [f"\t\tid = {tag}_{fid}", f"\t\ticon = GFX_focus_{tag}_{fid}", f"\t\tx = {x}", f"\t\ty = {y}"]
        for group in pre:
            parts.append("\t\tprerequisite = { " + " ".join(f"focus = {tag}_{q}" for q in group) + " }")
        if mx:
            parts.append("\t\tmutually_exclusive = { " + " ".join(f"focus = {tag}_{q}" for q in mx) + " }")
        if avail:
            parts.append("\t\tavailable = {\n" + indent(filled(avail), 3) + "\n\t\t}")
        parts += [f"\t\tcost = {weeks}", "\t\tai_will_do = { factor = 1 }",
                  "\t\tcompletion_reward = {\n" + indent(filled(reward), 3) + "\n\t\t}"]
        blocks.append("\tfocus = {\n" + "\n".join(parts) + "\n\t}")
    write(f"common/national_focus/evil_sofia_{tag}.txt", f"""focus_tree = {{
\tid = evil_sofia_{tag}_focus
\tcountry = {{
\t\tfactor = 0
\t\tmodifier = {{
\t\t\tadd = 20
\t\t\ttag = {tag}
\t\t}}
\t}}
\tdefault = no
\tcontinuous_focus_position = {{ x = 50 y = {(max(f[3] for f in tree.FOCUSES) + 1) * 130 + 60} }}

{chr(10).join(blocks)}
}}
""")

    # ---------------------------------------------------------------- events, opinion, traits, ideas, units
    ev = ["add_namespace = evil_sofia_srd", ""]
    for num, (title, desc, options) in tree.EVENTS.items():
        opts = []
        for i, (text, effect, chance) in enumerate(options):
            key = f"evil_sofia_srd.{num}.{'abcdef'[i]}"
            loc.append(f' {key}:0 "{text}"')
            body = ("\n" + indent(effect, 2)) if effect else ""
            opts.append(f"\toption = {{\n\t\tname = {key}\n\t\tai_chance = {{ factor = {chance} }}{body}\n\t}}")
        loc += [f' evil_sofia_srd.{num}.t:0 "{title}"', f' evil_sofia_srd.{num}.d:0 "{desc}"']
        ev.append(f"country_event = {{\n\tid = evil_sofia_srd.{num}\n\ttitle = evil_sofia_srd.{num}.t\n"
                  f"\tdesc = evil_sofia_srd.{num}.d\n\tis_triggered_only = yes\n" + "\n".join(opts) + "\n}\n")
    write("events/evil_sofia_srd.txt", "\n".join(ev))
    write("common/opinion_modifiers/evil_sofia.txt",
          "opinion_modifiers = {\n\tevil_sofia_dirty_communists = {\n\t\tvalue = -100\n\t}\n}\n")
    loc.append(' evil_sofia_dirty_communists:0 "Dirty communists!"')
    write("common/country_leader/evil_sofia_traits.txt", "leader_traits = {\n" + "".join(
        f"\t{k} = {{\n\t\trandom = no\n{indent(mods, 2)}\n\t}}\n" for k, (n, d, mods) in tree.TRAITS.items()) + "}\n")
    for k, (n, d, mods) in tree.TRAITS.items():
        loc += [f' {k}:0 "{n}"', f' {k}_desc:0 "{d}"']
    ideas, idea_sprites = [], []
    for k, (n, d, mods, icon) in tree.IDEAS.items():
        ideas.append(f"\t\t{k} = {{\n\t\t\tpicture = {k}\n\t\t\tallowed = {{ always = no }}\n"
                     f"\t\t\tmodifier = {{\n{indent(mods, 4)}\n\t\t\t}}\n\t\t}}\n")
        name = icon.partition(":")[2] if isinstance(icon, str) else "idea_" + k
        cached = os.path.join(cache, f"custom_{name}.png")
        if os.path.exists(cached):
            im = Image.open(cached).convert("RGBA")
        else:
            im = _custom(name) if isinstance(icon, str) else _idea_icon(*icon)
            im.save(cached)
        tex = f"gfx/interface/ideas/evil_sofia/{k}.dds"
        write_dds(tex, np.asarray(im))
        idea_sprites.append((f"GFX_idea_{k}", tex))
        loc += [f' {k}:0 "{n}"', f' {k}_desc:0 "{d}"']
    write("common/ideas/evil_sofia_ideas.txt", "ideas = {\n\tcountry = {\n" + "".join(ideas) + "\t}\n}\n")
    write("interface/evil_sofia_ideas.gfx", "spriteTypes = {\n" + "".join(
        f'\tspriteType = {{\n\t\tname = "{n}"\n\t\ttexturefile = "{t}"\n\t}}\n' for n, t in idea_sprites) + "}\n")
    divisions = "\n".join(f"""\tdivision = {{
\t\tname = "{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'} Vasil Levski Red Guard"
\t\tlocation = {facts['stadium_province']}
\t\tdivision_template = "City Guard"
\t\tstart_experience_factor = 0.3
\t\tstart_equipment_factor = 1.0
\t}}""" for i in range(1, 5))
    write(f"history/units/{tag}_red_guards.txt", f"units = {{\n{divisions}\n}}\n")
    for k, v in tree.FACTIONS.items():
        loc.append(f' {k}:0 "{v}"')
    # decisions
    cat, cname, cdesc, cvis = tree.DECISIONS["category"]
    write("common/decisions/categories/evil_sofia.txt", f"""{cat} = {{
\tallowed = {{ tag = {tag} }}
\tvisible = {{
{indent(cvis, 2)}
\t}}
}}
""")
    loc += [f' {cat}:0 "{cname}"', f' {cat}_desc:0 "{cdesc}"']
    dec = []
    for did, dname, cost, cooldown, avail, effect in tree.DECISIONS["decisions"]:
        re_en = f"\n\t\tdays_re_enable = {cooldown}" if cooldown else ""
        dec.append(f"""\t{did} = {{
\t\tcost = {cost}{re_en}
\t\tavailable = {{
{indent(avail, 3)}
\t\t}}
\t\tcomplete_effect = {{
{indent(effect, 3)}
\t\t}}
\t\tai_will_do = {{ factor = 1 }}
\t}}""")
        loc.append(f' {did}:0 "{dname}"')
    write("common/decisions/evil_sofia_SRD.txt", f"{cat} = {{\n" + "\n".join(dec) + "\n}\n")
    # flags: hand-drawn communist flags (tools/red_flags.py), only for the countries that can go red
    import red_flags

    def save_flag(name, im):
        for folder, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
            im.resize(size, Image.LANCZOS).save(os.path.join(root, "gfx", "flags", f"{folder}{name}.tga"))

    for folder in ("", "medium/", "small/"):        # communist flags of earlier builds for every district
        d = os.path.join(root, "gfx", "flags", folder)
        for f in os.listdir(d):
            if f.endswith("_communism.tga") and f[:3] not in tree.RED_COUNTRIES:
                os.remove(os.path.join(d, f))
    for t in tree.RED_COUNTRIES:
        save_flag(f"{t}_communism", red_flags.make(root, "district", t))
        nm = facts["countries"][t]
        loc += [f' {t}_communism:0 "{nm} Commune"', f' {t}_communism_DEF:0 "the {nm} Commune"']
    cosm = []
    for ct, (nm, adj, colour, (recipe, arg)) in tree.COSMETIC.items():
        save_flag(ct, red_flags.make(root, recipe, arg))
        r_, g_, b_ = colour
        cosm.append(f"{ct} = {{\n\tcolor = rgb {{ {r_} {g_} {b_} }}\n\tcolor_ui = rgb {{ {min(255, r_ + 40)} {min(255, g_ + 40)} {min(255, b_ + 40)} }}\n}}")
        loc += [f' {ct}:0 "{nm}"', f' {ct}_DEF:0 "{nm}"', f' {ct}_ADJ:0 "{adj}"']
    write("common/countries/cosmetic.txt", "\n".join(cosm) + "\n")
    write("localisation/english/replace/evil_sofia_focus_l_english.yml", "\n".join(loc) + "\n", bom=True)
    return len(tree.FOCUSES)
