-- Minimal Roblox API mock: enough of Vector3/CFrame/Instance/services to run the setup script for real.
local V3 = {}
V3.__index = V3
local function v3(x, y, z) return setmetatable({ X = x or 0, Y = y or 0, Z = z or 0 }, V3) end
V3.__add = function(a, b) return v3(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
V3.__sub = function(a, b) return v3(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
V3.__unm = function(a) return v3(-a.X, -a.Y, -a.Z) end
V3.__mul = function(a, b)
	if type(a) == "number" then return v3(a * b.X, a * b.Y, a * b.Z) end
	if type(b) == "number" then return v3(a.X * b, a.Y * b, a.Z * b) end
	return v3(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
V3.__div = function(a, b)
	if type(b) == "number" then return v3(a.X / b, a.Y / b, a.Z / b) end
	return v3(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
V3.__eq = function(a, b) return a.X == b.X and a.Y == b.Y and a.Z == b.Z end
V3.__tostring = function(a) return string.format("%.4f, %.4f, %.4f", a.X, a.Y, a.Z) end
local V3mt_index = function(self, k)
	if k == "Magnitude" then return math.sqrt(self.X ^ 2 + self.Y ^ 2 + self.Z ^ 2) end
	if k == "Unit" then local m = math.sqrt(self.X ^ 2 + self.Y ^ 2 + self.Z ^ 2) return v3(self.X / m, self.Y / m, self.Z / m) end
	return V3[k]
end
V3.__index = V3mt_index
function V3.Dot(a, b) return a.X * b.X + a.Y * b.Y + a.Z * b.Z end
function V3.Cross(a, b) return v3(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X) end
function V3.Lerp(a, b, t) return a + (b - a) * t end
Vector3 = { new = v3 }

local CF = {}
local function cf(px, py, pz, r)
	return setmetatable({ p = v3(px, py, pz), r = r or { 1, 0, 0, 0, 1, 0, 0, 0, 1 } }, CF)
end
local function rotmul(a, b)
	local r = {}
	for i = 0, 2 do
		for j = 0, 2 do
			r[i * 3 + j + 1] = a[i * 3 + 1] * b[j + 1] + a[i * 3 + 2] * b[3 + j + 1] + a[i * 3 + 3] * b[6 + j + 1]
		end
	end
	return r
end
local function rotvec(r, v)
	return v3(r[1] * v.X + r[2] * v.Y + r[3] * v.Z, r[4] * v.X + r[5] * v.Y + r[6] * v.Z, r[7] * v.X + r[8] * v.Y + r[9] * v.Z)
end
local function transpose(r) return { r[1], r[4], r[7], r[2], r[5], r[8], r[3], r[6], r[9] } end
CF.__index = function(self, k)
	if k == "Position" then return self.p end
	if k == "X" then return self.p.X end
	if k == "Y" then return self.p.Y end
	if k == "Z" then return self.p.Z end
	if k == "RightVector" then return v3(self.r[1], self.r[4], self.r[7]) end
	if k == "UpVector" then return v3(self.r[2], self.r[5], self.r[8]) end
	if k == "LookVector" then return v3(-self.r[3], -self.r[6], -self.r[9]) end
	return CF[k]
end
CF.__mul = function(a, b)
	if getmetatable(b) == CF then
		local p = a.p + rotvec(a.r, b.p)
		local r = rotmul(a.r, b.r)
		return cf(p.X, p.Y, p.Z, r)
	end
	return a.p + rotvec(a.r, b)
end
CF.__add = function(a, v) local p = a.p + v return cf(p.X, p.Y, p.Z, a.r) end
function CF.Inverse(a)
	local rt = transpose(a.r)
	local p = -rotvec(rt, a.p)
	return cf(p.X, p.Y, p.Z, rt)
end
function CF.ToObjectSpace(a, b) return a:Inverse() * b end
function CF.ToWorldSpace(a, b) return a * b end
function CF.PointToObjectSpace(a, v) return rotvec(transpose(a.r), v - a.p) end
function CF.PointToWorldSpace(a, v) return a * v end
function CF.VectorToWorldSpace(a, v) return rotvec(a.r, v) end
function CF.VectorToObjectSpace(a, v) return rotvec(transpose(a.r), v) end
function CF.GetComponents(a) local r = a.r return a.p.X, a.p.Y, a.p.Z, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9] end
local function rx(t) local c, s = math.cos(t), math.sin(t) return { 1, 0, 0, 0, c, -s, 0, s, c } end
local function ry(t) local c, s = math.cos(t), math.sin(t) return { c, 0, s, 0, 1, 0, -s, 0, c } end
local function rz(t) local c, s = math.cos(t), math.sin(t) return { c, -s, 0, s, c, 0, 0, 0, 1 } end
local function fromCols(p, x, y, z)
	return cf(p.X, p.Y, p.Z, { x.X, y.X, z.X, x.Y, y.Y, z.Y, x.Z, y.Z, z.Z })
end
CFrame = {
	new = function(a, b, c, ...)
		if a == nil then return cf(0, 0, 0) end
		if type(a) == "table" then return cf(a.X, a.Y, a.Z) end
		local extra = { ... }
		if #extra == 9 then return cf(a, b, c, extra) end
		return cf(a, b, c)
	end,
	Angles = function(x, y, z) return cf(0, 0, 0, rotmul(rotmul(rx(x), ry(y)), rz(z))) end,
	fromMatrix = function(p, x, y, z)
		z = z or x:Cross(y).Unit
		return fromCols(p, x, y, z)
	end,
	lookAt = function(at, target, up)
		up = up or v3(0, 1, 0)
		local look = (target - at).Unit
		local right = look:Cross(up).Unit
		local u = right:Cross(look).Unit
		return fromCols(at, right, u, -look)
	end,
}
CFrame.fromEulerAnglesXYZ = CFrame.Angles
IS_CFRAME = function(x) return getmetatable(x) == CF end
QUAT_CF = function(px, py, pz, qx, qy, qz, qw)   -- glTF (x,y,z,w) quaternion helper for scene building
	local r = {
		1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw),
		2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw),
		2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy),
	}
	return cf(px, py, pz, r)
end

-- Enums
local function enumItems(names)
	local t = {}
	for i, n in ipairs(names) do t[n] = { Name = n, Value = i - 1 } end
	return t
end
Enum = {
	PoseEasingStyle = enumItems({ "Linear", "Constant", "Elastic", "Cubic", "Bounce", "CubicV2" }),
	PoseEasingDirection = enumItems({ "In", "Out", "InOut" }),
	AnimationPriority = enumItems({ "Idle", "Movement", "Action", "Action2", "Action3", "Action4", "Core" }),
}

-- Instances
local SUPER = {
	Part = "BasePart", MeshPart = "BasePart", BasePart = "PVInstance", Model = "PVInstance", PVInstance = "Instance",
	Motor6D = "JointInstance", Weld = "JointInstance", JointInstance = "Instance", WeldConstraint = "Instance",
	PointLight = "Light", SpotLight = "Light", Light = "Instance", Script = "BaseScript", LocalScript = "BaseScript",
	BaseScript = "LuaSourceContainer", ModuleScript = "LuaSourceContainer", LuaSourceContainer = "Instance",
	ObjectValue = "ValueBase", StringValue = "ValueBase", NumberValue = "ValueBase", ValueBase = "Instance",
	Workspace = "Model",
}
local DEFAULTS = {
	BasePart = { CFrame = function() return CFrame.new() end, PivotOffset = function() return CFrame.new() end, Size = function() return v3(1, 1, 1) end, Anchored = false,
		CanCollide = true, CanTouch = true, CanQuery = true, Massless = false, CastShadow = true, Transparency = 0 },
	JointInstance = { C0 = function() return CFrame.new() end, C1 = function() return CFrame.new() end, Enabled = true },
	Attachment = { CFrame = function() return CFrame.new() end },
	Pose = { CFrame = function() return CFrame.new() end, Weight = 1 },
	Keyframe = { Time = 0 },
	KeyframeSequence = { Loop = true },
	Animation = { AnimationId = "" },
}
local Inst = {}
local allInstances = {}
local function isA(class, name)
	while class do
		if class == name then return true end
		class = SUPER[class]
	end
	return name == "Instance"
end
local function new(className)
	local self = { _props = { Name = className, ClassName = className, Archivable = true }, _children = {}, _attrs = {} }
	for cls, props in pairs(DEFAULTS) do
		if isA(className, cls) then
			for k, v in pairs(props) do
				self._props[k] = (type(v) == "function") and v() or v
			end
		end
	end
	setmetatable(self, Inst)
	table.insert(allInstances, self)
	return self
end
Inst.__index = function(self, k)
	if Inst[k] then return Inst[k] end
	local props = rawget(self, "_props")
	if k == "Position" and props.CFrame and isA(props.ClassName, "BasePart") then return props.CFrame.Position end
	if k == "WorldCFrame" and props.ClassName == "Attachment" then return props.Parent.CFrame * props.CFrame end
	if k == "WorldPosition" and props.ClassName == "Attachment" then return (props.Parent.CFrame * props.CFrame).Position end
	if props[k] ~= nil then return props[k] end
	for _, c in ipairs(rawget(self, "_children")) do
		if c.Name == k then return c end
	end
	if k == "Parent" or k == "PrimaryPart" or k == "Part0" or k == "Part1" then return nil end
	error("mock: unknown property " .. tostring(k) .. " on " .. tostring(props.ClassName), 2)
end
Inst.__newindex = function(self, k, v)
	local props = rawget(self, "_props")
	if k == "Parent" then
		local old = props.Parent
		if old then
			local ch = rawget(old, "_children")
			for i, c in ipairs(ch) do if c == self then table.remove(ch, i) break end end
		end
		props.Parent = v
		if v then table.insert(rawget(v, "_children"), self) end
		return
	end
	if k == "WorldCFrame" and props.ClassName == "Attachment" then
		props.CFrame = props.Parent.CFrame:Inverse() * v
		return
	end
	if k == "Position" and isA(props.ClassName, "BasePart") then
		props.CFrame = CFrame.new(v) * CFrame.fromMatrix(v3(), props.CFrame.RightVector, props.CFrame.UpVector)
		return
	end
	props[k] = v
end
Inst.__tostring = function(self) return self.Name end
function Inst.IsA(self, name) return isA(self.ClassName, name) end
function Inst.GetChildren(self) local t = {} for i, c in ipairs(rawget(self, "_children")) do t[i] = c end return t end
function Inst.GetDescendants(self)
	local out = {}
	local function walk(x) for _, c in ipairs(rawget(x, "_children")) do table.insert(out, c) walk(c) end end
	walk(self)
	return out
end
function Inst.FindFirstChild(self, name, recursive)
	for _, c in ipairs(recursive and self:GetDescendants() or rawget(self, "_children")) do
		if c.Name == name then return c end
	end
	return nil
end
function Inst.FindFirstChildWhichIsA(self, cls, recursive)
	for _, c in ipairs(recursive and self:GetDescendants() or rawget(self, "_children")) do
		if c:IsA(cls) then return c end
	end
	return nil
end
Inst.FindFirstChildOfClass = function(self, cls)
	for _, c in ipairs(rawget(self, "_children")) do if c.ClassName == cls then return c end end
	return nil
end
function Inst.FindFirstAncestorWhichIsA(self, cls)
	local p = self.Parent
	while p do if p:IsA(cls) then return p end p = p.Parent end
	return nil
end
function Inst.IsDescendantOf(self, other)
	local p = self.Parent
	while p do if p == other then return true end p = p.Parent end
	return false
end
function Inst.GetFullName(self)
	local parts, p = {}, self
	while p and p.ClassName ~= "DataModel" do table.insert(parts, 1, p.Name) p = p.Parent end
	return table.concat(parts, ".")
end
function Inst.Destroy(self) self.Parent = nil; rawget(self, "_props").Destroyed = true end
function Inst.GetPivot(self)
	if self:IsA("BasePart") then return self.CFrame * self.PivotOffset end
	local pp = rawget(self, "_props").PrimaryPart
	if pp and pp:IsDescendantOf(self) then return pp.CFrame * pp.PivotOffset end
	return rawget(self, "_props").WorldPivot or CFrame.new()
end
function Inst.SetAttribute(self, k, v) rawget(self, "_attrs")[k] = v end
function Inst.GetAttribute(self, k) return rawget(self, "_attrs")[k] end
function Inst.Clone(self)
	if not self.Archivable then return nil end
	local c = new(self.ClassName)
	for k, v in pairs(rawget(self, "_props")) do
		if k ~= "Parent" then rawget(c, "_props")[k] = v end
	end
	for _, ch in ipairs(rawget(self, "_children")) do
		local cc = ch:Clone()
		if cc then cc.Parent = c end
	end
	return c
end
Instance = { new = new }

-- DataModel / services
local log = {}
game = new("DataModel")
rawget(game, "_props").Name = "Game"
local services = {}
for _, n in ipairs({ "Workspace", "ServerStorage", "ReplicatedStorage" }) do
	local s = new(n)
	s.Name = n
	s.Parent = game
	services[n] = s
end
workspace = services.Workspace
SELECTION = {}
services.Selection = { Get = function() return SELECTION end }
services.ChangeHistoryService = { SetWaypoint = function(_, name) table.insert(log, "waypoint: " .. name) end }
function Inst.GetService(self, name)
	local s = services[name]
	if not s then error("mock: no service " .. name) end
	return s
end
RAWPRINT = print
OUTPUT = {}
print = function(...)
	local t = { ... }
	for i = 1, #t do t[i] = tostring(t[i]) end
	table.insert(OUTPUT, "PRINT " .. table.concat(t, " "))
end
warn = function(...)
	local t = { ... }
	for i = 1, #t do t[i] = tostring(t[i]) end
	table.insert(OUTPUT, "WARN  " .. table.concat(t, " "))
end
