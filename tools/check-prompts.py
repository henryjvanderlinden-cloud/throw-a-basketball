#!/usr/bin/env python3
"""Check the generated monkey prompts against the ones that actually worked.

docs/prompts-monkey.md is the record of seventeen prompts that produced usable
strips, four of which needed a re-roll whose wording is the version that then
worked. The manifest in art/ is supposed to reproduce those, not a plausible
paraphrase of them: a clause that quietly went missing is a failure mode that
will not show up until eighty strips later.

So this compares the rendered prompt for each monkey sequence against its
canonical fence, clause by clause, and reports:

  MISSING  a clause in the proven prompt with no counterpart in the new one
  ADDED    a clause in the new prompt that the proven one did not have

Some of both is expected and correct -- the calibration frame is new, frame
numbers shifted by one, and four sequences deliberately use their re-roll
wording. Anything else needs a look.

Run:  python tools/check-prompts.py [path/to/prompts-monkey.md]
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "build" / "prompts" / "monkey"

# sequence -> the heading of the fence that is in use. Four sequences use their
# re-roll: slice-strips.py points run_dribble_r/l and gameover at the "b" files,
# and dribble_idle's R1 is the wording that fixed the swapping hand.
CANON = {
    "dribble_idle":   "R1",
    "run_dribble_r":  "R2",
    "run_dribble_l":  "R3",
    "gameover":       "R4",
    "pickup":         "4 —",
    "turn":           "5 —",
    "aim":            "6 —",
    "charge":         "7 —",
    "shot":           "8 —",
    "run_r":          "9 —",
    "run_l":          "10 —",
    "celebrate":      "11 —",
    "break_banana":   "13 —",
    "break_wave":     "14 —",
    "panic":          "15 —",
    "celebrate_pump": "16 —",
    "celebrate_flip": "17 —",
}

# Clauses whose absence or presence is a known, intended consequence of the
# manifest rather than a regression. Listed rather than silently filtered so the
# report stays honest about what it is choosing to ignore.
EXPECTED_ADDED = ("CALIBRATION POSE",)

# Differences traced by hand once, when the manifest was first checked against
# the proven prompts, and found to be rewordings rather than losses. They are
# matched and counted separately so the report's headline number means "clauses
# nobody has accounted for" -- which is the number worth reacting to.
#
# Two real regressions were found this way and are NOT in this list, because
# they were fixed instead: panic had lost "Sweat beads are the only extra
# element", and celebrate_flip had lost "the same size ... even while he is in
# the air", which the shared camera clause contradicts for an airborne pose.
BENIGN = [
    (r"same height in both frames",
     "'both frames' -> 'every frame'; the shared camera clause is not per-length"),
    (r"^Do not zoom, crop, recompose or rescale between frames\.$",
     "folded into the shared camera clause, which also adds the reference-height "
     "pin these three prompts were missing"),
    (r"^FRAMES, left to right — .+:$",
     "the descriptive tail moved above the list as its own sentence, so the list "
     "header is identical in every prompt"),
    (r"^Frame #.* must settle back into",
     "replaced by the standard one-shot closing, which pins both ends"),
    (r"face contorted in panic: eyes wide",
     "the face description moved into the character's {panic_face} trait"),
    (r"bit arcade pixel art",
     "the style block was deliberately replaced: '16-bit arcade' was too vague "
     "and the output drifted smooth, so it is now an explicit VGA spec (three "
     "tones per material, ordered dither, no anti-aliasing)"),
]

# Sequences whose prompt is a deliberate REDESIGN, not an attempt to reproduce
# the monkey's. Their differences are the point, so they are reported on their
# own rather than counted against the headline number -- but they are still
# compared, because a redesign that silently loses a clause it did not mean to
# is exactly the failure this script exists to catch.
SUPERSEDED = {
    "dribble_idle": "rewritten as a whole-body action — the shoulder line "
                    "tilts, and the body leads the push while the hand leads "
                    "the recoil. The monkey's version described the arm only, "
                    "and the zombie came back symmetrical three times running.",
    "run_dribble_r": "reworded to agree with its pose guide: the hand's low "
                     "point is the hem and its high point the waistband (the "
                     "game's apex), and the free arm swings against its own "
                     "leg, where the monkey's version swung it with it.",
    "run_dribble_l": "the mirror of run_dribble_r, reworded with it.",
}


def clauses(text: str) -> list[str]:
    """Split into comparable units: one sentence, normalised, digits blanked.

    Frame numbers shift by one when a calibration frame goes in front, so a
    comparison that respects digits reports every numbered clause as changed and
    buries the real differences.
    """
    text = re.sub(r"\s+", " ", text)
    out = []
    for s in re.split(r"(?<=[.:;]) (?=[A-Z0-9])", text):
        s = s.strip()
        if len(s) < 12:
            continue
        s = re.sub(r"\b\d+\b", "#", s)
        s = re.sub(r"^#\. ", "", s)
        out.append(s)
    return out


def fences(md: str) -> dict[str, str]:
    found = {}
    for block in re.split(r"\n(?=#{1,2} )", md):
        head = block.split("\n", 1)[0]
        for f in re.findall(r"```\n(.*?)\n```", block, re.S):
            found.setdefault(head, f)
    return found


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv
    src = Path(args[0]) if args else ROOT / "docs" / "prompts-monkey.md"
    by_head = fences(src.read_text(encoding="utf-8"))

    total_missing = total_added = total_benign = total_superseded = 0
    for seq, marker in CANON.items():
        heads = [h for h in by_head if marker in h]
        if not heads:
            print(f"{seq:<18} NO FENCE matching {marker!r}")
            continue
        old = clauses(by_head[heads[0]])
        new_path = PROMPTS / f"{seq}.txt"
        if not new_path.exists():
            print(f"{seq:<18} NOT RENDERED")
            continue
        new = clauses(new_path.read_text(encoding="utf-8"))

        sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
        missing, added = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("delete", "replace"):
                missing += old[i1:i2]
            if tag in ("insert", "replace"):
                added += new[j1:j2]

        # A clause that merely moved, or was reworded below the noise floor,
        # is not a missing clause. Pair them up by similarity before reporting.
        really_missing, benign = [], []
        for m in missing:
            best = max((difflib.SequenceMatcher(None, m, a).ratio() for a in new),
                       default=0.0)
            if best >= 0.80:
                continue
            why = next((w for pat, w in BENIGN if re.search(pat, m)), None)
            (benign if why else really_missing).append((round(best, 2), m, why))
        really_added = []
        for a in added:
            if any(e in a for e in EXPECTED_ADDED):
                continue
            best = max((difflib.SequenceMatcher(None, a, m).ratio() for m in old),
                       default=0.0)
            if best < 0.80:
                really_added.append((round(best, 2), a))

        if seq in SUPERSEDED:
            print(f"~~ {seq:<18} {len(old):>2} -> {len(new):>2} clauses  "
                  f"(SUPERSEDED: {len(really_missing)} dropped, "
                  f"{len(really_added)} new)")
            print(f"     {SUPERSEDED[seq]}")
            for score, c, _ in really_missing:
                print(f"     dropped [{score}] {c[:120]}")
            total_superseded += len(really_missing)
            continue

        total_missing += len(really_missing)
        total_added += len(really_added)
        total_benign += len(benign)
        mark = "ok" if not (really_missing or really_added) else "**"
        print(f"{mark} {seq:<18} {len(old):>2} -> {len(new):>2} clauses  "
              f"({len(really_missing)} unaccounted, {len(really_added)} added, "
              f"{len(benign)} known)")
        for score, c, _ in really_missing:
            print(f"     MISSING [{score}] {c[:150]}")
        for score, c in really_added:
            print(f"     ADDED   [{score}] {c[:150]}")
        if verbose:
            for score, c, why in benign:
                print(f"     known   {c[:80]}\n               -> {why}")

    print(f"\n{'=' * 70}")
    print(f"{total_missing} unaccounted missing clause(s) across {len(CANON)} "
          f"sequences  <-- this is the number that matters")
    print(f"{total_benign} known rewording(s), {total_added} intentional "
          f"addition(s).  Pass -v to see the known ones.")
    if total_superseded:
        print(f"{total_superseded} clause(s) dropped from {len(SUPERSEDED)} "
              f"deliberately redesigned sequence(s) — listed above, not counted.")
    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
