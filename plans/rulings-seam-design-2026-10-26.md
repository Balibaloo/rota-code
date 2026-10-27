# The seam design of his ruling as one record per ref, 2026-10-26

Sprint 26 row 3. Read only at 9b0d4a5c on `rota/foundation`. The code equals d495db74, because the two commits after it change `plans/` only (observed: `git log d495db74..HEAD`). Line numbers are at head. No pytest, no model call, no night database opened.

## The result

One new table, `ruled_refs`, holds one row per ruling and ref: `id`, `ruling_id`, `ref`, `line`, `verdict`, `act`, `target_kind`, `target`, `words`, `words_from`, `old_text`, `ref_version` (reasoned: section 1). Confirmation and status are not stored. A view derives them, so each row is written once and never changes (reasoned: section 1). The Liaison's `rulings.rule` call writes the rows, and one checker at write time is the only place that compares the reading with his words (reasoned: section 2). Each later page shows one numbered line per reply that he has not confirmed. A reply that rules three refs adds one line with up to three clauses (reasoned: section 2). Of the 57 functions behind the brief's 49 readers, 24 are deleted, 22 read a column, 10 become parts of the one checker, and 1 is the one reader (reasoned: section 3). The build is five passes, about 14 cycles and about 140k of the holding session, measured on night 170 (reasoned: sections 3 and 6; ruled: Roman, 2026-10-26 23:4x, "I want all the fixes in", `plans/stack.md` 1445).

## 1. The record

### 1.1 The table (reasoned, from the six fields of `plans/rulings-ledger-match-2026-10-26.md` section 4)

| Column | Holds | Departs from today |
|---|---|---|
| `id` | a hash of `ruling_id` and `ref` | per ref, where today the key is the reply (observed: `schema.sql` 671 to 686) |
| `ruling_id` | the `rulings` row of the reply | new; the reply-level row stays (reasoned) |
| `ref` | the row it rules: a criterion, an item, `guess:<item>`, a batch, a test row, a ledger row, or `reading:<reply id>` | today a key inside the `per_item` JSON (observed: `schema.sql` 675) |
| `line` | the page line number as he saw it, or null for a row he did not see numbered | new; F28 and `_ruling_order` re-derive it today (observed: `facts-2026-10-27.md` F28; `api.py` 6709) |
| `verdict` | approve, contest, revise, later, now or drop | the `per_item` value, unchanged in meaning (observed: `_ruling_word` in `rulings_rule`) |
| `act` | drop, keep, rewrite, add, remove, or null | new. Null means that no act is granted. A reader never reads null as a permission (reasoned: "never ... treats silence as consent", `composition.md` Flows) |
| `target_kind` | row, check, sentence, identifier, source_line, path or request | new (reasoned: the targets of P1 to P11, `frame339-reach.md` section 2) |
| `target` | the thing the act names, as `path:line`, a symbol, a path or a sentence | new |
| `words` | the verbatim span of his words that rules this ref | today `rulings.words` holds the whole last reply (observed: `api.py` 12878 to 12881) |
| `words_from` | the message id of the span: his reply, or an earlier answer of the same exchange | new; it closes frame 337's cause, an earlier answer that counts for nothing (observed: `frame337-agency-read.md` section 3) |
| `old_text` | the text of `ref` when he ruled | replaces `rulings.texts` (observed: `schema.sql` 682 to 685) |
| `ref_version` | the version of `ref` when he ruled | new; it lets the view mark a row stale (reasoned) |

An index on `(ref, ruling_id)` lets every reader find the rulings on a row by key. Frame 300 asks for that join (observed: stack.md 1904 to 1906).

### 1.2 The view (reasoned)

`ruled_refs_live` adds three derived columns to each row:

- `status`: `open` while the `rulings` row is open, `landed` when `land` lands it, `superseded` when a newer landed row on the same `ref` exists, and `stale` when `ref` now has a higher version than `ref_version`. The newest landed row per ref is his ruling on the ref (observed: F1, "his newest ruling on a ref").
- `confirmed_by`: the reply id of a landed row with `ref` = `reading:<this row's reply id>` and verdict approve, else null.
- `provenance`: `decided` when `confirmed_by` is not null or the verdict came from his keypress, else `reasoned`.

A row never changes after its insert. So a later write cannot overwrite a reading, and the identity derives from the content (observed: `composition.md` Records, "A record's identity derives from its content").

### 1.3 The one writer (reasoned)

One function, `ruling_rows(conn, ruling_id, page, reading)` beside `last_ruling_on` in `principal.py`, builds the rows. Two callers stage them, as two callers write `rulings` today (observed: `api.py` 12878, `principal.py` 2433 to 2445):

1. The Liaison's `rulings.rule`, for a reply in his words. The session commit inserts the rows.
2. `land`, for his keypress verdict. That verdict is his own act and not an inference, so its rows read `decided` at once.

The writer refuses a ref that no table holds, by `_table_of_ref` (observed: `api.py` 12866). That is frame 300's red test (observed: stack.md 1906).

### 1.4 What happens to `rulings` and `per_item` (reasoned)

- `rulings` stays as the reply-level row: `ask_id`, `reply_id`, `verdict_id`, `status`, `version` and `words`. `words` keeps his whole reply, a copy of `messages.body_text`, for the night report.
- `per_item` stays written as the call's map, so the cases keep their shapes (observed: frame 300 Ends-when, "the op's map argument kept"). After pass 2, no reader in `rota/` reads it.
- `texts` is no longer read after pass 2. `old_text` holds the same fact per row.
- `init_db` back-fills `ruled_refs` from `per_item` on an old night database: `act` null, `words` the whole reply, `words_from` null (observed: `db.py` 256 adds the `texts` column the same way). A back-filled row never gets a read-back line, and it reads `reasoned`.

## 2. The writer and the read-back

### 2.1 The call (reasoned)

`rulings.rule(rulings={...}, words="<the whole reply>")` keeps its shape. A value is a verdict word, as today, or an object:

`{"verdict": "contest", "act": "remove", "target": "get_app_dir:518", "words": "you can remove the line at 518"}`

A contest or a revise needs the object with `words`. Today a contest needs `words` that are not empty (observed: `api.py` 12852 to 12855). `act` and `target` are optional, and a null act grants nothing.

### 2.2 The one checker at write time (reasoned)

`reading_fault(row, page, exchange)` runs once per row that is not an approve, inside `rulings_rule`:

1. `words` is a contiguous verbatim span of `words_from`, and `words_from` is his reply or one of his answers in `earlier_exchange`. The span rule is group 1's `_span_of`, case-folded (observed: `agency-groups-2026-10-26.md` line 13).
2. The target exists: a page line on the page, a `path:line` in the batch tree or in `drop_notes`, a path in the tree or the guess, a symbol in `code_index` (observed: `drop_notes` holds P1's target, `frame339-reach.md` section 1).
3. The span supports the verdict on the line. C1 to C5 become branches of this one check, with the span as input in place of the whole reply (observed: C1 to C5 check the reading, `frame339-reach.md` section 5).

After the write, no reader reads his words for a fact (reasoned). The re-checks in `land` that the facts record put at `principal.py` 2261 and 2311 are deleted, because `land` reads the row (observed: `frame337-agency-read.md` instances 11 and 12).

### 2.3 The read-back (reasoned; ruled: Roman, 2026-10-26 22:5x, "No it should be every time no? Why not", stack.md 1442)

`_page_body` adds one numbered line, last, to every page he gets while a landed reply of his has rows and no `confirmed_by`. The line goes last, so no other line number moves, and line 1 stays the request. The code writes the line from the columns. No model writes it.

The form, one line per reply:

`7. Your answer of 14:02, as the team read it: line 5 is wrong; remove line 518 of get_app_dir; lines 1 to 4 approved. Say ok, or say what we misread.`

- Each ref that is not a plain approve gets one clause: the verdict, then `act` and `target` when present.
- The approves collapse into one count clause.
- A reply that rules three refs adds one line with at most three clauses. A page carries one line per unconfirmed reply. In practice that is one line, because "ok" confirms it (reasoned).

The line's ref is `reading:<reply id>`. He rules it like any other line:

1. An approve, "ok" included, writes a row `reading:<reply id>` approve. The view then gives every row of that reply a `confirmed_by`. This is his reply and not silence (observed: `landing.md`, "ok" ... "approve every line").
2. A contest makes the Liaison write new rows on the refs that his words correct. Those rows supersede the old rows, and the next page reads them back once. A row on a `reading:` ref is never read back, so the chain ends at his approve (reasoned).

### 2.4 What a reader does with an unconfirmed row (reasoned)

- A reader acts on `verdict`, `act` and `target` as it acts on `per_item` today. A wrong reading is visible on the next page, and his contest revokes the work through the contest path (observed: `composition.md` Flows, "Only a ratified amendment to something approved revokes work downstream").
- A null `confirmed_by` never reads as confirmation. The provenance view reads the row `reasoned`, and `basis.ruled` counts confirmed rows only (observed: `schema.sql` 128 to 129 counts every landed ruling today).
- The night report counts the unconfirmed rows at the night's end.

## 3. The readers

The brief's 49 are 21 + 16 + 12 units. By function, the three facts name 57 functions, because P1, P6 and P7 hold helpers (observed: `facts-2026-10-27.md` F1 to F3). "Row" below means a row of `ruled_refs_live`, read through `ruled(conn, refs, ...)`, the one reader that replaces the body of `last_ruling_on`. Each mapping is reasoned from the docstring at head.

### 3.1 F1, readers of `rulings` (21)

| Function | File:line | Reads in place of its own rule |
|---|---|---|
| `last_ruling_on` | principal.py:769 | becomes `ruled(conn, [ref])[0]`, the one reader |
| `term_collision` | predicates.py:349 | rows on the term refs, `verdict`, `words` |
| `_words_on_rows` | runner.py:597 | deleted: `words` of the rows on `cids` |
| `_line_legend` | runner.py:633 | `line`, `ref` and `old_text` of the ruling's rows; the pattern goes |
| `contests_on` | runner.py:704 | rows with verdict contest on `ref`, `words`, `old_text` |
| `_retired_carry` | runner.py:4250 | rows on frame 322's key set: the item, `guess:<item>`, its tickets and its criteria |
| `park_ruling` | scheduler.py:1850 | the rows of the ruling cover the page refs |
| `ruled_clarify_criteria` | scheduler.py:2039 | deleted: frame 338's `ruled_rows` reads the contest and revise rows |
| `ruled_test_criteria` | scheduler.py:2065 | deleted: `ruled_rows`, as above |
| `_confirm_landed` | api.py:656 | `rulings.status` by ask, through the view |
| `_reply_sentence_fault` | api.py:1625 | `words` of the row on the item |
| `_assert_words_fault` | api.py:1707 | `words` and `act` of the rows on the item |
| `_landed_approval` | api.py:2307 | the newest landed row on `id`, verdict approve |
| `_ruling_order` | api.py:6709 | deleted: `line` of the ruling's rows |
| `rulings_load` | api.py:12938 | the view |
| `_ruling_texts` | api.py:20900 | `words` of the rows on frame 322's key set |
| `contested_statement` | principal.py:716 | the newest row on `sid`, verdict contest |
| `land` | principal.py:2026 | writes the keypress rows and reads rows to apply; its re-checks go |
| `_land_shift` | principal.py:2461 | rows with verdict later, now or drop |
| `apply_rulings` | principal.py:2530 | `rulings.status`; the rows follow by the view |
| `chain_verdict` | principal.py:2602 | the landed rows of the chain's ruling |

### 3.2 F2, the page lines his words name (16, less F1, F3 and the writer)

| Function | File:line | Reads in place of its own rule |
|---|---|---|
| `_page_named_lines` | runner.py:2739 | deleted: `line` and `ref` |
| `_item_sentences` | api.py:1428 | deleted: `target_kind` sentence on the item, against a row on a page line |
| `_about_a_check` | api.py:5622 | deleted: `target_kind` check |
| `_sentence_hits` | api.py:6195 | deleted with P7 |
| `_keep_cancels` | api.py:6760 | deleted: `act` keep against rewrite |
| `_ruling_words_on` | api.py:6782 | deleted: `words` of the row on `cid` |
| `_live_cues` | api.py:11218 | a helper of `reading_fault`, input the span |
| `_line_cues` | api.py:11636 | a helper of `reading_fault`, input the span |
| `_line_refusal` | api.py:11766 | becomes `reading_fault` |
| `_cue_clauses` | api.py:11912 | a helper of `reading_fault`, input the span |
| `pointer_fault` | api.py:11927 | a branch of `reading_fault` on `target_kind` path against request |
| `_unnumbered` | api.py:12123 | a helper of `reading_fault`, input the span |
| `_unnamed_contest` | api.py:12143 | a branch of `reading_fault`: the span from `words_from` names or quotes the line |
| `_earlier_reading` | api.py:12200 | deleted: `words_from` carries the earlier answer |
| `_agreed_contest` | api.py:12228 | a branch of `reading_fault`, input the span |
| `returned_line` | principal.py:1545 | deleted: the "about line N" clause; the sentence stays |

### 3.3 F3, what his words permit by a phrase (12 units, 20 functions)

| Unit | Functions, file:line | Reads in place of its own rule |
|---|---|---|
| P1 | `_asks_removal` api.py:20865, `_removal_spans` 20816, `_unruled_gone` 20893 | deleted: `_unruled_removal` reads rows with `act` remove and a `target` equal to the `drop_notes` line |
| P2 | `_words_remove_a_kind` api.py:1366 | deleted: `act` remove, `target_kind` identifier on the item |
| P3 | `_removal_asks` api.py:1466 | deleted: `act` remove, `target_kind` sentence on the item |
| P4 | `_other_line` api.py:1451 | deleted: `line` of a contest row other than line 1 |
| P5 | `_page_reply_fault` api.py:1392 | deleted: the reply has rows on page lines |
| P6 | `ruling_drops_line` api.py:6504; `_line_dropped_on` 6771, `_drops_whole_line` 6179 | `act` drop and `line`; the two helpers are deleted |
| P7 | `_words_fault_on` 6743, `_keeps_words_on` 6736, `ruling_asks_no_new_words` 6484, `_faults_on` 6152 | `act` rewrite or keep, `target_kind` check or row; `_faults_on` is deleted |
| P8 | `_page_added_lines` api.py:6539 | `act` add, `target` the ticket, `words` the line to add |
| P9 | `criteria_respecify` api.py:6858 | `words` of the contest row for the contested names |
| P10 | `disputed_paths` runner.py:2022 | deleted: `act` remove or add, `target_kind` path |
| P11 | `_note_words` api.py:12311 | deleted: `act` drop or rewrite on the team-note line |
| C2 | `_names_request` api.py:12018, `_faulted_approve` 12048 | branches of `reading_fault`, input the span |

### 3.4 Also at the reach and not in the 49 (observed: `frame339-reach.md` table; `python -m rota.tools.map table rulings`)

`_line_reading` 11174, `_head_verb` 11453, `code_line_faulted` 11984, `built_line_faulted` 11740 and `_quotes_line` 12354 become helpers of `reading_fault`. `_resolve_contest` runner.py:2696 reads the contest rows. `verdict_rows` scheduler.py:1949 folds into `ruled_rows`. `contested_texts` principal.py:750 becomes `old_text`. `nightreport.py` 309 and 455 and the two seeds in `testkit/fixtures.py` 92 and 184 read or write the table.

The count over the 57: F1 has 4 deleted, 16 on a column and 1 the one reader. F2 has 8 deleted and 8 in the checker. F3 has 12 deleted, 6 on a column and 2 in the checker (reasoned: the tables).

### 3.5 The passes and their order

| Pass | Builds | Functions | Order forced by |
|---|---|---|---|
| 1. The record | the table, the view, `ruling_rows`, the back-fill, the call form, checker steps 1 and 2, `last_ruling_on`, `rulings_load`, the writes in `land`, the two seeds, and the briefs `landing.md`, `landing.base.md` and `answering.md` with their `.tools` | 4 and 2 seeds | `land` is shared with F16, F20, F26, F28 and F37. Frame 330's pass 5 edits `land` now, so pass 1 starts after 330 commits (observed: `facts-2026-10-27.md` shared places; stack.md 1443) |
| 2. The readers of F1 | the other F1 readers, frame 338's `ruled_rows`, frame 322's key set | 18, and `verdict_rows`, `_resolve_contest`, `contested_texts` | pass 1's table. 339's door calls `_ruling_texts`, and 339 is on the branch (observed: `agency-groups` section 2) |
| 3. The one checker | `reading_fault` over the span, with the 8 F2 functions, the 2 of C2 and the 5 of section 3.4; the `land` re-checks out; `returned_line` | 16 | `rulings_rule` is pass 1's place, so pass 3 follows pass 1 (observed: shared place `rulings_rule`, F2, F26, F37) |
| 4. The permission readers | P1 to P11 on `act` and `target`, and the 7 deleted F2 helpers that feed them | 25 | P6 and P7 call `last_ruling_on` (pass 1). P1's door calls `_ruling_texts` (pass 2). P6 shares `_drops_whole_line` with the F2 cues (pass 3) |
| 5. The read-back | the line in `_page_body`, the `reading:` ref in the keys and in `_table_of_ref`, `confirmed_by` in the view, `basis.ruled`, the night report count | about 6 | pass 1's view, and `returned_line` after pass 3. It edits `_page_body` and not `land`, so it can run beside pass 4, as 339 ran beside 330 (observed: stack.md 1443) |

`criteria_respecify` is shared with F6, and `_assert_words_fault` with F25. Both facts are in sprint 27, so no order is forced now (observed: stack.md 76 to 88).

## 4. The red tests after the build

| Red test | From | Pass | Lands with no refusal |
|---|---|---|---|
| s193 turn 1, night 168: `{5: contest}` with the span "Line 5 is wrong" from m76, and m78 as the reply | 337 Ends-when 1 (observed: stack.md 1370) | 3 | yes |
| night 147's s281: six contests on lines that m131 does not name | 337's guard | 3 | no, it stays refused by design |
| s156, night 168: m50 carries crit_1 and crit_2 only, and s157 keys `criterion_repair` | 338 Ends-when 1 (observed: stack.md 1350) | 2 | yes |
| night 164's m94: the relay of cr_2 and cr_6 keys `criterion_repair` | 338 proposal line 5 (observed: `frame338-agency-read.md` section 5) | 2 | yes |
| s185, night 166: the window holds r_1ec1beb146's words | 322 proposal line 5 (observed: `frame322-agency-read.md` section 5) | 2 | yes |
| s199, night 163: the wake names tk_2 | 322 Ends-when 1 | not this row, the criteria wake | built at bf300ce4 (observed: 322 read section 4) |
| s200, night 163: the six-cap refusal names tk_2 | 322 proposal line 5 | not this row, the text pass (observed: `agency-groups` section 3) | no, a refusal by design |
| s274 and s276, night 161: the re-slice and the amend carry his landed words | 315 Ends-when 1 (observed: stack.md 1712) | 2 | yes |
| s282, night 161: the id refusal offers a new id | 315 Ends-when 1 | not this row, an id fact | no |
| s194 seq 2, night 166: a respecify into a sibling's words is refused and names the retire | 329 Ends-when 1 (observed: stack.md 1526) | 4, "names the retire" from `act` remove | no, a refusal by design |
| night 169's m36 and m37: "remove the line at 518" lets the Developer's commit through | 339 (observed: `frame339-reach.md` section 1) | 4 | yes |
| a reply on three refs gives one read-back line; "ok" confirms the three rows; a contest supersedes them | the ruling of 22:5x | 5 | yes |
| a ruling on a ref that no table holds is refused at write time | 300 Ends-when 1 (observed: stack.md 1906) | 1 | no, by design |

Seven land with no refusal. Four are refusals by design, and two are outside this row (reasoned: the table).

## 5. The cassettes

| Mode | Cases | Stale by | Count |
|---|---|---|---|
| liaison `landing` | 8 on a present, 1 on a confirm | the call form in `landing.md`, `landing.base.md` and `landing.tools` | 9 (observed: `tests/rota/cases/*.yaml`) |
| liaison `answering` | 1 | the call form in `answering.md` and `answering.tools` | 1 (observed) |
| liaison `verdict` | 1, with a `rulings` fixture | the read-back line, only if its wake shows a page | 0 to 1 (reasoned) |
| liaison, mode by inbound | 2, with a `rulings` fixture | a reader's output, only if their wake changes | 0 to 2 (reasoned) |
| every other mode | no case holds a `rulings` fixture | none | 0 (observed: a script over 167 cases) |

The re-record is 10 cases, 13 at most. At about 5 minutes of GPU per case, that is about 50 to 65 minutes on the main card (observed: `operating-facts.md` 107). A back-filled row never gets a read-back line, so the page line stales no recorded case (reasoned: section 1.4). The scene tests are not cassettes. 26 test files call `rulings.rule`, and 26 render a page (observed: `git grep -l`).

## 6. The price

The anchors of `operating-facts.md` 239 to 250 are 10k of the holding session per cycle, a cold implementer pass of 74k to 217k, a review of 61k to 76k, and a resumed pass of 7k to 40k (observed).

| Pass | Cycles | Agents | Note |
|---|---|---|---|
| Design review of this record | 1 | reviewer, about 66k (observed: frame 24's design review) | before pass 1 |
| 1. The record | 3 | implementer cold, about 150k to 217k; review, about 70k; resume, about 40k | the largest: a schema and a brief |
| 2. The readers of F1 | 2 | implementer, about 75k; review, about 65k | |
| 3. The one checker | 3 | a count over nights 160 to 169 first, then implementer, review and resume | gate: 0 new false refusals (ruled: `wall-guide.md` section 3, "the count") |
| 4. The permission readers | 2 | implementer, about 75k; review, about 65k | |
| 5. The read-back | 2 | implementer, about 75k; review, about 65k | beside pass 4 |
| Gate with 10 to 13 re-records | 1 | about 6k per gate run (observed: `operating-facts.md` 245) | |

The sum is 14 cycles and about 140k of the holding session (reasoned). The stack's row priced about 10 cycles (observed: stack.md 53). The four extra cycles buy F2, F3 and the read-back, which the group 2 pass alone leaves (reasoned).

Night 170 measures the build, after every row of sprint 26 (ruled: Roman, 2026-10-26 23:4x, stack.md 1445). The counts per frame (observed: the Ends-when lines and `agency-groups` section 3):

- 337: naming-door refusals that quote an earlier answer, 2 of 2 toward 0; approvals of a line he called wrong, 1 toward 0.
- 338: relays of a ruled row that end with no acting call, verdict and converse alike.
- 322: criteria that a page reply calls wrong, 3 of 7 toward 0.
- 315: batches with no criterion that holds his landed correction, 1 of 5 toward 0.
- 339: Developer removals refused on a granted removal.
- New, the read-back: read-back lines contested against lines shown, and rows unconfirmed at the night's end (reasoned).

### The smaller designs and what they leave (reasoned)

- The group 2 pass alone, `plans/rulings-ledger-match-2026-10-26.md` section 5 step 1, with no new column: it leaves the 16 F2 readers, the 20 F3 functions, the read-back and frame 300's JSON.
- `act` and `target` inside the `per_item` JSON, with no table: it leaves frame 300, the `LIKE` match of `last_ruling_on`, a `stale` that no join reaches, and a key that no join can walk (observed: `principal.py` 779; stack.md 1906).

## 7. The doubt

1. The call form is not measured on the night's model. An object per contested line can cost the Liaison more call errors than it saves (reasoned: `rulings_rule`'s docstring, where a second function invited misuse 5 of 5 on 2026-09-10). Measure the 9 landing cases on the object form before pass 1 fixes it, and keep a flat `acts` map as the fallback.
2. Pass 3 replaces measured doors. Each branch of C1 to C5 came from a night, and the span input can lose a case that the whole reply caught. The count before pass 3 is the guard, and s281 must stay refused (observed: `frame337-agency-read.md` section 1).
3. The night principal is an agent, `probes/agent_principal.py`, so night 170's read-back counts measure the agent and not Roman (observed: `operating-facts.md` 173). This record puts the line on the next page of any kind, and a page about another request then carries it. Frame 193's rule that a page is about one request may refuse that (observed: `principal.py` `_page_body`, "A page is about one request"; reasoned).
