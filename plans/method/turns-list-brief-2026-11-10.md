# Brief: the list of turns, 2026-11-10

Written by session 4a1d361a on frame 363, with the half of session
1efd37b1 (frame 364). One read, one agent on Opus. The agent reads and
writes one page. It edits no other file, and it runs no git command that
writes.

## What you do

Write one table of every turn of this project, to
`plans/method/turns-list-2026-11-10.md`. Return ten lines: the count of
turns, the counts of the columns, the path, and what you could not find.

One turn is: rota runs, the build session reads the run, the build
session changes rota or its own way of working, and rota runs again. The
unit is one run, or one block of nights on one commit of rota, with its
read page, the commits until the next run, and the next run.

The runs: dry runs 1 to 9 with their parts (6, 6b, 6c), blind run 1, and
nights 82 to 175 in blocks. Nights before 82 have no database. Take them
from the prose of `plans/archive/` only if a read page exists, and mark
them thin.

## What the list asks, and what it does not ask

The list counts what a turn met again, wall by wall. A wall is a problem
that a read of a run named.

The list does not ask whether a turn was good or bad. Equal nights, with
one set of models on the same three requests, merged 0 to 3. So one run
or two runs cannot show that a turn left the next turn better placed. Do
not rank the turns. Do not write a cause for a pattern. Write what the
records show for each cell, and write "not found" when they show
nothing.

This brief holds no expected answer. If you form one while you read,
write it in a last section of your page, apart from the table.

## The columns

For each turn, one row. Each cell names its source: a path with a line,
a commit, or a database with a query.

1. The run: its name, its dates, the commit of rota that it ran on, the
   requests and the models. Mark two runs as equal when the commit, the
   requests and the models are the same.
2. The question or the expectation that was written before the run, if
   any. Quote it, with the path and the time. "None" is an answer.
3. Where the goal of the run stood before it started: a page, a frame's
   line, a note, a message of Roman, or nowhere.
4. What the read named: each wall in one line, and the count. The path
   of the read page. The time between the end of the run and the read.
5. The first act of the build session after the read landed, and the
   minutes from the read to that act. An act is an edit, a commit, a
   frame pushed or an agent started.
6. The frames that the read produced, by number. For each: built before
   the next run, closed, put aside, or still open at the next run.
7. What the build session changed before the next run, by kind: a door
   or a refusal, a prompt or a brief of a seat, a cap or a limit, other
   code of rota, a tool of the build session, a rule or a memory text, a
   record only. Counts from `git log` between the two runs.
8. Which walls of this turn the next three runs met again, wall by wall.
   For each match say how you matched it: the same cause, the same sign
   at the same place, or not sure. A keyword match alone is "not sure".
9. Who judged the turn, and on what: Roman in his words, the session, or
   a count. Quote the line. Say what the judgement decided: the work
   continued, turned or stopped.
10. Roman's typed messages inside the turn: the count, and the count
    that corrects or turns the work.
11. The sessions that held the work inside the turn, and the hand-offs
    between them.

After the table, three short lists with no reading of yours: the turns
with no read page; the pairs of equal runs, with their results side by
side; the walls that came back three times or more, each with the turns
that met it.

## The sources

The rota side:

- The run databases, by the paths in
  `plans/method/product-seat-population-2026-11-10.md`.
- The read pages of the runs, `plans/*read*.md`, and `plans/dry9/`,
  `plans/dry-blind1/`.
- `git log` on `rota/` between two runs.
- Two reads that already count a part. Use their counts, and do not
  count again: `plans/method/product-stops-read-2026-11-10.md`, every
  batch that did not merge, by class; and
  `plans/method/product-doors-read-2026-11-10.md`, the origin commit of
  40 doors.
- `plans/wall-guide.md`, the known causes of walls. Use its names for a
  wall where they fit.

The meta side:

- `plans/stack.md` and `plans/archive/`: the frames, their status lines
  and their dates. A status line carries its minute.
- `plans/meta-review-2026-11-10.md`: the 16 walls of dry run 8 and their
  repeats. Check its count, and do not copy it.
- `plans/method/meta-above-frame-read-2026-11-10.md`: the sprints and
  the plans, and how each one ended.
- `plans/method/meta-direction-read-2026-11-10.md`: Roman's messages
  that turn the work, from 2026-10-11, with their minutes.
- The transcripts, `C:\Users\roman\.claude\projects\d--repos-rota\`,
  only where a status line does not give a time or his words.
- `python rota/tools/handover.py peers` for the hand-offs, and the notes
  `plans/method/handoff-*.md` and `plans/handoff-*.md`.

Ask the map tool before you grep the code:
`python -m rota.tools.map fn|table|mode|file <name>`.

## The limits that you must carry into the page

- 68 batches of the nights share their first session with an earlier
  night. Count a session one time, at the night that started it.
- The copy of the dry run 6 database is short by 12 sessions. Use the
  original file.
- The nights share state, so a count of a night is not a fresh
  observation.
- "Done" and "not seen again" were soft counts in earlier reads. A frame
  can be done and never closed, and a wall can return under a new name.
  Mark each such cell "not sure", and do not force a class.
- One reader and one pass. Say so at the top of the page.

## How you work

- You can start up to three sub-agents on Opus to extract one group of
  runs each, with a cap of 250k tokens each. Give each one these columns
  and these limits, word for word. Wait for them in the foreground. You
  write the one table yourself, and you use one way to name a wall
  across all groups. Report the usage of each sub-agent.
- Write the page in short plain sentences, with the result first: the
  count of turns and the count of each column at the top.
- When a source does not open or a count does not add up, write that in
  the page. Do not repair a record.
- Do not write the context count or a token estimate in the page.
