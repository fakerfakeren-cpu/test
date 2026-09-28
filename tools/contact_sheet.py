"""Render a labelled, upscaled contact sheet of PNGs for visual review."""
import os
import sys

from PIL import Image, ImageDraw

def main(out, paths, scale=8, cols=6):
    imgs = [(os.path.basename(p)[:-4], Image.open(p).convert('RGBA')) for p in paths]
    cell_w = max(i.width for _, i in imgs) * scale + 16
    cell_h = max(i.height for _, i in imgs) * scale + 28
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), (60, 60, 70, 255))
    d = ImageDraw.Draw(sheet)
    for idx, (name, im) in enumerate(imgs):
        x, y = (idx % cols) * cell_w + 8, (idx // cols) * cell_h + 4
        # checkerboard behind transparency
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        bg = Image.new('RGBA', big.size, (90, 90, 100, 255))
        bd = ImageDraw.Draw(bg)
        for yy in range(0, big.height, scale * 2):
            for xx in range(0, big.width, scale * 2):
                bd.rectangle([xx, yy, xx + scale - 1, yy + scale - 1], fill=(110, 110, 120, 255))
                bd.rectangle([xx + scale, yy + scale, xx + 2 * scale - 1, yy + 2 * scale - 1], fill=(110, 110, 120, 255))
        bg.alpha_composite(big)
        sheet.paste(bg, (x, y))
        d.text((x, y + big.height + 2), name, fill=(255, 255, 255, 255))
    sheet.save(out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
