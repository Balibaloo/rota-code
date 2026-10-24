Verdict: 460fdf30 stands. The predicate does what the brief says. Two test gaps remain, and neither blocks the merge.

# Frame 316, review 1 of 460fdf30

Reviewer: Opus, read-only in `C:/Users/roman/rota_p316` at 460fdf30 on fe4b3c78.

## (a) The verdict on each point

1. Stands. The owner comes from `_items_reached`. The skip fires only when every reached item has a non-None owner that is not the page's request. A note of no item keeps the carrier.
2. Stands. A note that reaches the page's item and another request's item keeps the contest. A note that reaches items of two other requests is skipped. Both outcomes are right.
3. The named test passes on both commits for a reason that does not pin the change. It should assert that the verdict holds no `items:echo_json`.
4. The four tests are red on fe4b3c78 and green on 460fdf30. They pin the skip side only. A predicate that skips every note with a reached item also passes all four.
5. Clean. The diff has no CR byte, no print, no `breakpoint`, no `connect` and no `?mode=ro` path.

## (b) Findings

1. `tests/rota/test_frame316_pass1.py:136-147`. Severity low. Confidence high. CONFIRMED. Test 3's docstring says the note about the page's own `c_2_..._format` still contests it. `_land` puts every `CRITERIA` id in `per_item`, so the criterion is in `ruled` and the carrier never runs for it. The mutation `elsewhere = bool(owners)` skips every note with a reached item, and all four tests still pass. Only `test_signoff_assumptions.py` catches the mutation, and only for a note whose `about_ref` is an item id. No test pins a note about the page's own criterion or ticket. Probe B shows that the code is right today: an unruled note about `tk_2_version_option_show_python` keeps the contest.
   Fix: add a test with an unruled note about the page's own ticket or criterion, and assert that its `about_ref` is in the verdict.
2. `tests/rota/test_signoff_assumptions.py:444-468`. Severity low. Confidence high. CONFIRMED. On fe4b3c78 the verdict holds `('items:echo_json', 'contest')`. On 460fdf30 the verdict does not hold it. `echo_json` stays `approved` on both commits, because `items:echo_json` is not an item id. The approval assertion therefore never tested the skip. The docstring still describes the old carrier.
   Fix: assert `"items:echo_json" not in verdict_for(db, mid)`, and say in the docstring that the challenge row is skipped.
3. `rota/roles/principal.py:2211-2216`. Severity low. Confidence low. PLAUSIBLE. An item that cites the page's statement and an earlier statement gets the earlier request from `request_of`. A note about that item's criterion is now skipped on the later page, and it was contested before. The same rule already applied to a note whose `about_ref` is the item id. `off_page` drops the same rows from the page, so the two doors agree.
   Fix: none in this frame. Name the case in the stack if a night shows it.
4. Outside the points. `rota/roles/principal.py:2211`. Severity low. Confidence low. PLAUSIBLE. A note whose `about_ref` is a statement id now reaches every item that cites the statement. When all those items are another request's, the carrier skips the note. Before, `request_of` of a statement id gave None, and the carrier contested it. The change is consistent with `off_page`, but the brief and the commit message name only criteria, tickets and tests.
   Fix: name the statement path in the frame's status line, or add one pin for it.
5. Outside the points. `tests/rota/test_frame316_pass1.py:116-133`. Severity low. Confidence high. CONFIRMED by reading. The provenance's red test 1 says that the verdict holds no `tst_4_confirm_default_on_eof`, and that no relay to the Terminologist names `cr_1`. The test asserts that `tst_4` stays, which agrees with repair 3 of the provenance. The test does not check the relay.
   Fix: assert that no message to the Terminologist after `land` names `cr_1` in its body refs.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/f316r1/`.

- `old/`: `git archive fe4b3c78` of `rota`, `tests` and `pyproject.toml`, plus the new test file from 460fdf30. The four tests ran there: 4 failed. In the worktree: 4 passed, and `test_signoff_assumptions.py` passed (25 passed in all).
- `probe_a.py`: ran in the worktree and in `old/`. Probe B: an unruled note about the page's own ticket keeps the contest on both commits. Probe C: item `x2` cites `s1` and `s3`. A note about `s3` reaches the page's item and `x2` of request `e_p1`, and the contest stays on both commits.
- `probe_b.py`: rebuilds `test_a_note_s_contest_reaches_the_page_s_own_request_item`. Old verdict holds `items:echo_json`. New verdict does not. `echo_json` is `approved` on both.
- `mut/`: `git archive 460fdf30` with `elsewhere = bool(owners)`. The four tests pass. Two `test_signoff_assumptions.py` tests fail. All 27 test files that call `land` ran: 5 failed. Three of the five are `test_refs.py` tests that also fail in the unmutated `old/` archive, because the archive has no untracked data. `test_refs.py` passes in the worktree.
- The diff of 460fdf30 has 0 CR bytes, and a grep found no print, `breakpoint`, `connect` or `mode=ro` in the added lines.

## (d) Usage

Input tokens: about 50k. Output tokens: about 8k. Total: about 58k. The counts are estimates from the context count.
