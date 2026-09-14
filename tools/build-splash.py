#!/usr/bin/env python3
"""Turn the splash artwork into the frames the menus are made of.

    python tools/build-splash.py      # artwork/Splash Screens/ -> splash/

Two screens come out of it:

    splash/mode-0.webp                  the number-of-players screen
    splash/mode-1.webp .. mode-4.webp   *patches*, not whole screens -- see below
    splash/select.webp                  the character select
    splash/won-1.webp, won-2.webp       the winner's banner, laid over the court
    splash/manifest.js                  where each patch goes

## Resolution is left alone

An earlier version resampled everything to 1280 wide. Do not put that back. This
is pixel art: hard one-pixel steps and ordered dithering in the gradients, and a
0.88x LANCZOS pass is precisely the thing that destroys both. It read as mush
around the lettering. The browser scales the picture to the stage anyway, so
resampling here only means doing it twice, the first time worse.

## The variations are patches

The four wink/blink/point frames are separate generations of the same painting,
not one painting with an edited face, so at the pixel level they differ *slightly
everywhere*: mean difference about 21/255, concentrated on linework, from the
generator re-rendering every edge. But the part that actually differs -- an eye,
a mouth, a raised finger -- is one small region, 1-3% of the frame.

So each variation is cut down to that region and written as a patch with a
feathered edge, and the game lays it over the base frame. The feather is what
hides the generator's edge jitter around the cut; without it the patch boundary
is faintly visible. Four patches come to about 68 KB against 1.45 MB for four
whole frames, the base never reloads, and the swap cannot flicker because only a
small overlay changes.

If the artwork is ever regenerated so the frames are pixel-identical outside the
expression, this still works unchanged -- the region finder simply finds a
cleaner region.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "artwork" / "Splash Screens"
OUT = ROOT / "splash"

QUALITY = 90          # the dithering needs the headroom; 82 smeared it
PATCH_QUALITY = 92
BLOCK = 16            # granularity of the region search
PAD_BLOCKS = 3        # margin around the found region, for the feather to live in
FEATHER = 14          # px of alpha ramp at the patch edge

BASE = ("mode-0", "Splash_Select_number_of_Players.png")
SCREENS = {"select": "Splash_Select_Player_v02.png"}
VARIATIONS = {
    "mode-1": "throw-a-basketball-7-blink-point.png",
    "mode-2": "throw-a-basketball-12-wink.png",
    "mode-3": "throw-a-basketball-34-ooo.png",
    "mode-4": "throw-a-basketball-13-blink.png",
}

BANNERS = {"won-1": "player-1-has-won-blue.png", "won-2": "player-2-has-won-red.png"}
BANNER_W = 1024
BANNER_Q = 88


def largest_region(mask: np.ndarray) -> list[tuple[int, int]]:
    """The biggest 8-connected group of True blocks, flood-filled by hand."""
    seen = np.zeros_like(mask, bool)
    best: list[tuple[int, int]] = []
    for sy in range(mask.shape[0]):
        for sx in range(mask.shape[1]):
            if not mask[sy, sx] or seen[sy, sx]:
                continue
            stack = [(sy, sx)]
            seen[sy, sx] = True
            comp = []
            while stack:
                y, x = stack.pop()
                comp.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1]
                                and mask[ny, nx] and not seen[ny, nx]):
                            seen[ny, nx] = True
                            stack.append((ny, nx))
            if len(comp) > len(best):
                best = comp
    return best


def feather(patch: Image.Image) -> Image.Image:
    w, h = patch.size
    a = np.ones((h, w), float)
    for i in range(min(FEATHER, h // 2, w // 2)):
        v = (i + 1) / (FEATHER + 1)
        a[i, :] = np.minimum(a[i, :], v)
        a[h - 1 - i, :] = np.minimum(a[h - 1 - i, :], v)
        a[:, i] = np.minimum(a[:, i], v)
        a[:, w - 1 - i] = np.minimum(a[:, w - 1 - i], v)
    arr = np.array(patch.convert("RGBA"))
    arr[..., 3] = (a * 255).astype("uint8")
    return Image.fromarray(arr)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    base_src = SRC / BASE[1]
    if not base_src.exists():
        print(f"no {BASE[1]} - nothing to do")
        return
    base = Image.open(base_src).convert("RGB")
    W, H = base.size
    a = np.asarray(base).astype(int)
    total = 0

    dest = OUT / f"{BASE[0]}.webp"
    base.save(dest, "WEBP", quality=QUALITY, method=6)
    total += dest.stat().st_size
    print(f"{BASE[0]:<10} {W}x{H}  {dest.stat().st_size/1024:6.0f} KB   <- {BASE[1]}")

    for name, fname in SCREENS.items():
        src = SRC / fname
        if not src.exists():
            print(f"{name:<10} SKIPPED (no {fname})")
            continue
        im = Image.open(src).convert("RGB")
        dest = OUT / f"{name}.webp"
        im.save(dest, "WEBP", quality=QUALITY, method=6)
        total += dest.stat().st_size
        print(f"{name:<10} {im.width}x{im.height}  {dest.stat().st_size/1024:6.0f} KB   <- {fname}")

    variations = []
    for name, fname in VARIATIONS.items():
        src = SRC / fname
        if not src.exists():
            print(f"{name:<10} SKIPPED (no {fname})")
            continue
        im = Image.open(src).convert("RGB")
        drift = ""
        if im.size != base.size:
            # The generator does not always come back to the pixel: one frame
            # arrived 1447x1087 against the others' 1448x1086.
            drift = f"  (source {im.width}x{im.height}, squared up)"
            im = im.resize(base.size, Image.LANCZOS)
        d = np.abs(a - np.asarray(im).astype(int)).max(axis=2).astype(float)
        bh, bw = H // BLOCK, W // BLOCK
        bm = d[:bh * BLOCK, :bw * BLOCK].reshape(bh, BLOCK, bw, BLOCK).mean(axis=(1, 3))
        thr = max(28.0, float(np.percentile(bm, 99.5)))
        comp = largest_region(bm >= thr)
        if not comp:
            print(f"{name:<10} SKIPPED (no region differs from the base){drift}")
            continue
        ys = [c[0] for c in comp]
        xs = [c[1] for c in comp]
        y0 = max(0, min(ys) - PAD_BLOCKS) * BLOCK
        y1 = min(H, (max(ys) + 1 + PAD_BLOCKS) * BLOCK)
        x0 = max(0, min(xs) - PAD_BLOCKS) * BLOCK
        x1 = min(W, (max(xs) + 1 + PAD_BLOCKS) * BLOCK)
        patch = feather(im.crop((x0, y0, x1, y1)))
        dest = OUT / f"{name}.webp"
        patch.save(dest, "WEBP", quality=PATCH_QUALITY, method=6)
        kb = dest.stat().st_size / 1024
        total += dest.stat().st_size
        variations.append({"name": name, "x": round(x0 / W, 6), "y": round(y0 / H, 6),
                           "w": round((x1 - x0) / W, 6), "h": round((y1 - y0) / H, 6)})
        print(f"{name:<10} patch {x1-x0}x{y1-y0} at ({x0},{y0})  {kb:6.0f} KB   "
              f"<- {fname} ({100*(x1-x0)*(y1-y0)/(W*H):.1f}% of the frame){drift}")

    for name, fname in BANNERS.items():
        src = SRC.parent / fname
        if not src.exists():
            print(f"{name:<10} SKIPPED (no {fname})")
            continue
        im = Image.open(src).convert("RGBA")
        al = np.array(im.getchannel("A"))
        ys, xs = np.where(al > 8)
        im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
        # The RGB beneath fully transparent pixels is the generator's
        # transparency checkerboard. Lossy compression drags that into the
        # visible edge, so flatten it first.
        arr = np.array(im)
        clear = arr[..., 3] < 8
        for c in range(3):
            arr[..., c][clear] = 0
        im = Image.fromarray(arr)
        if im.width != BANNER_W:
            im = im.resize((BANNER_W, round(im.height * BANNER_W / im.width)), Image.LANCZOS)
        dest = OUT / f"{name}.webp"
        im.save(dest, "WEBP", quality=BANNER_Q, method=6)
        total += dest.stat().st_size
        print(f"{name:<10} {im.width}x{im.height}  {dest.stat().st_size/1024:6.0f} KB   "
              f"<- {fname} (trimmed)")

    man = OUT / "manifest.js"
    man.write_text(
        "// Generated by tools/build-splash.py -- do not edit.\n"
        "// The mode screen is one base painting plus a small patch per variation;\n"
        "// x/y/w/h are fractions of the base, so they survive a re-render at any size.\n"
        "window.SPLASH_MANIFEST = " + json.dumps(
            {"base": BASE[0], "select": "select", "source": {"w": W, "h": H},
             "variations": variations}, indent=2) + ";\n",
        encoding="utf-8", newline="\n")
    print(f"\nmanifest.js  {len(variations)} variations")
    print(f"{total/1024/1024:.2f} MB total")


if __name__ == "__main__":
    main()
