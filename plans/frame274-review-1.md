# Frame 274, review 1: commit db1296e1 (pass 1)

Reviewer: a read-only agent on the worktree C:/Users/roman/rota_r274 at db1296e1, 2026-10-16.
Verdict: do not accept as is. One high finding and one low finding. The high fix is one clause.

## (a) Verdicts on the points

1. PARTLY HOLDS. A note about the page's own item, an item with no statement, and a page with no request keep today's result (CONFIRMED, probe cases 1a, 1c, 1d). A note about a description on a request page changes (CONFIRMED, case 1b). See finding 1.
2. HOLDS. The note's row resolves with an "overruled at signoff" decision, and the verdict keeps `l1: contest` for the relay to the note's owner (CONFIRMED, probe case 3 and the new test). The probe used the test's copy of night 152's m59 and m60 rows, not the night database.
3. HOLDS. The parent's `land` sets `echo_json` contested on the red test's shape, and the test asserts `approved` (CONFIRMED, probe case 3, old against new).
4. HOLDS. Both paths reach the changed lines. `rota/core/loop.py:232` calls `pump`. `rota/cli.py:845` calls `pump(conn, OneShot())`. `pump` calls `land` at `rota/roles/principal.py:1728`. `apply_rulings` calls `land` at `rota/roles/principal.py:2201`. The changed lines are `rota/roles/principal.py:1986-1989`.
5. HOLDS, by a read. The skip removes one wake only: the `contested` predicate at `rota/core/predicates.py:301-304` no longer wakes the Vision Keeper on `echo_json`. The verdict's `body_refs` and `verdict_for` no longer name `echo_json` (the new test asserts both). The next page does not show `echo_json` as contested and does not send it back for sign-off. The note still relays to its owner. The quarantine wake (`rota/core/predicates.py:1632-1660`) reads message status only, and the commit changes no message status. `render_page` (`rota/roles/principal.py:1337`) takes no new input from the change.
6. HOLDS. The diff stat is two files: `rota/roles/principal.py` +16 -1, and `tests/rota/test_signoff_assumptions.py` +128. The principal hunk adds a lazy sentinel for `page_req` and the predicate, with a comment. The test hunk adds one fixture and three tests. Nothing moves outside the design.

## (b) Findings

1. HIGH. `rota/roles/principal.py:1987-1989`. CONFIRMED. A note about a description on a request page loses the carrier. `request_of` gives a description the earliest request it cites. `off_page` (`rota/roles/principal.py:965-970`) rules that "The account belongs to no request, whatever statement it cites", but the new predicate does not exempt a description. Probe case 1b puts `how_it_works` (cites s1 and s2) on the confirm page, with a contested note about it. The parent sets `how_it_works` contested. The commit leaves it `draft` and drops it from the verdict. Night 152's real confirm page carries `how_it_works`, as the new test's fixture shows, so the shape is live. The count's 36 right calls hold descriptions only on pages with no request, so the count does not measure this shape (0 of 42 instances). Fix: keep the carrier when `_is_description(conn, row["about_ref"])` is true, and add a test for case 1b.
2. LOW. `rota/roles/principal.py:1986`. PLAUSIBLE. `land` reads `page_request` without the `current_request(conn, unread=False)` gate that `off_page` uses at line 953. `off_page` treats a run with no request boundary as one request, and every item keeps its line. In every probe case `current_request` was None, and the skip still fired (case 3, and the red test itself). A run whose items cite statements of two entries with no request boundary can lose a right contest. No night in the count shows the shape, because `_root_statement` folds a follow-up into its root. Fix: read `page_req` as None when `current_request(conn, unread=False)` is None, as `off_page` does, or write in the comment why the gate differs.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/04be1489-62d6-4964-8f68-ab5f38d2d1ea/scratchpad/r274/probe.py`. It loads the parent's `principal.py` (`principal_old.py`, from `git show db1296e1~1`) as a second module. It runs the old and the new `land` on five shapes built on the new test's `_two_requests` fixture. It prints `page_request`, `current_request`, the watched item's approval and the verdict.
- Results: 1a own item, contested in both. 1b description note on the confirm page, contested before and `draft` after. 1c item with no statement, contested in both. 1d page of a description and a note, `page_request` reads e_p1 from the note, contested in both. 3 the red test's shape, contested before and `approved` after.
- `pytest tests/rota/test_signoff_assumptions.py -q` on the worktree: 20 passed. The full gate was not run, because no point needed it.

## (d) Usage

Input about 40k tokens, output about 6k tokens, total about 46k tokens (estimated from the context count, not the harness line).
