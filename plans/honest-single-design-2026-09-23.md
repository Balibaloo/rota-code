# A case carries one verdict, from one live call, with its date

Frame 66, a sample of five is one measurement. Design record, revision 1,
written 2026-09-23 by session 9fe32e55. Meta workflow. The implementer
reads this record and `plans/scope-case-runs-readers-2026-09-22.md`, the
reader table of frame 64, before any code.

**Ruled: the honest single** (ruled: Roman, 2026-09-23 04:27, asked with a
real sample of five and a print-only change). The threshold goes. A case
carries the verdict of its newest row under the current key, the report
says whether that row was a live call or a replay, and it prints the date
of the newest live call. `trust` confirms on two live loads.

## 1. The fault, in one paragraph

`run_sampled` runs a case `runs` times, five for every case in the register,
and the tier asserts `passed >= threshold` (observed: `rota/testkit/fixtures.py:1230-1254`,
`tests/rota/test_l1.py:187`, 2026-09-23). Every tier pins `temperature=0.0`.
`RecordingBackend.complete` keys a call on model, temperature, window,
protocol, system text, user text and extras, and replays a hit before it
calls out (observed: `rota/llm/cassettes.py:175-193, 317-351`). So run 1
records and runs 2 to 5 replay it in the same process. The register holds
170,435 rows in `case_runs`, 2,591 first-seen transcripts and 167,844 copies
(observed: a count by transcript identity, 2026-09-23 04:03). No case has
ever scored anything but 5 of 5 or 0 of 5. The threshold `need 4` decides
nothing, and `trust` promotes a provisional green to earned when a gate run
two hours later replays the same cassette under a new `load_id`: 100,448 of
the copies sit in a later load than their original.

## 2. What the read showed

1. The register cannot tell a live row from a copy. A transcript is
   `{"say": text}` per turn from `RunOutcome.completions`, and the backend
   name that `Completion` carries, `cassette:<inner>` on a replay, is
   dropped before the write (observed: `rota/testkit/fixtures.py:669-684`,
   `rota/core/runner.py:40-52`). Transcript identity is a proxy: at
   temperature 0 a live call that repeats an earlier answer counts as a
   copy under it. So a live flag is written at record time from here on,
   and the proxy is used once, to backfill.
2. Each run holds its own backend. `run_sampled` calls `backend_factory()`
   per run and `run_chain` calls it per leg (observed:
   `rota/testkit/fixtures.py:1102, 1251`). `RecordingBackend` counts
   `hits` and `misses` on the instance. `misses` is the number of calls
   that reached the model. `ReplayOnlyBackend` and `ScriptedBackend` carry
   no counter, and a run on them made no live call.
3. The date of a call is not stored. `key_misses` carries `at`, and
   `case_runs` carries only `load_id`, which is `model@epoch//7200`, a
   two-hour window (observed: `rota/llm/cassettes.py:458-469`). The window
   is a date at two-hour precision, so a row without `at` still has one.
4. The seats run at temperature 0.0 and nothing overrides it (observed:
   `rota/llm/llm.py:111`, no profile sets it). Frame 58 measured that a
   zero-temperature model repeats an identical prompt exactly across three
   sessions of ten turns. The spread the register can see is across loads
   and days, which frame 55 measured at one key. `flip_history` already
   groups by load.
5. The readers. Frame 64's scope report tables 25 readers of `case_runs`.
   The ones this design changes are R2 `flip_history`, R3 `trust`, R5
   `pass_rate_history`, R6 `open_dev_db`, R9 `matching_runs`, R12 and R13
   the report's state and score, R15 the cockpit panel, R17
   `benchmarks.from_register`, and the writer R1. The rest read counts or
   whole rows and change nothing, section 5 says why for each.

## 3. The repair

### 3.1 The row says whether it was live, and when

Two columns on `case_runs`, added by `open_dev_db` in the `KEY_COLUMNS`
pattern, so an old register catches up on open at no rewrite:

```
live  INTEGER NOT NULL DEFAULT 0   -- 1 when at least one call reached the model
at    TEXT    NOT NULL DEFAULT ''  -- the clock at the write, '' before the column
```

`record_case_run` takes two keyword-only arguments, `live: bool` and no
other. It writes `at` itself from `time.strftime`, the way `key_misses`
does. `live` has no default. A writer that does not say is a writer that
has not thought about it, and there are six: `test_l1.py:152`,
`test_l3.py:118`, `test_gauntlet.py:98`, `test_t1_liaison.py` at four
sites, `cli.py:620-624`, and the tests in `test_register_key.py` and
`test_case_trust.py`.

`CaseResult` gains `live_calls: int`. `run_case` reads
`getattr(backend, "misses", 0)` after the session. `run_chain` keeps every
backend `_one` makes and sums their `misses`. A tier passes
`live=r.live_calls > 0`. The T1 tier and the tool check run on a
`RecordingBackend` and read the same counter. A replay-only run writes
`live = 0` and says so.

### 3.2 The threshold goes, and a case runs once

`run_sampled` returns `list[CaseResult]`. `runs` defaults to 1 and
`ROTA_RUNS` still overrides it for a smoke of a new column. `pass` is not
read. The tier asserts `all(r.passed for r in results)` with the same
message it prints now, per run. Chains run once too: `run_chain` makes one
worktree per run, so one run is one worktree.

The 128 case files carry `runs: 5` and `pass: 3` or `pass: 4` (observed:
`grep` over `tests/rota/cases/*.yaml`, 2026-09-23, 128 and 55 plus 73).
Both lines go, by a sweeper script over the files, and the diff is read
once for the judgement cases. A case that keeps a `runs:` line is a case
that wants more than one session for a reason it states in its comment.
None does today.

A gate then runs one session per case instead of five. The replays cost
nothing, the harness around them does: `init_db`, a seed, a worktree, a
session, a capture, five times per case. The gate's time line before and
after is part of the acceptance, and the number is not predicted here.

### 3.3 The report reads the newest row and names the newest live call

`matching_runs` keeps its key match and its window, and gains
`live: bool | None = None`. `None` matches every row, `True` matches
`live = 1`. `status` reads:

- `here = matching_runs(conn, case, want, system=system, limit=1)`, the
  newest row under the current key. Its `passed` is the verdict.
- `live_row = matching_runs(..., live=True, limit=1)`, the newest live
  row under the key. Its `at`, or its `load_id`'s window when `at` is
  empty, is the date. Its `seq` bounds the replay count: the rows under the
  key with a greater `seq` are replays since.
- The states keep their names. `NEW` and `STALE` are as today: no row
  under the key. `FAIL` and `green` come from `here[0]`. `PROV` comes from
  `trust`. The shrunk-denominator rule, `len(here) < threshold <=
  len(narrow)`, goes with the threshold. It caught a partly migrated
  register rendering `2 of 2`. Under one verdict the newest current row
  decides, and a legacy row it drops is a row about a key the tree does
  not send.
- A case whose newest row under the key is a replay and which has no live
  row under the key is `STALE`. That is a register swapped in without its
  live rows, and the line says `no live call at this key`. The backfill in
  3.5 makes this state empty on the committed register.

The line the report prints, one per case:

```
  green  live 2026-09-23 02:38, replayed 12x since   L1-LI-ratify
  FAIL   live 2026-09-23 03:53                       ACT-TS-five-criteria-one-per-reply
  STALE    -                                         L1-VK-reopen-after-an-election
```

The `need` column and the `passed/of` score go. The footer's five counts
stay. The advice line for stale cases stays. The `why` line stays.

### 3.4 `trust` confirms on live loads

`flip_history` adds `WHERE live = 1` and groups as today. A group is then
one live call per load in the normal case, and the bar `ok / n >= 0.8`
reads a single row's verdict. The bar stays as arithmetic, because a
`ROTA_RUNS` smoke writes several live rows per load and the bar reads
them. `trust` changes nothing. A provisional green is confirmed when a
second load's live call passes, which is what the 2026-08-27 ruling said.
`pass_rate_history` adds the same clause. `provisional_cases` reads
`trust` and changes nothing.

`tests/rota/test_case_trust.py` inserts five rows per load today. Its
`_runs` helper inserts live rows, one per verdict it lists, and the test
"the bar is the register's own, 4 of 5" becomes "one live row decides", a
`ROTA_RUNS` smoke of two live rows at 1 and 0 reads red.

### 3.5 The backfill, once, by a tool

`rota/tools/mark_live.py`, run once outside pytest, on the committed
register:

1. For each `(case_id, model, prompt_hash)`, walk the rows by `seq`. The
   first row of each distinct `transcript` gets `live = 1`. The rest keep
   `live = 0`.
2. `at` stays `''` for every backfilled row. The report reads the load
   window for it.
3. Print the counts: rows read, rows marked live, cases with no live row.
   The expected mark is about 2,591 (observed: the first-seen count of
   2026-09-23 04:03, which is the same rule).

The write-off, stated in the tool's docstring: a live call that repeated an
earlier answer at temperature 0 reads as a copy after the backfill. That
loses a live row's date and never a verdict, because the copy and the
original agree by construction. The other choice was a full re-record, 414
live calls in 11m28s (observed: frame 65's re-record summary, 2026-09-23
02:38), and frame 55 measured that a re-record loses greens to drift. The
backfill keeps the evidence and marks it. One `UPDATE` over 170,435 rows
runs about 5 s (observed: the 4.72 s note at `rota/llm/cassettes.py:160`),
and the tool runs alone, so no xdist worker meets the lock.

### 3.6 The cockpit and the benchmark

`progress.l1` (R15) fills `entry["live_at"]`, `entry["replays"]` and
`entry["live"]`, and drops `threshold` and `runs`. `panels.js:1143-1144,
1173, 1263` render `passed/runs` and `needs`. They render the verdict, the
live date and the replay count instead. `benchmarks.from_register` (R17)
tallies the latest prompt's rows per `(case, model)`; it adds `live = 1`
to its `SELECT`, so a copy count is not a share of cases.

## 4. What this design does not do, and why

- It does not make the sample real. Ruled out: five live calls at
  temperature 0 on one load are five identical answers (frame 58), and a
  temperature above 0 measures a model the seats never run.
- It does not add `live` to `key_misses`. A miss made no call by
  definition.
- It does not change the cassette key or the cassette table. `hits` on a
  cassette is a count of replays already, per cassette and not per case.
- It does not touch `triage.last_runs` (R19). It reads transcripts newest
  first for a person, and a copy's transcript is the original's.
- It does not touch the migration tool (R20 to R22). It copies old rows
  and the backfill runs after it.
- It does not touch the cassette store (R23 to R25). It counts rows for a
  manifest.

## 5. What this costs each reader

| Reader | Change | Why |
| --- | --- | --- |
| R1 `record_case_run` | two columns, one required argument | 3.1 |
| R2 `flip_history` | `WHERE live = 1` | 3.4 |
| R3 `trust` | none | reads R2 |
| R4 `provisional_cases` | none | reads R3 |
| R5 `pass_rate_history` | `WHERE live = 1` | 3.4 |
| R6 `open_dev_db` | two `ALTER TABLE` in the pattern | 3.1 |
| R7, R8 the key checks | none | schema presence, and the new columns join `KEY_COLUMNS` or a sibling tuple |
| R9 `matching_runs` | a `live` filter, and `limit` used by the caller | 3.3 |
| R10, R11 `ever`, `narrow` | `narrow` goes with the shrunk rule; `ever` stays | 3.3 |
| R12, R13 state, score, why | the verdict from one row, the date, the replay count | 3.3 |
| R14 `gate._stale` | none | reads the states, which keep their names |
| R15 `progress.l1` | three fields in, two out | 3.6 |
| R16 `progress._runs` | none | reads the YAML source text for the panel, and the sweep changes that text |
| R17 `benchmarks.from_register` | `live = 1` | 3.6 |
| R18 `from_tool_check` | none | one row per check, written live |
| R19 to R25 | none | section 4 |

## 6. The acceptance

1. `python -m rota.tools.casestatus --model qwen3:8b` on the backfilled
   register prints one verdict per case with a live date and a replay
   count, no `need` column, and the same five footer counts in kind. The
   counts before and after are in the status line, with the reason for
   every case whose state moved.
2. The backfill's printed counts, and the count of cases with no live row,
   which is expected to be 0.
3. `provisional_cases` before and after the backfill, with the reason for
   each change. A case that was `earned` on a replayed second load reads
   `provisional` after, and that is the design working.
4. A new test in `test_register_key.py`: a run on `ReplayOnlyBackend`
   writes `live = 0`, and a run on `RecordingBackend` whose inner backend
   is called once writes `live = 1` and a non-empty `at`.
5. The sweep's diff stat: 128 files, `runs:` and `pass:` lines removed,
   nothing else.
6. The gate's five lines on the closing commit: stale 0, and no new red
   beyond frame 65's three. The time line, against 509.4 s (observed:
   frame 71's gate, 2026-09-23).
7. The diff review on a worktree at the closing commit, before the close.
   No walk: the register is the meta workflow's instrument and no seat
   reads it.

## 7. What is not in this frame

- The temperature the seats run at, frame 42.
- A count of live calls per gate as a gate line. The report carries it.
- The `ROTA_RUNS` name, which `rota/paths.py:48` also reads as the runs
  directory. Two readers of one variable with two meanings is a fault, and
  a separate frame.

## 8. Estimate

From the anchors in `plans/operating-facts.md`. One implementer pass on
Opus, about ten files, one sweep and one tool: 90k to 110k, and a resumed
pass for the review's findings, 30k. The design review, 70k. The diff
review, 70k. This context, claim to close, about 120k. GPU: none.
