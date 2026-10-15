"""CI checks for the Mimas data pack.
  verify.py states <datapack_dir> <blocks.json>                     block IDs + states valid for this version
  verify.py interest <blocks.json>                                 print blocks I may want (new 26.x blocks)
  verify.py built <region_dir> <expected.json> <wx> <wy> <wz>       world == model
  verify.py same <region_a> <region_b> <expected.json> <wx> <wy> <wz>  two snapshots identical over the volume
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anvil import read_box  # noqa: E402

STATE_RE = re.compile(r"minecraft:([a-z0-9_]+)(\[([^\]]*)\])?")


def parse_state(s):
    m = STATE_RE.fullmatch(s) or STATE_RE.match(s)
    props = {}
    if m.group(3):
        for kv in m.group(3).split(","):
            k, v = kv.split("=")
            props[k] = v
    return "minecraft:" + m.group(1), props


def cmd_states(dp, report):
    blocks = json.load(open(report))
    used = collections.Counter()
    for root, _, files in os.walk(dp):
        for fn in files:
            if not fn.endswith(".mcfunction"):
                continue
            for line in open(os.path.join(root, fn), encoding="utf-8"):
                if line.startswith("#"):
                    continue
                for m in STATE_RE.finditer(line):
                    if m.group(1) in ("backup",):  # template name mimas:backup is not a block
                        continue
                    if line[m.start() - 6:m.start()] == "mimas:":
                        continue
                    used[m.group(0)] += 1
    bad = []
    ids = set()
    for s in sorted(used):
        bid, props = parse_state(s)
        ids.add(bid)
        if bid not in blocks:
            bad.append(f"UNKNOWN BLOCK {s}")
            continue
        allowed = blocks[bid].get("properties", {})
        for k, v in props.items():
            if k not in allowed:
                bad.append(f"UNKNOWN PROPERTY {k} in {s} (has {sorted(allowed)})")
            elif v not in allowed[k]:
                bad.append(f"BAD VALUE {k}={v} in {s} (allowed {allowed[k]})")
    print(f"STATES: {len(used)} distinct block states, {len(ids)} block IDs checked against blocks.json")
    for b in bad:
        print("STATES-ERROR:", b)
    print("STATES-RESULT:", "PASS" if not bad else f"FAIL ({len(bad)})")
    return not bad


def cmd_interest(report):
    blocks = json.load(open(report))
    pat = re.compile(r"cushion|wool_stairs|wool_slab|concrete_stairs|concrete_slab|chain|shelf|straw|poplar|lantern$|_bars")
    for bid in sorted(blocks):
        if pat.search(bid):
            print("INTEREST:", bid, json.dumps(blocks[bid].get("properties", {})))


def load_expected(path, wx, wy, wz):
    e = json.load(open(path))
    ox, oy, oz = e["origin"]
    (x0, y0, z0), (x1, y1, z1) = e["volume"]
    off = (wx - ox, wy - oy, wz - oz)
    exp = {}
    for k, v in e["blocks"].items():
        x, y, z = map(int, k.split(","))
        exp[(x + off[0], y + off[1], z + off[2])] = v
    box = (x0 + off[0], y0 + off[1], z0 + off[2], x1 + off[0], y1 + 2 + off[1], z1 + off[2])
    return exp, box


AIRS = ("minecraft:air", "minecraft:cave_air", "minecraft:void_air")


def cmd_built(region, expected, wx, wy, wz):
    exp, box = load_expected(expected, wx, wy, wz)
    world = read_box(region, *box)
    mism = []
    n = 0
    for x in range(box[0], box[3] + 1):
        for y in range(box[1], box[4] + 1):
            for z in range(box[2], box[5] + 1):
                n += 1
                a = world.get((x, y, z), "minecraft:air")
                e = exp.get((x, y, z))
                if e is None:
                    if a not in AIRS:
                        mism.append(((x, y, z), "air", a))
                    continue
                eid, eprops = parse_state(e)
                aid, aprops = parse_state(a) if a not in AIRS else (a, {})
                if eid != aid or any(aprops.get(k) != v for k, v in eprops.items()):
                    mism.append(((x, y, z), e, a))
    placed = sum(1 for p in exp)
    print(f"BUILT: compared {n} positions, {placed} expected non-air, {len(mism)} mismatches")
    by_kind = collections.Counter((m[1].split('[')[0], m[2].split('[')[0]) for m in mism)
    for (e, a), c in by_kind.most_common(40):
        print(f"BUILT-MISMATCH-KIND: expected {e} got {a} x{c}")
    for m in mism[:80]:
        print("BUILT-MISMATCH:", m)
    print("BUILT-RESULT:", "PASS" if not mism else f"FAIL ({len(mism)})")


def cmd_same(ra, rb, expected, wx, wy, wz):
    _, box = load_expected(expected, wx, wy, wz)
    a = read_box(ra, *box)
    b = read_box(rb, *box)
    diff = [(p, a.get(p), b.get(p)) for p in set(a) | set(b) if a.get(p) != b.get(p)]
    print(f"SAME: {len(diff)} differences over {len(a)} positions")
    for d in diff[:40]:
        print("SAME-DIFF:", d)
    print("SAME-RESULT:", "PASS" if not diff else f"FAIL ({len(diff)})")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "states":
        cmd_states(sys.argv[2], sys.argv[3])
    elif c == "interest":
        cmd_interest(sys.argv[2])
    elif c == "built":
        cmd_built(sys.argv[2], sys.argv[3], *map(int, sys.argv[4:7]))
    elif c == "same":
        cmd_same(sys.argv[2], sys.argv[3], sys.argv[4], *map(int, sys.argv[5:8]))
