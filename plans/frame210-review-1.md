# Frame 210, review 1: commit a2b70a84, a test's latest run in the batch that asks

Reviewer: Opus, read-only, on the worktree `C:/Users/roman/rota_rv210` at a2b70a84. Date: 2026-10-12. Rota workflow code, reviewed for the meta workflow.

Verdict: the pass stands. No finding is high. Three findings are low, and one finding is outside the points.

## (a) Verdicts on the points

1. The six changed readers: each one binds the run to the test's batch, and no reader loses a run that it needs. Stands.
2. The three readers left: `exhausted`, `tests_failing` and `failing_attempt` do not change behaviour on the night's shape. Stands.
3. The night: at a2b70a84, `tests.load` for bg_2 shows 33 passing and 2 failing, with their output. At c18f868c it shows 35 of 35 passing. Confirmed.
4. The test: it fails at c18f868c on the night's cause and passes at a2b70a84. The plain row is equal for `tests.load`. The test covers one of the six readers only. Stands, with finding 2.

### Point 1 in detail

- `tests_load`: the outer query holds `t.batch_id = ?`, so `batch_id = t.batch_id` is the batch that asks.
- `_challenge_evidence`: `tr.batch_id = t.batch_id` and `GROUP BY batch_id, test_id` give the newest run of the asking batch. Before the fix, a test with a newer run in another batch dropped out of the list.
- `_test_is_red`, `_bind_send.stage`, `_resolve_refs` and `check_line` bind to `tests.batch_id` and not to the asking batch. Rota runs one batch at a time, and `lifecycle.start` calls `harness.inherit` again on a resume. So `tests.batch_id` is the running batch in every case I found.
- The case the point asks for: the test's row cannot belong to the earlier batch while the new batch runs. `harness.inherit` moves the row inside `lifecycle.start`, before the first session of the new batch.
- The one window that changes: after the inherit and before the new batch's first harness run, every bound reader finds no run. Before the fix, the readers showed the earlier batch's last run. The new answer, "Not run yet", is true. The base run sits in `config`, and frame 207's sentences read it there. See finding 1.

### Point 2 in detail

- `exhausted` (`rota/core/predicates.py:995`): the newest row per test is global. On night 141, bg_2's rows 72 and 80 are newer than bg_1's rows 37 and 45. So bg_2's attempt counts, which is correct. In the window before bg_2's first run, the newest row is bg_1's pass, and bg_1 is merged, so nothing fires. See finding 3 for a deferred batch.
- `tests_failing` (`rota/core/predicates.py:923`): the same global pick, with a join on running batches. bg_1's merged rows never wake a seat. No change.
- `failing_attempt` and `park_reds` (`rota/core/scheduler.py:1565`, `:1599`): both bind the outer query and the subquery to one batch. No earlier batch's run reaches a seat.

## (b) Findings

1. `rota/core/sandbox.py:1590`, `rota/core/runner.py:2204`, `rota/roles/principal.py:518`, `rota/core/sandbox.py:2474`. Low. PLAUSIBLE. These four readers bind to `tests.batch_id`, not to the batch of the session that asks. The two agree while one batch runs and the inherit moves the row at start. A future change that runs two batches at once, or that skips the inherit on a resume, makes the readers show another batch's run again. Fix: pass the asking batch where the caller has one, as `_challenge_evidence` and `tests_load` do.
2. `tests/rota/test_developer.py`, the new test. Low. CONFIRMED. The test covers `tests.load` only. The other five changed readers have no case, and a revert of any one of them stays green. The plain `pending` row in b2 gives the same end state as `harness.inherit`, which writes `INSERT OR REPLACE` with the new batch id. So the plain row does not make the `tests.load` check weaker. Fix: add one row-level assertion for `_test_is_red` and `check_line` on the same three runs.
3. `rota/core/predicates.py:995`, `exhausted`. Low. PLAUSIBLE. The predicate has no batch status filter, and it picks the newest row per test across batches. A deferred batch at the cap whose inherited test moves to a new batch keeps its red as the newest row until the new batch runs. The ladder can then wake for the deferred batch. Night 141 does not have this shape. Fix: a frame of its own, as the pass report asks. Join `batches` on `status = 'running'`, as `tests_failing` does.
4. Outside the points. `rota/tools/invariants.py:139`, `i4`. Low. CONFIRMED. I4 says "a run row's test is a test of the run's batch". On the night copy, I4 reports 34 findings: bg_1's runs of 34 inherited tests that now belong to bg_2. The frame's fix accepts the shape that I4 calls a violation. So I4 reports every inheriting night as broken, and `i3` misses the inherited tests of a merged batch. Fix: decide in a frame whether `tests` keys by batch and id, or whether I4 allows a run of an earlier batch that the test came from.

The gate did not run on the pass, and the acceptance gate is still owed. The two-batch scene tests pass at a2b70a84: 36 passed, 1 skipped, 1 xfailed. The scene `merged_then_next` inherits the same `inh_` ids into b1 and b2, so the gate's stale line is the check for a changed prompt.

## (c) Probes

All probe files are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/91506043-2ba0-4cdf-b0eb-d1a00b7bca68/scratchpad/rv210/`.

- `night141_copy.db`: a backup of `clickI_night141.db`, read through `mode=ro`.
- `c18/`: `git archive c18f868c`, extracted, with a2b70a84's `tests/rota/test_developer.py` copied in.
- `probe_load.py` and `probe_load.out`: `api.tests_load` for bg_2 on the copy, at both trees. a2b70a84: 35 rows, 33 pass, 2 fail, `said` holds the pytest output, `raised at` is `tests/test_utils/test_confirm.py:49`. c18f868c: 35 rows, 35 pass.
- `probe_test.out`: the new test at both trees. a2b70a84: 1 passed. c18f868c: `AssertionError`, `'last_result': 'pass'`.
- `probe_scene.out`: `test_scene_merged_then_next.py`, `test_scene_merged_then_next_again.py` and `test_invariants.py` at a2b70a84. 36 passed, 1 skipped, 1 xfailed in 80.21s.
- `probe_i4.out`: `invariants.i4` on the copy. 34 findings.

## (d) Usage

Estimate: about 45k input tokens, 9k output tokens, 54k in all. The harness line holds the true count.
