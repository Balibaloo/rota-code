r"""
Append one status line to a frame of the stack, and commit the stack alone.

    python -m rota.tools.status 287 --sid 21800a2b --body line.txt
    python -m rota.tools.status 287 --sid 21800a2b --text "pass 1 landed"
    python -m rota.tools.status 287 --sid 21800a2b --ruling "his words" --at 02:35
    python -m rota.tools.status 287 --sid 21800a2b --put-down "the reason"

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

The tool refuses a time that is not from the clock and a frame that the
stack does not hold. It refuses nothing else. The `- Reach:` line of rule
C76 is read by `state`, and the session applies the rule. "No don't make
it a hard rule, the model should be smart enough to do it" (ruled: Roman,
2026-10-26 about 22:5x). So no pass line and no close is refused for its
Reach line.

`--put-down` writes a last status line with the reason, moves the frame's
block to `plans/archive/stack-<today>.md`, writes one line under
`## Put down` at the end of the stack, and commits the two files. A
session can put a frame down by itself, with one written reason in one
place that Roman reads, and he can pick the frame up again (ruled: Roman,
2026-11-10 08:17). The tool refuses an empty reason only. A frame that
another session holds, or that a debt of the suite names, gets one
warning line, and the put-down continues.

Exit codes: 0 the line is written and committed, or written with
`--no-commit`; 1 the line is written and the commit failed, or a write of
a put-down failed; 2 a usage error, an empty reason or a frame that the
stack does not hold.
"""
from __future__ import annotations

import argparse
import importlib
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rota.paths import REPO
from rota.tools import handover, state


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


PUT_DOWN_HEAD = ("One line for each frame that a session put down, with its reason. "
                 "Roman can pick any frame up again.")
ROMAN_TAG = re.compile(r"\s*\(Roman\)")
#: The suite's readers of `state.open_frames`, each with the test that reads
#: it. The test goes red when a debt names a frame that the stack no longer
#: holds (fact F33 of `plans/rootfix-audit-2026-10-27-b.md`). A project that
#: adopts rota has no such module, and the check passes over it.
READERS = (("tests.rota.test_f33_debts_name_open_frames",
            "test_each_debt_names_an_open_frame"),)
#: The stack that the readers read. The path is compared before the import,
#: because the import costs about a second on every run (observed:
#: `plans/f363-putdown-review-p1.md`, finding 3). Tests replace it. The path
#: comes from the one anchor, `rota/paths.py`, because no other module asks
#: where it is (`tests/rota/test_viewer.py`).
REPO_STACK = REPO / "plans" / "stack.md"


def cut_block(text: str, frame: str) -> tuple[str, list[str], state.Frame]:
    """Take the frame's block out of the text.

    Return the text, the block's lines with no line end, and the frame. The
    block runs from the heading to the line before the next heading, as
    `state.parse` reads it with `bounded` false.
    """
    raw = text.split("\n")
    bare = [r.rstrip("\r") for r in raw]
    found = [f for f in state.parse(bare, bounded=False) if f.number == str(frame)]
    if not found:
        raise KeyError(frame)
    f = found[0]
    end = f.end
    # The empty part after the last line end is not a line of the block.
    # It stays, so the file keeps its last line end.
    if end == len(raw) and raw[-1] == "":
        end -= 1
    block = bare[f.start:end]
    del raw[f.start:end]
    return "\n".join(raw), block, f


def add_put_down_line(text: str, line: str) -> str:
    """Write the line first in the stack's `## Put down` section.

    The section stands at the end of the file. A stack with no section gets
    one, with its sentence. The file's own line end is kept.
    """
    cr = "\r" if "\r\n" in text else ""
    raw = text.split("\n")
    bare = [r.rstrip("\r") for r in raw]
    heads = [i for i, b in enumerate(bare) if b.rstrip() == state.PUT_DOWN_SECTION]
    if not heads:
        if raw and raw[-1] == "":
            raw.pop()
        elif raw:
            raw[-1] += cr
        if raw and raw[-1].strip():
            raw.append(cr)
        raw += [state.PUT_DOWN_SECTION + cr, cr, PUT_DOWN_HEAD + cr, cr, line + cr, ""]
        return "\n".join(raw)
    h = heads[-1]
    end = next((i for i in range(h + 1, len(bare)) if bare[i].startswith("#")),
               len(bare))
    bullets = [i for i in range(h + 1, end) if bare[i].startswith("- ")]
    if bullets:
        raw.insert(bullets[0], line + cr)
    else:
        last = max(i for i in range(h, end) if bare[i].strip())
        raw[last + 1:last + 1] = [cr, line + cr]
    return "\n".join(raw)


def _without_put_down(lines: list[str]) -> list[str]:
    """The lines with no put-down status line and no blank line at the end."""
    kept = [x for x in lines if not ((m := state.STATUS.match(x))
                                     and m.group(3).startswith(state.PUT_DOWN))]
    while kept and not kept[-1].strip():
        kept.pop()
    return kept


def archived(path: Path, block: list[str]) -> bool:
    """The archive file holds the block already, from a run whose stack write failed.

    The put-down line of the earlier run has another time, so the compare
    leaves the put-down lines out. A second copy of a block made a rerun
    archive the frame twice (observed: `plans/f363-putdown-review-p1.md`,
    finding 5).
    """
    if not path.is_file():
        return False
    want = _without_put_down(block)
    number = state.HEAD.match(want[0]).group(1) if want else ""
    return any(f.number == number and _without_put_down(f.lines) == want
               for f in state.parse(state.read_lines(path), bounded=False))


def append_block(path: Path, block: list[str], day: str, eol: str) -> None:
    """Append the block to the archive file, and create the file with its head.

    An archive file that exists keeps its own line end and its own bytes.
    The file opens to append, so a kill during the write cannot cut off
    the blocks of earlier put-downs (observed: the review of frame 363,
    finding 8).
    """
    if path.is_file():
        old = path.read_bytes().decode("utf-8")
        if old:
            eol = "\r\n" if "\r\n" in old else "\n"
        start = old
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        old = ""
        start = "# Frames popped on %s%s" % (day, eol)
    lines = list(block)
    while lines and not lines[-1].strip():
        lines.pop()
    if start and not start.endswith(eol):
        start += eol
    if start and not start.endswith(eol * 2):
        start += eol
    with open(path, "ab") as fh:
        fh.write((start[len(old):] + eol.join(lines) + eol).encode("utf-8"))


def suite_reds(stack: Path, frame: str) -> list[str]:
    """One warning for each reader of the suite that the put-down turns red.

    A reader counts only when it reads this stack, so a put-down on another
    stack turns no test red. A reader that fails gives a warning, because
    the tool refuses nothing for a warning (ruled: Roman, 2026-10-18 02:25).
    """
    out: list[str] = []
    if not str(frame).isdigit() or stack.resolve() != Path(REPO_STACK).resolve():
        return out
    for module, test in READERS:
        where = "%s.py::%s" % (module.replace(".", "/"), test)
        try:
            reader = importlib.import_module(module)
        except Exception as exc:
            out.append("WARNING: the reader %s does not import (%r), so the debts "
                       "that name frame %s are not known." % (where, exc, frame))
            continue
        try:
            if Path(reader.STACK).resolve() != stack.resolve():
                continue
            found = reader.debts()
            held = state.open_frames(stack)
            ceiling = getattr(reader, "FRAMELESS_CEILING", frozenset())

            def reds(open_: set[int]) -> set[str]:
                return {n for names in reader.faults(found, open_).values()
                        for n in names if n not in ceiling}

            new = sorted(reds(held - {int(frame)}) - reds(held))
        except Exception as exc:
            out.append("WARNING: the reader %s did not run (%s), so the debts "
                       "that name frame %s are not known." % (where, exc, frame))
            continue
        if new:
            out.append("WARNING: %s reads state.open_frames, and it turns red on "
                       "%d debts that name frame %s: %s." % (
                           where, len(new), frame, "; ".join(new)))
    return out


def put_down_title(frame: state.Frame) -> str:
    """The heading with no session ids and no `(Roman)` tag. The push date stays."""
    return ROMAN_TAG.sub("", state.HOLDERS.sub("", frame.heading)).strip()


def name_of(stack: Path, sid: str) -> str:
    name = peer_name(stack, sid)
    if not name:
        print("WARNING: no enrolment names session %s, so the line carries the "
              "session id." % sid)
    return name or sid


def put_down(stack: Path, frame: str, sid: str, reason: str,
             now: datetime, no_commit: bool) -> int:
    """Write the last status line, move the block to the archive, and record it."""
    reason = one_line(reason)
    if not reason:
        print("the reason is empty, so nothing was put down.", file=sys.stderr)
        return 2
    when = now.strftime("%Y-%m-%d %H:%M")
    day = now.strftime("%Y-%m-%d")
    name = name_of(stack, sid)
    # The check of the debts takes seconds, so it runs before the read. A read
    # before it lost a status line that another session wrote in the gap
    # (observed: `plans/f363-putdown-review-p1.md`, finding 2).
    warnings = suite_reds(stack, frame)
    text = stack.read_bytes().decode("utf-8")
    try:
        marked, _ = insert(text, frame, "- Status %s (%s): %s %s: %s" % (
            when, name, state.PUT_DOWN, sid, reason))
    except KeyError:
        print("the stack holds no frame %s, so nothing was put down." % frame,
              file=sys.stderr)
        return 2
    left, block, f = cut_block(marked, frame)
    if f.holder and f.holder != sid:
        print("WARNING: session %s holds frame %s, and session %s puts it down."
              % (f.holder, frame, sid))
    for warning in warnings:
        print(warning)
    archive = stack.parent / "archive" / ("stack-%s.md" % day)
    rel = "%s/archive/%s" % (stack.resolve().parent.name, archive.name)
    # The title is cut and the reason is not, because the reason is what
    # Roman reads (observed: the review of frame 363, finding 4).
    stop = "" if reason.endswith((".", "?", "!")) else "."
    row = "- %s. %s Put down %s (%s): %s%s Block: %s." % (
        f.number, state.cut(put_down_title(f), state.NAME_LIMIT), when, name,
        reason, stop, rel)
    new = add_put_down_line(left, row)
    # The archive is written first. A failure between the two writes then
    # leaves the block in both files, and never in neither. A rerun finds the
    # block in the archive and does not append it again.
    try:
        if archived(archive, block):
            print("the archive %s holds the block of frame %s already, from an "
                  "earlier run, so it is not appended again." % (rel, frame))
        else:
            append_block(archive, block, day, "\r\n" if "\r\n" in text else "\n")
    except OSError as exc:
        print("the archive write failed (%s). The stack is unchanged and holds "
              "frame %s. Check %s for a part of the block." % (exc, frame, rel),
              file=sys.stderr)
        return 1
    try:
        with open(stack, "wb") as fh:
            fh.write(new.encode("utf-8"))
    except OSError as exc:
        print("the stack write failed (%s). The block of frame %s is in %s, and "
              "the frame is still in the stack. Run the put-down again: it does "
              "not archive the block twice." % (exc, frame, rel), file=sys.stderr)
        return 1
    print("frame %s put down: the block is in %s" % (frame, rel))
    if no_commit:
        return 0
    prose = ("The status tool puts frame %s down at %s for session %s. The block "
             "moves to %s, and one line under %s gives the reason."
             % (frame, when, sid, rel, state.PUT_DOWN_SECTION))
    return commit(stack, frame, "put down, " + reason, when, sid,
                  also=[archive], prose=prose,
                  failed="the put-down is written and the commit failed. The commit "
                         "takes the archive file of the day whole. Run: ")


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


def commit(stack: Path, frame: str, body: str, when: str, sid: str,
           also: list[Path] | None = None, prose: str = "", failed: str = "") -> int:
    """Commit the stack and the `also` files by pathspec, so nothing else staged goes in.

    With `failed`, a failed commit prints that text and the exact command
    that commits the same paths, so the session can run it.
    """
    repo = stack.resolve().parent
    paths = [str(p.resolve()) for p in [stack] + list(also or [])]
    git(repo, "add", "--", *paths)
    prose = prose or ("The status tool appends one line to frame %s at %s for "
                      "session %s." % (frame, when, sid))
    done = git(repo, "commit", "-m", summary(frame, body), "-m", prose,
               "--", *paths)
    if done.returncode != 0 and failed:
        print(failed + shlex.join(
            ["git", "-C", repo.as_posix(), "commit", "-m", summary(frame, body),
             "-m", prose, "--"] + [Path(p).as_posix() for p in paths]),
            file=sys.stderr)
    elif done.returncode != 0:
        print("the line is written and the commit failed:", file=sys.stderr)
    if done.returncode != 0:
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
    src.add_argument("--put-down", dest="put_down",
                     help="the reason: write it, move the frame's block to the "
                          "archive and record it under ## Put down")
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
    now = _clock()
    if args.put_down is not None:
        return put_down(stack, args.frame, sid, args.put_down, now, args.no_commit)
    text = stack.read_bytes().decode("utf-8")
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

    name = name_of(stack, sid)
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
