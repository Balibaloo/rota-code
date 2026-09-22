# A key miss is recorded, in its own table

**Revision 3, 2026-09-22 20:40: this design is the repair again** (ruled:
Roman, "Ok, as long as it's tracked properly", after frame 64's count).
Between 20:09 and 20:40 Roman had ruled the whole cassette key composed
cold instead, because under this design the report is history and answers
as of the last replay. **The count reversed that** (observed: every case run
against a capturing replay, 2026-09-22). The cassette key is per turn, and
turn N depends on the reply at turn N-1, so a cold read composes turn 1
only. Turn 1 hits for 128 of 128 cases, 10 cases miss on a later turn, and
7 of those read green. A cold turn-1 key would read all 128 as matched. The
suite's replay is the only instrument that sees the whole key, and this
design is how the replay tells the report. The cold turn-1 key is parked on
the stack with its trigger, a count that shows turn-1 drift.

**The observed instance** (observed: `probe64_miss.py` on
`L1-VK-an-outside-fact-is-the-researchers`, 2026-09-22). The recorded turn
4 carries `OK problem.assert -> unchanged since you asked earlier this
session; the answer is above.` The tree composes `... this session. What
problem.assert returned then still stands.` A tool's reply was reworded, the
user half of the key moved, and the report reads `FAIL 0/5` for a case
nobody has measured at the current key. Acceptance 8's probe can use this
case as it stands, with no edit to `runner.py`.

The other 9 later-turn misses are a fresh commit sha in `code.commit`'s
reply, frame 70, and no key design touches them.

Frame 64, the user prompt is the other half of the cassette key. Design
record, revision 2, written 2026-09-22 by session 41cb5184. Meta workflow.
Revision 1 was reviewed the same day and section 9 lists what changed. The
implementer reads this record and
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
and a miss measured nothing). A separate table leaves 22 of the 25 readers
unchanged. The three that change are `matching_runs`, `status` and the
cockpit's `l1` panel, and section 3.4 says how.

## 3. The repair

One table, one constant, one writer branch, one shared reader function, one
predicate.

### 3.1 A table

```sql
CREATE TABLE IF NOT EXISTS key_misses (
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    run_no       INTEGER NOT NULL,
    system_hash  TEXT NOT NULL,
    num_ctx      INTEGER NOT NULL,
    temperature  REAL NOT NULL,
    protocol     TEXT NOT NULL,
    extras       TEXT NOT NULL,
    load_id      TEXT NOT NULL,
    kind         TEXT NOT NULL,
    reason       TEXT NOT NULL,
    at           TEXT NOT NULL,
    seq          INTEGER NOT NULL,
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);
```

One row per unmeasured run. The row carries the whole key the run tried,
the same columns `case_runs` carries, so a reader can ask "did the last look
try the key the tree composes now". The primary key is the shape of
`case_runs`'s own (observed: `rota/llm/cassettes.py:91`, 2026-09-22), and
it is the index the reader's query uses. **`seq` is not a primary key on its
own.** Four tier files write the live register from four xdist workers
during a gate run, so two writers can allocate one `seq` (observed: the
design review's probe, four processes and 400 inserts each, 2 duplicate
`seq` values, 2026-09-22). A single-column primary key would refuse the
second insert inside a tier test and the gate would count a new red.

`kind` is `no cassette` or `unreachable`. `reason` is the problem string
that carries the marker, not the first problem string: `check` writes its
complaints first and `session did not commit: [...]` last (observed:
`rota/testkit/fixtures.py:1046-1050`, 2026-09-22), so `problems[0]` is
`expected a call to X` and not the miss. `at` is the clock, ISO, because a
miss is an observation and an observation ages.

`open_dev_db` creates the table beside `case_runs`, in `DEV_SCHEMA`
(observed: `executescript(DEV_SCHEMA)` at `rota/llm/cassettes.py:117`,
2026-09-22). It is the only creator. `migrate_register` builds its target
through it, and the tier fixtures open through it, so a pulled register
without the table gains it before the first miss is written. The snapshot
store has no schema version, so a reader never assumes the table exists.

### 3.2 One constant for the two markers

```python
MISS_MARKERS = {"no cassette": "no cassette for", "unreachable": "LLMUnavailable"}
```

`_is_unmeasured` reads it. The `kind` of a miss derives from it. The `LIKE`
clause in `matching_runs` at `rota/tools/casestatus.py:213-214` reads it,
so the second copy of the rule that names only `no cassette for` goes. Frame
60 and frame 54 both record what a second copy of a match costs.

### 3.3 The writer

`record_case_run` writes a `key_misses` row where it returns early today
(observed: `rota/llm/cassettes.py:447`, 2026-09-22), then returns. No
`case_runs` row is written. **The write-time guard's reason still holds**: a
`passed = 0` row would turn an unmeasured case into a hard red, and this
design writes none.

**One sequence across two tables, allocated in one statement.**
`key_misses.seq` and `case_runs.seq` share one counter, so "newer" is a
comparison on `seq` and never on the clock. The allocation is an
`INSERT ... SELECT COALESCE(MAX(s), 0) + 1 FROM (SELECT MAX(seq) s FROM
case_runs UNION ALL SELECT MAX(seq) FROM key_misses)`, one statement, so
the write lock is held while the maximum is read. The run row's allocation
at `rota/llm/cassettes.py:449-452` moves to the same one-statement form.
Today it is two statements and it races (observed: the review's probe,
2026-09-22), and a run and a miss that tie on `seq` would make the rule
below read green for a case that missed. The tie is removed at the source.

### 3.4 The reader

One function beside `matching_runs`, called by `status` and by the
cockpit's `l1` panel:

```python
def latest_miss(conn, case, want, *, keyed, system) -> sqlite3.Row | None
```

It filters on the columns `matching_runs` filters on: `case_id`, `model`
and `prompt_hash` always, `system_hash` when `system` is given, and the four
pin columns `num_ctx`, `temperature`, `protocol`, `extras` when `keyed`. It
returns the newest such miss, `ORDER BY seq DESC LIMIT 1`, or `None`. **The
miss must match the key the runs match** (reasoned: the review's point 3,
2026-09-22). A narrower filter reads a false `STALE` twice: after a person
reverts a system-half edit, the old runs match again but a miss at the
other `system_hash` is newer; and a local run under another profile or
window writes misses that stale the suite's read under the gate's pins.
Frame 65's `think` pin makes the second case live.

`matching_runs` returns `seq` beside `passed` and `problems`. Both callers
read rows by name, so the added column is safe.

The rule, applied after the state is decided and before `why`:

> **When `latest_miss` returns a row whose `seq` is greater than the newest
> matching run's `seq`, the case is `STALE`, whatever state it reached, and
> `why` carries the miss.** With no matching run, the state stays what it
> was, `NEW` or `STALE`, and `why` carries the miss.

The `why` sentence is `looked <at>, <kind>: <reason>`. The precedence for
`why` is: `replay_problem` first, then the miss, then the `FAIL` problem.
`render` cuts `why` at 96 characters (observed: `rota/tools/casestatus.py:389`,
2026-09-22), so the sentence leads with the time and the kind and the reason
is what gets cut.

| Rows | Miss at the key | State | `why` |
| --- | --- | --- | --- |
| none | none | `NEW` | empty, as today |
| none | any | `NEW` | the miss |
| some, none matching | any | `STALE`, as today | the miss |
| some matching | newer than the newest | `STALE` | the miss |
| some matching | older than the newest | as today | as today |

`NEW` keeps its meaning, nobody has measured this case. `ever` counts
`case_runs` only, so a miss-only case stays `NEW` and the gate's set does not
move for it: it already holds `NEW` (observed: `rota/tools/gate.py:131-132`,
2026-09-22). `STALE` keeps its meaning, the text moved since the case was
measured. The miss says the same thing from the other side.

**After a revert, one run of `STALE`.** A person edits `push_working_set`,
the replay misses, then reverts. The old runs match again and the miss at
the same key is still newer, so the case reads `STALE` until the next replay
writes runs. That is the safe direction, and it is one run wide.

**The panel.** `l1` never calls `status`. It calls `matching_runs` directly
(observed: `rota/cockpit/progress.py:244`, 2026-09-22). So it calls
`latest_miss` too, and applies the same rule, or the two instruments
disagree again, which is the fault frame 54 repaired. The panel connects
raw, and its `except sqlite3.Error` turns a missing table into `never run`
for every case in silence (observed: `rota/cockpit/progress.py:252`,
2026-09-22). So the predicate below runs once, beside `keyed` and `widen`,
and the panel names the table only when it is true.

### 3.5 The predicate

`records_misses(conn) -> bool`: the table exists, read from
`sqlite_master`. It sits beside `carries_the_key` and `holds_a_system_hash`
in `rota/tools/casestatus.py`. A reader that finds no table reads as today.
`status` opens through `open_dev_db`, which creates the table, so the
predicate matters to the panel and to a raw reader.

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

**It does not prune misses.** A gate run on a stale key writes one miss per
case per run, so cases × runs rows, about 640 for 128 cases at 5 runs. A
tree left stale for many gate runs grows the table by that much each run.
The reader's query walks the primary key and reads one row, so the cost
stays flat. The growth is bytes, and the record says so rather than
designing a pruner nobody has asked for.

## 5. What this costs each reader

- `casestatus.status`: one `SELECT ... ORDER BY seq DESC LIMIT 1` per case
  over the primary key, 128 queries. Under 50 ms at any table size the
  register can reach (reasoned: the query walks one key prefix and reads
  one row). The report's 10 s ceiling is untouched.
- The cockpit's `l1` panel: the same query behind the predicate, once per
  case.
- `matching_runs`: one more column in its `SELECT`.
- Every other reader of `case_runs`: nothing. The table is not read.

## 6. Where a miss comes from, and where it does not

A replay run never reaches a server. `ReplayOnlyBackend` reads cassettes
only (observed: `rota/llm/cassettes.py:338-353`, 2026-09-22), so a replay
miss is always `no cassette`. The `unreachable` kind arises under `ROTA_L1`
only, where `RecordingBackend` calls the model, and a stopped server then
writes cases × runs `unreachable` rows. Under `ROTA_REFRESH` the backend
skips the lookup and records, so a connection failure there is not a key
miss and the guard's reason still names it unmeasured. Both kinds are looks
that measured nothing, and the sentence names which.

## 7. The acceptance

1. A replay that misses the key writes one `key_misses` row and no
   `case_runs` row, with `kind = 'no cassette'`. A test asserts both counts
   and the kind.
2. A case with matching green rows and a newer miss reads `STALE`, and its
   `why` names the time, the kind and the reason. The test builds the
   register through `record_case_run` and never by raw insert, so the row
   is one the writer makes. The `register` fixture and `_record` in
   `tests/rota/test_register_key.py:65-85` already drive the writer with a
   real `Pins` (observed: the review's point 8, 2026-09-22).
3. A case with a miss and a newer matching green reads green. The miss is
   history.
4. A never-measured case with a miss reads `NEW`, with the miss in `why`.
5. A miss at another `system_hash`, or under other pins, does not stale the
   case when the read is widened or keyed. A test writes such a miss and
   asserts the state is unchanged.
6. A register without the table reads as today. A test opens a register that
   lacks it and asserts `records_misses` is false and `status` raises
   nothing. The panel's `l1` reads `never run` for no case because of the
   missing table.
7. The gate's stale set holds a case whose last replay missed the key,
   observed through `gate._stale` on a register built by the writer.
8. The probe from frame 64's push, **run after the night and never beside
   it**: change `pushed: dict[str, Any] = {}` at `rota/core/runner.py:1544`
   to carry one probe key, run one `L1` case's replay, and the case reads
   `STALE` with `no cassette` in `why`. Revert the edit. The probe leaves
   `runs` miss rows in the live register, and they are true.
9. `record_case_run` allocates `seq` in one statement for both tables. A
   test runs four processes against one register and asserts no duplicate
   `seq` across the two tables.
10. The whole report costs under 10 s, measured as frame 63 measured it.
11. The tests that pin the guard exist: `_is_unmeasured` is named by a test,
    and the early return of a `case_runs` row is asserted.
12. The cockpit's `l1` panel shows the miss in the case's `problems` list,
    so the two instruments read the same case the same way.

## 8. What is not in this frame

- The user-half composition. Section 4 says why, and Roman ruled it.
- `toolcheck`'s lost marker. Section 4.
- A pruner for `key_misses`. Section 4.
- Frame 65's pin: `think` absent from the key. A miss records the key the
  run tried, including `extras`, so frame 65's repair will make every case
  miss once and the misses will say so. That is the wanted behaviour and it
  is not this frame's work.
- Frame 66's replay counts. The miss table adds no rows to `case_runs`, so
  it neither helps nor worsens that frame.

## 9. What revision 2 changed

The design review of 2026-09-22 read revision 1 against nine points and
returned eight changes. All eight are in this revision.

1. `seq` is no longer a primary key on its own. The primary key is
   composite, and the allocation is one statement for both tables. The
   review's probe showed the race (section 3.1 and 3.3).
2. The miss filter matches the key `matching_runs` matches, so a revert or a
   run under other pins reads no false `STALE` (section 3.4).
3. One function, `latest_miss`, serves `status` and the panel (section 3.4).
4. A `kind` column and one constant for the two markers. `reason` is the
   string that holds the marker (section 3.1 and 3.2).
5. The primary key is the index. The cost section says the table grows by
   cases × runs per gate run on a stale key, and nothing prunes it
   (section 4 and 5).
6. The table row "rows some, none matching" and the `why` precedence
   (section 3.4).
7. A stopped server arises under `ROTA_L1` only and writes cases × runs
   rows. Under `ROTA_REFRESH` it is not a key miss (section 6).
8. Acceptance 8 names the edit at `runner.py:1544` and schedules the probe
   after the night.

## 10. Estimate

The repair and its tests, one implementer pass, 80k (reasoned: one table,
one constant, one writer branch with the one-statement allocation, one
shared reader function, one predicate, one panel call, and twelve
acceptance lines). The design review cost 134k against a 100k cap. No
re-record: the design writes nothing that a re-record would move.
