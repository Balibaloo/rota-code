# Frame 304, review 1: pass 1 at ccb37449

Verdict: accept for the night. The door refuses s187's tst_02 v3 through the
real `tests.encode` path. The door refuses no other body of the 138 stored
bodies. On the night's shape, the new tail shows the Architect the test line.
Four medium findings stay open. None of them blocks a night on clickI with the
worktree on D: and Python on C:. Fix them before rota runs on another layout.

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r304` at
ccb37449, parent 2453d945. Probes ran with `D:/repos/rota/.venv/Scripts/python.exe`
(Python 3.14.2). The night databases were opened with `?mode=ro`, and each
probe copied a database into memory before a call that writes. Probe
scaffolds are in the scratchpad, under `f304r1_probe` and `f304r1_base`.

## The findings by severity

| # | Severity | Status | Finding | Fix |
|---|---|---|---|---|
| F1 | medium | CONFIRMED | The tail rule misses a library frame that pytest prints as a relative path. | Resolve the last location against the worktree, and treat a path that leaves the worktree as outside. |
| F2 | medium | CONFIRMED | The tail labels a raise in project code when the last frame is in the standard library. | Return None when any location line after the test's frame lies inside the worktree. |
| F3 | medium | CONFIRMED | The door refuses five shapes that run. None occurs in the 138 bodies. | Record `configure_mock`, `setattr` and constructor keywords as stores, skip `mock_open(mock=...)`, and walk only test functions and fixtures. |
| F4 | medium | PLAUSIBLE | The label reaches the Architect only as a JSON key, the form frame 110 found a seat does not read. The Developer gets no label. | Add a plain-word block for a red ref in `build_prompt`, and a line in `rota/roles/prompts/architect/escalate.md` and `developer/tests_failing.md`. |
| F5 | low | CONFIRMED | The refusal gives two steps and no route, and "drop the spec" is not possible for `mock_open`. | For `mock_open`, name one step: the stdin route of frame 254, or a stub that holds the name. |
| F6 | low | CONFIRMED | An import that hangs stalls the door 60 seconds for each spec'd mock, on each encode. | Cache the probe by worktree, head and chain, failures included, and cut the timeout to 15 seconds. |
| F7 | low | PLAUSIBLE | The door asks rota's own `unittest.mock`, and the sandbox can run another Python version. | Run the `hasattr` check inside the same sandbox probe. |
| F8 | low | PLAUSIBLE | The call site parses `surface_refs` with no guard, so a bad row raises a plain error, not a refusal. | Wrap the parse as `_arrange_raise_tail` does. |
| F9 | low | PLAUSIBLE | The new tail is up to 2000 characters, not 700, so a recorded prompt with such a ref changes. | Run casestatus at the gate and re-record a case only when it goes stale. |

## Point 1: the red test

The door refuses s187's tst_02 v3 (CONFIRMED). The probe copied
`clickI_night158.db` into memory, built the Tester sandbox on bg_2, called
`tests.triage`, and then called `tests.encode` with the stored body. The
call raised `Wall` in 0.07 seconds, with this text:

```
Line 6, `mock_stdin.read.return_value = ""`, reads `mock_stdin.read`. The spec of `mock_stdin` is `open`, from mock_open, and that spec holds no `read`. So the line raises AttributeError before the call under test. Build the stub so that `read` exists, or drop the spec
```

The routes: the `Wall` goes back to the seat as the call's error. The call
writes no row in any table (the row count of every table did not change).

The line raises as the door says (CONFIRMED). The probe ran the body under
bg_2's own interpreter, `.venv/Scripts/python.exe` at f7bb9d5, with stdin
closed. The raise is `AttributeError: Mock object has no attribute 'read'`
at body line 6, with the last frame at `unittest/mock.py` line 696.

The text: each sentence holds 20 words or fewer. The text names one fact.
The step is two steps joined by "or" (F5). The text names no route. For
`mock_open`, the spec comes from `mock_open` itself, so "drop the spec" is
not a step the Tester can take. On this criterion the route that works is
frame 254's: `confirm()` inside a command that `CliRunner().invoke(...,
input=...)` runs.

## Point 2: right tests refused

Count: 138 stored bodies, 0 syntax errors, 1 refused, and that body raises.
False refusals: 0 (CONFIRMED). Only four bodies hold "spec" or "mock_open",
and only tst_confirm_eof_02 of night 158 builds a spec'd mock.

The probe also ran the door on 24 written shapes, and ran each body under
Python (CONFIRMED). Five shapes are false refusals (F3):

| Shape | Door | Run |
|---|---|---|
| `m.configure_mock(read=1)`, then `m.read` | refuses | runs |
| `setattr(m, 'read', 1)` on a plain `spec`, then `m.read` | refuses | runs |
| `MagicMock(spec=[...], read=1)`, then `m.read` | refuses | runs |
| `mock_open(mock=MagicMock())`, then `m.read` | refuses | runs |
| a helper that no test calls reads past its spec | refuses | runs |

These shapes are right: `mock_open(read_data=...)` with `m.read_data` raises,
and the door refuses it. `patch.object(..., create=True)` is admitted. A
`spec` set to a local instance is admitted, because `_spec_names` declines a
local binding. `m.return_value`, `m.side_effect` and the assert methods are
admitted. The door misses `m.count += 1` on a spec without `count`, which
raises. That miss is silent, so it is safe.

## Point 3: the tail and the label

The probe resolved m77's six refs on night 158 for the Architect with
detail `escalate` (CONFIRMED). The tst_confirm_eof_02 tail now starts at
`>           mock_stdin.read.return_value = ""`. The row carries
`"label": "the test failed before any assertion"`. `build_prompt` for that
wake puts both into the user prompt, inside the JSON of "The message that
woke you". So dec_123's prompt would now show the test line.

The key is not dead, but its form is weak (F4, PLAUSIBLE). Frame 110 found
that a seat read the escaped JSON wrongly and read plain words correctly.
That is the reason `_failed_run_blocks` exists for the Tester challenge. No
prompt text explains the key. The Developer that sent m77 reads red runs
through `tests.load` on a `tests_failing` wake. That path does not call
`_resolve_refs`, so the Developer gets the old output and no label. The pass
report says the label reaches every non-challenge reader. That is true only
for readers that go through `_resolve_refs`.

The Tester challenge keeps the whole output, and `_failed_run_blocks` gives
the same words for s187's output. The principal's pages call
`_resolve_refs` with no role, and they render no `last_run`.

Files that should carry the label in plain words:
`rota/roles/prompts/architect/escalate.md`,
`rota/roles/prompts/developer/tests_failing.md`, and a block in
`build_prompt` next to `_failed_run_blocks`.

## Point 4: the clauses

The probe made a small project with real pytest outputs from `--tb=auto`,
and ran the door and `_arrange_raise_tail` on each (CONFIRMED).

| Case | Door | Tail |
|---|---|---|
| a raise inside a `try` in the arrange step | silent, the walk stops | label, starts at the test line |
| a raise after the first `if` | silent, the walk stops | label, starts at the test line |
| a chained exception | silent | today's tail |
| arrange calls project code that raises in `src/` | silent | today's tail |
| arrange calls project code that raises in `json` | silent | label (F2) |
| the plain s187 shape | refuses | label |
| the raise after the surface call | refuses, "the test cannot pass" | today's tail |

The `try` and `if` cases are right: the door stays silent, and the run
catches them. The chained case is safe. The `json` case is wrong. The
project code raised, the code can be at fault, and the label points away
from the code (F2).

F1: in the first run of this probe, every tail came back as today's tail.
The probe project was on C:, the drive of the Python install. Pytest then
prints `..\..\..\..\..\..\Python\...\unittest\mock.py:696`, a relative path.
`_arrange_raise_tail` reads a relative path as inside the worktree. With the
path replaced by an absolute one on another drive, every row above came out
as shown. On night 158 the worktree is on D: and Python is on C:, so the
night's shape works. A worktree under `C:\Users\roman` would not work, and a
pyenv or uv Python under the home directory on Linux would not work either.

## Point 5: the sandbox cost

One encode on bg_2 with `MagicMock(spec=io.StringIO)`: 0.03 to 0.11 seconds
with the door off, and 0.09 to 0.12 seconds with the door on (CONFIRMED).
One probe on bg_2 costs about 0.1 second. The probe reads project classes
correctly. `MagicMock(spec=Context).command` is refused, and bg_2's Python
raises on it, because `command` is set in `__init__`.

An import that fails gives a silent door (CONFIRMED). An import that calls
`input()` gives a silent door in 0.11 seconds, because stdin is the null
device. An import that sleeps 90 seconds stalled the door for 120 seconds on
a body with two spec'd mocks (CONFIRMED, F6). `subprocess.run` kills the
child at 60 seconds. Each mock name runs its own probe, and no cache holds
the result between encodes.

## Point 6: nothing else changed

`git diff 2453d945 ccb37449 --stat` shows three files, 524 insertions and no
deletions (CONFIRMED). In `runner.py` the diff adds `import ast`, the seven
lines in `_resolve_refs`, `FAILED_BEFORE_ASSERTION`, `_LOCATION` and
`_arrange_raise_tail`. In `api.py` the diff adds the call site in
`tests_encode` after door 17, `_DIR_PROBE`, `_MOCK_CTORS`, `_RAISE_BLOCKS`,
`_spec_names`, `_spec_source` and `_spec_mock_raise`. No line lies outside
the door and `_resolve_refs`.

`test_invoke_door.py::test_a_session_with_no_batch_reads_the_root` is red at
2453d945 (CONFIRMED). The probe extracted 2453d945 with `git archive` and ran
the test there, with `pythonpath = .` from `pytest.ini`. It fails at line 381
there and at ccb37449. The six tests of `test_frame304_arrange_raises.py`
pass at ccb37449.
