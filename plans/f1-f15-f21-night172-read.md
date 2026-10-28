# Night 172's page walls W7, W8, W9 and W12, the read by rule C76

Meta workflow, read on 2026-10-28. Read only, at head 2b1ef4c9 on `rota/foundation`. `rota/roles/principal.py` is the same at de1203a9 and at head (observed: `git diff --stat de1203a9 HEAD`). Line numbers are at head. Sources: `.rota/clickI_night17{0,1,2}.db` opened `?mode=ro`, the three principal jsonl files filtered by `night`, `plans/night172-read.md` section 2, `plans/facts-2026-10-27.md`, the two audit halves, `plans/f1-review-p1.md`, `plans/f15-review-p1.md`, `plans/f20-review-p1.md`, frame 344's status lines, `plans/rulings-seam-design-2026-10-26.md`, `plans/frame190-design.md` 2.1 and `plans/wall-guide.md` causes 11 and 12. The probes are `w9probe.py`, `w12probe.py` and `reach_count.py` in session 77c8dc39's scratchpad. They import the head code and read the night databases. No code was edited and nothing was committed.

**The result. In each wall the fact's one reader stood and gave the answer that its own rule gives. The wrong line comes from a reader beside it or from a row kind that the one reader does not walk.**

- W7: `reading_line` reads its rows through `ruled` (F1), and the rows are right. The quote reads `messages.body_text`. A clarify answer lands on the verdict path of `land`, and that path writes no `body_text`. His words are in `entries` `e_<message>` (observed).
- W8: `request_of` (F15) gives None for every `reading:` ref, because `row_items` does not walk a reading. Also no page filter reads the readings. `readings_owed` has no request, and the send door adds every owed reading to every present and confirm page (observed).
- W9: `request_of` gives None for glossary terms, constraints and a ledger row about a constraint. `off_page` keeps a row that reaches no item. `request_rows` adds the open request to a page whose rows reach no item, by frame 190's design 2.1 (observed).
- W12: `_tick_words` (F21) gives the kind's words, "the tests still fail". No reader on the stopped page names the red test. `park_reds` already finds it and the stopped page does not call it (observed).

**The biggest by his answers spent is W7: 5 of his 25 answers on night 172 contest an empty quote, and the same shape shows on 9 pages over nights 170 to 172.** W9 is the biggest by lines, 26. W7 is also the cheapest fix, about 2 cycles.

## 1. The find

### W7. A page reads back an empty answer

| Page | Wrong line, verbatim | Reply read back | Ruling whose rows the line reads | Ruling with no reply | His contest |
|---|---|---|---|---|---|
| m33 | `10. Your answer "", as the team read it: 6 lines approved. Say ok, or say what we misread.` | m31, verb `converse`, `body_text` NULL | r_m31_2, reply m31, 6 `reading` rows, all approve | r_m31, `reply_id` None, verdict_id m31, `per_item` {} | m34: "line 10 is wrong because I gave no empty answer and approved no lines" |
| m47 | `3. Your answer "", as the team read it: a row is wrong; a row is wrong; a row is wrong; a row is wrong; a row is wrong. Say ok, or say what we misread.` | m44, NULL body | r_m44_2, 5 contest rows with no line | r_m44 | m48: "The second and third items quote answers I never gave" |
| m62 | `5. Your answer "", as the team read it: 3 lines approved. Say ok, or say what we misread.` | m55, NULL body | r_m55_2 | r_m55 | m63: "Line 5 is wrong because I never gave an empty answer, so please drop it" |
| m71 | `26. Your answer "", as the team read it: 2 lines approved. Say ok, or say what we misread.` | m68, NULL body | r_m68_2 | r_m68 | m72: "line 26 quotes an empty answer I never gave, so drop it" |
| m120 | `12. Your answer "", as the team read it: 1 line approved. Say ok, or say what we misread.` | m118, NULL body | r_m118_2 | r_m118 | m121: "Line 12 is wrong, because my last answer was not empty" |

(observed: the jsonl pages and words; `messages`; `rulings`; `ruled_refs`; `reading_line` run on the night 172 register gives the same five lines.)

His words of each reply are in the record. `entries` holds `e_m31`, `e_m44`, `e_m55`, `e_m68` and `e_m118` with his whole text, and `rulings.words` of both rulings holds it too, 185 to 290 characters (observed). The function that printed "Your answer" is `reading_line`, principal.py 1194 to 1223.

The brief names the five rulings with no reply as the source rows. The read does not support that (observed). The line reads the rows of the `_2` ruling, which has the reply. The ruling with no reply has no `ruled_refs` rows. `ruled(reply=...)` takes the newest ruling with `reply_id` or `verdict_id` equal to the reply, and that is the `_2` ruling (observed: principal.py 944 to 946). The rulings with no reply are a sign of the same path, not the cause. A clarify answer lands as `converse` with no `per_item`, and `land` writes `r_<message>` through `_insert_keypress_ruling` (observed: principal.py 3151, 3191 to 3206). The shape is older than F1: the jsonl of 2026-10-08 holds `r_m301` with `reply_id` null and `per_item` {} (observed).

A second fault sits on m47 line 3: "a row is wrong" five times. The reading rows of a clarify answer have no `line`, so the clause falls back to "a row" (observed: principal.py 1214).

### W8. A confirm page of a new request reads back an earlier request's answer

| Page | Verb, page request | Wrong line, verbatim | Reading ref | The reply's request | His words |
|---|---|---|---|---|---|
| m17 | confirm, e_p1 | `2. Your answer "That was my own question to you, so ...", as the team read it: line 3 is wrong; line 4 is wrong; 2 lines approved.` | reading:m14 | onboarding, no request: m14 answers m11 and m13 | m18: "this is the first page you sent me. Please drop item 2" |
| m47 | confirm, e_p2 | `2. Your answer "Lines 3 and 4 are wrong because the ...", as the team read it: line 2 is wrong; line 3 is wrong; line 4 is wrong; line 6 is wrong; line 7 is wrong; 3 lines approved.` | reading:m34 | e_p1, walk 1 | m48: "The second and third items quote answers I never gave" |
| m47 | confirm, e_p2 | line 3, the W7 line above | reading:m44 | e_p1, walk 1 | the same |
| m80 | confirm, e_p3 | `2. Your answer "Lines 1 to 4 are right, and line ...", as the team read it: line 5 is wrong: keep; 4 lines approved.` | reading:m77 | e_p2, walk 2 | m81: "I never gave an answer about lines 1 to 5, so please drop it" |
| m62 | present, e_p2 | line 5, the W7 line above | reading:m55 | the account: m55 answers the glossary clarify m54 | contested as empty, W7 |

(observed: `messages.body_refs`; the request of a reading is `request_of` over the refs of `read_back_rows`, computed by `reach_count.py` on the end state of the register.)

So 4 lines on 3 confirm pages, as the night read says, and 1 more on the present m62 (observed).

### W9. Rows from other work reach a request's page

| Page | Lines | Refs | Table | Owner | Who sent them |
|---|---|---|---|---|---|
| m71, e_p2 | 6 to 10 | `context#root`, `decorator#src_click`, `group`, `group#root`, `parameter` | `glossary_terms` | the account, no item | Liaison s179, wake `tick:observed_entries`, `msg.present_principal(refs=` the 19 refs `)` |
| m71, e_p2 | 11 to 24 | `flag_needs_value`, `get_best_encoding`, `get_current_context`, `helpformatter`, `is_ascii_encoding`, `make_text_stream`, `parametersource`, `pop_context`, `push_context`, `resolve_color_default`, `sentinel`, `t_unset`, `unset`, `t_flag_needs_value` | `constraints` | the account, no item | the same |
| m130, e_p3, twice | 9 to 15 | `challenge_constraints_flag_needs_value`, `_get_best_encoding`, `_get_current_context`, `_make_text_stream`, `_sentinel`, `_t_unset`, `_unset` | `ledger`, author critic, `about_ref` `constraints:<name>` | the account, no item; written by the walk 2 Critics s148 to s160 | Liaison s272, wake `tick:agenda`, the 7 refs only |

(observed: `turns` of s179 and s272; `sessions.wake_kind`; a table lookup per ref; `w9probe.py`.)

m71 line 6 reads verbatim "context: Holds execution state like the current command chain." m71 line 11 reads "The `FLAG_NEEDS_VALUE` sentinel is used to indicate an option was passed as a flag without a value but is not a flag option. Any code that uses `FLAG_NEEDS_VALUE` ... would break." m130 line 9 opens "the Critic falsified constraints:flag_needs_value against src/click/_utils.py" and ends "The claim stands in the record until ruled." (observed: the jsonl pages). Neither Liaison named a request row. The send door added lines 1 to 5 of m71 and lines 1 to 8 of m130 (observed: the calls against `body_refs`).

### W12. The page says the tests fail, and every check line says "Passes"

| Page | Tick keys at the send | Sentence | Check lines | Red test |
|---|---|---|---|---|
| m120 | `developer\|tick:tests_failing\|bg_3`, attempts 3 | "The team gave up: the tests still fail after 3 attempts." | lines 3, 5, 7: each "... expects result == "c.txt". Passes." | `inh_137414af`, `tests/test_types.py`, criterion none, at 128bec7e: "FAILED tests/test_types.py::test_file_error_surrogates - AssertionError ... 4 failed, 39 passed, 2 skipped" |
| m127, twice | the key above and `developer\|tick:touch_mistaken\|bg_3`, attempts 3 | "The team gave up: the tests still fail after 3 attempts; the team could not finish a step after 3 attempts." | the same three | the same |

(observed: `door_rows(m, "stalled")`, `tick_attempts`, `park_reds(conn, "bg_3")` by `w12probe.py`; the jsonl pages.) `touch_mistaken` has no entry in `TICK_WORDS`, so m127 shows the fallback words (observed: principal.py 1882 to 1908).

His three answers to these pages asked to put the removed code back (m121, m128, m129). None of them named the sentence or a test (observed). So W12 cost him no clause of his own, and its cost is what the page did not tell him (reasoned).

## 2. The mechanism

### W7: the quote reads by its own rule

`reading_line`, principal.py 1194 to 1223, reads the rows through the one reader, then reads the quote from the message:

```python
    rows = read_back_rows(conn, reply)
    ...
    said = conn.execute("SELECT body_text FROM messages WHERE id = ?",
                        (reply,)).fetchone()
    words = ((said["body_text"] if said else "") or "").split()
```

`read_back_rows` (1182) calls `ruled(conn, reply=reply, every=True)` and keeps `reading` and `backfill` rows. For m31 it returns the 6 approve rows of r_m31_2, which are right (observed). The defect is the quote. `parse_reply` gives `Answer(verb="converse")` to a clarify, because `words_keep_open` is false for a clarify (principal.py 145 to 163). `land` writes `body_text` only on its `reply` branch (2760 to 2781). Its verdict branch inserts the message with no `body_text` column (3107 to 3112):

```python
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq, status) "
```

The same branch writes his words to `config` `entry:<message>` and to `entries` through `record_entry` (3121 to 3126). `record_entry` calls the transcript "the one un-interpreted thing in the system" (3416). So two records hold his words, and the quote reads the one that the verdict path leaves empty (reasoned: wall-guide cause 12). F1's `ruled` is not at fault. F1's fact is "his verdict and his words on one ref", and the quote is his words of one reply, read beside it.

### W8: no reader gives a reading an owner

- `readings_owed`, principal.py 1154 to 1179, lists every owed `reading:` ref of the run, oldest first, with no request (observed).
- The send door adds them all to every present and confirm page, sandbox.py 4749 to 4754: `refs += [r for r in readings_owed(ctx.conn) if r not in refs]` (observed).
- `_page_body` splits the readings off before the request filter, 2319 to 2326, and the filter runs on a present only: `if verb == "present": off = off_page(conn, refs)` (observed). The send door's `off_page` call sits inside `if verb == "present"`, sandbox.py 4250 and 4288 (observed). So a confirm page runs no request filter at all.
- The render keeps a reading when it is still owed, 2558 to 2562. Ownership is not read (observed).

The one reader stands. `request_of("reading:m34")` gives None, because `row_items` gives [] for a reading ref (observed: `w9probe.py`, all 5 reading refs). The right answer is e_p1, the request of the rows that the reading reads back (reasoned). So the one reader answers "no owner" for a row kind it does not walk, and no caller asks it about a reading anyway.

### W9: a row of no item stays, and the door adds the request

- `row_items`, principal.py 1285 to 1303, walks an item, a criterion, a ticket, a batch, a test and a ledger row. It gives [] for a glossary term, a constraint, and a ledger row whose `about_ref` is a constraint (observed: `w9probe.py`, 26 of 26 refs). So `request_of` gives None.
- `off_page` keeps the row, 1484 to 1487: `items = row_items(conn, ref) or []` then `if not items: continue` (observed). Its docstring says "A row that reaches an item of no request, the account included, stays".
- `request_rows`, 1531 to 1535, adds the open request when the refs reach no item: `items = [i for i in open_requests(conn) if i not in aside]` (observed). The send door adds those rows to every present, sandbox.py 4258 to 4260.

That is frame 190's design 2.1, "when the refs reach no item: the open requests" (observed: `plans/frame190-design.md` 2.1). Its reason was night 136, where 49 agenda pages had no request line and his words had no row (observed: principal.py 1513 to 1517). So the page of s179 and s272 became a request page with the account's rows under "The team's notes" (reasoned).

### W12: the words reader gives the kind, and nobody names the test

- The stopped page, principal.py 2463 to 2473: "The team stopped work on this change." then `out.append(f"The team gave up: {_stalled_words(conn, keys)}.")` (observed).
- `_stalled_words` (1813) joins `_tick_words(kind)` and the attempts. `_tick_words` (1905) gives `TICK_WORDS["tests_failing"]`, "the tests still fail" (observed). So the sentence goes through the one reader, and the reader gives what it is built to give, the kind.
- The check lines come from `check_line` (528 to 568) on the criterion tests, and each reads "Passes" (observed). The red test has no criterion, so `request_block` gives it no line (observed: night172-read.md W12; `park_reds` own list empty).
- `park_reds`, scheduler.py 1843 to 1859, splits a batch's reds into own and project. It gives `tests/test_types.py` for bg_3 (observed). The park page names project reds, "It breaks checks the project had before: <files>", principal.py 1940 to 1945, and so does `render_state` at 416 to 419 (observed). Both run only on a parked batch. bg_3 stayed `running`, so the stopped page ran (observed).

## 3. The builds and their reviews

| Fact | What the build changed | Did the review name this gap |
|---|---|---|
| F1, landed at 475e083b (passes 1 to 1d) | The keypress verdict moved from `config` `verdict:` to `ruled_refs` rows with source `keypress` and `landed`; `verdict_for`, `chain_verdict`, `last_ruling_on` read `ruled`; `read_back_rows` keeps reading rows only; `land` writes `r_<message>` when no open ruling is on the ask (observed: frame 344, 00:16 to 01:48) | No. Finding 2 is the nearest: "`read_back_rows`. HIGH. ... On the open-row path, the keypress row is the newest row of the ruling, so `one_row_per_ref` returns it in place of the reading row." It is about the rows. No line names the quote, `body_text`, or a converse reply with no body (observed: the review, read whole) |
| F15, landed at 38a44c39 (passes 1, 1b) | `request_of` over `requests_of` became the one reader; `off_page`, `page_request`, `request_rows`, `land`, `ledger_items` and three more read it; a description owns no request; `row_items` walks a test to its criterion (observed: frame 344, 02:19 to 02:48) | No. Point 1: "PARTIAL for a page ref. Night 161's s1 reaches `echo_json` and the account, and `request_of` gives None." Finding 1 is about a note on a test. No line names a `reading:` ref, `readings_owed`, a confirm page, or a row of no item (observed: the review, read whole) |
| F21, with F20 at ba128953, landed at 82d426c4 | `key_parts` and `quarantined_keys` as one parse and one reader; the page and `code_gaps` read `TICK_WORDS` through `_gave_up_words`; the fallback became "the team could not finish a step" (observed: the commit message; the F20 review finding 2) | No. Point 5: "Partly. The five new entries are plain words. Kinds with no entry fall back to a phrase with no verb". No line names a red test with no criterion, or a sentence that names no test (observed: `plans/f20-review-p1.md`) |

The audits set the scope of each build. F15's proposal reads "One reader `request_of` over the ledger, criteria, tests, notes and page rows" (observed: audit a, F15). A read-back ref is a page row, and the build did not walk it (reasoned). F21's proposal moved 2 readers onto `_tick_words` (observed: audit b, F21). The words of a key were the fact, not the object of the words (reasoned). Night 171's read placed the same W8 sign under F15: "m65's read-back of m47 reached walk 2" (observed: `plans/night171-read.md` 160).

## 4. The reach

### W7: every reader of his reply's words that reads `messages.body_text`

1. principal.py 1204, `reading_line`, his page. The wall.
2. api.py 11755, `_his_reply`, a door's read of the waking message.
3. api.py 11763, `_faulted_by_his_words`.
4. api.py 13576, `rulings_rule`, "A call with no `words` rests on his reply".
5. api.py 13817, the span of an act.
6. principal.py 2099, the returned-page note's reply.
7. api.py 13195 and 13229, his earlier answers to a page, `body_text IS NOT NULL`, so a verdict-path answer is skipped.
8. runner.py 2499, the earlier exchange of a clarify thread, `body_text IS NOT NULL`.
9. sandbox.py 3738, the quote check of a clarify, `body_text IS NOT NULL`, with `entries` beside it.

(observed: `git grep "SELECT body_text FROM messages"` and `body_text IS NOT NULL`.) So 9 sites in 4 files read the record that the verdict path leaves empty. One renders to his page. The others are door or wake reads (observed). The empty-words refusals of W6 are not this gap: s119, s187, s271, s274 and s275 woke on replies that hold a body (observed: `sessions.trigger_msg`). Two sites read `messages.body_text` of a seat's message, sandbox.py 2569 and principal.py 2711, and they are not in the count (observed). Readers that read `entries` already: sandbox.py 3430, api.py 589, 658, 1032 to 1100, cockpit/inspect_api.py 422 (observed).

Pages by night with `Your answer ""`: night 170 m16, m35, m90; night 171 m16; night 172 m33, m47, m62, m71, m120. So 9 pages (observed: `reach_count.py`).

### W8 and W9: every page row path that can carry another request's rows

1. principal.py 1154, `readings_owed`: no request scope. W8.
2. sandbox.py 4749 to 4754: every owed reading onto every present and confirm. W8.
3. principal.py 2319 to 2326, `_page_body`: readings skip the filter, and a confirm runs no filter. W8, and any confirm row.
4. principal.py 2558 to 2562: the render of an owed reading, no owner check. W8.
5. principal.py 1285, `row_items`: [] for `reading:`, `glossary_terms`, `constraints` and a ledger row about a constraint. W8, W9.
6. principal.py 1484 to 1487, `off_page`: a row of no item stays. W9.
7. principal.py 1531 to 1535, `request_rows`: refs of no item take the open request. W9.
8. sandbox.py 4258 to 4260, the send door adds `request_rows`. W9.
9. sandbox.py 4250 and 4288: the door's filter on a present only. W8 on confirm.
10. api.py 13623, the rulings door's `off_page`, which keeps the same rows as the page. W8, W9.
11. The wakes that choose account rows while a request is open: `tick:agenda` and `tick:observed_entries`, frame 241's site, the agenda tick's row choice. W9.

(observed: the code at head.) So 11 places in 3 files. One reader change, `row_items`, reaches places 5, 6 and 10 through `request_of`. Places 1 to 4 and 9 do not call `request_of` today (observed).

Lines by night (observed: `reach_count.py`, the end state of each register):

| Night | W8, a reading of another request or of the account on a request page | W9, rows of no item on a request present |
|---|---|---|
| 170 | 7 lines on 4 pages: m20 (reading:m3, reading:m17, account), m35 (reading:m33, account), m42 (reading:m36, e_p1 on e_p2), m60 (reading:m43, m55, m59, e_p2 on e_p3) | m96, 4 glossary rows |
| 171 | 4 lines on 2 pages: m81 (reading:m70, e_p2; reading:m75, e_p1; on e_p3), m94 (reading:m80, account; reading:m89, e_p2; on e_p3) | 0 |
| 172 | 5 lines on 4 pages: m17, m47 twice, m62, m80 | m71, 19 rows; m130, 7 rows, rendered twice |

He contested the W8 line on m20, m42, m60, m81 (line 3) and on the three confirm pages of night 172 (observed: the words). On m81 he approved line 2 (observed).

### W12: every page sentence that names a tick key or a red test

1. principal.py 2473, the stopped page: `_stalled_words`, no test. The wall.
2. principal.py 429, `render_state`, a parked batch: `_stalled_words`, no test.
3. principal.py 454, `render_state`, a gave-up key: `_gave_up_words`, which prints "for bg_3", an id, because `_ref_words` returns a batch id as it is (reasoned: principal.py 1842 to 1860).
4. scheduler.py 1832, `stop_detail`: `_stalled_words`, a wake detail.
5. api.py 17607, `code_gaps`: `_gave_up_words`.
6. predicates.py 1844 to 1847, the park-ask detail: the kind's name, for a seat, on purpose (fact F21 comment).
7. principal.py 1779, "check: none. The team gave up writing it", a criterion line.
8. principal.py 1952 to 1954, the park page: "{own} of its {checks} checks still fail", own reds only.
9. principal.py 1940 to 1945 and 416 to 419: the park page and `render_state` name project reds by path. These already cover the gap, on a parked batch only.
10. principal.py 471 to 479, `render_state`: a count of failing tests, no name.

(observed.) So 10 sentences in 4 files, and 8 of them name no red test. Pages by night: night 172 m120 and m127 (3 renders); nights 170 and 171 none with this shape (observed: `reach_count.py`, a page with "still fail" and no "Fails" line). m127 also shows the fallback for `touch_mistaken`, twice (observed).

## 5. The match

| Candidate | What it says | Covers |
|---|---|---|
| Frame 241, open, 2026-10-14 | Ends when "the agenda page carries the rows of the current request and the rows that name no request go to the state view or their own page" (observed: stack.md 2716) | W9, whole. Unbuilt. Its last status, 2026-10-17, names `off_page` |
| Frame 264, parked, 2026-10-16 | A question to Roman: "does a request page show the account at all, and in which words" (observed: stack.md 2333) | W9's decision. The question is not asked yet (observed: its status, parked 2026-10-21) |
| Frame 316, open | An agenda page shows the rows of the item it is about (observed: stack.md 2107) | W9 by item, in part. Its count found 0 such pages on nights 163 to 164a. It does not cover rows of no item |
| Frame 325, open | The notes section shows a ledger row only when a seat took a default or asks him (observed: stack.md 1950) | W9's m130 rows are claims that ask for a ruling, so no |
| The seam design, doubt 3 | "This record puts the line on the next page of any kind, and a page about another request then carries it. Frame 193's rule that a page is about one request may refuse that" (observed: rulings-seam-design-2026-10-26.md 251) | W8, named before the build. No frame carries it |
| Frame 312, open | A page after a review with no verdict names the tick and the attempts (observed: stack.md 2135) | W12 in part: it names the tick, not the test |
| Frame 253, open | One helper writes a key in words (observed: stack.md 2561) | Built by F21. Not the test |
| Frame 336, open | The check line shows the error of a red test (observed: stack.md 1659 heading) | W12 for a red test with a line. This test has no line |
| Frames 130, 114 | A red project test shown as passing; a failing inherited test has no route | Kin of W12 and W3, older, not the page sentence |
| Frames 337, 338 | The naming door and the relay split | No. Neither is a page row path |

(observed: the stack headings by `grep "^### "`, the facts file.) No candidate covers W7. No frame names `body_text` or the read-back quote (observed: a grep of the stack for "read-back" and "body_text").

## 6. The proposals

### P7, W7: one reader of his words of a message

- **Change.** Add `said(conn, message_id)` beside `record_entry`, principal.py 3412. It reads `entries` `e_<message>` and falls back to `messages.body_text`. `reading_line` and the 8 other readers of section 4 call it (reasoned: `record_entry` names the transcript the one record of his words).
- **Price.** 2 cycles. A text change at one reader with 9 callers (reasoned).
- **Red test.** On a copy of the night 172 register, `reading_line(conn, "reading:m31")` gives `Your answer "Yes, use the AppData Roaming folder under the home ...", as the team read it: 6 lines approved.` At head it gives `Your answer ""` (observed: the head output in section 1).
- **Leaves out.** The rulings with no reply stay, because they hold no rows and no reader is wrong on them. The clause "a row is wrong" of a reading with no line stays, because it needs a line rule for a clarify's rows, a separate fact (reasoned).
- **The cheaper option.** `land` writes `body_text` on its verdict path, at 3107 to 3112, 1 cycle. It changes the sets of the 4 readers that filter `body_text IS NOT NULL`, and old registers stay empty (reasoned). The read does not recommend it.

### P8, W8: a reading rides the page of its own request

- **Change.** `row_items` walks a `reading:<reply>` ref to the refs of `read_back_rows(conn, reply)`, so `request_of` gives the reading's request. `readings_owed` takes the page's refs and keeps a reading whose `request_of` is the page's request, or the account on a page with no request. The send door and `_page_body` call it on present and confirm alike (reasoned).
- **Price.** 4 cycles, and one question first (reasoned).
- **Red test.** On the night 172 register, the send of m47 holds no reading:m34 and no reading:m44, m80 holds no reading:m77, and m17 holds no reading:m14. m62's reading:m48, the same request, stays.
- **Leaves out.** A reading of a delivered request then rides no page. That is the question. Roman ruled the read-back on 2026-10-26 22:5x: "No it should be every time no? Why not" (ruled: stack.md 1731). The question he answered was whether every reply gets a read-back (observed: the proposal of 22:04, "confirmed_by to Roman because a read-back costs his attention on every reply"). The design then wrote "every page he gets" (reasoned: design 2.3). Recommended answer: every reply is still read back, on the next page of its own request, and the reading of a delivered request or of onboarding shows on the state view and not on a page. A wrong reading after a merge revokes nothing on a new request's page (reasoned). This is a departure from the design's form and maybe from his ruling's reach, so the question goes to him (reasoned: the provenance rule, wall-guide cause 11, "Escalate. Always").

### P9, W9: rows of no request leave a request's page

- **Change.** Build frame 241's mechanism at `request_rows`, principal.py 1531 to 1535. When the refs reach no item, the page is the account's page and gets `how_it_works`, not the open request. `off_page` then treats a row of no item on a request page as off (reasoned).
- **Price.** 5 cycles, after frame 264's question (reasoned).
- **Red test.** On the night 172 register, s179's send renders m71 with lines 1 to 5 of the account and the 19 rows, and no clear() request line. s272's send renders m130 with the 7 claims and no format_filename lines.
- **Leaves out.** The choice of rows by the agenda and observed-entries ticks stays. The ticks still wake while a request is open. This reverses frame 190's design 2.1, which rests on law 8 and on night 136's 49 pages with no request line (observed: frame190-design.md 395 to 431). So frame 264's question comes first: does a request page show the account at all. Recommended answer: no. The account's open rows reach him on their own page, so law 8 still holds, and his words have the account row to land on (reasoned).

### P12, W12: the stopped sentence names the red test

- **Change.** For a `tests_failing` key, `_stalled_words` and `_gave_up_words` read `park_reds(conn, batch)` and name each red test by path with its error line from `_failure_line`. One helper serves sentences 1 to 5 of section 4. `TICK_WORDS` gets `touch_mistaken` (reasoned).
- **Price.** 2 cycles (reasoned).
- **Red test.** On the night 172 register, m120 renders "The team gave up: tests/test_types.py still fails after 3 attempts: AssertionError ...". m127 renders words for `touch_mistaken` and not "could not finish a step".
- **Leaves out.** The route for a red project test with no criterion stays, wall W3 under F7 and F25. The test gets a sentence and no numbered line, because "the principal never rules on a test" (ruled: Roman, 2026-10-08, cited in `check_line`, principal.py 528).

## 7. Doubt

1. The agent principal keeps the pages of its own walk only. Each walk starts with "Nothing yet. This is the first page of this walk." (observed: `probes/agent_principal.py` 141, 197 to 202). So "I gave no such answer" and "this is the first page" on W8 measure the driver's memory. Roman would remember m34 on m47. W8 is still wrong by "a page is about one request", not by his denial (reasoned).
2. P8 and P9 change what he sees, and each crosses a design that rests on a ruling or a law. The read cannot rule them. Frame 193's rule "a page is about one request" was not read for its provenance (not in the records read here).
3. The W8 and W9 counts use the end state of each register. A row that moved between the page and the end can count wrong (reasoned).
4. P7's helper changes 8 door reads beside the page. On night 172 none of them refused because of an empty body (observed: section 4). A changed read can make a door refuse where it passed (reasoned).
5. W12 cost him no clause of his own. Its rank rests on the false sentence, not on his answers (observed: m121, m128, m129).
6. This read ran over its 120k cap (observed: the session's token line).

## 8. Usage

One agent on Opus, no sub-agents. Three probe scripts against read-only registers. About 175k tokens on the session line at the write, above the 120k cap. Not read: frame 193's provenance; the line rule for a clarify's reading rows; the night 170 and 171 W7 sources by row.
