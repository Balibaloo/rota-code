# The stack's head rules, as they stood until 2026-10-18

Moved to `plans/method/reference.md` by frame 287's build step 3.

Rules:

1. Push a frame before starting it. Pop it when its "ends when" holds.
2. Write the status line with the date at every change and before any
   compaction.
3. Frames are mine to open, order and close. Roman's asks are frames too,
   marked "(Roman)". Roman can pop or reorder anything.
4. Linear. A frame that waits on another says which.
5. A frame is five lines: what, ends when, waits on, a pointer to the
   reasoning, and a dated status. The status line carries the peer name.
6. The session that holds a frame writes the first eight characters of
   its session id in the heading. A popped frame moves verbatim to
   `plans/archive/stack-<date>.md`.
7. Every frame carries a name of a few words in its heading, and every
   mention of it carries that name with the number. A number alone is an
   index into this file, so a reader who meets one has to open the file
   to learn what it means. That holds in a status line, in a commit
   message, in a message to a peer, and when you answer Roman (adopted
   from the kit on 2026-09-21, frame 52).
8. Every conclusion carries a mark with a headline-long reason:
   (observed: where and when), (reasoned: why), or (ruled: why). Say which
   workflow it is about, the meta workflow or the rota workflow (ruled
   2026-09-16: a ruling and a judgement looked the same in prose).
   An observation carries its date, because an observation ages. A check
   quoted without its date is a prediction that wears the word observed
   (adopted from the kit on 2026-09-20, frame 50).
9. Every frame's first line starts with `Site:`, the files or the seat it
   edits. Two frames that share a file are never held together. Every
   price line carries cycles beside tokens: a cycle is one agent's brief,
   report, status line and commit, about 10k of the holding session's
   context. A door text is 2 cycles, an instrument fix 3, a seam design
   with its night 8 to 10, a count that closes on a night 0 (ruled: Roman,
   2026-10-11 05:51; the measurement is in `plans/operating-facts.md`).
10. A session holds up to three agents at once and about twenty cycles
   in all. The session that launches a design frame's night hands off
   once every other held frame is at a commit (ruled: Roman, 2026-10-11
   05:51, "make sure that the meta workflow adopts these").
