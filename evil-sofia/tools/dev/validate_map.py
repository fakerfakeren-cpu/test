"""Own checker for Evil Sofia against the HOI4 1.19 map rules (provinces, states, regions, positions)."""
import sys, os, re, glob, collections
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
root = sys.argv[1]
errs, warns = [], []
def E(m): errs.append(m)
def Wn(m): warns.append(m)
raw = open(f'{root}/map/definition.csv', 'rb').read()
if b'\r\n' not in raw or raw.count(b'\n') != raw.count(b'\r\n'):
    E('definition.csv is not CRLF throughout')
rows = [l.split(';') for l in raw.decode().split('\r\n') if l.strip()]
ids = [int(r[0]) for r in rows]
if ids != list(range(len(ids))): E('definition ids not sequential')
typ = {int(r[0]): r[4] for r in rows}
for r in rows[1:]:
    if r[4] == 'land' and int(r[7]) < 1: E(f'land province {r[0]} continent 0')
    if r[4] != 'land' and int(r[7]) != 0: Wn(f'water province {r[0]} continent {r[7]}')
    if r[5] != 'false': E(f'province {r[0]} coastal={r[5]} but there is no sea')
col = {(int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3]): int(r[0]) for r in rows[1:]}
if len(col) != len(rows) - 1: E('duplicate colours')
im = np.asarray(Image.open(f'{root}/map/provinces.bmp').convert('RGB')).astype(np.int64)
H, W, _ = im.shape
key = (im[..., 0] << 16) | (im[..., 1] << 8) | im[..., 2]
u, inv = np.unique(key, return_inverse=True)
missing = [hex(int(c)) for c in u if int(c) not in col]
if missing: E(f'colours without definition: {missing[:5]}')
pid = np.array([col.get(int(c), -1) for c in u])[inv].reshape(H, W)
area = np.bincount(pid.ravel(), minlength=len(rows))
for i in range(1, len(rows)):
    if area[i] == 0: E(f'province {i} has no pixels')
    elif area[i] <= 8: E(f'province {i} only {area[i]} px')
pw = np.concatenate([pid, pid[:, :1]], 1)
a, b, c, d = pw[:-1, :-1], pw[:-1, 1:], pw[1:, :-1], pw[1:, 1:]
xc = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)
if xc.any(): E(f'{int(xc.sum())} X-crossings (wrap included)')
seam = set(np.unique(pid[:, 0])) & set(np.unique(pid[:, -1]))
if seam: E(f'provinces crossing the wrap seam: {sorted(seam)[:5]}')
sl_all = ndi.find_objects(pid)
tall = []
for i, sl in enumerate(sl_all, 1):
    if sl is None: continue
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if h > min(173, H // 8) or w > min(590, W // 8): tall.append((i, w, h))
    cl, n = ndi.label(pid[sl] == i)
    if n > 1: E(f'province {i} is in {n} pieces')
if tall: E(f'{len(tall)} provinces risk TOO LARGE BOX (h>173 or w>590): {tall[:5]}')
print('provinces', len(rows) - 1, 'max box h', max(sl[0].stop - sl[0].start for sl in sl_all if sl), 'w', max(sl[1].stop - sl[1].start for sl in sl_all if sl))
def block(t, k):
    m = re.search(r'\b' + k + r'\s*=\s*\{([^}]*)\}', t); return [int(v) for v in m.group(1).split()] if m else []
states = {}
for f in glob.glob(f'{root}/history/states/*.txt'):
    t = open(f, encoding='utf-8-sig').read()
    sid = int(re.search(r'\bid\s*=\s*(\d+)', t).group(1)); pv = block(t, 'provinces'); states[sid] = pv
    for vp in re.findall(r'victory_points\s*=\s*\{\s*(\d+)', t):
        if int(vp) not in pv: E(f'state {sid} VP {vp} outside')
if sorted(states) != list(range(1, len(states) + 1)): E('state ids not 1..N')
p2s = {p: s for s, v in states.items() for p in v}
for i, t in typ.items():
    if i and t == 'land' and i not in p2s: E(f'land province {i} in no state')
    if t != 'land' and i in p2s: Wn(f'water province {i} in state')
regions = {}
for f in glob.glob(f'{root}/map/strategicregions/*.txt'):
    t = open(f, encoding='utf-8-sig').read()
    regions[int(re.search(r'\bid\s*=\s*(\d+)', t).group(1))] = block(t, 'provinces')
p2r = collections.Counter(p for v in regions.values() for p in v)
for i in range(1, len(rows)):
    if p2r[i] != 1: E(f'province {i} in {p2r[i]} strategic regions')
r_of = {p: r for r, v in regions.items() for p in v}
for s, v in states.items():
    if len({r_of[p] for p in v}) > 1: E(f'state {s} spans regions')
for rid, mem in regions.items():
    boxes = []
    for q in mem:
        sl = sl_all[q - 1]
        xmin, xmax = sl[1].start, sl[1].stop - 1
        yb0, yb1 = H - sl[0].stop, H - 1 - sl[0].start
        boxes.append((2 * (xmin // 2), 2 * (xmax // 2 + 1), 2 * (yb0 // 2), 2 * (yb1 // 2 + 1)))
    mx = sum((b_[0] + b_[1]) // 2 for b_ in boxes) // len(boxes); my = sum((b_[2] + b_[3]) // 2 for b_ in boxes) // len(boxes)
    inside = any(b_[0] <= mx < b_[1] and b_[2] <= my < b_[3] for b_ in boxes)
    rx0, rx1 = min(b_[0] for b_ in boxes), max(b_[1] for b_ in boxes)
    den = mx - (rx0 + (rx1 - rx0) / 2)
    print(f'region {rid}: {len(mem)} provinces, mean ({mx},{my}) inside a member box: {inside}, divisor {den}')
    if not inside and abs(den) < 1: E(f'region {rid} hits the region-centre divide-by-zero')
for f in ('airports.txt', 'rocketsites.txt'):
    if os.path.exists(f'{root}/map/{f}'): Wn(f'legacy map/{f} present')
STATE_B = {"arms_factory": 6, "industrial_complex": 6, "anti_air_building": 3, "air_base": 1, "synthetic_refinery": 1,
           "radar_station": 1, "fuel_silo": 1, "stronghold_network": 1, "nuclear_reactor_spawn": 1, "rocket_site_spawn": 1}
cnt = collections.Counter(); prov_b = collections.Counter()
for l in open(f'{root}/map/buildings.txt', encoding='utf-8'):
    s_ = l.strip().split(';')
    if len(s_) != 7: E(f'buildings line with {len(s_)} columns'); continue
    sid, bt = int(s_[0]), s_[1]
    x, z = float(s_[2]), float(s_[4]); px, py = int(x), H - 1 - int(z)
    q = pid[py, px]
    if q not in states.get(sid, []): E(f'building {bt} of state {sid} sits in province {q} outside the state')
    cnt[(sid, bt)] += 1
    if bt in ('bunker', 'supply_node', 'special_project_facility_spawn'): prov_b[(q, bt)] += 1
for s in states:
    for bt, n in STATE_B.items():
        if cnt[(s, bt)] != n: E(f'state {s}: {cnt[(s, bt)]} x {bt}, vanilla has {n}')
    for q in states[s]:
        for bt in ('bunker', 'supply_node', 'special_project_facility_spawn'):
            if prov_b[(q, bt)] != 1: E(f'province {q}: {prov_b[(q, bt)]} x {bt}')
LAND_STACKS = {0, 1, 2, 9, 10, 21, 22, 23, 38}
SEA_STACKS = {0, 1, 2, 9, 10, 11, 12, 21, 22, 23, 30, 31, 38}
stack_types = collections.defaultdict(set)
vp_pos = {}
for l in open(f'{root}/map/unitstacks.txt'):
    s_ = l.strip().split(';')
    if len(s_) != 7: E('unitstacks line columns'); continue
    q, t = int(s_[0]), int(s_[1]); px, py = int(float(s_[2])), H - 1 - int(float(s_[4]))
    if pid[py, px] != q: E(f'unit stack {q}/{t} outside its province')
    if t == 38: vp_pos[q] = 1
    stack_types[q].add(t)
for s, v in states.items():
    for q in v:
        if q not in vp_pos: Wn(f'province {q} has no VP marker position')
for i, t_ in typ.items():
    if i == 0: continue
    need = LAND_STACKS if t_ == 'land' else SEA_STACKS if t_ == 'sea' else set()
    if not need <= stack_types.get(i, set()): E(f'{t_} province {i} lacks unit anchors {sorted(need - stack_types.get(i, set()))[:5]}')
tut = open(f'{root}/tutorial/tutorial.txt').read() if os.path.exists(f'{root}/tutorial/tutorial.txt') else ''
if tut.count('tutorial = {') != 1 or re.search(r'\b(state|province)\s*=\s*\d', tut): E('tutorial/tutorial.txt must be one block naming no state or province')
for f in ('map/terrain/colormap_rgb_cityemissivemask_a.dds', 'map/terrain/fow_rgb_waterspec_a.dds', 'map/terrain/colormap_water_0.dds', 'gfx/minimap/minimap.dds', 'gfx/interface/minimap.dds'):
    if not os.path.exists(f'{root}/{f}'): E(f'missing {f}')
for l in open(f'{root}/map/railways.txt'):
    v = [int(z) for z in l.split()]
    if v[1] != len(v) - 2: E('railway count')
    for q in v[2:]:
        if q not in p2s: E(f'railway on {q} not in a state')
for l in open(f'{root}/map/supply_nodes.txt'):
    q = int(l.split()[1])
    if q not in p2s: E(f'supply node {q} not in a state')
locf = f'{root}/localisation/english/replace/evil_sofia_l_english.yml'
if os.path.exists(f'{root}/localisation/english/evil_sofia_l_english.yml'): E('old localisation file outside replace/ still present')
loc = open(locf, 'rb').read()
if not loc.startswith(b'\xef\xbb\xbf'): E('localisation lacks BOM')
if not loc.decode('utf-8-sig').startswith('l_english:'): E('localisation header')
keys = dict(re.findall(r'^\s*([A-Za-z0-9_.]+):0 "(.*)"\s*$', loc.decode('utf-8-sig'), re.M))
vps = [k for k in keys if k.startswith('VICTORY_POINTS_')]
print('VP names', len(vps), 'loc keys', len(keys))
# names: unique keys only (vanilla STATE_n / STRATEGICREGION_n would win), each one localised
owner, names_used, cap_of = {}, collections.Counter(), {}
for f in glob.glob(f'{root}/history/states/*.txt'):
    t = open(f, encoding='utf-8-sig').read()
    sid = int(re.search(r'\bid\s*=\s*(\d+)', t).group(1))
    nk = re.search(r'\bname\s*=\s*"([^"]+)"', t).group(1)
    if re.fullmatch(r'STATE_\d+', nk): E(f'state {sid} uses vanilla-style key {nk}')
    if nk not in keys: E(f'state {sid} name key {nk} not localised')
    else: names_used[keys[nk]] += 1
    owner[sid] = re.search(r'\bowner\s*=\s*(\w+)', t).group(1)
    cat = re.search(r'state_category\s*=\s*(\w+)', t).group(1)
    if cat not in ('megalopolis', 'metropolis', 'large_city', 'city', 'large_town', 'town', 'rural', 'pastoral', 'small_island', 'enclave', 'tiny_island', 'wasteland'):
        E(f'state {sid} category {cat}')
    for vp in re.findall(r'victory_points\s*=\s*\{\s*(\d+)', t):
        if f'VICTORY_POINTS_{vp}' not in keys: E(f'VP {vp} has no name')
dups = [n for n, c in names_used.items() if c > 1]
if dups: E(f'duplicate state names: {dups[:8]}')
for f in glob.glob(f'{root}/map/strategicregions/*.txt'):
    t = open(f, encoding='utf-8-sig').read()
    nk = re.search(r'\bname\s*=\s*"([^"]+)"', t).group(1)
    if re.fullmatch(r'STRATEGICREGION_\d+', nk): E(f'region uses vanilla-style key {nk}')
    if nk not in keys: E(f'region name key {nk} not localised')
    if not block(t, 'provinces'): E(f'empty strategic region {f}')
MICRO_TAGS = {'IAP'}   # one-state countries by design (MICRO in tools/build_map.py)
per_tag = collections.Counter(owner.values())
print('states per country', dict(sorted(per_tag.items())))
for tag, n in per_tag.items():
    if n < 2 and tag not in MICRO_TAGS: E(f'{tag} has only {n} state')   # micro-states have one

    for k_ in (tag, tag + '_ADJ', tag + '_DEF'):
        if k_ not in keys: E(f'missing {k_}')
for f in glob.glob(f'{root}/history/countries/*.txt'):
    tag = os.path.basename(f).split(' ')[0]
    cap = int(re.search(r'capital\s*=\s*(\d+)', open(f, encoding='utf-8-sig').read()).group(1))
    if owner.get(cap) != tag: E(f'{tag} capital state {cap} owned by {owner.get(cap)}')
# every state is one connected piece of land
adjp = collections.defaultdict(set)
for a_, b_ in ((pid[:, :-1], pid[:, 1:]), (pid[:-1, :], pid[1:, :])):
    m_ = a_ != b_
    for x_, y_ in set(zip(a_[m_].tolist(), b_[m_].tolist())):
        adjp[x_].add(y_); adjp[y_].add(x_)
for s, v in states.items():
    seen, todo = {v[0]}, [v[0]]
    while todo:
        q = todo.pop()
        for r in adjp[q]:
            if r in v and r not in seen: seen.add(r); todo.append(r)
    if len(seen) != len(v): E(f'state {s} is not connected ({len(seen)}/{len(v)})')
print(f'{len(errs)} errors, {len(warns)} warnings')
for m in errs[:30]: print('ERROR', m)
for m in collections.Counter(w.split(' ')[0] + ' ' + w.split(' ')[-1] for w in warns).most_common(5): print('WARN', m)
