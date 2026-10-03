# Frame 108: a tail reply larger than the budget empties the window's middle

Design record. Written by 3d6e6173 on 2026-10-03 after a read of
`_cap_exchange` and the head of `_fit` in `rota/core/runner.py`, and of
frame 100's status lines of 2026-10-01 14:57 and 15:04 in
`plans/archive/stack-2026-10-02.md`. Meta workflow, about the runner.

## The defect

`_fit` keeps the wake and the last two blocks, the seat's reply and its
results, and packs the middle from what those leave. The wake is capped
at two thirds of the budget before the packing. The tail is not capped
before it. A tail over the budget leaves negative room, every middle
block drops, and `_cap_exchange` at the end cuts the tail only after the
middle is gone. Night 99, s132, turn 13: a 30,894-character reply against
a 26,309 budget emptied the middle, and turns 15 to 18 re-read four spans
(observed: frame 100's reviewer, 2026-10-01).

## The decision

1. The tail is capped at a fixed share of the budget before the tiers run:
   `tail_room = budget // 3`. The share is of the budget and not of the
   room the middle leaves, because a cap sized from the middle is circular
   (reasoned: frame 100's reviewer, point 8). One third pairs with the
   wake's two thirds, so a wake and a tail at their caps still fit.
2. The cut inside the tail is `_cap_exchange`'s own rule: the reply and
   the results share the room half each, and a block under its half lends
   the rest to the other, never below `_MIN_EXCHANGE`. The sharing moves
   into one helper that both the new cap and `_cap_exchange` call, so the
   two cuts cannot drift.
3. The final `_cap_exchange` stays as the safety net, and the fewer-than-
   four-blocks path does not change.
4. A tail under the share is untouched, so every transcript that fit
   before packs to the same bytes.

## The measure

- One runner test on s132's turn 13 shape: a wake of about 13,500
  characters, four read results in the middle, a reply of 30,894 and its
  results, budget 26,309. Green when at least one middle read survives and
  the tail is at most `budget // 3`.
- One test that a tail under the share packs to the parent's bytes.
- The next night shows it: the count of turns whose prompt holds the
  dropped note with every middle block gone.

Price: one pass about 30k on Opus, one diff review about 20k.

## Revision 2, after pass 1's stop

Pass 1 on Opus stopped before a commit: a flat `budget // 3` cap on both tail blocks turns 9 runner tests red (observed: the agent's runs on 032c71c, 2026-10-03). The runner sizes a turn's results at `budget - wake - reply` at `runner.py:2873`, and its comment says a cut must land in the runner, where the sentence names the call that fetches the rest. A third of 26,309 is 8,769, under `SOURCE_CHARS` at 14,000, so the flat cap cut whole source reads and undid night 79's rule that a cut span is re-asked. Decision 2 falls.

1. The cap cuts the reply only. The results block is the runner's to size, and s132's fault was the reply at 30,894 characters.
2. The reply's room is `max(budget // 3, budget - (len(wake) + 2) - budget // 3)`: a third at least, and a small wake lends the tail the part of its two thirds it does not use.
3. The cap fires only when the tail as it stands leaves the middle less room than the smallest middle block, so no middle block could survive the packing. A tail that leaves room for one block is not this defect, and the existing test that the tail stays untouched holds (reasoned: the agent's variant B failed that one test by a 50-character cut that freed no block).
4. The sharing helper is not needed. `_cap_exchange` does not change.
5. The runner's `result_room` does not change. Out of this frame.

The measure stands: on s132's shape at least one middle read survives and the reply is at most its room. The parent-bytes test covers a tail that leaves room for a middle block.
