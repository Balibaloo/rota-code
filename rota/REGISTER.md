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

Of twenty-six predicates, eleven move the spine forward, one is message
traffic, and **fourteen are register entries**: something is outstanding, and
the predicate exists to keep offering it until it is not.

    contradiction   contested        constraint_zero   awaiting_confirm
    agenda          quarantined      exhausted         round_close
    observed_entries reopen          tests_failing     verdict_failed
    checkpoint_invalid               survey

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
| **a role waiting on its own question** | this role sent a message still open | the answer arriving | — | **missing** |
| **a word with two live senses** | ≥2 `glossary_terms` sharing a term, no decision | the principal's ruling | terminologist raises | **derivable, underived** |
| **two questions about the same thing** | open questions whose refs intersect | merged before sending | liaison | **derivable, underived** — and dedupe is judgement today |
| **an answer that did not resolve it** | *not derivable* | asking again, elsewhere | the asker | **the one honest declaration** |

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

So the second half needs **one** declared transition, not the two verbs I
specced in `REFUSAL.md`. `settled` dissolves into predicates evaluated properly
— which is what fixing `round_close` already demonstrated. `blocked` collapses
into "this role has an open question", which is a query.

`REFUSAL.md` should be read as superseded by this on both counts, and is kept
for the evidence in it rather than the design.

## What is worth building, in order

1. **The waiting view.** A role with an open outbound question is not offered
   the work that question blocks. One query, and it stops the cap burn that is
   behind most of this week's churn.
2. **The open-question view.** Open questions as a queryable set, so dedupe is a
   join and not a judgement, and so "what is unresolved" can be answered at all.
3. **The two-senses predicate.** A word with two live senses and no ruling is an
   obligation nobody currently raises; today it is found only when a role trips
   over it.
4. **The declaration**, last, because it is the only piece that cannot be
   checked by derivation and should be added when everything cheaper is in
   place.

Nothing here adds an artefact. Three views and one verb.
