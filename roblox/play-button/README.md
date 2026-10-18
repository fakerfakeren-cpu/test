# PLAY button (Roblox, pixel art)

Colour set A (green). Art grid 64 x 24, exported at 8x (512 x 192).
`make_button.py` regenerates every PNG (`python3 make_button.py`).

## Files (`export/`)

| File | Use |
|---|---|
| `play_normal.png` | button, no text: `IMAGE_NORMAL` |
| `play_hover.png` | button, no text: `IMAGE_HOVER` |
| `play_pressed.png` | button, no text: `IMAGE_PRESSED` |
| `play_icon.png` | play triangle, 80 x 96: `IMAGE_ICON` |
| `play_normal_text.png`, `play_hover_text.png`, `play_pressed_text.png` | same three states with PLAY + icon baked in |

## Upload and IDs

1. Publish the place once (File > Publish to Roblox). Asset Manager needs it.
2. Open Asset Manager (View tab, or Window menu in the new Studio UI) > Images > Bulk Import, and pick
   `play_normal.png`, `play_hover.png`, `play_pressed.png`, `play_icon.png`.
3. Wait until they finish moderation (blank thumbnails = still pending).
4. Right-click each image > Copy Asset ID, and paste the number into `CONFIG` in `PlayButton.client.lua`:
   `IMAGE_NORMAL`, `IMAGE_HOVER`, `IMAGE_PRESSED`, `IMAGE_ICON`.
5. Click sound: Toolbox > Audio, search "click", insert one, copy its `SoundId` number into `CLICK_SOUND`.

If an image shows blank in game, you probably pasted a Decal ID (from the website) instead of an Image ID.
Paste it into any ImageLabel's `Image` property in Studio: Studio converts it to the Image ID, then copy that number.

## Script

`PlayButton.client.lua` goes in StarterPlayer > StarterPlayerScripts as a LocalScript.
It builds `PlayerGui.PlayMenu` with the button at the bottom centre. On click it calls `onPlay()`, which hides
the menu and enables a ScreenGui named `GamemodesGui` if you have one. To return, set
`PlayerGui.PlayMenu.Enabled = true`.

## 9-slice settings (if you set it up by hand)

| Property | Value |
|---|---|
| ScaleType | Slice |
| SliceCenter | `Rect.new(40, 56, 472, 136)` |
| SliceScale | pixel scale / 8 (0.5 at 256 x 96, 0.375 at 192 x 72) |
| ResampleMode | Pixelated |
| Size | multiples of the art: height 24 x scale; width 64 x scale or wider |

The borders keep 5 art pixels at each side (corner staircase + the shine's 3-px inset), 7 at the top
(outline, highlight, glint, and the pressed state's 2-px drop), 7 at the bottom (crease, bevel, outline,
shadow). The same SliceCenter works for all three states.
