"""Flat-colour preview renderer for the Mimas model (front elevation, isometric, top-down, cutaways).
Colours approximate the vanilla textures; this is a layout check, the real-client screenshots come from CI."""
import math

from PIL import Image, ImageDraw, ImageFont

C = {
    "stone": (125, 125, 125), "smooth_stone": (160, 160, 160), "polished_andesite": (132, 135, 134),
    "polished_diorite": (196, 196, 198), "gray_concrete": (55, 58, 62), "white_concrete": (208, 214, 215),
    "red_concrete": (142, 33, 33), "smooth_sandstone": (224, 214, 170), "smooth_quartz": (236, 230, 223),
    "quartz_bricks": (234, 228, 219), "polished_deepslate": (72, 72, 74), "polished_blackstone": (54, 49, 57),
    "polished_blackstone_wall": (54, 49, 57), "ochre_froglight": (250, 233, 150),
    "pearlescent_froglight": (247, 238, 236), "glass_pane": (190, 222, 235), "iron_bars": (110, 112, 115),
    "iron_door": (200, 200, 202), "dark_oak_door": (75, 50, 25), "spruce_door": (110, 82, 48),
    "polished_blackstone_pressure_plate": (54, 49, 57), "heavy_weighted_pressure_plate": (215, 215, 215),
    "smooth_quartz_slab": (236, 230, 223), "smooth_quartz_stairs": (236, 230, 223), "red_wool": (161, 39, 34),
    "white_wool": (234, 236, 236), "magma_block": (210, 95, 30), "iron_block": (219, 219, 219),
    "barrel": (134, 100, 58), "cauldron": (64, 63, 66), "water_cauldron": (64, 63, 66),
    "stripped_oak_log": (190, 150, 90), "stripped_dark_oak_log": (105, 75, 48), "iron_chain": (60, 66, 78),
    "smoker": (95, 88, 82), "furnace": (110, 110, 110), "stonecutter": (125, 125, 125),
    "oak_pressure_plate": (162, 131, 79), "white_candle": (225, 225, 225), "red_candle": (170, 40, 40),
    "yellow_candle": (230, 190, 60), "decorated_pot": (150, 85, 60), "daylight_detector": (80, 90, 110),
    "red_concrete_powder": (180, 55, 50), "lime_concrete_powder": (125, 190, 45),
    "white_concrete_powder": (226, 228, 228), "purple_concrete_powder": (135, 60, 180),
    "yellow_concrete_powder": (233, 200, 55), "orange_concrete_powder": (228, 132, 32),
    "smooth_stone_slab": (160, 160, 160), "light_blue_stained_glass": (100, 160, 220),
    "orange_stained_glass": (220, 125, 40), "red_stained_glass": (160, 45, 45), "lime_stained_glass": (120, 200, 40),
    "yellow_stained_glass": (230, 210, 50), "sea_lantern": (200, 225, 220), "dark_oak_fence_gate": (66, 43, 20),
    "dark_oak_hanging_sign": (66, 43, 20), "spruce_slab": (114, 84, 48), "spruce_fence": (114, 84, 48),
    "spruce_pressure_plate": (114, 84, 48), "dark_oak_fence": (66, 43, 20), "birch_pressure_plate": (200, 185, 130),
    "spruce_stairs": (114, 84, 48), "lantern": (230, 170, 80), "potted_bamboo": (90, 150, 40),
    "chest": (160, 110, 40), "composter": (120, 80, 40), "stone_bricks": (122, 121, 122),
    "stone_button": (125, 125, 125), "light": None, "spruce_planks": (114, 84, 48),
    "potted_red_tulip": (200, 50, 40), "potted_fern": (70, 120, 50), "brick_stairs": (150, 90, 75),
    "bricks": (140, 85, 72), "rail": (110, 100, 90), "oak_log": (105, 82, 50), "oak_leaves": (70, 125, 45),
    "grass_block": (95, 159, 53), "white_glazed_terracotta": (226, 230, 225), "dirt": (134, 96, 67), "structure_block": (80, 70, 90),
}
EMISSIVE = {"ochre_froglight", "pearlescent_froglight", "magma_block", "sea_lantern", "lantern", "smoker"}
ALPHA = {"glass_pane": 0.35, "light_blue_stained_glass": 0.6, "orange_stained_glass": 0.6,
         "red_stained_glass": 0.6, "lime_stained_glass": 0.6, "yellow_stained_glass": 0.6, "oak_leaves": 0.92}


def px(a):
    return a / 16.0


def shapes(b, m=None, pos=None):
    """Approximate geometry: list of (x0,y0,z0,x1,y1,z1) in block units."""
    i, s = b.id, b.states
    if i == "light":
        return []
    if i.endswith("_slab"):
        t = s.get("type", "bottom")
        return [(0, 0.5, 0, 1, 1, 1)] if t == "top" else [(0, 0, 0, 1, 0.5, 1)] if t == "bottom" else [(0, 0, 0, 1, 1, 1)]
    if i.endswith("_stairs"):
        top = s.get("half") == "top"
        base = (0, 0.5, 0, 1, 1, 1) if top else (0, 0, 0, 1, 0.5, 1)
        y0, y1 = (0, 0.5) if top else (0.5, 1)
        f = s.get("facing", "north")
        step = {"north": (0, y0, 0, 1, y1, 0.5), "south": (0, y0, 0.5, 1, y1, 1),
                "west": (0, y0, 0, 0.5, y1, 1), "east": (0.5, y0, 0, 1, y1, 1)}[f]
        return [base, step]
    if i in ("glass_pane", "iron_bars") or i.endswith("_pane"):
        out = [(px(7), 0, px(7), px(9), 1, px(9))]
        if s.get("north") == "true": out.append((px(7), 0, 0, px(9), 1, px(7)))
        if s.get("south") == "true": out.append((px(7), 0, px(9), px(9), 1, 1))
        if s.get("west") == "true": out.append((0, 0, px(7), px(7), 1, px(9)))
        if s.get("east") == "true": out.append((px(9), 0, px(7), 1, 1, px(9)))
        return out
    if i.endswith("_fence"):
        out = [(px(6), 0, px(6), px(10), 1, px(10))]
        for d, box in (("north", (px(7), px(6), 0, px(9), px(15), px(6))), ("south", (px(7), px(6), px(10), px(9), px(15), 1)),
                       ("west", (0, px(6), px(7), px(6), px(15), px(9))), ("east", (px(10), px(6), px(7), 1, px(15), px(9)))):
            if s.get(d) == "true": out.append(box)
        return out
    if i.endswith("_wall"):
        out = [(px(4), 0, px(4), px(12), 1, px(12))] if s.get("up") == "true" else []
        for d, box in (("north", (px(5), 0, 0, px(11), px(14), px(8))), ("south", (px(5), 0, px(8), px(11), px(14), 1)),
                       ("west", (0, 0, px(5), px(8), px(14), px(11))), ("east", (px(8), 0, px(5), 1, px(14), px(11)))):
            if s.get(d, "none") != "none": out.append(box)
        return out or [(px(4), 0, px(4), px(12), 1, px(12))]
    if i.endswith("_door"):
        f = s.get("facing", "north")
        t = px(3)
        return [{"north": (0, 0, 1 - t, 1, 1, 1), "south": (0, 0, 0, 1, 1, t),
                 "west": (1 - t, 0, 0, 1, 1, 1), "east": (0, 0, 0, t, 1, 1)}[f]]
    if i.endswith("_fence_gate"):
        f = s.get("facing", "north")
        return [(px(7), px(5), 0, px(9), 1, 1)] if f in ("east", "west") else [(0, px(5), px(7), 1, 1, px(9))]
    if i.endswith("pressure_plate"):
        return [(px(1), 0, px(1), px(15), px(1), px(15))]
    if i.endswith("_carpet") or i == "rail":
        return [(0, 0, 0, 1, px(1), 1)]
    if i.endswith("_candle"):
        return [(px(5), 0, px(5), px(11), px(6), px(11))]
    if i == "lantern":
        return [(px(5), px(1), px(5), px(11), px(9), px(11))] if s.get("hanging") == "true" else [(px(5), 0, px(5), px(11), px(9), px(11))]
    if i == "iron_chain":
        a = s.get("axis", "y")
        return [{"y": (px(7), 0, px(7), px(9), 1, px(9)), "x": (0, px(7), px(7), 1, px(9), px(9)),
                 "z": (px(7), px(7), 0, px(9), px(9), 1)}[a]]
    if i.endswith("_hanging_sign"):
        return [(px(1), 0, px(7), px(15), px(10), px(9)), (px(3), px(10), px(8), px(4), 1, px(8.5)),
                (px(12), px(10), px(8), px(13), 1, px(8.5))]
    if i == "daylight_detector":
        return [(0, 0, 0, 1, px(6), 1)]
    if i == "stonecutter":
        return [(0, 0, 0, 1, px(9), 1)]
    if i.startswith("potted_") or i == "flower_pot":
        return [(px(5), 0, px(5), px(11), px(6), px(11)), (px(6), px(6), px(6), px(10), px(12), px(10))]
    if i == "decorated_pot":
        return [(px(1), 0, px(1), px(15), 1, px(15))]
    if i.endswith("_button"):
        return [(px(5), px(6), 0, px(11), px(10), px(2))]
    if i == "chest":
        return [(px(1), 0, px(1), px(15), px(14), px(15))]
    return [(0, 0, 0, 1, 1, 1)]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


FACES = {  # name: (normal, function(box)->4 corners)
    "top": lambda b: [(b[0], b[4], b[2]), (b[3], b[4], b[2]), (b[3], b[4], b[5]), (b[0], b[4], b[5])],
    "south": lambda b: [(b[0], b[1], b[5]), (b[3], b[1], b[5]), (b[3], b[4], b[5]), (b[0], b[4], b[5])],
    "east": lambda b: [(b[3], b[1], b[2]), (b[3], b[1], b[5]), (b[3], b[4], b[5]), (b[3], b[4], b[2])],
    "west": lambda b: [(b[0], b[1], b[2]), (b[0], b[1], b[5]), (b[0], b[4], b[5]), (b[0], b[4], b[2])],
}
NEIGH = {"top": (0, 1, 0), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}


def render(m, view, scale=16, clip=None, title=None, flip_x=False):
    """view: 'iso' (from south-east, above), 'iso_sw', 'front' (from south), 'top' (from above).
    clip(x,y,z)->bool keeps only blocks for cutaways."""
    cos30, sin30 = math.cos(math.radians(30)), 0.5
    if view == "iso":
        proj = lambda x, y, z: ((x - z) * cos30 * scale, ((x + z) * sin30 - y) * scale)
        faces = (("top", 1.0), ("south", 0.80), ("east", 0.64))
        depth = lambda c: c[0] + c[1] + c[2]
    elif view == "iso_sw":
        proj = lambda x, y, z: ((x + z) * cos30 * scale, ((z - x) * sin30 - y) * scale)
        faces = (("top", 1.0), ("south", 0.80), ("west", 0.64))
        depth = lambda c: -c[0] + c[1] + c[2]
    elif view == "front":
        proj = lambda x, y, z: (x * scale, -y * scale)
        faces = (("south", 1.0),)
        depth = lambda c: c[2]
    elif view == "top":
        proj = lambda x, y, z: (x * scale, z * scale)
        faces = (("top", 1.0),)
        depth = lambda c: c[1]
    else:
        raise ValueError(view)

    def full_opaque(p):
        b = m.blocks.get(p)
        if b is None or (clip and not clip(*p)):
            return False
        sh = shapes(b)
        return len(sh) == 1 and sh[0] == (0, 0, 0, 1, 1, 1) and b.id not in ALPHA and C.get(b.id) is not None

    polys = []
    zs = [p[2] for p in m.blocks]
    zmin, zmax = min(zs), max(zs)
    for p, b in m.blocks.items():
        if clip and not clip(*p):
            continue
        col = C.get(b.id, (255, 0, 255))
        if col is None:
            continue
        a = ALPHA.get(b.id, 1.0)
        em = b.id in EMISSIVE
        for box in shapes(b):
            gb = (p[0] + box[0], p[1] + box[1], p[2] + box[2], p[0] + box[3], p[1] + box[4], p[2] + box[5])
            center = ((gb[0] + gb[3]) / 2, (gb[1] + gb[4]) / 2, (gb[2] + gb[5]) / 2)
            full = box == (0, 0, 0, 1, 1, 1)
            for fname, k in faces:
                if full and a == 1.0:
                    d = NEIGH[fname]
                    if full_opaque((p[0] + d[0], p[1] + d[1], p[2] + d[2])):
                        continue
                kk = 1.0 if em else k
                if view == "front" and not em:
                    kk *= 0.55 + 0.45 * (center[2] - zmin) / max(1, zmax - zmin)
                if view == "top":
                    kk *= 0.75 + 0.25 * min(1.0, max(0.0, (center[1] + 2) / 34))
                c = shade(col, kk)
                if b.id == "red_wool" and fname != "top":
                    c = shade(col, kk)
                pts = [proj(*q) for q in FACES[fname](gb)]
                fd = depth(center) + {"top": 0.001, "south": 0.0005, "east": 0.0002, "west": 0.0002}[fname]
                polys.append((fd, pts, c, a, full and a == 1.0 and not em))
    polys.sort(key=lambda t: t[0])
    xs = [q[0] for t in polys for q in t[1]]
    ys = [q[1] for t in polys for q in t[1]]
    pad = 24
    top_pad = 40 if title else pad
    W = int(max(xs) - min(xs)) + 2 * pad
    H = int(max(ys) - min(ys)) + pad + top_pad
    ox, oy = -min(xs) + pad, -min(ys) + top_pad
    img = Image.new("RGB", (W, H), (172, 205, 235))
    draw = ImageDraw.Draw(img)
    for _, pts, c, a, outline in polys:
        pp = [(x + ox, y + oy) for x, y in pts]
        if a >= 1.0:
            draw.polygon(pp, fill=c, outline=shade(c, 0.82) if outline and scale >= 10 else None)
        else:
            x0, y0 = int(min(q[0] for q in pp)), int(min(q[1] for q in pp))
            x1, y1 = int(max(q[0] for q in pp)) + 2, int(max(q[1] for q in pp)) + 2
            if x1 <= x0 or y1 <= y0:
                continue
            mask = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pp], fill=int(255 * a))
            region = img.crop((x0, y0, x1, y1))
            region.paste(Image.new("RGB", region.size, c), (0, 0), mask)
            img.paste(region, (x0, y0))
            draw = ImageDraw.Draw(img)
    if flip_x:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if title:
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except OSError:
            font = ImageFont.load_default()
        d.rectangle((0, 0, img.width, 32), fill=(30, 30, 34))
        d.text((10, 6), title, fill=(255, 255, 255), font=font)
    return img
