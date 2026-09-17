# The map: design record and brief (frame 29, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the scope report of 2026-09-17 (reviewer type on Opus,
83 tool calls, 125k). Amended after the design review of 10:30 (reviewer
type on Opus, 31 tool calls, 78k, thirteen findings). Findings are
cited as S<n> for the scope report and R<n> for the review. The
implementer builds from the brief. The reviewer read this record before
any code.

## Why

Frame 21's scope agent made 96 tool calls, most of them finding where
things were, and every later agent found them again (ruled: Roman
queued the frame). `rota/roles/api.py` is 8993 lines with 209 of the
806 `execute` sites under `rota/`, and three ops are over 200 lines each.
An agent asking "who writes `refs`" reads 500 lines to find one call
(observed: S15).

## What the reports changed

- The writers of an artefact table are not in SQL. Forty-eight
  `ctx.writes.append(("<table>", ...))` sites, all with a literal table
  name, feed one generic f-string in `rota/core/db.py:395-428`. A regex
  over SQL names `db.py` as the writer of every table (S1).
- Five ops register in a loop, `*.cite`, with no decorator. The op table
  is `(edge.t, edge.v)` from `rota/design/graph.json`, 87 pairs, equal
  to `len(api.REGISTRY)` (S3).
- A reader can name a table in a column fragment with no leading verb:
  `rota/core/runner.py:988-991` holds `FROM item_provenance` inside a
  constant that starts with `id,` (R1). A verb-prefix gate misses it.
- `PROVENANCE_VIEW_OF_TABLE` is a dict literal whose values are views the
  site then queries. `ARTEFACT_OF_TABLE` is a comprehension whose values
  are artefact names, and `TABLES_OF_ARTEFACT` maps the other way. Only
  the first is an indirect read path (R2).
- 119 `.tools` lines are `msg.<verb>_<recipient>`, built from the 54
  `messages` edges of the graph, never from `REGISTRY` (R3).
- Six schemas hold `CREATE TABLE` under `rota/`. One is a fixture
  project's, `rota/testkit/samplerepo.py` (S2). Nine regex patterns such
  as `CREATE TABLE IF NOT EXISTS (\w+)` parse as SQL (R7).
- The obvious cache key, `git ls-files -s` hashed, does not see an
  unstaged edit. A parse plus one visitor over the 68 files in scope
  costs 0.6 s (S7, S8, R10).

## What the map is

`rota/tools/map.py`, run as `python -m rota.tools.map <query> <name>`
from the repo root. No cache, no database. One run parses the tree,
joins, answers, and exits. The name stays `map.py` (ruled: the frame's
words). `rota/MAP.md` is a different page about the desks; the brief
line says "the map tool" (S13).

### Sources

1. An `ast` pass over every `rota/**/*.py` except
   `rota/testkit/samplerepo.py` (a fixture project's schema, S2) and
   `rota/tools/` itself (one-off scripts): 68 files (R10). Per file it
   records:
   - definitions: every `FunctionDef` and `AsyncFunctionDef`, with the
     qualified name (`Class.method` inside a class), file, first line and
     last line;
   - calls: every `Call` whose callee is a `Name` or an `Attribute`
     chain, recorded as `(bare name, chain, file, line, enclosing
     definition)`. The chain is the dotted source text of the callee,
     `ctx.stage_ref` or `api.stage_ref` (R5);
   - SQL constants: every string `Constant`, including a folded implicit
     concatenation, and every literal part of a `JoinedStr` (R2 of the
     scope, confirmed by the review). From each, the names after `FROM`,
     `JOIN`, `INTO`, `UPDATE`, `TABLE`, `VIEW`, case-insensitive, kept
     only when the name is a known table or view of source 2 (R7). A
     constant with no known name is dropped. The verb is the first word
     of the stripped text, case-sensitive, upper-case (R6): `INSERT`,
     `UPDATE`, `DELETE`, `REPLACE` mark a raw writer, and any other start,
     including no verb at all, marks a reader (R1). A `JoinedStr` whose
     literal part ends with a slot keyword is recorded as `dynamic` with
     no table (R8). Each record is attributed to the enclosing definition
     (S10);
   - pipeline writes: every call `<x>.writes.append((<literal>, ...))`,
     recorded as a pipeline writer of that table by the enclosing
     definition. When the second element is a dict literal with string
     keys, those keys are the columns written (S1);
   - indirect reads: every `Name` load of `PROVENANCE_VIEW_OF_TABLE`, or
     of a local alias bound to it by an `ImportFrom` (R9), inside a
     definition, recorded as an indirect reader of every view named in
     that dict's literal values in `rota/core/db.py`. The values are read
     by `ast` from that file, never imported (S9, R2).
   A raw writer or reader whose file is `rota/core/db.py` is marked
   `pipeline internal` (R11), so the outside raw writers stand alone.
2. Schemas: `rota/core/schema.sql` parsed for `CREATE TABLE` and
   `CREATE VIEW` with their column lists, and the `CREATE TABLE`
   constants found by source 1 in `rota/llm/cassettes.py`,
   `rota/core/web.py`, `rota/testkit/interview.py`, `rota/core/config.py`.
   Each table carries its owning file (S2). The known-name set of source
   1 is this set.
3. `rota/design/graph.json`, read by `json`, not by `rota.design.graph`:
   the `reads` and `writes` edges give the op table `(t, v)`, with `s`
   as the role; the `messages` edges give the message tools, `(s, v, t)`
   (R3). The `.tools` files under `rota/roles/prompts/` give the ops per
   mode: `<role>/<mode>.tools` is the base, and
   `<role>/<variant>/<mode>.tools` is an override, listed as such and
   never resolved through `prompts.mode_tools()` (S5). A line
   `artefact.attr` maps to the verb `attr` first, then to
   `attr.replace("_", " ")` (R4: `batches.judge_touch` keeps its
   underscore). A line `msg.<verb>_<recipient>` maps to the `messages`
   edge with that verb and recipient for the file's role.
4. `rota.roles.api.REGISTRY`, imported at query time: 0.04 s, no file
   open, no database, no environment read (observed: R4 of the review's
   probes). It maps `(artefact, verb)` to the function, and the function
   gives its file and first line through `__code__`. This is the only
   import of `rota` code the tool makes, and it exists because the five
   `cite` ops have no decorator (S3).

### Queries

Each answer is plain text, one fact per line, sorted by file then line.
Paths are relative to the repo root.

- `fn <name>`: every definition whose bare or qualified name equals
  `<name>`, as `def <qualified> <file>:<first>-<last>`. When more than
  one definition shares the bare name, a first line `<n> definitions
  share the name` (R5). Then the ops it implements, `op
  <artefact>.<verb>`. Then its tables, `reads <table>` or `writes
  <table> (pipeline|raw|indirect)`. Then `callers (<n>)`, one per line,
  `<file>:<line> <chain> in <definition>`. Callers are one hop: a caller
  through a helper is not listed, and the usage text says so (R12).
  `--callers 0` hides the list.
- `table <name>`: `schema <file>:<line>`, `columns <a>, <b>, ...`. Then
  `writers (<n>)`: one per line, `<file>:<line> <definition> (pipeline
  cols: a, b|raw|dynamic|pipeline internal)`. Then `readers (<n>)`: one
  per line, `<file>:<line> <definition> (literal|indirect via
  PROVENANCE_VIEW_OF_TABLE|pipeline internal)`. A view is a table here,
  with `view` in place of `schema`. `--column <c>` keeps only the sites
  whose statement or dict names that column. A raw statement names a
  column when the column name appears as a whole word in the statement
  text, said on the line as `(word match)`.
- `mode <role>/<mode>`: `tools <file>` for the base, `override <file>`
  per variant. Then one line per op: `<artefact>.<verb> -> <function>
  <file>:<line>`, or `msg.<verb>_<recipient> -> message <verb> to
  <recipient>`, or `-> not in REGISTRY` when the join fails.
- `file <path>`: every top-level definition with lines, then
  `reads`/`writes` per table with the count of sites, then the ops
  registered in the file.

An unknown name prints `no <query> named <name>` and exits 1. A query
with no argument prints the usage and exits 2.

### Time

One run parses 68 files and walks them in about 0.6 s, the join in
less. Budget: under two seconds per query. The frame's words say
"cached under `.rota/` by the tree's hash". The cache is not built: the
run is under the budget, `.rota/` is `paths.RUNS` and moves with
`ROTA_RUNS`, and the obvious key misses unstaged edits, which is the
state of every implementing pass (observed: S6, S7, S8, R10). This is a
deviation from the frame's words on a measurement. If a query ever
costs more than two seconds, a cache is its own frame.

## Tests

`tests/rota/test_map.py`. Every test runs the tool's functions in
process on the real tree, never as a child, and none opens a database.
The pins are by function name and file, never by line number, because
lines drift (observed: every line of the refs-scope report moved). Each
pin below holds at HEAD (observed: R5 of the review, each checked).

- `refs` pipeline writers are exactly `stage_ref` and `retire_ref` in
  `rota/roles/api.py`. The raw writers outside `rota/core/db.py` include
  `refresh_constraint_zero` in `rota/onboarding/boot.py` (S12: two write
  paths). `_apply_ref` in `rota/core/db.py` is marked `pipeline
  internal`.
- `fn stage_ref` callers include `glossary_amend`, `problem_assert`,
  `model_amend`, `frame_assign` and `_adopt_rows`, all direct.
- `item_provenance` readers include `tick_slicing` in
  `rota/core/scheduler.py`, `_resolve_refs` in `rota/core/runner.py`
  (R1: the column fragment), `problem_assert` in `rota/roles/api.py`,
  and the indirect reader `observed_entries` in `rota/core/predicates.py`
  via `PROVENANCE_VIEW_OF_TABLE`.
- The op table from `graph.json` has 87 pairs and every pair joins to a
  function in `REGISTRY`, `problem.cite` among them.
- `mode terminologist/unresolved` lists its base file; its four non-msg
  lines join to `REGISTRY` and its five `msg` lines join to `messages`
  edges (R3). `mode architect/touch_strayed` joins `batches.judge_touch`
  (R4).
- `rota/testkit/samplerepo.py` contributes no table: `table accounts`
  prints `no table named accounts`.
- A regex pattern string such as the one in `rota/design/graph.py`
  contributes no table named `(\w+)` (R7).
- `file rota/core/db.py` lists `_apply_write` and marks its `INSERT` as
  `dynamic`.
- `fn get` prints the shared-name line and each caller carries its chain
  (R5).
- An unknown name exits 1 with the message.

## Files

- Create `rota/tools/map.py`. Follow `rota/tools/casestatus.py`:
  relative imports for `paths`, an `if __name__ == "__main__"` block. No
  database open at import time. Import `rota.roles.api` inside the
  function that needs it.
- Create `tests/rota/test_map.py`.

No other file changes. The line in `CLAUDE.md` and the three agent
definitions are the assistant's, after the tool exists.

## Known answers the map will give, for the record

- `refs` has two write paths: the pipeline through `stage_ref` and
  `retire_ref`, and raw SQL at boot in `refresh_constraint_zero` with no
  receipt and no version bump (observed: S12). Rota workflow. Parked.
- `obligations.l2()` names 73 modes; 80 `.tools` files exist (S4). Rota
  workflow. Parked.
- `batches.judge_touch` is the one registered verb with an underscore;
  two other multi-word verbs carry a space (R13). Rota workflow. Parked.
- Six places regex `CREATE TABLE IF NOT EXISTS` (S14). The map's schema
  parse is the seventh. Not in this frame.

## The implementer's pass

One pass. Report in the shape the implementer definition gives. Do not
commit. Run `tests/rota/test_map.py` first, then the full suite through
the gate once. The baseline is at e75e67d with 22 reds. Report the
tool's wall time for `table refs` and `fn stage_ref` as `time` measures
it, and the tool-call count from your own report. Do not touch
`tests/rota/walks.jsonl` or `You are a standby peer.md`.
