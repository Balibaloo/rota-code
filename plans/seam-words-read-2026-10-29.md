# The seam read of his words, frame 345, 2026-10-29

Head df4b89b9, qwen3:8b, 24 cases, 72 runs, 11 passed. Source: register
`case_runs` rows 05:39:54 to 05:42:41, joined to `l3_rulings.yaml` through
`api.line_words` for his_words. Script: scratchpad `confusion.py`.

## 1. The confusion table (observed: the 66 landed runs)

Six runs landed nothing, all refusals: m6-m7 x3, m47-m48 run 1, m44-m45 run 2,
m44-m46 run 3. m53-m58 ruled x3 where an ask was expected. m102-m103 is a
replay with no `rulings.rule` call. Pairs are seat word -> judge's word: count.

Verdict mismatches, 65 lines: keep -> approve 26; revise -> approve 21;
approve -> drop 6; revise -> exclude 4; contest -> approve 3; rewrite ->
revise 3; keep -> absent 2.

Act or kind mismatches with the verdict right, 52 lines: contest -> drop 15;
drop -> exclude 9; approve -> add 8; contest -> rewrite 7; drop -> contest 6;
drop -> rewrite 3; rewrite -> contest 3; rewrite -> drop 1.

`keep` lands as verdict `revise` through `WORD_ACTS`, so the first two pairs
are the 47 problem lines "verdict 'revise', expected 'approve'".

## 2. The top five pairs on his words (observed: his_words per line)

keep -> approve, 26 lines, 10 distinct lines in 5 cases. His words: "line 4
reads my last answer correctly" (m74-m75, m27-m28), "Line 23 is read right, so
keep it" (m90-m92), "Lines 10 and 11 read me right" (m116-m118), "keep lines 2
to 6 as they are" (m121-m122). The seat's `keep` is defensible on his words,
twice literal. The prompt's `keep` means "fault only its check", and no case of
the 24 expects it. The suspect is the prompt's definition and example of `keep`.

revise -> approve, 21 lines. His words: "lines 5 and 6 read my earlier answers
right" (m58-m59), "line 6 reads my last answer correctly" (m76-m77), "Lines 1
to 6 and line 9 are ok" (m116-m118), "the other lines are approved" and "keep
line 9 as it is" (m136-m138), and "no words" (m80-m81 line 1, m121-m122 line
9). The seat's `revise` is wrong on his words: agreement, with no other words
asked for. The suspect is the prompt: it shows no approve example on a
read-back line, and `revise` says "right in substance", which reads as "right".

contest -> drop, 15 lines. His words: "Line 4 is wrong, because I asked only
for the one example and not for any added text" (m97-m98), "Lines 11 to 22 are
wrong because they name users of other parts of the library" (m90-m91 run 2;
runs 1 and 3 gave drop). He says wrong, never drop. The seat's `contest` is
defensible on his words. The suspect is the expectation, or a missing prompt
sentence that a line he never asked for is a drop.

drop -> exclude, 9 lines. His words: "remove the five formatting tests from
what you expect to touch" (m74-m75), "keep line 5 to the terminal module, the
compat module and the terminal tests" (m76-m77), "the change goes in the
docstring ... not in a test file" on a line with one path (m92-m93). The first
two are wrong on his words: he keeps part of the line. The prompt's line 19,
"On any other page line, `remove` is a drop", pulls the seat to drop. The
m92-m93 drop is defensible: the only path leaves, so the line is empty. That
expectation is the suspect (reasoned: the leaving session's doubt holds there).

approve -> add, 8 lines. his_words on line 1: "Ok, every line matches what I
asked for" (m58-m59) and "no words" (m47-m48, m75-m76). The add words name no
line, so the binding never shows them beside line 1. The seat's `approve` is
defensible on what it saw. The suspect is the expectation, out of the seat's reach.

## 3. The cases wrong in one turn with no refusal (observed: transcripts)

Eight cases, all three runs each. The brief counted seven; m75-m76 is the eighth.

- m74-m75: line 3 drop for exclude; line 4 keep for approve.
- m27-m28: line 3 drop for contest with no act; line 4 keep for approve.
- m92-m93: line 2 drop for exclude, the line's one path.
- m97-m98: line 4 contest for drop.
- m90-m92: line 23 keep for approve. This line alone fails the case.
- m34-m35: lines 2 and 3 contest for rewrite; line 7 rewrite for revise.
- m61-m62: line 5 drop for rewrite ("has to touch the clear function").
- m75-m76: line 1 approve for add, his_words "no words".

## 4. The lever (reasoned: lines counted from the table above)

1. Prompt, landing.md lines 14 and 21. Add to `approve`: "Line 4 reads my last
   answer correctly", "keep line 9 as it is" and "lines 2 to 6 are ok" approve
   those lines. Narrow `keep` to "keep line 4, but fix its check", and say that
   keep words with no fault are `approve`. Why: 42 of 65 verdict-wrong lines
   carry plain agreement, and m90-m92, m116-m118 and m121-m122 pass on it.
2. Prompt, line 17 `drop`. Add: words that say he never asked for what the line
   says, "I asked only for X", drop the line. Why: 15 lines, m97-m98 passes
   and m90-m91 reads 3 of 3; the seat already gives drop on the same words in
   2 of 3 runs, so the sentence settles a coin toss.
3. Prompt, lines 19 and 20. Add to `exclude`: words that take a file or a test
   off the touch line are `exclude`, also when they say "remove" or "keep line
   5 to X". Re-judge m92-m93 line 2 to drop, the words "not in a test file"
   name the line's only path. Why: 9 lines, and with change 1 the cases
   m74-m75, m76-m77 and m92-m93 pass.
