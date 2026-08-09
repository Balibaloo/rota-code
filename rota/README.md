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
| `cockpit.py` + `viewer.html` | local server: design structure + live state in one picture |

Not built: T2 arcs against real models, onboarding/survey, the TUI seam.

## Running it

```bash
python -m rota.graph                       # namespaces, contacts, consistency
python -m rota.predicates                  # every state has a way out
python -m rota.tools.vocabulary --analyse  # collisions, duplication, hierarchy
python -m pytest tests/rota/ -q            # 171 tests
python -m rota.cockpit <project_root>      # http://127.0.0.1:8899
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
constraint rather than a hope: `python -m rota.predicates` fails the build on a
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
