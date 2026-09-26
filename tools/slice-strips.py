#!/usr/bin/env python3
"""Cut generated sprite strips into individual frames.

Reads   artwork/basketball-players/<Character> poses/<strip>.png
Writes  artwork/basketball-players/<Character> frames/<sequence>/01.png ...

Each strip is one animation sequence laid out as a single horizontal row. The
generator is asked for equal-width, evenly spaced cells, so the cuts start at
equal divisions of the image width -- but a tail or a swinging arm often crosses
into the neighbouring cell, so each internal cut is then nudged to the nearby
column carrying the least ink. Looking for empty columns instead does not work:
on several strips the figures touch, and whole frames get merged.

Frames are written at full resolution with alpha intact. Scaling, trimming and
anchoring stay in build-sprites.py.

Run from anywhere:  python tools/slice-strips.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "artwork" / "basketball-players"

ALPHA_CUT = 128
SNAP_WINDOW = 0.12          # search +/- this share of a cell width for the cut

# character -> [(sequence name, strip file, frame count[, calibration])]
# Numbers match the prompts in docs/prompts-monkey.md.
#
# A fourth element of True means the strip carries a leading CALIBRATION FRAME:
# the character's plain standing pose, drawn identically at the start of every
# strip in the set. It is written as 00.png and left out of the animation;
# build-sprites.py measures it to scale the sequence automatically, which is
# what removes the hand-measured SEQ_SCALE entry. See docs/ANIMATION.md.
STRIPS = {
    "Monkey": [
        ("dribble_idle",    "Monkey_sequence_001.png", 4),
        # 002b/003b keep the hand low and open in all four frames; 002/003
        # alternate it with a running fist, which breaks the dribble.
        ("run_dribble_r",   "Monkey_sequence_002b.png", 4),
        ("run_dribble_l",   "Monkey_sequence_003b.png", 4),
        ("pickup",          "Monkey_sequence_004.png", 3),
        ("turn",            "Monkey_sequence_005.png", 2),
        ("aim",             "Monkey_sequence_006.png", 2),
        ("charge",          "Monkey_sequence_007.png", 3),
        ("shot",            "Monkey_sequence_008.png", 4),
        ("run_r",           "Monkey_sequence_009.png", 2),
        ("run_l",           "Monkey_sequence_010.png", 2),
        ("celebrate",       "Monkey_sequence_011.png", 2),
        # 012b is far more doubled-over, so the heave between the two frames
        # reads at game size where 012's barely did.
        ("gameover",        "Monkey_sequence_012b.png", 2),
        ("break_banana",    "Monkey_sequence_013.png", 4),
        ("break_wave",      "Monkey_sequence_014.png", 4),
        ("panic",           "Monkey_sequence_015.png", 4),
        ("celebrate_pump",  "Monkey_sequence_016.png", 3),
        ("celebrate_flip",  "Monkey_sequence_017.png", 6),
    ],
    # The zombie is mid-migration: sequences listed here replace their
    # counterparts from the eight old poses, which still supply the rest (see
    # build-sprites.py). Each is the approved take of the guided pipeline.
    "Zombie": [
        # Subtle and face-on, dribbling on the viewer's LEFT as the monkey does
        # (BALL_SIDE in build-sprites.py): r3 of the subtle batch, 2026-09-25,
        # picked by Rick, all four frames. It replaces take32 (handover 03).
        ("dribble_idle",    "dribble_idle.approved.png", 4, True),
        ("run_dribble_r",   "run_dribble_r.approved.png", 4, True),
        ("run_dribble_l",   "run_dribble_l.approved.png", 4, True),
        # No `idle` any more (Rick, 2026-09-26): the ball-less defensive loop
        # (idle.approved.png, set left / set right) read as "too desperate,
        # with the arm wailing". Without the ball he now holds his dribble's
        # highest-hand frame, still, exactly as the monkey does.
        # Running without the ball: four frames, a full stride. Batch 2 of the
        # guided pipeline, 2026-09-25 -- r3 running right, r1 running left,
        # picked by Rick.
        ("run_r",           "run_r.approved.png", 4, True),
        ("run_l",           "run_l.approved.png", 4, True),
        # Face-on, two-handed: reach, scoop between the feet, gathered in front
        # of the waist. r1 of the first batch, 2026-09-25, picked by Rick; the
        # game puts the ball in his hands frame by frame (PICKUP_BALL).
        ("pickup",          "pickup.approved.png", 3, True),
        # The shooting chain, matched to the monkey's frames like for like
        # (Rick, 2026-09-25). Batch 1, picked by Rick: turn r1, aim r1,
        # charge r2, shot r1. The shot's first frame (the coil) is sliced but
        # never shown; the game plays the last three.
        ("turn",            "turn.approved.png", 2, True),
        ("aim",             "aim.approved.png", 2, True),
        ("charge",          "charge.approved.png", 3, True),
        ("shot",            "shot.approved.png", 4, True),
        # The celebrations and the buzzer, matched to the monkey's frames like
        # for like (handover 10). Picked by Rick, 2026-09-26: celebrate r3,
        # celebrate_pump r1, gameover r1 ("looks more tired, and the heave of
        # r2 is too much").
        ("celebrate",       "celebrate.approved.png", 2, True),
        ("celebrate_pump",  "celebrate_pump.approved.png", 3, True),
        ("gameover",        "gameover.approved.png", 2, True),
        # Group B, the zombie's own (handover 10), picked by Rick 2026-09-26.
        # break_face: r3, the most comical, recoloured onto dribble_idle's
        # palette by tools/recolour-take.py (its kit and skin had drifted).
        # break_head: r2 ("returns to a natural stance"). panic: r1 ("the most
        # cartoon-like eye bulging"). The three are STORIES (STORY_SEQ).
        ("break_face",      "break_face.approved.png", 4, True),
        ("break_head",      "break_head.approved.png", 4, True),
        ("panic",           "panic.approved.png", 4, True),
        # celebrate_collapse: r1, "more ecstatic", WITHOUT its frame 3, the
        # heap of body parts on the floor (Rick: "I'd definitely not use
        # [it]"). That frame touched frame 4, so the slicer could not lift it
        # out; the approved strip is r1 with the heap erased by hand
        # (celebrate_collapse.r1noheap.png), leaving five frames: triumph,
        # flying apart, reassembling, nearly whole, whole.
        ("celebrate_collapse", "celebrate_collapse.approved.png", 5, True),
        # Group C (handover 10), picked by Rick 2026-09-26: steal_r r3,
        # steal_l r1, stolen r1 -- the last played 1, 3, 2: "it looks left and
        # right to see what happened, and then clenches fist in frustration",
        # then hands over to the ball-less still pose.
        ("steal_r",         "steal_r.approved.png", 3, True),
        ("steal_l",         "steal_l.approved.png", 3, True),
        ("stolen",          "stolen.approved.png", 3, True, [1, 3, 2]),
    ],
}


BLEED_MAX_SHARE = 0.15      # a stray blob is at most this share of the figure

# Sequences that deliberately leave the floor, so the ground-line check would
# only produce a misleading warning.
AIRBORNE = {"celebrate_flip", "celebrate_collapse"}


def ink_columns(im: Image.Image) -> np.ndarray:
    return (np.array(im.getchannel("A")) > ALPHA_CUT).sum(axis=0)


def flood_from(mask: np.ndarray, seeds, budget: int):
    """4-connected flood from `seeds`, abandoned once it exceeds `budget`.

    Returns the filled pixels, or None if the blob turned out to be big -- which
    means we walked into the character rather than a stray fragment. Bailing out
    early is what keeps this cheap: a real fragment is a few thousand pixels, and
    the main body is abandoned almost immediately.
    """
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


def drop_bleed(cell: Image.Image, touch_left: bool, touch_right: bool) -> int:
    """Erase small blobs that lean on an internal cut -- a neighbour's tail.

    Seeded only from the cut edges, so genuinely detached parts of the pose that
    sit inside the frame (the thrown banana peel, for instance) are never
    considered.
    """
    if not (touch_left or touch_right):
        return 0
    arr = np.array(cell)
    mask = arr[:, :, 3] > ALPHA_CUT
    total = int(mask.sum())
    if not total:
        return 0
    budget = int(total * BLEED_MAX_SHARE)

    removed = 0
    for edge, active in ((0, touch_left), (mask.shape[1] - 1, touch_right)):
        if not active:
            continue
        seeds = [(y, edge) for y in np.where(mask[:, edge])[0]]
        if not seeds:
            continue
        blob = flood_from(mask, seeds, budget)
        if blob is None:          # ran into the character; leave it be
            continue
        arr[:, :, 3][blob] = 0
        mask &= ~blob
        removed += 1
    if removed:
        cell.paste(Image.fromarray(arr), (0, 0))
    return removed


def components(mask: np.ndarray):
    """Connected blobs of ink: (labels, blobs), blobs left to right.

    `labels` is an int array, 0 for background and a blob's id elsewhere, so a
    figure can be lifted out by its own pixels rather than by a rectangle. Row
    runs plus union-find: a row holds a handful of runs, so this is fast and
    needs nothing beyond numpy.
    """
    parent: dict[int, int] = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    runs: list[tuple[int, int]] = []
    rows: list[list[int]] = []
    prev: list[int] = []
    for row in mask:
        xs = np.where(row)[0]
        cur = []
        if len(xs):
            breaks = np.where(np.diff(xs) > 1)[0]
            starts = np.concatenate(([0], breaks + 1))
            ends = np.concatenate((breaks, [len(xs) - 1]))
            for i, j in zip(starts, ends):
                rid = len(runs)
                runs.append((int(xs[i]), int(xs[j])))
                parent[rid] = rid
                for q in prev:
                    if runs[q][0] <= runs[rid][1] + 1 and runs[rid][0] <= runs[q][1] + 1:
                        union(q, rid)
                cur.append(rid)
        rows.append(cur)
        prev = cur

    ids: dict[int, int] = {}
    labels = np.zeros(mask.shape, dtype=np.int32)
    blobs: dict[int, list[int]] = {}
    for y, cur in enumerate(rows):
        for rid in cur:
            lab = ids.setdefault(find(rid), len(ids) + 1)
            x0, x1 = runs[rid]
            labels[y, x0:x1 + 1] = lab
            b = blobs.setdefault(lab, [x0, x1, 0])
            b[0] = min(b[0], x0)
            b[1] = max(b[1], x1)
            b[2] += x1 - x0 + 1
    return labels, sorted((b[0], b[1], b[2], lab) for lab, b in blobs.items())


def group_components(blobs, n: int, w: int):
    """Put every blob into one of n cells, by its distance to a moving centre.

    A cell is a FIGURE, not a slice of equal width. Running left, the trailing
    shoe reaches past the halfway line and still belongs to the runner it came
    off; cut by column it lands in the next frame, which is what the zombie's
    run_dribble_l did. Centres start at the equal divisions and are re-estimated
    -- a 1-D k-means with a sensible seed.

    Cells may OVERLAP in x, which is the point: no vertical cut can separate
    figures whose boxes overlap, but masking by component can. Returns the blobs
    of each cell, or None when this does not look like n figures, in which case
    the caller falls back on cutting by column.
    """
    if len(blobs) < n:
        return None
    centres = [(i + 0.5) * w / n for i in range(n)]
    groups: list[list] = []
    for _ in range(12):
        groups = [[] for _ in range(n)]
        for b in blobs:
            mid = (b[0] + b[1]) / 2
            groups[min(range(n), key=lambda k: abs(mid - centres[k]))].append(b)
        if any(not g for g in groups):
            return None
        new = [sum(((x0 + x1) / 2) * px for x0, x1, px, _ in g)
               / sum(px for _, _, px, _ in g) for g in groups]
        done = all(abs(u - v) < 0.5 for u, v in zip(new, centres))
        centres = new
        if done:
            break
    # every cell must hold a real figure rather than a stray fragment
    big = [max(b[2] for b in g) for g in groups]
    if min(big) < max(big) * 0.25:
        return None
    return groups


def cut_points(im: Image.Image, n: int) -> list[int]:
    """Equal divisions, each nudged to the emptiest nearby column."""
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


def slice_character(name: str, seqs) -> None:
    src_dir = SRC / f"{name} poses"
    out_root = SRC / f"{name} frames"
    print(f"== {name}")
    for entry in seqs:
        seq, filename, n = entry[0], entry[1], entry[2]
        calib = len(entry) > 3 and entry[3]
        # A fifth element keeps only those animation frames (1-based, calibration
        # not counted), renumbered 01, 02, ... in that order.
        pick = list(entry[4]) if len(entry) > 4 else None
        path = src_dir / filename
        if not path.exists():
            print(f"  {seq:<16} MISSING {filename}")
            continue
        im = Image.open(path).convert("RGBA")
        cells = n + 1 if calib else n
        mask = np.array(im.getchannel("A")) > ALPHA_CUT
        labels, blobs = components(mask)
        groups = group_components(blobs, cells, im.width)
        cuts = None if groups else cut_points(im, cells)

        out_dir = out_root / seq
        out_dir.mkdir(parents=True, exist_ok=True)
        for old in out_dir.glob("*.png"):
            old.unlink()                       # a re-roll may have fewer frames
        heights, feet, cleaned = [], [], 0
        for i in range(cells):
            if groups:
                # lift this figure out by its own pixels, so a shoe reaching
                # into the next cell's space travels with the leg it is on
                keep = np.isin(labels, [b[3] for b in groups[i]])
                arr = np.array(im)
                arr[:, :, 3] = np.where(keep, arr[:, :, 3], 0)
                x0 = max(0, min(b[0] for b in groups[i]) - 4)
                x1 = min(im.width, max(b[1] for b in groups[i]) + 5)
                cell = Image.fromarray(arr).crop((x0, 0, x1, im.height))
            else:
                cell = im.crop((cuts[i], 0, cuts[i + 1], im.height))
            m = np.array(cell.getchannel("A")) > ALPHA_CUT
            if not m.any():
                print(f"  {seq:<16} frame {i+1} is EMPTY -- wrong frame count?")
                continue
            # Ink on an *internal* cut means a neighbour bled in; the outer
            # edges are just the image border cropping the figure.
            if not groups:      # by figure, nothing bleeds in to remove
                cleaned += drop_bleed(cell, touch_left=i > 0,
                                      touch_right=i < cells - 1)
            k = i if calib else i + 1          # 1-based animation frame; 0 = calib
            if pick is not None and k and k not in pick:
                continue
            m = np.array(cell.getchannel("A")) > ALPHA_CUT
            ys, xs = np.where(m)
            # The calibration frame is 00 and is not part of the animation, so
            # it does not count towards the ground-line check either.
            if not (calib and i == 0):
                heights.append(int(ys.max() - ys.min()))
                feet.append(int(ys.max()))
            if pick is not None and k:
                k = pick.index(k) + 1
            cell.save(out_dir / f"{k:02d}.png")

        flags = []
        if seq not in AIRBORNE and max(feet) - min(feet) > 12:
            flags.append(f"GROUND LINE varies by {max(feet)-min(feet)}px")
        if cleaned:
            flags.append(f"removed {cleaned} bleed fragment(s)")
        if not groups:
            flags.append("figures touch — cut by column, not by figure")
        if pick is not None:
            flags.append(f"kept frames {pick} of {n}")
        note = "  <-- " + "; ".join(flags) if flags else ""
        print(f"  {seq:<16} {n} frames{' +calib' if calib else '       '}  "
              f"h={min(heights)}-{max(heights)}  "
              f"foot spread {max(feet)-min(feet)}px{note}")


def main() -> None:
    # Slicing every strip takes a while, so a sequence name (or several) can be
    # passed to redo just those: python tools/slice-strips.py panic celebrate_flip
    wanted = set(sys.argv[1:])
    for name, seqs in STRIPS.items():
        picked = [s for s in seqs if not wanted or s[0] in wanted]
        if picked:
            slice_character(name, picked)
    unknown = wanted - {s[0] for seqs in STRIPS.values() for s in seqs}
    if unknown:
        print(f"unknown sequence(s): {', '.join(sorted(unknown))}")


if __name__ == "__main__":
    main()
