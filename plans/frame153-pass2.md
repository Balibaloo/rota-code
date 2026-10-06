# Frame 153, pass 2: the flag clears at each answer, and frame 152's five lows

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-06, on branch `f153` from eee7fbc, in the worktree `C:/Users/roman/rota_f153`. The code and the tests are in 7fb40f2. A stopped implementer started this pass. Its uncommitted edits held the code of items 1, 3, 4 and 5 and the fixture of item 6. This pass kept those edits and wrote every test. The scripts are in the scratch area of session 2ba331e1, folder `f153/`: `mutate_p2.py`, `mutate3_p2.py`, `runs_p2.py`, `replay_p2.py`, `cmp_p2.py`.

## Frame 153

### 1. A call that lands clears the flag (MED)

The rule: `told_to_end` is true only while the newest answer to any call is the refusal with the step `End the session with no call.`.

- `rota/core/runner.py`, the OK branch of `sb.call`. The flag is false after the call runs.
- The held path. A held call that runs clears the flag. A held call that is refused sets the flag from its class.
- The two resets in the repeat refusals are gone. Both branches sit after a call that ran, so the new reset covers them.

The test `test_a_write_after_the_step_brings_the_nudge_back` is case C2: the step, then a `code.write` that lands, then prose. The session gets the owed-call nudge, as on the parent. Without the reset it ends after 3 model calls with the write uncommitted.

### 2. The tests of the held path, the resets and mode `exhausted` (LOW)

`tests/rota/test_end_step_nudge.py` now holds 11 tests. The 8 new tests:

| Test | The shape | What it holds |
|---|---|---|
| `test_a_write_after_the_step_brings_the_nudge_back` | C2 | the reset after a call that lands |
| `test_a_held_challenge_that_meets_the_step_ends` | C5: a fresh read holds the challenge | a held refusal with the step sets the flag |
| `test_a_held_write_after_the_held_step_brings_the_nudge_back` | the read, the challenge and a write, held | a held call that lands clears the flag |
| `test_a_call_error_after_the_step_brings_the_nudge_back`, 2 parameters | the step, then `criteria.load(batch_id=)` or a `tests.encode` from the Developer | the parser's reset and the argument check's reset |
| `test_a_session_with_no_refusal_gets_the_nudge` | prose first | the flag starts false |
| `test_mode_exhausted_ends_on_the_code_step` | `tick:exhausted`, a challenge that the Tester answered | `_code_step` gives the step to end, and the session ends |
| `test_the_step_toward_the_code_keeps_the_nudge` | the same state on `tick:tests_failing` | "Make one real change to the code the test calls." is no end |

The parser does not refuse `TOOL: criteria.load`. It reads the call as `criteria.load()`, which runs. So the parser's case uses an argument with no value.

### The mutants of `mutate.py`

`mutate_p2.py` is the reviewer's `mutate.py` on the worktree. It restores the bytes after each mutant (observed: 2026-10-06). M7 of the review removed the resets of the repeat refusals, and those lines are gone. M7 now removes the reset after a call that lands. M4b and M9 are new.

| Mutant | Result |
|---|---|
| M1 the condition loses `and not told_to_end` | red, 5 |
| M2 the door raises `ValueError` always | red, 5 |
| M3 a later refusal keeps the flag | red, 1 |
| M4 a held refusal with the step never sets the flag | red, 1 |
| M4b a held call that lands keeps the flag | red, 1 |
| M5 a parser error keeps the flag | red, 1 |
| M6 an argument error keeps the flag | red, 1 |
| M7 a call that lands keeps the flag | red, 1 |
| M8 every step becomes `_Ending` | red, 1 |
| M9 `_code_step` never ends | red, 1 |
| M10 any refusal sets the flag | red, 3 |
| M11 the flag starts true | red, 1 |
| M12 the condition is inverted | red, 11 |
| M13 the ending text gains a byte | red, 3 |
| M14 `EndRefusal` is not a `ValueError` | green in this file |

14 of 15 turn red. M14 turns red in `tests/rota/test_desk_guards.py`, 3 tests: those tests catch the door's refusal as `ValueError`.

## Frame 152's lows

3. **A ledger entry is not a stored test.** The fence nudge now asks `not any(w[0] == "tests" for w in sb.ctx.writes)`. Test: `test_a_ledger_entry_is_not_a_stored_test`, on the answer wake, which holds `ledger.log`. The parent's condition turns it red (mutant N1b).
4. **The encode door refuses the dots as an id.** `tests_encode` in `rota/roles/api.py` refuses an id that holds only dots and spaces: `id='...' is a placeholder, not an id. Give this test an id of its own, a short name for what it checks, and send the encode again`. Test: `test_the_encode_door_refuses_the_dots_as_an_id`, through the loop. No row is stored.
5. **The code form offers the end.** A fence with no `def test` now gets `... Send it as a call: tests.encode(...), or end by saying nothing is owed.` The test form keeps its bytes: the tests assert the constant `NUDGE`, which is the sentence of pass 2.
6. **The case's stored test needs no import.** The assert is `assert "key" in output and "value" in output`, and the body imports no `json`. The failure output moves to line 13.
7. **Four lines hold a test.** `test_a_fence_left_open_at_the_end_is_a_block` holds `_FENCE_BLOCK`'s `\Z`. `test_the_case_judges_the_first_call_of_a_reply_with_two` holds `first = calls[0]`. `test_a_first_reply_with_no_call_fails_the_case` holds "the reply holds no call". `test_no_completion_after_the_replies_names_the_missing_call` holds "the model made none".

### The mutants of `mutate3.py`

`mutate3_p2.py` is the reviewer's `mutate3.py` on the worktree, with the anchors of the current code. N1b is now the parent's condition. N3 and N3b use the new `if`. N5, D1 and D2 are new: the code form loses the end, and the door admits the dots in two ways. 40 mutants: **37 red, 3 green** (observed: 2026-10-06). The 3 green are M2, M8b and N2c. The review judged each equal on every wake that rota makes: no role holds both `tests.encode` and `code.write`, and the one Tester tick carries the batch.

## The recorded case

`L1-TS-send-a-test-written-into-the-reply-as-tests-encode`, recorded again on 2026-10-06 from 12:40:52 to 12:41:54: `ROTA_L1=1 ROTA_REFRESH=1 ROTA_MODEL=qwen3.5:9b ROTA_NUM_CTX=12288`, 5 runs, one foreground batch, `cassettes: 10 recorded in 42.7s`. Every run is live.

- **First calls: 5 of 5** are `tests.encode` on the challenged id, its criterion and `tests/test_utils/test_echo_json_compact.py`.
- **First encodes that land: 5 of 5.** Each run sends one encode, at turn 2. The session writes 1 test row, and turn 3 is prose. Pass 2 of frame 152 had 0 of 5.
- The case passes 5 of 5.

## The tests

`tests/rota/test_end_step_nudge.py`, `tests/rota/test_fence_nudge.py`, `tests/rota/test_runner.py`, `tests/rota/test_desk_guards.py`, and the encode door's tests in `tests/rota/test_triage_fork.py` and `tests/rota/test_night46_context.py`: **525 passed** in 275s (observed: 2026-10-06).

## The replay of nights 119 to 125

`replay_p2.py` is `replay153.py` with frame 152's condition joined: a session counts when any reply holds no call, when its last reply holds no call, or when a prompt holds the owed-call nudge. The parent is the copy of 73d10e6 in the scratch area of session 3f72d9cb, `review152/parent`. 481 sessions, **921 runs**: 481 in variant A and 440 in variant B, 0 exceptions on each tree (observed: 2026-10-06, 12:54 to 13:00).

The two trees ran one after the other in folders with the same names. A first run put the trees in folders with different names at the same time. The folder name stands in error lines, so 134 runs differed in their prompts only. That run is void.

**15 runs differ, in 14 sessions. Each has a cause that a frame names.**

- 13 runs are frame 152's Tester fence nudge. A Tester with `tests.encode` and no `code.write` sent a fence and no call, with no test stored at that turn.
  - Variant A: n119 s141, s247, s249, s251, s271; n120 s140; n121 s141, s247, s331; n124 s141; n125 s147, s149.
  - Variant B: n120 s140.
  - These are the 12 of the review of 5e0dd71 and n120 s140 variant A. In the replay the worktree is absent, so s140's encodes are refused, and its one write is the `ledger.log` of turn 4. Item 3 now nudges it, and the head takes 7 turns against the parent's 6. On the night its encodes landed, so the night would not nudge it.
- 2 runs are frame 153's step: n125 s144 A, 5 turns against 6, and n125 s158 A, 2 turns against 4. These are the 2 runs of pass 1.

No run of item 1's shape differs. No night session met the step and then sent a call that landed.

## Deviations

- The gate ran as a detached command with foreground waits. The Bash tool stops a foreground command at 600 seconds, and this gate took 823 seconds.
- The replay's selection joins two conditions. The brief named frame 152's condition, and the pass read it as an addition to frame 153's selection.
- `mutate.py` and `mutate3.py` ran as adapted copies on the worktree. The reviewers' copies hold the older code, and M7's lines are gone.

## Seen and not fixed

1. A dotted id with letters, such as `id='...x'`, passes the door. The door refuses only an id of dots and spaces.
2. The gate's summary holds `23 failed`. They are the 23 reds of the baseline, with the known three new reds and three reds gone.

## The gate

One run from the worktree root, `python -m rota.tools.gate`, at the tree of 7fb40f2 before the commit (observed: 2026-10-06 13:00 to 13:15). The first line said `main card: held by qwen3:8b until 2026-10-06T13:05:40.1883167+01:00, re-records wait`, because another gate ran:

```
suite: 23 failed, 2864 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 823.3s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the known ones of frames 152 and 153. The stale line is 0, so the gate recorded no case. The suite has 14 tests more than at d77bdec: 8 in `test_end_step_nudge.py` and 6 in `test_fence_nudge.py`.
