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
is Critic and Vision Keeper, and "is it working out there", which is evidence that
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

### Onboarding is three questions before it is a pass over areas

Orient (Vision Keeper, the whole program: what it does for its user), define
(Terminologist, one word at a time from the project's own lexicon, with the
concordance pushed), then the per-area survey (Terminologist for what an area
adds, Architect for the rename counterfactual). Strict phases, derived from the
rows by `scheduler.onboarding_phase`, each written with the previous phase's
artefact in front of it.

*Consequence:* the unit of work is a question with its context assembled by the
harness, not an area with a grain list; a word that lives in five areas is
defined once, over the program. The per-area Vision Keeper pass is withdrawn (not
deleted) because the orientation is the same role asking the right question at
the right grain. Measured reasoning in `ONBOARDING.md`; the worklist that forced
it in `probes/cnt/WORKLIST.md` items 21–24.

*Consequence:* `onboarding_phases` is a setting, so `survey` alone -- the
pre-orientation design -- stays runnable for measuring one phase against
another, and every test of the area pass still tests the area pass.

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

### The scope role is Vision Keeper

The role answerable for what the project is and is not was renamed from
`vision` to `gatekeeper` in the first rename, because the job is the gate:
what is in, what is explicitly out, and the tickets cut from approved items.
The name said the gate and hid the other half, which is the half onboarding
opens with: identity, purpose, the non-goals, the rejection log, the account
of what a program is *for* -- the original design's "Vision: identity and
scope over time". **Decided 2026-08-23: the role is `vision_keeper`, "Vision
Keeper" in prose** -- it says both halves and keeps the gate. Done
mechanically and reviewably by `rota/tools/rename_vision_keeper.py` (109
files; the prompts directory moved; case ids `GK-` became `VK-`). Consequence:
every brief that names the role changed, so the recordings made against the
old briefs are invalid and were re-earned; old run databases keep
`gatekeeper` in their session rows and are re-onboarded rather than migrated.

### Intake has three answers and its brief offered two

`liaison/converse` decides what the principal just said. Its brief asked one
question -- "is this **chat** or **work**?" -- and answered ties twice over:
"Default to chat", and "When in doubt, chat." A question *about the onboarded
program* is neither, so it fell to the tiebreaker, and so did everything else.
Measured on the shipped brief, four maintainer questions and two work requests
against two models: `chat` was the answer to five of six, and the two controls
that pass are the two the tiebreaker happens to be right about.

That is the whole of why validation 2 had never run. The read-only route is
drawn three times in the graph, has a brief and a `.tools` file at each end,
and a probe that beat the monolithic dump 4-8 to 2-8 -- and driven through the
real loop against the click run with the model onboarding uses, Liaison
answered a maintainer's question by asking the principal to clarify it.

It also explains a failure nobody had connected to it. `L1-LI-segment` hands
Liaison "morning. we need SSO, but only if it works with our LDAP" and expects
statements; it has been 0/5 for a long time and its diagnosis in
`l1_liaison.yaml` was already right -- "a brief that can only be tuned in one
direction gets tuned until the other direction breaks". The direction it was
tuned in was chat, after a greeting regression, and the tiebreaker is where the
tuning ended up.

**Decided: an ordered test, not a default.** Three questions asked in order,
stopping at the first yes -- does it ask for something the program does not do
yet; is it a question about the program as it already is; otherwise chat --
with the first test given the discriminator that separates the two hard cases:
work is *told* to you, a question is *asked* of you.

*Consequence:* inquiry went from 0-1 of 4 to **4 of 4 on both models, in both
passes**, chat held at its existing rate, and llama's work column recovered
from 0-1 of 2 to 2 of 2. Naming the third branch in prose without touching the
tiebreaker -- the obvious fix, measured first -- moved inquiry to 2-3 of 4 on
one model, nothing on the other, and cost work on both. The branch was never
the missing thing; the tiebreaker was.

*And the cost, which turned out to be mostly something else:* the ordered test
looked like it overshot -- work requests coming back as questions -- and most
of that was the session giving two answers rather than choosing the wrong one.
A stray chat reply was voiding whole segmentations at commit; a session that
segmented was free to route the same message as well; and a session that routed
was free to chat about it. All three are the same fault, and guarding them
pair by pair missed the third until a case caught it 0/5. `answers_given` names
the three answers once and each channel declares which one it is. What is left
of the overshoot is one fixture, below.

Worth keeping separately: **two of my own edits to this brief caused
regressions that only the recording caught.** "Clarify only when you cannot
tell what they are asking *for*" reads as a narrowing and licensed exactly the
clarification `L1-LI-no-report-no-question` forbids -- a vague request is still
a request. The measurement that chose the ordered test had no vague-request
fixture in it, so nothing could have found this before the case ran.

### Two models disagreeing is a diagnostic, not a portability problem

The question that prompted this was the right one: prompts should not be model
dependent, and capability should just be capability. Eight arms of the intake
measurement, run interleaved on `llama3.1:8b` and `qwen3:8b`, say it almost
exactly.

    change                                  llama3.1:8b   qwen3:8b
    `vacuous` over `unfounded` / `dismiss`     best          best
    ordered test replacing the tiebreaker      0-1/4 -> 4/4  0-1/4 -> 4/4
    refusing an ask with empty refs            0/4 -> 4/4    fixed
    one answer per message, at the channel     fixed         fixed
    adding a three-owner worked example        worse         better

**Every edit that corrected a defect helped both models. The only edit they
disagreed about was one that added emphasis rather than correcting anything.**

So the rule is a check rather than a policy, and it costs nothing because both
models are already run:

- helps both -> ship it
- helps one, hurts the other -> do not ship. It is emphasis, not a fix, and the
  structural form has not been found yet
- helps neither -> the diagnosis was wrong

That third arm is the one that matters historically. The refs *paragraph* is
what llama disliked; replacing it with the refs *guard* in `sandbox.py` made
both models agree, and the paragraph came back out. `l1_liaison.yaml` has been
warning about this since the chat path landed -- "a brief that can only be
tuned in one direction gets tuned until the other direction breaks" -- and the
second model is what detects the tuning while it is happening.

*Consequence:* no per-model brief mechanism is needed and none should be built.
`llama3.1:8b` stays the recording model, because cassettes are evidence about a
prompt and re-earning the corpus buys nothing here; `qwen3:8b` stays the second
detector, which is the job it was already doing.

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

### The greeting that precedes a request

"morning. we need SSO, but only if it works with our LDAP" is a greeting and a
commitment in one sentence, and it was the fixture no arm of the intake
measurement made stable. Most of that turned out not to be classification at
all: `llama3.1:8b` segmented it correctly on turn one in every arm of the
ordered test, and the commit-time chat guard threw the segmentation away
because of a stray reply on turn five. That is fixed at the channel now, and
what the fixture measures from here is genuinely the classifier.

What is left, and worth measuring before anything is changed. Whether the
leading greeting is what does the remainder -- the same sentence without
"morning." is one fixture's worth of evidence and costs nothing. And why
`qwen3:8b` commits nothing at all on it, which is a wasted turn rather than a
wrong answer, and which the entry below turns out to be part of.

Not open as a brief question. Six prose attempts have now been spent on
Liaison's classification and the one that worked replaced a rule rather than
adding one, so the next attempt should be structural or should not be made.

### The worked example decided it, and one example was the answer

Worth keeping because the obvious reading was wrong twice.

The brief's example of the inquiry route was
`msg.ask_terminologist(refs=[], question='...')`, refused twice over -- there
is no `question` parameter, and empty refs are now refused at the channel. So
correcting it was not optional. It was also not free: with the examples
corrected *and* a three-owner example added, `llama3.1:8b` routed a **greeting**
to an owner and lost its work column, while `qwen3:8b` improved on chat. Two
models disagreeing about one edit, for the first time in this measurement.

What separated them was not the correction but the *salience*: every arm that
gave asking more room in the examples pushed llama to over-route, and the
broken example had been suppressing asks by failing. One corrected example and
no three-owner block scores at least as well as the shipped brief on both
models in both passes, and strictly better on `qwen3:8b`'s chat column. That is
what shipped.

Recorded because it nearly went the other way: a brief whose score depends on
one of its examples not working would have passed every check this project has,
and the only thing that caught it was scoring an ask with empty refs
separately from an ask.

### A confirmation can name a statement nobody wrote

Found while reading the sessions that scored as doing nothing. Handed
"morning. we need SSO, but only if it works with our LDAP", `qwen3:8b` sent
`msg.confirm_principal(refs=['s1'])` three turns running without ever calling
`brief.segment`. The message went out. `receipts` is empty. The principal is
now holding a gate on a statement that does not exist, and the ratification
that answers it will refer to nothing.

The channel checks the *shape* of a ref and deliberately not the row --
"checking the shape rather than the row keeps this honest for ids written in
this same session, which are not in any table yet". That reasoning is right and
the conclusion is one step short: a row written in this session is in
`ctx.writes`, so the honest check is *exists in a table **or** was staged
here*, which refuses exactly this and nothing else.

Open rather than done, for one reason worth stating: a new refusal changes what
a session does on its *next* turn, and every cassette recorded past that point
stops matching. That is how the ledger guard's cause stayed hidden for a week.
The guard is cheap; re-earning eleven L1 cases is not, so it goes in with a
re-record and not beside one.

`L1-LI-a-question-the-roles-could-not-answer` is the third member of this
family and the oldest -- `clarify` reaches the principal five runs out of five
carrying no refs, and its case says outright that prose has been tried and the
fix will have to be structural. It is not the same guard: `clarify` has a
`question` field, so an empty refs list is thin rather than empty, and the
refusal would have to be situational -- refs are obligatory *when the wake
carried some* -- which is `sandbox.situational`'s shape and not `stage`'s. The
`ask` guard is the precedent that makes it tractable, not the fix.

### "Should we build this?" is a fourth kind of intake, and there is no branch for it

Intake decides three things: chat, a question about the program as it already
is, or work. A principal asking **"should we add xyz?"** or **"is this viable?"**
is none of them. It is not chat. It is not a question about what exists -- it is
about something that does not. And it is not work, because nothing has been
decided and segmenting it would put a statement in front of the principal to
ratify that they were asking about rather than asking for.

Under the ordered test it falls to chat, which is the tiebreaker doing what
tiebreakers do.

The design stories do not cover it either. They have "how does deletion handle
search results right now?" and "what happens after this batch?" -- both about
what is, one about the present and one about the plan. Nothing about appraisal.
So this is a gap in the spec and not only in the build.

What it would be, if built: the same read-only fan-out as an inquiry, and a
different shape coming back. Vision Keeper on whether it is in scope and what
it would contradict, Architect on what would break and what outside things
depend on the parts it touches, Terminologist on whether the words already mean
something else here. Every one of those is a *judgement*, which is what
separates it from an inquiry, and none of them is a commitment, which is what
separates it from work.

Two things to settle before building it. Whether an appraisal may write --
`ledger.log` is the honest home for "we would be assuming X", and law 10 says
inquiry writes nothing, so either appraisal is not inquiry or the ledger entry
waits for a decision that may never come. And whether a favourable appraisal
should flow into work without the principal saying so again; the answer is
almost certainly no, because "that sounds fine" is not a commitment, and the
whole ratification gate exists to keep those apart.

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

### The ledger's prose field is named like a flag

`ledger.log(about_ref, about_table, default_taken)` wants a sentence: what
was assumed where the criteria were silent, and what it would cost to be
wrong. `default_taken` reads as a yes/no question -- *was* a default taken?
-- and models answer it as one. Measured over the recorded corpus,
**1,052 of 1,209 calls (87%) pass `True` or `False`**, and it is not one
case repeated: Developer across five modes, Vision Keeper across three,
Terminologist, Tester.

The corpus also contains the natural experiment. `developer/batch_start` is
the only mode-brief that names what the field should contain -- "log the
choice and the default you took" -- and it is the only mode above a fifth
prose: 108 real sentences. The modes whose briefs say nothing about the
ledger are unanimous the other way: `tests_failing` 139 bools and no
strings, `verdict_failed` 163 and none, `exhausted` 75 and none. The name
alone gets a flag; the name plus a sentence about its content gets prose
two times in five.

Three consequences, and the third is the one that is not obvious. The
principal's agenda fills with entries reading "True". A milestone is
quiescence with an *empty* ledger, so the pollution is load-bearing. And
the row id is `sha256(about_table|about_ref|default_taken)`, derived so
that a cold retry upserts instead of duplicating -- with the field
constant at `True`, the id collapses to (table, ref), so two genuinely
different assumptions about one ticket silently become one row. The
deduplication built to protect the principal's attention is discarding
evidence.

**Not a guard.** Refusing non-strings was tried twice and reverted twice.
The second attempt is why the cause is now known: it crashed on
`default_taken=False` with an AttributeError, the session died mid-way,
and every cassette recorded after that point stopped matching -- which is
what made the first attempt look like it had no cause, since the composed
prompt really was byte-identical and the divergence was in a later turn.
Beyond the bug, a gate that refuses 87% of real calls is not a bounded
refusal, it is an outage, and this system's own law says a gate the model
cannot satisfy is a twelve-turn loop.

**Open, because the fix has a cost and a cheaper rival.** Renaming the
parameter -- `assumption=`, which cannot be answered `True` without
absurdity -- changes a signature that appears in every brief's toolkit,
and every cassette with it. Teaching it in the *base* brief instead costs
one paragraph and invalidates only the roles that hold the operation. The
corpus says the second works two times in five; nothing yet says what the
first does. What decides it is the same bench A/B the challenge rename is
waiting on: one situation, one model, one word changed in the signature.

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
