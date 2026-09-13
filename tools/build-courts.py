#!/usr/bin/env python3
"""Re-encode the court backdrops as WebP.

    python tools/build-courts.py      # artwork/basketball-courts/*.png -> *.webp

The sources are 1448x1086 PNGs of 1.5-2.5 MB. A court is drawn 960x720 behind
the play, never inspected closely, and never on screen at the same time as
another one -- so it is the cheapest two megabytes in the repo to give back.
Resolution is left alone (still 1448 wide, comfortably above the 960 CSS px the
stage is widest at, so it stays sharp on a scaled display); only the encoding
changes.

The game prefers the .webp and falls back to the .png, so an un-run build or a
browser without WebP still gets a court.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "artwork" / "basketball-courts"
QUALITY = 86


def main() -> None:
    before = after = 0
    for src in sorted(DIR.glob("*.png")):
        im = Image.open(src).convert("RGB")
        dest = src.with_suffix(".webp")
        im.save(dest, "WEBP", quality=QUALITY, method=6)
        b, a = src.stat().st_size, dest.stat().st_size
        before += b
        after += a
        print(f"{src.name:<14} {b/1024:7.0f} KB -> {dest.name:<15} {a/1024:6.0f} KB   ({a*100/b:.0f}%)")
    if before:
        print(f"\n{before/1e6:.1f} MB -> {after/1e6:.1f} MB")


if __name__ == "__main__":
    main()
