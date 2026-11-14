#!/usr/bin/env python3
"""Build the Evil Sofia HOI4 map from tools/districts_mask.png.

districts_mask.png is an 8-bit grayscale image where each pixel value is the
district number (1-24, see DISTRICTS below) and 0 is "outside the city".
Edit that image (or replace it) and re-run this script to regenerate every
map file. Requires: pip install numpy pillow scipy

Usage:  python3 tools/build_map.py        (run from the evil-sofia/ folder)
"""
import colorsys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 5632, 2048     # same size as the vanilla map (working custom maps keep the 2048 height)
MARGIN = 200          # lake ring around the city, in map pixels
# Province size limits. HOI4 misbehaves with huge provinces; vanilla ones are rarely over ~200px across.
LAND_TARGET, LAND_MAX_BOX = 30000, 256    # target pixels per land province, max bounding box side
LAKE_TARGET, LAKE_MAX_BOX = 60000, 320
SEA_LEVEL = 94        # heightmap values below this render as water
RNG = np.random.default_rng(1944)

# id: (TAG, name, adjective, terrain, state_category, approx. population, strategic region)
DISTRICTS = {
    1: ("SRD", "Sredets", "Sredetsian", "urban", "megalopolis", 32000, 1),
    2: ("VAZ", "Vazrazhdane", "Vazrazhdanian", "urban", "metropolis", 37000, 1),
    3: ("OBR", "Oborishte", "Oborishtian", "urban", "metropolis", 32000, 1),
    4: ("KRS", "Krasno Selo", "Krasnoselian", "urban", "large_city", 72000, 1),
    5: ("SRK", "Serdika", "Serdikan", "urban", "large_city", 52000, 2),
    6: ("POD", "Poduyane", "Poduyanian", "urban", "large_city", 75000, 2),
    7: ("SLA", "Slatina", "Slatinian", "urban", "large_city", 67000, 2),
    8: ("IZG", "Izgrev", "Izgrevian", "urban", "large_city", 33000, 1),
    9: ("LOZ", "Lozenets", "Lozenetsian", "urban", "large_city", 50000, 1),
    10: ("TRD", "Triaditsa", "Triaditsan", "urban", "large_city", 63000, 1),
    11: ("KRP", "Krasna Polyana", "Krasnopolyanian", "urban", "large_city", 59000, 1),
    12: ("ILN", "Ilinden", "Ilindenian", "urban", "large_city", 33000, 1),
    13: ("NAD", "Nadezhda", "Nadezhdan", "urban", "city", 67000, 2),
    14: ("ISK", "Iskar", "Iskarian", "urban", "city", 64000, 3),
    15: ("MLA", "Mladost", "Mladostian", "urban", "city", 103000, 3),
    16: ("STU", "Studentski", "Studentskian", "urban", "city", 71000, 3),
    17: ("LYU", "Lyulin", "Lyulinian", "urban", "city", 114000, 4),
    18: ("KRE", "Kremikovtsi", "Kremikovtsian", "plains", "large_town", 23000, 2),
    19: ("VIT", "Vitosha", "Vitoshan", "mountain", "town", 61000, 4),
    20: ("OVK", "Ovcha Kupel", "Ovchakupelian", "hills", "town", 52000, 4),
    21: ("VRB", "Vrabnitsa", "Vrabnitsan", "plains", "town", 47000, 4),
    22: ("NIS", "Novi Iskar", "Noviiskarian", "hills", "rural", 27000, 2),
    23: ("PNC", "Pancharevo", "Pancharevian", "hills", "rural", 28000, 3),
    24: ("BNK", "Bankya", "Bankyan", "hills", "rural", 13000, 4),
}
REGIONS = {1: "Downtown", 2: "Northern Sofia", 3: "Eastern Sofia", 4: "Western Sofia"}


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
src = np.asarray(Image.open(os.path.join(ROOT, "tools", "districts_mask.png")).convert("L"))
ys, xs = np.nonzero(src)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
src = src[y0:y1, x0:x1]
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

# Drop stray fragments created by the upscale: keep the largest piece of each district.
for k in DISTRICTS:
    cl, n = ndi.label(dist == k)
    if n > 1:
        keep = np.bincount(cl.ravel())[1:].argmax() + 1
        dist[(cl > 0) & (cl != keep)] = -1
holes = dist == -1
if holes.any():
    idx = ndi.distance_transform_edt(holes, return_distances=False, return_indices=True)
    dist = dist[idx[0], idx[1]]
city = dist > 0

# ---------------------------------------------------------------- split districts and the void into provinces
def kmeans_labels(pts, n, iters=15):
    sample = pts[RNG.choice(len(pts), min(len(pts), 20000), replace=False)]
    cen = sample[RNG.choice(len(sample), n, replace=False)].copy()
    for _ in range(iters):
        a = ((sample[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (a == j).any():
                cen[j] = sample[a == j].mean(0)
    lab = np.empty(len(pts), np.int32)
    for i in range(0, len(pts), 100000):
        chunk = pts[i:i + 100000]
        lab[i:i + 100000] = ((chunk[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
    return lab


def make_contiguous(local, sub):
    """Each cell keeps only its largest piece; stray pieces join the nearest cell."""
    for _ in range(3):
        for j in range(1, local.max() + 1):
            cl, n = ndi.label(local == j)
            if n > 1:
                keep = np.bincount(cl.ravel())[1:].argmax() + 1
                local[(cl > 0) & (cl != keep)] = 0
        holes = sub & (local == 0)
        if not holes.any():
            break
        idx = ndi.distance_transform_edt(local == 0, return_distances=False, return_indices=True)
        local[holes] = local[idx[0], idx[1]][holes]
    return local


def split(mask, target, max_box, min_cell=None):
    ys, xs = np.nonzero(mask)
    by, bx = ys.min(), xs.min()
    sub = mask[by:ys.max() + 1, bx:xs.max() + 1]
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
    local, by, bx = split(m, LAND_TARGET, LAND_MAX_BOX, min_cell=1200)
    view = prov[by:by + local.shape[0], bx:bx + local.shape[1]]
    # capital = the cell holding the district's most interior pixel
    dt = ndi.distance_transform_edt(m)
    cy, cx = np.unravel_index(dt.argmax(), dt.shape)
    cap = int(local[cy - by, cx - bx])
    state_provs[k] = []
    for j in [cap] + [j for j in range(1, local.max() + 1) if j != cap]:
        if not (local == j).any():
            continue
        view[local == j] = next_id
        prov_district[next_id] = k
        state_provs[k].append(next_id)
        next_id += 1
local, by, bx = split(~city, LAKE_TARGET, LAKE_MAX_BOX)
view = prov[by:by + local.shape[0], bx:bx + local.shape[1]]
lake_ids = []
for j in range(1, local.max() + 1):
    if not (local == j).any():
        continue
    view[local == j] = next_id
    prov_district[next_id] = 0
    lake_ids.append(next_id)
    next_id += 1
n_prov = next_id - 1

# HOI4 rejects "X crossings": 2x2 pixel blocks where four different provinces meet.
for _ in range(10):
    a, b, c_, d = prov[1:, :-1], prov[1:, 1:], prov[:-1, :-1], prov[:-1, 1:]
    xc = (a != b) & (a != c_) & (a != d) & (b != c_) & (b != d) & (c_ != d)
    if not xc.any():
        break
    for y, x in np.argwhere(xc):
        prov[y + 1, x + 1] = prov[y + 1, x]  # bottom-right pixel joins its left neighbour
land_ids = [p for p in prov_district if prov_district[p]]

# ---------------------------------------------------------------- centroids (HOI4 world coords: z counts up from the bottom)
cent = {}
for p, sl in enumerate(ndi.find_objects(prov), 1):
    if sl is None:
        continue
    py, px = np.nonzero(prov[sl] == p)
    py, px = py + sl[0].start, px + sl[1].start
    i = np.argmin((py - py.mean()) ** 2 + (px - px.mean()) ** 2)  # a pixel near the centre, always inside
    cent[p] = (int(px[i]), int(py[i]))

# ---------------------------------------------------------------- cities
# Victory points named after real neighbourhoods, streets and villages, biggest first.
# The first name of each district is its capital. Coordinates are approximate (lat, lon).
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

# Fit lat/lon onto districts_mask.png: start from a rough fit (Sredets ~ pixel 312,312, 13.7 px/km)
# and nudge it so as many places as possible land inside their own district.
full_mask = np.asarray(Image.open(os.path.join(ROOT, "tools", "districts_mask.png")).convert("L"))
places = [(k, nm, la, lo) for k, lst in NAMES.items() for nm, la, lo in lst]
pk = np.array([q[0] for q in places])
pla = np.array([q[2] for q in places])
plo = np.array([q[3] for q in places])
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
print(f"city placement: {hits}/{len(places)} places inside their own district")


def place_px(lat, lon):
    sx = 312 + fdx + (lon - 23.3215) * 1119 * fsc
    sy = 312 + fdy - (lat - 42.6966) * 1521 * fsc
    return ox + (sx - x0) * scale, oy + (sy - y0) * scale


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
        if i == 0:
            capital[k] = p
            vp[p] = (nm, CAPITAL_VP.get(k, 10))
        else:
            vp[p] = (nm, 3)
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

# Neighbours (4-connectivity) for railways/coastal checks.
adj = set()
for a, b in ((prov[:, :-1], prov[:, 1:]), (prov[:-1, :], prov[1:, :])):
    d = a != b
    for x, y in set(zip(a[d].tolist(), b[d].tolist())):
        adj.add((min(x, y), max(x, y)))

lines = ["0;0;0;0;land;false;unknown;0"]
for p in range(1, n_prov + 1):
    r, g, b = colors[p]
    if prov_district[p]:
        lines.append(f"{p};{r};{g};{b};land;false;{DISTRICTS[prov_district[p]][3]};1")
    else:
        lines.append(f"{p};{r};{g};{b};lake;false;lakes;0")
write("map/definition.csv", "\n".join(lines) + "\n")

# ---------------------------------------------------------------- heightmap
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def bump(sx, sy, radius, height):
    """Gaussian hill, position/radius given in districts_mask.png pixels."""
    cx, cy, r = ox + (sx - x0) * scale, oy + (sy - y0) * scale, radius * scale
    return height * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))


noise = ndi.gaussian_filter(RNG.normal(0, 1, (H // 8, W // 8)).astype(np.float32), 3)
noise = np.asarray(Image.fromarray(noise / (np.abs(noise).max() + 1e-6)).resize((W, H), Image.BICUBIC))
height = (108 + 6 * noise
          + bump(190, 470, 70, 120)   # Vitosha
          + bump(470, 600, 90, 55)    # Lozen / Pancharevo hills
          + bump(60, 280, 60, 35)     # Bankya / Lyulin mountain
          + bump(350, 60, 110, 45))   # Balkan foothills, north
land_h = np.clip(height, 100, 250)
water_h = np.full_like(land_h, 80)
shore = ndi.distance_transform_edt(city).astype(np.float32)
blend = np.clip(shore / 12.0, 0, 1)
heightmap = np.where(city, water_h + (land_h - water_h) * np.maximum(blend, 0.6), water_h)
heightmap = ndi.gaussian_filter(heightmap, 2).astype(np.uint8)
heightmap[city] = np.maximum(heightmap[city], SEA_LEVEL + 4)
Image.fromarray(heightmap, "L").save(out("map/heightmap.bmp"))

# ---------------------------------------------------------------- normal map (half size)
hm = heightmap.astype(np.float32)
gx, gy = np.gradient(ndi.gaussian_filter(hm, 1.5))
n = np.dstack([-gy * 0.6, gx * 0.6, np.ones_like(hm)])  # (x, y, z) -> RGB, flat = (128,128,255)
n = n[:, :, [1, 0, 2]]
n /= np.linalg.norm(n, axis=2, keepdims=True)
nrm = ((n * 0.5 + 0.5) * 255).astype(np.uint8)
Image.fromarray(nrm, "RGB").resize((W // 2, H // 2), Image.BILINEAR).save(out("map/world_normal.bmp"))


# ---------------------------------------------------------------- indexed bitmaps
def indexed(arr, palette):
    im = Image.fromarray(arr.astype(np.uint8), "P")
    pal = list(palette) + [0] * (768 - len(palette))
    im.putpalette(pal)
    return im


gray = [v for i in range(256) for v in (i, i, i)]
# terrain.bmp only picks ground textures; gameplay terrain comes from definition.csv.
# Palette indices follow vanilla common/terrain: 0 = plains, 14 = lakes.
indexed(np.where(city, 0, 14), gray).save(out("map/terrain.bmp"))
indexed(np.zeros((H, W)), gray).save(out("map/cities.bmp"))
river_pal = gray[:]
river_pal[254 * 3:254 * 3 + 3] = [122, 122, 122]
river_pal[255 * 3:255 * 3 + 3] = [255, 255, 255]
rivers = np.where(city, 255, 254)
indexed(rivers, river_pal).save(out("map/rivers.bmp"))
tw_t, th_t = round(W * 1650 / 5632), round(H * 564 / 2048)  # vanilla trees.bmp ratio
indexed(np.zeros((th_t, tw_t)), gray).save(out("map/trees.bmp"))

# No custom colormap: the vanilla one is stretched over the map until we paint our own.

def world(p):
    x, y = cent[p]
    return x, heightmap[y, x] / 10.0, H - 1 - y


# ---------------------------------------------------------------- default.map & misc map files
# Same keys as vanilla default.map (game build of 2026-11-05). Missing keys crash the game.
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
# The map is vanilla-sized, so the vanilla ambient_object.txt (map frame etc.) is used as-is.
write("map/positions.txt", "")
# Keep the vanilla continent names: portraits and AI files refer to them. Sofia counts as europe (index 1).
write("map/continent.txt", "continents = {\n" + "".join(f"\t{c}\n" for c in ("europe", "north_america", "south_america", "australia", "africa", "asia", "middle_east")) + "}\n")
write("map/adjacencies.csv", "From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment\n-1;-1;;-1;-1;-1;-1;-1;-1\n")
write("map/adjacency_rules.txt", "")
write("map/airports.txt", "".join(f"{k}={{{capital[k]} }}\n" for k in DISTRICTS))
write("map/rocketsites.txt", "".join(f"{k}={{{capital[k]} }}\n" for k in DISTRICTS))
write("map/supply_nodes.txt", "".join(f"1 {capital[k]}\n" for k in DISTRICTS))
# Model positions. Rough placements spread inside each district; fine-tune later with the nudger.
def spots(k, n):
    m = dist == k
    py, px = np.nonzero(m)
    inner = ndi.binary_erosion(m, iterations=6)[py, px]
    if inner.sum() >= n:
        py, px = py[inner], px[inner]
    pick = RNG.choice(len(px), n, replace=len(px) < n)
    return [(int(px[i]), int(py[i])) for i in pick]


def pos(x, y):
    return f"{x:.2f};{heightmap[y, x] / 10.0:.2f};{H - 1 - y:.2f}"


BUILDING_SLOTS = {"arms_factory": 6, "industrial_complex": 6, "air_base": 1, "supply_node": 1,
                  "anti_air_building": 3, "synthetic_refinery": 1, "fuel_silo": 1, "radar_station": 1,
                  "nuclear_reactor": 1, "rocket_site": 1, "bunker": 1}
bl = []
for k in DISTRICTS:
    for b, n in BUILDING_SLOTS.items():
        for x, y in spots(k, n):
            bl.append(f"{k};{b};{pos(x, y)};{RNG.uniform(0, 6.28):.2f};0")
write("map/buildings.txt", "\n".join(bl) + "\n")
# Unit positions are left to the game (working total conversions ship this file nearly empty).
write("map/unitstacks.txt", "")

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

# Supply areas (the game still ships map/supplyareas). One area for the whole city.
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
region_of = {p: DISTRICTS[prov_district[p]][6] for p in land_ids}
for p in lake_ids:
    lx, ly = cent[p]
    nearest = min(land_ids, key=lambda q: (cent[q][0] - lx) ** 2 + (cent[q][1] - ly) ** 2)
    region_of[p] = region_of[nearest]

# Sofia monthly climate: (min temp, max temp, no_phenomenon, rain_light, rain_heavy, snow, blizzard, mud)
CLIMATE = [(-6, 3, .45, .05, 0, .35, .05, .10), (-4, 6, .45, .08, 0, .30, .02, .15),
           (-1, 11, .50, .20, .03, .12, 0, .15), (4, 16, .55, .30, .10, 0, 0, .05),
           (9, 21, .55, .30, .15, 0, 0, 0), (12, 25, .60, .25, .15, 0, 0, 0),
           (14, 28, .75, .15, .10, 0, 0, 0), (14, 28, .80, .12, .08, 0, 0, 0),
           (10, 23, .75, .15, .10, 0, 0, 0), (5, 17, .60, .25, .05, .02, 0, .08),
           (1, 10, .50, .25, .05, .10, 0, .10), (-4, 4, .45, .10, 0, .30, .05, .10)]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
weather = []
for m, (tmin, tmax, nop, rl, rh, sn, bz, mud) in enumerate(CLIMATE):
    weather.append(f"""\t\tperiod = {{
\t\t\tbetween = {{ 0.{m} {DAYS[m] - 1}.{m} }}
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

# ---------------------------------------------------------------- states, countries, localisation
loc = ["l_english:", ' EVIL_SOFIA_START_NAME:0 "The Fall of Sofia"',
       ' EVIL_SOFIA_START_DESC:0 "The city council has collapsed. Twenty-four districts, twenty-four warlords. Only one will rule Sofia."']
tags_txt = []
bookmark_countries = []
for k, (tag, name, adj_, terr, cat, pop, reg) in DISTRICTS.items():
    infra = 5 if cat in ("megalopolis", "metropolis") else 4 if terr == "urban" else 3
    civ = {"megalopolis": 3, "metropolis": 2, "large_city": 2, "city": 1}.get(cat, 0)
    mil = 3 if tag == "KRE" else 0
    steel = "\n\t\tresources = { steel = 12 }" if tag == "KRE" else ""
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
""")
    bookmark_countries.append(f"\t\t\t{tag} = {{ }}")
    loc += [f' {tag}:0 "{name}"', f' {tag}_DEF:0 "{name}"', f' {tag}_ADJ:0 "{adj_}"',
            f' STATE_{k}:0 "{name}"']
    loc += [f' VICTORY_POINTS_{p}:0 "{vp[p][0]}"' for p in state_provs[k] if p in vp]
    # Placeholder flags: three horizontal stripes in the country colour.
    dark = (r // 2, g // 2, b // 2)
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

# ---------------------------------------------------------------- preview for humans
prev = np.zeros((H, W, 3), np.uint8)
prev[:] = (40, 52, 70)
for k in DISTRICTS:
    prev[dist == k] = country_color(k)
pb = np.zeros((H, W), bool)
pb[:, 1:] |= prov[:, 1:] != prov[:, :-1]
pb[1:, :] |= prov[1:, :] != prov[:-1, :]
prev[pb & city] = (prev[pb & city] * 0.6).astype(np.uint8)
border = np.zeros((H, W), bool)
border[:, 1:] |= dist[:, 1:] != dist[:, :-1]
border[1:, :] |= dist[1:, :] != dist[:-1, :]
border = ndi.binary_dilation(border, iterations=2)
prev[border] = (20, 20, 20)
lake_border = np.zeros((H, W), bool)
lake_border[:, 1:] |= (prov[:, 1:] != prov[:, :-1]) & ~city[:, 1:] & ~city[:, :-1]
lake_border[1:, :] |= (prov[1:, :] != prov[:-1, :]) & ~city[1:, :] & ~city[:-1, :]
prev[lake_border] = (60, 75, 98)
pim = Image.fromarray(prev).resize((W // 3, H // 3), Image.LANCZOS)
d = ImageDraw.Draw(pim)
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    big = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
except OSError:
    font = big = ImageFont.load_default()
for k, v in DISTRICTS.items():
    x, y = cent[capital[k]][0] / 3, cent[capital[k]][1] / 3
    label = v[1] if (dist == k).sum() > 60000 else str(k)
    d.text((x, y), label, fill="white", font=font, anchor="mm", stroke_width=3, stroke_fill="black")
d.text((40, 40), "EVIL SOFIA", fill=(220, 60, 60), font=big, stroke_width=3, stroke_fill="black")
pim.save(out("preview/political_preview.png"))
ys_, xs_ = np.nonzero(city)
cy0, cy1, cx0, cx1 = max(ys_.min() - 20, 0), min(ys_.max() + 20, H), max(xs_.min() - 20, 0), min(xs_.max() + 20, W)
cim = Image.fromarray(prev[cy0:cy1, cx0:cx1])
d2 = ImageDraw.Draw(cim)
try:
    small_f = ImageFont.truetype("DejaVuSans-Bold.ttf", 13)
    cap_f = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
except OSError:
    small_f = cap_f = ImageFont.load_default()
for p, (nm, val) in vp.items():
    x, y = cent[p][0] - cx0, cent[p][1] - cy0
    is_cap = val >= 10
    r_ = 6 if is_cap else 4
    d2.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(255, 215, 0) if is_cap else (255, 255, 255), outline="black", width=2)
    d2.text((x, y - r_ - 2), nm, fill=(255, 235, 120) if is_cap else "white", font=cap_f if is_cap else small_f,
            anchor="mb", stroke_width=3, stroke_fill="black")
cim.save(out("preview/cities_preview.png"))
Image.fromarray(heightmap).resize((W // 6, H // 6)).save(out("preview/heightmap_preview.png"))

print(f"{len(vp)} cities")
print(f"map {W}x{H}, {len(DISTRICTS)} states, {len(land_ids)} land provinces, {len(lake_ids)} lake provinces, {len(rails)} rail links")
