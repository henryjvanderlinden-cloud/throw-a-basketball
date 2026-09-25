# Throw a Basketball — Handover 08: **the zombie stands at full size, and picks the ball up with both hands**

## Handover for a fresh session (2026-09-25, late evening)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The zombie's stationary dribble and ball-less idle were drawn with a body about a tenth
> smaller than every other sequence; they are now scaled ×1.12 and ×1.08, which also fixed
> handover 07's one failing test.** ⭐⭐ **The zombie has a pickup: face-on, two-handed —
> reach, scoop between the feet, gathered in front of the waist — r1 of the first batch, picked
> by Rick.** ⭐ **The ball now goes into the hands during a pickup, for the monkey too: it used
> to start dribbling the instant he reached it, bouncing up at his side while his hands were
> still at the floor.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) A CALIBRATION FRAME CAN BE DRAWN OUT OF PROPORTION TO THE BODY BESIDE IT.
Rick: *"the zombie is smaller when he is in idle dribble and in idle non-dribble. They should be
sized up."* Every strip is scaled so its calibration frame (00.png) is 132 units tall, and the
rest of the strip inherits that scale — but the model does not always draw the calibration pose
at the same scale as the body next to it. Measured at in-game scale:

| sequence | the "13" | shoes | correction |
|---|---|---|---|
| runs, aim, shot | 19–20 px | 44–46 px (aim 34/45) | — |
| `dribble_idle` (subtle r3) | **17 px** | — | **×1.12** |
| `idle` (r3) | 18–20 px, head ~8% short | — | **×1.08** |
| `pickup` (r1) | 18 px | **41–42 px** | **×1.06** |

⭐ **Rule: after building any new zombie sequence, lay its frames beside a run and the aim at
in-game scale (the sprite PNGs, one baseline) and compare the "13", the shoes and the head.**
Silhouette height does NOT tell you — a crouch is short on purpose. The digit heights come
from a connected-component pass over yellow pixels (scipy, in the cloud workspace; the device
VM has no scipy).

The fix is `SEQ_SCALE` in `tools/build-sprites.py`, which until now only applied to strips
WITHOUT a calibration frame. It now multiplies the calibration scale too; `standH` stays at
132, so the ball's bounce is unchanged. Set by eye from a sheet of candidates (×1.00/1.08/
1.12/1.16) — Rick accepted the recommendation in one line.

> ### ⭐⭐ (B) THE BALL AND THE ART MUST AGREE FRAME BY FRAME, NOT ONLY IN THE LOOPS.
Filming the monkey's existing pickup showed the ball rising beside him on its own while both
his hands were at the floor between his feet — the dribble started in `giveBall()`. Now:

- `PICKUP_BALL` in `build-sprites.py` (→ `pickupBall` in the manifest): one `[out, up]` per
  pickup frame. `out` is a share of the dribble's lateral distance (0 = between the feet, 1 = out
  on the `BALL_SIDE["pickup"]` side), `up` the ball centre's height as a share of `standH`
  (0 = resting on the floor). Monkey `[[0,0],[0,0],[1,0.42]]`; zombie `[[0,0],[0,0],[0,0.42]]`
  (0.47 hid the "13" and sat above r1's hands).
- In `index.html` `step()`: during the pickup the ball goes there, `dribT` is held at π/2 so the
  first bounce starts from the hand, and during that first drop the ball slides from where he
  gathered it to the dribbling side of whatever follows (`p.gatherX`).
- ⭐ **He can reach a ball lying up to ~40 units to one side** (`PICKUP_DIST` 62 is measured to
  mid-body). The ball used to snap in on the first frame; it now slides in during frame 1
  (`p.reachX`, set in `giveBall`).
- A character with no `PICKUP_BALL` entry keeps the old behaviour.

⭐ **Any one-shot where the character touches the ball (`steal`, `stolen`, `aim`, `shot`) should
be checked the same way: film it, frame by frame, and look at the hands.**

> ### ⭐ (C) CHECK THE WORKING TREE BEFORE STARTING.
Midway through this session the whole pickup — guide, prose, ball code and three rolls — turned
out to be already on disk, uncommitted, written 18:45–18:54 by another branch of the
conversation with exactly the accepted defaults. It was reviewed and adopted, not redone.
**`git status` and the mtimes of `art/`, `index.html` and `Zombie poses/` first, every session.**

> ### ⭐ (D) IDENTITY DRIFT CONTINUES.
Pickup r2 went skull-faced with glowing eyes (the others kept the rotted face). Six of the last
nine zombie rolls have now drifted. Still nothing flags it automatically (§6 #3).

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, on `main`. HEAD is this handover's commit, on top of:

| commit | what |
|---|---|
| `1c7d96d` | zombie `dribble_idle` ×1.12, `idle` ×1.08; `SEQ_SCALE` applies to calibrated strips |
| `40ffb96` | zombie `pickup` (r1, ×1.06); the ball follows the hands during any pickup |
| (next) | this handover |

⛔ **Three commits unpushed** (Rick pushed handover 07's five at the start). Rick pushes.

### In the game (zombie)

| sequence | source | frames | notes |
|---|---|---|---|
| `dribble_idle` | subtle r3, handover 07 | 4 | **×1.12**; apex 3; ball viewer's LEFT |
| `idle` | r3, handover 05 | 2 of 4 | **×1.08** |
| **`pickup`** | **r1, this session** | **3** | **×1.06; two-handed, face-on; `pickupBall`** |
| `run_dribble_r` / `_l` | handover 04 | 4 | |
| `run_r` / `run_l` | handover 06 | 4 | |
| `aim`, `charge`, `shot` | the eight OLD poses | | still legacy art |

✅ Filmed: pickup standing, running right, running left, for the zombie AND the monkey; the ball
meets the hands in every frame and hands over smoothly to `dribble_idle` / `run_dribble_r` /
`run_dribble_l`. ✅ `tools/test-game.py` **ALL PASS**, 60 fps; the picker row is now
`[140, 124, 124, 112]`, so "the monkey is the shortest" passes again.

### Reproducibility

```
art/sequences.yml            f1fb8ed42a757acb55eb2900e7148080
art/guides/pickup.png        d863fecf5c049ec35edc6715be293470
art/guides/dribble_idle.png  397c585dd71aa292df9341980a01622a   (unchanged)
art/guides/idle.png          4df0b4795d5e30bcac5e26c0d7d630a4   (unchanged)
```
Prompt hash: `pickup` **040812742f69** = `pickup.approved.json`.

### The takes (untracked except `approved`)

`pickup.r1`–`r3`, `approved` = **r1**. Previews in `build/preview/pickup.r*/` (sheet + loop).

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **Per-sequence correction on calibrated strips** | ✅ `SEQ_SCALE` × calibration scale; zombie `dribble_idle` 1.12, `idle` 1.08, `pickup` 1.06, each with its measurement in a comment. |
| 2 | **`pickup` guide + prose** | ✅ Face-on (`nose`/`ears`, the "reference does not set the facing" sentence), calibration + 3, amplitude from the monkey (head top at 0.87 / ~0.75 / 0.99 of his dribbling height), the forward bend drawn with `joints` (shoulders dropped below the plain `drop`), both hands a ball's width apart (0.197 of standing), frame 3 two-handed and centred. |
| 3 | **Ball follows the pickup** | ✅ §0(B). `pickupFrame()` shared by `step()` and the drawing. |
| 4 | **Slide-in on reach** | ✅ §0(B), last bullet. |
| 5 | **The take in the game** | ✅ `slice-strips.py` entry, `pickup.approved.*` committed, sprites built. |

---

## 3 · ⭐⭐ THE PROCESS, AS RUN THIS SESSION

1. **Measure before the spec** — sizes against runs/aim for the resize; the monkey's pickup
   heights and an **in-game film of the monkey's pickup** before writing the zombie's. The film
   is what exposed the ball bug.
2. **Spec review as a numbered list with defaults** — Rick answered "default".
3. **Rolls** (done by the other branch, §0(C)): three via Codex, ~2 min each this time.
4. **Sheets and loops for every roll** — `preview-take.py --cells 4 --hz 10`. ⚠ its feet table is
   meaningless for frame 2 of a pickup: the hands are in the shoe band.
5. **In-game film per direction**, in the cloud workspace from a tarball; a throwaway Playwright
   script put the ball loose at `px ± 150` and held the direction (standing: `px + 12`, since
   pickup distance is measured to mid-body). Worth folding into `capture-game.py` as
   `--loose <dx>` next time.

---

## 4 · ⭐ BEST PRACTICES: additions to handover 07 §4

29. ⭐⭐ **Size check after every build** (§0(A)): "13", shoes, head, at in-game scale, beside a
    run and the aim.
30. ⭐⭐ **Film anything that touches the ball, frame by frame** (§0(B)), for every character that
    has the sequence — a fix for one character's art is often a game-code fix for all.
31. ⭐ **Hands placed around where the GAME puts the ball**: take the ball's size from `BALL_R`
    over `standH` (0.197), and its positions from the per-frame table, not from the prose.

---

## 5 · ⛔ Traps: **additions only; handovers 01–07 stand**

- ⚠ **Uncommitted work from another branch can be sitting in the tree** (§0(C)).
- ⚠ `pkill -f "http.server 8899"` inside a Bash call kills that call's own shell (its command
  line matches). Start the server once and reuse it.
- ⚠ Delete permission was lost to an MCP reconnect again mid-session; re-request, then
  `rm -f .git/index.lock` before and after device-side git.
- ⚠ `slice-strips.py pickup` re-slices the MONKEY's pickup too (same name); it came out identical.

---

## 6 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **Push** | Three commits. Rick pushes. |
| **2** | ⭐⭐ **The shooting chain: `turn`, `aim`, `charge`, `shot`** | Next in play order after the pickup, and still the old eight-pose art. Measure the monkey's versions first (§4 #25), film the ball against the hands (§4 #30), size-check (§4 #29). `turn` goes front → back, so the facing pull (07 §0(C)) is at its strongest. |
| **3** | ⭐ **An identity check** | Six of nine recent rolls drifted to a skull face (§0(D)). |
| **4** | **The rest of the roster** | `steal`, `stolen`, `celebrate`, `celebrate_pump`, `gameover`, and the zombie's own `panic`, `break_face`, `break_head`, `celebrate_collapse`. |
| **5** | `capture-game.py --loose <dx>` | §3 #5. |
| **6** | Carried over | 07 §6 #5–#7 unchanged. |

---

## 7 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **`git status`. Push. Then a numbered spec review for `turn` (or the whole shooting chain),
> starting from a measurement of the monkey's and a film of how the game plays it now.**

```
cd C:\Git\throw-a-basketball
git status
git log --oneline -4
git push
py tools\make-pose-guide.py --seq pickup                  # d863fecf...
py tools\gen-prompts.py                                   # pickup 040812742f69
py tools\preview-take.py "artwork\basketball-players\Zombie poses\pickup.approved.png" --cells 4 --hz 10
python -m http.server 8899   then
python tools\capture-game.py --p1 zombie --p2 nba --watch 0 --start --script=-:1,right:0.8,-:1,left:0.8,-:1.4
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **Rick's size complaint looked like a crouch and was a scale error**: the body itself was
> drawn small, and only a side-by-side at in-game scale showed it. ⭐ **Filming the monkey
> before specifying the zombie found a bug nobody had seen in seven sessions**, because every
> earlier check looked at the pickup art, never at the ball during it. ⛔ **What went wrong**: I
> started rewriting the pickup spec without checking the working tree and nearly overwrote a
> finished, better-commented version; caught on the diff, adopted instead.
