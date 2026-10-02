# Frame 110, the Tester interview in its own context

Written by an Opus agent for frame 110, 2026-10-02 15:04. Meta workflow: the
build session interviews the rota workflow's Tester seat.

## The case and the run

- Case: `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`
  in `tests/rota/cases/l1_tester.yaml`.
- Run: `case_runs` rowid 404452, run_no 5, live 1, at 2026-10-02T14:58:41,
  seq 302108, prompt_hash `fd35103e456acc3d`, system_hash `88855c15abc89daf`.
  Problems: "expected writes to tests (1..1), got 0".
- Turn: the first model call, cassette rowid 46758, key
  `df8f0e5097c4ad48dde94d50fd1a7496`. The case seeds `batches.expect`,
  `criteria.load` and `tests.consult` into the user text. The model then
  calls `msg.answer_developer`. Rows 46759 and 46760 are the retry after the
  bare-string `refs` error and the prose close.
- Message shape: one system message and one user message, as
  `OllamaBackend.complete` in `rota/llm/llm.py` sends them. Protocol `text`,
  so no native `tools` field. The tools are listed in the system text.

## Pins

`qwen3:8b`, temperature 0.0, num_ctx 12288, num_predict 8192, think false,
`/api/chat` on `http://localhost:11434`, stream false. The live call goes
direct to Ollama and does not touch the cassette layer. The prompt was
2134 tokens, so the window does not cut it.

## Replay

The replay matched byte for byte (observed: 2026-10-02 15:04). The live
completion and the recorded completion are both:

```
TOOL: msg.answer_developer(refs, quotes="echo_json prints the value as JSON on one line, with no indentation", round_no=0)
```

The interview appends this completion as the assistant turn and asks each
question as the next user message. No answer to a to d carried a tool call,
so no "Answer in prose only." retry was needed.

## Questions and answers, verbatim

**a.** "Stop. Do not call a tool. In two sentences, what did the challenge
ask you to decide?"

> The challenge asked whether the test for criterion `c_6f5fde` correctly encodes the criterion's requirements, specifically whether the test accurately checks that `echo_json` prints the value as JSON on one line with no indentation.

**b.** "The test's last run ended in `TypeError: An asyncio.Future, a
coroutine or an awaitable is required` before any assertion. Whose fault is
that, the test's or the code's, and why?"

> The error is the test's fault. The test calls `asyncio.run(echo_json(...))` but `echo_json` is not an awaitable or a coroutine. The test assumes `echo_json` is async, but the function may not be defined as such, leading to the TypeError. The test should either call `echo_json` synchronously or ensure it is properly defined as an async function.

**c.** "Your instructions begin: 'First, if the last run failed before any
assertion ran, read the failure and the called code with code.source, and
fix the call line.' What did that sentence mean to you, and why did you not
call code.source or tests.encode?"

> The sentence meant that if a test fails due to an error in the code it calls (before any assertion is reached), I should first inspect the called code using `code.source` to understand why the error occurred and then fix the test or the code accordingly. I did not call `code.source` or `tests.encode` because the error was clearly due to the test calling a non-awaitable function, and the test's structure was incorrect, not the code's. The test needed to be adjusted to match the function's actual behavior, not the code itself.

**d.** "What would have made you change the test instead of answering the
Developer? Name the exact words or tool result you would have needed."

> I would have changed the test if the `code.source` result showed that `echo_json` is indeed an async function, and the test was incorrectly structured (e.g., missing `await` or using the wrong API). The exact tool result I would have needed is: `code.source("report/export.py")` returning a definition of `echo_json` as an async function, which would justify adjusting the test to use `await echo_json(...)` instead of `asyncio.run(...)`.

**e.** "Write the tool call you would make now to fix the test, and nothing
else."

> TOOL: tests.encode(id="tst_4f3935", criterion_id="c_6f5fde", path="test_export.py", body="import asyncio\n\nfrom report.export import echo_json\n\n\ndef test_echo_json_prints_one_line(capsys):\n    asyncio.run(echo_json({\"a\": 1}))\n    out = capsys.readouterr().out\n    assert len(out.splitlines()) == 1\n    assert out.strip() == '{\"a\": 1}'\n", batch_id="b_027804")

## Reading

All lines below are (reasoned: one interview at temperature 0, one run, one
model), 2026-10-02.

1. The model reads the challenge as a criterion question only (answer a).
   It never names the failure as part of the decision.
2. Asked directly, the model blames the test (answer b). It can read the
   failure when a person puts the error line in front of it in plain words.
   In the seat's user text the same line sits inside an escaped JSON string
   under `resolved_refs.last_run.output_tail`.
3. The brief and the model part at "fix the call line". The model agrees the
   test is wrong (answer c) and still answered the Developer. The
   instruction does not bind its first act to the failure.
4. The model has no picture of the fix. Answer d inverts the case: it wants
   `echo_json` to be async. Answer e re-encodes the unchanged body with
   `asyncio.run` still in it. So "fix the call line" names no edit the model
   can write.
5. One change, from answers b and e: put the failure's last line and the
   failing call line as plain text above the JSON in the user message. Pair
   them with one concrete edit, for example "`asyncio.run(f(x))` on a plain
   function: call `f(x)` directly". Only a re-record can test this change.
