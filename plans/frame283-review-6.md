# Frame 283, review 6 of 268e565f

Reviewer: read-only agent on C:/Users/roman/rota_r283 at 268e565f, model Opus. Date: 2026-10-17.

Verdict: stands. Pass 6 fixes review 5's F2, F3 and F4 on the shapes that review 5 named. Three low findings remain. No finding is high.

## (a) Verdicts on the points

1. F2 fixed. S192 now returns no `dropped` key and opens no note (observed: r5_probe_tail.py, S192). The base-rule result still says `dropped`. The sentence is true and gives no order, so it does not ask for a restore. It is the same sentence an open note carries, so a seat cannot tell the two apart (finding 1).
2. F3 fixed for the "It drops" sentence. T4 shows `` `` return f'`{x}` "q"' `` `` and closes (observed: r5_probe_itdrops.py). A line with two backticks in a row breaks the double fence (finding 2). The two main sentences still use a single fence (finding 3).
3. F4 fixed. LONG closes on the full line (observed: r5_probe_tail.py, LONG). The cut form with a trailing `...` or `…` also closes, because `_says` needs no word character after the cut text (observed: r6 probe, `_says`).
4. Holds. `test_s388s_commit_in_the_next_reply_with_no_write_is_refused`, `test_s340s_unchanged_write_sends_the_note_again_and_holds_the_commit` and `test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused` are in the file. The three files pass: `70 passed in 28.00s` (observed: this review).
5. The next night meets finding 1 first: a seat sees one `dropped` sentence whether the commit door then refuses or not.

## (b) Findings

1. `rota/roles/api.py:15502-15512` `_code_write`, low, CONFIRMED (observed: r6 probe test_base). When the base rule empties the entry, the result says "This write removes 1 statement that your text does not hold: `def added_here() -> int:` at line 573." An open note carries the same sentence. The seat cannot tell from the result whether the next commit lands. A seat that learned "dropped means write a ledger" spends one ledger call it does not need. It does not restore, because the sentence gives no order. Fix: when the base rule empties the entry, add one clause, for example "The batch added it, so the commit is not held."
2. `rota/roles/api.py:16207-16210` `_quote`, low, CONFIRMED (observed: r6 probe test_two_ticks). The line `return 'a``b'` shows as `` `` return 'a``b' `` ``. The inner run of two backticks closes the double fence, so a reader of the fence sees `return 'a` as the line. The closure still works on the exact line, because `_shown_lines` matches the raw text. Fix: use a fence one backtick longer than the longest backtick run in the line.
3. `rota/roles/api.py:17455-17456` tail sentence and `_lost_sentence` under 17645, low, CONFIRMED (observed: r5_probe_tail.py T1 and TICK). Both sentences still wrap a stored line in single backticks. TICK shows `log("a `b` c", x)`, and T1 shows "from `log("a `b` c", x)`". This is review 5's F3 in the two sentences the seat reads first. Fix: use `_quote` in both sentences, and keep `_shown_lines` reading both fence forms.

## (c) Probes

- Review 5's probes re-run unchanged from C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/: r5_probe_subset.py (R5a and R5c still hidden, the accepted risk), r5_probe_itdrops.py, r5_probe_tail.py, r5_probe_whole.py. The pytest ones ran with `-s --rootdir=.` from the worktree: 15 passed.
- New: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/r6/test_r6_probe.py. test_base prints the result of the pass 3 base-rule write. test_two_ticks writes a tail drop of a line with two backticks in a row and prints the note and `_quote`. test_cut_mark calls `_says` on the cut form with `...`, `…`, nothing, `_name` and the rest of the line: the first three close, the last two do not, and the full line closes through the new F4 branch. 3 passed.
- The three test files: `tests/rota/test_frame140_commit_beside_note.py tests/rota/test_identity.py tests/rota/test_revert_door.py`, 70 passed. The gate did not run.

## (d) Usage

About 19k input tokens and 6k output tokens, about 25k in all, an estimate. The harness line is the record. No sub-agent ran.
