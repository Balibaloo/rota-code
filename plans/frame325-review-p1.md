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

## Re-check of bda07c54
Verdict: Does not stand. Findings 1, 3 and 4 are fixed, but an `other` row now reaches no page that the tick wakes.
1. Fixed, CONFIRMED. `git diff 7ebf2612 -- rota/core/runner.py` is empty, so the Liaison's wake bytes equal the baseline. `test_l1.py -k L1-LI` on a copy of `cassettes.db` gives 1 failed and 37 passed, the same red as the baseline. The review deleted the copy.
2. Half fixed, high, CONFIRMED. An `other` row alone wakes no page: `tick_agenda` returns `[]`. An `other` row beside a `default` row wakes the Liaison with `refs=('l_d',)` only, because `first` is built from `chosen` (`scheduler.py:1221`). The page from those refs shows "1. the tip is typed each time" and no count line. The test `test_an_other_row_beside_a_default_row_rides_the_page` passes its own refs to `_page`, not the wake's, so it misses this. The comment at `scheduler.py:1144` says the row "rides only on a page that a different row wakes", but no code adds it. The row is then on no page, which breaks "visible and countable" (composition, Records). Fix: append the page's open `other` rows to the wake's refs after `first`, and pin the test on `wakes[0].refs`.
3. Fixed, CONFIRMED. On `clarify`, `confirm` and the fallback, the probe finds no words of the `other` row.
4. Fixed for line numbers, CONFIRMED. The test sends "3: take this off the page", and the row stays open with no `rulings` row. A ruling keyed by the row's id still lands: `rulings_rule` admits `key in keys`, and `keys` is the page's refs (`api.py:12044`, `12087`). It matters only for `contest`, which contests the row's item through `land`. Low. Fix: refuse a key that is a quiet `other` id on a present page.
5. Pins hold. The 7 files give 66 passed. The diff removes no test line, so no assertion is weaker.
Probe: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/r325/p6_pass2.py`. Re-check usage: about 30k input and 4k output tokens, an estimate.
Does not stand

## Re-check of c7367d0f
Verdict: Stands. Finding 2 is fixed in full.
1. Fixed, CONFIRMED. `p6_pass2.py`: an `other` row alone wakes no page. Beside a `default` row, the wake's refs are `('l_d', 'l_o')`. The page from those refs shows "1. the tip is typed each time" and then "Not shown: 1 note from the Developer that fits no category."
2. The limit, CONFIRMED by `p7_cap.py`. When 7 rows fill the cap of 7 (`PAGE_ASSUMPTIONS`), the `other` row drops out of the refs. The row stays open and rides on a later page when the cap has room. That is acceptable for a quiet count line, because the line asks nothing and nothing waits on it. The count on the full page is low by the dropped rows. Low.
3. Outside, low, PLAUSIBLE. `riders` skips the held-item filter at `scheduler.py:1166`. A rider of a held item can then ride a page. `on_page` drops a row of another item, so the effect is small.
4. Pins hold. The 7 files give 66 passed. 4 test lines changed. The page is now built from the tick's refs, and the reply names line 2, the count line's position on that page. No assertion is weaker.
Usage for this re-check: about 15k input and 2k output tokens, an estimate.
Stands

## Review of 4519ac1c
Verdict: Stands, with one plausible misread of "after intent" to fix in a later pass.
1. Holds, CONFIRMED by the new file. A `default` row of an approved item under `auto` wakes no page by itself. It rides in the refs of the page that a conflict wakes, as `('l_c', 'l_d')`. The page lists it as "  - <words>" under `QUIET_DEFAULTS`, and `order` is `["l_c"]`.
2. Holds, CONFIRMED by `p8_bytes.py` on the worktree and on `git archive 73e1cf69` in `r325/base73`. Before intent and under `review`, the wake's refs are `('l_c', 'l_d')`, `order` is `['l_c', 'l_d']`, and the page hash is `214d7294fc42` at both commits.
3. A misread exists, PLAUSIBLE, medium. `quiet_defaults` (`principal.py:1717-1734`) reads `approval = 'approved'` and not `approval_ver = version`. An item that changed after his approval still reads as approved, so a `default` row about the new text loses its number. Law 9 treats that item as not approved. A second, low case: on the sign-off page he approves line 1 and leaves line 2 open. A default row of item 1 then goes quiet before the request's intent is settled. Fix: require `approval_ver = version`, and read intent from the request's sign-off page, not from each item.
4. Holds. `git diff 7ebf2612 -- rota/core/runner.py` is empty. `test_l1.py -k L1-LI` gives 1 failed and 37 passed, as at the baseline. The review deleted the copy of `cassettes.db`.
5. Holds, with one low gap. The 7 pins add `_review(db)` and lose no assertion. Each still checks what it checked, but only under `review`. No pin now checks the per-item page scope under `auto`, the default gate, with a non-default row. Fix: copy one scope pin with a `conflict` row under `auto`.
6. No other reader disagrees with the page. `_shift_waits` counts the lines of `order` and every open note. `ledger.list` and the cockpit read rows, not pages. An "ok" leaves the listed rows open, and the merge parks them, as section 5 rules.
Counts: the 9 files give 90 passed. Probe: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/r325/p8_bytes.py`.
Usage for this review: about 25k input and 4k output tokens, an estimate.
Stands
