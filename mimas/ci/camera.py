"""Writes the CI-only camera data pack: once a player is in the world it switches to spectator and steps
through camera poses, announcing each one in chat ("[CAM] shot <name>") so the driver can screenshot it.
usage: camera.py <out_dir> <pack_major> <pack_minor> <wx> <wy> <wz>   (world position of the build origin)"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from model import ORIGIN  # noqa: E402

# name, time, feet position (local), look-at target (local) or (yaw, pitch)
POSES = [
    ("01_front_day", "noon", (13.0, 10.0, 40.0), (13.0, 12.5, 10.0)),
    ("02_iso_day", "noon", (39.0, 27.0, 39.0), (12.5, 8.0, 7.0)),
    ("03_top_day", "noon", (13.0, 52.0, 13.0), (180.0, 90.0)),
    ("04_street_day", "noon", (3.5, 1.0, 22.5), (9.0, 4.5, 10.0)),
    ("05_takeaway_window", "noon", (18.5, 1.0, 15.5), (16.5, 2.8, 10.0)),
    ("06_inside_counter", "noon", (4.0, 1.0, 9.2), (11.0, 2.8, 4.0)),
    ("07_menu_closeup", "noon", (9.5, 1.6, 8.8), (9.5, 5.3, 6.5)),
    ("08_grill_line", "noon", (14.5, 1.0, 5.5), (7.5, 2.4, 3.5)),
    ("09_back_kitchen", "noon", (18.6, 1.0, 2.5), (2.0, 1.9, 1.5)),
    ("10_staff_side", "noon", (18.6, 1.0, 5.4), (7.0, 2.5, 5.5)),
    ("11_front_night", "18000", (13.0, 10.0, 40.0), (13.0, 12.5, 10.0)),
    ("12_street_night", "18000", (3.5, 1.0, 22.5), (9.0, 4.5, 10.0)),
    ("13_iso_night", "18000", (39.0, 27.0, 39.0), (12.5, 8.0, 7.0)),
]
HOLD = 440      # ticks per pose
START = 200


def to_world(p, w):
    return (p[0] - ORIGIN[0] + w[0], p[1] - ORIGIN[1] + w[1], p[2] - ORIGIN[2] + w[2])


def look(frm, to):
    eye = (frm[0], frm[1] + 1.62, frm[2])
    dx, dy, dz = to[0] - eye[0], to[1] - eye[1], to[2] - eye[2]
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return yaw, pitch


def main():
    out, major, minor = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    w = tuple(int(v) for v in sys.argv[4:7])
    fdir = os.path.join(out, "data", "mimascam", "function")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(os.path.join(out, "data", "minecraft", "tags", "function"), exist_ok=True)
    json.dump({"pack": {"description": "CI camera", "min_format": [major, minor], "max_format": major}},
              open(os.path.join(out, "pack.mcmeta"), "w"))
    json.dump({"values": ["mimascam:load"]}, open(os.path.join(out, "data", "minecraft", "tags", "function", "load.json"), "w"))
    json.dump({"values": ["mimascam:tick"]}, open(os.path.join(out, "data", "minecraft", "tags", "function", "tick.json"), "w"))
    open(os.path.join(fdir, "load.mcfunction"), "w").write("scoreboard objectives add cam dummy\n")
    tick = ["execute unless entity @a run return 0", "scoreboard players add #t cam 1",
            f"execute if score #t cam matches {START} run function mimascam:start"]
    open(os.path.join(fdir, "start.mcfunction"), "w").write(
        "gamemode spectator @a\nweather clear\ntime set noon\nkill @e[type=slime]\n"
        f"tp @a {to_world((13, 12, 47), w)[0]} {to_world((13, 12, 47), w)[1]} {to_world((13, 12, 47), w)[2]} 180 0\n"
        'tellraw @a {text:"[CAM] ready"}\n')
    t = START + 200
    for name, time, frm, to in POSES:
        if len(to) == 2:
            yaw, pitch = to
        else:
            yaw, pitch = look(frm, to)
        x, y, z = to_world(frm, w)
        with open(os.path.join(fdir, f"pose_{name}.mcfunction"), "w") as f:
            f.write(f"time set {time}\nkill @e[type=slime]\n")
            f.write(f"tp @a {x:.2f} {y:.2f} {z:.2f} {yaw:.1f} {pitch:.1f}\n")
            f.write(f'tellraw @a {{text:"[CAM] shot {name}"}}\n')
        tick.append(f"execute if score #t cam matches {t} run function mimascam:pose_{name}")
        t += HOLD
    tick.append(f'execute if score #t cam matches {t} run tellraw @a {{text:"[CAM] done"}}')
    open(os.path.join(fdir, "tick.mcfunction"), "w").write("\n".join(tick) + "\n")
    print(f"camera pack: {len(POSES)} poses, done at tick {t}")


if __name__ == "__main__":
    main()
