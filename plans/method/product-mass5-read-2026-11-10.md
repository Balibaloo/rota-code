# The read of mass 5, the structure against its records, 2026-11-10

Written by one blind reader for frame 364. The reader read the design
pages named in the brief, the 11 run databases, the last turn logs and
the code that writes the rows. The reader read no other reader's page.
Every query ran on copies in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass5/db/`,
opened with `mode=ro`. The scripts are in the same folder: `q.py`,
`extract.py`, `pool.py`, `draw.py`, `b1.py`, `b3.py`, `fr.py`.

## Result

1. Of 20 design statements, 7 hold on every row the queries reach, 9 do not hold on some rows, and 4 cannot be told from the rows (observed: Part C).
2. All 11 runs end with open rows that no open page names. Open `report` messages to the Liaison are in 10 runs, and dry6 has open `deliver` messages instead (observed: B1).
3. Five desk questions end `unresolved` with no climb wake, in dry1, dry4, dry5, dry7 and dry8 (observed: `messages` m20, m69, m33, m19, m19).
4. Seven databases hold 18 to 243 ledger rows each with `author = 'principal'`. `rota/core/loop.py:553-555` writes these rows, not a person (observed: B3).
5. The doors refused 4,209 tool calls in 10 database files, and 46% of these refusals are the Architect's (observed: B2 counts).
6. The tool-call table records the call and not the refusal, so the pool comes from each session's account turn and from the next prompt (observed: `rota/core/db.py:2423-2440`, `rota/core/sandbox.py:5356-5408`).
7. 1,418 of the 4,209 refusals appear in no later prompt of their session, so the seat never read them (observed: `pool.json`, field `turn` null).
8. In the draw of 30, the stated fact is true in 24, false in 1 and cannot be told in 5, and 29 refusals name a route (observed: B2).
9. After a drawn refusal, the session followed the route 10 times, sent the same call again 4 times, sent another call 6 times, and ended or never saw it 10 times (observed: B2).
10. One drawn refusal names as its route the value it refused, and one names a call that the role does not hold (observed: draws 28 and 25).
11. Every database holds three clock columns, against the law that no table carries a clock (observed: `schema.sql:1003`, `:1232`, `:1288`).
12. The current scheduler code could not evaluate dry1 to dry4, because their schema has no `candidate_bindings` table (observed: `fr.py` output).

## Part A: what the design says the structure must do

Each statement is near the source's words. The bracket gives the check.

1. "Every record has one writer", and "every artefact has exactly one writing role per row" (`plans/composition.md:47`, `rota/LAWS.md:95`). [Count the roles in `receipts` per row.]
2. "The graph grants each role its reads, writes and message verbs; a role cannot do what the graph does not name" (`rota/MAP.md:14-16`). [Compare the role of each receipt with the `writes` edges of `rota/design/graph.json`.]
3. The Principal "write[s] no records", and the top rung "is never a ledger row written on the principal's behalf" (`plans/composition.md:19`, `rota/LAWS.md:188-189`). [Count `ledger` rows with `author = 'principal'`.]
4. "Artefacts carry versions and receipts; runtime bookkeeping does not" (`rota/MAP.md:31-32`). [Count artefact rows with no `receipts` row.]
5. "Nothing stops quietly. Every open obligation stays visible and countable until something discharges it" (`plans/composition.md:50-51`). [B1: each open class against the open pages and the last turn log.]
6. "Outstanding work is re-derived from the records each pass" (`plans/composition.md:53-54`). [Evaluate `scheduler.frontier_readonly` on a copy.]
7. "A record's identity derives from its content, not from when it was made" (`plans/composition.md:60-61`, `rota/LAWS.md:356-358`). [No whole-table test exists. Count ids that name rows in two artefact tables.]
8. "A ruling is a record. The Principal rules, the Liaison writes it, and it carries a version" (`plans/composition.md:62-63`). [`rulings.version`, and `rulings` rows with a receipt of a Liaison session.]
9. "A session commits or discards before it ends", and "a failed session leaves its row with `committed = 0` and its error as its last turn" (`plans/composition.md:64-65`, `rota/MAP.md:22-23`). [Failed sessions: last turn, receipts, tool calls.]
10. "A crashed session leaves its trigger open with its attempt count raised; past `message_attempt_cap` the message is quarantined" (`rota/LAWS.md:164-166`). [Failed sessions per trigger message against `messages.attempts` and `status`.]
11. "A wake dispatched past its cap is quarantined and said out loud" (`rota/LAWS.md:190-191`). [`tick_attempts` and sessions per wake key, `reported` and `messages.told`.]
12. "A question nobody answers climbs (`unresolved`)" (`rota/LAWS.md:190`). [Each `unresolved` message against `tick:unresolved` sessions that name it.]
13. "Every cap is a ruling of the principal. The ruling is a record with a writer and a version" (`rota/LAWS.md:203-204`). [Cap rows in `config` and `config_history`.]
14. "A ledger entry is resolved by a decision that names it, in the same commit, and by nothing else" (`rota/LAWS.md:320-321`). [Resolved `ledger` rows with no `decisions.resolves_ledger`.]
15. "The tool never rules for the Principal. It never settles a conflict, closes an assumption, or treats silence as consent" (`plans/composition.md:74-75`). [`rulings` with no reply and no verdict.]
16. "Approval of intent is required before work starts", and "no batch schedules unless its item's approval postdates the item's last amendment" (`plans/composition.md:22`, `rota/LAWS.md:229-230`). [Batches against `items.approval` and `approval_ver`.]
17. A door "refuses what a fact makes wrong" (`rota/MAP.md:42-43`). [B2: the stated fact against the rows.]
18. A door "names the route" (`rota/MAP.md:43`). [B2: the refusal text, and the next call.]
19. "A door never decides what a role should have judged" (`rota/MAP.md:42`). [B2: refusals whose test is a judgement of words.]
20. "No table carries a clock", and "no date, duration or timestamp column exists in `schema.sql`" (`rota/MAP.md:32-33`, `rota/LAWS.md:405`). [Columns named `at` or `started_at` in each database.]

## Part B1: the end state of the 11 runs

The query script is `b1.py`, and its output is `b1.json`. Dry6b is the
copy `dry6b_after_turn4`. Dry6c is the shared final file, so dry6c
holds the rows of dry6b too.

### What is open, by run (observed: `b1.py`)

- **dry1.** No open page. Desk messages: 4 `report` open (m21, m22, m86, m87), 1 `question` unresolved (m20, architect to terminologist). Quarantined: 2 Principal replies (m4 verdict, m5 converse, `told = 1`), 3 tick keys (all `reported` at least 1). Batch: 1 merged. Ledger: 11 open, 3 parked. Faults: 2 open. Failed sessions: 8, of which 6 (liaison on m4 and m5) have no later committed session on the same trigger. No turn log was read for dry1.
- **dry2.** No open page. 2 `report` open. No quarantine. Batches: 1 merged, 1 abandoned. Ledger: 4 open, 4 parked. Faults: 2 open. No failed session. No turn log.
- **dry3.** No open page. 1 `report` open. 1 tick key quarantined and reported. Batch: 1 merged. Ledger: 30 open, 4 parked. Faults: 2 open. A `claims` row names liaison session s207, and no `sessions` row s207 exists. No turn log.
- **dry4.** 1 open page (m63 present). 2 `report` open, 1 `challenge` unresolved (m69, developer to tester). 1 tick key quarantined and reported. 1 tick key at its cap and not quarantined (`developer|tick:tests_failing|bg_1`, attempts 3). Batch: 1 running. `touch_strays`: 11 open, 8 mistake. `drop_notes`: 1 open. Ledger: 192 open, 64 parked. Faults: 1 open. No turn log.
- **dry5.** No open page. 1 `report` open, 1 `question` unresolved (m33, architect to terminologist). 2 tick keys quarantined and reported. Batch: 1 deferred. Ledger: 228 open, 52 parked. Faults: 1 open. Last log `dry5/t9.log`.
- **dry6.** 1 open page (m12 present). 3 `deliver` messages open (m9, m10, m11, liaison to architect, terminologist, vision_keeper). 2 Principal replies open and never read (m15, m16 converse). Quarantined: 1 Principal reply (m8, told), 1 tick key (`architect|tick:survey|news`, reported). 1 tick key at its cap and not quarantined (`architect|tick:survey|src/icalendar`). No batch. Ledger: 14 open. No fault. Failed sessions: 15, of which 9 have no later committed session on the same wake. Last log `dry6/t5.log`.
- **dry6b.** 1 open page (m18 present). 1 `report` open. 3 Principal replies quarantined (m8, m14, m17, told). No batch. Ledger: 193 open, 21 parked. Faults: 1 open. Failed sessions: 9, none done again on the same trigger. Last log `dry6b/t4.log`.
- **dry6c.** No open page. 1 `report` open. The same 3 quarantined replies. 1 tick key quarantined and reported (`tester|tick:tests_missing|b_1`). Batch: 1 deferred. Ledger: 179 open, 39 parked. Faults: 3 open. Last log `dry6b/t9.log`.
- **dry7.** 2 open pages (m61, `m_park_12fb7720e8_b1`). 1 `report` open, 1 `question` unresolved (m19). 2 tick keys quarantined and reported. Batch: 1 deferred. `touch_strays`: 1 open, 10 mistake. Ledger: 122 open, 51 parked. Faults: 2 open. Failed sessions: 3, all done again. Last log `dry7/t7c.log`.
- **dry8.** 5 open pages (m52, m54, m57, m58 clarify, m59 present). 1 `report` open, 1 `question` unresolved (m19). 2 tick keys quarantined and reported. Batch: 1 deferred. `touch_strays`: 1 open, 1 mistake. Ledger: 114 open, 51 parked. Faults: 1 open. Last log `dry8/turns/t6_agenda.txt`.
- **blind1.** 1 open page (m4 present). 1 `report` open (m12). No quarantine. No batch. 6 items in `draft`. Ledger: 18 open, 6 parked. Faults: 1 open. Last log `blind1/turns/t4.txt`.

### What the pages and the last logs name (observed)

- No open desk message is in the `body_refs` of any page to the Principal in any run (observed: `b1` page check, `named on pages: []` for all 21 rows).
- The last logs of dry5 and dry6c name the ledger count, the stopped batch and the fault count: "Rota itself failed 1 time this run" (`dry5/t9.log:23`), "failed 3 times" (`dry6b/t9.log:10`). The faults table holds 1 and 3 open rows.
- The last logs of dry6b, dry7, dry8 and blind1 name the open pages and `awaiting_principal`. They name no fault, although 1, 2, 1 and 1 faults are open (observed: grep of the four logs).
- The last log of dry6 says "Stuck: the team could not read a part of the code for news after 3 attempts ... Nothing waits on you, and nothing moves until that is cleared" (`dry6/t5.log:12`). The same log lists `survey n=6` and `commitments n=3` as outstanding (`:14-16`). The 9 failed sessions behind the stall end on `LLMUnavailable` (observed: last turns of s50 to s77).
- The run of that turn printed `run exit 127` (`dry6/t5.log`), and the Principal replies m15 and m16 of that turn stay `open`.

### What the scheduler would wake next (observed: `fr.py` on copies in `eval/`)

The reader ran `scheduler.frontier_readonly` and `predicates.outstanding`
of the current code on copies opened read-only. This is the current
code, not the code of each run.

| run | wakes, principal absent | wakes, principal present | outstanding with a count |
|---|---|---|---|
| dry1 to dry4 | error: no such table `candidate_bindings` | same | every entry errs, except dry4: `tests_failing` bg_1, `unresolved` m69, `awaiting_principal` 1 |
| dry5 | architect `tick:annotate` (b_1, m75), architect `tick:commitments` | same | `commitments` 1 |
| dry6 | 2 liaison `message`, 9 architect `tick:survey`, architect `tick:commitments` | same | `commitments` 1, `survey` 10, `awaiting_principal` 1 |
| dry6b | none | none | `awaiting_principal` 1 |
| dry6c | architect `tick:annotate` (b_1, m44) | that, and liaison `tick:agenda` | `agenda` 1 |
| dry7 | none | none | `awaiting_principal` 2 |
| dry8 | none | none | `awaiting_principal` 5 |
| blind1 | none | none | `awaiting_principal` 2 |

In dry5, dry7 and dry8, `outstanding` has no entry for the unresolved
questions m33 and m19, and no entry for the open reports.

## Part B2: the refusals

### Where a refusal is recorded (observed)

- `tool_calls` holds `fn`, `args_summary` and `seq`. The sandbox logs a call before the door runs, so a refused call is a row, with no outcome (`rota/core/sandbox.py:5356-5408`). Failed sessions write no `tool_calls` rows (observed: 0 rows for 35 failed sessions).
- The refusal text goes to the next prompt as `ERROR <call>: <text>` (`rota/core/runner.py:6701-6711`).
- A committed session with errors gets one more turn, "SESSION ENDED. The runner's account:", with every error in order (`rota/core/db.py:2423-2440`, `runner.py:7059`). This account is the only record of a refusal in the last turn, or in a turn whose next prompt was cut.

### The rule for the pool

A door refusal is an exception raised by a tool function, as the account
line `<fn>: <text>` shows it. The pool excludes four other kinds:

- The runner's repeat refusals. Counts per file: dry1 119, dry2 17, dry3 43, dry4 78, dry5 64, dry6 34, dry6c 2, dry7 109, dry8 60.
- Parse and grant errors, which take the form `ERROR TOOL: ...` or "is not in this role's working set" (about 520).
- `reply cut` and `no call` lines (113).
- `HELD` lines.

For committed sessions the pool is the account. For failed sessions the
pool is the prompts. The pool holds 0 refusals from failed sessions.
The list is ordered by run name (string order), then session `seq`, then
place in the account. Rows of the shared file take the run name dry6b
for session `seq` 137 or lower, else dry6c. The pool is 4,209. The draw
is `random.Random(364).sample(list, 30)` (`draw.py`).

### Calls and refusals, per run and role (observed: `tool_calls` rows / pool rows)

| run | architect | critic | developer | liaison | researcher | terminologist | tester | vision_keeper | total |
|---|---|---|---|---|---|---|---|---|---|
| blind1 | 73/15 | 50/0 | 0/0 | 19/1 | 0/0 | 42/4 | 0/0 | 45/7 | 229/27 |
| dry1 | 506/179 | 293/1 | 276/41 | 265/48 | 0/0 | 229/21 | 214/96 | 1811/174 | 3594/560 |
| dry2 | 155/19 | 75/0 | 104/18 | 66/7 | 0/0 | 95/25 | 60/15 | 109/7 | 664/91 |
| dry3 | 953/489 | 162/9 | 58/7 | 78/14 | 0/0 | 536/88 | 59/20 | 1567/136 | 3413/763 |
| dry4 | 881/434 | 75/0 | 480/97 | 99/5 | 1/0 | 479/44 | 115/35 | 1615/142 | 3745/757 |
| dry5 | 1135/486 | 221/51 | 180/99 | 122/32 | 0/0 | 519/59 | 102/35 | 1584/134 | 3863/896 |
| dry6 | 21/1 | 0/0 | 0/0 | 18/1 | 0/0 | 237/21 | 0/0 | 644/64 | 920/87 |
| dry6b | 486/146 | 68/2 | 0/0 | 23/0 | 0/0 | 321/18 | 0/0 | 1036/91 | 1934/257 |
| dry6c | 56/7 | 0/0 | 68/9 | 28/3 | 4/0 | 25/0 | 149/40 | 62/0 | 392/59 |
| dry7 | 749/91 | 161/1 | 632/78 | 64/6 | 0/0 | 340/43 | 133/33 | 2934/140 | 5013/392 |
| dry8 | 746/89 | 161/1 | 232/60 | 73/4 | 0/0 | 295/29 | 34/7 | 2901/130 | 4442/320 |
| all | 5761/1956 | 1266/65 | 2030/409 | 855/121 | 5/0 | 3118/352 | 866/281 | 14308/1025 | 30209/4209 |

The calls include the reads that the runner sends before turn 1. 1,418
refusals have no line in a later prompt of their session. 283 of them
are in sessions with one model turn. By role, 1,197 of the 1,418 are
the Architect's.

### The draw

The columns are: fact (T true, F false, C cannot be told), route, the
next act, "same" (how many times the same text appears in the session),
and done later.

| # | run, session | role, wake | call | refusal, short | fact | route | next | same | done later |
|---|---|---|---|---|---|---|---|---|---|
| 1 | blind1 s35 | architect, message deliver | model.amend(headline="Refuse negative bill amount", party="liaison", behaviour="deliver", witness="s1") | "a stated commitment cites a witness that [model.witnesses] showed, and only the survey of an area shows one" | T: deliver wake, no model.witnesses call | yes: amend with no party, behaviour or witness | follows route | 1 | no: no constraint with "negative" |
| 2 | dry3 s28 | VK, tick:reconcile | ledger.log(about_ref='about_ref') | "'about_ref' names no row" | T: no row with id `about_ref` | yes: the @-prefixed area name | other call: attest none_found | 5, one turn | no note. Area attested none_found |
| 3 | dry8 s110 | architect, tick:commitments | model.amend(behaviour="tzdata version requirement ...", witness=cc_6f9f39e79088) | "src_icalendar_version already governs this subject" | C: row exists; the guard shares 2 stems, `icalendar` and `version` | yes | session ends, never shown | 2 | no: no constraint with either witness |
| 4 | dry1 s14 | VK, tick:reconcile | surveys.attest(outcome='found') | "you have attested `found` and written no ledger" | T: 0 ledger calls, 0 receipts | yes | same call again | 1 | yes: area survey none_found |
| 5 | dry1 s83 | architect, tick:survey | model.amend(bindings core.py, types.py) | "you have not read src/click/core.py, src/click/types.py this session" | T: types.py never read; core.py first read at call 102 | yes | never shown, session went on | 11 | no: 0 constraints bind types.py |
| 6 | dry4 s14 | VK, tick:reconcile | ledger.log (held) about supports_recurring_events | "supports_recurring_events is the row this note is about, and one side of the note is its own text" | T: assumption equals `items.text` | yes: attest none_found | other: prose with no call | 1 | no note. Area none_found |
| 7 | dry5 s137 | architect, tick:survey | model.amend(headline="test_component_conversion" ...) | "test_issue_1237_jcal_paring_of_known_types already governs this subject" | C: shared stems `jcal`, `test` | yes | never shown, next turn attest | 16 | no: 0 of 7 headlines exist |
| 8 | dry4 s137 | architect, tick:survey | model.amend(bindings prop/binary.py) | "you have not read src/icalendar/prop/binary.py" | T: 0 code.source calls in s137 | yes | never shown, then attest | 6 | no: 0 bind binary.py |
| 9 | dry3 s160 | terminologist, message deliver | glossary.amend(term='caselessdict', sense_short='') | "'caselessdict' has a body and no `sense_short`" | T: sense_short='' | yes | same call again | 24 | no: no glossary row |
| 10 | dry4 s50 | VK, tick:reconcile | surveys.attest(found) | "attested `found` and written no ledger" | T: 5 ledger calls all refused, 0 receipts | yes | follows route: none_found | 1 | yes |
| 11 | dry4 s27 | VK, tick:reconcile | surveys.attest(found) | the same | T: attest is call 8, first ledger.log is call 9 | yes | follows route: ledger.log | 1 | yes: survey found, 1 ledger receipt |
| 12 | dry1 s149 | developer, tick:exhausted | ledger.log(kind='scope', about_ref='tk_1_criteria_waited') | "a change of scope on tk_1_criteria_waited is a question for the Vision Keeper" | T: kind='scope', criteria row exists | yes: msg.question_vision_keeper | session ends | 4 | yes: m52 to VK, answered |
| 13 | dry5 s2 | architect, tick:frame | frame.assign(path='pyproject.toml') | "pyproject.toml is a manifest: claimed mechanically as a boundary already" | C: the one row on it is from s170, a later session | no | session ends, never shown | 1 | yes: s170 surveyed `@surface:pyproject.toml` |
| 14 | dry3 s135 | architect, tick:survey | model.amend(bindings prop/vText.py) | "src/icalendar/prop/vText.py is not a grain in the index" | T: no `code_index` row | yes | other: code.source reads | 2 | no |
| 15 | dry3 s34 | VK, tick:reconcile | surveys.attest(found) | "your ledger.log was refused this session ... a refused ledger is not `found`" | T: 4 earlier refusals, 0 receipts | yes: fix or drop | follows route: none_found | 1 | yes |
| 16 | dry3 s134 | architect, tick:survey | model.amend(bindings src/icalendar/component.py) | "is not a grain in the index" | T: no `code_index` row | yes | other: code.source of 4 paths | 2 | yes: constraint `Component` |
| 17 | dry1 s86 | architect, tick:boundary | surveys.attest(found) | "attested `found` and written no constraints" | T: attest call 5, first amend call 6 | yes | follows route: model.amend | 1 | yes: area none_found |
| 18 | dry4 s131 | architect, tick:survey | model.amend(bindings test_issue_391_url_escaping.py) | "is not a grain in the index" | T | yes | session ends, never shown | 1 | no |
| 19 | dry6b s12 | VK, tick:reconcile | ledger.log(about_ref='about_ref') | "'about_ref' names no row ... takes that file's area id: '@prose:...'" | T | yes | follows route | 6, one turn | no note. Area none_found |
| 20 | dry7 s61 | terminologist, tick:define | glossary.amend(term='event') | "'event' is a kind here, and the sense does not say so" | C: a judgement of the words | yes | follows route: the body names Component | 1 | yes: row at version 2 |
| 21 | dry5 s193 | terminologist, message question | msg.answer_architect(refs=['cw_7039d1d2d899']) | "an answer from the glossary carries a term ... names none" | T: id is a constraint, no glossary row | yes: msg.report_liaison | same call again | 2 | no: m33 stays unresolved |
| 22 | dry7 s92 | architect, tick:survey | model.amend(bindings parser/parameter.py) | "you have not read src/icalendar/parser/parameter.py" | T: 0 code.source calls | yes | session ends, never shown | 8 | yes: 14 constraints bind it |
| 23 | dry3 s160 | terminologist, message deliver | msg.report_liaison(refs=['s1']) | "you have already sent report to liaison ... Your work here is done" | T: m30 exists, caused by m10 | yes: end | same call again | 3 | yes: m30 |
| 24 | dry3 s196 | architect, tick:survey | model.amend(headline="icalendar.<module>" ...) | "icalendar_prop already governs this subject" | C: shared stems `icalendar`, `prop` | yes | never shown, session went on | 58 | C: the headline of the drawn call is not known |
| 25 | dry1 s182 | architect, message deliver | model.amend(bindings termui.py::pause) | "you have not read src/click/termui.py::pause ... `code.source` them first" | T: 0 code.source calls | yes, but the role does not hold code.source | follows route, refused as "not in this role's working set" | 3 | no |
| 26 | dry5 s132 | architect, tick:survey | surveys.attest(found) | "attested `found` and written no constraints" | T: no model.amend in s132 | yes | other: model.describe | 1 | yes |
| 27 | dry7 s9 | VK, tick:reconcile | ledger.log(about_ref='handles_timezones') | "the two halves of this assumption say the same words" | T: the halves are equal in the call text | yes: attest none_found | follows route | 5, one turn | no note. Area none_found |
| 28 | dry7 s16 | VK, tick:reconcile | ledger.log(about_ref='@prose:docs/how-to/parse-errors.rst') | "'@prose:docs/how-to/parse-errors.rst' names no row ... '@prose:docs/how-to/parse-errors.rst' for docs/how-to/parse-errors.rst" | F: the wake refs and the refusal's own list name this id | the route is the refused value | other: attest none_found for index.rst | 1 | no note. Area none_found |
| 29 | dry4 s31 | VK, tick:reconcile | ledger.log(about_ref='generates_ical_data', assumption = the item's text) | "generates_ical_data is the row this note is about, and one side of the note is its own text" | T: assumption equals `items.text` | yes | follows route | 1 | no note. Area none_found |
| 30 | dry5 s135 | architect, tick:survey | model.amend(bindings prop/attendee.py) | "is not a grain in the index" | T | yes | never shown, then attest | 5 | no: `vAttendee` absent |

The evidence rows for the table are in the scripts' output. The main
sources are `tool_calls`, `receipts`, `code_index`, `constraints`,
`constraint_bindings`, `survey_records`, `glossary_terms`, `messages`
and `turns.completion`. "Never shown" means that the refusal is in the
account and in no later prompt. "Done later" for a reconcile note
means a `ledger` row from that file. The area's discharge is written
after it.

## Part B3: rules of records, by query (observed: `b3.py`, `b3.json`)

- **Rows with more than one writing role (receipts).** dry1 1, dry2 2, dry3 1, dry4 2, dry5 6, dry6 0, dry6b 0, dry6c 1, dry7 6, dry8 2, blind1 0. The pairs are: `batches` architect+developer (8 runs), `touch_strays` developer+architect (dry4, dry5, dry7, dry8), `ledger` terminologist+architect (dry2), and `ledger` critic+vision_keeper (dry7).
- **Writes by a role with no `writes` edge in the graph.** The Critic wrote `ledger` rows in 10 runs: dry1 10, dry2 5, dry3 5, dry4 2, dry5 7, dry6b 8, dry6c 8, dry7 3, dry8 3, blind1 4. The Developer wrote `touch_strays` (dry4 19, dry5 5, dry7 11, dry8 2), `batches` (8 runs, 1 each) and `drop_notes` (dry4 1, dry7 1). `graph.json` gives `ledger` writes to VK, architect, developer, terminologist, tester and liaison only.
- **Ledger rows with `author = 'principal'`.** dry4 214, dry5 243, dry6b 200, dry6c 200, dry7 139, dry8 139, blind1 18. Other runs: 0. The rows open with "observed and unconfirmed under the lazy election:". The writer is `rota/core/loop.py:553-555`, an `INSERT` with author `'principal'`, and the rows have no receipt.
- **Artefact rows with no receipt (id-keyed tables).** `entries`: all rows in 11 runs. `constraints`: 1 row in 11 runs. `rulings`: dry1 18/47, dry2 1/10, dry3 5/14, dry4 7/20, dry5 9/22, dry6 1/3, dry6c 1/11, dry7 4/13, dry8 3/10. `tests`: dry1 34/37, dry2 4/7, dry6c 162/163, dry7 162/167, dry8 162/164, with ids that start `inh_`. `ledger`: dry2 1, dry3 1, dry4 216, dry5 245, dry6b 201, dry6c 202, dry7 140, dry8 141, blind1 19. `decisions`: 7 runs.
- **Ids that name rows in two artefact tables.** dry1 3, dry2 4, dry3 19, dry4 19, dry5 19, dry6 0, dry6b 14, dry6c 14, dry7 12, dry8 12, blind1 2. Nearly all are `constraints` with `glossary_terms` (for example `calendar`, `component`). One is `glossary_terms` with `model_areas` (`news`).
- **Rulings.** No run has a ruling with neither `reply_id` nor `verdict_id`. Every ruling has `version = 1`. `ruled_refs_live` shows `outdated` approve rows in dry1 19, dry4 1, dry5 1, dry7 2, plus `outdated` contest 4 and revise 1. These are refs whose version rose after the ruling landed.
- **Approved items amended after approval.** 0 in 11 runs. Every batch rests on an approved item, or on a dropped item with an abandoned batch (dry2).
- **Ledger resolved without a decision that names it.** 1 of 23 resolved rows: dry7 `challenge_constraints_cw_4403c6b62018`, written by critic s128, with a second receipt from vision_keeper s163.
- **Failed sessions.** 35 distinct sessions with `committed = 0` (dry1 8, dry6 15, dry6b 9 that dry6c repeats, dry7 3). All 35 end with "SESSION FAILED", hold 0 receipts and 0 tool calls, and fail on `LLMUnavailable`. Done again on the same trigger: dry1 2 of 8, dry6 6 of 15, dry6b 0 of 9, dry7 3 of 3.
- **Dispatch counts against caps.** Message m5 of dry6 has 7 sessions, 6 of them failed. It ends with `attempts = 1`, `status = 'answered'`, and was never quarantined. The other 6 messages with 3 failed sessions end `quarantined` with `attempts = 3` and `told = 1`. The quarantined tick keys number 13, and all have `reported` of 1 or more. Eleven wake keys had more than 3 sessions and have no `tick_attempts` row. The largest is dry1 `developer|tick:tests_failing|bg_1`, with 10 sessions. Two keys end at 3 attempts with `quarantined = 0` (dry4, dry6).
- **Unresolved questions.** 5 messages end `unresolved` with no `tick:unresolved` session that names them: dry1 m20, dry4 m69, dry5 m33, dry7 m19, dry8 m19. 16 `tick:unresolved` sessions in these runs name other messages.
- **Caps.** No `config` or `config_history` row in any run has `cap` in its key. `config_history` holds 14 to 94 rows per run, and most have the author `loop`.
- **Clock columns.** `finding_rulings.at`, `config_history.at` and `runtime_processes.started_at` exist in 11 of 11 databases. `finding_rulings` holds 12 rows with `at` in dry5, and `config_history` holds rows in every run.
- **Messages with prose.** `body_text` is set on `clarify` pages and Principal replies. It is also set on desk edges: developer>tester challenge (dry1 9, dry2 2, dry4 3, dry5 2, dry7 1, dry8 2), architect>terminologist question (7 runs), and others.

## Part C: the grid

### Statements against the records

| # | statement | B1 | B2 | B3 | reading |
|---|---|---|---|---|---|
| 1 | one writer per row | | | 21 rows in 8 of 11 runs have two roles; 3 runs hold | does not hold |
| 2 | the graph grants each write | | 1 of 30 draws: route names an ungranted call | ungranted writes in 10 of 11 runs | does not hold |
| 3 | the Principal writes no record, no ledger row on his behalf | | | 18 to 243 rows per database in 7 of 11 | does not hold |
| 4 | artefacts carry receipts | | | rows with no receipt in 11 of 11 runs | does not hold |
| 5 | every open obligation stays visible | 11 of 11 runs end with an open class that no page names; 7 of 7 runs with a log have one that the log does not name | 1,418 of 4,209 refusals never shown to the seat | | does not hold |
| 6 | outstanding work re-derived each pass | current code: 7 of 11 evaluated, 4 err | | | cannot be told |
| 7 | identity from content | | | ids in two tables in 10 of 11 runs; content derivation not testable | cannot be told |
| 8 | ruling: Liaison writes it, it carries a version | | | version on every row, 11 of 11; 49 rulings in 9 runs have no Liaison receipt | version holds; writer does not hold |
| 9 | session commits or discards; failed row and error turn | | | 35 of 35 failed sessions hold | holds |
| 10 | past the message cap, quarantine | | | 6 of 7 messages hold; dry6 m5 does not | does not hold, 1 message |
| 11 | a wake past its cap is quarantined and said | 13 quarantined keys, all reported; 9 quarantined messages, all told | | 2 keys at cap not quarantined; 11 keys with more than 3 sessions and no attempt row | holds where rows exist; cannot be told for 13 keys |
| 12 | an unanswered question climbs | 5 unresolved messages in 5 runs | | 0 climb wakes on the 5 | does not hold, 5 messages |
| 13 | every cap is a ruling with a writer and a version | | | 0 cap rows in 11 runs | cannot be told from run rows |
| 14 | ledger resolved only by a naming decision | | | 22 of 23 hold; 1 in dry7 does not | does not hold, 1 row |
| 15 | never rules for the Principal, silence is not consent | | | 0 rulings without reply or verdict | holds by this check |
| 16 | approval before work | | | every batch on an approved item; 0 amended after approval | holds |
| 17 | a door refuses on a fact | | 24 T, 1 F, 5 C of 30 | | does not hold, 1 of 30 |
| 18 | a door names the route | | 29 of 30 name one; 10 followed; 1 route is the refused value; 1 is outside the role's tools | | holds in 27 of 30 |
| 19 | a door never decides a judgement | | 4 of 30 rest on a word test (3 stem overlaps, 1 sense) | | cannot be told, 4 |
| 20 | no clock column | | | 3 clock columns in 11 of 11 databases | does not hold |

### Evidence for each "does not hold"

- **1.** dry7: a `ledger` row with receipts from critic s128 and vision_keeper s163. dry2: a `ledger` row from terminologist and architect. `batches` and `touch_strays` rows carry receipts of both the Developer and the Architect (`b3.json`, `rows_multi_writer_by_table`).
- **2.** Critic sessions hold `ledger` receipts in 10 runs, and `graph.json` has no `critic writes ledger` edge. Draw 25: the route names `code.source`, and the next prompt says "'code.source' is not in this role's working set" (dry1 s182, turn 8 prompt).
- **3.** `ledger.author = 'principal'` in 7 runs. The rows come from `rota/core/loop.py:553-555`.
- **4.** For example dry8: 162 of 164 `tests` rows (`inh_*`) and 141 of 166 `ledger` rows have no receipt.
- **5.** Open `report` messages to the Liaison are in 10 runs, open `deliver` messages are in dry6, and no page names them. Unresolved m33 (dry5) and m19 (dry7, dry8) are absent from the last logs and from `outstanding`. dry7, dry8 and blind1 faults are open, and the last logs do not name them. dry3 has a stale `claims` row (s207). dry6 has replies m15 and m16 open after `run exit 127`.
- **8.** For example dry1: 18 of 47 `rulings` rows have no receipt of any session.
- **10.** dry6 m5: sessions s41 to s46 failed. The message ends with `attempts = 1` and `answered`, and was never `quarantined`.
- **12.** dry1 m20, dry4 m69, dry5 m33, dry7 m19 and dry8 m19 are `unresolved`, and no session has `wake_kind = 'tick:unresolved'` with that id.
- **14.** dry7 `challenge_constraints_cw_4403c6b62018` is `resolved`, and no `decisions` row names it.
- **17.** Draw 28: dry7 s16 refuses `'@prose:docs/how-to/parse-errors.rst'` as naming no row. The same text names that id as the area id of the file, and the session's `wake_refs` hold it.
- **20.** `pragma table_info` shows `finding_rulings.at`, `config_history.at` and `runtime_processes.started_at` in every database.

### B1, one row per run

| run | open pages | open questions between desks | quarantined or capped wakes | batches not merged | faults | failed sessions not done again | open classes that no page and no agenda names |
|---|---|---|---|---|---|---|---|
| dry1 | 0 | 4 report open, 1 question unresolved | 2 replies quarantined, 3 ticks quarantined | 0 | 2 | 6 of 8 | no log; m20, 4 reports, 2 faults, 11 ledger open |
| dry2 | 0 | 2 report open | 0 | 1 abandoned | 2 | 0 | no log; 2 reports, 2 faults |
| dry3 | 0 | 1 report open | 1 tick | 0 | 2 | 0 | no log; 1 report, 2 faults, stale claim s207 |
| dry4 | 1 | 2 report, 1 challenge unresolved | 1 tick quarantined, 1 at cap | 1 running | 1 | 0 | no log; m69, 2 reports, 11 open strays, 1 drop note, 1 fault |
| dry5 | 0 | 1 report, 1 question unresolved | 2 ticks | 1 deferred | 1 | 0 | m33, report m34 |
| dry6 | 1 | 3 deliver open | 1 reply, 1 tick quarantined, 1 at cap | none | 0 | 9 of 15 | deliver m9 to m11, replies m15 and m16 |
| dry6b | 1 | 1 report | 3 replies | none | 1 | 9 of 9 | report m20, 1 fault |
| dry6c | 0 | 1 report | 3 replies, 1 tick | 1 deferred | 3 | 9 of 9 | report m20 |
| dry7 | 2 | 1 report, 1 question unresolved | 2 ticks | 1 deferred | 2 | 0 of 3 | m19, report m20, 2 faults, 1 open stray |
| dry8 | 5 | 1 report, 1 question unresolved | 2 ticks | 1 deferred | 1 | 0 | m19, report m20, 1 fault, 1 open stray |
| blind1 | 1 | 1 report | 0 | none | 1 | 0 | report m12, 1 fault |

The open ledger rows are counted in the last logs of dry5 and dry6c.
The other logs do not count them. The failed sessions not done again
end on triggers that are quarantined and told, or, in dry6, on survey
keys that the log names.

### B2 by role

| role | in pool | drawn | fact true | fact false | cannot be told | names a route | next follows the route | same call again | session ends | done later |
|---|---|---|---|---|---|---|---|---|---|---|
| architect | 1956 | 15 | 11 | 0 | 4 | 14 | 3 | 0 | 4 (and 5 never shown, session went on) | 5 yes, 1 C |
| vision_keeper | 1025 | 10 | 9 | 1 | 0 | 10 | 6 | 1 | 0 | 4 |
| terminologist | 352 | 4 | 3 | 0 | 1 | 4 | 1 | 3 | 0 | 2 |
| developer | 409 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 1 |
| tester | 281 | 0 | | | | | | | | |
| liaison | 121 | 0 | | | | | | | | |
| critic | 65 | 0 | | | | | | | | |
| researcher | 0 | 0 | | | | | | | | |
| all | 4209 | 30 | 24 | 1 | 5 | 29 | 10 | 4 | 5 | 12 yes, 1 C, 17 no |

Six drawn sessions sent a different call, which is not in a column
(draws 2, 6, 14, 16, 26, 28).

## Part D: what the grid does not cover

1. 1,418 refusals (34%) never reach a prompt. The draws show turn-1 refusals that the next prompt cut out with "CUT this exchange" (dry4 s137 turns 2 and 3, dry5 s135, dry1 s83 turns 2 to 9). 1,197 of the 1,418 are the Architect's (observed: `pool.json`, `turns.user`).
2. The same refusal text returns many times in one session: 58 times in dry3 s196, 24 times in dry3 s160, 16 times in dry5 s137 (observed: pool counts per session and text).
3. The run files share turns. dry3, dry4 and dry5 share 418 to 436 turns with the same session id, seq and completion. dry7 and dry8 share 648. 1,027 of the 4,209 pooled refusals have a twin in another file, and 13 of the 30 draws have one (observed: hash comparison of `turns`).
4. The quarantined messages in dry1, dry6, dry6b and dry6c are the Principal's own replies (`verdict` or `converse`). Each of them has a landed ruling on the same page through a later reply, and each stays `quarantined` with `moved_refs = '[]'` (observed: `messages`, `rulings.ask_id`).
5. In 9 databases (dry2 to dry5, dry6b, dry6c, dry7, dry8, blind1), an open fault authored by the Liaison names the falsified claims on the ledger. Examples are dry4 `f_f25fe2ea89`, "require a ruling", and blind1 `f_331692176c`, "lack a ruling". A fault is shown on no page (`schema.sql:795-805`). The `challenges` table holds 2 to 9 `falsified` rows per run (observed: `faults.text`, `challenges`).
6. The dry6 log calls nine `LLMUnavailable` failures "could not read a part of the code" (observed: `dry6/t5.log:12`, last turns of s71 to s77).
7. The dry5 log prints "Stuck: b_1 stops here. It breaks . A new commit on the change starts it again", with no word after "breaks" (observed: `dry5/t9.log:22`).
8. dry6 ends with 3 `deliver` messages open from the Liaison to three desks, and none of them was ever woken (observed: `messages` m9 to m11, status `open`, `attempts = 0`).
9. The repeat refusals of the runner number 526 in the 10 files, and they are not door refusals (observed: account lines "repeat refused:").
10. `config_history` holds 12 to 92 rows per run with author `loop`, and 2 or 3 rows with author `principal` (observed: `config_history`).

## Part E: limits

- The final database shows the end state only. The order of a refusal against a later write is known only through `tool_calls.seq` inside one session.
- `tool_calls.args_summary` cuts each argument at 60 characters. Full arguments came from `turns.completion` where a draw needed them.
- The pool depends on the account turn. A committed session whose account was not written, or an account line with a line break inside, can shift a count. The account and the prompt lines agree for most sessions. They disagree in 2 to 6 sessions per file, mostly where a prompt was cut (observed: `extract.py` cross-check).
- The pool excludes grant refusals ("is not in this role's working set"), parse errors and runner repeat refusals. A reader who counts them as door refusals gets a larger pool.
- The frontier and `outstanding` ran under the current code, not the code of each run, and failed on dry1 to dry4.
- dry1 to dry4 have no last turn log in this read, so their agenda column rests on the pages alone.
- `tick_attempts` keeps no row for a key after a reset, so a dispatch past the cap cannot be told for 11 keys.
- The subject test of the "already governs this subject" door is a stem overlap (`rota/roles/api.py:4412-4460`). The rows cannot say whether two subjects are one.
- For draw 24, the drawn call is one of 58 identical refusals, and its headline is not known. For draw 7, the reader checked all 7 overlapping headlines.
- The reader did not check whether the `.rota/dry*.db` files changed after their runs.
