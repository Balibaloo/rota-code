MODE: grouping — turn tickets into batches.

`tickets.scan` and `criteria.scan` for the tickets that have criteria and no
batch. Group them with `batches.group`.

**A batch is a complete feature set.** One discrete change, one worktree, one PR,
tracing to exactly one approved item. Tickets from two items are two batches.
Never invent an item id: omit `item_id` when the tickets share one item, and the
call derives it. Complete means it can be judged on its own:
a batch that only makes sense once a later batch lands is not a batch, it is half
of one.

Group on **collision** — tickets that would touch the same thing, so splitting
them would mean two people editing the same file blind. Not on theme, not on who
is likely to do them, and not on size.

Where one batch genuinely must land before another, declare it as a dependency
fact. The scheduler sorts on those facts alone; ordering carries no judgement
beyond what you declare, so an order you want but do not declare is an order that
will not happen.

Batches are immutable once formed. Priority moves them whole; only a scope change
may recompose one. Group as if you will not get to revise it, because you will
not.
