# F5 review, pass 1: commit 461cc04b on f5root

Worktree `C:/Users/roman/rota_f5`, parent `ae9b99c6`. Read-only review. No gate ran.

Result: the move to one function is clean and holds no foreign hunk. The rule inside the function has two defects that real runs show. A single-test file that errors in a fixture gives the progress marker `[100%]` as the error line. The chained-raise rule gives the cause, and 175 of 179 recorded chained red runs then show click's internal `KeyError: 'prog_name'`. Readers still give two different lines for one chained run.

## (a) Verdicts

1. error_line and error_at: FAIL on 2 of 6 real outputs. Fixture error gives `[100%]`. Implicit chain gives the caught exception. Assert, raise-from, collection and SyntaxError give a usable line.
2. The 11 moved readers: PASS. Each calls error_line or error_at. No moved reader keeps an `E` rule of its own. The 3 that stay read another fact.
3. Cause over last part: INCONSISTENT. For one chained run, check_line, _first_error, _base_quote and _red_line_refusal give the cause. _own_reds and _unchanged_note give the last raise.
4. The pin test: FAIL as a guard. It catches only `startswith("E ")` and the regex `E` plus whitespace in a literal. It does not scan for `Traceback` or `Error:` at all.
5. test_frame317_answer_wake: PASS. The pin lost only the deleted "Traceback" fallback. It still pins a head for a run with no `E` line, and the empty head inside the tail.
6. Foreign hunks: NONE. The 19 hunks in db.py, runner.py, sandbox.py, api.py and principal.py are all F5. No `latest_runs` text is in the commit. The worktree is clean.
7. Stale cases: NONE. One recorded case holds a chain, and its first `E` line is the same under both rules. No case holds a collection error, an `E File` frame, a native traceback or a progress line.

## (b) Findings

1. rota/core/harness.py:190 and 205-212. Severity high. CONFIRMED.
   The pattern `_E_LINE` matches pytest's `-q` progress line when a one-test file errors. That line is `E` followed by spaces and `[100%]`.
   Probe 1 (fixture case) gave `[100%]` from error_line, _first_error, _failure_line and _base_quote. _own_reds gave `KeyError: 'host'` for the same run.
   The red identity in db._red_of is then `[100%]` for every setup error. So lift_on_red_move cannot see a red that moves from one setup error to another.
   _tail re-adds the progress line when a long output cuts it (probe 2). The old rules had the same defect. The new rule keeps it.
   Reach in the record: 0 of all red runs in clickI_night82 to night171 (probe 5). The path is real for a Tester who writes a fixture.
   Fix: skip a line that ends in a pytest progress marker, or start the `E` search after the FAILURES or ERRORS banner.

2. rota/core/harness.py:205 (the chain rule in the docstring at 203-205). Severity high. CONFIRMED for the count, PLAUSIBLE for the harm.
   The first `E` line of a chained run is the cause. In the night databases, 179 red runs are chained, and all 179 are implicit chains ("During handling").
   175 of them give `KeyError: 'prog_name'` as the cause and `AttributeError: 'function' object has no attribute 'name'` as the last raise (probe 6).
   The KeyError is click's own `extra.pop("prog_name")` lookup that click catches. The AttributeError names the seat's mistake, a plain `def` passed to CliRunner.
   Probe 1 (chain2) shows the same shape in a test: it catches a KeyError and fails on its assertion. error_line gives the caught `KeyError: 'missing'`.
   pytest's own `FAILED ... - ` summary line names the last raise. The code records night 107 (s151) and night 159 (tst_cr1) as the same shape.
   The build took the cause because test_frame317 went red. That test pins _raising_line_head, which shows the raising line that the 700-character tail cuts. The AttributeError is inside that tail already. So the test proves a need of the head, not a rule for every reader.
   Fix: let error_at give the last section's error line, and let _raising_line_head apply error_at to each chained section that the tail cuts.

3. rota/roles/api.py:18090 (_own_reds) and 17636 (_unchanged_note) against rota/roles/principal.py:510 (_failure_line). Severity low. CONFIRMED.
   For probe 1's raise-from run, error_line gives `KeyError: 'prog_name'`. _own_reds gives `app.ConfigError: the config is bad`.
   So the check row and the encode note name two different errors for one run. 179 recorded runs would show the split.
   The commit body says "one rule". The second rule lives in the callers' slice after the last `>` line, and the pin does not see it.
   Fix: after finding 2, the slice gives the same line as the whole run, so delete the slice or keep it as a named site in the pin.

4. tests/rota/test_f5_error_line.py:189 (`_E_RULE`). Severity low. CONFIRMED.
   Probe 3 put six readers in a scratch tree. The pin found 1 of 6: `startswith("E ")`.
   It missed `"Traceback" in ln` (the fallback that this commit deleted), a regex over `Error: `, `ln[:2] == "E "`, a tuple `startswith`, and a regex `E +`.
   Fix: assert by behaviour instead. Feed each reader one chained, one collection and one native output, and compare with error_line.

5. rota/core/harness.py:217-221 (the native form). Severity low. CONFIRMED.
   An INTERNALERROR run prefixes each frame with `INTERNALERROR>`. The native frame pattern needs leading whitespace, so error_line gives "" (probe 4).
   The old _raising_line_head found such a run through its "Traceback" fallback. The run ends `INTERNALERROR> RuntimeError: the hook broke`.
   Fix: strip an `INTERNALERROR> ` prefix before the native search.

Outside the points: none beyond findings 1 and 5, which reach db.red_before, db.lift_on_red_move and _tail.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/f5rev`. Each ran with the venv python from the worktree root.

- Six scratch projects (assert, chain, chain2, collect, syntax, fixture). pytest ran with the harness flags `-q --no-header --show-capture=all --tb=auto`. The outputs are `<name>.out`.
- probe1.py: error_line, _first_error, _failure_line, _base_quote and the last-`>` slice on each output after harness._tail.
- probe2.py: _own_reds, _failed_before_assertion and _raising_line_head on chain, chain2 and fixture. A padded fixture output tested the _tail cut.
- probe3.py with fakeroot/rota/fake.py: the pin's `_sites` scan over six reader shapes.
- probe4.py with internal and conf: an INTERNALERROR run and a conftest import error.
- probe5.py: read-only scan of `D:/repos/rota/.rota/clickI*.db` for progress-line error lines, chained runs and native-only runs.
- probe6.py: the cause and the last raise of each chained red run in clickI_night1*.db.
- grep of tests/rota/cases, tests/rota/fixtures, cassettes.json and walks.jsonl for the changed output shapes.

## (d) Usage

Input tokens: about 82k. Output tokens: about 9k. Total: about 91k. The run passed the 70k cap.
