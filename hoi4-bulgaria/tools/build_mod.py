"""Generate the whole bfx_bulgaria mod from tools/build/*.py.

usage: python3 tools/build_mod.py [--no-gfx]
Writes hoi4-bulgaria/mod/bfx_bulgaria/ and hoi4-bulgaria/mod/bfx_bulgaria.mod.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "build"))
sys.path.insert(0, HERE)

import core  # noqa: E402
import ideas, characters, mechanic, events, tree  # noqa: E402,E401

VERSION = "3.1"
GAME_VERSION = "1.19.*"
MOD = os.path.join(ROOT, "mod", "bfx_bulgaria")

LOC_FILES = {  # group -> file
    "focus": "bfx_focus_l_english.yml", "ideas": "bfx_ideas_l_english.yml", "characters": "bfx_characters_l_english.yml",
    "events": "bfx_events_l_english.yml", "decisions": "bfx_decisions_l_english.yml", "neuilly": "bfx_neuilly_l_english.yml",
    "tooltips": "bfx_tooltips_l_english.yml", "cosmetic": "bfx_cosmetic_l_english.yml", "misc": "bfx_misc_l_english.yml", "court": "bfx_court_l_english.yml",
}


def descriptor(path_line):
    return "\n".join([
        f'version="{VERSION}"',
        'tags={\n\t"Alternative History"\n\t"National Focuses"\n\t"Events"\n\t"Historical"\n}',
        'dependencies={\n\t"Road to 56"\n}',
        'name="Bulgaria: The Tsar\'s Balance"',
        'picture="thumbnail.png"',
        f'supported_version="{GAME_VERSION}"',
    ] + ([path_line] if path_line else [])) + "\n"


def main():
    with_gfx = "--no-gfx" not in sys.argv
    # clean script output but keep generated portraits (made by make_portraits.py)
    for sub in ("common", "events", "interface", "localisation"):
        shutil.rmtree(os.path.join(MOD, sub), ignore_errors=True)
    if with_gfx:
        for sub in ("gfx/interface/goals", "gfx/event_pictures", "gfx/flags"):
            shutil.rmtree(os.path.join(MOD, sub), ignore_errors=True)
        for f in os.listdir(os.path.join(MOD, "gfx/interface/ideas")) if os.path.isdir(os.path.join(MOD, "gfx/interface/ideas")) else []:
            if not f.endswith("_small.dds"):
                os.remove(os.path.join(MOD, "gfx/interface/ideas", f))

    ideas.generate()
    characters.generate()
    mechanic.generate()
    events.generate()
    tree.generate()
    if with_gfx:
        import gfx
        gfx.generate()

    for rel, text in core.FILES.items():
        p = os.path.join(MOD, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    locdir = os.path.join(MOD, "localisation", "english")
    os.makedirs(locdir, exist_ok=True)
    for group, keys in core.LOC.items():
        lines = ["l_english:"]
        for k, v in keys.items():
            v = v.replace('"', "'").replace("\n", "\\n")
            lines.append(f' {k}:0 "{v}"')
        with open(os.path.join(locdir, LOC_FILES[group]), "w", encoding="utf-8-sig", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
    with open(os.path.join(MOD, "descriptor.mod"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(descriptor(None))
    with open(os.path.join(ROOT, "mod", "bfx_bulgaria.mod"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(descriptor('path="mod/bfx_bulgaria"'))

    # ship only the portraits our characters use
    used = characters.used_portraits()
    for sub, suffix in (("gfx/leaders/BUL", ".dds"), ("gfx/interface/ideas", "_small.dds")):
        d = os.path.join(MOD, sub)
        for f in os.listdir(d) if os.path.isdir(d) else []:
            if f.startswith("bfx_") and f.endswith(suffix) and f[4:-len(suffix)] not in used and (suffix != ".dds" or sub.endswith("BUL")):
                os.remove(os.path.join(d, f))

    # focus table for DESIGN.md
    with open(os.path.join(HERE, "out", "focus_table.md"), "w") as fh:
        fh.write(tree.design_table() + "\n")
    if with_gfx:
        import gfx
        with open(os.path.join(HERE, "out", "glyph_credits.txt"), "w") as fh:
            for g, a in sorted(gfx.USED_GLYPHS.items()):
                fh.write(f"{g}\t{a}\n")
    n_loc = sum(len(v) for v in core.LOC.values())
    print(f"wrote {len(core.FILES)} script/interface files, {n_loc} loc keys")


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
