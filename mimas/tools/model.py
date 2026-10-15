"""Mimas (Sofia) - voxel model of the build.

Local coordinates: x = east, y = up, z = south (the street side).
  x 0..25   building frontage (shop x 0..20, residential entrance bay x 21..25)
  z 0..10   building (back wall z=0, shop front z=10)
  z 11..14  sidewalk, z 15 curb, z 16..22 road with two tram tracks, z 23 curb, z 24..25 far sidewalk
  y -2..-1  foundation, y 0 = ground / floor surface, shop interior y 1..5, ceiling y 6
The player who runs the function stands at local (10, 1, 13): on the sidewalk in front of the shop.
"""

ORIGIN = (10, 1, 13)               # player's feet in local coordinates
VOLUME = ((0, -2, 0), (25, 31, 25))  # everything the build touches (cleared + backed up)


class Block:
    __slots__ = ("id", "states", "nbt")

    def __init__(self, id, states=None, nbt=None):
        self.id = id
        self.states = dict(states or {})
        self.nbt = nbt

    def key(self):
        return (self.id, tuple(sorted(self.states.items())), self.nbt)

    def state_str(self):
        s = "minecraft:" + self.id
        if self.states:
            s += "[" + ",".join(f"{k}={v}" for k, v in sorted(self.states.items())) + "]"
        return s

    def __str__(self):
        return self.state_str() + (self.nbt or "")

    def __repr__(self):
        return str(self)


def _sv(v):
    if v is True:
        return "true"
    if v is False:
        return "false"
    return str(v)


class Model:
    def __init__(self):
        self.blocks = {}

    def set(self, x, y, z, id, nbt=None, **states):
        if id == "air":
            self.blocks.pop((x, y, z), None)
            return
        self.blocks[(x, y, z)] = Block(id, {k: _sv(v) for k, v in states.items()}, nbt)

    def fill(self, x1, y1, z1, x2, y2, z2, id, nbt=None, **states):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, id, nbt, **states)

    def get(self, x, y, z):
        return self.blocks.get((x, y, z))

    def id_at(self, x, y, z):
        b = self.blocks.get((x, y, z))
        return b.id if b else "air"


# --------------------------------------------------------------------------------------------
# Block knowledge used for state resolution, ordering and checks
# --------------------------------------------------------------------------------------------

def is_pane(i):
    return i == "glass_pane" or i.endswith("_stained_glass_pane") or i == "iron_bars"


def is_fence(i):
    return i.endswith("_fence") and not i.endswith("_fence_gate")


def is_wall(i):
    return i.endswith("_wall") and not i.endswith("_wall_sign") and not i.endswith("_wall_hanging_sign") \
        and not i.endswith("_wall_banner") and i not in ("wall_torch",)


# Blocks that are not full cubes (no sturdy faces) - used for pane/fence/wall attachment and support checks.
NON_FULL_SUFFIX = ("_slab", "_stairs", "_pane", "_fence", "_fence_gate", "_wall", "_door", "_trapdoor",
                   "_pressure_plate", "_carpet", "_candle", "_button", "_sign", "_hanging_sign", "_bars",
                   "_chain", "_leaves", "rail", "lantern")
NON_FULL = {"glass_pane", "iron_bars", "iron_chain", "lantern", "soul_lantern", "rail", "cauldron",
            "water_cauldron", "lava_cauldron", "lectern", "stonecutter", "daylight_detector", "flower_pot",
            "decorated_pot", "composter", "hopper", "light", "candle", "chest", "structure_void",
            "heavy_weighted_pressure_plate", "light_weighted_pressure_plate", "brewing_stand"}

# connection exceptions for panes/fences/walls (vanilla isExceptionForConnection)
CONNECT_EXCEPTION_SUFFIX = ("_leaves", "_shulker_box")
CONNECT_EXCEPTION = {"barrier", "carved_pumpkin", "jack_o_lantern", "melon", "pumpkin"}


def is_full(i):
    if i == "air":
        return False
    if i in NON_FULL or i.startswith("potted_"):
        return False
    return not any(i.endswith(s) for s in NON_FULL_SUFFIX)


def connect_exception(i):
    return i in CONNECT_EXCEPTION or any(i.endswith(s) for s in CONNECT_EXCEPTION_SUFFIX)


GRAVITY = lambda i: i.endswith("_concrete_powder") or i in ("sand", "red_sand", "gravel")

# Must be placed after their support exists (phase 3), bottom-up.
ATTACH_SUFFIX = ("_door", "_pressure_plate", "_carpet", "_candle", "_button", "_sign", "_hanging_sign")
ATTACH = {"rail", "lantern", "soul_lantern", "candle", "flower_pot", "heavy_weighted_pressure_plate",
          "light_weighted_pressure_plate", "lectern", "stonecutter", "daylight_detector"}


def is_attach(i):
    return i in ATTACH or i.startswith("potted_") or GRAVITY(i) or any(i.endswith(s) for s in ATTACH_SUFFIX)


def is_shaped(i):
    return is_pane(i) or is_fence(i) or is_wall(i) or i.endswith("_slab") or i.endswith("_stairs") \
        or i.endswith("_fence_gate") or i.endswith("_trapdoor") or i.endswith("_leaves") or i == "iron_chain"


# Blocks a player can walk through (for the walkability check). Closed doors / gates count: they open.
def passable(b):
    if b is None:
        return True
    i = b.id
    if i in ("light", "rail", "iron_chain") or i.endswith("_carpet") or i.endswith("_pressure_plate") \
            or i.endswith("_button") or i.endswith("_door") or i.endswith("_fence_gate") \
            or i.endswith("_wall_sign") or i in ("heavy_weighted_pressure_plate", "light_weighted_pressure_plate"):
        return True
    return False


def standable(b):
    """Can a player stand on top of this block?"""
    if b is None:
        return False
    i = b.id
    if i.endswith("_fence") or i.endswith("_wall"):
        return False  # 1.5 high, can't step onto
    if passable(b) and not i.endswith("_carpet") and not i.endswith("_pressure_plate") and i != "rail":
        return False
    return True


# --------------------------------------------------------------------------------------------
# Connection-state resolution (so setblock places the same states the game would compute)
# --------------------------------------------------------------------------------------------
DIRS = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}
CLOCKWISE_AXIS = {"north": "x", "south": "x", "east": "z", "west": "z"}


def _gate_connects(nb, d):
    # vanilla: FenceGateBlock.connectsToDirection -> gate facing axis == direction.getClockWise().getAxis()
    f = nb.states.get("facing", "north")
    gate_axis = "z" if f in ("north", "south") else "x"
    return gate_axis == CLOCKWISE_AXIS[d]


def resolve_shapes(m):
    for (x, y, z), b in list(m.blocks.items()):
        i = b.id
        if is_pane(i) or is_fence(i) or is_wall(i):
            conns = {}
            for d, (dx, dy, dz) in DIRS.items():
                nb = m.get(x + dx, y, z + dz)
                ni = nb.id if nb else "air"
                if is_pane(i):
                    c = is_pane(ni) or is_wall(ni) or (is_full(ni) and not connect_exception(ni))
                elif is_fence(i):
                    c = (is_fence(ni) and (("nether" in ni) == ("nether" in i))) \
                        or (ni.endswith("_fence_gate") and _gate_connects(nb, d)) \
                        or (is_full(ni) and not connect_exception(ni))
                else:
                    c = is_wall(ni) or is_pane(ni) or (ni.endswith("_fence_gate") and _gate_connects(nb, d)) \
                        or (is_full(ni) and not connect_exception(ni))
                conns[d] = c
            if is_wall(i):
                # vanilla WallBlock: side = TALL if the block above covers that side, LOW if connected, else NONE;
                # post raised if the wall above has a post, or the connections are not symmetric pairs.
                above = m.get(x, y + 1, z)
                ai = above.id if above else "air"
                above_full = is_full(ai)
                for d in DIRS:
                    b.states[d] = ("tall" if above_full else "low") if conns[d] else "none"
                n, s, e, w = (not conns[d] for d in ("north", "south", "east", "west"))
                asym = (n and s and e and w) or (n != s) or (e != w)
                tall_pair = above_full and ((conns["north"] and conns["south"]) or (conns["east"] and conns["west"]))
                above_post = is_wall(ai) and above.states.get("up") == "true"
                override = ai in ("lantern", "soul_lantern", "torch") or ai.endswith("_sign") or above_full
                up = above_post or asym or (not tall_pair and override)
                b.states["up"] = "true" if up else "false"
                b.states.setdefault("waterlogged", "false")
            else:
                for d in DIRS:
                    b.states[d] = "true" if conns[d] else "false"
                b.states.setdefault("waterlogged", "false")
        elif i.endswith("_stairs"):
            b.states.setdefault("shape", "straight")
            b.states.setdefault("waterlogged", "false")
        elif i.endswith("_slab") or i.endswith("_trapdoor") or i.endswith("_hanging_sign") or i.endswith("_wall_sign") \
                or i in ("iron_chain", "lantern", "rail") or i.endswith("_leaves"):
            b.states.setdefault("waterlogged", "false")
    # walls: second pass for 'up' of stacked walls (top-down so the raised post propagates)
    for (x, y, z), b in sorted(m.blocks.items(), key=lambda kv: -kv[0][1]):
        if is_wall(b.id):
            above = m.get(x, y + 1, z)
            if above and is_wall(above.id) and above.states.get("up") == "true":
                b.states["up"] = "true"


# --------------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------------

def floating_report(m):
    """Every block must be connected (face-adjacent chain) to the foundation layer."""
    ground_y = VOLUME[0][1]
    seen = set()
    stack = [p for p in m.blocks if p[1] == ground_y]
    seen.update(stack)
    while stack:
        x, y, z = stack.pop()
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + dx, y + dy, z + dz)
            if q in m.blocks and q not in seen:
                seen.add(q)
                stack.append(q)
    return [p for p in m.blocks if p not in seen and m.blocks[p].id != "light"]


def walk_bfs(m, start):
    """BFS over standing positions (feet cells). A cell is ok if feet+head are passable and the block
    below is standable. Steps up/down of 1 allowed."""
    (x0, y0, z0), (x1, y1, z1) = VOLUME

    def ok(x, y, z):
        if not (x0 <= x <= x1 and z0 <= z <= z1):
            return False
        return passable(m.get(x, y, z)) and passable(m.get(x, y + 1, z)) and standable(m.get(x, y - 1, z))

    seen = {start}
    q = [start]
    while q:
        x, y, z = q.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (0, 1, -1):
                n = (x + dx, y + dy, z + dz)
                if n in seen:
                    continue
                if dy == 1 and not passable(m.get(x, y + 2, z)):
                    continue  # need headroom to jump
                if ok(*n):
                    seen.add(n)
                    q.append(n)
                    break
    return seen
