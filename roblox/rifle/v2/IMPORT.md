# Rifle v2: Roblox import

Same design and side silhouette as v1; v2 varies the thickness of the parts (depth) instead of one 7-voxel slab.
Files: `Rifle_v2.glb` (recommended) or `Rifle_v2.fbx`, palette `Rifle_v2_palette.png` (embedded in both,
identical colours to v1). Model is named `Rifle`; parts `Body`, `Magazine`, `Slide` (charging handle), `Trigger`.
1 unit = 1 stud, +Y up, muzzle along -Z. Body size: 0.478 x 1.540 x 4.249 studs (the pin heads stick out 1 voxel).

Thicknesses (voxels): receiver 7 (pins 9), handguard 5, wood forend 7 (grooves 5), stock 5 with 7-wide hinge
collar and butt pad and a 3-deep cheek recess, lower 5 with a 7-wide magwell, magazine 5 (recessed panel 3,
base plate 7), grip 5, guard 3, rail 5, rear sight 5, front sight 3, barrel 3, muzzle device 7 with a 5-wide
collar, top/bottom and vent slots, trigger 1, charging handle knob 2 out from the left side plus a tab in its slot.

Import steps: same as v1 (Import 3D, Merge Meshes OFF, scale unit Stud, model about 4.25 studs long).

Muzzle attachment: same as v1, in **Body** at `Position = (0, 0.3187, -2.1245)`, orientation (0, 0, 0).

## Mesh check
| Part | Triangles | Open edges | Non-manifold edges | Degenerate tris | Signed volume (studs^3) |
|---|---|---|---|---|---|
| Body | 4738 | 0 | 0 | 0 | 0.92548 |
| Magazine | 440 | 0 | 0 | 0 | 0.09904 |
| Slide | 72 | 0 | 0 | 0 | 0.00315 |
| Trigger | 106 | 0 | 0 | 0 | 0.0027 |
