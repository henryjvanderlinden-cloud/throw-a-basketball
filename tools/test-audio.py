#!/usr/bin/env python3
"""Audio integration checks. Serve the repo over HTTP first:

    python -m http.server 8899        # repo root, another shell
    python tools/test-audio.py

Runs the browser with autoplay unlocked, because a synthetic key event is not
a trusted gesture and would leave the AudioContext suspended forever.
"""
import sys, time, pathlib
from playwright.sync_api import sync_playwright

URL = "http://localhost:8899/index.html"
fails = []


# Records which decoded clip each Web Audio voice actually plays, so a check can
# say that a basket swished rather than only that a sound happened.
SFX_PROBE = """() => {
  window.__sfxLog = [];
  const proto = (window.AudioContext || window.webkitAudioContext).prototype;
  const make = proto.createBufferSource;
  proto.createBufferSource = function () {
    const s = make.call(this);
    const start = s.start.bind(s);
    s.start = function () {
      const clips = __hoop.audio.clipmap;
      for (const u in clips) if (clips[u] === s.buffer) { __sfxLog.push(u.split('/').pop()); break; }
      return start.apply(null, arguments);
    };
    return s;
  };
}"""


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ("  " + str(detail) if detail else ""))
    if not ok:
        fails.append(name)


def section(t):
    print("\n== " + t + " ==")


with sync_playwright() as pw:
    b = pw.chromium.launch(args=[
        "--autoplay-policy=no-user-gesture-required",
        "--mute-audio",
    ])
    page = b.new_page(viewport={"width": 1200, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(URL)
    page.wait_for_function("window.__hoop && window.__hoop.audio")

    section("the music loads without waiting for the player")
    # Loading audio needs no gesture; only playing it does. Conflating the two is
    # what kept the music arriving seconds late -- it was not even asked for
    # until a key was pressed, by which time the queue was deep into something
    # else and could not be preempted.
    page.wait_for_function("__hoop.audio.context", timeout=15000)
    check("a context is built as soon as there is a menu, gesture or not",
          page.evaluate("__hoop.audio.context") is not None)
    check("the menu track is the one it wants",
          page.evaluate("__hoop.audio.wanted") == "menu")
    page.wait_for_function(
        "__hoop.audio.loaded.some(u => u.indexOf('full-court') >= 0)", timeout=30000)
    check("and it is fetched before anybody has pressed anything", True)

    section("the first gesture unlocks it")
    # And the gesture now has somewhere to happen: the start gate exists so that
    # the player presses something before the first menu, which is what the
    # browser wants before it will make a sound.
    check("there is a start gate to press", page.evaluate("__hoop.gate"))
    page.click("#startGate")
    check("pressing it takes the gate away", not page.evaluate("__hoop.gate"))
    page.wait_for_function("__hoop.audio.context && __hoop.audio.context.state === 'running'",
                           timeout=5000)
    check("context is running", True, page.evaluate("__hoop.audio.context.state"))
    check("menu music is playing", page.evaluate("__hoop.audio.track") == "menu")

    section("playing keeps playing")
    # ensureAudio() runs on every key press and every tap, not just the first,
    # and for one commit applyWantedTrack() nulled curTrack each time -- so every
    # keystroke restarted the music from the top with a fresh fade. Thirteen key
    # presses, thirteen restarts, and it sounded exactly as bad as that reads.
    before = len([t for t in page.evaluate("__hoop.audio.timeline")
                  if t[1].startswith("playing")])
    for _ in range(8):
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(80)
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(80)
    page.wait_for_timeout(400)
    after = len([t for t in page.evaluate("__hoop.audio.timeline")
                 if t[1].startswith("playing")])
    check("sixteen key presses do not restart the track", after == before,
          "started %d more time(s)" % (after - before))
    check("and only one music voice is alive", page.evaluate("__hoop.audio.voices") == 1,
          page.evaluate("__hoop.audio.voices"))

    section("every clip the game references decodes")
    page.wait_for_function("__hoop.audio.loaded.length >= 12", timeout=20000)
    want = page.evaluate("""() => {
      const a = __hoop.audio, out = [];
      for (const g of ['squeak','board','swish','bounce'])
        for (let i = 1; i <= 3; i++)
          out.push(a.SFX_DIR + g.replace('squeak','shoe-squeak').replace('board','backboard')
                   .replace('swish','net-swish').replace('bounce','floor-bounce')
                   + '-0' + i + '.wav');
      return out;
    }""")
    page.wait_for_function(
        "__hoop.audio.loaded.filter(u => u.indexOf('full-court') >= 0).length === 1", timeout=30000)
    loaded = page.evaluate("__hoop.audio.loaded")
    for u in want:
        check("decoded " + u.split("/")[-1], u in loaded)
    check("decoded the menu anthem",
          any("full-court-pressure" in u for u in loaded))

    section("the track follows the screen")
    page.evaluate("__hoop.setMode(2)")
    page.evaluate("__hoop.pick(0, 0)")
    page.wait_for_timeout(200)
    check("still on the menu track while player 2 is picking",
          page.evaluate("__hoop.audio.track") == "menu",
          page.evaluate("__hoop.audio.track"))
    page.evaluate("__hoop.pick(1, 1)")
    page.wait_for_timeout(200)
    check("tip-off switches to the in-game anthem",
          page.evaluate("__hoop.audio.track") == "play",
          page.evaluate("__hoop.audio.track"))

    section("the buzzer starts the victory sequence")
    page.evaluate("__hoop.state.clockOn = true; __hoop.state.clock = 0.001;")
    page.evaluate("__hoop.step(0.05)")
    page.wait_for_timeout(300)
    check("game over plays the victory music",
          page.evaluate("__hoop.audio.track") == "victory",
          page.evaluate("__hoop.audio.track"))
    page.wait_for_function(
        "__hoop.audio.loaded.filter(u => u.indexOf('victory') >= 0).length === 2", timeout=30000)
    page.wait_for_timeout(300)
    check("both victory assets decoded", True)
    # The sting and the loop are scheduled together, the loop four seconds out,
    # so both voices exist on the music bus straight away.
    check("sting and loop are both scheduled at once",
          page.evaluate("__hoop.audio.voices") == 2,
          page.evaluate("__hoop.audio.voices"))

    section("the right clip fires for the right event")
    page.evaluate("__hoop.reset(); __hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1);")
    page.evaluate(SFX_PROBE)

    def log_after(js, frames=1, dt="1/60"):
        page.evaluate("__sfxLog = []")
        page.evaluate(js)
        page.evaluate("(n) => { for (let i = 0; i < n; i++) __hoop.step(%s); }" % dt, frames)
        page.wait_for_timeout(60)
        return page.evaluate("__sfxLog")

    heard = log_after("__hoop.press(0,'right')", frames=30)
    check("running alone does not squeak", not any("squeak" in c for c in heard), heard)

    heard = log_after("__hoop.release(0,'right'); __hoop.press(0,'left')", frames=4)
    check("turning round while running squeaks",
          any("shoe-squeak" in c for c in heard), heard)

    # The per-group debounce runs on the audio clock, which is real time, while
    # step() is simulated time -- ninety frames driven from here pass in a few
    # milliseconds and all but the first would be swallowed. Hence the pauses.
    page.evaluate("__hoop.release(0,'left')")
    heard = []
    for _ in range(3):
        page.wait_for_timeout(150)
        heard += log_after("void 0", frames=30)
    check("dribbling bounces the ball on the floor",
          sum(1 for c in heard if "floor-bounce" in c) >= 2, heard)

    # Straight down through the middle of the ring, from above the rim.
    heard = log_after("""() => {
      const s = __hoop.state, H = __hoop.HOOP;
      s.owner = null; s.shooter = 0; s.scoredThisShot = false;
      s.ball.x = H.cx; s.ball.y = H.rimY - 30; s.ball.vx = 0; s.ball.vy = 600;
      __hoop.players[0].lockout = 5; __hoop.players[1].lockout = 5;
    }""", frames=8)
    check("a made basket swishes the net", any("net-swish" in c for c in heard), heard)

    # Flat into the left backboard wing.
    heard = log_after("""() => {
      const s = __hoop.state;
      s.owner = null; s.shooter = 0; s.scoredThisShot = true;
      s.ball.x = 340; s.ball.y = 95; s.ball.vx = 900; s.ball.vy = 0;
      __hoop.players[0].lockout = 5; __hoop.players[1].lockout = 5;
    }""", frames=10)
    check("the backboard is heard", any("backboard" in c for c in heard), heard)

    section("restarting comes back to the menu track")
    page.evaluate("__hoop.reset()")
    page.wait_for_timeout(200)
    check("back on the menu track", page.evaluate("__hoop.audio.track") == "menu",
          page.evaluate("__hoop.audio.track"))

    section("the mute button has a corner of its own")
    box = page.evaluate("""() => {
      const r = n => { const b = document.getElementById(n).getBoundingClientRect();
                       return {x: b.x, y: b.y, w: b.width, h: b.height}; };
      return {mute: r('muteBtn'), fs: r('fsBtn'), clock: r('clockHud')};
    }""")
    def clear(a, b):
        return (a["x"] + a["w"] <= b["x"] + 0.5 or b["x"] + b["w"] <= a["x"] + 0.5
                or a["y"] + a["h"] <= b["y"] + 0.5 or b["y"] + b["h"] <= a["y"] + 0.5)
    check("mute does not overlap the fullscreen button", clear(box["mute"], box["fs"]), box)
    check("mute does not overlap the shot clock", clear(box["mute"], box["clock"]), box)

    section("mute")
    page.keyboard.press("m")
    page.wait_for_timeout(100)
    check("M mutes", page.evaluate("__hoop.audio.muted") is True)
    check("mute survives a reload", True)
    page.reload()
    page.wait_for_function("window.__hoop && window.__hoop.audio")
    check("still muted after a reload", page.evaluate("__hoop.audio.muted") is True)
    page.evaluate("__hoop.audio.setMute(false)")
    check("and unmutes again", page.evaluate("__hoop.audio.muted") is False)

    section("a missing audio folder is silent, not broken")
    p2 = b.new_page()
    p2errs = []
    p2.on("pageerror", lambda e: p2errs.append(str(e)))
    p2.route("**/audio/**", lambda route: route.abort())
    p2.goto(URL)
    p2.wait_for_function("window.__hoop && window.__hoop.audio")
    p2.keyboard.press("ArrowLeft")
    p2.wait_for_timeout(1200)
    p2.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1);")
    for _ in range(60):
        p2.evaluate("__hoop.step(1/60)")
    check("no page errors with every audio file blocked", not p2errs, p2errs[:3])
    check("the game still reaches a match", p2.evaluate("__hoop.state.ms") == "PLAY")

    check("no console errors overall", not errors, errors[:3])

    # The game is normally played by opening index.html, not by serving it, and
    # fetch() will not read a file:// URL -- so the whole Web Audio path is
    # silent there. This is the check that says whether a player hears anything.
    section("opened straight off disk, not served")
    f = b.new_page()
    ferrs = []
    f.on("pageerror", lambda e: ferrs.append(str(e)))
    # Installed BEFORE the page script runs, not after: the menu track is now
    # fetched as soon as there is a menu, without waiting for a gesture, so a
    # probe injected after load would miss the very request it is checking for.
    f.add_init_script("""
      // Which files are requested, in order. Media elements created at once all
      // read at once, and on a slow disk the music ends up waiting behind the
      // rest -- which cost minutes of silence once.
      window.__openLog = [];
      const A = window.Audio;
      window.Audio = function (u) { __openLog.push(String(u).split('/').pop()); return new A(u); };
      window.__playLog = [];
      const play = HTMLMediaElement.prototype.play;
      HTMLMediaElement.prototype.play = function () {
        __playLog.push((this.currentSrc || this.src || '').split('/').pop());
        return play.apply(this, arguments);
      };
    """)
    f.goto("file://" + str(pathlib.Path(__file__).resolve().parent.parent / "index.html"))
    f.wait_for_function("window.__hoop && window.__hoop.audio")
    # Wait for the gate to be up before pressing: it does not appear until the
    # curtain lifts, and a key pressed before then is not the gesture that
    # dismisses it.
    f.wait_for_function("__hoop.gate", timeout=30000)
    f.keyboard.press("ArrowLeft")        # the gate, off the filesystem too
    f.wait_for_timeout(800)
    check("the start gate is dismissed here as well", not f.evaluate("__hoop.gate"))
    check("the music falls back to <audio> elements",
          f.evaluate("__hoop.audio.via") == "element", f.evaluate("__hoop.audio.via"))
    # The effects are inlined, so they reach Web Audio even here -- which is the
    # only way an effect lands on the frame that fired it.
    check("but a context is still built, for the effects",
          f.evaluate("__hoop.audio.context") is not None)
    check("and the effects are decoded into it",
          f.evaluate("__hoop.audio.loaded.filter(u => u.indexOf('bounce') >= 0).length") == 3,
          f.evaluate("__hoop.audio.loaded.length"))
    # The menu track is synthesised from its score, so it plays through Web Audio
    # even here -- no media element, and a sample-accurate loop off the filesystem.
    # Wait for the voice, not for the track name: curTrack is set the moment the
    # track is *asked* for, which on this path is while the synth is still
    # rendering it. Waiting on the name raced the render and failed about one run
    # in three.
    f.wait_for_function("__hoop.audio.voices >= 1", timeout=60000)
    check("the menu music actually starts", True, "track=" + f.evaluate("__hoop.audio.track"))
    check("and it is a Web Audio voice, not an element",
          f.evaluate("__hoop.audio.voices") >= 1, f.evaluate("__hoop.audio.voices"))
    check("rendered rather than loaded",
          any("rendered menu" in t[1] for t in f.evaluate("__hoop.audio.timeline")),
          [t[1] for t in f.evaluate("__hoop.audio.timeline") if "render" in t[1]])
    opened = f.evaluate("__openLog")
    check("no audio file is fetched for it at all",
          not any("full-court" in c for c in opened), opened[:6])
    check("no effect is ever fetched as a file",
          not any(k in c for c in opened
                  for k in ("squeak", "bounce", "swish", "backboard")), opened[:6])

    f.evaluate("__hoop.setMode(2); __hoop.pick(0,0); __hoop.pick(1,1);")
    f.wait_for_function("__hoop.audio.track === 'play'", timeout=60000)
    check("the in-game anthem actually starts", True, "track=" + f.evaluate("__hoop.audio.track"))

    # The menu track has to stop when the anthem starts. It once did not: the
    # fade branched on musicVia, which is 'element' here, so it emptied the list
    # of media elements -- which is empty -- and left the synthesised menu voice
    # running underneath the anthem. One more track playing at once per screen
    # change, and the player hears all of them.
    # Wait for the anthem to actually be sounding before counting: until its
    # render lands there are legitimately no voices at all.
    f.wait_for_function("__hoop.audio.voices >= 1", timeout=60000)
    f.wait_for_timeout(600)
    check("and the menu track is gone, not still playing under it",
          f.evaluate("__hoop.audio.voices") == 1, f.evaluate("__hoop.audio.voices"))

    # Effects are Web Audio here too, not elements, so they are counted the same
    # way as on the served pass.
    f.evaluate(SFX_PROBE)
    heard = []
    for _ in range(4):
        f.wait_for_timeout(160)
        f.evaluate("__sfxLog = []; for (let i = 0; i < 30; i++) __hoop.step(1/60)")
        heard += f.evaluate("__sfxLog")
    check("effects actually play, through Web Audio",
          any("floor-bounce" in c for c in heard), heard)

    f.evaluate("__playLog = []")
    f.evaluate("__hoop.state.clockOn = true; __hoop.state.clock = 0.001; __hoop.step(0.05);")
    f.wait_for_timeout(300)
    check("the victory sting actually starts",
          any("victory-sting" in c for c in f.evaluate("__playLog")), f.evaluate("__playLog"))
    # And the anthem stops for it. The victory music is a file, so it is the
    # other way round from the switch above: a Web Audio voice has to be faded
    # out by the element path's fade.
    f.wait_for_timeout(600)
    check("the anthem stops for it",
          f.evaluate("__hoop.audio.voices") == 0, f.evaluate("__hoop.audio.voices"))
    check("no page errors off the filesystem", not ferrs, ferrs[:3])

    b.close()

print("\n" + ("ALL PASS" if not fails else "FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
