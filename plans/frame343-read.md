# Frame 343, the read: the test-file door and the touch line point the Tester at two different files

Meta workflow, read on 2026-10-27, HEAD 979fb512, by rule C76. One agent on Opus. No code was edited, no model ran, and nothing was committed. Sources: `.rota/clickI_night170.db` opened `?mode=ro`, the night DBs of nights 130 to 170, the 28 `.rota/*.principal.jsonl` files, `plans/night170-read.md`, `plans/frame190-design.md`, `plans/frame328-pass4-provenance.md`, `rota/DECISIONS.md`, `rota/LAWS.md`, `git log` and `git blame`. The count script is `f343_reach.py` in session c66eae69's scratchpad.

**The verdict.** No seat landed a test because two built things disagree about one path. The harness makes every project test file a test row of the batch, and the test-file door refuses a second test in a file that a row holds. The `tests_missing` brief tells the Tester to use the path under `touch`, and the Architect's brief puts existing project test files under `touch`. So the brief sends the Tester to a file the door refuses by construction (reasoned: the three sites below). His "no new test is needed" reached no row because no row form exists for it. No act, no target kind and no predicate clause says that a live criterion owes no test (observed: `RULED_ACTS`, `tests_missing`). The narrow fix is the door's refusal, which names a placeholder where the seat needs a filled path.

**The counts.** On nights 137 to 170, after the touch line landed, 1271 of 5472 `tests.encode` calls, 23%, named a file that an inherited test of the same batch holds, in 175 sessions (observed: the script). On nights 130 to 133, before the line, the share was 305 of 571, 53% (observed). Of the 3 `tests_missing` keys quarantined on nights 130 to 170, 2 stopped at this door: night 155 bg_5 and night 170 b_3 (observed: `tick_attempts`, the encodes of each batch). His words "no new test is needed" occur in 1 reply in all 28 principal logs, night 170's m91 (observed).

## 1. The purpose of each mechanism, and who made it

| Mechanism | Purpose | Made by | Date and commit |
|---|---|---|---|
| The test-file door, "is already X's file; two tests in one file overwrite each other on disk" | The harness writes one file per stored test row. On walk twelve two tests named `tests/test_input_validation.py`, the second overwrote the first, and the harness ran one criterion under two ids | The build session, from a walk | 2026-09-02, e8c68bec, "walk twelve" (observed: `git blame`, the comment at `api.py` 10758) |
| The project's tests join the batch as rows `inh_<sha1>` with no criterion | A merge must not break what the tree already proved. On tipsY the repo's own tip test never ran | The build session | 2026-09-09, 8fb78e66 (observed: `harness.py` 278, the docstring) |
| A project test's id refused outside a challenge | Frame 135: a Tester must not overwrite a project test by its id | The build session | 2026-10-05, c68bd0ef (observed: `git log -L` on `harness.py`) |
| The brief line "A path under `touch` is the file the principal expects your tests in. Use it." | Frame 190, open question 2: on night 136 the tests went to `tests/test_utils/` while his words named other files. "A file the principal names is intent, which flows down by the composition" | The build session, not Roman. The stack status of 2026-10-09 11:07 says "neither goes to Roman", and Roman "typed no word on ... test files or the Tester" | Design 2026-10-09, 0332812b; built 2026-10-09 15:00, 2dace61b (observed: `plans/frame190-design.md` 1119 to 1128; `plans/archive/stack-2026-10-10.md` line 14) |
| The Architect lists existing test files under `touch` | `annotate.md`: "The paths under `the index's test files` are the test files that exist. A test path you write is one of them, or a new test file. List every file the change touches" | The build session | not read: the blame of `annotate.md` 21 to 23 |
| The `tests_missing` tick, per criterion | Each live criterion owes one live test of its own batch. Walk nine: a batch with one test never woke the Tester for the other three criteria | The build session | 2026-09-02, a15c92c7, per criterion; 2026-09-08, 01e48a6f, after the head commit; frame 239, per batch; frame 306, a retired criterion owes no test (observed: `git log -S`, the comments at `predicates.py` 803 to 822) |
| The role behind it | "Tester: what "done" means, written so a machine can check it" | The laws | `rota/LAWS.md` line 42 (observed). A ruling of Roman's that every criterion needs a test: not found |
| The path from his words to a row | `rulings.rule` lands `ruled_refs` rows with a verdict and an act from `drop, keep, rewrite, add, remove` on a target kind from `row, check, sentence, identifier, source_line, path, request`. A relay carries the row to its owner | The seam design, frames 190, 306 and 338 | `principal.py` 977 to 982 (observed). `tests.retire` on a dropped check line: 2026-10-24, f4aee767 (observed: `git log -S`) |

## 2. What the code holds now

- `rota/roles/api.py` 10758 to 10786, the door. The query reads `tests WHERE path = ? AND id != ? AND batch_id = ?`. An inherited row matches it, because `inherit` puts every project test file into the batch (observed). The same-criterion branch at 10764 offers a filled call through `_offer`. The other-test branch at 10781 raises a bare text with the placeholder `tests/test_<what it checks>.py` and no filled call (observed).
- `rota/core/harness.py` 267 to 311. `inherited_id` and `inherit` write one row per file under `tests/`, with `criterion_id` NULL. In night 170's b_3, 41 inherited rows hold every `tests/` file, `tests/test_formatting.py` and `tests/test_utils/test_format_filename.py` among them (observed: `tests`).
- `rota/roles/prompts/tester/tests_missing.md` lines 5 to 7, the touch line. Lines 35 to 38 say "the path is `tests/test_<thing>.py`" (observed).
- `rota/roles/prompts/architect/annotate.md` lines 21 to 23 tell the Architect to list existing test files under `paths` (observed).
- `rota/roles/api.py` 22256, `batches_expect`, shows the grains under "expected to touch" with no mark of which grain is a project test (observed: 22310). s196's wake showed `src/click/utils.py` and four `tests/test_formatting.py::...` grains (observed: s196 turn 1).
- `rota/core/predicates.py` 785 to 842, `tests_missing`. A criterion leaves the debt by four routes only: a live test of its batch, an open or unresolved Tester question with the criterion in refs, a retired ticket, or a retired criterion (observed: the query, 820 to 835).
- `rota/roles/api.py` 6550 to 6596, `criteria_retire`: only the relay of his ruling that drops the criterion's line retires it. `api.py` 6600, `tests_retire`: only his ruling that drops the check line retires a test, and then its criterion owes a test again (observed: the docstrings and `predicates.py` 820 to 822).
- `rota/roles/api.py` 6913 to 6949: a `rewrite` on target kind `check` routes his words to the Tester with `msg.answer_tester` (observed). This is the one route for "the check can simply be that the docstring shows the example". r_m91 used `approve` on c_1, not `rewrite` of its check (observed: night 170's read, section 3, step 9).
- `rota/roles/api.py` 5853, `_docs_ticket_refusal`, frame 322: a criterion on a docstring ticket must name the documentation (observed). A test of `format_filename.__doc__` is a machine check, so the criterion is encodable (reasoned).

**Is there a way for a criterion to need no new test?** Only by retiring it, which needs his ruling that drops its line. A live criterion with no test always owes one (observed: the four routes above). **Is there a way for his words to say so?** No. No act or target kind means "no test", and the predicate reads no ruling (observed: `RULED_ACTS`, the query). Whether the Critic's review needs a test per criterion: not read.

## 3. The reach

| # | Place with the same gap | Count | Source |
|---|---|---|---|
| R1 | Encodes that name a file an inherited row of the same batch holds | 1271 of 5472 on nights 137 to 170, in 175 sessions; 305 of 571 on nights 130 to 133. Night 170: 23, 16 of them in s196 to s200 | observed: the script; sends, not refusals |
| R2 | Walks stopped by a `tests_missing` quarantine at this door | 2 of 3 quarantined keys on nights 130 to 170: night 155 bg_5, 45 of 56 encodes at `tests/test_utils/test_echo.py`; night 170 b_3. Night 136 bg_2 stopped for another cause, 0 of 20 at an inherited file | observed: `tick_attempts`, the encodes by batch |
| R3 | Brief lines that send a seat to a path a door refuses | 1 line in force, `tests_missing.md` 5 to 7. 1 line feeds it, `annotate.md` 21 to 23. Frame 328's pass 4 found the same line showed `src/click/utils.py` on night 167, "the word `touch` names two lists" | observed: the grep of `prompts/` on "touch"; `plans/frame328-pass4-provenance.md` 59 to 63 |
| R4 | Touch grains, at the night's end, that name an inherited file of the batch | 158 grains on nights 137 to 163, 0 on nights 164 to 170. Night 170's four grains were cut by r_m75 to r_m97 before the end, so the end state undercounts | observed: `batch_touch` |
| R5 | His replies that ask for new tests inside an existing project test file, which the door cannot admit | 8 replies on 5 nights: 146 m283, 154 m177, 155 m139, m191 and m195, 166 m52, 167 m105 and m118. 5 more on night 155 name that file in the touch list | observed: the jsonl `words`; the read of each reply is from an excerpt |
| R6 | His words that a live criterion needs no new test | 1 reply in 28 logs: night 170 m91. With m97 and m103, 3 replies set the check form of a criterion with no test | observed: the jsonl `words` |
| R7 | The door's other-test branch with no filled call | 1 branch, `api.py` 10781 to 10786. The same-criterion branch at 10764 has `_offer` | observed |

R1, R2, R3, R4, R5 and R7 are one gap: the place a test goes is said in three places, and only the door knows that a project file is taken (reasoned). R6 is a second gap, with one case.

## 4. The proposal

**At the door, `api.py` 10776 to 10786.** Every encode passes this door in every mode, so it covers R1, R2, R5 and R7 for the brief line, the Architect's grains and his words alike (reasoned). When the clashing row is an inherited test, the door refuses with a filled call through `_offer`. The call keeps the seat's id, criterion and body, and names one new path beside the project file, for example `tests/test_formatting_c_1_format_filename_example.py`. The text says that the file holds the project's own tests, and that the new test goes beside it. Add one sentence to `tests_missing.md` after line 7: "A path under `touch` that already holds the project's tests is not yours. Put your test in a new file beside it." This covers R3. R4 needs no change, because the Architect's prediction is right as a prediction (reasoned).

- Red case: night 170 s196, turn 1, `tests.encode(path='tests/test_formatting.py')` on b_3. The door must return the filled call, and the re-sent call must land.
- Price: 2 cycles, one build and one review (reasoned: a door text and one brief sentence, as frame 341 prices a door text).
- Ruling: no departure found. The design of 2026-10-09 says a file he names is intent, and the sibling file keeps that intent as near as the harness allows (reasoned).
- What it does not cover: R5 asks for tests inside the existing file. Admitting that needs the harness to merge two bodies in one file, and `materialise` and the base run to read it. That is a larger build, not priced here (reasoned).

**R6 gets no build now.** A row "no test needed" would let his words stand in for the Tester's row. Roman ruled on 2026-10-24 at 01:30, "Yes there needs to be a passing review", and the recorded general form says "The approve never stands in for the verdict. A stuck Tester or Developer step still needs a moved row, law 6" (ruled: Roman, `rota/DECISIONS.md` 1539 to 1551, the general form is the session's). A "no test" act would depart from that general form, so it is a question for Roman and not a build (reasoned). With the door fixed, a docstring criterion gets a `__doc__` test, and his "the check can be that the docstring shows the example" then has a test to land on (reasoned). The reach is 1 reply, so the question can wait for a second case (reasoned: rule C76 prices by the reach).

## 5. Doubt

- The counts are sends whose path matches an inherited row of the same batch. Some of them may have landed, for example a challenge encode by the project id. I did not split sends from refusals per night.
- The batch match reads `batch_id='...'` from `args_summary`. A send with no batch in the summary counts as a match by path alone.
- R5 reads each reply from an 80-character excerpt. Some of the 8 may ask for the touch list only.
- The Tester bodies of s196 asserted `format_filename("a/b/c.txt", shorten=True) == "c.txt"`, which tests the code and not the docstring (observed: s196 turn 1). With the door fixed, the test lands and passes on the old code. Whether the Critic then holds the docstring line as evidence, by the ruling of 2026-10-24 at 01:05, is not read.
- Not read: whether the Critic's review needs a test per criterion; the blame of `annotate.md` 21 to 23; frame 306's review finding that a retired test makes its criterion owe a test again, and whether Roman ruled it; why night 155's Tester did not take a new file name either; `_offer`'s form for a path field.
- The night 170 turn texts were read for s196 to s200 only. The other walk 3 sessions come from `plans/night170-read.md`.
