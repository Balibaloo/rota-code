# Frame 200, review of pass 4b at deeda588

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200p4` at deeda588. Date: 2026-10-12.

Verdict: the pass stands. No high finding. Four low findings.

## (a) Verdict on each point

1. Night's rows: PASS. The night-142 tests pass at deeda588 and fail at 6cc81151. The real night-142 database counts 0 priors on c2, from 3.
2. Guarded chains: PASS. The moves chain and the new-id chain stay at the cap with words. A reworded chain now stops at the ceiling, the 7th challenge. The attempt cap still restarts on each reword, so the ceiling is the only bound.
3. Quote match: PASS. The split is on " ... ". A quote across two lines matches, because both sides are flattened. A quote under 20 characters ties no body, so `assert` keeps the prior counting. The exact tie to the sender's prompt replaces a line match.
4. Escalation door: unchanged since bef80289. A receipt on another test of the refs admits a new escalation. Low, as before.
5. "test changed and is still red": the step is now the end or the escalation, unless another test of the batch is red. That is right for night 142.
6. Other readers: none keeps the old count. The cap has three callers in `_challenge_repeat_refusal`, at lines 2076, 2084 and 2111, and all three get the ceiling.
7. Sender's prompt: sound enough to ship. A cut or evicted prompt fails toward the cap. On four nights, 35 of 35 woken challenges found the right sender and tied their quotes. A `tests` version row is not needed now.
8. Ceiling step: the escalation when its door admits, else the end. The step is never a code change. The no-words test now describes a prior with no tied line, not a seat output.

## (b) Findings

1. `rota/core/sandbox.py:1769-1783`. LOW. PLAUSIBLE. A tied line need not be a test line. A quote of another criterion of the batch passes the evidence door at `sandbox.py:1255-1258`. That quote stands in the prompt, is not in this criterion's words, and no test holds it. When the test-side quote is loose and so untied, the prior counts out on any `tests` receipt. The same holds after a Terminologist rewords the criterion. Both shapes are bounded by the ceiling. Fix: tie only lines that stood in a test body inside the sender's prompt, or require a tied line from the test side.
2. `rota/core/sandbox.py:1736-1737`. LOW. PLAUSIBLE. The escape undo replaces `\n` before `\\`. A test body with a string literal such as `"a\nb"` shows in JSON as `a\\nb`, and the undo turns it into a backslash and a newline. The quote then does not tie, and the prior keeps counting. The error is in the safe direction. Fix: decode the JSON string with `json.loads` where the prompt holds one, or undo `\\` first through a placeholder.
3. `rota/core/sandbox.py:2088-2093`. LOW. CONFIRMED by reading. The judged path refuses with `_code_step` and does not read the ceiling. Past six landed challenges, a judged prior still names a code change as the step. Fix: read the ceiling before the judged sentence, or pass END_STEP when the ceiling is met.
4. `rota/core/sandbox.py:1894-1897` with the escalation door. LOW. PLAUSIBLE. At the ceiling the step is the escalation. The escalation door admits a new escalation after any `tests` receipt on a test of the refs (point 4). A Tester that rewords each round can then drive one escalation per body after the ceiling. No probe ran on the escalation count. Fix: give the escalation door a ceiling per criterion, or name the escalation only once past the ceiling.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5d91f76d-246c-40b7-8ebe-acd318e106d2/scratchpad/`.

- `old6cc/`: `git archive 6cc81151` with the deeda588 test file. Selected tests: 3 failed at 6cc81151, the two night-142 tests and the ceiling test. 4 passed.
- `tests/rota/test_desk_guards.py` at deeda588: 315 passed in 90 seconds. The gate was not run.
- `probe_n142.py` on the copy `n142/clickI_night142.db` at deeda588: m331, m332 and m333 give `_quoted_body_gone = True`. m348 gives False. The count on c2 is 0 of 3 landed.
- `probe_sender.py` on copies of nights 139 to 142 in `n142/` and `nights/`: 35 challenges. 34 woke a session, and in each the found sender called `challenge_tester`. 0 quotes were untied. Night 140 holds one challenge that woke no session.

## (d) Usage

Input tokens: about 50k. Output tokens: about 6k. Total: about 56k. These are estimates from the context count, not the harness line.
