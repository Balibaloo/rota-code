# Frame 360, the false claim, the review of pass 1 (commit 8d384ed6)

**Verdict: fix before the pick.** The wake detail and the predicate are right for every state that writes `claimed_head`. But the encode door contradicts the new paragraph at the moment that F targets, and two Tester modes never see the claim. Findings: 1 high, 3 medium, 2 low.

## (a) The points

1. **Who gets the detail: holds for `tests_missing`, misses two other Tester wakes.** No batch that is not a claim gets the detail. The `answer` and `challenge` wakes of a claimed batch carry no claim word (finding 2).
2. **The red test on a claim: the loop runs, and nothing in it knows the claim.** `tests_failing` wakes the Developer with `attempt 1` only. A re-claim lands no write and repeats the same wake (finding 3). The encode door asks the Tester to re-encode a red test (finding 1). The challenge mode can replace it, and no door sees the claim (finding 2).
3. **A wrong red test: the same loop as a change batch, with one extra push to keep the wrong test.** The principal reads the Done line or a park ask, as on a change batch (finding 6).
4. **The words: two conflicts.** The encode door note conflicts with "Do not change a test so that it passes" (finding 1). "A test that fails ... shows that the claim is false" is not true for a wrong test (finding 6).
5. **The tests can fail: yes, all 4.** Six planted faults turn each test red at least once (probe 1).
6. **The replay probe: the prompt is right, the verdict is not.** Its verdict counts a broken test as a disproof (finding 4). Sample 1 is the only sample at the run's temperature (finding 5).

### Point 1, the states

- Before the first Developer session: `head_commit` is NULL and `claimed_head` is NULL, so `_claimed_batches` excludes the batch. `tests_missing` also needs a head.
- A claim: only `code_commit`, `rota/roles/api.py` 26439 to 26442, writes `claimed_head`, and only when `head_commit` is empty.
- After a real commit: api.py 26458 to 26463 clears `claimed_head`. No detail. The pass's test 3 shows it.
- A hand commit, a reset to the fork, a restart: `reconcile_worktrees`, `rota/core/boot.py` 168 to 180, moves the claim only over a furniture commit. A code commit leaves the claim unequal to the head. A head moved back after a real commit has a NULL claim. No detail in each case.
- A second `tests_missing` wake: the detail holds while the head is the claim. Tests are not committed before the merge, so the head stays.
- Other wakes that ask the Tester for tests: `answer` mode encodes tests and `challenge` mode replaces them. `CLAIM_DETAIL` has one reader, `tests_missing` (search over `rota/`). Neither `answer.md` nor `challenge.md` holds the paragraph.

### Point 5, the planted faults

All faults went into an archive copy of 8d384ed6. The probe restored each file and checked it by sha256.

| Fault | Where | Red |
|---|---|---|
| never_told | predicates.py, the condition is False | tests 1, 3, 4 |
| always_told | predicates.py, the condition is True | test 2 |
| not_null_only | `_claimed_batches` without the equality | test 2 |
| commit_keeps_claim | api.py 26461 keeps the claim | test 3 |
| failing_skips_claim | `tests_failing` drops claimed batches | test 3 |
| no_claimed_line | principal.py 364, the claimed count is 0 | test 4 |

## (b) Findings

1. **High. On a claimed batch, the encode door tells the Tester that the head holds the Developer's commit, and it offers a re-encode of the red test.** `rota/roles/api.py` 23474 to 23510, `_arrange_run_refusal`. `_developer_committed`, api.py 23074, is true on a claim, because the claim is a Developer receipt on the batch row. CONFIRMED (probe 3): a test red at the fork got "The test is stored. The batch's head holds the Developer's commit. If the criterion's words give the value that the run shows, the test is wrong. Encode it again with the same id." The first sentence is false on a claim. The note sets `encode_noted`, so a same-id re-encode lands. The note reaches the s153 replay too, so the replay measures F against this note. Fix: on a batch whose `claimed_head` equals `head_commit`, say "The head is the fork. No code changed." and keep the test when the criterion's words give a value other than the run's.
2. **Medium. The `challenge` and `answer` wakes of a claimed batch carry no claim, and a challenge can replace the disproving test.** `rota/core/predicates.py` 1013 to 1017 is the only reader of `CLAIM_DETAIL`. `rota/roles/prompts/tester/challenge.md` says "If they are right, fix the test". The Developer who claimed will most likely challenge the red test. CONFIRMED (probe 2): with the `challenge.tools` set, a same-id `tests.encode` of a new body landed on the claimed batch, and no door named the claim. With the replaced test green, the merge page shows "No code changed. These tests show the code already does this." Fix: add `CLAIM_DETAIL` to every Tester wake on a claimed batch, and add one claim sentence to `challenge.md` and `answer.md`.
3. **Medium. On `tests_failing`, a no-change `code.commit` tells the Developer to say that the criteria are met and to end, against a red test.** api.py 26449 to 26454. CONFIRMED (probe 2): the note says "If the criteria are already met, say so in your reply and end the session". The row did not change, and the wake came back as `('tick:tests_failing', 'attempt 1')`, the same key. PLAUSIBLE: only the barren guard of the loop, `rota/core/loop.py` 680 to 690, ends the repeat, as a stuck wake. The principal then reads a stop, with no word that a test disproved the claim. Fix: on a claimed head with a red criterion test, the note says that a test fails on the code as it is, and names `code.write` or `msg.challenge_tester`.
4. **Medium. The replay verdict counts any non-zero pytest exit as a test that fails at the fork.** `p360c/replay_s153.py` 124 to 135. CONFIRMED (probe 4): an import error, a file with no test and a raise in the arrange step each gave `fails`. The probe has no right-code control. A c3 test that fails on every code also counts, and the read says that c1 and c3 of run 1 contradict. Fix: count a hit only for an assertion failure at the fork that passes on a reference fold fix, and print the failure kind.
5. **Low. The replay target mixes the temperature of the run with a sampled temperature.** replay_s153.py 149 to 150. Sample 1 runs at temperature 0 with seed None, as s153 did. Only sample 1 can show what the run does with the new prompt, and its expect block still differs, as the report says. Samples 2 to 5 at 0.6 show what the model can reach, not what the run does. "At least 1 of 5" can pass on samples 2 to 5 alone. PLAUSIBLE, from the pins of the dry run (probe 5). Fix: report sample 1 apart as the result of the run, and report samples 2 to 5 as reach.
6. **Low. The sentences "A test that fails on the code as it is shows that the claim is false. That is a right result, not a fault of your test." are false for a wrong test.** `rota/roles/prompts/tester/tests_missing.md` 29 to 30. On a true claim, a wrong red test wakes the Developer. The Developer then challenges, or changes right code to fit the wrong test. In the second case the principal reads "Done: 1 change built, tested and merged." That is the path of a change batch today. The paragraph only adds weight to keep the wrong test at encode. PLAUSIBLE, from the briefs and probe 2. Fix: "A test that fails on the criterion's value on the code as it is shows that the claim is false."

Outside the points: nothing more that changes a run. The base brief line "You write before the implementation exists" is false on every `tests_missing` wake, because the predicate waits for a head. That line is older than this commit.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/rv360/`. The folder `tree/` holds a `git archive` of 8d384ed6. No tracked file changed.

1. `plant.py`, output `plant.out`. It plants six faults in `tree/` and runs the 4 new tests for each fault. Each fault turns a test red. Each file came back byte for byte.
2. `tree/tests/rota/test_rv360_probe.py`, output `probe_p2.out` and `probe_p2b.out`. On the `world` fixture it makes a claim, a red run, a no-change Developer commit and a same-id Tester encode with `challenge.tools`. Then it records a pass by hand and merges.
3. `tree/tests/rota/test_rv360_note.py`, output `probe_note.out`. On a claim it encodes a test that fails on its assertion at the fork, and it prints the door note.
4. `verdict_probe.py`, output `verdict_probe.out`. It calls the `run_test` of the replay on four bodies in the dry clone.
5. `replay_s153.py --dry --out rv360/dry`, output `dry.out` and `dry/results.json`. It ran from `C:/Users/roman/rota_r362o`. The prompt holds the claim detail and the paragraph. The pins are temperature 0.0 and seed None. Nothing committed.

## (d) Usage

No meter is available. Estimate: about 90k context at the end, about 1.3M input tokens over all turns, about 15k output tokens, about 1.3M in total.
