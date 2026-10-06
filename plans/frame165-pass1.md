# Frame 165, pass 1: the step to end the session names the reply that takes it

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-06, on branch `f165` from 44d3e382, in the worktree `C:/Users/roman/rota_f165`. The code and the tests are in d7610a48. The night databases were read through `mode=ro&immutable=1` connections, or copied as bytes with an empty WAL. The scripts are in the scratch area of session 488d31af, folder `f165/`: `look.py`, `fixture.py`, `append_case.py`, `mutate.py`, `runs.py`, `replay165.py`, `cmp165.py`, `why168.py`, `why168b.py`.

## The change

- `rota/core/sandbox.py`. The constant `END_FORM` holds the reply that takes `END_STEP`. `_escalation_or_step` gives the step, then the form, when its step is `END_STEP`. The new `_end_form` names the test ids among the refs, in the order of the refs. A ref list with no test names every ref. Each id goes through `api._fact(ctx, "row", ...)`, so frame 144's fact check reads it. `END_STEP`, `_Ending`, `api.EndRefusal`, the runner's flag of frame 153 and every other door keep their bytes.
- `rota/testkit/fixtures.py`. Three keys for a case of one session:
  - `replies:` takes `{file: <name>}` beside a string. The file is read as bytes from `tests/rota/fixtures`.
  - `rewrite:` holds `[old, new]` pairs that `_Replied` applies to each prompt the model gets. A pair that matches no prompt is a problem of the run.
  - `expect: {no_call: true}` judges the model's first reply after the scripted ones. The reply fails on a `TOOL:` line, and on a call that `toolproto.extract_lenient` reads.
- `tests/rota/fixtures/night126_s172_t2.txt`: s172's turn 2 of night 126, byte for byte from `turns.completion`, 351 characters, no CR.
- `tests/rota/cases/l1_developer.yaml`: the cases `L1-DV-end-the-session-when-the-door-says-end` and `L1-DV-end-the-session-when-the-door-says-end-the-old-step`.
- `tests/rota/test_end_form.py`: 9 tests, new.
- `tests/rota/test_end_step_nudge.py` and `tests/rota/test_desk_guards.py`: the expected refusals carry the form. 4 asserts in total.

No change to `rota/core/runner.py`. The one-line reply holds no word of `INTENT`, no fence and no call, and the frame 153 flag stops the owed-call nudge (observed: the tests below, 2026-10-06).

## The sentence before and after

On s172's state, night 126, turn 2 (observed: `test_the_step_on_s172s_state_names_the_test`, 2026-10-06).

Before:

```
ERROR msg.challenge_tester: you sent challenge to tester on exactly these refs already (m76, then m77), and the Tester answered neither and did not change the test. End the session with no call.
```

After:

```
ERROR msg.challenge_tester: you sent challenge to tester on exactly these refs already (m76, then m77), and the Tester answered neither and did not change the test. End the session with no call. Your whole next reply is this one line, and no TOOL: line: Nothing more is owed on inh_echo_json_01 in this session.
```

The form follows the voice of the door's other steps: one sentence that says what to send, as `send refs=[...]` and `Send msg.escalate_architect on the same refs.` do.

## The tests

`tests/rota/test_end_form.py`, on s172's rows: the item, the ticket, the criterion, version 1 of `inh_echo_json_01`, m76 and m77 closed with no Tester answer, the Architect's m83 to m76, and the escalation m78 closed.

| Test | What it holds |
|---|---|
| `test_the_step_on_s172s_state_names_the_test` | s172's turn 2 meets the real door, and the prompt ends with the refusal above |
| `test_the_one_line_reply_ends_the_session_with_no_nudge`, `tick:exhausted` and `tick:tests_failing` | the one line ends the session after 2 model calls. The only error is the door's refusal. No owed-call, fence, test-fence or named-act nudge. The session commits |
| `test_the_step_is_still_an_end_refusal` | the door raises `api.EndRefusal` with the text above, and `sandbox.check_facts` gives `ok` for the row fact `inh_echo_json_01` |
| `test_the_case_serves_the_nights_reply_and_the_real_door` | the case's turn 1 is the fixture's bytes, the model's prompt ends with the real door's refusal and the form, and the one line passes |
| `test_the_old_step_case_gives_the_nights_sentence` | the rewrite gives the night's line, which ends on `End the session with no call.` |
| `test_a_reply_with_a_call_fails_the_case`, 2 parameters | a `TOOL:` line fails the case, and a bare call that the parser reads fails it |
| `test_a_rewrite_that_matches_no_prompt_fails_the_case` | a pair that matches nothing is a problem |

The conftest's follow check and fact check of frame 144 ran on every refusal of these tests and found nothing.

### Each test goes red without its repair

`mutate.py` writes one revert at a time, runs `test_end_form.py` with `-n 0`, and restores the bytes (observed: 2026-10-06).

| Mutant | Red |
|---|---|
| S1 the step has no form | 4 of 4 door and runner tests |
| S2 the form records no fact | 1, `test_the_step_is_still_an_end_refusal` |
| S3 the form names every ref, not the test | 4 of 4 |
| R1 the owed-call nudge ignores the frame 153 flag | 2, the one-line tests |
| R2 the door raises `ValueError` | 3: the one-line tests and the `EndRefusal` test |

The case tests were written after the mutant run, and no mutant ran on them. Each asserts a text or a problem that the parent's `fixtures.py` does not produce (reasoned: the parent has no `{file:}` reply, no `rewrite:` and no `no_call:`).

Touched files, run first (observed: 2026-10-06): `test_end_form.py` 9 passed, `test_end_step_nudge.py` 11 passed, `test_desk_guards.py` 306 passed, `test_fence_nudge.py` 24 passed, `test_fixtures.py` passed after one fix. The fix: the case comments named `m76` and `m83` bare, and `test_no_case_leaves_a_reference_unwrapped` refused them. The comments now name no id.

## The recordings

Both cases: tier T1, the Developer, `tick: exhausted`, `detail: attempt 10 of 10`, `model: qwen3.5:9b`, window 12288. Turn 1 is `{file: night126_s172_t2.txt}`. The criterion and the test keep the night's ids, because the scripted reply names them and the door compares the refs. The batch, the item, the ticket, the messages and the run are holes, so the five runs are five prompts.

1. `L1-DV-end-the-session-when-the-door-says-end`, `pass: 4`. Recorded 17:23:02 to 17:23:42: `ROTA_L1=1 ROTA_REFRESH=1 ROTA_MODEL=qwen3.5:9b ROTA_NUM_CTX=12288`, one foreground batch, `cassettes: 5 recorded in 34.8s`. Every run is live. **5 of 5.** Each reply is the one line, `Nothing more is owed on inh_echo_json_01 in this session.`, and the session ends there.
2. `L1-DV-end-the-session-when-the-door-says-end-the-old-step`. The same case with the form rewritten out, so the model gets the night's line. Recorded 17:24:09 to 17:25:21, the same command, `cassettes: 22 recorded in 68.5s`. Every run is live. **0 of 5.** Each first reply after the refusal holds a `TOOL:` line: `msg.question_vision_keeper` in runs 1, 3 and 4, and `msg.escalate_architect` in runs 2 and 5. No run sent the refused challenge again.

The first case is at least 4 of 5, so both cases stay. The second case measures and does not gate: its bar is 0, and its comment holds both counts. A plain replay of both, with no refresh, passed: `cassettes: 27 replayed`.

## The replay of nights 119 to 126

`replay165.py` takes each session whose prompts hold an ERROR line that ends on `End the session with no call.`, and scripts every reply of the night. Each run gets a fresh copy of the night database, with the project root and the worktrees pointed at nothing. The parent is `git archive 44d3e382 rota`, and the head is a copy of this tree's `rota`, both in the scratch folder. The two trees ran one after the other in the same folder names. `cmp165.py` takes the form out of each head prompt and error, and compares with the parent to the byte, with the commit, the turn count and the replies left (observed: 2026-10-06, about 17:27).

- Nights 119 to 124 hold no such session (reasoned: the comments of `_challenge_repeat_refusal` date the step's branch to frame 132, 2026-10-05).
- **10 sessions**: night 125 s153, s156, s157, s158, and night 126 s159, s166, s167, s168, s169, s172. 0 exceptions on each tree.
- **64 refusals with the step** on each tree. On the head, 64 of 64 carry the form, and each names `inh_echo_json_01`.
- **9 of 10 sessions are equal to the byte less the form.** n126 s159 meets no step in the replay, because the database at the end of the night is not its state, so its prompts are equal raw.
- **n126 s168 differs in one more way.** Prompt 11 of 12 is 3,226 characters shorter than the parent's, less the forms. The prompt before it is 26,905 characters on the head, 117 more than the parent, and the window's fit, `runner._fit`, evicts a middle reply and its results one turn earlier. The errors, the commit and the turn count are equal (observed: `why168.py`, `why168b.py`, 2026-10-06). The night's s168 met the step 11 times, so its transcript holds 11 forms.

## The gate

One run from the worktree root, `python -m rota.tools.gate`, at the tree of d7610a48 before the commit (observed: 2026-10-06, 17:28 to 17:38). The first line said `main card: held by qwen3.5:9b until 2026-10-06T17:32:31.5973538+01:00, re-records wait`, the model of this pass's recordings.

```
suite: 23 failed, 3019 passed, 34 skipped, 12 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 603.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds and the three reds gone are the known ones of frames 152 and 153 (copied: `plans/frame153-pass2.md`, the gate). The stale line is 0. The summary holds `23 failed`, the count of the baseline.

## Deviations

- The contrast case has `pass: 0`, not `pass: 4`. The brief asked for a case equal to the first. With the bar of the first, its 0 of 5 is a new red in every gate, and the gate is the condition of the commit. The bar of 0 keeps the recordings, and the register keeps the count of each run.
- The old sentence reaches the contrast case through a new case key, `rewrite:`, and not through the door. The door renders only the new sentence. The rewrite takes the form out of the real door's refusal, so the rest of the line is still the door's own.
- The scripted reply reaches the case through a new form of `replies:`, `{file: ...}`. The key of frame 152 held only strings. The file lets the case and the tests share one copy of the night's bytes.
- The replay of nights 119 to 126 is a scratch script, not a suite test. It reads the night databases in `D:/repos/rota/.rota`, which the worktree does not hold.
- The replay shows one change beside the sentence: s168's fit. The brief asked for no other change. The fit is the window's rule, and the pass did not change it.
- The gate ran as a background command with a foreground wait. The Bash tool stops a foreground command at 600 seconds, and the gate took 604 seconds.
- File reads used the Bash tool where the session's harness asked for it. Every tracked file was written with the Write or Edit tool, or with a script that writes bytes, as the brief rules.

## Seen and not fixed

1. Two other refusals offer the end as a choice with no form: the escalation door, `make one real change to the code the test calls, or end the session with no call`, and `_waits_refusal`. They raise `ValueError`. s168 took the first option of the same choice in the `tests.load` result, `"after these"`, at turn 2 (copied: `plans/frame165-interview.md`). The brief names only the step.
2. A longer refusal moves the window's fit in a long session. In s168 the eviction came one turn earlier. Each form adds 117 characters per refusal with the step.
3. The case judges the copy of a named line. On a night the prompt is longer, the window is 16384 and the batch holds about 40 tests. Whether the seat takes the line there is for the walk.
4. In the contrast case, with one test in the batch, no run sent the refused challenge again. Each run sent a question to the Vision Keeper or an escalation to the Architect, and the escalation door refuses the latter on this state. The night's sessions sent the same challenge again in 5 of 11 turns (copied: `plans/night126-read.md`, section 2). The case's state is smaller than the night's.
5. When the refs of a refused challenge name no test, the form names every ref. No refusal of the replay met that branch: all 64 named a test.

## Report

- The commit of the code and the tests: d7610a48. This record follows in its own commit.
- The new sentence: `End the session with no call. Your whole next reply is this one line, and no TOOL: line: Nothing more is owed on inh_echo_json_01 in this session.`, after the door's fact.
- The cases: the form 5 of 5, the night's step 0 of 5, both on qwen3.5:9b at 12288, every run live.
- The replay: 10 sessions, 64 refusals with the step, 64 forms. 9 sessions equal to the byte less the form, and s168 differs by the window's fit at prompt 11.
- The gate: the three known new reds, stale 0.
- Usage: the harness reports the agent's usage to the holding session. This record does not estimate it.
