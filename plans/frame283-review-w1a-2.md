# Frame 283, W1 a, review 2 of pass 2

Review of ee3cbcd0 in `C:/Users/roman/rota_r283`, parent e60a3c25. Verdict: do not accept. Findings 1 and 2 are high. The reviewer edited nothing, ran no gate and re-recorded nothing.

## (a) The claim, point by point

1. Not right. The ledger door now refuses `fault` and `blocked` notes. On the night and at e60a3c25, a fault note landed in `faults`. Land fault notes as before. A refusal of `scope` and other page kinds is consistent with law 4, and the escalate route carries the claim.
2. Findings 2 and 6 are open, and finding 3 is half open. Findings 1 and 5 and the s279 seq 17 note close on their own cases. Negation and "without" admit a removal that a sentence forbids. No right removal of nights 140 to 158 is refused.
3. Kept. The revision keeps the frame 140 rule: a commit beside a note is refused and waits for the next reply. It removes only the close rules of frames 297 and 283. `_note_says` is dead in production, and `_removal_list` has no caller. Delete them with their rule tests in this pass.
4. The doors agree on the unruled removal and on the restore then second removal. They disagree on the ruled removal in the same reply. A non-statement drop lets the note land with no text while the commit door refuses, as before this pass.
5. One case goes stale: `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on`, runs 2, 4 and 5 on qwen3:8b. No other run holds the old texts.

## (b) Findings

1. **The ledger door refuses a fault note.** `rota/roles/api.py:10650-10656`, before the `FAULT_KINDS` branch at `10693-10706`. High. CONFIRMED.
   - Probe P1: on the s279 replay, `fault`, `blocked`, `scope` and `gap` notes all get the ledger text. No `faults` row is staged.
   - A fault about the real problem of the night, "the span door refused my write back three times", is refused too. The text tells the seat to put the line back, and the span door refused that route on the night.
   - At e60a3c25 the fault branch returned before the drop-note door. A fault note closes no drop note, because it returns before `_close_logged_notes`. So the refusal protects nothing and hides a report of rota.
   - For `scope` and other page kinds, the refusal keeps the claim off the page. Law 4 supports that: the claim is about a change that no commit holds. The escalate route in the text carries the claim to the Architect.
   - Fix: move the drop-note door below the fault branch. Land a fault note, and add the drop-note fact to its result as a `note` field.
2. **A sentence that forbids the removal admits the removal.** `rota/roles/api.py:16878-16901` (`_REMOVAL_WORDS`, `_DEMAND_WORDS`, `_asks_removal`). High. CONFIRMED.
   - Probe P2: these sentences admit the removal of `ctx.exit()`: "Do not remove ctx.exit().", "ctx.exit() must not be deleted.", "Never drop ctx.exit() from the callback.", "Removing ctx.exit() is a bug."
   - "Without show_python, the option must call ctx.exit()." admits it. This is open question 2 of the pass, and the door must refuse it.
   - "The callback no longer returns early, and it calls ctx.exit() after echo." admits it. "Stop the program with ctx.exit() after the echo." admits it.
   - "In callback, do not drop the early return." admits the removal of a bare `return`.
   - "The callback must still call ctx.exit()." is refused. Only "still" and "keep" guard the door.
   - Fix: refuse a sentence with a negation or a demand, such as not, never, must or should. Drop "without" and "stop" from the removal words.
3. **Page-line numbers of the principal admit a removal by chance.** `rota/roles/api.py:16899`. Low. CONFIRMED.
   - Probe P3: on the night database, the rulings of bg_3, the batch of s279, admit a removal of any statement at line 3 or line 7. "Line 7 just repeats line 3 ..., so drop it." is about a page line.
   - Fix: require the path or the call name of the line in the same sentence, or drop the line-number rule.
4. **The same-reply refusal of a ruled removal says to write the lines back.** `rota/roles/api.py:16719-16742`. Low. CONFIRMED.
   - Probe P4b: with a ruling that asks to remove `ctx.exit()`, the commit in the same reply ends "If it does not, write the lines back, then commit in your next reply." The commit in the next reply lands with no write back.
   - The `held` list is not filtered by `_unruled_gone`. Only the `later` list is.
   - Fix: filter `held` by the same ruling check. For a ruled removal, say only "commit in your next reply".
5. **Finding 3 of review 1 is half open: a merge still carries an earlier removal.** No merge reader of `drop_notes` exists. Medium. CONFIRMED.
   - `rota.tools.map table drop_notes` names four readers: `discard_uncommitted`, `close_restored_notes`, `_closed_notes` and `_open_notes`. None runs at the merge.
   - The pass recorded the merge check as "Fix 4 (record only)". Probe P5a of review 1 stays true.
   - The earlier-commit text works. `test_an_edit_after_an_earlier_commit_removed_the_line_names_that_commit` covers it.
   - Fix: build the merge check, or record it as an open item of frame 283 with its own ends-when.
6. **The ledger close is dead code, and five rule tests test it.** `rota/roles/api.py:17263-17274` (`_close_logged_notes`), `17283` (`_note_says`), `17319` (`_removal_list`). Low. CONFIRMED.
   - `_close_logged_notes` skips every entry with lines or definitions. For an entry with neither, `_note_says` returns False. So the close never writes.
   - `_removal_list` has no caller. `_shown_lines` keeps one live caller at `16247`, and its comment there cites the ledger close.
   - `tests/rota/test_frame140_commit_beside_note.py:1032` has a name that ends in `closes_it`, and its docstring says that the note closes. Its body asserts that the note stays open. The test at `1051` has the same defect.
   - Fix: delete `_close_logged_notes` and its call, `_note_says`, `_removal_list` and the five rule tests in this pass. Correct the comment at `16246`.
7. **The ledger door text has no bound on its list.** `rota/roles/api.py:17388-17396`. Low. PLAUSIBLE.
   - The text lists every stored line that the tree lacks, in full, in the first sentence. Frame 297 cut each line at 60 characters.
   - Each further line adds about four words, so a nine-line row passes 40 words in one sentence. The fix of finding 6 of review 1 changed the commit door only.
   - Fix: put the list in its own sentence, and cut each line at 60 characters.
8. **One recorded case goes stale.** `D:/repos/rota/tests/rota/cassettes.db`. Low. CONFIRMED.
   - Probe P5: 39 `case_runs` rows and 11 cassettes hold "log the removal with ledger.log". All 39 rows are `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on`, runs 2, 4 and 5.
   - The text is the later-reply commit refusal on a whole-file drop of seven lines of `src/notify/formatting.py`. The new route text replaces the old one, so the next prompt changes and its cassette key misses.
   - No run holds the old ledger door text "This note names none of them", or "discharge a removal".
   - Fix: re-record runs 2, 4 and 5 of that case after the fix of findings 1 and 2.

Outside the points:

- A note of the kind `assumption` gets the drop-note text before the kind door. The seat learns that its word is wrong only after it restores the line. Low, PLAUSIBLE. Fix: the fix of finding 1 can move the door below the kind door too.
- A drop with no stored line or definition lets a ledger note land with no text, while the commit door refuses with the write route. This was true at e60a3c25. Low, PLAUSIBLE from `17384-17386`.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/81fe1025-ee88-45f4-8210-744972761835/scratchpad/r2/`. Each ran from `C:/Users/roman/rota_r283` with `D:/repos/rota/.venv/Scripts/python.exe`.

- P1, `test_r2_doors.py`, test `test_p1_fault_and_scope`: on the s279 replay, four ledger kinds and one unrelated fault note after the removal. All five were refused, and no `faults` row was staged.
- P2, `p1_pred.py`: `_asks_removal` on twelve sentences that forbid, mention or demand the line.
- P2b, `p2_nights.py`: every sentence with a removal word in `_ruling_texts` of every batch of nights 140 to 158. No sentence asks to remove a code statement.
- P3, `p3_lineno.py`: the line-number rule on bg_3 of `D:/repos/rota/.rota/clickI_night158.db`, for the numbers 3, 7 and 550.
- P4, `test_r2_doors.py` and `test_r2_doors2.py`: the unruled removal, the ruled removal in the same reply and the next reply, and a restore then a second removal at line 544. `test_r2_doors3.py` tried a non-statement drop. The span door refused the write, so that path rests on the code.
- P5, `p5_cass2.py` to `p5_cass5.py`: read-only queries of `cassettes` and `case_runs` for the old and new route texts.

## (d) Usage

- Input tokens: about 90k, by the context count. The harness gives no exact split.
- Output tokens: about 12k.
- Total: about 102k. This passes the cap of about 50k in the brief.
