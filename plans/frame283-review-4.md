# Frame 283, review 4 of the pass 4 commit 02ea9522

Agent: Opus, read-only, 2026-10-17. Worktree `C:/Users/roman/rota_r283` at 02ea9522. Old code in `C:/Users/roman/rota_r283old` at 7471569c.
Verdict: the commit does not stand. F1 to F5 are fixed. The subset rule of `_changed_kept` hides a real loss on click's own `version_option`, the shape of s283 and s341.

## (a) Verdicts on the points

1. Review 3's F1 to F5 are fixed (observed: probes A to E and R3d on 02ea9522). C opens a note under the renamed owner. E opens a note on a base that does not parse. R3d closes on `X = 5`. F1's probe F still meets the span door at end=5, and the new test runs it at end=4. F4 and F5 are fixed in the test helper and in the `_put_note` docstring.
2. 19 tests are green on the old code, and 10 are red (observed: the new test file run in the old worktree). The green ones are the unchanged tests and `test_s282s_commit_beside_the_noted_write_is_refused[False]`, the new two-commit shape. That shape is F4's coverage fix, so green on the old code is expected. Three red tests are red only by `AttributeError: _changed_kept`: `test_s192s_widened_except_tuple_is_no_dropped_line`, `test_a_line_whose_tokens_sit_across_two_lines_is_still_dropped` and `test_a_line_of_two_tokens_is_never_kept_by_the_subset_rule`. They call the function on a hand-built entry, and no test sends the s192 write through `code.write`.
3. The subset rule hides real losses. See finding 1. In the count, 2 of the 23 right refusals (s283, s341) lost `if version is None:`, and the click callback holds a superset line beside it.
4. Yes. A ledger that quotes the refusal text back with the path closes any note with no restore (observed: probe PARROT). A note that shows no stored line closes on any ledger that names the path, such as "I edited src/m.py today" (observed: probe PATH-ONLY). The first matches the frame's intent: the landed note is the seat's word, and the Architect reads it. The second is weaker than the intent: see finding 2.
5. s340 and s388 are still refused at the commit (observed: 02ea9522). `test_s388s_commit_in_the_next_reply_with_no_write_is_refused`, `test_s340s_unchanged_write_sends_the_note_again_and_holds_the_commit` and `test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused` pass on the two-commit base. The three files pass 65 of 65.
6. The next night meets finding 1 first: a Developer that rewrites `version_option` and drops `if version is None:` commits with no refusal.

## (b) Findings

1. `rota/roles/api.py:16094-16110` `_changed_kept`, high, CONFIRMED (observed: probe SUBSET on click's `decorators.py`). The rule compares the dropped line with every line of the write's text. Unchanged old lines are in that text. Click's callback holds `if version is None and package_name is not None:` at line 512. A write of lines 506 to 560 without line 539, `if version is None:`, opens no note. The same holds for `self.conn.commit()` dropped once of two, and for `x = int(x)` beside `return int(x)`. The floor counts repeated words, so `x = int(x)` passes the floor with two distinct tokens. Fix: compare only against new lines that the old text did not hold, and count distinct tokens for the floor.
2. `rota/roles/api.py:16195-16199` `_close_logged_notes`, low, CONFIRMED (observed: probe PATH-ONLY). A note that shows no stored line closes on any ledger that holds the path. A ledger "I edited src/m.py today" closes it. This shape occurs when the base filter or the subset rule removes the shown line, or when a merged note keeps an earlier write's lines. Fix: require the path and one word of the removal, for example "remove", or the note's shown kept line `a`.
3. `rota/roles/api.py:16195-16201` `_close_logged_notes`, low, CONFIRMED (observed: probe DEF-UNNAMED). A note with lines and a dropped definition closes on one shown line. The old rule also required each definition name. Pass 4 deviation 2 records this as reasoned, not ruled. Fix: keep `all(_says(assumption, d) for d in e["defs"])` beside the line rule, or get a ruling.
4. `tests/rota/test_frame140_commit_beside_note.py`, low, CONFIRMED (observed: point 2). No test renders `_changed_kept` through `code.write`. The order `_changed_kept` then `_base_held` in `_code_write` (api.py:15493) has no case. Fix: add one s192 test that writes the widened tuple with `code.write` on the two-commit base and asserts no open note.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/`.

- `r3/test_probe_r3b.py`, `r3/test_probe_r3c.py`, `r3/test_probe_r3d.py` on 02ea9522 with `pytest -s -p no:xdist --rootdir .`: 12 passed, probe F failed at the span door. A, C, D and E open notes. R3d leaves no open note.
- `r4_newtests.py`: the new test file at 02ea9522, copied as the untracked `tests/rota/test_r4_new.py` in `C:/Users/roman/rota_r283old` at 7471569c. 19 passed, 10 failed.
- `r4_probe_subset.py`: five hand-built entries through `_changed_kept`. All five are hidden.
- A `python -c` call: click's `decorators.py` lines 506 to 560 without line 539 through `_changed_kept`. Result HIDDEN.
- `r4_probe_close.py`: PARROT, DEF-UNNAMED and PATH-ONLY on 02ea9522. Each note closes.
- `pytest tests/rota/test_frame140_commit_beside_note.py tests/rota/test_identity.py tests/rota/test_revert_door.py`: 65 passed.
- The old worktree `C:/Users/roman/rota_r283old` stays. Remove it with `git worktree remove --force`.

## (d) Usage

About 40k input tokens and 8k output tokens, 48k in total. This is an estimate. The harness line holds the exact count.
