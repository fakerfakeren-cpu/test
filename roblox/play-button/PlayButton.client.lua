--[[
	PLAY button - pixel-art main menu button (9-slice ImageButton + live text).

	Where: StarterPlayer > StarterPlayerScripts > LocalScript (name it "PlayButton").
	Builds:  PlayerGui.PlayMenu (ScreenGui) > PlayButton (ImageButton) > Content > icon + "PLAY"

	Paste your uploaded asset IDs into CONFIG, then edit onPlay() below it.
]]

local CONFIG = {
	-- Asset IDs (numbers, or full "rbxassetid://..." strings). 0 = not set.
	IMAGE_NORMAL = 0, -- play_normal.png
	IMAGE_HOVER = 0, -- play_hover.png
	IMAGE_PRESSED = 0, -- play_pressed.png
	IMAGE_ICON = 0, -- play_icon.png
	CLICK_SOUND = 0, -- any sound ID; 0 = no sound
	CLICK_VOLUME = 0.6,

	TEXT = "PLAY",
	FONT = Enum.Font.Arcade, -- Roblox's built-in pixel font, closest to the art
	SHOW_ICON = true,
	-- Baked-text option (pixel-perfect letters): put the *_text.png IDs above,
	-- set TEXT = "" and SHOW_ICON = false, and keep WIDTH = 64.

	-- Size. One pixel of the art is drawn as PIXEL_SCALE screen pixels; whole
	-- numbers keep every art pixel the same size (crisp).
	PIXEL_SCALE = nil, -- nil = automatic, or a whole number (4 = 256 x 96)
	HEIGHT_FRACTION = 0.25, -- automatic: button height is about this share of the screen
	MIN_SCALE = 2,
	MAX_SCALE = 5,
	WIDTH = 64, -- in art pixels; 9-slice lets it go wider (e.g. 80) without stretching the border
	BOTTOM_MARGIN = 4, -- art pixels between the button and the bottom of the safe area
	TEXT_NUDGE_Y = 0, -- art pixels (decimals OK) if the font sits a little high or low

	-- Gamepad: SHORTCUT presses PLAY from anywhere while the menu is visible.
	-- AUTO_SELECT highlights the button for the D-pad/A button, but while it is
	-- selected the thumbstick drives the UI instead of the character, so only
	-- turn it on if your menu has no character movement.
	GAMEPAD_SHORTCUT = Enum.KeyCode.ButtonY, -- nil = no shortcut
	GAMEPAD_AUTO_SELECT = false,

	GAMEMODES_GUI = "GamemodesGui", -- ScreenGui in PlayerGui that onPlay() opens, if it exists
}

-- Runs on click, tap, A on the selected button, or the gamepad shortcut.
-- Default: hide this menu and open your gamemode screen if there is one.
-- To come back, have your gamemode screen's back button set
-- PlayerGui.PlayMenu.Enabled = true.
local function onPlay(menu: ScreenGui)
	menu.Enabled = false
	local modes = menu.Parent:FindFirstChild(CONFIG.GAMEMODES_GUI)
	if modes and modes:IsA("ScreenGui") then
		modes.Enabled = true
	end
end

-----------------------------------------------------------------------------
-- Art geometry (matches the exported PNGs; no need to touch)

local ART_H = 24 -- art pixels, shadow included
local EXPORT_SCALE = 8 -- PNGs are 8x the art (512 x 192)
local SLICE_CENTER = Rect.new(40, 56, 472, 136)
local TEXT_TOP = 6 -- top row of the letters
local GLYPH_H = 7
local ICON_W = 6
local ICON_GAP = 6
local PRESS_DROP = 2 -- pressed face sits 2 art pixels lower

local WHITE = Color3.fromRGB(255, 255, 255)
local OUTLINE = Color3.fromHex("1B1F2A")
local TEXT_SHADOW = Color3.fromHex("2E9A22")
local TEXT_SHADOW_PRESSED = Color3.fromHex("28881E")

local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local SoundService = game:GetService("SoundService")
local ContentProvider = game:GetService("ContentProvider")

local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")

local function asset(id): string
	if id == nil or id == 0 or id == "" then
		return ""
	end
	id = tostring(id)
	return if id:find("^rbxassetid://") then id else "rbxassetid://" .. id
end

local IMAGES = { normal = asset(CONFIG.IMAGE_NORMAL) }
IMAGES.hover = if asset(CONFIG.IMAGE_HOVER) ~= "" then asset(CONFIG.IMAGE_HOVER) else IMAGES.normal
IMAGES.pressed = if asset(CONFIG.IMAGE_PRESSED) ~= "" then asset(CONFIG.IMAGE_PRESSED) else IMAGES.normal
local ICON_IMAGE = asset(CONFIG.IMAGE_ICON)
if IMAGES.normal == "" then
	warn("[PlayButton] Paste your image IDs into CONFIG at the top of the script.")
end

-----------------------------------------------------------------------------
-- Build

local gui = Instance.new("ScreenGui")
gui.Name = "PlayMenu"
gui.ResetOnSpawn = false
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets -- clear of notches and the home bar

local button = Instance.new("ImageButton")
button.Name = "PlayButton"
button.AnchorPoint = Vector2.new(0.5, 0.5) -- bounce scales around the centre
button.BackgroundTransparency = 1
button.AutoButtonColor = false
button.Image = IMAGES.normal
button.ScaleType = Enum.ScaleType.Slice
button.SliceCenter = SLICE_CENTER
button.ResampleMode = Enum.ResamplerMode.Pixelated
button.Selectable = true
button.Parent = gui

-- No default selection box: the hover look marks gamepad selection instead.
local noSelectionBox = Instance.new("Frame")
noSelectionBox.BackgroundTransparency = 1
button.SelectionImageObject = noSelectionBox

local bounce = Instance.new("UIScale")
bounce.Parent = button

-- Icon + text as one group, centred on the face.
local content = Instance.new("Frame")
content.Name = "Content"
content.AnchorPoint = Vector2.new(0.5, 0)
content.BackgroundTransparency = 1
content.AutomaticSize = Enum.AutomaticSize.X
content.Parent = button

local list = Instance.new("UIListLayout")
list.FillDirection = Enum.FillDirection.Horizontal
list.VerticalAlignment = Enum.VerticalAlignment.Top
list.SortOrder = Enum.SortOrder.LayoutOrder
list.Parent = content

-- Slot is the triangle's own size; the image (outline + shadow baked in)
-- hangs 2 art pixels over its edges, like the letters' UIStroke does.
local iconSlot = Instance.new("Frame")
iconSlot.Name = "IconSlot"
iconSlot.BackgroundTransparency = 1
iconSlot.LayoutOrder = 1
iconSlot.Visible = CONFIG.SHOW_ICON and ICON_IMAGE ~= ""
iconSlot.Parent = content

local icon = Instance.new("ImageLabel")
icon.Name = "Icon"
icon.BackgroundTransparency = 1
icon.Image = ICON_IMAGE
icon.ResampleMode = Enum.ResamplerMode.Pixelated
icon.Parent = iconSlot

local textSlot = Instance.new("Frame")
textSlot.Name = "TextSlot"
textSlot.BackgroundTransparency = 1
textSlot.AutomaticSize = Enum.AutomaticSize.X
textSlot.LayoutOrder = 2
textSlot.Parent = content

local function makeText(name: string, textColor: Color3, strokeColor: Color3, z: number)
	local label = Instance.new("TextLabel")
	label.Name = name
	label.BackgroundTransparency = 1
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Font = CONFIG.FONT
	label.Text = CONFIG.TEXT
	label.TextColor3 = textColor
	label.ZIndex = z
	label.Parent = textSlot
	local stroke = Instance.new("UIStroke")
	stroke.Color = strokeColor
	stroke.LineJoinMode = Enum.LineJoinMode.Miter -- square corners, closest to pixel art
	stroke.Parent = label
	return label, stroke
end

-- The shadow is a copy one art pixel lower, behind the label; only its
-- bottom pixel row shows below the navy outline.
local label, labelStroke = makeText("Label", WHITE, OUTLINE, 3)
local shadow, shadowStroke = makeText("LabelShadow", TEXT_SHADOW, TEXT_SHADOW, 2)

local clickSound: Sound? = nil
if asset(CONFIG.CLICK_SOUND) ~= "" then
	clickSound = Instance.new("Sound")
	clickSound.Name = "Click"
	clickSound.SoundId = asset(CONFIG.CLICK_SOUND)
	clickSound.Volume = CONFIG.CLICK_VOLUME
	clickSound.Parent = gui
end

-----------------------------------------------------------------------------
-- State + layout

local S = 4 -- screen pixels per art pixel, set by layout()
local mouseOver, selected, held = false, false, false

local function refresh()
	local hovered = mouseOver or selected
	button.Image = if held then IMAGES.pressed elseif hovered then IMAGES.hover else IMAGES.normal
	local drop = if held then PRESS_DROP else 0
	content.Position = UDim2.new(0.5, 0, 0, math.floor((TEXT_TOP + drop + CONFIG.TEXT_NUDGE_Y) * S + 0.5))
	local shadowColor = if held then TEXT_SHADOW_PRESSED else TEXT_SHADOW
	shadow.TextColor3 = shadowColor
	shadowStroke.Color = shadowColor
end

local function pixelScale(): number
	if CONFIG.PIXEL_SCALE then
		return CONFIG.PIXEL_SCALE
	end
	local h = gui.AbsoluteSize.Y
	if h <= 0 then
		h = workspace.CurrentCamera.ViewportSize.Y
	end
	return math.clamp(math.floor(h * CONFIG.HEIGHT_FRACTION / ART_H + 0.5), CONFIG.MIN_SCALE, CONFIG.MAX_SCALE)
end

local function layout()
	S = pixelScale()
	button.Size = UDim2.fromOffset(CONFIG.WIDTH * S, ART_H * S)
	button.Position = UDim2.new(0.5, 0, 1, -(CONFIG.BOTTOM_MARGIN + ART_H / 2) * S)
	button.SliceScale = S / EXPORT_SCALE -- borders stay exactly 5 / 7 art pixels at any size
	content.Size = UDim2.fromOffset(0, GLYPH_H * S)
	list.Padding = UDim.new(0, ICON_GAP * S)
	iconSlot.Size = UDim2.fromOffset(ICON_W * S, GLYPH_H * S)
	icon.Size = UDim2.fromOffset((ICON_W + 4) * S, (GLYPH_H + 5) * S)
	icon.Position = UDim2.fromOffset(-2 * S, -2 * S)
	textSlot.Size = UDim2.fromOffset(0, GLYPH_H * S)
	for _, l in { label, shadow } do
		l.Size = UDim2.fromScale(0, 1)
		l.TextSize = 8 * S -- Arcade is drawn on an 8-unit grid
	end
	shadow.Position = UDim2.fromOffset(0, S)
	labelStroke.Thickness = 2 * S
	shadowStroke.Thickness = 2 * S
	refresh()
end

-- Hover bounce: up and back to exactly 1, so the resting button stays pixel-perfect.
local UP = TweenInfo.new(0.07, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local DOWN = TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local activeTween: Tween? = nil

local function tweenScale(target: number, info: TweenInfo, onDone: (() -> ())?)
	if activeTween then
		activeTween:Cancel()
	end
	local t = TweenService:Create(bounce, info, { Scale = target })
	activeTween = t
	if onDone then
		t.Completed:Once(function(state)
			if state == Enum.PlaybackState.Completed then
				onDone()
			end
		end)
	end
	t:Play()
end

local function stopBounce()
	if activeTween then
		activeTween:Cancel()
		activeTween = nil
	end
	bounce.Scale = 1
end

local function setHover(isMouse: boolean, on: boolean)
	local before = mouseOver or selected
	if isMouse then
		mouseOver = on
	else
		selected = on
	end
	if not before and (mouseOver or selected) and not held then
		tweenScale(1.06, UP, function()
			tweenScale(1, DOWN)
		end)
	end
	refresh()
end

local function setHeld(on: boolean)
	if held == on then
		return
	end
	held = on
	if on then
		stopBounce()
	end
	refresh()
end

local function activate()
	if not gui.Enabled then
		return
	end
	if clickSound then
		SoundService:PlayLocalSound(clickSound)
	end
	mouseOver, held = false, false
	stopBounce()
	refresh()
	onPlay(gui)
end

-----------------------------------------------------------------------------
-- Input: mouse, touch, gamepad

local function lastInputIsTouch(): boolean
	return UserInputService:GetLastInputType() == Enum.UserInputType.Touch
end

local function usingGamepad(): boolean
	return UserInputService:GetLastInputType().Name:find("^Gamepad") ~= nil
end

local PRESS = {
	[Enum.UserInputType.MouseButton1] = true,
	[Enum.UserInputType.Touch] = true,
}

-- Touch has no hover; Roblox still fires MouseEnter on a tap, so skip it.
button.MouseEnter:Connect(function()
	if not lastInputIsTouch() then
		setHover(true, true)
	end
end)
button.MouseLeave:Connect(function()
	setHeld(false) -- dragging off cancels the press, same as Roblox's click
	setHover(true, false)
end)
button.SelectionGained:Connect(function()
	setHover(false, true)
end)
button.SelectionLost:Connect(function()
	setHeld(false)
	setHover(false, false)
end)

button.InputBegan:Connect(function(input)
	if PRESS[input.UserInputType] then
		setHeld(true)
	end
end)

-- Fires for mouse click, touch tap and A on the selected button.
button.Activated:Connect(activate)

local shortcutDown = false
UserInputService.InputBegan:Connect(function(input, processed)
	if not gui.Enabled then
		return
	end
	if input.KeyCode == Enum.KeyCode.ButtonA and GuiService.SelectedObject == button then
		setHeld(true)
	elseif CONFIG.GAMEPAD_SHORTCUT and input.KeyCode == CONFIG.GAMEPAD_SHORTCUT and not processed then
		shortcutDown = true
		setHeld(true)
	end
end)

UserInputService.InputEnded:Connect(function(input)
	if CONFIG.GAMEPAD_SHORTCUT and input.KeyCode == CONFIG.GAMEPAD_SHORTCUT and shortcutDown then
		shortcutDown = false
		if held then
			activate()
		end
	elseif PRESS[input.UserInputType] or input.KeyCode == Enum.KeyCode.ButtonA then
		setHeld(false)
	end
end)

local function autoSelect()
	if CONFIG.GAMEPAD_AUTO_SELECT and gui.Enabled and usingGamepad() and GuiService.SelectedObject == nil then
		GuiService.SelectedObject = button
	end
end
UserInputService.LastInputTypeChanged:Connect(autoSelect)

gui:GetPropertyChangedSignal("Enabled"):Connect(function()
	mouseOver, held, shortcutDown = false, false, false
	stopBounce()
	if not gui.Enabled and GuiService.SelectedObject == button then
		GuiService.SelectedObject = nil
	end
	refresh()
	autoSelect()
end)

gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(layout)
gui.Parent = playerGui
layout()
autoSelect()

-- Load the hover/pressed images and the click now, so the first hover doesn't flash.
task.spawn(function()
	local preload: { any } = {}
	for _, id in { IMAGES.normal, IMAGES.hover, IMAGES.pressed, ICON_IMAGE } do
		if id ~= "" then
			table.insert(preload, id)
		end
	end
	if clickSound then
		table.insert(preload, clickSound)
	end
	ContentProvider:PreloadAsync(preload)
end)
