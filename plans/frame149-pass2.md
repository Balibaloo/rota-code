# Frame 149, pass 2: the revert door admits a repair per test

Meta workflow. Pass 2 of frame 149, "the revert door says the tests pass both ways and refuses the repair of a head that fails at import". The implementing agent on Opus wrote this record on 2026-10-06, in the worktree `C:/Users/roman/rota_f149` on the branch `f149`. The code commit is 8636b6f. A previous agent started this pass and was stopped. This agent continued from the uncommitted edits in the worktree. The probes called no model.

The pass repairs the findings of the diff review of 9278be2: 1 medium and 4 lows. The probes are in the scratch area of session 2ba331e1, in `f149p2`. They are copies of the reviewer's probes in `review149`, carried to the new rule.

## 1. The rule (finding 1, medium)

**The door admits a revert only when going back turns no test red and at least one test green.** (observed: `tests/rota/test_revert_door.py`, 2026-10-06)

The door takes the tests that ran at `HEAD` and at `HEAD~1`. A test turns red when it passes at `HEAD` and does not pass at `HEAD~1`. A test turns green when it does not pass at `HEAD` and passes at `HEAD~1`. `error` counts as red on both sides.

A refusal with a test that turns red names the test: "Going back turns 1 test red that passes at the head: tst1." It names at most 5 tests and the count of the rest.

The review's built states under the new rule (observed: `f149p2/states.py`, 2026-10-06):

- `unrelated_two_red_at_head`: refused. The refusal names t1, the test that the head fixed.
- `flaky_one`: admitted. The brief's rule admits it. At `HEAD~1` every test passes. At `HEAD` one project test fails, and no test passes at `HEAD` that fails at `HEAD~1`. So going back turns p3 green and turns no test red. The door cannot tell a flaky run from a regression, because each sha holds one run per test. Section 6 names this.

## 2. The 46 night pairs and the 14 refusals

**Under the new rule the door admits 7 of 46 night pairs, the same 7 that the net count admits.** (observed: `f149p2/pairs2.py`, nights 113 to 125, 2026-10-06)

The script reads every commit with runs, and the runs of its parent in the same batch. 92 commits have runs. 46 of them have runs at the parent too. Of the 46 pairs, both rules admit 7 and both rules refuse 39. At each of the 7, going back turns 0 tests red. The 7 are nights 113, 114, 119, 120, 121, 123 and 124, one pair each.

**The replay of the 14 real refusals admits the 3 of night 124 and refuses the 11.** (observed: `f149p2/replay14.py`, 2026-10-06)

- Night 124, s144 turns 13 and 14 and s145 turn 22: admitted.
- Night 120, 2 refusals: "the head fails 43 and cfed9d8e5d fails 43".
- Night 121, 2 refusals: "Of the 36 tests that ran at both, the head fails 2 and 2aece0a4a8 fails 2".
- Night 123, 7 refusals: "Of the 37 tests that ran at both, the head fails 2 and 73b1ea60ae fails 2".

Each of the 11 says "Going back makes no test pass that fails at the head", then names `msg.escalate_architect` with refs. One call, night 121 s152 turn 5, holds a fake sha in its result, and the replay skips it as pass 1's did.

## 3. The facts (findings 3 and 4)

- A `runs` fact at a name that git cannot resolve now reads false, with the name in the reason: "git resolves no commit at HEAD~5". Before, `None` equal to `None` read true.
- The sentence "Of the N tests that ran at both, the head fails X and <sha> fails Y" now records a fact `both` with `(N, X, Y)`. The sentence "Going back turns K tests red" records a fact `turns_red` with the test ids. `sandbox._both_hold` computes both again from the stored runs of the two shas. The fact check reads the rows through `_stored_runs`, not through the door's reader.

Over the four touched and nearby test files, the revert door recorded 31 facts: `runs` 20, `both` 7 and `turns_red` 4. All 31 read true (observed: `ROTA_OFFER_LOG`, 2026-10-06).

## 4. The step where the head has no red run (finding 5)

The old step was "Say what stands and why (a decision), challenge the test (msg.challenge_tester) or escalate the criterion (msg.escalate_architect); do not flip". It named two calls with no refs and no `_offer` record. The new step is "Say what stands and why (a decision), and do not flip." Then the door tries each red test of `HEAD~1` in order. It names `msg.challenge_tester(refs=[<criterion>, <test>])` through `_offer` on the first test that `_challenge_admitted` passes. Where no test passes, the step names no call.

Where both commits pass, the refusal keeps the old sentence to the byte up to its step: "this commit puts the tree back where it stood before your last commit: you are undoing yourself. The tests pass both ways, so the disagreement is not in the code. Say what stands and why (a decision)". Only the step after it changed. No test is red there, so the step names no call.

Frame 144's follow check sent the 3 offers that the revert door tests made: `msg.escalate_architect` once and `msg.challenge_tester` twice. Each passed its doors, with no second refusal (observed: `ROTA_OFFER_LOG`, 2026-10-06).

Where the seat sent the escalation this session, the refusal still ends at "Do not flip." and names no call. That is the rule "else name no call", and `test_an_escalation_sent_this_session_is_not_named_again` holds it.

## 5. The mutants (finding 2)

**20 of 21 mutants fail at least one test. m6 survives.** (observed: `f149p2/mutants2.py`, 2026-10-06)

The review's 16 mutants are carried to the new rule where their line moved. m1 to m5 now mutate the rule's per-test lines. m14 adds 1 to N in the `both` fact. 4 mutants are new: m17 names the challenge with no door, m18 tries the first red test only, m19 reads every `both` fact as true, and m20 reads a `sha` of `None` as true. The parent of 9278be2 fails all 14 tests.

The 8 surviving mutants of the review that this pass meets with a test:

| Mutant | Test that fails |
|---|---|
| m3, a red test outside both stops the repair | `test_a_red_test_outside_both_does_not_stop_the_repair`, `test_the_count_at_the_tree_put_back_reads_only_the_tests_at_both` |
| m5, `error` at `HEAD~1` does not count as red | `test_a_test_that_errors_at_the_tree_put_back_turns_red_too` |
| m7, `_runs_at` reads every batch | `test_the_runs_of_another_batch_at_the_sha_are_not_read` |
| m9, the count at `HEAD~1` reads every run | `test_the_count_at_the_tree_put_back_reads_only_the_tests_at_both` |
| m12, `_runs_hold` checks no sha | `test_the_facts_of_a_name_git_cannot_resolve_or_a_wrong_count_read_false` |
| m13, the old sentence on a commit with no run | `test_a_commit_with_no_run_does_not_get_the_old_sentence` |
| m15, the escalation is named with no door | `test_an_escalation_sent_this_session_is_not_named_again`, `test_the_count_at_the_tree_put_back_reads_only_the_tests_at_both` |
| m16, `_runs_hold` reads every batch | `test_the_runs_of_another_batch_at_the_sha_are_not_read` |

m6 reverses the order of the rows at one sha. It stays green, and no test can make it fail in a real night. The harness deletes the rows of the batch at a sha before it runs the tests there again, so each test holds one row per sha (observed: `rota/core/harness.py` line 117, 2026-10-06).

## 6. Seen and not fixed

- Finding 6. The first run of every night is at the first Developer commit of the batch, never at the base. A first commit that fails at import, then a repair back to the base, meets "No run is stored at <base>" and is refused. No night of 113 to 125 holds that case.
- `flaky_one` (section 1). One red run at the head after a green `HEAD~1` admits the revert. The rule cannot tell a flaky run from a regression.
- Where the head has no run and `HEAD~1` has red runs, the head has no red run. So the step names the challenge on a red test of `HEAD~1` (observed: `states.py`, the state "A again, no run at the revert yet", 2026-10-06). The doors admit that challenge.
- Night 123's 7 refused commits hold a tree that the seat did not write, as pass 1 said. This pass does not touch that.

## 7. What changed

- `rota/roles/api.py`: `_revert_refusal` uses the per-test rule, names the tests that turn red, records the `both` and `turns_red` facts, and names the challenge through `_offer`. `_REVERT_OLD_STEPS` is gone.
- `rota/core/sandbox.py`: `_challenge_admitted`, `_stored_runs` and `_both_hold` are new. `_runs_hold` returns false when git resolves no commit. `check_facts` checks the kinds `both` and `turns_red`.
- `tests/rota/test_revert_door.py`: 10 new tests and 2 changed tests, 14 in all. The test of the old sentence now holds the old bytes up to the step and the new step.

## 8. The suite

The touched and nearby files pass: `test_revert_door.py`, `test_desk_guards.py`, `test_offers_followed.py` and `test_t0_sandbox.py`, 430 passed and 7 xfailed (observed: 2026-10-06).

The gate on the final tree, uncommitted on 5ca822b, then committed as 8636b6f with no change (observed: `python -m rota.tools.gate` in the worktree, 2026-10-06):

```
suite: 23 failed, 2838 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 1560.3s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 3 new reds and the 3 reds gone are the same lists as pass 1's gate (copied: `plans/frame149-pass1.md`, section 7). None of the 3 touches the revert door. The stale count is 0, so no case needed a new recording.
