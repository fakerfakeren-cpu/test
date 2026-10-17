# Scar third-person animations (what other players see)

`ScarCharacterAnims.rbxmx` holds an `AnimSaves` with three KeyframeSequences for your R15 rig:

| Sequence | Length | Priority | Plays as |
|---|---|---|---|
| `Scar3P_Idle` | 4.0 s, loops | Action | `AutoBlaster.Animations.Idle` |
| `Scar3P_Shoot` | 0.2 s | Action2 | `AutoBlaster.Animations.Shoot` |
| `Scar3P_Reload` | 1.5 s | Action3 | `AutoBlaster.Animations.Reload` |

There are no scripts, no parts and no sounds. The only thing in your game that changes besides the animation IDs is one property, `Tool.Grip`, in step 1.

## 1. Set the Grip once (required)
Right now your tool puts the right hand under the stock, 1.2 studs behind the pistol grip, with the gun sticking straight out of the fist. That is how a default Roblox tool is held. In these animations the right hand is on the pistol grip and the stock is in the shoulder. That needs the gun to sit differently in the hand, and `Tool.Grip` is what sets that.

Open View > Command Bar in Studio and run:

```lua
local t = game.StarterPack.AutoBlaster
print(t.Grip)  -- the default (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1), or the value from my first version (-0.025422, -0.053325, ...)
t.Grip = CFrame.new(-0.081722, -0.105072, -0.488714, 0.546268, 0.449282, 0.706921, -0.642160, 0.766517, 0.009067, -0.537793, -0.458909, 0.707235)
```

- The value is absolute, so running it twice is harmless.
- It assumes the Grip is the default or my first version's value. Your `Export.gltf` showed the default, and so did your earlier place file. If the print shows anything else, don't run the last line: send me the printed value.
- **If you already ran my first version's line, run this one too.** The straight hold sits differently in the hand. With the old value the gun would be twisted.
- Without this step the animations still play, but the gun floats in the wrong place.

## 2. Publish the animations
1. Insert `ScarCharacterAnims.rbxmx` into Studio. It appears as `AnimSaves`.
2. Move the three `Scar3P_*` sequences into your R15 Rig's `AnimSaves`. If the rig doesn't have one, move the whole `AnimSaves` into the rig.
3. In the Animation Editor, select the rig. For each sequence:
   - Use **...** > **Load** to open it.
   - Use **...** > **Publish to Roblox**.
   - Copy the ID.
4. Paste the IDs into `StarterPack.AutoBlaster.Animations` > `Idle`, `Shoot` and `Reload` > `AnimationId`, written as `rbxassetid://<id>`. Those are the template's IDs today: 17747384020, 17747381445 and 17747385966.

In the Animation Editor the gun may still sit in its old spot. The editor shows whatever weld your rig has, not the tool's Grip. In game, step 1 decides where the gun goes.

## How it works with your LookReplication script
- The animations only rotate the Waist, Neck, shoulders, elbows and wrists. Your script edits each joint's `C0` (or the AnimationConstraint attachment). Roblox applies `C0` first and the animation's Transform after it, so the two stack instead of fighting.
- Both shoulders pitch about the same line, so the arms and the gun turn as one piece. The left hand stays exactly on the magazine whatever the player looks at. This was checked at +60, +30, -30 and -50 degrees, in all three animations.
- The muzzle follows the look:

  | Look | Muzzle | Side drift |
  |---|---|---|
  | ±30° | about ±29.5° | under 1.5° |
  | +60° | 58.5° | 4° |
  | -50° | -49° | 3° |

  The small remainder comes from the torso's 15° turn: your script pitches the arms about the turned torso's axis.
- **The gun tilts when the player looks up or down.** That is your script doing what you asked, not the hold. Looking up 25° makes the gun point 25° up, which from the side reads as a tilted gun.
- `HumanoidRootPart` and `LowerTorso` are placeholders with Weight 0, the same as your existing R15 animations. Walking and running still drive the hips and legs.

## What the animations do
- **The hold is straight:**
  - The gun is level and points exactly where the character faces.
  - It sits in front of the chest, 0.1 studs right of centre, with the bore at chest height and the butt against the chest.
  - The torso turns only 15° (left shoulder forward) and leans 10° in. The head stays level and faces forward.
  - The right hand is on the pistol grip, elbow out. The left hand holds the back of the magazine, low. Both elbows are bent about 50°.

  **Why not on the right shoulder:** the first version had the gun there with the torso turned 35°. That made the gun lie diagonally across the body from most angles, which is the tilt in your screenshot. R15 arms are too short for the left hand to reach a gun on the right shoulder with a square torso, so the gun moved to the centre instead.
- **Idle (4 s loop):** slow breathing and a slight sway, kept small so that Shoot and Reload start and end on it without a pop.
- **Shoot (0.2 s):**
  - The gun kicks 0.1 studs back with a 6° muzzle rise, peaking at 33 ms, and the torso rocks back.
  - It has mostly recovered by 0.1 s, the next shot at 600 rpm, and is back on the hold at 0.2 s. On full auto it reads as a steady shudder, not a stutter.
- **Reload (1.5 s):**

  | Time | What happens |
  |---|---|
  | 0.24 s | The gun cants 30° and the left hand yanks the magazine down. |
  | 0.46 to 0.56 s | The hand drops to the belt. |
  | 0.83 s | The hand comes up under the magwell and shoves the new magazine home; the gun bumps. |
  | 1.07 to 1.15 s | The hand goes round the gun's left side and racks the charging handle. |
  | 1.5 s | Back to the hold. |

  These times match your first-person MagOut (0.23), MagIn (0.83) and Charger (1.07) sounds. The template stretches Reload to `reloadTime`, and 1.5 s is speed 1.
- **The magazine part never leaves the gun.** Character animations can only move body joints, and the gun is welded to the hand. The hand motion carries the reload. That is normal for third person, and at fighting distance it reads clearly.

## Limits
- **Body shapes:** the hold is built for the standard blocky R15 proportions, the ones in your export. On other body shapes it still forms, because every pose is a pure rotation, but the left hand can sit off the magazine by however much those arms differ.
- **Clipping:**
  - The butt of the stock sinks about 0.12 studs into the chest on purpose, so it reads as braced.
  - Blocky hands are 1x1 plates, wider than the grip, so they overlap the gun a little.
- **Not tested in Roblox.** I can't run Studio here. `tools/character/verify_char.py` checks the file offline:
  - It re-parses the `.rbxmx` and replays every keyframe the way Roblox does, with your script's `C0` offsets on top.
  - It hangs the gun on the hand through the new Grip.
  - It checks that the hand stays on the gun, that no joint flips between frames, that the loop closes, and that Shoot and Reload start and end on Idle.

## Previews
`previews/Idle.gif`, `Shoot.gif` and `Reload.gif` show each animation from the front-right and from the right side. The character is drawn as plain boxes, with your Scar meshes in the hand.
