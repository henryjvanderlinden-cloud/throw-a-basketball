#!/usr/bin/env python3
"""Bash both players' controls at random and check the game never lies to itself.

    python -m http.server 8899          # from the repo root, in another shell
    python tools/fuzz-game.py

Four rounds of random input, asserting on every frame the things that must be
true no matter what is pressed: one ball-holder at most, the holder's state
agreeing with who owns the ball, nobody off the court, no NaN, no negative
clock. It found nothing the last time it ran, which is the point of keeping it.
"""

import asyncio, sys

from playwright.async_api import async_playwright

# Bash two players on the controls at random for a while and assert that the
# match never reaches a state that cannot be true: two ball-holders, a holder
# whose state says otherwise, a player off the court, a stuck clock.
SCRIPT = """
async (seconds) => {
  const h = window.__hoop, dirs = ['left','right','up','down'];
  const bad = [];
  let rng = 12345;
  const rnd = () => (rng = (rng * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const t0 = performance.now();
  const held = [{},{}];
  let checks = 0;
  while (performance.now() - t0 < seconds * 1000) {
    for (let k = 0; k < 3; k++) {
      const n = rnd() < 0.5 ? 0 : 1;
      const d = dirs[Math.floor(rnd() * 4)];
      const on = rnd() < 0.5;
      if (on) h.press(n, d); else h.release(n, d);
      held[n][d] = on;
    }
    await new Promise(r => requestAnimationFrame(r));
    const s = h.state, ps = h.players;
    checks++;
    if (s.ms === 'PLAY' || s.ms === 'OVER') {
      const owners = ps.filter(p => p.state !== 'IDLE');
      if (owners.length > 1) bad.push('two holders: ' + ps.map(p => p.state).join(','));
      if (s.owner === null && owners.length) bad.push('loose ball but ' + owners[0].state);
      if (s.owner !== null && ps[s.owner].state === 'IDLE') bad.push('owner is IDLE');
      for (const p of ps) {
        if (!(p.px >= 40 && p.px <= 920)) bad.push('off court ' + p.px);
        if (!isFinite(p.px) || !isFinite(p.angle) || !isFinite(p.power)) bad.push('NaN player');
      }
      if (!isFinite(s.ball.x) || !isFinite(s.ball.y)) bad.push('NaN ball');
      if (s.clock < -0.001) bad.push('negative clock ' + s.clock);
      if (ps.some(p => p.points < 0)) bad.push('negative points');
    }
    if (bad.length > 8) break;
  }
  return { bad: [...new Set(bad)], checks,
           pts: h.players.map(p => p.points), ms: h.state.ms };
}
"""

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1000, "height": 820})
        errs = []
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto("http://localhost:8899/index.html")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.reload(); await pg.wait_for_timeout(700)
        await pg.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,2)")
        await pg.wait_for_timeout(200)
        # long enough to run the clock out several times over
        for round_ in range(4):
            r = await pg.evaluate(SCRIPT, 12)
            print(f"round {round_}: {r['checks']} frames checked, state={r['ms']}, points={r['pts']}")
            if r["bad"]:
                print("  INVARIANT BREAKS:", r["bad"]); errs.append(str(r["bad"]))
            # restart and go again
            await pg.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,1); __hoop.pick(1,1)")
            await pg.wait_for_timeout(150)
        print("errors:", errs[:5] if errs else "none")
        await b.close()
    sys.exit(1 if errs else 0)

asyncio.run(main())
