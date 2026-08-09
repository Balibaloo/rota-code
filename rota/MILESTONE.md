# Milestone: validated to L3, and onboarding a repo we did not write

**Aim.** Not "it works" — *we know precisely what works, the map is generated
from the graph rather than remembered, and the gaps are named.*

The thesis is that roles which never share context can hold a project together
if the artefacts and the message vocabulary carry enough. Everything below is
scaffolding for that one claim. The failure mode the system exists to prevent is
work nobody asked for arriving invisibly — and a suite that only proves the
plumbing has exactly that failure mode itself.

---

## 0 · Reorg — first, or never

- flat `rota/` becomes `core/ roles/ design/ tools/ tests/`-shaped
- **now**, because moving 40 modules is cheap and moving 40 modules plus 160
  fixtures and their cassettes is not
- cassette keys hash the prompt, so prompt *paths* moving after cassettes exist
  invalidates evidence for no reason
- one commit, no behaviour change, suite green either side

## 1 · Edge fixes — `EDGE_PLAN.md`

- **P1 loop closes** — `commit_sha` on `test_runs` / `verdicts` / `findings`;
  the three gates fire per-commit, not once per batch. Proof: fail → fix → pass
- **P2 cascade honest** — move `findings` out of `model`; add 6 refs edges;
  mark `model → code` non-cascading to break the cycle; fallback raises
- **P3 owner reads** — liaison→transcript, liaison→brief, architect→decisions
- **P4 vocabulary** — `tests.encode`, `model.attest`, reach on the 5 creates,
  `verdicts → code` becomes n:1
- **P5 checks** — refs acyclic · every crossing FK has a refs edge · every op
  offered by some mode · every op mentioned in some prompt
- **P6 briefing** — the 19 unmentioned capabilities; `architect → terminologist:
  question`; record the 6 deliberate no-verb channels
- **rulings landed** — Terminologist and Tester may log assumptions;
  Terminologist may author decisions; `ledger.log` gets a deterministic id so a
  repeat is an upsert, not a duplicate

## 2 · Tool calling — investigate, then rework

- probe every local model for native tool calls: `gemma3:4b`, `qwen2.5:7b`,
  `llama3.1:8b`, `qwen3.5:9b` — same prompt, same fixture, measure honour-rate
  and warm latency. Spill is acceptable; correctness is not
- **if a small model honours tools** → native becomes primary, `TOOL:` the
  fallback for models that do not
- **if none do** → `TOOL:` stays and gets fixed rather than replaced
- either way `TOOL:`'s known weaknesses go: the dropped marker that forced
  `extract_lenient`, argument quoting, and the fact that it is a bespoke parser
  competing with trained behaviour
- **cassettes are per-model and per-protocol** — native and text are different
  evidence about different things, and both are worth having

## 3 · Fixtures — the layer everything above stands on

- **wire `rota/fixtures.py`** — it has been the seed→inject→run→assert case
  runner since step 1 and is imported by nothing
- **obligation set generated from the graph**, like edge coverage: an edge
  creates a red row at every tier. The map cannot drift from the design because
  the design emits it
- **synthetic repo** — ~15 files, realistic, no LLM-repo tells: no essay
  comments, no `# Step 1:` scaffolding, plausible history. Properties *planted*
  and recorded:
  - one term with two genuine senses, in known files
  - one high fan-in module with a persisted schema
  - one area with nothing worth constraining
  - one diff touching a bound grain, one touching nothing bound
- **git harness** — pattern from `src/core/session.py`; safety rule from
  `tests/conftest.py` and it is load-bearing: **107 live worktrees in this repo,
  none temp-rooted.** Create under `tmp_path`, snapshot before, remove only what
  is new *and* temp-rooted
- shared, not Developer-only: Architect reads source and diffs, Terminologist
  and Gatekeeper survey code, Critic reads the batch diff

## 4 · L1 — every action a role can take · 63 operations

- one fixture per action where that action is the only right move
- structural asserts on DB deltas and messages; never on prose
- **4 of 5 sampled runs**
- negative half: the action must *not* fire when the fixture does not call for it
- expect prompt churn — this is where the vocabulary rework gets its verdict, so
  L1 is not a single pass

## 5 · L2 — situation to action · 18 predicates + 38 inbound verbs

- given this wake, does the role choose the right action *at all*
- **3 of 5** — cheaper cases held to the higher bar, not this one
- includes the modes with no `.tools` narrowing, where the role has everything
  and must still pick

## 6 · L3 — handoffs · 235 chains, prioritised subset

- 227 → **235** after `architect → terminologist: question`
- prioritise chains where B's action changes an artefact, not chains that relay
- **this is the tier that tests the thesis**: does the message vocabulary carry
  enough meaning to coordinate strangers
- nothing currently touches it

## 7 · Onboarding the synthetic repo — the keystone

- the first case whose **input we did not write**
- only exercise of the `observed` half: `provenance='observed'`, constraint zero
  and its starvation by survey records, `observed_entries` reaching the
  principal. Roughly a third of the design, currently dark
- expectations asserted on **what must be found**, not on wording:
  - two glossary entries for the planted term, citing the planted files
  - a constraint bound to the high fan-in module
  - constraint zero's binding shrunk by exactly the surveyed-and-empty areas
- comes last because an onboarding failure is unattributable until single
  actions and handoffs are already trusted

## 8 · Results surface — continuous

- 160 cases × 5 runs = 800 outcomes; without a view that is a wall nobody reads
- cockpit tab beside coverage: per-role, per-tier, pass-rate, last-run model
- **cassettes committed** — passing runs only, keyed by prompt hash, at case
  granularity so a diff shows which case's evidence moved
- GPU serialised: no `xdist` on model-touching tests

---

## Order

```
0 reorg → 1 edges → 2 tool calling → 3 fixtures → 4 L1 → 5 L2 → 6 L3 → 7 onboarding
                                                            8 results, throughout
```

- 0 must be first
- 1 must precede everything: validating a system whose loop cannot close
  validates the wrong thing
- 2 before 3, because the protocol decides what a cassette records
- 7 last, for the attribution reason

## Out of scope, deliberately

- dogfooding this repo — that is V1, after the map exists
- T2 arcs against the three design stories — after L3
- phases, ticket readiness, the abstain verdict — open in `AGREED.md` §7
