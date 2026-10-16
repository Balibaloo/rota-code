# Frame 267, review 1: a reply that lands no ruling, commit 0582873a

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_review_267` at 0582873a (2026-10-16).
Verdict: pass 1b for one high. The high is a small change in `_why_no_ruling`.
Counts: 1 high, 5 low. 4 findings are CONFIRMED by a probe or a read, and 2 are PLAUSIBLE.

## (a) Verdicts

1. Condition: holds. No right result in the shapes tried stays open. Night 151 keeps m108 and m178 open, and both are right (observed: probe 1).
2. Second wake: the line is on the second session only. The prompts differ by that one line. The line carries no fact the seat lacked (findings 1, 2 and 3).
3. Returned page: the top line says "the team", names line 11, and holds no id, tool or refusal text. It shows in the landing wake too. Keep it there (observed: probe 1).
4. attempts: no reply stays open forever. A reply gets at most two barren commits and at most three dispatches (reasoned: section 4).
5. The ask: `pending_asks` renders it once, the agenda tick stays blocked as before, and no predicate misreads the note (observed: probe 1, grep).
6. Tests: the red reasons hold only in the pass's stubbed copy. The replay is synthetic. No existing assertion changes (findings 4 and 5).
7. Drivers: both answer a returned page once and only once. Nothing caps the number of returns (finding 6).

## (b) Findings

1. `rota/core/db.py:730-737`, `_why_no_ruling`. High. CONFIRMED.
   The function takes the last refusal before any error. For m108 it picks a refusal that the seat already fixed.
   Probe 3 replayed the six real completions of s226 on m108. The note became "rulings.rule: lines 1, 5 have no ruling...".
   The seat added lines 1 and 5 at turn 2. Turns 2 to 6 then failed on the parse error "unterminated argument list ... The string `"approve}` has no cl...".
   So the second wake on m108 names a fixed fault and hides the live one. m108 is one of the two instances that the frame names.
   The implementer followed design 5.1 literally. The pass report asks this question in its (d) 2.
   Fix: take the last line of `result.errors` that is not the end line of the repeat door, and use `result.refusals` only when `errors` is empty.

2. `rota/core/runner.py:2386-2412`, `_missed_reply_line`. Low. PLAUSIBLE.
   For s336 the line repeats a refusal that the seat saw as a tool result at turns 2 and 3 of the first session (observed: night 151, the account of s336).
   The seat repeated its call verbatim against that text. At temperature zero, one added line can change the calls, but it adds no new fact (reasoned).
   The night counts whether the second session lands a ruling. If none lands, the cost is one session for each miss.
   Fix: none in this pass. If the night shows no ruling from a second session, state the action in plain words, for example that a question is `ask` with no `rulings`.

3. `rota/core/runner.py:2411`. Low. CONFIRMED by a read.
   The line says "Its last refusal:" also when the note is a runner error or the default sentence "the session wrote no ruling and sent nothing".
   Fix: write "It ended on:", or choose the word from the source of the note.

4. `tests/rota/test_runner.py`, `test_s336s_end_through_the_runner_keeps_then_returns_the_page`. Low. CONFIRMED.
   The test scripts `rulings.rule(rulings={"1": "ask"}, ...)` on a one-line page. It does not replay the real completion of s336.
   Probe 1 replayed the real turn 1 completion of s336 through `run_session` on a night 151 copy. Each run ended on the repeat door after 3 calls.
   The first run kept m178 open with the note. The second run closed m178 and returned m177. So the behaviour holds for the real completion.
   Fix: optional. Seed the test with the turn 1 text of s336, or accept the synthetic call.

5. `tests/rota/test_runner.py:1760-1768`, `_commit_reply_session`. Low. CONFIRMED.
   At HEAD~1 unmodified, four runner tests fail with `TypeError: SessionResult.__init__() got an unexpected keyword argument 'errors'`.
   The four include the two "as before" tests, which design 5.4 item 3 says are green at HEAD (observed: probe 4).
   The pass proved the behaviour reds in a copy where it removed `errors=` and stubbed `_missed_reply_line`. The method is sound, but no record keeps the copy.
   The replay test and the driver test fail at HEAD~1 for the reason of the design (observed: probe 4, `'answered' == 'open'` and the missing top line).
   Fix: pass `errors=` only in the tests that need the fallback, so the "as before" tests run unchanged at HEAD~1.

6. `rota/core/db.py:1013-1020` and `probes/agent_principal.py:37-48`. Low. PLAUSIBLE.
   Each second miss writes a new note with a new reply id, so the driver key is new and the driver answers again.
   A page that the Liaison cannot land loops: one reply, two sessions, one return, then one more reply. Only the step cap of the walk ends the loop (reasoned).
   This is the loop shape of the night stop rule, on one page.
   Fix: count the returns of a page, for example the principal replies whose cause is the page, and stop the return after the second one.

## Section 1. The condition (point 1)

Shapes tried. Each shape is placed by its code path (reasoned: reads of `landing.md`, `rulings_rule`, `parse_reply`, `land` and `_mode_key`):

- An ask-back through `rulings.rule(ask=...)`: a message to the principal. Excluded.
- A ruling, the empty ruling on a touch note included: a `rulings` write. Excluded.
- `drop`, `later` or `now` on the order page: `rulings.rule`, a `rulings` write. Excluded.
- A park page reply: landing mode, `rulings.rule`, and the relay of the door. Excluded.
- A reply to a plain clarify, in `answering` or `converse` mode, the m28 shape: `parse_reply` gives `converse`, and `land` closes the clarify. The page is not open at commit. Not matched.
- A reply that only closes an ask: landing mode has one function, `rulings.rule`. No seat op closes a page. The page closes in `apply_rulings` after the commit.
- A reply on a page that another reply already ruled, or on a superseded page: the page is not open. Not matched.
- A suspended session: `result.checkpoint` is set. Excluded.
- A reply the seat answers by another write: landing offers no other write. `stage_park_relay` adds only a relay beside a ruling.

Result: none in these shapes.

Night 151 holds 29 principal `converse` replies with a page cause, not 25 (observed: the first query of probe 1).

- 21 replies staged a `rulings` row. The branch answers them as before.
- m12 (s96) sent an ask-back. The branch answers it as before.
- 5 park clarify replies (m54, m98, m132, m143, m170) staged a ruling. The branch answers them as before.
- m28 (s112) replied to a plain clarify, which `land` closed. The session also sent `msg.confirm_principal`. The branch answers it as before.
- m108 (s226) and m178 (s336) staged nothing and sent nothing, with the page open. The branch keeps both open. Both are right: the batch of m108 merged without the correction, and m177 waited with no wake (the read of the frame).

## Section 2. The second wake (point 2)

The line as rendered on the second wake of m178 (observed: probe 1, the unified diff of the two user prompts):

```
A session on this reply ended with no ruling. Its last refusal: rulings.rule: line 11: 'ask' is a question back, and a question is its own call: rulings.rule(ask="<one sentence about line 11>") with no rulings.
```

- First session: the line is absent. The note is null before the first commit (observed: probe 1).
- Other wake kinds: absent. The query needs `wake.detail = 'converse'`, an open principal reply and a note. Only the new branch writes a note on an open principal reply (observed: grep of the `unresolved_note` writers, 2026-10-16).
- The system text is identical in both sessions. The user text differs by that one line only (observed: probe 1).
- Judgement: see findings 1, 2 and 3. For m108 the line names the wrong fault.

## Section 3. The returned page (point 3)

The top line for m177 after the refusal of s336 (observed: probe 1, `pending_asks`):

```
Your last answer to this page did not reach the team. The team could not turn your words about line 11 into a ruling. Answer the page again, and say for each line you want changed what to do with it.
```

The line says "the team" and names line 11. It holds no identifier, no tool name and no refusal text.
The second line of the page is the old first line, "Here is what I understand you want, on one page."
The line shows in the landing wake of a third reply, at the start of `landing.page` (observed: probe 1, the reply m9178).
Judgement: keep the line in the landing wake. The seat reads the page as the principal saw it, and `order` does not move.

## Section 4. attempts (point 4)

- `run_session` raises `attempts` at dispatch, before the commit (observed: runner.py:3598). `after_landing` is the only caller of `session_commit` that passes a trigger. `land_and_step` in scenes passes no `trigger_msg` (observed: the map, scenes.py:1476).
- So `attempts = 0` at commit is reachable only by a direct test call. A seeded 0 becomes 1 at the first dispatch. No reply stays open forever (reasoned).
- A failed, uncommitted dispatch also counts. Fail then barren returns the page after one barren session. Barren, fail, barren returns it at the third dispatch.
- `message_attempt_cap` is 3. A third failure quarantines the reply, and the page then waits with no note. That stuck state existed before this commit (reasoned: boot.py:173-190).
- Result: two barren commits at most, and three dispatches at most.

## Section 5. The ask after the second miss (point 5)

- `pending_asks` holds m177 once (observed: probe 1, count 1).
- `tick_agenda` returns nothing while a page is open. m177 was open before this commit too, so nothing changes (reasoned: design 5.3).
- `predicates.unresolved` and the criterion repair predicate read `status = 'unresolved'` only (observed: predicates.py:1131 and 1299).
- `nightreport` prints `unresolved_note` before `body_text` for an open message. The night report then shows the reason for m177 and for a kept reply. This helps a reader and is not a misread (observed: nightreport.py:482).
- No other reader of `unresolved_note` reads a message to the principal (observed: grep, 2026-10-16).

## Section 6. The tests (point 6)

- Red at HEAD~1: see finding 5. Probe 4 ran the new test files on a `git archive` of HEAD~1.
- The replay: see finding 4. Probe 1 replays the real completion, and the behaviour holds.
- Existing assertions: the commit adds lines to the two test files and removes none (observed: `git show 0582873a -- tests/`).
- At HEAD the new tests pass, 9 selected (observed: probe 5).
- The gate at HEAD: `8 failed, 1 passed`, then `exit 1: 9 new reds, 1 of them flaky`. These are the 8 reds that the pass report lists (observed: probe 6).
- Two of the 8 reds fail also at HEAD~1: `test_a_session_with_no_batch_reads_the_root` and the `test_templates.py` scene (observed: probe 7). So these two are not reds of this commit.
- Probe 6 piped the gate through `tail`, so the five summary lines and the stale line are lost. The holding session must read the stale line from its own gate run.

## Section 7. The probe drivers (point 7)

- `agent_principal.py`: `respond` keys `replied` on `page_key`. The returned page is a new key, and the driver answers it once more. A third visit returns None (observed: `test_a_returned_page_is_answered_once_more_and_no_more`, green).
- `walk.py`: the two once-guards of the script principal and the pending-asks filter key on `page_key`. The import from `agent_principal` resolves, because `walk.py` already imports `progress` from `probes/` (reasoned: walk.py:34 and 67).
- Both drivers answer each returned page once. Nothing caps the number of returns (finding 6).
- Outside the points: `walk.py:118` reads line 1 of a clarify page as the question. On a returned park page, line 1 is the old first line, so only the log line moves. Low, and no fix is needed.

## (c) Probes

All probes ran on 2026-10-16. The scripts are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f267rev/`.

1. `probe_s336.py`: backs up `clickI_night151.db` through the read-only URI to `n151.db`. It reopens m178 and m177 and replays the turn 1 completion of s336 twice through `run_session` with a `ScriptedBackend`. It diffs the two prompts, renders `pending_asks`, and runs the landing wake of a third reply. An inline query listed the 29 replies and their sessions on the read-only night database.
2. Not used.
3. `probe_s226.py`: backs up the night to `n151b.db`, rolls back m108, m107, m120 and their rulings, and replays turns 1 to 6 of s226 on m108.
4. `prev/`: a `git archive` of 0582873a~1 with the two new test files copied in. It ran `pytest -k` on the new tests.
5. `pytest tests/rota/test_runner.py tests/rota/test_agent_principal.py -k ...` in the worktree: 9 passed.
6. `python -m rota.tools.gate` in the worktree, piped through `tail -8`.
7. `prev/`: `pytest` on `test_a_session_with_no_batch_reads_the_root` and the `test_templates.py` scene at HEAD~1: both failed.

## (d) Usage

The harness line holds the true figure. Estimate: about 95k input and 15k output, about 110k in total. No sub-agent ran.
