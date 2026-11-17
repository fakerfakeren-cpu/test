"""Focus icons with people in them: the leader cut out of his portrait, in black and white, standing in the
middle of a focus frame, with a sword, handshake or the like in front of him.

Portraits have a plain painted background, so the cut-out models that background as a smooth colour surface
(fitted to the picture's top and side edges), marks everything that differs from it, and keeps the figure: the
part not connected to the edges through background-coloured pixels.
"""
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy import ndimage as ndi


def cutout(portrait):
    """RGBA image of the person with a transparent background, cropped to the figure.

    The painted background is smooth and close in colour to the picture's top corners. It is flood-filled from
    the top corners and upper sides through pixels that are both smooth (no strong edge) and background-coloured;
    the outline of hair, face and shoulders stops the fill. Everything not reached is the person."""
    rgb = np.asarray(portrait.convert("RGB")).astype(np.float64)
    h, w, _ = rgb.shape
    sm = ndi.gaussian_filter(rgb, (max(1.0, w / 160), max(1.0, w / 160), 0))
    lum = sm.mean(-1)
    grad = np.hypot(ndi.sobel(lum, 0), ndi.sobel(lum, 1))
    k = max(3, w // 14)
    corners = np.concatenate([sm[:k, :k].reshape(-1, 3), sm[:k, -k:].reshape(-1, 3)])
    ref = corners.mean(0)
    gcorner = np.concatenate([grad[:k, :k].ravel(), grad[:k, -k:].ravel()])
    smooth = grad < max(np.percentile(gcorner, 99) * 2.5, 6.0)
    # the background darkens towards the bottom: compare each pixel with the background colour of its own row,
    # taken from the picture's edge columns in the upper part and extrapolated below it
    edge_cols = np.concatenate([sm[:, :k], sm[:, -k:]], 1)
    row_ref = np.median(edge_cols, 1)
    upper = int(h * 0.45)
    yy = np.arange(h)
    for c in range(3):
        coef = np.polyfit(yy[:upper], row_ref[:upper, c], 1)
        row_ref[upper:, c] = np.polyval(coef, yy[upper:])
    colour = np.sqrt(((sm - row_ref[:, None, :]) ** 2).sum(-1)) < 30
    bg_like = smooth & colour
    seeds = np.zeros((h, w), bool)
    seeds[:k, :k] = seeds[:k, -k:] = True
    seeds[: int(h * 0.9), :2] = seeds[: int(h * 0.9), -2:] = True
    lab, _ = ndi.label(bg_like)
    background = np.isin(lab, np.unique(lab[seeds & bg_like])[np.unique(lab[seeds & bg_like]) > 0])
    background = ndi.binary_dilation(background, iterations=1) & bg_like | background
    for _ in range(2):   # learn the real background colour of every row from what is already background, regrow
        ref_rows = row_ref.copy()
        for y in range(h):
            row = background[y]
            if row.sum() >= 4:
                ref_rows[y] = np.median(sm[y][row], 0)
        ref_rows = ndi.gaussian_filter1d(ref_rows, 3, axis=0)
        colour = np.sqrt(((sm - ref_rows[:, None, :]) ** 2).sum(-1)) < 34
        bg_like = (grad < max(np.percentile(gcorner, 99) * 3.0, 7.0)) & colour
        lab, _ = ndi.label(bg_like | background)
        keep = np.unique(lab[background])
        background = np.isin(lab, keep[keep > 0])
    bgpix = sm[background]
    mu, sd = bgpix.mean(0), bgpix.std(0) + 4
    near = (np.abs(sm - mu) < 3.0 * sd).all(-1) & (grad < max(np.percentile(gcorner, 99) * 3.0, 7.0))
    side = np.zeros((h, w), bool)
    side[int(h * 0.54):, : int(w * 0.28)] = True
    side[int(h * 0.54):, w - int(w * 0.28):] = True
    lab, _ = ndi.label(near & side)
    edge_ids = np.unique(np.concatenate([lab[:, 0], lab[:, -1]]))
    background |= np.isin(lab, edge_ids[edge_ids > 0])
    figure = ndi.binary_opening(~background, iterations=2)
    lab, n = ndi.label(figure)
    if n > 1:
        figure = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    r_close = max(2, w // 60)
    figure = ndi.binary_closing(np.pad(figure, r_close + 1), structure=np.ones((3, 3)), iterations=r_close)[
        r_close + 1:-r_close - 1, r_close + 1:-r_close - 1] | figure
    figure = ndi.binary_fill_holes(figure)
    figure = ndi.binary_erosion(figure, iterations=max(1, w // 200))
    alpha = Image.fromarray((figure * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(0.6, w / 500)))
    out = portrait.convert("RGBA")
    out.putalpha(alpha)
    ys, xs = np.nonzero(figure)
    return out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def bust(cut, height_to_width=1.05):
    """Head and shoulders: the top of the figure, as tall as the figure is wide times height_to_width."""
    w, h = cut.size
    return cut.crop((0, 0, w, min(h, int(w * height_to_width))))


def black_and_white(im, contrast=1.15):
    a = im.getchannel("A")
    g = ImageOps.autocontrast(ImageOps.grayscale(im.convert("RGB")), cutoff=1)
    g = g.point(lambda v: max(0, min(255, int((v - 128) * contrast + 128))))
    out = Image.merge("RGBA", (g, g, g, a))
    return out


def frame_parts(frame):
    """Split a focus frame into its inner circle (the part a person stands in) and the rest (ring, swords...),
    which is drawn again on top of the person. Works for empty rings and for frames with a dark filled middle."""
    rgba = np.asarray(frame.convert("RGBA")).astype(np.int32)
    h, w = rgba.shape[:2]
    alpha, lum = rgba[..., 3], rgba[..., :3].mean(-1)
    cy, cx = h // 2 - 2, w // 2
    hole = alpha < 20
    lab, _ = ndi.label(hole)
    centre = lab[cy, cx]
    if centre and not (lab == centre)[[0, -1], :].any() and not (lab == centre)[:, [0, -1]].any():
        inner = lab == centre                      # empty ring: the transparent middle
        filled = False
    else:
        dark = (alpha > 150) & (lum < lum[cy, cx] + 40) & (lum < 110)
        lab, _ = ndi.label(dark)
        inner = lab == lab[cy, cx]                 # dark filled middle
        filled = True
    inner = ndi.binary_fill_holes(inner)
    ys, xs = np.nonzero(inner)
    centre = (ys.mean(), xs.mean())
    radius = np.sqrt(inner.sum() / np.pi)
    overlay = np.asarray(frame.convert("RGBA")).copy()
    overlay[inner] = 0
    return inner, Image.fromarray(overlay), centre, radius, filled


def person_icon(frame, portrait, front=None, fill=(28, 28, 34), front_width=0.62, front_y=0.78, bw=True,
                head_room=0.10, bust_width=1.25):
    """frame: focus frame image; portrait: the leader's portrait; front: a piece drawn in front of him."""
    frame = frame.convert("RGBA")
    W, H = frame.size
    inner, overlay, (cy, cx), r, filled = frame_parts(frame)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(frame)
    if not filled:                                 # an empty ring gets a dark middle to stand in
        disc = Image.new("RGBA", (W, H), fill + (255,))
        canvas.alpha_composite(Image.composite(disc, Image.new("RGBA", (W, H)), Image.fromarray((inner * 255).astype(np.uint8))))
    person = bust(cutout(portrait))
    if bw:
        person = black_and_white(person)
    pw = int(2 * r * bust_width)
    ph = int(person.height * pw / person.width)
    person = person.resize((pw, ph), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(person, (int(cx - pw / 2), int(cy - r + head_room * 2 * r)))
    clip = Image.fromarray((ndi.binary_dilation(inner, iterations=1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
    layer.putalpha(Image.fromarray(np.minimum(np.asarray(layer.getchannel("A")), np.asarray(clip))))
    canvas.alpha_composite(layer)
    canvas.alpha_composite(overlay)                # the ring (and any swords of the frame) in front of him
    if front is not None:
        front = front.convert("RGBA")
        fw = int(W * front_width)
        fh = int(front.height * fw / front.width)
        if fh > H * 0.6:
            fh = int(H * 0.6)
            fw = int(front.width * fh / front.height)
        front = front.resize((fw, fh), Image.LANCZOS)
        canvas.alpha_composite(front, (int(cx - fw / 2), int(min(H - fh, cy + r * front_y))))
    return canvas
