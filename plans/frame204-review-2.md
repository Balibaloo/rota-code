# Frame 204, pass 2: diff review of e7971500

Reviewer on Opus, 2026-10-13, read-only on a worktree at e7971500. Rota workflow unless a line says meta workflow.

Verdict: the hold matches section 4, and the tests pin it. One high finding: the Developer's `challenge` brief dictates a `scope` log that the new door refuses. Counts: 1 high, 5 low.

## (a) Verdicts on the points

1. The hold: correct against section 4, steps 1 to 5. 19 of 19 pass. With the check cut, 6 go red (detail below).
2. The `scope` door: a defect of the pass, not a wall for the night. `challenge.md` still dictates the refused call (finding 1).
3. The `conflict` door: night 138's three real `c_1` rows pass, and its four reconcile echoes are refused. A terse real conflict is refused (finding 2).
4. The attest door and the two tests: both changes are the implementer's, not the design's. The attest change is sound. The test pin is fragile (finding 5).
5. `waiting_on`: only `waiting_filter` reads it, through `frontier` and `frontier_readonly`. No page changes. The tick set and the cockpit frontier change for four roles (finding 4).
6. The new case: it is sound but measures no hold. A body that asks nothing cannot pass, because the challenge door needs both rows quoted verbatim (finding 6).
7. Line endings: 0 CR bytes in the six files. STE in the new prose holds, except one refusal text (finding 2).

### Point 1 in detail

The nine tests that the design lists map to these tests:

- Held by an open challenge: `test_an_open_challenge_holds_the_merge`.
- Held by an open question: `test_an_open_question_holds_the_merge`.
- Held by an unresolved question with a next rung: `test_an_unresolved_question_with_a_next_rung_holds_the_merge`.
- Held by a routed conflict row: `test_a_routed_conflict_row_holds_the_merge_and_is_named`.
- Held by a path note through its session's batch: `test_a_path_note_reaches_its_batch_through_its_session`.
- Not held by a quarantined question: `test_a_quarantined_question_holds_nothing`.
- Not held by a triage-made unresolved question: `test_a_question_the_triage_made_unresolved_holds_nothing`.
- Not held by a conflict row on a pair with no edge: `test_a_conflict_row_on_a_pair_with_no_edge_holds_nothing`.
- Released by an answer: `test_an_answer_releases_the_merge`.

The brief says eight. The design lists nine items: five holds, three negatives and one release. The other ten tests are a path note of another batch, the review gate after the hold, two `waiting_filter` cases, four conflict-door cases and two scope-door cases.

With `waiting_on_a_seat` patched to return None, 6 tests go red: the five holds and the release. The three negatives, the path note of another batch and the review gate stay green. A negative test cannot fail when the check is absent, so these four guard only against an over-wide hold.

The route through `receipts` is real. Night 138 has 71 ledger receipts for 71 ledger rows, and both `tests/test_utils/` rows carry one receipt each. The ladder's last rung is `liaison`, and the `unresolved` predicate has no `needs_principal` gate. So no hold waits on a page.

### Point 2 in detail

- `L1-DV-take-out-what-nobody-asked-for` (`l1_answers.yaml:253`). The wake is a Critic challenge, mode `challenge`. The seat logs `scope` on `c1`: "the ellipsis character is required to indicate truncation". That note is a reading of the criterion, category 2 or 7. Category 4 does not cover it. The rename that the case is about is never named.
- `L2-DV-name-the-block-rather-than-retry` (`l1_exhausted.yaml:13`). The tick is `exhausted`. The seat logs `scope` on `c1`: "The criterion 'every invoice field' requires all fields to be present in the export". That note is a reading, and its real cause is a criterion against constraint `k1`, category 3. Category 4 does not cover it. The same run already sends `msg.question_vision_keeper`.
- `developer/challenge.md:9-10` tells the seat to log `kind="scope"` and leave the change in. The `challenge` mode holds `msg.question_vision_keeper`, so the door now refuses that exact call. The brief's own honest answer is a refused call. That is a defect of the pass.
- The `tests_failing` brief says nothing about `scope` or `ledger.log`. Only the comment in `tests_failing.tools:14` lists `scope` among the kinds. In that mode the door writes the row, and the row holds nothing.
- What the door should say to a misfiled `scope` note: name the test of category 4, which is work you left out or added. Then name `default` for a reading of a criterion and `conflict` for two rows that disagree.

### Point 3 in detail

Night 143's ten rows in step 0 are all Vision Keeper reconcile notes that quote an account item. The door's restated test fits that shape. DECISIONS of 2026-09-12, point 4, makes two documents that disagree ask the principal. The door keeps that rule, because a README side that differs from the item still writes. On night 138, the door refuses the four reconcile rows that quote the item. It passes all three `c_1` and `tk_1` conflict rows, for example "The criterion c_1 states separators=(",", ":") but the test expects spaces after colon".

## (b) Findings

1. **`rota/roles/prompts/developer/challenge.md:9-10` against `rota/roles/api.py:8339-8353`. High. CONFIRMED.** The brief says to `ledger.log` with `kind="scope"` and leave the change in. The door refuses that call in the `challenge` mode and offers a Vision Keeper question. probe_doors.py showed "challenge scope refused" and that the offered call was admitted as `m1`. So every "it had to be there" answer becomes a question that holds the merge until the attempt cap. The same is true for misfiled readings in `batch_start`, `exhausted`, `findings_exhausted` and `verdict_failed`. `batch_start.md:46` and five `.tools` comments still list `scope` as a ledger kind. Fix: in the same pass, change `challenge.md:9-10` and `batch_start.md:46` to the question call, and make the refusal name `default` for a reading of a criterion.
2. **`rota/roles/api.py:8381-8436`, `_misplaced_conflict`. Low. CONFIRMED.** The restated test runs for every seat and every mode, not only for a reconcile wake. The probe made a Developer note about criterion `c2`: "echo_json writes compact JSON with separators comma colon and no spaces, the test disagrees". The door refused it in all four modes. The refusal tells a Developer about the README and the code. It also calls a criterion "the principal's ... words". Night 138's real `c_1` rows pass, so no measured conflict is lost. Fix: run the restated branch only when `about_ref` is an item or `@prose`, or when the seat is the Vision Keeper.
3. **`rota/core/lifecycle.py:442-461`, `_batch_rows`, with `waiting_on_a_seat`. Low. PLAUSIBLE.** On night 138, `b_1` (abandoned) and `b_2` (merged) have the same rows except the batch id: `tk_1`, `c_1` to `c_6`, `echo_json` and `tst_c*`. An owed challenge or escalate from `b_1` can therefore hold `b_2` until it is quarantined. Nothing found closes an abandoned batch's messages at the abandon. Night 138's messages were all `answered` by the night's end, so the overlap in time is not proved. Fix: skip a message whose sending session's batch is abandoned, or close it at the abandon.
4. **`rota/core/scheduler.py:1411-1414`, `waiting_on`. Low. PLAUSIBLE.** The filter is per role and covers every non-message wake. The Critic sends `challenge` to the Developer, and the Architect and the Terminologist send `challenge` to the Vision Keeper. Night 138 has four Architect challenges, `m54`, `m61`, `m83` and `m107`. While each one is open, the Architect gets no tick for any batch. The design's table names this change for every role. So the design owns it, but section 3.2 only reasons about the Developer. `frontier_readonly` changes the cockpit frontier in the same way. Fix: name in the design whether the Critic's and the Architect's challenges hold their ticks, and measure it on the walk.
5. **`tests/rota/test_request_page.py:1108-1113` and `:1187-1191`. Low. CONFIRMED.** Before, both tests built the Developer with the default tool set. Now both use the `tests_failing` set, so `scope` stays a row. Design section 3.1 adds `msg.question_vision_keeper` to `developer/tests_failing.tools` in pass 2. The implementer deferred that change. When it lands, both tests go red again. The tie-break test logs `"default, invented"` and never logs `scope`, so its change was not needed. Fix: pin a mode that the design leaves without the call, `answer` or `finding_violated`, and revert the tie-break test.
6. **`tests/rota/cases/l1_developer.yaml`, `L1-DV-ask-when-the-test-contradicts-its-criterion-at-the-fix-wake`. Low. CONFIRMED.** The new case has the same tick, the same `expect` and the same forbidden calls as `L1-DV-challenge-a-test-that-contradicts-its-criterion` (`l1_developer.yaml:232`). It asserts no hold, so it measures the old route on a new fixture. probe_challenge.py showed that `msg.challenge_tester` refuses quotes that are not verbatim from both rows. So a challenge that asks nothing cannot pass. Fix: keep the case as night 138's shape, and add a no-model test that the challenge it expects holds `mergeable`.

Outside the points: the attest door change (`api.py:3720-3724`) is sound. A `found` with no row still meets the later check at `api.py:3745`. The decision-alone refusal does not carry `RESTATED_ROW`, so it holds the attest once. That is the existing rule.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/31e55586-b1a2-4672-8fdb-8f8a2c2b2f46/scratchpad/rv204p2/`. They ran from the worktree `C:/Users/roman/rota_rv204p2` at e7971500.

- `pytest tests/rota/test_frame204_pass2.py -q`: 19 passed.
- `cutplug.py`, a pytest plugin loaded with `-p cutplug`, makes `waiting_on_a_seat` return None: 6 failed, 13 passed.
- A night 138 copy, `clickI_night138.db`: `waiting_on_a_seat` and `_batch_rows` for `b_1` to `b_3`, the ledger receipts, and the owed messages.
- The same copy: `_misplaced_conflict` over 18 conflict-like ledger rows refused 4 reconcile echoes and passed 14, the `c_1` rows among them.
- `probe_doors.py`: a `scope` log and a `conflict` log in four Developer modes, and the offered question call after the refusal.
- `probe_challenge.py`, with an inline follow-up: `msg.challenge_tester` with empty quotes and with quotes that are not verbatim.
- The `case_runs.transcript` column in `tests/rota/cassettes.db` for the two stale cases, read-only.
- A CR byte count on the six files: 0 in each.

## (d) Usage

The reviewer's estimate: about 75k input, 12k output, about 87k in total. The harness line is the measure.
