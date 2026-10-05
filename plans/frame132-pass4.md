# Frames 132 and 145, pass 4: the cap counts per criterion

Meta workflow. Pass 4 of frame 132 and frame 145, on the delta review of 4de1555. The implementing agent on Opus that wrote pass 3 wrote this record on 2026-10-05. The code and the tests are commit 96c5202, on top of bb1cce4, on the branch `f132p3`. Every line below is cited at 96c5202.

## The count that keeps the cap

`count_per_criterion.py` in the scratch folder `f132p3` of session 3f72d9cb reads the reviewer's copies of nights 113 to 124, read-only. A challenge counts for criterion c when its refs hold c, or hold a test whose criterion is c. A criterion ends green when every test of c has its newest run at `pass`, or its batch reads `merged` (observed: 2026-10-05).

| Landed challenges per criterion | Criteria | Green |
|---|---|---|
| 1 | 38 | 14 |
| 2 | 3 | 0 |

- The three criteria with 2 are night 117's `echo_json_compact`, `_2` and `_3`. Each has one challenge of its own and m79.
- The reviewer reports 39 with 1 and 2 with 2. The reviewer's `p4a_reach.py` counts only a criterion named in the refs, and this count also follows a test to its criterion. Both counts give the same cap.
- The longest chain on a criterion that ended green is 1. A cap of 3 refuses no challenge that led to green, so the cap stays at 3 (`LANDED_CHALLENGES`, `sandbox.py:1095`).

## The items

1. **HIGH, a new test id each round: fixed.** The cap counts per criterion. `_cap_keys` (`sandbox.py:1133`) gives the keys of the call's refs, in the refs' order: each criterion named directly or through a test. `_challenges_on` (`:1155`) counts every Developer challenge to the Tester whose refs hold the criterion or a test of it. A new test id of c1 is a test of c1, so it counts for c1.
2. **HIGH, one criterion against each test of the batch: fixed.** The same count. `[c1, tst1]`, `[c1, tst2]` and `[c1, tst3]` all count for c1. The call is refused when any criterion that it names is at the cap (`_challenge_cap_refusal`, `:1182`).
   - The count per test id is removed. A test with no criterion counts for itself, as the key `("test", id)`. Only that key adds a refusal that the criterion count lacks, because `tests.criterion_id` may be NULL in the schema. Refs that name neither a criterion nor a test keep pass 2's count of the same refs.
3. **LOW, the escalation with a repeated ref: fixed.** `_escalation_or_step` (`:1250`) asks `_escalation_admitted` on the refs with each ref once, and builds the offer on the same list. The true repeat, the bound and the cap all use it. The escalation door did not change.
4. **LOW, the encode of another criterion: fixed.** `_encodes_refused` (`:1277`) fires only when a Tester session that the prior woke holds a `tests.encode` row whose summary names a criterion of the prior's refs, directly or through a test. `_encoded_criterion` (`:1322`) reads `criterion_id='...'` from the summary. It needs exactly one match and the closing quote. Otherwise the rule does not fire.
5. **LOW, the criterion form of another criterion: fixed.** The cap reads criteria receipts on the counted criterion only. It reads tests receipts and red runs on the call's tests of that criterion, or on all its tests when the call names none.
6. **Tests: done.** One test per surviving row of the review, and one per line of this pass where a test could tell the change. The table is in proof 4.

## How reliable the encode's summary is

`Sandbox.call` cuts each argument of the summary at 60 characters (`sandbox.py`, the `args_summary` line). `criterion_id='` and the closing quote take 16, so an id of up to 44 characters reads whole. On the copies of nights 113 to 124, 877 of 878 `tests.encode` rows read a criterion that the night holds. The other row read an id that the night does not hold. One criterion id of the 12 nights has 45 characters, and its encodes would not read (observed: a count with `_encoded_criterion`, 2026-10-05). The body comes first in the summary and is cut at 60 characters too. A body that holds `, criterion_id='x', ` would make two matches, and the rule then does not fire.

## The new and changed sentences

The cap, when a counted prior holds other refs than this call:

- `you sent challenge to tester on c1 or a test of c1 3 times already (m1, m2, m3), and the test changed and is still red. Send msg.escalate_architect on the same refs.`
- The same with `, and the criterion changed and the test is still red.`, with `.` alone, and with the step `Make one real change to the code the test calls.` or `End the session with no call.`

For a test with no criterion, pass 3's form stays: `you sent challenge to tester with tst0 in the refs 3 times already (x1, x2, x3), ...`. When every counted prior holds the call's set of refs, the cap keeps `on exactly these refs`.

No other sentence changed. With a repeated ref, the offer's refs and the escalation check lose the repeat, so a sentence can now name the code step where it named the escalation (X6).

## Proof 1: the chains

Each round goes through `Sandbox.call`. The Tester's turn is a real `tests.encode` and a `session_commit`, and the harness records a failing run (observed: the tests, 2026-10-05).

- `test_a_tester_that_stores_a_new_test_id_each_round_meets_the_cap` (`test_desk_guards.py:1474`): the refs are `[c1, the newest test of c1]`, and the Tester stores `tstn1`, `tstn2`, `tstn3`. Rounds 1 to 3 land. Round 4, on `[c1, tstn3]`, is refused.
- `test_one_criterion_against_each_test_of_the_batch_meets_the_cap` (`:1488`), on batches of two and three tests: `[c1, tst1]`, `[c1, tst2]`, then `[c1, tst3]` or a new list. Round 4 is refused.

The reviewer's chains on the repair: `test_C` 8 of 8 and `test_D` 2 of 2 stop at round 4. `test_E` ends every one of its 24 chains at round 2, 3 or 4.

The reviewer's `test_F` with a new-id Tester: `p5_mix_newid.py` in `f132p3` replaces `other_refused+judges` with a Tester that stores a new test id of c1, and the Developer names c1 and the newest test of c1. Over 1875 mixes of 8 rounds, the landed counts are 125 at 1, 275 at 2 and 1475 at 3. **The highest is 3.** No chain passed the cap (observed: 2026-10-05, 433 s).

## Proof 2: the replays

- The 144 recorded refusals, the reviewer's `p4b_replay.py` on this tree: 138 admitted and 6 refused. The 6 are night 118's m104 (5) and night 121's m131 (1), all true repeats. The state check picks the cited prior in 144 of 144.
- The 308 recorded Developer `msg.challenge_tester` calls, the reviewer's `p2b_worker.py` on this tree against `p2b_old.json`: 287 admitted before and after, 14 refused before and admitted now, and 7 true repeats before and after. **0 newly refused**, and no refusal changed its text.

## Proof 3: the reviewer's states

`p3_states.py` and `p3b_escalate_chain.py` on this tree (observed: 2026-10-05):

- X1 and X2: a refused encode of tst2 and an answer on tst1 is a judgement now. X1's own set-up asserts that its second challenge lands, so the probe now fails at that assert. That is the repair.
- **X3, an accepted encode of the stored body with no receipt, and an answer: the door admits the re-send** (`{'id': 'm4', ...}`). The encode names c1, and no `tests` receipt exists, so the rule fires. Two such priors would meet the bound's new form, which says `The Tester sent changes to the test, and none landed.` The Tester sent the same body, so "changes" is not true there. No rule was added, as the brief says.
- X4: `on c1 or a test of c1 3 times already (m1, m2, m3).` The criterion form is gone.
- X6: with a repeated ref after a closed escalation, the cap now names the code step and records no offer. The added-ref list still offers and lands the escalation.
- X8: the probe fails in its own set-up, because the evidence door refuses its quote of tst2 after tst2 moved. That is outside the door.
- `p3b_escalate_chain.py`: with a repeated ref, 1 escalation lands, against 12 before. With an added ref each round, 7 land until the evidence of an unknown ref stops the probe. That chain is the escalation door's own, which this pass leaves.

## Proof 4: the mutants

`mutp4.py` in `f132p3`, on the door's 143 tests. With no mutant, they pass.

The review's rows that still apply, each now red: M27 1, M28 1, M25 1, M26 1, M03 1, M04 1, M05 1, M07 1, M08 3, M10 1, M11 1, M18 1, M20 1, M20b (the priors' refs) 1, M22 3, M23 1, M24 1, M31 1.

This pass's lines, each now red: N01 3, N02 3, N03 1, N04 1, N05 1, N06 1, N07 2, N09 1, N10 4, N12 12, N13 1, N14 1, N15 1, N16 1, N17 1, N18 5, N19 1, N20 1, N22 20.

Green, each argued equivalent (reasoned):

- M12, the cap's guard without the keys term. Same-refs rows name the same keys, so 3 such rows put a key at the cap first.
- N08, keys not deduplicated. A repeated key counts the same rows twice and gives the same answer.
- N11, a test key also matched through a test's criterion. No test has a criterion id equal to a test id with no criterion.
- N21, the regex without the lookahead. A cut id has no closing quote, so `[^']*` runs into `, id=`, and that is no criterion.
- N23, a prior whose refs are not a list fires the rule. Such a prior is never a same-refs row.

## The recorded cases

No recorded prompt holds a changed sentence (reasoned). The criterion form needs three challenges on one criterion over different refs lists. No case file holds a `tool_calls` row (observed: pass 3's grep). The gate's stale line reads 0, so no re-record ran.

## The suite

`tests/rota/test_desk_guards.py`, `test_offers_followed.py` and `test_t0_sandbox.py`: 397 passed and 6 xfailed (observed: 2026-10-05).

The gate from the worktree, on the working tree before the commit, with pass 3's copies of the register and the baseline (observed: `python -m rota.tools.gate`, 2026-10-05, 615.4 s):

```
suite: 23 failed, 2803 passed, 30 skipped, 7 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 615.4s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that frame 148 holds.

## Deviations from the brief

1. The sentence names the criterion as `on c1 or a test of c1`. A prior can name only a test of c1 and not c1, so `with c1 in the refs` would be false.
2. A test with no criterion keeps a count of its own. The schema allows a NULL `criterion_id`, and the criterion count cannot see such a test. So one count stands per key, and the key is the criterion or that test.
3. The rule for refused encodes reads the receipts of `tests` on any row, as before. The brief asks to match only the encode.
4. Several tests call `_same_refs_refusal` directly, because the evidence door reads the quotes against the first test of the refs.
5. The `test_F` run replaces one Tester kind with the new-id Tester, so it stays at 1875 mixes.

## Seen and not fixed

- The open challenge on another refs list (the review's finding 6) counts toward the cap and makes no new list wait.
- The escalation door compares a sorted list. A Developer at the cap with an added ref each round lands an escalation each round, 7 in the reviewer's probe.
- X3: an encode of the stored body with no receipt fires the rule. The bound's new form then says `The Tester sent changes to the test` of a Tester that sent no change.
- The evidence door reads only the first criterion and the first test of the refs.
- Pass 1's to 3's items stand: the Critic's kept sentence, the `SyntaxWarning` for `"\["`, and the skip count of 30 against 27.
