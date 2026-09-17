# The gate: design record and brief (frame 30, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the post-mortem of frame 21, changes 5 and 7. Amended
after the design review of 2026-09-17 03:45 (reviewer type on Opus, eight
findings, four outside). The implementer builds from the brief below.

## Why

Twelve suite runs inside agents cost about 25k tokens each. The agents
read the tracebacks of 22 known reds twelve times. One FAILED-list compare
missed a STALE case. Three quarters of a seven-minute run is fixture IO
on the HDD (observed: `plans/archive/postmortem-frame21-2026-09-16.md`,
the table row for suite replays). The gate turns a run into five lines
and a stored compare, so a reader sees only what moved.

## What the gate is

`rota/tools/gate.py`, run as `python -m rota.tools.gate` from the repo
root. One run does these steps in order:

1. Builds the child environment. Start from `os.environ`. Set
   `ROTA_MODEL` to `MODEL`, where `MODEL = os.environ.get("ROTA_MODEL") or "qwen3:8b"`,
   or the `--model` argument when given. Never read `DEFAULT_MODEL` from
   `rota.llm.llm`: its fallback is `llama3.1:8b`, and under that model
   `casestatus.status` reports 62 stale cases that are green under qwen
   (observed: the design review's probe 5). Delete `ROTA_L1`, `ROTA_T1`,
   `ROTA_REFRESH` and `ROTA_MODEL_FORCE` from the child environment: any
   of them turns a gate run into a recording run or moves the pins
   (observed: `rota_serial_plugin.py`, `tests/rota/test_l1.py:129`).
2. Sets the temp root through one setting. `TEMP_ROOT` at the top of
   `gate.py` is `Path(os.environ.get("ROTA_GATE_TMP", "C:/Users/roman/rota_gate/tmp"))`.
   The value takes the Windows form `C:/...`. A Git Bash form `/c/...`
   resolves to `C:\c\...` (observed: the design review, finding 7). The
   gate creates the directory and exports `TMPDIR`, `TEMP` and `TMP` to
   it for the child. All three names change together, because Python's
   `tempfile.gettempdir()` reads them in that order, and the git
   fixture's guard in `rota/testkit/gitfixture.py` follows `gettempdir()`
   (observed: the review's probes 3 and 4: `tmp_path` and `is_temp_rooted`
   followed the exported names).
3. Runs the suite as a child process from the repo root:
   `<sys.executable> -m pytest tests/rota --tb=no -rfE -q`. The child's
   stdout and stderr go to `.rota-gate.log` at the repo root, never to the
   terminal. The gate keeps the child's return code. A code other than 0
   or 1 means the suite did not run: print
   `suite: did not run (pytest exit <n>)` and the last 20 lines of the
   log, and exit 1 (reasoned: a usage error or an xdist crash has no
   FAILED line and no summary, so a count-based gate would exit 0).
4. Reads the summary: the last log line that matches
   `^=*\s*(.*?) in ([\d.]+)s` (observed: under `-q` the final line has
   no `=` padding, `3 failed, 1 passed, 1 error in 22.59s`). No match
   means the suite did not run: treat as step 3's failure.
5. Reads the red set from `.pytest_cache/v/cache/lastfailed` under the
   repo root, right after the run. The file is a JSON object keyed by
   node id. Every key is a red of this run, because the gate always runs
   the whole `tests/rota` tree, so pytest removes the ids that passed.
   Do not parse `FAILED` lines for ids: eight node ids in the suite hold
   a space, and a regex on `\S+` drops them (observed: the review's probe
   7, `tests/rota/test_delivery.py` and `tests/rota/test_toolproto_quotes.py`).
   A summary with `failed` or `error` above zero and no cache file means
   the cache is off: print a note and exit 1.
6. Reads the STALE set through `rota.tools.casestatus.status(MODEL)`:
   the ids of rows whose state is `STALE` or `NEW`. The model is the one
   from step 1.
7. Reads or writes the baseline `.rota-gate.json` at the repo root. The
   file holds: `commit` (`git rev-parse HEAD`), `dirty` (true when
   `git status --porcelain --untracked-files=no` prints a line), `when`,
   `model`, `summary`, `failed` (the sorted node ids), `stale` (the
   sorted case ids) and `seconds`. The gate writes the file when the file
   is missing, or when the caller passes `--baseline`. The gate never
   overwrites the file otherwise. A run that writes the baseline compares
   the run against itself: no new reds, no reds gone, no tracebacks, exit
   0 (reasoned: with no baseline every known red is new, and the first
   run would print 22 tracebacks, the wall the gate exists to remove).
8. Prints the five lines, in this order:
   - `suite: <summary>`
   - `new reds (<n>): <node ids, comma separated, or "none">`
   - `reds gone (<n>): <node ids or "none">`
   - `stale (<n>): <case ids or "none">`, with ` (+<a> -<b> against baseline)`
     when the set moved
   - `time: <seconds>s, model <MODEL>, temp root <path>, baseline <commit short> <when>`
9. After the five lines, the notes, each on its own line:
   - when this run wrote the baseline: `note: baseline stored at <commit short>`;
   - when `HEAD` differs from the baseline commit:
     `note: the tree moved past the baseline (<base short> -> <head short>)`;
   - always, when the baseline's `dirty` is true:
     `note: the baseline was taken on an uncommitted tree at <short>, so the compare is not commit to commit`.
10. After the notes, a traceback for each new red only. The gate re-runs
    the new reds as one child process with the same environment:
    `<sys.executable> -m pytest <node ids> --tb=short -q -n0`, and prints
    that child's output in full. `-n0` on the command line wins over the
    ini's `-n auto` (observed: the review's probe 9). A new red that
    passes on the re-run is printed as `flaky: <node id>` instead. Side
    effect, named here so a reader does not misread it: a re-run of an L1
    case writes `case_runs` rows through `record_case_run`, and those rows
    move the `trust` state that `casestatus` reports as PROV.
11. Exit code 1 when there is at least one new red. Exit code 0 otherwise.

Arguments: `--baseline` (store the baseline from this run) and
`--model M`. No other arguments. Extra pytest arguments are not passed
through, so every gate run measures the same thing.

## Tests

`tests/rota/test_gate.py`. No test runs pytest as a child and no test
opens `tests/rota/cassettes.db`. The gate takes its external calls as
module-level functions that a test replaces with `monkeypatch`:
`_run_suite(env, log) -> int` (writes the log, returns the child's code),
`_rerun(env, ids) -> str`, `_stale(model) -> set[str]`, `_head() -> str`
and `_dirty() -> bool`. The gate's `main(argv, root: Path)` takes the
root so a test points the log, the cache file and the baseline at
`tmp_path`. The tests cover:

- the summary parsed from a canned `-q` log whose last line is
  `3 failed, 1 passed, 1 error in 22.59s`, and from a log whose last
  line is `1 passed in 2.67s`;
- the red set read from a canned `lastfailed` file that holds a node id
  with a space and one with brackets;
- a child return code of 4 with an empty log: the did-not-run line and
  exit 1;
- the compare: new reds, reds gone, and the stale delta, against a
  baseline dict;
- the baseline round-trip in `tmp_path`: the first run writes the file
  and exits 0 with no traceback, the second run does not change the file,
  `--baseline` rewrites it;
- the five lines and the three notes, from a fixed baseline commit, a
  fixed head and a dirty baseline;
- the exit code: 1 with a new red, 0 without;
- the child environment: `ROTA_L1` and `ROTA_MODEL_FORCE` set by the
  caller are absent from the environment the gate hands to `_run_suite`,
  and `TMPDIR`, `TEMP`, `TMP` all equal the temp root.

## Files

- Create `rota/tools/gate.py`. Follow `rota/tools/casestatus.py`: relative
  imports, an `if __name__ == "__main__"` block, no database open at
  import time.
- Create `tests/rota/test_gate.py`.
- Edit `.gitignore`: add `.rota-gate.json` and `.rota-gate.log` under the
  `# rota framework state` block.

No other file changes. `CLAUDE.md`'s two lines and the agent definitions'
casestatus line are the assistant's, after the tool exists.

## Deviations from the frame's words, on purpose

- `-rfE`, not `-rf`: a collection error is a red that `-rf` does not
  list (reasoned: the `E` flag is the only way an ERROR node id reaches
  the log for a reader).
- The tracebacks come from a second, small pytest run on the new reds,
  not from the main run: the main run keeps `--tb=no`, so the log stays
  short, and the re-run prints only what is new (reasoned: slicing
  tracebacks out of a `--tb=short` log by test name is brittle under
  parametrised ids).

## The implementer's pass

One pass. Report in the shape the implementer definition gives. Do not
commit. The assistant runs the gate itself, then commits. Run the touched
test file first: `tests/rota/test_gate.py`. Then run one full suite
through the gate, `python -m rota.tools.gate --baseline`, with the Bash
timeout at 600000, in place of the plain pytest command in your
definition. The report's section (b) carries the gate's five lines and
its notes. The time line is the number frame 30's ends-when asks for,
beside 414 s. Do not run `casestatus --red`: its default model is llama,
and the gate's stale line replaces it. Do not touch
`tests/rota/walks.jsonl` or `You are a standby peer.md`: both are another
session's.
