# Throw a Basketball — Handover 12: **the art is finished; from here on, tuning**

## Handover for a fresh session (2026-09-27, evening)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **All four characters now have all twenty sequences: the high schooler's whole roster
> (`20412d7`) and the monkey's steals and head-scratching stolen reaction (`22e80c4`).**
> ⭐⭐ **The art pipeline is closed; Rick is now tweaking the game, starting with timing.**
> ⭐ **This handover is a map of where the tuning knobs are and how to check a change —
> the lessons of the whole art effort are in `lessons-learned/LESSONS_LEARNED.md`.**

---

## 1 · Where we stand

Repo `C:\Git\throw-a-basketball`, `main`. `20412d7` and `22e80c4` are pushed; ⛔ this handover
and the lessons learned are not (Rick pushes).

| character | sequences | notes |
|---|---|---|
| monkey | 20 | 17 hand-made strips (no calibration frames) + steal_r r1, steal_l r2, stolen r1 (guided) |
| NBA player | 20 | handover 11 |
| high schooler | 20 | picks in `tools/slice-strips.py` STRIPS comment; dribble held at x1.10 so the picker still shows the NBA player tallest |
| zombie | 20 | handover 10 |

✅ `test-game.py` ALL PASS, 60 fps. `sweep-shots.py`: monkey 3.5%, NBA 4.3%, high schooler 4.0%,
zombie 3.9%. Rick play-tested the high schooler: "great"; timing issues to be worked on.

⚠ The monkey's subject in `characters.yml` was rewritten twice this session (face, then a lighter,
cheekier temperament). His 17 older strips predate it and were not regenerated; if he looks
different between those and the new steals, that is why.

---

## 2 · ⭐⭐ Where the timing lives (`index.html` unless noted)

| what | constant | now |
|---|---|---|
| dribble cadence, standing / running | `p.dribT += dt * (vx !== 0 ? 9 : 7)` (~l.2553) | 7 / 9 rad/s; one bounce is π |
| story frames (breaks, panics) | `STORY_SECS = HALF_BEAT / 7` | ~0.22 s a frame |
| other loops | `ANIM_HZ` | aim 2.6, run 7, gameover 2.5, panic 6, idle 2.5 |
| celebrations | `CELEB_HZ`, `CELEB_HZ_DEFAULT`, `CELEB_RARE` | showpieces 5 (flip 8), others 2.5; rare 0.12 |
| idle breaks | `BREAK_MIN`, `BREAK_MAX`, `BREAK_CLOCK_FLOOR` | 2–4 s, not under 4 s on the clock |
| panic | `PANIC_CLOCK` | under 2 s |
| turn / pickup | `TURN_TIME`, `PICKUP_TIME`, `PICKUP_LOCKOUT` | 0.36 / 0.30 / 0.35 s |
| steal / stolen | `STEAL_HZ`, `STOLEN_HZ`, `STEAL_CD`, `STEAL_IMMUNE` | 8 / 6 fps; 0.5 s; 0.9 s |
| shooting | `CHARGE_RATE`, `AIM_RATE`, `RISE_HOLD` | full power ~1.05 s; 62°/s |
| shot clock | `CLOCK_BASE`, `CLOCK_FLOOR`, `CLOCK_STEP`, `PTS_PER_STEP` | 10 s → 3 s |
| victory | `VICTORY_PANTS` | 3 |

Per-character, in `tools/build-sprites.py` (needs a rebuild): `STORY_SEQ` (which sequences are
stories and which frames a panic holds), `APEX_FRAME` (which frame meets the ball at the top of the
bounce), `LOOP_BOUNCES` (runs: two bounces a loop), `SEQ_SCALE` (sizes).

---

## 3 · How to check a change

```
cd C:\Git\throw-a-basketball
python -m http.server 8899                     # then open http://localhost:8899/
py tools\build-sprites.py                      # only after build-sprites.py / art changes; slow: run in the background
python tools\test-game.py                      # headless suite (cloud container: stage a tar of index.html sprites splash audio tools artwork/basketball-courts artwork/overlays)
python tools\sweep-shots.py                    # after anything that touches shooting
python tools\capture-game.py --p1 zombie --p2 monkey --watch 1 --start --script=-:0.5,down:0.15,-:1.2
```

`capture-game.py` pumps the game clock in exact 1/60 s steps and writes a loop GIF and `shown.txt`
(which sequence and frame was drawn each step) — the tool for timing questions, since it shows
exactly how long each frame is held.

---

## 4 · ⛔ Traps (additions only; handovers 01–11 stand)

- Disk: 3.5 GB free. `df -h .` before a build.
- `.git/index.lock` left by git in the VM: remove it after git commands (delete permission lapses on
  reconnect; re-request it).
- `run_dribble_l` timed out twice for the high schooler (no image returned in 7 min); rerunning the
  same command fills only the gap.
- The capture script's `--script` value must be passed as `--script=...` when it starts with `-`.

---

## 5 · Open

| # | what |
|---|---|
| 1 | ⛔ Push this handover and `lessons-learned/`. |
| 2 | Timing tweaks (Rick). §2 is the map. |
| 3 | Play-test the monkey's steals and stolen in a match (only `steal_r` was filmed). |
| 4 | Optional: regenerate the monkey's 17 older strips on the guided pipeline, for calibration frames and a consistent face. Not asked for. |
| 5 | Carried over: identity-drift detector (h08 §6 #3); `LEGACY_POSES`/`POSE_SCALE` in `build-sprites.py` are now unused by any character and could be removed. |
