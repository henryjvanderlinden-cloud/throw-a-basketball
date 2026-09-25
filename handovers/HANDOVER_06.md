# Throw a Basketball — Handover 06: **the zombie runs without the ball**

## Handover for a fresh session (2026-09-25, late afternoon)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie now chases a rebound on his own art in both directions: a four-frame sprint,
> torso-anchored, bent arms and fists, played at 7 Hz. It replaces the two old dribble poses
> that had him pushing his hand down onto a ball that was not there.** ⭐⭐ **The first batch
> drew both strides as ONE pose, in all three rolls, because my guide gave them the same
> outline; making them differ in shape (one arm across the chest, the other reaching ahead)
> fixed it in the next batch, in all six rolls.** ⭐ **Rick picked r3 running right and r1
> running left on sight; r3 running left lost the character entirely, the one-in-three
> identity drift handover 05 §0(A) predicted.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) HANDOVER 04 §0(B) AGAIN, ON THE ARMS THIS TIME: SAME OUTLINE, SAME POSE.
Batch 1's guide placed every arm by an angle formula: upper arm swung so many degrees, elbow bent
90°. Both strides therefore had a fist out ahead of the chest and a leg forward and a leg back.
They differed only in WHICH arm (red or blue) was ahead. All three `run_r` rolls drew the two
strides as the same drawing, so in the loop the arms never swapped and he skipped on one side.
✅ **Fixed by placing the two strides' arms by hand so their outlines differ, as a
three-quarter view really does:**

| stride | near arm | far arm | outline |
|---|---|---|---|
| far leg leading | swings **across the front of the chest**, fist over the number | swung back, **hidden behind the body** | compact: nothing ahead of the chest, nothing behind the back |
| near leg leading | swung back, **elbow jutting out behind the back** | **reaching ahead** of the chest, clear of the body | open: a fist ahead and an elbow behind |

The prose was changed in the same edit (handover 04 §3), naming what shows and what is hidden,
and adding "this stride must NOT repeat the earlier one". All six rolls of batch 2 alternated.
⭐⭐ **Rule: for an alternating cycle, check the guide's two half-cycles as silhouettes, with the
colours ignored, before rolling. If they match, the art will too.**

> ### ⭐ (B) A FOUR-FRAME STRIDE, NOT TWO.
The manifest's `run_r`/`run_l` were placeholders written before the guides: two frames, "contact"
and "passing". A two-frame loop cannot change which leg leads. Four frames (stride, pass, stride,
pass) at the unchanged `ANIM_HZ.run = 7` give 3.5 steps a second, against the dribbling run's
2.87 at the same ground speed. Quicker, shorter steps without the ball read right; Rick
approved it in the capture. **No game code changed.**

> ### ⭐ (C) A RUN'S PREVIEW MUST BE REGISTERED LIKE THE GAME'S.
`preview-take.py` anchored every loop on the midpoint between the shoes, which is right for a
standing sequence and wrong for a run: a travelling stride slides back and forth under that
anchor. ✅ `--torso` uses `build-sprites.py`'s own `torso_centre()`, so the loop Rick judges is the
loop the game plays.

> ### ⭐ (D) THE CAPTURE HAD BEEN FILMING THE START SCREEN.
`capture-game.py` never started the match, so every capture sat under the dimmed START overlay,
logo and all. Movement still worked under it, which is why it went unnoticed. ✅ `--start` calls
`__hoop.dismissGate(); __hoop.startMatch()` first. **Always pass `--start`** unless the overlay is
the subject.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`. HEAD is this handover's commit, on top of:

| commit | what |
|---|---|
| `a199f8b` | `run_r`/`run_l` in the manifest: four frames, own guides and note |
| `5015a82` | `preview-take.py --torso`, `capture-game.py --start` |
| `6d89e96` | the runs in the game: approved takes, `STRIPS`, sprites, `manifest.js` |
| (next) | this handover |

⛔ **Four commits unpushed** (`origin/main` is `e7aa8d8`, handover 05's last). Rick pushes.

### In the game

| sequence | source | frames | rate | notes |
|---|---|---|---|---|
| `dribble_idle` | take32, handover 03 | 4 | follows the ball | apex frame 3 |
| `run_dribble_r` | take3, handover 04 | 4 | follows the ball | two bounces |
| `run_dribble_l` | r1, handover 04 | 4 | follows the ball | ball side −1 |
| `idle` | r3, handover 05 | 2 of 4 (1, 3) | 2.5 Hz | raised hand viewer's right |
| **`run_r`** | **r3 of batch 2** | **4** | **`ANIM_HZ.run` 7** | torso-anchored |
| **`run_l`** | **r1 of batch 2** | **4** | **`ANIM_HZ.run` 7** | torso-anchored; first passing frame sits 13 px (≈2%) higher |

✅ Watched in the game with the harness, as player 2 against the NBA player, holding left and then
right: `run_l[0..3]` and `run_r[0..3]` drawn, frames changing every ~8.6 ticks (7 Hz), no page
errors, P2's hue filter on, the number reading forwards both ways. ✅ `tools/test-game.py`: **ALL
PASS**, 60 fps. The 2% rise in `run_l`'s knee-up frame was left in as a runner's natural lift;
Rick saw it in the capture and did not object.
⚠ The monkey, NBA player and high schooler are unchanged: the monkey keeps his own two-frame run,
the other two their dribble poses.

### Reproducibility

```
art/sequences.yml            b2ce7e5cd7cc0c6740073cba76ebf6f4
art/guides/dribble_idle.png  32b2f9bfb72286f04e7477f0c5b80903   (unchanged)
art/guides/run_dribble_r.png 2279e6ba99a18e0533445e76922edf77   (unchanged)
art/guides/run_dribble_l.png cc84560f8d598f7268794ada5672a756   (unchanged)
art/guides/idle.png          4df0b4795d5e30bcac5e26c0d7d630a4   (unchanged)
art/guides/run_r.png         250be1ba36d1d8290f91d1e297b3bc08
art/guides/run_l.png         7f9db89a6380f0443c81eeef1645adc9
```
Prompt hashes: `run_r` **41f15fc58259** and `run_l` **98287ee24432**, each = its
`.approved.json`. `dribble_idle` **b4506347134b**, `run_dribble_l` **da8155e3a2b6**, `idle`
**b36c7e4619b5** unchanged; `run_dribble_r` **b88cff87e5b5** is still the known divergence from its
take (handover 04 §1).

### The takes (untracked except `approved`)

`run_r`: `b1r1`–`b1r3` (batch 1, strides identical), `r1`–`r3` (batch 2), `approved` = r3.
`run_l`: `b1r1` (batch 1, stopped after one roll), `r1`–`r3` (batch 2, **r3 lost identity**:
skull face, other style, smaller), `approved` = r1.
Batch 1 was renamed `b1r*` so batch 2 would not overwrite it (§5).

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`run_r` / `run_l` in the manifest** | ✅ Four frames: stride far leg, passing near leg in front, stride near leg, passing far leg behind. drop 0.05–0.065, lean 0.12, arch 0.03, turn 50, yaw 55; nose, ears, colours on. Each has its own `note` (every hand a fist, both arms bent, the colours naming far and near limbs), its own frozen frame table, and prose naming frames by pose. |
| 2 | **Arm placement** | ✅ Passing frames: computed from the calibration limb lengths (upper arm 0.176, forearm 0.190), sagittal swing foreshortened ×0.8 by the 50° turn, forearm opening to ~120° as the arms pass the hips. Strides: placed by hand (§0(A)). No stretch warnings. **No change to `make-pose-guide.py` was needed**: `hand`/`free` at `[x, y]` with `fist` already existed. |
| 3 | **`preview-take.py --torso`** | ✅ §0(C). |
| 4 | **`capture-game.py --start`** | ✅ §0(D). |
| 5 | **Slicer and build** | ✅ Two `STRIPS` entries; `build-sprites.py` already listed both runs in `TRAVELLING` and `BODY_ANCHORED`, and sliced sequences are `fixed` (never mirrored). |

---

## 3 · ⭐⭐ THE PROCESS, AS RUN THIS SESSION

Handover 05 §3 held. What was different:

1. **Spec review first**, as a numbered list with defaults (four frames; keep 7 Hz; bent arms
   against the zombie-reach prior; plain athletic sprint; left and right together). Rick accepted
   every default in one line.
2. **Rolled both directions in one job** (`--seq run_r --seq run_l --rolls 3`), right first.
   ⭐ **Look at the first roll the moment it lands.** Batch 1's defect showed in r1 and was
   confirmed by r2–r3; the job was stopped before it spent the other two left rolls.
3. **Stopping a job:** through Codex,
   `Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'gen-strips\.py' } | % { Stop-Process -Id $_.ProcessId -Force }`
   (it kills the `py` launcher and the Python child).
4. **Mirrored twins were taken to the game together**, not one direction at a time. That was
   right: a player turns constantly, so neither direction can be judged alone.
5. The capture, the tests and the stills ran in the **cloud workspace** from a tarball of the
   tree (`index.html sprites splash audio artwork/basketball-courts artwork/overlays tools/`),
   staged across and served with `python -m http.server 8899`.

---

## 4 · ⭐ BEST PRACTICES FOR A GUIDE: additions to handover 05 §4

21. ⭐⭐ **Compare the two half-cycles of an alternating loop as silhouettes** (§0(A)). Squint
    at the guide with the colours ignored; if the strides look alike, the art will be alike.
22. ⭐ **Occlusion is a silhouette too.** An arm drawn across the chest, or hidden behind the
    body, reached the art every time. Say it in the prose as well: "the far arm cannot be seen".
23. ⭐ **Compute where the rule is regular, place by hand where the silhouette matters.** The
    angle formula was right for the passing frames and wrong for the strides.
24. ⭐ **A new travelling sequence needs no tool change** if it is in `TRAVELLING` and
    `BODY_ANCHORED` in `build-sprites.py`. Check both before assuming work there.

---

## 5 · ⛔ Traps: **additions only; handovers 01–05 stand**

- ⛔ **`gen-strips.py` decides whether to re-roll from the PROMPT hash alone.** A change to the
  guide image that leaves the prose untouched keeps the hash, and a roll already on disk under
  `<seq>.rN` will be **skipped as current** even though it came from the old guide. This session
  changed both at once, so it did not bite, but a guide-only fix would. Rename or move the old
  rolls first (as `b1r*` here), or make the sidecar check include the guide's md5.
- ⚠ **New rolls overwrite `<seq>.r1`–`r3` when the prompt changes.** Keep a batch you may
  want by renaming it before the next one starts.
- ⚠ **Shell quoting ate two apostrophes in a commit message** (`'` inside a `$'…'` string).
  Fixed before pushing with `git filter-branch --msg-filter` on the unpushed range. Write long
  messages to a file and use `git commit -F` next time.
- ⚠ The device VM **does** have `python3` with PIL, numpy and yaml: `make-pose-guide.py`,
  `gen-prompts.py`, `slice-strips.py`, `build-sprites.py` and `preview-take.py` all ran there
  this session. Only generation needs native Windows, and only the harness and the tests need
  the cloud workspace.
- ⚠ `git status` still leaves `.git/index.lock` (handover 05 §5): prefix every device-side git
  command with `rm -f .git/index.lock`, and finish with it too.

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **Push** | Four commits. Rick pushes. |
| **2** | ⭐ **Make `gen-strips.py` skip on prompt AND guide** | §5's first trap. Small: add the guide's md5 to the sidecar and to the comparison. It will bite the first time a guide is fixed without touching the prose. |
| **3** | ⭐⭐ **The remaining sequences** | `pickup`, `turn`, `aim`, `charge`, `shot`, `steal`, `stolen`, `celebrate`, `celebrate_pump`, `gameover`, and the zombie's own `panic`, `break_face`, `break_head`, `celebrate_collapse`. The zombie's constant-on-screen set is now complete (standing and running, with and without the ball), so everything left is a one-shot or a character moment. ⚠ One-shots need props and detached parts, which a skeleton carries badly: expect the prose to do more, the guide less (handover 04 §6 #3). |
| **4** | **An identity check** | Handover 05 §6 #6, and it failed again (`run_l` r3). Even a crude palette check on the face region against the calibration frame would flag it before Rick has to. |
| **5** | **Why the file input fails on the first job** | Handover 05 §0(E). This session's first attach went through `input[type=file]` both times, so it did not reproduce. |
| **6** | **The other three characters** | The monkey keeps his own art; the NBA player and the high schooler run on their dribble poses. The first guided roll for another character is still an experiment (handover 04 §6 #8). |
| **7** | Carried over | `run_dribble_r` re-roll (Rick: "it's fine", **closed unless he reopens it**), `head_lean` in `measure-strip.py`, `HOME_COURT` entries, quantisation in the slicer. |

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Push. Then ask Rick what is next: the guide-aware skip in `gen-strips.py` (§6 #2) is a
> quick fix worth making before any further rolls, and after it the next sequence (§6 #3).**

```
cd C:\Git\throw-a-basketball
git log --oneline -6
git push
py tools\make-pose-guide.py --seq run_l                   # 7f9db89a...
py tools\gen-prompts.py                                   # run_r 41f15fc58259, run_l 98287ee24432
py tools\preview-take.py "artwork\basketball-players\Zombie poses\run_l.approved.png" --torso --hz 7
python -m http.server 8899   then   python tools\capture-game.py --p1 nba --p2 zombie --start --hold left
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **A new pair of sequences went from spec to game in one sitting, with one wasted batch.**
> The spec review settled five decisions in a line, no tool needed changing, and the second
> batch delivered six rolls with both strides distinct, five of them in character.
> ⛔ **What went wrong was mine**: I drew the two strides with the same outline and colour as
> the only difference, which handover 04 §0(B) had already warned against, on the legs. It cost
> four rolls. The capture harness had been filming the START overlay since it was written, and
> the run preview was registered on the feet; both are fixed. ⭐ **Rick's eye decided again**: he
> chose both takes on sight, from the loops, and approved the pair on the first in-game capture.
