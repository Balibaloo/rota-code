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

- [x] **0.1** flat `rota/` becomes grouped — `design/ core/ roles/ llm/
      cockpit/ testkit/ tools/`
- [x] **0.2** imports updated, suite green either side, no behaviour change
- [x] **0.3** two commits: `paths.py` first so the move could not break a path,
      then the move — 92 renames

**Landed.** 183 green, one more than before (the check that no module computes
its own location). Five things the move broke that a rename cannot see, each
caught by the suite: parenthesised imports, a non-idempotent second pass on
`rota.llm.llm`, string literals (`"rota.db"` became `"rota.core.db"`), indented
deferred imports that fail at *call* time rather than import time, and two file
scans keyed to the flat layout — one of which would have silently emptied the
vocabulary harvest of every L6 term.

**Why first:** cassette keys hash the prompt, and prompt paths moving after
cassettes exist invalidates evidence for nothing. Moving 40 modules is cheap;
moving 40 modules plus 160 fixtures is not.

**Verify:** `git show --stat` is renames only; `pytest tests/rota -q` unchanged.

---

## 1 · Edge fixes — detail in `EDGE_PLAN.md`

- [x] **1.1 P1 · the loop closes.** `commit_sha` on `test_runs` / `verdicts` /
      `findings`; `harness`, `review`, `structural_review` fire when the current
      `head_commit` has no row of that kind
- [x] **1.2 P2 · the cascade is honest.** `findings` out of `model`; six refs
      edges added; `model → code` marked non-cascading to break the cycle;
      `cascade_order` raises instead of falling back
- [x] **1.3 P3 · owners read what they own.** liaison→transcript,
      liaison→brief, architect→decisions
- [x] **1.4 P4 · vocabulary residue.** `tests.encode`, `model.attest`, reach on
      the five creates, `verdicts → code` becomes `n:1`
- [x] **1.5 P5 · four checks.** refs acyclic · every artefact-crossing FK has a
      refs edge · every operation offered by some mode · every operation
      mentioned in some prompt
- [x] **1.6 P6 · briefing.** the 19 unmentioned capabilities; add
      `architect → terminologist: question`; record the six deliberate channels
- [x] **1.7 rulings.** Terminologist and Tester may `ledger.log`; Terminologist
      may `decisions.author`; `ledger.log` id is deterministic so a repeat
      upserts rather than duplicating

**Landed. 200 green.** Fail → fix → pass works; `cascade_order()` is
`transcript, brief, problem, glossary, ledger, tickets, model, decisions,
criteria, batches, schedule, code, tests, findings, verdicts` — law 9's model
before backlog before schedule, at last; `amend tickets` reaches its criteria,
batch and tests; a clean finding wakes nobody.

Two things found while landing it. `findings` had to become its own artefact —
binding it to `model` was mine, from the previous session, and made a clean
review cascade as though the model had changed. And the new "owners read what
they own" check immediately caught two gaps *this stage created*, which is the
best argument for writing the check before the fix.

---

## 2 · Tool calling

- [x] **2.1** probe every local model on one fixture — `gemma3:4b`,
      `qwen2.5:7b`, `llama3.1:8b`, `qwen3.5:9b` — honour-rate and warm latency.
      Spill is acceptable, incorrectness is not
- [x] **2.2** native primary if any small model honours tools; otherwise `TOOL:`
      stays and is fixed rather than replaced
- [x] **2.3** `TOOL:`'s known weaknesses go regardless — the dropped marker that
      forced `extract_lenient`, argument quoting, a bespoke parser competing
      with trained behaviour
- [x] **2.4** cassettes are keyed **per model and per protocol**; native and
      text are different evidence about different things

**Landed.** `TOOLCALLING.md` holds the table and the reasoning. It corrected a
previous session's finding: `llama3.1:8b` honours native calls 3/3 at 0.4s, and
so does `qwen2.5:7b` — only `gemma3` refuses, with a 400. The native path turned
out to be *built and unwired*: `runner.py` computed the schemas into a variable
and called `complete()` without passing them. Verified end to end with a real
Gatekeeper session that committed a real item.

---

## 3 · Fixtures — the layer everything stands on

- [x] **3.1** wire `rota/fixtures.py` — the seed→inject→run→assert case runner,
      unused since step 1
- [x] **3.2** obligation set **generated from the graph**, like edge coverage:
      an edge creates a red row at every tier
- [x] **3.3** synthetic repo, **30–40 files across 4–5 modules** with a real
      dependency shape. Realistic: no essay comments, no `# Step 1:`
      scaffolding, no LLM-repo tells. Properties planted and recorded:
      - one term with two genuine senses, in known files
      - one high fan-in module with a persisted schema
      - one area with nothing worth constraining
      - one diff touching a bound grain, one touching nothing bound
- [x] **3.4** git harness — pattern from `src/core/session.py`, safety rule from
      `tests/conftest.py`. **107 live worktrees here, none temp-rooted**, so:
      create under `tmp_path`, snapshot before, remove only what is new *and*
      temp-rooted
- [x] **3.5** shared, not Developer-only — Architect reads source and diffs,
      Terminologist and Gatekeeper survey code, Critic reads the batch diff

**Note:** a found repo was considered. Synthesised wins — stage 7 asserts on
*planted* properties, and a real repo has none of them; cloning needs network and
pinning; vendoring puts someone else's licence in this tree.

---

## 3B · Developer buildout — the role has a namespace and no hands

This was missing from the plan. I had covered *testing* Developer — the git
harness above, its actions in L1, its handoffs in L3 — and assumed the role was
built. It is not, and the gap is the same shape as onboarding: a role wired into
a world that does not exist.

| what it needs | state |
|---|---|
| a worktree to work in | `batches.worktree` is **read** by boot and the harness, **written by nobody** |
| a way to change a file | there is **no `code.write` or `code.edit` operation at all** |
| `code.commit` | records a sha in the database; **it does not run git** |
| an environment | `runtime_processes` is reaped at boot and **spawned by nothing** |

So Developer can read its tickets, criteria, model and verdicts, ask questions —
and then record that a commit happened which never did.

- [x] **3Ba · worktree lifecycle.** Created on `batch_start`, torn down on
      merge, *surviving* deferral — law 9 says the commits persist and the
      checkpoint does not. Belongs in `lifecycle.py` beside `start`/`defer`/
      `merge`, because it is scheduler work, not a role's choice
- [x] **3Bb · file operations.** The missing verbs. Needs graph edges, which
      makes it an edge-audit-shaped decision about reach, not just a function
- [x] **3Bc · `code.commit` actually commits**, and stamps `head_commit`
- [ ] **3Bd · environment.** Law 9's *"processes and ports die with it;
      half-dead environments are forbidden"* has no implementation. **Still
      open** — nothing spawns a process yet, so nothing can orphan one

      Four things to define before any of it is written, because an environment
      is the first thing in this system that outlives the session that made it,
      and every other guarantee here rests on a session being a pure function:

      - **separation** — what an environment belongs to. A batch has a worktree;
        does it have one environment, or one per run? Two batches must never
        reach each other's ports, and the answer decides whether port
        allocation is owned by the batch or by the scheduler
      - **boundary** — what is inside it and what is merely near it. A process
        the session started is inside. A database the whole machine shares is
        not, and must not be torn down with it. The line has to be stated
        before teardown is written or teardown will cross it
      - **toolkit** — the verbs a role gets: start, stop, status, logs, and
        nothing that lets a role reach a *different* batch's environment. Same
        rule as every other namespace — the capability does not exist rather
        than being refused
      - **hooks** — where lifecycle attaches. Spawn on `batch_start`, teardown
        on the batch's terminal states *and* on crash, since a session that
        dies mid-flight is exactly the case Law 9 names. Crash teardown cannot
        be a session's own responsibility: it is not running
- [x] **3Be** then the harness and fixtures from 3.4

**Two consequences.** This is a bigger stage than 7 — it is the only place the
system touches the filesystem, spawns processes, and can damage something, in a
repo with 107 live worktrees. And **P1 depends on a slice of it**: the loop
closes when judgements are stamped with the commit they judged, and nothing
produces a real commit today. That slice lands inside stage 1.

---

## 4 · L1 — every action a role can take · 63 operations

- [~] **4.1** one fixture per action, where that action is the only right move
- [x] **4.2** structural asserts on DB deltas and messages, never on prose
- [x] **4.3** **4 of 5** sampled runs
- [x] **4.4** negative half — the action must not fire when the fixture does not
      call for it
- [~] **4.5** expect prompt churn; this is where the vocabulary rework gets its
      verdict, so L1 is not a single pass

**4 of 109 cases written, all Gatekeeper, all green at 4/5 or better against
`llama3.1:8b`.** The machinery is proven end to end — case file, seeded fixture,
real session, structural delta, sampled threshold, cassette. What remains is
volume.

The tier earned itself immediately. Three real bugs in four cases, none of them
visible to any deterministic check:

- `problem.set_approval` on an invented id took down a whole session inside the
  transaction, where it should have been one recoverable tool error
- the relay prompt said "approve, contest, or leave pending" — the *ruling*
  words — where the enum is `approved`/`contested`. Two vocabularies in one
  sentence, in a prompt, after the whole vocabulary pass
- Gatekeeper answered the same question twice, and once eleven times

---

## 5 · L2 — situation to action · 18 predicates + 38 inbound verbs

- [x] **5.1** given this wake, does the role choose the right action at all
- [x] **5.2** **3 of 5**
- [x] **5.3** includes un-narrowed modes, where the role has everything and must
      still pick

---

## 6 · L3 — handoffs · 235 chains

- [x] **6.1** prioritise chains where B *changes an artefact*, not chains that
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

- [x] **7a · code index.** Grains (path, symbol, table, route) and fan-in, via
      tree-sitter. One function per language behind one interface
- [x] **7b · dependency graph.** `code_edges` populated from imports and calls
- [x] **7c · area partitioning.** Partition the dependency graph into areas;
      pinned by decision, per the schema
- [x] **7d · constraint zero.** Created at onboarding, bound to repo-minus-
      surveyed, shrunk by survey records including `none_found`, never removed
      by judgement
- [x] **7e · trigger.** One entry point — CLI and test fixture share it; boot
      already detects an absent state folder
- [x] **7f · the arc.** Onboard the synthetic repo end to end, scripted
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

- [x] **8.1** cockpit tab beside coverage: per-role, per-tier, pass rate, model
- [x] **8.2** cassettes committed — passing runs only, keyed by prompt hash, at
      case granularity so a diff shows which case's evidence moved
- [x] **8.3** GPU serialised — no `xdist` on model-touching tests

---

## Order

```
0 reorg → 1 edges → 2 tool calling → 3 fixtures → 3B developer → 4 L1 → 5 L2 → 6 L3
                                                              → 7a…7f onboarding
                                                              8 results, throughout
```

- **0 first** or never
- **1 before everything** — validating a system whose loop cannot close
  validates the wrong thing
- **2 before 3** — the protocol decides what a cassette is evidence about
- **3B before 4** — L1 for Developer is untestable until it can act, and the
  git harness and the real worktree lifecycle are the same machinery approached
  from two sides
- **7 after 6** — an onboarding failure is unattributable until single actions
  and handoffs are already trusted, and 7 inherits the whole fixture layer

## Out of scope, deliberately

- dogfooding this repo — V1, after the map exists
- T2 arcs against the three design stories — after L3
- phases, ticket readiness, the abstain verdict — open in `AGREED.md` §7
