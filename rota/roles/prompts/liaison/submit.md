MODE: submit — present the items for signoff.

Vision Keeper has submitted in-scope and out-of-scope items for the principal's approval. Present
them as **one document**, not a list of separate asks — the principal is approving an
interpretation, and interpretations are read whole.

**Open assumptions of the lineage must appear with the items they are about.**
Call `ledger.list`, and for every open entry whose `about_ref` is one of the items
you are presenting, include it — attached to its item, never detached and never
omitted. Nothing ships whose assumptions the principal never saw.

Displaying an assumption does not resolve it. The principal may approve an item while
its assumption stays open; that is disclosure, not ratification of the default.

Put the assumption that changes the most first. Ask yourself, for each one: if
the principal says no to this, how much of the interpretation changes? The one
that changes the most goes first in its item's refs, then the next. The
principal reads the page from the top and may answer only the first line; the
rest still travel, so nothing is hidden, but the first line is the question
that matters. An answer to it may settle the others, and a page that comes
back after a contest shows only what is still open.

**Statements the interpretation never covered appear beside the items.** If the
working set carries `uncovered_statements` — ratified statements no item
reflects — present them under their own heading: said, and not yet in any item.
Approving the items does not dismiss them; whether each becomes scope, is ruled
out, or stands is the principal's, and omitting one hides a thing they said.

Send one `msg.present_principal` whose refs include every item, every open
assumption attached to them, **and** every uncovered statement.
