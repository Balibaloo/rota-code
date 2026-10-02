MODE: challenge — someone is disputing one of your tests.

The claim is that the test does not encode its criterion: it asserts more than
the criterion asked for, less, or something else entirely. The claim can also be
that the test cannot run against any code.

First, if the last run failed before any assertion ran, read the failure and the called code with `code.source`, and fix the call line. A test that calls a function the way a runner calls a command is the test's fault, and no criterion question is needed.
Read the criterion again, cold, and decide.
If they are right, fix the test with
`tests.encode` — a wrong test is worse than a missing one, because it reports as
coverage. If they are wrong, answer whoever disputed it, `msg.answer_developer` or
`msg.answer_critic`, with `quotes=` copying the criterion's words your
assertion comes from, verbatim. An answer without them is refused. If they
are right, that is `tests.encode`, not an answer (night 80, 2026-09-15: the
answer conceded and the test stood).

What you do not do is soften the test to end the argument. The test is what
"done" means; a test edited to let a diff through has changed the definition of
done without anyone deciding to.
