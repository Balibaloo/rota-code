# Frame 266, review 1: the diff of 74251f79

Verdict: pass 1b. One high finding blocks the accept. The new branch fires falsely on a common writer shape, and it then gives the Developer the wrong fix. The s226 case, the byte-for-byte claim, the tests and the register hold.

Written 2026-10-16 by a read-only reviewer on Opus. Worktree `C:/Users/roman/rota_review_266` at 74251f79. Probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f266/rv1/`.

## (a) Verdict on each point

1. False fires: one found. `code.write` with `print(x, end='')` and a later apostrophe gets the new text in place of the right old text (finding 1).
2. Byte-for-byte: holds. The diff deletes no line, and 74 of 79 toolproto tests pass on both parsers.
3. The s226 case: holds. All five calls name `rulings`, show `"approve}`, say the closing quote is missing, and give character 67.
4. The seat's next move: holds the placeholder rule. The 20-character head runs into the next argument, so the end of the value stays unclear (finding 3).
5. The tests: the five are red at HEAD~1 for the right reason. The sixth guards a name that is not a parameter, not the shape of finding 1.
6. The register: no recorded prompt carries any version of the new text. No live re-record exists after 17:00 in the worktree copy.

## (b) Findings

### Finding 1. A code keyword that is a parameter name reads as a missing closing quote

- File: `rota/llm/toolproto.py`, lines 495 to 511 (the `_NEXT_ARGUMENT` loop), and line 1107 (the call in `extract`).
- Severity: high.
- CONFIRMED (observed: probe p1d.py, 2026-10-16). The call is `code.write(path='a.py', text='print(x, end='')`, a newline, `# it's done`, a newline, `')`, with the real signature. `code_write` takes `path, text, start, end` (observed: `inspect.signature` on `rota.roles.api.code_write`).
  - HEAD~1 says: "the value of text never ends. Either a quote inside text closed it early ... between triple quotes". That advice is right.
  - 74251f79 says: "the value of text starts at `'print(x, end='')` ..., character 18 after the open bracket, and no closing quote follows it. ... Put the closing quote where that value ends, and change nothing else". That advice is wrong. The value has its closing quote, and the cause is the inner quotes.
- The cause: the string `'print(x, end='` holds `, end=`, the name `end` is a parameter, and words follow the quote. So every guard passes (reasoned: the guards at lines 499 to 518).
- The scope: production passes signatures through `extract_lenient` (observed: `rota/core/runner.py:3792`, `signatures=_param_sets(sb)`). Python code in `text` or `body` often holds `, end=`, `, start=`, `, path=` or `, text=`. The shape needs an odd count of quotes after the keyword, which is the tipsAH failure that the key branch exists for (reasoned).
- The order matters. An apostrophe before the keyword stops the scan by guard 3, so the old text comes (observed: p1d.py, the `with open(path='b')` and `run(path='x')` calls give the old text).
- Fix: skip `_missing_close` when `params` meets `_WRITES`, as `third_call` does, and add the `print(x, end='')` call as a test that keeps the key text.

### Finding 2. A missing closing quote with no later quote of its kind gets the old text

- File: `rota/llm/toolproto.py`, line 549 (`return None` when the scan ends inside a string).
- Severity: low.
- CONFIRMED (observed: probe p1.py, 2026-10-16). `rulings.rule(rulings={1: "approve}, words='x')` gives the same generic text at HEAD~1 and at 74251f79, bare and signed.
- The s226 call fired only because `"instead of aborting"` in `words` holds a double quote that closes the open string (reasoned: the scan needs a closing quote to test the string).
- Fix: when the scan ends inside an open string that holds `, name=` with a known name, return the same answer.

### Finding 3. The head runs into the next argument, and "no closing quote follows it" is not literal

- File: `rota/llm/toolproto.py`, lines 516 to 517 (`text[opened:opened + 20]`) and lines 1121 to 1127 (the text).
- Severity: low.
- CONFIRMED in part (observed: probe p4, 2026-10-16). The head is `"approve}, words='Li`. A seat that puts the quote after the brace, `"approve}"`, gets "could not parse arguments: '{' was never closed". A seat that puts it before the brace gets a ToolCall with `rulings[5] == "approve"`.
- PLAUSIBLE for the seat at temperature 0: the head shows the start and also the next argument, so the seat can see the open string. The text says "no closing quote follows it", but a quote does follow, the one inside `words` (reasoned).
- Fix, one line: cut the head at the swallowed `, name=` and say "the string `"approve}` has no closing quote before `, words=`".

## Point 1. False fires

Shapes tried (observed: p1.py, p1b.py, the inline fuzz, p1d.py, 2026-10-16), each bare and with a signature, old parser against new:

- Frame 122's shape, an apostrophe in `why`, with and without a later `ask='x'`: same text as before.
- An apostrophe in `quote` before a named argument, two apostrophes, a double quote inside a single-quoted value, a possessive, a list value with an apostrophe, a positional value: same text.
- Triple-quoted values with an apostrophe and `, ask='x'` inside: same.
- Code in `text` with `f(x, y='a')`, `g(x, path='b')`, `open(path='z')`: same.
- Fuzz, 40000 calls: an inner quote of the delimiter's kind inside a prose value with commas and `name=` words. The new text fired on 56, all with a signature. Each of the 56 had the inner quote right after `, <param>=` in the prose, so the text reads as a new argument. I rate those as not a defect.
- Fuzz, 6048 calls with one closing quote deleted: the new text fired on 932. That is the recall of the check on this generator.
- The false fire of finding 1: `print(x, end='')` in `code.write` with a later apostrophe.

## Point 2. Byte-for-byte

- `git show 74251f79 --stat` gives 104 and 56 insertions and no deletion. The key text and the generic text are unchanged lines (observed).
- `_missing_close` has no side effect, so a call where it returns None takes the same branch as before (reasoned: it only reads `text`).
- The three toolproto test files ran on both parsers (observed: 2026-10-16). At 74251f79: 79 passed. At HEAD~1, through the plugin `oldparser_plugin.py`: 5 failed, 74 passed. The 74 include the exact-text tests of the key and generic texts.
- The changed reads are only the calls where the new branch fires, which is the intent.

## Point 3. The s226 case

The five calls are seq 2 to 6 in `turns`, session s226, not seq 3 to 7. Seq 7 is the end account (observed: probe p3.py on `clickI_night151.db`, mode=ro). Seq 1 is the earlier "lines 1, 5 have no ruling" call, and it parses.

Seq 2 and 3, bare and signed:

```
unterminated argument list: a string in the value of rulings starts at `"approve}, words='Li`, character 67 after the open bracket, and no closing quote follows it. The string runs on into the next argument. Put the closing quote where that value ends, and change nothing else
```

Seq 4, 5 and 6: the same text with the head `"approve}, words='''`.

- Each names `rulings`, shows the text where the string opens, and says the closing quote is missing (observed).
- Character 67 is right. It is a 0-based offset from the character after `(`, the `args_start` of line 1036 (observed: `comp.find('"approve}') - start` gives 67).
- No other text in `toolproto.py` states a position, so no convention exists to break (observed: grep for "character", "column", "position"). An 8B seat cannot count to 67 with care. The head carries the location, so the number adds little and does no harm (reasoned).

## Point 4. The seat's next move

- The text shows the seat's own characters, and it holds no example to copy. The placeholder rule of frame 122's review holds (reasoned).
- At temperature 0 the old text named triple quotes, and the seat moved to triple quotes on `words` (observed: pass report, seq 4). The new text names a quote that opens at `"approve}` and says change nothing else. That points at the right token (reasoned).
- The risk is the place of the quote, after the brace or before it (finding 3). After the brace, the next refusal says the brace was never closed, so the seat gets a second clear sign (observed: p4).
- One line it could say: "the string `"approve}` has no closing quote before `, words=`".

## Point 5. The tests

- At HEAD~1 the four s226 forms fail on the exact-text assert at line 269, with the old generic text (observed: `--tb=line`). The named-value test fails at line 286 with the old key text. These are the right reasons.
- The fix half of the s226 test, `"approve"}`, parses. It asserts `rulings[5] == "approve"` (observed: the test passes at 74251f79).
- The sixth test guards `b=`, a name that is not a parameter, bare and signed. It does not guard a code keyword that is a parameter name, which is finding 1. Add that call.

## Point 6. The register

- The commit touches no register file. `tests/rota/cassettes.json` is tracked and unchanged since ea41c936. It holds no line with "no closing quote" or "after the open bracket" (observed: grep, 2026-10-16).
- `tests/rota/cassettes.db` is not tracked. The worktree copy is dated 19:04:26, after both gate runs. Its `case_runs` rows reach 19:01:36 (observed: mode=ro read).
- No `cassettes` row holds "no closing quote", "after the open bracket", "runs on into the next argument", "closing quote is missing" or "missing closing quote" in `user` or `system` (observed).
- Every "unterminated argument list:" text in recorded prompts is the generic text (242) or the key text (30). The other matches are model echoes (observed).
- No `case_runs` row after 17:00 has `live` set. All 1574 rows from 17:00 are replays (observed). So the worktree copy holds no re-record from the first gate run.
- Caution: I did not read `D:/repos/rota/tests/rota/cassettes.db`, by the brief. If the checkout's file differs from the worktree copy, repeat the `instr` query there.

## Outside the points

- The pass ran `git stash push` and `git stash pop` on the checkout (observed: pass report, deviation 4). The diff came back whole. This is a process note, not a code defect.
- `_missing_close` is quadratic in the count of closed strings, because each close slices the rest of the text. 20000 closed strings in 349k characters take 0.24 s (observed: probe p5). That is not a risk at real sizes (reasoned).

## (c) Probes

All are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f266/rv1/`, run from the worktree root.

- `toolproto_old.py`: `git show HEAD~1:rota/llm/toolproto.py`, the old parser.
- `p3.py`: reads s226 seq 1 to 7 from `clickI_night151.db`, mode=ro, and feeds each completion to `extract`, bare and with the `rulings.rule` signature.
- `p1.py`: 21 hand shapes, old parser against new, bare and signed.
- `p1b.py`: 6000 random calls with an inserted quote or a deleted closing quote. It counts the new text.
- Inline fuzz, not saved: 20000 calls with an inner quote of the delimiter's kind inside a prose value.
- `p1d.py`: four writer calls with code keywords, old against new. Finding 1 comes from the first call.
- Inline p4: the s226 shape as sent, with the quote after the brace, and with the quote before it.
- Inline p5: the time of `_missing_close` on a long value and on 20000 closed strings.
- `oldparser_plugin.py`: a pytest plugin that loads the old parser in place of `rota.llm.toolproto`. I ran `pytest tests/rota/test_toolproto*.py` with it and without it.
- Inline register reads: `cassettes` and `case_runs` in the worktree's `tests/rota/cassettes.db`, mode=ro.

## (d) Usage

- About 85k tokens of context by the budget counter: 15,000,000 at the start, about 14,915,000 at the report. That is above the brief's 60k cap. The harness line gives the exact input and output split.
- Sub-agents: none.
