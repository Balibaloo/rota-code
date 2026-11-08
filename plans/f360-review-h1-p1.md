# Review of frame 360, slice 2, pass 1 of H1: commits 045a01e8 to 3e068983

Verdict: fix. The pass is sound on the eight points, with 0 high, 1 medium and 9 low findings. The medium finding has a one-line fix: the door turns each CR LF of stderr into LF before the record. The worktree `C:/Users/roman/rota_r360h` is clean at `3e068983` after the revert of the planted fault.

## (a) The verdict on each point

1. One writer: holds. The map and a grep name `code_run` (`rota/roles/api.py` 24738) as the one writer in `rota/`. Only test fixtures write the table directly.
2. The four refusals: hold. Tests cover A1 to A4 and the four refusals, and an import-bound name is exempt. The report does not state the renamed-copy limit. The code docstring states it (finding 4).
3. The wake order and the hold: hold. A diff gets no `tick:claim`, and one ended session or one row settles the claim. A real commit ends the claim and the hold. A quarantined claim wake is a plausible gap (finding 8).
4. The bytes: stdout holds, stderr does not. The stdout row keeps CR LF, and the sentences show ⏎, ↵ and "(cut)". The stderr row loses CR LF (finding 1).
5. The worktree: holds for tracked and untracked files. The program runs under `.rota/claim_run` with a timeout of 60. The door puts back a write into `src/` (test and probe). Ignored files and `.rota/` files stay (finding 3).
6. The P1 door: holds. The door refuses a pass on a test claimed `encodes = False` in the session, with the quoted sentence. The control test flaw is real, and the pass does land (probe, finding 5).
7. `_built_words`: holds. No principal text in `principal.py` or `api.py` says that the tests check a claim. Two seat-facing sentences still say it (finding 9).
8. The measure: open, as the report says. No recorded case holds a claimed batch with a `claim_runs` row. The 8 stale cases are no evidence about this change (finding 6).

## (b) Findings

1. `rota/roles/api.py` 24722. Medium. CONFIRMED: a program wrote "one", CR LF, "two", CR LF to stderr, and the row held "one", LF, "two", LF. `Path.read_text` decodes with universal newlines. The brief asks for stderr as the program wrote it. Fix: read `err_file.read_bytes()` and decode it with no newline translation.
2. `rota/roles/api.py` 24616. Low. CONFIRMED: `vars(s)["_foldline"] = lambda line: "patched"` passed all four refusals, and the run printed "patched". The door checks no subscript target and no `sys.modules[...]`. Fix: refuse a subscript store on `vars(<touch module>)`, `<module>.__dict__` and `sys.modules`, or state the gap beside the renamed-copy limit.
3. `rota/roles/api.py` 24727 and 24734. Low. CONFIRMED: a program wrote `build/left.txt` (ignored) and `.rota/left.txt`, and both stayed. The note said nothing. `worktrees.discard` skips `.rota/`, and git status omits ignored files. Fix: list `git status --ignored` and `.rota/` before the run, and remove the new paths after it.
4. The report of the pass (`f360_h1_p1_report.md`). Low. CONFIRMED: the word "renamed" is absent from the report. The docstring of `_claim_program_fault` says that a renamed copy beside a real call passes. The brief asked the report to say it. Fix: add one sentence to the report or to the pass 2 report.
5. `tests/rota/test_f360_h1_claim_run.py` 578. Low. CONFIRMED: the control checks only that the first refusal is not the no-encode one. A probe landed the same pass with the `_land` helper of `test_critic_kept_route.py`, and the row held the routes `added` and `test`. Fix: land the pass in the control with `_land(sb, lines)`.
6. The report, section (b), items 4 and 5. Low. CONFIRMED: the register of the implementer, `C:/Users/roman/rota_p360h/tests/rota/cassettes.db`, holds 0 cassettes. The 8 stale ids are exactly the recorded case ids that `-k` matches. So these cases are stale at any commit, and "the same at the base" proves nothing. A second probe composed the system prompt and the mode tools of all 197 cases at the base and at the head. No case changed, so the change adds no stale case at that level. Fix: say in the report that the register was empty, and cite the compose comparison or a gate.
7. `rota/roles/api.py` 23189 and `rota/core/predicates.py` 1046. Low. CONFIRMED by a probe, reach PLAUSIBLE: a run row at an old head settles a later claim at a new head. The Tester then reads the old run, because no reader reads `commit_sha`. The claim door sets a claim only on a batch with no head, so no path reaches this today. Fix: none now. Read `commit_sha` if a second claim on one batch becomes possible.
8. `rota/core/predicates.py` 1046. Low. PLAUSIBLE: `claim_settled` reads only `claim_runs` and the `sessions` rows. The attempt cap can quarantine a `tick:claim` key before any session row exists. Then `tests_missing` stays held, and the Tester never wakes on the batch. Fix: count a quarantined `tick:claim` key of the batch as settled.
9. `rota/roles/api.py` 26939 and `rota/core/predicates.py` 1029 to 1031. Low. CONFIRMED by grep. The note to the Developer says "The Tester’s tests check the claim." `CLAIM_DETAIL` tells the Tester "Your tests decide the claim." Both are seat-facing and outside point 7. The run of the Architect is now evidence too. Fix: name the run in both sentences in pass 2.
10. Outside the points: `claim_printout` (`rota/roles/api.py`, about 23201). Low. PLAUSIBLE: the mark " ⏎ " puts a space on each side. A split shows as "wo ⏎ rds", and a correct fold shows as "words  ⏎ are". The two forms differ by one space, and the first count of the design depends on that difference. Fix: the case of the measure holds both forms, and the count says which form the Tester saw.

### The measure of point 8

A Tester L1 case can measure the count. The case has these parts:

- A claimed batch with `claimed_head = head_commit`.
- A `claim_runs` row whose stdout holds the A3 printout: "wo", CR LF, a space, "rds".
- The `tests_missing` wake of the Tester on the batch.

The expectation is a `tests.write` whose assert says that no word is split at the fold. The A3 fixture of `test_f360_h1_claim_run.py` (`_a3_on_record`) builds this state. No case YAML holds it, and the `claim` mode of the Architect has no case either. A gate with the full register re-records only the stale cases that it finds. The compose comparison found no change of a system prompt, so the stale set of the gate equals its stale set at the base.

### The planted fault

I changed the row value of stdout in `code_run` from the bytes to their utf-8 decode. The two test files then gave `2 failed, 54 passed`. The red tests were `test_a2_is_accepted_and_the_row_holds_the_exact_bytes` and `test_a_plain_print_of_a_fold_keeps_its_cr_lf`. I reverted the fault with the inverse byte replacement. After the revert, `git status --short` and `git diff --stat` were empty.

## (c) Probes

- The two test files at the head gave `56 passed in 86.04s`. The related set `-k "claim or critic or tester or architect or verdict"` gave `586 passed, 10 skipped, 2 xfailed`. This worktree has no register, so the recorded cases skip.
- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/r360h/test_probe_r360h.py` holds six pytest probes on the test fixtures. They test stderr CR LF, a renamed copy, a `vars()` patch, ignored and `.rota/` writes, the landing of the no-claim pass, and a run of an older head. The result was 3 failed and 3 passed, as findings 1, 2, 3, 5 and 7 state.
- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/r360h/compose_probe.py` composes the prompt and the mode tools of each case. It ran on an archive of `1259589a` under `scratchpad/r360h/base` and on the worktree. The result was 197 cases and 0 differences.
- A read-only query found 0 rows in `cassettes` and in `case_runs` of `C:/Users/roman/rota_p360h/tests/rota/cassettes.db`.
- The planted fault was in `code_run` of `rota/roles/api.py`. It ran on the two test files, and I reverted it.

## (d) Usage

No exact counter is visible to this agent. The estimate is about 72k input tokens of context against the cap of 60k. The output is about 14k tokens, so the total is about 86k. I ran no sub-agent and no model call.

## Second look: pass 1b at 19030c2e

Verdict: pick. Pass 1b fixes findings 1, 2, 3, 5, 8 and 9, and each fix follows its one-line fix. Fix the exclusion of the new case before the gate records it (item S1). The worktree is clean at `19030c2e` after the revert of the planted fault.

### The fixes

- Finding 1: fixed. The door reads `err_file.read_bytes()` and decodes it. The stderr probe now gives "one", CR LF, "two", CR LF in the row.
- Finding 2: fixed. The door refuses a subscript store on `vars(<module>)`, on `<module>.__dict__` and on `sys.modules`. The `vars()` probe now gets "The program changes `vars(icalendar.parser.string)`, the names of a module of the touch". The docstring states the indirect forms that still pass.
- Finding 3: fixed. `_hidden_paths` and `_remove_new_hidden` remove new ignored files and new `.rota/` files. The probe left no `left.txt`, and the note named both files.
- Finding 5: fixed. The control lands the pass. My probe landed it too, with the routes `added` and `test`.
- Finding 8: fixed. `claim_settled` returns true for a quarantined `tick:claim` key of the batch.
- Finding 9: fixed. Both seat-facing sentences name the run of the Architect.
- Tests: the two test files with `test_case_reachability.py` gave `919 passed, 35 skipped`. A planted fault put `read_text` back for stderr. `test_the_row_holds_stderr_as_the_program_wrote_it` failed (`1 failed, 28 passed`). I reverted the fault, and `git status` and `git diff` are empty.

### The case L1-TS-the-run-shows-a-split-word

The case follows the `tests_missing` form of `l1_tester.yaml`: `tick`, `detail`, `refs`, `fixture`, `expect.writes.tests` and `forbidden`. Its detail matches the new `CLAIM_DETAIL`.

S1. `tests/rota/cases/l1_tester.yaml`, the `text_excludes` of the new case. Low. CONFIRMED by reading `fixtures.py` 761 to 770: the check is a plain substring test on the JSON of the rows and on their raw text values. The risk is real, but it is narrower than the example of the coordinator. The excluded strings end in " are". So a right test that asserts the escape text of "wo", CR LF, " rds" is `not in` the output passes. A right test fails when its negated quote includes " are" or copies the whole printout. A test row whose description quotes the printout fails too. Fix: exclude only the positive forms, an `in` test or an `==` test on the printout, for example `"rds are" in ` and `== "This is a very long line`, so that a `not in` quote passes.

### New, outside the six findings

- S2. `rota/roles/api.py`, `_hidden_paths` and `_worktree_of`. Low. PLAUSIBLE: a batch with no `worktree` row falls back to the project root. Then `.rota/` is the state folder of rota, with all the batch worktrees. The door then deletes each new file under it that appeared during the run, and not only the files of the program. Fix: refuse `code.run` when the batch has no `worktree` row.
- S3. `rota/roles/api.py`, `_hidden_paths`. Low. PLAUSIBLE: the function walks each ignored folder, such as an ignored `.venv/`, before and after each run. That costs time and does nothing for correctness. A change to an existing ignored file stays, because only new paths are removed. Fix: skip `.venv/` in the walk, and state in the docstring that changed ignored files stay.
- S4. `tests/rota/cases/l1_tester.yaml`, the `detail` of the new case. Low. CONFIRMED by reading: the detail is a copy of `CLAIM_DETAIL` by hand. A later change of `CLAIM_DETAIL` makes the case wrong with no red test. Fix: add a test that compares the detail of the case with `"without a test: <c1>" + newline + CLAIM_DETAIL`.

### Probes of the second look

- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/r360h/test_probe_r360h.py`, run again with probes p1, p3, p4 and p5. Result: p1, p4 and p5 passed. p3 raised the new `vars()` refusal, which is the expected result now.
- The planted fault and its revert, as stated above.

### Usage of the second look

The estimate is about 24k input tokens of context against the cap of 25k, and about 5k output tokens. I ran no sub-agent and no model call.
