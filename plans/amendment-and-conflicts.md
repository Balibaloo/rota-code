# Amendment and conflicting sources

Two of the seat's four pages (DECISIONS.md, "The seat's four pages are one
surface", 2026-09-12). Both are answered in words through `principal.land`.
Neither adds a verb the principal must learn.

## Amendment, level 2

An approved item is amended: its text changes under the principal's name.

Rule: a batch built from the item that has not merged is cancelled and
its worktree kept as evidence. The item is re-batched from the new text.
A batch that merged stays merged, and the amendment becomes a new batch
on top of it, with the merged tests as its inherited floor.

Facts the doors need, all in the database today: which batches carry the
item (`batch_tickets`), whether each merged (`batches.status`), the
item's version (`items.version`). No judgement in the door.

The desks' part, in briefs: the Vision Keeper re-derives the criteria for
the amended text. The Architect re-predicts the touch. The touch note is
owed again because the batch is new.

What exists (read 2026-09-12, nothing here is new): a `revise` ruling at
a page marks the item contested, the Vision Keeper amends it and its
version rises, and the next signoff stamps `approval_ver`. The `cancel`
predicate abandons a live batch whose item's approval is older than its
version (law 9's ending, `test_steering.py`). The `slicing` predicate
re-slices a delivered item whose version rose past its delivered version
and has no live batch, and `grouping` batches the new tickets fresh. So
level 2 is mechanics already built, and what is owed is the measurement.

Build order:

1. A pinned test for the merged half: an item delivered at version 1,
   amended to version 2 and re-approved, owes new tickets, and its old
   tickets stay with the merged batch. (`test_steering.py` pins the
   running half.)
2. A walk on tipsI: amend the split item after its batch starts. The
   batch is abandoned, the item re-sliced, the new batch merges.
3. A walk on tipsI: amend a merged item. A new batch merges on top of it.
4. The same on click, the night after click merges cold.

## Amendment, level 3, the measured upgrade

Invalidate by touch: compare the amendment with the batch's touch set and
criteria. Untouched criteria keep their tests and verdicts. Touched ones
are re-tested. This saves the most work and needs a judgement, "does this
change affect that", from a desk. Gated on a walk where level 2 cancels a
batch the amendment did not touch. Not before.

Level 1 (restart everything) and level 4 (an amendment is a finding
against every dependent row, each owner rules) are recorded in
DECISIONS.md and not chosen.

## Conflicting sources

Two documents in the repository disagree about one fact: a README and a
config, two docs, a docstring and its code.

Rule: always ask. The finding names both sources and the sentence in each.
The page puts them to the principal in words. The answer is a ruling that
lands as a statement. The desks read it like any other.

Facts the doors need: the two rows (`findings`, `code_index` grains) and
that both still exist at present time. The judgement, "these disagree",
is the Researcher's or the Architect's at survey, in the brief.

Build order:

1. A register case: the Architect surveys two files that state one fact
   two ways and files a finding naming both.
2. The finding's page: the Liaison presents a conflict finding, and the
   ruling lands as a statement.
3. A walk on a sample repository seeded with one conflict. The page
   appears once and the ruling lands.

## Measured changes

| date | change | register | walk |
|---|---|---|---|
