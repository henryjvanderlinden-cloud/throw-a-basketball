#!/usr/bin/env python3
"""Turn the source pose art into game-ready sprites.

Reads   artwork/basketball-players/<Name> poses/*.png   (1086x1448, 8 poses)
Writes  sprites/<key>/01..08.png                        (trimmed, scaled, quantised)
        sprites/manifest.js                             (window.SPRITE_MANIFEST)

Each source pose was drawn to fill its own canvas, so the eight poses of a
character are NOT in register with one another. They are aligned here on the
one landmark that is reliable in every pose: the feet. Each pose is trimmed to
its own silhouette, and the manifest records where that pose's feet sit inside
the trimmed frame, so the game can plant every frame on the same spot.

A single scale per character keeps things simple. Poses with the arms overhead
are drawn slightly smaller by the artist, but each animation *pair* is two
poses of the same kind, so the small difference only ever shows up on a state
change, never inside a loop.

Run from anywhere:  python tools/build-sprites.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "artwork" / "basketball-players"
OUT = ROOT / "sprites"

# Height of the plain standing pose, in game units (the viewBox is 960x640).
# Frames are written at SUPERSAMPLE x this so they stay crisp on hidpi screens.
STANDING_H = 132
SUPERSAMPLE = 2

# The source art has a faint alpha haze over the whole canvas; anything below
# this is background.
ALPHA_CUT = 128

CHARACTERS = [
    # key,            source folder,        label,           idle pose (1-based)
    ("nba",          "NBA player poses",    "NBA Player",    1),
    ("highschooler", "Higschooler poses",   "High Schooler", 1),
    ("monkey",       "Monkey poses",        "Monkey",        1),
    ("zombie",       "Zombie poses",        "Zombie",        1),
]

# Which pose plays when. Numbers are 1-based pose indices.
#   dribble : two front-facing stances, alternated for the old-school heave
#   aim     : two back-facing stances, alternated slowly
#   charge  : the wind-up, alternated fast so it reads as tensing
#   release : held for a moment at the instant of the throw
#   follow  : the follow-through, straight after the release
POSES = {
    "nba":          {"dribble": [1, 5], "aim": [2, 6], "charge": [7, 6], "release": [8], "follow": [4]},
    "highschooler": {"dribble": [1, 2], "aim": [3, 4], "charge": [6, 5], "release": [7], "follow": [8]},
    "monkey":       {"dribble": [1, 2], "aim": [3, 4], "charge": [6, 8], "release": [7], "follow": [5]},
    "zombie":       {"dribble": [1, 2], "aim": [3, 4], "charge": [6, 5], "release": [7], "follow": [8]},
}


def mask(im: Image.Image) -> np.ndarray:
    return np.array(im.getchannel("A")) > ALPHA_CUT


def silhouette_box(m: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def foot_centre(m: np.ndarray, y1: int, band: int) -> float:
    """Horizontal centre of whatever is touching the ground."""
    strip = m[max(0, y1 - band):y1, :]
    xs = np.where(strip.any(axis=0))[0]
    return float((xs.min() + xs.max()) / 2) if len(xs) else m.shape[1] / 2


def build_character(key: str, folder: str, label: str, idle_pose: int) -> dict:
    files = sorted((SRC / folder).glob("*.png"))
    if len(files) != 8:
        raise SystemExit(f"{folder}: expected 8 poses, found {len(files)}")

    ims = [Image.open(f).convert("RGBA") for f in files]
    masks = [mask(im) for im in ims]
    boxes = [silhouette_box(m) for m in masks]

    idle_box = boxes[idle_pose - 1]
    scale = STANDING_H / (idle_box[3] - idle_box[1])

    out_dir = OUT / key
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for i, (im, m, box) in enumerate(zip(ims, masks, boxes), start=1):
        x0, y0, x1, y1 = box
        band = max(4, (y1 - y0) // 30)
        fx = foot_centre(m, y1, band) - x0        # feet, relative to the crop
        fy = y1 - y0                              # ground line = bottom of crop

        crop = im.crop(box)
        w = max(1, round(crop.width * scale * SUPERSAMPLE))
        h = max(1, round(crop.height * scale * SUPERSAMPLE))
        frame = crop.resize((w, h), Image.LANCZOS)

        alpha = frame.getchannel("A").point(lambda v: 255 if v > ALPHA_CUT else 0)
        q = frame.convert("RGB").quantize(colors=128, method=Image.MEDIANCUT,
                                          dither=Image.NONE).convert("RGBA")
        q.putalpha(alpha)
        q.save(out_dir / f"{i:02d}.png", optimize=True)

        frames.append({
            "src": f"sprites/{key}/{i:02d}.png",
            "w": round(crop.width * scale, 2),     # display units
            "h": round(crop.height * scale, 2),
            "footX": round(fx * scale, 2),         # where to plant it, within the frame
            "footY": round(fy * scale, 2),
        })

    # Where the raised hands land on the release pose -- the ball is drawn there.
    rel_i = POSES[key]["release"][0] - 1
    rel_m, rel_box, rel = masks[rel_i], boxes[rel_i], frames[POSES[key]["release"][0] - 1]
    x0, y0, x1, y1 = rel_box
    hand_band = rel_m[y0:y0 + max(4, (y1 - y0) // 14), :]
    hxs = np.where(hand_band.any(axis=0))[0]
    hand_x = (float((hxs.min() + hxs.max()) / 2) - x0) * scale - rel["footX"]
    hand_y = -rel["footY"]                        # top of the release pose

    return {
        "key": key, "label": label, "frames": frames, "poses": POSES[key],
        "handX": round(hand_x, 2), "handY": round(hand_y, 2),
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    chars = [build_character(k, f, l, i) for k, f, l, i in CHARACTERS]
    js = ("// Generated by tools/build-sprites.py -- do not edit by hand.\n"
          "window.SPRITE_MANIFEST = "
          + json.dumps({"standingHeight": STANDING_H, "characters": chars}, indent=1)
          + ";\n")
    (OUT / "manifest.js").write_text(js, encoding="utf-8")

    for c in chars:
        hs = [f["h"] for f in c["frames"]]
        print(f"{c['key']:<14} heights {min(hs):.0f}-{max(hs):.0f}  "
              f"hand ({c['handX']:+.0f},{c['handY']:+.0f})")
    pngs = list(OUT.rglob("*.png"))
    print(f"\n{len(pngs)} frames, {sum(f.stat().st_size for f in pngs)/1024:.0f} KB total")


if __name__ == "__main__":
    main()
