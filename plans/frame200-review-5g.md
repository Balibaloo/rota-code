# Frame 200, pass 5g: diff review of 88cbbe5a against f6748446

Read-only review, rota workflow, from the worktree `C:/Users/roman/rota_rv200p5g` at 88cbbe5a. Written 2026-10-13 06:41. Verdict: the pass holds. No high finding. Six low findings.

## (a) Verdicts on the points

1. PARTLY. The diff touches eight files, not seven. The eighth is `plans/stack.md` (finding 1). The diff and both blobs of every file hold no CR byte.
2. HOLDS. The two paragraphs are the same word for word. The test's id or file is in the first fact. The count stays at the parent's count: two sentences and the example. The example carries all four slot parts. "A project callable" is absent, and the report says why: neither brief holds a signature sentence at the parent. Finding 4 is a word issue.
3. HOLDS, with two lows. `REASON_SLOT`, the TOOL line, both briefs, tests 17, 18, 20 and the pins in `test_revert_door.py` and `test_row_route.py` agree. Test 18 refuses the new slot in three forms. The old slot text now passes the slot door (finding 2). This does not matter for a recorded cassette, because the cassette key covers the prompt and the prompt changed. It matters only for a live seat whose context still holds the old text.
4. HOLDS, with one low. All four verdicts are refused. The five facts of test 19 are admitted, "the test passes package_name to invoke" included. The new words also refuse some facts (finding 3).
5. HOLDS. `tester/challenge.md:8` adds one sentence of 23 words: "The next body goes on the test the row names, and on no other test, even when another test calls the same function."
6. HOLDS, with one low. Only the text of row `<d1>` changed. The row gains the test id but carries no error and no line (finding 6).
7. HOLDS. At the parent, with the new test files copied in, 12 tests fail. The three new or extended ones are among them: `test_20_the_reason_slot_names_the_test_beside_the_line`, `test_the_tester_edits_the_test_the_reason_row_names` and `test_19_a_reason_that_says_the_test_passes_is_refused`. At 88cbbe5a, 99 tests pass in the four touched or pinning files.

## (b) Findings

1. `plans/stack.md:277-284`. Low. CONFIRMED. The feat commit carries the stack's frame 226 claim and three status lines, which are outside the brief's seven files. The CLAUDE.md rule is "commit the stack alone after every change". Fix: commit stack edits in their own `docs(plans)` commit from the next pass on.
2. `rota/core/sandbox.py:1904-1907`. Low. CONFIRMED. The old slot `<the error, the line, and the call that takes the argument>` passes `_reason_problem`, in bare form and in brackets, and the door returns None. A seat that copies a hint from a run database of night 144 writes the slot as its reason. The cassettes do not show this, because `runner.py:340` says the cassette key covers the brief text. Fix: compare against a tuple of the old and the new slot texts, and keep the old literal in test 18.
3. `rota/core/sandbox.py:1871-1872`. Low. CONFIRMED. The words `in`, `with`, `for` and `fine` refuse a fact when fewer than four words come before "passes". The probe refused "the test passes in the args list to runner.invoke and invoke raises TypeError". It also refused "tst_v1 passes with package_name missing to version_option, RuntimeError". Fix: match two-word verdict tails, "for me", "with the current", "in CI", and keep `cleanly`, `fine`, `green` alone.
4. `rota/roles/prompts/developer/tests_failing.md:35-38` and `answer.md:27-30`. Low. PLAUSIBLE. The word "function" has two meanings in one sentence: the test's function and the raising function in the last frame. A 9b seat can put the test's function into the third fact. Fix: write "with the test's id or its file and test name".
5. `rota/core/sandbox.py:1906-1907, 1918-1920, 1931-1933`. Low. CONFIRMED by reading. The three refusals of the reason door still ask for "the error the test got and the line of the test", and do not ask for the test or the call. The refusal therefore teaches a shorter shape than the slot. Fix: add "with the test's id" to the three refusal texts and to their pins.
6. `tests/rota/cases/l1_tester.yaml:603-605`. Low. PLAUSIBLE. The row reads "In `tst_version_option_show_python`, `package_name` is an argument of `version_option(...)`, not of `runner.invoke(...)`." The row has the test and the call, but no error and no line, so the Tester case does not meet the full new shape. The case is STALE until a re-record, which the report names. Fix: accept as the brief's "gains the test's id", or write the full shape before the re-record.

Outside the points: none beyond findings 1 and 2.

## (c) Probes

1. In the review worktree, `git diff --stat` and a Python count of CR bytes in the added lines and in both blobs of every touched file. The result was 82 added lines and 0 CR.
2. In the review worktree, `python -c` on `sandbox._reason_problem` with an in-memory `criteria` table: the old slot in two forms returned None, and the new slot in two forms returned the slot refusal.
3. In the review worktree, `python -c` on `_REASON_VERDICT` with ten strings, and on `_reason_problem` with three fact strings that hold "passes in", "passes with" and "passes fine". All three facts were refused.
4. `pytest tests/rota/test_challenge_evidence.py tests/rota/test_prompts.py tests/rota/test_revert_door.py tests/rota/test_row_route.py -q` at 88cbbe5a: 99 passed.
5. A second worktree `C:/Users/roman/rota_rv200p5g_parent` at f6748446, with the two new test files copied in: 12 failed, 45 passed. The worktree was then removed with `git worktree remove --force`.

## (d) Usage

About 30k input tokens and 8k output tokens, about 38k in total, by this agent's estimate. Read the harness line for the true count.
