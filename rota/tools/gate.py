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
    for name in RECORDING_NAMES:
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


def _stale(model: str) -> set[str]:
    """The case ids with no recording against the current prompt."""
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

    The cache is shared with every other pytest run in this checkout. An id the
    tree does not collect is an id pytest never drops, so it would read as a red
    for ever. The first gate run found 29 ids for 23 reds: six came from a
    review probe on a temp file and had an empty file part, like `::test_bad`
    (observed: 2026-09-17, `.pytest_cache/v/cache/nodeids` held eight ids).
    """
    file = node.split("::", 1)[0]
    return file.startswith(f"{SUITE}/") and (root / file).exists()


def red_ids(root: Path) -> set[str] | None:
    """
    The reds of this run, from pytest's cache.

    Every key of this tree is a red of this run, because the gate always runs
    the whole `tests/rota` tree, so pytest drops the ids that passed. None means
    the cache is not there.
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
    model = args.model or os.environ.get("ROTA_MODEL") or FALLBACK_MODEL
    temp_root = TEMP_ROOT
    env = child_env(model, temp_root)

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
    stale = set(_stale(model))

    head = _head()
    record = {
        "commit": head,
        "dirty": _dirty(),
        "when": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "model": model,
        "summary": summary,
        "failed": sorted(failed),
        "stale": sorted(stale),
        "seconds": round(seconds, 1),
    }
    path = root / BASELINE_NAME
    stored = _read_baseline(path)
    # With no baseline every known red is new, and the first run would print 22
    # tracebacks. That is the wall the gate exists to remove, so a run that
    # stores the baseline compares itself against itself.
    wrote = stored is None or args.baseline
    base = record if wrote else stored
    if wrote:
        _write_baseline(path, record)

    base_failed = set(base.get("failed", []))
    base_stale = set(base.get("stale", []))
    new_reds = sorted(failed - base_failed)
    gone = sorted(base_failed - failed)
    came = sorted(stale - base_stale)
    left = sorted(base_stale - stale)

    print(f"suite: {summary}")
    print(f"new reds ({len(new_reds)}): {_listed(new_reds)}")
    print(f"reds gone ({len(gone)}): {_listed(gone)}")
    line = f"stale ({len(stale)}): {_listed(sorted(stale))}"
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

    if new_reds:
        # A re-run of an L1 case writes `case_runs` rows through
        # `record_case_run`, and those rows move the trust state that
        # `casestatus` reports as PROV. Named here, so a reader does not
        # misread the next report.
        out = _rerun(env, new_reds)
        after = red_ids(root)
        print("")
        for node in new_reds:
            if after is not None and node not in after:
                print(f"flaky: {node}")
        print(out)

    return 1 if new_reds else 0


if __name__ == "__main__":
    raise SystemExit(main())
