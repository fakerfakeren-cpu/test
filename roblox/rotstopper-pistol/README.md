# Rotstopper: blocky sidearm for Roblox

A PG3D-inspired pistol for a zombie PvP game. It's chunky, built from blocks, and uses flat saturated
colours. Every moving piece is a separate part, rigged with Motor6Ds so you can animate it.

![preview](preview.png)

## Files

| File | What it is |
|---|---|
| `build_rotstopper.lua` | **Use this.** Paste it into the Studio command bar and it builds a rigged `Tool` in StarterPack |
| `rotstopper.obj` / `.mtl` | The same model for Blender: one object per component, one stud = one unit |
| `tools/gen_rotstopper.py` | Source of truth. Edit sizes, colours or positions here and rerun it to regenerate everything |
| `preview.png` | Renders from the generator |

## Build it in Studio

1. Open **View → Command Bar**.
2. Paste the whole `build_rotstopper.lua` file and press Enter.
3. `StarterPack.Rotstopper` appears and is selected. Running the script again replaces it.

The barrel points along the Handle's front (-Z), and the Handle sits in the centre of the grip.
The default `Tool.Grip` should therefore put the gun in the hand pointing forward. If it sits
slightly off in your game, change `Tool.Grip` and don't move the parts.

## Rig

```
Handle (invisible root, the hand holds this)
├─ Weld    Frame      static: frame, beavertail, rail, trigger guard
├─ Weld    Grip       static: grip, olive panels, emblem, grooves
├─ Motor6D Slide      rack: move +Z about 0.32 studs (sights, stripe and serrations ride along)
├─ Motor6D Barrel     pivot at the breech: tilt a few degrees on lock-back
├─ Motor6D Magazine   pivot axes follow the grip rake, so pulling along its -Y drops it straight out
├─ Motor6D Trigger    pivot at the top of the blade: rotate on X to pull
├─ Motor6D Hammer     pivot at the hinge: rotate on X to cock
└─ Motor6D SlideStop  lever on the left side: nudge up on an empty reload
```

The small detail parts are children of their component and welded to it, so the Animation Editor
only shows the 6 joints that actually move. Attachments for effects:
`Barrel.Muzzle` (muzzle flash, raycast origin) and `Slide.ShellEject` (shell casings).

### Animating it with the character

Roblox only plays animation poses on tool parts when the tool is joined to the character by a
**Motor6D**. The default `RightGrip` is a Weld, so poses don't apply. The build script adds a small
`HandRig` Script that swaps `RightGrip` for a Motor6D named `Handle` on equip and removes it on
unequip. Set `ADD_HAND_RIG_SCRIPT = false` at the top if you already have your own system.

To keyframe the gun with the arms in the Animation Editor:

1. Put an R15 rig in Workspace and parent a copy of the Tool to it.
2. Make a Motor6D named `Handle` in the rig's `RightHand`, with `Part0 = RightHand` and `Part1 = Tool.Handle`.
3. The gun's joints now appear in the editor under `Handle`.

## Style notes

- **Proportions:** an oversized slide and trigger guard, a raked grip, and a big hazard-orange base
  plate. Exaggerated shapes read well at the small screen size PvP players see.
- **Palette:** charcoal frame, steel slide, olive panels, orange accents, and a lime **neon** front
  sight. The neon is a readability cue that fits the zombie theme.
- **What's missing compared with real PG3D art:** PG3D's look relies heavily on low-res pixel
  **textures**. This model uses flat-coloured parts with block details instead. To get closer, paint
  16×16 or 32×32 pixel textures, upload them, and apply them as `Texture`/`Decal` objects on the
  slide and grip faces, or rebuild as MeshParts with a `SurfaceAppearance`.

## About copying

The design, name, emblem and palette here are original. It doesn't trace any specific Pixel Gun 3D
weapon. Copying an art *style* (blocky, bright, chunky) isn't infringement on its own. Copying a
specific weapon's design, name, logo or textures could be. This isn't legal advice. If you sell
the game, keep your own names and art and don't reference PG3D in your store listing.
