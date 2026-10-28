r"""
The state page: what a session needs from the stack, and nothing else.

    python -m rota.tools.state                    # every held frame
    python -m rota.tools.state --sid 21800a2b     # one session's frames
    python -m rota.tools.state --from bf5baa63    # with a sender's doubts
    python -m rota.tools.state --since 2026-10-17 # for Roman's return

The stack is the history, and nobody reads it whole. A take that read the
stack cost 35k of context (observed: the count hook, 2026-10-18). This
tool prints the held frames, the count of live things, the open decisions
and the leaving session's doubts, about 3k tokens in all. It reads
`plans/stack.md` in place and never edits it.

No ruling prints on the normal page. A ruling lives at the thing it rules
(reasoned: `plans/method/design.md`, section 2, rulings at the thing).
`--since` is the exception. It prints his rulings back to him on his
return, beside what closed, what was assumed and what waits on him.
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
HOLDERS = re.compile(r"\s*\([0-9a-f]{8}\)")
SID = re.compile(r"\(([0-9a-f]{8})\)")
STATUS = re.compile(r"^- Status (\d{4}-\d\d-\d\d \d\d:\d\d) \(([^)]*)\):\s?(.*)$")
RATING = re.compile(r"\[(high|med|low)\]|\b(high|medium|low) impact\b")
WORKFLOW = re.compile(r"\b(Meta|Rota) workflow\b")
BOLD_SITE = re.compile(r"\*\*Site:\s*(.*?)\*\*")
PLAIN_SITE = re.compile(r"Site:\s*(.*?\.)(?:\s|$)")
ORDER_WAIT = re.compile(r"Roman's order|the sprint order|Roman orders it")
# A mark cites a word he gave. It is not a wait for a word he has not
# given, so it opens no decision (observed: 2026-10-26, five Waits-on
# lines read as open decisions on a citation alone).
CITED = re.compile(r"\((?:ruled|reasoned|observed)[^)]*\)")
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
        return "%s. %s" % (self.number, HOLDERS.sub("", self.heading).strip())

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
        """The workflow word after the Site field, else the first in the frame.

        Older frames carry the word on a bullet of its own. A status line
        names the workflow of its own statement, so it is read last.
        """
        line = self.what
        at = line.find("Site:")
        m = WORKFLOW.search(line, at if at >= 0 else 0)
        if m:
            return m.group(1)
        rest = self.lines[1:]
        for other in ([x for x in rest if not STATUS.match(x)]
                      + [x for x in rest if STATUS.match(x)]):
            m = WORKFLOW.search(other)
            if m:
                return m.group(1)
        return ""

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
        """The rating of the Waits on line first, then of any line.

        A rating is `[high]`, `[med]` or `[low]`, or the words "high
        impact", "medium impact" or "low impact".
        """
        for line in [self.waits] + self.lines:
            m = RATING.search(line)
            if m:
                word = m.group(1) or m.group(2)
                return "med" if word == "medium" else word
        return ""

    @property
    def waits_on_roman(self) -> bool:
        """The Waits on line names Roman for a decision, not for an order.

        A frame carries no wait on his order (ruled: Roman, 2026-10-12
        23:40). So a mention that is only an order does not count. A wait
        that starts with "nothing" waits on nobody, whatever follows.
        """
        if self.waits.lower().startswith("nothing"):
            return False
        return "Roman" in CITED.sub("", ORDER_WAIT.sub("", self.waits))


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
            # Every sid group in the heading counts, wherever it stands, so a
            # trailing tag such as "(parked)" does not unhold a frame.
            current = Frame(number=m.group(1), heading=heading, start=i, end=i + 1,
                            holders=SID.findall(heading),
                            roman="(Roman)" in heading)
        if current is not None:
            current.lines.append(line)
    if current is not None:
        current.end = hi
        frames.append(current)
    return frames


def open_frames(stack: Path | None = None) -> set[int]:
    """The numbers of the frames that the stack holds, held or parked.

    A frame closes when it moves to `plans/archive`, so every frame left in
    the stack file is open. A parked frame is open too, because it still owes
    its work. A debt in the suite names the frame that owes it, and this is
    the one reader that says the frame is still open (fact F33 of
    `plans/rootfix-audit-2026-10-27-b.md`).
    """
    path = stack if stack is not None else default_stack()
    return {int(f.number) for f in parse(read_lines(path), bounded=False)}


REACH = "- Reach:"


def reach_line(block: list[str] | str) -> str | None:
    """The text after `Reach:` on a frame block's last Reach line, or None.

    Rule C76 of `plans/method/reference.md` counts the reach of a placed
    cause before its pass. The status tool gates on this one reader, so
    no second reader parses the line its own way. A recount is a new Reach
    line below the old one, so the last line wins, as the last status line
    does (observed: plans/frame340-review-p1.md, finding 4). A wrapped
    Reach line keeps its continuation lines.
    """
    lines = block.split("\n") if isinstance(block, str) else block
    lines = [line.rstrip("\r") for line in lines]
    found = None
    for i, line in enumerate(lines):
        if not line.startswith(REACH):
            continue
        parts = [line[len(REACH):].strip()]
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.startswith("- ") or nxt.startswith("#"):
                break
            parts.append(nxt.strip())
        found = " ".join(p for p in parts if p)
    return found


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


ARCHIVE = re.compile(r"^stack-(\d{4}-\d\d-\d\d)\.md$")
# A decision taken for Roman while he is away carries one of these marks
# (reasoned: the session, 2026-10-18, step 5's review found no findable
# assumption in 229 status lines; `plans/method/reference.md`, section 8).
ASSUMED = ("taken by timeout", "(assumed:")
RULED_MARK = re.compile(r"\(ruled: Roman(?:, (\d{4}-\d\d-\d\d))?")
RULING_KEY = re.compile(r"Roman, (\d{4}-\d\d-\d\d)(?: about)? (\d\d:\d\d)")
QUOTE = re.compile(r'"([^"]{4,})"')
RANK = {"high": 0, "med": 1, "low": 2, "": 3}
NAME_LIMIT = 100
ROW_LIMIT = 300
SINCE_LIMIT = 12000


def archives_since(stack: Path, since: str) -> list[tuple[str, Path]]:
    """The archive files dated at or after `since`, newest first."""
    archive = stack.resolve().parent / "archive"
    dated = []
    if archive.is_dir():
        for path in archive.iterdir():
            m = ARCHIVE.match(path.name)
            if m and m.group(1) >= since:
                dated.append((m.group(1), path))
    return sorted(dated, reverse=True)


def closed_since(archives: list[tuple[str, Path]]) -> list[str]:
    """The frame headings of the archive files, newest file first."""
    rows: list[str] = []
    for day, path in archives:
        for line in read_lines(path):
            m = HEAD.match(line)
            if m:
                name = HOLDERS.sub("", m.group(2)).strip()
                rows.append(cut("%s. %s" % (m.group(1), name), NAME_LIMIT)
                            + " (archived %s)" % day)
    return rows


def dated_statuses(frames: list[tuple[Frame, bool]],
                   since: str) -> list[tuple[str, Frame, bool, str]]:
    """Every status line dated at or after `since`, newest first.

    Each frame comes with a flag that says it closed into the archive.
    """
    rows = []
    for f, closed in frames:
        for i in f.statuses:
            line = f.lines[i]
            when = STATUS.match(line).group(1)
            if when[:10] >= since:
                rows.append((when, f, closed, line))
    rows.sort(key=lambda r: r[0], reverse=True)
    return rows


def is_assumed(line: str) -> bool:
    return any(mark in line for mark in ASSUMED)


def is_ruling(line: str, since: str) -> bool:
    """A status in his words, by its start or by a ruling mark.

    A mark with a date counts when the date is at or after `since`. A
    mark with no date, such as "(ruled: Roman, in his words)", counts by
    the status line's own date, which the caller already filtered.
    """
    body = STATUS.match(line).group(3)
    if body.startswith("**ruled"):
        return True
    return any(not day or day >= since for day in RULED_MARK.findall(line))


def ruling_key(line: str) -> str:
    """What makes two ruling rows the same ruling: its time, else its words."""
    m = RULING_KEY.search(line)
    if m:
        return "at %s %s" % m.groups()
    m = QUOTE.search(line)
    if m:
        return "words " + m.group(1)
    return "line " + line


def since_row(frame: Frame, closed: bool, line: str, again: int = 0) -> str:
    name = cut(HOLDERS.sub("", frame.heading).strip(), 80)
    tail = " (cited again %d times)" % again if again else ""
    mark = " (closed)" if closed else ""
    return cut("%s. %s%s :: %s" % (frame.number, name, mark, line),
               ROW_LIMIT - len(tail)) + tail


def fold_rulings(rows: list[tuple[str, Frame, bool, str]]) -> list[str]:
    """One row per ruling, newest first, with the count of later citations.

    The first status that carries a ruling keeps the row. A later status
    with the same key only repeats or cites it, so it adds to the count.
    """
    first: dict[str, list] = {}
    for when, f, closed, line in sorted(rows, key=lambda r: r[0]):
        key = ruling_key(line)
        if key in first:
            first[key][4] += 1
        else:
            first[key] = [when, f, closed, line, 0]
    kept = sorted(first.values(), key=lambda r: r[0], reverse=True)
    return [since_row(f, closed, line, again) for _, f, closed, line, again in kept]


def render_since(stack: Path, since: str, cap: int = SINCE_LIMIT) -> str:
    """The page for Roman's return: four sections and nothing else.

    His attention is the scarcest budget, and a return should cost one
    screen (reasoned: `plans/method/design.md`, section 2, autonomy). So
    the page holds at `cap` characters. The oldest rows of the closed, the
    assumed and the ruled sections go, the longest section first, and the
    page says how many went. The waits are never cut, because they are
    what he must answer.
    """
    frames = parse(read_lines(stack))
    head = ["State since %s of %s, printed %s." % (
        since, stack.as_posix(), time.strftime("%Y-%m-%d %H:%M"))]
    archives = archives_since(stack, since)
    closed = closed_since(archives)
    # A frame that closed while he was away took its status lines to the
    # archive, so the archive is read too.
    every = [(f, False) for f in frames] + [
        (f, True) for _, path in archives
        for f in parse(read_lines(path), bounded=False)]
    statuses = dated_statuses(every, since)
    assumed = [since_row(f, shut, line) for _, f, shut, line in statuses
               if is_assumed(line)]
    ruled = fold_rulings([r for r in statuses if is_ruling(r[3], since)])
    asks = sorted([f for f in frames if f.waits_on_roman],
                  key=lambda f: RANK.get(f.rating, 3))
    waits = ["[%s] %s: %s" % (f.rating or "unrated", f.title,
                              cut(f.waits, FIELD_LIMIT)) for f in asks]

    sections = [("Closed since %s" % since, closed),
                ("Decided under assumption since %s" % since, assumed),
                ("Waits on Roman", waits),
                ("Rulings since %s" % since, ruled)]
    shown = [len(rows) for _, rows in sections]
    cuttable = (0, 1, 3)

    def page() -> str:
        out = list(head)
        for (title, rows), n in zip(sections, shown):
            out += ["", "## " + title]
            out += rows[:n] or ["None."]
            if n < len(rows):
                out.append("%d older rows cut to keep the page under %d characters."
                           % (len(rows) - n, cap))
        return "\n".join(out) + "\n"

    text = page()
    while len(text) > cap:
        sizes = {i: sum(len(r) + 1 for r in sections[i][1][:shown[i]])
                 for i in cuttable if shown[i]}
        if not sizes:
            break
        longest = max(sizes, key=lambda i: sizes[i])
        shown[longest] -= 1
        text = page()
    return text


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
    p.add_argument("--since", default="",
                   help="YYYY-MM-DD: print what closed, what was assumed, what "
                        "waits on Roman and his rulings since that date, and "
                        "nothing else")
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
    if args.since:
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", args.since):
            print("--since takes a date, YYYY-MM-DD", file=sys.stderr)
            return 2
        text = render_since(stack, args.since)
    else:
        text = render(stack, args.sid, args.sender, args.limit)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
