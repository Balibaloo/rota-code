# Frame 322, review of pass 1

Verdict: stands. Commit 7f158750 in `C:/Users/roman/rota_r322`. No high. Two mediums.

## (a) The points

1. Stands. On s199's state the wake's detail is `No criterion yet: tk_2 (clear() returns False when stdout is not a terminal). Covered: tk_1_clear_returns_bool (clear() returns True when it cleared the screen).` The refs hold the item. CONFIRMED by probe 1 on a copy of the night database.
2. Stands. The refusal of `c2_non_terminal_false` names tk_2 and its headline and drops "second sentence". The covered item keeps the old text. CONFIRMED by the new test file, 5 passed.
3. Stands. The diff of `criteria_specify` touches one line, `api.py` 5767. The other doors are unchanged. CONFIRMED by `git diff a49c96a0 7f158750`.
4. Stands, with finding 2. Before, the push showed each non-superseded statement the item's refs name, s2 only. Now it also shows each ratified statement on s2's entry. The gap is real: the item refs s2 on `e_p3`, s3 sits on `e_m65`, s4 on `e_m84`, and no refs row joins them to the item. CONFIRMED by probe 1.
5. Stands. The 13 files: 791 passed, 4 xfailed. `casestatus` returned in under two minutes and holds no measurement in the worktree, 166 never measured. CONFIRMED by probe 3.

## (b) Findings

1. Medium. `rota/core/runner.py` 423-440. `tick:criteria` joins `DETAIL_SHOWN` with no register case that carries its detail. The comment at 426 makes the case the condition. CONFIRMED: `tests/rota/cases/l1_terminologist.yaml` has no `detail:` line, and `fixtures.case_wake` sets `criteria`, which `build_prompt` drops. The register never measures the new line. Fix: give `L1-TE-specify-criteria` a `detail:` with one empty ticket, and let it re-record at the gate.
2. Medium. `rota/core/runner.py` 4297-4303. The second branch takes every ratified statement on the entry, whatever item it names. CONFIRMED by probe 2: one entry, s1 named by `f_one` and s2 named by `g_quiet`. The push for `f_one` showed both sentences as "the principal said". A page entry that rules two items pushes the other item's words to this seat. Fix: exclude a statement that another item's refs name.
3. Low, outside. `rota/core/scheduler.py` 459-461. `criteria_tickets` counts a retired criterion as cover, as `tick_criteria` does, while the twin door skips retired rows. The two agree with the wake, so no fix now. Note it for frame 319.
4. Low, outside. Cause 2 of W7 stays open. The report says so in (e)1. Fix: a frame that follows the thread chain `m65 -> m63 -> e_m50 -> r_9aa589dc0a.per_item` with a rule for a ruling that names two items.

## (c) Probes

All ran from `C:/Users/roman/rota_r322` with `D:/repos/rota/.venv/Scripts/python.exe`, in the Bash tool, not saved to disk.

1. Night rows: tickets, criteria, item refs, statements s1 to s4, statements on `e_p3`, then a `backup()` copy with the later criteria deleted, `tick_criteria`, `criteria_detail`, and the new push query for both items.
2. A fresh `init_db`, one entry with two ratified statements, two items that each ref one, `push_working_set` for `f_one`.
3. `pytest` on the new test file (5 passed) and on the 13 criteria files (791 passed, 4 xfailed). `rota.tools.casestatus` under `timeout 115`.

## (d) Usage

About 42k input tokens and 6k output tokens, about 48k in total.
