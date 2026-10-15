"""Print the java command line for an offline vanilla client (one arg per line, NUL-free).
usage: python3 launch_client.py <mcdir> <version> <gamedir> <world>"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_mc import rules_ok  # noqa: E402

mcdir, version, gamedir, world = sys.argv[1:5]
vj = json.load(open(os.path.join(mcdir, f"{version}.json")))
cp = json.load(open(os.path.join(mcdir, "classpath.json")))
natives = os.path.join(mcdir, "natives")
os.makedirs(natives, exist_ok=True)
features = {"has_custom_resolution": True, "is_quick_play_singleplayer": True}
subs = {
    "auth_player_name": "Mimas", "version_name": version, "game_directory": gamedir,
    "assets_root": os.path.join(mcdir, "assets"), "assets_index_name": vj["assetIndex"]["id"],
    "auth_uuid": "6d696d61-7300-4000-8000-000000000001", "auth_access_token": "0", "clientid": "0",
    "auth_xuid": "0", "user_type": "legacy", "version_type": vj.get("type", "release"),
    "natives_directory": natives, "launcher_name": "mimas-ci", "launcher_version": "1",
    "classpath": os.pathsep.join(cp), "classpath_separator": os.pathsep,
    "library_directory": os.path.join(mcdir, "libraries"), "resolution_width": "1280",
    "resolution_height": "720", "quickPlaySingleplayer": world, "quickPlayPath": "quickplay.json",
    "user_properties": "{}",
}


def expand(args):
    out = []
    for a in args:
        if isinstance(a, dict):
            if not rules_ok(a.get("rules"), features):
                continue
            vals = a["value"] if isinstance(a["value"], list) else [a["value"]]
        else:
            vals = [a]
        for v in vals:
            for k, s in subs.items():
                v = v.replace("${" + k + "}", s)
            out.append(v)
    return out


jvm = ["-Xmx3G", "-Dorg.lwjgl.util.Debug=false"]
if "arguments" in vj:
    jvm += expand(vj["arguments"].get("jvm", []))
    game = expand(vj["arguments"].get("game", []))
else:
    jvm += [f"-Djava.library.path={natives}", "-cp", subs["classpath"]]
    game = expand(vj["minecraftArguments"].split())
# keep only the quick-play option we asked for
clean = []
skip = False
for i, g in enumerate(game):
    if skip:
        skip = False
        continue
    if g.startswith("--quickPlay") and g != "--quickPlaySingleplayer":
        skip = True
        continue
    clean.append(g)
if "--quickPlaySingleplayer" not in clean:
    clean += ["--quickPlaySingleplayer", world]
print("\n".join(["java"] + jvm + [vj["mainClass"]] + clean))
