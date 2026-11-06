# Frame 362, the design review of "a record that he contested and nobody rewrote", 2026-11-06

The design is `plans/design-contested-record-2026-11-06.md` (below: the design). The measured fault is `plans/f362-contested-guess-read-2026-11-06.md` (below: the read). The brief is `scratchpad/f362_contested_record_design_review_brief.md`. The probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rc362/` (below: `RC`). Every run database opened with `immutable=1`, or `mode=ro` for the night 166 copy. One probe copied `dry6b/w7/dry6b.db` into memory and called `scheduler.next_batch` and `scheduler.parked` there. No model call, no suite. Line numbers are at the checkout as read, `2ee155e3`. Finished 10:34 (observed: `date`).

## Result

**Verdict: revise, then build.** The direction is right: a contest is an owed write, the fact is derived from his ruling, and the gate is per item. The guess half of the fact gives the right answer on all 5 recorded guess contests. The batch half does not. Two changes to the fact and the annotate write are needed before slice 1 closes m27. The open question to Roman is settled by the records, so do not ask it.

| # | Finding | Kind | Severity | Fix |
|---|---|---|---|---|
| 1 | The batch half of the fact is discharged by any `batch_touch` write after the ruling. On the recorded rows, m27's fact reads false from s150, which copied the contested set 6 of 6, so s152, s155 and s156 are still offered | CONFIRMED (probe `RC/p1_fact.py`) | High | Add `ruling_id` to `batch_touch`, as `touch_guesses` has. Stamp it on every write that rests on an owed ruling. Discharge on a stamped write only. The equal-set door reads the fact, not `_principal_relay` |
| 2 | A `tick:annotate` rewrite under an owed ruling keeps the contested rows. `batches_annotate` clears the set only on a relay | CONFIRMED (`api.py` 9119 to 9127) | High | Clear the set when the wake rests on an owed ruling, relay or tick |
| 3 | Section 3 lacks `predicates.touch_note` (a reader) and `batches_judge_touch` (a second writer of `batch_touch`). Section 4.3's touch-note claim has no mechanism in slice 1 | CONFIRMED (map tool, `predicates.py` 1079, `api.py` 28310; dry 5 s220) | Medium | `touch_note` reads the fact. Finding 1's stamp makes the judge's foreseen row harmless |
| 4 | The worst case is 9 sessions and two stuck lines, not 4 and one. The exhausted end is not frame 87's park: no page, no way out, and a second contest after the quarantine gets one relay and then a silent hold | CONFIRMED by code, not run (`scheduler.parked` 2779, `principal.py` 4051 to 4062, `quarantined_keys`) | Medium | Key the owed wake on the item and the verdict. Hold `annotate` while the guess key is live. Give the held item the park page with the way out |
| 5 | The exhausted end does not depart from R7. R7 of 2026-09-02 expects a per-item block that parks. P4's "nothing waits on the principal's reaction" applies R7 to the scope disclosure | CONFIRMED (text: `plans/archive/responsibility-audit.md` 332 to 335, 348 to 349; P4 lines 5 to 9) | Medium, changes what he is asked | Drop the open question. Cite R7, R10 and frame 87 in the design |
| 6 | Check 2 of section 7.1 tests nothing new. On `w7`, `b_1` is already parked by frame 87, so `next_batch` gives `[]` today, and it stays parked after the s171 insert | CONFIRMED (probe `RC/p6_w7.py`) | Medium | Run check 2 on the pre-s152 shape: `b_1` pending, its start key removed. Today that shape gives `['b_1']` |
| 7 | The replay plan names one model and the wrong port, and `wrap` never reaches `rota.cli run`. The three checks with no model are enough to accept the mechanism once findings 1 and 6 are fixed | CONFIRMED (`sessions.pins_json`, `dry6b_turn.sh`, `grep`) | Medium | Accept slice 1 on the corrected checks. Run the live arm once as evidence of capability, with the three role models |
| 8 | Design C mends 6 cases of the contest path, not cause 8. The code already holds a general form: the owner is the relay split's lookup, and "rests on the ruling" is a `refs` row of kind `ruling` or a `ruling_id` column | CONFIRMED (`sandbox.py` 953 to 975 and 4960 to 4973, `api.py` 2775 to 2809, `schema.sql` 96 to 106) | Low | Write `owed_rewrites` as one rule: a landed contest on ref X with verdict V is owed until a row of the owner of X rests on V |

The constraint cell of section 1 is also wrong: `bound_constraints` pushes a contested constraint (section 2 below). That changes slice 4 only.

## 1. The fact, run by hand on the recorded rows

### 1.1 The join

The schema gives the join (observed: `RC/schema.py` on dry 6b):

- `rulings` holds `per_item`, `verdict_id` and `status`. It holds no time. The landing session comes from `receipts` with `table_name = 'rulings'`, and its `sessions.seq` orders it.
- `touch_guesses.ruling_id` holds the verdict message id, not the ruling id. `batches_guess` writes `cause_id` of the trigger relay (observed: `api.py` 9074 to 9081). So the join is `rulings.verdict_id = touch_guesses.ruling_id`. On all 4 rewritten guess contests the set's `ruling_id` equals the verdict: dry 5 `m38`, night 166 `m29`, `m54`, `m70` (observed).
- "Routed to the Architect" needs no relay. The relay split is a lookup on the key: `guess:<item>` goes to `architect:guesses`, a batch id to `architect:batches` (observed: `sandbox.py` 4960 to 4973). A ruling with no verdict is not routed. Dry 4 `r_m50_2` and dry 6b `r_m40_2` are `revise` with `verdict_id` null and no `landed` row in `ruled_refs` (observed). So `verdict_id IS NOT NULL` excludes them. Night 166 has no `ruled_refs` table, so the fact must not need that table (observed).
- `batch_touch` has no ruling column and no time (observed: `schema.sql` 390). "Written after the ruling" exists only as `receipts` rows of `batch_touch` and their session's `seq`. The design does not name this.

### 1.2 The answers

`RC/p1_fact.py` runs the fact of design B.1 at each write and each batch start (output: `RC/p1_fact.out`).

| Run | Ruling | Owed from | Discharged by | Answer | Right? |
|---|---|---|---|---|---|
| dry 6b | r_m27, `guess:` contest | s143 | s150, `tick:annotate`, 6 `batch_touch` rows | false at s152, s155, s156 | **Wrong.** s150 copied the contested set, 6 of 6 grains equal (observed: `RC/p1_eq.py`) |
| dry 6b | r_m39, r_m41, `b_1` contest | s165, s167 | s171 relay write | false at s173 | Right |
| dry 5 | r_m37, `guess:` contest | s197 | s199, set `m38` | false at s207 | Right |
| night 166 | m28, m53, m69, `guess:` contests | s111, s151, s180 | s113, s153, s182 | false at s131, s164, s195 | Right |
| dry 4 / dry 6b | r_m50_2, r_m40_2, `revise` | never | not applicable | false | Right |
| dry 4, dry 5 | r_m58, r_m73, batch contests | s203, s262 | s205, s265 | false at s206 | Right |

So the fact gives an owed write on m27 before s150, and none on the 4 rewritten guess contests after their write. The one wrong answer is m27 from s150 to s165. The design's own check 7.1.1 expects "true for m27 from s145's commit to s171's write". The fact as B.1 states it gives the opposite (observed). Under the design s150 gets a different seed, and the equal-set door could refuse the verbatim copy. But B.6 says the door works "under a contest", and today the only test of that is `_principal_relay`, which is None on a tick wake (observed: `api.py` 2725 to 2747). A near copy, for example 5 of 6 grains, passes any equal-set door.

**Fix.** Stamp `batch_touch` with the ruling, as `touch_guesses` is stamped. Let `batches.annotate` write the stamp when the wake rests on an owed ruling, by relay or by tick. Discharge the batch half on a stamped set only. Then check 7.1.1 reads true for m27 from s143 to s171 on the recorded rows, because s150's rows carry no stamp (reasoned).

## 2. The cells marked "RA: unverified", and the readers the table lacks

### 2.1 The cells

- **Glossary term, reader.** `glossary_terms` has no status column (observed: `schema.sql` 210 to 218). "Stays `observed`" is the provenance view, `PROVENANCE_VIEW_OF_TABLE`, which `_adopt_rows` reads (observed: `api.py` 2775 to 2809). The cell is right in substance and wrong in form.
- **Constraint, reader.** The design says that whether `bound_constraints` reads a contest "is not read". It does not read one. `_bound_rows` drops only the falsified stated commitments (observed: `api.py` 4776 to 4803). So a contested constraint is still pushed to the Developer. The constraint kind seeds work from the contested record, like the guess, the batch line and the criterion. The paragraph "The kinds differ in what is lost" puts it in the other group. This changes the order of slice 4, not slice 1.
- **Statement, reader.** `statements.status` has no contested state (observed: `schema.sql` 40 to 42). `push_working_set` reads statements (observed: map, `runner.py` 4734). A contested statement that nobody rewrote is pushed as it stands (reasoned, not traced). Slice 4 only.

### 2.2 Readers and writers that section 3 lacks

The map tool and a `grep` give these (observed):

- `predicates.touch_note` (`predicates.py` 1079) reads `batch_touch` and sends the touch note page. Section 4.3 says "a touch note can go out only for a touch set that rests on his ruling or that he has not contested". Slice 1 changes no line of `touch_note`. With finding 1's stamp, `touch_note` must leave out a batch whose code line is owed.
- `batches_judge_touch` (`api.py` 28310) is a second writer of `batch_touch`. It writes a foreseen stray on a running batch. Dry 5's s220, `tick:touch_strayed`, wrote 4 such rows (observed: receipts). Under the fact as written, a foreseen row after a batch-line contest discharges the owed write. The stamp removes this.
- `db.batch_reads` and `lift_moved_reads` (`db.py` 1259 to 1277) read `batch_touch` to lift a running batch's quarantined keys. No change is needed. Name it in the table.
- `cockpit/inspect_api.py` 33 shows the rows. No change.

### 2.3 The annotate write under a tick wake

`batches_annotate` clears the set only when `_principal_relay(ctx)` is not None and the relay contests or revises the batch (observed: `api.py` 9119 to 9127). B.2 makes `annotate` fire on a batch "whose touch rows predate an owed ruling". That wake is a tick, so no clear runs. The write is an upsert by `(batch_id, grain)`, and the contested paths stay beside the new ones. The code comment names this fault: "an upsert would keep the disputed path beside the new one" (night 136's m85). **Fix:** clear under the owed fact, not under the relay.

## 3. The loop, worst case

The case: every seat ends with prose, and no write lands.

| # | Session | Bound by | Model time at the recorded rate |
|---|---|---|---|
| 1 | The relay, mode `guess`, as s145 | the message, answered at the commit | 20.8 s, 3 turns (observed: s145 `turns.ms`) |
| 2 to 4 | `architect|tick:guess|<item>`, 3 dispatches | `tick_attempt_cap` 3, `attempts >= cap` (observed: `scheduler.py` 3021 to 3060) | about 62 s at s145's rate |
| 5 to 7 | `architect|tick:annotate|b_1`, 3 dispatches, once grouping forms the batch | the same cap. Grouping does not wait on the guess | about 11 s at s150's rate |
| 8, 9 | `liaison|tick:quarantined`, once per newly quarantined key | `quarantined_keys(unreported=True)` | about 3 s at s163's rate |

So the worst case is 7 Architect sessions and 2 Liaison sessions, about 97 s of model time at the recorded rates. A session is bounded by `ROTA_MAX_ITERATIONS=24`, not by s145's rate. s160 spent 134 s in 7 turns (observed). The design counts 4 sessions, 80 s and one stuck line. It leaves out the annotate seat's own 3 retries and the second report.

**The rows that end it.** `tick_attempts` rows `architect|tick:guess|<item>` and `architect|tick:annotate|b_1`, each with `attempts` 3 and `quarantined` 1. No row ends the hold of the batch. The derived fact stays true until a stamped write.

**What he reads, and when.** No touch note, because no touch set exists. Two Liaison lines, of the form "guess for <item> (architect), 3 attempts" and then "annotate for b_1 (architect), 3 attempts", from the `quarantined` detail (observed: `predicates.py` 1985 to 2005). The first comes after about 85 s of model time, and the second after the annotate retries. The design's line "The team could not rewrite the guess you corrected" does not exist in slice 1. Slice 3 owns it.

**A second contest while the first is owed.** One owed write, because the fact reads the newest routed ruling and stores nothing. But three things go wrong (reasoned from the code, not run):

1. The tick key has no ruling in it, so the second ruling inherits the first ruling's spent attempts.
2. After the quarantine, his second contest lifts nothing. `land` lifts the seats of a running batch only (observed: `principal.py` 4051 to 4062). `lift_keys` lifts a step line only (observed: `principal.py` 3670 to 3682). The second relay session runs, writes nothing, and the hold goes silent, because the key is already reported. That breaks "Nothing stops quietly" (composition, Records).
3. A relay write of the first ruling that lands after the second carries the first verdict, so the fact stays true for one more wake. This is bounded and minor.

**Fix.** Key the owed wake as `tick:guess` with the refs `(item, verdict)`, so each ruling has its own bound and its own report. Let `annotate` wait while the guess key is live, so one owner retries at a time.

## 4. The waits

### 4.1 The three texts, quoted

- R7, through P4 (ruled R16/R17, 2026-09-03; observed: `plans/archive/p4-scope-disclosure.md` 5 to 9): "Non-blocking by R7: nothing waits on the principal's reaction; the steering loop (cancel/preempt, already pinned) is the lever if the scope smells wrong. A blocking variant, if ever wanted, is a config setting in the `merge_gate` mould".
- R7 itself (2026-09-02; observed: `plans/archive/responsibility-audit.md` 332 to 335): "Varies, and blockages are expected: whatever is not blocked keeps going, whatever is blocked parks, and work can be discarded if required. The system may never depend on response latency; blockage is per-item, never global." R10 (348 to 349): "Park it as a blockage. Consistent with R7: the item blocks and waits, everything unblocked keeps going."
- The composition, Flows (observed: `plans/composition.md` 73): "A prediction never blocks. Only a fact or a ruling gates."
- Frame 87 (ruled: Roman, 2026-09-27; observed: `plans/stack.md` 3621 to 3629): "a given-up batch put back in the chair waits for the principal ... the batch stays parked, the page says so with the way out, the principal says what to change or gives up on it, and the siblings start meanwhile."

### 4.2 What waits on what

| State | What waits | On what | Kind |
|---|---|---|---|
| No contest | Nothing new. The touch note stays non-blocking | Nothing | Not applicable |
| Contest landed, write owed, retries live | The start of the item's batches | The owner's stamped write under his ruling | A ruling and a missing fact of the team. His reaction exists already |
| Stamped write exists | Nothing | Nothing | The fact is false |
| Retries spent, keys quarantined | The start of the item's batches. Sibling items go on | His next act on the held item | A per-item block that parks |

### 4.3 Whether the exhausted end departs from R7

It does not, in my reading. R7's own text expects blockage, parks the blocked item, and forbids only a global block or a dependence on response latency. R10 says "the item blocks and waits". P4's sentence is R7 applied to the scope disclosure: the batch does not wait on his answer to the touch note. In the exhausted state the batch does not wait on a disclosure. It waits because the team failed a write he ordered. That is the park of R7 and R10, and frame 87 rules the same shape for a batch the team gave up on. So the question is settled, and Roman refuses a settled question asked again (CLAUDE.md, "What he refuses").

The design is wrong on one mechanical point. Section 4.4 says that "frame 87 already covers it" and that "the build follows frame 87". It does not. `parked` is true for a deferred batch with a given-up key (observed: `scheduler.py` 2779 to 2795). Under the design the batch is pending and its own keys are clean, so `park_ask` never fires, and no page carries the way out. The build must add that exit (finding 4).

**A design with no wait on him.** One exists: in the exhausted state, start the batch with an empty touch set and his words as the only scope. No contested record reaches the Developer. No case measures it. The read shows that the record moves the seat and the words alone do not: 0 of 20 with the old set (observed: the read, 7.2). An empty set also drops the bound block. R7 does not ask for it, so park the item.

## 5. Slice 1 alone

**Does it close m27 end to end?** Not as written. It closes two of the three recorded paths: no write at all, and a verbatim copy if the door reads the fact. It does not close a write after his ruling that ignores his words, which finding 1 shows the fact accepts. With findings 1 and 2, slice 1 closes m27 in every arm: a stamped set written under his words, or a held item with a page (reasoned).

**What it leaves open.**

- A batch-line contest on a running batch. `next_batch` gates a start and a resume, not a running batch. Today `land` lifts the running batch's seats, and the Developer reads the new set only after a write. Record it, and do not build it in slice 1.
- The `touch_note` gate (finding 3).
- The exit of the held item (finding 4).
- Whether a tick wake with his words and no path writes his files. The design marks this unproven (section 8). Only a live arm measures it.

**Size.** About 120 lines of code is low. Findings 1 to 4 add a `batch_touch.ruling_id` column with its migration and identity row (`identity.py` 84 names the table), the stamp in `batches_annotate` and `batches_guess` on a tick wake, the clear under the fact, the `touch_note` filter, the ruling in the tick key, and the park page for the held item. A fair estimate is about 200 lines of code and 220 lines of tests (reasoned).

**Recorded cases to change.** The design states them right. The probe shows no recorded start that changes but m27's (section 1.2). The register cases of section 7.3 stand. Unit tests read `tick:guess` in 10 test files and `next_batch` in 9 (observed: `grep`), so some unit tests change with the predicate.

**What slice 1 makes harder for slices 2 to 4.** Three choices:

1. "Written after the ruling" by `receipts` order is a second rule beside `ruling_id`. Slice 2's criterion and slice 4's adopts would each need their own order rule. One stamp rule, finding 8, serves all four slices.
2. A tick key without the verdict gives every later kind the silent second contest of section 3.
3. `owed_rewrites` placed in `scheduler.py` with a hand row per kind invites a fifth list beside `OWED_A_REPLY`, `RULED_TABLES`, the relay split and `RECEIPT_RULES`.

## 6. The measurement

**What exists.** `RecordingBackend` replays a hit and calls the server on a miss, and `key_for` keys the model, the options and the whole prompt (observed: `probes/night_cassette.py`). `probes/seed_night_cassettes.py` seeds from `turns` and `pins_json`, cut at the first sentence's session (observed: its docstring).

**What is missing, and what the design misstates.**

1. The seed's cut is onboarding only. A session range for s143 to s156 is a few lines.
2. `wrap` returns the backend unchanged for any phase but `onboarding`. Only `probes/walk.py` calls it (observed: `grep`). The turn driver runs `rota.cli run dry6b --all` (observed: `dry6b_turn.sh`), which never reaches `wrap`. So the replay needs a backend hook in the run path, or a driver that builds the loop itself.
3. The forced arm cannot be a cassette. The tick wakes have new prompts, so their keys miss. It needs a backend that answers by mode with s145's completions.
4. The turn uses three models by role: `gemma4:12b-it-qat` for the Liaison, `qwen3:8b` for the Architect and `qwen3.5:9b` for the Developer (observed: `sessions.pins_json` of s143, s145, s152). The driver names `OLLAMA_HOST=http://127.0.0.1:11436`. The design names `qwen3:8b` alone and port 11434.

**Cost.** About 100 lines of probe code in the scratch folder. Each arm is about one turn: 533 s of wall time and 288 s of model time on the recorded turn 6 (observed: the read, section 1), plus model swaps on the 3080.

**Are the three checks with no model enough?** Yes, for the mechanism, once two checks are corrected:

- Check 1 holds only with finding 1's stamp (section 1.2).
- Check 2 as written passes and fails for the wrong reason. On `w7`, `b_1` is deferred with `developer|tick:batch_start|b_1` quarantined, so `parked` is true and `next_batch` gives `[]` today. After the s171 insert, `b_1` stays parked, because a touch write lifts only a running batch's keys (observed: `RC/p6_w7.py`; `db.py` 1241 to 1256). With `b_1` set pending and its start key removed in memory, `next_batch` gives `['b_1']` today (observed). Run check 2 on that shape.
- Check 3, the unit tests, covers the stamp, the clear, the gate, the key and the exit.

The live arm is the only measure of capability: whether a tick wake with his words writes his files. Run it once after the build as evidence, not as the acceptance gate (reasoned: "Progress is rota's capability", CLAUDE.md).

## 7. Over-fit

Cause 8 of the wall guide is "A prose answer is called answered". The class lives in `session_commit`: a woken session answers every message outside `OWED_A_REPLY` (observed: the read, section 1, row 5). Design C mends six cases of one path, a contest of his on an owner's record. It does not mend the class. Frame 320's request and frame 267's page reply are other cases of the class with their own mechanism.

Design C's form is a hand row per kind. A seventh kind would need a new row, a new predicate branch, a new reader gate and its own discharge rule. The code already holds the two parts of a general rule:

- **The owner.** The relay split is a lookup by the single-writer law: `RULED_TABLES`, `_owner_of_ref`, the `GUESS_RELAY` and `BATCH_RELAY` keys (observed: `sandbox.py` 953 to 975 and 4960 to 4973).
- **"Rests on the ruling".** `_adopt_rows` writes a `refs` row of kind `ruling` (observed: `api.py` 2809). `refs` covers items, terms, constraints, model areas, criteria and business rules (observed: `schema.sql` 96 to 106). `touch_guesses` has `ruling_id`. `batch_touch` has neither, which is finding 1.

So the general rule is: a landed contest or revise on ref X with verdict V is owed until a row of the owner of X rests on V. Then a seventh kind costs one thing: its owner's write records the ruling it rests on. The readers stay per kind, because what a reader must do with a stale record differs. One function `owed(conn, ref)` that each reader calls keeps that to one call per reader.

## 8. Usage

One Opus reviewer. Probes in `RC`: `schema.py`, `p1_rows.py`, `p1_fact.py` with `p1_fact.out`, `p1_eq.py`, `p3_ms.py`, `p6_pins.py`, `p6_w7.py`. No model call, no suite, no run database written. The repository changed by this page only.
