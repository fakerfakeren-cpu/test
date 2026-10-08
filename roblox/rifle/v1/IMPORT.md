# Rifle v1: Roblox import

Files: `Rifle.glb` (recommended) or `Rifle.fbx`, plus `Rifle_palette.png` (64x64, already embedded in both).

Parts: `Body`, `Magazine`, `Slide` (charging handle), `Trigger`, under a model named `Rifle`.
Units: 1 unit = 1 stud (1 voxel = 0.0531125 studs, same as the pistol). +Y up, muzzle along -Z.
Body size: 0.372 x 1.540 x 4.249 studs (X x Y x Z).

## Import (Roblox Studio)
1. Home (or Avatar) tab > **Import 3D** > pick `Rifle.glb`.
2. In the import preview: keep **Merge Meshes OFF** (otherwise you get one part),
   set the scale unit to **Stud** if it asks, and check the preview says the model is about 4.25 studs long.
   If the size is off (e.g. 100x), change the scale unit and re-import.
3. Import. You get a Model `Rifle` with 4 MeshParts. Each part's TextureID should already point at the
   uploaded palette. If a part shows plain grey: upload `Rifle_palette.png` (Asset Manager > Import), copy its
   asset id, and set `TextureID = rbxassetid://<id>` on all four MeshParts.
4. Recommended part settings: `RenderFidelity = Precise` (stops automatic LOD from mangling the voxels at
   distance), `CollisionFidelity = Box`, Material `SmoothPlastic`.

## Muzzle attachment
Put an Attachment named `Muzzle` in **Body** at `Position = (0, 0.3187, -2.1245)` (= 0, 6, -40 voxels from
Body's centre: the centre of the muzzle device's front face), orientation (0, 0, 0). Its LookVector is the
firing direction (-Z). Command bar:

```lua
local body = workspace.Rifle.Body
local a = Instance.new("Attachment")
a.Name = "Muzzle"
a.Position = Vector3.new(0, 0.3187, -2.1245)
a.Parent = body
```

## Mesh check (from the exporter, see Rifle_check.json)
| Part | Triangles | Open edges | Non-manifold edges | Degenerate tris | Signed volume (studs^3) |
|---|---|---|---|---|---|
| Body | 4264 | 0 | 0 | 0 | 0.99800 |
| Magazine | 388 | 0 | 0 | 0 | 0.09664 |
| Slide | 48 | 0 | 0 | 0 | 0.00270 |
| Trigger | 106 | 0 | 0 | 0 | 0.00270 |

Texture filtering: the glTF sampler is set to NEAREST (Closest). Roblox has no point-filter switch for
MeshPart textures, so the palette uses 8x8-texel colour blocks with every UV at a block centre: bilinear
filtering and the first 3 mip levels cannot bleed neighbouring colours.
