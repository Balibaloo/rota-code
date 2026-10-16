# Frame 267, review 2: pass 1b at 5dded316

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_review_267b` at 5dded316. Date: 2026-10-16. Meta workflow.

Verdict: a pass 1c with one high. The high is cheap. The note skips the end line of the repeat door, but not the other end line of the runner.

## (a) Verdict on each point

1. The high of review 1 is closed for s226. A second end line of the same kind survives the skip (finding 1, high).
2. The once-per-ask cap holds. No path leaves a reply open with no wake. No path returns a page twice. The principal sees no change after a later lost answer (finding 3, low).
3. Seven callers. Only the landing wake of the Liaison passes `returned=False`. Park and shift pages keep the line.
4. Nothing moved outside the design. The two extra hunks are part of it and change no text that a seat reads.
5. All five tests fail at 0582873a for the reason each names. The replay completion matches the night copy exactly.

## Point 1: the note on s226

The replay of the six turns of s226 through `run_session` on a copy of night 151 gives this note on m108 (observed: probe 1). The note starts "unterminated argument list: a string in the value of rulings starts at character 67 after the open bracket." It names the unclosed string before `, words=`, and ends "Put the closing quote where that value ends, and change nothing else".

The head of the second wake reads "A session on this reply ended with no ruling. Its last refusal or error: unterminated argument list: ..." (observed: probe 1, `_missed_reply_line`). The errors list held the refusal, four parse errors and the end line of the repeat door, in that order (observed: probe 1).

The predicate is `str(e) != REPEAT_END` at `rota/core/db.py:744`. It drops one end line only. The runner has a second end door, `stop_reason` at `rota/core/runner.py:4553` and `:4561`: "{op} was refused the same way in four turns; the session ended on it". The runner appends it at `runner.py:3779` as the last error. The note then keeps that line and drops the refusal text before it (observed: probe 2). See finding 1.

No other error is wrongly dropped. `REPEAT_END` replaces the literal at `runner.py:4046` with the same text, so the account and the fixtures read the same line (observed: the diff). The cut lines join `outcome.errors` at `runner.py:4835`, after `SessionResult.errors` is copied at `:4807`, so they never reach the note (observed: `runner.py:4800-4836`).

## Point 2: the states of one ask

The page is m177. `attempts` rises at each dispatch (reasoned: the comment at `db.py:698`).

1. Reply 1, the first session misses. Attempts 1 is below 2. The reply stays open with the note, and the Liaison wakes on it again. The principal sees the page with no top line (observed: `db.py:1022-1029`, the s336 replay test).
2. Reply 1, the second session misses. The reply closes as answered. The page gets `m178: <note>` and stays open. The principal sees the line "Your last answer to this page did not reach the team." (observed: `db.py:1030-1042`, `test_a_second_reply_that_lands_no_ruling_returns_the_page`).
3. Reply 2, one session misses. `returned` is true, so the reply closes at once. The page keeps its first note. The principal sees the same page with the same line (observed: `db.py:1014-1021`, `test_a_page_comes_back_once_and_a_later_miss_closes_the_reply`).
4. Reply 3, one session misses. The result is the same as for reply 2. The page never gets a second note, so it never returns twice (reasoned: the branch writes no page row).

No reply stays open without a wake. Only the first-miss branch keeps a reply open, and it needs `returned` false and attempts below 2 (reasoned: the branch order at `db.py:1014-1029`). A reply on a returned page gets one session, not two, as the commit body says (observed: the commit body).

A suspended session gets no page, because `_page_under_reply` needs `checkpoint is None` (observed: `db.py:716`). A new page has a NULL note, so the cap is per ask (reasoned: `returned` reads the note of the page itself).

## Point 3: the callers of render_page

The map lists seven callers (observed: `rota.tools.map fn render_page`).

- `runner.py:2176` `resolve_inbound`, the landing wake, park included: `returned=False`, the line is out.
- `api.py:9294` `rulings_rule`: default. The line is in `page_text`, which only `_quotes_line` reads, for a line that starts `1.`.
- `api.py:9574` `rulings_line`: default. It uses the order only.
- `principal.py:194` `pending_asks`: default. The line is in, and this is the view of the principal.
- `principal.py:460` `render_ask`: default, with no `ask_id`, so the line never shows.
- `principal.py:1267` `_shift_waits`: default. It counts the order only.
- `principal.py:1758` `_page_order`: default. It uses the order only.

The landing wake is the only caller that turns the line off (observed: the list). Park and shift pages reach the principal through `pending_asks`, so they keep the line (reasoned: the default is True). The line has no `N.` head, so `_quotes_line` and the order do not move (observed: `api.py:9160`).

## Point 4: lines outside the four sites

Two hunks sit outside the note function, the converse head and `render_page`:

- `db.py:983-985` and `db.py:1014-1021`: the `returned` read and the closing branch in `session_commit`. They are the once-per-ask cap of the design.
- `runner.py:34-35` and `runner.py:4046`: the import and the use of `REPEAT_END`. The text is identical, so `session_note`, `loop.py` and `fixtures.py` read the same line.

No schema, op list or brief moved (observed: `git show --stat`, four files). The head text "Its last refusal or error" has one reader, `build_prompt` at `runner.py:628` (observed: the map). No tracked file outside the runner and its tests holds "Its last refusal" (observed: grep, `plans/` excluded).

## Point 5: the tests

At HEAD the seven runner tests on this path pass (observed: probe 3). At a `git archive` of 0582873a with the new test file, five fail and two pass (observed: probe 4):

- `test_the_second_wake_on_a_missed_reply_says_the_last_refusal`: the head lacks "or error".
- `test_the_note_names_the_newest_fault_not_a_fixed_refusal`: the note is the fixed refusal.
- `test_a_page_comes_back_once_and_a_later_miss_closes_the_reply`: the reply stays open.
- `test_the_landing_wake_shows_the_page_without_the_returned_line`: the landing page holds the line.
- `test_s336s_end_through_the_runner_keeps_then_returns_the_page`: the head wording at line 1925 only.

`S336_TURN_1` equals turns 1, 2 and 3 of s336 on the night copy, 728 characters (observed: probe 5). Turn 4 is the account of the runner. `S226_PARSE` is not the text of the night (finding 2).

## (b) Findings

1. `rota/core/db.py:744`. High. CONFIRMED for the function, PLAUSIBLE for the seat.
   The skip drops the end line of the repeat door only. The same-refusal door ends a session with "rulings.rule was refused the same way in four turns; the session ended on it" (`runner.py:4553`, `:4561`).
   Probe 2 gave that line as the note, and the refusal text was gone. The second wake then reads why the session ended, not what failed.
   The door fires for any op after four equal refusals with completions that differ, so a Liaison can reach it (reasoned: `runner.py:4560`).
   Fix: skip both end lines, for example with a tuple that holds `REPEAT_END` and the same-refusal stop line, and add one test.

2. `tests/rota/test_runner.py`, `S226_PARSE`. Low. CONFIRMED.
   The comment calls the constants the account of s226 on night 151, verbatim. The parse error of the night reads "a string in the value of rulings starts at character 67 ...". The test string is a generic parse error.
   The test still proves the order. The comment overstates the source.
   Fix: copy the line of the night, or remove the word "verbatim".

3. `rota/core/db.py:1014-1021`. Low. PLAUSIBLE.
   A lost answer on a returned page changes nothing the principal sees. The page shows the line of the first note again.
   A person cannot tell a second lost answer from an answer that the team still works on.
   Fix: count the closed replies to a returned page on the night. Add a second line only if the night shows one.

4. `rota/core/runner.py:3845`. Low. PLAUSIBLE.
   The "written as a list" line goes into `errors` once only. A session that repeats the list at its last turn keeps the line at its first position.
   An earlier, different error can then come after it and become the note.
   Fix: none now. Read the notes on the night for a note that names a fixed fault.

## (c) Probes

All probes ran on 2026-10-16. The scripts are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f267rev2/`.

1. `probe_s226.py` copies the night through the read-only URI to `n151b.db`. It rolls back m108, m107, m120 and their rulings, and replays turns 1 to 6 of s226 on m108. It wraps `_why_no_ruling` to print the errors, the refusals and the note, then prints `_missed_reply_line`.
2. An inline `python -c` calls `_why_no_ruling` on two built `SessionResult` rows. One holds four equal refusals and the same-refusal end line. One holds a prompt overrun.
3. `pytest tests/rota/test_runner.py -k ...` in the worktree: 7 passed.
4. `prev/` is a `git archive` of 0582873a with the new `test_runner.py` copied in. The same `pytest -k`: 5 failed, 2 passed.
5. An inline script compares `S336_TURN_1` with the `turns` rows of s336 on the read-only night copy.

No gate ran. The points needed no full suite.

## (d) Usage

The harness line holds the true figure. Estimate: about 50k input and 12k output, about 62k in total. No sub-agent ran.
