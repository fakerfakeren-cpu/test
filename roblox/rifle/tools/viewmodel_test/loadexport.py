"""Read the Roblox-exported ScarView.gltf: per-part local triangles (studs, part space) + per-triangle colours."""
import json, base64, io, numpy as np
from PIL import Image
def load(path):
    d = json.load(open(path))
    def buf(i): return base64.b64decode(d['buffers'][i]['uri'].split(',', 1)[1])
    def acc(i):
        a = d['accessors'][i]; bv = d['bufferViews'][a['bufferView']]
        raw = buf(bv['buffer'])[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
        dt = {5125: np.uint32, 5126: np.float32, 5121: np.uint8, 5123: np.uint16}[a['componentType']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        arr = np.frombuffer(raw, dt)
        return arr.reshape(-1, n) if n > 1 else arr
    tex = np.array(Image.open(io.BytesIO(base64.b64decode(d['images'][0]['uri'].split(',', 1)[1]))).convert('RGB'))
    th, tw = tex.shape[:2]
    parts = {}
    for n in d['nodes']:
        if 'mesh' not in n or n['name'] not in ('Body', 'Magazine', 'Slide'): continue
        pr = d['meshes'][n['mesh']]['primitives'][0]
        P = acc(pr['attributes']['POSITION']).astype(float) * np.array(n.get('scale', [1, 1, 1]))
        UV = acc(pr['attributes']['TEXCOORD_0']); I = acc(pr['indices']).reshape(-1, 3)
        uvc = UV[I].mean(1)
        cols = tex[np.clip((uvc[:, 1] * th).astype(int), 0, th - 1), np.clip((uvc[:, 0] * tw).astype(int), 0, tw - 1)]
        parts[n['name']] = (P[I], cols.astype(np.uint8))
    return parts
if __name__ == '__main__':
    import sys
    p = load(sys.argv[1])
    for k, (T, C) in p.items(): print(k, T.shape, T.reshape(-1, 3).min(0).round(3), T.reshape(-1, 3).max(0).round(3))
