# Brief: the judges that are not Roman, 2026-11-10

Written by session 4a1d361a on frame 363. One read, one agent on Opus.
The agent reads and writes one page. It edits no other file, and it runs
no git command that writes.

## What you do

The build session of this project uses judges that are not Roman: a
review of a diff by an agent, a review of a design by an agent, the test
gate, and from 2026-11-10 a second view of one session on the page or
the brief of another session. Write what each kind of judge finds, at
which scale, and what the session then does with the finding. Write to
`plans/method/judges-read-2026-11-10.md`, 250 lines at most. Return ten
lines: the counts of the cells, the path, and what you could not find.

## What the read asks, and what it does not ask

The read asks what the records show for each review: its findings, the
scale of each finding, and the next act on each finding.

The read does not ask whether a review was good. Do not rank the
judges. Do not write a cause for a pattern. Write what the records show
for each cell, with its source, and write "not found" when they show
nothing. This brief holds no expected answer. If you form one while you
read, write it in a last section of your page, apart from the tables.

## The sample

- `plans/` holds about 359 pages with "review" in the name. List them
  with their dates. Draw 40 with Python's `random.Random(363).sample`
  over the sorted list of paths. Write the list and the draw in the
  page.
- Add every review of a design or of a rule, by name or by first lines,
  that the draw did not take, up to 15.
- Add the second views between sessions of 2026-11-10. They are in the
  status lines of frames 363 and 364 of that day in `plans/stack.md`
  (search for "second view", "check of session" and "compare"), and in
  `plans/method/product-map-2026-11-10.md` and
  `plans/method/boundary-synthesis-2026-11-10.md` by the same words.
- For the gate, take the status lines that hold "new red" or "0 new
  reds" on the frames of the 40 drawn reviews. Do not run the gate.

## The cells, for each review

1. The review: its path, its date, the frame and the pass, the kind of
   judge, and who or what asked for it: a rule of the method, a message
   of Roman, or the session's own choice. Quote the line.
2. What the judge was given: the diff, the brief, the frame's line, the
   goal of the frame, the destination. Take this from the review page
   and from the status line that starts the review.
3. The findings: the count, and for each finding one mark of scale:
   - a line or a value;
   - a function or a file;
   - the approach of the pass;
   - the size or the question of the frame;
   - the direction above the frame: the plan, the order, a capability,
     or the destination.
   When a finding does not fit, write it in words and do not force it.
4. The verdict of the review, in its words.
5. The next act on each finding, from the status lines of the frame and
   from `git log` after the review: repaired in the next pass, named as
   owed, set aside with a reason, set aside with no reason, or no
   record.
6. For a finding at the scale of the frame or above: quote it, and
   quote the session's next line about it.
7. After the frame closed: does a later record name a fault at the same
   place that the review did not name? Search the stack and its
   archives for the file and the function. "Not sure" is an answer, and
   "not searched" is an answer for a review of the last three days.

After the cells, three plain tables with no reading of yours: the
findings by scale and by kind of judge; the next acts by scale; and the
reviews by what the judge was given.

## The sources

- The review pages, `plans/*review*.md`.
- `plans/stack.md` and `plans/archive/`, for the frames and their
  status lines. Search them. Do not read `plans/stack.md` whole in one
  call.
- `git log` and `git show`, read commands only.
- `plans/method/reference.md`, sections 5 and 6, for the rules that ask
  for a review.

## The limits that you must carry into the page

- A status line is the session's own account of what it did with a
  finding. An earlier check found the status lines true and too sure: a
  doubt or a limit of an agent is often left out.
- A review page is the agent's account. Nobody checked a review against
  the code in this read.
- 40 of about 359 is one draw. Say so at the top of the page.
- One reader and one pass.
- Open no database.

## How you work

- You can start up to two sub-agents on Opus, each for a part of the
  sample, with a cap of 250k tokens each. Give each one the cells and
  the limits of this brief, word for word. Each writes to
  `plans/method/judges-read-extract-<part>-2026-11-10.md` and nowhere
  else. Wait for them in the foreground. You write the one page.
- Helper scripts go in the scratchpad of your session, written with the
  Write tool, and never in the repository.
- Write short plain sentences, with the result first: the counts of
  cells 3 and 5 at the top.
- When a source does not open or a count does not add up, write that in
  the page. Do not repair a record.
- Do not write the context count or a token estimate in the page.
