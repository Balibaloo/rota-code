# Frame 308, review 5: passes 3b and 3c at 46471ca4

Reviewer on Opus, read-only, in `C:/Users/roman/rota_r308` at 46471ca4. No gate, no re-record. Night databases opened with `?mode=ro`.

## Verdict

Accept 46471ca4 for the colon split, the negation guard and the drop admission, with two high findings to fix before the branch. Review 4's findings 1 to 3 are closed. Finding 4 stays open, because no count ran on the record path of night 160. The two new readers are too wide. A keep phrase on a line cancels an explicit request for new words on that line. `_DROP_LINE` reads "Line 3 should go back to how you had it" as a drop, so an answer can omit a criterion he asked to rewrite. Night 140 holds that shape. None of the twelve reds is this frame's.

## (a) The points

1. Review 4: F1 closed, F2 closed, F3 closed, F4 open.
2. A contested criterion with no drop: refused. The half shape: refused, with a respecify of cr_2 asked. A false drop is admitted (finding 2).
3. Keep phrases: three real sentences in nights 140 to 159 match a keep and ask for other things in the same sentence. The reader is right on all three. Synthetic shapes show the keep wins over a words request (finding 1).
4. Twelve reds: six are red at 695e8be7 too, and six are the "again" scene tests that a970d886 fixes. None is this frame's.

## Point 1, review 4's findings

- F1, the colon split: closed. `_ruling_words_on` now splits on `_RULING_SENTENCE`, at sentence ends only. `test_a_line_label_before_a_colon_keeps_its_body_on_its_line` passes. The file runs 19 passed.
- F2, the cr_3 rewrite in the tests: closed. `_land_cr3` and `CR3_NEW` are gone. The tests assert the drop text and name frame 192 at lines 132, 139, 264 and 324.
- F3, the negation guard: closed. `_faults_on` skips a match with `_NEGATION_WORDS` in its own clause. `test_a_negated_removal_asks_no_new_words_of_its_lines` passes. Probe D: "Do not drop line 5" reads no drop, and the answer without cr_3 is refused.
- F4, the count: open. Passes 3b and 3c counted nights 158 and 159 again. Those nights hold no `order:` row. Night 160 still runs, so its `clickI.db` has no end state yet.

## Point 2, the dropped criterion

Probe `r5/test_r5_drop.py` changes the words of m98 on the frame fixture and calls `msg.answer_tester`.

- A. "Line 4 should say ..." with no word on cr_3, refs `[cr_3]`: refused, "Your answer leaves out cr_2".
- A2. The same words, refs `[cr_2]`: refused, "leaves out cr_3". A criterion the ruling contests and does not drop cannot be omitted.
- B. "Line 4 should say .... Drop line 5." with refs `[cr_2]` and no respecify: refused, "No respecify of cr_2 has landed ... Respecify cr_2 first". The refusal says nothing of cr_3, because cr_3 is not in the answer. That is right.
- C. The m98 words, refs `[cr_2]`: admitted, as pass 3c intends.
- H. The m98 words, refs `[]`: refused, "leaves out cr_2".
- E. "Remove line 5's last clause about the prompt": admitted. A partial edit reads as a drop of the whole line.
- F. "Line 5 should go further and name the default": admitted. The pattern part "should go" with a word end matches "go further".
- G. "Drop the word hidden from line 5": refused. The pattern needs the line right after the verb.

The door is sound where the drop reader is right. The leak is the drop reader itself (finding 2).

## Point 3, the keep phrases

Probe `r5/p3_keep.py` splits every `rulings.words` of `clickI_night140.db` to `clickI_night159.db` at sentence ends. It prints each sentence with "keep", "as is", "as it is", "unchanged", "stays", "as it stands" or "as written", with the `_KEEP_WORDS` and `_WORDS_FAULT` matches.

Sentences where a keep phrase matches and the same sentence asks for something else:

- n157 r_4a62d8a771, line 3: "keep the requirement, but change its check ...". The reader reads a keep and a check fault. The criterion stands. Right: he asked for a new check, not new words.
- n157 r_4a62d8a771, line 5: "keep it as written, but fix the code ...". The criterion stands. Right: he faulted the code.
- n154 r_bfed1d4d86: "Keep lines 3 and 4 as they are, and delete line 5 ...". The keep bears on lines 3 and 4 only. Line 5 reads as a drop. Right.

Sentences that ask for other words beside a keep that `_KEEP_WORDS` does not match. The keep has no effect on these:

- n154 r_bfed1d4d86: "For line 1, keep the wording but point it only at the terminal UI test file". "the wording" is not in the list.
- n156 r_beb6f61b09: "On line 1, keep my request as written but change the code it points at". "my request" is not in the list.
- n155 r_653db6b97b and r_7a4508f047: "Keep change 1 as I wrote it ..." with a change to the file list.
- n140 r_m103: "Please keep line 3 as you wrote it last time and don't add the module to it". This asks for the old words back. No keep, and no words fault (outside note 2).
- n142 r_6713c97786 and r_356ec00c04: "Lines 10 and 11 should keep only their first sentence". This asks for new words. No keep, and no words fault (outside note 2).

No real sentence of these nights has a matched keep that cancels a words request. Probe `r5/test_r5_keep.py` shows that the shape is open. Each shape below reads keep True, fault False, and `ruling_asks_no_new_words` True for cr_2 on line 4:

- "Line 4: keep the requirement, but it should say that confirm returns the default."
- "Keep line 4 as it is, but change it to say that confirm returns the default."
- "Line 4 should say that confirm returns the default, and keep it as written otherwise."
- "Line 4 should say that confirm returns the default. Keep it as it is for the rest." A keep sentence with no line ref bears on every line.

## Point 4, the twelve reds

The twelve are in `f308p3c_suite.txt`. Probe: the same files at 46471ca4 in the worktree, and at 695e8be7 from `git archive` into `r5/h695`, both with `-n 4`. Both trees give 7 failed and 188 passed, with the same seven.

Red at 695e8be7 too:

- `test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`
- `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`
- `test_onboarding.py::test_the_same_constraint_written_twice_is_one_gate`
- `test_fixtures.py::test_no_case_leaves_a_reference_unwrapped`
- `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`
- `test_pins.py::test_with_prompt_keeps_every_pin`

The "again" scene tests, fixed by a970d886 (`rota/testkit/scenes.py` masks the run journal's output):

- `test_scene_two_batches_again.py`: red at file scope at both commits.
- `test_scene_review_again.py`, `test_scene_large_module_again.py`, `test_scene_challenged_again.py`, `test_scene_merged_then_next_again.py`, `test_scene_park_again.py`: red in the full run only.
- With a970d886's `scenes.py` laid over an archive of 46471ca4 (`r5/c464`), all six "again" files pass: 64 passed and 1 failed, the two_batches right-call red.

The brief and the pass report say five "again" tests and seven head reds. The list holds six "again" tests and six head reds. The pass report counts `test_scene_two_batches_again` with the head reds. No red is this frame's.

## (b) Findings

1. `rota/roles/api.py` `_KEEP_WORDS` (about line 5431) and `_words_fault_on` (about line 5797). High. CONFIRMED. A keep match on a line returns no words fault, whatever else the words ask of that line. Probe `test_r5_keep.py`: four shapes that ask new words of line 4 read `ruling_asks_no_new_words` True. A keep sentence with no line ref bears on every line, so "Keep it as it is for the rest." silences "Line 4 should say ...". The answer door then admits cr_2 as it stands. Fix: let a keep cancel only a check or code fault, never a `_WORDS_FAULT` match on the same line, and ignore a keep with no line ref in a ruling that names lines.
2. `rota/roles/api.py` `_DROP_LINE` (about line 5416). High. CONFIRMED. The pattern matches a revert or a partial edit. Night 140's r_4dfcbd586b "Line 3 should go back to how you had it" reads as a drop of line 3 in `p3_keep.py`, and probe `test_r5_keep.py` gives `_line_dropped_on` 4 for the same shape on line 4. Probe E "Remove line 5's last clause" and probe F "Line 5 should go further" admit an answer without cr_3, and cr_3 keeps the text he faulted. Fix: end the drop match at a clause end (".", ",", "because", "and" or the end of the words), and refuse a possessive after the line number.
3. `rota/core/sandbox.py:1611-1627`. Low. CONFIRMED. The refusal says "Do not rewrite cr_3", but no door enforces it. Probe `test_r5_resp.py`: a respecify of the dropped cr_3 lands, and the answer `[cr_2, cr_3]` is admitted. That is the frame 306 shape, a merged change that holds a line his words refused. Fix: record the case for frame 192, or refuse `criteria.respecify` on a criterion whose line the last ruling drops.
4. Review 4, F4. Low. CONFIRMED. Passes 3b and 3c count the fallback only, on nights 158 and 159. Fix: count the record path on night 160's `clickI.db` after the night ends.
5. The pass report's count of the reds. Low. CONFIRMED. It names seven head reds and five "again" reds, but the list holds six of each. Fix: correct the count in the pass report and in the frame's status line.

Outside the points:

- The respecify refusal for a keep still says "the principal faulted the check", as pass 3c notes. Low.
- `_WORDS_FAULT` misses "should keep only its first sentence" (n142 r_356ec00c04 and r_6713c97786) and "keep line 3 as you wrote it last time" (n140 r_m103). Both ask new words. The same holds at 695e8be7, so this is not a change of this frame.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad/r5/`. The pytest probes import the fixture of `tests/rota/test_frame308_ruling_answer.py` and run from the worktree with `--rootdir`.

- `test_r5_drop.py`: nine word shapes on m98 and an answer per shape (cases A to H).
- `test_r5_keep.py`: four keep shapes and one "should go back" shape. It prints `_keeps_words_on`, `_words_fault_on`, `_line_dropped_on` and `ruling_asks_no_new_words` for cr_2.
- `test_r5_resp.py`: a respecify of the dropped cr_3, then the answer `[cr_2, cr_3]`.
- `p3_keep.py`: the keep sweep and the drop sweep over `clickI_night140.db` to `clickI_night159.db`, read-only.
- `reds.txt`, `h695/` (archive of 695e8be7) and `c464/` (archive of 46471ca4 with a970d886's `scenes.py`): the red files run with `-n 4` in each tree.

## (d) Usage

About 50k tokens in total, measured from the session budget. This is over the cap of 20k. Most of it is the night sweep output and the three test runs. The split into input and output tokens is not available. No sub-agent ran.
