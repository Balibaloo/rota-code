# Frame 195 design review, Opus, 2026-10-11 03:03

The reviewer's report, verbatim from its final message. The harness
refused its write to the scratchpad, so this file is the only copy.
102.9k on the harness line against 100k. Probes ran on copies under the
session's scratchpad `rv195d/`. Rota workflow.

Verdict: start the build after the fixes below. Six of the eight points are defects or gaps in the design, and none is a reason to drop it. The one change that matters most is that the plugin must never change a test's result. Today it can, in four ways that I reproduced.

## 1. The load

**CONFIRMED.** Two things can shadow or hide the plugin.

`python_for` returns the worktree venv when one exists. On `bg_3` that venv is Python 3.14.2 with pytest 9.1.1, and click is installed editable from `src`. The plugin loads under that interpreter (observed). pytest imports a `-p` module before any `conftest.py` and before the ini `pythonpath`. So a conftest that edits `sys.path` cannot shadow it (reasoned: pytest's load order).

- **Shadow 1:** `python -m pytest` puts the working directory ahead of `PYTHONPATH`. A file `pytest_caught.py` at the worktree root replaced the plugin, and the run printed `shadow` (observed).
- **Shadow 2:** `addopts = --show-capture=no` hides every report section. With `--show-capture=no` the section count was 0. With `--tb=short` it was 1 (observed).
- The plugin runs under any Python that a project venv has. Its syntax must stay old, with no `match` and no new f-string forms (reasoned).

Fix: give the module a name unique to rota, for example `_rota_caught`. Add `--show-capture=all` to the harness argv, because a command-line value wins over `addopts`.

## 2. The import before the call

**CONFIRMED.** The import can turn a pass into a fail, because the design catches only `ImportError`.

- **No click installed:** one failed import per test, and no result changes (reasoned: the `try`).
- **`click/testing.py` raises `NameError` at import:** `test_plain` passed without the plugin and failed with it, at `click\testing.py:1: NameError` (observed, `stub_nameerr`).
- **`click/testing.py` warns `DeprecationWarning` under `filterwarnings = error`:** the pass became `FAILED ... DeprecationWarning: old` (observed, `stub_warn`). The import runs inside pytest's warning filter for each test.
- **Import order:** an early import fills `sys.modules`. A test that expects a warning at import time with `pytest.warns` then sees none (reasoned).

Fix: import only when `"click" in sys.modules`. Do the import inside `warnings.catch_warnings()` with `simplefilter("ignore")`, and catch `Exception`, not `ImportError`.

## 3. The wrap and the code under test

**CONFIRMED.** I found two ways the wrapper turns a pass into a fail. I found no way it turns a fail into a pass, because the wrapper returns the original value and the section goes on failed reports only (reasoned).

- **A diff stores `exc_info` as an exception, not a tuple:** `exc[1]` raised `TypeError: 'ValueError' object is not subscriptable` inside `invoke`, and the test failed (observed, `stub_res`).
- **A test checks `inspect.signature(CliRunner.invoke)`:** it failed, because the signature became `(self, *a, **k)` (observed, `stub_res`).
- **A subclass:** one that calls `super().invoke` is seen. One that overrides `invoke` without `super` is not seen, and no result changes (reasoned).
- **A reload of `click.testing`:** the reloading test runs unwrapped, and the next test wraps the new class (reasoned).
- **Kept frames:** the stored `exc_info` keeps its frames alive until the next test. That can delay a `ResourceWarning` under `filterwarnings = error` (reasoned). The scope's full run of click's suite did not show it.

Fix: wrap the inspection in `try/except Exception` and apply `functools.wraps(orig)`. Format the traceback text at once, and keep the text, not `exc_info`.

## 4. The section and the tail

**CONFIRMED for one call, a defect for more calls and for a frame on a second drive.**

One call gives a section of 539 characters and an output of 1512. The tail holds all three lines that matter (observed, `rv195d/one.txt`):

- `E       AssertionError: ...`
- `tests\test_version_option_version_format.py:17: AssertionError`
- `src\click\decorators.py:508: NameError`

More calls and other drives:

- **Three raising calls:** the section is 1409 characters and the output is 2333. The tail still keeps the assertion line. The cut falls five lines above it (observed, `three.txt`).
- **Four calls:** the section is 1844 and the output is 2808. The tail drops the assertion line (observed, `four.txt`).
- **Five calls:** the cut also drops the section title. The wording then falls back to "before any assertion ran", which is false (reasoned: about 470 characters per entry).
- **A frame on another drive:** `os.path.relpath` raises `ValueError: path is on mount 'C:', start on mount 'D:'` for a stdlib frame. Base Python is on C:, and the worktrees are on D: (observed). An exception in the report hook gave `INTERNALERROR` and exit code 3, so the harness records `error`, not `fail` (observed, `stub_x`).

Fix: dedupe the entries by type, file and line, and keep one entry plus "and N more". Fall back to the absolute path when `relpath` raises.

## 5. The `raised at` words

**CONFIRMED that the design's order holds, with one gap.**

The regex at `api.py:7069` matches the probe output's assertion line first and `src\click\decorators.py:508: NameError` last (observed). The summary line `FAILED tests/...::test - NameError: ...` starts with `FAILED `, so `^[^\s:]+\.py` cannot match it (observed: the stub runs printed that form, and the regex found no match in it).

The gap: the regex needs a `.py` path and an exception name that ends in `Error`, `Exception` or `Exit`. Some caught exceptions give a final line that the regex misses:

- a custom `class Boom(Exception)`
- a `StopIteration`
- a last frame in `<string>`

The last match is then the assertion. The row says "the test's own assertion" next to the section (read: the regex).

Fix: give the final line a fixed prefix, for example `caught by CliRunner at <path>:<line>: <Name>`. Let the third wording read that line with its own pattern, not `frames[-1]`.

## 6. The `-W` flag and the own flag

**NOT A DEFECT.** Load the plugin on both the project's tests and the batch's own tests, as item 6 says.

- **Click's own suite:** on click at 3eebc90, the probe plugin kept 3 failed and 1910 passed (observed by the scope). The project's `test_testing.py` exception tests pass, so they get no section.
- **The measure:** night 138's project test `inh_dcc9ea38` failed beside `tst_v3` at 3eebc90. A plugin on the own tests alone leaves that row with the false "the test's own assertion", and the measure then reads two row shapes.
- **Caveat:** `-W ignore::DeprecationWarning` goes on the own tests only. So the warning failure of point 2 hits project tests only, and the fix of point 2 removes it.

Fix: none.

## 7. The rules

**NOT A DEFECT, with one wording fix.**

`DECISIONS.md:943` governs refusals at the door. The plugin refuses nothing, so the certainty test does not apply. Law 2 governs judgement that travels between roles. The section is text that the test process printed, which is a harness fact.

In the third wording, the file, the line, the exception name and the touched-file flag are facts. "The runner caught it inside the command so `result.output` was empty" is a causal claim, because a command can echo text and then raise.

Fix: let the plugin record `result.output == ""` as a fact. Let the wording state the facts without "so".

## 8. The measure

**CONFIRMED.** The baseline "8 of 8" cannot be reproduced from the night's database.

`test_runs` for b_3 keeps attempts 4, 6, 7 and 8, and the 34 rows of attempt 4 are all `pass` (observed). The sessions and their wake turns survive. In turn 1, 10 of 11 `tests_failing` sessions on b_3 carry the empty-output assertion. These are s380 to s393, over 6 of 7 wake attempts (3 to 8). s378, attempt 2, does not carry it (observed, on a copy of `.rota/clickI_night138.db`).

The query:

```sql
SELECT s.id, s.wake_detail,
       max(instr(t.user,'Expected Python version string in output: ')>0),
       max(instr(t.user,'CliRunner caught an exception')>0)
FROM sessions s JOIN turns t ON t.session_id=s.id
WHERE s.role='developer' AND s.wake_kind='tick:tests_failing'
  AND s.wake_refs LIKE '%"b_3"%' AND t.seq=1
GROUP BY s.id ORDER BY s.seq
```

Fix: count the Developer `tests_failing` sessions whose turn 1 shows an empty-output red with no section. Write the baseline as 10 of 11 sessions, and put the query in the design.

## Verdict

Start the build, after the fixes above. The change that matters most is that the plugin must never change a result:

1. Guard the import, the wrapper and the report hook with `except Exception`.
2. Apply `functools.wraps` to the wrapper.
3. Keep the formatted text, not `exc_info`.

These three steps close the failures of points 2, 3 and 4.
