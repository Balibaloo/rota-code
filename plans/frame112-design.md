# Frame 112, a wake repeats on an unchanged tree: design, revision 1

Scope reader, meta workflow, 2026-10-02. Every statement is about the rota workflow unless it says meta workflow.

## 1. The dispatch path

- `tests_failing` produces the wake each tick from `test_runs`, with `detail="attempt {MAX(test_runs.attempt)}"`, while that attempt is below `loop_cap` = 10 (observed: rota/core/predicates.py:813-842, config.py:59, 2026-10-02).
- `step` counts the dispatch before the session runs: `note_dispatch` upserts `tick_attempts.attempts` for the key `role|kind|refs` (observed: loop.py:303, scheduler.py:1570-1591, 2026-10-02).
- When the count is 2 or more, `step` sets `wake.attempt = n`, and the runner says "attempt n of 3" in the prompt (observed: loop.py:304-311, runner.py:367-380, 2026-10-02).
- At the next frontier, `quarantine_overrun` and `quarantine_stalled` mark the key `quarantined = 1` at `tick_attempt_cap` = 3 and drop the wake (observed: scheduler.py:1705-1770, 1205-1217, config.py:122, 2026-10-02).
- A quarantined key wakes the Liaison on `tick:quarantined`, which presents "abandoned" to the principal (observed: night 107 s147, night 106 s206 and s229, 2026-10-02).
- The other ladder is `exhausted`: at `loop_cap` failing test attempts it wakes `_next_rung` of LADDER developer, architect, vision_keeper (observed: predicates.py:46, 887-923, 2026-10-02).
- There are two counters, not one. "attempt 8" is `MAX(test_runs.attempt)`, which grows per harness run on a new commit. `tick_attempts.attempts` counts dispatches without progress and is reset by a new `head_commit` or a moved test of the batch (observed: db.py:575-608, 2026-10-02).
- So night 107's `attempts=3` and "attempt 8" agree. s143 re-encoded `tst_echo_json_compact_4` (receipt tests v7), which reset the key, and s144, s145, s146 were dispatches 1, 2, 3 at test attempt 8 (observed: receipts and tick_attempts of clickI_night107.db, 2026-10-02).

## 2. The repeat groups

| night | sessions | key refs | detail | turns | receipts written | end of the last session |
|---|---|---|---|---|---|---|
| 106 | s143, s145 | bg_1 | attempt 3 | 8, 22 | none; batches v4 (commit) | a door refused four turns |
| 106 | s201, s202 | bg_2 | attempt 1 | 15, 9 | none; batches v11 (commit) | a refusal reply |
| 106 | s203, s204, s205 | bg_2 | attempt 2 | 11, 12, 18 | none, none, none | "ended a tick with nothing done" |
| 106 | s223, s224 | bg_2 | attempt 7 | 12, 23 | ledger row; batches v15 (commit) | "wrote code into its reply" |
| 106 | s226, s227, s228 | bg_2 | attempt 8 | 25, 17, 5 | none, none, none | a door refused four turns |
| 107 | s144, s145, s146 | echo_json_group | attempt 8 | 17, 25, 7 | none, none, none | the verbatim-repeat end |

- The head is one commit inside each group, because no session in the group wrote a `batches` receipt before the last (observed: receipts, both databases, 2026-10-02).
- Every session has a different `prompt_hash`, a different first-turn hash and a different completion hash (observed: sessions and turns, sha1 of the joined completions, 2026-10-02). No group is byte-identical. The attempt sentence moves the prompt.
- Ends in night 107: s144 ended on `code.source` refused four turns, s145 ran 25 turns and ended on a span door reply, s146 ended on the verbatim repeat (observed: last completion of each, 2026-10-02).
- Each group is separate dispatches of one live key. The key counted 1, 2, 3 and then quarantined (observed: tick_attempts rows, 2026-10-02). It is not one dispatch retried by the runner.
- The second dispatch committed in 3 of 6 groups (s145 of night 106, s202, s224). The third dispatch committed in 0 of 3 groups (s205, s228, s146) (observed: receipts, 2026-10-02).

## 3. The fact that says nothing changed

- `receipts` records every artefact write, but not `messages` and not `test_runs` (observed: receipts grouped by table_name, night 107, 2026-10-02).
- `batches.head_commit` alone misses a Tester re-encode, a ruling or a decision row (reasoned: those write other tables).
- `tests` versions catch a re-encode only. The last `prompt_hash` of the key always differs, because the attempt sentence is in the prompt (observed: section 2).
- The cheapest sufficient set: `MAX(receipts.rowid)`, `MAX(messages.rowid)` and `MAX(test_runs.rowid)` read at dispatch. Equal values at the next dispatch of the key mean no write, no message and no test run came between (reasoned: those three tables carry every move the seats and the harness make).
- A stored mark is needed, because a message has no session link (observed: messages columns, 2026-10-02). One column on `tick_attempts`, `mark TEXT`, holds the three numbers (reasoned).

## 4. What "the next rung" is in code

- The rung for a stuck key is the quarantine: `tick_attempts.quarantined = 1`, which `quarantine_stalled` reads to drop the wake and `tick:quarantined` reads to wake the Liaison (observed: scheduler.py:1758-1770, predicates.py:1500, 2026-10-02).
- The door must write that row. A skip that writes nothing spins: the predicate produces the same wake next tick, and the count does not move (reasoned: loop.py:261-290, tests_failing reads test_runs only).
- A door that sets `attempts = cap, quarantined = 1` drains the wake through the existing path. The Liaison reports it, and a commit or a moved test revives it (observed: db.py:557-572, 2026-10-02).
- `exhausted` is not this rung. It reads test attempts, and a skipped dispatch adds none (observed: predicates.py:907-923, 2026-10-02).

## 5. Relation to the existing ends

- The attempt sentence at runner.py:367-380 moves the prompt on dispatch 2 and 3. That move is what made the second dispatch commit in 3 of 6 groups (observed: section 2). It does not stop dispatch 3.
- The verbatim-repeat end at runner.py:2804-2809 ends a session after three equal turns. It works inside one session and never across sessions (observed: runner.py:2794-2809, 2026-10-02). s146 ended on it after 7 turns, so it shortened the third session but did not skip it.
- The CYCLE alert in rota/core/cycles.py keys on the detail and the receipt signature, writes nothing and gates nothing (observed: cycles.py:1-60, 2026-10-02).

## 6. Designs

- A, the frame's ends-when as written: skip any repeat with an unchanged mark. It would have removed s202 and s224, two commits, and s145 of night 106 if no message came between (observed: section 2). Declined.
- B, `tick_attempt_cap` = 2. It removes all three unproductive third dispatches. It also stops a third dispatch after a Tester answer between dispatch 2 and 3. It changes a law-4 setting for every tick kind (reasoned). Declined as the default.
- C, recommended, a door in the loop: at dispatch n >= 3, if the key's stored mark equals the three maxima now, do not run the session. Write `attempts = cap, quarantined = 1` and return a note. The record shows the quarantine row and the Liaison's `tick:quarantined` session, with no Developer session (reasoned).
- C rests on "a door is a fact about the database, wrong under every model": three row counts, no judgement of the reply (ruled: operating-facts doors). It bounds no LLM judgement. It refuses no call, so the note names the mark and the key, not a call that passes.
- Where: `step` in loop.py, after `note_dispatch` returns n and before `run_session`. `note_dispatch` writes the mark on every dispatch (reasoned).
- Test: one scheduler test in tests/core. Dispatch a `tests_failing` key twice with no write, then step a third time. Expect no session row, `quarantined = 1` and a `tick:quarantined` wake. A second case writes a message before the third step and expects the session (reasoned).
- Price, meta workflow: one implementer pass at about 300k, one diff review, and one night as the walk, because the frame moves the loop (reasoned: CLAUDE.md, a frame that touches a predicate ends on a walk).
- The ends-when needs Roman: "no group of sessions shares key and head" fails under C, because the second dispatch stays. The measured form is "no group of three" (reasoned: section 2).

Unanswered: night 105's groups and their "same 13 calls" are not read. Whether a do:harness run between dispatches writes `test_runs` before the next step is not checked.
