"""Minimal binary FBX reader: prints GlobalSettings axes/units, model transforms, vertex ranges."""
import struct, zlib, sys, numpy as np
b = open(sys.argv[1], 'rb').read()
assert b[:21] == b'Kaydara FBX Binary  \x00'
ver = struct.unpack('<I', b[23:27])[0]; W = 8 if ver >= 7500 else 4
def prop(o):
    t = chr(b[o]); o += 1
    if t in 'YCIFDL':
        fmt = {'Y': '<h', 'C': '<?', 'I': '<i', 'F': '<f', 'D': '<d', 'L': '<q'}[t]; s = struct.calcsize(fmt)
        return struct.unpack(fmt, b[o:o + s])[0], o + s
    if t in 'fdlib':
        n, enc, cl = struct.unpack('<III', b[o:o + 12]); o += 12; raw = b[o:o + cl]; o += cl
        if enc: raw = zlib.decompress(raw)
        return np.frombuffer(raw, {'f': '<f4', 'd': '<f8', 'l': '<i8', 'i': '<i4', 'b': '<i1'}[t]), o
    if t in 'SR':
        n = struct.unpack('<I', b[o:o + 4])[0]; o += 4; return b[o:o + n], o + n
    raise ValueError(t)
def node(o):
    if W == 8: end, np_, pl = struct.unpack('<QQQ', b[o:o + 24]); o += 24
    else: end, np_, pl = struct.unpack('<III', b[o:o + 12]); o += 12
    if end == 0: return None, o
    nl = b[o]; name = b[o + 1:o + 1 + nl].decode(); o += 1 + nl
    props = []
    for _ in range(np_): p, o = prop(o); props.append(p)
    kids = []
    while o < end:
        k, o2 = node(o)
        if k is None: o = o2; break
        kids.append(k); o = o2
    return (name, props, kids), end
o = 27; top = []
while True:
    n, o2 = node(o)
    if n is None: break
    top.append(n); o = o2
def find(nodes, name): return [n for n in nodes if n[0] == name]
gs = find(top, 'GlobalSettings')[0]
for p in find(find(gs[2], 'Properties70')[0][2], 'P'):
    if p[1][0] in (b'UpAxis', b'UpAxisSign', b'FrontAxis', b'FrontAxisSign', b'CoordAxis', b'CoordAxisSign', b'UnitScaleFactor', b'OriginalUnitScaleFactor'):
        print('GlobalSettings', p[1][0].decode(), p[1][-1])
objs = find(top, 'Objects')[0][2]
for m in find(objs, 'Model'):
    tr = {p[1][0].decode(): tuple(round(float(x), 4) for x in p[1][4:]) for p in find(find(m[2], 'Properties70')[0][2], 'P') if p[1][0].startswith(b'Lcl')}
    print('Model', m[1][1].split(b'\x00')[0].decode(), m[1][2].decode(), tr)
for g in find(objs, 'Geometry'):
    v = find(g[2], 'Vertices')[0][1][0].reshape(-1, 3)
    print('Geometry', g[1][1].split(b'\x00')[0].decode(), 'verts', len(v), 'min', v.min(0).round(4), 'max', v.max(0).round(4))
print('Video/embedded textures:', [(n[1][1].split(b'\x00')[0].decode(), len(find(n[2], 'Content')[0][1][0]) if find(n[2], 'Content') else 0) for n in find(objs, 'Video')])
