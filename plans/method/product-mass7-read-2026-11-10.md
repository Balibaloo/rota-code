# The ground of the 11 runs, a blind read, 2026-11-10

Written by one reader for frame 364. The reader got no hypothesis. Every
count comes from a read-only query (`sqlite3`, `mode=ro`) or a read-only
git command. The scripts are `q1.py` to `q23.py` in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass7/`.
`T` is `C:/Users/roman/AppData/Local/Temp/claude/`.

## Result

1. The index is complete in all 11 runs: every top-level function and class at the base has a row, and only binary files, two `.ics` files and `uv.lock` are absent.
2. No record holds a stack decision in any run, and the harness runs pytest in every run with a batch.
3. Three icalendar runs (dry3, dry4, dry5) register 1 of the repository's 162 test files, and the other three runs with a batch on icalendar register 162.
4. In dry4 and dry5 a refusal named `.github/workflows` as the only test folder, and the Tester then wrote batch tests in `.github/workflows/`.
5. The provisioner of dry3, dry4, dry5 and dry6c installed no package of icalendar's `test` group, and dry6c's base run errored on `No module named 'hypothesis'`.
6. Three runs on the same base commit and the same 162 test files record two different base results: dry6c 157 pass, 4 fail, 1 error, and dry7 and dry8 159 pass, 3 fail.
7. The repository's own tests are red at the base in dry6c, dry7 and dry8, in three to five files.
8. 38 sessions failed on the model server: dry1 8, dry6 18, dry6b 9, dry7 3, all `LLMUnavailable`. No session failed on a cut prompt, and no record shows a missing program.
9. The pages that followed name the work, not the server: "the team could not read a part of the code" (dry6), "the team could not put back code it was not asked to change" (dry7).
10. Three runs merged (dry1 clickI, dry2 tipsI, dry3 icalendarI). Each merge moved the person's main branch, and each added three test files with made names.
11. No refused write names a path outside the worktree. The path refusals are the test-file door and the program-file door.
12. The repository copies changed after the runs: start scripts reset main, deleted `batch/*` branches and removed `.rota`. So the end state of dry3 to dry8 comes from the reflog, the object store and the rows.

## Part A: what the design says the ground is

1. A worktree is made for each batch by the scheduler, never by a role (`rota/ENVIRONMENT.md:30`). [Check: each batch row names a worktree under `<root>/.rota/worktrees/<id>`, and no `worktree:<id>` failure key is in `config`.]
2. "a **worktree** lives in the target project and the only record that it is ours is a row in the database" (`rota/README.md:124-127`). [Check: the rows that name a worktree agree with `git worktree list`.]
3. "A worktree with uncommitted changes at session end is a fault. The uncommitted change never existed" (`rota/LAWS.md:169-171`). [Check: the runner's end notes discard writes that no commit holds, and a surviving worktree is clean.]
4. The expected touch set "is a *prediction*, never a permission — nothing rejects a diff for straying outside it" (`rota/LAWS.md:337-342`). [Check: no refused write names the touch set.]
5. "The account rules the stack", and an existing repository's stack is read from its manifest, "the ruling row it writes is `observed`" (`rota/COMPLETION.md:82,88-89`, `plans/greenfield-setup.md:76-81`). [Check: a row records the stack.]
6. "the provisioner installs its toolchain" (`rota/COMPLETION.md:82-83`). [Check: the `env:<batch>` note lists pytest and the test packages the manifest declares.]
7. "the floor is that stack's test runner" (`rota/COMPLETION.md:83`). [Check: every recorded test run is the stack's runner, run in the batch worktree.]
8. "one environment per batch, and its lifetime is the worktree's" (`rota/ENVIRONMENT.md:68`). [Check: one `env:<batch>` note for each started batch, and the `.venv` is inside the worktree.]
9. "the harness runs the batch's tests and the repository's own" (`rota/MAP.md:69-71`). [Check: the inherited test rows equal the repository's test files at the base.]
10. "A test that only passes because of state a previous run left behind is the exact failure this system exists to prevent", and the environment is disposable (`rota/ENVIRONMENT.md:182-186`). [Check: runs at one base commit record the same base result for the same test files.]
11. "The code index (`code_index`, `code_edges`, `code_lexicon`) is built by the provisioner", and the structure holds the project's shape "as records observed from the code" (`rota/MAP.md:103-104`, `plans/composition.md:40-43`). [Check: index rows against the files and the top-level definitions at the base.]
12. "The spawner exists and **nothing calls it**" (`rota/README.md:38-40`). [Check: `runtime_processes` has no row.]
13. `num_ctx` "is set explicitly and recorded as a pin alongside model id, temperature and prompt hash" (`rota/README.md:234-236`). [Check: every `sessions` row carries `num_ctx`.]
14. "A crashed session leaves its trigger open with its attempt count raised; past `message_attempt_cap` the message is quarantined" (`rota/LAWS.md:164-167`). [Check: failed sessions come in runs of the cap, then a quarantine or an exhaustion.]
15. "A wake dispatched past its cap is quarantined and said out loud (`quarantined`). There is no silence" (`rota/MAP.md:94-96`). [Check: a page or a log line says the stop, and its words name what the failed session rows record.]
16. "The scheduler merges (`merge`, `worktrees.integrate`)" (`rota/MAP.md:85-86`). [Check: main moves only by a `merge batch/<id>` reflog entry, for a batch whose row says `merged`.]
17. "Git commits are outside it, so the database *lags* the worktree and boot reconciles the two" (`rota/README.md:220-222`). [Check: each `batches.head_commit` is a commit in the object store that descends from the base.]
18. "The clean-workspace rule returns" (`plans/composition.md:123-124`). [Check: at the end of the run the repository holds nothing that rota made outside a commit. The page gives no definition, so this check is the reader's.]

## Part B: the ground of each run

### B.1 The repositories and the bases

| run | repository copy | base | how the base is known |
|---|---|---|---|
| dry1 | `D:/repos/_AI/sample_repos/clickI` | `2c8cd3a` | reflog `reset: moving to 2c8cd3a` 2026-10-31 03:43:32, `config.created_at` 03:44:34 |
| dry2 | `D:/repos/_AI/sample_repos/tipsI` | `99101f1` | reflog reset 2026-11-02 13:44:16, `created_at` 13:44:25 |
| dry3 | `D:/repos/_AI/sample_repos/icalendarI` | `99619246` | reflog `clone` 2026-11-02 18:42:16, `created_at` 18:44:05 |
| dry4 | icalendarI | `99619246` | reflog reset 2026-11-03 05:18:24, `created_at` 05:19:57 |
| dry5 | icalendarI | `99619246` | reflog reset 2026-11-04 12:18:24, `created_at` 12:19:35, `dry5_start.sh` |
| dry6 | icalendarI | `99619246` | reflog reset 2026-11-06 00:30:41, `created_at` 00:30:50 |
| dry6b | icalendarI | `99619246` | reflog reset 2026-11-06 04:02:14, `created_at` 04:02:28 |
| dry6c | icalendarI | `99619246` | the same database as dry6b, continued |
| dry7 | icalendarI | `99619246` | reflog reset 2026-11-06 14:09:28, `created_at` 14:09:51 |
| dry8 | icalendarI | `99619246` | reflog reset 2026-11-08 17:35:44, `created_at` 17:36:12, `dry8_start.sh` |
| blind1 | `T/6d9eb18c9e6274ab/5ee5ec0b-.../scratchpad/blind1/tips` | `ff1f65f` | reflog `clone: from D:/repos/_AI/sample_repos/tipsI` 2026-11-10 01:04:15 |

Size at the base (observed: `git ls-tree -r`, `git grep 'def test_'`, which counts methods too):

| repository at base | files | `.py` files | test files | `def test_` | top-level functions and classes |
|---|---|---|---|---|---|
| clickI `2c8cd3a` | 166 | 79 | 34, and 1 conftest | 547 | 876 |
| tipsI `99101f1` | 7 | 3 | 1 | 1 | 9 |
| icalendarI `99619246` | 698 | 258 | 162, and 1 conftest | 1231 | 1470 |
| blind1 tips `ff1f65f` | 10 | 6 | 4 | 7 | 15 |

- The tipsI base `99101f1` is the commit "rota: deliver bg_1" (observed: `git log`).
- The blind1 base `ff1f65f` is tipsI after the dry2 merge, "rota: deliver b_1" (observed: blind1 reflog and `git log`).
- icalendar's `pyproject.toml` sets `testpaths = ["src/icalendar/tests"]` (observed: `git show 99619246:pyproject.toml`, line 298).

### B.2 What rota provisioned

The environment record is the `config` key `env:<batch>`, written by `lifecycle.start` (observed: `rota/core/lifecycle.py:130-137`). The harness runs `python_for(root) -m pytest` (observed: `rota/core/harness.py:380`).

| run | batch | `env:` note |
|---|---|---|
| dry1 | bg_1 | `installed pytest; installed the project (editable)` |
| dry2 | b_1, b_2 | `made .venv; installed pytest`, then `installed pytest` |
| dry3 | bg_1 | `made .venv; installed pytest, python-dateutil, tzdata>=2025.3, typing-extensions~=4.10; python_version < '3.13'; installed the project (editable)` |
| dry4 | bg_1 | the same packages as dry3, without `made .venv` |
| dry5 | b_1 | the same as dry3 |
| dry6c | b_1 | the same packages as dry4 |
| dry7 | b1 | the dry3 packages and `coverage, hypothesis, mypy>=1.0, pytest, pytz>=2025.2, types-python-dateutil, types-pytz` |
| dry8 | bg_1 | `made .venv;` and the dry7 packages |
| dry6, dry6b, blind1 | none | no batch, no note |

- No note reports a failed step (observed: q1, q15).
- icalendar declares the `test` group with `coverage`, `hypothesis`, `mypy>=1.0`, `pytest`, `pytz>=2025.2`, `types-python-dateutil`, `types-pytz` (observed: `pyproject.toml:109-117`). dry3, dry4, dry5 and dry6c did not install it.
- No `decisions` row and no `config` key names a stack, a language or a runner in any run (observed: q13, q16).
- `runtime_processes` has 0 rows in every run. `batches.port_base` is NULL in dry1 to dry3 and 41000 from dry4 on (observed: q21).
- dry6 has a turn log of a failed start before its database: "profile local: no ollama at http://127.0.0.1:11434, or it has no models", then "Stopped at 2026-11-06 00:29: the model qwen3:8b does not answer." (observed: `T/d--repos-rota/94cb1260-.../scratchpad/dry6/t0_noserver.log`).

### B.3 The index

| run | path rows | files at base | files absent from the index | symbol rows | top-level defs at base held | `code_edges` | `code_calls` | `code_lexicon` |
|---|---|---|---|---|---|---|---|---|
| dry1 | 166 | 166 | 2 `.jpg`, `uv.lock` | 888 | 876 of 876 | 108 | no table | 159 |
| dry2 | 10 | 7 | none | 15 | 9 of 9 | 4 | no table | 3 |
| dry3 | 697 | 698 | 2 `.png`, `Index_Error.ics`, `Type_Error.ics` | 1475 | 1470 of 1470 | 313 | no table | 403 |
| dry4 | 699 | 698 | the same 4 | 1478 | 1470 of 1470 | 313 | no table | 403 |
| dry5 | 694 | 698 | the same 4 | 1472 | 1470 of 1470 | 313 | 500 | 403 |
| dry6, dry6b, dry6c, dry7, dry8 | 694 | 698 | the same 4 | 1472 | 1470 of 1470 | 313 | 594 | 403 |
| blind1 | 10 | 10 | none | 15 | 15 of 15 | 4 | 4 | 3 |

- The extra path rows are the batch's test files: the merged tests in dry1, dry2 and dry3, and the five tests of the running batch in dry4 (observed: q3).
- The extra symbol rows are definitions inside an `if` block, for example `src/icalendar/cal/lazy.py::_benchmark` (observed: q3).
- No symbol row is a method (observed: 0 grains with a dot after `::`).

### B.4 The tests the harness holds

| run | repository test files | inherited rows | batch test paths |
|---|---|---|---|
| dry1 | 34 | 34 | `tests/test_termui_tk_1_criteria_{skipped,terminal_check,waited}.py` |
| dry2 | 1 | b_1 1, b_2 4 | `tests/test_calculate_tip_c_{1,2,3}.py` |
| dry3 | 162 | 1, `.github/workflows/test_generate_matrix.py` | `tests/test_caselessdict.py`, `tests/test_caselessdict_c1.py`, `tests/test_caselessdict_sort.py` |
| dry4 | 162 | 1, the same file | `.github/workflows/test_test_fold_no_boundary.py`, `src/icalendar/tests/test_fold_{max_length,no_boundary,preserves_content,semantics}.py` |
| dry5 | 162 | 1, the same file | `.github/workflows/test_fold_c{1,2,3}.py` |
| dry6c | 162 | 162 | `src/icalendar/tests/test_folding.py` |
| dry7 | 162 | 162 | `tests/test_fold_{component_definitions,long_lines,no_split_delimiters,parameter_values,preserve_chars}.py` |
| dry8 | 162 | 162 | `src/icalendar/tests/test_foldline.py`, `src/icalendar/tests/test_foldline_75octets.py` |
| dry6, dry6b, blind1 | 162, 162, 4 | 0 | no batch |

- The icalendar root has no `tests/` folder at the base (observed: `git ls-tree -d 99619246`).
- No batch test path is a file of the base tree (observed: `git ls-tree` per path).
- All 9 icalendar runs carry the frame ruling `src` = `program`. Only dry1 to dry4 and dry7 to dry8 also carry `.github` = `attached` (observed: q12).

The base result is the `config` key `base_run:<batch>` (observed: `harness.inherit`, `rota/core/harness.py:552-557`):

| run | base result of the inherited files | red files at the base |
|---|---|---|
| dry1 | 34 pass | none |
| dry2 | b_1 1 pass, b_2 4 pass | none |
| dry3, dry4, dry5 | 1 pass | none |
| dry6c | 157 pass, 4 fail, 1 error | `test_issue_1445.py`, `test_rfc_6868.py`, `test_issue_313_globally_unique_tzid.py`, `test_with_doctest.py`, and `hypothesis/test_fuzzing.py` error |
| dry7, dry8 | 159 pass, 3 fail, the same nodes in both | `test_issue_1445.py`, `test_rfc_6868.py` (8 nodes), `test_time.py` |

The dry6c error is "E   ModuleNotFoundError: No module named 'hypothesis'" and "Interrupted: 1 error during collection" (observed: `test_run_journal`, q5).

The last result of each inherited file at each commit (observed: `test_run_journal`, q20):

- dry1: `4fcd6d73` 34 pass, 12 passes of the harness (408 rows). No journal row at the base.
- dry2: `e40742e3` 1 pass.
- dry3: `99619246` 1 pass, `c5e780a5` 1 pass.
- dry4: 5 commits, 1 pass at each. The head `1c452198` has no journal row.
- dry5: `99619246` 1 pass, `670629b3` 1 pass.
- dry6c: `99619246` 157 pass, 4 fail, 1 error. The batch head is the base.
- dry7: `99619246` 159/3, five commits at 154 pass and 8 fail, `17ed55ce` and `49e0fc1a` 161 error and 1 pass, `21bbe661` 105 pass, 56 fail, 1 error.
- dry8: `99619246` 159/3, `67e0b2d0` 159/3, `a585c4ea` 159/3, `fddff3af` 157 pass, 5 fail.

At the same base `99619246`, dry3, dry4 and dry5 agree, and dry7 and dry8 agree. dry6c disagrees with dry7 and dry8 on the same 162 files.

### B.5 Where the desks wrote

- Each batch row names `<root>\.rota\worktrees\<id>`, or NULL after a merge (observed: q1). No `worktree:<id>` key is in any `config` (observed: q1).
- `git worktree list` now shows one batch worktree, tipsI `.rota/worktrees/b_2` at `ff1f65f`, and its status is clean (observed).
- Branches now: clickI `batch/bg_1`, tipsI `batch/b_1` and `batch/b_2`, icalendarI none (observed: `git branch -a`).
- The batch heads of icalendar exist as commits in the object store: `c5e780a5`, `1c452198`, `670629b3`, `21bbe661`, `fddff3af` (observed: `git cat-file -t`).
- Commits since the base on the head: dry3 1, dry4 8, dry5 1, dry6c 0, dry7 9, dry8 5 (observed: `git rev-list --count`). Every batch head touches only `src/icalendar/parser/` or `src/icalendar/caselessdict.py` (observed: `git diff --stat`).
- Refusals that name "escapes the worktree" or "is outside the project": 0 in every run (observed: q8).
- Path refusals, counted once per session and text (observed: q10):
  - dry2: 7, the test-file door of `code.write`: "tests/test_calculate_tip.py is a test file, and the tests are the Tester's. The harness runs the tests on record; a test you cannot pass is `msg.challenge_tester`, not a rewrite".
  - dry4: 3, the program-file door of `tests.encode`: "path 'src/icalendar/tests/test_fold_no_boundary.py' is a program file of the project. The harness writes the test at its path, so the test replaces that file. Write the test in a test folder of the index: .github/workflows. For example, path='.github/workflows/test_test_fold_no_boundary.py'".
  - dry5: 2. One is the program-file door on `src/icalendar/tests/test_icalendar.py`, a test file of the base, with the same route `.github/workflows`. One is the test-file door on `.github/workflows/test_fold_c1.py`.
  - dry7: 2 and dry8: 1, the test-file door on `src/icalendar/tests/` files.
  - dry1, dry3, dry6, dry6b, dry6c, blind1: 0.
- Runner discards of writes no commit held: dry4 1 and dry7 1, both `["src/icalendar/parser/string.py"]` (observed: q22).

### B.6 Failures of the ground

Failed sessions are `sessions.committed = 0` with a last turn `SESSION FAILED: ...` (observed: `rota/core/db.py:2390-2419`, q6). Each failed session has that turn.

| run | failed sessions | text |
|---|---|---|
| dry1 | 8 liaison | `LLMUnavailable('ollama at http://127.0.0.1:11434: no answer in 300s')` |
| dry6 | 18: 10 liaison, 8 architect | the same on 11434, and on 11435 with "The model answered a probe, so the failure is the wake's own." |
| dry6b | 9 liaison | the same on 11436, with the probe sentence |
| dry7 | 3 developer | `LLMUnavailable('ollama at http://127.0.0.1:11434: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>')` |
| others | 0 | none |

dry6c adds no failed session to the shared database (observed: q17).

The words that the logs show after the failures:

- dry6, after the architect surveys of `news` and `src/icalendar` failed 3 times each: "Stuck: the team could not read a part of the code for news after 3 attempts; the team could not read a part of the code for src/icalendar after 3 attempts. Nothing waits on you, and nothing moves until that is cleared. Tell me what to change." (observed: `dry6/t5.log`, line 12, and q18).
- dry6b: "liaison<-message(m8) ... [quarantined past the attempt cap: m8]" (observed: `dry6b/t2.log:14`). The same for m14 (`t3.log:10`).
- dry7, after the three `touch_mistaken` sessions failed: "The team gave up: the team could not put back code it was not asked to change after 3 attempts." (observed: `dry7/t7c.log`, q18).
- dry1: no turn log file holds its pages (see Part E).

Other ground events:

- Harness timeout: dry1, 3 runs of `tests/test_termui_tk_1_criteria_waited.py` at `4fcd6d73` with output "timed out after 120s" (observed: journal seq 141, 178, 215). The same test later passed at the same commit (seq 437).
- Collection errors of the environment: dry6c 2 rows, the `hypothesis` import (above).
- Collection errors from the batch's own code: dry7 330 error rows. At `17ed55ce` and `49e0fc1a` the text is "ImportError: cannot import name 'foldline' from 'icalendar.parser.string'" (reasoned: the name is one that the batch removed, so this is the model's write, not the ground). At `21bbe661`, 2 rows "ERROR collecting src/icalendar/tests/test_issue_662_component_properties.py ... ValueError".
- A cut prompt: "prompt did not fit" 0 in every run (observed: q8). The output budget cut, "your reply was cut at the output budget", ended a reply in this many sessions: dry1 13, dry2 3, dry3 10, dry4 10, dry5 8, dry6 0, dry6b 2, dry6c 1, dry7 13, dry8 9, blind1 1.
- A missing program: 0. The matches of "FileNotFoundError" are icalendar's `news/1493.bugfix` text (observed: q7).

### B.7 The time

The sum of `turns.ms` covers the model call only (observed: `rota/core/runner.py:5888-5901`).

| run | minutes | by role | longest turn |
|---|---|---|---|
| dry1 | 91.1 | liaison 30.2, vision_keeper 16.5, tester 14.8, architect 9.8, critic 8.5, developer 5.8, terminologist 5.4 | s164 liaison, 1.9 min |
| dry2 | 22.3 | liaison 7.7, developer 4.2, architect 3.1, terminologist 2.5, tester 1.8, critic 1.6, vision_keeper 1.6 | s81 liaison, 1.9 |
| dry3 | 131.7 | liaison 50.7, architect 49.0, terminologist 10.5, vision_keeper 9.5, critic 6.0, tester 3.4, developer 2.6 | s205 liaison, 2.0 |
| dry4 | 89.9 | architect 27.6, developer 22.5, liaison 11.8, vision_keeper 10.4, terminologist 9.3, tester 6.6, critic 1.4, researcher 0.3 | s203 liaison, 1.9 |
| dry5 | 110.1 | architect 27.4, developer 21.6, liaison 18.9, vision_keeper 13.0, terminologist 12.8, critic 8.5, tester 7.9 | s259 liaison, 3.5 |
| dry6 | 52.7 | terminologist 20.1, architect 12.0, liaison 11.1, vision_keeper 9.5 | s88 architect, 5.8 |
| dry6b | 32.9 | liaison 9.6, architect 9.5, vision_keeper 6.0, terminologist 5.4, critic 2.4 | s19 vision_keeper, 1.8 |
| dry6c | 13.3 | tester 4.3, architect 4.1, liaison 1.8, developer 1.7, vision_keeper 0.7, terminologist 0.4, researcher 0.3 | s160 architect, 1.6 |
| dry7 | 96.2 | developer 29.2, architect 23.7, vision_keeper 16.3, tester 8.1, liaison 8.0, terminologist 7.0, critic 3.9 | s146 liaison, 1.9 |
| dry8 | 69.9 | vision_keeper 18.6, architect 16.7, liaison 9.8, developer 9.7, terminologist 6.9, critic 4.1, tester 4.1 | s184 liaison, 2.0 |
| blind1 | 6.9 | terminologist 2.6, critic 1.4, liaison 1.4, architect 1.0, vision_keeper 0.6 | s36 terminologist, 1.5 |

dry6c is the shared database less the 137 sessions and 428 turns of the dry6b copy. All 137 sessions and 428 turns of the copy are in the shared file with the same `committed` and `ms` (observed: q17).

### B.8 What the person's repository holds at the end

| run | merged | main moved | rota's files at the end |
|---|---|---|---|
| dry1 | yes, bg_1 | `2c8cd3a` to `09c82f3`, reflog 2026-11-02 02:28:10, still there | 3 test files with made names in the merge, branch `batch/bg_1`, an empty `.rota/worktrees` (mtime 2026-11-02 02:28) |
| dry2 | yes, b_1 | `99101f1` to `ff1f65f`, 2026-11-02 14:00:20, still there | 3 test files with made names in the merge, branches `batch/b_1` and `batch/b_2`, the worktree `.rota/worktrees/b_2` with `.venv` of the abandoned batch. `git status` shows `?? .rota/` |
| dry3 | yes, bg_1 | `99619246` to `4f12af1e`, 2026-11-02 20:27:37. Reset to `99619246` at 2026-11-03 05:18:24 | 3 test files with made names in a new root `tests/` folder |
| dry4 | no, `running` | no entry between the resets | the row names `.rota/worktrees/bg_1` at `1c452198` |
| dry5 | no, `deferred` | no | the row names `.rota/worktrees/b_1` at `670629b3` |
| dry6, dry6b | no batch | no | nothing in the rows |
| dry6c | no, `deferred` | no | the row names `.rota/worktrees/b_1` at the base |
| dry7 | no, `deferred` | no | the row names `.rota/worktrees/b1` at `21bbe661` |
| dry8 | no, `deferred` | no | the row names `.rota/worktrees/bg_1` at `fddff3af` |
| blind1 | no batch | no | nothing. The operator ran `python -m pytest -q` in the copy after the run (observed: `blind1/turn_record.md:300`), so `.pytest_cache` and `__pycache__` are the operator's |

- icalendar's `.gitignore` line 5 `.*` ignores `.rota`. The `.gitignore` of clickI and tipsI does not (observed: `git check-ignore -v`).
- The Developer commits and the "rota: tests of" commits carry the author "Roman Kubiv <romankubiv101@gmail.com>". The merge commit carries "rota <rota@local>" (observed: `git log --format`).

The merged diffs (observed: `git diff --stat` and `git diff`):

dry1, clickI `2c8cd3a..09c82f3`, 4 files:
- `src/click/termui.py`: `pause()` returns `bool`. It returns `False` when stdin or stdout is not a terminal and `True` after the wait (+3, -2).
- `tests/test_termui_tk_1_criteria_skipped.py`: a new test, 11 lines.
- `tests/test_termui_tk_1_criteria_terminal_check.py`: a new test, 8 lines.
- `tests/test_termui_tk_1_criteria_waited.py`: a new test, 18 lines. It patches `isatty` and `getchar` and asserts that `pause()` is `True`.

dry2, tipsI `99101f1..ff1f65f`, 5 files:
- `main.py`: `calculate_tip` raises `ValueError` for a percentage below 0 or above 100 (+2).
- `tip_calculator.py`: the same guard (+2). The last line of the file loses its final newline.
- `tests/test_calculate_tip_c_1.py` (14 lines), `tests/test_calculate_tip_c_2.py` (10), `tests/test_calculate_tip_c_3.py` (9): new tests.

dry3, icalendarI `99619246..4f12af1e`, 4 files:
- `src/icalendar/caselessdict.py`: `canonsort_keys` raises `ValueError` when `canonical_order` holds a duplicate key, with a `Raises:` section in the docstring. The last line, `__all__`, loses its final newline.
- `tests/test_caselessdict.py` (9 lines), `tests/test_caselessdict_c1.py` (11), `tests/test_caselessdict_sort.py` (9): new tests in a root `tests/` folder that the base does not have.

## Part C: the grid

The 11 runs are dry1, dry2, dry3, dry4, dry5, dry6, dry6b, dry6c, dry7, dry8, blind1.

| # | statement | holds | does not hold | cannot be told |
|---|---|---|---|---|
| 1 | a worktree per batch, by the scheduler | 8: dry1, dry2, dry3, dry4, dry5, dry6c, dry7, dry8 | 0 | 3: dry6, dry6b, blind1 |
| 2 | the worktree in the project, the row its record | 3: dry1, dry2, dry3 | 0 | 8: dry4, dry5, dry6c, dry7, dry8, dry6, dry6b, blind1 |
| 3 | uncommitted at session end is a fault | 3: dry2, dry4, dry7 | 0 | 8: the rest |
| 4 | the touch set is no permission | 8: the runs with a batch | 0 | 3: dry6, dry6b, blind1 |
| 5 | the stack read from the manifest, an observed row | 0 | 11: all | 0 |
| 6 | the provisioner installs the toolchain | 4: dry1, dry2, dry7, dry8 | 4: dry3, dry4, dry5, dry6c | 3: dry6, dry6b, blind1 |
| 7 | the floor is the stack's test runner | 8: the runs with a batch | 0 | 3: dry6, dry6b, blind1 |
| 8 | one environment per batch, in its worktree | 8: the runs with a batch | 0 | 3: dry6, dry6b, blind1 |
| 9 | the harness runs the repository's own tests | 5: dry1, dry2, dry6c, dry7, dry8 | 3: dry3, dry4, dry5 | 3: dry6, dry6b, blind1 |
| 10 | no result rests on what another run left | 3: dry3, dry4, dry5 | 3: dry6c, dry7, dry8 | 5: dry1, dry2, blind1, dry6, dry6b |
| 11 | the index is built and observed | 11: all | 0 | 0 |
| 12 | nothing calls the spawner | 11: all | 0 | 0 |
| 13 | `num_ctx` is a recorded pin | 11: all | 0 | 0 |
| 14 | a crashed session is bounded by the cap | 4: dry1, dry6, dry6b, dry7 | 0 | 7: the runs with no failed session |
| 15 | a quarantine is said out loud | 0 | 2: dry6, dry7 | 9: the rest |
| 16 | the scheduler merges | 11: all | 0 | 0 |
| 17 | the database lags git, the head is a real commit | 8: the runs with a batch | 0 | 3: dry6, dry6b, blind1 |
| 18 | the clean-workspace rule | 1: blind1 | 7: dry1, dry2, dry4, dry5, dry6c, dry7, dry8 | 3: dry3, dry6, dry6b |

Evidence for each "does not hold" cell:

- 5, all 11: no `decisions` row and no `config` key names a stack, and the harness calls pytest by code (observed: q13, q16, `rota/core/harness.py:380`).
- 6, dry3: the `env:bg_1` note lists no package of icalendar's `test` group (observed: q1, `pyproject.toml:109-117`).
- 6, dry4: the `env:bg_1` note is the same as dry3's (observed: q1).
- 6, dry5: the `env:b_1` note is the same as dry3's (observed: q1).
- 6, dry6c: the same, and the base run errors on `No module named 'hypothesis'` (observed: q15, q5).
- 9, dry3: 1 inherited row, `.github/workflows/test_generate_matrix.py`, of 162 test files (observed: q2).
- 9, dry4: the same 1 of 162 (observed: q2).
- 9, dry5: the same 1 of 162 (observed: q2).
- 10, dry6c: base 157 pass, 4 fail, 1 error on the 162 files at `99619246` (observed: `config.base_run:b_1`).
- 10, dry7 and dry8: base 159 pass, 3 fail on the same files at the same commit, with a different red set from dry6c's (observed: q15).
- 15, dry6: the session rows record `LLMUnavailable ... no answer in 300s`, and the page says "the team could not read a part of the code" (observed: q6, `dry6/t5.log:12`).
- 15, dry7: the session rows record "actively refused", and the log says "the team could not put back code it was not asked to change" (observed: q6, `dry7/t7c.log`).
- 18, dry1: an empty `.rota/worktrees` stays in clickI, with mtime at the merge (observed: `ls -la`).
- 18, dry2: `.rota/worktrees/b_2` with `.venv` stays, and `git status` shows `?? .rota/` (observed).
- 18, dry4, dry5, dry6c, dry7, dry8: the batch row names a worktree at the end, and `worktrees.destroy` sets the column NULL when it removes one (reasoned: `rota/core/worktrees.py:176-196`, q1).

| run | repository | test files in the repository | repository tests the harness holds | base result of those tests | index rows against source files | sessions failed on the ground | model minutes | merged | files rota added at the end |
|---|---|---|---|---|---|---|---|---|---|
| dry1 | clickI `2c8cd3a` | 34 | 34 | 34 pass | 166 paths / 166 files, 876 of 876 defs | 8 | 91.1 | yes | 3 made-name tests, termui change, branch, empty `.rota/worktrees` |
| dry2 | tipsI `99101f1` | 1 | 1, then 4 | 1 pass, then 4 pass | 10 / 7, 9 of 9 | 0 | 22.3 | yes | 3 made-name tests, 2 code files, 2 branches, worktree b_2 with `.venv` |
| dry3 | icalendarI `99619246` | 162 | 1 | 1 pass | 697 / 698, 1470 of 1470 | 0 | 131.7 | yes | 3 made-name tests in a new root `tests/`, caselessdict change |
| dry4 | icalendarI | 162 | 1 | 1 pass | 699 / 698 | 0 | 89.9 | no | worktree bg_1 and branch (reasoned) |
| dry5 | icalendarI | 162 | 1 | 1 pass | 694 / 698 | 0 | 110.1 | no | worktree b_1 and branch (reasoned) |
| dry6 | icalendarI | 162 | 0 | none | 694 / 698 | 18 | 52.7 | no | none recorded |
| dry6b | icalendarI | 162 | 0 | none | 694 / 698 | 9 | 32.9 | no | none recorded |
| dry6c | icalendarI | 162 | 162 | 157 pass, 4 fail, 1 error | 694 / 698 | 0 | 13.3 | no | worktree b_1 (reasoned) |
| dry7 | icalendarI | 162 | 162 | 159 pass, 3 fail | 694 / 698 | 3 | 96.2 | no | worktree b1 and branch (reasoned) |
| dry8 | icalendarI | 162 | 162 | 159 pass, 3 fail | 694 / 698 | 0 | 69.9 | no | worktree bg_1 and branch (reasoned) |
| blind1 | tips copy `ff1f65f` | 4 | 0 | none | 10 / 10, 15 of 15 | 0 | 6.9 | no | none |

## Part D: what the grid does not cover

1. The test folder the doors name. In dry4 and dry5 the program-file door gave `.github/workflows` as the only test folder, and four batch tests were written there (observed: q10, B.4). In dry5 the door called `src/icalendar/tests/test_icalendar.py`, a test file of the base, "a program file of the project" (observed: q10).
2. The repository's own tests are red at the base. dry6c holds 5 red files, and dry7 and dry8 hold 3, among them `test_issue_1445.py` in all three (observed: B.4).
3. The batch tests go where the repository does not keep tests. dry3 and dry7 wrote them in a root `tests/` folder, while icalendar's `testpaths` is `src/icalendar/tests` (observed: B.4, `pyproject.toml:298`).
4. A test that waits for a key press ran into the harness timeout. In dry1 it gave "timed out after 120s" three times at one commit, and the merged version passed (observed: journal seq 141 to 437).
5. The person's identity is on rota's commits. The Developer commits and the test commits carry "Roman Kubiv <romankubiv101@gmail.com>", and only the merge carries "rota <rota@local>" (observed: `git log --format`).
6. Two of three merged diffs remove the final newline of a file the request did not name for that change: `tip_calculator.py` in tipsI and `caselessdict.py` in icalendar (observed: `git diff`, "\ No newline at end of file").
7. Scripts outside rota changed the repositories between runs. `dry5_start.sh` and `dry8_start.sh` run `reset --hard 99619246`, `branch -D` on each `batch/*`, `rm -rf "$ROOT/.rota"` and `git clean -fdq` (observed: the scripts). The icalendar reflog holds two more resets, 2026-11-04 18:28 and 2026-11-06 00:25, that no database of the 11 matches (observed: reflog against `created_at`).
8. The tips lineage starts from rota's own deliveries. The tipsI base `99101f1` is "rota: deliver bg_1", and the blind1 base is the dry2 merge with its three made-name tests (observed: `git log`).
9. The runs used three model server ports: 11434, 11435 (dry6) and 11436 (dry6b) (observed: q6, `config.spill_seen`). A `rota.tools.gate --rerecord-now` process and its pytest children ran during all of blind1 (observed: `blind1/turn_record.md:11`).
10. Stray judgement held batches. `touch_strays` has 19 rows in dry4, 5 in dry5, 11 in dry7 and 2 in dry8, and dry5 and dry7 ended on "the team could not put back code it was not asked to change after 3 attempts" (observed: q21, q23, `dry5/t8.log`, `dry7/t7c.log`).

## Part E: limits

- The repository copies changed after the runs. For dry3 to dry8 the end state comes from the HEAD reflog, the object store (`git cat-file -t`, a read-only command outside the listed set) and the batch rows. The batch branches and worktrees of dry4 to dry8 no longer exist. Whether each one existed at the end of its run is reasoned from the rows and from the start scripts that removed them.
- Nothing shows who removed dry8's worktree and branch. The icalendarI `.rota/worktrees` folder has mtime 2026-11-10 05:05, and no start script of the 11 runs falls after dry8.
- dry1 to dry4 ran rota from `D:/repos/rota` and kept no clone, so their rota commit is not known. dry5 used `79b1cdb0`, dry6 `cd03aa46`, dry6b and dry6c `3b209833`, dry7 `dbd8d920`, dry8 `33c1e697`, blind1 `787d7112` (observed: the `rota_*` clones). The code that wrote each run's rows therefore differs between runs. This read quotes today's code only to name where a row comes from.
- No database stores the text of a page. The page words in B.6 come from the turn logs of dry6, dry6b and dry7. dry1 to dry4 have no turn log file, so their page words for a failure are not known.
- dry1's database holds four measures, and the clickI reflog shows many merges and resets before 2026-10-31. The base `2c8cd3a` rests on the reset at 03:43:32 and `created_at` at 03:44:34.
- The dry6b and dry6c split assumes the `dry6b_after_turn4` copy is the end of dry6b. All its sessions and turns are in the shared file unchanged (observed: q17).
- The `.rota/dry*.db` files were opened by other readers on 2026-11-10. This read did not check them for a change.
- `turns.ms` holds model time only. Harness time and tool time are not in the minutes, and no table records them.
- The `def test_` count is a text count. It includes methods and counts a parametrised test once.
- A "cut of the context" was searched as the runner's sentence "prompt did not fit". A cut that the runner did not detect would not show.
- Statement 18 has no definition on its page. The check in brackets is this reader's.
