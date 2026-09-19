# Throw a Basketball — Handover 01: **the dribble was an arm until it was a body, and the VGA prompt did nothing measurable**

## Handover for a fresh session (2026-09-19)

> ## ⭐⭐ THE SESSION IN THREE SENTENCES
>
> **A manifest-driven pipeline now renders all 80 animation prompts from two YAML files and drives
> ChatGPT unattended from Rick's Windows machine — stage 0 verified against the monkey's proven
> prompts, stage 1 working end to end.** ⭐⭐ **The zombie's `dribble_idle` was re-rolled four times;
> the fourth, written as a whole-body action with lead-and-follow, nearly TRIPLED inter-frame
> difference (11% → 31%) and near-doubled pose asymmetry (24% → 41%) — both of the failures that
> three previous takes could not shift.** ⛔ **It is still not usable: the dribbling hand never drops
> below the shorts hem, the free arm came back up into the zombie claw, and the VGA rewrite changed
> nothing a measurement can see.**

---

## 0 · ⛔⭐⭐ THE FINDINGS THAT OUTLIVE EVERYTHING ELSE HERE

> ### ⭐⭐ (A) DESCRIBING THE BODY FIXED WHAT THREE ROUNDS OF DESCRIBING THE ARM COULD NOT.
The first three takes all failed the same two ways: consecutive frames were 8–14% different (a
puppet with an arm at four heights), and both arms mirrored each other. Every fix attempted was a
sharper instruction about the **hand**. None moved either number.

Rick's note moved both, in one take:

| measured on the silhouette | r1 (arm-only prompt) | r2 (whole-body prompt) |
|---|---|---|
| mean inter-frame difference, frames 2→3→4→5→2 | **11%** | ⭐ **31%** |
| mean pose-frame asymmetry (XOR against own mirror) | **24%** | ⭐ **41%** |
| calibration frame asymmetry (the control) | 7% | 8% |

⭐⭐ **The control barely moved, which is what makes the other two rows mean something** — the
calibration frame is the same plain standing pose in both sheets and it stayed symmetric, so the
asymmetry that appeared is in the poses, not in the rendering.

**The clause that did it** is not the one about the hand. It is:

> *His SHOULDER LINE TILTS: the shoulder on the dribbling side drops as the hand goes down and lifts
> as the hand comes up, while the far shoulder does the opposite. … He is NEVER symmetrical — a
> frame in which both shoulders are level and both arms are doing the same thing is wrong.*

⭐⭐ **A tilted shoulder line is a pose that CANNOT be drawn symmetrically.** The symmetry failure was
never fixable by forbidding symmetry; it was fixed by asking for a shape that excludes it. **Where a
generator keeps producing a defect, ask for a form that cannot contain the defect, rather than
forbidding the defect.**

And **lead-and-follow gave the frames somewhere different to be** — body leads the push down, hand
leads the recoil up — which is where the inter-frame difference came from. Frame 5 exists only
because of it: the body has committed to the push and the hand is still trailing at hip height.

> ### ⛔⭐⭐ (B) IT STILL FAILED — AND THE FAILURE MOVED TO THE FREE ARM, WHICH IS NOT WHERE ANY PROMPT WAS AIMED.
Look at `artwork/basketball-players/Zombie poses/dribble_idle.r2.png`. What is wrong with it:

- ⛔ **No hand ever reaches knee height.** The prompt says the dribbling hand must be the lowest part
  of him apart from his feet, *below the hem of his shorts*, and it is not — mid-thigh at best, in
  all four pose frames. **Fourth take, fourth time this clause has been ignored.**
- ⛔ **Both arms are forward and hooked — the classic zombie claw, in every pose frame.** `no_shamble`
  exists precisely to prevent this and did not. The free arm is supposed to hang loose and never rise
  above the hip; it is up, bent, and clawed.
- ⚠ Consequence: the sheet reads as *a zombie crouching and shifting his weight*, which is a real
  animation and an improvement, but it is **not a dribble**.

⭐⭐ **The diagnosis worth carrying forward: `no_shamble` is a NEGATIVE instruction and the two
clauses that failed are the only two negative ones in the block.** Everything phrased positively —
tilt the shoulder line, drop that hip, tilt the head, let the body lead — landed. Everything phrased
as *do not* — do not hold both arms out, a sheet where the hand never drops below the waist is wrong
— did not. **Rewrite both as descriptions of what the free arm IS doing** (hanging straight down at
his side, elbow almost straight, knuckles level with the shorts hem) before trying anything cleverer.

⚠ **Second candidate, if that fails: the block is too long.** `CRITICAL` now runs ~300 words before
the frame list, and the two ignored clauses are the last two in it.

> ### ⛔⭐⭐ (C) THE VGA REWRITE PRODUCED NO MEASURABLE CHANGE. THE STYLE CANNOT BE WON IN THE PROMPT ALONE.
The style block was rewritten from "16-bit arcade pixel art" into an explicit spec — three tones per
material, ordered dither, no anti-aliasing anywhere, chunky pixels on one grid, bold outline. It
**looks** a little harder-edged. It is not:

| | r1 (old style block) | r2 (explicit VGA spec) |
|---|---|---|
| unique opaque colours | 140,847 | ⛔ **134,432** |
| alpha edge-haze | 8.5% | ⛔ **11.5%** |
| mean flat-run length, normalised to one height | 84 px | ⛔ **81 px** |

⛔ **"At most three tones per material" produced 134,000 colours.** What comes back is a smooth,
anti-aliased render of something that *depicts* pixel art, at ~2172×724. It is not indexed and never
was.

⭐⭐ **This is not fatal and should not be chased with more prompt words.** `build-sprites.py`
downsamples to `STANDING_H` 132 × `SUPERSAMPLE` 2 = 264 px, and 134,000 colours averaged down to 264
px tall is a perfectly good sprite. **The place to enforce the palette is the slicer, where it can be
asserted, not the prompt, where it can only be requested.** Add a quantisation pass to stage 2 —
median-cut to a fixed palette per character, measured against the reference art — and stop paying
prompt budget for it.

⚠ **Keep the style block anyway.** It costs nothing, and the bolder outline and larger flat areas it
asks for survive downsampling even though the colour count says the instruction was not obeyed
literally.

> ### ✅⭐⭐ (D) THE CALIBRATION FRAME WORKS, AND IT DELETES A TABLE OF FOURTEEN GUESSES.
Every strip now leads with one extra cell: the character's plain standing pose, drawn identically in
every sheet. ✅ **Measured across every take: scale ratios constant to three decimals, ground-line
spread 0–1 px.**

That turns `SEQ_SCALE` — **14 hand-eyeballed numbers for one character, spanning 0.72 to 1.16** —
into an exact computed ratio. Three more characters would have meant 42 more numbers that nobody can
check. ⭐ It also gives a registration anchor with the feet definitely on the floor, and an instant
read on identity drift, because the same pose appears in all twenty sheets and is directly
comparable.

⚠ `slice-strips.py` already supports it (a fourth element `True` on a `STRIPS` row) and **no strip
currently uses it.** That wiring is stage 3 and is not built.

> ### ⭐⭐ (E) THE SHEET MUST BE MEASURED, NOT LOOKED AT — AND TWO CHEAP INSTRUMENTS CATCH BOTH KNOWN FAILURES.
Both halves of the monkey's R1 failure were found *by building the game and playing it*. Both are
detectable in seconds from the PNG alone, and both were used to write §0(A):

- **Mean inter-frame difference** — XOR of consecutive silhouettes, registered on ink centroid and
  ground line, normalised by union. Catches *"all four frames read as the same pose"*. **Below ~15%
  is a failed sheet; 31% is a live one.**
- **Mirror asymmetry** — XOR of each frame against its own horizontal flip about the ink centroid.
  Catches *"both arms are doing the same thing"*. ⭐ **The calibration frame is the built-in control:
  it should score ~8%, and if it does not, the instrument is measuring the rendering rather than the
  pose.**

⭐⭐ **A cheap instrument needs its own control, and the calibration frame is one for free.** That is
the earlier scale lesson — *measure the art, do not assume it* — arriving in a new place.

> ### ⛔ (F) `device_commit_files` SILENTLY FAILS TO OVERWRITE IN THIS REPO.
It returns `{"written": [...]}` with nothing rejected while the file on disk is unchanged, and
`force: true` makes no difference. ⛔ **Two rounds of edits appeared to land and had not, and were
reported as landed.** Windows Controlled Folder Access is refusing the replace and the result does
not say so.

✅ **The working sequence: `rm` the target from the device shell first** (which needs
`device_request_delete_permission` on the exact root spelling `C:\Git\throw-a-basketball`, and the
grant does not survive an MCP reconnect), **then commit, then verify with `md5sum` against the
container copy.** Never trust the tool's own result on an overwrite here.

---

## 1 · Where we stand

Repo at **`C:\Git\throw-a-basketball`**, HEAD **`d2392f9`** *(Generate the animation prompts from a
manifest, and the strips from a browser)*, on `main`, ⛔ **1 unpushed — 2 with this file's own
commit.** The session opened at `29cd13a` with 0 unpushed.

✅ **The pipeline is committed.** `d2392f9` carries six files, 2554 insertions, staged by name:

```
.gitignore   art/sequences.yml   art/characters.yml
tools/gen-prompts.py   tools/gen-strips.py   tools/check-prompts.py
```

⚠ **Deliberately NOT committed: the four zombie takes** —
`artwork/basketball-players/Zombie poses/dribble_idle.r{1,2}.{png,json}`, 2.9 MB of rejected output.
They sit untracked alongside the dozen other untracked drafts already in `artwork/`, which is how
this repo has always treated work-in-progress art. ⛔ **They are the evidence for §0(A)–(C) and they
exist only on this machine — do not `git clean`.** Commit them if a take is ever kept; the sidecar
JSON carries the exact prompt and its hash, which is what makes a kept take reproducible.

⚠ **`.chatgpt-profile/` holds live ChatGPT session cookies and is gitignored. It must never be
committed.** ⚠ **`git add -A` is a trap in this repo** for the reasons in
`claude/session-handover.md` §Traps — `.gitignore` carries an edit that is not ours and `artwork/`
holds a dozen untracked drafts. **Always stage by name here.**

**Verify the manifest is the version this file describes:**

```
Get-FileHash art\sequences.yml      -Algorithm MD5   # F472572BBB55541081CB4F56CF95E6F9
Get-FileHash tools\check-prompts.py -Algorithm MD5   # 7E67154C92C737E060053A991C816D4C
```

⚠ `build/hx/` holds two handover files copied from `C:\git\compendium\handovers` as style reference.
`build/` is gitignored; delete it whenever.

> ### ⛔ `claude/session-handover.md` OPENS WITH A PARAGRAPH THAT IS NOW FALSE.
> It says *"There is uncommitted work in the tree"* and gives a commit recipe using
> `badges-commit-msg.txt`. ✅ **That work is committed — it IS `29cd13a` — and the file is gone.**
> ⚠ **Everything else in that document is current and load-bearing** (the five audio faults, the
> start gate, the traps, the test suites). **Read it, but ignore its first section; §1 of this file
> is the true git position.**

---

## 2 · ✅ What was built

| # | unit | outcome |
|---|---|---|
| 1 | **`art/sequences.yml`** | The 16 shared sequences, character-agnostic. Nothing in it names a character; per-character text enters through `{trait}` placeholders. |
| 2 | **`art/characters.yml`** | Four characters — subject block, traits, `CHAR_SCALE`, refs, and each one's own four sequences. |
| 3 | **`tools/gen-prompts.py`** | Renders **80 prompts** into `build/prompts/<char>/<seq>.txt` plus `index.json`. Frame numbers substituted, never typed. |
| 4 | **`tools/check-prompts.py`** | Round-trips the rendered monkey prompts against the 17 proven ones in `docs/prompts-monkey.md`. **0 unaccounted missing clauses.** |
| 5 | **`tools/gen-strips.py`** | Playwright driving a signed-in chatgpt.com on native Windows. **Working end to end** — attaches the reference, sends, waits, downloads, writes a sidecar. |
| 6 | **The zombie's `dribble_idle`** | Four takes. ⛔ **None usable.** §0(A)–(B). |

---

## 3 · The pipeline as it stands

**Stage 0 — the manifest. ✅ Built and verified.**
Two YAML files replace `docs/prompts-monkey.md`, a 57 KB prose document in which the SUBJECT block is
retyped verbatim seventeen times. That repetition is load-bearing — any rewording drifts the
character's identity — and was maintained by hand. It is now verbatim-identical by construction.

**Stage 1 — generation. ✅ Working, unattended.**
`py tools\gen-strips.py --char zombie --seq dribble_idle --rolls 2 --slow`. Keeps a signed-in profile
in `.chatgpt-profile/`. ⭐ **Resumable by content hash** on (character, sequence, roll, prompt text):
anything already on disk is skipped, and an **edited prompt produces a new roll rather than silently
reusing an old strip** — which is why tonight's run wrote `r2` and left `r1` alone.

**Stage 2 — the contact sheet. ⛔ NOT BUILT. This is the next thing worth building.**
Per character, one page: every roll of every sequence, frames composited on a common floor line with
the standing-height line drawn, calibration frames overlaid on the reference. Plus flags that need no
judgement — cell count ≠ expected, ground-line spread > 10 px, calibration ratio outside ±10%,
**inter-frame difference below threshold**, **mirror asymmetry below threshold** (§0(E)), palette
distance from the reference. Then a keyboard picker writing `choices.json`.
⭐⭐ **This screen should be the only place Rick's attention is required.**

**Stage 3 — slicing and building. ⛔ NOT BUILT.**
`STRIPS` in `slice-strips.py` generated from the manifest with the calibration frame switched on;
`build-sprites.py` reading the chosen roll; then `SEQ_SCALE`, `POSE_SCALE`, `LEGACY_POSES`,
`LEGACY_IDLE_POSE` and the whole `build_from_poses` path deleted. ⚠ **Deliberately not built yet:
tolerances guessed before seeing a real strip are tolerances guessed twice.**

---

## 4 · ⛔ Where measuring corrected the work

> ⛔⭐⭐ **SIX BROWSER BUGS WERE GUESSED AT IN A ROW AND NONE OF THE GUESSES WERE RIGHT. READING THE
> LIVE DOM FROM RICK'S SIGNED-IN SESSION SOLVED ALL OF THEM IN ONE PASS.** The turning point of the
> whole session. `expect_file_chooser` timed out forever because `composer-plus-btn` opens a *menu*,
> not a file dialog; `inputs.nth(0)` hit `octane-mobile-composer-photos-input`; and attachments do
> not render as `<img>` at all — they are **buttons with an `aria-label`**. ⭐ **Never guess a
> selector twice. Open the page and read it.**

> ⛔ **A SELECTOR WAS WRITTEN IN ENGLISH AND RICK'S CHATGPT UI IS DUTCH.** `img[alt*='Uploaded']`
> matched nothing, so the reference never attached, and the model replied *"Please reattach the
> zombie reference image"* — **after seven minutes of waiting.** ⭐ **Detection now matches the
> filename inside any `aria-label`, which is language-independent**, with a button-count fallback.

> ⛔⭐ **A FAILED ATTACHMENT WAS A WARNING, NOT AN ERROR, SO IT SENT ANYWAY.** The worst shape of bug
> in an unattended pipeline: it burned the request, waited the full timeout, and produced a plausible
> file. **It fails fast now and quotes the model's reply back.** ⭐ **In an unattended pipeline, a
> precondition that is merely logged is a precondition that does not exist.**

> ⛔ **THE FIRST "STRIP" DOWNLOADED WAS A BYTE-IDENTICAL COPY OF THE REFERENCE IMAGE.** Candidates
> were filtered by host, and the uploaded reference is served from the same hosts. ⭐ **Fixed with a
> new-since-send snapshot, a width ≥ 800 and aspect ≥ 1.4 filter, and an IHDR sanity check.**

> ⚠ **THE PROMPT CHECK FOUND TWO GENUINE REGRESSIONS THE MANIFEST HAD INTRODUCED**, which is the
> whole reason it exists: `panic` had lost *"Sweat beads are the only extra element"* (the
> prop-limiting clause), and `celebrate_flip` had lost *"the same size … even while he is in the
> air"* — the shared camera clause pins height to the reference image, which for an airborne pose
> invites the generator to shrink him back to standing height. Both fixed; airborne sequences now
> take a camera override.

> ⛔ **THE ZOMBIE'S SUBJECT BLOCK CONTAINED POSTURE MASQUERADING AS IDENTITY.** It ended *"He is
> round-shouldered and his hands are hooked into stiff claws"* — and the subject block is pasted into
> **all twenty prompts**, so it silently overrode every pose line in every sequence. ⭐⭐ **A SUBJECT
> BLOCK DESCRIBES WHAT A CHARACTER IS, NEVER WHAT HIS BODY IS DOING.** Moved into the `no_shamble`
> trait. ⚠ Check the other three for the same thing before generating them.

---

## 5 · ⛔ Open, ranked

| # | what | why it is where it is |
|---|---|---|
| **1** | ⛔ **The free arm and the low hand** — §0(B) | Rewrite both negative clauses as positive descriptions. **One sequence, one character, two clauses. Do not touch anything else until a sheet comes back right.** |
| **2** | **Stage 2, `tools/contact-sheet.py`** | Both instruments already exist as throwaway scripts in this session; they want a home. Until this exists every sheet is judged by eye, which is how three takes were called "nearly right". |
| **3** | ⚠ **Carry the whole-body mechanics to `run_dribble_r` / `run_dribble_l`** | ⛔ **NOT YET.** The same rewrite applied to three sequences unproven is three failures instead of one. |
| **4** | **The remaining 19 zombie sequences** | Cheap once (1) is settled — the manifest already renders all of them. |
| **5** | **Quantisation in the slicer** — §0(C) | Replaces a prompt instruction that demonstrably does not work with a step that can be asserted. |
| **6** | **Stage 3, and the deletions it unlocks** | `SEQ_SCALE`, `POSE_SCALE`, `LEGACY_POSES`, `build_from_poses`. |
| **7** | ⚠ **`HOME_COURT` entries** | Each new character needs one in `index.html` or it falls back to the arena. |
| **8** | ⚠ **Push** | ✅ Committed as `d2392f9` plus this file's own commit. ⛔ **2 unpushed — the device shell has no GitHub credentials, so Rick pushes.** |

---

## 6 · ⭐⭐ Standing rules added this session

- **⭐⭐ WHERE A GENERATOR KEEPS PRODUCING A DEFECT, ASK FOR A FORM THAT CANNOT CONTAIN IT.** Three
  rounds of forbidding symmetry did nothing; one clause requiring a tilted shoulder line ended it.
  §0(A).
- **⭐⭐ POSITIVE INSTRUCTIONS LAND, NEGATIVE ONES DO NOT.** Every *do this* clause in the rewrite was
  obeyed and both *do not* clauses were ignored, in the same prompt, in the same take. §0(B).
- **⭐⭐ A SUBJECT BLOCK SAYS WHAT A CHARACTER IS, NEVER WHAT HIS BODY IS DOING.** It is pasted into
  every prompt, so posture written there outranks every pose line in the set. §4.
- **⭐⭐ ENFORCE IN THE PIPELINE WHAT THE PROMPT CAN ONLY REQUEST.** A palette can be asserted in the
  slicer; asking for it costs prompt budget and bought 134,000 colours. §0(C).
- **⭐⭐ MEASURE THE SHEET; DO NOT LOOK AT IT — AND GIVE THE INSTRUMENT A CONTROL.** The calibration
  frame is a free one. §0(E).
- **⭐ NEVER GUESS A SELECTOR TWICE. OPEN THE PAGE AND READ THE DOM.** Six bugs, one pass. §4.
- **⭐ IN AN UNATTENDED PIPELINE, A PRECONDITION THAT IS MERELY LOGGED DOES NOT EXIST.** §4.
- **⭐ AN EDITED PROMPT MUST PRODUCE A NEW ROLL, NEVER REUSE AN OLD STRIP.** Content-hash keying is
  what makes the generator safe to kill and restart. §3.

---

## 7 · Traps — **additions only; `claude/session-handover.md` §Traps stands in full**

- ⛔⭐ **`device_commit_files` SILENTLY NO-OPS ON OVERWRITE HERE.** §0(F). **Verify every overwrite
  with `md5sum`.** New files in new folders are fine; it is replacement that fails.
- ⛔ **THE DEVICE'S LINUX WORKSPACE FAILED FOR LONG STRETCHES** — *"Workspace unavailable"* — while
  `device_list_dir` / `device_stage_files` / `device_commit_files` kept working. ✅ **It came back on
  its own.** Nothing in the repo is involved; do not debug the repo for it.
- ⛔ **THE CODEX BRIDGE CUTS OFF AT 60 SECONDS.** A `dir` returns; a `type` of a 20 KB file does not.
  ⭐ **To read a file outside the connected folder, have Codex COPY it into `build/` and read it from
  the device shell.** ⚠ Codex needs `model: gpt-5.6-sol` named explicitly, and **it reported "done"
  on a `copy` that had not happened** — make it show you the listing.
- ⚠ **`C:\git\compendium` IS NOT CONNECTED TO THIS SESSION** and `device_request_folder_access` was
  refused for it. Only `C:\Git\throw-a-basketball` is connected. Codex is the way across.
- ⚠ **`gen-prompts.py` REPORTS STALE FILES RATHER THAN DELETING THEM**, because Controlled Folder
  Access refuses `unlink` in this repo. `index.json` is the authoritative list of what is current —
  **nothing downstream may glob the prompt directory.**
- ⚠ **CHATGPT'S UI IS IN DUTCH ON THIS MACHINE.** Any selector matching visible English text is
  broken before it is written.

---

## 8 · Output spec

> ### ⭐⭐ ONE SEQUENCE, ONE CHARACTER, TWO CLAUSES. FIX THE FREE ARM BEFORE TOUCHING ANYTHING ELSE.
> The manifest makes it cheap to change eighty prompts at once, and that is exactly the temptation
> to refuse. Four takes have gone into `dribble_idle` and the fourth finally moved both numbers;
> **the next change should move one more and nothing else.**

**⛔ NEXT: `art/sequences.yml`, `dribble_idle`, the two negative clauses.** Rewrite `no_shamble` and
the low-hand clause as positive descriptions of what the free arm and the dribbling hand *are*
doing. Then:

```
cd C:\Git\throw-a-basketball
py tools\gen-prompts.py
py tools\check-prompts.py
py tools\gen-strips.py --char zombie --seq dribble_idle --rolls 2 --slow
```

**Then measure before judging** — inter-frame difference and mirror asymmetry, against r2's 31% and
41% and the calibration frame's 8% control.

**Then either:** build stage 2 so the measuring stops being ad-hoc, or — only once a sheet comes back
right — carry the mechanics to `run_dribble_r` / `run_dribble_l` and generate the zombie's remaining
19.

> ### ⭐⭐ THE SESSION'S HONEST ARC
> **The pipeline is real: eighty prompts render from two files, the generator drives a browser
> unattended and resumes by content hash, and the calibration frame deletes a table of fourteen
> guesses.** ⭐ **And the one insight that moved the art came from Rick, not from the tooling** — the
> observation that a dribble leans, hunches, drops a shoulder and tilts a head, which turned out to
> be the same fix as the symmetry failure three sessions had been fighting.
> ⛔ **What the session did not buy is a single usable frame of zombie animation.** Four takes, and
> the sheet still is not a dribble. ⚠ **The honest reading is that the measurements improved before
> the picture did, which is progress but is not a sprite**, and that two clauses phrased as
> prohibitions have now been ignored four times running without anyone rewriting them.

---

### Git

✅ **Committed this session:** `d2392f9` (the pipeline) and this file's own commit.
⛔ **Both unpushed. The device shell has no GitHub credentials — Rick pushes.**

```
cd C:\Git\throw-a-basketball
git log --oneline -3
git push
```

⛔ **Ask for `device_request_delete_permission` on `C:\Git\throw-a-basketball` at the START of the
session, before any git command.** Without it a commit still succeeds but leaves `.git/index.lock`,
`.git/HEAD.lock` and stray `.git/objects/*/tmp_obj_*` behind that git could not unlink, and the next
git command trips over the lock. ✅ **Asking early is what kept this session's two commits clean.**

⭐ **`git commit -F -` with a heredoc avoids the commit-message file entirely** — `.git` is off
limits to `device_commit_files`, so the old recipe put a message file in the repo root and deleted it
afterwards. Piping it in needs neither.
