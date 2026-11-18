#!/usr/bin/env python3
"""Build the Evil Sofia HOI4 map.

Sources (see README):
  tools/districts_mask.png          the 24 districts, traced from a district map (pixel value = district)
  tools/geodata/kvartali.geojson    Sofia's 310 official neighbourhoods (provinces and state names)
  tools/geodata/sofia_geodata.npz   real elevation and land cover (python3 tools/fetch_geodata.py)

Each district is a country. Its provinces are the real neighbourhoods inside it; land that belongs to no
neighbourhood (fields, forest, mountain) joins the nearest one along the terrain, and pieces that are too big
are split along the terrain too, so no border is a straight-sided polygon. Neighbouring provinces are grouped
into several states per country.

Usage:  python3 tools/build_map.py        (run from the evil-sofia/ folder; needs numpy pillow scipy)

Engine rules this script follows (measured in game on HOI4 1.19, see README):
- every file is written with CRLF line endings (definition.csv needs them)
- provinces stay small (TOO LARGE BOX), no four-province pixel corners
- buildings.txt and unitstacks.txt hold the full stock sets of placements and anchors
- every strategic region passes the region-centre divide-by-zero check
"""
import colorsys
import heapq
import importlib.util
import json
import os
import re
import shutil
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 5632, 2048     # vanilla map size: the camera, the map frame and vanilla textures are made for it
CITY_HEIGHT = 1150    # height of the city on the map in pixels; around it is the real land around Sofia
MAX_BOX = 140         # province bounding box limit in px (the engine's "TOO LARGE BOX" starts at ~174 px tall)
LAKE_TARGET, LAKE_MAX_BOX = 12000, 150
SEA_LEVEL = 94
RNG = np.random.default_rng(1944)

# id: (TAG, name, adjective, state category of the capital state, approx. population)
DISTRICTS = {
    1: ("SRD", "Sredets", "Sredetsian", "megalopolis", 32000),
    2: ("VAZ", "Vazrazhdane", "Vazrazhdanian", "metropolis", 37000),
    3: ("OBR", "Oborishte", "Oborishtian", "metropolis", 32000),
    4: ("KRS", "Krasno Selo", "Krasnoselian", "large_city", 72000),
    5: ("SRK", "Serdika", "Serdikan", "large_city", 52000),
    6: ("POD", "Poduyane", "Poduyanian", "large_city", 75000),
    7: ("SLA", "Slatina", "Slatinian", "large_city", 67000),
    8: ("IZG", "Izgrev", "Izgrevian", "large_city", 33000),
    9: ("LOZ", "Lozenets", "Lozenetsian", "large_city", 50000),
    10: ("TRD", "Triaditsa", "Triaditsan", "large_city", 63000),
    11: ("KRP", "Krasna Polyana", "Krasnopolyanian", "large_city", 59000),
    12: ("ILN", "Ilinden", "Ilindenian", "large_city", 33000),
    13: ("NAD", "Nadezhda", "Nadezhdan", "city", 67000),
    14: ("ISK", "Iskar", "Iskarian", "city", 64000),
    15: ("MLA", "Mladost", "Mladostian", "city", 103000),
    16: ("STU", "Studentski", "Studentskian", "city", 71000),
    17: ("LYU", "Lyulin", "Lyulinian", "city", 114000),
    18: ("KRE", "Kremikovtsi", "Kremikovtsian", "large_town", 23000),
    19: ("VIT", "Vitosha", "Vitoshan", "town", 61000),
    20: ("OVK", "Ovcha Kupel", "Ovchakupelian", "town", 52000),
    21: ("VRB", "Vrabnitsa", "Vrabnitsan", "town", 47000),
    22: ("NIS", "Novi Iskar", "Noviiskarian", "rural", 27000),
    23: ("PNC", "Pancharevo", "Pancharevian", "rural", 28000),
    24: ("BNK", "Bankya", "Bankyan", "rural", 13000),
}
# Province size by kind of district: (target px, largest px, smallest px). 1 km^2 is about 450 px.
SIZES = {"inner": (380, 650, 100), "middle": (1100, 1800, 180), "outer": (2600, 4200, 300)}
PROVINCES_PER_STATE = {"inner": 3.0, "middle": 3.5, "outer": 4.5}


def size_class(k):
    return "inner" if k <= 12 else "middle" if k <= 17 else "outer"


# Strategic regions (air zones and weather): (id, name, districts). Pancharevo is split north/south.
REGION_DEFS = [(1, "Old Town", [1, 2, 3, 12]), (2, "Southern Quarters", [4, 8, 9, 10]),
               (3, "Western Quarters", [11, 17, 20]), (4, "Northern Quarters", [5, 6, 13]),
               (5, "Eastern Quarters", [7, 14, 15, 16]), (6, "Vitosha", [19]), (7, "Bankya Hills", [24]),
               (8, "Vrabnitsa Plain", [21]), (9, "Novi Iskar", [22]), (10, "Kremikovtsi", [18]),
               (11, "Pancharevo", []), (12, "Upper Iskar", [23])]
PANCHAREVO_NORTH_REGION = 11
SEA_REGION = (13, "Edge of the World")   # one small sea in the map corner: vanilla always has sea provinces
SEA_BOX = 96

# Where each country's capital is (lat, lon); the neighbourhood there becomes the capital province.
CAPITALS = {1: (42.6895, 23.3195), 2: (42.6975, 23.3075), 3: (42.6975, 23.3420), 4: (42.6805, 23.2870),
            5: (42.7135, 23.3140), 6: (42.7050, 23.3540), 7: (42.6850, 23.3720), 8: (42.6740, 23.3500),
            9: (42.6750, 23.3250), 10: (42.6800, 23.3080), 11: (42.7000, 23.2870), 12: (42.7100, 23.2960),
            13: (42.7310, 23.3020), 14: (42.6650, 23.3950), 15: (42.6500, 23.3750), 16: (42.6500, 23.3450),
            17: (42.7140, 23.2550), 18: (42.7900, 23.5000), 19: (42.6430, 23.2670), 20: (42.6800, 23.2570),
            21: (42.7370, 23.2780), 22: (42.8170, 23.3500), 23: (42.5960, 23.4140), 24: (42.7080, 23.1460)}
# Capital neighbourhood where the district name does not give it away (district: neighbourhood name).
CAPITAL_NAMES = {6: "Hadzhi Dimitar"}
CAPITAL_VP = {1: 30, 2: 15, 3: 15}
POP_RNG = np.random.default_rng(1300)  # state population multipliers (100-200), separate from the map's RNG   # other country capitals get 10, other state capitals 3, other places 1

# Rivers: (name, rivers.bmp width index, waypoints). The first one is the main river; the others end where
# they first touch a river drawn before them (tributaries).
RIVERS = [
    ("Iskar", 8, [(42.500, 23.540), (42.530, 23.505), (42.548, 23.488), (42.565, 23.445), (42.585, 23.425),
                  (42.600, 23.418), (42.625, 23.425), (42.650, 23.430), (42.672, 23.437), (42.695, 23.443),
                  (42.720, 23.440), (42.745, 23.430), (42.770, 23.410), (42.795, 23.380), (42.815, 23.352),
                  (42.840, 23.345), (42.870, 23.345), (42.910, 23.345)]),
    ("Perlovska", 4, [(42.585, 23.295), (42.615, 23.305), (42.640, 23.318), (42.668, 23.330), (42.688, 23.338),
                      (42.697, 23.343), (42.706, 23.360), (42.718, 23.385), (42.730, 23.410), (42.745, 23.440)]),
    ("Vladayska", 4, [(42.610, 23.200), (42.646, 23.205), (42.660, 23.240), (42.676, 23.275), (42.690, 23.300),
                      (42.705, 23.318), (42.725, 23.335), (42.750, 23.350), (42.780, 23.365), (42.805, 23.370)]),
    ("Boyanska", 3, [(42.600, 23.255), (42.640, 23.268), (42.665, 23.272), (42.680, 23.278)]),
]
# terrain.bmp palette indices of vanilla common/terrain/00_terrain.txt (ground textures)
TEX_PLAINS, TEX_FIELDS, TEX_FOREST, TEX_FOREST_HIGH, TEX_HILLS = 0, 5, 1, 4, 17
TEX_ROCK, TEX_SNOW, TEX_MARSH, TEX_CITY, TEX_LAKE = 6, 16, 9, 13, 14

# Leaders and generals: one of each per country (first name, surname).
FIRST = ["Krum", "Asen", "Boris", "Kaloyan", "Simeon", "Petar", "Ivan", "Todor", "Stoyan", "Hristo", "Vasil", "Lyuben",
         "Georgi", "Dimitar", "Nikola", "Atanas", "Kiril", "Angel", "Rumen", "Plamen", "Ognyan", "Bozhidar", "Radoslav",
         "Zhivko", "Stefan", "Yordan", "Mihail", "Lazar", "Konstantin", "Velizar", "Tsvetan", "Emil", "Rayko", "Sava",
         "Pavel", "Trayko", "Kosta", "Vladimir", "Dobri", "Spas", "Grigor", "Anton", "Valentin", "Svetoslav", "Yasen",
         "Momchil", "Zlatko", "Iliya"]
SURNAMES = ["Ivanov", "Petrov", "Georgiev", "Dimitrov", "Nikolov", "Stoyanov", "Todorov", "Hristov", "Vasilev", "Angelov",
            "Atanasov", "Kirilov", "Popov", "Kolev", "Marinov", "Yordanov", "Iliev", "Mihaylov", "Kostov", "Pavlov",
            "Stefanov", "Lazarov", "Radev", "Zhelev", "Bonev", "Tsvetkov", "Kamenov", "Dobrev", "Spasov", "Grigorov",
            "Antonov", "Valchev", "Penev", "Slavov", "Rusev", "Tonchev", "Genov", "Velchev", "Ganev", "Yankov",
            "Draganov", "Bogdanov", "Ruskov", "Simeonov", "Tasev", "Uzunov", "Vulkov", "Zahariev"]
# Country leaders with a set name (the others get one from the lists below). A leader gets a portrait when
# tools/portraits/<TAG>.png exists (156x210 px); portraits stay out of the git repository.
LEADER_TRAITS = {"VIT": ["evil_sofia_hates_communism"]}   # traits from tools/focus_sredets.py
LEADER_NAMES = {"SRD": "Victor Kolev", "MLA": "Georgi Poryazov", "VIT": "Daniel-Henry Capel",
                "KRP": "Stefan Kartunov", "OBR": "Anton Zafirov", "LOZ": "Georgi Yanchovichin",
                "TRD": "Alexander Dimitrov", "LYU": "GrimBoss"}
# Countries with their own leader are the featured ones on the start screen, with these descriptions; the
# others are the small flags along the bottom.
import sys as _sys
_sys.path.insert(0, os.path.join(ROOT, "tools"))
import texts as _texts   # start screen and leader descriptions, starting advisors
FEATURED = _texts.FEATURED
FEMALE = ["Maria", "Elena", "Ivanka", "Yordanka", "Rositsa", "Desislava", "Vesela", "Teodora", "Milena", "Radka",
          "Stefka", "Tsvetana", "Gergana", "Kalina", "Nevena", "Zornitsa"]


def _advisor_names(n):
    """Names for the starting advisors (men and women), none the same as a leader's or general's."""
    rng = np.random.default_rng(1878)
    taken = {f"{FIRST[i]} {SURNAMES[i]}" for i in range(len(FIRST))}
    names = []
    while len(names) < n:
        surname = SURNAMES[rng.integers(len(SURNAMES))]
        if rng.random() < 0.35:
            name = f"{FEMALE[rng.integers(len(FEMALE))]} {surname}a"
        else:
            name = f"{FIRST[rng.integers(len(FIRST))]} {surname}"
        if name not in taken:
            taken.add(name)
            names.append(name)
    return names


ADVISOR_NAMES = _advisor_names(3 * 24)


# Folders whose files are named after states and regions: cleared first, so no stale file survives a rebuild.
for folder in ("history/states", "map/strategicregions", "map/supplyareas", "gfx/leaders", "history/units",
               "gfx/interface/goals/evil_sofia", "gfx/interface/ideas/evil_sofia"):
    shutil.rmtree(os.path.join(ROOT, folder), ignore_errors=True)


def out(path):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def write(path, text, bom=False):
    # CRLF line endings: with plain LF the game silently drops the continent column of
    # definition.csv, every land province then fails the "must have a continent" map check,
    # and the game stops with "Failed to load the map".
    with open(out(path), "w", encoding="utf-8-sig" if bom else "utf-8", newline="\r\n") as f:
        f.write(text)


def country_color(i):
    r, g, b = colorsys.hsv_to_rgb(((i * 0.381966) % 1.0), 0.55 + 0.35 * (i % 2), 0.55 + 0.15 * (i % 3))
    return int(r * 255), int(g * 255), int(b * 255)


# ---------------------------------------------------------------- neighbourhood names
CYR = dict(zip("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ",
               ["A", "B", "V", "G", "D", "E", "ZH", "Z", "I", "Y", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U",
                "F", "H", "TS", "CH", "SH", "SHT", "A", "Y", "YU", "YA"]))
# Names that are cut short in the source data, or that read better translated.
KV_NAMES = {
    "ЦЕНТЪР": "City Centre", "ЖИЛИЩНА ГРУПА - ЗООПАРК": "Zoo Estate", "ЖИЛИЩНА ГРУПА ЮЖЕН ПАРК": "South Park Estate",
    "ЖК. ЛЮЛИН - ЦЕНТЪР": "Lyulin Centre", "ЛЕТИЩЕ СОФИЯ": "Sofia Airport", "7-МИ  11-ТИ КИЛОМЕТЪР": "7th-11th Kilometre",
    "СКЛАДОВО-ПРОИЗВОДСТВЕНА ЗО": None, "---": None, "": None,
    "ЗАПАДЕН ПАРК": "West Park", "СЕВЕРЕН ПАРК": "North Park", "ЮЖЕН ПАРК": "South Park", "ЗООПАРК": "Sofia Zoo",
    "ПАРК БОРИСОВА ГРАДИНА": "Borisova Gradina", "ПАРК БОТАНИЧЕСКА ГРАДИНА": "Botanical Garden",
    "ПАРК ЦЕНТРАЛНИ СОФИЙСКИ ГР": "Central Cemetery", "ПАРК МАЛАШЕВСКИ ГРОБИЩА": "Malashevtsi Cemetery",
    "РЕЗИДЕНЦИЯ БОЯНА": "Boyana Residence", "М. НАЦИОНАЛЕН КИНОЦЕНТЪР": "National Film Centre",
    "В.З. АМЕРИКАНСКИ КОЛЕЖ": "American College", "В.З. ПАСАРЕЛСКО ЕЗЕРО": "Pasarel Lake",
    "В.З. ДРАГАЛЕВЦИ ЛИФТА": "Dragalevtsi Lift", "В.З. ВРАНА-ЛОЗЕН ТРИЪГЪЛНИК": "Vrana-Lozen Triangle",
    "В.З. КИНОЦЕНТЪРА III ЧАСТ": "Kinotsentara 3",
}
LOCAL_PREFIXES = ("ЖК. ", "КВ. ", "В.З. ", "М. ", "С. ", "ГР. ", "МАХ. ")


def translit(text):
    """Bulgarian (official streamlined system), title case: 'МЛАДОСТ 1' -> 'Mladost 1'."""
    words = []
    for w in text.upper().split():
        if w.endswith("ИЯ"):
            w = w[:-2] + "IA"          # София -> Sofia
        latin = "".join(CYR.get(ch, ch) for ch in w)
        words.append(latin.capitalize() if latin.isalpha() else latin.title())
    return " ".join(words)


def kvartal_name(props):
    raw = (props.get("kvname") or "").strip()
    if raw in KV_NAMES:
        return KV_NAMES[raw]
    name, villas = raw, raw.startswith("В.З. ")
    for pre in LOCAL_PREFIXES:
        if name.startswith(pre):
            name = name[len(pre):].strip()
    name = name.replace("СВ. ", "СВЕТИ ").replace(" - ", "-").replace("- ", "-")
    for bg, en in (("ПРОМИШЛЕНА ЗОНА ", " Industrial Zone"), ("НПЗ ", " Industrial Zone"), ("ПАРК ", " Park"),
                   ("МАХАЛА ", " Mahala"), ("ЗОНА ", "Zone ")):
        if name.startswith(bg):
            rest = translit(name[len(bg):])
            return en + rest if en.endswith(" ") else rest + en
    for bg, en in (("-ИЗТОК", " East"), ("-СЕВЕР", " North"), ("-ЮГ", " South")):
        if name.endswith(bg):
            return translit(name[:-len(bg)]) + en + (" Villas" if villas else "")
    return translit(name) + (" Villas" if villas else "")


# Landmarks that name provinces no neighbourhood name reaches (pieces of big neighbourhoods, mountain land).
LANDMARKS = [("Vitosha Boulevard", 42.6895, 23.3195), ("Graf Ignatiev", 42.6905, 23.3290),
             ("Slaveykov Square", 42.6935, 23.3245), ("Sveta Nedelya", 42.6967, 23.3212),
             ("Alexander Nevsky", 42.6959, 23.3328), ("Lions' Bridge", 42.7040, 23.3240),
             ("Central Station", 42.7115, 23.3215), ("Zhenski Pazar", 42.7010, 23.3165),
             ("Vazrazhdane Square", 42.6975, 23.3075), ("Doctor's Garden", 42.6930, 23.3355),
             ("Eagles' Bridge", 42.6905, 23.3390), ("Zaimov Park", 42.7010, 23.3380), ("NDK", 42.6845, 23.3190),
             ("Gerena", 42.6970, 23.3680), ("Malashevtsi", 42.7170, 23.3450),
             ("Musagenitsa", 42.6570, 23.3600), ("Business Park", 42.6260, 23.3770), ("Pavlovo", 42.6670, 23.2700),
             ("Kopitoto", 42.6370, 23.2400), ("Zlatni Mostove", 42.6056, 23.2364), ("Aleko", 42.5835, 23.2918),
             ("Cherni Vrah", 42.5639, 23.2778), ("The Steelworks", 42.7560, 23.5090), ("Plana", 42.4720, 23.4340)]


# ---------------------------------------------------------------- districts
full_mask = np.asarray(Image.open(os.path.join(ROOT, "tools", "districts_mask.png")).convert("L"))
ys, xs = np.nonzero(full_mask)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
src = full_mask[y0:y1, x0:x1]
scale = CITY_HEIGHT / src.shape[0]
tw, th = int(src.shape[1] * scale), int(src.shape[0] * scale)
ox, oy = (W - tw) // 2, (H - th) // 2
best = np.full((th, tw), -1.0, np.float32)   # smooth upscale: strongest blurred district mask wins
lab = np.zeros((th, tw), np.int32)
for k in range(0, 25):
    m = ndi.gaussian_filter((src == k).astype(np.float32), 0.8)
    m = np.asarray(Image.fromarray(m).resize((tw, th), Image.BILINEAR))
    sel = m > best
    best[sel], lab[sel] = m[sel], k
dist = np.zeros((H, W), np.int32)
dist[oy:oy + th, ox:ox + tw] = lab


def tidy_districts(d):
    """Keep the largest piece of each district; stray pieces join the district around them."""
    d = d.copy()
    for k in DISTRICTS:
        cl, n = ndi.label(d == k)
        if n > 1:
            keep = np.bincount(cl.ravel())[1:].argmax() + 1
            d[(cl > 0) & (cl != keep)] = -1
    holes_ = d == -1
    if holes_.any():
        idx_ = ndi.distance_transform_edt(d <= 0, return_distances=False, return_indices=True)
        d[holes_] = d[idx_[0], idx_[1]][holes_]
    return d


dist = tidy_districts(dist)
city = dist > 0

# ---------------------------------------------------------------- georeference (lat/lon <-> map pixels)
# Fitted so that the official neighbourhoods, taken together, cover the traced city outline as well as
# possible: mask_x = 312 + dx + (lon - 23.3215) * 1119 * sx, mask_y = 312 + dy - (lat - 42.6966) * 1521 * sy.
KV = json.load(open(os.path.join(ROOT, "tools", "geodata", "kvartali.geojson"), encoding="utf-8"))["features"]


def kv_outline(sx, sy, dx, dy):
    img = Image.new("L", full_mask.shape[::-1], 0)
    d_ = ImageDraw.Draw(img)
    for f in KV:
        for poly in f["geometry"]["coordinates"]:
            d_.polygon([(312 + dx + (lo - 23.3215) * 1119 * sx, 312 + dy - (la - 42.6966) * 1521 * sy)
                        for lo, la in poly[0]], fill=255)
    return np.asarray(img) > 0


def overlap(params):
    u = kv_outline(*params)
    return (u & (full_mask > 0)).sum() / (u | (full_mask > 0)).sum()


fit = [0.95, 0.95, -16.0, -11.0]
score = overlap(fit)
for step in ((0.01, 0.01, 2, 2), (0.005, 0.005, 1, 1)):
    improved = True
    while improved:
        improved = False
        for i in range(4):
            for sign in (-1, 1):
                trial = list(fit)
                trial[i] += sign * step[i]
                s_ = overlap(trial)
                if s_ > score + 1e-6:
                    fit, score, improved = trial, s_, True
GSX, GSY, GDX, GDY = fit
print(f"georeference: neighbourhoods cover the district outline at {score:.3f} overlap")


def place_px(lat, lon):
    sx_ = 312 + GDX + (lon - 23.3215) * 1119 * GSX
    sy_ = 312 + GDY - (lat - 42.6966) * 1521 * GSY
    return ox + (sx_ - x0) * scale, oy + (sy_ - y0) * scale


# ---------------------------------------------------------------- neighbourhoods on the map
def ring_area(ring):
    a = np.asarray(ring, np.float64)
    return abs(np.dot(a[:, 0], np.roll(a[:, 1], 1)) - np.dot(a[:, 1], np.roll(a[:, 0], 1))) / 2


kv_raster = Image.new("I", (W, H), 0)
dr = ImageDraw.Draw(kv_raster)
kv_info = {}
order = sorted(range(len(KV)), key=lambda i: -sum(ring_area(p[0]) for p in KV[i]["geometry"]["coordinates"]))
for i in order:   # biggest first, so a neighbourhood inside another one stays on top
    f = KV[i]
    if f["properties"].get("type_kv") == "0":
        continue      # "rest of the municipality": land that belongs to no neighbourhood
    kv_info[i + 1] = (kvartal_name(f["properties"]), f["properties"].get("type_kv"))
    for poly in f["geometry"]["coordinates"]:
        dr.polygon([place_px(la, lo) for lo, la in poly[0]], fill=i + 1)
KVR = np.asarray(kv_raster, dtype=np.int32)
del kv_raster, dr
RESIDENTIAL = ("1", "6")              # housing estates, quarters, villages and towns


def kv_shares():
    """For each neighbourhood: the district holding most of it {kvid: (district, px)}, its size inside the
    city, and the pixels it covers there."""
    yy_, xx_ = np.nonzero((KVR > 0) & (dist > 0))
    kv_, d_ = KVR[yy_, xx_], dist[yy_, xx_]
    cnt_ = np.bincount(kv_.astype(np.int64) * 32 + d_)
    home = {}
    for code in np.nonzero(cnt_)[0]:
        kvid_, dd = divmod(int(code), 32)
        if cnt_[code] > home.get(kvid_, (0, 0))[1]:
            home[kvid_] = (dd, int(cnt_[code]))
    return home, np.bincount(kv_), yy_, xx_, kv_


# Neighbourhoods spread over several districts with no clear majority, and where they really belong.
KV_HOME_OVERRIDES = {"City Centre": 1, "Poduyane": 3}
# Neighbourhoods the hand-traced district lines split or put in the wrong district: they join their real
# district whole (Yavorov is in Sredets, Krastova Vada in Lozenets).
KV_DISTRICT_FIXES = {"Yavorov": 1, "Krastova Vada": 9}
# The part of a neighbourhood in another district that goes by its own name there: (name, district) -> name.
KV_PIECE_NAMES = {("Poduyane", 7): "Reduta"}
# The districts were traced by hand from a district map, so their lines are approximate. Inside the city they
# now follow the real neighbourhood edges: a neighbourhood that lies mostly (60 %+) in one traced district joins
# that district whole. The traced line stays only where a neighbourhood really is split between districts.
kv_home, kv_total, _yy, _xx, _kv = kv_shares()
snap = np.zeros(int(KVR.max()) + 1, np.int32)
for kvid_, (dd, n_) in kv_home.items():
    if kv_info[kvid_][0] in KV_DISTRICT_FIXES:
        snap[kvid_] = KV_DISTRICT_FIXES[kv_info[kvid_][0]]
    elif n_ >= 0.6 * kv_total[kvid_]:
        snap[kvid_] = dd
_to = snap[_kv]
dist[_yy[_to > 0], _xx[_to > 0]] = _to[_to > 0]
dist = tidy_districts(dist)
city = dist > 0
kv_home, kv_total, _yy, _xx, _kv = kv_shares()
for kvid_, (nm_, t_) in kv_info.items():
    if nm_ in KV_HOME_OVERRIDES and kvid_ in kv_home:
        kv_home[kvid_] = (KV_HOME_OVERRIDES[nm_], kv_home[kvid_][1])
_n = np.maximum(np.bincount(_kv), 1)
KV_CY, KV_CX = np.bincount(_kv, weights=_yy) / _n, np.bincount(_kv, weights=_xx) / _n
print(f"districts: {sum(n_ for _, n_ in kv_home.values()) / len(_kv):.3f} of neighbourhood land lies in its home district")
del _yy, _xx, _kv, _n, _to

gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
LON = 23.3215 + (x0 + (gx - ox) / scale - 312 - GDX) / (1119 * GSX)
LAT = 42.6966 - (y0 + (gy - oy) / scale - 312 - GDY) / (1521 * GSY)
KM_PER_PX = 1 / (13.7 * (GSX + GSY) / 2 * scale)
del gy, gx

# ---------------------------------------------------------------- real elevation and land cover
# tools/fetch_geodata.py downloads them: AWS Terrain Tiles (metres) and ESA WorldCover 2021 (classes:
# 10 trees, 20 shrubs, 30 grass, 40 crops, 50 built-up, 60 bare, 70 snow, 80 water, 90 wetland).
geo = np.load(os.path.join(ROOT, "tools", "geodata", "sofia_geodata.npz"))
g_lat_min, g_lat_max, g_lon_min, g_lon_max, g_res = geo["bounds"]
gi = (g_lat_max - LAT) / g_res - 0.5
gj = (LON - g_lon_min) / g_res - 0.5
ELEV = ndi.map_coordinates(geo["elevation"].astype(np.float32), [gi, gj], order=1, mode="nearest")
LC = ndi.map_coordinates(geo["landcover"], [gi, gj], order=0, mode="nearest")
del gi, gj, LAT, LON
M_PER_PX = KM_PER_PX * 1000
ELEV_S = ndi.gaussian_filter(ELEV, 1.0)
slope_y, slope_x = np.gradient(ELEV_S, M_PER_PX)
SLOPE = np.hypot(slope_x, slope_y)
TREES = LC == 10
BUILT = LC == 50
WATER = ndi.binary_opening(LC == 80, iterations=2)     # lakes and reservoirs, not thin river lines
MOUNT = (ELEV > 1400) | (SLOPE > 0.40)
HILL = (ELEV > 850) | (SLOPE > 0.15)
print(f"geodata: elevation {ELEV.min():.0f}-{ELEV.max():.0f} m, {M_PER_PX:.0f} m per map pixel")

# Big real lakes and reservoirs inside the city (the Iskar reservoir) become impassable lake provinces.
cl_, n_ = ndi.label(WATER & city)
sizes_ = np.bincount(cl_.ravel())
big_water = np.isin(cl_, [j for j in range(1, n_ + 1) if sizes_[j] >= 1500])
dist[big_water] = 0
city = dist > 0

# ---------------------------------------------------------------- rivers (they also guide province borders)
river = np.full((H, W), 255, np.uint8)         # rivers.bmp: 255 land, 254 water, 0 source, 1 joins, 3..11 width
river[~city] = 254
ELEV_R = ndi.gaussian_filter(ELEV, 3.0)


def valley_path(a, b, pad=40):
    """4-connected cheapest path from a to b, where climbing above the local valley floor is expensive."""
    (xa, ya), (xb, yb) = [(int(round(v[0])), int(round(v[1]))) for v in (a, b)]
    bx0, bx1 = max(min(xa, xb) - pad, 0), min(max(xa, xb) + pad, W - 1)
    by0, by1 = max(min(ya, yb) - pad, 0), min(max(ya, yb) + pad, H - 1)
    e = ELEV_R[by0:by1 + 1, bx0:bx1 + 1]
    hh, ww = e.shape
    cost = 1.0 + ((e - e.min()) / 15.0) ** 1.5
    ix = np.arange(hh * ww).reshape(hh, ww)
    pairs = [(ix[:, :-1], ix[:, 1:], (cost[:, :-1] + cost[:, 1:]) / 2),
             (ix[:-1, :], ix[1:, :], (cost[:-1, :] + cost[1:, :]) / 2)]
    rows = np.concatenate([q for a_, b_, c_ in pairs for q in (a_.ravel(), b_.ravel())])
    cols = np.concatenate([q for a_, b_, c_ in pairs for q in (b_.ravel(), a_.ravel())])
    wts = np.concatenate([q for a_, b_, c_ in pairs for q in (c_.ravel(), c_.ravel())])
    graph = coo_matrix((wts, (rows, cols)), shape=(hh * ww, hh * ww)).tocsr()
    s_i, d_i = (ya - by0) * ww + (xa - bx0), (yb - by0) * ww + (xb - bx0)
    _, pred = dijkstra(graph, indices=s_i, return_predecessors=True)
    path, cur = [], d_i
    while cur != s_i and cur >= 0:
        path.append((cur % ww + bx0, cur // ww + by0))
        cur = pred[cur]
    path.append((xa, ya))
    return path[::-1]


def river_course(waypoints):
    pts = [place_px(la, lo) for la, lo in waypoints]
    res = []
    for a, b in zip(pts, pts[1:]):
        seg = valley_path(a, b)
        res += seg if not res else seg[1:]
    out_, seen = [], {}
    for q in res:   # cut out any loop
        if q in seen:
            del out_[seen[q] + 1:]
            seen = {v: i for i, v in enumerate(out_)}
            continue
        seen[q] = len(out_)
        out_.append(q)
    i = 0           # 1 px wide: if it touches itself further along, skip the detour in between
    while i < len(out_):
        xi, yi = out_[i]
        for j in range(len(out_) - 1, i + 1, -1):
            if abs(out_[j][0] - xi) + abs(out_[j][1] - yi) == 1:
                del out_[i + 1:j]
                break
        i += 1
    return out_


river_mask = np.zeros((H, W), bool)


def n4(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def junction_ok(base, seq):
    """seq = new tributary pixels; the last one is the flow-in pixel that touches the river."""
    taken = set(base)
    for i_, (x, y) in enumerate(seq):
        if not (0 < x < W - 1 and 0 < y < H - 1) or not city[y, x] or river_mask[y, x] or (x, y) in taken:
            return False
        if sum(river_mask[yy, xx] for xx, yy in n4(x, y)) != (1 if i_ == len(seq) - 1 else 0):
            return False
        taken.add((x, y))
    for x, y in seq:   # no 2x2 block of river pixels around the new ones
        for ddx in (-1, 0):
            for ddy in (-1, 0):
                cells = [(x + ddx + a_, y + ddy + b_) for a_ in (0, 1) for b_ in (0, 1)]
                if all(river_mask[cy_, cx_] or (cx_, cy_) in taken for cx_, cy_ in cells):
                    return False
    return True


for ri, (rname, width, waypoints) in enumerate(RIVERS):
    pix = river_course(waypoints)
    on_land = [city[y, x] if 0 <= x < W and 0 <= y < H else False for x, y in pix]
    joins = False
    if ri == 0:   # main river: its longest stretch on land
        runs, cur = [], []
        for q, ok in zip(pix, on_land):
            if ok:
                cur.append(q)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        course = max(runs, key=len)
    else:         # tributary: from its source until it reaches a river already drawn
        course = []
        for q, ok in zip(pix, on_land):
            if not ok:
                break
            x, y = q
            if river_mask[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2].any():
                for back in range(0, 12):
                    base = course[:len(course) - back] if back else list(course)
                    start = course[len(course) - back] if back else q
                    options = [[start]]
                    for n1 in n4(*start):
                        options.append([start, n1])
                        options += [[start, n1, n2] for n2 in n4(*n1) if n2 != start]
                    good = next((seq for seq in options if junction_ok(base, seq)), None)
                    if good:
                        course = base + good
                        joins = True
                        break
                if not joins:   # no clean junction: end the river just before it would touch
                    course = course[:-2]
                break
            course.append(q)
    if len(course) < 5:
        continue
    for i, (x, y) in enumerate(course):
        river[y, x] = 0 if i == 0 else (1 if joins and i == len(course) - 1 else width)
        river_mask[y, x] = True

# ---------------------------------------------------------------- cost of crossing the land
# Provinces and states grow outwards from real neighbourhoods; where growth fronts meet becomes a border.
# Rivers, steep slopes and edges between built-up land, forest and fields slow growth, so borders settle on
# them, and fractal noise makes them wander like real boundaries instead of straight polygon edges.
cy0_, cy1_ = np.nonzero(city.any(1))[0][[0, -1]]
cx0_, cx1_ = np.nonzero(city.any(0))[0][[0, -1]]
CB = (slice(cy0_ - 4, cy1_ + 5), slice(cx0_ - 4, cx1_ + 5))   # bounding box of the city
noise = np.zeros(city[CB].shape, np.float32)
for sigma, amp in ((2.0, 0.45), (6.0, 0.35), (16.0, 0.20)):
    n_ = ndi.gaussian_filter(RNG.normal(0, 1, noise.shape).astype(np.float32), sigma)
    noise += amp * n_ / (np.abs(n_).max() + 1e-6)
noise = (noise - noise.min()) / (noise.max() - noise.min())
edges = np.zeros(noise.shape, np.float32)
for mask_ in (BUILT[CB], TREES[CB]):
    sm = ndi.gaussian_filter(mask_.astype(np.float32), 1.5)
    gy_, gx_ = np.gradient(sm)
    edges += np.hypot(gx_, gy_)
COST = np.zeros((H, W), np.float32)
COST[CB] = (1.0 + 2.5 * noise + 15.0 * np.clip(SLOPE[CB], 0, 1) + 6.0 * (edges / (edges.max() + 1e-6))
            + 8.0 * ndi.binary_dilation(river_mask[CB], iterations=1))
del noise, edges


def grow(mask, labels, cost):
    """Fill the zero pixels of `labels` inside `mask` with the label whose growth front reaches them first
    (multi-source shortest paths over an 8-connected pixel graph weighted by `cost`)."""
    n = int(mask.sum())
    ix = -np.ones(mask.shape, np.int64)
    ix[mask] = np.arange(n)
    rows, cols, wts = [], [], []
    hh, ww = mask.shape
    for dy, dx, f in ((0, 1, 1.0), (1, 0, 1.0), (1, 1, 1.4142), (1, -1, 1.4142)):
        a_ = (slice(0, hh - dy), slice(max(0, -dx), ww - max(0, dx)))
        b_ = (slice(dy, hh), slice(max(0, dx), ww - max(0, -dx) if dx < 0 else ww))
        both = mask[a_] & mask[b_]
        rows.append(ix[a_][both])
        cols.append(ix[b_][both])
        wts.append(((cost[a_][both] + cost[b_][both]) / 2 * f).astype(np.float64))
    graph = coo_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
    flat = labels[mask]
    seeds = np.flatnonzero(flat > 0)
    if len(seeds) == 0:
        return labels
    _, _, srcs = dijkstra(graph, directed=False, indices=seeds, min_only=True, return_predecessors=True)
    filled = flat.copy()
    reach = srcs >= 0
    filled[reach] = flat[srcs[reach]]
    out_ = labels.copy()
    out_[mask] = filled
    gaps = mask & (out_ == 0)                  # cut off from every seed: nearest label
    if gaps.any():
        idx_ = ndi.distance_transform_edt(out_ == 0, return_distances=False, return_indices=True)
        out_[gaps] = out_[idx_[0], idx_[1]][gaps]
    return out_


def split_organic(mask, n, cost):
    """Split `mask` into n parts that grow from well-spread seeds along the terrain (labels 1..n)."""
    pts = np.argwhere(mask).astype(np.float32)
    cen = pts[RNG.choice(len(pts), n, replace=False)]
    for _ in range(12):   # k-means on coordinates only places the seeds
        a = ((pts[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (a == j).any():
                cen[j] = pts[a == j].mean(0)
    labels = np.zeros(mask.shape, np.int32)
    for j, (cy_, cx_) in enumerate(cen, 1):
        q = np.argmin(((pts - (cy_, cx_)) ** 2).sum(1))
        labels[int(pts[q][0]), int(pts[q][1])] = j
    return grow(mask, labels, cost)


def border_counts(lab_):
    """{(a, b): shared edge length} for neighbouring labels > 0."""
    pairs = {}
    for a_, b_ in ((lab_[:, :-1], lab_[:, 1:]), (lab_[:-1, :], lab_[1:, :])):
        m_ = (a_ != b_) & (a_ > 0) & (b_ > 0)
        for x_, y_ in zip(a_[m_].tolist(), b_[m_].tolist()):
            key = (min(x_, y_), max(x_, y_))
            pairs[key] = pairs.get(key, 0) + 1
    return pairs



# ---------------------------------------------------------------- provinces and states, district by district
landmark_px = [(nm, *place_px(la, lo)) for nm, la, lo in LANDMARKS]


def refine(lab_, m, cost, built, names, kinds, origin, sizes_):
    """Split pieces that are too big (or too long for the engine) along the terrain, then merge slivers and
    stray bits into the neighbour they share the longest border with; repeat until nothing changes.
    sizes_ = (target, largest, smallest) px; built-up land in an outer district uses the middle sizes."""
    target, largest, smallest = sizes_
    nl = int(lab_.max())
    for _ in range(12):
        changed = False
        for j, bb in enumerate(ndi.find_objects(lab_), 1):
            if bb is None:
                continue
            pm = lab_[bb] == j
            area = int(pm.sum())
            b_ = built[bb][pm].mean()      # dense city: smaller provinces, open land: bigger ones
            mid = SIZES["middle"]
            t_, l_ = ((min(target, mid[0]), min(largest, mid[1])) if b_ >= 0.4 else
                      (max(target, mid[0]), max(largest, mid[1])) if b_ < 0.15 else (target, largest))
            if area <= l_ and max(bb[0].stop - bb[0].start, bb[1].stop - bb[1].start) <= MAX_BOX:
                continue
            n = max(2, int(np.ceil(area / t_)))
            parts = split_organic(pm, n, cost[bb])
            for part in range(2, n + 1):
                nl += 1
                lab_[bb][parts == part] = nl
                names[nl], kinds[nl], origin[nl] = None, kinds.get(j), origin.get(j)
            changed = True
        for j, bb in enumerate(ndi.find_objects(lab_), 1):
            if bb is None:
                continue
            pad = (slice(max(bb[0].start - 1, 0), bb[0].stop + 1), slice(max(bb[1].start - 1, 0), bb[1].stop + 1))
            sub = lab_[pad]
            cl, n = ndi.label(sub == j)
            if n == 0:
                continue
            sizes = np.bincount(cl.ravel())
            main = int(sizes[1:].argmax()) + 1
            # a named housing estate, quarter or village stays a province down to 100 px (Lyulin Centre)
            keep_from = 100 if names.get(j) and kinds.get(j) in RESIDENTIAL else smallest
            pieces = [c for c in range(1, n + 1) if c != main] + ([main] if sizes[main] < keep_from else [])
            for c in pieces:
                piece = cl == c
                ring = ndi.binary_dilation(piece) & ~piece & m[pad] & (sub != j) & (sub > 0)
                if not ring.any():
                    continue
                py_, px_ = np.nonzero(piece)
                py_, px_ = py_ + pad[0].start, px_ + pad[1].start
                best_t, best_n = None, 0
                for t, cnt in zip(*np.unique(sub[ring], return_counts=True)):
                    ty_, tx_ = np.nonzero(lab_ == t)   # the merged province must still fit the engine's box
                    h_ = max(ty_.max(), py_.max()) - min(ty_.min(), py_.min()) + 1
                    w_ = max(tx_.max(), px_.max()) - min(tx_.min(), px_.min()) + 1
                    if max(h_, w_) <= MAX_BOX and cnt > best_n:
                        best_t, best_n = int(t), cnt
                if best_t is None:
                    continue
                sub[piece] = best_t
                if c == main and names.get(j) and not names.get(best_t):
                    names[best_t], kinds[best_t] = names[j], kinds.get(j)
                changed = True
        if not changed:
            break
    return lab_


prov = np.zeros((H, W), np.int32)
prov_district, prov_name, prov_kvtype, prov_partial = {}, {}, {}, set()
states = []           # [{"district", "provinces" (main province first), "name", "country_capital"}]
next_id = 1
for k in DISTRICTS:
    target, largest, smallest = SIZES[size_class(k)]
    dm = dist == k
    ys_, xs_ = np.nonzero(dm)
    sl = (slice(ys_.min() - 1, ys_.max() + 2), slice(xs_.min() - 1, xs_.max() + 2))
    m = dm[sl]
    cost = COST[sl]
    kv = np.where(m, KVR[sl], 0)
    # 1. pieces of the real neighbourhoods inside the district. A neighbourhood keeps its plain name in the
    #    district that holds most of it; a sizeable piece elsewhere is called after its side ("West Lozenets").
    lab_ = np.zeros(m.shape, np.int32)
    names, kinds, partial, origin = {}, {}, set(), {}
    for kvid in np.unique(kv[kv > 0]):
        cl, n = ndi.label(kv == kvid)
        sizes = np.bincount(cl.ravel())
        for c in range(1, n + 1):
            if sizes[c] < 40:
                continue
            j = int(lab_.max()) + 1
            lab_[cl == c] = j
            names[j], kinds[j], origin[j] = None, kv_info[kvid][1], kvid
            nm = kv_info[kvid][0]
            if nm and (nm, k) in KV_PIECE_NAMES and sizes[c] == sizes[1:].max():
                names[j] = KV_PIECE_NAMES[(nm, k)]
            elif nm and kv_home[kvid][0] == k and sizes[c] == sizes[1:].max():
                names[j] = nm
            elif nm and sizes[c] >= smallest and kv_info[kvid][1] in RESIDENTIAL + ("3", "4", "5.1", "5.2"):
                pcy, pcx = np.argwhere(cl == c).mean(0) + (sl[0].start, sl[1].start)
                dy, dx = pcy - KV_CY[kvid], pcx - KV_CX[kvid]
                side = ("East" if dx > 0 else "West") if abs(dx) > abs(dy) else ("South" if dy > 0 else "North")
                names[j] = f"{side} {nm}"
                partial.add(j)
    if lab_.max() == 0:
        lab_ = split_organic(m, max(2, int(m.sum() // target)), cost)
    # 2. land that belongs to no neighbourhood (fields, forest, mountain) joins the nearest one along the terrain
    lab_ = grow(m, lab_, cost)
    # 3. right sizes, organic borders
    lab_ = refine(lab_, m, cost, BUILT[sl], names, kinds, origin, SIZES[size_class(k)])
    ids = [j for j, bb in enumerate(ndi.find_objects(lab_), 1) if bb is not None]
    if len(ids) < 2:   # every country gets at least two states, so at least two provinces
        parts = split_organic(lab_ == ids[0], 2, cost)
        j = int(lab_.max()) + 1
        lab_[parts == 2] = j
        names[j], kinds[j] = None, kinds.get(ids[0])
        ids.append(j)
    lut_ = np.zeros(int(lab_.max()) + 1, np.int32)
    for j in ids:
        lut_[j] = next_id
        prov_district[next_id] = k
        prov_name[next_id] = names.get(j)
        prov_kvtype[next_id] = kinds.get(j)
        if j in partial and names.get(j):
            prov_partial.add(next_id)
        next_id += 1
    glab = lut_[lab_]
    prov[sl][m] = glab[m]
    for nm, lx, ly in landmark_px:   # a landmark beats no name and beats a "West Lozenets" kind of name
        yy, xx = int(round(ly)) - sl[0].start, int(round(lx)) - sl[1].start
        if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and glab[yy, xx] > 0:
            q = int(glab[yy, xx])
            if not prov_name[q] or q in prov_partial:
                prov_name[q] = nm
                prov_partial.discard(q)
    # unnamed built-up pieces of a split housing estate or quarter are named after their side of it
    for j in ids:
        q, kvid = int(lut_[j]), origin.get(j)
        if prov_name[q] or kvid is None or kv_info[kvid][1] != "1" or not kv_info[kvid][0]:
            continue
        pm = glab == q
        if BUILT[sl][pm].mean() < 0.3:
            continue
        pcy, pcx = np.argwhere(pm).mean(0) + (sl[0].start, sl[1].start)
        dy, dx = pcy - KV_CY[kvid], pcx - KV_CX[kvid]
        side = ("East" if dx > 0 else "West") if abs(dx) > abs(dy) else ("South" if dy > 0 else "North")
        nm = f"{side} {kv_info[kvid][0]}"
        if nm not in prov_name.values():
            prov_name[q] = nm
            prov_partial.add(q)
    # 4. states: neighbouring provinces grouped around the main neighbourhoods. Seeds: the capital, then again
    #    and again the province farthest (through the province graph) from every seed so far, favouring named,
    #    built-up places. States grow from their seeds, a big state more slowly than a small one, and every seed
    #    but the capital moves to the middle of its state a few times: compact states of similar size.
    plist = [int(lut_[j]) for j in ids]
    cents = {p: np.argwhere(glab == p).mean(0) for p in plist}
    builtp = {p: float(BUILT[sl][glab == p].sum()) for p in plist}
    nb = border_counts(glab)
    nbl = {p: set() for p in plist}
    for a, b in nb:
        nbl[a].add(b)
        nbl[b].add(a)
    idx_of = {p: i for i, p in enumerate(plist)}
    rows = [idx_of[a] for a, b in nb] + [idx_of[b] for a, b in nb]
    cols = [idx_of[b] for a, b in nb] + [idx_of[a] for a, b in nb]
    wts = [float(np.hypot(*(cents[a] - cents[b]))) + 1 for a, b in nb] * 2
    pgraph = coo_matrix((wts, (rows, cols)), shape=(len(plist), len(plist))).tocsr()
    pd = dijkstra(pgraph, directed=False)
    pd[~np.isfinite(pd)] = 1e9
    n_states = int(np.clip(round(len(plist) / PROVINCES_PER_STATE[size_class(k)]), 3 if len(plist) >= 9 else 2, 12))
    # the capital: the neighbourhood the district is named after ("Mladost 1" for Mladost), else the housing
    # estate, quarter or village nearest to the district's real centre
    cx_, cy_ = place_px(*CAPITALS[k])
    cap_local = np.array((cy_ - sl[0].start, cx_ - sl[1].start))
    dname = DISTRICTS[k][1]
    homes = [p for p in plist if prov_name[p] and prov_kvtype[p] in RESIDENTIAL and p not in prov_partial]
    def named_as(test):
        return [p for p in homes if test(prov_name[p])]

    cands = (named_as(lambda n: n == CAPITAL_NAMES.get(k)) or named_as(lambda n: n == dname)
             or named_as(lambda n: n == dname + " Centre") or named_as(lambda n: n == dname + " 1")
             or named_as(lambda n: n.startswith(dname + " ")) or homes or plist)
    first = min(cands, key=lambda q: np.hypot(*(cents[q] - cap_local)))
    weight = {p: (1.6 if prov_name[p] and prov_kvtype[p] in RESIDENTIAL else 1.2 if prov_name[p] else 1.0)
              * (1 + builtp[p] / 400) for p in plist}
    seeds = [first]
    while len(seeds) < n_states:
        dmin = pd[[idx_of[s] for s in seeds]].min(0)
        seeds.append(max((p for p in plist if p not in seeds), key=lambda p: dmin[idx_of[p]] * weight[p] ** 0.35))
    per_state = len(plist) / n_states

    def grow_states(seeds_):
        owner_, size_, heap = {s: s for s in seeds_}, {s: 1 for s in seeds_}, []

        def push(s, q):
            d_ = pd[idx_of[s], idx_of[q]]
            heapq.heappush(heap, (d_ * (1 + size_[s] / per_state) ** 2, d_, s, q, size_[s]))

        for s in seeds_:
            for q in nbl[s]:
                if q not in owner_:
                    push(s, q)
        while heap:
            _, d_, s, q, sz = heapq.heappop(heap)
            if q in owner_:
                continue
            if sz != size_[s]:      # the state grew since: queue again at its current size
                push(s, q)
                continue
            owner_[q] = s
            size_[s] += 1
            for r in nbl[q]:
                if r not in owner_:
                    push(s, r)
        for p in plist:             # cut off from every seed: nearest one
            owner_.setdefault(p, min(seeds_, key=lambda s: pd[idx_of[s], idx_of[p]]))
        return owner_

    for _ in range(6):
        owner = grow_states(seeds)
        moved = [first]
        for s in seeds[1:]:
            members = [p for p in plist if owner[p] == s]
            mi = [idx_of[q] for q in members]
            moved.append(min(members, key=lambda q: pd[idx_of[q], mi].sum()))
        if moved == seeds:
            break
        seeds = moved
    owner = grow_states(seeds)

    def importance(p):
        t = prov_kvtype[p]
        return (2 if t in RESIDENTIAL else 1 if t in ("4", "5.1", "5.2") else 0, p not in prov_partial, builtp[p])

    for s in seeds:   # the state's main place: its most important named place
        members = [p for p in plist if owner[p] == s]
        named = [p for p in members if prov_name[p]]
        main = s if s == first or not named else max(named, key=lambda p: (importance(p), p == s))
        states.append({"district": k, "provinces": [main] + [p for p in members if p != main],
                       "country_capital": s == first})

# Per-province sums for the rest of the script: pixel count, centre, elevation, forest and built-up land.
_yy, _xx = np.nonzero(prov)
_pv = prov[_yy, _xx]
P_AREA = np.bincount(_pv, minlength=next_id).astype(np.float64)
P_CY = np.bincount(_pv, weights=_yy, minlength=next_id) / np.maximum(P_AREA, 1)
P_CX = np.bincount(_pv, weights=_xx, minlength=next_id) / np.maximum(P_AREA, 1)
P_ELEV = np.bincount(_pv, weights=ELEV[_yy, _xx], minlength=next_id)
P_TREES = np.bincount(_pv, weights=TREES[_yy, _xx], minlength=next_id)
P_BUILT = np.bincount(_pv, weights=BUILT[_yy, _xx], minlength=next_id)
del _yy, _xx, _pv


def state_sum(st, arr):
    return float(sum(arr[p] for p in st["provinces"]))


# State names: the capital state carries the country's name, the others the name of their main place.
# A state with no named place is named after the nearest one and its land ("Bistritsa Heights").
named_all = [p for p in prov_name if prov_name[p] and p not in prov_partial
             and prov_kvtype[p] in RESIDENTIAL + ("4", "5.1", "5.2")]
used_names = {}          # state name -> district
for st in sorted(states, key=lambda s: not s["country_capital"]):
    k = st["district"]
    country = DISTRICTS[k][1]

    def variants(nm, quarter=False):
        """The name itself, or when another state has it: "X Quarter" in the same country, "X (Country)"."""
        if nm not in used_names:
            return [nm]
        return ([f"{nm} Quarter"] if quarter and used_names[nm] == k else []) + [f"{nm} ({country})"]

    if st["country_capital"]:
        options = [country]
    else:
        options = []
        for p in st["provinces"]:
            if prov_name[p]:
                options += variants(prov_name[p], prov_kvtype[p] == "1" and p not in prov_partial)
        area_ = state_sum(st, P_AREA)
        elev_, forest_ = state_sum(st, P_ELEV) / area_, state_sum(st, P_TREES) / area_
        built_ = state_sum(st, P_BUILT) / area_
        industry_ = sum(P_AREA[p] for p in st["provinces"] if prov_kvtype[p] == "2") / area_
        land_ = ("Industrial Zone" if industry_ > 0.5 else "Quarter" if built_ > 0.35 else "Heights" if elev_ > 1100
                 else "Woods" if forest_ > 0.5 else "Hills" if elev_ > 750 else "Fields")
        cy_ = sum(P_CY[p] * P_AREA[p] for p in st["provinces"]) / area_
        cx_ = sum(P_CX[p] * P_AREA[p] for p in st["provinces"]) / area_
        near = sorted((p for p in named_all if prov_district[p] == k and p not in st["provinces"]),
                      key=lambda p: np.hypot(P_CY[p] - cy_, P_CX[p] - cx_))
        options += [f"{prov_name[p].removesuffix(' Villas')} {land_}" for p in near[:4]]
        options += [f"{country} {land_}"]
    name_ = next((o for o in options if o not in used_names), None)
    if name_ is None:
        base = options[0]
        name_ = next(f"{base} {r}" for r in ("II", "III", "IV", "V", "VI", "VII", "VIII") if f"{base} {r}" not in used_names)
    used_names[name_] = k
    st["name"] = name_
print(f"{next_id - 1} land provinces in {len(states)} states")

# ---------------------------------------------------------------- the land around the city: impassable lakes
sea_mask = np.zeros((H, W), bool)
sea_mask[:SEA_BOX, :SEA_BOX] = True        # top-left corner, far away from the city
void = ~city & ~sea_mask
# The land around the city is cut into impassable lake provinces the same way as the city: they grow from
# well-spread seeds over the real terrain with a noisy cost, at half resolution to keep the build quick.
F = 2
small_void = void[::F, ::F]
_pts = np.argwhere(small_void).astype(np.float32)
_sample = _pts[RNG.choice(len(_pts), 60000, replace=False)]
_cen = _sample[RNG.choice(len(_sample), int(round(len(_pts) * F * F / LAKE_TARGET)), replace=False)].copy()
for _ in range(12):
    _a = cKDTree(_cen).query(_sample, workers=-1)[1]
    for j in range(len(_cen)):
        if (_a == j).any():
            _cen[j] = _sample[_a == j].mean(0)
_seed = np.unique(cKDTree(_pts).query(_cen, workers=-1)[1])
lab_c = np.zeros(small_void.shape, np.int32)
lab_c[_pts[_seed, 0].astype(int), _pts[_seed, 1].astype(int)] = np.arange(1, len(_seed) + 1)
_noise = np.zeros(small_void.shape, np.float32)
for sigma, amp in ((1.5, 0.30), (5.0, 0.40), (14.0, 0.30)):
    n_ = ndi.gaussian_filter(RNG.normal(0, 1, _noise.shape).astype(np.float32), sigma, mode="wrap")
    _noise += amp * n_ / (np.abs(n_).max() + 1e-6)
_noise = (_noise - _noise.min()) / (_noise.max() - _noise.min())
cost_void_c = 1.0 + 8.0 * _noise ** 2 + 15.0 * np.clip(SLOPE[::F, ::F], 0, 1)
lab_c = grow(small_void, lab_c, cost_void_c)
COST_VOID = np.repeat(np.repeat(cost_void_c, F, 0), F, 1)[:H, :W]
lab = np.repeat(np.repeat(lab_c, F, 0), F, 1)[:H, :W].copy()
lab[~void] = 0
del _pts, _sample, _cen, _a, _seed, _noise, lab_c, cost_void_c
for _ in range(6):
    holes = void & (lab == 0)
    if holes.any():
        idx = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
        lab[holes] = lab[idx[0], idx[1]][holes]
    changed = False
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        cl, n = ndi.label(lab[sl] == j)
        sizes = np.bincount(cl.ravel())
        keep = sizes[1:].argmax() + 1
        drop = (cl > 0) & ((cl != keep) | (sizes[keep] < 100))
        if drop.any():
            lab[sl][drop] = 0
            changed = True
    if not changed and not (void & (lab == 0)).any():
        break
holes = void & (lab == 0)
if holes.any():
    idx = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    lab[holes] = lab[idx[0], idx[1]][holes]
lake_ids = []
for j, sl in enumerate(ndi.find_objects(lab), 1):
    if sl is None:
        continue
    prov[sl][lab[sl] == j] = next_id
    prov_district[next_id] = 0
    lake_ids.append(next_id)
    next_id += 1
for _ in range(5):                 # a lake too big for the engine is split in two along the terrain
    lake_slices = ndi.find_objects(prov)
    too_big = [q for q in lake_ids if max(z.stop - z.start for z in lake_slices[q - 1]) > LAKE_MAX_BOX]
    if not too_big:
        break
    for q in too_big:
        sl = lake_slices[q - 1]
        m = prov[sl] == q
        parts = split_organic(m, 2, COST_VOID[sl])
        prov[sl][parts == 2] = next_id
        prov_district[next_id] = 0
        lake_ids.append(next_id)
        next_id += 1
prov[sea_mask] = next_id
prov_district[next_id] = -1                # -1 = sea
sea_id = next_id
next_id += 1
n_prov = next_id - 1



def fix_x_crossings():
    """HOI4 rejects "X crossings": 2x2 pixel blocks where four different provinces meet. The map wraps
    around horizontally, so the last column also forms blocks with the first one."""
    found = False
    for _ in range(10):
        pw_ = np.concatenate([prov, prov[:, :1]], axis=1)
        a, b, c_, d = pw_[1:, :-1], pw_[1:, 1:], pw_[:-1, :-1], pw_[:-1, 1:]
        xc = (a != b) & (a != c_) & (a != d) & (b != c_) & (b != d) & (c_ != d)
        if not xc.any():
            break
        found = True
        for y, x in np.argwhere(xc):
            prov[y + 1, x] = prov[y, x]  # bottom-left pixel joins the one above (never across the seam)
    return found


def join_stray_pieces():
    """Every province must be one piece: a stray bit joins the neighbour of the same kind (same district,
    or lake to lake) it shares the longest border with."""
    found = False
    for q, sl in enumerate(ndi.find_objects(prov), 1):
        if sl is None:
            continue
        pad = (slice(max(sl[0].start - 1, 0), sl[0].stop + 1), slice(max(sl[1].start - 1, 0), sl[1].stop + 1))
        sub = prov[pad]
        cl, n = ndi.label(sub == q)
        if n < 2:
            continue
        found = True
        main = np.bincount(cl.ravel())[1:].argmax() + 1
        for c in range(1, n + 1):
            if c == main:
                continue
            piece = cl == c
            ring = sub[ndi.binary_dilation(piece) & ~piece & (sub != q)]
            same = ring[np.array([prov_district.get(int(r)) == prov_district[q] for r in ring], bool)]
            pool = same if same.size else ring
            if pool.size:
                sub[piece] = np.bincount(pool).argmax()
    return found


for _ in range(5):
    if not (fix_x_crossings() | join_stray_pieces()):
        break
land_ids = [p for p, d_ in prov_district.items() if d_ > 0]
prov_slices = ndi.find_objects(prov)

# centroids (a pixel near the middle, always inside the province)
cent = {}
for p, sl in enumerate(prov_slices, 1):
    if sl is None:
        continue
    py, px = np.nonzero(prov[sl] == p)
    py, px = py + sl[0].start, px + sl[1].start
    i = np.argmin((py - py.mean()) ** 2 + (px - px.mean()) ** 2)
    cent[p] = (int(px[i]), int(py[i]))

# ---------------------------------------------------------------- province terrain (gameplay)
prov_terrain = {}
for p in land_ids:
    sl = prov_slices[p - 1]
    m = prov[sl] == p
    mount = MOUNT[sl][m].mean()
    built = BUILT[sl][m].mean()
    forest = (TREES[sl] & ~MOUNT[sl])[m].mean()
    hills = (HILL[sl] & ~MOUNT[sl])[m].mean()
    if mount >= 0.35:
        prov_terrain[p] = "mountain"
    elif built >= 0.30:
        prov_terrain[p] = "plains"          # where the houses are
    elif forest >= 0.50:
        prov_terrain[p] = "forest"
    elif hills >= 0.40:
        prov_terrain[p] = "hills"
    elif forest >= 0.35:
        prov_terrain[p] = "forest"
    else:
        prov_terrain[p] = "plains"

# ---------------------------------------------------------------- states: ids, capitals, cities
states.sort(key=lambda s: (s["district"], not s["country_capital"]))
state_of = {}
for sid, st in enumerate(states, 1):
    st["id"] = sid
    for p in st["provinces"]:
        state_of[p] = sid
state_lut = np.zeros(n_prov + 1, np.int32)
for st in states:
    state_lut[st["provinces"]] = st["id"]
state_map = state_lut[prov]
state_slices = ndi.find_objects(state_map)
country_capital_state = {st["district"]: st["id"] for st in states if st["country_capital"]}
capital = {st["district"]: st["provinces"][0] for st in states if st["country_capital"]}
vp = {}            # province id -> (name, victory points)
for st in states:
    k = st["district"]
    cap = st["provinces"][0]
    city_name = prov_name[cap] or st["name"]
    if not st["country_capital"] and st["name"].startswith(city_name + " "):
        city_name = st["name"]          # "Kremikovtsi Quarter": told apart from the country's capital
    vp[cap] = (city_name, CAPITAL_VP.get(k, 10) if st["country_capital"] else 3)
    for p in st["provinces"][1:]:
        if prov_name[p] and prov_kvtype[p] in RESIDENTIAL:
            vp[p] = (prov_name[p], 1)
# A city name used in two countries (three quarters are called Izgrev): the lesser ones get their country's name.
_by_name = {}
for p, (nm, v) in vp.items():
    _by_name.setdefault(nm, []).append(p)
for nm, ps in _by_name.items():
    ps.sort(key=lambda p: (-vp[p][1], p))
    for p in ps[1:]:
        if prov_district[p] != prov_district[ps[0]]:
            vp[p] = (f"{nm} ({DISTRICTS[prov_district[p]][1]})", vp[p][1])

# ---------------------------------------------------------------- provinces.bmp + definition.csv
used = set()
colors = {}
for p in range(1, n_prov + 1):
    while True:
        c = tuple(int(v) for v in RNG.integers(16, 256, 3))
        if c not in used:
            used.add(c)
            colors[p] = c
            break
lut = np.zeros((n_prov + 1, 3), np.uint8)
for p, c in colors.items():
    lut[p] = c
Image.fromarray(lut[prov], "RGB").save(out("map/provinces.bmp"))

adj = set()
for a, b in ((prov[:, :-1], prov[:, 1:]), (prov[:-1, :], prov[1:, :])):
    d = a != b
    for x, y in set(zip(a[d].tolist(), b[d].tolist())):
        adj.add((min(x, y), max(x, y)))

lines = ["0;0;0;0;land;false;unknown;0"]
for p in range(1, n_prov + 1):
    r, g, b = colors[p]
    if prov_district[p] > 0:
        lines.append(f"{p};{r};{g};{b};land;false;{prov_terrain[p]};1")
    elif prov_district[p] < 0:
        lines.append(f"{p};{r};{g};{b};sea;false;ocean;0")
    else:
        lines.append(f"{p};{r};{g};{b};lake;false;lakes;0")
write("map/definition.csv", "\n".join(lines) + "\n")

# ---------------------------------------------------------------- heightmap and normal map from the real elevation
# 96 is the lowest land value; 300 m -> 96, 2700 m and above -> 251, compressed so lowland relief shows.
E0, E1 = 300.0, 2700.0
height_f = 96 + 155 * np.clip((ELEV_S - E0) / (E1 - E0), 0, 1) ** 0.75
heightmap = np.clip(np.round(ndi.gaussian_filter(height_f, 0.8)), 96, 255).astype(np.uint8)
del height_f
heightmap[WATER] = 92                          # real lakes and reservoirs render as water
heightmap[sea_mask] = 89
Image.fromarray(heightmap, "L").save(out("map/heightmap.bmp"))

# Normal map (half size) from the real slopes, exaggerated so hills and valleys read clearly. Red = east,
# green = north, blue = up (Paradox map shaders read the normal map as .rbg).
EXAG = 3.0
nrm = np.dstack([-slope_x * EXAG, slope_y * EXAG, np.ones((H, W), np.float32)])
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
nrm_img = ((nrm * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
Image.fromarray(nrm_img, "RGB").resize((W // 2, H // 2), Image.BOX).save(out("map/world_normal.bmp"))
del nrm, nrm_img


def write_dds_bgra(path, rgba):
    """Uncompressed A8R8G8B8 DDS without mipmaps (the layout of a generated map verified to run on 1.19)."""
    h_, w_ = rgba.shape[:2]
    header = struct.pack("<4s7I44s8I5I", b"DDS ", 124, 0x100F, h_, w_, w_ * 4, 0, 0, bytes(44),
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0, 0, 0, 0)
    with open(out(path), "wb") as f:
        f.write(header)
        f.write(rgba[..., [2, 1, 0, 3]].tobytes())


def solid_dds(path, size, rgba):
    img = np.zeros((size[1], size[0], 4), np.uint8)
    img[...] = rgba
    write_dds_bgra(path, img)


# Map-shaped textures. Vanilla's are paintings of the Earth, so they are replaced with one colour each,
# sampled from the stock files: ground tint, fog of war / water shine, and the three water colour maps.
solid_dds("map/terrain/colormap_rgb_cityemissivemask_a.dds", (W // 2, H // 2), (78, 86, 62, 0))
solid_dds("map/terrain/fow_rgb_waterspec_a.dds", (W // 2, H // 2), (131, 132, 131, 27))
for level in range(3):
    solid_dds(f"map/terrain/colormap_water_{level}.dds", (W // 2 ** (level + 1), H // 2 ** (level + 1)),
              (20, 28, 63, 255))


# ---------------------------------------------------------------- indexed bitmaps
def indexed(arr, palette):
    im = Image.fromarray(arr.astype(np.uint8), "P")
    im.putpalette(list(palette) + [0] * (768 - len(palette)))
    return im


gray = [v for i in range(256) for v in (i, i, i)]
tmap = np.full((H, W), TEX_PLAINS, np.uint8)
tmap[LC == 40] = TEX_FIELDS
tmap[HILL] = TEX_HILLS
tmap[TREES] = TEX_FOREST
tmap[TREES & (ELEV > 1100)] = TEX_FOREST_HIGH
tmap[MOUNT & ~TREES] = TEX_ROCK
tmap[(ELEV > 2500) & ~TREES] = TEX_SNOW
tmap[LC == 90] = TEX_MARSH
tmap[BUILT & ~MOUNT] = TEX_PLAINS      # whole built-up areas with houses made the game lag
tmap[WATER] = TEX_LAKE
tmap[sea_mask] = 15                    # ocean
for p, (nm, val) in vp.items():        # houses around every city instead
    cx_, cy_ = cent[p]
    r_ = 8 if val >= 10 else 6 if val >= 3 else 4
    sl = (slice(max(cy_ - r_, 0), cy_ + r_ + 1), slice(max(cx_ - r_, 0), cx_ + r_ + 1))
    yy_, xx_ = np.mgrid[sl]
    houses = ((xx_ - cx_) ** 2 + (yy_ - cy_) ** 2 <= r_ * r_) & (prov[sl] == p) & ~WATER[sl]
    tmap[sl][houses] = TEX_CITY
indexed(tmap, gray).save(out("map/terrain.bmp"))
# cities.bmp picks the city model group: 0 would be asia_city (a few buildings scattered over the whole map),
# 4 is no group at all, 15 the western cities group, used for the house patches.
cities_idx = np.full((H, W), 4, np.uint8)
cities_idx[tmap == TEX_CITY] = 15
indexed(cities_idx, gray).save(out("map/cities.bmp"))

# trees.bmp (1650x600 for the vanilla-sized map): palette indices 3 and 4 are trees
tw_t, th_t = round(W * 1650 / 5632), round(H * 600 / 2048)
frac = np.asarray(Image.fromarray(TREES.astype(np.float32)).resize((tw_t, th_t), Image.BOX))
high = np.asarray(Image.fromarray((ELEV > 1100).astype(np.float32)).resize((tw_t, th_t), Image.BOX))
# Tree models cost performance: dense ones in and right around the city, a light sprinkle further out.
near = np.asarray(Image.fromarray((ndi.distance_transform_edt(~city) < 120).astype(np.float32))
                  .resize((tw_t, th_t), Image.BOX)) > 0.5
keep = np.where(near, frac > 0.5, (frac > 0.7) & (RNG.random((th_t, tw_t)) < 0.25))
trees = np.zeros((th_t, tw_t), np.uint8)
trees[keep] = 4
trees[keep & (high > 0.5)] = 3
trees[:SEA_BOX * th_t // H + 1, :SEA_BOX * tw_t // W + 1] = 0
indexed(trees, gray).save(out("map/trees.bmp"))

river_pal = gray[:]
river_pal[0:3] = [0, 255, 0]
river_pal[3:6] = [255, 0, 0]
river_pal[254 * 3:254 * 3 + 3] = [122, 122, 122]
river_pal[255 * 3:255 * 3 + 3] = [255, 255, 255]
indexed(river, river_pal).save(out("map/rivers.bmp"))


# ---------------------------------------------------------------- default.map & misc map files
def pos(x, y):
    return f"{x:.2f};{heightmap[y, x] / 10.0:.2f};{H - 1 - y:.2f}"


def world(p):
    x, y = cent[p]
    return x, heightmap[y, x] / 10.0, H - 1 - y


write("map/default.map", """definitions = "definition.csv"
provinces = "provinces.bmp"
positions = "positions.txt"
terrain = "terrain.bmp"
rivers = "rivers.bmp"
heightmap = "heightmap.bmp"
tree_definition = "trees.bmp"
continent = "continent.txt"
adjacency_rules = "adjacency_rules.txt"
adjacencies = "adjacencies.csv"
#climate = "climate.txt"
ambient_object = "ambient_object.txt"
seasons = "seasons.txt"

# Define which indices in trees.bmp palette which should count as trees for automatic terrain assignment
tree = { 3 4 7 10 }
""")
cxm, cym = ox + tw / 2, oy + th / 2           # middle of the city in map pixels
write("common/defines/zz_evil_sofia_defines.lua", f"""-- Evil Sofia: defines for a city-sized map. Only keys the game already has are changed.
local function set(tbl, ns, key, value)
\tif tbl ~= nil and tbl[ns] ~= nil and tbl[ns][key] ~= nil then
\t\ttbl[ns][key] = value
\tend
end
-- One map pixel is about {M_PER_PX:.0f} m in reality; 1.5 km per pixel keeps unit movement close to vanilla pacing.
set(NDefines, "NGame", "MAP_SCALE_PIXEL_TO_KM", 1.5)
-- The main menu camera looks at the city.
for _, tbl in ipairs({{NDefines, NDefines_Graphics}}) do
\tset(tbl, "NFrontend", "CAMERA_LOOKAT_X", {cxm:.1f})
\tset(tbl, "NFrontend", "CAMERA_LOOKAT_Z", {H - cym:.1f})
\tset(tbl, "NFrontend", "CAMERA_START_X", {cxm:.1f})
\tset(tbl, "NFrontend", "CAMERA_START_Z", {H - cym - 120:.1f})
\tset(tbl, "NFrontend", "CAMERA_END_X", {cxm:.1f})
\tset(tbl, "NFrontend", "CAMERA_END_Z", {H - cym - 120:.1f})
end
""")
write("map/positions.txt", "")
# Keep the vanilla continent names: portraits and AI files refer to them. Sofia counts as europe (index 1).
write("map/continent.txt", "continents = {\n" + "".join(f"\t{c}\n" for c in ("europe", "north_america", "south_america", "australia", "africa", "asia", "middle_east")) + "}\n")
write("map/adjacencies.csv", "From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment\n-1;-1;;-1;-1;-1;-1;-1;-1\n")
write("map/adjacency_rules.txt", "")
# supply hubs: every country capital, plus the capitals of large outlying states
hubs = sorted(set(capital.values()) | {st["provinces"][0] for st in states if len(st["provinces"]) >= 5})
write("map/supply_nodes.txt", "".join(f"1 {p}\n" for p in hubs))


def state_spots(st, n):
    sl = state_slices[st["id"] - 1]
    m = state_map[sl] == st["id"]
    inner = ndi.binary_erosion(m, iterations=2)
    py, px = np.nonzero(inner if inner.sum() >= n else m)
    pick = RNG.choice(len(px), n, replace=len(px) < n)
    return [(int(px[i]) + sl[1].start, int(py[i]) + sl[0].start) for i in pick]


def province_spots(p, n):
    sl = prov_slices[p - 1]
    m = prov[sl] == p
    inner = ndi.binary_erosion(m, iterations=2)
    py, px = np.nonzero(inner if inner.sum() >= n else m)
    pick = RNG.choice(len(px), n, replace=len(px) < n)
    return [(int(px[i]) + sl[1].start, int(py[i]) + sl[0].start) for i in pick]


# Same building position types and counts as vanilla 1.19 buildings.txt. A state without an air base,
# rocket site or gun emplacement position is a fatal map error at scenario start.
STATE_BUILDINGS = {"arms_factory": 6, "industrial_complex": 6, "anti_air_building": 3, "air_base": 1,
                   "synthetic_refinery": 1, "radar_station": 1, "fuel_silo": 1, "stronghold_network": 1,
                   "nuclear_reactor_spawn": 1, "rocket_site_spawn": 1}
PROVINCE_BUILDINGS = ("bunker", "supply_node", "special_project_facility_spawn")
bl = []
for st in states:
    for b, n in STATE_BUILDINGS.items():
        for x, y in state_spots(st, n):
            bl.append(f"{st['id']};{b};{pos(x, y)};{RNG.uniform(0, 6.28):.2f};0")
    for p in st["provinces"]:
        for b, (x, y) in zip(PROVINCE_BUILDINGS, province_spots(p, len(PROVINCE_BUILDINGS))):
            bl.append(f"{st['id']};{b};{pos(x, y)};{RNG.uniform(0, 6.28):.2f};0")
write("map/buildings.txt", "\n".join(bl) + "\n")
# Unit-counter anchors. At match start the engine looks up a set of anchors for every land and sea province
# and dereferences them without checking; a missing one is a crash with no log line. These are the sets the
# stock unitstacks.txt supplies: 0 standstill, 1-2 moving, 9 attacking, 10 defending, 21-23 regrouping,
# 11-12 and 30-31 disembarking, 38 the victory point. Lakes have none, as in vanilla.
LAND_STACKS = (0, 1, 2, 9, 10, 21, 22, 23, 38)
SEA_STACKS = (0, 1, 2, 9, 10, 11, 12, 21, 22, 23, 30, 31, 38)
stack_lines = []
for p in land_ids + [sea_id]:
    for slot in (LAND_STACKS if p != sea_id else SEA_STACKS):
        stack_lines.append(f"{p};{slot};{pos(*cent[p])};0.00;0.30")
write("map/unitstacks.txt", "\n".join(stack_lines) + "\n")

# Railways: spanning tree over land neighbours, starting in Sredets.
land_adj = {p: set() for p in land_ids}
for a, b in adj:
    if prov_district.get(a, 0) > 0 and prov_district.get(b, 0) > 0:
        land_adj[a].add(b)
        land_adj[b].add(a)
seen, queue, rails = {capital[1]}, [capital[1]], []
while queue:
    a = queue.pop(0)
    for b in sorted(land_adj[a]):
        if b not in seen:
            seen.add(b)
            queue.append(b)
            rails.append(f"{3 if prov_district[a] <= 12 and prov_district[b] <= 12 else 2} 2 {a} {b}")
write("map/railways.txt", "\n".join(rails) + "\n")

write("map/supplyareas/1-Sofia.txt", f"""supply_area = {{
\tid = 1
\tname = "EVIL_SOFIA_SUPPLY_AREA"
\tvalue = 10
\tstates = {{
\t\t{' '.join(str(st['id']) for st in states)}
\t}}
}}
""")

# Strategic regions: by district, Pancharevo split north/south; each lake joins the nearest land region.
REGIONS = {rid: name for rid, name, _ in REGION_DEFS}
district_region = {k: rid for rid, _, ds in REGION_DEFS for k in ds}
pan_states = [st for st in states if st["district"] == 23]
pan_mid = np.median([np.mean([cent[p][1] for p in st["provinces"]]) for st in pan_states])
region_of = {}
for st in states:
    rid = district_region[st["district"]]
    if st["district"] == 23 and np.mean([cent[p][1] for p in st["provinces"]]) < pan_mid:
        rid = PANCHAREVO_NORTH_REGION
    st["region"] = rid
    for p in st["provinces"]:
        region_of[p] = rid
region_of[sea_id] = SEA_REGION[0]
empty = [rid for rid in REGIONS if rid not in region_of.values()]
if empty:
    raise SystemExit(f"strategic regions without land: {empty}")
nbrs = {p: set() for p in range(1, n_prov + 1)}
for a, b in adj:
    nbrs[a].add(b)
    nbrs[b].add(a)
land_pts = np.array([cent[p] for p in land_ids])
for p in lake_ids:
    region_of[p] = region_of[land_ids[int(np.argmin(((land_pts - cent[p]) ** 2).sum(1)))]]


def region_centre_unsafe(members):
    """HOI4 snaps each member box to a 2-px grid (y counted from the bottom), averages the box centres
    and, when that point is in no member box, divides by (mean.x - centre of the union box): zero there
    crashes the game while loading (INT_DIVIDE_BY_ZERO)."""
    boxes = []
    for q in members:
        sl = prov_slices[q - 1]
        xmin, xmax = sl[1].start, sl[1].stop - 1
        yb_min, yb_max = H - sl[0].stop, H - 1 - sl[0].start
        boxes.append((2 * (xmin // 2), 2 * (xmax // 2 + 1), 2 * (yb_min // 2), 2 * (yb_max // 2 + 1)))
    mx = sum((b_[0] + b_[1]) // 2 for b_ in boxes) // len(boxes)
    my = sum((b_[2] + b_[3]) // 2 for b_ in boxes) // len(boxes)
    if any(b_[0] + 1 <= mx < b_[1] - 1 and b_[2] + 1 <= my < b_[3] - 1 for b_ in boxes):
        return False
    rx0, rx1 = min(b_[0] for b_ in boxes), max(b_[1] for b_ in boxes)
    return abs(mx - (rx0 + (rx1 - rx0) / 2)) < 2


for rid in REGIONS:
    for _ in range(80):
        members = [p for p, r in region_of.items() if r == rid]
        if not region_centre_unsafe(members):
            break
        lakes_here = [p for p in members if prov_district[p] == 0]
        if lakes_here:
            far = max(lakes_here, key=lambda q: (cent[q][0] - W / 2) ** 2 + (cent[q][1] - H / 2) ** 2)
            region_of[far] = (rid % len(REGIONS)) + 1
            continue
        # no lake to hand over: give a border state to the neighbouring region instead
        st_, to = next((st, region_of[q]) for st in states if st["region"] == rid for p in st["provinces"]
                       for q in nbrs[p] if prov_district.get(q, 0) > 0 and region_of[q] != rid)
        st_["region"] = to
        for p in st_["provinces"]:
            region_of[p] = to
    else:
        raise SystemExit(f"strategic region {rid} keeps failing the region-centre check")

# Sofia monthly climate: (min temp, max temp, no_phenomenon, rain_light, rain_heavy, snow, blizzard, mud)
CLIMATE = [(-6, 3, .45, .05, 0, .35, .05, .10), (-4, 6, .45, .08, 0, .30, .02, .15),
           (-1, 11, .50, .20, .03, .12, 0, .15), (4, 16, .55, .30, .10, 0, 0, .05),
           (9, 21, .55, .30, .15, 0, 0, 0), (12, 25, .60, .25, .15, 0, 0, 0),
           (14, 28, .75, .15, .10, 0, 0, 0), (14, 28, .80, .12, .08, 0, 0, 0),
           (10, 23, .75, .15, .10, 0, 0, 0), (5, 17, .60, .25, .05, .02, 0, .08),
           (1, 10, .50, .25, .05, .10, 0, .10), (-4, 4, .45, .10, 0, .30, .05, .10)]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
weather = []
for mo, (tmin, tmax, nop, rl, rh, sn, bz, mud) in enumerate(CLIMATE):
    weather.append(f"""\t\tperiod = {{
\t\t\tbetween = {{ 0.{mo} {DAYS[mo] - 1}.{mo} }}
\t\t\ttemperature = {{ {tmin:.1f} {tmax:.1f} }}
\t\t\tno_phenomenon = {nop} rain_light = {rl} rain_heavy = {rh} snow = {sn} blizzard = {bz} arctic_water = 0 mud = {mud} sandstorm = 0
\t\t\tmin_snow_level = 0.0
\t\t}}""")
weather_txt = "\n".join(weather)
wpos = []
for rid, rname in list(REGIONS.items()) + [SEA_REGION]:
    provs = sorted(p for p, r in region_of.items() if r == rid)
    naval = "\n\tnaval_terrain = water_deep_ocean" if rid == SEA_REGION[0] else ""
    write(f"map/strategicregions/{rid}-{rname.replace(' ', '_')}.txt", f"""strategic_region = {{
\tid = {rid}
\tname = "EVIL_SOFIA_REGION_{rid}"
\tprovinces = {{
\t\t{' '.join(map(str, provs))}
\t}}{naval}
\tweather = {{
{weather_txt}
\t}}
}}
""")
    land_in = [p for p in provs if prov_district[p] > 0]
    x, h, z = world(min(land_in) if land_in else provs[0])
    wpos.append(f"{rid};{x:.2f};{h:.2f};{z:.2f};small")
write("map/weatherpositions.txt", "\n".join(wpos) + "\n")

# ---------------------------------------------------------------- states, countries, characters, localisation
# Every key is unique to the mod (vanilla's STATE_1, STRATEGICREGION_1... would win otherwise), and the file
# goes into localisation/english/replace, which also beats vanilla's VICTORY_POINTS_<province> names.
loc = ["l_english:", ' EVIL_SOFIA_START_NAME:0 "The Fall of Sofia"',
       ' EVIL_SOFIA_START_DESC:0 "1 January 1936. The city council of Sofia has collapsed overnight, and the mayor has fled. In the morning every district hall raises its own flag, every district guard hands out rifles, and every district leader looks at the map and counts the streets to the centre.\\n\\nTwenty-four districts. Twenty-four warlords. Only one will rule Sofia."']
for st in states:
    st["built"], st["area"] = state_sum(st, P_BUILT), state_sum(st, P_AREA)
for k, (tag, name, adj_, cat, pop) in DISTRICTS.items():
    mine = [st for st in states if st["district"] == k]
    weights = [st["built"] + 0.1 * st["area"] for st in mine]
    for st, w_ in zip(mine, weights):
        # The real population of the state's share of the district, times a random 100-200 per state, so the
        # districts can raise armies of a real war's size. Its own generator keeps the numbers fixed per build.
        st["pop_factor"] = int(POP_RNG.integers(100, 201))
        st["manpower"] = int(round(max(500, pop * w_ / sum(weights)) * st["pop_factor"], -3))
industry_state = {}
for k in (18,):   # the Kremikovtsi steelworks: the state with the most industrial-zone land
    mine = [st for st in states if st["district"] == k]
    industry_state[k] = max(mine, key=lambda st: sum(P_AREA[p] for p in st["provinces"] if prov_kvtype[p] == "2")
                            + st["built"] * 0.01)["id"]
for st in states:
    k = st["district"]
    tag, name, adj_, cat, pop = DISTRICTS[k]
    urban = st["built"] / max(st["area"], 1)
    if st["country_capital"]:
        category = cat
    else:
        category = ("city" if urban >= 0.55 else "large_town" if urban >= 0.30 else "town" if urban >= 0.12
                    else "rural" if urban >= 0.04 else "pastoral")
    infra = 5 if cat in ("megalopolis", "metropolis") else 4 if urban >= 0.3 else 3
    bld = f"infrastructure = {infra}"
    if st["country_capital"]:
        civ = {"megalopolis": 3, "metropolis": 2, "large_city": 2, "city": 1}.get(cat, 0)
        if civ:
            bld += f"\n\t\t\tindustrial_complex = {civ}"
    extra = ""
    if industry_state.get(k) == st["id"]:
        bld += "\n\t\t\tarms_factory = 3"
        extra = "\n\tresources = { steel = 12 }"
        if category in ("town", "rural", "pastoral"):
            category = "large_town"      # room for the steelworks' factories
    vp_lines = "\n".join(f"\t\tvictory_points = {{ {p} {vp[p][1]} }}" for p in st["provinces"] if p in vp)
    file_name = re.sub(r"[^A-Za-z0-9_-]", "", st["name"].replace(" ", "_"))
    write(f"history/states/{st['id']}-{tag}_{file_name}.txt", f"""state = {{
\tid = {st['id']}
\tname = "EVIL_SOFIA_STATE_{st['id']}"
\tmanpower = {st['manpower']}
\tstate_category = {category}{extra}

\thistory = {{
\t\towner = {tag}
\t\tadd_core_of = {tag}
{vp_lines}
\t\tbuildings = {{
\t\t\t{bld}
\t\t}}
\t}}

\tprovinces = {{
\t\t{' '.join(map(str, st['provinces']))}
\t}}
}}
""")
    loc.append(f' EVIL_SOFIA_STATE_{st["id"]}:0 "{st["name"]}"')
    loc += [f' VICTORY_POINTS_{p}:0 "{vp[p][0]}"' for p in st["provinces"] if p in vp]

tags_txt, bookmark_countries, name_lists, featured_entries = [], [], [], {}
for k, (tag, name, adj_, cat, pop) in DISTRICTS.items():
    r, g, b = country_color(k)
    file_name = name.replace(" ", "_")
    write(f"common/countries/{file_name}.txt", f"""graphical_culture = eastern_european_gfx
graphical_culture_2d = eastern_european_2d

color = {{ {r} {g} {b} }}
""")
    tags_txt.append(f'{tag} = "countries/{file_name}.txt"')
    leader = LEADER_NAMES.get(tag, f"{FIRST[2 * (k - 1)]} {SURNAMES[2 * (k - 1)]}")
    general = (FIRST[2 * (k - 1) + 1], SURNAMES[2 * (k - 1) + 1])
    def leader_portrait(src_name, dds_name):
        """Large leader portrait (156x210, uncompressed DDS) from tools/portraits/<src_name>.png, if it exists."""
        src = os.path.join(ROOT, "tools", "portraits", f"{src_name}.png")
        if not os.path.exists(src):
            return ""
        face = Image.open(src).convert("RGBA")
        fw, fh = face.size
        if fw * 210 > fh * 156:          # too wide: trim both sides
            nw = round(fh * 156 / 210)
            face = face.crop(((fw - nw) // 2, 0, (fw - nw) // 2 + nw, fh))
        elif fw * 210 < fh * 156:        # too tall: trim the bottom, keep the head
            face = face.crop((0, 0, fw, round(fw * 210 / 156)))
        face = face.resize((156, 210), Image.LANCZOS)
        write_dds_bgra(f"gfx/leaders/{tag}/{dds_name}.dds", np.asarray(face))
        return f"""
\t\tportraits = {{
\t\t\tcivilian = {{
\t\t\t\tlarge = "gfx/leaders/{tag}/{dds_name}.dds"
\t\t\t}}
\t\t}}"""

    portrait = leader_portrait(tag, f"{tag}_leader")
    extra_blocks = []   # characters that only appear through focuses (tools/texts.py EXTRA_CHARACTERS)
    for cid, cname, cdesc in _texts.EXTRA_CHARACTERS.get(tag, []):
        extra_blocks.append(f"\t{cid} = {{\n\t\tname = {cid}{leader_portrait(cid, cid)}\n"
                            f"\t\tcountry_leader = {{\n\t\t\tdesc = \"{cid}_desc\"\n\t\t\tideology = despotism\n"
                            f"\t\t\texpire = \"1965.1.1.1\"\n\t\t\tid = -1\n\t\t}}\n\t}}")
        loc += [f' {cid}:0 "{cname}"', f' {cid}_desc:0 "{cdesc}"']
    advisor_blocks = []
    for i, trait in enumerate(_texts.ADVISORS[tag], 1):
        cid = f"{tag}_advisor_{i}"
        slot = _texts.ADVISOR_TRAITS[trait][3]
        advisor_blocks.append(f"""\t{cid} = {{
\t\tname = {cid}
\t\tadvisor = {{
\t\t\tslot = {slot}
\t\t\tidea_token = {cid}
\t\t\tallowed = {{ original_tag = {tag} }}
\t\t\ttraits = {{ {trait} }}
\t\t\tcost = {100 if slot == "political_advisor" else 75}
\t\t\tai_will_do = {{ factor = 1 }}
\t\t}}
\t}}""")
        loc.append(f' {cid}:0 "{ADVISOR_NAMES.pop(0)}"')
    advisor_blocks = "\n".join(advisor_blocks)
    write(f"common/characters/{tag}.txt", f"""characters = {{
\t{tag}_leader = {{
\t\tname = {tag}_leader{portrait}
\t\tcountry_leader = {{
\t\t\tdesc = "{tag}_leader_desc"
\t\t\tideology = despotism{(chr(10) + chr(9) * 3 + "traits = { " + " ".join(LEADER_TRAITS[tag]) + " }") if tag in LEADER_TRAITS else ""}
\t\t\texpire = "1965.1.1.1"
\t\t\tid = -1
\t\t}}
\t}}
\t{tag}_general = {{
\t\tname = {tag}_general
\t\tcorps_commander = {{
\t\t\ttraits = {{ }}
\t\t\tskill = 3
\t\t\tattack_skill = 3
\t\t\tdefense_skill = 2
\t\t\tplanning_skill = 2
\t\t\tlogistics_skill = 2
\t\t\tlegacy_id = -1
\t\t}}
\t}}
{advisor_blocks}
{chr(10).join(extra_blocks)}
}}
""")
    write(f"history/countries/{tag} - {name}.txt", f"""capital = {country_capital_state[k]}

set_research_slots = 2
set_stability = 0.5
set_war_support = 0.5

set_politics = {{
\truling_party = neutrality
\tlast_election = "1932.1.1"
\telection_frequency = 48
\telections_allowed = no
}}
set_popularities = {{
\tdemocratic = 0
\tfascism = 0
\tcommunism = 0
\tneutrality = 100
}}

recruit_character = {tag}_leader
recruit_character = {tag}_general

oob = "{tag}_1936"

# A basic start like vanilla minor nations: no country starts without technology or an army.
set_technology = {{
\tinfantry_weapons = 1
\tinfantry_weapons1 = 1
\ttech_support = 1
\ttech_engineers = 1
\ttech_recon = 1
\tgw_artillery = 1
\tbasic_train = 1
}}
""")
    n_div = 1 + pop // 40000
    divisions = "\n".join(f"""\tdivision = {{
\t\tname = "{i + 1}{'st' if i == 0 else 'nd' if i == 1 else 'rd' if i == 2 else 'th'} {name} Guard"
\t\tlocation = {capital[k]}
\t\tdivision_template = "City Guard"
\t\tstart_experience_factor = 0.2
\t\tstart_equipment_factor = 1.0
\t}}""" for i in range(n_div))
    write(f"history/units/{tag}_1936.txt", f"""division_template = {{
\tname = "City Guard"
\tregiments = {{
\t\tinfantry = {{ x = 0 y = 0 }}
\t\tinfantry = {{ x = 0 y = 1 }}
\t\tinfantry = {{ x = 1 y = 0 }}
\t\tinfantry = {{ x = 1 y = 1 }}
\t}}
}}

units = {{
{divisions}
}}

instant_effect = {{
\tadd_equipment_to_stockpile = {{
\t\ttype = infantry_equipment_1
\t\tamount = 500
\t\tproducer = {tag}
\t}}
}}
""")
    name_lists.append(f"""{tag} = {{
\tmale = {{
\t\tnames = {{ {' '.join(FIRST)} }}
\t}}
\tfemale = {{
\t\tnames = {{ {' '.join(FEMALE)} }}
\t}}
\tsurnames = {{ {' '.join(SURNAMES)} }}
\tcallsigns = {{ Vitosha Iskar Lion Eagle Hawk Falcon Wolf Bear }}
}}""")
    if tag in FEATURED:
        loc.append(f' EVIL_SOFIA_{tag}_DESC:0 "{FEATURED[tag]}\\n\\nLeader: {LEADER_NAMES[tag]}."')
        featured_entries[tag] = (f"\t\t{tag} = {{\n\t\t\thistory = \"EVIL_SOFIA_{tag}_DESC\"\n"
                                 f"\t\t\tideology = neutrality\n\t\t}}")
    else:
        bookmark_countries.append(f"\t\t{tag} = {{\n\t\t\tminor = yes\n\t\t\thistory = \"EVIL_SOFIA_START_DESC\"\n"
                                  f"\t\t\tideology = neutrality\n\t\t}}")
    loc += [f' {tag}:0 "{name}"', f' {tag}_DEF:0 "{name}"', f' {tag}_ADJ:0 "{adj_}"',
            f' {tag}_leader:0 "{leader}"', f' {tag}_leader_desc:0 "{_texts.LEADER_DESCS[tag]}"',
            f' {tag}_general:0 "{general[0]} {general[1]}"']
    # Flags: tools/flags/<TAG>.png, cut from the "Flags of Sofia and her regions" sheet; without one, three
    # stripes in the country colour.
    flag_src = os.path.join(ROOT, "tools", "flags", f"{tag}.png")
    dark = (r // 2, g // 2, b // 2)
    for folder, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
        if os.path.exists(flag_src):
            flag = Image.open(flag_src).convert("RGBA").resize(size, Image.LANCZOS)
        else:
            flag = Image.new("RGBA", size, (r, g, b, 255))
            d = ImageDraw.Draw(flag)
            d.rectangle([0, 0, size[0], size[1] // 3], fill=dark + (255,))
            d.rectangle([0, size[1] - size[1] // 3, size[0], size[1]], fill=dark + (255,))
        flag.save(out(f"gfx/flags/{folder}{tag}.tga"))
for rid, rname in list(REGIONS.items()) + [SEA_REGION]:
    loc.append(f' EVIL_SOFIA_REGION_{rid}:0 "{rname}"')
loc.append(' EVIL_SOFIA_SUPPLY_AREA:0 "Sofia"')
# Separate file: vanilla tags stay registered (they own no states, so they never appear),
# which keeps vanilla scripts that mention GER, SOV etc. parsing cleanly.
write("common/country_tags/evil_sofia_countries.txt", "\n".join(tags_txt) + "\n")
write("common/names/evil_sofia_names.txt", "\n".join(name_lists) + "\n")
# A starter focus tree for the countries without their own leader. The start screen only shows a minor country as
# a small flag when it has a focus tree of its own (vanilla's generic tree does not count). The featured
# countries keep vanilla's generic tree until real focus trees are made. Icons are vanilla's.
STARTER_FOCUSES = [
    # id, x, y, prerequisites (any one of them), icon, search filter, reward, name, description
    ("seize_the_district_hall", 1, 0, [], "GFX_goal_generic_political_pressure", "FOCUS_FILTER_POLITICAL",
     "add_political_power = 120", "Seize the District Hall",
     "The city council has fled and the mayor's office is empty. In every district of Sofia, whoever holds the district hall holds the stamps, the payroll and the keys to the armoury. Tonight it will be us."),
    ("martial_law", 0, 1, ["seize_the_district_hall"], "GFX_goal_generic_propaganda", "FOCUS_FILTER_WAR_SUPPORT",
     "add_war_support = 0.10", "Martial Law", "A curfew from ten in the evening, checkpoints on every bridge and a guard at every tram stop. The people will complain, but they will complain indoors."),
    ("neighbourhood_patrols", 2, 1, ["seize_the_district_hall"], "GFX_goal_generic_national_unity",
     "FOCUS_FILTER_STABILITY", "add_stability = 0.10", "Neighbourhood Patrols",
     "Every block elects a warden, and every warden reports to the district hall: who has moved in, who has moved out and who has been talking to the neighbours across the boulevard."),
    ("propaganda_on_every_block", 1, 2, ["martial_law", "neighbourhood_patrols"], "GFX_goal_generic_propaganda",
     "FOCUS_FILTER_POLITICAL", "add_political_power = 100\n\t\t\tadd_stability = 0.05\n\t\t\tadd_war_support = 0.05",
     "Propaganda on Every Block", "Posters on every panel block, loudspeakers on every lamp post and our newspaper in every kiosk. By the end of the month there will be nobody in the district who does not know whose side they are on."),
    ("fix_the_streets", 5, 0, [], "GFX_goal_generic_construct_infrastructure", "FOCUS_FILTER_INDUSTRY",
     "random_owned_controlled_state = {\n\t\t\t\tlimit = { free_building_slots = { building = infrastructure size > 0 } }\n"
     "\t\t\t\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }\n\t\t\t}",
     "Fix the Streets", "Sofia's potholes have broken more axles than any enemy ever will. If our guards are to reach the front, someone has to fill them in first."),
    ("district_workshops", 4, 1, ["fix_the_streets"], "GFX_goal_generic_construct_civ_factory", "FOCUS_FILTER_INDUSTRY",
     "capital_scope = {\n\t\t\t\tadd_extra_state_shared_building_slots = 1\n"
     "\t\t\t\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }\n\t\t\t}",
     "District Workshops", "Bakeries, print shops and car repair garages are reopened under district management. They will make what the district needs, and the district needs everything."),
    ("arms_workshops", 6, 1, ["fix_the_streets"], "GFX_goal_generic_construct_mil_factory", "FOCUS_FILTER_INDUSTRY",
     "capital_scope = {\n\t\t\t\tadd_extra_state_shared_building_slots = 1\n"
     "\t\t\t\tadd_building_construction = { type = arms_factory level = 1 instant_build = yes }\n\t\t\t}",
     "Arms Workshops", "A lathe in a garage can turn a rifle barrel as well as a car part, given a drawing and some encouragement. Every workshop in the district gets both."),
    ("industrial_drive", 5, 2, ["district_workshops", "arms_workshops"], "GFX_goal_generic_production",
     "FOCUS_FILTER_RESEARCH", "add_tech_bonus = { name = ESF_industrial_drive bonus = 0.5 uses = 2 category = industry }",
     "Industrial Drive", "Two shifts, then three. The workshops never close, the lights never go off and the foremen sleep in their offices."),
    ("district_institute", 5, 3, ["industrial_drive"], "GFX_goal_generic_research", "FOCUS_FILTER_RESEARCH",
     "add_research_slot = 1", "District Institute", "Engineers, chemists and radio men from the city's universities are given a building, a budget and a list of problems the district guard needs solved by spring."),
    ("raise_the_city_guard", 9, 0, [], "GFX_goal_generic_allies_build_infantry", "FOCUS_FILTER_ARMY_XP",
     "army_experience = 10\n\t\t\tadd_tech_bonus = { name = ESF_raise_the_city_guard bonus = 0.5 uses = 1 category = land_doctrine }",
     "Raise the City Guard", "Night watchmen, bus drivers, students and pensioners: every resident who can carry a rifle is enrolled in the district guard and given a unit, an armband and a place to report to."),
    ("arm_the_blocks", 8, 1, ["raise_the_city_guard"], "GFX_goal_generic_small_arms", "FOCUS_FILTER_RESEARCH",
     "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1000 }\n"
     "\t\t\tadd_tech_bonus = { name = ESF_arm_the_blocks bonus = 0.5 uses = 1 category = infantry_weapons }",
     "Arm the Blocks", "A rifle in every flat and a crate of ammunition in every basement. If the enemy comes, every staircase in the district will be a fighting position."),
    ("rooftop_air_defence", 10, 1, ["raise_the_city_guard"], "GFX_goal_generic_fortify_city", "FOCUS_FILTER_INDUSTRY",
     "capital_scope = { add_building_construction = { type = anti_air_building level = 1 instant_build = yes } }",
     "Rooftop Air Defence", "The tallest panel blocks in the district get anti-aircraft guns on their roofs and lookouts on the top floor. Nothing will fly over us unseen."),
    ("rooftop_artillery", 9, 2, ["arm_the_blocks"], "GFX_goal_generic_army_artillery", "FOCUS_FILTER_RESEARCH",
     "add_tech_bonus = { name = ESF_rooftop_artillery bonus = 0.5 uses = 1 category = artillery }",
     "Rooftop Artillery", "From the roof of a fourteen-storey block, every street of the neighbouring district is within range of a field gun. The residents of the top floor have been asked to move downstairs."),
]
starter_tags = [DISTRICTS[k][0] for k in DISTRICTS if DISTRICTS[k][0] not in FEATURED]
focus_blocks = []
STARTER_COST = {"seize_the_district_hall": 5, "martial_law": 6, "neighbourhood_patrols": 6,
                "propaganda_on_every_block": 8, "fix_the_streets": 7, "district_workshops": 10, "arms_workshops": 10,
                "industrial_drive": 9, "district_institute": 12, "raise_the_city_guard": 5, "arm_the_blocks": 7,
                "rooftop_air_defence": 6, "rooftop_artillery": 8}
for fid, fx, fy, prereq, icon, filt, reward, fname, fdesc in STARTER_FOCUSES:
    pre = ("\n\t\tprerequisite = { " + " ".join(f"focus = ESF_{q}" for q in prereq) + " }") if prereq else ""
    focus_blocks.append(f"""\tfocus = {{
\t\tid = ESF_{fid}
\t\ticon = {icon}
\t\tx = {fx}
\t\ty = {fy}{pre}
\t\tcost = {STARTER_COST[fid]}
\t\tsearch_filters = {{ {filt} }}
\t\tai_will_do = {{ factor = 1 }}
\t\tcompletion_reward = {{
\t\t\t{reward}
\t\t}}
\t}}""")
    loc += [f' ESF_{fid}:0 "{fname}"', f' ESF_{fid}_desc:0 "{fdesc}"']
write("common/national_focus/evil_sofia_starter.txt", f"""focus_tree = {{
\tid = evil_sofia_starter_focus
\tcountry = {{
\t\tfactor = 0
\t\tmodifier = {{
\t\t\tadd = 10
\t\t\tOR = {{ {' '.join(f'tag = {t}' for t in starter_tags)} }}
\t\t}}
\t}}
\tdefault = no

{chr(10).join(focus_blocks)}
}}
""")
write("localisation/english/replace/evil_sofia_l_english.yml", "\n".join(loc) + "\n", bom=True)
if os.path.exists(out("localisation/english/evil_sofia_l_english.yml")):
    os.remove(out("localisation/english/evil_sofia_l_english.yml"))
# The stock tutorial names state 550 and provinces 5010, 5091 and 12766, and the in-game hint loader looks
# them up at every match start, tutorial or not: on this map that is a null lookup and a crash. It cannot be
# empty either (the loader then reads element -1), so it is one block that names no state or province.
write("tutorial/tutorial.txt", """tutorial = {
\twindow = "tutorial_screen_1"
\tuse_mil_fac = { textbox = "obj_1" }
}
""")
# Minimap widgets: vanilla's are pictures of the Earth. These show the city, the land around it and water.
minimap = np.zeros((H, W, 4), np.uint8)
minimap[...] = (60, 72, 50, 255)
minimap[city] = (86, 104, 70, 255)
minimap[WATER | sea_mask] = (32, 52, 84, 255)
for path_, size_ in (("gfx/minimap/minimap.dds", (268, 97)), ("gfx/interface/minimap.dds", (268, 98))):
    write_dds_bgra(path_, np.asarray(Image.fromarray(minimap).resize(size_, Image.BOX)))
del minimap

# Vanilla on_actions, events and decisions are written for the world map and its countries; they are
# replaced (descriptor.mod) by this file: checkpoints in game.log, and the news when a district capitulates.
write("common/on_actions/evil_sofia_on_actions.txt", """on_actions = {
\ton_capitulation = {
\t\teffect = {
\t\t\tnews_event = { id = evil_sofia_news.8 hours = 1 }
\t\t}
\t}
\ton_startup = {
\t\teffect = {
\t\t\tlog = "Evil Sofia checkpoint 2: on_startup ran"
\t\t}
\t}
\ton_monthly = {
\t\teffect = {
\t\t\tif = {
\t\t\t\tlimit = { tag = SRD }
\t\t\t\tlog = "Evil Sofia checkpoint 3: a month has passed"
\t\t\t}
\t\t}
\t}
}
""")
write("common/bookmarks/the_fall_of_sofia.txt", f"""bookmarks = {{
\tbookmark = {{
\t\tname = "EVIL_SOFIA_START_NAME"
\t\tdesc = "EVIL_SOFIA_START_DESC"
\t\tdate = 1936.1.1.12
\t\tpicture = "GFX_select_date_1936"
\t\tdefault_country = "SRD"
\t\tdefault = yes

{chr(10).join(featured_entries[t] for t in FEATURED)}
{chr(10).join(bookmark_countries)}

\t\teffect = {{
\t\t\trandomize_weather = 22345
\t\t\tlog = "Evil Sofia checkpoint 1: bookmark effect ran"
\t\t}}
\t}}
}}
""")

# ---------------------------------------------------------------- previews for humans
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 11)
    cap_f = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    big = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
except OSError:
    font = cap_f = big = ImageFont.load_default()
ys_, xs_ = np.nonzero(city)
cy0, cy1, cx0, cx1 = max(ys_.min() - 15, 0), min(ys_.max() + 15, H), max(xs_.min() - 15, 0), min(xs_.max() + 15, W)


def edge_mask(a):
    e = np.zeros((H, W), bool)
    e[:, 1:] |= a[:, 1:] != a[:, :-1]
    e[1:, :] |= a[1:, :] != a[:-1, :]
    return e


pb, sb, cb = edge_mask(prov), edge_mask(state_map), edge_mask(dist)


def preview(base, path, labels="vp"):
    img = base.copy()
    img[pb & city] = (img[pb & city] * 0.75).astype(np.uint8)
    img[sb & city] = (img[sb & city] * 0.35).astype(np.uint8)
    img[ndi.binary_dilation(cb, iterations=1)] = (15, 15, 15)
    img[river_mask] = (40, 110, 230)
    im_ = Image.fromarray(img[cy0:cy1, cx0:cx1])
    d_ = ImageDraw.Draw(im_)
    if labels == "vp":
        for p, (nm, val) in vp.items():
            if val < 3:
                continue
            x, y = cent[p][0] - cx0, cent[p][1] - cy0
            is_cap = val >= 10
            r_ = 4 if is_cap else 2
            d_.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(255, 215, 0) if is_cap else (255, 255, 255), outline="black")
            d_.text((x, y - r_ - 1), nm, fill=(255, 235, 120) if is_cap else "white", font=cap_f if is_cap else font,
                    anchor="mb", stroke_width=2, stroke_fill="black")
    im_.save(out(path))


political = np.zeros((H, W, 3), np.uint8)
political[:] = (40, 52, 70)
for st in states:   # each state a shade of its country's colour
    r, g, b = country_color(st["district"])
    f_ = 0.80 + 0.35 * ((st["id"] * 0.618) % 1.0)
    political[state_map == st["id"]] = (min(int(r * f_), 255), min(int(g * f_), 255), min(int(b * f_), 255))
preview(political, "preview/states_preview.png")
shade = np.clip(0.55 + 0.45 * ((-slope_x + slope_y) * EXAG * 0.7), 0.25, 1.2)[..., None]
terrain_rgb = np.zeros((H, W, 3), np.float32)
terrain_rgb[:] = (196, 186, 132)
terrain_rgb[tmap == TEX_FIELDS] = (210, 196, 120)
terrain_rgb[np.isin(tmap, [TEX_FOREST, TEX_FOREST_HIGH])] = (56, 120, 52)
terrain_rgb[tmap == TEX_HILLS] = (160, 140, 90)
terrain_rgb[tmap == TEX_ROCK] = (130, 120, 115)
terrain_rgb[tmap == TEX_SNOW] = (235, 235, 240)
terrain_rgb[tmap == TEX_CITY] = (200, 60, 50)
terrain_rgb[WATER] = (60, 110, 190)
terrain_rgb = (terrain_rgb * shade).clip(0, 255)
terrain_rgb[~city] = terrain_rgb[~city] * 0.55
preview(terrain_rgb.astype(np.uint8), "preview/terrain_preview.png")
whole = political.copy()
whole[cb] = (20, 20, 20)
pim = Image.fromarray(whole).resize((W // 2, H // 2), Image.BOX)
d = ImageDraw.Draw(pim)
d.text((30, 25), "EVIL SOFIA", fill=(220, 60, 60), font=big, stroke_width=3, stroke_fill="black")
pim.save(out("preview/political_preview.png"))

terr_count = {t_: sum(1 for p in land_ids if prov_terrain[p] == t_) for t_ in ("plains", "forest", "hills", "mountain")}
per_country = [sum(1 for st in states if st["district"] == k) for k in DISTRICTS]
print(f"{len(vp)} cities; {len(states)} states ({min(per_country)}-{max(per_country)} per country); terrain {terr_count}")
print(f"map {W}x{H}, {len(land_ids)} land provinces, {len(lake_ids)} lake provinces, {len(REGIONS) + 1} strategic regions")

# ---------------------------------------------------------------- cores & claims map mode
# A scripted map mode (format: the game's common/map_modes documentation; idea: Road to 56's core map mode).
# For the player's country, every state is coloured: green own core, yellow owned but not a core, purple a core
# someone else owns, blue a claim, orange occupied by the player but owned by someone else.
MM = "evil_sofia_cores_claims"
write(f"common/map_modes/{MM}.txt", f"""scripted_map_modes = {{
	{MM} = {{
		top = {{
			type = state
			color = {{
				FROM = {{
					set_temp_variable = {{ alpha = 1.0 }}
					if = {{
						limit = {{ is_owned_by = ROOT is_core_of = ROOT }}
						set_temp_variable = {{ red = 0.1 }}
						set_temp_variable = {{ green = 0.75 }}
						set_temp_variable = {{ blue = 0.2 }}
					}}
					else_if = {{
						limit = {{ is_owned_by = ROOT }}
						set_temp_variable = {{ red = 0.95 }}
						set_temp_variable = {{ green = 0.85 }}
						set_temp_variable = {{ blue = 0.2 }}
					}}
					else_if = {{
						limit = {{ is_core_of = ROOT }}
						set_temp_variable = {{ red = 0.6 }}
						set_temp_variable = {{ green = 0.15 }}
						set_temp_variable = {{ blue = 0.85 }}
					}}
					else_if = {{
						limit = {{ is_claimed_by = ROOT }}
						set_temp_variable = {{ red = 0.15 }}
						set_temp_variable = {{ green = 0.55 }}
						set_temp_variable = {{ blue = 1.0 }}
					}}
					else = {{
						set_temp_variable = {{ red = 1.0 }}
						set_temp_variable = {{ green = 0.5 }}
						set_temp_variable = {{ blue = 0.1 }}
					}}
				}}
			}}
			thickness = no
			targets = {{
				target_array = global.states
				target_trigger = {{
					FROM = {{
						OR = {{
							is_owned_by = ROOT
							is_controlled_by = ROOT
							is_core_of = ROOT
							is_claimed_by = ROOT
						}}
					}}
				}}
			}}
		}}
		bottom = {{
			type = none
		}}
		far_text = country
		near_text = state
		update_daily = yes
	}}
}}
""")
# its button icons (selected and not selected): a small coloured map legend
for sel, bg in (("selected", (90, 75, 40, 255)), ("deselected", (45, 45, 45, 255))):
    icon = Image.new("RGBA", (32, 32), bg)
    d_ = ImageDraw.Draw(icon)
    for i, c in enumerate([(26, 190, 50), (240, 215, 50), (150, 40, 215), (40, 140, 255)]):
        d_.rectangle([4 + (i % 2) * 12, 4 + (i // 2) * 12, 14 + (i % 2) * 12, 14 + (i // 2) * 12], fill=c + (255,))
    d_.rectangle([0, 0, 31, 31], outline=(200, 170, 100, 255) if sel == "selected" else (110, 110, 110, 255))
    write_dds_bgra(f"gfx/interface/mapmode_{MM}_{sel}.dds", np.asarray(icon))
write("interface/evil_sofia_mapmodes.gfx", "spriteTypes = {\n" + "".join(
    f'\tspriteType = {{\n\t\tname = "GFX_mapmode_buttons_{sel}_small_{MM}"\n'
    f'\t\ttexturefile = "gfx/interface/mapmode_{MM}_{sel}.dds"\n\t}}\n' for sel in ("selected", "deselected")) + "}\n")
mm_desc = ("Green: your core. Yellow: yours, not a core. Purple: your core owned by someone else. "
           "Blue: your claim. Orange: occupied by you.")
write("localisation/english/replace/evil_sofia_mapmode_l_english.yml", "\n".join([
    "l_english:", f' MAPMODE_{MM.upper()}:0 "Cores and Claims"', f' MAPMODE_{MM.upper()}_NAME:0 "Cores and Claims"',
    f' MAPMODE_{MM.upper()}_DESCRIPTION:0 "{mm_desc}"', f' {MM}_tooltip:0 "Cores and Claims"',
    f' {MM}_tooltip_delayed:0 "{mm_desc}"']) + "\n", bom=True)

# ---------------------------------------------------------------- focus trees (tools/build_focus.py)
_sx, _sy = place_px(42.6875, 23.3355)                 # Vasil Levski National Stadium
stadium = int(prov[int(round(_sy)), int(round(_sx))])
if prov_district.get(stadium) != 1:
    stadium = capital[1]
_spec = importlib.util.spec_from_file_location("build_focus", os.path.join(ROOT, "tools", "build_focus.py"))
_bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bf)
_n = _bf.build(ROOT, {"states": [{"id": st["id"], "owner": DISTRICTS[st["district"]][0], "name": st["name"]} for st in states],
                      "capital_state": {DISTRICTS[k][0]: sid for k, sid in country_capital_state.items()},
                      "stadium_province": stadium,
                      "countries": {v[0]: v[1] for v in DISTRICTS.values()}}, write, write_dds_bgra)
print(f"focus tree: {_n} focuses for Sredets")
