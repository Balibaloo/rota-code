r"""
Append one status line to a frame of the stack, and commit the stack alone.

    python -m rota.tools.status 287 --sid 21800a2b --body line.txt
    python -m rota.tools.status 287 --sid 21800a2b --text "pass 1 landed"
    python -m rota.tools.status 287 --sid 21800a2b --ruling "his words" --at 02:35

Two steps failed often enough by hand to become a tool. A status time was
typed from memory 15 times by 2026-10-15 (observed: the memory file of the
status time). A body with a backslash went through a heredoc and lost it
27 times by 2026-09-30 (observed: the memory file of the heredoc). So the
time comes from the clock here, never from an argument, and the body comes
from a file or one argument, never from a shell heredoc.

The peer name comes from the hook's enrolment of the session. A session
with no enrolment gets its session id in the line and a warning. The tool
never refuses a status line for a missing name (ruled: Roman, 2026-10-18
02:25, "enabling not inhibiting").

Two gates enforce rule C76 of `plans/method/reference.md`: an issue is
read, and its reach counted, before it is fixed (ruled: Roman, 2026-10-26
about 21:17). Fourteen frames fixed 0 of 14 at the source while the rule
was a reminder (observed: `plans/agency-prevalence-2026-10-26.md`). So
the tool refuses a pass line on a frame with no `- Reach:` line. It also
refuses a close while the Reach line reads fewer places than its count.
`--force-close` passes the second gate and writes its reason into the
line. Nothing passes the first gate. A `--ruling` body is his words, and
no gate refuses it.

Exit codes: 0 the line is written and committed, or written with
`--no-commit`; 1 the line is written and the commit failed; 2 a usage
error, a frame that the stack does not hold, or a refusal of a gate.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rota.tools import handover, state


PASS_LINE = re.compile(
    r"\bpass \d+[a-z]? (runs|built|is at)\b|\bimplementer\b.*\bruns\b", re.IGNORECASE)
# A read, a review or a gate runs on a pass but is not one, so it needs no
# Reach line (reasoned: the pass 1 brief of frame 340).
NOT_PASS = re.compile(r"\b(read|review|reviewer|gate)\b", re.IGNORECASE)
CLOSE_LINE = re.compile(r"(?:^|\*\*)\s*(closed|closes|popped|pops)\b", re.IGNORECASE)
COUNT = re.compile(r"^(\d+)\s+of\s+(\d+)\b")
WANT_REACH = '"- Reach: <k> of <N>, <where the gap is>"'


def gate(frame: str, block: list[str], body: str, force: str | None) -> str:
    """The refusal of rule C76 for a body, or empty when the body passes.

    The first gate refuses a pass line on a frame with no Reach line. The
    second refuses a close below the count. `force` passes the second only.
    """
    reach = state.reach_line(block)
    if reach is None and PASS_LINE.search(body) and not NOT_PASS.search(body):
        return ("frame %s has no Reach line. Write %s after the Waits on line "
                "before any pass." % (frame, WANT_REACH))
    if force is not None or not CLOSE_LINE.search(body):
        return ""
    if reach is None:
        return ("frame %s has no Reach line, so no count shows its reach. Write %s "
                'before the close, or give --force-close "<reason>".'
                % (frame, WANT_REACH))
    m = COUNT.match(reach)
    if m and int(m.group(1)) < int(m.group(2)):
        return ("frame %s has Reach %s of %s. Close it when the Reach line reads "
                '%s of %s, or give --force-close "<reason>".'
                % (frame, m.group(1), m.group(2), m.group(2), m.group(2)))
    return ""


def _clock() -> datetime:
    """The clock. Tests replace this, and no argument does."""
    return datetime.now()


def one_line(text: str) -> str:
    """Join the lines of a body with one space each."""
    return re.sub(r"\s*\r?\n\s*", " ", text).strip()


def peer_name(stack: Path, sid: str) -> str:
    """The name the hook enrolled for the session, or empty.

    The enrolment is read without building a mailbox, so a repository
    with no `.handover` stays without one.
    """
    root = state.mailbox_root(stack)
    path = root / handover.BOX / "sessions" / (sid[:8] + ".json")
    try:
        row = handover._read_json(path) or {}
    except handover.Unreadable:
        return ""
    return str(row.get("name") or "")


def insert(text: str, frame: str, line: str) -> tuple[str, int]:
    """Insert one line into a frame. Return the new text and the line index.

    The line goes after the frame's last status line, or after its Pointer
    line when it has no status line, or after its last bullet. The file's
    own line end is kept, so a CRLF file stays CRLF and an LF file stays LF.
    """
    eol = "\r\n" if "\r\n" in text else "\n"
    raw = text.split("\n")
    bare = [r.rstrip("\r") for r in raw]
    found = [f for f in state.parse(bare, bounded=False) if f.number == str(frame)]
    if not found:
        raise KeyError(frame)
    f = found[0]
    marks = f.statuses
    if marks:
        at = marks[-1]
    else:
        hit = f.first("- Pointer:")
        if hit:
            at = hit[0]
        else:
            bullets = [i for i, b in enumerate(f.lines) if b.startswith("- ")]
            at = bullets[-1] if bullets else 0
    # A bullet can wrap. Its continuation runs to the next line that is
    # blank or starts a bullet or a heading, and the new line goes after it.
    # 10 of 125 live frames end on a wrapped status (observed: the review of
    # f934ec21, 2026-10-18).
    while at + 1 < len(f.lines):
        nxt = f.lines[at + 1]
        if not nxt.strip() or nxt.startswith("- ") or nxt.startswith("#"):
            break
        at += 1
    index = f.start + at + 1
    raw.insert(index, line + ("\r" if eol == "\r\n" else ""))
    return "\n".join(raw), index


def ruling_body(words: str, at: str, today: str, workflow: str) -> str:
    body = ('**ruled. Roman, %s %s, in the terminal: "%s"** (ruled: Roman, in his words).'
            % (today, at, one_line(words)))
    if workflow:
        body += " %s workflow." % workflow
    return body


def summary(frame: str, body: str) -> str:
    words = body.replace("*", "").replace("`", "").split()[:8]
    head = " ".join(words).rstrip(".,;:")
    return "docs(plans): frame %s, %s" % (frame, head)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def commit(stack: Path, frame: str, body: str, when: str, sid: str) -> int:
    """Commit the stack by pathspec, so nothing else staged goes in."""
    repo = stack.resolve().parent
    git(repo, "add", "--", str(stack.resolve()))
    prose = ("The status tool appends one line to frame %s at %s for session %s."
             % (frame, when, sid))
    done = git(repo, "commit", "-m", summary(frame, body), "-m", prose,
               "--", str(stack.resolve()))
    if done.returncode != 0:
        print("the line is written and the commit failed:", file=sys.stderr)
        print((done.stdout + done.stderr).strip(), file=sys.stderr)
        return 1
    sha = git(repo, "rev-parse", "--short=8", "HEAD").stdout.strip()
    print("committed %s" % sha)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Append one status line to a frame and commit the stack.")
    p.add_argument("frame", help="the frame number")
    p.add_argument("--sid", required=True, help="the session that writes the line")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--body", help="a file that holds the body")
    src.add_argument("--text", help="the body as one argument")
    src.add_argument("--ruling", help="Roman's words, written as a ruling")
    p.add_argument("--at", default=None,
                   help="HH:MM of his words, for --ruling. It goes in the body")
    p.add_argument("--date", default=None,
                   help="YYYY-MM-DD of his words, for --ruling, when he said them "
                        "before midnight. Today by default")
    p.add_argument("--workflow", default=None,
                   help="Meta or Rota, when the frame's Site line names neither")
    p.add_argument("--stack", default=None, help="the stack, plans/stack.md by default")
    p.add_argument("--no-commit", action="store_true",
                   help="write the line and commit nothing")
    p.add_argument("--force-close", default=None, metavar="REASON",
                   help="close a frame below its Reach count. The reason goes "
                        "in the line as (forced: REASON)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bad = handover._check_sid(args.sid)
    if bad:
        print("--sid is not usable: %s" % bad, file=sys.stderr)
        return 2
    sid = args.sid[:8]
    stack = Path(args.stack) if args.stack else state.default_stack()
    if not stack.is_file():
        print("no stack at %s" % stack, file=sys.stderr)
        return 2
    text = stack.read_bytes().decode("utf-8")
    now = _clock()
    when = now.strftime("%Y-%m-%d %H:%M")

    if args.body is not None:
        body = one_line(Path(args.body).read_bytes().decode("utf-8"))
    elif args.text is not None:
        body = one_line(args.text)
    else:
        bare = [r.rstrip("\r") for r in text.split("\n")]
        found = [f for f in state.parse(bare, bounded=False)
                 if f.number == str(args.frame)]
        workflow = found[0].workflow if found else ""
        if not workflow and args.workflow:
            workflow = args.workflow.strip().capitalize()
        if not workflow:
            print("WARNING: the frame names no workflow and --workflow is not "
                  "given, so the ruling carries no workflow word.")
        at = args.at
        if not at:
            at = now.strftime("%H:%M")
            print("WARNING: no --at, so the ruling carries the clock's time %s." % at)
        elif not re.fullmatch(r"\d\d:\d\d", at):
            print("WARNING: --at %r is not HH:MM. It is written as given." % at)
        day = args.date or now.strftime("%Y-%m-%d")
        if args.date and not re.fullmatch(r"\d{4}-\d\d-\d\d", args.date):
            print("WARNING: --date %r is not YYYY-MM-DD. It is written as given."
                  % args.date)
        body = ruling_body(args.ruling, at, day, workflow)
    if not body:
        print("the body is empty, so no line was written.", file=sys.stderr)
        return 2
    force = None
    if args.force_close is not None:
        force = one_line(args.force_close)
        if not force:
            print("--force-close needs a reason, so no line was written.",
                  file=sys.stderr)
            return 2
    if args.ruling is None:
        bare = [r.rstrip("\r") for r in text.split("\n")]
        found = [f for f in state.parse(bare, bounded=False)
                 if f.number == str(args.frame)]
        refusal = gate(args.frame, found[0].lines, body, force) if found else ""
        if refusal:
            print(refusal, file=sys.stderr)
            return 2
    if force is not None:
        body += " (forced: %s)" % force

    name = peer_name(stack, sid)
    if not name:
        name = sid
        print("WARNING: no enrolment names session %s, so the line carries the "
              "session id." % sid)
    line = "- Status %s (%s): %s" % (when, name, body)
    try:
        new, index = insert(text, args.frame, line)
    except KeyError:
        print("the stack holds no frame %s, so no line was written." % args.frame,
              file=sys.stderr)
        return 2
    with open(stack, "wb") as fh:
        fh.write(new.encode("utf-8"))
    print("frame %s, line %d: - Status %s (%s)" % (args.frame, index + 1, when, name))
    if args.no_commit:
        return 0
    return commit(stack, args.frame, body, when, sid)


if __name__ == "__main__":
    sys.exit(main())
