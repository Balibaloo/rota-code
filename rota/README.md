# rota

An LLM team where roles never share context, own artefacts single-writer, and
communicate by messages.

**Start at [LAWS.md](LAWS.md)** — what an engagement is, and the thirteen things
the system may never do. Everything below is how those are made true.

## What exists

| file | what it is |
|---|---|
| `LAWS.md` | **L0 and the laws.** The level every other file presupposed and none stated |
| `ONBOARDING.md` | **understanding a repository, derived**: why onboarding is three questions over the whole program before it is a pass over areas, and what each phase is shown |
| `ROLES.md` | **the nine seats** — what each is answerable for and what it may never decide. Read before changing a brief; checked against the graph by `test_roles_doc` |
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
| `cockpit/` | local server: design structure, live state, cases and progress in one picture. `tui.py` is the seat |
| `onboarding/` | an existing checkout -> index, dependency edges, areas, **lexicon**, constraint zero. The phases that follow -- orient, define, survey -- are [ONBOARDING.md](ONBOARDING.md) |
| `cli.py` | **one way in.** A run has a name; the run records the project |

Not built: the environment half of Developer. The spawner exists and **nothing
calls it**, which is the safe order — a writer nothing calls cannot orphan
anything — and step 5 of [ENVIRONMENT.md](ENVIRONMENT.md), the toolkit, is the
first thing that would hand a *role* the capability.

## Running it

A **run** is a named database about a checkout. It records which one, so
nothing downstream has to be told twice.

```bash
python -m rota ls                                  # what runs exist, and their state
python -m rota onboard ctn_v3 --root <checkout>    # index, partition, lexicon, constraint zero
python -m rota onboard ctn_v3 --root <checkout> --no-prose   # and withhold README/docs from every session
python -m rota tui ctn_v3                          # the seat: talk, run, wipe, rerun
python -m rota cockpit ctn_v3                      # http://127.0.0.1:8899
python -m rota report ctn_v3                       # what came out, and the audit
python -m rota wipe ctn_v3                         # worktrees, processes, then the file
```

Two runs against one checkout are two names, not two wipes — which is what
comparing a branch against its main needs, and is the case
[ANSWER_KEY_ctn_v3.md](ANSWER_KEY_ctn_v3.md) exists for.

**`.rota/live.md` is the present tense.** One file, overwritten at the start
of every model call: the pins, the system prompt, the user prompt, and the
completion streaming in as Ollama generates it. Keep it open in an editor that
reloads on change to watch a run work. `ROTA_LIVE=<path>` moves it,
`ROTA_LIVE=0` turns it off. The historical record is the `turns` table, which
the cockpit renders; this is only ever the current call.

**The TUI is the seat.** `python -m rota tui` with no name opens the run list.

| key | what it does |
|---|---|
| `ctrl+l` | the run list — open, make, fork, wipe, diff |
| `alt+p` | run / pause — or, while single-step is holding a completion open, let that one step go |
| `alt+shift+p` | single-step: toggle on/off (on by default) |
| `alt+o` | index the project this run is about |

| `ctrl+alt+r` | wipe, then index the same project again |
| `alt+w` | wipe: worktrees, processes, then the file |
| `alt+b` | the cockpit, on the run you are in |
| `alt+m` | model setup: the providers and models this machine can serve, what it holds, a recommendation, and a profile file written from it |

Everything that destroys something arms rather than fires, and the confirmation
is typing the run's name — the same rule `rota wipe` uses, and it costs the one
thing a yes/no cannot: you have to know which run you are in. `alt+o` is on that
list because `indexer.build` opens with `DELETE FROM code_index`; a run with
nothing indexed yet does not ask, because arming everything is how
confirmations stop being read.

**Single-step is on by default.** After every completion — every model turn,
whether or not it carried a tool call — the seat holds the worker thread open
and shows `single-step: paused` in the sidebar until `alt+p` releases exactly
that one step. `alt+shift+p` turns the mode off (and back on); turning it off
while a step is held releases it immediately, on the reasoning that a mode a
seat just disabled should not go on blocking anything on its behalf. This is
why `alt+shift+p`, not `ctrl+shift+p`: unlike `ctrl+shift+`, an `alt+` chord on
a plain letter carries the letter's own case even on the legacy encoding path
— pressing shift changes which byte follows the escape — so Kitty's keyboard
protocol was never needed to tell `alt+p` from `alt+shift+p` apart.

Bindings are `alt+` and not `ctrl+` because the input has the focus and a widget
binding beats an app one — `ctrl+w` is its delete-word, and a key the input eats
is a key the footer advertises and nothing performs. None is `ctrl+shift+`
either: that combination only reaches a program under the Kitty keyboard
protocol, and elsewhere it collapses to the plain `ctrl+` key and silently does
nothing. `test_the_footer_keys_are_the_ones_the_code_binds` checks this table
against `RotaApp.BINDINGS`.

**The cockpit is for depth.** The register beside the chat answers what is
*owed*; the cockpit answers the two questions it cannot — what a role was
actually shown (the built prompt) and what caused a message (the `cause_id`
chain). Neither is a row in any table, which is why a SQLite browser is a poor
substitute and an ad-hoc SQL prompt is still worth having beside it.

Wipe is a command rather than an `rm` because two of the three things a run owns
are not in the file: a **worktree** lives in the target project and the only
record that it is ours is a row in the database, and a **spawned process** is
the same shape with a worse ending. Delete the file first and neither can ever
be proved ours again. The **WAL** is the third — `rm run.db` leaves `run.db-wal`
behind for the next run of that name to open.

The checks, and the cockpit on a project rather than a run:

```bash
python -m rota.design.graph                       # namespaces, contacts, consistency
python -m rota.core.predicates                  # every state has a way out
python -m rota.tools.vocabulary --analyse  # collisions, duplication, hierarchy
python -m pytest tests/rota/ -q             # the deterministic suite
python -m rota.cockpit.server [root] [--open]     # http://127.0.0.1:8899
```

`--open` opens a browser tab; without it the URL is printed. Reloads never open
one. The server restarts itself when `rota/` changes, so leave it running.

Pointed at a **project root** the cockpit boots a database if there is none —
a root may legitimately have no run yet. Pointed at a **named file** it refuses,
because a name you typed cannot be missing for a good reason. It used to do the
first in both cases, so every foreign-repo run was unviewable and looked like a
system that had produced nothing.

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
tickets is not a message — nothing would ever wake Vision Keeper for it. Predicates are
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
