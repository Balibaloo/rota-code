# Frame 283, review 4 of the pass 4 commit cbdc68f8

Agent: Opus, read-only, 2026-10-23. Worktree `C:/Users/roman/rota_r283` at cbdc68f8, parent d2b4f79a.

Verdict: accept for the branch. Do not close the frame. The pass fixes review 3's findings 1 to 3, and the night exposure measures zero. The clause cut opens one new wrong-admit class (F1): the rule reads the request in its own clause, but `_asks_removal` finds the name in the whole sentence. So "Keep ctx.exit(), and remove the extra echo." now admits the removal of `ctx.exit()`.

Path note: the brief names `plans/frame283-review-4.md`. That path holds a tracked review 4 of commit 02ea9522, dated 2026-10-17. This reviewer edits no tracked file, so this review is in the scratchpad.

## (a) The claim, point by point

1. Met. All eleven shapes of review 3's probe Q2 and "must no longer call" are on the right side. "Do not remove" and "Never drop" still refuse (probe S, group P1).
2. Met. Ten sampled sentences, five each way, moved the right way by their words. No sentence of the 24 would have landed a removal on its night: probe N finds no pair of a noted gone statement and a ruling text that admits, before or after.
3. Partly met. "Remove X and Y" admits both, which is right. "Drop X, and keep Y" admits Y as well as X, before and after (F2). "Keep Y and remove X" now admits Y, and before it refused (F1).
4. Met. The list admits "You can drop" and "Go ahead and remove". It refuses "I would not drop", "You should not drop", "You shouldn't drop", "We must not remove", "I don't want you to drop" and "I never asked you to drop".
5. Met. The frame 140 tests still check frame 140's meaning: the same-reply commit is refused, the note is quoted, HEAD does not move, and the next reply commits. Only the step text changed, and the new text is the shared route of review 3, finding 3.
6. Met. The diff is three files. The code hunks are `_unread_drop_refusal`, the new `_CLAUSE_BREAK`, `_REQUEST_VERBS` and `_REQUEST_LEADS`, and `_removal_asked`. `_removal_asked` has one caller, `_asks_removal`. No recorded case holds the old text "You sent this commit before you read", so no replay goes stale on it.

## (b) Findings

1. **The request is read in its clause, but the name is read in the whole sentence.** `rota/roles/api.py:17558-17572` (`_removal_asked`) and `17580-17596` (`_asks_removal`). Low for the night, high for the frame. CONFIRMED.
   - Probe S, group X: four shapes moved from refuse to admit, and each one keeps `ctx.exit()`.
   - "Keep ctx.exit(), and remove the extra echo." admits.
   - "Do not remove ctx.exit(), but drop the blank line." admits.
   - "Do not touch ctx.exit(); remove the comment above it." admits.
   - "ctx.exit() must stay, so please delete the debug print." admits.
   - Before, the negation in the earlier clause refused each one. Now the earlier clause is cut off for the verb, but the name test still reads it.
   - The shape "keep X, and remove Y" is the principal's common shape: n143, n146, n152 and n154 use it. Probe N measured no gone statement named in such a sentence on nights 140 to 158.
   - Fix: return the span of the request clause from `_removal_asked`, and match the name only in that span, or in the clause before when the request is "which ..." or has the object "it" or "them".
2. **"Drop X, and keep Y" admits the removal of Y.** Same lines. Low. CONFIRMED.
   - Probe S, group P3: with `echo(message)` gone, "Drop ctx.exit(), and keep echo(message)." admits the echo removal.
   - The pass 3 rule did the same, so this is not new. The F1 fix closes it: the name must sit in the request clause.
   - Fix: the F1 fix. Add the sentence to the frame 283 shape test with the side False for `echo(message)`.
3. **A bare "stop" admits a removal of a named statement.** `rota/roles/api.py:17544`. Low. CONFIRMED.
   - Probe S: "Stop the command after ctx.exit() runs." admits, before and after.
   - "stop" with an empty lead is a request, but not a request to remove the named line.
   - Fix: admit "stop" only with a gerund after it, as in "stop calling".

Outside the points: none found beyond the path note above.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r4/`. Each ran from `C:/Users/roman/rota_r283` with `D:/repos/rota/.venv/Scripts/python.exe`. `api_old.py` is `git show d2b4f79a:rota/roles/api.py`, loaded as `rota.roles.api_old`.

- S, `r4_shapes.py`: `_asks_removal` at cbdc68f8 and at d2b4f79a on the eleven shapes, "Do not remove", "Never drop", eight lead shapes, eight clause shapes and four clause cuts with two gone statements.
- N, `r4_nights.py`: nights 140 to 158, read-only. It takes every `` `line` at line N `` of each write note in `turns.user`, and every ruling text of `_ruling_texts` over all batches of the night. It tests each pair with both rules. Result: 136 gone statements on 10 nights, and zero pairs admit under either rule. The parse found no statement on night 150, which holds two note texts, so night 150 is a gap.
- T: `tests/rota/test_frame283_removal_on_ruling.py` and `tests/rota/test_frame140_commit_beside_note.py` with `-n 0`, 80 passed.
- G: `git grep` for the old same-reply text: only `plans/stack.md` holds it.
- The pass's count ran on `C:/Users/roman/rota_p283`, and that worktree is at cbdc68f8 and clean.

## (d) Usage

- Input: about 60k tokens of context at the end. The harness gives no exact split.
- Output: about 8k tokens.
- Total: about 68k tokens, against a cap of about 30k.
