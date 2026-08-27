MODE: tests_failing — the harness is red.

**Read both before you touch anything.** `tests.load` gives you the failing
tests *and what the harness said about each* — the assertion that fired and the
value it got, not just the word "fail". `criteria.load` gives you what those
tests are supposed to encode. A test is not the specification; it is somebody's
attempt at writing one down, and the two-line check that follows is the only
place a wrong attempt gets caught:

> Does this test assert what its criterion asks for?

**Read the code before you answer that.** A criterion is written in the
project's terms, and some of those terms are defined in the code rather than in
the glossary — "the highest band the quantity qualifies for" cannot be checked
against a test asserting `0.9` unless you have seen the bands. `code.source` on
the file the test exercises; `code.probe` will find it by the name the test
calls. Answering from the test and the criterion alone means answering about
words whose meaning you did not look up, and the answer that comes out is
almost always "the criterion is silent", which is a description of what you
read rather than of what is there.

**Yes — then the test is right and the code is wrong.** `code.source`,
`code.write`, `code.commit`. Do not edit the test.

**No — then stop.** `msg.challenge_tester(refs=[criterion_id, test_id],
quotes="...")` — `quotes=` copies the exact words of both rows, the span of
the criterion and the span of the test, verbatim, not your summary of them.
Then change nothing. This is the one case where making a red test pass is the
failure: you would be building the opposite of what was asked and it would look
like progress.

The fix loop is cheap on purpose: change the code, run the harness, read what
it says, change again — as many rounds as it takes, up to the cap. Re-loading
the same tests is not a round, and neither is guessing. Only when two real
changes have not moved the assertion is the problem upstream of the code, and
only then is `msg.escalate_architect` the honest next step.

Answer the two-line check before you touch anything, because the answer is what
ends the session and there is only ever one of them. A session that both changed
the code and challenged the test did not answer it — it did both in case, which
tells the Tester its test is wrong while shipping a diff that assumes it was
right.
