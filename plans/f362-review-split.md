# Frame 362, review of pass 4 and 4b: the door shape and the split of the survey wake

Worktree `C:/Users/roman/rota_r362s`, detached at `2e242d81`. The worktree has no tracked change. I ran no live model and no gate.

## 1. Verdict

**Fix.** The split is right, but the project-wide fill must change before the slice ships. The count is 1 high, 2 medium and 3 low.

- High 1: in the commitments mode, a project-wide line binds every file of each area that states it. On icalendar, one line gets up to 422 binding rows, and the harvester holds 84 rows for that line.
- Medium 1: the twin-guard exemption skips every row that has no witness, so the guard also lets through a decided constraint that contradicts the statement.
- Medium 2: `exported-name` is red at `f7d7d787`, but the prompt text is not the cause. The system text changed.

| Point | Verdict |
|---|---|
| 1 Wake condition | Stands. The wake has the same condition as the old push. No wake is empty. The cut lines and the lines of a quarantined area get no push, as before. |
| 2 Door fills | Stands for a placed line. Fix for a project-wide line (high 1). |
| 3 Twin exemption | Fix. A contradicting decided constraint gets through (medium 1). |
| 4 Survey prompt restore | Stands for the prompt. The case count is six, not five. The red has a different cause (medium 2, low 1). |
| 5 Three optional arguments | Hide the three arguments in the survey mode. A `.tools` file cannot narrow an argument. |
| 6 Four new cases | Stand, with one gap: the key does not measure each line or a refusal (low 2). |
| 7 Critic fixture seed | Stands. |
| 8 Mode default | Stands. Production never reaches the default. |
| 9 Consumers | Stands. The two modes write the same row, except the headline and the text. |
| 10 Suite | 6488 passed, 0 failed, 265 skipped, 13 xfailed. The pass reported 6479 passed and 9 failed, so 6479 + 9 = 6488. |

## 2. Findings by point

### Point 1, the wake condition

The commitments wake fires when `witness_push(conn, area)[1]` holds text (`rota/core/scheduler.py:1153`). The survey push before `d80718d4` carried `[model.witnesses]` on the same condition: `model_witnesses` returns the text of `witness_push(ctx.conn, ctx.area)` (`rota/roles/api.py:3989-3992`). So the condition is the same. CONFIRMED by reading.

- No area gets a wake with nothing to state. An area that has only lost ties gets a wake whose push says "No line below can restate it, so decline it" (`rota/roles/api.py:3945`). The only act of that wake is an attest, and the old survey push showed the same text.
- These witness lines get no push. The cut drops project-wide lines first (`rota/roles/api.py:3966-3975`). On icalendar, `src/icalendar/prop` shows 0 of its 17 project-wide lines, and `src/icalendar` and `src/icalendar/parser` show 12 each. An area whose Architect survey is quarantined has no fresh survey record, so it gets no commitments wake (`rota/core/scheduler.py:1144-1148`). Both gaps existed before the split.
- 9 of the 20 icalendar areas get a commitments wake (probe 2).

### Point 2, the door fills

The headline is `<witness path>: <behaviour>` (`rota/roles/api.py:4162-4168`). The id comes from the witness key through `_statement_id` (`rota/roles/api.py:4090`). A shift of the line keeps the id, as pass 2c asks. A placed line binds only its placed files in the surveyed area (`rota/roles/api.py:4057-4060`), as pass 3b asks. CONFIRMED by probe 4: the commitments mode and the survey mode write the same id, witness key, binding and `is_global`.

**High 1. A project-wide line binds every file of the area.** At `rota/roles/api.py:4061-4065`, the door sets `placed = sorted(area_files)`. `_area_files` returns every grain path of the area (`rota/roles/api.py:3796-3799`), which includes test files and data files. Each area that states the same line adds its own files to the one row. CONFIRMED by probe 2 on icalendar at `99619246`:

- The harvest holds 17 project-wide lines. Each one has 84 `candidate_bindings` rows, and all 84 are `.py` files outside `tests/`.
- 12 of the 17 lines reach 8 areas through the push. One statement in each of those areas gives 422 binding rows. 316 of the 332 files in `src/icalendar` are under `tests/`, and 160 are `.ics` files.
- The 3 `pyproject.toml` lines (13, 58 and 80) and 2 `parse-errors.rst` lines reach 6 areas and get 85 rows. The cut drops these lines in `src/icalendar`, so the 85 rows do not include the core modules that the harvester binds.
- So the binding is wider than the harvester binding, because it includes tests and data files. It is also narrower, because it leaves out the files of every area where the push cut the line. The push cut decides which files the line binds, and the code does not. Ruling 3 makes each bound file a merge stop.

Fix: state a project-wide line once, in the `.` area, and bind its `candidate_bindings` rows with rule `project_wide`. Drop project-wide lines from the push of every other area.

### Point 3, the twin-guard exemption

**Medium 1.** The exemption at `rota/roles/api.py:4317` skips every row that has an empty `witness`. That includes survey surfaces, but also decided constraints and every constraint that a statement did not write. The guard exists for the contradicting twin (`rota/roles/api.py:4285-4293`). CONFIRMED by probe 3. A row `src/pkg/fold.py: a folded line holds at most 80 octets` with no witness was present, and a statement of "at most 75 octets" landed in the commitments mode. The same statement in the survey mode was refused with "k_other already governs this subject". A surface that states the same promise also gets through, and that is the case the deviation intends.

Fix: skip only the rows that the Architect survey of this area wrote, for example rows with no party whose headline has the `path::symbol` form. Keep the guard for every other row.

### Point 4, the survey prompt restore

`git diff 5bf2815 2e242d81` on `survey.md`, `survey.tools` and `survey.base.md` is empty. Every change that passes 2b and 2c made to the survey prompt was about witnesses: the `[model.witnesses]` paragraph, the two "except a witness line" clauses and the `model.witnesses` tool. So the prompt lost nothing that is not about witnesses. The composed brief hashes to `f7d7d7874ad4ccf3` (probe 5). CONFIRMED.

The register (`tests/rota/cassettes.db`, read with `mode=ro`) has six `L1-AR-survey-*` cases, not five.

| Case | Last green: prompt hash, system hash, time |
|---|---|
| a-patch-seam | `f7d7d787`, `41eb77dc`, 2026-11-04T00:41:50 |
| a-shared-helper | `f7d7d787`, `41eb77dc`, 2026-11-04T00:41:51 |
| a-signature-callers-rely-on | `f7d7d787`, `41eb77dc`, 2026-11-04T00:41:48 |
| an-exception-contract | `ee6a03fe`, `d4d564d7`, 2026-11-04T02:55:25. It was also green at `f7d7d787` until 00:41:49. |
| an-exported-name | `bc13ca5a`, `206cf148`, 2026-11-04T06:54:56. At `f7d7d787` it has 509 green rows and no red row. The last one is at 2026-11-04T00:41:52. |
| an-area-for-its-commitments | `bc13ca5a`, `206cf148`, 2026-11-04T06:54:19 |

**Medium 2. The red of `exported-name` comes from the system text, not the prompt.** All five 4b runs in `g5_live.db` have prompt `f7d7d787` and system hash `4469455e`. The green runs had system hash `41eb77dc`. The prompt is the same, so the change is in the system text: the session prose, the `TOOL:` lines or the signatures. The `model.amend` signature with its three optional arguments is in that text (point 5). The hashes are CONFIRMED. The cause is PLAUSIBLE. Fix: diff the system text of `41eb77dc` against `4469455e` before any change to a sentence.

**Low 1.** The pass measured four survey cases. It did not run `an-exception-contract` or `an-area-for-its-commitments` on the restored prompt, and both are stale through the prompt hash. Fix: add both cases to the next live measure.

### Point 5, the three optional arguments

A `.tools` file narrows functions only. `mode_tools` returns a list of function names (`rota/roles/prompts.py:135-152`). `guess.tools` lists four functions and narrows no signature. So a hide of the three arguments needs a new seam. The sandbox already has a mode-keyed seam for `model.amend` (`rota/core/sandbox.py:568`). The rendered signature would need the same key.

- The door refusal is the smaller change in code. It does not change the system text. But the model still sees the three arguments. The cold load still fills them, and the split brief measured that the model does not recover from a refusal.
- The hide changes only the system text of survey-mode wakes. All six survey cases are stale already through the prompt hash, so the stale set grows by no case. The hide also removes cause 8, and it can bring the system text back to the green `41eb77dc` (medium 2).

Recommendation: hide the three arguments in the survey mode. The two stale sets are equal, and only the hide removes the cause. PLAUSIBLE until a diff of the system text shows the result.

### Point 6, the four new cases

The fixture shape matches the survey cases: `runs: 1`, `pass: 1`, `repo: {onboard: true}`, `tick_unseedable` and `refs` (`tests/rota/cases/l1_survey_spike.yaml:136-206`). The key requires one survey record, 1 to 9 constraints, one row with `"is_global": 0`, and `party`, `behaviour` and `witness` on every written row (`rota/testkit/fixtures.py:726-735`). The door writes a witness only for a pushed id, so a non-empty witness is a pushed id.

**Low 2.** The key does not count lines. A run that states 1 of 5 pushed lines passes. The key also does not measure a refusal: the store case passed 5 of 5 with 3 refused calls in each run. Only the unit test `tests/rota/test_f362_commitments.py:771` measures the refusal of a call that has no id. Fix: compare the constraint count with the count of pushed lines, or record the refusal count as a problem.

### Point 7, the Critic fixture seed

The green case `L1-CR-a-kept-behaviour-passes-by-its-kept-line` seeds `head_commit: HEAD` and a `test_runs` row at `HEAD`, with a repo (`tests/rota/cases/l1_judgement.yaml:328`, `:336-338`). The changed case uses the same form (`:244`, `:253`). The key still requires a fail with `failed_commitment` set to `<k1>`. The door adds the witness quote to every landed commitment fail through `_commitment_reason` (`rota/roles/api.py:17379`). So the case measures what ruling 3 asks. CONFIRMED by reading.

### Point 8, the mode default

`_wake_mode_key` (`rota/roles/api.py:7159`) is the reader. Its callers are `rota/core/sandbox.py:568` and `:5651`, and `rota/roles/api.py:2024`, `:4008`, `:4162`, `:4317` and `:5525`. The default applies only to a context that has no wake and no `mode`. The production `Ctx` has `mode: str = "normal"` (`rota/roles/api.py:51`). The one production `SimpleNamespace` context (`rota/roles/principal.py:4266`) calls only `_stage_fault`. The stub `Ctx` in `tests/rota/test_survey_evidence.py:44` has no `mode`, and `surveys_attest` now reads the mode at `rota/roles/api.py:5525`. That stub explains the nine reds. The file passes at `2e242d81`. CONFIRMED by reading and by the run.

### Point 9, the consumers

`test_f362_consumers.py` and `test_f362_commitments.py` gave 85 passed, with `test_survey_evidence.py` in the same run. No consumer test writes its row through the commitments mode. So probe 4 compared one landed row from each mode. Both rows have id `cw_40fbbc34cda8`, witness `wk_40fbbc34cda8`, `is_global` 0 and the binding `src/pkg/fold.py`, and `stated_commitments` reads both with a line. Only `headline` and `text` differ. CONFIRMED.

### Point 10, the suite

`tests/rota`, with `ROTA_DEV_DB` on a scratch file and `ROTA_MODEL=qwen3:8b`, gave `6488 passed, 265 skipped, 13 xfailed` in 362 s. 6479 + 9 = 6488, so the nine reds are now green and no new red appeared.

### Outside the points

- **Low 3, outside.** Two readers take the record `commitments:<area>` for the survey of a role. `surveys_consult` (`rota/roles/api.py:5648`) splits the id prefix, so `commitments` shows in `surveyed_by` as a role. `compare._areas` (`rota/compare.py:77`) maps each area to one outcome, and the commitments row can overwrite the survey outcome. CONFIRMED by reading. Fix: leave out ids that start with `commitments:` in both readers.
- **Outside, PLAUSIBLE.** Each call of `onboarding_phase` now calls `_commitment_wakes`, which calls `witness_push` for each surveyed area (`rota/core/scheduler.py:1054`). Nobody measured this cost on a large run. No fix line until a measure.

## 3. The project-wide question

Counts on icalendar at `99619246` (probe 2):

| Line | Areas whose push shows it | Rows that the mode binds | Harvester rows |
|---|---|---|---|
| 12 lines: `README.rst` 99, `api-design.rst` 61 and 10 `custom-components.rst` lines | 8 | 422 | 84 |
| `pyproject.toml` 13, 58, 80 and `parse-errors.rst` 94, 97 | 6 | 85 | 84 |

The pinned tree has no project-wide `pyproject.toml` line 42. The `pyproject.toml` lines are 13, 58 and 80.

State a project-wide line once, at the root, with the harvester bindings. The reasons:

- The harvester already decided the reach: 84 source files, with no tests and no data files.
- One statement gives one decision. Eight sessions that state one line with eight different behaviours amend one row eight times.
- The push cut no longer decides the reach.

The costs:

- The `.` session gets 17 project-wide lines and 2 placed lines in one push, so the cut applies there.
- The other eight sessions lose their project-wide rows. `src/icalendar/prop` still has a wake for its placed lines.
- The scenes and the four new cases need a change, because every scene area has a project-wide witness (deviation 6 of the pass). The four cases re-record.
- A row with 84 bindings still reaches every diff of a source file. Ruling 3 decides whether a project-wide line is a merge stop. This review does not answer that question.

## 4. Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/9f60e445-30b5-431b-b448-1ab48919fbaf/scratchpad/`.

1. `r362s_pw.py` read `f362_probe_ical.db` read-only. It found 17 project-wide lines, each with 84 bindings.
2. `r362s_areas.py` built `r362s_ical.db` from `D:/tmp/rota-live/icalendar` at `99619246`. It ran the indexer, the area pin and the harvest. Then it called `witness_push` and `_area_files` for each area.
3. `r362s_twin.py` used the fixture of `test_f362_commitments.py` with one row that has no witness. It sent the call in both modes.
4. `r362s_rows.py` landed one statement from each mode and compared the rows.
5. A `python -c` call hashed `prompts.compose("architect", "survey")` and `"commitments"`. The hashes are `f7d7d787` and `65a382fe`.
6. `python -c` calls read `case_runs` of `D:/repos/rota/tests/rota/cassettes.db` with `mode=ro`, and `case_runs` of `g5_live.db`. Each call took less than two minutes.
7. One pytest call ran the three test files. One pytest call ran the full `tests/rota` with `ROTA_DEV_DB=r362s_dev.db`.

## 5. Usage against the cap

About 100k tokens of input context and about 15k tokens of output, so about 115k in total. The cap was about 70k. The reads of `api.py` and of the cassettes history caused the overrun.

## Second look, passes 4c to 4e

Worktree `C:/Users/roman/rota_r362s`, detached at `c0ced085`. The worktree has no tracked change after the run. I ran no live model and no gate.

### (a) Verdict

**Fix.** Six of six earlier findings are fixed, and each has a test. The count of new findings is 3 high and 1 low. The suite gives 6500 passed, 0 failed.

| Point | Verdict |
|---|---|
| 1 The six findings | Stands. All six are fixed. The outside cost note stays open, with no measure. |
| 2 Root wake | Fix. The wake fires once and closes. A new harvest with a new project-wide line does not wake it again (high A). |
| 3 Offer check | Fix in part. The piece is generic. The scalar door still offers a call that the same door refuses (low D). |
| 4 Hide and drop | Fix. The note and the other modes hold. The drop breaks the restate form of a lost line (high C). |
| 5 Tester header | Fix. A batch that nothing binds gets no commitment sentence. A batch that only a survey surface binds gets the ask (high B). |
| 6 Suite | Stands. 6500 passed, 265 skipped, 13 xfailed, 0 failed in 360 s. 6497 + 3 new tests of pass 4e = 6500. |

### (b) Findings

Point 1, the six findings:

- High 1, the project-wide binding: fixed. Tests: `test_one_session_states_the_project_wide_lines`, `test_the_root_binds_the_harvester_rows_of_a_project_wide_line`, `test_a_project_wide_line_is_not_in_the_push_of_an_area`, `test_a_surveyed_area_that_holds_only_project_wide_lines_gets_no_wake`.
- Medium 1, the twin exemption: fixed. Test: `test_a_decided_row_that_contradicts_the_statement_is_its_twin`, in both modes.
- Medium 2, the system text: fixed. The survey text is `41eb77dc` again. Test: `test_the_survey_signature_hides_the_three_statement_arguments`. The exported-name rate stays 1 of 5, and pass 4d shows the same input byte for byte.
- Low 1: fixed. Pass 4c measured both cases, 5 of 5 each.
- Low 2: fixed. Test: `test_the_witness_key_counts_the_lines_stated_and_the_refusals`.
- Low 3: fixed. Test: `test_a_commitments_record_is_no_role_survey`.

Point 2, the root wake. On a tree with no project-wide line, `any(...)` is false, so no root wake comes. On a tree with no git, `boot` harvests with commit `""`. `project_wide_witnesses` reads no commit, so the root wake comes as on a git tree.

**High A. The root record closes the root wake for good.** `rota/core/scheduler.py:1166-1171` checks only that the record `commitments:@project-wide` exists. An area wake reads the area hash, but the root wake reads no hash. CONFIRMED by probe 1: after the record, one new project-wide line was unstated, and `_commitment_wakes` returned `[]`. So `onboarding_phase` also leaves the survey phase with the line unstated. Fix: wake the root while any project-wide line has no statement, or store the hash of the stated keys in the record and compare it.

Point 3, the offer check. `_offer_checked` (`rota/roles/api.py:323`) takes any tuple of checks, so a third door can use it with no copy. `_exist_check` (`:348`) reads only a literal `_must_exist(ctx, "<table>", <name>)` in the op body, so a call in a helper or through a renamed variable is not seen. It passes a real id of the wrong table, as pass 4d says.

**Low D. The scalar door offers a call that the same door refuses.** At `rota/core/sandbox.py:433`, the offer fixes the first scalar word only, and the loop returns. The offer does not go through the later scalar arguments or the enum check. CONFIRMED by probe 2: `code.source(start='top', end='bottom')` offers `start=1, end='bottom'`, and the resend is refused on `end`. `brief.segment` and `code.write` have the same shape. Fix: convert or replace every scalar word before the offer, then run the enum check on the offer as one more check.

Point 4, the hide and the drop. The note names only the sent arguments. A positional headline is bound before the drop, so it is dropped and named too (probe 1). The survey mode keeps the binding guard: `bindings=["Account"]` is refused with "Account is not a grain in the index" (probe 1). The tests are `test_the_commitments_door_drops_a_binding_and_a_headline_and_says_so` and `test_a_dropped_argument_keeps_the_witness_refusals`. No test pins that another mode keeps a binding refusal. Probe 1 shows it.

**High C. The drop breaks the restate form of a lost line.** The twin refusal at `rota/roles/api.py:4442` says "Restate it: write model.amend(headline=...)". The push of a lost row at `:4050` gives the same form. The commitments mode drops `headline` (`rota/core/sandbox.py:594`) and writes `<path>: <behaviour>`. A restatement with new behaviour words gets a new headline, and the guard refuses it again. CONFIRMED by probe 1: the literal follow of the refusal was refused with the same text. The lost row stayed alone. Before `fe491e81`, the seat's headline passed through. Fix: in the commitments mode, give the restate form without `headline`, and let the door take the lost row's id when the new witness restates it.

Point 5, the Tester header. The paragraph is gone from `tests_missing.md`, and no Tester prompt file holds the word "commitment". An empty touch gives no block, and a batch with no bound row gets the note "No constraint binds the files of this batch", with the plain header.

**High B. The ask reaches a batch that no commitment binds.** `bound_key` (`rota/core/runner.py:4220-4223`) picks the Tester header for any non-empty list. `bound_constraints` (`rota/roles/api.py:4771-4778`) lists every reaching constraint, which includes survey surfaces, decided rows and constraint zero before all areas are surveyed. So a batch that only a surface binds gets "Write a test that guards each pushed commitment ... Send the commitment's id as `criterion_id=`". Gate 5 measured that this sentence costs one of the two one-per-reply cases. CONFIRMED by reading. Fix: pick the Tester header only when one row of `bound` has a `witness` and a `party`.

Point 6, the suite. `tests/rota` with `ROTA_DEV_DB` on a scratch file and `ROTA_MODEL=qwen3:8b` gave `6500 passed, 265 skipped, 13 xfailed`. It names no red. The handover timing red of pass 4d did not come back.

Outside the points:

- Outside, PLAUSIBLE. `onboarding_phase` now also calls `project_wide_witnesses`, and so `stated_commitments`, on each call (`rota/core/scheduler.py:1058`, `:1170`). Nobody measured the cost on a large run. No fix line until a measure.

### (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/9f60e445-30b5-431b-b448-1ab48919fbaf/scratchpad/`.

1. `test_r362t_probe.py` used the `tree` fixture of `test_f362_commitments.py`. It checked the root wake after a new line, the survey binding guard, a positional headline, and a restate of a lost line in the commitments mode.
2. `r362t_scalar.py` listed the ops with two scalar arguments. `r362t_offer.py` sent `code.source` two scalar words and re-checked the offer.
3. One pytest call ran the full `tests/rota` with `ROTA_DEV_DB=r362t_dev.db`.

### (d) Usage

About 90k tokens of input context and about 12k tokens of output, so about 102k in total. The cap was about 50k. The reads of the three pass reports and the probe cycles caused the overrun.
