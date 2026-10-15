"""Minimal Anvil (.mca) reader: block states of a box of the world."""
import io
import os
import struct
import zlib
import gzip


def read_nbt(buf):
    f = io.BytesIO(buf)

    def rd(n):
        return f.read(n)

    def payload(t):
        if t == 1: return struct.unpack(">b", rd(1))[0]
        if t == 2: return struct.unpack(">h", rd(2))[0]
        if t == 3: return struct.unpack(">i", rd(4))[0]
        if t == 4: return struct.unpack(">q", rd(8))[0]
        if t == 5: return struct.unpack(">f", rd(4))[0]
        if t == 6: return struct.unpack(">d", rd(8))[0]
        if t == 7:
            n = struct.unpack(">i", rd(4))[0]; return rd(n)
        if t == 8:
            n = struct.unpack(">H", rd(2))[0]; return rd(n).decode("utf-8", "replace")
        if t == 9:
            et = rd(1)[0]; n = struct.unpack(">i", rd(4))[0]
            return [payload(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = rd(1)[0]
                if tt == 0:
                    return d
                n = struct.unpack(">H", rd(2))[0]
                name = rd(n).decode("utf-8", "replace")
                d[name] = payload(tt)
        if t == 11:
            n = struct.unpack(">i", rd(4))[0]; return list(struct.unpack(f">{n}i", rd(4 * n)))
        if t == 12:
            n = struct.unpack(">i", rd(4))[0]; return list(struct.unpack(f">{n}q", rd(8 * n)))
        raise ValueError(f"tag {t}")

    t = rd(1)[0]
    n = struct.unpack(">H", rd(2))[0]
    rd(n)
    return payload(t)


def read_chunk(region_dir, cx, cz):
    rx, rz = cx >> 5, cz >> 5
    path = os.path.join(region_dir, f"r.{rx}.{rz}.mca")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    i = 4 * ((cx & 31) + (cz & 31) * 32)
    off = int.from_bytes(data[i:i + 3], "big")
    if off == 0:
        return None
    start = off * 4096
    length = struct.unpack(">i", data[start:start + 4])[0]
    comp = data[start + 4]
    raw = data[start + 5:start + 4 + length]
    if comp == 2:
        raw = zlib.decompress(raw)
    elif comp == 1:
        raw = gzip.decompress(raw)
    elif comp == 3:
        pass
    else:
        raise ValueError(f"compression {comp} not supported")
    return read_nbt(raw)


_seen_formats = set()


def state_str(p):
    """Palette entry -> 'minecraft:id[k=v,...]'. 26.3 changed the encoding, so accept the classic
    {Name, Properties} compound, lower-case keys, or a plain state string."""
    if isinstance(p, dict) and set(p) == {""}:
        # 26.x heterogeneous NBT lists wrap non-compound elements as {"": value}
        return state_str(p[""])
    if isinstance(p, (bytes, str)):
        s = p.decode() if isinstance(p, bytes) else p
        if ":" not in s.split("[")[0]:
            s = "minecraft:" + s
        name, _, rest = s.partition("[")
        if rest:
            props = dict(kv.split("=", 1) for kv in rest.rstrip("]").split(",") if kv)
            s = name + "[" + ",".join(f"{k}={v}" for k, v in sorted(props.items())) + "]"
        kind = "string"
    else:
        name = p.get("Name") or p.get("name") or p.get("id") or p.get("block")
        props = p.get("Properties") or p.get("properties") or p.get("state") or {}
        if name is None:
            raise ValueError(f"unknown palette entry format: {p!r}")
        if ":" not in name:
            name = "minecraft:" + name
        s = name
        if isinstance(props, dict) and props:
            s += "[" + ",".join(f"{k}={v}" for k, v in sorted(props.items())) + "]"
        kind = "compound:" + ",".join(sorted(p))
    if kind not in _seen_formats:
        _seen_formats.add(kind)
        print(f"ANVIL: palette entry format {kind} e.g. {p!r:.120}")
    return s


def read_box(region_dir, x0, y0, z0, x1, y1, z1):
    out = {}
    cache = {}
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            ch = read_chunk(region_dir, cx, cz)
            if ch is None:
                continue
            for sec in ch.get("sections", []):
                sy = sec["Y"]
                bs = sec.get("block_states")
                if not bs:
                    continue
                if not _seen_formats:
                    print("ANVIL: section keys", sorted(sec), "block_states keys", sorted(bs),
                          "palette type", type(bs.get("palette")).__name__)
                pal = [state_str(p) for p in bs["palette"]]
                if sy * 16 > y1 or sy * 16 + 15 < y0:
                    continue
                longs = bs.get("data")
                bits = max(4, (len(pal) - 1).bit_length())
                per = 64 // bits
                mask = (1 << bits) - 1
                for ly in range(16):
                    y = sy * 16 + ly
                    if y < y0 or y > y1:
                        continue
                    for lz in range(16):
                        z = cz * 16 + lz
                        if z < z0 or z > z1:
                            continue
                        for lx in range(16):
                            x = cx * 16 + lx
                            if x < x0 or x > x1:
                                continue
                            if longs is None:
                                v = 0
                            else:
                                idx = ly * 256 + lz * 16 + lx
                                word = longs[idx // per] & 0xFFFFFFFFFFFFFFFF
                                v = (word >> ((idx % per) * bits)) & mask
                            out[(x, y, z)] = pal[v]
    return out
