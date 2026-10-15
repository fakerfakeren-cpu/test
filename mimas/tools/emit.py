"""Turns the Mimas model into a vanilla data pack (mimas:build / mimas:clear)."""
import json
import os
import shutil
import zipfile

from model import ORIGIN, VOLUME, is_attach, is_shaped, resolve_shapes

NS = "mimas"
# Data-pack format of Java 26.3, read from the 26.3 server jar (version.json "pack_version") by CI.
PACK_FORMAT = None   # filled in by build.py from mimas/tools/version_info.json


def rel(x, y, z):
    # the build function runs aligned to the player's feet block
    return " ".join("~" if d == 0 else f"~{d}" for d in (x - ORIGIN[0], y - ORIGIN[1], z - ORIGIN[2]))


def phase_of(b):
    if is_attach(b.id):
        return 3
    if is_shaped(b.id):
        return 2
    return 1


def greedy_boxes(positions):
    """Merge a set of positions holding the same block into axis-aligned boxes."""
    left = set(positions)
    boxes = []
    for p in sorted(positions, key=lambda q: (q[1], q[2], q[0])):
        if p not in left:
            continue
        x, y, z = p
        x2 = x
        while (x2 + 1, y, z) in left:
            x2 += 1
        z2 = z
        while all((xx, y, z2 + 1) in left for xx in range(x, x2 + 1)):
            z2 += 1
        y2 = y
        while all((xx, y2 + 1, zz) in left for xx in range(x, x2 + 1) for zz in range(z, z2 + 1)):
            y2 += 1
        for xx in range(x, x2 + 1):
            for yy in range(y, y2 + 1):
                for zz in range(z, z2 + 1):
                    left.discard((xx, yy, zz))
        boxes.append(((x, y, z), (x2, y2, z2)))
    return boxes


def commands_for_phase(m, phase):
    groups = {}
    nbt_blocks = []
    for p, b in m.blocks.items():
        if phase_of(b) != phase:
            continue
        if b.nbt:
            nbt_blocks.append((p, b))
        else:
            groups.setdefault(b.key(), (b, []))[1].append(p)
    cmds = []  # (sort_y, text)
    for key, (b, plist) in groups.items():
        for (a, c) in greedy_boxes(plist):
            n = (c[0] - a[0] + 1) * (c[1] - a[1] + 1) * (c[2] - a[2] + 1)
            assert n <= 32768
            if a == c:
                cmds.append((a[1], a, f"setblock {rel(*a)} {b.state_str()}"))
            else:
                cmds.append((a[1], a, f"fill {rel(*a)} {rel(*c)} {b.state_str()}"))
    for p, b in nbt_blocks:
        cmds.append((p[1], p, f"setblock {rel(*p)} {b}"))
    if phase == 3:
        # supports first: bottom-up; within a level keep door lower halves before upper (y handles it)
        cmds.sort(key=lambda t: (t[0], t[1][2], t[1][0]))
    else:
        cmds.sort(key=lambda t: (t[0], t[1][2], t[1][0]))
    return [c for _, _, c in cmds]


def write_datapack(m, out_dir, pack_format, description):
    resolve_shapes(m)
    (x0, y0, z0), (x1, y1, z1) = VOLUME
    sx, sy, sz = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    fdir = os.path.join(out_dir, "data", NS, "function")
    os.makedirs(os.path.join(fdir, "internal"))
    os.makedirs(os.path.join(out_dir, "data", "minecraft", "tags", "function"))

    major, minor = pack_format
    mcmeta = {"pack": {"description": description, "min_format": [major, minor], "max_format": major}}
    with open(os.path.join(out_dir, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(mcmeta, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "data", "minecraft", "tags", "function", "load.json"), "w") as f:
        json.dump({"values": [f"{NS}:internal/load"]}, f, indent=2)

    def write(name, lines):
        with open(os.path.join(fdir, name + ".mcfunction"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

    corner = rel(x0, y0, z0)
    far = rel(x1, y1, z1)
    sb = rel(x0, y1 + 1, z0)            # structure block just above the volume
    rs = rel(x0, y1 + 2, z0)
    phases = {p: commands_for_phase(m, p) for p in (1, 2, 3)}
    counts = {p: len(c) for p, c in phases.items()}

    write("internal/load", [
        f"scoreboard objectives add {NS} dummy",
    ])
    write("build", [
        "# Builds Mimas around you. You end up on the sidewalk in front of the shop, facing it (north).",
        "# Footprint: 26 wide (x) x 26 deep (z) x 34 high, from 10 blocks west to 15 east, 13 north to 12 south.",
        f"execute if entity @e[type=marker,tag={NS}_origin,distance=..80] run function {NS}:clear",
        f"execute align xyz run function {NS}:internal/build_here",
    ])
    write("internal/build_here", [
        'tellraw @s [{text:"[Mimas] ",color:"red"},{text:"Building...",color:"gold"}]',
        f'summon marker ~0.5 ~ ~0.5 {{Tags:["{NS}_origin"]}}',
        "# back up what is here now (in memory) so mimas:clear can put it back",
        f'setblock {sb} minecraft:structure_block[mode=save]{{mode:"SAVE",name:"{NS}:backup",author:"mimas",'
        f'posX:0,posY:{y0 - (y1 + 1)},posZ:0,sizeX:{sx},sizeY:{sy},sizeZ:{sz},ignoreEntities:1b,'
        f'showboundingbox:0b,showair:0b}}',
        f"setblock {rs} minecraft:redstone_block",
        f"setblock {rs} minecraft:air",
        f"setblock {sb} minecraft:air",
        f"fill {corner} {far} minecraft:air",
        f"function {NS}:internal/blocks_1",
        f"function {NS}:internal/blocks_2",
        f"function {NS}:internal/blocks_3",
        f"execute positioned {corner} run kill @e[type=item,dx={sx - 1},dy={sy - 1},dz={sz - 1}]",
        "tp @s ~0.5 ~ ~0.5 180 0",
        'tellraw @s [{text:"[Mimas] ",color:"red"},{text:"Done. Undo with ",color:"gold"},'
        '{text:"/function mimas:clear",color:"yellow"}]',
    ])
    for p in (1, 2, 3):
        write(f"internal/blocks_{p}", phases[p])
    write("clear", [
        "# Removes the nearest Mimas build and restores what was there before (same session).",
        f'execute unless entity @e[type=marker,tag={NS}_origin] run tellraw @s '
        '{text:"[Mimas] No build found nearby (stand near it).",color:"red"}',
        f"execute as @e[type=marker,tag={NS}_origin,sort=nearest,limit=1] at @s align xyz run function "
        f"{NS}:internal/clear_here",
    ])
    write("internal/clear_here", [
        f"fill {corner} {far} minecraft:air",
        f"scoreboard players set #restored {NS} 0",
        f"execute store success score #restored {NS} run place template {NS}:backup {corner}",
        f"execute if score #restored {NS} matches 0 run function {NS}:internal/flatten",
        f"execute positioned {corner} run kill @e[type=item,dx={sx - 1},dy={sy - 1},dz={sz - 1}]",
        f'execute if score #restored {NS} matches 1 run tellraw @a[distance=..64] [{{text:"[Mimas] ",color:"red"}},'
        '{text:"Removed - original terrain restored.",color:"gold"}]',
        f'execute if score #restored {NS} matches 0 run tellraw @a[distance=..64] [{{text:"[Mimas] ",color:"red"}},'
        '{text:"Removed. No backup in memory (world was reloaded), so the area was levelled to grass.",'
        'color:"gold"}]',
        "kill @s",
    ])
    write("internal/flatten", [
        f"fill {rel(x0, y0, z0)} {rel(x1, -1, z1)} minecraft:dirt",
        f"fill {rel(x0, 0, z0)} {rel(x1, 0, z1)} minecraft:grass_block[snowy=false]",
    ])
    return counts


def zip_dir(src, zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, src))
