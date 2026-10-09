"""Minimal reader for Roblox binary place/model files (.rbxl/.rbxm).

Usage: python -I rbxl_read.py <file> <out.json>
Writes a JSON list of instances: {ref, class, parent, props}.
Unknown property types are recorded as {"_unparsed": type_id}.
"""
import json
import struct
import sys

import zstandard


def lz4_block(src, out_len):
    dst = bytearray()
    i = 0
    n = len(src)
    while i < n:
        token = src[i]; i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                b = src[i]; i += 1
                lit += b
                if b != 255:
                    break
        dst += src[i:i + lit]; i += lit
        if i >= n:
            break
        off = src[i] | (src[i + 1] << 8); i += 2
        ml = token & 15
        if ml == 15:
            while True:
                b = src[i]; i += 1
                ml += b
                if b != 255:
                    break
        ml += 4
        start = len(dst) - off
        for k in range(ml):
            dst.append(dst[start + k])
    assert len(dst) == out_len, (len(dst), out_len)
    return bytes(dst)


def decompress(blob, clen, ulen):
    if clen == 0:
        return blob
    if blob[:4] == b'\x28\xb5\x2f\xfd':
        return zstandard.ZstdDecompressor().decompress(blob, max_output_size=ulen)
    return lz4_block(blob, ulen)


class R:
    def __init__(self, b):
        self.b = b
        self.i = 0

    def u8(self):
        v = self.b[self.i]; self.i += 1; return v

    def u16(self):
        v = struct.unpack_from('<H', self.b, self.i)[0]; self.i += 2; return v

    def u32(self):
        v = struct.unpack_from('<I', self.b, self.i)[0]; self.i += 4; return v

    def i32(self):
        v = struct.unpack_from('<i', self.b, self.i)[0]; self.i += 4; return v

    def f32(self):
        v = struct.unpack_from('<f', self.b, self.i)[0]; self.i += 4; return v

    def f64(self):
        v = struct.unpack_from('<d', self.b, self.i)[0]; self.i += 8; return v

    def bytes(self, n):
        v = self.b[self.i:self.i + n]; self.i += n; return v

    def string(self):
        n = self.u32()
        return self.bytes(n)

    def interleaved(self, count, width):
        raw = self.bytes(count * width)
        out = []
        for k in range(count):
            v = 0
            for j in range(width):
                v = (v << 8) | raw[j * count + k]
            out.append(v)
        return out

    def i32s(self, count):
        return [(x >> 1) ^ -(x & 1) for x in self.interleaved(count, 4)]

    def i64s(self, count):
        return [(x >> 1) ^ -(x & 1) for x in self.interleaved(count, 8)]

    def u32s(self, count):
        return self.interleaved(count, 4)

    def floats(self, count):
        out = []
        for x in self.interleaved(count, 4):
            bits = ((x >> 1) | ((x & 1) << 31)) & 0xFFFFFFFF
            out.append(struct.unpack('<f', struct.pack('<I', bits))[0])
        return out

    def refs(self, count):
        vals = self.i32s(count)
        acc = 0
        out = []
        for v in vals:
            acc += v
            out.append(acc)
        return out


NORMALS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def basic_rotation(rid):
    r, u = divmod(rid - 1, 6)
    R_ = NORMALS[r]; U = NORMALS[u]
    Z = (R_[1] * U[2] - R_[2] * U[1], R_[2] * U[0] - R_[0] * U[2], R_[0] * U[1] - R_[1] * U[0])
    # matrix columns are R, U, Z -> rows
    return [R_[0], U[0], Z[0], R_[1], U[1], Z[1], R_[2], U[2], Z[2]]


def to_text(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return {'_bytes_hex': b.hex()}


def read_values(r, t, count, sstr):
    if t == 0x01 or t == 0x1D:
        return [to_text(r.string()) for _ in range(count)]
    if t == 0x02:
        return [bool(r.u8()) for _ in range(count)]
    if t == 0x03:
        return r.i32s(count)
    if t == 0x04:
        return r.floats(count)
    if t == 0x05:
        return [r.f64() for _ in range(count)]
    if t == 0x06:
        s = r.floats(count); o = r.i32s(count)
        return [[s[k], o[k]] for k in range(count)]
    if t == 0x07:
        sx = r.floats(count); sy = r.floats(count); ox = r.i32s(count); oy = r.i32s(count)
        return [[sx[k], ox[k], sy[k], oy[k]] for k in range(count)]
    if t == 0x08:
        return [[r.f32() for _ in range(6)] for _ in range(count)]
    if t in (0x09, 0x0A):
        return [r.u8() for _ in range(count)]
    if t == 0x0B:
        return r.u32s(count)
    if t == 0x0C:
        a = r.floats(count); b = r.floats(count); c = r.floats(count)
        return [[a[k], b[k], c[k]] for k in range(count)]
    if t == 0x0D:
        a = r.floats(count); b = r.floats(count)
        return [[a[k], b[k]] for k in range(count)]
    if t == 0x0E:
        a = r.floats(count); b = r.floats(count); c = r.floats(count)
        return [[a[k], b[k], c[k]] for k in range(count)]
    if t == 0x10 or t == 0x1E:
        if t == 0x1E:
            assert r.u8() == 0x10
        rots = []
        for _ in range(count):
            rid = r.u8()
            if rid == 0:
                rots.append([r.f32() for _ in range(9)])
            else:
                rots.append(basic_rotation(rid))
        x = r.floats(count); y = r.floats(count); z = r.floats(count)
        out = [[x[k], y[k], z[k]] + rots[k] for k in range(count)]
        if t == 0x1E:
            assert r.u8() == 0x02
            has = [bool(r.u8()) for _ in range(count)]
            out = [out[k] if has[k] else None for k in range(count)]
        return out
    if t == 0x12:
        return r.u32s(count)
    if t == 0x13:
        return r.refs(count)
    if t == 0x14:
        return [[struct.unpack('<h', r.bytes(2))[0] for _ in range(3)] for _ in range(count)]
    if t == 0x15:
        out = []
        for _ in range(count):
            n = r.u32()
            out.append([[r.f32(), r.f32(), r.f32()] for _ in range(n)])
        return out
    if t == 0x16:
        out = []
        for _ in range(count):
            n = r.u32()
            out.append([[r.f32(), r.f32(), r.f32(), r.f32(), r.f32()] for _ in range(n)])
        return out
    if t == 0x17:
        return [[r.f32(), r.f32()] for _ in range(count)]
    if t == 0x18:
        a = r.floats(count); b = r.floats(count); c = r.floats(count); d = r.floats(count)
        return [[a[k], b[k], c[k], d[k]] for k in range(count)]
    if t == 0x19:
        out = []
        for _ in range(count):
            flag = r.u8()
            if flag & 1:
                vals = [r.f32() for _ in range(5)]
                if flag & 2:
                    vals.append(r.f32())
                out.append(vals)
            else:
                out.append(None)
        return out
    if t == 0x1A:
        a = r.bytes(count); b = r.bytes(count); c = r.bytes(count)
        return [[a[k], b[k], c[k]] for k in range(count)]
    if t == 0x1B:
        return r.i64s(count)
    if t == 0x1C:
        idx = r.u32s(count)
        return [{'_sstr': i} for i in idx]
    if t == 0x1F:
        raw = r.interleaved(count, 16)
        return ['%032x' % v for v in raw]
    if t == 0x20:
        out = []
        for _ in range(count):
            fam = to_text(r.string()); w = r.u16(); st = r.u8(); cache = to_text(r.string())
            out.append([fam, w, st, cache])
        return out
    if t == 0x21:
        return r.interleaved(count, 8)
    raise ValueError('unknown type 0x%02x' % t)


def main(path, out_path):
    d = open(path, 'rb').read()
    assert d[:8] == b'<roblox!'
    i = 32
    classes = {}
    inst_class = {}
    props = {}
    parents = {}
    sstr = []
    errors = []
    schema = {}
    while i < len(d):
        name = d[i:i + 4]
        clen, ulen, _ = struct.unpack_from('<III', d, i + 4)
        i += 16
        n = clen if clen else ulen
        data = decompress(d[i:i + n], clen, ulen)
        i += n
        r = R(data)
        if name == b'META':
            pass
        elif name == b'SSTR':
            r.u32()
            cnt = r.u32()
            for _ in range(cnt):
                r.bytes(16)
                sstr.append(r.string())
        elif name == b'INST':
            cid = r.u32()
            cname = r.string().decode()
            fmt = r.u8()
            cnt = r.u32()
            refs = r.refs(cnt)
            classes[cid] = (cname, refs)
            for ref in refs:
                inst_class[ref] = cname
                props[ref] = {}
        elif name == b'PROP':
            cid = r.u32()
            pname = r.string().decode()
            t = r.u8()
            cname, refs = classes[cid]
            schema.setdefault(cname, {})[pname] = t
            try:
                vals = read_values(r, t, len(refs), sstr)
            except Exception as e:  # keep going; chunks are independent
                errors.append('%s.%s type 0x%02x: %s' % (cname, pname, t, e))
                vals = [{'_unparsed': t}] * len(refs)
            for ref, v in zip(refs, vals):
                props[ref][pname] = v
        elif name == b'PRNT':
            r.u8()
            cnt = r.u32()
            ch = r.refs(cnt)
            pa = r.refs(cnt)
            for c, p in zip(ch, pa):
                parents[c] = p
        elif name == b'END\x00':
            break
    out = []
    for ref, cname in inst_class.items():
        pr = props[ref]
        for k, v in list(pr.items()):
            if isinstance(v, dict) and '_sstr' in v:
                blob = sstr[v['_sstr']]
                pr[k] = {'_sstr_len': len(blob), '_sstr_head': blob[:64].hex()}
        out.append({'ref': ref, 'class': cname, 'parent': parents.get(ref, -1), 'props': pr})
    json.dump({'instances': out, 'errors': errors, 'sstr_count': len(sstr), 'schema': schema}, open(out_path, 'w'))
    print('instances', len(out), 'errors', len(errors))
    for e in errors[:20]:
        print('  ', e)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
