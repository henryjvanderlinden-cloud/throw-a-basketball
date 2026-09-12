# Throw a Basketball

A 2D, physics-based basketball shooting game. One HTML file, no build step, no
dependencies — open `index.html` in a browser and play.

The basket hangs in the top middle. You control a small basketball guy on the
baseline: dribble, set your angle, charge the throw, and let the physics decide.

## Controls

Every run opens on the character select — pick with <kbd>←</kbd> <kbd>→</kbd> (or
click a card) and start with <kbd>Space</kbd>.

| Key | Dribbling | Aiming |
| --- | --- | --- |
| <kbd>←</kbd> <kbd>→</kbd> | move along the baseline | set the throw angle |
| <kbd>Space</kbd> | pick the ball up and start aiming | hold to charge, release to throw |
| <kbd>R</kbd> | restart, back to character select | restart |
| <kbd>C</kbd> / <kbd>1</kbd>–<kbd>4</kbd> | switch court | switch court |

A dotted line shows where you are aiming. The power meter fills green → yellow →
red while <kbd>Space</kbd> is held; release at the strength you want. After the
shot the ball bounces around live — walk into it and you pick it up automatically.

## Rules

- **3 points** per made basket.
- The **shot clock** starts on your first ever <kbd>Space</kbd> press and resets
  on **every throw**. Let it reach zero and the game is over.
- The clock starts at **10 seconds** and drops by **0.5 s for every 12 points**
  scored, down to a floor of **3 seconds**.

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

## How it works

Everything lives in `index.html`:

- **Rendering** is SVG, manipulated through the DOM each frame. The player is one
  `<g id="player">` moved by `transform`, the ball one `<g id="ballg">` moved by
  translate + rotate.
- **State machine**: `DRIBBLE → AIM → CHARGE → LIVE → (DRIBBLE | OVER)`.
- **Physics** runs in three fixed sub-steps per frame so hard shots cannot tunnel
  through the rim. The ball collides with the floor, walls, ceiling beam, both
  backboard wings, and each rim nub, with separate restitution per surface.
- **Scoring** is a swept test: a basket counts when the ball's centre crosses the
  rim plane downwards, inside the ring.

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

Widening `HOOP.halfW` or raising `SPEED_MIN` makes the game noticeably easier.

## Characters

Four playable characters: **Monkey**, **NBA Player**, **High Schooler**,
**Zombie**. Animation is deliberately a few frames at a handful of frames per
second — the heave that old DOS sports games ran on.

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
| `celebrate` | one-shot | 0.9 s on a made basket |
| `gameover` | loop | 2.5 fps, panting |
| `break_banana`, `break_wave` | one-shot | idle breaks, see below |

The other three still run on the original eight poses, which the build script
maps onto the same sequence names — so the game has one code path, and they get
mirrored for facing while the Monkey never is. Replacing them is a matter of
generating strips; nothing in the game needs to change.

### Idle breaks

Stand still and dribble for 2–4 seconds and the character does something in
character — the Monkey peels a banana, or waves to the crowd. The dribbling hand
keeps the same four positions as the stationary loop throughout, so the ball
never stops bouncing and the break needs no handover frames. Any input cancels
it instantly, and breaks are suppressed under 4 seconds on the shot clock.

### The sprite pipeline

Two stages. Generated strips (one image per sequence, frames side by side — see
[docs/ANIMATION.md](docs/ANIMATION.md)) go in
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

## Development

`window.__hoop` exposes `{ state, step, render, reset, keys, STATE, HOOP }` for
poking at the game from the console or driving it from a headless test.

## Layout

```
index.html                 the whole game
sprites/                   generated - manifest.js + 8 frames per character
artwork/basketball-courts/ court backdrops
artwork/basketball-players/ source poses (input to the build script)
tools/build-sprites.py     regenerates sprites/ from artwork/
```

## Credits

Court and character artwork in `artwork/` is pixel art: an NBA arena, a school
gym and an outdoor graffiti court, and four ballers with eight poses each.
