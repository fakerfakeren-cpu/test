"""Generate the Mimas data pack + previews.   python3 mimas/tools/build.py [--no-render]"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import design  # noqa: E402
from emit import write_datapack, zip_dir  # noqa: E402
from model import ORIGIN, VOLUME, floating_report, walk_bfs  # noqa: E402

ROOT = os.path.dirname(HERE)


def main():
    m = design.build()
    info_path = os.path.join(HERE, "version_info.json")
    info = json.load(open(info_path)) if os.path.exists(info_path) else {}
    pack_format = tuple(info.get("data_pack_format", (0, 0)))
    version = info.get("version", "26.3")
    counts = write_datapack(m, os.path.join(ROOT, "datapack"), pack_format,
                            f"Mimas döner, Sofia - /function mimas:build (Java {version})")
    zip_dir(os.path.join(ROOT, "datapack"), os.path.join(ROOT, "mimas-datapack.zip"))

    # expected block list for the in-game diff (written after shape resolution)
    with open(os.path.join(ROOT, "tools", "expected_blocks.json"), "w") as f:
        json.dump({"origin": ORIGIN, "volume": VOLUME,
                   "blocks": {f"{x},{y},{z}": b.state_str() for (x, y, z), b in sorted(m.blocks.items())}}, f)

    by_id = collections.Counter(b.id for b in m.blocks.values())
    total = sum(by_id.values())
    print(f"blocks placed: {total} non-air ({len(by_id)} block types); commands per phase: {counts}")
    floating = floating_report(m)
    print("floating blocks:", len(floating), floating[:10])

    reach = walk_bfs(m, ORIGIN)
    targets = {
        "shop door (inside)": (4, 1, 9), "counter front": (9, 1, 7), "window-bar stool side": (11, 1, 8),
        "seating nook": (4, 1, 5), "staff gate": (14, 1, 8), "takeaway counter (staff)": (16, 1, 8),
        "spit line (staff)": (8, 1, 5), "back kitchen": (16, 1, 2), "back kitchen far end": (1, 1, 1), "takeaway window (outside)": (16, 1, 12),
        "residential vestibule": (22, 1, 8), "far sidewalk": (12, 1, 24),
    }
    for name, t in targets.items():
        print(f"  walk {'OK ' if t in reach else 'NO!'} {name} {t}")

    if "--no-render" in sys.argv:
        return
    from render import render
    out = os.path.join(ROOT, "previews")
    os.makedirs(out, exist_ok=True)
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
    shots = [
        ("front", dict(view="front", scale=22, title="Front elevation (from the street, looking north)")),
        ("iso", dict(view="iso", scale=18, title="Isometric (from south-east)")),
        ("top", dict(view="top", scale=20, title="Top-down")),
        ("plan", dict(view="top", scale=28, clip=lambda x, y, z: y <= 2 and z <= 15,
                      title="Floor plan (cut at counter height)")),
        ("cutaway", dict(view="iso", scale=30,
                         clip=lambda x, y, z: z <= 15 and (y <= 4 if z >= 10 else y <= 5),
                         title="Interior cutaway (ceiling, upper floors and sign removed)")),
    ]
    for name, kw in shots:
        img = render(m, **kw)
        p = os.path.join(out, f"{name}{tag}.png")
        img.save(p)
        print("wrote", p, img.size)


if __name__ == "__main__":
    main()
