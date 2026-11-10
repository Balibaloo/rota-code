# Review of pass 1, frames 182 and 171: the base verdict of a criterion test

Worktree `C:/Users/roman/rota_p182`, commits 53f3f214 to 077a7b5f after
9a60cade. Read-only. Reviewer: a sub-agent of session 13b7eef8, 2026-11-10.

## (a) The verdict

Fix before the pick. One high finding: on dry run 8's real rows the door
refuses the right c3 test and lands the wrong one. The kind reader
`criterion_commitment` returns None on every row that rota writes today,
so every criterion is a change criterion to the door. The rest of the
pass holds. The base run restores the tree on a raise, reads the fork,
and the challenge line composes in a real wake.

The points, one line each:

1. Confirmed. `base_verdict` is the one reader of the record, and
   `record_criterion_bases` the one writer. The config key by body hash is
   the right table. `test_runs` has no test version, and the identity
   rule of `plans/composition.md` line 60 covers a key that is the body.
2. Confirmed. The planted fault is caught by one test,
   `test_tst_c1_v2_green_at_the_base_is_refused`. No scene test catches it.
3. Confirmed in the unit test. On the real rows the refusal does not fire,
   and the gap is harmful, not only incomplete. See finding 1.
4. Confirmed. The restore is in a `finally`. A raise between the put and
   the restore leaves the head tree. The run reads the fork, not the root
   HEAD. A second run sees the head tree. A kill in the window is not
   covered. See finding 4.
5. Right by construction. The printout door `_printout_literal` stands at
   line 12787, before the new door, and the new door does not touch it.
   The kept refusal still runs on a claim. See finding 5.
6. Confirmed on a real wake through the runner, the `challenged` scene.
   The Developer's answer and challenge wakes carry no base line.
7. Confirmed by the run. The scene tests what the docstring says: b1's
   red project test, the park, b2's take, and frame 135's project-id door.
   The sweep's bodies still carry the project test after the c2 check.
8. The two files: 68 passed, 4 xfailed. The related set: 440 passed,
   19 skipped, 2 xfailed, 0 failed. No test pins a run time.
9. One base run of one file costs about 1.0 s of wall time on icalendar.
   It is bounded to the one test file. Each new body runs at the base
   twice, once in the door and once in the harness pass. See finding 6.
10. Confirmed. The loose file is absent in the run and back after it, also
    after a raise. The dot folder stays. A committed new file is absent in
    the run and back after it. A separate checkout is not worth its cost
    now. See finding 4.

## (b) Findings, by severity

### 1. High. The door inverts W2 on the real rows. CONFIRMED.

`rota/roles/api.py` lines 23763 to 23797, `criterion_commitment`, and
lines 23810 to 23838, `_base_verdict_refusal`.

The kind reader has three ties, and rota writes none of them:

- The row tie asks for a `tests` row with `criterion_id = ?` and
  `commitment_id IS NOT NULL`. The one writer of `tests.commitment_id` is
  `_encode_guard`, line 11744, and it stores `"criterion_id": None`. So the
  tie never matches a row that the code writes. Only the hand-made row of
  `test_a_test_row_that_cites_a_commitment_makes_the_criterion_kept` matches.
- The surface tie asks for a commitment id in `criteria.surface_refs`. Dry
  run 8's rows hold `src/icalendar/parser/string.py::_foldline` there.
- The text tie asks for equality with the commitment's words. c3 says
  "every line is at most 75 octets long, excluding the line break".
  cw_99502ef494ad says "Lines of text SHOULD NOT be longer than 75 octets,
  excluding the line". The Terminologist paraphrases, so the tie is dead.

The probe `probe_dry8.py` read dry run 8's `final.db`: tst_c3 has
`commitment_id` NULL, c3's surface refs cite the function, and the three
commitment texts differ from c3. So c3 is a change criterion to the door.
Then `test_right_c3.py` ran the door on the fixture without the stub:

- `RIGHT_C3`, the test that splits on CRLF and is green at the base, is
  refused: "This test passes on the code before the change. A test of a
  change must fail before the change and pass after it. Write a check
  that the code as it is fails."
- `TST_C3`, the test that counts the CR and is red at the base, lands.

This is harmful. The door tells the Tester that the right test of a kept
commitment is wrong, and asks for a test that the base fails. The only
test of c3 that the base fails is a wrong one. Dry run 8's W2 was a Tester
who wrote that wrong test on its own. After this pass the door asks for
it. The same shape holds for every criterion that restates a commitment,
and that is most criteria of a change that keeps a behaviour.

Fix: make the green refusal fire only on a criterion with a recorded
kind, and record the kind at `criteria.specify` as the report proposes
(`criteria.commitment_id` from the bound list). Until the column exists,
the green refusal is a note that states the base run, not a Wall.

### 2. Medium. The row tie of `criterion_commitment` is dead code. CONFIRMED.

`rota/roles/api.py` lines 23774 to 23778. See finding 1: the one writer
of `tests.commitment_id` stores `criterion_id` NULL, line 11744. The test
at `tests/rota/test_frame182_base_verdict.py` line 173 passes on a row no
door writes.

Fix: remove the tie, or make `_encode_guard` store the criterion when a
pushed commitment also has a criterion.

### 3. Medium. An error at the base reads as the test's fault. PLAUSIBLE.

`rota/roles/api.py` line 23836: `if kept is None or verdict == "pass":
return None`. For a kept criterion a verdict of `error` falls through to
`BASE_RED_WORDS`, "The test is wrong, not the code". `_run_file` returns
`error` for a run that could not start, for a missing pytest and for a
timeout. The kept path is dead today, so the fault waits for finding 1's
fix.

Fix: return None on `error` in the kept branch, and refuse on `fail` only.

### 4. Low. The in-place swap has two windows. PLAUSIBLE.

`rota/core/harness.py` lines 728 to 796, `run_at_base`.

- A kill of the rota process between the put and the restore leaves base
  bytes in the batch worktree, and the Developer's next read sees them.
  `finally` does not run on a kill. The probe `probe_base.py` confirmed
  that a raise restores every file: the fold, the loose file, the
  committed file and the test file. A kill was not probed.
- A head change that keeps a file's size, put and restored inside one
  second, lets Python's bytecode check accept the base's `.pyc` for the
  head's source. The probe tried three rounds with a same-size change and
  did not reproduce it. The base run took 1.6 s each time, so the seconds
  differed. The window is real but narrow.

A separate checkout of the base commit would close both windows. Its
cost: the worktree's `.venv` holds an editable install of the batch
worktree, so a second checkout imports the head's source unless it gets
its own install or a `PYTHONPATH` that puts the checkout first. On
icalendar that is a `git worktree add` of about 1 s and an install of
about 10 s, once per batch. The in-place swap is the right choice for
this pass.

Fix: set `PYTHONDONTWRITEBYTECODE=1` on the base run, and write a marker
file in the worktree for the window that the next run reads and heals.

### 5. Low. The kept refusal on a claim crosses frame 360's rule. PLAUSIBLE.

`rota/roles/api.py` line 23826 skips the green refusal on a claim and
lets the kept refusal run. Frame 360's rule at lines 13241 to 13250 and
23962 says a red test on a claim stands, and its red goes to the
Developer. On a claim the base is the head, so a red kept test at the
base is the red run that disproves the claim. The new door refuses it as
"the test is wrong". The kept path is dead today, so the two rules do not
meet yet.

Fix: skip both refusals on a claim, and leave the red to frame 360's route.

### 6. Low. Each new body runs at the base twice. CONFIRMED by reading.

`rota/roles/api.py` line 23830 runs the body at the base in the door and
records nothing. `rota/core/harness.py` line 199 runs it again in the
harness pass and records it. On icalendar one run of one file is about
1.0 s of wall time (`_run_one` on bg_1, three runs: 1.02, 0.93, 0.93 s).
The run is bounded to the one file: `_run_one(root, rel, ...)`. The git
calls add one `diff`, one `ls-files` and one `show` per changed file.

Fix: let the door write the record it ran, and let the harness pass skip
a body whose hash is on record.

### 7. Low. The challenge line says "red" for a collection error. CONFIRMED.

`rota/core/runner.py` line 3727. The `challenged` scene's Tester wake
reads "t1: at the base this test is red. The base run ended with: 1
error". The base has no `src.billing.upgrade`, so the error is right for
a change test. The word "red" hides the difference between an assertion
and a missing module.

Fix: say "errors" when the record's result is `error`, and keep "red"
for `fail`.

### Outside the points

- `record_criterion_bases` returns before its write when `run_at_base`
  returns None for one test, line 826. The conditions for None do not
  depend on the test, so the loss is theoretical. Low.
- The `criterion_base:` key is never removed. The `base_run:` key has the
  same life. Low.
- `_encode_guard` gets no base door. A guard test red at the base is W2's
  shape. The report names it.

## (c) Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/13b7eef8-9ba8-4251-a72e-fd3511e65682/scratchpad/f182probes/`.

- `fault_plugin.py`: a pytest plugin that makes `_base_verdict_refusal`
  return None on `BASE_GREEN_WORDS`. Run with `-p fault_plugin` on the new
  test file and `test_scene_two_batches.py`: 1 failed, 67 passed, 4
  xfailed. The one red is `test_tst_c1_v2_green_at_the_base_is_refused`.
- `probe_base.py`: a fixture repo with a base fold and a head fold. A
  raise in `_run_one` restores every file. The run sees the base tree,
  with the loose file and the committed new file absent and the dot folder
  present. The base stays the fork after the root commits. Three rounds of
  a same-size head change show no stale bytecode.
- `probe_wake.py`: builds the `challenged` scene and reads the Tester's
  message wake. The line "t1: at the base this test is red. The base run
  ended with: 1 error" is in the prompt.
- `probe_dry8.py`: reads dry run 8's `final.db` read-only. c1, c2 and c3
  with their surface refs, tst_c1 and tst_c3 with `commitment_id` NULL,
  and the three commitments.
- `test_right_c3.py`: the door on c3 without the stub. `RIGHT_C3` is
  refused as green at the base. `TST_C3` lands.
- Timing: `harness._run_one` on
  `D:/repos/_AI/sample_repos/icalendarI/.rota/worktrees/bg_1`, the file
  `src/icalendar/tests/test_foldline_75octets.py`, three runs: 1.02 s,
  0.93 s, 0.93 s wall. pytest reports 0.30 s warm and 2.14 s cold.

## (d) The counts and the time

- `tests/rota/test_frame182_base_verdict.py` and
  `tests/rota/test_scene_two_batches.py`, `-n 0`: 68 passed, 4 xfailed in
  80 s.
- `tests/rota -k "encode or harness or challenge or base or
  tests_missing"`, `-n 0`: 440 passed, 19 skipped, 2 xfailed, 0 failed in
  256 s.
- One base run on icalendar: about 1.0 s wall for one test file.

## (e) What I did not read

- Whether the scheduler runs `do:harness` while a Developer session is
  live on the same batch. The swap window of finding 4 matters only then.
- `_bound_rows` and the Terminologist's `criteria.specify` door, the home
  of the fix for finding 1.
- The Developer's challenge and answer wakes beyond the grep that shows
  `_base_verdict_lines` is called for the Tester only.
- The gate. The brief did not ask for it.

## (f) Usage

Input tokens: about 100k. Output tokens: about 14k. Total: about 114k.
