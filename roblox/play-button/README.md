# PLAY button (Roblox, pixel art)

Green PLAY button with text and play icon baked in, 512 x 192 (64 x 24 art pixels at 8x).

| File | ImageButton property |
|---|---|
| `export/play_normal.png` | `Image` |
| `export/play_hover.png` | `HoverImage` |
| `export/play_pressed.png` | `PressedImage` |

Set `ResampleMode = Pixelated`, `BackgroundTransparency = 1`, and a size that is a whole multiple of
64 x 24 (192 x 72, 256 x 96, 320 x 120) so the pixels stay sharp.

`make_button.py` regenerates the PNGs (`python3 make_button.py`).
