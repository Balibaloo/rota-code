# Frame 306, W-A pass 1 review, at 2a464938

Verdict: Does not stand. The row narrowing can attach a sentence with no line number to the wrong row (finding 1).

## (a) The points

1. Partial. The c1 wake holds the line 2 sentence and its legend, and nothing for lines 4 to 7. The wake also holds "change line 3 so ..." and "line 3 was c2". A seat can read that as a second instruction (finding 4).
2. Holds. The Developer block holds his words whole, then "line 3 was crit_2_..." and "line 4 was crit_3_...". No docstring line appears.
3. Holds with a defect. Both legends are byte-equal on the s132 fixture (A, lines 6-7 and 15-16). They can differ when one wake repairs two rows of one ruling (finding 3).
4. Fails for the wake, holds for the block. The repair wake changes without an order (finding 2). The block is byte-equal with and without a line (D1, D2). A live night reaches the fallback only on a pre-272 database or a reply with an empty `ask.order`.
5. Holds. The three reds fail at 03f6e900 and at 2a464938 with the same three assertions. Only the print order differs.
6. Holds. 172 passed. The commit edits no existing test. The byte-compare pins the 03f6e900 block for no-line words with an order. A format change in `_contest_block`, or a legend on no-line words, breaks it. No test pins the repair wake without an order.
7. Holds. No case yaml seeds an `order:<reply id>` row, so no recorded Terminologist prompt changes. The relay legend reads right (E, E2). It names every line his words name, also lines outside the relay.

## (b) Findings

1. `rota/core/runner.py` 575-594 `_words_on_rows`, high, CONFIRMED. `_ruling_words_on` keeps every sentence with no line number for every row. The narrowing then cuts the sentence that gives the pronoun its referent. Probe B2: "Line 2 should only apply when ... Line 4 is wrong. Delete it." The c1 wake reads "Line 2 should only apply when the roaming flag is True. Delete it." The 03f6e900 wake keeps "Line 4 is wrong" before "Delete it". Test 3 of the commit uses this same shape, "Line 4 is wrong. Drop it." Fix: bind a sentence with no line number to the lines of the sentence before it, and keep it only with them.
2. `rota/core/runner.py` 560-563, low, CONFIRMED. The instruction "Write the behaviour his words ask for." replaces the old one also without an order. Probe B diff shows one changed line. No cassette holds a repair-wake quote (0 of the cassettes), so no case goes stale. The mode page `terminologist/criterion_repair.md` line 26 still says "Write the criterion in the principal's words." Fix: keep the old sentence when the legend is empty, or change the mode page in the same commit.
3. `rota/core/runner.py` 555-557 and 714-718, low, PLAUSIBLE. The quote narrows to one ref, and the block narrows to all refs of the ruling on the wake. With c1 and c2 woken from one ruling, the block legend names more lines than each quote legend. The map is the same, but the seat reads two lists. Fix: pass `on_rows=True` without a legend, so the legend shows once, under the quote.
4. `rota/core/runner.py` 597-650 `_line_legend`, low, PLAUSIBLE. The c1 wake names "line 3 was c2" beside an imperative on line 3. Nothing says c2 is outside this repair. Night 165 shows a seat that copies other rows' sentences into the woken row. Fix: on the repair wake, mark a legend row that is not the woken ref as "another criterion, not this repair".
5. `rota/core/runner.py` 641-644, low, PLAUSIBLE. An uncontested row shows the latest criterion version. A row revised after his reply shows text he never read. Fix: read the version current at the reply's seq, or name the id alone.
6. Outside. The gate stored a baseline at 2a46493 for the worktree on its first run. Its "new reds 0" therefore compares 2a464938 with itself. The suite gave 9 failed. The stale set was not measured, because the worktree has no register.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/r306wa/`.

- `old/`: `git archive 03f6e900 rota tests`, plus a copy of the cassettes and `pyproject.toml`.
- `probe.py`: builds fixtures A, B, B2, C, D1, D2, E, E2 with the commit's seed helpers. It ran with the `rota` of each tree. Output is in `new/` and `oldout/`. A `cmp` gave SAME for D1 and D2 only.
- `p5_old.txt`, `p5_new.txt`: the three old reds at each tree.
- The pin files through pytest: 172 passed. The gate: 9 failed, 4774 passed, 0 new reds against its own baseline.
- A read-only count over `cassettes.db`: 0 repair-wake quotes, 51 "He said" lines that name a line.

## (d) Usage

About 55k input tokens, 10k output tokens, 65k total.

## Re-check of 2ece9cd2

1. Finding 1 is closed. On B2, the c1 wake holds "Line 2 should only apply when the roaming flag is True." alone. The c3 wake (line 4) holds "Line 4 is wrong. Delete it." together.
2. Finding 2 is closed. Without an order, the repair wake is byte-equal to `oldout/B_s132_noorder.txt` (`cmp` by the reviewer).
3. Finding 3 is closed. Each repair wake shows one legend, under the quote. The Developer block on the s359 fixture keeps its 5 legend lines.
4. Finding 4 is closed with a low defect. The mark reads "line 3 was c2: ... AppData Local folder, another criterion, not this repair". The mark joins c2's text with a comma, so a seat can read it as part of the criterion. Fix: put the mark before the text, "line 3 was c2 (another criterion, not this repair): <text>".
5. Check lines: medium, CONFIRMED. The s132 fixture has no check rows. There "Line 3's check is wrong." stays on the c2 wake only, which is correct. With a test id on line 4 (`t_2`, the check of crit_2), the crit_2 wake keeps "Line 3 is fine." only. It loses "Line 4 is wrong. Drop it." `api._ruling_words_on` keeps "Line 3 is fine. Drop it." for the same wake. Fix: count the line of each check of a criterion as that criterion's row in `_words_on_rows` and in `api._ruling_words_on`.
6. Pins: the seven `test_frame306_*.py` files give 85 passed. The commit removes two assertions and replaces each with a stricter one. It weakens no assertion.

Probe: `scratchpad/r306wa/probe2.py`, with output in `new2/`.
Usage of the re-check: about 9k input tokens, 3k output tokens, 12k total.

Stands. The check-line gap (point 5) is a follow-up, not a block. The same gap was in `api._ruling_words_on` before this frame.

## Re-check of 28f1b719

1. Closed. The words are "Line 2 is fine. Line 4 is wrong. Drop it.", and line 4 is `t_2`. `api._ruling_rows` returns {3, 4} for crit_2. The crit_2 wake through `build_prompt` holds "Line 4 is wrong. Drop it." without "Line 2 is fine.", so the whole-words fallback did not run.
2. Closed. The mark now stands in brackets before his text: "line 3 was c2 (another criterion, not this repair): When ...". It reads as a mark, not as his words.
3. Closed. The Developer block for a ruling that names no line, with the order recorded, is byte-equal to the 03f6e900 tree (`cmp`).
4. The pins pass: 7 `test_frame306_*.py` files plus 6 files of `test_frame308_*` and `test_frame283_*` give 248 passed. The commit replaces two mark assertions with assertions for the new form, and weakens no assertion.
5. The fault path has a missing pin, not a confirmed defect (PLAUSIBLE). `_words_fault_on` now gets sentences about a check, but `_sentence_hits` still filters them on the criterion's own line from `_ruling_line`. Fix: add one test, a faulted-check sentence under a recorded order that opens no words fault.

Probe: `scratchpad/r306wa/probe3.py`, with output in `new3/`. Usage of the re-check: about 7k input tokens, 2k output tokens, 9k total.

Stands.
