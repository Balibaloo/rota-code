# The map: design record and brief (frame 29, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the scope report of 2026-09-17 (reviewer type on Opus,
83 tool calls, 125k against an 80k cap; its findings are numbered 1 to
15 below by the report's numbers). The implementer builds from the
brief. The reviewer reads this record before any code.

## Why

Frame 21's scope agent made 96 tool calls, most of them finding where
things were, and every later agent found them again (ruled: Roman
queued the frame). `rota/roles/api.py` is 8993 lines with 209 of the
806 `execute` sites under `rota/`, and three ops are over 200 lines each.
An agent asking "who writes `refs`" reads 500 lines to find one call
(observed: the scope report, finding 15).

## What the scope report changed

- The writers of an artefact table are not in SQL. Forty-eight
  `ctx.writes.append(("<table>", ...))` sites, all with a literal table
  name, feed one generic f-string in `rota/core/db.py:395-428`. A regex
  over SQL names `db.py` as the writer of every table (finding 1).
- Five ops register in a loop, `*.cite`, with no decorator. The op table
  is `(edge.t, edge.v)` from `rota/design/graph.json`, 87 pairs, equal
  to `len(api.REGISTRY)` (finding 3).
- Four readers of `item_provenance` reach the view through
  `PROVENANCE_VIEW_OF_TABLE` and carry no literal (finding 9). One
  `execute` takes its SQL from the caller (finding 10).
- Six schemas hold `CREATE TABLE` under `rota/`. One is a fixture
  project's, `rota/testkit/samplerepo.py` (finding 2).
- The obvious cache key, `git ls-files -s` hashed, does not see an
  unstaged edit. A full `ast.parse` of the 88 files costs 0.47 s
  (findings 7 and 8).

## What the map is

`rota/tools/map.py`, run as `python -m rota.tools.map <query> <name>`
from the repo root. No cache, no database. One run parses the tree,
joins, answers, and exits. The name stays `map.py` (ruled: the frame's
words). `rota/MAP.md` is a different page about the desks; the brief
line says "the map tool" (finding 13).

### Sources

1. An `ast` pass over every `rota/**/*.py` except
   `rota/testkit/samplerepo.py` (a fixture project's schema, finding 2)
   and `rota/tools/` itself (one-off scripts). Per file it records:
   - definitions: every `FunctionDef` and `AsyncFunctionDef`, with the
     qualified name (`Class.method` inside a class), file, first line and
     last line;
   - calls: every `Call` whose callee is a `Name` or the last attribute
     of an `Attribute` chain, recorded as `(callee, file, line,
     enclosing definition)`. The callee is the bare name. A `fn` query
     matches callers on that bare name (reasoned: the tree has no
     resolver, and a bare-name match over-reports rather than misses);
   - SQL literals: every string `Constant`, including a folded implicit
     concatenation, whose stripped text starts with one of `SELECT`,
     `INSERT`, `UPDATE`, `DELETE`, `WITH`, `CREATE`, `DROP`, `ALTER`,
     `REPLACE`, `PRAGMA`, in any position, attributed to the enclosing
     definition (finding 10). From each: the verb, and the names after
     `FROM`, `JOIN`, `INTO`, `UPDATE`, `TABLE`, `VIEW`, case-insensitive.
     `INSERT`, `UPDATE`, `DELETE`, `REPLACE` mark a raw writer. The rest
     mark a reader. An f-string is scanned by its literal parts only;
     a name interpolated as `{w.table}` is recorded as `dynamic`;
   - pipeline writes: every call `<x>.writes.append((<literal>, ...))`,
     recorded as a pipeline writer of that table by the enclosing
     definition. When the second element is a dict literal with string
     keys, those keys are the columns written (finding 1);
   - indirect reads: every `Subscript` or `.get(...)` on a `Name` that
     is one of `TABLES_OF_ARTEFACT`, `ARTEFACT_OF_TABLE`,
     `PROVENANCE_VIEW_OF_TABLE`, recorded as an indirect reader of every
     table or view named in that dict's literal values in
     `rota/core/db.py` (finding 9). The dict values are read by `ast`
     from that file, never imported.
2. Schemas: `rota/core/schema.sql` parsed for `CREATE TABLE` and
   `CREATE VIEW` with their column lists, and the `CREATE TABLE`
   literals found by source 1 in `rota/llm/cassettes.py`,
   `rota/core/web.py`, `rota/testkit/interview.py`, `rota/core/config.py`.
   Each table carries its owning file (finding 2).
3. `rota/design/graph.json`, read by `json`, not by `rota.design.graph`:
   the `reads` and `writes` edges give the op table `(t, v)`, with `s`
   as the role. The `.tools` files under `rota/roles/prompts/` give the
   ops per mode: `<role>/<mode>.tools` is the base, and
   `<role>/<variant>/<mode>.tools` is an override, listed as such and
   never resolved through `prompts.mode_tools()` (finding 5). A line
   `artefact.attr` maps to the verb `attr.replace("_", " ")`.
4. `rota.roles.api.REGISTRY`, imported at query time: 0.02 s and no
   database (observed: the scope report, point 6). It maps `(artefact,
   verb)` to the function, and the function gives its file and first
   line through `__code__`. This is the only import of `rota` code the
   tool makes, and it exists because the five `cite` ops have no
   decorator (finding 3).

### Queries

Each answer is plain text, one fact per line, sorted by file then line.
Paths are relative to the repo root.

- `fn <name>`: every definition whose bare or qualified name equals
  `<name>`, as `def <qualified> <file>:<first>-<last>`. Then the ops it
  implements, `op <artefact>.<verb>`. Then its tables, `reads <table>` or
  `writes <table> (pipeline|raw|indirect)`. Then `callers (<n>)`, one per
  line, `<file>:<line> in <definition>`. `--callers 0` hides the list.
- `table <name>`: `schema <file>:<line>`, `columns <a>, <b>, ...`. Then
  `writers (<n>)`: one per line, `<file>:<line> <definition> (pipeline
  cols: a, b|raw|dynamic)`. Then `readers (<n>)`: one per line,
  `<file>:<line> <definition> (literal|indirect via <DICT>)`. A view is
  a table here, with `view` in place of `schema`.
  `--column <c>` keeps only the sites whose statement or dict names that
  column. A raw statement names a column when the column name appears as
  a whole word in the statement text (reasoned: best effort, stated on
  the line as `(word match)`).
- `mode <role>/<mode>`: `tools <file>` for the base, `override <file>`
  per variant. Then one line per op: `<artefact>.<verb> -> <function>
  <file>:<line>`, or `-> not in REGISTRY` when the join fails.
- `file <path>`: every top-level definition with lines, then
  `reads`/`writes` per table with the count of sites, then the ops
  registered in the file.

An unknown name prints `no <query> named <name>` and exits 1. A query
with no argument prints the usage and exits 2.

### Time

One run parses 88 files in about 0.5 s and the join in less. The
frame's words say "cached under `.rota/` by the tree's hash". The cache
is not built: the parse is under a second, `.rota/` is `paths.RUNS` and
moves with `ROTA_RUNS`, and the obvious key misses unstaged edits, which
is the state of every implementing pass (observed: findings 6, 7, 8).
This is a deviation from the frame's words on a measurement. If a run
ever costs more than two seconds, a cache is its own frame.

## Tests

`tests/rota/test_map.py`. Every test runs the tool's functions in
process on the real tree, never as a child, and none opens a database.
The pins are by function name and file, never by line number, because
lines drift (observed: every line of the refs-scope report moved).

- `refs` pipeline writers are exactly `stage_ref` and `retire_ref` in
  `rota/roles/api.py`, and the raw writer set holds
  `refresh_constraint_zero` in `rota/onboarding/boot.py` (finding 12:
  two write paths).
- `refs` callers through `stage_ref` include `glossary_amend`,
  `problem_assert`, `model_amend`, `frame_assign` and `_adopt_rows`
  (`fn stage_ref` callers).
- `item_provenance` readers include `tick_slicing` in
  `rota/core/scheduler.py`, `_resolve_refs` in `rota/core/runner.py`,
  `problem_assert` in `rota/roles/api.py`, and the indirect reader
  `observed_entries` in `rota/core/predicates.py` via
  `PROVENANCE_VIEW_OF_TABLE`.
- The op table from `graph.json` has 87 pairs and every pair joins to a
  function in `REGISTRY`, `problem.cite` among them.
- `mode terminologist/unresolved` lists its base file and each op joins.
- `rota/testkit/samplerepo.py` contributes no table: `table accounts`
  prints `no table named accounts`.
- `file rota/core/db.py` lists `_apply_write` and marks its `INSERT` as
  `dynamic`.
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
  receipt and no version bump (observed: finding 12). Rota workflow.
  Parked on the stack.
- `obligations.l2()` names 73 modes; 80 `.tools` files exist (finding
  4). Rota workflow. Parked on the stack.
- Six places regex `CREATE TABLE IF NOT EXISTS` (finding 14). The map's
  schema parse is the seventh. Not in this frame.

## The implementer's pass

One pass. Report in the shape the implementer definition gives. Do not
commit. Run `tests/rota/test_map.py` first, then the full suite through
the gate once, `python -m rota.tools.map` is not run by the gate. The
baseline is at e75e67d with 22 reds. Report the tool's run time for
`table refs` and `fn stage_ref` as `time` measures it, and the tool-call
count from your own report. Do not touch `tests/rota/walks.jsonl` or
`You are a standby peer.md`.
