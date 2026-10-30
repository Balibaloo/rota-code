# Frame 344, the sprint rows from the audit, drafted 2026-10-30

Head: `rota/foundation` at df9293fb. Sprints 28 to 31 built a fix for every fact of the two audit pages between 2026-10-27 and 2026-10-28, and frames 345 and 347 retired the Liaison's word form. At head, 33 of 37 facts read one reader or are moot, and 4 keep a residue (observed: `git log --since=2026-10-27 -- rota`, the frame 344 status lines, grep at head).

## 1. The verdicts at head

| Fact | Audit | At head | Fixed by, or the residue |
|---|---|---|---|
| F1 | PARTIAL | FIXED | 475e083b, `ruled_refs` the one store. Three comments still name the old map (f1-review-p1 point 1), no reader |
| F2 | PARTIAL | FIXED, moot | e1e0e4fc `_line_reading`, then 559b2540 and f5487759 retire the page word form for the menu (frames 345, 347) |
| F3 | PARTIAL | FIXED, moot | 4886c8ae, bebaa2d5, then the menu form |
| F4 | PARTIAL | FIXED | e0514007, the `latest_runs` view |
| F5 | OPEN, known | FIXED | 695e3beb, `harness.error_line` |
| F6 | OPEN, unknown | FIXED as a fact | 72846cc4, the probe: every rule gives one criterion for 85 tests on 4 nights. One gap outside F6 stays, see read R1 |
| F7 | OPEN, known | FIXED | c8c819cd, the commit compares the base with the tree |
| F8, F9, F11 | PARTIAL | FIXED | 33d49c3b, `stray_paths` on `_grain_path`, `_is_test_file`, the `_grain_path` sweep |
| F10, F12 | PARTIAL | FIXED | 0e1675dc, `item_callables` and one test-body reader |
| F13, F14 | OPEN, known | FIXED | e040eea2 `module_of`, 592371de `assert_cannot_fail` |
| F15 | OPEN, known | PARTIAL | 38a44c39 `request_of`. 9 sites still call `_items_reached`, which has no `tests` lookup: principal.py 268, 1545, 2303, 3302, 3516, 3695, api.py 14715, predicates.py 1780, scheduler.py 1177 (observed: grep). f15-review-p1 named `off_page` and `page_request` |
| F16 | OPEN, known | FIXED | cc46a790, `mark_answered` the one writer |
| F17 | OPEN, known | moot | closed into W8 at 1fab56ca: a copy of a landed call is answered as done |
| F18 | PARTIAL | FIXED | 1629b3aa, `_quote_reads` at both |
| F19 | PARTIAL | FIXED, one doubt | f8955d32. `_seat_forms`, `_one_backslash`, `_unescaped` are gone. `_escape_note` api.py 26063 does not call `_call_values` in its body head; not read further |
| F20 | PARTIAL | PARTIAL, low | ba128953, c41cdffb `quarantined_keys` and `key_parts`, a7127d41 the lift. `loop.step` loop.py 336 marks every quarantined key reported by its own SELECT. f20-review-p1 finding 6: three deletes skip `lift_keys`, and `invariants.i6` parses keys by its own rule (not re-read at head) |
| F21 | PARTIAL | FIXED | ba128953. `kind_words` and `gave_up_on` are gone (grep) |
| F22 | OPEN, known | FIXED | 471ec356, `db.table_of`. f22-review-p1 named literal chains outside the pin, not re-read |
| F23 | OPEN, known | FIXED | 2b445996, `db.journal_author`. A status-only write passes for another role by design. Frame 280 owes a close line |
| F24, F27, F29, F32 | PARTIAL, OPEN | FIXED | 1629b3aa. `discover.py` 31 reads `OLLAMA_HOST` |
| F25 | PARTIAL | PARTIAL | 2bbace14. `KNOWN_UNHELD` test_f25_offers_in_mode.py 338 holds 4 offers outside the seat's mode, and 7 strict xfails stay (f25-review-p1 point 5) |
| F26, F28, F33 | PARTIAL, OPEN | FIXED | 97b7ff0c, and d81fd5b4 `seen_order` in the harness |
| F30, F34, F36 | FIXED | FIXED | the audit |
| F31 | OPEN, known | PARTIAL | e42d13d1 `asks_for_docs`. `_HEADLINE_NAMES_DOCS` api.py 5956 (read at 5982) and `_ABOUT_TEXT` 8022 through `_about_text` (read at 11027, 11035) still decide documentation by their own list. `_ABOUT_TEXT` holds "comments", the ruled words do not |
| F35 | OPEN, known | FIXED | 7021f964 `predicted_files`. 5 raw `FROM batch_touch` reads remain, 2 in lifecycle.py |
| F37 | FIXED | FIXED | 4547edee, the residue |
| Frame 233 | OPEN, known | FIXED | 5b59b63a, the cassettes store `done_reason` |

Counts at head: FIXED 33 (F2, F3 and F17 moot among them), PARTIAL 4 (F15, F20, F25, F31), OPEN with the cause known 0, OPEN with the cause unknown 0 among the facts and 1 residue gap outside them (F6's inherited test).

## 2. The rows

### The page and the agenda read `_items_reached` direct, so a test row reaches no request (2026-10-30)

- **Site: `principal.request_of` and its 9 bypass sites.** Meta workflow.
- Ends when: every reader of the request a row belongs to calls `request_of` or `requests_of`, a source pin holds it, and an agenda page carries no row of another item over 3 nights.
- Waits on: nothing. Priced an instrument, 3 cycles, about 120k tokens on Opus.
- Sprint: next sprint, rank 1, reach 9 times 4 nights is 36.
- Reach: 9 sites call `_items_reached` direct (observed: grep at df9293fb).
- Pointer: `plans/rootfix-audit-2026-10-27-a.md` F15; `plans/f15-review-p1.md`.

### Three quarantine writes and one invariant keep their own key rule after F20 (2026-10-30)

- **Site: `scheduler.quarantined_keys`, `key_parts` and `db.lift_keys`.** Meta workflow.
- Ends when: `loop.step`, the three deletes and `invariants.i6` read keys through `key_parts` and lift through `lift_keys`, with a source pin.
- Waits on: nothing. Priced a door text, 2 cycles, about 80k tokens on Opus.
- Sprint: next sprint, rank 2, reach 4 times 8 nights is 32.
- Reach: 4 sites, loop.py 336 observed at head, the other 3 from `plans/f20-review-p1.md` finding 6.
- Pointer: `plans/rootfix-audit-2026-10-27-b.md` F20.

### Four offers a seat's mode does not hold stay listed as known, so a refusal can still name a call the seat lacks (2026-10-30)

- **Site: `sandbox.follow` and `KNOWN_UNHELD`.** Meta workflow.
- Ends when: `KNOWN_UNHELD` is empty and the 7 strict xfails are gone or each names an open frame.
- Waits on: nothing. Priced an instrument, 3 cycles, about 100k tokens on Opus.
- Sprint: next sprint, rank 3, reach 4 times 5 nights is 20.
- Reach: 4 offers and 7 xfails (observed: test_f25_offers_in_mode.py 338; `plans/f25-review-p1.md` point 5).
- Pointer: `plans/rootfix-audit-2026-10-27-b.md` F25.

### Two documentation word lists stand beside `asks_for_docs` (2026-10-30)

- **Site: `api.asks_for_docs`.** Meta workflow.
- Ends when: `_HEADLINE_NAMES_DOCS` and `_ABOUT_TEXT` are gone or read `asks_for_docs`, and "comments" is kept only where a ruling names the word.
- Waits on: nothing. Priced a door text, 2 cycles, about 80k tokens on Opus.
- Sprint: next sprint, rank 4, reach 3 times 5 nights is 15.
- Reach: 2 lists at 3 sites (observed: api.py 5982, 11027, 11035).
- Pointer: `plans/rootfix-audit-2026-10-27-b.md` F31; DECISIONS.md 1515 to 1531.

### R1. A merged Tester test loses its criterion link when the next batch inherits it (2026-10-30)

- **Site: read only, the inherit path of a merged test.** Meta workflow.
- Ends when: the cause is named with its reach, the writers that copy a test into a new batch and which of them drops `criterion_id`.
- Waits on: nothing. Priced 1 read cycle on Opus, about 80k tokens.
- Sprint: next sprint, after the four rows, reach 7 copies times 1 night.
- Reach: 7 inherited copies on night 170's b_3, none red (observed: frame 344 status 2026-10-27 19:48).
- Pointer: `plans/f6-probe-2026-10-27.md`.

## 3. Overlap with the stack

No draft duplicates a heading on the stack, so none is dropped. Three overlap:

1. The F15 row covers frames 241 and 316, the agenda page carries another request's rows. Fold both into the row.
2. The F20 row overlaps frame 242, a raw status write skips the lift. Frame 242 is the lift half; the row is the key-parse half.
3. The F31 row touches frame 311, whose wall the audit put in the documentation list of `_pass_lines_check`.

## 4. The doubt

1. F19's `_escape_note`, F20's three deletes and `i6`, and F22's literal chains were not re-read at head.
2. Nights per row are the audit's nights 160 to 170. Nights 171 to 174 were not read.
