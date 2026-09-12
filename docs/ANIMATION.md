# Animation plan

How to think about the character animation, what to generate next, and how to
ask for it.

> **Using this document.** It is a plan, not a prompt. The only part you paste
> into an image generator is the fenced block under [The prompt](#the-prompt),
> with the bracketed parts filled in — **one sequence per prompt**, producing
> one strip image. The sequence table says what to ask for; the worked examples
> show what a filled-in FRAMES list looks like.

## The structural idea: anchors, loops and one-shots

Every sequence is one of two kinds, and they have different rules.

**Loops** run for an unknown length of time and must close back on themselves —
dribbling, holding an aim, running. The last frame has to flow into the first.

**One-shots** play once, triggered by a state change, and have a fixed duration
— the shot, a turn, a celebration. They don't loop; instead they have to *land*
somewhere, because the moment they end the character drops back into a loop.

That handover is the whole problem. If a one-shot ends in a pose that looks
nothing like the first frame of the loop that follows, you get a visible snap.
So the sequences are not designed independently — they're designed around a
small set of shared **anchor poses** that everything starts and ends on:

| Anchor | Pose | Role |
| --- | --- | --- |
| **A1** | front stance, weight low, arms down | hub for everything with the ball in hand |
| **A2** | back stance, squared to the hoop | hub for everything shooting |
| **A3** | full extension, arms overhead | the release point |

A loop's first frame *is* an anchor. A one-shot starts on one anchor and ends on
another. Get the three anchors right and the rest stops fighting you.

This is also why the current set has a visible flaw: there is no transition
between A1 and A2. Turning to shoot is an instant swap, which is the roughest
moment in the game right now. One in-between frame fixes it.

## Facing: draw it, don't mirror it

The game currently mirrors the sprite to turn the character around. That
reverses the jersey number, which is why the number reads backwards half the
time.

Drawing a left-facing and a right-facing version fixes it — but only if it is
done *everywhere*. A number that reads correctly while dribbling and then
reverses the instant he shoots is worse than one that is consistently wrong. So
the policy has to cover every sequence, and the cheapest way to do that is to
make most sequences **not need a direction at all**:

| Sequence group | Facing | Why |
| --- | --- | --- |
| Moving with the ball | **left and right, both drawn** | He is travelling; direction is the point. Also a real run cycle isn't a clean mirror anyway. |
| Standing with the ball — stationary dribble, idle breaks, pick-up | **square to camera, one version** | He isn't going anywhere. Nothing to mirror, number always right. |
| Aiming, charging, shooting | **squared to the hoop, one version** | The dotted line already shows where he is aiming; the body doesn't need to. |

That leaves exactly one sequence pair that needs doubling, and removes
horizontal mirroring from the game entirely.

**Consequence for the code:** once nothing is mirrored, the ball can no longer
be positioned as `px ± offset`. Each sequence needs its ball attachment point
stored in the manifest — ideally per frame, so the dribbling hand sits exactly
on the ball right through the loop instead of approximately.

## The sequences

What exists today, and what each one wants.

| Sequence | Kind | Now | Wants | Notes |
| --- | --- | --- | --- | --- |
| **Stationary dribble** | loop | — | **4** | Feet planted, weight shifting. Driven by the ball's bounce, not a timer. |
| **Run-dribble, left** | loop | — | **4** | Legs actually running, hand pushing the ball. |
| **Run-dribble, right** | loop | — | **4** | Drawn, not mirrored. |
| **Idle break** | one-shot | — | **2 × 4** | The signature move. See below. |
| **Pick up off the floor** | one-shot | — | **3** | Bend, gather, rise. Ends on the stationary dribble's first frame. |
| Turn to shoot | one-shot | 0 | **2** | A1 → A2. The only hard cut left in the game. |
| Aim hold | loop | 2 | 2 | Fine as is. A settle, nothing more. |
| Charge | loop | 2 | **3** | Plays faster as power builds, so frames should differ in *crouch depth*, not arm position — a coil that visibly tightens. |
| Shot | one-shot | 2 | **4** | load → rise → release (A3) → follow-through. Today it is just release + follow, so the throw has no build. |
| Run without the ball | loop | reuses dribble | **2 × 2** | Chasing a loose ball. Distinct from run-dribble: no hand pushing down, arms pumping. Left and right. |
| Made basket | one-shot | 0 | **2 + 3 + 6** | Three of them, picked at random so scoring does not always look the same: arms overhead, a low fist pump, and a rare back handspring. All end on A1. Duration comes from the frame count, not a fixed timer, and any movement cancels — chasing the rebound beats showboating. |
| Shot-clock panic | loop | 0 | **4** | Grimacing and jabbing a finger at the clock, under 2 seconds. Built like an idle break — the dribbling hand keeps its cycle, the other hand does the business — so it needs no handover. |
| Game over | loop | 0 | **2** | Hands on knees, panting, when the clock hits zero — feet and hands pinned, only the shoulders and head move, at about 2.5 fps. Right now the overlay just appears over a dribbling character. |

Roughly 40 frames per character, against today's 8.

### Frame counts

Two-frame loops are the intended look and they hold up. Go past two only where
the motion has a genuine middle: a run cycle has contact and passing positions;
a dribble has a push, a recoil and two travel positions; a shot has a build. An
aim hold does not.

**The frames must differ enough to read.** In a two-frame loop the difference
between the frames *is* the animation. This is why the NBA player and the zombie
dribble better than the high schooler today — their two stances differ clearly
in arm position, while his are nearly the same pose. Ask for exaggerated
differences, not subtle ones.

## Idle breaks

Every so often during the stationary dribble, the character does something in
character: waving to the crowd, spinning the ball on a finger, the monkey
peeling and eating a banana, the zombie's arm falling off and being
reattached.

Rules that make these land:

- **Two per character, not one.** A single break becomes wallpaper the third
  time you see it. Two, picked at random, stay surprising for much longer.
- **Long, jittered interval.** Somewhere around 8–15 seconds of continuous
  stationary dribbling, randomised. A fixed timer reads as mechanical.
- **Interruptible.** Any input — moving, pressing space — drops straight back to
  the stationary loop. The break must never cost the player a moment of control,
  especially with a shot clock running.
- **Never while the clock is low.** Suppress them under about 4 seconds; a
  character mugging for the crowd while the clock runs out is a bad joke.
- **Starts and ends on the loop's first frame**, like any one-shot.

They also solve the character select screen, which is currently four static
figures. Playing each character's signature move on their card is the most
natural possible way to show off who they are.

## Free with no new art

Two things worth doing that need no frames at all:

- **Speed the loops up as the shot clock drops.** Scaling the dribble and aim
  rates by up to ~1.4× under 4 seconds makes the character look hurried.
- **Slow the release.** Holding the release pose ~50 ms longer on a made basket
  than a miss gives a made shot a beat of weight.

## Suggested order

40 frames per character × 4 characters is a lot of generation, so phase it by
how often the player actually sees each thing:

1. **Stationary dribble, run-dribble L/R, pick-up** (15 frames). The states that
   are on screen almost all the time.
2. **Turn to shoot, shot build** (6 frames). The moment of drama, and the fix
   for the only hard cut in the game.
3. **Idle breaks, celebration, game over** (12 frames). Personality — and where
   the characters stop being reskins of each other.
4. **Run without the ball** (4 frames). Least visible; happens only while
   chasing a rebound.

Each phase is independently shippable, and the build script and manifest can
absorb them one at a time.

## Generating the frames

### The workflow

For each sequence, in order. Steps 1–4 are one sequence's worth of work; do a
whole one end-to-end before starting the next.

1. **Write the prompt** from the template below. Fill in the frame list from the
   sequence table; paste the character's SUBJECT block in verbatim.
2. **Generate**, attaching a reference frame of the character. Re-roll on the
   spot if the frame count is wrong — everything downstream assumes it.
3. **Slice**: `python tools/slice-strips.py <sequence>` after adding a row to
   `STRIPS`. The tool reports the frame count, the ground-line spread and any
   bleed it cleaned. A ground-line spread over ~10px means re-roll.
4. **Look at it on a baseline** before anything else — all frames composited on
   a common floor line with a standing-height line. Scale drift and sideways
   slide are invisible frame by frame and obvious here.
5. **Build**: `python tools/build-sprites.py`, then check the new sequence
   against the others at game size.
6. **Play it**, then keep or re-roll. Re-rolls are a coin flip; generate a
   couple and keep the best rather than refining the prompt forever.

### The calibration frame

The one piece of manual work left in this pipeline is `SEQ_SCALE` — a measured
correction per sequence, because separately generated strips drift in scale
against each other by as much as 40%.

**This is avoidable, and future strips should avoid it.** Ask for one extra
frame at the *start* of every strip: the character's plain neutral standing
pose, identical in every strip. Then every strip contains the same pose, and the
scale correction is no longer a judgement call — it is the ratio between that
frame's height here and its height in the reference strip, which a tool can
compute exactly.

It costs one frame per generation and buys three things: automatic scaling, a
registration anchor with feet definitely on the floor, and an instant read on
whether the character's identity has drifted.

**The tools already support it.** Add `True` as a fourth element of the strip's
row in `STRIPS`:

```python
("aim", "Monkey_sequence_006.png", 2, True),   # 3 cells: calibration + 2 frames
```

The slicer then expects one extra cell, writes it as `00.png` and leaves it out
of the animation; `build-sprites.py` measures it and scales that sequence
exactly, ignoring `SEQ_SCALE`. Verified on a synthetic strip drawn 25%
oversized: it comes back at the correct standing height with no manual figure.

Sequences without a calibration frame keep using `SEQ_SCALE`, so this can be
adopted one strip at a time as sequences get regenerated.

### The one change that matters most

**Ask for all frames of a sequence in a single image, as one horizontal strip.**

The current art was generated as eight separate images, and it shows: each pose
was drawn to fill its own canvas, so the eight are at different scales and share
no ground line. `tools/build-sprites.py` works around this by aligning on the
feet and accepting that arms-up poses come out slightly smaller.

Generated as one strip, the model keeps scale, proportion, palette and identity
consistent across the row, because it is drawing them side by side in a single
picture. Registration stops being a problem instead of being compensated for.

The build script currently expects one file per pose; slicing a strip into
frames is a small addition once there is a strip to test against.

### The prompt

Fill in the bracketed parts. Keep everything else — each clause is there to head
off a specific failure.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: [a lanky teenage basketball player, blue sleeveless jersey with a
yellow number 12, blue shorts, white high-top sneakers, messy brown hair].
The same character in every frame: identical colours, identical proportions,
identical build.

LAYOUT: one horizontal row of [N] frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame — do not zoom, crop,
recompose or rescale between frames. All frames share one ground line: the
soles of the feet touch the same horizontal line in every frame[, except
frame N where the character is airborne].

VIEW: [front view, facing the viewer / back view, seen from behind].

FRAMES, left to right:
1. CALIBRATION POSE: standing straight upright, feet shoulder-width apart, arms
   hanging relaxed at his sides, facing the viewer. This exact pose appears as
   the first frame of every sheet in this set and must be drawn identically
   every time.
2. [pose]
3. [pose]
...

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

Remember to ask for N+1 frames in LAYOUT when you include the calibration frame,
and to name the *animation's* first frame as frame 2.

For a loop, add:

```
This row is a seamless loop: frame [N] must flow back into frame 1 with no jump.
```

For a one-shot, add:

```
Frame 1 must match [the character's neutral front stance, arms down]; frame [N]
must settle back into that same stance.
```

### Working with it in practice

- **One sequence per prompt.** Never ask for the whole plan at once. Each
  generation produces one strip; the sequence table is a list of generations to
  run, not a single request.
- **Keep the strip short.** Four frames in a row is reliable. Past six, quality
  falls off and frames start drifting in scale — the exact problem the strip is
  there to avoid.
- **The SUBJECT block is fixed per character.** Write it once, paste the
  identical text into every prompt for that character. Any rewording is a chance
  for the jersey number, skin tone or build to drift between sequences.
- **Attach a reference image if the tool accepts one.** Handing it an existing
  frame of that character holds identity far better than describing them, and
  lets the SUBJECT line stay short.
- **Expect to re-roll.** Scale drift and a wandering ground line are the usual
  failures. Both are obvious in the check described at the end of this document,
  and neither is worth fixing by hand — regenerate.
- **Generate one character's sequence first and wire it in** before doing the
  other three. A problem found after 160 frames is expensive.

### A complete, ready-to-send example

The monkey's stationary dribble, with every bracket filled in:

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: an anthropomorphic monkey basketball player with brown fur, shaggy
darker head fur, a long curling tail, wearing a blue sleeveless basketball
jersey with a yellow number 7, blue shorts with white and yellow trim, and
blue-and-white high-top sneakers. The same character in every frame: identical
colours, identical proportions, identical build. The tail curls clear of the
body and stays roughly the same shape in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame — do not zoom, crop,
recompose or rescale between frames. All frames share one ground line: the
soles of the feet touch the same horizontal line in every frame.

VIEW: front view, facing the viewer, squared to camera.

FRAMES, left to right:
1. Standing low in an athletic stance, knees bent, feet planted shoulder-width
   apart, right hand pushed all the way down at about hip height, palm facing
   the floor, fingers spread.
2. The same planted stance, weight rising slightly, right hand halfway between
   hip and chest, palm still down, elbow bending.
3. The same planted stance, standing tallest, right hand at its highest just
   below chest height, wrist cocked.
4. The same planted stance, settling back down, right hand dropping toward the
   hip, palm down.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.
The feet do not move at any point.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

### Why each clause is there

| Clause | Failure it prevents |
| --- | --- |
| one image, one row | frames drawn at different scales *within* a sequence |
| the calibration frame | sequences drawn at different scales *from each other* |
| "exactly the same height … do not zoom" | the model re-composing each pose to fill the frame |
| "share one ground line" | feet floating at different heights |
| "no haze, glow or soft fringe" | the faint alpha wash over the whole canvas in the current art |
| "NOT holding a basketball" | a second ball appearing next to the game's own |
| "identical colours … identical build" | drift in jersey number, skin tone and body shape |

### A worked example — the stationary dribble loop

```
VIEW: front view, facing the viewer, squared to camera.

FRAMES, left to right:
1. Standing low in an athletic stance, knees bent, feet planted shoulder-width
   apart, right hand pushed all the way down at about hip height, palm facing
   the floor, fingers spread.
2. The same planted stance, weight rising slightly, right hand halfway between
   hip and chest, palm still down, elbow bending.
3. The same planted stance, standing tallest, right hand at its highest just
   below chest height, wrist cocked.
4. The same planted stance, settling back down, right hand dropping toward the
   hip, palm down.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.
The feet do not move at any point.
```

Frame 1 is the anchor A1. The hand tracks the ball: lowest when the ball is up
at the hand, highest when the ball is down at the floor.

### A worked example — the run-dribble, moving right

```
VIEW: three-quarter view, the character running toward the right of frame,
chest turned slightly toward the viewer so the jersey number stays readable.

FRAMES, left to right:
1. Right leg forward and planted, left leg trailing behind, right hand pushed
   down at hip height pushing the ball, left arm swinging back.
2. Mid-stride, trailing leg swinging through under the body, right hand rising
   to chest height, torso leaning slightly forward.
3. Left leg forward and planted, right leg trailing, right hand pushed down
   again at hip height, left arm swinging forward.
4. Mid-stride the other way, leading leg swinging through, right hand rising.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.
```

The left-facing version is a separate generation with the same frame
descriptions and the direction reversed — not a mirror of this one.

## What this asks of the code

The current manifest is a flat list of eight frames plus a map of state → pose
numbers. Forty frames across a dozen named sequences wants a different shape:

- Sequences become first-class: a name, a kind (`loop` / `once`), an ordered
  frame list, and a duration or a driver (the dribble is driven by the ball, the
  charge by the power meter).
- Each frame carries its own ball attachment point, so the ball follows the hand
  instead of being placed at a fixed offset.
- One-shots declare what they return to, so the handover is data rather than
  something spelled out in the animation code.

Worth doing as part of phase 1, while there are still few enough sequences that
the migration is small.

## Checking the result

Before wiring new frames in, run them through the same check the existing set
went through — composite all frames on a common baseline with a vertical centre
line and look at them together. Drift in height, ground line or body width shows
up instantly there and is very hard to see frame by frame.
