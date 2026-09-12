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

What exists (read 2026-09-12): the reconcile phase of onboarding reads
prose against the account written from code, logs each disagreement as
a ledger row ("README says X; the code shows Y"), and the agenda puts
open ledger rows to the principal. That is the conflict page, and it
already always asks. The gap was reach: the phase read only the root
README, and clickI's 37 files under docs/ went unchecked.

Built 2026-09-12: one reconcile wake per prose file, `@prose` for the
README and `@prose:<path>` for each file under docs/ or doc/;
`code.prose` reads the wake's file; the attest closes that area alone
(`test_onboarding_phases.py`, "reads each docs file as its own area").

Owed:

1. Re-record `L1-VK-reconcile-the-readme` on the brief's new first
   paragraph (the file you were woken for).
2. A walk on a sample repository with a docs/ file that disagrees with
   the code. The page appears once and the ruling lands.
3. Code against prose inside one file (a docstring against its function)
   is the Architect's at survey and stays a finding. Not scheduled.

## Measured changes

| date | change | register | walk |
|---|---|---|---|
| 2026-09-12 | tipsAU: contest at the touch note, driver contested every page after | pinned both halves | amended, abandoned, re-batched; VK contested tick quarantined under twenty contests |
| 2026-09-12 | tipsAV: the driver contests once | | amended, four clarifies, re-approved at v2, new touch note, new batch running; stalled on the Architect grouping the wrong tickets and the Developer dropping the main guard; two doors (36a47df): the tickets its wake named, and the refusal names the appending span. No merge yet |
| 2026-09-12 | tipsAW: the two doors | | amended, two clarifies, re-approved, new touch note; the Vision Keeper re-sliced the new items under tk_1..tk_3, refused three times a session, quarantined. A colliding ticket id is derived now (3de1b89). No merge yet |
| 2026-09-12 | tipsAX: the derived ticket id | | amended, re-sliced under a derived id, a new batch running; then the Vision Keeper made an item of a challenged criterion's words under the criterion's id, and the Tester, Terminologist and Developer each stalled on the rebuilt batch in their own way. Two doors on the Vision Keeper's side; the three stalls are 9B judgement on tipsI's rebuilt batch. No merge yet |
| 2026-09-12/13 | tipsAY on the Titan: the two Vision Keeper doors | | amended, re-approved at v2, re-sliced and re-batched cleanly; the Developer made an empty package `split_bill/` beside the function in main.py, the Tester imported the name from the package, four tests died at collection, and the fix loop stalled; then one generation hung the Titan for three hours. Door: an import from a module that lacks the surface is pointed at the file that defines it. No merge yet |
