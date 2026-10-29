# 2D terrain renderer test bench (Roblox)

A throwaway test, not a game. It checks whether `EditableImage` chunks can carry a
Terraria-style world on Roblox before any real development starts.

## Setup

1. Make a new **empty** place (delete the Baseplate so the 3D scene costs nothing).
2. Publish it, then in **Game Settings** turn on **Allow Mesh / Image APIs**.
3. Optional: in **Players** set `CharacterAutoLoads` to false.
4. Add a **LocalScript** under `StarterPlayer > StarterPlayerScripts` and paste
   `TerrainBench.client.luau` into it.
5. Press Play. To test on a phone, publish and join from a low-end Android device.

The window size is read once when the script starts. After resizing the window or
rotating the phone, rejoin.

## What it does

- Generates a 1600×608 tile world (surface, dirt, stone, caves, ore, torches), stored as bytes in `buffer`s.
- Draws 32×32-tile chunks into a **fixed set of 256×256 EditableImages** that is created once and
  reused (about 256 KB each). Walls and tiles are merged into one image.
- Edits a single tile by writing just that 8×8 area. A chunk is only fully redrawn
  when it comes into view.
- Lighting is one EditableImage with one pixel per tile, recomputed 30 times per second by default. The player's light follows their exact position, not just whole tiles.
- 50 mobs share one sprite image. Collision is tile-grid AABB, and there are up to 200 particles.

## Using your own tile art

A ready-made sheet is in `art/tiles.png`. `art/tiles_preview.png` is a zoomed-in copy for
viewing, and `art/make_tiles.py` regenerates both if you edit the pixel maps.

Upload the PNG tile sheet as an image asset owned by you or the group that owns the game,
then set `ATLAS_ASSET_ID` at the top of the script to its asset ID. Layout, with 8×8 px tiles and no padding:

- **Row 0 (y 0–7):** air, dirt, grass, stone, ore, torch. The air slot is ignored.
- **Row 1 (y 8–15):** no wall, dirt wall, stone wall. The no-wall slot is ignored.

The minimum size is 48×16. Transparent pixels in a foreground tile show the wall behind it.
The sheet is read into a buffer once and its EditableImage is destroyed right away,
so it costs nothing against the image memory budget. The HUD's `tiles:` field shows whether
the sheet loaded, or why it didn't.

### Or one image per tile

`art/single/` has one 64×64 PNG per tile: `dirt`, `grass`, `stone`, `ore`, `torch`,
`dirt_wall` and `stone_wall`. They are the 8×8 tiles scaled up 8× with no smoothing. Upload each one,
then put its asset ID in the matching entry of the `TILE_ASSETS` table at the top of the script.
The script scales them back down to the exact 8×8 pixels. Any entry left at 0 keeps
the sheet or generated texture, so you can replace tiles one at a time. A tile image can be any
square size that is a multiple of 8. The HUD's `tiles:` field lists each one that loaded, or `<name> FAILED`.

## Controls

- **Keyboard and mouse:** A/D move, Space jump, hold left mouse to dig, hold right mouse to place dirt, T places a torch.
- **Touch:** hold a finger to dig. Bench mode starts on by default.
- **Bench mode:** the camera pans across the world, going between the sky and the caves, and
  makes 30 random tile edits per second. It needs no input, so it works for phone tests.

## Buttons

| Button | What it tests |
|---|---|
| Bench | Starts and stops bench mode. |
| Uploads/frame | Caps full chunk uploads per frame (1, 2, 4, 8, unlimited). |
| Flash all chunks | Re-tints and re-uploads **every** loaded chunk in one frame. **Watch the screen:** if every chunk changes color at once, there is no hidden one-update-per-frame limit. If they change one after another over several frames, the limit is real. |
| Lighting | Turns lighting on or off to isolate its cost. |
| Light rate | How often lighting is recalculated: 10, 20, 30 (default) or 60 per second. Higher looks smoother and costs more. |
| Light look | Switches between smooth light (default) and blocky light (pixel). |
| Probe memory budget | Creates extra 256×256 images until creation fails, then frees them, and reports the real client budget. It runs **once per session**. It prints one `Failed to create empty EditableImage ... memory budget limits` warning, which is expected: hitting the limit is how it measures it. When it finishes, the button shows the measured budget. Rejoin to run it again. |

## Pass / fail

Run bench mode for 2 minutes on a **low-end Android phone** and on PC.

| Check | Pass |
|---|---|
| FPS in bench mode | PC: 60. Phone: 30 or higher |
| Worst frame | Under about 50 ms on the phone, with no regular stutter while scrolling |
| Pool shortages | 0 |
| "All images created OK" | Yes |
| Probe headroom | At least 10 MB left above what the pool uses |
| Flash all chunks | All chunks change in the same frame, or within 2–3 frames |
| Light ms | Under about 2 ms on the phone |

If it passes, commit to the game. If FPS is low, turn lighting off and
set uploads/frame to 1 to find which part is responsible. Then send the HUD numbers back.

The HUD timings are CPU time on the Lua side. The GPU work of uploading the image
is not included. That's why FPS and the flash test matter more than the ms numbers.
