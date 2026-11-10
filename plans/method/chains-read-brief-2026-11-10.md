# Brief: the walls that came back, and what ended them, 2026-11-10

Written by session 4a1d361a on frame 363. One read, one agent on Opus.
The agent reads and writes one page. It edits no other file, and it runs
no git command that writes.

## What you do

`plans/method/turns-list-2026-11-10.md`, section "3. The walls that came
back three times or more", lines 311 to 366, lists 41 chains. A chain is
one wall that the reads of the runs named in four turns or more. 27
chains hold by firm links, and 14 hold only with a "not sure" link.

For each of the 41 chains, write one block to
`plans/method/chains-read-2026-11-10.md`. Return ten lines: the counts
of the cells, the path, and what you could not find.

A wall is a problem that the read of a run named. A turn is a run of
rota, its read, the changes of the build session, and the next run.

## What the read asks, and what it does not ask

The read asks what the records show about the life of each wall: where
it came from, what was tried, and whether and how it stopped.

The read does not ask whether a fix was good. Do not rank the chains.
Do not write a cause for a pattern across chains. Write what the records
show for each cell, with its source, and write "not found" when they
show nothing. A cell that rests on absence alone says so.

This brief holds no expected answer. If you form one while you read,
write it in a last section of your page, apart from the blocks.

## The cells of one block

Each cell names its source: a path with a line, a commit, or a status
line of a frame with its minute.

1. The wall: its first line from the list, the first turn and the last
   turn that named it, and the count of turns. Check the chain against
   the wall lines in the three extracts,
   `plans/method/turns-list-extract-{a,b,c}-2026-11-10.md`, and against
   the read pages. If two walls of the chain are not the same wall, say
   so and split the block.
2. The state at the end of the records. "Open" when one of the last
   three runs of its series named it. "Ended" when three runs or more
   after the last naming did not name it. "Cannot tell" when fewer than
   three runs followed.
3. The conditions at the end. Did the requests, the models, the
   repository or the kind of run change between the last naming and the
   next three runs? The requests changed at night 163, the nights
   stopped at night 175, and the dry runs use another repository. A
   chain that ends at such a change is marked "conditions changed".
4. Every change that aimed at this wall, in order: the frame, the
   commits, the files, the kind (a door or a refusal, a prompt or a
   brief of a seat, a cap or a limit, other code of rota, the harness or
   the measure, a rule or a record only), and what the read of the next
   run said about the wall, with its count if it gives one. The count of
   such changes.
5. For an ended chain, the last change before the end. The evidence
   that joins the change and the end: a later read says with a count
   that the sign is gone, or a frame closes on such a count, or the sign
   is absent and no record says why.
6. The place of the changes. For each change of cell 4: does it touch
   the file and the function where the sign shows, or another place?
   Name both places. Do not class the change beyond that.
7. Who started each change of cell 4: a message of Roman (quote it), a
   read of a run, a row of a plan or a sprint, or a count.
8. The origin of the wall. Which code produces the sign: the file, the
   function, and the commit that added it (`git log -S` on the refusal
   text or the name, or `git blame`). Does that commit belong to a frame
   that answered another wall? Name that frame and that wall. "Rota's
   first design" is an answer, and "not found" is an answer.
9. After the end. Did the next three reads name another wall at the same
   place, or with the same seat and step, under another name? "Not
   sure" is an answer.

After the blocks, two plain tables with no reading of yours: one row for
each chain with cells 2, 3, the count of cell 4, the evidence of cell 5
in three words, and cell 8 in three words; and the list of frames that
appear in cell 8 of more than one chain.

## The sources

- The list and its extracts, named above.
- The read pages of the runs: `plans/night*-read*.md`, `plans/dry*.md`,
  `plans/archive/`, `plans/dry9/`, `plans/dry-blind1/`.
- `plans/stack.md` and `plans/archive/`, for the frames and their status
  lines. Search them. Do not read `plans/stack.md` whole in one call.
- `git log`, `git log -S` and `git blame` on `rota/` and `probes/`.
- `plans/wall-guide.md`, the known causes of walls, and
  `plans/method/product-doors-read-2026-11-10.md`, the origin commit of
  40 doors. Use their findings where they hold a chain, and do not count
  again.
- `python -m rota.tools.map fn|table|mode|file <name>` before you grep
  the code.

## The limits that you must carry into the page

- The chains come from one reader and one pass. A firm link is that
  reader's call. Cell 1 is the second look, so do it for every chain.
- A read page is the build session's own account. A wall that no read
  named after a change can still be there.
- The nights share state, and the records hold no pair of equal runs
  with fresh state. So one run without the sign does not show that the
  sign is gone. That is why cell 2 asks for three runs.
- The reads count walls in different ways. Some reads list only new
  walls, nights 127 to 137. A wall that such a read does not name is
  "not named", and not "gone".
- Do not open a database unless a cell needs it. If you must, open it
  with the URI `file:<path>?mode=ro&immutable=1`, so that SQLite writes
  no file beside it. The earlier read wrote `-shm` files with `mode=ro`
  alone.

## How you work

- You can start up to two sub-agents on Opus, each for a part of the
  chains, with a cap of 300k tokens each. Give each one the cells and
  the limits of this brief, word for word. Each writes its blocks to
  `plans/method/chains-read-extract-<part>-2026-11-10.md` and nowhere
  else. Wait for them in the foreground. You write the one page, and you
  check a sample of five blocks of each sub-agent against the sources
  yourself. Report the usage of each sub-agent.
- Write the page in short plain sentences, with the result first: the
  counts of cells 2, 3, 5 and 8 at the top.
- When a source does not open or a count does not add up, write that in
  the page. Do not repair a record.
- Do not write the context count or a token estimate in the page.
