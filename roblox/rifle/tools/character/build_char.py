"""Write the third-person animations as KeyframeSequences for the R15 rig's AnimSaves.

Usage: python -I build_char.py <Export.gltf> <out.rbxmx> <grip.json>
The pose tree matches the user's existing R15 animations: HumanoidRootPart and LowerTorso are placeholders
(Weight 0, so walking still drives the hips and legs), UpperTorso/Head/arms are keyed every frame.
grip.json receives the Tool.Grip the hold was built for.
"""
import json
import os
import sys
import uuid
from xml.sax.saxutils import escape

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charcore as C  # noqa: E402

PREFIX = 'Scar3P_'
TREE = {'HumanoidRootPart': ['LowerTorso'], 'LowerTorso': ['UpperTorso'],
        'UpperTorso': ['Head', 'RightUpperArm', 'LeftUpperArm'],
        'RightUpperArm': ['RightLowerArm'], 'RightLowerArm': ['RightHand'],
        'LeftUpperArm': ['LeftLowerArm'], 'LeftLowerArm': ['LeftHand']}


def num(v):
    v = float(v)
    if abs(v) < 5e-13: v = 0.0
    r = repr(v)
    return r[:-2] if r.endswith('.0') else r


def cf_list(M):
    return [M[0, 3], M[1, 3], M[2, 3], *M[:3, :3].ravel()]


def prop(name, kind, value):
    if kind == 'string': return f'<string name="{name}">{escape(value)}</string>'
    if kind == 'bool': return f'<bool name="{name}">{"true" if value else "false"}</bool>'
    if kind == 'float': return f'<float name="{name}">{num(value)}</float>'
    if kind == 'token': return f'<token name="{name}">{int(value)}</token>'
    if kind == 'Ref': return f'<Ref name="{name}">{value or "null"}</Ref>'
    if kind == 'CFrame':
        tags = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
        return f'<CoordinateFrame name="{name}">' + ''.join(f'<{t}>{num(x)}</{t}>' for t, x in zip(tags, cf_list(value))) + '</CoordinateFrame>'
    raise ValueError(kind)


class Item:
    def __init__(self, cls, name):
        self.cls, self.ref, self.props, self.kids = cls, 'RBX' + uuid.uuid4().hex.upper(), [('Name', 'string', name)], []

    def add(self, *props):
        self.props += list(props); return self

    def child(self, item):
        self.kids.append(item); return item

    def xml(self, out, ind):
        t = '\t' * ind
        out.append(f'{t}<Item class="{self.cls}" referent="{self.ref}">')
        out.append(f'{t}\t<Properties>')
        out += [f'{t}\t\t' + prop(n, k, v) for n, k, v in self.props]
        out.append(f'{t}\t</Properties>')
        for c in self.kids: c.xml(out, ind + 1)
        out.append(f'{t}</Item>')


def build(gltf, out_path, grip_path):
    rig = C.Rig(gltf); P = C.Poser(rig)
    saves = Item('ObjectValue', 'AnimSaves').add(('Value', 'Ref', None))
    for anim, (length, fps, loop, prio, fn) in C.ANIMS.items():
        seq = saves.child(Item('KeyframeSequence', PREFIX + anim).add(('Loop', 'bool', loop), ('Priority', 'token', prio)))
        for t, Tm, W, G, lp in P.sample(anim):
            kf = seq.child(Item('Keyframe', 'Keyframe').add(('Time', 'float', t)))

            def pose(part, parent):
                keyed = part in C.JOINT_OF
                M = C.cf(Tm[C.JOINT_OF[part]]) if keyed else np.eye(4)
                it = parent.child(Item('Pose', part).add(('CFrame', 'CFrame', M), ('Weight', 'float', 1.0 if keyed else 0.0),
                                                         ('EasingStyle', 'token', 0), ('EasingDirection', 'token', 0)))
                for c in TREE.get(part, []): pose(c, it)
            pose('HumanoidRootPart', kf)
    lines = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
             '\t<External>null</External>', '\t<External>nil</External>']
    saves.xml(lines, 1)
    lines.append('</roblox>')
    open(out_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    json.dump({'grip': cf_list(P.grip), 'K_h': cf_list(P.K_h)}, open(grip_path, 'w'), indent=1)
    print('wrote', out_path, 'grip', np.round(cf_list(P.grip), 4).tolist())


if __name__ == '__main__':
    build(*sys.argv[1:4])
