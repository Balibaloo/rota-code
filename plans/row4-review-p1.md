# Review of 9a068333: one quote reader for the view the seat was shown (sprint 26, row 4, pass 1)

**Verdict: not ready to merge. Fix three high findings first.** The pass removes the window and runs green. The four sites now read through `_shown_views`. But the pass does not give one reader. The Tester channel keeps its own reader. The other channels and the answer door refuse seat forms that the Tester channel admits. The red-line door refuses a form that the evidence door admits. The red-line refusal also offers the `E` line, and every door now refuses that quote.

Worktree `C:/Users/roman/rota_r333` at 9a068333, parent d495db74. Every probe ran in a scratch copy or as a read-only call. No tracked file of the worktree changed.

## (a) The verdict on each point

1. One reader: PARTLY. `_quotes_span` is gone. The answer door and the tail call `_quote_reads`. The red-line door calls `_quote_holds`. The Tester channel keeps `_cites`. Findings 1 and 2.
2. The ruling on all five channels: HOLDS on four channels and FAILS on the Tester channel. `("statements", "text")` is quotable. Finding 4.
3. The night red tests: CONFIRMED. 19 red on the d495db74 code, 68 green at 9a068333. The m88 test is green both ways.
4. The deviations: three are right. The `E` line change is right, but it leaves a dead hint (finding 3). The `_own_reds` note has a weak tail (finding 6).
5. Weakened assertions: NONE. One parametrized accept case flips to a refusal, as deviation 5 says. The pin at 111 holds the strict form.
6. The brief and refusal lines: each offers a call the mode holds, and the call passes the doors. The staled count is 7 cases, not 4 (finding 5).
7. The 6 suite reds: CONFIRMED. All 6 are red on the d495db74 code and on the 9a068333 code.

## Point 1: one reader

- `_quotes_span` is gone (`test_the_window_is_gone` is green, and grep finds no name).
- `_answer_evidence` (sandbox.py 1064 to 1069) and the `_challenge_evidence` tail (1806 to 1809) call `_quote_reads`, through `_rows_quote_refusal` for the tail.
- `_red_line_refusal` (1318, 1324) calls `_quote_holds`, a second predicate. It asks the opposite question: the whole line is inside the quote. The difference is right, because the rule is the whole line. Both predicates share `_shown_views`.
- `_shown_views` (955 to 973) gives the raw row, `json.dumps` with and without `ensure_ascii`, `_escaped_view`, and the `_call_values` of each. `_quote_reads` reads each view through `_span_of`, and through `_unescaped` on both sides.
- `_quote_reads` reads no seat form of the quote. `_seat_forms` and `_one_backslash` stay only in the Tester channel's `_cites` (1757 to 1767). `_cites` also reads a test row through `_code_only`, and `_quote_reads` does not. So the Tester channel keeps its own rule beside the new reader.
- `_answer_evidence` keeps its own rule beside the call: one quote must be a span of a criterion. That rule is right for an answer.

## Point 2: the ruling on all five channels

- Two refs and one quote: refused on Terminologist to Vision Keeper, Architect to Vision Keeper (`refs=["s1","c1"]`) and Critic to Developer. Each refusal names the unquoted row. CONFIRMED (probe_edges).
- A quote that spans two rows (`for seven years close the account`): refused. A single string `A ... B` that is passed as `quotes=` is one quote, and it is refused. CONFIRMED.
- `("statements", "text")` is in `_QUOTABLE`, and `statements.text` exists in schema.sql 33. CONFIRMED.
- The Tester channel does not hold the rule. A third quotable row in refs passes with no quote. A quote of the sibling criterion c2, which refs does not name, passes. CONFIRMED (finding 4).

## Point 3: the night red tests

The scratch copy `parent` holds the d495db74 tree with the 9a068333 `tests/`. The scratch copy `child` holds the 9a068333 tree. The run covered `test_frame333_quote_reader.py`, `test_challenge_evidence.py`, `test_frame328_encode_note.py`, `test_pushes.py` and `test_frame328_challenge_quote.py`.

- On the parent code: 19 failed, 49 passed. The failed set is the 11 tests of frame 333, the pin at 111, the 2 encode note tests and the 5 night148 and night149 tests. CONFIRMED.
- On the child: 68 passed. CONFIRMED.
- The m88 test of frame 328 is green both ways, as the report says.

## Point 4: the deviations

1. The `E` line is no quote: RIGHT under the ruling, because the run output is no row of refs. On the Tester channel the parent code refused the `E` line already (probe_doors A2, parent). On the other channels the change is new. Night 142's m83 path (`test_desk_guards.py` 5947) shows it. The clause stays in `_red_line_refusal` as dead code, and the refusal still offers the line. Finding 3.
2. The short traceback form: RIGHT. With the clause disabled in a scratch copy, `test_frame328_criterion_quote.py` s327, s336 and m189 go red. With it, the 19 tests of the two files are green. CONFIRMED. Night 167's tr110 shows the form.
3. `_own_assertions` became `_own_reds`: RIGHT for frame 328 item 4. The new note tail fits an assertion and not a raise. Finding 6.
4. The encode note's second form: RIGHT. `test_a_raise_inside_the_code_after_the_commit_gets_a_note` shows the harness tail without the test's frame. Nights 163 to 168 held 3 such reds of 17, as the test docstring says.

## Point 5: weakened assertions

- `test_desk_guards.py` 5945: the parametrized accept of `AssertionError: assert ...` is gone. A refusal of that quote replaces it. The flip is the behaviour of deviation 5, so it is no weakening.
- `test_desk_guards.py` 5982 and 6006: the inputs add `N142_CRIT`. The assertions are the same.
- `test_triage_fork.py` 461: the prose answer moves from an accept to a refusal. A span alone is the new accept.
- `test_predicates.py` 1488 and `test_frame329_staged_twin.py` 193: only the scripted quotes change. The assertions are the same.
- `test_pushes.py`: four assertions now use `_contested`. The helper uses the code's own compare to pick the form. Each night148 and night149 test failed on the parent code, so each one pins the replaced form at least once.
- The pin at `test_challenge_evidence.py` 111 holds the strict form. Prose alone is refused, a span with prose around it is refused, and a span in outer marks is admitted.
- No assertion is removed without a replacement on the new behaviour.

## Point 6: the brief and refusal lines

- `criteria.md` 36: "`msg.challenge_vision_keeper` with the ticket and `quotes=` copying the words you dispute, after its criteria land."
- `criterion_repair.md` 45: "send `msg.challenge_vision_keeper` with the criterion and `quotes=` copying the words you dispute."
- api.py 6006: "To replace the landed criterion, send msg.challenge_vision_keeper with its id and quotes= copying the words you dispute."
- api.py 6081: "msg.challenge_vision_keeper with the ticket and quotes= copying the words you dispute."
- api.py 6851: "send msg.challenge_vision_keeper with {skip} and quotes= copying the words you dispute"
- api.py 6972: "send msg.challenge_vision_keeper with this criterion and quotes= copying the words you dispute."

Frame 135's law holds for each line. Only `criteria.tools` and `criterion_repair.tools` hold `criteria.specify` or `criteria.respecify`, and both hold `msg.challenge_vision_keeper`. Sites 6851 and 6972 gate on `_wake_mode_tools`. In mode `criteria`, the call with one row and a span of it passes (probe_offer). Each line names one row, so the per-row rule passes.

The staled cases, by mode. The cassette key holds the system prompt (cassettes.py 212).

- `criteria`, 5 cases: `L1-TE-specify-criteria`, `L1-TE-a-new-behaviour-is-a-new-callable`, `L1-TE-a-docstring-ticket-gets-a-docstring-criterion`, `L3-scope-becomes-a-ticket-with-criteria` (the `then` step) and `L3-a-challenge-reaches-the-role-that-can-answer-it` (the `first` step).
- `criterion_repair`, 2 cases: `L1-TE-repair-the-criterion-the-tester-cannot-encode` (by `tick:`) and `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` (by `prompt:`, l1_terminologist.yaml 213).
- The four refusals and the contest block stale a case only when a recorded turn shows them. The worktree has no register, so this review does not count those.

## Point 7: the 6 suite reds

The six files are the same at both commits. On the parent copy and on the child copy, the same 6 fail and 184 pass:

- `test_pins.py::test_with_prompt_keeps_every_pin`
- `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`
- `test_fixtures.py::test_no_case_leaves_a_reference_unwrapped`
- `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`
- `test_onboarding.py::test_the_same_constraint_written_twice_is_one_gate`
- `test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`

None of the 6 comes from this pass. CONFIRMED.

## (b) Findings

1. **High.** sandbox.py 986 to 998, `_quote_holds`. The red-line door does not read the seat's form with a backslash before each mark. The Tester's evidence door admits that form through `_span_of`. The red-line door then refuses it. The refusal shows the line that the seat already copied. On the parent code the call passed. CONFIRMED: probe_doors D1 passes at d495db74 and is refused at 9a068333. D2, with a green run, passes. Night 167 walk 3 (s327, s336 to s338) measured this form. Fix: read the quote in `_quote_holds` through the same seat forms as `_span_of` and `_seat_forms`.
2. **High.** sandbox.py 976 to 983, `_quote_reads`, against 1757 to 1767, `_cites`. A quote with one opening mark passes on the Tester channel. The same quote is refused on Terminologist to Vision Keeper and at the Tester's answer door. A quote with an escaped mark at each end is refused on Terminologist to Vision Keeper. This divergence is the fact that frame 333 exists to remove. The 333 Ends-when asks for "the helper the Tester channel uses". CONFIRMED: probe_doors B1 passes, and B2, B3 and C1 are refused at 9a068333. All four pass at d495db74. Fix: put `_seat_forms`, `_one_backslash` and `_unescaped` in one reader, and let `_cites` and `_quote_reads` call it.
3. **High.** sandbox.py 1329 to 1332, the red-line refusal. The refusal names the run's `E` line as a line to copy. The evidence door refuses that quote on every channel now. That breaks frame 135's law. The pass makes the refusal fire on each quote of part of the line, so seats meet it more often. CONFIRMED: probe_doors A1 is refused and names `assert ['inv1'] == []`. A2 then sends that line and is refused. Fix: name only the failing line in the refusal, and delete the dead admissions of the `E` line and of the fault's error.
4. **Low.** sandbox.py 1724 to 1793, the Tester channel. The channel does not ask for a quote of each quotable row of refs. It also admits a quote of a sibling criterion that refs does not name. The ruling of 2026-08-26 names all five channels. CONFIRMED: in probe_edges, `refs=["c1","ts1","t1"]` passes with no quote of t1, and a quote of c2 passes. Walks 23 to 27 measured the sibling exception. Fix: hold the per-row rule on the Tester channel, or record the sibling exception against DECISIONS.md 1290.
5. **Low.** The implementer's report, section (b). The report names 4 staled cases. The case files show 7: 5 in `criteria` and 2 in `criterion_repair`. CONFIRMED by grep of `tick:` and `prompt:` in `tests/rota/cases/`. Fix: re-record the 7 cases before the night.
6. **Low.** api.py 17763 to 17767, the encode note. A raise in the project's code now gets the tail "If the criterion's words give the value that the run shows, the test is wrong." A raise shows no value. The tail can send the Tester to rewrite a right test around a fault of the Developer. PLAUSIBLE: no night has shown the new note yet. Fix: give the `raised` form a tail that names the Developer's code as one cause.
7. **Low, outside.** sandbox.py 976 to 983. `_quote_reads` does not read a test row through `_code_only`. A quote of a test comment passes on Critic to Developer, and the Tester channel refuses it. PLAUSIBLE from the code. This is the same divergence as finding 2. Fix: the one reader of finding 2 takes the `_code_only` view for a `tests` row.
8. **Low, outside.** runner.py 771 to 779, `_contest_block`. A retired criterion keeps its row, so the block shows "He contested this text" with no word of the retirement. PLAUSIBLE from the schema (`retired_by` in schema.sql). Fix: say that the criterion is retired when `retired_by` is set.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/r4p/`.

- `parent/` is `git archive d495db74` with `tests/` from 9a068333. `child/` is `git archive 9a068333`. `nod2/` is a copy of `child/` with the short-form clause disabled.
- `probe_edges.py` holds the point 2 edges at 9a068333. It covers two refs and one quote on three channels, a quote across two rows, the Tester channel with a third row and a sibling quote, and `_QUOTABLE`.
- `probe_doors.py` ran on `parent/` and `child/`. It covers the red-line refusal and its `E` line offer (A1 to A3), the escaped-mark form (D1, D2), the one-mark form on three doors (B1 to B3, C1) and the answer door (C2, C3).
- `probe_offer.py` sends the offered call in mode `criteria` with one ticket and with one criterion.
- pytest with `-p no:cacheprovider` ran on both copies: the five red-test files (point 3) and the six red files (point 7). It ran `test_frame328_criterion_quote.py` and `test_frame328_restage.py` on `child/` and `nod2/` (point 4).
- No full gate run. No point needed it, and the gate writes a baseline in the worktree. No old night database was read, because the brief forbids `.rota/*.db` of `D:/repos/rota`.

## (d) Usage

- Input tokens: about 100k, estimated from the session budget. The harness gives no exact count.
- Output tokens: about 20k, estimated.
- Total: about 120k. The brief capped the review at about 60k. The scratch copies and the both-ways runs used the extra.
