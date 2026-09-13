# Phase 3 — quality dependency map

Companion to [responsibility-audit.md](responsibility-audit.md) (the ratified
universe) and [responsibility-allocation.md](responsibility-allocation.md)
(phase 2, who holds what). This phase classifies each responsibility by
**discharge kind** (model / machinery / principal), **quality type** (the
taxonomy in the audit doc), and **upstream quality edges** — each edge
**gated** (a downstream check catches upstream failure) or **silent** (poison
propagates undetected). Load-bearing edges only.

## The map, by responsibility

| id | discharge | quality type | inherits from | edge status |
|---|---|---|---|---|
| A1 elicit | model + principal | completeness | — (root) | **silent by nature** — the named permanent choke point |
| A2 record | machinery + model (segmentation) | faithfulness | A1 | **gated** — principal ratifies the cut |
| A3 scope | model (VK) | discrimination | A2 | **gated** — per-set signoff; but see silent edge S1 below |
| A4 terms | model (Term.) | precision | A2 | **gated** — `term_collision`, `criterion_repair`, challenges |
| A5 contradiction detection | model (any session marks; Liaison routes) | vigilance | A2, A3 | **silent when missed** — the predicate drains marked rows; marking is unchecked judgment |
| A6 interrupt worth | machinery + model | calibration | — | **gated** — `interrupt_cap` mechanical |
| A7 pre-commitment risk | — (P4) | calibration | B1, C3 | **silent** — unheld |
| A8 push back | model | discrimination | A3, A4 | partially gated — contest flow bounds it |
| B1 understand code | model + machinery | completeness | — | **gated for reading** (citations validate grains; challenge falsifies claims), **silent for finding** — see S2 |
| B2 outside facts | model + machinery | faithfulness | — | **gated** — the passage is the evidence |
| B3 currency | machinery | mechanical | B1 | **gated** — area-hash re-fire, chaos-covered |
| B4 known ignorance | machinery | mechanical | B1 | **gated** — derived, never accumulated |
| B5 answer anytime | model (readonly) | discrimination + faithfulness | B1, B3, A4 | **gated at build** (consult key corpus), **silent at runtime** — no check judges a live answer |
| C1 slice into tickets | model (VK) | completeness + discrimination | A3 | **silent** — see S1; `VK-slice` is a known red |
| C2 order | principal + machinery | precision | C1 | **gated** — unsatisfiable schedules raise |
| C3 structure + constraints | model (Arch.) | completeness + discrimination | B1 | **silent for completeness** — see S2; gated for consistency (structural review, boundary phase) |
| C4 write code | model (Dev.) | construction | C1, C5, C3 | **gated** — harness, review order, door guards |
| C5 define done | model ×2 (criteria → tests) | precision | C1, A4 | increasingly **gated at the doors** (surface refs vetted, executable bar, harness facts, invented-literal detector, `tested_by`); residual judgment gap at the Critic (P5) |
| C6 only what was asked | model + machinery | discrimination | C1 | **gated** — touch-set answerability + Critic intent verdict |
| D1 intent verdict | model (Critic) | discrimination | C5, C4 | **gated structurally** (independence by starvation); verdict ≤ criteria quality — inherited, partially gated by `criterion_repair` + the `cannot` ladder |
| D2 structural verdict | model + machinery trigger | discrimination | C3 | **trigger inherits C3's completeness silently** — a commitment nobody wrote a constraint for is never reviewed (S2) |
| D3 refuse hollow tests | Critic + door machinery | discrimination | C5 | doors gated; the Critic link is the known 8B red (P5) |
| D4 bounded failure | machinery | mechanical | — | **gated** — tested, chaos-covered |
| E1 propagate change | machinery | mechanical | — | **gated** — cascade + checkpoint sweep |
| E2 record decisions | model discipline + machinery | faithfulness | — | **gated** — provenance NOT NULL, content identity |
| E3 assumptions visible | machinery detectors + gate | completeness | C5, C4 | **honestly semi-gated** — detected-divergence covers only built detector classes, and the design says so |
| E4 quiescent vs stuck | machinery | mechanical | — | **gated** — predicate lint, quarantines |
| E5 untriggered noticing | — (P2) | vigilance | B1 | **silent** — unheld in steady state |
| E6 drift sensing | machinery | mechanical | C3 (bindings) | **gated**, but bindings completeness inherits S2 |
| F1–F4 | machinery | mechanical/precision | — | **gated** |
| F5 envelope fit | Roman + bench | calibration | — | **silent at runtime** (P7 residue) |
| G1–G2 greenfield | in-flight | construction | A1 | walk-by-walk gating being built |

## The named silent edges (choke points, ranked)

- **S1 — statements → items coverage (feeds C1).** Nothing checks that every
  ratified statement is reflected in an item, and nothing checks tickets
  cover their item: `item_statements` appears in no predicate. The principal
  gates the *content* of items at signoff but cannot gate their
  *completeness* against what he said — he is reviewing what is there, not
  what is absent. Downstream: a dropped want vanishes silently through
  slicing (C1, known red `VK-slice`), criteria, and delivery. **The
  highest-value gate this system could add is mechanical: every ratified
  statement traces to ≥1 item, or the gap is presented at signoff.**
- **S2 — constraint completeness (feeds D2, E6).** Structural review triggers
  on diff ∩ bindings; a commitment the Architect never wrote a constraint
  for is invisible to the trigger forever. Challenge falsifies claims that
  exist; citations prove a surveyor *read*, not that it *found*. Constraint
  zero covers the unsurveyed; surveyed-but-missed is the hole. A
  `none_found` that should have found is the one lie the trail cannot catch.
- **S3 — the vigilance class has no reliable holder.** A5 (contradiction
  marking) and E5 (untriggered noticing) are both vigilance-type, both model
  judgment, both silent when missed, and vigilance is the quality type
  hardest to door-guard: a door checks what a session *does*, not what it
  fails to notice. This is a structural fact about the design, and consistent
  with the observer-effect worry in R4 — the honest treatments are sampling
  (periodic falsification passes over *unchanged* areas, the challenge phase
  made recurring) rather than per-session duties.
- **S4 — live answers are ungated at runtime (B5).** Inquiry quality is
  measured on the consult-key corpus at build time; a live answer to the
  principal passes through no check. Inherits A4/B1/B3 quality silently at
  the moment of use.
- **S5 — the done-chain (C5 → D1/D3)** is the *best-instrumented* choke:
  multiple hops, but the doors accrete mechanical guards walk by walk and
  the residual is one known, attributed judgment red. Listed because verdict
  quality still cannot exceed criteria quality, and criteria inherit S1.

## Type-vs-discharge mismatches (the phase's second product)

- **No mismatch of the fenced-judgment kind found**: discrimination-type
  responsibilities are held by models with mechanical doors, not replaced by
  rules — consistent with the ratified machinery-over-model reading (narrow:
  don't ask for judgment where a schema would do).
- **The measured model boundary is discrimination at desks** (the seven reds
  are "right evidence, wrong desk"; the fork verdict: can/cannot arrives at
  14B, the taxonomy at no local tier). The design's response — collapse the
  judgment, let the ladder diagnose — is type-correct: it converts
  discrimination into precision plus escalation.
- **Vigilance is the unhandled type** (S3). Completeness is the
  under-handled one (S1, S2) — both fail silently, which is exactly why they
  outrank the loud types in this ranking.

## What phase 4 should scrutinize first (the router's output)

1. Modes sitting on S1: Vision Keeper `slicing` (red), the signoff
   presentation path.
2. Modes sitting on S2: Architect survey/boundary/constraint-writing.
3. The D3 chain: Critic `challenge`/`review`, Tester `encode` (several
   known reds live here — richest empirical record).
4. Liaison converse/contradiction (S3's nearest briefed relatives) and the
   generality of the `cannot` door beyond criteria triage (P7 residue).
5. Machinery-discharged rows route to phase 5, which owes: the signoff
   gate's strength (P6), and the enforcement-strength table.
