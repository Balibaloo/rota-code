# The nine seats

What each role is answerable for, and — more usefully — what it must never
decide. `LAWS.md` says what the system may never do; this says who may do what,
which is the question that actually comes up when something goes wrong.

**Read this before changing a brief.** Four separate failures in one week were a
role being asked to do something that is not its job, and every one of them cost
a model run to find. Liaison deciding whether a round had settled. Developer
re-asking a question in the mode whose job is to apply the answer. Architect
passing an escalation on rather than routing it. Critic holding a second route to
Developer for something its verdict already carries. All four are legible from a
boundary; none is legible from a brief.

Nothing here grants anything. `design/graph.json` is the authority and the
namespaces are built from it — a role's edges are what exist, and a sentence in
this file cannot add one. `tests/rota/test_roles_doc.py` asserts that every claim
below matches the graph, so this drifts loudly rather than quietly.

---

## Ownership, and the three exceptions

Law 1 is single-writer, and fifteen artefacts have exactly one:

| artefact | owner | | artefact | owner |
|---|---|---|---|---|
| `problem` | vision_keeper | | `model` | architect |
| `tickets` | vision_keeper | | `batches` | architect |
| `glossary` | terminologist | | `findings` | architect |
| `criteria` | terminologist | | `code` | developer |
| `brief` | liaison | | `tests` | tester |
| `transcript` | liaison | | `verdicts` | critic |
| `references` | researcher | | `frame` | architect |
| `challenge` | critic | | | |

Four are shared, by ruling rather than by accident:

- **`ledger`** — architect, developer, vision_keeper, terminologist, tester. A
  choice the criteria did not make is logged by whoever had to make it, so
  restricting the writer would mean the choice went unrecorded or was recorded by
  somebody who did not make it.
- **`decisions`** — architect, vision_keeper, terminologist. Each owns a kind of
  ruling in its own domain.
- **`surveys`** — architect, vision_keeper, terminologist. A survey record is an
  attestation by the role that did the reading.
- **`schedule`** — architect, developer, vision_keeper, terminologist, tester, via
  `schedule.reask` alone. Everything else about the schedule is derived and
  read-only; this is the one thing the scheduler cannot derive, which is a role
  saying an answer it received did not resolve what it asked. Same shape as the
  ledger: whoever hit it is the only one who can report it, and restricting the
  writer would mean it went unreported.

An artefact acquiring a second writer is a design change, not a convenience.

---

## liaison

**Answerable for** the brief and the transcript, and for the principal's
attention, which is the one budget in this system that cannot be topped up.

**Never decides anything.** Its responsibility is lossless communication. This
is the sharpest line in the system and the easiest to erode, because almost
every decision looks like a small helpful tidy on the way past. Ranking two
contradictory statements by recency, choosing which sense of a word was meant,
judging that a role has finished — none of these are Liaison's, and each has
been attempted.

The corollary is structural: anything mechanical is done *before* Liaison is
woken. Whether a report has settled is a lookup on `approval` and `status`, so
`report_is_settled` does it in the scheduler and a settled round never reaches
Liaison at all. If you find yourself writing "Liaison should work out whether…"
into a brief, the sentence belongs in a predicate.

**Reaches** architect, vision_keeper, terminologist (ask, deliver), vision_keeper
(relay), and the principal (clarify, confirm, present).

**Woken by** agenda, awaiting_confirm, blindspot, contradiction, observed_entries,
quarantined, round_close.

**The principal is the one reader who cannot follow a ref**, so refs to them are
rendered as words by `render_refs`. What a question carries is whatever the
problem being raised actually is — the two senses of a word when the collision is
the problem, the statement when the wording is. Nothing is mandatory beyond
naming the thing in question.

## vision_keeper

**Answerable for** scope: what is in, what is explicitly out, and cutting
approved items into tickets a Developer can pick up cold.

**Never decides meaning.** A word's sense is Terminologist's. A scope ambiguity
and a term collision are frequently the same blocker in two vocabularies, and
the difference is whose artefact changes.

**Reaches** developer (answer, reopen), liaison (answer, report, submit),
researcher (question), tester (answer).

**Woken by** contested, orient, reconcile, reorient, signoff, slicing.

**Orient is its first session on any repository.** Before a word in the
program has been named, it reads the front — manifest, README, the authoring
surface, the entry point — and writes what the product does for its user, as
observed items. Every later onboarding phase is written with that account in
front of it.

## terminologist

**Answerable for** the glossary and the acceptance criteria — meaning, and what
would satisfy it.

**Never decides scope.** If a statement is vague about *what should be built*
that is Vision Keeper's report. Collapsing two senses into one is a decision, and
two senses is a finding, not a failure to resolve.

**Reaches** architect (answer), developer (answer), vision_keeper (challenge),
liaison (answer, report), researcher (question), tester (answer).

**Woken by** criteria, define, term_collision.

**Define is one word at a time, over the whole program.** The lexicon — what the
checkout declares: directories, files, types, authoring keys — says which words,
the concordance is pushed, and the session writes one entry for the word it was
woken for. A meaning is not shaped like a place; this is the mode that stops
asking area-shaped questions about words that live in five areas.

**A word with two live senses is raised for you, not by you.** Two statements
that conflict have always been an obligation the frontier derives; two senses of
one word are the same situation in your artefact and used to be raised by
whichever role tripped over them while trying to do something else. It is one
fact about the glossary, so it is on the register once and it is yours.

## architect

**Answerable for** the system model — constraints that are external commitments
— their bindings, batch grouping, and structural review.

**Never grants scope.** A refactor is scope, so a seam the structure cannot
carry is `msg.propose_vision_keeper`, not a decision. An escalation that arrives
carrying a constraint has already been diagnosed by the role that hit it;
passing it to Liaison spends a rung of the ladder and answers nobody.

**Reaches** developer (answer), vision_keeper (challenge, propose), liaison
(answer, report), researcher (question), terminologist (question).

**Woken by** annotate, boundary, frame, grouping, structural_review.

## developer

**Answerable for** the code, and for the ticket in front of it.

**Never builds what nobody asked for.** Noticing something else is a scope
question or a `ledger.log`, never a quiet fix — invisible in the moment and
undiscoverable afterwards is the exact failure this system exists to prevent.

**Reaches** architect (escalate), vision_keeper (elect, question), researcher
(question), terminologist (question), tester (challenge).

**Woken by** batch_start, reopen, tests_failing, verdict_failed.

**Its `answer` mode cannot ask anything, deliberately.** Asking a second role
the same question is how one question becomes three answers; asking the same
role again is a loop with nothing new in it. A block that genuinely survives an
answer bounces the batch and wakes it in `exhausted`, where asking is the job.

## tester

**Answerable for** encoding each criterion as a test — the criterion, never the
implementation.

**Never decides what the criterion means.** A word it cannot pin down is
`msg.question_terminologist`; a criterion no machine could check is
`msg.question_vision_keeper`. A test that passes trivially is worse than no test,
because it reports as coverage.

**Reaches** developer (answer), vision_keeper (question), researcher (question),
terminologist (question).

**Woken by** tests_missing.

## critic

**Answerable for** one verdict per batch, on one commit.

**Never fixes anything**, and holds the narrowest namespace in the system:
criteria, tests, code, a verdict and two challenges. A fail names its criterion
and stops.

**Reaches** developer (challenge), tester (challenge).

**Woken by** challenge, review.

**Work nobody asked for is the one judgement a verdict cannot carry** — a fail
names the criterion it fails, and an unrequested change satisfies every criterion
there is. That is what `msg.challenge_developer` is for, and it is the reason the
edge exists.

## researcher

**Answerable for** facts from outside this repository, and for the references
that make them checkable later.

**Never decides whether the fact applies.** A standard's definition is
authoritative about the standard and says nothing about which sense this project
means — that judgement stays with whoever asked.

**Reaches** architect, developer, vision_keeper, terminologist, tester (answer).

**Woken by** nothing. It is the only role with no predicate: it acts when asked
and never on its own initiative.

**It has no code execution and no unrestricted network.** Domains are granted by
the principal through the interface, never by a role and never by Liaison. A
refusal is a result: record nothing, say what was tried.

## the principal

Not a role. A person at a terminal, or a scripted stand-in for arc tests, whose
whole power is answering questions and holding final authority. They cannot
write an artefact, address a role other than Liaison, or see the frontier.

They are also the only participant who cannot dereference an id, which is why
`render_refs` exists.

---

## Known open boundaries

Written down because an undecided boundary is worse when it is invisible.

- **Where outward questions belong.** No mode's job is asking the Researcher, so
  the channel competes with the deciding action wherever it is offered — briefing
  it in five deciding modes cost four green cases. Answers persist as references
  and `references.load` is pushed, so the asker gets what is already known for
  free; what is unsettled is where the *asking* goes. See `KNOWN_UNBRIEFED` in
  `tests/rota/test_prompts.py`.
- **Whether messages should carry prose by default.** Law 2 says conclusions
  travel and reasoning stays home, and only the Researcher channel has a text
  field, because it shares no database. Making prose the default across every
  channel is an amendment to Law 2 rather than a change of habit.
- **Ticket readiness** is split three ways — Architect via the touch set,
  Vision Keeper owning the text, Terminologist the criteria — and is recorded as an
  accountability rather than resolved.
