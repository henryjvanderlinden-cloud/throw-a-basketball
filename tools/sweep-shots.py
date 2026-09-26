#!/usr/bin/env python3
"""How easy is each character to score with? Fire a grid of shots and count.

handovers/HANDOVER_09.md §0(D). A character's launch point is measured from his
release frame (build-sprites.py hand_point), so new shot art quietly changes his
difficulty. This fires every angle (20-160 in 4-degree steps) at every power
(0-1 in 0.05 steps) from six spots on the court, exactly as shoot() in
index.html launches the ball, and reports the share that goes in.

    python -m http.server 8899          # from the repo root, then
    python tools/sweep-shots.py
    python tools/sweep-shots.py --launch zombie:13.91,-140.41   # what-if: an old launch point

Needs Playwright with Chromium, so it runs where test-game.py runs.
"""
import argparse, asyncio
from playwright.async_api import async_playwright

GROUND = 596                      # index.html
JS = """([ov, xs, GROUND]) => {
  const H = __hoop, g = H.state, p = H.players[0];
  if (ov) { p.char.handX = ov[0]; p.char.handY = ov[1]; }
  let made = 0, tot = 0;
  for (const x of xs) for (let a = 20; a <= 160; a += 4) for (let pw = 0; pw <= 1.0001; pw += 0.05) {
    g.ms = H.MS.PLAY; g.clockOn = false; g.clock = 99; p.px = x;
    const rad = a * Math.PI / 180, sp = 760 + (1560 - 760) * pw;      // SPEED_MIN/MAX
    const flip = p.char.mirror && !(p.char.fixed && p.char.fixed.includes('shot'));
    const b = g.ball;
    b.x = x + p.char.handX * (flip ? p.facing : 1); b.y = GROUND + p.char.handY + 12;
    b.vx = Math.cos(rad) * sp; b.vy = -Math.sin(rad) * sp; b.rest = false;
    g.owner = null; g.shooter = 0; g.scoredThisShot = false; p.state = H.PS.IDLE;
    for (let i = 0; i < 480 && !g.scoredThisShot; i++) H.step(1 / 120);
    tot++; if (g.scoredThisShot) made++;
  }
  return [made, tot];
}"""


async def main(a):
    over = {}
    for spec in a.launch or []:
        k, v = spec.split(":")
        over[k] = [float(x) for x in v.split(",")]
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        await pg.goto(a.url.rstrip("/") + "/index.html")
        await pg.wait_for_timeout(1500)
        keys = await pg.evaluate("__hoop.chars.map(c => c.key)")
        for k in keys:
            await pg.evaluate(f"__hoop.reset(); __hoop.setMode(1); __hoop.pick(0,{keys.index(k)});"
                              " __hoop.dismissGate(); __hoop.startMatch()")
            made, tot = await pg.evaluate(JS, [over.get(k), [150, 300, 450, 600, 750, 850], GROUND])
            print(f"{k:<14} {made:>4}/{tot}  {made / tot * 100:.1f}%"
                  + ("   (launch overridden)" if k in over else ""))
        await b.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8899/")
    ap.add_argument("--launch", action="append", help="key:handX,handY what-if override")
    asyncio.run(main(ap.parse_args()))
