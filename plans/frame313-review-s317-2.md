# Frame 313 review 2 of 2a447887 (s317's span wall, pass 1b)

Verdict: the change stands. No finding blocks it. Finding 1 is a false fact in the test instrument, and pass 1c can fix it in one line.
The door refuses the same spans as before. The offer now carries a text that lands, and frame 140's note on that text is true.

## (a) Verdicts on the points

1. Holds. The offer text is `lines[515:536] + s317's turn 4 text + lines[560:560]`. The text lands, parses, and changes only 536 to 559. The refusal says "A write to start=515, end=560 replaces every line from 515 to 559". Frame 140's note is a true fire. s317's text has no `if version is None:`, and line 547 holds that check inside 537..560. A turn 4 text that keeps lines 546 to 550 lands with `dropped` None.
2. Holds. In the end-of-def case, the offer is "send start=3, end=6 with line 3 of the file, then your text". "To replace f whole" comes once. The refused offer that the conftest line exempts is the old "To add after it send start=6, end=6" (cut door, finding 2). The new offer is not refused.
3. Partly. The new statement facts carry `node`, `name` and `head`, and `sandbox._span_holds` reads them against the tree. Facts on an `ExceptHandler` are false (finding 1). The fact for the whole span lo..hi still carries bounds only (finding 2).
4. Holds. The span, desk-guard and offers-followed tests give 406 passed and 3 xfailed. The 805-span sweep of decorators.py gives the hash d731bacde40cb572dec10c23f36d546d. Review 1 got the same hash at 76ab6976.

## (b) Findings

1. rota/roles/api.py:17034-17037 (`_stmt_fact`) and 17307. Severity low. CONFIRMED.
   A cut across two `except` clauses makes `held` a list of `ExceptHandler` nodes.
   `_stmt_fact` records `node='ExceptHandler'`. `sandbox._span_holds` (rota/core/sandbox.py:4988) walks only `ast.stmt` and `match_case`, so the fact is false.
   Probe p7: spans 5..10 and 4..9 in a try with two handlers. Each gives two false facts: "the statement named has the spans []".
   No seat sees the facts, because `api.RECORD` is off in a session. A test that meets this case goes red under frame 144's check.
   Fix: admit `ast.excepthandler` in `_span_holds`, or let `_stmt_fact` skip a handler.
2. rota/roles/api.py:17053. Severity low. CONFIRMED by reading.
   The holding span fact `(lo, hi)` still names no node. The statement facts check `held[0]` and `held[-1]`, but not that they are the span's ends.
   When a falls on a blank or comment line, lo is a. lo is then not the first statement's line, and nothing checks lo.
   Fix: record `lo == _lo(held[0])` or the gap as a `line_text` fact, or accept the bounds check and say so.

Outside the points:

3. rota/roles/api.py:17088-17093. Severity low. CONFIRMED by reading.
   The spliced text is in the recorded offer only. `_send` records it only when `api.RECORD` is on, and a session runs with it off.
   The seat gets the words "lines 515 to 535 of the file, then your text" and must build the 45 lines itself.
   The tests take the recorded text, so no test shows that a small model builds the text from the words.
   Fix: none in this pass. A night with s317's case shows if the words are enough.
4. tests/rota/test_span_holding.py:5. Severity low. CONFIRMED.
   The docstring says that s317 "sent the right repair". s317's turn 2 and turn 4 texts both drop the `if version is None:` guard.
   Probe p6 shows the landed callback has no such guard. The note is right, and the docstring is wrong.
   Fix: say that s317's text fixes the order and drops the guard.

The test's S317 texts match `tool_calls` and `turns` 2 and 4 of session s317 in `.rota/clickI_night161.db`, character for character.
The `_edge` shift was probed with a first line that repeats a file line two lines above start. The older first-line door refused first, so the shift did not drop lines.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/r313b.

- q1.py: reads s317's turns from `.rota/clickI_night161.db` read-only into s317.json.
- p6.py: takes the offer with s317's turn 4 and turn 2 texts, and with a turn 4 text that keeps the guard. It prints `dropped`, the fact check, and the guard lines. It also probes the `_edge` shift.
- p7.py: three cuts in a try with two `except` clauses, and the false facts.
- ../r313/p4.py: the 805-span sweep at 2a447887 (new2.txt). It matches ../r313/old.txt byte for byte.
- log.jsonl: `ROTA_OFFER_LOG` of test_span_holding.py. It names the refused offer of each exempt test.
- pytest: test_span_holding.py, test_desk_guards.py and test_offers_followed.py gave 406 passed and 3 xfailed.

## (d) Usage

Input tokens: about 60k. Output tokens: about 8k. Total: about 68k.
