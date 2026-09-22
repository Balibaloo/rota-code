# A key miss is recorded, in its own table

Frame 64, the user prompt is the other half of the cassette key. Design
record, revision 1, written 2026-09-22 by session 41cb5184. Meta workflow.
The design review reads this record and
`plans/scope-case-runs-readers-2026-09-22.md` before any code.

## 1. The fault, in one paragraph

A replay that finds no cassette at the current key writes nothing to the
register. `record_case_run` returns early when `_is_unmeasured` is true
(observed: `rota/llm/cassettes.py:447`, 2026-09-22). The report then reads
the older rows at the same `prompt_hash`, `model` and `system_hash`, and the
case reads green. The gate's stale set is the report's `STALE` and `NEW`
states (observed: `rota/tools/gate.py:115-132`, 2026-09-22), so the case
never enters it. The suite's own test fails with `STALE <case>: no recording
for the current prompt`, and the gate counts that as a red. **So the two
instruments contradict each other: the acceptance line "zero stale" holds
while a case is unmeasured, and the red count carries a case that nobody
measured.** Any key miss the report does not itself compose is invisible to
it. The user half of the key is one such miss. A pin the key omits, frame
65, is another.

## 2. What the scope report showed

The first design was a sentinel row in `case_runs`. The scope report tables
25 readers of that table against three shapes of sentinel row (observed:
`plans/scope-case-runs-readers-2026-09-22.md`, section 3, 2026-09-22).

- A `passed = 0` row with the miss text corrupts 15 readers. A `measured`
  column corrupts 18. A sentinel in a key column corrupts 17.
- Twelve readers filter on `case_id` or on nothing, so every shape edits
  twelve readers (fact 3).
- `matching_runs` windows on `ORDER BY seq DESC LIMIT runs`, so a sentinel in
  the window displaces a real row and reads `FAIL` (fact 4).
- `passed` is `INTEGER NOT NULL`. A NULL needs a table rebuild over 136455
  rows, raises `TypeError` in four readers, and skews `flip_history` (fact 6).
- `holds_a_system_hash` is global, and a sentinel with a real digest widens
  the match for the whole register (fact 10).
- No test pins the early return (fact 18).

**Conclusion: the miss is not a run, and it does not go in the runs table**
(reasoned: every reader of `case_runs` reads it as "what has been measured",
and a miss measured nothing). A separate table leaves all 25 readers
unchanged.

## 3. The repair

Three changes and one predicate.

### 3.1 A table

```sql
CREATE TABLE IF NOT EXISTS key_misses (
    seq          INTEGER PRIMARY KEY,
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    system_hash  TEXT NOT NULL,
    num_ctx      INTEGER NOT NULL,
    temperature  REAL NOT NULL,
    protocol     TEXT NOT NULL,
    extras       TEXT NOT NULL,
    load_id      TEXT NOT NULL,
    reason       TEXT NOT NULL,
    at           TEXT NOT NULL
);
```

One row per unmeasured run. The row carries the whole key the run tried,
the same columns `case_runs` carries, so a reader can ask "did the last look
try the key the tree composes now". `reason` is the first problem string,
which today is `no cassette for <model> key=<12 chars>…` or an
`LLMUnavailable` connection message. `at` is the clock, ISO, because a miss
is an observation and an observation ages.

`open_dev_db` creates the table beside `case_runs` (observed: the `CREATE
TABLE IF NOT EXISTS` block at `rota/llm/cassettes.py:54`, and the column
migration at `:121-140`, 2026-09-22). A pulled register from the snapshot
store has no schema version, so a reader never assumes the table exists.

### 3.2 The writer

`record_case_run` writes a `key_misses` row where it returns early today
(observed: `rota/llm/cassettes.py:447`, 2026-09-22). The guard
`_is_unmeasured` stays as the one definition of "unmeasured". The row is
written with the same `pins`, `system` and `protocol` the run row would have
carried. The early return stays: no `case_runs` row is written. **The
write-time guard's reason still holds**: a `passed = 0` row would turn an
unmeasured case into a hard red, and this design writes none.

### 3.3 The predicate

`records_misses(conn) -> bool`: the table exists, read from
`sqlite_master`. It sits beside `carries_the_key` and `holds_a_system_hash`
in `rota/tools/casestatus.py`. A reader that finds no table reads as today.
The cockpit's L1 panel connects raw (observed: `rota/cockpit/progress.py:261`,
2026-09-22), so the panel calls the predicate before it names the table.

### 3.4 The reader

One rule in `casestatus.status`, after `here` and `ever` are read:

> **When a miss at the case's current `prompt_hash` and `model` is newer than
> the newest matching run, the case is `STALE`, and `why` carries the miss's
> reason and time.**

`matching_runs` returns `passed, problems` today (observed:
`rota/tools/casestatus.py:193`, 2026-09-22). It returns `seq` as well, so the
newest matching run has a sequence to compare. The misses are read once per
case:

```sql
SELECT seq, reason, at FROM key_misses
WHERE case_id = ? AND model = ? AND prompt_hash = ?
ORDER BY seq DESC LIMIT 1
```

The comparison is on `seq` across the two tables. **The two tables share
one sequence**: `key_misses.seq` is allocated from
`MAX(case_runs.seq, key_misses.seq) + 1`, the way `record_case_run`
allocates today from `MAX(seq) + 1` (observed: `rota/llm/cassettes.py:449`,
2026-09-22). Two sequences would need the clock to order them, and the clock
is not a sequence.

Three cases, and the report's state for each:

| Rows | Miss | State | `why` |
| --- | --- | --- | --- |
| none | none | `NEW` | empty, as today |
| none | any | `NEW` | `looked <at>, key missed: <reason>` |
| some, matching | newer than the newest | `STALE` | `looked <at>, key missed: <reason>` |
| some, matching | older than the newest | as today | as today |

`NEW` keeps its meaning, nobody has measured this case. The miss adds a
sentence to it and does not change the state, so the gate's set does not
move for a never-measured case: it already holds `NEW`. `STALE` keeps its
meaning, the text moved since the case was measured. The miss says the same
thing from the other side: somebody tried the current text and no recording
answered.

The `LLMUnavailable` connection case reads the same way. A stopped server
is a look that measured nothing, and the reason says so. The report's
count line gains nothing: the miss is a `why`, not a state.

## 4. What this design does not do, and why

**It does not compose the user prompt.** Frame 64's title says the user
half of the key is unmatched. It is composable, from `push_working_set` and
`resolve_inbound` over the case's seeded database. Ten `repo:` cases need a
git worktree for it (observed: frame 63's status of 2026-09-22 17:22, where
the preview raised for 10 such cases). Frame 63 measured the session setup
with worktrees at 67 seconds for 128 cases, and the cockpit panel calls the
same reader. So a composed user half in the reader is a panel fault or a
cache, and either is its own design.

**What the miss record gives instead.** Every gate run replays first, so
the gate's stale line is current on every run: a drift in the user half
misses the key, the miss is written, and the case reads `STALE` in the same
run. **What it does not give**: a person who edits `push_working_set` and
reads the report or the panel with no suite run in between still sees
green. The system half does not have that gap, because frame 63's reader
composes it on every read. **Roman ruled the write-off** (ruled: Roman,
2026-09-22, asked with three options and this one recommended: the gate
replays first, so the miss record catches the drift on every gate run, and
the cold read is the one gap that remains). The user-half composition is
written off in this frame with that reason, and no frame carries it.

**It does not touch `toolcheck`.** The scope report's fact 13 says
`toolcheck` formats its error with `str()` and loses the `LLMUnavailable`
marker, so a connection failure on a `T0-PROVIDER` case writes a red today.
That is a second writer's fault and not this frame's. It is noted for a
frame of its own.

**It does not migrate misses.** `migrate_register` rebuilds `case_runs`
from cassettes. A miss is evidence about one tree at one time and it has no
cassette to rebuild from. A migrated register starts with an empty
`key_misses`, which reads as "nobody has looked since the migration", and
that is true.

**It does not count misses in the manifest.** `cassette_store` compares
`(cassettes, case_runs)` against the published manifest (observed:
`rota/testkit/cassette_store.py:326-332`, 2026-09-22). Misses are not
evidence and do not invite a publish.

## 5. What this costs each reader

- `casestatus.status`: one `SELECT ... LIMIT 1` per case over an indexed
  small table, 128 queries. Under 20 ms (reasoned: the table holds one row
  per miss and a miss is rare). The report's 10 s ceiling is untouched.
- The cockpit's L1 panel: the same query behind the predicate.
- Every other reader of `case_runs`: nothing. The table is not read.

## 6. The acceptance

1. A replay that misses the key writes one `key_misses` row and no
   `case_runs` row. A test asserts both counts.
2. A case with matching green rows and a newer miss reads `STALE`, and its
   `why` names the reason and the time. A test builds the register by hand
   through `record_case_run`, and never by raw insert, so the row is one the
   writer makes (frame 64's status of 19:23: a probe of a state the code never
   reaches measures the probe).
3. A case with a miss and a newer matching green reads green. The miss is
   history.
4. A never-measured case with a miss reads `NEW`, with the miss in `why`.
5. A register without the table reads as today. A test opens a register that
   lacks it and asserts the predicate is false and `status` raises nothing.
6. The gate's stale set holds a case whose last replay missed the key
   (observed through `gate._stale` on a register built by the writer).
7. The probe from frame 64's push: edit `push_working_set`, run one `L1`
   case's replay, and the case reads `STALE` with `key missed` in `why`.
   Revert the edit.
8. The whole report costs under 10 s, measured as frame 63 measured it.
9. The tests that pin the guard exist: `_is_unmeasured` is named by a test,
   and the early return from `record_case_run` is asserted.

## 7. What is not in this frame

- The user-half composition. Section 4 says why, and Roman rules where it
  goes.
- `toolcheck`'s lost marker. Section 4.
- Frame 65's pin: `think` absent from the key. A miss records the key the
  run tried, including `extras`, so frame 65's repair will make every case
  miss once and the misses will say so. That is the wanted behaviour and it
  is not this frame's work.
- Frame 66's replay counts. The miss table adds no rows to `case_runs`, so
  it neither helps nor worsens that frame.

## 8. Two questions for the design review

1. Is one sequence across two tables sound, or does a concurrent writer
   race on `MAX(seq) + 1`? `record_case_run` races the same way today, so
   the answer is "no worse", unless the review finds a path where two
   processes write the register at once.
2. Should the miss carry the first problem string or the whole list? The
   first is what `casestatus` prints for `FAIL` today
   (observed: `rota/tools/casestatus.py:345-347`, 2026-09-22).

## 9. Estimate

The repair and its tests, one implementer pass, 60k (reasoned: one table,
one writer branch, one predicate, one reader rule, nine tests, and no
reader of `case_runs` changes). The design review, 100k. No re-record: the
design writes nothing that a re-record would move.
