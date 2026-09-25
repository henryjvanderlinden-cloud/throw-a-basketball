# Throw a Basketball — Handover 05: **the zombie stands his ground**

## Handover for a fresh session (2026-09-25, afternoon)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie has a ball-less idle in the game: a wide defensive stance, one hand high and one
> low, shifting his weight from leg to leg. It is two frames cut from a four-frame roll, because
> only those two keep his feet still.** ⭐⭐ **Rick's eye threw out two of the three rolls for
> the FACE, which no instrument here measures, and chose the livelier pair of frames over the
> perfectly still pair, calling the feet "forgivable".** ⛔ **Two generator faults cost three
> rolls, and both were ours: an echo refused and then given up on, and a reference that never
> attached while a button count said it had. Both are fixed.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) IDENTITY IS JUDGED BY EYE, AND IT FAILS FIRST.
All three rolls got the pose right. The guide did its job: asymmetric hands, elbows out, and not
one straight-armed zombie reach. Rick rejected r1 and r2 at a glance: *"the face of 1 and 2 is
very different from the reference image."* Nothing in `measure-strip.py` or `preview-take.py` looks
at the face. ⭐ **Check identity before anything else on a sheet (face, kit trim, number), and
only then measure pose.** r2 also drifted in pixel scale and in its trim colours. On this
evidence, one roll in three keeps the character.

> ### ⭐⭐ (B) WHEN THE WHOLE LOOP FAILS, A SUBSET MAY NOT.
In r3, the only roll Rick accepted, the feet were NOT one drawing: the stance widened with
the crouch (outer span 72% and 69% of standing height in the two low frames, 63% in the two up
frames). Rather than re-roll, the four frames were paired up with the near shoe aligned,
measuring how far the far shoe moves:

| pair | far shoe moves |
|---|---|
| UP / UP AGAIN | 0.3% (their feet match exactly) |
| SET LEFT / SET RIGHT | 3.6% |
| any SET with any UP | 5.1–9.0% |

Rick picked **SET LEFT / SET RIGHT**: *"more dynamic and looks really good except for the feet,
but it's forgivable."* In the game, anchored on the midpoint between the shoes, that is 2 screen
px at each shoe, symmetric. ⭐ **`tools/preview-take.py` prints this pair table for any take,
and `slice-strips.py` can now keep a subset (§2).** Remember the monkey's ball-less idle is ONE
frame and reads fine, so a take with even one clean frame is not a loss.

> ### ⭐ (C) CROUCH DEPTH MOVES THE FEET, WHATEVER THE GUIDE SAYS.
The guide drew identical footprints in every cell, and the prose said so in capitals. The
generator still widened the stance for the deeper crouch. It is the same failure as
`dribble_idle`'s widening stance in handovers 01–02, and it tracks crouch depth: the two frames at
the same depth have matching feet. ⭐ **For a standing loop whose feet must hold, keep the crouch
depth the same across frames and put the motion in the lean and the arms.** Otherwise, plan for
a subset.

> ### ⛔⭐ (D) AN ECHO CAN ARRIVE BEFORE THE STRIP. REFUSE IT, THEN KEEP WAITING.
Handover 04 §0(F)'s aspect guard fired on the first two rolls, correctly: the 2048×507
download was the guide coming back. But it raised `NoImage`, and the roll ended. The failure
screenshot showed ChatGPT still thinking ("Aan het denken"): the real strip was on its way.
✅ Now an `Echo` (a subclass of `NoImage`) is added to the ignore set and the wait continues
within the same timeout. It fired on every roll afterwards, and every one of those rolls then
delivered its strip 25–35 s later.

> ### ⛔⭐ (E) "ATTACHED" WAS A BUTTON COUNT, AND OPENING THE MENU ADDS BUTTONS.
On the first job after a fresh page load, the file input does not take, so `attach()` falls
through to the plus menu. `_wait_attached` accepts a rise in the composer's button count as a
last resort, and **opening the plus menu is itself such a rise**. The reference was declared
attached and was not. ChatGPT answered in words: *"the colour zombie character reference is not
attached in this turn."* The old post-send check asked only for *an* image, and the guide
satisfied it. ✅ The sent message must now carry **as many distinct pictures as were attached**
(two with a guide), polled for up to 12 s. A short count fails the roll in seconds, instead of
after a 7-minute wait.
⚠ The plus-menu path still RUNS on the first job of every launch, and passed on the last roll.
The count now catches it when it goes wrong; the root cause (why the input fails on a fresh page)
is not fixed.

> ### ⭐ (F) A SLICED SEQUENCE IS NEVER MIRRORED, SO SAY WHICH SIDE THINGS ARE ON.
The spec proposed mirroring `idle` with facing. That was wrong: `build_mixed()` lists every sliced
sequence in `fixed` because a mirrored jersey number reads backwards. The raised hand is
therefore **always on the viewer's right**, whichever way he faces. That is fine for a defender.
⭐ Any future asymmetric pose is fixed to the side it was drawn on.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`, HEAD **`8617112`** plus this handover's commit.
⛔ **Seven commits unpushed**: `7b5e2b9` and `dd4753f` from handover 04, and five from this
session. Rick pushes.

| commit | what |
|---|---|
| `64b92a8` | `idle`'s pose guide and prose; the `open` hand in `make-pose-guide.py` |
| `f8a41bd` | generator: wait past an echo, count the pictures the message carried |
| `e1de55e` | the idle in the game: r3 approved, frames 1 and 3 sliced, built, wired |
| `8617112` | `tools/capture-game.py` and `tools/preview-take.py` |
| (next) | this handover |

### In the game

| sequence | source | frames | rate | notes |
|---|---|---|---|---|
| `dribble_idle` | take32, handover 03 | 4 | follows the ball | apex frame 3 |
| `run_dribble_r` | take3, handover 04 | 4 | follows the ball | two bounces |
| `run_dribble_l` | r1, handover 04 | 4 | follows the ball | ball side −1 |
| **`idle`** | **r3 of this session** | **2 of 4 (1, 3)** | **`ANIM_HZ.idle` 2.5** | raised hand viewer's right |

`animatePlayer()`'s last branch now plays `idle` when the character has it and otherwise falls
back to the upright dribble frame as before. So the monkey, the NBA player and the high schooler
are unchanged. `idle` is fourth in `FRAME_ORDER`, after the three dribbles, because in
two-player it is on screen from the first second.
✅ Watched in the game with the harness: `idle[0]`/`idle[1]` alternating at 2.5 Hz, the feet
moving 2 px each way, no page errors. ✅ `tools/test-game.py`: **207 checks, ALL PASS** (against a
tree that includes `artwork/basketball-courts` and `artwork/overlays`: without them, three
checks fail on 404s, which is the snapshot's fault, not the game's).
⚠ Watched only as player 2 while player 1 dribbles. The one-player case (after a shot) runs the
same branch but was not captured.

### Reproducibility

```
art/sequences.yml            26e1d1b9c05a40f60e935bf651f532cf
art/guides/dribble_idle.png  32b2f9bfb72286f04e7477f0c5b80903   (unchanged)
art/guides/run_dribble_r.png 2279e6ba99a18e0533445e76922edf77   (unchanged)
art/guides/run_dribble_l.png cc84560f8d598f7268794ada5672a756   (unchanged)
art/guides/idle.png          4df0b4795d5e30bcac5e26c0d7d630a4
```
Prompt hashes: `dribble_idle` **b4506347134b**, `run_dribble_l` **da8155e3a2b6**, both as in
handover 04. `run_dribble_r` **b88cff87e5b5** is the same known divergence from its take. `idle`
**b36c7e4619b5** = `idle.approved.json`. ✅ The existing guides render byte-identical with the
new `open` hand in the tool, because it is opt-in (handover 04 §4 point 16 holds).

### The takes (untracked except `approved`)

`idle`: `r1` and `r2` (pose right, **face wrong**, Rick), `r3` = `approved` (committed, png + json).
Batch 1's r1 and r2 never existed: they were lost to (D) and (E).

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`idle` in the manifest** | ✅ Four frames: SET LEFT, UP, SET RIGHT, UP AGAIN. Stance 0.27, drop 0.13/0.095, lean ±0.04, tilt ±0.025. Each arm fixed relative to its own shoulder, with elbows placed by `joints`. Its own `note`, because the shared one describes a flat dribbling hand. The prose names frames by pose, never by number (the listing counts the calibration pose as 1). |
| 2 | **`open` hand shape** | ✅ Palm to the viewer, fingers continuing the forearm (up for a raised hand, out and down for a low one), thumb toward the centre line. The palm is 1.2 × 1.4 of the flat hand's, so the mark is big enough to register. Opt-in. |
| 3 | **Generator: echo** | ✅ §0(D). |
| 4 | **Generator: picture count** | ✅ §0(E). `sent_with_image()` → `sent_images()`, returning a count. |
| 5 | **Slicer: frame subset** | ✅ A fifth element on a `STRIPS` entry, e.g. `("idle", "idle.approved.png", 4, True, [1, 3])`, keeps those frames, renumbered 01, 02. Only kept frames are measured. The report says `kept frames [1, 3] of 4`. |
| 6 | **Game wiring** | ✅ `ANIM_HZ.idle = 2.5`, `FRAME_ORDER`, the idle branch. |
| 7 | **`tools/capture-game.py`** | ✅ Handover 04's instrument, now committed. `--p1/--p2` characters, `--watch`, `--hold left/right`, `--seconds`, `--every`. Writes per-step PNGs, `loop.gif` (a crop that follows the watched player) and `shown.txt`. ⚠ Runs where Chromium launches (the cloud workspace), from `python -m http.server 8899` in a copy of the tree. |
| 8 | **`tools/preview-take.py`** | ✅ Cuts by figure, not by equal cells: `measure-strip.py`'s preview chopped r1's raised hand off. Anchors on the midpoint between the shoes. Writes `sheet.png`, `loop.gif` and `feet.txt`, the §0(B) pair table. `--frames` previews a subset as a loop. This is most of handover 04 §6 #6 (the contact sheet), minus the keyboard pick. |

---

## 3 · ⭐⭐ THE PROCESS, AS RUN THIS SESSION

Handover 04 §3 held throughout. Three additions:

1. **Before the roll, read the generated prompt end to end.** The off-by-one in frame numbers
   ("mirror of frame 1" meaning the calibration pose) was visible only in the output, not in the
   YAML.
2. **Judge the sheet in this order: identity, then feet, then pose** (§0(A), §0(B)).
3. **When a take fails as a loop, run `preview-take.py` and read the pair table before re-rolling**
   (§0(B)). Offer Rick the candidates as loops. He chose on liveliness, not on the smallest number.

Rolls ran through **Codex again** (`gpt-5.6-sol`, sandbox `danger-full-access`, approval `never`),
as a detached `Start-Process` with stdout redirected to `build\gen-<name>.log`, and were watched by
tailing the log from the device shell. The one-liner, for when Codex is down:

```
cd C:\Git\throw-a-basketball
py tools\gen-prompts.py
py tools\gen-strips.py --char zombie --seq <seq> --rolls 3 --slow
```

---

## 4 · ⭐ BEST PRACTICES FOR A GUIDE: additions to handover 04 §4

17. ⭐⭐ **Keep the crouch depth constant where the feet must hold** (§0(C)).
18. ⭐ **Asymmetry is a silhouette.** One hand high and one low reached the art on the first roll.
    Two matching raised palms would have been the colour-only kind of distinction (04 §0(B)).
19. ⭐ **Arms as offsets from their own shoulder**, computed once and written into `joints`, keep
    each arm one drawing moved with the body. Generate the table with a few lines of Python
    rather than by hand; §2 #1's numbers were made that way.
20. ⭐ **A guide that departs from the shared picture needs its own `note`.** The shared one
    describes whatever hands it was written for, and a contradiction between note and guide is a
    contradiction in the prompt.

---

## 5 · ⛔ Traps: **additions only; handovers 01–04 §5/§7 stand**

- ⛔ **`git status` from the device shell leaves `.git/index.lock` behind**, which then blocks
  Rick's own git. It needs delete permission (`device_request_delete_permission` on
  `C:\Git\throw-a-basketball`, capital G) and `rm -f .git/index.lock`. Make that the first line
  of every git command run from the device.
- ⚠ **In-place writes into the repo worked all session** from the device shell (`cp`, Python
  `write_text`), and `device_commit_files` created new files fine. Verify with `md5sum` anyway,
  since Controlled Folder Access has refused this before.
- ⚠ **`gen-strips.py` reads `build/prompts/`**, which is git-ignored and goes stale. Run
  `gen-prompts.py` first, every time. The one-liner above does.
- ⚠ **"NOT SIGNED IN" at every launch** clears itself in ~7 s. Leave it.
- ⚠ **`measure-strip.py`'s preview cuts equal cells** and clips overlapping figures. Use
  `preview-take.py` for anything Rick will look at.
- ⚠ **`artwork/* frames/` is git-ignored**, so git cannot show that a re-slice changed nothing.
  Compare frame md5s yourself if it matters.
- ⚠ The capture tree for the harness needs `artwork/basketball-courts` and `artwork/overlays` as
  well as `index.html`, `sprites/`, `splash/` and `audio/`, or the court is blank and the tests
  fail on 404s.

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **Push** | Seven commits. Rick pushes. |
| **2** | ⭐ **Running without the ball: `run_r` / `run_l`** | Rick said early on he thought this session was the "ball-less dribble". If that meant running without the ball, this is it: still placeholder art, and on screen every time a player chases a rebound. Travelling, torso-anchored, no ball. The closest model is the run-dribble guides with the free arm swinging on both sides. |
| **3** | ⭐ **Re-roll `run_dribble_r` on the current footing** | Unchanged from 04 §6 #2. |
| **4** | **The remaining sequences** | `pickup`, `turn`, `aim`, `charge`, `shot`, `steal`, `stolen`, `celebrate`, `celebrate_pump`, `gameover`, and the zombie's `panic`, `break_face`, `break_head`, `celebrate_collapse`. `stolen` hands over to `idle`, which now exists. |
| **5** | **Why the file input fails on the first job** | §0(E). Now caught, not cured. `--dom` on a fresh launch would show it. |
| **6** | **An identity check** | §0(A). Even a crude one (the face region's palette against the calibration frame's) would flag r1/r2-style drift before Rick has to. |
| **7** | **The other three characters' idle** | They fall back to the dribble frame. The guide is in fractions of standing height, but 04 §6 #8 stands: the first guided roll for another character is an experiment. |
| **8** | Carried over | `head_lean` in `measure-strip.py`, `HOME_COURT` entries, quantisation in the slicer. |

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Push. Then ask Rick whether next is running without the ball (§6 #2) or the right run's
> re-roll (§6 #3), and take whichever it is to the game before starting another.**

```
cd C:\Git\throw-a-basketball
git log --oneline -8
git push
py tools\make-pose-guide.py --seq idle                    # 4df0b479...
py tools\gen-prompts.py                                   # idle b36c7e4619b5
py tools\preview-take.py "artwork\basketball-players\Zombie poses\idle.approved.png" --frames 1 3 --hz 2.5
python -m http.server 8899   then   python tools\capture-game.py --p1 nba --p2 zombie
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The pipeline carried a new sequence from spec to game in one sitting**: guide, three rolls,
> pick, slice, build, wire, watch. That is what handover 04 set out to make possible.
> ⭐ **Rick's eye decided it twice.** He rejected two rolls for a face no tool measures, and
> chose the dynamic pair over the still one. The measurements framed both choices; they did not
> make them.
> ⛔ **What went wrong was mine**: an off-by-one in the frame numbering, caught only by reading the
> generated prompt; a preview that clipped a hand and would have misled him; a spec point
> (mirroring) that contradicted the build's own rule; and a generator that, after handover 04's
> repairs, still threw away a strip that was on its way and believed a menu was an attachment.
> Each is fixed, or written down above.
