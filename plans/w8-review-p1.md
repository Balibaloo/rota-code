# W8 pass 1 review: commit 5a357256 on w8root

Read-only review of `C:/Users/roman/rota_w8` at 5a357256, parent ae9b99c6. The read is `plans/night170-w8-read.md` section 6. No gate ran. Registers and `tests/rota/cassettes.db` were opened with `?mode=ro`.

Result: the check does what section 6 asks on the register shapes of s117 and s187. It holds law 14 for journal calls. The build's stale list is wrong in both directions. The new end does not reach s222, the case cited for it. Findings: 0 high, 8 low.

## (a) Verdicts

1. Holds. s117 turn 2 and s187 turn 6, replayed verbatim from the registers, get the OK line and no `criteria.specify` door call. A copy after a later write to the same row reaches its door.
2. Answered. The COPIES_END session commits with its writes, `loop.step` marks it productive, and the ladder wakes the next role, not the same seat.
3. Holds. Every call the check skips stages a table that `identity.NATURAL_KEYS` marks `journal`, or sends a message. `problem.assert` on an existing row stages an `items` row (kind `unkeyed`) and `refs` rows (kind `relation`). It is a staged row and not a journal write.
4. Partly. An exact copy of c_1 no longer reaches the twin door. The new id c_a gets the own-row branch, which names no next call and does not say that nothing more is needed (finding 4).
5. A pin exists, but it guards one phrase and not the rule (finding 6). The shape still arises at the message door, `verdicts.emit`, `batches.group` on a new id, `criteria.specify` on a new id, and the stood-by path (findings 5 and 7).
6. Holds. The tests still assert one row for one set of words.
7. Seven of the eight cases re-send a landed write in one session. L1-VK-the-account-before-the-behaviours does not. None of the seven is stale by the copy line, and one stale case is missing from the list (finding 1).

Point 3, the calls the check skips, by function and journal table:

- `ledger_log`: `ledger`, `faults`.
- `ledger_unaddressed`: `ledger`.
- `rulings_rule`: `rulings`, `faults`, `ledger`.
- `verdicts_emit`: `verdicts`.
- `verdicts_rule`: `finding_rulings`.
- `findings_find`: `findings`.
- `challenge_uphold`, `challenge_break`, `challenge_vacuous`: `challenges`, and `ledger` for break and vacuous.
- `decisions_author`: `decisions`, `ledger`.
- `transcript_append`: `entries`.
- `frame_assign`: `frame_rulings`, `ledger`.
- `surveys_attest`: `survey_records`, `survey_citations`.
- `schedule_reask`: `messages`.
- `tests_encode`, on the path that calls `_stage_ledger` (`api.py` 11002): `ledger`.
- Every `msg.*` verb: the check reads `ctx.outbound`.

The check decides per call result and not per op name. A call takes today's path only when it actually staged a journal row. Every table that a literal `ctx.writes.append` stages has a kind in `NATURAL_KEYS` (probe 6).

Point 4, the text the seat reads at s117 turn 3 (probe 4):

```
ERROR criteria.specify(id='c_a'): those are c_1's words already, on the same ticket. c_1 is your criterion from this session. It landed and stands.
ERROR criteria.specify(id='c_c'): those are c_3's words already, on the same ticket. c_3 is your criterion from this session. It landed and stands.
```

## (b) Findings

1. The stale list in the build report, section "Stale cases". Severity low. CONFIRMED.
   - L1-TE-a-new-behaviour-is-a-new-callable is stale, and the list omits it. cr_003 lands at turn 3, cr_005 sends cr_003's words at turn 5, and the turn 6 cassette holds the old twin text. The own-row branch changes that text.
   - L1-VK-the-account-before-the-behaviours is not a copy. Its turn 3 cassette says `NOT RUN, because you wrote a tool result of your own` for `calculate_total_with_tip`.
   - In the other seven, the copy turn holds copies alone. The session now ends there with COPIES_END. No later prompt shows the copy line, so no cassette key misses on it.
   - In L1-VK-relay-the-ruling the copy is `problem.set_approval` at turn 4, which landed again at turn 3. It is not `problem.prioritize`.
   - Fix: replace the list with the copy-only turns and the own-row twin cases, and let the gate count the stale set.
2. The six L1 cases of finding 1 end earlier than their recording. Severity low. PLAUSIBLE.
   - The build's suite ran with `--ignore=tests/rota/test_l1.py`. Nobody measured whether these six still pass with the shorter session.
   - L1-VK-an-outside-fact-is-the-researchers is red in its newest run already.
   - Fix: run the gate before the merge, and read each of the six for a call lost after the copy turn.
3. `tests/rota/test_landed_copy.py` 112, `test_s222_a_reply_of_copies_alone_ends_the_session`. Severity low. CONFIRMED.
   - The register's s222 turns 4 to 6 each pair c_1 with `glossary.lookup`. The test replaces turns 5 and 6 with c_1 alone.
   - Probe 1 replayed the six register turns verbatim. The copies got the OK line, but COPIES_END never fired. The lookups got "asked three times" refusals.
   - The commit cites s222 as the reason for the end. The end does not reach the real s222 shape.
   - Fix: replay the register turns verbatim, and count a read that the repeat line answers as no new call, or drop the s222 claim.
4. `rota/roles/api.py` 5905 to 5909, the own-row branch of `_twin_refusal`. Severity low. CONFIRMED.
   - The branch is an ERROR line with no step. It does not say that nothing more is needed.
   - The runner's copy line ends "It stands, and nothing more is needed for it." The message door ends "Your work here is done". `verdicts.emit` ends "end the session".
   - One situation, a re-send of the seat's own landed work, now gets three different answers.
   - Fix: end the own-row branch with "Nothing more is needed for it.", as the runner line does.
5. `rota/roles/api.py` 7261, the `batches.group` twin. Severity low. CONFIRMED.
   - A new id on an item that this session batched gets "already batched as b_123456 ... reorder it with problem.prioritize, or recompose it through a scope change".
   - The recorded case L1-AR-group-into-batches does this at turn 4. The refusal offers other work for a batch that landed and stands. This is the W8 shape, and only the criteria twin got an own-row branch.
   - Fix: add an own-session branch at 7261 that names the batch as the seat's own and says it stands.
6. `tests/rota/test_landed_copy.py` 180, `test_the_copy_line_has_one_writer`. Severity low. CONFIRMED.
   - The pin counts the string "-> done at turn" in `rota/`. A door that answers a copy in other words passes it.
   - The own-row branch in `api.py` is such a second answer already.
   - Fix: pin the behaviour instead. Send an exact copy of each non-journal write through `run_session`, and assert that its door is not called.
7. `rota/core/runner.py` 5309 to 5321, the stood-by path. Severity low. PLAUSIBLE.
   - A held call that lands is not added to `already_run` or `landed`.
   - When another held call is refused, the seat gets one retry turn. A re-send of the whole batch, the s117 shape, then sends the landed call to its door.
   - Not probed. In the criteria mode every read is pushed, so nothing is held there.
   - Fix: enter a held call that lands into `already_run` and `landed`, as the main loop does.
8. Outside the points. `rota/core/runner.py` 5616, the repeat line after a dropped entry. Severity low. CONFIRMED. The fault exists before this commit.
   - Probe 3 sent `problem.assert` A, then B on the same id, then A again. The third call reached its door and moved the row back from B to A.
   - The seat read "unchanged since you asked earlier this session", which is false.
   - The comment on `drop_landed` states the opposite premise: "the copy then changes the rows again".
   - Fix: do not show the repeat line for a key whose `landed` entry a later write dropped.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/w8rev/`. Each ran from the worktree root with `PYTHONPATH=C:/Users/roman/rota_w8`.

1. `p1_replay.py s117`, `s187` and `s222`: seed a fresh database with the register's item, tickets and glossary. Feed the register completions to `run_session` through `ScriptedBackend`. Log every door call.
   - s117: in turn 2 the door saw only c_2. The turn 3 prompt held the OK lines for c_1 and c_3.
   - s187: two `criteria.specify` door calls, at turns 1 and 4. Turn 6 got the OK line, and `ledger.log` beside it ran.
   - s222: one `criteria.specify` door call. There was no COPIES_END, and the run took 7 prompts.
2. `p2_step.py`: s222's c_1 sent twice through `loop.step`. Result: committed, 2 iterations, COPIES_END, productive, 2 writes. The frontier after it is `architect<-tick:grouping()`.
3. `p1d_later_write.py`: a Vision Keeper challenge session on an existing item, with `problem.assert` A,A and then A,B,A, each on a fresh database.
   - A,A ends with COPIES_END after one door call.
   - A,B,A makes three door calls, and the item ends with A's text.
   - `p2b_message_end.py` shows trigger m1 `answered` and the next wake `vision_keeper<-tick:signoff()`.
4. `p4_s117_t3.py s117t3`: s117 turns 1 to 3 from the register. The output gives the own-row text for c_a and c_c, and the near-twin text for c_b.
5. `p7_stale.py` and `p7b_results.py`: these read the newest qwen3:8b run of the eight cases. They also read the cassette of each copying turn whose prompt holds the earlier turns. An inline query searched the newest runs for the twin and batch refusal texts.
6. Inline queries:
   - The kinds in `NATURAL_KEYS`.
   - The tables that `ctx.writes.append` stages, against their kinds.
   - `rota.tools.map` on the writers of each journal table.
7. `p7c_relay.py` and `p7d_relay_cut.py`: the relay case's call order through `run_session`, with the two doors stubbed to stage the item row.
   - Without the turn 3 cut, there is no copy line.
   - With the recorded cut, COPIES_END comes at turn 4 after 3 door calls.

## (d) Usage

The harness gives no split by input and output. Its counter fell by about 185k tokens over the review, and that figure counts each turn's context again. The output was about 18k tokens. The total passed the 80k cap, mainly from the register and cassette reads.
