r"""
The state page: what a session needs from the stack, and nothing else.

    python -m rota.tools.state                    # every held frame
    python -m rota.tools.state --sid 21800a2b     # one session's frames
    python -m rota.tools.state --from bf5baa63    # with a sender's doubts

The stack is the history, and nobody reads it whole. A take that read the
stack cost 35k of context (observed: the count hook, 2026-10-18). This
tool prints the held frames, the count of live things, the open decisions
and the leaving session's doubts, about 3k tokens in all. It reads
`plans/stack.md` in place and never edits it.

No ruling prints here. A ruling lives at the thing it rules (reasoned:
`plans/method/design.md`, section 2, rulings at the thing).
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from rota.tools import handover

HEAD = re.compile(r"^### (\d+)\.\s+(.*)$")
TAGS = re.compile(r"((?:\s*\((?:[0-9a-f]{8}|Roman)\))+)\s*$")
HOLDERS = re.compile(r"(?:\s*\([0-9a-f]{8}\))+\s*$")
SID = re.compile(r"\(([0-9a-f]{8})\)")
STATUS = re.compile(r"^- Status (\d{4}-\d\d-\d\d \d\d:\d\d) \(([^)]*)\):\s?(.*)$")
RATING = re.compile(r"\[(high|med|low)\]")
WORKFLOW = re.compile(r"\b(Meta|Rota) workflow\b")
BOLD_SITE = re.compile(r"\*\*Site:\s*(.*?)\*\*")
PLAIN_SITE = re.compile(r"Site:\s*(.*?\.)(?:\s|$)")
DOUBTS = "## What I believe, and what to doubt"

FIELD_LIMIT = 200
STATUS_LIMIT = 400
LIVE_CAP = 10        # the frame economy of the method design, section 2


def cut(text: str, limit: int) -> str:
    """Cut a text at a limit, and show the cut."""
    if len(text) <= limit:
        return text
    return text[:max(limit - 3, 0)].rstrip() + "..."


@dataclass
class Frame:
    """One frame of the stack, read from its heading to the next heading."""

    number: str
    heading: str
    start: int
    end: int
    lines: list[str] = field(default_factory=list)
    holders: list[str] = field(default_factory=list)
    roman: bool = False

    @property
    def holder(self) -> str:
        """The last session id in the heading holds the frame."""
        return self.holders[-1] if self.holders else ""

    @property
    def title(self) -> str:
        """The heading without the session tags, which the section names.

        `(Roman)` stays, because it says the frame is his ask.
        """
        return "%s. %s" % (self.number, HOLDERS.sub("", self.heading).rstrip())

    def first(self, prefix: str) -> tuple[int, str] | None:
        for i, line in enumerate(self.lines):
            if line.startswith(prefix):
                return i, line
        return None

    @property
    def what(self) -> str:
        """The frame's first bullet, which carries the Site field."""
        hit = self.first("- ")
        return hit[1] if hit else ""

    @property
    def site(self) -> str:
        line = self.what
        m = BOLD_SITE.search(line)
        if m:
            text = m.group(1)
        else:
            m = PLAIN_SITE.search(line)
            text = m.group(1) if m else ""
        return WORKFLOW.sub("", text).rstrip(" .") if text else ""

    @property
    def workflow(self) -> str:
        """The workflow word after the Site field: Meta, Rota, or empty."""
        line = self.what
        at = line.find("Site:")
        m = WORKFLOW.search(line, at if at >= 0 else 0)
        return m.group(1) if m else ""

    def field_text(self, prefix: str) -> str:
        hit = self.first(prefix)
        return hit[1][len(prefix):].strip() if hit else ""

    @property
    def waits(self) -> str:
        return self.field_text("- Waits on:")

    @property
    def sprint(self) -> str:
        return self.field_text("- Sprint:")

    @property
    def statuses(self) -> list[int]:
        """The indexes of the status lines, in the order of the file."""
        return [i for i, line in enumerate(self.lines) if STATUS.match(line)]

    @property
    def rating(self) -> str:
        """The rating of the Waits on line first, then of any line."""
        m = RATING.search(self.waits)
        if m:
            return m.group(1)
        for line in self.lines:
            m = RATING.search(line)
            if m:
                return m.group(1)
        return ""

    @property
    def waits_on_roman(self) -> bool:
        return "Roman" in self.waits


def parse(lines: list[str], bounded: bool = True) -> list[Frame]:
    """Read the frames between `## Stack` and `## Parked`.

    The lines carry no line end. With `bounded` false, every frame of the
    file is read, because a status line can go to a parked frame too.
    """
    lo, hi = 0, len(lines)
    if bounded:
        for i, line in enumerate(lines):
            if line.rstrip() == "## Stack" and lo == 0:
                lo = i + 1
            elif line.startswith("## Parked"):
                hi = i
                break
    frames: list[Frame] = []
    current: Frame | None = None
    for i in range(lo, hi):
        line = lines[i]
        m = HEAD.match(line)
        if m or line.startswith("#"):
            if current is not None:
                current.end = i
                frames.append(current)
                current = None
        if m:
            heading = m.group(2).rstrip()
            tags = TAGS.search(heading)
            group = tags.group(1) if tags else ""
            current = Frame(number=m.group(1), heading=heading, start=i, end=i + 1,
                            holders=SID.findall(group), roman="(Roman)" in group)
        if current is not None:
            current.lines.append(line)
    if current is not None:
        current.end = hi
        frames.append(current)
    return frames


def read_lines(path: Path) -> list[str]:
    """The file's lines with no line end, whatever line end the file uses."""
    text = path.read_bytes().decode("utf-8")
    return [line.rstrip("\r") for line in text.split("\n")]


def status_line(line: str, limit: int) -> str:
    """Cut a status line in its body, so the time and the peer name stay."""
    m = STATUS.match(line)
    if not m:
        return cut(line, limit)
    head = "- Status %s (%s): " % (m.group(1), m.group(2))
    return head + cut(m.group(3), max(limit - len(head), 40))


def print_frame(frame: Frame, limit: int, out: list[str]) -> None:
    """Four lines: the heading, the site, the waits and sprint, the last status."""
    out.append(frame.title)
    out.append("  Site: %s%s" % (cut(frame.site or "(none)", FIELD_LIMIT),
                                 (". %s workflow." % frame.workflow)
                                 if frame.workflow else ""))
    out.append("  Waits on: %s | Sprint: %s" % (
        cut(frame.waits or "(none)", FIELD_LIMIT),
        cut(frame.sprint or "(none)", FIELD_LIMIT)))
    marks = frame.statuses
    out.append("  " + (status_line(frame.lines[marks[-1]], limit)
                       if marks else "(no status line)"))


def mailbox_root(stack: Path) -> Path:
    """The directory that holds `.handover`, the way `handover.py` finds it.

    Outside git, `_root` answers the directory it starts in, which is
    `plans/`. The mailbox then sits one level up, beside `plans/`.
    """
    start = stack.resolve().parent
    root = handover._root(start)
    if root == start and start.name == "plans":
        return start.parent
    return root


def sender_of(root: Path, sid: str) -> dict | None:
    """The claim that handed this session its frame, or None.

    `take` moves the claim into `taken/` and names the receipt in the
    peer state, so a claim is read from the claim file first, then from
    the receipt, then from the peer state's sender.
    """
    if not (root / handover.BOX).is_dir():
        return None
    box = handover.Box(root)
    try:
        claim = handover._read_json(box.claim_file(sid))
    except handover.Unreadable:
        claim = None
    if not claim:
        state = box.read_state(sid) or {}
        receipt = state.get("receipt")
        if receipt:
            claim = box.soft(box.taken / str(receipt), "receipt")
        if not claim and state.get("from_sid"):
            claim = {"from_sid": state["from_sid"]}
    if not claim or not claim.get("from_sid"):
        return None
    return claim


def doubts(note: Path) -> str:
    """The note's section of beliefs and doubts, verbatim, or empty."""
    lines = read_lines(note)
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line.rstrip() == DOUBTS
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip("\n")


def render(stack: Path, sid: str = "", sender: str = "",
           limit: int = STATUS_LIMIT) -> str:
    """The state page as one text."""
    frames = parse(read_lines(stack))
    held = [f for f in frames if f.holder]
    out: list[str] = ["State of %s, printed %s." % (
        stack.as_posix(), time.strftime("%Y-%m-%d %H:%M"))]

    if sid:
        groups = [(sid, [f for f in held if f.holder == sid[:8]])]
    else:
        by: dict[str, list[Frame]] = {}
        for f in held:
            by.setdefault(f.holder, []).append(f)
        groups = sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for holder, mine in groups:
        out.append("")
        out.append("## Held by %s" % holder[:8])
        if not mine:
            out.append("No frame.")
        for f in mine:
            print_frame(f, limit, out)

    live = len(held) + len([f for f in frames if not f.holder and f.waits_on_roman])
    out += ["", "## Live", "Live things: %d of %d" % (live, LIVE_CAP)]
    if live > LIVE_CAP:
        # The economy prints and never refuses: a tool enables and never
        # gates (ruled: Roman, 2026-10-18 02:25).
        out.append("Over the frame economy by %d: park or close before you push."
                   % (live - LIVE_CAP))

    out += ["", "## Open decisions"]
    asks = [f for f in frames if f.waits_on_roman]
    for f in asks:
        out.append("[%s] %s: %s" % (f.rating or "unrated", f.title,
                                    cut(f.waits, FIELD_LIMIT)))
    if not asks:
        out.append("None.")

    claim = None
    root = mailbox_root(stack)
    if sender:
        claim = {"from_sid": sender}
    elif sid:
        claim = sender_of(root, sid[:8])
    if claim:
        who = str(claim["from_sid"])[:8]
        name = ""
        if (root / handover.BOX).is_dir():
            name = handover.sender_name(handover.Box(root), claim)
        out += ["", "## The leaving session's doubts",
                "From %s%s." % (who, " (%s)" % name if name else "")]
        note = handover.momentum_note(stack.resolve().parent.parent, who)
        text = doubts(note) if note else ""
        if not note:
            out.append("No momentum note found for %s." % who)
        elif not text:
            out.append("The note %s has no section headed %r." % (
                note.as_posix(), DOUBTS))
        else:
            out.append(text)

    out += ["", "## Next", "Read the frame's Pointer before you act on it."]
    return "\n".join(out) + "\n"


def default_stack() -> Path:
    top = handover._git(Path.cwd(), "rev-parse", "--show-toplevel")
    return (Path(top) if top else Path.cwd()) / "plans" / "stack.md"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Print the state page from the stack.")
    p.add_argument("--sid", default="", help="print the frames this session holds")
    p.add_argument("--from", dest="sender", default="",
                   help="print this sender's doubts from its momentum note")
    p.add_argument("--stack", default=None, help="the stack, plans/stack.md by default")
    p.add_argument("--limit", type=int, default=STATUS_LIMIT,
                   help="characters of the last status line")
    args = p.parse_args(argv)
    for value in (args.sid, args.sender):
        bad = handover._check_sid(value) if value else ""
        if bad:
            print("a session id is not usable: %s" % bad, file=sys.stderr)
            return 2
    stack = Path(args.stack) if args.stack else default_stack()
    if not stack.is_file():
        print("no stack at %s" % stack, file=sys.stderr)
        return 2
    text = render(stack, args.sid, args.sender, args.limit)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
