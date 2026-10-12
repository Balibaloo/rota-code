# Frame 200, pass 4 review, commit bef80289

Reviewer: read-only agent on Opus, worktree `C:/Users/roman/rota_rv200p4` at bef80289 (2026-10-12).
Verdict: the commit does not stand. Night 142's row is fixed. The quote rule opens the 4de1555 chain and leaves two other chains unbounded.

## (a) Verdict on each point

1. Night's rows: PASS. The new test passes at bef80289 and fails at 6cc81151. The real night-142 database counts 0 priors at s491.
2. Guarded chains: FAIL. The 4de1555 each-test chain escapes the cap when the priors carry words. A reworded defect is never capped. The attempt cap restarts each round.
3. Quote match: FAIL in both directions. A loose quote counts out a kept line. A short fragment keeps a changed body at the cap. A line match with a minimum length is needed.
4. Escalation door: admitted on a receipt on another test of the refs. Acceptable by the rule, but the skip also serves the Tester's own escalations. Low.
5. "test changed and is still red": fires only on priors that still hold their line or have no words. The step is mostly the escalation now. Low.
6. Other readers: none keeps the old count. `_challenges_on` and `_cap_keys` have one caller each, the cap. Runner readers at `runner.py:2103` and `runner.py:2578` list history and do not count.

## (b) Findings

1. `rota/core/sandbox.py:1679-1690` and `:1798-1801`. HIGH. CONFIRMED.
   `_counted_tests` takes the tests that the current refs name. A prior on tst2 is then checked against tst1's body only.
   tst2 never changed, but its prior counts out after any receipt on tst1.
   Probe P6: the 4de1555 chain "one criterion against each test" with words on each prior.
   Two tests: landed m1 to m5, refused at round 6 (the test expects round 4).
   Three tests: landed m1 to m7, never refused.
   Fix: check each prior against the bodies and the receipts of the tests that the prior's own refs name.

2. `tests/rota/test_desk_guards.py:767-774` (`_msg`) and `_chain` at `:1154`. HIGH. CONFIRMED.
   The chain fixtures write no `body_text`. The guard tests pass through "a prior with no words keeps counting", not through the quote rule.
   A real challenge always carries words, because the binder raises when `quotes=` is empty (`sandbox.py:3425`).
   So the commit's claim that the 4968ea7 and 4de1555 chains stay at the cap holds only for rows that a night never writes.
   Probe P6 shows the cost (finding 1). The moves chain with words still stops at round 4 (P6m).
   Fix: let `_chain` write `" ... ".join(quotes_of(i))` as `body_text`, and re-run the 20 cap tests.

3. `rota/core/sandbox.py:1693-1720`. HIGH. CONFIRMED.
   A Tester that stores a new body each round, drops the quoted line, and keeps the defect in other words is never capped.
   Probe P2: body `result_i = close_account('a1')` then `assert result_i == 'closed'`, a new name each round. 8 of 8 challenges land.
   The attempt cap restarts too: a `tests` body write deletes the test's runs (`db.py:606-607`), and a moved test lifts the batch's quarantine (`db.py:621-635`).
   So the step budget of the night is the only bound now.
   Fix: keep a second, larger ceiling on landed challenges per criterion across bodies, for example 2 x LANDED_CHALLENGES.

4. `rota/core/sandbox.py:1708-1716`. HIGH. CONFIRMED.
   The evidence door admits a quote on one 12-character window (`_quotes_span`). The new match needs the whole quoted line as a substring.
   A quote with added words passes the door, never matches the body, and counts out after any receipt, also when the Tester kept the line.
   Probe P2c: quote `QUOTES[1] + "  # returns None here"`, body keeps `QUOTES[1]`. 5 of 5 land. The exact-quote control P2b refuses at round 4.
   Fix: at the match, use the body lines that the quote's windows hit, not the raw quote string.

5. `rota/core/sandbox.py:1708-1716`. LOW. CONFIRMED.
   The split is on `" ... "` only. A quote that holds the joiner splits into fragments. A dict of quotes joins on the same joiner.
   A quote that spans two lines works, because both sides are whitespace-normalised.
   A short fragment keeps every prior counting. Probe P3: quote `assert result` (13 characters). Bodies change each round. Refused at round 4, the night-142 shape again.
   `assert` alone fails the evidence door, so a bare token does not land.
   A criterion quote that the Tester copies into a test docstring does the same (PLAUSIBLE: every challenge quotes the criterion).
   Fix: drop a quoted line under about 20 characters, and drop the line that matches the criterion text.

6. `rota/core/sandbox.py:2059-2067`. LOW. CONFIRMED and PLAUSIBLE.
   CONFIRMED, probe P4: answered escalation m1, a `tests` receipt on tst9 (another test of c1 in the refs), new escalation on [c1, tst1, tst9]: admitted.
   An escalation quotes no body, so "a test of the refs changed" is the closest reading of the rule. This part is acceptable.
   PLAUSIBLE: the skip runs for every role's escalation. The Tester writes the `tests` receipts itself, so it can escalate, re-encode, and escalate again.
   Fix: apply the skip only when `ctx.role == "developer"`, or only on receipts from a session of another role.

7. `rota/core/sandbox.py:1827-1838`. LOW. PLAUSIBLE.
   The branch fires when a counted prior still holds its line, or has no words, a `tests` receipt landed after it, and the test is red.
   `_escalation_or_step` offers the escalation first. With the new escalation door a receipt usually admits it.
   The code step shows only when an escalation is open or answered with no receipt since. Then the Tester kept the disputed line, so a code change is the wrong step on a right product.
   Fix: when an escalation on the refs is open, end the session instead of the code step.

8. `rota/core/sandbox.py:1964-1968`. LOW. CONFIRMED by reading.
   The `_challenge_repeat_refusal` docstring still says the cap counts "across moves". It now counts per quoted body.
   Fix: change the docstring.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5d91f76d-246c-40b7-8ebe-acd318e106d2/scratchpad/`.

- `old6cc/`: `git archive 6cc81151` with the bef80289 test file. Selected tests: at 6cc81151, 2 failed (the two night-142 tests) and 2 passed. At bef80289, 4 passed.
  Old refusal text: "you sent challenge to tester on exactly these refs 3 times already (m1, m2, m3), and the test changed and is still red."
- `probe_n142.py` on a copy of `.rota/clickI_night142.db` in `n142/`. m331, m332, m333 each give `_quoted_body_gone = True` on tst_2 version 6. The cap's count on c2 is 0, from 3.
- `test_probe_rv200p4.py`, pytest from the worktree root: P2 (8 of 8 land), P2b (refused at 4), P2c (5 of 5 land), P3 (refused at 4), P4 (admitted), P6 two tests (refused at 6), P6 three tests (7 of 7 land), P6m (refused at 4).
- `tests/rota/test_desk_guards.py` at bef80289: 311 passed. The gate was not run.

## (d) Usage

Input tokens about 60k, output tokens about 8k, total about 68k (reviewer estimate, read the harness line). The run went about 8k over the 60k cap.
