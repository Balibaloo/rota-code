# Review p7 of frame 354: commit 1f8e6e1a

Verdict: the claim holds, with 0 high and 5 low findings. Points: 6 hold. Point 2 holds with three findings on forms outside the claim. Point 3 holds with one finding. Point 5 finds no hunk outside the claim. Tests: 25, 48, 11 and 137 passed, 0 failed. L3R: 23 of 25 passed, and no case moved.

## (a) Verdicts on the points

1. Holds. After "1 ok 2 try again" on a page of I1 and the step, the line says 'line 2 runs again; 1 line approved.' `read_back_rows` gives `[('I1', 1, 'approve'), (KEY, 2, 'contest')]`, so the line and the landing wake agree. When the step runs through, his retry reads back on the next page of other work, as line 2 of the page of I2. When the step stalls again, the page has the step on line 1 with "You asked me to try it again once before", and the read-back on line 2 says "line 2 runs again". See finding 1.
2. Holds for the claimed forms. On a page of two lines and of three lines, "1 ok 2 drop", "1 ok, 2 drop" and "line 1 ok 2 drop" bind line 1 and line 2 apart. "1 try again" binds line 1 only. "2 examples are too many", "I want 2 examples", "3 at most" and "Drop both of those examples" name no line, so every line takes the whole reply. "1 drop it 2 ok" binds the whole reply to line 1 and leaves line 2 unnamed (finding 3). "1: drop" names every line (finding 2). In `_nearest_sentence` nothing changes, because it reads only the tokens and the cut adds only cuts. In `_words_outside` the span check accepts more spans: "2 drop" now holds in "1 ok 2 drop" and in "I never said ok 2 drop" (finding 4). "ok 2" is still refused.
3. Holds as claimed. On a present with `body_refs` `[]`, each of `{"rest": "approve"}`, `{"1": "drop"}` and `{}` returns `per_item` `{}` and the note "The ask closes, and nothing is ruled". Each writes one `rulings` row with `per_item` `{}`, status `landed`, and 0 `ruled_refs` rows. The ask becomes `answered`. The next `render_state` says "Nothing waits on you and nothing is building." Nothing tells him that the page closed, and his "drop" is read back nowhere (finding 5).
4. Holds. A scripted `drop` and a scripted `try again` stage 0 `faults` rows. `drop` writes one `keypress` and one `landed` row with `approve`, and the `tick_attempts` row stays with `quarantined` 1 and `reported` 2. `try again` writes one `keypress` and one `landed` row with `contest`, and the `tick_attempts` row is lifted. The ask is `answered` in both.
5. None outside the claim. The `readings_owed` query now groups by `reply_id` with `MIN(ruling_seq)`, which keeps the old order. The `page_clauses` coverage check and the `_clause_tokens` cut serve the binder claim, and the pass report names them as deviation 3. Their reach into the cue doors is finding 4.
6. `test_frame354_quarantine_page.py -n0`: 25 passed. `test_r1_menu_form.py -n0`: 48 passed. `test_agent_principal.py -n0`: 11 passed. `test_runner.py -n0`: 137 passed. `test_l3_rulings.py -n0`: 2 failed, 23 passed. The reds are L3R-n171-m27-m28 and L3R-n172-m76-m77, the same two as p6. No case moved off 23 of 25.

## (b) Findings

1. rota/roles/principal.py 1303-1330, low, CONFIRMED. On the page of a step that stalls again, the read-back says "line 2 runs again", and line 2 of that page is the read-back line itself. The step moved to line 1. Probe p1, case A, shows both lines. The step line also says "You asked me to try it again once before", so the page states the retry twice with two different numbers. Fix: when the read-back rides a page that shows the same step, name the step by its text, or let the step line carry the read-back.
2. rota/roles/api.py 13573, low, CONFIRMED. "1: drop" names every line of a page of two or three lines. `_PAIR_WORD` allows a colon, but `_clause_spans` cuts at the colon first, so the pair never reaches the binder. The p6 wall comes back for this form: the seat must rule every line. Fix: read a leading "N:" as "line N" before the colon cut, or remove `:?` from `_PAIR_WORD` so the list says what it binds.
3. rota/roles/api.py 13580-13589, low, CONFIRMED. "1 drop it 2 ok" binds "1 drop it 2 ok" to line 1 and gives line 2 no words. `_PAIR_END` needs a menu word right before the second number, and "it" is not one. Line 1 then carries the words "2 ok", and line 2 takes approve with no words of his. Fix: cut at a bare number before a pair word when an earlier line name stands in the clause, without the end word.
4. rota/roles/api.py 12145-12147, low, CONFIRMED. The pair cut in `_clause_tokens` drops a negation from the span check. `_words_outside("2 drop", "I never said ok 2 drop")` returns None, so a seat can quote "2 drop" as his words. The binder itself does not bind that reply, so the reach is the cue doors and `rulings_rule` words only. No recorded reply has this form. Fix: skip the pair cut when `_NEGATED` matches the words before it in the clause.
5. rota/roles/api.py 14943-14948, low, CONFIRMED. On a page with no line, `{"1": "drop"}` closes the ask with nothing ruled, and his words read back nowhere. The note goes to the seat only. `render_state` then says "Nothing waits on you", so he does not learn that his "drop" ruled nothing. The pass report names this doubt. Fix: the assistant rules. One option is a read-back line owed on his reply when a map with a line key lands on an empty page.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/393648aa-e5f9-4235-ad76-56489455e14e/scratchpad/f354p7r/`. They ran from `C:/Users/roman/rota_f354r` with `ROTA_MODEL=qwen3:8b`. No model call ran.

- `common.py`: the fixture copied from p6.
- `p1_mixed_retry.py`: copied from p6. It rules "1 ok 2 try again", then prints `reading_line`, `read_back_rows`, the next page of I2, and the page where the step stalls again.
- `p2_binder.py`: `line_words` and `page_clauses` on the ten forms on pages of two and three lines, then `_words_outside` and `_nearest_sentence` on five spans.
- `p2b_faults.py`: copied from p6. `land` with scripted `revise`, `contest`, `try again`, `drop` and a mixed reply. It prints `faults` and `rulings`. No `faults` row shows.
- `p3_empty.py`: `rulings.rule` with three maps on a present with `body_refs` `[]`. It prints the return, the writes, the ask status, the row counts and `render_state`.
- `p4_state.py`: scripted `drop` and `try again` through `land`. It prints the `faults` count, the `ruled_refs` rows, the `tick_attempts` row and the ask status.
- The point 6 runs with `-q -n0`. The worktree holds no `cassettes.db`, so the L3R run read a copy of `D:/repos/rota/tests/rota/cassettes.db` through `ROTA_DEV_DB`. The copy is deleted.

## (d) Usage

The harness shows no exact counts, so these figures are estimates. Input: about 50k tokens of context at the end. Output: about 10k tokens. Total: about 60k. The brief's cap was 30k, and the cap did not hold.
