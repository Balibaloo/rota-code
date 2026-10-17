# Frame 290, review 1 of pass 1 (db99b45b)

Reviewer: a read-only agent on `C:/Users/roman/rota_r283old` at db99b45b. Date: 2026-10-17.
Workflow: the meta workflow reviews a pass on the rota workflow's Tester doors.

Verdict: the pass stands on the code. The count of point 6 does not stand.

## (a) The verdict on each point

1. A lift, not a change: CONFIRMED. The helper body is the removed block token for token, less `raise` and the return.
2. The frame of `_offer`: CONFIRMED safe. No reader keys on the function name alone, and the tests that read sites pass.
3. The `then` step: CONFIRMED correct. Neither offer carries `then`, and an `AGAIN` step on the encode offer is refused.
4. The order of checks: CONFIRMED safe. The contradiction offer takes the place of the `encodable` offer and keeps its order.
5. The red test: CONFIRMED. At the parent the new test fails on the `encodable` offer, and the follow check flags the same wall.
6. The count: does not stand. The 2 hits are the seat's own triage calls on another criterion. The wall count is 0 of 112.

## (b) Findings

1. `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0162323a-8602-4856-80d2-0fa70223b3b2/scratchpad/f290/count.py`, lines 7 and 21. Severity low. CONFIRMED.
   The numerator string `verdict='contradicts_request', request_span=` also matches the seat's own `TOOL: tests.triage(...)` call.
   Both hits are night 152, session s207, seq 2 and 3.
   In both, the next turn holds the seat's call `tests.triage(criterion_id='cr_3_confirm_default_on_eof_stdin_open', verdict='contradicts_request', ...)`.
   The encode offers named `cr_2_...` and `cr_1_...`, so no triage door refused them.
   A probe counted triage refusals with the text "Send tests.triage(criterion_id='X', verdict='contradicts_request'".
   It found 0 such refusals over nights 140 to 154, after an encode offer or otherwise.
   The wall comes from the replay of frame 143 pass 1d (the follow check), not from a night.
   Fix: write "0 of 112 on nights 140 to 154; the wall is a replay finding" in the status line and the register.
2. The same script, line 21. Severity low. PLAUSIBLE.
   112 is every new encode-door `encodable` offer, not the offers whose criterion contradicts the request.
   The rule "a door carries its count" wants the predicate's fires: `_contradiction_offer` on the 112 offered criteria.
   Fix: re-run `_contradiction_offer` against each night database for the 112 offered ids and report a of 112.
3. Outside. `L1-TS-a-criterion-that-contradicts-the-request-goes-back`. Severity low. PLAUSIBLE.
   The pass report says the case is not re-recorded and its encode refusal text changed. The gate shows it STALE until the re-record.
   Fix: re-record the case by exact id before the frame's gate acceptance.

No finding on the code of `rota/roles/api.py`.

## Detail on the points

1. The diff of `rota/roles/api.py` moves lines 6137 to 6161 of the parent into `_contradiction_offer` with no token change.
   The triage door keeps its gate `verdict == "encodable" and not done and request`.
   The encode door mirrors the gate: no row in `tests` for the criterion, and a non-empty request (`said = request and ...`).
2. `_offer` records the whole stack, not one frame. `Offer.site` reads it through `door_of`, from the statement up to the op.
   The readers are `sandbox.follow` (`door`, `raised_at`, the `AGAIN` compare `res.site != first`), `conftest._problems`, and `scene_tests.py:69`.
   `scene_tests.py:69` compares only the last element of the site, the op, which stays `tests_triage` or `tests_encode`.
   The probe shows two sites: `_contradiction_offer < tests_encode` and `_contradiction_offer < tests_triage`. The identities stay distinct.
   `KNOWN_REFUSED_OFFERS` keys on the node id and the second refusal text, not on a site.
   `test_triage_fork.py` and `test_offers_followed.py` at HEAD: 93 passed, 3 xfailed.
3. The triage door's own `contradicts_request` offer had `then=()` before the pass and has it now.
   The verdict routes the criterion. `ctx.triaged[c]` becomes `contradicts_request`, and the triage door returns "End the session".
   A later encode of that criterion in the same session is refused: "c1 was triaged contradicts_request in this session" (probe P5).
   So an `AGAIN` step would make the follow check fail. No `then` is right.
   The next wake: the staged question goes to the Terminologist, born unresolved, and `criterion_repair` wakes the criterion's writer.
   After the rewrite, `tests_missing` wakes the Tester for the new text, and that session triages and encodes.
4. The encode door refuses in this order: the placeholder id, the routed criterion, `_must_exist`, the fork.
   The contradiction offer sits inside the fork branch, before the `.py` path, the parse and the fence checks.
   Before the pass, the `encodable` offer sat at the same place. So the pass changes the offer text and not the order.
   Probe P1: `id='...'` gets the placeholder refusal first. Probes P2 and P3: a `.txt` path and a bad body get the contradiction offer.
   Probe P4: after `cannot`, the routed refusal comes first. Each first offer names a call that lands.
5. A scratch copy of the parent tree with the HEAD test file: 1 failed, 1 passed.
   The failure: `assert "verdict='contradicts_request'" in "c1 has no triage verdict from you yet. Call tests.triage(criterion_id='c1', verdict='encodable') ..."`.
   The follow check's section names the second refusal "c1 says 'returns' and item i1 says 'prints'" at `api.py:6153 in tests_triage`.
   That is the wall of `plans/frame143-pass1d-read.md`, line 46.
6. The re-run prints the implementer's numbers: total 2 of 112, both on night 152. Finding 1 gives their shape.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0162323a-8602-4856-80d2-0fa70223b3b2/scratchpad/f290/`.

- `r1parent/`: `git archive HEAD~1` plus the HEAD `tests/rota/test_triage_fork.py`. It ran `pytest -k encode_before_triage` (point 5).
- `r1head/`: `git archive HEAD` plus `tests/rota/test_r1probe.py`. Probes P1 to P8 ran on the fork fixtures (points 2, 3, 4).
- `count.py`: the implementer's script, re-run unchanged (point 6).
- `r1count2.py`: prints the two night 152 hits with their context (finding 1).
- `r1count3.py`: counts the triage contradiction refusals on nights 140 to 154, and found 0 (finding 1).
- `r1count.py`: a first try on the last turn of each session. It read empty last turns and found nothing.
- In the worktree: `pytest tests/rota/test_triage_fork.py tests/rota/test_offers_followed.py`. No tracked file changed. No git command changed the tree.

## (d) Usage

The harness line holds the exact numbers. The estimate is about 45k input and 9k output, about 54k in total.
