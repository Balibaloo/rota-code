"""
The suite in five lines, with a traceback for a new red only.

    python -m rota.tools.gate              # compare this run against the baseline
    python -m rota.tools.gate --baseline   # store this run as the baseline
    python -m rota.tools.gate --no-rerecord  # leave the stale cases stale

A stale case is re-recorded after the run, one case at a time, and the gate
prints one `rerecorded` line per case before the five lines. When a model is
loaded on the main card, the re-records wait, and the run exits 3.
`--rerecord-now` re-records anyway.

Twelve suite runs inside agents cost about 25k tokens each. Every agent read the
tracebacks of the same 22 known reds, and one FAILED-list compare still missed a
stale case (observed: `plans/archive/postmortem-frame21-2026-09-16.md`). The
gate sends the child's output to `.rota-gate.log` and prints what moved.

One run reads three sources. The summary line gives the counts. Pytest's own
`lastfailed` cache gives the red node ids. `casestatus.status` gives the stale
case ids. The red ids come from the cache because eight node ids in this suite
hold a space, and a regex over the `FAILED` lines drops them.

Every external call is a module-level function, so a test replaces it with
`monkeypatch`. No test starts pytest and no test opens the cassette database.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from rota.llm import llm

#: The temp root for the child. The value takes the Windows form `C:/...`,
#: because a Git Bash form `/c/...` resolves to `C:\c\...` (observed: the
#: design review of 2026-09-17, finding 7). The suite spends three quarters of
#: its time on fixture IO, so this path belongs on the SSD.
TEMP_ROOT = Path(os.environ.get("ROTA_GATE_TMP", "C:/Users/roman/rota_gate/tmp"))

#: Never `DEFAULT_MODEL` from `rota.llm.llm`: its fallback is `llama3.1:8b`,
#: and under llama `casestatus.status` calls 62 qwen-green cases stale.
FALLBACK_MODEL = "qwen3:8b"

#: Any of these four turns a replay into a recording run, or moves the pins
#: (observed: `rota_serial_plugin.py`, `tests/rota/test_l1.py:129`).
RECORDING_NAMES = ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH", "ROTA_MODEL_FORCE")

#: `PYTEST_ADDOPTS` goes out with them, because it edits the run the gate
#: measures and shows in no line. `-x` truncates the run and
#: `-p no:cacheprovider` removes the red set (observed: the diff review of
#: 2026-09-17, the environment probe).
DROPPED_NAMES = RECORDING_NAMES + ("PYTEST_ADDOPTS",)

#: The one tree the gate runs. Extra pytest arguments are not passed through,
#: so every gate run measures the same thing.
SUITE = "tests/rota"

#: The exit code of a run whose stale cases wait for the main card. It is
#: not 1, because a wait is no red.
WAIT_EXIT = 3

BASELINE_NAME = ".rota-gate.json"
LOG_NAME = ".rota-gate.log"
LASTFAILED = Path(".pytest_cache") / "v" / "cache" / "lastfailed"

#: Under `-q` the final line carries no `=` padding: `3 failed, 1 passed,
#: 1 error in 22.59s`. Under a louder mode the same line has the padding.
SUMMARY = re.compile(r"^=*\s*(.*?) in ([\d.]+)s")


def repo_root() -> Path:
    """The checkout this module was imported from."""
    from .. import paths

    return paths.REPO


def child_env(model: str, temp_root: Path | None = None) -> dict[str, str]:
    """The environment for the child, with the recording switches removed."""
    root = Path(temp_root) if temp_root is not None else TEMP_ROOT
    env = dict(os.environ)
    env["ROTA_MODEL"] = model
    for name in DROPPED_NAMES:
        env.pop(name, None)
    root.mkdir(parents=True, exist_ok=True)
    # All three names change together. `tempfile.gettempdir()` reads them in
    # this order, and the git fixture's guard in `rota/testkit/gitfixture.py`
    # follows `gettempdir()` (observed: the design review, probes 3 and 4).
    for name in ("TMPDIR", "TEMP", "TMP"):
        env[name] = str(root)
    return env


def _get_json(url: str) -> dict | None:
    """The JSON body of a GET, or None when the server does not answer."""
    import http.client
    import urllib.request

    # A reply cut short raises `IncompleteRead`, which is no `OSError`
    # (observed: frame 118's diff review). The gate must reach the suite.
    try:
        with urllib.request.urlopen(url, timeout=2) as reply:
            data = json.loads(reply.read().decode("utf-8"))
    except (OSError, ValueError, http.client.HTTPException):
        return None
    return data if isinstance(data, dict) else None


def main_card_held(env: dict[str, str]) -> list[str]:
    """
    The models the children's server holds now, each with its expiry when
    given. Empty when the card is free or the server does not answer.

    A held card means a night runs there, so the re-records wait. The gate
    never moves them to the Titan: the Titan gives another temperature-0
    reply to the same prompt, so its recording is no evidence for this
    register (ruled: Roman, frame 124).
    """
    # The fallback is `llm.OLLAMA_HOST`, the one reader of the model host
    # (F29). The probe then asks the server the re-records call. A night
    # holds that server for hours (observed: frame 124's diff review).
    host = env.get("OLLAMA_HOST", llm.OLLAMA_HOST).rstrip("/")
    ps = _get_json(f"{host}/api/ps") or {}
    models = ps.get("models")
    if not isinstance(models, list):
        return []
    # Ollama keeps a model loaded for five minutes after its last call, so
    # the gate's own re-record also reads as held. The expiry tells a reader
    # which case it is (ruled: frame 118's diff review).
    return [f"{m['name']} until {m['expires_at']}" if m.get("expires_at")
            else str(m["name"])
            for m in models if isinstance(m, dict) and m.get("name")]


def _run_suite(env: dict[str, str], log: Path) -> int:
    """Run the whole tree as a child. Write the log. Return the child's code."""
    # `CI` makes pytest print each `FAILED` line whole. Without it the line is
    # cut to 80 columns, and a case node id alone fills them, so the `STALE`
    # text never reaches the log (reasoned: `_get_line_with_reprcrash_message`
    # in `_pytest/terminal.py`). No code in this repository reads `CI`.
    with log.open("w", encoding="utf-8", errors="replace", newline="") as out:
        child = subprocess.run(
            [sys.executable, "-m", "pytest", SUITE, "--tb=no", "-rfE", "-q"],
            cwd=str(repo_root()), env={**env, "CI": "1"}, stdout=out,
            stderr=subprocess.STDOUT)
    return child.returncode


def case_of(node: str) -> str | None:
    """The case id of a case node, or None for any other node."""
    for _, _, test in CASE_TESTS:
        if node.startswith(f"{test}[") and node.endswith("]"):
            return node[len(test) + 1:-1]
    return None


def stale_by_failure(text: str, failed: set[str]) -> set[str]:
    """
    The case ids whose red in the log says `STALE`.

    `casestatus.status` counts the rows a case wrote. The suite fails a case
    when one run finds no cassette. So a case can read green in `status` and
    fail `STALE` in the suite (observed: frame 89, 2026-09-29,
    `L1-DV-give-the-new-parameters-defaults`).
    """
    out = set()
    for node in failed:
        case_id = case_of(node)
        if case_id is None:
            continue
        head = f"FAILED {node} - "
        # The message must open with the tiers' own `pytest.fail` text. An
        # assertion that quotes the word would otherwise cost five live runs.
        if any(line.startswith(head)
               and line[len(head):].startswith("Failed: STALE ")
               for line in text.splitlines()):
            out.add(case_id)
    return out


def _rerun(env: dict[str, str], ids: list[str]) -> str:
    """Run the new reds again, with tracebacks. Return the child's output."""
    # `-n0` on the command line wins over the ini's `-n auto` (observed: the
    # design review, probe 9).
    child = subprocess.run(
        [sys.executable, "-m", "pytest", *ids, "--tb=short", "-q", "-n0"],
        cwd=str(repo_root()), env=env, capture_output=True, text=True,
        errors="replace")
    return (child.stdout or "") + (child.stderr or "")


def register_path() -> Path:
    """The cassette database the stale line is read from."""
    from .. import paths

    return paths.DEV_DB


def _stale(model: str) -> set[str] | None:
    """
    The case ids with no recording against the current prompt.

    None means the register is not on this machine. The check comes first and
    `casestatus.status` is never called, because `open_dev_db` creates an empty
    database from a missing file. That empty file reports 127 NEW cases, and it
    then stops `ensure_for_tests` from ever fetching the real one (observed: the
    diff review of 2026-09-17, the probe in the worktree).
    """
    if not register_path().exists():
        return None

    # Imported here, so that `import rota.tools.gate` opens no database.
    from . import casestatus

    return {row["id"] for row in casestatus.status(model)
            if row["state"] in ("STALE", "NEW")}


def _states(model: str) -> dict[str, str]:
    """Each case's state as the report prints it, for example `green 5/5`."""
    from . import casestatus

    return {row["id"]: row["state"] if row["passed"] is None
            else f"{row['state']} {row['passed']}/{row['of']}"
            for row in casestatus.status(model)}


#: Which test holds a case. An `l` case with `first` is a chain and runs in the
#: L3 tier. The gauntlet takes every `g` case, `first` or not, so its chain
#: value is None (observed: `tests/rota/test_l1.py:74`,
#: `tests/rota/test_l3.py:67`, `tests/rota/test_gauntlet.py:60`).
CASE_TESTS = (("l*.yaml", False, "tests/rota/test_l1.py::test_l1_case"),
              ("l*.yaml", True, "tests/rota/test_l3.py::test_l3_chain"),
              ("g*.yaml", None,
               "tests/rota/test_gauntlet.py::test_seat_flow_segment"))


def node_of(case_id: str) -> str | None:
    """The exact node id of the case, or None when no test holds the case."""
    from .. import paths
    from ..testkit import fixtures

    for pattern, chain, test in CASE_TESTS:
        for path in sorted(paths.CASES.glob(pattern)):
            for case in fixtures.load_case(path) or []:
                if case.get("id") != case_id:
                    continue
                if chain is None or bool(case.get("first")) == chain:
                    return f"{test}[{case_id}]"
    return None


def rerecord_argv(command: str) -> tuple[dict[str, str], list[str]]:
    """
    Split the re-earn command into its variables and its arguments.

    The command is the one line `casestatus` prints. The gate runs that line,
    so the key it records under is the key a reader sees.
    """
    words = shlex.split(command)
    names = {}
    while words and re.fullmatch(r"[A-Z_][A-Z0-9_]*=.*", words[0]):
        name, _, value = words.pop(0).partition("=")
        names[name] = value
    if words and words[0] == "python":
        words[0] = sys.executable
    return names, words


def _rerecord(env: dict[str, str], case_id: str, log: Path) -> str | None:
    """
    Re-earn one case, then run the case once more without ROTA_REFRESH.
    Append both runs to the log.

    Return the node id when the plain run passed, and None when it failed or
    no test holds the case. The caller clears that node from the red set.

    The second run carries no `ROTA_REFRESH`. A refresh run can leave run 5
    unwritten, and a plain run then records run 5 live (observed:
    `plans/operating-facts.md`, frame 92, 2026-09-29).
    """
    from ..llm.llm import DEFAULT_NUM_CTX, Pins
    from ..testkit import fixtures

    node = node_of(case_id)
    with log.open("a", encoding="utf-8", errors="replace", newline="") as out:
        if node is None:
            out.write(f"\n== rerecord {case_id}: no test holds the case\n")
            return None
        command = fixtures.rerecord_command(
            Pins(model=env["ROTA_MODEL"], num_ctx=DEFAULT_NUM_CTX),
            shlex.quote(node))
        names, argv = rerecord_argv(command)
        # `-n0` keeps one process. The cache stays off, so the red set of the
        # suite run stays in `lastfailed` for the flaky check. The exit code of
        # the plain run gives this case's red instead.
        argv += ["-n0", "-p", "no:cacheprovider"]
        code = 1
        for refresh in (True, False):
            run_env = {**env, **names}
            run = "refresh run" if refresh else "plain run"
            if refresh:
                run_env["ROTA_REFRESH"] = "1"
            out.write(f"\n== rerecord {case_id}: {run}: {command}\n")
            out.flush()
            code = subprocess.run(argv, cwd=str(repo_root()), env=run_env,
                                  stdout=out, stderr=subprocess.STDOUT).returncode
    return node if code == 0 else None


def _head() -> str:
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root()),
                         capture_output=True, text=True)
    return out.stdout.strip()


def _dirty() -> bool:
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                         cwd=str(repo_root()), capture_output=True, text=True)
    return bool(out.stdout.strip())


def summary_of(text: str) -> str | None:
    """The counts from the last summary line, or None when the suite did not run."""
    for line in reversed(text.splitlines()):
        found = SUMMARY.match(line.strip())
        if found:
            return found.group(1).strip()
    return None


def count_in(summary: str, word: str) -> int:
    found = re.search(rf"(\d+) {word}", summary)
    return int(found.group(1)) if found else 0


def of_the_suite(root: Path, node: str) -> bool:
    """
    True when the node id names a test file of the tree the gate runs.

    `main` deletes the cache before the run, so this filter holds two cases
    only: a directory-level id like `tests/rota` from a collection error, and a
    file removed while the run was in flight. Neither is a red this gate can
    name.
    """
    file = node.split("::", 1)[0]
    return file.startswith(f"{SUITE}/") and (root / file).exists()


def red_ids(root: Path) -> set[str] | None:
    """
    The reds of this run, from pytest's cache.

    Every key is a red of this run, because `main` deletes the cache first and
    then runs the whole `tests/rota` tree.

    None carries two meanings, and the caller tells them apart by the summary.
    The cache is off, or the run was green: pytest writes `lastfailed` only when
    the value changes, so a green run after the delete leaves no file at all
    (observed: the reviewer's probe of 2026-09-17, a green `-n 2` run recreated
    `nodeids` only).
    """
    path = root / LASTFAILED
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return {node for node in data if of_the_suite(root, node)}


def _read_baseline(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _write_baseline(path: Path, record: dict) -> None:
    # `newline=""` keeps the file at LF under Windows.
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(json.dumps(record, indent=2) + "\n")


def _listed(ids: list[str]) -> str:
    return ", ".join(ids) if ids else "none"


def _short(commit: str) -> str:
    return commit[:7] if commit else "unknown"


def _waits(ids: list[str]) -> str:
    return f"{len(ids)} stale cases wait for the main card"


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m rota.tools.gate",
        description="Run the suite once and print only what moved.")
    ap.add_argument("--baseline", action="store_true",
                    help="store this run as the baseline")
    ap.add_argument("--model", default=None,
                    help=f"the model the replay is held by (default {FALLBACK_MODEL})")
    ap.add_argument("--no-rerecord", action="store_true",
                    help="do not re-record the stale cases")
    ap.add_argument("--rerecord-now", action="store_true",
                    help="re-record even when the main card is held, for a "
                         "model the gate itself left loaded")
    args = ap.parse_args(argv)

    root = Path(root) if root is not None else repo_root()
    path = root / BASELINE_NAME
    stored = None
    if path.exists() and not args.baseline:
        stored = _read_baseline(path)
        # The gate never replaces a baseline in silence: a rewrite would drop
        # the reds the file held, and every later run would read green. The
        # refusal comes before the eight minutes of the run.
        if stored is None:
            print(f"baseline: did not parse ({path}); "
                  "delete it or pass --baseline")
            return 1

    model = args.model or os.environ.get("ROTA_MODEL") or FALLBACK_MODEL
    temp_root = TEMP_ROOT
    env = child_env(model, temp_root)
    # Asked once, before the run, so the line comes before the five lines.
    # The suite's replay calls no model, so only the re-records wait.
    held = [] if args.no_rerecord else main_card_held(env)
    if held:
        then = ("re-records run on --rerecord-now" if args.rerecord_now
                else "re-records wait")
        print(f"main card: held by {', '.join(held)}, {then}", flush=True)
    wait = bool(held) and not args.rerecord_now

    # The cache is cumulative: pytest drops only the ids it ran, so a removed
    # parametrised id or a fixed collection error stays in it for ever under
    # xdist (observed: the diff review of 2026-09-17, probe 1).
    (root / LASTFAILED).unlink(missing_ok=True)

    log = root / LOG_NAME
    started = time.monotonic()
    code = _run_suite(env, log)
    seconds = time.monotonic() - started

    try:
        text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    summary = summary_of(text)
    # A usage error or an xdist crash writes no summary and no FAILED line, so
    # a gate that counted reds would call that run green.
    if code not in (0, 1) or summary is None:
        print(f"suite: did not run (pytest exit {code})")
        for line in text.splitlines()[-20:]:
            print(line)
        return 1

    failed = red_ids(root)
    if failed is None:
        if count_in(summary, "failed") or count_in(summary, "error"):
            print(f"suite: {summary}")
            print("note: the suite has reds and there is no "
                  f"{LASTFAILED.as_posix()}, so the cache is off and the red "
                  "set is unknown")
            return 1
        failed = set()
    stale = _stale(model)
    # A case that failed `STALE` in the suite is stale, whatever `status`
    # reads. It joins the set only when the register is here to re-record.
    by_failure = set()
    if stale is not None:
        by_failure = stale_by_failure(text, failed) - stale
        stale = stale | by_failure
    failed_stale = set(by_failure)
    waiting = sorted(stale) if stale and wait else []
    if waiting:
        # A `STALE` red is unmeasured, not wrong, so a held card must not
        # turn it into a new red. A red for another reason stays, or a
        # known red would read as gone (observed: frame 124's diff review).
        unmeasured = stale_by_failure(text, failed)
        failed = {node for node in failed if case_of(node) not in unmeasured}
    if stale and not args.no_rerecord and not wait:
        # One case at a time, after the suite ends. Two writers on the
        # cassette file lost a run to `database is locked` (observed:
        # `plans/operating-facts.md`, frame 86, 2026-09-25).
        ids = sorted(stale)
        print(f"rerecording {len(ids)} stale cases, five live runs each, "
              f"on {model}")
        # The suite run is already spent. A failed step here must not take
        # the five lines and the baseline with it. Each step keeps what the
        # steps before it earned.
        before = after = None
        try:
            before = _states(model)
        except Exception as exc:
            print(f"note: re-record stopped: {exc!r}")
        passed_nodes = {}
        for case_id in ids:
            try:
                passed_nodes[case_id] = _rerecord(env, case_id, log)
            except Exception as exc:
                print(f"note: re-record stopped: {exc!r}")
                break
        skipped = [case_id for case_id in ids if case_id not in passed_nodes]
        if skipped:
            print(f"note: not rerecorded: {', '.join(skipped)}")
        try:
            stale_after = _stale(model)
            after = _states(model)
        except Exception as exc:
            # The stale set from before the re-records stays on the stale
            # line.
            print(f"note: re-record stopped: {exc!r}")
        else:
            stale = stale_after
        # A case stale by its failure stays stale only when it got no run.
        # After a run it is a measured red, and a second gate must not spend
        # five more live runs on it (ruled: frame 89's diff review, pass 7).
        by_failure = {case_id for case_id in by_failure
                      if case_id not in passed_nodes}
        if stale is not None:
            stale = stale | by_failure
        # These lines come before the five, so the last five lines stay the
        # gate.
        cleared = 0
        for case_id, node in passed_nodes.items():
            was = "unread" if before is None else before.get(case_id, "absent")
            now = "unread" if after is None else after.get(case_id, "absent")
            line = f"rerecorded {case_id}: {was} -> {now}"
            if case_id in failed_stale:
                line += ", stale by its failure"
            # A stale case fails its replay in the suite run. A plain run that
            # passes after the re-record clears that red. A case that still
            # fails stays in the red set like any other red.
            if node is not None and node in failed:
                failed.discard(node)
                cleared += 1
                line += ", red cleared"
            print(line)
        if cleared:
            # The counts come from the suite run, and a re-record does not
            # rerun the suite.
            print(f"note: {cleared} reds cleared by re-record. "
                  "The suite line still counts them.")

    head = _head()
    record = {
        "commit": head,
        "dirty": _dirty(),
        "when": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "model": model,
        "summary": summary,
        "failed": sorted(failed),
        "stale": None if stale is None else sorted(stale),
        "seconds": round(seconds, 1),
    }
    # With no baseline every known red is new, and the first run would print 22
    # tracebacks. That is the wall the gate exists to remove, so a run that
    # stores the baseline compares itself against itself.
    fresh = stored is None or args.baseline
    base = record if fresh else stored
    # A waiting run holds no red for its unmeasured cases, so a baseline from
    # it would call them green (observed: frame 124's diff review).
    wrote = fresh and not waiting
    if wrote:
        _write_baseline(path, record)

    base_failed = set(base.get("failed") or [])
    new_reds = sorted(failed - base_failed)
    gone = sorted(base_failed - failed)

    # The baseline's summary beside this run's: a change that stops 300 tests
    # from collecting reads as green against the reds alone, and the reader has
    # no other reference number.
    first = f"suite: {summary}"
    if not fresh:
        first += f" (baseline: {base.get('summary', '')})"
    print(first)
    print(f"new reds ({len(new_reds)}): {_listed(new_reds)}")
    print(f"reds gone ({len(gone)}): {_listed(gone)}")

    if stale is None:
        print(f"stale: the register is absent ({register_path()})")
    else:
        # The mark tells a reader why a case that `status` reads green is here.
        shown = [f"{case_id} (stale by its failure)" if case_id in by_failure
                 else case_id for case_id in sorted(stale)]
        line = f"stale ({len(stale)}): {_listed(shown)}"
        base_stale = base.get("stale")
        if base_stale is None:
            # The baseline was taken with no register, so the delta has nothing
            # to stand on. Said on the line: a silent skip would hold for ever
            # once the register comes back.
            line += " (no stale baseline)"
        else:
            came = sorted(stale - set(base_stale))
            left = sorted(set(base_stale) - stale)
            if came or left:
                line += f" (+{len(came)} -{len(left)} against baseline)"
        print(line)

    print(f"time: {seconds:.1f}s, model {model}, temp root {temp_root}, "
          f"baseline {_short(base.get('commit', ''))} {base.get('when', '')}")

    if wrote:
        print(f"note: baseline stored at {_short(record['commit'])}")
    elif fresh:
        print("note: baseline not stored, because stale cases wait for the "
              "main card")
    if head != base.get("commit"):
        print("note: the tree moved past the baseline "
              f"({_short(base.get('commit', ''))} -> {_short(head)})")
    if base.get("dirty"):
        print("note: the baseline was taken on an uncommitted tree at "
              f"{_short(base.get('commit', ''))}, so the compare is not "
              "commit to commit")
    passed = count_in(summary, "passed")
    was = count_in(base.get("summary") or "", "passed")
    if not fresh and passed < was:
        print(f"note: passed fell from {was} to {passed}")

    if new_reds:
        # A re-run of an L1 case writes `case_runs` rows through
        # `record_case_run`, and those rows move the trust state that
        # `casestatus` reports as PROV. Named here, so a reader does not
        # misread the next report.
        out = _rerun(env, new_reds)
        after = red_ids(root)
        flaky = [node for node in new_reds
                 if after is not None and node not in after]
        print("")
        for node in flaky:
            print(f"flaky: {node}")
        print(out)
        # A test that fails under load and passes alone is a defect, not noise,
        # so a flaky red keeps the exit code at 1 (ruled: the diff review of
        # 2026-09-17, point 7).
        if waiting:
            print(f"note: {_waits(waiting)}")
        print(f"exit 1: {len(new_reds)} new reds, {len(flaky)} of them flaky")
        return 1

    if waiting:
        print(f"exit {WAIT_EXIT}: {_waits(waiting)}")
        return WAIT_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
