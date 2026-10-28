# W3 review, pass 1: commit d6a9efe6 on w3root

Verdict: one high, three low. The raw form and the chr(92) form keep the value in 13 of 14 probes. One chr(92) form is not Python, and the advice offers it first.

## (a) Verdicts on the points

1. Mostly yes. The first form keeps the meant value in 12 of 14 strings. Case 12, an escaped mark, gets a broken first form (finding 1). Case 7 gets no form (finding 4).
2. Yes for every form that the code builds: raw, joined and slash. But `_call_keeps` checks the transport only, so it passes a form that is not Python (finding 1).
3. Yes, one form comes first and the text is short. The slash tail still shows on an assert line (finding 2). The words "both parse paths" mean nothing to a seat (finding 3).
4. Yes. Both callers give the new advice. A real pytest run of the night 171 body gives the raw form in the note. Finding 1 reaches both callers.

## (b) Findings

1. rota/roles/api.py:18212-18219, high, CONFIRMED. The joined form splits `one` on every backslash, an escaped mark included. For the literal `"say ` + chr(92) + `"hi` + chr(92) + `" ` + chr(92) + `d"`, the advice offers `"say " + chr(92) + ""hi" + chr(92) + "" " + chr(92) + "d"` first. That form is a SyntaxError. `_call_keeps` returns True, because it compares the call's value with the form and never compiles the form. Probe 2 shows the same advice in the collection note. Fix: build the joined form from the parsed value (an escaped mark becomes `chr(34)` or `chr(39)`), and offer a form only when `eval` of the form equals `one`.
2. rota/roles/api.py:18225-18229, low, CONFIRMED. The slash tail shows on `assert "C:...Users...new...Local" in result` and on three other assert lines. The slash form is the shortest form, and night 171 showed that an 8B seat takes the short form. PLAUSIBLE that a seat takes it again on an assert. Fix: give the slash tail only when the line holds no `assert`, no `==` and no ` in `.
3. rota/roles/api.py:18218-18219, low, PLAUSIBLE. "That form keeps a real backslash on both parse paths" names an internal part of the harness. A seat cannot act on the words. Fix: write "That form keeps each backslash."
4. rota/roles/api.py:18220-18224, low, CONFIRMED. A string with both marks, `"it's ` + chr(92) + `d"`, gets "Write the value with no backslash". That advice changes the value. The form `"it" + chr(39) + "s " + chr(92) + "d"` keeps the value and the call keeps it. Fix: in the joined form, write each bare mark as `chr(39)` or `chr(34)`.

Notes on point 1, not findings. The octal case `"` + chr(92) + `777"` gets `chr(92) + "777"`. Python 3.14 reads the original as chr(511), so the meant value is not certain. The f-string and the bytes cases get `rf` and `rb` forms that keep the value. The no-literal branch (18195-18199) holds a static example that the call keeps. Its slash sentence shows for a value that is not a path.

Outside the points: no test in tests/rota/test_frame335_escape.py covers an escaped mark or a string with both marks.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/w3rev/probe1.py: 14 literals on an assert line. For each: the escape from `ast.parse` with SyntaxWarning as an error, `_raw_advice`, then `_call_keeps` and `eval` of each advised form against the meant value.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/w3rev/probe2.py: three test files run by pytest with `-W error::SyntaxWarning`. The output goes to `_note_collection_error`. The night 171 body, a `\U` path and the escaped mark.
- tests/rota/test_frame335_escape.py with ROTA_MODEL=qwen3:8b: 18 passed.

## (d) Usage

Input tokens: about 45k. Output tokens: about 7k. Total: about 52k. The counts are estimates. The harness shows no exact count to the agent.
