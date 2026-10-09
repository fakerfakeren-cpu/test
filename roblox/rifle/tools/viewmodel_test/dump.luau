-- Dump the finished viewmodel tree for the .rbxmx writer
local print = RAWPRINT
local vm = SCENE.vm
local ids, n = {}, 0
local function id(inst) if not ids[inst] then n += 1; ids[inst] = n end return ids[inst] end
local function cfs(c) return string.format("%.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g", c:GetComponents()) end
local function v3s(v) return string.format("%.9g %.9g %.9g", v.X, v.Y, v.Z) end
local function P(i, name, typ, val) print("P\t" .. i .. "\t" .. name .. "\t" .. typ .. "\t" .. val) end
local function emit(inst, parentId)
	local i = id(inst)
	local pr = rawget(inst, "_props")
	local cls = inst.ClassName
	if cls == "WeldConstraint" then cls = "Weld" end   -- written as a plain Weld (same result, simpler file)
	print("I\t" .. i .. "\t" .. parentId .. "\t" .. cls)
	P(i, "Name", "string", inst.Name)
	if inst:IsA("BasePart") then
		P(i, "CFrame", "CoordinateFrame", cfs(inst.CFrame)); P(i, "size", "Vector3", v3s(inst.Size))
		for _, k in ipairs({ "Anchored", "CanCollide", "CanTouch", "CanQuery", "Massless", "CastShadow" }) do P(i, k, "bool", tostring(inst[k])) end
		P(i, "Transparency", "float", string.format("%.9g", inst.Transparency))
		if pr.XColor then
			local c = pr.XColor
			P(i, "Color3uint8", "Color3uint8", tostring(0xFF000000 + c[1] * 65536 + c[2] * 256 + c[3]))
		end
		if pr.XMaterial then P(i, "Material", "token", tostring(pr.XMaterial)) end
		if pr.XShape then P(i, "shape", "token", tostring(pr.XShape)) end
		if cls == "Part" then P(i, "TopSurface", "token", "0"); P(i, "BottomSurface", "token", "0") end
		if pr.XMeshId then
			P(i, "MeshId", "Content", pr.XMeshId); P(i, "TextureID", "Content", pr.XTextureID)
			P(i, "InitialSize", "Vector3", v3s(pr.XInitialSize))
			P(i, "RenderFidelity", "token", "1")       -- Precise
			P(i, "CollisionFidelity", "token", "2")    -- Box
		end
		P(i, "PivotOffset", "CoordinateFrame", cfs(inst.PivotOffset))
	elseif inst:IsA("Motor6D") or inst:IsA("Weld") then
		P(i, "Part0", "Ref", tostring(id(inst.Part0))); P(i, "Part1", "Ref", tostring(id(inst.Part1)))
		P(i, "C0", "CoordinateFrame", cfs(inst.C0)); P(i, "C1", "CoordinateFrame", cfs(inst.C1))
	elseif inst.ClassName == "WeldConstraint" then
		P(i, "Part0", "Ref", tostring(id(inst.Part0))); P(i, "Part1", "Ref", tostring(id(inst.Part1)))
		P(i, "C0", "CoordinateFrame", cfs(inst.Part0.CFrame:Inverse() * inst.Part1.CFrame)); P(i, "C1", "CoordinateFrame", cfs(CFrame.new()))
	elseif inst.ClassName == "Attachment" then
		P(i, "CFrame", "CoordinateFrame", cfs(inst.CFrame))
	elseif inst.ClassName == "Model" then
		if inst.PrimaryPart then P(i, "PrimaryPart", "Ref", tostring(id(inst.PrimaryPart))) end
	elseif inst.ClassName == "KeyframeSequence" then
		P(i, "Loop", "bool", tostring(inst.Loop)); P(i, "Priority", "token", tostring(inst.Priority.Value))
	elseif inst.ClassName == "Keyframe" then
		P(i, "Time", "float", string.format("%.9g", inst.Time))
	elseif inst.ClassName == "Pose" then
		P(i, "CFrame", "CoordinateFrame", cfs(inst.CFrame)); P(i, "Weight", "float", string.format("%.9g", inst.Weight))
		P(i, "EasingStyle", "token", tostring(inst.EasingStyle.Value)); P(i, "EasingDirection", "token", tostring(inst.EasingDirection.Value))
	end
	for _, c in ipairs(inst:GetChildren()) do emit(c, i) end
end
emit(vm, 0)
