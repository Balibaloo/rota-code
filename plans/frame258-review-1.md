# Frame 258, review 1 of e445aa64

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_r258` at e445aa64. Rota workflow throughout. Date 2026-10-16.

Verdict: **accept with fixes**. The door refuses what the frame names, and no named-line ruling moves. One refusal text sends three agreement replies to the request line, and two of those replies are plain approvals.

## (a) Verdict on each point

1. CONFIRMED. All six maps are refused at HEAD and admitted at db7c950d. Three named-line maps are still admitted.
2. CONFIRMED with one finding. 15 of the 16 refusals are right. The text on 3 agreement replies sends the seat to the wrong line (finding 1).
3. CONFIRMED. The m28 row now asserts on a page with no request line. The m181 row, frame 234’s own case, still holds.
4. PLAUSIBLE. The item text gains the constraint, and no batch dies at m25. A contested wake can still make a new item (finding 2).
5. CONFIRMED. 181 passed and 5 xfailed. No assertion of frames 250, 255 or 256 changed.
6. CONFIRMED. The refusal texts and comments follow STE. No finding.

## (b) Findings

1. `rota/roles/api.py:8920-8948`, `_agreed_contest`. Severity low. CONFIRMED by probe 3.
   - Night 121’s m119, "yes that all looks right, go ahead", and night 139’s m132, "ok, this matches what I asked for, so go ahead.", are plain approvals.
   - `_BARE_AGREEMENT` does not fullmatch either reply, so the "adds an instruction" test passes on the agreement sentence alone.
   - The refusal says "their instruction is about the request, line 1 ... rule line 1 as the words say". A seat can read that as "contest line 1". On m119 and m132 a batch line is on the page, so an item contest can cancel the batch.
   - Night 137’s m175 asks for "the new page for the show_python flag". That is a different request. The same text steers the seat to contest the confirm item with the show_python words.
   - The refusal is right on all three. The text is wrong.
   - Fix: require one sentence after the agreeing first sentence. When no such sentence exists, refuse with "The words agree with the page. Approve every line."
2. `rota/roles/api.py:1325-1336`, `_assert_words_fault`. Severity low. PLAUSIBLE.
   - On a `tick:contested` wake, an assert on a new id is admitted, because the `cur is None` branch returns None for every verb except challenge.
   - Night 150’s `json_only` came from that route.
   - At HEAD the contest lands on `echo_json`. The contested brief says "One call, on the item’s own id". The drop check at 1441-1465 keeps `echo_json` in the text. The carried-words check at 1467-1486 admits the json words of the principal. So the instructed path makes the item gain the constraint.
   - No batch exists at m25 on night 150, because that page is the first present. The amendment drops the approval, and the item is presented again. Nothing is cancelled.
   - The door still does not stop a second `json_only`. No recorded case shows this route at HEAD.
   - Fix: on a `tick:contested` wake, refuse an assert on an id that is not in `wake_refs`, and name the contested item.
3. `tests/rota/test_frame234_verdict_lines.py:497-508`. Severity low. CONFIRMED by a read of the diff.
   - The m28 row now runs with `request_lines` empty. No night showed that page shape. The night 147 m28 page had the request on line 1, and the count refuses it.
   - The row now guards the `not request_lines` branch only. The old shape moved to `test_m28s_words_with_the_request_on_line_1_are_refused`, which asserts the refusal.
   - The change is deliberate and is not a weakening. The comment says so.
   - The m181 row, "Ok, go ahead." on the batch line, still returns None with request line 1. That is the case of frame 234.
   - Fix: none needed. Optionally change the row comment to "a page that shows no request".

Point 2 in detail. Probe 2 lists 18 maps that move: 16 newly refused, and 2 that now also name the batch line (night 143 m142, night 146 m259).

- Night 150 m25, night 149 m25, night 147 m29: they contest the description row, or the description row and a note. Refusal right.
- Night 121 m119, night 139 m132: they contest a batch line on a plain approval. Refusal right, text wrong (finding 1).
- Night 137 m175: it contests all 13 lines for a request about another flag. Refusal right, text wrong (finding 1).
- Night 150 m38, m53, m59, night 138 m49, night 142 m327, night 144 m375: a batch line is contested, and the words fault criteria only and name no files or tests. Refusal right by the night 150 evidence, where m37 cost an Architect relay.
- Night 140 m98: line 3 is a description row, and "It should also name ..." follows line 1. Refusal right.
- Night 150 m140: "Ok, I approve the page." contests the description row. Refusal right.
- Night 150 m317: lines 3 (`json_only`) and 9 (`how_it_works`) are never named. "They repeat ..." follows "Lines 4 to 8". Refusal right.
- Night 146 m64: it contests line 3, `echo_json_output_format`. "It also points at the existing echo function ..." follows "Line 5", and line 5 is the prediction of bg_3. The surface ref of the criterion at the night end is also `src/click/utils.py::echo`, so the seat may have read "It" as line 3. The grammar binds "It" to line 5, and the criterion does not say "return a string". Refusal right, with doubt. No high.

Outside the points:

- The line-1 refusal near `api.py` 8780 still uses the old unnumbered test, not `_unnumbered`. The pass report names it. No case shows it. Low.
- `_LINE_WORD` leaves alone any reply that holds "note" or "notes", for example "Please note that ...". That is a bypass of `_agreed_contest`. No case shows it. Low.
- `request_lines` comes from `_is_request_item`, which leaves out a delivered item. After a merge, the line of that item loses the item spare until its version moves. No case among the 160 shows it. Low.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cc1d654e-81ee-41bf-8230-9fa3f5a060b9/scratchpad/f258/rev1/`. Every night database was opened `mode=ro`.

1. `run_count.py` runs the `count.py` of the pass with `sys.path` on the worktree. The main checkout has an uncommitted `rota/roles/api.py` from another frame, so it was not used. Output in `head.out`, then in `parent.out` with `api_db7c950d.py`. That file is byte-equal to `git show db7c950d:rota/roles/api.py`. Result: a 160 and b 204, refused 72 against 56, and 17 b refusals at both.
2. `pair.py` compares the a sections of the two outputs. `moved.txt` holds the 18 moved maps with the refusal texts.
3. A `python -c` call checks `_BARE_AGREEMENT` on the m119, m132 and m140 openings. All three return False.
4. `bthree.py` runs the night 150 named-line maps m7, m67 and m78 through the same door at HEAD. All three return None.
5. A heredoc reads the full words and `per_item` of night 146 m64, night 150 m317, m38 and m25, and night 149 m25. It also reads the criteria texts of night 146.
6. `pytest` ran `test_frame234_verdict_lines.py`, `test_frame250_verdict_faults.py`, `test_frame255_files_correction.py` and `test_request_page.py` with `ROTA_MODEL=qwen3:8b`. Result: 181 passed, 5 xfailed. `git diff db7c950d e445aa64 --stat -- tests/` shows that only the frame 234 file changed.

The probes replay `_line_refusal` with inputs that the `door()` function of the count rebuilds. They are not a live `rulings_rule` call. The rebuild matches `rulings_rule` at 9271-9296. The one difference: it takes `request_lines` from the "You asked:" header of the page, because the night-end state marks some items delivered.

## (d) Usage

The harness counter fell about 85k over the review. The agent cannot see the input and output split. The estimate is about 75k input and 10k output, 85k total. That is over the 60k cap, because each turn reads the context again.
