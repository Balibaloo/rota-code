# Seam review, pass 1: 69561d5b on rota_rseam, against 3b31077a

**Verdict: NOT READY.** The commit refuses the three removals the read named. It still lands two removals that his words do not ask for. The W9 span hides a fault of this page, and a probe lands a wrong approve. Findings: 3 high, 4 low.

## (a) Verdicts on the points

1. W16: not met. s179 on m62 and s165 on m52 are refused, and r_m121 stays refused. r_m75 and r_m97 land, but neither removal is his (finding 2). A request with no code name grants any target (finding 3).
2. W9: not met. A report verb hides a fault of this page in 8 of 12 probe forms. A door probe lands an approve on a line his words fault (finding 1). "I did not say line 4 is wrong" faults no line at the parent and at the commit, so the negation gap does not change.
3. Replay: 290 calls, 18 results move. 17 are right on his words. One, s120 call 3 on m35, lands a revise his words do not hold (finding 7).
4. Tests: pass. The 35 files that name `rulings.rule`, the new file included, and the 6 known-red files give 1180 passed, 17 xfailed and 6 failed. The 6 are the known 6. The diff holds no CR byte. Its 8 hunks are all in the claim.

### Point 1, his words for r_m75 and r_m97

- m75: "only the docstring in the utils file changes, so please remove the five formatting tests from what you expect to touch". He asks the plan to touch the tests less. He does not ask to delete a test. The landed act is `remove` on `tests/test_formatting.py::test_formatting_with_options_metavar_empty`. `granted` reads that act as his permission for `_unruled_gone` to spare the deletion of that test. So the removal is not his.
- m97: "only the docstring in the utils file changes, so please drop all three formatting tests". "Only the docstring changes" excludes a change to a test, and a deletion is a change. So the drop is not his, by the same reading.
- The read, section 4, calls both right. That reading confuses "remove from the page" with "delete the code". Tests 170 and 183 of `tests/rota/test_seam_night173.py` pin the wrong reading.

### Point 3, the moved results

| Night, session, call, reply | Parent | Commit | Right on his words? |
|---|---|---|---|
| 171 s139 6, m41 | "lines 1, 4 have no ruling" | W16 refusal of `drop` on `tests/test_utils/test_get_app_dir.py` | yes. "put the new tests with the other utils tests" asks to place tests, not to delete a file |
| 171 s139 7, m41 | stray-fields text names line 4 as faulted | the same text without line 4 | yes. "the old line 4" is of the earlier page |
| 171 s139 9, m41 | "The words name lines 4, 6 and 7" | "The words name lines 6 and 7" | yes, the same reason |
| 172 s91 3, m7 | "lines 1 to 12 have no ruling" | W16 refusal on line 7 | yes. His line 7 sentence faults a glossary row and asks no removal of `keepopenfile` |
| 172 s91 5, m7 | lands, line 7 `remove` on `keepopenfile:7` | W16 refusal on line 7 | yes, the grant was not his |
| 172 s107 2, m25 | AS refusal on line 4 | W16 refusal of `remove` on `src/click/_winconsole.py` | yes. "the function I named lives in click's utilities file" asks no deletion |
| 172 s199 2 and 4, s200 2, 3 and 5, m84 | NM, "do not name line 2" | lands, 1 approve, 2 contest, twice with `drop` on the row | yes. "I said line 1 is right" reports the earlier answer, and "drop the second line" contests line 2 |
| 173 s91 3 and 5, m7 | as night 172 | as night 172 | yes |
| 173 s120 2, m35 | fault of lines 1 and 4 | lands, c_3 approve | yes, the W9 target case |
| 173 s120 3, m35 | fault of line 1 | lands, c_3 `revise` | no. His words fault no part of c_3 (finding 7) |
| 173 s165 2 and 3, m52 | AS refusal on line 3 | W16 refusal on line 2 | yes. "not the string helper" asks no removal of `make_str` |
| 173 s179 1, m62 | "bg_2 is merged" | W16 refusal on line 5 | yes. He asks to name `clear`, not to remove it |

Totals: 7 refusals become lands, 2 lands become refusals, 9 refusal texts change, 0 errors move. The replay does not restore the batch state of night 173. Both trees run on the same state, so each move comes from the code.

## (b) Findings

1. **rota/roles/api.py 12207 to 12241, high. CONFIRMED.** `_reported` runs a report span to the sentence end when no join word follows. A clause of this page after a bare comma or a bare "and" loses its line. `door9b.py` puts "I asked for two checks, line 4 adds a third." in m35 and approves line 4. The parent refuses on the fault "adds". The commit lands the approve. `w9.py` shows the same loss for "I asked for one test, line 3 adds five.", "I did not say line 4 is right, line 4 is wrong.", "I said line 1 is right and line 9 is a made-up answer." and "I approved three lines, and line 9 was never my answer.". Fix: end the span at the first clause after the object that has its own line subject and a present verb.
2. **rota/roles/api.py 23738 to 23754 and tests/rota/test_seam_night173.py 170 to 195, high. CONFIRMED.** `_asks_removal_of` passes "please remove the five formatting tests from what you expect to touch" for a test target. The replay lands s192 call 2 with `remove` on the test. `granted` then permits the deletion of a test that he asked the change not to touch. r_m97 has the same shape. Fix: refuse a code-kind removal whose clause removes the object "from" the page or the plan, or whose sentence says only another thing changes, and change the two tests to expect a refusal.
3. **rota/roles/api.py 23748 to 23752, high. CONFIRMED.** A removal clause with no code token grants every target. `w16.py` gives True for "remove the string helper, not the clear function" on `src/click/termui.py::clear`, and for "please delete it" on any target. So the m52 pattern with a removal verb still grants the reverse of his words. Fix: when the clause names no code token, require the target name or its plain-word kind in the clause object, and refuse an object that a "not" clause names.
4. **rota/roles/api.py 23749, low. CONFIRMED.** `_removal_spans` reads "drop nothing" as a request. `w16.py` gives True for "keep the clear function, drop nothing" on `clear`. The reader is older, but the W16 check now makes its answer a grant. Fix: skip a removal clause whose object is "nothing" or "none".
5. **rota/roles/api.py 14090, low. PLAUSIBLE.** The check reads only the four code kinds. An act with a code target and no `target_kind` skips the check. The builder reports that `granted` matches a target of any kind. Fix: check every kind except `row`, `check` and `request`.
6. **rota/roles/api.py 12254 to 12263, low. PLAUSIBLE.** When every number of a reply sits in a report, the reply names no line, and the naming door then spares any contest. m84 moved from an NM refusal to a land in this way. That land is right, but the door no longer guards such a reply. Fix: add a test that pins the m84 land and refuses a wrong contest beside it.
7. **Outside. rota/roles/api.py, the revise path of `rulings_rule`, low. CONFIRMED by the replay.** s120 call 3 on m35 lands `revise` on c_3 at the commit. The parent refused the call on line 1. His words fault no part of c_3. In the night, call 2 now lands first, so the seat would not make call 3. Fix: refuse a revise of a line that `_line_reading` of his reply does not fault.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/rsrev/`.

- `regs/`: copies of `.rota/clickI_night170.db` to `clickI_night173.db` with their WAL and SHM files. The probes open only these copies, and each call runs on an in-memory copy.
- `parent/`: `git archive 3b31077a rota`, the parent tree.
- `replay.py`: replays all 290 `rulings.rule` calls of nights 170 to 173 at one tree, the method of `plans/f2-review-p2.md`. The results are in `par.json` and `new.json`. `diff.py` prints the 18 moved results.
- `texts.py`: prints m75, m97, m41, m25 and m84, and the replay results of s192 and s222.
- `w16.py`: 16 spans through `_asks_removal_of` and `_removal_spans` at the commit.
- `w9.py`: 18 sentences through `_line_reading(words, 10)` at the parent and at the commit.
- `door9.py` and `door9b.py`: the verdicts of s120 call 2 on m35 with one sentence changed, at the parent and at the commit.
- Tests: `pytest` on the 35 files of `tests/rota` that name `rulings.rule` and the 6 known-red files, at the commit. 6 failed, the known 6, 1180 passed, 17 xfailed.
- `git diff 3b31077a 69561d5b`: 0 CR bytes, 8 hunks.

## (d) Usage

Input about 64k tokens, output about 16k tokens, about 80k in total. These are estimates. The cap was 50k. The replay output, the test run and a failed report write used the rest.

## p2

**Verdict: NOT READY.** Pass 2 at d28e6e05 closes the three highs of p1, and all 19 replay moves are right on his words. The new revise check refuses a revise that he asked for, and its refusal text leads to a wrong approve. Finding 5 of p1 is a law 6 hole and blocks the land. Findings: 2 high, 4 low.

### (a) Verdicts on the points

1. Highs of p1: closed. `w16b.py` gives False for the m75 span, the m97 span, "remove the string helper, not the clear function" and "keep the clear function, drop nothing". The replay refuses s192 call 2 on m75. `door9b.py` refuses the approve of line 4 on "adds", as the parent does.
2. Replay: 19 moves, the same 19 that the builder lists: 7 refusals become lands, 3 lands become refusals, and 9 texts change. Each move is right on his words. The 18 moves of p1 keep the p1 reading. 170 s192 2 on m75 is new, and its refusal is right. 173 s120 3 is now refused, which is right. The parent results equal those of p1.
3. Revise check: it refuses a right revise. "Replace Roaming in line 4 with Local." faults no line, so the revise of line 4 is refused, and the approve then lands (finding p2-1). 11 other phrasings fault line 4.
4. Findings 5 and 6 of p1: finding 5 is a law 6 hole, and it blocks (finding p2-2). Finding 6 is no law 6 hole. The door writes no verdict there, and the m84 land is right. It stays low.
5. Tests: pass. The 35 files that name `rulings.rule`, `test_f2_line_parser.py`, `test_frame305_line_reader.py` and the 6 known-red files give 1205 passed, 17 xfailed and 6 failed. The 6 are the known 6. The diff of pass 2 holds no CR byte. Its 9 hunks are in the claim. The `PARSER_SITES` hunk lists `_reported` as a parser site.

### (b) Findings

- p2-1. **rota/roles/api.py 14268 to 14279, high. CONFIRMED.** The revise check reads a revise as right only when `_line_reading` faults the line. "Replace Roaming in line 4 with Local." faults nothing, so the door refuses the revise of line 4 on m35. The refusal says "Approve line 4". The probe then sends line 4 `approve`, and the call lands. So the check turns his request for a change into a landed approve. Fix: accept a revise when his sentence that numbers the line holds an edit verb ("replace", "change", "reword", "rewrite", "say"), or refuse with a text that offers contest, not approve.
- p2-2. **rota/roles/api.py 14090, high. CONFIRMED for the land, PLAUSIBLE for the grant.** The W16 check runs only for the four code kinds. The call of s179 on m62 with no `target_kind` lands `remove` on `src/click/termui.py:clear`. `grant` in `rota/roles/principal.py` 839 to 842 matches a row by its target alone. `_on_the_row` gives False for a kind of None, so a later plain verdict does not end the row. 6 of 133 removal acts with a target in the 290 calls carry no kind, so seats do send this form. Fix: run the check for every kind except `row`, `check` and `request`, a missing kind included.
- p2-3. **rota/roles/api.py `_target_names`, low. CONFIRMED.** The file stem counts as a name of the target. "remove the helper in the termui file" grants a removal of `src/click/termui.py::pause`. Fix: accept the file stem only for a `path` target.
- p2-4. **tests/rota/test_seam_night173.py, the m17 case, low. CONFIRMED by the builder's test.** m17's "and only lines 18 to 28 were wrong" now faults line 18 of this page again. The read puts line 18 on the earlier page. The result is a false refusal of an approve, not a wrong land. Fix: none in this frame. Count it on the next night.
- p2-5. **rota/roles/api.py `_reported`, low. CONFIRMED.** "I asked you to drop line 3 and it is still on the page." still hides line 3. The bare "and" joins no second reference here, so the span should end, but line 3 sits in the object. The line is in the report object, so the rule reads it as the earlier page. Fix: none. The sentence is ambiguous on his words.
- p2-6. **Finding 6 of p1, low. PLAUSIBLE.** Unchanged. A reply whose numbers are all reported names no line, and the naming door spares any contest. Fix: add a test that pins the m84 land and refuses a wrong contest beside it.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/rsrev/`.

- `regs2/`: fresh copies of the four registers. The WAL file in `regs/` was gone, so I copied again before I opened them.
- `replay3.py`: `replay.py` on `regs2/`. `par3.json` is the parent, and it equals `par.json`. `new3.json` is d28e6e05. `diff3.py` writes the 19 moves to `p2moves.txt`.
- `w16b.py`: 10 spans through `_asks_removal_of`. `w9.py` and `door9b.py`: the p1 probes at d28e6e05.
- `rev.py`: 12 revise phrasings through `_line_reading`. A stdin probe puts "Replace Roaming in line 4 with Local." in m35, then rules line 4 `revise` and `approve`.
- A stdin probe runs the s179 call on m62 with and without `target_kind`, with bg_2 set to `pending`.
- A stdin probe counts removal acts with no kind in `new3.json`.
- Tests: `pytest` as in point 5.

### (d) Usage

Input about 24k tokens, output about 7k tokens, about 31k in total. These are estimates. The cap was 30k.

## p3

**Verdict: NOT READY.** Pass 3 at cb7783db and 5cd73a2d closes both p2 highs on the probed forms. The new removal verbs, the page-noun rule and the unchecked `exclude` each land a row that his words do not ask for. A target-less `remove` now lands, and it was refused at d28e6e05. Findings: 4 high, 2 low.

### (a) Verdicts on the points

1. p2 highs: closed on the probed forms. "Replace Roaming in line 4 with Local." lands the revise, a plain fault lands it, and a reply that faults nothing is refused with no approve in the text. s179's call on m62 with no `target_kind` is refused, with the full target and with `clear`. A new hole opens beside p2-2 (finding p3-1).
2. `exclude`: no `exclude` row reaches a removal reader. `grant` lets the newest act on the target decide and returns a row only when its act equals the asked act. Exclude then remove: `granted(remove)` True, `disputed_paths` empty. Remove then exclude: `granted(remove)` False, the path disputed. `_unruled_gone` and frame 339's `_asks_removal` read only `remove` and the criterion text, never `exclude`. Both orders are right on his words.
3. Missing check: an `exclude` lands on any target, any kind, and on words that ask the opposite (finding p3-4). Law 6 is broken: the row is "a ledger row written on the principal's behalf". For a batch ref, `predicted_rows` in `rota/core/lifecycle.py` 442 to 478 (37 lines) gives the paths. For a guess key, no single function does. `code_target` in `rota/roles/principal.py` 1593 to 1607 gives the stamp, and a 4-line `touch_guesses` query gives the paths, as `resolve_inbound` does.
4. Page-noun rule: a reading beyond his words, by law 6. High (finding p3-3). The prompt's example gives True. Two flags on one page: "I don't want a flag" names both `show_python` and `verbose`. No page noun: False. "I don't want a test" names `show_python` when the page writes "the show_python test".
5. Prompts: the `path` example shows his words beside the act. The acts-list line has 18 words, and its second sentence has 6. The example has no `words` key, so a seat that copies it is refused once, as with the older examples (low). The `remove` line still says it takes "a file away" (finding p3-6). New stale cases: 0. `casestatus` gives 59 stale on both trees, 11 of them Liaison cases, the same set.
6. Replay: 25 moves against 3b31077a, the builder's 25. 18 equal p2's moves and keep p2's reading. 7 change text only: 6 "is not an act" refusals now list `exclude`, and 173 s120 3 drops "Approve line 4". No wrong move. No decision changes.
7. Tests: 39 files, 1 failed, 1084 passed, 13 xfailed. The red is `test_pins.py::test_with_prompt_keeps_every_pin`, a known red. The diff holds no CR byte. The worktree stays clean.

### (b) Findings

- p3-1. **rota/roles/api.py 14105 to 14114 and `_code_target`, high. CONFIRMED.** `_code_target("")` gives False, so a `remove` with no target skips the removal rule. s179's m62 words with `act` `remove`, kind `identifier` and no target land at 5cd73a2d and are refused at d28e6e05. `grant(ref, "remove")` with no target reads that row, so `_amend_step` at 1534 and `_assert_words_fault` at 1881 let an amend drop his sentences (PLAUSIBLE for that effect). Fix: run the removal rule on every `remove` or `drop` whose target is empty, or is not a page line or a register ref.
- p3-2. **rota/roles/api.py `_REMOVAL_WORDS` 23603 and `_REQUEST_VERBS` 23627, high. CONFIRMED.** The "want" forms and "without" read the object as removed when the clause asks for no change. True at the W16 reader: "We do not want clear changed.", "I don't want any function renamed.", "Fix it without touching clear.", "Make it return True without changing the clear function." True at frame 339's `_asks_removal`: "We do not want ctx.exit() to change." and "Print the version without changing ctx.exit()." So the door can land a removal he forbids (law 6), and a stray removal hides as asked (law 12). Fix: count a "want" form or "without" only when the clause ends at its object, with no verb or participle after it.
- p3-3. **rota/roles/api.py `_asks_removal_of` 23816 to 23821, high. CONFIRMED.** The page-noun rule gives a name to every code target that the page writes before a noun. "I don't want a flag" names both flags of a two-flag page. "I don't want a test" names the flag `show_python` on a page with "the show_python test". "I don't want the flag to default to on." names it too. Fix: remove the rule, or accept the noun only when one target on the page holds it and the clause ends at the noun.
- p3-4. **rota/roles/api.py `rulings_rule`, the act check, high. CONFIRMED.** An `exclude` lands with only the span check. The words "the change has to touch the clear function in the terminal UI file" land `exclude` on `src/click/termui.py`. They also land it on `src/click/core.py`, which no prediction names, and on the identifier `clear`. `disputed_paths` then takes `src/click/termui.py` off `predicted_rows`. The prompts now send every path contest as `exclude`. Fix: refuse an `exclude` whose target is not a path of the ref's prediction (`predicted_rows`, or `touch_guesses` at the `code_target` stamp), or whose words do not name the target by `_target_names`.
- p3-5. **rota/roles/api.py 14280 to 14288, low. CONFIRMED.** `note_act` reads "Do not change line 4." as a change request. The revise of line 4 lands on that reply. The check at d28e6e05 needed a fault, and this reply faults line 7 only, so the parent refused it (PLAUSIBLE, not probed at the door). He sees the rewrite on the next page. Fix: give `note_act` the negation guard that `_NEGATION_WORDS` gives the removal reader.
- p3-6. **rota/roles/prompts/liaison/landing.md and answering.md, the `remove` line, low. PLAUSIBLE.** The line still says `remove` takes "code or a file away", beside the new `exclude` line. A seat can then send `remove` on a path for a touch-list correction. The W16 rule refuses it unless his words hold a removal verb. Then it lands as a code removal of the file. Fix: narrow the `remove` line to code at the next re-record, as the builder recommends.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/p3rev/`.

- `new4.json` and `diff4.py`: p2's `replay3.py` on `C:/Users/roman/rota_rseam`, against p2's `par3.json` and `new3.json`. `moves4.txt` holds the 25 moves.
- `probe.py`: opens `D:/repos/rota/.rota/clickI_night173.db` with `mode=ro`. It runs five revise replies on m35 (1a to 1e) and s179's call on m62 with no kind (1f, 1g).
- `probe2.py`: the same, with `bg_2` set `pending` in memory. It runs the target-less `remove` (1h), three `exclude` calls (3a to 3c) and `note_act` on "Do not change line 4.".
- `d28/`: `git archive` of d28e6e05. `probe2.py` on it refuses 1h.
- `probe3.py`: two seeded rulings in both orders on a fresh `init_db`, then `granted` and `disputed_paths`. Then 12 spans through `_asks_removal_of` and 3 criteria through `_asks_removal`.
- `probe4.py`: the prompt's `path` example with no `words`. The door refuses it.
- `t5cd73a2d/` and `td28e6e05/`: `git archive` of `rota` and `tests/rota`, with a hard link to a copy of the register. `cs_*.txt` hold the `casestatus` prints.
- Tests: `pytest` on the 6 named files and the files that name `rulings.rule`, `rulings_rule`, `disputed_paths` or `_asks_removal`.

### (d) Usage

Input about 70k tokens, output about 13k tokens, about 83k in total. These are estimates. The cap was 40k, and the review went over it.

## p4

**Verdict: NOT READY.** Pass 3c and 3d at 9b2d34d6 and 3944adee close five of the six p3 findings on their probes. The new clause start after "say" lands a rewrite that his words forbid, and an `exclude` still lands on words that name no path. Findings: 2 high, 4 low.

### (a) Verdicts on the points

1. p3 findings: p3-1, p3-2, p3-3, p3-5 and p3-6 are closed. A target-less `remove` is refused. All 15 "want", "without" and page-noun spans give False. "Do not change line 4." is refused as a revise. p3-4 is half closed (finding p4-2). The prompt example "Remove the show_python flag, I don't want it." gives True at `_asks_removal_of`, and the brief-example door test passes.
2. Exclude check: the m62 `exclude` on `src/click/termui.py` is refused, and so is the one on `src/click/core.py`. Both P10 tests pass. The check reads only the lines of the act's own ref, so a path on another line of the page is refused. m62 shows no path on any line, so this is read from the code, not probed. The check reads no words (finding p4-2).
3. No-target acts: a no-target `drop` never reaches `grant(ref, "remove")`, because the newest act must equal `remove`. No code removal reader reaches it, because those readers pass targets and `grant` then skips rows with no target. A no-target `remove` of kind `row`, `check` or `sentence` does reach `grant(ref, "remove")` (finding p4-5).
4. Fault A: `_lines_of` and `_ref_of_key` are right on the read. The remaining one-line readers change only refusal text, or read the first line where a reply can name the second (finding p4-6). `_backed` needs a connection, so I probed only its approve case. No wrong land was found.
5. Fault B: "Line 4 should say the local variable matters." lands the rewrite with his whole clause, and that is right. The s175 call 2 span is right by law 6. It keeps a whole clause, and the dropped ", not only that it might" restates his "for certain". A cut is right only when the dropped words do not negate or frame the kept clause. A cut after "say" can drop a negation before it (finding p4-1).
6. Replay: 27 moves against 3b31077a. 25 are the p3 set. 2 are text only, 171 s171 calls 3 and 6, where the new hint quotes his whole clause. No move is wrong. `r174.py` on s168, s175 and s177 gives the builder's results.
7. Tests: 46 files, 2 failed, 1353 passed, 13 xfailed. The reds are `test_pins` (known) and `test_a_clause_starts_after_should_say` (finding p4-3). New stale cases: 0. `casestatus` gives 59 stale on 3944adee and on d28e6e05, with the same 11 Liaison cases.

### (b) Findings

- p4-1. **rota/roles/api.py 11875 to 11893, `_clause_tokens`, high. CONFIRMED.** A clause now starts after "say" behind "to" or a modal, whatever comes before. On m35, "Line 4 is fine, and it is wrong to say the local variable matters." lands `revise` with `rewrite` "the local variable matters" on line 4. 5cd73a2d refused the same call. `_holds_clauses` also accepts "the tests pass" in "I never said line 7 should say the tests pass." and in "Nobody wants line 7 to say the tests pass.". Fix: start the clause after "say" only when no negation or fault word stands earlier in its clause.
- p4-2. **rota/roles/api.py `rulings_rule`, the exclude check, high. CONFIRMED.** The check reads the prediction and never his words. On the P10 guess page, `exclude` on `tests/test_defaults.py` with "Lines 2 to 4 are still wrong" lands. `resolve_inbound` then disputes that path. The same holds for `tests/test_options.py` with "Lines 9 and 11 are wrong too". Law 6 is broken: the row is written on his behalf. Fix: refuse an `exclude` whose words do not name the target by `_target_names`.
- p4-3. **tests/rota/test_seam_night173.py 30 to 33, `_home`, low. CONFIRMED.** `test_a_clause_starts_after_should_say` is red in this worktree. `_home(174)` now picks `D:/repos/rota/.rota/clickI_night174.db` (13:59), where `bg_2` is merged. The builder ran it against the copy in `C:/Users/roman/rota_seam/.rota` (13:36). Fix: set the batch's state in the test, as the replays do, or read one fixed copy.
- p4-4. **rota/roles/api.py `rulings_rule`, the exclude check, low. CONFIRMED.** The check uses `_says`, so any word that the line shows passes. On m62, `exclude` on the identifier `clear` lands, because line 5 shows "clear()". Fix: refuse an `exclude` target that has no path shape.
- p4-5. **rota/roles/api.py, the no-target exemption, low. PLAUSIBLE.** A no-target `remove` of kind `row`, `check` or `sentence` passes the removal rule. `grant(ref, "remove")` with no target returns it. `_amend_step` at 1534 and `_assert_words_fault` at 1881 then let an amend drop his sentences. The m62 probe stopped at another rule. Fix: give the sentence example a target, and drop the exemption for `remove`, as the builder recommends.
- p4-6. **rota/roles/api.py 6769, 12001, 13249, 14298 and the refusal lines, low. PLAUSIBLE.** `_backed` and `pointer_fault` read the first line of a ref that the page shows on two lines. A mixed reply such as "Line 8 is wrong, line 47 is right" is then judged on line 8 only. `_ruling_line`, the guess key line and the refusal lines change only the line that a text names. Fix: move `_backed` and `pointer_fault` to `_lines_of`.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/p3rev/`.

- `probe.py`, `probe2.py` and `probe3b.py`: the p3 probes at 3944adee. `probe3b.py` is `probe3.py` without the `page` argument.
- `probe5.py`: prints the paths that each m62 line shows. There are none.
- `test_p4_exclude.py`: runs from the worktree root with pytest. It lands three `exclude` calls on the P10 guess page of `test_guess_route.py`.
- `probe6.py`: three "say" replies on m35 at 3944adee. `probe6_old.py` runs them on `t5cd73a2d/`.
- `probe7.py`: a no-target `remove` of each exempt kind on m62 line 1. Another rule refused all three.
- `new5.json`, `diff5.py` and `moves5.txt`: the replay of the 290 calls and its 27 moves.
- `../r174.py` on s168, s175 and s177.
- `t3944adee/` and `cs_3944adee.txt`: `casestatus` on an archive of 3944adee with the register copy.
- Tests: `pytest` on `test_seam_night173.py`, `test_seam_permission_readers.py` and the 44 files that name the readers.

### (d) Usage

Input about 26k tokens, output about 7k tokens, about 33k in total. These are estimates. The cap was 40k.
