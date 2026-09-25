#!/usr/bin/env python3
"""Generate sprite strips by driving a signed-in ChatGPT session.

Reads   build/prompts/index.json and build/prompts/<char>/<seq>.txt
Writes  artwork/basketball-players/<Folder> poses/<seq>.r<N>.png
        artwork/basketball-players/<Folder> poses/<seq>.r<N>.json   (sidecar)

WHERE THIS RUNS
---------------
On Rick's Windows machine, in a normal terminal -- NOT in the Cowork container
and NOT in the desktop VM. Neither of those can reach chatgpt.com: the egress
allowlist refuses it, which is also why Playwright's Chromium will not download
there. This script needs the open internet and a browser it can keep signed in.

    py -m pip install playwright
    py -m playwright install chromium
    py tools/gen-strips.py --char zombie --dry-run     # see the job list
    py tools/gen-strips.py --char zombie --once        # one strip, watch it
    py tools/gen-strips.py --char zombie               # the rest

FIRST RUN
---------
The browser opens with an empty profile stored in .chatgpt-profile/ (gitignored)
and waits for you to sign in to ChatGPT by hand. That happens once; the profile
persists, and later runs go straight to work.

No keypress is involved: the script polls until the composer appears. An earlier
version asked for Enter in the terminal and sat blocked while the login flow
closed the tab it was holding, then woke up and touched a dead page.

RESUMABILITY
------------
Every job is keyed on (character, sequence, roll, prompt text). A strip already
on disk whose sidecar records the same prompt hash is skipped, so the script can
be killed and restarted freely -- which matters, because eighty generations will
walk into ChatGPT's rate limits repeatedly and the only sane response is to wait
and carry on. Editing a prompt changes its hash, so the next run produces a NEW
roll rather than silently reusing the old strip.

WHEN IT BREAKS
--------------
chatgpt.com is a web UI, not an API, and its markup will change. Every selector
below is a LIST of candidates tried in order, and the one that worked is logged,
so a failure says which layer moved rather than just "timeout". On any failure
the page is screenshotted into build/gen-debug/ and the run moves to the next
job instead of dying.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "build" / "prompts" / "index.json"
PROMPTS = ROOT / "build" / "prompts"
ART = ROOT / "artwork" / "basketball-players"
PROFILE = ROOT / ".chatgpt-profile"
DEBUG = ROOT / "build" / "gen-debug"

CHAT_URL = "https://chatgpt.com/"

# A generated strip is a wide landscape row of frames. The reference image is
# portrait (1086x1448) and UI chrome is small or square, so shape alone tells
# them apart -- which matters because the uploaded reference is served from the
# same hosts as the output.
MIN_STRIP_W = 800
MIN_STRIP_ASPECT = 1.4

# Every selector is a list tried in order. The winner is logged. When ChatGPT
# moves its markup, the log says which of these stopped matching, which is the
# difference between a five-minute fix and an afternoon.
SEL = {
    "composer": [
        "#prompt-textarea",
        "div[contenteditable='true'][id='prompt-textarea']",
        "textarea[data-id='root']",
        "div.ProseMirror[contenteditable='true']",
    ],
    "file_input": [
        "input[type='file']",
    ],
    "plus": [
        "[data-testid='composer-plus-btn']",
        "[data-testid='composer-action-file-upload']",
        "form button[aria-label*='add' i]",
        "form button[aria-label*='voeg' i]",
        "form button[aria-label*='bestand' i]",
        "form button[aria-label*='file' i]",
        "form button[aria-label*='attach' i]",
    ],
    "send": [
        "[data-testid='send-button']",
        "button[aria-label*='Send' i]",
        "button[data-testid='fruitjuice-send-button']",
    ],
    "stop": [
        "[data-testid='stop-button']",
        "button[aria-label*='Stop' i]",
    ],
    "turn": [
        "[data-testid^='conversation-turn-']",
        "article[data-testid^='conversation-turn-']",
        "div.group\\/conversation-turn",
    ],
}

# Substrings that mean "you have run out of image generations". Checked against
# the page's text; any match parks the run rather than burning through the
# remaining jobs against a wall.
RATE_LIMIT_MARKERS = [
    "you've reached your limit",
    "you have reached your limit",
    "limit for image generation",
    "please try again later",
    "rate limit",
    "you can create more images after",
    "usage limit",
]


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# job planning -- no browser involved, so --dry-run exercises all of it
# --------------------------------------------------------------------------

def plan(characters: list[str], sequences: list[str], rolls: int) -> list[dict]:
    if not INDEX.exists():
        sys.exit(f"no {INDEX.relative_to(ROOT)} -- run tools/gen-prompts.py first")
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    jobs, skipped = [], 0
    for key, char in index["characters"].items():
        if characters and key not in characters:
            continue
        out_dir = ART / f"{char['folder']} poses"
        for seq, meta in char["sequences"].items():
            if sequences and seq not in sequences:
                continue
            text = (PROMPTS / key / f"{seq}.txt").read_text(encoding="utf-8")
            h = prompt_hash(text)
            for roll in range(1, rolls + 1):
                png = out_dir / f"{seq}.r{roll}.png"
                side = png.with_suffix(".json")
                if png.exists() and side.exists():
                    try:
                        if json.loads(side.read_text(encoding="utf-8")).get("prompt_hash") == h:
                            skipped += 1
                            continue
                    except (ValueError, OSError):
                        pass          # unreadable sidecar: regenerate
                jobs.append({
                    "char": key, "label": char["label"], "seq": seq, "roll": roll,
                    "frames": meta["frames"], "cells": meta["frames"] + 1,
                    "ref": ROOT / meta["ref"], "out": png, "sidecar": side,
                    "guide": ROOT / meta["guide"] if meta.get("guide") else None,
                    "text": text, "hash": h,
                })
    if skipped:
        log(f"{skipped} strip(s) already on disk with a matching prompt — skipping")
    return jobs


# --------------------------------------------------------------------------
# the browser backend
# --------------------------------------------------------------------------

class ChatGPT:
    def __init__(self, ctx, slow: bool):
        self.ctx = ctx
        self.slow = slow

    @property
    def page(self):
        """A live page, re-acquired on demand.

        Holding one page reference for the whole run does not survive the
        manual sign-in: ChatGPT's login navigates away and may open its own
        tab, and the original tab is closed under us. Everything after that
        fails with a bare "Page closed", which says nothing about the cause.
        So the page is looked up each time instead of cached.
        """
        for p in self.ctx.pages:
            if not p.is_closed():
                return p
        return self.ctx.new_page()

    def first(self, kind: str, timeout: int = 15000):
        """First matching candidate selector, logging which one won."""
        last = None
        for sel in SEL[kind]:
            try:
                loc = self.page.locator(sel).first
                loc.wait_for(state="visible", timeout=timeout // len(SEL[kind]) + 500)
                return loc, sel
            except Exception as e:            # noqa: BLE001 - any miss is a miss
                last = e
        raise RuntimeError(
            f"no selector matched for {kind!r}; tried {SEL[kind]}. "
            f"ChatGPT's markup has probably changed. Last error: {last}")

    def new_chat(self) -> None:
        self.page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(2500 if self.slow else 1200)

    def signed_in(self) -> bool:
        try:
            self.first("composer", timeout=8000)
            return True
        except Exception:                      # noqa: BLE001 - closed page too
            return False

    def wait_for_sign_in(self, minutes: int = 10) -> bool:
        """Poll until the composer appears, rather than waiting on a keypress.

        Asking the user to press Enter in the terminal meant the script sat
        blocked while the login flow closed the tab it was holding, and the
        first thing it did on waking was touch a dead page. Polling needs no
        keystroke and notices the moment sign-in lands, whatever route it took.
        """
        deadline = time.time() + minutes * 60
        while time.time() < deadline:
            if self.signed_in():
                return True
            left = int(deadline - time.time())
            log(f"    waiting for sign-in… {left // 60}m{left % 60:02d}s left")
            time.sleep(5)
        return False

    def _img_srcs(self) -> set:
        try:
            return set(self.page.eval_on_selector_all(
                "img", "els => els.map(e => e.currentSrc || e.src).filter(Boolean)"))
        except Exception:                      # noqa: BLE001
            return set()

    # Reading the live DOM (signed in, Dutch UI) settled how this works:
    #
    #   input#upload-files   is inside the composer's form and IS wired to it
    #   input#upload-photos / -media / -camera / -media-files are NOT
    #   button[data-testid=composer-plus-btn] opens a MENU, not a file dialog,
    #     which is why expect_file_chooser around its click always timed out
    #   an attached file shows as a BUTTON whose aria-label names the file
    #     ("Bestand 1 verwijderen: zombie(2).png") -- there is no <img> chip,
    #     which is why counting images saw nothing and every method reported
    #     failure after succeeding, attaching the reference twice over
    _STATE = """(stem) => {
        const c = document.querySelector('#prompt-textarea');
        if (!c) return null;
        let scope = c.closest('form');
        if (!scope) { scope = c;
            for (let i = 0; i < 5 && scope.parentElement; i++) scope = scope.parentElement; }
        const s = stem.toLowerCase();
        const named = [...scope.querySelectorAll('[aria-label]')].filter(
            e => (e.getAttribute('aria-label') || '').toLowerCase().includes(s)).length;
        return {named: named, buttons: scope.querySelectorAll('button').length};
    }"""

    def _state(self, stem: str):
        try:
            return self.page.evaluate(self._STATE, stem) or {"named": 0, "buttons": 0}
        except Exception:                      # noqa: BLE001
            return {"named": 0, "buttons": 0}

    def _wait_attached(self, before: dict, stem: str, seconds: int) -> bool:
        """Attached = a control in the composer now names our file.

        The filename is the one part of that chip no UI language changes, so
        this works on a Dutch ChatGPT exactly as on an English one. Button
        count is the fallback for a redesign that stops naming the file.
        """
        deadline = time.time() + seconds
        while time.time() < deadline:
            now = self._state(stem)
            if now["named"] > before["named"] or now["buttons"] > before["buttons"]:
                return True
            self.page.wait_for_timeout(1000)
        return False

    def dom_report(self) -> str:
        """What the composer looks like right now, for a failure to explain
        itself. ChatGPT's UI is redesigned without notice -- when an attach
        stops working, this says whether the file input, the composer and the
        plus button are there at all, rather than leaving a bare exception."""
        try:
            info = self.page.evaluate("""() => {
                const sel = s => document.querySelectorAll(s).length;
                const inputs = [...document.querySelectorAll("input[type=file]")]
                    .map(e => ({accept: e.accept || "", hidden: e.offsetParent === null,
                                inForm: !!e.closest("form"), multiple: e.multiple}));
                const buttons = [...document.querySelectorAll("form button, [data-testid*=composer] button")]
                    .slice(0, 14)
                    .map(b => (b.getAttribute("aria-label") || b.getAttribute("data-testid")
                               || (b.textContent || "").trim()).slice(0, 34));
                return {
                    url: location.href,
                    title: document.title,
                    promptTextarea: sel("#prompt-textarea"),
                    contenteditable: sel("div[contenteditable='true']"),
                    forms: sel("form"),
                    turns: sel("[data-testid^='conversation-turn-']"),
                    fileInputs: inputs,
                    composerButtons: buttons,
                };
            }""")
        except Exception as e:                 # noqa: BLE001
            return f"could not read the DOM: {e.__class__.__name__}: {e}"
        lines = [f"url {info['url']}",
                 f"title {info['title']!r}",
                 f"#prompt-textarea={info['promptTextarea']}  "
                 f"contenteditable={info['contenteditable']}  forms={info['forms']}  "
                 f"turns={info['turns']}",
                 f"file inputs: {len(info['fileInputs'])}"]
        for i in info["fileInputs"]:
            lines.append(f"  accept={i['accept']!r} hidden={i['hidden']} "
                         f"inForm={i['inForm']} multiple={i['multiple']}")
        lines.append("composer buttons: " + ", ".join(repr(b) for b in info["composerButtons"]))
        return "\n".join(lines)

    def _via_file_chooser(self, path: Path) -> bool:
        """Click the composer's plus button and answer the file dialog.

        The route for a composer that keeps its input out of the DOM until the
        menu is open, which is what the September redesign does.
        """
        for sel in SEL["plus"]:
            try:
                btn = self.page.locator(sel).first
                if not btn.count():
                    continue
                with self.page.expect_file_chooser(timeout=8000) as fc:
                    btn.click()
                fc.value.set_files(str(path))
                return True
            except Exception:                  # noqa: BLE001
                # the plus may open a MENU whose item opens the chooser
                try:
                    with self.page.expect_file_chooser(timeout=8000) as fc:
                        for label in ("bestand", "file", "upload", "computer", "afbeelding"):
                            item = self.page.get_by_text(re.compile(label, re.I)).first
                            if item.count():
                                item.click()
                                break
                    fc.value.set_files(str(path))
                    return True
                except Exception:              # noqa: BLE001
                    continue
        return False

    def attach(self, path: Path) -> None:
        """Attach the reference, and REFUSE to continue if it did not land.

        Order is from the live DOM, not from guesswork: the composer's own
        input first because it demonstrably works, then a synthetic drop, and
        the plus-menu last because it needs two clicks and a menu item whose
        label is translated.
        """
        stem = path.stem.lower()
        before = self._state(stem)
        tried = []
        settle = 2500 if self.slow else 1200
        wait = 90 if self.slow else 60

        # Any file input on the page, not only one inside the composer's form:
        # the September 2026 redesign moved it out, and the old selector then
        # matched nothing at all.
        def any_file_input():
            inputs = self.page.locator("input[type='file']")
            n = inputs.count()
            if not n:
                raise RuntimeError("no input[type=file] on the page")
            last = None
            for i in range(n):
                try:
                    inputs.nth(i).set_input_files(str(path), timeout=8000)
                    return
                except Exception as e:         # noqa: BLE001
                    last = e
            raise last or RuntimeError("no file input accepted the file")

        for label, act in (
            ("input[type=file]", any_file_input),
            ("plus menu", lambda: self._via_file_chooser(path)),
            ("drop", lambda: self._drop(path)),
        ):
            try:
                act()
                if self._wait_attached(before, stem, wait):
                    log(f"    attached via {label}")
                    self.page.wait_for_timeout(settle)
                    return
                tried.append(f"{label}:not-attached")
            except Exception as e:             # noqa: BLE001
                tried.append(f"{label}:{e.__class__.__name__}")

        log("    DOM at the time of failure:")
        for line in self.dom_report().splitlines():
            log(f"      {line}")
        raise RuntimeError(
            "could not attach the reference image — tried " + ", ".join(tried) +
            ". Not sending: without the reference ChatGPT just asks for it and "
            "the strip never gets generated.")

    def _drop(self, path: Path) -> bool:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return bool(self.page.evaluate("""({b64, name}) => {
            const bin = atob(b64);
            const arr = new Uint8Array(bin.length);
            for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
            const file = new File([arr], name, {type: 'image/png'});
            const dt = new DataTransfer();
            dt.items.add(file);
            const c = document.querySelector('#prompt-textarea');
            if (!c) return false;
            const target = c.closest('form') || c;
            for (const type of ['dragenter', 'dragover', 'drop']) {
                target.dispatchEvent(new DragEvent(type,
                    {bubbles: true, cancelable: true, dataTransfer: dt}));
            }
            return true;
        }""", {"b64": b64, "name": path.name}))

    def sent_with_image(self) -> bool:
        """Did the message we just sent actually carry an image?

        Checked straight after sending, because the answer is available in
        seconds and the alternative is waiting out the whole generation timeout
        to be told the reference was missing.
        """
        try:
            return bool(self.page.evaluate("""() => {
                const turns = [...document.querySelectorAll(
                    "[data-testid^='conversation-turn-']")];
                if (!turns.length) return true;
                const user = turns.filter(t =>
                    t.querySelector("[data-message-author-role='user']"));
                const last = (user.length ? user : turns).slice(-1)[0];
                return !!last.querySelector("img");
            }"""))
        except Exception:                      # noqa: BLE001
            return True                        # can't tell: don't block

    def send(self, text: str) -> None:
        box, sel = self.first("composer")
        box.click()
        # Three ways in, because the composer is a ProseMirror contenteditable
        # and Enter SUBMITS. Anything that types the prompt line by line without
        # Shift would fire off a dozen half-prompts.
        for how, fn in (
            ("fill", lambda: box.fill(text)),
            ("insert_text", lambda: self.page.keyboard.insert_text(text)),
            ("shift-enter", lambda: self._type_lines(text)),
        ):
            try:
                fn()
                got = (box.inner_text() or "").strip()
                if len(got) > len(text) * 0.6:
                    log(f"    composer via {how} ({sel})")
                    break
                log(f"    ! {how} put {len(got)} of {len(text)} chars in; trying next")
            except Exception as e:             # noqa: BLE001
                log(f"    ! {how} failed ({e.__class__.__name__}); trying next")
        else:
            raise RuntimeError("could not get the prompt into the composer")

        self.page.wait_for_timeout(600)
        try:
            btn, _ = self.first("send", timeout=6000)
            btn.click()
        except RuntimeError:
            self.page.keyboard.press("Enter")

    def _type_lines(self, text: str) -> None:
        for i, line in enumerate(text.split("\n")):
            if i:
                self.page.keyboard.press("Shift+Enter")
            self.page.keyboard.type(line, delay=0)

    def rate_limited(self) -> bool:
        try:
            body = (self.page.inner_text("body") or "").lower()
        except Exception:                      # noqa: BLE001
            return False
        return any(m in body for m in RATE_LIMIT_MARKERS)

    def _images(self) -> list:
        """Every image with its natural size and WHOSE TURN it is in.

        The role is what actually separates an input from an output: our
        uploads render inside the user's turn, the generated strip inside the
        assistant's. Shape does not separate them -- a pose guide is wide, like
        a strip -- and neither does "appeared after we sent", because an upload
        can render late and then look new.
        """
        try:
            return self.page.eval_on_selector_all(
                "img",
                """els => els.map(e => {
                     const turn = e.closest("[data-testid^='conversation-turn-']");
                     const holder = turn && turn.querySelector("[data-message-author-role]");
                     return {
                       src: e.currentSrc || e.src,
                       w: e.naturalWidth, h: e.naturalHeight,
                       role: holder ? holder.getAttribute("data-message-author-role") : ""
                     };
                   }).filter(o => o.src)""")
        except Exception:                      # noqa: BLE001
            return []

    def wait_for_image(self, before: set, timeout_s: int = 420) -> str:
        """Poll for a generated image URL in the newest assistant turn.

        Image generation takes 30-120s and shows no single reliable "done"
        event, so this polls rather than waiting on a selector, and ignores
        the reference image we just uploaded by matching only ChatGPT's own
        file-service hosts.
        """
        deadline = time.time() + timeout_s
        seen_working = False
        idle_since = None
        while time.time() < deadline:
            if self.rate_limited():
                raise RateLimited()
            # Two things separate the generated strip from the reference image
            # we uploaded a moment ago, and the first version used NEITHER --
            # so it matched the attachment thumbnail, returned instantly, and
            # saved a byte-identical copy of the reference as the "strip".
            #
            #   1. the strip appears only AFTER the prompt is sent
            #   2. the strip is WIDE; a reference is portrait, and UI icons are
            #      small or square
            # NOT in the user's turn, rather than "in the assistant's": a
            # generated image does not always sit inside a role-tagged
            # container, and requiring one threw away a real generation (the
            # reply read "Bewerken", the Edit caption under a picture). Our own
            # uploads are reliably tagged `user`, which is all this needs; the
            # aspect check in download() is what stops an untagged copy of one.
            hits = [o for o in self._images()
                    if o.get("role") != "user"
                    and o["src"] not in before
                    and ("oaiusercontent" in o["src"] or "/backend-api/" in o["src"])
                    and not o["src"].startswith("blob:")
                    and o["w"] >= MIN_STRIP_W
                    and o["h"] and o["w"] / o["h"] >= MIN_STRIP_ASPECT]
            if hits:
                best = max(hits, key=lambda o: o["w"])
                log(f"    image {best['w']}x{best['h']}"
                    + (f" (turn role {best['role']!r})" if best.get("role") else
                       " (in no role-tagged turn)"))
                return best["src"]

            streaming = bool(self.page.locator(SEL["stop"][0]).count())
            if streaming:
                if not seen_working:
                    seen_working = True
                    log("    generating…")
                idle_since = None
            elif seen_working:
                # The model has finished answering and produced no image, which
                # means it replied in words instead -- usually to say something
                # is wrong with the request. Waiting out the full timeout tells
                # us nothing; the reply itself is the diagnosis.
                idle_since = idle_since or time.time()
                if time.time() - idle_since > 20:
                    raise NoImage(self.last_reply())
            self.page.wait_for_timeout(3000)
        raise TimeoutError(f"no image after {timeout_s}s")

    def last_reply(self, limit: int = 400) -> str:
        """The text of the newest turn, for putting in an error message."""
        try:
            turns = self.page.locator(SEL["turn"][0])
            n = turns.count()
            if n:
                return " ".join((turns.nth(n - 1).inner_text() or "").split())[:limit]
        except Exception:                      # noqa: BLE001
            pass
        return "(could not read the reply)"

    @staticmethod
    def png_size(data: bytes):
        """Width/height straight out of the PNG IHDR, with no dependencies.

        Pillow is not necessarily installed where this runs, and the point is
        only to confirm the bytes are the wide strip we think they are.
        """
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return (int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"))

    def download(self, url: str, dest: Path, inputs=()) -> int:
        """Fetch through the page so the session's cookies apply.

        `inputs` are the files we attached. ChatGPT serves a resized copy of an
        upload from its own file service, so a copy of one cannot be recognised
        by its bytes -- but resizing preserves the ASPECT, and a pose guide's
        aspect (five tall cells) is nothing like a strip's. A download whose
        aspect matches an attachment's to within half a percent is that
        attachment coming back, not a generation.
        """
        data = self.page.evaluate(
            """async (u) => {
                 const r = await fetch(u, {credentials: 'include'});
                 if (!r.ok) throw new Error('HTTP ' + r.status);
                 const b = new Uint8Array(await r.arrayBuffer());
                 return Array.from(b);
               }""", url)
        raw = bytes(data)
        size = self.png_size(raw)
        for src in inputs:
            try:
                in_size = self.png_size(src.read_bytes()[:64])
            except OSError:
                continue
            if not (size and in_size and in_size[1]):
                continue
            a_in, a_got = in_size[0] / in_size[1], size[0] / max(size[1], 1)
            if abs(a_got - a_in) <= 0.005 * a_in:
                raise NoImage(
                    f"downloaded a {size[0]}x{size[1]} image with the same "
                    f"shape as {src.name} ({in_size[0]}x{in_size[1]}) — that is "
                    f"the attachment coming back, not a generated strip")
        if size and (size[0] < MIN_STRIP_W or size[0] / max(size[1], 1) < MIN_STRIP_ASPECT):
            raise NoImage(
                f"downloaded a {size[0]}x{size[1]} image, which is not a strip "
                f"— that is almost certainly the reference, not the output")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        return dest.stat().st_size


class RateLimited(Exception):
    pass


class NoImage(Exception):
    """The model answered in words instead of producing an image."""
    def __init__(self, reply: str):
        super().__init__(f"ChatGPT replied without an image: {reply!r}")


# --------------------------------------------------------------------------

def run(jobs: list[dict], args) -> int:
    from playwright.sync_api import sync_playwright

    PROFILE.mkdir(parents=True, exist_ok=True)
    DEBUG.mkdir(parents=True, exist_ok=True)
    done = failed = 0

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=args.headless,
            viewport={"width": 1400, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        bot = ChatGPT(ctx, slow=args.slow)

        bot.new_chat()
        if not bot.signed_in():
            log("NOT SIGNED IN — sign in to ChatGPT in the window that just opened.")
            log("This is a one-off; the profile in .chatgpt-profile/ persists.")
            log("No keypress needed here — this notices by itself. Leave the")
            log("browser window open when you're done.")
            if not bot.wait_for_sign_in(minutes=args.signin_wait):
                ctx.close()
                sys.exit("still not signed in after waiting; stopping")
        log("signed in")

        if getattr(args, "dom", False):
            for line in bot.dom_report().splitlines():
                log("  " + line)
            ctx.close()
            return 0

        for n, job in enumerate(jobs, 1):
            tag = f"{job['char']}/{job['seq']} r{job['roll']}"
            log(f"[{n}/{len(jobs)}] {tag} — {job['cells']} cells, "
                f"ref {job['ref'].name}"
                + (f", guide {job['guide'].name}" if job["guide"] else ""))
            if not job["ref"].exists():
                log(f"    ! reference missing: {job['ref']} — skipping")
                failed += 1
                continue
            # A guide named in the manifest but absent from disk is a mistake,
            # not an option: the prompt that goes with it talks about a second
            # image, so sending it alone asks for a pose nothing describes.
            if job["guide"] and not job["guide"].exists():
                log(f"    ! pose guide missing: {job['guide']} — skipping")
                failed += 1
                continue
            try:
                bot.new_chat()
                # The reference goes first and stays the authority on identity;
                # the guide is attached second and the prompt names it by what
                # it looks like, not by its position, in case the order slips.
                bot.attach(job["ref"])
                if job["guide"]:
                    bot.attach(job["guide"])
                before = {o["src"] for o in bot._images()}
                bot.send(job["text"])
                bot.page.wait_for_timeout(4000)
                if not bot.sent_with_image():
                    raise NoImage("the sent message carried no image — the "
                                  "reference did not travel with the prompt")
                # A SECOND snapshot, and it cost two rolls to learn why. Until
                # a message is sent its attachments are buttons, not <img>, so
                # the snapshot above cannot see them; wait_for_image then falls
                # back on SHAPE, and shape is exactly what stops separating the
                # input from the output once a pose guide is attached. A guide
                # is wide, five cells on one ground line -- it passes the strip
                # filter as well as a real strip does, and both rolls returned
                # the guide itself, byte-identical, three seconds after sending.
                # The user turn has now rendered, so everything on the page is
                # an input and only the assistant's image can appear after here.
                before |= {o["src"] for o in bot._images()}
                url = bot.wait_for_image(before, timeout_s=args.timeout)
                size = bot.download(url, job["out"],
                                    inputs=[f for f in (job["ref"], job["guide"]) if f])
                job["sidecar"].write_text(json.dumps({
                    "character": job["char"], "sequence": job["seq"],
                    "roll": job["roll"], "frames": job["frames"],
                    "cells": job["cells"], "prompt_hash": job["hash"],
                    "reference": str(job["ref"].relative_to(ROOT)),
                    "guide": (str(job["guide"].relative_to(ROOT))
                              if job["guide"] else None),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source_url": url, "bytes": size,
                    "prompt": job["text"],
                }, indent=1), encoding="utf-8")
                log(f"    saved {job['out'].name} ({size // 1024} KB)")
                done += 1
                if args.once:
                    log("--once: stopping after one strip")
                    break
                bot.page.wait_for_timeout(
                    int(args.gap * 1000 * random.uniform(0.8, 1.3)))
            except RateLimited:
                log(f"    RATE LIMITED — sleeping {args.cooldown // 60} min, "
                    f"then retrying this job")
                shot(bot.page, f"ratelimit-{job['char']}-{job['seq']}")
                time.sleep(args.cooldown)
                jobs.append(job)                # back of the queue
            except NoImage as e:
                log(f"    NO IMAGE — {e}")
                log("    (that is ChatGPT's own words; it usually says what it "
                    "wanted and did not get)")
                shot(bot.page, f"noimage-{job['char']}-{job['seq']}")
                failed += 1
            except Exception as e:              # noqa: BLE001
                log(f"    FAILED: {e.__class__.__name__}: {e}")
                shot(bot.page, f"fail-{job['char']}-{job['seq']}-r{job['roll']}")
                failed += 1
        ctx.close()

    log(f"done: {done} generated, {failed} failed")
    return 1 if failed and not done else 0


def shot(page, name: str) -> None:
    try:
        p = DEBUG / f"{name}-{int(time.time())}.png"
        page.screenshot(path=str(p), full_page=False)
        log(f"    screenshot: {p.relative_to(ROOT)}")
    except Exception:                           # noqa: BLE001
        pass


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--char", action="append", default=[],
                    help="character key (repeatable); default all")
    ap.add_argument("--seq", action="append", default=[],
                    help="sequence name (repeatable); default all")
    ap.add_argument("--rolls", type=int, default=1,
                    help="takes per sequence (default 1). Re-rolls are a coin "
                         "flip, so 2 is a reasonable first pass.")
    ap.add_argument("--dom", action="store_true",
                    help="open ChatGPT, print what the composer looks like, and "
                         "exit — for when an attach stops working")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the job list and exit; no browser")
    ap.add_argument("--once", action="store_true", help="stop after one strip")
    ap.add_argument("--headless", action="store_true",
                    help="hide the browser (NOT for the first run)")
    ap.add_argument("--slow", action="store_true",
                    help="longer waits everywhere; try this if uploads race")
    ap.add_argument("--signin-wait", type=int, default=10,
                    help="minutes to wait for a manual sign-in (default 10)")
    ap.add_argument("--timeout", type=int, default=420,
                    help="seconds to wait for one image (default 420)")
    ap.add_argument("--gap", type=float, default=8.0,
                    help="seconds between strips (default 8)")
    ap.add_argument("--cooldown", type=int, default=900,
                    help="seconds to sleep on a rate limit (default 900)")
    args = ap.parse_args()

    jobs = plan(args.char, args.seq, args.rolls)
    if args.dom:
        sys.exit(run(jobs or [], args))
    if not jobs:
        log("nothing to do — every requested strip is already on disk")
        return
    log(f"{len(jobs)} strip(s) to generate")
    if args.dry_run:
        for j in jobs:
            print(f"  {j['char']:<14} {j['seq']:<20} r{j['roll']}  "
                  f"{j['cells']} cells  ref={j['ref'].name}  "
                  f"guide={j['guide'].name if j['guide'] else '--'}  "
                  f"prompt={j['hash']}  -> {j['out'].relative_to(ROOT)}")
        return
    sys.exit(run(jobs, args))


if __name__ == "__main__":
    main()
