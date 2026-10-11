# Frame 200 review of pass 2c on 8d090e2e, Opus, 2026-10-11

Read-only review. Worktree `C:/Users/roman/rota_rv200c` at 8d090e2e with pass 2c as uncommitted edits. Parent worktree `C:/Users/roman/rota_rv200c_base` at 8d090e2e. Rota workflow. All observations 2026-10-11.

## (a) Verdicts

1. The receipt rule holds for findings 1, 2 and 8. `p1.py` cases B, C and D change as the fixes intend, and case A is unchanged (observed: `p1.py` on both trees). The night replay marks 0 rows on night 138 and 0 on night 139, on the parent and on the patch (observed: `r1.py`). The proposal edge has a designed reply that nothing discharges (finding 1).
2. `_received` has one caller, `session_commit` at `rota/core/db.py:889`, and the patch updates it (observed: map tool). A decision that cites a message id and a ref of the trigger is no receipt for the trigger (observed: `p1.py` case D). Night 138's Vision Keeper decisions still count as receipts (observed: `r1.py`, 0 rows on the patch).
3. The exemption fires on the designed path through the trigger answer's refs (observed: `r6.py`, `carries: True`). It also fires when the decision cites a test of the challenge and not the answer (observed: the edited test passes). A `tests_failing` wake with no trigger passes the cap only with a decision that cites a test of the challenge (reasoned: the `carried` set is empty). The cap does not stop the designed route in the night shapes, because night 139's `d_6710df81d1` cites the test (observed: tool_calls of s259).
4. `_escalated_test_route` fires on an `escalate` trigger with a test ref and no finding ref, when `constraint_id` names a row of another table (observed: `r4.py` for a criterion and a test, no route for an unknown id). The escalate mode offers `decisions.author` (observed: `mode_tools`). The offer with `text=INVENT` raises `DrySkipped` and is never judged. With a filled text, `decisions.author(refs=[tst1])` and the answer after it are admitted (observed: `r4.py`).
5. `p5.py` line 1 now ends in the offer `msg.answer_developer(refs=['k_new'])`. Every offered answer is admitted for a constraint, a finding, a decision and two rows (observed: `r5.py`). For two rows the refusal says "This session wrote k_new, d_new" and offers both (observed). A `model.amend` with a binding also offers the binding's composite id (finding 3).
6. `rota/testkit/fixtures.py:603-620` supports `text_includes_any` and `text_excludes` on a writes expectation (observed: read). `seed` lands the `decisions` row of the Developer case (observed: `r6.py`). The fixture's answer passes `_rowless_answer_refusal`, the answer-mode door and the cap (observed: `r6.py`, three `None`).
7. Two new or edited tests pass on the parent: `test_a_decision_the_trigger_answer_carries_passes_the_cap` and `test_a_challenge_that_carries_a_decision_row_passes_the_cap` (observed). Both guard against a cap that is too narrow, so this is correct. No expected text differs from the built text, because all 107 tests pass on exact equality (observed).
8. Prompt moves, predicted below. The re-record set is 2 sure cases and up to 2 more.

Point 8 prediction (observed: `case_runs.transcript` in the cassette copy `cass.db`, model `qwen3:8b`):

- The `findings.find` route text: `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row`, 24 transcripts hold the refusal.
- The rowless text moves only when the session wrote a row before the refusal. Transcripts hold the old text in `L1-AR-a-dead-answer-is-a-question-about-the-model` (15), `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row` (9) and `L1-AR-route-an-escalation` (4). Whether a write came first is PLAUSIBLE only, because the brief text also names the ops.
- The "no words" text: 0 transcripts hold the challenge refusal. The text is byte-identical when `body_text` is empty (reasoned: `said` is the old sentence).
- The cap: 0 transcripts hold a cap refusal.
- The fixture change: `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone` re-records, because its inbound refs changed.
- The Architect expectation change moves no prompt. It re-grades the recorded runs.

## (b) Findings

1. **`rota/core/db.py:660` and `:700-743`, with `rota/roles/prompts/vision_keeper/propose.md:9`. High. CONFIRMED.** The proposal brief says "assert it as an item ... Both are answers". `problem.assert` writes a new item and refs under that item, and neither is a ref of the proposal. So the stamp marks the proposal unresolved, and `unresolved()` wakes `('liaison', ('m9',))`. Probe `r1b.py` shows this on the patch and on the parent. The class is finding 1 of the last review, on another edge. Fix: count an `items` write by the Vision Keeper as the receipt for `architect -> vision_keeper propose`.
2. **`rota/core/db.py:722-723`. Low. CONFIRMED.** The `receipt_of` check runs before the `_answers_by_message` check. So an Architect that amends a constraint of the escalation and sends no answer leaves the escalation `answered`. Probe `r2.py` shows `('answered', None)`. This is night 127's m72 shape through `model.amend`, which the escalate brief designs. Fix: for `developer -> architect escalate`, count only a message caused by the trigger as the receipt.
3. **`rota/core/sandbox.py:997-1004`. Low. CONFIRMED.** `mine` keeps every non-refs write, and `model.amend` stages `constraint_bindings` rows with ids like `k_new:src/x.py`. The refusal then offers `msg.answer_developer(refs=['k_new', 'k_new:src/x.py'])`, and the doors admit the id that names no row. Probe `r5.py`, shape one. Fix: keep in `mine` only the rows of `constraints`, `findings` and `decisions`.

Outside the points: none beyond findings 1 and 2, which sit outside the patch's hunks.

## (c) Probes

All new probes are in `C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\c81dd240-3837-494d-a148-76820abc8093\scratchpad\rv200p2c\`. Each ran with `PYTHONPATH` set to the tree it names.

- `p1.py` and `p5.py` of the last review, on both trees.
- `r1.py`: replays the stamp over read-only `n138p5.db` and `n139p5.db`. It takes writes from `receipts` and decision refs from `tool_calls`, and calls each tree's `_received`.
- `r1b.py`: a proposal answered by an item, through `session_commit` and `unresolved()`.
- `r2.py`: an escalation on a constraint, an amend of it, and no answer.
- `r4.py`: `findings.find` on a criterion, a test and an unknown id, then `dry_run` of the offer with a filled text.
- `r5.py`: the rowless refusal with five written shapes, and `dry_run` of each offer.
- `r6.py`: the Developer case's fixture built with `fixtures.seed`, `_with_repo` and `seed_inbound`, then the three doors.
- Inline queries on the graph's edges and on `cass.db`.
- pytest: `test_row_route.py` and `test_predicates.py` on the patch, 107 passed. The two files copied into the parent worktree as untracked files, run with `-k` on the new tests, 7 failed and 2 passed, then removed.
- No gate run, no model call.

## (d) Usage

About 100k input tokens, about 13k output tokens, about 113k in total, against a cap of 120k. These are estimates from the context counter, not the harness line.

One more pass: 1 high, 0 medium, 2 low.
