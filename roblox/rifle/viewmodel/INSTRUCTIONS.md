# Scar viewmodel for the AutoBlaster tool

`ScarViewmodel.rbxmx` replaces `ReplicatedStorage.Blaster.ViewModels.AutoBlaster` in your place.
It was built from your uploaded place file (`game.rbxl`), not from a guess.

## What is in it
- **Only the Scar.** There are no Blaster parts, no extra hand parts, no scripts and no Sound objects.
- **Your normal arms.** `RightArm` and `LeftArm` are 0.6 x 0.6 x 4, the same as now. Your ViewModelController still hides them and adds the sleeves.
- **Your parts, unchanged.**
  - The Scar meshes and texture.
  - `MuzzleAttachment` with `FlashEmitter` and `CircleEmitter`. All 35 properties of each emitter are copied from your place.
- **Joints like the template and your Glock viewmodel:**
  ```
  HumanoidRootPart --BodyJoint--> Body
  Body --RightArmJoint--> RightArm
  Body --LeftArmJoint--> LeftArm
  Body --MagazineJoint--> Magazine
  Body --SlideJoint--> Slide            (charging handle)
  ```
  The hands hang off the gun. When you move the gun in the Animation Editor, the hands come with it.
  Each arm joint sits at the shoulder end of the arm, like your Glock viewmodel, so rotating an arm in the editor swings it from the shoulder.
- **The left hand holds the magazine, low,** in every pose, so it no longer clips up into the gun. LeftArm hangs off Body, not the magazine: the magazine is thrown and swapped in the reload, and an arm attached to it had to turn more than 180 degrees between frames, which Roblox can play as a full spin.
- **The gun has not moved.** Body, Magazine and Slide sit exactly where they are now, relative to `HumanoidRootPart`, so your `adsOffset` (0.9, -0.2, 0) still lines up the sights.
- **`AnimSaves`** holds four animations: `Scar_Idle`, `Scar_Equip`, `Scar_Shoot` and `Scar_Reload`.

## Sounds: nothing to add
Your template plays viewmodel sounds from animation events, in `ReplicatedStorage.Blaster.Utility.bindSoundsToAnimationEvents`:
- An event named `Sound` plays the AudioPlayer of that name from the tool's `Sounds` folder.
- An event named `RandomSound` plays a random child of the folder of that name.

The new animations carry exactly those events:

| Animation | Time | Event | Plays from `StarterPack.AutoBlaster.Sounds` |
|---|---|---|---|
| Equip | 0.000 s | `Sound` = `Equip` | Equip |
| Shoot | 0.000 s | `RandomSound` = `Shoot` | Shoot1, Shoot2 or Shoot3 |
| Reload | 0.233 s | `Sound` = `MagOut` | MagOut |
| Reload | 0.833 s | `Sound` = `MagIn` | MagIn |
| Reload | 1.067 s | `Sound` = `Charger` | Charger |

AimIn and AimOut are played by your ViewModelController when you aim, not by animations.

**Why the gun was silent before:** the old animations had no events, or events named `MagIn`, `Fire` and so on. The template only listens for `Sound` and `RandomSound`.

## Install
1. **Insert.** Drag `ScarViewmodel.rbxmx` into Studio. It appears in Workspace as `AutoBlaster`.
2. **Publish the animations.** Open the Avatar tab, then the Animation Editor, and click the model. For each of `Scar_Idle`, `Scar_Equip`, `Scar_Shoot` and `Scar_Reload`:
   - Use **...** > **Load** to open it.
   - Use **...** > **Publish to Roblox**.
   - Copy the ID.

   The events are already in each animation, so they publish with it.
3. **Paste the IDs.** Put the four IDs into `AutoBlaster.Animations` > `Idle`, `Equip`, `Shoot` and `Reload` > `AnimationId`, written as `rbxassetid://<id>`.
4. **Move it into place.** Delete the old `ReplicatedStorage.Blaster.ViewModels.AutoBlaster` and move this model there. Keep the name `AutoBlaster`, because the tool's `viewModel` attribute points at it.

Until step 3 is done, the `Animations` folder still holds the IDs you have now. Those are the old animations: they have no sound events and they don't match the new arm joints.

**Check your Glock too:** your current AutoBlaster `Reload` ID (`129834366601529`) is the same as the Reload ID in your Glock viewmodel (`ViewModels.Blaster`). Step 3 replaces it for the Scar. Make sure the Glock still has the reload you meant.

## Timing against your tool settings
- **Reload is 1.5 s**, the same as the AutoBlaster's `reloadTime`. The template stretches the reload to `reloadTime`, so this one plays at normal speed. The old 2.35 s reload was being played 1.57 times too fast.
- **Shoot** kicks to its peak at 0.033 s and has nearly settled by 0.1 s. At `rateOfFire` 600 that is one shot every 0.1 s, so full auto stays readable. The charging handle cycles back and forward on every shot. Shoot only moves the gun and the charging handle; the arms ride along on their joints.
- **Priorities:** Idle = Idle, Equip = Action, Shoot = Action2, Reload = Action3. Firing during the equip, and reloading at any time, override cleanly instead of blending.
- **Equip hands off to Idle without a pop.** Your controller starts Equip and Idle together, and Equip ends exactly on the Idle pose for that moment.

## What the animations do
The motion is springy rather than stiff:
- **Overshoot:** the gun swings into each pose, overshoots a little and settles.
- **Arm drag:** the arms lag a beat behind the gun and catch up.
- **Anticipation:** the big moves start with a small counter-move.
- **Bouncy hits:** impacts (mag in, palm slap, bolt home) bounce instead of stopping dead.

The arms otherwise move like your Glock's: they take about 30% of the gun's turn (75% while equipping) and never twist about their own length. No arm joint goes past 45 degrees, so Roblox has nothing to interpolate the long way round.

- **Idle (4 s loop):** a slow breathing sway with the arms swaying a beat behind. Your controller adds walk bob, look sway and jump kick on top.
- **Equip (0.7 s):** the gun swings up from below, pops about 0.16 studs past the hold and springs back. The arms drag behind and the left hand slaps onto the magazine. It ends exactly on the Idle pose.
- **Shoot (0.25 s):** a springy kick that peaks at 0.037 s and swings back through the hold right at the next shot (600 rpm). It rebounds forward slightly and settles. The charging handle cycles on every shot.
- **Reload (1.5 s):**
  1. A quick dip, then the gun swings into the tilt and settles.
  2. The left hand yanks the magazine out and flings it away. It flies down and to the left, spinning, and is off the screen by 0.53 s.
  3. The hand drops out of view and brings a fresh magazine up. It slams home with a bounce, then gets a palm slap.
  4. The hand racks the charging handle, which snaps forward with a bounce.
  5. The hand returns to the magazine and the gun settles.

  Roblox has only one Magazine part, so the same part plays both magazines. It jumps from the thrown position into the hand at 0.55 to 0.57 s. Both of those positions, and the path between them, are off the screen; this is checked against your camera framing.

## Previews
- `previews/*.gif` and `player/` show each animation from two views:
  - **Left:** your game's real camera framing: `VIEW_MODEL_OFFSET` (0.9, -1.3, -1.3) and FOV 70.
  - **Right:** an outside view, similar to what the Animation Editor shows.
- The arms are drawn as their 0.6 x 0.6 x 4 parts. In game your controller hides those parts and shows a sleeve mesh (`rbxassetid://488154609`) in the same place. I could not download that mesh, so the in-game arms will look different from the boxes.

## What was checked, and what wasn't
- The file was checked offline with `tools/viewmodel_v3/verify.py`:
  - It re-parses the `.rbxmx`.
  - It replays every keyframe through the joints the way Roblox's Animator does and compares the result with the intended motion.
  - It checks that every sound event names something in your AutoBlaster's `Sounds` folder.
  - It compares both emitters with your place, property by property.
- I cannot run Studio or your game here. Nothing has been tested in Roblox itself.

## Regenerating
`roblox/rifle/tools/viewmodel_v3/README.md` explains how to rebuild the file from a place file.
