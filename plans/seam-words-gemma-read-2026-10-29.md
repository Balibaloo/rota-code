# The seam read of his words on Gemma, frame 345, 2026-10-29

Head dfec94a6, gemma4:12b-it-qat, 24 cases, 72 runs, 12 cases and 34 runs right. Source: register
`case_runs` rows 07:31:22 to 07:41:09, joined to `l3_rulings.yaml` through `api.line_words`, by
scratchpad `confusion_gemma.py`. The prompt at head, with the approve examples and the narrowed
`keep`, is the one the seat ran on: `landing.md` last changed 06:08, ac900593 (observed: git log).

## 1. The confusion table, seat word -> judge's word: count (observed: 70 landed runs)

Two runs landed nothing, m44-m45 runs 1 and 2, and m53-m58 ruled in 3 runs where an ask was
expected. The script's "none -> drop 6" on m102-m103 is left out, a by-ref case, 3 of 3 right.

Verdict mismatches, 35 lines: keep -> approve 18; revise -> exclude 9; revise -> approve 5;
revise -> contest 2; revise -> rewrite 1. Act or kind mismatches with the verdict right, 21
lines: approve -> add 9; contest -> rewrite 6; drop -> contest 3; contest -> exclude 1;
contest -> drop 1; drop -> rewrite 1. `revise` carries 17 of the 35 verdict-wrong lines.

## 2. The top four pairs on his words (observed: his_words per line)

keep -> approve, 18 lines, 6 lines in 2 cases. m121-m122 line 2 "The docstring for
format_filename must include an example...", his_words "keep lines 2 to 6 as they are", seat
`keep`, expected approve. m136-m138 line 9, the work line, his_words "keep line 9 as it is,
because the work changes only the docstring...", seat `keep`, expected approve. Wrong on his
words: the prompt's approve line quotes "keep lines 2 to 6 as they are" word for word, and its
keep line sends keep words that fault nothing to `approve`. The seat copied his verb in 18 of
18 runs, so the prompt route is spent. Suspect: the word table.

revise -> exclude, 9 lines, 4 touch lines in 4 cases. m76-m77 line 5, the touch line of
clear() with seven paths, his_words "Line 5 is wrong because ... Please keep line 5 to the
terminal module, the compat module and the terminal tests.", seat `revise`, expected exclude.
m44-m46 line 2, the touch line with src/click/utils.py, his_words "For line 2, drop the utils
file and the string helper in it, and keep only the clear function...", seat `revise`, expected
exclude. Wrong on his words: "Drop the utils file" is the prompt's own exclude example, and the
seat gave `exclude` on no touch line in 72 runs. Suspect: the prompt's `revise`
definition, "right in substance and needs other words", fits every narrowed line and comes first.

approve -> add, 9 lines, line 1 of 3 cases. m58-m59 line 1 "Make clear() return True...",
his_words "Ok, every line matches what I asked for", seat `approve`, expected add on "keep what
clear() prints exactly as it is now". m75-m76 line 1, the Click account line, his_words "no
words", seat `approve`, expected add on "This page also leaves out my request". Defensible: the add
words name no line, so his_words shows them beside no line, and he never says "add". Suspects:
the m58-m59 expectation, a constraint judged as an add, and a missing add example in the prompt.

contest -> rewrite, 6 lines, lines 2 and 3 of m34-m35. Line 2 "When get_app_dir is called on
Windows with roaming=True and APPDATA or LOCALAPPDATA are unset...", his_words "Lines 2 and 3
are wrong: with the roaming flag on, only the roaming app data variable being unset should
matter...", seat `contest`, expected rewrite. Line 3 carries the same words and result. Wrong
on his words by a thin line: after "wrong" the words say what is true, so the line must say
something else. With the verb there, m44-m46 line 3 "replace the note with this", the seat gave
rewrite 3 of 3. Suspect: the prompt's rewrite line has no "X is wrong: Y" example.

## 3. The 12 wrong cases (observed: the log and the register)

m58-m59 and m75-m76: line 1 approve for add, wrong on the add alone. m27-m28: lines 1 and 2
revise for approve on "Lines 1 and 2 are right, with Roaming when the roaming flag is True and
Local otherwise", defensible under the prompt's revise line (reasoned), so the expectation or
that line is the suspect. m76-m77 line 5 and m44-m46 line 2: revise for exclude. m92-m93 line
2: revise for exclude in runs 2 and 3, contest with no act in run 1. m34-m35: lines 2 and 3
contest for rewrite. m47-m48: line 1 approve for add, and "line 47: no ruling" though the
landed call has drop on all 68 keys; line 47 repeats the text of line 8, so the landing loses a
repeated row's line (reasoned), not a word fault. m53-m58: ruled drop instead of asked, on
"Please drop all twelve lines", so the ask expectation is the suspect (reasoned). m44-m45:
runs 1 and 2 landed nothing, line 3 revise refused by the note door four
times, then the budget cut; run 3 line 2 revise for exclude, line 3 drop for rewrite. m121-m122:
lines 2 to 6 keep for approve. m136-m138: line 9 keep for approve, and line 10 revise for
contest in 2 runs on "Line 10 misreads me on line 9". Cases wrong only on an `add` line that no
words reach: 2, m58-m59 and m75-m76; m47-m48 is a third but for line 47.

## 4. The lever (reasoned: lines counted from the table above)

1. `WORD_ACTS` and `_WORD_KINDS` in api.py: take `keep` out of both, and add `"keep": "approve"`
   to `RULING_WORDS`. Why: 18 of 35 verdict-wrong lines are a literal `keep` on words the
   prompt already lists as approve, no case expects a keep act, and m121-m122 passes.
2. Prompt, the `revise` line: add "Words that say the line is wrong are never `revise`, whatever
   follows them". Why: 12 verdict-wrong lines carry "wrong" or "misreads" and got revise, and
   m76-m77, m44-m46, m92-m93 and, with change 1, m136-m138 move.
3. Prompt, the `add` line: add "Words that say the page leaves out or no longer shows his
   request are `add` on line 1", and re-judge m58-m59 line 1 to approve with no add, since "keep
   what clear() prints exactly as it is now" names no missing line. Why: 9 lines, m58-m59 and
   m75-m76 pass, and m47-m48 then rests on line 47 alone.
