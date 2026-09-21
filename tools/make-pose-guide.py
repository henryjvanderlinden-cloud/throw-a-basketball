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

WHAT A GUIDE DRAWS LIVES IN THE MANIFEST, not here. A sequence in
art/sequences.yml (or a character's own sequence in art/characters.yml) carries

    guide:
      file: art/guides/<seq>.png
      side: right                   # the edge the dribbling hand is on
      frames:                       # calibration first, one entry per cell
        - {pose: calibration}
        - {drop: 0.150, tilt: 0.035, lean: 0.045, hand: 0.26, ...}

and this tool turns that table into the picture. The field reference is
FRAME_FIELDS below; the body's own proportions stay constants in this file
until a second character needs its own (handover 03 §9(B)).

  py tools\\make-pose-guide.py --seq dribble_idle
  py tools\\make-pose-guide.py --seq dribble_idle --overlay build\\guide-check\\approved.preview
  py tools\\make-pose-guide.py --seq break_face --char zombie

The overlay is the cheap validation §4 asks for: if the skeleton does not sit on
the character we already have, it will not help the generator either. It writes
overlay.png beside the guide -- run it before spending a roll.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"

# ---------------------------------------------------------------- the canvas
CELL_W, CELL_H = 420, 520
STANDING = 400                      # standing height in pixels
GROUND_Y = CELL_H - 46              # the shared ground line

LINE = 3                            # one uniform line weight, everywhere
JOINT_R = 5
INK = (0, 0, 0)
PAPER = (255, 255, 255)

# ------------------------------------------------------------- the skeleton
# The body's proportions, in fractions of standing height. Measured off the
# zombie's dribble_idle.approved.png. These describe WHO is drawn, not the pose,
# which is why they are not in the manifest -- see handover 03 §9(B) for when a
# character will need his own.
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

FREE_HAND = (-0.032, -0.365)        # a hanging hand, as an offset from its shoulder

# Hands, drawn like the footprints: ONE drawing, moved -- never redrawn. That is
# the playbook's "constancy is an operation" made literal in the guide.
PALM_LEN, PALM_W = 0.055, 0.046     # the palm, as a flat paddle off the wrist
FINGER = 0.046                      # palm + finger ~ a tenth of his height
FINGER_FAN = (-8, 4, 16, 28)        # dribbling fingers: flat, fanning slightly down
FIST = 0.052                        # a closed fist: a rounded square this wide

# Hair: five strands rooted on the upper half of the head circle.
HAIR_ROOTS = (-64, -32, 0, 32, 64)  # degrees either side of the crown
HAIR_REST, HAIR_UP, HAIR_FLAT = 0.030, 0.055, 0.040

GAME_APEX = 0.52                    # index.html, via handover 02 §0(C)
GAME_LATERAL = 0.26

# A projected limb can only get SHORTER than its true length (foreshortening);
# a frame that makes one longer than in the calibration pose by more than this
# share has stretched the body, and is reported.
STRETCH_WARN = 0.05


# ------------------------------------------------------------- the manifest

# Every field a frame may carry, with its default. `pose: calibration` swaps in
# CALIBRATION's values instead, so the calibration cell is one short line.
#
#   drop    how far the whole upper body sinks, 1 - (head top / standing).
#           Measured per frame off a reference take where one exists.
#   tilt    how far the dribbling-side hip and shoulder drop below level.
#   lean    how far the chest sits out over the dribbling hip, from the middle
#           of the hips. The spine is roughly perpendicular to the shoulder
#           line, so a tilt without a lean is inconsistent.
#   turn    degrees the body is turned away from the camera, for a
#           three-quarter view: hips and shoulders narrow by cos(turn), which
#           is what a turned body looks like projected onto the picture plane.
#   stance  how far each ankle sits out from the centre line.
#   hand    the dribbling hand. A number is its height, with the palm's middle
#           on the ball's own line (GAME_LATERAL); [x, y] places the wrist
#           anywhere (x out from the centre line, toward the dribbling side);
#           null lets it hang.
#   hand_shape  flat | hang | fist. Defaults to flat when `hand` is given.
#   free    the other hand: null hangs it; [x, y] places its wrist (x toward
#           the dribbling side, like `hand`).
#   free_shape  flat | hang | fist. Defaults to hang.
#   palm    extra downward tilt of a flat palm, in degrees.
#   head    head tilt in degrees, the ear dropping toward the dribbling
#           shoulder. The head itself rides on top of the spine.
#   hair    up (standing off the scalp -- the body dropped out from under
#           them) | flat (lying toward the ears -- the body just rose) | rest.
#   joints  per-joint overrides, {name: [x, y]}, x toward the dribbling side.
#           Ankles, hips and wrists are placed BEFORE the knees and elbows are
#           worked out, so overriding a foot moves its knee with it; knees,
#           elbows and the rest are replaced afterwards. Names are those of
#           JOINT_NAMES. Use them for what the fields above cannot say -- a
#           stride, a swinging arm -- and keep the rest parametric, because
#           parametric is what keeps limb lengths and footprints constant.
FRAME_FIELDS = dict(
    name="", drop=0.0, tilt=0.0, lean=0.0, turn=0.0, stance=STANCE_POSE,
    hand=None, hand_shape=None, free=None, free_shape="hang", palm=0.0,
    head=0.0, hair="rest", joints=None,
)
CALIBRATION = dict(name="calibration", stance=STANCE_CALIB)

JOINT_NAMES = ("hip_d", "hip_f", "sh_d", "sh_f", "knee_d", "knee_f",
               "elb_d", "elb_f", "hand_d", "hand_f", "ank_d", "ank_f",
               "pelvis", "chest", "head")
PLACED_FIRST = {"ank_d", "ank_f", "hip_d", "hip_f", "hand_d", "hand_f"}


def load_sequence(seq: str, char: str | None) -> dict:
    """The sequence's manifest entry: a character's own first, then shared."""
    shared = yaml.safe_load((ART / "sequences.yml").read_text(encoding="utf-8"))
    chars = yaml.safe_load((ART / "characters.yml").read_text(encoding="utf-8"))
    chars = chars.get("characters", chars) if isinstance(chars, dict) else {}
    places = []
    if char:
        own = (chars.get(char) or {}).get("sequences") or {}
        places.append((f"characters.yml / {char}", own))
    places.append(("sequences.yml", shared.get("sequences") or {}))
    if not char:
        for key, c in chars.items():
            if isinstance(c, dict):
                places.append((f"characters.yml / {key}", c.get("sequences") or {}))
    for where, seqs in places:
        if seq in seqs:
            return seqs[seq] | {"_where": where}
    sys.exit(f"no sequence called {seq!r} in the manifest")


def guide_spec(entry: dict, seq: str) -> dict:
    g = entry.get("guide")
    if not isinstance(g, dict) or not g.get("frames"):
        sys.exit(f"{seq}: its `guide:` has no frame table "
                 f"(in {entry['_where']}) -- see FRAME_FIELDS in this tool")
    n = int(entry.get("frames", 0)) + 1
    if len(g["frames"]) != n:
        sys.exit(f"{seq}: the guide has {len(g['frames'])} cells, but the "
                 f"sequence is {n} (calibration + {n - 1})")
    return g


def frames(spec: dict) -> list[dict]:
    """The manifest's frame table with every default filled in."""
    out = []
    for i, raw in enumerate(spec["frames"]):
        raw = dict(raw or {})
        base = dict(FRAME_FIELDS)
        if raw.pop("pose", None) == "calibration":
            base.update(CALIBRATION)
        unknown = set(raw) - set(FRAME_FIELDS)
        if unknown:
            sys.exit(f"cell {i}: unknown field(s) {', '.join(sorted(unknown))}")
        base.update(raw)
        if not base["name"]:
            base["name"] = f"cell{i}"
        if base["hand_shape"] is None:
            base["hand_shape"] = "hang" if base["hand"] is None else "flat"
        for k in (base["joints"] or {}):
            if k not in JOINT_NAMES:
                sys.exit(f"cell {i}: no joint called {k!r}")
        out.append(base)
    return out


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
    over = {k: (dribble * v[0], v[1]) for k, v in (f["joints"] or {}).items()}
    narrow = math.cos(math.radians(f["turn"]))
    hip_x, sh_x = HIP_X * narrow, SH_X * narrow

    hip_d = over.get("hip_d", (dribble * hip_x, PELVIS_Y - drop - tilt))
    hip_f = over.get("hip_f", (-dribble * hip_x, PELVIS_Y - drop + tilt))
    pelvis = ((hip_d[0] + hip_f[0]) / 2, (hip_d[1] + hip_f[1]) / 2)

    # The spine leans from the pelvis: the chest slides out over the dribbling
    # hip, the shoulders hang off the chest, and the head continues the same
    # line, so everything above the belt tilts as one piece.
    lean = dribble * f["lean"]
    torso = SH_Y - PELVIS_Y
    chest = (pelvis[0] + lean, SH_Y - drop)
    sh_d = (chest[0] + dribble * sh_x, chest[1] - tilt)
    sh_f = (chest[0] - dribble * sh_x, chest[1] + tilt)
    head_c = (chest[0] + lean * HEAD_UP / torso, chest[1] + HEAD_UP)

    ank_d = over.get("ank_d", (dribble * f["stance"], ANKLE_Y))
    ank_f = over.get("ank_f", (-dribble * f["stance"], ANKLE_Y))

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

    # The dribbling hand. The joint is the WRIST; a flat palm reaches outward
    # from it, so for a height alone the wrist sits half a palm inboard and the
    # palm's middle lands on the ball's own line, GAME_LATERAL.
    hand = f["hand"]
    if "hand_d" in over:
        hand_d = over["hand_d"]
    elif hand is None:
        hand_d = (sh_d[0] - dribble * FREE_HAND[0], sh_d[1] + FREE_HAND[1])
    elif isinstance(hand, (list, tuple)):
        hand_d = (dribble * hand[0], hand[1])
    else:
        hand_d = (dribble * (GAME_LATERAL - PALM_LEN / 2), hand)
    joints["hand_d"] = hand_d
    joints["elb_d"] = middle(sh_d, hand_d, ELBOW_ALONG, dribble * ELBOW_OUT)

    free = f["free"]
    if "hand_f" in over:
        hand_f = over["hand_f"]
    elif free is None:
        # hanging: the mirror image of the dribbling side's hang
        hand_f = (sh_f[0] + dribble * FREE_HAND[0], sh_f[1] + FREE_HAND[1])
    else:
        hand_f = (dribble * free[0], free[1])
    joints["hand_f"] = hand_f
    joints["elb_f"] = middle(sh_f, hand_f, ELBOW_ALONG, -dribble * ELBOW_OUT)

    for k, v in over.items():                 # knees, elbows, anything else
        if k not in PLACED_FIRST:
            joints[k] = v
    return joints


LIMBS = {
    "thigh (dribbling side)": ("hip_d", "knee_d"), "shin (dribbling side)": ("knee_d", "ank_d"),
    "thigh (free side)": ("hip_f", "knee_f"), "shin (free side)": ("knee_f", "ank_f"),
    "upper arm (dribbling)": ("sh_d", "elb_d"), "forearm (dribbling)": ("elb_d", "hand_d"),
    "upper arm (free)": ("sh_f", "elb_f"), "forearm (free)": ("elb_f", "hand_f"),
}


def stretch_report(cells: list[dict], side: int) -> list[str]:
    """Limbs LONGER than in the calibration pose, in any cell.

    Checked everywhere, not only where `joints` overrides something: a plain
    `hand` height can be out of reach too. Reaching the knee needs the crouch
    to come with it -- dribble_idle's LOWEST (hand 0.26, drop 0.150) has its
    arm at 96% of standing length, and the same hand with a shallow crouch is
    an arm a third too long."""
    ref = skeleton(dict(FRAME_FIELDS, **CALIBRATION, hand_shape="hang"), side)
    true = {n: math.dist(ref[a], ref[b]) for n, (a, b) in LIMBS.items()}
    warn = []
    for f in cells:
        j = skeleton(f, side)
        for n, (a, b) in LIMBS.items():
            got = math.dist(j[a], j[b])
            if got > true[n] * (1 + STRETCH_WARN):
                warn.append(f"{f['name']}: {n} is {got / true[n] - 1:+.0%} "
                            f"longer than standing -- a projected limb can only "
                            f"shorten")
    return warn


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


def draw_flat_hand(d, wrist, dribble: int, palm_deg: float, ink) -> None:
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


def draw_fist(d, wrist, elbow, ink) -> None:
    """A closed fist: a rounded square continuing the forearm past the wrist,
    with one line across it for the knuckles."""
    s = FIST * STANDING
    ux, uy = wrist[0] - elbow[0], wrist[1] - elbow[1]
    n = math.hypot(ux, uy) or 1.0
    cx, cy = wrist[0] + ux / n * s / 2, wrist[1] + uy / n * s / 2
    d.rounded_rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                        radius=s * 0.3, outline=ink, width=LINE)
    kx, ky = -uy / n * s * 0.35, ux / n * s * 0.35
    fx, fy = cx + ux / n * s * 0.15, cy + uy / n * s * 0.15
    d.line([(fx - kx, fy - ky), (fx + kx, fy + ky)], fill=ink, width=LINE)


def draw_hand(d, shape: str, wrist, elbow, dribble: int, palm: float, ink) -> None:
    if shape == "flat":
        draw_flat_hand(d, wrist, dribble, palm, ink)
    elif shape == "fist":
        draw_fist(d, wrist, elbow, ink)
    elif shape == "hang":
        draw_hanging_hand(d, wrist, ink)
    else:
        sys.exit(f"unknown hand shape {shape!r} (flat | hang | fist)")


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
        elif mode == "rest":
            # at rest: short spikes straight out from the scalp
            L = HAIR_REST * S
            d.line([(rx, ry), (rx + math.sin(a) * L, ry - math.cos(a) * L)],
                   fill=ink, width=LINE)
        else:
            sys.exit(f"unknown hair mode {mode!r} (up | flat | rest)")


def draw_cell(d: ImageDraw.ImageDraw, cx: float, f: dict, side: int,
              ink=INK) -> None:
    j = skeleton(f, side)
    P = lambda k: to_px(cx, j[k])

    # the two footprints, one drawing in every cell -- the shoe rests on the
    # ground under its ankle; a raised ankle (a stride) lifts it with the foot
    for k in ("ank_d", "ank_f"):
        ax, _ = to_px(cx, (j[k][0], 0.0))
        lift = max(0.0, j[k][1] - ANKLE_Y) * STANDING
        w, h = SHOE_W * STANDING, SHOE_H * STANDING
        d.rounded_rectangle([ax - w / 2, GROUND_Y - h - lift, ax + w / 2,
                             GROUND_Y - lift],
                            radius=h * 0.45, outline=ink, width=LINE)
        d.line([P(k), (ax, GROUND_Y - h * 0.5 - lift)], fill=ink, width=LINE)

    for a, b in BONES:
        d.line([P(a), P(b)], fill=ink, width=LINE)

    # the head: a circle, and inside it the crown-to-chin axis and the eye line
    # rotated together. The tilt is the whole point -- the head does not travel,
    # so the circle stays over the chest and only this axis turns.
    hx, hy = P("head")
    r = HEAD_R * STANDING
    d.ellipse([hx - r, hy - r, hx + r, hy + r], outline=ink, width=LINE)
    draw_hair(d, hx, hy, r, f["head"] * side, f["hair"], ink)

    draw_hand(d, f["hand_shape"], P("hand_d"), P("elb_d"), side, f["palm"], ink)
    draw_hand(d, f["free_shape"], P("hand_f"), P("elb_f"), -side, f["palm"], ink)

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


def build(cells: list[dict], side: int) -> Image.Image:
    im = Image.new("RGB", (CELL_W * len(cells), CELL_H), PAPER)
    d = ImageDraw.Draw(im)
    d.line([(0, GROUND_Y), (im.width, GROUND_Y)], fill=INK, width=LINE)
    for i, f in enumerate(cells):
        draw_cell(d, i * CELL_W + CELL_W / 2, f, side)
    return im


# --------------------------------------------------------------- the overlay

def overlay(preview: Path, cells: list[dict], side: int, out: Path) -> None:
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

    sheet = Image.new("RGB", (CELL_W * len(cells), CELL_H), PAPER)
    names = ["calib"] + [f"f{i}" for i in range(len(cells) - 1)]
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


def describe_hand(v) -> str:
    if v is None:
        return "hanging"
    if isinstance(v, (list, tuple)):
        return f"({v[0]:+.2f},{v[1]:.2f})"
    return f"{v * 100:.0f}%"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", default="dribble_idle")
    ap.add_argument("--char", default=None,
                    help="look in this character's own sequences first")
    ap.add_argument("--left", action="store_true",
                    help="draw the mirror image, dribbling hand toward the "
                         "viewer's LEFT (written as <file>-left.png)")
    ap.add_argument("--overlay", type=Path, default=None,
                    help="a measure-strip.py preview directory to check against")
    a = ap.parse_args()

    entry = load_sequence(a.seq, a.char)
    spec = guide_spec(entry, a.seq)
    cells = frames(spec)
    side = {"right": +1, "left": -1}[str(spec.get("side", "right"))]
    if a.left:
        side = -side

    out = ROOT / spec.get("file", f"art/guides/{a.seq}.png")
    if a.left:
        out = out.with_name(out.stem + "-left" + out.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    build(cells, side).save(out)
    print(f"{out.relative_to(ROOT).as_posix()}  {CELL_W * len(cells)}x{CELL_H}, "
          f"standing height {STANDING}px  (from {entry['_where']})")
    for f in cells:
        extra = f"  joints {','.join(f['joints'])}" if f["joints"] else ""
        print(f"  {f['name']:<12} drop {f['drop']*100:4.1f}%  "
              f"tilt {f['tilt']*100:4.1f}%  lean {f['lean']*100:4.1f}%  "
              f"hand {describe_hand(f['hand']):>13}  head {f['head']:.0f}deg"
              + (f"  turn {f['turn']:.0f}deg" if f["turn"] else "") + extra)
    for w in stretch_report(cells, side):
        print(f"  ! {w}")

    if a.overlay:
        overlay(a.overlay, cells, side, a.overlay / "overlay.png")


if __name__ == "__main__":
    main()
