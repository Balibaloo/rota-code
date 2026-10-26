# The closed frames of the last two weeks, how much should have been generalised

Roman asked on 2026-10-26 at about 21:5x: "with all this knowledge, send another agent to review frames resolved in the last two weeks to see how much work should have been generalised". Four reads on Opus, parts a to d, over the 67 frames closed from 2026-10-12 to 2026-10-26, `plans/closed-reach-a.md` to `plans/closed-reach-d.md`. Each counted the readers of the frame's fact with `git grep` at the closing commit and at head d1c934ae, searched the later frames at the same fact, and priced a fix at the source by the anchors in `plans/operating-facts.md`.

## The count

| Part | Frames | At the source | At one door of N | Wrong premise | Not this shape | Cycles spent | At the source |
|---|---|---|---|---|---|---|---|
| a, 10-12 to 10-14 | 15 | 2 | 10 | 0 | 3 | 105 | about 79 |
| b, 10-15 to 10-16 | 20 | 1 | 15 | 0 | 4 | 112 | 61 to 65 |
| c, 10-17 to 10-21 | 17 | 2 | 13 | 0 | 2 | about 138 | about 42 |
| d, 10-23 to 10-26 | 15 | 2 | 10 | 1 | 2 | 164 to 187 | 54 to 83 |
| all | 67 | 7 | 48 | 1 | 11 | about 520 to 540 | about 240 to 270 |

Of the 56 frames of the shape, 7 fixed at the source, 48 at one door, 1 on a wrong premise (observed: the four records). The one-door frames covered a median of 1 of 6 places. 45 of the 48 have a later frame at the same fact, about 90 links in all, and those later frames' cycles are in neither sum, so the gap is wider than 2 to 1 (reasoned: parts b and d price no later frame).

## The facts that came back

- His ruling on a ref: frames 213, 221, 225, 226, 227 (part a), then 258, 305, 308 (part d), then 329, 337, 338, 339 open. About 20 readers at head. Frame 221 replaced the shared reader `last_ruling_on` with its own query (observed: part a).
- The latest run of a batch: frame 210, 24 readers at head, three ordering rules; frame 213 added one more the next day (observed: part a).
- The lines his words fault: 12 readers at the close, 16 at head (observed: part d).
- The test's error line: 9 rules at the close, 12 at head; frame 336 open (observed: part d).
- Which request owns a row: six functions, two disagree, frame 274 added a seventh, frame 316 followed (observed: part c).
- In 6 of part b's 15 one-door frames the one reader already existed and the fix wrote a copy beside it: 187, 202, 229, 230, 238, 245 (observed: part b).

## What the records say about the method

The wall guide, frame 251, prices a fix at one door as the norm (observed: part b). Frames 228, 229 and 236 closed on three nights of 0 at a door that never fired, and frame 236 closed with no fix built (observed: part b). Frame 189 waited five days on a refusal another frame had changed five hours after the push (observed: part a). Rule C76 of 2026-10-26 is the amendment, and frame 340's gates enforce its reach line (ruled: Roman, 2026-10-26).
