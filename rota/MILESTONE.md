# Milestone: validated to L3, then onboard a repo we did not write

**Aim.** Not "it works" — *we know precisely what works, the map is generated
from the graph rather than remembered, and the gaps are named.*

The thesis is that roles which never share context can hold a project together
if the artefacts and the message vocabulary carry enough. Everything below is
scaffolding for that one claim. The failure mode the system exists to prevent is
work nobody asked for arriving invisibly — and a suite that only proves the
plumbing has exactly that failure mode itself.

Written to be **checked**, like `AGREED.md`. Status: `[ ]` · `[~]` · `[x]`

---

## 0 · Reorg

- [ ] **0.1** flat `rota/` becomes grouped — `core/ roles/ design/ tools/`
- [ ] **0.2** imports updated, suite green either side, no behaviour change
- [ ] **0.3** one commit, reviewable as a move

**Why first:** cassette keys hash the prompt, and prompt paths moving after
cassettes exist invalidates evidence for nothing. Moving 40 modules is cheap;
moving 40 modules plus 160 fixtures is not.

**Verify:** `git show --stat` is renames only; `pytest tests/rota -q` unchanged.

---

## 1 · Edge fixes — detail in `EDGE_PLAN.md`

- [ ] **1.1 P1 · the loop closes.** `commit_sha` on `test_runs` / `verdicts` /
      `findings`; `harness`, `review`, `structural_review` fire when the current
      `head_commit` has no row of that kind
- [ ] **1.2 P2 · the cascade is honest.** `findings` out of `model`; six refs
      edges added; `model → code` marked non-cascading to break the cycle;
      `cascade_order` raises instead of falling back
- [ ] **1.3 P3 · owners read what they own.** liaison→transcript,
      liaison→brief, architect→decisions
- [ ] **1.4 P4 · vocabulary residue.** `tests.encode`, `model.attest`, reach on
      the five creates, `verdicts → code` becomes `n:1`
- [ ] **1.5 P5 · four checks.** refs acyclic · every artefact-crossing FK has a
      refs edge · every operation offered by some mode · every operation
      mentioned in some prompt
- [ ] **1.6 P6 · briefing.** the 19 unmentioned capabilities; add
      `architect → terminologist: question`; record the six deliberate channels
- [ ] **1.7 rulings.** Terminologist and Tester may `ledger.log`; Terminologist
      may `decisions.author`; `ledger.log` id is deterministic so a repeat
      upserts rather than duplicating

**Verify:** fail → fix → pass on one batch. `cascade_order()` is not
alphabetical. `amend tickets` wakes its criteria, batch and tests. A clean
finding wakes nobody.

---

## 2 · Tool calling

- [ ] **2.1** probe every local model on one fixture — `gemma3:4b`,
      `qwen2.5:7b`, `llama3.1:8b`, `qwen3.5:9b` — honour-rate and warm latency.
      Spill is acceptable, incorrectness is not
- [ ] **2.2** native primary if any small model honours tools; otherwise `TOOL:`
      stays and is fixed rather than replaced
- [ ] **2.3** `TOOL:`'s known weaknesses go regardless — the dropped marker that
      forced `extract_lenient`, argument quoting, a bespoke parser competing
      with trained behaviour
- [ ] **2.4** cassettes are keyed **per model and per protocol**; native and
      text are different evidence about different things

**Verify:** the benchmark table is committed, with the reasoning, not a
preference.

---

## 3 · Fixtures — the layer everything stands on

- [ ] **3.1** wire `rota/fixtures.py` — the seed→inject→run→assert case runner,
      unused since step 1
- [ ] **3.2** obligation set **generated from the graph**, like edge coverage:
      an edge creates a red row at every tier
- [ ] **3.3** synthetic repo, **30–40 files across 4–5 modules** with a real
      dependency shape. Realistic: no essay comments, no `# Step 1:`
      scaffolding, no LLM-repo tells. Properties planted and recorded:
      - one term with two genuine senses, in known files
      - one high fan-in module with a persisted schema
      - one area with nothing worth constraining
      - one diff touching a bound grain, one touching nothing bound
- [ ] **3.4** git harness — pattern from `src/core/session.py`, safety rule from
      `tests/conftest.py`. **107 live worktrees here, none temp-rooted**, so:
      create under `tmp_path`, snapshot before, remove only what is new *and*
      temp-rooted
- [ ] **3.5** shared, not Developer-only — Architect reads source and diffs,
      Terminologist and Gatekeeper survey code, Critic reads the batch diff

**Note:** a found repo was considered. Synthesised wins — stage 7 asserts on
*planted* properties, and a real repo has none of them; cloning needs network and
pinning; vendoring puts someone else's licence in this tree.

---

## 4 · L1 — every action a role can take · 63 operations

- [ ] **4.1** one fixture per action, where that action is the only right move
- [ ] **4.2** structural asserts on DB deltas and messages, never on prose
- [ ] **4.3** **4 of 5** sampled runs
- [ ] **4.4** negative half — the action must not fire when the fixture does not
      call for it
- [ ] **4.5** expect prompt churn; this is where the vocabulary rework gets its
      verdict, so L1 is not a single pass

---

## 5 · L2 — situation to action · 18 predicates + 38 inbound verbs

- [ ] **5.1** given this wake, does the role choose the right action at all
- [ ] **5.2** **3 of 5**
- [ ] **5.3** includes un-narrowed modes, where the role has everything and must
      still pick

---

## 6 · L3 — handoffs · 235 chains

- [ ] **6.1** prioritise chains where B *changes an artefact*, not chains that
      relay
- [ ] **6.2** the tier that tests the thesis — does the message vocabulary carry
      enough to coordinate strangers. Nothing currently touches it

---

## 7 · Onboarding — build it, then confirm it

Not "test onboarding". The entire `observed` half is gated on a table nothing
fills: `code_index` has no writer, `code_edges` is referenced by no Python at
all, area partitioning has no algorithm, and nothing creates constraint zero.
`tick_survey` is a working predicate over an empty world — which is why no lint
caught it. *"Does anything ever produce the input this consumes"* is a sequence
question, and every check we have is about a thing.

**Language-agnostic from the start** — tree-sitter with bundled grammars, not
stdlib `ast`. The schema comment said so; I was about to take a Python-only
shortcut.

- [ ] **7a · code index.** Grains (path, symbol, table, route) and fan-in, via
      tree-sitter. One function per language behind one interface
- [ ] **7b · dependency graph.** `code_edges` populated from imports and calls
- [ ] **7c · area partitioning.** Partition the dependency graph into areas;
      pinned by decision, per the schema
- [ ] **7d · constraint zero.** Created at onboarding, bound to repo-minus-
      surveyed, shrunk by survey records including `none_found`, never removed
      by judgement
- [ ] **7e · trigger.** One entry point — CLI and test fixture share it; boot
      already detects an absent state folder
- [ ] **7f · the arc.** Onboard the synthetic repo end to end, scripted
      principal

**The bar, for now:** everything must have *at least something good*. Planted
properties are hard assertions:

- two glossary entries for the planted term, citing the planted files
- a constraint bound to the high fan-in module
- constraint zero's binding shrunk by exactly the surveyed-and-empty areas

Volume and quality get **reported with evidence, not asserted** — if it is
obviously wrong, fix and retest. A precise bar comes later, once there is output
to calibrate against.

---

## 8 · Results surface — throughout

- [ ] **8.1** cockpit tab beside coverage: per-role, per-tier, pass rate, model
- [ ] **8.2** cassettes committed — passing runs only, keyed by prompt hash, at
      case granularity so a diff shows which case's evidence moved
- [ ] **8.3** GPU serialised — no `xdist` on model-touching tests

---

## Order

```
0 reorg → 1 edges → 2 tool calling → 3 fixtures → 4 L1 → 5 L2 → 6 L3
                                              → 7a…7f onboarding
                                              8 results, throughout
```

- **0 first** or never
- **1 before everything** — validating a system whose loop cannot close
  validates the wrong thing
- **2 before 3** — the protocol decides what a cassette is evidence about
- **7 after 6** — an onboarding failure is unattributable until single actions
  and handoffs are already trusted, and 7 inherits the whole fixture layer

## Out of scope, deliberately

- dogfooding this repo — V1, after the map exists
- T2 arcs against the three design stories — after L3
- phases, ticket readiness, the abstain verdict — open in `AGREED.md` §7
