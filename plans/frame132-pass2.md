# Frames 132 and 145, pass 2: a cap on the chain, and the review's five smaller points

Meta workflow. Pass 2 of frame 132 and frame 145, on the review of 4968ea7 (`fc5ea79`). The implementing agent on Opus wrote this record on 2026-10-05. The code and the tests are commit b2ed55b, on top of a25f192. Every line below is cited at b2ed55b.

## The count that chooses the cap

`count.py` in the scratch folder `f132p1` of session c81b16d3 reads nights 113 to 123 read-only. It groups the Developer's landed challenges to the Tester by batch and sorted refs. A set ends green when every test of its refs has its newest `test_runs` row at `pass`, or its batch reads `merged` (observed: 2026-10-05).

- 41 sets. Each set holds exactly 1 landed challenge.
- 14 sets ended green. The longest chain that ended green is 1.
- Night 124, the one night on the new door, holds 1 set with 1 landed challenge. It did not end green (observed: the same script on night 124, 2026-10-05).

The rule is one above the longest green chain and not below 3, so the cap is 3: `LANDED_CHALLENGES = 3` (`sandbox.py:1073`). The count cannot show a longer chain, because the old door refused every re-send on these nights (reasoned: the design's section 2.2). So 3 is the floor of the ruling, and no night measured it.

## The findings

1. **HIGH, the endless chain: fixed.** `_challenge_cap_refusal` (`sandbox.py:1087`) runs at both admit points of `_challenge_repeat_refusal` (`:1121`): after a move, and below the bound. It counts every landed challenge of the Developer on the same sorted refs, across moves. At 3 it refuses, and below 3 it admits. It runs only where the door would admit, so the waiting, true-repeat and bound sentences keep their texts. `db.py` and the attempt logic did not change.
2. **HIGH for the tests, the moved line: fixed.** `test_night122_a_judged_challenge_whose_test_moved_at_the_wake_lands` (`test_desk_guards.py:1025`) copies night 122's state at s145's turns 7 and 8: m64, the Tester's answer m65, and the receipt of s141, the session that m64 woke. It asserts the admit with s145's recorded call. `test_a_receipt_before_the_wake_is_no_move` (`:1035`) keeps only the receipt of s139, before the wake, and asserts the true-repeat refusal.
3. **LOW, the count loop: fixed.** `test_the_count_stops_at_a_moved_prior` (`:1056`), `test_the_count_stops_at_a_judged_prior` (`:1069`) and `test_the_count_skips_an_older_open_prior` (`:1078`). The skip test asserts the ids `(m1, then m3)`, so it tells a skip from a count and from a stop.
4. **LOW, the step in mode `exhausted`: fixed.** `build` now stores the session's working set as `ctx.working_set`, after every narrowing by `allow` and by the wake (`sandbox.py:582`). It follows the pattern of `ctx.triaged` and `ctx.intake`, which `build` arms from the same set. `_code_step` (`:1051`) gives `End the session with no call.` when `code.write` is not in the set. A context that `build` did not make keeps the step toward the code. `test_a_judged_challenge_in_mode_exhausted_ends_the_session` (`:1118`) holds it.
5. **LOW, a receipt of any table: fixed.** `_moved_since_woken` (`:1027`) reads only `table_name IN ('tests', 'criteria')`. Those are the real names: nights 113 to 123 hold 118 `tests` receipts and 119 `criteria` receipts among 22 table names (observed: a count, 2026-10-05). `test_a_receipt_of_another_table_is_no_move` (`:1047`) holds it with a `batches` receipt whose `row_id` is the test's id.
6. **LOW, an open prior with an answer row: fixed.** `test_an_open_prior_with_an_answer_row_waits` (`:1095`) pins the waiting sentence on that state.

## The new sentences

The cap, with the Developer's own landed challenges, oldest first:

- The test changed and is red, escalation admitted: `you sent challenge to tester on exactly these refs 3 times already (m1, m2, m3), and the test changed and is still red. Send msg.escalate_architect on the same refs.` The sentence records the offer.
- The same fact, escalation refused, `code.write` in the working set: `... and the test changed and is still red. Make one real change to the code the test calls.`
- The same fact, escalation refused, no `code.write`: `... and the test changed and is still red. End the session with no call.`
- No receipt on the refs since a prior's wake, or no newest run at fail or error: `you sent challenge to tester on exactly these refs 3 times already (m96, m99, m101). Send msg.escalate_architect on the same refs.`, with the same two other steps. A chain that the cap stops moved the test at least once, so this form is a guard (reasoned: an admit with three landed priors and no move needs a judged prior that a later challenge passed).

The true repeat in a session with no `code.write`: `you sent challenge to tester on exactly these refs already (m96) and they answered (m98). Sending it again is the same argument again. End the session with no call.`

"Still red" reads the newest `test_runs` row of each test of the refs (`_test_is_red`, `:1076`). "Changed" reads the same receipts as the move (`_moved_since_woken` on each prior). The sentence of `L1-DV-act-on-an-answered-challenge` did not change, so the case stays fresh (observed: the gate's stale line).

## Proof 1: the chain in the suite

`test_a_chain_of_moved_challenges_stops_at_the_cap` (`:1175`), on a batch of one test and on a batch of two tests. Each round the Developer challenges through `Sandbox.call`. The Tester runs `tests.triage` and `tests.encode` on `tst1` in mode `challenge`. `session_commit` lands the new version with the challenge as `trigger_msg`. The harness records a failing run of each test of the batch at `lifecycle.next_attempt` (observed: the test, 2026-10-05).

- A batch of one test: rounds 1 to 3 land, m1, m2 and m3. Round 4 is refused with the cap's sentence.
- A batch of two tests: rounds 1 to 3 land. Round 4 is refused with the same sentence.
- In both, the sentence records one offer, `msg.escalate_architect(refs=['c1', 'tst1'])`, and the same sandbox then sends that call, which lands to the Architect. The follow check sent the same offer through the doors, and they admitted it.

`test_the_cap_ends_the_session_when_no_escalation_or_code_is_left` (`:1189`), `test_the_cap_says_only_the_count_when_the_test_is_not_red` (`:1200`) and `test_the_cap_says_only_the_count_when_the_test_did_not_change` (`:1210`) hold the other forms.

## Proof 2: the replay of the 141 refusals

`replay2.py` in `f132p1` is pass 1's `replay.py` with one change: each session's sandbox is built with its mode's tools, from the session's wake kind (observed: 2026-10-05).

| Class | Refusals | Admitted | Refused |
|---|---|---|---|
| a1 | 16 | 16 | 0 |
| a2 | 43 | 43 | 0 |
| b | 66 | 66 | 0 |
| c | 16 | 0 | 16 |
| All | 141 | 125 | 16 |

The cap changes the answer of 0 calls. Each per-call line equals pass 1's line, because no set held more than one landed challenge at the time of its refusal. The state check holds again: on the rebuilt state the old door's loop picks the cited prior in 141 of 141 runs. Of the 7 refusals from mode `exhausted`, 4 are challenges of class b, which the door admits, and 3 are escalations, outside this door. So the new step meets no refusal of these nights.

## Proof 3: the mutants

`mutp.py` in `f132p1` is a pytest plugin. `MUT=<name>` execs a changed copy of `sandbox.py` as the module, and the file on disk does not change. The reviewer's nine mutants are M1 to M8. M9 to M16 are this pass's lines. Each run is `test_desk_guards.py` with the door's 51 tests selected. With no mutant, 51 pass (observed: 2026-10-05).

| Mutant | Change | Red tests |
|---|---|---|
| M1 | the move admit becomes `if False:` | 1 |
| M2 | `answer = None` | 10 |
| M3 | the bound always admits | 3 |
| M4 | the judged query ignores the role | 4 |
| M5a | the count does not stop at a moved prior | 1 |
| M5b | the count does not stop at a judged prior | 2 |
| M6 | `s.seq >` for `s.seq >=` | 1 |
| M7 | the helper ignores the duplicate guard | 1 |
| M8 | the count does not skip an open prior | 1 |
| M9 | a receipt of any table | 1 |
| M10 | no cap after a move | 4 |
| M11 | no cap below the bound | 1 |
| M12 | the cap at 99 | 5 |
| M13 | the code step ignores the working set | 2 |
| M14 | the test never reads red | 3 |
| M15 | "changed" is not checked | 1 |
| M16 | the helper ignores the escalation's own door | 4 |

All 17 mutants turn at least one test red.

## The follow check

The full gate ran the follow check on every test. It failed no test, so every offer that the new sentences record was admitted by the doors (observed: the gate, 2026-10-05). Nothing was added to `KNOWN_REFUSED_OFFERS`.

## The suite

`tests/rota/test_desk_guards.py`, `test_offers_followed.py` and `test_t0_sandbox.py`: 352 passed and 6 xfailed before the last test was added. The door's 51 tests pass with it (observed: 2026-10-05).

The gate on the working tree before the commit (observed: `python -m rota.tools.gate`, 2026-10-05, 627.1 s):

```
suite: 23 failed, 2762 passed, 27 skipped, 7 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 627.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that the brief names. No case went stale, so no re-record ran.

## Deviations from the brief

1. The cap's fact has a short form. The brief says that the fact is the count and that the test changed and is still red. The door states the second part only when the rows show a move and a red run, so that no sentence states a fact the rows do not hold (reasoned: frame 144's rule that a refusal's facts are true). One test holds the short form for each missing part.
2. The cap's second step follows the true repeat's step: the code change, or the end of the session when the working set holds no `code.write`. The brief names "the step of point 4", which is this choice.
3. `ctx.working_set` is a new attribute that `build` sets. No field held the working set before. `api.Ctx` did not change, and a context that `build` did not make reads None (reasoned: the pattern of `ctx.triaged`).
4. The test of finding 2 uses version 2 of `inh_echo_json_03`, the night's end state. s145's turn-7 quote, `assert output.getvalue() == "{}\n"`, is not in that body, and the evidence door still passes the call (observed: the test, 2026-10-05). So that call reached the same-refs door in the night too.
5. The cap's sentences record no `_fact`. The fact kinds of `check_facts` hold no message id and no test result.

## Seen and not fixed

- The evidence door passed s145's turn-7 call with a test-side quote that is not in the stored test. That door is `_challenge_evidence`, outside this frame.
- Pass 1's items stand: the Critic's kept sentence names a call that the Critic does not hold, and `test_desk_guards.py` prints a `SyntaxWarning` for `"\["`, which was there before.
