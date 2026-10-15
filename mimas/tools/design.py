"""The Mimas build, block by block. See model.py for the coordinate system."""
from model import Model, VOLUME

# ---- palette -------------------------------------------------------------------------------
PLASTER = "smooth_sandstone"        # cream plaster of the residential floors
TRIM = "smooth_quartz"
TILE = "quartz_bricks"              # white tiled shop walls
FRAME = "polished_deepslate"        # dark aluminium shop-front frame
SIGN_BG = "red_concrete"
SIGN_FRAME = "polished_blackstone"
LETTER = "ochre_froglight"          # lit letters
ROOF = "brick_stairs"
ASPHALT = "gray_concrete"

# Hanging-sign menu (Bulgarian, EUR). Prices: Wolt/Takeaway listings for Mimas, bul. Vasil Levski 68 (2026) -
# approximate, see README.
MENU = [
    ("ПИЛЕШКИ", "ДЮНЕР", "среден", "5,50 €"),
    ("ПИЛЕШКИ", "ДЮНЕР", "XL", "8,60 €"),
    ("ТЕЛЕШКИ", "ДЮНЕР", "среден", "7,44 €"),
    ("ШИШ ТАУК", "сандвич", "двоен", "7,41 €"),
    ("ФАЛАФЕЛ", "сандвич", "среден", "3,83 €"),
    ("ФАЛАФЕЛ", "сандвич", "голям", "4,35 €"),
    ("ФАЛАФЕЛ", "порция", "10 бр.", "5,62 €"),
    ("МИМАС", "МЕНЮ", "+ картофи", "10,73 €"),
]

# 5-row block font for the sign band: М И М А С (Cyrillic).
GLYPHS = {
    "М": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"],
    "И": ["X..X", "X..X", "X.XX", "XX.X", "X..X"],
    "А": [".X.", "X.X", "XXX", "X.X", "X.X"],
    "С": [".XX", "X..", "X..", "X..", ".XX"],
}
SIGN_WORD = "МИМАС"


def snbt_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def sign_nbt(lines, color="yellow", glow=True, back=None):
    msgs = ",".join(snbt_str(l) for l in lines)
    back_lines = back or ["", "", "", ""]
    bmsgs = ",".join(snbt_str(l) for l in back_lines)
    return ("{front_text:{color:\"%s\",has_glowing_text:%s,messages:[%s]},"
            "back_text:{color:\"%s\",has_glowing_text:%s,messages:[%s]},is_waxed:1b}"
            % (color, "1b" if glow else "0b", msgs, color, "1b" if glow else "0b", bmsgs))


def build():
    m = Model()
    ground(m)
    street(m)
    shop_shell(m)
    shop_front(m)
    interior(m)
    residential_bay(m)
    upper_floors(m)
    sign_band(m)
    roof(m)
    return m


# ---- ground --------------------------------------------------------------------------------
def ground(m):
    (x0, y0, z0), (x1, _, z1) = VOLUME
    m.fill(x0, -2, z0, x1, -1, z1, "stone")
    # sidewalk tiles (2x2 grey pavers)
    for x in range(x0, x1 + 1):
        for z in list(range(11, 15)) + [24, 25]:
            m.set(x, 0, z, "smooth_stone" if ((x // 2) + (z // 2)) % 2 == 0 else "polished_andesite")
    # curbs (low half-block edge)
    for z in (15, 23):
        m.fill(x0, 0, z, x1, 0, z, "polished_andesite")
        m.fill(x0, 1, z, x1, 1, z, "smooth_stone_slab", type="bottom")
    # road + tram tracks
    m.fill(x0, 0, 16, x1, 0, 22, ASPHALT)
    for z in (18, 20):
        m.fill(x0, 0, z, x1, 0, z, "polished_andesite")
    # zebra crossing (stripes run with the traffic, repeat across the road)
    for z in range(16, 23):
        if z % 2 == 1 and z not in (18, 20):
            m.fill(21, 0, z, 24, 0, z, "white_concrete")
    # building footprint floor
    m.fill(0, 0, 0, 25, 0, 10, "smooth_stone")


def street(m):
    (x0, _, _), (x1, _, _) = VOLUME
    # tram rails
    for z in (18, 20):
        m.fill(x0, 1, z, x1, 1, z, "rail", shape="east_west")
    # catenary poles with a street lamp on top (near + far side), placed in the gap between И and М
    # of the sign so they don't hide the lettering from the street
    for zp in (14, 24):
        m.fill(11, 1, zp, 11, 6, zp, "polished_blackstone_wall")
        m.set(11, 7, zp, "lantern", hanging=False)
    m.fill(11, 6, 15, 11, 6, 23, "iron_chain", axis="z")      # cross-span wire
    for z in (18, 20):
        m.fill(x0, 5, z, x1, 5, z, "iron_chain", axis="x")    # contact wires over the tracks
    # bollards ("колчета") along the curb
    for x in (1, 4, 10, 13, 19, 22, 25):
        m.set(x, 1, 14, "polished_blackstone_wall")
    # street bin
    m.set(16, 1, 14, "cauldron")
    # two standing tables
    for x in (9, 12):
        m.set(x, 1, 12, "polished_blackstone_wall")
        m.set(x, 2, 12, "heavy_weighted_pressure_plate", power=0)
    # two street trees on the far sidewalk
    for tx in (2, 23):                       # young lindens: canopy stays below the sign band
        m.fill(tx, 1, 25, tx, 3, 25, "oak_log", axis="y")
        for y, r in ((3, 2), (4, 1)):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) == r and abs(dz) == r and r > 1:
                        continue
                    x, z = tx + dx, 25 + dz
                    if 0 <= x <= 25 and z <= 25 and m.id_at(x, y, z) == "air":
                        m.set(x, y, z, "oak_leaves", persistent=True, distance=1)


# ---- shop shell ----------------------------------------------------------------------------
def shop_shell(m):
    # side + back walls of the ground floor (x 0..20 shop, z 0..10)
    m.fill(0, 0, 0, 0, 5, 10, TILE)
    m.fill(20, 0, 0, 20, 5, 10, TILE)
    m.fill(0, 0, 0, 20, 5, 0, TILE)
    # ceiling over the whole ground floor
    m.fill(0, 6, 0, 25, 6, 10, TRIM)
    # floors
    for x in range(1, 20):
        for z in range(1, 10):
            if customer_cell(x, z):
                m.set(x, 0, z, "polished_diorite" if (x + z) % 2 == 0 else "polished_andesite")
            else:
                m.set(x, 0, z, "smooth_stone")
    # ceiling lights
    for x in (3, 6, 9, 12, 15, 18):
        for z in (2, 5, 8):
            m.set(x, 6, z, "pearlescent_froglight", axis="y")


def customer_cell(x, z):
    return (1 <= x <= 4 and 4 <= z <= 9) or (5 <= x <= 13 and 6 <= z <= 9)


def shop_front(m):
    z = 10
    for x in (0, 14, 20):                      # piers
        m.fill(x, 0, z, x, 5, z, FRAME)
    m.fill(0, 5, z, 20, 5, z, FRAME)           # head beam
    for x in list(range(1, 3)) + list(range(5, 14)) + [19]:
        m.fill(x, 1, z, x, 4, z, "glass_pane")
    # double entrance door (iron, opens automatically via pressure plates on both sides)
    for x, hinge in ((3, "left"), (4, "right")):
        m.set(x, 1, z, "iron_door", facing="north", half="lower", hinge=hinge, open=False, powered=False)
        m.set(x, 2, z, "iron_door", facing="north", half="upper", hinge=hinge, open=False, powered=False)
        m.fill(x, 3, z, x, 4, z, "glass_pane")
        m.set(x, 1, 9, "polished_blackstone_pressure_plate", powered=False)
        m.set(x, 1, 11, "polished_blackstone_pressure_plate", powered=False)
    # street-facing takeaway window: wall below, open hatch, glass above
    for x in range(15, 19):
        m.set(x, 1, z, FRAME)
        m.fill(x, 3, z, x, 4, z, "glass_pane")
        m.set(x, 1, 11, "smooth_quartz_slab", type="top")        # outside ledge
    # striped awning over the takeaway window
    for x in range(14, 20):
        for zz in (11, 12):
            m.set(x, 4, zz, "red_wool" if x % 2 == 0 else "white_wool")


def interior(m):
    # partition between service area and back kitchen (z=3) + end wall of the cooking line (x=5)
    m.fill(1, 1, 3, 19, 5, 3, TILE)
    m.fill(5, 1, 4, 5, 5, 5, TILE)
    # glowing grill panels behind the two vertical spits
    for x in (7, 9):
        m.fill(x, 1, 3, x, 3, 3, "magma_block")
    # staff door into the back kitchen
    m.set(16, 1, 3, "dark_oak_door", facing="south", half="lower", hinge="left", open=False, powered=False)
    m.set(16, 2, 3, "dark_oak_door", facing="south", half="upper", hinge="left", open=False, powered=False)

    # --- cooking line along the partition (z=4) ---
    line = {6: "iron_block", 8: "iron_block", 10: "iron_block", 14: "iron_block", 15: "iron_block",
            17: "iron_block", 18: "iron_block"}
    for x, b in line.items():
        m.set(x, 1, 4, b)
    m.set(19, 1, 4, "barrel", facing="up", open=False)
    m.set(19, 2, 4, "barrel", facing="up", open=False)
    # two vertical döner spits: drip pan, meat cone, rod to the ceiling
    for x, meat in ((7, "stripped_oak_log"), (9, "stripped_dark_oak_log")):   # chicken, beef
        m.set(x, 1, 4, "cauldron")
        m.fill(x, 2, 4, x, 3, 4, meat, axis="y")
        m.fill(x, 4, 4, x, 5, 4, "iron_chain", axis="y")
    m.set(11, 1, 4, "smoker", facing="south", lit=True)                     # flat grill (plate on top)
    m.set(11, 2, 4, "heavy_weighted_pressure_plate", power=0)
    m.set(12, 1, 4, "cauldron")                                             # fryer (two vats)
    m.set(13, 1, 4, "cauldron")
    m.set(14, 2, 4, "stonecutter", facing="south")                          # prep counter: slicer
    m.set(15, 2, 4, "oak_pressure_plate", powered=False)                    # cutting board
    m.set(6, 2, 4, "white_candle", candles=3, lit=False)                    # sauce bottles
    m.set(8, 2, 4, "red_candle", candles=2, lit=False)
    m.set(10, 2, 4, "yellow_candle", candles=2, lit=False)
    m.set(17, 2, 4, "decorated_pot", facing="south", cracked=False)

    # --- service counter (z=6) with glass display ---
    m.set(6, 1, 6, SIGN_BG)                                                  # till
    m.set(6, 2, 6, "daylight_detector", inverted=False)
    display = ["red_concrete_powder", "lime_concrete_powder", "white_concrete_powder",
               "purple_concrete_powder", "yellow_concrete_powder", "orange_concrete_powder"]
    for i, b in enumerate(display):                                          # tomato, lettuce, cabbage,
        m.set(7 + i, 1, 6, b)                                                # red cabbage, corn, carrot
        m.set(7 + i, 2, 6, "glass_pane")
    m.set(13, 1, 6, SIGN_BG)
    m.set(13, 2, 6, "smooth_stone_slab", type="bottom")                     # tray stack
    m.set(14, 1, 6, SIGN_BG)
    # drinks fridges (customer side) with a gate between them into the staff area
    for z, cols in ((7, ("light_blue_stained_glass", "orange_stained_glass", "red_stained_glass")),
                    (9, ("lime_stained_glass", "yellow_stained_glass", "red_stained_glass"))):
        for y, c in enumerate(cols, start=1):
            m.set(14, y, z, c)
        m.set(14, 4, z, "sea_lantern")
    m.set(14, 1, 8, "dark_oak_fence_gate", facing="east", open=False, in_wall=False, powered=False)

    # --- takeaway window counter + staff side storage ---
    m.fill(15, 1, 9, 18, 1, 9, "iron_block")
    m.set(16, 2, 9, "daylight_detector", inverted=False)            # second till
    m.set(19, 1, 9, "barrel", facing="up", open=False)
    m.fill(19, 1, 6, 19, 1, 8, "iron_block")
    m.set(19, 2, 7, "white_candle", candles=4, lit=False)

    # --- menu board: hanging signs over the counter ---
    for i, lines in enumerate(MENU):
        m.set(6 + i, 5, 6, "dark_oak_hanging_sign", nbt=sign_nbt(lines), rotation=0, attached=False)

    # --- window bar with stools ---
    m.fill(6, 1, 9, 12, 1, 9, "spruce_slab", type="top")
    for x in (6, 8, 10, 12):
        m.set(x, 1, 8, "spruce_fence")
        m.set(x, 2, 8, "spruce_pressure_plate", powered=False)
    # --- two small tables with chairs in the seating nook ---
    for z in (4, 6):
        m.set(2, 1, z, "dark_oak_fence")
        m.set(2, 2, z, "birch_pressure_plate", powered=False)
        m.set(1, 1, z, "spruce_stairs", facing="west", half="bottom")
        m.set(3, 1, z, "spruce_stairs", facing="east", half="bottom")
        m.set(2, 5, z, "lantern", hanging=True)
    for x in (7, 10, 13):
        m.set(x, 5, 9, "lantern", hanging=True)
    m.set(1, 1, 9, "potted_bamboo")

    # --- back kitchen (z=1..2) ---
    k = {1: ("barrel", 2), 2: ("barrel", 1), 4: ("white_concrete", 2), 5: ("white_concrete", 2),
         8: ("iron_block", 1), 9: ("iron_block", 1), 10: ("iron_block", 1), 13: ("white_concrete", 1),
         14: ("white_concrete", 1), 17: ("barrel", 2), 18: ("barrel", 2)}
    for x, (b, h) in k.items():
        for y in range(1, h + 1):
            if b == "barrel":
                m.set(x, y, 1, b, facing="up", open=False)
            else:
                m.set(x, y, 1, b)
    m.set(3, 1, 1, "chest", facing="south", type="single", waterlogged=False)
    for x in (6, 7):
        m.set(x, 1, 1, "water_cauldron", level=3)                          # sinks
    m.set(9, 2, 1, "oak_pressure_plate", powered=False)
    m.set(11, 1, 1, "smoker", facing="south", lit=False)
    m.set(12, 1, 1, "furnace", facing="south", lit=False)
    m.set(15, 1, 1, "composter", level=0)
    m.set(19, 1, 1, "cauldron")


def residential_bay(m):
    # x 21..25: entrance to the flats, stone base
    m.fill(21, 0, 10, 25, 5, 10, "stone_bricks")
    m.fill(25, 0, 0, 25, 5, 10, PLASTER)
    m.fill(21, 0, 0, 24, 5, 0, PLASTER)
    m.fill(21, 1, 5, 24, 5, 5, PLASTER)               # back of the vestibule
    m.fill(21, 1, 6, 21, 5, 9, PLASTER)
    m.fill(24, 1, 6, 24, 5, 9, PLASTER)
    m.fill(22, 0, 6, 23, 0, 9, "polished_andesite")
    for x, hinge in ((22, "left"), (23, "right")):
        m.set(x, 1, 10, "spruce_door", facing="north", half="lower", hinge=hinge, open=False, powered=False)
        m.set(x, 2, 10, "spruce_door", facing="north", half="upper", hinge=hinge, open=False, powered=False)
        m.fill(x, 3, 10, x, 4, 10, "glass_pane")
    m.set(24, 2, 11, "stone_button", face="wall", facing="south", powered=False)   # intercom
    m.set(22, 5, 7, "lantern", hanging=True)
    m.set(22, 3, 2, "light", level=15, waterlogged=False)                          # stops mob spawns


# ---- upper floors (facade only, hollow behind) -------------------------------------------
FLOORS = (12, 15, 18, 21)                 # floor-slab level of each upper storey
WINDOWS = ((2, 3), (6, 7), (10, 11), (14, 15), (18, 19), (22, 23))
BALCONIES = ((5, 8), (17, 20))


def upper_floors(m):
    m.fill(0, 7, 10, 25, 24, 10, PLASTER)     # front
    m.fill(0, 7, 0, 25, 24, 0, PLASTER)       # back
    m.fill(0, 7, 0, 0, 24, 10, PLASTER)       # sides
    m.fill(25, 7, 0, 25, 24, 10, PLASTER)
    m.fill(1, 24, 1, 24, 24, 9, PLASTER)      # attic floor
    for b in FLOORS:
        m.fill(1, b, 1, 24, b, 9, "spruce_planks")
        m.set(6, b + 2, 5, "light", level=15, waterlogged=False)
        m.set(19, b + 2, 5, "light", level=15, waterlogged=False)
        m.fill(0, b, 10, 25, b, 10, TRIM)      # string course at each floor line
        for x1, x2 in WINDOWS:
            m.fill(x1, b + 1, 10, x2, b + 2, 10, "glass_pane")
            for x in (x1, x2):
                m.set(x, b, 11, "smooth_quartz_slab", type="top")    # sill
        for x1, x2 in BALCONIES:
            m.fill(x1, b, 11, x2, b, 12, "smooth_quartz_slab", type="top")
            m.fill(x1, b + 1, 12, x2, b + 1, 12, "iron_bars")
            m.set(x1, b + 1, 11, "iron_bars")
            m.set(x2, b + 1, 11, "iron_bars")
        m.set(7, b + 1, 11, "potted_red_tulip" if b % 2 else "potted_fern")
    # outdoor AC units hung on the piers between windows (white glazed terracotta swirl = fan)
    for x, b in ((4, 15), (12, 12), (21, 18), (13, 21), (24, 12), (9, 18)):
        m.set(x, b + 1, 11, "white_glazed_terracotta", facing="south")
    m.set(6, 8, 5, "light", level=15, waterlogged=False)     # mezzanine behind the sign
    m.set(19, 8, 5, "light", level=15, waterlogged=False)
    # cornice
    m.fill(0, 24, 11, 25, 24, 11, "smooth_quartz_stairs", facing="north", half="top")


def roof(m):
    for x in range(0, 26):
        for i in range(6):
            m.set(x, 25 + i, 11 - i, ROOF, facing="north", half="bottom")   # front slope z 11..6
            m.set(x, 25 + i, i, ROOF, facing="south", half="bottom")        # back slope z 0..5
    for x in (0, 25):                                                      # gable ends
        for z in range(0, 11):
            top = 25 + (z if z <= 5 else 11 - z)
            if top > 25:
                m.fill(x, 25, z, x, top - 1, z, PLASTER)
    for x in (6, 19):                                                      # chimneys
        m.fill(x, 25, 3, x, 31, 3, "bricks")
    m.set(12, 26, 5, "light", level=15, waterlogged=False)


# ---- lit sign band -------------------------------------------------------------------------
def sign_band(m):
    z = 11
    m.fill(0, 5, z, 25, 11, z, SIGN_FRAME)
    m.fill(1, 6, z, 24, 10, z, SIGN_BG)
    x = 1
    for ch in SIGN_WORD:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, px in enumerate(row):
                if px == "X":
                    m.set(x + c, 10 - r, z, LETTER, axis="y")
        x += len(g[0]) + 1
    assert x - 1 == 25, x
