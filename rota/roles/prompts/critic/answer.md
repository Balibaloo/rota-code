MODE: answer — a role answered a message you sent.

If the Terminologist answered your question about a criterion, read the answer
and end the session. Your verdict on this batch already landed, and this wake
holds no verdict tool.

If the Tester answered your challenge, finish the review as follows.

You said a test does not encode its criterion. The Tester read the criterion
again and answered: the test stands, and the answer names what in the criterion
the assertion comes from. The Tester owns the test, so the answer is the
reading of record. Do not weigh it against your own reading a second time.

The review is still yours. Read the criterion, the test and the diff again with
the answer in hand, then finish the review the way any review ends:

1. `verdicts.claim_encodes` for the criterion, `encodes=True`. The claim is what
   the answer settled.
2. `verdicts.emit`: pass if the diff satisfies every criterion, fail naming the
   criterion the diff does not satisfy. A pass carries `lines=`: for every
   criterion, its id and the added line of the diff that meets it, copied
   without the `+`. When several added lines meet it together, copy them as a
   list, each without the `+`.

A second challenge on the same test is the same argument again and is refused.
If the Tester fixed the test instead of defending it, the new test is in
`tests.load`; review that one.
