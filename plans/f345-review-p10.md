# Frame 345, pass R2 review (p10): commit f5487759 on r2root

Verdict: NOT READY. The code of R2 is sound on the clarify, the shift page and the doors. The test sort deleted landed-row pins, and one guard changed behaviour. High 1, low 2.

## (a) Verdicts on the points

1. Partial. 55 of 120 gate reds replayed at the parent, and all 55 are red there. No id is green at the parent. 65 L1 ids are not replayed, because the serial plugin runs L1 one case at a time at about 90 s each.
2. Clean. All 27 doors had callers only inside `rulings_rule` or inside each other. `runner.py` 2472 read `MENU_PAGES` in a guard that R2 rewrites to the same truth. No clarify, shift page, `principal.land` or other seat reached a door.
3. Finding 1. 6 of the 15 sampled tests pinned a landed row or a path outside the word form. The sort rule deleted them because the name or one assertion held a refusal.
4. 74 of the 101 skipped tests assert a landed row. A script that inverts `_OPTION_ROWS` moves most of them. The 27 others pin a non-refusal of a deleted door and have no menu equivalent.
5. Yes, the acknowledgement is the parent's behaviour. `None`, `[]`, a string and an empty map on a lined page take the menu refusal. One exception: a non-empty map on a page with no line and no ref lands (finding 2).
6. Clean. A clarify and two shift-page calls write the same rows at both trees.

## (b) Findings

1. tests, 6 of 15 sampled deletions. Severity high. CONFIRMED by `asserts.py` and `body.py` on the parent bodies. The rule "a name with refus, or an assertion on refusal text" deleted tests whose later lines pin landed rows and other seats:
   - `test_park_page.py::test_a_whole_approve_on_a_park_page_rests_the_park` pins the run commit, the park ask answered, `park_ask` empty and invariant `i5`.
   - `test_request_page.py::test_a_revise_of_the_item_line_lands_with_the_words_on_the_item` pins the item `contested` at version 4 and the Vision Keeper wake through `_resolve_contest`.
   - `test_runner.py::test_s336s_end_through_the_runner_keeps_then_returns_the_page` pins the runner repeat door, the second wake line and the page return end to end. Kept unit tests cover the parts, not the run.
   - `test_ruled_refs.py::test_the_object_form_writes_the_rows_and_the_flat_form_is_refused`, `test_seam2_word_per_line.py::test_one_word_on_a_line_with_no_words_lands_on_the_whole_reply` and `test_principal_reply.py::test_the_ruling_door_holds_the_page` each end on a landed row.
   - The sample rate, 6 of 15, puts about 35 of the 94 deletions at risk. None of them is on the re-pin list.
   - Fix: restore every deleted test with a landing assertion after its refusal as skipped with the re-pin reason, and re-pin the park and runner ones on a menu refusal now.
2. `rota/roles/api.py` 14289-14292. Severity low. CONFIRMED by `test_probe_empty.py`. The menu guard lost the parent's `(order or refs)` term from 14866. On a page with no line and no ref, `{"rest": "approve"}` now lands a ruling with an empty `per_item` and no acknowledgement note. It also skips `_words_outside`. The parent refused it with "'rest' is not a line of the page". Fix: put `(order or refs)` back in the guard, so that page reaches only the acknowledgement or the menu refusal.
3. `C:/Users/roman/rota_r2/.rota-gate.json`. Severity low. CONFIRMED by reading the record. The record names commit b9337a8c with `dirty` true, not f5487759. The 120 reds belong to an uncommitted tree, and "new reds (0)" compares the run with itself. Fix: run the gate once on the clean f5487759 tree after the main register holds a b9337a8c record.

Outside the points: none beyond finding 3.

### Detail for point 2

Inside the parent `rulings_rule`, the clarify and the shift page still ran past the deleted parts. Each part was inert for both:
- `his_lines` was empty for both, so the `WORD_ACTS` branch and `_word_shape` never ran.
- The read-back keys, the guess-key admit (`_request_item`), the account page refusal and the earlier-answer fill carry `not shift` or `not is_clarify` guards. The fill also writes only on contest or revise.
- `asked` is empty for a clarify. Shift words map to park, now and drop, so the note-revise loop, the pointer-fault loop and the `_no_words_refusal` loop skip every shift row.
- The `_line_refusal` block ran on a shift page. Its `contested` set is empty there, so it returned None.

### Detail for point 4

Skipped tests that assert a landed row, by file: test_frame234_verdict_lines 15 of 17, test_frame305_note_revise 8 of 13, test_guess_route 7 of 8, test_seam_night173 6 of 7, test_f2_rulings_words 5 of 5, test_read_back 5 of 15, test_park_page 5 of 5, test_request_page 4 of 4, test_frame250 3 of 3, test_frame337 3 of 3, test_frame193_pass1 3 of 4, test_f25 2 of 2, test_f28 2 of 2, test_ruled_refs 2 of 2, test_frame255 2 of 2, test_principal_reply 1 of 2, test_f345_p5 1 of 1. The others have 0: test_criterion_contest 0 of 1, test_frame258 0 of 4, test_seam2 0 of 1.

Of the 74, 43 call `rulings.rule` directly, 24 through a helper and 7 through a scripted seat TOOL line. The mapping is the inverse of `_OPTION_ROWS` by line kind:
- approve goes to `approve`, or to `ok` on a read-back line.
- contest with drop or remove goes to `drop`, or to `misread, drop` on a read-back line.
- contest or revise with rewrite goes to `rewrite`.
- contest with exclude P goes to `exclude P`.
- approve with add goes to `add <quote>`.
- a bare contest goes to `other <quote>`, or to `misread` on a read-back line.
- a bare revise on a read-back line goes to `slightly off`.

A bare revise on any other line has no option that lands `revise`. Those tests need new expected rows, and most of them are in test_frame305_note_revise. The 27 tests with no row assertion pin a non-refusal of `_line_refusal` or `_unnamed_contest`. Delete them.

## (c) Probes

All probes are under `D:/rota_r2_tmp/probes`. Every run had ROTA_L1 unset, ROTA_MODEL=qwen3:8b, and TMP, TEMP and TMPDIR at D:/rota_r2_tmp.
- `D:/rota_r2_tmp/failed_ids.txt`, `ids_rest.txt` and `ids_l1.txt` hold the 120 gate ids from the worktree record.
- `D:/rota_r2_tmp/parent_rest.txt` holds the result of the 41 non-L1 ids at `D:/rota_r2_tmp/head`: 41 failed.
- `D:/rota_r2_tmp/parent_replay.txt` holds the serial run, stopped after 19 results, all F. `D:/rota_r2_tmp/parent_l1d.txt` holds a second L1 run, stopped after 5 L1 reds. Together they give 55 distinct ids red at the parent.
- `callers.py` lists, by AST, the enclosing function of every reference to the 27 doors in the parent `api.py`. A grep of the parent `rota/` gave the callers outside `api.py`.
- `body.py` and `asserts.py` print the bodies and assertions of the 15 sampled deleted tests from the parent tree.
- `skips.py` classifies the 101 skipped tests in the worktree by call form and assertion.
- `t/test_probe_hold.py` runs the menu form at f5487759 with a partial map, a bad option, an out-of-range line and the empty and non-map rulings. All are refused with no write.
- `t/test_probe_seats.py` runs a clarify and two shift-page calls at both trees. `seats_rota_r2.txt` and `seats_head.txt` differ only in the run time.
- `t/test_probe_empty.py` runs six rulings on a page with no line at both trees.

## (d) Usage

Input tokens: about 95k. Output tokens: about 14k. Total: about 109k. These are estimates, because the harness shows no exact count. The cap was 60k, and the slow L1 replay polls and the door trace took the excess.

## p10b: re-check of 7e19e250 and 11bd1ab8 on f5487759

Verdict: READY for the land. All four points hold. Point 4 holds only on reading, because the release test did not go red in isolation at either tree.

### (a) The points

1. Holds. 15 tests are back at 11bd1ab8, and all 6 that the p10 sample flagged are among them. 79 stay deleted. A sample of 10 deletions, none read before, pin only a word-form refusal text or a deleted door (`_line_refusal`, `WORD_ACTS`, `_KEEP_CHANGE`).
2. Holds. `api.py` puts `(order or refs)` back in the menu guard. The probe now refuses `{"rest": "approve"}` on a page with no line and no ref, and it refuses `{"1": "approve"}` too. The empty map still lands the acknowledgement.
3. Holds. 116 tests carry a skip with "R2", and all 116 reasons name frame 345: "re-pin to the menu form, frame 345: R2 word form".
4. Plausible, not confirmed. `test_release_empties_the_seat` passed 6 of 6 runs alone at the parent and 6 of 6 at 11bd1ab8. R2 changes neither `rota/tools/handover.py` nor `test_handover.py`. The test joins a watcher thread with a 5 s timeout, so it is load-sensitive under the full parallel suite.

### (b) Findings

1. `tests/rota/test_f2_rulings_words.py`, the deleted `test_words_the_seat_adds_to_his_reply_are_refused`. Severity low. PLAUSIBLE from reading. The test pinned law 6 on a page: seat words that he never said do not land. The menu form keeps the property, because it never reads `words`. But no kept test now pins the property on the menu form. Fix: add one menu-form test that passes extra `words` and asserts that the rows carry only his clause.

The builder's replay (`D:/rota_r2_tmp/parent_l1_left.txt`, "66 failed in 1464.23s") closes the 65 L1 ids that p10 point 1 left. With p10's 55 ids, all 120 gate reds are red at the parent.

### (c) Probes

- `D:/rota_r2_tmp/probes/p10b.py` compares the test functions at b9337a8c, f5487759 and 11bd1ab8 by AST: 15 restored, 79 deleted, 116 skips with reasons.
- `D:/rota_r2_tmp/probes/asserts.py` printed the assertions of 10 more deleted tests from the parent tree.
- `D:/rota_r2_tmp/probes/t/test_probe_empty.py` ran again at 11bd1ab8.
- `tests/rota/test_handover.py::test_release_empties_the_seat` ran 6 times at `D:/rota_r2_tmp/head` and 6 times at 11bd1ab8, with -n0.

### (d) Usage

Input tokens: about 14k. Output tokens: about 3k. Total: about 17k. These are estimates.
