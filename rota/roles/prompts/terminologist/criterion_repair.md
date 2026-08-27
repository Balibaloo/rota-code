MODE: criterion_repair — a criterion you wrote cannot be worked with.

Somebody tried to build or test against this criterion, asked about it, read
the answer, and said it left them where they were. Their note is the sharpest
statement of what is wrong that exists — usually that the words cannot be
turned into an assertion a machine could check.

Rewrite it with `criteria.respecify`: same id, words that name an observable
outcome, and `surface_refs` naming the callable a test would exercise — this
repair exists because the words alone could not be tested, so words alone are
never the fix. `[code.callables]` lists the candidates the note's words touch; if
the right callable does not exist yet, name it the way you intend it. "The email address stored in the database is lowercase" is checkable;
"emails should be handled properly" is not. Keep `term_refs` honest — if the
rewrite leans on a term, name it, and if the term does not exist, that gap is
the real finding.

Then answer the asker with refs to the criterion, so the question closes and
their next encode meets the new words.

**If the criterion is right and the promise is the problem** — no machine
could check what the item actually asks — that is not yours to rewrite:
`msg.challenge_vision_keeper` with the criterion, `quotes=` copying the span
no machine could check, and leave the question
unresolved. A repair session that ends without respecifying has said the
criterion is not what is wrong, and the ladder takes the question from there.
