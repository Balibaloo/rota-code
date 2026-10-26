# Frame 339, the reach read: every reader of the principal's words by a phrase

Read on 2026-10-26 at HEAD af0ec66a. `rota/roles` and `rota/core` equal 8264e4fd, so the line numbers of `plans/night169-m36-read.md` hold (observed: `git diff --stat 8264e4fd HEAD -- rota/roles rota/core` is empty). Register copy: `f339_clickI.db` in the scratchpad of session 8db3a3f9, taken by the sqlite backup API. No fix is proposed.

## 1. The record

His permission is held only as free text. The `rulings` row holds his answer: `words` (his text, whole) and `per_item` (a verdict per page row, approve, contest or revise). No column says what the ruling permits as a line, a symbol, a path or an act (observed: `rota/core/schema.sql:671` to `692`).

- m36 (seq 37) has ruling `r_58bf1e8c70`: `ask_id` m36, `reply_id` m37, `verdict_id` m38, status `landed`. `per_item` is `{"get_app_dir_windows": "approve", "crit_1": "approve", "crit_2": "approve", "crit_3": "contest", "batch_1": "approve"}`. `words` start "You can remove the line at 518 in get_app_dir ..." (observed: copy).
- m40 (seq 41) has ruling `r_62dd42ab85`: `reply_id` m41, `verdict_id` m42, the same `per_item`, `words` "Yes, you can remove the line at 518 ..." (observed: copy).
- The route: m37 and m41 are `converse` messages from the principal. The Liaison read them and wrote the row by `rulings.rule`, and `principal.land` landed it (observed: `schema.sql:665` to `670`, the comment; `principal.py:131` "No parser reads the words").
- `texts` holds the old text of each contested criterion, not a permission (observed: `schema.sql:681` to `685`).
- No `requests` table and no `contests` table exist. `frame_rulings` classifies paths (program, attached, ignore, surface) and holds no answer of his (observed: `schema.sql:992`).
- The removal side has a structured record. `drop_notes` holds the batch, the path and each gone line with its owner and count, for batch_1 `[["get_app_dir", "folder = os.path.expanduser(\"~\")", 1]]` (observed: `schema.sql:370`; the gathering read). No row links a ruling to a `drop_notes` line (observed: schema).
- `_ruling_texts` (`api.py:20856`) selects the landed rulings by `per_item` keys, a record, and returns only `(words, True)` pairs. The door then reads the text (observed: `api.py:20856` to `20880`).

## 2. Every reader of his words by a phrase

Twenty readers take his answer, a ruling's words or a contest's words as input and decide by a regular expression, a substring or a fixed word list. Eleven gate a permission or a refusal on what he allows. Five check the Liaison's reading against his words. Four select or show sentences and gate nothing (observed: the table; the grouping is reasoned).

| # | File:line | Function | Phrase or pattern | Decision it gates |
|---|---|---|---|---|
| P1 | api.py:20822 | `_asks_removal`, with `_removal_spans` 20773 and `_unruled_gone` 20849 | the gone line quoted in a request clause (`_REQUEST_LEADS` 20713, `_REQUEST_VERBS` 20711, `_REMOVAL_WORDS` 20691, `_NEGATION_WORDS` 20696), a call head, or for his words `\bline {no}\b` (20844) | `code.commit` refusal by `_unruled_removal` 20562; the stop page lines of `_refused_commit` (principal.py:1402) |
| P2 | api.py:1366 | `_words_remove_a_kind` | `_REMOVE_CUES` 1363 within four words before `_KIND_WORDS` 1361 | `problem.assert` may drop an identifier from his item (api.py:1925) |
| P3 | api.py:1465 | `_removal_asks` | `_REMOVAL_ASK` 1460: "take it out", "remove", "not what i asked" | `problem.assert` may remove a sentence from his item |
| P4 | api.py:1451 | `_other_line` | `(?i)\bline\s+(\d+)` | refuses an item amend when his words contest another page line (1553) |
| P5 | api.py:1392 | `_page_reply_fault` | `_PAGE_CUE` 1384: "page", "line N" | refuses his page reply asserted as item text (1890) |
| P6 | api.py:6504, 6771, 6179 | `ruling_drops_line`, `_line_dropped_on`, `_drops_whole_line` | `_DROP_LINE` 6132: "drop/remove/delete line N", "line N should go" | the answer door names a drop and asks no rewrite (6607, 6662; sandbox.py:1929) |
| P7 | api.py:6743, 6736, 6152, 6760, 6484 | `_words_fault_on`, `_keeps_words_on`, `_faults_on`, `_keep_cancels`, `ruling_asks_no_new_words` | `_WORDS_FAULT` 6122, `_KEEP_WORDS` 6146, `_CHECK_FAULT` 6110 | `criteria.respecify` refuses with "The criterion stands" (7028 to 7048); sandbox.py:1921 |
| P8 | api.py:6539 | `_page_added_lines` | `_ADD_LINE` 6523: "add a line that says ..." | the criterion lines his words add (6581) |
| P9 | api.py:6995 | `criteria_respecify` | `contested["words"].lower()` against `_named_tokens` | refuses a rewrite that brings back a name he contested |
| P10 | runner.py:2019 | `disputed_paths` | `_NO_BEYOND`, `_BEYOND`, `_COVERS`, `_NOTHING_TO_DO`, `_KEEP_LED`, `_TEST_FILE_LIST` (1959 to 1990) | paths taken off the touch guess (2357, 2394) |
| P11 | api.py:12311 | `_note_words` | `_NOTE_DROP` 12283, `_NOTE_CHANGE` 12288 | what his words ask of a team-note line, in `rulings_rule` (12610) |
| C1 | api.py:11174, 11636, 11453, 11218 | `_line_reading`, `_line_cues`, `_head_verb`, `_live_cues` | `_LINE_REF` 11129 ("line N", "N is"), `_LINE_FAULT` 11136, `_AGREE` 11142 | `rulings_rule` refuses a reading by `_line_refusal` 11766 (12824); `land` (principal.py:2261) |
| C2 | api.py:12143, 12228, 12048, 12018 | `_unnamed_contest`, `_agreed_contest`, `_faulted_approve`, `_names_request` | `_LINE_REF`, `_AGREES` 12106, `_BUILD_VERB` 12002 | the sub-refusals of `_line_refusal` |
| C3 | api.py:11984, 11927 | `code_line_faulted`, `pointer_fault` | `_TOUCH_WORDS` 11868, `_CUE_FILES` 11891 | keeps a contest of a built batch's code line (12711; principal.py:2311) |
| C4 | api.py:12354 | `_quotes_line` | five or more words of a page line | `rulings_rule` (12626, 12826) |
| C5 | api.py:12200 | `_earlier_reading` | `_LINE_REF` on his earlier answers | the lines his earlier answers name |
| S1 | runner.py:594, 630 | `_words_on_rows`, `_line_legend` | `api._LINE_REF` | the sentences and legend a seat gets |
| S2 | api.py:6782 | `_ruling_words_on` | `_LINE_REF` | the sentences that feed P6 and P7 |
| S3 | principal.py:1653 | `returned_line` | `_LINE_REF` | "about line N" on a returned page |
| S4 | runner.py:2693 | `_resolve_contest` | `_LINE_REF.sub` at 2757 | the contest text a seat gets |

Left out: `_asks_for` (api.py:13934) and `fence.named` (fence.py:110) read criterion text, not his (observed). `parse_reply` has no keyword list (observed: principal.py:131).

"line N" means a page line in C1 to C5, S1 to S4, P4 and P6. It means a source line only in P1 (observed: the patterns). m37 holds both: "Line 4 is still wrong" (page) and "the line at 518" (source) (observed: copy; reasoned: one pattern serves two meanings).

## 3. Every sentence to copy

One page offers a sentence to copy. The other pages offer a fixed form ("ok", "Name a line") (observed: `grep` of `principal.py`; no `pages*.py` and no `rota/liaison` exist).

| Where | Sentence or form | Reader it is written for | Plain meaning accepted? |
|---|---|---|---|
| principal.py:1482 | "To allow that, say so, as 'remove the `<line>` at line N in f()'." | P1, `_asks_removal` | No. "the line at 518 ... that sets the folder to the bare home folder" reads False (observed: the probe in the gathering read) |
| principal.py:1881, 1910, 1931, 1541, 1972 | "Reply 'ok' ..." | the Liaison model, then C1 (`_AGREE`) checks the reading | Yes for the Liaison. C1 accepts a list of agreement words (reasoned: `_AGREE` 11142 is a word list) |
| principal.py:1910, 1543, 1973 | "Name a line to correct only that line." | C1 and C2, by `_LINE_REF` | Partly. "line N" or "N is" counts. A line named by its content counts only through `_names_request` or the clause before (reasoned: `_LINE_REF` 11129, `_cue_clauses` 11912) |
| principal.py:1688 | "say for each line you want changed what to do with it" | C1, after a returned answer | The same as the row above (reasoned) |

The sentence at 1482 also quotes a docstring line as the rewrite (observed: m36, gathering read). It names the source line by number, and the same number reads as a page line in C1 (reasoned).

## 4. The lift

Three places lift a quarantine. Each reads the answer's arrival or a row's move, never the answer's meaning (observed: the code below).

- `land`, principal.py:2207 to 2214: an answer that closes a stopped page deletes each quarantined key `developer|tick:batch_start|...` that `door_rows(conn, ask, "stalled")` lists. It reads only that the ask closed. m37 and m41 each restarted the Developer once (observed: gathering read, s129 and s136).
- `land`, principal.py:2476 to 2485: an item approval change calls `db._lift_quarantines`. The item was already approved, so m37 moved nothing here (reasoned: rowcount 0 on a same-value write).
- `db._lift_quarantines`, db.py:589: a commit that moves a row lifts the keys that name the row. A ruling row moves no batch, criterion or item row (reasoned: the trigger list in the docstring).
- `scheduler.py:2558` deletes counts of keys that are not live and not quarantined. It lifts no quarantine (observed). `predicates.py:1755` and `runner.py` only read the quarantine (observed: grep).

## 5. The count

One structured record of his permission, a target and an act, replaces P1 directly, one reader with three functions (reasoned: only P1 gates a code removal). By the same shape it could replace P2, P3, P6, P7 (the drop part), P10 and P11, which also decide whether his words permit or ask an act on a named target. That is seven of eleven permission readers (reasoned). C1 to C5 check the Liaison's `per_item` reading against his words, so a record would not replace them; they would check it (reasoned). S1 to S4 select text and gate nothing. Readers that already read a record before the text: `_ruling_texts` and P6, P7 and P10 gate on `per_item` (contest or revise) and then read the words; the lift in `land` reads only `door_rows` and arrival (observed: api.py:6492, 6511, 6575; runner.py:2392). No reader reads a record of what he permits, because none exists (observed: question 1). `drop_notes` already holds the target of P1 in structured form (observed).
