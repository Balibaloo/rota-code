# Review of P8 and P9, pass 1: 8237d93c and 4a21fd42 on w89root

**Verdict: NOT READY. 2 high, 3 low.** A row that reaches the account item still renders on a request page, against the ruling of 2026-10-28 09:10. A run with no `how_it_works` row drops the account rows at the send door, and they never reach him while a request item is open.

The review ran read-only in `C:/Users/roman/rota_r89` at 4a21fd42. Every register probe ran on a copy of `.rota/clickI_night172.db` in the scratchpad, with its deliveries undone.

## (a) The verdict on each point

1. The ruling: FAILS. A claim, a ledger note, a glossary term and a constraint that reach `how_it_works` render as lines 4 to 7 of an open request's page (finding 1).
2. The night 172 pages: HOLDS. m17, m47 and m80 carry no reading of another request. m62 keeps `reading:m48` and drops `reading:m55`. The replays of s179 and s272 give the account page with no request line.
3. The delivered read-back: HOLDS, with one low. `render_state` feeds `rota agenda` only, so he reads it at will and owes no answer. The line still says "Say ok, or say what we misread." and no page can take that answer (finding 4).
4. The door deviation: HOLDS for m131, with one low. "Drop lines 9 to 15" lands as 7 contests on the 7 claims he saw. A contest keyed by the raw id lands on an off claim that today's render never numbered (finding 3).
5. Night 136's shape: does not return, but the cost is high. In a run with no `how_it_works`, the send door drops all 19 and all 7 account rows, and the page is the open request's page (finding 2).
6. The account's page: `tick:agenda` and `tick:observed_entries` send it while a request is open, after the open page closes. With no account row, those rows reach him never while a request item is open (finding 2).
7. The test files: HOLD. Each changed assertion still tests what its name says. The m212 scene's "no stamped request" half now holds with no stamp at all, so only the other stamp tests cover the stamp guard. No test covers a row that reaches `how_it_works` on a request page.
8. Stale cases: NONE by text. No recorded prompt in `D:/repos/rota/tests/rota/cassettes.db` holds a reading line, the account heading or a glossary heading. The 244 qwen3:8b Liaison prompts with "You asked:" hold none of them. The gate in the worktree could not count stale cases, because `paths.DEV_DB` resolves to the worktree and the file is absent there.
9. The gate: HOLDS. The 5 touched and door files pass, 105 tests. The 6 known reds fail at 4a21fd42. The diff holds no CR byte. Every hunk is in the claim, and the door hunk is the declared deviation 5.

## (b) Findings

1. **`rota/roles/principal.py` 1617 to 1628, `off_page`. High. CONFIRMED.** A row whose items are all of no request stays on a request page. The `others` test keeps a row when `requests_of` holds a None. Probe p1 put `challenge_items_how_it_works`, the night's open note `l_e7c6ed5501`, the term `command` and the constraint `argument` on the page of e_p3. `off_page` returned an empty set. The page numbered them as lines 4 to 7 under "Where you did not say, I assumed:", and the footer says "'ok' approves all of this". A note or a claim about a description item takes the same path. In the live schema a glossary term or a constraint reaches an item only through a statement ref, so the claim and the note are the live shape.
   Fix: in `off_page`, before the `others` test, put a row off when `req` is set and the requests of the row, less None, are empty. In `rulings_rule`, refuse only when the row reaches an item of a request, so the message never names `how_it_works` as "your earlier request".

2. **`rota/roles/principal.py` 1665 to 1676, `request_rows`, with `rota/core/sandbox.py` 4258 and 4288. High. CONFIRMED for the drop, PLAUSIBLE for the repeat.** With no `how_it_works` row, `request_rows` adds the open request. `off_page` then owns the page by that request and drops every row of no item. Probe p5 deleted the account item and replayed s179 and s272. The sent refs kept none of the 19 rows and none of the 7 claims. The page was the request page of e_p3 with its 3 readings. The rows stay open and unshown, so the next `tick:agenda` offers them again after his answer. Each round then sends him the request's page again. The builder's open question 4 names the same loop.
   Fix: refuse the present at the send door when `off_page` drops every row the Liaison named, and say why, so no row leaves the page in silence.

3. **`rota/roles/api.py` 13680 to 13690, `rulings_rule`. Low. CONFIRMED.** The door now lets words land on any off row of no item, seen or not. A key that equals a raw ref passes through `keys`, the page refs, and not through the order he saw. Probe `test_p89_door.py::test_unseen_id_key` removed the recorded order of m131, so the door read today's render of m130. That render numbers none of the 7 claims. A contest keyed `challenge_constraints_sentinel` landed with `line` None and his words of m131. Law 6 asks that a ruling land only on a row he saw. The window is a reply with no recorded order, or a page in flight across the land of P9.
   Fix: refuse words on an off row when the row is not in `order`, the rows he saw, in place of the test on `items`.

4. **`rota/roles/principal.py` 366 to 373, `render_state`. Low. CONFIRMED.** The state view prints the page's line with its tail "Say ok, or say what we misread." No ask carries the line, and no answer of his can land on it. The reading stays owed for the rest of the run, so the line prints on every `rota agenda`. Probe `test_p89_state.py` printed the same text on two reads and found no pending ask.
   Fix: print the reading without the "Say ok" tail on the state view, or name the page that takes a correction.

5. **Outside the points. `rota/core/scheduler.py` 1218 to 1221, `tick_agenda`. Low. PLAUSIBLE.** The tick still puts "a row of no item and no batch" on the page of a request item, so "it rides on this page and is not lost". The `off_page` of P9 now drops that row at the send door. The row waits until no request item has an open ledger row. The comment and the rule disagree, and a page can go out without the rows the wake named.
   Fix: in `tick_agenda`, keep rows of no item out of the wake of an item, and give them their own wake when the item rows are done.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p89/`. Each register probe copies `n172.db` first.

- `p1.py`: adds a claim on `items:how_it_works` and two statement refs from `how_it_works`, then renders the present of e_p3 (point 1, finding 1).
- `p2.py`: renders m62, m47, m80, m71, m130 and m17 from their stored refs, m17 with its s1 refs removed (point 2).
- `p3.py`: removes the later ruling of `reading:m48` and renders m62, then replays s179 and s272 through the send door (point 2).
- `p5.py`: deletes `how_it_works` and replays s179 and s272 (points 5 and 6, finding 2).
- `t/test_p89_state.py`: the seeded run of P8, delivered, then `render_state` twice and the pending asks (point 3, finding 4).
- `t/test_p89_door.py`: "Drop lines 9 to 15" of m131 on the recorded order, and a raw-id contest with no recorded order (point 4, finding 3).
- `q8b.py`: scans a copy of `cassettes.db` for reading lines and account headings on request pages (point 8).
- pytest at 4a21fd42: `test_p8_page_readings.py`, `test_p9_account_rows.py`, `test_f15_request_of.py`, `test_request_page.py` and `test_f2_rulings_words.py`, 105 passed. The 6 known reds, 6 failed.

## (d) Usage

- Input tokens: about 92k. Output tokens: about 20k. Total: about 112k. The harness gives no exact split, so these come from the context counter. The total is over the 70k cap, because the report write failed four times in the shell and the probes needed reruns.
