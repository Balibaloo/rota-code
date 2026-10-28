# Review of P12 pass 1, commit 61608940 on w12root

Verdict: READY. The commit names the red test in all five sentences, and it adds no numbered line. No recorded case goes stale. The review found 0 high and 6 low findings. The low findings are about sentence length and some edge words. None of them blocks the land.

The review was read-only, in `C:/Users/roman/rota_r12` at 61608940. The parent is 2b1ef4c9.

## (a) The points

1. CONFIRMED. All five sentences name the red test, for a project red and for an own red with a criterion (probe 1). Items 1, 3, 4 and 5 were probed directly. Item 2, the parked line, is covered by `test_next_batch.py`, which passes.
2. CONFIRMED. The commit adds no numbered line. The page order is `[item, cr_1, t_own, bg_3]` in every variant, and the project red is never in it (probe 1). No hunk touches `numbered(`.
3. PARTLY. No rota name, id or key prints, and "for bg_3" is gone (probe 1). Some sentences run past 25 words: m127's shape has 32 words, and a sentence with two to four files has 49 to 77 words (finding 1). Each sentence carries one statement and no instruction.
4. CONFIRMED. No case goes stale, so the re-record list is empty. No recorded prompt in the register holds "after N attempt" (probe 4). The L1 `tick: exhausted` cases take the literal `detail:` of the case file, so they never call `stop_detail`. Two `l1_liaison2.yaml` park_ask cases get new `_gave_up_words` output (probe 2), but no prompt of theirs reads it.
5. CONFIRMED. Each changed assertion still tests what its name says. `test_the_wake_says_the_tests_still_fail_after_3_attempts` now asserts "p still fails", so its name is stale words, not a defect. `test_the_park_count_survives_a_commit_and_quarantines` no longer checks which batch the line names, but the test name asks only for the quarantine line. `test_a_long_error_line_is_cut` checks the wrong span (finding 5).
6. CONFIRMED. The touched and related files give 308 passed. The 6 known reds are red at the commit. Their errors are not in the changed code (probe 5). The diff holds 0 CR bytes. All 10 hunks are inside the claim.

## (b) Findings

1. `rota/roles/principal.py` 1866 to 1877, `_key_words`. Low. CONFIRMED. The sentences can run past the 25-word limit. Probe 1 measured 32 words for m127's shape with one file. It measured 49 words for 5 files and 77 words for 4 files with long errors. The code comment says the sentence "stays under 25 words per test", but that is true only for one key with one file. Fix: give each red file its own sentence, and cut the error to the words that fit.
2. `rota/roles/principal.py` 1974, `_capital`. Low. CONFIRMED. A red test file at the repository root has no "/", so `code_gaps` printed "Test_types.py still fails ..." (probe 1, variant root). That is the wrong path that the change was written to stop. Small repositories often keep test files at the root. Fix: skip the capital when the first word ends in `.py` or is one of the red paths.
3. `rota/roles/principal.py` 1910, `_ref_words` returns "" for a batch. Low. CONFIRMED. With two stuck batches, `render_state` printed "Stuck: the review gave no verdict after 3 attempts; the review gave no verdict after 3 attempts." (probe 3). The principal cannot tell which change each clause is about. The builder's report names this as deviation 2. Fix: name the item of the batch in words, or count the repeated clauses once.
4. `rota/roles/principal.py` 1868, the extra-files count. Low. CONFIRMED. One extra file prints as "and 1 more test files" (probe 1, variant four). Fix: write "1 more test file" when the count is 1.
5. `tests/rota/test_w12_stopped_names_red_test.py` 110 to 115. Low. PLAUSIBLE. The test counts the words of `_stalled_words` alone, which gives 22. The page adds "The team gave up:", so the sentence has 26 words. The test therefore passes on a sentence past 25 words. Fix: count the words of the sentence on the rendered page.
6. `rota/roles/principal.py` 1860 to 1864, an own red test. Low. CONFIRMED. A red test with a criterion now shows its error two times: on check line 3 ("Fails: AssertionError: assert ...") and again in "The team gave up" (probe 1, variant own). Fix: name only the project reds in the sentence, because the check line names the own reds already.

Outside the points: none beyond finding 6. `_key_words` looks up `batches` with its own SQL. The F22 pin allows a look-up in one table, and it passes.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p12rev/`.

1. `probe1.py`. It builds the bg_3 fixture of the new test file in five variants: a project red, an own red, a root-level path, four files with long errors, and five files. For each variant it renders the stopped page, `render_state`, `code_gaps` and `stop_detail`. It prints the page order and the word count of each sentence.
2. `probe2.py`. It seeds every case fixture under `tests/rota/cases/`. It compares the words of the parent's form with the commit's words for each quarantined key and for `stop_detail` of each batch. It found 2 cases that differ: `L1-LI-a-parked-batch-is-put-to-the-principal-once` and `L1-LI-a-parked-batch-with-only-project-reds-is-a-note`.
3. `probe3.py`. It renders two batches, each with a quarantined `critic|tick:review` key, and it prints the gave-up line.
4. An inline `python -c` probe opened `D:/repos/rota/tests/rota/cassettes.db` read-only (`mode=ro`). It searched `cassettes.user` and `cassettes.system` for the old words. "the tests still fail", "after 3 attempts", "could not finish a step", "was stopped for" and "after N attempt" for N from 1 to 10 all gave 0 rows. "The team gave up on: tests_failing" gave 15 rows. That string is the park_ask literal, item 6, which the commit does not change.
5. pytest with `-p no:cacheprovider` on the commit. First run: test_w12_stopped_names_red_test, test_frame330_stopped_bouncing, test_next_batch, test_f20_quarantined_keys, test_frame312_stuck_review, test_onboarding_phases, test_predicates and test_f22_table_of, with 308 passed. Second run: the 6 known red ids, with 6 failed. Their errors are a `ledger.log` missing `kind` and a "DID NOT RAISE ValueError". Neither is in the changed code.
6. `git diff 2b1ef4c9 61608940` piped to Python counted 0 CR bytes, and the hunk headers showed 10 hunks.

The reviewer did not run the full gate, because point 6 asks for the touched files only.

## (d) Usage

- Input tokens: about 95k, cumulative.
- Output tokens: about 12k.
- Total: about 107k.
