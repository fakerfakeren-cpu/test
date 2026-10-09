--[[
	Scar viewmodel setup + animations (Equip, Shoot, Reload, Idle)
	================================================================
	HOW TO RUN (once):
	  1. In the Explorer, select your viewmodel Model (the one that contains the AnimationController,
	     the arms, the template "Blaster" and your "Scar").
	  2. View > Command Bar, paste this whole script, press Enter.
	  3. Read the Output window: it lists everything it changed.

	WHAT IT DOES (nothing is lost):
	  - Saves a full copy of the viewmodel to ServerStorage as "<name>_Backup".
	  - Removes the template blaster's visible parts (moved to ServerStorage "<name>_BlasterParts").
	    The "Blaster" model itself, its folders, configuration, attributes, scripts, sounds and its
	    attachments (with their effects) are kept; attachments/effects are moved onto the Scar.
	  - Rigs the Scar exactly like the blaster was rigged: the blaster's Motor6D (same name, same parent,
	    same Part0) now drives Scar.Body, and Body drives Magazine and Slide with their own Motor6Ds.
	  - Arms: slimmer, shorter forearms that come up from below the screen, each with a hand block on its
	    own wrist Motor6D (RightWrist / LeftWrist). Welds or anchoring that would lock the arms are removed.
	  - Sounds: Sound objects in Scar.Body (Equip, Fire, MagOut, MagIn, Tap, RackBack, RackRelease), markers
	    with the same names inside the animations, and a client Script "ScarSounds" that plays each sound
	    when its marker is reached. Paste your sound IDs into CONFIG.Sounds below (or into the Sounds later).
	  - Builds 4 animations as KeyframeSequences in <viewmodel>.AnimSaves:
	      Scar_Idle (loops), Scar_Equip, Scar_Shoot, Scar_Reload
	    Open them in the Animation Editor (select the viewmodel, ... > Load) and Publish to Roblox,
	    then use the IDs in your blaster config.
	Undo: Ctrl+Z right after running, or restore "<name>_Backup" from ServerStorage.
]]

local CONFIG = {
	ScarName = "Scar",            -- the Scar model inside the viewmodel
	BlasterName = "Blaster",      -- the template blaster model inside the viewmodel
	BodyName = "Body",
	MagazineName = "Magazine",
	SlideName = "Slide",          -- the charging handle
	-- Rifle v3 file data (studs, unscaled, axes of the .glb, relative to the Body centre).
	-- If you resized the gun these are scaled automatically from Body.Size.
	OriginalBodySize = Vector3.new(0.37185, 1.54026, 4.24900),
	Points = {
		Muzzle = Vector3.new(0, 0.3187, -2.1245),
		Grip   = Vector3.new(0, -0.2655, 0.5417),   -- right hand (centre of the hand on the pistol grip)
		GripTop = Vector3.new(0, -0.1327, 0.4780),
		GripBottom = Vector3.new(0, -0.6639, 0.7435),
		Forend = Vector3.new(0, -0.0700, -0.9500),  -- left hand, cupping the wooden forend from below
	},
	-- arms and hands
	ResizeArms = true,                       -- slimmer, shorter forearms (the template's are 0.6 x 0.6 x 4)
	ArmThickness = 0.42,
	ArmLength = 2.6,
	AddHands = true,                         -- a hand block on a wrist Motor6D at the end of each arm
	HandSize = Vector3.new(0.5, 0.5, 0.54),
	HandColor = Color3.fromRGB(58, 64, 70),  -- dark gloves
	-- where each forearm comes from, measured from where its hand rests, in camera terms
	-- (x right, y up, z back): the arms rise from below the screen instead of reaching across it
	RightArmPivot = Vector3.new(0.35, -1.45, 1.45),
	LeftArmPivot = Vector3.new(-0.55, -2.30, 1.10),
	-- sound IDs (e.g. "rbxassetid://123"); empty ones can be filled in later on the Sound objects
	Sounds = {
		Equip = "", Fire = "", MagOut = "", MagIn = "", Tap = "", RackBack = "", RackRelease = "",
	},
	Fps = 60,
	IdleFps = 30,
}

local Selection = game:GetService("Selection")
local ServerStorage = game:GetService("ServerStorage")
local ChangeHistoryService = game:GetService("ChangeHistoryService")

local TAG = "[ScarSetup]"
local function say(...) print(TAG, ...) end
local function note(...) warn(TAG, ...) end
local function fail(msg) error(TAG .. " " .. msg, 0) end

---------------------------------------------------------------------------------------------------
-- 1. Find everything
---------------------------------------------------------------------------------------------------
local function hasController(inst)
	return inst:FindFirstChildWhichIsA("AnimationController", true) ~= nil
end
local vm = Selection:Get()[1]
while vm and not (vm:IsA("Model") and hasController(vm)) do
	vm = vm.Parent
end
if not vm then
	fail("Select the viewmodel Model (the one with the AnimationController) in the Explorer, then run again.")
end
local scar = vm:FindFirstChild(CONFIG.ScarName, true)
if not scar then fail("No '" .. CONFIG.ScarName .. "' inside " .. vm:GetFullName()) end
local body = scar:FindFirstChild(CONFIG.BodyName)
local mag = scar:FindFirstChild(CONFIG.MagazineName)
local slide = scar:FindFirstChild(CONFIG.SlideName)
if not (body and body:IsA("BasePart")) then fail("No BasePart '" .. CONFIG.BodyName .. "' in " .. scar:GetFullName()) end
if mag and not mag:IsA("BasePart") then mag = nil end
if slide and not slide:IsA("BasePart") then slide = nil end
local blaster = vm:FindFirstChild(CONFIG.BlasterName)

ChangeHistoryService:SetWaypoint("Before Scar viewmodel setup")

local function uniqueName(parent, base)
	local name, n = base, 1
	while parent:FindFirstChild(name) do
		n += 1
		name = base .. "_" .. n
	end
	return name
end

local oldPrimary = vm.PrimaryPart
local oldPivot = vm:GetPivot()

-- full backup first
do
	local wasArchivable = vm.Archivable
	vm.Archivable = true
	local copy = vm:Clone()
	vm.Archivable = wasArchivable
	if copy then
		copy.Name = uniqueName(ServerStorage, vm.Name .. "_Backup")
		copy.Parent = ServerStorage
		say("Backup saved:", copy:GetFullName())
	else
		note("Could not clone the viewmodel for a backup (Archivable is off on it). Continuing; Ctrl+Z still works.")
	end
end

local function isIn(inst, ancestor)
	return inst ~= nil and ancestor ~= nil and (inst == ancestor or inst:IsDescendantOf(ancestor))
end

---------------------------------------------------------------------------------------------------
-- 2. Remove the template blaster's visible parts, keep everything functional
---------------------------------------------------------------------------------------------------
local removed = {}          -- [BasePart] = true
local removedList = {}
local keptParts = {}        -- e.g. Body_attachments/Muzzle_Att: kept and welded to the Scar
local blasterPartRef        -- a removed part to copy render/physics flags from
if blaster then
	for _, d in ipairs(blaster:GetDescendants()) do
		if d:IsA("BasePart") then
			local inAttFolder = false
			local p = d.Parent
			while p and p ~= blaster do
				if string.find(string.lower(p.Name), "attachment") then inAttFolder = true end
				p = p.Parent
			end
			local lname = string.lower(d.Name)
			if inAttFolder or string.find(lname, "_att", 1, true) or string.find(lname, "attachment", 1, true) then
				table.insert(keptParts, d)
			else
				removed[d] = true
				table.insert(removedList, d)
				if not blasterPartRef or d.Size.Magnitude > blasterPartRef.Size.Magnitude then blasterPartRef = d end
			end
		end
	end
else
	note("No '" .. CONFIG.BlasterName .. "' model found; nothing to remove.")
end

-- Scar geometry (needed to place moved attachments at the Scar's muzzle)
local size0 = CONFIG.OriginalBodySize
local scale = Vector3.new(body.Size.X / size0.X, body.Size.Y / size0.Y, body.Size.Z / size0.Z)
local sigma = 1   -- +1: muzzle is the Body's local +Z end (Roblox's importer turns the model around)
do
	local probe = mag or slide
	if probe then
		local z = body.CFrame:PointToObjectSpace(probe.Position).Z
		sigma = (z >= 0) and 1 or -1
	else
		note("No Magazine/Slide to detect which end is the muzzle; assuming local +Z.")
	end
end
local function gunPoint(v)   -- file-space point (relative to Body centre) -> Body local space
	return Vector3.new(-sigma * v.X * scale.X, v.Y * scale.Y, -sigma * v.Z * scale.Z)
end
local muzzleLocal = gunPoint(CONFIG.Points.Muzzle)
local muzzleCF = CFrame.lookAt(muzzleLocal, muzzleLocal + Vector3.new(0, 0, sigma))   -- LookVector = firing direction

-- move functional children off the parts that are being removed
local movedFunctional = {}
local FUNCTIONAL = { "Attachment", "Sound", "ParticleEmitter", "Light", "Beam", "Trail", "Fire", "Smoke",
	"Sparkles", "LuaSourceContainer", "ValueBase", "Configuration", "Folder" }
for _, part in ipairs(removedList) do
	for _, child in ipairs(part:GetChildren()) do
		local keep = false
		for _, cls in ipairs(FUNCTIONAL) do
			if child:IsA(cls) then
				keep = true
				break
			end
		end
		if keep then
			if child:IsA("Attachment") then
				local world = child.WorldCFrame
				child.Parent = body
				if string.find(string.lower(child.Name), "muzzle") then
					child.CFrame = muzzleCF
				else
					child.WorldCFrame = world
				end
			else
				child.Parent = body
			end
			table.insert(movedFunctional, child:GetFullName())
		end
	end
end

---------------------------------------------------------------------------------------------------
-- 3. Joints: re-point the blaster's joints to Scar.Body (keeping name, parent, Part0), rig Mag/Slide
---------------------------------------------------------------------------------------------------
local function allJoints()
	local list = {}
	for _, d in ipairs(vm:GetDescendants()) do
		if d:IsA("JointInstance") or d:IsA("WeldConstraint") then table.insert(list, d) end
	end
	return list
end
local function volume(p) return p.Size.X * p.Size.Y * p.Size.Z end

local backupFolder
local function toBackup(inst)
	if not backupFolder then
		backupFolder = Instance.new("Model")
		backupFolder.Name = uniqueName(ServerStorage, vm.Name .. "_BlasterParts")
		backupFolder.Parent = ServerStorage
	end
	inst.Parent = backupFolder
end

local bodyJoint            -- the Motor6D that drives Scar.Body
-- a joint already driving the Body (script was run before)
for _, j in ipairs(allJoints()) do
	if j:IsA("Motor6D") and j.Part1 == body and not isIn(j.Part0, scar) then bodyJoint = j end
end
local mainCandidate, mainScore
for _, j in ipairs(allJoints()) do
	local r0 = j.Part0 and removed[j.Part0]
	local r1 = j.Part1 and removed[j.Part1]
	if (r0 and not r1) or (r1 and not r0) then
		if j:IsA("Motor6D") and r1 and not bodyJoint then
			local score = volume(j.Part1) + ((j.Part0 == vm.PrimaryPart) and 1e6 or 0)
			if not mainScore or score > mainScore then mainCandidate, mainScore = j, score end
		end
	end
end
if mainCandidate then bodyJoint = mainCandidate end

local rewired = {}
for _, j in ipairs(allJoints()) do
	local r0 = j.Part0 and removed[j.Part0]
	local r1 = j.Part1 and removed[j.Part1]
	if r0 and r1 then
		if not isIn(j, blaster) or not removed[j.Parent] then toBackup(j) end
	elseif r1 or r0 then
		if j == bodyJoint then
			-- keep C0 (the joint's pivot), solve C1 so the Scar stays exactly where it is now
			j.Part1 = body
			j.C1 = body.CFrame:Inverse() * j.Part0.CFrame * j.C0
			if removed[j.Parent] then j.Parent = j.Part0 end
			table.insert(rewired, j.Name .. " (" .. j.ClassName .. ") now drives " .. body:GetFullName())
		elseif r0 and not isIn(j.Part1, scar) then
			-- something of the rig hung off the blaster: hang it off the Scar Body instead
			if j:IsA("WeldConstraint") then
				j.Part0 = body
			else
				j.C0 = body.CFrame:Inverse() * j.Part1.CFrame * j.C1
				j.Part0 = body
			end
			if removed[j.Parent] then j.Parent = body end
			table.insert(rewired, j.Name .. " (" .. j.ClassName .. ") now hangs off " .. body:GetFullName())
		else
			toBackup(j)   -- other rig -> blaster-subpart joints: the Scar has its own Mag/Slide joints
		end
	end
end
for _, part in ipairs(removedList) do toBackup(part) end
if #removedList > 0 then say("Moved", #removedList, "blaster part(s) to", backupFolder and backupFolder:GetFullName()) end
for _, s in ipairs(movedFunctional) do say("Kept (moved onto the Scar):", s) end
for _, s in ipairs(rewired) do say("Joint:", s) end

-- roots / arms
local function motorsNow()
	local list = {}
	for _, d in ipairs(vm:GetDescendants()) do
		if d:IsA("Motor6D") and d.Part0 and d.Part1 then table.insert(list, d) end
	end
	return list
end
local function partNamed(side, what)
	local exact, loose
	for _, d in ipairs(vm:GetDescendants()) do
		if d:IsA("BasePart") and not isIn(d, scar) and not isIn(d, blaster) then
			local n = string.lower((string.gsub(d.Name, "[%s_]", "")))
			if n == side .. what then exact = exact or d
			elseif string.find(n, side, 1, true) and string.find(n, what, 1, true) then loose = loose or d end
		end
	end
	return exact or loose
end
local function findArm(side) return partNamed(side, "arm") or partNamed(side, "hand") end
local armR, armL = findArm("right"), findArm("left")
if not armR then note("No RightArm found: the right arm will not be animated.") end
if not armL then note("No LeftArm found: the left arm will not be animated.") end

local function rootOfRig()
	local isPart1 = {}
	for _, m in ipairs(motorsNow()) do isPart1[m.Part1] = true end
	local pp = vm.PrimaryPart
	if pp and pp:IsDescendantOf(vm) and not removed[pp] and not isPart1[pp] then return pp end
	for _, m in ipairs(motorsNow()) do
		if not isPart1[m.Part0] then return m.Part0 end
	end
	return nil
end
local root = rootOfRig()

-- If the blaster itself was the rig root, the Scar would now be the root and could not be animated:
-- give the rig an invisible anchored root at the old pivot instead.
local newRoot
if not bodyJoint and (root == nil or root == body or removed[root]) then
	newRoot = Instance.new("Part")
	newRoot.Name = "ScarRoot"
	newRoot.Size = Vector3.new(0.2, 0.2, 0.2)
	newRoot.Transparency = 1
	newRoot.Anchored = true
	newRoot.CanCollide = false
	newRoot.CanTouch = false
	newRoot.CanQuery = false
	newRoot.CastShadow = false
	newRoot.CFrame = oldPivot
	newRoot.Parent = vm
	root = newRoot
	say("Created", newRoot:GetFullName(), "as the rig root (the blaster used to be the root)")
end
-- keep the model's pivot exactly where the template expects it
if oldPrimary == nil or removed[oldPrimary] or newRoot then
	if oldPrimary ~= nil or newRoot then
		vm.PrimaryPart = root
		root.PivotOffset = root.CFrame:ToObjectSpace(oldPivot)
		say("PrimaryPart:", root:GetFullName(), "(pivot kept where it was)")
	end
end

if not bodyJoint then
	local part0 = root or armR
	if not part0 then fail("Could not find a root part or arm to attach the Scar to.") end
	bodyJoint = Instance.new("Motor6D")
	bodyJoint.Name = CONFIG.ScarName
	bodyJoint.Part0 = part0
	bodyJoint.Part1 = body
	bodyJoint.C0 = part0.CFrame:Inverse() * body.CFrame
	bodyJoint.C1 = CFrame.new()
	bodyJoint.Parent = part0
	say("Joint: created", bodyJoint:GetFullName(), "(the blaster had no Motor6D to copy)")
end

-- arms and hands: every one driven by exactly one Motor6D, nothing welding or anchoring them in place
local fwd0 = body.CFrame:VectorToWorldSpace(Vector3.new(0, 0, sigma)).Unit   -- firing direction
local function longAxis(sz)
	if sz.X >= sz.Y and sz.X >= sz.Z then return Vector3.new(1, 0, 0), sz.X end
	if sz.Y >= sz.Z then return Vector3.new(0, 1, 0), sz.Y end
	return Vector3.new(0, 0, 1), sz.Z
end
local function frontEnd(part)   -- local offset of the end of a long part that points toward the muzzle
	local axis, len = longAxis(part.Size)
	local tip = axis * (len / 2)
	if part.CFrame:VectorToWorldSpace(tip):Dot(fwd0) < 0 then tip = -tip end
	return tip
end
local function reachable(from, target)
	local seen, queue, head = { [from] = true }, { from }, 1
	while queue[head] do
		local p = queue[head]
		head += 1
		if p == target then return true end
		for _, m in ipairs(motorsNow()) do
			if m.Part0 == p and not seen[m.Part1] then seen[m.Part1] = true; table.insert(queue, m.Part1) end
		end
	end
	return false
end
local function freePart(p)
	p.Anchored = false
	for _, d in ipairs(vm:GetDescendants()) do
		if (d:IsA("WeldConstraint") or (d:IsA("JointInstance") and not d:IsA("Motor6D"))) and (d.Part0 == p or d.Part1 == p) then
			say("Removed weld", d:GetFullName(), "(it locked", p.Name, "so animations could not move it)")
			toBackup(d)
		end
	end
end
local function driveWith(part, parentPart, jointName)
	local drivers = {}
	for _, m in ipairs(motorsNow()) do if m.Part1 == part then table.insert(drivers, m) end end
	for i = 2, #drivers do
		say("Removed extra joint", drivers[i]:GetFullName(), "(only one joint may drive", part.Name .. ")")
		toBackup(drivers[i])
	end
	local m = drivers[1]
	if m and (m.Part0 == parentPart or reachable(parentPart, m.Part0)) then return m end
	if m then
		-- driven from outside the rig: re-attach it to the rig, keeping its name and current placement
		m.C0 = parentPart.CFrame:Inverse() * part.CFrame * m.C1
		m.Part0 = parentPart
		say("Joint:", m:GetFullName(), "now hangs off", parentPart.Name)
		return m
	end
	m = Instance.new("Motor6D")
	m.Name = jointName
	m.Part0 = parentPart
	m.Part1 = part
	m.C0 = parentPart.CFrame:Inverse() * part.CFrame
	m.C1 = CFrame.new()
	m.Parent = parentPart
	say("Joint: created", m:GetFullName())
	return m
end
local handR, handL
for _, side in ipairs({ "Right", "Left" }) do
	local arm = (side == "Right") and armR or armL
	if arm and root and arm ~= root then
		freePart(arm)
		driveWith(arm, root, side .. "Shoulder")
		if CONFIG.ResizeArms then
			local axis = longAxis(arm.Size)
			local t, L = CONFIG.ArmThickness, CONFIG.ArmLength
			arm.Size = Vector3.new(axis.X > 0 and L or t, axis.Y > 0 and L or t, axis.Z > 0 and L or t)
		end
		local hand = partNamed(string.lower(side), "hand")
		if hand == arm then hand = nil end
		if not hand and CONFIG.AddHands then
			hand = Instance.new("Part")
			hand.Name = side .. "Hand"
			hand.Size = CONFIG.HandSize
			hand.Color = CONFIG.HandColor
			hand.Material = Enum.Material.SmoothPlastic
			hand.CanCollide = false
			hand.CanTouch = false
			hand.CanQuery = false
			hand.Massless = true
			hand.CastShadow = arm.CastShadow
			hand.CFrame = arm.CFrame * CFrame.new(frontEnd(arm))
			hand.Parent = arm.Parent
			say("Created", hand:GetFullName())
		end
		if hand then
			freePart(hand)
			driveWith(hand, arm, side .. "Wrist")
		end
		if side == "Right" then handR = hand else handL = hand end
	end
end

-- Scar parts: unanchored, jointed to Body, copy the blaster's physics/render flags
local refPart = blasterPartRef or armR or body
local function prepPart(p)
	p.Anchored = false
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = refPart.CastShadow
end
prepPart(body)
for _, d in ipairs(scar:GetDescendants()) do
	if d:IsA("WeldConstraint") or d:IsA("JointInstance") then
		local touchesScarPart = (d.Part0 and isIn(d.Part0, scar)) and (d.Part1 and isIn(d.Part1, scar))
		if touchesScarPart and d ~= bodyJoint then d:Destroy() end
	end
end
local function rigChild(part, jointName)
	prepPart(part)
	local m = Instance.new("Motor6D")
	m.Name = jointName
	m.Part0 = body
	m.Part1 = part
	m.C0 = body.CFrame:ToObjectSpace(part.CFrame)
	m.C1 = CFrame.new()
	m.Parent = body
	return m
end
for _, d in ipairs(scar:GetDescendants()) do
	if d:IsA("BasePart") and d ~= body then
		rigChild(d, d.Name)
	end
end
say("Joint:", body.Name, "drives", (mag and mag.Name or "-"), "and", (slide and slide.Name or "-"))

-- muzzle: an Attachment on the Scar, and the old Muzzle_Att part (kept where it is) welded to the Scar
local muzzleAtt = body:FindFirstChild("Muzzle")
if not (muzzleAtt and muzzleAtt:IsA("Attachment")) then
	muzzleAtt = Instance.new("Attachment")
	muzzleAtt.Name = "Muzzle"
	muzzleAtt.Parent = body
end
muzzleAtt.CFrame = muzzleCF
for _, p in ipairs(keptParts) do
	p.CFrame = body.CFrame * muzzleCF
	p.Anchored = false
	p.CanCollide = false
	p.Massless = true
	for _, w in ipairs(p:GetChildren()) do
		if w:IsA("WeldConstraint") or w:IsA("JointInstance") then w:Destroy() end
	end
	local w = Instance.new("WeldConstraint")
	w.Part0 = body
	w.Part1 = p
	w.Parent = p
	say("Kept", p:GetFullName(), "and moved it to the Scar's muzzle (welded to Body)")
end

-- sounds: one Sound per animation event, played by a small client script when the marker is reached
local SOUND_VOLUME = { Equip = 0.4, Fire = 0.6, MagOut = 0.55, MagIn = 0.6, Tap = 0.5, RackBack = 0.55, RackRelease = 0.6 }
local SOUND_ORDER = { "Equip", "Fire", "MagOut", "MagIn", "Tap", "RackBack", "RackRelease" }
local missingIds = {}
for _, name in ipairs(SOUND_ORDER) do
	local snd = body:FindFirstChild(name)
	if not (snd and snd:IsA("Sound")) then
		snd = Instance.new("Sound")
		snd.Name = name
		snd.Volume = SOUND_VOLUME[name]
		snd.Parent = body
	end
	local id = CONFIG.Sounds[name]
	if id and id ~= "" then snd.SoundId = id end
	if snd.SoundId == "" then table.insert(missingIds, name) end
end
local PLAYER_SOURCE = [==[
-- Plays the Scar's sounds in time with its animations: every KeyframeMarker in an animation played on this
-- viewmodel plays the Sound with the same name in Scar.Body (Equip, Fire, MagOut, MagIn, Tap, RackBack,
-- RackRelease). Sounds without a SoundId are skipped, so leave Fire empty if your blaster code already
-- plays a shot sound.
local viewmodel = script.Parent
local animator = viewmodel:FindFirstChildWhichIsA("Animator", true)
local scar = viewmodel:FindFirstChild("Scar")
local soundHome = scar and scar:FindFirstChild("Body")
if not (animator and soundHome) then return end
local NAMES = { "Equip", "Fire", "MagOut", "MagIn", "Tap", "RackBack", "RackRelease" }
local hooked = setmetatable({}, { __mode = "k" })
animator.AnimationPlayed:Connect(function(track)
	if hooked[track] then return end
	hooked[track] = true
	for _, name in ipairs(NAMES) do
		track:GetMarkerReachedSignal(name):Connect(function()
			local sound = soundHome:FindFirstChild(name)
			if sound and sound:IsA("Sound") and sound.SoundId ~= "" then
				sound.TimePosition = 0
				sound:Play()
			end
		end)
	end
end)
]==]
do
	local old = vm:FindFirstChild("ScarSounds")
	if old then old:Destroy() end
	local player = Instance.new("Script")
	player.Name = "ScarSounds"
	player.RunContext = Enum.RunContext.Client
	player.Source = PLAYER_SOURCE
	player.Parent = vm
end
say("Sounds:", table.concat(SOUND_ORDER, ", "), "in", body:GetFullName(), "+ Script", vm.Name .. ".ScarSounds")
if #missingIds > 0 then
	note("No SoundId yet for:", table.concat(missingIds, ", "), "- paste IDs into those Sounds (or CONFIG.Sounds) to hear them.")
end

---------------------------------------------------------------------------------------------------
-- 4. Animation math (everything in world space, converted to Motor6D transforms at the end)
---------------------------------------------------------------------------------------------------
local motors = motorsNow()
local childrenOf, motorOf = {}, {}
for _, m in ipairs(motors) do
	childrenOf[m.Part0] = childrenOf[m.Part0] or {}
	table.insert(childrenOf[m.Part0], m)
	motorOf[m.Part1] = m
end
local roots, isRoot = {}, {}
for _, m in ipairs(motors) do
	if not motorOf[m.Part0] and not isRoot[m.Part0] then
		isRoot[m.Part0] = true
		table.insert(roots, m.Part0)
	end
end
-- rest pose (Transform = identity) of every jointed part, and a parent-first joint order
local rest, order = {}, {}
for _, r in ipairs(roots) do
	rest[r] = r.CFrame
	local queue = { r }
	local head = 1
	while queue[head] do
		local p0 = queue[head]
		head += 1
		for _, m in ipairs(childrenOf[p0] or {}) do
			if not rest[m.Part1] then
				rest[m.Part1] = rest[p0] * m.C0 * m.C1:Inverse()
				table.insert(order, m)
				table.insert(queue, m.Part1)
			end
		end
	end
end
if not rest[body] then fail("Scar.Body is not connected to the rig after rewiring; check the Output above.") end

local B0 = rest[body]
local fwd = B0:VectorToWorldSpace(Vector3.new(0, 0, sigma)).Unit
local up0 = B0:VectorToWorldSpace(Vector3.new(0, 1, 0)).Unit
local rightV = fwd:Cross(up0).Unit
local upV = rightV:Cross(fwd).Unit
local VIEW = CFrame.fromMatrix(Vector3.new(), rightV, upV, -fwd)   -- x right, y up, z back, LookVector = muzzle
local function viewVec(x, y, z) return VIEW:VectorToWorldSpace(Vector3.new(x, y, z)) end

local gripLocal = gunPoint(CONFIG.Points.Grip)
local forendLocal = gunPoint(CONFIG.Points.Forend)
local pivot = B0 * gripLocal          -- the gun turns around the right hand
-- the right hand follows the slant of the pistol grip; the left hand is square to the gun
local gripUp = (gunPoint(CONFIG.Points.GripTop) - gunPoint(CONFIG.Points.GripBottom)).Unit
local gripHandLocal = CFrame.fromMatrix(gripLocal, Vector3.new(1, 0, 0), gripUp)
local forendHandLocal = CFrame.new(forendLocal)
local magRest = mag and body.CFrame:ToObjectSpace(mag.CFrame)
local slideRest = slide and body.CFrame:ToObjectSpace(slide.CFrame)
local leftLocal = Vector3.new(sigma, 0, 0)   -- the gun's left side in Body space (the knob sticks out there)

local function frameFromDir(pos, dir)
	local hint = upV
	if math.abs(dir:Dot(hint)) > 0.98 then hint = -fwd end
	local r = dir:Cross(hint).Unit
	local u = r:Cross(dir).Unit
	return CFrame.fromMatrix(pos, r, u, -dir)
end
local function armInfo(arm, holdWorld, pivotOffset)
	if not (arm and rest[arm]) then return nil end
	local cf = rest[arm]
	local axis, len = longAxis(arm.Size)
	local e1, e2 = cf * (axis * (len / 2)), cf * (-axis * (len / 2))
	local tip, tail = e1, e2
	if (e2 - e1):Dot(fwd) > 0 then tip, tail = e2, e1 end
	local look = frameFromDir(cf.Position, (tip - tail).Unit)
	local thick = math.min(arm.Size.X, arm.Size.Y, arm.Size.Z)
	-- the forearm swings around a point below and behind where its hand rests
	local shoulder = holdWorld + viewVec(pivotOffset.X, pivotOffset.Y, pivotOffset.Z)
	return { part = arm, len = len, thick = thick, shoulder = shoulder, corr = look:Inverse() * cf }
end
local R_INFO = armInfo(armR, B0 * gripLocal, CONFIG.RightArmPivot)
local L_INFO = armInfo(armL, B0 * forendLocal, CONFIG.LeftArmPivot)
local function armCF(info, handPos)
	-- forearm from its pivot to the hand; its front end sits inside the hand block
	local d = handPos - info.shoulder
	d = (d.Magnitude > 1e-4) and d.Unit or fwd
	return frameFromDir(handPos - d * (info.len / 2), d) * info.corr
end

-- monotone cubic (PCHIP) curves through keys: smooth, no unwanted overshoot, exact peaks
local function curve(keys)
	local n = #keys
	local t, v, m, h, d = {}, {}, {}, {}, {}
	for i = 1, n do t[i], v[i] = keys[i][1], keys[i][2] end
	for i = 1, n - 1 do
		h[i] = t[i + 1] - t[i]
		d[i] = (v[i + 1] - v[i]) / h[i]
	end
	m[1], m[n] = 0, 0
	for i = 2, n - 1 do
		if d[i - 1] * d[i] <= 0 then
			m[i] = 0
		else
			local w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
			m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
		end
	end
	return function(x)
		if n == 1 or x <= t[1] then return v[1] end
		if x >= t[n] then return v[n] end
		local i = 1
		while x > t[i + 1] do i += 1 end
		local hh = t[i + 1] - t[i]
		local s = (x - t[i]) / hh
		local s2, s3 = s * s, s * s * s
		return (2 * s3 - 3 * s2 + 1) * v[i] + (s3 - 2 * s2 + s) * hh * m[i]
			+ (-2 * s3 + 3 * s2) * v[i + 1] + (s3 - s2) * hh * m[i + 1]
	end
end
local function zero() return 0 end
local function curves(spec)
	local out = {}
	for _, k in ipairs({ "x", "y", "z", "pitch", "yaw", "roll", "magDown", "magBack", "magTilt",
		"slide", "pull", "tapY" }) do
		out[k] = spec[k] and curve(spec[k]) or zero
	end
	return out
end

local function gunCF(c, t)
	local rot = VIEW * CFrame.Angles(math.rad(c.pitch(t)), math.rad(c.yaw(t)), math.rad(c.roll(t))) * VIEW:Inverse()
	return CFrame.new(viewVec(c.x(t), c.y(t), c.z(t))) * CFrame.new(pivot) * rot * CFrame.new(-pivot) * B0
end
local function magCF(gun, down, back, tilt)
	return gun * CFrame.new(0, -down, -sigma * back) * magRest * CFrame.Angles(math.rad(sigma * tilt), 0, 0)
end
local function slideCF(gun, back)
	return gun * CFrame.new(0, 0, -sigma * back) * slideRest
end

local HAND = CONFIG.HandSize
local TARGETS = {   -- where the left hand is (position and orientation) for each thing it holds
	forend = function(s) return s.gun * forendHandLocal end,
	magGrip = function(s) return s.mag and s.mag * CFrame.new(0, -mag.Size.Y * 0.18, 0) or s.gun * forendHandLocal end,
	magBottom = function(s)
		return s.mag and s.mag * CFrame.new(0, -(mag.Size.Y / 2 + HAND.Y / 2 - 0.06), 0) or s.gun * forendHandLocal
	end,
	knob = function(s)
		local cf = s.gun * CFrame.new(0, 0, -sigma * s.pull) * (slideRest or CFrame.new(gripLocal))
		local side = (slide and slide.Size.X / 2 or 0.05) + HAND.X / 2 - 0.04
		return cf * CFrame.new(leftLocal * side)   -- the palm against the charging handle
	end,
}
local function smoother(a) return a * a * a * (a * (a * 6 - 15) + 10) end
local function leftHand(prog, t, state)
	local cur = prog.start
	for _, mv in ipairs(prog.moves or {}) do
		local t0, t1, target, arc = mv[1], mv[2], mv[3], mv[4]
		if t < t0 then break end
		if t <= t1 then
			local e = smoother((t - t0) / (t1 - t0))
			local p = TARGETS[cur](state):Lerp(TARGETS[target](state), e)
			if arc then p += viewVec(arc.X, arc.Y, arc.Z) * math.sin(math.pi * e) end
			return p
		end
		cur = target
	end
	return TARGETS[cur](state)
end

-- one animation frame -> desired world CFrames -> Motor6D transforms
local animatedParts = {}
local function solve(desired)
	local W, T = {}, {}
	for _, r in ipairs(roots) do W[r] = rest[r] end
	for _, m in ipairs(order) do
		local w0 = W[m.Part0]
		local w1 = desired[m.Part1] or (w0 * m.C0 * m.C1:Inverse())
		W[m.Part1] = w1
		T[m] = m.C0:Inverse() * w0:Inverse() * w1 * m.C1
	end
	return T
end
local function frame(c, prog, t, gunOverride)
	local gun = gunOverride or gunCF(c, t)
	local state = { gun = gun, pull = c.pull(t) }
	local desired = { [body] = gun }
	if mag then
		state.mag = magCF(gun, c.magDown(t), c.magBack(t), c.magTilt(t))
		desired[mag] = state.mag
	end
	if slide then desired[slide] = slideCF(gun, c.slide(t)) end
	local rh = gun * gripHandLocal
	local lh = leftHand(prog, t, state) + viewVec(0, c.tapY(t), 0)
	if R_INFO then desired[armR] = armCF(R_INFO, rh.Position) end
	if L_INFO then desired[armL] = armCF(L_INFO, lh.Position) end
	if handR and rest[handR] then desired[handR] = rh end
	if handL and rest[handL] then desired[handL] = lh end
	for p in pairs(desired) do animatedParts[p] = true end
	return solve(desired)
end

-- joints that must appear in the animation: animated ones and the ones above them
local function includedJoints()
	local inc = {}
	for p in pairs(animatedParts) do
		local m = motorOf[p]
		while m and not inc[m] do
			inc[m] = true
			m = motorOf[m.Part0]
		end
	end
	return inc
end

local function buildSequence(name, duration, fps, loop, priority, sampler, markers)
	local seq = Instance.new("KeyframeSequence")
	seq.Name = name
	seq.Loop = loop
	seq.Priority = priority
	local frames = math.max(1, math.ceil(duration * fps - 1e-6))
	local samples = {}
	for i = 0, frames do
		local t = duration * i / frames
		samples[i] = { t, sampler(t) }
	end
	local inc = includedJoints()
	for i = 0, frames do
		local t, T = samples[i][1], samples[i][2]
		local kf = Instance.new("Keyframe")
		kf.Time = t
		local poseOf = {}
		for _, r in ipairs(roots) do
			local p = Instance.new("Pose")
			p.Name = r.Name
			p.CFrame = CFrame.new()
			p.Parent = kf
			poseOf[r] = p
		end
		for _, m in ipairs(order) do
			if inc[m] and poseOf[m.Part0] then
				local p = Instance.new("Pose")
				p.Name = m.Part1.Name
				p.CFrame = T[m]
				p.EasingStyle = Enum.PoseEasingStyle.Linear
				p.EasingDirection = Enum.PoseEasingDirection.In
				p.Weight = 1
				p.Parent = poseOf[m.Part0]
				poseOf[m.Part1] = p
			end
		end
		kf.Parent = seq
	end
	-- sound markers on the keyframe nearest to each event
	local kfs = seq:GetChildren()
	for _, mk in ipairs(markers or {}) do
		local best, bestDist
		for _, kf in ipairs(kfs) do
			local dist = math.abs(kf.Time - mk[2])
			if not best or dist < bestDist then best, bestDist = kf, dist end
		end
		local marker = Instance.new("KeyframeMarker")
		marker.Name = mk[1]
		marker.Value = ""
		best:AddMarker(marker)
	end
	return seq
end

---------------------------------------------------------------------------------------------------
-- 5. The four animations (times in seconds, offsets in studs, angles in degrees;
--    x right, y up, z back as seen from the camera; pitch + = muzzle up, yaw + = muzzle left,
--    roll - = top of the gun to the right)
---------------------------------------------------------------------------------------------------
local HOLD = { start = "forend" }

-- IDLE: slow breathing sway, seamless loop
local IDLE_LEN = 3.2
local function idleGun(t)
	local w = 2 * math.pi / IDLE_LEN
	local c = {
		x = function() return 0.012 * math.sin(w * t + 1.1) end,
		y = function() return 0.020 * math.sin(w * t) + 0.005 * math.sin(2 * w * t + 0.7) end,
		z = function() return 0.008 * math.sin(w * t + 2.0) end,
		pitch = function() return 0.60 * math.sin(w * t + 0.4) end,
		yaw = function() return 0.40 * math.sin(w * t + 2.2) end,
		roll = function() return 0.75 * math.sin(w * t + 1.0) end,
	}
	return gunCF(c, t)
end
local IDLE_C = curves({})

-- EQUIP: swing up from low-right, small overshoot, settle
local EQUIP_LEN = 0.6
local EQUIP_C = curves({
	x = { { 0, 0.30 }, { 0.30, 0.02 }, { 0.45, -0.006 }, { 0.60, 0 } },
	y = { { 0, -1.10 }, { 0.26, -0.06 }, { 0.36, 0.03 }, { 0.48, -0.005 }, { 0.60, 0 } },
	z = { { 0, 0.45 }, { 0.28, 0.04 }, { 0.40, -0.015 }, { 0.60, 0 } },
	pitch = { { 0, -45 }, { 0.26, -4 }, { 0.36, 4 }, { 0.48, -0.8 }, { 0.60, 0 } },
	roll = { { 0, -35 }, { 0.30, 3.5 }, { 0.44, -1.2 }, { 0.60, 0 } },
	yaw = { { 0, 18 }, { 0.28, -2 }, { 0.44, 0.6 }, { 0.60, 0 } },
})

-- SHOOT: sharp kick back and up, charging handle cycles, quick recovery (short enough for full auto)
local SHOOT_LEN = 0.14
local SHOOT_C = curves({
	z = { { 0, 0 }, { 0.022, 0.15 }, { 0.06, 0.04 }, { 0.14, 0 } },
	y = { { 0, 0 }, { 0.028, 0.028 }, { 0.08, 0.005 }, { 0.14, 0 } },
	pitch = { { 0, 0 }, { 0.028, 4.2 }, { 0.075, 0.9 }, { 0.14, 0 } },
	roll = { { 0, 0 }, { 0.03, -1.2 }, { 0.085, 0.3 }, { 0.14, 0 } },
	yaw = { { 0, 0 }, { 0.03, 0.6 }, { 0.14, 0 } },
	slide = { { 0, 0 }, { 0.018, 0.22 }, { 0.03, 0.22 }, { 0.065, 0 }, { 0.14, 0 } },
})

-- RELOAD: cant, mag out and away, new mag in with a seat bump, palm tap, rack the charging handle
local RELOAD_LEN = 2.35
local RELOAD_C = curves({
	roll = { { 0, 0 }, { 0.30, -24 }, { 0.62, -26 }, { 1.10, -22 }, { 1.42, -23 }, { 1.52, -26 }, { 1.62, -24 },
		{ 1.95, -18 }, { 2.12, -16 }, { 2.35, 0 } },
	pitch = { { 0, 0 }, { 0.30, 7 }, { 0.62, 5 }, { 0.70, 3.5 }, { 0.85, 5 }, { 1.10, 5 }, { 1.42, 6 }, { 1.50, 10 }, { 1.60, 6.5 },
		{ 1.70, 7.5 }, { 1.78, 6 }, { 1.95, 6 }, { 2.08, 4 }, { 2.13, 9 }, { 2.22, 5 }, { 2.35, 0 } },
	yaw = { { 0, 0 }, { 0.30, 9 }, { 1.42, 7 }, { 1.95, 4 }, { 2.35, 0 } },
	x = { { 0, 0 }, { 0.30, 0.05 }, { 1.95, 0.03 }, { 2.35, 0 } },
	y = { { 0, 0 }, { 0.30, 0.06 }, { 0.62, 0.05 }, { 0.70, 0.035 }, { 0.85, 0.055 }, { 1.42, 0.06 }, { 1.50, 0.09 },
		{ 1.60, 0.06 }, { 1.70, 0.07 }, { 1.78, 0.06 }, { 2.08, 0.05 }, { 2.13, 0.08 }, { 2.22, 0.055 }, { 2.35, 0 } },
	z = { { 0, 0 }, { 0.30, 0.05 }, { 1.50, 0.04 }, { 2.08, 0.06 }, { 2.13, 0.02 }, { 2.35, 0 } },
	magDown = { { 0, 0 }, { 0.50, 0 }, { 0.62, 0.12 }, { 0.80, 0.8 }, { 1.02, 2.8 }, { 1.10, 2.8 }, { 1.31, 0.7 },
		{ 1.44, 0.06 }, { 1.50, 0 }, { 2.35, 0 } },
	magBack = { { 0, 0 }, { 0.62, 0 }, { 0.80, 0.05 }, { 1.02, 0.6 }, { 1.10, 0.6 }, { 1.31, 0.1 }, { 1.44, 0 }, { 2.35, 0 } },
	magTilt = { { 0, 0 }, { 0.62, 0 }, { 0.80, 8 }, { 1.02, 30 }, { 1.10, 30 }, { 1.31, 14 }, { 1.44, 2 }, { 1.50, 0 },
		{ 2.35, 0 } },
	slide = { { 0, 0 }, { 1.95, 0 }, { 2.08, 0.34 }, { 2.10, 0.34 }, { 2.13, 0 }, { 2.35, 0 } },
	pull = { { 0, 0 }, { 1.95, 0 }, { 2.08, 0.34 }, { 2.35, 0.34 } },
	tapY = { { 0, 0 }, { 1.55, 0 }, { 1.63, -0.12 }, { 1.70, 0 }, { 2.35, 0 } },
})
local RELOAD_HAND = {
	start = "forend",
	moves = {
		{ 0.08, 0.46, "magGrip", Vector3.new(0, -0.18, 0.12) },
		{ 1.44, 1.52, "magBottom" },
		{ 1.74, 1.95, "knob", Vector3.new(-0.15, 0.10, 0.05) },
		{ 2.12, 2.33, "forend", Vector3.new(0, -0.06, 0.04) },
	},
}

local saves = vm:FindFirstChild("AnimSaves")
if not saves then
	saves = Instance.new("ObjectValue")
	saves.Name = "AnimSaves"
	saves.Parent = vm
end
local made = {}
local function publish(seq)
	local old = saves:FindFirstChild(seq.Name)
	if old then old:Destroy() end
	seq.Parent = saves
	table.insert(made, seq.Name)
end

-- run every sampler once first so the included joint set is complete for all four
local function idleSampler(t) return frame(IDLE_C, HOLD, t, idleGun(t)) end
local function equipSampler(t) return frame(EQUIP_C, HOLD, t) end
local function shootSampler(t) return frame(SHOOT_C, HOLD, t) end
local function reloadSampler(t) return frame(RELOAD_C, RELOAD_HAND, t) end
reloadSampler(1.0)

publish(buildSequence("Scar_Idle", IDLE_LEN, CONFIG.IdleFps, true, Enum.AnimationPriority.Idle, idleSampler))
publish(buildSequence("Scar_Equip", EQUIP_LEN, CONFIG.Fps, false, Enum.AnimationPriority.Action, equipSampler,
	{ { "Equip", 0.03 } }))
publish(buildSequence("Scar_Shoot", SHOOT_LEN, CONFIG.Fps, false, Enum.AnimationPriority.Action, shootSampler,
	{ { "Fire", 1 / 60 } }))
publish(buildSequence("Scar_Reload", RELOAD_LEN, CONFIG.Fps, false, Enum.AnimationPriority.Action2, reloadSampler,
	{ { "MagOut", 0.56 }, { "MagIn", 1.47 }, { "Tap", 1.68 }, { "RackBack", 1.97 }, { "RackRelease", 2.10 } }))

vm:SetAttribute("ScarRigVersion", 1)
ChangeHistoryService:SetWaypoint("Scar viewmodel setup")

say("Rig root:", (roots[1] and roots[1]:GetFullName()) or "?", "| arms:", armR and armR.Name or "-", armL and armL.Name or "-",
	"| hands:", handR and handR.Name or "-", handL and handL.Name or "-")
for _, m in ipairs(order) do say("  joint", m.Name, ":", m.Part0.Name, "->", m.Part1.Name) end
say("Animations saved in", saves:GetFullName() .. ":", table.concat(made, ", "))
say("Next: Animation Editor > select this viewmodel > ... > Load > pick one > Publish to Roblox (or right-click the")
say("KeyframeSequence > Save to Roblox). Put the 4 IDs where your blaster's Idle/Equip/Shoot/Reload animations were.")
local anims = {}
for _, d in ipairs(vm:GetDescendants()) do
	if d:IsA("Animation") then table.insert(anims, d:GetFullName() .. " = " .. d.AnimationId) end
end
if blaster then
	for _, d in ipairs(blaster:GetDescendants()) do
		if d:IsA("Animation") and not isIn(d, vm) then table.insert(anims, d:GetFullName() .. " = " .. d.AnimationId) end
	end
end
for _, s in ipairs(anims) do say("Existing Animation object:", s) end
