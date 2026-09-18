#!/usr/bin/env python3
"""Play the game headlessly and check that it still behaves.

    pip install playwright && playwright install chromium
    python -m http.server 8899          # from the repo root, in another shell
    python tools/test-game.py           # or: ... test-game.py http://host:port/

Everything is driven through `window.__hoop`, the same handle the console uses:
`press`/`release` go in through the real input path, so a test presses keys
rather than setting variables. Screenshots of each stage land in OUT.

The checks are deliberately about behaviour that has actually broken at least
once -- a stuck pad button, a charge with no way out, a sprite anchored to one
shoe, two frames of a splash that do not line up -- rather than about coverage.
"""

import asyncio, sys, json, os, tempfile

from playwright.async_api import async_playwright

URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8899/").rstrip("/")
if not URL.endswith(".html"):
    URL += "/index.html"
OUT = os.environ.get("HOOP_SHOTS", os.path.join(tempfile.gettempdir(), "hoop-shots"))
os.makedirs(OUT, exist_ok=True)

FAILS = []
def check(name, cond, extra=""):
    print(("  PASS " if cond else "  FAIL ") + name + ("  " + str(extra) if extra else ""))
    if not cond: FAILS.append(name)

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1000, "height": 820})
        errs = []
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error","warning") else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        await pg.goto(URL)
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.reload()
        await pg.wait_for_timeout(900)

        print("\n== the start gate ==")
        # It covers everything, including the buttons, so it has to go before
        # anything else here can be clicked -- which is the point of it: the
        # browser will not play a sound until the player has pressed something.
        check("the gate is up at boot", await pg.evaluate("__hoop.gate"))
        gate = await pg.evaluate("""() => {
          const g = document.getElementById('startGate');
          const r = g.querySelector('rect'), im = document.getElementById('startArt');
          return {op: +g.getAttribute('opacity'), scrim: +r.getAttribute('opacity'),
                  w: +r.getAttribute('width'), h: +r.getAttribute('height'),
                  href: im.getAttribute('href') || '',
                  last: g === g.parentNode.lastElementChild};
        }""")
        check("it is visible", gate["op"] == 1, gate)
        check("the black layer is see-through, not opaque",
              0 < gate["scrim"] < 1, gate["scrim"])
        check("and it covers the whole stage",
              gate["w"] == 960 and gate["h"] >= 720, gate)
        check("the start artwork is on it", gate["href"].endswith("start.webp"), gate["href"])
        check("nothing else can be reached past it", gate["last"], gate)
        # A keyboard player has no button to aim at, so any key does it -- and
        # that press must not also work the menu underneath.
        before = await pg.evaluate("__hoop.state.ms")
        await pg.keyboard.press("ArrowRight")
        await pg.wait_for_timeout(100)
        check("the first key press only dismisses the gate",
              not await pg.evaluate("__hoop.gate"))
        check("and does not reach the menu behind it",
              await pg.evaluate("__hoop.state.ms") == before)
        check("it fades out rather than vanishing",
              await pg.evaluate("document.getElementById('startGate').classList.contains('gone')"))
        await pg.wait_for_timeout(350)

        print("\n== boot ==")
        ms = await pg.evaluate("__hoop.state.ms")
        check("boots into mode select", ms == "MODE", ms)
        check("no console errors on boot", not errs, errs[:5])
        await pg.screenshot(path=f"{OUT}/01-mode.png")

        # ---- keyboard navigation of the mode screen
        await pg.keyboard.press("ArrowRight")
        check("arrow picks 2P card", await pg.evaluate("__hoop.state.ms") == "MODE")
        await pg.keyboard.press("ArrowUp")
        await pg.wait_for_timeout(200)
        check("up enters character select", await pg.evaluate("__hoop.state.ms") == "SELECT")
        check("two players built", await pg.evaluate("__hoop.numPlayers") == 2)
        await pg.screenshot(path=f"{OUT}/02-select-p1.png")

        # P2's keys must be inert during P1's turn
        before = await pg.evaluate("__hoop.players[0].charIdx")
        await pg.keyboard.press("KeyD")
        after = await pg.evaluate("__hoop.players[0].charIdx")
        check("P2 keys inert during P1 pick", before == after, f"{before}->{after}")
        await pg.keyboard.press("ArrowRight")
        check("P1 arrow moves P1 selection",
              await pg.evaluate("__hoop.players[0].charIdx") == (before + 1) % 4)
        await pg.keyboard.press("ArrowUp")
        await pg.wait_for_timeout(150)
        check("still in select, now P2's turn", await pg.evaluate("__hoop.state.ms") == "SELECT")
        await pg.screenshot(path=f"{OUT}/03-select-p2.png")

        # P1's keys inert during P2's turn; P2 picks the SAME character as P1
        p1c = await pg.evaluate("__hoop.players[0].charIdx")
        await pg.keyboard.press("ArrowRight")
        check("P1 keys inert during P2 pick",
              await pg.evaluate("__hoop.players[0].charIdx") == p1c)
        await pg.evaluate(f"__hoop.pick(1,{p1c})")
        await pg.wait_for_timeout(200)
        check("match started", await pg.evaluate("__hoop.state.ms") == "PLAY")
        check("both players on same character",
              await pg.evaluate("__hoop.players[0].charIdx === __hoop.players[1].charIdx"))
        check("P1 has the ball", await pg.evaluate("__hoop.state.owner") == 0)
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=f"{OUT}/04-play-2p.png")

        print("\n== movement / independence ==")
        st = await pg.evaluate("({a:__hoop.players[0].px, b:__hoop.players[1].px})")
        await pg.keyboard.down("ArrowLeft"); await pg.keyboard.down("KeyD")
        await pg.wait_for_timeout(350)
        await pg.keyboard.up("ArrowLeft"); await pg.keyboard.up("KeyD")
        st2 = await pg.evaluate("({a:__hoop.players[0].px, b:__hoop.players[1].px})")
        check("P1 moved left", st2["a"] < st["a"] - 20, st2["a"] - st["a"])
        check("P2 moved right", st2["b"] > st["b"] + 20, st2["b"] - st["b"])

        print("\n== space is disabled in 2P ==")
        await pg.keyboard.press("Space")
        check("space does not start aiming in 2P",
              await pg.evaluate("__hoop.players[0].state") == "DRIBBLE")

        print("\n== steal ==")
        # park them apart, opponent tries to steal -> must fail on distance
        await pg.evaluate("__hoop.players[0].px=300; __hoop.players[1].px=700;"
                          "__hoop.state.stealImmune=0; __hoop.players[1].stealCd=0")
        await pg.keyboard.press("KeyS"); await pg.wait_for_timeout(80)
        check("steal fails when far apart", await pg.evaluate("__hoop.state.owner") == 0)
        await pg.keyboard.up("KeyS")
        # close in, clear immunity, steal
        await pg.evaluate("__hoop.players[1].px=340; __hoop.state.stealImmune=0;"
                          "__hoop.players[1].stealCd=0")
        await pg.keyboard.down("KeyS"); await pg.wait_for_timeout(120)
        check("steal succeeds when close", await pg.evaluate("__hoop.state.owner") == 1)
        check("victim is IDLE", await pg.evaluate("__hoop.players[0].state") == "IDLE")
        check("thief is DRIBBLE", await pg.evaluate("__hoop.players[1].state") == "DRIBBLE")
        await pg.keyboard.up("KeyS")
        await pg.screenshot(path=f"{OUT}/05-after-steal.png")

        # immunity blocks the instant steal-back
        await pg.evaluate("__hoop.players[0].stealCd=0")
        imm = await pg.evaluate("__hoop.state.stealImmune")
        await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(100)
        check("steal-back blocked by immunity",
              await pg.evaluate("__hoop.state.owner") == 1, f"immune={imm:.2f}")
        await pg.keyboard.up("ArrowDown")
        # ...but works once immunity lapses
        await pg.evaluate("__hoop.state.stealImmune=0; __hoop.players[0].stealCd=0")
        await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(120)
        check("steal-back works after immunity", await pg.evaluate("__hoop.state.owner") == 0)
        await pg.keyboard.up("ArrowDown")

        print("\n== aiming player cannot be robbed ==")
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(80)
        check("P1 aiming", await pg.evaluate("__hoop.players[0].state") == "AIM")
        await pg.evaluate("__hoop.state.stealImmune=0; __hoop.players[1].stealCd=0;"
                          "__hoop.players[1].px=__hoop.players[0].px+20")
        await pg.keyboard.down("KeyS"); await pg.wait_for_timeout(150)
        check("cannot steal from an aiming player", await pg.evaluate("__hoop.state.owner") == 0)
        await pg.keyboard.up("KeyS")

        print("\n== shooting / scoring ==")
        # aim and charge, then drop the ball straight through the hoop by fiat
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(400)
        check("charging", await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        pw_ = await pg.evaluate("__hoop.players[0].power")
        check("power builds", 0.2 < pw_ < 1.01, round(pw_, 2))
        await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(60)
        check("ball released", await pg.evaluate("__hoop.state.owner") is None)
        check("clock reset on throw", await pg.evaluate("__hoop.state.clock") > 9.0)
        # force a make
        await pg.evaluate("""
          const s=__hoop.state; s.ball.x=480; s.ball.y=120; s.ball.vx=0; s.ball.vy=400;
          s.scoredThisShot=false; s.shooter=0;
        """)
        await pg.wait_for_timeout(250)
        check("P1 scored 3", await pg.evaluate("__hoop.players[0].points") == 3)
        check("P2 still 0", await pg.evaluate("__hoop.players[1].points") == 0)
        await pg.screenshot(path=f"{OUT}/06-scored.png")

        print("\n== rebound goes to the nearer player, not the shooter ==")
        await pg.evaluate("""
          const h=__hoop, s=h.state;
          s.owner=null; s.shooter=0; s.scoredThisShot=true;
          h.players[0].px=200; h.players[0].lockout=0;
          h.players[1].px=700; h.players[1].lockout=0;
          s.ball.x=700; s.ball.y=560; s.ball.vx=0; s.ball.vy=0;
        """)
        await pg.wait_for_timeout(150)
        check("nearer player collects", await pg.evaluate("__hoop.state.owner") == 1)

        print("\n== game over ==")
        await pg.evaluate("__hoop.state.clockOn=true; __hoop.state.clock=0.02")
        await pg.wait_for_timeout(250)
        check("match ended", await pg.evaluate("__hoop.state.ms") == "OVER")
        title = await pg.evaluate("document.getElementById('ovTitle').textContent")
        check("winner announced", "WINS" in title or title == "DRAW", title)
        await pg.screenshot(path=f"{OUT}/07-over.png")
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(200)
        check("up restarts to mode select", await pg.evaluate("__hoop.state.ms") == "MODE")

        print("\n== one-player mode unchanged ==")
        await pg.keyboard.press("ArrowLeft"); await pg.keyboard.press("ArrowUp")
        await pg.wait_for_timeout(150)
        check("1P select", await pg.evaluate("__hoop.numPlayers") == 1)
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(250)
        check("1P match running", await pg.evaluate("__hoop.state.ms") == "PLAY")
        check("only one player", await pg.evaluate("__hoop.players.length") == 1)
        await pg.keyboard.press("Space"); await pg.wait_for_timeout(80)
        check("space works in 1P", await pg.evaluate("__hoop.players[0].state") == "AIM")
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(60)
        check("up also charges in 1P", await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        # Space and Up share one direction: letting go of one must not shoot
        # while the other is still held.
        await pg.keyboard.down("Space"); await pg.wait_for_timeout(40)
        await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(60)
        check("releasing Up while Space is held keeps charging",
              await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        await pg.keyboard.up("Space"); await pg.wait_for_timeout(60)
        check("releasing the last one shoots", await pg.evaluate("__hoop.state.owner") is None)
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=f"{OUT}/08-play-1p.png")

        print("\n== touch pads ==")
        await pg.evaluate("__hoop.reset()"); await pg.wait_for_timeout(100)
        # click the 2P card, then pick with taps
        box = await pg.evaluate("""() => {
          const c = document.getElementById('modeCards').children[1].getBoundingClientRect();
          return {x:c.x+c.width/2, y:c.y+c.height/2};
        }""")
        await pg.mouse.click(box["x"], box["y"]); await pg.wait_for_timeout(150)
        check("tapping the 2P card works", await pg.evaluate("__hoop.numPlayers") == 2)
        await pg.evaluate("__hoop.pick(0,0)"); await pg.evaluate("__hoop.pick(1,1)")
        await pg.wait_for_timeout(200)
        # press and hold P1's up pad button -> should charge
        pad = await pg.evaluate("""() => {
          const b = document.querySelectorAll('#pads > g')[0].children[2].getBoundingClientRect();
          return {x:b.x+b.width/2, y:b.y+b.height/2};
        }""")
        await pg.mouse.move(pad["x"], pad["y"]); await pg.mouse.down()
        await pg.wait_for_timeout(120)
        check("pad up -> aiming", await pg.evaluate("__hoop.players[0].state") == "AIM")
        await pg.mouse.up(); await pg.wait_for_timeout(50)
        await pg.mouse.down(); await pg.wait_for_timeout(350)
        check("pad up held -> charging", await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        await pg.screenshot(path=f"{OUT}/09-pad-charge.png")
        await pg.mouse.up(); await pg.wait_for_timeout(80)
        check("pad release shoots", await pg.evaluate("__hoop.state.owner") is None)
        # a thumb that slides off keeps charging (the button captures the
        # pointer), and lifting it anywhere still releases
        await pg.evaluate("""
          const h=__hoop; h.state.owner=0; h.players[0].state='DRIBBLE';
        """)
        await pg.mouse.move(pad["x"], pad["y"]); await pg.mouse.down(); await pg.wait_for_timeout(100)
        await pg.mouse.move(pad["x"], pad["y"] - 200); await pg.wait_for_timeout(250)
        check("sliding off keeps charging", await pg.evaluate("__hoop.players[0].held.up"))
        await pg.mouse.up(); await pg.wait_for_timeout(80)
        check("lifting off the button still releases",
              await pg.evaluate("!__hoop.players[0].held.up"))

        print("\n== bugs found in review ==")
        # 1. confirming P1's character with the PAD must not stick that button
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2)"); await pg.wait_for_timeout(150)
        padUp = await pg.evaluate("""() => {
          const b = document.querySelectorAll('#pads > g')[0].children[2].getBoundingClientRect();
          return {x:b.x+b.width/2, y:b.y+b.height/2};
        }""")
        await pg.mouse.move(padUp["x"], padUp["y"]); await pg.mouse.down()
        await pg.wait_for_timeout(120); await pg.mouse.up()
        await pg.wait_for_timeout(120)
        await pg.evaluate("__hoop.pick(1,0)"); await pg.wait_for_timeout(200)
        check("match started after pad confirm", await pg.evaluate("__hoop.state.ms") == "PLAY")
        check("P1's up is not stuck after confirming on the pad",
              await pg.evaluate("!__hoop.players[0].held.up"))
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(80)
        check("P1's up key still works after a pad confirm",
              await pg.evaluate("__hoop.players[0].state") in ("AIM", "CHARGE"))
        await pg.keyboard.up("ArrowUp")

        # 2. a key held through the character select must not leak into the match
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2)"); await pg.wait_for_timeout(120)
        await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(100)
        await pg.evaluate("__hoop.pick(0,0); __hoop.pick(1,0)"); await pg.wait_for_timeout(200)
        check("held key does not leak into the match",
              await pg.evaluate("!__hoop.players[0].held.right"))
        await pg.keyboard.up("ArrowRight")

        # 3. tip-off carries steal immunity
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,0)")
        await pg.wait_for_timeout(60)
        check("tip-off is protected", await pg.evaluate("__hoop.state.stealImmune") > 0.5)

        # 4. the buzzer must not strand a player mid-charge
        await pg.evaluate("__hoop.players[0].state='AIM'")
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(200)
        check("charging when the buzzer goes", await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        await pg.evaluate("__hoop.state.clockOn=true; __hoop.state.clock=0.02")
        await pg.wait_for_timeout(200)
        check("match over", await pg.evaluate("__hoop.state.ms") == "OVER")
        check("nobody left charging", await pg.evaluate("__hoop.players[0].state") != "CHARGE")
        check("owner and state still agree",
              await pg.evaluate("__hoop.state.owner === null || "
                                "__hoop.players[__hoop.state.owner].state !== 'IDLE'"))
        await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(80)
        check("releasing after the buzzer fires no shot",
              await pg.evaluate("__hoop.state.ms") == "OVER")

        # 5. losing focus mid-charge cancels the wind-up, it does not shoot
        await pg.evaluate("__hoop.reset(); __hoop.setMode(1); __hoop.pick(0,0)")
        await pg.wait_for_timeout(150)
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(80)
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(250)
        check("charging before blur", await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        await pg.evaluate("window.dispatchEvent(new Event('blur'))")
        await pg.wait_for_timeout(80)
        check("blur does not fire the shot", await pg.evaluate("__hoop.state.owner") == 0)
        check("blur winds back to the aim, not a dead state",
              await pg.evaluate("__hoop.players[0].state") == "AIM")
        await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(60)
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(200)
        check("can charge again after a blur",
              await pg.evaluate("__hoop.players[0].state") == "CHARGE")
        await pg.keyboard.up("ArrowUp")

        # 6. __hoop.pick on a player that does not exist must not throw
        await pg.evaluate("__hoop.reset(); __hoop.setMode(1)")
        check("pick() on a missing player is a no-op",
              await pg.evaluate("__hoop.pick(1,0)") is False)

        print("\n== pad layout mirrors the keyboard ==")
        geo = await pg.evaluate("""() => {
          const out = [];
          for (const pad of document.querySelectorAll('#pads > g')) {
            const b = {};
            ['left','right','up','down'].forEach((d,i) => {
              const r = pad.children[i].firstChild;
              b[d] = {x:+r.getAttribute('x'), y:+r.getAttribute('y'),
                      w:+r.getAttribute('width'), h:+r.getAttribute('height')};
            });
            out.push(b);
          }
          return out;
        }""")
        for n, pad in enumerate(geo):
            cx = lambda d: pad[d]["x"] + pad[d]["w"] / 2
            tag = f"pad {n}"
            check(f"{tag}: up and down share a column", abs(cx("up") - cx("down")) < 0.01,
                  f"{cx('up')} vs {cx('down')}")
            check(f"{tag}: up sits above the other three", pad["up"]["y"] < pad["down"]["y"])
            check(f"{tag}: left, down, right share a row",
                  pad["left"]["y"] == pad["down"]["y"] == pad["right"]["y"])
            check(f"{tag}: left is left of down is left of right",
                  cx("left") < cx("down") < cx("right"))
            check(f"{tag}: no two buttons overlap", not any(
                  not (pad[i]["x"] + pad[i]["w"] <= pad[j]["x"] or
                       pad[j]["x"] + pad[j]["w"] <= pad[i]["x"] or
                       pad[i]["y"] + pad[i]["h"] <= pad[j]["y"] or
                       pad[j]["y"] + pad[j]["h"] <= pad[i]["y"])
                  for i in pad for j in pad if i < j))
        check("pads do not collide with each other or the scoreboard",
              geo[1]["right"]["x"] + geo[1]["right"]["w"] < 280 and geo[0]["left"]["x"] > 680)

        print("\n== the clock holds between possessions ==")
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,0)")
        await pg.wait_for_timeout(200)
        check("clock is not running at tip-off", await pg.evaluate("!__hoop.state.clockOn"))
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(400)
        check("first press starts it", await pg.evaluate("__hoop.state.clockOn"))
        c1 = await pg.evaluate("__hoop.state.clock")
        check("and it is counting down", c1 < 9.9, round(c1, 2))
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(300)
        await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(60)
        check("throw stops the clock", await pg.evaluate("!__hoop.state.clockOn"))
        check("throw resets it to full", await pg.evaluate("__hoop.state.clock") > 9.99)
        held = await pg.evaluate("__hoop.state.clock")
        await pg.wait_for_timeout(600)
        check("it stays put while the ball is loose",
              abs(await pg.evaluate("__hoop.state.clock") - held) < 0.01)
        check("nobody has the ball", await pg.evaluate("__hoop.state.owner") is None)
        # walk player 2 into the ball
        await pg.evaluate("""
          const h=__hoop, s=h.state;
          s.ball.x=700; s.ball.y=560; s.ball.vx=0; s.ball.vy=0;
          h.players[1].px=700; h.players[1].lockout=0;
        """)
        await pg.wait_for_timeout(200)
        check("picking it up restarts the clock",
              await pg.evaluate("__hoop.state.owner") == 1 and
              await pg.evaluate("__hoop.state.clockOn"))
        await pg.wait_for_timeout(400)
        check("and it counts down again", await pg.evaluate("__hoop.state.clock") < 9.9)

        print("\n== panic without the ball ==")
        await pg.evaluate("""
          const h=__hoop, s=h.state;
          s.clockOn=true; s.clock=1.5;
          h.players[0].px=200; h.players[1].px=700;
        """)
        await pg.wait_for_timeout(250)
        shown = await pg.evaluate("({a:__hoop.players[0].shown, b:__hoop.players[1].shown})")
        check("the player WITHOUT the ball panics", shown["a"][0] == "panic", shown["a"])
        check("the player WITH the ball panics too", shown["b"][0] == "panic", shown["b"])
        # ...but running cancels it
        await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(250)
        run = await pg.evaluate("__hoop.players[0].shown")
        check("running cancels the ball-less panic", run[0] != "panic", run)
        await pg.keyboard.up("ArrowRight")
        # ...and a held clock does not panic anyone
        await pg.evaluate("__hoop.state.clockOn=false"); await pg.wait_for_timeout(200)
        quiet = await pg.evaluate("__hoop.players[0].shown")
        check("a stopped clock panics nobody", quiet[0] != "panic", quiet)

        print("\n== nothing on the court can be dragged or grabbed ==")
        await pg.evaluate("__hoop.reset(); __hoop.setMode(1); __hoop.pick(0,0)")
        await pg.wait_for_timeout(300)
        drag = await pg.evaluate("""() => {
          const imgs=[...document.querySelectorAll('svg#stage image')];
          const bad = imgs.filter(i => {
            const cs=getComputedStyle(i);
            return cs.webkitUserDrag !== 'none' || cs.pointerEvents !== 'none';
          });
          return {total: imgs.length, draggable: bad.length};
        }""")
        check("no image on the stage is draggable",
              drag["draggable"] == 0, f"{drag['draggable']} of {drag['total']}")
        # the player must not be grabbable: a press on him should hit nothing
        hit = await pg.evaluate("""() => {
          const im=[...document.querySelectorAll('#players image')].find(i=>i.getAttribute('opacity')==='1')
                || document.querySelector('#players image');
          const r=im.getBoundingClientRect();
          const el=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2);
          return el ? (el.id || el.tagName) : null;
        }""")
        check("pressing on the player does not grab the sprite", hit != "image", f"hit {hit}")
        # ...but the character cards must still be clickable through their art
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2)"); await pg.wait_for_timeout(600)
        art = await pg.evaluate("""() => {
          const g=document.getElementById('selCards').children[3];
          const r=g.children[1].getBoundingClientRect();
          return {x:r.x+r.width/2, y:r.y+r.height/2, want:+g.getAttribute('data-i')};
        }""")
        await pg.mouse.click(art["x"], art["y"]); await pg.wait_for_timeout(250)
        check("clicking a character's artwork still picks him",
              await pg.evaluate("__hoop.players[0].charIdx") == art["want"],
              f"wanted {art['want']}")

        print("\n== splash artwork ==")
        await pg.evaluate("__hoop.reset()"); await pg.wait_for_timeout(1200)
        sp = await pg.evaluate("""() => {
          const f=[...document.querySelectorAll('#splashFrames image')];
          return {
            n: f.length,
            loaded: f.filter(i => i.getBBox().width > 0).length,
            sizes: [...new Set(f.map(i => i.getAttribute('width')+'x'+i.getAttribute('height')))],
            shown: document.getElementById('splash').getAttribute('opacity'),
            title: document.getElementById('modeTitle').getAttribute('opacity')
          };
        }""")
        check("all six frames are in the page", sp["n"] == 6, sp["n"])
        # The mode screen is a base painting plus a small patch laid over it, so
        # the frames are deliberately NOT all one size any more. What must hold
        # is that the full-screen paintings agree with each other, and that every
        # patch lands inside the picture where the manifest says.
        geo = await pg.evaluate("""() => {
          const all=[...document.querySelectorAll('#splashFrames image')];
          const full=all.filter(i => !i.hasAttribute('data-patch'));
          const patch=all.filter(i => i.hasAttribute('data-patch'));
          const box=i => [+i.getAttribute('x'), +i.getAttribute('y'),
                          +i.getAttribute('width'), +i.getAttribute('height')];
          const vb=document.getElementById('stage').getAttribute('viewBox').split(' ').map(Number);
          return {fullSizes:[...new Set(full.map(i => box(i).slice(2).join('x')))],
                  nPatch:patch.length, patches:patch.map(box), vw:vb[2], vh:vb[3]};
        }""")
        check("the full-screen paintings are all one size",
              len(geo["fullSizes"]) == 1, geo["fullSizes"])
        check("there is a patch per variation", geo["nPatch"] == 4, geo["nPatch"])
        check("every patch lands inside the painting",
              all(x >= 0 and y >= 0 and x + w <= geo["vw"] + 0.5 and y + h <= geo["vh"] + 0.5
                  for x, y, w, h in geo["patches"]), geo["patches"])
        check("and every patch is a patch, not a whole screen",
              all(w * h < 0.25 * geo["vw"] * geo["vh"] for x, y, w, h in geo["patches"]),
              [f"{w}x{h}" for x, y, w, h in geo["patches"]])
        check("the splash shows on the mode screen", sp["shown"] == "1")
        check("the menu's own title gives way to the painted one", sp["title"] == "0")
        # the menu stage is exactly 4:3, so the art runs to every edge
        fit = await pg.evaluate("""() => {
          const i=document.querySelector('#splashFrames image');
          const vb=document.getElementById('stage').getAttribute('viewBox').split(' ').map(Number);
          return {w:+i.getAttribute('width'), h:+i.getAttribute('height'),
                  vw:vb[2], vh:vb[3],
                  band:document.getElementById('band').getAttribute('opacity')};
        }""")
        check("the menu stage is exactly 4:3", abs(fit["vw"]/fit["vh"] - 4/3) < 0.002,
              f"{fit['vw']}x{fit['vh']}")
        check("the art fills it edge to edge, no bars",
              fit["w"] == fit["vw"] and fit["h"] == fit["vh"], f"{fit['w']}x{fit['h']}")
        check("the control band is out of frame during a menu", fit["band"] == "0")

        # the idle cycle: base, a variation, base, a different variation
        seen = []
        base_dropped = False
        for _ in range(70):
            cur = await pg.evaluate("""() => {
              const all=[...document.querySelectorAll('#splashFrames image')];
              const patch=all.filter(i => i.hasAttribute('data-patch'));
              const base=all.find(i => !i.hasAttribute('data-patch'));
              return {p: patch.findIndex(i => i.getAttribute('opacity') === '1'),
                      base: base.getAttribute('opacity')};
            }""")
            if cur["base"] != "1":
                base_dropped = True
            if not seen or seen[-1] != cur["p"]: seen.append(cur["p"])
            await pg.wait_for_timeout(180)
        variations = [x for x in seen if x >= 0]
        check("the mode screen cycles through variations", len(variations) >= 2, seen)
        # The whole point of patching rather than swapping whole frames: the
        # painting underneath never reloads, so the swap cannot flicker.
        check("the base painting never blinks out during a swap", not base_dropped)
        check("it returns to the bare base between them",
              all(not (seen[i] >= 0 and seen[i+1] >= 0) for i in range(len(seen)-1)), seen)
        check("never the same variation twice running",
              all(variations[i] != variations[i+1] for i in range(len(variations)-1)), variations)

        await pg.evaluate("__hoop.setMode(1); __hoop.pick(0,0)"); await pg.wait_for_timeout(300)
        check("the splash gets out of the way in a match",
              await pg.evaluate("document.getElementById('splash').getAttribute('opacity')") == "0")

        print("\n== no flash of the wrong menu at boot ==")
        pg2 = await b.new_page(viewport={"width": 1000, "height": 880})
        seen_bare = []
        await pg2.goto(URL)
        for _ in range(24):
            st = await pg2.evaluate("""() => {
              const m=document.getElementById('mode');
              const sp=document.getElementById('splash');
              if (!m) return null;
              return {menu:+m.getAttribute('opacity'), splash:+sp.getAttribute('opacity'),
                      scrim:+document.getElementById('modeScrim').getAttribute('opacity')};
            }""")
            if st and st["menu"] > 0: seen_bare.append(st["splash"] > 0 or st["scrim"] > 0)
            await pg2.wait_for_timeout(25)
        check("the menu is never shown before its backdrop is decided",
              all(seen_bare), f"{seen_bare.count(False)} frames of bare menu")
        await pg2.close()

        print("\n== the winner takes a lap of honour ==")
        await pg.evaluate("__hoop.reset()"); await pg.wait_for_timeout(400)
        await pg.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1)")
        await pg.wait_for_timeout(300)
        await pg.evaluate("""
          const h=__hoop; h.players[0].points=12; h.players[1].points=6;
          h.state.clockOn=true; h.state.clock=0.02;
        """)
        await pg.wait_for_timeout(300)
        check("match over with a winner", await pg.evaluate("__hoop.state.winner") == 0)
        ban = await pg.evaluate("""() => {
          const g=document.getElementById('ovBanner');
          const on=[...g.children].filter(i=>i.getAttribute('opacity')==='1');
          return {shown:g.getAttribute('opacity'), which: on.length ? on[0].getAttribute('href') : null,
                  title: document.getElementById('ovTitle').getAttribute('opacity')};
        }""")
        check("player 1's banner is up", ban["shown"] == "1" and "won-1" in (ban["which"] or ""), ban)
        check("the text title steps aside for it", ban["title"] == "0")
        # the winner should pant, then celebrate, then pant again
        phases = []
        for _ in range(90):
            sh = await pg.evaluate("__hoop.players[0].shown && __hoop.players[0].shown[0]")
            if sh and (not phases or phases[-1] != sh): phases.append(sh)
            await pg.wait_for_timeout(100)
        pants = [i for i, x in enumerate(phases) if x == "gameover"]
        celebs = [x for x in phases if x.startswith("celebrate")]
        check("the winner pants", len(pants) >= 1, phases)
        check("...then celebrates", len(celebs) >= 1, phases)
        check("...then goes back to panting", len(pants) >= 2, phases)
        loser = await pg.evaluate("__hoop.players[1].shown && __hoop.players[1].shown[0]")
        # (this loser is the NBA player, who has no panting strip at all, so the
        # test is that he is not celebrating rather than that he is panting)
        check("the loser does not celebrate", not loser.startswith("celebrate"), loser)
        check("...and neither does a winner with nothing to celebrate with",
              await pg.evaluate("__hoop.players[1].overSeq") is None)
        await pg.screenshot(path=f"{OUT}/win.png")

        print("\n== a draw names nobody ==")
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1)")
        await pg.wait_for_timeout(300)
        await pg.evaluate("__hoop.state.clockOn=true; __hoop.state.clock=0.02")
        await pg.wait_for_timeout(300)
        check("no winner on a draw", await pg.evaluate("__hoop.state.winner") is None)
        check("no banner on a draw",
              await pg.evaluate("document.getElementById('ovBanner').getAttribute('opacity')") == "0")
        check("the text title comes back",
              await pg.evaluate("document.getElementById('ovTitle').getAttribute('opacity')") == "1")

        print("\n== the shot clock is back in the top right of the court ==")
        await pg.evaluate("__hoop.reset(); __hoop.setMode(1); __hoop.pick(0,0)")
        await pg.wait_for_timeout(200)
        hud = await pg.evaluate("""() => {
          const r = document.querySelector('#clockHud rect');
          const b = {x:+r.getAttribute('x'), y:+r.getAttribute('y'),
                     w:+r.getAttribute('width'), h:+r.getAttribute('height')};
          const fs = document.querySelector('#fsBtn rect');
          b.fsx = +fs.getAttribute('x');
          b.vis = document.getElementById('clockHud').getAttribute('opacity');
          b.dim = document.getElementById('clockText').getAttribute('opacity');
          return b;
        }""")
        check("clock sits in the court, not the band", hud["y"] + hud["h"] < 640)
        check("clock is in the top right", hud["x"] > 640 and hud["y"] < 100, hud)
        check("clock does not overlap the fullscreen button",
              hud["x"] + hud["w"] <= hud["fsx"], f"{hud['x']+hud['w']} vs {hud['fsx']}")
        check("clock is visible in a match", hud["vis"] == "1")
        check("a held clock is dimmed", float(hud["dim"]) < 1)
        await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(200)
        lit = await pg.evaluate("document.getElementById('clockText').getAttribute('opacity')")
        check("a running clock is not dimmed", float(lit) == 1)
        await pg.evaluate("__hoop.reset()"); await pg.wait_for_timeout(150)
        check("clock is hidden on the menus",
              await pg.evaluate("document.getElementById('clockHud').getAttribute('opacity')") == "0")

        print("\n== badges ==")
        await pg.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,2); __hoop.pick(1,3)")
        await pg.wait_for_timeout(250)

        async def score(n):
            """Drop the ball through the hoop by fiat, credited to player n.

            Everything happens inside one evaluate -- the drop, the step that
            registers it, and the draw -- so the transform that comes back is the
            badge's very first frame, at exactly t=1. Sampling it from the outside
            costs a round trip, and the game's own loop keeps running during it.
            """
            return await pg.evaluate("""(n) => { const s = __hoop.state;
              s.ball.x = 480; s.ball.y = 120; s.ball.vx = 0; s.ball.vy = 400;
              s.ball.rest = false; s.scoredThisShot = false; s.shooter = n; s.owner = null;
              for (let i = 0; i < 60 && !s.scoredThisShot; i++) __hoop.step(1 / 120);
              s.ball.rest = true; s.ball.vy = 0;
              __hoop.render();
              return document.getElementById('badge').getAttribute('transform'); }""", n)

        def parts(t):
            return (float(t.split("rotate(")[1].split(")")[0]),
                    float(t.split("scale(")[1].split(")")[0]))

        async def walk(frames, step):
            """Run the badge animation by hand and read back what it is drawn at."""
            await pg.evaluate("__hoop.state.ball.rest = true; __hoop.state.ball.vy = 0")
            out = []
            for _ in range(frames):
                await pg.evaluate("(h) => { __hoop.step(h); __hoop.render(); }", step)
                t = await pg.evaluate(
                    "document.getElementById('badge').getAttribute('transform')")
                out.append((float(t.split("rotate(")[1].split(")")[0]),
                            float(t.split("scale(")[1].split(")")[0])))
            return out

        art = await pg.evaluate("""() => [...document.getElementById('badge').children]
          .map(im => [im.id, (im.getAttribute('href') || '').split('/').pop(),
                      +im.getAttribute('x'), +im.getAttribute('y'),
                      +im.getAttribute('width')])""")
        names = {a[0]: a[1] for a in art}
        check("all five badge graphics are loaded",
              len(art) == 5 and all(a[1] for a in art), art)
        # The colours are the players' own: blue is player 1's kit and his half of
        # the scoreboard, red is player 2's. Getting these the wrong way round
        # would look like a bug in the scoring, not in the artwork.
        check("blue belongs to player 1 and red to player 2",
              names["bgScore0"] == "score-blue.webp"
              and names["bgScore1"] == "score-red.webp"
              and names["bgWow0"] == "incredible-blue.webp"
              and names["bgWow1"] == "incredible-red.webp", names)
        corner = [a for a in art if a[0] in ("bgSteal", "bgScore0", "bgScore1")]
        check("steal and score sit in the top-left corner",
              all(a[2] < 80 and a[3] < 120 for a in corner), corner)
        # The banner arrives spinning, and at three turns and full size it sweeps
        # 307 px from its own centre -- off the top and left of the stage from the
        # corner, comfortably inside it from the middle.
        wow = [a for a in art if a[0].startswith("bgWow")]
        check("the INCREDIBLE! banner is centred instead",
              all(abs(a[2] + a[4] / 2 - 480) < 1 for a in wow), wow)
        check("nothing is showing to begin with",
              await pg.evaluate("+document.getElementById('badge').getAttribute('opacity')") == 0)

        await pg.evaluate("""() => {
          const [a, b] = __hoop.players;
          a.px = 460; b.px = 500; __hoop.state.stealImmune = 0; __hoop.state.owner = 0;
          a.state = 'DRIBBLE'; b.state = 'IDLE'; b.stealCd = 0;
          __hoop.press(1, 'down'); __hoop.step(1 / 60);
        }""")
        badge = await pg.evaluate("__hoop.badge")
        check("a steal throws up STEAL!",
              badge["art"] == "steal.webp" and not badge["spin"] and badge["t"] > 0.9, badge)
        frames = await walk(24, 1 / 24)
        scales = [f[1] for f in frames]
        peaks = sum(1 for i in range(1, len(scales) - 1)
                    if scales[i] > scales[i - 1] and scales[i] >= scales[i + 1])
        check("it pops three times", peaks == 3, scales)
        check("between 80% and 100%",
              0.79 <= min(scales) <= 0.85 and 0.98 <= max(scales) <= 1.0,
              (min(scales), max(scales)))
        check("it never turns", all(f[0] == 0 for f in frames), frames[:3])
        check("and it is gone after a second",
              (await pg.evaluate("__hoop.badge"))["t"] == 0)
        await pg.wait_for_timeout(120)
        check("nothing is left on screen",
              await pg.evaluate("+document.getElementById('badge').getAttribute('opacity')") == 0)

        first = parts(await score(0))
        b0 = await pg.evaluate("__hoop.badge")
        check("player 1's basket shows the blue SCORE!",
              b0["art"] == "score-blue.webp" and not b0["spin"], b0)
        check("and it starts at 80%, square on",
              first == (0.0, 0.8), first)
        await score(1)
        b1 = await pg.evaluate("__hoop.badge")
        check("player 2's shows the red one",
              b1["art"] == "score-red.webp" and not b1["spin"], b1)

        await pg.evaluate("__hoop.players[0].made = 9")
        firstWow = parts(await score(0))
        w = await pg.evaluate("__hoop.badge")
        check("every tenth basket is INCREDIBLE! instead",
              w["art"] == "incredible-blue.webp" and w["spin"], w)
        # Its very first frame is the whole specification: a tenth of full size,
        # three full turns out.
        check("it comes in at 10% and three full turns out",
              firstWow == (-1080.0, 0.1), firstWow)
        check("...and it is the tenth that gets it, not the ninth",
              await pg.evaluate("__hoop.players[0].made") == 10)
        await score(0)
        check("the eleventh is an ordinary basket again",
              (await pg.evaluate("__hoop.badge"))["art"] == "score-blue.webp",
              await pg.evaluate("__hoop.badge"))
        # Each player counts his own, so one man's tenth is not the other's.
        await pg.evaluate("__hoop.players[1].made = 9")
        await score(1)
        w2 = await pg.evaluate("__hoop.badge")
        check("each player counts his own tenth",
              w2["art"] == "incredible-red.webp" and w2["spin"], w2)

        await pg.evaluate("__hoop.players[0].made = 19")
        await score(0)
        frames = await walk(24, 1 / 24)
        turns = [f[0] for f in frames]
        scales = [f[1] for f in frames]
        check("it never over-rotates", max(turns) <= 0, max(turns))
        check("and lands square at full size",
              turns[-1] == 0 and scales[-1] == 1.0, (turns[-1], scales[-1]))
        # The growth and the turn come off one eased progress, which is what makes
        # three turns land exactly on zero at exactly full size. Checking the
        # relation rather than the values proves it at every frame, whenever the
        # sample happens to fall -- and the game's own loop is still running
        # between these round trips, so *when* is not something to rely on.
        off = max(abs(deg + 1080 * (1 - (k - 0.1) / 0.9)) for deg, k in frames)
        check("scale and turn stay locked together", off < 0.15, off)
        # Half a second in, half a second held: from the twelfth frame of
        # twenty-four onwards nothing moves.
        held = frames[12:]
        check("held at rest for the second half",
              all(f[0] == 0 and f[1] == 1.0 for f in held), held[:3])
        check("then it is gone", (await pg.evaluate("__hoop.badge"))["t"] == 0)

        print("\n== the court comes with the character ==")
        # Each baller has a home court: the gym for the two kids, the arena for
        # the pro, the street for the monkey. Player 1's pick decides it.
        keys = await pg.evaluate("__hoop.chars.map(c => c.key)")
        home = {"monkey": "graffiti", "nba": "nba", "highschooler": "school",
                "zombie": "school"}
        for i, k in enumerate(keys):
            await pg.evaluate(f"__hoop.reset(); __hoop.setMode(1); __hoop.pick(0,{i})")
            await pg.wait_for_timeout(120)
            got = await pg.evaluate("__hoop.court")
            check(f"{k} plays at {home[k]}", got == home[k], got)
        p1 = keys.index("zombie")
        p2 = keys.index("nba")
        await pg.evaluate(f"__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,{p1}); __hoop.pick(1,{p2})")
        await pg.wait_for_timeout(120)
        check("in a two-player match it is player 1 who brings the court",
              await pg.evaluate("__hoop.court") == "school",
              await pg.evaluate("__hoop.court"))

        print("\n== the blank vector stage is not a court any more ==")
        courts = await pg.evaluate("__hoop.courts")
        check("it is not in the list", "vector" not in courts, courts)
        check("and the list is the three paintings", len(courts) == 3, courts)
        # Cycling the whole way round must come back where it started and never
        # land on nothing: the vector stage is reachable only as a load failure.
        start = await pg.evaluate("__hoop.court")
        seen = []
        for _ in range(len(courts)):
            await pg.keyboard.press("KeyC")
            await pg.wait_for_timeout(80)
            seen.append(await pg.evaluate("__hoop.court"))
        check("C cycles through every painted court", sorted(seen) == sorted(courts), seen)
        check("and comes back where it started", seen[-1] == start, (start, seen))
        check("the backdrop is never switched off by cycling",
              await pg.evaluate("document.getElementById('court').getAttribute('opacity')") == "1")
        await pg.keyboard.press("Digit4"); await pg.wait_for_timeout(80)
        check("there is no fourth court to ask for",
              await pg.evaluate("__hoop.court") == start, await pg.evaluate("__hoop.court"))

        print("\n== the court button ==")
        box = await pg.evaluate("""() => {
          const r = document.querySelector('#courtBtn rect');
          const t = document.getElementById('toastBox');
          return {x:+r.getAttribute('x'), y:+r.getAttribute('y'),
                  w:+r.getAttribute('width'), h:+r.getAttribute('height'),
                  op:+r.getAttribute('fill-opacity'), tx:+t.getAttribute('x'),
                  vis: document.getElementById('courtBtn').getAttribute('opacity')};
        }""")
        check("it is in the top left corner", box["x"] < 80 and box["y"] < 80, box)
        check("it is semi-transparent", 0 < box["op"] < 1, box["op"])
        check("it does not sit on top of the toast", box["x"] + box["w"] <= box["tx"], box)
        check("it is there during a match", box["vis"] == "1", box["vis"])
        before = await pg.evaluate("__hoop.court")
        await pg.click("#courtBtn")
        await pg.wait_for_timeout(120)
        after = await pg.evaluate("__hoop.court")
        check("one push moves to the next court", after != before, (before, after))
        check("and it says which one",
              (await pg.evaluate("document.getElementById('toastText').textContent")).lower()
              .endswith(after), await pg.evaluate("document.getElementById('toastText').textContent"))
        await pg.evaluate("__hoop.reset()"); await pg.wait_for_timeout(150)
        check("and it is gone on the menus",
              await pg.evaluate("document.getElementById('courtBtn').getAttribute('opacity')") == "0")

        print("\n== every character stands centred on his card ==")
        await pg.evaluate("__hoop.setMode(2)"); await pg.wait_for_timeout(200)
        cards = await pg.evaluate("""() => [...document.getElementById('selCards').children]
          .map(g => {
            const card = g.firstChild, im = g.children[1];
            const cx = +card.getAttribute('x') + +card.getAttribute('width') / 2;
            const ix = +im.getAttribute('x') + +im.getAttribute('width') / 2;
            return {label: g.children[2].textContent, off: ix - cx, w: +im.getAttribute('width')};
          })""")
        for c in cards:
            check(f"{c['label']} is centred in his box", abs(c["off"]) < 0.13 * c["w"],
                  f"off by {c['off']:.0f}px of {c['w']:.0f}px wide")

        print("\n== the picker shows their real relative sizes ==")
        sizes = await pg.evaluate("""() => {
          const cards = [...document.getElementById('selCards').children].map(g => ({
            label: g.children[2].textContent,
            h: +g.children[1].getAttribute('height')
          }));
          const manifest = {};
          __hoop.chars.forEach(c => manifest[c.label] = c.sequences.dribble_idle[0].h);
          return cards.map(c => ({...c, real: manifest[c.label]}));
        }""")
        ratio = sizes[0]["h"] / sizes[0]["real"]
        for c in sizes:
            check(f"{c['label']} drawn at his real size",
                  abs(c["h"] / c["real"] - ratio) < 0.01,
                  f"{c['h']:.0f}px for a {c['real']:.0f}-unit character")
        nba = next(c for c in sizes if "NBA" in c["label"])
        check("the NBA player is the tallest on the card row",
              all(nba["h"] >= c["h"] for c in sizes), [round(c["h"]) for c in sizes])
        monkey = next(c for c in sizes if "Monkey" in c["label"])
        check("the monkey is the shortest",
              all(monkey["h"] <= c["h"] for c in sizes), [round(c["h"]) for c in sizes])

        print("\n== anchors do not make anyone jitter while dribbling ==")
        anchors = await pg.evaluate("""() => __hoop.chars.map(c => {
            const f = c.sequences.dribble_idle;
            const xs = f.map(fr => fr.footX / fr.w);
            return {key: c.key, spread: Math.max(...xs) - Math.min(...xs),
                    worst: Math.max(...xs.map(x => Math.abs(x - 0.5)))};
          })""")
        for a in anchors:
            check(f"{a['key']}: dribble frames share an anchor", a["spread"] < 0.10,
                  f"spread {a['spread']:.2f} of frame width")
            check(f"{a['key']}: anchored near his own feet", a["worst"] < 0.15,
                  f"{a['worst']:.2f} from centre")

        print("\n== performance (two rigs + the P2 filter) ==")
        await pg.evaluate("__hoop.reset()")
        await pg.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,0)")
        await pg.wait_for_timeout(300)
        fps = await pg.evaluate("""() => new Promise(res => {
          let n=0; const t0=performance.now();
          function f(){ n++; if (performance.now()-t0 < 2000) requestAnimationFrame(f);
                        else res(n/((performance.now()-t0)/1000)); }
          requestAnimationFrame(f);
        })""")
        check("holds 55+ fps", fps > 55, f"{fps:.1f} fps")

        errs2 = [e for e in errs if "favicon" not in e.lower()]
        check("no console errors overall", not errs2, errs2[:6])
        await b.close()

    print("\n" + ("ALL PASS" if not FAILS else f"FAILURES: {FAILS}"))
    sys.exit(1 if FAILS else 0)

asyncio.run(main())
