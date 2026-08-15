# The second half is a register

The delivery spine is a pipeline: work enters as intent and leaves as a
committed diff, through stages that are fixed, ordered, owned and drained. It
was straightforward to design because software practice hands that shape over
ready-made — a sequence, an artefact per step, a definition of done per step,
an owner per step.

The other half has no sequence and cannot be given one. A question can be
raised at any stage, by any role, about work that was already finished, and it
has to reach an owner and be discharged. That is not a pipeline. It is a
**register of open obligations**, and it gets easy the moment it is designed as
one, because registers have their own well-worn discipline: issue tracking in
the everyday form, an audit's open-findings register in the rigorous one, proof
obligations in the formal one — a goal is discharged or reduced, and
undischarged goals stay visible and countable.

## It is already here, and was never named

Of twenty-eight predicates, eleven move the spine forward, one is message
traffic, and **sixteen are register entries**: something is outstanding, and
the predicate exists to keep offering it until it is not.

    contradiction   contested        constraint_zero   awaiting_confirm
    agenda          quarantined      exhausted         round_close
    observed_entries reopen          tests_failing     verdict_failed
    checkpoint_invalid               survey            term_collision
    unresolved

`agenda` is the tell — its docstring is "on principal presence, present what is
blocked on them", which is an open-obligations query with no other name.

So the second half was not an afterthought in the sense of being absent. It was
built one predicate at a time, correctly each time, and never looked at as a
set. That is why its common properties are unenforced and its gaps invisible:
nobody can see a hole in a collection nobody has drawn.

## The invariant, taken from the one that works

Constraint zero is the best-designed thing in this repository and it is a
register entry. Four properties, each enforced by a test:

1. **It names what is not yet known** — every area nobody has surveyed.
2. **It is derived, never authored.** `refresh_constraint_zero` recomputes it
   from the surveys that exist: "the binding cannot drift from the evidence,
   because it is a function of it."
3. **It shrinks only by evidence** — a survey record whose citations are
   validated against the code index.
4. **No role can shrink it by judgement.** There is a test that it is
   unreachable rather than merely refused.

And `none_found` is a first-class discharge: "I looked and there is nothing"
closes the obligation exactly as firmly as finding something does.

**Derive, don't declare.** That is the whole principle, and it is the one thing
that went right this week: moving "has this role finished with this report" out
of Liaison's head and into `report_is_settled` fixed a case that five prose
attempts could not, and closed a livelock underneath it. Every mechanism
proposed afterwards -- a `settled` verb, a `blocked` verb -- was a role
*declaring* its own state, which is the same mistake wearing a spec.

## The register

Every obligation type, what derives it, what discharges it, and who owns the
discharge. `derived` is the state it is a function of; nothing on this table
should be a thing a role remembers to file.

| obligation | derived from | discharged by | owner | today |
|---|---|---|---|---|
| an area nobody surveyed | areas − surveyed areas | `surveys.attest`, incl. `none_found` | architect · gatekeeper · terminologist | **works** |
| a statement awaiting ratification | proposed, no confirm outstanding | the principal's verdict | liaison relays | works |
| two statements in contradiction | both `contradicted` | the principal's ruling | liaison relays | works |
| an item the principal rejected | `approval = contested` | gatekeeper amends or defends | gatekeeper | works |
| entries observed, never ruled on | onboarding entries with no decision | presented and ruled | liaison relays | works |
| a batch that spent its loop cap | `loop_cap` reached | escalation up the ladder | developer | works |
| a message the system gave up on | dispatched past cap | reported to the principal | liaison relays | works |
| **a question awaiting an answer** | open message, verb `question` | the answer arriving | the role asked | **derivable, underived** |
| a role waiting on its own question | this role sent a message still open | the answer arriving | — | **works** |
| a word with two live senses | ≥2 `glossary_terms` sharing a term, no decision | the principal's ruling | terminologist raises | **works** |
| two reports about the same thing | reports whose refs intersect, transitively | merged before sending | liaison | **works** |
| **an answer that did not resolve it** | *declared*: `schedule.reask` | somebody new speaking in the thread | the ladder, then liaison | **works** |

## What the gaps have in common

The four marked derivable-but-underived are the same omission: **an open
question is not treated as an obligation.** It is a message, and messages are
traffic. So:

- the asker has no *waiting* state, and `tests_failing` re-offers the work
  regardless — the loop cap burns, and only then does `exhausted` fire. The
  system's current answer to "I am waiting" is *spend the budget, then
  escalate*
- two roles blocked on one ambiguity are two independent discoveries
- dedupe has to be Liaison's judgement, which it should not be making, because
  there is no set to query
- and "what does this system not know" has no answer, though every part of it
  is a row that already exists

Note what this is *not*: a missing artefact. Every one of those derives from
`messages` and `glossary_terms` as they stand. It is a missing *view*, and one
predicate each.

## The one thing that must be declared

An answered question that did not help. The row says `answered`; only the asker
knows the answer left it where it was. Nothing derives that, and it is exactly
what the `exhausted` modes are written for.

So the second half needs **one** declared transition, not the two verbs an
earlier spec proposed. `settled` dissolves into predicates evaluated properly —
which is what fixing `round_close` already demonstrated. `blocked` collapses
into "this role has an open question", which is a query.

That spec was `REFUSAL.md` and is deleted. Both of its verbs were a role
declaring its own state, which is the mistake this page is about; keeping the
document to preserve the argument against it is the same instinct one level
out.

## What is worth building, in order

1. ~~**The waiting view.**~~ Built. A role with an open outbound question is not
   offered new work; the answer still reaches it, because message tips are never
   filtered.
2. ~~**The two-senses predicate.**~~ Built as `term_collision`, the glossary's
   `contradiction`.
3. ~~**Dedupe as a join.**~~ Built. Reports sharing a ref arrive grouped in
   `about`, by connected components rather than pairs, so A-B and B-C is one
   question in three vocabularies rather than two questions.
4. ~~**Suppression generalised.**~~ Built. Waiting held a role back for *its
   own* open question; work resting on somebody else's obligation is the same
   principle, and not applying it was the inconsistency. A batch whose criteria
   turn on a word with two live senses is not offered to Tester, because a test
   written from the wrong sense passes and pins the wrong promise. Narrow on
   purpose: only this obligation, because `criteria.term_refs` is a join that
   exists and there is no general way to say what a wake's work rests on.
5. ~~**The declaration.**~~ Built as `schedule.reask`, in `answer` mode for
   every role that can receive one. Everything after the declaration is derived
   as before: the next rung is the first role that has not spoken in the thread
   *and can reply to the asker*, Liaison last, and the obligation is discharged
   by somebody new speaking rather than by anyone closing it.

Nothing here added an artefact. Four views and one verb, and the verb writes a
single column.

**What the declaration replaced.** `developer/answer.md` used to end: *"if the
block truly survives the answer, the batch will bounce and wake you where the
ladder is."* That is a role being told to spend attempts it knows are wasted so
that a cap can notice what it already knows — the loop cap doing design work,
when a cap is a net for glitches and nothing else. A role that reports being
blocked is doing its job, and the system should act on the report rather than
wait for the budget to agree with it. Every `answer` mode now says the opposite,
and each says it in the terms of that role's own failure: a test encoded from a
guess passes, a constraint that cannot be tied to a commitment binds nobody, a
sense recorded twice leaves the collision live.

**The aggregation.** Built, as `predicates.outstanding()`. "What does this
system not know" is one query now: a fold over the sixteen register predicates,
returning each outstanding obligation with its owners and refs. It needed no
artefact, which is the point -- the obligations were always derived and only the
sum was missing, and an open-uncertainty artefact would have been a second copy
of rows that already exist.

`REGISTER_ENTRIES` lives in `predicates.py` and the list above is checked
against it, rather than this document being the only place the classification
exists. A runtime that folds over the set cannot take it from prose.

## Item 5, specified

The situation, exactly: Developer asks Gatekeeper whether partial
reconciliation counts as done. Gatekeeper's session commits, so the message is
`answered` and Developer stops waiting. The answer was "follow the acceptance
criteria", and Developer's question *was* that the criteria do not cover it.

Nothing in the database can tell the difference between that and a good answer.
`waiting` releases the role, `tests_failing` re-offers the batch, and Developer
guesses -- which is the loop the waiting view was built to stop, arrived at
through the front door.

**The declaration.** `schedule.reask(message_id)`: the asker says an
answered question of its own left it where it was. It goes on `schedule`
because it is scheduler-facing rather than about any artefact -- a role telling
the system about its own state, which is the one thing the system cannot
derive. New message status `unresolved`; the row is no longer open, so the
asker is not held by `waiting`, and no longer answered, so the register stops
believing the obligation is discharged.

**The escalation, derived.** A predicate over `status = 'unresolved'` wakes the
next role that has not sent in that thread, one rung at a time, exactly as
`exhausted` does for a spent batch -- the rung is a function of the messages,
not a stored pointer, for the same reason it is there.

Three things I decided against, recorded because each was tempting:

- *Deriving it from a re-ask.* If the asker knew who to ask next it would just
  ask, and there would be nothing to build. The whole content of the
  declaration is **"I am still blocked and I do not know who else to ask"**,
  which is also why the batch version of this exists.
- *Widening `exhausted` to cover it.* Same obligation, but a different ladder:
  a spent batch climbs `developer → architect → gatekeeper`, and a dead answer
  cannot start at Developer when Tester is the one asking. Two ladders in one
  predicate reads as one mechanism and is two.
- *Reusing the `exhausted` prompts.* Architect and Gatekeeper have them, so it
  is free -- and every word in them is about a batch that has spent its loop.
  A mode whose prompt describes a different situation is the prose failure this
  repository has paid for repeatedly.

**Both open questions are now settled, and the second one moved.**

1. **The ladder** is `architect → gatekeeper → liaison`, ruled. Liaison is the
   last rung rather than a silence, because a ladder ending in nothing is the
   dead end this half exists to prevent; it is not there to answer but because
   it is how anything reaches the principal. Rungs are skipped when the graph
   gives them no way to reply to the asker — which is not hypothetical, since
   Architect cannot answer Tester.
2. **Which modes brief it** was the wrong question, asked in cap-shaped terms.
   It belongs in `answer` mode for every role that can receive an answer, and
   the reason is not that this is a safe subset: that mode's job is *already*
   judging whether the answer landed, so the declaration is the honest branch of
   a decision the role is being asked to make rather than an alternative to
   making it. The failure that cost four cases was a briefed alternative inside
   a mode whose job is decisive, and this is the other thing.

   The old briefing question presumed roles should be trusted with a capability
   only where a regression would be attributable. That is designing around the
   measurement. The system trusts every role to do its job; the caps are for
   glitches.

## What it looks like from the floor

The table above is the shape; these are the situations it exists for. One
running project throughout -- a fulfilment service, where the principal wants
orders that arrive out of sequence reconciled.

**One word, two live senses.** Terminologist logs `order` = a customer's
purchase from the intake statement, and two rounds later, working from the
reconciliation ticket, logs `order` = the sequence events arrive in. Both
entries are right. The spine does not care: there is a glossary row, so
`criteria` proceeds, Tester writes `test_order_is_preserved`, it passes, and
the batch merges having pinned the wrong promise. Green is the worst outcome
here, because green is what everyone downstream reads. `term_collision` derives
it from the rows as the second entry lands, and any batch whose criteria touch
either entry stops being offered until the principal rules -- not a warning, an
absence from the frontier.

**Two roles, one blocker, two vocabularies.** The same ambiguity, later.
Gatekeeper cannot slice the item and reports ambiguous scope; Terminologist
reports a term collision; Architect reports that the boundary between queue and
ledger depends on which `order` is meant. Three roles that never share context,
three reports, one statement. Without a set to query, deciding they are the
same is Liaison's judgement, which Liaison may not exercise -- so the principal
gets three questions and answers two. `about` groups by shared refs
transitively, and one group is one question.

**Waiting is not "try again".** Developer asks Gatekeeper whether partial
reconciliation counts as done, and goes quiet. `tests_failing` offers the same
batch back next pass; Developer, with no memory of asking, guesses; the guess
costs an attempt; twelve attempts later `exhausted` escalates. The old answer
to "I am waiting" was spend the budget, then ask for help.

**The specification withdrawn mid-build.** The principal un-approves the item
while a batch is four commits into it. `batch_start` refuses to start an
unapproved batch and nothing touched one already running, so Developer kept
building, Critic judged against withdrawn criteria, and it merged. The only
case where effort is actively spent on something nobody wants, and it was the
half that was missing.

**The area nobody looked at.** Twelve areas, four surveyed. The system's
confidence should be bounded by that, and the only honest form of the bound is
a named list that no role can shrink by judging the code irrelevant.

**The system gave up, quietly.** A message past dispatch cap stops. A tick that
cannot drain is produced again every pass, so the run stays busy, keeps
committing, and never arrives -- six sessions on area one of twelve before
anybody read a counter. Reporting itself healthy while looping is the failure
that costs the most wall-clock.

**The principal walks in with ten minutes.** What is blocked on them is a
query, not whatever Liaison remembers.

**And the one still open.** Developer asks whether partial reconciliation
counts as done. Gatekeeper answers: follow the acceptance criteria. The row
says answered. It resolved nothing, because the question was that the criteria
do not cover it. Nothing derives that.
