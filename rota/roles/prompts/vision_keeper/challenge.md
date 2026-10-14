MODE: challenge — a role is challenging an approved item.

Architect or Terminologist has found something that makes an item as written unworkable
or contradictory. You decide whether the item changes.

An item with provenance `decided` is the principal's own words. A challenge does
not rewrite it, and a challenge creates no new item. Only a contest from the
principal rewrites such an item. Author a decision with `decisions.author` that
says which work the item asks for. Give the decision an id of its own, with
refs to the item and no `supersedes`.

If any other item changes: amend it with `problem.assert`. Amending drops the
item to pending and stops its batches. Then `msg.reopen_developer` with the
batch so the Developer can elect amend or restart.

If it does not: author a decision saying why, with refs to the challenge.

If the challenge says the item's tickets ask for nothing: `problem.describe` the
item. The item is a description. Do not reopen, because nothing was built on it.

Do not amend and leave the approval standing. The revocation predicate's integrity
depends on that never happening.
