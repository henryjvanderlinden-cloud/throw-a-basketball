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
    ],
}


BLEED_MAX_SHARE = 0.15      # a stray blob is at most this share of the figure


def ink_columns(im: Image.Image) -> np.ndarray:
    return (np.array(im.getchannel("A")) > ALPHA_CUT).sum(axis=0)


def components(mask: np.ndarray):
    """Label 4-connected blobs. Row-wise union-find; no scipy needed."""
    h, w = mask.shape
    parent: dict[int, int] = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    labels = np.zeros((h, w), dtype=np.int32)
    nxt = 1
    for y in range(h):
        row = mask[y]
        if not row.any():
            continue
        for x in np.where(row)[0]:
            up = labels[y - 1, x] if y else 0
            left = labels[y, x - 1] if x else 0
            if up and left:
                labels[y, x] = min(up, left)
                union(up, left)
            elif up or left:
                labels[y, x] = up or left
            else:
                labels[y, x] = nxt
                parent[nxt] = nxt
                nxt += 1
    for lab in range(1, nxt):
        find(lab)
    flat = np.zeros(nxt, dtype=np.int32)
    for lab in range(1, nxt):
        flat[lab] = find(lab)
    return flat[labels]


def drop_bleed(cell: Image.Image, touch_left: bool, touch_right: bool) -> int:
    """Erase small blobs that lean on an internal cut -- a neighbour's tail.

    Only blobs touching a cut are removed, so genuinely detached parts of the
    pose (the thrown banana peel, for instance) survive.
    """
    if not (touch_left or touch_right):
        return 0
    arr = np.array(cell)
    mask = arr[:, :, 3] > ALPHA_CUT
    if not mask.any():
        return 0
    lab = components(mask)
    ids, counts = np.unique(lab[lab > 0], return_counts=True)
    if len(ids) < 2:
        return 0
    biggest = counts.max()
    removed = 0
    for i, c in zip(ids, counts):
        if c >= biggest * BLEED_MAX_SHARE:
            continue
        blob = lab == i
        on_left = touch_left and blob[:, 0].any()
        on_right = touch_right and blob[:, -1].any()
        if on_left or on_right:
            arr[:, :, 3][blob] = 0
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
        if max(feet) - min(feet) > 12:
            flags.append(f"GROUND LINE varies by {max(feet)-min(feet)}px")
        if cleaned:
            flags.append(f"removed {cleaned} bleed fragment(s)")
        note = "  <-- " + "; ".join(flags) if flags else ""
        print(f"  {seq:<16} {n} frames  h={min(heights)}-{max(heights)}  "
              f"foot spread {max(feet)-min(feet)}px{note}")


def main() -> None:
    for name, seqs in STRIPS.items():
        slice_character(name, seqs)


if __name__ == "__main__":
    main()
