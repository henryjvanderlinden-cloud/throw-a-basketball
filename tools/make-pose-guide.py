#!/usr/bin/env python3
"""Draw the wireframe POSE GUIDE for a sequence, and check it against the art.

handovers/HANDOVER_02.md §4. Every failure the dribble prompt chased -- which
knee bends, the four hand heights and their order, the stance widening, the head
travelling instead of tilting -- is geometry, and eight rolls went into
conveying geometry in sentences. A pose guide does not describe the geometry, it
IS the geometry. It also makes constancy true by construction: one skeleton,
transformed per frame, shares its limb lengths and its footprints exactly.

Everything is a fraction of STANDING HEIGHT, the character's height in the
calibration pose, which is the unit measure-strip.py already reports in. So one
guide serves every character: the manifest's `scale` changes how tall he is
drawn, not where his knee sits in his own body.

The numbers are not taste. GAME_APEX and GAME_LATERAL come from index.html
(§0(C)); the crouch depths, the stance and the hip offsets were measured off
dribble_idle.approved.png with tools/measure-strip.py.

  py tools\\make-pose-guide.py --seq dribble_idle
  py tools\\make-pose-guide.py --seq dribble_idle --overlay build\\guide-check\\approved.preview

The overlay is the cheap validation §4 asks for: if the skeleton does not sit on
the character we already have, it will not help the generator either. It writes
overlay.png beside the guide -- run it before spending a roll.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "art" / "guides"

# ---------------------------------------------------------------- the canvas
CELL_W, CELL_H = 420, 520
STANDING = 400                      # standing height in pixels
GROUND_Y = CELL_H - 46              # the shared ground line

LINE = 3                            # one uniform line weight, everywhere
JOINT_R = 5
INK = (0, 0, 0)
PAPER = (255, 255, 255)

# ------------------------------------------------------------- the skeleton
# Fractions of standing height. Measured off dribble_idle.approved.png unless
# marked otherwise.
HIP_X = 0.090
PELVIS_Y = 0.480                    # hip joint; the waistband sits at 0.52
SH_X = 0.130
SH_Y = 0.790
HEAD_R = 0.075
HEAD_UP = 0.110                     # head centre above the shoulder line

ANKLE_Y = 0.090
SHOE_W, SHOE_H = 0.137, 0.075
STANCE_POSE = 0.213                 # ankle out from the centre line, dribbling
STANCE_CALIB = 0.1835               # ... and standing, "shoulder-width apart"

FREE_HAND = (-0.032, -0.365)        # free hand, as an offset from its shoulder

# Hands, drawn like the footprints: ONE drawing, moved -- never redrawn. That is
# the playbook's "constancy is an operation" made literal in the guide.
PALM_LEN, PALM_W = 0.055, 0.046     # the palm, as a flat paddle off the wrist
FINGER = 0.046                      # palm + finger ~ a tenth of his height
FINGER_FAN = (-8, 4, 16, 28)        # dribbling fingers: flat, fanning slightly down

# Hair: five strands rooted on the upper half of the head circle.
HAIR_ROOTS = (-64, -32, 0, 32, 64)  # degrees either side of the crown
HAIR_REST, HAIR_UP, HAIR_FLAT = 0.030, 0.055, 0.040

GAME_APEX = 0.52                    # index.html, via §0(C)
GAME_LATERAL = 0.26


def frames(side: int) -> list[dict]:
    """The five cells, left to right. `side` is +1 for a hand on the right edge.

    drop      how far the whole upper body sinks, 1 - (head top / standing).
              0.150 / 0.093 / 0.016 / 0.101 on the approved take -- note that
              DRIVING DOWN is already deeper than RISING, which is the body
              leading the hand.
    tilt      how far the dribbling-side hip and shoulder drop below level.
    hand      the dribbling palm's height. The ladder is knee, hem, WAISTBAND,
              just below the hem -- and the waistband is GAME_APEX, where
              index.html actually puts the ball.
    head      head tilt in degrees, the ear dropping toward the dribbling
              shoulder. The head itself rides on top of the spine.
    lean      how far the chest sits out over the dribbling hip, measured from
              the midpoint of the hips. Rick, 2026-09-21: the spine tilts toward
              the dribbling hand on the downstroke and is straight at the top.
              A tilted shoulder line over a vertical spine was also plain
              inconsistent -- the spine is roughly perpendicular to it -- so
              this is the shoulder tilt's own consequence, kept smaller than
              the full perpendicular because he asked for "a little".
    hair      where the five strands on the head point: "up" (standing off the
              scalp -- the body has dropped out from under them), "flat" (lying
              down toward the ears -- the body has just risen), or "rest". Two
              prose wordings of this failed; the guide draws it instead.
    palm      extra downward tilt of the dribbling palm in degrees. Only the
              LOWEST frame has any -- "at the end of the push".
    """
    return [
        dict(name="calibration", drop=0.0, tilt=0.0, hand=None, head=0.0,
             lean=0.0, stance=STANCE_CALIB, hair="rest", palm=0.0),
        dict(name="lowest", drop=0.150, tilt=0.035, hand=0.26, head=9.0,
             lean=0.045, stance=STANCE_POSE, hair="up", palm=18.0),
        dict(name="rising", drop=0.093, tilt=0.018, hand=0.38, head=5.0,
             lean=0.020, stance=STANCE_POSE, hair="rest", palm=0.0),
        dict(name="highest", drop=0.016, tilt=0.000, hand=GAME_APEX, head=0.0,
             lean=0.000, stance=STANCE_POSE, hair="flat", palm=0.0),
        # The hand TRAILS here: the body has already dropped, the hand is still
        # above the hem. At 0.33 this frame was drawn almost like LOWEST and
        # every guided roll gave a dead seam (6-12%) between the two.
        dict(name="driving", drop=0.101, tilt=0.018, hand=0.42, head=5.0,
             lean=0.035, stance=STANCE_POSE, hair="rest", palm=0.0),
    ]


# --------------------------------------------------------------- geometry
# World coordinates: x out from the centre line, y up from the ground, both in
# fractions of standing height. to_px is the only place the canvas exists.

def to_px(cx: float, p: tuple[float, float]) -> tuple[float, float]:
    return cx + p[0] * STANDING, GROUND_Y - p[1] * STANDING


def middle(a: tuple[float, float], b: tuple[float, float],
           along: float, out: float) -> tuple[float, float]:
    """The middle joint of a limb, seen from the FRONT.

    Two-link IK in the picture plane is the wrong model here and it shows: it
    bends the limb sideways, so a crouch splays the knees out past the shoes and
    a dribbling elbow swings out level with the shoulder. A knee and an elbow
    both bend in the SAGITTAL plane -- toward the camera -- and from the front
    that is not a sideways bend at all, it is FORESHORTENING. So the joint stays
    on the line between its neighbours, at a fixed share of the way along, and
    `out` is the small lateral bulge that is actually visible.
    """
    return (a[0] + (b[0] - a[0]) * along + out,
            a[1] + (b[1] - a[1]) * along)


KNEE_ALONG = 0.513                  # knee at 0.28 with the hip at 0.48
KNEE_RIDE = 0.060                   # a squatting knee sinks less than its hip
KNEE_OUT = 0.030                    # its outward bulge at full crouch
# WHICH KNEE BENDS was the defect that survived three rewrites of the clause,
# so the guide states it as geometry: at full crouch the loaded knee sits lower
# and further out than the far one, which stays straighter and carries less.
KNEE_LOAD, KNEE_FREE = 0.035, -0.020
BULGE_LOAD, BULGE_FREE = 1.8, 0.3
ELBOW_ALONG = 0.480
ELBOW_OUT = 0.020                   # keeps the forearm clear of the jersey


def skeleton(f: dict, side: int) -> dict:
    """Every joint of one cell, in world coordinates."""
    drop, tilt = f["drop"], f["tilt"]
    dribble = side                            # +1: the hand nearer the right edge

    hip_d = (dribble * HIP_X, PELVIS_Y - drop - tilt)     # the loaded hip, dropped
    hip_f = (-dribble * HIP_X, PELVIS_Y - drop + tilt)
    pelvis = ((hip_d[0] + hip_f[0]) / 2, (hip_d[1] + hip_f[1]) / 2)

    # The spine leans from the pelvis: the chest slides out over the dribbling
    # hip, the shoulders hang off the chest, and the head continues the same
    # line, so everything above the belt tilts as one piece.
    lean = dribble * f.get("lean", 0.0)
    torso = SH_Y - PELVIS_Y
    chest = (pelvis[0] + lean, SH_Y - drop)
    sh_d = (chest[0] + dribble * SH_X, chest[1] - tilt)
    sh_f = (chest[0] - dribble * SH_X, chest[1] + tilt)
    head_c = (chest[0] + lean * HEAD_UP / torso, chest[1] + HEAD_UP)

    ank_d = (dribble * f["stance"], ANKLE_Y)
    ank_f = (-dribble * f["stance"], ANKLE_Y)

    # The deeper the crouch, the more the knee shows outside the thigh line.
    load = min(1.0, drop / 0.150)
    bulge = KNEE_OUT * load
    base = KNEE_ALONG - KNEE_RIDE * load
    joints = dict(
        hip_d=hip_d, hip_f=hip_f, sh_d=sh_d, sh_f=sh_f,
        ank_d=ank_d, ank_f=ank_f, pelvis=pelvis, chest=chest, head=head_c,
        knee_d=middle(hip_d, ank_d, base + KNEE_LOAD * load,
                      dribble * bulge * BULGE_LOAD),
        knee_f=middle(hip_f, ank_f, base + KNEE_FREE * load,
                      -dribble * bulge * BULGE_FREE),
    )

    if f["hand"] is None:                     # calibration: both arms hang
        for tag, sgn in (("d", dribble), ("f", -dribble)):
            sh = joints[f"sh_{tag}"]
            hand = (sh[0] - sgn * FREE_HAND[0], sh[1] + FREE_HAND[1])
            joints[f"hand_{tag}"] = hand
            joints[f"elb_{tag}"] = middle(sh, hand, ELBOW_ALONG,
                                          sgn * ELBOW_OUT)
    else:
        # The joint is the WRIST; the drawn palm reaches outward from it, so the
        # wrist sits half a palm inboard and the palm's middle lands on the
        # ball's own line, GAME_LATERAL.
        hand_d = (dribble * (GAME_LATERAL - PALM_LEN / 2), f["hand"])
        joints["hand_d"] = hand_d
        joints["elb_d"] = middle(sh_d, hand_d, ELBOW_ALONG,
                                 dribble * ELBOW_OUT)
        hand_f = (sh_f[0] + dribble * FREE_HAND[0], sh_f[1] + FREE_HAND[1])
        joints["hand_f"] = hand_f
        joints["elb_f"] = middle(sh_f, hand_f, ELBOW_ALONG,
                                 -dribble * ELBOW_OUT)
    return joints


# ---------------------------------------------------------------- drawing

BONES = [
    ("hip_d", "hip_f"), ("sh_d", "sh_f"), ("pelvis", "chest"),
    ("hip_d", "knee_d"), ("knee_d", "ank_d"),
    ("hip_f", "knee_f"), ("knee_f", "ank_f"),
    ("sh_d", "elb_d"), ("elb_d", "hand_d"),
    ("sh_f", "elb_f"), ("elb_f", "hand_f"),
]


def _paddle(d, x, y, ux, uy, length, width, ink):
    """A flat rectangle running `length` from (x, y) along the unit (ux, uy)."""
    nx, ny = -uy * width / 2, ux * width / 2
    ex, ey = x + ux * length, y + uy * length
    d.polygon([(x + nx, y + ny), (ex + nx, ey + ny),
               (ex - nx, ey - ny), (x - nx, y - ny)], outline=ink, width=LINE)
    return ex, ey, nx, ny


def draw_dribble_hand(d, wrist, dribble: int, palm_deg: float, ink) -> None:
    """Flat and open, palm to the floor: a horizontal paddle reaching outward
    from the wrist, four fingers fanning out from its end. Pixel coords, y down."""
    S = STANDING
    a = math.radians(palm_deg)
    ux, uy = dribble * math.cos(a), math.sin(a)
    ex, ey, nx, ny = _paddle(d, *wrist, ux, uy, PALM_LEN * S, PALM_W * S, ink)
    for i, fan in enumerate(FINGER_FAN):
        t = (i / (len(FINGER_FAN) - 1) - 0.5) * 1.6       # spread across the end
        sx, sy = ex + nx * t, ey + ny * t
        b = math.radians(palm_deg + fan)
        d.line([(sx, sy), (sx + dribble * math.cos(b) * FINGER * S,
                           sy + math.sin(b) * FINGER * S)], fill=ink, width=LINE)


def draw_hanging_hand(d, wrist, ink) -> None:
    """Hanging, palm turned in to the thigh, fingers pointing at the floor --
    seen edge-on from the front, so a narrow paddle with the fingers below it."""
    S = STANDING
    ex, ey, nx, ny = _paddle(d, *wrist, 0.0, 1.0, PALM_LEN * 0.9 * S,
                             PALM_W * S, ink)
    for t in (-0.75, -0.25, 0.25, 0.75):
        sx = ex + nx * t
        d.line([(sx, ey), (sx + t * 2, ey + FINGER * S)], fill=ink, width=LINE)


def draw_hair(d, hx, hy, r, crown_deg: float, mode: str, ink) -> None:
    """Five strands from the upper head. `crown_deg` is the head tilt, so the
    roots ride the head; the strand DIRECTION is what the frame is about."""
    S = STANDING
    for k, root in enumerate(HAIR_ROOTS):
        a = math.radians(crown_deg + root)                # 0 = straight up
        rx, ry = hx + math.sin(a) * r, hy - math.cos(a) * r
        if mode == "up":
            # standing straight up off the scalp, the whole bunch pointing at
            # the ceiling with only a slight fan
            b = math.radians(root * 0.22)
            L = HAIR_UP * S
            d.line([(rx, ry), (rx + math.sin(b) * L, ry - math.cos(b) * L)],
                   fill=ink, width=LINE)
        elif mode == "flat":
            # lying against the scalp, combed down the sides toward the ears:
            # a short arc just outside the circle, running away from the crown
            sgn = 1 if root > 0 else -1          # the middle strand goes left
            # separate short arcs, clear of the head outline and of each other
            pts = []
            R = r + 7
            for s in range(5):
                c = math.radians(crown_deg + root + sgn * s * 6.0)
                pts.append((hx + math.sin(c) * R, hy - math.cos(c) * R))
            d.line(pts, fill=ink, width=LINE)
        else:
            # at rest: short spikes straight out from the scalp
            L = HAIR_REST * S
            d.line([(rx, ry), (rx + math.sin(a) * L, ry - math.cos(a) * L)],
                   fill=ink, width=LINE)


def draw_cell(d: ImageDraw.ImageDraw, cx: float, f: dict, side: int,
              ink=INK) -> None:
    j = skeleton(f, side)
    P = lambda k: to_px(cx, j[k])

    # the two footprints, one drawing in every cell
    for k in ("ank_d", "ank_f"):
        ax, ay = to_px(cx, (j[k][0], 0.0))
        w, h = SHOE_W * STANDING, SHOE_H * STANDING
        d.rounded_rectangle([ax - w / 2, GROUND_Y - h, ax + w / 2, GROUND_Y],
                            radius=h * 0.45, outline=ink, width=LINE)
        d.line([P(k), (ax, GROUND_Y - h * 0.5)], fill=ink, width=LINE)

    for a, b in BONES:
        d.line([P(a), P(b)], fill=ink, width=LINE)

    # the head: a circle, and inside it the crown-to-chin axis and the eye line
    # rotated together. The tilt is the whole point -- the head does not travel,
    # so the circle stays over the chest and only this axis turns.
    hx, hy = P("head")
    r = HEAD_R * STANDING
    d.ellipse([hx - r, hy - r, hx + r, hy + r], outline=ink, width=LINE)
    draw_hair(d, hx, hy, r, f["head"] * side, f.get("hair", "rest"), ink)

    if f["hand"] is None:
        draw_hanging_hand(d, P("hand_d"), ink)
    else:
        draw_dribble_hand(d, P("hand_d"), side, f.get("palm", 0.0), ink)
    draw_hanging_hand(d, P("hand_f"), ink)

    th = math.radians(f["head"] * side)
    ax, ay = math.sin(th), -math.cos(th)                  # crown direction
    d.line([(hx - ax * r, hy - ay * r), (hx + ax * r, hy + ay * r)],
           fill=ink, width=LINE)
    ex, ey = math.cos(th), math.sin(th)                   # the eye line
    d.line([(hx - ex * r * 0.66, hy - ey * r * 0.66 + r * 0.30),
            (hx + ex * r * 0.66, hy + ey * r * 0.66 + r * 0.30)],
           fill=ink, width=LINE)
    d.line([P("chest"), (hx - ax * r, hy - ay * r)], fill=ink, width=LINE)

    for k in ("hip_d", "hip_f", "sh_d", "sh_f", "knee_d", "knee_f",
              "elb_d", "elb_f", "hand_d", "hand_f", "ank_d", "ank_f"):
        x, y = P(k)
        d.ellipse([x - JOINT_R, y - JOINT_R, x + JOINT_R, y + JOINT_R],
                  fill=ink)


def build(side: int) -> Image.Image:
    cells = frames(side)
    im = Image.new("RGB", (CELL_W * len(cells), CELL_H), PAPER)
    d = ImageDraw.Draw(im)
    d.line([(0, GROUND_Y), (im.width, GROUND_Y)], fill=INK, width=LINE)
    for i, f in enumerate(cells):
        draw_cell(d, i * CELL_W + CELL_W / 2, f, side)
    return im


# --------------------------------------------------------------- the overlay

def overlay(preview: Path, side: int, out: Path) -> None:
    """Draw the skeleton over measure-strip.py's registered frames.

    Those frames are scaled by the calibration frame and pinned by the foot
    span, so the skeleton's own unit -- standing height above the ground line --
    lands on them directly.
    """
    import numpy as np

    calib = Image.open(preview / "calib.png").convert("RGBA")
    a = np.array(calib.getchannel("A")) > 128
    rows = np.nonzero(a.any(axis=1))[0]
    standing = float(rows.max() - rows.min() + 1)
    ground = float(rows.max())

    global STANDING, GROUND_Y, CELL_W, CELL_H
    STANDING, GROUND_Y = standing, ground
    CELL_W, CELL_H = calib.width, calib.height

    cells = frames(side)
    sheet = Image.new("RGB", (CELL_W * len(cells), CELL_H), PAPER)
    names = ["calib", "f0", "f1", "f2", "f3"]
    for i, (f, n) in enumerate(zip(cells, names)):
        art = Image.open(preview / f"{n}.png").convert("RGBA")
        tile = Image.new("RGBA", (CELL_W, CELL_H), PAPER + (255,))
        tile.alpha_composite(art)
        d = ImageDraw.Draw(tile)
        d.line([(0, GROUND_Y), (CELL_W, GROUND_Y)], fill=(220, 60, 60), width=1)
        draw_cell(d, CELL_W / 2, f, side, ink=(220, 40, 40))
        sheet.paste(tile.convert("RGB"), (i * CELL_W, 0))
    sheet.save(out)
    print(f"overlay -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", default="dribble_idle")
    ap.add_argument("--left", action="store_true",
                    help="the dribbling hand is toward the viewer's LEFT")
    ap.add_argument("--overlay", type=Path, default=None,
                    help="a measure-strip.py preview directory to check against")
    a = ap.parse_args()
    side = -1 if a.left else +1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{a.seq}{'-left' if a.left else ''}.png"
    build(side).save(out)
    print(f"{out.relative_to(ROOT)}  {CELL_W * 5}x{CELL_H}, "
          f"standing height {STANDING}px")
    for f in frames(side):
        h = f"{f['hand']*100:.0f}%" if f["hand"] else "hanging"
        print(f"  {f['name']:<12} drop {f['drop']*100:4.1f}%  "
              f"tilt {f['tilt']*100:4.1f}%  lean {f['lean']*100:4.1f}%  "
              f"hand {h:>8}  head {f['head']:.0f}deg")

    if a.overlay:
        overlay(a.overlay, side, a.overlay / "overlay.png")


if __name__ == "__main__":
    main()
