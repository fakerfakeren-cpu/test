"""Convert a source portrait into HOI4 leader portrait DDS files.

Usage: python3 make_portrait.py <source image> <output dir>

Writes:
  BUL_victor_kolev.dds        156x210  (country leader / large portrait)
  BUL_victor_kolev_small.dds   65x67   (advisor-style small portrait)

The DDS files are uncompressed 32-bit A8R8G8B8, which HOI4 loads fine.
"""
import struct
import sys
from pathlib import Path

from PIL import Image


def write_dds(img: Image.Image, path: Path) -> None:
    img = img.convert("RGBA")
    w, h = img.size
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()  # BGRA byte order
    header = struct.pack(
        "<4s7I44x" "2I4s5I" "4I4x",
        b"DDS ", 124, 0x100F, h, w, w * 4, 0, 0,
        32, 0x41, b"\0\0\0\0", 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
        0x1000, 0, 0, 0,
    )
    assert len(header) == 128, len(header)
    path.write_bytes(header + data)


def cover(img: Image.Image, size, focus_box=None) -> Image.Image:
    """Crop to the target aspect ratio (optionally inside focus_box) and resize."""
    if focus_box:
        img = img.crop(focus_box)
    tw, th = size
    w, h = img.size
    target = tw / th
    if w / h > target:
        nw = round(h * target)
        x = (w - nw) // 2
        img = img.crop((x, 0, x + nw, h))
    else:
        nh = round(w / target)
        img = img.crop((0, 0, w, nh))  # keep the top (head) when trimming height
    return img.resize(size, Image.LANCZOS)


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    write_dds(cover(img, (156, 210)), out / "BUL_victor_kolev.dds")
    # Small portrait: tight crop around the face.
    face = (int(w * 0.17), int(h * 0.12), int(w * 0.83), int(h * 0.62))
    write_dds(cover(img, (65, 67), face), out / "BUL_victor_kolev_small.dds")


if __name__ == "__main__":
    main()
