# A retired present

Loop 3's third chaos injury (`LOOPS.md`: "a verdict for a present that was
re-presented meanwhile"), reproduced 2026-09-03 and pinned `xfail(strict)` in
`tests/rota/test_chaos_confirm.py`. Held back on one word: the message-status
CHECK at `rota/core/schema.sql:482` allows `open`, `answered`, `unresolved`,
`quarantined`, and a superseded present is none of those.

## The injury

The principal's screen shows a present of an item at version one. The world
moves: the item is amended (`problem.assert` on an existing id, `version + 1`,
approval dropped) and Vision Keeper submits it again; Liaison presents it
again. Both presents are open. `pending_asks` puts both to the principal; a
ruling on the first lands, relays to the owner, and `problem.set_approval`
stamps `approval_ver` with the item's *current* version -- the principal
approved words they never saw.

## What must hold

The first present is retired, and retired is a third state:

- not **open** -- it must not be put to them again, and an open ask to the
  principal silences the agenda tick (`scheduler.py`, "if something is already
  open to the principal ... there is nothing to add") and the baseline offer
  (`predicates.py`, `observed_entries` is suppressed while a present is open);
- not **answered** -- an answered present with no verdict is a deferral
  (`predicates.py`, "a deferral is an election", `do:defer_baseline`), and the
  audit flags an answered message nothing was caused by.

## The mechanic, written and measured

Landed in `rota/core/db.py` in the session-commit path, immediately after the
loop that inserts `result.messages`, and reverted the same hour because every
re-present then failed to commit on the CHECK (`IntegrityError: CHECK
constraint failed: status IN ('open','answered','unresolved','quarantined')`):

```python
        # A present puts a row to the principal once, and a later present of
        # the same row is the one to answer. The earlier one is superseded
        # here, at the door every present lands through -- superseded, not
        # answered: an answered present with no verdict is a deferral
        # (`do:defer_baseline`), and this is not that.
        for m in result.messages:
            if m.verb != "present" or m.to_role != "principal":
                continue
            fresh = set(m.body_refs)
            for old in conn.execute(
                    "SELECT id, body_refs FROM messages WHERE verb = 'present' "
                    "AND to_role = 'principal' AND status = 'open' AND id != ?",
                    (m.id,)).fetchall():
                if fresh & set(json.loads(old["body_refs"] or "[]")):
                    conn.execute(
                        "UPDATE messages SET status = 'superseded' WHERE id = ?",
                        (old["id"],))
```

With the word in the CHECK, nothing else changes: `pending_asks` selects
`open`, so the retired present is not offered; `principal.land` (2026-09-03)
closes an ask only `WHERE status = 'open'`, so a stale ruling lands nothing;
the deferral predicate selects `answered`, so it is not a deferral. The
pinned test asserts exactly that and flips loudly the day it passes.

## The decision

Two shapes, the seat's:

1. Add `superseded` to the CHECK. An existing database keeps its old
   constraint -- `init_db` only creates -- so a running run needs the
   constraint rebuilt or accepts the door failing on it until re-created.
2. A rule that needs no new word. None found: `unresolved` has the ladder's
   semantics, `quarantined` has exhaustion's, and deleting a message is not a
   thing the transcript does.
