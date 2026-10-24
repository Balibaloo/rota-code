# Frame 303, review 2, of de647206: a Liaison wake resolves a batch ref

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r303` at de647206.
Verdict: the change stands. Two low findings and one medium finding stay open.

## (a) The verdict on each point

1. The seam: CONFIRMED. m108 is `architect -> liaison report`, `body_refs ["b_2"]`, `body_text` NULL. s232 has `trigger_msg m108`, `wake_refs []`. Its system turn (6796 characters) holds no `b_2`. Its user turn holds `b_2` only as the bare ref. With the change, the user turn holds a `resolved_refs.b_2` row: item `confirm_default_on_eof`, the item text, `status merged`, head `8717098b`, `last_verdict {result: pass}`.
2. The row: it reaches the seat in the user turn, under "The message that woke you:", as JSON. This is the same channel and the same key, `resolved_refs`, that every other resolved row uses. The `item_text` value is prose. `report.md` says "Read what it points at before you write the question", but it names no key. No brief names `resolved_refs`, so the batch row has the same status as an item row.
3. The reach: CONFIRMED by a static scan, not by the stale set. No Liaison case of 42 has a batch id in the refs of its inbound message. The one hit is `L1-AR-re-annotate-from-the-principals-correction`, an Architect wake, and its prompt does not change. Answer cases (sibling path) seed no batches. Tick wakes return `{}` before `_resolve_refs`. The gate showed 0 new reds, but the worktree has no register, so the gate printed no stale set.
4. The thin batch: CONFIRMED safe. An unknown id returns None and adds no row. A batch with an orphan item gives `item_text: null` and no `last_verdict`. A batch with no head gives `head_commit: null`. The prompt builds in each case.
5. The diff: two hunks, both as the report says. Findings 2 and 3 are details that the report does not give.

## (b) Findings

1. `tests/rota/test_frame303_case.py` line 57, low, CONFIRMED. The assertion `"invoice" not in user` is true without the fix. The invoice example is in the system turn (`report.md` line 18), and the recorded s232 user turn has no "invoice". The assertion guards nothing. Fix: assert on the m110 shape in a recorded replay, or delete the line.
2. `rota/core/runner.py` lines 2855 to 2860, low, PLAUSIBLE. `last_verdict` drops `commit_sha`. A pass on an older commit then reads as a pass on `head_commit`. Night 162's verdict matches its head, so night 162 does not show the gap. Fix: keep `commit_sha` in `last_verdict`, or mark the verdict when it differs from `head_commit`.
3. `rota/core/runner.py` lines 2811 to 2814, medium, PLAUSIBLE. The fix gives the facts, but nothing measures what s232 does with them. `report.md` gives the seat only one way out, `msg.clarify_principal`, plus the `prior_answers` relay. A merged and passed batch with no conflict can still give an empty question. The report states this as open question 3. Fix: run the s232 wake on the new prompt before the frame closes, and decide the brief step for "nothing to ask".
4. Outside, `rota/core/runner.py` line 2811, low, CONFIRMED. The gate is `role == "liaison"` on every message wake, not only on the report mode. On night 162 s233 (m109) also gets the b_2 row. The commit message says "a Liaison message wake", so the scope is as the commit states. Fix: none needed. Name the scope in the frame record.
5. Outside, the gate, low, CONFIRMED. With no `.rota-gate.json` in the worktree, the gate stored its own run as the baseline and compared the run with itself. So "new reds (0)" says nothing. Against the main baseline f9f5cd19, one red is new, `test_handover.py::test_release_empties_the_seat`. That test passed alone on a rerun, so it is flaky and not related to this diff. Fix: run the gate of a review against the main baseline file.

Stands: the row is correct on night 162 and on thin batches, no recorded case moves, and finding 3 is a brief question.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f1f0bcfa-7b93-4f01-99dc-afb4bf54e8a6/scratchpad/`.

- `r303_p1.py`: reads m108, m110 and s232 from `clickI_night162.db` with `mode=ro`. It runs `_batch_row` and `_resolve_refs` for the Liaison, the Developer and thin refs.
- An inline query on `turns`: s232's system turn has no `b_2`, and its user turn has only the ref.
- `r303_p2.py` on `r303_n162.db`, a backup copy of night 162: it runs `build_prompt` for m108. It also checks m105, m106 and m109.
- `r303_p3.py` and `r303_p3b.py`: they scan `tests/rota/cases/*.yaml` for Liaison wakes whose refs hold a batch id.
- `r303_p4.py` on `r303_p4.db`: thin, orphan and unknown batches, and two verdicts. The test confirms that the last rowid wins.
- The gate: `7 failed, 4592 passed`, 472 s. The failures were compared with `D:/repos/rota/.rota-gate.json`. The new test file gave 4 passed.

## (d) Usage

About 70k input tokens, about 10k output tokens, about 80k in total. These are estimates. The harness gives no exact count.
