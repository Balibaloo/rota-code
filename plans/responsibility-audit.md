# Responsibility audit — the foundation

## Why this document

Roman does not trust the quality of the rota doctrine — the laws, the role
boundaries, the briefs. The audit therefore rebuilds trust from zero: nothing
in `rota/` is assumed good, including the self-checking tests (a test asserting
a doc against a graph proves consistency, not that either is right, and we have
not even verified the tests run). Ground truth for what the responsibilities
*are* is first-principles reasoning ratified by Roman in interview. The docs
are then audited against that — never against themselves.

## Status: CLOSED (2026-09-03)

All five phases complete, plus the final pass Roman ruled (DECISIONS.md,
REGISTER.md, TOOLCALLING.md swept — clean, with three self-filed defects
folded into grades and two cosmetic defects fixed). S2/S4 closed under R15.
Residue routed: delivery-mode case coverage lives in COMPLETION.md Track A;
unswept remainder (ANSWER_KEYs, ASSUMPTIONS, MILESTONE, ENVIRONMENT,
HARDWARE_GUIDE) is evidence/reference material, unswept by choice. Open on
the principal's desk: the `CR-a-test-that-encodes-nothing` lever, and
commit/split of the audit-era changes.

## Phase status (2026-09-02): all five phases complete

Phase 1 ratified (rulings R1–R10). Phase 2:
[responsibility-allocation.md](responsibility-allocation.md). Phase 3:
[quality-dependency.md](quality-dependency.md). Phase 4:
[feasibility-audit.md](feasibility-audit.md). Phase 5:
[enforcement-verification.md](enforcement-verification.md). Findings P1–P11
below; open decisions the audit hands back: the P11 fork ruling, P10's door,
the S1 statements-coverage gate (highest-value mechanical addition), and
whether P2's untriggered-noticing gap is core-now or extension-later.

## Method — progressive

1. **Phase 1 — the universe.** Draft every responsibility involved in real,
   sensible development capability, in plain language. Interview Roman on the
   items only he can rule on. Output: a ratified universe. **Done —
   ratified v1, 2026-09-02.**
2. **Phase 2 — allocation (top down).** For each ratified responsibility: who
   or what in rota is answerable for it? Allocated to a role, to machinery, to
   Roman himself, deliberately to nobody, or *accidentally* to nobody — the
   last is a finding. Deliberate no-owner needs a recorded reason. Zero-trust
   grading: each allocation is marked VERIFIED (mechanism checked), CLAIMED
   (prose only), PARTIAL, CONTRADICTED, or MISSING. **Both directions:**
   top-down, every ratified responsibility finds its holder; and the reverse
   sweep — the direct test of the distrust that started this audit — every
   law, doctrine position and structural choice in `rota/` must trace to a
   ratified responsibility, a governing property, or the hardware
   constraint. Doctrine that serves nothing is flagged as unjustified
   complexity, however well written.
3. **Phase 3 — quality dependency (added by Roman mid-audit).** For each
   allocated responsibility, two questions before feasibility is even asked:
   - **Quality type** — what kind of quality its discharge demands:
     *faithfulness* (matches a source, comparable), *completeness* (what was
     not missed — fails silently), *discrimination* (correct judgment calls,
     measurable against cases), *precision* (unambiguous, machine-checkable
     output), *construction* (the artifact works), *mechanical correctness*
     (deterministic code), *calibration* (good cost/benefit sense).
   - **Quality dependency** — which upstream responsibilities' quality it
     inherits, and whether each edge is **gated** (a downstream check catches
     upstream failure) or **silent** (poison propagates undetected). A
     verdict cannot exceed its criteria; criteria cannot exceed the
     glossary; the glossary cannot exceed the elicitation.
   The step's product: the quality-dependency map, with choke points —
   inherited, ungated, judgment-type edges — ranked. Choke points get the
   hardest scrutiny in phase 4. Two more rules: the map covers *all*
   ratified responsibilities, allocated or not — an ungated edge feeding an
   unowned responsibility is the strongest finding class this audit can
   produce — and a mismatch between quality type and discharge kind is
   itself a finding: a discrimination-type judgment fenced into mechanical
   rules, or a precision-type output left to model prose, is an allocation
   bug even when the holder is diligent.
4. **Phase 4 — functionality / feasibility (bottom up).** Per role×mode:
   does the brief, pushed context, namespace and harness actually let the
   model discharge what phase 2 says it holds, at the quality phase 3 says
   it needs — **on a mid-capacity model** (see the hardware constraint
   below), which is the only bar that matters. Where empirical record
   exists (the register, case history), it outranks judgment about what a
   mid model can do. Output: per-seat feasibility verdicts naming the
   failing quality type.
5. **Phase 5 — enforcement verification.** The claims "this is checked by
   test X" are themselves audited: run the tests, read what they actually
   assert, find laws whose enforcement is weaker than the prose implies.
   Split with phase 2: phase 2 verified *wiring* (the mechanism exists and
   holds the responsibility); phase 5 verifies *strength* (it catches what
   it claims to catch). Output: an enforcement-strength table.

**Anchor risk, declared:** I read `ROLES.md` and `LAWS.md` before this method
was set. To limit anchoring, the universe below uses no rota vocabulary and is
derived from what building software requires plus Roman's rulings — and the
interview deliberately pushes on areas those docs are silent about.

---

## The mission — draft 2 (reframed by round 1)

The first draft assumed an *engagement* shape: ask → build → finish line.
Roman rejected the finish line outright. The ratified frame:

> **One standing team stewards one living project for one principal, on
> consumer hardware. The project never ends — the backlog empties and
> refills. What the team owes the principal is not an artifact but four
> competencies, available at any moment of the project's life:**
>
> 1. **Safe change** — the capability to make complex changes without
>    breaking what exists. Tests and harness exist *in service of* this
>    competency; they are not deliverables.
> 2. **Live understanding** — the ability to answer complex questions about
>    the project truthfully, at any stage.
> 3. **Unprompted noticing** — surfacing rot, risks and contradictions the
>    team stumbled on, without being asked, as backlog candidates for the
>    principal to rule on. Never acting on its own findings.
> 4. **Starting from nothing** — the other three competencies must hold on
>    an empty repository too; bootstrapping a new project is core, not an
>    afterthought to stewarding an existing one.
>
> Quiescence — an empty backlog, nothing open — is a state the project
> passes through, not an ending anyone declares.

**Governing properties** (rulings R6, R7, R9, R10) — not competencies, but
properties every competency must exhibit; each still needs an owner in
phase 2, and an unowned property is a finding:

- *Breaking is two-tier.* Breakage proper is mechanical: existing checks
  fail; a basic harness pass is the gate. Changes to commitments,
  constraints, or the project's understandability form a second tier that
  must be **sensed and surfaced**, not automatically blocked.
- *Asynchrony and discardability.* The principal's availability varies and
  the system may never depend on his response latency. Blockage is per-item:
  what is blocked parks, everything else keeps going. Parked and in-flight
  work must be discardable without corruption.
- *Settled memory.* Everything ever ruled stays ruled: no settled question
  is re-asked, no decision is lost, and "why is it this way" stays
  answerable indefinitely.
- *Truthful standing.* The system's reports of its own state are
  trustworthy: done means verified, stuck is reported as stuck, unknown as
  unknown. It never claims more than it earned.
- *The principal stays in command.* Nothing hardens into fact unseen; every
  assumption, default and self-noticed finding passes his eyes before
  becoming load-bearing.
- *Parking at the model's limit.* At runtime, a judgment beyond the mid
  model's reliability parks as a per-item blockage for the principal —
  never silently assumed, never globally halting.

**The hardware constraint (foundational).** The target deployment is consumer
hardware with mid-capacity models — 10–12 GB VRAM, roughly the 8B–14B class.
Consequence: every responsibility in the universe must be dischargeable by a
mid-capacity model, by deterministic machinery, or by the principal. There is
no frontier-model escape hatch, and any allocation that quietly assumes one is
a finding. *(Inference ratified by implication of R8 and R10 —
redesign-until-it-fits and park-at-the-limit both price model judgment as
the scarce resource. Read narrowly: don't fence judgments with rules, but
don't ask for judgment where a schema would do. Veto if wrong.)*

**The ring structure (from ruling R2).** The universe has a core and an
extension ring. Core is what the four competencies require. Extensions are
capabilities that good sense should deliver incidentally today but whose
*verified* form is deliberately post-core: quality verification (security,
performance, maintainability, documentation) and feedback/self-improvement
modes. The audit judges the core strictly and the extension ring only for
"is it cleanly separable later", never for absence.

---

## The universe — draft 2

Each entry is "someone must be answerable for X." The someone may turn out to
be a role, machinery, or Roman — that is phase 2's question. Everything below
is core ring unless marked otherwise.

### A. Intent — knowing what is wanted

There is exactly one principal (ruling R3). Every other audience — end users,
future developers, the outside world's rules — matters only as voiced or
commanded by him. So intent handling is the *sole* channel through which any
requirement enters.

One permanent choke point is named up front rather than discovered later:
the root of every quality chain is only half gateable. Fidelity to what was
*said* (A2) can be gated — the principal ratifies the record. Completeness
of what was *meant* (A1) cannot: no gate can confirm the absence of what he
forgot to say. Everything downstream inherits this, which is why A1 is
elicitation — an active craft — and not transcription, and why unprompted
noticing (E5) doubles as the recovery channel for intent that never got
voiced.

- **A1.** Eliciting what the principal wants — including the things he did
  not think to say, and the things he will only recognize when shown.
- **A2.** Recording what was said faithfully, so later disputes have a source
  that is not anyone's memory.
- **A3.** Deciding what is in scope and what is explicitly out — and keeping
  that boundary current.
- **A4.** Fixing one meaning per term wherever ambiguity would change what
  gets built.
- **A5.** Detecting contradictions — between statements, and between a new
  statement and an old ruling.
- **A6.** Judging what each ambiguity costs to resolve, and whether
  interrupting the principal is worth it. His attention is the one budget
  that cannot be refilled.
- **A7.** Surfacing cost, risk and infeasibility *before* work is committed,
  so every ruling is made with open eyes.
- **A8.** Pushing back — saying that an ask conflicts with an earlier ruling
  or with reality, rather than silently building the conflict.

### B. Ground truth — the understanding competency

Elevated from a supporting section to half the mission: "answer complex
questions at any stage" is owed directly to the principal, not just needed
internally.

- **B1.** Understanding the existing code before changing it.
- **B2.** Understanding relevant facts outside the repository — specs,
  licenses, dependency behavior — with sources that stay checkable.
- **B3.** Keeping the understanding current as the code and the world change,
  and knowing *when* it has gone stale.
- **B4.** Knowing what is not yet understood, and making that ignorance safe
  and visible rather than silent.
- **B5.** Answering the principal's questions from that understanding — at
  any time, without the answering itself disturbing work in flight.

### C. Making — the change competency, forward half

- **C1.** Cutting intent into units a builder can execute cold.
- **C2.** Ordering the units — by what the principal cares about, and by
  dependency.
- **C3.** Designing structure that will hold, and guarding the commitments
  that face outward: published interfaces, stored data, protocols.
- **C4.** Writing the code.
- **C5.** Defining "done" per unit precisely enough that a machine can check
  it.
- **C6.** Building only what was asked. Anything else noticed along the way is
  surfaced, never quietly done.

### D. Judging — the change competency, guarding half

"Preventing breaking changes" is the competency all of this serves. Ruled
(R6): breakage proper = existing checks fail (mechanical, harness-passed);
commitment/constraint/understanding drift = sensed and surfaced, second tier.

- **D1.** Verifying the work does what was asked — by someone other than
  whoever built it.
- **D2.** Verifying the work broke nothing that existed before it.
- **D3.** Refusing hollow verification: a check that passes trivially reports
  as coverage and is worse than no check.
- **D4.** Deciding what happens on failure — rework, escalate, abandon — and
  bounding how many times the same failure is retried.

### E. Steering and change over a project that never ends

- **E1.** Absorbing changed intent at any moment, and propagating it: knowing
  which approved or already-built work the change invalidates.
- **E2.** Recording decisions and assumptions, so nothing load-bearing rests
  on a choice nobody remembers making.
- **E3.** Guaranteeing every open assumption is seen by the principal before
  it hardens into delivered fact.
- **E4.** Recognizing quiescence — backlog empty, nothing open — and telling
  it apart from *silently stuck*, which looks identical from the outside.
- **E5.** Noticing problems unprompted — rot, risk, contradiction stumbled on
  in passing — and surfacing them as backlog candidates for the principal to
  rule on. The positive twin of C6: never quietly acted on, never quietly
  dropped.
- **E6.** Sensing drift in the second tier of breaking: a change that
  modifies a commitment, a constraint, or the project's understandability is
  detected and surfaced even when every check still passes.

### F. Operating the capability itself

- **F1.** Budgeting the scarce resources: compute, money, principal
  attention — and keeping those budgets in the principal's hands.
- **F2.** Containing machinery failure — crashes, loops, model misbehavior —
  so it is bounded, visible, and recoverable.
- **F3.** Observability: the principal can see state, progress and health
  without doing archaeology.
- **F4.** Safety boundaries: what the agents may touch — network, secrets,
  destructive operations — and who grants each.
- **F5.** Fitting the hardware envelope: the whole capability runs within
  10–12 GB VRAM and mid-model judgment. Someone is answerable for noticing
  when a responsibility has quietly outgrown the envelope.

### G. Starting from nothing

- **G1.** Standing up a new project from bare intent — initial structure,
  stack, conventions — such that the other competencies hold from day one.
- **G2.** The understanding competency must not silently depend on there
  being code to read. On an empty repository, understanding is built from
  the principal's intent alone.

### X. Extension ring — real, deliberately post-core (ruling R2)

- **X1.** Verified qualities: security, performance, maintainability,
  documentation checked semi-deterministically / by roles, rather than hoped
  for from good sense.
- **X2.** Feedback and self-improvement modes: the system measuring whether
  its own seats do their jobs. Open question whether this is possible at mid
  model capacity without the measurement interfering with function (observer
  effect: feedback shares the channels — prompts, signals, the same model —
  that the working system uses).

---

## Rulings log

- **R1 (2026-09-02, finish line).** There is no finish line. The project
  never ends; the backlog empties. Owed: the standing competency to make
  complex changes safely and to answer complex questions at any stage; tests
  and harness are in service of preventing breaking changes. Roman flagged
  his phrasing as partial — round 2 completes it.
- **R2 (2026-09-02, default qualities).** Security / performance /
  maintainability / documentation are *extensions to the core capability*:
  common-sense development should deliver them incidentally, but their
  verified form (semi-deterministic + roles) is deliberately for after the
  core works. → ring structure.
- **R3 (2026-09-02, audiences).** One principal, and only him. He is — or
  commands on behalf of — every other audience. Nothing is owed to anyone by
  default except through him.
- **R4 (2026-09-02, self-improvement).** Open question, not a responsibility.
  Limiting factors: mid-model capability and noise; the ultimate target is
  consumer hardware, 10–12 GB VRAM, normal mid-capacity models. Whether
  feedback modes can exist without interfering with system function is
  unresolved. The hardware envelope itself is hereby a foundational
  constraint on every allocation.
- **R5 (2026-09-02, core mission).** All four competencies are core: safe
  change, live understanding, unprompted noticing, starting from nothing.
  Roman turned the completeness question back ("anything I'm missing?") —
  round 3 offers candidates.
- **R6 (2026-09-02, breaking).** Breakage proper is mechanical — existing
  checks fail, a basic harness pass is the gate. Modification of
  commitments/constraints and of understanding must be *sensed* by the
  system — surfaced, not automatically treated as breakage.
- **R7 (2026-09-02, availability).** Varies, and blockages are expected:
  whatever is not blocked keeps going, whatever is blocked parks, and work
  can be discarded if required. The system may never depend on response
  latency; blockage is per-item, never global.
- **R8 (build-time fallback, recorded as observed practice, vetoable).**
  While the system is being *built*, a judgment that proves too hard for a
  mid model is met by redesigning the task until a mid model or machinery
  can carry it. The *operational* fallback — what the deployed system does
  at runtime — is a separate open ruling (round 3).

- **R9 (2026-09-02, implied properties).** Settled memory, truthful
  standing, and principal-in-command are implied properties of the four
  competencies, not standalone competencies ("I think these are all
  implied, im not sure"). Recorded as governing properties: auditable,
  ownable, but not mission items. The uncertainty is noted — if phase 2
  shows one of them needs its own machinery, the ruling can be revisited.
- **R10 (2026-09-02, runtime fallback).** Park it as a blockage. Consistent
  with R7: the item blocks and waits, everything unblocked keeps going.
- **R11 (2026-09-03, S1).** The statements→items coverage check is built as
  **disclosure at signoff**: the present includes statements not reflected
  in any item; never blocking. Build pending, measured like any change.
- **R12 (2026-09-03, P2).** Untriggered noticing is **extension ring** —
  filed with the feedback-modes open question (X2). Core competency #3
  stays change-triggered for now, by ruling.
- **R13 (2026-09-03, P11).** Recipient-scope the verdict-after-challenge
  guard (blocks only after a challenge to the Tester — instrument in
  dispute) and add one brief sentence governing `challenge_developer`
  (unsure → challenge, no verdict; sure → the fail verdict is the act).
  Accepted worst case: occasional redundant double-wake of the Developer.
  Both Critic cases must re-earn on one load.
- **R14 (2026-09-03, P10).** The slicing sentence names the act that
  exists: `ledger.log` the undecided scope point, slice only what the item
  says. Accepted worst case: extra ledger rows. Re-record before banking.
- **R16 (2026-09-03, P4 disposition).** P4 is the Architect's, and it is
  **modification-scope disclosure, not risk or cost**: time and effort are
  not considerations (law 13's spirit); what the principal needs is the
  predicted touch — areas, commitments, unsurveyed ground — presented as a
  sense check before work proceeds. Build is a measured change like any
  other.
- **R17 (2026-09-03, P4 timing).** **Both** moments: a coarse
  Architect guess beside the items at signoff, and the grounded
  `batch_touch` set presented before a batch builds. Non-blocking per R7 —
  the steering loop is the lever. Full design:
  [p4-scope-disclosure.md](p4-scope-disclosure.md).
- **R15 (2026-09-03, S2/S4 closure — by extension of Roman's own ruling,
  vetoable).** The two remaining silent chokes — a `none_found` survey that
  should have found (S2), and a live answer reaching the principal
  unchecked (S4) — are instances of the class Roman ruled on 2026-08-29
  (DECISIONS: "what deterministic checks cannot catch"): semantic misses
  are permanent residents, met by the standing ladder — preregistered keys,
  adversarial passes, two-model disagreement, cheap spot-checks,
  containment — with the gauntlet as the composite instrument. The claim is
  "no invisible, unattributable, irreversible errors", not "no errors".
  Both chokes stay named in the quality map; neither blocks closure.

## Open rulings

*(none — universe ratified v1, 2026-09-02. New rulings will be raised as
phase 2 findings require them.)*

## Findings (accumulates from phase 2 on)

Details and evidence in [responsibility-allocation.md](responsibility-allocation.md).
Two findings below were published wrong and corrected after deeper reads
(P3 retracted, P7 reframed) — the correction note at the end says why.

- **P1 (reframed: active frontier, not absence).** "Starting from nothing"
  is a core competency (R5). The base mechanisms assume code — but the S0
  track is a live, measured effort exactly here: thirty-eight walks from an
  empty folder, each stall attributed and answered with a structural floor,
  walk 38 delivering hello-world end to end (2026-09-02). Gap remaining:
  distribution one story wide; the audit tracks it as in-flight, not
  missing.
- **P2 (softened: noticing is change-triggered only).** The stay-true loop
  gives *triggered* noticing — a changed area is re-surveyed and new
  constraints found. What has no steady-state mechanism is *untriggered*
  noticing: `blindspot` and `challenge` are onboarding-scoped, and no duty
  makes a delivery-loop role file rot, risk, or contradiction it stumbled
  on outside a changed area. Core competency #3 is half-held.
- **P3 — RETRACTED.** Understanding staleness *is* sensed: surveys stamp
  `area_hash` at attest, a changed area counts as unread, and the same
  machinery re-fires (loop 5, G3, chaos-covered). Outside facts carry
  `content_hash` for the same purpose. My grading missed the mechanism
  because it lives in the survey wake derivation, not in anything named
  "stale".
- **P4 (stands).** Cost/risk/infeasibility reaches the principal only after
  failure (propose fires when the Architect says the structure cannot carry
  the ask); nothing surfaces risk at approval time. The seed interview's
  price-stated questions are the nearest designed relative — and unbuilt.
- **P5 (reframed: guarded, guard unreliable, known).** The Critic holds the
  hollow-test duty and mechanical door guards accrete (harness facts,
  constant-assert refusal, invented-literal detector). But the Critic's
  challenge case is a known, attributed 8B judgment red — so today the
  Tester is in practice near-sole guardian. A phase-4 feasibility fact,
  already on the project's books.
- **P6 (revised down by phase 5).** Gate presentation of open assumptions
  is briefed discipline, not enforced — no validator checks a present's
  refs. But the backstops are mechanical: `tick_agenda` re-offers every
  open ledger entry whenever the principal is present with nothing pending,
  and no assumption closes without a decision naming it. An assumption can
  slip one gate; it cannot stay unseen while open, and cannot silently
  resolve. Residual ask: a refs-completeness validator on submit-mode
  presents would close the gap entirely.
- **P7 (corrected: the channel exists for triage).** The `cannot` verdict
  (ruled and built 2026-09-01, re-earned 5/5) is a park-at-the-limit
  channel: a complete verdict at the nearest desk, climbed by the ladder.
  What remains open: whether every judgment-bearing mode has such a door,
  or only criteria triage — a phase-3/4 question — and envelope-outgrowth
  detection still lives with Roman.
- **P8 (note for phase 3, not a defect).** "Done" has two writers by
  design — criteria (Terminologist) and tests (Tester) — so verdict quality
  inherits through two hops. The criteria→tests edge must be classified
  gated or silent in the phase-3 map.
- **P9 (doc drift, minor).** SYSTEM.md's gap list still claims the
  what-does-this-system-not-know aggregation is "still not one query";
  `predicates.outstanding()` exists, is that query, and the cockpit renders
  it. One stale line in an otherwise self-correcting document.
- **P10 (phase 4: brief instructs an act the namespace can't perform).**
  The in-flight `vision_keeper/slicing.md` rewrite says an undecidable item
  is "a question for the seat, not a ticket" — but `slicing.tools` is
  `tickets.slice problem.consult ledger.log`: no message channel exists in
  that sandbox. The edit needs a door, or the sentence must name the ledger
  row, before it lands. (The rewrite otherwise measures green: its three
  staled downstream cases re-earned 2026-09-02.)
  **Resolved per R14, built 2026-09-03:** the sentence now names
  `ledger.log`; re-record pending.
- **P11 (phase 4: guard overreach locks Critic out of its verdict).**
  `CR-fail-names-its-criterion` re-earned 0/5: the model produces the
  correct fail-naming-its-criterion verdict four times and the
  verdict-after-challenge guard refuses it each time, because the model
  first reached for `msg.challenge_developer` — a tool in review's
  namespace that no brief sentence governs. Together with
  `CR-a-test-that-encodes-nothing` (verdict where challenge was due), both
  chronic Critic reds trace to one under-specified three-way fork
  (verdict / challenge_tester / challenge_developer). Candidate
  resolutions and their trade-offs are in
  [feasibility-audit.md](feasibility-audit.md); the ruling is the
  project's, and whichever lands must re-earn both cases on one load.
  **Resolved per R13, built and re-earned 2026-09-03:** the guard is
  recipient-scoped (deterministic pin:
  `test_a_developer_challenge_does_not_block_the_verdict`),
  `challenge_developer` has its brief sentence;
  `CR-fail-names-its-criterion` re-earned green. The re-record also exposed
  and fixed a mis-authored chain (`L3-a-failed-verdict-turns-into-a-fix`
  had only ever passed via the wrong route; re-declared `tick:
  verdict_failed`, re-earned 5/5). `CR-a-test-that-encodes-nothing` keeps
  its pre-existing attributed shape — verdict first, challenge late — and
  its two candidate levers (brief reorder vs. structural fork) await a
  ruling. **R11 built and green:** `resolve_inbound` pushes
  `uncovered_statements`; the present's refs carry them *mechanically* in
  the sandbox binding (the "added, never substituted" rule — measured
  first: briefed-but-not-mechanical scored 0/5, the model presenting the
  items alone), pinned by `L1-LI-present-carries-the-uncovered-statement`.

**Correction note (method).** P3 and half of P7 were published on grep-level
evidence — keyword searches over predicates and doctrine — and fell to
reading the actual draining logic and the project's own tracking docs. The
audit's zero-trust standard cuts both ways: a finding is CLAIMED until the
mechanism is read, exactly like an allocation. Every grade in the allocation
table was re-checked at that standard after the retraction; the docs
(LOOPS.md, COMPLETION.md) also verified against a fresh suite run — 1354
passed, 9 failed, all nine the documented known-red/flip set.
