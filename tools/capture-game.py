#!/usr/bin/env python3
"""Watch a character in the game, at the game's own speed.

handovers/HANDOVER_04.md §0(A): the game is the instrument, the sheet is only a
screen. This replaces requestAnimationFrame with a manual pump, so game time
advances in exact 1/60 s steps however slow the machine or the screenshots
are, and a frame can be captured at any step.

    python -m http.server 8899                  # from the repo root
    python tools/capture-game.py --p1 nba --p2 zombie
    python tools/capture-game.py --p1 zombie --watch 0 --hold right

Writes into --out: one PNG per step, `loop.gif` (a crop around the watched
player at true speed) and `shown.txt` (which sequence and frame the game drew
at each step). A two-player match starts with player 1 holding the ball, so to
watch someone WITHOUT it, put him in as player 2 and watch player 2.

Needs Playwright with Chromium; like test-game.py it runs where a browser can
be launched, not in the device VM.
"""
import argparse, asyncio, json
from pathlib import Path

from playwright.async_api import async_playwright
from PIL import Image

PUMP = """
(() => {
  let q = [], t = 0;
  window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
  window.__pump = n => { for (let i = 0; i < n; i++) {
    t += 1000 / 60; const r = q; q = []; r.forEach(cb => cb(t)); } };
})();
"""


async def main(a) -> None:
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1000, "height": 820})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(PUMP)
        await pg.goto(a.url.rstrip("/") + "/index.html")
        await pg.wait_for_timeout(1500)
        keys = await pg.evaluate("__hoop.chars.map(c => c.key)")
        picks = f"__hoop.pick(0,{keys.index(a.p1)})"
        if a.p2:
            picks += f"; __hoop.pick(1,{keys.index(a.p2)})"
        await pg.evaluate(f"__hoop.reset(); __hoop.setMode({2 if a.p2 else 1}); {picks}")
        await pg.evaluate("__pump(90)")
        await pg.wait_for_timeout(1500)            # let the sprites arrive
        if a.start:
            # past the START overlay, so the capture shows play, not the dimmed
            # gate with the logo over the court
            await pg.evaluate("__hoop.dismissGate(); __hoop.startMatch()")
            await pg.evaluate("__pump(30)")
        if a.hold:
            await pg.evaluate(f"__hoop.press({a.watch}, '{a.hold}')")
        n = int(a.seconds * 60 / a.every)
        shown, crops = [], []
        for k in range(n):
            await pg.evaluate(f"__pump({a.every})")
            await pg.wait_for_timeout(30)
            p = await pg.evaluate(f"(() => {{ const p = __hoop.players[{a.watch}];"
                                  f" return {{shown: p.shown, state: p.state}}; }})()")
            shown.append(p)
            path = out / f"s{k:03d}.png"
            await pg.screenshot(path=str(path))
            # the rig's screen position, for the crop
            box = await pg.evaluate(f"""(() => {{
              const r = __hoop.players[{a.watch}].rig.root.getBoundingClientRect();
              return [r.left, r.top, r.right, r.bottom]; }})()""")
            x0, y0, x1, y1 = box
            cx, by = (x0 + x1) / 2, y1
            im = Image.open(path).convert("RGB")
            crop = im.crop((int(cx - 90), int(by - 170), int(cx + 90), int(by + 10)))
            crops.append(crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST))
        crops[0].save(out / "loop.gif", save_all=True, append_images=crops[1:],
                      duration=round(1000 * a.every / 60), loop=0)
        (out / "shown.txt").write_text(
            "\n".join(json.dumps(s) for s in shown), encoding="utf-8")
        seqs = sorted({tuple(s["shown"]) for s in shown if s["shown"]})
        print(f"{n} steps of {a.every} ticks -> {out}")
        print("drawn:", ", ".join(f"{s}[{i}]" for s, i in seqs))
        print("page errors:", errs or "none")
        await b.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8899/")
    ap.add_argument("--p1", default="zombie", help="character key for player 1")
    ap.add_argument("--p2", default=None, help="character key for player 2 (two-player)")
    ap.add_argument("--watch", type=int, default=None,
                    help="which player to follow, 0 or 1 (default: the last one picked)")
    ap.add_argument("--hold", default=None, help="hold a direction: left | right")
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--every", type=int, default=5, help="game ticks between captures")
    ap.add_argument("--out", default="build/capture")
    ap.add_argument("--start", action="store_true",
                    help="dismiss the START overlay and begin the match first")
    a = ap.parse_args()
    if a.watch is None:
        a.watch = 1 if a.p2 else 0
    asyncio.run(main(a))
