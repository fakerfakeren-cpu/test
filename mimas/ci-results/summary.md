# Mimas CI verification (2026-10-15T18:24Z)

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
STATES: 108 distinct block states, 84 block IDs checked against blocks.json
STATES-RESULT: PASS

## Server
function load / runtime problems in session 1: 0 lines (see server_problems.txt)
[18:25:03] [ServerMain/INFO]: Found new data pack file/mimas, loading it automatically
[18:25:03] [ServerMain/INFO]: Found new data pack file/mimascam, loading it automatically
[18:25:05] [Worker-Main-1/INFO]: Loaded 1866 advancements
[18:25:11] [Server thread/INFO]: System chat: There are 3 data pack(s) enabled: [vanilla (built-in)], [file/mimas (world)], [file/mimascam (world)]
[18:25:11] [Server thread/INFO]: System chat: There are no more data packs available
[18:25:15] [Server thread/INFO]: System chat: Running function mimas:build
[18:25:24] [Server thread/INFO]: [Not Secure] [Server] NO-ITEM-DROPS
[18:25:25] [Server thread/INFO]: System chat: -4, -56, -7 has the following block data: {back_text: {has_glowing_text: 1b, color: "yellow", messages: ["", "", "", ""]}, components: {}, is_waxed: 1b, x: -4, y: -56, z: -7, id: "minecraft:hanging_sign", front_text: {has_glowing_text: 1b, color: "yellow", messages: ["ПИЛЕШКИ", "ДЮНЕР", "среден", "5,50 €"]}}
[18:25:26] [Server thread/INFO]: [Not Secure] [Server] MARKER-OK
[18:25:29] [Server thread/INFO]: System chat: Running function mimas:build
[18:25:40] [Server thread/INFO]: System chat: Running function mimas:clear
[18:25:46] [Server thread/INFO]: System chat: #restored has 1 [mimas]
[18:25:47] [Server thread/INFO]: [Not Secure] [Server] MARKER-REMOVED
[18:25:50] [Server thread/INFO]: System chat: Running function mimas:build
session 2 (after restart):
[18:26:21] [Server thread/INFO]: System chat: #restored has 0 [mimas]

## World diffs (actual world vs generator model)
rebuild over an existing build == first build:
mimas:clear restores the original terrain exactly:
mimas:clear after a server restart vs original terrain:

## Client screenshots
- 01_front_day: 1280x720 (F2)
- 02_iso_day: 1280x720 (F2)
- 03_top_day: 1280x720 (F2)
- 04_street_day: 1280x720 (F2)
- 05_takeaway_window: 1280x720 (F2)
- 06_inside_counter: 1280x720 (F2)
- 07_menu_closeup: 1280x720 (F2)
- 08_back_kitchen: 1280x720 (F2)
- 09_staff_side: 1280x720 (F2)
- 10_front_night: 1280x720 (F2)
- 11_street_night: 1280x720 (F2)
- 12_iso_night: 1280x720 (F2)
12 screenshots
