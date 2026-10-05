# Frame 152, pass 2: the eight lows of the diff review of 9684e3c

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-05, on branch `f152` from ce270ef, in the worktree `C:/Users/roman/rota_f152`. The reviewer's probes are in the scratch area of session 3f72d9cb, folder `review152/`. This pass's scripts are in the folder `f152/`: `mutate2.py` and `cmp2.py`.

## The repairs

1. **A session that wrote is not told "nothing landed".** `test_fence` now holds `not sb.ctx.writes`. A Tester that landed an encode and then shows the test in a fence closes as on the parent. Test: `test_a_session_that_wrote_is_not_told_nothing_landed`, from `probe2.py` I.
2. **An answer that names one criterion with one stored test names that test.** `_encode_nudge` looks up the tests of a single named criterion. When exactly one exists, its id and path fill the call. Test: `test_an_answer_naming_a_criterion_with_its_one_test_names_the_test`, from `probe2.py` G and G2.
3. **A mode that holds `tests.triage` names the triage first.** The real `tests_missing` tick carries the batch, so the values stay `'...'`. The test copies the two calls from the sentence, fills the values, and both land through the doors. Test: `test_the_real_tests_missing_tick_names_the_triage_and_both_land`, from `probe2.py` F.
4. **A fence with no `def test` is code.** `_FENCE_BLOCK` finds the fenced blocks, and the sentence says "You wrote code" when none holds `def test`. A test function named in the prose does not count. Test: `test_a_fence_with_no_test_function_is_code_in_the_sentence`, from `fences.py`.
5. **The case judges one thing.** The new key `expect.first_call` checks the model's first call after the scripted replies: its function and the arguments that the case names. The case no longer scores the write. The fixture's test now asserts `json.loads(output) == {"key": "value"}` and imports `json`, so it holds no literal with both quote kinds. The failure output moves to line 14 to match.
6. **A case that judged nothing fails.** `_Replied` counts the calls that reach the model. A case whose replies end the session gets the problem `the model made no completion after the scripted replies, so the case judged nothing`. `CaseResult.scripted` marks the scripted entries in the transcript with `"scripted": true`. `run_chain` raises on `replies:` in the case or in either leg. Tests: `test_a_case_whose_replies_end_the_session_judged_nothing`, `test_the_case_judges_the_first_call_after_the_replies` and `test_a_chain_refuses_scripted_replies`, from `probe5b.py`.
7. **The mutants.** New tests: an Architect's fenced reply, a Developer's second fence, a wake with two tests, an answer with two criteria, and a project test with a NULL criterion. The results are below.
8. **The tick test is the real one.** The test with `refs=("echo_json_compact",)` is now driven by a Terminologist's answer that names the criterion. The real tick, `refs=("bg_1",)`, is the test of repair 3. Every `tests_missing` tick of nights 119 to 125 carries the batch: 30 of 30 (observed: `sessions.wake_refs`, 2026-10-05).

## Every form of the sentence

| The wake | The sentence |
|---|---|
| A challenge that names the test, with a fence that holds `def test`: s147, s149 | `You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...').` |
| The same challenge, with a fence that holds no `def test` | `You wrote code into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...').` |
| An answer that names a criterion with one stored test | The first form |
| An answer that names a criterion with no stored test | `... Send it as a call: tests.encode(id='...', criterion_id='echo_json_compact', path='...', body='...').` |
| The `tests_missing` tick, `refs=("bg_1",)` | `You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.triage(criterion_id='...', verdict='encodable') and then tests.encode(id='...', criterion_id='...', path='...', body='...').` |
| Two tests, or two criteria, in the refs | `... tests.encode(id='...', criterion_id='...', path='...', body='...').` |
| A project test with a NULL criterion | `... tests.encode(id='inh_1', criterion_id='...', path='tests/test_echo.py', body='...').` |

The Developer's sentence keeps its bytes (observed: `test_the_developers_fence_sentence_keeps_its_bytes`, 2026-10-05).

## The model case

`L1-TS-send-a-test-written-into-the-reply-as-tests-encode`, recorded again at 21:17 on qwen3.5:9b, the window 12288, 5 runs in one foreground batch, 45s. **5 of 5**: the first call after the nudge is `tests.encode` on the challenged id, criterion and path in every run.

**First encodes that land: 0 of 5.** Each first body was refused with `the test uses json and never imports it: a NameError against any code. Add the line ``import json`` ...`. The model took the imports of s149's repair and the new `json.loads` assert of the fixture, and it did not add `import json`. The door is right: the body has no `import json` (observed: run 1's call, 2026-10-05). The escape wall of pass 1 is gone from the first call. Each run landed the encode on the same id at its second encode.

## The replay of nights 119 to 125

The reviewer's `replay.py` ran on this tree. `cmp2.py` compares the result with the reviewer's parent replay at 73d10e6. The replay covers 449 sessions that end on a no-call reply, in 889 runs: variant A scripts every reply of the session, and variant B scripts only the trailing no-call replies (observed: 2026-10-05 21:14).

**10 runs differ, in 10 sessions.** Every one is a Tester on a message wake, with `tests.encode` and no `code.write`, and its nudged reply holds a fence and no call, in a session that had written nothing at that turn:

- Variant A: n119 s141, s249, s251, s271; n121 s141, s247, s331; n125 s147, s149.
- Variant B: n120 s140.

**Night 120 s140, variant A, does not differ.** At the head of pass 1 it differed: the head closed it in 3 turns, and the parent in 2. Repair 1 closes it in 2. Variant B of s140 starts the session at the trailing fenced reply, so that session has written nothing, and the nudge is right there. The head of pass 1 differed in 11 runs, and this tree differs in 10.

## Mutants

`mutate2.py` writes one mutant at a time into `runner.py` or `fixtures.py`, runs `test_fence_nudge.py`, and puts the bytes back. The 16 mutants of the review, renamed to the new code, and 13 on this pass's lines: 29 in all. 27 turn red. 2 stay green, and both are equivalent on every wake that rota makes (reasoned):

- **M2, drop `"code.write" not in allowed`.** The condition differs only for a seat that holds both `tests.encode` and `code.write`. No role holds both (observed: the calls of the system texts, nights 119 to 125, `count.py` of pass 1).
- **M8b, read the refs from the message only.** The fallback to `wake.refs` serves a tick. The one Tester tick, `tests_missing`, carries the batch (`rota/core/predicates.py:716`, and 30 of 30 on the nights), and a batch fills no value. So both versions print the same sentence.

## The gate

The first gate read stale 1: `ACT-TS-give-the-prompt-a-stream`, stale by its failure. Its run 2 is a `tests_missing` tick whose recorded reply holds a fence and no call, and its next prompt now holds the form that names the triage (observed: `miss.py`, 2026-10-05). It was re-recorded by exact id at 21:31. Only run 2 went live. **5 of 5**, as before. In run 2 the seat sent `tests.triage` after the nudge, and the encode landed.

The second gate, from the worktree root (observed: 2026-10-05 21:32 to 21:43):

```
suite: 23 failed, 2847 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 620.2s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the known ones.

## Seen and not fixed

1. The assumption door offers `ledger.log(...)` to a Tester in the challenge mode, and that mode's calls hold no `ledger` (`rota/roles/api.py:5708-5719`). The finding is the same as in pass 1.
2. The parser decodes one level of escapes inside a quoted value. A literal that holds both quote kinds does not survive a call. The fixture now avoids it. The wall stands for the nights.
3. The fixture's `json.loads` assert asks the model to carry an import, and 5 of 5 first bodies did not carry it. A body that needs no import would measure the landing more closely. The pass did not try a second fixture.
