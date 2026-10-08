# Frame 178, pass 1: three refusals at the door of `findings.find`

**Record of 2026-10-08, meta workflow. The door it changes serves the rota workflow, the Architect seat.**

The door `findings_find` in `rota/roles/api.py` now refuses three calls that it wrote before (observed: `tests/rota/test_findings_doors.py`, 12 passed, 2026-10-08). The faults come from `plans/frame170-merges-read.md`, sections 1, 3 and 5.

## 1. The change

| Check | When the door refuses | What the refusal names | Helper |
|---|---|---|---|
| 1, the id | Another batch's row, stored or staged in this session, holds the id | The batch that holds the id, and one free id in the seat's own form | `_finding_holder`, `_free_finding_id` |
| 2, the grain | A `satisfied` row, or a `k0` row, has a path grain that is not a file of the diff and not a parent directory of one | The files the diff changed | `_diff_files`, the helper of the `violated` check, and `_binding_grains` |
| 3, `k0` in range | A `k0` row names a file that a constraint other than `k0` reaches | Each reaching constraint by id and the first six words of its headline, and that `k0` is for a file no constraint reaches | `_reaching_constraints`, `_constraint_heads` |

- The free id is the next number after the seat's number that no row holds: `f2` after `f1`, `f3` when `f2` is also held. An id with no number gets `_2`, then `_3` (reasoned: the brief's "the first free number").
- A seat that names its own batch's id keeps today's behaviour: the pipeline writes a new version of its own row (observed: `test_the_seats_own_id_stays_a_new_version`).
- Check 1 runs after the same-session repeat check. So a seat that sends one finding twice still gets `unchanged`, and not a refusal.
- Check 2 uses `_diff_files`, the list the `violated` check already uses. It writes no second diff reader. `_batch_diff` gives the diff text, and a grain check needs the file list, so check 2 does not call it.
- Check 3 counts every constraint that `_reaching_constraints` returns, except `k0`. A global constraint, or a constraint with no binding, reaches every file, so it also stops a `k0` row. `_bound_exit` and the push already show the same set as "the constraints that bind this diff" (reasoned: one rule for the push, the exit and the refusal).
- A grain that is not path-shaped, such as a bare symbol or a test id, passes checks 2 and 3 as today. The `violated` check keeps its exact-file rule.

## 2. The tests

`tests/rota/test_findings_doors.py` sends each recorded call verbatim to the real door through the sandbox. Each call was read from its turn in the night's database, opened `mode=ro` (observed: 2026-10-08).

| Call | Night | Refusal test | Landing test |
|---|---|---|---|
| s196 turn 1, `f1` for bg_2 while bg_1's `f1` stood | 128 | `test_s196_f1_held_by_bg_1_is_refused` | `test_s196_with_the_free_id_lands` |
| s203 turn 4, `k0` on `tests/test_defaults.py::...`, diff `termui.py` | 114 | `test_s203_grain_off_the_diff_is_refused` | `test_s203_with_a_grain_in_the_diff_lands` |
| s145 turn 2, `k0` on `src/click/__init__.py` beside 11 bound constraints | 118 | `test_s145_k0_beside_eleven_bound_constraints_is_refused` | `test_s145_k0_on_an_unreached_file_lands` |

Five more tests cover the next free id past a held one, an id with no number, the seat's own id, a `satisfied` row on a bound constraint off the diff, a bound constraint on s145's file, and a long headline.

The fixture builds a project root and one batch worktree whose commit changes the diff's files. Night 118's register is copied row by row: 13 constraints and their bindings. The tests copy each call and do not open the night database at test time. The database is not in the repository, and frame 170's tests copy their calls the same way.

No existing test of `findings_find` changed. All 234 tests of `test_t0_sandbox.py`, `test_delivery.py`, `test_developer.py`, `test_predicates.py` and `test_arc_seam.py` pass (observed: 2026-10-08). The Architect cases `L1-AR-find-against-a-constraint` and `L1-AR-a-diff-no-constraint-binds-files-k0` pass in the gate.

## 3. Out of scope: night 130's `fnd_001`

None of the three checks refuses s236's `fnd_001`, a `violated` row on merged bg_1 with the grain `inh_51d478df`: the id is free, the grain is a test id and not a path, and the row is not `k0` (observed: `.rota/clickI_night130.db`, 2026-10-08). The `violated` check also lets it through, because bg_1 has no worktree after its merge, so the diff's files are unknown.

## 4. The gate

`suite: 25 failed, 3298 passed, 35 skipped, 17 xfailed, 25 warnings`, stale 0. The worktree had no baseline, so the gate stored this run (observed: 2026-10-08).

- 7 reds are in the brief's known list: 2 L1-CR cases, `L1-CR-fail-names-its-criterion` among them, 4 L1-TS cases, and `test_map`. The watcher test is green.
- 18 reds are beside that list. Each of the 18 is also in the main checkout's stored gate baseline of 658abb63 (observed: `.rota-gate.json`, 2026-10-08): `L1-AR-cite-the-clause-into-a-constraint`, `L1-AR-constrain-an-external-commitment`, `L1-DV-fix-the-code-not-the-test`, `L1-DV-log-the-choice-the-criteria-did-not-make`, `L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`, `L1-RS-say-what-you-tried-when-you-find-nothing`, `L1-TE-amend-glossary`, `L1-TE-log-the-word-you-took-one-way`, `L1-TE-resurvey-an-area-that-moved`, `L1-VK-a-statement-on-an-existing-account-is-a-behaviour`, `L1-VK-amend-a-contested-item`, `L1-VK-an-outside-fact-is-the-researchers`, `L1-VK-answer-a-refactor-proposal`, `L3-a-challenge-reaches-the-role-that-can-answer-it`, `L3-a-failed-verdict-turns-into-a-fix`, `test_the_same_constraint_written_twice_is_one_gate`, `test_with_prompt_keeps_every_pin`, `test_a_verb_carries_words_or_does_not_regardless_of_recipient`, and no other.
- 4 of the known reds are not in that old baseline: `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`, `L1-CR-fail-names-its-criterion` and `test_map`. The three L1 cases fail on the base tree 91e76e2e with this change stashed (observed: 3 failed, 2026-10-08). So this pass did not cause them. The count of 4 is corrected in pass 2. Pass 1 named 2 of the 4 and wrote 19 for a list of 18.
- No Architect case turned red. The two Architect reds write constraints and call no `findings.find`.

## Pass 2

**Record of 2026-10-08, meta workflow.** Pass 2 answers the six findings of the diff review of af2ee732. The probes are in the session scratchpad, `review178/`.

| Finding | The change |
|---|---|
| 1, a `k0` row on a directory avoids check 3 | Check 3 gives `_reaching_constraints` the grain and every changed file inside the grain's directory. `k0` on `src/click` is now refused on night 118's register |
| 2, an empty file list refuses every grain with `one of []` | Check 2 stands down when the list is empty, as it does when the list is `None` |
| 3, check 2 reads `_diff_files` and not what the seat sees | Check 2 reads `_shown_files`: `worktrees.touched` from the batch's fork, the base that `code.diff` uses. The list holds the batch's test files and no untracked file |
| 4, 3 of 6 mutants survive | 7 new tests: a staged id of another batch, a directory grain in and off the diff, `k0` on a directory, `k0` on a `path::symbol` grain, an empty diff, a test file, an untracked file |
| 5, the free id drops the padding | `fnd_001` gives `fnd_002`, and `fnd_` gives `fnd_2`. The free id also skips an id that a row of `_ID_TABLES` holds |
| 6, a call with two faults takes two round trips | Check 1 and the same-session repeat check now run first, before the constraint check and checks 2 and 3 |

- Finding 3 reuses `worktrees.touched` and `_batch_base`. It writes no second diff reader. `touched` compares the fork with `HEAD`, and `code.diff` compares the fork with the working tree. So an uncommitted edit of a tracked file shows in `code.diff` and not in the list. The Architect reads a batch after the Developer's commit, so the gap is small (reasoned: the order of the seats).
- Finding 5's plausible part holds. The sandbox refuses an id that a row of `statements`, `items`, `tickets`, `criteria`, `tests` or `batches` holds, before the door runs (observed: `rota/core/sandbox.py`, `_ID_TABLES`, 2026-10-08). So `_free_finding_id` reads the same tables, and the new test shows `f3` when a criterion holds `f2`.
- The same-session repeat check moved up with check 1. It matches only rows this session staged, which passed every check, so the move refuses nothing new (reasoned: the rows it compares).
- The `violated` check still reads `_diff_files`. The review named no fault there, and this pass leaves it as it is.
- No existing test changed. `test_findings_doors.py` holds 25 tests, all green. The 234 tests of the other five files that call `findings.find` pass (observed: 2026-10-08).
- The review's `mutants.py` patches pass 1's text, so it does not apply to this tree. I did not run it again.

The gate of pass 2 reads `suite: 26 failed, 3310 passed, 35 skipped, 17 xfailed, 18 warnings`, stale 0 (observed: 2026-10-08). The one new red is `test_handover.py::test_a_newer_watcher_retires_the_older_one`, the watcher test of the brief's known list. The gate ran the test again, and it passed, so the gate marks it flaky. The test reads the hand-off tool and not `findings.find`. The 12 new tests are the 3310 minus 3298 passed.
