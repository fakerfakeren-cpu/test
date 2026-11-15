#!/usr/bin/env python3
"""Build the Evil Sofia HOI4 map from tools/districts_mask.png.

districts_mask.png is an 8-bit grayscale image where each pixel value is the
district number (1-24, see DISTRICTS below) and 0 is "outside the city".
Edit that image (or the tables below) and re-run this script to regenerate
every map file. Requires: pip install numpy pillow scipy

Usage:  python3 tools/build_map.py        (run from the evil-sofia/ folder)

Engine rules this script follows (measured in game on HOI4 1.19, see README):
- every file is written with CRLF line endings (definition.csv needs them)
- provinces stay small (TOO LARGE BOX), no four-province pixel corners
- buildings.txt uses the 1.19 position types and vanilla counts
- every strategic region passes the region-centre divide-by-zero check
"""
import colorsys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 2048, 1024     # small canvas: the whole city fits on screen when zoomed out
MARGIN = 100          # water ring around the city; keeps every state under half the map height
LAND_TARGET, LAND_MAX_BOX, LAND_MIN_CELL = 3000, 100, 300   # px per land province, max box side, min split
LAKE_TARGET, LAKE_MAX_BOX = 8000, 100
SEA_LEVEL = 94        # heightmap values below this render as water
RNG = np.random.default_rng(1944)

# id: (TAG, name, adjective, state_category, approx. population, strategic region)
DISTRICTS = {
    1: ("SRD", "Sredets", "Sredetsian", "megalopolis", 32000, 1),
    2: ("VAZ", "Vazrazhdane", "Vazrazhdanian", "metropolis", 37000, 1),
    3: ("OBR", "Oborishte", "Oborishtian", "metropolis", 32000, 1),
    4: ("KRS", "Krasno Selo", "Krasnoselian", "large_city", 72000, 1),
    5: ("SRK", "Serdika", "Serdikan", "large_city", 52000, 2),
    6: ("POD", "Poduyane", "Poduyanian", "large_city", 75000, 2),
    7: ("SLA", "Slatina", "Slatinian", "large_city", 67000, 2),
    8: ("IZG", "Izgrev", "Izgrevian", "large_city", 33000, 1),
    9: ("LOZ", "Lozenets", "Lozenetsian", "large_city", 50000, 1),
    10: ("TRD", "Triaditsa", "Triaditsan", "large_city", 63000, 1),
    11: ("KRP", "Krasna Polyana", "Krasnopolyanian", "large_city", 59000, 1),
    12: ("ILN", "Ilinden", "Ilindenian", "large_city", 33000, 1),
    13: ("NAD", "Nadezhda", "Nadezhdan", "city", 67000, 2),
    14: ("ISK", "Iskar", "Iskarian", "city", 64000, 3),
    15: ("MLA", "Mladost", "Mladostian", "city", 103000, 3),
    16: ("STU", "Studentski", "Studentskian", "city", 71000, 3),
    17: ("LYU", "Lyulin", "Lyulinian", "city", 114000, 4),
    18: ("KRE", "Kremikovtsi", "Kremikovtsian", "large_town", 23000, 2),
    19: ("VIT", "Vitosha", "Vitoshan", "town", 61000, 4),
    20: ("OVK", "Ovcha Kupel", "Ovchakupelian", "town", 52000, 4),
    21: ("VRB", "Vrabnitsa", "Vrabnitsan", "town", 47000, 4),
    22: ("NIS", "Novi Iskar", "Noviiskarian", "rural", 27000, 2),
    23: ("PNC", "Pancharevo", "Pancharevian", "rural", 28000, 3),
    24: ("BNK", "Bankya", "Bankyan", "rural", 13000, 4),
}
REGIONS = {1: "Downtown", 2: "Northern Sofia", 3: "Eastern Sofia", 4: "Western Sofia"}

# ---------------------------------------------------------------- geography (approximate lat, lon)
# Cities (victory points): neighbourhoods, streets and villages, biggest first; the first is the capital.
NAMES = {
    1: [("Vitosha Boulevard", 42.6895, 23.3195), ("Graf Ignatiev", 42.6905, 23.3290),
        ("Borisova Gradina", 42.6835, 23.3405), ("Slaveykov Square", 42.6935, 23.3245)],
    2: [("Vazrazhdane Square", 42.6975, 23.3075), ("Zona B-5", 42.6915, 23.3050),
        ("Zona B-18", 42.7005, 23.3010), ("Zhenski Pazar", 42.7010, 23.3165)],
    3: [("Oborishte", 42.6975, 23.3420), ("Doctor's Garden", 42.6930, 23.3355),
        ("Zaimov Park", 42.7010, 23.3380), ("Eagles' Bridge", 42.6905, 23.3390)],
    4: [("Krasno Selo", 42.6805, 23.2870), ("Hipodruma", 42.6850, 23.2935), ("Borovo", 42.6720, 23.2850),
        ("Belite Brezi", 42.6770, 23.2960), ("Lagera", 42.6860, 23.3000), ("Buxton", 42.6720, 23.2700)],
    5: [("Banishora", 42.7135, 23.3140), ("Orlandovtsi", 42.7340, 23.3310), ("Fondovi Zhilishta", 42.7210, 23.3200),
        ("Malashevtsi", 42.7170, 23.3450), ("Benkovski", 42.7360, 23.3150)],
    6: [("Poduyane", 42.7050, 23.3540), ("Hadzhi Dimitar", 42.7100, 23.3560), ("Levski", 42.7120, 23.3750),
        ("Suhata Reka", 42.7040, 23.3690), ("Gerena", 42.6970, 23.3680)],
    7: [("Slatina", 42.6850, 23.3720), ("Geo Milev", 42.6800, 23.3610), ("Reduta", 42.6900, 23.3560)],
    8: [("Izgrev", 42.6740, 23.3500), ("Iztok", 42.6690, 23.3460), ("Dianabad", 42.6680, 23.3560)],
    9: [("Lozenets", 42.6750, 23.3250), ("Krastova Vada", 42.6560, 23.3130), ("Hladilnika", 42.6620, 23.3170),
        ("South Park", 42.6730, 23.3110)],
    10: [("Ivan Vazov", 42.6800, 23.3080), ("Strelbishte", 42.6720, 23.2960), ("Gotse Delchev", 42.6690, 23.3020),
         ("Manastirski Livadi", 42.6620, 23.2990)],
    11: [("Krasna Polyana", 42.7000, 23.2870), ("Fakulteta", 42.6920, 23.2800), ("Razsadnika", 42.7040, 23.2930),
         ("Zapaden Park", 42.7060, 23.2700)],
    12: [("Ilinden", 42.7100, 23.2960), ("Zaharna Fabrika", 42.7140, 23.2880), ("Sveta Troitsa", 42.7060, 23.3030)],
    13: [("Nadezhda", 42.7310, 23.3020), ("Svoboda", 42.7230, 23.2920), ("Tolstoy", 42.7240, 23.2810),
         ("Trebich", 42.7720, 23.2960)],
    14: [("Druzhba", 42.6650, 23.3950), ("Druzhba 2", 42.6530, 23.4070), ("Dimitar Milenkov", 42.6800, 23.4370)],
    15: [("Mladost", 42.6500, 23.3750), ("Mladost 4", 42.6290, 23.3820), ("Business Park", 42.6260, 23.3770),
         ("Gorublyane", 42.6390, 23.4020)],
    16: [("Studentski Grad", 42.6500, 23.3450), ("Darvenitsa", 42.6600, 23.3490), ("Musagenitsa", 42.6570, 23.3600),
         ("Malinova Dolina", 42.6350, 23.3550)],
    17: [("Lyulin", 42.7140, 23.2550), ("Lyulin 10", 42.7060, 23.2340), ("Filipovtsi", 42.7230, 23.2620),
         ("Lyulin 3", 42.7180, 23.2440)],
    18: [("Kremikovtsi", 42.7900, 23.5000), ("Botunets", 42.7520, 23.4730), ("Chelopechene", 42.7300, 23.4580),
         ("The Steelworks", 42.7560, 23.5090), ("Gorni Bogrov", 42.7350, 23.5600), ("Dolni Bogrov", 42.7140, 23.5250),
         ("Yana", 42.7600, 23.5800), ("Seslavtsi", 42.7680, 23.4560)],
    19: [("Boyana", 42.6430, 23.2670), ("Dragalevtsi", 42.6280, 23.3080), ("Simeonovo", 42.6260, 23.3420),
         ("Knyazhevo", 42.6590, 23.2400), ("Pavlovo", 42.6670, 23.2700), ("Vladaya", 42.6460, 23.2010),
         ("Marchaevo", 42.6230, 23.1960), ("Kinotsentara", 42.6340, 23.2560), ("Aleko", 42.5850, 23.2900)],
    20: [("Ovcha Kupel", 42.6800, 23.2570), ("Gorna Banya", 42.6760, 23.2380), ("Suhodol", 42.6720, 23.2180),
         ("Ovcha Kupel 2", 42.6880, 23.2440)],
    21: [("Vrabnitsa", 42.7370, 23.2780), ("Obelya", 42.7430, 23.2880), ("Moderno Predgradie", 42.7320, 23.2620),
         ("Mramor", 42.7650, 23.2560), ("Volyak", 42.7560, 23.2380)],
    22: [("Novi Iskar", 42.8170, 23.3500), ("Kurilo", 42.8290, 23.3630), ("Kubratovo", 42.7860, 23.3680),
         ("Svetovrachene", 42.7910, 23.3920), ("Negovan", 42.7610, 23.4060), ("Mirovyane", 42.8410, 23.3880),
         ("Balsha", 42.8560, 23.3070), ("Vlado Trichkov", 42.8730, 23.3670), ("Gnilyane", 42.8380, 23.4040),
         ("Dobroslavtsi", 42.8040, 23.2830), ("Lokorsko", 42.7980, 23.4300), ("Podgumer", 42.7920, 23.3240)],
    23: [("Pancharevo", 42.5960, 23.4140), ("Kazichene", 42.6620, 23.4650), ("German", 42.6170, 23.3870),
         ("Bistritsa", 42.5850, 23.3620), ("Zheleznitsa", 42.5410, 23.3680), ("Lozen", 42.6000, 23.4880),
         ("Kokalyane", 42.5670, 23.4290), ("Pancharevo Lake", 42.5800, 23.4250), ("Dolni Pasarel", 42.5440, 23.4950),
         ("Plana", 42.4720, 23.4340)],
    24: [("Bankya", 42.7080, 23.1460), ("Ivanyane", 42.7050, 23.1640), ("Klisura", 42.6930, 23.0960),
         ("Verdikal", 42.7250, 23.1120), ("Mihaylovo", 42.6860, 23.0700)],
}
CAPITAL_VP = {1: 30, 2: 15, 3: 15}   # other capitals get 10, other cities 3

# Mountains: elliptical massifs (lat, lon, radius lat, radius lon, extra height, hill/forest/mountain cut-offs
# on the 0..1 "how far up the massif" scale; None = that class does not occur).
MOUNTAINS = [
    ("Vitosha", 42.560, 23.285, 0.075, 0.120, 150, 0.05, 0.25, 0.55),
    ("Lyulin", 42.655, 23.150, 0.035, 0.070, 70, 0.00, 0.30, None),
    ("Lozen mountain", 42.555, 23.515, 0.050, 0.090, 110, 0.05, 0.30, 0.60),
    ("Plana", 42.470, 23.430, 0.045, 0.100, 100, 0.05, 0.25, 0.50),
]
NORTH_FOOTHILLS_LAT = 42.830          # Stara Planina foothills start here and rise northwards
PARKS = [  # (name, lat, lon, radius in km)
    ("Borisova Gradina", 42.6825, 23.3400, 0.75), ("South Park", 42.6715, 23.3085, 0.55),
    ("West Park", 42.7030, 23.2750, 0.60), ("North Park", 42.7340, 23.3080, 0.50),
    ("Loven Park", 42.6555, 23.3445, 0.40), ("Vrana Park", 42.6640, 23.4330, 0.60),
    ("Kambanite Park", 42.6290, 23.3390, 0.40),
]
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
CLASS_NAMES = ["plains", "forest", "hills", "mountain"]
TERRAIN_BMP_INDEX = {0: 0, 1: 1, 2: 17, 3: 6}   # vanilla terrain.bmp palette: plains, forest, hills, mountain
LAKE_BMP_INDEX = 14

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
FEMALE = ["Maria", "Elena", "Ivanka", "Yordanka", "Rositsa", "Desislava", "Vesela", "Teodora", "Milena", "Radka",
          "Stefka", "Tsvetana", "Gergana", "Kalina", "Nevena", "Zornitsa"]


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


# ---------------------------------------------------------------- districts
full_mask = np.asarray(Image.open(os.path.join(ROOT, "tools", "districts_mask.png")).convert("L"))
ys, xs = np.nonzero(full_mask)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
src = full_mask[y0:y1, x0:x1]
scale = min((W - 2 * MARGIN) / src.shape[1], (H - 2 * MARGIN) / src.shape[0])
tw, th = int(src.shape[1] * scale), int(src.shape[0] * scale)
ox, oy = (W - tw) // 2, (H - th) // 2

# Smooth upscale: blur each district's mask, resize, take the strongest one per pixel.
best = np.full((th, tw), -1.0, np.float32)
lab = np.zeros((th, tw), np.int32)
for k in range(0, 25):
    m = ndi.gaussian_filter((src == k).astype(np.float32), 0.8)
    m = np.asarray(Image.fromarray(m).resize((tw, th), Image.BILINEAR))
    sel = m > best
    best[sel], lab[sel] = m[sel], k
dist = np.zeros((H, W), np.int32)
dist[oy:oy + th, ox:ox + tw] = lab
for k in DISTRICTS:   # keep the largest piece of each district
    cl, n = ndi.label(dist == k)
    if n > 1:
        keep = np.bincount(cl.ravel())[1:].argmax() + 1
        dist[(cl > 0) & (cl != keep)] = -1
holes = dist == -1
if holes.any():
    idx = ndi.distance_transform_edt(holes, return_distances=False, return_indices=True)
    dist = dist[idx[0], idx[1]]
city = dist > 0

# ---------------------------------------------------------------- georeference (lat/lon <-> map pixels)
# Rough fit (Sredets ~ pixel 312,312 of the mask, 13.7 px/km), nudged so as many named places as possible
# land inside their own district.
places = [(k, la, lo) for k, lst in NAMES.items() for _, la, lo in lst]
pk = np.array([q[0] for q in places])
pla = np.array([q[1] for q in places])
plo = np.array([q[2] for q in places])
best_fit = (-1, 0, 0, 1.0)
for sc in np.arange(0.85, 1.16, 0.025):
    bx_ = 312 + (plo - 23.3215) * 1119 * sc
    by_ = 312 - (pla - 42.6966) * 1521 * sc
    for dx in range(-25, 26):
        for dy in range(-25, 26):
            xi = np.clip(np.round(bx_ + dx).astype(int), 0, full_mask.shape[1] - 1)
            yi = np.clip(np.round(by_ + dy).astype(int), 0, full_mask.shape[0] - 1)
            hits = int((full_mask[yi, xi] == pk).sum())
            if hits > best_fit[0] or (hits == best_fit[0] and abs(dx) + abs(dy) < abs(best_fit[1]) + abs(best_fit[2])):
                best_fit = (hits, dx, dy, sc)
hits, fdx, fdy, fsc = best_fit
print(f"georeference: {hits}/{len(places)} named places inside their own district")


def place_px(lat, lon):
    sx = 312 + fdx + (lon - 23.3215) * 1119 * fsc
    sy = 312 + fdy - (lat - 42.6966) * 1521 * fsc
    return ox + (sx - x0) * scale, oy + (sy - y0) * scale


gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
LON = 23.3215 + (x0 + (gx - ox) / scale - 312 - fdx) / (1119 * fsc)
LAT = 42.6966 - (y0 + (gy - oy) / scale - 312 - fdy) / (1521 * fsc)
KM_PER_PX = 1 / (13.7 * fsc * scale)

# ---------------------------------------------------------------- terrain classes (0 plains, 1 forest, 2 hills, 3 mountain)
cls = np.zeros((H, W), np.uint8)
elev = np.zeros((H, W), np.float32)


def smooth_noise(sigma):
    n_ = ndi.gaussian_filter(RNG.normal(0, 1, (H // 4, W // 4)).astype(np.float32), sigma)
    n_ /= np.abs(n_).max() + 1e-6
    return np.asarray(Image.fromarray(n_).resize((W, H), Image.BICUBIC))


ragged = 0.6 * smooth_noise(3) + 0.4 * smooth_noise(1.2)   # makes mountain and forest edges irregular
for name, la, lo, rla, rlo, peak, t_hill, t_forest, t_mount in MOUNTAINS:
    e = 1 - ((LAT - la) / rla) ** 2 - ((LON - lo) / rlo) ** 2 + 0.22 * ragged
    elev += peak * np.clip(e, 0, 1) ** 1.2
    if t_hill is not None:
        cls[(e > t_hill) & (cls < 2)] = 2
    if t_forest is not None:
        cls[(e > t_forest) & (cls != 3)] = 1
    if t_mount is not None:
        cls[e > t_mount] = 3
t = (LAT - NORTH_FOOTHILLS_LAT) / 0.06 + 0.45 * ragged
elev += 60 * np.clip(t, 0, 1.3)
cls[(t > 0) & (cls == 0)] = 2
cls[(t > 0.5) & (cls != 3)] = 1
cls[t > 0.95] = 3
for name, la, lo, r in PARKS:
    px_, py_ = place_px(la, lo)
    cls[(gx - px_) ** 2 + (gy - py_) ** 2 <= (r / KM_PER_PX) ** 2] = 1
cls[~city] = 0

# ---------------------------------------------------------------- split districts and the void into provinces
def kmeans_labels(pts, n, iters=15):
    sample = pts[RNG.choice(len(pts), min(len(pts), 20000), replace=False)]
    cen = sample[RNG.choice(len(sample), n, replace=False)].copy()
    for _ in range(iters):
        a = ((sample[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (a == j).any():
                cen[j] = sample[a == j].mean(0)
    labels = np.empty(len(pts), np.int32)
    for i in range(0, len(pts), 100000):
        chunk = pts[i:i + 100000]
        labels[i:i + 100000] = ((chunk[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
    return labels


def make_contiguous(local, sub):
    """Each cell keeps only its largest piece; stray pieces join the nearest cell."""
    for _ in range(3):
        for j in range(1, local.max() + 1):
            cl, n = ndi.label(local == j)
            if n > 1:
                keep = np.bincount(cl.ravel())[1:].argmax() + 1
                local[(cl > 0) & (cl != keep)] = 0
        holes_ = sub & (local == 0)
        if not holes_.any():
            break
        idx_ = ndi.distance_transform_edt(local == 0, return_distances=False, return_indices=True)
        local[holes_] = local[idx_[0], idx_[1]][holes_]
    return local


def split(mask, target, max_box, min_cell=None):
    ys_, xs_ = np.nonzero(mask)
    by, bx = ys_.min(), xs_.min()
    sub = mask[by:ys_.max() + 1, bx:xs_.max() + 1]
    pts = np.argwhere(sub).astype(np.float32)
    n = max(1, int(np.ceil(len(pts) / target)))
    if min_cell:
        n = max(n, min(4, len(pts) // min_cell))
    while True:
        local = np.zeros(sub.shape, np.int32)
        local[sub] = (kmeans_labels(pts, n) + 1) if n > 1 else 1
        local = make_contiguous(local, sub)
        worst = max(max(z.stop - z.start for z in b) for b in ndi.find_objects(local) if b is not None)
        if worst <= max_box or n > 400:
            return local, by, bx
        n += max(1, n // 5)


prov = np.zeros((H, W), np.int32)
prov_district = {}        # province id -> district number (0 = lake)
state_provs = {}          # district number -> [province ids], capital first
next_id = 1
for k in DISTRICTS:
    m = dist == k
    local, by, bx = split(m, LAND_TARGET, LAND_MAX_BOX, min_cell=LAND_MIN_CELL)
    view = prov[by:by + local.shape[0], bx:bx + local.shape[1]]
    state_provs[k] = []
    for j in range(1, local.max() + 1):
        if (local == j).any():
            view[local == j] = next_id
            prov_district[next_id] = k
            state_provs[k].append(next_id)
            next_id += 1

# The void around the city: impassable lakes, split on a 2x coarser grid, then cleaned at full resolution.
F = 2
void = ~city
small_void = void[::F, ::F]
local_s, sby, sbx = split(small_void, LAKE_TARGET / F ** 2, LAKE_MAX_BOX // F - 3)
lab_s = np.zeros(small_void.shape, np.int32)
lab_s[sby:sby + local_s.shape[0], sbx:sbx + local_s.shape[1]] = local_s
lab = np.repeat(np.repeat(lab_s, F, 0), F, 1)[:H, :W].copy()
lab[~void] = 0
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
    view = prov[sl]
    view[lab[sl] == j] = next_id
    prov_district[next_id] = 0
    lake_ids.append(next_id)
    next_id += 1
lake_slices = ndi.find_objects(prov)
for q in list(lake_ids):          # merging slivers can stretch a lake past the size limit; split those again
    sl = lake_slices[q - 1]
    if max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) <= LAKE_MAX_BOX:
        continue
    m = prov[sl] == q
    local, by, bx = split(m, m.sum() / 2, LAKE_MAX_BOX)
    view = prov[sl][by:by + local.shape[0], bx:bx + local.shape[1]]
    for j in range(2, local.max() + 1):
        if (local == j).any():
            view[local == j] = next_id
            prov_district[next_id] = 0
            lake_ids.append(next_id)
            next_id += 1
n_prov = next_id - 1

# HOI4 rejects "X crossings": 2x2 pixel blocks where four different provinces meet. The map wraps
# around horizontally, so the last column also forms blocks with the first one.
for _ in range(10):
    pw_ = np.concatenate([prov, prov[:, :1]], axis=1)
    a, b, c_, d = pw_[1:, :-1], pw_[1:, 1:], pw_[:-1, :-1], pw_[:-1, 1:]
    xc = (a != b) & (a != c_) & (a != d) & (b != c_) & (b != d) & (c_ != d)
    if not xc.any():
        break
    for y, x in np.argwhere(xc):
        prov[y + 1, x] = prov[y, x]  # bottom-left pixel joins the one above (never across the seam)
land_ids = [p for p in prov_district if prov_district[p]]
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
    c = cls[sl][prov[sl] == p]
    share = np.bincount(c, minlength=4) / len(c)
    if share[3] >= 0.35:
        prov_terrain[p] = "mountain"
    elif share[1] >= 0.35:
        prov_terrain[p] = "forest"
    elif share[1] + share[2] + share[3] >= 0.5:
        prov_terrain[p] = "hills"
    else:
        prov_terrain[p] = "plains"

# ---------------------------------------------------------------- cities
vp = {}            # province id -> (name, victory points)
capital = {}
for k, provs in state_provs.items():
    free = list(provs)
    for i, (nm, la, lo) in enumerate(NAMES[k]):
        if not free:
            break
        px_, py_ = place_px(la, lo)
        p = min(free, key=lambda q: (cent[q][0] - px_) ** 2 + (cent[q][1] - py_) ** 2)
        free.remove(p)
        vp[p] = (nm, CAPITAL_VP.get(k, 10) if i == 0 else 3)
        if i == 0:
            capital[k] = p
    state_provs[k] = [capital[k]] + [p for p in provs if p != capital[k]]

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
    if prov_district[p]:
        lines.append(f"{p};{r};{g};{b};land;false;{prov_terrain[p]};1")
    else:
        lines.append(f"{p};{r};{g};{b};lake;false;lakes;0")
write("map/definition.csv", "\n".join(lines) + "\n")

# ---------------------------------------------------------------- heightmap
noise = ndi.gaussian_filter(RNG.normal(0, 1, (H // 8, W // 8)).astype(np.float32), 3)
noise = np.asarray(Image.fromarray(noise / (np.abs(noise).max() + 1e-6)).resize((W, H), Image.BICUBIC))
land_h = np.clip(104 + 3 * noise + elev, 99, 250)
shore = ndi.distance_transform_edt(city).astype(np.float32)
blend = np.clip(shore / 6.0, 0, 1)
heightmap = np.where(city, 80 + (land_h - 80) * np.maximum(blend, 0.6), 80)
heightmap = ndi.gaussian_filter(heightmap, 1.5).astype(np.uint8)
heightmap[city] = np.maximum(heightmap[city], SEA_LEVEL + 4)
Image.fromarray(heightmap, "L").save(out("map/heightmap.bmp"))

# normal map (half size)
hm = heightmap.astype(np.float32)
gyy, gxx = np.gradient(ndi.gaussian_filter(hm, 1.5))
nrm = np.dstack([-gxx * 0.6, -gyy * 0.6, np.ones_like(hm)])
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB").resize((W // 2, H // 2), Image.BILINEAR) \
    .save(out("map/world_normal.bmp"))


# ---------------------------------------------------------------- indexed bitmaps
def indexed(arr, palette):
    im = Image.fromarray(arr.astype(np.uint8), "P")
    im.putpalette(list(palette) + [0] * (768 - len(palette)))
    return im


gray = [v for i in range(256) for v in (i, i, i)]
tmap = np.full((H, W), LAKE_BMP_INDEX, np.uint8)
for c_, idx_ in TERRAIN_BMP_INDEX.items():
    tmap[city & (cls == c_)] = idx_
indexed(tmap, gray).save(out("map/terrain.bmp"))
indexed(np.zeros((H, W)), gray).save(out("map/cities.bmp"))

# trees.bmp (vanilla ratio 1650x600 for 5632x2048): tree palette indices 3 and 4 count as trees
tw_t, th_t = round(W * 1650 / 5632), round(H * 600 / 2048)
forest_small = np.asarray(Image.fromarray((city & (cls == 1)).astype(np.uint8) * 255).resize((tw_t, th_t), Image.BILINEAR)) > 100
mount_small = np.asarray(Image.fromarray((city & (cls == 3)).astype(np.uint8) * 255).resize((tw_t, th_t), Image.BILINEAR)) > 160
trees = np.zeros((th_t, tw_t), np.uint8)
trees[forest_small] = 4
trees[mount_small & (RNG.random((th_t, tw_t)) < 0.35)] = 3
indexed(trees, gray).save(out("map/trees.bmp"))

# rivers.bmp: 255 land, 254 water, 0 source, 1 joins another river, 3..11 river width
river = np.full((H, W), 255, np.uint8)
river[~city] = 254


def path4(pts):
    """Pixels of a polyline, 4-connected (rivers must not connect only diagonally)."""
    res = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        xa, ya, xb, yb = int(round(xa)), int(round(ya)), int(round(xb)), int(round(yb))
        n = max(abs(xb - xa), abs(yb - ya), 1)
        prev = None
        for i in range(n + 1):
            x = int(round(xa + (xb - xa) * i / n))
            y = int(round(ya + (yb - ya) * i / n))
            if prev and prev[0] != x and prev[1] != y:
                res.append((x, prev[1]))
            if not res or res[-1] != (x, y):
                res.append((x, y))
            prev = (x, y)
    out_, seen = [], {}
    for q in res:   # cut out any loop the polyline makes
        if q in seen:
            del out_[seen[q] + 1:]
            seen = {v: i for i, v in enumerate(out_)}
            continue
        seen[q] = len(out_)
        out_.append(q)
    # a river must stay 1 px wide: if it touches itself further along, skip the detour in between
    i = 0
    while i < len(out_):
        xi, yi = out_[i]
        for j in range(len(out_) - 1, i + 1, -1):
            if abs(out_[j][0] - xi) + abs(out_[j][1] - yi) == 1:
                del out_[i + 1:j]
                break
        i += 1
    return out_


def meander(waypoints, wiggle=0.25):
    """Map-pixel waypoints with gentle bends between the given points."""
    pts = [place_px(la, lo) for la, lo in waypoints]
    res = [pts[0]]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        nx, ny = -(yb - ya), xb - xa
        for f in (1 / 3, 2 / 3):
            off = wiggle * RNG.uniform(-1, 1)
            res.append((xa + (xb - xa) * f + nx * off * 0.3, ya + (yb - ya) * f + ny * off * 0.3))
        res.append((xb, yb))
    return res


river_mask = np.zeros((H, W), bool)


def n4(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def junction_ok(base, seq):
    """seq = new tributary pixels; the last one is the flow-in pixel that touches the river."""
    taken = set(base)
    for i_, (x, y) in enumerate(seq):
        if not (0 < x < W - 1 and 0 < y < H - 1) or not city[y, x] or river_mask[y, x] or (x, y) in taken:
            return False
        touching = sum(river_mask[yy, xx] for xx, yy in n4(x, y))
        if touching != (1 if i_ == len(seq) - 1 else 0):
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
    pix = path4(meander(waypoints))
    on_land = [city[y, x] if 0 <= x < W and 0 <= y < H else False for x, y in pix]
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
        joins = False
    else:         # tributary: from its source until it reaches a river already drawn
        course, joins = [], False
        for i, (q, ok) in enumerate(zip(pix, on_land)):
            if not ok:
                break
            x, y = q
            if river_mask[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2].any():
                # join with a single flow-in pixel that touches exactly one river pixel and makes no 2x2 block
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
        print(f"river {rname}: skipped (too short on land)")
        continue
    for i, (x, y) in enumerate(course):
        river[y, x] = 0 if i == 0 else (1 if joins and i == len(course) - 1 else width)
        river_mask[y, x] = True
river_pal = gray[:]
river_pal[0:3] = [0, 255, 0]
river_pal[3:6] = [255, 0, 0]
river_pal[254 * 3:254 * 3 + 3] = [122, 122, 122]
river_pal[255 * 3:255 * 3 + 3] = [255, 255, 255]
indexed(river, river_pal).save(out("map/rivers.bmp"))
blocks = river_mask[:-1, :-1] & river_mask[1:, :-1] & river_mask[:-1, 1:] & river_mask[1:, 1:]
print(f"rivers: {int(river_mask.sum())} px, {int((river == 0).sum())} sources, {int(blocks.sum())} thick spots")


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
write("map/ambient_object.txt", "")   # vanilla ambient objects are placed for the 5632x2048 world map
write("map/positions.txt", "")
# Keep the vanilla continent names: portraits and AI files refer to them. Sofia counts as europe (index 1).
write("map/continent.txt", "continents = {\n" + "".join(f"\t{c}\n" for c in ("europe", "north_america", "south_america", "australia", "africa", "asia", "middle_east")) + "}\n")
write("map/adjacencies.csv", "From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment\n-1;-1;;-1;-1;-1;-1;-1;-1\n")
write("map/adjacency_rules.txt", "")
write("map/supply_nodes.txt", "".join(f"1 {capital[k]}\n" for k in DISTRICTS))


def spots(k, n):
    m = dist == k
    py, px = np.nonzero(m)
    inner = ndi.binary_erosion(m, iterations=3)[py, px]
    if inner.sum() >= n:
        py, px = py[inner], px[inner]
    pick = RNG.choice(len(px), n, replace=len(px) < n)
    return [(int(px[i]), int(py[i])) for i in pick]


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
for k in DISTRICTS:
    for b, n in STATE_BUILDINGS.items():
        for x, y in spots(k, n):
            bl.append(f"{k};{b};{pos(x, y)};{RNG.uniform(0, 6.28):.2f};0")
    for p in state_provs[k]:
        for b, (x, y) in zip(PROVINCE_BUILDINGS, province_spots(p, len(PROVINCE_BUILDINGS))):
            bl.append(f"{k};{b};{pos(x, y)};{RNG.uniform(0, 6.28):.2f};0")
write("map/buildings.txt", "\n".join(bl) + "\n")
# Unit stacks: type 38 is the victory point (city) marker; unit model positions are placed by the game.
write("map/unitstacks.txt", "".join(f"{p};38;{pos(*cent[p])};0.00;0.00\n" for p in land_ids))

# Railways: spanning tree over land neighbours, starting in Sredets.
land_adj = {p: set() for p in land_ids}
for a, b in adj:
    if prov_district.get(a) and prov_district.get(b):
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
\tname = "SUPPLYAREA_1"
\tvalue = 10
\tstates = {{
\t\t{' '.join(map(str, DISTRICTS))}
\t}}
}}
""")

# Strategic regions: each lake joins the region of the nearest district.
region_of = {p: DISTRICTS[prov_district[p]][5] for p in land_ids}
for p in lake_ids:
    lx, ly = cent[p]
    nearest = min(land_ids, key=lambda q: (cent[q][0] - lx) ** 2 + (cent[q][1] - ly) ** 2)
    region_of[p] = region_of[nearest]


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
    for _ in range(50):
        members = [p for p, r in region_of.items() if r == rid]
        if not region_centre_unsafe(members):
            break
        lakes_here = [p for p in members if not prov_district[p]]
        far = max(lakes_here, key=lambda q: (cent[q][0] - W / 2) ** 2 + (cent[q][1] - H / 2) ** 2)
        region_of[far] = rid % len(REGIONS) + 1
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
for rid, rname in REGIONS.items():
    provs = sorted(p for p, r in region_of.items() if r == rid)
    write(f"map/strategicregions/{rid}-{rname.replace(' ', '_')}.txt", f"""strategic_region = {{
\tid = {rid}
\tname = "STRATEGICREGION_{rid}"
\tprovinces = {{
\t\t{' '.join(map(str, provs))}
\t}}
\tweather = {{
{weather_txt}
\t}}
}}
""")
    x, h, z = world(min(p for p in provs if prov_district[p]))
    wpos.append(f"{rid};{x:.2f};{h:.2f};{z:.2f};small")
write("map/weatherpositions.txt", "\n".join(wpos) + "\n")

# ---------------------------------------------------------------- states, countries, characters, localisation
loc = ["l_english:", ' EVIL_SOFIA_START_NAME:0 "The Fall of Sofia"',
       ' EVIL_SOFIA_START_DESC:0 "The city council has collapsed. Twenty-four districts, twenty-four warlords. Only one will rule Sofia."']
tags_txt, bookmark_countries, name_lists = [], [], []
for k, (tag, name, adj_, cat, pop, reg) in DISTRICTS.items():
    infra = 5 if cat in ("megalopolis", "metropolis") else 4 if cat in ("large_city", "city") else 3
    civ = {"megalopolis": 3, "metropolis": 2, "large_city": 2, "city": 1}.get(cat, 0)
    mil = 3 if tag == "KRE" else 0
    steel = "\n\tresources = { steel = 12 }" if tag == "KRE" else ""
    bld = f"infrastructure = {infra}"
    if civ:
        bld += f"\n\t\t\tindustrial_complex = {civ}"
    if mil:
        bld += f"\n\t\t\tarms_factory = {mil}"
    vp_lines = "\n".join(f"\t\tvictory_points = {{ {p} {vp[p][1]} }}" for p in state_provs[k] if p in vp)
    write(f"history/states/{k}-{name.replace(' ', '_')}.txt", f"""state = {{
\tid = {k}
\tname = "STATE_{k}"
\tmanpower = {pop}
\tstate_category = {cat}{steel}

\thistory = {{
\t\towner = {tag}
\t\tadd_core_of = {tag}
{vp_lines}
\t\tbuildings = {{
\t\t\t{bld}
\t\t}}
\t}}

\tprovinces = {{
\t\t{' '.join(map(str, state_provs[k]))}
\t}}
}}
""")
    r, g, b = country_color(k)
    file_name = name.replace(" ", "_")
    write(f"common/countries/{file_name}.txt", f"""graphical_culture = eastern_european_gfx
graphical_culture_2d = eastern_european_2d

color = {{ {r} {g} {b} }}
""")
    tags_txt.append(f'{tag} = "countries/{file_name}.txt"')
    # one country leader and one general per country
    leader = (FIRST[2 * (k - 1)], SURNAMES[2 * (k - 1)])
    general = (FIRST[2 * (k - 1) + 1], SURNAMES[2 * (k - 1) + 1])
    write(f"common/characters/{tag}.txt", f"""characters = {{
\t{tag}_leader = {{
\t\tname = {tag}_leader
\t\tcountry_leader = {{
\t\t\tideology = despotism
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
}}
""")
    write(f"history/countries/{tag} - {name}.txt", f"""capital = {k}

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
    bookmark_countries.append(f"\t\t\t{tag} = {{ }}")
    loc += [f' {tag}:0 "{name}"', f' {tag}_DEF:0 "{name}"', f' {tag}_ADJ:0 "{adj_}"',
            f' STATE_{k}:0 "{name}"', f' {tag}_leader:0 "{leader[0]} {leader[1]}"',
            f' {tag}_general:0 "{general[0]} {general[1]}"']
    loc += [f' VICTORY_POINTS_{p}:0 "{vp[p][0]}"' for p in state_provs[k] if p in vp]
    dark = (r // 2, g // 2, b // 2)    # placeholder flags: three stripes in the country colour
    for folder, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
        flag = Image.new("RGBA", size, (r, g, b, 255))
        d = ImageDraw.Draw(flag)
        d.rectangle([0, 0, size[0], size[1] // 3], fill=dark + (255,))
        d.rectangle([0, size[1] - size[1] // 3, size[0], size[1]], fill=dark + (255,))
        flag.save(out(f"gfx/flags/{folder}{tag}.tga"))
for rid, rname in REGIONS.items():
    loc.append(f' STRATEGICREGION_{rid}:0 "{rname}"')
loc.append(' SUPPLYAREA_1:0 "Sofia"')
# Separate file: vanilla tags stay registered (they own no states, so they never appear),
# which keeps vanilla scripts that mention GER, SOV etc. parsing cleanly.
write("common/country_tags/evil_sofia_countries.txt", "\n".join(tags_txt) + "\n")
write("common/names/evil_sofia_names.txt", "\n".join(name_lists) + "\n")
write("localisation/english/evil_sofia_l_english.yml", "\n".join(loc) + "\n", bom=True)
write("common/bookmarks/the_fall_of_sofia.txt", f"""bookmarks = {{
\tbookmark = {{
\t\tname = "EVIL_SOFIA_START_NAME"
\t\tdesc = "EVIL_SOFIA_START_DESC"
\t\tdate = 1936.1.1.12
\t\tpicture = "GFX_select_date_1936"
\t\tdefault_country = "SRD"
\t\tdefault = yes

{chr(10).join(bookmark_countries)}

\t\teffect = {{
\t\t\trandomize_weather = 22345
\t\t}}
\t}}
}}
""")

# ---------------------------------------------------------------- previews for humans
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 12)
    cap_f = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    big = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
except OSError:
    font = cap_f = big = ImageFont.load_default()
ys_, xs_ = np.nonzero(city)
cy0, cy1, cx0, cx1 = max(ys_.min() - 15, 0), min(ys_.max() + 15, H), max(xs_.min() - 15, 0), min(xs_.max() + 15, W)
pb = np.zeros((H, W), bool)
pb[:, 1:] |= prov[:, 1:] != prov[:, :-1]
pb[1:, :] |= prov[1:, :] != prov[:-1, :]
border = np.zeros((H, W), bool)
border[:, 1:] |= dist[:, 1:] != dist[:, :-1]
border[1:, :] |= dist[1:, :] != dist[:-1, :]


def preview(base, path, scale_up=2):
    img = base.copy()
    img[pb & city] = (img[pb & city] * 0.6).astype(np.uint8)
    img[border] = (20, 20, 20)
    img[river_mask] = (40, 110, 230)
    im_ = Image.fromarray(img[cy0:cy1, cx0:cx1]).resize(((cx1 - cx0) * scale_up, (cy1 - cy0) * scale_up), Image.NEAREST)
    d_ = ImageDraw.Draw(im_)
    for p, (nm, val) in vp.items():
        x, y = (cent[p][0] - cx0) * scale_up, (cent[p][1] - cy0) * scale_up
        is_cap = val >= 10
        r_ = 5 if is_cap else 3
        d_.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(255, 215, 0) if is_cap else (255, 255, 255), outline="black")
        d_.text((x, y - r_ - 1), nm, fill=(255, 235, 120) if is_cap else "white", font=cap_f if is_cap else font,
                anchor="mb", stroke_width=2, stroke_fill="black")
    im_.save(out(path))


political = np.zeros((H, W, 3), np.uint8)
political[:] = (40, 52, 70)
for k in DISTRICTS:
    political[dist == k] = country_color(k)
preview(political, "preview/cities_preview.png")
terrain_rgb = np.zeros((H, W, 3), np.uint8)
terrain_rgb[:] = (40, 52, 70)
for c_, col_ in {0: (196, 186, 132), 1: (56, 120, 52), 2: (150, 128, 78), 3: (120, 110, 110)}.items():
    terrain_rgb[city & (cls == c_)] = col_
preview(terrain_rgb, "preview/terrain_preview.png")
whole = political.copy()
whole[border] = (20, 20, 20)
pim = Image.fromarray(whole)
d = ImageDraw.Draw(pim)
d.text((30, 25), "EVIL SOFIA", fill=(220, 60, 60), font=big, stroke_width=3, stroke_fill="black")
pim.save(out("preview/political_preview.png"))

terr_count = {t_: sum(1 for p in land_ids if prov_terrain[p] == t_) for t_ in CLASS_NAMES}
print(f"{len(vp)} cities; province terrain {terr_count}")
print(f"map {W}x{H}, {len(DISTRICTS)} states, {len(land_ids)} land provinces, {len(lake_ids)} lake provinces, {len(rails)} rail links")
