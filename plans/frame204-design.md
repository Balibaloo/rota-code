# Frame 204 design: what a seat's note is for, who answers it, and whether a merge waits on it

Read-only design pass, Opus, 2026-10-11, an agent of session c81dd240, brief
`scratchpad/design204_brief.md`. Rota workflow throughout, except the costs
and the passes, which are meta workflow. Line numbers are read on the working
tree of 2026-10-11. That tree holds the uncommitted edits of frame 200's pass
2c and frame 203's pass 1 in `api.py`, `sandbox.py` and `db.py`, so a line
can move by a few rows before the build (observed: `git status`, 2026-10-11).

Two facts about the brief itself. The briefs live in `rota/roles/prompts/<role>/<mode>.md`
with the tool lists beside them in `<mode>.tools`, not under `rota/roles/briefs/`
(observed: `ls rota/roles/prompts`, 2026-10-11). Rota has no Gate Keeper seat.
"gatekeeper" was the Vision Keeper's name until DECISIONS of 2026-08-23
renamed it (observed: `rota/DECISIONS.md:252-267`). Section 8 tests the
Gate Keeper note on the Vision Keeper's scope gate.

## 0. Changes in pass 2

Pass 2 folds in the nine findings of `plans/frame204-design-review.md`, 2026-10-11. The coordinator's nine points map onto them. Each line says what changed and where.

1. Review finding 1, high, the fallback holds the merge on a page. **Changed.** Under `merge_gate = auto` nothing holds a merge on a page. A conflict row on a pair with no edge holds nothing, parks at the merge, and shows in the shipped line and on the night read. A new edge or an owner mode is a composition question, held in section 11 until a night shows such a row. Sections 3.1, 4, 5 and 11.
2. Review finding 2, high, a quarantined message holds a batch for ever. **Changed.** The hold reads only messages that a seat still owes: `open`, and `unresolved` while the `unresolved` predicate still names a next rung. A `quarantined` message and a triage-made `unresolved` message hold nothing, so the hold ends with no write and no person. The `Stuck` line for the hold is removed. The existing `quarantined` predicate tells the principal, and his answer lands as new work on top. Sections 3.2 and 4.
3. Review finding 6, high, the `faults` table has no reader and no discharge. **Changed.** Pass 1 adds `faults` to the cockpit snapshot (`rota/cockpit/server.py`), to `rota/tools/nightreport.py`, and as one count line to `render_state`. The table has `status` (`open`, `closed`) and `closed_by` (the build frame's number). The build session discharges a fault, through one operator command. Sections 7 and 10.
4. Review finding 5, the counts. **Changed.** The predicate holds 0 of 6 merges on nights 136 to 139 by its ledger half and at most 2 by its message half (observed: the review's `q2.py` to `q4.py`). The corpus's 131 rows count readers, and 117 of them need a reader and no hold. Section 4.1 gives the split per category and per night. Pass 2 adds a seam night on night 138's `c_1` pair so that the hold measures something, and its ratio runs over four nights. Sections 4.1 and 10.
5. Review findings 3 and 4, the generalisation. **Changed.** A third question comes first: is the obstacle a rule of rota or the content of a row? A tie-break orders two cells. A note about a file path reaches its batch through the writing session, by the park's route, for the hold and the park alike. Sections 4 and 8.
6. Review finding 8, the stale cases. **Changed.** Pass 1 names 57 cases by mode, read from `tests/rota/cases/*.yaml`, and prices them at about 6 card hours. Frame 200's two seat cases are on the list. Section 10.
7. The wait, verdict 7 of the review. **Changed.** The shape is named in the composition's body words, "Each seat wakes cold, acts once, and ends" and "A seat restarts from records". The Open section's same-session sentence stays tentative and unbuilt. No question is needed. Section 3.2.
8. Review finding 9, the questions. **Changed.** Q1 and Q3 are dropped, with the records' answers quoted. Q2 stays as a story rated medium. The fixes create one held question, the composition question of item 1, rated low and not asked now. Section 11.
9. Review finding 7, pass 5 and the three unrouted pairs. **Changed.** The corpus holds 0 conflict notes on the three pairs. Pass 5 is removed from the plan. The design parks such a row and counts it on the night read, and section 11 holds the composition question. Sections 3.1 and 10.

## 0b. Changes in pass 3

Pass 3 folds in two rulings of 2026-10-11 and one judged point.

1. Ruling 1: "Start as written" (ruled: Roman, 2026-10-11 15:44, by `AskUserQuestion`). The design stands as one piece. No section changes for it.
2. Ruling 2: "Every default" (ruled: Roman, 2026-10-11 15:49), changed to "Maybe change this, add an investigation task post 179" (ruled: Roman, 2026-10-11 16:01). Section 6 and pass 4 keep the rule: only a default on constrained code goes to the Architect's structural review. Section 6 records both lines. Section 9's law 8 line is now ruled, with the new wording. Section 11 closes Q2. Section 12 gains item 6, the investigation frame after frame 179, which the holding session pushes on the stack.
3. Judged point: the `ledger.log` door turns a bare `scope` log into an offer of `msg.question_vision_keeper`, as it does for `conflict`, so a scope row never stands with no message beside it. Section 2's row 4, section 4 and pass 2's files.

## 1. The problem in rota's terms

1. A note is a row of `ledger` (`rota/core/schema.sql:552-562`). It has a
   prose column `default_taken`, a `kind` of `default` or
   `unaddressed_answer`, and a status of `open` or `resolved` (observed).
2. A seat writes one through `ledger.log` (`rota/roles/api.py:7811-7932`).
   Twenty modes offer the call, and 18 brief lines invite it, for example
   `developer/batch_start.md:42` and `terminologist/relay.md:14-15` (observed: `grep`, 2026-10-11).
3. Six code paths write a note with no seat's own words: the two
   `tests.encode` doors (`api.py:6996-7012`, `api.py:7031-7043`),
   `challenge.break` (`api.py:10224`), `challenge.vacuous` (`api.py:10277`),
   `frame.assign` (`api.py:10437`), `ledger.unaddressed` (`api.py:7948-7977`)
   and the lazy election in `loop.py:500` (observed).
4. Nothing reads a note except the principal's page. `tick_agenda`
   (`rota/core/scheduler.py:1024-1108`) puts up to 7 open rows on a page,
   `render_page` (`rota/roles/principal.py:1242`) numbers them, and only
   `principal.land` (`principal.py:1814`) or a seat's `decisions.author`
   with `resolves_ledger` (`api.py:8073`) closes one (observed).
5. The corpus holds 583 fresh notes on nights 120 to 139 (observed: `plans/frame204-corpus.md`, section 0).
6. A real pick in the seat's own words is 39 of 583, 7%. Doors dictate 103 and code writes 44.
   Relay wakes echo a ruling 221 times, seats log 95 tool faults and 65 work logs (observed: the same, section 1).
7. 496 of 583 reached a page. A seat read a note back in 4 of 567 (observed: section 3).
8. The principal contested 38 tool faults as if they were assumptions (observed: section 3).
9. About 131 of 583, 22%, need a reader before a merge (reasoned: the corpus, section 5).
10. So the ledger is today the only free-text channel a door accepts from a
    seat. It mixes disclosures, questions, faults and logs on one page, and
    nothing in it holds a merge (observed: `lifecycle.mergeable`,
    `lifecycle.py:430-513`, reads no ledger row).

## 2. The categories, settled

The table keeps the grid's eleven categories (`plans/frame204-categories.md`, section 3).
Counts are fresh notes over nights 120 to 139. A count marked "about" is the grid's split of a corpus mass, and it is (reasoned).

"Holds the merge" applies Roman's answer to the diary story: "thats where the
categories of note come in because some categories do and some don't"
(ruled: Roman, 2026-10-11 15:00).

| # | Category | Definition | Count | Example, verbatim | Who must say so if wrong | Holds the merge | What discharges it | Named at log time |
|---|---|---|---|---|---|---|---|---|
| 1 | Invented value | A literal that a test or the code chose where the material gives none. | about 80: 73 of mass B, and a few of C | "test chooses name, age, Alice" | The criterion's owner, the Terminologist. The principal only if he asks. | No | Nothing. It is a disclosure, and it stays countable under its request. | The `tests.encode` door names it. A Developer's names it with `invented`. |
| 2 | Default behaviour | A behaviour that a seat chose where the criteria are silent. | about 40: about 30 of B, and C | "Preserved existing 'one-retry' behavior by restoring the break statement, as criteria are silent on this edge case" | The principal is final. The criterion's owner can say that the criterion covers it. | No | A principal keypress on a numbered line, or a later amendment that supersedes the row's subject. | Yes, `default`. The returns door names its own. |
| 3 | Conflict | Two rows with owners disagree, and the seat built to one side or stopped. | 9 | "The criterion c_1 states separators=(",", ":") but the test expects spaces after colon; assuming the test expectation is correct" | The owner of one of the two rows, never the principal first. | Yes, while an owner seat asked through an edge still owes the answer. Under `auto` a row on a pair with no edge holds nothing (pass 2, review finding 1) | The owner's answer: an amended row, or a decision that names which row stands. | Yes, `conflict`. The door turns it into a message to the owner. |
| 4 | Scope change | The seat left out part of the asked work, or added work the asked work needed. | about 5 | "The confirm function does not exist in the current codebase; its implementation is out of scope for this batch" | The Vision Keeper owns scope. The principal is final. | Yes, when the change departs from the item's own words. | The Vision Keeper: "build it", or an amendment through law 9. | Yes, `scope`. The door turns a bare `scope` log into `msg.question_vision_keeper`, as it does for `conflict`, so a scope row never stands with no message beside it (judged: pass 3). A mode with no such call writes the row, which holds nothing, as a conflict on a pair with no edge |
| 5 | Blocked by the record | A ruling or a relay names a row that the record does not hold, so the seat cannot act. | 68 | "Adoption of c_6 blocked because the ruling names an ID that exists in criteria but not in glossary_terms" | Nobody in rota. The build session, because the cause is in rota. | No | A fault report to the operator, read on the night read. | Yes, `blocked`. |
| 6 | Tool fault | A door refused, or the environment failed. | 27 | "two tests in one file overwrite each other on disk" | Nobody in rota. The build session. | No | A fault report to the operator. | Yes, `fault`. |
| 7 | Trace | A step, a plan or a state. No choice. | 65 | "Adding default_on_eof parameter to confirm() function signature" | Nobody. | No | Not written. | Not offered. |
| 8 | Echo | A seat restates a ruling that reached it. | 221, 207 before commit 2dace61b | "The principal contests the criterion, and no action is required here" | Nobody. | No | Not written. The door at `api.py:7869-7875` refuses it. | Not offered. |
| 9 | Finding | A judgement on an onboarding claim, with a quoted source. | 24 | "the Critic falsified items:echo_json_compact_v2 against @claim:items:echo_json_compact_v2: the probe for def echo_json returned an empty list" | The claim's owner, and the principal rules today. | No. It holds an adoption, not a merge. | A principal keypress on the onboarding page. | The door names it. |
| 10 | Gap | A survey gap, one word for an area. | 16 | `surface` | The principal reads it. | No | A principal keypress on the onboarding page. | The door names it. |
| 11 | Unaddressed | The principal's answer did not touch the row. | 20 | "Should echo_json(obj) be added as a helper next to echo?" | The principal. | No | The principal's next answer. | The door names it. |

Where the grid and the corpus disagree with a category:

- **Scope change takes the grid's predicted "necessity" kind.** `developer/challenge.md:9`
  asks for "it had to be there", which is scope in the other direction. Both
  depart from the item's words, and both have the Vision Keeper as owner, so
  one category holds both (reasoned: one owner, one discharge).
- **Conflict splits by owner.** DECISIONS of 2026-09-12, point 4, rules that two documents of the project that disagree "always ask" the principal (`rota/DECISIONS.md:1392-1395`).
  Such a conflict has no owner seat, so it lands in the cell "owed to the principal, could not choose", beside unaddressed.
  The grid's conflict row covers rota rows with owners only (reasoned: the grid, section 5, against the ruling).
- **Default hides in the invented-value template.** About 30 of the door's
  103 notes name a behaviour, an exception type or a return type (observed:
  the corpus, section 5). The returns door at `api.py:6996-7012` writes
  "returns what it prints", which is a behaviour. So that door names
  `default` and the literal door names `invented` (reasoned).
- **The masses C, D and F each hold 5 to 8 misfiles** (observed: the corpus, section 1).
  About 3 tool faults and 5 work logs hide a pick (observed: the corpus, section 5).
  Section 10's residue rule reads them.
- **Two code writers are not in the corpus.** `frame.assign` writes rows with author `frame`, and the lazy election writes rows with author `principal`.
  The corpus counts the six seat authors only (observed: the corpus, section 0).
  This design places the first as a default at onboarding and the second as a gap (reasoned: their texts at `api.py:10440` and `loop.py:496`).
- **The 950 Vision Keeper onboarding lines are not placed** (observed: frame 204's block, 14:34).
  Most are `how_it_works` defaults that `vision_keeper/deliver.md:23` asks for at intent time.
  A pass 1 count places a sample of 50 before the set is called complete.

The rule that the table follows: **a note that fills a silence never holds a
merge, and a note that says the change contradicts an owned row holds it
until the owner answers** (reasoned: categories 1 and 2 fill a silence,
categories 3 and 4 contradict a row, and the rest are not about the change).

## 3. The routes

Roman's question at 15:06, "notes can come from many sources and seats cant
escalate to everyone? is that right?", is answered yes. The graph fixes the
edges, and law 3 derives them once at load (observed: `rota/LAWS.md:121-146`;
`rota/design/graph.json`, 56 message edges, `contact_exceptions` empty, 2026-10-11).

### 3.1 The routes for a conflict

The route is from the seat that holds both rows at build time to the owner, with the batch waiting (ruled: Roman, 2026-10-11 15:00, the two builders story).

| Finder, mode, moment | The two rows | Owner to ask | Edge in the graph | Tool in the mode today | Change |
|---|---|---|---|---|---|
| Developer, `tests_failing`, fix wake | a test and its criterion | the Tester for the test, through `challenge` | `developer -> tester challenge`, exists | yes, `developer/tests_failing.tools` | none |
| Developer, `tests_failing`, fix wake | a criterion and the item, or a criterion with two readings | the Terminologist, or the Vision Keeper | `developer -> terminologist question` and `developer -> vision_keeper question`, exist | no | add both calls to `developer/tests_failing.tools` |
| Developer, `answer`, after an answer | a test and its criterion | the Tester | exists | yes, since frame 200's pass 2 | none |
| Tester, `tests_missing`, encode | a criterion's text and its surface ref | the Terminologist | `tester -> terminologist question`, exists | yes | frame 202's door offers it |
| Tester, `tests_missing`, encode | a criterion and the item | the Vision Keeper | `tester -> vision_keeper question`, exists | yes | none |
| Critic, `review` | the diff and a criterion | the Developer, through the fail | `critic -> developer challenge`, exists | yes | none. A diff that contradicts a criterion is a fail, not a note (frame 201) |
| Critic, `review` | a criterion with a doubt, and its test | the Terminologist | `critic -> terminologist question`, exists | yes | none |
| Terminologist, `criteria` | a criterion and the item | the Vision Keeper | `terminologist -> vision_keeper challenge`, exists | yes | none |
| Architect, `deliver` or `escalate` | a criterion and a constraint | the Terminologist | `architect -> terminologist question`, exists | yes in `deliver`, no in `escalate` | none. The Architect owns the constraint side |
| Architect, any mode | a test and a constraint | the Tester | **none** | no | the fallback below |
| Vision Keeper, `slicing` | an item and a constraint | the Architect | **none**. The graph's `silent_channels` says the receipt cascade informs it | no | the fallback below |
| Critic, `review` | the diff and the item's scope | the Vision Keeper | **none** | no | the fallback below. The Architect's `touch_strays` gate covers the files already |

The corpus's nine conflicts come from the Developer, the Tester and the Terminologist (reasoned: the grid's examples).
Each pair in the table above has an edge for those three seats. So the corpus needs no new edge.
The design adds two tool lines to one mode, and **no new edge**.

**A pair with no edge (pass 2, review findings 1 and 7).** The corpus holds 0 conflict notes on the three pairs (observed: the review, finding 7; the grid, section 3).
A prediction never gates (composition, Flows), so the design builds no route for them now.

- The seat logs `kind="conflict"`. The row records the owner from `_owner_of_ref` (`rota/core/sandbox.py:858-874`), with `tests` added for the Tester.
- Under `merge_gate = auto` the row **holds nothing**. No seat is woken by a ledger row, so the only discharge would be the principal's keypress. A hold on it is a wait on a page, against DECISIONS of 2026-09-12, point 2 (observed: the review, finding 1).
- The row parks at the merge with the others (section 4). The shipped line counts it as "a disagreement no seat could take" (section 4). The night read counts it apart (pass 1, `nightreport.py`).
- Under `merge_gate = review` the row is a numbered line on the review page, and the review gate holds the merge already (`lifecycle.py:510-511`).
- The only route that answers such a row before the merge is a new edge, or a new mode for each owner that the scheduler wakes on a ledger row. Either one changes who is summoned, and law 3 and the composition decide that. Section 11 holds it as a composition question, raised when a night shows one such row.

The old line, "the fallback holds the merge as a numbered line", is withdrawn. The old pass 5 is removed from the plan (review finding 7).

### 3.2 The wait

The composition's open section records Roman's tentative ruling of 2026-09-16: a seat that asks another seat "waits for the answer in the same session, with a depth cap and a timeout" (`plans/composition.md:128-142`).
Roman "holds the ruling tentative and low priority until the code confirms the reading" (ruled: the same lines).
Law 4 and law 6 say the opposite today: "Nothing routes a counter-question into a suspended session" (`LAWS.md:192`).
So this design makes **the batch wait, not the session**. The asking session ends as it does today (reasoned: no ruling confirms the same-session wait, and law 4 is in force).

**The shape in the composition's words (pass 2, review verdict 7).** The body of the composition names it. The Parties section says "Each seat wakes cold, acts once, and ends. Nothing accumulates in a conversation. Everything accumulates in records."
The Records section says "A seat restarts from records. There is no snapshot." and "Work is not assigned. Being woken is the assignment."
The Open section's second candidate sentence ends the same way: a seat "otherwise restarts from records" (`plans/composition.md:140-142`).
So the asker's session ends. The open message is the record of the wait, and the answer's tip wakes a fresh session of the asker. The batch waits on the record.
The Open section's first sentence, the same-session wait, stays tentative and unbuilt. The code does not confirm it (observed: `LAWS.md:192`; `scheduler.waiting_filter`, "It asked; it waits.", `scheduler.py:1409-1440`). No question to Roman is needed, because the body already rules the shape.

| Part | Where | Today | This design |
|---|---|---|---|
| Where the obligation sits | `messages`, `status = 'open'`, or `status = 'unresolved'` while the `unresolved` predicate names a next rung for it; verb `question`, `challenge` or `escalate`, with refs that reach the batch | exists (`schema.sql:649-694`; `predicates.py:1087-1160`) | unchanged |
| Where the batch waits | `lifecycle.mergeable` | reads no message | returns `"waiting on <role>: <message id>"` while a seat still owes such a message a reply (section 4) |
| What the asker does meanwhile | `scheduler.waiting_filter` (`scheduler.py:1409-1440`) | holds a role with an open `question`, and not a `challenge` | adds `challenge` and `escalate` from the same role, so a Developer that challenged is not woken to build again. Frame 200's `_refuse_after_challenge` holds the session, and this holds the next wake |
| What wakes the batch | the answer's tip wakes the asker | exists | unchanged |
| The depth cap | the ladder `QUESTION_LADDER = ("architect", "vision_keeper")` (`predicates.py:53`), then the Liaison | exists, through `unresolved` (`predicates.py:1087-1130`) | unchanged. A question asked from an answering mode counts as depth 2, and no answering mode offers a third ask |
| The timeout | `message_attempt_cap = 3` (`config.py:86`), then `quarantined` | exists | unchanged. Law 13 says time is not a concept, so the bound counts wakes, never minutes (`LAWS.md:344`) |
| A quarantined conflict (pass 2, review finding 2) | `scheduler.py:2187` and `boot.py:190` write `quarantined`. No code moves a message out of it, and only the operator's reset touches it (observed: the review, finding 2) | the batch can merge | **The hold ends by itself.** The predicate reads no `quarantined` message, so the quarantine that the attempt cap or the loop cap writes is the release. No write and no person is needed. The existing `quarantined` predicate (`predicates.py:1590`) wakes the Liaison, and the principal hears what stalled. The conflict's rows park at the merge, and the shipped line names the stalled question. His answer lands through `principal.land` as a ruling on the rows. A changed row after the merge is new work on top, by DECISIONS of 2026-09-12, point 3. Nothing stops quietly, because the quarantine page and the shipped line both show it (composition, Records) |
| A triage-made `unresolved` question | `schema.sql:692-693`: "nobody owes that question a reply" | | holds nothing, because the `unresolved` predicate names no rung for it (reasoned: the hold reads the predicate's wakes, not the status alone) |

The old `Stuck` line for a held batch is withdrawn. Under `auto` no quarantined message holds a batch, so the line has nothing to report.

## 4. The merge

By Roman's ruling the hold is per category (ruled: Roman, 2026-10-11 15:00).
Two categories hold: conflict and scope change. The rest never hold.

**The predicate.** `lifecycle.mergeable` (`lifecycle.py:430-513`) gains one check, after the verdict check and before `merge_gate`.

1. Find the batch's rows: its item, its tickets, their criteria, and the tests of those criteria.
2. Find the batch's ledger rows by the park's route, so that the hold and the park read one set (pass 2, review finding 4). A row belongs to the batch when its `about_ref` reaches one of the rows of step 1. A row whose `about_ref` is a file path, or reaches no item, belongs to the batch of the session that wrote it, through `receipts`, `sessions.wake_refs` and `checkpoints.batch_id` (observed: `plans/frame198-scope.md`, section 4). Night 138's two rows under `tests/test_utils/` reach their batch only this way (observed: the review's `q4.py`).
3. Keep the open rows of step 2 with `kind = 'scope'`, and with `kind = 'conflict'` when an owner seat was asked through an edge. A `conflict` row on a pair with no edge holds nothing under `auto` (section 3.1).
4. Read the messages with verb `question`, `challenge` or `escalate` whose `body_refs` reach one of the rows of step 1, and that a seat still owes: `status = 'open'`, or `status = 'unresolved'` while the `unresolved` predicate names a next rung. A `quarantined` message holds nothing (pass 2, review finding 2).
5. If step 3 or step 4 is not empty, return `"waiting on <owner>: <ids>"`. The loop already says this reason aloud (observed: `mergeable`'s docstring, `lifecycle.py:431-438`).

Every hold has an end that no person writes. An open message reaches its attempt cap or the loop cap and becomes `quarantined` (`config.py:86`; `scheduler.py:2187`). An `unresolved` message runs out of rungs. A `scope` row closes by the Vision Keeper's decision through `decisions.author` with `resolves_ledger` (`api.py:8073`), or by an amendment that cancels the batch (law 9).
A `scope` row whose Vision Keeper never answers is the one open end. The Vision Keeper is woken for a scope row by the same message route as a conflict. The `ledger.log` door turns a bare `scope` log into an offer of `msg.question_vision_keeper`, as it does for `conflict`, so the row always has a message beside it, and the message's attempt cap ends the hold (judged: pass 3). A `scope` row from a mode with no such call holds nothing (reasoned: the same rule as a conflict on a pair with no edge).

Messages carry no batch (observed: `scheduler.py:1420-1423`), so the check joins on the refs, and not on a batch column.
A conflict is a fact on record, and "only a fact or a ruling gates" (composition, Flows), so the hold is a predicate and law 8 holds.

### 4.1 What the predicate holds, in numbers (pass 2, review finding 5)

The predicate holds 0 of the 6 merges on nights 136 to 139 by its ledger half, because no row has kind `conflict` or `scope` before pass 1 (observed: the review's `q0.py` and `q4.py` on the night copies, 2026-10-11).
It holds at most 2 by its message half. 17 messages reach a merged batch's rows before its merge. All 17 are `answered` at the night's end, 7 with a reply before the merge.
Night 139's m105 and m108 sit inside bg_2's merge window (observed: the review's `q2.py` and `q3.py`).

Per night, with the fresh rows re-typed by keyword as pass 1 would type them (observed: a read-only keyword count on `n136.db` to `n139.db`, 2026-10-11; the keyword rules are (reasoned) and misfile some rows):

| Night | Merges | Fresh rows | Conflict-like | Scope-like | Permission (now `blocked`) | Holds by the ledger half after pass 1 | Holds by the message half |
|---|---|---|---|---|---|---|---|
| 136 | bg_1, bg_3 | 217 | 2: a Tester literal that names an error string, and an onboarding Terminologist row. Neither is a conflict of two owned rows | 0 | 0 | 0 | 0 |
| 137 | echo_json_group | 45 | 0 | 1: the Developer's "out of scope" on the confirm item, whose batches were all abandoned | 0 | 0 | 0 |
| 138 | b_2 | 24 | 3 Developer rows on `c_1`, written on b_1's life, and b_1 was abandoned | 0 | 2 rows under `tests/test_utils/` | 0. The `c_1` conflict was real, and its batch never reached a merge | 0 |
| 139 | bg_1, bg_2 | 16 | 0 | 0 | 0 | 0 | 0 to 2 (m105, m108) |

So the hold meets about one real conflict in four nights, night 138's `c_1`. That conflict killed its batch before a merge.
A predicate that holds nothing measures nothing. So pass 2 adds two measures beside the night: a recorded case on the `c_1` shape, and a seam night that starts from night 138's b_1 pair (`probes/seam_start.py pair`; observed: `plans/operating-facts.md:153`). Pass 2's ratio runs over four nights, not two.

**The 131 rows that need a reader, per category.** The corpus's 22% counts rows that need a reader before a merge. Most of them need a reader and no hold (reasoned: the corpus, section 5, against section 2's table).

| Corpus mass | Need a reader | Category in this design | Holds the merge | The reader the design gives it |
|---|---|---|---|---|
| C, a real choice | 39 | about 25 default, 9 conflict, about 5 scope | 14 hold | the conflict route and the Vision Keeper; the defaults go to the quiet section, the review page, and the Architect's rule |
| B, behavioural third | about 30 | default | no | the same as the defaults above |
| D, faults that hide a pick | about 3 | default after a re-read | no | the same |
| E, echoes that invent a sense | about 10 | not written. A sense the seat invents is a default of the Terminologist, logged outside a relay | no | the Terminologist's own `criteria` or `define` wake |
| F, logs that hide a pick | about 5 | default | no | the same as the defaults |
| G, findings | 24 | finding | no. An onboarding claim holds an adoption | the onboarding page |
| H, unaddressed | 20 | unaddressed | no | the next page |
| Total | about 131 | | about 14 hold, 117 do not | |

So the 22% is not a count of holds. About 14 of 583 notes, 2%, hold a merge (reasoned: the sum). The predicate's low count on four nights agrees with that.

**The other categories at the merge.** Frame 198's park sits here. `lifecycle.merge` (`lifecycle.py:185-247`) parks every open row of the merged batch's request after the line that sets `status = 'merged'`.
The rows are kinds 1, 2, 9, 10 and 11, because 3 and 4 held the merge until they closed.
A park is not a close. A close would write a decision with no keypress, against DECISIONS of 2026-09-03 (`rota/DECISIONS.md:1358-1364`).
The row's request comes from its `about_ref` through `_items_reached`. A row that reaches no item takes the request of the batch of the session that wrote it, through `receipts` and `sessions.wake_refs` (observed: `plans/frame198-scope.md`, section 4).

The schema: `ledger.status` gains `parked`, and `ledger.kind` gains `invented`, `scope`, `conflict` and `other`.
Both CHECKs change, so `SCHEMA_MARK` moves once (`rota/core/db.py:165-169`). A cold night is unaffected, and the warm snapshot is re-created (observed: `plans/operating-facts.md:152`).
A new table `ledger_parks` would keep the mark. The kind CHECK moves the mark anyway, so one column is simpler (reasoned).

**The state view of a shipped request.** `render_state` (`principal.py:282-443`) gains one quiet line under "Done", per shipped request with parked rows:

    Shipped: <request headline>. It carries 3 choices the team made where you said nothing, and 4 invented test values. Ask me to show them.

When a parked row is a `conflict` on a pair with no edge, or the request shipped beside a quarantined question, the line adds one clause: "and 1 disagreement that no one on the team could answer before it shipped" (pass 2, review findings 1 and 2).

The line numbers nothing and asks for nothing. The Liaison's `converse` mode shows the rows when the principal asks, and the principal's words then land as a ruling through the existing door.

## 5. The principal's page

Roman's answer to the Alice story: "they can reach me if they are shown quietly" (ruled: Roman, 2026-10-11 15:00).

| Category | Before intent: the sign-off page | After intent, `merge_gate = auto` | After intent, `merge_gate = review` |
|---|---|---|---|
| 1 Invented value | a count in a quiet section | a count in the request's quiet section, and in the state view after the ship | the same count |
| 2 Default behaviour | a numbered line. The hold at intent time is ruled | listed, not numbered, in the request's quiet section; parked at the merge | a numbered line on the review page |
| 3 Conflict | a numbered line, when no seat can route it | off the page while an owner can answer. A question that climbed to the Liaison is put to the principal by the existing `unresolved` and `quarantined` paths, and holds nothing. A row on a pair with no edge is in the shipped line (pass 2, review finding 1) | a numbered line on the review page |
| 4 Scope change | a numbered line | off the page while the Vision Keeper can answer; a numbered line when it climbs | the same |
| 5 Blocked, 6 Tool fault | off every page | off every page | off every page |
| 7 Trace, 8 Echo | not written | not written | not written |
| 9 Finding, 10 Gap | numbered lines on the onboarding page, as today | not produced after intent | not produced |
| 11 Unaddressed | a numbered line | a numbered line | a numbered line |

The hold at intent time follows DECISIONS of 2026-09-12, point 2: "No batch starts until the first page is answered. After that, nothing waits on a page" (`DECISIONS.md:1384`).
After intent a numbered line asks for a ruling and holds nothing. Under `auto` the merge waits on a seat, never on a page, with no exception (pass 2, review findings 1 and 9).
Under `review` the merge waits on the review page, which the principal turned on (composition, Parties).
`merge_gate = review` has no release path in the code today: `lifecycle.py:510-511` is its only reader (observed: `grep merge_gate`, 2026-10-11). That gap is outside this frame, and section 12 names it.

**What the agenda tick carries.** `tick_agenda` (`scheduler.py:1053-1108`) changes in three places.

1. The query reads `status = 'open'` and so skips a parked row. This is frame 198's option (a).
2. `chosen` keeps the line kinds of the table above: `default` only when `merge_gate = review`, plus `conflict`, `scope` and `unaddressed_answer`.
   A row of kind `invented`, or of kind `default` under `auto`, wakes no page. It shows in the quiet section of the next page that the request's own rows put up.
3. Rows of the current request sort first, as today. A row of another open request stays, because `off_page` drops it from the page by the request rule of frame 193's 2.F.7.

`off_page` (`principal.py:873-914`) keeps its 2.F.7 exception, so the pinned test `tests/rota/test_frame193_pass2.py:335-337` holds (observed: `plans/frame198-scope.md`, section 4).
A row of a delivered item is parked before any later page reads it, so the exception now fires only for a row that a ruling reopened (reasoned).
Night 139's m143 would have held none of its 7 rows: 6 of them reach `echo_json` of request A, and 1 reaches request B, and all were parked at the merges of bg_1 and bg_2 (reasoned: `plans/frame198-scope.md`, section 1).

## 6. The Architect's check on opt-out

Roman: "this is another one that probably depends on category, im not sure here, we need to investigate this problem space" (ruled: Roman, 2026-10-11 15:00).
The grid named one rule, "a default whose row reaches a constraint's binding" (`plans/frame204-categories.md`, section 6). Law 12 holds that rule already: "Structural review triggers by mechanical intersection of diff-touched grains with bindings" (`LAWS.md:325-330`).

| Category | Check before the merge | What the check reads | Corpus rows |
|---|---|---|---|
| 1 Invented value | Nothing. A test's literal binds no product grain. A product literal is a default | | 73 of mass B name only prompt strings or dictionary keys (observed: the corpus, section 5) |
| 2 Default behaviour | **A rule, then the existing judgement.** The rule picks a default whose `about_ref` reaches a grain with `constraint_bindings.resolves = 1`, except constraint zero. The grain comes through a criterion's `surface_refs`, a test's criterion, or a path. The picked rows join the Architect's structural review, which already ends in a finding | `criteria.surface_refs` (`schema.sql:443-455`), `constraint_bindings` (`schema.sql:242-248`), `needs_structural_review` (`lifecycle.py:285-340`) | about 40, for example the `one-retry` row. The corpus does not record bindings, so the count of hits is a pass 4 step-0 query |
| 3 Conflict | Nothing new. The route holds the merge | | 9 |
| 4 Scope change | A judgement, by the Vision Keeper and not by the Architect. The existing rule `touch_strays` catches files beyond the prediction (`lifecycle.py:470-481`) | | about 5 |
| 5 to 8 | Nothing | | |
| 9 Finding, 10 Gap | Nothing at the merge. Constraint zero is the existing rule for an area nobody surveyed (law 12) | | 24 and 16 |
| 11 Unaddressed | Nothing. It is the principal's question | | 20 |

The rule is a predicate with no model call, so law 8 holds. The judgement after the rule is the structural review's, which is a merge gate today (`LAWS.md:236-239`).
The check fires only where a batch did not already need a structural review. On click, frame 179 found `k0` the only constraint in every review (observed: frame 179's heading), so the rule can fire on zero batches.
That result is the pass 4 step-0 query, and a zero sends pass 4 to wait for frame 179.

Roman first chose a wider reader: "Every default" (ruled: Roman, 2026-10-11 15:49, by `AskUserQuestion`). One minute later he changed it: "Maybe change this, add an investigation task post 179" (ruled: Roman, 2026-10-11 16:01). So the rule above stands, and only a default on constrained code goes to the Architect's structural review (pass 3, ruling 2). Whether the Architect reads every default under opt-out is an investigation frame after frame 179 (section 12).

## 7. The code paths that write notes without a seat

| Writer | File and line | Fresh notes | What the design does |
|---|---|---|---|
| The literal door of `tests.encode` | `rota/roles/api.py:7031-7043` | about 73 of 103 | The row stays a note, kind `invented`. The door stages the row itself and admits the encode, so the seat spends no turn on a dictated `ledger.log`. The author stays the seat |
| The returns door of `tests.encode` | `rota/roles/api.py:6996-7012` | about 30 of 103, with the behavioural literals | The row stays a note, kind `default`. The door offers the call as today, because a seat that asserts on a return chose a behaviour |
| `challenge.break` | `rota/roles/api.py:10224` | 24, with `vacuous` | The row stays a note of category finding. The kind `default` is unchanged in the column, because the page already reads it as a line. Onboarding only |
| `challenge.vacuous` | `rota/roles/api.py:10277` | in the 24 | the same |
| `ledger.unaddressed` through `_stage_ledger` | `rota/roles/api.py:7948-7977` and `:7940` | 20 | unchanged. Kind `unaddressed_answer` |
| `frame.assign` | `rota/roles/api.py:10437` | not counted | stays a note, kind `default`, onboarding only |
| The lazy election, `defer_baseline` | `rota/core/loop.py:471-504` | not counted | stays a note, kind `default` with author `principal`, onboarding only |
| Seats' tool faults and blocks through `ledger.log` | `rota/roles/api.py:7811` | 95 | **Becomes a fault report to the operator.** `ledger.log(kind="fault")` or `kind="blocked"` writes a row of a new table `faults`: session, the refused call's name, the text, seq, `status` (`open` or `closed`), and `closed_by`. No page shows it. The reply to the seat says that the fault is recorded for the people who build rota and that the seat ends. The readers and the discharge are below |
| Ruling echoes on relay wakes | `terminologist/relay.md:14-15`; `ledger.log` in `architect/relay.tools` and `terminologist/relay.tools`; the door at `api.py:7869-7875` | 221 | **Stops being written.** Remove the brief sentence and the tool from both relay modes. The door stays as the guard |
| Work logs | `developer/batch_start.md:47-49` names the cause: a session with no work left "fills the remaining turns" | 65 | **Stops being written.** The `kind` parameter has no `trace` value. A text that names no choice and no silence is refused by the existing four-word rule and a new kind rule. The residue rule reads what is left |
| Gap labels of the blindspot tick | `liaison/blindspot.md:18-20` | 16 | unchanged. Onboarding lines |

The 44 faults of `glossary.adopt` (`rota/roles/api.py:1801`) are a defect of rota, and frames 197 and 192 hold their causes.
They become fault rows in pass 1, so the next night counts them where the operator reads, and the principal no longer contests them (observed: the corpus, section 3, 38 contests of faults).

**The `faults` table is visible and countable from pass 1 (pass 2, review finding 6).** The composition's Records line rules it: "Nothing stops quietly. Every open obligation stays visible and countable until something discharges it."

| Part | What | Where |
|---|---|---|
| Writer of a row | the `ledger.log` door, in the seat's session, author = the seat | `rota/roles/api.py`, `ledger_log` |
| Reader 1, live | the cockpit snapshot gains `"faults"`: the open rows, newest first, beside `"ledger"` | `rota/cockpit/server.py`, `snapshot`, next to the `ledger` query at `:153` |
| Reader 2, after a night | the night report gains one section: open faults per refused call, with counts | `rota/tools/nightreport.py` |
| Reader 3, the state view | one count line, no rows: `Rota itself failed 3 times this run. The people who build it have the list.` The principal sees the count at his altitude and is asked nothing | `principal.render_state` |
| Discharge column | `status` moves from `open` to `closed`, and `closed_by` holds the number of the build frame that fixed the cause | `schema.sql`, the new table |
| Who discharges | the build session, the meta workflow, through one operator command, `python -m rota.tools.faults close --call <name> --frame <n>`. It closes every open row of that refused call. A seat never closes a fault, and the principal is never asked to | a new `rota/tools/faults.py` |
| One writer per column | the door writes the row, and the command writes `status` and `closed_by`. The `ledger` follows the same split: a seat writes the row, and `land` writes `status` | `schema.sql:552-562`; `principal.py:1814` |

A fault whose cause no frame fixes stays `open` and stays counted on the cockpit, the night report and the state view. It never stops quietly.

## 8. What generalises

**The rule.** A seat answers three questions at log time, and one word follows from the answers. Pass 2 adds question 0 (review finding 3).

0. Is the obstacle a rule of rota (a permission, a door, a tool) or the content of a row?
   - A rule of rota that works as designed is no note. The Developer may not write the Tester's files by design. If the seat believes the row behind the rule is wrong, the note is about the row, so go to question 1. If not, the seat writes nothing.
   - A rule of rota that fails, or a record that names a row that does not exist, is `fault` or `blocked`.
   - The content of a row: go to question 1.
1. If this is wrong, who must say so: the principal, the owner of a row, or nobody in rota?
2. Did I pick: yes, I could not, or I did not need to?

Night 138's two Developer rows, "The test files are owned by the Tester and cannot be written by me. I must leave them as-is and assume my implementation is correct", place by question 0. The obstacle is a permission that works as designed, and the seat does not say the test is wrong. So the seat writes nothing. Before pass 2 these rows sat in two cells, scope cut by the grid and tool fault by the corpus (observed: the review, finding 3; `q4.py` on night 138).

**The tie-break, for a note that still fits two cells.** Take the first cell of this order (reasoned: a missed hold ships a guess, and an extra answer costs one wake):

1. A cell that holds the merge: `conflict`, then `scope`.
2. A cell owed to a row's owner, before one owed to the principal. The owner is the shorter loop (composition, The ceiling).
3. A cell owed to the principal, before one owed to nobody.
4. Within one row of the grid, "could not" before "picked", and "picked" before "did not need to".

The door applies the order when a seat sends two words, and it keeps the first. A seat sends one word, so the order is mostly the door's.

**A note about a file path.** `ledger.log` admits a path or an `@area` as `about_ref` (observed: `api.py:7841`, "use the @-prefixed area name"; the comment at `api.py:7853-7855` keeps a path legal). Such a row reaches no item. It belongs to the batch of the session that wrote it, by the park's route (section 4, step 2). A path note written outside any batch, for example by a survey, belongs to no request and stays an onboarding line.

| | Picked | Could not | Did not need to |
|---|---|---|---|
| Owed to the principal | `default`, `scope` | `unaddressed`, and a conflict of two project sources | `gap` |
| Owed to a row's owner | `invented`, `finding` | `conflict` | (empty on purpose) |
| Owed to nobody in rota | | `blocked` | `fault`; trace and echo are not written |

A merge waits when the note says that the change contradicts an owned row and the owner has not answered. A word the seat cannot place is `other`.
An `other` row goes to the quiet section and to a count on the night read. Three `other` rows of one shape on one night make a new category, and that change is a design frame (reasoned: Roman, "the set of types is still unknown", 2026-10-11 14:34).

Five notes that the corpus does not cover, placed by the rule:

1. **The Researcher, `question` mode.** "The docs I found are for click 8.1, and the repository pins 8.0." The Researcher picked a source, and the asker owns the row the answer feeds.
   The Researcher has no `ledger.log` (observed: `researcher/question.tools`). Its edge carries prose (observed: `graph.json`, `prose: question`).
   So the sentence goes in the answer's `body_text`. If the asker builds on it, the asker logs `default`. Nothing holds the merge. Answers: the asker, then the principal on a review page.
2. **The Terminologist, `survey` mode.** "The README uses 'group' for a set of commands, and `core.py` uses it for an option group." Two project sources disagree, and no rota seat owns either.
   `survey.tools` has no `ledger.log` (observed). The collision goes to `term_collision` as today, and DECISIONS of 2026-09-12, point 4, sends it to the principal.
   The cell is "owed to the principal, could not choose". Intent time holds it. Answers: the principal.
3. **The Liaison, a relay of a verdict.** "The principal said 'fine, but not the colours', and I cannot tell which line 'the colours' means." The Liaison could not choose, and it must not rule for the principal (composition, Flows).
   The cell is `unaddressed`: `ledger.unaddressed` for each row the words may touch. No merge waits. Answers: the principal, on the next page.
4. **The Vision Keeper, `deliver` at onboarding.** "The statement does not say whether the tool reads its settings from the environment. I took no." The seat picked, and the principal must say so if it is wrong.
   The cell is `default`. Intent time holds it: a numbered line on the sign-off page, as `vision_keeper/deliver.md:23` does today. Answers: the principal.
5. **The Gate Keeper, which is the Vision Keeper at `slicing`.** "Item `add --json` also says 'and pretty-print by default'. I sliced only the flag." The seat departed from the item's words, and it owns scope itself.
   The cell is `scope`, owed to the principal, because the owner is the writer. The Vision Keeper has no seat above it to ask but the Liaison. So no seat owes the row an answer, and by section 4, step 5, it holds nothing (pass 2).
   Slicing runs before the batch starts, so the row is on the request's next page as a numbered line, and the merge comes after it. If the merge gate itself ever wrote a note, the cell would be `blocked` or `fault`, because the gate is code (reasoned).

## 9. The rulings crossed

| Ruling, date | Words | Design |
|---|---|---|
| Composition, Records, 2026-09-16 | "Nothing stops quietly. Every open obligation stays visible and countable until something discharges it." | **Keeps.** A parked row stays countable in the state view. A quarantined conflict shows on the quarantine page and in the shipped line. A fault stays an open row on the cockpit, the night report and the state view's count until a build frame closes it (pass 2, review finding 6). Trace and echo were never obligations |
| Composition, Flows, 2026-09-16 | "The tool never rules for the Principal. It never settles a conflict, closes an assumption, or treats silence as consent." | **Keeps.** A park is not a close. A conflict is settled by its owner or the principal, never by code |
| Composition, Flows | "A question changes nothing." | **Keeps.** The hold delays a merge and revokes nothing |
| Composition, Parties | "Sign-offs after that, including on merges, are opt-in." | **Keeps.** Defaults are numbered lines only under `merge_gate = review` (`config.py:70-74`) |
| Composition, Open, 2026-09-16, tentative | "A seat that asks another seat waits for the answer in the same session." | **Not built.** The batch waits, and the session ends, in the body's words "A seat restarts from records" (section 3.2). Roman holds the ruling tentative |
| DECISIONS, 2026-09-03 (`DECISIONS.md:1358-1364`) | "a decided row enters the record only from a keypress" | **Keeps.** The merge parks and never closes |
| DECISIONS, 2026-09-12, point 2 (`DECISIONS.md:1384`) | "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page." | **Keeps, with no exception** (pass 2, review findings 1, 2 and 9). Under `auto` a hold reads only what a seat still owes. A conflict on a pair with no edge, a quarantined question and a question that climbed to the principal hold nothing |
| DECISIONS, 2026-09-12, point 4 (`DECISIONS.md:1392-1395`) | "Conflicting sources always ask." | **Keeps.** A conflict of two project sources goes to the principal. A conflict of two rota rows goes to an owner first |
| LAWS, law 2 (`LAWS.md:112-119`) | "Judgement crosses a role boundary only as structured findings." | **Keeps.** A conflict travels as a message with refs. The prose stays in the ledger row or the decision |
| LAWS, law 3 (`LAWS.md:121-146`) | Contact lists are derived, and the graph is the oracle | **Keeps.** No new edge and no new wake. A route for the three unrouted pairs is a composition question, held in section 11 (pass 2, review finding 7) |
| LAWS, law 6 (`LAWS.md:183-200`) | "Nothing routes a counter-question into a suspended session." | **Keeps.** |
| LAWS, law 8 (`LAWS.md:229-232`) | "nothing ships whose assumptions the principal never saw" | **Changed, ruled** (pass 3, ruling 2; ruled: Roman, 2026-10-11 15:49 and 16:01, section 11). The new wording: "A lineage's open assumptions are presented at its gates, and nothing ships whose assumptions the principal cannot always see." Under `auto`, a default made after intent ships, parked, and the shipped line shows it |
| LAWS, law 12 (`LAWS.md:325-343`) | Structural review triggers by mechanical intersection | **Keeps.** The Architect's rule is the same intersection, read from a default's row |
| LAWS, law 13 | "Time is not a concept." | **Keeps.** The bound on a wait counts wakes |
| Frame 193's design, 2.F.7 (`plans/frame193-design.md:830-834`) | A delivered item's notes stay numbered, so a ruling closes them | **Narrows.** The exception now applies only to a row a ruling reopened. A design review set 2.F.7, not Roman |

## 10. The passes

Prices come from the latest actuals, which run above the anchors (observed: frame 200's status lines, 2026-10-11). A cold implementer pass cost 135k to 257k, a diff review 150k to 190k, and the gate 12 minutes.
A cycle costs the holding session about 10k (observed: `plans/operating-facts.md:237`). Each pass ends on a diff review. Passes 1 to 3 share one walk of two nights.

**Pass 1, the kinds at the door.** About 250k on one implementer, a 150k review, 4 cycles.

- Files: `rota/core/schema.sql` (kind and status CHECKs, the table `faults` with `status` and `closed_by`); `rota/core/db.py` (the mark); `rota/roles/api.py` (`ledger_log` takes a required `kind`; `fault` and `blocked` write `faults`; `conflict` is refused with an offer of the owner's message when the mode holds it, and is otherwise written as a row; question 0 and the tie-break of section 8 in the door's text; the literal door stages `invented` itself; the returns door names `default`); `relay.tools` and `relay.md` of the Architect and the Terminologist; each brief line of section 1, item 2, names the words that its mode offers; `rota/cockpit/server.py`, `rota/tools/nightreport.py`, `principal.render_state` and a new `rota/tools/faults.py` for the faults' readers and discharge (pass 2, review finding 6).
- Tests with no model: one door test per kind; the two encode doors; a relay mode with no `ledger.log`; the mark; the cockpit snapshot holds `faults`; the night report's section; the state view's count; the close command closes the rows of one call and writes the frame number.
- Step 0 (pass 2, review finding 8): the implementer confirms the stale list below from the gate's STALE lines on the first run, and names any case that an open frame holds as its measure.
- Recorded cases that replay stale (pass 2, review finding 8). The tool's text changes in every mode that offers `ledger.log` (observed: the `.tools` files, 2026-10-11). The cases of those modes, by role and inbound verb or tick, from `tests/rota/cases/*.yaml` (observed: a read of the 157 cases, 2026-10-11; the mode is (reasoned) from the verb or the tick):
  - Developer, 19: `L1-DV-apply-the-answer-and-carry-on`, `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`, `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on`, `L1-DV-take-out-what-nobody-asked-for`, `L1-DV-build-a-clear-criterion`, `L1-DV-log-the-choice-the-criteria-did-not-make`, `L1-DV-read-the-map-not-the-whole-file`, `ACT-DV-edit-inside-the-function`, `L1-DV-fix-the-code-not-the-test`, `L1-DV-challenge-a-test-that-contradicts-its-criterion`, `L1-DV-challenge-a-test-with-a-long-body`, `L1-DV-act-on-an-answered-challenge`, `L1-DV-fix-what-the-verdict-names`, `L1-DV-end-the-session-when-the-door-says-end`, `L2-DV-name-the-block-rather-than-retry`, `L2-DV-name-the-deferred-batch-not-the-running-one`, `L1-DV-restore-what-the-finding-names`, `L1-DV-give-the-new-parameters-defaults`, `L1-DV-escalate-a-finding-the-loop-could-not-answer`.
  - Architect, 11: `G1-a-ratified-conflict-is-caught-by-the-owner`, `L1-AR-constrain-an-external-commitment`, `L1-AR-cite-the-clause-into-a-constraint`, `L1-AR-route-an-escalation`, `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row`, `L1-AR-a-ruled-constraint-gets-no-new-row`, `L1-AR-re-annotate-from-the-principals-correction`, `L1-AR-adopt-what-the-principal-approved`, `L2-AR-place-a-block-developer-could-not`, `L1-AR-a-dead-end-leaves-the-desk-to-a-named-seat`, `L1-AR-a-dead-answer-is-a-question-about-the-model`.
  - Vision Keeper, 10: `L1-VK-assert`, `L1-VK-the-account-before-the-behaviours`, `L1-VK-a-statement-on-an-existing-account-is-a-behaviour`, `L1-VK-an-outside-fact-is-the-researchers`, `L1-VK-slice`, `L1-VK-slice-a-description`, `L2-VK-end-it-rather-than-send-it-back`, `L1-VK-reconcile-the-readme`, `L1-VK-survey-an-area-for-what-it-does`, `L1-VK-a-source-does-not-settle-scope`.
  - Tester, 9: `L1-TS-apply-a-term-and-write-the-test`, `L1-TS-encode-a-criterion-the-principal-corrected`, `ACT-TS-give-the-prompt-a-stream`, `ACT-TS-three-criteria-one-per-reply`, `ACT-TS-five-criteria-one-per-reply`, `L1-TS-encode-a-criterion`, `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers`, `L1-TS-an-outside-fact-is-the-researchers`, `L1-TS-a-criterion-that-contradicts-the-request-goes-back`.
  - Terminologist, 7: `L1-TE-a-standard-definition-is-not-automatically-ours`, `L1-TE-a-new-behaviour-is-a-new-callable`, `L1-TE-specify-criteria`, `L1-TE-repair-the-criterion-the-tester-cannot-encode`, `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told`, `L1-TE-adopt-what-the-principal-approved`, and `L1-TE-log-the-word-you-took-one-way`, whose `deliver` mode lists no `ledger.log` but whose name says it logs, so step 0 checks it.
  - Liaison, 1: `L1-LI-say-what-the-run-could-not-see`.
  - Total 57 of 157. Frame 200 holds two of them as its measures, `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone` and `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row`. Their re-records are read against frame 200's known reds, and not as this pass's regressions.
  - The four relay cases lose `ledger.log`. `L1-AR-a-ruled-constraint-gets-no-new-row` asserts no new row already, so the loss is a designed note only if a relay case expects one. Step 0 reads the four cases' `expect` blocks.
  - Price: about one card hour per 10 cases, so about 6 card hours. These hours share the card with the walk nights.
- The night's ratio: fresh notes of fault, blocked, trace or echo written as ledger rows. Baseline 160 of 362 non-echo fresh notes, 44%, over nights 120 to 139: masses D and F. Target at most 1 in 10 over two nights.
- Second ratio: turns spent on a dictated `ledger.log`, from 103 of 103 B notes to 0.
- Residue: a session that still writes such a row is read. The pass closes when the cause is not the missing kind.

**Pass 2, the conflict hold.** About 200k, a 150k review, 4 cycles. An interview when a seat holds a conflict and does not ask (ruled: Roman, 2026-10-02).

- Files: `rota/roles/api.py` (the `ledger.log` door turns a bare `scope` log into an offer of `msg.question_vision_keeper`, as for `conflict`, with a door test each way; judged: pass 3); `rota/core/lifecycle.py` (`mergeable` gains the check of section 4, with the park's route for a path note); `rota/core/scheduler.py` (`waiting_filter` counts `challenge` and `escalate`); `rota/roles/principal.py` (the shipped line's clause for a disagreement no one could answer); `developer/tests_failing.tools` and its brief (`msg.question_terminologist`, `msg.question_vision_keeper`); `sandbox.py` (`_owner_of_ref` knows `tests`).
- Tests with no model: `mergeable` held by an open challenge, an open question, an unresolved question with a next rung, a routed conflict row, and a path note through its session's batch; **not** held by a quarantined question, a triage-made unresolved question, or a conflict row on a pair with no edge; released by an answer (pass 2, review findings 1, 2 and 4).
- Recorded cases: the Developer's 5 `tests_failing` cases of pass 1's list replay stale again. New case: a Developer at its fix wake reads a test that contradicts its criterion, on night 138's `c_1` shape, asks, and writes no code.
- A seam night from night 138's b_1 pair, where the `c_1` conflict happened, beside the walk (pass 2, review finding 5). The hold meets about one real conflict in four nights (section 4.1), so the walk alone cannot measure it.
- The night's ratio: conflicts that an owner answered before the merge. Baseline 0 of 9 in the corpus: all 9 were paged, and neither owner read one (observed: the grid, section 3). Target at least 4 of 5, over four nights plus the seam night, not two nights (pass 2, review finding 5).
- Residue: a merged batch that still carries an unanswered conflict is read. The pass closes when its cause is not the missing hold.

**Pass 3, the page and the park.** About 200k, a 120k review, 3 cycles. This pass is frame 198's pass.

- Files: `lifecycle.merge` (the park); `scheduler.tick_agenda` (the status filter and the line kinds); `principal.render_page` (the quiet section with its count); `principal.render_state` (the shipped line).
- Tests with no model: night 139's 7 rows of m143 are parked at the merges of bg_1 and bg_2. `test_frame193_pass2.py:335-337` still passes. An invented row makes no page.
- Recorded cases: 0 or 1. `L1-LI-put-the-open-assumptions-to-a-present-principal` (`l1_answers.yaml:355`) has no merge and no request message (observed: `plans/frame198-scope.md`, section 4).
- First ratio: pages whose lines belong to a merged request. Baseline 1 of 20 on night 139. Target at most 1 in 20 on two nights.
- Second ratio: numbered lines that are invented values. Baseline 4 of 7 on night 139's m143 (observed: the grid, section 7). Target 0, with the count shown.
- Residue: as frame 193 wrote it.

**Pass 4, the Architect's rule.** About 120k, a 100k review, 3 cycles. A step-0 query comes before the build.

- Step 0: count the defaults on nights 136 to 139 whose rows reach a binding other than `k0`. If the count is 0, the pass waits for frame 179. A rule with no hit on the sample measures nothing.
- Files: `lifecycle.needs_structural_review`; the structural review's working set.
- Tests with no model: a default on a bound symbol needs a review; a default on `k0` alone does not; `merge_gate = review` does not trigger the rule, by Roman's words "when the principal opts out of review" (section 11, the answered Q3).
- Recorded cases: the Architect's `structural_review` cases, about 3.
- The night's ratio: defaults that reach a binding and get a finding before the merge. Baseline 0, because no check exists. Target 4 of 5 of the step-0 hits.
- Residue: as above.

**Pass 5 is removed** (pass 2, review findings 1 and 7). The corpus holds 0 conflict notes on the three unrouted pairs. The night report counts parked `conflict` rows on a pair with no edge. The first such row raises the held composition question of section 11.

**Total** for passes 1 to 4: about 770k in implementers and 520k in reviews, about 14 cycles, about 6 card hours of re-records, and the walk nights. The walk is two nights for passes 1 and 3, and four nights plus one seam night for pass 2's ratio. The design review comes before them.

## 11. The questions left for Roman

Pass 2 drops two questions, because the records answer them (review finding 9).

- **The old Q1, "when a disagreement climbs all the way to you, does the change wait?", is answered: no under `auto`, yes under `review`.** The composition, Parties: "Approval of intent is required before work starts. Sign-offs after that, including on merges, are opt-in." DECISIONS of 2026-09-12, point 2: "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page." The switch exists as `merge_gate = review` (`lifecycle.py:510-511`). Sections 3.2, 4 and 5 follow this answer.
- **The old Q3, "does the engineer check the diary only when you are away?", is answered: only when the principal opts out.** Roman's own words in frame 204's block: "What if, when the principal opts out of review, the architect reviews assumptions with relevant constraints and escalates if there are issues?" (ruled: Roman, 2026-10-11 14:40 to 15:05). Section 10's pass 4 follows this answer.

Pass 3 closes Q2 (pass 3, ruling 2). Roman ruled the design as one piece: "Start as written" (ruled: Roman, 2026-10-11 15:44, by `AskUserQuestion`). On the reader of a build-time default he chose "Every default" (ruled: Roman, 2026-10-11 15:49), and then changed it: "Maybe change this, add an investigation task post 179" (ruled: Roman, 2026-10-11 16:01). So a choice made during the build ships under `auto`. Law 8's wording changes from "never saw" to "can always see" (section 9). The Architect's rule of section 6 reads the defaults on constrained code, and an investigation frame after frame 179 decides whether it reads every default (section 12).

No question stays open. One is held. Q2's story stays below as the record of what was asked.

**Q2, closed (pass 3, ruling 2). [med] Can a choice made during the build ship before you have seen it?**
The plan was silent on whether the light switch is on the left. The builder put it on the left and wrote it in the diary.
You chose "do not call me for every wall", so nothing waits for you after the plan.
Today's rule says that nothing ships whose choices you never saw. So today the choice either sits on your page as a line to rule, or it blocks the wall, and both contradict your choice.
- Option A: it ships. The diary line stays listed under that finished job until you read it or say something about it. The rule changes from "never saw" to "can always see".
- Option B: it does not ship until you have seen it. Every job then waits on a page.

Answered A (pass 3, ruling 2). The recommendation was A: your answer to the diary story already pointed there. The words of the rule needed your change, because law 8 says "nothing ships whose assumptions the principal never saw" (`LAWS.md:229-232`), and frame 198's scope raised the same point at medium.
Pass 2's fixes make the same question cover two more things that ship before you see them. A disagreement that no one on the team could take, and a question that went unanswered until the system gave up, also ship under A and are named in the finished job's line (sections 3.1 and 3.2). This is still one question about one rule.

**Held, not asked now: [low] Who answers a disagreement between two people who cannot talk to each other?**
The engineer finds that a test contradicts a building rule. The engineer has no line to the tester. Today the note waits in the finished job's line, and the job goes ahead.
- Option A: give the engineer a line to the tester. That changes who may talk to whom, which the team chart fixes.
- Option B: let the office wake the tester with the note, with no line between the two. That gives the tester a new kind of task.
- Option C: leave it as it is, in the finished job's line.

Recommended: C until a night shows one such note. The corpus holds 0 notes on the three pairs: Architect and Tester, Vision Keeper and Architect, Critic and Vision Keeper (observed: the review, finding 7). A prediction never gates (composition, Flows). Options A and B change law 3's contact list or the composition's list of who is summoned, so Roman rules on them, and the design does not.

## 12. What this design does not cover

1. The same-session wait of a seat that asks another seat. The composition holds it tentative, and this design keeps the batch wait.
2. The causes of the faults themselves: `glossary.adopt` on a ruled id (frames 197 and 192), and the `tests.encode` parse doors. Pass 1 only moves the faults to the operator.
3. Whether an 8b model names the right word at log time. Pass 1's night measures it, and the interview rule governs the next step.
4. The 950 Vision Keeper onboarding lines, beyond a sample of 50 in pass 1.
5. A route for a conflict on a pair with no edge, held as a composition question in section 11. Also the release path of `merge_gate = review`, which no code builds today (observed: `lifecycle.py:510-511` is the only reader of the setting, 2026-10-11). That gap is a candidate frame.
6. Whether the Architect reads every default under opt-out, and not only the defaults on constrained code. This is an investigation frame after frame 179 binds constraints beyond `k0`, on the data of the nights that run with the rule. The holding session pushes that frame on the stack (pass 3, ruling 2; ruled: Roman, 2026-10-11 16:01, "Maybe change this, add an investigation task post 179").
