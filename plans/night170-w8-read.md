# The read of night 170's W8 under rule C76: a seat re-sends a write that landed

Read only, 2026-10-28, on `rota/foundation` at 8fab13fd. Registers opened with `?mode=ro`. Scripts `turns.py`, `twins.py` and `reach2.py` are in the read session's scratchpad.

## 0. The result

- **The cause is not in the twin check.** All 16 twin refusals of the two nights name a row that the same session wrote earlier and saw land with an `OK` line. 0 name a row of another session (observed: `twins.py` on both registers).
- **The seat re-sends because nothing tells it that its work is done.** In all 5 sessions, the first landed criterion met the wake ("No criterion yet: tk_1") by turn 2. Every twin refusal came after that (observed: `sessions.wake_detail`, `turns`).
- **The shape is wider than criteria.** A seat re-sends a call that landed earlier in the session, and a door refuses it. Night 170 has 37 such refusals in 27 sessions, and night 171 has 32 in 20 sessions (observed: `reach2.py`, a lower bound, 32 turns a night not mapped).
- **Proposal:** one check in the runner before the door runs. A copy of a call that landed in this session gets an `OK` line that names the turn and the earlier answer. A turn of copies only ends the session. Price: 2 cycles (reasoned).

## 1. The turns, verbatim

Night 170 s118, turn 1: c_1 to c_6 sent. Turn 2 shows "OK ... c_1" to "c_5", then "ERROR criteria.specify(id='c_6'): this says what c_4 says, in nearly the same words". The seat sends c_6 again with c_4's exact words. Turn 3 shows "those are c_4's words already, on the same ticket. The same words are the same criterion; if the ticket needs a second criterion, it needs a second sentence". The seat tries c_7, then c_6, with the same words (observed: `turns`, s118).

Night 170 s160, turn 1: two calls. Turn 2 shows an id refusal for `tk_1_clear_screen_return` and "OK criteria.specify -> {"id": "tk_2_clear_screen_return"}". The seat re-sends both calls unchanged. Turn 3 shows "those are tk_2_clear_screen_return's words already". The seat renames to `c2_nonterminal_false`, then sends `msg.answer_tester` with that id: "'c2_nonterminal_false' names no row" (observed: s160 turns 2 to 6).

Night 170 s187: c_1 lands at turn 2. Turns 3 to 5 show a `ledger.log` refusal and two "You wrote tool results into your own reply" lines. The seat sends c_2 with c_1's words and a fault "This criterion duplicates c_1". At turn 6 it re-sends c_1 with its own id and words. The refusal reads "those are c_1_format_filename_example's words already" three times (observed: s187).

Night 171 s117, turn 2: "OK ... c_1", a near-twin refusal of c_2, "OK ... c_3". The seat re-sends the whole batch. The twin refusals name c_1 and c_3 against themselves. The seat then writes "c_1, c_2, c_3 were rejected as duplicates or already existing" and "duplicates of non-existent or invalid previous attempts". It logs 5 `blocked` faults and challenges the Vision Keeper with a wrong quote (observed: s117 turns 3 to 9). c_1 and c_3 landed (observed: `criteria` of tk_1). Correction to the brief: c_2 was refused as a near twin of c_1, not as an exact twin (observed: s117 turn 2).

Night 171 s222: c_1 lands at turn 2. After "no entry for 'format_filename'" the seat re-sends c_1 at turn 3, and at turns 4 to 6. At turn 6 it writes "already specified in this session ... The work is done" and sends c_1 again (observed: s222).

What the seat saw before the first re-send, in three kinds (observed: the turns above):
1. A mixed batch result, some `OK` and one `ERROR`: the seat re-sends the whole batch (s160, s117).
2. A turn with no new state, a correction or an empty read: the seat goes back to its one write (s187, s222).
3. A near-twin refusal: the seat cuts its text into the twin's words (s118).

After the first twin refusal, the text names the seat's own row as "already" and asks for "a second sentence". It does not say that the row landed and stands. One seat read it as a rejection (s117). One seat read it right and still re-sent (s222).

## 2. Match by symptom

- Frame 93, parked: "A write that changes nothing is accepted silently, and the seat repeats it". Its built sentence for `code.write` did not stop the repeat on nights 100 and 101. Its last open status says "the repeat itself is the seat's judgement" (observed: `plans/stack.md` line 3361 and its status of 2026-09-30 22:24).
- Frame 322: changed the twin text to name the empty ticket, at bf300ce4 (observed: `git log`). It did not change the answer to a seat's own row.
- Night 170's W11, "Seats repeat a call after 'Your work here is done'", 24 refusals, no fact (observed: `plans/night170-read.md`). The same shape at the message door.
- Night 171's W10 and W18 for s117 (observed: `plans/night171-read.md`).
- F17 does not reach it. The door reads staged over landed correctly. The fault is the answer, not the read (reasoned: section 0, first point). F16 and F24 are near, and neither covers a re-sent landed call (observed: `plans/facts-2026-10-27.md`).

## 3. Purpose of the twin check

- DECISIONS 2026-08-28, "A fourth organ": "eleven for one item ... two of them the identical sentence. ... same ticket, same words, one row" (observed: `rota/DECISIONS.md` line 844). Law 14: "a model re-emits an act it already performed, and any table keyed by an invented id turns each re-issue into a new row" (observed: `rota/LAWS.md` line 351).
- The purpose is one row for one set of words. A refusal is one way to keep it, and an `OK` answer is another (reasoned).
- History: the text from 395535da (2026-08-27). The near twin at d579f6cf (2026-09-12). Frame 257's pass 1 answered "same id, same words" as unchanged. 4f69d0a4 (2026-10-24) put the twin refusal back, because "frame 257 does not own" the twin door, a coordinator's ruling, not Roman's (observed: the commit body and `api.py` comment at the `prior_ticket == ticket_id` branch).
- `tests.encode` already answers a byte-for-byte copy: "Reported rather than refused. ... an error would only invite it to try something else" (observed: `api.py` about 10758 to 10777).

## 4. What the code holds now

- The exact twin: `criteria_specify`, `api.py` about 6024 to 6047, reads `ctx.writes` then landed rows. `_twin_refusal`, `api.py` 5882 (observed).
- The message door: "you have already sent {verb} to {recipient}; saying it again with different refs ..." at `sandbox.py` 4522, through `_sent_this_session` at 1967. The text says "different refs" for an exact copy (observed).
- The runner's reader of "this session already sent this call": `already_run`, `answered` and `answered_at`, set at `runner.py` 5596 only after a call runs (observed). The repeat line "unchanged since you asked earlier" fires only when the door returns the same answer (`would_repeat`, about 5551). A door that raises skips it (observed).
- The stops: "refused the same way in three turns" note and the four-turn end, `runner.py` 5832 to 5842. Three identical completions end the session, 5317 (observed).

## 5. The reach

Refused exact re-sends of a call that landed earlier in the same session (observed: `reach2.py`):

| Door | Night 170 | Night 171 |
|---|---|---|
| Message door, `sandbox.py` 4522 | 18 | 14 |
| Runner repeat refusal "asked three times" on a write | 12 | 11 |
| `criteria.specify` exact twin | 3 | 5 |
| `verdicts.emit` "already landed", `api.py` 14368 | 3 | 2 |
| `batches.group` "already batched", `api.py` 7253 | 1 | 0 |
| All | 37 in 27 sessions | 32 in 20 sessions |

Same words under a new id, against the session's own row: 6 of 9 twin refusals on night 170 and 2 of 7 on night 171 (observed: `twins.py`). Only `criteria.specify` shows this kind (observed: the table). Doors that answer a copy without a refusal: `tests.encode`, `code.write` (frame 93), `brief.segment` (observed: `api.py` 1059, 10774).

## 6. Proposal

One check in `run_session`, `runner.py` about 5500, before `sb.call`. For a call that is not a read, with its key in `already_run` and an earlier `OK` answer, do not run the door. Answer "OK <name> -> done at turn <n> of this session: <the earlier answer>. It stands, and nothing more is needed for it." When every call of a turn is such a copy, end the session, as the verbatim stop does. A copy of a refused call still goes to its door (reasoned).

One branch beside it in `_twin_refusal`: when the twin is a row this session wrote, say "<id> is your criterion from this session. It landed and stands." Drop "a second sentence" there. This covers the new-id kind (reasoned).

- Red tests: replay s117 turn 2, s187 turn 6 and s222 turn 3 from the registers.
- Price: 1 pass and 1 review, 2 cycles. The gate marks stale the recorded cases where a seat re-sent a landed call, as frame 93 found (reasoned).
- Counts that move: the 37 and 32 refusals toward 0. W8's 9 and W10's 10 toward 0 with the branch. W11's 24 down. s117's 5 fault rows toward 0, unproven (reasoned).
- Departure: none from a ruling of Roman's found. Frame 93's premise holds: the answer is not silent, and the end, not the text, stops the loop. It reverses the coordinator's call at 4f69d0a4 (observed and reasoned).

## 7. Doubt

- Frame 93's sentence and the runner's "unchanged" line both failed to stop repeats (observed: nights 100 and 101; `ledger.log` and `problem.set_approval` rows in section 5). Only the session end is proven to stop the loop.
- Law 14 says "Journals record events. Saying a thing twice is two events." Skipping a copy of `ledger.log` may lose a row. Keep journal calls on today's path until a test shows what the ledger does with a copy.
- The end on a turn of copies may end a seat that meant to retry. s160 renamed ids and landed `c1_terminal_true` at turn 4. The rule keeps that path, because a refused copy still runs. Only a replay proves it.
- s117's root trigger is a near-twin refusal of a distinct fact: roaming=False and Local against roaming=True and Roaming. c_2 never landed. That is a separate wall, outside this proposal (observed: s117 turn 2; reasoned: the fact differs).
- 32 turns a night did not map calls to results, so the reach is a lower bound.
