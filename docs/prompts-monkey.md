# Monkey — generation prompts

Fourteen prompts, one per sequence. **Copy only the text inside the ``` fences.**
Everything outside a fence is a note for you, not for the image generator.

**Attach a reference image with every prompt:**

| Prompt views | Attach |
| --- | --- |
| front and three-quarter | `artwork/basketball-players/Monkey poses/Monkey 001.png` |
| back-facing (7, 8, 9) | `artwork/basketball-players/Monkey poses/Monkey 003.png` |

Each prompt says which one at the top.

**Do prompt 1 first and stop.** Send me the strip, I'll add slicing to the build
script and wire it into the game, and we'll see whether the prompt needs another
clause before you spend the other thirteen.

**A convention that runs through all of these:** in front views the monkey
dribbles with the hand on the **viewer's right**. That is why the idle breaks
(13, 14) do their business with the other hand — the dribbling hand keeps
cycling through the same four positions as the stationary dribble, so the ball
never stops bouncing and the break drops in and out of the loop seamlessly.

Order below is the phase order from `ANIMATION.md`. Prompts 1–4 are the states
on screen almost all the time; 5–9 are the shot; 10–14 are personality.

===============================================================================

## 1 — Stationary dribble · loop · 4 frames · attach Monkey 001.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame. The tail curls clear of the body and keeps roughly
the same shape in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the feet touch the same
horizontal line in every frame.

VIEW: front view, facing the viewer, squared to camera.

FRAMES, left to right:
1. Standing low in an athletic stance, knees bent, feet planted shoulder-width
   apart. The hand on the viewer's right is pushed all the way down at about hip
   height, palm facing the floor, fingers spread.
2. The same planted stance, weight rising slightly. The same hand is halfway
   between hip and chest, palm still down, elbow bending.
3. The same planted stance, standing tallest. The same hand is at its highest,
   just below chest height, wrist cocked.
4. The same planted stance, settling back down. The same hand is dropping back
   toward the hip, palm down.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.
The feet do not move at any point.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 2 — Run-dribble, moving right · loop · 4 frames · attach Monkey 001.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the planted foot touch the same
horizontal line in every frame.

VIEW: three-quarter view, the character running toward the right of frame, chest
turned slightly toward the viewer so the jersey number stays readable. He
dribbles with the hand on the viewer's right, the leading side. The tail streams
out behind him, to the viewer's left.

FRAMES, left to right:
1. Leading leg forward and planted, trailing leg stretched out behind. The
   dribbling hand is pushed down at hip height, palm to the floor. The free arm
   swings back.
2. Mid-stride: the trailing leg swings through beneath the body, torso leaning
   forward into the run. The dribbling hand rises to chest height.
3. The other leg forward and planted, the first leg now trailing. The dribbling
   hand is pushed down at hip height again. The free arm swings forward.
4. Mid-stride the other way: the leading leg swings through beneath the body.
   The dribbling hand rises to chest height.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 3 — Run-dribble, moving left · loop · 4 frames · attach Monkey 001.png

Not a mirror of prompt 2 — drawn fresh, so the jersey number stays the right way
round.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the planted foot touch the same
horizontal line in every frame.

VIEW: three-quarter view, the character running toward the left of frame, chest
turned slightly toward the viewer so the jersey number stays readable and reads
forwards. He dribbles with the hand on the viewer's left, the leading side. The
tail streams out behind him, to the viewer's right.

FRAMES, left to right:
1. Leading leg forward and planted, trailing leg stretched out behind. The
   dribbling hand is pushed down at hip height, palm to the floor. The free arm
   swings back.
2. Mid-stride: the trailing leg swings through beneath the body, torso leaning
   forward into the run. The dribbling hand rises to chest height.
3. The other leg forward and planted, the first leg now trailing. The dribbling
   hand is pushed down at hip height again. The free arm swings forward.
4. Mid-stride the other way: the leading leg swings through beneath the body.
   The dribbling hand rises to chest height.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 4 — Pick the ball up off the floor · one-shot · 3 frames · attach Monkey 001.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 3 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height when standing as in the reference
image — do not zoom, crop, recompose or rescale between frames. All frames share
one ground line: the soles of the feet touch the same horizontal line in every
frame.

VIEW: front view, facing the viewer, squared to camera.

FRAMES, left to right:
1. Starting from a low athletic stance, bending forward at the waist, both arms
   reaching down and forward toward the floor in front of the feet, knees
   beginning to bend.
2. Bent right down, knees deeply bent, both hands at floor level just in front
   of the feet, cupped as if scooping something up. Head down, looking at the
   floor. Tail raised for balance.
3. Rising back up, weight coming back over the feet, head lifting. The hand on
   the viewer's right is coming up to about hip height, palm down; the other arm
   returns to the side.

This is a one-shot, not a loop. Frame 1 must continue naturally from a low
athletic standing stance, and frame 3 must settle back into that same stance.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 5 — Turn to shoot · one-shot · 2 frames · attach Monkey 001.png

Bridges the front stance and the back stance. This is the hard cut in the game
today.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. The
character must be exactly the same height in both frames, and the same height as
in the reference image. Both frames share one ground line: the soles of the feet
touch the same horizontal line.

VIEW: the character turning on the spot, away from the viewer.

FRAMES, left to right:
1. Halfway through the turn: a three-quarter view from behind-ish, shoulders
   rotated away from the viewer, feet pivoting, head starting to lift and look
   up and away over the shoulder. Tail swinging across with the turn.
2. Almost fully turned: back nearly square to the viewer, both hands coming up
   in front of the chest, knees bending into a shooting stance, head tilted up.

This is a one-shot, not a loop. Frame 1 must continue naturally from a front
view facing the viewer; frame 2 must settle into a back view squared away from
the viewer.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 6 — Aim hold · loop · 2 frames · attach Monkey 003.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. The
character must be exactly the same height in both frames, and the same height as
in the reference image. Both frames share one ground line: the soles of the feet
touch the same horizontal line.

VIEW: back view, seen from directly behind, squared away from the viewer and
looking up toward a basket high in front of him.

FRAMES, left to right:
1. Knees slightly bent, feet shoulder-width apart, both hands raised in front of
   the chest as if cradling something, head tilted up. Tail hanging in a relaxed
   curl.
2. The same pose settled very slightly lower: knees a touch more bent, hands a
   fraction lower, tail swayed a little to one side. A small breathing settle,
   nothing more — the two frames should be close.

This row is a seamless loop: frame 2 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 7 — Charge / wind-up · loop · 3 frames · attach Monkey 003.png

The game plays these 1-2-3-2 as the power builds, so the sequence has to read in
both directions. The frames differ in **crouch depth**, not arm position.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 3 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. Do not
zoom, crop, recompose or rescale between frames. All frames share one ground
line: the soles of the feet touch the same horizontal line in every frame. The
character's head height changes between frames only because he is crouching, not
because the drawing has been rescaled.

VIEW: back view, seen from directly behind, squared away from the viewer and
looking up toward a basket high in front of him.

FRAMES, left to right — a single motion, coiling deeper each frame:
1. Upright: knees slightly bent, hands up at chest height, back straight. The
   beginning of the wind-up.
2. Crouching: knees clearly bent, hips dropped, hands drawn in closer to the
   chest, shoulders starting to hunch, tail curling up.
3. Fully coiled: knees deeply bent, hips low, back compressed and rounded, hands
   tucked tight against the chest, every muscle loaded and about to spring. Tail
   curled tight.

The three frames are one continuous deepening crouch and will be played forwards
and then backwards, so the motion must read smoothly in both directions.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 8 — The shot · one-shot · 4 frames · attach Monkey 003.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. Do not
zoom, crop, recompose or rescale between frames. Frames 1, 2 and 4 share one
ground line with the soles of the feet touching it; in frame 3 he is up on his
toes on that same line.

VIEW: back view, seen from directly behind, squared away from the viewer and
looking up toward a basket high in front of him.

FRAMES, left to right — one continuous shooting motion:
1. Fully coiled: knees deeply bent, hips low, back rounded, hands tucked tight
   against the chest.
2. Driving upward: legs extending, hips rising, both hands lifting past the head,
   elbows still bent, tail beginning to straighten.
3. Full extension: standing at full stretch up on the toes, both arms straight
   overhead, wrists snapped forward, fingers spread, tail straight out behind
   for balance. This is the moment of release.
4. Follow-through: still tall, arms still overhead but relaxing, wrists flopped
   loosely downward, weight settling back onto the heels, tail dropping.

This is a one-shot, not a loop. Frame 1 must continue naturally from a deep
crouch, and frame 4 is the end of the motion.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 9 — Run without the ball, moving right · loop · 2 frames · attach Monkey 001.png

Chasing a loose ball: no hand pushing down, both arms pumping.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. The
character must be exactly the same height in both frames, and the same height as
in the reference image. Both frames share one ground line: the sole of the
planted foot touches the same horizontal line.

VIEW: three-quarter view, the character sprinting toward the right of frame,
chest turned slightly toward the viewer so the jersey number stays readable. The
tail streams out behind him, to the viewer's left.

FRAMES, left to right:
1. Contact: leading leg forward and planted, trailing leg stretched out behind,
   both arms pumping — the arm on the viewer's left driven forward across the
   chest, the other swung back. Leaning into the sprint.
2. Passing: the legs cross beneath the body mid-stride, arms swapped — the other
   arm now driven forward. Leaning further forward.

This row is a seamless loop: frame 2 must flow back into frame 1 with no jump.
He is running flat out and is not dribbling — neither hand reaches toward the
floor.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 10 — Run without the ball, moving left · loop · 2 frames · attach Monkey 001.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. The
character must be exactly the same height in both frames, and the same height as
in the reference image. Both frames share one ground line: the sole of the
planted foot touches the same horizontal line.

VIEW: three-quarter view, the character sprinting toward the left of frame,
chest turned slightly toward the viewer so the jersey number stays readable and
reads forwards. The tail streams out behind him, to the viewer's right.

FRAMES, left to right:
1. Contact: leading leg forward and planted, trailing leg stretched out behind,
   both arms pumping — the arm on the viewer's right driven forward across the
   chest, the other swung back. Leaning into the sprint.
2. Passing: the legs cross beneath the body mid-stride, arms swapped — the other
   arm now driven forward. Leaning further forward.

This row is a seamless loop: frame 2 must flow back into frame 1 with no jump.
He is running flat out and is not dribbling — neither hand reaches toward the
floor.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 11 — Made basket celebration · one-shot · 2 frames · attach Monkey 001.png

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. Do not
zoom, crop, recompose or rescale between frames. Both frames share one ground
line: in frame 1 he is up on his toes on that line, in frame 2 his soles are
flat on it.

VIEW: front view, facing the viewer.

FRAMES, left to right:
1. Triumph: both arms thrown straight up overhead, up on the toes, head back,
   mouth wide open mid-shout, eyes screwed shut with delight, tail curled high
   above him.
2. Settling: arms coming back down, one fist pumped at chest height, a wide
   toothy grin, weight dropping back into a low athletic stance, tail lowering.

This is a one-shot, not a loop. Frame 2 must settle back into a low athletic
standing stance.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## 12 — Game over, panting · loop · 2 frames · attach Monkey 001.png

Loops under the game-over overlay. The whole effect is one breath: the feet and
hands are nailed in place and only the torso, shoulders and head move, so the
loop reads as breathing rather than as the figure wobbling.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. Do not
zoom, crop, recompose or rescale between frames. Both frames share one ground
line: the soles of both feet touch the same horizontal line.

VIEW: front view, facing the viewer. In both frames he is completely spent:
bent forward at the waist, both hands braced on his bent knees, legs
shoulder-width apart, the tail drooping limply to the floor behind him.

The feet, the legs and the hands-on-knees are in EXACTLY the same position in
both frames. Only the chest, shoulders and head move between them.

FRAMES, left to right — one breath:
1. The bottom of an exhale: shoulders dropped low, back rounded, chest
   collapsed, head hanging right down toward the floor, eyes half shut, mouth
   hanging open.
2. The top of a gulping inhale: shoulders heaved up around his ears, back
   arched, chest puffed out, head lifted a little so the muzzle points forward,
   mouth wide open gasping for air.

This row is a seamless loop: frame 2 must flow back into frame 1 with no jump.
The two frames should differ clearly in the height of the shoulders and head —
enough that flicking between them reads unmistakably as panting.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in either frame — the ball is drawn
separately by the game.
```

===============================================================================

## 13 — Idle break A: eating a banana · one-shot · 4 frames · attach Monkey 001.png

The dribbling hand keeps the exact four positions of prompt 1, so the ball never
stops bouncing. **This is the one prompt where a prop is allowed.**

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the feet touch the same
horizontal line in every frame. The feet stay planted throughout.

VIEW: front view, facing the viewer, squared to camera, in a low athletic stance
with the knees bent.

FRAMES, left to right. The hand on the viewer's RIGHT is dribbling and cycles
through four fixed positions; the hand on the viewer's LEFT eats a banana:
1. Dribbling hand pushed all the way down at hip height, palm to the floor.
   Other hand holding a peeled yellow banana up near his mouth, about to eat.
2. Dribbling hand halfway up, between hip and chest. Other hand bringing the
   banana to his mouth, taking a big bite.
3. Dribbling hand at its highest, just below chest height. Cheeks bulging,
   chewing happily with his eyes closed, other hand lowering the banana.
4. Dribbling hand dropping back toward the hip. Other hand flicking the empty
   banana peel away off to the side.

This is a one-shot played between repeats of a dribbling loop. The dribbling
hand's four positions must exactly match a normal dribbling cycle so the motion
is continuous.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

A banana is the only prop. The character is NOT holding a basketball in any
frame — the ball is drawn separately by the game.
```

===============================================================================

## 14 — Idle break B: waving to the crowd · one-shot · 4 frames · attach Monkey 001.png

Same structure as 13: dribbling hand unchanged, other hand does the business.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the feet touch the same
horizontal line in every frame. The feet stay planted throughout.

VIEW: front view, facing the viewer, squared to camera, in a low athletic stance
with the knees bent.

FRAMES, left to right. The hand on the viewer's RIGHT is dribbling and cycles
through four fixed positions; the arm on the viewer's LEFT waves to the crowd:
1. Dribbling hand pushed all the way down at hip height, palm to the floor.
   Other arm raised high above his head, palm open, starting to wave.
2. Dribbling hand halfway up, between hip and chest. Raised arm swung out to one
   side at the end of the wave, big toothy grin, looking out at the crowd.
3. Dribbling hand at its highest, just below chest height. Raised arm swung
   across to the other side, still grinning.
4. Dribbling hand dropping back toward the hip. Raised arm coming back down
   toward his side.

This is a one-shot played between repeats of a dribbling loop. The dribbling
hand's four positions must exactly match a normal dribbling cycle so the motion
is continuous.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## Saving the results

One file per prompt, in a new folder, named after the sequence:

```
artwork/basketball-players/Monkey strips/
  01-dribble-idle.png
  02-run-dribble-right.png
  03-run-dribble-left.png
  04-pickup.png
  05-turn.png
  06-aim.png
  07-charge.png
  08-shot.png
  09-run-right.png
  10-run-left.png
  11-celebrate.png
  12-gameover-panting.png
  13-break-banana.png
  14-break-wave.png
```

`tools/slice-strips.py` cuts each strip into its frames using the frame count
above, so the number of cells in the image has to match exactly. If a generation
comes back with three frames when you asked for four, re-roll rather than
keeping it.

===============================================================================

# Re-rolls

Three of the fourteen came back wrong. Everything else is good and sliced
cleanly. Replace the strip file and re-run the slicer.

## R1 — replaces prompt 1, stationary dribble

**What went wrong:** the raised hand swapped sides between frames 2 and 3, so he
looks like he is alternating hands, and it never rose above hip height — so all
four frames read as the same pose. In a loop this short, the hand travel *is*
the animation.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the soles of the feet touch the same
horizontal line in every frame.

VIEW: front view, facing the viewer, squared to camera, low athletic stance with
the knees bent and the feet planted shoulder-width apart.

CRITICAL: exactly ONE hand dribbles — the hand on the VIEWER'S RIGHT — and it is
the same hand in all four frames. It must never switch sides. The other arm
hangs relaxed and almost still at his side throughout, and never rises above his
hip.

The four frames differ ONLY in the height of that one dribbling hand, and the
difference must be large and obvious — the hand travels a long way, from down by
his knee up to his chest:

FRAMES, left to right:
1. The dribbling hand is at its LOWEST — reaching right down, palm flat to the
   floor, level with the KNEE, arm almost straight.
2. The dribbling hand has risen to HIP height, palm still facing down, elbow
   starting to bend.
3. The dribbling hand is at its HIGHEST — up at CHEST height, elbow sharply
   bent, wrist cocked, palm still facing down.
4. The dribbling hand has dropped back to HIP height, palm down, on its way
   down.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.
The feet do not move at any point, and the body stays in the same low stance —
only the dribbling arm moves.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game.
```

===============================================================================

## R2 — replaces prompt 2, run-dribble moving right

**What went wrong:** he came back sprinting with both fists pumping — a running
cycle with no dribble in it, identical in function to prompt 9. The dribbling
hand needs to be the headline of every frame, not a detail at the end.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the sole of the planted foot touches the same
horizontal line in every frame.

VIEW: three-quarter view, running toward the right of frame, chest turned
slightly toward the viewer so the jersey number stays readable. The tail streams
out behind him to the viewer's left.

CRITICAL: he is DRIBBLING A BASKETBALL WHILE HE RUNS — this is not a plain
sprint. The hand on the VIEWER'S RIGHT is the dribbling hand in all four frames.
It is always held out in front of his body with the palm facing DOWN toward the
floor, fingers spread, pushing an invisible ball down. It is never a fist, never
swung back, and never tucked in at his side. The OTHER arm does the running,
swinging freely.

FRAMES, left to right:
1. Dribbling hand pushed low, near knee height, palm flat to the floor. Legs:
   leading leg forward and planted, trailing leg stretched out behind. Free arm
   swung back.
2. Dribbling hand risen to hip height, palm still down. Legs mid-stride, the
   trailing leg swinging through beneath the body. Torso leaning forward.
3. Dribbling hand pushed low again near knee height, palm flat down. Legs: the
   other leg forward and planted. Free arm swung forward.
4. Dribbling hand risen to hip height, palm down. Legs mid-stride the other way,
   the leading leg swinging through.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game. His hand pushes down as if a ball were there.
```

===============================================================================

## R3 — replaces prompt 3, run-dribble moving left

Same fix, other direction. Not a mirror of R2.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 4 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in every frame. The
character must be exactly the same height in every frame, and the same height as
in the reference image — do not zoom, crop, recompose or rescale between frames.
All frames share one ground line: the sole of the planted foot touches the same
horizontal line in every frame.

VIEW: three-quarter view, running toward the left of frame, chest turned
slightly toward the viewer so the jersey number stays readable and reads
forwards. The tail streams out behind him to the viewer's right.

CRITICAL: he is DRIBBLING A BASKETBALL WHILE HE RUNS — this is not a plain
sprint. The hand on the VIEWER'S LEFT is the dribbling hand in all four frames.
It is always held out in front of his body with the palm facing DOWN toward the
floor, fingers spread, pushing an invisible ball down. It is never a fist, never
swung back, and never tucked in at his side. The OTHER arm does the running,
swinging freely.

FRAMES, left to right:
1. Dribbling hand pushed low, near knee height, palm flat to the floor. Legs:
   leading leg forward and planted, trailing leg stretched out behind. Free arm
   swung back.
2. Dribbling hand risen to hip height, palm still down. Legs mid-stride, the
   trailing leg swinging through beneath the body. Torso leaning forward.
3. Dribbling hand pushed low again near knee height, palm flat down. Legs: the
   other leg forward and planted. Free arm swung forward.
4. Dribbling hand risen to hip height, palm down. Legs mid-stride the other way,
   the leading leg swinging through.

This row is a seamless loop: frame 4 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in any frame — the ball is drawn
separately by the game. His hand pushes down as if a ball were there.
```

===============================================================================

## R4 — replaces prompt 12, game over panting

**What went wrong:** close, but his hands hang loose instead of gripping his
knees, and the shoulders barely move between the two frames — most of the
difference is in his face, which is too small to read at game size.

```
Pixel-art sprite sheet, single image, fully transparent background.

SUBJECT: the anthropomorphic monkey basketball player in the attached reference
image. Match that character exactly: brown fur, shaggy darker head fur, a long
curling tail, a blue sleeveless basketball jersey with a yellow number 7, blue
shorts with white and yellow trim, blue-and-white high-top sneakers. Identical
colours, identical proportions, identical build and identical height as the
reference, in every frame.

LAYOUT: one horizontal row of 2 frames of equal width, evenly spaced.
No borders, no frame numbers, no labels, no background, no drop shadows.

CAMERA: locked off. Identical distance and eye level in both frames. Do not
zoom, crop, recompose or rescale between frames. Both frames share one ground
line: the soles of both feet touch the same horizontal line.

VIEW: front view, facing the viewer. In BOTH frames he is doubled over,
exhausted, bent forward at the waist with BOTH PALMS PLANTED FLAT ON HIS OWN
BENT KNEES, elbows locked out, propping himself up. His tail lies limp on the
floor behind him. The feet, legs and the hands-on-knees are in EXACTLY the same
position in both frames — do not let the arms hang loose.

The two frames differ in ONE thing: how high his shoulders and head are. That
difference must be large and unmistakable, because it is the whole animation.

FRAMES, left to right — one huge breath:
1. EXHALED, at his lowest: shoulders dropped right down, back deeply rounded and
   hunched, chest collapsed, head hanging straight down toward the floor, tongue
   lolling out.
2. INHALING, at his highest: shoulders heaved right up around his ears, back
   arched, chest puffed out wide, head lifted so the muzzle points forward,
   mouth wide open gasping for air.

This row is a seamless loop: frame 2 must flow back into frame 1 with no jump.

STYLE: 16-bit arcade pixel art, bold dark outline, flat cel shading, limited
palette, crisp hard pixel edges. The background must be fully transparent
(alpha 0) with no haze, glow or soft fringe around the silhouette. Output a wide
landscape image.

The character is NOT holding a basketball in either frame — the ball is drawn
separately by the game.
```
