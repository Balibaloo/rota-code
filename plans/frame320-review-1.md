# Frame 320, review 1: commit 41bde21f in `C:/Users/roman/rota_p320`

Verdict: does not stand. The retry and the bound work, and frame 267 is intact.
Two paths still end a request in quiet. A resend through the reply route gets no retry.
A session that writes only a glossary row or a note closes the request with nothing sent.

## (a) The verdict on each point

1. Holds as a mechanism. The line is not plain enough to act on (finding 3).
2. The rule must read "no statement, no page and no message". The probe confirms a quiet close (finding 2).
3. He sees the line, but his reply to it loses the retry. The line is a half dead end (finding 1).
4. Yes. `_bind_send` holds `ctx`, and `api._wake_mode_tools(ctx)` gives the mode's ops (finding 4).
5. Unchanged. 143 tests in `test_runner.py` and the frame 320 file pass, frame 267's 12 among them.
6. Bounded. A third wake does not occur, and no loop exists.
7. No case goes stale. 43 Liaison and G1 cases pass on the register. The 2 reds are red on the parent too.

## (b) Findings

1. `rota/core/db.py:816`, `_request_missed`, high. CONFIRMED.
   The rule needs `not trig["cause_id"]`. The line tells him "Send the request again".
   `rota agenda` offers "reply with: rota sign ... --say", and the walk's `answer_replies` replies the same way.
   Either route makes a principal `converse` caused by the Liaison line.
   Probe P3: one barren session on that reply left it `answered`, with no note and 0 lines to him.
   This is the night's shape again, one step later. The implementer's open question 1 names it.
   Fix: admit a cause that is not a page, or a cause that is a Liaison line to the principal, in `_request_missed`.

2. `rota/core/db.py:816`, `_request_missed`, high. CONFIRMED.
   The rule reads `not result.writes`, so any write cancels the miss.
   Probe P2: a first session with one `glossary_terms` write and the s145 refusal ended `answered`, with no note and no line.
   The implementer's reason is a double intake on retry. A glossary row or a note does not intake.
   Fix: count only the writes that land a request, `statements` and `items`, and keep every other write out of the test.

3. `rota/core/db.py:820`, `unread_line`, medium. CONFIRMED.
   The line for s145 reads: "The team could not read your request, and it did not reach the work. The last try stopped on this: 'in get app dir on windows when appdata ...' is your own sentence, pasted back to you. Send the request again in other words."
   Nothing reached him, because the door refused the paste. The line says the team pasted his words back.
   "Could not read" is false. The Liaison read the request and asked the wrong question.
   The line asks him to rephrase a request that was clear. The fault is the seat's route, not his words.
   Fix: say what happened in his terms: "The team tried to ask you about it, and the ask was refused." Drop the refusal quote.

4. `rota/core/sandbox.py:3244`, the paste door, medium. CONFIRMED by reading.
   The refusal names `brief.segment` in every mode that holds `msg.clarify_principal`.
   Four Liaison modes lack `brief.segment`: contradiction, report, round_close and unresolved (report section d).
   `_note_routes` in `rota/roles/api.py:20185` reads `_wake_mode_tools(ctx)` for the same reason. `_bind_send` holds `ctx`.
   Fix: add the segment sentence only when `"brief.segment" in api._wake_mode_tools(ctx)`.

5. `rota/core/db.py:1158` with `_why_no_ruling`, low. CONFIRMED.
   A request session with no refusal gets the note "the session wrote no ruling and sent nothing".
   He sees: "The last try stopped on this: the session wrote no ruling and sent nothing."
   A request owes no ruling, and "the session" is a seat word. The second wake's head carries the same note.
   Fix: give a request miss its own note, for example "the session landed nothing and sent nothing".

6. `rota/cli.py:749`, low, PLAUSIBLE. Outside the points.
   `rota agenda` prints the line under "said to you (no answer needed, but you can reply)".
   The line asks him to act, so the heading contradicts the line.
   The TUI `show_replies` marks the line answered when it shows it, so the line shows once.
   Fix: let a line caused by a closed request print under its own heading, or accept the heading and note it.

## (c) Probes

All probe files are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a0790d20-6463-44cf-97ca-89e1ddd75c84/scratchpad/f320r1/`.

- `probe_p2p3p6.py`: P2 commits a glossary-only miss at attempts 1. P3 sends the line, replies through `scenes.answer_replies`, and commits one barren session on the reply. P6 runs s145's turn 1 through `run_session` three times.
  P6: run 0 left m_p2 open, run 1 closed it and sent 1 line, run 2 found m_p2 answered.
- `python -c` on `unread_line(_why_no_ruling(empty result))`, for finding 5.
- `pytest tests/rota/test_runner.py tests/rota/test_frame320_request_miss.py` in the worktree: 143 passed.
- The gate in the worktree: 6 failed, 4669 passed, 207 skipped. The register is absent there, so no case replayed.
  The gate stored the ignored file `.rota-gate.json` in the worktree, because no baseline existed. I did not pass `--baseline`.
- `parent/`: `git archive 41bde21f^`. The gate's 6 reds are red on the parent too.
- `head/` and `parent/` each hold a copy of the main register. `test_l1.py -k "LI or G1"` on `head/`: 43 passed, 2 failed, 1 skipped.
  The 2 reds, `L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question` and `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time`, fail on `parent/` too. No STALE line printed.

## (d) Usage

About 56k tokens of context, about 9k output, about 65k total. The cap was about 20k. The gate and the case replays took most of the excess.

## Re-check of db4d2da2

Verdict: does not stand. Findings 1 to 6 are closed. The fix for finding 1 opens two new paths.

### The verdict on each finding

1. Closed. Probe P3: one empty session on his reply leaves the reply open with the note.
2. Closed. Probe P2: a glossary-only first miss leaves m_p2 open with the note.
3. Closed. His line, once: "Your request did not reach the team. The team tried to ask you about it, and the ask was refused: the question is your own sentence, pasted back to you. Reply to this line to send it again."
   He can act on the line. "Pasted back to you" still describes an ask that never reached him, but the clause before it says so.
4. Closed. `sandbox.py:3243` adds the route only when `api._wake_mode_tools(ctx)` holds `brief.segment`.
5. Closed. `REQUEST_NOTHING` at `db.py:839` gives a request its own note.
6. Closed. `cli.py:743` prints the line under "not reached the team (reply to send the request again)".

### New findings

7. `db.py:828`, `_request_missed`, high. CONFIRMED.
   The walk's `answer_replies` replies to every Liaison line, the line of `unread_line` among them.
   The reply is a request again, so two empty sessions send a new line, and the walk replies again.
   Probe LOOP: 4 cycles of a request that never lands each ended with 1 new line to him. Nothing ends the chain.
   Each cycle costs two sessions. Before db4d2da2 the chain ended after one quiet session.
   Fix: when the cause is itself a line of `unread_line`, close the second miss with the note and send no new line.

8. `db.py:828`, `_request_missed`, medium. CONFIRMED.
   The rule accepts a reply to any Liaison chat line, not only to the line of `unread_line`.
   Probe THANKS: he answers "Noted, I filed it." with a reply, and the Liaison sends nothing back twice.
   He then gets "Your request did not reach the team. The team tried twice and landed nothing."
   Chat is not work, so the line is a false alarm.
   Fix: accept a Liaison line as the cause only when its body starts with `UNREAD_HEAD`.

### Counts

- `test_runner.py` with `test_frame320_request_miss.py` in the worktree: 149 passed.
- `test_l1.py -k "LI or G1"` on a `git archive db4d2da2` copy with the register: 43 passed, 2 failed, 1 skipped.
  The 2 reds are the same as on the parent. No STALE line printed.

### Probes

- `f320r1/probe_recheck.py` imports `probe_p2p3p6.py` and runs P2, P3 and P6 again. It then runs LOOP and THANKS through `session_commit` and `scenes.answer_replies`.
- `f320r1/head2/` is `git archive db4d2da2` with a copy of the main register.

### Usage

The re-check used about 10k input and 3k output, about 13k total.

## Re-check of 07b3bf0c

Verdict: stands, with one low finding. Findings 7 and 8 are closed.

- Finding 7 closed. Probe LOOP: he gets 1 line for a request that never lands. The walk's resend misses twice and closes with its note. No message stays open.
- Finding 8 closed. Probe THANKS: an empty session on a reply to an ordinary chat line sends him no line. `_request_missed` at `db.py:829` accepts only a cause whose body starts with `UNREAD_HEAD`.
- Counts: `test_runner.py` with `test_frame320_request_miss.py`: 151 passed.

### New finding

9. `db.py:1242`, low. CONFIRMED by reading and probe.
   The resend closes as `answered` with its note, and no line follows it.
   The only reader of a note in front of him is `principal.py:1534`, and it reads open pages to him only.
   `rota agenda`, the cockpit and the pages show no closed request. The note is visible in the database only.
   He saw one line already, so the chain does not stop in silence. A second miss on his resend is invisible to him.
   Fix: let `rota agenda` list a closed resend with its note under "not reached the team", or accept the gap and record it.

### Probes

- `f320r1/probe_recheck.py` runs LOOP and THANKS again.
- A stdin probe builds the LOOP end state, then lists the messages that are not answered (none) and the resend's status and note.

### Usage

About 5k input and 1.5k output, about 6.5k total.
