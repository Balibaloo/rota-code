# Review of F25, commit f4951389 on f25root, pass 1

Verdict: not ready to merge. The commit adds 2 reds that the pass reports as old reds. The approve offer can rule a line against his words. Counts: 3 high, 3 low.

Worktree: C:/Users/roman/rota_f25 at f4951389, parent 9827e38a. Parent tree: C:/Users/roman/rota_g328.

## (a) Verdicts on the points

1. Partly. The follower reads the doors' function, but both differ from the runtime list on a criterion_repair page-act wake (F1).
2. Yes. Every old caller of `_wake_mode_tools` gets the same list. No caller sees None.
3. No. The offer approves each line the seat's map leaves out. The door's rule is about the lines the reply does not contest (F3).
4. No offer picks a verdict for the seat. All three calls land. A question-back word loses its own call (F4).
5. The count is honest. 3 of the 11 entries are false positives, because the lint reads only enclosing `if` guards (F5).
6. The 2 extra reds are in `test_identity.py` and `test_frame308_ruling_answer.py`. f4951389 causes both (F2).
7. Yes for the live shape, by a scripted replay of the gate's calls. The L1 replays of the two cases did not run at the f25 gate (F6).

## (b) Findings

1. `rota/core/sandbox.py:5383-5386`, `held_calls`. Severity high. CONFIRMED.
   The runtime builds the seat's list with `runner._wake_allow`. That list adds `criteria.retire` and `criteria.specify` on a criterion relay wake with page acts.
   `held_calls` intersects `sb.functions()` with `_wake_mode_set`, and `criterion_repair.tools` holds neither op.
   Probe p1 built that sandbox. `sb.functions()` holds `criteria.specify`, and `held_calls` does not. An offer of `criteria.specify` got `not_in_mode == ['criteria.specify']`.
   The doors read `_wake_mode_tools` and have the same gap. That gap is older than this commit.
   Fix: make one function that returns the runtime list, the mode set plus the page acts, and use it in `_wake_allow`, `_wake_mode_set` and `held_calls`.

2. `rota/core/sandbox.py:5383` with `tests/rota/conftest.py:201`. Severity high. CONFIRMED.
   The 8 named reds give 6 failed at 9827e38a and 8 failed at f4951389.
   The 2 new reds are `test_identity.py::test_an_assumption_is_about_an_artefact_never_about_an_assumption` and `test_frame308_ruling_answer.py::test_an_approved_criterion_with_a_ruled_test_counts_among_the_ruled`.
   Each fails on the new mode check. The first: `ledger_log ... the mode 'deliver' does not hold it`. The second: `_ruling_answer_refusal ... msg.answer_tester ... the mode 'relay' does not hold it`.
   In the first test, the test builds a `deliver` sandbox and calls `ledger.log`, which `deliver.tools` does not hold. In the second test, the sandbox gets the `criterion_repair` list, but its trigger m101 keys `relay` (probe p6: `park_criterion_relay` is False).
   So both tests build a sandbox that does not match its wake. The check is right that no live seat sees these offers. The pass report says "0 new reds", because the worktree baseline already held the two reds.
   Fix: skip the mode check when the refused call itself is outside `held`, or make the two sandboxes match their wakes. Rebuild the f25 baseline from 9827e38a.

3. `rota/roles/api.py:11327-11330`, `_stray_act_fields`. Severity high. CONFIRMED.
   `_unruled_lines` reads the seat's map. It does not read his words. Every line the map leaves out gets approve.
   The door at `api.py:13312-13321` names the rule "a line the reply does not contest is approve". That door then lets the seat read the reply.
   Probe p3b set the reply to "please drop line 3, and line 2 is wrong too". The offer gave line 2 approve. The next door refused it: "The words fault line 2 ... It takes no approve."
   So the tool rules line 2 for him against his words, and the follow check would show a second refusal. The two unit tests use replies that fault no other line, so they pass.
   Fix: give approve only to a line that the fault reader of `rulings_rule` does not name. Name any other unruled line, and do not give it a verdict.

4. `rota/roles/api.py:11356-11372`, `_stray_on_shift`. Severity low. CONFIRMED.
   `SHIFT_WORDS` maps `ask`, `unclear` and `question` to None, which means a question back. The offer reads None as "no word", and it offers later, now and drop.
   `_ruling_word` offers `rulings.rule(ask=...)` for those words. Probe p4 sent `{"1": "ask", "act": "drop"}` and got three verdict offers and no ask call.
   The lookup is exact, but `_ruling_word` also matches the first word. So "later please" also gets three offers in place of one.
   Fix: use the `_ruling_word` match, and offer the ask call when the word is a question back.

5. `tests/rota/_refusal_calls.py:153-166`, `_guards`. Severity low. CONFIRMED.
   The lint reads only the tests of enclosing `if` nodes. It does not read an early return or a context attribute that the mode arms. 3 entries of `KNOWN_UNHELD` are false positives:
   - `_owner_call:msg.challenge_tester`. `api.py:13675` returns None when `"msg.challenge_tester" not in working`.
   - `tests_encode:tests.triage`. The text sits under `hasattr(ctx, "triaged")` at `api.py:9324`. `sandbox.py:813` arms `ctx.triaged` only when the mode holds `tests.triage`. Probe p5: challenge and answer do not arm it, and tests_missing does.
   - `_contradiction_offer:tests.triage`. Both callers, `tests_triage` and the guarded block of `tests_encode` at `api.py:9339`, need the mode to hold `tests.triage`.
   The `_revert_refusal` entries are true positives. `_escalation_admitted` and `_challenge_admitted` check the repeat and evidence doors, not the mode. `tests_encode:ledger.log` and `tests_encode:schedule.reask` have no guard and are true positives.
   Fix: take the 3 entries out of the table, and mark them guarded in the lint by the early-return form and the `triaged` arm.

6. The pass report, section (b), "Casestatus". Severity low. PLAUSIBLE.
   The report says the recorded qwen3:8b runs of both cases send no stray fields. `gate_9827e38a.txt` lines 108-131 show that both L1 cases sent stray fields and failed the follow check.
   The f25 worktree has no register, so its gate skipped the L1 cases. The new refusal text changes the next prompt of those runs, so a replay can miss its recording.
   Probe p7 sent the gate's exact first calls through a scripted seat. Both cases land with the new offers. A model run did not happen.
   Fix: run the two L1 cases where the register exists, before the merge.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/f25p/`. Each ran from the f25 worktree with `PYTHONPATH` set to it.

- `p1.py`: builds a terminologist sandbox with the criterion_repair list plus the page-act ops, then calls `held_calls` and `follow`.
- `p3.py` and `p3b.py`: runs the dropped-line case with a scripted seat. p3b sets the reply to fault line 2 too.
- `p4.py`: runs the separate-request case with the first verdicts contest and ask, and picks later, now and drop.
- `p5.py`: builds tester sandboxes in three modes and reads `ctx.triaged`.
- `p6.py`: reads the m101 trigger of the frame 308 fixture and its wake mode key.
- `p7.py`: sends the gate's exact first calls of the two Liaison cases through a scripted seat.
- pytest: the 8 named tests in rota_g328 and rota_f25 (6 and 8 failed), then the 2 extra reds alone with `-n0`. `tests/rota/test_f25_offers_in_mode.py` did not run again.

## (d) Usage

- Input tokens: about 55k, an estimate. The harness gives no exact split.
- Output tokens: about 9k, an estimate.
- Total: about 64k, against a cap of 60k.

## Review p2

Scope: pass 1b (fbf9bbc4) and pass 1c (f0ef3086) on f25root, in C:/Users/roman/rota_f25.
Verdict: 4 findings closed, 1 partly closed, 1 open. Pass 1c adds 1 new high finding. Point (a) shows no live leak.

### The six findings

1. Closed. `_wake_mode_set` now returns `runner._wake_allow` for a sandbox with a wake. The doors and the follower read one list.
   The new test `test_the_follower_and_the_doors_hold_the_page_acts_of_the_wake` passes.
   Side effect: `_wake_mode_tools` now also gives the 9 door callers the page acts. A door text can change on a criterion relay wake.
2. Closed. The two tests pass. Run: the touched files and the two tests gave `72 passed, 7 xfailed`.
3. Partly closed. Probe p3b ran again. When his reply faults line 2, the offer gives line 2 no approve, and the door records no offer for line 2. When his reply faults no other line, lines 1 and 2 get approve.
   The refusal text still holds the full call `rulings.rule(rulings={"1": "approve", "3": {...}})` before "Add line 2 to the same call". The scripted seat sent that call, and the door refused it with "lines 2 have no ruling".
   So the text names a call that the doors refuse, which is against frame 135's law. The follower and the lint do not see it, because the call is not an `_offer`.
   Fix: when a line is open, leave the call out of the text, and name only the lines and their fields.
4. Closed. Probe p4 ran again. `ask` now gets one offer, `rulings.rule(ask="<one sentence about line 1>")`, and no verdict. `_word_key` gives "later please" the word door's match.
5. Closed by the read. 4 entries left `KNOWN_UNHELD`, and 7 strict xfails stay. The lint now reads an early return and a flag that `sandbox.build` arms. The test comment names the forms that the lint does not read.
6. Open. No model run of the two L1 cases happened. The pass 1b report agrees that the recordings claim was false.

### (a) An offer of the refused op counts as held

The exemption lets no live offer outside the mode through. CONFIRMED by the read.
`Sandbox.call` resolves the op through `self[artefact]`, and that raises `NotInWorkingSet` for an op that the built list does not hold. The built list is `_wake_allow` with the situational narrowing.
So a live door that refuses op X met a seat whose list holds X, and an offer of X is in the mode. The other ops of each offer and of each `then` step stay checked.
The cost is only in tests. A test sandbox that holds the whole graph gets no mode check on an offer of its own op. The 2 tests of finding 2 still build sandboxes that do not match their wakes.

### (b) Pass 1c, his reply whole as `words`

The offer picks a verdict for him. Severity high. CONFIRMED by probe p8.
`_shift_acts_conflict` at `api.py`, about line 11377, keeps the seat's word in `rulings`. It checks only that the word is a shift word. It does not check that the word agrees with the shift word that his reply holds.
Probe p8 used night 171's reply, which starts "Later for line 1: put the screen-clearing change aside".
- The seat sent `{"1": "now"}`. The refusal said "his words say 'Later'", and it then offered `rulings.rule(rulings={"1": "now"}, words="Later for line 1: ...")`. That call landed `{"i_ecb6a9": "now"}`.
- The seat sent `{"1": "drop"}`. `heard` picked 'drop' from his reply, because it takes the shift word that matches the seat's verdict. The offer landed `{"i_ecb6a9": "drop"}`.
So the door names a ready call with a verdict that his words contradict. His whole reply in `words` then stamps that verdict as his. The words field only carries text. The verdict comes from the seat, and the door confirms the seat's verdict where it should check it.
Fix: offer the call only when the seat's verdict maps to the same shift meaning as every shift word of his reply. Otherwise name the conflict and record no offer.

### Probes of p2

All are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/f25p/`.
- `p3b.py` ran again with two replies: one that faults line 2, and the case's own reply.
- `p4.py` ran again.
- `p8.py` is new. It sends night 171's reply with the seat's verdicts now and drop and an approve and keep in `acts`, then reads the rulings rows.
- pytest: `test_f25_offers_in_mode.py`, `test_frame306_page_acts.py` and the two tests of finding 2 gave `72 passed, 7 xfailed`.

### Usage of p2

- Input tokens: about 30k, an estimate.
- Output tokens: about 5k, an estimate.
- Total: about 35k, against a cap of 35k.
