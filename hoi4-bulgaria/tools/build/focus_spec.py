"""The bfx_bulgaria focus tree (v3): single source of truth for the tree file, its loc and DESIGN.md.
Two big paths that each split once (the Tsar's Way, the Legionary Revolution), the secret Coburg path,
and shared industry and military blocks."""
from focus_core import FOCUSES  # noqa: F401
import focus_opening  # noqa: F401,E402  (registers focuses in order)
import focus_tsar  # noqa: F401,E402
import focus_legion  # noqa: F401,E402
import focus_secret  # noqa: F401,E402

import focus_eco_mil  # noqa: F401,E402

ECO_MIL_SHIFT = 4  # keeps the industry and military blocks clear of the Legion's right edge
for _f in FOCUSES:
    if _f["block"] in ("eco", "mil"):
        _f["x"] += ECO_MIL_SHIFT

# ---- focus durations (cost x 7 days). Explicit costs set in a module are kept; the default 10 is replaced by a tier.
PATH_BLOCKS = ("tsar", "fascist", "secret")
CAPSTONES = {"bfx_tsar_of_the_bulgarians", "bfx_tsar_the_kingmaker", "bfx_tsar_master_of_the_peninsula",
             "bfx_fas_new_bulgarian_order", "bfx_fas_tsardom_of_three_seas", "bfx_alt_empire_of_the_bulgars", "bfx_alt_new_rome"}


def _tier(f):
    r = f["reward"]
    if f["kind"] == "stat":
        return 5   # 35 days: plain stat bumps
    if "set_cosmetic_tag" in r or f["id"] in CAPSTONES or (f["excl"] and f["block"] in PATH_BLOCKS):
        return 10  # 70 days: path choices, formables, finales
    if "create_wargoal" in r or "declare_war_on" in r or "transfer_state" in r or r.count("add_building_construction") >= 2:
        return 8   # 56 days: war goals, land transfers, two or more buildings
    return 7       # 49 days: everything else


for _f in FOCUSES:
    if _f["cost"] == 10:
        _f["cost"] = _tier(_f)
        if _f.get("merged", 1) >= 3:
            _f["cost"] = max(_f["cost"], 8)  # three focuses in one: 56 days

# industry and military: every focus takes 21 days, so the long side blocks keep pace with the political paths
for _f in FOCUSES:
    if _f["block"] in ("eco", "mil"):
        _f["cost"] = 3
