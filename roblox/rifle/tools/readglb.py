"""Independent .glb reader: returns world-space triangles + colours sampled from the texture at each UV."""
import json, struct, io, sys, numpy as np
from PIL import Image
def load(path):
    b = open(path, 'rb').read()
    magic, ver, length = struct.unpack('<III', b[:12]); assert magic == 0x46546C67 and ver == 2 and length == len(b)
    jl, jt = struct.unpack('<II', b[12:20]); js = json.loads(b[20:20 + jl]); off = 20 + jl
    bl, bt = struct.unpack('<II', b[off:off + 8]); binb = b[off + 8: off + 8 + bl]
    def acc(i):
        a = js['accessors'][i]; v = js['bufferViews'][a['bufferView']]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a['componentType']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
        arr = np.frombuffer(binb[v['byteOffset']: v['byteOffset'] + v['byteLength']], dt)
        return arr.reshape(-1, n) if n > 1 else arr
    iv = js['bufferViews'][js['images'][0]['bufferView']]
    tex = np.array(Image.open(io.BytesIO(binb[iv['byteOffset']: iv['byteOffset'] + iv['byteLength']])).convert('RGB'))
    th, tw = tex.shape[:2]
    out = {}
    for n in js['nodes']:
        if 'mesh' not in n: continue
        pr = js['meshes'][n['mesh']]['primitives'][0]
        P = acc(pr['attributes']['POSITION']) + np.array(n.get('translation', [0, 0, 0]))
        UV = acc(pr['attributes']['TEXCOORD_0']); I = acc(pr['indices']).reshape(-1, 3)
        cols = np.array([tex[min(th - 1, int(UV[t[0]][1] * th)), min(tw - 1, int(UV[t[0]][0] * tw))] for t in I])
        out[n['name']] = (P[I], cols)
    return js, out
if __name__ == '__main__':
    js, parts = load(sys.argv[1])
    print('nodes', [n['name'] for n in js['nodes']], 'sampler', js['samplers'])
    for k, (T, C) in parts.items(): print(k, 'tris', len(T), 'bbox', T.reshape(-1, 3).min(0).round(3), T.reshape(-1, 3).max(0).round(3))
