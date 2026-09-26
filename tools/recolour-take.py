#!/usr/bin/env python3
"""Pull a generated strip's colours onto an approved strip's palette.

handovers/HANDOVER_10.md. Some rolls come back with the right poses in the
wrong colours -- a brighter blue kit, paler skin, a lemon-yellow number --
and the pose is worth more than the palette. This moves each colour family of
the take (blue kit, yellow trim and number, olive skin, white, the browns of
hair and rot) onto the same family's mean and spread in the reference, in
CIELAB, so shading and line work survive and only the palette shifts. Shapes
are untouched: it cannot remove a patch of kit the model drew that the
reference lacks.

    py tools\\recolour-take.py "<poses>\\dribble_idle.approved.png" "<poses>\\break_face.r3.png" "<poses>\\break_face.r3cc.png"

Needs numpy, Pillow and scikit-image.
"""
import sys
import numpy as np
from PIL import Image
from skimage import color

FAMILIES = ["blue kit", "yellow", "skin", "white", "brown"]


def load(p):
    return np.array(Image.open(p).convert("RGBA")).astype(float) / 255


def families(rgb):
    hsv = color.rgb2hsv(rgb)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    c = np.full(h.shape, -1)
    c[(h > 200) & (h < 260) & (s > 0.35) & (v > 0.2)] = 0
    c[(h > 35) & (h < 65) & (s > 0.45) & (v > 0.55) & (c < 0)] = 1
    c[(h >= 38) & (h < 100) & (s > 0.08) & (s <= 0.45) & (v > 0.25) & (c < 0)] = 2
    c[(s < 0.12) & (v > 0.75) & (c < 0)] = 3
    c[((h < 38) | (h > 330)) & (s > 0.2) & (v < 0.8) & (c < 0)] = 4
    return c


def main(ref_path, src_path, out_path):
    ref, src = load(ref_path), load(src_path)
    ra, sa = ref[..., 3] > 0.5, src[..., 3] > 0.5
    rl, sl = color.rgb2lab(ref[..., :3]), color.rgb2lab(src[..., :3])
    rc, sc = families(ref[..., :3]), families(src[..., :3])
    out = sl.copy()
    for k, name in enumerate(FAMILIES):
        rm, sm = ra & (rc == k), sa & (sc == k)
        if rm.sum() < 100 or sm.sum() < 100:
            continue
        mu_r, sd_r = rl[rm].mean(0), rl[rm].std(0) + 1e-3
        mu_s, sd_s = sl[sm].mean(0), sl[sm].std(0) + 1e-3
        out[sm] = (sl[sm] - mu_s) / sd_s * sd_r + mu_r
        print(f"{name:<9} L a b  {np.round(mu_s, 1)} -> {np.round(mu_r, 1)}")
    rgb = np.clip(color.lab2rgb(out), 0, 1)
    Image.fromarray((np.dstack([rgb, src[..., 3]]) * 255).round().astype(np.uint8)).save(out_path)
    print(out_path)


if __name__ == "__main__":
    main(*sys.argv[1:4])
