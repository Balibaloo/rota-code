# Frame 266, review 2: pass 1b at ce658cdb

Written 2026-10-16 by a read-only reviewer on Opus. Worktree `C:/Users/roman/rota_review_266b` at ce658cdb. Probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f266/rv2/`.

Verdict: accept. Review 1's high is closed. One low false fire remains on a function with no source parameter. No high finding.

## (a) Verdicts

1. Review 1's high: closed. A new false fire exists on `rulings.rule` when a value quotes a call (finding 1, low).
2. The five s226 calls: hold. Seq 2 to 6 each name `rulings`, `"approve}` and `, words=`, bare and signed.
3. The skip list: the same set, `_WRITES` at line 193. The predicate differs when `params` is None (finding 2, low).
4. The other refusal texts: byte for byte. The diff from 0213c1db adds 113 lines and deletes none.
5. Stale cases: none. No recorded prompt carries the new text, and no signed parse of a recorded completion changes.

## Point 1: review 1's high, and other false fires

- Review 1's call is `code.write(path='a.py', text='print(x, end='')`, a newline, `# it's done`, a newline, `')`, with the real `code.write` signature. At ce658cdb it gets the key text (observed: q1.py, 2026-10-16): "unterminated argument list: the value of text never ends. Either a quote inside text closed it early, or its closing quote has a backslash before it. Put a value with quotes or line breaks between triple quotes, three single quotes at each end. Write the value as it is, with no backslashes:" and then `text='''the text, with its quotes and line breaks as they are'''`.
- `criteria.specify` cannot false-fire. It takes `text`, so the skip covers it (observed: `inspect.signature` on `rota.roles.api.criteria_specify`). The skip covers 16 of 107 api functions (observed: an inline count).
- Shapes tried on `rulings.rule`, signed with `rulings, words, ask, ctx` (observed: q1.py):
  - `words="set x=1, then y=2"`: a ToolCall. Correct.
  - `words='set x=1, then y=2, it's done'`: the key text. Correct.
  - `words='set it, words='x' and then ask='y''`: a ToolCall. Correct.
  - `rulings={1: "see words=, then ask=", 2: 'approve'}, words='it's'`: the key text. Correct.
  - `rulings={1: 'call g(x, ask='y')'}, words='ok'`: "could not parse arguments". Not the new branch.
  - `words='set x=1, words=2, it's done'`: the new text names `'set x=1` before `, words=`. The input is ambiguous. Not counted as a false fire.
  - `rulings={1: 'call it with x, ask=1'}, words='don't'`: the new text. `, ask=1` is a real argument form. Ambiguous. Not counted.
  - `rulings={1: "call g(x, ask='y')"}, words='it's ok'`: false fire (finding 1).
  - `words='call g(x, ask="y"), it's ok'` and `words="call g(x, ask='y'), it"s ok"`: false fire (finding 1).
  - `words='the line says f(a, words="x") and it's wrong'`: false fire (finding 1).

## Point 2: the five s226 calls

All five calls, seq 2 to 6 of session s226, give this text with a signature and bare (observed: q2.py on `D:/repos/rota/.rota/clickI_night151.db`, opened read-only and immutable, 2026-10-16):

```
unterminated argument list: a string in the value of rulings starts at character 67 after the open bracket. The string `"approve}` has no closing quote before `, words=`, so it runs on into the next argument. Put the closing quote where that value ends, and change nothing else
```

Each text holds `rulings`, the string `"approve}` in backticks and `, words=` in backticks (observed: q2.py, three checks per call). The triple-quoted form, seq 4 to 6, gives the same text (observed).

## Point 3: the skip list

- `third_call` and the new skip both read `_WRITES = frozenset({"text", "body", "path"})` at `rota/llm/toolproto.py:193` (observed). The names match.
- The predicates differ. `third_call` returns None on `not params or _WRITES & set(params)` (line 1085). The new skip is `params and _WRITES & set(params)` (line 1115). So with no signature, `_missing_close` runs on a writer (finding 2).

## Point 4: the other refusal texts

`git diff 0213c1db ce658cdb -- rota/` gives 113 insertions and 0 deletions in `rota/llm/toolproto.py` (observed). So the joined, key and generic texts keep every byte. The new `elif missing:` branch sits between the joined branch and the key branch (observed: lines 1117 to 1136).

## Point 5: stale cases

How I checked (observed: q5.py and q5b.py, 2026-10-16, on the worktree's `tests/rota/cassettes.db`, read-only):

1. I read all 33315 cassettes.
2. I counted the `user` texts that hold "has no closing quote before" or "after the open bracket". The count is 0.
3. I parsed every `completion` with the 0213c1db parser and the ce658cdb parser, bare and with the signatures of all api functions. I compared the refusal reasons.
4. Four parses differ. All four are `code.write` calls on `src/notify/formatting.py`, and all four differ only in the bare parse (observed: q5b.py).

A bare refusal reaches no seat prompt. The runner parses a reply with `_param_sets(sb)` (observed: `rota/core/runner.py:3792`). The bare callers `_stub` and `probe_tools.graded_text` keep ToolCalls only (observed: `runner.py:1266`, `probe_tools.py:126`). So no case goes stale (reasoned). The tests assert parser output, not a prompt. The test file passes, 46 of 46 (observed).

## (b) Findings

1. A value that quotes a call with a parameter name gets the new text when a stray quote sits later.
   - File: `rota/llm/toolproto.py`, lines 497 to 524, the `_NEXT_ARGUMENT` loop in `_missing_close`.
   - Severity: low. The value must quote a call that uses `rulings=`, `words=` or `ask=`. A seat writes that rarely (reasoned). Writers, the common case, are skipped now.
   - CONFIRMED (observed: q1.py). The call `rulings.rule(rulings={1: "call g(x, ask='y')"}, words='it's ok')` gives "a string in the value of rulings starts at character 12". It goes on: the string `"call g(x` has no closing quote before `, ask=`. The rulings string is closed. The fault is the apostrophe in `it's`. The advice breaks the call more.
   - The same class: `words='the line says f(a, words="x") and it's wrong'` and `words='call g(x, ask="y"), it's ok'`.
   - Fix: skip a `, name=` match that sits inside a bracket the string itself opened.
2. With no signature, the new branch still runs on a writer, unlike `third_call`.
   - File: `rota/llm/toolproto.py:1115`.
   - Severity: low. Every seat parse passes signatures, so a bare refusal reaches no seat (reasoned: point 5).
   - CONFIRMED (observed: q5b.py). Four recorded `code.write` completions get the new text bare and the old text signed. The first names the string `'ELLIPSIS = chr(8230` before `, limit=`, which is source code, not an argument.
   - Fix: test `not params or _WRITES & set(params)` at line 1115, if the bare path must match `third_call`.

## (c) Probes

All probes are in the `rv2` directory named above. Each ran from the worktree root.

- `q1.py`: review 1's call, and eleven `rulings.rule` shapes, with signatures from `inspect.signature` on `rota.roles.api`.
- `q2.py`: the five s226 completions, seq 2 to 6, from `clickI_night151.db`, read-only, signed and bare.
- `toolproto_0213.py`: the output of `git show 0213c1db:rota/llm/toolproto.py`, loaded as a separate module.
- `q5.py`: all 33315 register completions, old against new, bare and signed, and a count of the user texts.
- `q5b.py`: the four differing completions, bare against signed.
- Inline: a count of the api functions the skip covers. Pytest on `tests/rota/test_toolproto_quotes.py`: 46 passed.

## (d) Usage

About 72k tokens in all, by the harness counter: about 62k input and about 10k output. This is above the 40k cap. The register sweep in q5.py ran past the 120-second limit, and the report write failed twice in the shell.
