# Review p2 of frame 330: be53aee1 (pass 1b) and 1304c56c (pass 2)

Verdict: the pass 1b claim holds. The pass 2 claim holds on a fresh page and fails on dry1 itself. 1 high, 4 low. Tests: 347 passed, 4 skipped, 5 xfailed, L3R 23 of 25.

Worktree `C:/Users/roman/rota_f354r` at 1304c56c. Copy of dry1 from after turn 9: `scratchpad/dry1w5/dry1.db`, never written. Every probe copies it first.

## (a) The points

1. Holds in part. `park_rows(conn, "bg_1")` gives the item and three criteria. `park_untested` is true. But `park_ask` returns `[]` on the copy, so the seat never gets the page (finding 1). The page, rendered through `_park_page`, is quoted under probe 1. Every line is one the seat can act on. No sentence names a raw id, a key or a tool. The attempts sentence reads "the team could not write the tests after 3 attempts".
2. Holds, with the Terminologist's move as the tests shortcut it. A `rewrite` on line 2 lands as `contest` on `tk_1_criteria_skipped`. The key stays until the criterion's version moves. After the move: `quarantined_keys` is `[]`, `parked` is false, `next_batch` offers `bg_1`, `frontier` returns the Liaison's message wake first and `developer tick:batch_start bg_1` second. A second give-up parks at once: `spent_park` says "past its cap and its ladder is spent", and the park ask opens under the new id `m_park_04cf311ed9_bg_1`. The pass report's doubt 1 is right (finding 3).
3. Holds. All four rows approve, the ruling rests, the batch stays `deferred`, `frontier` is empty. The status line reads: "Stuck: bg_1 stops here. You approved its lines as they stand, and the team could not write the tests. A new commit on the change starts it again." On the copy an open intake ask hides that line (finding 4).
4. Holds. A held wake at 2 attempts, cap 3, keeps 2 across a `frontier` call that parks. `frontier_readonly` and `frontier` both return `do:park batch_1`. The read and the write agree within one pass, because the pass writes no count for a wake it does not perform. The probe shows the row unchanged after `frontier`.
5. The reading matches the ruling's words. It is narrower than the ruling's reason (finding 5). A batch with green own tests and red project tests keeps the note, as point 3 says.
6. Three hunks sit outside the claim: `parked_line` (declared, deviation 4), the `check: no test yet.` branch, and the import swap in `park_ask` (finding 2).
7. Eight files: 347 passed, 4 skipped, 5 xfailed. L3R: 23 of 25. The reds are `L3R-n171-m27-m28` and `L3R-n172-m76-m77`, the two off the brief's 23 of 25. No case is off that count.

## (b) Findings

1. `rota/core/scheduler.py` 2372-2400, `park_ask_id`. High. CONFIRMED. On the dry1 copy `park_ask` returns `[]`, while `park_rows` returns four rows. The rested note `m_park_ac1ca5b10a_bg_1` carries the same id that `park_ask_id` computes now, because the id reads the batch, the head, the keys, the versions and the closed asks that did not rest, and never the kind. A rested note stops the ask. So the deploy of 1304c56c shows dry1's seat no page, and the wall the frame fixes stays. No test replays a rested note whose rows grow, so the suite is green. Fix: fold `park_rows` into the hash of `park_ask_id`, so a note that becomes a page asks again under a new id.
2. `rota/roles/principal.py` 2114-2115, `request_block`. Low. CONFIRMED by the diff. The `if park:` branch fires for every park page row with no test, the red-own-test page included. That page read "check: none yet." before. The claim names the untested page alone. Fix: guard the branch with `park_untested(conn, batch)`, or declare the change in the pass report.
3. `rota/core/predicates.py` `spent_park`, with `_next_rung`. Low. CONFIRMED. After the resume the Tester gets `tick_attempt_cap` attempts, 3 on dry1, and no rung. The second park asks at once under a new id. That matches the red-own-test page today, and Roman already ruled on the rows. Fix: none now. Record in the frame that his rewrite buys three Tester attempts, not a new ladder.
4. `rota/roles/principal.py` `_render_state`. Low. CONFIRMED. On the copy the state prints "Waiting on you. Did I hear you right?" from an open intake ask, and the park line is unseen until that ask closes. Outside the claim, a dry1 state. Fix: none in this frame. Note it for the dry1 read.
5. `rota/core/scheduler.py` 2057-2071, `park_untested`. Low. PLAUSIBLE. The ruling says "before any test existed for the batch's criteria", and the code reads exactly that. The ruling's reason is "a note has no row the seat can rule". A batch with one green criterion test and a give-up on the other two criteria also gives him no row, and keeps the note. Fix: ask Roman one question, with a recommended answer that a criterion with no test is a page row whenever the Tester gave up.

## (c) Probes

Directory: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/3b83d22b-0033-48d3-816a-f69a7fe15544/scratchpad/f330r2/`.

- `probe1_page.py`: copies dry1 to `dry1_p1.db`. Reads `given_up`, `quarantined_keys`, `park_rows`, `park_untested`, `park_ask`, `open_park_ask`, `park_ask_id`, the park messages and `park_message_rests`. Renders `_park_page(conn, "bg_1", rows)` and `_render_state`. The page as rendered:

```
This change stopped before it had any checks, because the team could not write the tests after 3 attempts.
You asked:
  1. Make click.pause() return True when it waited for a key and False when it skipped because stdin or stdout is not a terminal.
It must:
  2. When click.pause() skips execution because stdin or stdout is not a terminal (e.g., piped input), it must return False.
     check: no test yet.
  3. The return value depends on whether the current environment is a terminal, determined by checking stdin and stdout.
     check: no test yet.
  4. When click.pause() suspends execution awaiting a keypress from the user, it must return True.
     check: no test yet.
Reply 'ok' if every line says what you want. The team then stops here and tells you.
Name a line to correct only that line. Ask, if something here is unclear.
```

- `probe2_restart.py`: two copies, `dry1_p2.db` and `dry1_p3.db`. Deletes the rested note, because `park_ask` is empty while it rests. Runs the Liaison's present with `ScriptedBackend`, lands a reply, moves `tk_1_criteria_skipped` with `_lift_quarantines` as the tests do, reads the keys, `parked`, `next_batch`, `frontier`. Then sets the Tester's key at the cap again and reads `spent_park`, `preempt`, `park_ask_id` and `park_ask`.
- `probe3_landing.py`: two copies, `dry1_p2b.db` and `dry1_p3b.db`. Lands the rulings through the Liaison with `rulings.rule`. `revise` is no option of a criterion row, the vocabulary is approve, drop, rewrite, other. Reads `park_ruling`, the versions, the keys, `frontier` and `_render_state` before and after the intake ask closes.
- `probe4_readonly.py`: the night 168 fixture with `_dry1`, a held Architect wake at 2 attempts. Compares `frontier_readonly` with `frontier` and reads the row after.
- `probe7_pytest.txt`: `pytest -n0` over the eight files, then `test_l3_rulings.py` with a copy of `D:/repos/rota/tests/rota/cassettes.db` in the worktree. The copy was removed after, and `git status` is clean.

No model was called. The gate did not run. The worktree stands.

## (d) Usage

The harness shows no token counter to this agent. The review used about 28k tokens of context against the cap of 30k. Input about 24k, output about 4k.
