# Lessons

What we learned building the sprite pipeline, including the things that did not
work. [ANIMATION.md](ANIMATION.md) says what to *do*; this says why, and records
the dead ends, which are the part that leaves no trace in the finished code.

## Generating the art

**Generate a whole sequence as one strip, in one image.** This is the single
highest-leverage decision. The first character was generated as eight separate
images, and every pose came back drawn to fill its own canvas — different
scales, no shared ground line, nothing in register. Asking for one horizontal
row of frames in a single image fixed all of that at the source: within a strip,
scale, proportion, palette and ground line come back consistent to within a few
pixels.

**But strips drift against each other.** Within-strip consistency does not give
you between-strip consistency. Measured against the standing dribble, the aim
hold came back 39% too large and the ball-less run 32%. This is now the main
remaining source of manual work — see *the calibration frame* in ANIMATION.md
for how to stop paying it.

**No automatic landmark rescues the scale.** Three were tried and all three
failed, because each one moves with the *pose* as much as with the scale:

| Landmark | Why it fails |
| --- | --- |
| silhouette height | arms overhead and crouches change it by more than the drift does |
| shoe width | a shoe seen side-on in a stride is longer than one seen head-on; strides merge two shoes into one run |
| ink area | a crouch is compact, a star-jump is not |

A body landmark that is genuinely pose-invariant (head size, leg length) is
either hard to detect or moves when the knees bend.

The way out is not a cleverer measurement but a change to the *input*: put the
same standing pose at the start of every strip and measure that. The problem
stops being "infer the scale from an arbitrary pose" and becomes "compare like
with like", which is exact. Worth remembering as a shape: **when a measurement
is unreliable, look for a way to change what is being measured.**

**The generator ignores instructions it finds inconvenient, quietly.** The
prompt asked for the dribbling hand on the viewer's right in every standing
pose. It came back on the left — consistently, across the original take and both
re-rolls. The fix that worked was not a fourth re-roll; it was measuring the art
and configuring the game to match. **Prefer reading the art to asserting what it
contains.**

**It is reliable about frame counts, though.** All seventeen strips came back
with exactly the number of frames requested. When four of them appeared to have
too few, that was a bug in our slicer, not in the art.

**In a two-frame loop, the difference between the frames is the entire
animation.** The NBA player and the zombie read well because their two dribble
stances differ clearly in arm position; the high schooler's are nearly the same
pose and read as static. Ask for exaggerated differences, not subtle ones, and
say which body part must move and how far.

**Re-rolls are a coin flip, not a ratchet.** Four alternates generated from the
*old* prompts beat the carefully-revised versions in three cases out of four.
Prompt quality raises the average; it does not decide any single generation.
Generate, measure, keep the best — and keep the losers around, since a later
sequence may want them.

## Slicing

**Do not cut on empty columns.** The obvious approach — find vertical gaps
between figures — merged whole frames on four of fourteen strips, because tails
and swinging arms cross the gaps. Cutting at equal divisions of the width and
nudging each cut to the emptiest nearby column works on all of them.

**Clean bleed by flooding from the cut, not by keeping the largest blob.**
Keeping only the biggest connected component removes a neighbour's tail-tip, but
it also deletes the banana peel the monkey throws, which is legitimately
detached. Flood-filling inward from the cut edge and discarding what comes back
small removes exactly the fragments that leaned on a cut and nothing else.

**Bail out early or it is far too slow.** A full connected-component labelling
in Python took minutes across seventeen strips. The flood fill abandons a blob
as soon as it exceeds the size budget, so walking into the character's body
costs almost nothing.

**Threshold the alpha.** The source art carries a faint alpha haze over the
entire canvas. A plain bounding box returns "the whole image" for every frame.
Everything downstream assumes `alpha > 128`.

## Wiring it into the game

**Index an animation on the thing it represents, not on a clock.** This came up
three times, and it improved the result every time:

- the dribble is indexed on the ball's bounce phase, so the hand cannot drift
  out of step with the ball, and running faster speeds up both together;
- the charge is indexed on the power meter, so the coil deepens as you hold and
  *holds* at its deepest — as a timed loop it made the character bob up and down
  while winding up;
- the shot picks its frames from the *end* of the sequence, so a four-frame shot
  and a two-frame one work through the same code.

Where a natural driver exists, a timer is the worse choice.

**Mirror everything or nothing.** Horizontal mirroring reverses the jersey
number. Mirroring some sequences and not others is worse than mirroring all of
them, because the number flips depending on what the character is doing. Once
there is per-direction art, turn mirroring off entirely — and remember that
anything positioned relative to the character (the ball) stops flipping too.

**Anchor planted poses on the feet, travelling poses on the cell.** Anchoring
everything on the cell let the character slide sideways during the aim hold,
because the figure sat at slightly different places inside its two cells.
Anchoring everything on the feet breaks the poses that have no feet on the floor
— the handspring is on its hands in one frame and airborne in two.

**Read the feet from a band deep enough to hold both shoes.** Having decided to
anchor on the feet, the first version measured a band a thirtieth of the
figure's height at the bottom of the silhouette and took the middle of it. Most
stances put one foot a little lower than the other, so that band saw one shoe
and anchored the whole character on it: the High Schooler's standing pose came
out anchored at 91% of his own width and the NBA player's charge at 18%. On the
character select they stood outside their own cards; in play they jumped most of
a body-width sideways on every dribble frame, because the two frames of the loop
disagreed about where the feet were.

The tell is in the data, not on the screen — a `footX / w` column, which should
read about 0.5 for anyone standing on both feet. What makes it safe to fix by
widening rather than by guessing is that the measurement *converges*: sweep the
band from a thirtieth of the height to a sixth and every pose settles by a tenth
and does not move after that. Anything in the stable range is right, so there is
no knife edge to balance on. A leaning pose that stays off centre at every depth
— the shot, at 0.32 — is telling you about the pose, not about the measurement.

**Design an interruption as a variant of the loop it interrupts.** The idle
breaks keep the dribbling hand on the same four positions as the stationary
dribble, so the ball never stops bouncing and the break needs no handover frames
in or out. Building them as standalone one-shots would have needed a catch, a
held-ball state and two transitions.

**An animation must never cost the player anything.** Idle breaks and
celebrations cancel on any input, and breaks are suppressed when the shot clock
is low. A character mugging for the crowd while the clock runs out is a bad joke
at the player's expense.

**Check the trigger against the rest of the game.** Idle breaks were written to
fire after 8–15 seconds of standing still. With a 10-second shot clock that
window does not exist, so they never fired once.

## Verifying

**Composite everything on a common baseline and look at it together.** Scale
drift, ground-line wander and sideways slide are all but invisible frame by
frame and obvious the moment the frames share a red floor line and a blue
standing line. Nearly every art problem in this project was found that way, and
several were found *before* they reached the game.

**Measure before re-rolling.** "The dribble looks wrong" became actionable only
after diffing frames to find that the raised hand swapped sides between frames 2
and 3. Diagnosis first, then a prompt that addresses the diagnosis.

**A headless harness makes animation testable.** Rendering the page in jsdom
with a stubbed `requestAnimationFrame`, plus a `step(dt)` the test drives
directly, makes frame-accurate assertions possible: which pose shows at which
bounce phase, that the charge never bobs backwards, that moving cancels a
celebration. Seventy-odd of these run in about a minute.

**Sweep the parameter space for balance.** A solver that tries every
angle/power combination from five positions catches things playtesting would
take hours to notice — that the original power curve only ever scored above 85%
power, and that the monkey's higher release makes him measurably easier than the
other three.

## Process

**One sequence end-to-end before generating the rest.** The advice was to
generate one strip, wire it in, and look at it moving before spending on the
other thirteen. We did not follow it, and paid for it: the dribbling-hand side,
the scale drift and the mirroring bug each applied to every strip at once.

**Whole-sequence swaps are free; frame-level mixing is not.** Each sequence
carries its own scale correction, so swapping an entire sequence between takes
costs nothing. Mixing frames from two takes inside one sequence makes the
character change size mid-loop, which is the most visible place it can happen.

**Keep a record of which take is in use.** Once there are `_b` files, the
slicer's configuration is the only thing that says which one the game loads.
That is a real decision and it is easy to lose.
