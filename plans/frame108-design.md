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
