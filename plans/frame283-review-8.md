# Frame 283, review 8 of 90c8d5ef: a rewrite is not a removal

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r283` at 90c8d5ef.
Verdict: does not stand. The span branch now admits a removal that no note names (finding 1).

## (a) The points

1. Holds. The s221 shape opens no note, the write result has no `dropped` key, and `code.commit` lands. The test `test_a_span_write_that_rewrites_a_bare_return_opens_no_note` shows it, green on this run.
2. Partly holds. The door notes the `if` drop with the rewrite, and it notes `return x` to `raise`. The door misses a move between owners, and it misses a same-kind swap (findings 1 and 2).
3. Holds. 491 tests pass: test_frame283_rewrite_not_removal 4, test_frame283_whole_file_drop 17, test_frame283_removal_on_ruling 59, test_frame140_commit_beside_note 51 (s388), test_desk_guards 360 (s386). s340 is at test_frame283_whole_file_drop.py:211. The whole-file branch keeps its old logic, now moved into `_kind_shortfall`.
4. Holds. In `batch_start` mode the text is "A note does not allow a removal or a rewrite. To undo the change, put the line back with code.write, then commit in your next reply." The mode holds `code.write` and `code.commit` and does not hold `msg.escalate_architect`. So the text names only calls that the mode's doors admit, as frame 135 requires. In `tests_failing` mode the text keeps the tool.
5. Partly holds. Before pass 8, the test showed that a same-kind span rewrite (`return x` to `return x + 1`) opens a note and the refusal names both routes. Now it puts `print(x + 1)` where the return was. The test still pins the two-route text. It no longer pins a rewrite, so the name "for_a_rewrite" is now wrong (finding 4).

## (b) Findings

1. rota/roles/api.py:21582-21595 and 21480-21484. High. CONFIRMED. `_rewritten_heads` reads a held count of each kind as "every change is a rewrite", and then the door clears every lost line. A span write that drops `validate(x)` and adds a second copy of `self.log(x)` under the same owner now gets no note (probe E5). At 90c8d5ef^ the same write named `validate(x)`. The swap of `validate(x)` for `print(x)` also gets no note now (E4). E5 is a removal that adds no content, so it does not fit the frame's design. The whole-file branch has the same gap: `_whole_lost` returns None on E5. Fix: count a changed statement as a rewrite only when its owner and line key also fall and the text gains a new key under that owner, not a copy of a key the old owner already holds.
2. rota/roles/api.py:21474-21482. Medium. CONFIRMED. The span branch misses a move of `validate(x)` from `clear` to `other` (probe E2). The cause is that `_lost_statements` finds the line text elsewhere in the file. Pass 8 computes the `Expr` shortfall under `clear` and then discards it, because `_rewritten_heads` returns an empty set. `_whole_lost` on the same text names `validate(x)`. The gap was there before pass 8, and pass 8 does not make it worse. Fix: when `_kind_shortfall` reports a fall, add the statements that `_whole_lost` selects to `lost`.
3. tests/rota/test_frame283_rewrite_not_removal.py:79-87. Low. PLAUSIBLE. No test covers the `tests_failing` mode after an escalation went this session. That is the second half of the frame 135 condition, `_escalation_admitted`. The refs are the note's file paths, and a real escalation can carry other refs. Fix: add a test that sends one escalation and then expects the write route alone.
4. tests/rota/test_frame283_whole_file_drop.py:252-262. Low. CONFIRMED by reading. The test name says "rewrite", but the write is now a removal and an add. A same-kind span rewrite now has no route test, because no note opens. Fix: rename the test to say a kind change, and keep the route assertion.

Outside the points: none beyond finding 2, which comes before pass 8.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e7141541-fc20-4c5c-a91b-4a10a610ec42/scratchpad/r8/probe_edges.py` calls `_drop_note` on a nine-line, two-function file for edges E0 to E6. At 90c8d5ef: E0 None, E1 names `if x:` and `return`, E2 None, E3 names `return x`, E4 None, E5 None, E6 names `return`. At 90c8d5ef^, from `git archive` into `scratchpad/r8/parent`: E0, E4 and E5 name the line, and E2 is None.
- An inline `python -c` run of `_whole_lost` on E2 names `validate(x)`, and on E5 it returns None. The same run of `prompts.mode_tools` shows that `batch_start` holds code.write and code.commit and does not hold msg.escalate_architect.
- pytest on the three frame 283 files, test_desk_guards.py and test_frame140_commit_beside_note.py: 491 passed in 76 s.

## (d) Usage

About 45k tokens in and 6k out. These numbers are an estimate.
