# Frame 306, review of fac4045f, 19046a17 and 1464cfb7: his page corrections land

Reviewer: read-only, Opus. Worktree `C:/Users/roman/rota_r306w2` at 1464cfb7.
No gate and no model ran. The change does not stand as it is: two high findings.

## (a) Verdicts on the points

1. End to end: FAILS for the added line. In one relay session, two retires and the line-6 rewrite land. The `criteria.specify` call is refused by the cap. The next page shows five live criteria and no new line.
2. Old test: FAILS. A red test of a retired criterion still holds the merge and parks the batch. `park_criteria` lists retired rows on the park page.
3. Retire doors: HOLD with gaps. The door needs his ruling to drop the line. The row records the ruling. No op reverses a retire.
4. Schema: HOLDS. `retired_by` is nullable, the mark moved, and `test_identity` and `test_refs` pass. `NATURAL_KEYS` text is now incomplete.
5. Recorded cases: HOLDS on the report's evidence, PLAUSIBLE only. The new lines come only on a relay wake whose ruling drops or adds. 40 of the 81 cases are red, so a hash change there is invisible.
6. Add-line reader: NARROW. It misses "add a check that" and "add a line: X". It merges two adds into one. It files a line about another item under the contested ticket.

## (b) Findings

1. `rota/roles/api.py` 5633-5639 (`criteria_specify` cap), high, CONFIRMED.
   The cap counts live rows in the database plus staged specify writes. A retire staged in the same session does not free a seat.
   Night 163's ticket holds 7 live rows. The relay wake offers retire and specify together, and the wake text asks for both.
   Probe P1: retire x2, respecify, then specify gave "tk_1_clear_returns_bool has 7 criteria already". The refusal tells the seat to end.
   The added line is lost, because the relay message is answered and no second wake comes for it.
   The pass-1b cap test deletes a row and retires one before the session, so it never meets this path.
   Fix: subtract the ids of staged `retired_by` writes in `ctx.writes` from `existing` before the count.

2. `rota/core/lifecycle.py` 849-854 and `rota/core/scheduler.py` 1672-1682, high, CONFIRMED.
   `mergeable` counts every non-passing run at the head, with no criterion filter. A red test of a retired criterion holds the merge.
   `park_reds` puts that test in `own`, so the batch parks with a page. `park_criteria` lists both retired rows on that page.
   Probe P2: an old red test `tst_old` on `c3_no_terminal_true`. `park_reds` gave own `['tst_old']`. `park_rows` listed both retired criteria.
   `tests_triage` and the harness run also read the test, because neither joins `criteria` for state (read, not probed).
   Fix: when `criteria.retire` commits, abandon the tests of that criterion, or filter them out of the harness run, `mergeable`, `park_reds` and `park_criteria`.

3. `rota/roles/api.py` 6147 (`criteria_retire` write) and the report's deviation 4, low, CONFIRMED.
   The retire write is staged with `amends` true by default, so `_apply_write` bumps `version`. Probe P1 shows version 2 on both retired rows.
   The report says no version moves. The bump changes the park ask id in `_park_versions` and can open a new park ask.
   Fix: stage the retire as `("criteria", id, {...}, False)`, or correct the report and accept the move.

4. `rota/roles/api.py` 6080-6083 (`_ADD_LINE`), medium, CONFIRMED.
   Probe P6 results:
   - "Add a check that the output stays the same." gives no match.
   - "Please add a line: the output stays the same." gives no match.
   - "add a line that says X stays, and also add a line that says Y holds" gives one text with both sentences.
   - "Add a line that says clear() returns True, e.g. on a tty." cuts the text at "e".
   - "Add a line that says item two keeps its colour." lands under the ticket of the first contested criterion.
   Fix: stop the text at ", and also add", accept "check" and a colon, and leave a line out when the sentence names another item.

5. `rota/roles/api.py` 6125-6148 (`criteria_retire`), low, PLAUSIBLE.
   The door checks the ruling, not the wake. Any Terminologist mode with no `.tools` file offers every op, retire included.
   No op reverses a retire. A misread drop in `_line_dropped_on` therefore removes a line until he writes it again.
   Fix: refuse a retire when the wake is not a criterion relay, and add a principal-side restore path.

6. `rota/core/identity.py` 51-52, low, CONFIRMED by reading.
   The criteria rule says "same ticket, same words, one row". `_near_twin` now skips retired rows, so a retired text may return under a new id.
   Fix: add "among live rows" to the rule text.

7. Outside: `tests/rota/test_l1.py` evidence, low, PLAUSIBLE.
   The 81-case check keeps "the same failed list". A recorded case that was already red can change its prompt hash and show no difference.
   No recorded case was found to hold a ruling that drops or adds on a criterion relay. The reviewer did not search the cassettes.
   Fix: list the recorded criterion_repair relay wakes and assert that `_page_act_lines` is empty for each one.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e7141541-fc20-4c5c-a91b-4a10a610ec42/scratchpad/r306w2/test_probe_r306w2.py` reuses the `db` fixture of `test_frame306_page_acts.py`.
  - P1 `test_p1_one_session`: the relay wake allow list and lines, retire x2, respecify line 6 and specify c8 in one session, then commit, rows and page.
  - P1b `test_p1_two_sessions`: retires commit first. The next wake text then holds only the added line.
  - P2 `test_p2_park`: an old red test on a retired criterion, then `park_reds`, `park_rows` and `mergeable`.
  - P6 `test_p6_add`: seven phrasings through `_ADD_LINE`.
  - The command was `pytest <probe> -q -s --rootdir=C:/Users/roman/rota_r306w2`. The result was 10 passed, with the output above.
- `pytest tests/rota/test_identity.py test_refs.py test_frame306_page_acts.py test_frame306_respecify_twin.py`: 69 passed.

## (d) Usage

Estimate: about 48k input tokens, 9k output tokens, 57k total.

Stands line: does not stand. Findings 1 and 2 are high, and the brief names finding 2's route as high.
