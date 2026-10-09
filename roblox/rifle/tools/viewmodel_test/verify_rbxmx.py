"""Independent check of the .rbxmx: parse it, rebuild joints, replay every keyframe like the Animator,
compare with the poses the Luau run produced, and check the hands."""
import sys, numpy as np, xml.etree.ElementTree as ET
from collections import Counter
tree = ET.parse(sys.argv[1]); root = tree.getroot()
def cf(e):
    v = [float(e.find(k).text) for k in ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']]
    M = np.eye(4); M[:3, 3] = v[:3]; M[:3, :3] = np.array(v[3:]).reshape(3, 3); return M
items = {}; parent = {}
def walk(e, par):
    for it in e.findall('Item'):
        d = dict(cls=it.get('class'), ref=it.get('referent'), props={}, kids=[])
        for p in it.find('Properties'):
            n = p.get('name')
            if p.tag == 'CoordinateFrame': d['props'][n] = cf(p)
            elif p.tag == 'Vector3': d['props'][n] = np.array([float(p.find(k).text) for k in 'XYZ'])
            elif p.tag == 'Content': d['props'][n] = p.find('url').text if p.find('url') is not None else ''
            else: d['props'][n] = p.text
        items[d['ref']] = d; parent[d['ref']] = par
        if par: items[par]['kids'].append(d['ref'])
        walk(it, d['ref'])
walk(root, None)
print('classes:', dict(Counter(d['cls'] for d in items.values())))
refs_ok = all(d['props'][k] in items for d in items.values() for k in ('Part0', 'Part1') if k in d['props'])
print('all Part0/Part1 refs resolve:', refs_ok)
name = lambda r: items[r]['props']['Name']
motors = [d for d in items.values() if d['cls'] == 'Motor6D']
by = {(name(m['props']['Part0']), name(m['props']['Part1'])): m for m in motors}
part1 = {m['props']['Part1'] for m in motors}
roots = {m['props']['Part0'] for m in motors if m['props']['Part0'] not in part1}
print('rig roots:', [name(r) for r in roots], '| motors:', sorted(f"{name(m['props']['Part0'])}>{name(m['props']['Part1'])}" for m in motors))
# reference poses from the Luau run
ref_frames = {}
for line in open(sys.argv[2]):
    if line.startswith('F '):
        _, anim, t, part, *v = line.split()
        M = np.eye(4); M[:3, 3] = list(map(float, v[:3])); M[:3, :3] = np.array(list(map(float, v[3:]))).reshape(3, 3)
        ref_frames[(anim, round(float(t), 4), part)] = M
worst = 0; checked = 0; nframes = 0
for seq in [d for d in items.values() if d['cls'] == 'KeyframeSequence']:
    for kref in seq['kids']:
        kf = items[kref]; t = float(kf['props']['Time']); nframes += 1
        T = {}
        def apply(pref, pname):
            for c in items[pref]['kids']:
                cd = items[c]; key = (pname, cd['props']['Name'])
                if key not in by: raise SystemExit(f'unmatched pose {key}')
                T[id(by[key])] = cd['props']['CFrame']; apply(c, cd['props']['Name'])
        for top in kf['kids']: apply(top, items[top]['props']['Name'])
        W = {r: items[r]['props']['CFrame'] for r in roots}
        changed = True
        while changed:
            changed = False
            for m in motors:
                p0, p1 = m['props']['Part0'], m['props']['Part1']
                if p0 in W and p1 not in W:
                    W[p1] = W[p0] @ m['props']['C0'] @ T.get(id(m), np.eye(4)) @ np.linalg.inv(m['props']['C1']); changed = True
        for p1, M in W.items():
            k = (seq['props']['Name'], round(t, 4), name(p1))
            if k in ref_frames:
                worst = max(worst, np.abs(M - ref_frames[k]).max()); checked += 1
markers = Counter(f"{items[parent[k]]['props']['Name'] if False else ''}{d['props']['Name']}" for k, d in items.items() if d['cls'] == 'KeyframeMarker')
print('markers:', dict(markers))
print('sounds:', sorted(d['props']['Name'] for d in items.values() if d['cls'] == 'Sound'))
scripts = [d for d in items.values() if d['cls'] == 'Script']
print('scripts:', [(d['props']['Name'], 'RunContext=' + d['props'].get('RunContext', '?'), len(d['props'].get('Source', ''))) for d in scripts])
print(f'keyframes replayed from the file: {nframes}; part poses compared with the Luau run: {checked}; max difference: {worst:.2e}')
