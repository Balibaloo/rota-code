# rota — the engagement, and the laws

Every other document in this repo presupposes this one. `HANDOFF.md` opens at the
laws; `schema.sql` opens at the tables; the prompts open at "You are Vision Keeper."
Not one of them says what the whole thing *is*, which is why the vocabulary drifted
in the first place — there was no level above the parts for the parts to hang from.

Two parts, then. **L0**: what this is. **The laws**: what it may never do.

---

## L0 — the engagement

> **An engagement is the whole relationship with one principal, from their first
> ask to a milestone.**

Everything in the system is a fragment of that relationship, and every term below
means something only inside one.

**The principal** is the person who wants the software and rules on it. Singular,
technical, and holding final authority over what the work is for. *Principal* in
the principal–agent sense — the party on whose behalf the agents act — not in the
sense of seniority. They are not a customer being served and not a manager being
reported to. They are the one who knows what they want and is the only one who
can say whether they got it.

**The team** is nine roles that never share context and communicate only by
artefact and message. Each is answerable for one thing. Each is woken, acts, and
ends, with no memory of having been woken before. That is not a limitation being
worked around: it is what makes a role's output attributable to its brief rather
than to the accumulated drift of a long conversation.

The nine, and what each is answerable for:

| role | answerable for |
|---|---|
| **Principal** | wanting it, and ruling on it. Not a role — the root of the message DAG, and the whole that stayed whole while the roles are fragments of their attention |
| **Liaison** | the conversation with the principal, and the clarity of everything crossing to and from them |
| **Vision Keeper** | what the project is, and isn't — over time |
| **Terminologist** | one meaning per word |
| **Architect** | the system holding together, and its outward promises |
| **Tester** | what "done" means, written so a machine can check it |
| **Developer** | making it exist |
| **Critic** | whether it was done, and done well |
| **Researcher** | what is true outside this repository, and where that is written |

**The understanding loop** — *hear, shape, agree* — turns what was said into what
is meant. The principal speaks; Liaison records it verbatim and cuts it into
statements; the principal confirms the cut; Vision Keeper, Terminologist and
Architect each read the same words against different artefacts and write what
they mean for scope, for terms, for structure; the principal approves.

**The delivery loop** — *plan, build, judge* — turns what is meant into what
exists. Vision Keeper slices tickets, Terminologist writes criteria in glossary
terms, Architect groups tickets into batches; a batch is built, tested, judged
for intent and then for structure, and merged.

**Reconciling** is running the first loop's discipline again when the second finds
the world has changed. There is no third loop and no special path for it.

**Everything outside the engagement arrives through one role.** The Researcher
answers questions of fact about things this repository is obliged to — a
specification, a licence, an advisory — and owns nothing but its own record of
what it read. Nothing it writes reaches the model on its own: the role that asked
decides whether to cite it, so a wrong answer stays a wrong row instead of
becoming a constraint that blocks real work forever. It is contained rather than
distributed for one reason, and it is the same reason the roles are separated at
all: a boundary you can see is a boundary you can check.

**A milestone** is quiescence with an empty ledger: no predicate fires and no
assumption is open. There is nothing to "close" — a milestone is a state the
system is observed to be in, not an event anyone declares.

### What an engagement is not

- **Not a chat.** The transcript is an artefact with provenance, not history.
  Nothing accumulates in a context window; everything accumulates in the database.
- **Not a project plan.** Time is not a concept here. Order and dependency exist;
  dates, durations and deadlines appear nowhere.
- **Not a workflow.** Nothing is "assigned". The frontier is derived from state
  every pass, so residual work is re-computed rather than remembered.

---

## The laws

Numbered as in the design. Where a law has been amended, the amendment is marked
and the reason given — a law that changed silently is a law nobody can rely on.

### 1. Single writer — one writer per row

Every artefact has exactly one writing role per row. Journals — the transcript,
the decision record, the ledger — may have several writers but one author per
entry, append-only, which is the same property stated for a table whose rows are
independent.

Per-table ownership is the strict form. The backlog is three tables:
`tickets` (Vision Keeper), `criteria` (Terminologist), `batches` (Architect).

> **Amended.** Priority moved from `batches` to `items`. It is a property of what
> the principal wants, and what they want is an item — which makes `batches`
> single-writer in the strict sense, and gives law 9's "priority moves batches
> whole" for free: there is no per-batch number for a recomposition to preserve.

A batch's *runtime state* — running, deferred, merged — is not artefact content
and has one writer that is not a role: `rota/lifecycle.py`. Nothing about it is
decided.

### 2. Conclusions travel; reasoning stays home

Judgement crosses a role boundary only as structured findings — ids and states.
Verdicts, receipts, per-item rulings. The reasoning is written into the decision
record by whoever decided, and reached by following a ref.

> A finding is `{constraint_id, status, grain}` and has no `why` column. The
> schema enforces the law rather than the prompt asking for it.

### 3. Contact lists are derived, not designed

A message routes to the writer of the artefact holding the answer. Two clauses:

- **ask** — the writer of a judgement artefact this role reads
- **inform** — a role that reads a judgement artefact this role writes

**Fact artefacts** — transcript, code, decisions, ledger — generate no contact:
reading them yields evidence, not judgement, so there is nobody to ask.

Nothing here is dynamic. Contacts are computed once at load from the read/write
edges and fixed. The point of deriving is that no second, hand-maintained list
exists to disagree with the structure. The graph's declared message edges are the
*oracle*: a boot assertion requires them to equal the derived set.

> **Amended.** The one declared exception — `architect → critic: finding` — is
> gone. It was underivable by construction: Critic must not read the model, so
> the conclusion had to be *pushed*. With the review order flipped, Architect's
> judgement is a gate rather than an input, so it has nobody to tell; the verdict
> lands as rows the merge gate reads, and the scheduler is not a role. **Law 3
> now derives every message edge with no exceptions at all.**

**Being woken is the assignment.** No role asks, or is asked, what to work on.
Dispatch is the stateless scheduler reading state — a query, not a conversation.
The one legitimate schedule question is the principal's, and it arrives as a
read-only inquiry.

### 4. A session is one message

Woken by exactly one inbound message or one predicate; reads its working set;
emits writes, messages and a receipt; ends. All writes commit atomically at
session end, or the session never happened.

**Carve-out for the codebase.** Git commits are outside the transaction, so the
database *lags* the worktree. A session that committed code and then died leaves
the two out of step. That is not corruption — the batch's trigger is still on the
frontier — but a cold role reads criteria, probes code, and has no reason to run
`git log`, so it would redo finished work. Boot reconciles `batches.head_commit`
against real HEAD and hands the divergence to the woken role.

**Failure is bounded.** A crashed session leaves its trigger open with its attempt
count raised; past `message_attempt_cap` the message is quarantined. Semantic
failures resolve themselves; these are infrastructure ones, and without a bound
the scheduler wakes the same role with the same message forever.

### 5. Completion is the default; suspension is a cache

A suspended checkpoint must always be safely discardable. Invalidation is
mechanical: the working set's version stamps. Receipts — artefact and row ids
plus version bumps, refs and never prose — allow patched resume; overlap with the
plan forces reconstruction.

### 6. Escalation only climbs

Developer → Architect → Vision Keeper → principal. Budget exhaustion escalates; only
exhaustion *at the principal* converts to a ledger assumption. Cycles collapse by
routing the counter-question into the suspended session; roles are single-instance.

> Exhaustion escalates one rung at a time, because the usual *reason* a loop
> exhausts itself is not knowing who to ask — and going straight to the principal
> skips the two people who could have answered. The rung is derived from what has
> already been sent about the batch, not stored: a stored rung is a second record
> that can disagree with the messages that *are* the escalation.

### 7. Budgets are structural

Every cap is declared in `rota/config.py` and owned by the principal. A number
written into a predicate is a decision made by whoever typed it, at a moment
nobody remembers, that nobody can change without reading code.

`loop_cap` and `interrupt_cap` are both "how many times before we stop", and they
are deliberately not one number: **one spends compute and the other spends the
principal.** Different scarcity, different right answer, and the moment they share
a name someone tunes the cheap one and changes how often a person is interrupted.

The reframing discipline applies at every cap level: any touch after the first
must reframe — decompose, or offer a concrete default they can veto — never
repeat the question.

> **Amended.** Caps are no longer phase-dependent. `merge_gate` is a setting the
> principal toggles, not a value derived from how far along the work is: trust
> should not increase on a schedule.

### 8. Gates are predicates, not judgement

- **L1 (fidelity)** — the principal ratifies the segmented statements: *did I hear
  you right*. Segmentation is at **principal granularity** — one thing they asked
  for is one statement, never irreducible atoms. Downstream roles re-decompose
  into their own artefacts.
- **Signoff (interpretation)** — per-item approval of the problem statement's
  in-scope and out-of-scope items, presented as one document. No batch schedules
  unless its item's approval postdates the item's last amendment. A lineage's open
  assumptions are presented at its gates: nothing ships whose assumptions the
  principal never saw.
- **The merge gate** — harness, then Critic, then Architect. Cheap checks loop;
  expensive checks run once. Most failures are failures of intent, so screen there
  first and never pay for a constraint review on work that does not do what was
  asked.

A gate is not machinery. It is what the loop looks like when the principal has not
answered yet.

### 9. Amendment ⇒ revocation ⇒ cascade

Any write to an approved item drops it to pending and stops its batches.
Resolution descends the refs DAG through each artefact's owner in dependency
order before the Developer resumes and elects amend or restart.

Cascade wakes are scheduler events carrying receipts. No role-to-role notification
exists anywhere in the cascade: the scheduler walks the refs DAG and summons each
owner itself.

**Priority is a different lever than scope, and never blurs into it.** Batches are
complete feature sets, immutable once formed. A priority change alters no approved
content, trips no revocation, involves no Architect, and moves batches **whole**.
Only a scope change may recompose one.

**Preemption:** if a reorder bumps a batch ahead of the running one, the scheduler
kills the running batch's environment outright — processes and ports die with it;
half-dead environments are forbidden — and discards its checkpoint. The worktree
and its commits persist as *deferred* work. Commit-first is what bounds the loss:
an uncommitted change never existed.

### 10. Inquiry is free

Every principal message is handled read-only first. A readonly session may read
and answer but not write, and therefore cannot revoke anything or invalidate any
checkpoint. The write is *unavailable*, not session-fatal: a readonly sandbox is
built without writers at all, so the function does not exist and a model reaching
for one gets an ordinary tool error.

Only a ratified amendment to an approved item escalates an inquiry into change.

> This is also why **intake lands while the system is stopped or halted.**
> Recording what the principal said costs nothing and revokes nothing, and a
> system that stops listening because it stopped working is just broken.

### 11. Provenance is explicit

Entries in the model, glossary and problem statement are `decided` — the reason on
file, written by the decider *in the same session as the decision*, with no
recording step and no scribe role — or `observed`, extracted from an onboarded
codebase: found, not chosen. Challenging an observed entry forces its first
decision. The decision record accretes lazily.

> **Amended.** A third value, `cited`: found outside the repository, attributable
> to a source. It is neither of the other two — nobody chose it and it was not
> extracted from the code — and it is the only provenance that can become false
> without anyone touching the project, because the page it rests on can change.
> A `cited` entry carries `source_refs` to the reference rows that support it,
> and a reference carries the passage as well as the URL: elsewhere conclusions
> travel and reasoning stays home, but for an outside source the passage *is* the
> evidence, and a confident sentence with a link after it is indistinguishable
> from an invention.

> A ledger entry is resolved by a decision that names it, in the same commit, and
> by nothing else. There is no `ledger.resolve`: an assumption that could close
> itself would void "no milestone with open assumptions", which is the only thing
> making the ledger more than a list of regrets.

### 12. Constraints protect external commitments only

Blast radius exits the module: persisted data, published APIs, high fan-in
contracts, compliance. Each constraint declares **bindings** — the addressable
grain it governs. Structural review triggers by mechanical intersection of
diff-touched grains with bindings.

**Constraint zero** — *"this codebase is not yet understood"*, bound to the repo
minus surveyed areas — makes ignorance safe on day one. It is starved by positive
survey records ("surveyed, no constraints found" counts), never removed by
judgement.

> Architect also records an **expected touch set** per batch: paths always, symbols
> where confident, with the confidence written down rather than implied. It is a
> *prediction*, never a permission — nothing rejects a diff for straying outside
> it. Its job is to make "was this change incidental?" answerable at review time
> instead of arguable. A prediction that could block work would quietly become a
> permission system nobody designed.

### 13. Time is not a concept

Order and dependency exist. Dates, deadlines and durations appear in no artefact,
no plan and no prompt.

---

## How the laws are enforced

Not by asking. Each of these is a check that fails the build:

| law | check |
|---|---|
| 1 | `graph.check_writers` — every artefact has a writer, and `batches` has exactly one |
| 2 | `findings` has no `why` column; message bodies carry refs |
| 3 | `graph.check_contacts` — derived set equals declared set, with zero exceptions |
| 4 | `db.session_commit` is one transaction; `boot.reconcile_worktrees` for the carve-out |
| 5 | `scheduler.sweep_checkpoints` against `artefact_versions` |
| 6 | `predicates.exhausted` climbs `LADDER` one rung at a time |
| 7 | `config.SETTINGS` — reading an undeclared key is an error, not a default |
| 8 | `lifecycle.mergeable` returns the reason, in review order |
| 9 | `scheduler.cascade_wakes`; `problem.prioritize` writes with `amends=False` |
| 10 | `sandbox.build(mode="readonly")` constructs no write functions at all |
| 11 | `provenance` is `NOT NULL CHECK` on every artefact that has one |
| 12 | `check_structure` — a non-owner may take every row, or bodies, never both |
| 13 | no date, duration or timestamp column exists in `schema.sql` |

And one check that is about the laws themselves: **every state a row can be in
must have a way out.** A state with no predicate draining it is a place work stops
silently — and quiescence is defined as "no predicate fires", so a dead end makes
the system report itself *finished* while work has been abandoned. The invariant
we rely on would pass. `python -m rota.core.predicates` is the check.
