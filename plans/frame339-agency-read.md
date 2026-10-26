# Frame 339, the agency read: the removal door

Read-only read on Opus, 2026-10-26, at HEAD 19b41a89. Code lines are at HEAD. The register is the scratchpad copy `f339_clickI_copy.db` of session 8db3a3f9, opened `?mode=ro`. The fix under judgement is the recommended option 1 that the session put to Roman at about 21:00 (observed: transcript 8db3a3f9, the terminal reply "Recommended. The drop note becomes a row on the stopped page"). No fix is built.

**Verdict: wrong premise.** The frame places the cause in how the door reads his permission. The code shows that the door asks for a permission at all, inside a definition that every criterion names, where law 12 and his ruling of 2026-10-17 record the change for the Architect (observed: `rota/DECISIONS.md:1503`, "a door that refuses a write for the want of a criterion is a wall to fix, not a rule"). The recommended fix covers 2 of 5 instances of that cause, and 1 of 12 of the frame's own reach.

## 1. The purpose

The door `_unruled_removal` (`rota/roles/api.py:20562`) closes night 158's wall. There the Developer s279 dropped `ctx.exit()` from the callback of `version_option`, logged a false note "unreachable", and bb7c4492 landed the removal (observed: `tests/rota/test_frame283_removal_on_ruling.py:1-12`). The session built it in frame 283, W1 a, pass 1, commit 92e240fc, 2026-10-21, from night 158's read. No ruling of Roman's made it. The only cited source is the composition line "Only a fact or a ruling gates" (observed: `plans/frame339-provenance.md`, Q1; ruled: C, 2026-09-16). The `line N` matcher came in pass 2, 2acc7b5c, 2026-10-23, with no brief that asked for it (observed: the same, Q2). The door's purpose is to stop a removal that nobody wanted from reaching a merge (reasoned: the test docstring and the frame 283 Ends-when).

## 2. What exists

| Record or mechanism | Where | What it already does for this case |
|---|---|---|
| `criteria.surface_refs` | register copy, crit_1 to crit_3 | Each criterion of batch_1 names `src/click/utils.py::get_app_dir`, the definition that holds the removed line (observed: copy) |
| The item text | register copy, `get_app_dir_windows` | "use the AppData Roaming or AppData Local folder ... instead of the bare home folder". His request asks for the rewrite by behaviour (observed: copy) |
| `drop_notes` | `rota/core/schema.sql:370`; api.py:20930 | Holds the batch, the path, the owner and the removed line in structured form (observed) |
| `touch_strays` with `note` | schema.sql:354; api.py:20470-20500 | Records a change outside the prediction. "The commit stands. The Architect is asked whether it was foreseen or a mistake before the batch merges" (observed) |
| `_unnamed_def_strays` | api.py:21317 | Frame 286's change of 2026-10-17: the unnamed-definition door stopped refusing and records a definition stray, by his ruling (observed: api.py:19860-19884) |
| `touch_strayed`, `touch_mistaken` | `rota/core/predicates.py:2370`, 2395 | Wake the Architect to judge, and wake the Developer to take out a mistake. The merge waits (observed) |
| `batches.judge_touch` and the mode | api.py:21355; `rota/roles/prompts/architect/touch_strayed.md` | The Architect's verdict, foreseen or mistake, per grain (observed) |
| `rulings.per_item` | schema.sql:671-692 | r_58bf1e8c70 holds `"batch_1": "approve"` and `"get_app_dir_windows": "approve"`. `_ruling_texts` (api.py:20856) selects by these keys, then reads only the words (observed: copy; `plans/frame339-reach.md` section 1) |
| `msg.escalate_architect` | api.py:21193-21216 | The route to keep a change exists, but the `batch_start` mode lacks the tool, so the refusal names none (observed) |

## 3. The reach

The cause by the code: a commit door refuses a change for the want of a named permission, and turns that want into a question for the Principal. Law 12 says "nothing rejects a diff for straying outside it" (observed: `rota/LAWS.md:339`). The ruling of 2026-10-17 sends an unexpected change to the Architect (ruled: Roman, 2026-10-17 16:50, `DECISIONS.md:1490`). The kept backstop "a removal" in that ruling is the fence's file-removal kind, `rmtree` and `unlink`, not a removed statement (observed: `rota/core/fence.py:38-42`).

Instances in `rota/` and `tests/` with this gap (observed: the lines; the grouping is reasoned):

1. `_unruled_removal`, api.py:20562, called at 20327, with its reader `_asks_removal` 20822, `_unruled_gone` 20849 and `_ruling_texts` 20856. The refusal.
2. `_refused_commit`, `rota/roles/principal.py:1402-1500`, the sentence to copy at 1482. It asks him for the permission the door wants.
3. `land`, principal.py:2207-2214. It lifts the quarantine on the answer's arrival, so a refused Developer restarts into the same refusal.
4. `_note_routes`, api.py:21193-21216. The `batch_start` mode gets no route to keep the change.
5. The scenes that encode the refusal: `tests/rota/test_frame283_removal_on_ruling.py`, 22 tests, and `tests/rota/test_frame312_stuck_review.py:179-210`.

The count is 5 (observed). The same gap stopped night 163 too: m115 showed "rewrites `return` at line 609 ... as `return False`", a rewrite the criteria asked for (observed: test_frame312_stuck_review.py:183-185; `plans/frame312-review-w5.md:49-55` via the provenance). Frame 286 was the sixth instance, and it is fixed (observed: api.py:20470). The fence and api.py:5755 are out of the reach (reasoned: a ruled backstop, and a check on a criterion, not on a write).

The frame's own reach, from the reach read, is 11 readers of his words by a phrase that gate a permission, and 1 lift: 12 (observed: `plans/frame339-reach.md` sections 2 and 4).

## 4. The fix against the reach

Option 1 makes the drop note a row on the stopped page, reads his verdict on the row, and offers the Architect route on the page (observed: the transcript). Against the 5:

- Instance 1: in part. The door reads a record, but it still refuses until he answers.
- Instance 2: yes. A row replaces the sentence to copy.
- Instance 3: no. The lift still reads arrival, not the verdict.
- Instance 4: yes, on the page. The Developer's mode still lacks the call.
- Instance 5: the scenes change with any fix.

The first stop is not covered. s124's three refusals and the first quarantine came before any words of his on the removal existed (observed: provenance Q5). So every criterion-asked rewrite still costs three Developer sessions, one stop page and one answer of his (reasoned). Against the frame's own 12, option 1 covers P1 only, 1 of 12. The session named the other ten for a later frame (observed: the transcript).

## 5. My proposal

I would not propose the same fix. The door should record, not refuse, as frame 286 did:

1. In `code_commit`, write a `touch_strays` row for an unruled removal, grain `path::owner`, the removed line in `note`, and let the commit stand (api.py:20327, 20475; LAWS.md:339).
2. Keep `_unruled_gone` as the detector, and drop the `line N` branch at api.py:20844, because no seat then needs his words in a fixed form (provenance Q2).
3. The Architect judges in `touch_strayed`, and `touch_mistaken` wakes the Developer to put the line back. Night 158's `ctx.exit()` is caught there before merge (predicates.py:2370, 2395; ruled: Roman, 2026-10-17).
4. Remove the refusal lines and the sentence to copy from `_refused_commit` (principal.py:1468-1483). The lift at 2207 then has no refusal loop to restart.
5. Rewrite the scenes of test_frame283_removal_on_ruling.py and test_frame312_stuck_review.py:179-210 to assert the stray row and the landed commit, with s122's write and m37 as the red case.

Price: a door change, 2 to 3 cycles, about 30k of the holding session, and about 150k to 190k of agent tokens for one cold implementer pass, one review and one resumed fix (observed: `plans/operating-facts.md:241-247`). The night count is 0 cycles. Option 1 costs about 3 cycles too, plus one stop page and one answer of his on each criterion-asked rewrite (reasoned: composition line 103, attention is the scarcest budget). The 11 other phrase readers stay a separate frame, because they read his words about page rows, not a permission for code (reasoned: `plans/frame339-reach.md` section 2).

## 6. The doubt

- The Architect is a small model. It can judge a wanted-looking removal "foreseen", as s279's note claimed "unreachable", and a removal can then merge (reasoned; not measured on any night).
- I did not run the Architect's `touch_strayed` mode on a removal grain, and I did not check that its prompt shows the stray `note` (not checked).
- A ruling after 2026-10-17 that keeps a statement removal behind his word would make this proposal a departure. The provenance's greps found none, and I did not repeat them (observed: provenance Q4; not re-checked).
