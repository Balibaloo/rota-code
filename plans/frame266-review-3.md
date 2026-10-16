# Frame 266, pass 2: diff review 3 of commit 3c38f2e5

Reviewer: a read-only agent on the worktree C:/Users/roman/rota_r266c at 3c38f2e5.
Date: 2026-10-16. Workflow: the meta workflow (this build session's review of a parser pass).

Verdict: accept. 0 high findings, 2 low findings.

## (a) The verdict on each point

1. CONFIRMED. The new branch fires only where the key branch fired. A full close parses, and the generic refusal stays byte for byte.
2. CONFIRMED. `code.write` keeps the old key text on the short shape, with and without the signature, on `text` and on `path`.
3. CONFIRMED. Both guards keep the old key text. The old text is the less wrong text there, so the guards are right.
4. CONFIRMED. Fuzz case `prose-1-2500-inject #737` moves to the three-quote text. The new text is true for that input.
5. CONFIRMED. A seat can act on "why= opens with ' and never closes". Moving the check before the rescan gives nothing, because `_short_close` returns None on s247 seq 5.
6. CONFIRMED. No string literal of the parent is removed. The commit adds 12 literals, all in the new function and the new branch.
7. CONFIRMED. The 4 new red tests and the fuzz slice test fail on the parent parser for the reason the pass names.

## (b) Findings

1. Low. rota/llm/toolproto.py:627 and 1195-1197. With no signatures, the unknown-key guard and the write-parameter guard do not run. Only the `key in _WRITES` check holds. CONFIRMED for the unknown key: `challenge.break(citation='a', quote='b', end='''x'')` with `signatures=None` gets "the value of end opens with three quotes". With the signature it keeps the old text. The no-signature callers are rota/core/runner.py:1272 (ToolCalls only, no refusal reaches a seat), rota/llm/toolcheck.py:89, and the bare fallback at rota/llm/toolproto.py:1709. Whether a seat reads a refusal from the bare fallback is PLAUSIBLE, not probed. The new text is literally true on that shape, so the harm is small. Fix: return None from `_short_close` when `params` is None, or record that the no-signature path takes the new text by design.

2. Low. rota/llm/toolproto.py:622. The check `q * opening in core` counts an escaped apostrophe (a backslash, then a quote) as a quote inside the value. CONFIRMED: `_short_close(S247_SEQ5, ...)` returns None. So the s247 seq 5 shape stays out of reach even if the check moves before the rescan or into the lenient branch. Fix: in a later frame, remove escaped quotes from `core` before the inner-quote check, and keep the xfail test as the red test.

Outside the points, no defect. The probes also show these facts:

- A short close followed by text on the same line keeps the old text, because the region must end with `)`. This is conservative.
- A second call on the next line still parses after a short-close refusal on the first call.
- A `why` value that holds `, b=1` keeps the old text because of the `_NEXT_ARGUMENT` guard. This is conservative.
- A three-quote value with an apostrophe inside, `why='''it's wrong.'')`, gets the citation-swallow text, before and after the commit. The commit does not change it.

## Point details

Point 1. Structure: `short` is computed only inside `args_end is None`, after `third_call()` returns None. It requires `key` truthy, `joined` empty and `missing` None. The `elif short` branch sits before `elif key`, so it replaces only the key text. Probes with identical old and new output: `why='''x is wrong.''')` parses, `why='x is wrong.')` parses, and two broken lists get the generic text. Probes that move from the key text to the new text: `why='''x is wrong.'')` (three, two), `why='x is wrong)` (one, none), `why="x is wrong)` (one double, none).

Point 2. A `code.write` call with `text='''x = 1`, a newline, and `y = 2'')` gets "the value of text never ends", old and new, with the `code.write` signature and with none. The same shape on `path` as the last argument gets "the value of path never ends", old and new.

Point 3. The `, name=` guard: a `why` value that holds `, quote='b'` gets the citation-swallow text, old and new. A `why` value that holds `f(a, b=1)` gets the old key text. The unknown-key guard: `end='''x'')` with the `challenge.break` signature gets the old key text "the value of end never ends". The old key text says a quote inside may have closed the value early. On a value that may hold a later argument or code, that cause can be true. The new text could then tell the seat to close a value that is not the last one. So the old text is the right text for a seat to act on there.

Point 4. The input is `TOOL: rulings.rule(ask='a1', words='', rulings='''s'no'(don't'sits'')`. The case wants `words` to hold the injected piece that starts `', rulings='''`. The old text told the seat to put `rulings` between triple quotes, which it already was. The new text says `rulings` opens with three quotes and ends with two. That is true of the text as written. A seat that adds one quote gets a call that parses, with `rulings` as its own argument. The fuzz input is adversarial, and no text can recover the generator's intent. The new text is right for the input.

Point 5. The text names the key and the quote, and says the value never closes. The value of s247 seq 5 ends `false.)` with no closing quote. One added quote before the bracket makes the call parse, so a seat can act on the text. It does not name the count, so it is weaker than the new text. `_short_close` on S247_SEQ5 returns None, because of finding 2. So a check before the rescan changes nothing on that call. Used as an early refusal, such a check would also pre-empt `_rescan_args` and `third_call` parses. The pass's choice to leave it is right.

Point 6. An AST walk of both versions collects every string constant and every f-string. Removed: 0. Added: 12: the two new f-strings, their 5 constant pieces, the docstring, and the four count words.

Point 7. A pytest plugin replaced `rota.llm.toolproto` with the parent's file, loaded by `probes.frame122.fuzz.parser_at`. Result: 5 failed, 51 passed, 1 xfailed. The reds are `test_three_open_two_close_names_the_counts` (s245_seq5 and s246_seq6), `test_double_quote_open_none_close_names_the_counts`, `test_single_quote_open_none_close_names_the_counts` and `test_the_parser_keeps_its_reads_on_the_fuzz_slice`. Each quotes test fails on the reason assert, the old key text against the new text. The fuzz test fails on case #737 alone. At 3c38f2e5 the quotes, fuzz and triple files give 87 passed, 1 xfailed. These match the pass report.

## (c) Probes

All are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/04be1489-62d6-4964-8f68-ab5f38d2d1ea/scratchpad/r266c/. Each ran from the worktree root with the rota venv Python on 2026-10-16.

- p1.py: 21 built calls through the parent parser and the commit's parser, with and without signatures. Points 1, 2 and 3, finding 1, and the outside facts.
- p2.py: fuzz case #737, old and new. `_short_close` and `extract` on S247_SEQ5. The AST literal diff of toolproto.py. Points 4, 5 and 6, and finding 2.
- oldtp.py: a pytest plugin that loads the parent parser. The run was pytest with `-p oldtp` on the quotes and fuzz test files, then the three files at the commit. Point 7.

No tracked file changed. No git command that changes a tree or the index ran. The gate did not run, because no point needs it.

## (d) Usage

The harness counter shows about 70k tokens in all, over the 40k cap. My estimate is about 58k input and 12k output. The harness line is the true figure.
