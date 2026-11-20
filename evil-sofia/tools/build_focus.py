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
    import decisions_world
    tag = tree.TAG
    states, capital = facts["states"], facts["capital_state"]

    def start_states(tags):
        return [s_["id"] for s_ in states if s_["owner"] in tags]

    fill = {"{OBR_CAP}": str(capital["OBR"]), "{VIT_CAP}": str(capital["VIT"])}

    def claims(tags):
        return "\n".join(f"add_state_claim = {i}" for i in start_states(tags))

    def core_held(t, tags):
        ids = " ".join(f"state = {i}" for i in start_states(tags))
        return f"every_state = {{\n\tlimit = {{ OR = {{ {ids} }} is_controlled_by = {t} }}\n\tadd_core_of = {t}\n}}"

    def held(tags):
        return "\n".join(f"{i} = {{ OR = {{ is_controlled_by = ROOT controller = {{ is_in_faction_with = ROOT }} }} }}"
                         for i in start_states(tags))

    def state_id(tag_, name):
        ids = [s_["id"] for s_ in states if s_["owner"] == tag_ and s_["name"] == name]
        assert len(ids) == 1, f"no single state {name} of {tag_}: {ids}"
        return str(ids[0])

    def filled(text):
        for k, v in fill.items():
            text = text.replace(k, v)
        text = re.sub(r"\{STATE:([A-Z]+):([^{}:]+)\}", lambda m: state_id(m.group(1), m.group(2)), text)
        text = re.sub(r"\{CLAIMS:([A-Z,]+)\}", lambda m: claims(m.group(1).split(",")), text)
        text = re.sub(r"\{COREALL:([A-Z]+):([A-Z,]+)\}", lambda m: (   # the free centre: cores at once
            f"every_state = {{\n\tlimit = {{ OR = {{ {' '.join(f'state = {i}' for i in start_states(m.group(2).split(',')))} }} }}\n"
            f"\tadd_core_of = {m.group(1)}\n}}"), text)
        text = re.sub(r"\{COREHELD:([A-Z]+):([A-Z,]+)\}", lambda m: core_held(m.group(1), m.group(2).split(",")), text)
        text = re.sub(r"\{HELD:([A-Z,]+)\}", lambda m: held(m.group(1).split(",")), text)
        text = re.sub(r"\{INVITE:([A-Z]+)\}", lambda m: (
            f"if = {{\n\tlimit = {{ country_exists = {m.group(1)} NOT = {{ is_in_faction_with = {m.group(1)} "
            f"has_war_with = {m.group(1)} }} }}\n\t{m.group(1)} = {{ country_event = {{ id = evil_sofia_srd.11 }} }}\n}}"), text)
        text = re.sub(r"\{CALL:([A-Z]+)\}", lambda m: (     # the C Class Hools call an old classmate
            f"if = {{\n\tlimit = {{ country_exists = {m.group(1)} NOT = {{ has_war_with = {m.group(1)} }} "
            f"{m.group(1)} = {{ is_in_faction = no }} }}\n\t{m.group(1)} = {{ country_event = {{ id = evil_sofia_srd.25 }} }}\n}}"), text)
        text = re.sub(r"\{OFFER_PARTS:([A-Z]+)\}", lambda m: (
            f"if = {{\n\tlimit = {{ country_exists = {m.group(1)} NOT = {{ has_war_with = {m.group(1)} }} }}\n"
            f"\t{m.group(1)} = {{ country_event = {{ id = evil_sofia_srd.20 }} }}\n}}"), text)
        text = re.sub(r"\{OFFER:([A-Z]+)\}", lambda m: (
            f"if = {{\n\tlimit = {{ country_exists = {m.group(1)} NOT = {{ has_war_with = {m.group(1)} }} }}\n"
            f"\t{m.group(1)} = {{ country_event = {{ id = evil_sofia_srd.17 }} }}\n}}"), text)
        text = re.sub(r"\{WAR:([A-Z,]+)\}", lambda m: "\n".join(
            f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} is_in_faction_with = {t} }} }} "
            f"create_wargoal = {{ type = annex_everything target = {t} }} }}" for t in m.group(1).split(",")), text)
        assert "{" + "CORES" not in text and not re.search(r"\{[A-Z_]+:", text), text
        return text

    def L(text):
        """A localisation value: line breaks as the game writes them, no stray quotes."""
        return text.replace("\n", "\\n").replace('"', "'")

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
        if kind == "photo":
            src, frame, box, piece = tree.PHOTO_ICONS[key]
            photo = os.path.join(root, "tools", "portraits", f"{src}.png")
            if os.path.exists(photo) and os.path.isdir(FRAMES):
                im = focus_icons.photo_icon(Image.open(os.path.join(FRAMES, frame)), Image.open(photo), box,
                                            _piece(piece) if piece else None)
                tex = f"gfx/interface/goals/evil_sofia/people/{tag}_{fid}.dds"
            else:
                kind, key = "duo", tree.PHOTO_FALLBACK[key]
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
        loc += [f' {tag}_{fid}:0 "{L(name)}"', f' {tag}_{fid}_desc:0 "{L(desc)}"']
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
        parts += [f"\t\tcost = {weeks}",
                  "\t\tsearch_filters = { " + " ".join(f"FOCUS_FILTER_{f}" for f in tree.FILTERS[fid]) + " }",
                  "\t\tai_will_do = { factor = 1 }",
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

    # ---------------------------------------------------------------- events, pictures, opinion, traits
    import event_pictures
    import events_world
    import texts
    pictures = {}

    own_pictures = os.path.join(root, "tools", "event_pictures")
    wanted = []

    def picture(kind, spec, key):
        flags, mood = spec
        name = f"GFX_evil_sofia_{key}"
        if name not in pictures:
            own = os.path.join(own_pictures, f"{key}.png")
            tex = f"gfx/event_pictures/evil_sofia/{key}.dds"
            if kind == "country" and not os.path.exists(own):
                return None        # private events: no drawn picture, only the user's own (the user's choice)
            if os.path.exists(own):        # a picture made for this event: cropped to the frame's shape
                im = event_pictures.fit(Image.open(own), kind)
                tex = f"gfx/event_pictures/evil_sofia/own/{key}.dds"     # the user's pictures stay out of git
            else:
                im = event_pictures.picture(kind, [event_pictures.flag_image(root, f) for f in flags], mood,
                                            seed=sum(map(ord, key)))
            write_dds(tex, np.asarray(im))
            pictures[name] = tex
        return name

    def events(namespace, items, kind="country", major=False, mtth=False):
        out = [f"add_namespace = {namespace}", ""]
        for num, ev in items.items():
            title, desc, pic = ev[0], ev[1], ev[2]
            options = ev[-1]
            eid = f"{namespace}.{num}"
            opts = []
            for i, opt in enumerate(options):
                text, effect, chance = opt[:3]
                trig = opt[3] if len(opt) > 3 else ""
                key = f"{eid}.{'abcdef'[i]}"
                loc.append(f' {key}:0 "{L(text)}"')
                body = ("\n\t\ttrigger = {\n" + indent(trig, 3) + "\n\t\t}") if trig else ""
                body += ("\n" + indent(filled(effect), 2)) if effect else ""
                ai = (f"ai_chance = {{\n{indent(chance, 3)}\n\t\t}}" if isinstance(chance, str)
                      else f"ai_chance = {{ factor = {chance} }}")
                opts.append(f"\toption = {{\n\t\tname = {key}\n\t\t{ai}{body}\n\t}}")
            loc.extend([f' {eid}.t:0 "{L(title)}"', f' {eid}.d:0 "{L(desc)}"'])
            wanted.append((eid.replace(".", "_"), kind, title))
            pic_name = picture(kind, pic, eid.replace('.', '_'))
            head = [f"\tid = {eid}", f"\ttitle = {eid}.t", f"\tdesc = {eid}.d"] + (
                [f"\tpicture = {pic_name}"] if pic_name else [])
            if major:
                head.append("\tmajor = yes")
            if mtth:
                days, trig = ev[3], ev[4]
                flag = f"{eid.replace('.', '_')}_happened"
                head += ["\ttrigger = {", "\t\texists = yes",
                         f"\t\tNOT = {{ has_country_flag = {flag} has_country_flag = {namespace}_cooldown }}"] + ([indent(trig, 2)] if trig else []) + ["\t}",
                         f"\tmean_time_to_happen = {{ days = {days} }}",
                         f"\timmediate = {{\n\t\tset_country_flag = {flag}\n"
                         f"\t\tset_country_flag = {{ flag = {namespace}_cooldown days = 730 }}\n\t}}"]
            else:
                head.append("\tis_triggered_only = yes")
            out.append(f"{kind}_event = {{\n" + "\n".join(head) + "\n" + "\n".join(opts) + "\n}\n")
        return "\n".join(out)

    write("events/evil_sofia_srd.txt", events("evil_sofia_srd", tree.EVENTS))
    write("events/evil_sofia_news.txt", events("evil_sofia_news", events_world.NEWS, "news", major=True))
    write("events/evil_sofia_flavour.txt", events("evil_sofia_flavour", events_world.FLAVOUR, mtth=True))
    briefs = importlib.util.spec_from_file_location("briefs", os.path.join(root, "tools", "picture_briefs.py"))
    pb = importlib.util.module_from_spec(briefs)
    briefs.loader.exec_module(pb)
    lines = [pb.HEADER]
    for key, kind, title in wanted:
        w, h = event_pictures.SIZES[kind]
        done = "done" if os.path.exists(os.path.join(own_pictures, f"{key}.png")) else "wanted"
        lines.append(f"| `{key}.png` | {w}x{h} | {title} | {pb.BRIEFS.get(key, '')} | {done} |")
    with open(os.path.join(own_pictures, "PICTURES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    write("interface/evil_sofia_events.gfx", "spriteTypes = {\n" + "".join(
        f'\tspriteType = {{\n\t\tname = "{n}"\n\t\ttexturefile = "{t}"\n\t}}\n' for n, t in pictures.items()) + "}\n")
    write("common/opinion_modifiers/evil_sofia.txt", "opinion_modifiers = {\n"
          "\tevil_sofia_dirty_communists = {\n\t\tvalue = -100\n\t}\n"
          "\tevil_sofia_day_ones = {\n\t\tvalue = 100\n\t}\n"
          "\tevil_sofia_gang = {\n\t\tvalue = 50\n\t}\n"
          "\tevil_sofia_free_friends = {\n\t\tvalue = 30\n\t}\n"
          "\tevil_sofia_mom_was_wrong = {\n\t\tvalue = 40\n\t}\n}\n")
    loc += [' evil_sofia_dirty_communists:0 "Dirty communists!"', ' evil_sofia_day_ones:0 "Day ones"',
            ' evil_sofia_gang:0 "The Evil Gang"',
            ' evil_sofia_free_friends:0 "Friends of Freedom"', ' evil_sofia_mom_was_wrong:0 "Mom was wrong"']
    all_traits = dict(tree.TRAITS)
    all_traits.update({k: (n, d, mods) for k, (n, d, mods, slot) in texts.ADVISOR_TRAITS.items()})
    # default military advisors for every country (tools/military_advisors.py)
    import military_advisors as mil
    all_traits.update({k: (n, d, mods) for k, (n, d, mods, slot, cost) in mil.TRAITS.items()})
    mil_blocks = []
    for cid, cname, ctag, trait in mil.advisors(sorted(facts["countries"])):
        slot, cost = mil.TRAITS[trait][3], mil.TRAITS[trait][4]
        mil_blocks.append(f"\t{cid} = {{\n\t\tname = {cid}\n\t\tadvisor = {{\n\t\t\tslot = {slot}\n"
                          f"\t\t\tidea_token = {cid}\n\t\t\tallowed = {{ original_tag = {ctag} }}\n"
                          f"\t\t\ttraits = {{ {trait} }}\n\t\t\tcost = {cost}\n\t\t\tai_will_do = {{ factor = 1 }}\n"
                          f"\t\t}}\n\t}}")
        loc.append(f' {cid}:0 "{cname}"')
    write("common/characters/evil_sofia_military.txt", "characters = {\n" + "\n".join(mil_blocks) + "\n}\n")
    write("common/country_leader/evil_sofia_traits.txt", "leader_traits = {\n" + "".join(
        f"\t{k} = {{\n\t\trandom = no\n{indent(mods, 2)}\n\t\tai_will_do = {{ factor = 1 }}\n\t}}\n"
        for k, (n, d, mods) in all_traits.items()) + "}\n")
    for k, (n, d, mods) in all_traits.items():
        loc += [f' {k}:0 "{L(n)}"', f' {k}_desc:0 "{L(d)}"']
    ideas, idea_sprites = [], []
    for k, (n, d, mods, icon, *extra) in {**tree.IDEAS, **decisions_world.IDEAS}.items():
        extra = ("\n" + indent(extra[0], 3)) if extra else ""
        ideas.append(f"\t\t{k} = {{\n\t\t\tpicture = {k}\n\t\t\tallowed = {{ always = no }}{extra}\n"
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
        loc += [f' {k}:0 "{L(n)}"', f' {k}_desc:0 "{L(d)}"']
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
    # decisions: the Sredets tree's own (the Oborishte Question, the Road to Power) and basic ones for everyone
    cat, cname, cdesc, cvis = tree.DECISIONS["category"]
    srd_cats = [(cat, cname, cdesc, f"tag = {tag}", cvis, [
        dict(id=did, name=dname, desc=ddesc, cost=cost, cooldown=cooldown, visible="", available=avail,
             effect=effect, ai="factor = 1", icon="generic_political_discourse")
        for did, dname, ddesc, cost, cooldown, avail, effect in tree.DECISIONS["decisions"]]), tree.GRIP_DECISIONS]

    def decision_files(cats):
        cat_blocks, files = [], []
        for key, name, desc, allowed, visible, decs in cats:
            cat_blocks.append(f"{key} = {{\n\tallowed = {{\n{indent(allowed, 2)}\n\t}}\n"
                              f"\tvisible = {{\n{indent(visible, 2)}\n\t}}\n}}\n")
            loc.extend([f' {key}:0 "{L(name)}"', f' {key}_desc:0 "{L(desc)}"'])
            out = []
            for d_ in decs:
                d_ = {"cooldown": 0, "visible": "", "ai": "factor = 1", "extra": "", **d_}
                re_en = f"\n\t\tdays_re_enable = {d_['cooldown']}" if d_["cooldown"] else ""
                vis = f"\n\t\tvisible = {{\n{indent(d_['visible'], 3)}\n\t\t}}" if d_["visible"] else ""
                out.append(f"""\t{d_['id']} = {{
\t\ticon = {d_['icon']}
\t\tcost = {d_['cost']}{re_en}{vis}{("\n" + indent(d_["extra"], 2)) if d_["extra"] else ""}
\t\tavailable = {{
{indent(d_['available'], 3)}
\t\t}}
\t\tcomplete_effect = {{
{indent(d_['effect'], 3)}
\t\t}}
\t\tai_will_do = {{
{indent(d_['ai'], 3)}
\t\t}}
\t}}""")
                loc.extend([f' {d_["id"]}:0 "{L(d_["name"])}"', f' {d_["id"]}_desc:0 "{L(d_["desc"])}"'])
            files.append(f"{key} = {{\n" + "\n".join(out) + "\n}\n")
        return "".join(cat_blocks), "".join(files)

    c1, f1 = decision_files(srd_cats)
    c2, f2 = decision_files(decisions_world.CATEGORIES)
    write("common/decisions/categories/evil_sofia.txt", c1 + c2)
    write("common/decisions/evil_sofia_generic.txt", f2)
    write("common/decisions/evil_sofia_SRD.txt", f1)
    # scripted effects (the Grip on the Centre) and Sredets' own monthly on_action (a second on_actions file;
    # the game merges it with the one build_map.py writes)
    write("common/scripted_effects/evil_sofia_effects.txt", "".join(
        f"{k} = {{\n{indent(v, 1)}\n}}\n" for k, v in tree.SCRIPTED_EFFECTS.items()))
    write("common/on_actions/evil_sofia_srd_on_actions.txt",
          f"on_actions = {{\n\ton_monthly = {{\n\t\teffect = {{\n{indent(tree.ON_MONTHLY, 3)}\n\t\t}}\n\t}}\n}}\n")
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
