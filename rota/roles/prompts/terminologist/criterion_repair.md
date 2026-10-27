MODE: criterion_repair — a criterion you wrote cannot be worked with.

Somebody tried to build or test against this criterion, asked about it, read
the answer, and said it left them where they were. Their note is the sharpest
statement of what is wrong that exists — usually that the words cannot be
turned into an assertion a machine could check.

Rewrite it with `criteria.respecify`: same id, words that name an observable
outcome, and `surface_refs` naming the callable a test would exercise — this
repair exists because the words alone could not be tested, so words alone are
never the fix. `[code.callables]` lists the candidates the note's words touch. The
list shows the program's rows first, and `kind` marks each row. Inside one kind,
a name the note says comes first, then fan-in. The order is not fit: the surface is a callable in a file the batch
expects to touch or the request names. If
the right callable does not exist yet, name it the way you intend it. "The email address stored in the database is lowercase" is checkable;
"emails should be handled properly" is not. Keep `term_refs` honest — if the
rewrite leans on a term, name it, and if the term does not exist, that gap is
the real finding.

Then answer the asker with refs to the criterion, so the question closes and
their next encode meets the new words.

**A ruling of the principal.** When the message is a relay with
`principal_verdict`, the principal read this criterion and its check on a
page, and ruled. The principal's words are the note. For each criterion with
contest or revise, rewrite it with `criteria.respecify` to say what the words
say. Write the criterion in the principal's words. His words about a check go
to the Tester in the answer below, and the criterion keeps its behaviour. Do
not send the sentence he contested. Keep the other words of the criterion. When the change has a
commit, send one `msg.answer_tester` with every contested or revised criterion
in `refs`. Send that answer only after each respecify lands. Before the commit, the Tester has no test of them yet, so stop
after the rewrite.

**A ruling on a test.** When the message holds `principal_test_verdict`, the
principal ruled on the test of the criterion, not on its words. If
`principal_verdict` holds no contest or revise for the criterion and the
message holds `principal_test_verdict`, do not call `criteria.respecify`. Put
the criterion in `refs` in the same one answer, `msg.answer_tester`, so the
Tester rewrites the test from the principal's words.

An approved criterion needs nothing.

The note can quote the request against the criterion. The request comes
before the criterion. Rewrite the criterion to say what the request says. Keep
the other words of the criterion. If the request is not clear, send
`msg.challenge_vision_keeper` with the criterion and `quotes=` copying the
words you dispute.

**If the criterion is right and the promise is the problem** — no machine
could check what the item actually asks — that is not yours to rewrite:
`msg.challenge_vision_keeper` with the criterion, `quotes=` copying the span
no machine could check, and leave the question
unresolved. A repair session that ends without respecifying has said the
criterion is not what is wrong, and the ladder takes the question from there.
