-- Your viewmodel exactly as exported (ScarView.gltf), with what the export cannot carry added:
-- an invisible root, arm Motor6Ds, AnimationController. No template blaster parts (the export had none).
local P = CFrame.new(-17.9999847, 0.836580515, -9.59998512)
local vm = Instance.new("Model"); vm.Name = "AutoBlaster"; vm.Parent = workspace
local function part(cls, name, cframe, size, parent)
	local p = Instance.new(cls); p.Name = name; p.CFrame = cframe; p.Size = size; p.Parent = parent
	return p
end
local root = part("Part", "HumanoidRootPart", P, Vector3.new(0.2, 0.2, 0.2), vm)
root.Transparency = 1; root.Anchored = true; root.CanCollide = false; root.CanTouch = false; root.CanQuery = false
root.CastShadow = false; root.Massless = false
rawget(root, "_props").XColor = { 163, 162, 165 }; rawget(root, "_props").XMaterial = 272
vm.PrimaryPart = root
local function arm(name, cframe)
	local a = part("Part", name, cframe, Vector3.new(0.6, 0.6, 4), vm)
	a.Anchored = false; a.CanCollide = false; a.CanTouch = false; a.CanQuery = false; a.CastShadow = false; a.Massless = true
	rawget(a, "_props").XColor = { 163, 162, 165 }; rawget(a, "_props").XMaterial = 272   -- SmoothPlastic
	return a
end
local armR = arm("RightArm", P * CFrame.new(0.5, 0, 1.70000029))
local armL = arm("LeftArm", P * CFrame.new(-0.5, 4.76837158e-07, 0))
local scarNode = P * QUAT_CF(-0.0460720062, 0.445092916, -1.26106834, 0, -1, 0, 0)
local scar = Instance.new("Model"); scar.Name = "Scar"; scar.Parent = vm
local TEX = "rbxassetid://96279669712196"
local function mesh(name, localPos, size, meshId, initial)
	local m = part("MeshPart", name, scarNode * CFrame.new(localPos.X, localPos.Y, localPos.Z), size, scar)
	m.Anchored = true
	local pr = rawget(m, "_props")
	pr.XMeshId = meshId; pr.XTextureID = TEX; pr.XInitialSize = initial
	pr.XColor = { 163, 162, 165 }; pr.XMaterial = 256   -- Plastic, as exported
	return m
end
local slide = mesh("Slide", Vector3.new(0.159643173, 0.296481371, 0.433318138), Vector3.new(0.0912250131, 0.182450026, 0.22806254),
	"rbxassetid://82150188184524", Vector3.new(0.1062, 0.2125, 0.2656))
local mag = mesh("Magazine", Vector3.new(-0.0456123352, -0.364900112, 0.273675919), Vector3.new(0.22806254, 0.592962623, 0.547350109),
	"rbxassetid://80480420910453", Vector3.new(0.2656, 0.6905, 0.6374))
local body = mesh("Body", Vector3.new(-0.0456123352, 0, 0), Vector3.new(0.319287568, 1.32276273, 3.64900064),
	"rbxassetid://131917924785503", Vector3.new(0.37185, 1.54026, 4.249))
local blasterNode = P * QUAT_CF(-0.000385284424, 0.240277052, -0.203482628, 0.707106769, 0, 0, 0.707106769)
local blaster = Instance.new("Model"); blaster.Name = "Blaster"; blaster.Parent = vm
local folder = Instance.new("Folder"); folder.Name = "Body_attachments"; folder.Parent = blaster
local muz = part("Part", "Muzzle_Att", blasterNode * QUAT_CF(0, -2.59648609, -0.409265041, -0.707106829, 0, 0, 0.707106709), Vector3.new(0.1, 0.1, 0.1), folder)
muz.Anchored = true
local mp = rawget(muz, "_props"); mp.XColor = { 0, 0, 0 }; mp.XMaterial = 256; mp.XShape = 0   -- Ball
local ac = Instance.new("AnimationController"); ac.Parent = vm
local an = Instance.new("Animator"); an.Parent = ac
local function motor(name, p0, p1)
	local m = Instance.new("Motor6D"); m.Name = name; m.Part0 = p0; m.Part1 = p1
	m.C0 = p0.CFrame:Inverse() * p1.CFrame; m.C1 = CFrame.new(); m.Parent = p0
	return m
end
motor("RightShoulder", root, armR)
motor("LeftShoulder", root, armL)
SELECTION = { vm }
PIVOT_BEFORE = vm:GetPivot()
SCENE = { vm = vm, body = body, mag = mag, slide = slide, armR = armR, armL = armL, root = root, muz = muz,
	rest = { body = body.CFrame, mag = mag.CFrame, slide = slide.CFrame } }
