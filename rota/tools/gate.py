"""
The suite in five lines, with a traceback for a new red only.

    python -m rota.tools.gate              # compare this run against the baseline
    python -m rota.tools.gate --baseline   # store this run as the baseline

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
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

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


def _run_suite(env: dict[str, str], log: Path) -> int:
    """Run the whole tree as a child. Write the log. Return the child's code."""
    with log.open("w", encoding="utf-8", errors="replace", newline="") as out:
        child = subprocess.run(
            [sys.executable, "-m", "pytest", SUITE, "--tb=no", "-rfE", "-q"],
            cwd=str(repo_root()), env=env, stdout=out, stderr=subprocess.STDOUT)
    return child.returncode


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


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m rota.tools.gate",
        description="Run the suite once and print only what moved.")
    ap.add_argument("--baseline", action="store_true",
                    help="store this run as the baseline")
    ap.add_argument("--model", default=None,
                    help=f"the model the replay is held by (default {FALLBACK_MODEL})")
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
    wrote = stored is None or args.baseline
    base = record if wrote else stored
    if wrote:
        _write_baseline(path, record)

    base_failed = set(base.get("failed") or [])
    new_reds = sorted(failed - base_failed)
    gone = sorted(base_failed - failed)

    # The baseline's summary beside this run's: a change that stops 300 tests
    # from collecting reads as green against the reds alone, and the reader has
    # no other reference number.
    first = f"suite: {summary}"
    if not wrote:
        first += f" (baseline: {base.get('summary', '')})"
    print(first)
    print(f"new reds ({len(new_reds)}): {_listed(new_reds)}")
    print(f"reds gone ({len(gone)}): {_listed(gone)}")

    if stale is None:
        print(f"stale: the register is absent ({register_path()})")
    else:
        line = f"stale ({len(stale)}): {_listed(sorted(stale))}"
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
    if head != base.get("commit"):
        print("note: the tree moved past the baseline "
              f"({_short(base.get('commit', ''))} -> {_short(head)})")
    if base.get("dirty"):
        print("note: the baseline was taken on an uncommitted tree at "
              f"{_short(base.get('commit', ''))}, so the compare is not "
              "commit to commit")
    passed = count_in(summary, "passed")
    was = count_in(base.get("summary") or "", "passed")
    if not wrote and passed < was:
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
        print(f"exit 1: {len(new_reds)} new reds, {len(flaky)} of them flaky")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
