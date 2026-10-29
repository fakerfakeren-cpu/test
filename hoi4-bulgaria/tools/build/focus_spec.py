"""The bfx_bulgaria focus tree (v3): single source of truth for the tree file, its loc and DESIGN.md.
Two big paths that each split once (the Tsar's Way, the Legionary Revolution), the secret Coburg path,
and shared industry and military blocks."""
from focus_core import FOCUSES  # noqa: F401
import focus_opening  # noqa: F401,E402  (registers focuses in order)
import focus_tsar  # noqa: F401,E402
import focus_legion  # noqa: F401,E402
import focus_secret  # noqa: F401,E402

_n = len(FOCUSES)
import focus_eco_mil  # noqa: F401,E402

ECO_MIL_SHIFT = 4  # keeps the industry and military blocks clear of the Legion's right edge
for _f in FOCUSES[_n:]:
    _f["x"] += ECO_MIL_SHIFT
