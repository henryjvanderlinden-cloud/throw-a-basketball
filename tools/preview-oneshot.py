#!/usr/bin/env python3
"""Play a one-shot's rolls side by side between stretches of the still pose.

handovers/HANDOVER_10.md. For the steal and `stolen`: each roll's animation
frames at the game's rate, preceded and followed by the character's still
pose (his dribble's highest-hand frame, which frame 3 of both is meant to
match), so a jump at either end shows. Writes build/preview/<seq>-oneshot.gif.

    py tools\\preview-oneshot.py steal_r 1,2,3 --fps 8
    py tools\\preview-oneshot.py stolen 1,2,3 --fps 6
"""
import argparse, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("ct", ROOT / "tools" / "compare-takes.py")
ct = importlib.util.module_from_spec(_s); _s.loader.exec_module(ct)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seq")
    ap.add_argument("rolls", nargs="?", default="1,2,3")
    ap.add_argument("--char", default="zombie")
    ap.add_argument("--folder", default="Zombie")
    ap.add_argument("--frames", type=int, default=3)
    ap.add_argument("--fps", type=float, default=8)
    ap.add_argument("--scale", type=float, default=1.12)
    ap.add_argument("--still", type=int, default=3, help="1-based dribble_idle frame held still")
    a = ap.parse_args()
    still = ct.reference(a.char, "dribble_idle")[a.still - 1]
    poses = ROOT / "artwork" / "basketball-players" / f"{a.folder} poses"
    cols = [(r, ct.take(poses / f"{a.seq}.r{r}.png", a.frames + 1, a.scale)) for r in a.rolls.split(",")]
    K, CW, H = 1.0, 330, 360
    order = [None] + list(range(a.frames)) + [None]
    ms = [600] + [round(1000 / a.fps)] * a.frames + [900]
    out = []
    for fi in order:
        img = Image.new("RGB", (CW * len(cols), H), (238, 238, 232))
        d = ImageDraw.Draw(img)
        g = H - 15
        d.line([(0, g), (img.width, g)], fill=(150, 150, 150))
        for ci, (r, fr) in enumerate(cols):
            im, fx, fy = still if fi is None else fr[fi]
            img.paste(im, (round(ci * CW + CW / 2 - fx), round(g - fy)), im)
            d.text((ci * CW + 6, 6), f"{a.char} r{r}  " + ("still pose" if fi is None else f"{a.seq} {fi + 1}"),
                   fill=(0, 0, 0))
        out.append(img)
    path = ROOT / "build" / "preview" / f"{a.seq}-oneshot.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0)
    print(path)


if __name__ == "__main__":
    main()
