# Frame 325, pass 1: the review of 48eb9537

Verdict: Does not stand. The page change is right, but the resolve change makes 5 recorded Liaison cases STALE.

## (a) The points
1. Holds. m172's shape renders as designed: `order` is `["s1", "l_a69ad6edd4"]`, and the count line has no number. No test pins a reply that names line 3 (finding 4).
2. Partly. An `other` row is quiet only on the plain present page. It is unseen on the two touch pages, as before. `clarify` (`principal.py:1955-1959`) and the fallback (`1962-1965`) still show its words as context. The shift page (`1583-1616`) counts lines from `order` and notes as a number. `render_refs` (`2022-2025`) says "assumed:", but no code calls it. The wake's `resolved_refs` (`runner.py:2299`, `2578`) gives the Liaison the full text and now the kind.
3. The design gives no words. Section 8 line 372 says: "An `other` row goes to the quiet section and to a count on the night read." Section 5 gives "a count in a quiet section" for `invented`. The line is a count, so it fits. The night-read count is not built (finding 5).
4. Fails. `_resolve_refs` has 10 callers. `resolve_inbound` and `_resolve_contest` put the rows in a seat's user text, and the user text is in the cassette key. 323 qwen3:8b cassettes hold a resolved ledger row with no `kind` (finding 1).
5. Holds. The 7 named files give 60 passed. The new file at the baseline gives 3 failed and 1 passed, so `BEFORE` is the page at 7ebf2612. The commit changes no old test, so no assertion is weaker.

## (b) Findings
1. `rota/core/runner.py:2925`, high, CONFIRMED. `kind` on the ledger resolve changes the Liaison's wake bytes. `test_l1.py -k L1-LI` gives 6 failed at 48eb9537 and 1 failed at the baseline. The 5 new reds say "STALE ... no recording for the current prompt". casestatus does not compare the user text, so its "no stale case" is no evidence. Fix: read `kind` in `_page_body` with its own query, as `_quiet_line` reads `author`, and keep the resolve columns.
2. `rota/core/scheduler.py:1142-1150`, high, CONFIRMED for the wake, PLAUSIBLE for the repeat. `tick_agenda` still wakes a page for an open `other` row. The probe gives a wake `ledger=1` and a page with no numbered line that says "'ok' approves all of this". `order` is empty, so no ruling closes the row, and the agenda can fire again until the merge parks it. Provenance section 5 says "The tick and the hook stop waking a page for `other`". Fix: leave `kind = 'other'` out of `chosen` in `tick_agenda`, and pin the empty page.
3. `rota/roles/principal.py:1955-1965`, low, CONFIRMED. On `clarify` and on the fallback, an `other` row still shows its words to him as context. Fix: apply the `quiet` diversion on every verb, or record why only `present` needs it.
4. `tests/rota/test_frame325_quiet_other.py`, low, PLAUSIBLE. The tests pin `order` only. No test sends a reply that names line 3 through `land` or the Liaison's line refs. The Liaison's wake still holds the row's id, so a ruling by id may still land. Fix: add a test where a reply names line 3, and assert that the `other` row stays open.
5. Outside. `plans/frame204-design.md:372`, low, CONFIRMED by a read. The "count on the night read" and the three-of-one-shape signal have no code. Fix: name them as the next step of repair K in the frame.

## (c) Probes
All are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/r325/`.
- `p1_cassette_ledger.py`, `p2_resolved_ledger.py`, `p3_users.py`: read-only scans of `cassettes.db` for resolved ledger rows, by model and by ref.
- `test_l1.py -k L1-LI -n 6` in the worktree, with a copy of `cassettes.db` that the review deleted after the run, and in `D:/repos/rota` (rota and tests equal to 7ebf2612).
- `p4_other_only.py`: one open `other` row, `tick_agenda`, then `render_page` for `present` and `clarify`.
- `p5_base_test325.py`: the new test file run against the baseline checkout. The 7 pinned files ran in the worktree with `-n 6`.

## (d) Usage
About 75k input tokens and 10k output tokens, about 85k in total. This is an estimate from the session.
