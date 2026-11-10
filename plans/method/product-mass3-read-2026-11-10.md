# Build and judgement in 11 runs, the blind read of mass 3, 2026-11-10

Written by one reader for frame 364. The reader got no hypothesis and read
no other reader's page. Every query opened a run database with
`file:<path>?mode=ro`. The scripts are in the reader's scratch directory
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass3/`
(`list.py`, `dump.py`, `jr.py`, `res.py`, `extra.py`, `devs.py`). The
dumps of each batch are `d_<run>_<batch>.txt` in the same directory.

## Result

The 11 databases hold 9 batches, so the reader read all 9 and drew none (observed: `list.py`).
Dry runs 6, 6b and blind run 1 hold no batch (observed: `list.py`).
Three batches merged: dry1 bg_1, dry2 b_1 and dry3 bg_1, each on one Developer commit with a Critic pass on that commit (observed: `verdicts`, git).
Dry2 b_2 is abandoned, dry4 bg_1 is still `running`, and four batches of the fold request are `deferred` and parked (observed: `batches.status`, `park_ask` sessions).
Of 119 Developer sessions on the 9 batches, 97 landed no code write and made no commit (observed: `devs.py`).
Three Developer sessions have `committed = 0`, all in dry7, and each failed on `LLMUnavailable` (observed: `turns` of s217 to s219).
No batch has a fail verdict, and the only violated findings are the 12 of dry5, which the Critic dismissed and which woke no Developer session (observed: `verdicts`, `finding_rulings`, `sessions.wake_kind`).
In 7 of 8 batches with tests the Tester read implementation files with `code.source` (observed: `extra.py`).
In 6 batches a batch test changed from fail to pass at a commit the code did not change, after a re-encode of the test (observed: `test_run_journal`, `tests.version`).
Four batches have stray rows, the Architect judged a mistake in each, and only dry8 has a head commit with no mistake row (observed: `touch_strays`).
The Part A statements that fail most often are "the test follows from the criterion" (7 batches), "the Tester never sees the implementation" (7) and "one test per criterion" (3) (observed: Part C).
In dry3, dry4 and dry5 the "repository's own tests" are 1 test file of the 162 the repository holds (observed: `tests` rows with `criterion_id IS NULL`, `git ls-tree`).

## Part A: the design's statements on build and judgement

1. The Tester encodes one test per criterion (`rota/MAP.md:68`). [Check: one live `tests` row per live `criteria` row.]
2. The test comes from the criterion alone and encodes the criterion, never the implementation (`rota/MAP.md:68-69`, `rota/ROLES.md:189-190`). [Check: the test's assertion against the criterion's words, reasoned.]
3. The Tester writes before the implementation exists (`rota/DECISIONS.md:1070-1071`, the Tester's charter quoted). [Check: the first `tests_missing` session against the first Developer commit.]
4. The Tester never sees the implementation and has no access to the codebase (`rota/DECISIONS.md:1071-1072`). [Check: `tool_calls` of `code.source` in Tester sessions.]
5. A test that passes trivially is worse than no test, because it reports as coverage (`rota/ROLES.md:194-195`). [Check: a test of a change criterion that passes on the base commit, or an assertion that cannot fail.]
6. The Developer never builds what nobody asked for (`rota/ROLES.md:172`). [Check: a stray row the Architect judged a mistake.]
7. The harness runs the batch's tests and the repository's own (`rota/MAP.md:70-71`). [Check: inherited `tests` rows against the test files of the repository.]
8. Failing tests wake the Developer (`tests_failing`), bounded by `loop_cap` (`rota/MAP.md:71-72`). [Check: Developer wakes after a red run, `attempt` against `loop_cap`, 10 in `rota/core/config.py:59` today.]
9. A session commits or discards before it ends, and a worktree with uncommitted changes at session end is a fault (`rota/LAWS.md:169-171`). [Check: writes "not committed" at session end, the runner's account.]
10. Boot writes the real HEAD back to `batches.head_commit`, so every reader of the head sees the commit that exists (`rota/LAWS.md:158-162`). [Check: `head_commit` against the last commit result and git.]
11. A commit that touches paths the prediction never named writes `touch_strays` rows (`rota/MAP.md:73-74`). [Check: files of each commit against `batch_touch`.]
12. The prediction is never a permission, and nothing rejects a diff for straying outside it (`rota/LAWS.md:339-340`). [Check: commits with stray rows landed.]
13. The Architect judges each stray foreseen or a mistake (`rota/MAP.md:75`). [Check: `touch_strays.status` at the run's end.]
14. A mistake wakes the Developer (`touch_mistaken`) to take it out (`rota/COMPLETION.md:50-51`). [Check: `touch_mistaken` sessions, and the mistake rows of later commits.]
15. The Critic gives one verdict per batch on one commit, reads the diff against the criteria, and a fail wakes the Developer (`rota/ROLES.md:204`, `rota/MAP.md:78-79`). [Check: `verdicts` rows, their commit, `verdict_failed` wakes.]
16. The Architect reads the diff against the constraints, and a violated finding wakes the Developer (`finding_violated`) (`rota/MAP.md:80-82`). [Check: `findings`, `finding_violated` wakes.]
17. The merge gate runs the harness, then the Critic, then the Architect (`rota/LAWS.md:233`). [Check: session order of review and findings.]
18. `lifecycle.mergeable` holds a batch with no commit, an untested criterion, no verdict on the head, a failed verdict, an unjudged stray or a violated finding, and the scheduler merges the rest (`rota/MAP.md:83-86`). [Check: the conditions at the merge or at the run's end.]
19. The merge gate holds while a stray is unjudged or a mistake is still in the head commit (`rota/COMPLETION.md:51-52`). [Check: open or mistake rows at the head, and `status`.]
20. Exhaustion climbs one rung at a time from Developer to Architect to Vision Keeper to Liaison, a wake past its cap is quarantined and said out loud, and it is never silence (`rota/LAWS.md:185-191`). [Check: `tick:exhausted`, `tick:quarantined` and `tick:park_ask` sessions in order.]

## Part B: every batch

The list, ordered by run then id (observed: `list.py` on `batches`):
dry1 bg_1 merged, dry2 b_1 merged, dry2 b_2 abandoned, dry3 bg_1 merged,
dry4 bg_1 running, dry5 b_1 deferred, dry6c b_1 deferred, dry7 b1
deferred, dry8 bg_1 deferred. Counts per run: dry1 1, dry2 2, dry3 1,
dry4 1, dry5 1, dry6 0, dry6b 0 (the copy `dry6b_after_turn4`), dry6c 1,
dry7 1, dry8 1, blind1 0. The count is 9, so no draw was made.

Common sources for each block: criteria and tests from `criteria` and
`tests` (the body is the newest version), sessions from `sessions` with
`wake_refs` naming the batch plus Developer and Tester `message` sessions,
tool results from the `OK` and `ERROR` lines in `turns.user` and the
runner's account in `turns.completion`, test results from
`test_run_journal` grouped by commit and `attempt`, and the newest run from
the view `latest_runs`. "Wrote nothing" means no `code.write` landed a
change and no `code.commit` returned `committed: true`.

### dry1 bg_1 (clickI), merged

1. Ticket tk_1: "click.pause() returns True when it waited for a key and False when it skipped because stdin or stdout is not a terminal". Criteria: `tk_1_criteria_waited` "When click.pause() suspends execution awaiting a keypress from the user, it must return True." `tk_1_criteria_skipped` "When click.pause() skips execution because stdin or stdout is not a terminal (e.g., piped input), it must return False." `tk_1_criteria_terminal_check` (v2) "The return value is False when raw_terminal reports a non-terminal, and True when execution suspended for a keypress."
2. Tests (`tests.body`, also git aa7af37). `tst_waited` (v9, waited): patches `click.termui.isatty` True and `getchar`, asserts `pause() is True`. The assertion follows. The patch targets are not in the words. `tst_skipped` (v1, skipped): patches isatty False, asserts `pause() is False`. It follows. `inh_03a1b2c3` (v3, terminal_check): asserts `raw_terminal().__enter__() == -1`. It does not follow, because the criterion speaks of the return value of `pause()` (reasoned). 34 inherited tests.
3. Developer, 18 sessions: s145 batch_start commits 4fcd6d73. s149 exhausted. s151 message. s192 batch_start, write "unchanged", commit "nothing changed". s193, s201, s203, s266 tests_failing, each write refused with "you challenged the test". s196, s199, s205, s207, s209, s257 tests_failing, challenges only. s198, s236 message, commit "nothing changed". s256, s265 batch_start, no change. 17 wrote nothing.
4. All 437 journal rows are on 4fcd6d73. Seq 35-69: `inh_03a1b2c3` fail. Seq 105-400: `tst_waited` error, then fail. Seq 401-437: 3 of 3 batch tests and 34 of 34 inherited pass. The code did not change between the reds and the green.
5. No strays.
6. Critic s269: pass on 4fcd6d73, reason empty, lines `{"terminal_check": "return False\n    return True", "waited": "return True", "skipped": "return False"}`. Architect s270: f1, k0, satisfied, `src/click/termui.py`.
7. No fail verdict and no violated finding.
8. Merged: clickI 09c82f3 "rota: deliver bg_1", files `src/click/termui.py` and the three test files. `latest_runs` holds 37 of 37 pass on 4fcd6d73.
9. Sessions: Developer 18, Tester 16, Architect 3, Critic 1. 0 have `committed = 0`.

### dry2 b_1 (tipsI), merged

1. Ticket tk_1: "the program raises a ValueError when the tip percentage is invalid". c_1 "The program raises a ValueError when the tip percentage is below 0 or above 100." c_2 "When the tip percentage is valid (between 0 and 100 inclusive), the program returns the calculated tip amount without raising an exception." c_3 "The ValueError raised for invalid percentages must be a standard Python ValueError with no additional message requirements."
2. Tests (`tests.body`, git 51231b6). `tst_tip_invalid_low` (v3, c_1): `pytest.raises(ValueError, match="Tip percentage must be between 0 and 100.")` for -5 and 101. The message literal does not follow, and c_3 says no message (reasoned). `tst_tip_valid` (v3, c_2): asserts 0.0, 100.0 and 50.0 on total 100. The formula is not in the words (reasoned). `tst_tip_error_type` (v1, c_3): asserts a ValueError for -1. It follows. 1 inherited test, `tests/test_calculate_tip.py`.
3. Developer, 3 sessions: s55 batch_start commits e40742e3, its test-file writes refused ("a test file, and the tests are the Tester's"). s57, s59 tests_failing, challenges only. 2 wrote nothing.
4. All journal rows on e40742e3: att 2 c_1 and c_2 fail, att 3 c_2 fail, att 4 all pass. The inherited test passes in all 4.
5. No strays.
6. Critic s61: pass on e40742e3, each criterion's line `if tip_percentage < 0 or tip_percentage > 100: raise ValueError(...)`. Architect s62: f_1 and f_2, k0, satisfied.
7. None.
8. Merged: tipsI ff1f65f, files `main.py`, `tip_calculator.py` and three test files. `latest_runs` 4 of 4 pass.
9. Sessions: Developer 3, Tester 3 (s56, s58, s60), Architect 2, Critic 1. 0 with `committed = 0`.

### dry2 b_2 (tipsI), abandoned

1. Ticket tk_2: "the program returns the tip amount as before when the tip percentage is valid". c_5 and c_10, both on valid percentages.
2. No batch test. Four inherited rows are the merged b_1 tests and the original test.
3. Developer, 5 sessions: s63, s64, s65 batch_start, writes to test files refused, code writes "unchanged", commit "nothing changed". s66 exhausted. s69 message. 5 wrote nothing.
4. No journal row. No Tester `tests_missing` session.
5. to 7. None.
8. Not merged. `head_commit` is NULL. s74 Liaison quarantined "1 abandoned: batch_start for b_2 (developer), 3 attempts". Ruling r_m38: "Line 1 is not a change. The program already returns the tip as before. Drop it." Gate conditions not met: no commit, no test.
9. Sessions: Developer 5, Architect 2 (s52, s70). 0 with `committed = 0`.

### dry3 bg_1 (icalendarI), merged

1. Ticket tk_1: "the icalendar.caselessdict.canonsort_keys() method raises ValueError when canonical_order names the same key twice". c1 "The method raises ValueError if canonical_order contains duplicate keys." c2 "If no duplicates are found in canonical_order, the method returns the sorted keys as before." c3 "The method sorts the keys as before when no duplicates are found in canonical_order."
2. Tests (`tests.body`, git 08aab3c8). `tst_c1_raises_on_dup_keys` (v1): ValueError on a duplicate. It follows. `tst_c2_no_dup_keys` (v3) and `tst_c3_sorts_keys_without_duplicates` (v2): assert exact lists. The words say "as before", and the expected lists come from the current behaviour, which the words do not give (cannot be told). 1 inherited test, `.github/workflows/test_generate_matrix.py`.
3. Developer, 4 sessions: s180 batch_start, write refused (quote), commit returns `claimed` 99619246. s184 tests_failing, writes refused. s185 no write. s186 commits c5e780a5. 3 wrote nothing.
4. Att 2 on 99619246: c2, c3 fail. Att 3 on 99619246: c1 fail, c2 and c3 pass after re-encode. Att 4 on c5e780a5: all pass.
5. No strays.
6. Critic s187 and s188: verdict refused (a quote, "not one unit"). s189: pass on c5e780a5, lines c1 `raise ValueError(...)`, c2 and c3 "kept:". Architect s190: f1, k0, satisfied.
7. None.
8. Merged: icalendarI 4f12af1e, files `caselessdict.py` and three test files. `latest_runs` 4 of 4 pass. The main branch was later reset to 99619246 (observed: `git reflog main`).
9. Sessions: Developer 4, Tester 2, Critic 3, Architect 2. 0 with `committed = 0`.

### dry4 bg_1 (icalendarI), running at the run's end

1. Ticket tk_1: "when icalendar writes a long line, fold it at a space where it can, so that a word is not split". Six criteria c1 to c5 and c7, each with surface `src/icalendar/parser/parameter.py::q_split`. `batch_touch` names `string.py` and nine test files, and not `parameter.py`.
2. Tests on `q_split`: `tst_fold_c1` (asserts "\r\n" in the result and a space after it), `tst_fold_c2` (asserts `q_split(q_split(x)) == x`), `tst_fold_c3` (asserts the result equals the token), `tst_fold_c3_fixed` at `.github/workflows/` (asserts `len(result) == 1` and `result[0]` equals the token), `tst_fold_c5` (as c2). The two c3 tests assert a string and a list, and the words give no return type (reasoned). c4 and c7 have no test. 1 inherited test.
3. Developer, 22 sessions. s178 to s180 and s199 to s201 batch_start wrote nothing. s206 commits 8e706696. s208, s209, s212 touch_mistaken, writes refused or discarded ("The runner discarded the writes that no commit held"), and s208's commit refused "you are undoing yourself". s221 commits 7fe86f47. s229 commits edd92b42. s231 commits 3f27b9e6 and 751f67c2. s232 commits 87071d8b and 4b1c3a3b. s234 commits 1c452198. 15 wrote nothing.
4. Att 2 to 8, on 8e706696 to 4b1c3a3b: c1, c2, c3, c5 fail, `tst_fold_c3_fixed` passes from att 5. The inherited test passes. No run on 1c452198.
5. 19 stray rows: 8 `string.py::_foldline` "mistake", one per commit from 8e706696 to 1c452198, judged once by s207. 11 rows on `parameter.py` and `parameter.py::q_split` stay `open`.
6. No Critic session and no finding.
7. None.
8. Not merged. At the end: commits exist, c4 and c7 untested, no verdict, open strays, a mistake row on the head, and no run on the head. s213 quarantined touch_mistaken. The last sessions are s232 to s234 tests_failing.
9. Sessions: Developer 22, Tester 5, Architect 3. 0 with `committed = 0`.

### dry5 b_1 (icalendarI), deferred

1. Ticket tk_1: "...fold it at a space where it can, so that a word is not split, and keep everything else". c_1 "...folded at a space character within a word boundary to prevent splitting words." c_2 "...preserve all original characters and formatting...". c_3 "Folding must only occur where a space exists within the line; if no suitable space is found before the limit, the behavior follows existing constraints without splitting words." Surfaces name `q_split`. The touch names `string.py`.
2. Tests at `.github/workflows/`, all v3. `tst_fold_c1` captures stdout of `q_split` and checks line ends. The words say nothing of printing (reasoned). `tst_fold_c2` checks characters and a newline in the result. `tst_fold_c3` checks a no-space word stays whole and that "very" and "long" are not in one word. 1 inherited test.
3. Developer, 11 sessions: s207 batch_start, commit returns `claimed` 99619246. s212 challenges. s216 commits 670629b3, message "Fix tst_fold_c1 to call _foldline instead of q_split", diff 109 lines of `string.py`, its test write refused. s221, s225, s226 touch_mistaken, every write refused. s227 exhausted. 10 wrote nothing.
4. Att 2 and 3 on 99619246: c_1 fail, c_2 and c_3 pass. Att 4 on 670629b3: c_1 fail. Att 5 on 670629b3: all pass after re-encode.
5. 5 strays on 670629b3, judged by s220: four escape symbols "foreseen", `_foldline` "mistake" (removal of `assert "\n" not in line` and the escape check).
6. Critic s243 refused, s244 pass on 670629b3, lines `"test: tst_fold_c1"`, `"test: tst_fold_c2"`, `"test: tst_fold_c3"`. Findings fnd_1 to fnd_12, all "violated" on 670629b3, written by Architect message sessions s217 and s222. Critic s245 to s257 dismissed all 12 (`finding_rulings`).
7. No `finding_violated` session follows. No commit after 670629b3, so no later commit changed `string.py`.
8. Not merged. At the end: verdict pass on the head, criteria tested, tests green, a mistake row on the head, 12 violated findings with dismissals. s242 quarantined touch_mistaken, s258 parked.
9. Sessions: Developer 11, Critic 15, Tester 6, Architect 3 (plus s217 and s222). 0 with `committed = 0`.

### dry6c b_1 (icalendarI), deferred

1. Ticket tk_1: "fold long lines in iCalendar output at spaces to avoid splitting words". c_1 "The serialized iCalendar output must fold lines at whitespace boundaries without splitting any word." c_2 retired by r_m54. c_3 "The folding behavior must not alter existing escape sequences or break them across lines."
2. One test, `c_1_fold` (v1): splits the output on "\n", asserts no word contains "\n" and every line is at most 75 characters. The first assertion cannot fail, and 75 is not in the words (reasoned). c_3 has no test. 162 inherited tests.
3. Developer, 7 sessions: s152, s155, s156, s173 batch_start, every write refused by the runner. s154, s159 message. s157 exhausted. 7 wrote nothing. `head_commit` and `claimed_head` are both 99619246.
4. Att 1 and 2 on 99619246: `c_1_fold` passes. 157 of 162 inherited pass, 5 red.
5. to 7. None. Tester sessions s174 to s194 had 0 `code.source` calls and many encode refusals.
6. No verdict and no finding.
8. Not merged. At the end: no commit, c_3 untested. s187 quarantined tests_missing, s195 parked "The team gave up on: tests_missing for b_1".
9. Sessions: Tester 10, Developer 7, Architect 2. 0 with `committed = 0`.

### dry7 b1 (icalendarI), deferred

1. Ticket tk_1: "fold long lines in the icalendar parser at a space where a word is not split". Live c1 "The parser must fold long lines at a space character that does not split a word." c2 (v2) "...must invoke _foldline when a line exceeds the limit...". c3 (v2) "The output of _foldline must preserve all original characters except for the inserted newline...". c_1, c_2, c_3 retired by r_m42.
2. Tests: `tst_fold_c1` (v2, c1) calls `q_split(..., sep=" ", maxsplit=1)` and compares character sets. `tst_fold_c2` (v2) calls `_foldline` and asserts `word not in line or line.count(word) == 1`. `tst_fold_c3` (v2) compares character sets. Neither check tells a split word from a whole one (reasoned). `tst_fold_c_1` and `tst_fold_c_3` stay live for retired criteria and call `q_split(..., max_length=75)`. 162 inherited tests.
3. Developer, 35 sessions. Commits: s164 63a1c381, s191 2d20cc90, s195 aba4c0a2, s196 40778404, s202 c85fe55f, s204 3d20a228 and 17ed55ce, s207 49e0fc1a, s209 21bbe661. s160 and s172 test-file writes refused. s217 to s219 failed on `LLMUnavailable`. 27 wrote nothing.
4. Base att 2: 5 batch tests fail, 159 of 162 inherited pass. Att 3 on 63a1c381: 154 inherited pass. Att 4: c1 passes at the same commit. Att 9 and 10 on 17ed55ce and 49e0fc1a: batch tests error, 1 of 162 inherited pass. Att 11 on 21bbe661: c1 pass, 105 of 162. Att 12 on 21bbe661: c2 passes at the same commit, c3 fails.
5. 11 strays: 10 "mistake" on `_foldline` or `string.py`, from 63a1c381 to 21bbe661, one "open" on 3d20a228. Architect s190, s192, s205, s208.
6. No Critic session and no finding.
7. None.
8. Not merged. At the end: no verdict, c3 red, 57 inherited red, a mistake row on the head, an open stray. s222 quarantined touch_mistaken, s223 parked "attempt 12 of 10".
9. Sessions: Developer 35, Architect 6, Tester 4. 3 of 35 Developer sessions have `committed = 0`.

### dry8 bg_1 (icalendarI), deferred

1. Ticket tk_1: "fold long lines in the _foldline function at src/icalendar/parser/string.py". c1 "The _foldline function must not split a word at any point; it may only insert a CRLF followed by a space between existing characters." c2 retired by r_m46. c3 "The function must return a string where every line is at most 75 octets long, excluding the line break."
2. `tst_c1` (v2): asserts each line before "\n" ends with "\r". It follows in part. `tst_c3` (v1): splits on "\n" and asserts each line, with its "\r", is at most 75 octets. That counts the CR, which the criterion excludes (reasoned). 162 inherited tests.
3. Developer, 14 sessions: s157 batch_start, commit returns `claimed` 99619246. s162 commits 67e0b2d0. s164 commits a585c4ea. s198 touch_mistaken commits 8a8eb07f, 4d42947d and fddff3af, its test write refused. 11 wrote nothing. Architect s160 `tick:claim` ran one program (`claim_runs` cr_a6346f6a91cb).
4. Base: both fail, 159 of 162 inherited pass. Att 5 on a585c4ea: c1 passes at the same commit. Att 6 on fddff3af: both pass, 157 of 162 inherited pass.
5. Strays: 67e0b2d0 `_foldline` "open", a585c4ea `_foldline` "mistake" (removal of `assert "\n" not in line`). No row on the three later commits, and fddff3af holds the assert at line 130 (git show).
6. No Critic session and no finding.
7. None.
8. Not merged. At the end: tests green at the head, no verdict on the head, an open stray on 67e0b2d0. s196 quarantined tests_failing before s198, s199 parked.
9. Sessions: Developer 14, Architect 4, Tester 3. 0 with `committed = 0`.

## Part C: the grid

Batch codes: D1 dry1 bg_1, D2a dry2 b_1, D2b dry2 b_2, D3 dry3 bg_1, D4
dry4 bg_1, D5 dry5 b_1, D6c dry6c b_1, D7 dry7 b1, D8 dry8 bg_1.

| # | statement | holds | does not hold | cannot be told |
|---|---|---|---|---|
| 1 | one test per criterion | 6: D1 D2a D3 D5 D7 D8 | 3: D2b D4 D6c | 0 |
| 2 | test from the criterion's words | 0 | 7: D1 D2a D4 D5 D6c D7 D8 | 2: D2b D3 |
| 3 | tests before the implementation | 5: D3 D5 D6c D7 D8 | 3: D1 D2a D4 | 1: D2b |
| 4 | Tester never sees the code | 1: D6c | 7: D1 D2a D3 D4 D5 D7 D8 | 1: D2b |
| 5 | no trivially passing test | 4: D3 D4 D7 D8 | 2: D5 D6c | 3: D1 D2a D2b |
| 6 | nothing built that was not asked | 3: D1 D2a D3 | 4: D4 D5 D7 D8 | 2: D2b D6c |
| 7 | harness runs the repository's tests | 5: D1 D2a D6c D7 D8 | 3: D3 D4 D5 | 1: D2b |
| 8 | red wakes Developer, within loop_cap | 6: D1 D2a D3 D4 D5 D8 | 1: D7 | 2: D2b D6c |
| 9 | commit or discard at session end | 9: all | 0 | 0 |
| 10 | head_commit is the real head | 8: all but D2b | 0 | 1: D2b |
| 11 | unpredicted path writes a stray | 7: D1 D2a D3 D4 D5 D7 D8 | 0 | 2: D2b D6c |
| 12 | prediction never rejects a diff | 4: D4 D5 D7 D8 | 0 | 5: D1 D2a D2b D3 D6c |
| 13 | each stray judged | 1: D5 | 3: D4 D7 D8 | 5: D1 D2a D2b D3 D6c |
| 14 | mistake wakes Developer to take it out | 1: D8 | 3: D4 D5 D7 | 5: D1 D2a D2b D3 D6c |
| 15 | one Critic verdict on one commit | 4: D1 D2a D3 D5 | 0 | 5: D2b D4 D6c D7 D8 |
| 16 | violated finding wakes Developer | 3: D1 D2a D3 | 1: D5 | 5: D2b D4 D6c D7 D8 |
| 17 | harness, then Critic, then Architect | 3: D1 D2a D3 | 1: D5 | 5: D2b D4 D6c D7 D8 |
| 18 | mergeable conditions decide the merge | 9: all | 0 | 0 |
| 19 | gate holds on a stray or a mistake | 4: D4 D5 D7 D8 | 0 | 5: D1 D2a D2b D3 D6c |
| 20 | exhaustion climbs, never silence | 7: D1 D2b D4 D5 D6c D7 D8 | 0 | 2: D2a D3 |

Evidence for each "does not hold" cell:

- 1 D2b: `tests` has 0 rows with `batch_id='b_2'` and a criterion, and no `tick:tests_missing` session names b_2.
- 1 D4: `criteria` c4 and c7 have no `tests` row.
- 1 D6c: `criteria` c_3 (live) has no `tests` row.
- 2 D1: `tests` inh_03a1b2c3 v3 asserts `raw_terminal().__enter__() == -1`.
- 2 D2a: `tests` tst_tip_invalid_low v3 matches the literal "Tip percentage must be between 0 and 100.".
- 2 D4: `tests` tst_fold_c3 and tst_fold_c3_fixed assert a string and a list for one criterion.
- 2 D5: `tests` tst_fold_c1 v3 reads `sys.stdout` of `q_split`.
- 2 D6c: `tests` c_1_fold asserts no "\n" in words of a text split on "\n", and a 75-character limit.
- 2 D7: `tests` tst_fold_c1 and tst_fold_c3 compare character sets, tst_fold_c2 asserts `word not in line or line.count(word) == 1`.
- 2 D8: `tests` tst_c3 counts the "\r" of each line against 75 octets.
- 3 D1: s145 commit 4fcd6d73 (seq 145) before s146 tests_missing.
- 3 D2a: s55 commit e40742e3 before s56 tests_missing.
- 3 D4: s206 commit 8e706696 before s214 tests_missing.
- 4 D1, D2a, D3, D4, D5, D7, D8: `tool_calls` `code.source` in Tester sessions: 5, 4, 3, 11, 15, 12 and 4 calls, on `termui.py`, `main.py`, `caselessdict.py`, `parameter.py` and `string.py` (dry1 s186 and s194, dry2 s58 and s60, dry4 s217 to s226, dry8 s166 and s171).
- 5 D5: `test_run_journal` att 2 on 99619246: tst_fold_c2 and tst_fold_c3 pass before any commit.
- 5 D6c: `test_run_journal` att 2 on 99619246: c_1_fold passes, and no commit follows.
- 6 D4, D5, D7, D8: `touch_strays` "mistake" rows: 8, 1, 10 and 1.
- 7 D3, D4, D5: `tests` has one row with `criterion_id IS NULL` (`.github/workflows/test_generate_matrix.py`). `git ls-tree -r 99619246` lists 162 `test_*.py` files.
- 8 D7: `test_run_journal` attempt 11 and 12 on 21bbe661, s223 detail "attempt 12 of 10".
- 13 D4: `touch_strays` 11 rows "open" (parameter.py and q_split, 7fe86f47 to 1c452198).
- 13 D7: `touch_strays` 3d20a228 `_foldline` "open".
- 13 D8: `touch_strays` 67e0b2d0 `_foldline` "open".
- 14 D4: mistake rows on every commit up to the head 1c452198.
- 14 D5: mistake row on the head 670629b3, and no later commit.
- 14 D7: mistake row on the head 21bbe661 (removal of `escaped_prefix = current_chars.pop()`).
- 16 D5: `findings` fnd_1 to fnd_12 "violated", and no session with `wake_kind='tick:finding_violated'` in dry5.
- 17 D5: findings written by s217 and s222 (Architect, `message`, escalate), before the Critic's pass by s244.

| run and batch | request | criteria (live) | tests | Developer sessions | wrote nothing | commits | fail verdicts | violated findings | strays | end state | condition at the end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dry1 bg_1 | pause() returns True or False | 3 (3) | 3 | 18 | 17 | 1 | 0 | 0 | 0 | merged | merged on 4fcd6d73 |
| dry2 b_1 | ValueError on an invalid tip percentage | 3 (3) | 3 | 3 | 2 | 1 | 0 | 0 | 0 | merged | merged on e40742e3 |
| dry2 b_2 | tip as before when valid | 2 (2) | 0 | 5 | 5 | 0 | 0 | 0 | 0 | abandoned | batch_start quarantined, item contested |
| dry3 bg_1 | canonsort_keys raises on a duplicate key | 3 (3) | 3 | 4 | 3 | 1 | 0 | 0 | 0 | merged | merged on c5e780a5 |
| dry4 bg_1 | fold long lines at a space | 6 (6) | 5 | 22 | 15 | 8 | 0 | 0 | 19 | running | no run and no verdict on the head |
| dry5 b_1 | fold at a space, keep everything else | 3 (3) | 3 | 11 | 10 | 1 | 0 | 12 | 5 | deferred | mistake in the head, parked |
| dry6c b_1 | fold long lines at spaces | 3 (2) | 1 | 7 | 7 | 0 | 0 | 0 | 0 | deferred | c_3 without a test, parked |
| dry7 b1 | fold long lines in the parser | 6 (3) | 5 | 35 | 27 | 9 | 0 | 0 | 11 | deferred | mistake in the head, parked |
| dry8 bg_1 | fold long lines in _foldline | 3 (2) | 2 | 14 | 11 | 5 | 0 | 0 | 2 | deferred | no verdict on the head, open stray |

## Part D: what the grid does not cover

1. A batch test changed from fail to pass at a commit the code did not change, after a re-encode, in 6 batches: dry1 tst_waited (4fcd6d73, v9), dry2 b_1 tst_tip_invalid_low and tst_tip_valid (e40742e3), dry3 c2 and c3 (99619246), dry5 tst_fold_c1 (670629b3), dry7 tst_fold_c1 and tst_fold_c2, dry8 tst_c1 (a585c4ea) (observed: `test_run_journal`, `tests.version`). In dry1, dry2 b_1 and dry5 that change was the last step to green before the verdict.
2. The Developer challenged the Tester in 7 of 9 batches, all but dry2 b_2 and dry6c, and 175 `msg.challenge_tester` calls are in `tool_calls` of the build desks across the 11 databases (observed: `fns.py`). In dry1 the door refused 4 Developer writes because a challenge had gone out in the same session (observed: s193, s201, s203, s266).
3. Developers wrote to test files in 5 batches, and the door refused each write: dry2 b_1 s55, dry2 b_2 s63 to s65, dry5 s216, dry7 s160 and s172, dry8 s198 (observed: `ERROR code.write ... is a test file`). Commit messages describe test edits that did not land, for example 670629b3 "Fix tst_fold_c1 to call _foldline instead of q_split" changes only `string.py` (observed: git show).
4. In dry4, dry5 and dry7 the criteria name `parameter.py::q_split`, while `batch_touch` names `string.py` (observed: `criteria.surface_refs`, `batch_touch`). In dry4 the commits then went to `parameter.py` and wrote 11 open strays.
5. Stray rows record removed lines inside a predicted path and symbol: dry7 and dry8 list `string.py::_foldline` in `batch_touch` and still hold 11 and 2 stray rows on it (observed: `touch_strays.note` "removal: ...").
6. The repository's own tests got worse at the head in dry7, 159 of 162 at the base to 105 of 162, and in dry8, 159 to 157. At the same base commit dry6c recorded 157 of 162 and dry7 and dry8 recorded 159 of 162 (observed: `test_run_journal`).
7. Batch tests sit in `.github/workflows/` in dry4 (tst_fold_c3_fixed) and dry5 (all three), the folder of the only inherited test (observed: `tests.path`).
8. Three Developer sessions answered "the code already meets the criteria" with a `claimed` commit result: dry3 s180, dry5 s207, dry8 s157. Dry6c holds `claimed_head = 99619246` (observed: `turns`, `batches`). Dry8 then woke an Architect `tick:claim` session that ran a program (observed: `claim_runs`).
9. The Critic's verdict door refused passes in dry3 (s187, s188) and dry5 (s243) with "not one unit that a pass can name", and dry5's pass names tests in place of diff lines (observed: `turns`, `verdicts.lines`).
10. Two dry7 tests for retired criteria c_1 and c_3 keep `retired_by` NULL, and their last runs are red on 63a1c381 (observed: `tests`, `latest_runs`).

## Part E: limits

- The `tests.body` is the newest version. The reader did not read earlier versions in `artefact_versions`, so the text of a test at the time of a red run is not shown.
- Tool results come from a pattern search over `turns.user` and the runner's account. A result in another form can be missing. The counts of "wrote nothing" rest on that search.
- Sessions have no batch column. The reader took a session as the batch's when `wake_refs` names the batch, or when it is a Developer or Tester `message` session in a run with one batch. In dry2 the reader gave s58 and s60 to b_1 and s69 to b_2 by their refs and order (reasoned).
- `loop_cap` is 10 in `rota/core/config.py` today. The run databases hold no `loop_cap` row, so the value at run time is not recorded. Dry1's park note "attempt 10 of 10" and dry7's "attempt 12 of 10" give 10.
- Dry1's database holds four measures. The one batch row and sessions s143 to s270 do not show where a measure starts.
- The worktree folder `icalendarI/.rota/worktrees` holds only `bg_1`, now dry8's branch. The dry4, dry5 and dry6c commits are not on any branch and could be lost to `git gc`. The main branches of icalendarI and clickI were reset after merges, and the dry3 merge 4f12af1e is on the reflog only.
- The `.rota/dry*.db` files were opened by others on 2026-11-10 (the inventory page). The other databases have `-wal` files. A later write to any of them can change what the reader saw.
- The reader did not run any test. "Green at the merge" means the `latest_runs` rows on the merged commit. In dry3 those rows cover 1 of the repository's 162 test files.
- Whether a test "follows from the criterion's words" is the reader's reasoning, marked so in each block.
