#!/usr/bin/env python3
"""The sheet and the loop Rick judges a take by, cut the way the game cuts it.

measure-strip.py previews with equal-width cells, which clips any figure that
reaches past its neighbour's line -- idle's raised hand came back chopped off,
with a fragment of it in the next cell. This lifts each figure out by its own
pixels with slice-strips.py's blob grouping, anchors every frame on the
midpoint between the shoes (as build-sprites.py does for a standing sequence),
and writes

    sheet.png      the posed frames in a row on one ground line
    loop.gif       those frames at the game's rate for the sequence
    feet.txt       each shoe's position, and for every PAIR of frames how far
                   the far shoe moves with the near one aligned -- the number
                   that picked idle's two usable frames (handover 05 §0(B))

    py tools\\preview-take.py "artwork\\basketball-players\\Zombie poses\\idle.r3.png" --hz 5
    py tools\\preview-take.py <strip> --frames 1 3 --hz 2.5      # a subset, as a loop

A run's feet travel on purpose, so build-sprites.py anchors a run on the
torso instead; --torso does the same here, with its own torso_centre():

    py tools\\preview-take.py "artwork\\basketball-players\\Zombie poses\\run_l.r1.png" --torso --hz 7
"""
import argparse, importlib.util, itertools
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ss", ROOT / "tools" / "slice-strips.py")
ss = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ss)

_bspec = importlib.util.spec_from_file_location("bs", ROOT / "tools" / "build-sprites.py")
bs = importlib.util.module_from_spec(_bspec); _bspec.loader.exec_module(bs)

SHOE_BAND = 0.07        # the bottom 7% of standing height holds both shoes
TILE_H, SHOW_H = 360, 300


def figures(path: Path, cells: int) -> list[Image.Image]:
    im = Image.open(path).convert("RGBA")
    mask = np.array(im.getchannel("A")) > ss.ALPHA_CUT
    labels, blobs = ss.components(mask)
    groups = ss.group_components(blobs, cells, im.width)
    if not groups:
        raise SystemExit("the figures touch -- cannot lift them out one by one")
    out = []
    for g in groups:
        arr = np.array(im)
        arr[:, :, 3] = np.where(np.isin(labels, [b[3] for b in g]), arr[:, :, 3], 0)
        out.append(Image.fromarray(arr))
    return out


def shoes(f: Image.Image, stand: float):
    """(left shoe x0, x1), (right shoe x0, x1), sole y -- split at the widest gap."""
    a = np.array(f.getchannel("A")) > ss.ALPHA_CUT
    bot = np.nonzero(a.any(1))[0].max()
    cols = np.nonzero(a[bot - int(SHOE_BAND * stand): bot + 1].any(0))[0]
    k = np.diff(cols).argmax()
    return (cols[0], cols[k]), (cols[k + 1], cols[-1]), bot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("strip", type=Path)
    ap.add_argument("--cells", type=int, default=5, help="calibration included")
    ap.add_argument("--frames", type=int, nargs="*", default=None,
                    help="1-based animation frames to show (default all)")
    ap.add_argument("--hz", type=float, default=5.0, help="loop rate")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--torso", action="store_true",
                    help="anchor on the torso, as the game does a run")
    a = ap.parse_args()
    out = a.out or ROOT / "build" / "preview" / a.strip.stem
    out.mkdir(parents=True, exist_ok=True)

    figs = figures(a.strip, a.cells)
    ys = np.nonzero((np.array(figs[0].getchannel("A")) > ss.ALPHA_CUT).any(1))[0]
    stand = float(ys.max() - ys.min())
    S = SHOW_H / stand
    W = int(SHOW_H * 1.4)
    pick = a.frames or list(range(1, len(figs)))

    feet = [shoes(f, stand) for f in figs]
    lines = [f"standing height {stand:.0f}px"]
    for i in range(1, len(figs)):
        (L, R, bot) = feet[i]
        lines.append(f"frame {i}: left shoe {L[0]}-{L[1]}, right shoe {R[0]}-{R[1]}, "
                     f"outer span {(R[1] - L[0]) / stand * 100:.1f}%, sole y {bot}")
    lines.append("pairs, left shoe aligned -- how far the right shoe moves:")
    for i, j in itertools.combinations(range(1, len(figs)), 2):
        (Li, Ri, _), (Lj, Rj, _) = feet[i], feet[j]
        d = ((Rj[0] + Rj[1]) - (Ri[0] + Ri[1])) / 2 - ((Lj[0] + Lj[1]) - (Li[0] + Li[1])) / 2
        lines.append(f"  {i} / {j}: {d:+.0f}px ({d / stand * 100:+.1f}%)")
    (out / "feet.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    tiles = []
    for i in pick:
        f = figs[i]
        (L, R, bot) = feet[i]
        cx = (L[0] + R[1]) / 2
        if a.torso:
            m = np.array(f.getchannel("A")) > ss.ALPHA_CUT
            cx = bs.torso_centre(m, bs.bbox(m))
        s = f.resize((int(f.width * S), int(f.height * S)), Image.NEAREST)
        t = Image.new("RGBA", (W, TILE_H), (250, 250, 250, 255))
        t.alpha_composite(s, (int(round(W / 2 - cx * S)), int(round(TILE_H - 12 - bot * S))))
        tiles.append(t)
    sheet = Image.new("RGB", (W * len(tiles), TILE_H + 22), "white")
    d = ImageDraw.Draw(sheet)
    for k, (i, t) in enumerate(zip(pick, tiles)):
        sheet.paste(t.convert("RGB"), (k * W, 22))
        d.text((k * W + 8, 6), f"{a.strip.stem}  frame {i}", fill=(60, 60, 65))
        d.line([(k * W, 0), (k * W, TILE_H + 22)], fill=(215, 215, 220))
    d.line([(0, 22 + TILE_H - 12), (sheet.width, 22 + TILE_H - 12)], fill=(228, 150, 150))
    sheet.save(out / "sheet.png")
    fl = [t.convert("P", palette=Image.ADAPTIVE, colors=255) for t in tiles]
    fl[0].save(out / "loop.gif", save_all=True, append_images=fl[1:],
               duration=round(1000 / a.hz), loop=0, disposal=2)
    print(f"{out}  frames {pick} at {a.hz} Hz")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
