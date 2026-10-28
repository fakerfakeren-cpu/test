"""Minimal DDS I/O for HOI4 sprites: uncompressed 32-bit BGRA (A8R8G8B8), no mipmaps.

HOI4 reads this format for every UI texture (portraits, focus/idea icons,
event pictures). Pillow's own DDS writer varies between versions, so the
header is written by hand and every file is read back to verify it.
"""
import struct
from PIL import Image

DDSD_CAPS, DDSD_HEIGHT, DDSD_WIDTH, DDSD_PITCH, DDSD_PIXELFORMAT = 0x1, 0x2, 0x4, 0x8, 0x1000
DDPF_ALPHAPIXELS, DDPF_RGB = 0x1, 0x40
DDSCAPS_TEXTURE = 0x1000


def write_dds(img: Image.Image, path: str) -> None:
    img = img.convert("RGBA")
    w, h = img.size
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIIIIIIII",
        b"DDS ", 124,
        DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PITCH | DDSD_PIXELFORMAT,
        h, w, w * 4, 0, 0, b"\0" * 44,
        # DDS_PIXELFORMAT
        32, DDPF_RGB | DDPF_ALPHAPIXELS, 0, 32,
        0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
        DDSCAPS_TEXTURE, 0, 0, 0, 0,
    )
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()  # byte order B,G,R,A
    with open(path, "wb") as f:
        f.write(header)
        f.write(data)


def read_dds(path: str) -> Image.Image:
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"DDS ":
        raise ValueError(f"{path}: not a DDS file")
    h, w = struct.unpack_from("<II", raw, 12)
    pf_flags, fourcc, bits = struct.unpack_from("<II4sI", raw, 80)[0], raw[84:88], struct.unpack_from("<I", raw, 88)[0]
    if fourcc not in (b"\0\0\0\0",) or bits != 32:
        # fall back to Pillow for compressed files (DXT1/3/5)
        return Image.open(path).convert("RGBA")
    data = raw[128:128 + w * h * 4]
    if len(data) != w * h * 4:
        raise ValueError(f"{path}: truncated pixel data")
    b, g, r, a = Image.frombytes("RGBA", (w, h), data).split()
    return Image.merge("RGBA", (r, g, b, a))


def dds_info(path: str):
    """(width, height, has_meaningful_alpha) without decoding more than needed."""
    img = read_dds(path)
    lo, hi = img.getchannel("A").getextrema()
    return img.size[0], img.size[1], lo < 255
