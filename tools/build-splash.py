#!/usr/bin/env python3
"""Turn the splash artwork into web-sized frames for the menu screens.

The source paintings are 1448x1086 PNGs of about 3 MB each. Six of them on a
menu is 18 MB, which is silly for a game that otherwise fits in one HTML file,
so they are resampled and written as WebP.

    python tools/build-splash.py      # artwork/Splash Screens/ -> splash/

Two screens come out of it:

    splash/mode-0.webp .. mode-4.webp   the number-of-players screen: one base
                                        frame and four variations, each with a
                                        different character doing something
    splash/select.webp                  the character select

Every frame of a screen must share its composition exactly -- the game crossfades
nothing, it swaps the whole picture, which only reads as a wink or a blink if
the rest of the image is identical.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "artwork" / "Splash Screens"
OUT = ROOT / "splash"

# 853 CSS px on screen at the stage's widest, so this is comfortably sharp
# without paying for pixels nobody sees.
WIDTH = 1280
QUALITY = 82

# out-name -> source file. The base frame of a screen comes first.
FRAMES = {
    "mode-0": "Splash_Select_number_of_Players.png",
    "mode-1": "throw-a-basketball-7-blink-point.png",
    "mode-2": "throw-a-basketball-12-wink.png",
    "mode-3": "throw-a-basketball-34-ooo.png",
    "mode-4": "throw-a-basketball-13-blink.png",
    "select": "Splash_Select_Player_v02.png",
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    # Every frame of a screen is written at the base frame's size, whatever the
    # source measured. The generator does not always come back to the pixel --
    # the wink frame arrived 1447x1087 against the others' 1448x1086 -- and a
    # frame one pixel out makes the entire picture jump on the swap, which is
    # exactly the thing the identical composition was for.
    base_src = Image.open(SRC / FRAMES["mode-0"])
    size = (WIDTH, round(base_src.height * WIDTH / base_src.width))
    total = 0
    for name, fname in FRAMES.items():
        src = SRC / fname
        if not src.exists():
            print(f"{name:<10} SKIPPED (no {fname})")
            continue
        im = Image.open(src).convert("RGB")
        drift = "" if im.size == base_src.size else f"  (source {im.width}x{im.height}, squared up)"
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        dest = OUT / f"{name}.webp"
        im.save(dest, "WEBP", quality=QUALITY, method=6)
        kb = dest.stat().st_size / 1024
        total += kb
        print(f"{name:<10} {im.width}x{im.height}  {kb:6.0f} KB   <- {fname}{drift}")
    print(f"\n{total/1024:.1f} MB total")


if __name__ == "__main__":
    main()
