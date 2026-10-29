--!native
-- 2D terrain renderer test bench (LocalScript, goes in StarterPlayer > StarterPlayerScripts).
--
-- Not a game. It answers one question: can EditableImage chunks carry a Terraria-style
-- world on Roblox? It measures chunk memory against the client budget, chunk redraw and
-- upload cost, how uploads behave when many happen in one frame, lighting cost, and
-- sprite/particle load. Every texture is generated in code, so nothing has to be uploaded.
--
-- Controls (keyboard/mouse): A/D move, Space jump, hold LMB dig, hold RMB place dirt,
-- T place torch. On touch devices bench mode starts on and holding a finger digs.

local AssetService = game:GetService("AssetService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local CONFIG = {
	WORLD_W = 1600, -- tiles, must be a multiple of CHUNK
	WORLD_H = 608, -- tiles, must be a multiple of CHUNK
	CHUNK = 32, -- tiles per chunk side
	TILE_ART = 8, -- source pixels per tile side
	SCALE = 2, -- screen pixels per source pixel
	MARGIN = 1, -- ring of chunks kept loaded around the screen
	UPLOADS_PER_FRAME = 4, -- full chunk uploads per frame (cycled by a button)
	ATLAS_ASSET_ID = 0, -- uploaded tile sheet (layout in README); 0 = generated textures
	LIGHT_HZ = 30, -- lightmap recomputes per second (cycled by a button)
	LIGHT_PAD = 12, -- extra tiles computed around the screen so edge light is right
	LIGHT_SKIPS_CHUNK_FRAME = false, -- true: never upload light and chunks in the same frame
	MOB_COUNT = 50,
	MAX_PARTICLES = 200,
	BENCH_SPEED = 40, -- tiles per second the bench camera pans
	BENCH_EDITS = 30, -- tile edits per second in bench mode
}

local W, H = CONFIG.WORLD_W, CONFIG.WORLD_H
local CHUNK = CONFIG.CHUNK
local TILE_ART = CONFIG.TILE_ART
local CHUNK_ART = CHUNK * TILE_ART -- 256 source px per chunk side
local TILE_PX = TILE_ART * CONFIG.SCALE
local CHUNK_PX = CHUNK_ART * CONFIG.SCALE
local CHUNKS_X, CHUNKS_Y = W // CHUNK, H // CHUNK
local TILE_BYTES = TILE_ART * TILE_ART * 4
local TILE_ROW_BYTES = TILE_ART * 4
local CHUNK_ROW_BYTES = CHUNK_ART * 4
local CHUNK_BYTES = CHUNK_ART * CHUNK_ART * 4
local CHUNK_SIZE = Vector2.new(CHUNK_ART, CHUNK_ART)
local TILE_SIZE = Vector2.new(TILE_ART, TILE_ART)

local GRAVITY = 70 -- tiles/s^2
local MAX_FALL = 28 -- tiles/s, keeps per-frame movement under one tile at 30 fps
local EPS = 1e-4

--------------------------------------------------------------------------------
-- Tiles
--------------------------------------------------------------------------------

local AIR, DIRT, GRASS, STONE, ORE, TORCH = 0, 1, 2, 3, 4, 5
local FG_COUNT = 6
local NO_WALL, DIRT_WALL, STONE_WALL = 0, 1, 2
local WALL_COUNT = 3

local SOLID = { [AIR] = false, [DIRT] = true, [GRASS] = true, [STONE] = true, [ORE] = true, [TORCH] = false }
local PARTICLE_COLOR = {
	[DIRT] = Color3.fromRGB(120, 80, 50),
	[GRASS] = Color3.fromRGB(70, 150, 60),
	[STONE] = Color3.fromRGB(120, 120, 128),
	[ORE] = Color3.fromRGB(200, 120, 60),
	[TORCH] = Color3.fromRGB(255, 200, 80),
}

local fg = buffer.create(W * H)
local wall = buffer.create(W * H)

local function inWorld(x: number, y: number): boolean
	return x >= 0 and x < W and y >= 0 and y < H
end

local function getFg(x: number, y: number): number
	return buffer.readu8(fg, y * W + x)
end

local function solidAt(x: number, y: number): boolean
	if not inWorld(x, y) then
		return true
	end
	return SOLID[buffer.readu8(fg, y * W + x)]
end

local surfaceY = table.create(W, 0)

local function generateWorld(worldSeed: number)
	local rng = Random.new(worldSeed)
	local seed = worldSeed % 1000 + 0.317 -- math.noise is 0 at integer points, so keep the seed off them
	for x = 0, W - 1 do
		local surface = math.floor(H * 0.3 + math.noise(x * 0.02, seed) * 50 + math.noise(x * 0.1, seed + 1) * 8)
		local dirtDepth = 10 + math.floor(math.noise(x * 0.05, seed + 2) * 8)
		surfaceY[x + 1] = surface
		for y = 0, H - 1 do
			local f, w = AIR, NO_WALL
			if y == surface then
				f = GRASS
			elseif y > surface then
				local deep = y > surface + dirtDepth
				f = if deep then STONE else DIRT
				w = if deep then STONE_WALL else DIRT_WALL
				if y > surface + 4 and math.noise(x * 0.06, y * 0.06, seed + 3) > 0.22 then
					f = if rng:NextNumber() < 0.003 then TORCH else AIR
				elseif deep and math.noise(x * 0.15, y * 0.15, seed + 4) > 0.42 then
					f = ORE
				end
			end
			local i = y * W + x
			buffer.writeu8(fg, i, f)
			buffer.writeu8(wall, i, w)
		end
	end
end

--------------------------------------------------------------------------------
-- Generated textures. Every foreground/wall pair is baked into one atlas slot,
-- so a chunk is drawn with plain buffer copies and no per-pixel blending.
--------------------------------------------------------------------------------

local function noiseTexture(seed: number, r: number, g: number, b: number, spread: number): buffer
	local tex = buffer.create(TILE_BYTES)
	local rng = Random.new(seed)
	for p = 0, TILE_ART * TILE_ART - 1 do
		local k = 1 + (rng:NextNumber() - 0.5) * spread
		buffer.writeu8(tex, p * 4, math.clamp(math.floor(r * k), 0, 255))
		buffer.writeu8(tex, p * 4 + 1, math.clamp(math.floor(g * k), 0, 255))
		buffer.writeu8(tex, p * 4 + 2, math.clamp(math.floor(b * k), 0, 255))
		buffer.writeu8(tex, p * 4 + 3, 255)
	end
	return tex
end

local function setPixel(tex: buffer, px: number, py: number, r: number, g: number, b: number, a: number)
	local o = (py * TILE_ART + px) * 4
	buffer.writeu8(tex, o, r)
	buffer.writeu8(tex, o + 1, g)
	buffer.writeu8(tex, o + 2, b)
	buffer.writeu8(tex, o + 3, a)
end

-- Optional uploaded tile sheet: 8x8 tiles, row 0 = foreground in id order
-- (AIR, DIRT, GRASS, STONE, ORE, TORCH), row 1 = walls (NO_WALL, DIRT_WALL, STONE_WALL).
-- It is read into a buffer once and the EditableImage is destroyed, so it costs no budget.
local tileSource = "generated"

local function loadSheet(): (buffer?, number)
	if CONFIG.ATLAS_ASSET_ID == 0 then
		return nil, 0
	end
	local ok, image = pcall(function()
		return AssetService:CreateEditableImageAsync(Content.fromAssetId(CONFIG.ATLAS_ASSET_ID))
	end)
	if not ok or not image then
		tileSource = "generated (sheet failed: " .. string.sub(tostring(image), 1, 60) .. ")"
		return nil, 0
	end
	local size = image.Size
	if size.X < FG_COUNT * TILE_ART or size.Y < 2 * TILE_ART then
		image:Destroy()
		tileSource = string.format("generated (sheet is %dx%d, needs %dx%d)", size.X, size.Y, FG_COUNT * TILE_ART, 2 * TILE_ART)
		return nil, 0
	end
	local pixels = image:ReadPixelsBuffer(Vector2.zero, size)
	image:Destroy()
	tileSource = "sheet " .. CONFIG.ATLAS_ASSET_ID
	return pixels, size.X
end

local sheet, sheetW = loadSheet()

local function sheetTile(col: number, row: number): buffer
	local tex = buffer.create(TILE_BYTES)
	for r = 0, TILE_ART - 1 do
		local src = ((row * TILE_ART + r) * sheetW + col * TILE_ART) * 4
		buffer.copy(tex, r * TILE_ROW_BYTES, sheet :: buffer, src, TILE_ROW_BYTES)
	end
	return tex
end

local function buildFgTextures(): { [number]: buffer }
	local t = {}
	if sheet then
		for f = 0, FG_COUNT - 1 do
			t[f] = sheetTile(f, 0)
		end
		t[AIR] = buffer.create(TILE_BYTES)
		return t
	end
	t[AIR] = buffer.create(TILE_BYTES) -- fully transparent
	t[DIRT] = noiseTexture(1, 125, 85, 55, 0.35)
	t[STONE] = noiseTexture(2, 125, 125, 132, 0.3)
	local grass = noiseTexture(3, 125, 85, 55, 0.35)
	for px = 0, TILE_ART - 1 do
		for py = 0, 1 do
			setPixel(grass, px, py, 70, 155 + (px % 3) * 15, 60, 255)
		end
	end
	t[GRASS] = grass
	local ore = noiseTexture(4, 125, 125, 132, 0.3)
	local rng = Random.new(5)
	for _ = 1, 10 do
		setPixel(ore, rng:NextInteger(0, TILE_ART - 1), rng:NextInteger(0, TILE_ART - 1), 215, 125, 60, 255)
	end
	t[ORE] = ore
	local torch = buffer.create(TILE_BYTES)
	for py = 3, 7 do
		setPixel(torch, 3, py, 110, 70, 40, 255)
		setPixel(torch, 4, py, 90, 55, 30, 255)
	end
	for py = 1, 2 do
		setPixel(torch, 3, py, 255, 220, 90, 255)
		setPixel(torch, 4, py, 255, 170, 50, 255)
	end
	t[TORCH] = torch
	return t
end

local function buildWallTextures(): { [number]: buffer }
	if sheet then
		local t = {}
		for w = 0, WALL_COUNT - 1 do
			t[w] = sheetTile(w, 1)
		end
		t[NO_WALL] = buffer.create(TILE_BYTES)
		return t
	end
	return {
		[NO_WALL] = buffer.create(TILE_BYTES),
		[DIRT_WALL] = noiseTexture(6, 60, 40, 28, 0.3),
		[STONE_WALL] = noiseTexture(7, 55, 55, 62, 0.3),
	}
end

-- tint is an {r, g, b} multiplier; used by the flash test to make a visibly different atlas
local function buildAtlas(tint: { number }): buffer
	local fgTex, wallTex = buildFgTextures(), buildWallTextures()
	local atlas = buffer.create(FG_COUNT * WALL_COUNT * TILE_BYTES)
	for f = 0, FG_COUNT - 1 do
		for w = 0, WALL_COUNT - 1 do
			local base = (f * WALL_COUNT + w) * TILE_BYTES
			for p = 0, TILE_ART * TILE_ART - 1 do
				local src = if buffer.readu8(fgTex[f], p * 4 + 3) > 0 then fgTex[f] else wallTex[w]
				for c = 0, 2 do
					local v = math.floor(buffer.readu8(src, p * 4 + c) * tint[c + 1])
					buffer.writeu8(atlas, base + p * 4 + c, math.clamp(v, 0, 255))
				end
				buffer.writeu8(atlas, base + p * 4 + 3, buffer.readu8(src, p * 4 + 3))
			end
		end
	end
	return atlas
end

local atlasNormal = buildAtlas({ 1, 1, 1 })
local atlasFlash = buildAtlas({ 1.6, 0.7, 0.7 })
local atlas = atlasNormal

local function slotOf(i: number): number
	return buffer.readu8(fg, i) * WALL_COUNT + buffer.readu8(wall, i)
end

--------------------------------------------------------------------------------
-- Stats
--------------------------------------------------------------------------------

local stats = {
	frames = 0,
	worstDt = 0,
	chunkUploads = 0,
	chunkBuildTime = 0,
	chunkUploadTime = 0,
	tileWrites = 0,
	lightUpdates = 0,
	lightTime = 0,
	maxUploadsInFrame = 0,
	poolShortage = 0,
}
local memoryBytes = 0
local poolCreateError: string? = nil
local probeResult = "Probe: not run"
local flashResult = ""

--------------------------------------------------------------------------------
-- GUI
--------------------------------------------------------------------------------

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local camera = workspace.CurrentCamera
camera.CameraType = Enum.CameraType.Scriptable
camera.CFrame = CFrame.new(0, 10000, 0) * CFrame.Angles(math.rad(90), 0, 0) -- look at empty sky

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "TerrainBench"
screenGui.IgnoreGuiInset = true
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 10
screenGui.Parent = playerGui

local sky = Instance.new("Frame")
sky.Size = UDim2.fromScale(1, 1)
sky.BackgroundColor3 = Color3.fromRGB(120, 175, 235)
sky.BorderSizePixel = 0
sky.Parent = screenGui

local worldFrame = Instance.new("Frame")
worldFrame.BackgroundTransparency = 1
worldFrame.Size = UDim2.fromOffset(0, 0)
worldFrame.Parent = sky

while screenGui.AbsoluteSize.X < 2 do
	task.wait()
end
-- Read once: resize the window or rotate the phone, then rejoin.
local viewW, viewH = math.floor(screenGui.AbsoluteSize.X), math.floor(screenGui.AbsoluteSize.Y)

local function createImage(size: Vector2): (EditableImage?, string?)
	local ok, result = pcall(function()
		return AssetService:CreateEditableImage({ Size = size })
	end)
	if not ok then
		return nil, tostring(result)
	end
	if not result then
		return nil, "CreateEditableImage returned nil"
	end
	return result, nil
end

local function imageLabel(image: EditableImage, sizePx: Vector2, z: number): ImageLabel
	local label = Instance.new("ImageLabel")
	label.BackgroundTransparency = 1
	label.BorderSizePixel = 0
	label.Size = UDim2.fromOffset(sizePx.X, sizePx.Y)
	label.ResampleMode = Enum.ResamplerMode.Pixelated
	label.ImageContent = Content.fromObject(image)
	label.ZIndex = z
	label.Parent = worldFrame
	return label
end

--------------------------------------------------------------------------------
-- Chunk pool: a fixed set of 256x256 EditableImages created once and reused.
--------------------------------------------------------------------------------

type Entry = {
	image: EditableImage,
	label: ImageLabel,
	cx: number?,
	cy: number?,
	dirty: boolean,
	drawn: boolean,
}

local poolCols = math.ceil(viewW / CHUNK_PX) + 1 + CONFIG.MARGIN * 2
local poolRows = math.ceil(viewH / CHUNK_PX) + 1 + CONFIG.MARGIN * 2
local entries: { Entry } = {}
local freeEntries: { Entry } = {}
local resident: { [number]: Entry } = {}

for _ = 1, poolCols * poolRows do
	local image, err = createImage(CHUNK_SIZE)
	if not image then
		poolCreateError = err
		break
	end
	local label = imageLabel(image, Vector2.new(CHUNK_PX, CHUNK_PX), 1)
	label.Visible = false
	local entry: Entry = { image = image, label = label, cx = nil, cy = nil, dirty = false, drawn = false }
	table.insert(entries, entry)
	table.insert(freeEntries, entry)
	memoryBytes += CHUNK_BYTES
end

local scratch = buffer.create(CHUNK_BYTES)
local tileScratch = buffer.create(TILE_BYTES)

local function buildChunk(cx: number, cy: number)
	local x0, y0 = cx * CHUNK, cy * CHUNK
	for ly = 0, CHUNK - 1 do
		local rowBase = (y0 + ly) * W + x0
		local dstRow = ly * TILE_ART * CHUNK_ROW_BYTES
		for lx = 0, CHUNK - 1 do
			local src = slotOf(rowBase + lx) * TILE_BYTES
			local dst = dstRow + lx * TILE_ROW_BYTES
			for r = 0, TILE_ART - 1 do
				buffer.copy(scratch, dst + r * CHUNK_ROW_BYTES, atlas, src + r * TILE_ROW_BYTES, TILE_ROW_BYTES)
			end
		end
	end
end

local function uploadChunk(entry: Entry)
	local t0 = os.clock()
	buildChunk(entry.cx :: number, entry.cy :: number)
	local t1 = os.clock()
	entry.image:WritePixelsBuffer(Vector2.zero, CHUNK_SIZE, scratch)
	local t2 = os.clock()
	stats.chunkBuildTime += t1 - t0
	stats.chunkUploadTime += t2 - t1
	stats.chunkUploads += 1
	entry.dirty = false
	entry.drawn = true
	entry.label.Visible = true
end

local camX, camY = 0, 0 -- top-left of the view, in screen pixels

local function updateResidency()
	local cx0 = math.max(0, camX // CHUNK_PX - CONFIG.MARGIN)
	local cy0 = math.max(0, camY // CHUNK_PX - CONFIG.MARGIN)
	local cx1 = math.min(CHUNKS_X - 1, (camX + viewW) // CHUNK_PX + CONFIG.MARGIN)
	local cy1 = math.min(CHUNKS_Y - 1, (camY + viewH) // CHUNK_PX + CONFIG.MARGIN)

	for _, e in entries do
		local cx, cy = e.cx, e.cy
		if cx and cy and (cx < cx0 or cx > cx1 or cy < cy0 or cy > cy1) then
			resident[cy * CHUNKS_X + cx] = nil
			e.cx, e.cy = nil, nil
			e.dirty, e.drawn = false, false
			e.label.Visible = false
			table.insert(freeEntries, e)
		end
	end

	for cy = cy0, cy1 do
		for cx = cx0, cx1 do
			local key = cy * CHUNKS_X + cx
			if not resident[key] then
				local e = table.remove(freeEntries)
				if not e then
					stats.poolShortage += 1
					continue
				end
				e.cx, e.cy = cx, cy
				e.dirty, e.drawn = true, false
				e.label.Position = UDim2.fromOffset(cx * CHUNK_PX, cy * CHUNK_PX)
				resident[key] = e
			end
		end
	end
end

local flashPending = false

local function processUploads(): number
	local centerX, centerY = camX + viewW / 2, camY + viewH / 2
	local queue = {}
	for _, e in entries do
		if e.dirty and e.cx then
			table.insert(queue, e)
		end
	end
	if #queue == 0 then
		return 0
	end
	local function dist(e: Entry): number
		local dx = (e.cx :: number + 0.5) * CHUNK_PX - centerX
		local dy = (e.cy :: number + 0.5) * CHUNK_PX - centerY
		return dx * dx + dy * dy
	end
	table.sort(queue, function(a, b)
		return dist(a) < dist(b)
	end)
	local limit = if flashPending then #queue else CONFIG.UPLOADS_PER_FRAME
	local count = math.min(limit, #queue)
	local t0 = os.clock()
	for i = 1, count do
		uploadChunk(queue[i])
	end
	if flashPending then
		flashPending = false
		flashResult = string.format("Flash: %d chunks uploaded in one frame, %.1f ms CPU", count, (os.clock() - t0) * 1000)
	end
	stats.maxUploadsInFrame = math.max(stats.maxUploadsInFrame, count)
	return count
end

local function setTile(x: number, y: number, f: number): boolean
	if not inWorld(x, y) then
		return false
	end
	local i = y * W + x
	if buffer.readu8(fg, i) == f then
		return false
	end
	buffer.writeu8(fg, i, f)
	local e = resident[(y // CHUNK) * CHUNKS_X + (x // CHUNK)]
	if e and e.drawn and not e.dirty then
		buffer.copy(tileScratch, 0, atlas, slotOf(i) * TILE_BYTES, TILE_BYTES)
		e.image:WritePixelsBuffer(Vector2.new((x % CHUNK) * TILE_ART, (y % CHUNK) * TILE_ART), TILE_SIZE, tileScratch)
		stats.tileWrites += 1
	end
	return true
end

--------------------------------------------------------------------------------
-- Lighting: one pixel per tile, black with alpha = darkness, stretched over the world.
-- GUI has no additive blending, so all light (including the player's) lives in this map.
--------------------------------------------------------------------------------

local LIGHT_W = math.ceil(viewW / TILE_PX) + 2 + CONFIG.LIGHT_PAD * 2
local LIGHT_H = math.ceil(viewH / TILE_PX) + 2 + CONFIG.LIGHT_PAD * 2
local AIR_DECAY, SOLID_DECAY = 0.88, 0.62

local lightImage, lightErr = createImage(Vector2.new(LIGHT_W, LIGHT_H))
local lightLabel: ImageLabel? = nil
if lightImage then
	lightLabel = imageLabel(lightImage, Vector2.new(LIGHT_W * TILE_PX, LIGHT_H * TILE_PX), 6)
	lightLabel.ResampleMode = Enum.ResamplerMode.Default -- smooth; the button switches to pixel
	memoryBytes += LIGHT_W * LIGHT_H * 4
else
	poolCreateError = poolCreateError or lightErr
end
local lightBuf = buffer.create(LIGHT_W * LIGHT_H * 4)
local L = table.create(LIGHT_W * LIGHT_H, 0)
local D = table.create(LIGHT_W * LIGHT_H, AIR_DECAY)
local lightEnabled = true
local lightSmooth = true
local PLAYER_LIGHT_RADIUS = 5

local function updateLight(lightX: number, lightY: number)
	if not lightImage or not lightLabel then
		return
	end
	local t0 = os.clock()
	local ox = camX // TILE_PX - 1 - CONFIG.LIGHT_PAD
	local oy = camY // TILE_PX - 1 - CONFIG.LIGHT_PAD

	for ly = 0, LIGHT_H - 1 do
		local y = oy + ly
		for lx = 0, LIGHT_W - 1 do
			local x = ox + lx
			local k = ly * LIGHT_W + lx + 1
			local v, d = 0, SOLID_DECAY
			if inWorld(x, y) then
				local i = y * W + x
				local f = buffer.readu8(fg, i)
				if f == TORCH or (f == AIR and buffer.readu8(wall, i) == NO_WALL) then
					v = 1
				end
				if not SOLID[f] then
					d = AIR_DECAY
				end
			elseif y < 0 then
				v, d = 1, AIR_DECAY
			end
			L[k], D[k] = v, d
		end
	end

	-- Seed the player light from the exact sub-tile position so it glides instead of
	-- jumping a whole tile at a time.
	local R = PLAYER_LIGHT_RADIUS
	for ty = math.floor(lightY) - R, math.floor(lightY) + R do
		for tx = math.floor(lightX) - R, math.floor(lightX) + R do
			local lx, ly = tx - ox, ty - oy
			if lx >= 0 and lx < LIGHT_W and ly >= 0 and ly < LIGHT_H then
				local dx, dy = tx + 0.5 - lightX, ty + 0.5 - lightY
				local v = 1 - math.sqrt(dx * dx + dy * dy) / (R + 1)
				local k = ly * LIGHT_W + lx + 1
				if v > L[k] then
					L[k] = v
				end
			end
		end
	end

	-- Two rounds of four directional sweeps: light(k) = max(light(k), neighbour * decay(k)).
	for _ = 1, 2 do
		for ly = 0, LIGHT_H - 1 do
			local row = ly * LIGHT_W + 1
			for lx = 1, LIGHT_W - 1 do
				local k = row + lx
				local c = L[k - 1] * D[k]
				if c > L[k] then
					L[k] = c
				end
			end
			for lx = LIGHT_W - 2, 0, -1 do
				local k = row + lx
				local c = L[k + 1] * D[k]
				if c > L[k] then
					L[k] = c
				end
			end
		end
		for lx = 1, LIGHT_W do
			for ly = 1, LIGHT_H - 1 do
				local k = ly * LIGHT_W + lx
				local c = L[k - LIGHT_W] * D[k]
				if c > L[k] then
					L[k] = c
				end
			end
			for ly = LIGHT_H - 2, 0, -1 do
				local k = ly * LIGHT_W + lx
				local c = L[k + LIGHT_W] * D[k]
				if c > L[k] then
					L[k] = c
				end
			end
		end
	end

	for k = 1, LIGHT_W * LIGHT_H do
		local o = (k - 1) * 4
		buffer.writeu32(lightBuf, o, 0)
		buffer.writeu8(lightBuf, o + 3, math.clamp(math.floor((1 - L[k]) * 255), 0, 255))
	end
	lightImage:WritePixelsBuffer(Vector2.zero, Vector2.new(LIGHT_W, LIGHT_H), lightBuf)
	lightLabel.Position = UDim2.fromOffset(ox * TILE_PX, oy * TILE_PX)

	stats.lightTime += os.clock() - t0
	stats.lightUpdates += 1
end

--------------------------------------------------------------------------------
-- Bodies: player and mobs share tile-grid AABB collision (positions in tiles).
--------------------------------------------------------------------------------

type Body = { x: number, y: number, w: number, h: number, vx: number, vy: number, grounded: boolean }

local function overlapsSolid(x: number, y: number, w: number, h: number): boolean
	for ty = math.floor(y), math.floor(y + h - EPS) do
		for tx = math.floor(x), math.floor(x + w - EPS) do
			if solidAt(tx, ty) then
				return true
			end
		end
	end
	return false
end

local function moveBody(b: Body, dt: number)
	b.vy = math.min(b.vy + GRAVITY * dt, MAX_FALL)

	local nx = b.x + b.vx * dt
	if overlapsSolid(nx, b.y, b.w, b.h) then
		if b.grounded and not overlapsSolid(nx, b.y - 1, b.w, b.h) then
			b.y -= 1 -- step up a one-tile ledge
		else
			nx = if b.vx > 0 then math.floor(nx + b.w) - b.w else math.floor(nx) + 1
			if overlapsSolid(nx, b.y, b.w, b.h) then
				nx = b.x
			end
			b.vx = 0
		end
	end
	b.x = nx

	local ny = b.y + b.vy * dt
	b.grounded = false
	if overlapsSolid(b.x, ny, b.w, b.h) then
		if b.vy > 0 then
			ny = math.floor(ny + b.h) - b.h
			b.grounded = true
		else
			ny = math.floor(ny) + 1
		end
		if overlapsSolid(b.x, ny, b.w, b.h) then
			ny = b.y
		end
		b.vy = 0
	end
	b.y = ny
end

local function surfaceSpawn(x: number, h: number): number
	local tx = math.clamp(math.floor(x), 0, W - 1)
	for y = 0, H - 1 do
		if solidAt(tx, y) then
			return y - h - 0.05
		end
	end
	return 0
end

--------------------------------------------------------------------------------
-- World setup
--------------------------------------------------------------------------------

local genStart = os.clock()
generateWorld(math.random(1, 100000))
local genMs = (os.clock() - genStart) * 1000

local hero: Body = { x = W / 2, y = 0, w = 1.25, h = 2.75, vx = 0, vy = 0, grounded = false }
hero.y = surfaceSpawn(hero.x, hero.h)
local heroFrame = Instance.new("Frame")
heroFrame.Size = UDim2.fromOffset(hero.w * TILE_PX, hero.h * TILE_PX)
heroFrame.BackgroundColor3 = Color3.fromRGB(240, 210, 90)
heroFrame.BorderSizePixel = 0
heroFrame.ZIndex = 4
heroFrame.Parent = worldFrame

-- All mobs share one 12x12 EditableImage to check that one image can feed many labels.
local mobImage = createImage(Vector2.new(12, 12))
if mobImage then
	local px = buffer.create(12 * 12 * 4)
	for y = 0, 11 do
		for x = 0, 11 do
			local dx, dy = x - 5.5, (y - 7) * 1.4
			if dx * dx + dy * dy < 36 and y >= 3 then
				local o = (y * 12 + x) * 4
				local eye = (y == 6 and (x == 4 or x == 8))
				buffer.writeu8(px, o, if eye then 20 else 80)
				buffer.writeu8(px, o + 1, if eye then 20 else 200)
				buffer.writeu8(px, o + 2, if eye then 20 else 90)
				buffer.writeu8(px, o + 3, 235)
			end
		end
	end
	mobImage:WritePixelsBuffer(Vector2.zero, Vector2.new(12, 12), px)
	memoryBytes += 12 * 12 * 4
end

type Mob = { body: Body, label: GuiObject, hopTimer: number }
local mobs: { Mob } = {}
for _ = 1, CONFIG.MOB_COUNT do
	local label: GuiObject
	if mobImage then
		label = imageLabel(mobImage, Vector2.new(1.5 * TILE_PX, 1.5 * TILE_PX), 3)
	else
		local f = Instance.new("Frame")
		f.Size = UDim2.fromOffset(1.5 * TILE_PX, 1.5 * TILE_PX)
		f.BackgroundColor3 = Color3.fromRGB(80, 200, 90)
		f.ZIndex = 3
		f.Parent = worldFrame
		label = f
	end
	label.Visible = false
	table.insert(mobs, {
		body = { x = 0, y = -1000, w = 1.5, h = 1.5, vx = 0, vy = 0, grounded = false },
		label = label,
		hopTimer = math.random(),
	})
end

type Particle = { frame: Frame, x: number, y: number, vx: number, vy: number, life: number }
local particles: { Particle } = {}
local nextParticle = 1
for _ = 1, CONFIG.MAX_PARTICLES do
	local f = Instance.new("Frame")
	f.Size = UDim2.fromOffset(TILE_PX / 2, TILE_PX / 2)
	f.BorderSizePixel = 0
	f.ZIndex = 5
	f.Visible = false
	f.Parent = worldFrame
	table.insert(particles, { frame = f, x = 0, y = 0, vx = 0, vy = 0, life = 0 })
end

local function burst(x: number, y: number, color: Color3)
	for _ = 1, 4 do
		local p = particles[nextParticle] -- oldest particle gets recycled when the pool is full
		nextParticle = nextParticle % #particles + 1
		p.x, p.y = x + math.random(), y + math.random()
		p.vx, p.vy = (math.random() - 0.5) * 12, -math.random() * 12
		p.life = 0.6
		p.frame.BackgroundColor3 = color
		p.frame.Visible = true
	end
end

local function dig(x: number, y: number)
	if not inWorld(x, y) then
		return
	end
	local f = getFg(x, y)
	if f ~= AIR and setTile(x, y, AIR) then
		burst(x, y, PARTICLE_COLOR[f])
	end
end

--------------------------------------------------------------------------------
-- HUD and buttons
--------------------------------------------------------------------------------

local hud = Instance.new("TextLabel")
hud.BackgroundColor3 = Color3.new(0, 0, 0)
hud.BackgroundTransparency = 0.4
hud.TextColor3 = Color3.new(1, 1, 1)
hud.Font = Enum.Font.Code
hud.TextSize = 14
hud.TextXAlignment = Enum.TextXAlignment.Left
hud.TextYAlignment = Enum.TextYAlignment.Top
hud.Position = UDim2.fromOffset(8, 8)
hud.Size = UDim2.fromOffset(560, 300)
hud.ZIndex = 20
hud.Parent = screenGui

local buttonY = 8
local function button(text: string, onClick: (TextButton) -> ()): TextButton
	local b = Instance.new("TextButton")
	b.Text = text
	b.Font = Enum.Font.GothamBold
	b.TextSize = 14
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	b.BackgroundTransparency = 0.15
	b.AnchorPoint = Vector2.new(1, 0)
	b.Position = UDim2.new(1, -8, 0, buttonY)
	b.Size = UDim2.fromOffset(210, 36)
	b.ZIndex = 20
	b.Parent = screenGui
	buttonY += 42
	b.Activated:Connect(function()
		onClick(b)
	end)
	return b
end

local touchOnly = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
local benchMode = touchOnly
local benchT = 0

button(if benchMode then "Bench: ON" else "Bench: OFF", function(b)
	benchMode = not benchMode
	b.Text = if benchMode then "Bench: ON" else "Bench: OFF"
end)

local uploadSteps = { 1, 2, 4, 8, 1000 }
local uploadIndex = table.find(uploadSteps, CONFIG.UPLOADS_PER_FRAME) or 3
CONFIG.UPLOADS_PER_FRAME = uploadSteps[uploadIndex]
local function uploadLabel(): string
	local n = CONFIG.UPLOADS_PER_FRAME
	return "Uploads/frame: " .. (if n >= 1000 then "unlimited" else tostring(n))
end
button(uploadLabel(), function(b)
	uploadIndex = uploadIndex % #uploadSteps + 1
	CONFIG.UPLOADS_PER_FRAME = uploadSteps[uploadIndex]
	b.Text = uploadLabel()
end)

button("Flash all chunks", function()
	atlas = if atlas == atlasNormal then atlasFlash else atlasNormal
	for _, e in entries do
		if e.cx then
			e.dirty = true
		end
	end
	flashPending = true
end)

button("Lighting: ON", function(b)
	lightEnabled = not lightEnabled
	b.Text = if lightEnabled then "Lighting: ON" else "Lighting: OFF"
	if lightLabel then
		lightLabel.Visible = lightEnabled
	end
end)

local lightSteps = { 10, 20, 30, 60 }
local lightIndex = table.find(lightSteps, CONFIG.LIGHT_HZ) or 3
CONFIG.LIGHT_HZ = lightSteps[lightIndex]
button("Light rate: " .. CONFIG.LIGHT_HZ .. "/s", function(b)
	lightIndex = lightIndex % #lightSteps + 1
	CONFIG.LIGHT_HZ = lightSteps[lightIndex]
	b.Text = "Light rate: " .. CONFIG.LIGHT_HZ .. "/s"
end)

button("Light look: smooth", function(b)
	lightSmooth = not lightSmooth
	b.Text = if lightSmooth then "Light look: smooth" else "Light look: pixel"
	if lightLabel then
		lightLabel.ResampleMode = if lightSmooth then Enum.ResamplerMode.Default else Enum.ResamplerMode.Pixelated
	end
end)

-- Runs once per session. Hitting the limit is the point, so the engine prints one
-- "Failed to create empty EditableImage ... memory budget limits" warning. That is expected.
local probeUsed = false
button("Probe memory budget", function(b)
	if probeUsed then
		return
	end
	probeUsed = true
	b.Text = "Probe: running..."
	probeResult = "Probe: running..."
	task.defer(function()
		local extra = {}
		local err: string? = nil
		for _ = 1, 400 do -- caps the probe at 100 MB
			local image, e = createImage(CHUNK_SIZE)
			if not image then
				err = e
				break
			end
			table.insert(extra, image)
		end
		local n = #extra
		for _, image in extra do
			image:Destroy()
		end
		probeResult = string.format(
			"Probe: %d more 256x256 images (%.1f MB) fit; total ~%.1f MB. %s",
			n,
			n * CHUNK_BYTES / 1048576,
			(memoryBytes + n * CHUNK_BYTES) / 1048576,
			if err then "Stopped by: " .. string.sub(err, 1, 80) else "No failure up to the 100 MB cap."
		)
		print("TerrainBench " .. probeResult)
		b.Text = string.format("Budget ~%.0f MB (done)", (memoryBytes + n * CHUNK_BYTES) / 1048576)
	end)
end)

--------------------------------------------------------------------------------
-- Input
--------------------------------------------------------------------------------

-- Touch positions exclude the top bar inset; this GUI ignores the inset, so add it back.
local guiInset = game:GetService("GuiService"):GetGuiInset()
local touchPos: Vector2? = nil
UserInputService.InputBegan:Connect(function(input, processed)
	if processed then
		return
	end
	if input.UserInputType == Enum.UserInputType.Touch then
		touchPos = Vector2.new(input.Position.X, input.Position.Y) + guiInset
	elseif input.KeyCode == Enum.KeyCode.T then
		local m = UserInputService:GetMouseLocation()
		setTile((m.X + camX) // TILE_PX, (m.Y + camY) // TILE_PX, TORCH)
	end
end)
UserInputService.InputChanged:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.Touch and touchPos then
		touchPos = Vector2.new(input.Position.X, input.Position.Y) + guiInset
	end
end)
UserInputService.InputEnded:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.Touch then
		touchPos = nil
	end
end)

local editTimer = 0

local function handleManualInput(dt: number)
	local move = 0
	if UserInputService:IsKeyDown(Enum.KeyCode.A) or UserInputService:IsKeyDown(Enum.KeyCode.Left) then
		move -= 1
	end
	if UserInputService:IsKeyDown(Enum.KeyCode.D) or UserInputService:IsKeyDown(Enum.KeyCode.Right) then
		move += 1
	end
	hero.vx = move * 12
	if hero.grounded and (UserInputService:IsKeyDown(Enum.KeyCode.Space) or UserInputService:IsKeyDown(Enum.KeyCode.W)) then
		hero.vy = -24
	end

	editTimer -= dt
	if editTimer > 0 then
		return
	end
	local m = UserInputService:GetMouseLocation()
	local digging = UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton1)
	local placing = UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton2)
	if touchPos then
		m, digging = touchPos, true
	end
	if digging or placing then
		editTimer = 0.05
		local tx, ty = (m.X + camX) // TILE_PX, (m.Y + camY) // TILE_PX
		for oy = -1, 1 do
			for ox = -1, 1 do
				if digging then
					dig(tx + ox, ty + oy)
				elseif inWorld(tx + ox, ty + oy) and getFg(tx + ox, ty + oy) == AIR then
					setTile(tx + ox, ty + oy, DIRT)
				end
			end
		end
	end
end

local benchEditAcc = 0
local function runBench(dt: number): (number, number)
	benchT += dt
	local span = W * 0.42
	local x = W / 2 + span * math.sin(benchT * CONFIG.BENCH_SPEED / span)
	local surface = surfaceY[math.clamp(math.floor(x), 0, W - 1) + 1]
	local y = surface + 30 + 45 * math.sin(benchT * 0.35) -- swings between sky and caves

	benchEditAcc += CONFIG.BENCH_EDITS * dt
	local viewTilesW, viewTilesH = viewW // TILE_PX, viewH // TILE_PX
	while benchEditAcc >= 1 do
		benchEditAcc -= 1
		local tx = math.floor(x) + math.random(-viewTilesW // 2, viewTilesW // 2)
		local ty = math.floor(y) + math.random(-viewTilesH // 2, viewTilesH // 2)
		local r = math.random()
		if r < 0.6 then
			dig(tx, ty)
		elseif r < 0.95 then
			if inWorld(tx, ty) and getFg(tx, ty) == AIR then
				setTile(tx, ty, STONE)
			end
		elseif inWorld(tx, ty) and getFg(tx, ty) == AIR then
			setTile(tx, ty, TORCH)
		end
	end
	return x, y
end

--------------------------------------------------------------------------------
-- Main loop
--------------------------------------------------------------------------------

local lightTimer = 0
local statTimer = 0
local MAX_X = W * TILE_PX - viewW
local MAX_Y = H * TILE_PX - viewH

RunService.RenderStepped:Connect(function(rawDt)
	local dt = math.min(rawDt, 1 / 30)
	stats.frames += 1
	stats.worstDt = math.max(stats.worstDt, rawDt)

	local focusX, focusY
	if benchMode then
		focusX, focusY = runBench(dt)
	else
		handleManualInput(dt)
		moveBody(hero, dt)
		focusX, focusY = hero.x + hero.w / 2, hero.y + hero.h / 2
	end

	-- whole-pixel camera so pixel art never lands between screen pixels
	camX = math.clamp(math.floor(focusX * TILE_PX - viewW / 2), 0, MAX_X)
	camY = math.clamp(math.floor(focusY * TILE_PX - viewH / 2), 0, MAX_Y)
	worldFrame.Position = UDim2.fromOffset(-camX, -camY)
	heroFrame.Visible = not benchMode
	heroFrame.Position = UDim2.fromOffset(math.floor(hero.x * TILE_PX), math.floor(hero.y * TILE_PX))

	updateResidency()
	local uploaded = processUploads()

	lightTimer += rawDt
	if lightEnabled and lightTimer >= 1 / CONFIG.LIGHT_HZ then
		if not (CONFIG.LIGHT_SKIPS_CHUNK_FRAME and uploaded > 0) then
			lightTimer = 0
			updateLight(focusX, focusY)
		end
	end

	-- mobs: simulate all, draw only those on screen, respawn the ones left far behind
	local viewTilesW = viewW / TILE_PX
	local camTx, camTy = camX / TILE_PX, camY / TILE_PX
	for _, mob in mobs do
		local b = mob.body
		if math.abs(b.x - focusX) > viewTilesW then
			b.x = focusX + (math.random() - 0.5) * viewTilesW
			b.y = surfaceSpawn(b.x, b.h)
			b.vx, b.vy = 0, 0
		end
		mob.hopTimer -= dt
		if b.grounded and mob.hopTimer <= 0 then
			mob.hopTimer = 0.8 + math.random() * 1.5
			b.vy = -18
			b.vx = (math.random() - 0.5) * 16
		elseif b.grounded then
			b.vx = 0
		end
		moveBody(b, dt)
		local onScreen = b.x + b.w > camTx and b.x < camTx + viewTilesW and b.y + b.h > camTy and b.y < camTy + viewH / TILE_PX
		mob.label.Visible = onScreen
		if onScreen then
			mob.label.Position = UDim2.fromOffset(math.floor(b.x * TILE_PX), math.floor(b.y * TILE_PX))
		end
	end

	for _, p in particles do
		if p.life > 0 then
			p.life -= dt
			if p.life <= 0 then
				p.frame.Visible = false
			else
				p.vy += GRAVITY * dt
				p.x += p.vx * dt
				p.y += p.vy * dt
				p.frame.Position = UDim2.fromOffset(math.floor(p.x * TILE_PX), math.floor(p.y * TILE_PX))
			end
		end
	end

	statTimer += rawDt
	if statTimer >= 1 then
		local s = stats
		local used = #entries - #freeEntries
		hud.Text = table.concat({
			string.format("FPS %d   worst frame %.1f ms   world gen %.0f ms", math.floor(s.frames / statTimer), s.worstDt * 1000, genMs),
			string.format("View %dx%d   chunk pool %d/%d   pool shortages %d", viewW, viewH, used, #entries, s.poolShortage),
			string.format("EditableImage memory ~%.2f MB (budget reported ~32 MB)   tiles: %s", memoryBytes / 1048576, tileSource),
			string.format(
				"Chunk uploads %d/s   build %.2f ms   WritePixelsBuffer %.2f ms (avg CPU)",
				s.chunkUploads,
				if s.chunkUploads > 0 then s.chunkBuildTime / s.chunkUploads * 1000 else 0,
				if s.chunkUploads > 0 then s.chunkUploadTime / s.chunkUploads * 1000 else 0
			),
			string.format("Most chunk uploads in one frame %d   tile writes %d/s", s.maxUploadsInFrame, s.tileWrites),
			string.format(
				"Light %dx%d   %d updates/s   %.2f ms avg",
				LIGHT_W,
				LIGHT_H,
				s.lightUpdates,
				if s.lightUpdates > 0 then s.lightTime / s.lightUpdates * 1000 else 0
			),
			if poolCreateError then "CREATE FAILED: " .. string.sub(poolCreateError, 1, 90) else "All images created OK",
			flashResult,
			probeResult,
		}, "\n")
		for k in s do
			s[k] = 0
		end
		statTimer = 0
	end
end)
