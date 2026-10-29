"""Builds tiles.png (the 48x16 sheet to upload) and tiles_preview.png (16x zoom, for viewing).

Each tile is drawn by hand as an 8x8 character map; edit the maps or colours and rerun:
    python3 make_tiles.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

TILE = 8
OUT = Path(__file__).parent

COLORS = {
    ".": (0, 0, 0, 0),
    # dirt
    "d": (74, 46, 27, 255),
    "m": (110, 72, 42, 255),
    "l": (138, 92, 54, 255),
    "p": (160, 120, 80, 255),
    # grass
    "a": (126, 206, 86, 255),
    "b": (82, 168, 62, 255),
    "c": (48, 112, 44, 255),
    # stone
    "k": (60, 60, 70, 255),
    "s": (104, 104, 116, 255),
    "h": (140, 140, 154, 255),
    # copper ore
    "x": (122, 62, 26, 255),
    "o": (196, 112, 46, 255),
    "O": (244, 168, 88, 255),
    # torch
    "w": (128, 84, 46, 255),
    "v": (82, 52, 28, 255),
    "y": (255, 236, 140, 255),
    "r": (255, 176, 58, 255),
    "e": (232, 98, 30, 255),
    # dirt wall
    "B": (60, 38, 24, 255),
    "C": (47, 30, 19, 255),
    "E": (74, 49, 31, 255),
    # stone wall
    "S": (52, 52, 62, 255),
    "T": (40, 40, 48, 255),
    "U": (64, 64, 76, 255),
}

EMPTY = ["........"] * 8

DIRT = [
    "mmmlmmdm",
    "mdmmmmmm",
    "mmmmpmml",
    "lmdmmmmm",
    "mmmmmdmm",
    "mmpmmmml",
    "mdmmlmmm",
    "mmmmmmdm",
]

GRASS = [
    "abaabbab",
    "bbbcbbbb",
    "cbcmcbcc",
    "mcmmmcmm",
    "mmmpmmdm",
    "lmmmmmmm",
    "mmdmmlmm",
    "mmmmmmmd",
]

STONE = [
    "hsssshss",
    "ssksssss",
    "sskkssss",
    "sssssshs",
    "shssssss",
    "sssskkss",
    "ssssskss",
    "hssssssh",
]

ORE = [
    "sssshsss",
    "soOsssss",
    "sxossOos",
    "ssssoxss",
    "shssssss",
    "sssoOsss",
    "ssoxxsss",
    "ssssssks",
]

TORCH = [
    "....y...",
    "...yy...",
    "...ry...",
    "...re...",
    "...wv...",
    "...wv...",
    "...wv...",
    "...wv...",
]

DIRT_WALL = [
    "BBEBBBCB",
    "BCBBBBBB",
    "BBBBEBBB",
    "EBBCBBBE",
    "BBBBBBBB",
    "BCBBBEBB",
    "BBEBBBBB",
    "BBBBCBBC",
]

STONE_WALL = [
    "USSSSUSS",
    "SSTSSSSS",
    "SSTTSSSS",
    "SSSSSSUS",
    "SUSSSSSS",
    "SSSSTTSS",
    "SSSSSTSS",
    "USSSSSSU",
]

# Order must match the script: row 0 = AIR, DIRT, GRASS, STONE, ORE, TORCH;
# row 1 = NO_WALL, DIRT_WALL, STONE_WALL.
ROWS = [
    [("air", EMPTY), ("dirt", DIRT), ("grass", GRASS), ("stone", STONE), ("ore", ORE), ("torch", TORCH)],
    [("no wall", EMPTY), ("dirt wall", DIRT_WALL), ("stone wall", STONE_WALL)],
]


def main() -> None:
    sheet = Image.new("RGBA", (6 * TILE, 2 * TILE), (0, 0, 0, 0))
    for row, tiles in enumerate(ROWS):
        for col, (name, art) in enumerate(tiles):
            assert len(art) == TILE and all(len(line) == TILE for line in art), name
            for y, line in enumerate(art):
                for x, ch in enumerate(line):
                    sheet.putpixel((col * TILE + x, row * TILE + y), COLORS[ch])
    sheet.save(OUT / "tiles.png")

    zoom = 16
    big = sheet.resize((sheet.width * zoom, sheet.height * zoom), Image.NEAREST)
    preview = Image.new("RGBA", (big.width, big.height + 2 * 14), (235, 235, 240, 255))
    # checkerboard so transparent pixels are visible
    draw = ImageDraw.Draw(preview)
    for y in range(0, big.height, zoom):
        for x in range(0, big.width, zoom):
            if (x // zoom + y // zoom) % 2:
                draw.rectangle([x, y, x + zoom - 1, y + zoom - 1], fill=(205, 205, 212, 255))
    preview.alpha_composite(big)
    for row, tiles in enumerate(ROWS):
        for col, (name, _) in enumerate(tiles):
            draw.rectangle([col * TILE * zoom, row * TILE * zoom, (col + 1) * TILE * zoom - 1, (row + 1) * TILE * zoom - 1], outline=(30, 30, 30, 255))
            draw.text((col * TILE * zoom + 3, big.height + 2 + row * 14), name, fill=(20, 20, 20, 255))
    preview.save(OUT / "tiles_preview.png")


if __name__ == "__main__":
    main()
