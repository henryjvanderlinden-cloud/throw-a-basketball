# Lessons learned — Throw A Basketball

*Written 2026-09-27, at the end of the art pipeline: all four characters have their full rosters of
twenty sequences. Drawn from handovers 01–11 and this session. Meant for future projects, not only
this game: each lesson is stated generally first, then with the evidence from here. The handovers
remain the detailed record; section numbers below point into them.*

---

## 1 · How the work was run

**1.1 Review the specification before building, as a numbered list of decisions with defaults.**
Every productive session began with a short list of the choices that were genuinely Rick's —
temperament, which hand dribbles, what a panic looks like — each with a proposed default. He
answers "default" to most and overrides the few he cares about, and nothing is built on an
assumption he would have rejected. The expensive failures of the project were the places where a
default was assumed silently instead of offered.

**1.2 Put a person's taste in front of them early, in the form they judge by.** Rick judges
animation by watching it move, not by reading a strip. From the pilot onward every roll went out as
a sheet of its frames *and* the loop playing at the game's speed, the rolls side by side, so a pick
takes seconds. Close-ups of the face beside the reference became part of the same package once
faces turned out to be where identity fails first (§3.1).

**1.3 Pilot one sequence before a batch.** Three rolls of the stationary dribble, reviewed, before
fifty-seven rolls of everything else. The NBA player's first pilot and the monkey's first steals
both came back as the wrong person; each time one rewrite of the subject fixed every later roll.
A batch launched before that check would have been two hours of the wrong character.

**1.4 Reuse what already reads well; do not redesign it.** The monkey's approved frames were the
specification for every other character's shooting chain and celebrations (h09 §0(A)). Tracing the
guide off his sprites worked twelve rolls out of twelve (h09 §0(B)). The one time a "bug" was found
in art Rick was already happy with, a mechanism was designed around it and then discarded.

**1.5 Where nothing exists to copy, describe the move in play, with its timing.** For sequences with
no precedent (idle breaks, panics, steals) the productive spec review stated how often the move
plays, how fast, and what cancels it, before any pose was drawn (h10 §0(B)). Those three numbers
decided more of the design than any description of the pose.

**1.6 Ask the one question that changes what gets built; decide the rest.** "Does the head-pluck go
in the steal or in the stolen reaction?" was worth asking; frame counts and scale factors were not.
When an answer is blank ("steal_r:"), ask again rather than guess.

**1.7 Leave a durable record at the end of every working session.** The handovers (what was done,
what was learned, what is open, what to do first) let each new session start in minutes. The
format that worked: three sentences, then the findings that outlive the session, then state, process,
traps and open items, then an honest account of what went wrong.

---

## 2 · Prompting an image model

**2.1 Relations, not properties.** The generator obeys statements that relate two things in the
picture ("the hand is further out than the shoulder", "the feet are one drawing repeated in all four
frames") and drifts on statements about one thing ("the hand is flat", "at chest height")
(h02 §0(A)). Before generating, read every clause and rewrite the properties as relations.

**2.2 Ask for a form that cannot contain the defect; do not forbid the defect.** Symmetrical arms
were not cured by "never symmetrical" but by "the shoulder line tilts", a pose that cannot be drawn
symmetrically (h01 §0(A)). Negative clauses were the ones ignored; positive descriptions of what
the limb *is doing* landed (h01 §0(B)).

**2.3 Describe the face and the temperament in words.** A reference image is not enough. With only
"brown fur" or "a stern set jaw" to go on, the model filled the gap with its own default: a generic
severe face for the NBA player, a friendly cartoon monkey for the ape. One paragraph naming the face
as the reference draws it, plus a resting expression, fixed each (h11 §0(A); this session).

**2.4 Describing intensity overshoots.** Correcting the cartoon monkey with "dark" and "stern,
intense stare" produced a monkey that was too dark and "too menacing". Name the exact shade ("no
darker than the reference") and a temperament that says what he is, not only what he is not
("cheeky, determined, never menacing").

**2.5 One subject block, pasted verbatim into every prompt.** Identity drift between sequences is
invisible until two sit side by side, so the character's description is written once and never
reworded per sequence. A posture instruction placed in it ("hands hooked into claws") overrode every
pose in every sequence; posture belongs in per-sequence traits (h01).

**2.6 A drawn guide beats prose, and does not cost identity.** A stick-figure pose guide attached
beside the reference, with a note saying which image is WHO and which is WHERE, carried knee bends,
hand heights, stance and even hair lag that prose had failed to deliver for many rolls, with no style
bleed (h03 §0(A)(B)). Where prose and guide both describe a thing, draw it and keep the prose as a
caption.

**2.7 What the guide draws only in colour or a small mark does not reach the art.** Two frames
differing only in which leg was orange came back as one pose twice (h04 §0(B)). A strong default of
the model (sprites face right) needs a large mark *and* a sentence: a nose wedge, not a face arc
(h04 §0(C)). If two frames must differ, their silhouettes must differ.

**2.8 Draw the guide on the character's own body.** A guide drawn on a narrower body pulled a heavily
built character's build toward it. Measure the reference on a grid (shares of standing height) and
give the guide that body (h11 §0(B)). Measure, don't assume: the high schooler turned out to have the
zombie's body exactly.

**2.9 A dead transition in every roll is a contradiction, not variance.** When one frame-to-frame
change is near zero across a whole batch, two instructions disagree about that frame; resolve them
(h03 §0(D)).

**2.10 Style cannot be won in the prompt.** An explicit pixel-art specification changed nothing
measurable; the output is a smooth render depicting pixel art. Enforce the look where it can be
asserted (downsampling, the slicer), not where it can only be requested (h01 §0(C)).

**2.11 Roll-to-roll variance is as large as most prompt effects. Stop tuning; generate three and
pick.** Two rolls of an unchanged prompt differed as much as most prompt changes did (h02 §0(B)).
What survives is categorical and visible in the sheet. Three rolls per sequence, then a person's
pick, was the stable rhythm for the remaining eighty-odd strips.

---

## 3 · Judging and measuring

**3.1 Identity fails first, and is judged by eye — look at the face.** Kit, shoes and build are easy
to check; the face is where a roll becomes someone else, and where "the likeness is fine" was twice
the wrong verdict. Check identity before pose: face, then colours, then shoes (white trainers were the
commonest drift) (h05 §0(A), h11 §2).

**3.2 The game is the instrument; the sheet is only a screen.** Four defects that no sheet could show
— frame phase against the ball, sizing off a crouch, a runner lurching sideways, the ball floating
off the hand — appeared only when the loop played in the game with the ball (h04 §0(A)). Film it at
the game's own speed before calling a sequence done.

**3.3 Derive targets from the game's own constants.** Hand height, lateral offset and cadence were
already fixed in `index.html`; the prompt had contradicted them for nineteen takes (h02 §0(C)).

**3.4 A calibration frame measures scale; it can still be drawn out of proportion.** Every strip
starts with the same plain standing pose, which replaced a table of guessed scale factors (h01 §0(D)),
but a model sometimes draws that frame small beside its own poses. Final sizes are set against the
character's own dribble and runs, side by side at game scale (h08 §0(A), h10 §0(D)).

**3.5 A measurement is only as good as its landmark.** Shoe width lied on some rolls; gold-coloured
pixels caught skin as well as the jersey number; hair width worked for a character with a distinctive
mop. Check a metric against the eye before trusting it, and let a hard constraint win over it (the
dribble scale was held down so the character picker still shows the professional tallest).

**3.6 When a whole loop fails, a subset of its frames may not** (h05 §0(B)). Picking frames within
a roll ("this roll, but frames 1, 3, 2") rescued several sequences; the pipeline supports it.

**3.7 Stories play once; loops loop.** A narrative break looped strobes; played once, a frame per
half bounce, locked to the ball, it reads (h10 §0(A)).

---

## 4 · Building the pipeline

**4.1 Data-driven from the start.** Two YAML files (characters, sequences) render every prompt;
per-character traits fill placeholders, so a character without a tail simply gets no tail sentences.
New characters were a block of YAML, not new code.

**4.2 Make runs resumable and never overwrite.** Each roll is keyed on the prompt text and the
md5 of the guide and reference it was sent with; a stale roll is renamed (`b1r2`), never replaced.
Killing and restarting a batch cost nothing, and rejected rolls stayed available for comparison.

**4.3 Guard against the tool lying to you.** Three recurring false successes: the uploaded
attachment coming back as the "generated" image (guard on turn, aspect *and* size — h03 §0(C),
h04 §0(F), h11 §0(D)); a file-write tool that reported success without overwriting; a timeout that
looked like a hang. A result that arrives in three seconds, or is byte-identical to an input, is not
a generation.

**4.4 Drive a web UI defensively.** The site changed its composer mid-project and four faults queued
behind each other (h04 §0(E)). Every selector is a list of candidates with the winner logged, and
every failure saves a screenshot — which diagnosed all four before any theory did.

**4.5 Cut figures by their own pixels.** Figures in a strip overlap horizontally; column cuts cannot
separate them, connected-component masking can (h04 §0(D)).

**4.6 Build the review tools early.** A preview that slices exactly as the game does, a side-by-side
loop of all rolls, a headless test suite and a shot-difficulty sweep made every decision fast and
every regression visible. New shot art changes how easy a character is; the sweep catches it
(h09 §0(D)).

---

## 5 · Environment and tooling (Rick's machine)

**5.1 Know which machine can reach what.** The cloud container and the desktop VM are both behind an
egress allowlist; only native Windows reaches chatgpt.com. Image generation therefore ran natively,
launched as a detached process through the Codex connection (each Codex turn is cut at 60 s, so it
starts jobs, it does not run them). Headless browser tests ran in the cloud from a staged tarball.

**5.2 Windows Controlled Folder Access shapes everything in the repo.** Files can be created but not
truncated in place, so edits are remove-then-write; every read is slow, so long builds run in the
background and are polled; deletes need an explicit permission that lapses on reconnect. Tools
written for the repo must not depend on deleting files.

**5.3 Git from the VM leaves stale `index.lock` files.** Check for and remove the lock after git
commands; Rick pushes, since the VM holds no credentials.

**5.4 Watch the disk.** The drive filled to zero once mid-build and left `sprites/` half-written.
`df -h .` before any batch or build.

**5.5 Schedule check-ins for long unattended work, and cancel the stale ones.** A two-hour batch was
followed by check-ins every half hour; a check-in overtaken by a change of plan should be deleted,
and if it fires anyway, recognised as superseded rather than acted on.

---

## 6 · The one-paragraph version

Settle the person's decisions first, as defaults they can wave through. Describe the character — face
and temperament above all — in words, once, and paste it everywhere. Draw poses rather than describe
them, on the character's own body, with relations and silhouettes that differ. Generate three and let
a person pick from the moving loop. Judge in the game, with the ball. Build the pipeline so that
nothing is ever overwritten, every run can resume, and every tool shows what it actually saw.
