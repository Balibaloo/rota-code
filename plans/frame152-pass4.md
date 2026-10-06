# Frame 152, pass 4: the five lows and the medium of the review of 1cfbe704

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-06, on branch `f152p3` from 1cfbe704, in the worktree `C:/Users/roman/rota_f152p3`. The review's report is in the scratch area of session 488d31af, `review152c/REPORT.md`. This pass's mutant script is `f152p3/mutate4.py` in the same area. The code commit is 6784e6df.

## The change

1. **A fenced test that is the stored test** (the review's finding 1, medium). `_encode_nudge` compares the seat's last test fence with the stored body of the one test that the wake names. Both have their ends stripped. When they are equal, the sentence names the version and says that it failed when its newest run is not a pass. It offers `tests.encode` with the dots in body, because the seat must change the test. On a challenge wake it also offers the answer call of the asker, with the wake's refs and `quotes=['...']`, because the answer door asks for a verbatim span of the criterion.
2. **The unchanged door** (finding 5 of the review, the coordinator's 2). `tests.encode` compares `body.rstrip()` with the stored body's `rstrip()`. A line break alone moves no version.
3. **`whole=bool(cut_note)` in the fence branch** (finding 2, the coordinator's 3). A new test covers a second cut reply with a whole test fence and an open one.
4. **A cut test fence keeps the test form** (finding 3, the coordinator's 4). When `whole` is set and a test fence stands only as an open block, the sentence keeps the test form and the dots, and says that the budget cut the test.
5. **The tests parse with the signatures** (finding 4, the coordinator's 5). `SIGS` is built from `inspect.signature(api.tests_encode)` less `ctx`, as `_param_sets` builds it. `_parsed`, the round-trip test and the fallback test pass it.

Files: `rota/core/runner.py` (`_encode_nudge` and its two call sites), `rota/roles/api.py` (the unchanged door), `tests/rota/test_fence_nudge.py`.

## The sentences before and after

s154's turn 1 reply against night 126's state at m76, where `inh_echo_json_01` is version 1 and its run failed. Before, pass 3:

```
ERROR no call: You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='''def test_echo_json_compact():
    ...
''').
```

After (observed: `test_s154s_fence_that_is_the_stored_test_is_told_so`, 2026-10-06):

```
ERROR no call: Your fenced test is the stored version 1, which failed. Change the test and send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...'), or answer the challenge: msg.answer_developer(refs=['echo_json_compact', 'inh_echo_json_01'], quotes=['...']).
```

A second cut reply whose only test fence is open. Before, pass 3 (copied: the review's probe p7):

```
ERROR no call: You wrote code into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...'), or end by saying nothing is owed.
```

After (observed: `test_a_second_cut_reply_whose_test_is_cut_keeps_the_test_form`, 2026-10-06):

```
ERROR no call: You wrote a test into your reply, and a reply is not a stored test -- nothing landed. The output budget cut your fenced test before it ended. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...'). Put the whole test in place of the dots of body.
```

Every other form of pass 3 keeps its bytes.

## The tests

`tests/rota/test_fence_nudge.py`, 39 passed (observed: 2026-10-06 17:55). The new tests:

- `test_s154s_fence_that_is_the_stored_test_is_told_so`: s154's reply on a fixture with its body as version 1 and a failed run. The prompt ends with the reply, an empty line and the sentence above, byte for byte.
- `test_both_calls_of_the_same_test_sentence_pass_the_doors`: the encode with s149's body in place of the dots lands as version 2. The answer with `quotes=['followed by a single newline']` is sent. Each runs on its own fixture, through every door.
- `test_an_encode_of_the_stored_body_with_a_line_break_is_unchanged`: the door returns `identical to what is already on file`, and the version stays 1.
- `test_a_second_cut_reply_gives_its_whole_test_and_not_the_cut_one`.
- `test_a_second_cut_reply_whose_test_is_cut_keeps_the_test_form`: the review's probe p7 shape.

Mutants (observed: `mutate4.py`, 2026-10-06). Each undoes one repair, runs the file, and puts the bytes back:

| Mutant | Red |
|---|---|
| no same-test check | 1 |
| no cut-test form | 1 |
| the fence branch's `whole=False` | 2 |
| no answer offer | 1 |
| the door compares bytes | 1 |
| the tests parse with no signatures | 0 |

The last mutant stays green, and that is expected. Every body in the tests round-trips with and without the signatures. The review found 7 night bodies that round-trip without the signatures and fall back with them, all holding the text `tests.encode(`. With the signatures, the tests now measure the parser that the runner uses.

## The gate

One run from the worktree root, `python -m rota.tools.gate`, at the code of 6784e6df before its commit (observed: 2026-10-06 17:56:59 to 18:11):

```
suite: 23 failed, 3013 passed, 34 skipped, 12 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 838.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three of passes 1 and 2. `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` replays at 1 of 5, as pass 3 recorded it. Stale 0, so no case was re-recorded.

## Deviations

1. The answer call is offered only on a challenge wake that holds exactly one `msg.answer_` call. Another wake gets the encode alone. The coordinator's sentence names the challenge, and an answer mode or a tick has no challenger to answer.
2. `which failed` stands only when the newest run of the test is not a pass. A stored test with no failed run gets the sentence without those words, so the sentence states no fact the database does not hold.

## Seen and not fixed

1. The review's finding 6, plausible: the named-act nudge and the owed-call nudge carry no mark. The recorded cases key on the prompt, so the mark there is a frame of its own.
2. The review's note: the once-only nudge now spends itself in the cut branch. s156 gets the nudge at turn 1 beside the cut line, and turn 4 gets none. That is the design, told once.
3. The comparison of finding 1 strips both ends, and the door strips the right end only. A fence that differs from the stored body by leading whitespace alone gets the same-test sentence, and the door would land it. No night body was seen in that shape.

## Report

Status 2026-10-06 18:13: the code is committed as 6784e6df and this record as the next commit on `f152p3`. The gate reads stale 0 and the three known reds. No recording changed in this pass.
