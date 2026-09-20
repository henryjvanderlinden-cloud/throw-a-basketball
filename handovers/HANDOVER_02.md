# Throw a Basketball — Handover 02: **the prompt has a grammar, and the roll has a variance larger than most of our edits**

## Handover for a fresh session (2026-09-20)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie's `dribble_idle` is DONE and committed** — `dribble_idle.approved.png`, nineteen takes
> in, with the hand at four ordered heights, both hands drawn as one shape moved, the feet nearly
> still and the head tilting rather than leaning. ⭐⭐ **Six prompt patterns came out of it, and they
> are the transferable product of the day: this generator obeys RELATIONS and ignores PROPERTIES.**
> ⛔ **And the sting: two rolls of an UNCHANGED prompt differ by up to 9.6 points of inter-frame
> difference, 12 points of hand apex and 4 points of stance — as much as most of the prompt edits we
> spent the afternoon attributing, which means the fine-grained tuning was partly reading noise.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) THE GENERATOR OBEYS RELATIONS AND IGNORES PROPERTIES. THIS IS THE WHOLE GRAMMAR.
Every clause that landed first time was a relation between two things in the picture:

- the dribbling hand is *further out from his centre line than his shoulder is*
- his hand and his knee are *side by side, overlapping in the silhouette*
- the HIGHEST frame is *unmistakably the highest of the four*
- his feet are *one drawing repeated in all four frames*
- the free arm is *exactly as it is in frame 1*

Every clause that took three or four rolls, or never landed, was a property stated in isolation —
"the hand is flat", "the feet stay in the same place", "it keeps that same shape", "the hand is at
CHEST height". ⭐⭐ **Before generating anything, read each clause and ask: is this a relation between
two things in the picture, or a property I am hoping persists? Rewrite the second kind.**

§3 is the full playbook. It is also written to the project docs as **`claude/art-prompt-playbook.md`**
so a session that never opens this file still finds it.

> ### ⛔⭐⭐ (B) ROLL-TO-ROLL VARIANCE IS AS LARGE AS MOST PROMPT EFFECTS. STOP TUNING; START PICKING.
Five prompt versions were each rolled twice. The two rolls of the **same** prompt:

| prompt version | inter-frame r1 / r2 | hand apex r1 / r2 | stance spread r1 / r2 |
|---|---|---|---|
| ordinal hand ladder | 22.2 / **31.8** | 45.6 / **52.0** | — |
| feet + knee | 24.5 / 23.4 | 48.4 / 48.4 | 4.8 / 2.8 |
| weight shift ⭐ *(the kept take)* | 23.7 / **25.6** | 44.0 / 47.2 | 5.6 / **1.6** |
| blanket delta | 18.4 / 15.8 | 34.9 / 34.7 | 3.6 / 0.8 |
| hybrid | 20.0 / 24.3 | 44.0 / **56.0** | 2.8 / 2.4 |

⛔ **Within one unchanged prompt: up to 9.6 points of inter-frame difference, 12 points of hand apex,
4 points of stance.** The prompt effects argued over all afternoon are mostly that size or smaller.
Even the two largest — the feet clause moving stance 7.3 → 2.8, and the blanket delta dropping
inter-frame 25.6 → 15.8 — sit only just outside the noise band of a single pair.

⭐⭐ **What survives the test is categorical, not statistical**: the hand ladder going from out-of-order
to ordered, both hands becoming one shape at four heights, the free hand ceasing to dribble, the
zombie claw disappearing. Those are visible in the sheet, not in the third decimal.

⭐⭐ **The consequence for the remaining nineteen sequences: do not tune per sequence. Generate three
or four rolls with the playbook prompt and PICK.** At n = 2 you cannot tell a good prompt from a
lucky roll. This is the argument for stage 2 that §3 of handover 01 was missing.

> ### ⭐⭐ (C) THE GAME'S OWN CONSTANTS ARE THE TARGETS. DERIVE, DO NOT TASTE.
`index.html` already fixes the numbers the art has to hit, and the prompt contradicted them for
nineteen takes' worth of history before anyone looked:

| what | where it comes from | value |
|---|---|---|
| hand height at the top of the cycle | `peak = bodyH*DRIBBLE_HAND_H - 0.5*BALL_R`, hand on the ball's upper quarter | **0.52 of standing height** — the waistband, NOT the chest |
| hand's lateral offset | `b.x = p.px + bodyH * 0.26 * ballSide` | **0.26 of standing height** out from the centre line |
| loop cadence, standing | `p.dribT += dt * 7`, one bounce is π, four frames | **112 ms/frame, 8.9 fps** |
| loop cadence, running | `dt * 9` | **87 ms/frame, 11.5 fps** |
| which side dribbles | new-pipeline characters get `mirror: False`; `ballSide` falls back to `+1` | the art must dribble on the **viewer's right** |

⛔ The prompt had asked for CHEST height (~0.72) — a fifth of a body height above where the ball is.
✅ Rewritten to the waistband, and take 11 landed the apex at exactly 52.0%.

> ### ⛔⭐ (D) `dribbleFrame()` DRAWS THE LOWEST-HAND FRAME AT THE BALL'S APEX. POSTPONED, NOT FIXED.
```js
return Math.floor(((((u - 0.5) % 1) + 1) % 1) * n) % n;   // u = bounce phase
```
At `u = 0.5` the ball is at its apex and this returns frame 0 — the LOWEST frame, hand at the knee.
At `u = 0` the ball is on the floor and it returns frame 2, the HIGHEST. ⛔ **Inverted from a real
dribble, and from what the sheet is drawn to do.** The comment above it states this as the intent, so
it is not a typo.

Two ways out, and **Rick chose to postpone both** until the art settles:
- the one-line fix, `return Math.floor(u * n) % n;` — changes how the dribble reads on screen for
  every character at once, so it wants a playtest;
- ⭐ **or rotate the zombie's four frames by two at slice time** — the loop is cyclic, so
  HIGHEST, DRIVING, LOWEST, RISING puts the highest-hand frame at index 0, which is the frame the
  game draws at the apex. Same effect, one character, no game change. Belongs in stage 3 as a
  `phase: 2` field on the sequence.

> ### ✅⭐ (E) THE INSTRUMENT EXISTS NOW, AND TWO OF ITS SIX MEASURES ARE KNOWN-BAD.
`tools/measure-strip.py` — one file, committed. Cuts a strip by `slice-strips.py`'s own rule,
registers the frames on the **foot span** (not the ink centroid, which a swinging arm drags sideways),
writes `loop.gif` at the game's cadence and `sheet.png` with each frame's hand height ruled across it,
and prints: inter-frame difference, mirror asymmetry with the calibration frame as control, hand apex
and lateral offset against §0(C)'s constants, head lean, and stance spread.

⚠ **`head_lean` is mis-aimed since the head spec became a TILT.** It measures the crown, and a head
that tilts moves its crown the *opposite* way, so it now reports negatives for correct tilts. Either
re-derive it from the eye line or delete it and keep the head crops.
⛔ **A hem-height measure built to answer "which knee is bent" failed its own control**: the
calibration frames, which are the same pose every time, disagreed by ±5 px — noise the size of the
signal. It was not kept. **The knee question is judged by eye.**

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, HEAD **`a61b989`** *(Keep the zombie's dribble, and the
instruments that judged it)*, on `main`. ⛔ **Unpushed — the device shell has no GitHub credentials,
so Rick pushes.** The session opened at `7f1c940` with nothing unpushed.

✅ **The working tree reproduces the approved take.** `art/sequences.yml` is MD5
`655304e2f007bcfd4513c47d3720adfd`; running `gen-prompts.py` yields prompt hash `26bd9a553321`, which
is exactly the hash in `dribble_idle.approved.json`. **Re-rolling that file regenerates the take we
kept**, subject to §0(B)'s variance.

```
Get-FileHash art\sequences.yml        -Algorithm MD5   # 655304E2F007BCFD4513C47D3720ADFD
Get-FileHash tools\measure-strip.py   -Algorithm MD5   # 870DC24DD8D1F4EA0CCF3C49B34F0CE7
```
⚠ Verify `measure-strip.py` by running it rather than by hash; it gained the stance measure late.

**Committed in `a61b989`:** `dribble_idle.approved.{png,json}`, `art/sequences.yml`,
`art/characters.yml`, `tools/measure-strip.py`.

⚠ **Nineteen takes sit untracked** as `dribble_idle.take1..take19.{png,json}` in
`artwork/basketball-players/Zombie poses/`, plus the live `r1`/`r2`. They are ~28 MB, they exist only
on this machine, and they are the evidence for everything in §0(B). ⛔ **Do not `git clean`.**
`take15` is the approved take; `take18`/`take19` are the last (hybrid) experiment.

⚠ **`git add -A` is still a trap here** — `.gitignore` carries an edit that is not ours and
`artwork/` holds a dozen untracked drafts. **Stage by name.**

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`dribble_idle.approved.png`** | ✅ The zombie's stationary dribble, judged usable by Rick. Sidecar carries the exact prompt and its hash. |
| 2 | **`tools/measure-strip.py`** | ✅ The instrument (§0(E)). Replaces the throwaway scripts handover 01 lost. |
| 3 | **The prompt playbook** | ⭐⭐ §3, also at `claude/art-prompt-playbook.md` in the project docs. |
| 4 | **The game's constants as art targets** | ⭐ §0(C). The prompt had been contradicting `index.html`. |
| 5 | **The variance finding** | ⛔⭐⭐ §0(B). Changes the plan for the other nineteen sequences. |
| 6 | **The wireframe plan** | §4. Designed, costed, not built. |

---

## 3 · ⭐⭐ THE PLAYBOOK — and the FALL-BACK SCENARIO

> **This section is the thing to read before writing any prompt for any sequence.** It is duplicated
> to `claude/art-prompt-playbook.md` in the project docs so it is findable without this file.

### The six patterns

1. ⭐⭐ **Relations, not properties.** §0(A). Every clause should tie one thing in the picture to
   another thing in the picture.
2. ⭐⭐ **Constancy is an OPERATION, not an adjective.** "It keeps the same shape" failed three rolls
   running. *"DRAW THE SAME HAND FOUR TIMES — one drawing, the same shape, the same spread of the
   fingers, the same angle to the floor, simply moved up and down the picture"* landed at once, and
   the same form fixed the feet (*"HIS FEET ARE ONE DRAWING REPEATED IN ALL FOUR FRAMES"*).
3. ⭐⭐ **Ordering needs distinct landmarks AND an ordinal claim.** Two frames that shared the landmark
   "MID-THIGH" came back ranked at random — the apex landed on the wrong frame, measured as
   25.8 / 43.5 / 33.9 / 36.3. Four distinct landmarks (knee, hem, waistband, just below the hem) plus
   *"the HIGHEST frame is unmistakably the highest of the four and the LOWEST frame unmistakably the
   lowest"* produced 24.6 / 39.5 / 52.0 / 45.2 on the next roll.
4. ⭐⭐ **Anchor sides to the PICTURE, not the body.** "the hand on the VIEWER'S RIGHT" was misread
   twice; *"the hand nearer the RIGHT EDGE of the picture"* was not. The same fix was needed again
   for the knee. ⚠ All four characters currently dribble on the viewer's right, so naming the edge in
   a shared sequence is safe *today* — a left-handed character needs a `{dribble_edge}` trait.
5. ⭐⭐ **A destination, never a ceiling.** *"rises no higher than the WAISTBAND"* produced a hand that
   stopped well under it (39.5% against a 52% target). *"it REACHES the WAISTBAND and touches that
   level"* produced 52.0%. Limits are obeyed by undershooting.
6. ⭐⭐ **Delta-from-frame-1 for INVARIANTS ONLY.** The calibration frame is the most reliable thing in
   any sheet (ground line 0–1 px, scale constant to three decimals), so *"exactly as it is in
   frame 1"* is the strongest copy instruction available — it produced the best feet of the day,
   0.8% stance spread. ⛔ **But a blanket delta — *"anything not mentioned is exactly as in frame 1"*
   — collapses the poses**: inter-frame fell to 15.8%, a failed sheet, with the ordinal hand ladder
   still in the prompt and losing to it. Use deltas for feet, free limbs, build, camera; use
   absolute, ordinal wording for whatever must change.

Inherited from handover 01 and confirmed all day: **positive descriptions land, prohibitions do not**;
**where a defect recurs, ask for a form that cannot contain it**; **a subject block says what a
character IS, never what his body is doing**.

### ⚠ On prompt length

The block ran 7.0k → 9.5k characters across the day. Regressions appeared as it grew past ~8.4k, and
cutting it to 7.0k recovered them — but §0(B) says that evidence is one pair of rolls wide. Treat
length as a suspect when a working clause stops working, not as a law. The approved take was produced
at 8,545 characters.

### ⛔⭐⭐ THE FALL-BACK SCENARIO — what to do if §4's wireframe does not work

**Do not go back to tuning prose. Roll and pick.** The prompt in `a61b989` is good enough that
roll-to-roll variance dominates it (§0(B)).

1. Write the sequence's prompt once, against the six patterns above and the constants in §0(C).
2. `py tools\gen-strips.py --char zombie --seq <name> --rolls 4 --slow`.
3. Run `py tools\measure-strip.py` on each roll. **Accept a roll only if all of these hold:**

   | check | threshold | why |
   |---|---|---|
   | calibration control (asymmetry) | **≤ 10%** | above this the sheet's calibration frame is itself bad, which also breaks `build-sprites.py`'s auto-scale |
   | mean inter-frame difference | **≥ 22%** | below ~15% the four frames read as one pose; the approved take is 25.6% |
   | weakest single transition | **≥ 15%** | catches a dead seam that the mean hides |
   | stance spread | **≤ 3%** | feet drifting means he is crouching by splaying |
   | hand apex | **45–55%** | §0(C) puts the ball at 52% |
   | hand ladder | monotone up to the HIGHEST frame | catches the apex landing on the wrong frame |

4. Then look, for the things no number catches: both hands the same shape in every frame; the free
   hand hanging, not dribbling; the knee bending on the dribbling side; no zombie claw.
5. Keep the winner as `<seq>.approved.{png,json}` and commit it with its sidecar.

⭐ **Four rolls costs about twelve minutes of wall clock and no attention until they land.** That is
cheaper than one prompt iteration, and unlike a prompt iteration it is not fooled by noise.

---

## 4 · ⭐ THE WIREFRAME IDEA — designed, costed, NOT BUILT

**Rick's idea, and it follows directly from §0(A):** every failure chased today — which knee bends,
the hand's four heights and their order, the stance widening, the head travelling instead of tilting
— is *geometry*, and we spent eight rolls trying to convey geometry in sentences. **A pose guide does
not describe the geometry, it IS the geometry.** It also makes the constancy true by construction: one
skeleton, transformed per frame, shares limb lengths and footprints exactly.

### ✅ The plumbing is cheap, and this was checked rather than assumed

`GenBot.attach(path)` in `tools/gen-strips.py` takes one path and confirms the upload by matching the
**filename** inside any `aria-label` (`_state(stem)`), which is language-independent and per-file. ⭐
**So a second attachment with a different stem is detected independently of the first.** The change is
roughly:

- a `guide:` key on the sequence (or character) in the manifest, rendered into `index.json`;
- a second `bot.attach(job["guide"])` after the reference, at the call site around line 559;
- one sentence in the prompt naming what the guide is.

### The guide image, as designed

- **One PNG, five cells, the same layout as the output strip** — calibration pose plus the four
  dribble frames. The mapping is then positional and needs no explaining, and it doubles as a
  statement of the layout.
- **Unmistakably schematic**: thin uniform lines, dots at the joints, a circle for the head, a drawn
  ground line and two fixed footprints, plain white background, no shading, no colour. ⛔ **It must
  look like an instruction, not like art**, or the model may imitate its flatness.
- **Parametric from numbers already trusted**: knee at 0.28 of standing height, hand apex at 0.52,
  hand 0.26 out laterally, stance from the approved take, head tilt small. One skeleton, transformed
  per frame.
- **Prompt wording**: say the second image is a POSE GUIDE — take joint positions from it, and take
  identity, proportions, colour and style from the character reference, which remains the only
  authority on who he is.

### ⚠ The risks, and how they will show

ChatGPT's image generation is **not pose-conditioned** the way ControlNet is; it treats a second
image as another reference and may blend it. Two failure signatures, both obvious on sight:
**style bleed** (a flatter, thinner figure, visible joint marks) and **identity drift** (the guide
winning over the character reference). One roll settles it.

### ✅ Validate before spending a roll

**Overlay the wireframe on `dribble_idle.approved.png`'s frames.** If the skeleton does not sit on the
character we already have, it will not help the generator either. `measure-strip.py` writes the
registered frames, so the overlay is a few lines against `<out>/f0..f3.png`.

### How success is measured

Hand heights within a few points of the guide's prescribed heights; stance spread near zero; the knee
question resolved by looking. ⭐ **And a second prize if it works at all: the guide generalises to the
other nineteen sequences far better than prose does, because a skeleton can be posed by hand in
minutes and needs no grammar.**

---

## 5 · Where measuring corrected the work, and where it misled

> ✅⭐ **THE INSTRUMENT REPRODUCED HANDOVER 01'S NUMBERS BEFORE IT WAS TRUSTED.** Re-implemented from
> §0(E) of that file, it scored the two archived takes at 11.3 / 24.2 and 31.3 / 41.4 against the
> recorded 11 / 24 and 31 / 41. ⭐ **An instrument that cannot reproduce the measurement it replaces
> is not an instrument.**

> ⛔ **THE PROMPT CONTRADICTED THE GAME AND NOBODY HAD CHECKED.** CHEST height against a ball whose
> apex is at 0.52 of standing height, and no lateral constraint at all against a ball drawn 0.26 out.
> §0(C). ⭐ **Derive art targets from the code that will draw the art.**

> ⛔ **A CLAUSE OF MINE WAS CAUSING THE DEFECT RICK KEPT REPORTING.** The pelvic counter-shift I
> argued for from biomechanics — *"his hips slide the opposite way"* — puts the weight on the FAR leg,
> so the far knee bent, for three rolls, while I kept rewriting the knee clause. ⭐ **When a defect
> survives several attempts, re-read the rest of the block for a clause that requires it.**

> ⛔ **TWO MEASURES WERE MIS-AIMED AND ONE FAILED ITS CONTROL.** §0(E). The calibration frame is the
> free control that catches this; use it every time.

> ⚠ **`check-prompts.py` HAD BEEN REPORTING THE PALM REGRESSION ALL DAY.** The monkey's proven prompt
> carries *"palm facing down"* in every frame; the whole-body rewrite kept it only in the lowest, and
> the dropped clauses were listed under the SUPERSEDED heading on every run. ⭐ **Read the dropped
> list, not just the headline number.**

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⭐ **Build the wireframe guide** (§4) and roll it once | The highest-value experiment left. Everything needed to start is in §4. |
| **2** | ⭐⭐ **Stage 2, `tools/contact-sheet.py`** | §0(B) makes picking the strategy rather than tuning. `measure-strip.py` already computes every number the picker needs; what is missing is many-rolls-on-one-page and a keyboard choice written to `choices.json`. |
| **3** | **`run_dribble_r` / `run_dribble_l`** | The sequences most like the one that now works. Apply the playbook, roll four, pick. |
| **4** | **The zombie's remaining seventeen sequences** | Same recipe. The manifest already renders them. |
| **5** | ⚠ **Fix or drop `head_lean`** in `measure-strip.py` | §0(E). It currently reports negatives for correct tilts. |
| **6** | **Stage 3, and the deletions it unlocks** | `SEQ_SCALE`, `POSE_SCALE`, `LEGACY_POSES`, `build_from_poses`; plus the `phase: 2` rotation from §0(D). |
| **7** | **Quantisation in the slicer** | Carried over from handover 01 §0(C), untouched today. |
| **8** | ⚠ **`HOME_COURT` entries** | Each new character needs one in `index.html` or it falls back to the arena. |
| **9** | ⛔ **Push** | `a61b989` plus this file's commit. Rick pushes. |

---

## 7 · Traps — **additions only; handover 01 §7 and `claude/session-handover.md` §Traps stand**

- ⚠ **THE DEVICE LINK DROPPED MID-SESSION AND CAME BACK BY ITSELF.** The MCP server disconnected,
  every `device_*` tool vanished for a turn, and both returned without intervention. ✅ Do not debug
  the repo for it; re-issue the call.
- ⚠ **`gen-strips.py` REGENERATES ROLL SLOTS, IT DOES NOT ADD NEW ONES.** `plan()` iterates
  `roll in range(1, rolls+1)` and writes `<seq>.r<roll>.png`, so an edited prompt **overwrites r1 and
  r2** rather than producing r3. ⛔ The docstring's claim that an edited prompt "produces a NEW roll"
  is not what the code does. **Copy the current rolls aside before every run** — that is what the
  nineteen `takeN` files are.
- ⚠ **A ROLL CAN FAIL SILENTLY-ISH.** Two runs today produced only one of the two rolls; the evidence
  was `build/gen-debug/noimage-zombie-dribble_idle-*.png` and a stale sidecar hash. ⭐ **Check the
  sidecar's `prompt_hash` against the current prompt before measuring anything.**
- ⚠ **`measure-strip.py` needs numpy and Pillow**, which the device's Python has; it runs from either
  the device shell or native Windows.
- ⚠ **`check-prompts.py` reports 9 clauses dropped from `dribble_idle`** and 0 unaccounted missing.
  That is expected — the sequence is a deliberate redesign and the dropped clauses are the monkey's
  arm-only wording.

---

## 8 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Read §3, then build §4's wireframe guide and roll it once against the approved take.** If it
> works, it replaces most of the prompt grammar for the remaining sequences. If it does not, §3's
> fall-back is written out step by step and needs no further thought: one prompt, four rolls, pick by
> the table, keep the winner.

```
cd C:\Git\throw-a-basketball
git log --oneline -3
git push
py tools\gen-strips.py --char zombie --seq dribble_idle --rolls 4 --slow
py tools\measure-strip.py "artwork\basketball-players\Zombie poses\dribble_idle.r1.png"
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **One sequence went from unusable to kept, and the route there produced a grammar that should
> transfer: relations over properties, copying over describing, ordinals over adjectives, the picture
> frame over the body, destinations over ceilings, and the calibration frame as the anchor for
> everything that must not move.** ⭐ **Rick supplied the diagnosis at every turning point** — the
> whole-body dribble in the last session, the palm orientation, the free hand mimicking the dribbling
> hand, the feet sliding, the wrong knee, and the wireframe idea that opens the next session.
> ⛔ **What the day did not buy is a method for knowing whether the last few edits helped**: with two
> rolls per prompt, the noise is the size of the effect, and the honest reading is that the sheet got
> good somewhere around take 11 and the rest was within the spread. ⭐ **That is precisely why the
> next tool to build is the one that picks.**

---

### Git

✅ **Committed this session:** `a61b989` *(the kept take, the manifest that made it, and
`measure-strip.py`)*, plus this file's own commit.
⛔ **Both unpushed. The device shell has no GitHub credentials — Rick pushes.**

⛔ **Ask for `device_request_delete_permission` on `C:\Git\throw-a-basketball` at the START of the
session, before any git command** — without it a commit leaves `.git/index.lock` behind that git
cannot unlink. ✅ Asking early is what kept today's commits clean.
⭐ **`git commit -F -` with a heredoc** avoids putting a message file in the repo.
