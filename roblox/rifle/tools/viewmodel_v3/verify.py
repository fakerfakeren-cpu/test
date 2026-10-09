"""Independent check of ScarViewmodel.rbxmx against the user's place and the intended motion.

Usage: python -I verify.py <ScarViewmodel.rbxmx> <frames.json> <game.json>
"""
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter

import numpy as np

rbxmx, frames_path, game_json = sys.argv[1:4]
TAGS = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']


def cf(e):
    v = [float(e.find(k).text) for k in TAGS]
    M = np.eye(4); M[:3, 3] = v[:3]; M[:3, :3] = np.array(v[3:]).reshape(3, 3); return M


def L(v):
    M = np.eye(4); M[:3, 3] = v[:3]; M[:3, :3] = np.array(v[3:12]).reshape(3, 3); return M


items, parent = {}, {}


def walk(e, par):
    for it in e.findall('Item'):
        d = dict(cls=it.get('class'), ref=it.get('referent'), props={}, kids=[], raw={})
        for p in it.find('Properties'):
            n = p.get('name'); d['raw'][n] = p
            if p.tag == 'CoordinateFrame':
                d['props'][n] = cf(p)
            elif p.tag == 'Vector3':
                d['props'][n] = np.array([float(p.find(k).text) for k in 'XYZ'])
            elif p.tag == 'Content':
                d['props'][n] = p.find('url').text if p.find('url') is not None else ''
            else:
                d['props'][n] = p.text or ''
        items[d['ref']] = d; parent[d['ref']] = par
        if par:
            items[par]['kids'].append(d['ref'])
        walk(it, d['ref'])


walk(ET.parse(rbxmx).getroot(), None)
name = lambda r: items[r]['props']['Name']
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


classes = Counter(d['cls'] for d in items.values())
print('classes:', dict(classes))
check(classes.get('Script', 0) + classes.get('LocalScript', 0) + classes.get('ModuleScript', 0) == 0, 'scripts present')
check(classes.get('Sound', 0) + classes.get('AudioPlayer', 0) == 0, 'sounds present')
partnames = sorted(name(r) for r, d in items.items() if d['cls'] in ('Part', 'MeshPart'))
print('parts:', partnames)
check(partnames == sorted(['HumanoidRootPart', 'RightArm', 'LeftArm', 'Body', 'Magazine', 'Slide']), 'unexpected parts')
check(not any(name(r) == 'Blaster' for r in items), 'Blaster still present')
model = [r for r in items if parent[r] is None][0]
check(items[model]['props']['PrimaryPart'] in items and name(items[model]['props']['PrimaryPart']) == 'HumanoidRootPart', 'PrimaryPart')
muz = [r for r in items if name(r) == 'MuzzleAttachment']
check(len(muz) == 1 and sorted(name(k) for k in items[muz[0]]['kids']) == ['CircleEmitter', 'FlashEmitter'], 'muzzle/emitters')
anims = {name(k): items[k]['props']['AnimationId'] for k in items if items[k]['cls'] == 'Animation'}
print('Animations folder:', anims)

# ---- joints
motors = [d for d in items.values() if d['cls'] == 'Motor6D']
by = {(name(m['props']['Part0']), name(m['props']['Part1'])): m for m in motors}
print('joints:', sorted(f"{name(m['props']['Part0'])} -> {name(m['props']['Part1'])} ({m['props']['Name']}, under {name(parent[m['ref']])})" for m in motors))
part_cf = {name(r): d['props']['CFrame'] for r, d in items.items() if d['cls'] in ('Part', 'MeshPart')}
# rest pose consistency: Part1 == Part0 * C0 * C1^-1
worst_rest = max(np.abs(part_cf[a] @ m['props']['C0'] @ np.linalg.inv(m['props']['C1']) - part_cf[b]).max() for (a, b), m in by.items())
print(f'rest pose: Part0*C0*C1^-1 vs Part1 max diff {worst_rest:.1e}')
check(worst_rest < 1e-5, 'rest pose inconsistent')

# ---- compare against the user's place: unchanged things stay unchanged
G = json.load(open(game_json))
inst = {x['ref']: x for x in G['instances']}


def gpath(r):
    parts = []
    while r in inst:
        parts.append(inst[r]['props'].get('Name', '?')); r = inst[r]['parent']
    return '.'.join(reversed(parts))


base = 'ReplicatedStorage.Blaster.ViewModels.AutoBlaster'
old = {gpath(r)[len(base) + 1:]: x for r, x in inst.items() if gpath(r).startswith(base + '.')}
H = part_cf['HumanoidRootPart']
check(np.abs(H - L(old['HumanoidRootPart']['props']['CFrame'])).max() < 1e-6, 'HRP moved')
for p in ('Scar.Body', 'Scar.Magazine', 'Scar.Slide'):
    nm = p.split('.')[-1]
    o = L(old[p]['props']['CFrame'])
    d = np.abs(part_cf[nm] - o).max()
    print(f'{nm}: rest CFrame vs your current one: max diff {d:.1e}')
    check(d < 1e-5, f'{nm} moved (gun rest pose must stay for the ADS offset)')
    for k in ('MeshId', 'TextureID'):
        check(items[[r for r in items if name(r) == nm][0]]['props'][k] == old[p]['props'][k], f'{nm}.{k}')
mz = items[muz[0]]['props']['CFrame']
check(np.abs(mz - L(old['Scar.Body.MuzzleAttachment']['props']['CFrame'])).max() < 1e-7, 'muzzle moved')
for em in ('FlashEmitter', 'CircleEmitter'):
    r = [k for k in items if name(k) == em][0]
    raw = items[r]['raw']; o = old['Scar.Body.MuzzleAttachment.' + em]['props']
    bad = []
    for k, e in raw.items():
        if k == 'Name':
            continue
        ov = o[k]
        if e.tag in ('float',):
            ok = abs(float(e.text) - ov) < 1e-6
        elif e.tag == 'bool':
            ok = (e.text == 'true') == ov
        elif e.tag in ('token', 'int'):
            ok = int(e.text) == ov
        elif e.tag in ('NumberSequence', 'ColorSequence', 'NumberRange'):
            ok = np.allclose([float(x) for x in e.text.split()], np.array(ov).reshape(-1))
        elif e.tag in ('Vector3', 'Vector2'):
            ok = np.allclose([float(e.find(a).text) for a in 'XYZ'[:len(ov)]], ov)
        elif e.tag == 'Content':
            ok = e.find('url').text == ov
        else:
            ok = False
        if not ok:
            bad.append(k)
    print(f'{em}: {len(raw) - 1} properties, mismatches vs your place: {bad}')
    check(not bad, em)

# ---- sounds: every marker must name something in StarterPack.AutoBlaster.Sounds
snd = {gpath(r)[len('StarterPack.AutoBlaster.Sounds.'):]: x['class'] for r, x in inst.items()
       if gpath(r).startswith('StarterPack.AutoBlaster.Sounds.')}
players = {k for k, c in snd.items() if c == 'AudioPlayer' and '.' not in k}
folders = {k for k, c in snd.items() if c == 'Folder'}
print('tool sounds:', sorted(players), 'folders:', sorted(folders))

# ---- replay every keyframe like the Animator
F = json.load(open(frames_path))
Hw = L(F['H_world'])
seqs = {name(r): r for r, d in items.items() if d['cls'] == 'KeyframeSequence'}
worst = 0.0; nposes = 0
for sname, sref in sorted(seqs.items()):
    anim = sname.replace('Scar_', '')
    kfs = sorted(items[sref]['kids'], key=lambda k: float(items[k]['props']['Time']))
    mk = []
    for k in kfs:
        for c in items[k]['kids']:
            if items[c]['cls'] == 'KeyframeMarker':
                mk.append((round(float(items[k]['props']['Time']), 4), name(c), items[c]['props']['Value']))
    for t, mname, val in mk:
        ok = (mname == 'Sound' and val in players) or (mname == 'RandomSound' and val in folders)
        check(ok, f'{sname}: marker {mname}={val} does not match a sound in the AutoBlaster tool')
    print(f'{sname}: loop={items[sref]["props"]["Loop"]} priority={items[sref]["props"]["Priority"]} keyframes={len(kfs)} '
          f'length={float(items[kfs[-1]]["props"]["Time"]):.3f}s markers={mk}')
    ref_frames = F['frames'][anim]
    for k, fr in zip(kfs, ref_frames):
        T = {}

        def apply(pref, pname):
            for c in items[pref]['kids']:
                cd = items[c]
                if cd['cls'] != 'Pose':
                    continue
                key = (pname, cd['props']['Name'])
                check(key in by, f'{sname}: pose {key} has no joint')
                T[key] = cd['props']['CFrame']
                R = T[key][:3, :3]
                check(np.abs(R @ R.T - np.eye(3)).max() < 1e-5, f'{sname}: non-orthonormal pose')
                apply(c, cd['props']['Name'])
        for top in items[k]['kids']:
            if items[top]['cls'] == 'Pose':
                apply(top, items[top]['props']['Name'])
        W = {'HumanoidRootPart': H}
        for _ in range(4):
            for (a, b), m in by.items():
                if a in W and b not in W:
                    W[b] = W[a] @ m['props']['C0'] @ T.get((a, b), np.eye(4)) @ np.linalg.inv(m['props']['C1'])
        keyed = {b for (a, b) in T}
        for part, M in W.items():
            if part == 'HumanoidRootPart' or part not in keyed:
                continue
            ref = Hw @ L(fr['W'][part])
            worst = max(worst, np.abs(M - ref).max()); nposes += 1
print(f'replayed {nposes} part poses from the file: max diff vs intended motion {worst:.1e}')
check(worst < 1e-4, 'replay mismatch')

# ---- motion sanity on the intended frames (HRP frame)
fr = {a: [(f['t'], {k: L(v) for k, v in f['W'].items()}) for f in F['frames'][a]] for a in F['frames']}
rest = {k: L(v) for k, v in F['rest'].items()}


def diff(A, B, parts=('Body', 'Magazine', 'Slide', 'RightArm', 'LeftArm')):
    return max(np.abs(A[p] - B[p]).max() for p in parts)


print(f"Idle loop seam (first vs last frame): {diff(fr['Idle'][0][1], fr['Idle'][-1][1]):.1e}")
check(diff(fr['Idle'][0][1], fr['Idle'][-1][1]) < 1e-9, 'idle seam')
import os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vmcore as V  # noqa: E402  (same folder; only for idle(t) at the equip's end time)
S = V.load_scene(game_json); rig = V.Rig(S)
te, We = fr['Equip'][-1]
print(f"Equip last frame vs Idle at the same clock time ({te}s): {diff(We, V.anim_idle(rig, te)):.1e}")
check(diff(We, V.anim_idle(rig, te)) < 1e-9, 'equip->idle handoff')
for a in ('Shoot', 'Reload'):
    print(f"{a}: first frame vs rest {diff(fr[a][0][1], rest):.1e}, last frame vs rest {diff(fr[a][-1][1], rest):.1e}")
    check(diff(fr[a][0][1], rest) < 1e-9 and diff(fr[a][-1][1], rest) < 1e-9, f'{a} start/end')
# biggest per-frame jump of any part (studs or rotation-matrix units)
for a, frames in fr.items():
    jumps = [diff(frames[i][1], frames[i + 1][1]) for i in range(len(frames) - 1)]
    i = int(np.argmax(jumps))
    print(f'{a}: largest frame-to-frame change {jumps[i]:.3f} at t={frames[i][0]:.3f}')
# right hand stays on the grip; left hand where it should be at rest
for a, frames in fr.items():
    if a == 'Shoot':
        continue
    err = max(np.linalg.norm(V.pt(W['RightArm'], [0, 0, -2]) - V.pt(W['Body'], V.RIGHT_HAND_BODY)) for t, W in frames)
    print(f'{a}: right hand off the grip by at most {err:.1e}')
    check(err < 1e-9, f'{a}: right hand slipped')
print('\nRESULT:', 'PASS' if not fails else 'FAIL')
for f in fails:
    print('  -', f)
