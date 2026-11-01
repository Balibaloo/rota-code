# Review p2 of frame 357: 351f63c8, the item drop

Verdict: not accepted as it stands. The drop on m122 lines 1 and 3 works on the dry1 rows. Two highs leak past the request line and past the end of the request. Both fixes are small. 2 high, 3 low.

Worktree `C:/Users/roman/rota_f354r` at 351f63c8 (the `fix(roles)` commit, the cherry-pick of 37ef5980). `rota.__file__` resolved to the worktree. Copy of dry1 after turn 13: `scratchpad/dry1w7/dry1.db`, never written. Each probe wrote a fresh copy under `scratchpad/rv/`.

Highs:

1. `_item_drops` ends any item that a ruling contests with the act `drop`, not only a request item. A drop on the description `how_it_works` now lands `dropped` (CONFIRMED, probe 2).
2. `_request_finished` and `resume_behind` read the park drops of `scheduler.dropped_items`, not the approval `dropped`. A request whose items are all dropped never finishes (CONFIRMED, probe 3).

Lows:

3. The open clarifies m108, m112 and m114 about the dropped items stay on the agenda (CONFIRMED, probe 1).
4. A contest by the seat itself, through `rota sign --contest` or the TUI, has no drop and still wakes the defend of the Vision Keeper (CONFIRMED by code read).
5. `problem.describe` has no `_refuse_dropped` and stages the approval `draft`, so it can revive a dropped item (PLAUSIBLE).

## (a) The points

1. Holds. On a copy, a Liaison ruling r_rv on m122 with lines 1 and 3 `contest`/`drop` landed as m123. Both items read `dropped`. Line 1 keeps its text and version 2. `contested` returns `[]`. `off_page` on the refs of m122 gives all four item and guess rows, for present and for confirm. The verdict m123 carries `[]` and lands `answered`. The `agenda` predicate returns no wake, and `request_shift` returns none. `pending_asks`, the builder of `rota agenda`, shows no new page about the items. It still shows the three old clarifies (finding 3).
2. Holds in part. Each reader on the dry1 rows:
   - The status line and `_render_state` count `approved` items only (`principal.py:347`). A dropped item shows nowhere. No effect on dry1.
   - `account_rows` keeps a row with no owner. Both dropped items have a request owner (s2, s3), so neither is an account row. A dropped `how_it_works` has no owner and is not approved, so it becomes an account row and the head of `account_page_refs` (finding 1).
   - The slicing (`scheduler.py:401`) and `grouping` (`predicates.py:635`) read `approved` only. `cancel` and `reopen` read any approval other than `approved`, so a live batch of a dropped item is cancelled and also wakes an election. Neither dropped item has a batch on dry1.
   - `decisions.author` changes no item. Nothing wakes the Vision Keeper on a dropped item after the land. No effect on dry1.
   - The amend route: `problem.assert` and `problem.set_approval` refuse a dropped item. `problem.describe` does not (finding 5).
   - Outside the list: `_request_finished` and `resume_behind` (finding 2), and `report_is_settled` (`scheduler.py:167`), which reads a report that names a dropped item as never settled.
3. Holds. The commit changes no prompt file. The only text in the landing wake that moves is the request entry of `_MENU_BASE`, which `page_menus` renders on every page with a request line. The refusal text also builds from `_MENU_BASE`. `line_menu` picks the menu by the kind of the row, not the kind of the page. So `drop` now shows on a request line of a present, a confirm, a clarify and a park page, for example `m_park_421158fa15_bg_1` line 1. A shift page lands through `_land_shift` first (`principal.py:3409`), so a drop there keeps its park meaning. The door checks that the option is on the menu of the line. I found no check that the words of the principal hold "drop". So a Liaison can rule `drop` where he wrote contest or later (PLAUSIBLE, no model run).
4. Both opens are real.
   - Open notes: m108, m112 and m114 stay `open` in `pending_asks`. Each asks him about an item he dropped. Cost on dry1: three pages to read or answer on turn 14. An answer lands with no harm, because the write guard keeps `dropped`. Fix: in `land`, close each open ask to the principal whose item refs are all dropped. m114 also names `write_tests_again_rebuttal`, so the rule needs a decision about decision refs. Price: 0.5 to 1 cycle with a test.
   - The contest by the seat itself: `_item_drops` returns nothing with no ruling id. That contest lands `contested`, and the Vision Keeper defends. Cost on dry1: none so far, because the seat answers through the Liaison. Fix: a drop keypress on `rota sign` and the TUI that writes a ruling row with the act `drop`. Price: 1 cycle.
5. Holds. The line pinned the request menu that e810eb77 (2026-10-29) wrote. Its message gives no reason for a request menu without `drop`. `rota/DECISIONS.md` has no line with "menu". No line with "drop" is about an item or a request menu. The change departs from no ruling.

## (b) Findings

1. `rota/roles/principal.py:3846-3860`, `_item_drops`. High. CONFIRMED: probe 2 ruled `contest`/`drop` on `how_it_works` (menu kind `other`), and the item read `dropped` with `is_description = 1`. Before the commit, the same ruling landed `contested`. The `other` menu offers `drop` since e810eb77, so the change reaches every description and every out-of-scope item. Nothing writes an item back from `dropped`. Fix: keep only the refs where `_is_request_item(conn, ref)` is true. Price: 0.25 cycle with one test.
2. `rota/core/predicates.py:201-211` and `rota/core/scheduler.py:2635`. High. CONFIRMED: probe 3 read the current request `e_m70` (s2, s3) after the drop, and `_request_finished` returned False. Its only items are the two dropped ones. An item parked behind such a request never resumes, and `request_shift` does not stop early at a finished request. On dry1 no `park` row waits behind e_m70 now, so no effect yet. Fix: let `scheduler.dropped_items` also return the items with the approval `dropped`. Price: 0.25 cycle with one test.
3. `rota/roles/principal.py`, `land`. Low. CONFIRMED: probe 1 printed m108, m112 and m114 in `pending_asks` after the land. Fix: point 4, first open. Price: 0.5 to 1 cycle.
4. `rota/roles/principal.py:3850-3853`. Low. CONFIRMED by code read: no ruling id gives no drop. Fix: point 4, second open. Price: 1 cycle.
5. `rota/roles/api.py:2463`, `problem_describe`. Low. PLAUSIBLE: the door stages the approval `draft` with no check for `dropped`, and the write has no guard. Its check on `decided` provenance may refuse the dry1 items first. Fix: call `_refuse_dropped` at the top of the door. Price: 0.1 cycle.

## (c) Probes

1. `scratchpad/rv/p2rev_land.py` on `scratchpad/rv/p2rev.db`, a copy of dry1w7. It ran `init_db`, added a reply m_rv to m122 and a ruling r_rv with `contest`/`drop` on lines 1 and 3, then ran `apply_rulings`. It printed the items, the verdict, `contested`, `off_page`, `open_requests`, `agenda`, `request_shift`, `pending_asks` and `_render_state`.
2. `scratchpad/rv/p2rev_hiw.py` on `scratchpad/rv/p2rev_hiw.db`, a second copy. It added a present page with `how_it_works`, a reply, and a ruling `contest`/`drop` on line 1, then ran `apply_rulings`. It printed the menu kind `other` and the approval `dropped`.
3. Inline `python -c` calls on `p2rev.db`, opened read only. One ran `_request_finished` on the current request and printed the entry e_m70, the statements s2 and s3, and False. One rendered m108 and m114 and printed the `line_menu` of `write_tests_again`.
4. Reads: the commit diff, the message of e810eb77, and a grep of `rota/DECISIONS.md` for "menu" and "drop".

No test run, no gate, no model, no rota.

## (d) Usage

Opus. Input about 80k, output about 12k, total about 92k, against a cap of 25k. The agent cannot read exact counts.
