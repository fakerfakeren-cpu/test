"""Rotstopper pistol, voxel edition (Pixel Gun 3D / Minecraft-style).

The gun is drawn as pixel art in side view, one canvas per moving component. Each pixel is
extruded into voxels across the gun's width, edges are stair-step bevelled, every visible voxel
face gets one texel of shaded pixel-art colour, and faces are greedy-merged into large quads
UV-mapped onto one shared texture atlas.

Outputs (next to this folder):
  rotstopper.obj / .mtl   one object per component (Frame, Grip, Slide, Barrel, Magazine,
                          Trigger, Hammer, SlideStop); import with Studio's 3D Importer
  rotstopper_texture.png  1024x512 atlas (nearest-neighbour upscaled so it stays crisp in Roblox)
  rig_rotstopper.lua      select the imported model, paste into the command bar: makes a rigged Tool
  preview.png             renders

Units: Roblox studs. +X right, +Y up, -Z forward (barrel), origin = centre of the grip.
Run:   python3 tools/gen_rotstopper.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
VOX = 0.04  # studs per voxel; the gun is ~53 voxels long = ~2.1 studs, chunky like PG3D

# ---------------------------------------------------------------- palette
# 5-step ramps: 0 deepest shadow .. 4 highlight. Pixel shading picks a step per texel.
RAMPS = {
    "steel":  ["1C2330", "3A4658", "6A7B92", "A4B4C9", "E2EBF5"],
    "gun":    ["121419", "23272F", "363B46", "4E5563", "707A8B"],
    "black":  ["07080A", "111317", "1B1E24", "2A2E37", "3E444F"],
    "orange": ["5A2805", "A64C0B", "E8781A", "FFA244", "FFD48E"],
    "olive":  ["1E230F", "38411F", "55622E", "75853F", "9AAB5B"],
    "brass":  ["4A3208", "8A6214", "C9962A", "EAC45C", "FFEBA4"],
    "neon":   ["2C6A10", "4CBC20", "7CFF3A", "B6FF80", "E8FFD4"],
}
NOISE = {"olive": 0.32, "steel": 0.06, "gun": 0.10, "orange": 0.08}

# ---------------------------------------------------------------- pixel-art spec
# char -> (ramp, base level, width in voxels, inner hole width, bevel-exempt)
SPEC = {
    # slide
    "S": ("steel", 2, 10, 0, False),   # slide body
    "H": ("steel", 3, 10, 0, False),   # polished streak
    "D": ("steel", 1, 10, 0, False),   # lower shadow band
    "X": ("steel", 0, 10, 0, False),   # rear serrations
    "O": ("orange", 2, 10, 0, False),  # hazard stripe
    "r": ("black", 2, 8, 2, True),     # rear sight (notched)
    "n": ("neon", 3, 2, 0, True),      # front sight
    # barrel
    "b": ("steel", 1, 6, 0, False),
    "o": ("steel", 1, 6, 2, True),     # muzzle with a bore hole
    # frame
    "F": ("gun", 2, 8, 0, False),
    "g": ("gun", 1, 6, 0, True),       # rail lugs
    "k": ("black", 2, 10, 0, True),    # takedown pin heads
    "G": ("gun", 2, 4, 0, False),      # trigger guard
    # grip
    "f": ("gun", 2, 8, 0, False),      # grip frame
    "d": ("gun", 1, 8, 0, False),      # grip butt
    "q": ("gun", 1, 8, 0, False),      # front-strap grooves
    "p": ("olive", 2, 10, 0, False),   # grip panel (stands proud of the frame)
    "e": ("orange", 2, 10, 0, False),  # diamond emblem on the panel
    # magazine
    "m": ("gun", 1, 6, 0, False),
    "B": ("orange", 2, 10, 0, False),  # base plate
    "c": ("brass", 2, 4, 0, False),    # top round
    # small parts
    "T": ("black", 3, 2, 0, True),     # trigger
    "h": ("black", 2, 4, 0, False),    # hammer
    "s": ("black", 3, 1, 0, True),     # slide stop (x range set per component)
}
# Overlays paint texels on one side only (they don't change shape). side: +1 = right (+X).
OVERLAY_SPEC = {"P": ("black", 0)}  # ejection port

COMPONENTS = ["Frame", "Grip", "Slide", "Barrel", "Magazine", "Trigger", "Hammer", "SlideStop"]
BEVEL = {"Slide": 2, "Barrel": 1, "Frame": 1, "Grip": 1, "Magazine": 1, "Hammer": 1, "Trigger": 0, "SlideStop": 0}
X_RANGE = {"SlideStop": (-5, -4)}  # explicit x span instead of the centred char width

canvas = {c: {} for c in COMPONENTS}       # comp -> {(row, col): char}; row 0 = top, col grows forward
overlay = {c: {1: {}, -1: {}} for c in COMPONENTS}


def rect(comp, r0, r1, c0, c1, ch):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            canvas[comp][(r, c)] = ch


def rake(r):
    """Grip rake: one column back for every three rows down."""
    return max(0, (r - 23) // 3)


# Slide: tall, chunky, stepped nose
rect("Slide", 5, 16, 6, 46, "S")
rect("Slide", 7, 16, 47, 48, "S")
rect("Slide", 7, 15, 49, 50, "S")
rect("Slide", 7, 7, 16, 48, "H")
for c in (8, 10, 12, 14):
    rect("Slide", 7, 14, c, c, "X")
rect("Slide", 13, 14, 22, 46, "O")
rect("Slide", 16, 16, 6, 48, "D")
rect("Slide", 3, 4, 7, 10, "r")
rect("Slide", 3, 4, 44, 45, "n")
for r in range(7, 11):
    for c in range(18, 28):
        overlay["Slide"][1][(r, c)] = "P"

# Barrel: mostly hidden in the slide, bore pokes out the front
rect("Barrel", 9, 12, 33, 52, "b")
rect("Barrel", 10, 11, 51, 52, "o")

# Frame: dust cover with rail, beavertail, trigger guard
rect("Frame", 17, 22, 6, 47, "F")
rect("Frame", 17, 19, 1, 5, "F")
rect("Frame", 20, 22, 4, 8, "F")
for c in (36, 40, 44):
    rect("Frame", 23, 23, c, c + 1, "g")
canvas["Frame"][(19, 35)] = "k"
rect("Frame", 23, 29, 32, 34, "G")
rect("Frame", 28, 29, 21, 34, "G")

# Grip: raked, olive panel with emblem, grooved front strap
for r in range(23, 37):
    front, back = 22 - rake(r), 8 - rake(r)
    rect("Grip", r, r, back, front, "d" if r == 36 else "f")
    if 24 <= r <= 35:
        rect("Grip", r, r, back + 1, front - 1, "p")
        if r % 2 == 0:
            canvas["Grip"][(r, front)] = "q"
er, ec = 29, (8 - rake(29) + 22 - rake(29)) // 2
for r in range(er - 2, er + 3):
    for c in range(ec - 2, ec + 3):
        if abs(r - er) + abs(c - ec) <= 2:
            canvas["Grip"][(r, c)] = "e"

# Magazine: body hidden in the grip, orange base plate below it, brass round on top
for r in range(23, 37):
    rect("Magazine", r, r, 8 - rake(r) + 3, 22 - rake(r) - 3, "m")
rect("Magazine", 37, 38, 8 - rake(36), 22 - rake(36) + 1, "B")
rect("Magazine", 21, 22, 12, 17, "c")

# Trigger (curved blade), hammer (with spur), slide stop (left side only)
rect("Trigger", 22, 23, 27, 28, "T")
rect("Trigger", 24, 25, 26, 27, "T")
rect("Trigger", 26, 27, 25, 26, "T")
rect("Hammer", 12, 18, 3, 5, "h")
rect("Hammer", 10, 11, 1, 4, "h")
rect("SlideStop", 17, 18, 24, 31, "s")

# Grid -> handle space. Voxel (x, row, col) occupies [x, x+1] * VOX on X, etc.
GRIP_CENTER = np.array([0.0, -29.5, -14.0])  # (x, -row, -col) of the hand position, in voxels


def to_studs(i, j, k):
    return (np.array([i, j, k], float) - GRIP_CENTER) * VOX


# Animated components: pivot position (voxel coords: x, row, col) and an X-axis tilt (degrees)
PIVOTS = {
    "Slide":     ((0, 11, 27), 0),           # translate +Z ~8 voxels to rack
    "Barrel":    ((0, 10.5, 33), 0),         # breech: tilt the muzzle up on lock-back
    "Magazine":  ((0, 30, 13), -math.degrees(math.atan(1 / 3))),  # axes follow the grip rake
    "Trigger":   ((0, 22, 27.5), 0),         # top of the blade
    "Hammer":    ((0, 18, 4), 0),            # hinge
    "SlideStop": ((-4.5, 17.5, 24), 0),      # rear of the lever
}
STATIC = {"Frame", "Grip"}
ATTACHMENTS = [("Barrel", "Muzzle", (0, 10.5, 53)), ("Slide", "ShellEject", (5.5, 8.5, 22.5))]
HANDLE_SIZE = (0.32, 0.56, 0.44)


def pivot_point(rc):
    x, row, col = rc
    return to_studs(x, -row, -col)


# ---------------------------------------------------------------- voxelise
def voxelise(comp):
    vox = {}
    for (r, c), ch in canvas[comp].items():
        _, _, w, hole, _ = SPEC[ch]
        x0, x1 = X_RANGE.get(comp, (-w // 2, w // 2))
        for x in range(x0, x1):
            if hole and -hole // 2 <= x < hole // 2:
                continue
            vox[(x, -r, -c)] = ch
    # stair-step bevel: remove voxels exposed on X and also on Y or Z
    for _ in range(BEVEL[comp]):
        kill = []
        for (i, j, k), ch in vox.items():
            if SPEC[ch][4]:
                continue
            ex = (i - 1, j, k) not in vox or (i + 1, j, k) not in vox
            eo = any(n not in vox for n in ((i, j - 1, k), (i, j + 1, k), (i, j, k - 1), (i, j, k + 1)))
            if ex and eo:
                kill.append((i, j, k))
        for p in kill:
            del vox[p]
    return vox


VOXELS = {c: voxelise(c) for c in COMPONENTS}

# ---------------------------------------------------------------- texel shading
DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def texel(comp, p, d):
    vox = VOXELS[comp]
    ch = vox[p]
    ramp, lvl, *_ = SPEC[ch]
    i, j, k = p
    empty = lambda q: q not in vox
    if d[0] != 0:  # side faces carry the pixel art; edge rows get rim light / shadow
        ov = overlay[comp].get(d[0], {}).get((-j, -k))
        if ov:
            ramp, lvl = OVERLAY_SPEC[ov]
        else:
            if empty((i, j + 1, k)):
                lvl += 1
            if empty((i, j - 1, k)):
                lvl -= 1
            if empty((i, j, k + 1)) or empty((i, j, k - 1)):
                lvl -= 1
    elif d[1] == 1:  # tops are lit, with a bright rim
        lvl += 1
        if empty((i + 1, j, k)) or empty((i - 1, j, k)):
            lvl += 1
    elif d[1] == -1:  # undersides in shadow
        lvl -= 1
        if empty((i + 1, j, k)) or empty((i - 1, j, k)):
            lvl -= 1
    else:  # front/back ends
        if any(empty(q) for q in ((i + 1, j, k), (i - 1, j, k), (i, j + 1, k), (i, j - 1, k))):
            lvl -= 1
    rng = random.Random(f"{comp}{p}{d}")
    if rng.random() < NOISE.get(ramp, 0):
        lvl += rng.choice((-1, 1))
    return hexrgb(RAMPS[ramp][max(0, min(4, lvl))])


# ---------------------------------------------------------------- greedy meshing
def greedy(comp):
    """Merge coplanar visible faces into rectangles. Each quad keeps its own texel grid."""
    vox = VOXELS[comp]
    quads = []
    for d in DIRS:
        ax = [n for n in range(3) if d[n] != 0][0]
        a_ax, b_ax = [n for n in range(3) if n != ax]
        slices = {}
        for p in vox:
            q = tuple(p[n] + d[n] for n in range(3))
            if q in vox:
                continue
            slices.setdefault(p[ax], {})[(p[a_ax], p[b_ax])] = p
        for s in sorted(slices):
            cells = slices[s]
            used = set()
            for (a, b) in sorted(cells, key=lambda t: (t[1], t[0])):
                if (a, b) in used:
                    continue
                a1 = a
                while (a1 + 1, b) in cells and (a1 + 1, b) not in used:
                    a1 += 1
                b1 = b
                while all((x, b1 + 1) in cells and (x, b1 + 1) not in used for x in range(a, a1 + 1)):
                    b1 += 1
                grid = []
                for y in range(b, b1 + 1):
                    row = []
                    for x in range(a, a1 + 1):
                        used.add((x, y))
                        row.append(texel(comp, cells[(x, y)], d))
                    grid.append(row)
                plane = s + (1 if d[ax] > 0 else 0)
                quads.append((d, ax, a_ax, b_ax, plane, (a, a1 + 1), (b, b1 + 1), grid))
    return quads


QUADS = {c: greedy(c) for c in COMPONENTS}


# ---------------------------------------------------------------- atlas
def pack():
    items = [(c, n, len(q[7][0]) + 2, len(q[7]) + 2) for c in COMPONENTS for n, q in enumerate(QUADS[c])]
    items.sort(key=lambda t: (-t[3], -t[2]))
    for size in (64, 128, 256, 512):
        x = y = shelf = 0
        place = {}
        ok = True
        for c, n, w, h in items:
            if x + w > size:
                x, y, shelf = 0, y + shelf, 0
            if y + h > size:
                ok = False
                break
            place[(c, n)] = (x, y)
            x += w
            shelf = max(shelf, h)
        if ok:
            used = y + shelf
            height = 1 << max(0, (used - 1).bit_length())  # non-square power of two is fine in Roblox
            return size, height, place
    raise RuntimeError("atlas too large")


ATLAS_N, ATLAS_H, PLACE = pack()
SCALE = 1024 // ATLAS_N
atlas = np.zeros((ATLAS_H, ATLAS_N, 3), np.uint8)
for _c in COMPONENTS:
    for _n, _q in enumerate(QUADS[_c]):
        _x0, _y0 = PLACE[(_c, _n)]
        _g = np.pad(np.array(_q[7], np.uint8), ((1, 1), (1, 1), (0, 0)), mode="edge")  # bleed guard
        atlas[_y0:_y0 + _g.shape[0], _x0:_x0 + _g.shape[1]] = _g


def quad_geometry(c, n):
    """Corners (studs, CCW seen from outside), atlas UVs (texel units, top-left origin), normal."""
    d, ax, a_ax, b_ax, plane, (a0, a1), (b0, b1), _ = QUADS[c][n]
    x0, y0 = PLACE[(c, n)]
    corners, uvs = [], []
    for (a, b) in ((a0, b0), (a1, b0), (a1, b1), (a0, b1)):
        p = [0, 0, 0]
        p[ax], p[a_ax], p[b_ax] = plane, a, b
        corners.append(to_studs(*p))
        uvs.append((x0 + 1 + (a - a0), y0 + 1 + (b - b0)))
    nrm = np.cross(corners[1] - corners[0], corners[3] - corners[0])
    if np.dot(nrm, d) < 0:
        corners.reverse()
        uvs.reverse()
    return corners, uvs, np.array(d, float)


def bbox(c):
    pts = np.array([p for n in range(len(QUADS[c])) for p in quad_geometry(c, n)[0]])
    lo, hi = pts.min(0), pts.max(0)
    return (lo + hi) / 2, hi - lo


# ---------------------------------------------------------------- OBJ
def gen_obj():
    out = ["# Rotstopper voxel pistol. One object per component. Units: studs. -Z forward, +Y up.",
           "mtllib rotstopper.mtl"]
    vi = 0
    for c in COMPONENTS:
        out.append(f"o {c}")
        out.append("usemtl rotstopper")
        for n in range(len(QUADS[c])):
            corners, uvs, _ = quad_geometry(c, n)
            for p in corners:
                out.append(f"v {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}")
            for u, v in uvs:
                out.append(f"vt {u / ATLAS_N:.6f} {1 - v / ATLAS_H:.6f}")
            out.append("f " + " ".join(f"{vi + m + 1}/{vi + m + 1}" for m in range(4)))
            vi += 4
    mtl = "newmtl rotstopper\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nd 1\nillum 1\nmap_Kd rotstopper_texture.png\n"
    return "\n".join(out) + "\n", mtl


# ---------------------------------------------------------------- Luau rig script
def fnum(x):
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def lv(v):
    return "Vector3.new(" + ", ".join(fnum(x) for x in v) + ")"


def lcf(pos, tilt_deg=0.0):
    a = math.radians(tilt_deg)
    c, s = math.cos(a), math.sin(a)
    m = [1, 0, 0, 0, c, -s, 0, s, c]
    return "CFrame.new(" + ", ".join(fnum(v) for v in list(pos) + m) + ")"


def gen_rig_lua():
    L = []
    w = L.append
    w("--[[ Rotstopper rig. Run AFTER importing rotstopper.obj with the 3D Importer.")
    w("     1. Select the imported model in the Explorer.")
    w("     2. Paste this whole file into View > Command Bar and press Enter.")
    w("     It builds Tool \"Rotstopper\" in PARENT: an invisible Handle, Motor6Ds for the moving")
    w("     pieces (Slide, Barrel, Magazine, Trigger, Hammer, SlideStop), welds for Frame and Grip.")
    w("     Generated by tools/gen_rotstopper.py.")
    w("]]")
    w("")
    w('local TEXTURE_ID = "" -- e.g. "rbxassetid://123456"; leave empty if the importer kept the texture')
    w('local PARENT = game:GetService("StarterPack")')
    w("local ADD_HAND_RIG_SCRIPT = true -- swaps RightGrip for a Motor6D on equip so animations reach the gun")
    w("")
    w("-- mesh bounding-box centres and sizes, in the file's coordinates (studs)")
    w("local MESHES = {")
    for c in COMPONENTS:
        ctr, size = bbox(c)
        w(f"\t{c} = {{ center = {lv(ctr)}, size = {lv(size)} }},")
    w("}")
    w(f"local HANDLE_SIZE = {lv(HANDLE_SIZE)} -- the Handle sits at the file origin (grip centre)")
    w("local PIVOTS = {")
    for c, (rc, tilt) in PIVOTS.items():
        w(f"\t{c} = {lcf(pivot_point(rc), tilt)},")
    w("}")
    w("local ATTACHMENTS = {")
    for c, name, rc in ATTACHMENTS:
        w(f'\t{{ "{c}", "{name}", {lv(pivot_point(rc))} }},')
    w("}")
    w('''
local model = game:GetService("Selection"):Get()[1]
assert(model, "Select the imported Rotstopper model in the Explorer first")

-- find each component by name (case-insensitive, tolerant of importer prefixes/suffixes)
local found = {}
for _, d in ipairs(model:GetDescendants()) do
	if d:IsA("MeshPart") then
		local lname = d.Name:lower()
		for comp in pairs(MESHES) do
			local lc = comp:lower()
			-- "Slide" must not match "SlideStop"
			local hit = lname:find(lc, 1, true) and not (lc == "slide" and lname:find("slidestop", 1, true))
			if hit and (not found[comp] or #d.Name < #found[comp].Name) then
				found[comp] = d
			end
		end
	end
end
local missing = {}
for comp in pairs(MESHES) do
	if not found[comp] then table.insert(missing, comp) end
end
assert(#missing == 0, "Could not find MeshParts named: " .. table.concat(missing, ", ") .. ". Rename them and run again.")

-- file -> world transform, measured from the imported pieces (handles importer scale and placement)
local frame, slide = found.Frame, found.Slide
local scale = (slide.Position - frame.Position).Magnitude / (MESHES.Slide.center - MESHES.Frame.center).Magnitude
local fileToWorld = frame.CFrame * CFrame.new(-MESHES.Frame.center * scale)
local function place(cf) -- file-space CFrame -> world, applying scale to the position
	return fileToWorld * (CFrame.new(cf.Position * scale) * cf.Rotation)
end

-- sanity check: every mesh should be where the file says it is
local worst = 0
for comp, info in pairs(MESHES) do
	local expected = fileToWorld * (info.center * scale)
	worst = math.max(worst, (found[comp].Position - expected).Magnitude / scale)
end
if worst > 0.02 then
	warn(("Rotstopper rig: imported pieces are up to %.3f studs off their expected layout. "
		.. "The importer may have rotated or re-centred them; check the result."):format(worst))
end

local old = PARENT:FindFirstChild("Rotstopper")
if old then old:Destroy() end
local tool = Instance.new("Tool")
tool.Name = "Rotstopper"
tool.RequiresHandle = true
tool.CanBeDropped = false
tool.Grip = CFrame.new()

local handle = Instance.new("Part")
handle.Name = "Handle"
handle.Size = HANDLE_SIZE * scale
handle.CFrame = place(CFrame.new())
handle.Transparency = 1
handle.CanCollide = false
handle.CanQuery = false
handle.CanTouch = false
handle.Parent = tool

for comp, part in pairs(found) do
	part.Name = comp
	part.Anchored = false
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.Massless = true
	if TEXTURE_ID ~= "" then part.TextureID = TEXTURE_ID end
	local pivot = PIVOTS[comp]
	if pivot then
		local p = place(pivot)
		local m = Instance.new("Motor6D")
		m.Name = comp
		m.Part0 = handle
		m.Part1 = part
		m.C0 = handle.CFrame:Inverse() * p
		m.C1 = part.CFrame:Inverse() * p
		m.Parent = handle
	else
		local wld = Instance.new("Weld")
		wld.Name = comp
		wld.Part0 = handle
		wld.Part1 = part
		wld.C0 = handle.CFrame:Inverse() * part.CFrame
		wld.Parent = handle
	end
	part.Parent = tool
end

for _, a in ipairs(ATTACHMENTS) do
	local part = found[a[1]]
	local att = Instance.new("Attachment")
	att.Name = a[2]
	att.CFrame = part.CFrame:Inverse() * place(CFrame.new(a[3]))
	att.Parent = part
end

if ADD_HAND_RIG_SCRIPT then
	local s = Instance.new("Script")
	s.Name = "HandRig"
	s.Source = [==[
local tool = script.Parent
local motor

tool.Equipped:Connect(function()
	local character = tool.Parent
	local hand = character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm")
	if not hand then return end
	local grip = hand:FindFirstChild("RightGrip") or hand:WaitForChild("RightGrip", 2)
	if not grip then return end
	motor = Instance.new("Motor6D")
	motor.Name = "Handle"
	motor.Part0 = hand
	motor.Part1 = tool.Handle
	motor.C0 = grip.C0
	motor.C1 = grip.C1
	grip:Destroy()
	motor.Parent = hand
end)

tool.Unequipped:Connect(function()
	if motor then
		motor:Destroy()
		motor = nil
	end
end)
]==]
	s.Parent = tool
end

tool.Parent = PARENT
if #model:GetChildren() == 0 then model:Destroy() end
pcall(function() game:GetService("Selection"):Set({ tool }) end)
print(("Rotstopper rigged in %s (scale %.3f, layout error %.4f studs)"):format(PARENT:GetFullName(), scale, worst))
''')
    return "\n".join(L)


# ---------------------------------------------------------------- preview renderer
def rx(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def pose_about(comp, local_R=np.eye(3), local_t=(0, 0, 0)):
    """(R, t) moving a component by local_R / local_t expressed in its pivot frame."""
    rc, tilt = PIVOTS[comp]
    P = pivot_point(rc)
    Rp = rx(tilt)
    Rw = Rp @ local_R @ Rp.T
    t = P + Rp @ np.array(local_t, float) - Rw @ P
    return Rw, t


def render(pose, yaw, pitch, W, H, scale, center, bg):
    ss = 2
    W2, H2 = W * ss, H * ss
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    V = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    light = np.array([-0.4, 0.8, 0.45])
    light /= np.linalg.norm(light)
    zbuf = np.full((H2, W2), -1e9)
    img = np.zeros((H2, W2, 3))
    img[:] = bg
    tex = atlas.astype(float) / 255
    for c in COMPONENTS:
        Rw, t = pose.get(c, (np.eye(3), np.zeros(3)))
        for n in range(len(QUADS[c])):
            corners, uvs, nrm = quad_geometry(c, n)
            pts = np.array([Rw @ p + t for p in corners])
            nw = Rw @ nrm
            if (V @ nw)[2] <= 1e-6:
                continue
            k = 0.78 + 0.22 * max(0.0, float(nw @ light))
            vv = (V @ (pts - center).T).T
            px = vv[:, 0] * scale * ss + W2 / 2
            py = -vv[:, 1] * scale * ss + H2 / 2
            pz = vv[:, 2]
            uv = np.array(uvs, float)
            for tri in ((0, 1, 2), (0, 2, 3)):
                x, y, z, u = px[list(tri)], py[list(tri)], pz[list(tri)], uv[list(tri)]
                x0, x1 = int(max(0, math.floor(x.min()))), int(min(W2 - 1, math.ceil(x.max())))
                y0, y1 = int(max(0, math.floor(y.min()))), int(min(H2 - 1, math.ceil(y.max())))
                if x0 > x1 or y0 > y1:
                    continue
                den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
                if abs(den) < 1e-12:
                    continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
                l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
                l2 = 1 - l0 - l1
                inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
                zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
                sub = zbuf[y0:y1 + 1, x0:x1 + 1]
                upd = inside & (zz > sub)
                if not upd.any():
                    continue
                uu = l0 * u[0, 0] + l1 * u[1, 0] + l2 * u[2, 0]
                vv2 = l0 * u[0, 1] + l1 * u[1, 1] + l2 * u[2, 1]
                ti = np.clip(np.floor(uu).astype(int), 0, ATLAS_N - 1)
                tj = np.clip(np.floor(vv2).astype(int), 0, ATLAS_H - 1)
                sub[upd] = zz[upd]
                img[y0:y1 + 1, x0:x1 + 1][upd] = tex[tj[upd], ti[upd]] * k
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return out.resize((W, H), Image.LANCZOS)


def gen_preview():
    W, H = 900, 560
    bg = np.array(hexrgb("23262D")) / 255
    center = np.array([0, 0.40, -0.30])
    T = lambda *v: (np.eye(3), np.array(v, float) * VOX)
    exploded = {"Slide": T(0, 10, 0), "Barrel": T(0, 5, -10), "Magazine": T(0, -16, 3),
                "Trigger": T(0, -7, -6), "Hammer": T(0, 5, 8), "SlideStop": T(-14, 5, 0)}
    test = {"Slide": pose_about("Slide", local_t=(0, 0, 8 * VOX)),
            "Barrel": pose_about("Barrel", rx(4)),
            "Magazine": pose_about("Magazine", local_t=(0, -14 * VOX, 0)),
            "Hammer": pose_about("Hammer", rx(40)),
            "Trigger": pose_about("Trigger", rx(-12)),
            "SlideStop": pose_about("SlideStop", local_t=(0, 0.5 * VOX, 0))}
    shots = [
        ("Left 3/4", render({}, 32, 16, W, H, 255, center, bg)),
        ("Right side (ejection port side)", render({}, -90, 0, W, H, 290, center + [0, -0.06, 0], bg)),
        ("Exploded: each separate mesh", render(exploded, 40, 14, W, H, 180, center + [0, -0.22, 0], bg)),
        ("Test pose: slide back, hammer cocked, mag out", render(test, -48, 16, W, H, 190, center + [0, -0.40, 0.1], bg)),
    ]
    sheet = Image.new("RGB", (W * 2, H * 2), hexrgb("23262D"))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate(shots):
        x, y = (i % 2) * W, (i // 2) * H
        sheet.paste(im, (x, y))
        d.text((x + 18, y + 14), label, fill=(235, 238, 242), font=font)
    return sheet


def ascii_dump():
    rows = [["."] * 56 for _ in range(40)]
    for c in ["Barrel", "Magazine", "Grip", "Frame", "Trigger", "Hammer", "SlideStop", "Slide"]:
        for (r, col), ch in canvas[c].items():
            rows[r][col] = ch
    return "\n".join("".join(r) for r in rows)


if __name__ == "__main__":
    obj, mtl = gen_obj()
    with open(os.path.join(OUT, "rotstopper.obj"), "w") as fh:
        fh.write(obj)
    with open(os.path.join(OUT, "rotstopper.mtl"), "w") as fh:
        fh.write(mtl)
    Image.fromarray(atlas).resize((ATLAS_N * SCALE, ATLAS_H * SCALE), Image.NEAREST).save(
        os.path.join(OUT, "rotstopper_texture.png"))
    with open(os.path.join(OUT, "rig_rotstopper.lua"), "w") as fh:
        fh.write(gen_rig_lua())
    gen_preview().save(os.path.join(OUT, "preview.png"))
    tris = {c: 2 * len(QUADS[c]) for c in COMPONENTS}
    print(f"atlas {ATLAS_N}x{ATLAS_H} texels, x{SCALE}; voxels {sum(len(v) for v in VOXELS.values())}; triangles {tris}")
    if os.environ.get("ASCII"):
        print(ascii_dump())
