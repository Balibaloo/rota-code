# Frame 313 review of 50412ca8 (s317's span wall)

Verdict: the change does not stand. Pass 1b must make fix 1. Fix 2 is recommended.
The door refuses the same spans as before, and s237's words are unchanged.
The offer names the right span, but its text does not tell the seat to send the whole span.

## (a) Verdicts on the points

1. Partly. 515..560 is the smallest span for both 537..560 and 540..560. The offer does not tell the seat to send all 45 lines (finding 1).
2. Holds. The span tests pass, and a sweep of 805 spans gives the same outcome at 76ab6976 and at 50412ca8.
3. Holds. The s237 refusal text is identical at 76ab6976 and at 50412ca8, and the two offers are unchanged.
4. Holds. The two edited asserts are stronger, and no assertion is lost. The conftest line exempts one test from a finding that existed before.
5. Partly. Three deep, the offer names the right list and span. At the end of a def, the offer is missing (finding 2).
6. Holds. The commit has no CR, no debug print, and `git diff --check` is clean. The fixtures are 22 KB and 36 KB (finding 4).

## (b) Findings

1. rota/roles/api.py:17025-17040 (`_holding_offer`). Severity high. CONFIRMED.
   The offer says only "To replace lines 515 to 560 send start=515, end=560", with text INVENT.
   The code comment says "the seat writes the text again", but the refusal does not say that.
   Probe p1: the seat's own text at 515..560 gets the parse door for both 537 and 540.
   The parse door then says "Send only the lines you add ... the file's own lines stay where they are".
   That advice contradicts the offered span, so s317 can loop again.
   Probe p2 (parse-own-take): own text that parses lands, and frame 140's dropped note names `x = g(`.
   The write opens a frame 283 note, so the commit is held (PLAUSIBLE for the hold, no git in the probe).
   The new tests take the offer only with the hand-made right body, so no test sees this path.
   Fix: say "Your text replaces all N lines from lo to hi, so send them all with your change". Better, offer the splice `lines[lo:start] + text + lines[stop:hi]` when the merged file parses.
2. rota/roles/api.py:17005-17023 (`_holding`). Severity low. CONFIRMED.
   When the innermost node that holds a..b is a simple statement, `_holding` returns None and not that statement.
   Probe p2 (eof-last): start=11 inside the last `return h(` of f, end=13 at the end of f.
   The refusal offers only "To replace f whole send start=0, end=13", two times, and no span of the return.
   This is the s317 pattern: the seat gets the whole def and no span that holds its lines.
   The duplicate sentence existed at 76ab6976 (outside, from `_whole_parent`).
   Fix: when no field of n holds a..b, return the list that holds n, with the span `_lo(n)..._end(n)`.
3. rota/roles/api.py:17036 and 17250. Severity low. CONFIRMED by reading.
   The new span facts carry no `node`, `name` or `end_of`. `sandbox._span_holds` (rota/core/sandbox.py:4966) then checks the bounds only.
   A wrong holding span or wrong block lines passes the frame 144 fact check.
   Fix: record a fact kind that the check re-derives, such as the list's first and last statement.
4. tests/rota/fixtures/night161_termui_ff776a1.txt. Severity low. CONFIRMED.
   The s237 test reads lines 297 to 327 only, and the fixture holds 1031 lines.
   Fix: none needed. Keep it if the full file is the recorded fact.

Outside the points:

5. tests/rota/test_span_holding.py:40. Severity low. CONFIRMED.
   The [540] text is `LINES[540:560]`, the file's own lines 541 to 560. It is not s317's text.
   The conftest exemption at tests/rota/conftest.py:170 exists because that text starts with `) from None`.
   Fix: none needed. A pass 1b test for finding 1 should use s317's real text from night 161.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/r313.

- p1.py: s317's spans 537..560 and 540..560, then the offer 515..560 with the seat's text and with the right body.
- p2.py: three-deep spans, a span to the end of file, a top-level cut, and an own text that parses on the offered span.
- p3.py: the s237 refusal with api.py of 76ab6976 (api_old.py) and of 50412ca8. The two texts are identical.
- p4.py: 805 spans of decorators.py, starts 500 to 567, at both commits. The outcome hashes match (old.txt, new.txt).
- p5.py: the end-of-def span at 76ab6976, to show that the duplicate offer existed before.
- pytest: test_span_holding.py, test_desk_guards.py and test_offers_followed.py gave 404 passed and 3 xfailed.
- git: `git diff HEAD~1 --check`, a CR count, and a search for `print(` in the commit. All three were empty.

## (d) Usage

Input tokens: about 240k. Output tokens: about 10k. Total: about 250k.
