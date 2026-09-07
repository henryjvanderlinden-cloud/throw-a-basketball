# Throw a Basketball

A 2D, physics-based basketball shooting game. One HTML file, no build step, no
dependencies — open `index.html` in a browser and play.

The basket hangs in the top middle. You control a small basketball guy on the
baseline: dribble, set your angle, charge the throw, and let the physics decide.

## Controls

| Key | Dribbling | Aiming |
| --- | --- | --- |
| <kbd>←</kbd> <kbd>→</kbd> | move along the baseline | set the throw angle |
| <kbd>Space</kbd> | pick the ball up and start aiming | hold to charge, release to throw |
| <kbd>R</kbd> | restart | restart |
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

### Swapping in sprites

The vector art is deliberately isolated. To move to sprites, replace the shapes
inside `<g id="player">` and `<g id="ballg">` with `<image>` elements — both
groups are positioned entirely by their `transform`, so no game logic changes.
`g.facing` already flips the player, and `b.spin` already drives ball rotation.

## Development

`window.__hoop` exposes `{ state, step, render, reset, keys, STATE, HOOP }` for
poking at the game from the console or driving it from a headless test.

## Credits

Court artwork in `artwork/` is pixel art of an NBA arena, a school gym and an
outdoor graffiti court.
