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

## What this predicts, and what actually happened

A frame is worth having only if it predicts the failures before you look. This
one does.

**Tester** has one move. So a Tester that cannot proceed will do the only thing
it can: the work in front of it, badly, and an ask alongside. That is precisely
what four red cases show — three tests written *and* a question sent, in the
same session, when the case wanted the question alone. It is not a role being
careless. It is a role with an obligation and no affordance, improvising.

**Critic** cannot ask. No case tests a Critic that does not understand a
criterion, so this has never been observed. It is a hole, not a bug, and holes
are only found by drawing the set.

**Gatekeeper answering the wrong role** is the other shape: not a missing move
but an ambiguous one. Woken to a thread between Tester and Terminologist, it
answered Developer five runs out of five, because the mode offers both channels
and only prose says which. An affordance the situation does not narrow is a
guess with extra steps.

So the failures divide cleanly:

- **no affordance** — the role has nothing to say. Tester, Critic.
- **ambiguous affordance** — the role has two and the situation determines
  which, but only prose says so. Gatekeeper's answer channel.

Both are structural. Neither is a prompt problem, which is consistent with prose
having failed to move any of them.

## Where the current design is lacking

In the order the frame produces them, not the order they were noticed.

1. **Tester's vocabulary.** Ruled: it gets `escalate`, the same as Developer.
   `challenge` and `report` follow from the same argument and should be settled
   at the same time rather than one per discovered failure.
2. **Critic's inability to ask.** Critic is starved of the model and the
   decisions on purpose, and that starvation is load-bearing — a judge that
   remembers its prior objection is anchored. But *cannot see* and *cannot ask*
   are different properties, and only the first was intended.
3. **Ambiguous recipients.** Where a mode grants two channels and the wake
   determines which, the sandbox should narrow to the one — it narrows per mode
   today and not per wake. The recipient is derivable; it is the role that
   asked.
4. **`architect → terminologist` has no reply edge.** The only question channel
   in the system that cannot be answered.
5. **The aggregation.** "What does this system not know" is still not one query,
   though every row of it exists.

Items 1–3 are one design decision each and would close five of the six failing
cases. Item 4 is a single edge. Item 5 is the register's last piece.

## What this does not change

The spine, the laws, the register, and the artefact set all survive the
derivation unchanged — they are what the constraint forces, and they are what is
there. The gap is one vocabulary that was never drawn, in a system whose
recurring failure is precisely that: a set nobody has looked at as a set.

Twice now. Worth expecting a third.
