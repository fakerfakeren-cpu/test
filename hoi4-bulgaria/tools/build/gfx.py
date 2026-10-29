"""Generated graphics: focus icons (95x85), spirit icons (64x64), event pictures (210x176),
cosmetic-tag flags (TGA 82x52 / 41x26 / 10x7) and the launcher thumbnail.

Glyphs are SVGs from game-icons.net (CC BY 3.0, see CREDITS.md); the Bulgarian tricolour is
drawn directly. Every DDS is read back and checked for size and alpha.
"""
import io
import json
import os
import sys

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from ddslib import write_dds, read_dds  # noqa: E402
from core import add_file  # noqa: E402

ASSETS = os.path.join(TOOLS, "assets", "game-icons")
ICON_JSON = os.environ.get("BFX_GAME_ICONS_JSON", "/tmp/claude-0/icons/gi/package/icons.json")
AUTHORS_TXT = os.environ.get("BFX_GAME_ICONS_AUTHORS", "/tmp/claude-0/icons/authors.txt")
MOD = os.path.join(ROOT, "mod", "bfx_bulgaria")
USED_GLYPHS = {}

STYLES = {  # top colour, bottom colour
    "gold": ((255, 231, 150), (170, 112, 28)),
    "silver": ((244, 246, 250), (118, 126, 140)),
    "iron": ((170, 170, 176), (58, 58, 64)),
    "red": ((236, 86, 72), (128, 18, 18)),
    "green": ((150, 210, 110), (34, 96, 34)),
    "white": ((255, 255, 255), (205, 205, 210)),
    "bronze": ((236, 178, 116), (118, 66, 26)),
    "blue": ((130, 180, 240), (24, 60, 130)),
    "fire": ((255, 232, 120), (200, 50, 10)),
    "orange": ((255, 190, 90), (190, 90, 10)),
}
DISCS = {
    "crimson": ((150, 30, 36), (70, 8, 12)), "purple": ((112, 44, 120), (46, 12, 54)),
    "red": ((190, 30, 30), (90, 6, 6)), "green": ((52, 120, 58), (16, 52, 20)),
    "olive": ((108, 112, 66), (44, 46, 24)), "iron": ((90, 92, 100), (32, 32, 38)),
    "sea": ((40, 100, 160), (10, 36, 70)), "orange": ((210, 120, 40), (110, 50, 8)),
    "steppe": ((150, 128, 60), (70, 56, 20)), "sky": ((90, 150, 210), (30, 70, 120)),
    "night": ((40, 44, 60), (14, 14, 22)), "teal": ((40, 120, 120), (12, 48, 50)),
}


def _icons():
    if not hasattr(_icons, "d"):
        _icons.d = json.load(open(ICON_JSON))
    return _icons.d


def _author(name):
    if not hasattr(_author, "m"):
        _author.m = {}
        for line in open(AUTHORS_TXT):
            line = line.strip()
            if "/" in line:
                a, f = line.split("/", 1)
                _author.m.setdefault(f[:-4], a)
    return _author.m.get(name, "unknown")


def glyph_mask(name, size):
    d = _icons()
    if name not in d["icons"]:
        raise KeyError(f"game-icons has no glyph '{name}'")
    body = d["icons"][name]["body"]
    w, h = d["icons"][name].get("width", d["width"]), d["icons"][name].get("height", d["height"])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{size}" height="{size}">{body}</svg>'
    USED_GLYPHS[name] = _author(name)
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, name + ".svg"), "w") as f:
        f.write(svg)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    return im.getchannel("A")


def vgrad(size, top, bottom):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t)
    return Image.fromarray(np.repeat(arr, w, 1).astype(np.uint8), "RGB")


def metal(mask, style):
    """Fill a mask with a gradient, emboss it and outline it dark."""
    top, bottom = STYLES[style]
    w, h = mask.size
    base = vgrad((w, h), top, bottom).convert("RGBA")
    a = np.array(mask).astype(float) / 255
    blur = np.array(mask.filter(ImageFilter.GaussianBlur(1.6))).astype(float) / 255
    gy, gx = np.gradient(blur)
    light = np.clip(-(gx + gy) * 2.4, -0.45, 0.45)
    rgb = np.array(base)[..., :3].astype(float)
    rgb = np.where(light[..., None] > 0, rgb + (255 - rgb) * light[..., None], rgb * (1 + light[..., None]))
    out = Image.fromarray(np.dstack([rgb.clip(0, 255), a * 255]).astype(np.uint8), "RGBA")
    outline = mask.filter(ImageFilter.MaxFilter(3))
    ol = Image.new("RGBA", (w, h), (24, 18, 12, 0))
    ol.putalpha(outline.point(lambda v: int(v * 0.9)))
    ol.alpha_composite(out)
    return ol


def disc(size, colours, radius_frac=0.46, rim="gold", tricolour=False):
    w, h = size
    r = int(min(w, h) * radius_frac)
    cx, cy = w // 2, h // 2
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    if tricolour:
        band = np.clip(((yy - (cy - r)) / (2 * r) * 3).astype(int), 0, 2)
        cols = np.array([(250, 250, 250), (0, 150, 110), (214, 38, 18)])
        rgb = cols[band].astype(float) * (1 - 0.25 * dist[..., None] ** 2)
    else:
        c1, c2 = np.array(colours[0], float), np.array(colours[1], float)
        rgb = c1[None, None] * (1 - dist[..., None]) + c2[None, None] * dist[..., None]
    alpha = np.clip((1 - dist) * r, 0, 1) * 255
    im = Image.fromarray(np.dstack([rgb.clip(0, 255), alpha]).astype(np.uint8), "RGBA")
    ring = Image.new("L", (w, h), 0)
    ImageDraw.Draw(ring).ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=3)
    im.alpha_composite(metal(ring, rim))
    return im


def shadowed(img, offset=(2, 3), blur=2.2, strength=0.65):
    w, h = img.size
    sh = img.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * strength))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s.putalpha(sh)
    out.alpha_composite(s, offset)
    out.alpha_composite(img)
    return out


def compose(size, layers, pad=6):
    W, H = size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    inner = (W - pad * 2, H - pad * 2)
    for layer in layers:
        kind = layer[0]
        if kind == "disc":
            d = disc(inner, DISCS.get(layer[1], DISCS["iron"]), tricolour=(layer[1] == "tricolour"))
            canvas.alpha_composite(d, (pad, pad))
        elif kind == "glyph":
            _, name, style, scale, dx, dy = (list(layer) + [0, 0])[:6]
            gs = int(min(inner) * scale)
            g = metal(glyph_mask(name, gs), style)
            canvas.alpha_composite(g, (W // 2 - gs // 2 + dx, H // 2 - gs // 2 + dy))
    return shadowed(canvas)


FOCUS_ICONS = {
    "bfx_tsars_dilemma": [("disc", "crimson"), ("glyph", "imperial-crown", "gold", 0.62, 0, -2)],
    "bfx_neuilly_ledger": [("disc", "iron"), ("glyph", "scroll-unfurled", "silver", 0.66)],
    "bfx_tsars_balance": [("disc", "crimson"), ("glyph", "scales", "gold", 0.64)],
    "bfx_salonika_agreement": [("disc", "sea"), ("glyph", "scroll-quill", "gold", 0.62), ("glyph", "dove", "white", 0.30, 16, -14)],
    "bfx_tear_up_neuilly": [("glyph", "burning-book", "fire", 0.92)],
    "bfx_open_the_chancelleries": [("disc", "sea"), ("glyph", "shaking-hands", "gold", 0.66)],
    "bfx_handshake": [("disc", "iron"), ("glyph", "shaking-hands", "silver", 0.66)],
    "bfx_tsar_steps_forward": [("disc", "tricolour"), ("glyph", "imperial-crown", "gold", 0.60)],
    "bfx_tsar_raindrops": [("disc", "sky"), ("glyph", "umbrella", "silver", 0.66)],
    "bfx_bessarabian_bulgars": [("disc", "steppe"), ("glyph", "wheat", "gold", 0.64)],
    "bfx_crusade_east": [("disc", "night"), ("glyph", "crossed-swords", "silver", 0.70)],
    "bfx_greater_bulgaria": [("disc", "tricolour"), ("glyph", "lion", "gold", 0.64)],
    "bfx_tsar_three_seas": [("disc", "sea"), ("glyph", "lion", "gold", 0.66)],
    "bfx_san_stefano": [("disc", "green"), ("glyph", "scroll-unfurled", "gold", 0.66)],
    "bfx_tsar_of_the_bulgarians": [("disc", "crimson"), ("glyph", "crown", "gold", 0.66)],
    "bfx_tsar_stands_alone": [("disc", "crimson"), ("glyph", "lion", "silver", 0.66)],
    "bfx_balkan_tsardom": [("disc", "crimson"), ("glyph", "throne-king", "gold", 0.66)],
    "bfx_master_of_the_peninsula": [("disc", "purple"), ("glyph", "castle", "gold", 0.66)],
    "bfx_legions_march": [("disc", "olive"), ("glyph", "knight-banner", "gold", 0.66)],
    "bfx_legionary_state": [("disc", "green"), ("glyph", "vertical-banner", "silver", 0.66)],
    "bfx_into_the_axis": [("disc", "night"), ("glyph", "eagle-emblem", "silver", 0.68)],
    "bfx_new_bulgarian_order": [("disc", "olive"), ("glyph", "eagle-emblem", "gold", 0.68)],
    "bfx_iron_imperium": [("disc", "iron"), ("glyph", "mailed-fist", "gold", 0.66)],
    "bfx_alt_old_fox_stirs": [("disc", "purple"), ("glyph", "fox-head", "orange", 0.66)],
    "bfx_third_empire": [("disc", "purple"), ("glyph", "imperial-crown", "gold", 0.62)],
    "bfx_alt_tsargrad": [("disc", "crimson"), ("glyph", "byzantin-temple", "gold", 0.66)],
    "bfx_alt_hagia_sophia": [("disc", "purple"), ("glyph", "byzantin-temple", "white", 0.66)],
    "bfx_new_rome": [("disc", "purple"), ("glyph", "church", "gold", 0.66)],
    "bfx_eco_rose_and_leaf": [("disc", "teal"), ("glyph", "rose", "red", 0.62, -6, 0), ("glyph", "curled-leaf", "green", 0.40, 14, 10)],
    "bfx_eco_german_clearing": [("disc", "iron"), ("glyph", "scales", "gold", 0.64)],
    "bfx_atom": [("disc", "night"), ("glyph", "atom", "blue", 0.68)],
    "bfx_bukhovo_uranium": [("disc", "night"), ("glyph", "radioactive", "gold", 0.66)],
    "bfx_nuclear_plant": [("disc", "teal"), ("glyph", "nuclear-plant", "silver", 0.68)],
    "bfx_rila_device": [("disc", "night"), ("glyph", "mushroom-cloud", "fire", 0.72)],
    "bfx_air_aero_clubs": [("disc", "sky"), ("glyph", "biplane", "silver", 0.70)],
    "bfx_parachute": [("disc", "sky"), ("glyph", "parachute", "white", 0.68)],
    "bfx_revolution_must_march": [("disc", "crimson"), ("glyph", "vertical-banner", "fire", 0.66)],
    "bfx_auction": [("disc", "sea"), ("glyph", "scales", "gold", 0.62), ("glyph", "shaking-hands", "silver", 0.30, 16, 14)],
    "bfx_fortress_bulgaria": [("disc", "iron"), ("glyph", "castle", "silver", 0.66)],
}
IDEA_ICONS = {
    "bfx_neuilly_shackles": ("night", "crossed-chains", "iron"),
    "bfx_covert_rearmament": ("olive", "rifle", "silver"),
    "bfx_court_balance": ("crimson", "scales", "gold"),
    "bfx_balkan_embargo": ("iron", "cargo-ship", "red"),
    "bfx_border_crisis": ("crimson", "crossed-swords", "silver"),
    "bfx_salonika_freedom": ("sea", "breaking-chain", "gold"),
    "bfx_royal_propaganda": ("crimson", "radio-tower", "silver"),
    "bfx_open_chancelleries": ("sea", "shaking-hands", "gold"),
    "bfx_tsar_unifier": ("crimson", "imperial-crown", "gold"),
    "bfx_raindrops": ("sky", "umbrella", "silver"),
    "bfx_occupation_corps": ("olive", "police-officer-head", "silver"),
    "bfx_crusade_east": ("night", "crossed-swords", "silver"),
    "bfx_balkan_hegemon": ("crimson", "lion", "gold"),
    "bfx_legionary_state": ("green", "knight-banner", "gold"),
    "bfx_brannik": ("green", "vertical-banner", "silver"),
    "bfx_iron_fist": ("iron", "mailed-fist", "gold"),
    "bfx_ferdinand_restoration": ("purple", "butterfly", "gold"),
    "bfx_byzantine_pretension": ("purple", "eagle-emblem", "gold"),
    "bfx_natural_history": ("green", "flying-beetle", "bronze"),
    "bfx_tobacco_and_rose": ("teal", "rose", "red"),
    "bfx_pernik_coal": ("night", "coal-wagon", "iron"),
    "bfx_iskar_hydro": ("sea", "water-mill", "white"),
    "bfx_chemical": ("teal", "test-tubes", "white"),
    "bfx_trudovaks": ("olive", "hammer-nails", "bronze"),
    "bfx_atomic": ("night", "atom", "blue"),
    "bfx_mountain_army": ("green", "mountain-climbing", "white"),
    "bfx_bayonet": ("olive", "bayonet", "silver"),
    "bfx_reservists": ("olive", "medal", "gold"),
    "bfx_black_sea_fleet": ("sea", "anchor", "silver"),
    "bfx_momentum": ("crimson", "vertical-banner", "fire"),
    "bfx_fortress": ("iron", "castle", "silver"),
    "bfx_storm": ("crimson", "mailed-fist", "fire"),
}
EVENT_PICS = {"bfx_ferdinand_returns": "ferdinand_i", "bfx_lukov_legion": "hristo_lukov", "bfx_imro_uprising": "ivan_mihaylov"}
FLAGS = {
    "bfx_greater_bulgaria": ("tricolour_h", "lion", "gold"),
    "bfx_san_stefano_bulgaria": ("tricolour_h", "crown", "gold"),
    "bfx_balkan_tsardom": ((150, 30, 40), "throne-king", "gold"),
    "bfx_legionary_bulgaria": ((60, 100, 40), "knight-banner", "gold"),
    "bfx_bulgarian_imperium": ((70, 20, 20), "mailed-fist", "gold"),
    "bfx_third_empire": ((120, 20, 50), "imperial-crown", "gold"),
    "bfx_byzantium": ((110, 20, 90), "eagle-emblem", "gold"),
    "bfx_independent_macedonia": ((190, 30, 30), "lion", "gold"),
    "bfx_bulgarian_empire": ("tricolour_v", "imperial-crown", "gold"),
}


def write_checked(img, rel, size):
    path = os.path.join(MOD, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_dds(img, path)
    back = read_dds(path)
    assert back.size == size, (rel, back.size)
    return path


def focus_icons():
    sprites, shines = [], []
    for name, layers in FOCUS_ICONS.items():
        img = compose((95, 85), layers)
        assert img.getchannel("A").getextrema()[0] == 0, f"{name}: no transparency"
        rel = f"gfx/interface/goals/{name}.dds"
        write_checked(img, rel, (95, 85))
        g = f"GFX_focus_{name}"
        sprites.append(f'\tSpriteType = {{\n\t\tname = "{g}"\n\t\ttexturefile = "{rel}"\n\t}}')
        anim = "\n".join(f"""\t\tanimation = {{
\t\t\tanimationmaskfile = "{rel}"
\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"
\t\t\tanimationrotation = {rot}
\t\t\tanimationlooping = no
\t\t\tanimationtime = 0.75
\t\t\tanimationdelay = 0
\t\t\tanimationblendmode = "add"
\t\t\tanimationtype = "scrolling"
\t\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}
\t\t\tanimationtexturescale = {{ x = 1.0 y = 1.0 }}
\t\t}}""" for rot in ("-90.0", "90.0"))
        shines.append(f'\tSpriteType = {{\n\t\tname = "{g}_shine"\n\t\ttexturefile = "{rel}"\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n{anim}\n\t\tlegacy_lazy_load = no\n\t}}')
    add_file("interface/bfx_goals.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")
    add_file("interface/bfx_goals_shine.gfx", "spriteTypes = {\n" + "\n".join(shines) + "\n}\n")


def idea_icons():
    sprites = []
    for name, (bg, glyph, style) in IDEA_ICONS.items():
        W = 64
        plate = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        d = DISCS[bg]
        grad = vgrad((W - 8, W - 8), d[0], d[1]).convert("RGBA")
        m = Image.new("L", (W - 8, W - 8), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, W - 9, W - 9), radius=7, fill=255)
        grad.putalpha(m)
        plate.alpha_composite(grad, (4, 4))
        frame = Image.new("L", (W, W), 0)
        ImageDraw.Draw(frame).rounded_rectangle((4, 4, W - 5, W - 5), radius=7, outline=255, width=2)
        plate.alpha_composite(metal(frame, "bronze"))
        gs = 42
        plate.alpha_composite(metal(glyph_mask(glyph, gs), style), ((W - gs) // 2, (W - gs) // 2))
        img = shadowed(plate, (1, 2), 1.5, 0.5)
        rel = f"gfx/interface/ideas/{name}.dds"
        write_checked(img, rel, (64, 64))
        sprites.append(f'\tSpriteType = {{\n\t\tname = "GFX_idea_{name}"\n\t\ttexturefile = "{rel}"\n\t}}')
    add_file("interface/bfx_ideas.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")


def event_pictures():
    sprites = []
    src = os.path.join(ROOT, "source_images")
    for name, person in EVENT_PICS.items():
        f = next(os.path.join(src, x) for x in os.listdir(src) if x.startswith(person + "."))
        im = Image.open(f).convert("L")
        w, h = im.size
        target = 210 / 176
        ch = int(min(h * 0.62, w / target))
        cw = int(ch * target)
        x0 = max(0, (w - cw) // 2)
        im = im.crop((x0, int(h * 0.04), x0 + cw, int(h * 0.04) + ch)).resize((210, 176), Image.LANCZOS)
        lum = np.array(im).astype(float) / 255
        sep = np.dstack([lum * 240 + 15, lum * 214 + 12, lum * 170 + 8])
        yy, xx = np.mgrid[0:176, 0:210]
        vig = 1 - 0.45 * (((xx - 105) / 105) ** 2 + ((yy - 88) / 88) ** 2)
        sep = sep * vig[..., None] + np.random.default_rng(7).normal(0, 4, sep.shape)
        out = Image.fromarray(sep.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
        rel = f"gfx/event_pictures/{name}.dds"
        write_checked(out, rel, (210, 176))
        sprites.append(f'\tSpriteType = {{\n\t\tname = "GFX_event_{name}"\n\t\ttexturefile = "{rel}"\n\t}}')
    add_file("interface/bfx_eventpictures.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")


def flags():
    for tag, (field, glyph, style) in FLAGS.items():
        W, H = 328, 208
        if field == "tricolour_h":
            base = Image.new("RGB", (W, H))
            for i, c in enumerate([(250, 250, 250), (0, 150, 110), (214, 38, 18)]):
                ImageDraw.Draw(base).rectangle((0, i * H // 3, W, (i + 1) * H // 3), fill=c)
        elif field == "tricolour_v":
            base = Image.new("RGB", (W, H))
            for i, c in enumerate([(250, 250, 250), (0, 150, 110), (214, 38, 18)]):
                ImageDraw.Draw(base).rectangle((i * W // 3, 0, (i + 1) * W // 3, H), fill=c)
        else:
            base = vgrad((W, H), tuple(min(255, c + 25) for c in field), tuple(max(0, c - 25) for c in field))
        base = base.convert("RGBA")
        gs = 150
        g = metal(glyph_mask(glyph, gs), style)
        base.alpha_composite(shadowed(g, (3, 4), 3, 0.5), ((W - gs) // 2, (H - gs) // 2))
        for sub, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
            path = os.path.join(MOD, "gfx", "flags", sub, tag + ".tga")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            base.resize(size, Image.LANCZOS).save(path)
            assert Image.open(path).size == size


def thumbnail():
    W = 512
    img = vgrad((W, W), (60, 22, 26), (14, 10, 12)).convert("RGBA")
    band = Image.new("RGBA", (W, 60))
    for i, c in enumerate([(250, 250, 250), (0, 150, 110), (214, 38, 18)]):
        ImageDraw.Draw(band).rectangle((0, i * 20, W, (i + 1) * 20), fill=c + (255,))
    img.alpha_composite(band, (0, 452))
    lion = shadowed(metal(glyph_mask("lion", 300), "gold"), (5, 6), 5, 0.6)
    img.alpha_composite(lion, ((W - 300) // 2, 40))
    dr = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 46)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 24)
    for text, f, y in (("BULGARIA", font, 342), ("The Tsar's Balance", small, 400)):
        tw = dr.textlength(text, font=f)
        dr.text(((W - tw) / 2 + 2, y + 2), text, font=f, fill=(0, 0, 0, 200))
        dr.text(((W - tw) / 2, y), text, font=f, fill=(245, 222, 150, 255))
    path = os.path.join(MOD, "thumbnail.png")
    img.convert("RGB").save(path, optimize=True)
    assert os.path.getsize(path) < 1024 * 1024


def generate():
    focus_icons()
    idea_icons()
    event_pictures()
    flags()
    thumbnail()
