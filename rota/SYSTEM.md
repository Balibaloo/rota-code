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
| I cannot tell what would satisfy this | ask the vision_keeper |
| this conflicts with a commitment | escalate to the architect |
| this contradicts something a peer wrote | challenge the peer |
| the answer I got did not land | `schedule.reask` |
| I cannot reconcile this with that | challenge · propose · escalate, *refs only — words cost three cases* |
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
| vision_keeper | question · report · submit | — |
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
alone. But every one of those cases wants a `question` to Vision Keeper,
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
- **Vision Keeper**, woken to a thread between Tester and Terminologist, answered
  Developer five runs out of five: two answer channels, one situation, prose
  alone distinguishing them.
- **Architect**, given `schedule.reask` in a mode whose job is to record a
  constraint, called it with a boolean and never recorded the constraint.
- **Liaison** attached a message id, then the statement's text, to a channel
  where only the statement id resolves.

One diagnosis, four roles: **the toolkit is narrowed per mode, and never per
situation.** Every one of these is a session holding both the decisive action
and an alternative, where the state already determines which applies.

**How many cases it actually closes: one.** Counted rather than asserted, on
the third try, because the first two counts in this document were wrong:

| case | derivable from state? |
|---|---|
| `VK-the-last-rung` | **yes** — the asker is on the wake |
| `LI-a-question-the-roles-could-not-answer` | yes, and already fixed |
| `TS-a-word-with-two-senses` | yes, and the frontier already suppresses it — this case only runs because L1 injects wakes directly |
| `TS-a-criterion-no-machine-could-check` | **no.** "Easy for the finance team to work with" is unambiguous and untestable, and nothing in the rows says so |
| `TS-an-outside-fact-is-the-researchers` | **no.** Which criteria need a fact the project does not hold is a judgement |
| `TS-apply-a-term-and-write-the-test` | unrelated — a regression from the `reask` rename |

So the principle is sound and its reach is narrow. That is worth writing down
plainly, because a design principle that explains everything explains nothing,
and this one was on its way there.

**The two judgement cases are the interesting residue.** They have never passed,
under any prompt, in fifty runs each. No affordance is missing and no narrowing
applies: the role has to look at a sentence and conclude *this cannot be
tested*, or *this needs a fact we do not have*. If anything here is a limit of
the model rather than of the design, it is these two — and unlike the earlier
version of that claim, this one is arrived at by elimination rather than
offered as a hypothesis.

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

1. ~~**The toolkit is narrowed per mode and never per situation.**~~ Closed.
   `sandbox.build` takes the wake, and `situational()` is where a rule that
   depends on the state lives. One rule so far: on `tick:unresolved` the rung
   can answer the role that asked and nobody else, because the asker is the
   sender of the message the wake refers to. Vision Keeper answered Developer five
   runs out of five about a thread Developer is not in — not a temptation to
   resist, a capability with no situation.

   Right as a principle, small as a fix, and the value is forward-looking: the
   scheduler has always narrowed by situation and the sandbox stopped at the
   session boundary, so every rule of this kind had nowhere to live. Now it has
   one.

2. **Critic cannot ask.** Critic is starved of the model and the decisions on
   purpose, and that starvation is load-bearing — a judge that remembers its
   prior objection is anchored. But *cannot see* and *cannot ask* are different
   properties, and only the first was intended.

   The specific version of this — *Critic can object to the code and to the
   test, but not to the criterion it is judging against* — turns out to be
   already routed, and the route was drawn before anybody noticed the hole.
   Critic's own brief says it: "if a test does not encode its criterion,
   challenge Tester. Do not re-derive the criterion yourself." Tester holds all
   three question channels, so the chain is `critic → tester →
   {terminologist, vision_keeper, researcher}` and every edge of it exists. Giving
   Critic its own line would let it skip the role whose job that is, and would
   start it accumulating exactly the context the starvation exists to deny.

   What is left of the gap is narrower than it looked, and no case has yet
   produced a Critic that is stuck: every fixture tried resolves to a defensible
   `msg.challenge_tester`. It stays on this list because "I could not construct
   one" is evidence and not proof.

3. ~~**`architect → terminologist` has no reply edge.**~~ Closed. It was the
   only question channel in the system that could not be answered, and the
   reason it survived is on file: `terminologist → architect` was listed as a
   *silent channel*, "inform: the receipt cascade wakes it". True of a push and
   false of a reply — a correct answer often writes nothing at all, so no
   cascade fires and the question is simply never answered. Law 3 permitted the
   edge all along; nobody had drawn it.

   The pairing is a lint now rather than a thing to notice: every `question`
   channel needs its `answer` back, and every `answer` needs some verb it is
   replying to. The second half is what stops the first being satisfied by
   drawing answers nobody asked for.

4. ~~**The aggregation.** "What does this system not know" is still not one
   query, though every row of it exists.~~ Closed. `predicates.outstanding()`
   is that query — a fold over the register entries plus what the principal
   is sitting on — and the cockpit and TUI render it. (Staleness caught by
   the responsibility audit, 2026-09-03.)

**Not on the list, having been checked and found not to be a gap:** Tester's
missing `escalate`. It has the three question channels its failing cases call
for, and Law 3 refuses the escalate edge on the grounds that Tester cannot read
what it would be escalating about. The vocabulary table above is still worth
having — it is how Critic's hole was found — but it is not what is breaking
Tester.

## A note on this document

Three claims in it were wrong and were corrected within the hour: that Tester's
reds came from a missing verb, that one gap explained five of six cases, and
that the vocabulary table was the main finding. Each was stated confidently,
each was checked afterwards rather than before, and each fell to a five-minute
query against fixtures that were already there.

The pattern is worth more than the corrections. A frame that explains everything
you already knew is doing something other than explaining, and the tell each
time was reaching for a satisfying shape — *four roles, one cause* — before
counting. Where this document now says something is derivable, it has been
checked. Where it says a thing cannot be, that has been checked too.

## What this does not change

The spine, the laws, the register, and the artefact set all survive the
derivation unchanged — they are what the constraint forces, and they are what is
there. The gap is one vocabulary that was never drawn, in a system whose
recurring failure is precisely that: a set nobody has looked at as a set.

Twice now. Worth expecting a third.
