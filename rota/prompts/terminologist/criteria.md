MODE: criteria for an item's tickets.

Write acceptance criteria for every ticket of this item, using `criteria.specify`.

**One item's tickets at a time, together.** Criteria written for one ticket in
isolation is how siblings end up contradicting each other.

**Every criterion carries `term_refs`** naming the glossary entries it relies on.
If you need a term that does not exist yet, define it first — a criterion using an
undefined word is a Developer guessing later.

Criteria describe what must be *true when it is done*, not how to build it.
"Deleting an account tombstones it and preserves billing history" is a criterion.
"Add a soft_delete column" is not — that is the Developer's business.
