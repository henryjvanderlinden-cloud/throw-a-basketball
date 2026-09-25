#!/usr/bin/env python3
"""Turn the source pose art into game-ready sprites.

Two kinds of input, one kind of output.

NEW: artwork/basketball-players/<Name> frames/<sequence>/NN.png
     -- produced by tools/slice-strips.py from generated strips. One folder per
     animation sequence, left and right facings drawn separately.

OLD: artwork/basketball-players/<Name> poses/*.png
     -- the original eight single poses, which the game maps onto sequences and
     still mirrors for facing.

MIXED: a character listed in MIXED takes the old poses as its base and lets
     every sliced sequence replace its old counterpart. This is how a character
     migrates one approved sequence at a time without losing the rest.

Both become sprites/<key>/<sequence>/NN.png plus sprites/manifest.js, so the
game only ever sees named sequences and has one code path.

Run from anywhere:  python tools/build-sprites.py
"""

from __future__ import annotations

import json
import re
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

# The eight old poses are named "<Name> 001.png" .. "<Name> 008.png". The poses
# folders also hold generated strips and takes, which must not be read as poses.
LEGACY_NAME = re.compile(r" \d{3}\.png$")

# Characters built from BOTH kinds of input: old poses for everything, then each
# sliced sequence in "<Name> frames/" replacing its old counterpart. Opt-in,
# because the monkey still has his old poses on disk and must stay strips-only.
MIXED = {"zombie"}

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
        "pickup": 0.85, "celebrate": 0.88, "gameover": 0.88,
        "run_r": 0.78, "run_l": 0.73, "break_wave": 0.95,
        "panic": 0.95, "celebrate_flip": 1.16,
        "run_dribble_r": 0.95, "run_dribble_l": 0.98,
    },
}

# How big each character is, as a multiple of the standing height above.
# Normalising everyone to the same total height is not the same as making them
# the same size: the monkey stands in a crouch, so matching his overall height
# scaled his body up until he was the biggest thing on the court. These are
# measured by eye, side by side on one baseline.
CHAR_SCALE = {
    "monkey": 0.88,          # a monkey, and crouched, so the shortest of them
    "nba": 1.10,             # the pro: taller and heavier than everybody
    "highschooler": 0.97,    # a teenager next to a professional
    "zombie": 1.00,
}

# Per-pose scale corrections for the old eight-pose art, keyed by pose number.
#
# Each of those poses was drawn to fill its own canvas, so a pose with the arms
# overhead has a SMALLER body -- the character visibly shrank at the moment it
# shot. These bring every pose back to the body scale of that character's
# standing pose. The landmark is the top of the kit: the jersey sits at the
# shoulders and does not move when the arms do, unlike the bounding box, and a
# pose used by two sequences measures the same from both, which is what says it
# is reading scale rather than posture.
#
# This table is scaffolding for the placeholder art and goes with it. Strips
# carry a calibration frame instead, which measures the same thing exactly.
POSE_SCALE = {
    "nba":         {1: 1.000, 2: 1.029, 4: 1.116, 5: 1.015,
                     6: 1.034, 7: 1.150, 8: 1.210},
    "highschooler":{1: 1.000, 2: 1.000, 3: 1.018, 4: 1.040,
                     5: 1.116, 6: 1.092, 7: 1.132, 8: 1.079},
    "zombie":      {1: 1.000, 2: 1.025, 3: 1.014, 4: 1.090,
                     5: 1.075, 6: 1.119, 7: 1.066, 8: 1.089},
}

# Which side of the body the ball sits on, +1 = viewer's right. Measured from
# the art: the generator put the monkey's dribbling hand on the viewer's LEFT
# for the standing poses, not the right the prompt asked for.
BALL_SIDE = {
    # Running left, the ball is ahead of him on the LEFT. Standing, the subtle
    # face-on dribble (2026-09-25) bounces it on the viewer's left too, like the
    # monkey, so it stays in the same hand when he stops after a left run.
    # Everything else is the default, the viewer's right.
    "zombie": {"dribble_idle": -1, "run_dribble_l": -1},
    "monkey": {
        "dribble_idle": -1, "break_banana": -1, "break_wave": -1,
        "pickup": -1, "panic": -1, "run_dribble_r": +1, "run_dribble_l": -1,
    },
}

# Which frame of a dribble loop has the hand at its HIGHEST, 1-based as in the
# frame files (03.png = 3). The game centres that frame on the ball's apex, the
# moment the ball meets the hand. A sequence not listed keeps the game's older
# convention (frame 1 drawn from the apex onward), which the placeholder art was
# drawn for.
APEX_FRAME = {
    "zombie": {"dribble_idle": 3,      # LOWEST, RISING, HIGHEST, DRIVING DOWN
               "run_dribble_r": 2,     # contact, PASSING, contact, passing
               "run_dribble_l": 2},
}

# How many bounces of the ball one loop of a sequence covers. Default 1. The
# running dribble is a full stride -- two steps, each with its own bounce, and
# the hand pushes once per step -- so its four frames span two bounces. A
# runner bounces the ball as each foot lands.
LOOP_BOUNCES = {
    "zombie": {"run_dribble_r": 2, "run_dribble_l": 2},
}

# Sequences anchored on the cell rather than on the feet: either the feet
# travel on purpose (running), or they are not on the floor to anchor to at all
# (the handspring goes up on its hands and through the air). Everywhere else the
# feet are planted and anchor directly, which stops the character sliding
# sideways mid-loop.
TRAVELLING = {"run_r", "run_l", "run_dribble_r", "run_dribble_l", "celebrate_flip"}

# ... and of those, the ones anchored on the BODY rather than on the middle of
# the source cell. A run is drawn in place: the feet swing, the torso does not,
# so the torso is what the frames must be registered on. Anchoring on the cell
# assumes the generator centred the figure in it, and it does not: the zombie's
# run_dribble_r torso wandered 24 units (a fifth of his height) across the four
# frames, which in the game is the character lurching sideways as he runs, with
# the ball left hanging away from his hand. The handspring keeps the cell: it
# leaves the floor and turns over, so it has no steady torso to anchor on.
BODY_ANCHORED = {"run_r", "run_l", "run_dribble_r", "run_dribble_l"}


def torso_centre(m: np.ndarray, box) -> float:
    """The middle of the upper body: the band between 15% and 55% of the
    figure's height, which holds the chest and hips and excludes the swinging
    arms' full reach and the legs."""
    y0, y1 = box[1], box[3]
    band = m[y0 + int(0.15 * (y1 - y0)):y0 + int(0.55 * (y1 - y0)), :]
    xs = np.where(band.any(axis=0))[0]
    return float((xs.min() + xs.max()) / 2) if len(xs) else (box[0] + box[2]) / 2


def mask_of(im: Image.Image) -> np.ndarray:
    return np.array(im.getchannel("A")) > ALPHA_CUT


def bbox(m: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


# The point on the floor the character stands on -- the middle of the stance,
# read off a band at the bottom of the silhouette.
#
# The band has to be deep enough to hold BOTH shoes. Most stances put one foot a
# little lower than the other, and a shallow band then sees only that shoe and
# anchors the whole character on it. At a thirtieth of the figure's height the
# High Schooler's standing pose anchored at 91% of his own width and the NBA
# player's charge at 18%, which drew both of them most of a body-width away from
# where the game thought they were standing. A tenth clears every shoe in the
# current art, and the measurement stops moving well before that depth -- from a
# tenth to a sixth it does not change at all -- so it is not a knife edge.
FOOT_BAND = 10


def foot_centre(m: np.ndarray, box) -> float:
    y1 = box[3]
    band = m[max(0, y1 - max(4, (y1 - box[1]) // FOOT_BAND)):y1, :]
    xs = np.where(band.any(axis=0))[0]
    return float((xs.min() + xs.max()) / 2) if len(xs) else (box[0] + box[2]) / 2


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

    # Base scale, from the standing dribble's first animation frame. Only used
    # for sequences with no calibration frame of their own; the SEQ_SCALE
    # figures are measured against this, so it must skip any 00.png.
    ref_dir = src / "dribble_idle"
    ref_file = ref_dir / "01.png"
    if not ref_file.exists():
        ref_file = sorted(ref_dir.glob("*.png"))[0]
    ref = Image.open(ref_file).convert("RGBA")
    rx0, ry0, rx1, ry1 = bbox(mask_of(ref))
    target_h = STANDING_H * CHAR_SCALE.get(key, 1.0)
    scale = target_h / (ry1 - ry0)

    seq_scale = SEQ_SCALE.get(key, {})
    sequences = {}
    auto = []
    stand_h = None
    for d in seq_dirs:
        files = sorted(d.glob("*.png"))
        if not files:
            continue

        # A leading 00.png is a calibration frame: the same standing pose drawn
        # at the start of every strip. Measuring it scales the sequence exactly,
        # instead of relying on a hand-measured SEQ_SCALE entry.
        calib = None
        if files[0].name == "00.png":
            calib, files = files[0], files[1:]
        if not files:
            continue

        if calib is not None:
            ch = bbox(mask_of(Image.open(calib).convert("RGBA")))
            s = target_h / (ch[3] - ch[1])
            auto.append(d.name)
            # The calibration pose IS the standing height. The game otherwise
            # takes it from the first dribble frame, which on a strip that opens
            # on a crouch is too short and sizes the ball's bounce too low.
            if d.name == "dribble_idle":
                stand_h = round(target_h, 2)
        else:
            s = scale * seq_scale.get(d.name, 1.0)

        ims = [Image.open(f).convert("RGBA") for f in files]
        masks = [mask_of(im) for im in ims]
        boxes = [bbox(m) for m in masks]

        ground = max(b[3] for b in boxes)
        cell_cx = ims[0].width / 2
        travelling = d.name in TRAVELLING

        # In a mixed build the old poses were written here first; clear them so
        # a shorter strip cannot leave an old frame behind.
        shutil.rmtree(OUT / key / d.name, ignore_errors=True)
        frames = []
        for i, (im, m, box) in enumerate(zip(ims, masks, boxes), start=1):
            # A travelling pose cannot anchor on its feet, because they are
            # mid-stride and move on purpose: a run anchors on the torso, and
            # what is left (the handspring) on the cell. A planted pose anchors
            # on its own feet, so the character cannot drift through the loop.
            ax = (torso_centre(m, box) if d.name in BODY_ANCHORED
                  else cell_cx) if travelling else foot_centre(m, box)
            dest = OUT / key / d.name / f"{i:02d}.png"
            w, h = write_frame(im, box, s, dest)
            frames.append({
                "src": f"sprites/{key}/{d.name}/{i:02d}.png",
                "w": w, "h": h,
                "footX": round((ax - box[0]) * s, 2),
                "footY": round((ground - box[1]) * s, 2),
            })
        sequences[d.name] = frames

    if auto:
        print(f"{key:<14} auto-scaled from calibration frames: {', '.join(auto)}")
    char = {"key": key, "label": label, "mirror": False, "sequences": sequences,
            "ballSide": BALL_SIDE.get(key, {})}
    apex = {n: k - 1 for n, k in APEX_FRAME.get(key, {}).items() if n in sequences}
    if apex:
        char["apexFrame"] = apex                  # 0-based in the manifest
    bounces = {n: b for n, b in LOOP_BOUNCES.get(key, {}).items() if n in sequences}
    if bounces:
        char["loopBounces"] = bounces
    if stand_h is not None:
        char["standH"] = stand_h
    return char


# ---------------------------------------------------------------- old style
def build_from_poses(key: str, stem: str, label: str) -> dict | None:
    src = SRC / f"{stem} poses"
    files = sorted(p for p in src.glob("*.png") if LEGACY_NAME.search(p.name))
    if len(files) < 8:
        return None
    ims = [Image.open(f).convert("RGBA") for f in files]
    masks = [mask_of(im) for im in ims]
    boxes = [bbox(m) for m in masks]

    idle = boxes[LEGACY_IDLE_POSE - 1]
    scale = STANDING_H * CHAR_SCALE.get(key, 1.0) / (idle[3] - idle[1])
    pose_scale = POSE_SCALE.get(key, {})

    def frame_for(pose: int, seq: str, idx: int) -> dict:
        im, m, box = ims[pose - 1], masks[pose - 1], boxes[pose - 1]
        s = scale * pose_scale.get(pose, 1.0)
        dest = OUT / key / seq / f"{idx:02d}.png"
        w, h = write_frame(im, box, s, dest)
        return {
            "src": f"sprites/{key}/{seq}/{idx:02d}.png",
            "w": w, "h": h,
            "footX": round((foot_centre(m, box) - box[0]) * s, 2),
            "footY": round((box[3] - box[1]) * s, 2),
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


def build_mixed(key: str, stem: str, label: str) -> dict | None:
    """Old poses as the base, sliced sequences on top.

    The old art is drawn facing one way and flipped to turn round; a sliced
    sequence is drawn for the facing it is used in and must never be flipped
    (the jersey number would read backwards). So the character stays `mirror`,
    and the sliced sequences are listed in `fixed`, which the game checks per
    sequence.
    """
    base = build_from_poses(key, stem, label)
    strips = build_from_sequences(key, stem, label)   # writes after, so it wins
    if not base or not strips:
        return base or strips
    base["sequences"].update(strips["sequences"])
    base["fixed"] = sorted(strips["sequences"])
    base["ballSide"] = strips["ballSide"]
    for k in ("apexFrame", "loopBounces", "standH"):
        if k in strips:
            base[k] = strips[k]
    return base


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
        if key in MIXED:
            char = build_mixed(key, stem, label)
        else:
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
        kind = ("mixed" if c.get("fixed") else "poses") if c["mirror"] else "strips"
        print(f"{c['key']:<14} {len(c['sequences']):>2} sequences, {n:>2} frames "
              f"({kind})  hand ({c['handX']:+.0f},{c['handY']:+.0f})")
    pngs = list(OUT.rglob("*.png"))
    print(f"\n{len(pngs)} frames, {sum(f.stat().st_size for f in pngs)/1024:.0f} KB total")


if __name__ == "__main__":
    main()
