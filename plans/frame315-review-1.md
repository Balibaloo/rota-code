# Frame 315, review 1 of ab2b8809

Verdict: the change stands. Two low findings and one high finding ask for a follow-up. None of them blocks the merge of pass 1.

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_p315` at ab2b8809 on fe4b3c78.

## (a) The verdict on each point

1. Old-ticket rule: right on night 161. It marks tk_1 of both re-sliced items old and nothing else. A live ticket can read as old only between an amend and its re-slice (finding 4).
2. Rulings selected: the query catches r_5346319ecc and r_206b20c23b through the item id and the old criteria ids. No ruling of another item enters on night 161. Rulings that name a new ticket's criteria also enter, and they crowd the cap (finding 1).
3. Cap of three: rowid is the insert order, and it equals the landing order on night 161. At s282 the cap drops m118 only, and m131 and the item text keep its point. The claim holds. At the end of the night the cap drops m131 and m137 (finding 1).
4. Wake size: the carry adds 2,063 characters for confirm_default_on_eof and 2,048 for version_option_show_python, in both wakes. No builder trims them. `_render` caps each key at 20,000 characters.
5. Unchanged path: proved. The rendered push is byte-identical with and without the carry for echo_json and how_it_works, in both wakes. 90 wake and push tests pass.
6. Hazards: none. The helper uses the caller's connection, and opens no path. The commit adds no CR byte and no debug print.

## (b) Findings

1. `rota/core/runner.py:3911-3920`. Severity high. CONFIRMED. The ruling set holds every ruling that names a criterion of any ticket of the item, the new ticket included. On the night 161 end state, the version_option_show_python carry holds r_40c94b2c6d, r_288739e866 and r_810ee68dc8. These three rulings say "take the confirm lines off this page". m131 and m137, the correction the carry exists for, drop out. A third slice after one more amend would show those three rulings. The pass report raises the same question.
   Fix: select rulings that name the item or an old ticket's criteria, and rank a contest or a revise above an approval within the cap.
2. `rota/core/runner.py:3922-3926`. Severity low. PLAUSIBLE. The carry shows the old criteria with their ids. s282's seat lost c_1 to the cross-ticket id refusal at `api.py:5374-5384`, which has no `_offer` (provenance Q4). A 9b seat that copies a shown id hits that refusal again.
   Fix: show the old criteria text without the id, or give the cross-ticket refusal an `_offer` with a new id.
3. `rota/core/runner.py:3913`. Severity low. PLAUSIBLE. `ORDER BY rowid` is the insert order of the ruling row, not its landing order. Two rulings open at the same time can land in the other order. On night 161 the rowid order follows the ask order on all 39 rows.
   Fix: order by the landing message's `seq` through `reply_id` or `verdict_id`, with rowid as the tie-break.
4. `rota/core/runner.py:3902-3906`. Severity low. PLAUSIBLE. The branch `item_ver < items.version` marks every ticket old after an amend, also a live ticket that has criteria. `db.py:487-488` raises `items.version` on any amending write. The criteria wake then labels a sibling's live criteria "written before the item changed". The label is true, but the seat can read live criteria as retired.
   Fix: in the criteria wake, use `not_retired` alone, and keep the `items.version` branch for the slicing wake.
5. `rota/core/runner.py:3904` and `3911`. Severity low. PLAUSIBLE. `names` holds the item and the criteria ids, not the ticket ids. A ruling whose `per_item` names only an old ticket id is missed. On night 161 r_c68fd20f2a names tk_1 and its criteria, so nothing is missed there.
   Fix: add the item's ticket ids to `names`.
6. Outside the points. `rota/core/scheduler.py:391`. Severity low. PLAUSIBLE. One slicing wake holds every item due for a slice. Each item adds its own carry, and the old criteria list has no cap. A night with many re-sliced items or many slices of one item grows the slicing wake with no bound below 20,000 characters for each key.
   Fix: cap the old criteria to the newest old ticket.

## (c) Probes

- Read-only queries on `D:/repos/rota/.rota/clickI_night161.db` with `?mode=ro`: tickets, items, criteria and all 39 rulings with `per_item`, `status` and `words`.
- `_retired_carry` on every night 161 item through a read-only connection. The probe printed the carry, its size, and every ruling that matches before the cap.
- A backup copy of the night 161 database at `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/f315r1_n161.db`. The probe built the sandbox and rendered `push_working_set` for four items in both wakes. It compared the real carry against a carry patched to empty.
- The sessions and messages rows of s281, s282, m136, m137, m139 and m140, for the order of the wakes and the rulings.
- `pytest` on `test_frame315_carry.py`, `test_pushes.py`, `test_push_scope.py`, `test_criteria_surface.py`, `test_cycles.py` and `test_steering.py`: 90 passed in 5.85 s.
- `git show ab2b8809` scanned for CR bytes and `print(`. The blob at fe4b3c78 has no CR. The working-tree CR bytes come from the checkout.

## (d) Usage

No exact counter is available to this agent. The estimate is about 70k input tokens and 9k output tokens, about 79k in total.
