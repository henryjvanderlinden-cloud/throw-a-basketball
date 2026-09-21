#!/usr/bin/env python3
"""Render every generation prompt from the manifest.

Reads   art/sequences.yml   the sequences every character gets
        art/characters.yml  each character's subject, traits and own sequences
Writes  build/prompts/<character>/<sequence>.txt   the prompt, ready to send
        build/prompts/index.json                   metadata for the downstream tools

The point of this script is that nobody writes a prompt by hand again. The
SUBJECT block in particular is pasted verbatim into every prompt for a
character by construction rather than by discipline -- rewording it between
sequences is what drifts a character's identity between strips, and the drift
is invisible until two finished sequences sit side by side.

Run from anywhere:  python tools/gen-prompts.py [character ...]
"""

from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"
OUT = ROOT / "build" / "prompts"

WIDTH = 79

# A trait that is not defined for a character renders as nothing. That is the
# mechanism that lets one set of pose lines serve a character with a tail and a
# character without one, so an unknown name is normal and never an error.
TRAIT = re.compile(r"\{([a-z_][a-z0-9_]*)\}")



def guide_file(seq: dict) -> str | None:
    """The pose guide's path. `guide:` is either the path itself or, since the
    frame table moved into the manifest, a mapping with the path under `file`
    and the table tools/make-pose-guide.py draws from."""
    g = seq.get("guide")
    if isinstance(g, dict):
        return g.get("file") or None
    return g or None

def resolve(text: str, traits: dict) -> str:
    """Substitute {traits}, then repair the whitespace an empty one leaves."""
    out = TRAIT.sub(lambda m: str(traits.get(m.group(1), "")).strip(), text)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r" +([.,;:])", r"\1", out)       # " ." from an empty trait
    out = re.sub(r"\n ", "\n", out)
    return out.strip()


def wrap(text: str, initial: str = "", subsequent: str = "") -> str:
    """Re-wrap a paragraph. Substitution moves every line ending, so the
    manifest's own wrapping cannot survive and is not relied on."""
    return textwrap.fill(
        " ".join(text.split()),
        width=WIDTH,
        initial_indent=initial,
        subsequent_indent=subsequent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def render(seq: dict, char: dict, defaults: dict) -> str:
    traits = dict(char.get("traits") or {})
    n = int(seq["frames"])
    calib = seq.get("calibration", defaults.get("calibration") is not None)

    # Frame numbers are substituted, never written by hand. The generator sees
    # cells, and with a calibration frame at the head the Nth pose of the
    # animation is cell N+1 -- so a prompt that says "frame 3" when it means the
    # third pose is off by one, in a clause whose whole job is to be precise
    # about which frame does what. {f1}..{fN} are the cell numbers; {first} and
    # {last} are the first and last animation cells.
    offset = 1 if calib else 0
    for j in range(1, n + 1):
        traits[f"f{j}"] = str(j + offset)
    traits["first"] = str(1 + offset)
    traits["last"] = str(n + offset)
    traits["nframes"] = str(n)

    def field(name, fallback=None):
        raw = seq.get(name, fallback if fallback is not None else defaults.get(name, ""))
        return resolve(str(raw), traits) if raw else ""

    parts: list[str] = []
    parts.append(resolve(str(defaults["header"]), traits))

    parts.append(wrap("SUBJECT: " + resolve(str(char["subject"]), traits),
                      subsequent=""))

    cells = n + 1 if calib else n
    parts.append(wrap(
        f"LAYOUT: one horizontal row of {cells} frames of equal width, evenly "
        f"spaced. No borders, no frame numbers, no labels, no background, no "
        f"drop shadows."))

    # A sequence with a `guide:` is sent TWO images, so the prompt has to say
    # which is which. The wording is a default rather than a per-sequence line
    # for the same reason the SUBJECT block is: the division of authority
    # between the reference and the guide must not drift between sequences.
    if guide_file(seq):
        parts.append("\n\n".join(
            wrap(p) for p in paragraphs(
                resolve(str(defaults["guide_note"]), traits))))

    camera = field("camera") + " " + field("ground")
    parts.append(wrap(resolve(camera, traits)))

    parts.append(wrap("VIEW: " + field("view")))

    for optional in ("preamble", "critical"):
        if seq.get(optional):
            body = field(optional)
            parts.append("\n\n".join(wrap(p) for p in paragraphs(body)))

    lines = ["FRAMES, left to right:"]
    i = 1
    if calib:
        lines.append(wrap(resolve(str(defaults["calibration"]), traits)
                          .lstrip("1. ").strip(),
                          initial="1. CALIBRATION POSE: ".replace(
                              "CALIBRATION POSE: ", "") + "CALIBRATION POSE: ",
                          subsequent="   "))
        i = 2
    for pose in seq["poses"]:
        lines.append(wrap(resolve(str(pose), traits),
                          initial=f"{i}. ", subsequent="   "))
        i += 1
    parts.append("\n".join(lines))

    kind = seq.get("kind", "loop")
    closing = seq.get("closing") or defaults[
        "closing_loop" if kind == "loop" else "closing_one_shot"]
    parts.append(wrap(resolve(str(closing), traits)))

    if seq.get("extra"):
        parts.append(wrap(field("extra")))

    parts.append(wrap(resolve(str(defaults["style"]), traits)))
    parts.append(wrap(field("ball")))

    return "\n\n".join(p for p in parts if p.strip()) + "\n"


def main() -> None:
    seq_doc = yaml.safe_load((ART / "sequences.yml").read_text(encoding="utf-8"))
    chars = yaml.safe_load((ART / "characters.yml").read_text(encoding="utf-8"))
    defaults = seq_doc["defaults"]
    shared = seq_doc["sequences"]

    # The calibration pose text is a numbered line in the manifest for
    # readability; strip its number here so the renderer owns the numbering.
    defaults["calibration"] = re.sub(
        r"^\s*1\.\s*CALIBRATION POSE:\s*", "",
        str(defaults["calibration"]).strip())

    wanted = set(sys.argv[1:])
    index: dict = {"width": WIDTH, "characters": {}}

    for key, char in chars.items():
        if wanted and key not in wanted:
            continue
        own = char.get("sequences") or {}
        all_seqs = {**shared, **own}
        out_dir = OUT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        before = {p.stem for p in out_dir.glob("*.txt")}

        entries = {}
        print(f"== {char['label']}  ({len(all_seqs)} sequences)")
        for name, seq in all_seqs.items():
            text = render(seq, char, defaults)
            (out_dir / f"{name}.txt").write_text(text, encoding="utf-8")
            entries[name] = {
                "title": seq.get("title", name),
                "kind": seq.get("kind", "loop"),
                "frames": int(seq["frames"]),
                "calibration": True,
                "ref": char["refs"][seq.get("ref", "front")],
                "guide": guide_file(seq),
                "travelling": bool(seq.get("travelling")),
                "airborne": bool(seq.get("airborne")),
                "own": name in own,
                "chars": len(text),
            }
            flag = "*" if name in own else " "
            print(f"  {flag} {name:<20} {seq['frames']}+1 cells  "
                  f"{len(text):>5} chars"
                  + ("  + pose guide" if guide_file(seq) else ""))

        # A renamed or removed sequence leaves its old .txt behind. Deleting it
        # is not always possible -- Windows Controlled Folder Access refuses
        # unlink in this repo, and so does the desktop bridge unless deletion
        # has been granted -- and a tool that dies on cleanup is worse than one
        # that leaves a file lying about. So: report, never delete. index.json
        # is the authoritative list of what is current, and everything
        # downstream reads that rather than globbing the directory.
        for orphan in sorted(before - set(entries)):
            print(f"  ! {orphan:<20} STALE — no longer in the manifest; "
                  f"delete {(out_dir / (orphan + '.txt')).name} by hand")
        index["characters"][key] = {
            "label": char["label"], "folder": char["folder"],
            "scale": char["scale"], "status": char.get("status", "proposed"),
            "sequences": entries,
        }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    total = sum(len(c["sequences"]) for c in index["characters"].values())
    print(f"\n{total} prompts written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
