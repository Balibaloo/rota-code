MODE: park_ask — the team gave up on a change, and it waits for the principal.

The change on the `Refs:` line is parked. The line below the refs says which
batch it is and what the team gave up on. The first ref is the item the
change builds. The second ref is the batch. The other changes go on without
it.

Send one `msg.clarify_principal`. Put the item in `refs`. Say four things in
`question`, in plain words:

- which change is parked: the batch, by the name the line below gives it;
- what the team gave up on, as the line below says it;
- that a new commit on the change starts it again;
- that a contest of the item stops the change, and name the item.

Then ask what they want changed. Do not guess why the team gave up, and do
not suggest a fix. The principal decides.

    msg.clarify_principal(refs=["<the item>"], question="<the four things, then the question>")

Send it once, then stop.
