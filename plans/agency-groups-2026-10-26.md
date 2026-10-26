# The fourteen agency reads, matched by cause, 2026-10-26

Roman asked at about 21:3x on 2026-10-26: "are the proposals all unique? do we have 14 completeley separate issuse?" Read only, at 704f104e, from the fourteen records `plans/frame<n>-agency-read.md`, the prevalence page and the sprint 26 header. Code lines are checked by grep where a section says observed.

## The result

The fourteen frames are 11 groups, not 14 separate issues (reasoned: section 1). Two groups merge five frames: the quote check (333, 328) and his ruling as a record (337, 338, 322). Nine frames stand alone. Seven code places carry edits from two groups, and each needs one pass or a fixed order (observed: section 2). All fourteen share one shape: a fact held once, re-derived by N readers (observed: the prevalence page, "The shape"). The shape is common, and the facts are different.

## 1. The groups

Two frames are one group when one reader, one record or one helper closes both (the brief's test).

1. **The quote check: the disputed row's live text, read by one per-quote `_span_of` rule.** Frames 333 and 328. 333 lines 88 to 90 replace `_quotes_span` at `sandbox.py` 983, 1216, 1222 and 1710. 328 lines 87 to 88 name the same four sites, and "frame 333 takes sites 12 and 13" (observed: the records). Both rest on the ruling of 2026-08-26, "a contiguous span of the disputed row, verbatim" (observed: 333 line 22, 328 line 13).
2. **His ruling: the `rulings` row, one record of his words and his verdict per ref.** Frames 337, 338 and 322. 337 lines 92 to 100: the doors read his exchange from `messages`, and `rulings.words` stores it. 338 lines 52 to 55: `ruled_rows` reads the verdict map, else the landed `rulings` row. 322 lines 87 to 89: one reader of his landed words on an item, by the `per_item` keys of `_ruling_texts`. Each reader re-derives his ruling from a source other than that row (reasoned: the three section 2 tables).
3. **The removal door: a removal is a stray for the Architect.** Frame 339 alone. Its fact is `touch_strays` and frame 286's route, not his words (observed: 339 lines 57 to 60). Its 11 phrase readers go to group 2 by sprint row 6 (observed: stack.md lines 42 to 44).
4. **The stalled seat: `given_up`.** Frame 330 alone. No other record reads the quarantine table (observed: 330 lines 92 to 96).
5. **The escape level of the view: `_render` and one level helper beside `parse_args`.** Frame 335 alone. Its doors are `_cites` and the call-form refusals, not the quote window (observed: 335 line 48, the window doors "tolerate it").
6. **The sibling fact: one sentence in `criterion_repair.md`.** Frame 329 alone. "No overlay of staged rows exists", so no shared reader holds its fact (observed: 329 lines 46 to 48).
7. **The error of a red run: `error_line()` in the harness.** Frame 336 alone. 328's line 4 is near it, but 328 sits in group 1 (reasoned: one group per frame).
8. **The program partition: `areas.kind_of`.** Frame 324 alone. Its fact is `frame_rulings` (observed: 324 lines 20 to 26).
9. **The night's world in the test kit: `_with_repo` by default.** Frame 331 alone (observed: 331 lines 51 to 54).
10. **A debt names its open frame: `open_frames()` and `held by frame N`.** Frame 332 alone. 331 and 332 both edit `OWED`, but neither fix closes the other's cause (reasoned: 331 line 54, 332 line 68).
11. **The brief per mode: `compose` against `mode_tools`.** Frame 334 alone (observed: 334 lines 57 to 58).

A shape crosses groups 5, 6, 1, 8 and 11: a text the seat reads offers an act the door refuses (observed: 335 I4 to I6, 329 B3, 333 instances 7 to 12, 324 place 4, 334 gap A). No single reader closes the five. 334's lint sees a call outside the mode's set only, not a call form or a fact the door refuses (reasoned: 334 line 57).

## 2. The overlap in code

Inside group 1, one pass (observed: grep at 704f104e). 333 and 328 both edit `_answer_evidence` (`sandbox.py` 965, call 983), `_red_line_refusal` (1178, calls 1216 and 1222) and the tail of `_challenge_evidence` (1476, call 1710). Both delete `_quotes_span` (951). 328's lines 3 to 5 touch `tester/base.md` 3, `tester/tests_missing.md`, `_own_assertions` (`api.py` 17447) and the contested block (`runner.py` 764). 333 does not touch them.

Inside group 2, no function has two editors (reasoned: the cited lines). 337 edits `runner.py` 2640 to 2660, `api.py` 11797 to 12880 and `principal.py` 2261 to 2663. 338 edits `scheduler.py` 1949 to 2096 and the split, `sandbox.py` 4486 to 4532. 322 edits `_ruling_texts` (`api.py` 20856) and `runner.py` 4242 to 4571. The members share the record and not the code. So three passes in one row: 337, then 338, then 322.

Across groups, one pass or a fixed order:

| Place | Editors | Order |
|---|---|---|
| `_red_line_refusal`, `sandbox.py` 1178 | 336 (`said`, 1212 to 1213); 333 and 328 (1216, 1222) | 336 first (observed: grep) |
| `_ruling_texts`, `api.py` 20856 | 322 widens the key set; 339's door calls it at 20537, 20585, 21279 | 339 first, its scenes guard 322 (observed: grep) |
| `_arrange_run_refusal`, `api.py` 17649 | 336 item 5 (`_note_collection_error`, 17606); 328 line 4 (`_own_assertions`, 17447) | 336 first, 328 line 4 calls `error_line()` (observed: both called inside 17649) |
| Six-cap refusal `api.py` 6076 to 6081, `_near_twin` tail 6836 to 6855 | 322 item 4 (empty tickets); 333 item 4 (`quotes=`); 329 built the tail | one text pass for both texts (observed: the records' lines) |
| `criterion_repair.md` | 324 line 12; 329 after line 25; 333 line 45 | 329's new sentence offers `msg.challenge_vision_keeper` with no `quotes=`, a new instance of 333's shape. Write it with `quotes=` (reasoned: 329 line 100, 333 line 91) |
| `_call_keeps`, `api.py` 17530 | 335 moves it beside `parse_args`; 328 line 2 compares quotes with its forms | 335 first (reasoned: 335 line 63, 328 line 90) |
| `OWED`, `test_case_reachability.py` 212 | 331 removes it; 332 makes it a map | 331 first, then 332 has nothing to map (observed: grep) |

Two test files have two editors: `test_frame312_stuck_review.py` (339 rewrites 179 to 210, 330 names it as the old answer) and `test_park_page.py` (330 at 696, 336's red test). The tests differ, so the passes run in sprint order (observed: the records).

## 3. The order inside a group

Group 1: 333's proposal is the general one (reasoned: it covers 13 instances, and 328's quote sites are 333's instances 1 to 3, 5 and 6). 328's second Ends-when clause, "a challenge quote must be in the live criterion text", collapses into 333's (observed: stack.md 1401). 328's first clause is built, and its third clause keeps its own count: Developer ticks spent on a test the Tester rewrites, 5 of 5 toward 0. 333's Ends-when has no night clause. It needs one, for example Terminologist challenges the strict door refuses, from review 1's 182 of 206 (reasoned: 333 line 69).

Group 2: 337's proposal is the general one: the value is fixed once at its source, and the `rulings` row holds the exchange (observed: 337 line 90). 338's `ruled_rows` and 322's item reader become readers of that row by key (reasoned). 337's first clause becomes the group's mechanism clause. 338's m50 and m94 and 322's s199 become red tests of the one reader. The night counts stay per frame: 337 naming-door refusals 2 of 2 and wrong approvals 1 toward 0; 338 relays of a ruled row with no acting call, widened to converse replies; 322 criteria a reply calls wrong, 3 of 7 (observed: stack.md 1288, 1278, 1547). 322's refusal tails are not about his ruling and go to the text pass of section 2 (reasoned).

## 4. The sprint

Sprint 26, in order by what stops a night first, with cycles summed from the records:

1. Frame 340, the C76 gates. 2. Not one of the fourteen. Stays.
2. Group 3, frame 339. 2 to 3. Stopped night 169 (observed: stack.md 20). Stays.
3. Group 4, frame 330. 4. Night 169 stalled on `batch_start` (observed: stack.md 36). Stays.
4. Group 5, frame 335. 3. Stopped night 168's three walks, and it comes before group 1 (observed: stack.md 70). Stays.
5. Group 2, frames 337, 338, 322. 5 + 2 + 2 to 3 = 9 to 10. Rows 6 and 7 merge, and parked 322 joins as the third pass, after 339.
6. Group 6, frame 329. 2. Stays, with the sentence in the quote form.
7. Group 7, frame 336. 2. Stays, and it comes before group 1.

Night 170 runs on rows 1 to 7, about 25 cycles against 23 now. Parked for sprint 27, in order: group 8, frame 324, 3 (a wrong surface derails a batch, observed: 324 line 49); group 1, frames 333 and 328, 3 to 4 + 9 = 12 to 13 summed, 9 to 10 with 328's lines 1 and 2 removed; group 9, frame 331, 4; group 10, frame 332, 3; group 11, frame 334, 4. Groups 9 to 11 stop no night, because they are instruments (reasoned).

## 5. The doubt

1. Group 2 rests on the records, not the code. The check: read `_ruling_texts` (`api.py` 20856), `ruled_test_criteria` (`scheduler.py` 2065) and the `rulings.words` write (`api.py` 12880). If the first two key on different things, by ref and by message id, one helper cannot serve both, and group 2 is three groups.
2. 328 has two mechanisms. It sits in group 1 by its largest piece. If its lines 3 to 5 are a frame of their own, the count is 12 (reasoned: 328 lines 34 to 71).
3. The cross-group shape of section 1 is grouped on the summaries. The check: run 334's per-mode render and count which of 329 B3, 333 7 to 12 and 335 I4 to I6 it flags.
4. HEAD moved to 704f104e after the reads at 46e5c88b. Frame 339's pass 1 is built and not yet in this read (observed: `git log`).
