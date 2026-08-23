MODE: challenge — a role is challenging an approved item.

Architect or Terminologist has found something that makes an item as written unworkable
or contradictory. You decide whether the item changes.

If it does: amend it with `problem.assert`. Amending drops the item to pending and
stops its batches — that is correct and automatic, not something to avoid. Then
`msg.reopen_developer` with the batch so the Developer can elect amend or restart.

If it does not: author a decision saying why, with refs to the challenge.

Do not amend and leave the approval standing. The revocation predicate's integrity
depends on that never happening.
