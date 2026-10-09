# Momentum note of session 7d45e193, peer name rota-68

Message rota-68 for a context question before you ask Roman. The session
stays open until Roman closes the window. Facts are in `plans/stack.md`,
frame 142, and in `plans/frame142-design.md` and `plans/frame142-pass1.md`,
sections "Pass 2" to "Pass 2f". The previous note, `plans/handoff-acb1f403.md`,
holds the altitude reading and the rulings of 2026-10-08; it still stands.
This page holds the judgement of this session, 2026-10-09 02:20 to the hand-off.

## What this session did

- Took frame 142 at 6e4b1d3f with night 134 running. Night 134 was void: the
  launcher pinned `CLAUDE_BIN` to an extension directory that had moved. The
  sign is a register line in `plans/operating-facts.md`, Running rota.
- Passes 2b to 2f on one implementer, resumed by message each time, 263.1k
  cumulative: 137.4k cold, then 44.1k, 18.0k, 46.6k and 17.0k. A resumed pass
  costs a sixth of a cold one. One delta review after each pass, all on Opus.
- Night 135 at 55fe8a04 found two loops in onboarding and walk 1, read while
  it ran: the `brief.segment` on-file refusal sent the Liaison to ask the
  principal about row s1, and no door refused a Liaison question the
  principal had answered; and a self-relay with no entry staged a
  `span_entry` that named no entry, which killed three sessions at commit.
  Both are fixed in passes 2e and 2f. I stopped the night in walk 2 on a
  quarantine loop; its database is `.rota/clickI_night135.db`, a mid-run copy,
  268 sessions. Frames 187 and 188 are its other two walls.
- Night 136 at 40691aa7, cold, the agent principal on Opus, launched 06:27 as
  the frame's walk. Launcher `.rota/launch_night136.sh`, log
  `.rota/night136.log`. Its watcher dies with this session, so arm your own:
  `python -I <your scratchpad>/watch_night.py .rota/night136.log 6900` in the
  background with a 7200000 timeout; the script is in this session's
  scratchpad, `watch_night.py`, and polls the log for `CYCLE`, `quarantin`
  and `GAUNTLET-DONE`.

## What I believe and why

- The frame's three doors now hold on every night row the reviews probed,
  nine in ten. What I do not know is what the walk does with the park page
  on bg_2, because no night has reached it since pass 1: night 134 was void
  and night 135 stopped in walk 2. Night 136 is the first measure.
- The residue rule will decide the close. Night 135's residue, the
  principal's words landing nowhere, had this frame's own door as its cause,
  so the frame did not close. On night 136, read the three ratios first, then
  every session where the principal's words drew no row and no ruling.
- The altitude reading of the previous note gained weight: night 135's
  onboarding ended at the step cap with the agent refusing every page whose
  lines were the system's own notes, and walk 1 merged nothing because the
  Liaison's own question became a line on the page. Frame 45 is still the
  nearest heading. Put the re-batch to Roman after this frame closes.

## What to doubt first

- The medium of the last review: the question check in `brief_segment` reads
  the span before the move. A wrong span that lands on a question is refused
  as a question with the wrong step. Not on the walk's path as far as the
  rows show, but the first segment refusal on night 136 is the place to look.
- The answered-question door keys on the words alone across the whole night.
  A generic question asked again in a new context is refused. The reviewer
  found no false positive on three nights; count them on night 136.
- `earlier_exchange` goes one level deep and has no size bound. On a loop it
  grows the page view each round.
- The gate's `test_handover.py::test_a_newer_watcher_retires_the_older_one`
  went red once on pass 2e's gate and green on every other run. A thread race
  on a 50 ms sleep. Not a frame unless it recurs.

## Live agents and their notes

- Implementer of frame 142, Opus, at 263.1k after pass 2f. Resume it for one
  more small pass at most, or take a fresh one from `plans/frame142-pass1.md`.
  Its id is in this session only; a fresh agent reads the note.
- The review and diagnosis probes are in this session's scratchpad:
  `r142p2e/`, `r142p2f/`, `n135live/`, `n135fk/`.

## Next, in order

1. Read a CYCLE line of night 136 at once, as the rules say. Expect a park
   page on bg_2 when its own tests go red, and no chat session anywhere.
2. At `GAUNTLET-DONE`: copy the database and `.rota/clickI.principal.jsonl`
   to `_night136` names. One read on Opus, shaped on
   `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/acb1f403-fab6-4e1b-89ba-a879c1ae39ab/scratchpad/n133_brief.md`,
   with frame 142's three ratios first, then the residue sessions, then the
   answered-question door's refusals and the segment door's refusals by
   count, then frame 182's read as Roman ordered on 2026-10-08. Cap 220k.
3. Close frame 142 on the three-part rule, or push the residue's cause as a
   frame. Write the actual beside the estimate in the closing status; the
   numbers so far are in the status of 2026-10-09 02:20 and after.
4. Then the re-batch question to Roman, frame 45 nearest, before frames 184
   to 188 get work. Frames 187 and 188 are unpriced.
