"""Static validator for the bfx_bulgaria mod. Exit code 1 if any error.

usage: python3 tools/validate.py
Checks (see README): syntax balance, focus graph & layout, localisation, graphics,
events/flags/variables, bfx_ prefixes and file names, state IDs, and a key whitelist
built from the game's own script documentation (effects, triggers, modifiers).
"""
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "mod", "bfx_bulgaria")
REF = os.path.join(ROOT, "reference")
sys.path.insert(0, HERE)
from ddslib import read_dds  # noqa: E402

ERR, WARN = [], []


def err(m):
    ERR.append(m)


def warn(m):
    WARN.append(m)


# ------------------------------------------------------------------ parsing
TOK = re.compile(r'"(?:[^"\\\n]|\\.)*"|[{}]|[<>]=?|!=|=|[^\s{}=<>"#]+')


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        res, q = [], False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == "#" and not q:
                break
            res.append(ch)
        out.append("".join(res))
    return "\n".join(out)


def tokens(text):
    return TOK.findall(strip_comments(text))


def parse(toks, i=0):
    """Returns list of (key, op, value) where value is str or list."""
    out = []
    while i < len(toks):
        t = toks[i]
        if t == "}":
            return out, i + 1
        if t == "{":  # anonymous block
            v, i = parse(toks, i + 1)
            out.append((None, None, v))
            continue
        if i + 1 < len(toks) and toks[i + 1] in ("=", "<", ">", "<=", ">=", "!="):
            op = toks[i + 1]
            if i + 2 < len(toks) and toks[i + 2] == "{":
                v, i = parse(toks, i + 3)
            else:
                v, i = toks[i + 2] if i + 2 < len(toks) else "", i + 3
            out.append((t, op, v))
        else:
            out.append((t, None, None))
            i += 1
    return out, i


def walk(node, path=()):
    for k, op, v in node:
        yield k, op, v, path
        if isinstance(v, list):
            yield from walk(v, path + (k,))


def get(node, key):
    return [v for k, _, v in node if k == key]


def first(node, key, default=None):
    r = get(node, key)
    return r[0] if r else default


def files(ext, base=MOD):
    for d, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(ext):
                yield os.path.join(d, f)


def rel(p):
    return os.path.relpath(p, MOD)


# ------------------------------------------------------------------ 1. balance
def check_balance():
    for ext in (".txt", ".gfx", ".gui", ".mod"):
        for p in files(ext):
            text = open(p, encoding="utf-8-sig").read()
            depth, line_no = 0, 1
            for line in strip_comments(text).split("\n"):
                if line.count('"') % 2:
                    err(f"{rel(p)}:{line_no}: unbalanced quotes")
                for ch in re.sub(r'"[^"]*"', "", line):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth < 0:
                            err(f"{rel(p)}:{line_no}: unexpected '}}'")
                            depth = 0
                line_no += 1
            if depth:
                err(f"{rel(p)}: {depth} unclosed '{{'")


# ------------------------------------------------------------------ load everything
def load_all():
    data = {}
    for p in files(".txt"):
        data[p] = parse(tokens(open(p, encoding="utf-8-sig").read()))[0]
    for p in files(".gfx"):
        data[p] = parse(tokens(open(p, encoding="utf-8-sig").read()))[0]
    return data


def load_loc():
    keys, dup = {}, []
    for p in files(".yml"):
        raw = open(p, "rb").read()
        if not raw.startswith(b"\xef\xbb\xbf"):
            err(f"{rel(p)}: missing UTF-8 BOM")
        if not os.path.basename(p).startswith("bfx_") or not p.endswith("_l_english.yml"):
            err(f"{rel(p)}: localisation file name must be bfx_*_l_english.yml")
        lines = raw.decode("utf-8-sig").split("\n")
        if lines[0].strip() != "l_english:":
            err(f"{rel(p)}: first line must be l_english:")
        for n, line in enumerate(lines[1:], 2):
            if not line.strip() or line.strip().startswith("#"):
                continue
            m = re.match(r'^ ([A-Za-z0-9_.\-]+):\d* "(.*)"\s*$', line)
            if not m:
                err(f"{rel(p)}:{n}: malformed loc line")
                continue
            k, v = m.groups()
            if k in keys:
                dup.append(k)
            if not v.strip():
                err(f"{rel(p)}:{n}: empty loc value for {k}")
            keys[k] = v
    for k in dup:
        err(f"duplicate loc key {k}")
    return keys


def ref_set(name):
    p = os.path.join(REF, name)
    return {l.strip() for l in open(p) if l.strip() and not l.startswith("#")}


def ref_sprites():
    s = {}
    for f in os.listdir(REF):
        if f.endswith(".gfx"):
            for m in re.finditer(r'name = "([^"]+)" texturefile = "([^"]+)"', open(os.path.join(REF, f)).read()):
                s[m.group(1)] = m.group(2)
    return s


# ------------------------------------------------------------------ main checks
def main():
    check_balance()
    data = load_all()
    loc = load_loc()
    allt = {p: tokens(open(p, encoding="utf-8-sig").read()) for p in data}
    script_tokens = Counter(t.strip('"') for p, ts in allt.items() for t in ts)

    def find(sub):
        return [p for p in data if sub in p.replace("\\", "/")]

    # ---------- definitions
    focus_file = find("common/national_focus/")[0]
    tree = first(data[focus_file], "focus_tree")
    focuses = get(tree, "focus")
    ideas = {}
    for p in find("common/ideas/"):
        for k, _, v in data[p]:
            for cat_k, _, cat_v in v:
                for idk, _, idv in cat_v:
                    ideas[idk] = idv
    chars = {k: v for p in find("common/characters/") for k, _, v in first(data[p], "characters")}
    traits = {k for p in find("common/country_leader/") for k, _, v in first(data[p], "leader_traits")}
    opinion = {k for p in find("common/opinion_modifiers/") for k, _, v in first(data[p], "opinion_modifiers")}
    dynmods = {k for p in find("common/dynamic_modifiers/") for k, _, v in data[p]}
    seffects = {k for p in find("common/scripted_effects/") for k, _, v in data[p]}
    cats = {k: v for p in find("common/decisions/categories/") for k, _, v in data[p]}
    decisions = {}
    for p in find("common/decisions/"):
        if "categories" in p:
            continue
        for c, _, v in data[p]:
            if c not in cats:
                err(f"decisions grouped under unknown category {c}")
            for d, _, dv in v:
                decisions[d] = dv
    events, namespaces = {}, set()
    for p in find("/events/"):
        for k, _, v in data[p]:
            if k == "add_namespace":
                namespaces.add(v)
            elif k in ("country_event", "news_event", "state_event"):
                eid = first(v, "id")
                if eid in events:
                    err(f"duplicate event id {eid}")
                events[eid] = v
    sprites = {}
    for p in find("interface/"):
        for k, _, v in data[p]:
            for sk, _, sv in v:
                if sk.lower() == "spritetype":
                    n = first(sv, "name").strip('"')
                    if n in sprites:
                        err(f"duplicate sprite {n}")
                    sprites[n] = (first(sv, "texturefile").strip('"'), p)
    refspr = ref_sprites()
    cosmetic = {t.strip('"') for p in data for k, _, v, _ in walk(data[p]) if k == "set_cosmetic_tag" for t in [v]}
    factions = {v for p in data for k, _, v, _ in walk(data[p]) if k == "create_faction"}

    # ---------- focuses
    ids = [first(f, "id") for f in focuses]
    for k, n in Counter(ids).items():
        if n > 1:
            err(f"duplicate focus id {k}")
    byid = {first(f, "id"): f for f in focuses}
    pos = {}

    def abs_pos(fid, seen=()):
        if fid in pos:
            return pos[fid]
        f = byid[fid]
        x, y = float(first(f, "x", 0)), float(first(f, "y", 0))
        r = first(f, "relative_position_id")
        if r:
            if r not in byid:
                err(f"{fid}: relative_position_id {r} does not exist")
                return (x, y)
            if r in seen:
                err(f"{fid}: relative position cycle")
                return (x, y)
            rx, ry = abs_pos(r, seen + (fid,))
            x, y = x + rx, y + ry
        pos[fid] = (x, y)
        return pos[fid]

    for fid in byid:
        abs_pos(fid)
    occupied = defaultdict(list)
    for fid, p in pos.items():
        occupied[p].append(fid)
    for p, fs in occupied.items():
        if len(fs) > 1:
            err(f"focuses share position {p}: {fs}")
    edges = []
    for fid, f in byid.items():
        for grp in get(f, "prerequisite"):
            for k, _, v in grp:
                if v not in byid:
                    err(f"{fid}: prerequisite {v} does not exist")
                    continue
                edges.append((v, fid))
                if pos[v][1] >= pos[fid][1]:
                    err(f"{fid}: prerequisite {v} is not above it")
        for grp in get(f, "mutually_exclusive"):
            for k, _, v in grp:
                if v not in byid:
                    err(f"{fid}: mutually_exclusive {v} does not exist")
                elif fid not in [x for g in get(byid[v], "mutually_exclusive") for _, _, x in g]:
                    warn(f"{fid}: exclusive with {v} but not vice versa")
        if not first(f, "ai_will_do"):
            err(f"{fid}: missing ai_will_do")
        if not first(f, "search_filters"):
            err(f"{fid}: missing search_filters")
        for key in (fid, fid + "_desc"):
            if key not in loc:
                err(f"missing loc {key}")
    # line crossing (HOI4 draws parent -> down -> across -> down to child)
    for a, b in edges:
        (ax, ay), (bx, by) = pos[a], pos[b]
        mid = ay + 0.5
        segs = [((ax, ay), (ax, mid)), ((ax, mid), (bx, mid)), ((bx, mid), (bx, by))]
        for fid, (x, y) in pos.items():
            if fid in (a, b):
                continue
            for (x1, y1), (x2, y2) in segs:
                if min(x1, x2) - 0.4 < x < max(x1, x2) + 0.4 and min(y1, y2) - 0.3 < y < max(y1, y2) + 0.3:
                    if (x1 == x2 and abs(x - x1) < 0.4) or (y1 == y2 and abs(y - y1) < 0.3):
                        err(f"line {a} -> {b} crosses focus {fid} at {(x, y)}")
                        break
    # stat-bump share
    # (ratio is reported from the spec by build output; here only count ids)

    # ---------- loc presence for other objects
    def need(key, what):
        if key not in loc:
            err(f"missing loc for {what}: {key}")
    for i in ideas:
        need(i, "idea"); need(i + "_desc", "idea desc")
    for c, v in chars.items():
        need(c, "character")
        for adv in get(v, "advisor"):
            need(first(adv, "idea_token"), "advisor token")
    for t in traits:
        need(t, "trait")
    for o in opinion:
        need(o, "opinion modifier")
    for d in dynmods:
        need(d, "dynamic modifier")
    for c in cats:
        need(c, "decision category"); need(c + "_desc", "category desc")
    for d in decisions:
        need(d, "decision"); need(d + "_desc", "decision desc")
    for eid, ev in events.items():
        need(first(ev, "title"), "event title"); need(first(ev, "desc"), "event desc")
        opts = get(ev, "option")
        if not opts:
            err(f"event {eid} has no options")
        for o in opts:
            need(first(o, "name"), "event option")
            body = [k for k, _, _ in o if k not in ("name", "ai_chance", "trigger")]
            if not body and first(ev, "major") != "yes":
                err(f"event {eid}: option {first(o, 'name')} has no effect")
    for c in cosmetic:
        need(c, "cosmetic tag"); need(c + "_DEF", "cosmetic DEF"); need(c + "_ADJ", "cosmetic ADJ")
        for sub in ("", "medium/", "small/"):
            if not os.path.exists(os.path.join(MOD, "gfx/flags", sub, c + ".tga")):
                err(f"missing flag gfx/flags/{sub}{c}.tga")
    for f in factions:
        need(f, "faction name")
    for p in data:
        for k, _, v, _ in walk(data[p]):
            if k == "custom_effect_tooltip":
                need(v, "tooltip")
            if k == "add_named_threat" and isinstance(v, list):
                need(first(v, "name"), "named threat")
            if k == "add_mastery_bonus" and isinstance(v, list):
                need(first(v, "name"), "mastery bonus name")
    # unused loc keys
    derived = set()
    for k in loc:
        cands = {k, re.sub(r"_desc$", "", k)}
        c = re.sub(r"_(DEF|ADJ)$", "", k)
        cands |= {c, re.sub(r"_(neutrality|fascism|communism|democratic)$", "", c)}
        if any(x in script_tokens for x in cands):
            derived.add(k)
    tree_id = first(tree, "id")
    for k in loc:
        if k not in derived and k != tree_id:
            err(f"unused loc key {k}")

    # ---------- graphics
    for n, (tex, p) in sprites.items():
        if "shine_overlay" in tex:
            continue
        path = os.path.join(MOD, tex)
        if not os.path.exists(path):
            err(f"sprite {n}: texture {tex} missing")
            continue
        want = (95, 85) if "/goals/" in tex else (64, 64) if "/ideas/" in tex else (210, 176) if "event_pictures" in tex else None
        try:
            img = read_dds(path)
            if want and img.size != want:
                err(f"{tex}: size {img.size}, expected {want}")
        except Exception as e:  # pragma: no cover
            err(f"{tex}: unreadable DDS ({e})")
    for n in sprites:
        if n.startswith("GFX_focus_") and not n.endswith("_shine") and n + "_shine" not in sprites:
            err(f"focus sprite {n} has no _shine variant")
    gfx_refs = set()
    for p in data:
        if "/interface/" in p:
            continue
        for t in allt[p]:
            t = t.strip('"')
            if t.startswith("GFX_"):
                gfx_refs.add(t)
    for f in focuses:
        gfx_refs.add(first(f, "icon"))
    for i, v in ideas.items():
        pic = first(v, "picture")
        gfx_refs.add(pic if pic.startswith("GFX_") else "GFX_idea_" + pic)
    for d, v in decisions.items():
        ic = first(v, "icon")
        gfx_refs.add(ic if ic.startswith("GFX_") else "GFX_decision_" + ic)
    for c, v in cats.items():
        ic = first(v, "icon")
        gfx_refs.add(ic if ic.startswith("GFX_") else "GFX_decision_category_" + ic)
    for g in sorted(gfx_refs):
        if g not in sprites and g not in refspr:
            err(f"unknown sprite {g}")
    for c, v in chars.items():
        for pt in get(v, "portraits"):
            for _, _, kind in pt:
                for size_key, _, path in kind:
                    path = path.strip('"')
                    full = os.path.join(MOD, path)
                    if not os.path.exists(full):
                        err(f"{c}: portrait {path} missing")
                        continue
                    want = (156, 210) if size_key == "large" else (65, 67)
                    if read_dds(full).size != want:
                        err(f"{c}: portrait {path} wrong size")
    thumb = os.path.join(MOD, "thumbnail.png")
    if os.path.getsize(thumb) > 1024 * 1024:
        err("thumbnail.png larger than 1 MB")
    from PIL import Image
    tw, th = Image.open(thumb).size
    if tw != th:
        err("thumbnail.png is not square")

    # ---------- events fired, flags, variables
    fired = set()
    flags_set, flags_chk, vars_set, vars_chk = set(), set(), set(), set()
    for p in data:
        for k, _, v, _ in walk(data[p]):
            if k in ("country_event", "news_event", "state_event"):
                fired.add(v if isinstance(v, str) else first(v, "id"))
            if k in ("set_country_flag", "set_global_flag"):
                flags_set.add(v if isinstance(v, str) else first(v, "flag"))
            if k in ("has_country_flag", "has_global_flag"):
                flags_chk.add(v if isinstance(v, str) else first(v, "flag"))
            if k in ("set_variable", "add_to_variable", "subtract_from_variable", "multiply_variable") and isinstance(v, list):
                for kk, _, _ in v:
                    vars_set.add(kk)
            if k == "check_variable" and isinstance(v, list):
                for kk, _, _ in v:
                    vars_chk.add(kk)
            if k == "clamp_variable" and isinstance(v, list):
                vars_chk.add(first(v, "var"))
    fired.discard(None)
    for e in fired:
        if e not in events:
            err(f"fired event {e} does not exist")
    for e in events:
        if e not in fired:
            warn(f"event {e} is never fired")
    for f in flags_chk - flags_set:
        err(f"flag {f} is checked but never set")
    for vv in vars_chk - vars_set:
        err(f"variable {vv} is checked but never set")
    for k, v in loc.items():
        for vv in re.findall(r"\[\?([A-Za-z0-9_]+)", v):
            if vv not in vars_set:
                err(f"loc {k} shows variable {vv} that is never set")
    for p in find("common/dynamic_modifiers/"):
        for _, _, v in data[p]:
            for k, _, val in v:
                if isinstance(val, str) and re.match(r"^[a-z_]+$", val) and val not in ("yes", "no") and k not in ("icon",):
                    if val not in vars_set:
                        err(f"dynamic modifier uses variable {val} that is never set")

    # ---------- prefixes & file names
    defined = set(ids) | set(ideas) | set(chars) | traits | opinion | dynmods | seffects | set(cats) | set(decisions) | cosmetic | factions
    for d in defined:
        if not d.startswith("bfx_"):
            err(f"id without bfx_ prefix: {d}")
    for ns in namespaces:
        if not ns.startswith("bfx"):
            err(f"event namespace without bfx prefix: {ns}")
    for n in sprites:
        if "bfx_" not in n:
            err(f"sprite without bfx_: {n}")
    for f in flags_set:
        if not f.startswith("bfx_"):
            err(f"flag without bfx_: {f}")
    for vv in vars_set:
        if not vv.startswith("bfx_"):
            err(f"variable without bfx_: {vv}")
    for k in loc:
        if not k.lower().startswith("bfx"):
            err(f"loc key without bfx prefix: {k}")
    for d, _, fs in os.walk(MOD):
        for f in fs:
            if f in ("descriptor.mod", "thumbnail.png"):
                continue
            if not f.startswith("bfx_"):
                err(f"file name without bfx_ prefix (could collide with vanilla/R56): {os.path.join(rel(d), f)}")
    if "replace_path" in open(os.path.join(MOD, "descriptor.mod")).read():
        err("descriptor uses replace_path")

    # ---------- state ids
    known_states = {l.split("\t")[0] for l in open(os.path.join(REF, "states_used.txt")) if l[0].isdigit()}
    state_keys = {"add_state_claim", "add_state_core", "owns_state", "controls_state", "transfer_state", "remove_state_core"}
    for p in data:
        for k, _, v, path in walk(data[p]):
            if k in state_keys and isinstance(v, str) and v.isdigit() and v not in known_states:
                err(f"{rel(p)}: state {v} not in reference/states_used.txt")
            if k and k.isdigit() and k not in known_states and 'random_list' not in path:
                err(f"{rel(p)}: state scope {k} not in reference/states_used.txt")
            if k == "generator" and isinstance(v, list):
                for s, _, _ in v:
                    if s not in known_states:
                        err(f"{rel(p)}: generator state {s} unknown")

    # ---------- key whitelist (catches misspelled effects/triggers/modifiers)
    effects = ref_set("effects_all.txt")
    triggers = ref_set("triggers_all.txt")
    modifiers = ref_set("modifiers_all.txt")
    structural = set("""
    focus_tree id country factor modifier add tag default reset_on_civilwar continuous_focus_position initial_show_position
    x y focus icon cost prerequisite mutually_exclusive available bypass search_filters ai_will_do completion_reward
    relative_position_id will_lead_to_war_with select_effect limit if else else_if hidden_effect custom_effect_tooltip
    ideas picture allowed removal_cost name portraits civilian army large small country_leader ideology traits expire
    advisor slot idea_token skill attack_skill defense_skill planning_skill logistics_skill field_marshal corps_commander
    leader_traits random opinion_modifiers value enable remove_trigger on_actions on_startup effect on_monthly_BUL
    title desc is_triggered_only trigger immediate option ai_chance base major add_namespace country_event news_event
    days days_re_enable fire_only_once visible complete_effect priority spriteTypes SpriteType spritetype texturefile
    effectFile animation animationmaskfile animationtexturefile animationrotation animationlooping animationtime
    animationdelay animationblendmode animationtype animationrotationoffset animationtexturescale legacy_lazy_load
    type level instant_build province all_provinces limit_to_border limit_to_coastal building size include_locked
    bonus uses category ideology popularity ruling_party elections_allowed target generator threat amount producer
    var min max remove_idea add_idea idea transfer_troops OR AND NOT ROOT FROM PREV THIS owner controller capital_scope
    folder flag yes no characters
    """.split())
    ideologies = {"fascism", "communism", "democratic", "neutrality"}
    tags = set("BUL GRE YUG TUR ROM ALB GER ITA ENG FRA SOV CZE HUN POL UKR CRI MNT MAC SER CRO SLV BOS AUS SLO MOL LIT LAT EST".split())
    own = defined | seffects | set(byid) | set(ideas)
    allowed_keys = effects | triggers | modifiers | structural | ideologies | tags | own
    for p in data:
        if "/interface/" in p:
            continue
        top_level_defs = {k for k, _, _ in data[p]}
        for k, op, v, path in walk(data[p]):
            if k is None or op is None or k.startswith('"') or k.isdigit() or k in top_level_defs:
                continue
            if k.startswith(("event_target:", "var:")) or re.match(r"^bfx_", k):
                continue
            if any(seg in ("modifier", "set_variable", "add_to_variable", "subtract_from_variable", "multiply_variable",
                           "check_variable", "leader_traits", "opinion_modifiers", "ideas", "characters", "country",
                           "portraits", "research_bonus") for seg in path if seg) and k not in allowed_keys:
                # inside these blocks keys are modifiers / variable names / definitions
                if "modifier" in path and k not in modifiers and k not in structural:
                    err(f"{rel(p)}: unknown modifier '{k}'")
                continue
            if k not in allowed_keys:
                err(f"{rel(p)}: unknown key '{k}' (not an effect/trigger/modifier in 1.19 script docs)")

    # ---------- DLC gating
    for p in data:
        if "has_dlc" in allt[p]:
            err(f"{rel(p)}: uses has_dlc")

    # ---------- summary
    print("bfx_bulgaria static validation")
    print(f"  focuses {len(byid)} | ideas {len(ideas)} | characters {len(chars)} | events {len(events)} | decisions {len(decisions)} in {len(cats)} categories")
    print(f"  sprites {len(sprites)} | loc keys {len(loc)} | flags {len(flags_set)} | variables {len(vars_set)}")
    for w in WARN:
        print("  WARN ", w)
    for e in sorted(set(ERR), key=ERR.index):
        print("  ERROR", e + (f"  (x{ERR.count(e)})" if ERR.count(e) > 1 else ""))
    print(f"  => {len(ERR)} errors, {len(WARN)} warnings")
    return 1 if ERR else 0


if __name__ == "__main__":
    sys.exit(main())
