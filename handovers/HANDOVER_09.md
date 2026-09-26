# Throw a Basketball — Handover 09: **the zombie shoots like the monkey — now the rest of his roster**

## Handover for a fresh session (2026-09-26, morning)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie has the whole shooting chain — `turn`, `aim`, `charge`, `shot` — matched to the
> monkey's frames pose for pose, from pose guides traced off the monkey's sprites; Rick picked
> one take of each from a single twelve-roll batch.** ⭐⭐ **Rick rejected the "realistic"
> redesign in one message: *"We're not going for super-realism, it just needs to read right …
> every image in the four sequences read very well, so try to match them like for like."*** ⭐
> **What is left is nine sequences in three groups: three the monkey already has (match like for
> like, as here), four that are the zombie's own (Rick's designs, already specified), and two
> nobody has yet (`steal`, `stolen`), which also need game code.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) THE MONKEY'S FRAMES ARE THE SPEC. MATCH THEM; DO NOT REDESIGN THEM.
The session opened by filming the monkey's shooting chain and "finding" that the ball floats above
his head while his hands are at his chest. I proposed a one-handed, ball-on-the-palm hold with a
per-frame ball table, a held release frame and a moved aim line; Rick accepted the list as
"default", saw the first `aim` batch, and reversed it:

> *"sorry, this is not how basketballs are thrown. Instead, try to match the monkey poses like for
> like instead, all of them. In the game, there are no problems at all with these poses. It reads
> fine with the ball hanging in the air above his head, it's completely understandable."*

⭐ **Rule: where the monkey has a sequence, the zombie's is the monkey's, pose for pose, frame count
for frame count.** A "bug" found by filming is only a bug if it reads wrong *in play*; ask before
engineering around it. (Handover 08 §0(B)'s pickup fix was a real one: the ball visibly bounced on
its own. The shooting chain's floating ball was not.) Everything built for the redesign was
reverted except the `holdPos()` fix, §2 #4.

> ### ⭐⭐ (B) TRACE THE GUIDE OFF THE MONKEY'S SPRITES — IT WORKED FIRST TIME, 12 ROLLS OF 12.
Every one of the twelve rolls matched the monkey's poses. The method:

1. Draw the monkey's frames on a grid in shares of his standing height (his `dribble_idle` 116 taken
   as 0.98 of standing, as the zombie's is), feet midpoint at x = 0.
2. Read off, per frame: **head-top height** (→ `drop` = 0.975 − head top), **feet** (→ `stance`),
   **elbows and hands** (→ `hand`, `free`, `joints`), and whether the view is front, profile or back.
3. Write them into the zombie's own copy of the sequence in `art/characters.yml` with a `guide:`,
   and keep the shared prose, minus the character traits that would pull away from the monkey
   (the zombie's `coil_deep` "spine folded over at an unnatural angle" would have).

The monkey's measurements for the shooting chain are in the comment above the zombie's `turn` in
`characters.yml`. The grid script was a throwaway; its heart is ten lines — each sprite pasted at
`footX`/`footY` onto lines every 0.1 of 118.5 units.

> ### ⭐ (C) SIZE: TIE A NEW SEQUENCE TO ITS NEIGHBOURS THROUGH THE POSES THEY SHARE.
Every automatic landmark disagreed with the eye on some take: shoe width (turned feet, tiptoes),
head width (charge r2 and shot r1 draw a smaller head on the same body). What held was the chain:
`charge` frame 1 *is* `aim`'s pose, so their silhouettes must be the same height (ratio 1.004 at
×1.00), and `turn`'s last frame nearly is (0.97). So: pick one sequence's scale by eye beside the
dribble and the run, then derive its neighbours from the shared poses. Result: `turn` 1.03, `aim`
1.06, `charge` 1.08, `shot` 1.10 (`SEQ_SCALE`, with the reasoning in its comment).

> ### ⭐ (D) NEW SHOT ART CHANGES HOW EASY A CHARACTER IS.
`build-sprites.py hand_point()` takes the launch point from the top of the release frame, so the
zombie's moved from 140 to 178 above the feet. `tools/sweep-shots.py` (new) fires 4,536 shots per
character: zombie **3.9%** (3.3% at the old launch point), monkey 3.5%, high schooler 3.5%, NBA
4.0%. Rick has been told; he has not asked to pin it. Run the sweep after any `shot` change.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`.

| commit | what |
|---|---|
| `68ef84f` | the zombie's `turn`, `aim`, `charge`, `shot`; `holdPos()` facing fix; back-view guides |
| (next) | this handover, `tools/compare-takes.py`, `tools/sweep-shots.py` |

⛔ **Unpushed: `68ef84f` and this handover's commit.** Rick pushes.

### The zombie now

| sequence | source | frames | scale | notes |
|---|---|---|---|---|
| `dribble_idle` | h07 subtle r3 | 4 | ×1.12 | |
| `idle` | h05 r3 | 2 of 4 | ×1.08 | |
| `pickup` | h08 r1 | 3 | ×1.06 | `pickupBall` |
| `run_dribble_r` / `_l` | h04 | 4 | | |
| `run_r` / `run_l` | h06 | 4 | | |
| **`turn`** | **h09 r1** | **2** | **×1.03** | also the robbed player's spin, played backwards |
| **`aim`** | **h09 r1** | **2** | **×1.06** | |
| **`charge`** | **h09 r2** | **3** | **×1.08** | |
| **`shot`** | **h09 r1** | **4** | **×1.10** | the game plays frames 2–4 |
| `gameover` | — | | | ⛔ falls back to `dribble_idle` (no old pose was mapped to it) |
| celebrations, `panic`, breaks | — | | | ⛔ none: he just stands there |

He is still `mirror` + `fixed` (mixed), but every sequence the game reaches is now a strip. The
eight old poses supply nothing that is shown.

✅ Filmed standing and after a run, aiming both ways: the "13" never reads backwards, sizes hold
through the chain, the ball hangs above his head with the monkey's gap. ✅ `tools/test-game.py`
**ALL PASS**, 60 fps. ✅ The monkey's `turn/aim/charge/shot` frames re-sliced byte-identical.

### Reproducibility

```
art/guides/turn.png    aim.png    charge.png    shot.png (2100x570 -- the canvas grew, §2 #3)
art/guides/pickup.png        d863fecf5c049ec35edc6715be293470   (unchanged, re-drawn identically)
art/guides/dribble_idle.png  397c585dd71aa292df9341980a01622a   (unchanged)
```
⚠ PNGs that pass through `device_commit_files` come out **re-encoded** (pixel-identical, different
md5), so compare guides by pixels, not md5, across the bridge.

### The takes (untracked except `approved`)

`turn/aim/charge/shot.r1–r3`; the first, rejected one-handed `aim` batch is archived as
`aim.b1r1–b1r3`. `approved` = turn r1, aim r1, charge r2, shot r1.

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **Four zombie-own sequences** in `characters.yml` | ✅ Shared prose made like-for-like, one `note` (YAML anchor `&backnote`) explaining the back-of-head marks and the hidden hands, guides traced off the monkey (§0(B)). |
| 2 | **Back view in `make-pose-guide.py`** | ✅ Frame field `back: true`: three hair strokes across the skull and both ears, no face lines, no nose. |
| 3 | **Guide canvas grows for hands overhead** | ✅ Only when a pose reaches past the standard 520 px; every existing guide is byte-identical. |
| 4 | **`holdPos()` follows the SHOT art's facing** | ✅ A mixed character is `mirror`, so the launch point flipped whenever the zombie aimed left, though his shot art never flips. Kept after the revert; it matters for every mixed character. |
| 5 | **`tools/compare-takes.py`** | ✅ The monkey beside r1/r2/r3 (or `--approved`), at the game's timing, one ground line, `--scale` for candidates. This is how Rick picked all four in one line. |
| 6 | **`tools/sweep-shots.py`** | ✅ §0(D). |
| — | ~~per-frame ball table, held release frame, aim line from the ball~~ | reverted, §0(A) |

---

## 3 · ⭐⭐ THE PROCESS THAT WORKED — do it this way for the rest

1. **`git status` and mtimes first** (h08 §0(C)). Push if Rick has not.
2. **Measure the monkey's version on a grid** (§0(B)) and **film it in the game**
   (`capture-game.py --every 2`, contact sheet of the frames where `shown` changes).
3. **Spec review, short:** "matched to the monkey like for like" plus only the genuine choices.
   Do not propose redesigns of poses that already read (§0(A)).
4. **Guides for the whole group, then ONE batch for all of it:**
   `gen-strips.py --char zombie --seq a --seq b ... --rolls 3 --slow` in one detached Codex
   `Start-Process`. Twelve rolls took 24 minutes, ~2 min each, no failures.
5. **`compare-takes.py` per sequence** (all rolls, ×1.00), plus a look at each raw strip for identity
   (skull face, darker/desaturated kit — both drifted on some rolls this time). Recommend one per
   sequence; Rick answered "agreed with all suggestions".
6. **Approve** (`cp <seq>.rN.* <seq>.approved.*` on the device), **`slice-strips.py` entries**,
   **sizes** (§0(C)), `slice-strips.py <seqs>` then `build-sprites.py` **on the device**.
7. **Tar `sprites index.html tools/...` on the device → stage → film + `test-game.py` +
   `sweep-shots.py` in the cloud.**
8. Commit on the device; Rick pushes.

---

## 4 · ⭐ BEST PRACTICES: additions to handover 08 §4

32. ⭐⭐ **Match, don't redesign** (§0(A)). Where the monkey has it, it is the spec.
33. ⭐⭐ **Trace guides off the reference sprites** (§0(B)); the numbers go in a comment beside the
    sequence so the next person can check them.
34. ⭐ **Size through shared poses** (§0(C)), not through a landmark.
35. ⭐ **Batch a whole group of sequences** in one generation run and one review.

---

## 5 · ⛔ Traps: **additions only; handovers 01–08 stand**

- ⛔ **`build-sprites.py` deletes `sprites/` before it builds.** Run it in the cloud copy without the
  untracked `Monkey frames/` and `Zombie frames/` and it crashes half-way, leaving no sprites —
  after which `test-game.py` fails in baffling ways (boots straight into PLAY). Build on the device;
  in the cloud, restore `sprites/` from the tarball.
- ⚠ **`git archive` does not carry `* frames/` folders** (untracked). The cloud copy can film and
  test, not build.
- ⚠ The cloud's `http.server` dies between Bash calls unless started with `setsid nohup`.
- ⚠ Re-encoded PNGs across the bridge (§1).
- ⚠ Several rolls drew the **calibration frame from behind** for back-view sequences. It still
  scales correctly (it is the full standing height), but head-width checks against it are
  meaningless.
- ⚠ Identity drift continues: skull face on turn r2 and on most calibration frames; a darker,
  desaturated kit on aim r2 and charge r1. Still nothing flags it automatically.

---

## 6 · ⛔ Open, ranked — **the rest of the zombie's roster**

| # | what | how |
|---|---|---|
| **1** | ⛔ **Push** | `68ef84f` + this handover. |
| **2** | ⭐⭐ **Group A — the monkey has these: `celebrate` (2), `celebrate_pump` (3), `gameover` (2)** | §3 exactly: grid the monkey's frames, trace guides, one batch of nine rolls, compare, pick, size, build. All front view. `gameover` matters most: today the zombie just dribbles in place at the buzzer. Check `pickCelebration()`: celebrations are any `celebrate*` sequence, so these join `celebrate_collapse` in the draw. |
| **3** | ⭐⭐ **Group B — the zombie's own: `panic` (4), `break_face` (4), `break_head` (4), `celebrate_collapse` (6)** | Already specified in `characters.yml` from Rick's descriptions (panic: looks at the clock, eyes pop out, one arm raised stiffly to it; break A: pulls his face down impossibly far, snaps back rubbery, legs X-shaped; break B: tilts his head back impossibly far, snaps back). No monkey equivalent **pose for pose**, but the monkey's `panic`, `break_banana`, `break_wave` fix the **structure**: the dribbling hand keeps cycling through the four `dribble_idle` heights on the viewer's LEFT while the rest acts. Trace the dribbling side off the zombie's own approved `dribble_idle`, and the rest from the prose. `celebrate_collapse` is his rare showpiece, like the monkey's flip: check `CELEB_HZ`/`CELEB_RARE` for it. Spec review first; these are the ones with real choices in them. |
| **4** | ⭐ **Group C — nobody has these: `steal` (3), `stolen` (3)** | Rick wants a steal animation. **The game plays neither yet**: a steal press does nothing visible, and the robbed player plays `turn` backwards. Needs game code as well as art — play `steal` on every down press (hit or miss), `stolen` on the victim (cancellable by any input, handing over to `idle`, see the comments on `stolen` in `sequences.yml`). The zombie would be the first character with them; the monkey falls back to today's behaviour. Full spec review. |
| **5** | An identity check | h08 §6 #3, still open (§5). |
| **6** | Carried over | h07 §6 #5–#7, h08 §6 #5 (`capture-game.py --loose`). |

When all of 2–4 are in, the zombie's old eight poses serve nothing, and he can drop `MIXED` and
become a strips-only character like the monkey (check `LEGACY_POSES` and the `fixed` list).

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **`git status`. Push. Then Group A (§6 #2), exactly as §3: grid and film the monkey's
> `celebrate`, `celebrate_pump` and `gameover`, a short spec review, one batch of nine rolls.**

```
cd C:\Git\throw-a-basketball
git status
git log --oneline -3
git push
py tools\make-pose-guide.py --seq shot --char zombie           # 2100x570
py tools\gen-prompts.py zombie
py tools\compare-takes.py shot --approved --scale 1.10         # -> build\preview\shot-compare.gif
python -m http.server 8899   then
python tools\sweep-shots.py                                    # zombie 3.9%
python tools\capture-game.py --p1 zombie --p2 nba --watch 0 --start --every 2 --script=up:0.1,-:0.7,left:0.9,-:0.3,up:1.1,-:1.0
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **I found a "bug" in art Rick was happy with and designed a whole mechanism around it**, and he
> accepted the numbered list with "default" because the list read reasonably. Only the first
> rolls showed him what it meant. ⭐ **The recovery was fast because the monkey was a finished
> spec**: tracing guides off his sprites produced twelve usable rolls out of twelve, and the chain
> went from reversal to committed in under an hour. ⛔ **Lesson: for anything that changes how a
> finished character already looks in play, show a mock-up before the spec review, not after.**
