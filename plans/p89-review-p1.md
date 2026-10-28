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

## p2

**Verdict: NOT READY. 2 high, 2 low.** The four findings of p1 are closed. A claim about a description still renders on a request page, against the ruling. His words about the open request land as contests on seat rows of the account page.

The review ran read-only in `C:/Users/roman/rota_r89` at 03876804, on top of 4a21fd42.

### (a) The verdict on each point

1. Findings 1 to 4: CLOSED. Probe p1 now puts the 4 account rows off e_p3's page, and the page numbers 3 lines. Probe p5 keeps all 19 rows of s179 and all 7 claims of s272, with no request row. The raw-id contest is refused with "is no line of this page". The state view line ends at "2 lines approved." with no ask. The recorded m131 contests still land.
2. The seven scenes: 3 hold, 4 name their requests only to pass. The m133 scene and the follow-up scene of frame 193 test what their names say. The bg4 scene still tests the wake, and its scripted call names the request so that the description note keeps a request page. The four m399 scenes no longer test the agenda wake of one constraint row (finding p2-3).
3. Night 136's shape: CONFIRMED. On the account page with no account row, his words about format_filename land as 7 contests on the 7 critic claims. No word reaches the request (finding p2-2).
4. A description item: NOT the request's own. `_is_request_item` excludes a description with the account and observed behaviour, and its rows render under "What the project does today". The ruling names the claims as the account's rows, so a claim about a description belongs off a request page (finding p2-1).
5. The gate: HOLDS. The 6 touched files pass, 130 tests. The 6 known reds fail at 03876804. The diff holds no CR byte, and every hunk is in the claim.

### (b) Findings

1. **`rota/roles/principal.py` 1625 to 1631, `off_page`. High. CONFIRMED.** The new test puts a row off only when its items are a subset of `how_it_works`. Probe p7 put the night's `challenge_items_parses_and_executes_inputs` on e_p3's page. `off_page` returned an empty set, and the page numbered the claim as line 4: "the Critic falsified items:parses_and_executes_inputs".
   Fix: put a row off when every item it reaches has no request by `request_of`, and keep the exception for a note about a delivered item.

2. **`rota/roles/api.py` `rulings_rule`, with `request_rows` 1673 to 1676. High. CONFIRMED.** The account page has no line of the open request, and every line must take a ruling. Probe p6 sent s272's page in a run with no account row and landed his words about format_filename. The door landed 7 contests on the 7 claims, with words that name none of them. A one-line ruling and an empty ruling are refused, so the Liaison has no path for the words to the request. He saw the rows, so law 6 holds by the letter. The contests still change 7 rows he did not speak about. With `how_it_works` present, the same words land on the account line.
   Fix: give the account page a route for words about an open request, such as a converse to that request's thread, and refuse a contest whose words name an open request item and no line of the page.

3. **`tests/rota/test_request_page.py` `M399_CALL` and its four scenes. Low. CONFIRMED by the assertions.** The scripted Liaison call now names both requests, so the scenes pass on a page that the door no longer builds from the wake. `test_every_open_request_has_its_own_line` asserts a page with two requests, "You also asked:", and the constraint row `l_d24f6997d1` as line 9. The run has no request message, so `off_page` drops nothing. The scene keeps green a page of two requests and an account row, which the ruling forbids.
   Fix: keep the old call with the wake row alone, and assert the account page, or record why a run with no request message keeps two requests on one page.

4. **`rota/core/scheduler.py` 1218 to 1221, `tick_agenda`. Low. PLAUSIBLE.** Finding 5 of p1 stays open as the builder's declared debt.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p89/`.

- `p1.py` and `p5.py` again at 03876804 (point 1).
- `t/test_p89_door.py` and `t/test_p89_state.py` again (point 1).
- `p6.py`: deletes `how_it_works`, sends s272's page, lands a reply about format_filename, then tries three rulings (point 3).
- `p7.py`: a claim about the description `parses_and_executes_inputs` on e_p3's page (point 4).
- pytest: the 6 touched files, 130 passed. The 6 known reds, 6 failed.

### (d) Usage

- Input tokens: about 25k. Output tokens: about 6k. Total: about 31k, from the context counter.

## p3

**Verdict: NOT READY. 2 high, 2 low.** The two highs of p2 are closed as written. His words about the open request now land as 7 approvals of the critic claims on the account page. A sign-off submit drops the account item and the descriptions, and no page takes them.

The review ran read-only in `C:/Users/roman/rota_r89` at 65cbda09, on top of 03876804.

### (a) The verdict on each point

1. The two highs of p2: CLOSED. Probe p7 puts `challenge_items_parses_and_executes_inputs` off e_p3's page, and the page numbers 3 lines. Probe p6 gets "The words name no line of this page, so they change no row on it." for the 7 contests.
2. The two risks: both CONFIRMED. The sign-off of m283 sends the version item alone and drops the 4 account rows (finding p3-2). His words about the request do not land nowhere. They land as 7 approvals (finding p3-1). The refusal sentence goes to the Liaison, not to him. The sentence does not say where he can answer, so the cost is not one reply.
3. The scenes: HOLD. The constraint-row scene sends the wake row alone and asserts the account page. The three m399 scenes test what their names say on a page of one request. They keep the constraint row on that page only because the run has no request message. The m283 scene name claims more than it tests (finding p3-3).
4. The gate: HOLDS. The 6 touched files pass, 132 tests. The 6 known reds fail at 65cbda09. The diff holds no CR byte, and every hunk is in the claim.

### (b) Findings

1. **`rota/roles/api.py` 14121 to 14130, `rulings_rule` with `_account_page_refusal`. High. CONFIRMED.** The refusal covers a contest only. Every line must take a ruling, and "a line the reply does not contest is approve". Probe p6 then sent 7 approves with his words about format_filename. The door landed 7 approves on the 7 claims, and it did the same with empty `words`. His words approved rows they never named. Law 6 says that nothing is ruled on his behalf. The refusal pushes the Liaison to the one call that lands.
   Fix: on the account page, when his words name no line, refuse an approve as well as a contest. Give the Liaison one call that keeps the page open and asks him which page his words are for.

2. **`rota/core/sandbox.py` 4288, the send door, with `off_page`. High. CONFIRMED for the drop, PLAUSIBLE for the loop.** Probe `t/test_p89_m283.py` replayed the m283 submit through the send door. The page kept `version_option_show_python` only. The door dropped `how_it_works`, 3 descriptions and 2 items of other requests. Nothing sends the account rows on their own page, and `tick_agenda` reads ledger rows, not draft items. So the account items stay at draft, and each sign-off can submit them again, as on night 133.
   Fix: when the send door drops rows of no request from a sign-off, queue them as the account's page, or refuse the present and name the dropped rows.

3. **`tests/rota/test_frame193_pass2.py` 516, `test_m283_puts_the_account_item_on_the_accounts_page`. Low. CONFIRMED by the assertions.** The scene asserts that the description is off the request page and the version item stays. It never asserts that the description reaches an account page. Finding p3-2 shows that it does not.
   Fix: assert the account page that the dropped rows reach, or rename the scene to what it tests.

4. **`rota/core/scheduler.py` 1218 to 1221, `tick_agenda`. Low. PLAUSIBLE.** Finding 5 of p1 stays open as the builder's declared debt.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p89/`.

- `p6.py`: now also tries 7 approves with his words and with no words (point 2, finding p3-1).
- `p7.py`: again at 65cbda09 (point 1).
- `t/test_p89_m283.py`: the m283 submit through the send door, with base temp `bt/` (point 2, finding p3-2).
- pytest: the 6 touched files, 132 passed. The 6 known reds, 6 failed.

### (d) Usage

- Input tokens: about 20k. Output tokens: about 5k. Total: about 25k, from the context counter.

## p4

**Verdict: READY. 0 high, 2 low.** The two highs of p3 and its m283 low are closed. His first answer that names no line is not lost. The Liaison retries the reply once, and the sign reaches him one session later.

The review ran read-only in `C:/Users/roman/rota_r89` at 0d0bc33d. The merge 34b6331a of w7root sits on 65cbda09.

### (a) The verdict on each point

1. Probe p6: CLOSED. His words about format_filename change 0 rows. The 7 contests and the 7 approves are refused, with his words and with empty `words`. The refusal is "The words name no line of this page, so they change no row on it."
2. The first failed session: NOT SILENT, and not a loss. On the first miss, `session_commit` keeps the reply open and puts the note in the next wake of the Liaison, by frame 267. His answer waits as any reply in flight waits. On the second miss, the account page goes back to him with its reason, and his next request page opens with `ACCOUNT_UNNAMED`. The cost is one more Liaison session, not one more reply of his. One case shows the sentence late (finding p4-1).
3. Probe `t/test_p89_m283.py`: CLOSED. The sign-off sends two presents. The first holds `how_it_works`, `defines_commands_and_options`, `parses_and_executes_inputs` and `provides_command_line_interface`. The second holds `version_option_show_python`.
4. The m192 scene: the ruling's shape. The account rows go on their own page, and the call's page keeps every old assertion. The pattern `*account, sent` also accepts zero account pages, so the scene does not pin that the account page exists (finding p4-2).
5. The gate: HOLDS. 8 files, the touched ones and the merged w7 files, pass with 182 tests. The 6 known reds fail at 0d0bc33d. The diff of 0d0bc33d holds no CR byte. Every hunk of 0d0bc33d is in the claim.

### (b) Findings

1. **`rota/roles/principal.py` 2311 to 2345, `account_unnamed_line`. Low. PLAUSIBLE.** The sentence goes only on a request page with a `seq` after the account page. A `tick:agenda` account page can come after the open request page. Then no request page qualifies until a new one is sent. He sees the returned account page with its reason line, and his words about the request stay with no route.
   Fix: put the sentence on the open request page of the run, whatever its `seq`.

2. **`tests/rota/test_frame193_pass2.py`, the m192 scene. Low. CONFIRMED by the pattern.** `*account, sent` passes when the door sends no account page. The loop over `account` then checks nothing.
   Fix: assert the count of account pages that the m192 refs give.

3. Finding 5 of p1, `tick_agenda`, stays open as the declared debt.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p89/`.

- `p6.py`: again at 0d0bc33d, 5 rulings, all refused (point 1).
- `t/test_p89_m283.py`: now prints every outbound page (point 3).
- Read: `rota/core/db.py` 1808 to 1855, the first and the second miss of frame 267, and `account_unnamed_line` (point 2).
- pytest: 8 files, 182 passed. The 6 known reds, 6 failed.

### (d) Usage

- Input tokens: about 16k. Output tokens: about 4k. Total: about 20k, from the context counter.
