# L1 reds after the Critic land and the R land, 2026-10-29

Read-only causal read of the main-register run of the Liaison and Critic L1
cases. The log is
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/l1_li_cr_main_R.txt`
(9 failed, 40 passed). The history is from `tests/rota/cassettes.db`, table
`case_runs`, opened with `?mode=ro`. No model call ran and no file changed
except this page.

## Result

| Case | Cause | Red before today? |
|---|---|---|
| L1-CR-pass-a-conforming-diff | The model: llama3.1:8b, not Gemma and not qwen. The run had no `ROTA_MODEL`. | No. Green on qwen3:8b, 175/175 at 26d3fd0c, last 2026-10-28 01:33 |
| L1-CR-a-test-that-encodes-nothing-is-a-challenge | The Critic land (64e4cfa8). Same model, gemma3:12b. | No. Green, 10/10 at 26d3fd0c, 2026-10-28 01:36 |
| L1-CR-a-kept-behaviour-passes-by-its-kept-line | The model: llama3.1:8b, for the same missing `ROTA_MODEL`. The case has no measure on any other model. | New today, no history |
| L1-LI-a-reply-reaches-the-desk-that-asked | The model: gemma4:12b-it-qat against qwen3:8b. Not the R land. | Yes. Red 0/5 on gemma4 at 07:41 today, before both lands. Green on qwen3:8b to 2026-10-26 |

### A correction to the brief of this read

The brief says that the register re-recorded the cases "live on Gemma". That
is true for the Liaison cases only. `tests/rota/test_l1.py` line 42 reads
`MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")`. A case with no `model:`
pin ran on llama3.1:8b today. The Critic cases have three models in this run:

- `pass-a-conforming-diff` and `a-kept-behaviour-passes-by-its-kept-line`
  have no pin. They ran on llama3.1:8b. Every earlier run of
  `pass-a-conforming-diff` was on qwen3:8b.
- `a-test-that-encodes-nothing-is-a-challenge` has the pin `gemma3:12b`.
- `a-doubtful-criterion-is-a-question-to-the-terminologist` has the pin
  `qwen3:8b`.

The other unpinned Critic cases also ran on llama3.1:8b today and passed 5/5:
challenge-a-claim, dismiss-a-finding-on-a-falsified-constraint,
fail-names-its-criterion, finish-the-review-with-the-answer-in-hand. So two of
the four reds have no measure on the reference model after the Critic land.

## 1. L1-CR-pass-a-conforming-diff

**Assertion.** `expect.writes.verdicts: {count: 1}`, 4 of 5 runs. Every run:
"expected writes to verdicts (1), got 0".

**Calls.** All five runs call `verdicts.claim_encodes` and then
`msg.challenge_tester`. Run 1 repeats the challenge and sends
`msg.question_terminologist` many times. The tool refuses the repeats ("you
have already sent challenge to tester"). Runs 4 and 5 try `verdicts.emit`
after the challenge, and the tool refuses one verdict after a challenge. The
reason in run 1: "the test `tst_…` asserts `prorate(999, 1, 3) == 333`. This
does not encode the criterion."

**History** (newest first, groups of one load):

| Time | Model | Prompt hash | Result |
|---|---|---|---|
| 2026-10-29 14:32 | llama3.1:8b | 3fef5a81 | 0/5 live |
| 2026-10-28 01:24 to 01:33 | qwen3:8b | 26d3fd0c | 10/10 replay |
| 2026-10-26 18:02 | qwen3:8b | 26d3fd0c | 5/5 replay |
| 2026-10-26 08:13 to 09:04 | qwen3:8b | 26d3fd0c | 10/10 replay |
| 2026-10-26 06:48 to 07:29 | qwen3:8b | 26d3fd0c | 15/15 replay |

**Cause: the model (llama3.1:8b).** The case never ran on llama3.1:8b before.
The case never ran on qwen3:8b at the new hash. So the Critic land is not
measured on this case, and today's red does not show a land fault.

**Finding about the case, not a cause.** The fixture's test
`assert prorate(999, 1, 3) == 333` does not encode its criterion "prorating
more days than the period holds is refused". Step 2 of `review.md` tells the
Critic to challenge such a test. So llama3.1:8b follows the brief, and the
case expects a pass that the brief forbids. The sibling case
`a-test-that-encodes-nothing-is-a-challenge` expects the challenge for the
same shape. qwen3:8b passed this case because it did not apply step 2.

**Fix line.** No land fix. Re-record with `ROTA_MODEL=qwen3:8b`. Separately,
give the fixture a test that encodes the refusal, for example
`with raises(ValueError): prorate(999, 4, 3)`.

## 2. L1-CR-a-test-that-encodes-nothing-is-a-challenge

**Assertion.** A message to `tester` with verb `challenge`, refs `<c1>` and
`<tst1>`, 3 of 5 runs. A write to `verdicts` is forbidden. Every run: "got 0
match(es); forbidden write to verdicts".

**Calls.** All five runs: `code.read`, `criteria.load`, `tests.load`, then
`verdicts.emit(result='pass', lines={'<c1>': 'rec.values["state"] =
"tombstoned"'})`. The review loop asks "Does that line do what the criterion
says, or the opposite?". The model sends the pass again, and the pass lands.
Run 3 also questions the Terminologist. Run 5 claims `encodes` and still
passes. No run sends `msg.challenge_tester`. Runs 1, 2 and 4 say in the reply
that the test passed, for example "The test `assert close_account('a1') is
not None` passed."

**History:**

| Time | Model | Prompt hash | Result |
|---|---|---|---|
| 2026-10-29 14:42 | gemma3:12b | 3fef5a81 | 0/5 live |
| 2026-10-28 01:26 to 01:36 | gemma3:12b | 26d3fd0c | 10/10 replay |
| 2026-10-26 18:04 | gemma3:12b | 26d3fd0c | 5/5 replay |
| 2026-10-26 08:16 to 09:06 | gemma3:12b | 26d3fd0c | 10/10 replay |
| 2026-10-26 06:52 to 07:31 | gemma3:12b | 26d3fd0c | 15/15 replay |

**Cause: the Critic land.** The model is the same. The prompt hash moved from
26d3fd0c to 3fef5a81, and the result moved from 10/10 to 0/5. Before the land,
gemma3:12b opened with `msg.challenge_tester` (run 1 at 26d3fd0c: five
challenges, then `claim_encodes`). After the land, step 1 of `review.md`
names "the passing test" as a route that meets a criterion. The model now
reads a passing test as evidence in step 1 and never reaches step 2. The
evidence is the "test passed" sentence in three of five replies. Five
identical failures are not variance.

**Fix line.** In step 1 of `rota/roles/prompts/critic/review.md`, write that
the test route holds only for a test that step 2 finds encodes its criterion,
and put step 2's question before any pass that names a test.

## 3. L1-CR-a-kept-behaviour-passes-by-its-kept-line (new today)

**Assertion.** One `verdicts` write with `"result": "pass"` and `kept:`, or
with `"result": "pass"` and `test:`, 4 of 5 runs. Every run: "none of the
permitted answers was given". Runs 1, 3 and 5 wrote a verdict without the
route. Runs 2 and 4 wrote nothing. Runs 2, 3 and 4 sent a challenge to the
Tester. Run 5 sent a question to the Terminologist.

**Calls.** llama3.1:8b thrashes. Runs 1, 2 and 4 copy the test bodies as
lines (`'assert send(msg) is True'`), which the tool refuses as "not an added
line of the diff". Runs 1, 2 and 4 write their own tool results, and the
stream stops at "the invented result `OK verdicts.claim_encodes ->`". The
model flips `claim_encodes` from True to False, and the tool refuses the
reversal. Run 3 makes 41 calls. Run 4 once writes
`'kept:     with smtplib.SMTP(host, port) as smtp:'` for `<c3>`, which is the
correct form, but in the same call it gives `return True` for `<c1>` and then
loops. Run 5 gives `return True` for both criteria.

**History.** One group only: 2026-10-29 14:36, llama3.1:8b, 3fef5a81, 0/5
live. No other run. `plans/f344-review-p1.md` and `plans/` hold no
measurement of this case on any model.

**Cause: the model (llama3.1:8b).** The case is unpinned, so it ran on the
default model. The failure modes are invented tool results, copied test
bodies and loops. Those are capability faults of the model, and the other
Critic cases show none of them on qwen3:8b. The case still has no measure
on qwen3:8b or on gemma3:12b, so the Critic land is not yet tested by it.

**Fix line.** No land fix. Re-record with `ROTA_MODEL=qwen3:8b`, or pin the
case to the Critic's profile model, before the case judges the land.

## 4. L1-LI-a-reply-reaches-the-desk-that-asked

**Assertion.** One message to `terminologist`, verb `relay`, refs include
`<c1>`, 3 of 5 runs. Every run: "message m1 missing refs {'c_…'}". The
message exists and its stored refs lack the criterion.

**Calls.** All five runs make the same two calls:
`rulings.rule(rulings={"<c1>": "approve"}, words="the tests should check the
tip amount and the total, both printed")`, then
`msg.relay_terminologist(refs=["e_m_in", "<c1>"], round_no=0)`. The writes
are `rulings: 1` and `ruled_refs: 1`. The green qwen3:8b run of 2026-10-26
17:53 made the same `rulings.rule` call but relayed `refs=["<c1>"]` only, and
wrote `rulings: 1` with no `ruled_refs` row.

**History:**

| Time | Model | Prompt hash | Result |
|---|---|---|---|
| 2026-10-29 14:42 | gemma4:12b-it-qat | aae0abc3 | 0/5 replay |
| 2026-10-29 07:41 | gemma4:12b-it-qat | aae0abc3 | 0/5 live |
| 2026-10-26 17:53 | qwen3:8b | 3e928dc6 | 5/5 replay |
| 2026-10-26 08:06 to 08:55 | qwen3:8b | 3e928dc6 | 10/10 replay |
| 2026-10-26 06:39 to 07:21 | qwen3:8b | 3e928dc6 | 15/15 replay |

**Cause: the model (gemma4:12b-it-qat against qwen3:8b), not the R land.**
The case uses `prompt: answering`. R changed `landing.md`, `landing.base.md`
and `landing.tools` only. The prompt hash is aae0abc3 before and after R, and
the 14:42 run is a replay of the 07:41 cassettes, so the system text did not
change. The red starts on the first gemma4 run at 07:41, after the seat moved
to gemma4 (102adb0d, frame 345 pass 4) and before both lands. Five identical
replies are not variance.

**Open point.** The stored refs drop `<c1>` although the call names it. The
difference from qwen is the extra entry ref `e_m_in` and the new `ruled_refs`
write. Relay and ruled-refs code changed between 2026-10-26 and today
(f920fd39, 9e4d7c6c, ed7d00a8). This read did not trace which code drops
`<c1>`, and did not replay the qwen reply against today's code. So a code
part of the cause is not excluded.

**Fix line.** No land fix. First find where `msg.relay_terminologist` loses
`<c1>` when the refs carry an entry id, before any brief change for gemma4.

## The five other reds

Last run before 2026-10-29, from `case_runs`:

- **L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist**: red
  before. 0/10 on qwen3:8b at 26d3fd0c, 2026-10-28 01:37, and 0/5 in every
  group since 2026-10-26.
- **L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about**: green
  before at the threshold. 3/5 on qwen3:8b at 1128cdfd, 2026-10-26 18:02.
  Red in all six runs today (qwen3:8b at 05:43 and 06:37, gemma4 from 07:42).
- **L1-LI-a-new-request-on-another-function-takes-no-supersedes**: green
  before. 10/10 on qwen3:8b at 3b708d0a, 2026-10-28 01:34. 3/5 on gemma4 at
  07:58 today, the same hash and the same result at 14:52.
- **L1-LI-drop-both-examples-is-a-drop-of-both-rows**: no run before today.
  Today: 0/5 qwen3:8b 05:44, 5/5 qwen3:8b 06:37, then 0/5 on gemma4 in four
  groups.
- **L1-LI-two-questions-at-most-from-three-reports**: green before. 10/10 on
  qwen3:8b at 16719916, 2026-10-28 01:34. 0/5 on gemma4 at 07:46 today, the
  same hash, and the 14:51 run is a replay.
