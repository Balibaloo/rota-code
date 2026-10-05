# Frames 132 and 145, pass 1: the same-refs door reads who answered and what moved

Meta workflow. Pass 1 of frame 132, a Tester answers a challenge in prose and sends no test, and frame 145, a challenge of a test's new version is refused as answered. The implementing agent on Opus wrote this record on 2026-10-05. It builds sections 3.1 to 3.6 of `plans/frame132-design.md` on HEAD f5e1884, with the judging session's four rulings: option 1, a bound of 2, the one-step text, and the Developer's `msg.challenge_tester` only. The code and the tests are commit 4968ea7, on top of fbb905b.

## The predicate as built

The door is now a set of module functions in `rota/core/sandbox.py`, so that a replay on a night's database runs the same code as `stage` (observed: the diff, 2026-10-05).

- `_same_refs_refusal(ctx, recipient, verb, refs)` (`sandbox.py:1109`) returns the refusal or None. `stage` calls it at `:1583` and raises the text. The branch for every sender and verb except the Developer's challenge to the Tester is today's code, moved and not changed.
- `_challenge_repeat_refusal(ctx, rows, refs)` (`:1045`) holds the new predicate. It runs only when `ctx.role == "developer"`, `recipient == "tester"` and `verb == "challenge"`.
- `_same_refs_rows` (`:946`) is today's query and today's sorted-refs match, newest first.
- `_moved_since_woken(conn, msg_id, refs)` (`:1015`) is `moved(P)`: a `receipts` row on a row id of the refs, any table, from a session whose `seq` is at or above the lowest `seq` of the sessions with `trigger_msg = P`. It is false when P woke no session.
- `_judged_by(conn, msg_id, "tester")` (`:1036`) is `judged(P)`: the newest answer row with `cause_id = P` from the Tester.
- `UNANSWERED_CHALLENGES = 2` (`:943`) is the bound.

The order, on the newest prior P:

1. No prior: admit.
2. P is `open`: today's waiting sentence, from `_waits_refusal` (`:1002`), which both branches now use.
3. `moved(P)`: admit (frame 145).
4. `judged(P)`: the true-repeat sentence.
5. Otherwise: count the unanswered priors, newest first, from P. Each counted prior is closed, not judged and not moved. The count stops at the first judged or moved prior. An older `open` prior is skipped, and it neither counts nor stops the count. Below 2: admit (frame 132). At 2: the bound's sentence.

An admitted call returns today's result, `{"id": ..., "to": "tester", "verb": "challenge"}`, with no note (observed: the three night tests, 2026-10-05).

## The helper

`_escalation_admitted(ctx, refs)` (`sandbox.py:988`) is true when `msg.escalate_architect` on the refs passes the two repeat doors of `_bind_send`:

- the same-refs door: `_same_refs_refusal(ctx, "architect", "escalate", refs) is None`, which is the function `stage` runs for the escalation. For the Developer it refuses any escalation on the same sorted refs, open or closed.
- the duplicate guard: `_sent_this_session(ctx, "architect", "escalate")` (`:976`). The guard in `stage` (`:2052`) now calls the same function. Its sentence did not change.

Each sentence that names the escalation records it with `api._offer(ctx, said, "msg.escalate_architect", {"refs": list(refs)})`.

## The refusal texts

The true repeat, judged and not moved:

- Escalation admitted: `you sent challenge to tester on exactly these refs already (m96) and they answered (m98). Sending it again is the same argument again. Send msg.escalate_architect on the same refs.`
- Escalation refused: `you sent challenge to tester on exactly these refs already (m96) and they answered (m98). Sending it again is the same argument again. Make one real change to the code the test calls.`

The bound, two unanswered priors on one version, the older first:

- Escalation admitted: `you sent challenge to tester on exactly these refs already (m1, then m3), and the Tester answered neither and did not change the test. Send msg.escalate_architect on the same refs.`
- Escalation refused: `you sent challenge to tester on exactly these refs already (m1, then m3), and the Tester answered neither and did not change the test. End the session with no call.`

The waiting sentence, the Critic's sentences, the escalation's three sentences and the duplicate guard's sentence keep today's text (observed: their tests pass unchanged, and `test_the_critics_repeat_challenge_keeps_its_sentence` holds the Critic's to the byte, 2026-10-05).

## The tests

All in `tests/rota/test_desk_guards.py`, beside the door's existing tests.

Changed, three (section 3.5):

- `test_a_challenge_that_waits_for_its_answer_is_not_sent_twice` (`:594`), second half. Before: m1 stayed `open` beside the Tester's answer m2, and the test asserted `... already (m1) and they answered. Sending it again is the same argument again. Do not send this challenge again. Send msg.escalate_architect on the same refs, or make one real change to the code the test calls.` Now: m1 is set `answered`, and the test asserts the one-step sentence with `(m2)`. The commit that writes a Tester's answer also sets the challenge `answered` (`db.py:778-782`), so an open challenge with the Tester's answer row does not occur in a night (reasoned: `cause_id` is the session's trigger, `sandbox.py` stages `cause_id = ctx.trigger`).
- `test_a_closed_challenge_with_no_answer_row_is_answered` became `test_a_closed_challenge_with_no_answer_row_admits_one_resend` (`:671`). Before: it asserted the refusal `(m1) and they answered. ... Send msg.escalate_architect on the same refs`. Now: it asserts the admitted result `{"id": "m2", "to": "tester", "verb": "challenge"}`.
- `test_a_repeat_challenge_is_told_the_rung_as_a_sentence` (`:688`). Before: the two-step sentence with no answer id. Now: `(m96) and they answered (m98). ... Send msg.escalate_architect on the same refs.`, and still no ` -- `.

Added, 13 test functions, 14 test cases (section 3.6, items 1 to 9):

1. `test_night122_a_challenge_of_the_tests_new_version_lands` (`:781`): s145's turn-4 call on night 122's rows. m66 `answered`, s144 woken by m66 with a `tests` receipt on `inh_echo_json_01`, the row at version 2. Admitted as m67.
2. `test_night119_a_challenge_the_tester_left_unanswered_lands` (`:800`): s250's first call on night 119's rows. m136 `unresolved` with the note, s249 with nothing, and the receipts of s241 and s247 before m136's wake. Admitted as m137. Then the Architect's empty answer m143 and the status `answered`: admitted again, as m144.
3. `test_night123_a_challenge_after_an_empty_rung_lands` (`:825`): s143's turn-7 call on night 123's rows. m64 `answered` with the note, the Architect's empty answer m67, s141 with nothing. Admitted as m68.
4. `test_two_unanswered_challenges_on_one_version_refuse_with_the_bound` (`:859`) and `test_the_bound_names_no_escalation_that_the_door_refuses` (`:872`): the bound's two forms. The first records one offer. The second records none, and the escalation is then refused by the door with `(m4)`.
5. `test_a_judged_challenge_names_the_escalation_when_the_door_admits_it` (`:897`), and `test_a_judged_challenge_names_a_code_change_after_an_escalation` (`:913`) with two cases, a stored escalation and one sent in this session. The first form records one offer, and the named escalation then lands.
6. `test_a_judged_challenge_after_a_move_refuses_on_the_newest_prior` (`:930`).
7. `test_an_open_newest_challenge_waits_beside_an_older_closed_one` (`:947`).
8. `test_the_critics_repeat_challenge_keeps_its_sentence` (`:963`). The Developer's escalation sentences are held by the existing escalation tests, which did not change.
9. `test_night119_a_burst_lands_its_first_challenge_and_guards_the_second` (`:982`): s250's two calls in one sandbox. The first lands as m137. The second meets the duplicate guard's sentence. Version 1 of `tst_v3` is copied from the prompt of s250's first turn, because the row moved to version 2 later that night.

The fixtures copy the criteria texts and the test bodies byte for byte from the nights (observed: a `repr` of each row, 2026-10-05). The session s139 has no trigger in the fixtures, because the foreign key refuses `m63`, a message that the fixtures do not hold. The trigger takes no part in the door.

The follow check sent the five offers that the new tests record through the real doors. The doors admitted all five (observed: `ROTA_OFFER_LOG` on the new tests, 2026-10-05).

`tests/rota/test_desk_guards.py`: 249 passed. `tests/rota/test_offers_followed.py` and `tests/rota/test_t0_sandbox.py`: 87 passed, 3 xfailed (observed: 2026-10-05).

## The case's tally

`L1-DV-act-on-an-answered-challenge` on qwen3:8b at prompt hash `3697edde4a361441` (observed: `case_runs`, 2026-10-05):

- Before: 258 of 258. A replay of the case on the new text read `STALE ... no recording for the current prompt`.
- The re-record, as `rota.tools.gate` runs one: `ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 ROTA_REFRESH=1`, then the same without `ROTA_REFRESH`, each on the exact node id, `-n0`. The refresh run: 5 of 5, 33 recorded, all five live. The plain run: 5 of 5, 33 replayed.
- After: 268 of 268 at the same prompt hash. The hash did not move, because the case's first prompt holds no refusal.
- In each of the five live runs, the seat sent the challenge, met `... and they answered (m_...). Sending it again is the same argument again. Send msg.escalate_architect on the same refs.`, and then sent `msg.escalate_architect` on the same refs, which landed.

The repository does not commit the register: `.gitignore:32` names `tests/rota/cassettes.db`. So no cassette commit exists.

## Proof 1: the replay through the real code

`replay.py` in the scratch folder `f132p1` of session c81b16d3 (observed: 2026-10-05). It copies each night with SQLite's backup API from a read-only connection. For each of the 141 refused challenges of `classes.tsv`, it rebuilds the night's state at the refusing session S inside a savepoint, calls `sandbox._same_refs_refusal(ctx, "tester", "challenge", refs)` on a Developer's `ctx`, and rolls back.

The rebuilt state:

- Sessions at or after S, and their receipts, are deleted.
- A message is visible at S when its id number is at most the highest id that a session before S sent, or a trigger of a session up to S, or the prior S cited. It is gone when its id is at least the lowest id that a session at or after S sent. The sender of a message comes from the runner's `OK msg.* -> {"id": ...}` line in that session's turns. The runner is serial, and `new_id` counts up from the table, so id order is creation order (reasoned: `runner.py:61-91`, no thread in the runner).
- A visible same-refs challenge that no session before S woke reads `open`.

The check of the rebuilt state: on it, the old door's loop picks the prior that the night's refusal cited in 141 of 141 runs. No message on the refs fell between the two bounds.

| Class | Refusals | Admitted | Refused |
|---|---|---|---|
| a1 | 16 | 16 | 0 |
| a2 | 43 | 43 | 0 |
| b | 66 | 66 | 0 |
| c | 16 | 0 | 16 |
| All | 141 | 125 | 16 |

The real door and the design's script differ on 0 of 141 calls. Of the 16 refusals, 15 name the escalation, and 1 says `Make one real change to the code the test calls.`: night 121 s241 on m131, where an escalation on the same refs exists. No refusal took the bound's form or the waiting form.

## Proof 2: the seam

`seam.py` in the same folder sends each recorded call through `Sandbox.call`, so every door of `stage` runs, `_challenge_evidence` included. Each runs on a copy of its night, once at the rebuilt state of the session and once at the night's end state (observed: 2026-10-05).

- Night 122, s145, turn 4: `{'id': 'm117', 'to': 'tester', 'verb': 'challenge'}` at both states.
- Night 119, s250, turn 1, the first call: `{'id': 'm170', 'to': 'tester', 'verb': 'challenge'}` at both states.
- Night 123, s143, turn 7: `{'id': 'm156', 'to': 'tester', 'verb': 'challenge'}` at both states.

The id is the copy's next id, because the rebuild removes only the rows on the same refs. At s250's rebuilt state, m136 reads `answered`, not `unresolved`, because the rebuild restores only `open`. The door reads both as closed (reasoned: `_challenge_repeat_refusal` tests `status == "open"` only).

## Deviations from the design

1. The helper checks the duplicate guard as well as the same-refs branch. The design names the same-refs branch only. A Developer who escalated earlier in the session meets `you have already sent escalate to architect` on the named call. So the sentence names the escalation only where both doors admit it (reasoned: frame 135's law, `plans/operating-facts.md`). `test_a_judged_challenge_names_a_code_change_after_an_escalation[this session]` holds it.
2. The whole same-refs door moved out of `stage` into module functions. The design asked for one helper for the escalate check. The move lets the replay call the door that `stage` calls, and it lets the helper call the escalation's real branch. No text moved (reasoned: the gate's stale line and the unchanged escalation tests).
3. An older `open` prior is skipped in the count. The design does not say what an older open prior does. It has not reached the Tester, so it is not a challenge that the Tester left unanswered (reasoned). No refusal of the 141 met that state.
4. The first half of section 3.6 item 4 and item 5 run on the suite's own fixture rows, not a night's rows. The design asks for night rows on items 1 to 3 only.

## Seen and not fixed

- The Critic's kept sentence, `Send msg.escalate_architect on the same refs, or make one real change to the code the test calls.`, names a call that the Critic does not hold. `rota/roles/prompts/critic/review.tools` holds `msg.challenge_tester` and no `msg.escalate_architect` (observed: grep, 2026-10-05). The brief keeps the Critic's text to the byte. It is frame 135's law in another door.
- `test_desk_guards.py:1898` prints a `SyntaxWarning` for `"\["` in a `match=` string. It was there before this pass.
- The design's class a2 reads answer rows at the night's end. At s250's time on night 119 and at s143's time on night 123, the Architect's empty answers m143 and m67 did not exist yet. Those refusals were class a1 at their time. Both classes admit, so the count does not change (observed: the seam's rebuilt states, 2026-10-05).

## The suite

The gate on the working tree of this pass, before the commit (observed: `python -m rota.tools.gate`, 2026-10-05, 604.1 s):

```
suite: 24 failed, 2744 passed, 27 skipped, 4 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_handover.py::test_release_empties_the_seat, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 604.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate also printed `flaky: tests/rota/test_handover.py::test_release_empties_the_seat`, and that test passed on the gate's re-run. `plans/operating-facts.md` names the same test as a new red that passes alone. The other three new reds are the three that the brief names at the baseline. Their tracebacks: `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist` 0/5, no question to the Terminologist; `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` 0/5, no write to `tests`; `test_mode_lists_its_base_file_and_joins_every_line`, `assert 10 == 9`. None of them reads the same-refs door (reasoned: a Critic's question, a Tester's encode, and the map tool's mode listing).
