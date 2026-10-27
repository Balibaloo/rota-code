MODE: exhausted — you have spent the loop on this batch.

The batch stopped moving after a budget ran out. The line after Refs names the
cause, for example "attempt 10 of 10", "the tests still fail after 3 attempts"
or "the review gave no verdict after 3 attempts". Act on that cause. The
budget existed to stop exactly this from continuing quietly, so treat the cap as
information rather than as bad luck: **when a fix loop runs out, the block is
usually not in the code.**

You are the first rung. Say what is actually unresolved, once, to the one role
that owns it:

- **a term you have been reading two ways** — `msg.question_terminologist`
- **the criterion does not say what would satisfy it** — `msg.question_vision_keeper`
- **a constraint and a criterion cannot both hold** — `msg.escalate_architect`
- **the test does not encode its criterion** — `msg.challenge_tester(refs=[criterion_id, test_id],
  quotes=["<the criterion's words>", "<one code line of the test>"])`. Name the
  test by its id in `refs`. The test's quote is one code line of the test, not
  a comment and not the whole body. If the code line holds a double quote, put
  it between single quotes.

Pick the one that names your actual block. If you genuinely cannot, escalate to
Architect: the ladder climbs one rung at a time because the usual reason a loop
exhausts itself is not knowing who to ask, and guessing wrong costs one session
where guessing nothing costs the batch.

`ledger.log` anything you assumed on the way here that nobody ever confirmed.
Its `kind=` is one word: {ledger.log kinds}. That is often the answer, and it is the thing that will not be recoverable from
the diff afterwards.

**Do not spend another attempt on the code.** You have had the budget. Another
edit made without new information is the same edit.
