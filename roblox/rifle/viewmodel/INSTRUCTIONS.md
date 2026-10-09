# Scar viewmodel: setup script + 4 animations

## Drop-in model: `ScarViewmodel.rbxmx`
A ready-made copy of your viewmodel with the blaster removed, the Scar rigged and the four animations inside
(`AutoBlaster.AnimSaves`). Drag it into Studio (or right-click a service > Insert from File).

- It was rebuilt from `ScarView.gltf`: same arm and gun positions, your own Scar mesh IDs
  (Body `131917924785503`, Magazine `80480420910453`, Slide `82150188184524`) and palette `96279669712196`.
- The export did not contain the root part, the joints or the AnimationController, so the file adds them:
  an invisible anchored `HumanoidRootPart` at the model pivot (the PrimaryPart), Motor6Ds `RightShoulder`,
  `LeftShoulder` and `Scar` on it, and `Magazine`/`Slide` Motor6Ds on `Scar.Body`.
- Anything else your original viewmodel had that the export could not include (scripts, attributes, values,
  a differently named root part) is not in this file. If your template code expects those, either copy them over
  or run the setup script below on your original viewmodel instead.
- After inserting: publish the four KeyframeSequences from `AnimSaves` in the Animation Editor, as described below.

`ScarViewmodelSetup.lua` is a one-time Studio command-bar script. It removes the template blaster from your
viewmodel, rigs the Scar with the blaster's own joint, and builds four animations
(Equip, Shoot, Reload, Idle) against **your actual rig**.

It is a script rather than a ready-made model because Roblox's glTF export drops Motor6Ds,
the AnimationController, invisible parts and Roblox-owned meshes (the template blaster). Those are exactly the
things the animations depend on. The script finds them in Studio instead.

## Run it
1. Open the place. In the Explorer, select the viewmodel Model (`AutoBlaster`, the one with the
   AnimationController, RightArm/LeftArm, `Blaster` and your `Scar`).
2. View > **Command Bar**, paste the whole script, press Enter.
3. Read the Output window. It lists every change: backup made, parts moved, joints re-pointed, animations made.

Undo: Ctrl+Z straight away, or use the full copy it saves to `ServerStorage.<name>_Backup`.

## What it changes (nothing is deleted)
- **Backup:** a full clone of the viewmodel goes to `ServerStorage.<name>_Backup`.
- **Blaster:** its visible parts move to `ServerStorage.<name>_BlasterParts`. The `Blaster` model itself stays,
  with its folders, config, attributes and `Body_attachments`. Attachments on the blaster parts (with their particle
  emitters and lights), sounds, scripts and values move onto `Scar.Body`. Any attachment with "Muzzle" in its
  name is placed at the Scar's muzzle.
- **Joints:** the blaster's Motor6D now drives `Scar.Body`. It keeps the same name, parent, Part0 and C0, and C1 is
  solved so the Scar stays exactly where you placed it. `Body` gets Motor6Ds named `Magazine` and `Slide`
  so the magazine and charging handle can move.
- **Scar parts:** unanchored, CanCollide/CanTouch/CanQuery off, Massless, CastShadow copied from the blaster.
- **Muzzle:** a `Muzzle` Attachment on `Scar.Body` at the muzzle, LookVector = firing direction.
  `Blaster.Body_attachments.Muzzle_Att` stays where it is in the Explorer, but is moved to the Scar's muzzle and
  welded to `Body`, so it follows recoil and reloads.
- **Rig root:** if the blaster itself was the rig root or PrimaryPart, an invisible anchored `ScarRoot` replaces it
  at the same pivot, so the template's camera code keeps working.
- **Animations:** four KeyframeSequences in `<viewmodel>.AnimSaves`.

## Publish the animations and hook them up
1. Avatar tab > **Animation Editor**, click the viewmodel.
2. `...` > **Load** > `Scar_Idle` (and so on). Press play to preview. You can still edit them here.
3. `...` > **Publish to Roblox**, then copy the asset ID.
4. Put the four IDs where the AutoBlaster's animations were. The Output prints every `Animation` object it found
   in the viewmodel with its current ID, to help you find them.

| Animation | Length | Loop | Priority | What happens |
|---|---|---|---|---|
| `Scar_Idle` | 3.2 s | yes | Idle | slow breathing sway (bob, small tilt and roll), seamless loop |
| `Scar_Equip` | 0.6 s | no | Action | swings up from low right with a small overshoot, settles into the hold |
| `Scar_Shoot` | 0.14 s | no | Action | sharp kick back and up, charging handle cycles, fast recovery (short enough for full auto) |
| `Scar_Reload` | 2.35 s | no | Action2 | cant right, left hand pulls the mag, swaps it below the screen, seats it with a bump, palm tap, racks the charging handle, back to the forend |

The animations are baked at 60 fps (idle at 30) from smooth monotone curves, so there are no keyframe pops.
The right hand stays on the grip and the left hand on the forend, magazine or charging handle in every frame:
the arms are re-aimed every frame so the hands track the gun.

## How it was tested
I don't have Roblox Studio here. The script was run with the real Luau interpreter against a mock Roblox API, on
your viewmodel rebuilt from `ScarView.gltf` with five different guesses at the template's hidden rig:
- arms and blaster on a root part;
- unusual joint frames;
- blaster carried by the right arm;
- blaster as the rig root and PrimaryPart;
- blaster as PrimaryPart under a root;

plus running the script twice. Results in every case:
- The Scar moved 0 studs and the model pivot moved 0 studs.
- Every Pose matched a joint.
- The hands stayed on their targets to within 1e-14 studs.
- The idle loop seam is exact.

`previews/*.gif` are rendered from those tested keyframes. The left half is a first-person view from a
**guessed** camera position (your export does not contain the camera setup); the right half is an outside view.

To re-run the tests: `python3 tools/viewmodel_test/run.py 1` (needs the `luau` CLI next to it).
