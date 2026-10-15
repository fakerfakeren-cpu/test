# Mimas CI verification (2026-10-15T19:35Z)

```
{
  "version": "26.3",
  "data_pack_format": [
    121,
    0
  ],
  "resource_pack_format": [
    97,
    1
  ],
  "java": {
    "component": "java-runtime-epsilon",
    "majorVersion": 25
  },
  "world_version": 5023,
  "raw_pack_version": {
    "resource_major": 97,
    "resource_minor": 1,
    "data_major": 121,
    "data_minor": 0
  }
}
```
block report: /home/runner/work/test/test/ci_work/gen/reports/blocks.json
STATES: 115 distinct block states, 88 block IDs checked against blocks.json
STATES-RESULT: PASS

## Server
function load / runtime problems in session 1: 0 lines (see server_problems.txt)
[19:35:29] [ServerMain/INFO]: Found new data pack file/mimas, loading it automatically
[19:35:29] [ServerMain/INFO]: Found new data pack file/mimascam, loading it automatically
[19:35:31] [Worker-Main-2/INFO]: Loaded 1866 advancements
[19:35:36] [Server thread/INFO]: System chat: There are 3 data pack(s) enabled: [vanilla (built-in)], [file/mimas (world)], [file/mimascam (world)]
[19:35:36] [Server thread/INFO]: System chat: There are no more data packs available
[19:35:40] [Server thread/INFO]: System chat: Running function mimas:build
[19:35:49] [Server thread/INFO]: [Not Secure] [Server] NO-ITEM-DROPS
[19:35:50] [Server thread/INFO]: System chat: -4, -56, -7 has the following block data: {back_text: {has_glowing_text: 1b, color: "yellow", messages: ["", "", "", ""]}, components: {}, is_waxed: 1b, x: -4, y: -56, z: -7, id: "minecraft:hanging_sign", front_text: {has_glowing_text: 1b, color: "yellow", messages: ["ПИЛЕШКИ", "ДЮНЕР", "среден", "5,50 €"]}}
[19:35:51] [Server thread/INFO]: [Not Secure] [Server] MARKER-OK
[19:35:54] [Server thread/INFO]: System chat: Running function mimas:build
[19:36:04] [Server thread/INFO]: System chat: Running function mimas:clear
[19:36:10] [Server thread/INFO]: System chat: #restored has 1 [mimas]
[19:36:11] [Server thread/INFO]: [Not Secure] [Server] MARKER-REMOVED
[19:36:14] [Server thread/INFO]: System chat: Running function mimas:build
session 2 (after restart):
[19:36:46] [Server thread/INFO]: System chat: #restored has 0 [mimas]

## World diffs (actual world vs generator model)
BUILT: compared 24336 positions, 6290 expected non-air, 0 mismatches
BUILT-RESULT: PASS
rebuild over an existing build == first build:
SAME: 0 differences over 24336 positions
SAME-RESULT: PASS
mimas:clear restores the original terrain exactly:
SAME: 0 differences over 24336 positions
SAME-RESULT: PASS
mimas:clear after a server restart vs original terrain:
SAME: 0 differences over 24336 positions
SAME-RESULT: PASS

## Client screenshots
- 01_front_day: 1280x720 (F2)
- 02_iso_day: 1280x720 (F2)
- 03_top_day: 1280x720 (F2)
- 04_street_day: 1280x720 (F2)
- 05_takeaway_window: 1280x720 (F2)
- 06_inside_counter: 1280x720 (F2)
- 07_menu_closeup: 1280x720 (F2)
- 08_grill_line: 1280x720 (F2)
- 09_back_kitchen: 1280x720 (F2)
- 10_staff_side: 1280x720 (F2)
- 11_front_night: 1280x720 (F2)
- 12_street_night: 1280x720 (F2)
- 13_iso_night: 1280x720 (F2)
13 screenshots
