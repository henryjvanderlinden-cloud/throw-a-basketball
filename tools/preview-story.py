#!/usr/bin/env python3
"""Play a STORY sequence's rolls inside the standing dribble, at game timing.

handovers/HANDOVER_10.md. A story (build-sprites.py STORY_SEQ) plays once, one
frame per half bounce, starting on the ball's apex, between stretches of the
plain dribble -- so a roll is only judged fairly in that setting, with the
ball: does the hand meet it in frames 1 and 3, and does the break read at
0.22 s a frame? This lays every roll side by side, each wrapped in the
character's approved dribble_idle and with the ball drawn where the game
draws it, and writes build/preview/<seq>-story.gif.

    py tools\\preview-story.py break_face 1,2,3
    py tools\\preview-story.py panic 1,2,3 --hold 3,4        # then cycle 3-4
    py tools\\preview-story.py break_face --approved --scale 1.12

--scale is the roll's size against its own calibration frame (SEQ_SCALE's
job); the dribble around it is the built sprite, already at its own.
"""
import argparse, importlib.util, math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("ct", ROOT / "tools" / "compare-takes.py")
ct = importlib.util.module_from_spec(_s); _s.loader.exec_module(ct)

DRIB = 7.0                  # dribT per second, standing (index.html)
BALL_R, HAND_H, LATERAL = 13, 0.42, 0.26
APEX = 2                    # dribble_idle's apex frame, 0-based (APEX_FRAME)
K = 1.0
FPS = 30


def dribble_frame(d, n=4):
    u = (d % math.pi) / math.pi
    return math.floor((u * n + APEX + 0.5 - n / 2) % n) % n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seq")
    ap.add_argument("rolls", nargs="?", default="1,2,3")
    ap.add_argument("--char", default="zombie")
    ap.add_argument("--folder", default="Zombie")
    ap.add_argument("--frames", type=int, default=4)
    ap.add_argument("--scale", type=float, default=1.12)
    ap.add_argument("--hold", default=None, help="1-based frames to cycle after the story")
    ap.add_argument("--stand", type=float, default=132.0, help="standH, game units")
    ap.add_argument("--approved", action="store_true")
    a = ap.parse_args()

    drib = ct.reference(a.char, "dribble_idle")
    poses = ROOT / "artwork" / "basketball-players" / f"{a.folder} poses"
    names = ["approved"] if a.approved else [f"r{r}" for r in a.rolls.split(",")]
    cols = [(nm, ct.take(poses / f"{a.seq}.{nm}.png", a.frames + 1, a.scale)) for nm in names]
    hold = [int(x) - 1 for x in a.hold.split(",")] if a.hold else []

    start = math.ceil((2 * math.pi - math.pi / 4) / math.pi) * math.pi + math.pi / 4
    story_len = a.frames + 2 * len(hold) * 2          # hold cycles twice, if any
    end = start + story_len * math.pi / 2
    total = end + 2 * math.pi                        # two bounces of dribble after
    CW, H = int(260 * K), int(345 * K)
    out = []
    t = 0.0
    while t * DRIB < total:
        d = t * DRIB
        j = math.floor((d - start) / (math.pi / 2)) if d >= start else -1
        img = Image.new("RGB", (CW * len(cols), H), (238, 238, 232))
        dr = ImageDraw.Draw(img)
        g = H - 15
        dr.line([(0, g), (img.width, g)], fill=(150, 150, 150))
        for ci, (nm, fr) in enumerate(cols):
            if 0 <= j < a.frames:
                im, fx, fy = fr[j]; label = f"{a.seq} {j + 1}"
            elif hold and a.frames <= j < story_len:
                k = hold[(j - a.frames) % len(hold)]
                im, fx, fy = fr[k]; label = f"{a.seq} {k + 1} (hold)"
            else:
                im, fx, fy = drib[dribble_frame(d)]; label = "dribble"
            im2 = im.resize((round(im.width * K), round(im.height * K)), Image.NEAREST)
            cx = ci * CW + CW / 2
            img.paste(im2, (round(cx - fx * K), round(g - fy * K)), im2)
            # the ball, where index.html puts it: out on the viewer's left
            peak = max(6, a.stand * HAND_H - 0.5 * BALL_R)
            h = abs(math.sin(d)) * peak
            bx = cx - a.stand * LATERAL * 2 * K
            by = g - (BALL_R + h) * 2 * K
            r = BALL_R * 2 * K
            dr.ellipse([bx - r, by - r, bx + r, by + r], fill=(222, 110, 30), outline=(90, 40, 10))
            dr.text((ci * CW + 6, 6), f"{a.char} {nm}", fill=(0, 0, 0))
            dr.text((ci * CW + 6, 20), label, fill=(0, 0, 0))
        out.append(img)
        t += 1 / FPS
    path = ROOT / "build" / "preview" / f"{a.seq}-story.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    out[0].save(path, save_all=True, append_images=out[1:], duration=round(1000 / FPS), loop=0)
    print(path, f"{len(out)} frames")


if __name__ == "__main__":
    main()
