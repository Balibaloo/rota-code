# Frame 328, review of pass 4: the test path door and the collection error as a red

Verdict: stands after the named fixes. Finding 1 is high. Findings 2 to 4 are low.

Reviewer: a read-only sub-agent. Worktree `C:/Users/roman/rota_r328d`, detached at 2063d17c on 4bb2656b. No tracked file changed. No model call.

## The commits

- 3348d48a `fix(roles): tests.encode refuses a program file and notes a collection error`
- 2063d17c `fix(briefs): the answer and challenge briefs name the test path form`

Diff 4bb2656b..2063d17c: `rota/roles/api.py` +93 -5, `answer.md` +2, `challenge.md` +1, `tests/rota/test_frame328_path_door.py` +155 (new).

## (a) The points

1. Holds, with one gap. The door refuses `src/click/utils.py` and names `tests` and `tests/test_utils.py`. `tests/test_utils.py` lands. The unindexed `src/click/new_helper.py` lands, as at 4bb2656b. The spelling `./src/click/utils.py` passes the door (finding 1).
   - No test folder in the index: the door refuses every indexed non-test path. The text names `tests` and `tests/test_<stem>.py`. A new `tests/test_a.py` lands.
   - Tests beside the modules (`pkg/test_x.py` next to `pkg/x.py`): `pkg` is a test folder, so the door passes `pkg/x.py`. The door is blind there. It refuses nothing that is right.
   - Root tests (`test_x.py` at the root): the door refuses `pkg/x.py` and names "the root" and `test_<thing>.py`.
   - A right encode that the door refuses: only an indexed test file of a non-default name, `tests/check_x.py`, in a folder with no `test_` file (finding 4).
2. Holds. `_refuse_unindexed_files` binds `test_shaped = _test_shaped` and `test_dirs = _test_dirs(indexed)`. The regex and the set expression are the same text as before. The `indexed` set is computed as before. `test_frame302_unindexed_path.py` is green.
3. Holds. The branch needs `verdict == "error"`, a non-None `notes`, a marker in the output, and `_developer_committed`. Probes P3b, P3c and P3d each gave the plain `{'id': ...}` with no note: an `error` with no marker, a `fail` with the marker, and the marker with no Developer receipt. Pass 2c's test is `tests/rota/test_frame304_arrange_door.py::test_a_failed_import_line_lands_whatever_the_name`, 2 passed. Test 5 of the new file adds the `error` shape of pass 2c and is green. The tst_c4 body reaches the Tester as a `SyntaxError` only under `filterwarnings = error` (P2). Without that setting, the run is `pass` and no note comes (P3a). The guard `_developer_committed` is batch-wide, not per criterion (finding 2).
4. Holds. The note for the module case, from test 4 and probe P2, follows.

   ```
   The run of this body on the batch's head errors when pytest collects `tests/test_shorten.py`: `ModuleNotFoundError: No module named 'click.shorten'`. No test in the body runs. The test is stored. The batch's head holds the Developer's commit. Fix the test and encode it again with the same id.
   ```

   The tst_c4 note has the same frame and quotes the `E` line `SyntaxError: "<backslash>M" is an invalid escape sequence...`. P2 printed `encode_noted == {('bg_3', 'c_1_format_filename_example', 'tests/test_shorten.py')}`. A re-encode with the same id and a raw string returned `version: 2` and the note of pass 3's `test_s271_re_encode_after_the_note_lands_as_version_2`. Test 4 does not pin the re-encode (finding 3).
5. Holds. The line has the same words in both files, and it is bold in `answer.md` only.

   ```
   The path of `tests.encode` is a test file, `tests/test_<thing>.py`, and never the file of the code under test.
   ```

   No other line of either prompt names a path. `tests_missing.md` is not in the diff, and its one `touch` line is unchanged. The stale count comes from `casestatus.wanted_pins(case, 'qwen3:8b').prompt_hash` at 4bb2656b and at 2063d17c. 9 of 167 cases change hash, all `L1-TS-*`. 5 of the 9 hold a qwen3:8b run at the base hash in `cassettes.db`, so 5 recorded cases go STALE.
6. Holds. The touched file and its neighbours (`path_door`, `arrange_door`, `encode_note`, `restage`, `unindexed_path`, `invoke_door`) give 1 failed, 108 passed. The one red is `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`. A `git archive` copy of 4bb2656b gives the same red at line 381, `DID NOT RAISE <class 'ValueError'>`. The base holds no path door and no collection branch, so the red does not come from these doors.
7. Holds. No existing test file changed. The new file removes nothing. Test 1 catches `Exception`, not `ValueError`, but it asserts the full text and `seen == []`.

## (b) Findings

1. `rota/roles/api.py:7424` and `:9246`, high, CONFIRMED. `tests_encode` normalises only the backslash. So `./src/click/utils.py` is not in `indexed`, and the door returns. Probe P5 encoded the S326 body at `./src/click/utils.py`. The run wrote over the module and errored on the circular import, and the test landed with that path. The night 167 wall stays open for one more spelling. An absolute path has the same gap by the same code. Fix: normalise the path with `posixpath.normpath` before the door, and refuse an absolute path or a path out of the root.
2. `rota/roles/api.py:17490`, low, PLAUSIBLE. `_developer_committed` reads any Developer receipt on the batch. After a commit for one criterion, a module-level import of a module that the Developer still owes for another criterion gets "Fix the test". The docstring of pass 2c's test rules that import right. The `fail` note hedges on the criterion's words, and the collection note does not. Test 4 `[module]` pins the unhedged words for an import of a missing project module. Fix: hedge the note as the `fail` note does, or keep it silent when the missing name is in the criterion's surface or the batch's rows.
3. `tests/rota/test_frame328_path_door.py:114`, low, CONFIRMED. Test 4 checks the note only. No test pins the `encode_noted` key or the version 2 re-encode for the collection branch. Probe P2 shows that the behaviour is right today. Fix: add the second encode of P2 to test 4 and assert `version == 2`.
4. `rota/roles/api.py:7428`, low, PLAUSIBLE. The door reads only the default pytest names. A project with `python_files = check_*.py` and no `test_` file in that folder has its indexed test files refused (P1, `tests/check_x.py`). The Tester re-encodes at such a file only when its own stored test has that name. Fix: read `python_files` from the pytest config of the project in `_test_shaped`.

Outside the points: the brief line names `tests/` for every project, and the door names the test folders of the index. A project that keeps its tests in `test/` or beside the modules gets two different answers. This is no defect today. Measure it on a night before a change.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r328p4/`.

- `probe_r328p4.py` ran from the worktree root with `-p tests.rota.conftest -s`: 7 passed. P1 calls `_refuse_program_path` on 12 index shapes in memory. P2 encodes tst_c4 under `filterwarnings = error`, then encodes again with the same id. P3a runs tst_c4 without that setting. P3b, P3c and P3d fake `_encode_run` for each guard. P5 encodes at `./src/click/utils.py`.
- `hashes.py` writes the qwen3:8b prompt hash of each case to `head.json` (the worktree) and `base.json` (the archive). One `python -c` call read `cassettes.db` with `mode=ro` and counted the changed hashes that hold a run.
- `base/` is `git archive 4bb2656b`. The known red ran there.
- The pytest runs of point 6 and the test of pass 2c ran in the worktree.

## (d) Usage

About 68k tokens in total, by the count of tokens left that the harness reports. The harness does not split input and output.

## Pass 4b: review of a79474fd

Verdict: pass 4b stands. Findings 1 to 3 of the pass 4 review are closed. One new low finding follows.

Commit: a79474fd `fix(roles): tests.encode reads the normal form of the test path`, on 2063d17c. `git log --oneline -1` in the worktree printed a79474fd.

### The points

1. Closed. `tests_encode` runs `posixpath.normpath` after the backslash step. It then refuses a path that is absolute, has a drive, or starts with `..`. Probe Q1 started no run for any refused form.
   - `./src/click/utils.py`, `src/./click/utils.py` and `src/click/../click/utils.py` are refused with this text: `path 'src/click/utils.py' is a program file of the project. The harness writes the test at its path, so the test replaces that file. Write the test in a test folder of the index: tests. For example, path='tests/test_utils.py'`
   - `../x.py`, `C:/x.py`, `/x.py`, `//x.py` and `tests/../../x.py` are refused with this text: `path '../x.py' is outside the project. The harness writes the test at its path inside the project. Name the file tests/test_<thing>.py`. Each form shows its own normal form. `tests/../../x.py` shows as `'../x.py'`.
   - `tests/test_x.py` and `./tests/test_x.py` land. Each one ran once and got the `fail` note.
   - No form lands over the module.
2. Closed. Probe Q2 quotes the collection note: `... No test in the body runs. The test is stored. The batch's head holds the Developer's commit. If the criterion's words give the value that the run shows, the test is wrong. Encode it again with the same id.` The last three sentences are the same words as the `fail` note in Q1.
3. Closed. Test 4 now encodes again with the same id and `FIXED_BODY`. It asserts `version == 2`, no `unchanged`, and one staged test that holds the new body. The old `endswith` assertion is now a longer `endswith`, so no assertion is weaker.

Counts: `tests/rota/test_frame328_path_door.py` gives 13 passed, and pytest exits with code 0. That exit code comes from a separate run with no pipe. The neighbour files (`arrange_door`, `encode_note`, `restage`, `unindexed_path`, `invoke_door`) give 100 passed and 1 failed. The one red is the known `test_a_session_with_no_batch_reads_the_root`, which is red at 4bb2656b. A grep of `tests/rota` found no other `tests.encode` call with a `./` or `/` path.

### Finding

5. `rota/roles/api.py:17453`, low, PLAUSIBLE. The hedge now matches the `fail` note word for word, but a collection error shows no value. The words "the value that the run shows" give the Tester nothing to compare for an import or a SyntaxError. A small model can read the condition as false and keep a test that never runs. Fix: for a collection error, write "If the criterion names the module or name that the run lacks, the test is right. Otherwise fix the test, and encode it again with the same id."

### Probe

`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r328p4/probe_r328p4b.py`: 11 passed. It encodes S326's body at 10 path forms with the real run (Q1), and encodes the pass 2c body after the Developer's commit (Q2).

Usage for pass 4b: about 9k tokens, by the count of tokens left that the harness reports.
