#!/usr/bin/env python3
"""Re-encode the two full-screen overlay graphics as WebP.

    python tools/build-overlays.py     # artwork/*.png -> artwork/overlays/*.webp

Two pieces of graffiti lettering that sit over the game rather than in it:

- **start** — the START button on the gate that covers the first menu. It is on
  screen at the same moment as the first menu, so it is one of the handful of
  files allowed in front of that menu (see claude/loading-policy.md) and its
  size is part of that budget. Keep it small.
- **steal** — the STEAL! badge that flashes in the top-left corner when somebody
  robs the ball.

Both sources are 1536x1024 RGBA with the generator's background keyed out by
artwork/prepare_*_alpha.py. Two things happen here that do *not* happen to the
splash paintings:

1. **They are cropped to their own alpha.** The lettering floats in a large
   transparent field; cropping is what lets the game place the graphic by its
   ink rather than by the empty space around it.
2. **They are resampled.** This is safe here and is not safe there: these are
   airbrushed graffiti with soft gradients, not the hard one-pixel steps and
   ordered dithering of the pixel-art splash screens, which a LANCZOS pass
   destroys. Do not copy this step back into tools/build-splash.py.

The PNGs stay in artwork/ as the fallback, the same arrangement as the courts.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "artwork"
OUT = ART / "overlays"
QUALITY = 86

# name, source, width in pixels. The widths are about 1:1 with the widest the
# graphic is ever drawn on a 1200px window, which is as much as a soft-edged
# overlay needs -- the start button costs 79 KB at 640 and 125 KB at 960, and
# the first of those has to fit in front of the menu.
JOBS = [
    ("start", "start-orange-basketball.png", 640),
    ("steal", "steal-purple-skull-v2.png", 480),
    ("score-blue", "score-blue-text.png", 480),
    ("score-red", "score-red-text.png", 480),
    # Drawn 600 wide across the middle of the stage rather than 260 in the
    # corner, so it gets the extra resolution.
    ("incredible-blue", "incredible-blue-text.png", 720),
    ("incredible-red", "incredible-red-text.png", 720),
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, src, width in JOBS:
        path = ART / src
        if not path.exists():
            print("%-6s SKIPPED (no %s)" % (name, src))
            continue
        im = Image.open(path).convert("RGBA")
        box = im.split()[3].getbbox()
        if box:
            im = im.crop(box)
        height = round(im.height * width / im.width)
        im = im.resize((width, height), Image.LANCZOS)
        dest = OUT / (name + ".webp")
        im.save(dest, "WEBP", quality=QUALITY, method=6)
        print("%-6s %s  %dx%d  %.0f KB  (from %.0f KB)"
              % (name, dest.name, width, height, dest.stat().st_size / 1024,
                 path.stat().st_size / 1024))


if __name__ == "__main__":
    main()
