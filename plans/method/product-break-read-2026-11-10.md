# The break test of claims C1 to C5, 2026-11-10

Written by one adversarial reader for frame 364, step 5 of the product
review. The claims are in `plans/method/product-map-2026-11-10.md`,
"Step 5". The reader changed no file but this page, and started no model
run and no test run. Every database was opened with `mode=ro`.

`S` is the scratchpad folder
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/break/`.
The scripts and their outputs are there: `h.py` (paths), `inv.py`,
`c1_dry.py`, `c1_all.py`, `c1b.py`, `c1q.py`, `c2.py`, `c2b.py`, `c2c.py`,
`c3.py`, `c5.py`, `wh.py`, `lo.py`, and a `.txt` file beside each.

## Result

1. No claim stands whole. C1, C2, C3 and C5 stand in part. C4 falls for
   three of the five fold runs.
2. C1 is too wide. A contest moves the target row in most cases for the
   delivery records. It does not move a glossary row, a constraint or a
   batch row. The quarantined replies are failures of the model server,
   not of the carry down.
3. C2's merge half stands on the nights: 74 merges, each with a pass
   verdict at the head and no red latest run. "No verdict fails" is an
   effect of the dry-run sample: the nights hold 18 fail verdicts, and 16
   got a new commit.
4. C2's test half stands out of sample: 36 criterion tests turned green at
   an unchanged commit in 17 nights, and 12 of them at a merged head. But
   40 of the 46 such turns in all runs follow a Developer challenge, which
   is the designed path.
5. C3's cost half stands for sessions before the first batch start (median
   64% to 69% on the nights), and fails for model time over a whole night
   (14% to 29%).
6. C3's feed half stands on the late nights (3% of delivery prompts carry
   a record's text) and fails on the dry runs (43%).
7. C4 falls as written. In dry runs 7 and 8 the criteria and the Developer
   prompts name `_foldline`, and in dry runs 5, 7 and 8 the commits go to
   `string.py`. The batches stop on mistakes inside `_foldline`.
8. C5 loses its main example. 21 of the 38 failed sessions of the dry runs
   ended with "The model answered a probe". Today's code says "no answer
   from the model" in the loop note when the server is down.
9. The nights are 98 files, and 3 of them are one run: night109,
   night109_cut and night110 have the same turns.

## The two bodies of evidence

- Dry runs: the 11 databases of `product-seat-population-2026-11-10.md`.
  dry6b and dry6c are one file, and a count over "dry" uses dry6c and
  leaves out dry6b where the two would count twice.
- Nights: 98 files `clickI_night*.db`, nights 82 to 175 with partial,
  cut, walk and `164a` files. The file dates run from 2026-09-18 to
  2026-10-28 (observed: `ls`). All 98 were read, so no draw was made. The
  thirds are by night number, not by name: early is night82 to night110
  (33 files), middle is night111 to night144 (33), late is night145 to
  night175 (32).
- 47 of the 98 nights merged at least one batch: early 8, middle 20, late
  19. They merged 9, 26 and 39 batches (observed: `c5_n.txt`, `lo.py`).
- Tables missing on old nights (observed: `inv.txt`): `ruled_refs` before
  night170, `test_run_journal` before night160, `faults` in night82 to night94
  and in night141 to night169, `finding_rulings` before night95,
  `touch_guesses` in most nights before night153.
- The seat of the early nights approved every row: each `rulings.per_item`
  value in night82 to night117 is `approve` (observed: `g6.py`). So no
  claim about a contest can be tested on the early third.

## C1. Rota keeps the person's word and does not carry it down

1. The claim: rota records his words but a landed contest, revise or drop
   does not change the record it targets. It rests on four observations: a
   landed contest leaves its row unchanged (mass 1 grid row 11, 4 pages;
   mass 2 grid row 16, 4 requests), a drop leaves project records
   unchanged and `observed` (mass 4 row 17), his replies are quarantined
   in 4 runs (mass 5 D.4), and a later session rewrote rows he approved
   (mass 6, item 10).
2. Re-check of the heaviest rows (observed: `c1_dry.txt`, a join of
   `ruled_refs` and `rulings` on `status='landed'` and `verdict in
   ('contest','revise') or act='drop'`):
   - dry5 r_m61_2 and r_m62_2 revise c_1 and c_3. Both are version 1, and
     `rulings.texts` equals `criteria.text`. The read pages read this row
     correctly.
   - dry3 r_m20_2 contests `alarm#src_icalendar_tests_events` with act
     `remove`. The glossary row is version 1, and no row has `supersedes`
     on it. Correct.
   - dry6c r_m27 contests `guess:folds_long_lines_in_icalendar`.
     `touch_guesses` holds only rows with `ruling_id=''`. Correct.
   - Mass 2 grid row 16 also says that the contest re-derives in 4
     requests (R1, R3, R9, R10). The map's C1 kept the 4 that fail and
     left out the 4 that hold.
3. Counter-cases in the dry runs. 90 landed contest, revise or drop rows
   are in `ruled_refs` (observed: `c1_dry.txt`). The target moved, by a
   higher version, `retired_by`, a dropped state, a resolved ledger row or
   a ruled guess set, on these:
   - criteria 6 of 10: dry1 terminal_check v1 to v2; dry6c c_2, dry7 c_1
     to c_3 and dry8 c2 have `retired_by` the ruling. dry5's 4 do not move.
   - tests 7 of 10, items 7 of 8, statements 4 of 6 (s4 to s7 `dropped`;
     s2 and s3 stay `ratified`), ledger 4 of 4 (`resolved`).
   - guesses 3 of the 4 fold runs that contested one: dry5 (ruled set
     `m38`), dry7 and dry8 (ruled set `m26`). dry6c did not (observed:
     `g.py`, `touch_guesses` by `ruling_id`).
   - Did not move: constraints 0 of 15 (all dry1 r_m147), glossary rows 1
     of 14, batch rows 0 of 6.
   - So delivery records moved on 31 of 44 rows, and glossary, constraint
     and batch rows on 1 of 35.
4. The nights (observed: `c1_all_n.txt`). Moved means a receipt that raises
   the row's version from a session after the ruling's session, a
   retirement, a drop, a resolved ledger row, or a ruled guess set.
   Middle and late thirds together:

   | target | contested refs | moved |
   |---|---|---|
   | criteria | 531 | 362 |
   | tests | 32 | 15 |
   | items | 212 | 209 |
   | ledger rows | 932 | 932 |
   | guesses (late only) | 47 | 45 |
   | statements | 51 | 12 |
   | constraints | 557 | 85 |
   | glossary rows | 45 | 4 |
   | batch rows | 94 | 0 |

   The early third holds no contest. A contested item also cancels its
   batch: 41 of the 63 abandoned batches of the middle and late thirds
   have an item with `approval='contested'` (observed: `lo.py`).
   The quarantined replies: all 6 distinct quarantined messages from the
   principal in the dry runs (dry1 m4, m5; dry6 m8; dry6b m8, m14, m17)
   had three sessions each, and every one failed with `LLMUnavailable`
   (observed: `c1q.py`). The nights hold 4 such messages in 98 files.
   The rewrite after approval: a second version-raising session after an
   approve hit 5 of 35 glossary rows and 2 of 17 constraints in the dry
   runs, and 115 of 1,369 glossary rows and 14 of 904 constraints on the
   nights (observed: `c1b.py`; reasoned: the first raise is the adopt of
   the approval, as s166 in mass 6). Of the items rewritten after an
   approve, 636 of 664 on the nights are approved again at their new
   version.
5. Other readings that the rows support:
   - A contested project-model row is meant to stay as it is.
     `predicates.py:702-706` says "a contested one stays, and it is on
     file as contested" and that asking again spends his attention. The
     word is kept in `ruled_refs`, which never changes
     (`schema.sql:885-889`).
   - The constraint and glossary tables have no column that holds a drop
     (`schema.sql:202-228`, `:254-264`). Items and statements got one in
     frame 357 (`schema.sql:39-42`, `:57-58`), and dry1's later drops of
     s4 to s7 did land as `dropped`. So r_m147's 15 unchanged constraints
     show a table with no drop state, not a lost word.
   - A new row beside the old is the design for a guess: "A correction
     writes a new set beside the old one" (`schema.sql:403-407`).
   - The quarantined replies are a failure of the ground. The words were
     landed through a later reply on the same page in each case (mass 5
     D.4), so the cost is a second page, not a lost word.
6. Verdict: stands in part. The part about glossary, constraint and batch
   rows stands on both bodies. The part about the delivery records and
   the quarantine falls. The true sentence: "A contest, revise or drop
   changes the criteria, tests, items, ledger rows and guesses it names
   in most cases, and almost never changes a glossary row, a constraint
   or a batch row, which have no state for it."

## C2. The gate of the merge is sound, and what the gate reads is not

1. The claim: the merge conditions decide every merge, but the tests and
   reviews that the gate reads are weak. It rests on mass 3 grid row 18
   (9 of 9), row 2 (0 of 7), row 4 (1 of 8), the 6 batches with a turn to
   green at an unchanged commit, "no batch has a fail verdict", and mass
   4's dry8 Critic verdict that falsified a true statement.
2. Re-check (observed: `c2_dry.txt`). The dry runs hold 4 verdicts, all
   `pass`, and 0 `fail`. The 3 merged batches each have a pass verdict on
   the head, no red newest run and no open stray at the head. dry5 holds
   12 `violated` findings and 12 `dismissed` rulings, and 0 sessions of
   `tick:finding_violated`. 10 criterion tests of 25 turned from red to
   green at one commit, and all 10 have `version > 1`. The read page is
   right on the rows.
3. Counter-cases in the dry runs:
   - 3 of the 10 turns are on criteria of the kind "as before": dry3 c2
     and c3 on the base commit 99619246, and dry8's one (observed:
     `c2b.py`, the criterion text). A test of kept behaviour passes on the
     base by design.
   - 7 of the 10 follow a Developer `challenge` that names the test, 1 a
     contest of the principal, 2 have no cause found (observed: `c2c.py`).
   - The violated findings of dry5 did not wake the Developer because the
     Critic dismissed all 12. `predicates.py:1927-1948` wakes the Developer
     only on an upheld finding (ruled: Roman, frame 88, 2026-09-27).
   - A test whose assertion follows from its criterion: not checked by
     query. The judgement of mass 3 row 2 is one reader's and is not
     re-tried here.
4. The nights (observed: `c2_n.txt`, `c2b.py`, `c2c.py`):
   - Verdicts: pass 14, 26, 40 and fail 3, 0, 15 by third. After the 18
     fails, the batch got a new head on 16, a later pass verdict on 8,
     and the batch ended merged 8, abandoned 4, deferred 3, running 3.
     74 Developer sessions woke on `tick:verdict_failed`.
   - Findings: 23 violated (21 early), 2 `tick:finding_violated` wakes.
   - Merges: 74 merged batches. 74 have a pass verdict at the head, 0 a
     red newest run, 0 an open stray at the head.
   - Turns to green at an unchanged commit: in the 17 nights with a
     journal (night160 to night175 and night164a), 36 of 122 criterion
     tests with runs. 12 of the 36 are at the merged head, in nights 162,
     170, 173, 174 and 175. 33 of the 36 follow a Developer challenge
     that names the test. 2 are on a criterion of kept behaviour. The
     earlier nights keep only the live run per test, so this cannot be
     told on them.
   - The Tester calls `code.*` in 11 of 272 Tester sessions early, 38 of
     472 middle and 341 of 728 late.
5. Other readings:
   - The briefs tell the Tester to read the code. `tester/answer.md:11`:
     "call the function its surface names after you read it with
     `code.source`". `tester/challenge.md:7` says the same for a failed
     call. So "the Tester reads the code" is the brief of today, and the
     statement "Tester never sees the code" of mass 3 row 4 is older than
     the brief.
   - A test written again after the Developer's challenge is the designed
     answer: the challenge goes to the Tester, and a green newest run
     answers it (`predicates.py:1595-1606`). Whether the new test is right
     is a judgement no query makes.
   - "No fail verdict" is a sample effect: the 9 dry batches hold 0 of
     the 18 fails that the nights hold.
6. Verdict: stands in part. The gate half stands on 77 of 77 merges. "No
   verdict fails" falls. The rest stands as a description of the rows,
   with the designed path named. The true sentence: "The merge
   conditions held on every merge in both bodies. A merge can rest on a
   test that turned green when it was written again after a Developer
   challenge, which happened at 12 merged heads on the nights."

## C3. The model of the project costs half of a run or more and feeds the delivery little

1. The claim: onboarding wakes are most of the work before the first
   batch start, and the delivery desks read few of its records. It rests
   on mass 2 Part D.1 (48% to 81%) and mass 4's 0 of 40 drawn records.
2. Re-check (observed: `c3_dry.txt`). With the onboarding kinds of mass 2
   plus `tick:annotate` and `tick:observed_entries`, the share before the
   first batch start is dry1 92 of 144, dry2 29 of 54, dry3 142 of 179,
   dry4 141 of 177, dry5 167 of 206, dry6c 112 of 151, dry7 124 of 153,
   dry8 124 of 156. The counts agree with mass 2 within 3 sessions.
3. Counter-cases in the dry runs:
   - By model time (`turns.ms`), onboarding is 20% (dry2) to 85% (dry3)
     of a run, and 53% over all 11.
   - 80 of 185 delivery sessions carry a glossary sense or a constraint
     headline of 25 or more characters in the first prompt, and 22 carry
     a pushed list of glossary rows (observed: `c3.py`). dry7 alone has 38
     of 43. In dry8, s177's prompt holds "[glossary.lookup]" with the row
     `fold` and its sense.
   - The 40-record draw of mass 4 held 14 challenges and no area row. A
     challenge is a record no delivery desk is meant to read.
4. The nights (observed: `c3_n.txt`):

   | third | onboarding share before first batch, median | runs at 50% or more | onboarding share of model time | delivery prompts with a record's text |
   |---|---|---|---|---|
   | early | 65% | 30 of 30 | 29% | 171 of 998 |
   | middle | 64% | 28 of 32 | 28% | 308 of 1,326 |
   | late | 69% | 31 of 31 | 14% | 51 of 1,765 |

   Five nights have no batch start. Over a whole night, onboarding is 30%
   to 38% of the sessions.
5. Other readings:
   - A record reaches a desk through a pushed key, not a load call. The
     runner puts `[glossary.lookup]`, `[references.load]` and
     `[model.load]` blocks into the prompt, and `tool_calls` records them
     with empty arguments (observed: dry2 s64, dry8 s177). A count of
     load calls by the model misses them.
   - "Feeds little" cannot be split from "is used little". No query here
     tells whether a session acted on the text it carried.
   - The nights reuse one onboarding of clickI each night. Their share is
     not independent of the code of each night.
6. Verdict: stands in part. The cost half stands for sessions before the
   first batch start, and falls for model time. The feed half stands on
   the nights and falls on the dry runs. The true sentence: "Onboarding
   wakes are about two in three of the sessions before the first batch
   start on both bodies. The text of the project model reaches 3% to 23%
   of the delivery prompts of the nights and 43% of those of the dry
   runs, and no record shows its use."

## C4. The fold request stops on a fact that the person gave and that did not arrive

1. The claim: in the fold runs the guess names the wrong file, he names
   `_foldline` in `string.py`, the criteria still name `q_split` in
   `parameter.py`, the commits go there, a stray is judged a mistake and
   the batch parks. It rests on mass 2 row 10 and Part D.4, mass 3's end
   states, and mass 7 Part D.
2. Re-check (observed: `g2.py`, `g3.py`):
   - Criteria surfaces: dry4 6 of 6 `parameter.py::q_split`, dry5 3 of 3
     `q_split`. dry7: live c1 `q_split`, live c2 and c3 version 2
     `string.py::_foldline`. dry6c 3 of 3 `to_ical`. dry8 3 of 3
     `string.py::_foldline`.
   - `batch_touch` names `src/icalendar/parser/string.py` in all 5 fold
     runs before any contest.
   - The commits: only dry4 has strays on `parameter.py` (7 commits) and
     `parameter.py::q_split` (4 commits), all `open`. dry5, dry7 and dry8
     strays are all inside `string.py`. dry6c has no commit after the
     base (head 99619246 is `claimed_head`).
   - The mistakes: dry4 7 on `_foldline`; dry5 1 on the removal of
     `assert "\n" not in line`; dry7 10 on the removal of the escape
     branch or `foldline = deprecate_for_version_8(_foldline)`; dry8 1 on
     the removal of the assert.
3. Counter-cases. In dry8, 14 of 14 Developer first prompts name
   `_foldline` and `string.py`, 0 name `q_split`, 6 name "#1501" and 3
   name "keep the line assert" (observed: `g4.py`). In dry7, 27 of 35
   name `_foldline` and 7 name `q_split`. In dry5, 4 of 11 name "#1501".
   So in dry8 his facts on the file and on the kept lines reached the
   Developer, and the batch still stopped on a mistake inside
   `_foldline`.
4. The nights are clickI and hold no fold request, so the claim cannot be
   told on the nights. The general form, a contest of the guess that does
   not reach a new guess, can: 45 of 47 contested guesses of the late
   third got a ruled guess set (observed: `c1_all_n.txt`).
5. Other readings. The stop of dry5, dry7 and dry8 is a removal inside the
   right function that he had told the team to keep (dry5 m43, dry8 m30,
   in mass 2's R6 and R10). That is a different fact from the file. The
   guess at signoff and `batch_touch` are two records (mass 2 Part D.3),
   and the second was right from the start.
6. Verdict: falls for dry5, dry7 and dry8, and stands for dry4. dry6c
   stops on a criterion with no test. The true sentence: "In dry4 the
   criteria and commits went to `parameter.py`. In dry5, dry7 and dry8
   the commits went to `_foldline`, and the batch stopped when a
   Developer removed lines of `_foldline` that he had asked to keep."

## C5. Rota says that it stopped, and not truly why

1. The claim: a model-server failure shows as "the team could not read a
   part of the code", last words disagree with rows and no row keeps
   them, a fault shows on no page, 5 questions end unresolved with no
   climb, and no instrument measures the stop for a whole request.
2. Re-check (observed: `c5_dry.txt` and the probe query in the session):
   the 38 distinct failed sessions of the dry runs all end in
   `LLMUnavailable`. 21 of them end with "The model answered a probe, so
   the failure is the wake's own" (dry6 12, dry6b 9). 3 are "actively
   refused" (dry7). 14 are "no answer in 300s" with no probe note (dry1
   8, dry6 6). The read of mass 6 says no row keeps the last words. That
   is a mis-read: `turns.completion` keeps them, for example dry7 s195
   seq 13, "The mistaken removal of the space-folding logic in `_foldline`
   has been restored". What holds is that no door and no page reads them.
3. Counter-cases. In dry6, the server answered the probe, so the survey
   wake of `news` itself failed 3 times. "The team could not read a part
   of the code for news after 3 attempts" then names the failed wake
   truly, and leaves out the 300-second limit. Today's code gives back
   the attempt when the probe is refused or silent and writes "no answer
   from the model, waited {wait}s" in the loop note (`runner.py:7079-7083`,
   `loop.py:399-408`). The dry7 sessions show no probe note, so their run
   came before that path or did not take it (reasoned: the note is
   missing from all 3 rows).
4. The nights (observed: `c5_n.txt`):
   - Failed sessions: early 0 (the early files hold no uncommitted
     session, so this cannot be told), middle 4, late 27. 26 are
     `LLMUnavailable`, 21 of them refused. So a server failure is rare on
     the nights: 31 failed of 28,803 sessions.
   - Unresolved questions: 24, and 3 have a `tick:unresolved` session that
     names them.
   - Open faults at the end: middle 17, late 226. The early files have no
     `faults` table.
   - Page texts are not stored, so the words of a stop on a page cannot
     be told on the nights.
5. Other readings:
   - A fault is meant for the builders, not the person. "No page shows the
     row, and no seat answers it ... the cockpit, the night report and the
     state view read the open rows" (`schema.sql:795-805`).
   - The no-climb rule is the code's. Four of the five dry questions
     (dry1 m20, dry5 m33, dry7 m19, dry8 m19) are Architect to
     Terminologist, and their thread already holds the architect, the
     terminologist, the liaison and the principal. The ladder goes quiet
     when every rung has spoken, on the premise that "Liaison has sent"
     (`predicates.py:1562-1567`, `:1614-1621`). dry4 m69 has only the
     Developer in its thread and its test is red, so it is a no-climb that
     the rule does not explain.
6. Verdict: stands in part. The server example falls for 21 of 38
   sessions and has a fix in today's code. The no-climb half stands on
   both bodies, with the thread rule as its stated cause. The true
   sentence: "A stop shows on a page by the wake that failed, not by the
   limit or the rule that caused it, and 21 of 24 unresolved questions on
   the nights did not climb."

## What holds

The two weakest statements, tried the same way.

1. "A session commits or discards." No receipt belongs to an uncommitted
   session in any of the 10 dry databases (1,858 sessions) or the 98
   nights (28,803 sessions) (observed: `wh.py`). The runner's discard
   notes exist in dry4 and dry7 (mass 7 B.5). The early nights hold no
   uncommitted session, so their failure path cannot be told. Verdict:
   stands at the rows.
2. "22 of 38 sessions leave a record that a later act uses." The draw
   held no failed session. In the population, a committed session writes
   at least one row in 1,348 of 1,820 dry sessions (74%) and 18,891 of
   28,772 night sessions (66%) (observed: `wh.py`). "A later act uses"
   cannot be told by query. Verdict: stands in part. About two in three
   sessions write a row. The use rests on one draw of 38.

## What the claims leave out

1. The merge rate rose over the nights. Nights with a merge: 8 of 33, 20
   of 33, 19 of 32. Sessions per merged batch: 906, 404, 260 (observed:
   `c5_n.txt`, `lo.py`).
2. Early nights end with work in the middle. 51 of 72 early batches are
   `pending` or `running` at the end of the file, against 21 of 102 late
   (observed: `lo.py`).
3. A contest stops work by cancel. 41 of 63 abandoned batches of the
   middle and late nights have a contested item, and abandoned batches
   (63) are close to merged ones (65) in those thirds (observed: `lo.py`).
4. A fail verdict is followed by a fix: 16 of 18 got a new head, and 8 of
   the 18 batches merged (observed: `c2_n.txt`).
5. Open records at the end grow late: 226 open faults in the late third
   against 17 in the middle, and 334 open `report` messages to the
   Liaison on the nights (observed: `c5_n.txt`). No claim says whether
   these hold a merge.

## Limits

- "Moved" in C1 is an upper bound. A version raise by a later session can
  have another cause than the ruling, for example a new survey of the
  same constraint. The statement rows count only a state change.
- The nights' seat is a script that says yes or an agent. The contests of
  the middle and late thirds are an agent's, not a person's.
- Night109, night109_cut and night110 have the same turns (observed:
  count, length and time of `turns`). Night103 and night104 differ in
  turns. The 98 files hold 96 distinct runs.
- The text match of C3 uses glossary senses and constraint headlines of
  25 or more characters. A shorter sense, as dry8's `fold`, is missed
  unless it comes as a pushed list. The pushed-list pattern found no
  match on the nights, so their format may differ, and the night counts
  can be low.
- The onboarding kinds are mass 2's set plus two. The grouping is the
  reader's.
- Whether a test follows from its criterion, and whether a re-encoded test
  is right, were not judged.
- No turn log and no page render were read. Statements about page words
  come from the read pages.
