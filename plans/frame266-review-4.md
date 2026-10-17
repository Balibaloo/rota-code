# Frame 266, pass 2b: review 4 of commit 0617afda

Reviewer: a read-only agent on the worktree C:/Users/roman/rota_r266d at 0617afda.
Date: 2026-10-17. Verdict: accept, with 0 high and 2 low findings.

## (a) Verdicts

1. The guard: CONFIRMED. Each listed shape gives None, and the three right shapes give the last key. A `TOOL:` line with no leading whitespace cuts the region correctly. A `TOOL:` inside a value gives None or a correct text.
2. The instrument: CONFIRMED. The six changed calls on nights 151 and 152 all end on a closed quote with no `)`. All 1089 night 152 completions that gave a ToolCall at the parent give the same result now.
3. The xfail: CONFIRMED for its input. The text names `verdict`, which is a parameter of `tests_triage`, and names the missing `)`. A seat can act on it. The wider intent does not hold on a neighbouring shape (finding 1).
4. The hunk: CONFIRMED. The module adds one import, one function, one `bracket =` assignment of three lines and one `elif`. It removes 0 lines. The two test files give 100 passed, 4 xfailed.

## (b) Findings

1. LOW, CONFIRMED. tests/rota/test_offers_followed.py:558 and rota/llm/toolproto.py, the generic `else` branch after line 1296. The xfail of frame 144 tested one input. The input `TOOL: tests.triage(criterion_id='c1', verdict=encodable` still gets the generic text with `text='''...'''`. `tests.triage` has no `text` parameter. So frame 137's sign survives for a last value that is a name or a number. The test passes because its one input now takes the new branch. Fix: add a strict xfail test for the bare-name shape, or push a frame that gates the triple-quote sentence on a `text` parameter.
2. LOW, PLAUSIBLE. pass2b_compare.py calls `extract_lenient(seg, {fn}, None)` with no signatures. Production passes signatures, and `missing` is then None for every writer op (toolproto.py:1225). So `bracket` can fire on a writer call where the compare saw `missing` fire. The count of 7 is then a lower bound for writer ops. The risk is small, because `bracket` needs every value closed and `_missing_close` rarely fires then. Fix: re-run the compare with the signatures that `extract` gets in the runner.

Notes, not findings:

- The region ends at the first line that starts with `TOOL:`. A `TOOL:` at a line start inside an open triple-quoted value cuts the region inside the value. The cut region then fails `ast.parse`, so the guard gives None. The probe shows both variants.
- An inline `TOOL:` inside a closed value gives the bracket text. The text is correct for that call. The second `missing argument list` error comes from the old scan, not from this pass.
- Implicit string concatenation, `text='a' 'b'`, gives the bracket text. The text is correct, because the value closes.
- For s153 (night 151), s290 (night 152) and s179 (night 149), the probe added `)` to the completion. Each then parses as a ToolCall with all its keys. So the advice repairs the call.

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1cf2843b-91ea-4332-96ca-93eb8010ff0b/scratchpad/r266d/.

- guard.py: 20 sources through `_no_close_bracket` and `extract`. Never closes, second open quote, prose on the same line, prose on the next line, positional, last number, last name, ends on `)`, `**` splat, f-string and bytes all give None. s290 with `'''` and with `"""`, a single-quote value, the next `TOOL:` with and without indent, an inline `TOOL:` and implicit concatenation give the last key. A `TOOL:` at a line start inside the value gives None.
- inst.py: loads the parent module from `git show 0617afda~1:rota/llm/toolproto.py` as old.py. It runs `extract` on whole completions. Night 151 s153 seqs 10 to 12 and night 152 s290 seqs 9 to 11 change, each tail ends on a closed quote. Night 152: 1089 completions gave a ToolCall at the parent. A seeded sample of 20 is 20 of 20 the same, and all 1089 are the same.
- close.py: appends `)` to three changed completions. Each gives a ToolCall with all keys.
- An inline `python -c` probe: the xfail input gives the bracket text that names `verdict`. The bare-name variant gives the generic `text='''...'''` text (finding 1).
- pytest on tests/rota/test_toolproto_quotes.py and tests/rota/test_offers_followed.py with `-o addopts=""`: 100 passed, 4 xfailed in 6.31 s.
- `git show 0617afda -- rota/llm/toolproto.py`: 0 removed lines.

## (d) Usage

The agent has no harness count of its own tokens. Its estimate is about 25k input in the context and about 6k output. Read the harness line for the true figure.
