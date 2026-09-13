#!/usr/bin/env python3
"""What the game loads before the player can see anything.

    python -m http.server 8899        # repo root, another shell
    python tools/test-startup.py

This is the check that would have caught the slow start. The game once opened
sixty-eight files and read about seven megabytes before the first menu appeared
-- all of it in parallel, most of it for screens the player was not looking at.
On a fast disk that is invisible. On a disk where every read is scanned before
it is served it is several seconds of watching the wrong things load, and no
other test in this repo could see it, because none of them measured *when*.

So the thing asserted here is not correctness, it is order: that whatever is on
screen loads on its own, and everything else waits.
"""
import sys, pathlib
from playwright.sync_api import sync_playwright

URL = "http://localhost:8899/index.html"
FILE_URL = "file://" + str(pathlib.Path(__file__).resolve().parent.parent / "index.html")

# The page, the sprite manifest, the inlined effects, and the one painting the
# menu is made of. Anything else in front of the menu is a regression.
MAX_FILES = 5
MAX_KB = 800

fails = []


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ("  " + str(detail) if detail else ""))
    if not ok:
        fails.append(name)


def section(t):
    print("\n== " + t + " ==")


PROBE = """() => {
  const tl = __hoop.audio.timeline;
  const menu = (tl.find(e => e[1] === 'first menu on screen') || [0])[0];
  const res = performance.getEntriesByType('resource');
  const before = res.filter(e => e.responseEnd <= menu);
  const kb = a => Math.round(a.reduce((s, e) => s + (e.encodedBodySize || 0), 0) / 1024);
  return { menuAt: Math.round(menu), files: before.length + 1, kb: kb(before),
           names: before.map(e => e.name.split('/').pop()),
           allFiles: res.length + 1, allKb: kb(res) };
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required", "--mute-audio"])

    section("nothing loads in front of the first menu")
    p = b.new_page(viewport={"width": 1200, "height": 1000})
    errors = []
    p.on("pageerror", lambda e: errors.append(str(e)))
    p.goto(URL)
    p.wait_for_function("window.__hoop")
    p.wait_for_function("document.getElementById('splash').getAttribute('opacity') === '1'",
                        timeout=30000)
    p.wait_for_timeout(4000)
    r = p.evaluate(PROBE)
    print("  (menu on screen at %d ms; %d files / %d KB before it, %d / %d KB in total)"
          % (r["menuAt"], r["files"], r["kb"], r["allFiles"], r["allKb"]))
    check("at most %d files before the menu" % MAX_FILES, r["files"] <= MAX_FILES, r["names"])
    check("at most %d KB before the menu" % MAX_KB, r["kb"] <= MAX_KB, "%d KB" % r["kb"])

    names = " ".join(r["names"])
    check("the court backdrop is not one of them", "court" not in names, r["names"])
    check("no sprite frames are among them",
          not any(n[0].isdigit() and n.endswith(".png") for n in r["names"]), r["names"])
    check("only the base splash frame, not all eight",
          sum(1 for n in r["names"] if n.endswith(".webp")) <= 1, r["names"])
    check("the effects are inlined, not fetched",
          not any("shoe-squeak" in n or "floor-bounce" in n for n in r["names"]), r["names"])

    section("but everything does arrive, in the end")
    for want in ["select.webp", "mode-4.webp", "won-1.webp"]:
        p.wait_for_function(
            "(w) => performance.getEntriesByType('resource').some(e => e.name.endsWith(w))",
            arg=want, timeout=30000)
        check("%s loaded eventually" % want, True)
    check("no page errors", not errors, errors[:2])

    section("the court waits for the menus to be over")
    # The default court is the vector one, which is no file at all, so pick a
    # painted one first. Pressing 2 is how a player does it.
    p.keyboard.press("2")
    p.wait_for_timeout(300)
    p.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1);")
    p.wait_for_timeout(1500)
    href = p.evaluate("document.getElementById('court').getAttribute('href')")
    check("a painted court has a source once a match starts", bool(href), href)
    check("and it is the WebP, not the PNG", bool(href) and href.endswith(".webp"), href)

    section("the same, opened straight off disk")
    f = b.new_page()
    ferrs = []
    f.on("pageerror", lambda e: ferrs.append(str(e)))
    opened = []
    f.on("request", lambda rq: opened.append(rq.url.split("/")[-1]))
    f.goto(FILE_URL)
    f.wait_for_function("window.__hoop")
    f.wait_for_function("document.getElementById('splash').getAttribute('opacity') === '1'",
                        timeout=30000)
    menu_at = f.evaluate(
        "(() => { const t = __hoop.audio.timeline.find(e => e[1] === 'first menu on screen');"
        " return t ? Math.round(t[0]) : -1; })()")
    check("the menu still appears", menu_at >= 0, "%d ms" % menu_at)
    # Resource Timing does not cover file://, so count what Chrome actually asked
    # for instead. The order is the thing under test either way.
    head = [n for n in opened if n.endswith((".png", ".webp", ".js"))][:4]
    check("the base splash frame comes before any other picture",
          "mode-0.webp" in head, head)
    check("no page errors off the filesystem", not ferrs, ferrs[:2])

    b.close()

print("\n" + ("ALL PASS" if not fails else "FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
