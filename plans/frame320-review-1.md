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
