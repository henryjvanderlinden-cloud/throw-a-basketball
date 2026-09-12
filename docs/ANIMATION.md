# Animation plan

How to think about the character animation, what to generate next, and how to
ask for it.

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

## The sequences

What exists today, and what each one wants.

| Sequence | Kind | Now | Wants | Notes |
| --- | --- | --- | --- | --- |
| Dribble | loop | 2 | **4** | Driven by the ball's bounce, not a timer. 4 frames map onto the bounce as hand-down / rising / hand-up / falling. |
| Turn to shoot | one-shot | 0 | **1–2** | A1 → A2. The single highest-value addition: it is the only hard cut left. |
| Aim hold | loop | 2 | 2 | Fine. Small settle, nothing more. |
| Charge | loop | 2 | **3** | Plays faster as power builds, so the frames should differ in *crouch depth*, not arm position — a coil that visibly tightens. |
| Shot | one-shot | 2 | **4** | load → rise → release (A3) → follow-through. Currently just release + follow, so the throw has no build. |
| Run after a loose ball | loop | reuses dribble | **2** | A real contact/passing run cycle. Right now he walks in his dribbling stance with no ball. |
| Made basket | one-shot | 0 | **2** | Ends on A1. |
| Miss | one-shot | 0 | **1** | Optional; a slump that ends on A1. |

That is ~16 frames per character against today's 8 — but the increase is mostly
in the two places the eye actually goes: the turn and the shot.

### Frame counts

Two-frame loops are the intended look and they hold up. Go past two only where
the motion has a genuine middle: a dribble has a push and a recoil *and* two
travel positions; a shot has a build. An aim hold does not.

## Generating the frames

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
1. [pose]
2. [pose]
...

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

For a loop, add:

```
This row is a seamless loop: frame [N] must flow back into frame 1 with no jump.
```

For a one-shot, add:

```
Frame 1 must match [the character's neutral front stance, arms down]; frame [N]
must settle back into that same stance.
```

### Why each clause is there

| Clause | Failure it prevents |
| --- | --- |
| one image, one row | frames drawn at different scales |
| "exactly the same height … do not zoom" | the model re-composing each pose to fill the frame |
| "share one ground line" | feet floating at different heights |
| "no haze, glow or soft fringe" | the faint alpha wash over the whole canvas in the current art |
| "NOT holding a basketball" | a second ball appearing next to the game's own |
| "identical colours … identical build" | drift in jersey number, skin tone and body shape |

### A worked example — the dribble loop

```
FRAMES, left to right:
1. Standing low in an athletic stance, knees bent, dribbling hand pushed all
   the way down at about hip height, palm facing the floor, fingers spread.
2. The same stance, dribbling hand rising, now halfway between hip and chest,
   palm still down, elbow bending.
3. The same stance, dribbling hand at its highest, just below chest height,
   wrist cocked, weight shifted slightly up.
4. The same stance, dribbling hand dropping back toward the hip, palm down.
```

Frame 1 is the anchor A1. The hand tracks the ball: lowest when the ball is up
at the hand, highest when the ball is down at the floor.

## Checking the result

Before wiring new frames in, run them through the same check the existing set
went through — composite all frames on a common baseline with a vertical centre
line and look at them together. Drift in height, ground line or body width shows
up instantly there and is very hard to see frame by frame.
