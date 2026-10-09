"""Build ScarViewmodel.rbxmx from the user's real AutoBlaster viewmodel + the new rig and animations.

Usage: python -I build.py <game.json> <out.rbxmx> <frames.json>
Parts, meshes, textures, muzzle attachment and both particle emitters are copied value-for-value from
ReplicatedStorage.Blaster.ViewModels.AutoBlaster in the user's place. Only the joints, the rest pose of the
arms and the AnimSaves are new. No scripts, no sounds, no extra parts.
"""
import json
import os
import sys
import uuid
from xml.sax.saxutils import escape

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vmcore as V  # noqa: E402

game_json, out_path, frames_path = sys.argv[1], sys.argv[2], sys.argv[3]
S = V.load_scene(game_json)
rig = V.Rig(S)
BP, BASE = S['by_path'], S['base']
H = S['H_world']


def src(p):
    return BP[BASE + p]['props']


def num(v):
    v = float(v)
    if abs(v) < 5e-13:
        v = 0.0
    r = repr(v)
    return r[:-2] if r.endswith('.0') else r


def cf_xml(name, M):
    v = V.to_list(M)
    tags = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
    return f'<CoordinateFrame name="{name}">' + ''.join(f'<{t}>{num(x)}</{t}>' for t, x in zip(tags, v)) + '</CoordinateFrame>'


def v3_xml(name, v):
    return f'<Vector3 name="{name}"><X>{num(v[0])}</X><Y>{num(v[1])}</Y><Z>{num(v[2])}</Z></Vector3>'


def prop(name, kind, value):
    if kind == 'string':
        return f'<string name="{name}">{escape(value)}</string>'
    if kind == 'bool':
        return f'<bool name="{name}">{"true" if value else "false"}</bool>'
    if kind == 'float':
        return f'<float name="{name}">{num(value)}</float>'
    if kind == 'int':
        return f'<int name="{name}">{int(value)}</int>'
    if kind == 'token':
        return f'<token name="{name}">{int(value)}</token>'
    if kind == 'Vector3':
        return v3_xml(name, value)
    if kind == 'Vector2':
        return f'<Vector2 name="{name}"><X>{num(value[0])}</X><Y>{num(value[1])}</Y></Vector2>'
    if kind == 'CFrame':
        return cf_xml(name, value)
    if kind == 'Content':
        return f'<Content name="{name}"><url>{escape(value)}</url></Content>' if value else f'<Content name="{name}"><null></null></Content>'
    if kind == 'Color3uint8':
        r, g, b = value
        return f'<Color3uint8 name="{name}">{0xFF000000 | (r << 16) | (g << 8) | b}</Color3uint8>'
    if kind == 'NumberSequence':
        return f'<NumberSequence name="{name}">' + ''.join(f'{num(t)} {num(v)} {num(e)} ' for t, v, e in value) + '</NumberSequence>'
    if kind == 'ColorSequence':
        return f'<ColorSequence name="{name}">' + ''.join(f'{num(t)} {num(r)} {num(g)} {num(b)} {num(e)} ' for t, r, g, b, e in value) + '</ColorSequence>'
    if kind == 'NumberRange':
        return f'<NumberRange name="{name}">{num(value[0])} {num(value[1])} </NumberRange>'
    if kind == 'Ref':
        return f'<Ref name="{name}">{value or "null"}</Ref>'
    raise ValueError(kind)


class Item:
    def __init__(self, cls, name):
        self.cls, self.ref, self.props, self.kids = cls, 'RBX' + uuid.uuid4().hex.upper(), [('Name', 'string', name)], []
        self.name = name

    def add(self, *props):
        self.props += list(props); return self

    def child(self, item):
        self.kids.append(item); return item

    def xml(self, out, ind):
        t = '\t' * ind
        out.append(f'{t}<Item class="{self.cls}" referent="{self.ref}">')
        out.append(f'{t}\t<Properties>')
        for n, k, v in self.props:
            out.append(f'{t}\t\t' + prop(n, k, v))
        out.append(f'{t}\t</Properties>')
        for c in self.kids:
            c.xml(out, ind + 1)
        out.append(f'{t}</Item>')


# ---- copy helpers: same values as the user's instances
BOOL_PROPS = ['Anchored', 'CanCollide', 'CanTouch', 'CanQuery', 'CastShadow', 'Massless', 'Locked']
SURF = ['TopSurface', 'BottomSurface', 'LeftSurface', 'RightSurface', 'FrontSurface', 'BackSurface']


def part_from(cls, path, world_cf):
    p = src(path)
    it = Item(cls, p['Name'])
    it.add(('CFrame', 'CFrame', world_cf), ('size', 'Vector3', p['size']))
    for k in BOOL_PROPS:
        it.add((k, 'bool', p[k]))
    it.add(('Transparency', 'float', p['Transparency']), ('Reflectance', 'float', p['Reflectance']),
           ('Color3uint8', 'Color3uint8', p['Color3uint8']), ('Material', 'token', p['Material']),
           ('CollisionGroup', 'string', p['CollisionGroup']), ('PivotOffset', 'CFrame', V.from_list(p['PivotOffset'])))
    for k in SURF:
        it.add((k, 'token', p[k]))
    if cls == 'Part':
        it.add(('shape', 'token', p['shape']))
    else:
        it.add(('MeshId', 'Content', p['MeshId']), ('TextureID', 'Content', p['TextureID']),
               ('InitialSize', 'Vector3', p['InitialSize']), ('DoubleSided', 'bool', p['DoubleSided']),
               ('RenderFidelity', 'token', p['RenderFidelity']))
    return it


EMITTER_KINDS = {
    'Acceleration': 'Vector3', 'Brightness': 'float', 'Color': 'ColorSequence', 'Drag': 'float', 'EmissionDirection': 'token',
    'Enabled': 'bool', 'FlipbookBlendFrames': 'bool', 'FlipbookFramerate': 'NumberRange', 'FlipbookLayout': 'token',
    'FlipbookMode': 'token', 'FlipbookSizeX': 'int', 'FlipbookSizeY': 'int', 'FlipbookStartRandom': 'bool',
    'Lifetime': 'NumberRange', 'LightEmission': 'float', 'LightInfluence': 'float', 'LockedToPart': 'bool',
    'Orientation': 'token', 'Rate': 'float', 'RotSpeed': 'NumberRange', 'Rotation': 'NumberRange', 'Shape': 'token',
    'ShapeInOut': 'token', 'ShapePartial': 'float', 'ShapeStyle': 'token', 'Size': 'NumberSequence', 'Speed': 'NumberRange',
    'SpreadAngle': 'Vector2', 'Squash': 'NumberSequence', 'Texture': 'Content', 'TimeScale': 'float',
    'Transparency': 'NumberSequence', 'VelocityInheritance': 'float', 'WindAffectsDrag': 'bool', 'ZOffset': 'float',
}


def emitter_from(path):
    p = src(path)
    it = Item('ParticleEmitter', p['Name'])
    for k, kind in EMITTER_KINDS.items():
        it.add((k, kind, p[k]))
    missing = set(p) - set(EMITTER_KINDS) - {'Name', 'AttributesSerialize', 'Capabilities', 'DefinesCapabilities', 'HistoryId',
                                              'UniqueId', 'SourceAssetId', 'Tags', 'SerializedOverrides', 'FlipbookIncompatible'}
    assert not missing, missing
    return it


# ---- tree
R = rig.rest
model = Item('Model', 'AutoBlaster')
ac = model.child(Item('AnimationController', 'AnimationController'))
ac.child(Item('Animator', 'Animator'))
anims_folder = model.child(Item('Folder', 'Animations'))
for n in ('Idle', 'Reload', 'Shoot', 'Equip'):
    anims_folder.child(Item('Animation', n).add(('AnimationId', 'Content', src(f'.Animations.{n}')['AnimationId'])))

scar = model.child(Item('Model', 'Scar'))
parts = {}
parts['Body'] = scar.child(part_from('MeshPart', '.Scar.Body', H @ R['Body']))
parts['Magazine'] = scar.child(part_from('MeshPart', '.Scar.Magazine', H @ R['Magazine']))
parts['Slide'] = scar.child(part_from('MeshPart', '.Scar.Slide', H @ R['Slide']))
muzzle = parts['Body'].child(Item('Attachment', 'MuzzleAttachment').add(
    ('CFrame', 'CFrame', S['muzzle_local']), ('Visible', 'bool', src('.Scar.Body.MuzzleAttachment')['Visible'])))
muzzle.child(emitter_from('.Scar.Body.MuzzleAttachment.FlashEmitter'))
muzzle.child(emitter_from('.Scar.Body.MuzzleAttachment.CircleEmitter'))

saves = model.child(Item('ObjectValue', 'AnimSaves').add(('Value', 'Ref', None)))
parts['HumanoidRootPart'] = model.child(part_from('Part', '.HumanoidRootPart', H))
parts['RightArm'] = model.child(part_from('Part', '.RightArm', H @ R['RightArm']))
parts['LeftArm'] = model.child(part_from('Part', '.LeftArm', H @ R['LeftArm']))
model.add(('PrimaryPart', 'Ref', parts['HumanoidRootPart'].ref))

for name, p0, p1, C0, C1 in rig.joints:          # Motor6D parented to Part0, like the user's Glock viewmodel
    parts[p0].child(Item('Motor6D', name).add(('Part0', 'Ref', parts[p0].ref), ('Part1', 'Ref', parts[p1].ref),
                                              ('C0', 'CFrame', C0), ('C1', 'CFrame', C1)))

# ---- animations
TREE = {}
for _n, _p0, _p1, _c0, _c1 in rig.joints:
    TREE.setdefault(_p0, []).append(_p1)
JOINT_OF = {p1: name for name, p0, p1, C0, C1 in rig.joints}
frames_out = {}
for anim, (length, fps, loop, prio, fn, markers, keyed) in V.ANIMS.items():
    seq = saves.child(Item('KeyframeSequence', 'Scar_' + anim).add(('Loop', 'bool', loop), ('Priority', 'token', prio)))
    frames = V.sample(rig, anim)
    keyed_parts = None if keyed is None else {p1 for n, p0, p1, C0, C1 in rig.joints if n in keyed}
    frames_out[anim] = []
    for t, W, Tm in frames:
        kf = seq.child(Item('Keyframe', 'Keyframe').add(('Time', 'float', t)))

        def pose(part, parent_item):
            if part != 'HumanoidRootPart' and keyed_parts is not None and part not in keyed_parts:
                return
            M = np.eye(4) if part == 'HumanoidRootPart' else Tm[JOINT_OF[part]]
            pi = parent_item.child(Item('Pose', part).add(('CFrame', 'CFrame', M), ('Weight', 'float', 1.0),
                                                          ('EasingStyle', 'token', 0), ('EasingDirection', 'token', 0)))
            for c in TREE.get(part, []):
                pose(c, pi)
        pose('HumanoidRootPart', kf)
        for mt, mname, mval in markers:
            if abs(mt - t) < 1e-6:
                kf.child(Item('KeyframeMarker', mname).add(('Value', 'string', mval)))
        frames_out[anim].append({'t': t, 'W': {k: V.to_list(v) for k, v in W.items()}})
    hit = {round(mt, 6) for mt, _, _ in markers} - {round(t, 6) for t, _, _ in frames}
    assert not hit, (anim, hit)

lines = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
         'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
         '\t<External>null</External>', '\t<External>nil</External>']
model.xml(lines, 1)
lines.append('</roblox>')
open(out_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def count(it):
    return 1 + sum(count(c) for c in it.kids)


json.dump({'H_world': V.to_list(H), 'frames': frames_out,
           'joints': [(n, p0, p1, V.to_list(C0), V.to_list(C1)) for n, p0, p1, C0, C1 in rig.joints],
           'rest': {k: V.to_list(v) for k, v in R.items()}, 'sizes': {k: list(v) for k, v in S['sizes'].items()},
           'markers': {a: [(mt, mn, mv) for mt, mn, mv in V.ANIMS[a][5]] for a in V.ANIMS}},
          open(frames_path, 'w'))
print('wrote', out_path, count(model), 'instances')
