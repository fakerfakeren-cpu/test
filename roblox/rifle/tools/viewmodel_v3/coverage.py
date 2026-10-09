"""Arm screen coverage over time, old v1 (in the user's game now) vs new, in-game hip camera."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vmcore as V
import render2 as R2
game, gltf = sys.argv[1:3]
S = V.load_scene(game); inst = S['inst']; bp = S['by_path']; base = S['base']
kids = {}
for r, x in inst.items(): kids.setdefault(x['parent'], []).append(r)
def name(r): return inst[r]['props'].get('Name')
motors = [(name(x['props']['Part0']), name(x['props']['Part1']), V.from_list(x['props']['C0']), V.from_list(x['props']['C1']))
          for p, x in bp.items() if x['class'] == 'Motor6D']
scene = R2.Scene(gltf, S['arm_size'])
def coverage(Wp):
    img = np.array(R2.view(scene, Wp, Wd=192, Hd=108, ss=1)).astype(int)
    return (np.all(np.abs(img - np.array(R2.SLEEVE)) < 60, -1) & (img[..., 0] > img[..., 2] + 20)).mean()
def old_series(seqname, step=3):
    seq = [r for r, x in inst.items() if x is bp[base + '.AnimSaves.' + seqname]][0]
    kfs = sorted([c for c in kids[seq] if inst[c]['class'] == 'Keyframe'], key=lambda c: inst[c]['props']['Time'])
    out = []
    for k in kfs[::step]:
        Tr = {}
        def walk(p, parent):
            for c in kids.get(p, []):
                if inst[c]['class'] == 'Pose':
                    Tr[(parent, name(c))] = V.from_list(inst[c]['props']['CFrame']); walk(c, name(c))
        for c in kids[k]:
            if inst[c]['class'] == 'Pose': walk(c, name(c))
        W = {'HumanoidRootPart': np.eye(4)}
        for _ in range(4):
            for p0, p1, C0, C1 in motors:
                if p0 in W: W[p1] = W[p0] @ C0 @ Tr.get((p0, p1), np.eye(4)) @ V.inv(C1)
        out.append((inst[k]['props']['Time'], coverage(W)))
    return out
def new_series(anim, step=3):
    rig = V.Rig(S)
    length, fps = V.ANIMS[anim][0], V.ANIMS[anim][1]
    n = int(round(length * fps))
    return [(i / fps, coverage(V.ANIMS[anim][4](rig, i / fps))) for i in range(0, n + 1, step)]
for label, ser in (('OLD reload', old_series('Scar_Reload')), ('NEW reload', new_series('Reload')),
                   ('OLD equip', old_series('Scar_Equip')), ('NEW equip', new_series('Equip'))):
    c = np.array([v for _, v in ser])
    tmax = ser[int(np.argmax(c))][0]
    print('%-11s mean %.3f  max %.3f (at %.2fs)  time above 8%%: %.2fs' % (label, c.mean(), c.max(), tmax,
          (c > 0.08).sum() * (ser[1][0] - ser[0][0])))
