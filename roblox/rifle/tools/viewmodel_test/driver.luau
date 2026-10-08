local print = RAWPRINT
-- After the setup script ran: replay every KeyframeSequence the way the Animator does and check it.
local S = SCENE
local vm = S.vm
local function fmt(c) return string.format("%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f", c:GetComponents()) end
local function cfErr(a, b)
	local d = (a.Position - b.Position).Magnitude
	local r = 0
	for _, k in ipairs({ "RightVector", "UpVector", "LookVector" }) do r = math.max(r, (a[k] - b[k]).Magnitude) end
	return d, r
end
-- 1. the Scar must not have moved
for k, cf0 in pairs(S.rest) do
	local d, r = cfErr(S[k].CFrame, cf0)
	print(string.format("CHECK rest %s moved %.2e studs, rot %.2e", k, d, r))
end
do
	local pv = vm:GetPivot()
	local dd = (pv.Position - PIVOT_BEFORE.Position).Magnitude
	print(string.format("CHECK model pivot moved %.2e studs; PrimaryPart=%s", dd, vm.PrimaryPart and vm.PrimaryPart.Name or "nil"))
end
print("CHECK scar anchored:", tostring(S.body.Anchored), tostring(S.mag.Anchored), tostring(S.slide.Anchored))
-- 2. joints
local motors = {}
for _, d in ipairs(vm:GetDescendants()) do
	if d:IsA("Motor6D") and d.Part0 and d.Part1 then table.insert(motors, d) end
end
for _, m in ipairs(motors) do print("JOINT", m:GetFullName(), m.Part0.Name, "->", m.Part1.Name) end
local byNames = {}
for _, m in ipairs(motors) do byNames[m.Part0.Name .. ">" .. m.Part1.Name] = m end
local isPart1 = {}
for _, m in ipairs(motors) do isPart1[m.Part1] = true end
local roots = {}
for _, m in ipairs(motors) do if not isPart1[m.Part0] then roots[m.Part0] = true end end
for r in pairs(roots) do print("ROOTPART", r.Name, "anchored", tostring(r.Anchored)) end
-- 3. replay
local saves = vm:FindFirstChild("AnimSaves")
local seqs = saves and saves:GetChildren() or {}
local gripErrMax, forErrMax = 0, 0
local SIG = 1
local function armHand(arm)
	return arm.CFrame * Vector3.new(0, 0, -arm.Size.Z / 2)
end
for _, seq in ipairs(seqs) do
	local kfs = seq:GetChildren()
	table.sort(kfs, function(a, b) return a.Time < b.Time end)
	print(string.format("SEQ %s keyframes=%d length=%.3f loop=%s priority=%s", seq.Name, #kfs, kfs[#kfs].Time, tostring(seq.Loop), seq.Priority.Name))
	local prevPos, prevVel, maxAcc, maxSpeed = nil, nil, 0, 0
	for _, kf in ipairs(kfs) do
		for _, m in ipairs(motors) do m.Transform = CFrame.new() end
		local unmatched = 0
		local function apply(pose, parentName)
			for _, child in ipairs(pose:GetChildren()) do
				local m = byNames[parentName .. ">" .. child.Name]
				if m then m.Transform = child.CFrame else unmatched += 1 end
				apply(child, child.Name)
			end
		end
		for _, top in ipairs(kf:GetChildren()) do apply(top, top.Name) end
		if unmatched > 0 then print("ERROR unmatched poses", seq.Name, kf.Time, unmatched) end
		-- world CFrames
		local W = {}
		for r in pairs(roots) do W[r] = r.CFrame end
		local changed = true
		while changed do
			changed = false
			for _, m in ipairs(motors) do
				if W[m.Part0] and not W[m.Part1] then
					W[m.Part1] = W[m.Part0] * m.C0 * (m.Transform or CFrame.new()) * m.C1:Inverse()
					changed = true
				end
			end
		end
		for p, c in pairs(W) do
			if p.Name == "Body" or p.Name == "Magazine" or p.Name == "Slide" or p.Name == "RightArm" or p.Name == "LeftArm" then
				print("F " .. seq.Name .. " " .. string.format("%.4f", kf.Time) .. " " .. p.Name .. " " .. fmt(c))
			end
		end
		-- hands
		local gunW = W[S.body]
		local sx = S.body.Size.X / 0.37185
		local sy = S.body.Size.Y / 1.54026
		local sz = S.body.Size.Z / 4.249
		local grip = gunW * Vector3.new(0, -0.2655 * sy, -SIG * 0.5417 * sz)
		local fore = gunW * Vector3.new(0, 0.1 * sy, SIG * 0.95 * sz)
		local rh = W[S.armR] * Vector3.new(0, 0, -S.armR.Size.Z / 2)
		local lh = W[S.armL] * Vector3.new(0, 0, -S.armL.Size.Z / 2)
		gripErrMax = math.max(gripErrMax, (rh - grip).Magnitude)
		local onFore = seq.Name ~= "Scar_Reload" or kf.Time < 0.08 or kf.Time > 2.335
		if onFore then forErrMax = math.max(forErrMax, (lh - fore).Magnitude) end
		-- smoothness of the gun (studs/s, studs/s^2)
		local pos = gunW.Position
		if prevPos then
			local dt = 1 / 60
			local vel = (pos - prevPos) / dt
			maxSpeed = math.max(maxSpeed, vel.Magnitude)
			if prevVel then maxAcc = math.max(maxAcc, ((vel - prevVel) / dt).Magnitude) end
			prevVel = vel
		end
		prevPos = pos
	end
	print(string.format("SMOOTH %s max gun speed %.2f studs/s", seq.Name, maxSpeed))
end
print(string.format("CHECK right hand on grip: max error %.2e studs", gripErrMax))
print(string.format("CHECK left hand on forend (when it should be): max error %.2e studs", forErrMax))
for _, p in ipairs({ S.body, S.mag, S.slide, S.armR, S.armL }) do
	print("SIZE " .. p.Name .. string.format(" %.6f %.6f %.6f", p.Size.X, p.Size.Y, p.Size.Z))
end
print("ROOT " .. fmt(S.root.CFrame))
print("MUZZLE_ATT", S.muz.Anchored, tostring(S.muz.CFrame.Position))
