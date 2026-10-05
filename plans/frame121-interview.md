# Frame 121, three runner notes tell the seat a wrong thing: the interviews

Rota workflow. Seven calls of `probes/frame37/interview_turn.py` on 2026-10-05, 03:07 to 03:15, on the Titan's server, port 11435. Each call replays one recorded turn at temperature 0 with the session's own model, window and think pin (`think False`, as the runner sends when nobody pins one). The probe adds the questions after the prompt. An answer is a report about inputs. Each answer is read against the prompt below it.

Two properties of the probe apply to every call (reasoned: `interview_turn.py`, lines 55-75). The probe prints the whole session's call list, later turns included. The probe's own preamble follows the prompt, so a question that names "the sentence after X" can land on the preamble.

The question files and the raw output of each call are in the scratchpad of session e6218d79, `f121/q_*.txt` and `f121/call*_*.txt`.

The runner's sites (observed: `rota/core/runner.py` at e23efd2, 2026-10-05):

- The repeat answer, `runner.py:3393-3395`: `ERROR <call>: asked three times this session and the answer has not changed; not answered again. The answer is in this prompt.` Night 115 printed `If the window dropped it, ask once more and it is served again.` in place of the last sentence.
- The serve cap refusal, `runner.py:3331-3345`: `ERROR <call>: served three times this session, and the window took it each time; not served again. Ask <call> for a narrower span, or finish without it.`
- The cut note, `_render_cut`, `runner.py:570-586`, with `_WAKE_CUT_CALL` at `runner.py:562`: `CUT your wake: N of M characters are not shown. Nothing returns a wake. Ask by name for the reads you need.`
- The push header, `runner.py:404-406`: `Already run for you, with the results below. Calling any of these again returns the same thing and costs you a turn:`

## A. The repeat answer, the changed wording (night 115, s33, seq 6)

- Database: `.rota/clickI_night115.db`. Session s33, Vision Keeper, `tick:reconcile`, `qwen3:8b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night115.db --sid s33 --seq 6 --questions f121/q_repeat.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 1: 64 s, prompt 5,872 tokens, output 178 tokens.

Seq 6 is the turn the frame names (observed: the prompt and the completion, 2026-10-05). The prompt of 22,502 characters equals night 113's s33 seq 6 except one line (observed: a line diff, 2026-10-05). The completion repeats the whole earlier reply: four `code.probe` calls, each followed by an `OK code.probe -> []` that the seat wrote itself, a `code.source`, four `ledger.log` and a `surveys.attest`.

**Correction to the frame's premise.** The prompt holds no eviction notice. `dropped to fit the window` is absent. The word "dropped" appears only in the new sentence (observed: a substring search, 2026-10-05). The real result of `code.probe(pattern='defines_commands_and_options')` stands once, at character 8,209, as `OK code.probe -> []` in the runner's results block of turn 4. Every other `OK code.probe -> []` in the prompt is a line the seat wrote in its own reply.

The runner's note at the tail of the prompt, exactly:

```
You wrote tool results into your own reply -- the lines beginning `OK ...` or `ERROR ...`. Those did not come from me and nothing behind them ran. Only results I send back are real. Send the calls alone and stop; I will answer.
ERROR code.probe: asked three times this session and the answer has not changed; not answered again. If the window dropped it, ask once more and it is served again.
NOT RUN, because you wrote a tool result of your own ahead of them: code.probe(pattern='how_it_works'), [... the other nine calls ...]. The real results of the calls that did run follow. Send the rest again with those results in view.
```

Questions (`q_repeat.txt`, used for A, B1, B2 and B3):

1. Quote the last ERROR line the runner sent you, exactly as it appears in your prompt.
2. In your own words, what did the runner's last message say?
3. Was the result of the call that ERROR line names in front of you? If yes, quote its first line and say where in the prompt it stood. If no, say `not shown`.
4. What did the sentence after "not answered again." tell you to do?
5. What would you need to see in your prompt to stop asking for the same call?

Answers, verbatim:

```
1. "ERROR code.probe: asked three times this session and the answer has not changed; not answered again."
2. The runner's last message indicated that the `code.probe` call had been asked three times during the session and the result had not changed, so it would not be answered again.
3. Yes, the result of the call that the ERROR line names was in front of me. The first line was "OK code.probe -> []" and it stood in the prompt as part of the tool call results.
4. The sentence after "not answered again." told me to ask once more if I needed the result, and it would be served again.
5. I would need to see the result of the `code.probe` call again in my prompt, or a confirmation that the result has changed, to stop asking for the same call.
```

What the answers show:

- The seat read the new sentence as an unconditional invitation: "ask once more if I needed the result". The condition "If the window dropped it" is gone from its report (observed: the answer of call 1, 2026-10-05).
- The seat knew the result was in front of it, `OK code.probe -> []`. So the repeat did not come from a missing result (observed: the answer of call 1, 2026-10-05).
- The quote in answer 1 drops the second sentence. The prompt holds it on the same line (observed: the prompt against the answer of call 1, 2026-10-05).
- Answer 5 asks for "the result ... again in my prompt". A seat that reads an invitation and wants a fresh copy repeats the call (reasoned: answers 4 and 5 together).

## B. The repeat answer, the old wording

Three turns. B2 is the exact pair of A. B1 and B3 hold the old sentence beside the eviction notice.

### B2. Night 113, s33, seq 6: the old wording, the seat did not repeat

- Database: `.rota/clickI_night113.db`. Session s33, Vision Keeper, `tick:reconcile`, `qwen3:8b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night113.db --sid s33 --seq 6 --questions f121/q_repeat.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 2: 21 s, prompt 5,884 tokens, output 210 tokens.

The prompt equals A's except one line, and it holds no eviction notice. The completion is one call, `surveys.attest(outcome="found", ...)`. The note, exactly:

```
ERROR code.probe: asked three times this session and the answer has not changed; not answered again. The answer is in this prompt.
NOT RUN, because you wrote a tool result of your own ahead of them: [...]
```

Answers, verbatim:

```
1. "ERROR code.probe: asked three times this session and the answer has not changed; not answered again. The answer is in this prompt."
2. The runner's last message indicated that the `code.probe` call was asked three times during the session and the result did not change, so it would not be answered again. It also mentioned that the answer is already in the prompt.
3. Yes, the result of the call that the ERROR line names was in front of me. The first line is "ERROR code.probe: asked three times this session and the answer has not changed; not answered again. The answer is in this prompt." It stood as the last line in the prompt.
4. The sentence after "not answered again." told me to stop asking for the same call and to answer only from what was actually in front of me.
5. I would need to see a new result or a different response from the `code.probe` call in my prompt to stop asking for the same call.
```

What the answers show:

- With the old wording, the seat read the line as "stop asking for the same call" (observed: the answer of call 2, 2026-10-05). With the new wording, on an equal prompt, it read "ask once more" (observed: the answer of call 1, 2026-10-05).
- Answer 3 names the refusal line itself as the result. The real result, `OK code.probe -> []`, is not quoted. The refusal is also not the last line: the `NOT RUN` line follows it (observed: the prompt against the answer of call 2, 2026-10-05).
- Answer 4 mixes the note with the probe's preamble, "answer only from what was actually in front of me" (reasoned: the preamble follows the prompt and holds those words).

### B1. Night 119, s32, seq 11: the old wording beside the eviction notice, the seat repeated

- Database: `.rota/clickI_night119.db`. Session s32, Vision Keeper, `tick:reconcile`, `qwen3:8b`, `num_ctx` 16384, think False. The prompt equals night 113's s32 seq 11 byte for byte (observed: a comparison, 2026-10-05).
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night119.db --sid s32 --seq 11 --questions f121/q_repeat.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 3: 72 s, prompt 8,559 tokens, output 217 tokens.

The prompt holds `[7 earlier exchange(s) dropped to fit the window. ...]` at character 8,065. Every `OK code.probe -> [{"grain": "src/click/core.py::ParameterSource", ...` in the prompt stands inside the seat's own replies. The last of those copies is cut by `CUT this exchange: 15,616 of 23,579 characters are not shown.` The runner's own answer, at character 12,219, is `OK code.probe -> unchanged since you asked earlier this session. What code.probe returned then still stands.` (observed: the prompt, 2026-10-05). The completion repeats `code.probe(pattern='ParameterSource')` and `code.source(path='src/click/core.py', start=168, end=205)` with invented results. The tail of the prompt, exactly:

```
ERROR reply cut: your reply was cut at the output budget before it ended, so the last call did not run and nothing was written. Send less in one reply: one or two calls, then read their results. For a long file, write the span you changed with start and end copied from code.source, not the whole file
You wrote tool results into your own reply -- the lines beginning `OK ...` or `ERROR ...`. Those did not come from me and nothing behind them ran. Only results I send back are real. Send the calls alone and stop; I will answer.
OK code.source -> unchanged since you asked earlier this session. What code.source returned then still stands.
NOT RUN, because you wrote a tool result of your own ahead of them: code.probe(pattern='ParameterSource'), [...]. The real results of the calls that did run follow. Send the rest again with those results in view.

TOOL: code.probe(pattern='ParameterSource')

ERROR code.probe: asked three times this session and the answer has not changed; not answered again. The answer is in this prompt.
```

Answers, verbatim:

```
1. "ERROR reply cut: your reply was cut at the output budget before it ended, so the last call did not run and nothing was written. Send less in one reply: one or two calls, then read their results. For a long file, write the span you changed with start and end copied from code.source, not the whole file"
2. The runner's last message indicated that my reply was cut off due to the output budget limit, and advised me to send fewer calls at once, focusing on one or two calls and reading their results.
3. The result of the call that the ERROR line names was not in front of me. It was not shown.
4. The sentence after "not answered again." told me to answer only from what was actually in front of me and to say I do not know rather than reconstructing something plausible. It also instructed me to call no tool.
5. To stop asking for the same call, I would need to see a result or confirmation that the call was processed successfully and that the output was fully received.
```

What the answers show:

- The seat named the `ERROR reply cut` line as the last runner message. The repeat refusal, which is the real last line, did not register (observed: the prompt against the answer of call 3, 2026-10-05).
- The seat read its last call as "did not run", from `the last call did not run`. Its answer 5 asks for proof "that the call was processed successfully" (observed: the answer of call 3, 2026-10-05).
- On the reading the seat gives, the result was "not shown". The prompt holds only the seat's own copies, the last one cut, and the real result was dropped by the eviction. So `The answer is in this prompt.` was false in this turn for the real result (observed: the prompt, 2026-10-05).
- Answer 4 lands on the probe's preamble (reasoned: as in B2).

### B3. Night 113, s155, seq 8: the old wording beside the eviction notice, the seat did not repeat

- Database: `.rota/clickI_night113.db`. Session s155, Developer, `tick:tests_failing`, `qwen3.5:9b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night113.db --sid s155 --seq 8 --questions f121/q_repeat.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 7: 66 s, prompt 9,012 tokens, output 172 tokens.

The prompt holds `[3 earlier exchange(s) dropped to fit the window. ...]` at character 18,204. The runner's result of `code.source(path='src/click/utils.py', start=674, end=690)` follows it at character 18,389 (observed: the prompt, 2026-10-05). The next call on record is a `code.write`. The tail of the prompt, exactly:

```
You wrote tool results into your own reply -- the lines beginning `OK ...` or `ERROR ...`. Those did not come from me and nothing behind them ran. Only results I send back are real. Send the calls alone and stop; I will answer.
ERROR code.source(path='src/click/utils.py'): asked three times this session and the answer has not changed; not answered again. The answer is in this prompt.
OK code.source -> unchanged since you asked earlier this session. What code.source returned then still stands.
OK code.source -> unchanged since you asked earlier this session. What code.source returned then still stands.
OK code.source -> unchanged since you asked earlier this session. What code.source returned then still stands.
```

Answers, verbatim:

```
1. ERROR code.source(path='src/click/utils.py'): asked three times this session and the answer has not changed; not answered again. The answer is in this prompt.

2. The runner's last message said that I had already called `code.source` on `src/click/utils.py` three times in this session, the result hasn't changed, so I should stop asking for it because the answer is already available in the current prompt.

3. not shown

4. It told me to stop asking for the same call and instead use the information that was already provided in the prompt.

5. To stop asking for the same call, I would need to see a message indicating that the result of that call has been answered or is available in the current context, rather than being marked as an error due to repeated requests.
```

What the answers show:

- The seat read the old sentence as "stop asking ... and instead use the information that was already provided" (observed: the answer of call 7, 2026-10-05).
- The seat said the result was "not shown". A utils.py read, 674-690, stands in the prompt after the eviction notice. The refusal names no span, so the refused key may be a different span (observed: the prompt against the answer of call 7, 2026-10-05).
- So the seat acted on "stop", not on a result it could find. It wrote a change and did not repeat (reasoned: answers 3 and 4 with the completion).
- Answer 5 asks that the result stand in the line itself, "answered or ... available", and not as an error (observed: the answer of call 7, 2026-10-05).

## C. `CUT your wake` on a cut reply (night 119, s263, seq 5)

- Database: `.rota/clickI_night119.db`. Session s263, Developer, `message` (answer), `qwen3.5:9b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night119.db --sid s263 --seq 5 --questions f121/q_cut.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 4: 71 s, prompt 6,775 tokens, output 195 tokens.

Seq 5 is the brief's "turn 4": its prompt is the retry after the reply of seq 4, 38,567 characters of prose (observed: the completion lengths, 2026-10-05). s167 was not used: its `CUT your wake` cuts a real wake of 22,178 characters, not a reply. The completion of seq 5 is prose again, with no call. The note at the tail, exactly:

```
CUT your wake: 34,567 of 38,567 characters are not shown. Nothing returns a wake. Ask by name for the reads you need.

ERROR reply cut: your reply was cut at the output budget before it ended, so the last call did not run and nothing was written. Send less in one reply: one or two calls, then read their results. For a long file, write the span you changed with start and end copied from code.source, not the whole file Send calls, or end with one sentence.
```

Questions (`q_cut.txt`):

1. Quote the line in your prompt that begins `CUT`, exactly.
2. What text was cut? Say whose text it was: the runner's, a tool's, or yours.
3. What did the cut note tell you to do next?
4. Quote the ERROR line that follows the cut note, exactly.
5. Which call, if any, did these two notes name for your next reply? Quote it, or say `none`.

Answers, verbatim:

```
1. CUT your wake: 34,567 of 38,567 characters are not shown. Nothing returns a wake. Ask by name for the reads you need.
2. The text cut was mine (the developer's reply).
3. The cut note told me to send less in one reply: one or two calls, then read their results. For a long file, write the span you changed with start and end copied from code.source, not the whole file Send calls, or end with one sentence.
4. ERROR reply cut: your reply was cut at the output budget before it ended, so the last call did not run and nothing was written. Send less in one reply: one or two calls, then read their results. For a long file, write the span you changed with start and end copied from code.source, not the whole file Send calls, or end with one sentence.
5. none
```

What the answers show:

- The seat knew the cut text was its own reply, although the note says "your wake" (observed: the answer of call 4, 2026-10-05). Question 2 offered "yours" as an option, so the answer may lean on the question (reasoned: the question's form).
- The seat did not report the cut note's own instruction, "Ask by name for the reads you need". It reported the ERROR line's instruction as the cut note's (observed: answer 3 against the prompt, call 4, 2026-10-05).
- The seat found no call named for its next reply: "none" (observed: answer 5 of call 4, 2026-10-05). The completion then sent prose with no call.

## D. The serve cap refusal (night 119, s260, seq 13)

- Database: `.rota/clickI_night119.db`. Session s260, Developer, `tick:tests_failing` attempt 4, `qwen3.5:9b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night119.db --sid s260 --seq 13 --questions f121/q_cap.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 5: 60 s, prompt 7,348 tokens, output 220 tokens.

The refusal stands in 4 turns of night 114 (s208, Terminologist) and in 24 turns of night 119 (s260 and s261, Developers). Nights 113 and 115 hold none (observed: a LIKE search, 2026-10-05). Seq 13 is s260's first. The prompt holds an eviction notice at character 13,691 and no test body (observed: the prompt, 2026-10-05). The completion is prose that infers the tests from criteria. The note at the tail, exactly:

```
TOOL: tests.load(batch_id='bg_3')

ERROR tests.load: served three times this session, and the window took it each time; not served again. Ask tests.load for a narrower span, or finish without it.
```

`tests.load` takes `batch_id` only (observed: `rota/roles/api.py:5649`, 2026-10-05). It has no span.

Questions (`q_cap.txt`):

1. Quote the last ERROR line in your prompt, exactly.
2. In your own words, what did that refusal say?
3. What step did the refusal name for you to take next?
4. Which arguments does tests.load take, as your prompt shows them? Quote them, or say `not shown`.
5. Were the bodies of the failing tests in front of you? If yes, say where in the prompt. If no, say `not shown`.

Answers, verbatim:

```
1. "ERROR tests.load: served three times this session, and the window took it each time; not served again. Ask tests.load for a narrower span, or finish without it."
2. The refusal stated that `tests.load` has already been called three times in this session and the results were consumed by the window limits, so it cannot be called again. It offered two paths: ask for a narrower span of tests, or finish the work without loading them.
3. The refusal named asking for a narrower span of tests as the next step to take if I needed more test data.
4. `tests.load` takes one argument: `batch_id`. This is shown in the prompt's tool list: `TOOL: tests.load(batch_id=None)`.
5. No, the bodies of the failing tests were not in front of me. The prompt only listed their IDs and paths (e.g., `"id": "tst_v1", "path": "tests/test_version_option.py"`), but did not include the actual test code or assertions.
```

What the answers show:

- The seat took "a narrower span of tests" as the step, and it knew `tests.load` takes `batch_id` only. So the named step has no argument the seat can send (observed: answers 3 and 4 of call 5, 2026-10-05).
- Answer 4 quotes `TOOL: tests.load(batch_id=None)`. The prompt holds `tests.load(batch_id='bg_3')` and no `batch_id=None` (observed: a substring search, 2026-10-05). The quote is reconstructed.
- The seat knew the test bodies were not in front of it (observed: answer 5 of call 5, 2026-10-05). The only open path the note leaves is "finish without it", and the completion inferred the tests from the criteria (reasoned: answers 3 to 5 with the completion).

## E. The header "returns the same thing" (night 119, s261, seq 1)

- Database: `.rota/clickI_night119.db`. Session s261, Developer, `tick:tests_failing` attempt 4, `qwen3.5:9b`, `num_ctx` 16384, think False.
- Command: `python probes/frame37/interview_turn.py --db .rota/clickI_night119.db --sid s261 --seq 1 --questions f121/q_header.txt --host http://127.0.0.1:11435 --timeout 900`
- Call 6: 50 s, prompt 6,441 tokens, output 162 tokens.

The pushed `[tests.load]` block starts at character 15,099 as the shaped dict: the thread, `after these`, then `the batch's tests, not passing`. The wake is cut inside the block at 18,182 characters (observed: the prompt, 2026-10-05). The completion calls `tests.load(batch_id='bg_3')` first. At seq 2 that call returned the raw list, `[{"id": "tst_v1", "criterion_id": ..., "body": ...`, with no thread and no `after these` (observed: the seq 2 prompt, 2026-10-05). The shaping is `runner.py:2298-2345`, and it applies to the push only. The notes, exactly:

```
Already run for you, with the results below. Calling any of these again returns the same thing and costs you a turn:
[...]
CUT your wake: 26,137 of 44,201 characters are not shown. Nothing returns a wake. Ask by name for the reads you need.
```

Questions (`q_header.txt`):

1. Quote the header sentence above the results that were already run for you, exactly.
2. What did that sentence say a repeat call to one of those returns?
3. Was the result of tests.load in front of you? If yes, quote its first 100 characters and say whether it was complete or cut.
4. Quote any line in your prompt that begins `CUT`, exactly, or say `none`.
5. What did you expect a new call to tests.load to return?

Answers, verbatim:

```
1. "Already run for you, with the results below. Calling any of these again returns the same thing and costs you a turn:"
2. It said a repeat call returns the same thing and costs a turn.
3. Yes, it was in front of me. The first 100 characters are: `{"challenges and escalations on these tests": [{"id`: It was cut (the output ends with "CUT your wake...").
4. CUT your wake: 26,137 of 44,201 characters are not shown. Nothing returns a wake. Ask by name for the reads you need.
5. I expected it to return the same data as before, since the prompt says calling again returns the same thing.
```

What the answers show:

- The seat read the header correctly and knew that its `tests.load` result was cut (observed: answers 2 and 3 of call 6, 2026-10-05).
- The seat expected "the same data as before" from a repeat call. The repeat returned raw rows with bodies, not the shaped dict (observed: answer 5 against the seq 2 prompt, 2026-10-05).
- Two notes stand in one prompt. The header says a repeat returns the same thing. The cut note says "Ask by name for the reads you need". The seat asked by name for a result it knew was cut (reasoned: answers 3 to 5 with the completion).
- The header's claim was false for this call, and the seat's call bought the bodies the cut had taken (observed: the seq 2 prompt, 2026-10-05).

## What the answers say for each note

1. **The repeat answer.** With `The answer is in this prompt.`, two seats read "stop asking" and moved on (calls 2 and 7). With `If the window dropped it, ask once more and it is served again.`, the seat read "ask once more" and dropped the condition (call 1). Only one of the four seats quoted a result line, `OK code.probe -> []`, and the seat's own copies carry the same text (call 1). The others quoted the refusal line or said "not shown" (calls 2, 3, 7). The answers ask for a wording with no conditional invitation to call again. They ask for a line that stands as an answer and not as an error (call 7, answer 5). They also ask for a line that holds the result itself or points to one line the seat can find.
2. **The repeat answer beside `ERROR reply cut`.** In call 3 the seat read only the `ERROR reply cut` line and believed its call "did not run". The answers ask that a refusal of a repeat does not stand after a line that says the last call did not run, or that the two lines agree.
3. **The serve cap refusal.** The seat read the named step, "a narrower span", and knew `tests.load` has no span (call 5). The answers ask that the refusal name a step that the refused call can take, or name a different call.
4. **`CUT your wake` on a cut reply.** The seat knew the cut text was its own reply despite "your wake". It found no next call in the two notes, and it reported the ERROR line's instruction as the cut note's (call 4). The answers ask that the cut note name the seat's reply as the cut text, and that the notes name one next call.
5. **The header "returns the same thing".** The seat took the header as true and called again anyway, because the result was cut and the cut note invited a read by name (call 6). The answers ask that the header not claim an equal result where the call returns a different shape, and that the header and the cut note do not give opposite instructions on one block.
