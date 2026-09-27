# Throw a Basketball — Handover 11: **the NBA player is finished — on his own body, with his own face**

## Handover for a fresh session (2026-09-27, midday)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **The NBA player has all 20 sequences in the game, strips-only like the zombie: 57 rolls in one
> batch, every pick Rick's, committed as `8239d45`.** ⭐⭐ **Pose guides can now be drawn on a
> character's OWN body (`skeleton:` in `characters.yml`, guides in `art/guides/<char>/`); the
> zombie's guides and prompts came out byte-for-byte unchanged.** ⭐⭐ **The face is described in
> words in the SUBJECT block, not left to the reference: the first pilot drew him "too Caucasian and
> too serious", and one rewrite of the subject fixed every later roll.**

---

## 0 · ⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) DESCRIBE THE FACE AND THE TEMPERAMENT IN THE SUBJECT BLOCK.
The old subject said "a stern set jaw" and nothing about the face itself; the model filled the gap
with a generic, severe face. Rick: *"too caucasian and too serious … he is playing this game on easy
mode, against easy adversaries."* The subject now names his ethnicity, describes the face as the
reference draws it (broad, full, rounded, full cheeks, heavy brow, broad nose, full lips) and sets a
resting expression (a confident half-smile, never a scowl). Every expression line in his copied
sequences was rewritten to match (laughing triumph, lazy grin at the clock). **Do this for the high
schooler before the pilot**, not after it. Rick's standard after r3: *"Now you know what to look for."*

> ### ⭐⭐ (B) A GUIDE DRAWN ON THE WRONG BODY PULLS THE BUILD.
`make-pose-guide.py`'s skeleton constants are the zombie's. A character whose build differs carries
`skeleton:` (keys `sh_x hip_x head_r head_up free_hand bald`) in `characters.yml`; `--char <key>`
then draws on that body into `art/guides/<key>/`, and `gen-prompts.py` attaches those.
Frame tables stay the zombie's numbers; shoulders placed by `joints` scale with `sh_x`, elbows ride
along, hands placed by `hand`/`free` do NOT move (they are where the ball/knees/fists are). His own
sequences, written for his body, say `native: true` beside `file`. Measure the proportions off the
reference on a grid in shares of standing height (NBA: shoulders ×1.3 the zombie's, hips ×1.12,
smaller shaved head). The high schooler is slim and lanky — **measure him; he may be narrower than
the zombie**, not wider.

> ### ⭐ (C) HAIR LINES ARE TRAITS NOW.
The guide notes' hair sentences became `{guide_hair}`, `{guide_hair_out}`, `{hair_still}` in
`sequences.yml`, filled per character in `traits`. The NBA player (bald) says "shaved smooth; the
guide draws no hair". The high schooler has hair: give him the zombie's wording, or say "messy hair
swept forward".

> ### ⭐ (D) THE ECHO GUARD THREW AWAY TWO REAL STRIPS.
`gen-strips.py` rejected any download with the guide's aspect ±0.5%. A three-cell guide is
1260×562 (2.24); celebrate came back 1881×836 (2.25). Fixed: an echo must also be no larger than the
upload. Re-rolled cleanly. If a batch reports "failed" with "ignoring an echo" lines, check sizes.

---

## 1 · Where we stand

Repo `C:\Git\throw-a-basketball`, `main`. ⛔ **Unpushed** (Rick pushes):

| commit | what |
|---|---|
| `8239d45` | the NBA player's whole roster; per-character skeletons; echo-guard fix |
| `dc4a389` | tab title and mode-select heading "Throw A Basketball" (were "Hoop Shooter") |
| (next) | this handover |

### The NBA player now (all h11, all ×1.00 unless noted)

| sequence | pick | scale | notes |
|---|---|---|---|
| `dribble_idle` | pilot 2 r3 | ×1.10 | the face reference for everything after |
| `run_dribble_r` / `_l` | r3 / r2 | | |
| `run_r` / `run_l` | r2 / r3 | | |
| `pickup` | r2 | | `PICKUP_BALL` as the zombie |
| `turn` `aim` `charge` `shot` | r2 r2 r1 r2 | .97 .97 1.00 .97 | charge r1: "the pants look better" |
| `celebrate` / `celebrate_pump` | r3 / r3 | — / 1.06 | |
| `gameover` | r2 | 1.10 | "the face looks better" |
| `break_flex` / `break_yawn` | r1 / r1 | 1.06 / 1.07 | stories |
| `panic` | r2 | 1.03 | 6-frame story: look, cock, thumb, hold, hip, hip; holds [4,5] |
| `celebrate_crowd` | r1 | 1.04 | rare 0.12, 5 fps |
| `steal_r` / `steal_l` | r2 / r2 | 1.10 / 1.04 | |
| `stolen` | r3 [1,3,2] | 1.04 | look, look, clench (the snarl kept) |

✅ `test-game.py` ALL PASS, 60 fps. ✅ `sweep-shots.py`: NBA **4.3%** (was 4.0%; release point
moved), zombie 3.9% unchanged. ✅ Filmed: dribble, yawn break, run right, pickup, aim, charge, shot.
⚠ Not yet seen in a match: celebrations, panic, steals, buzzer — Rick to play-test, sizes especially
(set by eye against his runs; the dribble came out drawn small, like the zombie's).

Old rolls: `dribble_idle.b1r1–3` is the stern-face pilot (b1r2 was Rick's first pick).

---

## 2 · ⭐ THE PROCESS (as run; use it for the high schooler)

1. `df -h .`, `git status`, clear `.git/index.lock` (delete permission lapses on MCP reconnects —
   re-request it).
2. Grid the reference (tenths of standing height) → `skeleton:` block → spec review with numbered
   defaults (Rick answered "default").
3. **Pilot `dribble_idle` alone, 3 rolls**, face close-ups beside the reference. Fix the subject
   until the face is right. Approve.
4. His own sequences rewritten as stories (dribbling hand viewer's LEFT, two positions 0.42/0.095
   and 0.30/0.12); copies of the zombie's turn/aim/charge/shot/celebrate/celebrate_pump/gameover
   with his faces. Guides for all 20; check stretch warnings (fix elbows with 2-link IK, not arm
   length).
5. One detached batch of 57 via Codex `Start-Process` (~2 h, ~2 min a roll).
6. Review per group with `~/work/review.py`-style script: preview-take per roll, a sheet of the
   three, and the three loops side by side in one GIF. Identity first (face, kit, shoes — white
   trainers were the commonest drift), then pose. "Figures touch" in the preview is not a slicer
   failure.
7. Approve, `slice-strips.py` entries (slice only that character via `slice_character`), build-sprites
   config (`BALL_SIDE`, `APEX_FRAME`, `LOOP_BOUNCES`, `STORY_SEQ`, `PICKUP_BALL`, `SEQ_SCALE`),
   `CELEB_HZ`/`CELEB_RARE` in `index.html` for the showpiece. Build with `nohup … &`.
8. Size sheet at in-game scale against the dribble and the runs; tar → cloud → `test-game.py`,
   `sweep-shots.py`, a filmed match. Commit on the device.

---

## 3 · ⛔ Traps: additions only; handovers 01–10 stand

- ⛔ Disk hovered at 4.9–5.6 GB free; the batch plus builds cost ~0.7 GB. Check before each run.
- ⚠ Regenerating shared guides to verify them re-encodes the PNGs (git shows them modified though
  pixel-identical): `git checkout -- art/guides` afterwards (needs delete permission).
- ⚠ The high schooler's poses folder is misspelled on disk (`Higschooler poses`); `folder:` in
  `characters.yml` and `CHARACTERS` in `build-sprites.py` already use it. His frames folder will be
  `Higschooler frames`, and the `STRIPS` key in `slice-strips.py` must be `"Higschooler"`.

---

## 4 · ⛔ Open, ranked

| # | what | how |
|---|---|---|
| **1** | ⛔ **Push** | `8239d45`, `dc4a389`, this handover. |
| **2** | Play-test the NBA player | sizes, panic hold, crowd showpiece, steals. |
| **3** | ⭐⭐ **The high schooler** | §2, from the top. His own four are specified in `characters.yml` (h08): `break_phone`, `break_hair`, `celebrate_dab` (showpiece), `panic` (hands on head then up, big eyes, sweating). They predate stories: rewrite them as the NBA player's were. Rick's temperament for him is not yet stated — **ask** (teenager, eager? nervous?) before the pilot, and describe his face in the subject. When done, `LEGACY_POSES` is empty and the old eight-pose code path is unused. |
| 4 | Identity drift detector | h08 §6 #3, still open. |
| 5 | Carried over | h07 §6 #5–#7, h08 §6 #5. |

---

## 5 · Output spec

> ### ⭐⭐ THE ONE THING TO DO FIRST
> **`df -h .`, `git status`, clear the lock, push. Then ask Rick about the high schooler's
> temperament and face, grid his reference, and propose his `skeleton:` and the pilot.**

```
cd C:\Git\throw-a-basketball
git push
py tools\make-pose-guide.py --seq dribble_idle --char highschooler   # once he has skeleton:
py tools\gen-prompts.py
py tools\gen-strips.py --char highschooler --seq dribble_idle --rolls 3 --slow --dry-run
py tools\preview-take.py "artwork\basketball-players\Higschooler poses\dribble_idle.r1.png" --cells 5 --hz 9
python -m http.server 8899   then   python tools\test-game.py   and   python tools\sweep-shots.py
```

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The first pilot looked right to me and wrong to Rick** — I checked build, kit and pose, and read
> the face only for "likeness", not for who he is. The subject block had asked for a stern jaw and
> never described the face; one rewrite fixed it for all 57 rolls that followed. ⭐ The per-character
> skeleton was the one piece of new machinery, and it paid for itself: no roll came back slimmed
> down to the zombie's frame.
