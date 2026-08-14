# The system, derived

Written the other way round from everything else here: not what rota is, but
what a system like this *has to* contain, taken from its purpose and its one
hard constraint. Then the diff against what exists.

`REGISTER.md` was written this way and it worked — not by adding anything, but
by drawing a set nobody had drawn, so its gaps became visible. The same method,
one level up.

## Purpose, and the one constraint

Nine roles turn a principal's intent into a merged diff, and **no role ever sees
another's context.** That is not a limitation to work around; it is the point.
A role that cannot see how a conclusion was reached cannot inherit its author's
mistake, and a system whose parts cannot silently agree has to make agreement
explicit or fail loudly.

Everything below follows from that one constraint.

## What it forces

1. **Shared state must be artefacts**, because there is no other way for two
   roles to know the same thing. Hence: an artefact per kind of knowledge.
2. **Artefacts must have one writer**, because two writers with no shared
   context produce two truths and no way to tell which is current.
3. **Communication must be messages**, and a role can only address whom the
   graph connects it to — otherwise the context boundary is advisory.
4. **Every session starts cold.** A role is woken, acts, and is gone. So what it
   needs must be *pushed*, not remembered, and a mode is the answer to "why are
   you awake".
5. **Nothing may stop silently.** With no overseer holding the whole picture,
   work that stalls is invisible unless the stall is itself a row somebody is
   obliged to act on. Hence the register, and hence quiescence being a claim the
   system has to earn rather than a state it falls into.

## The three vocabularies

Each role needs three, and they are not the same kind of thing.

**What it owns** — the artefact it writes, and the operations on it. Designed as
a set, enforced by Law 1, checked against the graph by `ROLES.md`'s tests.

**What it can ask** — who it may address and with what verb. Designed as a set,
derived by Law 3, checked by `check_contacts`. There are no undeclared contacts.

**What it can say when it cannot proceed** — and *this was never designed as a
set*. It accumulated one verb at a time, each addition correct on its own, and
nobody has looked at the collection. Which is exactly what had happened to the
register.

### The moves that vocabulary needs

A role that cannot proceed is in one of a small number of situations, and each
needs a way out that is not a guess:

| the situation | the move |
|---|---|
| a word means two things | ask the terminologist |
| I cannot tell what would satisfy this | ask the gatekeeper |
| this conflicts with a commitment | escalate to the architect |
| this contradicts something a peer wrote | challenge the peer |
| the answer I got did not land | `schedule.reask` |
| nobody here can settle it | report upward, to the principal via liaison |
| I looked and there is nothing | `none_found` — a result, not a silence |

The last one is the tell. `none_found` was designed deliberately, as a
first-class discharge, because a survey that finds nothing had no way to say so
and the alternative was silence indistinguishable from failure. That was the
same problem as this, solved once, in one place, and never generalised.

### Who actually has what

| role | can say when stuck | missing |
|---|---|---|
| architect | question · challenge · propose · report | — |
| gatekeeper | question · report · submit | — |
| terminologist | question · challenge · report | — |
| developer | question · challenge · escalate | — |
| **tester** | **question** | escalate · challenge · report |
| **critic** | **challenge** | question — it cannot ask anything at all |
| researcher | answer | *deliberate*: it shares no context, so it has nothing to escalate about and nowhere to send it |
| liaison | ask · clarify · confirm · present · relay · deliver | — |

Two roles cannot say most of what a stuck role needs to say.

## What this predicts, and where it was wrong

A frame is worth having only if it predicts the failures before you look, and
this one has to be corrected on its first test.

**It predicted Tester's reds and the prediction was false.** Tester has one
move *when stuck*, so a stuck Tester should improvise — and four red cases do
show three tests written *and* a question sent when the case wanted the question
alone. But every one of those cases wants a `question` to Gatekeeper,
Terminologist or Researcher, and **Tester already has all three.** The
affordance is there. The role reaches for it and writes the tests anyway.

Law 3 makes the same point from the other side. `tester → architect escalate`
was drafted and refused: Tester neither reads an artefact Architect writes nor
writes one Architect reads. Developer's escalate is legitimate because Developer
reads the model, and a role that cannot see constraints could never detect the
collision it would be escalating. The missing edge was not missing; it was
undetectable, which is a different thing and a better answer.

**What actually explains every observed failure is the other half.**

- **Tester** is offered `tests.encode` in the same session where the right move
  is to ask. Both are available and only prose says when.
- **Gatekeeper**, woken to a thread between Tester and Terminologist, answered
  Developer five runs out of five: two answer channels, one situation, prose
  alone distinguishing them.
- **Architect**, given `schedule.reask` in a mode whose job is to record a
  constraint, called it with a boolean and never recorded the constraint.
- **Liaison** attached a message id, then the statement's text, to a channel
  where only the statement id resolves.

One diagnosis, four roles: **the toolkit is narrowed per mode, and never per
situation.** Every one of these is a session holding both the decisive action
and an alternative, where the state already determines which applies.

And that is not a new principle — it is one the frontier already applies and
the sandbox does not. `rests_on_a_collision` refuses to *offer* Tester a batch
whose criteria turn on a word with two live senses, precisely because a test
written from the wrong sense passes and pins the wrong promise. The scheduler
narrows by situation. Once a session starts, that reasoning stops.

So there is one gap, not two, and it accounts for five of the six failing
cases. Prose has failed to move any of them, which is what a structural gap
looks like from the outside.

**Critic's hole survives the correction**, and stands on its own: it cannot ask
anything. No case tests a Critic that does not understand a criterion, so it has
never been observed. Holes look like that before somebody draws the set.

## Where the current design is lacking

In the order the frame produces them, not the order they were noticed.

1. **The toolkit is narrowed per mode and never per situation.** This is the
   one that matters, and it accounts for five of six failing cases across four
   roles. The scheduler already reasons this way and refuses to offer work that
   rests on an open obligation; the sandbox builds the same namespace for a
   mode no matter what the wake says. Where the state determines which of two
   available things applies — which role asked, whether the term is settled,
   whether this session's job is to record or to report — the namespace should
   reflect it, and the alternative should be absent rather than discouraged.

   That is this repository's one reliable finding, applied where it has not
   been: *absence works, prose does not.*

2. **Critic cannot ask.** Critic is starved of the model and the decisions on
   purpose, and that starvation is load-bearing — a judge that remembers its
   prior objection is anchored. But *cannot see* and *cannot ask* are different
   properties, and only the first was intended.

3. **`architect → terminologist` has no reply edge.** The only question channel
   in the system that cannot be answered.

4. **The aggregation.** "What does this system not know" is still not one query,
   though every row of it exists.

**Not on the list, having been checked and found not to be a gap:** Tester's
missing `escalate`. It has the three question channels its failing cases call
for, and Law 3 refuses the escalate edge on the grounds that Tester cannot read
what it would be escalating about. The vocabulary table above is still worth
having — it is how Critic's hole was found — but it is not what is breaking
Tester.

## What this does not change

The spine, the laws, the register, and the artefact set all survive the
derivation unchanged — they are what the constraint forces, and they are what is
there. The gap is one vocabulary that was never drawn, in a system whose
recurring failure is precisely that: a set nobody has looked at as a set.

Twice now. Worth expecting a third.
