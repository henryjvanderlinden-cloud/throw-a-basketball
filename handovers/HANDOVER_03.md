# Throw a Basketball — Handover 03: **draw the geometry, don't describe it**

## Handover for a fresh session (2026-09-21)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The wireframe pose guide from handover 02 §4 was built, validated and made to work, and the
> zombie's `dribble_idle` has a new approved take — `take32`, Rick's pick, the first roll with a
> genuinely flat, open, palm-down dribbling hand and visible hair movement.** ⭐⭐ **The guide is now
> the primary way to specify a pose: every property the prose chased for nineteen takes — knee
> asymmetry, spine lean, hand shape, hand ladder, hair — landed once it was DRAWN, and the one that
> stayed prose-only (hair) did not land until it was drawn too.** ⛔ **The first two "rolls" with the
> guide were not generations at all — the downloader saved the uploaded guide itself, because a wide
> attachment looks exactly like a strip — and the fix is in `gen-strips.py`.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) THE POSE GUIDE WORKS, AND IT DOES NOT COST IDENTITY.
Handover 02 §4 named two failure signatures for a second attached image — **style bleed** (a flatter,
thinner figure, visible joint marks) and **identity drift** (the guide winning over the character
reference). **Across ten real guided rolls neither appeared once.** No stick-figure lines, no joint
dots, no flattening; the zombie, his kit and the pixel style came through every time. ChatGPT's image
model is not pose-conditioned in the ControlNet sense, but told plainly which image is WHO and which is
WHERE (`defaults.guide_note`), it keeps them apart.

> ### ⭐⭐ (B) WHAT A GUIDE CAN CARRY — AND THE EVIDENCE FOR EACH
| drawn on the guide | before (prose only) | after (drawn) |
|---|---|---|
| which knee bends | the defect Rick reported for three rolls running | loaded knee lower and further out, as drawn |
| the four hand heights, in order | apex landing on the wrong frame; ceiling-undershoot | ladder monotone in all ten guided rolls; apex 45–53% |
| the stance | 7.3% drift before the feet clause | 0.4–3.2%; best-ever 0.4% (take30) |
| spine tilt toward the dribbling hand, straight at the top | never specified | visible in every roll from the first batch that drew it |
| **the dribbling hand as ONE flat shape, palm down** | the claw came back in almost every roll | **take32: flat, open, palm-down in three of four frames** |
| **hair lagging the bounce** | two prose wordings, six rolls, no visible movement | **drawn as five strands: stands up in LOWEST in take31/32** |

⭐⭐ **The pattern is handover 02 §0(A) taken to its conclusion.** The generator obeys relations
between things in the picture; a drawing IS a set of relations, all stated at once, none of them
open to a misreading of "viewer's right". **Where prose and guide both describe a thing, draw it; keep
the prose as a caption.**

⚠ **What the guide has NOT yet carried:** hair lying FLAT in the HIGHEST frame (drawn as short arcs
hugging the scalp; no roll shows it), and the head's TILT (take32 omits the face turn — Rick judged
that acceptable). Both are small marks inside a small circle; they are probably below what the
generator reads at that scale.

> ### ⛔⭐⭐ (C) A WIDE ATTACHMENT IS INDISTINGUISHABLE FROM THE OUTPUT. TWO ROLLS WERE LOST TO IT.
`wait_for_image()` separates the generated strip from the uploaded reference by **shape** — the
reference is portrait, a strip is wide. **The pose guide is wide.** It passed every filter, and the
first two "rolls" were ChatGPT's resized copy of the guide (2048×507, byte-identical, saved three
seconds after sending). I misread the first as the generator copying the guide and swapped the upload
order; that diagnosis was wrong and is reverted.

✅ **Fix, in `gen-strips.py`:** attachments are buttons, not `<img>`, until the message is sent — so a
**second snapshot of the page's images is taken after `sent_with_image()`**, when the user turn has
rendered both uploads. Everything on the page at that moment is an input; only the assistant's image
can appear later. ⭐ **Rule: a result that arrives in three seconds, or that is byte-identical to the
previous one, is not a generation. Check the size and the md5 before looking at the picture.** The two
false files are kept as `dribble_idle.bug-guide-echo-{1,2}.{png,json}` so nobody mistakes them.

> ### ⭐⭐ (D) A CONTRADICTION BETWEEN GUIDE AND PROSE SHOWS UP AS A DEAD SEAM.
The first guided batch (take25–27) had every roll's DRIVING DOWN → LOWEST transition at **6–12%**, a
near-repeated pose — against 21–22% for the unguided takes on the old prompt. Cause: the prompt said
two things about that frame. The height ladder put the hand "just BELOW the hem" (~0.33); the pose line
said "the dribbling hand is still high, trailing behind" the body. The guide had followed the ladder,
drawing DRIVING DOWN almost like LOWEST.
✅ **Resolved in favour of the pose line:** hand at **0.42**, above the hem, body already dropped. The
next batch's weakest transition rose to **18–22%**, and the batch after to **21–30%**.
⭐ **When one transition is dead in every roll, it is not variance — look for two instructions that
disagree about that frame.**

> ### ⭐ (E) FRONT VIEW MEANS FORESHORTENING, NOT IK.
The first guide used two-link inverse kinematics in the picture plane. It splayed the knees out past
the shoes and swung the dribbling elbow up level with the shoulder. A knee and an elbow bend in the
**sagittal** plane — toward the camera — and from the front that shows as a SHORTER limb, not a
sideways one. `middle()` in `make-pose-guide.py` places the joint on the line between its neighbours
with a small visible bulge. ⭐ **Check any new guide against a real take with `--overlay` before
spending a roll** — this error was caught there, not by a roll.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`. The session opened at `c382522` with nothing
unpushed. **This session's work is one commit on top of it** (see Git). ⛔ **Unpushed — Rick pushes.**

✅ **The working tree reproduces the approved take.** Rendering `art/sequences.yml` with
`gen-prompts.py` yields prompt hash **`b4506347134b`** (11,750 characters), which is exactly the hash
in `dribble_idle.approved.json`, and the guide it was generated with is `art/guides/dribble_idle.png`
as committed.

```
Get-FileHash art\sequences.yml            -Algorithm MD5   # D828680732A77E4268DECE3E00DE3CAF
Get-FileHash art\guides\dribble_idle.png  -Algorithm MD5   # 32B2F9BFB72286F04E7477F0C5B80903
Get-FileHash tools\make-pose-guide.py     -Algorithm MD5   # 4D15BEE806679B1B0B04B1BF5CA60A0D
Get-FileHash tools\gen-strips.py          -Algorithm MD5   # 7016AB4B1DD23EE7CE1DA8D0BF741652
Get-FileHash tools\gen-prompts.py         -Algorithm MD5   # B6A6023E9338EDBC3E7C119F24008F9F
```

### The takes, and which ones Rick singled out

All in `artwork/basketball-players/Zombie poses/`, **untracked, ~1.3 MB each, only on this machine.
⛔ Do not `git clean`.**

| file | what | status |
|---|---|---|
| `take20`, `take21` | the live `r1`/`r2` at session start (unguided, hybrid prompt) | archive |
| `bug-guide-echo-1`, `-2` | **not generations** — the uploaded guide, saved by the downloader bug (§0(C)) | evidence |
| `take24` | first real guided roll | archive |
| `take25`–`take27` | + spine tilt, + hair prose | **`take27` = `best-guided`**, Rick's pick of that batch |
| `take28`–`take30` | + trailing hand (§0(D)), hair as destinations | **`take29` = `favorite`**, Rick's pick; take30 is the table's best |
| `take31`–`take33` | + hands and hair strands drawn on the guide | **`take32` = `approved`** ⭐ |

`dribble_idle.best-guided.*` and `dribble_idle.favorite.*` are copies of take27 and take29, set aside
at Rick's request. `dribble_idle.approved.*` is take32 and is committed.

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`tools/make-pose-guide.py`** | ✅ Draws the five-cell guide from numbers — game constants plus crouch depths measured off the old approved take. `--overlay <preview dir>` draws it over a measured take to validate it. |
| 2 | **`art/guides/dribble_idle.png`** | ✅ The guide: skeleton, footprints, ground line, **hands** (dribbling hand a flat paddle with spread fingers; free hand narrow, fingers down), **hair** (five strands: up / rest / flat), head tilt axis. |
| 3 | **`guide:` key in the manifest** | ✅ Any sequence can carry one. `gen-prompts.py` renders `defaults.guide_note` into its prompt and writes `guide` into `index.json`. |
| 4 | **Second attachment in `gen-strips.py`** | ✅ Reference first, guide second; sidecar records `guide`; `--dry-run` shows it. |
| 5 | **Downloader fix** | ✅ §0(C). Without it, every guided roll saves the guide. |
| 6 | **`dribble_idle` prompt** | ✅ Spine clause; hand trails above the hem in DRIVING DOWN; hair as destinations; `guide_note` explains the hand and hair marks. |
| 7 | **New approved take** | ✅ take32. |

---

## 3 · ⭐⭐ THE PROCESS — what we did, in the order that worked

This is the loop, and it is the recommended loop for the remaining nineteen sequences.

1. **Derive the targets from `index.html`**, never from taste (handover 02 §0(C)): hand apex 0.52,
   lateral 0.26, cadence 112 / 87 ms.
2. **Measure a reference take** with `measure-strip.py` to get what the art actually does — crouch
   depth per frame, stance, hand heights. For a sequence with no take yet, use the nearest one.
3. **Build the guide** from those numbers, one frame table per sequence.
4. **Overlay it on the reference take** (`make-pose-guide.py --overlay`). If the skeleton does not sit
   on the character we already have, it will not help the generator. Fix it here — it is free.
5. **Roll three** (`gen-strips.py --rolls 3 --slow`) after copying the current rolls aside.
6. **Check each result is a real generation** — size 2172×724, ~1.3 MB, a minute of generating, and an
   md5 that differs from the last. Then measure each with `measure-strip.py`.
7. **Send Rick both the sheet and the loop for every roll.** He judges by watching it move, and his
   picks have repeatedly differed from the table's winner (take27, take29 and take32 were each his
   choice). The table screens; Rick picks.
8. **Read failures as instructions.** A transition dead in every roll is a contradiction (§0(D)); a
   property that stays wrong across a batch is something to draw rather than reword (§0(B)).
9. **Adjust the guide first, the prose second, and change only what the evidence points at** — then
   roll three again. Four batches took this sequence from "the hand is fine" to the approved take.
10. **Keep the winner** as `<seq>.approved.{png,json}`, confirm the working tree reproduces its prompt
    hash, and commit by name.

---

## 4 · ⭐⭐ BEST PRACTICES FOR A POSE GUIDE

1. ⭐⭐ **Unmistakably schematic.** Pure black on white, one line weight, joint dots, a circle for the
   head, no shading, **no text at all** — labels risk being copied into the art. It must read as an
   instruction, not as artwork.
2. ⭐⭐ **Same layout as the output strip.** Five cells, calibration pose first, one ground line across
   the whole image. The mapping is then positional and needs no explaining.
3. ⭐⭐ **Everything in fractions of standing height.** One guide then serves every character; the
   manifest's `scale` changes his size, not where his knee sits.
4. ⭐⭐ **Constancy by construction.** Feet and hands are ONE drawing, moved — never redrawn per frame.
   This is playbook pattern 2 ("constancy is an operation") made literal, and it is why stance drift
   and hand-shape drift fell.
5. ⭐⭐ **Draw what prose failed to convey.** The knee, the spine, the hand shape and the hair all went
   into the guide because words had not worked. Conversely, what prose already did well can stay prose.
6. ⭐ **Front-view geometry is foreshortening** (§0(E)). Bends toward the camera shorten a limb; they
   do not move it sideways.
7. ⭐ **Make asymmetries visible at a glance.** The loaded knee sits lower AND further out; the spine
   leans out over the loaded hip. A difference the eye has to hunt for in the guide will not reach the
   output.
8. ⭐ **Marks must be big enough to read.** Hands at first drawn at 5% of height smudged into blobs;
   at ~10% (palm + fingers) they read and the output followed. Hair "up" (long strokes) landed; hair
   "flat" (short arcs on the scalp) did not. **Budget: if a mark is smaller than the head circle's
   radius, assume it will be ignored.**
9. ⭐⭐ **The prompt must say which image is which, by appearance, not by order** — "the COLOUR image is
   the only authority on who he is; the black stick figure on white is a POSE GUIDE; take only the
   geometry from it; its lines, dots, background and blank head are not part of the drawing." The
   upload order is not something we control reliably.
10. ⭐⭐ **Guide and prose must never disagree** (§0(D)). When changing a number in the guide, search
    the prompt for every sentence about that frame.
11. ⭐ **Guides are validated against art, not against intuition.** Overlay first, always.

**Prompt length** reached 11,750 characters and the best rolls of the session came at 11.2–11.8k —
handover 02's ~8.4k warning did not reproduce with a guide attached. ⭐ **Now that the guide carries
the geometry, much of the dribble prose is duplication and is a candidate for trimming** — as its own
roll-and-pick experiment, never mixed with another change.

---

## 5 · Where measuring corrected the work, and where it misled

> ⛔ **I REPORTED A FINDING THAT WAS A DOWNLOADER BUG.** "The generator copied the guide" was written
> into a code comment before anyone checked the file's size and md5. Corrected within the hour.
> ⭐ **Check that an output is an output before interpreting it.**

> ✅ **THE OVERLAY CAUGHT THE IK ERROR FOR FREE.** No roll was spent on a skeleton with splayed knees.

> ⭐ **THE TABLE AND RICK DISAGREED THREE TIMES, AND RICK WAS RIGHT TO OVERRIDE IT.** take27 failed the
> weakest-transition check; take29 and take32 were not the table's first choice. The numbers catch
> gross failures — dead seams, drifting feet, a hand that never reaches the ball — and are silent on
> hand shape, hair and whether a loop *feels* like a dribble. ⭐ **Screen by the table, pick by eye.**

> ⚠ **`head_lean` is still mis-aimed** (handover 02 §0(E)) and reported "wrong side" on nearly every
> roll this session. Ignore it until it is re-derived from the eye line.

---

## 6 · ⛔ Open, ranked — THE NEXT ACTION IS #1b (see §9)

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **Push** | This session's commit. Rick pushes. |
| **1b** | ⛔⭐⭐ **`dribble_idle` end to end in the game, phase resolved** | §9(A). Nothing from this session has been seen in the game, and `dribbleFrame()` will currently show the hand low when the ball is high. |
| **2** | ⭐⭐ **Generalise `make-pose-guide.py` to any sequence** | Its frame table is hard-coded for `dribble_idle`. Move each sequence's frame table (drop, tilt, lean, hand, head, hair, palm) into `art/sequences.yml` under its `guide:` so a new guide is a manifest edit, not a code edit. Everything else in the pipeline already takes a guide per sequence. |
| **3** | ⭐⭐ **`run_dribble_r` / `run_dribble_l`** with a guide | The sequences most like the one that now works. These are travelling: the guide needs a stride cycle and the 87 ms running cadence. Then the §3 loop. |
| **4** | **The zombie's remaining seventeen sequences** | Same loop. Guides for the one-shots (celebrations, idle breaks) need more than a skeleton — props, detached parts — so expect the prose to carry more there. |
| **5** | **Stage 2, `tools/contact-sheet.py`** | Still valuable: three rolls × sheet + loop is what Rick judges from. One page with all rolls and a keyboard choice would cut the round-trip. |
| **6** | **Trim the duplicated dribble prose** (§4) | A clean experiment now that a working guided baseline exists. |
| **7** | **Hair FLAT and head TILT on the guide** | Enlarge the marks (§4 point 8) or accept their absence. Rick accepted the missing face turn on take32. |
| **8** | ⚠ **Fix or drop `head_lean`** | §5. |
| **9** | **Stage 3 and the `dribbleFrame()` phase** | Handover 02 §0(D), still postponed: rotate the approved frames by two at slice time, or fix the one-liner and playtest. |
| **10** | **`HOME_COURT` entries, quantisation in the slicer** | Carried over unchanged. |

---

## 7 · Traps — **additions only; handovers 01 §7 and 02 §7 stand**

- ⛔ **`device_commit_files` SILENTLY FAILS TO OVERWRITE an existing file** — it reports `written` and
  leaves the old file on disk. **`rm` the target first** (needs delete permission), commit, then
  **verify with `md5sum`** against the container copy. Hit twice this session.
- ⛔ **It ALSO SERVES A STALE COPY when the same staged path is reused** — editing
  `/mnt/user-data/outputs/x.py` and committing it again can deliver the previous version. **Give each
  revision a new staged filename** (`-v2`, `-v3` …) or patch in place on the device with `sed`.
- ⚠ **Delete permission does not survive an MCP reconnect**, and the bridge dropped **three times** this
  session. Re-request when `rm` fails.
- ⚠ **Generation only runs on native Windows** — Playwright and the signed-in `.chatgpt-profile/` live
  there; the device VM has no Playwright. **Launch through Codex as a detached process**, then poll the
  log from the device shell:
  ```
  Start-Process -FilePath "py" -ArgumentList "tools\gen-strips.py","--char","zombie","--seq","<seq>","--rolls","3","--slow" `
    -WorkingDirectory "C:\Git\throw-a-basketball" `
    -RedirectStandardOutput "C:\Git\throw-a-basketball\build\genrollN.log" `
    -RedirectStandardError  "C:\Git\throw-a-basketball\build\genrollN.err"
  ```
  Use Codex model **`gpt-5.6-sol`**, sandbox `danger-full-access`, approval `never`. Three rolls take
  about six minutes.
- ⚠ **Take numbering is manual.** Copy `r1..r3` to the next free `takeN` before every run (§1's table
  is the record). `gen-strips.py` overwrites roll slots.
- ⚠ **`build/patch-*.py`** are the one-off manifest patches used this session (textual, so the
  manifest's comments survive). They are in `build/`, which is ignored; they are not tools.

---

## 8 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **Push, then take `dribble_idle` end to end into the game and resolve the phase — see §9,
> added at the end of the session. Only then generalise the guide (§6 #2).**

```
cd C:\Git\throw-a-basketball
git log --oneline -3
git push
py tools\make-pose-guide.py --seq dribble_idle --overlay build\guide-check\approved.preview
py tools\gen-strips.py --char zombie --seq run_dribble_r --rolls 3 --dry-run
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The guide went from untested idea to the method.** Its first real roll was already Rick's "best one
> yet"; four batches of three, each changing one thing the previous batch pointed at, ended in a take
> with a flat hand, a trailing driving-down frame, a spine that leans and straightens, and hair that
> moves. ⭐ **Rick supplied the direction at every step** — the spine tilt, drawing the hands, drawing
> the hair as strands — and each of those was a case of moving a property from words into the picture.
> ⛔ **What went wrong was mine and procedural**: a downloader bug read as a finding, and a file-copy
> tool that lies about overwriting. Both are now written down in §0(C) and §7.


---

## 9 · ⭐⭐ CLOSING THOUGHTS — added at the end of the session, and they change what to do first

> ### ⛔⭐⭐ (A) NOTHING MADE THIS SESSION HAS BEEN SEEN IN THE GAME.
Every judgement above was made on the strip, the ruled sheet and a `loop.gif` — the art on its own, at
the right cadence, but **without the ball, at preview scale, and not through the game's own frame
selection.** The game is where the art has to work, and there is a known reason it will currently
look wrong there:

**`dribbleFrame()` is phase-inverted** (handover 02 §0(D), postponed twice). At the ball's apex it
draws frame 0 — which in this sheet is LOWEST, the hand at the knee. So in the game, as it stands,
**the hand will be at its lowest exactly when the ball is at its highest**, and the take that measured
best on every sheet may read as the hand and ball moving in opposition. The effect is the same for the
old approved take; the difference is that this time we have tuned the art carefully to a phase the
game does not yet use.

⭐⭐ **Therefore: before generating a single further sequence, take `dribble_idle` end to end** —
slice it, build it into the sprites, add the `phase: 2` rotation (or the one-line fix), and **play it**.
Twenty sequences built on a pipeline that has never been run to the end would multiply any mismatch
we have not seen. This moves handover 02's "stage 3" ahead of §6 #2 and #3.

> ### ⚠⭐ (B) "ONE GUIDE SERVES EVERY CHARACTER" IS A DESIGN CLAIM, NOT A RESULT.
Every guided roll this session was the zombie. The guide is in fractions of standing height, so it
*should* transfer — but the monkey has a tail and a different build, the NBA player is 1.10× and far
heavier, the high schooler slighter. ⭐ **The first guided roll for another character is an experiment,
not a production run**: overlay the guide on that character's existing art first (§3 step 4), and
expect the proportions — head size, shoulder width, hip height — to need a per-character override.

> ### ⚠ (C) THE GUIDE'S NUMBERS WERE MEASURED FROM THE ZOMBIE'S OWN EARLIER TAKE.
The crouch depths (0.150 / 0.093 / 0.016 / 0.101) came off the old approved `dribble_idle`, so the
guide partly teaches the generator to repeat what it already drew. That was the right starting point,
but for sequences with no reference take the numbers will be invented, and the overlay has nothing to
check them against. **For those, derive the frame table from `index.html` where the game constrains
the pose, and otherwise treat the first batch as the measurement.**

### The revised first action

> **Push. Then take `dribble_idle` end to end into the game and resolve the phase (§9(A)) — play it
> and judge it there. Only then generalise the guide (§6 #2) and move on to `run_dribble_r`.**

---

### Git

✅ **Committed this session:** one commit on `c382522` — the guide tool, the guide, the manifest, the
two pipeline changes, the new approved take and this file. **Staged by name**; nothing else in the
working tree was touched.
⛔ **Unpushed. The device shell has no GitHub credentials — Rick pushes.**
