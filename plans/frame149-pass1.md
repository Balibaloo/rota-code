# Frame 149, pass 1: the revert door reads the runs

Meta workflow. Pass 1 of frame 149, "the revert door says the tests pass both ways and refuses the repair of a head that fails at import". The implementing agent on Opus wrote this record on 2026-10-05, in the worktree `C:/Users/roman/rota_f149` on the branch `f149`, from 75918de. The night databases were opened read only. The read called no model.

## 1. The count

**14 revert refusals on nights 113 to 125. At 5 of them the head is worse than the tree that the commit restores, by the counts of runs. At 3 of them the head is worse on the tests that ran at both commits.** (observed: `count.py`, 2026-10-05)

The script is `f149/count.py` in the scratch area of session 2ba331e1. It reads the `turns` table of each night. A turn's `user` text is trimmed to the window, so it is not cumulative. The script reads the results of a turn's calls after the last echoed `TOOL:` line of the next turn. It counts each line that starts `ERROR code.commit: this commit puts the tree back where it stood`. The head is the last `head_commit` of an `OK code.commit` result for the session's batch. A Developer woken by a message has no batch ref, and the script takes the batch of the last commit. The restored tree is the head's parent in the project repository `D:/repos/_AI/sample_repos/clickI`. The runs are the rows of `test_runs` at each sha.

The script finds the counts of the reads: night 120 2, night 124 3, night 123 7. Nights 113 to 119, 122 and 125 hold 0.

| Night | Session, turn | Batch | Head | Runs at the head | Restored tree | Runs of the restored tree | Head worse, by counts | Head worse, on the tests at both |
|---|---|---|---|---|---|---|---|---|
| 120 | s232 turn 13 | bg_3 | 128f6e4967 | 0 pass, 0 red, 43 error | cfed9d8e5d | 0 pass, 0 red, 43 error | no | no, 43 and 43 |
| 120 | s232 turn 15 | bg_3 | 128f6e4967 | 0 pass, 0 red, 43 error | cfed9d8e5d | 0 pass, 0 red, 43 error | no | no, 43 and 43 |
| 121 | s144 turn 22 | bg_1 | ee54cc18a1 | 34 pass, 3 red, 0 error | 2aece0a4a8 | 34 pass, 2 red, 0 error | yes | no, 2 and 2 of 36 |
| 121 | s148 turn 7 | bg_1 | ee54cc18a1 | 34 pass, 3 red, 0 error | 2aece0a4a8 | 34 pass, 2 red, 0 error | yes | no, 2 and 2 of 36 |
| 123 | s162 turn 15 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s168 turn 5 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s168 turn 16 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s168 turn 20 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s170 turn 1 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s170 turn 2 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 123 | s170 turn 3 | bg_1 | 70723b7576 | 35 pass, 2 red, 0 error | 73b1ea60ae | 35 pass, 2 red, 0 error | no | no, 2 and 2 |
| 124 | s144 turn 13 | bg_1 | 35211b40e4 | 0 pass, 0 red, 37 error | 617055787d | 34 pass, 3 red, 0 error | yes | yes, 37 and 3 |
| 124 | s144 turn 14 | bg_1 | 35211b40e4 | 0 pass, 0 red, 37 error | 617055787d | 34 pass, 3 red, 0 error | yes | yes, 37 and 3 |
| 124 | s145 turn 22 | bg_1 | 35211b40e4 | 0 pass, 0 red, 37 error | 617055787d | 34 pass, 3 red, 0 error | yes | yes, 37 and 3 |

Totals: 14 refusals. The sentence "The tests pass both ways" is false at all 14, because each head holds red or `error` runs. Head worse by counts: 5. Head worse on the tests at both: 3.

Night 121's head is worse by counts only. Its third red test, `inh_echo_json_02`, has no run at 2aece0a4a8. The Tester stored it after that commit. So the restored tree does not show that it passes that test (observed: `test_runs` of night 121, 2026-10-05).

Night 123's 7 refusals (observed: the completions of each turn, 2026-10-05). The head 70723b7576 removes the `isinstance(obj, str)` branch of `echo_json`. Every refused commit has a message about a Click command, such as `Make echo_json a Click command so runner.invoke can call it`. s170's commit messages name `tk_1`, and its writes went to `echo_json.py` and `src/click/echo_json.py` first. The tree that each commit held equals 73b1ea60ae, so the seat's own write did not reach the tree. The commit's message and the commit's tree disagree. That is night 124's wall 3, a write left in the worktree, and this pass does not fix it.

## 2. Design

**What the door reads today.** The door is the block in `code_commit`, `rota/roles/api.py`, at 75918de lines 10840 to 10856. It runs `git rev-parse --verify -q HEAD~1`, then `git diff --quiet HEAD~1` and `git diff --quiet HEAD` on the worktree. It reads no row. "The tests pass both ways" comes from clickI night 30, a flip of one trailing newline (copied: the comment at the door). The sentence is a constant and states no fact that the door read.

**The runs that the door holds at the refusal.** `test_runs` holds one row per test, per commit sha and per attempt, with `batch_id`, `commit_sha` and `result`. The harness runs the tests at each head before the fix wake. So at all 14 refusals, the database held the runs of the head and of `HEAD~1` (observed: the table above). The restored tree equals the tree of `HEAD~1`, and its runs are stored under the sha of `HEAD~1`. The door needs no new test run. It reads two shas from git and the rows of `test_runs`.

**The rule.**

1. The door reads the latest run of each test of the batch at `HEAD` and at `HEAD~1`.
2. It takes the tests that ran at both commits. It counts the tests that do not pass at each commit.
3. It admits the commit when fewer of those tests fail at `HEAD~1` than at `HEAD`.
4. Otherwise it refuses. Where both commits have runs and every run passes, the refusal is the old sentence to the byte.
5. Otherwise the refusal states the runs: the counts of pass, red and `error` at the head and at `HEAD~1`, or "No run is stored" for a commit with no run. It states the count on the tests at both, and that going back does not lower it.
6. Where the head has red or `error` runs, the step is "Change the code that the red tests call, then commit." The door names `msg.escalate_architect` on the criteria of the red tests when the escalation doors admit it. Where the head has no red run, the step is the old step.
7. The door records each side's runs as a fact of kind `runs`. `sandbox.check_facts` reads git and `test_runs` itself and compares.

The rule counts only the tests at both commits, because a test stored after `HEAD~1` has no run there. Night 121 shows the case. The brief's words are "fewer `error` or red runs than the head". The rule reads them on the tests at both. Section 5 names this as a deviation.

Neither stop condition holds. The door needs no new test run, and 3 refusals are at a head worse than the restored tree. So the pass continued to step 3.

## 3. What changed

- `rota/roles/api.py`. `_runs_at`, `_runs_said`, `_REVERT_HEAD`, `_REVERT_OLD_STEPS` and `_revert_refusal` are new, before `code_commit`. The door in `code_commit` calls `_revert_refusal` and raises its sentence, or admits when it returns None.
- `rota/core/sandbox.py`. `_runs_hold` is new. `check_facts` checks the kind `runs` with it.
- `tests/rota/test_revert_door.py`, new, 4 tests.
- `tests/rota/fixtures/night124_utils_617055787d.txt`, new. The bytes of `src/click/utils.py` at 617055787d, from the project repository.

The new sentence, for night 123's head, reads like this:

`this commit puts the tree back where it stood before your last commit: you are undoing yourself. The runs at the head 70723b7576: 35 pass, 2 red, 0 error. The runs at 73b1ea60ae, the tree this commit puts back: 35 pass, 2 red, 0 error. Of the 37 tests that ran at both, the head fails 2 and 73b1ea60ae fails 2. Going back does not lower that count. Change the code that the red tests call, then commit. Do not flip.` A last sentence names `msg.escalate_architect(refs=[...])` when the doors admit it.

## 4. The ends-when

1. `test_the_repair_of_a_head_that_fails_at_import_is_admitted`. The worktree holds the real file at 617055787d and s143's 20 lines at 35211b40e4. s144's real write of turn 13, `start=688, end=725`, puts the file back to the byte. The door admits `code.commit(message='Remove echo_json_cmd to avoid import cycle')`. Pass.
2. `test_where_both_commits_pass_the_refusal_is_the_old_sentence`. The refusal equals the sentence of 75918de to the byte. The test also asserts that the door records two `runs` facts and that both read true. Pass.
3. `test_a_revert_where_the_head_is_not_worse_states_the_runs`. One red test at both commits and a second red test at the head only. The door refuses, and the test asserts the whole sentence with the counts. Pass.
4. The fact check and the follow check. `test_a_runs_fact_that_the_state_contradicts_reads_false` holds four facts: a true one, a wrong result, a wrong `at`, and an empty runs fact of a commit with no run. It reads `[True, False, False, True]`. With `ROTA_OFFER_LOG` on the four new tests and `test_a_commit_that_undoes_the_last_one_is_churn`, 6 `runs` facts read true, and the offer `msg.escalate_architect({'refs': ['c1']})` was admitted, with no second refusal (observed: 2026-10-05).
5. The proof by removal. With `rota/roles/api.py` and `rota/core/sandbox.py` put back to 75918de, all 4 new tests fail (observed: 2026-10-05):
   - test 1: `ValueError: this commit puts the tree back ... The tests pass both ways`.
   - test 2: `assert [] == ['HEAD', 'HEAD~1']`, no fact recorded.
   - test 3: `assert 'pass both ways' not in ...`.
   - test 4: `[False, False, False, False]`, the kind is unknown.
6. The table under the new rule: the door admits 3 past refusals, all of night 124. It still refuses 11: night 120 2, night 121 2 and night 123 7. Each of the 11 now states the runs and does not say that the tests pass.

## 5. Deviations

- The rule counts the failing runs on the tests that ran at both commits, and not all runs of each commit. The count of all runs admits night 121's 2 refusals. There the extra red test has no run at the restored tree, so the admission would rest on a missing run.
- The new sentence names `msg.escalate_architect` with refs only when `sandbox._escalation_admitted` holds. Frame 135's law says a refusal names only a call that the doors admit. The old step stays where the head has no red run.
- Where one commit has no run, the old sentence is gone, and the refusal says "No run is stored". The old test `test_a_commit_that_undoes_the_last_one_is_churn` meets this branch. It matches `undoing yourself` only and still passes.
- A fixture file of 21901 bytes holds the real file of 617055787d, so that test 1 uses s144's real write and commit.

## 6. Seen and not fixed

- Night 123's 7 refused commits hold a tree that the seat did not write. The message names a Click command, and the tree equals 73b1ea60ae. The seat's writes were refused, and a write left in the worktree went to the commit. Night 124's wall 3.
- The runs of `HEAD~1` can be of an older test version. `test_runs` has no test version column, so the door cannot tell. A Tester's new version after `HEAD~1` can make the counts unequal for a cause that is not the code.
- The door's facts check the counts per side. No fact checks the sentence "Of the N tests that ran at both".
- `code.write` writes the platform's line ends in the worktree. Test 1 compares the file as lines for that cause.
- The cassette store holds the old sentence in one llama3.1:8b cassette and in 10 transcripts of `L1-DV-build-a-clear-criterion`. No qwen3:8b recording holds it.

## 7. The suite

The touched and nearby files pass: `test_revert_door.py`, `test_desk_guards.py`, `test_offers_followed.py` and `test_t0_sandbox.py`, 420 passed and 7 xfailed (observed: 2026-10-05).

The gate on the final tree, uncommitted on 75918de (observed: `python -m rota.tools.gate` in the worktree, 2026-10-05):

```
suite: 23 failed, 2828 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 999.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 3 new reds and the 3 reds gone are the same lists as the gate of frame 144's pass 4 on a994576 (copied: `plans/frame144-pass4.md`, section "The suite"). The baseline is 658abb6, and the reds came before this pass. None of the 3 touches the revert door.
