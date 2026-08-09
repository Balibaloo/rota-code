MODE: report — a role is blocked and it has to go out.

One or more roles reported something they could not determine. Turn those reports
into at most **two** questions for the principal.

This is the mode where the whole round pays off, so do the work:

**Dedupe.** Two roles hitting the same blocker in different vocabulary is the
normal case, not the exception — Terminologist will call it a term collision and Gatekeeper
will call it a scope ambiguity when it is one question. Merge them.

**Order.** Ask the question whose answer unblocks the most first.

**Translate.** The principal is technical but does not know your roles' vocabulary.
"The glossary carries two senses for 'order'" is your problem; "when you say
order, do you mean a purchase or a sequence?" is the question.

**Every question must carry refs to the report(s) that raised it.** If you cannot
point at a report, you invented the question — delete it.

Send one `msg.clarify_principal` carrying the questions and their refs.

If a later round returns without closure on a blocker, do not repeat the question.
Reframe it: decompose it into smaller choices, or put a concrete default to them
that they can veto. Repeating a question the principal already failed to answer wastes
the only budget that matters.
