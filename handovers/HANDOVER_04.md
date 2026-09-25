# Throw a Basketball — Handover 04: **the loop closes, and the ground moves**

## Handover for a fresh session (2026-09-25)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **Three sequences are now IN THE GAME and playable — the standing dribble and both running
> dribbles — and the pipeline that put them there went end to end for the first time: guide drawn
> from the manifest, strip rolled, take picked by eye, sliced, built, wired, and watched moving with
> the ball at the right speed.** ⭐⭐ **Every defect that mattered this session was found by taking
> the art the last mile into the game, not by looking at sheets: the phase, the ball's height, the
> 24-unit lurch, the ball floating off the hand — none of them visible in a preview.** ⛔ **ChatGPT
> redesigned its composer on the morning of the 25th and broke the generator in four places at once,
> each fault hiding the next; all four are fixed and the tool now diagnoses itself.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) THE GAME IS THE INSTRUMENT. THE SHEET IS ONLY A SCREEN.
Handover 03 §9(A) said to take a sequence end to end before generating more. It was right, and the
bill for not having done it earlier was four defects that no ruled sheet could show:

| defect | how it read on the sheet | how it read in the game |
|---|---|---|
| `dribbleFrame()` phase | fine | hand at its lowest exactly at the ball's apex |
| `bodyH()` from the first frame | fine | bounce sized off a CROUCH, apex ~6 units under the hand |
| travelling frames anchored on the cell | fine | the runner **lurched 24 units sideways**, a fifth of his height |
| the ball's lateral offset | fine | ball floating a hand's width off his fingers while running |

⭐ **Judge a loop in the game, with the ball, at the game's own speed.** The capture harness that does
this is §2 #7 and costs a minute per look.

> ### ⭐⭐ (B) COLOUR IS A READING AID. GEOMETRY IS THE INSTRUCTION.
The run guide colour-codes the limbs, and it genuinely helped a human read crossing legs. **The
generator ignored it.** Two mid-stride frames drawn with near-identical silhouettes — knee up, shoe
hanging behind, planted foot under the body — and differing only in which limb was orange and which
green came back as *the same pose twice*, in every roll of two separate batches.
✅ **Fixed by making them differ in SHAPE**, which is also what a three-quarter view really does: the
near leg swings through in front and projects large; the far leg swings behind the standing leg and
comes back foreshortened.
⭐⭐ **Generalisation: a distinction the guide draws only in colour, or only in a label, does not
reach the art. If two frames must differ, their silhouettes must differ.**

> ### ⭐⭐ (C) A DEFAULT THE MODEL ALREADY HAS BEATS A SMALL MARK.
All three rolls of the first left-running batch came back **looking right while running left** — the
direction sprite art faces by default. The guide had said otherwise, with the face arc and the ear,
and handover 03 §4 point 8 had already warned that a mark smaller than the head's radius is ignored.
✅ **A NOSE fixed it in one batch** — a wedge that juts the way he looks, drawn big enough to read —
together with a prose clause saying he is not looking back over his shoulder or at the viewer.
⭐ **When the model has a strong prior, the counter-instruction has to be a big mark AND a sentence.**

> ### ⛔⭐ (D) FIGURES OVERLAP. CUTTING CANNOT SEPARATE THEM; MASKING CAN.
Rick, on a roll he otherwise liked: *"It was cut wrong, one shoe went to the second frame."* Running
left, the trailing shoe reaches past the halfway line, so two figures' bounding boxes OVERLAP in x.
No vertical cut separates them, and widening the snap window does not help.
✅ `slice-strips.py` now finds connected blobs (row runs plus union-find, no new dependency), groups
them into cells with a 1-D k-means seeded at the equal divisions, and **lifts each figure out by its
own pixels**, so cells may overlap. Touching figures fall back to the old cut and the report says so.
⭐ Every existing sequence re-sliced to identical frame sizes; the only change was 148 px of alpha
haze per frame, in 112 pieces, the largest 12 px.

> ### ⛔⭐⭐ (E) THE SITE CHANGES UNDER YOU, AND FAULTS QUEUE UP BEHIND EACH OTHER.
On the morning of the 25th ChatGPT shipped a new composer. Four faults, each hiding the next, each
costing a round trip:
1. **the error handler crashed** — `dom_report()` was called on the attach-failure path and had never
   been written, so `AttributeError` replaced the real message;
2. **the file input moved** — `attach()` looked for it *inside the form holding `#prompt-textarea`*, a
   narrower selector than the rest of the script, and that now matches nothing;
3. **the attachment check was blind** — `_STATE` anchored on `#prompt-textarea`, returned null when it
   was absent, and so could never see two thumbnails plainly sitting in the composer;
4. **the image matcher refused the scheme** — the finished strip arrives as a `blob:` URL, which the
   matcher skipped, so it waited out 420 s in front of a generated strip.
⭐⭐ **The failure screenshots diagnosed all of it** — they showed the new composer, then the images
attached, then the strip generated. **Look at `build/gen-debug/` before theorising.**
✅ The tool now says what it sees: `--dom` prints the composer's DOM, a timeout lists every picture on
the page with size, turn role and source.

> ### ⭐ (F) TWO GUARDS, NOT ONE, TELL AN UPLOAD FROM A GENERATION.
The guide echo of handover 03 §0(C) came back, because its fix assumed an upload has rendered by the
time we snapshot. It had not. Now: an image in the **user's turn** is ignored, and a download whose
**aspect** matches an attachment's to within half a percent is refused as that attachment coming back
(a guide is 4.04, a strip 3.00). ⭐ The aspect guard fired for real mid-batch on the 25th and turned a
silent corruption into a failed roll. ⚠ A first attempt at the turn guard required the assistant's
turn and threw away a real generation: **the strip sits in NO role-tagged turn**, so the rule is "not
the user's", not "the assistant's".

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`, HEAD **`7b5e2b9`**. ⛔ **One commit unpushed**
(`7b5e2b9`, untracking a `.pyc`); everything before it is on `origin/main`. Rick pushes.

**Fifteen commits since handover 03.** In order: the guide's frame table into the manifest; the
standing dribble into the game; the run guide; two batches for the right run; the right run into the
game with two-bounce timing and the torso anchor; the mirrored left guide; the four generator
repairs; slicing by figure; the nose; the reshaped mid-stride frames; the left run into the game.

### In the game

| sequence | source | apex frame | bounces | ball side |
|---|---|---|---|---|
| `dribble_idle` | take32, handover 03 | 3 of 4 | 1 | default (+1) |
| `run_dribble_r` | take3 of the first guided batch | 2 of 4 | 2 | default (+1) |
| `run_dribble_l` | roll 1 of the third batch | 2 of 4 | 2 | **−1, stated** |

The zombie is a **MIXED** character in `build-sprites.py`: his eight old poses supply everything else,
and each sliced sequence replaces its counterpart. Seventeen sequences still on placeholder art.

### Reproducibility

```
art/sequences.yml           7fdfd953c9688fe2baef096c05a5b7fa
art/guides/dribble_idle.png 32b2f9bfb72286f04e7477f0c5b80903
art/guides/run_dribble_r.png 2279e6ba99a18e0533445e76922edf77
art/guides/run_dribble_l.png cc84560f8d598f7268794ada5672a756
```
✅ `dribble_idle` renders **b4506347134b** and `run_dribble_l` **da8155e3a2b6** — both exactly the
hash in their approved sidecar.
⚠ `run_dribble_r` renders **b88cff87e5b5** against its take's **e00eb966b32d**: the difference is the
corrected near/far wording in the note (§3), a fix, not a change of pose. **Its guide is byte for byte
the one the take came from**, which is what matters for a re-roll.

### The takes (untracked, ~1.2 MB each, only on this machine — ⛔ do not `git clean`)

`run_dribble_r`: `take1`–`take3` (first guided batch), `favorite` = `approved` = take3.
`run_dribble_l`: `take1`–`take3` (looked right while running left), `take4`–`take6` (open free hand,
mid-stride frames identical), `r1`–`r3` (the batch that worked), `approved` = r1,
`bug-guide-echo-1/2` = **not generations**, the guide coming back.

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`guide:` as a mapping in the manifest** | ✅ file, side, switches and one line of numbers per frame. A new guide is a manifest edit. `gen-prompts.py` still accepts a bare path. |
| 2 | **`make-pose-guide.py` generalised** | ✅ Draws any sequence, shared or a character's own (`--char`). New fields: `turn`, `arch`, `yaw`, separate `sh_tilt`/`hip_tilt`, `feet` pitch, free placement of both hands, `joints` overrides. Switches: `colors`, `ears`, `nose`. **All opt-in — `dribble_idle`'s guide is byte-identical.** |
| 3 | **The stretch check** | ✅ Warns when a limb is drawn longer than standing: a projected limb can only shorten. Caught a 16% far thigh, a 30% arm, an out-of-reach hand height — all before a roll. |
| 4 | **Mixed characters** | ✅ `build-sprites.py`: old poses as the base, sliced sequences on top; `fixed` (never mirrored), `standH`, `apexFrame`, `loopBounces`, per-sequence `ballSide`. |
| 5 | **Per-sequence timing in the game** | ✅ `dribbleFrame(p, n, apex, bounces)`: the named frame is centred on the ball's apex, and a loop may span more than one bounce. Sheets that name nothing keep the old convention exactly. |
| 6 | **Torso anchoring for runs** | ✅ §0(A). Drift 23.8 → 0.1 units for the zombie; the monkey's runs improved from 11–13 too. |
| 7 | **The in-game capture harness** | ✅ `/tmp` script, not committed: wraps `requestAnimationFrame`'s timestamp so game time advances in exact 1/60 s steps, then screenshots each step. Gives a GIF at true speed, a fixed-camera GIF showing travel, and stills at the ball's apex. **Rebuild it — it is the instrument §0(A) asks for.** |
| 8 | **Slicing by figure** | ✅ §0(D). |
| 9 | **Generator repairs** | ✅ §0(E), §0(F), plus `--dom`. |

---

## 3 · ⭐⭐ THE PROCESS THAT WORKED, IN ORDER

Handover 03 §3's loop, now with the last mile attached and two changes learned the hard way:

1. **Derive the targets from `index.html`.** Hand apex 0.52, lateral 0.26, cadence: standing
   `dribT += 7·dt`, running `+= 9·dt`, one bounce is π. ⭐ **Check how many bounces the sheet spans**:
   the run is a stride of two steps and bounces once per footfall, so four frames cover two bounces.
   Rick, having just gone running: *"I bounce with every foot landing."*
2. **Write the frame table in the manifest**, then render and LOOK at the guide before anything else.
3. **Check the stretch report.** A warning is geometry telling you the pose is impossible.
4. **Overlay on a real take** where one exists (`--overlay`).
5. **Roll three** (`--slow`). ⭐ Check each is a real generation: 2172×724-ish, >1 MB, a minute of
   generating, an md5 differing from the last.
6. **Cut and send Rick both the sheet and the loop** at the game's cadence for the sequence.
7. **Read the failures as instructions.** A property wrong in every roll is the guide's fault, not
   variance (§0(B), §0(C)). A property wrong in one roll is variance.
8. **Take the pick into the game and watch it there** (§0(A)) — slice, build, wire, capture.
9. **Keep the winner** as `<seq>.approved.{png,json}`, confirm the tree reproduces its prompt hash,
   commit by name.

⭐⭐ **A change to the guide and its matching change to the prose are ONE change, not two.** The rule
from handover 03 §4 point 10 held all session: when the guide said the free arm swung forward and the
prose said back, the batch came out confused.

---

## 4 · ⭐ BEST PRACTICES FOR A GUIDE — additions to handover 03 §4

12. ⭐⭐ **Silhouette carries; colour and labels do not** (§0(B)).
13. ⭐⭐ **Against a strong prior, mark big and say it in words** (§0(C)).
14. ⭐ **Each foot is placed from ITS OWN hip.** In a three-quarter view the hips are offset, and
    measuring both feet from the centre line stretched the far thigh 16%.
15. ⭐ **A guide is frozen once its take is approved.** The left run's frame table was shared with the
    right through a YAML anchor; the moment the right was approved, the left needed its own copy.
16. ⭐ **Opt-in switches, always.** Every new drawing feature is off by default, which is the only
    reason `dribble_idle`'s approved guide still renders byte-identical after six sessions of tool
    changes.

---

## 5 · ⛔ Traps — **additions only; handovers 01 §7, 02 §7 and 03 §7 stand**

- ⛔ **ChatGPT's UI changes without warning, and the script's own error handling can hide it.** Look at
  `build/gen-debug/fail-*.png` FIRST. Then `py tools\gen-strips.py --char zombie --seq <seq> --dom`.
- ⛔ **Generation only runs on native Windows, and the only route to it is Codex** — which on the 25th
  failed with `failed to spawn code-mode host codex-code-mode-host.exe`. Rick then ran the command
  himself. ⭐ **If Codex is down, hand Rick the one-liner rather than stalling.**
- ⚠ **A run that is already going does not pick up a fix.** Python reads the script at startup; stop
  it and restart after any edit.
- ⚠ **Delete permission does not survive an MCP reconnect** (handover 03), and the reconnects were
  frequent this session. A stale `.git/index.lock` after one blocks every commit: `rm` it and retry.
- ⚠ **`git branch -d` after a merge means the next branch needs a NEW name.** Quoting the old one cost
  Rick a confusing round of git errors. Check `git branch --list` before writing merge instructions.
- ⚠ The device shell is a **Linux VM**: no `py`, no PowerShell. Only Codex, or Rick, reaches Windows.

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **Push `7b5e2b9`** | Rick pushes. |
| **2** | ⭐ **Re-roll `run_dribble_r` on the current footing** | Its guide predates the nose and the reshaped mid-stride frames, and its prompt has since diverged from its take (§1). The pair should be made the same way. Cheap: the guide only needs `nose: true` and the left's mid-stride numbers mirrored. |
| **3** | ⭐⭐ **The remaining seventeen sequences** | `pickup`, `turn`, `aim`, `charge`, `shot`, `run_r`, `run_l`, `idle`, `steal`, `stolen`, `celebrate`, `celebrate_pump`, `gameover`, and the zombie's own `panic`, `break_face`, `break_head`, `celebrate_collapse`. ⚠ The one-shots need props and detached parts, which a skeleton carries badly — **expect the prose to do more there, and the guide less**. |
| **4** | **The ball's lateral offset while running** | Rick looked and said it reads fine, so this is closed unless it annoys him later. The lever, if wanted: a per-sequence ball offset beside `ballSide`, about 0.20 instead of 0.26. |
| **5** | **A ball-less idle** | Standing without the ball currently shows the upright dribble frame, hand out over nothing. `idle` is in the manifest, ungenerated. |
| **6** | **Stage 2, `tools/contact-sheet.py`** | Still unbuilt, still valuable: one page per batch with sheet + loop and a keyboard pick would cut the round trip Rick makes three times a batch. |
| **7** | ⚠ **`head_lean` in `measure-strip.py`** | Still mis-aimed (handover 02 §0(E)). Ignore or re-derive from the eye line. |
| **8** | **The other three characters** | ⚠ Handover 03 §9(B) stands and is now **more** certain: the guide is in fractions of standing height, but every roll so far has been the zombie. The first guided roll for the monkey (tail, crouch) or the NBA player (1.10×) is an experiment. |
| **9** | **`HOME_COURT` entries, quantisation in the slicer** | Carried over unchanged. |

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Push, then decide with Rick between re-rolling `run_dribble_r` (§6 #2) and starting the next
> sequence. Whichever it is, take it to the game before starting another.**

```
cd C:\Git\throw-a-basketball
git log --oneline -3
git push
py tools\make-pose-guide.py --seq run_dribble_l          # renders byte-identical
py tools\gen-prompts.py                                  # dribble_idle b4506347134b
py tools\gen-strips.py --char zombie --seq <seq> --dry-run
py tools\gen-strips.py --char zombie --seq <seq> --dom    # if ChatGPT changed again
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The pipeline became a pipeline.** Before this session a guide was code, a cut was a column, and no
> generated frame had ever been seen in the game. Now a guide is numbers in the manifest, a cut
> follows the figures, and three sequences have been watched running with the ball at the right
> cadence — where four defects were found that no sheet showed.
> ⭐ **Rick's eye beat the measurements again**, as in handover 03: he picked takes the tables ranked
> lower, spotted the miscut shoe, the head facing the wrong way and the repeated mid-stride pose —
> each one a defect in MY wireframe or MY slicer, not in the generation. ⛔ **What went wrong was
> mine**: colour-coding treated as instruction, a shared frame table that should have been frozen,
> and a slicer that assumed figures do not overlap. The generator's own collapse on the 25th was not
> mine, but the four hours it took to unpick were partly the script's: an error handler that crashed,
> and no way to ask the page what it looked like. Both now exist.
