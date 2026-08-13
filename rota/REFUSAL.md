# What a role says when it cannot

A spec, written to be checked. Nothing here is built yet.

Every terminal act in this system is positive: a message sent, an artefact
written, an area attested. A role that has nothing to produce has no way to say
so, and a role that *cannot* produce what it was woken for has no way to say
that either. Both come out as invention, because a session with turns left and
no way to stop does not stop.

## The evidence

**Three new Tester cases, all red, all the same shape.** A criterion turning on
a word with two senses; a criterion no machine could check; a criterion needing
a fact from outside the project. In each the right move is to ask and write
nothing. The session asks *and writes the tests anyway* — three of them, in a
fixture where every one is wrong:

    message m1 missing refs {c_d5288d}; forbidden write to tests: [t1, t2, t3]

It hedges. Note carefully what this is and is not evidence for: sending the
question and writing nothing *is* representable today, so this is a judgement
failure and not proof of a missing act. What it shows is subtler and still to
the point — the mode's decisive instruction is "one test per criterion", the
question is an exception to it, and stopping without producing anything is an
absence rather than an outcome. A session asked to produce something, holding a
reason it should not, and given no way to *record* that reason, produces
something and records the reason beside it. Making the not-producing an act
with a name is what turns that from a hedge into an answer.

**Twelve turns arguing with an argument.** An Architect bound a constraint to
`account`, a name it had probed with rather than anything the probe returned, in
a fixture whose code index is empty. Refused, it alternated `code.source` with
the identical amend for the whole budget. It could have said "there is nothing
here I can bind" on turn two.

**Three attempts at a stopping rule.** All channels used, all recipients
reached, reply-to-the-sender — each fixed one case and broke another, and the
last is in the tree as an admitted heuristic. The terminal condition is not
derivable from the tool list: *the session knows and has no way to say.*

**`round_close` fired forever on a settled round.** Fixed by moving the lookup
into the predicate, which is right — but the general form is unfixed. A mode
whose correct outcome is nothing has no act with which to be correct.

## The prototype that already works

`surveys.attest(outcome="none_found", citations=[...])`.

A surveyor woken for an area can say *"I read this and there is no commitment in
it"*, and that is a **result**: it closes the area, drains the predicate, and is
checkable, because the citations are validated against the code index. Its brief
says so outright — *"you are not stuck and you have not failed, you are
finished."*

It is the best-behaved thing in the system, and everything below generalises it.

## Two verbs, and they must not be one

The distinction is the whole design, and collapsing it is the failure mode:

| | `settled` | `blocked` |
|---|---|---|
| means | there was nothing to do here | I cannot do this |
| the work is | **finished** | **not finished** |
| the wake | drains | must stay live |
| propagates to | nobody | whoever can unblock it |
| precedent | `none_found` | quarantine, but declared |

A block that drains looks like completion, and the work disappears. That is the
one failure this whole design is arranged against — *"a system that quietly
stopped trying would report itself finished with the work undone"*, which is
already why `quarantine_stalled` reports through `tick_quarantined` rather than
dropping silently.

Note what that means: **quarantine already exists and is only ever inflicted.**
The scheduler infers "this could not proceed" from a wake dispatched past its
cap. `blocked` is the same state, declared by the role that knows it, twelve
turns earlier and with a reason attached.

## Evidence is mandatory

`none_found` is trustworthy because citations are validated. A refusal that
cannot be checked is a quieter escape hatch, and this week's most reliable
finding is that **any alternative to the decisive action gets taken** — four
cases lost to it in three files, one of them an error message of mine that named
a way out.

So both verbs carry evidence, and the evidence is checked at the boundary:

- `settled` carries what was examined. For a survey that is citations; for a
  round-close it is the reports crossed off; for a review it is the criteria
  read. The rule: **name what you looked at, and it must exist.**
- `blocked` carries the refs it is blocked *on*, and they must resolve. "I
  cannot write this test until `<c1>` says what would satisfy it" is checkable.
  "I am stuck" is not, and is refused.

A `blocked` whose refs all resolve to rows in a terminal state is refused too —
if everything it names is settled, it is not blocked on any of them.

## Per role

What each may legitimately refuse, and the evidence that makes it checkable.
Derived from what each role is answerable for; see `ROLES.md`.

| role | `settled` means | `blocked` means | evidence |
|---|---|---|---|
| **gatekeeper** | the statements imply no new scope | the boundary turns on something only the principal can rule | the statements read; the item or statement in question |
| **terminologist** | every term is already defined the same way | a word carries two senses and choosing is a decision | the terms looked up; the colliding term ids |
| **architect** | nothing here leaves the module | the structure cannot carry it without a scope change | grains read (already `none_found`); the seam |
| **developer** | the batch is already satisfied by the code | a criterion cannot be met without breaking a constraint | files opened; criterion and constraint |
| **tester** | every criterion already has a test | the criterion is not machine-checkable as written | criteria read; the criterion |
| **critic** | *never* — a batch always gets a verdict | *never* — abstain is a verdict question, open in `AGREED.md` §7 | — |
| **researcher** | the sources say nothing on this | no granted domain can answer it | what was searched and refused |
| **liaison** | nothing came back needing a ruling | — it decides nothing, so it is blocked by nothing | the reports crossed off |

Two rows are deliberately empty. **Critic may not refuse**: a batch it was woken
for gets a verdict, and "I could not judge this" is the abstain verdict, which is
a different open question and should not be smuggled in through this door.
**Liaison cannot be blocked**: its responsibility is lossless communication and
it makes no decisions, so there is nothing for it to be unable to decide — a
question it cannot answer is one it passes on, which is its ordinary work.

## Propagation

- **Message wake.** `blocked` answers the sender with the refusal and its refs.
  The sender is woken by it and is the one who chose to ask, so it is the one
  that must now do something else. This is the "error that propagates to the
  invoker" in the ordinary sense.
- **Tick wake.** There is no sender. `blocked` must land somewhere a predicate
  can see, or the work is silently dropped — which is the artefact this system
  does not have. Until open uncertainty is a table, a tick-woken `blocked` has
  nowhere honest to go, and **this half should not be built first.**
- **`settled`** drains the wake and propagates to nobody, which is what makes it
  the safe half to build.

## Build order

1. **`settled`, tick wakes only.** It has a working precedent, needs no new
   artefact, and its propagation question is empty. It closes the round_close
   shape and the "no terminal act" gap directly.
2. **The open-uncertainty artefact**, because `blocked` from a tick has nowhere
   to land without it, and because it is separately worth having: answers
   accumulate in this system and questions do not, so the same ambiguity found
   in two batches is two discoveries by two roles with no memory.
3. **`blocked`, message wakes**, which needs only the refusal verb and the
   sender.
4. **`blocked`, tick wakes**, once 2 exists.

## What would falsify this

The obvious risk is that both verbs become the universal answer — every session
refusing, because refusing always succeeds. The measurement already exists: the
negative half of L1 says an action must not fire when the fixture does not call
for it, so every case in the suite is also a case about not refusing.

If the L1 pass rate falls when these land, they are wrong, and the evidence
requirement is the first thing to tighten.
