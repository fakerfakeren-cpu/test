# Lobby (greybox)

`Lobby.rbxmx` is a walkable layout made of plain anchored parts in flat matte colours (no neon). The signs use the pixel font Press Start 2P. It has no scripts. `preview.png` shows it from above and from the spawn.

## Install
1. Drag `Lobby.rbxmx` into Studio. It lands in Workspace with its floor at height 300, well above your baseplate and test map. Move it with the model's pivot if you want it somewhere else.
2. Delete or disable the old `Workspace.SpawnLocation` (set `Enabled` off), so players spawn on `LobbySpawn`.
3. Drag your target dummies onto the white `Target15` to `Target60` spots in the range. The numbers are distances in studs from the yellow shooting line.

## What's in it
| Part | What it is |
|---|---|
| `Floor` | 10-stud checker tiles: a 120 x 100 plaza, plus a 70 x 30 range off the west side. |
| `Walls` | 10-stud walls with a darker trim. The range has a 14-stud backstop. |
| `LobbySpawn` | Faces the pads, so new players see them first. It has no spawn shield (`Duration` 0). |
| `Pads/<mode>/<pad>` | Three 1v1, two 2v2, one 3v3, one 4v4, plus the Infection `Zone`. |
| `Range/RangeZone` | An invisible box, used later to give guns only while a player is inside the range. |

Each pad has:
- standing spots `A1..An` (blue) and `B1..Bn` (red);
- a `SignBoard` whose `Sign.Count` label shows the queue count.

The back-row signs sit higher, so they read over the front row from the spawn. The front-row signs start 6 studs up, so players walk under them.

The pads don't do anything yet. The queue code (milestone 2) will:
- read the team size from the number of `A` spots;
- update the `Count` label;
- teleport a full pad into an arena.

## Rebuilding
To change sizes, colours or positions, edit `tools/build_lobby.py`, then run:

```sh
python3 tools/build_lobby.py Lobby.rbxmx preview.png
```
