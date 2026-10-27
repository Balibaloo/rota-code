# The review of F19 at f4dc65e4, pass 1

Worktree `C:/Users/roman/rota_f19`, commit f4dc65e4 on `f19root`, parent 9827e38a. Read only. Verdict: the change holds on each escape level, with 0 high and 5 low findings. Two lows reverse a reviewed rule with no record. The 41 tests of the four changed files pass, and the 12 tests of `test_frame328_challenge_quote.py` and `test_span_holding.py` pass.

## (a) The verdict on each point

1. Holds. Each of the five levels reads a span and refuses a changed word, on both parse paths. One raw-string case reads a non-span on the strict path, and the parent read it too (finding 3).
2. Yes, in letter. A strict value that holds the text `\x41` reads as `A`, and `\x20` in prose reads as a space. Each decode gives one character, so the decoded value is a span. The stored text is not (finding 2).
3. No. The markers cut the cell, so a border and the header are in no view. The only added decoration is `\` before `|`, one for one with the row (probe 2, b).
4. `_outer_marks` is a different fact: the seat's wrapping marks. `_span_of` is a missed reader. It keeps its own decoder of `\n`, `\t`, `\"` and `\'` (finding 4).
5. Yes. `test_only_an_escape_of_a_control_character_is_read_as_one` was a test of behaviour, and its successor asserts the opposite (finding 2). The other two are wording.

## (b) Findings

1. **The line-break rule of frame 328 review 1, finding 4, is dead at the door.** `rota/core/sandbox.py` 1046 to 1049 and 1001 to 1017. Severity low. CONFIRMED: `_quote_reads('assert r == "a\nb is the text"', 'assert r == "a b is the text"', "tests")` gives True at f4dc65e4 and False at 9827e38a. `_call_values` turns `\n` into a line break, and `_span_of` then normalises the line break to a space. `test_a_decoded_line_break_meets_only_a_line_break` calls `_span_of` directly, so it stays green. The strict path already stored a line break before this change, so the rule only ever held for the text that the lenient path keeps. Fix: decide the rule once, then either drop it from `_span_of` and its test with a note, or test it through `_quote_reads`.

2. **A printable escape and a second decode read as the character, and a behaviour test was inverted.** `rota/core/sandbox.py` 1011 to 1016, `tests/rota/test_frame328_restage.py` 250 to 259. Severity low. CONFIRMED: the seat text `x = "\\x41BCDEF"` stores `x = "\x41BCDEF"` on the strict path, and that value reads against `x = "ABCDEF"` (True, parent False). `lists\x20the files of\x20the batch` reads against a prose criterion (True, parent False). `\N{LATIN CAPITAL LETTER A}` and `\101` read too. No case was found where the decoded value is not a span of the row. The old test asserted that `\x41BCDEF` is no span of `ABCDEF`. The new test asserts that it reads, against pass 3's review, finding 1. Fix: record the reversal of pass 3's finding 1 in the frame, or decode the quote only where the strict and the lenient values differ.

3. **The case of pass 3's finding 1 still reads on the strict path.** `rota/core/sandbox.py` 1020 to 1029, `tests/rota/test_f19_quote_forms.py` 54 to 63. Severity low. CONFIRMED, not new: the seat text `assert r"\033[2J" in out` stores the ESC byte on the strict path. That value meets the decoded view of a row that holds `r"\x1b[2J"`, at f4dc65e4 and at 9827e38a. The new test passes only the text that the lenient path keeps. A verbatim copy of the row stores the same value, so the door cannot tell the two apart. Fix: say the limit in the docstring of `_quote_pairs` and in the test, or hand the seat's call text to the door.

4. **`_span_of` keeps a decoder of the call syntax of its own.** `rota/core/sandbox.py` 1458 to 1460. Severity low. CONFIRMED: a quote with a bare `'`, a bare `"` and `\'` (`It\'s \'c.txt\' for "a/b" now`) gets `()` from `_call_values`. It reads only through the decoder in `_span_of`. The decoder also runs after `_call_values`, so `\n` gets a second decode. Fix: let `_call_values` carry a form with both marks bare by escaping one, then remove the decoder from `_span_of`.

5. **The new guard of `_escape_note` reads no seat text.** `rota/roles/api.py` 23102 to 23103. Severity low. CONFIRMED: `_call_values("\n")` gives `('\n', '\n')` as a line break, and `_call_values("\\n")` holds `\n`. The guard is True on every call, and it does not read the fragment. Fix: remove the two clauses, or test the values of the fragment.

Outside the points:

6. **The lenient path stores a backslash and a line break for `\\n`.** `rota/llm/toolproto.py`, `_escape_newlines_in_quotes`. Severity low. PLAUSIBLE: `_call_values("\\n")` gives `'\n'` strict and `'\' + line break` lenient. The decoded forms now carry the lenient value, so the door compares a value that no seat meant. No probe found a false read from it. Fix: make the lenient path keep an escaped backslash as one backslash.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c66eae69-d69c-45cb-8d68-947dc45d2ac1/scratchpad/`. The parent tree is `f19old/`, made by `git archive 9827e38a rota`. Each probe ran on both trees.

- `f19_probe1.py`: five escape levels (no escape, `\\`, one `\`, `\n` from JSON, a raw string, a raw escape, a triple-quoted body). It passes each seat text through `_call_values` and reads each stored value.
- `f19_probe2.py`: mixed marks, the table cell view and its header, the printable escapes `\x41`, `\N{...}`, `\101` and `\x20`, the lenient path on keyword text, and the `_escape_note` guard.
- `f19_probe3.py`: a `\n` quote against a space, and the second decode of `\x41`.
- `python -c`: the finding 4 case of `test_frame328_challenge_quote.py` through `_quote_reads`, on both trees.
- `pytest`: the four changed test files (41 passed), then `test_frame328_challenge_quote.py` and `test_span_holding.py` (12 passed).

## (d) Usage

Input about 70k tokens, output about 10k tokens, total about 80k. The brief capped the review at 40k, and the review went past the cap.
