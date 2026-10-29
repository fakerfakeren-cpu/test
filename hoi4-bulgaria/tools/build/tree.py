"""Writes common/national_focus/bfx_bulgaria.txt from focus_spec.FOCUSES."""
from core import add_file, loc
from focus_spec import FOCUSES

TREE_ID = "bfx_bulgaria_focus"
ROW_PX = 150         # generous estimate of one focus row in pixels
X_SPREAD = 1.5      # horizontal spread: 1 = vanilla-tight, 2 = very airy
X_OFFSET = 14        # columns of empty space on the left, reserved for the continuous-focus panel


def column_map():
    """Spec column -> tree column. Adds one extra column only between columns where two focuses
    would otherwise sit side by side in the same row, so nothing touches but the tree stays compact."""
    cols = sorted({f["x"] for f in FOCUSES})
    rows = {}
    for f in FOCUSES:
        rows.setdefault(f["y"], set()).add(f["x"])
    out, prev_c, prev_x = {}, None, None
    for c in cols:
        x = int(c * X_SPREAD + 0.5)
        if prev_c is not None:
            x = max(x, prev_x + 1)
            if any(prev_c in r and c in r for r in rows.values()):
                x = max(x, prev_x + 2)  # same-row neighbours never touch
        out[c] = x
        prev_c, prev_x = c, x
    return {c: x + X_OFFSET for c, x in out.items()}


def ind(text, n):
    return "\n".join(("\t" * n + l) if l.strip() else l for l in text.split("\n"))


def generate():
    cm = column_map()
    anchors = {}
    for f in FOCUSES:
        anchors.setdefault(f["block"], f)
    out = [ind(f"""focus_tree = {{
	id = {TREE_ID}
	country = {{
		factor = 0
		modifier = {{ add = 1000 tag = BUL }}
	}}
	default = no
	reset_on_civilwar = no
	continuous_focus_position = {{ x = 50 y = {(max(f['y'] for f in FOCUSES) + 2) * ROW_PX} }}
	initial_show_position = {{ focus = bfx_tsars_dilemma }}""", 0)]
    loc(TREE_ID, "Bulgaria: The Tsar's Balance", "focus")
    for f in FOCUSES:
        a = anchors[f["block"]]
        b = ["focus = {", f"\tid = {f['id']}", f"\ticon = {f['icon']}"]
        if a is f:
            b += [f"\tx = {cm[f['x']]}", f"\ty = {f['y']}"]
        else:
            b += [f"\trelative_position_id = {a['id']}", f"\tx = {cm[f['x']] - cm[a['x']]}", f"\ty = {f['y'] - a['y']}"]
        b.append(f"\tcost = {f['cost']}")
        for grp in f["prereq"]:
            b.append("\tprerequisite = { " + " ".join(f"focus = {p}" for p in grp) + " }")
        if f["excl"]:
            b.append("\tmutually_exclusive = { " + " ".join(f"focus = {p}" for p in f["excl"]) + " }")
        if f["available"]:
            b.append("\tavailable = {")
            b.append(ind(f["available"], 2))
            b.append("\t}")
        if f.get("allow_branch"):
            b.append("\tallow_branch = {")
            b.append(ind(f["allow_branch"], 2))
            b.append("\t}")
        if f["bypass"]:
            b.append("\tbypass = {")
            b.append(ind(f["bypass"], 2))
            b.append("\t}")
        for w in f["war_with"]:
            b.append(f"\twill_lead_to_war_with = {w}")
        b.append("\tsearch_filters = { " + " ".join(f["filters"]) + " }")
        b.append("\tai_will_do = {")
        b.append(ind(f["ai"], 2))
        b.append("\t}")
        if f["select"]:
            b.append("\tselect_effect = {")
            b.append(ind(f["select"], 2))
            b.append("\t}")
        b.append("\tcompletion_reward = {")
        b.append(ind(f["reward"], 2))
        b.append("\t}")
        b.append("}")
        out.append(ind("\n".join(b), 1))
        loc(f["id"], f["name"], "focus")
        loc(f["id"] + "_desc", f["desc"], "focus")
    out.append("}")
    add_file("common/national_focus/bfx_bulgaria.txt", "\n\n".join(out) + "\n")


def design_table():
    cm = column_map()
    rows = ["| ID | Name | x,y | Prerequisites | Exclusive with | Reward (one line) |", "|---|---|---|---|---|---|"]
    for f in FOCUSES:
        pre = "; ".join(" or ".join(g) for g in f["prereq"]) or "—"
        exc = ", ".join(f["excl"]) or "—"
        first = f["reward"].strip().split("\n")
        summary = ", ".join(l.strip() for l in first if l.strip() and not l.strip().startswith(("}", "limit", "if =", "else", "hidden", "every_", "random_", "#")))[:140]
        rows.append(f"| `{f['id']}` | {f['name']} | {cm[f['x']]},{f['y']} | {pre} | {exc} | {summary.replace('|', '/')} |")
    return "\n".join(rows)
