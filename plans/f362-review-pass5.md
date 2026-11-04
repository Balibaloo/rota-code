# Review: frame 362, pass 5, `044b76de`

Reviewer: subagent of 94cb1260, 2026-11-04 16:23. Worktree
`C:/Users/roman/rota_r362`, read-only. No tracked file changed.

## Verdict: fix

The rule in `ruling_for` is correct for icalendar, and the tests pin it.
The fix does not deliver a merge on icalendar, for two reasons. First, 5
inherited test files are red at the base, and the review and merge gates
read every inherited red (finding 1). Second, the refusal that sends the
Tester to a test folder still names `.github/workflows` first (finding 2).
Do not continue the held dry run. Start it again at the fix, after
findings 1 and 2 (point 5).

## (a) The eight points

1. The rule: CONFIRMED. Each of the four claims holds on `dry5.db` and on a fixture. Two shapes give a wrong kind: findings 3 and 5.
2. The frame 324 ruling: CONFIRMED departure, wider than the brief's paragraph. See the paragraph below.
3. Downstream reach: CONFIRMED. The areas drop from 22 to 11. Two doors change in a way nobody wants: findings 2 and 6.
4. The base run: CONFIRMED. The base run takes about 5.3 minutes, and each harness run after it about 4.4 minutes. The push is a context cost, not a new wall. The base-red gate is a new wall (finding 1).
5. The held dry run: CONFIRMED. The 161 tests join `b_1`, no base run is recorded, and no door can say "it passed before this batch". Start the run again.
6. The tests: CONFIRMED. 4 of 9 cases are red at `623b3ada`, and 9 of 9 are green at `044b76de`. No CR bytes. The stat matches. Two claims of the brief have no test (finding 7).
7. Deviation 1: CONFIRMED right, with one wrong edge (finding 5). The residue count is one line below.
8. Outside the points: findings 8 and 9.

### Point 2, the departure from the frame 324 ruling

The basename half of the ruling holds: `src/pkg/test_helpers.py` under a
`src` program ruling stays `program`. The other half changes. Before the
fix, "the frame's kind" for every path below a ruled prefix was the word of
the judge or the principal. After the fix, a folder name from `TEST_DIRS`
outranks a `program` or `surface` ruling above it. The brief's paragraph
calls the cut path "a path the judge never ruled". The judge did rule it,
by the prefix rule that `ruling_for` documents. The paragraph also says the
principal's ruling "on that directory" still wins. It does not say that a
`decided` ruling above the test folder loses: a principal who rules
`src/icalendar` as `program` now gets `attached` for its tests. The cut
also applies to files with no test shape, such as `django/test/client.py`.
So the departure is: a folder-name heuristic now decides the kind below a
test-named folder, against the frame's ruling, the principal's included.
The question for Roman: does a test-named folder outrank his own ruling on
the folder above it?

### Point 7, the residue in one line

The next dry run on icalendar must count 11 survey areas with none under
`src/icalendar/tests`, and 162 `inh_` rows in the first batch with a base
run record of 162 entries.

## (b) Findings

### High

1. `rota/core/predicates.py:1561-1564` and `rota/core/lifecycle.py:1130-1136`, high, CONFIRMED.
   The `review` predicate and `mergeable` count every non-pass inherited run at the head.
   They never read the base run record. On icalendar 5 files are red at the base:
   `hypothesis/test_fuzzing.py`, `test_issue_1445.py`, `test_issue_313_globally_unique_tzid.py`,
   `test_rfc_6868.py` and `test_with_doctest.py`. Probe `p4_gate.py`: with one inherited
   test red at the head and red at the base, `predicates.review` gives no wake for `b_1`.
   With that test green, the Critic wakes. Only the principal can lift the block, by a
   retire of each test (`scheduler.live_tests`). So no icalendar batch reaches the Critic
   or the merge. Report residue 2 says the doors do not blame the batch. That is true for
   the Developer's text in `sandbox.project_tests_fact`, and false for the gates.
   Fix: make the review and merge gates skip an inherited test that is red at the base with the same result.

2. `rota/roles/api.py:8640-8651`, high, CONFIRMED for the text, PLAUSIBLE for the Tester's reaction.
   `_refuse_program_path` sorts the test folders by depth, so `.github/workflows`
   (one slash) comes before `src/icalendar/tests` (two). Probe on `dry5.db`: the refusal
   reads "Write the test in a test folder of the index: .github/workflows, src/icalendar/tests,
   ..." and "For example, path='.github/workflows/test_string.py'". That is the path of dry
   run 4's wall 16 and dry run 5's wall 9, which the brief says this fix closes.
   Fix: rank the test folders by the count of test files they hold, or put a dot-folder last.

### Low

3. `rota/onboarding/areas.py:72-81`, low, CONFIRMED.
   The cut applies to every file below a test-named folder, also a program file with no
   test shape. Fixture probe: `django/test/client.py` under `django` program reads `attached`.
   `openapi_core/spec/paths.py` reads `attached`. `lib/sqlalchemy/testing/suite/test_types.py`
   reads `attached`, so `harness.inherit` would run it. These packages ship to users. No
   sample tree has the shape, so no case shows it.
   Fix: cut only at a test folder whose subtree holds a test-shaped file, and give the judge the nested test folders.

4. `rota/core/harness.py:158-160`, low, CONFIRMED.
   `harness.run` runs each live test as its own pytest child at every new head. On icalendar
   that is 161 children and 263 s per run (probe `p4_all.py`). The report names the cost of
   the base run only. The dry run's wall time grows by about 4.4 minutes per Developer commit.
   Fix: run the inherited group in one pytest call, and re-run file by file only on a red group, as `record_base_run` does.

5. `rota/onboarding/areas.py:79-81`, low, CONFIRMED.
   The `continue` drops a skipped `program` ruling, so a shorter ruling of another kind wins.
   Fixture probe: `vendor` ignore and a `decided` ruling `vendor/lib` as `program` give
   `ignore` for `vendor/lib/tests/test_x.py`. A careful reader expects `attached`, from the
   most specific ruling's cut. The edge needs a `decided` ruling inside an ignored folder.
   Fix: take the most specific ruling first, and fall to the heuristic when that ruling is a cut `program` or `surface` ruling.

6. `rota/core/runner.py:4323-4332`, low, CONFIRMED.
   `_index_test_files` stops at 80 files in grain order. On `dry5.db` it now finds 162, so the
   Architect's re-annotate push shows 80, and `src/icalendar/tests/test_parsing.py` is not one
   of them. The list carries no word that it is cut.
   Fix: say the count that the list leaves out, or rank the files by the item's words before the cut.

7. `tests/rota/test_f362_pass5_test_dir_ruling.py`, low, CONFIRMED.
   No case pins a `surface` ruling that stops at a test folder, although `PROGRAM_KINDS` holds
   `surface`. No case pins a `decided` ruling above the test folder that the cut removes,
   although the brief states it. Both behave as the brief says in the fixture probe.
   Fix: add the two cases.

8. Outside the points. `rota/onboarding/areas.py:55-57` and `areas.py:205-208`, low, CONFIRMED.
   The `ruling_for` docstring still says "the most specific ruling whose prefix covers the path".
   The `propose` comment still says a `program` ruling is "surveyed even where a heuristic
   would attach it". Both are now false below a test folder.
   Fix: name the test-folder cut in the docstring and in the comment.

9. Outside the points. The gap against `plans/dry3-key-score-2026-11-03.md`, low, CONFIRMED.
   After the fix `areas.propose` on `dry5.db` gives 11 areas, against the key's 9. The rest
   of the gap is `news` (71 files, judge `program`) and `src/icalendar/fuzzing/corpus`
   (32 files). The fix closes the test half of the gap only.
   Fix: none in this pass. Count the two areas in the next dry run's score.

### Point 4, the numbers

- The base run: one pytest call for the 161 inherited files, 54 s (the report's measure).
  The group is red, so 161 children follow, 263 s measured. Total about 317 s, inside
  `lifecycle.start`. The slowest file is `test_with_doctest.py` at 35.6 s, so the 120 s
  timeout does not bind.
- The push on the `b_1` shape, 4 own tests and 161 plus 1 inherited, 5 red with 2,000
  characters of output each: `tests.load` renders 51,951 characters. The per-key cap cuts
  it to 20,125. The own tests survive. 2 of 5 red rows survive. The 157 green rows cost
  124 characters each, 19,572 in total.
- The Critic gets the full `tests.load` in `critic/review`. With finding 1, the Critic wakes
  only when every test is green, so it gets about 20,000 characters of "passing, not shown"
  lines. That is about 5k tokens of context. No other key is lost, because each key has its own cap.
- The Developer in `tests_failing` gets the red rows only. The 5 base-red bodies are 18,776
  characters before their output. A sixth red row, the issue 1501 regression, sorts after
  them by path, so the cut can drop its body. PLAUSIBLE: the `what that means` key keeps its
  own cap and names the test.
- The push is not a new wall. The base-red gate of finding 1 is.

### Point 5, the held run

Probe `p45_push_held.py` on a copy of `dry5.db`, with `execute.run` stubbed:

- `harness.inherit` writes 161 rows into `b_1`.
- `record_base_run` does not run. `base_run:b_1` exists with one entry, and the batch has a head.
- `sandbox.project_tests_fact` on `inh_96f585ba` (`test_parsing.py`) says "no base run of inh_96f585ba is on record. A challenge has no side there".
- The 5 base-red tests get the same text. So the Developer is told to find what the change broke in tests that the change did not break.

Start the run again at the fix, on a new batch, so the base run records 162 entries
before any commit. Fix finding 1 first, or the new run stops at the review gate.

## (c) Probes

All are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/94cb1260-d91d-4109-aa38-7528925f5f83/scratchpad/r5/`.

- `p1_dry5.py`: the kinds on `dry5.db`, read-only. 338 of 338 test-folder grains are `attached`. All 694: 199 `program`, 494 `attached`, 1 `ignore`. `_test_dirs` gives 9 folders.
- `p1_fixture.py`: 15 path shapes on fixture databases. The 7 claims of the brief hold. It also shows the shapes of findings 3 and 5.
- `p3_propose.py`: `areas.propose` on `dry5.db` before (`PROGRAM_KINDS` empty) and after. 22 areas and 537 program files, then 11 areas and 199 files.
- `p4_time.py` and `p4_all.py`: each icalendar test file alone, on the pass's provisioned clone `.../scratchpad/ical5`, with the harness plugin. 161 files, 263.3 s, 5 red.
- `p45_push_held.py`: the copy `dry5_copy.db`. It runs `harness.inherit` on `b_1` with `execute.run` stubbed, then `project_tests_fact`, the rendered size of `tests.load` and `_index_test_files`.
- `p4_gate.py` and one inline call: `predicates.review` and `lifecycle.mergeable` on the copy, with one base-red inherited test.
- `base/`: a `git archive` of `623b3ada` with the two new test files. 4 failed, 5 passed.
- In the worktree: the two new files and the three frame 324 files, 42 passed. CR bytes of the 3 touched files at `044b76de`: 0 each.
- `_refuse_program_path` on `dry5.db` for `src/icalendar/parser/string.py`, one inline call: the refusal text of finding 2.

## (d) Usage

- Input tokens: about 85k of context at the end, against the cap of about 60k. The timing runs and the gate reads took the excess.
- Output tokens: about 14k.
- Total: about 99k.

## Pass 5b, `b81f9639`

Second look, 2026-11-04, read-only, cap 20k. Finding 4 goes to pass 5c and is not reviewed here.

### Verdict: fix

The gates, the refusal order, the cut rule and the list cut are correct. One new high
finding remains: the fix-loop predicates still wake the Developer for a test red at the
base. The 6 touched test files pass with the frame 324 and F9 files, 44 passed. The 10
touched files hold no CR bytes.

### The findings of pass 5

1. Fixed. `harness.reds_that_hold` (`rota/core/harness.py:475-489`) is the one reader for `predicates.review` and `lifecycle.mergeable`. `principal.touch_words` names the base-red files.
2. Fixed. `_refuse_program_path` (`rota/roles/api.py:8640-8646`) ranks by the count of test files, so `src/icalendar/tests` (111 files) comes first.
3. In part. `django/test/client.py` stays `program`. Probe: under a `numpy` judge ruling, `numpy/testing/overrides.py` is still `attached`, because `_holds_a_test_file` reads the whole subtree and finds `numpy/testing/tests/test_utils.py`. Fix: require a test-shaped file directly in the cut folder.
5. Fixed by a different rule. A `decided` ruling now covers its whole prefix, so `vendor/lib/tests/test_x.py` is `program`. That follows "the principal rules what he names" and frame 324. My expectation of `attached` assumed the old cut for a `decided` ruling. The test is right. A judge ruling that the cut removes now gives the heuristic, not a shorter ruling.
6. Fixed. `_callers_of` reads `code_calls.src`, which holds a file path. On `dry5.db`, `test_parsing.py` calls `string.py::_foldline`, so it comes first. The count row is a string inside a list of paths. That is acceptable.
7. Fixed. The new cases pin the `surface` cut and a `decided` ruling above the test folder.
8. Fixed. The `ruling_for` docstring names the cut. The `propose` comment names the exception.
- Point 2 paragraph: the departure for a `decided` ruling above the test folder no longer exists. The remaining departure is for the judge's ruling only, which the brief's paragraph covers.

### The two questions of the report

- Any red result is excused, not only the same result. Both rules are too weak, because the excuse is per file. A Developer regression inside a base-red file passes both gates. On icalendar, `test_rfc_6868.py` and `test_issue_1445.py` are base-red files that parse content lines. A same-result rule would not catch a new failure in a file that already fails. See new finding 11.
- The `vendor/lib` case: the expectation of `program` is right under the new rule. See finding 5 above.

### New findings

10. `rota/core/predicates.py:1137-1145` (`tests_failing`), `predicates.py:1215-1219` (`exhausted`) and `rota/core/scheduler.py:2238-2244` (`park_reds`), high. CONFIRMED by reading. The effect is PLAUSIBLE, because I ran no loop.
    The three predicates read `latest_runs` for `fail` or `error` with `live_tests` only. They do not use `reds_that_hold`.
    So the 5 base-red files wake the Developer at every head until the attempt cap or the challenge bound is reached. The batch can then stop as exhausted on tests it never broke.
    Fix: make `tests_failing`, `exhausted` and `park_reds` drop `harness.base_red_ids`, as the gates do.

11. `rota/core/harness.py:466-489`, low. PLAUSIBLE.
    `base_red_ids` excuses a whole file by its id, for any red result at the head.
    A new failure inside a base-red file holds no gate, and only the touch line tells the principal.
    Fix: excuse a test only when `harness.error_line` of the head output equals that of the base output.

### Probes of pass 5b

- One inline `python -c` call: `kind_of` under a `numpy` judge ruling, with `numpy/testing/tests/test_utils.py` indexed. The result is `attached` for `overrides.py`.
- One inline call on `dry5.db` read-only: `code_calls` rows for `_foldline` give file paths in `src`.
- In the worktree at `b81f9639`: the 4 pass 5 and pass 5b test files, `test_frame324_one_reader.py` and `test_f9_test_file_one_reader.py`, 44 passed. `ROTA_DEV_DB` was `.../scratchpad/r5/dev5b.db`.

### Usage of pass 5b

About 18k input tokens and 4k output tokens, against the cap of 20k.

## Pass 5c, `458a3ea2`

Second look, 2026-11-04, read-only, cap 20k. Worktree `C:/Users/roman/rota_p362w`.

### Verdict: fix

The grouped run, the fix-loop predicates and the cut are correct. Finding 11 is fixed in
part: the 2,000-character tail can hide a new red node at the head, so a file is wrongly
excused (finding 12). The 5 test files of pass 5, 5b and 5c pass, 24 passed. The 8
touched files hold no CR bytes.

### The findings of pass 5 and 5b

4. Fixed. `harness.run` and `record_base_run` share `_run_group` (`rota/core/harness.py:419-471`). Only a file that the summary names green and never red gets a grouped pass. Each other file runs alone.
10. Fixed. `tests_failing`, `exhausted`, `scheduler.failing_attempt` and `park_reds` read `harness.drop_base_reds`, which is the reader that the gates use.
3. Fixed. The cut needs a test-shaped file directly in a test folder on the path, or a test-shaped grain. `numpy/testing/overrides.py` stays `program`, and `numpy/testing/tests/test_utils.py` is `attached`.
11. In part. A base-red file is excused only when its red node ids at the head are a subset of the base's. The node ids come from the tail of the output, so the rule is as strong as the tail (finding 12).

### The two questions

- A pass for a test that pytest never ran: no, with one exception. A file that the summary does not name runs alone. A deselected file and a file with no item give exit code 5 alone, which is `error`. A file skipped whole is `SKIPPED` in the group and exit code 0 alone, so both paths give `pass`, as before. `execute._local` does not cut stdout, so a red file with passing tests keeps its `FAILED` line and runs alone. The exception is the branch "exit code 0 and no summary" (`harness.py:456-458`). That branch passes every file, also a file that collected no item. That branch is reachable only when a project hides the summary, for example with `-p no:terminal` in `addopts` (finding 13).
- The tail: losing a base node makes the rule hold a file, which is the safe side. Losing a head node excuses a file, which is the wrong side. Probe: a file with 40 base failures keeps 27 in the 2,000-character tail. A new failure that runs first is not in the head tail, and `now <= before` is True, so the file is excused.

### New findings

12. `rota/core/harness.py:576-608` (`_red_nodes`, `drop_base_reds`), high, CONFIRMED.
    `_red_nodes` reads the stored output, which `_tail` cuts to 2,000 characters. About 27 `FAILED` lines fit.
    A file with more red nodes than the tail holds hides a new red node of the head. Then the gates and the fix loop excuse a regression.
    `test_parsing.py` holds 305 tests, so a wide break of `_foldline` reaches this size.
    Fix: parse the red node ids from the whole stdout in `_run_one`, and store them beside the output, in the base record and the run row.

13. `rota/core/harness.py:456-458`, low, PLAUSIBLE.
    With exit code 0 and no summary line, every file of the group gets `pass`, with no proof that it ran.
    Fix: drop the branch, so that a file that the summary does not name runs alone.

### Probes of pass 5c

- One inline `python -c` call with `harness._tail` and `harness._red_nodes` on a synthetic pytest output of 40 and 41 failures: 27 of 40 base nodes kept, the new head node not visible, and the subset True.
- A reading of `execute._local` (`rota/core/execute.py:32-44`): stdout is whole.
- In the worktree at `458a3ea2`: the 3 pass 5c test files, `test_f362_pass5b_base_red_gates.py` and `test_f362_pass5_test_dir_ruling.py`, 24 passed. `ROTA_DEV_DB` was `.../scratchpad/r5/dev5c.db`.

### Usage of pass 5c

About 17k input tokens and 4k output tokens, against the cap of 20k.
