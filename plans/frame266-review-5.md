# Frame 266, review 5: pass 3 at 58edbb6a

Reviewer on Opus, read-only, on the worktree `C:/Users/roman/rota_r266e` at 58edbb6a. Rota workflow, about the call parser. In this file, "BQ" means a backslash before a double quote.

**Verdict: accepted.** The two night 153 turns get true texts. 22 of 89,409 calls change text, and 0 right calls change. No high or medium finding. Four low findings stand.

## (a) The verdict on each point

1. False fires: CONFIRMED clean for all five shapes the brief names. Two other shapes get a new text that is wrong in a detail (findings 1 and 3).
2. The texts are true: CONFIRMED. Offsets 69 and 259 land on the open quote. Heads and the inner key match. The three-quote step parses s132 seq 6, 7, 8, 20 and 21.
3. Byte for byte: CONFIRMED. My own compare gives 22 changed and 0 right changed in both signature modes. Nights 145 to 152 change only s132 on night 151, so the 127 generic dict turns keep their text.
4. Branch order: CONFIRMED. No source reaches two branches. No shape of pass 2 or pass 2b moves to a new branch.
5. Tests: CONFIRMED for the two red tests. The four right-behaviour tests do not catch a helper that fires on every dict (finding 2).

## (b) Findings

1. `rota/llm/toolproto.py:1411` (`whose`) and `:734` (`inner_key`). Low. CONFIRMED. The source `lines={'k: 1})` is a dict whose key string never closes. The text says "is an item of the list in lines". `whose` takes the list words whenever `inner_key` is None, also inside a `{`. Fix: say "a string inside the dict in {key}" when the last bracket is `{` and no inner key matched.
2. `tests/rota/test_toolproto_quotes.py:896-918`. Low. CONFIRMED by the code path. The three right-parse tests parse, so `args_end` is not None and neither helper runs (`if args_end is None`, about line 1336). The write tests stop at the `keyed` guard. So a helper that returns a value for every unterminated dict passes all nine tests. No test pins the `)` guard on a cut completion either. Fix: add a keyed, unterminated call whose dict strings all close, and a cut list item with no `)`, and assert that both keep the key text.
3. `rota/llm/toolproto.py:676-683` and `:752-756`. Low. CONFIRMED. The call region runs to the end of the text when no next `TOOL:` follows. Prose after the call that ends with `)` meets the guard. The probe `lines={'k': 'x = 1})` plus a new line `done (see above)` gets the new text, with the head `'x = 1})` and a new line and `done (see a` in one backtick span. The text is still true, but the head shows prose. Fix: stop the head at the first new line.
4. `rota/llm/toolproto.py:1359-1361` (`keyed`). Low. PLAUSIBLE. The write guard is `_WRITES`, which holds `text`, `body` and `path` only. With no signatures, `code.run(source={'k': 'x = 1})` and `fs.put(content=...)` get the new inner text. My grep found no op whose signature has a `source` or `content` parameter, and pass 2's `short` uses the same guard. Fix: none now. Add the parameter to `_WRITES` if an op with a source parameter appears.

Outside the points: the pass's compare script imports `D:/repos/rota` and `HEAD`. Since the commit, HEAD there is 58edbb6a, so a rerun compares the new parser with itself and prints 0. I ran a copy that pins `58edbb6a~1` and the worktree. Also note that "after the open bracket" in the W4 text counts from the call's `(`. The sentence sits next to "inside the value of lines", and a seat can read it as the dict's `{`. Pass 1's text uses the same words, so I list this as a note and not a finding.

## Point detail

Point 1. Old parser (58edbb6a~1) against the worktree, through `extract` with no signatures:

- A right dict value, inner string with a double quote, closes: same ToolCall.
- A right list value, inner string with a comma, closes: same ToolCall.
- A right double-quoted value with BQ, closes: same ToolCall.
- `code.write(path='a.py', text={'k': 'x = 1})`: same key text.
- `model.amend(citations=['CHARGES-` (cut, no `)`): same key text.
- `lines=['a', 'b)` and `lines={'k': ['a', 'b})`: same generic text (no key).
- Shapes that change and should: `lines={'k': 'x = 1})`, a BQ value with no close, the same after another argument, and an open dict followed by a right second call (the second ToolCall stays).

Point 2. From `.rota/clickI_night153.db`, read-only. s257 seq 2: args start at 20. Offset 69 lands on `'base_message += f", Python {s`. The text before it is `lines={'ver_opt_show_py': `, so the inner key `'ver_opt_show_py'` is right. The completion ends `}"})`, and the inner string has no close. s276 seq 4: args start at 27. Offset 259 lands on `"the line ``assert result.exit_`, after `reason=`. The completion ends with a BQ, then `, raised in ...)`, and no plain close. s132 seq 6 on night 151: the value is `"'''the line ...'''` and ends with `)`. I dropped the leading `"` and every backslash before a quote, and `extract` gave one ToolCall for seq 6, 7, 8, 20 and 21. The text does not say to drop the leading `"`. Its first step, a plain `"` at the end, also gives a valid value.

Point 4. The chain is `joined`, `missing`, `short`, `inner`, `escaped`, `key`, `bracket`, else. `keyed` needs no `joined`, `missing` or `short`, and needs a key. `bracket` needs no key. `escaped` is None when `inner` holds. So the branches exclude each other, and the old branches keep their sources.

Point 5. A pytest plugin loaded 58edbb6a~1's `toolproto.py` as `rota.llm.toolproto` for one run. Result: 4 failed, 5 passed. The four reds are the two red tests in both parameters. Each fails on the reason text, old key text against the new text. No import or fixture error.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/eefbf293-6e8b-4a35-91c4-b3f1fed91a11/scratchpad/f266/r5/`:

- `p1.py`: sixteen sources through old and new `extract`. Point 1 and findings 1, 3, 4.
- `compare.py` and `compare.out`: the pass's compare, pinned to `58edbb6a~1` and the worktree. Point 3.
- Inline Python on the night 153 and 151 records, read-only: offsets, heads and the three-quote step. Point 2.
- `oldtp_plugin.py` and `old/`: the old module swapped in for one pytest run. Point 5.

## (d) Usage

Read the harness line for the exact count. My estimate is about 35k input and 9k output in context.
