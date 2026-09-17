# The gate: design record and brief (frame 30, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the post-mortem of frame 21, changes 5 and 7. The
implementer builds from the brief below. The reviewer reads this record
before any code exists.

## Why

Twelve suite runs inside agents cost about 25k tokens each. The agents
read the tracebacks of 22 known reds twelve times. One FAILED-list compare
missed a STALE case. Three quarters of a seven-minute run is fixture IO
on the HDD (observed: `plans/archive/postmortem-frame21-2026-09-16.md`,
the table row for suite replays). The gate turns a run into five lines
and a stored compare, so a reader sees only what moved.

## What the gate is

`rota/tools/gate.py`, run as `python -m rota.tools.gate`. One run does
these steps in order:

1. Runs the suite as a child process:
   `<sys.executable> -m pytest tests/rota --tb=no -rfE -q`. The child's
   stdout and stderr go to `.rota-gate.log` at the repo root, never to the
   terminal. `ROTA_MODEL` is `qwen3:8b` unless the caller's environment
   already sets `ROTA_MODEL`. The Bash timeout for a gate run is 600000.
2. Sets the temp root through one setting. `TEMP_ROOT` at the top of
   `gate.py` is `Path(os.environ.get("ROTA_GATE_TMP", "C:/Users/roman/rota_gate/tmp"))`.
   The gate creates the directory and exports `TMPDIR`, `TEMP` and `TMP`
   to it for the child process. All three names change together, because
   Python's `tempfile.gettempdir()` reads them in that order, and the git
   fixture's guard in `rota/testkit/gitfixture.py` follows `gettempdir()`.
   `--basetemp` alone breaks that guard (observed: `plans/operating-facts.md`,
   the WSL line under Hardware and drives).
3. Parses the log. The summary is the last line that matches
   `^=+ (.*) in ([\d.]+)s.*=+$`, kept without the `=` padding. A red is a
   line `^(FAILED|ERROR) (\S+)( - (.*))?$`. The red's key is the node id.
4. Reads the STALE set through `rota.tools.casestatus.status(model)`,
   with the same model the suite ran under. The set holds the ids of rows
   whose state is `STALE` or `NEW`. The model must match, because a
   qwen-held green renders as a llama STALE under the wrong model
   (observed: the comment in `casestatus.status`).
5. Reads or writes the baseline `.rota-gate.json` at the repo root. The
   file holds: `commit` (`git rev-parse HEAD`), `dirty` (true when
   `git status --porcelain` prints a tracked change), `when`, `summary`,
   `failed` (the sorted node ids), `stale` (the sorted case ids) and
   `seconds`. The gate writes the file when the file is missing, or when
   the caller passes `--baseline`. The gate never overwrites the file
   otherwise.
6. Prints the five lines, in this order:
   - `suite: <summary>`
   - `new reds (<n>): <node ids, comma separated, or "none">`
   - `reds gone (<n>): <node ids or "none">`
   - `stale (<n>): <case ids or "none">`, with ` (+<a> -<b> against baseline)`
     when the set moved
   - `time: <seconds>s, temp root <path>, baseline <commit short> <when>`
7. After the five lines, one note when `HEAD` differs from the baseline
   commit: `note: the tree moved past the baseline (<base short> -> <head short>)`.
   When the run wrote the baseline, the note is
   `note: baseline stored at <commit short>`.
8. After the notes, a traceback for each new red only. The gate re-runs
   the new reds as one child process:
   `<sys.executable> -m pytest <node ids> --tb=short -q -n0`, and prints
   that child's output in full. A new red that passes on the re-run is
   printed as `flaky: <node id>` instead.
9. Exit code 1 when there is at least one new red. Exit code 0 otherwise.

Arguments: `--baseline` (store the baseline from this run), `--model M`
(the suite's model, default from the environment as in step 1). No other
arguments. Extra pytest arguments are not passed through, so every gate
run measures the same thing.

## Tests

`tests/rota/test_gate.py`. No test runs pytest as a child and no test
opens `tests/rota/cassettes.db`. The gate takes its two external calls as
module-level functions that a test replaces with `monkeypatch`: `_run_suite(env) -> str`
(the log text) and `_stale(model) -> set[str]`. The tests cover:

- the summary and the red list parsed from a canned `-rfE -q` log that
  holds two FAILED lines, one ERROR line and one summary line with
  `failed`, `passed`, `skipped` and a time;
- a log with no failures: the red list is empty and the summary parses;
- the compare: new reds, reds gone, and the stale delta, against a
  baseline dict;
- the baseline round-trip in `tmp_path`: the first run writes the file,
  the second run does not change it, `--baseline` rewrites it;
- the five lines and the moved-tree note, from a fixed baseline commit
  and a fixed head;
- the exit code: 1 with a new red, 0 without.

The gate's main takes `root: Path` so a test points the baseline and the
log at `tmp_path`.

## Files

- Create `rota/tools/gate.py`.
- Create `tests/rota/test_gate.py`.
- Edit `.gitignore`: add `.rota-gate.json` and `.rota-gate.log` under the
  `# rota framework state` block.

No other file changes. `CLAUDE.md`'s two lines are the assistant's, after
the tool exists.

## Deviations from the frame's words, on purpose

- `-rfE`, not `-rf`: a collection error is a red that `-rf` does not
  list (reasoned: the `E` flag is the only way an ERROR node id reaches
  the log).
- The tracebacks come from a second, small pytest run on the new reds,
  not from the main run: the main run keeps `--tb=no`, so the log stays
  short, and the re-run prints only what is new (reasoned: slicing
  tracebacks out of a `--tb=short` log by test name is brittle under
  parametrised ids).

## The implementer's pass

One pass. Report in the shape the implementer definition gives. Do not
commit. The assistant runs the gate itself, then commits. The report's
section (b) carries the gate's five lines from one full run through
`python -m rota.tools.gate --baseline`, and the run time is the number
frame 30's ends-when asks for, beside 414 s. Do not touch
`tests/rota/walks.jsonl` or `You are a standby peer.md`: both are another
session's.
