"""Rebuild only the focus/event/text output from an already built map (dev shortcut)."""
import glob, os, re, struct, sys, importlib.util
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def out(p):
    p = os.path.join(ROOT, p); os.makedirs(os.path.dirname(p), exist_ok=True); return p
def write(path, text, bom=False):
    with open(out(path), "w", encoding="utf-8-sig" if bom else "utf-8", newline="\r\n") as f: f.write(text)
def write_dds_bgra(path, rgba):
    h_, w_ = rgba.shape[:2]
    header = struct.pack("<4s7I44s8I5I", b"DDS ", 124, 0x100F, h_, w_, w_ * 4, 0, 0, bytes(44),
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0, 0, 0, 0)
    with open(out(path), "wb") as f:
        f.write(header); f.write(rgba[..., [2, 1, 0, 3]].tobytes())
loc = open(f"{ROOT}/localisation/english/replace/evil_sofia_l_english.yml", encoding="utf-8-sig").read()
state_names = {int(i): n for i, n in re.findall(r'EVIL_SOFIA_STATE_(\d+):0 "([^"]*)"', loc)}
states = []
for f in glob.glob(f"{ROOT}/history/states/*.txt"):
    t = open(f, encoding="utf-8-sig").read()
    states.append({"id": int(re.search(r"\bid\s*=\s*(\d+)", t).group(1)), "owner": re.search(r"owner\s*=\s*(\w+)", t).group(1)})
    states[-1]["name"] = state_names.get(states[-1]["id"], "")
cap, names = {}, {}
for f in glob.glob(f"{ROOT}/history/countries/*.txt"):
    tag, name = os.path.basename(f)[:-4].split(" - ")
    cap[tag] = int(re.search(r"capital\s*=\s*(\d+)", open(f, encoding="utf-8-sig").read()).group(1)); names[tag] = name
stadium = int(re.search(r"location = (\d+)", open(f"{ROOT}/history/units/SRD_red_guards.txt").read()).group(1))
spec = importlib.util.spec_from_file_location("build_focus", f"{ROOT}/tools/build_focus.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
print("focuses", bf.build(ROOT, {"states": states, "capital_state": cap, "stadium_province": stadium, "countries": names}, write, write_dds_bgra))
