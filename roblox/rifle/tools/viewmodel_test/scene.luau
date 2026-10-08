-- Viewmodel as exported in ScarView.gltf (positions/rotations/sizes copied from the file), plus the parts the
-- export cannot contain: an invisible root, Motor6Ds, AnimationController, and a stand-in template blaster.
local P = CFrame.new(-17.9999847, 0.836580515, -9.59998512)
local vm = Instance.new("Model"); vm.Name = "AutoBlaster"; vm.Parent = workspace
local function part(cls, name, cframe, size, parent)
	local p = Instance.new(cls); p.Name = name; p.CFrame = cframe; p.Size = size; p.Parent = parent
	return p
end
local root = part("Part", "HumanoidRootPart", P, Vector3.new(0.2, 0.2, 0.2), vm)
root.Transparency = 1; root.Anchored = true
vm.PrimaryPart = root
local armR = part("Part", "RightArm", P * CFrame.new(0.5, 0, 1.70000029), Vector3.new(0.6, 0.6, 4), vm)
local armL = part("Part", "LeftArm", P * CFrame.new(-0.5, 4.76837158e-07, 0), Vector3.new(0.6, 0.6, 4), vm)
local scarNode = P * QUAT_CF(-0.0460720062, 0.445092916, -1.26106834, 0, -1, 0, 0)
local scar = Instance.new("Model"); scar.Name = "Scar"; scar.Parent = vm
local slide = part("MeshPart", "Slide", scarNode * CFrame.new(0.159643173, 0.296481371, 0.433318138), Vector3.new(0.0912250131, 0.182450026, 0.22806254), scar)
local mag = part("MeshPart", "Magazine", scarNode * CFrame.new(-0.0456123352, -0.364900112, 0.273675919), Vector3.new(0.22806254, 0.592962623, 0.547350109), scar)
local body = part("MeshPart", "Body", scarNode * CFrame.new(-0.0456123352, 0, 0), Vector3.new(0.319287568, 1.32276273, 3.64900064), scar)
for _, p in ipairs({ slide, mag, body }) do p.Anchored = true end
local blasterNode = P * QUAT_CF(-0.000385284424, 0.240277052, -0.203482628, 0.707106769, 0, 0, 0.707106769)
local blaster = Instance.new("Model"); blaster.Name = "Blaster"; blaster.Parent = vm
local folder = Instance.new("Folder"); folder.Name = "Body_attachments"; folder.Parent = blaster
local muz = part("Part", "Muzzle_Att", blasterNode * QUAT_CF(0, -2.59648609, -0.409265041, -0.707106829, 0, 0, 0.707106709), Vector3.new(0.1, 0.1, 0.1), folder)
muz.Anchored = true
-- stand-in template blaster (the real one's meshes are not in the export)
local handle = part("MeshPart", "Handle", P * CFrame.new(0, 0.25, -1.2), Vector3.new(0.35, 0.7, 2.6), blaster)
handle.CastShadow = false
local bmag = part("MeshPart", "BlasterMag", P * CFrame.new(0, -0.25, -1.0), Vector3.new(0.25, 0.6, 0.4), blaster)
local wc = Instance.new("WeldConstraint"); wc.Part0 = handle; wc.Part1 = bmag; wc.Parent = bmag
local att = Instance.new("Attachment"); att.Name = "MuzzleAttachment"; att.CFrame = CFrame.new(0, 0.1, -1.3); att.Parent = handle
local fx = Instance.new("ParticleEmitter"); fx.Name = "Flash"; fx.Parent = att
local light = Instance.new("PointLight"); light.Name = "FlashLight"; light.Parent = att
local snd = Instance.new("Sound"); snd.Name = "FireSound"; snd.Parent = handle
local anims = Instance.new("Folder"); anims.Name = "Animations"; anims.Parent = blaster
for _, n in ipairs({ "Idle", "Shoot", "Reload", "Equip" }) do
	local a = Instance.new("Animation"); a.Name = n; a.AnimationId = "rbxassetid://000"; a.Parent = anims
end
local ac = Instance.new("AnimationController"); ac.Parent = vm
local an = Instance.new("Animator"); an.Parent = ac

local function motor(name, p0, p1, c1, parent)
	local m = Instance.new("Motor6D"); m.Name = name; m.Part0 = p0; m.Part1 = p1
	c1 = c1 or CFrame.new()
	m.C1 = c1
	m.C0 = p0.CFrame:Inverse() * p1.CFrame * c1
	m.Parent = parent or p0
	return m
end
local V = VARIANT or 1
if V == 2 then
	-- unusual joint frames, same rest pose: the script must not depend on C0/C1 conventions
	motor("Right Shoulder", root, armR, CFrame.new(0, 0, 1.5) * CFrame.Angles(0.3, 0.2, 0.1))
	motor("Left Shoulder", root, armL, CFrame.new(0.2, -0.1, 1.2) * CFrame.Angles(-0.2, 0.5, 0.0))
	motor("BlasterJoint", root, handle, CFrame.new(0, 0.1, 0.4) * CFrame.Angles(0, math.pi, 0))
elseif V == 4 then
	-- the blaster is the rig root AND the PrimaryPart (arms hang off it); no HumanoidRootPart joints
	root.Parent = nil
	handle.Anchored = true
	vm.PrimaryPart = handle
	handle.PivotOffset = handle.CFrame:Inverse() * P
	motor("Right Shoulder", handle, armR)
	motor("Left Shoulder", handle, armL)
elseif V == 5 then
	-- the blaster's Handle is the PrimaryPart but it is jointed to the root
	motor("Right Shoulder", root, armR)
	motor("Left Shoulder", root, armL)
	motor("BlasterJoint", root, handle)
	vm.PrimaryPart = handle
	handle.PivotOffset = handle.CFrame:Inverse() * P
elseif V == 3 then
	motor("Right Shoulder", root, armR)
	motor("Left Shoulder", root, armL)
	motor("BlasterJoint", armR, handle)          -- blaster carried by the right arm
else
	motor("Right Shoulder", root, armR)
	motor("Left Shoulder", root, armL)
	motor("BlasterJoint", root, handle)
end
SELECTION = { vm }
PIVOT_BEFORE = vm:GetPivot()
SCENE = { vm = vm, body = body, mag = mag, slide = slide, armR = armR, armL = armL, root = root, muz = muz,
	rest = { body = body.CFrame, mag = mag.CFrame, slide = slide.CFrame } }
