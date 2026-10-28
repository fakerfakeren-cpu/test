"""Turn source photos into HOI4-style portraits.

  source_images/<name>.*  ->  mod/bfx_bulgaria/gfx/leaders/BUL/bfx_<name>.dds        (156x210, leader)
                          ->  mod/bfx_bulgaria/gfx/interface/ideas/bfx_<name>_small.dds (65x67, advisor)

Pipeline: rembg person cut-out (GrabCut fallback) -> face-centred crop (OpenCV Haar)
-> mild colourisation (luminance gradient map, warm skin / cool shadows) -> painterly
softening + grain -> composited on a generated backdrop matching vanilla portraits
(dark warm-grey vertical gradient, vignette, faint canvas texture).
Also writes a preview sheet to tools/out/portrait_preview.png.
"""
import os, sys, glob
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ddslib import write_dds, read_dds

SRC = os.path.join(ROOT, "source_images")
MOD = os.path.join(ROOT, "mod", "bfx_bulgaria")
OUT_L = os.path.join(MOD, "gfx", "leaders", "BUL")
OUT_S = os.path.join(MOD, "gfx", "interface", "ideas")
PREV = os.path.join(HERE, "out")
for d in (OUT_L, OUT_S, PREV):
    os.makedirs(d, exist_ok=True)

RNG = np.random.default_rng(1936)


def backdrop(w, h, seed=0):
    """Vanilla-like portrait background: darker top/edges, lighter band behind the shoulders."""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(-1, 1, w)[None, :]
    # vertical profile sampled from vanilla: ~30 at top, ~85 at 55-60% height
    prof = 30 + 58 * np.exp(-((y - 0.6) / 0.33) ** 2)
    vign = 1 - 0.28 * (x ** 2)
    lum = prof * vign
    tex = rng.normal(0, 1, (h // 3 + 1, w // 3 + 1))
    tex = np.array(Image.fromarray(((tex * 12) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(float) - 128
    lum = lum + tex * 0.35 + rng.normal(0, 1.6, (h, w))
    rgb = np.stack([lum + 3, lum, lum - 6], -1)  # slightly warm, as in vanilla
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8), "RGB")


def cutout(img):
    """RGBA person cut-out. rembg first; GrabCut if the model is unavailable."""
    try:
        from rembg import remove, new_session
        global _SESSION
        if "_SESSION" not in globals():
            _SESSION = {m: new_session(m) for m in ("u2net_human_seg", "u2net")}
        best = None
        for model, sess in _SESSION.items():
            out = remove(img, session=sess, post_process_mask=True)
            a = np.array(out.getchannel("A")) > 128
            # a usable person mask covers a good share of the frame and reaches the bottom edge
            if a.mean() > 0.18 and a[-3:].mean() > 0.25:
                return out, "rembg/" + model
            if best is None or a.mean() > best[0]:
                best = (a.mean(), out, "rembg/" + model + " (best of two)")
        if best[0] > 0.10 and np.array(best[1].getchannel("A"))[-3:].mean() > 60:
            return best[1], best[2]
        # halftone scans defeat segmentation: keep the photo, feather it into the backdrop
        w, h = img.size
        yy, xx = np.mgrid[0:h, 0:w]
        ell = ((xx - w / 2) / (w * 0.50)) ** 2 + ((yy - h * 0.62) / (h * 0.66)) ** 2
        m = np.clip((1.0 - ell) / 0.35, 0, 1) * 255
        out = img.convert("RGBA")
        out.putalpha(Image.fromarray(m.astype(np.uint8)))
        return out, "elliptical vignette (segmentation failed)"
    except Exception as e:  # pragma: no cover - network/model failure path
        print("  rembg unavailable:", e)
    arr = np.array(img.convert("RGB"))[:, :, ::-1].copy()
    h, w = arr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(w * 0.06), int(h * 0.03), int(w * 0.88), int(h * 0.96))
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(arr, mask, rect, bg, fg, 6, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    m = cv2.GaussianBlur(m, (5, 5), 0)
    out = img.convert("RGBA")
    out.putalpha(Image.fromarray(m))
    return out, "opencv/grabcut"


_FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


def find_face(img):
    g = cv2.equalizeHist(np.array(img.convert("L")))
    h, w = g.shape
    best = None
    for casc, flip in ((_FACE, False), (_PROF, False), (_PROF, True)):
        gg = g[:, ::-1] if flip else g
        faces = casc.detectMultiScale(gg, 1.08, 5, minSize=(w // 8, w // 8))
        for (x, y, fw, fh) in faces:
            if flip:
                x = w - x - fw
            if y > h * 0.6:
                continue
            if best is None or fw * fh > best[2] * best[3]:
                best = (x, y, fw, fh)
        if best is not None:
            return best
    # fallback: top of the alpha mask
    return None


def colourise(rgba):
    """Gradient-map luminance to a muted painted palette, keep alpha."""
    a = rgba.getchannel("A")
    lum = np.array(ImageOps.autocontrast(rgba.convert("L"), cutoff=1)).astype(float) / 255
    stops = np.array([0.0, 0.18, 0.45, 0.72, 1.0])
    cols = np.array([[12, 12, 16], [50, 40, 36], [138, 104, 84], [208, 168, 140], [246, 228, 210]], float)
    rgb = np.stack([np.interp(lum, stops, cols[:, c]) for c in range(3)], -1)
    grey = (lum * 255)[..., None].repeat(3, -1)
    rgb = 0.82 * rgb + 0.18 * grey  # mild, not full colourisation
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8), "RGB")
    out = out.filter(ImageFilter.SMOOTH_MORE)  # soften halftone/scan noise -> painterly
    out = ImageEnhance.Contrast(out).enhance(1.08)
    out.putalpha(a)
    return out


def compose(cut, face, size, head_frac, top_frac, seed):
    W, H = size
    cw, ch = cut.size
    # fade alpha over the last few pixels of the source so photo borders never show as hard edges
    edge = np.ones((ch, cw))
    k = max(4, cw // 40)
    ramp = np.linspace(0, 1, k)
    edge[:, :k] *= ramp[None, :]; edge[:, -k:] *= ramp[None, ::-1]
    edge[:k, :] *= ramp[:, None]
    a = (np.array(cut.getchannel("A")).astype(float) * edge).astype(np.uint8)
    cut = cut.copy(); cut.putalpha(Image.fromarray(a))
    if face is None:
        a = np.array(cut.getchannel("A")) > 128
        ys, xs = np.nonzero(a)
        top = ys.min()
        cx = xs[ys < top + ch * 0.15].mean()
        fh = ch * 0.22
        fy = top + fh * 0.25
    else:
        fx, fy, fw, fh = face
        cx = fx + fw / 2
    # head height (Haar box ~ brow..chin) scaled so it fills head_frac of the frame
    scale = (H * head_frac) / fh
    # never let the photo run out above the bottom edge of the frame
    scale = max(scale, H * (1 - top_frac) / max(1, ch - fy))
    crop_h = H / scale
    crop_w = W / scale
    y0 = fy - crop_h * top_frac
    x0 = cx - crop_w / 2
    box = tuple(int(round(v)) for v in (x0, y0, x0 + crop_w, y0 + crop_h))
    canvas = Image.new("RGBA", (int(crop_w) + 1, int(crop_h) + 1), (0, 0, 0, 0))
    canvas.paste(cut, (-box[0], -box[1]))
    person = canvas.resize((W, H), Image.LANCZOS)
    bg = backdrop(W, H, seed).convert("RGBA")
    # soft drop shadow behind the figure so it sits in the scene
    sh = person.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.45))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(sh)
    bg.alpha_composite(shadow, (2, 2))
    bg.alpha_composite(person)
    out = bg.convert("RGB")
    grain = RNG.normal(0, 3.2, (H, W, 1))
    out = Image.fromarray((np.array(out).astype(float) + grain).clip(0, 255).astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(1.2, 40, 2))


def main(names=None):
    files = sorted(f for f in glob.glob(os.path.join(SRC, "*.*")) if not f.endswith(".gitkeep"))
    previews, report = [], []
    for i, f in enumerate(files):
        name = os.path.splitext(os.path.basename(f))[0]
        if names and name not in names:
            continue
        img = Image.open(f).convert("RGB")
        if name.endswith("__hoi4"):
            # already a finished in-game portrait (user-supplied): keep it, derive the small one
            name = name[: -len("__hoi4")]
            large = img.resize((156, 210), Image.LANCZOS) if img.size != (156, 210) else img
            face = find_face(large)
            fx, fy, fw, fh = face if face is not None else (40, 40, 76, 90)
            side = int(fh * 1.75)
            cx, cy = fx + fw / 2, fy + fh * 0.55
            box = (int(cx - side / 2), int(cy - side * 0.52), int(cx + side / 2), int(cy + side * 0.52))
            small = large.crop(box).resize((65, 67), Image.LANCZOS)
            how = "as supplied (HOI4 portrait)"
        else:
            cut, how = cutout(img)
            face = find_face(img)
            col = colourise(cut)
            large = compose(col, face, (156, 210), head_frac=0.33, top_frac=0.25, seed=i)
            small = compose(col, face, (65, 67), head_frac=0.52, top_frac=0.20, seed=i + 100)
        pl = os.path.join(OUT_L, f"bfx_{name}.dds")
        ps = os.path.join(OUT_S, f"bfx_{name}_small.dds")
        write_dds(large, pl)
        write_dds(small, ps)
        for p, sz in ((pl, (156, 210)), (ps, (65, 67))):
            back = read_dds(p)
            assert back.size == sz, (p, back.size)
            assert back.getchannel("A").getextrema() == (255, 255), p
        report.append(f"{name}: cutout={how} face={'found' if face is not None else 'mask-fallback'}")
        previews.append((name, large, small))
    if previews:
        sheet = Image.new("RGB", (len(previews) * 166 + 10, 300), (24, 24, 24))
        for k, (n, l, s) in enumerate(previews):
            sheet.paste(l, (10 + k * 166, 10))
            sheet.paste(s, (10 + k * 166, 225))
        sheet.save(os.path.join(PREV, "portrait_preview.png"))
    print("\n".join(report))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
