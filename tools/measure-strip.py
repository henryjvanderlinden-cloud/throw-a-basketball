#!/usr/bin/env python3
"""Measure a generated sprite strip, and preview it as an animation.

Four instruments. The first two are the ones from handovers/HANDOVER_01.md
§0(E); the other two check the clauses the prompt now states as geometry,
against index.html's own constants rather than against taste.

  inter-frame difference  XOR of consecutive silhouettes, registered on ink
                          centroid and ground line, normalised by union.
                          Catches "all four frames read as the same pose".
                          Below ~15% is a failed sheet.
  mirror asymmetry        XOR of each frame against its own horizontal flip
                          about its ink centroid. Catches "both arms are doing
                          the same thing". The calibration frame is the built-in
                          control: it should score ~8%, and if it does not, the
                          instrument is measuring the rendering, not the pose.
  hand apex / lateral     index.html puts the ball's apex where the hand rests
                          on its upper quarter -- GAME_APEX of standing height --
                          and the ball GAME_LATERAL out from the centre line. A
                          sheet whose hand does not reach that height, or that
                          draws the arm across the jersey, cannot meet the ball.
  head lean               head centre against the midpoint of the foot span,
                          signed positive toward the dribbling side. The trunk
                          side-bends toward the dribbling hand, so the head
                          belongs on that side in every pose frame.

Heights are fractions of the character's own standing height, taken from the
calibration frame, which is what makes them comparable between sheets and
between characters.

  py tools\\measure-strip.py "artwork\\basketball-players\\Zombie poses\\dribble_idle.r1.png"

A hand height of "--" means the arm was drawn touching the torso, so there was
no separate run of ink to measure -- which is the piston clause failing rather
than a missing measurement.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ALPHA_CUT = 128
SNAP_WINDOW = 0.12          # search +/- this share of a cell width for the cut
BLEED_MAX_SHARE = 0.15

STANDING_H = 132            # matches tools/build-sprites.py
SUPERSAMPLE = 2
OUT_H = STANDING_H * SUPERSAMPLE

# index.html: dribT advances by dt*7 standing and dt*9 running; one bounce is PI.
STATIONARY_HZ = 7 / np.pi * 4
RUNNING_HZ = 9 / np.pi * 4

# index.html: peak = bodyH * DRIBBLE_HAND_H - 0.5 * BALL_R with the hand on the
# ball's upper quarter, and b.x = p.px + bodyH * 0.26 * ballSide.
GAME_APEX = 0.52
GAME_LATERAL = 0.26

ARM_MIN = 0.18              # further out than this from the centre line: an arm
LEG_ZONE = 0.22             # lower than this above the floor: a shin or a shoe
TORSO_LO, TORSO_HI = 0.30, 0.62


# --------------------------------------------------------------- cutting
# The rule is slice-strips.py's: equal divisions nudged to the emptiest nearby
# column, then blobs leaning on an internal cut are erased as a neighbour's tail.

def ink_columns(im: Image.Image) -> np.ndarray:
    return (np.array(im.getchannel("A")) > ALPHA_CUT).sum(axis=0)


def cut_points(im: Image.Image, n: int) -> list[int]:
    occ = ink_columns(im)
    w = im.width
    cell = w / n
    cuts = [0]
    for i in range(1, n):
        centre = round(i * cell)
        span = max(2, round(cell * SNAP_WINDOW))
        lo, hi = max(1, centre - span), min(w - 1, centre + span)
        window = occ[lo:hi]
        cuts.append(lo + int(window.argmin()) if len(window) else centre)
    cuts.append(w)
    return cuts


def flood_from(mask, seeds, budget):
    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    stack = [s for s in seeds if mask[s[0], s[1]]]
    for y, x in stack:
        seen[y, x] = True
    filled = 0
    while stack:
        y, x = stack.pop()
        filled += 1
        if filled > budget:
            return None
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return seen


def drop_bleed(cell: Image.Image, touch_left: bool, touch_right: bool) -> None:
    if not (touch_left or touch_right):
        return
    arr = np.array(cell)
    mask = arr[:, :, 3] > ALPHA_CUT
    total = int(mask.sum())
    if not total:
        return
    budget = int(total * BLEED_MAX_SHARE)
    hit = False
    for edge, active in ((0, touch_left), (mask.shape[1] - 1, touch_right)):
        if not active:
            continue
        seeds = [(y, edge) for y in np.where(mask[:, edge])[0]]
        if not seeds:
            continue
        blob = flood_from(mask, seeds, budget)
        if blob is None:                  # ran into the character; leave it be
            continue
        arr[:, :, 3][blob] = 0
        mask &= ~blob
        hit = True
    if hit:
        cell.paste(Image.fromarray(arr), (0, 0))


def cut(path: Path, cells: int) -> list[Image.Image]:
    im = Image.open(path).convert("RGBA")
    cuts = cut_points(im, cells)
    out = []
    for i in range(cells):
        c = im.crop((cuts[i], 0, cuts[i + 1], im.height))
        drop_bleed(c, i > 0, i < cells - 1)
        out.append(c)
    return out


# ------------------------------------------------------ silhouette helpers

def silhouette(im: Image.Image) -> np.ndarray:
    return np.array(im.getchannel("A")) > ALPHA_CUT


def anchors(mask: np.ndarray):
    ys, xs = np.nonzero(mask)
    return float(xs.mean()), int(ys.max())          # ink centroid x, ground line


def foot_anchor(mask: np.ndarray):
    """Midpoint of the foot span, which is where a planted-feet loop registers.

    The ink centroid wanders sideways with a swinging arm, so a loop registered
    on it shuffles along the floor.
    """
    ys, _ = np.nonzero(mask)
    g = int(ys.max())
    band = mask[g - max(2, int(mask.shape[0] * 0.05)):g + 1]
    xs = np.nonzero(band.any(axis=0))[0]
    return float((xs.min() + xs.max()) / 2), g


def runs(row: np.ndarray) -> list[tuple[int, int]]:
    idx = np.nonzero(row)[0]
    if not len(idx):
        return []
    breaks = np.nonzero(np.diff(idx) > 1)[0]
    starts = np.concatenate(([0], breaks + 1))
    ends = np.concatenate((breaks, [len(idx) - 1]))
    return [(int(idx[s]), int(idx[e])) for s, e in zip(starts, ends)]


# ------------------------------------------------- the first two instruments

def place(mask: np.ndarray, cx: float, ground: int, shape) -> np.ndarray:
    H, W = shape
    out = np.zeros((H, W), dtype=bool)
    dx = int(round(W / 2 - cx))
    dy = int(round(H - 8 - ground))
    ys, xs = np.nonzero(mask)
    ys, xs = ys + dy, xs + dx
    keep = (ys >= 0) & (ys < H) & (xs >= 0) & (xs < W)
    out[ys[keep], xs[keep]] = True
    return out


def xor_share(a: np.ndarray, b: np.ndarray) -> float:
    union = (a | b).sum()
    return float((a ^ b).sum() / union) if union else 0.0


def asymmetry(m: np.ndarray) -> float:
    cx, ground = anchors(m)
    one = place(m, cx, ground, (m.shape[0], int(m.shape[1] * 1.6)))
    return xor_share(one, one[:, ::-1])


def measure(frames: list[Image.Image]) -> dict:
    masks = [silhouette(f) for f in frames]
    poses = masks[1:]
    H = max(m.shape[0] for m in poses)
    W = int(max(m.shape[1] for m in poses) * 1.6)
    reg = [place(m, *anchors(m), (H, W)) for m in poses]

    inter = [xor_share(reg[i], reg[(i + 1) % len(reg)]) for i in range(len(reg))]
    asym = [asymmetry(m) for m in poses]
    return {
        "inter_frame": inter,
        "inter_frame_mean": float(np.mean(inter)),
        "asymmetry": asym,
        "asymmetry_mean": float(np.mean(asym)),
        "calibration_asymmetry": asymmetry(masks[0]),
    }


# ------------------------------------------------ the per-frame geometry

def frame_checks(m: np.ndarray, standing: float, side: int) -> dict:
    """side: +1 when the dribbling hand is toward the viewer's right."""
    cx, ground = foot_anchor(m)
    limit = cx + side * ARM_MIN * standing
    floor_cut = ground - int(LEG_ZONE * standing)
    lo, hi = ground - int(TORSO_HI * standing), ground - int(TORSO_LO * standing)

    hand_row, lat, detached, torso_rows = None, [], 0, 0
    for y in range(int(m.shape[0] * 0.02), ground + 1):
        rr = runs(m[y])
        if lo <= y <= hi:
            torso_rows += 1
            if len(rr) >= 2:
                detached += 1
        if len(rr) < 2 or y > floor_cut:
            continue
        outer = [r for r in rr if (r[0] > limit if side > 0 else r[1] < limit)]
        if outer:
            r = max(outer, key=lambda r: r[1]) if side > 0 else min(outer)
            hand_row = y if hand_row is None else max(hand_row, y)
            lat.append((r[0] + r[1]) / 2)

    ys, _ = np.nonzero(m)
    top, bot = int(ys.min()), int(ys.max())
    head = m[top:top + int((bot - top + 1) * 0.20)]
    hxs = np.nonzero(head.any(axis=0))[0]

    # Stance width: the span of ink in the shoe band. A figure that crouches by
    # splaying its feet instead of bending its knees shows up here as a stance
    # that widens in the low frames and narrows in the high ones.
    band = m[ground - max(2, int(standing * 0.04)):ground + 1]
    bxs = np.nonzero(band.any(axis=0))[0]
    stance = (bxs.max() - bxs.min() + 1) / standing if len(bxs) else None

    return {
        "hand_height": (ground - hand_row) / standing if hand_row is not None else None,
        "hand_lateral": abs(float(np.mean(lat)) - cx) / standing if lat else None,
        "arm_separation": detached / torso_rows if torso_rows else 0.0,
        "head_lean": side * ((hxs.min() + hxs.max()) / 2 - cx) / (bot - top + 1),
        "stance": stance,
    }


# ------------------------------------------------------------- the preview

def registered(frames: list[Image.Image]):
    """Scale by the calibration frame, then pin the feet to one spot."""
    rows = np.nonzero(silhouette(frames[0]).any(axis=1))[0]
    scale = (OUT_H * 0.94) / (rows.max() - rows.min() + 1)
    H, W = OUT_H, int(OUT_H * 1.25)
    out = []
    for f in frames:
        w, h = f.size
        s = f.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                     Image.LANCZOS)
        cx, ground = foot_anchor(silhouette(s))
        canv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canv.alpha_composite(s, (int(round(W / 2 - cx)), int(round(H - 6 - ground))))
        out.append(canv)
    return out


def write_sheet(reg, per: dict, out: Path, labels: list[str]) -> None:
    """The four poses in a row, each with its measured hand height ruled across
    it -- the contact sheet a human judges, beside the loop a human watches."""
    from PIL import ImageDraw
    poses = reg[1:]
    w, h = poses[0].size
    sheet = Image.new("RGBA", (w * len(poses), h + 34), (255, 255, 255, 255))
    d = ImageDraw.Draw(sheet)
    ground = h - 6
    for i, im in enumerate(poses):
        sheet.alpha_composite(im, (i * w, 34))
        c = per.get(f"f{i}", {})
        hh = c.get("hand_height")
        d.text((i * w + 10, 8), labels[i] if i < len(labels) else f"frame {i}",
               fill=(60, 60, 65))
        if hh:
            d.text((i * w + 10, 20),
                   f"hand at {hh*100:.1f}% of standing height", fill=(150, 90, 90))
            y = 34 + ground - int(hh * OUT_H * 0.94)
            d.line([(i * w + 6, y), (i * w + w - 6, y)], fill=(228, 150, 150))
        d.line([(i * w, 0), (i * w, h + 34)], fill=(225, 225, 230))
    sheet.convert("RGB").save(out / "sheet.png")


def write_preview(reg, out: Path, hz: float) -> int:
    reg[0].save(out / "calib.png")
    for i, f in enumerate(reg[1:]):
        f.save(out / f"f{i}.png")
    ms = int(round(1000 / hz))
    flat = []
    for f in reg[1:]:
        bg = Image.new("RGBA", f.size, (250, 250, 250, 255))
        bg.alpha_composite(f)
        flat.append(bg.convert("P", palette=Image.ADAPTIVE, colors=255))
    flat[0].save(out / "loop.gif", save_all=True, append_images=flat[1:],
                 duration=ms, loop=0, disposal=2)
    return ms


# -------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("strip", type=Path)
    ap.add_argument("--cells", type=int, default=5,
                    help="cells on the strip, calibration frame included")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--left", action="store_true",
                    help="the dribbling hand is toward the viewer's LEFT")
    ap.add_argument("--running", action="store_true",
                    help="preview at the running cadence instead of standing")
    ap.add_argument("--labels", default=None,
                    help="pipe-separated frame names for the sheet, e.g. "
                         "\"LOWEST|RISING|HIGHEST|DRIVING DOWN\"")
    a = ap.parse_args()

    out = a.out or a.strip.parent / f"{a.strip.stem}.preview"
    out.mkdir(parents=True, exist_ok=True)
    side = -1 if a.left else +1

    frames = cut(a.strip, a.cells)
    m = measure(frames)
    reg = registered(frames)
    ms = write_preview(reg, out, RUNNING_HZ if a.running else STATIONARY_HZ)

    standing = float(np.diff(np.nonzero(
        silhouette(reg[0]).any(axis=1))[0][[0, -1]])[0] + 1)
    per = {}
    for name, f in zip(["calib", "f0", "f1", "f2", "f3"], reg):
        per[name] = frame_checks(silhouette(f), standing, side)

    print(f"\n{a.strip.name}   loop at {ms}ms/frame -> {out / 'loop.gif'}")
    print(f"  mean inter-frame difference : {m['inter_frame_mean']*100:5.1f}%   "
          f"({', '.join(f'{v*100:.0f}%' for v in m['inter_frame'])})")
    print(f"  mean pose asymmetry         : {m['asymmetry_mean']*100:5.1f}%   "
          f"({', '.join(f'{v*100:.0f}%' for v in m['asymmetry'])})")
    print(f"  calibration asymmetry (ctrl): {m['calibration_asymmetry']*100:5.1f}%"
          "   -- should be ~8%, or the instrument is measuring the rendering")

    print(f"\n  dribbling side: viewer's {'left' if side < 0 else 'right'}")
    print("  frame      hand height   lateral   arm gap   head lean   stance")
    fmt = lambda v: f"{v*100:6.1f}%" if v is not None else "    -- "
    apex = 0.0
    for name, c in per.items():
        if name != "calib" and c["hand_height"]:
            apex = max(apex, c["hand_height"])
        print(f"  {name:<9}  {fmt(c['hand_height'])}       {fmt(c['hand_lateral'])}  "
              f"{fmt(c['arm_separation'])}  {fmt(c['head_lean'])}  {fmt(c['stance'])}")
    st = [c["stance"] for n, c in per.items() if n != "calib" and c["stance"]]
    if st:
        print(f"  stance spread across the pose frames: "
              f"{(max(st)-min(st))*100:.1f}% of standing height "
              f"({min(st)*100:.1f}–{max(st)*100:.1f}%) -- flat is the target, "
              f"the feet are meant to be one drawing")
    write_sheet(reg, per, out, a.labels.split("|") if a.labels else
                ["LOWEST", "RISING", "HIGHEST", "DRIVING DOWN"])
    print(f"  hand apex {apex*100:.1f}% against the game's {GAME_APEX*100:.0f}%, "
          f"lateral against {GAME_LATERAL*100:.0f}%")
    print(f"  sheet -> {out / 'sheet.png'}")
    lean = [c["head_lean"] for n, c in per.items() if n != "calib"]
    wrong = [f"{n}" for n, c in per.items()
             if n != "calib" and c["head_lean"] < 0]
    print(f"  head on the dribbling side in {4 - len(wrong)}/4 pose frames"
          + (f" -- wrong side in {', '.join(wrong)}" if wrong else ""))

    m["per_frame"] = per
    m["source"] = a.strip.name
    (out / "measure.json").write_text(json.dumps(m, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
