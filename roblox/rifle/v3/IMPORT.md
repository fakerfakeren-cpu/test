# Rifle v3: Roblox import

v1 shape and thicknesses, with:
- **Trigger merged into Body.** Parts are now `Body`, `Magazine`, `Slide` (charging handle), under a model `Rifle`.
- **Black outline on everything**: every component boundary, panel, slot, groove, vent and rail gap, wrapped
  around the top/front/back faces too.
- **Every detachable part carries its own outline**, so the Magazine, the Slide and the Body's magwell still look
  finished when the parts are separated (reload/charging animations).

Two options, pick one:
- `Rifle_v3.glb` / `.fbx`: original muzzle device (7 px tall).
- `Rifle_v3_slim_muzzle.glb` / `.fbx`: thinner muzzle device (5 px tall).

Palette `Rifle_v3_palette.png` (64x64) is embedded in all four files.
1 unit = 1 stud, +Y up, muzzle along -Z. Body size 0.372 x 1.540 x 4.249 studs.

## Import (Roblox Studio)
1. Home (or Avatar) tab > **Import 3D** > pick the `.glb`.
2. Keep **Merge Meshes OFF**, scale unit **Stud**; the model should be about 4.25 studs long.
3. Import. If a part shows plain grey, upload the palette PNG and set `TextureID = rbxassetid://<id>` on the three
   MeshParts.
4. Recommended: `RenderFidelity = Precise`, `CollisionFidelity = Box`, Material `SmoothPlastic`.

## Muzzle attachment (both options)
Attachment named `Muzzle` in **Body** at `Position = (0, 0.3187, -2.1245)`, orientation (0, 0, 0).

```lua
local body = workspace.Rifle.Body
local a = Instance.new("Attachment")
a.Name = "Muzzle"
a.Position = Vector3.new(0, 0.3187, -2.1245)
a.Parent = body
```

## Mesh check
Option A (`Rifle_v3`):

| Part | Triangles | Open edges | Non-manifold edges | Degenerate tris | Signed volume (studs^3) |
|---|---|---|---|---|---|
| Body | 4398 | 0 | 0 | 0 | 1.0007 |
| Magazine | 464 | 0 | 0 | 0 | 0.09664 |
| Slide | 110 | 0 | 0 | 0 | 0.00599 |

Option B (`Rifle_v3_slim_muzzle`):

| Part | Triangles | Open edges | Non-manifold edges | Degenerate tris | Signed volume (studs^3) |
|---|---|---|---|---|---|
| Body | 4328 | 0 | 0 | 0 | 0.98721 |
| Magazine | 464 | 0 | 0 | 0 | 0.09664 |
| Slide | 110 | 0 | 0 | 0 | 0.00599 |
