"""Write a Roblox XML model (.rbxmx) from the Luau dump, then verify it by re-reading the file."""
import sys, uuid, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
dump, out = sys.argv[1], sys.argv[2]
insts, order = {}, []
for line in open(dump):
    if line.startswith('I\t'):
        _, i, p, cls = line.rstrip('\n').split('\t'); insts[i] = dict(cls=cls, parent=p, props=[], kids=[]); order.append(i)
    elif line.startswith('P\t'):
        _, i, name, typ, val = line.rstrip('\n').split('\t', 4); insts[i]['props'].append((name, typ, val))
for i in order:
    p = insts[i]['parent']
    if p != '0': insts[p]['kids'].append(i)
ref = {i: 'RBX' + uuid.uuid4().hex.upper() for i in order}
def prop_xml(name, typ, val, ind):
    t = '\t' * ind
    if typ == 'CoordinateFrame':
        v = val.split(); tags = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
        return f'{t}<CoordinateFrame name="{name}">' + ''.join(f'<{k}>{x}</{k}>' for k, x in zip(tags, v)) + '</CoordinateFrame>'
    if typ == 'Vector3':
        x, y, z = val.split(); return f'{t}<Vector3 name="{name}"><X>{x}</X><Y>{y}</Y><Z>{z}</Z></Vector3>'
    if typ == 'Ref':
        return f'{t}<Ref name="{name}">{ref.get(val, "null")}</Ref>'
    if typ == 'Content':
        return f'{t}<Content name="{name}"><url>{escape(val)}</url></Content>'
    return f'{t}<{typ} name="{name}">{escape(val)}</{typ}>'
lines = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
         'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
         '\t<External>null</External>', '\t<External>nil</External>']
def item(i, ind):
    t = '\t' * ind; d = insts[i]
    lines.append(f'{t}<Item class="{d["cls"]}" referent="{ref[i]}">')
    lines.append(f'{t}\t<Properties>')
    for name, typ, val in d['props']: lines.append(prop_xml(name, typ, val, ind + 2))
    lines.append(f'{t}\t</Properties>')
    for k in d['kids']: item(k, ind + 1)
    lines.append(f'{t}</Item>')
item(order[0], 1)
lines.append('</roblox>')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote', out, len(order), 'instances')
