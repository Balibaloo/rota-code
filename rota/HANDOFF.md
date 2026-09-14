# LLM Team Development Framework — Design Handoff

> **STATUS: PARTIALLY IMPLEMENTED.** The machine exists; the roles do not.
> Built and under test in `rota/`: the graph as loadable wiring, the schema, the
> atomic session commit, the scheduler (frontier, six predicates, claims,
> cascade, boot), the sandbox (per-role namespaces built from edges), the `TOOL:`
> parser, the session runner against a local model, the fixture loader and the
> cockpit. Not built: role prompts, T1 role-contract cases, T2 arcs against real
> models, onboarding/survey.
>
> Amendments below carry a **[A]** marker where this document was changed after
> the design session that produced it. Each was a challenge raised against the
> spec and ruled on, per §6 — none was quietly weakened. Git holds the record of
> why: the commit that made the change carries the challenge.

Companion to `team-graph.html` (the interactive graph: roles, artefacts, edges with
verb/noun/scope grammar, ERD refs, three stories that validate the *design's* internal consistency (every
operational edge exercised by at least one narrated case — this proves the graph
coherent, not any implementation correct), coverage tool). This
document carries what the graph cannot: the laws, the rulings, the migration plan,
and the open questions. Together they are the complete state of the design. The
conversation that produced them is *not* required reading — that is the point.

The next session is a cold-awoken role. It reads artefacts, not transcripts.

---

## 1. What this is

A team of LLM roles that develops software for a single technical client. Roles
never share context. Each role owns (single-writer) a small set of artefacts and
communicates by messages. The client holds final authority. Cost and calendar
time are explicitly **not** concepts in this system — ordering is; dates are not.

Two loops: the **understanding loop** (Hear → Shape → Agree) and the **delivery
loop** (Plan → Build → Judge), bridged by **Reconcile** (re-runs the first loop's
discipline when the second discovers the world changed) and drained by the
assumption ledger through the client gates.

## 2. The laws (violate none of these)

1. **Single writer — one writer per *row*.** [A] Every state artefact has exactly
   one writing role per row. Journals (transcript, decision record, message log)
   may have multiple writers but one author per entry, append-only — which is the
   same property, stated for a table whose rows are independent. The backlog's old
   three-writer risk (open q. 2) is closed by the same reading: it is three tables,
   `tickets` (Vision), `criteria` (Domain), `batches` (Architect), each with one
   writer. Per-table ownership is the strict form of per-row ownership.
2. **Conclusions travel; reasoning stays home.** Judgement crosses role
   boundaries only as structured findings (IDs + states): verdicts, receipts,
   per-item flags. Reasoning is written into the decision record by its author
   and reached only by following a ref.
3. **Contact lists are derived, not designed.** [A] A message routes to the writer
   of the artefact holding the answer — questions, challenges, and escalations
   alike. Nothing here is dynamic: contacts are computed once at load from the
   read/write edges and fixed thereafter. The point of deriving is that no second,
   hand-maintained list exists to disagree with the structure. Two clauses, plus
   two qualifications the implementation forced:
   *ask* — the writer of a judgement artefact this role reads; *inform* — a role
   that reads a judgement artefact this role writes. **Fact artefacts** (transcript,
   code, decisions, ledger) generate no contact: reading them yields evidence, not
   judgement, so there is nobody to ask. **Exceptions** are listed in the graph with
   reasons — currently one, `architect → critic: finding`, which is underivable by
   construction because Critic must not read the model. The graph's declared message
   edges are the *oracle*: a startup assertion requires them to equal the derived
   set, so a disagreement is a finding rather than a silent divergence. `Interface` is reached from below only via an owner reporting blocked.
   **Being woken is the assignment**: no role ever asks, or is asked, what to
   work on. Dispatch is the stateless scheduler reading `Planner`'s artefact —
   a query, not a conversation — so no role holds or needs schedule knowledge.
   The one legitimate schedule question is the client's, and it arrives as a
   consult-mode inquiry.
4. **A session is one message.** Woken by exactly one inbound message (or gate /
   schedule event); reads its working set; emits writes + messages + receipt;
   ends. All writes commit atomically at session end (one SQLite transaction) or
   the session never happened.
   **[A] Carve-out for the codebase.** Git commits are outside the transaction, so
   the database *lags* the worktree: a session that committed code and then died
   leaves the two out of step. This is not corruption — the batch's trigger is
   still on the frontier and the Developer wakes again — but a cold role reads
   criteria and probes code and has no reason to run `git log`, so it would
   duplicate finished work. Boot therefore reconciles `batches.head_commit`
   against real HEAD and hands the divergence to the woken role. The index must
   also be clean at handoff, so "what did this session produce" stays answerable.
   **[A] Failure is bounded.** A session that crashes leaves its trigger open with
   its attempt count raised; past a configured cap the message is quarantined.
   Semantic failures resolve; these are infrastructure ones — model eviction, a
   hung tool call, a stream that dies after retries — and without a bound the
   scheduler wakes the same role with the same message forever, across restarts
   too.
5. **Completion is the default; suspension is a cache.** A suspended checkpoint
   must always be safely discardable. Invalidation is mechanical: the working
   set's version stamps. Receipts (artefact + entry IDs + version bumps — refs,
   never prose) allow patched resume; overlap with the plan forces reconstruction.
6. **Escalation only climbs.** Developer → Architect → Vision → Client. Budget
   exhaustion escalates; only exhaustion **at the client** converts to a ledger
   assumption. Cycles collapse via resume-with-question (route the counter-question
   into the suspended session; roles are single-instance).
7. **Budgets are structural — and phase-dependent.** Hop budget ≈ 2× ladder
   depth (tripwire, not quota). The client-touch cap is a config value per
   phase: **high (effectively generous) during initial shaping and onboarding**,
   where interviewing is the work and the client expects rounds of questions;
   tightening to the low steady-state default (2 consecutive non-closing touches
   per blocker) once the problem statement exists. The reframing discipline
   applies at every cap level: any touch after the first must reframe
   (decomposition or a vetoable concrete default), never repeat the question.
8. **Gates are predicates, not judgement.**
   - *L1 (fidelity)*: client ratifies the segmented statements — "did I hear
     you right". Segmentation is at **client granularity** (one thing they asked
     for = one statement), never irreducible atoms; downstream roles re-decompose
     into their own artefacts.
   - *Client Signoff (interpretation)*: per-item approval of the problem
     statement's scope items and non-goals, presented as one document ("lgtm"
     approves everything raised). **No batch schedules unless its item's approval
     postdates the item's last amendment.** Open assumptions of a lineage are
     presented at its gates — nothing ships whose assumptions the client never saw.
   - *PR gate*: optional client review mode, invisible to all roles (verdicts
     simply take longer).
9. **Amendment ⇒ revocation ⇒ cascade.** Any write to an approved item drops it
   to pending and stops its batches. Resolution descends the refs DAG through
   each artefact's owner in dependency order (model → backlog → schedule) before
   the developer resumes and elects amend (keep worktree, rebuild understanding)
   or restart (wipe both).
    Cascade wakes are scheduler events carrying receipts — no role-to-role
    notification messages exist anywhere in the cascade; the scheduler walks
    the refs DAG and summons each owner itself.
    **Priority is a different lever than scope, and never blurs into it.**
    Batches are complete feature sets, immutable once formed: a priority change
    alters no approved content, trips no revocation, involves no Architect, and
    never recomposes a batch — it moves batches **whole**. The target batch is
    found mechanically by refs (statement → item → batch); Vision writes the
    priority onto the backlog entry; the receipt cascades to Planner, who
    reorders whole batches. Only a scope change (via revocation) may recompose
    a batch. **Preemption:** if the reorder bumps a batch ahead of the running
    one, the scheduler kills the running batch's environment outright —
    processes and ports die with it; half-dead environments are forbidden — and
    discards its checkpoint. The worktree and its commits persist as *deferred*
    work (commit-first bounds the loss: an uncommitted change never existed).
    A deferred batch later resumes as a cold session in its surviving worktree;
    a newly started batch always gets a fresh worktree, never a reused one.
10. **Inquiry is free.** Every client message is handled read-only first.
    Consult-mode sessions may read and answer but not write — therefore cannot
    revoke anything or invalidate any checkpoint. [A] The write is *unavailable*,
    not session-fatal: a consult sandbox is built without writers at all, so the
    function does not exist. A model reaching for one gets an ordinary tool error
    and carries on. Only a ratified amendment to an
    approved item escalates an inquiry into change.
11. **Provenance is explicit.** Model/glossary/problem entries are `decided`
    (authored reason on file, written by the decider *in the same session as the
    decision* — no recording steps, no scribe role) or `observed` (extracted from
    an onboarded codebase; found, not chosen). Challenging an observed entry
    forces its first decision. The decision record accretes lazily.
12. **Constraints protect external commitments only** (blast radius exits the
    module: persisted data, published APIs, high fan-in contracts, compliance).
    Each declares **bindings** — the addressable grain it governs (paths,
    symbols, tables, routes). Structural review triggers by mechanical
    intersection of diff-touched grains with bindings. **Constraint zero** ("this
    codebase is not yet understood", bound to repo minus surveyed areas) makes
    ignorance safe on day one; it is starved by positive survey records
    ("surveyed, no constraints found" counts), never removed by judgement.
13. **Time is not a concept.** Order and dependency exist; dates, deadlines, and
    durations do not appear in any artefact, plan, or prompt.

## 3. Roles (7) and artefacts

| Role | Owns (writes) | One line |
|---|---|---|
| Interface | transcript (append), brief (segment/ratify) | Only role that sees the client. Records, broadcasts, harvests, dedupes, orders, translates. Reflow (reorder-for-output) lives here exclusively. Never interprets, never invents questions. |
| Vision | problem statement (items, non-goals, approval state), rejection log | Identity and scope **over time**: checks every intake against prior refusals; notices expired reasons; slices tickets from approved items. |
| Domain | glossary + business rules | Canonical meaning. Criteria are written in glossary terms. |
| Architect | system model (constraints + bindings), batch grouping | Feasibility; groups tickets into batches (collision judgement); emits conformance **findings** to Critic (constraint ID + satisfied/violated, no reasoning). |
| ~~Planner~~ | — | **[A] Dissolved.** Its entire output was a topological sort of Architect's declared dependency facts — a deterministic function, not a judgement. Ordering is now scheduler code (`graphlib.TopologicalSorter`); an unsatisfiable set of deps (a cycle) wakes Architect with the conflicting facts. The schedule artefact survives as derived state that no role owns, and Interface gained a read of it so client ordering questions are still answerable. Removing it took four T1 cases with it. |
| Tester | test suite | **[A] New.** Writes executable tests from criteria, before the diff exists and without ever seeing it. Note its isolation is *temporal*, not informational: Critic can read everything Tester reads, so the only thing making these tests intent rather than description is that they were written first. Do not merge the two roles. A failing test returns to Developer directly (cap 10, then escalate by the ordinary routes); Developer or Critic may dispute a test via `challenge` to Tester. |
| Developer | codebase (branch/worktree per batch), diffs | Woken per batch, cold. Questions route by artefact: terms → Domain, criterion/scope → Vision, constraints → Architect. |
| Critic | review verdicts | **Information-starved on purpose**: reads batch criteria + batch tests + batch diff only. [A] It judges the diff *given* the tests, and may challenge Tester; it does not relitigate criteria. Never the reasoning, escalation threads, or client rulings. Judges intent conformance; composes Architect's structural finding without learning why. |

Historian was dissolved: recording belongs to deciders (law 11); surfacing prior
refusals belongs to Vision (identity); the decision record survives as a
multi-writer append-only journal.

**Shared artefacts:** backlog (tickets + criteria + batches; three writers —
flagged risk, see §7), assumption ledger (any role logs; Interface reads as the
agenda for the next client conversation; engagement cannot close non-empty),
decision record, message log.

**Scope grammar** (every read/write edge carries verb + noun + scope):
`none < single < batch < index < window < delta < query < full`. `full` is
allowed only for a role consulting its own artefact before amending — a
restriction about **authority**, not cost.

**[A] `full` means the full *index*, never the full text.** Glossary terms and
constraints carry a one-line headline alongside their body; a `full` read returns
ids plus headlines, and bodies are fetched singly. Nothing about "artefacts
plateau" was ever enforced — it was an assumption with no mechanism, and an
onboarded monolith could yield hundreds of observed constraints. Two levers keep
an 8k budget viable at any size: the index/body split, and — when even the index
grows — filtering it by binding intersection (constraints) or term occurrence
(glossary). Filtering is *principled*, not economising: a constraint that does not
bind the modules in play genuinely does not apply there. A role never receives a
silently clipped list.

**[A] Nothing deletes; scope does the work.** Superseded statements and resolved
ledger entries are excluded from index reads rather than removed. Genuine
compaction — retiring a constraint — is a *decision* with an author and a reason
(law 11), so it is client-gated, never a background sweep.

## 4. Runtime

- **[A] Frontier = open message tips ∪ tick predicates evaluated against current
  state.** The second half is not optional. An approved item with no tickets is
  not a message, it is a *state*; nothing would ever wake Vision for it. Because
  the predicates are re-evaluated every pass, residual work cannot be lost —
  deferred batches, half-sliced items, criteria-less tickets are all re-derived.
  That is also *why* the scheduler is disposable: pending work was never held in
  memory to lose. The system is, in effect, a fixpoint engine: it runs until state
  stops implying work. One invariant covers every residual-work bug at once:
  **at quiescence, no predicate fires.**

  The six predicates, each a pure query:
  *round-close* — every recipient of a broadcast has committed and its whole
  subtree is terminated (a round exists for one reason: dedupe, which is
  impossible if Interface wakes per report);
  *slicing* — an item approved past its last amendment with no tickets, fired per
  gate result rather than per item;
  *criteria* — tickets without criteria, fired per item so siblings cannot
  contradict each other;
  *batch-start* — schedulable batch, ordered first, nothing running;
  *survey* — onboarding, one elected area at a time, Domain → Architect → Vision;
  *agenda* — on client presence with open ledger entries or gates awaiting a
  verdict, wake Interface to present what is blocked on the client. Presentation,
  not a gate: the client may defer indefinitely and keep working. Deferral costs
  are deferred, not waived — open assumptions reappear at each of their lineage's
  gates.

- **Message DAG.** Every message refs its cause. Roots: client utterances, gate
  events, schedule ticks. Active path = unterminated chain. The scheduler (infrastructure, not a role, ~200 lines) picks one tip
  per Planner's order, wakes one role, repeats. **The scheduler is stateless and
  disposable by design**: it holds nothing — the frontier is a query, the
  schedule is Planner's artefact, claims and checkpoints are rows. Killing and
  restarting it at any moment loses nothing (this is a required property with
  its own test, TESTS.md T0-S3), and it is what makes hand-rolling it safe: the
  code can be deleted and rewritten freely against the database contract. Quiescence = empty frontier +
  no schedulable batches = valid idle.
- **Boot is not special.** All framework state lives in `.rota/` inside the project
  the tool is opened in. [A] Seven steps, then the ordinary loop — assertions
  before state, so a code/graph disagreement stops the system before it touches
  anything:
  **0.** graph assertions (namespace exports == edges; derived contacts == declared);
  **1.** folder present → boot, absent → onboarding initiation (§5);
  **2.** reap stale claims — a session live when the process died still holds one,
  and "the session never happened" is true for rows but not for the claim, which
  was written before it ran;
  **3.** reap orphan processes — spawned runtimes outlive their session and §9
  forbids half-dead environments;
  **4.** reconcile worktrees against `head_commit` (law 4's carve-out);
  **5.** sweep checkpoints against version stamps;
  **6.** quarantine messages past their attempt cap;
  **7.** continue.
  There is nothing to "continue" *to*: the frontier is the state, so reconstructing
  it is the entire recovery, and boot and steady state run identical code. A
  crashed session never happened.
- **Interrupts:** intake always lands; consult mode answers questions with zero
  side effects; ratified amendments trigger law 9. Unratified pending statements
  freeze nothing (superseded earlier rule).
- **[A] Push vs pull.** The working set is *pushed* into the prompt; tools are for
  going deeper than the push. Having `model.consult()` available does not mean a
  cold session will call it, and a role that re-derives what it was already given
  wastes a turn. For survey specifically the minimal push is the current area plus
  the constraint and term index for *adjacent clusters* in the dependency graph —
  adjacency is what makes it minimal rather than arbitrary.

- **Tooling model:** the code-execution pattern. Each role's session gets one
  tool (run code in a sandbox) plus a per-role API module that *is* its working
  set — scope adjectives compile to function signatures; a missing edge is an
  ImportError. [A] Built, and literally true: the namespace is *constructed* from
  the role's edges, so an ungranted capability was never created. Signatures are
  derived from the implementations and advertised in the prompt, and arguments are
  validated at the sandbox boundary — an invalid value that reaches SQLite raises
  inside the transaction and takes an otherwise sound session down with it. Intermediate data stays in the sandbox. Custom `TOOL:` text
  protocol at the `complete()` seam; provider-native function calling is an
  optional backend. MCP is a possible later transport, not a dependency.

## 5. Onboarding (existing projects)

Onboarding triggers when the tool is **opened inside a project** whose
framework state folder does not yet exist — the tool attaches to the project
and stores all its state (database, worktrees, config) in that folder; it is
never "pointed at" a repo from outside. Initiation then runs via Interface
(interview: intent, trust map,
what-changes-next ordering, least-familiar areas, upfront-vs-lazy election —
client's choice, per area). **[A] Areas come from graph partitioning, not bin-packing.** The mechanical index
yields a dependency graph (imports, calls, fan-in); areas are cut where the edges
are thinnest, subject to a size cap — a min-cut problem, still fully
deterministic. This is the step that makes cross-area constraints *rare by
construction* rather than something to mitigate afterwards: a constraint spans two
areas only when the cut between them was already bad. Three things fall out: the
**residual cut weight is the seam plan**, ranked by traffic crossing it; a cluster
that will not fit under the cap is a *finding* (no internal seam to cut on — the
mechanical detection of a true monolith); and survey order comes from the cluster
graph, highest fan-in first. An LLM sits *over* the deterministic base, not in
place of it: it reads cluster summaries only and proposes merges, splits and
names, and the partition is written as a `decided` entry so re-running the
algorithm never silently moves a boundary. Cross-area coupling stays visible
because fan-in is global index data — no session sees the whole repo, but the
index does.

Mechanical index built before any role wakes
(tree-sitter/ripgrep: modules, symbols, term frequency, routes, schemas),
**respecting .gitignore throughout** (ripgrep does natively) so build
artefacts, dependencies, and the framework's own state folder never enter it;
plus trust-ranked extras: **test suite = machine-ratified intent** (outranks all prose
in the repo), issue tracker, usage data. Evidence hierarchy: client > tests >
running behaviour > structure > comments/docs/commit messages (hearsay).

Survey: Architect seeds constraint zero, drafts observed constraints; Domain
extracts the glossary as found (collisions included); Vision drafts observed
baseline statements (what it *appears* to be for — only the client can say what
it is for). Baseline lives as problem-statement items (the brief stays
client-utterance-only) and is confirmed at Signoff. Lazy-elected areas become
ledger entries (named debt). Optional product: the seam plan (Architect proposes
boundary work from fan-in + constraint-zero residue; funded or declined at
Signoff). **[A] Survey sessions compound through artefacts, not context.** Each role consults
its own artefact before amending, so area N's cold session sees the index of
everything areas 1..N-1 found — which is exactly how collision detection works at
all. This requires the sessions to run sequentially, which single-instance roles
already guarantee. **[A] Citations, not claims:** a survey record names the grains
it examined and those are validated against the code index, so a lazy surveyor
cannot starve constraint zero by asserting `none_found` everywhere.
Maturity gauges: observed→decided ratio; constraint-zero shrinkage; [A] cut weight
across pinned area boundaries.
A true monolith prices as globally-reviewed until the client funds seams —
degradation is to *expensive*, never to *wrong*.

## 6. EOS salvage doctrine + library rulings

The design (this doc + the graph) is the spec. [A] The scavenge material is
`main` @ `a1fea34` — *not* `roman/wip`, which is 52 commits behind it and fully
contained in main. `Custom_AI_TUI` with **observed provenance and no track
record**: nothing is trusted because it exists; where code and spec disagree the
code is wrong by definition (apparent code-rightness = an explicit challenge
against the spec, never silent adoption). Every salvaged component earns
admission by passing tests written **from this spec** — roman's own tests
encode EOS assumptions and prove nothing here.

**Roman → design map** [A] corrected against the actual code:
`QueueManager` → **conceptual ancestor, zero reusable code.** It is 97 lines of
JSON-file CRUD; `get_available_atoms` is a ten-line comprehension over status
flags, and a frontier is a query over a message DAG — a different data model, not
an evolution. Migration step 2 is "write the scheduler", not "evolve it".
`orchestrate(plan)` → **does not exist** in `src/`; only
`.architect/verify_orchestration.py`. Dropped from the map.
`ChatController` → **parser and stream handling only.** It is 925 lines, of which
`run_agent_loop` is ~490, entangled with UI callbacks, personas, vision-init and
context culling. The genuinely reusable part is `_parse_tool_args` /
`_extract_tool_calls` (~70 lines, quote- and paren-aware, hard-won). The session
runner is new.
Still good: `AI_Toolbox` → Developer sandbox API (keep the `search_replace` CRLF
scars *and* `_resolve_path`'s traversal rejection from `dfc440c`) ·
`mark_stale`'s cycle guard from `3e26816` → the cascade's refs-DAG walk needs the
same · `SessionManager` worktrees → batch execution · promotion harness →
mechanical gate before Critic · `IControllerCallbacks` → the UI seam (TUI =
renderer over frontier + artefact views; zero logic).

**[A] Import rule.** `rota/` may import the mechanical utilities (`AI_Toolbox`,
worktree helpers, test mocks) and must not import the things this section retires
(controller, session history, persona config). The rule is not about losing code —
git handles that — but about not silently re-importing the concept you decided to
delete.
**Retire:** chat-history-as-memory (working sets replace it — the largest
conceptual change), Gemini coupling, JSON-file state, Manager/Tech-Lead
dual-persona (splits along the artefact partition; Critic has no EOS ancestor
and must be built new).

**[A] Already present** in `requirements.txt` before this work started: pydantic,
tenacity, tree-sitter, textual, pytest, pytest-textual-snapshot. Only litellm was
added. SQLite/FTS5 is stdlib; ripgrep is an external binary.
**[A] Model pin, measured on the target box (RTX 3080), not assumed:** at
`num_ctx=8192` warm round-trip is llama3.1:8b **0.2s**, qwen2.5:7b **0.3s**,
qwen3.5:9b **>100s** — the 9B spills ~27% to CPU once its KV cache is allocated
and stops being usable in a loop. Default pin: `llama3.1:8b`. **Ollama defaults
`num_ctx` to a small value regardless of what the model supports**, so a working
set budgeted at 8k would be silently truncated and the failure would look like bad
reasoning: it is set explicitly and recorded as a pin alongside model id,
temperature and prompt hash.

**Libraries — unequivocal:** SQLite (atomicity law), litellm (+ streaming with
chunk reassembly; tool args arrive fragmented — execute only on completion),
tenacity (replace hand-rolled 429 retry), pydantic (validate parsed tool args;
parser itself stays custom), tree-sitter + ripgrep (replace hand-rolled
analysis), FTS5 when the decision index outgrows in-context reads (deferred —
vectors/sqlite-vec deferred further, until FTS5 + index reads measurably fail),
Textual (keep), pytest (keep).

**Libraries — judgement calls (default: hand-roll, it's identity):** scheduler
/frontier (never a workflow framework; stateless and disposable — see §4 — so
rewriting it is always cheap), `TOOL:` parser, `search_replace`,
sandbox (subprocess + import allowlist suffices while local/single-user),
config (TOML), schema migration (plain DDL).

**Rule: libraries for plumbing, hand-rolling for identity.**

## 7. Open questions

**Closed [A]:**

1. ~~Signoff-with-visible-assumption semantics.~~ **Disclosure-only.** Approval
   while an assumption is displayed does not ratify its default; the entry stays
   open. Implicit acceptance would let defaults slide through an "lgtm"
   unexamined.
2. ~~Backlog's three writers.~~ **Closed by the schema**, which was always the
   answer: `tickets` / `criteria` / `batches` are three tables with one writer
   each. Note what this does *not* solve — a criterion that contradicts its own
   ticket is still writable and no schema constraint sees it. It is caught late
   but it is caught, and now by two things: Tester (a contradictory criterion
   produces a test that cannot be written or fights another test) and Developer
   (Dev1's routing). Residual, with named catchers.
3. ~~Message schema fields.~~ Formalised in the DDL. `cause_id` is nullable and
   `cause_kind` records which kind of root a message hangs from, because ticks and
   gates are roots too — with the agenda tick, Interface can wake with no inbound
   message at all.

**Still open (need real data or a client ruling):**
4. **Retrieval threshold** for intake-vs-decisions matching — build
   instrumented, tune against a real decision record.
5. **Initiation interview** full script — five movements sketched (§5), detail
   deferred to Interface implementation.
6. **Binding staleness** — [A] narrowed. Fail-safe defaults now cover the two
   easy cases: **unbound = global** and **unresolvable = global**, so a missing or
   broken binding always means "always visible, therefore expensive", never
   "filtered out, therefore wrong". This matters more than it did, because
   binding-filtered index reads make bindings load-bearing rather than merely
   annoying. What survives is the *actively wrong but resolvable* binding — points
   at a real grain, the wrong one — which still wants the operational check.
7. **Suspension count cap** per task (context re-bloat through repeated resume).
8. **[A] Area partition re-cutting.** Boundaries are pinned by a `decided` entry so
   they cannot drift between runs. Additions self-heal (new modules fall into
   constraint zero and trigger review until surveyed); a boundary that was thin
   when cut and has since grown heavy does not. Probably a maturity gauge — cut
   weight across pinned boundaries — rather than a tick.
9. **[A] Interface's load.** It runs record, segment, ratify, broadcast, harvest,
   dedupe, order, translate, present, and route consults — more jobs than any
   other role, single-instance, on the critical path of every client interaction,
   and the only role that cannot be information-starved. Composed as lego pieces
   over one base conversational prompt (one per verb, selected by inbound message
   type), which is also what makes I1–I6 test one piece each. If any role needs
   splitting later it is this one.

## 8. Migration plan (ordered, no dates)

**[A] Status.** Steps 1-4 are built and under test in `rota/`; step 5 is the next
piece of real work. What exists: `design/graph.json` (extracted from the viewer,
now the loaded wiring), `graph.py` (contact derivation + boot assertions),
`schema.sql`, `db.py` (atomic session commit), `scheduler.py`, `boot.py`,
`sandbox.py`, `api.py`, `toolproto.py`, `llm.py`, `runner.py`, `fixtures.py`,
`cockpit.py` + `viewer.html`. 78 tests green: T0 plumbing, T0-S9 sandbox, T0-S10
parser, runner contract, and a synthetic arc that drives a full lifecycle through
the real machine with canned completions - composition evidence that does not wait
for T2.

**[A] Two steps inserted, one reordered.** The fixture loader moved ahead of the
scheduler (it needs only the schema, and it is what makes everything after it
visible). A synthetic arc with mocked roles was added after the scheduler, so
composition is proven at step 2 rather than step 5 - each part passing does not
prove the parts compose.

1. **Schema first.** SQLite DDL from the graph's ERD: statements, items,
   glossary, constraints+bindings, tickets/batches, ledger, decisions, verdicts,
   messages (with cause/thread/receipts), version stamps. Resolves open q. 3.
2. **Scheduler.** Evolve `QueueManager` onto the schema: frontier query, claim,
   atomic session commit, checkpoint sweep, cascade trigger from receipts.
3. **Session runner.** Evolve `ChatController`: one message in → sandbox tool
   loop → atomic commit + receipt out. litellm behind `complete()`; `TOOL:`
   parser + pydantic validation.
4. **Role configs.** Split the dual persona along the artefact partition; per-
   role sandbox API modules (working sets as importable functions).
5. **First vertical slice: the understanding loop only.** Interface + the three
   shape roles + L1 + Signoff, against a toy request. No Developer yet. This
   exercises laws 1–4, 7, 8 with the least machinery.
6. **Delivery loop.** Developer (wrap `SessionManager` + `AI_Toolbox`), harness
   gate, Critic (new — starved reads only), Planner.
7. **Reconcile + consult.** Revocation predicate, cascade, receipts, consult
   mode. Test against story 3's beats (`test_interrupt` scaffolding exists).
8. **Dogfood: onboard `Custom_AI_TUI` itself** as the first legacy project —
   survey it, extract its observed constraints, let the remaining EOS→design
   migration be the first signed-off seam plan. The system's first client is its
   own predecessor.

**[A] Findings the implementation forced back onto the design.** Each was raised
rather than absorbed, per section 6:
* The graph gave the backlog three writers and *no readers among them* - Domain
  specified criteria for tickets it could not see, Architect batched tickets it
  could not read. Fixed by the split plus read edges.
* Developer and Tester read criteria but not the ticket those criteria serve, so
  Dev1 (recognising a criterion as a *scope gap*) was impossible as drawn.
  Developer also could not read the verdict against its own batch.
* Architect had no edge to record a survey, though survey records are the
  mechanism that starves constraint zero - the whole onboarding story rested on a
  capability the graph never granted.
* `batch` is a legal scope in section 3's grammar but was missing from the
  viewer's legend, which is where the first implementation copied it from.
* T0-S8's "hard error" was too strong: consult-mode writes are unavailable, not
  fatal.
* TESTS.md's canonical `messages` table left `type/verb` undecided and had no
  attempt counter; both were forced by the first DDL.

Implementation happens in a coding session inside the roman repo (Claude Code),
with this file, `team-graph.html`, and `TESTS.md` (the role test-harness
specification: fixtures, per-role contract tests, arc tests derived from the
stories) as the loaded artefacts. TESTS.md doubles as the schema's requirements
list — migration step 1's DDL must support every fixture defined there. Verify any
library/API specifics current at build time rather than trusting this document's
snapshot.
