#!/usr/bin/env python3
"""Play a reference character's sequence beside every roll of a new one.

handovers/HANDOVER_09.md §0(A): the monkey's frames are the spec. This lays the
monkey's game sprites and each roll's frames side by side on one ground line,
at the game's own scale, and animates them at the game's timing -- so a take is
judged moving, against the thing it has to match.

    py tools\\compare-takes.py shot 1,2,3                  # zombie rolls vs the monkey
    py tools\\compare-takes.py aim 1,2,3 --scale 1.06      # at a candidate size
    py tools\\compare-takes.py celebrate 1,2 --timing 400,400

Writes build/preview/<seq>-compare.gif. Rolls are read from
artwork/basketball-players/Zombie poses/<seq>.r<N>.png; --approved compares
the approved take instead. The zombie is drawn at its calibration scale times
--scale (SEQ_SCALE's job, set after a take is picked); nothing is normalised
automatically, because every automatic landmark tried (shoes, head width)
disagreed with the eye on some take (handover 09 §0(C)).
"""
import argparse, importlib.util, json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("pt", ROOT / "tools" / "preview-take.py")
pt = importlib.util.module_from_spec(_s); _s.loader.exec_module(pt)

# Frame order and per-frame milliseconds, as index.html plays each sequence.
# The shot shows its coil frame as a bridge; the game itself starts at frame 2.
TIMING = {
    "turn": ([0, 1, 1], [180, 180, 700]),
    "aim": ([0, 1], [385, 385]),
    "charge": ([0, 1, 2, 1], [350, 350, 700, 350]),
    "shot": ([0, 1, 2, 3, 3], [300, 60, 220, 500, 500]),
}
K = 1.5          # display pixels per sprite pixel (sprites are 2 px per unit)


def reference(char, seq):
    s = (ROOT / "sprites" / "manifest.js").read_text(encoding="utf-8")
    m = {c["key"]: c for c in json.loads(s[s.index("{"):s.rindex("}") + 1])["characters"]}
    return [(Image.open(ROOT / f["src"]).convert("RGBA"), f["footX"] * 2, f["footY"] * 2)
            for f in m[char]["sequences"][seq]]


def take(path, cells, scale):
    figs = pt.figures(path, cells)
    ys = np.nonzero((np.array(figs[0].getchannel("A")) > 128).any(1))[0]
    k = 264 / (ys.max() - ys.min()) * scale          # 132 units standing, 2 px each
    out = []
    for f in figs[1:]:
        a = np.array(f.getchannel("A")) > 128
        yy, xx = np.nonzero(a)
        f = f.crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1))
        a = np.array(f.getchannel("A")) > 128
        cols = np.nonzero(a[int(a.shape[0] - 0.07 * (ys.max() - ys.min())):].any(0))[0]
        cx = (cols.min() + cols.max()) / 2
        f = f.resize((round(f.width * k), round(f.height * k)), Image.NEAREST)
        out.append((f, cx * k, f.height))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seq")
    ap.add_argument("rolls", nargs="?", default="1,2,3")
    ap.add_argument("--char", default="zombie")
    ap.add_argument("--folder", default="Zombie")
    ap.add_argument("--ref", default="monkey")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--approved", action="store_true")
    ap.add_argument("--timing", default=None, help="ms per frame, comma-separated")
    a = ap.parse_args()

    ref = reference(a.ref, a.seq)
    n = len(ref)
    order, ms = TIMING.get(a.seq, (list(range(n)), [300] * n))
    if a.timing:
        ms = [int(x) for x in a.timing.split(",")]
        order = list(range(len(ms)))
    poses = ROOT / "artwork" / "basketball-players" / f"{a.folder} poses"
    names = ["approved"] if a.approved else [f"r{r}" for r in a.rolls.split(",")]
    cols = [(a.ref, ref)] + [(f"{a.char} {nm}", take(poses / f"{a.seq}.{nm}.png", n + 1, a.scale))
                             for nm in names]
    CW, H = int(200 * K), int(360 * K)
    frames = []
    for fi in order:
        img = Image.new("RGB", (CW * len(cols), H), (238, 238, 232))
        d = ImageDraw.Draw(img)
        g = H - 15
        d.line([(0, g), (img.width, g)], fill=(150, 150, 150))
        d.line([(0, g - 264 * K), (img.width, g - 264 * K)], fill=(225, 160, 160))
        for ci, (name, fr) in enumerate(cols):
            im, fx, fy = fr[min(fi, len(fr) - 1)]
            im2 = im.resize((round(im.width * K), round(im.height * K)), Image.NEAREST)
            img.paste(im2, (round(ci * CW + CW / 2 - fx * K), round(g - fy * K)), im2)
            d.text((ci * CW + 6, 6), f"{name}  {a.seq} {fi + 1}", fill=(0, 0, 0))
        frames.append(img)
    out = ROOT / "build" / "preview" / f"{a.seq}-compare.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(out)


if __name__ == "__main__":
    main()
