-- Evil Sofia: defines for a city-sized map. Only keys the game already has are changed.
local function set(tbl, ns, key, value)
	if tbl ~= nil and tbl[ns] ~= nil and tbl[ns][key] ~= nil then
		tbl[ns][key] = value
	end
end
-- One map pixel is about 47 m in reality; 1.5 km per pixel keeps unit movement close to vanilla pacing.
set(NDefines, "NGame", "MAP_SCALE_PIXEL_TO_KM", 1.5)
-- The main menu camera looks at the city.
for _, tbl in ipairs({NDefines, NDefines_Graphics}) do
	set(tbl, "NFrontend", "CAMERA_LOOKAT_X", 2815.5)
	set(tbl, "NFrontend", "CAMERA_LOOKAT_Z", 1024.0)
	set(tbl, "NFrontend", "CAMERA_START_X", 2815.5)
	set(tbl, "NFrontend", "CAMERA_START_Z", 904.0)
	set(tbl, "NFrontend", "CAMERA_END_X", 2815.5)
	set(tbl, "NFrontend", "CAMERA_END_Z", 904.0)
end
