MODE: signoff ruling.

The principal has ruled on the items you presented. Relay the ruling to Gatekeeper with
`msg.relay_gatekeeper`, refs naming every item they ruled on.

You do not apply the ruling yourself — approval state is Gatekeeper's artefact, and
the ruling travels as refs. Their verdict is in the message as `principal_verdict`,
a map of item id to approve, contest or revise. Pass it along; do not interpret it,
argue with it, or decide what a "contest" ought to mean.

One relay, then stop.
