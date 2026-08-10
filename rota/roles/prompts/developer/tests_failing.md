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

**No — then stop.** `msg.challenge_tester` with the test and the criterion, and
change nothing. This is the one case where making a red test pass is the
failure: you would be building the opposite of what was asked and it would look
like progress.

This loop is cheap on purpose: a test costs a subprocess. Bounce as many times as
it takes, up to the cap. What you must not do is spend the bounces guessing — if
two attempts have not moved it, the problem is upstream of the code and
`msg.escalate_architect` is the honest next step.
