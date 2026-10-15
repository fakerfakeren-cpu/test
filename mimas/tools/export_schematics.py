"""Export the Mimas model as schematics (needs nbtlib: pip install nbtlib).
  mimas/mimas.litematic  Litematica  (schematic origin = your feet, same as /function mimas:build)
  mimas/mimas.schem      Sponge v2 for WorldEdit / FAWE / Axiom (//paste at your feet, same placement)
usage: python3 mimas/tools/export_schematics.py"""
import json
import os
import sys
import time

import nbtlib
from nbtlib.tag import Byte, ByteArray, Compound, Int, IntArray, List, Long, LongArray, Short, String

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design  # noqa: E402
from model import ORIGIN, VOLUME, resolve_shapes  # noqa: E402

ROOT = os.path.dirname(HERE)
AUTHOR = "Mimas generator"


def model_grid():
    m = design.build()
    resolve_shapes(m)
    (x0, y0, z0), (x1, y1, z1) = VOLUME
    size = (x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1)
    return m, (x0, y0, z0), size


def state_key(b):
    return b.state_str() if b else "minecraft:air"


def block_entity(b):
    """SNBT block-entity data of the model block (only signs carry data)."""
    if not b or not b.nbt:
        return None
    data = nbtlib.parse_nbt(b.nbt)
    data["id"] = String("minecraft:hanging_sign" if b.id.endswith("_hanging_sign") else "minecraft:sign")
    return data


def export_litematic(m, mn, size, data_version, path):
    W, H, L = size
    palette = ["minecraft:air"]
    index = {"minecraft:air": 0}
    cells = []
    tiles = []
    blocks = 0
    for y in range(H):
        for z in range(L):
            for x in range(W):
                b = m.get(mn[0] + x, mn[1] + y, mn[2] + z)
                k = state_key(b)
                if k not in index:
                    index[k] = len(palette)
                    palette.append(k)
                cells.append(index[k])
                if b:
                    blocks += 1
                be = block_entity(b)
                if be is not None:
                    be["x"], be["y"], be["z"] = Int(x), Int(y), Int(z)
                    tiles.append(be)
    bits = max(2, (len(palette) - 1).bit_length())
    n_longs = (len(cells) * bits + 63) // 64
    arr = [0] * n_longs
    for i, v in enumerate(cells):
        bit = i * bits
        li, off = bit >> 6, bit & 63
        arr[li] |= (v << off) & 0xFFFFFFFFFFFFFFFF
        if off + bits > 64:
            arr[li + 1] |= v >> (64 - off)
    signed = [a - (1 << 64) if a >= (1 << 63) else a for a in arr]

    def pal_entry(k):
        name, _, rest = k.partition("[")
        c = Compound({"Name": String(name)})
        if rest:
            c["Properties"] = Compound({kv.split("=")[0]: String(kv.split("=")[1]) for kv in rest[:-1].split(",")})
        return c

    now = Long(int(time.time() * 1000))
    # region position is relative to the schematic origin; the origin is the player's feet block
    pos = (mn[0] - ORIGIN[0], mn[1] - ORIGIN[1], mn[2] - ORIGIN[2])
    root = Compound({
        "Version": Int(6), "SubVersion": Int(1), "MinecraftDataVersion": Int(data_version),
        "Metadata": Compound({
            "Name": String("Mimas (Sofia) döner shop"), "Author": String(AUTHOR),
            "Description": String("Mimas takeaway, Graf Ignatiev / Vasil Levski, Sofia. Java 26.3. "
                                  "Origin = where you stand on the sidewalk in front of the shop."),
            "RegionCount": Int(1), "TotalVolume": Int(W * H * L), "TotalBlocks": Int(blocks),
            "TimeCreated": now, "TimeModified": now,
            "EnclosingSize": Compound({"x": Int(W), "y": Int(H), "z": Int(L)}),
        }),
        "Regions": Compound({"Mimas": Compound({
            "Position": Compound({"x": Int(pos[0]), "y": Int(pos[1]), "z": Int(pos[2])}),
            "Size": Compound({"x": Int(W), "y": Int(H), "z": Int(L)}),
            "BlockStatePalette": List[Compound]([pal_entry(k) for k in palette]),
            "BlockStates": LongArray(signed),
            "TileEntities": List[Compound](tiles),
            "Entities": List[Compound]([]),
            "PendingBlockTicks": List[Compound]([]),
            "PendingFluidTicks": List[Compound]([]),
        })}),
    })
    nbtlib.File(root).save(path, gzipped=True)
    return blocks, len(palette), len(tiles)


def varint(v):
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return out


def export_schem(m, mn, size, data_version, path):
    W, H, L = size
    palette = {"minecraft:air": 0}
    data = bytearray()
    bes = []
    for y in range(H):
        for z in range(L):
            for x in range(W):
                b = m.get(mn[0] + x, mn[1] + y, mn[2] + z)
                k = state_key(b)
                if k not in palette:
                    palette[k] = len(palette)
                data += varint(palette[k])
                be = block_entity(b)
                if be is not None:
                    be["Id"] = be.pop("id")
                    be["Pos"] = IntArray([x, y, z])
                    bes.append(be)
    off = (mn[0] - ORIGIN[0], mn[1] - ORIGIN[1], mn[2] - ORIGIN[2])
    root = Compound({
        "Version": Int(2), "DataVersion": Int(data_version),
        "Width": Short(W), "Height": Short(H), "Length": Short(L),
        "Offset": IntArray([0, 0, 0]),
        "Metadata": Compound({"WEOffsetX": Int(off[0]), "WEOffsetY": Int(off[1]), "WEOffsetZ": Int(off[2]),
                              "Name": String("Mimas (Sofia) döner shop"), "Author": String(AUTHOR),
                              "Date": Long(int(time.time() * 1000))}),
        "PaletteMax": Int(len(palette)),
        "Palette": Compound({k: Int(v) for k, v in palette.items()}),
        "BlockData": ByteArray([b - 256 if b > 127 else b for b in data]),
        "BlockEntities": List[Compound](bes),
    })
    nbtlib.File(root, root_name="Schematic").save(path, gzipped=True)
    return len(palette), len(bes)


def main():
    info = json.load(open(os.path.join(HERE, "version_info.json")))
    dv = int(info["world_version"])
    m, mn, size = model_grid()
    lb, lp, lt = export_litematic(m, mn, size, dv, os.path.join(ROOT, "mimas.litematic"))
    sp, sbe = export_schem(m, mn, size, dv, os.path.join(ROOT, "mimas.schem"))
    print(f"DataVersion {dv} ({info['version']}), size {size[0]}x{size[1]}x{size[2]}")
    print(f"mimas.litematic: {lb} blocks, {lp} palette entries, {lt} tile entities")
    print(f"mimas.schem: {sp} palette entries, {sbe} block entities")


if __name__ == "__main__":
    main()
