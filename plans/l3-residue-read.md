# The L3 residue read: L3-a-challenge-reaches-the-role-that-can-answer-it

Read on 2026-10-26 by a fresh agent on Opus, for session 8db3a3f9 (rota-b4), from `l3_residue_brief.md`. Read only. The register was read from a copy of `D:/repos/rota/tests/rota/cassettes.db` (509129 `case_runs` rows). The register is `tests/rota/cassettes.db` (`rota/paths.py` 60), not a file in `.rota/`.

Result: the case is a known red on qwen3:8b, not a residue that the suite reads green. The Terminologist writes criteria for the vague item and never sends `msg.challenge_vision_keeper`. The cause is the model's answer, and the case has had the same fault since 2026-09-13.

## 1. What the case asserts

The case asserts that a Terminologist on `tick: criteria` who meets an approved item it cannot build sends a message to the Vision Keeper, and that the Vision Keeper then answers with an item write or a decision write (observed: `tests/rota/cases/l3_handoffs.yaml` 100 to 123).

- The test is `tests/rota/test_l3.py::test_l3_chain`, line 91. The bar is 3 of 5 runs, line 131 (observed).
- The fixture holds one item and one ticket, both "make the reporting better" (observed: `l3_handoffs.yaml` 112 to 115).
- Leg one must send a message to `vision_keeper`. If it sends none, the run fails with "terminologist never messaged vision_keeper" before leg two starts (observed: `rota/testkit/fixtures.py` 1516 and 1562 to 1571).
- The `expect` and `forbidden` keys score leg two only (observed: `fixtures.py` 1587 and 1599). So the criteria that leg one writes do not fail the run. Only the missing message fails it.
- The route under test is the Terminologist's brief line for `msg.challenge_vision_keeper` (observed: `rota/roles/prompts/terminologist/base.md` 45 to 46, `criteria.md` 28 to 31). The case tests a brief route, not a door predicate (reasoned: no refusal in the five runs names vagueness).

## 2. What "the suite reads it green" means

No measurement reads the case green. The sender read the gate's silence about a known red as green (reasoned: from the diff logic below).

- The gate prints only the reds that moved against the baseline: `new_reds = failed - base_failed` and `gone = base_failed - failed` (observed: `rota/tools/gate.py` 580 to 582).
- The stored baseline `C:/Users/roman/rota_g328/.rota-gate.json`, commit f9f5cd19, 2026-10-18 15:51, holds `tests/rota/test_l3.py::test_l3_chain[L3-a-challenge-reaches-the-role-that-can-answer-it]` in its `failed` list (observed: the file).
- In the 18:16 gate output the case is in neither "new reds" nor "reds gone" (observed: `gate_e03b1098_rr.txt` lines 9 and 10). So the suite run held it red, as the baseline did (reasoned: a node absent from `failed` prints under "reds gone").
- The `rerecorded` line reads `casestatus` before and after the re-record: STALE, then FAIL 0/5 (observed: `gate.py` 506, 521 and 541). The plain run after the refresh failed, so the gate did not clear its red (observed: `gate.py` 316 and 548 to 550; line 5 of the output has no "red cleared").
- The next gate log in the same worktree, `C:/Users/roman/rota_g328/.rota-gate.log`, written 20:22, shows the replay red at 0/5 with "terminologist never messaged vision_keeper; sent nothing" on all five runs (observed: lines 125 to 131).

The two measurements are the `casestatus` state (FAIL 0/5) and the gate's red diff (no line for the case). They agree, and both say red. The diff hides a red that the baseline already holds (reasoned).

## 3. Why 5 of 5 live runs failed

All five runs fail for one cause: qwen3:8b writes invented criteria for "make the reporting better" and sends no message to the Vision Keeper (observed: `case_runs`, prompt hash 0447c235dbc24744, live rows seq 569632 to 569636, replay rows seq 569637 to 569641, 2026-10-26 18:12).

- Run 1, seq 569632: five `criteria.specify` calls with invented surfaces such as `generate_report`, then a prose summary. Sent nothing.
- Run 2, seq 569633: three criteria, then the reply wrote its own result "OK criteria.specify ->" and the stream stopped. Sent nothing.
- Run 3, seq 569634: six criteria. The seventh met the cap "six is many", whose text names `msg.challenge_vision_keeper` (`rota/roles/api.py` 6077). The seat did not send it.
- Run 4, seq 569635: three criteria. Sent nothing.
- Run 5, seq 569636: four criteria. Sent nothing.

The cause is a model answer that the case refuses (observed: the transcripts). It is not a harness error, because every run committed and called the tools. It is not a fixture mismatch, because the fixture rows loaded and the seat read the ticket (observed: `tickets.scan` in every `called` list).

The history shows a long-standing wall, not a change at a door (observed: `case_runs`, 2388 rows for the case, all on qwen3:8b, 4 passing rows):

- Prompt 2d0c8e96, to 2026-10-11: 1513 rows, 0 passes. Prompt 3d6355ba, 2026-10-12 to 10-21: 725 rows, 0 passes. Prompt fe65642c, 2026-10-24 to 10-26 07:24: 130 rows, 0 passes.
- Prompt ad304fa3, 2026-10-26 08:41: 2 of 5 (seq 567916 and 567919 pass), still below the bar of 3. This prompt carried the widened base line of 5c1f388c, "or when a ticket holds more than one piece of work".
- 864ea719 took that line back, because the line cost `L1-TE-challenge-an-unusable-item` two runs. The prompt hash then moved to 0447c235, the case read STALE, and the re-record gave 0 of 5 (observed: `git show 864ea719`; reasoned: the hash change follows the brief change).
- The case's own comment records 0 of 5 on 2026-09-13 with the same fault (observed: `l3_handoffs.yaml` 103 to 105). `plans/frame257-gate-reds-read.md`, section "Case 2", gives the same verdict.

The brief sends the Vision Keeper call for an item that "cannot mean anything consistent", a contradiction (observed: `base.md` 45, `criteria.md` 28 to 31). "Make the reporting better" is vague, not contradictory, so the brief gives the seat no clear trigger for this item (reasoned).

## 4. Which open frame the cause belongs to

The cause is not at the site of frames 328, 329, 330, 335, 336, 337 or 338 (observed: their Site lines in `plans/stack.md`).

- 328: `tests.encode` and the quote check of `msg.challenge_tester`. 329: `criteria.respecify` beside `_twin_refusal`. 330: `exhausted`, `preempt` and `parked`. 335: the parse check of `tests_encode`. 336: `_failure_line` of the page writer. 337: `_unnamed_contest`. 338: the relay split in `sandbox.py`.
- Frame 329 touches the criteria doors, but no run met a twin refusal (observed: no near-duplicate error in seq 569632 to 569636).

The nearest open frame is 322, "the Terminologist invents cases for the empty ticket" (observed: `plans/stack.md` 1463; listed open by `python -m rota.tools.state`). Its passes 5c1f388c, 44137683 and 864ea719 changed the Terminologist briefs and made the case STALE. Its last status, 08:57, says "e03b1098 stands on the branch; the gate decides it" (observed: `stack.md` 1494). The case is not in the Ends-when line of frame 322, so frame 322 does not own a fix for it (reasoned).

## 5. A wall for night 169

No. The case is a qwen3:8b chain recording on a vague fixture item, and the night seats the Terminologist on qwen3.5:9b with items from his own words (reasoned: frame 322 status 07:56, `stack.md` 1490; the case history above). The Terminologist briefs are the same at e03b1098 and 322da4b9, so the red is the same red that every gate since 2026-10-18 carries (observed: `git diff --stat e03b1098 322da4b9 -- rota/roles/prompts/` prints nothing; the baseline).

## Recommendation

Write a residue line on frame 322, not on frame 328, and open no frame. The case is a known red in the baseline since 2026-10-18 and a model wall on qwen3:8b since 2026-09-13. The one change that moved it, 2 of 5 under the line of 5c1f388c, cost a green case two runs. So a brief fix for this case alone fits one case. If a night shows a vague approved item with invented criteria on qwen3.5:9b, open a frame from that night's read.
