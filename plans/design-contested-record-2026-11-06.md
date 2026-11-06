# Frame 362, a design before any build: a record that he contested and nobody rewrote, 2026-11-06

The brief is `scratchpad/f362_contested_record_design_brief.md`. The measured fault is in `plans/f362-contested-guess-read-2026-11-06.md` (below: the read). The checkout is `9f439f3c` (observed: `git log`). This page calls no model and runs no suite. It edits no tracked file but itself (observed). A mark "(observed, RA: place)" means that a reader agent of this page read the code at that place, and this page did not read the place again. Finished 10:16 (observed: `date`).

## Result

**The recommended design: a contest of his on a record that an owner must rewrite is an owed write. The owed write is a fact derived from his ruling and the owner's table, not from the relay message. Until the write exists, the owner wakes again, no reader shows the contested record as his, and no batch starts on it.** The design is design C below, built in four slices. Slice 1 is design B. It closes the measured case, the guess line and the batch line, end to end (reasoned: sections 5 and 6).

The story of one reply under slice 1 (reasoned: sections 2 to 4, on dry run 6b's m27):

1. He reads the sign-off page. He writes "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py ..." The Liaison lands the ruling with a contest on `guess:<item>`, and relays it to the Architect, as today.
2. The relay session reads `string.py` and ends with the line "guessed ..." and no `batches.guess`. The commit marks the relay answered, as today. The relay is not the record of the owed write, so its status does not matter.
3. The one fact function `owed_rewrites` reads his ruling and the `touch_guesses` table. The newest contest on the code line has no set written under it. So the fact is true.
4. While the fact is true, three things hold. The `guess` predicate fires again, with his words in the inbound, and the write stamps his ruling. `_guess_seed` gives the annotate seat his words in the files-contest block and no path of the contested set. `next_batch` does not offer the item's batch.
5. The Architect writes a new set on a retry, or the annotate seat writes a touch set after his ruling. Either write makes the fact false. The batch starts on a set written after his words.
6. When the relay and the three retries all write nothing, the tick bound quarantines the key. His agenda says that the team could not rewrite the guess he corrected. The batch stays out, as a batch with a quarantined key stays out today.

Nothing waits on his reaction before step 6 (reasoned: section 4). At step 6 the batch waits on his decision, and that is the one open question.

**The open question for Roman (reasoned: section 4.4).** A team member guessed the wrong file, he said so, and the team tried four times and wrote nothing. Today a batch whose work failed three times waits for him, and the other batches go on (ruled: frame 87, 2026-09-27, in the comment of `scheduler.next_batch`). The ruling R7 of 2026-09-03 says that nothing waits on his reaction to the scope disclosure. Does the batch wait for him here too? Recommended answer: yes, it waits, because the other choice starts the work on the file he called wrong, and that is the measured fault.

## 1. The class: every kind of record that a contest can name

A ruling's key is a page line, a clause or `rest`. The line resolves to a ref, and `menu_kind` gives the line a kind: read-back, step, touch, request, criterion or other (observed, RA: `rota/roles/api.py` 15549 to 15565 and 15985 to 16010). A guess line has the kind `touch` (observed, RA: `_is_touch_line`, `api.py` 12977 to 12981). The table names the kinds by the record behind the line.

| Kind of record | The seat that owes the rewrite, and its mode | The call that is the write | What marks the contest answered today | Can a prose end pass? | Reader of the record after the contest |
|---|---|---|---|---|---|
| Guess line, `guess:<item>` | Architect, `guess`, by `scheduler.guess_relay` (observed: `runner.py` 405 to 412) | `batches.guess`, rows of `touch_guesses` with `ruling_id` the verdict (observed: `api.py` 9030 to 9052) | The commit, because `relay` is not in `OWED_A_REPLY` (observed: `db.py` 1505 to 1528, 2108 to 2112). `predicates.guess` fires only when no set exists at the item's version (observed: `predicates.py` 333 to 337) | **Yes.** Measured on s145 (observed: the read, section 1, row 5) | `_guess_seed`, `code_target`, `code_line`, `resolve_inbound`, `land` (observed: `map table touch_guesses`). None reads the contest |
| Batch line, `b_<n>` on the touch note | Architect, `annotate`, by `scheduler.batch_relay` (observed: `runner.py` 413 to 414) | `batches.annotate`, rows of `batch_touch`, cleared first on a contest (observed, RA: `api.py` 9084 to 9099) | The commit, as above. `predicates.annotate` fires only on a batch with no touch rows (observed: `predicates.py` 1048 to 1051) | **Yes,** by the same mechanism (reasoned). 6 of 6 recorded relays with file words wrote (observed: the read, 5.2) | `predicted_rows` drops only `exclude` paths (observed: `runner.py` 2111 to 2125). `next_batch` reads no contest (observed: `scheduler.py` 1884 to 1898) |
| Criterion | Terminologist, `criterion_repair`, for a park page's ruling only (observed: the comment at `runner.py` 386 to 399) | `criteria.respecify`, then `msg.answer_tester` (observed, RA: `terminologist/criterion_repair.md` 23 to 33) | The commit, as above. `_ruling_answer_refusal` refuses `answer_tester` before the respecify, but only when the seat sends it (observed, RA: `sandbox.py` 2139 to 2270) | **Yes** (reasoned: no call means no door runs). A criterion contest on another page goes to plain `relay`, which has no respecify tool (reasoned: the comment's "Only a park page's ruling"; not read further) | `tests_missing` encodes the criterion text as it stands (observed, RA: `predicates.py` 943 to 981) |
| Glossary term | Terminologist, plain `relay` (observed, RA: `sandbox.py` 966) | `glossary.adopt` of the approved ids. A contested sense "is not yours to fix in this session" (observed: `terminologist/relay.md`) | The commit | **Yes, for the adopt of approved ids.** The contested sense stays `observed`, so no reader takes it as his (reasoned: the brief) | Not read (RA: unverified) |
| Constraint or model area | Architect, plain `relay` (observed, RA: `sandbox.py` 967 to 968) | `model.adopt` of the approved ids. "With no approved id, end the session with no call" (observed: `architect/relay.md`) | The commit | **Yes, for the adopt of approved ids** (reasoned: as the term) | `bound_constraints` pushes a constraint by its binding, and `cw_985d42272f1e` was pushed while `observed` (observed: the read, section 4). Whether it reads a contest is not read |
| Statement, a rewrite | Vision Keeper, plain `relay` (observed, RA) | A drop lands in `land` (observed, RA: `principal.py` 4047, 4066). A rewrite has no tool (observed, RA: `vision_keeper/relay.tools`) | The commit | Yes, for a rewrite (reasoned: no tool, so no write is possible) | Not read (RA: unverified) |
| Item, the request's text | Vision Keeper, `contested` (observed: `predicates.py` 301 to 316) | `land` writes `items.approval = 'contested'` at the keypress (observed, RA: `principal.py` 3922 to 3940). The amend is `problem.assert` | `predicates.contested` fires until the item is amended or defended | **No.** The state is in the record, and the tick returns (observed: `predicates.py` 314 to 316) | `next_batch` needs `approval = 'approved' AND approval_ver >= version` (observed: `scheduler.py` 1887 to 1888) |
| Team note, a ledger row | None. `land` writes a principal decision and resolves the row (observed, RA: `principal.py` 3821 to 3897) | The keypress | The keypress | No | A contest with words also contests the row's item, which takes the item row (observed, RA: `principal.py` 3871 to 3887) |
| Step, a stopped tick key | None (observed, RA: `scheduler.rowless_key` 2006 to 2024) | `lift_keys` or `mark_ruled` in `land` (observed, RA: `principal.py` 3677 to 3682) | The keypress | No | Not applicable |
| Read-back, `reading:<reply>` | None (observed, RA: `principal.py` 3666 to 3667) | The `ruled_refs` row | The keypress | No | `menu_ruling` reads earlier answers (observed, RA) |
| Test row | It travels as its criterion (observed, RA: `sandbox.py` 4947 to 4958) | As the criterion | As the criterion | As the criterion | As the criterion |

**The rule that sorts the kinds (reasoned: the table).** A kind is safe when `land` writes the final state at the keypress, or when the record itself carries the contest and a predicate reads that state. The item is the model: `items.approval` holds the contest, `contested` fires until it changes, and `next_batch` reads it. A kind is open when the fix is a judgement that an owner writes, and only a message carries the contest. Six kinds are open: the guess line, the batch line, the criterion, the term adopt, the constraint adopt and the statement rewrite. Four are safe: the item, the team note, the step and the read-back. The test row follows the criterion.

**The kinds differ in what is lost (reasoned).** On the guess line, the batch line and the criterion, a reader seeds work from the contested text. That is the measured fault. On a term or a constraint, the contested row stays `observed`, and only the approved rows miss their adopt. On a statement rewrite, no tool exists, so the gap is a missing write path, not an owed write. The design closes the first three, and lists the other three in slice 4.

**One more gap (observed, RA: `principal.py` 3979 to 3985, `db.py` 1525 to 1527).** `land` writes the verdict message, and the Liaison's `verdict_signoff` session sends the relay. `verdict` is outside `OWED_A_REPLY` too. So a verdict session that sends no relay also reads answered, and no owner ever wakes. A design that reads the relay message cannot see this gap. A design that reads the ruling can (reasoned).

## 2. The owed write: what exists, and what each mechanism costs

| Mechanism | What it holds a session to | Fit for an owed rewrite |
|---|---|---|
| `OWED_A_REPLY` and `_received` (observed: `db.py` 1505 to 1528, 1838 to 1880) | A woken session that sends no message caused by the trigger and writes no receipt leaves the trigger `unresolved` | **Poor.** `unresolved` climbs a question ladder to a role that has not spoken in the thread (observed: `predicates.unresolved`, 1345 to 1466). For a Liaison relay, that is another artefact owner, which cannot write the guess (reasoned). Also `_received` matches the trigger's refs against row keys, and `guess:<item>` never equals a `touch_guesses` key `<item>:<ver>:<ruling>:<grain>` (observed: `db.py` 1869 to 1873, `api.py` 9045). A `RECEIPT_RULES` entry keys on the edge, and the Liaison-to-Architect relay edge carries three modes with three different writes (observed: `runner.py` 405 to 414, `db.py` 1535 to 1548) |
| Frame 267's page reply and frame 320's request (observed: `db.py` 1559 to 1616, 2081 to 2104) | A barren session leaves the message open with its reason as a note. The same seat wakes once more. The second miss closes it and tells him in one Liaison line. `REPLY_SESSIONS = 2` | **Good shape, wrong carrier.** The retry goes to the same seat, and the note puts the reason in the next head. But it keys on the message, so a relay that is never sent escapes it (reasoned: section 1, the verdict gap) |
| Law 4, "Failure is bounded" (observed: `rota/LAWS.md` 164 to 167) | A crashed session leaves its trigger open with its attempts raised. Past `message_attempt_cap`, 3, it is quarantined (observed: `config.py` 86) | Covers a crash, not a session that commits prose (reasoned) |
| Law 6, "Escalation only climbs" (observed: `LAWS.md` 183 to 200) | "A question nobody answers climbs (`unresolved`). A wake dispatched past its cap is quarantined and said out loud (`quarantined`)." | The quarantine half fits. The climb half is for a question (reasoned: above) |
| The tick bound, `tick_attempt_cap` 3 (observed: `config.py` 127; frame 298's design, 4.2, "A session that writes no row leaves the predicate true ... quarantines the key after three attempts") | A predicate that stays true wakes its seat again, then quarantines | **The best carrier.** It needs a predicate that reads the owed write as a state. Today `guess` cannot, because a set exists at the item's version (observed: `predicates.py` 336 to 337) |
| The item's `contested` state (observed: `predicates.py` 301 to 316) | The record holds the contest. The owner wakes until the state changes. `next_batch` reads the state | **The model for the class.** But `items.approval` is a column that `land` writes. For the guess and the touch set, a stored mark would be a second writer of the Architect's tables (reasoned: law 1, "one writing role per row") |

**The shape the design takes (reasoned: the table).** The owed write is derived, as the item's is, and not stored. One function reads his landed ruling and the owner's table, and says whether a write rests on the ruling. A predicate reads that function, so the tick bound gives frame 320's retry and law 6's quarantine with no new counter. Law 6's own reason applies: "a stored rung is a second record that can disagree with the wakes that *are* the escalation" (observed: `LAWS.md` 196 to 199).

**What a relay that ends with no write costs under slice 1 (reasoned: from s145's figures).**

- Wakes: the relay, then at most 3 `tick:guess` wakes, then the quarantine line. That is 4 Architect sessions at most. A tick wake is one session (law 4).
- Turns: s145 used 2 turns and about 20 s of model time, from 06:08:24 to about 06:08:44 (observed: the read, section 1). Four such wakes are about 8 turns and about 80 s of model time.
- The annotate seat is a second owner. When the batch forms during the retries, `annotate` fires on it with his words. One write of either seat ends the cost (reasoned: section 6, slice 1).
- What he sees, and when. While the fact is true, no batch of the item starts, so no touch note shows a set written before his words (reasoned: section 3). If every seat fails, the agenda shows one stuck line, after the fourth Architect session, about 80 s of model time after his reply. Today he saw the old set on the touch page m31 about 54 s after his reply, and then 3 Developer sessions on the wrong file (observed: the read, section 1, rows 8 to 10).

## 3. The stale record: every reader, today and under the design

The map tool names 11 readers of `touch_guesses` and 8 of `batch_touch` (observed: `map table touch_guesses`, `map table batch_touch`). The design changes the readers that seed work or show the set to him.

| Reader | What it reads today after an unanswered contest | What it reads under the design while the write is owed |
|---|---|---|
| `runner._guess_seed` (observed: `runner.py` 4262 to 4287) | The newest set, the sign-off set with `ruling_id` '', with no words of his (observed: the read, section 1, row 7) | His words in the files-contest block, and no path of the contested set. The block "never lists a path of `expected` or `possible`", because models read a listed set as his own list (observed: `_files_contest_block` docstring, `runner.py` 953 to 973) |
| `architect/annotate.md` line 6 | "`the item's guess` is what you guessed at sign-off, and what the principal corrected" (observed) | One sentence more: when the principal's words stand under the guess and no path does, start from the paths his words name (reasoned: the brief rule for a model text) |
| `runner.resolve_inbound`, the relay branch (observed: the read, section 1, row 4) | The old set as `guess`, and `disputed: []` | The same on the relay. A `tick:guess` wake under an owed contest gets the same inbound, `principal_said` and `principal_verdict`, so its write stamps his ruling. Today `batches_guess` stamps the ruling only when the trigger is the relay (observed: `api.py` 9030 to 9041) |
| `predicates.guess` | False, because a set exists at the item's version | True while the guess line is owed |
| `predicates.annotate` | False on a batch with touch rows | True on a batch whose code line is owed and whose touch rows were written before his ruling |
| `scheduler.next_batch` (read by `tick_batch_start` and `preempt`) | Offers the batch (observed: `scheduler.py` 1884 to 1898) | Leaves out a batch whose item's code line is owed |
| `principal.code_target` and `code_line` (observed: `principal.py` 2068 to 2128) | A later page shows "The team's guess at the code this touches: " and the stamped set | A page sent while the line is owed shows "You corrected this guess. The team has not rewritten it yet." in place of the set (reasoned: the composition, "never ... treats silence as consent") |
| `lifecycle.predicted_rows`, `touch_set`, `first_touch_rows` | The touch set | No change. While the line is owed, the gate keeps the batch out, so these read only a set written after his ruling (reasoned) |
| `bound_constraints` | Follows the touch set (observed: the read, section 4) | No change. It follows the touch set by itself (observed: the read, section 4, the FIXED build) |
| `land` (observed: `principal.py` 3745 to 3769) | Moves a guess contest to the batch line when the stamped target is a batch with a head commit | No change. The fact reads both the guess line and the batch line |
| `nightreport._guess_section`, `audit.orphaned_grain_refs` | Reports | No change in slice 1. The night report gains the owed count in slice 3 |

## 4. The gate: what waits on what

### 4.1 The rulings, quoted

- The composition, "Flows": "A prediction never blocks. Only a fact or a ruling gates." (ruled: ratified 2026-09-16; observed: `plans/composition.md` line 73).
- R7, through P4: "Non-blocking by R7: nothing waits on the principal's reaction; the steering loop (cancel/preempt, already pinned) is the lever if the scope smells wrong. A blocking variant, if ever wanted, is a config setting in the `merge_gate` mould" (ruled: R16/R17, 2026-09-03; observed: `plans/archive/p4-scope-disclosure.md` lines 5 to 9).
- Frame 298's design, 4.3, "What the sign-off waits on": "**Nothing new** (copied: P4, "Non-blocking by R7"; reasoned: a prediction never blocks). `tick_signoff` and the Vision Keeper's `submit` brief do not name the guess" (observed: `plans/frame298-design.md` 408 to 413). The section is about the sign-off waiting on the guess. It is not about a batch start waiting on a rewrite (observed: its heading). Its "a prediction never blocks" is a design session's reasoning (observed: the mark "reasoned").
- Law 8: "No batch schedules unless its item's approval postdates the item's last amendment" (observed: `LAWS.md`, section 8). A start already waits on a fact of the record.
- Frame 87: "A deferred batch with a quarantined key stays out too, so its siblings start while the principal decides" (ruled: 2026-09-27; observed: the comment in `scheduler.next_batch`, `scheduler.py` 1904 to 1905).

### 4.2 What waits under the design

| Phase | What waits | On what | A fact, a ruling or his reaction? |
|---|---|---|---|
| Before his reply | Nothing new. The sign-off, the touch note and the start do not wait on the guess | Nothing | Not applicable (reasoned: the fact needs a landed contest, so no contest means no wait) |
| He contests, and the owner has not written | The item's batch start | The owner's write under his ruling | **A ruling and a fact.** The ruling exists. The missing write is the team's (reasoned) |
| The owner writes | Nothing new | Nothing | The fact is false (reasoned) |
| Every seat failed, the key is quarantined | The item's batch start | His decision on the stuck line, or a new ruling | **His reaction.** See 4.4 |

### 4.3 Why the middle phase does not cross R7 or the composition (reasoned)

The guess is a prediction, and the guess never blocks under the design. What blocks is the absence of a write under his ruling. His contest is a ruling, and the composition says that a ruling gates. R7 forbids a wait on his reaction. In the middle phase his reaction already exists, and the wait is on the team. P4 names "the steering loop (cancel/preempt)" as his lever "if the scope smells wrong" (observed: P4). On m27 he used a lever of that kind, and the start ignored it. The gate makes his lever act. It adds no wait for him.

The touch note stays non-blocking. `batch_start` still never waits on the note's answer (observed: the `touch_note` docstring, `predicates.py` 1059 to 1066). Under the design, a touch note can go out only for a touch set that rests on his ruling or that he has not contested (reasoned: section 3).

### 4.4 The exhausted end crosses R7, and frame 87 already covers it

When the relay and three retries write nothing, and the annotate seat also writes nothing, the key is quarantined, and the batch waits on him. That is a wait on his reaction. R7 of 2026-09-03 forbids it for the scope disclosure. Frame 87 of 2026-09-27 rules it for a batch with a quarantined key (reasoned: 4.1). The departure from R7 is real but narrow. It happens only after four failed sessions, and the other batches go on. The two other choices are worse (reasoned):

- Start the batch on the contested set. That is the measured fault: 0 of 20 first replies open his file (observed: the read, section 7.2).
- Start the batch with no touch set and his words alone. No case measures it. A mechanical set from his file names would cross the ruling "Remove the mechanical guess, the architect owns the guess" (ruled: Roman, 2026-10-18 about 12:05; observed: `frame298-design.md` 12 to 14).

So the page asks Roman the question in the result. Until he rules, the build follows frame 87, and the stuck line says the reason (reasoned).

## 5. Three designs

### Design A: the relay owes its write (the message shape)

- **What.** A relay whose mode names a write, `guess`, `annotate` or `criterion_repair`, owes a write on that mode's table. A session that writes nothing leaves the relay open with its reason as a note. The same seat wakes once more. The second miss closes the relay and sends one Liaison line, as frame 320 does. `_guess_seed` gives his words and no contested path.
- **Files and functions.** `rota/core/db.py`: a `RELAY_WRITES` map from mode to table beside `OWED_A_REPLY`, a `_relay_missed` beside `_request_missed`, and one branch in `session_commit`. `rota/core/runner.py`: `_guess_seed`. `architect/annotate.md` line 6.
- **Size.** About 60 lines of code and 80 lines of tests (reasoned: frame 320's branch and its helpers are of that size, `db.py` 1587 to 1720).
- **Recorded cases that change.** m27, if the second relay session writes. The other 4 guess contests and the 6 touch contests wrote on the first relay, so they do not change (observed: the read, 5.1 and 5.2).
- **Loop risk.** Low. `REPLY_SESSIONS` bounds the retry at 2 (observed: `db.py` 1556).
- **What he reads when the team fails twice.** One Liaison line: the team did not rewrite the guess he corrected, with the reason. **The batch can still start,** because nothing orders the retry before `tick_batch_start` (reasoned: in dry 6b the start came about 56 s after the relay, the read, section 1).
- **Holes.** It does not see a relay that is never sent (section 1, the verdict gap). It does not stop a start during the retry. It does not stop an annotate seat that copies the old set.

### Design B: the code line's owed write is a derived fact (slice 1 of C)

- **What.**
  1. `owed_rewrites(conn)` in one place, as `OWED_A_REPLY` is the one list of its fact. For the code line of an item, the fact is true when three things hold. His newest landed ruling that `land` routes to the Architect contests or revises `guess:<item>` or the item's batch line. No `touch_guesses` set carries that ruling. No `batch_touch` row of the item's live batch was written after it.
  2. `predicates.guess` fires for an item with an owed guess line. `predicates.annotate` fires for a live batch whose touch rows predate an owed ruling on the code line.
  3. A `tick:guess` wake under an owed ruling gets the relay's inbound, `principal_said`, `principal_verdict` and `disputed`, so `batches_guess` stamps the ruling.
  4. `_guess_seed` under an owed ruling gives his words in the files-contest block and no contested path. `annotate.md` line 6 says how to read that.
  5. `next_batch` leaves out a batch whose item has an owed code line.
  6. Under a `contest`, the write door of `batches.guess` and `batches.annotate` refuses a set equal to the contested set. A `revise` takes any write. s150 sent the seed back whole (observed: the read, section 1, row 7).
- **Files and functions.** A new `owed_rewrites` in `rota/core/scheduler.py` beside `next_batch` (reasoned: its readers are the scheduler and the predicates). `predicates.guess`, `predicates.annotate`, `scheduler.next_batch`, `runner.resolve_inbound`, `runner._guess_seed`, `api.batches_guess`, `api.batches_annotate`, `architect/annotate.md`.
- **Size.** About 120 lines of code and 150 lines of tests (reasoned).
- **Recorded cases that change.** m27 in every arm: either a later write, or no start and a stuck line (reasoned). The other 10 contests do not change, if the fact reads false after their first write (reasoned; the check is in section 7.1). dry 4 m50 and dry 6b m40 are a `revise` with no words and no relay (observed: the read, 5.2). The fact must read false on them, or the annotate seat wakes on them for nothing. So the fact counts only the lines that `land` routes to an owner (reasoned).
- **Loop risk.** Bounded. The tick bound quarantines after 3 attempts (observed: `config.py` 127). The equal-set door can turn a seat that copies into a quarantine, not into a loop (reasoned). A new set that he contests again is a new ruling, and his replies bound that loop, as frame 298's 4.2 says (observed).
- **What he reads when the team fails twice.** Nothing yet. After the relay and 3 retries, one stuck line on the agenda: "Stuck: the guess of <item> stops here. The team could not rewrite the guess you corrected after 3 attempts." The form copies the `tests_missing` stuck line of dry 6c (observed: `dry6c-read-2026-11-06.md`, the result). No touch note shows the old set (reasoned).

### Design C: every owner-written kind (the class)

- **What.** Design B's fact for every open kind of section 1, with one row per kind in `owed_rewrites`: the line, the owner, the mode, the table, and the reader that must not seed from the contested text.
  1. The criterion: owed until `criteria.respecify` writes under his ruling. `tests_missing` does not encode a criterion with an owed rewrite. A criterion contest outside a park page gets a route to `criterion_repair`, or the page offers no rewrite for it (reasoned: section 1).
  2. The readers: `code_target` and `code_line` show the owed line, as section 3 says. The night report counts the owed lines.
  3. The term and the constraint: the adopt of approved ids is owed until `glossary.adopt` or `model.adopt` writes. `bound_constraints` does not push a constraint he contested (reasoned; the reader is not read, section 1).
  4. The statement rewrite has no tool. The page offers no rewrite on a statement, or a tool is added. That is a page question, not an owed write (reasoned).
- **Files and functions.** Design B's, and `predicates.tests_missing`, the `criterion_repair` route in `runner._mode_key`, `principal.code_target`, `principal.code_line`, `api.bound_constraints`, `nightreport._guess_section`, the adopt receipts.
- **Size.** About 250 lines of code and 300 lines of tests, over four slices (reasoned).
- **Recorded cases that change.** Design B's. On criteria and terms, the recorded runs give no measured miss, because the read counted guess and touch lines only (observed: the read, section 5). So slices 2 to 4 start with a reach count, as rule C76 asks (reasoned: the memory "read before fix").
- **Loop risk.** As B, per kind. A kind with no write tool must never become owed, or it quarantines with no seat that can write. So the statement rewrite stays out of the fact (reasoned).
- **What he reads when the team fails twice.** As B, with the kind named in the stuck line.

### Rejected: a mechanical write from his words

`land` could write his named files as the guess. That crosses "the architect owns the guess" (ruled: Roman, 2026-10-18). Frame 298 also removed the reading of his words by patterns after twelve reviews found missed forms (observed: `disputed_paths` docstring, `runner.py` 2114 to 2121).

## 6. The recommended design, in slices

Design C, in this order. The biggest measured cause is first (reasoned: CLAUDE.md, "the biggest issue comes first").

1. **Slice 1, the code line (design B).** `owed_rewrites` for `guess:<item>` and the batch line. The two predicates, the tick inbound with his ruling, the seed, `annotate.md` line 6, the gate in `next_batch`, and the equal-set door. It closes m27 end to end: no start on the contested set, a start on a set written after his words, or a stuck line (reasoned). Measure it as section 7 says.
2. **Slice 2, the criterion.** Count the reach first: criterion contests on the recorded runs, their relays and the sessions that wrote nothing. Then the criterion row of `owed_rewrites`, the gate in `tests_missing`, and the route outside a park page.
3. **Slice 3, the readers he sees.** `code_target` and `code_line` show an owed line. The stuck line names the kind. The night report counts owed lines.
4. **Slice 4, the adopts and the statement.** Count the reach of a term or constraint relay that adopted nothing. Then the adopt row, the `bound_constraints` check, and the page choice for a statement rewrite.

The verdict gap of section 1 closes with slice 1 for the code line, because the fact reads the ruling and not the relay (reasoned).

## 7. The measurement for slice 1, with no new run from zero

### 7.1 The checks that need no model

1. Run `owed_rewrites` on the five run databases at `immutable=1`, at the state before each recorded batch start after a contest (observed sources: `GR/reach.py`, `GR/reach.json`). Expected: true for m27 from s145's commit to s171's write, and false for the other 10 replies at their next start. False also on dry 4 m50 and dry 6b m40, the `revise` lines with no relay.
2. On a copy of `dry6b/runs/w7/dry6b.db` loaded in memory, as `GR/build_fixed.py` does, call `next_batch`. Expected: `b_1` is left out. After the insert of s171's two paths as rows written after r_m27, `b_1` is offered (reasoned: the same in-memory change as the FIXED build, the read, 7.1).
3. Unit tests with seeded rows: the fact per line kind, the gate, the tick inbound that stamps the ruling, and the equal-set door under a contest and not under a revise.

### 7.2 The replay of turn 6

What exists (observed):

- The database before turn 6: `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1b9e813c-4464-4439-95c2-d0e1bf698557/scratchpad/dry6b/runs/w6/dry6b.db` with its `-wal` and `-shm` (observed: `ls`). The final run database holds every turn of s143 to s156, with `system`, `user`, `completion` and `sessions.pins_json` (observed: the read, section 7).
- The turn driver `dry6b_turn.sh`: copy, `git checkout --detach <commit>` in `rota_dry6b`, `rota.cli sign dry6b m26 --say <words>`, `rota.cli run dry6b --all` (observed).
- `probes/seed_night_cassettes.py` fills a cassette from a run's `turns`, keyed by `cassettes.key_for`, the model, the options and the prompt hash (observed: its docstring). `probes/night_cassette.py` `wrap` replays a hit and calls the server on a miss, for the `onboarding` phase only (observed: its docstring and the test at `tests/rota/test_frame233_night_cassette.py` 78 to 100).

What to add, in the scratch directory (reasoned):

1. A seed argument that takes the sessions of turn 6, s143 to s156, and not only the onboarding sessions.
2. A wrap phase for the replay that replays every hit. s143, s144 and s145 have the same prompts under slice 1, because slice 1 changes only what follows s145's commit. So s145's recorded reply replays by itself.
3. A force map for the worst case: every wake in mode `guess` on the item takes s145's recorded completions, so the Architect never writes a set.

Run the two arms at the slice 1 commit, on a copy made with the SQLite backup API:

| Arm | The guess wakes | The other wakes after s145 | Today | Pass line |
|---|---|---|---|---|
| Forced | s145's recorded reply, every time | Live on a miss: the annotate seat, the Liaison, the Developer | 3 starts of `b_1`, 0 read his files (observed: the read, section 1) | 0 starts on the contested set. Every start of `b_1` has `string.py` and `test_icalendar.py` in its `[batches.expect]` line, or no start and the stuck line |
| Live | s145 replays once, the retries run live | Live on a miss | As above | As above, and at least 1 start that reads his files |

Count from the copy, as the read counted: each `tick:batch_start` session on `b_1`, and its first `turns.user` line `[batches.expect]` (observed method: the read, section 1, row 9). Use the 3080's server on `127.0.0.1:11434`, the run's model `qwen3:8b` for the turn, temperature 0 (observed: `dry6b_turn.sh` names `ROTA_MODEL=qwen3:8b`). The Developer's first reply on the fixed set is already measured: 4 of 4 open `string.py` (observed: the read, 7.2). So the replay must prove the path to the start, not the Developer's reply.

### 7.3 What the register needs

- **Add** a case from s145's prompt: the guess relay on the dry 6b prompt, with its 4,314-character `the index's test files` key. Expected: `batches.guess` with `string.py` (observed shape: the read, 5.1). Today it is red at 0 of 1 recorded. It names the seat's own miss, which slice 1 survives and does not fix.
- **Add** a case `tick: guess` under an owed ruling, with `principal_said` in the inbound. Expected: one `batches.guess` with his paths.
- **Add** a case `tick: annotate` under an owed ruling, from s150's prompt with the new seed. Expected: `batches.annotate` with `string.py` and no `property.py`.
- **Re-record** the annotate cases if `annotate.md` changes the brief hash: `L1-AR-annotate-a-batch`, `L1-AR-annotate-from-the-guess`, `L1-AR-re-annotate-from-the-principals-correction` (observed: `tests/rota/cases/l1_architect.yaml` lines 8, 46, 469).
- **Keep** `L1-AR-rewrite-the-guess-from-the-ruling` and `L1-AR-guess-the-code-of-a-request` unchanged, unless the guess brief changes (observed: lines 88 and 117).

## 8. What is unproven

- Why s145 sent reads and not the call, when s199 sent the call on the same words (observed: the read, section 9). The guess brief ends "After the call, end the session with one line: "guessed <item>."" (observed: `architect/guess.md`). s145 wrote that line with no call. Whether the end line invites the miss is not measured (reasoned).
- That the annotate seat writes his files from his words alone in the files-contest block, with no contested path. s171 did so on the batch relay (observed: the read, section 3). The tick wake is a new prompt (reasoned).
- That the fact can tell, from the rows, which lines `land` routed to an owner. The join of the ruling, the verdict and the set's `ruling_id` is a build detail (reasoned). `touch_guesses.ruling_id` holds the verdict message id (observed: `api.py` 9038 to 9041).
- The reader cells marked "RA: unverified" in section 1.
- The sizes of section 5 are estimates (reasoned).

## 9. Usage

One Opus designer and one reader agent for the table of section 1. No model call, no suite, no run database written. The repository changed by this page only.
