MODE: deliver — new ratified statements.

Statements have been ratified by the principal. Decide what they mean for scope.

**First, check the decision record** with `decisions.search` for prior refusals
that are semantically adjacent — the wording will differ, that is the point. If you
find one, report it to Liaison with refs to both the decision and the statement,
and write **no** items. You are blocked pending a principal ruling, not proceeding
with a caveat.

Otherwise, assert in-scope and out-of-scope items with `problem.assert`. One item per
distinct thing the software must do. Check `problem.consult` first — an item already
on file for the same behaviour is not asserted again under a new id, however
differently worded.

Write an out-of-scope item only where the statement's own words name a boundary —
not any boundary you can imagine holding. A short, simple statement implies little;
do not manufacture caveats it never raised.

If a statement is too vague to turn into an item, report the blocker to Liaison
rather than guessing. But if this blocker has already been put to the principal once
without closure, do not report it again — instead propose: draft concrete items
with explicit out-of-scope items that the principal can veto. A concrete wrong answer they can
reject beats an abstract question they cannot answer.
