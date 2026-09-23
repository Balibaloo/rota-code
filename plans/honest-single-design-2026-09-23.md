# A row says whether it was live, and five runs are five problems

Frame 66, a sample of five is one measurement. Design record, revision 2,
written 2026-09-23 by session 9fe32e55. Meta workflow. Revision 1 was
reviewed the same day, and section 10 lists what changed. The implementer
reads this record and `plans/scope-case-runs-readers-2026-09-22.md`, the
reader table of frame 64, before any code.

**Ruled** (Roman, 2026-09-23, three rulings between 04:27 and 05:05):

1. Every `case_runs` row says whether a call reached the model, and when.
   The report prints a replay apart from a live call. `trust` reads live
   rows.
2. The five runs of a case become five problems: the fixture ids are
   salted with the run number, so each run composes its own prompt and
   records its own cassettes. The threshold stays and means something.
   Run 1 keeps today's ids, so the recorded register stays evidence about
   run 1.
3. The committed register is re-earned live after the code lands, under
   `ROTA_REFRESH=1`. No backfill.

## 1. The fault, in one paragraph

`run_sampled` runs a case `runs` times, five for every case, and the tier
asserts `passed >= threshold` (observed: `rota/testkit/fixtures.py:1230-1254`,
`tests/rota/test_l1.py:187`, 2026-09-23). Every tier pins `temperature=0.0`,
and `fill` gives a case the same ids every run on purpose (observed:
`rota/testkit/fixtures.py:797-806`). So run 1 records and runs 2 to 5 replay
it in the same process. No invocation of five runs has ever split: 8,841
groups of (case, model, prompt hash, load), 115 mixed, none of exactly five
rows (observed: the register, 2026-09-23 05:10). The register holds
170,435 rows, 2,591 first-seen transcripts and 167,844 copies. `trust`
promotes a provisional green when a gate run two hours later replays the
same cassette under a new `load_id`.

## 2. What the read and the review showed

1. The register cannot tell a live row from a copy. A transcript is
   `{"say": text}` per turn, and the backend name `cassette:<inner>` that
   `Completion` carries on a replay is dropped before the write (observed:
   `rota/testkit/fixtures.py:669-684`, `rota/core/runner.py:40-52`).
2. `RecordingBackend.misses` counts exactly the calls that reach
   `self.inner`: 1 of 2 on replay, 2 of 2 under `refresh=True`, and 1 when
   the inner call raises (observed: the design review's probe D,
   2026-09-23). `run_case` holds the backend as its parameter. `run_chain`
   drops each leg's backend at `fixtures.py:1101`. The T1 fixture is a
   `RecordingBackend` (`tests/rota/test_t1_liaison.py:71`). The tool check
   is not: `rota/cli.py:608` runs on `prof.backend()`, a bare provider
   backend that never replays (observed: probe D on `Profile.backend`).
3. A copy is re-judged by the checker of the day. 4,400 copies in 18 cases
   carry a verdict different from their original's, 780 of them in
   `L1-TE-survey-an-area-for-its-terms` (observed: the review's probe B,
   2026-09-23). Today 0 of the 65 newest copies disagree with their
   original. The hazard is a future checker edit.
4. The system text carries no fixture id: 0 of 121 single-session cases
   compose a system text that contains a filled id (observed:
   `system_text_for` over `casestatus._cases()`, 2026-09-23 05:00). So a
   salt moves the user half of the cassette key only, and the report's
   match on `system_hash` and `prompt_hash` stays per case.
5. All 293 distinct `load_id` values parse as `model@epoch//7200`. 60,820
   rows carry `''`. A window is UTC-aligned, so it prints 01:00 or 03:00
   local and never a minute (observed: probe A2).
6. `carries_the_key` tests `{KEY_COLUMNS names} <= have` (observed:
   `rota/tools/casestatus.py:121`). Two new columns in that tuple would
   make a register with the five and not the two read as unkeyed on the
   cockpit's raw connection, in silence (reasoned: the review, finding 5).
7. The cockpit builds its case list at `progress.py:663-684`, `cases()`,
   with `threshold` from `case.get("pass", ...)` and `history` from the
   last five rows across loads, and `panels.js:1170-1174, 1203-1204,
   1250-1256, 1262-1263` read that list. `test_progress.py` pins none of
   the four fields (observed: the review, point 6).
8. Writers of `case_runs` beyond the tiers: `tests/rota/test_discover.py:71`
   builds the table by hand with nine columns, and
   `rota/tools/migrate_register.py:294` copies old rows (observed: the
   review, point 1).

## 3. The repair

### 3.1 The row says whether it was live, and when

Two columns on `case_runs`, added by `open_dev_db` beside `KEY_COLUMNS`
in a sibling tuple `LIVE_COLUMNS`, never inside it (2.6):

```
live  INTEGER NOT NULL DEFAULT 0   -- 1 when at least one call reached the model
at    TEXT    NOT NULL DEFAULT ''  -- the clock at the write, '' before the column
```

`record_case_run` takes one new keyword-only argument, `live: bool`, with
no default. It writes `at` itself from `time.strftime`, as `key_misses`
does. The writers, each named because each must say:

- `tests/rota/test_l1.py:152`, `tests/rota/test_l3.py:118`,
  `tests/rota/test_gauntlet.py:98`: `live=r.live_calls > 0`.
- `tests/rota/test_t1_liaison.py` at four sites: the fixture's backend
  counter, the same way.
- `rota/cli.py:620-624`: `live=True`. The tool check never replays.
- `tests/rota/test_register_key.py`, `tests/rota/test_case_trust.py`,
  `tests/rota/test_discover.py:62-71`: the tests say which rows are live,
  and the hand-built table in `test_discover.py` gains both columns.
- `rota/tools/migrate_register.py:294` copies old rows and leaves the
  default. An old row is a copy of unknown provenance, and 0 says so.

`CaseResult` gains `live_calls: int`. `run_case` reads
`getattr(backend, "misses", 0)` after the session. `run_chain` keeps every
backend `_one` makes in a list and sums their `misses`. A backend without
the counter made no live call.

`casestatus.carries_live(conn)` is a predicate beside `carries_the_key`.
`matching_runs` gains `live: bool | None = None`; `None` matches every
row, `True` adds `AND live = 1`, and the clause is skipped with a
`STALE`-safe result when `carries_live` is False, so the cockpit's raw
connection never raises `no such column`.

### 3.2 Five runs are five problems: the salt

`fill(text, case_id, run_no=1)` salts every hole: the digest is
`sha1(f"{case_id}:{name}")` for run 1 and `sha1(f"{case_id}:{name}:{run_no}")`
for every other run. Run 1's ids are today's, byte for byte, so every
cassette and every `case_runs` row recorded so far stays evidence about
run 1, and `replayed_chain_text` in the report, which replays a chain
against the recordings, replays run 1's keys.

`load_case` keeps each case's unfilled block in a module registry,
`_RAW[case_id] = block text`, when it fills. `fixtures.for_run(case,
run_no)` returns `parse(fill(_RAW[case["id"]], case["id"], run_no))` when
the id is registered and `case` itself when it is not, so a case a test
builds by hand runs as it does today. `run_sampled` calls `for_run` per
run and passes the result to `run_case` or `run_chain`, and the result
carries through to `seed`, `_with_repo`, `wake_for`, `check` and every
expected value. The `fill` docstring's sentence on determinism changes to
say why run 1 is deterministic and the others are salted, and the test in
`tests/rota/test_fixtures.py` that pins the same ids every run, if one
does, pins run 1.

`run_case` and `run_chain` keep `run_no=1` as their default, and only
`run_sampled` calls `for_run`. So `replayed_chain_text` in the report,
which calls `run_chain(case, ...)` with the loaded case, replays run 1's
keys, and a refresh overwrites run 1's cassette at its key, so the replay
follows the newest run-1 reply (observed: the second look, point 3,
2026-09-23).

**Twelve cases carry no hole at all**, so `for_run` returns the same
bytes for every run and runs 2 to 5 would replay run 1 as today
(observed: the second look's scan of `tests/rota/cases/*.yaml`, point 1):
`L1-TE-survey-an-area-for-its-terms`,
`L1-AR-survey-a-signature-callers-rely-on`,
`L1-AR-survey-an-exception-contract`, `L1-AR-survey-a-patch-seam`,
`L1-AR-survey-a-shared-helper`, `L1-AR-survey-an-exported-name`,
`L1-TE-resurvey-an-area-that-moved`,
`L1-AR-a-boundary-file-read-outside-in`, `L1-AR-judge-the-frame`,
`L1-LI-say-what-the-run-could-not-see`, `L1-VK-orient-the-program`,
`L1-VK-reconcile-the-readme`. Each of the twelve gets `runs: 1` and
`pass: 1` in its file, because one problem is one run, and the line is
then true for every case. Twelve edits across a few files is a script.
Twenty-one further cases mix holes with a bare `t1`, `s1` or `a1`; those
ids stay the same on every run and nothing breaks, and they are left.

`runs: 5` and `pass:` stay in every other case file, and `run_sampled`
keeps its signature. The threshold reads real: four of five problems, not
four of five copies.

### 3.3 The report prints the score, the live date, and the replays

`status` keeps `here = matching_runs(conn, case, want, system=system)`,
the newest `runs` rows under the current key, and keeps the score
`sum(passed)/len(here)` against `need`. The shrunk-denominator rule stays,
because the threshold stays. It adds:

- `live_row = matching_runs(..., live=True, limit=1)`, the newest live row
  under the key. Its date is `at` when set, `~HH:00 window` from
  `load_id` when `at` is empty, and `date unknown` when both are (2.5).
  Rows under the key with a greater `seq` are replays since.
- A case with rows under the key and no live row is `STALE`, and the line
  says `no live call at this key`. Between the code landing and the
  re-record finishing, every case reads that way, and the acceptance reads
  the register after the re-record.
- Re-judged copies (2.3): for each row in `here` with `live = 0`, the
  report finds its original: the newest live row under the same key and
  the same `run_no` with a lower `seq`. A replay reads the cassette
  current at its time, and that cassette is the newest live row at that
  key and run before it, so the join is a prefix of the primary key and
  compares no blob (observed: the second look, point 4, 2026-09-23). When
  the verdicts differ, the `why` line says `re-judged: N of M replays
  differ from their live originals`, and the state is what the newest rows
  say. The checker of the day is the checker, and the line says the model
  did not move.

The line the report prints, one per case:

```
  green  5/5 (need 4)  live 2026-09-23 06:12, replayed 5x since   L1-LI-ratify
  FAIL   1/5 (need 4)  live 2026-09-23 06:31                      ACT-TS-five-criteria-one-per-reply
  STALE    -                                                      L1-VK-reopen-after-an-election
```

The footer's five counts stay. The advice line for stale cases stays.

### 3.4 `trust` reads live rows

`flip_history` and `pass_rate_history` add `WHERE live = 1`. A group is
then the live runs of one load, five problems under the salt and one for
each of the twelve hole-less cases that run once, and the bar
`ok / n >= 0.8` is the register's own bar over real runs. A group of one
row reads that row's verdict. `trust` changes
nothing. A provisional green is confirmed when a second load's live runs
pass, which is what the 2026-08-27 ruling said.

Consequence, stated: after the re-record every case has one live load,
tonight's, so `trust` reads every green as `earned` on one load with no
flip behind it, and the flip history restarts from tonight. The rows
before tonight stay in the table as copies of unknown provenance, and
`flip_history` does not read them. A reader who wants the old history
reads the rows.

`tests/rota/test_case_trust.py`'s `_runs` helper inserts live rows. The
tests keep their shapes, five rows per load, because the salt makes five
rows per load true again.

### 3.5 The re-record

After the code lands and the suite is green on replay for run 1, the
register is re-earned live. The commands are the ones `rerecord_command`
prints, with `ROTA_REFRESH=1`, per tier file:

```
ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 ROTA_REFRESH=1 python -m pytest tests/rota/test_l1.py -q
ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 ROTA_REFRESH=1 python -m pytest tests/rota/test_l3.py -q
ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 ROTA_REFRESH=1 python -m pytest tests/rota/test_gauntlet.py -q
```

and the T1 tier under its own switch. Under refresh every run is live, so
the count is about five times frame 65's 414 recordings, about 2,075
calls, about an hour on the 3080 at the 1.66 s per cassette that run
measured (observed: 414 in 11m28s, 2026-09-23 02:38). Some greens will not
return, and that is the ruled price. The old cassettes are overwritten at
their keys by `INSERT OR REPLACE`; runs 2 to 5 write new keys.

### 3.6 The cockpit and the benchmark

`progress.cases()` at `663-684` and `progress.l1` at `244-275` add
`live_at` and `replays` to each entry, keep `threshold` and `runs`, and
`panels.js:1143-1146` and `1262-1263` print the live date beside the score.
`caseState` at `1170-1174` is unchanged, because the threshold stays. A
test in `test_progress.py` pins `live_at` and `replays` on one entry.
`benchmarks.from_register` adds `live = 1` to its `SELECT`, so a share of
cases is a share of live runs. `progress._runs` at `719-736` reads the last
five rows for the detail panel and prints `live` beside each.

## 4. What this design does not do, and why

- It does not template values. A name, a path, a line of code and a
  criterion are cross-referenced, and a template that varies one must vary
  all of them with the check. Each case becomes a generator. Not ruled.
- It does not add `live` to `key_misses`. A miss made no call.
- It does not change the cassette key. The salt changes the user text,
  which the key already covers.
- It does not touch `triage.last_runs`. Its dedupe per `run_no` is right
  while runs stay five.
- It does not touch the migration tool beyond the writer note in 3.1, or
  the cassette store. `check_source`'s column count moves by two, and that
  is a runbook number.

## 5. What this costs each reader

| Reader | Change | Why |
| --- | --- | --- |
| R1 `record_case_run` | two columns, one required argument | 3.1 |
| R2 `flip_history` | `WHERE live = 1` | 3.4 |
| R3 `trust`, R4 `provisional_cases` | none | read R2 |
| R5 `pass_rate_history` | `WHERE live = 1` | 3.4 |
| R6 `open_dev_db` | two `ALTER TABLE` from `LIVE_COLUMNS` | 3.1 |
| R7 `carries_the_key`, R8 `holds_a_system_hash` | none; `carries_live` is a sibling | 2.6 |
| R9 `matching_runs` | a guarded `live` filter | 3.1, 3.3 |
| R10 to R13 the report | the live date, the replays, the re-judged line | 3.3 |
| R14 `gate._stale` | none | the states keep their names |
| R15 `progress.l1`, `cases()` | `live_at`, `replays` | 3.6 |
| R16 `progress._runs` | prints `live` per row | it reads `case_runs`, not YAML; revision 1's row was wrong |
| R17 `benchmarks.from_register` | `live = 1` | 3.6 |
| R18 `from_tool_check` | none; the writer passes `live=True` | 3.1 |
| R19 to R25 | none | section 4 |

## 6. The acceptance

1. Two runs of one case compose different user prompts and the same
   system text, and run 1's ids equal today's byte for byte: a test in
   `test_fixtures.py` over `for_run` and `fill`.
2. `check` passes on a salted run: the expected values follow the fill. A
   replay-only gate on run 1 before the re-record is green on every case
   that is green today, because run 1's keys did not move.
3. A run on `ReplayOnlyBackend` writes `live = 0`, and a run on
   `RecordingBackend` whose inner backend is called once writes `live = 1`
   and a non-empty `at`: a test in `test_register_key.py`. A chain sums its
   legs.
4. `python -m rota.tools.casestatus --model qwen3:8b` on the re-earned
   register prints, per case, the score against `need`, a live date from
   tonight, and a replay count; the footer's five counts before and after,
   with the reason for every case whose state moved.
5. `provisional_cases` before and after: after the re-record it is empty,
   for the reason in 3.4, and the status line says so.
6. The gate's five lines on the closing commit: stale 0, no new red beyond
   frame 65's three and the ones the re-record lost, each named.
7. The diff review on a worktree at the closing commit, before the close.
   No walk: the register is the meta workflow's instrument and no seat
   reads it.

## 7. What is not in this frame

- The temperature the seats run at, frame 42.
- Value templating, section 4.
- The `ROTA_RUNS` name, which `rota/paths.py:48` reads as a directory and
  `run_sampled` reads as a count. A fault, and a separate frame.

## 8. Estimate

From the anchors in `plans/operating-facts.md`. One implementer pass on
Opus, about twelve files, no sweep, no tool: 100k to 120k, and a resumed
pass for the review's findings, 40k. The second design look, resumed on
the salt sections, 20k. The diff review, 70k. The re-record, an hour of
GPU and no context. This context, claim to close, about 140k.

## 9. Revision 1's findings, and where each went

1. Backfill leaves 63 cases with no live row at the key: moot, no
   backfill. 2. The tool check has no counter: 3.1, `live=True`. 3. Copies
   are re-judged: 3.3, the re-judged line. 4. The bar over mixed live
   groups: moot under the salt, five real runs per load; the `ROTA_RUNS`
   smoke is unchanged. 5. `KEY_COLUMNS` and the raw connection: 3.1,
   `LIVE_COLUMNS` and `carries_live`. 6. The cockpit's builder: 3.6, and
   the threshold stays. 7. `test_discover.py`'s hand-built table: 3.1. 8.
   `triage.last_runs` per `run_no`: moot, runs stay five. 9. The date's
   three branches: 3.3. 10. R16's reason: section 5.

## 11. The second look, on the salt

Resumed on the same reviewer, four points, 14 tool calls, 3 minutes
(observed: 2026-09-23). The salt reaches every expected value, because
`fill` runs on the whole block before the parse and every derived id such
as `e_<m_in>` has a matching hole in the same block, 0 mismatches over 128
blocks. No caller mutates a loaded case, so the registry is safe. The
chain replay in the report follows run 1. The changes it made to this
record: the twelve hole-less cases run once (3.2), the re-judged join is
on the key prefix and not on the transcript (3.3), and 3.4's line on the
bar names the twelve.

## 10. What revision 2 changed

Revision 1 dropped the threshold and one run per case, swept `runs:` and
`pass:` from 128 files, and backfilled the register by first-seen
transcript. Roman ruled the salt instead, at 05:05, after asking whether
the runs swapped values in. They did not, and now they do. The threshold
and the five runs stay, the sweep and the backfill go, the register is
re-earned live, and sections 3.2, 3.5 and 9 are new.
