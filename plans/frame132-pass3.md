# Frames 132 and 145, pass 3: the cap counts per test, and refused encodes are no judgement

Meta workflow. Pass 3 of frame 132 and frame 145, on the delta review of b2ed55b. A fresh implementing agent on Opus wrote this record on 2026-10-05. The code and the tests are commit 4de1555, on top of 6d084cf, on the branch `f132p3`. Every line below is cited at 4de1555.

## The count that keeps the cap

`count_per_test.py` in the scratch folder `f132p3` of session 3f72d9cb reads the reviewer's copies of nights 113 to 124, read-only. A test counts a challenge when the Developer's challenge to the Tester holds the test's id in its refs, whatever the other refs. A test ends green when its newest `test_runs` row is `pass`, or its batch reads `merged` (observed: 2026-10-05).

| Landed challenges per test | Tests | Green |
|---|---|---|
| 1 | 38 | 14 |
| 2 | 3 | 0 |

- The three tests with 2 are night 117's `inh_echo_json_01`, `_02` and `_03`. Each has one challenge of its own and m79, which names all three. None ended green.
- The longest chain on a test that ended green is 1.

So a cap of 3 refuses no challenge that led to green. The cap stays at 3: one above the longest green chain is 2, and the ruling's floor is 3 (`LANDED_CHALLENGES`, `sandbox.py:1094`).

## The items

1. **HIGH, the cap per list: fixed.** `_challenge_cap_refusal` (`sandbox.py:1128`) counts per test id with `_challenges_naming` (`:1108`). Every Developer challenge to the Tester whose refs hold the test id counts. A challenge that names several tests is refused when any test is at the cap. The cap now also runs where no prior holds the same refs (`_challenge_repeat_refusal`, `:1230`, the first branch), because a new refs list had no prior and so met no cap. For this door only, `_same_refs_rows` (`:963`) compares the refs as a set (`:1320`), so a repeated ref is the same refs. Refs that name no test keep the count of the same refs.
2. **LOW, "the test changed": fixed.** The cap says `the test changed` only on a `tests` receipt on the test, since the wake of a counted prior. A `criteria` receipt alone gives the new criterion form. `_receipt_since_woken` (`:1052`) reads the receipts of the named tables, and `_moved_since_woken` calls it with both tables.
3. **LOW, seven surviving mutants: fixed.** Each now turns at least one test red. The table is in proof 3.
4. **The new rule: built.** `_encodes_refused` (`:1196`) is true when the Tester sessions that the prior woke hold a `tool_calls` row with `fn = 'tests.encode'` and no `receipts` row of `tests`. `_tester_judged` (`:1219`) then returns no answer. The door uses it at the true-repeat branch and in the count, so such a prior is unanswered and the bound of 2 applies. No text is parsed, and the encode is not matched to a ref.

## The new sentences

The cap, when a counted prior holds other refs than this call, oldest first:

- `you sent challenge to tester with tst1 in the refs 3 times already (m1, m2, m3), and the test changed and is still red. Send msg.escalate_architect on the same refs.`
- The short form, with no change or no red run: `you sent challenge to tester with tst1 in the refs 3 times already (m1, m2, m3). Send msg.escalate_architect on the same refs.`

When every counted prior holds the same set of refs, the cap keeps `on exactly these refs`, and pass 2's sentences keep their bytes.

The cap, when only the criterion moved:

- `you sent challenge to tester on exactly these refs 3 times already (m1, m2, m3), and the criterion changed and the test is still red. Send msg.escalate_architect on the same refs.`

The bound, when a counted prior holds the Tester's answer row after refused encodes:

- `you sent challenge to tester on exactly these refs already (m64, then m66), and the test did not change. The Tester sent changes to the test, and none landed. Send msg.escalate_architect on the same refs.`
- With the escalation refused: `... and none landed. End the session with no call.`

Each form that names `msg.escalate_architect` records it as an offer, and the second step is `_code_step` or `End the session with no call.` as before. The true-repeat, waiting, Critic and escalation sentences did not change.

## What ends each chain

The chains of `test_a_chain_on_one_test_stops_at_the_cap_whatever_the_other_refs` (`test_desk_guards.py:1256`) and `test_the_bound_and_the_true_repeat_end_their_chains_whatever_the_refs` (`:1287`). Each round runs through `Sandbox.call`, and `_chain` (`:1140`) then plays the Tester (observed: the tests, 2026-10-05).

| The Tester each round | Repeated ref, `['c1'] * i + ['tst1']` | Added ref, `g1`, `tk1`, `b1` in turn |
|---|---|---|
| Moves the test: a real `tests.encode`, `session_commit`, a failing run | the cap, round 4 | the cap, round 4 |
| Moves the criterion only | the cap, round 4, the criterion form | not run |
| Barren: a woken session, no answer | the bound, round 3 | the cap, round 4 |
| Judges: an answer row | the true repeat, round 2 | the cap, round 4 |

The moved chain runs on a batch of one test and of two. A repeated ref meets the bound and the true repeat, because the door compares sets. An added ref escapes both, because they read the newest prior on the same refs, and the cap per test ends the chain at round 4.

The reviewer's `p6c_loop.py`, run on the real door with no patch: three Testers with refused encodes and an answer meet the bound at round 3. The pattern of moves, refused, refused meets the bound at round 4. Both refusals use the new form and record the offer (observed: `f132p3/loop`, 2026-10-05).

## Proof 1: the replay of 144 refusals

`replay3.py` in `f132p3` is pass 2's `replay2.Night` on the reviewer's copies, with the real door of the worktree and no patch. It runs the 141 refusals of `classes.tsv` and night 124's 3 (observed: 2026-10-05).

| Class | Refusals | Admitted | Refused |
|---|---|---|---|
| a1 | 16 | 16 | 0 |
| a2 | 43 | 43 | 0 |
| b | 66 | 66 | 0 |
| c | 16 | 10 | 6 |
| night 124 | 3 | 3 | 0 |
| All | 144 | 138 | 6 |

These are the review's numbers for rule (b): 138 admitted and 6 refused, 10 of 16 true repeats changed, and 3 of 3 on night 124. The 10 are night 114's m64 (7) and night 117's m68 (3). The 6 refused are night 118's m104 (5, true repeat, escalation named) and night 121's m131 (1, true repeat, code step). The state check holds: the old loop picks the cited prior in 144 of 144 runs. The cap and the set match change no answer on these nights.

## Proof 2: the night 124 tests

- `test_night124_an_answer_after_refused_encodes_admits_one_resend` (`:1405`): s144's turn-9 call on m64, m65 and s141 with 4 `tests.encode` rows. Admitted as m66.
- `test_night124_the_third_challenge_meets_the_bound_with_the_refused_encodes` (`:1411`): a second prior m66 with refused encodes and the answer m67. The third call meets the new form. The offer is recorded, and the named escalation lands.
- `test_night124_a_tester_that_sent_no_encode_and_answered_judged` (`:1443`): the same state with no encode. The true repeat refuses with `(m64) and they answered (m65)`.
- `test_an_answer_after_an_encode_that_stored_a_test_is_a_judgement` (`:1431`): an encode that stored a test outside the refs. The answer stays a judgement.

## Proof 3: the mutants

`mutp3.py` in `f132p3` execs a changed copy of `sandbox.py`. Each run is `test_desk_guards.py` with the door's 102 tests selected. With no mutant, 102 pass (observed: 2026-10-05).

| Mutant | Change | Red tests |
|---|---|---|
| A2 | the move reads `tests` only | 2 |
| A5 | the move also reads `glossary_terms` | 1 |
| B3 | `MAX` for `MIN` of the wake's seq | 1 |
| D8 | `error` is not red | 1 |
| D9 | the oldest run decides | 1 |
| D13 | "changed" reads the newest prior only | 1 |
| D14 | "changed" reads the oldest prior only | 1 |
| P1 | no cap where no prior holds the same refs | 5 |
| P2 | the rows match as a sorted list | 2 |
| P3 | the cap per test never fires | 16 |
| P4 | rule (b) is off | 2 |
| P5 | rule (b) ignores the `tests` receipt | 1 |
| P6 | the new bound form is off | 1 |
| P7 | the criterion form is off | 1 |
| P8 | the count reads every answer as a judgement | 1 |

All 15 turn at least one test red. The tests that turn the review's seven: `test_a_criteria_receipt_since_the_wake_is_a_move` (`:1359`), `test_a_receipt_of_another_table_is_no_move[glossary_terms]` (`:1048`), `test_a_move_after_the_first_of_two_wakes_counts` (`:1366`), `test_the_cap_reads_an_error_as_red` (`:1322`), `test_the_cap_reads_the_newest_run_and_a_pass_after_a_fail_is_not_red` (`:1329`) and `test_the_cap_reads_a_change_at_a_middle_prior` (`:1340`).

## The recorded cases

No recorded prompt holds a changed sentence (reasoned). The new forms need three challenges on one test, or a Tester session with a `tests.encode` row and no `tests` receipt. No case file holds a `tool_calls` row (observed: grep of `tests/rota/cases`, 2026-10-05). The one case that meets the door, `L1-DV-act-on-an-answered-challenge`, holds one prior, so it meets the unchanged true-repeat sentence. The gate's stale line reads 0, so no re-record ran.

## The suite

`tests/rota/test_desk_guards.py`, `test_offers_followed.py` and `test_t0_sandbox.py`: 373 passed and 6 xfailed (observed: 2026-10-05).

The gate from the worktree, on the working tree before the commit (observed: `python -m rota.tools.gate`, 2026-10-05, 663.1 s). The worktree holds a backup copy of the register and a copy of `.rota-gate.json`, both from `D:/repos/rota`, read-only:

```
suite: 23 failed, 2779 passed, 30 skipped, 7 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 663.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that frame 148 holds. The gate also printed `main card: held by qwen3:8b ..., re-records wait`. No case was stale, so no re-record waited.

## Deviations from the brief

1. The cap names the test when a counted prior holds other refs: `with tst1 in the refs`. "On exactly these refs" is then false (reasoned: frame 144's rule that a refusal's facts are true). When all counted priors hold the same set, pass 2's bytes stay.
2. Refs that name no row of `tests` keep pass 2's count on the same refs. The brief does not say what such a challenge counts.
3. Rule (b) reads every Tester session that the prior woke, as one set, as the reviewer's `p6c_loop.py` does. The brief says "the Tester session". On nights 113 to 124, each of the 42 Developer challenges to the Tester woke exactly one Tester session, so the two readings give the same numbers (observed: a count on the copies, 2026-10-05).
4. The new bound form is true for both refused and mixed states: it fires when any counted prior holds the Tester's answer row. It says `none landed`, not `were refused both times`, because a barren prior beside a refused one makes "both times" false, and the rows show no refusal, only no receipt.
5. `test_a_challenge_of_several_tests_stops_when_one_is_at_the_cap` calls `_same_refs_refusal` directly. Through `Sandbox.call`, the evidence door reads the quotes against the first test of the refs and refused first.
6. The gate ran in the worktree on copies of the register and of the baseline file, so that no run wrote in `D:/repos/rota`. The copied register is not tracked.

## Seen and not fixed

- The suite's skip count is 30, against 27 in pass 2's gate. The gate does not list skips, and this pass added no skip.
- An open challenge on another refs list with the same test counts toward the cap, and it does not make a new list wait. The waiting sentence reads the same set of refs only.
- The evidence door matches the quotes against the first criterion and the first test of the refs. A challenge that names two tests cannot quote the second.
- Pass 1's and pass 2's items stand: the Critic's kept sentence names a call that the Critic does not hold, and `test_desk_guards.py` prints a `SyntaxWarning` for `"\["`.
