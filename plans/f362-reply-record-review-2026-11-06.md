# Review of 0c5e4a4d, frame 362: every clause add of his reply is kept, or the door refuses by name

Worktree `C:/Users/roman/rota_p362r` at `0c5e4a4d`, parent `a791c31e`. Read only. No model was called.

## Result

Verdict: NOT READY. One high finding and five low findings. Two of the low findings are outside the points.

- High: two adjacent clauses with the same words land once. The door gives no refusal, and `words_from` names his reply. The parent refused those calls. So the commit turns a refusal into a silent loss of his words.
- The other shapes of point 1 hold. A repeated sentence apart, a repeated piece, a quote across two clauses, his case, white space, a newline, curly quotes and a line key `add` keep every add or refuse by name.
- The register: two of 13 cases change at the door, L3R-n174-m53-m58 and L3R-n175-m75-m76. No case of n173 changes, so the budget fault of R3e does not return on n173-m34-m35.
- 34 test files that name `clause` run green: 2218 passed, 39 skipped, 1 xfailed.

## (a) The verdict on each numbered point

1. FAILS on one shape. Adjacent clauses with the same words lose one copy with no refusal (finding 1). A part quote lands the part (finding 2). The other shapes hold.
2. HOLDS. The principal's page does not read `page_clauses`. The Liaison's menu gets one more clause per repeated piece. No test is red.
3. HOLDS, with a cost. Ten recorded call shapes change on n174 and n175. The named way out takes two refusals on n174 (finding 3). A seat that repeats ends in four turns with no ruling.
4. HOLDS for the record today. 84 of 189 recorded clause adds quote a strict part of the clause. None turns his meaning. A whole clause would put his drop words into an add row.
5. HOLDS, with one gap. No code branches on `words_from`. The stamp is a text match in the whole reply, not at the place of the words (finding 4).
6. ANSWERED. All three old pins came from the session's reasoning, not from words of Roman.
7. ANSWERED. L3R-n174-m53-m58 and L3R-n175-m75-m76 change. The table is under point 7 below.

### Point 2, the cut

- Readers by the map tool: `rota/core/runner.py:2517` (`resolve_inbound`, the `landing.clauses` of the Liaison's wake), `rota/roles/api.py:15865` and `15888` (`menu_ruling`), and `16435` and `16469` (`rulings_rule`, the count in `menu_form_text`).
- The principal's page: no reader renders `page_clauses` to him, so his page does not change.
- The Liaison's menu: a repeated sentence is now its own clause, and each later clause number moves up by one. Probe R2: "Add the tax. Drop line 3. Add the tax." now shows c3 with `none`, `held`, `add <quote>`. A call that does not key c3 gets one refusal of 205 characters, and the repeat lands. The parent showed no c3.
- A repeated sentence that names a line becomes a clause with `none` only (probe R1), so it costs no key.
- The cut of the 37 case replies in `tests/rota/cases/*.yaml` is the same on both trees (`cuts.py`). No recorded prompt moves for the cut.
- Tests: the 34 files under `tests/rota` that name `clause` or `page_clauses` give 2218 passed, 39 skipped, 1 xfailed, 0 failed.

### Point 3, the refusals of B and C

- R3e: commit `4fa8f775` (frame 345, 2026-10-30). Its reason: in R3d, n173-m34-m35 ran out of output budget after two conflict refusals. The status line of 01:16 (rota-86) says "Judged: a refusal that is right by design and costs the seat its budget is a worse landing". That is the session's judgement. Commit `f144bab1` then removed the note of a displaced add.
- Replay: every distinct `rulings` map of the gemma recordings of the L3R cases of n173, n174 and n175 went through `rulings.rule` on each tree, with each case's fixture (`reg_replay.py`). 169 maps, 727 recorded calls.
- Refused at the first call: 119 maps at the commit. Refused at the end of four tries: 106 maps at the parent, 108 at the commit.
- Changed: 10 maps, all on two cases. n173 has no change.
- New refusal lengths: C with line 11 `drop`, 386 characters. C with line 11 `other <his first sentence>`, 572 characters. D on n175-m75-m76, 257 characters. The second C after the named way out, 529 characters. B fires on no recorded call.
- The way out on n174-m53-m58 (`wayout.py`): "11": "other <quote of c2>" with "c2": "none" gets a second C refusal for c3. "11": "other <quote to the end>" with c2 and c3 `none` lands a contest on line 11. A line 11 `approve` with both adds lands an add. `rulings.rule(ask=...)` lands the ask that the case expects.
- A seat that repeats the same call: `rota/core/runner.py:6250-6276` counts the same refusal per turn. Turn 3 gets the NOTE "will not be accepted again". Turn 4 ends the session. No `rulings` row lands. `rota/core/db.py:2085-2090` writes `unresolved_note` on his reply, and the Liaison wakes again with the refusal text. After the second miss, the page goes back to him with the line of `returned_line` (`rota/roles/principal.py:2720`).

### Point 4, the part quotes

Register, 146 gemma recordings, 189 clause adds (`parts.py`): 89 whole, 84 strict part, 9 run past the clause, 2 lie in another clause, 5 lie in no clause. Dry runs 3 to 6c, 47 clause adds: all whole.

| Shape of the part | Count | Row now | Row with the whole clause |
|---|---|---|---|
| "the docstring gains an example ... c.txt." of "Please drop all twelve lines and replace them with one line saying the docstring gains ..." | 31 | the request words only | adds his "Please drop all twelve lines and replace them" to an add row |
| "only the docstring in the termui file changes ..." of "The new page should also say that only ..." | 31 | the request words only | adds his "The new page should also say that" |
| "add one example ... touched." of "Replace line 6 with my real request: add one example ..." | 12 | the request words only | adds his "Replace line 6 with my real request:" |
| "my request for the one docstring example" of "This page also leaves out my request ..." | 6 | the noun phrase only | the whole clause, which says what the page leaves out |
| "Please keep line 5 to the terminal module ..." of a clause of two sentences | 3 | the second sentence | adds his fault of line 5 to an add row |
| "it should print the total ..." of "no, it should print the total ..." | 1 | drops "no," | keeps "no," |

No recorded part drops a negation or a condition of the add. So no recorded row turns his meaning today. The built case "add add tests." on "Do not add tests." does turn it (probe Q6).

### Point 5, his spelling for other quotes and line key quotes

- Readers of `ruled_refs.words_from`: the writer `_ruled_rows` (`rota/roles/api.py:13671-13676`), the builder `ruling_rows` (`rota/roles/principal.py:1275`), and the copy to the `landed` row (`rota/roles/principal.py:4271`). No reader branches on the value.
- Tests that read `words_from`: 8 files. All run green at the commit. No test pins a seat quote whose case or white space differs from his text.
- Meaning: the stamp says that his message holds the row's words as whole clauses. The commit now takes the words from his reply at a place. The stamp still tests the text anywhere in the reply (finding 4).

### Point 6, the three old pins

| Old test | Behaviour | Source | Frame and commit |
|---|---|---|---|
| `test_a_line_key_on_the_add_line_wins_with_no_note` | a line key wins over a clause add with no refusal and no note | the session's judgement of pass R3e, from the budget loss of n173-m34-m35 | frame 345, `4fa8f775` (pass R3e). The name and the "no note" came with `f144bab1` (pass R3f, re-check p12b). |
| `test_a_repeated_quote_stands_once` | one quote on two clauses lands once | the review of `c91c9a5b`, finding 2 | frame 362, `901659b0` |
| `test_turned_quotes_join_in_the_order_of_his_reply` | a quote of another clause joins at its own clause's place | the review of `c91c9a5b`, then the review of `ede08a30` | frame 362, `901659b0`. The pass 3 docstring came with `c5851e5b`. |

No old pin quotes Roman. The rule that the record holds his words verbatim is the composition's.

### Point 7, the register

The 146 recordings with a clause add map to 13 cases: 137 by his reply, and 9 to L3R-n174-m47-m48. 37 distinct maps went through the door on both trees (`reg_replay2.py`, `reg_replay3.py`).

| Case | Maps (calls) | Old result | New result |
|---|---|---|---|
| L3R-n174-m53-m58 | 2 (3) | lands contests on lines 1 to 11, against the expected ask | C refusal of 572 characters on every call |
| L3R-n174-m53-m58 | 7 (19) | refused: "line 12: 'drop' is not an option of line 12", 156 characters | C refusal first, 386 or 572 characters, on every call |
| L3R-n175-m75-m76 | 1 (1) | lands line 1 approve add with his c2 | D refusal once, 257 characters. The repeat lands line 1 approve add with c2 and c3 joined. |

No change on L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about, L1-LI-a-named-line-is-contested-and-the-rest-approved, L1-LI-a-separate-request-is-later, L1-LI-removing-lines-is-right-is-a-drop, L3R-n170-m58-m59, L3R-n172-m76-m77, L3R-n173-m34-m35, L3R-n174-m47-m48, L3R-n174-m53-m55, L3R-n175-m75-m77 and L3R-n175-m136-m138.

## (b) Findings

1. `rota/roles/api.py:16108-16111`. High. CONFIRMED. The offset loop starts each search at the start of the previous clause. A clause with the same words as the clause before it gets the earlier offset. Probe Q1: "Drop line 3. Add the tax. Add the tax." with c2 and c3 `add` lands "Add the tax." once, with `words_from` m10 and no refusal. Probe Q4: "Use the tax. Use the tax. Use the fee." lands "Use the tax. Use the fee.". The parent refused both calls. Fix: take each clause offset from `page_clauses`, or start each search at the end of the previous clause.
2. `rota/roles/api.py:15704-15720` and `16182-16185`. Low. CONFIRMED. A quote that overlaps its own clause by one character lands as the row, whole words or not. Probe Q6: "add add tests." on "Do not add tests." lands "add tests." as an add. Probe Q5: "add he page leaves out the t" lands "he page leaves out the t". No recorded row turns his meaning (point 4). Fix: refuse once a quote that cuts a word or leaves out a negation of its clause.
3. `rota/roles/api.py:16027-16032` with `15723-15731`. Low. CONFIRMED. The C refusal names one clause add and fires on every call. On n174-m53-m58 with c2 and c3 `add`, the named way out gets a second refusal of 529 characters for c3. Each refusal costs a turn of the seat that ran out of budget in R3d. Fix: name every clause add of the line, and one way out, in one refusal.
4. `rota/roles/api.py:13672-13676`. Low. CONFIRMED. `words_from` tests the text anywhere in his reply, not at the place of the words. Probe P2b: "add tests." taken from c1 "Do not add tests." gets `words_from` m15, because c4 holds the same text as a whole clause. Probe Q6 gives the same text no stamp. Fix: stamp from the place `at` that the door now knows.
5. Outside the points. `rota/roles/api.py:15753-15757`. Low. CONFIRMED. When `line_words` binds a line to his whole reply, the whole reply can be the one clause. Probe P1d: "Drop line 3. The page leaves out the tax. Drop line 3." gives one clause, so his add has no key. The parent gives the same. Fix: drop the group of the whole reply whenever the cut gives more than one piece.
6. Outside the points. `tests/rota/test_f362_clause_adds.py:401-420`. Low. CONFIRMED by reading. The rule test returns at the first refusal. So it never checks the row after a D refusal that fires once, and it holds no adjacent repeat. Fix: call again after a refusal that fires once, check the row, and add the replies of probes Q1 and Q4.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rr362/`. The parent tree is `parent/`, from `git archive a791c31e`. Each database opened with `immutable=1`.

- `test_p1.py`: 20 built replies through `rulings.rule`, up to three calls each, at the commit and at the parent (copied as `parent/tests/rota/test_zz_p1.py`).
- `test_p1b.py`: adjacent repeats, a word fragment, and a part that turns his meaning, on both trees.
- `test_p1c.py`: a repeated line sentence and an unkeyed repeat, on both trees.
- `reg_replay.py`, `reg_old.json`, `reg_new.json`: every `rulings` map of the n173 to n175 L3R recordings through the door on both trees. `cmp.py` compares them.
- `reg_replay2.py`, `reg_replay3.py`, `reg2_*.json`, `reg3_*.json`: the 146 clause add recordings by case, on both trees.
- `wayout.py`: the C refusal's way out and the ask on L3R-n174-m53-m58.
- `parts.py`: the kind of each recorded clause add quote against its clause, in the register and in the implementer's `reach_new.json`.
- `cuts.py`, `cuts_old.json`, `cuts_new.json`: the cut of the 37 case replies on both trees.
- pytest at the commit, with `-p no:cacheprovider`: the 34 test files that name `clause`, and the 4 other files that read `words_from`.

## (d) Usage

The harness gives the agent no count. Estimate: input about 140k tokens, output about 25k tokens, total about 165k tokens. The cap was about 80k of context. The register replay took the excess.

## Second look, 58c6bd76

Worktree `C:/Users/roman/rota_p362r` at `58c6bd76`. The diff `0c5e4a4d..58c6bd76` only. Read only. No model was called.

### Result

Verdict: NOT READY. Findings 1, 3, 4 and 6 of the first look are fixed. Finding 2 is fixed for letters and digits only. Two new low findings are below.

- The three test files `test_f362_clause_adds.py`, `test_r1_menu_form.py` and `test_ruled_refs.py` give 113 passed.
- The cut of the 37 case replies is the same as at the parent, so the revert of finding 5 is whole.

### (a) The verdict on each point

1. Finding 1: FIXED. Probe Q1 lands "Add the tax. Add the tax.", and probe Q4 lands "Use the tax. Use the tax. Use the fee.". `menu_ruling` takes `clause_at` from the cut at `rota/roles/api.py:15882`, and it holds no second search for a clause offset. The one `find` left, at `16261`, places the words of a line key, not a clause. Finding 2: FIXED for letters and digits only. Probe Q5 lands "The page leaves out the tax". Probe Q6 still lands "add tests.", as decided. Finding 3: FIXED. One refusal names c2 and c3. Finding 4: FIXED. Probe P2b now gives `words_from` null. Finding 6: FIXED. The rule test repeats the call after a refusal that fires once, and it holds both adjacent repeats (`tests/rota/test_f362_clause_adds.py:404-405`).
2. The word extension: FAILS on six joiners. No row holds a character that is not his. Rows lose his characters at a hyphen, an apostrophe, an underscore, a dot, a comma and an opening curly quote (new finding A).
3. The new refusal: HOLDS. It is 187 characters with `drop` and 188 with `other`, and it names c2, c3. The way out lands in one call, but its row rules against his words (new finding B).
4. Finding 5: the revert is WHOLE. The diff of `page_clauses` holds only the `at` of each piece and the `offsets` flag. The three worse cuts are PLAUSIBLE. A split question loses the one `ask` clause of pass R3d, and a drop piece with no line loses its drop lines. I did not rebuild the reverted code.
5. New defects: findings A and B.

### Point 2, the word extension (`test_p2w.py`)

| Reply part | Quote | Row | His characters lost | `words_from` |
|---|---|---|---|---|
| "follow-up rule." | "up rule." | "up rule." | "follow-" | null |
| "Use the follow-up rule." | "Use the follow" | "Use the follow" | "-up" | null |
| "Don't round the tax." | "t round the tax." | "t round the tax." | "Don'" | null |
| the same, curly apostrophe | "t round the tax." | "t round the tax." | "Don" and the curly apostrophe | null |
| "in string.py now." | "py now." | "py now." | "string." | m14, his reply |
| the same | "The fold is in string." | "The fold is in string." | "py now." | m15, his reply |
| the same | "ring.p" | "string.py" | none | null |
| "is _foldline here." | "foldline here." | "foldline here." | "_" | null |
| "Call parse_args first." | "args first." | "args first." | "parse_" | null |
| "Round to 3.14 always." | "14 always." | "14 always." | "3." | m19, his reply |
| "at 1,000 dollars." | "000 dollars." | "000 dollars." | "1," | m20, his reply |
| a curly double quote around "Tax" | "Tax" and the closing quote | "Tax" and the closing quote | the opening quote | null |
| the first word of his reply | "he page leaves out the tax." | "The page leaves out the tax." | none | his reply |
| the last word of his reply | "The page leaves out the ta" | "The page leaves out the tax" | none | his reply |
| "the tax." | "x." | "tax." | none | null |

### Point 3, the register at 58c6bd76

`reg_replay2.py` and `reg_replay3.py` ran again on the 146 recordings. The changed maps are the same 10 as at `0c5e4a4d`, and no other map changed.

- L3R-n174-m53-m58, 9 maps (22 calls): every call is refused, with 187 characters for line 11 `drop` and 188 for line 11 `other`. The parent landed contests for 2 of the maps (3 calls) and refused the other 7 at line 12.
- L3R-n175-m75-m76, 1 map (1 call): the D refusal fires once (257 characters). The repeat lands line 1 approve add, with c2 and c3 joined.
- The way out on n174-m53-m58 (`wayout.py`): lines 1 to 10 `drop`, line 11 `approve`, c2 and c3 `add`, line 12 `approve`. It lands in one call. Line 11 holds verdict approve, act add, the words "the docstring gains an example ... c.txt. only the docstring in the termui file changes ...", and `words_from` null.
- The ask lands in one call. The case expects the ask.

### (b) New findings

A. `rota/roles/api.py:16226-16236`. Low. CONFIRMED. The extension stops at any character that is not a letter or a digit. So a quote cut at a hyphen, an apostrophe, an underscore, a dot or a comma lands part of his word. At a dot or a comma, `_holds_clauses` reads the part as whole clauses, so "py now." and "14 always." get his reply as `words_from`. Paths such as `string.py` are in the recorded m27. Fix: extend to the white space on each side, so each word lands whole.

B. `rota/roles/api.py:16083-16092`. Low. CONFIRMED. The way out names only the approve of line 11, or the ask. On n174-m53-m58 his c1 drops lines 1 to 12. The named approve lands approve on line 11, against his words, and the case expects the ask. Fix: name the ask first, and give the approve only when no clause of his faults the add line.

### (c) Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rr362/`.

- `test_p1.py`, `test_p1b.py`, `test_p1c.py`: run again at `58c6bd76`.
- `test_p2w.py`: 15 quotes for the word extension.
- `reg2_p2.json`, `reg3_p2.json`: the register replay at `58c6bd76`, compared with `reg2_old.json` and `reg2_new.json`.
- `wayout.py`: the new way out and the ask on n174-m53-m58.
- `cuts_p2.json`: the cut of the 37 case replies at `58c6bd76`.

### (d) Usage

Estimate for the second look: input about 35k tokens, output about 8k tokens, total about 43k tokens.

## Third look, dc15b676

Worktree `C:/Users/roman/rota_p362r` at `dc15b676`. The diff `58c6bd76..dc15b676` only. Read only. No model was called.

### Result

Verdict: READY, with one low finding. Finding A and finding B of the second look are fixed. The approve branch of `_displaced_text` cannot be reached through the door (finding C).

- The three test files `test_f362_clause_adds.py`, `test_r1_menu_form.py` and `test_ruled_refs.py` give 128 passed.

### (a) The verdict on each point

1. Finding A: FIXED. All 15 quotes of `test_p2w.py`, run again as `test_p3w.py`, land his whole words. No row holds a character that is not his. "string.py", "Don't", the curly apostrophe, "_foldline", "parse_args", "3.14", "1,000", "follow-up" and the opening curly quote all land whole. A quote that ends at a newline stops at the newline: "Use the tax". A quote inside a tab keeps his tab: "Use the", a tab, then "tax now". The one character that a row can lose is a sentence mark after his last word when the quote stops inside that word. "Read string" gives "Read string.py" without his final dot. The diff says that it does this by design (`rota/roles/api.py:16246-16248`).
2. Finding B: FIXED. On n174-m53-m58, line 11 `drop` now gets 172 characters, and line 11 `other` gets 169 characters. Both texts name only the ask. `rulings.rule(ask=...)` is accepted in one call, and the case expects an ask. The approve branch cannot be reached through the door (finding C).
3. New defects: none in the door's behaviour. The `his_place` region now spans the words as well as the clauses (`16111-16118`), and this is correct for a word that the extension takes past a clause edge.

### (b) New finding

C. `rota/roles/api.py:15742-15757`. Low. CONFIRMED by reading the tables. `_displaced_text` offers the approve only when the line key's row is not a contest or a revise. In `_OPTION_ROWS`, every option that does not ride with an add is a contest or a revise. Only a `step` line maps `drop` to approve, and `line_menu` gives a step line no `add <quote>` (`15427` and `15572`). So `_add_lines` never names a step line, and the branch has no path through the door. Only `tests/rota/test_f362_clause_adds.py:358` calls it, with the kind `step`. Fix: delete the approve branch and its direct test, and keep the text that names the ask.

### (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rr362/test_p3w.py`: the 15 quotes of `test_p2w.py`, and 6 more for a newline, a tab, a final dot, an abbreviation, a parenthesis and a question mark.
- `wayout.py` run again: the refusals of the fault key, and the ask, on n174-m53-m58.
- A print of `_RIDES_WITH_ADD`, `_OPTION_ROWS` and `_STEP_ROWS` at `dc15b676`.

### (d) Usage

Estimate for the third look: input about 15k tokens, output about 4k tokens, total about 19k tokens.
