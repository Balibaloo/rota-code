# The reach of fifteen closed frames, 2026-10-26

Roman asked on 2026-10-26 at about 21:5x: "send another agent to review frames resolved in the last two weeks to see how much work should have been generalised". This record reads the 15 frames of `plans/archive/stack-2026-10-23.md`, `stack-2026-10-24.md` and `stack-2026-10-26.md`. Five read-only agents on Opus read the frames, 2 to 4 frames each, and counted the reach with `git grep` at each closing commit and at head d1c934ae. This session checked the cycle lines by script and spot-checked three counts at head (321, 317, 297).

## The result

Ten of 15 closed frames fixed one door of N (observed: the table). Two fixed the fact at the source, 309 and 321. One rested on a wrong premise, 297. Two are not this shape, 323 (a model trial) and 310 (a duplicate of 257). The 15 frames cost about 164 cycles. A fix at the source of each fact prices at 70 to 83 cycles by the anchors, and at 54 to 63 when one seam serves 258, 305 and 308 (reasoned: the last section).

## The table

| Frame | Closed on | The fact | Reach then | Reach now | Later frames | Verdict |
|---|---|---|---|---|---|---|
| 307 | 2026-10-23 | the guess a page showed, the `code:<message>` stamp; the commit landed after a turn | 1 of 3 stamp readers; 1 of 2 landed-commit readers | 3 and 2, unchanged | none | at one door of 3 |
| 310 | 2026-10-23, popped | 257's fact | 0, no fix | see 257 | see 257 | not this shape: a duplicate |
| 309 | 2026-10-24 | every execution of a test, one row | 1 of 1 writer, 1 of 1 reader; the id-table fact 1 of 2 | 1 reader; the id-table fact 2 readers, 2 rules | none | at the source |
| 297 | 2026-10-24 | law 4, the tree holds no line a commit does not hold | the discard 3 of 3 at close; the furniture fact 1 of 5 | discard 3 of 3; furniture 5 places, 2 rules | 306, 312, 339 | wrong premise |
| 301 | 2026-10-24 | which names in a test body mean click | 0 of 2 own rules (6 readers) | 8 readers, 4 own rules | 304, 328 | at one door of 6 |
| 302 | 2026-10-24 | a path a seat names is a file `code_index` holds, in `_grain_path`'s form | 1 of 8 membership readers; 6 path-form rules | 9 readers; 7 path-form rules | 328, 306 | at one door of 8 |
| 308 | 2026-10-24 | what his ruling's words ask of one page line | 2 of 7 cue families | 7 families, still separate | 329, 337, 338, 339 | at one door of 7 |
| 272 | 2026-10-24 | the row order of a page as he saw it | 1 of 4 line-to-row mappers | 7 readers: 4 read the record with 4 fallbacks, 3 render today | 305, 306, 308 | at one door of 4 |
| 257 | 2026-10-24 | the criteria a session holds now, staged over landed | 1 of 2 writer ops; staged readers 6 | staged readers 10; `respecify` still has no surface door | 315, 322, 324, 329 | at one door of 2 |
| 258 | 2026-10-24 | which lines his words fault, line 1 included | 1 of 5 request-line deciders; 12 `_LINE_REF` readers | 6 deciders; 16 readers | 289, 299, 305, 315, 337 | at one door of 5 |
| 305 | 2026-10-24 | which numbered lines his words fault, drop, approve or name | 3 of 7, and 1 of the 3 is a new rule | 7 readers, 6 own rules; raw scans 12 to 15 | 306, 308, 337 | at one door of 7 |
| 317 | 2026-10-24 | the live test of a criterion and its run's raising line | lookup 1 of 9 as a new rule; raising line a 9th rule | lookup 10; raising line 12 | 318, 336 | at one door of 9 |
| 321 | 2026-10-26 | whether a criterion's prose says it prints | 2 of 2, one helper | 2 readers, one helper | none | at the source |
| 283 | 2026-10-26 | which base statements the batch's tree no longer holds | 1 of 10 removal finders | 10, unchanged | 297, 305, 306, 308, 312, 313, 339 | at one door of 10 |
| 323 | 2026-10-26 | none, a model trial | n/a | n/a | 326, 327 (trial tools) | not this shape |

## The frames

**307.** `api.py:code_stamp` already served `rulings_rule` and `principal.land`, and the fix gave `nightreport.py:_guess_section` its own parse and a third fallback rule (observed: git grep `code:|code_stamp\(|FROM touch_guesses` at b798cb90, nightreport.py 353 to 413). The landed-commit counter at `nightcount.py` 167 changed, and the tree reader at about 215 kept its own rule (observed: the same grep). The pass 1b note shows the cost: the tool's M0 and the night read's M0 "measure different sets" (observed: status 2026-10-23 14:49). No later frame came back, so the cost stays low (reasoned).

**310.** The frame named the reused-id check of `criteria_specify` and was popped before any fix (observed: the pop line). Its provenance read became 257's evidence (observed: 257, status 2026-10-23 20:44). A second frame on one fact opened because the push read the night and not the stack, which C76 step 2 now stops (reasoned).

**309.** One writer, `lifecycle.py:record_test_run`, and one reader, `nightreport.py` 703 to 724, hold the run history, at close and at head (observed: git grep `test_run_journal` at a970d886 and d1c934ae). The overrun to 5 cycles came from five registers that each declare the tables: `schema.sql`, `identity.py`, `_NOT_REFFABLE`, `scenes.TIMED` and a schema test (observed: statuses 18:49 to 20:34). A sixth, `tools/audit.py:_ids` 47 to 54, still counts the journal's ids, and `identity.py` 108 still calls `test_runs` "one execution, one row" (observed: head).

**297.** The pushed cause was wrong: s214 wrote its own note, and no relay read a quarantined write (observed: status 16:49). About 4 cycles built a ledger door that pass 4 made read-only and frame 283 later found dead (observed: stack-2026-10-26 line 63). The end fix is at the source: three session ends call `lifecycle.discard_uncommitted` (observed: boot.py 192, runner.py 6373 at head). The fact "a batch's test files are furniture" kept 5 places with 2 rules, and `lifecycle.py` 289 copies `_uncommitted`'s rule by its docstring (observed: git grep at c0549d84 and head).

**301.** `api.py:_click_names` held the fact, and its default would have resolved s266's decorator (reasoned: 6668 against 7013 at f6a80169). The fix added a hop to `_invoked_command_calls` and left its own `import click` rule (observed: the diff). Frame 304 then added two more own rules, at 17803 and 17865, so 2 own rules at close became 4 at head (observed: git log -S, git grep at head). Every rule hardcodes the library "click", which does not transfer to another project (reasoned: the intent page, "prevent over fitting").

**302.** Eight places compare a seat's path with the index, each with its own form, and `_grain_path` already folded `::`, `\` and `./` (observed: git grep "grain_kind = 'path'" at 045ab3b1). The fix built `file_half` and `test_shaped` as a sixth path-form rule and a sixth test-file rule, and passes 1b and 1c re-derived the `::` fold one review at a time (observed: 997ec895, 6add96c2, 1c9ca3ea). Frame 328 met the same `./` form at `tests_encode` and added `normpath` there only (observed: stack.md 1436 to 1438, api.py 9249). Passes 2 to 2c, a new file named by a seat, are a separate question (reasoned).

**308.** Seven cue families read his words, each with its own regex list, and the fix widened two of them (observed: git grep `^_[A-Z_]* = re.compile` at 045ab3b1). The session named the shape at 19:19, "a word list that leaks, the same shape as frame 305's reader", and still widened its list through five more passes (observed: the 19:19 status). `_LINE_FAULT` at api.py 9970 already listed "isn't right", the phrase review 6 left as residue (observed: 045ab3b1). Frames 329, 337, 338 and 339 sit at the same words (observed: their agency reads).

**272.** The fix built the right record, `order:<reply id>`, and moved one reader of four onto it (observed: git grep `render_page\(|f"order:` at 695e8be7). Frames 306 and 308 each added a reader of the record with its own fallback (observed: `_line_legend`, `_ruling_order`). At head `rulings_rule`, `rulings_line` and `resolve_inbound` still render today's rows (observed: api.py 12492, 12916, runner.py 2574). So the shift frame 308 met at m98 is still possible where his rulings land (reasoned).

**257.** The same-ticket refusal went into `criteria.specify` only, and `criteria.respecify` reads no staged text (observed: api.py 5937 at 87dc9910). Review 2 named the gap as "residue for a later cycle", and frame 329 then found the same split for the twin door (observed: stack.md, frame 329). Staged-criteria readers of `ctx.writes` went from 6 at close to 10 at head, each with its own rule for ticket and retired rows (observed: git grep `w\[0\] == "criteria"`). Frames 315, 322 and 324 also sit at this door (observed: stack.md headings).

**258.** Eight passes over nine days changed 3 of 5 deciders of line 1 and left `_assert_words_fault` and `pointer_fault` (observed: git grep at fe4b3c78). The 2026-10-24 provenance found the spare rule "shares one content word with the request", one door's private rule for a shared fact (observed: `plans/frame258-provenance.md`). Readers of `_LINE_REF` went from 12 to 16 (observed: git grep at head). Frame 337's read lists 14 doors on `words`, and 258's three doors are among them (observed: `plans/frame337-agency-read.md` lines 53 to 66).

**305.** The fix rebuilt `_line_cues` and `returned_line` and added `_note_words` as a new rule, and four readers kept their own (observed: git grep at c12c42b7). It ran beside frame 308 on the same evening, and each widened its own cue list (observed: both blocks, 2026-10-23 19:19 to 19:24). The frame wrote the shape itself, "the fit trap from the other side" (observed: status 19:22). One line reader of his words would have taken the cycles once, not again in 308 and 337 (reasoned).

**317.** The criterion-to-test lookup had 8 readers with three filters, and the fix added a ninth with a fourth filter (observed: git grep `criterion_id *= *\?` at 51b5fa07). Review 1 found the raising-line search wrong, and pass 1c copied the first-`E ` rule a ninth time (observed: status 06:51, the diff). Head holds 12 raising-line readers (observed: git grep `startswith\("E ` at d1c934ae, checked by this session). Frame 336 proposes one `error_line()` for the same fact (observed: `plans/frame336-agency-read.md` section 2).

**321.** The brief asked for "one helper the encode door and the triage wall share", and the commit delivers `_plain_words` for both (observed: status 2026-10-24 23:36, api.py 7765, 7766, 10564 at head). The provenance counted the reach before the pass (observed: the Site line). One gap stays open: `_about_text` has one reader, so the triage wall does not apply the docstring exemption (observed: api.py 10557, 10565). No night shows the gap (reasoned: no later frame).

**283.** Ten functions find "what this change removes", seven on one write and three against the base (observed: git grep of the ten `def`s at 205a43fb). The fix recorded removals per write as `drop_notes` rows, and four of the seven write rules were added during the frame, one per night wall (observed: `git log -S` on each `def`). `_removed_lines` existed from 2026-09-30 and `_base_text` from 2026-10-17, so one base-against-tree reader was open from the start (reasoned: the dates). Seven later frames sit at the same fact, and 339's read calls its removal door a wrong premise (observed: `plans/frame339-agency-read.md`).

**323.** The frame trialled `gemma4:12b-it-qat` per seat, and Roman ruled "no switch, qwen3.5:9b stays in every seat" (observed: status 2026-10-26 18:26). No fact has readers here (reasoned).

## The counts

- At the source: 2. Frames 309 and 321.
- At one door of N: 10. Frames 307, 301, 302, 308, 272, 257, 258, 305, 317 and 283. The median N is 6.5, and the median fix covered 1 (observed: the table).
- Wrong premise: 1. Frame 297.
- Not this shape: 2. Frames 310 and 323.

Later frames at the same fact: 9 of the 10 one-door frames have them, 32 links in all (observed: the table). Frame 283's fact draws seven later frames. The words-to-lines fact of 258, 305 and 308 draws 337, 338, 339 and 329 (observed: the table).

## The cycles

Actual, from the closing and the last counted status lines: 307 2, 310 1, 309 6, 297 19, 301 7, 302 10, 308 17, 272 5, 257 6, 258 about 18, 305 about 19, 317 4, 321 3, 283 47. Sum: about 164 (observed: "Cycles: x of y" and "Actual" lines; 258, 305 and 317 reasoned at one cycle per agent run, because their close lines carry no count). Frame 283's counter restarted three times, so its per-series sum is about 70 and the sum is then about 187 (reasoned: series of 26, 1, 15, 7, and 26 to 47). Frame 323's block carries no cycle line, and it is not in either sum.

At the source, by the anchors of `plans/operating-facts.md` line 247: 307 3, 310 0, 309 3, 297 8 to 10, 301 3, 302 3 to 4, 308 8 to 10, 272 8 to 10, 257 3, 258 8 to 10, 305 8 to 10, 317 5, 321 2, 283 8 to 10. Sum: 70 to 83 (reasoned: an instrument fix 3, a door text 2, a seam with its night 8 to 10). 258, 305 and 308 share one fact, so one seam serves the three, and the sum is then 54 to 63 (reasoned: the table).

The gap is 81 to 94 cycles by frame, and 101 to 110 with the one seam, about 2 to 1 or more (reasoned: the sums). Two doubts stay. First, a source fix priced at 8 to 10 rests on the anchor, not a measured case. Frame 272's source fix costs more than its actual 5, and it pays back only through the later frames. Second, which readers count as one gap is the agents' judgement, and frames 257, 258 and 297 name their criterion in the paragraphs.
