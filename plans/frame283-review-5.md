# Frame 283, review 5 of f99988f5

Verdict: the commit stands. Review 4's F1 and F2 are fixed. Four low findings remain, and none blocks the night.

## (a) Verdicts on the points

1. F1 is fixed (observed: probes R5b and R5d). An unchanged old line no longer hides a dropped line, and a re-indented old line counts as old. The brief's extra shape still hides the loss (observed: probe R5a). See finding 1.
2. F2 is fixed (observed: `r4_probe_close.py`, PATH-ONLY stays open). The "It drops" sentence fires on a tail note with one stored line, and the path alone does not close that note (observed: probe T3). A tail note with no stored line opens no note, so the sentence has nothing to show (observed: probe T5). A line with a backtick and a quote closes when the seat quotes it exactly (observed: probe T4). The display of that line is ambiguous. See finding 3.
3. The s192 test sends the widened tuple through `code.write` (observed: the diff). It asserts that `RuntimeError` is in the file, that no note is open, and that a separate `code.commit` returns `committed` True. The commit is a second call, not part of the write reply. The test passes at 02ea9522 too (reasoned: `_changed_kept(..., before="")` is the old rule, and it returns False on this entry, observed). It is coverage of the call order, not a red-then-green test.
4. s340 and s388 stay refused (observed: `test_s388s_commit_in_the_next_reply_with_no_write_is_refused`, `test_s340s_unchanged_write_sends_the_note_again_and_holds_the_commit`, `test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused`, 3 passed). The three files are green: `test_frame140_commit_beside_note.py` and `test_frame234_verdict_lines.py` 104 passed, `test_runner.py` 137 passed.
5. The next night meets finding 2 first: the s192 reply still tells the seat that its changed `except` line is removed.

## (b) Findings

1. `rota/roles/api.py:16105-16125` `_changed_kept`, low, CONFIRMED (observed: probe R5a). The old text holds `self.conn.commit()` twice and the new text holds it once. A new unrelated line `log(self.conn, 'commit')` holds the three tokens, so the dropped copy opens no note. This is the subset rule's known risk, the same as review 4's `validate(user, token)` shape (observed: R5c). Fix: count a dropped line as kept only when the count of that stripped line in the new text plus the subset matches is at least its count in the old text, or accept the risk by ruling.
2. `rota/roles/api.py:15494-15509` `_code_write`, low, CONFIRMED (observed: probe S192). When `_changed_kept` removes every stored line, `entry` is None but `tail_note` stays. The reply then carries `dropped`: "This write removes 1 statement that your text does not hold: `except (KeyboardInterrupt, EOFError):` at line 3." The seat reads a false fact about the line it widened. No note opens, so the commit door does not refuse. Fix: when `_changed_kept` left no line and no definition, drop `out["dropped"]` or say that the line is changed and kept.
3. `rota/roles/api.py:15505-15506` "It drops" sentence, low, PLAUSIBLE (reasoned: probe T4 output). The sentence wraps the stored line in backticks without an escape. The line `return f'`{x}` "q"'` shows as `` `return f'`{x}` "q"'` ``. A seat can read the quote as `return f'` and quote that, which closes nothing. The quote character also needs a JSON escape in the `ledger.log` argument. A closure works only on the exact line (observed: T4 closes). Fix: choose the first stored line with no backtick for the sentence, or use a double-backtick fence when the line holds a backtick.
4. Outside the points. `rota/roles/api.py:16191-16197` `_shown_lines` with `_says` at 16188, low, CONFIRMED (observed: probe LONG). A stored line longer than 60 characters shows cut, here `result = compute_the_long_value(alpha_parameter, beta_parame`. A seat that quotes the whole line does not close the note, because `_says` needs no word character after the cut text. The "It drops" sentence uses the same cut. Fix: in `_close_logged_notes`, accept the full stored line when the note shows its cut form.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/`. All ran from `C:/Users/roman/rota_r283` at f99988f5.

- `r4_probe_subset.py`: the same five results as review 4, because the probe passes no `before`. Three shapes stay hidden, and they are genuine changed-line shapes with an empty old text.
- `r4_probe_close.py`, run under pytest: PARROT closes, DEF-UNNAMED closes (ruled in review 4's F3), PATH-ONLY stays open.
- `r5_probe_subset.py`: R5a hidden, R5b opens, R5c hidden, R5d opens.
- `r5_probe_tail.py`, under pytest: S192 reply text, span notes ONE, TICK, CMT, CM2, MANY, and LONG with the full-line quote that stays open.
- `r5_probe_whole.py`, under pytest: whole-file tail notes T1 and T2. The note's `from` line is shown, so no "It drops" sentence fires.
- `r5_probe_itdrops.py`, under pytest: T3, T4 and T5, where a changed line removes the first tail line. T3 and T4 add "It drops", T5 opens no note.
- A `python -c` call: `_changed_kept` on the s192 entry with `before=""` returns False.
- pytest on the three test files, and `-k "s340 or s388"`.

## (d) Usage

Input about 48k tokens, output about 9k tokens, total about 57k (estimate from this session's context; the harness line holds the true count).
