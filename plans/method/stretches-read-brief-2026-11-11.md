# Brief: the stretches where an order stood, 2026-11-11

Written by session 4a1d361a on frame 363. One read, one agent on Opus.
The agent reads and writes one page. It edits no other file, and it runs
no git command that writes.

## What you do

The build session of this project works under orders above a frame: a
sprint with rows, a plan, a list. For each such order, write how long
the work followed it, how much Roman had to say while it stood, and
what ended it. Write to `plans/method/stretches-read-2026-11-11.md`,
230 lines at most. Return ten lines: the counts of the cells, the path,
and what you could not find.

Roman is the Principal of the build session. He types messages to the
sessions. Some of his messages correct or turn the work.

## What the read asks, and what it does not ask

The read asks what the records show for each order: its start, its end,
the work inside it, and Roman's messages inside it.

The read does not ask whether an order was good. Do not rank the
orders. Do not write a cause for a pattern. Write what the records show
for each cell, with its source, and write "not found" when they show
nothing. This brief holds no expected answer. If you form one while you
read, write it in a last section of your page, apart from the tables.

## The unit

One order above a frame, from the time it was written to the time the
next order replaced it or the work left it. Take the units from
`plans/method/meta-above-frame-read-2026-11-10.md`: every sprint and
every plan of its list, by its name and its lines. Do not find the
units again. If that page and the stack disagree on a start or an end,
write both.

## The cells, for each order

1. The order: its name, where it stands (path and lines), who wrote it,
   and on what: a message of Roman (quote it), a read of a run, or the
   session's own choice.
2. Its start and its end, to the minute where a status line or a commit
   gives one. The length in hours.
3. Its rows: the count, and what a row is (a frame, a fix, a read, a
   run).
4. Its measure: does the order name a count or a result that says when
   it is done or whether it worked? Quote it. Is that measure the count
   of one fix at one place, the count of a run as a whole, or a thing
   about the destination or a capability?
5. The work inside the stretch: the frames that the sessions worked on,
   from the status lines by their time. How many are rows of the order,
   and how many are not. For the frames that are not rows: where each
   one came from (a read of a run, a message of Roman, another source).
6. The rows at the end: built, closed, carried to the next order by
   name, or dropped with no word. Use the counts of the above-frame
   read, and do not count again.
7. Roman's typed messages inside the stretch: the count, and the count
   that corrects or turns the work, with the rate for each day of the
   stretch. Give the first words of each one that corrects or turns.
8. What ended the order: a message of Roman (quote it), the read of a
   run, a rule of the method, a hand-off or a context line, or nothing
   that the records name.
9. The runs inside the stretch: the nights and the dry runs by name.
   Take them from column 1 of `plans/method/turns-list-2026-11-10.md`.
10. The sessions that held the work inside the stretch, and the count
    of hand-offs.

After the cells, three plain tables with no reading of yours: one row
for each order with cells 2, 3, 4 in three words, 5 as two counts, 7 as
two counts and a rate, and 8 in three words; the orders sorted by the
rate of cell 7; and the list of Roman's messages that ended an order.

## The sources

- `plans/method/meta-above-frame-read-2026-11-10.md`: the 114 units
  above a frame and how each one ended.
- `plans/stack.md` and `plans/archive/`, for the sprint sections, the
  plans and the status lines. Search them. Do not read `plans/stack.md`
  whole in one call.
- Roman's typed messages with their times: the list `typed.txt` in
  `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\b49d24d2-*\scratchpad\direction\`
  if it is still there, and
  `plans/method/meta-direction-read-2026-11-10.md` for the messages
  that correct or turn the work. If `typed.txt` is gone, build the list
  again from the transcripts in
  `C:\Users\roman\.claude\projects\d--repos-rota\`: a line with
  `"type":"user"` and `"origin":{"kind":"human"}`.
- `plans/method/turns-list-2026-11-10.md`, columns 1, 9, 10 and 11, and
  its three extract pages for a whole cell. Do not read its table whole
  in one call.
- `git log`, read commands only.

## The limits that you must carry into the page

- The transcripts start on 2026-10-10 19:23. Roman's messages before
  that time are not in the records. An order that stood before that
  time gets "not found" in cell 7, and never 0.
- Roman corrects what he sees. A stretch with few messages can be a
  stretch where he was away. Where the records show that he was present
  or away, say so: a message of his on another matter, a ruling, a
  dialog answer.
- A status line is the session's own account, true and often too sure.
- The above-frame read had one reader, and its "done" count is soft.
- One reader and one pass. Say so at the top of the page.
- Open no database. Run no gate, no test, no model and no rota command.

## How you work

- You can start up to two sub-agents on Opus, each for a part of the
  orders. Each one must stop at 250k tokens and return what it has. Give
  each one the cells and the limits of this brief, word for word. Each
  writes to `plans/method/stretches-read-extract-<part>-2026-11-11.md`
  and nowhere else. Wait for them in the foreground. You write the one
  page.
- Helper scripts go in the scratchpad of your session, written with the
  Write tool, and never in the repository.
- Write short plain sentences, with the result first: the count of
  orders, and the counts of cells 4, 7 and 8 at the top.
- When a source does not open or a count does not add up, write that in
  the page. Do not repair a record.
- Do not write the context count or a token estimate in the page.
