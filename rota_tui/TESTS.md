# TESTS.md — LLM Test Harness Specification

> **STATUS: PARTIALLY IMPLEMENTED.** T0 exists and is green (plumbing, sandbox
> surface, parser), plus a runner contract suite and a synthetic arc. T1 role
> cases and T2 arcs against real models do not exist yet - they need role prompts.
> Amendments carry **[A]**. This document specifies
> the test harness to be built alongside the framework. It is a companion to
> `HANDOFF.md` (the laws and migration plan) and `team-graph.html` (the graph and
> stories). It also serves a second purpose: **the fixture definitions below are
> the requirements list for the database schema** (migration step 1) — the DDL
> must be able to represent every fixture in this file.

---

## 1. Why LLM roles are testable here at all

In this design a session is a function:

```
(fixture database, one inbound message) → (writes, outbound messages, receipt)
```

No hidden state, no shared context, no conversation memory. Therefore every
role test has one shape: **seed rows → inject message → run session → assert on
deltas.** This is the payoff of laws 1–4 (single writer, structured findings,
derived contacts, atomic one-message sessions), and it is why the harness must
be built early: the tests enforce the laws while the code is still soft.

## 2. Test tiers

| Tier | Name | LLM? | What it proves |
|---|---|---|---|
| **T0** | Plumbing | Mock (canned completions) | Scheduler, predicates, gates, parser, sandbox surface, atomicity — deterministic, exact-match asserts. |
| **T0.5** | **[A] Synthetic arc** | Canned, all roles | Composition, with zero LLM judgement: a full lifecycle driven through the real scheduler, sandbox, bus and commit path. Exists because each part passing does not prove the parts compose, and T2 (which would) needs roles. |
| **T1** | Role contract | Real, sampled | One role, one session, structural asserts on DB deltas + messages. |
| **T2** | Arc | Real, scripted client | Multi-session traces replaying the three stories end to end. |

Roman's existing suite (MockGenAIClient, `test_hotreload_no_api_calls`,
`test_interrupt`) is scaffolding lineage for T0 only. **Its assertions prove
nothing about this design** (HANDOFF §6 doctrine); reuse its mocking machinery,
rewrite every assertion from this spec.

## 3. Reliability doctrine for LLM-in-the-loop tests

LLM output is stochastic; the harness must treat that as a measured quantity,
never an excuse.

0. **[A] Fixtures stay tiny - three to five rows, one judgement per case.** An 8B
   model will not fail a structural assertion, but it will drown in twenty
   statements with three plausible readings, and then the pass rate measures the
   fixture rather than the role. Harder variants get their own case ids so the
   simple one survives as the regression floor.
1. **Sampled runs with thresholds.** Every T1/T2 case declares `runs: N,
   pass: k` (defaults `N=5, k=4`). A case passing 5/5 for weeks that drops to
   3/5 is a **prompt regression signal** — the pass-rate history is itself an
   artefact, persisted per (case, model, prompt-version).
2. **Pinned everything.** Model ID, temperature (default 0 for T1 unless the
   case tests variability), prompt version hash recorded on every run. A result
   without its pins is not a result. **[A] `num_ctx` is a pin too** - Ollama
   defaults it low regardless of the model, so an unpinned run silently truncates
   the working set and the failure presents as bad reasoning.
3. **Structural-first assertions.** Assert on *which tables changed, which
   rows appeared, who received which message type, what refs a row carries* —
   never on prose content. Prose is checked only by:
4. **Checkable judgement.** Where the role's output is a choice inside a legal
   space, a deterministic validator asserts legality of the LLM's choice:
   Planner's ordering must be a valid topological sort of declared deps;
   Architect's bindings must be addressable grains that exist in the index;
   Interface's segmentation must cover the utterance (every ratified statement
   carries a span; spans must not overlap and their union flags uncovered
   substance for review). LLM proposes, code verifies.
5. **Semantic judge as last resort.** A judge-LLM assertion (e.g., "does this
   question actually address the blocker?") is allowed only where structure
   cannot express the property, must be marked `judge:` in the case definition,
   and the judge gets a rubric + the same pin discipline. Judge-based cases can
   never be the *only* test of a law.
6. **Negative assertions are half the suite.** Most laws are prohibitions.
   Every case declares `forbidden:` — tables that must show zero writes,
   recipients that must receive zero messages, version stamps that must not
   move. A test with no `forbidden:` block is presumed incomplete.
7. **Tool-call log as evidence.** Every session records its sandbox calls
   (`tool_calls` table). Assertions may target it: "Developer re-read exactly
   the receipt-touched entries" is `tool_calls WHERE session=… AND fn='model.get'
   AND arg IN (receipt ids)`.

## 4. Canonical table names (fixtures bind to these)

The schema (migration step 1) must provide at least:

```
utterances        (id, author, text, ts_order)                      -- transcript
statements        (id, span_utterance, span, text, status, ratified) -- brief
items             (id, text, kind[scope|non_goal], provenance[observed|decided],
                   approval[draft|pending|approved|contested], approval_ver)
glossary_terms    (id, term, sense_short, sense_body, provenance, source_refs)
                   -- [A] index/body split: `full` returns headlines, not text
business_rules    (id, text, term_refs)
constraints       (id, headline, text, provenance, is_global, rationale_decision)
constraint_bindings (constraint_id, grain, grain_kind, resolves)
                   -- [A] bindings are rows, so the trigger is a join. Zero
                   -- bindings = global; resolves=0 promotes back to global.
survey_citations  (survey_id, grain, resolves)   -- [A] evidence, not claims
survey_records    (id, area, outcome[constraints_found|none_found], refs)
tickets           (id, item_id, text)
criteria          (id, ticket_id, text, term_refs[])
batches           (id, item_id, worktree, head_commit, status[pending|running|
                   deferred|merged], priority)
                   -- [A] head_commit is what boot reconciles the worktree against
batch_tickets     (batch_id, ticket_id)
batch_dep_facts   (before_batch, after_batch, reason)  -- [A] Architect declares
schedule_deps     (before_batch, after_batch)          -- [A] derived by the
                   -- scheduler; Planner is dissolved, ordering carries no judgement
ledger            (id, about_ref, default_taken, status[open|resolved], author)
decisions         (id, author, text, resolves_ledger?, supersedes?, refs[])
verdicts          (id, batch_id, diff_ref, result[pass|fail], failed_criterion?)
messages          (id, cause_id, cause_kind[message|utterance|gate|tick|receipt],
                   thread_id, from_role, to_role, verb, body_refs[], round_no,
                   seq, attempts, status[open|answered|quarantined])
                   -- [A] cause_id nullable: ticks and gates are roots, and with the
                   -- agenda tick Interface can wake with no inbound message at all.
                   -- [A] attempts/status bound infrastructure failure loops.
sessions          (id, role, trigger_msg, mode[normal|consult], committed, seq,
                   model, temperature, num_ctx, prompt_hash)
claims            (role PK, session_id, message_id)
                   -- [A] role as PK makes single-instance structural. No FK on
                   -- session_id: a claim precedes its session row by design, and a
                   -- claim with no session is exactly what boot reaps.
tests             (id, batch_id, criterion_id, path, body)          -- [A] Tester
test_runs         (id, batch_id, test_id, result, attempt)          -- [A]
runtime_processes (pid, batch_id, command)                          -- [A] orphan reaping
code_index        (grain, grain_kind, area, fan_in)                 -- [A] partitioning
code_edges        (src, dst)                                        -- [A]
config            (key, value)                                      -- [A] phase caps
receipts          (session_id, table_name, row_id, new_version)
checkpoints       (session_id, role, working_set[(table,version)], valid)
tool_calls        (session_id, fn, args_summary, seq)
artefact_versions (table_name, version)              -- bumped per committed write
```

Fixture blocks below name tables from this list. A fixture row given as
`table: {field: value, …}` means "at least one row matching"; counts are given
where they matter.

## 5. Case definition format

```yaml
id: V2
tier: T1
role: vision
runs: 5
pass: 4
fixture:
  decisions: [{id: R1, text: "deletion rejected: billing history must survive"}]
  statements: [{id: s2, text: "account means login identity", status: ratified},
               {id: s3, text: "regulator requires deletion", status: ratified}]
inbound: {from: interface, to: vision, verb: brief, body_refs: [s2, s3]}
expect:
  writes:
    items:     [{kind: scope, count: ">=1"}]
    decisions: [{supersedes: R1, refs_include: [s2, s3], author: vision, count: 1}]
  messages: []
forbidden:
  writes: [glossary_terms, constraints, schedule_deps, verdicts]
  recipients: [client, developer, critic]
same_session: [items.write, decisions.write]   # law 11: authored at the moment
```

`same_session` asserts the listed writes share one `sessions.id` — several laws
are *about* what happens inside a single commit.

---

## 6. T0 — Plumbing (mock LLM, deterministic)

| id | What | Assert |
|---|---|---|
| T0-S1 | Atomic session commit | Kill runner between tool calls → zero rows from that session in any table; trigger message still on frontier. |
| T0-S2 | Frontier correctness | Fixture: messages with/without terminal responses + one approved batch → frontier query returns exactly the open tips + batch root. |
| T0-S3 | **Scheduler disposability** | Start run, kill scheduler mid-flight, restart → frontier, claims, and next-wake identical to uninterrupted run. (The scheduler holds no state; this test is the proof.) |
| T0-S4 | Revocation predicate | Item approved@v3, amended→v4 → its batches unschedulable; re-approve@v5 → schedulable. Pure query test. |
| T0-S5 | Binding intersection | Diff touching paths/symbols × constraint bindings → correct Architect-trigger set; `global` binding triggers always; empty constraint set + constraint zero present → always triggers. |
| T0-S6 | Constraint-zero shrink | Add survey_record (incl. `none_found`) → recomputed binding excludes area; full coverage → constraint zero binding empty. |
| T0-S7 | Checkpoint invalidation | Checkpoint working_set stamps vs. artefact_versions: disjoint receipt → valid; overlap → invalid. |
| T0-S8 | Consult isolation | Session in `mode: consult` attempting any write → hard error; artefact_versions unchanged. |
| T0-S9 | Sandbox surface = working set | Per role: importing any function outside its graph edges → ImportError. Critic's module contains exactly `criteria.*`, `diff.*`. |
| T0-S10 | Parser round-trip | `TOOL:` protocol: quoting, newlines, CRLF, JSON form, malformed input → error not misparse; pydantic validation of parsed args. |
| T0-S11 | Cascade order | Receipt on `constraints` → wake order derived from refs DAG is model-owner → backlog-owner → schedule-owner → developer; never developer first. Assert zero role-to-role messages produced by the cascade itself — wakes are scheduler events carrying receipts. |
| T0-S12 | Contact enforcement | Message send to a non-derived recipient (e.g. developer→client, developer→planner) rejected at the bus. No role can ask about dispatch: "being woken is the assignment". |
| T0-S15 | Preemption kills whole, parks the rest | Running batch b1 (session live, runtime processes recorded); schedule reorder makes b2 next → b1's runtime process set empty (killed outright), checkpoint discarded, worktree and commits untouched (git state identical), b1 status `deferred`; next wake is b2 in a **fresh** worktree. Later reschedule of b1 → cold session in b1's surviving worktree. |
| T0-S13 | Cycle collapse | Escalation path A→B→C, C targets B (suspended on-path) → routed as resume-with-question into B's session, no second B session. |
| T0-S14 | Budget meters | Hop count and per-blocker client-touch count computed from message DAG paths match hand-computed values on a fixture DAG. Caps are read from phase config: assert the shaping/onboarding phase resolves to the high cap and steady-state to the low default. |

---

## 7. T1 — Role contract tests

Every case implicitly asserts: exactly one session row, committed=true, a
receipt for every write, zero writes to tables not listed in `expect`, zero
messages to recipients not listed. Only case-specific content is shown.

### 7.1 Interface

**I1 — Segmentation at client granularity.**
Fixture: empty tables.
Inbound: client utterance: greeting + `"we need SSO, but only if it works with
our LDAP"` (a conditional; no time content).
Expect: `utterances` +1 verbatim (greeting included); proposed statements at
client granularity — validator: the conditional is **one** statement (span
covers it whole); `confirm` message to client carrying the proposal.
Forbidden: writes to items/glossary/anything else; `clarify` messages; any
paraphrase (validator: statement text ⊆ utterance modulo whitespace).

**I2 — Ratification commit and correction loop.**
Fixture: `utterances` u1; prior `confirm` message with proposed s1–s3.
Inbound: client: accepts s1, s3; rewords s2.
Expect: s1, s3 → `ratified`; rewording lands as new utterance u2; re-proposal
(`confirm`) covers only the s2 replacement.
Forbidden: s2-original silently mutated (statements are superseded, not edited).

**I3 — Harvest: dedupe, order, traceability.**
Fixture: three `report` messages from vision/domain/architect; two are the same
blocker in different vocabulary (fixture marks them with a shared `blocker_key`
for the validator's answer key).
Expect: one `clarify` to client; question count ≤ 2; **every question's
body_refs contains ≥1 report message id** (nothing invented — structural
traceability); the duplicated blockers map to one question.
Forbidden: questions with empty ref sets; separate questions for the duplicate.

**I4 — Consult mode routes and touches nothing.**
Fixture: approved items; running batch; a valid `checkpoints` row for developer;
recorded `artefact_versions`.
Inbound: client question ("how does X behave right now?").
Expect: `consult` messages to the relevant shape role(s); after their canned
`answer`s (T1 may mock the consulted roles), one reply to client.
Forbidden: any write anywhere; any version bump; checkpoint remains `valid`.
(The invariant "read-only inquiry is free" — asserted, not assumed.)

**I5 — Signoff presents the lineage's open assumptions.**
Fixture: items i1 (draft), i2 (draft); `ledger` open entry a1 with
`about_ref: i1`; `submit` message from vision.
Expect: `present` message whose body_refs include i1, i2, **and a1**; on canned
per-item verdicts, `relay` to vision with per-item results.
Forbidden: presenting a1 detached from i1; omitting a1.

**I6 — Interface never invents questions.**
Fixture: brief with one vague ratified statement; **zero** report messages.
Inbound: scheduler tick for round-close.
Expect: broadcast (`brief` messages) to the three shape roles.
Forbidden: any `clarify` to client — with no blockers there are no questions,
however tempting the vagueness.

### 7.2 Vision

**V1 — Identity check fires unprompted.**
Fixture: `decisions` R1 = rejection semantically adjacent to the inbound
statement, *different wording*; ratified statement s1.
Inbound: `brief` broadcast.
Expect: `report` to interface with body_refs ⊇ {R1, s1}.
Forbidden: `items` writes (blocked, not proceeding); messages to client.
Note: this case's pass-rate is the future tuning target for open question 4
(retrieval threshold); record it from day one.

**V2 — Overturn authored at the moment of deciding.** (Definition in §5.)
The load-bearing asserts: `decisions` row with `supersedes: R1`, author=vision,
and `same_session` with the `items` write. R1 remains present (append-only;
supersession is a pointer).

**V3 — Amendment drops approval and reopens.**
Fixture: item i1 approved (approval_ver > last amendment); batch b1 on i1 with
a developer checkpoint.
Inbound: `challenge` from architect requiring i1's scope to change.
Expect: i1 amended; `approval → pending` in the same write set; `reopen` message
to developer carrying b1.
Forbidden: i1 amended with approval left `approved` (the predicate's integrity
depends on this never happening).

**V4 — Cap-2 reframing: strawman, not repetition.**
Fixture: vague statement s1 ("an AI TUI app"); message DAG showing one prior
`clarify` on this blocker that returned no closure (round_no evidence).
Inbound: round-close tick.
Expect: vision's output toward interface is a **proposal**: draft items with
concrete scope + non-goals marked vetoable — validator: items count ≥ 2, at
least one `kind: non_goal`.
Forbidden: a second `report` restating the same open question.
`judge:` (allowed, secondary): "is the proposal concrete enough to veto?"

**V5 — Slices only approved lineages.**
Fixture: i1 approved (postdating amendment), i2 pending.
Inbound: slicing tick.
Expect: `tickets` rows only with item_id = i1.
Forbidden: any ticket on i2.

**V6 — Priority maps by refs, touches nothing else.**
Fixture: items i1, i2 with i2 → batch b3 (refs); ratified statement s9 =
"the search behaviour matters most" (fixture answer key: s9 is about i2);
i2 `approved` with approval_ver current.
Inbound: `brief` delta carrying s9.
Expect: `tool_calls` include consult of own problem statement (the mapping
walk); a `prioritize` write on the backlog entry for i2/b3.
Forbidden: any `items` amendment; any approval change (i2 stays `approved` —
the revocation predicate must not be tripped by a priority); messages to
architect or developer; ledger writes. This case exists to prove priority and
scope are different levers end to end.

### 7.3 Domain

**D1 — Collision detection against own glossary.**
Fixture: `glossary_terms` "order" = sense A (purchase); ratified statement using
"order" as sense B (sequence).
Inbound: `brief` broadcast.
Expect: `report` naming the term (body_refs include the term id + statement id);
glossary amended to carry both senses, both `observed`/appropriately flagged.
Forbidden: silently picking a sense; writing criteria.

**D2 — Criteria in glossary terms.**
Fixture: glossary terms t1..t4; approved item i1; tickets on i1.
Inbound: criteria tick.
Expect: `criteria` rows each with non-empty `term_refs` ⊆ {t1..t4} (schema
enforces the column; the test asserts it's used).
Forbidden: criteria referencing undefined terms (validator cross-checks).

**D3 — Term question answered from the artefact, in the building.**
Fixture: glossary defines the term both ways with one canonical.
Inbound: `question` from developer.
Expect: `answer` to developer with body_refs = glossary ids.
Forbidden: messages to interface or client; glossary writes (answering ≠
amending).

### 7.4 Architect

**A1 — Constraints only where blast radius is external.**
Fixture: code-index rows: module M1 (persists data, external API), module M2
(internal helper, zero external consumers — the fixture's answer key marks it);
survey task message.
Expect: `constraints` on M1 concerns with `bindings` naming addressable grains
that exist in the index (validator); `survey_records` for both, **including a
`none_found` record for M2**.
Forbidden: any constraint on M2; constraints without bindings (unless explicitly
`global`).

**A2 — Escalation onward, not upward-grab.**
Fixture: `escalate` from developer where every resolution changes an approved
item (fixture constructs this: constraint conflict whose fixes all touch i1's
promised behaviour).
Expect: `challenge` to vision.
Forbidden: `constraints` writes (deciding above its authority); messages to
client or interface.

**A3 — Finding, not advice.**
Fixture: diff touching a bound module; the message log *deliberately contains
the full escalation thread* (temptation material).
Inbound: structural-review trigger.
Expect: `finding` message to critic validating against the finding schema:
body = {constraint_id, status ∈ {satisfied, violated}} and nothing else
(schema-enforced, so this is structural, not a length heuristic).
Forbidden: any prose field; any reference to the escalation thread's content.

**A4 — Batching is collision judgement; Planner is not dictated to.**
Fixture: tickets T1,T2 touching overlapping files; T3 disjoint; index rows
provide the touch sets.
Expect: `batches` grouping T1+T2 together, T3 apart; declared dependencies (if
any) written as backlog facts (Planner reads backlog only — it has no model
read).
Forbidden: writes to `schedule_deps` (Planner's artefact); `order`-verb messages
to planner. Notify (`notify`) is allowed.

### 7.5 ~~Planner~~ - [A] dissolved

Its four cases are gone with the role. P1 (legal ordering) survives as
deterministic scheduler tests: a valid topological sort of declared deps, a cycle
raised rather than guessed, and no date/duration content in the schedule. P3
(ordering inquiry) moves to Interface, which gained a schedule read. P4's
load-bearing assertion - priority moves batches whole, `batch_tickets` unchanged -
moves to Vision's V6.

<details><summary>original, for reference</summary>

**P1 — Legal ordering (checkable judgement, flagship of the pattern).**
Fixture: batches b1..b4; declared deps (b2 needs b1's migration; b3, b4 free).
Inbound: ordering tick.
Expect: `schedule_deps` rows; **validator asserts**: topologically valid w.r.t.
declared deps; no dep invented that no declared fact supports; parallelism not
forbidden without cause.
Forbidden: writes outside schedule_deps; any date/duration-like content
anywhere in output (time is not a concept — validator greps structured fields).

**P2 — Recompute on composition change (cascade wake).**
Fixture: existing schedule_deps; a receipt on `batches` (b2 regrouped by
architect via the revocation path).
Inbound: scheduler cascade wake carrying the receipt — **not** a role message;
no notify edge exists.
Expect: `tool_calls` show consult of own schedule before writing (law: read
before amend); updated schedule_deps re-validated as in P1.
Forbidden: stale deps referencing the pre-regroup composition; any assumption
in output that a message announced the change (body_refs must point at the
receipt, nothing else).

**P3 — Ordering inquiry via consult mode.**
Fixture: schedule_deps rows for b1..b4; a running batch b1.
Inbound: `consult` from interface (client asked "what happens after this?"),
session `mode: consult`.
Expect: `answer` to interface with body_refs = schedule_deps rows; content
derivable from the artefact (validator recomputes and compares).
Forbidden: any write; any version bump (consult isolation, per T0-S8); any
recipient other than interface. Note: no role may ask Planner anything —
the developer has no schedule contact by design (see T0-S12); the only
legitimate schedule question is the client's, arriving exactly this way.

**P4 — Priority moves batches whole.**
Fixture: schedule_deps ordering b1 → b2 → b3; b1 `running`; a receipt on the
backlog: priority written (by vision) onto b3's entry; `batch_tickets` for all
three.
Inbound: scheduler cascade wake carrying the receipt.
Expect: updated schedule_deps place b3 ahead of b1's successors per the
priority; **validator asserts `batch_tickets` unchanged for every batch** —
the reorder moved batches whole, recomposed nothing.
Forbidden: writes to `batches` or `batch_tickets`; any message to architect
(priority never involves recomposition); any date/duration content.

</details>

### 7.6 Developer

**Dev1 — Question routes by artefact ownership.**
Fixture: batch with a criterion that is ambiguous as a *scope gap* (fixture's
answer key: the gap is an item-level omission, not a term).
Expect: `question` to **vision**; `checkpoints` row written (session suspends).
Forbidden: messages to interface, client, domain, or planner; guessing (no
`code` writes resolving the ambiguity silently — assert no diff commit this
session).

**Dev2 — Constraint conflict escalates, cannot self-serve.**
Fixture: batch whose natural implementation violates constraint C7 (C7 in the
working set, bound to the touched module).
Expect: `escalate` to architect with body_refs ⊇ {C7}; checkpoint written.
Forbidden: model writes (T0-S9 makes it impossible; this asserts it wasn't
*attempted* via tool_calls either); diff that violates C7.

**Dev3 — Assumption logged with the diff.**
Fixture: criteria silent on an edge case the fixture's task forces a choice on.
Expect: diff committed (worktree/branch per batch) **and** `ledger` open entry
`about_ref` = the relevant statement/item, author=developer, same session.
Forbidden: the choice made with no ledger entry (the silent-default failure —
this case exists to catch exactly that).

**Dev4 — Amend/restart election with a stale checkpoint.**
Fixture: revoked-then-reapproved item; receipts overlapping the checkpoint's
working set; surviving worktree with partial commits.
Inbound: `reopen` from vision.
Expect: `elect` message to vision; if amend → worktree preserved (git state
untouched by harness assertion), checkpoint discarded (invalid), understanding
rebuilt — evidenced by `tool_calls` re-reading criteria/constraints.
Forbidden: resuming from the stale checkpoint (no session may load an invalid
checkpoint — also a T0 guard, asserted here end-to-end).

**Dev5 — Patched resume reads exactly the receipt set.**
Fixture: valid checkpoint; receipts touching model rows m3, m7 only (disjoint
from nothing else in the working set).
Expect: session resumes from checkpoint; `tool_calls` include reads of m3, m7.
Forbidden: full re-read of unchanged artefacts (tool_calls show no
`*.read_all`-shape calls — the scope grammar has no such function anyway; assert
no bulk enumeration patterns).

### 7.7 Tester - [A] new

**Te1 - Tests are written from criteria, never from a diff.**
Fixture: batch with criteria; a diff present in the fixture as temptation.
Expect: `tests` rows each ref'ing a criterion; `tool_calls` touch criteria,
tickets and glossary only.
Forbidden: any read of `code.*`; tests with no `criterion_id`.
(The isolation is temporal, not informational - this case is what keeps it real.)

**Te2 - A term used in a criterion is looked up, not guessed.**
Fixture: criterion whose text uses a glossary term with two senses.
Expect: `question` to domain, or a test that names the canonical sense.
Forbidden: silently picking a sense.

### 7.7 Critic

**C1 — Starvation is structural.** (T0-S9 covers the sandbox; this is the T1
half.) Fixture: full DB including decision record, escalation thread, ledger.
Inbound: review trigger.
Expect: `tool_calls` touch only criteria + diff functions.
Forbidden: everything else — the richest fixture in the suite paired with the
narrowest permitted trace.

**C2 — Letter-vs-spirit catch (flagship LLM-judgement case).**
Fixture: criteria for account deletion (tombstone semantics per glossary);
diff that satisfies every criterion literally but whose user-facing confirmation
copy claims permanent hard deletion (story 1's "the button lies", frozen as a
fixture).
Expect: `verdicts` fail with `failed_criterion` set; `challenge` to developer
with body_refs = the criterion.
Sampling: runs: 10, pass: 8 (this is the hardest judgement in the suite; its
pass-rate trend is a first-class model/prompt quality metric).
Forbidden: pass verdict; challenge without a named criterion.

**C3 — Clean pass stays clean.**
Fixture: conforming diff for the same criteria.
Expect: pass verdict.
Forbidden: `challenge` messages; invented objections (fail verdict) — this case
guards against a critic tuned by C2 into rejecting everything.

**C4 — Composes the finding without the reasoning.**
Fixture: C3's conforming diff **plus** a `finding: violated` from architect.
Expect: fail verdict citing the constraint (via the finding's ref).
Forbidden: `tool_calls` or messages requesting the model/rationale; any consult
of the decision record.

---

## 8. T2 — Arc tests (the stories, executable)

The three stories in `team-graph.html` each define an ordered list of steps,
each step an edge set `[from, to, kind, verb]`. That data structure **is** the
expected trace format:

- **Scripted client.** Client turns are canned responses keyed to step index
  (ratifications, verdicts, answers, the interrupt utterance, "lgtm").
- **Per-step assertion.** After the scheduler drains the step's frontier work:
  every expected edge fired = a matching row in `messages` / a matching receipt
  in `receipts`, attributable to the step's window.
- **Global negative.** Across the whole arc: zero messages between non-derived
  contacts (T0-S12 at integration scale), zero writes by non-owners, zero
  client-touch budget violations (recompute meters from the final DAG).
- **Arcs:** Story 1 (greenfield, full lifecycle incl. Signoff, revocation,
  cascade-lite, review, ledger drain), Story 2 (onboarding: index, constraint
  zero, observed provenance, first decision, lazy-election ledger, seam plan),
  Story 3 (boot from durable state, consult-mode isolation, interrupt,
  emphasis-recovery transcript reads, full cascade, `Domain` question).
- Extract step data from the html's `STORIES` block mechanically (it is already
  JSON-shaped); do not hand-copy — the viewer and the arc tests must share one
  source or they will drift.

Arc tests are expensive (dozens of sampled sessions); run nightly-equivalent
cadence (whatever "infrequent" means operationally — no time semantics implied),
with T0 on every change and T1 per affected role.

## 9. Build order for the harness itself

1. T0-S1/S2/S10 first — atomic commit, frontier, parser: nothing else is
   trustworthy until these pass.
2. The fixture loader + case-definition format (§5) — YAML in, seeded SQLite
   out, session runner invoked, delta captured.
3. One role end-to-end: **Interface I1–I3** (cheapest fixtures, exercises the
   most-used machinery).
4. Critic C1/C2 — the design's most distinctive claims deserve early evidence.
5. Remaining T1 by migration-plan order; T2 arcs after the first vertical slice
   (HANDOFF §8 step 5) exists.

Every case in this file traces to a law in HANDOFF §2 or an edge in the graph.
When implementation pressure suggests a case is wrong, that is a challenge
against the spec (HANDOFF §6 doctrine) — raise it explicitly; never quietly
weaken an assertion.
