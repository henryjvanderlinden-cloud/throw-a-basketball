# Throw a Basketball — Handover 07: **the zombie dribbles in place, calmly, looking at you**

## Handover for a fresh session (2026-09-25, evening)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie's stationary dribble is new art: face-on, a steady low crouch that bobs about
> 2%, the ball on the viewer's LEFT like the monkey's, four frames (r3 of the "subtle" batch,
> picked by Rick as "clearly the best").** ⭐⭐ **The old dribble looked stiff because the
> guide asked for it: a 13% crouch and a hand travelling to 0.52, about six times what the
> monkey moves, so every take exaggerated.** ⭐ **`gen-strips.py` now re-rolls when a guide
> or reference changes, not only the prompt, and moves a stale roll aside instead of
> overwriting it; both worked on Rick's machine on the first real run.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) MEASURE THE REFERENCE CHARACTER'S AMPLITUDE BEFORE WRITING A GUIDE.
Rick's complaint ("too stiff, primarily because it is too exaggerated") was traced to numbers,
not to the model. Height change across the dribble loop, as a share of the tallest frame:

| art | height change | hand travel |
|---|---|---|
| monkey `dribble_idle` | **~2%** | knee to mid-thigh |
| zombie take32 (handover 03, the old approved) | 8% | knee to waistband |
| zombie face-on r3 (tried as a two-frame loop) | 6% | knee to waistband |
| **the guide those came from** | crouch 1.6%–15% of standing | 0.26–**0.52** |
| the new guide | crouch 9.5%–12% | 0.30–**0.42** |
| **the new take (r3)** | frames 603–604 px tall | knee, thigh, hem, hem |

The model drew roughly what the guide asked. ⭐ **Rule: before a guide for a looping move, measure
the same move on a character Rick already likes, and set the table to that amplitude.** A few
lines of PIL on `sprites/<char>/<seq>/*.png` (alpha bbox heights) is enough.

> ### ⭐ (B) THE HAND WAS REACHING ABOVE THE BALL.
`index.html` puts the ball's peak at `DRIBBLE_HAND_H = 0.42` of body height for every character.
The old guide's HIGHEST hand was at 0.52 (the comment claimed that was where the ball peaks; it
was not). The new table tops out at 0.42. **Check a guide's contact heights against the game's
constants, not against a comment.**

> ### ⭐ (C) FACE-ON TAKES THE NOSE, BOTH EARS, AND ONE SENTENCE ABOUT THE REFERENCE.
`zombie.png`, the reference for every standing sequence, is drawn three-quarter with his head
in profile toward the viewer's RIGHT. Every dribble take copied that. Fixed on the first batch,
all six rolls since face-on: `nose: true` + `ears: true` on the guide (head-on: a wedge down the
middle and both ears), a `note` explaining them, and in the prose: *"the reference … does NOT
decide which way he faces: in that drawing he is turned toward the right edge, and in this
sheet he is not."* Expect the same pull in **every** standing sequence built on `zombie.png`.

> ### ⭐ (D) BALL SIDE AT REST FOLLOWS THE LEFT RUN, AS THE MONKEY'S DOES.
`BALL_SIDE["zombie"]["dribble_idle"] = -1` (viewer's left). Stopping after a left run, the ball
stays in the same hand; stopping after a right run, it changes hands — exactly the monkey's
behaviour. The alternative (two idles, one per facing) was offered and not taken.

> ### ⭐ (E) IDENTITY DRIFT: FOUR OF SIX ROLLS WENT SKULL-FACED.
Face-on batch r1, r2 and subtle batch r1, r2 all drew a skull with glowing eyes and lost the
reference's rotted-skin face; face-on r3 and subtle r3 kept it. This is handover 05 §0(A)'s drift
again, now at ~2 in 3 for face-on views. Nothing flags it before Rick sees it (§6 #3).

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`. HEAD is this handover's commit, on top of:

| commit | what |
|---|---|
| `3a4a3cf` | `gen-strips.py`: skip on prompt + guide md5 + reference md5; archive stale rolls |
| `6cd44be` | `dribble_idle` guide/prose face-on (superseded in part by the next) |
| `2e8c919` | `dribble_idle` guide/prose subtle, ball on the viewer's left |
| `79a5105` | the take in the game: approved = subtle r3, `BALL_SIDE`, sprites, `capture-game.py --script` |
| (next) | this handover |

⛔ **Five commits unpushed** (`origin/main` is `28cda9d`, handover 06's last). Rick pushes.

### In the game

| sequence | source | frames | rate | notes |
|---|---|---|---|---|
| **`dribble_idle`** | **subtle r3, this session** | **4** | follows the ball | **apex frame 3; ball on the viewer's LEFT** |
| `run_dribble_r` | take3, handover 04 | 4 | follows the ball | two bounces |
| `run_dribble_l` | r1, handover 04 | 4 | follows the ball | ball side −1 |
| `idle` | r3, handover 05 | 2 of 4 (1, 3) | 2.5 Hz | raised hand viewer's right |
| `run_r` / `run_l` | handover 06 | 4 | 7 Hz | torso-anchored |

✅ Filmed in the game (`capture-game.py --p1 zombie --p2 nba --watch 0 --start
--script=-:1,right:0.8,-:1,left:0.8,-:1.4`): all four `dribble_idle` frames drawn, ball meets the
hand at the top, face-on at every stop, no page errors. Rick approved from the loops.
⛔ **`tools/test-game.py` fails one check: "the monkey is the shortest"** — picker card heights
`[140, 111, 124, 112]`, the zombie 111 px against the monkey's 112. The picker draws each
character's dribble apex frame, and the new dribble never stands up out of its crouch. Every
other check passes, 60 fps. §6 #1.

### Reproducibility

```
art/sequences.yml            495155cacf1f970c17241e13edc1dfcf
art/guides/dribble_idle.png  397c585dd71aa292df9341980a01622a
art/guides/run_r.png         250be1ba36d1d8290f91d1e297b3bc08   (unchanged)
art/guides/run_l.png         7f9db89a6380f0443c81eeef1645adc9   (unchanged)
art/guides/idle.png          4df0b4795d5e30bcac5e26c0d7d630a4   (unchanged)
```
Prompt hashes: `dribble_idle` **07870e997418** = its `.approved.json`; `run_r` 41f15fc58259,
`run_l` 98287ee24432, `idle` b36c7e4619b5 unchanged.

### The takes (untracked except `approved`)

`dribble_idle`: `take1`–`take32` and friends (handover 03); `b1r1`–`b1r3` (the handover-03-era
rolls, archived automatically); `b2r1`–`b2r3` (the face-on batch; r3 was the two-frame trial);
`r1`–`r3` (the subtle batch), `approved` = **r3**. Previews in `build/review/` (gitignored):
`dribface-r*`, `subtle-r*`, `idle-compare.png`, `guides.png`.

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **Guide-aware skip** in `gen-strips.py` | ✅ Sidecars record `guide_md5` and `ref_md5`; a roll is current only if prompt hash and both md5s match. Legacy sidecars (no md5s) count as current and are **listed** by the plan. `--dry-run` prints why each job runs (`new`, `prompt changed`, `guide changed`, `reference changed`). Tested on a copy: guide-only change scheduled a re-roll; untouched rolls skipped. |
| 2 | **Archive, never overwrite** | ✅ A stale `<seq>.rM` pair is renamed to `<seq>.bNrM` before its replacement is generated, N the first unused batch for that sequence. Refuses if the target exists or the rename fails. ⭐ **Renaming works natively under Controlled Folder Access**: both real runs archived without a hitch. |
| 3 | **`dribble_idle` guide + prose** | ✅ Rewritten (§0(A)–(D)): `side: left`, `nose`/`ears`, own `note`, stance 0.27 (the ball-less idle's), crouch 0.095–0.12, tilt ≤ 0.01, head ≤ 3°, hair at rest, hand 0.30/0.35/0.42/0.39. Prose: "a CALM, EASY DRIBBLE, AND HIS BODY HARDLY MOVES", one line insisting each frame's hand is at a different height. No stretch warnings. |
| 4 | **The take in the game** | ✅ `STRIPS` back to all four frames, `APEX_FRAME` 3, `BALL_SIDE` −1. |
| 5 | **`capture-game.py --script`** | ✅ Timed held directions, `dir:seconds` comma-separated, `-` for nothing held. ⚠ Pass as `--script=…` when it starts with `-`, or argparse reads it as a flag. |

---

## 3 · ⭐⭐ THE PROCESS, AS RUN THIS SESSION

1. **Spec review twice**, numbered lists with defaults; Rick accepted both in a line.
2. **A cheap trial before a re-roll.** Rick asked to try two frames of the face-on r3 in the game;
   it took one slice, one build and one capture, and it is what showed the problem was amplitude,
   not framing. Worth offering whenever a take is half right.
3. **Rolls via Codex** (`gpt-5.6-sol`, `danger-full-access`, `never`), one detached
   `Start-Process` per batch, log in `build\gen-<name>.log`, watched from the device shell.
   Each three-roll batch took ~7 minutes. First roll inspected the moment it landed.
4. **Sheets and loops for every roll** with `preview-take.py --cells 5`, its feet table read
   before recommending; Rick chose from the loops.
5. **In-game capture and tests in the cloud workspace** from a tarball of
   `index.html sprites splash audio artwork/basketball-courts artwork/overlays tools`.

---

## 4 · ⭐ BEST PRACTICES FOR A GUIDE: additions to handover 06 §4

25. ⭐⭐ **Amplitude from a liked reference** (§0(A)). Measure it; write it into the table.
26. ⭐ **Contact heights from the game's constants** (§0(B)): `DRIBBLE_HAND_H` for the ball.
27. ⭐ **Say that the reference does not set the facing** when the pose faces differently from it
    (§0(C)), and draw nose and ears on the guide.
28. ⭐ **"Small and steady" needs one counterweight.** A subtle prompt risks four identical
    frames; one sentence that each frame's hand is at a different height kept all six distinct.

---

## 5 · ⛔ Traps: **additions only; handovers 01–06 stand**

- ⚠ **Handover 06 §5's first trap is fixed** (skip on the prompt hash alone). Its replacement:
  a sidecar from **before 2026-09-25 18:00** has no md5s and is trusted on its prompt alone; the
  plan lists such rolls. If you know you changed their guide, move them aside first.
- ⚠ An interrupted batch can split across two archive numbers (the rolls archived before the
  stop get bN, the rest bN+1 on the next run). Harmless; the sidecars say what each was.
- ⚠ **Delete permission did not survive an MCP reconnect again** mid-session; re-request it
  when `rm` starts failing. `rm -f .git/index.lock` before and after device-side git still needed.
- ⚠ `capture-game.py --script -:1,…` fails; write `--script=-:1,…`.

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **The picker's "monkey is the shortest" check** | Fails since this take (§1). Choices for Rick: size the picker by `standH` where a strip has one; let the picker show a standing frame for strip characters; or accept and change the test. His call — it is what the character-select screen looks like. |
| **2** | ⛔ **Push** | Five commits. Rick pushes. |
| **3** | ⭐ **An identity check** | Handover 05 §6 #6 and 06 §6 #4, and four of six rolls drifted this session (§0(E)). A palette/face-region comparison against the calibration frame would catch the skull face before Rick has to. |
| **4** | ⭐⭐ **The remaining sequences** | `pickup`, `turn`, `aim`, `charge`, `shot`, `steal`, `stolen`, `celebrate`, `celebrate_pump`, `gameover`, and the zombie's own `panic`, `break_face`, `break_head`, `celebrate_collapse`. Apply §4 #25–27 from the start: measure the monkey's version first where one exists, and expect the facing pull on anything standing. |
| **5** | **Why the file input fails on the first job** | Handover 05 §0(E); still did not reproduce (both batches attached via the plus menu, then `input[type=file]`). |
| **6** | **The other three characters** | Unchanged; handover 06 §6 #6. |
| **7** | Carried over | `head_lean` in `measure-strip.py`, `HOME_COURT` entries, quantisation in the slicer. `run_dribble_r` re-roll closed unless Rick reopens it. |

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Push. Then put §6 #1 to Rick as a numbered choice — it is a visible change on the select
> screen — and after it the next sequence (§6 #4).**

```
cd C:\Git\throw-a-basketball
git log --oneline -7
git push
py tools\make-pose-guide.py --seq dribble_idle            # 397c585d...
py tools\gen-prompts.py                                   # dribble_idle 07870e997418
py tools\gen-strips.py --char zombie --dry-run            # says why each job would run
py tools\preview-take.py "artwork\basketball-players\Zombie poses\dribble_idle.approved.png" --cells 5 --hz 6
python -m http.server 8899   then
python tools\capture-game.py --p1 zombie --p2 nba --watch 0 --start --script=-:1,right:0.8,-:1,left:0.8,-:1.4
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The fix Rick asked for (face the camera) took one batch; what he actually wanted (a calm
> dribble) took one more, once the cause was measured.** The face-on batch worked on the first
> try because handover 05 had already solved facing for the ball-less idle. ⛔ **What went wrong
> was mine, and old**: the dribble's amplitude had been set in handover 03 without ever being
> compared with the monkey, and a comment claiming 0.52 was the ball's peak went unchecked for
> four sessions. ⭐ **Rick's trial request (two frames of r3 in the game) was the turning point**:
> seeing it move is what made "too exaggerated" visible. The gen-strips fix paid for itself on its
> first run, archiving six rolls that would otherwise have been overwritten.
