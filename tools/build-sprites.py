#!/usr/bin/env python3
"""Turn the source pose art into game-ready sprites.

Two kinds of input, one kind of output.

NEW: artwork/basketball-players/<Name> frames/<sequence>/NN.png
     -- produced by tools/slice-strips.py from generated strips. One folder per
     animation sequence, left and right facings drawn separately.

OLD: artwork/basketball-players/<Name> poses/*.png
     -- the original eight single poses, which the game maps onto sequences and
     still mirrors for facing.

Both become sprites/<key>/<sequence>/NN.png plus sprites/manifest.js, so the
game only ever sees named sequences and has one code path.

Run from anywhere:  python tools/build-sprites.py
"""

from __future__ import annotations

import json
import shutil
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

# The source art has a faint alpha haze over the whole canvas; below this is
# background.
ALPHA_CUT = 128

CHARACTERS = [
    # key,            source folder stem,  label
    ("monkey",       "Monkey",             "Monkey"),
    ("nba",          "NBA player",         "NBA Player"),
    ("highschooler", "Higschooler",        "High Schooler"),
    ("zombie",       "Zombie",             "Zombie"),
]

# --- old-style characters -----------------------------------------------
# Which of the eight poses stands in for which sequence. Numbers are 1-based.
# In `dribble_idle` the LOWER-handed pose goes first: it is shown while the ball
# is up at the hand.
LEGACY_POSES = {
    "nba":          {"dribble": [1, 5], "aim": [2, 6], "charge": [7, 6], "shot": [8, 4]},
    "highschooler": {"dribble": [1, 2], "aim": [3, 4], "charge": [6, 5], "shot": [7, 8]},
    "zombie":       {"dribble": [1, 2], "aim": [3, 4], "charge": [6, 5], "shot": [7, 8]},
}
LEGACY_IDLE_POSE = 1        # the plain standing pose, used to set the scale

# --- per-sequence corrections -------------------------------------------
# Each strip is generated separately, so they drift in scale relative to each
# other even though every frame *within* a strip is consistent. No automatic
# landmark survives the pose changes (silhouette height, shoe width and ink area
# all move with the pose, not just with the scale), so these are measured by eye
# against the standing dribble. Regenerating a strip at a matching scale is the
# real fix; then its entry goes back to 1.0.
SEQ_SCALE = {
    "monkey": {
        "aim": 0.72, "turn": 0.87, "charge": 0.86, "shot": 0.94,
        "pickup": 0.85, "celebrate": 0.88, "gameover": 0.80,
        "run_r": 0.78, "run_l": 0.73, "break_wave": 0.95,
    },
}

# Which side of the body the ball sits on, +1 = viewer's right. Measured from
# the art: the generator put the monkey's dribbling hand on the viewer's LEFT
# for the standing poses, not the right the prompt asked for.
BALL_SIDE = {
    "monkey": {
        "dribble_idle": -1, "break_banana": -1, "break_wave": -1,
        "pickup": -1, "panic": -1, "run_dribble_r": +1, "run_dribble_l": -1,
    },
}

# Sequences where the feet genuinely travel, so the frame is anchored on the
# cell rather than on the feet. Everywhere else the feet are planted and get
# anchored directly, which stops the character sliding sideways mid-loop.
TRAVELLING = {"run_r", "run_l", "run_dribble_r", "run_dribble_l"}


def mask_of(im: Image.Image) -> np.ndarray:
    return np.array(im.getchannel("A")) > ALPHA_CUT


def bbox(m: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def write_frame(im: Image.Image, box, scale: float, dest: Path) -> tuple[float, float]:
    """Crop to `box`, scale, quantise, save. Returns display width/height."""
    crop = im.crop(box)
    w = max(1, round(crop.width * scale * SUPERSAMPLE))
    h = max(1, round(crop.height * scale * SUPERSAMPLE))
    frame = crop.resize((w, h), Image.LANCZOS)
    alpha = frame.getchannel("A").point(lambda v: 255 if v > ALPHA_CUT else 0)
    q = frame.convert("RGB").quantize(colors=128, method=Image.MEDIANCUT,
                                      dither=Image.NONE).convert("RGBA")
    q.putalpha(alpha)
    dest.parent.mkdir(parents=True, exist_ok=True)
    q.save(dest, optimize=True)
    return round(crop.width * scale, 2), round(crop.height * scale, 2)


# ---------------------------------------------------------------- new style
def build_from_sequences(key: str, stem: str, label: str) -> dict | None:
    src = SRC / f"{stem} frames"
    if not src.is_dir():
        return None
    seq_dirs = sorted(d for d in src.iterdir() if d.is_dir())
    if not seq_dirs:
        return None

    # Scale from the standing dribble, so every character stands the same height.
    ref_dir = src / "dribble_idle"
    ref = Image.open(sorted(ref_dir.glob("*.png"))[0]).convert("RGBA")
    rx0, ry0, rx1, ry1 = bbox(mask_of(ref))
    scale = STANDING_H / (ry1 - ry0)

    def foot_cx(m, box):
        y1 = box[3]
        band = m[max(0, y1 - max(4, (y1 - box[1]) // 12)):y1, :]
        xs = np.where(band.any(axis=0))[0]
        return float((xs.min() + xs.max()) / 2) if len(xs) else (box[0] + box[2]) / 2

    seq_scale = SEQ_SCALE.get(key, {})
    sequences = {}
    for d in seq_dirs:
        files = sorted(d.glob("*.png"))
        if not files:
            continue
        ims = [Image.open(f).convert("RGBA") for f in files]
        masks = [mask_of(im) for im in ims]
        boxes = [bbox(m) for m in masks]
        s = scale * seq_scale.get(d.name, 1.0)

        ground = max(b[3] for b in boxes)
        cell_cx = ims[0].width / 2
        travelling = d.name in TRAVELLING

        frames = []
        for i, (im, m, box) in enumerate(zip(ims, masks, boxes), start=1):
            # A travelling pose anchors on the cell, because its feet are
            # mid-stride and move on purpose. A planted pose anchors on its own
            # feet, so the character cannot drift sideways through the loop.
            ax = cell_cx if travelling else foot_cx(m, box)
            dest = OUT / key / d.name / f"{i:02d}.png"
            w, h = write_frame(im, box, s, dest)
            frames.append({
                "src": f"sprites/{key}/{d.name}/{i:02d}.png",
                "w": w, "h": h,
                "footX": round((ax - box[0]) * s, 2),
                "footY": round((ground - box[1]) * s, 2),
            })
        sequences[d.name] = frames

    return {"key": key, "label": label, "mirror": False, "sequences": sequences,
            "ballSide": BALL_SIDE.get(key, {})}


# ---------------------------------------------------------------- old style
def build_from_poses(key: str, stem: str, label: str) -> dict | None:
    src = SRC / f"{stem} poses"
    files = sorted(p for p in src.glob("*.png") if "_sequence_" not in p.name)
    if len(files) < 8:
        return None
    ims = [Image.open(f).convert("RGBA") for f in files]
    masks = [mask_of(im) for im in ims]
    boxes = [bbox(m) for m in masks]

    idle = boxes[LEGACY_IDLE_POSE - 1]
    scale = STANDING_H / (idle[3] - idle[1])

    def foot_centre(m, box):
        y1 = box[3]
        band = m[max(0, y1 - max(4, (y1 - box[1]) // 30)):y1, :]
        xs = np.where(band.any(axis=0))[0]
        return float((xs.min() + xs.max()) / 2) if len(xs) else m.shape[1] / 2

    def frame_for(pose: int, seq: str, idx: int) -> dict:
        im, m, box = ims[pose - 1], masks[pose - 1], boxes[pose - 1]
        dest = OUT / key / seq / f"{idx:02d}.png"
        w, h = write_frame(im, box, scale, dest)
        return {
            "src": f"sprites/{key}/{seq}/{idx:02d}.png",
            "w": w, "h": h,
            "footX": round((foot_centre(m, box) - box[0]) * scale, 2),
            "footY": round((box[3] - box[1]) * scale, 2),
        }

    p = LEGACY_POSES[key]
    plan = {
        "dribble_idle": p["dribble"],
        "run_dribble_r": p["dribble"],
        "run_dribble_l": p["dribble"],
        "run_r": p["dribble"],
        "run_l": p["dribble"],
        "aim": p["aim"],
        "charge": p["charge"],
        "shot": p["shot"],
    }
    sequences = {name: [frame_for(pose, name, i) for i, pose in enumerate(poses, 1)]
                 for name, poses in plan.items()}
    return {"key": key, "label": label, "mirror": True, "sequences": sequences,
            "ballSide": {}}


def hand_point(char: dict) -> tuple[float, float]:
    """Where the ball leaves the hand: the top of the release frame.

    The release is the second-to-last frame of `shot` for a full four-frame
    sequence, and the first of two for the old-style characters -- in both cases
    frames[-2].
    """
    shot = char["sequences"]["shot"]
    rel = shot[-2] if len(shot) >= 2 else shot[-1]
    im = Image.open(ROOT / rel["src"]).convert("RGBA")
    m = mask_of(im)
    x0, y0, x1, y1 = bbox(m)
    band = m[y0:y0 + max(2, (y1 - y0) // 14), :]
    xs = np.where(band.any(axis=0))[0]
    k = rel["w"] / im.width
    hand_x = float((xs.min() + xs.max()) / 2) * k - rel["footX"]
    return round(hand_x, 2), round(-rel["footY"], 2)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    chars = []
    for key, stem, label in CHARACTERS:
        char = build_from_sequences(key, stem, label) or build_from_poses(key, stem, label)
        if not char:
            print(f"{key:<14} SKIPPED (no art found)")
            continue
        char["handX"], char["handY"] = hand_point(char)
        chars.append(char)

    js = ("// Generated by tools/build-sprites.py -- do not edit by hand.\n"
          "window.SPRITE_MANIFEST = "
          + json.dumps({"standingHeight": STANDING_H, "characters": chars}, indent=1)
          + ";\n")
    (OUT / "manifest.js").write_text(js, encoding="utf-8")

    for c in chars:
        n = sum(len(f) for f in c["sequences"].values())
        kind = "strips" if not c["mirror"] else "poses"
        print(f"{c['key']:<14} {len(c['sequences']):>2} sequences, {n:>2} frames "
              f"({kind})  hand ({c['handX']:+.0f},{c['handY']:+.0f})")
    pngs = list(OUT.rglob("*.png"))
    print(f"\n{len(pngs)} frames, {sum(f.stat().st_size for f in pngs)/1024:.0f} KB total")


if __name__ == "__main__":
    main()
