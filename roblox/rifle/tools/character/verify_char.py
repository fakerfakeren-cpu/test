"""Independent check of the written file: re-parse the .rbxmx, replay every keyframe the way Roblox does
(Part1 = Part0 * C0 * Pose.CFrame * C1^-1, with the LookReplication script's C0 offsets on top), hang the gun
on the right hand through RightGrip with the new Tool.Grip, and measure.

Usage: python -I verify_char.py <Export.gltf> <anims.rbxmx> <grip.json>
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charcore as C  # noqa: E402

gltf, rbxmx, grip_json = sys.argv[1:4]
rig = C.Rig(gltf)
g = json.load(open(grip_json))['grip']
GRIP = C.cf(np.array(g[3:]).reshape(3, 3), g[:3])


def cfr(el):
    v = [float(el.find(t).text) for t in ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']]
    return C.cf(np.array(v[3:]).reshape(3, 3), v[:3])


def props(item):
    return {p.get('name'): p for p in item.find('Properties')}


root = ET.parse(rbxmx).getroot()
seqs = {}
for seq in root.iter('Item'):
    if seq.get('class') != 'KeyframeSequence': continue
    pr = props(seq); name = pr['Name'].text
    frames = []
    for kf in seq.findall('Item'):
        t = float(props(kf)['Time'].text); poses = {}

        def walk(item, parent):
            p = props(item); n = p['Name'].text
            poses[(parent, n)] = (cfr(p['CFrame']), float(p['Weight'].text))
            for c in item.findall('Item'):
                if c.get('class') == 'Pose': walk(c, n)
        for c in kf.findall('Item'):
            if c.get('class') == 'Pose': walk(c, None)
        frames.append((t, poses))
    frames.sort(key=lambda f: f[0])
    seqs[name] = (frames, pr['Loop'].text == 'true', int(pr['Priority'].text))

ok = True


def check(cond, msg):
    global ok
    print(('  ok   ' if cond else '  FAIL ') + msg)
    ok &= bool(cond)


def replay(poses, look):
    Tm = {}
    for j, p0, p1 in C.JOINTS:
        M, w = poses[(p0, p1)]
        check_rot = np.allclose(M[:3, 3], 0, atol=1e-6) and w == 1.0
        if not check_rot: raise SystemExit(f'pose {p1} has translation or weight {w}')
        Tm[j] = M[:3, :3]
    for (p0, p1), (M, w) in poses.items():
        if p1 in ('HumanoidRootPart', 'LowerTorso') and w != 0.0: raise SystemExit(f'{p1} pose must have Weight 0')
    W = rig.fk(Tm, look)
    gun = W['RightHand'] @ rig.A_local @ C.inv(GRIP) @ rig.P_export     # RightGrip weld, then the tool's own welds
    return W, gun


def muzzle_dir(gun):
    return gun[:3, :3] @ np.array([0, 0, 1.0])


LOOKS = {'level': None}
for pitch in (60, 30, -30, -50):            # LookReplication: waist and arms each take half, the neck the rest
    p = np.radians(pitch); LOOKS[f'look {pitch:+d}'] = (0.5 * p, 0.5 * p, np.radians(20), 0.5 * p)

for name, (frames, loop, prio) in seqs.items():
    print(f'{name}: {len(frames)} keyframes, {frames[-1][0]:.3f} s, loop={loop}, priority={prio}')
    worst = {k: 0.0 for k in LOOKS}; elev = {}
    steps = []
    prev = None
    for t, poses in frames:
        for k, look in LOOKS.items():
            W, gun = replay(poses, look)
            # left hand stays where it was relative to the gun (rigid under any look offset)
            if k == 'level': rel0 = C.inv(gun) @ W['LeftHand']
            else: worst[k] = max(worst[k], np.linalg.norm((C.inv(gun) @ W['LeftHand'])[:3, 3] - rel0[:3, 3]))
            if t == 0.0:
                d = muzzle_dir(gun); elev[k] = np.degrees(np.arcsin(d[1])), np.degrees(np.arctan2(-d[0], -d[2]))
        cur = {j: poses[(p0, p1)][0][:3, :3] for j, p0, p1 in C.JOINTS}
        if prev is not None: steps.append(max(C.angle(prev[j].T @ cur[j]) for j in cur))
        prev = cur
    check(max(worst.values()) < 1e-6, f'left hand stays on the gun under every look offset (max drift {max(worst.values()):.1e} studs)')
    check(max(steps) < 20, f'largest joint change between neighbouring keyframes {max(steps):.1f} deg (no flips or snaps)')
    big = max(C.angle(poses[(p0, p1)][0][:3, :3]) for t, poses in frames for j, p0, p1 in C.JOINTS)
    check(big < 150, f'largest joint rotation {big:.0f} deg (well short of 180)')
    if loop:
        a, b = frames[0][1], frames[-1][1]
        d = max(C.angle(a[k][0][:3, :3].T @ b[k][0][:3, :3]) for k in a)
        check(d < 1e-3, f'loop closes ({d:.4f} deg)')
    print('    muzzle at t=0 (elevation, yaw) by look offset:', {k: (round(e, 1), round(y, 1)) for k, (e, y) in elev.items()})

# the same base pose in all three, so Shoot/Reload start and end on Idle
base = {n: seqs[n][0][0][1] for n in seqs}
names = list(seqs)
for n in names[1:]:
    for which in (0, -1):
        d = max(C.angle(base[names[0]][k][0][:3, :3].T @ seqs[n][0][which][1][k][0][:3, :3]) for k in base[n])
        check(d < 1.5, f'{n} {"starts" if which == 0 else "ends"} on the Idle pose (within {d:.2f} deg; Idle breathes)')

# the gun's measured hold against the place the pose was designed for
W, gun = replay(seqs[names[0]][0][0][1], None)
print('  gun body centre at Idle t=0:', np.round(gun[:3, 3], 3), ' muzzle dir', np.round(muzzle_dir(gun), 3))
check(np.linalg.norm(gun[:3, 3] - C.BASE_GUN) < 0.03, 'Tool.Grip puts the gun where the hold was built')
print('ALL OK' if ok else 'SOME CHECKS FAILED')
sys.exit(0 if ok else 1)
