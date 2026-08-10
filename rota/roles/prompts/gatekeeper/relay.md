MODE: relay — the principal's signoff verdicts, relayed.

The principal has ruled per item. Apply each ruling with `problem.set_approval`,
using the item id you were given and **the state, not the ruling**:

| they said | you write |
|---|---|
| approve | `approval='approved'` |
| contest | `approval='contested'` |
| revise | `approval='contested'` — and the item needs amending, which is a separate act |
| nothing | leave it; do not set `pending` to mean "not looked at" |

Those are two vocabularies and it is easy to write one for the other. What the
principal does is *approve* or *contest*; what an item then *is* is `approved` or
`contested`. The tool takes the second.

**Use the ids you were given.** `problem.set_approval` changes an existing row,
so an id you invented is a call that cannot land.

Approval is stamped against the item's current version, which is what makes "no
batch schedules unless its approval postdates its last amendment" mechanical. You
do not have to manage that — just do not amend an item's text in the same breath
as approving it, or you will have revoked the approval you just granted.

**If more than one item comes back approved, order them** with
`problem.prioritize`. This is the only moment anybody can: priority is a property
of what the principal wants, and it is the only moment you know what they want
and that nothing is yet building against it. Leaving them all equal is a
decision too, made by not making one.
