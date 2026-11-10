# Brief: the turns where the measured count moved, 2026-11-10

Written by session 1efd37b1 on frame 364, with three points of session
4a1d361a (frame 363). One read, one agent on Opus. The agent reads and
writes one page. It edits no other file, and it runs no git command that
writes.

## What you do

Write one page, `plans/method/moved-count-read-2026-11-10.md`, 230 lines
at most. Return ten lines: the count of moves, the count by grade, the
path, and what you could not find.

One turn of this project is: rota runs, the build session reads the run,
the build session changes rota, and rota runs again. Every read of today
looked at the problems of a turn. This read looks at the other half. In
which turns did a count that the runs measure move, and what changed
before each move?

## What the read asks, and what it does not ask

The read finds the moves of the counts and the changes before each move.
A change before a move is a candidate and not a cause. The records hold
no pair of equal runs with a fresh start, so the noise between two equal
runs is not measured. Do not write "caused". Write what the rows and the
commits show, and grade each candidate by the rule in part 4.

This brief holds no expected answer. If you form one while you read,
write it in a last section of your page, apart from the tables.

## The work

1. **The series.** For each night from 82 to 175, one row: batches,
   merged batches, sessions, sessions for each merged batch, batches
   that wait behind a stuck batch, the share of Developer sessions that
   commit, the sessions before the first batch starts, and the model
   time of the night if a row holds it. Count a session one time, at the
   night that started it. Give the dry runs 1 to 9 and blind run 1 as a
   second, short series.
2. **The moves.** Find the moves from the series, with one rule that you
   state before you apply it. A move is a level of a count that changes
   and stays for three nights or more. List the moves that hold. List
   apart the moves of one night that do not hold. Say plainly if a
   series only drifts and has no move.
3. **The conditions.** For each move, say whether the conditions of the
   run changed at that night. The conditions are: the requests (they
   changed at night 163), the seat (a script approved every page before
   night 133, and a model sat from night 133), the models at a desk, the
   start of the night (a fresh onboarding, a warm snapshot, a database
   that continues an earlier night), the length of the night, and the
   harness under `probes/`. A move at a change of conditions gets the
   grade "conditions changed".
4. **The changes before a move.** For each other move, take the three
   turns before it. List the commits to `rota/` and `probes/` in those
   turns, by kind:
   - a door or a refusal;
   - a prompt or a brief of a desk;
   - a cap or a limit;
   - other code of rota (name the part: scheduler, predicates,
     lifecycle, loop, harness of tests, other);
   - the harness or the measure of a run (`probes/`);
   - a rule or a record of the build session, with no code. This is its
     own kind and never joins a code kind.

   For each change, give its origin, one of three:
   - the answer to a wall that a read named. Column 6 of the list of
     turns holds only the frames that a read opened. A wall that a read
     matched to an older frame is not there. The subject of a commit
     carries "frame N" by convention, and the heading of the frame says
     what the frame answers;
   - a row of a sprint or a plan, or a message of Roman, for example "I
     want all the fixes in";
   - neither of the two.

   Keep the three groups apart in every table.

   Grade each candidate. The moved count is never the evidence for a
   grade.
   - "mechanism seen" needs three conditions, all by rows. First, the
     diff names a state, a kind of row, a text or a path of the code.
     Second, the rows show that exact thing after the change and not in
     the three nights before it, or the reverse. Third, the batches or
     the sessions that make the moved count pass through that thing, by
     their own rows. Quote the lines of the diff and the rows for each
     condition.
   - "change seen in the rows, link to the count not shown": the first
     two conditions hold and the third does not.
   - "timing only": the change is before the move, and no row shows its
     effect.
   - "conditions changed": part 3.
5. **The reverse view.** Take the ten largest changes to `rota/` by
   lines changed that are not the answer to a named wall, and the ten
   largest that are. For each, did a series move in the three turns
   after it? This view finds a change that moved nothing.
6. **The dry runs.** Three dry runs merged on 2026-11-02 and none
   after. Say what differs between those three and the later runs: the
   request, the repository, the commit of rota, the seat and the models.

## The sources

- The night databases, `D:/repos/rota/.rota/clickI_night*.db`, and the
  run databases by the paths in
  `plans/method/product-seat-population-2026-11-10.md`. The schema is
  `rota/core/schema.sql`.
- `plans/method/turns-list-2026-11-10.md`: column 1 (the commit, the
  requests and the models of each run), column 6 (the frames that a read
  produced) and column 7 (the changes by kind). Use these columns, and
  do not count again.
- `plans/method/product-stops-read-2026-11-10.md`: every batch that did
  not merge, by class, and the classes over the thirds of the nights.
  Its scripts are in
  `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\stops\`.
  Use its rule for "waits behind a stuck batch".
- `plans/method/product-model-read-2026-11-10.md`: the models by desk
  for each night, and the commit share of the Developer.
- `plans/method/product-break-read-2026-11-10.md`: the nights over
  time, by thirds.
- `git log` and `git show` on `rota/` and `probes/`. Read commands only.
- `plans/stack.md` and `plans/archive/stack-*.md` by pattern for one
  frame or one night. Most frames before 2026-10-30 are in the archive.
  Do not read a stack page whole.
- The three extract pages,
  `plans/method/turns-list-extract-{a,b,c}-2026-11-10.md`. They hold
  each cell of column 6 whole. The table of the list cuts a cell at
  about 300 characters.
- For the second origin of a change, the tables only of two pages:
  `plans/method/meta-above-frame-read-2026-11-10.md`, the rows of the
  sprints and the plans, and
  `plans/method/meta-direction-read-2026-11-10.md`, Roman's messages
  with their minutes. Use the rows. Do not use the readings of these
  pages.

## The limits that you must carry into the page

- A database opened with `mode=ro` still makes SQLite write a `-shm`
  file beside it. Open a database with `immutable=1` when no `-wal` file
  with bytes lies beside it. Otherwise copy the database with its
  `-wal` and `-shm` files to your scratch folder and open the copy.
- 68 batches of the nights share their first session with an earlier
  night. The nights share state, so a count of a night is not a fresh
  observation.
- The copy of the dry run 6 database is short by 12 sessions. Use the
  original file with its `-wal`.
- Nights 82 to 86 and dry run 1 have a commit "by date" only.
- A commit can lie in two ranges when a run started from a worktree.
- One reader and one pass. Say so at the top of the page.

## How you work

- Scratch folder:
  `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\moved\`.
  Write scripts there with the Write tool, not with a heredoc.
- Run no model, no night, no dry run, no gate and no rota command that
  wakes a desk. Use no GPU.
- You can start up to two sub-agents on Opus to extract a part, with a
  cap of 250k tokens each. Give each one these parts and these limits,
  word for word. You write the one page yourself.
- Do not read `plans/method/product-map-2026-11-10.md`,
  `plans/method/one-turn-2026-11-10.md` or a `plans/method/meta-*.md`
  page other than the two tables that the sources name. They hold
  readings, and this read must not copy one.
- Mark each claim (observed: where) or (reasoned).
- Write Simplified Technical English: one topic for each sentence, 25
  words at most, the active voice, the present tense, no idioms. Quotes,
  code and paths are copied exactly.
- Put the result first: the count of moves and the count of each grade.
- When a source does not open or a count does not add up, write that in
  the page. Do not repair a record.
- Do not write the context count or a token estimate in the page.
