# Frame 153, pass 1: a door tells the Developer to end the session, and the runner's nudge then asks for a call

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-05, on branch `f153` from 8838632, in the worktree `C:/Users/roman/rota_f153`. The night databases were read through `mode=ro&immutable=1` connections. The scripts are in the scratch area of session 2ba331e1, folder `f153/`: `dump.py`, `mutate.py`, `replay153.py`, `cmp153.py`.

## The 7 turns that met the step

The step is `End the session with no call.` of the same-refs door. Night 125 has 7 turns whose results hold it (observed: `turns` of s153, s156, s157, s158, `dump.py`, 2026-10-05). The table gives what the seat sent next and what the runner sent between.

| Met at | The seat's next reply | What the runner sent before that reply | Followed |
|---|---|---|---|
| s153 t2 | t3: prose, "The session ends here with no further tool calls." The session ended | The results of t2 only. The same reply had sent m72, so no nudge could fire | yes |
| s156 t1, 4 results | t2: the same challenge, a bare call | The 4 refusals only | no |
| s156 t2 | t3: the same challenge | The refusal only | no |
| s156 t3 | t4: the same challenge. The session ended on a repeated turn | The refusal and the `NOTE ... will not be accepted again` | no |
| s157 t1 | t2: `msg.escalate_architect`, refused by the escalation door | The refusal only | no |
| s158 t1 | t2: prose, "I must end the session now" | The refusal only | yes |
| s158 t3 | t4: prose, the same words as t2. The session ended | The refusal only. The owed-call nudge had fired once, so it did not fire again | yes |

Between s158 t2 and t3 the runner sent the owed-call nudge: `You were woken because something is owed here, ... Act on your conclusion with a call: fix it, dispute it with the evidence quoted, or escalate it. If truly nothing is owed, say so and stop.` s158's t3 is its t1 again, with the same refused challenge.

What the rows show:

- The nudge caused one turn: s158 t3. That is the sign that the frame names, and the cause holds.
- The nudge is not the cause of the 4 turns that did not follow. No runner text stood between the refusal and those replies. s156 sent the refused call again at once, and s157 tried the escalation. That cause is a different one, and this pass did not touch it.
- s158 read the full prompt with the step at the end of each result block. Its system text holds no word that conflicts with the step. The prompt of t1 also says `A listed message that is answered or closed is refused if sent again on these refs. Make one real change to the code the test calls, or end the session with no call.` (observed: s158 t1 user, `[tests.load]`).

## What changed

- `rota/roles/api.py`. The new class `EndRefusal(ValueError)` sits beside `Wall`.
- `rota/core/sandbox.py`. The constant `END_STEP` holds the step's text. `_escalation_or_step` returns the text as `_Ending`, a subclass of `str`, when its step is `END_STEP`. `_bind_send` raises an `_Ending` as `api.EndRefusal`, and any other refusal as `ValueError`. The text of every refusal keeps its bytes.
- `rota/core/runner.py`. `run_session` keeps `told_to_end`. Each ERROR line that answers a call sets it: true for an `EndRefusal`, false for any other refusal, tool error, argument error or repeat refusal. The owed-call nudge needs `not told_to_end`. A reply with no call then reaches `if not calls`, and the session ends.
- `tests/rota/test_end_step_nudge.py`, 3 tests with no model.
- `tests/rota/fixtures/night125_s158_t1.txt` to `t4.txt` and `night125_s157_t2.txt`: the replies of the night, byte for byte from `turns.completion`.

### How the runner knows

The fact is the class of the exception, and the door sets it. The precedent is `api.Wall`, which `db.py` reads by class and not by words.

The first design read `sb.ctx.refusals[-1]`. That failed: a message's refusal never reaches `ctx.refusals`, because `msg.*` is bound by `_bind_send` and not by `_bind` (observed: the first test run, 2026-10-05). So the runner keeps its own flag, set at every ERROR line that answers a call.

The tests use `sandbox.END_STEP` to build the refusal they expect. A change of the sentence keeps the tests in step with the door. The class, not the words, decides the nudge.

## The tests

1. `test_s158_ends_when_the_door_says_end`: s158's four replies. The door gives the night's refusal at turn 1. Turn 2 has no call, and the session ends there with 2 model calls. No `ended a tick with nothing done`. The session commits.
2. `test_a_refusal_with_another_step_keeps_the_nudge`: s150's shape, with no escalation yet, so the door offers the escalation. The reply with no call gets the nudge, and the prompt ends with the reply, a blank line and the parent's sentence, to the byte. The same turns on a state with m70 get no nudge.
3. `test_only_the_newest_refusal_counts`: the step, then s157's escalation, which the door refuses with no step, then a reply with no call. The nudge comes back. The reverse order gets no nudge.

### Each test goes red without the repair

`mutate.py` writes one revert at a time and runs the file with `-n 0` (observed: 2026-10-05):

| Revert | Red |
|---|---|
| R1, the runner's condition loses `and not told_to_end` | 3 of 3 |
| R2, the door raises `ValueError` again | 3 of 3 |
| R3, a later door refusal does not clear the flag | 1 of 3, the newest-refusal test |

A plain `git stash` of the code made the file fail at import on `sandbox.END_STEP`. That is not a behaviour red, so the mutants replace it.

## The replay of nights 119 to 125

`replay153.py` is the frame 152 reviewer's `replay.py` with a wider selection: a session counts when its last reply holds no call, or when any prompt of the night holds the owed-call nudge. Variant A scripts every reply. Variant B scripts only the trailing replies with no call. Each run gets a fresh copy of the night database. `cmp153.py` compares this tree with the parent 8838632 on the users' hashes, the errors, the commit and the turn count (observed: 2026-10-05, finished before 22:23).

- 458 sessions, 898 runs: 458 in variant A and 440 in variant B. 449 sessions end on a reply with no call. 28 got the owed-call nudge on the night.
- The parent replay sends the owed-call nudge 188 times. 3 of those prompts hold the step as the newest ERROR line before the nudge, in 2 runs.
- **2 runs differ, in 2 sessions. Both are a Developer on `tick:tests_failing` whose newest refusal held the step.**
  - n125 s158, variant A: the parent closes in 4 turns with the nudge, and this tree in 2.
  - n125 s144, variant A: the parent closes in 6 turns with the nudge, and this tree in 5. On the night, s144's challenge landed as m67. The replay runs on the database at the end of the night, where m68 and m69 stand, so the door refuses it. The difference is real for that state and is not a night event.
- Every other run is equal, so the Tester's fence nudge of frame 152 and the Developer's fence nudge keep their bytes on all 898 runs.

## What happens after the silent end

This is a read of the code and of night 125 (reasoned: `rota/core/loop.py:300-345`, `rota/core/scheduler.py:1575-1720`, `rota/core/loop.py:550-575`).

1. `step` counts each dispatch of a tick key before the session runs, `note_dispatch`. The count does not depend on what the session does.
2. The test stays red, so `tick:tests_failing` for `bg_1` fires again. The next seat to wake is the same Developer with the same wake, and the door refuses the same challenge.
3. `quarantine_overrun` sets the key to quarantined at `tick_attempt_cap`, 3. The Liaison then wakes on `tick:quarantined`.
4. On night 125 that is s156, s157 and s158, then the Liaison s163 (copied: `plans/night125-cycle-read.md`, section 1.5). s158's prompt says `This is attempt 3 of 3 on this wake`.

So the silent end makes no loop of wakes. The same Developer wake does come again with the same refused challenge, at most 3 times, as on the parent. The nudge changed no count, because s158 wrote nothing and sent nothing with it or without it. The change saves 2 turns in s158.

## Deviations

- The brief preferred a fact that the door sets. The first form of that fact, the newest entry of `ctx.refusals`, does not see message refusals. The runner now keeps the flag itself. The fact is still the door's class.
- The gate ran as a background command with a wait loop in the foreground. The Bash tool caps a foreground command at 600 seconds, and frame 152's gates took 620 and 741 seconds.

## Seen and not fixed

1. 4 of the 7 turns did not follow the step, with no runner text between: s156 three times, s157 once. That cause is not the nudge.
2. The named-act nudge does not read the flag. A reply such as "I will end the session" matches `INTENT`, and with nothing written or sent it gets `Send the call you named, ... or end by saying nothing is owed.` The replay of nights 119 to 125 holds 0 such cases after the step. The sentence offers the end, so it does not contradict the door.
3. Two other refusals offer the end as a choice: `_waits_refusal` and the escalation door, `make one real change to the code the test calls, or end the session with no call`. They raise `ValueError`, so the nudge still follows them. The brief names only the step.
4. The escalation door prints `they answered (answered)` when no answer row exists (`rota/core/sandbox.py`, the `answer_id = prior["answer_id"] or prior["status"]` line). The night read found this.

## The gate

One run from the worktree root, `python -m rota.tools.gate`, at d77bdec's tree (observed: 2026-10-05 22:23 to 22:39):

```
suite: 23 failed, 2850 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 769.4s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds and the three reds gone are the known ones of frame 152. The stale line is 0, so no case was recorded. The gate ended at 22:39, before the order to pause the GPU reached this pass. After the order, this pass ran no command that calls a model.
