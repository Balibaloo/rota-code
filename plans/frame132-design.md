# Frames 132 and 145: the same-refs door on a challenge to the Tester, pass 0

Meta workflow. Pass 0 of frame 132, a Tester answers a challenge in prose and sends no test, and frame 145, a challenge of a test's new version is refused as answered. The implementing agent on Opus wrote this record on 2026-10-05. It writes no code. The read started at 10a50ed. Frame 144's pass 1 landed at c888968 during the read, so every line below is cited at ed43c08 unless it says otherwise. `db.py`, `runner.py` and `predicates.py` did not move between the two commits (observed: `git diff 10a50ed HEAD --stat`, 2026-10-05).

## Summary

1. The door, `rota/core/sandbox.py:1310-1417`, refuses a Developer's challenge when any earlier challenge on the same sorted refs is closed, or has an answer row from any role. It never reads who answered or whether the test changed (observed: the code at ed43c08, 2026-10-05).
2. A challenge that the Tester never answers still reads as answered. A barren Tester session sets it `unresolved` (`db.py:765`). The Architect's `tick:unresolved` answer then carries the challenge as its `cause_id` (`runner.py:4061`), and the thread sweep sets it `answered` (`db.py:717`) (observed: the code and nights 119, 121 and 123, 2026-10-05).
3. Count, nights 113 to 123, all 11 databases open: 141 challenge refusals of the answered form. 16 had no answer row (a1). 43 had only the Architect's answer row (a2). 66 came after the test moved (b). 16 are true repeats (c) (observed: `refusals.py`, `classify.py`, 2026-10-05).
4. 43 Tester challenge sessions: 21 moved the test, 10 answered, 3 stored another test, 1 sent a question, 4 had every encode refused, 4 made no call. After each of the 8 barren sessions, 0 later challenges on that test reached the Tester (observed: `outcomes.py`, `second.py`, 2026-10-05).
5. The predicate: the newest prior on the same refs decides. A receipt on a row of its refs since the prior woke the Tester admits. The Tester's answer row with no such receipt refuses. Neither admits one re-send per version.
6. Replay on each night's state: 125 of 141 refusals turn to admitted, and 16 true repeats stay refused. No wiring changes. No schema changes.
7. Stale: one case, `L1-DV-act-on-an-answered-challenge`, if the repeat's text changes. 252 of its 258 runs at the current hash meet the sentence (observed: `cassette_grep.py`, 2026-10-05).
8. Price: pass 1 about 60k and one review about 80k. With a second loop, about 100k in passes and 150k in reviews.

## 1. The read of the code

### 1.1 The same-refs door

- Site: `_bind_send.stage` in `rota/core/sandbox.py:1310-1417` at ed43c08. It runs for the verbs `challenge` and `escalate`, after `_challenge_evidence` (`:1301`) and before the in-session duplicate guard (`:1884`) (observed: the code, 2026-10-05).
- What it compares: rows of `messages` with `from_role = ctx.role`, `to_role = recipient` and `verb = verb`, newest first by `seq`, whose `body_refs` equals the call's refs as a sorted list (`:1327-1339`). It does not compare the batch or the round (observed: the query, 2026-10-05).
- What "answered" means for it: a row whose newest message with `cause_id = m.id` and `verb = 'answer'` exists, from any role (`:1330-1332`). For the Developer, a row whose status is not `open` counts too (`:1340`). The loop takes the newest row that meets either, and it stops there (`:1341-1343`) (observed: the code, 2026-10-05).
- An open row is `waiting` only when no older closed row exists, because the loop breaks on the first closed row and the answered branch raises first (reasoned: `:1341-1345` and the order of the branches).
- The challenge sentence, recipient `tester` (`:1390-1400`): `you sent challenge to tester on exactly these refs already (m64) and they answered. Sending it again is the same argument again. Do not send this challenge again. Send msg.escalate_architect on the same refs, or make one real change to the code the test calls.`
- The escalate sentence with no new row (`:1375-1382`): `you sent escalate to architect on exactly these refs already (m65) and they answered (answered) with no row beyond your own refs. Sending it again is the same argument again. The attempt cap carries this batch to the ladder: make one real change to the code the test calls, or end the session with no call`. The value in brackets is the answer's id, or the prior's status when no answer row exists (`:1374`).
- The escalate sentence with new rows (`:1366-1372`) names the rows the answer added. The waiting sentence (`:1406-1417`) is the Developer's only: `... and it waits for an answer. A second copy is the same question twice ...`.
- No sentence of this door records an offer. Frame 144 left "the repeat doors of `_bind_send`" out (copied: `plans/frame144-pass1.md`, the sites).

### 1.2 How a challenge closes

Every path that sets `messages.status` on a challenge (observed: `python -m rota.tools.map table messages --column status` and the code, 2026-10-05):

- `db.py:759-782`, the session that the challenge woke commits. If the session wrote nothing and sent nothing, and the challenge is `open`, the status goes to `unresolved` with the note `the session woken by it wrote nothing and sent nothing` (`:765-777`, night 33's rule). Otherwise it goes to `answered` (`:778-782`).
- `db.py:717-722`, the thread sweep. When a role sends a message in the thread, every `unresolved` message of another role in that thread goes to `answered`.
- `boot.quarantine_exhausted` (`boot.py:186-190`) sets an `open` message past `message_attempt_cap` 3 to `quarantined`. `scheduler.quarantine_looping` (`scheduler.py:1669-1671`) does the same past `loop_cap` repeats of one causal edge.
- The other writers act on other verbs: `close_park_asks`, `schedule_reask`, `principal.land`, the compose round (`db.py:788`), the Liaison's send to the principal (`db.py:815`), the parroted question (`db.py:865`) and the report (`db.py:892`).

What `answered` means in the rows: only a status. An answer row is a message with `verb = 'answer'` and `cause_id` equal to the challenge. A Tester's answer gets that `cause_id` because the sandbox stages `cause_id = ctx.trigger` (`sandbox.py:1958`). The Architect's answer on a `tick:unresolved` wake gets it too, because the runner fills `cause_id` from `wake.message_id` (`runner.py:4061`), and that wake's ref is the challenge (`predicates.py:1085`) (observed: the code, 2026-10-05).

What the runner does when the woken session ends with nothing (observed: the code and the rows of nights 119 and 123, 2026-10-05):

1. A session that "named an act and did not perform it" (night 119 s249) or that "was refused the same way in four turns" (night 123 s141) commits with no writes and no messages. `db.py:765` sets the challenge `unresolved` with the note.
2. `predicates.unresolved` (`predicates.py:1003-1105`) wakes the first role of `QUESTION_LADDER = ("architect", "vision_keeper")` that has not spoken in the thread and can answer the asker. For a Developer's challenge that is the Architect, kind `tick:unresolved`, detail the note.
3. The Architect answers the Developer with `cause_id` equal to the challenge. Night 119 m143 and m149, night 121 m69 and m199, and night 123 m67 hold no words (observed: `classify.py`, 2026-10-05). That is frame 115's sign.
4. The sweep sets the challenge `answered`. The note stays. So night 123's m64 reads `answered`, with the note and an answer row m67 that is the Architect's (observed: `probe1.py 123`, 2026-10-05). The night read called m64 "answered with no answer row" (copied: `plans/night123-read.md`, section 3, item 5). The door sees m67 as m64's answer row.

### 1.3 The test's version and the link to a challenge

- `tests.version` starts at 1. `_apply_write` adds 1 on each update of a stored row with `amends` (`db.py:447-448`). `tests_encode` under a stored id with the same path stages an update (`api.py:5709`, `:5783`). A byte-identical body is not a write and moves nothing (`api.py:5644`) (observed: the code, 2026-10-05).
- A moved test loses its runs (`db.py:579-580`), so the harness runs it again at `next_attempt`, one above the batch's highest attempt (`lifecycle.py:274-278`, `predicates.py:723-750`). A moved test also lifts the batch's quarantined keys and clears its counts (`db.py:596-610`) (observed: the code, 2026-10-05).
- `receipts(session_id, table_name, row_id, new_version)` holds one row per session per changed artefact row (`db.py:675-686`). `new_version` is the table's counter, not the row's. On night 123 the count of `tests` receipts on a row equals its `version`: `inh_echo_json_02` has 2 receipts and version 2 (observed: an inline query, 2026-10-05).
- No row links a challenge to the version it challenged. The message holds refs and text only (`schema.sql:626-674`). The link that exists: `sessions.trigger_msg` names the challenge that woke a session, and `receipts` names the rows that session changed. `sessions.seq` orders the commits (observed: the schema, 2026-10-05).
- Each refused challenge quoted the test's current body. `_challenge_evidence` matches the test-side quote against the stored row's code (`sandbox.py:711-850`) and runs before the door (reasoned: the order at `:1301` and `:1310`). So a challenge refused after a move is a challenge of the new version.

### 1.4 The wakes, and what stops a loop

- The Tester's challenge wake: mode `challenge` (`tester/challenge.md`, tools `criteria.load`, `tests.consult`, `code.source`, `tests.encode`, `msg.answer_developer`, two questions, `batches.expect`, `msg.answer_critic`). The body holds the failed-run blocks (`runner.py:390-394`) and `The message that woke you:` with the message's rows resolved (`runner.py:395-398`). A test row carries its last run's whole output on this wake (`runner.py:1795-1812`). The wake shows no earlier challenge on the same test (observed: the code, 2026-10-05).
- The `tick:unresolved` wake: the Architect in mode `unresolved` (`architect/unresolved.md`), refs the challenge, detail the note. The brief says to answer whoever asked (observed: the brief, 2026-10-05).
- The Developer's fix wake lists the thread of each red test (`runner.py:2004-2050`). A challenge with no answer row and a closed status reads `closed (<status>) with no answer row`. An answer row with no text reads `answered with no words`, from any role. So night 123's m64 reads `answered with no words` there (reasoned: m67 has `cause_id` m64 and no text).
- A challenge admitted a second time is a new `open` message to the Tester. The Tester wakes on it in mode `challenge`, and the wake shows that message only (reasoned: the same frontier and the same wake builder).
- What stops a loop today: the same-refs door; the duplicate guard, one message per recipient and verb per session (`sandbox.py:1884-1891`); `tick_attempt_cap` 3 wakes per tick key (`config.py:121`), a quarantine that a commit or a moved test lifts; `loop_cap` 10 attempts per batch (`predicates.py:844`), then `exhausted` and the park; `message_attempt_cap` 3 for an open message (`boot.py:186`); `quarantine_looping` past 10 repeats of one causal edge (`scheduler.py:1669`). A Developer's challenge from a tick wake has no cause, so the edge count does not see a challenge loop (copied: the door's comment at `sandbox.py:1311-1315`, S0 walk eight).

## 2. The count

### 2.1 The databases and the scripts

All 11 databases open read-only, `.rota/clickI_night113.db` to `.rota/clickI_night123.db`. Night 115 holds no refusal of either form (observed: `refusals.py`, 2026-10-05). The scripts are in the scratchpad folder `f132` of session c81b16d3:

- `lib.py` opens a night with `mode=ro`.
- `refusals.py` finds each refusal event. A prompt holds the earlier turns, so it reads only the text after the echo of the reply before it. A seat can write `ERROR ...` lines into its own reply (frame 113). Night 122's s145 did so with `(m67)` and `(m68)`, and the script drops those. Output `refusals.tsv`, 200 events.
- `classify.py` classes each refusal by the state of its prior at the time of the refusal, and replays the proposed predicate. Output `classes.tsv`.
- `outcomes.py` gives each Tester challenge session's outcome and each night's batch ends. `batches.py` maps refused groups to batches. `second.py` follows each silent Tester session. `cassette_grep.py` reads the cassette. `probe1.py` to `probe4.py` are reads.

The classes, for a refusal in session S that cites the prior P:

- a1: no answer row names P, and no row of P's refs has a receipt from a session at or after P's first woken session and before S.
- a2: only an answer row of another role names P, the Architect's rung, and nothing moved.
- b: a row of P's refs moved after P, as above.
- c: the recipient's answer row names P, and nothing moved. A true repeat.
- d: other. No challenge refusal is d. The waiting form never appears.

The count of night 123 is 18 refusals in 10 sessions, and the read gives 17 (copied: `plans/night123-read.md`, section 3, item 6). The difference is s149: its turn 3 reply held 21 calls with no `TOOL:` prefix, and the door refused one on m64. Its turn 4 call put the refs in another order and was refused again (observed: `probe2.py 123 s149`, 2026-10-05). Night 122 gives 6, and the read's four refusals on m66 are among them (copied: `plans/night122-read.md`, question 2).

### 2.2 Challenge refusals by night and class

Refusals (sessions), `refusals.py` then `classify.py`:

| Night | a1 | a2 | b | c | d | Total |
|---|---|---|---|---|---|---|
| 113 | 0 | 0 | 4 (2) | 0 | 0 | 4 (2) |
| 114 | 0 | 0 | 15 (10) | 7 (5) | 0 | 22 (15) |
| 116 | 0 | 3 (2) | 0 | 0 | 0 | 3 (2) |
| 117 | 16 (11) | 0 | 13 (3) | 3 (3) | 0 | 32 (13) |
| 118 | 0 | 0 | 0 | 5 (3) | 0 | 5 (3) |
| 119 | 0 | 15 (8) | 10 (5) | 0 | 0 | 25 (9) |
| 120 | 0 | 0 | 2 (2) | 0 | 0 | 2 (2) |
| 121 | 0 | 7 (5) | 16 (6) | 1 (1) | 0 | 24 (9) |
| 122 | 0 | 0 | 6 (4) | 0 | 0 | 6 (4) |
| 123 | 0 | 18 (10) | 0 | 0 | 0 | 18 (10) |
| All | 16 (11) | 43 (25) | 66 (32) | 16 (12) | 0 | 141 |

The priors behind each class (observed: `classify.py`, 2026-10-05):

- a1: night 117's m64 before s163 moved `inh_echo_json_03`, after the Tester s142 stored a new id and left the old test. Night 117's m118, after the Tester s213 stored another test.
- a2: night 116 m90, night 119 m136 and m148, night 121 m65, night 123 m64. Each woke a Tester session that wrote nothing and sent nothing, and each has an empty Architect answer.
- b: for example night 122's m66 (s144 stored version 2), night 119's m137 (s251 replaced `tst_v3`), night 114's m124 (s237 moved the test).
- c: night 114 m64 (answer m65), night 117 m68 (answer m70), night 118 m104 (answer m105), night 121 m131 (answer m133).

### 2.3 By session

Class and prior of each refusal, in order (observed: `classes.tsv`, 2026-10-05):

- 113: s143 b(m64) x3, s148 b(m64).
- 114: s144, s145, s148 c(m64); s149, s153 c(m64) x2; s238 to s251, 10 sessions, b(m124) x15.
- 116: s187 a2(m90) x2, s190 a2(m90).
- 117: s143 a1(m64); s147 a1(m64) x2, b(m66); s152 a1(m64) x3, c(m68); s156 c(m68), a1(m64); s159 a1(m64); s162 b(m66) x3, c(m68); s164 b on m64, m66 and m68, x9; s214, s217, s218, s224 a1(m118); s222, s223 a1(m118) x2.
- 118: s204 c(m104) x3; s207, s220 c(m104).
- 119: s147 b(m64); s250 a2(m136) x3; s252 a2(m136), b(m137) x2; s255 a2(m136) x3, b(m137) x3; s259, s260, s267 a2(m136); s270 a2(m136) x3, b(m137) x3; s272 a2(m148), b(m137), a2(m136).
- 120: s229, s230 b(m122).
- 121: s144 a2(m65) x2, b(m64) x2; s153 a2(m65), b(m66), b(m64); s160 b x4; s163 a2(m65) x2, b x4; s241 c(m131); s305, s306 a2(m198); s323 b(m198); s329 b(m198) x3.
- 122: s145 b(m66), b(m64) x2; s148, s149, s150 b(m66).
- 123: s143 x2, s148, s149 x2, s152 x2, s159 x4, s160, s161, s162 x3, s165, s168, all a2(m64).

### 2.4 Batches given up or parked while the refusals stood

12 batches met a refusal of class a or b. 7 ended given up, `running` with the `tests_failing` key quarantined. 3 ended parked, `deferred`. 2 ended `running` past `loop_cap`. None merged (observed: `batches.py`, 2026-10-05).

| Night | Batch | End | Attempt | Refusals by class |
|---|---|---|---|---|
| 113 | bg_1 | given up | 6 | b 4 |
| 114 | bg_3 | running | 11 | b 15 |
| 116 | bg_2 | given up | 4 | a2 3 |
| 117 | bg_1 | parked | 10 | a1 8, b 13, c 3 |
| 117 | bg_2 | given up | 4 | a1 8 |
| 119 | bg_1 | parked | 11 | b 1 |
| 119 | bg_3 | given up | 5 | a2 15, b 9 |
| 120 | bg_3 | given up | 6 | b 2 |
| 121 | bg_1 | parked | 10 | a2 5, b 12 |
| 121 | bg_3 | running | 12 | a2 2, b 4 |
| 122 | bg_1 | given up | 5 | b 6 |
| 123 | bg_1 | given up | 8 | a2 18 |

Three more batches met only class c: night 114 bg_1 parked, night 118 `confirm_default_on_eof_group` given up, night 121 bg_2 parked. Other walls also stopped these batches, frames 131 and 87 among them, so the table does not say the door alone stopped them (reasoned: the night reads name several causes per batch).

### 2.5 The escalate form, a table only

That door is not in this design. Class c here means the Architect's answer row (observed: `classify.py`, 2026-10-05).

| Night | a1 | a2 | b | c | d | Total |
|---|---|---|---|---|---|---|
| 114 | 12 (6) | 0 | 0 | 0 | 0 | 12 (6) |
| 117 | 11 (7) | 0 | 1 (1) | 3 (2) | 0 | 15 (8) |
| 118 | 0 | 0 | 0 | 0 | 1 (1) | 1 (1) |
| 119 | 2 (2) | 0 | 0 | 1 (1) | 0 | 3 (3) |
| 121 | 7 (4) | 0 | 0 | 4 (3) | 0 | 11 (5) |
| 122 | 7 (3) | 0 | 0 | 0 | 0 | 7 (3) |
| 123 | 9 (5) | 0 | 0 | 0 | 0 | 9 (5) |
| All | 48 (27) | 0 | 1 (1) | 8 (6) | 1 (1) | 58 |

Night 118's d is m97, whose refs name no test. 48 of 58 escalate refusals cite an escalation that the Architect closed with no answer row. That is frame 115's ground, an answer that carries nothing.

### 2.6 Tester challenge sessions

43 Tester sessions woke on a challenge, 41 from the Developer and 2 from the Critic (observed: `outcomes.py`, 2026-10-05):

| Outcome | Sessions |
|---|---|
| Moved the challenged test | 21 |
| Answered, test unchanged | 10 |
| Stored another test, the challenged one unchanged | 3 |
| Sent a question, nothing else (night 116 s144) | 1 |
| Every `tests.encode` refused, nothing sent | 4: night 116 s185, night 121 s143 and s304, night 123 s141 |
| No call, nothing sent | 4: night 119 s249 and s271, night 121 s247 and s331 |

So 21 of 43 challenge sessions move the test, and 8 of 43 write nothing and send nothing. Each of the 8 carries the note `the session woken by it wrote nothing and sent nothing` and reads `answered` at the night's end (observed: an inline query, 2026-10-05). After each of the 8, no later challenge on that test reached the Tester: 0 of 8. The test moved after 1 of 8, night 121's `vopt_cr1`, by the Tester s321 woken by the Terminologist's answer m204 (observed: `second.py`, 2026-10-05).

## 3. The design

### 3.1 The predicate

Scope: the Developer's `msg.challenge_tester`. Every other sender and verb keeps today's branch byte for byte (reasoned: the Critic's challenge and the escalate form have other causes, sections 2.5 and 3.10).

Let P be the newest message with the same `from_role`, `to_role`, `verb` and sorted refs. The rows that decide:

- `woke(P)`: the lowest `sessions.seq` with `trigger_msg = P.id`. None when P never woke a session.
- `moved(P)`: a `receipts` row whose `row_id` is in P's refs, from a session with `seq >= woke(P)`. Any table counts, so a repaired criterion counts as well as a repaired test. False when `woke(P)` is None.
- `judged(P)`: a message with `cause_id = P.id`, `verb = 'answer'` and `from_role = P.to_role`. The Architect's rung answer is not the Tester's judgement.

The door, in order:

1. P is `open`: refuse with today's waiting sentence. Unchanged.
2. `moved(P)`: admit. The challenge is of a new version (frame 145).
3. `judged(P)`: refuse as the same argument. The Tester judged this version.
4. Otherwise P is unanswered. Count the unanswered priors on these refs, newest first: each is closed, not judged and not moved, and the count stops at the first prior that is judged or moved. Below 2: admit (frame 132). At 2: refuse with the bound's sentence.

This is the judging session's first reading with two changes (reasoned):

- "An answer row exists" becomes "the recipient's answer row exists". On nights 119, 121 and 123, every unanswered challenge has an empty answer row from the Architect, so the first reading would still refuse night 123's 18 and night 119's 15 a2 refusals.
- "The test's version moved" becomes "a row of the refs has a receipt since the prior woke a session". No row stores the version that a challenge saw, and the receipt is the smallest record that exists. It needs no new column.

The smallest record, and its limit: the derivation needs no schema change. Its gap: a write to the test after P is sent and before P's first woken session counts as before P (reasoned: the sender's session is not stored on the message). In that gap the Tester wakes on the newer version anyway. A new column `messages.ref_versions` would close the gap and costs a schema change, the commit's insert at `db.py:691` and every fixture of `messages`. Not recommended for this pass.

### 3.2 A challenge whose Tester session ends with nothing

Four options, with what each wakes next:

1. **Admit one re-send per version (recommended).** The door admits the Developer's next challenge on the same refs. The new message wakes the Tester in mode `challenge`. The barren close and the Architect's `tick:unresolved` wake stay as they are. A second unanswered prior on the same version refuses. No wiring change: the Developer-to-Tester edge exists, and a new message uses it.
2. **Keep the challenge open, and wake the Tester again on the same message.** `db.py:765` would leave a barren challenge `open`, so the Tester wakes again until `message_attempt_cap` 3 quarantines it. The Architect no longer wakes on it. **This is a wiring change.** It reverses night 33's rule, which sends a barren challenge to the ladder (copied: the comment at `db.py:766-772`). The Developer meets the waiting sentence meanwhile.
3. **Refuse as today, with a sentence that states the fact.** Nothing wakes. The test does not move. Night 123's 18 refusals become 18 refusals with a truer sentence. The escalation route after a barren close moved the test in 0 of 8 cases (observed: section 2.6).
4. **The runner wakes the Tester again by itself after a barren session.** A new predicate, and a wiring change. More code than option 1 for the same wake.

Option 1 is recommended. It gives a stochastic seat one more wake on the same test, and 21 of 43 Tester challenge sessions move the test (observed: section 2.6). It keeps every edge and every close as they are. The cost of one round is one Tester session, one Architect session on `tick:unresolved`, and the Developer's wake.

What the re-send meets on each night (reasoned):

- Night 119: the Tester wakes on `tst_v1` a second time. s249 and s271 made no call, so a second wake has a fair chance.
- Night 123: the Tester wakes on `inh_echo_json_03` a second time. s141 lost its repair to the constant-assertion door and the literal door, so a second wake likely meets the same doors until frame 147 lands. Then the bound refuses the third challenge.
- Night 122: the challenge of version 2 is admitted, and the Tester wakes on the space that the criterion forbids.

### 3.3 The replay, and the loop bound

On each night's state, the predicate turns 125 of 141 refusals to admitted, and it still refuses 16 (observed: `classify.py`, 2026-10-05):

| Class | Refusals | Admitted | Sessions where one would land | Still refused |
|---|---|---|---|---|
| a1 | 16 | 16 | 11 | 0 |
| a2 | 43 | 43 | 24 | 0 |
| b | 66 | 66 | 22 | 0 |
| c | 16 | 0 | 0 | 16 |

"Would land" counts the sessions where the admitted call is the first challenge of the session. The duplicate guard refuses the rest. No refusal of the 141 had two unanswered priors on its version, so the bound refuses none on the night's state. The night's state is not the state after a landing: a landed re-send becomes the newest prior, and the later refusals of that night depend on what the Tester does with it. So the 57 sessions are an upper bound on the new landings (reasoned).

The loop bound (reasoned from the code, not run):

- A true repeat stays refused, so S0 walk eight's livelock, a held answer on an unchanged test, stays closed.
- On one version of the refs, at most two unanswered challenges reach the Tester. The door enforces it.
- Each move of a test is a new harness run at a new attempt (`db.py:579-580`, `lifecycle.py:274`). `loop_cap` 10 ends the batch's `tests_failing` wakes (`predicates.py:844`), and `exhausted` parks the batch. So a challenge-and-repair loop ends at the attempt cap, law 6 (copied: the comment at `db.py:592-593`).
- A move of a criterion does not add an attempt. Its loop is bounded by the question door, two answers per criterion (from `sandbox.py:1418`), and by the Terminologist's own caps (reasoned, not counted).

### 3.4 The refusal texts

The waiting sentence stays. Each refusal below states one fact and one step. The step names `msg.escalate_architect` only when the escalate same-refs branch admits it: no escalation from this seat on the same sorted refs exists, open or closed. That check is the same function the door uses, refactored into one helper. Each sentence that names the call records it with `api._offer(ctx, said, "msg.escalate_architect", {"refs": list(refs)})`, so frame 144's follow check sends it through every door in the suite (reasoned: `api.py:204-220` and `plans/frame144-pass1.md`). Another door can still refuse the escalation, for example `_escalation_over_removed_grain`. The follow check then fails the test that meets it.

The true repeat, judged and not moved:

- Escalation admitted: `you sent challenge to tester on exactly these refs already (m96) and they answered (m98). Sending it again is the same argument again. Send msg.escalate_architect on the same refs.`
- Escalation refused: `you sent challenge to tester on exactly these refs already (m96) and they answered (m98). Sending it again is the same argument again. Make one real change to the code the test calls.`

The bound, two unanswered priors on one version:

- Escalation admitted: `you sent challenge to tester on exactly these refs already (m64, then m71), and the Tester answered neither and did not change the test. Send msg.escalate_architect on the same refs.`
- Escalation refused: `you sent challenge to tester on exactly these refs already (m64, then m71), and the Tester answered neither and did not change the test. End the session with no call.`

Why "end the session" is the step there: the Developer can write no test, and the ladder already climbed twice on `tick:unresolved`. Ending the session lets the tick cap take the batch to the Liaison (reasoned). Frame 87's wall then holds the seat on nights 122 and 123, and that is frame 87's cause (copied: `plans/night123-read.md`, section 4).

The admitted call returns today's result, `{"id": ..., "to": "tester", "verb": "challenge"}`, with no note. So no recorded prompt moves where a challenge lands (reasoned).

### 3.5 The recorded cases whose prompt holds the sentence

No tool in `rota/tools` greps a recorded prompt (observed: `grep -l cassette rota/tools/*.py`, 2026-10-05). So `cassette_grep.py` reads `tests/rota/cassettes.db` read-only.

- `case_runs` whose transcript holds `exactly these refs already`: one case, `L1-DV-act-on-an-answered-challenge`. On qwen3:8b, 252 of its 258 runs at prompt hash `3697edde4a` hold the challenge sentence, the last at 2026-10-05T12:41:48 (observed: `cassette_grep.py`, 2026-10-05). Its fixture is class c: m1 answered, and the Tester's answer m2 names it (`tests/rota/cases/l1_developer.yaml`, the case before `L1-DV-fix-what-the-verdict-names`).
- The cassette holds 93 qwen3:8b rows under 14 prompt hashes and 4 qwen3.5:9b rows under 2 hashes whose user text holds the challenge sentence. No `case_runs` row names those hashes (observed: the same script). They are not keys that a current case replays (reasoned).
- `tests/rota/cases/l1_answers.yaml:317` and `l1_developer.yaml:456` hold the words in comments only, and a comment is not in a prompt.

So a changed true-repeat sentence makes one case stale: `L1-DV-act-on-an-answered-challenge`. Pass 1 re-records it at 5 runs and reads its tally. The case's `expect` is `any_of` a code write and commit, or one escalation, so the one-step sentence fits it (observed: the case, 2026-10-05). The bound's sentence and the admit change no recorded prompt, because no case holds an unanswered or a moved prior (reasoned: the one case that meets the door is class c). The gate's stale line is the check.

Unit tests at ed43c08 that assert today's behaviour and change in pass 1 (observed: `tests/rota/test_desk_guards.py`, 2026-10-05):

- `test_a_closed_challenge_with_no_answer_row_is_answered` (`:670`) asserts the refusal that this frame removes. It becomes the admit test of option 1.
- `test_a_challenge_that_waits_for_its_answer_is_not_sent_twice` (`:594`), its second half, and `test_a_repeat_challenge_is_told_the_rung_as_a_sentence` (`:685`) assert today's true-repeat text to the byte.

### 3.6 The sandbox tests that pass 1 adds

One per cause, each on the recorded call of its night. The fixtures copy the night's rows for the criterion and the test, because `_challenge_evidence` matches the quotes against them (reasoned: section 1.3).

1. **Night 122, frame 145.** s145 turn 4, `msg.challenge_tester(refs=['echo_json_compact', 'inh_echo_json_01'], quotes=['The callable `echo_json` accepts any Python object and writes its JSON representation to the stream using `json.dumps(obj, separators=(",", ":"))`, followed by a single newline.', 'assert output.getvalue() == "{\\"key\\": \\"value\\"}\\n"'])`. State: m66 `answered` with no answer row, a Tester session with `trigger_msg = 'm66'` and a `tests` receipt on `inh_echo_json_01`, the row at version 2. Admitted.
2. **Night 119, frame 132's first cause.** s250 turn 1, the first call, `msg.challenge_tester(refs=["c1_version_option_show_python", "tst_v1"], quotes=['"When `version_option` is invoked, if `show_python` is true, the output message must include the running Python version string."', 'assert hasattr(dummy_cmd.params[0], "name")'], round_no=0)`. State: m136 `unresolved` with the note, s249 with no receipt and no message. Admitted. The same test then adds the Architect's empty answer with `cause_id` m136 and status `answered`. Still admitted.
3. **Night 123, frame 132's second cause.** s143 turn 7, `msg.challenge_tester(refs=["echo_json_compact_3", "inh_echo_json_03"], quotes=['The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.', 'result = runner.invoke(echo_json, [str(BadObj())], catch_exceptions=False)'], round_no=0)`. State: m64 `answered` with the note, the Architect's answer m67 with no text, s141 with no receipt. Admitted.

The guards beside them:

4. Two unanswered priors on one version refuse with the bound's sentence. With no escalation on the refs, the sentence names `msg.escalate_architect` and records the offer. With an answered escalation, it says `End the session with no call.` and records none.
5. A judged prior refuses with the true-repeat sentence, in both step forms.
6. A prior that moved and then was judged: the newest prior decides, so a judged prior after a move refuses.
7. An open newest prior beside an older closed one gets the waiting sentence.
8. The Critic's challenge and the Developer's escalation keep today's sentences to the byte.
9. Night 119's s250 burst, both calls in one reply: the first lands, and the second meets the duplicate guard. That is frame 116's ground, section 3.7.

### 3.7 Frame 116

Frame 116 reads two lines: replies that land or attempt more than one challenge, and sessions refused the same challenge three times (copied: `plans/stack.md`, frame 116).

- The duplicate guard at `sandbox.py:1884` is unchanged, so a reply still lands at most one challenge to the Tester (reasoned).
- The door admits calls that it refused before, so refusals of one refs set fall. The second line can only fall (reasoned: no new refusal enters, and the bound's refusal needs two landed challenges first).
- One thing changes. In a burst, the door can now admit the first call, and the duplicate guard then refuses the second. Night 119's s250 landed `tst_v3` as m137 only because the door refused `tst_v1` first (observed: `probe4.py 119 s250`, 2026-10-05). With the new door, `tst_v1`'s re-send lands, and `tst_v3`'s challenge waits for a later session. The count per reply does not change.
- The duplicate guard's sentence says `with different refs` even when the refs are equal. That sentence is frame 116's, and this pass leaves it.

### 3.8 The ends-when

1. **Mechanism.** For the Developer's `msg.challenge_tester`, the door decides on the newest prior with the same sorted refs. An open prior waits. A prior after which a row of its refs has a receipt, from a session at or after the prior's first woken session, admits. A prior with the Tester's answer row and no such receipt refuses as the same argument. A prior with neither admits, unless two such priors stand on one version. Each refusal states one fact and one step, and it names `msg.escalate_architect` only when the escalate branch admits it, recorded as an offer. The sandbox tests on the calls of s145 (night 122), s250 (night 119) and s143 (night 123) admit. The bound and the true repeat refuse. `L1-DV-act-on-an-answered-challenge` is green again after its re-record. The gate's stale line reads 0.
2. **Ratio, on a night that has a challenge to the Tester.** Refusals of the answered form whose prior the Tester did not answer, with fewer than two such priors on the version, or whose test moved after the prior, fall from 125 of 141 on nights 113 to 123 to at most 1 in 20. The nights that found the wall: night 119 25 of 25, night 122 6 of 6, night 123 18 of 18. After a Tester challenge session that ends with nothing written and nothing sent, a second challenge on the same test reaches the Tester in at least half of such sessions, from 0 of 8 on nights 113 to 123. The behaviour it buys is read and not gated: the challenged test moves after a barren close, from 1 of 8.
3. **Residue.** A Developer session that still meets `on exactly these refs already ... and they answered` while the Tester's last session on those refs wrote nothing, or while a row of the refs moved after the prior, is read. The frame closes when its cause is not this predicate: the bound, a move before the prior's first woken session, another door, or the Tester's own doors, frame 147. That cause is a new frame.

A night may have no such case: nights 115 and 118 had none of class a or b. Then the frame closes on a seam: the three recorded calls of section 3.6, each on a read-only copy of its night's database, sent through the real door. Frames 135 and 136 closed that way (copied: `plans/archive/stack-2026-10-05.md`, frame 136, status 12:32).

### 3.9 The price

Anchors (copied: `plans/archive/stack-2026-10-05.md`, frames 135 and 136, last status lines):

- Frame 136: the design 214.6k, pass 1 56.9k and pass 2 41.4k on the same agent, reviews 122.4k and 76.9k.
- Frame 135: four passes 188.1k against 30k, four reviews 304.3k against 20k. Each review found a hole behind a sentence that named a call (copied: `plans/operating-facts.md`, rulings on briefs and doors, the last line).

The pass touches one function, `_bind_send.stage`, one new helper, nine tests and one re-record. It touches no schema, no runner and no brief. Price:

- Pass 1 on this agent, resumed: about 60k. The behaviour it buys: sections 3.1, 3.4 and 3.6, and the gate.
- One diff review: about 80k. The behaviour it buys: a reader on a worktree who follows each named call, and who replays the three recorded calls.
- A second pass, about 40k, and a delta review, about 70k, are likely, because both anchors needed them. Expected total: about 100k in passes and 150k in reviews. The re-record of one case and the gate's wall time, about 10 to 19 minutes, are apart.
- The risk that cost frame 135 four reviews is smaller here, because frame 144's follow check sends each named call through the doors on every gate (reasoned).

### 3.10 Open questions for the judging session

1. **[med] Which route opens an unanswered challenge?** Option 1 admits one re-send per version and changes no wiring. Option 2 keeps the challenge open and wakes the Tester again on the same message. That is a wiring change: the Tester wakes instead of the Architect's `tick:unresolved` rung, and night 33's barren close at `db.py:765` is reversed. Recommended: option 1.
2. **[low] How many unanswered challenges stand on one version before the bound refuses?** Recommended: 2, one re-send. A stochastic seat gets one more wake, and 21 of 43 Tester challenge sessions move the test. A higher number adds one Tester and one Architect session per round with no evidence that a third wake helps.
3. **[low] Does the true repeat's sentence move to one step now?** One step obeys the ruling in `plans/operating-facts.md` and makes one case stale, `L1-DV-act-on-an-answered-challenge`, 5 runs. Keeping the old sentence keeps the case and keeps two steps, one of which the escalate branch refuses after a first escalation. Recommended: one step, with the re-record.
4. **[low] Is the scope the Developer's challenge to the Tester only?** The Critic's challenge, the escalate form and the fix wake's thread line stay. The thread line reads the Architect's empty answer as `answered with no words` (reasoned: section 1.4), and night 123's seats re-sent 18 times past it (observed: section 2.2). The escalate form's 48 of 58 refusals with no answer row are frame 115's ground. Recommended: yes, this scope.

## Not read, not run

- The turns of the 8 barren Tester sessions past their calls. Night 119's s249 and night 123's s141 are read by the night reads (copied: `plans/night119-read-fable.md`, `plans/night123-read.md`). s185, s143, s304, s247 and s331 are not read.
- The counterfactual of a landed re-send. The replay runs on each night's state, and no model ran.
- Whether any write to a challenged test fell between the challenge and its first woken session, the derivation's gap of section 3.1. The sender's session is not stored, so the script cannot find it.
- The night reads' pairing of calls and results. The difference on night 123, 18 against 17, is explained by s149 only (observed: section 2.1).
- The register's tallies of `L1-DV-act-on-an-answered-challenge` per load. Only the pass rate and the transcripts at the current hash were read.
- No test ran, and no gate ran, as the brief rules for pass 0.
