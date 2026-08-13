# rota

An LLM team where roles never share context, own artefacts single-writer, and
communicate by messages.

**Start at [LAWS.md](LAWS.md)** — what an engagement is, and the thirteen things
the system may never do. Everything below is how those are made true.

## What exists

| file | what it is |
|---|---|
| `LAWS.md` | **L0 and the laws.** The level every other file presupposed and none stated |
| `AGREED.md` | the change set from the design session, written to be checked rather than remembered |
| `design/graph.json` | **the wiring.** Roles, artefacts, edges with verb, noun, rows and depth. Not a picture of the system — the part-list it is assembled from |
| `design/layout.json` | viewer geometry, split out so editing meaning never touches coordinates |
| `design/stories.json` | the three narrated traversals, for arc tests |
| `graph.py` | loads the graph, derives contacts, asserts consistency at boot |
| `schema.sql` | the DDL. Every fixture in TESTS.md §4 must be representable here |
| `db.py` | the atomic session commit, and the table↔artefact binding |
| `predicates.py` | **the frontier**, as 21 declared predicates in four bands, plus four lints |
| `scheduler.py` | claims, cascade, ordering, and the tick bodies the predicates delegate to |
| `config.py` | every cap the principal owns, and the two ways to stop |
| `lifecycle.py` | a batch's runtime state, and the only place that writes it |
| `harness.py` | running the tests — the one gate with no judgement in it |
| `boot.py` | the seven steps, then the ordinary loop |
| `sandbox.py` | per-role namespaces **built from edges** — an ungranted capability was never created |
| `api.py` | one function per (artefact, verb) edge |
| `toolproto.py` | the `TOOL:` text protocol. Malformed input is an error, never a misparse |
| `llm.py` | the `complete()` seam. Ollama direct, litellm optional, scripted for tests |
| `runner.py` | one message in → tool loop → one atomic commit out |
| `fixtures.py` | seed → inject → run → assert on deltas; the case format |
| `cockpit/` | local server: design structure, live state, cases and progress in one picture |
| `onboarding/` | an existing checkout -> index, dependency edges, areas, constraint zero |

Not built: the environment half of Developer (nothing spawns a process yet), and
the TUI seam.

## Running it

```bash
python -m rota.design.graph                       # namespaces, contacts, consistency
python -m rota.core.predicates                  # every state has a way out
python -m rota.tools.vocabulary --analyse  # collisions, duplication, hierarchy
python -m pytest tests/rota/ -q             # the deterministic suite
python -m rota.cockpit.server [root] [--open]     # http://127.0.0.1:8899
```

`--open` opens a browser tab; without it the URL is printed. Reloads never open
one. The server restarts itself when `rota/` changes, so leave it running.

For local-model hardware profiles, context budgeting, cache distinctions, and
the evidence required before adopting a new model, see
[HARDWARE_GUIDE.md](HARDWARE_GUIDE.md).

Against a real model — these cost model time, and replay from committed
cassettes when the prompts have not changed:

```bash
ROTA_L1=1 python -m pytest tests/rota/test_l1.py -q   # one case per mode
ROTA_L1=1 python -m pytest tests/rota/test_l3.py -q   # handoffs, two sessions
ROTA_L1=1 ROTA_REFRESH=1 python -m pytest tests/rota/test_l1.py -q  # re-record
```

Rebuilding the graph from the design viewer (only needed if `team-graph.html`
changes):

```bash
node rota/tools/extract_graph.js rota_tui/team-graph.html rota/design
python rota/tools/amend_graph.py        # Planner out, Tester in, backlog reads
python rota/tools/amend_graph2.py       # backlog split, fact artefacts, missing edges
```

The amendments are scripts rather than hand-edits so the change set is reviewable
as code and survives a re-extraction.

## The three things worth knowing

**The graph is load-bearing.** `sandbox.build(role, conn)` constructs that role's
namespace from its edges. Critic gets exactly `criteria.load`, `tests.load`,
`code.read`, `verdicts.emit` and two `msg.challenge_*` — not because a check
refuses the rest, but because nothing else was created. The only way to grant a
capability is to draw an edge; a prompt has no authority.

**The frontier includes state, not just messages.** An approved item with no
tickets is not a message — nothing would ever wake Gatekeeper for it. Predicates are
re-evaluated every pass, so residual work is re-derived rather than remembered,
which is also why the scheduler can be deleted and rewritten. The universal
invariant: *at quiescence, no predicate fires.*

That only holds if every state a row can be in has a way out, so that is a hard
constraint rather than a hope: `python -m rota.core.predicates` fails the build on a
state nothing drains, a predicate that cannot fire, and a state nothing writes.

**A session is atomic, except for git.** Writes, messages, receipts and version
bumps land in one transaction or none. Git commits are outside it, so the database
*lags* the worktree and boot reconciles the two — see `boot.reconcile_worktrees`.

## Model pin

Measured on the target box (RTX 3080), warm round-trip at `num_ctx=8192`:

| model | warm | note |
|---|---|---|
| `llama3.1:8b` | 0.2s | default |
| `qwen2.5:7b` | 0.3s | fine |
| `qwen3.5:9b` | >100s | spills ~27% to CPU; unusable in a loop |

Ollama defaults `num_ctx` low regardless of the model, so it is set explicitly and
recorded as a pin alongside model id, temperature and prompt hash. An unpinned run
silently truncates the working set and the failure looks like bad reasoning.
