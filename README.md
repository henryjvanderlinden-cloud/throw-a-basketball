# Throw a Basketball

A 2D, physics-based basketball shooting game. One HTML file, no build step, no
dependencies — open `index.html` in a browser and play.

The basket hangs in the top middle. You control a small basketball guy on the
baseline: dribble, set your angle, charge the throw, and let the physics decide.
Two can play, sharing one keyboard and one ball.

## Controls

Every run opens on the mode select — one player or two — and then the character
select. Both are painted screens (see *Splash screens* below). In a two-player
game player 1 picks first, then player 2; they may pick the same character.

| | Player 1 | Player 2 |
| --- | --- | --- |
| move / set the angle | <kbd>←</kbd> <kbd>→</kbd> | <kbd>A</kbd> <kbd>D</kbd> |
| pick up, aim, hold to charge, release to throw | <kbd>↑</kbd> | <kbd>W</kbd> |
| steal | <kbd>↓</kbd> | <kbd>S</kbd> |

<kbd>Space</kbd> is a second name for player 1's <kbd>↑</kbd>, but only in a
one-player game: sharing a keyboard it sits far too close to player 2's hand.
<kbd>R</kbd> restarts back to the mode select, <kbd>C</kbd> or
<kbd>1</kbd>–<kbd>4</kbd> switches court, <kbd>F</kbd> toggles fullscreen.

A dotted line shows where you are aiming. The power meter fills green → yellow →
red while the shoot key is held; release at the strength you want. After the
shot the ball bounces around live — walk into it and you pick it up automatically.

### On screen, for a tablet

Both players also have a four-button pad along the bottom of the stage: player 2
on the left, player 1 on the right, matching where <kbd>WASD</kbd> and the arrow
keys sit on a keyboard. Each pad is laid out like the keys themselves — the shoot
key alone on top, the other three in a row beneath it, shoot and steal in the
same column — so there is nothing to translate mid-game. They work for the menus
as well as the game, so an iPad needs no keyboard at all. The pads light up with
whatever is held, keyboard included.

The stage fits itself to the screen height in landscape, so the buttons stay
thumb-sized. The fullscreen button sits top right; Safari on iPhone and iPad has
no element fullscreen, so there the button hides itself — add the page to the
home screen instead and it opens without browser chrome.

## Rules

- **3 points** per made basket.
- The **shot clock** runs only while somebody has the ball. Every throw resets it
  *and holds it*; it starts again when anyone gathers the ball, so the scramble
  for the rebound is free time. Let it reach zero and the game is over. The
  clock sits in the top right corner of the court; it reads `SHOT CLOCK · HELD`
  and goes quiet while it is stopped. The scores live in the control band, each
  above its own player's pad.
- The one exception is the opening possession, which waits for the first shoot
  press rather than starting at the tip-off — so the game does not begin ticking
  before anyone's hands are on the keys.
- The clock starts at **10 seconds** and drops by **0.5 s for every 12 points**
  scored, down to a floor of **3 seconds**. In a two-player game the ramp runs on
  the two scores added together.

### Two players

One ball, one basket, one clock — the clock is shared, so stalling costs you as
much as it costs the other one. Player 1 starts with it. Most points when the
buzzer goes wins; equal is a draw.

**Stealing** is the whole game. Press <kbd>↓</kbd> (or <kbd>S</kbd>) next to an
opponent who is *dribbling* and the ball is yours. Three things bound it:

- **Reach.** 70 px along the baseline, a little wider than the pickup radius.
- **Only while dribbling.** The moment they start aiming they cannot be robbed,
  and shots cannot be blocked. Winding up is safe; walking the ball around is not.
- **No instant steal-back.** Every change of possession — steal, rebound,
  tip-off — protects the ball for 0.9 s. A steal attempt costs the thief 0.5 s
  before they can try again, whether or not it worked, so holding the button
  down is not free. Holding it *does* keep trying, once per cooldown.

A steal does **not** reset the shot clock. Taking the ball off someone late is
supposed to leave you with their problem, not a fresh ten seconds.

Players run through each other; there is no body contact. A loose ball goes to
whoever is nearest, and a dead heat goes to whoever did *not* take the last shot.

## Courts

Four backdrops, cycled with <kbd>C</kbd>:

1. **Vector** — no artwork, pure SVG. Also the automatic fallback if the PNGs
   cannot be loaded (for example when `index.html` is opened on its own).
2. **NBA** — `artwork/basketball-courts/nba.png`
3. **School** — `artwork/basketball-courts/school.png`
4. **Graffiti** — `artwork/basketball-courts/graffiti.png`

The artwork is framed so that when it is drawn 960×720 and top-aligned inside the
960×640 viewBox, the *painted* rim lands on the *play* rim. Any new court should
follow the same framing: 4:3, hoop centred, rim about 24 % of the way down.
Your court choice is remembered in `localStorage`.

## Splash screens

The two menus are paintings with a black panel left in them for the game to draw
into. `splash/` holds them, generated from `artwork/Splash Screens/`:

```
python tools/build-splash.py     # 4:3 PNGs -> splash/*.webp at 1280px
```

The sources are about 3 MB each, which is silly for a game that otherwise fits in
one file, so they come out as WebP — six frames, 2.1 MB the lot.

**The number-of-players screen has five frames.** One base, and four variations
in which a single character does something — a wink, a blink, a point, a shout.
The game sits on the base for 2.4–4.2 s, cuts to a variation for about a second,
cuts back, and picks a different character next time. Because the frames are
identical apart from that one character, a straight swap of the whole picture
reads as movement. That only holds if they are in exact register: the generator
returned one frame at 1447×1087 against the others' 1448×1086, which is enough to
make the entire image jump, so the build resamples every frame of a screen to the
base frame's size and says when it had to.

**The panels are measured, not guessed.** The rectangles in `PANEL` are the
largest solid black region of each painting, expressed as fractions of the image,
so they still land correctly if the art is re-rendered at another size. The
menus lay themselves out inside whichever panel they are on.

**The character select is the v02 layout**, the one with the four characters in a
row along the top, because the plates below can then sit under the faces they
belong to — `SPLASH_CHAR_ORDER` puts them in the painting's left-to-right order
rather than the manifest's. The alternative layout scatters the characters around
a smaller panel, which leaves nothing to line the plates up with.

The paintings are 4:3 and the court is 3:2, so the picture is fitted whole —
nothing of it is ever cropped, which matters because the title runs close to the
top edge — and the slack down each side is filled with the same picture blown up
to cover and dimmed almost to black. It reads as a vignette rather than as two
letterbox bars.

If `splash/` is missing or a frame fails to load, the menus fall back to a plain
dark screen with their own titles, exactly as they looked before. It is
all-or-nothing per set: half a painting is worse than none.

## How it works

Everything lives in `index.html`:

- **Rendering** is SVG, manipulated through the DOM each frame. The player is one
  `<g id="player">` moved by `transform`, the ball one `<g id="ballg">` moved by
  translate + rotate.
- **State machine**: the match runs `MODE → SELECT → PLAY → OVER`, and inside a
  match each player runs `IDLE → DRIBBLE → AIM → CHARGE → IDLE`. Exactly one
  player is ever out of `IDLE`: `g.owner` says which, or `null` while the ball is
  loose. Every change of possession goes through `giveBall()`, which is also the
  one place steal immunity is armed.
- **Physics** runs in three fixed sub-steps per frame so hard shots cannot tunnel
  through the rim. The ball collides with the floor, walls, ceiling beam, both
  backboard wings, and each rim nub, with separate restitution per surface.
- **Scoring** is a swept test: a basket counts when the ball's centre crosses the
  rim plane downwards, inside the ring.
- **Two rigs.** Each player gets its own clone of `#rigTemplate`, its own frame
  `<image>` elements and its own "currently shown" cursor, which is what lets
  both players wear the same character at once.
- **Input** is two sources — keyboard and touch — feeding one set of held flags
  per player, so releasing a pad button cannot cancel a key that is still down.
  A direction counts its keys rather than holding a flag, because <kbd>Space</kbd>
  and <kbd>↑</kbd> share one. Anything that changes the screen under the players'
  hands calls `clearInput()`, and a charge nobody is holding any more winds back
  to the aim rather than firing a throw nobody asked for.

### Tuning

The constants block near the top of the `<script>` is the place to change feel:

| Constant | Effect |
| --- | --- |
| `G` | gravity |
| `SPEED_MIN` / `SPEED_MAX` | throw speed at 0 % and 100 % power |
| `CHARGE_RATE` | how fast the power meter fills |
| `AIM_RATE`, `AIM_MIN`, `AIM_MAX` | aiming speed and angle limits |
| `HOOP.halfW` | ring width — the main difficulty dial |
| `REST_*`, `FRICTION`, `AIR` | bounciness and damping |
| `CLOCK_BASE`, `CLOCK_STEP`, `CLOCK_FLOOR` | shot-clock difficulty ramp |
| `STEAL_DIST` | how close a steal needs |
| `STEAL_IMMUNE`, `STEAL_CD` | protection after a change of possession, and the cost of trying |

Widening `HOOP.halfW` or raising `SPEED_MIN` makes the game noticeably easier.

## Characters

Four playable characters: **Monkey**, **NBA Player**, **High Schooler**,
**Zombie**. Animation is deliberately a few frames at a handful of frames per
second — the heave that old DOS sports games ran on.

They are not all the same size. `CHAR_SCALE` in `build-sprites.py` sets each
one's height against the standing height: the NBA player is the biggest thing on
the court at 1.10, the High Schooler a teenager beside him at 0.97, the Monkey
shortest at 0.88. Normalising everyone to the same *total* height is not the same
as making them the same size — the Monkey stands in a crouch, so matching his
overall height scaled his whole body up until he loomed over the professionals.

The **Monkey** is fully animated, with fourteen sequences:

| Sequence | Kind | Rate |
| --- | --- | --- |
| `dribble_idle` | loop | locked to the ball's bounce |
| `run_dribble_r` / `run_dribble_l` | loop | locked to the bounce; drawn per direction, never mirrored |
| `run_r` / `run_l` | loop | 7 fps, chasing a loose ball |
| `pickup` | one-shot | 0.30 s, scooping it off the floor |
| `turn` | one-shot | 0.18 s, front stance → shooting stance |
| `aim` | loop | 2.6 fps |
| `charge` | *not* a loop | frame chosen by the power meter, holding at its deepest |
| `shot` | one-shot | rise 0.05 s → release 0.27 s → follow-through 0.5 s |
| `celebrate`, `celebrate_pump`, `celebrate_flip` | one-shot | one picked at random per made basket; the handspring lands about one basket in eight and plays faster |
| `gameover` | loop | 2.5 fps, panting |
| `break_banana`, `break_wave` | one-shot | idle breaks, see below |
| `panic` | loop | while the shot clock is at 2s or less and he is standing still — with the ball, locked to the bounce; without it, 6 fps, because the clock is everyone's problem |

The other three still run on the original eight poses, which the build script
maps onto the same sequence names — so the game has one code path, and they get
mirrored for facing while the Monkey never is. Replacing them is a matter of
generating strips; nothing in the game needs to change.

### Player 2's kit

Player 2 wears the same art in red. Nothing is regenerated and no second set of
sprites is stored: the `#kitP2` SVG filter rotates the hue of blue-dominant
pixels only, so the jersey, shorts and shoe flashes turn over while fur, skin,
the gold trim and the white socks stay exactly as drawn. The mask is the alpha
row of an `feColorMatrix` — blue, minus the red and green it beats — sharpened
by a transfer function and clipped to the sprite's own alpha. It costs about a
millisecond a frame.

If the characters are ever regenerated with a second set of jerseys, drop the
`filter` attribute in `makeRig()` and point player 2 at the new art instead.

### Idle breaks

Stand still and dribble for 2–4 seconds and the character does something in
character — the Monkey peels a banana, or waves to the crowd. The dribbling hand
keeps the same four positions as the stationary loop throughout, so the ball
never stops bouncing and the break needs no handover frames. Any input cancels
it instantly, and breaks are suppressed under 4 seconds on the shot clock.

### The sprite pipeline

Two stages. Generated strips (one image per sequence, frames side by side — see
[docs/ANIMATION.md](docs/ANIMATION.md) for the workflow and prompt template, and
[docs/LESSONS.md](docs/LESSONS.md) for why it is shaped that way) go in
`artwork/basketball-players/<Name> poses/`:

```
python tools/slice-strips.py     # strips  -> <Name> frames/<sequence>/NN.png
python tools/build-sprites.py    # frames  -> sprites/ + manifest.js
```

`slice-strips.py` cuts at equal divisions of the width, nudging each cut to the
emptiest nearby column. Cutting on *empty* columns does not work: tails and
swinging arms cross the gaps, and whole frames merge. Where a neighbour still
bleeds across a cut, the fragment is erased by flood-filling from the cut edge
and discarding small blobs — scoped to blobs touching a cut, so a genuinely
detached part of the pose like a thrown banana peel survives.

`build-sprites.py` trims, scales, quantises, and writes the manifest. Two
per-sequence corrections live at the top of it:

- **`SEQ_SCALE`** — each strip is generated separately, so strips drift in scale
  relative to each other even though every frame *within* a strip is consistent.
  No automatic landmark survives the pose changes: silhouette height, shoe width
  and ink area all move with the pose, not just with the scale. So these are
  measured by eye against the standing dribble. Regenerating a strip at a
  matching scale is the real fix; then its entry goes back to 1.0.
- **`BALL_SIDE`** — which side the dribbling hand is on, read off the art rather
  than assumed. The generator put the monkey's dribbling hand on the viewer's
  *left* for the standing poses, not the right the prompt asked for.

Anchoring is per sequence too. A travelling pose (`run_*`) anchors on the cell
midpoint, because its feet are mid-stride and move on purpose. A planted pose
anchors on its own feet, so the character cannot slide sideways through a loop.
The old eight-pose art has no shared frame at all, so it is always anchored on
the feet.

Two quirks of the source art shape both tools: a faint alpha haze over the whole
canvas, so silhouettes need an alpha cut-off rather than a plain bounding box;
and, in the old eight-pose sets, each pose drawn to fill its own canvas, so
those are not in register with one another.

To add a sequence: generate the strip, add a row to `STRIPS` in
`slice-strips.py`, re-run both tools. The game picks up any sequence it
recognises and falls back gracefully when one is missing.

If `sprites/manifest.js` is missing the game skips the picker and falls back to
a plain vector figure, so `index.html` still runs on its own.

### The ball

The ball stays vector — it needs to rotate freely and scale with the physics.
`<g id="ballg">` is positioned entirely by its `transform`, so swapping in an
`<image>` needs no logic changes; `b.spin` already drives the rotation.

## Sound

Music and effects are original, generated by the `tools/build-*` scripts, and
live in `audio/`. The game needs no library for them: one `AudioContext`, a
music bus and an effects bus.

| When | What |
| --- | --- |
| Mode and character screens | *Full Court Pressure*, looped |
| A match | *Overtime Overdrive*, looped |
| The buzzer | the *Victory Lap* sting once, then its loop, four seconds later |
| A basket | net swish |
| Backboard or beam | backboard, at the strength of the hit |
| Rim | the backboard sample, short and high -- there is no rim sample |
| A loose or shot ball landing | floor bounce, at the strength of the hit |
| A dribble | the same bounce, on every bounce, at a third of the volume |
| A wall | the same bounce, quieter still |
| A running player turning round | shoe squeak |

The squeak is the one with a rule behind it: it fires on a **change of
direction while running**, not on starting, stopping, or running. Holding both
direction keys stops a player without ending their run -- that is how a turn is
actually made on a keyboard -- so the run is only forgotten after
`RUN_TURN_GAP` (0.25 s) of standing still.

<kbd>M</kbd> or the speaker button silences everything; the choice is remembered
in `localStorage`. The button is there because a tablet has no <kbd>M</kbd>.

### Two engines, because of how the game is opened

The game is usually opened by double-clicking `index.html`, not served, and
`fetch()` refuses a `file://` URL outright. So there are two paths:

- **Web Audio** (`engine === 'wa'`), chosen when the page is on `http(s)`:
  decoded buffers, sample-accurate looping, the victory hand-off scheduled on
  the audio clock, per-voice gain. This is what GitHub Pages gets.
- **`<audio>` elements** (`engine === 'el'`), chosen for anything else, and
  fallen back to if the context comes up but the bytes never arrive. Three
  elements per effect so a bounce landing on a squeak does not cut it off, a
  volume walked by hand where the gain ramp was, and the victory hand-off on a
  `setTimeout` rather than a schedule. The loop seam is at the browser's mercy
  and the hand-off is a few milliseconds loose; everything is audible.

The protocol check is made once, on the first gesture. In element mode no
`AudioContext` is built at all.

### How it behaves

- **Nothing is created until the player touches something.** A browser will not
  start audio before a gesture, so the game only remembers which track it
  *wants* and starts it on the first key, tap or click. Everything is
  best-effort: a missing file, a refused context, or a browser with no Web Audio
  leaves a silent game and never a broken one.
- **Loading is a ladder, and the music is on the top rung.** Whatever the player
  can hear right now loads alone; everything else queues behind it, in the order
  it will be wanted: the in-game anthem, then one voice of each effect, then the
  victory pair, then the spare voices. In element mode the queue is strictly one
  file at a time and is held shut until the music is actually playing.

  This is not tidiness. Media elements created together all start reading
  together, and the first version created thirty-six of them before asking for
  the music. Where a read is cheap nobody notices; where every read is scanned
  first — a Windows repo folder under ransomware protection is the case that
  found it — the music waits at the back and the game is silent for minutes.

- **`__hoop.audio.timeline`** is a timestamped list of what was chosen and what
  loaded when. It is the first thing to read when the sound is late, because it
  distinguishes a bug from a slow disk.
- **The victory hand-off is scheduled, not fired** (on the Web Audio path). The
  sting is exactly four seconds and the loop is written to begin where it ends,
  so the loop is scheduled at `stingStart + 4` on the audio clock. Waiting for
  an `ended` event would arrive late and leave a hole in the middle of the tune.
- **Tracks loop on the audio engine, not on the media element.** All three are
  written so their reverb tails wrap across the repeat point; only
  sample-accurate looping keeps the seam inaudible.
- **Every effect group has its own debounce** (70 ms for impacts, 180 ms for
  squeaks), on the wall clock rather than the audio clock, because in element
  mode there is no audio clock. A frame runs three physics sub-steps and a ball
  can rattle between the two rim nubs inside one of them.
- Variants are randomised and never repeat twice running.

### The packs

`audio/basketball-natural/` is the pack in use. `tools/build-basketball-sfx.py`
generates a crunchier alternative with the same twelve file names, so swapping
packs is one constant (`SFX_DIR`) -- it is not committed, since only one pack
can be in use at a time.

Each folder also holds previews, a zip, a `score.json` and an 8-bit PCM copy of
every asset. Those are for auditioning and are regenerated by the build scripts,
so they are ignored by git; the game uses the 16-bit containers, which already
have the 8-bit waveform baked in and decode everywhere.

## Development

`window.__hoop` exposes `{ state, players, numPlayers, step, render, reset, keys,
STATE, MS, PS, HOOP, startMatch, press, release, setMode, pick, chars, audio }` for
poking at the game from the console or driving it from a headless test. `press`
and `release` take `(playerIndex, 'left'|'right'|'up'|'down')` and go in through
the same path as a real key, so a test can play the game rather than set its
variables. `setMode(1|2)` and `pick(player, charIndex)` skip the menus.

### Tests

There is a headless harness. It needs Playwright, and it needs the game served
over HTTP rather than opened as a file, because the sprites and splash frames
are fetched:

```
pip install playwright && playwright install chromium
python -m http.server 8899          # from the repo root, in another shell
python tools/test-game.py           # ~140 checks, a few seconds
python tools/fuzz-game.py           # random two-player input, four rounds
python tools/test-audio.py          # music, effects and the events behind them
```

`test-game.py` plays the game through `window.__hoop` — pressing keys and
clicking pads rather than setting variables — and screenshots each stage into a
temp folder (`HOOP_SHOTS=` to put them somewhere else). Point it at another host
with `python tools/test-game.py http://host:port/`.

The checks are about behaviour that has actually broken at least once, not about
coverage: a touch button left stuck down by a screen change, a charge with no way
out of it, a player anchored to one shoe, two splash frames that do not line up,
a clock that runs when it should be held. When one of them fails it is usually
telling the truth — three of them were written after the bug, and each has caught
a regression since.

`fuzz-game.py` bashes both players' controls at random and asserts, every frame,
the things that must hold whatever is pressed: at most one ball-holder, the
holder's state agreeing with who owns the ball, nobody off the court, no NaN, no
negative clock.

`test-audio.py` runs every check over HTTP and then runs a second pass on a
`file://` URL, because those are two different audio engines and the served one
passing says nothing about the one a player actually gets. It runs the browser
with `--autoplay-policy=no-user-gesture-required`,
because a synthetic key press is not a trusted gesture and would leave the
context suspended forever. It patches `createBufferSource` to record which file
each voice actually plays -- and `HTMLMediaElement.play` for the same reason on
the filesystem pass -- so it can check that a basket swishes and a turn squeaks
rather than only that *a* sound happened. Note that the effect debounce
runs on the audio clock -- real time -- while `step()` is simulated time, so a
test driving ninety frames in ten milliseconds will hear one bounce, not three.

## Layout

```
index.html                  the whole game
sprites/                    generated - manifest.js + frames per character
splash/                     generated - the painted menu screens and banners
artwork/basketball-courts/  court backdrops
artwork/basketball-players/ source poses and strips (input to the build)
artwork/Splash Screens/     source paintings for the menus
tools/build-sprites.py      regenerates sprites/ from artwork/
tools/slice-strips.py       cuts generated strips into frames
tools/build-splash.py       regenerates splash/ from artwork/
tools/test-game.py          headless checks - see Tests above
tools/fuzz-game.py          random input, invariants only
tools/test-audio.py         music and effect checks - see Tests above
audio/                      generated - the music and effect packs
tools/build-basketball-natural-sfx.py   regenerates the effect pack in use
tools/build-basketball-sfx.py           the alternative, crunchier pack
tools/build-full-court-soundtrack.py    regenerates the menu music
tools/build-overtime-anthem.py          regenerates the in-game music
tools/build-victory-music.py            regenerates the sting and victory loop
tools/build-arcade-soundtrack.py        an earlier soundtrack, unused
```

## Credits

Court and character artwork in `artwork/` is pixel art: an NBA arena, a school
gym and an outdoor graffiti court, and four ballers with eight poses each.
