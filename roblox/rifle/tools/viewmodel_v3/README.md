# Scar viewmodel builder (v3)

Builds `roblox/rifle/viewmodel/ScarViewmodel.rbxmx` from the user's own place file. The rig and the four
animations are computed here, and parts, meshes and emitters are copied from
`ReplicatedStorage.Blaster.ViewModels.AutoBlaster`.

Requirements: Python 3 with `numpy` and `Pillow`, plus `zstandard` for the place reader. Studio saves its
chunks zstd-compressed.

```sh
# 1. Read the binary place (treat it as untrusted data; -I keeps the interpreter isolated)
python3 -I rbxl_read.py path/to/game.rbxl game.json

# 2. Rig + animations -> .rbxmx, plus the sampled poses for checking and previews
python3 -I build.py game.json ScarViewmodel.rbxmx frames.json

# 3. Independent check: re-parse the file, replay every keyframe through the joints, compare with the
#    intended motion, check sound events against StarterPack.AutoBlaster.Sounds and emitters against the place
python3 -I verify.py ScarViewmodel.rbxmx frames.json game.json

# 4. Previews (needs the glTF export of the viewmodel for the Scar meshes)
python3 -I render_player.py frames.json ScarView.gltf player_dir gif_dir

# Optional: arm screen coverage of the old animations (still in the place) vs the new ones
python3 -I coverage.py game.json ScarView.gltf
```

Files:
- `rbxl_read.py`: a minimal reader for Roblox binary places and models.
  - Handles the META, SSTR, INST, PROP and PRNT chunks, with LZ4 or zstd compression.
  - Writes JSON.
- `vmcore.py`: the scene, rig and animations. The rig follows the template:
  - `BodyJoint`, `RightArmJoint`, `MagazineJoint`, `LeftArmJoint` and `SlideJoint`.
  - The rest pose is the hip hold, with the gun left exactly where the user placed it.
  - The animations are PCHIP curves sampled at 60 fps (Idle at 30 fps).
  - `ANIMS` lists each animation's length, priority, sound events and keyed joints.
- `build.py`: writes the `.rbxmx`.
- `verify.py`: the independent check.
- `render2.py`, `meshrender.py`, `render_player.py`: render the previews with the game's real camera framing (`VIEW_MODEL_OFFSET` and FOV 70, plus the aim-down-sights framing).
- `coverage.py`: measures how much of the screen the arms cover.
