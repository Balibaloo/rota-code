"""
Running the tests. The one gate in the system with no judgement in it at all.

It is deliberately the cheapest thing in the delivery loop and deliberately
first: a test costs a subprocess, a Critic session costs a model call, and a
structural review costs a model call over source. Ordering them by cost is not
an optimisation — it is what keeps `loop_cap` bounces affordable enough to be
the normal way a batch converges.

Nothing here interprets. The test said what it said; recording that through a
model would introduce a paraphrase risk over a boolean.
"""
from __future__ import annotations

import re
import shlex
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

from .. import paths
from . import lifecycle
from .runner import new_id

# pytest's contract, and the reason the three-way result exists: a test that
# fails is information about the code, a test that errors is usually information
# about the test.
EXIT_OK, EXIT_FAILED = 0, 1

# The pytest plugin that reports an exception a `CliRunner` caught (frame
# 195). Its directory holds plugins alone, because the whole directory goes
# on the child's `PYTHONPATH`. No file goes into the worktree, so no diff or
# commit can carry the plugin.
PLUGIN = "_rota_caught"
PLUGIN_DIR = paths.PACKAGE / "core" / "plugins"


def plugin_env() -> dict[str, str]:
    """The child's `PYTHONPATH`, with the plugin directory first."""
    import os

    rest = os.environ.get("PYTHONPATH", "")
    return {"PYTHONPATH": os.pathsep.join(
        [str(PLUGIN_DIR)] + ([rest] if rest else []))}


def tests_for(conn: sqlite3.Connection, batch_id: str) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT id, path, body, criterion_id FROM tests WHERE batch_id = ? ORDER BY id",
        (batch_id,))]


def live_tests_for(conn: sqlite3.Connection, batch_id: str) -> list[dict]:
    """The batch's tests less those of a retired criterion. The run skips
    them, so their old red sets no colour on the batch (frame 306, pass 2b).
    The tests and their runs stay in the table."""
    from .scheduler import live_tests

    return [dict(r) for r in conn.execute(
        "SELECT id, path, body, criterion_id FROM tests WHERE batch_id = ?"
        + live_tests(conn, "id") + " ORDER BY id", (batch_id,))]


def tester_paths(conn: sqlite3.Connection, batch_id: str) -> set[str]:
    """The paths of tests that rota's Tester wrote for a merged batch.

    Frame 207, night 140: bg_1's Tester test merged, and bg_2 inherited it
    with no criterion. The harness then dropped the warning filter, and the
    project's `filterwarnings = error` turned the test red. A test keeps
    the filter of the batch that wrote it.
    """
    return {r["path"].replace("\\", "/") for r in conn.execute(
        "SELECT DISTINCT t.path FROM tests t JOIN batches b ON b.id = t.batch_id "
        "WHERE (t.criterion_id IS NOT NULL OR t.commitment_id IS NOT NULL) "
        "AND t.batch_id != ? "
        "AND b.status = 'merged'", (batch_id,))}


def _own(t: dict, tester: set[str]) -> bool:
    """True when the test runs under the batch's filter, not the project's."""
    return bool(t.get("criterion_id")) or t["path"].replace("\\", "/") in tester


def worktree_of(conn: sqlite3.Connection, batch_id: str) -> str | None:
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return row["worktree"] if row else None


def materialise(worktree: Path, tests: list[dict]) -> list[Path]:
    """
    Write each test to its declared path.

    Tester owns the test *bodies*; the worktree is Developer's. Writing them out
    at run time rather than committing them keeps that ownership intact — the
    tests are not part of the diff under review, which is what stops a batch
    from passing by editing its own criteria.
    """
    written = []
    for t in tests:
        target = worktree / t["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(t["body"], encoding="utf-8")
        written.append(target)
    return written


def run(conn: sqlite3.Connection, batch_id: str,
        *, timeout: int = 120) -> list[tuple[str, str]]:
    """
    Run every test for one batch, record each result, return them.

    A batch with no worktree runs nothing and records nothing — that is a batch
    that has not started, not a batch whose tests all pass, and the difference
    matters to every predicate downstream.
    """
    tests = live_tests_for(conn, batch_id)
    if not tests:
        return []
    worktree = worktree_of(conn, batch_id)
    if not worktree or not Path(worktree).is_dir():
        # Could not run is a result, and it is recorded as one. This returned
        # [] -- "a batch that has not started, not a batch whose tests all
        # pass" -- which is the right distinction with the wrong consequence:
        # the harness predicate fires on "this commit has no test_runs row",
        # so a batch with tests and no worktree was re-offered every pass,
        # forever. Measured live on cnt_v2r: forty harness actions printing
        # "0 test(s)" while a 91-row ruling sat undispatched behind them.
        #
        # An error row per test is the drain the predicate already declares
        # -- drains=[("test_runs", "result", "error")] -- and it flows into
        # `tests_failing`, where a Developer is woken to a batch whose state
        # says exactly what is wrong.
        head = lifecycle.head_of(conn, batch_id)
        attempt = lifecycle.next_attempt(conn, batch_id)
        said = (f"the batch has no worktree at {worktree!r}; nothing can run. "
                f"The tests exist and were not attempted")
        results = [(t["id"], "error") for t in tests]
        for test_id, result in results:
            lifecycle.record_test_run(conn, new_id("tr", conn), batch_id,
                                      test_id, result, attempt,
                                      commit_sha=head, output=said)
        # No code ran, so the red did not move. The key keeps its count.
        return results

    root = Path(worktree)
    materialise(root, tests)
    attempt = lifecycle.next_attempt(conn, batch_id)

    from . import config as _config

    runner = _config.get(conn, "runner")
    results: list[tuple[str, str]] = []
    output: dict[str, str] = {}
    tester = tester_paths(conn, batch_id)
    for t in tests:
        verdict, said = _run_one(root, t["path"], timeout, runner=runner,
                                 own=_own(t, tester))
        results.append((t["id"], verdict))
        output[t["id"]] = said

    head = lifecycle.head_of(conn, batch_id)
    # The red before this run: the run at this head when one exists, so a
    # re-run at one head compares with itself (frame 318, review 1).
    from .db import lift_on_red_move, red_before

    before = red_before(conn, batch_id)
    # A run at this head already exists, so a new red is a new test, not a
    # new commit (frame 318, pass 3b). A no-worktree error row ran no code,
    # so it is no run at this head (review 3, low). Fact F4 leaves this read
    # on `test_runs`: it asks whether any run at this head exists, not which
    # run is the newest.
    from .db import NO_WORKTREE

    same_head = conn.execute(
        "SELECT 1 FROM test_runs WHERE batch_id = ? AND commit_sha IS ? "
        "AND output NOT LIKE ?", (batch_id, head, f"{NO_WORKTREE}%")).fetchone() is not None
    # A run supersedes the run before it at the same commit: the tests may
    # have changed under it (walk eighteen), and the `review` gate reads
    # "no non-pass run at this commit", which stale fail rows kept false
    # forever after the tests went green.
    conn.execute("DELETE FROM test_runs WHERE batch_id = ? AND commit_sha = ?",
                 (batch_id, head))
    for test_id, result in results:
        lifecycle.record_test_run(conn, new_id("tr", conn), batch_id, test_id,
                                  result, attempt, commit_sha=head,
                                  output=output.get(test_id, ""))
    lift_on_red_move(conn, batch_id, head, before, same_head)
    return results


_E_LINE = re.compile(r"E\s+\S")
_E_FRAME = re.compile(r'E\s+File ".*", line \d+')
_NATIVE_FRAME = re.compile(r'\s+File ".*", line \d+')
# pytest's `-q` progress line. A one-test file that errors in a fixture
# prints `E` and `[100%]` (review 1 of F5, finding 1).
_PROGRESS = re.compile(r"[.EFsxXp]+\s+\[\s*\d+%\]\s*")
# The header above one test's traceback, or above a collection error.
_SECTION_HEAD = re.compile(r"_{3,} \S.*? _{3,}$")
# pytest puts this mark before each line of a crash of its own.
_INTERNAL = "INTERNALERROR> "
# The texts that join two tracebacks of one chained raise.
_CHAIN_MARKS = (
    "During handling of the above exception, another exception occurred:",
    "The above exception was the direct cause of the following exception:")


class ErrorAt(NamedTuple):
    """Where a red run says what raised: `line` is the last raise, and
    `cause` is the first raise of a chain, else None."""
    line: int | None
    cause: int | None


def _marked_error(lines: list[str], lo: int, hi: int, block: bool) -> int | None:
    """The `E` line in lines[lo:hi] that says what raised, or None."""
    first = next((i for i in range(lo, hi) if _E_LINE.match(lines[i])
                  and not _PROGRESS.fullmatch(lines[i])), None)
    # Frame 336: a collection error puts the frame first and the error
    # last. Night 168's m53 showed only the file and the line.
    if first is not None and (block or _E_FRAME.match(lines[first])):
        while first + 1 < hi and _E_LINE.match(lines[first + 1]):
            first += 1
    return first


def _native_error(lines: list[str], lo: int, hi: int, block: bool) -> int | None:
    """The exception line after the first native frame in lines[lo:hi]."""
    frame = next((i for i in range(lo, hi) if _NATIVE_FRAME.match(lines[i])), None)
    if frame is None:
        return None
    return next((i for i in range(frame + 1, hi)
                 if lines[i].strip() and not lines[i][0].isspace()), None)


def _chain_error(lines: list[str], lo: int, hi: int, find, block: bool) -> ErrorAt:
    """The last raise and the cause of the one block lines[lo:hi]."""
    cuts = [i for i in range(lo, hi) if any(m in lines[i] for m in _CHAIN_MARKS)]
    found = [at for a, b in zip([lo] + [c + 1 for c in cuts], cuts + [hi])
             if (at := find(lines, a, b, block)) is not None]
    if not found:
        return ErrorAt(None, None)
    return ErrorAt(found[-1], found[0] if len(found) > 1 else None)


def error_at(lines: list[str]) -> ErrorAt:
    """Where a red run says what raised, as indexes into `lines`.

    1. The block. The first test section that holds an error, between two
       `___ name ___` headers. The whole run when it has no header.
    2. The raise. The last section of a chained raise in that block gives
       `line`, and the first section gives `cause`.
    3. pytest's form, in one section. The first `E` line that is not the
       progress line. The last line of that `E` block when the block starts
       with a frame or the run has an `ERROR collecting` line.
    4. The native form, when the run has no `E` line. The first line that
       is not indented after the first `File "...", line N` frame. An
       `INTERNALERROR> ` mark does not count.
    """
    # Fact F5: this is the one reader of the error line. Rule C76 puts
    # every reader at one rule. Fourteen readers used four rules before.
    # The last raise names the seat's own mistake in 175 of 179 recorded
    # chained runs, and frame 328, item 4, rules the same. Frame 317's
    # Tester still needs the cause, so the cause comes too.
    view = [ln[len(_INTERNAL):] if ln.startswith(_INTERNAL) else ln for ln in lines]
    block = any("ERROR collecting" in ln for ln in view)
    heads = [i for i, ln in enumerate(view) if _SECTION_HEAD.match(ln)]
    bounds = list(zip([0] + heads, heads + [len(view)]))
    for find in (_marked_error, _native_error):
        for lo, hi in bounds:
            got = _chain_error(view, lo, hi, find, block)
            if got.line is not None:
                return got
    return ErrorAt(None, None)


def _text(line: str) -> str:
    """One error line without pytest's `E` or the INTERNALERROR mark."""
    line = line[len(_INTERNAL):] if line.startswith(_INTERNAL) else line
    return (line[1:] if _E_LINE.match(line) else line).strip()


def error_line(output: str | None) -> str:
    """The line of a red run that says what raised, the last raise of a
    chain, without its marker. "" when no line says it."""
    lines = (output or "").splitlines()
    at = error_at(lines).line
    return "" if at is None else _text(lines[at])


def error_cause(output: str | None) -> str:
    """The first raise of a chained red run, without its marker. "" when
    the run holds no chain."""
    lines = (output or "").splitlines()
    at = error_at(lines).cause
    return "" if at is None else _text(lines[at])


def _tail(text: str, size: int = 2000) -> str:
    """
    The last `size` characters from a line start, led by the run's error
    line and its cause when the cut changes what `error_at` reads.
    """
    # Frame 318, review 1 finding 2: the red's identity is the error line.
    # A cut mid-output gave a later line or half a line instead.
    if len(text) <= size:
        return text.strip()
    cut = text.rfind("\n", 0, len(text) - size) + 1
    tail = text[cut:].strip()
    lines = text.splitlines()
    at = error_at(lines)
    if at.line is None or ((error_line(tail), error_cause(tail))
                           == (error_line(text), error_cause(text))):
        return tail
    keep = []
    if at.cause is not None:
        keep += _raise_lines(lines, at.cause) + [_CHAIN_MARKS[0]]
    # A strip of the whole would take a native frame's indent.
    return "\n".join(keep + _raise_lines(lines, at.line) + [tail])


def _raise_lines(lines: list[str], at: int) -> list[str]:
    """The error line at `at`, led by its frame in the native form."""
    if _E_LINE.match(lines[at]):
        return [lines[at]]
    view = [ln[len(_INTERNAL):] if ln.startswith(_INTERNAL) else ln for ln in lines]
    start = next((i for i in range(at, -1, -1) if _NATIVE_FRAME.match(view[i])), at)
    return view[start:at + 1]


def _run_one(root: Path, path: str, timeout: int,
             runner: str | None = None, own: bool = False) -> tuple[str, str]:
    """
    One test file: one word, and what the harness actually said.

    The word alone was all that was kept, and it left the Developer in
    `tests_failing` reading the test *body* and guessing what red looked like —
    the assertion that fired, the value it got, the traceback. Two L1 cases
    turned on exactly that judgement and produced precisely swapped answers,
    because from a criterion and a test body there is nothing to tell "the code
    is wrong" from "the test is wrong".

    Every non-pass outcome that is not an ordinary failure — a timeout, a
    collection error, an interpreter that would not start — is `error` rather
    than `fail`. They are different things to a Developer: `fail` says the code
    is wrong, `error` says the test could not answer.
    """
    # `sys.executable`, not "python". The first version used the latter and every
    # test came back `fail` — the interpreter on PATH had no pytest, so the exit
    # code was 1 and 1 means "tests failed". A missing harness reporting as a red
    # test suite is the worst available failure: it looks like the Developer's
    # problem and it is not.
    try:
        # The worktree's own interpreter when it has one. `sys.executable` was
        # rota's own, with rota's own packages, so a project that imported
        # anything else could not be tested and nothing said why.
        from . import execute
        from .provision import python_for
        out = execute.run(
            root, [python_for(root), "-m", "pytest", shlex.quote(path), "-q", "--no-header",
                   # ruling: DECISIONS 943, a harness fact is the door's, not a desk's
                   # The batch's own tests test criteria, not the project's
                   # warning hygiene. Click night 55 (2026-09-14): the
                   # project's `filterwarnings = error` turned a
                   # DeprecationWarning inside the Tester's own test into
                   # five red tests nobody could fix. The project's tests
                   # keep the project's rules.
                   *(["-W", "ignore::DeprecationWarning"] if own else []),
                   # Night 138 (frame 195): click's `CliRunner` caught a
                   # `NameError` and the red row showed the assertion alone.
                   # The plugin adds a section with the caught exception. A
                   # project's `--show-capture=no` or `--tb=no` hides every
                   # section, and the command line wins over `addopts`.
                   # pytest's default is already `auto`, so no recorded
                   # output changes. The plugin loads on the project's tests
                   # and the batch's own alike.
                   "-p", PLUGIN, "--show-capture=all", "--tb=auto"],
            timeout=timeout, runner=runner, env=plugin_env())
    except KeyError as exc:
        return "error", str(exc)
    if out.error:
        return "error", out.error

    # Tail rather than head: pytest puts the summary and the failing assertion
    # at the end, and the beginning is collection chatter.
    said = _tail(out.stdout or out.stderr or "")
    if out.returncode == EXIT_OK:
        return "pass", said
    if out.returncode == EXIT_FAILED and "No module named pytest" not in out.stderr:
        return "fail", said
    return "error", said


def inherited_id(rel: str) -> str:
    """The id `inherit` gives the project's test at `rel`, a posix path.

    `tests.encode` reads the same id to tell a project row from a Tester's
    row (frame 135). One function keeps the two from drifting apart.
    """
    import hashlib

    return "inh_" + hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]


def project_tests(conn: sqlite3.Connection, worktree: Path) -> list[str]:
    """The test files of the tree, posix paths relative to `worktree`, sorted."""
    # F9 (ruled: Roman, 2026-10-26 20:37): the basename gives the shape of a
    # test file, and the frame's kind says whether the file is part of the
    # program. A glob under `tests/` decided both before.
    import os

    from ..roles.api import _is_test_file

    out = []
    for top, dirs, files in os.walk(worktree):
        # The worktree itself lives under `.rota/`, so the walk prunes by the
        # relative parts, not the full path's.
        dirs[:] = [d for d in dirs if d not in (".rota", ".venv", ".git")]
        for name in files:
            rel = Path(top, name).relative_to(worktree).as_posix()
            # A conftest is a test file, but pytest collects no test from
            # it. The harness runs each inherited file, and a run with no
            # test is an error.
            if _is_test_file(conn, rel) and name != "conftest.py":
                out.append(rel)
    return sorted(out)


def inherit(conn: sqlite3.Connection, batch_id: str, worktree: Path) -> list[str]:
    """
    The repository's own tests join the batch, with no criterion.

    A merge must not break what the tree already proved. tipsY (2026-09-09):
    the batch's tests were green and the Critic passed, and the merged
    program read the tip percentage and ignored it, because the repo's own
    tip test never ran. The harness runs every test of the batch, so the
    existing tests become tests of the batch at start. Their bodies are the
    files as found, and `materialise` writes the same bytes back.
    """
    owned = {t["path"].replace("\\", "/") for t in tests_for(conn, batch_id)}
    found: list[str] = []
    for rel in project_tests(conn, worktree):
        if rel in owned:
            continue
        f = worktree / rel
        tid = inherited_id(rel)
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        conn.execute(
            "INSERT OR REPLACE INTO tests (id, batch_id, criterion_id, path, body) "
            "VALUES (?, ?, NULL, ?, ?)", (tid, batch_id, rel, body))
        found.append(rel)
    # The base run needs the tree as the batch found it. A resumed batch
    # holds its own commits, so it keeps the record of its first start.
    if (found and base_run(conn, batch_id) is None
            and not lifecycle.head_of(conn, batch_id)):
        record_base_run(conn, batch_id, worktree,
                        [inherited_id(rel) for rel in found])
    return found


def base_red_ids(conn: sqlite3.Connection, batch_id: str) -> set[str]:
    """The inherited tests of the batch that its base run records red."""
    base = base_run(conn, batch_id) or {}
    return {r["id"] for r in conn.execute(
        "SELECT id FROM tests WHERE batch_id = ? AND criterion_id IS NULL",
        (batch_id,))
        if (base.get(r["id"]) or {}).get("result", "pass") != "pass"}


def reds_that_hold(conn: sqlite3.Connection, batch_id: str, commit: str,
                   where: str = "") -> list[str]:
    """The test ids red at `commit` that hold the review and merge gates.

    `where` adds an SQL condition on `test_id`. The review predicate and
    `lifecycle.mergeable` both ask this one function, so they never drift.
    """
    # Frame 362, pass 5b (review high 1): 5 icalendar files are red at the
    # base. The tree never proved them, so the batch did not break them.
    # A Tester's test, and an inherited test with no red base record, hold.
    excused = base_red_ids(conn, batch_id)
    return [r["test_id"] for r in conn.execute(
        "SELECT test_id FROM latest_runs WHERE batch_id = ? AND commit_sha = ? "
        "AND result != 'pass'" + where, (batch_id, commit))
        if r["test_id"] not in excused]


def _base_key(batch_id: str) -> str:
    return f"base_run:{batch_id}"


def base_run(conn: sqlite3.Connection, batch_id: str) -> dict | None:
    """The recorded base run of the batch's inherited tests, or None.

    The value maps a test id to its result, and a red result to its output.
    """
    import json

    row = conn.execute("SELECT value FROM config WHERE key = ?",
                       (_base_key(batch_id),)).fetchone()
    if row is None:
        return None
    try:
        data = json.loads(row["value"])
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def record_base_run(conn: sqlite3.Connection, batch_id: str, worktree: Path,
                    test_ids: list[str], *, timeout: int = 120) -> dict:
    """
    Run the inherited tests once at the batch's base, and record the result.

    Frame 207, night 140: three doors said "it passed before this batch"
    from a constant, and the test was red at bg_2's base. A door now says
    that sentence only from this record. Each test runs under the filter
    the batch's own run gives it, so the base run and the batch's runs agree.

    One pytest call runs each filter group. A green group costs one child.
    A red group runs again file by file, so each red row has its own output.
    """
    import json

    from . import config as _config
    from . import execute
    from .provision import python_for

    wanted = set(test_ids)
    tests = [t for t in tests_for(conn, batch_id) if t["id"] in wanted]
    tester = tester_paths(conn, batch_id)
    runner = _config.get(conn, "runner")
    root = Path(worktree)
    record: dict[str, dict] = {}
    for own in (True, False):
        group = [t for t in tests if _own(t, tester) == own]
        if not group:
            continue
        try:
            out = execute.run(
                root, [python_for(root), "-m", "pytest",
                       *[shlex.quote(t["path"]) for t in group],
                       "-q", "--no-header",
                       *(["-W", "ignore::DeprecationWarning"] if own else []),
                       "-p", PLUGIN],
                timeout=timeout * len(group), runner=runner, env=plugin_env())
            green = not out.error and out.returncode == EXIT_OK
        except KeyError:
            green = False
        if green:
            for t in group:
                record[t["id"]] = {"result": "pass"}
            continue
        for t in group:
            verdict, said = _run_one(root, t["path"], timeout, runner=runner,
                                     own=own)
            record[t["id"]] = ({"result": verdict} if verdict == "pass"
                               else {"result": verdict, "output": said})
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                 (_base_key(batch_id), json.dumps(record, sort_keys=True)))
    return record
