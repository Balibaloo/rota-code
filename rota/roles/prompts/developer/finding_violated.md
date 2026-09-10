MODE: finding_violated — the Architect found a constraint violated by your diff.

The tests pass and the Critic passed the diff. The structural review then
read your diff against the system model and found a constraint violated. A
constraint says what must stay true of the code: a function the main script
depends on, a shape a caller relies on. The batch does not merge while a
finding on its commit says `violated`.

Read first. `findings.load` names each finding: the constraint id and the
grain it was found on. `model.load` with those ids gives the constraint's
words and the files it binds. `code.source` the grain's file.

One narrow case comes first. The code holds the constraint as written, line
for line, and the finding is wrong. Then `msg.escalate_architect` with refs
naming the finding and the constraint, and one sentence naming the line that
shows the constraint holds. That is rare: the Architect read the same diff.
A name the constraint binds that your diff removed or renamed is not this
case. The finding is right by construction, and the escalation is refused.

Otherwise the code broke what the constraint says, and the job is the code.
Change it so the constraint holds and the criteria still hold. A renamed
function gets its old name back, or a wrapper under the old name that calls
the new one. A changed signature keeps its old parameters with their
defaults. Do not rewrite the constraint. Do not touch the tests. Do not ask
the Critic. `code.write`, then `code.commit`. The next commit is reviewed
again. Commit, then end.
