# Throw a Basketball — Handover 10: **the zombie is finished — every sequence, strips-only**

## Handover for a fresh session (2026-09-26, evening)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **All three groups left by handover 09 are in the game:** the monkey's celebrations and buzzer pant
> matched like for like (A), the zombie's own panic, idle breaks and collapse (B), and a brand-new
> steal and robbed reaction that no character had before (C), all from pose guides, all picked by
> Rick. ⭐⭐ **Two new game mechanisms came with them:** *story* sequences (played once, a frame per
> half bounce, starting on the ball's apex; the monkey's banana break now uses it too) and the
> steal/stolen animations with the ball carried into the thief's dribble. ⭐ **The zombie is now a
> strips-only character like the monkey, and without the ball he holds his dribble's still pose
> instead of the old "desperate" defensive loop.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) A LOOPED STORY STROBES. PLAY STORIES ONCE, ON THE BALL.
A four-frame sequence locked to the ball plays at 4 frames per bounce (0.11 s a frame), so an idle
break used to run twice in 0.9 s and a panic written as "notices slowly, then reaches" would have
strobed every 0.45 s. Rick chose **stories**: `build-sprites.py STORY_SEQ` → manifest `storySeq`.
A story waits for the next apex, plays once at one frame per HALF bounce (~0.22 s), so the ball
meets the hand in frames 1 and 3 — **the guides give the dribbling hand exactly two positions**,
traced off the approved `dribble_idle` (highest: hand 0.42, drop 0.095; lowest: hand 0.30, drop
0.12). A story may **hold** frames afterwards (`panic: [2, 3]` — arm up, eyes pulsing — until the
clock resets). Monkey `break_banana` is a story too (Rick: "half speed and only once").

> ### ⭐⭐ (B) WHERE THERE IS NO MONKEY TO COPY, SHOW THE STORY IN PLAY, WITH THE BALL.
`tools/preview-story.py` plays each roll inside the real dribble, ball drawn where the game draws
it, at game timing; `tools/preview-oneshot.py` plays a one-shot between stretches of the still pose.
That is what Rick judged Group B and C from, and it is what exposed the timing problems before any
code was written. Keep sending BOTH the sheet and the moving loop (ways-of-working).

> ### ⭐ (C) PICKS ARE OFTEN "THIS ROLL, BUT…" — THE PIPELINE NOW HANDLES THE COMMON BUTS.
- **Wrong colours, right pose** → `tools/recolour-take.py` (per colour family, CIELAB mean/spread
  onto the approved dribble's palette). Used on `break_face` r3. It cannot change shapes (r3's cream
  shorts patches stay).
- **Drop a frame / reorder** → `slice-strips.py` 5th element: `("stolen", …, 3, True, [1, 3, 2])`.
- **A frame that touches its neighbour** → erase it by hand into a new strip
  (`celebrate_collapse.r1noheap.png`) and slice that with one fewer frame.
- `preview-take.figures` (used by `compare-takes.py`) mis-splits touching figures; **the real
  slicer groups by component and does not** — check with `slice-strips` before telling Rick a roll
  is broken (steal_r r3 "went wrong" only in the preview).

> ### ⭐ (D) SIZE BY EYE AGAINST THE DRIBBLE; SHOE WIDTH LIES ON SOME ROLLS.
Shoe width worked for Group A (front-on stance shared with the dribble) but said ×1.35 for
`break_head` and the panic, whose rolls draw small feet. Final sizes were set side by side against
`dribble_idle` (head, "13", torso), see `SEQ_SCALE`.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`. ⛔ **Unpushed** (Rick pushes):

| commit | what |
|---|---|
| `0b838b6` | Group A: `celebrate` r3, `celebrate_pump` r1, `gameover` r1 *(pushed)* |
| `96d6738` | story mechanism, Group B specs + guides, collapse rare/5 fps, banana as story |
| `64c935d` | Group B art: `break_face` r3 (recoloured), `break_head` r2, `panic` r1, `celebrate_collapse` r1 minus heap |
| `9843530` | no `idle` for the zombie: the ball-less still pose |
| `47f8794` | steal/stolen game code, Group C specs + guides |
| `2dcbeb4` | Group C art: `steal_r` r3, `steal_l` r1, `stolen` r1 played 1,3,2 |
| `81cc1f6` | zombie strips-only (MIXED empty) |
| (next) | this handover |

### The zombie now — every sequence the game plays is a strip

| sequence | source | frames | scale | notes |
|---|---|---|---|---|
| `celebrate` | h10 r3 | 2 | ×1.07 | flat-footed triumph, fist-at-shoulder settle |
| `celebrate_pump` | h10 r1 | 3 | ×1.12 | |
| `gameover` | h10 r1 | 2 | ×1.18 | "looks more tired"; r2's heave "too much" |
| `break_face` | h10 r3cc | 4 | ×1.10 | story; recoloured; X-legs |
| `break_head` | h10 r2 | 4 | ×1.08 | story |
| `panic` | h10 r1 | 4 | ×1.15 | story, holds 3–4 |
| `celebrate_collapse` | h10 r1noheap | 5 | ×1.15 | rare (0.12), 5 fps; heap frame removed |
| `steal_r` / `steal_l` | h10 r3 / r1 | 3 | ×1.06 / ×1.12 | 8 fps, every press |
| `stolen` | h10 r1 [1,3,2] | 3 | ×1.15 | 6 fps, any key cancels |
| `idle` | — | | | **removed** — without the ball he holds `dribble_idle` frame 3, as the monkey does |
| earlier (h04–h09) | | | | dribble, runs, pickup, turn/aim/charge/shot unchanged |

✅ `test-game.py` ALL PASS, 60 fps. ✅ `sweep-shots.py`: zombie 3.9% (unchanged). ✅ Filmed in play:
celebrations, win lap, breaks, panic with and without ball, collapse, steals both ways (zombie vs
zombie), a miss, running/aiming left (the "13" reads forwards).

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **Group A specs** (zombie's own `celebrate`, `celebrate_pump`, `gameover`) | Traced off the monkey; unit rescaled by 1/1.10 (the monkey upright is 1.10 of h09's unit). Front-view note `&frontnote`; a `back: true` head marks the hanging crown in `gameover` 1. |
| 2 | **Story sequences** (`index.html` `storyStart/storyFrame`, `STORY_SEQ`) | §0(A). Breaks end after their last frame; panic holds. |
| 3 | **Group B specs** | Dribbling hand moved to the viewer's LEFT (it was still RIGHT), two hand positions, `&dribnote`. Collapse prose-only. |
| 4 | **Celebration C** | `CELEB_HZ.celebrate_collapse = 5`, `CELEB_RARE … = 0.12`. |
| 5 | **No ball-less loop** | `idle` entry removed from `slice-strips.py`; its frames moved to `build/retired/`. |
| 6 | **Steal / stolen** (`index.html` `trySteal`, `STEAL_HZ`, `STOLEN_HZ`, `STEAL_REACH`) | Lunge toward the opponent on every press; a hit carries the ball opponent → swiping hand (mid-lunge) → top of own dribble, no pickup; victim plays `stolen`, cancelled by any key. Characters without the art behave as before. |
| 7 | **Group C specs** (shared, `sequences.yml`) | Generic, one-handed, per side; frame 3 of all three = the still pose. Old front-view `steal` spec replaced. |
| 8 | **Strips-only zombie** | MIXED empty; manifest identical except `mirror`/`fixed`. |
| 9 | Tools | `recolour-take.py`, `preview-story.py`, `preview-oneshot.py`. |

---

## 3 · ⭐ THE PROCESS (unchanged from h09 §3, plus)

- Where the monkey has it: match like for like (h09). Where nobody has it: **spec review with the
  game's timing spelled out** (how often it plays, how fast, what cancels it) — every Group B
  decision came from that.
- Draw the wireframes and look at them before generating; stretched-limb warnings from
  `make-pose-guide.py` above ~15% mean the pose is unreachable — move the hand, not the arm length.
- One batch per group via Codex `Start-Process` (chain two runs with `cmd.exe /c "… & …"` when a
  sequence needs a different `--rolls`). A failed roll is resumable: rerun the same command.

---

## 4 · ⛔ Traps: additions only; handovers 01–09 stand

- ⛔ **Rick's C: drive filled to 0 bytes mid-build** (`[Errno 5] Input/output error`), leaving
  `sprites/` half-written. He cleaned it (2.9 GB free at the end). **`df -h .` before any build or
  batch.** `build/capture`, `build/review`, `build/preview` were deleted to recover — regenerable.
- ⛔ **`build-sprites.py` can exceed the 180 s device_bash limit** on his slow disk: run it with
  `nohup … &` and poll, or it is killed half-way with no `manifest.js`.
- ⚠ **Git read commands from the device shell (`git status`, `git diff`) leave a stale empty
  `.git/index.lock`** that blocks Rick's own git. Check for it and `rm` it after every git call
  (delete permission needed).
- ⚠ ChatGPT occasionally times out a roll (416 s) or receives the guide without the reference; the
  run continues; rerun later to fill the gap.
- ⚠ In headless films, a sequence's first frames may not be decoded at screenshot time — prime
  them (set opacity 1, wait, restore) and **never** clear `p.shown`, which leaves a ghost frame.
- ⚠ PIL merges identical consecutive GIF frames: index into a filmed GIF by duration, not by count.

---

## 5 · ⛔ Open, ranked

| # | what | how |
|---|---|---|
| **1** | ⛔ **Push** | the seven commits in §1 + this handover. |
| **2** | Play-test the new work in real matches | especially break A's X-legs snap, the panic hold, steal feel, and the banana at half speed (its hand rises once over two bounces — Rick to judge). |
| **3** | **The next character** (NBA player or high schooler) | Same pipeline, zombie as the template: add it to `MIXED`, then groups as for the zombie. Their celebrations/panic/breaks are already specified in `characters.yml` (h08). Steal/stolen specs are shared — only the art is per character. |
| 4 | Identity drift detector | h08 §6 #3, still open; `recolour-take.py` covers colour, not face. |
| 5 | Carried over | h07 §6 #5–#7, h08 §6 #5. |

---

## 6 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **`df -h .`, `git status`, remove any stale `.git/index.lock`, push. Then ask Rick which character
> is next.**

```
cd C:\Git\throw-a-basketball
git status
git push
py tools\preview-story.py break_face --approved --scale 1.10
py tools\preview-oneshot.py stolen 1,2,3 --fps 6
py tools\recolour-take.py "<poses>\dribble_idle.approved.png" "<poses>\X.rN.png" "<poses>\X.rNcc.png"
python -m http.server 8899   then   python tools\test-game.py
```
