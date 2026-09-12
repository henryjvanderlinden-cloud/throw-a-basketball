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

# character -> [(sequence name, strip file, frame count)]
# Numbers match the prompts in docs/prompts-monkey.md.
STRIPS = {
    "Monkey": [
        ("dribble_idle",    "Monkey_sequence_001.png", 4),
        ("run_dribble_r",   "Monkey_sequence_002.png", 4),
        ("run_dribble_l",   "Monkey_sequence_003.png", 4),
        ("pickup",          "Monkey_sequence_004.png", 3),
        ("turn",            "Monkey_sequence_005.png", 2),
        ("aim",             "Monkey_sequence_006.png", 2),
        ("charge",          "Monkey_sequence_007.png", 3),
        ("shot",            "Monkey_sequence_008.png", 4),
        ("run_r",           "Monkey_sequence_009.png", 2),
        ("run_l",           "Monkey_sequence_010.png", 2),
        ("celebrate",       "Monkey_sequence_011.png", 2),
        ("gameover",        "Monkey_sequence_012.png", 2),
        ("break_banana",    "Monkey_sequence_013.png", 4),
        ("break_wave",      "Monkey_sequence_014.png", 4),
        ("panic",           "Monkey_sequence_015.png", 4),
        ("celebrate_pump",  "Monkey_sequence_016.png", 3),
        ("celebrate_flip",  "Monkey_sequence_017.png", 6),
    ],
}


BLEED_MAX_SHARE = 0.15      # a stray blob is at most this share of the figure

# Sequences that deliberately leave the floor, so the ground-line check would
# only produce a misleading warning.
AIRBORNE = {"celebrate_flip"}


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
    for seq, filename, n in seqs:
        path = src_dir / filename
        if not path.exists():
            print(f"  {seq:<16} MISSING {filename}")
            continue
        im = Image.open(path).convert("RGBA")
        cuts = cut_points(im, n)

        out_dir = out_root / seq
        out_dir.mkdir(parents=True, exist_ok=True)
        heights, feet, cleaned = [], [], 0
        for i in range(n):
            cell = im.crop((cuts[i], 0, cuts[i + 1], im.height))
            m = np.array(cell.getchannel("A")) > ALPHA_CUT
            if not m.any():
                print(f"  {seq:<16} frame {i+1} is EMPTY -- wrong frame count?")
                continue
            # Ink on an *internal* cut means a neighbour bled in; the outer
            # edges are just the image border cropping the figure.
            cleaned += drop_bleed(cell, touch_left=i > 0, touch_right=i < n - 1)
            m = np.array(cell.getchannel("A")) > ALPHA_CUT
            ys, xs = np.where(m)
            heights.append(int(ys.max() - ys.min()))
            feet.append(int(ys.max()))
            cell.save(out_dir / f"{i+1:02d}.png")

        flags = []
        if seq not in AIRBORNE and max(feet) - min(feet) > 12:
            flags.append(f"GROUND LINE varies by {max(feet)-min(feet)}px")
        if cleaned:
            flags.append(f"removed {cleaned} bleed fragment(s)")
        note = "  <-- " + "; ".join(flags) if flags else ""
        print(f"  {seq:<16} {n} frames  h={min(heights)}-{max(heights)}  "
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
