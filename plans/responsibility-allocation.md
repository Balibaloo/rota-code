# Phase 2 — allocation audit (top down, code-first)

Companion to [responsibility-audit.md](responsibility-audit.md). Every grade
below was earned from mechanisms — predicates, schema, config, scheduler —
not from doctrine prose. Grades: **VERIFIED** (mechanism read and wired),
**PARTIAL** (held for some of the responsibility, a gap named), **MISSING**
(no mechanism found), CLAIMED (prose only — none survived; everything either
verified or degraded), CONTRADICTED (none found so far).

Evidence pointers name the mechanism, not the doc that describes it.

## A. Intent

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| A1 elicit | Liaison (converse, agenda) + Vision Keeper (ask, elect) | `predicates.agenda`, liaison converse mode; the seed interview (SEAT.md 2026-08-25: priced questions, taken/evidenced/checked degrees, derive-it default) is the designed answer — principles fixed, **not yet built** | **PARTIAL** — recording strong; elicitation craft designed but unimplemented. The named permanent choke point at the root. |
| A2 record faithfully | Liaison + machinery | transcript append-only, `actor: system` ("Liaison owns it, does not type it"); `statements` segmentation; `predicates.awaiting_confirm` ratify gate | **VERIFIED**, one recorded hole: `brief.segment` never checks a span bounds its own text (DECISIONS, open) — the ratified *text* is gated, the span provenance can lie |
| A3 scope in/out | Vision Keeper | `items` with approval states; `tick_signoff` (per-set, one document); `predicates.contested` + `contest_defences=1` | **VERIFIED** |
| A4 one meaning per term | Terminologist | `glossary_terms`; `predicates.term_collision`, `criterion_repair` | **VERIFIED** |
| A5 detect contradictions | Liaison (+ Critic in onboarding) | `predicates.contradiction`; `challenges` (citation-required) | **VERIFIED** wiring; strength → phase 5 |
| A6 ambiguity cost / interrupt worth | machinery + Liaison | `interrupt_cap=3` with reframe discipline in its declaration; agenda batches asks | **VERIFIED** |
| A7 cost/risk/infeasibility BEFORE commitment | Vision Keeper (propose) | propose mode fires only *after* "Architect says the structure cannot carry what was asked" | **PARTIAL** — reactive only; nothing surfaces cost/risk at approval time → finding P4 |
| A8 push back | Liaison, Vision Keeper, Critic | contradiction; contested (defend once, then amend); liaison base: "never answer from your own reading" | **VERIFIED** wiring |

## B. Ground truth — the understanding competency

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| B1 understand before change | onboarding phases + machinery | 9-phase program (`onboarding_phases` setting); constraint zero bound to unsurveyed areas | **VERIFIED** |
| B2 outside facts | Researcher | `references_` with passage+URL; `cited` provenance; `research_cap`, allowlist granted-never-not-forbidden | **VERIFIED** |
| B3 keep understanding current | machinery (stay-true loop) | `survey_records.area_hash` stamps content at attest; `_survey_wakes.surveyed()` treats a changed area as unread and the same machinery re-fires; loop 5 at G3 with chaos coverage; outside facts: `references_.content_hash` ("the page changed" is a hash comparison) | **VERIFIED** — the original MISSING grade was my error (P3, retracted): the mechanism lives in the survey wake derivation, not in a predicate named for staleness |
| B4 known ignorance | machinery | constraint zero derived-never-accumulated; `predicates.outstanding` ("what this system does not know, as one query"); ledger | **VERIFIED** |
| B5 answer questions anytime | Liaison + machinery | `frontier_readonly`; readonly sandbox "constructs no write functions at all"; intake while halted (`run_state`) | **VERIFIED** |

## C. Making

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| C1 cut into units | Vision Keeper | `predicates.slicing` → `tickets` | **VERIFIED** |
| C2 order units | principal + machinery | `items.priority` (principal's), `rebuild_schedule`, `batch_dep_facts` | **VERIFIED** |
| C3 structure + outward commitments | Architect | `model_areas`, `frame_rulings`; `constraints`+`constraint_bindings`; `structural_review` by grain intersection; boundary sessions outside-in | **VERIFIED** |
| C4 write the code | Developer | `batch_start`; per-batch worktrees; commit-first bounds loss | **VERIFIED** |
| C5 machine-checkable "done" | Terminologist (criteria) + Tester (tests) | `criteria` in glossary terms; `tests`, `test_runs` as "the mechanical gate before Critic" | **VERIFIED** — but "done" has two writers; the criteria→tests edge goes to the phase-3 map (P8) |
| C6 only what was asked | Critic + Architect | `batch_touch` prediction-never-permission makes incidental change answerable; Critic judges intent | **PARTIAL** — extra work *noticed but not done* has no surfacing duty; ties to E5 |

## D. Judging

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| D1 intent verified by non-builder | Critic | `predicates.review` → `verdicts`; Critic barred from reading the model (independence by construction) | **VERIFIED** |
| D2 broke nothing | machinery, then Architect | `predicates.harness` (cheap, loops) → `structural_review` (expensive, once) | **VERIFIED** |
| D3 refuse hollow verification | Critic + machinery at the door | Critic's brief: a test that doesn't encode its criterion is a challenge to Tester (case exists: `CR-a-test-that-encodes-nothing`); mechanical door guards accreted from the S0 walks: harness facts refuse impossible tests, constant asserts refused toward `cannot`, invented literals owe ledger rows, criteria carry vetted `surface_refs` | **PARTIAL** — allocated and increasingly mechanized, but the Critic case is a known, attributed 8B judgment red → phase 4 (P5, reframed) |
| D4 bounded failure handling | machinery | `loop_cap`, `LADDER` one-rung exhaustion, `verdict_failed`, `reopen`, quarantine trio (looping/overrun/stalled), `tick_attempt_cap` | **VERIFIED** — richly held |

## E. Steering

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| E1 propagate changed intent | machinery | revocation cascade: `cascade_wakes` walks refs DAG in `cascade_order`; `checkpoint_invalid`; `sweep_checkpoints` | **VERIFIED** |
| E2 record decisions/assumptions | writing roles + machinery | `decisions`, `ledger` append-only; provenance NOT NULL; content-derived identity (`core/identity.py`) | **VERIFIED**, one recorded exception: principal rulings written to `config` are unversioned/unreceipted, outside law 11 (DECISIONS: "Law 11 has never been asked about it") |
| E3 assumptions seen before hardening | gates + detectors | signoff presents a lineage's open assumptions; deferral "costs deferred, not waived"; ruled 2026-08-30: introspection abandoned (1 ledger row in 134 sessions measured) in favour of **detected divergence** — mechanics locate underdetermined points and demand the sentence there; first detector built (invented test literals) | **PARTIAL** — mechanization strengthening; `ledger_signoff=False` still means the gate is the sight guarantee → finding P6 |
| E4 quiescent vs stuck | machinery | `is_quiescent` = no predicate fires; `check_terminal_states` (every state has an exit); `quarantine_stalled` for busy-not-progressing | **VERIFIED**, one recorded exception: deferred-eager `observed_entries` rows are offered once, ever — a deferral strands them undecided, unledgered, never re-offered (DECISIONS: "the put-once rule assumed a ruling always arrives") |
| E5 unprompted noticing | — (onboarding only) | `blindspot` = "onboarding's last word"; `challenge` = onboarding; ledger writable but no duty or predicate in steady state | **MISSING** in delivery → finding P2 |
| E6 sense second-tier drift | Architect + machinery | commitments: diff grains × bindings; understanding: area-hash re-fire (=B3, corrected) | **VERIFIED** wiring |

## F. Operating the capability

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| F1 budgets with principal | machinery | `config.SETTINGS` — undeclared key errors; `config_history`; distinct scarcities deliberately unshared (`loop_cap` vs `interrupt_cap` vs `research_cap`) | **VERIFIED** |
| F2 contain machinery failure | machinery | `boot`: reap claims/processes, reconcile worktrees, quarantine exhausted; `run_state`; environments die whole | **VERIFIED** |
| F3 observability | cockpit | tui/server/progress/inspect_api; `turns`, `tool_calls` | **VERIFIED** wiring; usefulness → phase 4 |
| F4 safety boundaries | principal via config | fetch/search granted-never-not-forbidden; readonly sandbox; worktree isolation | **VERIFIED** |
| F5 fit the hardware envelope | Roman + machinery | `model_routing` from measured bakeoff; the `cannot` verdict (ruled & built 2026-09-01) is a park-at-the-limit channel for triage — a complete verdict at the nearest desk, climbed by the ladder, re-earned 5/5; the model bench as a seat flow is designed. Envelope-outgrowth *detection* still lives with Roman | **PARTIAL** (P7 corrected: channel exists for triage; generality open) |

## G. Starting from nothing

| id | holder(s) | mechanism | grade |
|---|---|---|---|
| G1 bootstrap from bare intent | S0 track (active frontier) | `probes/s0_walk.py`; thirty-eight measured walks from an empty folder, each stall attributed and answered with a structural floor; walk 38 delivered hello-world end to end (2026-09-02) | **PARTIAL, in flight** — P1 reframed: not absent, the active frontier; distribution still one story wide |
| G2 understanding without code | S0 track | vacuous-signal degradation (near-empty index → orient/challenge attest "nothing here" and close) answered walk 2's invented-scope stall | **PARTIAL, in flight** |

## Governing properties

| property | grade | note |
|---|---|---|
| breaking is two-tier | **VERIFIED** wiring | tier 1 (harness); tier 2: commitments (bindings × grains) and understanding (area-hash re-fire) both sensed |
| asynchrony & discardability | **VERIFIED** | `waiting_filter` per-item; suspension-is-a-cache; intake while halted |
| settled memory | **VERIFIED** wiring | `report_is_settled`; content-derived identity; decisions journal |
| truthful standing | **PARTIAL, strengthening** | receipts/turns/harness are structural honesty; the project actively converts false greens to honest reds and guards claim-without-work (walk seven's hold-as-deferral); residual: hollow-test judgment red (P5) |
| principal stays in command | **PARTIAL** | inherits P6; SEAT's decided-rows-only-from-keypress contract is the designed strengthening |
| park at the model's limit | **PARTIAL** | the `cannot` verdict + ladder is the channel for criteria triage (built, re-earned 5/5); generality beyond triage open (P7, corrected) |

## Reverse sweep — the fourteen laws

Every law must serve a ratified responsibility, governing property, or the
hardware constraint. All fourteen trace; none is unjustified complexity:

L1→E2/D1 (attribution), L2→hardware constraint (short contexts) + quality
gating, L3→structural integrity of contacts, L4→F2 + atomicity, L5→
asynchrony/discardability, L6→D4, L7→F1, L8→A3/D1/D2, L9→E1, L10→B5,
L11→E2/B2, L12→C3/E6, L13→the no-finish-line mission (R1), L14→settled
memory/E2.

## Reverse sweep — the narrative docs (position level)

- **SYSTEM.md** — clean. Derives the design from the one constraint,
  self-corrects with counts ("three claims were wrong and corrected within
  the hour"). Its stuck-vocabulary analysis and two never-passed judgment
  cases corroborate the model-limit findings from inside the project's own
  record. One stale item: §"lacking" item 4 says the what-don't-we-know
  aggregation is "still not one query" — `predicates.outstanding()` exists,
  is that query, and the cockpit renders it (finding P9).
- **LOOPS.md** — clean, and load-bearing for truthful standing: grades are
  build-evaluated propositions, not status prose. Its loop-5 claim is what
  exposed my false P3.
- **COMPLETION.md** — clean and ahead of this audit in places: the `cannot`
  ruling (P7's correction), the detected-divergence assumptions design, the
  honest-red discipline ("LI-present is the resolution guard converting a
  historically false green into an honest red"), and the S0 track (P1's
  correction) all live here.
- **SEAT.md** — positions trace (attention scarcity → A6/F1; rulings
  revisable → E1; decided-rows-only-from-keypress → principal-in-command).
  The seed interview is the designed answer to A1's gap — unbuilt.
- **ONBOARDING.md** — its spine was verified through mechanisms earlier
  (phases config, predicates, indexer, areas); remaining prose is
  measurement history, no unjustified positions found at this depth.

**The final pass (2026-09-03, ruled by Roman before closing):**

- **DECISIONS.md** — the healthiest document in the repo: consequences
  recorded, reversals kept with causes, and its 2026-08-29 entry ("what
  deterministic checks cannot catch") is the project's own prior answer to
  the S2/S4 chokes. Its self-filed open defects were folded into the
  allocation grades (A2 span hole, E2 config-rulings outside law 11, E4
  deferred-eager limbo). One inconsistency caught and fixed: LAWS.md said
  "nine roles" while its own table and DECISIONS' claim say eight.
- **REGISTER.md** — positions all trace; the classification defers to
  `REGISTER_ENTRIES` in code by design. Fixed: a spliced sentence in "Item
  5, specified" (a paragraph inserted mid-sentence). Left: the "twenty-four"
  count is stale by one; the doc itself says code, not prose, is
  authoritative for the list.
- **TOOLCALLING.md** — claims verified: native wiring exists
  (runner.py:1079), cassettes key per protocol. Noted: the register's
  evidence corpus is text-protocol while the production default is native —
  documented, but a real evidence split.

## Test-suite baseline (2026-09-02)

`pytest tests/rota/`: **1354 passed, 9 failed, 21 skipped** (299s). Every
failure is a recorded model-behaviour case (L1/L3); all structural and
enforcement tests backing the VERIFIED grades above passed. The 9 reds match
COMPLETION.md's attributed known-red set plus the documented chronic-marginal
per-load flip class — the docs' claims verify against a fresh run.
