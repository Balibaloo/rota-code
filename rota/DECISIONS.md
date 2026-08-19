# The decision register

`LAWS.md` says what this is and what it may never do. This says what we have
*decided* and what is still open — with the consequence of each decision written
next to it, because a decision whose consequence is not recorded gets re-argued
the first time it costs something.

Three sections. **Settled** is the input to the vision. **Open** is the work list
for the next design round. **Assumptions** is the settled column rephrased so
each claim can be falsified, which is the only form in which a decision can be
tested rather than defended.

---

## The claim

> Eight roles that never share context, given a repository none of them wrote,
> can produce a change a competent engineer would accept — and the artefacts
> explain why it was made.

Note what it does not say. Nothing about fixture pass rates: those measure
whether the harness is honest, which is a gate on interpreting the claim rather
than the claim itself. Nothing about speed. Nothing about autonomy.

The second clause is not decoration. A monolithic agent with a large context
window can plausibly produce the change. It cannot produce the account of why,
and it has no boundary across which to refuse.

---

## Settled

### The researcher owns nothing shared

It answers a message and writes only its own `references` rows. The **asking**
role decides whether to cite, and citing means writing into the artefact that
role already owns.

*Consequence:* over-indexing is structurally impossible — nothing enters the
model unless a role with ownership put it there. And "who may ask" stops being a
policy: a role can ask if it can cite, which is an edge in the graph. Law 3
derives the contact list from that with no second list to disagree.

*Consequence:* the researcher's scope — questions of fact about things outside
this repository — is a property of its artefact, rendered into every asker's
contact list from one declaration. Roles that would otherwise ask it for
judgement, implementation, or scope are told what it is for in the same place
they are told it exists.

### The researcher is never woken by a predicate

Predicates are defined by what they drain. The researcher owns nothing shared,
so a predicate waking it would have nothing to drain and would fire forever.

*Consequence:* external push still works, through the owner. A reference goes
stale; the drift predicate wakes **the role whose artefact cited it**; that role
asks. One mechanism, not two, and the same shape as code drift.

### A new role is justified by a trust boundary, not a capability

*Consequence:* git history is read tools on the roles that need it — local,
hermetic, replayable, no boundary to police. The internet is a role, because it
is none of those. This rule is expected to settle the next several arguments of
the same shape.

### Drift is scoped to exactly what has been cited

Commits are the unit. Diff to files, files to grains, grains to citations,
citation to the artefact, artefact to its owner — and the owner is woken.

*Consequence:* the watched set is derived, never configured, and grows exactly as
fast as the system's actual responsibility does. On a large repository where
three areas have been surveyed, nothing else is watched.

*Consequence:* it needs a watermark (last reconciled commit), a diff→grain
mapper, and line spans in `code_index`. The spans already exist in the parser —
tree-sitter nodes carry `start_byte`/`end_byte` and `_text()` uses them — they
are simply not persisted. Until they are, drift resolves at **path** granularity,
which over-notifies but is correct.

### No deployment role

It splits three ways: a **gate the principal owns**, an **environment concern**
under 3Bd, and **runtime observation** under Tester.

*Consequence:* it fails the role test on its own terms. Every role exists to make
a judgement no other can; a deployer would judge "is this safe to release", which
is Critic and Gatekeeper, and "is it working out there", which is evidence that
it works and therefore Tester's.

*Consequence:* deployment is the first irreversible outward action in a system
where everything else is reversible — a bad commit is a branch, a bad artefact is
superseded. That asymmetry is why it is a gate rather than an act.

### Declarative infrastructure only

*Consequence:* declared infrastructure collapses into the delivery loop that
already exists. The file is a diff, writing it satisfies a criterion, `plan` or
`what-if` is the test, Critic reviews, and `apply` is the principal's gate.
Imperative infrastructure has no criterion, no test, no review, and no way to say
afterwards what it did.

*Consequence:* credentials belong to the **environment**, not the role. A role
calls a tool; the environment it runs in holds the identity. This is the first
reason 3Bd has to exist beyond running tests.

### The domain allowlist is configuration, not an artefact

*Consequence:* the "humans do not edit artefacts" position never comes under
pressure, because an allowlist is not an artefact. It is a cap like any other,
and law 7 puts caps in `config.py`, owned by the principal.

*Consequence:* an unlisted domain is not an error path. It folds into the
researcher's ordinary "I could not find out, and here is what I tried" answer.

### Research spends a third kind of scarcity

`loop_cap` spends compute. `interrupt_cap` spends the principal. A research cap
spends the outside world — rate limits, and trust surface.

*Consequence:* law 7 says these are deliberately not one number, for exactly the
reason that sharing a name lets someone tune the cheap one and change the
expensive one. A third scarcity gets a third cap.

### Fetched text is never instruction

*Consequence:* the containment already does most of the work — the researcher
writes nothing but its own rows, the asker sees a claim and a source rather than
raw page text, and no namespace widens because of what was read. Worth stating
as a property because it is the strongest security argument the design has.

*Consequence:* queries are **constructed** from the question, never forwarded.
The asker may put whatever context it likes into a question; that context is for
the researcher's understanding and must not reach the wire.

### The researcher does not know the system

No batches, no criteria, no constraints. Questions from roles, answers with
sources.

*Consequence:* smaller prompt, replaceable component, and no path by which the
outside world learns anything about the project through it.

### Git: do not rebase mid-batch

*Consequence:* a verdict is a judgement on a specific commit. Move the base and
the judgement describes code that never existed. Reconcile at merge; an unclean
merge is a wake, not a silent auto-resolve.

*Consequence:* `batch_dep_facts` declares "A before B" and git currently ignores
it. Dependent batches should stack — B cut from A, not from main — or the
dependency is expressed in the database and discarded at the point it would pay.

*Consequence:* PR versus auto-merge is a config switch, not an architecture
decision. The principal already signs off at item level, so a diff-level gate is
redundant when supervised and essential when unattended.

### Test files are indexed but not partitioned

*Consequence:* roles can read tests as evidence — which matters for a repository
whose specification conformance is pinned in its test suite — without test
directories becoming areas of their own. Measured on icalendar: six of fourteen
proposed areas were `tests/*`.

### The first target is oauthlib, as a fork

Four RFCs, directories named after them, twelve areas that survive the dependency
check, `nonce` and `client` each used in two senses, a suite proved to pass with
sockets blocked. icalendar is second, once test partitioning is fixed.

*Consequence:* fork only. No PR is opened against oauthlib, which removes the
question of putting unrequested output in front of maintainers and keeps `gh` out
of scope. Upstreaming can be decided later on the merits of an actual diff.

### Onboarding runs twice

Once with the researcher unavailable to survey modes, once with it available.

*Consequence:* same repository, one variable. Strictly better evidence than
either run alone, and it removes the objection that a first foreign-repo run with
a brand-new role has two possible causes for any failure.

### The operator's interface: the seat drives, the cockpit answers

Three rulings, made while making rota runnable rather than derived from the
laws. Argued in [SEAT.md](SEAT.md); recorded here because a proposal is where a
decision gets re-argued and this is where it gets found.

**The cockpit is read-only, always. The TUI drives.** Everything with an
*intent* — create, run, wipe, fork, talk — is the seat's. Everything with a
*question* — what was this role shown, what caused this — is the browser's.

*Consequence:* the cockpit never changes state, so it never has to answer "is
what I am looking at still true", and every panel in it inherits that guarantee
instead of that question. The run list is therefore the seat's, and a
browser-first operator is a thing this system does not offer rather than a gap
in it.

**A run that cannot be read is named, not migrated.** Seven of eight existing
runs are behind the schema; `ls` reports `stale` and the reason and touches
nothing.

*Consequence:* databases stay throwaway — every one is built by `init_db` at
boot — and no migration path is promised. The blank column that preceded this
read as "no state yet", which is the silent shape the whole register exists to
refuse.

**Closing the seat stops the run, so quitting takes a confirmation.** The loop
runs in the app's worker thread and there is no headless continuation.

*Consequence:* pausing is free and resuming is just running again — "the
frontier *is* the state; reconstructing it is the entire recovery" — so the
interface says what happens rather than engineering around it. And a
confirmation must be *cancellable* rather than merely observed, which makes
`src/ui/modals.py` the thing to reuse rather than the arm-and-type mechanism I
improvised without checking whether one already existed.

**A survey is a receipt for a tree, and must be signed like one.** Four tables
already record the commit their evidence was gathered at — `batches.head_commit`,
`test_runs.commit_sha`, `findings.commit_sha`, `verdicts.commit_sha` — and
`boot.reconcile_worktrees` is the half that notices the tree has moved past the
receipt. None of it was ever pointed at the understanding side: `survey_records`,
`glossary_terms` and the run itself record no commit at all.

*Consequence:* **Re-surveying**, below in Open, is not blocked on a design — it
is blocked on this. Nothing can fire on "an area whose code changed since its
record" while nothing records which code the record was of. Recording the commit
is also what makes two runs comparable, which is what an interface wants it for,
but that is the smaller reason.

---

## Amendments the settled column forces on LAWS.md

### Law 11 — provenance gains a third value

`decided` is the reason on file, written by the decider. `observed` is extracted
from an onboarded codebase: found, not chosen. External knowledge is neither.

Proposed: **`cited`** — found outside the repository, attributable to a source,
and the only kind of claim that can become false without anyone touching the
project. `provenance` is a `NOT NULL CHECK` on every artefact that has one, so
this is a schema change, not a convention.

### Law 13 — the retrieval date

Law 13 forbids it: *"no date, duration or timestamp column exists in
`schema.sql`"*, enforced as a build check.

Resolution without amending the law: **the date is for a human, not the system.**
Nothing the system does with staleness needs one — "the page changed" is a hash
comparison, and "it has been a year" is a time judgement law 13 says the system
does not get to make. So `references` carries `content_hash` and a retrieval
sequence, and the real timestamp lives in the **fetch cache**, which is evidence
like the cassettes rather than an artefact, and therefore outside the law.

---

## Open

### The frontier, when several things are ready — the big one

Wakes are ordered by band, then **alphabetically by predicate name**. The loop
takes the first whose role is unclaimed. That is a placeholder that has never
been under load.

Evidence it is load-bearing: `message_tips` sits in band `traffic` (0) and
`round_close` in band `gate` (20), so the first report always won, Liaison
answered from the one report it could see, and the harvest check then suppressed
the round permanently. The round existed in the design, the docstring and the
prompt, and never ran once.

Every test we have runs a frontier of size one. 41 of 59 cases seed at most one
row in any fixture table; 33 hand the role zero refs, 24 hand it one, 3 hand it
two. Nothing has ever been handed three. 5 of 55 mode prompts contain any
language about handling several of something.

*Blocked on:* nothing. *Gated by:* onboarding, deliberately — `tick_survey`
serialises itself, so onboarding will run on today's frontier and its failures
are the specification for this work.

### Re-surveying

`tick_survey` fires on areas with no record. Nothing fires on an area whose code
changed since its record. Over a project's lifetime this is what decides whether
the model of the codebase stays true.

*Blocked on:* ~~a survey recording the commit it surveyed~~ — **built.**
`survey_records.commit_sha` carries it, read from `config.project_commit`
because a survey reads grains from `code_index` and the index was built at that
commit; asking git at attest time would record where the tree is standing rather
than what was surveyed. Empty when the project is not a checkout, so the
predicate can tell "surveyed at an unknown commit" from "surveyed at this one".

*Now blocked on:* nothing. The predicate is the work — an area whose grains have
changed since `commit_sha` needs re-surveying — and it was never hard, which is
why it sat here behind a missing column.

### Amendment as the normal operation

Every mode is optimised for writing something new. Over a project lifetime the
common session is "this glossary sense is now wrong". Superseding is currently
something statements do; it may need to be the main verb for everything.

### The push does not scale in time

`brief.list` pushes statements into every Liaison prompt. Relevance filtering
stops being an optimisation and becomes load-bearing.

### Conflicting sources

Two authorities disagreeing is the interesting case. The researcher reports the
conflict rather than resolving it — consistent with Liaison not choosing between
contradicting statements — but there is no mode for it.

### Challenging a test costs less than fixing the code

`L1-DV-fix-the-code-not-the-test` went 5/5 to 0/5 when eight exported JS symbols
entered the index. The interesting part is that nothing about what the Developer
can see of its own task changed: `probe('pricing')` returns five hits, none from
`web/`, with `src/catalog/pricing.py` first, and the same holds for `line_total`
and `catalog`. Only an empty pattern reaches `web/` at all.

So it flipped on a prompt *perturbation*, not a degradation — and what that
measures is that the choice is not robust. Every run emits
`msg.challenge_tester` and then `code.write` in one turn; the forbidden call
arrives first and neither lands. It is trying to do the right thing behind the
wrong thing.

The case file has said why since before any of this: challenging is *"the escape
hatch being used as a door: cheaper than fixing the code and indistinguishable
from progress."* **Cheaper** is the whole of it. Challenging costs one call
carrying an id; fixing costs reading, writing and committing. When two outcomes
cost that differently, which one you get is decided by noise — which is exactly
the shape of `none_found` being free, one artefact along, and that one was
closed by making both outcomes cite what was read.

*Proposed:* `msg.challenge_tester` carries evidence. The criterion it claims is
contradicted must exist and belong to the batch, and the challenge must **quote**
— not paraphrase — a span of that criterion's text and a span of the test's
body. All three are mechanically checkable, and quote-not-paraphrase is the rule
`check_segmentation` already holds Liaison to.

It deliberately does not decide whether the contradiction is *real*.
`validators.py` states the line: "None of these say the choice was good. They say
it was legal." What it removes is the asymmetry — a session that must read both
rows before challenging has, by then, done the reading that would show it the
test is right. The legitimate sibling survives easily: in
`L1-DV-challenge-a-test-that-contradicts-its-criterion` the criterion says
"leaves its invoices in place" and the test asserts `invoices_for(account_id) ==
[]`. Quoting both is trivial when the contradiction is there.

*Blocked on:* a ruling, because it changes a verb's arguments in the graph. And
on model time: tool signatures are in every system prompt, so changing one
invalidates the recordings for **every** Developer case, not the two this
targets — six cases at five runs each to re-earn, not two.

---

## Assumptions

The settled column, rephrased so it can be wrong. Each of these is currently
believed and untested.

1. **Artefacts are sufficient compression.** A glossary, a constraint set and an
   area partition are a lossy-but-adequate index over a codebase nobody can hold
   in a context window. *If false, nothing else matters.*
2. **The structure carries what the model cannot.** An 8B model denied context
   sharing produces coherent output because the roles and artefacts hold what a
   larger context would have held.
3. **Directory layout is a good partition.** Somebody already chose it, usually
   for the right reasons; the dependency graph is for checking it, not replacing
   it.
4. **A funnel bounds multiplicity within a session.** One entry becomes
   statements, statements become items, items become tickets — each stage
   designed so the next sees one thing. *Believed; the frontier is where it does
   not hold.*
5. **Refusal is success.** A role that says "I cannot do this, here is who can"
   is the design working. Several existing cases score silence as failure, so
   this is asserted and contradicted in the same repository.
6. **Citation scoping is sufficient for drift.** Everything the system needs to
   notice is something it pointed at.
7. **A trust boundary is the right test for a new role.** Applied to git history
   and the internet; untested on the next case.
