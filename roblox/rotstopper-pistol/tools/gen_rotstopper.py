"""Rotstopper pistol: single source of truth for the geometry.

Generates, next to this folder:
  build_rotstopper.lua   paste into the Roblox Studio command bar; builds a rigged Tool
  rotstopper.obj/.mtl    one object per animatable component, for Blender
  preview.png            renders: 3/4 view, side view, exploded view, reload pose

Units are Roblox studs. Handle space: +X right, +Y up, -Z forward (barrel points along the
Handle's LookVector, which is what the default Tool.Grip expects). The origin is the centre of
the grip, where the hand holds it.

Run:  python3 tools/gen_rotstopper.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# ---------------------------------------------------------------- palette
# Chunky, saturated, flat colours. Charcoal frame, steel slide, olive grips, hazard-orange accents,
# lime neon front sight (zombie-game readability).
C = {
    "frame":  "3B4048",
    "slide":  "A9B4C2",
    "sdark":  "5C6673",
    "barrel": "8A939F",
    "black":  "16181C",
    "panel":  "6B7A3A",
    "pdark":  "4A5528",
    "accent": "FF8C1A",
    "brass":  "D9A934",
    "neon":   "7CFF3A",
}


# ---------------------------------------------------------------- math
def rx(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


class CF:
    """Rigid transform: world = R @ local + p (same convention as a Roblox CFrame)."""

    def __init__(self, p=(0, 0, 0), R=None):
        self.p = np.array(p, float)
        self.R = np.eye(3) if R is None else np.array(R, float)

    def __mul__(self, o):
        return CF(self.R @ o.p + self.p, self.R @ o.R)

    def point(self, v):
        return self.R @ np.array(v, float) + self.p

    def components(self):
        r = self.R
        return [self.p[0], self.p[1], self.p[2],
                r[0, 0], r[0, 1], r[0, 2], r[1, 0], r[1, 1], r[1, 2], r[2, 0], r[2, 1], r[2, 2]]


def T(x, y, z):
    return CF((x, y, z))


def R(m):
    return CF((0, 0, 0), m)


# ---------------------------------------------------------------- model
# Grip and magazine share a frame raked 14 degrees (bottom swept back).
GRIP = T(0, -0.03, 0.06) * R(rx(-14))

# Components. "Handle" is the invisible Tool handle. animated=True gets a Motor6D from the Handle,
# pivoted at `pivot`; the others are welded. Detail parts are welded to their component's main part.
COMPONENTS = [
    # name        animated  pivot (handle space)                        why the pivot is there
    ("Frame",     False,    CF()),
    ("Grip",      False,    CF()),
    ("Slide",     True,     T(0, 0.65, -0.36)),                       # translate +Z to rack
    ("Barrel",    True,     T(0, 0.66, -0.80)),                       # breech end, for tilt-up
    ("Magazine",  True,     GRIP * T(0, -0.08, 0.02)),                # axes follow the grip rake
    ("Trigger",   True,     T(0, 0.28, -0.42)),                       # top of the blade
    ("Hammer",    True,     T(0, 0.51, 0.42)),                        # hammer hinge
    ("SlideStop", True,     T(-0.155, 0.47, -0.12)),                  # rear of the lever
]

PARTS = []  # (component, name, size, CF, colour key, material)


def part(comp, name, size, cf, col, mat="SmoothPlastic"):
    PARTS.append((comp, name, tuple(size), cf, col, mat))


# Frame (lower receiver), static
part("Frame", "Frame",        (0.28, 0.22, 1.30), T(0, 0.39, -0.33), "frame")
part("Frame", "Beavertail",   (0.26, 0.12, 0.20), T(0, 0.44, 0.42), "frame")
for i, z in enumerate((-0.70, -0.82, -0.94)):
    part("Frame", f"RailLug{i + 1}", (0.20, 0.05, 0.08), T(0, 0.255, z), "sdark")
part("Frame", "GuardFront",   (0.10, 0.26, 0.07), T(0, 0.15, -0.60), "frame")
part("Frame", "GuardBottom",  (0.10, 0.07, 0.44), T(0, 0.055, -0.39), "frame")
part("Frame", "TakedownPin",  (0.02, 0.06, 0.06), T(0.145, 0.40, -0.55), "sdark")

# Grip, static
part("Grip", "Grip",          (0.30, 0.78, 0.40), GRIP, "frame")
for side, sx in (("L", -1), ("R", 1)):
    part("Grip", f"Panel{side}",   (0.025, 0.52, 0.30), GRIP * T(sx * 0.16, -0.04, 0), "panel")
    part("Grip", f"Emblem{side}",  (0.012, 0.10, 0.10), GRIP * T(sx * 0.178, 0.07, 0) * R(rx(45)), "accent")
    for i, y in enumerate((-0.10, -0.18, -0.26)):
        part("Grip", f"Groove{side}{i + 1}", (0.012, 0.03, 0.26), GRIP * T(sx * 0.178, y, 0), "pdark")
for i, y in enumerate((-0.04, -0.14, -0.24)):
    part("Grip", f"FrontStrap{i + 1}", (0.26, 0.03, 0.02), GRIP * T(0, y, -0.205), "pdark")

# Slide
part("Slide", "Slide",        (0.32, 0.30, 1.44), T(0, 0.65, -0.36), "slide")
part("Slide", "Nose",         (0.28, 0.24, 0.10), T(0, 0.64, -1.13), "slide")
part("Slide", "Rib",          (0.14, 0.04, 1.20), T(0, 0.82, -0.42), "sdark")
for i, z in enumerate((0.28, 0.20, 0.12, 0.04)):
    part("Slide", f"Serration{i + 1}", (0.34, 0.20, 0.035), T(0, 0.65, z), "sdark")
part("Slide", "Stripe",       (0.34, 0.05, 0.62), T(0, 0.58, -0.62), "accent")
part("Slide", "EjectionPort", (0.02, 0.12, 0.30), T(0.165, 0.71, -0.12), "black")
part("Slide", "RearSightL",   (0.08, 0.09, 0.07), T(-0.09, 0.845, 0.30), "black")
part("Slide", "RearSightR",   (0.08, 0.09, 0.07), T(0.09, 0.845, 0.30), "black")
part("Slide", "FrontSight",   (0.06, 0.09, 0.06), T(0, 0.885, -0.95), "neon", "Neon")

# Barrel
part("Barrel", "Barrel",      (0.17, 0.17, 0.46), T(0, 0.66, -1.01), "barrel")
part("Barrel", "Bore",        (0.09, 0.09, 0.02), T(0, 0.66, -1.245), "black")

# Magazine (sits inside the grip; base plate and top round show when it drops)
part("Magazine", "Magazine",  (0.22, 0.70, 0.30), GRIP * T(0, -0.08, 0.02), "sdark")
part("Magazine", "BasePlate", (0.30, 0.07, 0.42), GRIP * T(0, -0.46, 0.02), "accent")
part("Magazine", "TopRound",  (0.10, 0.06, 0.20), GRIP * T(0, 0.30, -0.02), "brass")

# Trigger
part("Trigger", "Trigger",    (0.07, 0.20, 0.07), T(0, 0.19, -0.42), "sdark")
part("Trigger", "TriggerShoe", (0.07, 0.06, 0.09), T(0, 0.12, -0.45), "sdark")

# Hammer
part("Hammer", "Hammer",      (0.10, 0.18, 0.08), T(0, 0.58, 0.42), "black")
part("Hammer", "HammerSpur",  (0.12, 0.05, 0.10), T(0, 0.665, 0.46), "black")

# Slide stop lever (left side)
part("SlideStop", "SlideStop", (0.03, 0.06, 0.22), T(-0.155, 0.47, -0.23), "black")

# Attachments for VFX/sounds: (component main part, name, handle-space CF)
ATTACHMENTS = [
    ("Barrel", "Muzzle", T(0, 0.66, -1.26)),
    ("Slide", "ShellEject", T(0.18, 0.71, -0.12)),
]

HANDLE_SIZE = (0.28, 0.50, 0.36)

for comp, *_ in COMPONENTS:
    assert any(p[0] == comp and p[1] == comp for p in PARTS), f"{comp} needs a main part named {comp}"
assert len({p[1] for p in PARTS}) == len(PARTS), "part names must be unique"


# ---------------------------------------------------------------- Luau builder
def fmt(v):
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def gen_lua():
    L = []
    w = L.append
    w("--[[ Rotstopper pistol: PG3D-inspired blocky sidearm, built from Parts and rigged for animation.")
    w("     Generated by tools/gen_rotstopper.py. Paste the whole file into the Studio command bar")
    w("     (View > Command Bar) and press Enter. A Tool named \"Rotstopper\" appears in PARENT.")
    w("")
    w("     Rig: every animatable component has a Motor6D in the Handle named after the component")
    w("     (Slide, Barrel, Magazine, Trigger, Hammer, SlideStop). Frame and Grip are welded to the")
    w("     Handle; small detail parts are welded to their component, so they follow it.")
    w("]]")
    w("")
    w('local PARENT = game:GetService("StarterPack")')
    w("local ADD_HAND_RIG_SCRIPT = true -- adds a Script that swaps RightGrip for a Motor6D on equip")
    w("")
    w("-- name, component, size, CFrame (relative to Handle), colour, material")
    w("local PARTS = {")
    for comp, name, size, cf, col, mat in PARTS:
        w(f'\t{{"{name}", "{comp}", Vector3.new({", ".join(fmt(v) for v in size)}), '
          f'CFrame.new({", ".join(fmt(v) for v in cf.components())}), "#{C[col]}", "{mat}"}},')
    w("}")
    w("")
    w("-- animated component -> pivot CFrame (relative to Handle)")
    w("local PIVOTS = {")
    for name, animated, pivot in COMPONENTS:
        if animated:
            w(f'\t{name} = CFrame.new({", ".join(fmt(v) for v in pivot.components())}),')
    w("}")
    w("")
    w("-- component main part, attachment name, CFrame (relative to Handle)")
    w("local ATTACHMENTS = {")
    for comp, name, cf in ATTACHMENTS:
        w(f'\t{{"{comp}", "{name}", CFrame.new({", ".join(fmt(v) for v in cf.components())})}},')
    w("}")
    w("")
    w('''local old = PARENT:FindFirstChild("Rotstopper")
if old then old:Destroy() end

local tool = Instance.new("Tool")
tool.Name = "Rotstopper"
tool.RequiresHandle = true
tool.CanBeDropped = false
tool.Grip = CFrame.new()

local function newPart(name, size, cf)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cf
	p.Anchored = false
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	return p
end

local handle = newPart("Handle", Vector3.new(''' + ", ".join(fmt(v) for v in HANDLE_SIZE) + '''), CFrame.new())
handle.Transparency = 1
handle.Massless = false
handle.Parent = tool

local mains = {}
for _, d in ipairs(PARTS) do
	local name, comp = d[1], d[2]
	local p = newPart(name, d[3], d[4])
	p.Color = Color3.fromHex(d[5])
	p.Material = Enum.Material[d[6]]
	if name == comp then
		mains[comp] = p
		p.Parent = tool
	end
end

for _, d in ipairs(PARTS) do
	local name, comp = d[1], d[2]
	local main = mains[comp]
	local p = (name == comp) and main or nil
	if not p then
		p = newPart(name, d[3], d[4])
		p.Color = Color3.fromHex(d[5])
		p.Material = Enum.Material[d[6]]
		p.Parent = main
		local weld = Instance.new("Weld")
		weld.Name = name
		weld.Part0 = main
		weld.Part1 = p
		weld.C0 = main.CFrame:Inverse() * p.CFrame
		weld.Parent = p
	end
end

for comp, main in pairs(mains) do
	local pivot = PIVOTS[comp]
	if pivot then
		local m = Instance.new("Motor6D")
		m.Name = comp
		m.Part0 = handle
		m.Part1 = main
		m.C0 = handle.CFrame:Inverse() * pivot
		m.C1 = main.CFrame:Inverse() * pivot
		m.Parent = handle
	else
		local weld = Instance.new("Weld")
		weld.Name = comp
		weld.Part0 = handle
		weld.Part1 = main
		weld.C0 = handle.CFrame:Inverse() * main.CFrame
		weld.Parent = handle
	end
end

for _, a in ipairs(ATTACHMENTS) do
	local main = mains[a[1]]
	local att = Instance.new("Attachment")
	att.Name = a[2]
	att.CFrame = main.CFrame:Inverse() * a[3]
	att.Parent = main
end

if ADD_HAND_RIG_SCRIPT then
	-- Animations only drive tool parts if the tool is joined to the character by a Motor6D.
	-- This swaps the default RightGrip weld for a Motor6D named "Handle" while equipped.
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
pcall(function() game:GetService("Selection"):Set({ tool }) end)
print(("Rotstopper built in %s: %d parts"):format(PARENT:GetFullName(), #PARTS + 1))
''')
    return "\n".join(L)


# ---------------------------------------------------------------- mesh helpers
CUBE_V = np.array([[x, y, z] for x in (-.5, .5) for y in (-.5, .5) for z in (-.5, .5)])
# quads, CCW seen from outside; index = x*4 + y*2 + z
CUBE_F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def box_verts(size, cf):
    return np.array([cf.point(v * np.array(size)) for v in CUBE_V])


def gen_obj():
    mtl = []
    for k, hexv in C.items():
        r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4))
        mtl += [f"newmtl {k}", f"Kd {r:.4f} {g:.4f} {b:.4f}", "Ka 0 0 0", "Ks 0.05 0.05 0.05", "d 1", "illum 1", ""]
    obj = ["# Rotstopper pistol, one object per component, studs, -Z forward, origin = grip centre",
           "mtllib rotstopper.mtl"]
    n = 0
    for comp, *_ in COMPONENTS:
        obj.append(f"o {comp}")
        for c2, name, size, cf, col, _ in PARTS:
            if c2 != comp:
                continue
            obj.append(f"g {comp}_{name}")
            obj.append(f"usemtl {col}")
            for v in box_verts(size, cf):
                obj.append(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}")
            for f in CUBE_F:
                obj.append("f " + " ".join(str(n + i + 1) for i in f))
            n += 8
    return "\n".join(obj) + "\n", "\n".join(mtl)


# ---------------------------------------------------------------- renderer
def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def render(pose, yaw, pitch, W, H, scale, center, bg):
    """Orthographic z-buffer render with flat shading and face outlines. Returns PIL image."""
    ss = 2
    W2, H2 = W * ss, H * ss
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rp = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    V = Rp @ Ry  # world -> view; view looks down -Z, +Y up
    light = np.array([-0.45, 0.75, 0.5])
    light /= np.linalg.norm(light)

    zbuf = np.full((H2, W2), -1e9)
    img = np.zeros((H2, W2, 3))
    img[:] = bg
    fid = np.full((H2, W2), -1, int)
    face_id = 0
    for comp, name, size, cf, col, mat in PARTS:
        cf2 = pose.get(comp, CF()) * cf
        verts = box_verts(size, cf2)
        vv = (V @ (verts - center).T).T
        base = hex_rgb(C[col])
        for f in CUBE_F:
            a, b, c, d = (verts[i] for i in f)
            nrm = np.cross(b - a, d - a)
            nrm /= np.linalg.norm(nrm)
            nv = V @ nrm
            face_id += 1
            if nv[2] <= 1e-6:
                continue
            if mat == "Neon":
                shade = np.minimum(base * 1.15, 1)
            else:
                k = 0.42 + 0.58 * max(0.0, float(nrm @ light))
                shade = base * k
            q = vv[list(f)]
            px = q[:, 0] * scale * ss + W2 / 2
            py = -q[:, 1] * scale * ss + H2 / 2
            pz = q[:, 2]
            for tri in ((0, 1, 2), (0, 2, 3)):
                x = px[list(tri)]
                y = py[list(tri)]
                z = pz[list(tri)]
                x0, x1 = int(max(0, math.floor(x.min()))), int(min(W2 - 1, math.ceil(x.max())))
                y0, y1 = int(max(0, math.floor(y.min()))), int(min(H2 - 1, math.ceil(y.max())))
                if x0 > x1 or y0 > y1:
                    continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
                if abs(den) < 1e-12:
                    continue
                l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
                l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
                l2 = 1 - l0 - l1
                inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
                zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
                sub = zbuf[y0:y1 + 1, x0:x1 + 1]
                upd = inside & (zz > sub)
                sub[upd] = zz[upd]
                img[y0:y1 + 1, x0:x1 + 1][upd] = shade
                fid[y0:y1 + 1, x0:x1 + 1][upd] = face_id
    # outlines where the visible face changes
    edge = np.zeros_like(fid, bool)
    for dy, dx in ((0, 1), (1, 0), (1, 1), (0, ss), (ss, 0)):
        a = fid[: H2 - dy, : W2 - dx]
        b = fid[dy:, dx:]
        diff = a != b
        edge[: H2 - dy, : W2 - dx] |= diff
        edge[dy:, dx:] |= diff
    img[edge & (fid >= 0)] *= 0.35
    edge_bg = edge & (fid < 0)
    img[edge_bg] = img[edge_bg] * 0.35
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return out.resize((W, H), Image.LANCZOS)


def pivot_of(name):
    return next(p for n, _, p in COMPONENTS if n == name)


def about(pivot, local):
    """Pose for a component: transform `local` applied in its pivot's frame."""
    inv = CF(-pivot.R.T @ pivot.p, pivot.R.T)
    return pivot * local * inv


def gen_preview():
    W, H = 900, 560
    bg = hex_rgb("23262D")
    center = np.array([0, 0.25, -0.35])
    rest = {}
    exploded = {
        "Slide": T(0, 0.55, 0), "Barrel": T(0, 0.30, -0.55), "Magazine": T(0, -0.75, 0.20),
        "Trigger": T(0, -0.35, -0.35), "Hammer": T(0, 0.25, 0.45), "SlideStop": T(-0.6, 0.35, 0),
    }
    reload_pose = {
        "Slide": T(0, 0, 0.32),
        "Barrel": about(pivot_of("Barrel"), R(rx(5))),
        "Magazine": about(pivot_of("Magazine"), T(0, -0.70, 0)),
        "Hammer": about(pivot_of("Hammer"), R(rx(40))),
        "Trigger": about(pivot_of("Trigger"), R(rx(-12))),
        "SlideStop": about(pivot_of("SlideStop"), T(0, 0.02, 0)),
    }
    shots = [
        ("Left 3/4", render(rest, 35, 18, W, H, 300, center, bg)),
        ("Right side (ejection port side)", render(rest, -90, 0, W, H, 330, center, bg)),
        ("Exploded: every separate piece", render(exploded, 40, 14, W, H, 190, center + [0, -0.12, 0], bg)),
        ("Test pose: slide back, hammer cocked, mag out", render(reload_pose, -50, 16, W, H, 215, center + [0, -0.35, 0.1], bg)),
    ]
    sheet = Image.new("RGB", (W * 2, H * 2), tuple((bg * 255).astype(int)))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for i, (label, im) in enumerate(shots):
        x, y = (i % 2) * W, (i // 2) * H
        sheet.paste(im, (x, y))
        d = ImageDraw.Draw(sheet)
        d.text((x + 18, y + 14), label, fill=(235, 238, 242), font=font)
    return sheet


if __name__ == "__main__":
    with open(os.path.join(OUT, "build_rotstopper.lua"), "w") as fh:
        fh.write(gen_lua())
    obj, mtl = gen_obj()
    with open(os.path.join(OUT, "rotstopper.obj"), "w") as fh:
        fh.write(obj)
    with open(os.path.join(OUT, "rotstopper.mtl"), "w") as fh:
        fh.write(mtl)
    gen_preview().save(os.path.join(OUT, "preview.png"))
    print(f"{len(PARTS)} parts, {sum(1 for c in COMPONENTS if c[1])} animated components")
