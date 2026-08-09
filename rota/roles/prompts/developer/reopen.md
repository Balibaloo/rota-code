MODE: reopen — an approved item changed under you.

Something the batch traces to was amended, so its approval was revoked and this
batch stopped. The message carries the revoked item and the batch you were in.

You elect, with `msg.elect_gatekeeper`:

- **amend** — the change is small enough that the worktree is still worth having.
  You keep the commits and rebuild your understanding of what is now being asked
- **restart** — the change is large enough that the existing work would be a
  liability to reason around. Both the worktree and your understanding go

Elect on how much of your *understanding* survives, not on how much code does.
Keeping a worktree whose assumptions have quietly expired is the expensive
mistake here, and it is the one that looks like thrift.
