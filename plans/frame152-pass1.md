# Frame 152, pass 1: a Tester writes its repair in a code block and sends no `tests.encode`

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-05, on branch `f152` from 73d10e6, in the worktree `C:/Users/roman/rota_f152`. The night databases were read through `mode=ro&immutable=1` connections. The scripts are in the scratch area of session 3f72d9cb, folder `f152/`: `count.py`, `paths.py`, `preview.py`, `miss.py`.

## What changed

- `rota/core/runner.py`. `_encode_nudge` is new. A new branch in `run_session` sits after the Developer's fence branch and before the named-act nudge. Two conditions gained `not test_fence`.
- `rota/testkit/fixtures.py`. `_Replied` is new. A case's `replies:` key gives the seat's own earlier replies, and `run_case` serves them before the model.
- `tests/rota/test_fence_nudge.py`, 7 tests with no model.
- `tests/rota/fixtures/night125_s147_t1.txt`, `night125_s147_t2.txt`, `night125_s149_t1.txt`: the replies of the night, byte for byte from `turns.completion`.
- `tests/rota/cases/l1_tester.yaml`: the case `L1-TS-send-a-test-written-into-the-reply-as-tests-encode`.

## The mechanism

A reply that holds a fence and no call, from a seat whose calls hold `tests.encode` and not `code.write`, gets one nudge in the session. The nudge is:

```
You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...').
```

The values come from the wake's refs (reasoned: `_encode_nudge`):

- The refs name one row of `tests`: its `id`, `criterion_id` and `path` fill the call. A challenge carries the criterion and the test, so a challenge wake always fills all three (observed: m68 and m69 carry `["echo_json_compact", "inh_echo_json_01"]`).
- The refs name no test and one criterion: `criterion_id` is filled, and `id` and `path` stay `'...'`.
- Any other wake keeps `'...'` for all three. `body` is always `'...'`, as `text` is in the Developer's sentence.

The Developer's sentence keeps its bytes. `test_the_developers_fence_sentence_keeps_its_bytes` asserts the whole sentence.

A second fenced reply with no call is the session's real stop. The named-act nudge and the owed-call nudge do not answer it, because both conditions now hold `not test_fence`. `test_fence` is true only for a fenced reply with no call from a seat with `tests.encode` and no `code.write`. So the owed-call nudge is unchanged for every other case. For that one case it changes: a Tester on a tick whose first fenced reply got the new nudge does not get the owed-call nudge on its second fenced reply (observed: `test_a_tick_wake_names_the_one_criterion_it_holds`).

The account line is `wrote a test into its reply`. `rota/tools/nightreport.py` does not count it, and it does not count the Developer's line either.

## Every path that closes a session after a reply with no call

The order in `run_session`, at 73d10e6 (observed: `rota/core/runner.py:2939-3053`, 2026-10-05):

1. The cut branch: `done_reason == "length"`, no call, once. A cut reply comes here first, fence or not.
2. The Developer's fence branch: a fence, no call, `code.write` in the calls, once.
3. New: the Tester's fence branch, as above.
4. The named-act nudge: no call, `INTENT` in the text, and a named call in the text or nothing staged and sent. Once.
5. The owed-call nudge: no call, no held calls, a `tick:` wake, nothing staged and sent. Once.
6. `if not calls`: the held calls run. A refusal among them gets one more turn. Otherwise `break`, the session's end.
7. After `break`, `db.session_note` adds the turn `SESSION ENDED. The runner's account:` when `outcome.errors` is not empty. A session with no account line has no such turn.

s147, woken by m68, a message wake (observed: `paths.py` on 73d10e6 and on this tree, with the night's replies, 2026-10-05):

| Turn | The night | Why the fence branch was not reached | Now |
|---|---|---|---|
| 1 | No cut. Branch 2 false: no `code.write`. Branch 4 true: "I will rewrite". The named-act nudge, `continue` | Its condition needs `code.write` | Branch 3: the new nudge, with the challenged test's values |
| 2 | Branch 4 false: warned. Branch 5 false: a message wake. Branch 6: no held calls, `break` | The same | Branch 3 false: warned. Branches 4 and 5 false: `test_fence`. Branch 6, `break`. The stop |
| 3 | The account turn, `- named an act and did not perform it` | | The account turn, `- wrote a test into its reply` |

s149, woken by m69, a message wake:

| Turn | The night | Why the fence branch was not reached | Now |
|---|---|---|---|
| 1 | Branch 2 false. Branch 4 false: "We must rewrite", "Let’s fix" and "Now encode" hold no word of `INTENT`. Branch 5 false: a message wake. Branch 6, `break`. No error, so no account turn | Its condition needs `code.write` | Branch 3: the new nudge. The model's next turn decides. On the case below, qwen3.5:9b sent `tests.encode` on the challenged id in 5 of 5 runs |

The new branch is reachable on both paths: the named-act path of s147 and the silent path of s149. It also comes after a named-act nudge on an earlier prose turn, and on a tick wake.

The call that the nudge names lands with s149's own body. `test_the_call_the_nudge_names_lands_with_s149s_body` copies the call from the sentence, puts in the body of s149's fence, and the encode passes the doors and moves the test past version 2. The fixture needs the night's ledger row `l_a9da008d82`. Without it the assumption door refuses `'{"key": "value"}'`, see "Seen and not fixed".

## Other seats with a writing call

The gap is in the code for every seat whose writing calls are other calls (reasoned: branches 2 and 3 name `code.write` and `tests.encode` only). A fenced reply with no call from the Terminologist (`criteria.specify`, `glossary.amend`), the Vision Keeper (`tickets.slice`, `decisions.author`) or the Architect (`model.amend`, `decisions.author`) meets only the named-act nudge or the owed-call nudge.

The count, nights 119 to 125 (observed: `count.py`, 2026-10-05). A session counts when its last model reply holds a fence and `toolproto.extract_lenient` finds no call against the calls of its system text.

| Role | Sessions | Ends on a fenced reply with no call | Has any fenced reply with no call |
|---|---|---|---|
| Architect | 179 | 8 | 8 |
| Critic | 113 | 0 | 0 |
| Developer | 145 | 9 | 27 |
| Liaison | 574 | 0 | 0 |
| Researcher | 2 | 0 | 0 |
| Terminologist | 276 | 0 | 0 |
| Tester | 70 | 6 | 12 |
| Vision Keeper | 463 | 0 | 0 |

- Tester, 6: n119 s249 and s271, n120 s140, n121 s247, n125 s147 and s149.
- Developer, 9: all hold `code.write`, so the old branch already reaches them.
- Architect, 8: n119 s194 and s262, n121 s255, n122 s146, n123 s226, n124 s197, n125 s151 and s159.

The Architect has 8, which is 3 or more. So the pass stops before it widens, and the nudge is for the Tester only. The 8 replies are not one sign (observed: the fences, read by `count.py`'s list, 2026-10-05):

- 3 hold a `msg.challenge_vision_keeper` call written as JSON in a fence, on a `deliver` wake: n121 s255, n123 s226, n124 s197.
- 1 holds a result line the seat wrote itself, `OK msg.challenge_vision_keeper -> ...`: n119 s194.
- 3 hold code or a test that the Architect has no call to write: n119 s262 and n125 s159 on `tick:unresolved`, n122 s146 on an escalation.
- 1 quotes the error of the test and analyses it: n125 s151.

None of the 8 holds the body of an Architect's own writing call. A sentence that says "a reply is not a stored X" fits none of them. The JSON call is a different gap: the parser does not read a call written as JSON.

## The model case

`L1-TS-send-a-test-written-into-the-reply-as-tests-encode`, tier T1, the Tester in the challenge mode, `model: qwen3.5:9b`, the window 12288 as the other qwen3.5:9b cases. The fixture is s149's wake: the criterion's text, version 2 of the test, its failing run, the ledger row, and m69's refs and words. The batch holds one test, not the night's 37. Turn 1 is s149's reply from `replies:`. The runner answers it with the new nudge, and the model's turn 2 is the judgement. The case passes when the challenged test is written under its own id.

Recorded 2026-10-05 20:02, `ROTA_L1=1 ROTA_MODEL=qwen3.5:9b ROTA_NUM_CTX=12288`, 5 runs, one foreground batch, 1m51s. **5 of 5.** The first call after the nudge, in every run: `tests.encode(id=<the challenged test>, criterion_id=<its criterion>, path='tests/test_utils/test_echo_json_compact.py', body=...)`. In every run the doors refused that first encode: `the body is not Python (invalid syntax, line 12)`. Each run then landed the encode on the same id, at turn 3 in runs 1, 2 and 4, at turn 4 in run 3, and at turn 6 in run 5.

## The recorded cases that the change moved

The first gate read stale 3, each `stale by its failure`. `miss.py` replayed them, and each misses on exactly the prompt that now holds the new nudge after a recorded fenced reply with no call. They were re-recorded by exact id at 20:17, with no `ROTA_REFRESH`, so only the moved runs went live:

| Case | Model | The live run | Before | After |
|---|---|---|---|---|
| `ACT-TS-five-criteria-one-per-reply` | qwen3.5:9b | run 1 | 4 of 5 | 4 of 5 |
| `ACT-TS-give-the-prompt-a-stream` | qwen3.5:9b | run 2 | 5 of 5 | 5 of 5 |
| `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` | qwen3:8b | run 2 | 0 of 5 | 0 of 5 |

- In run 1 of the first case, the seat said at turn 6: "The previous `tests.encode` calls did not land because I included the test bodies directly in my text response". It then sent the encodes.
- In run 2 of the third case, the seat sent `tests.encode` on the challenged id after the nudge. The doors refused it twice, `invalid syntax, line 10`, and the session ended on a repeated turn. The case was 0 of 5 before this frame, and it is a known red of the baseline.

## The gate

Two runs from the worktree root, `python -m rota.tools.gate`. The first read stale 3, the three cases above. The second ran after the re-records, at 9684e3c's tree (observed: 2026-10-05 20:20 to 20:33):

```
suite: 23 failed, 2835 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 741.3s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the known ones of the brief.

## Frame 144's follow check

The follow check is in this tree: `api._offer`, `sandbox.follow`, `sandbox._ON_REFUSAL`. A runner nudge cannot be recorded as an offer through it (reasoned: `rota/core/sandbox.py:354-362`, `rota/roles/api.py:259-276`). `_ON_REFUSAL` fires only on a `ValueError` that a door raises inside `Sandbox.call`, and `_offer` records on `ctx.offers` from inside that door. A runner nudge is text that `run_session` appends to the transcript. No call is refused, and no door raises. A recording needs a new hook in the runner loop: the op `tests.encode`, the arguments of `_encode_nudge`, the body from the fence, and `dry_run` to follow it. That was not built. `test_the_call_the_nudge_names_lands_with_s149s_body` makes the same check by hand for s149.

## Seen and not fixed

1. The assumption door offers `ledger.log(...)` to a Tester in the challenge mode, and that mode's calls hold no `ledger`. The follow check reported it on the first fixture, which had no ledger row: `second refusal: NotInWorkingSet: 'ledger' is not in tester's working set; available: ['batches', 'code', 'criteria', 'msg', 'tests']`. s149's system text says "What you can reach, whatever woke you: `ledger.log`", and its list of calls lacks it (observed: night 125, s149 turn 1, the system text). This breaks frame 135's law for this mode.
2. A body that holds `\"` inside a single-quoted value does not survive the parse. In run 1 the model wrote `"{\"key\": \"value\"}"`, and the doors read line 12 as `"{"key": "value"}"`, which is not Python (reasoned: the line number and the call's text). 5 of 5 runs of the new case met `invalid syntax, line 12` on the first encode. Run 2 of the third case above met `invalid syntax, line 10` twice, and that body was not read.

## Open for the holding session

- The recordings of this pass are in the worktree's `tests/rota/cassettes.db`. The main checkout's database does not have them.
- `casestatus` stales a case on its system text. A later edit of the new sentence moves the cassette key of turn 2 and not the system text, so the case then fails as `no cassette` in the suite and does not show on the stale line until the gate classifies it by its failure.
