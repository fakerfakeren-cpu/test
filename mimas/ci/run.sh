#!/usr/bin/env bash
# CI verification for the Mimas data pack on a real vanilla server + client.
# Results go to mimas/ci-results/ (committed back by the workflow).
set -u
VER="${MC_VERSION:-26.3}"
ROOT="$(pwd)"
WORK="$ROOT/ci_work"
RES="$ROOT/mimas/ci-results"
mkdir -p "$WORK"
rm -rf "$RES"; mkdir -p "$RES/shots"
SUM="$RES/summary.md"
note() { echo "$*" | tee -a "$SUM"; }

note "# Mimas CI verification ($(date -u +%Y-%m-%dT%H:%MZ))"
note ""
python3 mimas/ci/fetch_mc.py "$VER" "$WORK/mc" --client 2>&1 | tail -5 || true
[ -f "$WORK/mc/server.jar" ] || { note "FATAL: could not download $VER"; exit 1; }

# ---- version info (pack format) ----------------------------------------------------------
unzip -p "$WORK/mc/server.jar" version.json > "$WORK/version.json"
python3 - "$WORK/version.json" "$WORK/mc/$VER.json" > "$ROOT/mimas/tools/version_info.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1])); vj = json.load(open(sys.argv[2]))
pv = v.get("pack_version")
if isinstance(pv, dict):
    data = [pv.get("data_major", pv.get("data")), pv.get("data_minor", 0)]
    res = [pv.get("resource_major", pv.get("resource")), pv.get("resource_minor", 0)]
else:
    data, res = [pv, 0], [pv, 0]
print(json.dumps({"version": v.get("id", v.get("name")), "data_pack_format": data, "resource_pack_format": res,
                  "java": vj.get("javaVersion"), "world_version": v.get("world_version"),
                  "raw_pack_version": pv}, indent=2))
PY
note '```'; cat "$ROOT/mimas/tools/version_info.json" | tee -a "$SUM"; note '```'
read MAJ MIN < <(python3 -c "import json;d=json.load(open('$ROOT/mimas/tools/version_info.json'))['data_pack_format'];print(d[0],d[1])")

# ---- block report from the game itself -----------------------------------------------------
(cd "$WORK" && java -DbundlerMainClass=net.minecraft.data.Main -jar mc/server.jar --reports --output gen > datagen.log 2>&1)
BLOCKS=$(find "$WORK/gen" -name blocks.json | head -1)
note "block report: ${BLOCKS:-MISSING}"
python3 mimas/tools/build.py --no-render | tee "$RES/generator.txt"
python3 mimas/ci/verify.py states mimas/datapack "$BLOCKS" | tee "$RES/states.txt"
python3 mimas/ci/verify.py interest "$BLOCKS" > "$RES/interest.txt"
grep -E "STATES(-RESULT)?:" "$RES/states.txt" | tee -a "$SUM"

# ---- dedicated server session 1 ------------------------------------------------------------
SRV="$WORK/server"
rm -rf "$SRV"; mkdir -p "$SRV/world/datapacks"
cp -r mimas/datapack "$SRV/world/datapacks/mimas"
python3 mimas/ci/camera.py "$SRV/world/datapacks/mimascam" "$MAJ" "$MIN" 0 -60 0
echo "eula=true" > "$SRV/eula.txt"
cat > "$SRV/server.properties" <<'PROPS'
online-mode=false
level-type=minecraft\:flat
level-seed=mimas
spawn-protection=0
max-tick-time=-1
view-distance=6
simulation-distance=4
pause-when-empty-seconds=0
generate-structures=false
spawn-monsters=false
PROPS

start_server() {
  rm -f "$SRV/in"; mkfifo "$SRV/in"
  (cd "$SRV" && exec java -Xmx3G -jar ../mc/server.jar nogui < in > "server_$1.log" 2>&1) &
  SPID=$!
  exec 3<>"$SRV/in"
  LOG="$SRV/server_$1.log"
  for i in $(seq 1 240); do grep -q "Done (" "$LOG" 2>/dev/null && break; sleep 1; done
}
send() { echo "$*" >&3; sleep "${2:-1}"; }
cmd() { echo "$1" >&3; sleep "${2:-2}"; }
save_snap() {
  local before; before=$(grep -c "Saved the game" "$LOG")
  echo "save-all flush" >&3
  for i in $(seq 1 60); do [ "$(grep -c "Saved the game" "$LOG")" -gt "$before" ] && break; sleep 1; done
  sleep 1
  REG=$(find "$SRV/world" -type d -name region | grep -vE "DIM-?1|nether|the_end" | head -1)
  rm -rf "$WORK/snap_$1"; cp -r "$REG" "$WORK/snap_$1"
}
stop_server() { echo "stop" >&3; wait "$SPID" 2>/dev/null; exec 3>&-; }

start_server 1
cmd "forceload add -48 -48 48 48" 4
cmd "datapack list" 2
save_snap pre
cmd "execute positioned 0 -60 0 run function mimas:build" 8
cmd "execute if entity @e[type=item] run say ITEMS-DROPPED" 1
cmd "execute unless entity @e[type=item] run say NO-ITEM-DROPS" 1
cmd "data get block -4 -56 -7" 1
cmd "execute if entity @e[type=marker,tag=mimas_origin] run say MARKER-OK" 1
save_snap built
cmd "execute positioned 0 -60 0 run function mimas:build" 8
save_snap rebuilt
cmd "function mimas:clear" 6
cmd "scoreboard players get #restored mimas" 1
cmd "execute unless entity @e[type=marker,tag=mimas_origin] run say MARKER-REMOVED" 1
save_snap cleared
cmd "execute positioned 0 -60 0 run function mimas:build" 8
save_snap final
stop_server
rm -rf "$WORK/world_built"; cp -r "$SRV/world" "$WORK/world_built"; rm -f "$WORK/world_built/session.lock"

# ---- dedicated server session 2: undo after a restart ---------------------------------------
start_server 2
cmd "forceload add -48 -48 48 48" 4
cmd "function mimas:clear" 6
cmd "scoreboard players get #restored mimas" 1
save_snap after_restart_clear
stop_server

S1="$SRV/server_1.log"; S2="$SRV/server_2.log"
cp "$S1" "$RES/server_session1.log"; cp "$S2" "$RES/server_session2.log"
note ""
note "## Server"
grep -nE "Failed to|Couldn't|rror|Unknown|nvalid|xception|Missing|Whilst" "$S1" | grep -viE "realms|narrator" | head -40 | tee "$RES/server_problems.txt"
note "function load / runtime problems in session 1: $(wc -l < "$RES/server_problems.txt") lines (see server_problems.txt)"
grep -E "Executed|Running function|ITEMS-DROPPED|NO-ITEM-DROPS|MARKER-|#restored|messages|Loaded [0-9]+ |data pack|datapack|\[file/" "$S1" | cut -c1-400 | tee -a "$SUM"
note "session 2 (after restart):"
grep -E "Executed|#restored|Failed|rror" "$S2" | cut -c1-300 | tee -a "$SUM"

note ""
note "## World diffs (actual world vs generator model)"
python3 mimas/ci/verify.py built "$WORK/snap_built" mimas/tools/expected_blocks.json 0 -60 0 "$BLOCKS" 2>&1 | tee "$RES/diff_built.txt" | grep -E "^BUILT(-RESULT|:| -MISMATCH-KIND)" | tee -a "$SUM"
note "rebuild over an existing build == first build:"
python3 mimas/ci/verify.py same "$WORK/snap_built" "$WORK/snap_rebuilt" mimas/tools/expected_blocks.json 0 -60 0 "$BLOCKS" 2>&1 | tee "$RES/diff_rebuild.txt" | grep -E "SAME(-RESULT)?:" | tee -a "$SUM"
note "mimas:clear restores the original terrain exactly:"
python3 mimas/ci/verify.py same "$WORK/snap_pre" "$WORK/snap_cleared" mimas/tools/expected_blocks.json 0 -60 0 "$BLOCKS" 2>&1 | tee "$RES/diff_clear.txt" | grep -E "SAME(-RESULT)?:" | tee -a "$SUM"
note "mimas:clear after a server restart vs original terrain:"
python3 mimas/ci/verify.py same "$WORK/snap_pre" "$WORK/snap_after_restart_clear" mimas/tools/expected_blocks.json 0 -60 0 "$BLOCKS" 2>&1 | tee "$RES/diff_restart_clear.txt" | grep -E "SAME(-RESULT)?:" | tee -a "$SUM"

# ---- real client screenshots ----------------------------------------------------------------
note ""
note "## Client screenshots"
GAME="$WORK/client"
rm -rf "$GAME"; mkdir -p "$GAME/saves"
cp -r "$WORK/world_built" "$GAME/saves/world"
printf 'onboardAccessibility:false\nrenderDistance:8\nsimulationDistance:5\npauseOnLostFocus:false\ntutorialStep:none\nguiScale:2\nsoundCategory_master:0.0\nfov:0.0\nskipMultiplayerWarning:true\njoinedFirstServer:true\n' > "$GAME/options.txt"
python3 mimas/ci/launch_client.py "$WORK/mc" "$VER" "$GAME" world > "$WORK/launch_args.txt"
cat > "$WORK/client.sh" <<SH
mapfile -t ARGS < "$WORK/launch_args.txt"
(cd "$GAME" && exec "\${ARGS[@]}") > "$GAME/client.log" 2>&1 &
CPID=\$!
python3 "$ROOT/mimas/ci/shot_driver.py" "$GAME/client.log" "$GAME" "$WORK/shots" \$CPID
wait \$CPID 2>/dev/null
SH
export LIBGL_ALWAYS_SOFTWARE=1 SDL_VIDEODRIVER=x11 GALLIUM_DRIVER=llvmpipe
timeout 1800 xvfb-run -a -s "-screen 0 1280x720x24" bash "$WORK/client.sh" || true
cp "$GAME/client.log" "$RES/client.log" 2>/dev/null || true
grep -nE "rror|xception|Failed|CAM\]" "$GAME/client.log" | grep -viE "realms|narrator|OpenAL|ALSA|audio|sound" | cut -c1-300 | head -60 > "$RES/client_problems.txt"
python3 - "$WORK/shots" "$RES/shots" <<'PY' | tee -a "$SUM"
import glob, os, sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
names = sorted({os.path.basename(p).replace("_x11.png", "").replace(".png", "") for p in glob.glob(src + "/*.png")})
for n in names:
    p = os.path.join(src, n + ".png")
    kind = "F2"
    if not os.path.exists(p):
        p, kind = os.path.join(src, n + "_x11.png"), "X11"
    im = Image.open(p).convert("RGB")
    im.save(os.path.join(dst, n + ".jpg"), quality=88)
    print(f"- {n}: {im.size[0]}x{im.size[1]} ({kind})")
print(f"{len(names)} screenshots")
PY
echo "done"
