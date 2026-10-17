# Frame 283, review 2 of abd3caf4, with the count

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r283` at abd3caf4, 2026-10-17. Meta workflow review of a rota workflow door.

Verdict: does not stand. Findings 1, 2, 5 and 7 of review 1 are fixed. Finding 3 is fixed for dropped definitions only. The commit adds a new red in `test_identity.py`. The count, finding 8, is still not done, and the cap stopped this review before the hand count.

## (a) Verdicts on the points

1. F1 fixed (T1). F2 fixed (T2). F3 partly fixed: T3 closes, T3b does not. F4 fixed for the s282 shape, with a residue (point 3). F5 fixed: 16 passed. F6 fixed for a session that lands, with a residue (finding 4). F7 fixed (the diff, `_unread_drop_refusal`).
2. `drop_notes` has one writer, `_put_note` (api.py:15998), and one reader, `_open_notes` (api.py:15969), by the map. A row lands through `session_commit` as a junction write, as `touch_strays` does. A session that ends without a commit and without an exception lands its rows through `after_landing`. A session that dies on an exception lands no row (finding 4). A merged or abandoned batch keeps its open rows forever. They block nothing, because only that batch's id reads them (finding 5).
3. The ledger route now needs every dropped line's first 60 characters, or every whole definition's name. A short line or a common name passes on a substring: `pass` inside "bypass", `get` inside "get the tests" (T4, T5, finding 3).
4. Not done. The two lists differ because each script reads one result format. A unified scan of the JSON format finds 25 of 26 noted sessions with a later commit. A proxy says the door may refuse about 10 of 25. No session is judged by hand, so b is unknown (finding 6).

## (b) Findings

1. `rota/core/identity.py:41` NATURAL_KEYS, high, CONFIRMED (observed: `pytest tests/rota/test_identity.py` at abd3caf4, 1 failed). `test_every_table_declares_what_makes_two_rows_the_same` fails: "['drop_notes'] declare no sameness rule". The pass did not run the gate. `rota/testkit/fixtures.py:368` `_JUNCTION_LABELS` also lacks `drop_notes`, so a case assertion on the table loads no rows. Fix: add `drop_notes` to NATURAL_KEYS as a (batch, path) relation, and add `("batch_id", "path")` to `_JUNCTION_LABELS`.
2. `rota/roles/api.py:15470` the whole-file branch, high, CONFIRMED (observed: probe T3b). `_whole_drop` does not fill `drop_lines`. A whole-file write that drops only module-level lines, such as `X = 5` and an `if __name__` block, stores no lines and no definitions. A one-line comment write then closes the note. A ledger note can never close the note. This is review 1's F3 shape for every top-level drop that is not a definition. Fix: give `_whole_drop` a `gone_out` list and pass `drop_lines` to it.
3. `rota/roles/api.py:16110` `_close_logged_notes`, low, CONFIRMED (observed: probes T4 and T5). The match is a substring test. A note of the one line `pass` closes on "src/m.py: the bypass is kept". A dropped definition `get` closes on "I will get the tests to pass, nothing removed". The text need not say that anything was removed. Fix: match a line or a name as a whole token in backticks, or ask for a removal word beside it.
4. `rota/core/runner.py:5060` the `except` path of `run_session`, low, PLAUSIBLE (reasoned: `session_fail` lands no `ctx.writes`, and the worktree keeps the noted file). A session that dies after a noted write leaves the dropped text uncommitted and no `drop_notes` row. The retry session commits the removal with no note, which is review 1's F6 shape. Fix: land the staged `drop_notes` writes in `session_fail`, or accept the residue with a record line.
5. `drop_notes` rows of a merged or abandoned batch, low, CONFIRMED (observed: the map lists `_open_notes` as the one reader). The rows stay `open` and block nothing. Fix: none needed now. Close them at merge if a reader ever counts open notes.
6. Finding 8 of review 1, the count, high, CONFIRMED (observed: the scripts and the unified scan). `probe_exposure2.py` matches `"dropped": "This write` in one-line JSON results, and its commit regex needs the key order `"committed": true, "head_commit"`. `count2.py` matches the `[dropped]` form in the last 6000 characters only. So the lists share s453 alone. The unified JSON scan adds s197 (141), s132 and s158 (147), s228 (149), s297 (151), s282 and s283 (153), which the probe's commit regex missed. count2's s340, s341, s343, s346 (154), s173 (146), s291, s292 (152) and s158 (147) use the bracket form, and the JSON scan does not see them. The proxy over the 25 JSON sessions: later writes hold the note's heads in 16, a ledger call names them in 3. Ten have neither: s197, s463, s146, s158, s132 (151), s297, s314, s379, s381, and s453's first commit dd6f422f is unclear. Fix: one script reads both formats, replays `_note_entry` and `_restored` on the file text from the batch's commits, and a person judges each refused commit from its turns.
7. `rota/roles/api.py:16080` `_restored`, low, CONFIRMED (observed: probe T3). A dropped whole definition counts as back when its name is back. The body is not checked, so `def b(): pass` restores a note on a ten-line `b`. Fix: store the definition's lines too, as the span path does.

## (c) Probes

Every probe ran from stdin, with no file written, from the worktree root with `D:/repos/rota/.venv/Scripts/python.exe`. Review 1's `probe_helpers.py` and `probe_tail.py` import `_note_heads` and `_head_count`, which abd3caf4 removes, so they do not apply. The stdin probe replaces them.

- Helper probe: calls `_drop_note`, `_note_entry`, `_restored`, `_whole_drop`, `_put_note`, `_open_notes` and `_close_logged_notes` on an in-memory `drop_notes` table. T1, a tail note of 4 lines with one put back: not restored, all back: restored. T2, `return x` moved from `a` into `b`: not restored. T3, a whole-file note dropping `def b`: a comment does not close, `b` back closes. T3b, a whole-file note dropping `X = 5` and `__main__`: lines [] and defs [], a comment closes, a ledger note cannot close. T4, `pass` closes on "bypass". T5, `get` closes on "get the tests".
- `pytest tests/rota/test_identity.py tests/rota/test_frame140_commit_beside_note.py -q`: 1 failed, 30 passed.
- `probe_exposure2.py` re-run: 26 noted, 18 with a later commit, the same as review 1.
- The unified JSON scan of nights 140 to 154, read-only: 26 noted, 25 with a later commit, with the head proxy and the ledger proxy per session.
- The map: `table drop_notes`, `table touch_strays`, `fn session_commit`.

## (d) Usage

Estimate, because the agent cannot read its harness line: about 60k input tokens, 10k output tokens, about 70k total, over the 60k cap. Read the harness line for the true number.
