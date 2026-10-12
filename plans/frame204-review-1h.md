# Frame 204, review 1h of 78b9b705

Read-only review on the worktree `C:/Users/roman/rota_rv204h` at 78b9b705 (the meta workflow).
The reviewer ran no gate and re-recorded no case. Probes are dated 2026-10-12, about 14:55 to 15:00.

Verdict: the code holds points 1, 2, 4, 5, 6 and 7. Point 3 does not hold as an acceptance. The stale line of the pass is clean because the L3 case failed on a locked database, not because the case replayed (H1). Re-run the case before the walk.

## (a) Verdicts

1. HOLDS. `session_sandbox` (`rota/core/runner.py:3210`) passes `wake=wake` to `sandbox.build`, and `build` sets `wake_kind=wake.kind` (`rota/core/sandbox.py:707`). The scheduler makes the wake as `Wake("vision_keeper", "tick:reconcile", ...)` (`rota/core/scheduler.py:708`). Nights 141 and 142 stored 38 `tick:reconcile` sessions each, all in mode "normal".
2. HOLDS, with one low. The Developer on `tick:verdict_failed` has the wake refs `b_a9c366`, the batch. It now reads "'criterion_deviation' is no table, so send the id of a row your wake names: b_a9c366, with the table that row is in". The ref resolves through `ref_resolves`, and `batches` is an id table, so a call can take it. The note is about criterion `c_3958f9`, which the advice does not name (L1).
3. FAILS as an acceptance. The case failed with `sqlite3.OperationalError: database is locked` (`.rota-gate.log:101`). `stale_by_failure` admits only a `Failed: STALE ` message, so the case left the stale set. The case wrote no `case_runs` row in the 1h gate. The last rows are from 13:08:42, the 1g gate (H1).
4. HOLDS. Every reconcile ref of nights 141 and 142 gets the same answer from the old and the new `_is_prose_ref`. All 76 reconcile wake refs are `@prose` or `@prose:docs/*.md`, and all read true. The new test misses refs that no night sent (L2).
5. HOLDS. `tests/rota/test_prompts.py:300` joins `sentence` and `template` on single spaces before the three asserts.
6. HOLDS. With `rota` from 07b2cbcc and the test files from 78b9b705: "3 failed, 40 passed". The three reds are the reconcile test at line 164, the `readme_parser.py` step at line 214, and the unknown-table test at line 238. At 78b9b705: "43 passed".
7. HOLDS. The commit touches three files. It changes the docstring of the private `_is_prose_ref` only, no op docstring and no brief. The diff and the three files hold 0 CR bytes at both commits.

## (b) Findings

H1. `rota/tools/gate.py:165-186` and `:484`, high, CONFIRMED.
The 1h suite failed 10 chain and gauntlet cases with "database is locked" (`.rota-gate.log:93-102`).
Nine were new reds. The gate ran them again, they passed, and the gate called them flaky.
`L3-a-failed-verdict-turns-into-a-fix` is a baseline red, so the gate did not run it again.
Its lock error is no `Failed: STALE ` line, so the stale set dropped it, and the line printed `stale (0): none`.
`case_runs` holds no row for the case after 13:08:42, and the gate wrote other rows until 14:48.
So no replay of the new refusal text ran, and the case that renders the changed text is unmeasured.
Fix: re-run the L3 case alone, and make the gate treat a "database is locked" red as unmeasured, known red or not.

L1. `rota/roles/api.py:8244-8252`, low, PLAUSIBLE.
The unknown-table advice names every wake ref. For the L3 Developer, that is the batch `b_a9c366`.
The assumption is about criterion `c_3958f9`, which the wake block shows in `criteria.load`.
So a seat that follows the advice logs the note on the batch, not on the criterion.
Fix: name the rows the pre-run reads show, or accept the wake refs as a known limit and record it.

L2. `rota/roles/api.py:8148-8160`, low, PLAUSIBLE.
The new test reads the last path part as a whole name. `README.md#install` and `docs/x.md#usage` were true and are now false.
`docs/index.html`, `CHANGES` and `readme.markdown` are false too. No ref of nights 141 and 142 has these shapes.
`@prosecutor` reads true, which is harmless.
Fix: strip a `#` anchor before the suffix test, and add `.html` and `.markdown`.

L3 (outside). `rota/roles/api.py:8235-8236`, low, PLAUSIBLE.
`_declares_an_area` comes first. On a night, orient writes `model_areas` before reconcile, and both nights end with 2 rows in `model_areas` and in `area_hashes`.
So at night the reconcile seat gets the area advice, and never the `@prose` advice, whatever its wake kind.
The H1 fix of review 1g acts on an empty account only, which is the VK4 interview's state.
Nights 141 and 142 show 0 ref refusals for the reconcile seat, so no night measures this.
Fix: test the reconcile wake kind before `_declares_an_area`, or add `@prose` to the area advice for that seat.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv204h/`. The databases there are copies.

- p1.py: the Vision Keeper sessions by mode and wake kind in n141.db and n142.db. Night 141: `('vision_keeper', 'normal', 'tick:reconcile', 38)`. Night 142: the same, 38. `model_areas` and `area_hashes` hold 2 rows each in both nights.
- p2.py: the 4 old-text cassettes in a copy of `tests/rota/cassettes.db`. All four are gemma3:12b, "You were woken by: tick:verdict_failed", "Refs: b_a9c366". The pre-run reads are `batches.expect`, `criteria.load` with `c_3958f9`, and `verdicts.load`.
- p2b.py: the Developer built at 78b9b705 in mode "normal", with `wake_refs=('b_a9c366',)`. `kind='gap'` gives the refusal quoted in point 2. `kind='blocked'` takes the fault route. `batches` and `criteria` are in `_id_tables`.
- p4.py: the old and the new `_is_prose_ref` on every `ledger.log` ref and every reconcile wake ref of both nights. No ref gives a different answer.
- Inline: `_is_prose_ref` on the edge refs of L2. The output is quoted in L2.
- Inline, read-only: `case_runs` of the L3 case in `C:/Users/roman/rota_rv204h/tests/rota/cassettes.db`. The last 15 rows are at 11:57:50, 12:28:08 and 13:08:42, with `live = 0`, and with 2 of 5 passed in each set. The register's last row is at 14:48:11. In 14:00 to 14:48, gemma3:12b rows exist for other cases, and none for this case.
- Grep: `D:/repos/rota/.rota-gate.log`, written 14:25:15. Line 101 is `FAILED tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix] - sqlite3.OperationalError: database is locked`. Lines 93 to 102 hold 10 such reds.
- old/: `git archive 07b2cbcc` of `rota`, `tests/__init__.py`, `tests/rota/conftest.py`, `pytest.ini`, `pyproject.toml` and `rota_serial_plugin.py`, with `test_identity.py` and `test_prompts.py` from 78b9b705. `pytest -n0` gives "3 failed, 40 passed in 1.56s". At 78b9b705 the same two files give "43 passed in 1.42s".
- git: `git log 07b2cbcc..78b9b705` shows one code commit and five plans commits. The CR count is 0 in the diff and in the three files at both commits.

## (d) Usage

The harness line holds the exact figures. Estimate: about 60k input tokens, about 10k output tokens, about 70k in all. That is above the 40k cap.
