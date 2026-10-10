# Frame 193, the second request: interviews of the two Liaison seats at night 138's request boundaries

Date: 2026-10-10. Night: 138, database `.rota/clickI.db` (live, opened
read-only). Tool: `probes/frame37/interview_turn.py`, no `--model`, no
`--think`, `--timeout 900`. Workflow: the rota workflow, the Liaison seat.

- s270: turn 1 of message (converse), role liaison, model qwen3:8b, think
  False, num_ctx 16384. Run 12:44:02 to 12:44:15, the tool reports 13s.
- s353: turn 1 of message (converse), role liaison, model qwen3:8b, think
  False, num_ctx 16384. Run 12:44:19 to 12:44:36, the tool reports 17s.

Both sessions have one turn. Both have the same system prompt.

## s270, the second request m_p2

The prompt held (quoted from the turn, 4 of 12 lines allowed):

```
"principal_said": "Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting.",
  "current_request": {
    "statement": "s1",
    "text": "Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline."
```

Recorded completion: `TOOL: msg.confirm_principal(refs=["s1"])`.

Tool header, verbatim:

```
interview s270 turn 1 of message (converse), role liaison, model qwen3:8b, think False, num_ctx 16384, prompt 5213 chars, 2 calls on record
13s, prompt 3942 tok, out 435 tok, thinking 0 chars
```

Questions, verbatim:

1. What did the `principal_said` field say, in its own words?
2. Which statement ids did the pre-run `brief.list` return, and what was each statement about?
3. Did the words in `principal_said` describe the same change as statement s1, or a different change? Name the function each one is about.
4. The first of the three tests in the brief lists words such as "add", "let people", "make it". Did `principal_said` start with one of those words, and which one?
5. Which line of the brief or of the prompt did you read as the instruction to call `msg.confirm_principal` with s1? Quote it.
6. Did you read a line in the brief about when to call `brief.segment`, and a line about a request on another thing with no `supersedes`? Quote each one if you can.
7. Did `current_request` naming s1, or the `recent_chat` turns about echo_json, tell you that the new words belonged to s1?
8. What in the prompt, if changed or removed, would have led you to call `brief.segment` on the new words?

Answers, verbatim as the tool printed them:

```
1. The `principal_said` field said: "Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting."

2. The pre-run `brief.list` returned one statement id: `s1`. The statement was about: "Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline."

3. The words in `principal_said` described a different change from statement s1. The `principal_said` field was about adding a `default_on_eof` flag to the `confirm()` function, while statement s1 was about adding an `echo_json(obj)` helper. They are about different functions.

4. The `principal_said` did not start with one of the words such as "add", "let people", or "make it". It started with "Let", which is part of a directive, but not one of the listed words.

5. The line in the brief that instructed to call `msg.confirm_principal` with s1 was: "The principal's words are already in the transcript � recorded verbatim before you woke, because the transcript is the one un-interpreted thing in the system and nothing should retype it. Its id is `entry_id` in the message below."

6. The brief did not mention when to call `brief.segment`. It did, however, mention a line about a request on another thing with no `supersedes`: "When the wake has no `current_request`, leave `supersedes` out."

7. Yes, `current_request` naming s1 and the `recent_chat` turns about `echo_json` told me that the new words belonged to s1. The `current_request` was about adding the `echo_json(obj)` helper, and the `recent_chat` turns were about the same change.

8. If the prompt had included a new statement about adding the `echo_json(obj)` helper, or if the `current_request` had not named s1, I would have called `brief.segment` on the new words.
```

Reading against the record (observed: the turn of s270 in `.rota/clickI.db`, 2026-10-10):

- Answers 1, 2 and 3 match the prompt. The seat read the new words, read s1, and named two different functions.
- Answer 4 matches the brief's letter. Test 1 lists "let people", not "let". The seat did not count "Let confirm()" as a work word.
- Answer 5 quotes a line that says nothing about `msg.confirm_principal`. No line of the brief tells the seat to confirm s1.
- Answer 6 contradicts the brief. The brief says "Work means segment-and-confirm" and shows a `brief.segment` example. The seat quoted the no-`current_request` line, not the "another thing" sentence.
- Answer 7 names `current_request` and the echo_json `recent_chat` as the inputs that tied the new words to s1.
- The fact read and not acted on: the seat said that the new words are about `confirm()` and s1 is about `echo_json`, and it still confirmed s1.

## s353, the third request m_p3

The prompt held (quoted from the turn, 3 of 12 lines allowed):

```
"principal_said": "Give version_option a show_python flag that appends the running Python version to the message.",
      "text": "Line 1 is wrong because it describes the JSON printing helper, but I am working on the version option change now, which adds a flag that appends the running Python version to the message. The Python version should come from the interpreter's version info as major.minor.micro."
    "statement": "s1",
```

Recorded completion:
`TOOL: brief.segment(id='s2', span_start=0, span_end=123, text='Give version_option a show_python flag that appends the running Python version to the message.', span_entry='e_p3', supersedes='s1')`
and `TOOL: msg.confirm_principal(refs=['s2'])`.

Tool header, verbatim:

```
interview s353 turn 1 of message (converse), role liaison, model qwen3:8b, think False, num_ctx 16384, prompt 4802 chars, 3 calls on record
17s, prompt 3838 tok, out 314 tok, thinking 0 chars
```

Questions, verbatim:

1. What did the `principal_said` field say, in its own words?
2. What did the last turn of `recent_chat` say, and who said it?
3. Was the new request about the same function as statement s1? Name the function each one is about.
4. Which line of the brief did you read as the instruction to set `supersedes` to s1? Quote it.
5. The brief's example of a follow-up names `version_option`. Did that example tell you that a request about `version_option` takes `supersedes`?
6. The same paragraph says that a request about another thing is a new request with no `supersedes`. Did you read that sentence, and which thing did you compare the new words against?
7. Did `current_request` naming s1 tell you that the new words belonged to s1?
8. What in the prompt, if changed or removed, would have led you to leave `supersedes` out?

Answers, verbatim as the tool printed them:

```
1. The `principal_said` field said: "Give version_option a show_python flag that appends the running Python version to the message."

2. The last turn of `recent_chat` said: "Line 1 is wrong because it describes the JSON printing helper, but I am working on the version option change now, which adds a flag that appends the running Python version to the message. The Python version should come from the interpreter's version info as major.minor.micro." and it was said by the principal.

3. The new request was not about the same function as statement s1. Statement s1 was about adding an `echo_json(obj)` helper, while the new request was about adding a `show_python` flag to `version_option`.

4. The line of the brief that instructed to set `supersedes` to s1 was: "After a request about `version_option`, 'also show the version as major.minor' is about the same thing, so it takes `supersedes`."

5. Yes, the example told me that a request about `version_option` takes `supersedes`.

6. Yes, I read that sentence. The new words were compared against the request about `version_option`.

7. Yes, `current_request` naming s1 told me that the new words belonged to s1.

8. If the new words were about a different function or a new request that was not a follow-up to s1, then `supersedes` would have been left out.
```

Reading against the record (observed: the turn of s353 in `.rota/clickI.db`, 2026-10-10):

- Answers 1, 2 and 3 match the prompt. The seat named `echo_json` for s1 and `version_option` for the new words.
- Answer 4 quotes the brief's example exactly. The seat took the example as the instruction.
- Answers 5 and 6 say that the seat compared the new words against the brief's example request about `version_option`, not against s1.
- Answer 7 names `current_request` as an input that tied the new words to s1.
- Answer 8 states the rule that the seat broke. The new words were about a different function, and the seat said so in answer 3.
- The fact read and not acted on: s1 is about `echo_json`, a different function, and the seat still set `supersedes='s1'`.

## What would move the seat

(reasoned: from the interviews, counted over both seats' answers)

1. `current_request` naming s1: named 3 times as the input that tied the new words to s1 (s270 answers 7 and 8, s353 answer 7). s270 said that a wake without s1 in `current_request` would have led to `brief.segment`.
2. The `version_option` example in the `supersedes` paragraph: named 3 times by s353 (answers 4, 5, 6). The seat compared against the example's subject, not against the `current_request` text.
3. `recent_chat` about echo_json: named once (s270 answer 7).
4. The work-word list in test 1: named once (s270 answer 4). "let people" did not match "Let confirm()".

Neither seat named a change in its own answer 8 that the prompt did not already hold. Both seats stated the difference of function and did not use it. The comparison against `current_request` is the step that neither seat made.
