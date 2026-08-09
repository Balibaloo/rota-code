MODE: signoff presentation.

Vision has submitted scope items and non-goals for the client's approval. Present
them as **one document**, not a list of separate asks — the client is approving an
interpretation, and interpretations are read whole.

**Open assumptions of the lineage must appear with the items they are about.**
Call `ledger.list`, and for every open entry whose `about_ref` is one of the items
you are presenting, include it — attached to its item, never detached and never
omitted. Nothing ships whose assumptions the client never saw.

Displaying an assumption does not resolve it. The client may approve an item while
its assumption stays open; that is disclosure, not ratification of the default.

Send one `msg.present_client` whose refs include every item **and** every open
assumption attached to them.
