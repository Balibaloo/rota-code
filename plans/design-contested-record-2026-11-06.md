# Frame 362, a design before any build: a record that he contested and nobody rewrote, 2026-11-06

The brief is `scratchpad/f362_contested_record_design_brief.md`. The measured fault is in `plans/f362-contested-guess-read-2026-11-06.md` (below: the read). The review is `plans/design-contested-record-review-2026-11-06.md` (below: the review), with its probes in `scratchpad/rc362/` (below: `RC`). This page is revision 2. It calls no model and runs no suite, and it edits no tracked file but itself (observed). A mark "(observed, RA: place)" means that a reader agent read the code at that place. A mark "(observed, review: place)" means that the review's probe or read found it, and this page did not run the probe again. Revision 2 finished 10:38 (observed: `date`).

## Result

**The design: one rule. A contest or revise of his on ref X, with ruling V, stays owed until a row of X's owner rests on V. "Rests on V" means that the owner's write carries the ruling: a `refs` row of kind `ruling`, or a `ruling_id` column where a table has no `refs` rows.** The fact is derived on every read and is never stored. Each reader that seeds work or shows the record calls one function, `owed(conn, ref)`. A twelfth kind of record needs nothing but this: its owner's write carries the ruling (reasoned: section 1).

The story of one reply under slice 1, on dry run 6b's m27 (reasoned: sections 2 to 4):

1. He reads the sign-off page and writes "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py ..." The Liaison lands ruling r_m27 with a contest on `guess:<item>`. The relay goes to the Architect, as today.
2. The relay session reads `string.py`, ends with "guessed ...", and writes nothing. The commit marks the relay answered, as today. The relay's status no longer matters, because the owed write is read from the ruling.
3. `owed` finds no `touch_guesses` row that carries r_m27's verdict. So the code line of the item is owed.
4. While it is owed: `tick:guess` wakes the Architect with the refs `(item, verdict)` and his words in the inbound. `annotate` does not fire for the item. `touch_note` leaves the item's batch out. `next_batch` does not offer the batch.
5. A retry writes a set that carries the verdict. The fact is false. `annotate` then seeds from the new set and his words, and its write carries the ruling too. The batch starts on files written after his words.
6. When the relay and three retries write nothing, the key `architect|tick:guess|(item, verdict)` is quarantined, and the item parks. The park page gives him the way out: say what to change, or give the request up. The other items go on.
7. If he contests again while the first write is owed, the newer ruling replaces the first. One write is owed, on the newer ruling, with its own key and its own three attempts.

**No question for Roman is left.** The exhausted end is a per-item park, which R7 and R10 of 2026-09-02 expect, and which frame 87 of 2026-09-27 rules for a batch the team gave up on (reasoned: section 4).

### Slice 1, the build brief

1. Files: `rota/core/schema.sql` and its migration, `rota/core/scheduler.py`, `rota/core/predicates.py`, `rota/core/runner.py`, `rota/roles/api.py`, `rota/roles/prompts/architect/annotate.md`, `rota/core/identity.py`.
2. Schema: add `batch_touch.ruling_id TEXT NOT NULL DEFAULT ''`, as `touch_guesses` has. Add the column to the identity row of `batch_touch` (observed, review: `identity.py` 84).
3. `scheduler.owed(conn, ref)`: the newest landed ruling with `verdict_id` not null that contests or revises a line of the item's code line (`guess:<item>` or the item's batch id). It is owed when no row of the owner table carries that verdict.
4. `scheduler.owed_ruling(ctx)`: the ruling a write rests on. It comes from the relay chain (`_principal_relay`) or from the tick refs `(item, verdict)`.
5. `api.batches_guess` stamps `owed_ruling(ctx)` on a relay and on a tick. `api.batches_annotate` stamps it, and clears the contested set when it is set, by relay or by tick. `api.batches_judge_touch` writes `ruling_id` '' (a foreseen row discharges nothing).
6. The equal-set door in `batches_guess` and `batches_annotate`: under an owed `contest` (not a `revise`), refuse a set equal to the contested set.
7. `predicates.guess`: fire for an item whose guess line is owed, with refs `(item, verdict)`. `predicates.annotate` and `predicates.touch_note`: leave out an item whose code line is owed on the guess line.
8. `runner.resolve_inbound`: a `tick:guess` with a verdict in its refs gets `principal_said`, `principal_verdict` and `disputed`, as the relay does. `runner._guess_seed` under an owed ruling gives his words in the files-contest block and no contested path. `annotate.md` line 6 gains one sentence for that case.
9. `scheduler.next_batch` leaves out a batch whose item's code line is owed. `scheduler.parked` is true for the batches of an item whose owed key is quarantined, so `park_ask` sends the page with the way out.
10. Tests, in this order: the stamp on each writer; `owed` on seeded rulings (contest, revise, no verdict, a second contest); the clear on a tick; the equal-set door; the tick refs and inbound; `touch_note`, `annotate` and `next_batch` under an owed line; the park and its page; the second contest gets a fresh key.
11. Check A, no model: `owed` on the recorded contests (section 7.1). m27 is owed from s143 until s171's write under the newer ruling r_m39. Nothing is owed after the write on dry 5 m37 and night 166 m28, m53, m69.
12. Check B, no model: `next_batch` on an in-memory copy of `w7` with `b_1` set `pending` and `developer|tick:batch_start|b_1` removed. Today it gives `['b_1']` (observed, review: `RC/p6_w7.py`). Slice 1 must give `[]`.
13. Check C: the unit tests of step 10.
14. Then one live arm as evidence of capability, not as the gate (section 7.2).
15. Size: about 220 lines of code and 240 lines of tests (reasoned: the review's 200 and 220, plus the tick key and the park).

## 1. The one rule, kind by kind

The owner of a ref is the relay split's lookup by the single-writer law: `RULED_TABLES`, `_owner_of_ref`, and the `GUESS_RELAY` and `BATCH_RELAY` keys (observed, review: `sandbox.py` 953 to 975 and 4960 to 4973). "Rests on V" exists in two forms today. `_adopt_rows` stages a `refs` row of kind `ruling` with the `rulings` id from `_landed_ruling` (observed: `api.py` 2763 to 2809). `touch_guesses.ruling_id` holds the verdict message id, and the join is `rulings.verdict_id = touch_guesses.ruling_id` (observed, review: section 1.1; `api.py` 9030 to 9041). The `refs` table takes rows from `items`, `glossary_terms`, `constraints`, `model_areas`, `frame_rulings`, `criteria` and `business_rules` (observed: `schema.sql` 96 to 106). `owed` accepts both forms through one join (reasoned).

| # | Kind, ref X | Owner of X | A row that rests on V | Exists today? |
|---|---|---|---|---|
| 1 | Guess line, `guess:<item>` | Architect, `touch_guesses` | A `touch_guesses` set with `ruling_id` = V's verdict | Yes, on a relay only (observed: `api.py` 9030 to 9041). Slice 1 adds the tick |
| 2 | Batch line, `b_<n>` | Architect, `batch_touch` | A `batch_touch` set with `ruling_id` = V's verdict | No column (observed: `schema.sql` 390 to 397). Slice 1 adds it |
| 3 | Criterion | Terminologist, `criteria` | A `refs` row `criteria`, the criterion id, kind `ruling`, target V, staged by `criteria.respecify` | No. `criteria_respecify` stages no ruling ref (observed: `grep`). Slice 2 |
| 4 | Test row | As its criterion (observed, RA: `sandbox.py` 4947 to 4958) | As row 3 | As row 3 |
| 5 | Glossary term, contested | Terminologist, `glossary_terms` | A `refs` row of kind `ruling` on the new sense | The relay mode has no write for a contested sense, "not yours to fix in this session" (observed: `terminologist/relay.md`). Slice 4 gives the owner a write, or the page offers no rewrite |
| 6 | Constraint or model area, contested | Architect, `constraints` or `model_areas` | A `refs` row of kind `ruling` on the new row | As row 5 (observed: `architect/relay.md`). A contested constraint is still pushed by `_bound_rows` (observed, review: `api.py` 4776 to 4803). Slice 4 |
| 7 | Statement, a rewrite | Vision Keeper, `statements` | None possible: `statements` is not a `refs` source and has no contested state (observed, review: `schema.sql` 40 to 42) | No write tool (observed, RA). Slice 4: the page offers no rewrite, or a tool with a `ruling_id` |
| 8 | Item, the request's text | Vision Keeper, `items` | The amend or the defending decision. `items.approval` leaves `contested` only then (observed: `predicates.py` 301 to 316) | Yes, as a state. `owed` reads `approval = 'contested'` as owed, with no new code |
| 9 | Team note | `land`, at the keypress (observed, RA: `principal.py` 3821 to 3897) | The principal decision that `land` writes | Yes, by construction. Never owed |
| 10 | Step, a stopped tick key | `land` (observed, RA: `principal.py` 3677 to 3682) | `lift_keys` or `mark_ruled` | Yes, by construction. Never owed |
| 11 | Read-back | `land` (observed, RA: `principal.py` 3666 to 3667) | The `ruled_refs` row | Yes, by construction. Never owed |

**One record, two refs (reasoned).** The guess line and the batch line are two refs of one fact, the item's code line. `land` already moves a guess contest to the batch line when the page showed the batch's plan (observed: `principal.py` 3745 to 3764). So `owed` reads the newest ruling on either ref, and a newer ruling on the batch line replaces an owed guess ruling. This is the second-contest rule of the result, step 7, and not a rule per kind.

**What a twelfth kind needs (reasoned).** Its owner's write stages a `refs` row of kind `ruling`, or writes a `ruling_id`. The relay split already names its owner. No new predicate branch, no new list and no new discharge rule are needed. Its readers call `owed`.

**An approve that is owed.** The adopts of rows 5 and 6 are approves, not contests. A relay that adopts nothing leaves an approved row `observed` (observed: `architect/relay.md`, "With no approved id, end the session with no call"). `_adopt_rows` already stamps the ruling (observed: `api.py` 2809), so the same rule reads an approve as owed until the stamp exists. Slice 4 decides whether to include approves (reasoned).

**The verdict gap closes by the rule (reasoned).** `land` writes the verdict, and a Liaison `verdict_signoff` session that sends no relay also reads answered (observed, RA: `principal.py` 3979 to 3985). `owed` reads the ruling, so it sees the gap. The tick wakes the owner with no relay.

## 2. The owed write, and what a write that never comes costs

The carrier is the tick bound, not `OWED_A_REPLY`. `unresolved` climbs a question ladder to another role, which cannot write the owner's row (observed: `predicates.unresolved`). `_received` matches refs against row keys, and `guess:<item>` never equals a `touch_guesses` key (observed: `db.py` 1869 to 1873). The tick bound quarantines after `tick_attempt_cap` 3 (observed: `config.py` 127). The key carries the verdict, so each ruling has its own bound and its own report (reasoned: review section 3, point 1).

**The worst case, every seat ends with prose (reasoned from the review's table, section 3).**

| # | Session | Bound | Model time at the recorded rate |
|---|---|---|---|
| 1 | The relay, mode `guess`, as s145 | the message | 20.8 s, 3 turns (observed, review: s145 `turns.ms`) |
| 2 to 4 | `architect\|tick:guess\|(item, verdict)` | `tick_attempt_cap` 3 | about 62 s |
| 5 | `liaison\|tick:quarantined` for that key | once per key (observed, review: `quarantined_keys(unreported=True)`) | about 3 s |
| 6 | `liaison\|tick:park_ask` for the held item | once per park | about 3 s |

So 4 Architect sessions and at most 2 Liaison sessions, about 89 s of model time. `annotate` does not fire while the guess line is owed, so its own 3 retries of the review's count do not happen. If the park page marks the key reported, sessions 5 and 6 are one session (reasoned; not read). A session is bounded by `ROTA_MAX_ITERATIONS=24`, not by s145's rate, and s160 spent 134 s in 7 turns (observed, review). So the model time can be several times more.

**What he reads, and when.** No touch note, because no touch set exists for the item. The quarantine line, then the park page with the way out, after about 90 s of model time or more. Today he saw the old set on m31 and three Developers on the wrong file (observed: the read, section 1).

**A second contest while the first is owed.** The fact reads the newest ruling, so one write is owed, on the newer verdict. Its key `(item, verdict 2)` is fresh, so it gets three attempts and its own report. The park is derived from the newest ruling's key, so a new ruling ends the park with no lift code (reasoned). A late write that carries the first verdict discharges nothing, and costs one more wake at most (observed, review: section 3, point 3).

## 3. The readers, today and under slice 1

| Reader or writer | Today after an unanswered contest | Under slice 1 while the line is owed |
|---|---|---|
| `runner._guess_seed` (observed: `runner.py` 4262 to 4287) | The sign-off set, no words | Not read: `annotate` does not fire. After the stamped rewrite: the new set and his words, as today on a ruled set |
| `predicates.guess` (observed: `predicates.py` 333 to 337) | False, a set exists at the version | True, refs `(item, verdict)` |
| `predicates.annotate` (observed: `predicates.py` 1048 to 1051) | True on a batch with no touch rows | False for the item |
| `predicates.touch_note` (observed, review: `predicates.py` 1079) | Sends the old set | Leaves the batch out |
| `scheduler.next_batch` (observed: `scheduler.py` 1884 to 1898) | Offers the batch | Leaves it out |
| `api.batches_annotate` (observed, review: `api.py` 9119 to 9127) | Clears only on a relay, an upsert keeps the contested paths | Clears and stamps under `owed_ruling` |
| `api.batches_judge_touch` (observed, review: `api.py` 28310) | A second writer of `batch_touch` | Writes `ruling_id` '', discharges nothing |
| `principal.code_target`, `code_line` (observed: `principal.py` 2068 to 2128) | Shows the stamped set | No change in slice 1. Slice 3 shows the owed line |
| `lifecycle.predicted_rows`, `touch_set`, `first_touch_rows`, `db.batch_reads`, `lift_moved_reads` (observed, review) | Read the touch set | No change. The gate keeps an owed set from a start |
| `bound_constraints` (observed: the read, section 4) | Follows the touch set | No change |
| A batch-line contest on a running batch | `land` lifts the running seats, and the Developer reads the new set after a write (observed, review: section 5) | No change in slice 1. Recorded as open |

## 4. The waits

The texts, quoted:

- R7 (2026-09-02, observed: `plans/archive/responsibility-audit.md` 332 to 335): "Varies, and blockages are expected: whatever is not blocked keeps going, whatever is blocked parks, and work can be discarded if required. The system may never depend on response latency; blockage is per-item, never global."
- R10 (2026-09-02, observed: the same page, 348 to 349): "Park it as a blockage. Consistent with R7: the item blocks and waits, everything unblocked keeps going."
- R7 as P4 applies it (ruled R16/R17, 2026-09-03; observed: `plans/archive/p4-scope-disclosure.md` 5 to 9): "Non-blocking by R7: nothing waits on the principal's reaction; the steering loop (cancel/preempt, already pinned) is the lever if the scope smells wrong."
- Frame 87 (ruled: Roman, 2026-09-27; observed: `plans/stack.md` 3623 to 3630): "a given-up batch put back in the chair waits for the principal ... the batch stays parked, the page says so with the way out, the principal says what to change or gives up on it, and the siblings start meanwhile."
- The composition, Flows (ruled: ratified 2026-09-16; observed: `plans/composition.md` 73): "A prediction never blocks. Only a fact or a ruling gates."

**What waits on what (reasoned).** Before he contests, nothing new waits, and the touch note stays non-blocking. After he contests, the start of that item's batches waits on the team's write under his ruling. That is a ruling and a missing fact, and his reaction already exists. When the write lands, nothing waits. When the team spends its attempts, that item parks, its page gives him the way out, and every other item keeps going. That is the per-item park of R7 and R10. It is the shape that frame 87 rules for a batch the team gave up on. P4's sentence is R7 applied to the disclosure: no batch waits on his answer to the touch note, and under slice 1 none does.

**Is a departure left?** I read the three texts and see none. R7 forbids a global block and a dependence on his response latency. The park is per item, and the rest of the work does not depend on when he answers. So the question of revision 1 is dropped. Revision 1 also said that frame 87's park "already covers" the end. That was wrong in mechanism: `parked` is true only for a deferred batch with a given-up key (observed, review: `scheduler.py` 2779 to 2795). Slice 1 step 9 adds the park of the held item.

**A design with no wait on him** starts the batch with an empty touch set and his words alone. No case measures it, and the words alone did not move the seat, 0 of 20 with the old set (observed: the read, 7.2). R7 does not ask for it, so the item parks (reasoned).

## 5. Three designs

| | A: the relay owes its write | B: the code line, a hand fact (revision 1's slice 1) | C: the one rule |
|---|---|---|---|
| What | `RELAY_WRITES` by mode, frame 320's retry on the relay, `_guess_seed` | `owed_rewrites` for the guess and batch lines, discharged by any write after the ruling | `owed(conn, ref)`: a row of X's owner rests on V. Stamp on every owner write. Keys `(ref, verdict)`. Per-item park |
| Files | `db.py`, `runner.py`, `annotate.md` | B's of revision 1 | Slice 1 brief above, then one stamp per kind |
| Size | about 60 + 80 lines | about 120 + 150 | slice 1 about 220 + 240. Each later kind about 20 lines and its readers |
| Recorded cases that change | m27, only if the second relay writes | m27 wrongly read as discharged by s150's copy (observed, review: `RC/p1_fact.out`) | m27 only. The 4 rewritten guess contests and the touch contests stay (observed, review: section 1.2) |
| Loop risk | Low, `REPLY_SESSIONS` 2 | Bounded, but a second contest inherits spent attempts | Bounded per ruling |
| He reads after two failures | One line, and the batch can still start | Two quarantine lines and a silent hold | The quarantine line and the park page with the way out |
| Closes | Not the gap of a relay never sent | Not a copy after the ruling | The class of a contest on an owner's record |

Rejected: a mechanical guess from his file names. It crosses "Remove the mechanical guess, the architect owns the guess" (ruled: Roman, 2026-10-18 about 12:05; observed: `frame298-design.md` 12 to 14).

Design C does not mend all of cause 8 of the wall guide, "A prose answer is called answered". That class lives in `session_commit`, and frame 267 and frame 320 hold other cases of it (observed, review: section 7). Design C mends every contest of his on an owner's record with one rule.

## 6. The slices

1. **Slice 1, the code line.** The build brief in the result.
2. **Slice 2, the criterion and the test row.** Count the reach first (reasoned: rule C76). Then `criteria.respecify` stages the ruling ref, `tests_missing` calls `owed`, and a criterion contest outside a park page gets a route to `criterion_repair` (observed: the comment at `runner.py` 386 to 399, "Only a park page's ruling").
3. **Slice 3, the pages he reads.** `code_target` and `code_line` show an owed line. The park page names the kind. The night report counts owed lines.
4. **Slice 4, the term, the constraint, the statement and the approves.** Count the reach first. `_bound_rows` calls `owed` for a contested constraint. Each owner gets a write that carries the ruling, or the page offers no rewrite.

## 7. The measurement

### 7.1 The acceptance of slice 1: three checks with no model

- **Check A.** Run `owed` on the run databases at `immutable=1` (night 166 copy at `mode=ro`), at each recorded write and batch start (method: `RC/p1_fact.py`). On recorded rows no `batch_touch` row carries a stamp, so the check counts a write as stamped when its session was woken by the relay of V, which is what slice 1 stamps (reasoned). Expected: m27 owed from s143, still owed at s150, s152, s155 and s156, and replaced by r_m39 at s165, which s171 discharges. Nothing owed after s199 (dry 5 m37), s113, s153 and s182 (night 166). Nothing owed on dry 4 `r_m50_2` and dry 6b `r_m40_2`, which have no verdict (observed, review: section 1.1).
- **Check B.** In-memory copy of `w7`, `b_1` set `pending`, `developer|tick:batch_start|b_1` removed. Today `next_batch` gives `['b_1']` (observed, review: `RC/p6_w7.py`). Slice 1 must give `[]`. Revision 1's check on `w7` as it stands gave `[]` today, because frame 87 already parks `b_1` there (observed, review).
- **Check C.** The unit tests of the brief, step 10. `tick:guess` is read in 10 test files and `next_batch` in 9, so some tests change (observed, review: `grep`).

### 7.2 One live arm, as evidence of capability

The live arm answers what the checks cannot: whether a `tick:guess` wake with his words writes his files. Corrected facts (observed, review: section 6):

- The turn uses three models by role: `gemma4:12b-it-qat` for the Liaison, `qwen3:8b` for the Architect and `qwen3.5:9b` for the Developer (`sessions.pins_json` of s143, s145, s152).
- The driver `dry6b_turn.sh` names `OLLAMA_HOST=http://127.0.0.1:11436`. Revision 1 said port 11434 and one model, which was wrong.
- `night_cassette.wrap` returns the backend unchanged for any phase but `onboarding`, and only `probes/walk.py` calls it. `rota.cli run dry6b --all` never reaches it. So the replay needs a backend hook in the run path, or a driver that builds the loop itself.
- The seed's cut is onboarding only. A session range for s143 to s156 is a few lines.
- A forced arm cannot be a cassette, because the tick wakes have new prompts. It needs a backend that answers by mode. The checks of 7.1 cover the forced case, so it is not run.

The arm: the database before turn 6, `scratchpad/dry6b/runs/w6/` of session 1b9e813c, copied with the SQLite backup API. Sign m26 with the m27 words, at the slice 1 commit, with s143 to s145 replayed from their recordings and the rest live. Count each `tick:batch_start` on `b_1` and whether its `[batches.expect]` line names `string.py` and `test_icalendar.py`. Today: 0 of 3. About 100 lines of probe code and about one turn, 533 s of wall time on the recorded turn (observed, review).

### 7.3 The register

- Add: the guess relay on s145's prompt, expected `batches.guess` with `string.py`. Red today, 0 of 1 recorded.
- Add: `tick: guess` with refs `(item, verdict)` and `principal_said`. Expected: one `batches.guess` with his paths.
- Add: `tick: annotate` after a stamped rewrite, from s150's prompt with the new seed. Expected: `batches.annotate` with `string.py` and no `property.py`.
- Re-record if `annotate.md` changes the brief hash: `L1-AR-annotate-a-batch`, `L1-AR-annotate-from-the-guess`, `L1-AR-re-annotate-from-the-principals-correction` (observed: `tests/rota/cases/l1_architect.yaml` lines 8, 46, 469).

## 8. What is unproven

- Why s145 sent reads and not the call, when s199 sent the call on the same words (observed: the read, section 9). The guess brief's end line "guessed <item>." may invite the miss. Not measured.
- That a `tick:guess` wake with his words writes his files. Only the live arm measures it.
- That the park page marks the quarantined key reported, so that the worst case is 5 sessions and not 6.
- The sizes are estimates.

## 9. Usage

Revision 1: one Opus designer and one reader agent. Revision 2: the same designer, from the review and four reads of the code and the records. No model call, no suite, no run database written. The repository changed by this page only.

## Revision

Revision 2 answers the eight findings of the review.

1. Finding 1, the batch half discharged by any write: taken. `batch_touch.ruling_id`, the stamp on every write under an owed ruling, and discharge on a stamped write only. The equal-set door reads the fact (slice 1, steps 2, 5 and 6).
2. Finding 2, a tick rewrite keeps the contested rows: taken. `batches_annotate` clears under `owed_ruling`, by relay or by tick (step 5).
3. Finding 3, `touch_note` and `batches_judge_touch`: taken. `touch_note` reads the fact, and the judge writes `ruling_id` '' so its rows discharge nothing (steps 5 and 7, section 3).
4. Finding 4, the worst case and the exit: taken. Keys `(item, verdict)`, `annotate` held while the guess line is owed, a per-item park with the page, and one owed write on the newer ruling. The walk gives 4 Architect sessions and at most 2 Liaison sessions (section 2).
5. Finding 5, the question to Roman: taken after a read of R7, R10, P4 and frame 87 (section 4). The park is per item, and the rest does not wait, so I see no departure.
6. Finding 6, check 2 tests nothing: taken. Check B runs on `w7` with `b_1` pending and its start key removed. Today `['b_1']`, must be `[]` (section 7.1).
7. Finding 7, the replay facts: taken. Three models and port 11436. `wrap` is not reached by `rota.cli run`. The forced arm is dropped for the checks. Acceptance is on the three checks, and one live arm is evidence (section 7).
8. Finding 8, one rule and not a row per kind: taken, as the core. `owed(conn, ref)`, a row of X's owner rests on V, per kind in section 1. A twelfth kind needs only its owner's write to carry the ruling.
