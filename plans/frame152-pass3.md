# Frame 152, pass 3: a marked nudge whose call holds the seat's own body

Rota workflow code, meta workflow build. The implementing agent on Opus wrote this record on 2026-10-06, on branch `f152p3` from ac35f260, in the worktree `C:/Users/roman/rota_f152p3`. The night database was read through `mode=ro&immutable=1` connections. The scripts are in the scratch area of session 488d31af, folder `f152p3/`: `dump.py`, `copy_fixtures.py`, `show.py`, `mutate.py`, `wake154.py`, `runs154.py`, `case154.yaml`, `insert_case.py`, `read_runs.py`.

**A case on s154's reply read 0 of 5 first calls, and the pass removed it.** The brief's bar was 4 of 5, and the brief said to stop and report under it. The holding session then ruled: commit without the s154 case, remove the case and its recordings, keep the fixture for the runner test, and run the gate (ruled: the coordinator's message, 2026-10-06, after the stop report).

## The change

1. **The mark.** The sentence after a fenced reply with no call now opens with `ERROR no call: `. The cut sentence carries the same form, `ERROR reply cut:`. The Developer's sentence of the same branch gets the same mark. No other word moves.
2. **The body.** `_body_literal` renders the body of the seat's last fence that holds `def test`. Every backslash is doubled, because the parser decodes one level of escapes. The first quote that the body does not hold wins: `'`, `"`, `'''`, `"""`. The last form escapes each `'` inside `'''`. The real parser, `toolproto.extract_lenient` with the seat's calls and signatures, reads each form back. A form that does not return the same text is not offered. When no form returns it, the call keeps `body='...'`, and the sentence adds `Put the text of your fenced test in place of the dots of body.` The code form, a fence with no `def test`, keeps `body='...'` and gets no paste sentence, because its fence is not a test.
3. **The cut.** A reply that the output budget cut, with no whole call and a whole fence, now gets the nudge after the cut sentences, in the same results block. The runner reads the fence from the whole reply. Only closed fences count in a cut reply, because the budget cut the last block. A later cut reply that reaches the fence branch reads closed fences only too.

Files:

- `rota/core/runner.py`: `_WHOLE_FENCE` (line 1876), `_NO_CALL` (1882), `_body_literal` (1885), `_encode_nudge` (1910) takes `allowed`, `signatures` and `whole`. In `run_session`, `test_seat` (3052) moves above the cut branch, the cut branch adds the nudge (3082), the Developer's sentence gets the mark, and the fence branch passes `whole=bool(cut_note)`.
- `tests/rota/test_fence_nudge.py`: the constants and helpers, the tests that asserted the old sentence, 6 new test functions, and the landing test now parametrized on s149 and s154.
- `tests/rota/fixtures/night126_s154_t1.txt`, `night126_s156_t1.txt`: the turn 1 replies of s154 and s156, byte for byte from `turns.completion`.
- `tests/rota/cases/l1_tester.yaml`: unchanged. The case `L1-TS-send-the-test-of-a-reply-that-trails-off-as-tests-encode` was added, recorded and removed. Its 10 cassettes and 5 `case_runs` rows were deleted from the worktree's `tests/rota/cassettes.db`.

## The sentences before and after

Before, s154 turn 1 (copied: `plans/night126-read.md`, section 1):

```
You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...').
```

After, s154 turn 1, on the fixture of night 125 (observed: `test_s154s_turn_1_meets_a_marked_sentence_that_holds_its_body`, 2026-10-06):

```
ERROR no call: You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='''def test_echo_json_compact():
    from click.testing import CliRunner
    from src.click.utils import echo_json
    
    runner = CliRunner()
    result = runner.invoke(echo_json, ['{"key": "value"}'], catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output.strip() == '{"key": "value"}'
    # Check for single newline at end
    assert result.output.endswith('\\n')
    # Check no extra newlines
    assert result.output.count('\\n') == 1
''').
```

After, s156 turn 1, a cut reply. The results block is the cut line, a line break, and the sentence with s156's last whole test:

```
ERROR reply cut: your reply was cut at the output budget before it ended. It held no whole call, so no call ran and nothing was written. Send one call, or end with one sentence.
ERROR no call: You wrote a test into your reply, ... body='''def test_echo_json_compact():
    from src.click.utils import echo_json
    ...
''').
```

The Developer, before and after:

```
You wrote code into your reply, and a reply is not a file -- nothing landed. Send it as a call: code.write(path='...', text='...') and then code.commit.
ERROR no call: You wrote code into your reply, and a reply is not a file -- nothing landed. Send it as a call: code.write(path='...', text='...') and then code.commit.
```

The fallback, for a body that no form returns:

```
ERROR no call: You wrote a test into your reply, ... body='...'). Put the text of your fenced test in place of the dots of body.
```

## The tests

`tests/rota/test_fence_nudge.py`, 34 items, no model. Run with the neighbours `test_desk_guards.py`, `test_runner.py`, `test_night46_context.py` and `test_offers_followed.py`: 541 passed, 7 xfailed (observed: 2026-10-06 16:55).

The new tests:

- `test_s154s_turn_1_meets_a_marked_sentence_that_holds_its_body`: the prompt ends with s154's reply, an empty line and the whole sentence above, byte for byte.
- `test_s156s_cut_turn_1_meets_the_nudge_after_the_cut_sentences`: s156's reply with `done_reason: length`. The block is the cut line and the sentence. The body is s156's last whole test, which is not in the 4,000 characters shown.
- `test_a_cut_reply_whose_fence_is_cut_gets_the_cut_line_alone` and `test_a_cut_reply_gives_its_last_whole_test_and_not_the_cut_one`.
- `test_the_rendered_body_parses_back_to_the_fences_text`, 4 items: the bodies of s154 and s156, a body with `'`, `"`, a backslash, `'''` and `"""`, and the same body ending on a quote. Render, parse with `toolproto.extract_lenient`, compare.
- `test_a_body_the_parser_cannot_return_falls_back_to_the_dots`: a comment `` # `n` = 1 `` loses its backticks in the lenient parse, so the call keeps `body='...'` and the paste sentence stands.
- `test_the_call_the_nudge_names_lands_its_body_unchanged`, 2 items, s149 and s154: the call copied from the sentence as it stands goes through the real doors, and the stored body equals the fence's text.

`test_the_developers_fence_sentence_keeps_its_bytes` now asserts that the last block is the mark and the sentence of before, byte for byte.

Mutants (observed: `mutate.py`, 2026-10-06). Each undoes one repair in `runner.py`, runs the file, and puts the bytes back. Every one turns red:

| Mutant | Red |
|---|---|
| no mark | 18 |
| no body | 13 |
| no nudge in the cut branch | 2 |
| no doubled backslash | 15 |
| no paste sentence | 1 |
| the first fence, not the last | 2 |
| an open fence counts in a cut reply | 1 |

Frame 144's follow check runs on a door's refusal inside `Sandbox.call`. A runner sentence is not a refusal, so the hook does not follow it (reasoned: pass 1, "Frame 144's follow check"). The landing test makes the same check by hand: the call of the sentence goes through every door and lands. The conftest's hooks ran on every test above, and none reported a finding.

## The recordings with the counts

One foreground batch, `ROTA_L1=1 ROTA_REFRESH=1 ROTA_MODEL=qwen3.5:9b ROTA_NUM_CTX=12288`, both ids exact, 2026-10-06 16:58 to 17:01, 20 cassettes in 2m53s.

| Case | Passed | First calls `tests.encode` on the challenged id | First encodes that land |
|---|---|---|---|
| `L1-TS-send-a-test-written-into-the-reply-as-tests-encode` (s149's reply) | 5 of 5 | 5 of 5 | 5 of 5 |
| `L1-TS-send-the-test-of-a-reply-that-trails-off-as-tests-encode` (s154's reply) | 0 of 5 | 0 of 5 | 0 of 5 |

- The s149 case: each first call is the sentence's call, copied whole, with the body in `'''`. Each wrote `tests: 1`. Pass 2 read 0 of 5 first encodes that landed.
- The s154 case: the second prompt ends with the marked sentence and s154's body (observed: cassette rows 48846 to 48854, 2026-10-06 17:01, deleted since). Each turn 2 reply is 3,489 characters with 0 fences and 0 calls. It repeats turn 1's loop, "I will encode a corrected test that wraps `echo_json` ...", and ends on `But`. The 5 runs are the same text. The named-act nudge follows, and turn 3 is the stop.

Two causes can explain the 0 of 5. Neither was tested:

- s154's fence is the failing version 1 of `inh_echo_json_01` with one more line break, and s154's own text says "Wait, that's the same." So the call that the sentence offers stores the failing test again, and a seat that judged the test wrong has no reason to copy it (reasoned: the fence against the night's row, and the seat's own words).
- s154's turn 1 holds the same paragraph group three times and ends on `But`. At temperature 0 the model continues the repeated text above the sentence, and not the sentence (reasoned: 5 identical turn 2 replies that copy turn 1's paragraphs).

The case was removed on the holding session's ruling. The fixture `night126_s154_t1.txt` stays for the runner tests. The judgement of the s149 case did not change.

## The gate's five lines

One run from the worktree root, `python -m rota.tools.gate`, after the s154 case was removed (observed: 2026-10-06 17:07:56 to 17:24):

```
suite: 26 failed, 3005 passed, 34 skipped, 12 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_handover.py::test_a_newer_watcher_retires_the_older_one, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (3): ACT-DV-edit-inside-the-function (stale by its failure), ACT-TS-give-the-prompt-a-stream (stale by its failure), L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner (stale by its failure) (+3 -0 against baseline)
time: 955.2s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate marked `test_a_newer_watcher_retires_the_older_one` as flaky. This pass did not touch `rota/tools/handover.py`. The other two new reds are the known ones of passes 1 and 2.

The three stale cases were re-recorded by exact id with no `ROTA_REFRESH`, so only the moved runs went live, at the window 12288. The two qwen3.5:9b cases ran at 17:26 and the qwen3:8b case at 17:28, after the card was idle for one minute. The ratios count each run's newest row, before 17:07 and after 17:26 (observed: `case_runs`, 2026-10-06 17:29):

| Case | Model | Live runs | Before | After |
|---|---|---|---|---|
| `ACT-DV-edit-inside-the-function` | qwen3.5:9b | 1, 2 | 5 of 5 | 5 of 5 |
| `ACT-TS-give-the-prompt-a-stream` | qwen3.5:9b | 2 | 5 of 5 | 5 of 5 |
| `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` | qwen3:8b | 2 | 0 of 5 | 1 of 5 |

- `ACT-DV-edit-inside-the-function` moved on the Developer's mark. Pass 1 and pass 2 did not name it, because their sentence for the Developer did not change.
- `ACT-TS-five-criteria-one-per-reply` did not go stale. Its moved run of pass 1 did not stand on this gate's stale line.
- The third case is not equal, and it moved the right way. Before, run 2's seat copied a body with one level of escapes, and the doors refused it twice: `the body is not Python (invalid syntax, line 10)`. After, the seat sent the call of the sentence, whose body has doubled backslashes, and the first encode wrote `tests: 1`. The case stays a red of the baseline, with a bar of 4.

A replay of the three cases and the s149 case after the re-records made no live call: 100 cassettes replayed, 3 passed, and the third case failed as above.

## Deviations

1. The two night replies are fixture files, as pass 1's are. A script copied them as bytes from the night database. The Write tool would retype 40,000 characters, and a byte copy cannot change one.
2. The text blocks of the s154 case came from a script. `case154.yaml` was written with the Write tool. `insert_case.py` filled the reply, the body and the run output from the night's bytes, checked each against the loaded YAML, and inserted the case as bytes. `remove_case.py` removed it as bytes, and the case file is back at its parent's bytes.
3. The s154 case is not committed. The pass stopped on its count, and the holding session ruled its removal.

## Seen and not fixed

1. **The unchanged door of `tests.encode` compares bytes.** A body equal to the stored version apart from a line break lands as a new version (reasoned: `rota/roles/api.py`, the `prior["body"] == body` check, against s154's fence and version 1).

## Report

Status 2026-10-06 17:31: the code, the tests, the fixtures and this record are committed on `f152p3`. The s149 case reads 5 of 5 first calls and 5 of 5 landings. The s154 case read 0 of 5 first calls and was removed. The gate's stale line read 3, and the 3 cases were re-recorded: 5 of 5, 5 of 5, and 0 of 5 to 1 of 5. The recordings are in the worktree's `tests/rota/cassettes.db`. The main checkout's database does not have them.
