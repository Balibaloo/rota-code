# Scope: every reader of `case_runs`, against three sentinel shapes

Frame 64, the scope report. Written 2026-09-22. Read-only on the code.

The question: `record_case_run` drops a run that measured nothing. Frame 64
wants to write that run down. Three shapes are on the table. This report says
what each shape does to each reader. It chooses no shape.

---

## 1. The writer and the guard

1. The table is `case_runs` (observed: `rota/llm/cassettes.py:54`).
2. `passed` is `INTEGER NOT NULL` (observed: `rota/llm/cassettes.py:64`).
3. The primary key is `(case_id, model, prompt_hash, run_no, seq)` (observed:
   `rota/llm/cassettes.py:91`).
4. The one writer is `record_case_run` (observed:
   `rota/llm/cassettes.py:433`). The migration tool writes the table too, and
   it copies old rows rather than measuring (observed:
   `rota/tools/migrate_register.py:274`).
5. The guard is `if not passed and _is_unmeasured(problems, transcript):
   return` (observed: `rota/llm/cassettes.py:447`). A passing run is always
   written, whatever its text.
6. `_is_unmeasured` joins `problems` and the JSON of `transcript`, then looks
   for `no cassette for` or `LLMUnavailable` (observed:
   `rota/llm/cassettes.py:375-379`).
7. `LLMUnavailable` reaches the text because the runner appends
   `f"session failed: {exc!r}"`, and a repr carries the class name (observed:
   `rota/core/runner.py:2997`).
8. A writer that formats the same exception with `str()` loses that marker.
   `toolcheck` is such a site: it stores `f"error: {exc}"` (observed:
   `rota/llm/toolcheck.py:83`). So an unreachable model already writes a
   `passed = 0` row for the native leg of the tool check (reasoned: the
   message carries neither marker, so the guard cannot fire).
9. A dropped run is invisible everywhere. A recorded run gets the current
   `prompt_hash`, the current `load_id`, the current pins and a real
   `system_hash`, because the miss happens after `build_prompt` (reasoned:
   the model call is the last step, and `CaseResult.system_text` reads the
   outcome at `rota/testkit/fixtures.py:669`).
10. Point 9 is the whole difficulty. A sentinel row matches every key filter
    a reader applies, so no reader rejects it by accident.

---

## 2. The readers

Twenty-two readers. Grep found nineteen. This report adds `trust`,
`carries_the_key` and the `seq` allocator inside the writer.

### R1. `rota/llm/cassettes.py:449` — `record_case_run`, the seq allocator

- Access: `SELECT COALESCE(MAX(seq), 0) + 1 n FROM case_runs`.
- Filters on: nothing. The whole table (observed: line 450).
- Computes: the next `seq`.
- Consumer: the new row, and through it every `ORDER BY seq` window below.
- Shape A: clean. A sentinel raises `MAX(seq)` and no reader reads that number
  directly.
- Shape B: clean, for the same reason.
- Shape C: clean, for the same reason.

### R2. `rota/llm/cassettes.py:473-477` — `flip_history`

- Access: `SELECT prompt_hash, load_id, MIN(seq) first_seq, COUNT(*) n,
  SUM(passed) ok FROM case_runs WHERE case_id = ? GROUP BY prompt_hash,
  load_id ORDER BY first_seq`.
- Filters on: `case_id` only. No exclusion of any kind (observed: line 476).
- Computes: one verdict per `(prompt_hash, load_id)` group, at the bar
  `ok / n >= 0.8`, and a flip against the previous group.
- Consumer: `trust`, then the report's `PROV` state, then `provisional_cases`.
- Shape A: corrupts. A sentinel carries the live `prompt_hash` and the live
  `load_id`, so it joins the group that holds the real runs of the same two
  hours. Five real passes plus five sentinels read `5/10`, which is under the
  bar, so a green group turns red (reasoned: the SQL has no filter and the
  arithmetic is at line 480). Fix: add the sentinel's exclusion to the
  `WHERE` clause.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts, the same way, unless the sentinel sits in `prompt_hash`
  or `load_id`. A sentinel in either of those two columns makes a group of its
  own, which then reads as a red group between green ones and invents two
  flips (reasoned: the grouping key is exactly those two columns). Fix: a
  `WHERE` clause that names the sentinel, in every case.

### R3. `rota/llm/cassettes.py:488` — `trust`

- Access: none of its own. It reads `flip_history`.
- Filters on: nothing more.
- Computes: `earned`, `provisional`, `red` or `unmeasured`, from the last
  group and the trailing green streak (observed: lines 495-510).
- Consumer: `casestatus.status:331`, which turns a green into `PROV`.
- Shape A: corrupts. R2 turns the latest group red, so `trust` returns `red`.
  The call site tests `== "provisional"`, so the `PROV` branch never fires and
  a genuinely provisional green renders as plain green (observed: the equality
  at `rota/tools/casestatus.py:331`). The safety net of the 2026-08-27 ruling
  goes quiet. Fix: the R2 fix repairs this reader.
- Shape B: corrupts, the same way. Fix: the R2 fix.
- Shape C: corrupts, the same way. Fix: the R2 fix.

### R4. `rota/llm/cassettes.py:515-516` — `provisional_cases`

- Access: `SELECT DISTINCT case_id FROM case_runs ORDER BY case_id`, then
  `trust` per case.
- Filters on: nothing.
- Computes: the list of cases whose green may not be banked.
- Consumer: `tests/rota/test_case_trust.py:50` only. No shipping caller today
  (observed: the grep of 2026-09-22 found no other use).
- Shape A: corrupts. The case list grows to hold cases that hold only
  sentinels, and each such case then answers `red` through R3. Fix: the R2 fix,
  plus a decision on whether a sentinel-only case belongs in the list at all.
- Shape B: corrupts, the same way. Fix: the R2 fix.
- Shape C: corrupts, the same way. Fix: the R2 fix.

### R5. `rota/llm/cassettes.py:522-526` — `pass_rate_history`

- Access: `SELECT model, prompt_hash, COUNT(*) runs, SUM(passed) passed,
  MAX(seq) last_seq FROM case_runs WHERE case_id = ? GROUP BY model,
  prompt_hash ORDER BY last_seq DESC`.
- Filters on: `case_id` only.
- Computes: the pass rate per prompt version, newest first.
- Consumer: none in the tree today (observed: the grep of 2026-09-22).
- Shape A: corrupts. `runs` grows and `passed` does not, so the printed rate
  falls. Fix: exclude the sentinel in the `WHERE` clause.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts, the same way. Fix: name the sentinel in the `WHERE`
  clause.

### R6. `rota/llm/cassettes.py:121-140` — `open_dev_db`, the migrator

- Access: `PRAGMA table_info(case_runs)`, then one `ALTER TABLE` per missing
  column.
- Filters on: nothing. It reads the schema, not the rows.
- Computes: whether the committed register carries each column.
- Consumer: every caller that opens through this function.
- Shape A: clean. No schema change.
- Shape B: this is the site that must add `measured`. `KEY_COLUMNS` at
  `rota/llm/cassettes.py:98-104` is the pattern, and an `ALTER TABLE ... ADD
  COLUMN` with a default costs no table rewrite (observed: the note at
  `rota/llm/cassettes.py:133-137`). A default of 1 makes every old row read as
  measured, which is the true statement about it. Fix: none needed beyond
  writing it.
- Shape C: clean. No schema change.

### R7. `rota/tools/casestatus.py:119` — `carries_the_key`

- Access: `PRAGMA table_info(case_runs)`.
- Filters on: nothing.
- Computes: whether the five frame-54 columns exist.
- Consumer: `matching_runs(keyed=...)` and `holds_a_system_hash:144`.
- Shape A: clean.
- Shape B: this predicate does not cover `measured`, so a second predicate is
  needed. The cockpit panel connects with a raw `sqlite3.connect` and never
  migrates (observed: `rota/cockpit/progress.py:261` and the note at lines
  277-279). So a fresh checkout that pulls the published snapshot can read the
  table before any `ALTER TABLE` has run, and a query naming `measured` would
  raise `no such column` (reasoned: the same fault frame 54 met, recorded at
  `rota/tools/casestatus.py:108-116`). Fix: a `has_measured(conn)` predicate
  beside this one, and a fallback to the narrow behaviour.
- Shape C: clean. The column already exists.

### R8. `rota/tools/casestatus.py:146-148` — `holds_a_system_hash`

- Access: `SELECT 1 FROM case_runs WHERE system_hash NOT IN ('', ?) LIMIT 1`,
  with `UNBUILT`.
- Filters on: `system_hash`. Nothing else. The predicate is global and not per
  case (observed: the docstring at lines 138-143).
- Computes: whether the whole report widens its match to the system text.
- Consumer: `status:287` and `progress.l1:229`.
- Shape A: corrupts, quietly. A sentinel row carries a real digest, because
  the miss happens after `build_prompt`. One sentinel in an otherwise legacy
  register turns the widened match on for every case, and every legacy case
  then reads `STALE` (reasoned: the predicate is global, and the row is not
  excluded here). Fix: exclude the sentinel from this predicate too.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts in the other direction when the sentinel sits in
  `system_hash`. A sentinel value that is not in `('', UNBUILT)` satisfies
  this predicate, so a register holding only sentinels widens the match and
  stales every case. Fix: name the new sentinel in the `NOT IN` list, exactly
  as `UNBUILT` is named.

### R9. `rota/tools/casestatus.py:193-217` — `matching_runs`

- Access: `SELECT passed, problems FROM case_runs WHERE case_id = ? AND
  prompt_hash = ? AND model = ?`, then optional clauses, then
  `AND NOT (passed = 0 AND (problems LIKE '%no cassette for%' OR transcript
  LIKE '%no cassette for%')) ORDER BY seq DESC LIMIT ?`.
- Filters on: `case_id`, `prompt_hash`, `model` always. `system_hash` when
  `system` is passed. `num_ctx`, `temperature`, `protocol`, `extras` when
  `keyed` is true. `passed`, `problems` and `transcript` in the exclusion
  clause. `seq` orders the window.
- Computes: the newest `runs` rows that are evidence about this case under
  these pins.
- Consumer: the report's score and state, the cockpit's L1 panel, and through
  `status` the gate's stale line.
- Shape A: clean, with one gap. The exclusion clause is a `WHERE` predicate,
  so it runs before the `LIMIT` window. Five sentinel rows are dropped and the
  window falls back to the five real rows behind them (reasoned: SQLite
  applies `WHERE`, then `ORDER BY`, then `LIMIT`). The dead clause at lines
  213-215 becomes live code. The gap: the clause matches only the literal
  `no cassette for`, and `_is_unmeasured` also fires on `LLMUnavailable`
  (observed: `rota/llm/cassettes.py:379`). A run that could not reach the
  model carries `LLMUnavailable` and not `no cassette for` (observed: the
  message at `rota/llm/llm.py:426` is `ollama at {host}: {exc}`). Such a row
  enters the window, displaces a real row and reads as a red. Fix: widen the
  clause to the same two markers the writer uses, from one shared constant.
- Shape B: corrupts. No clause mentions `measured`, so five sentinels fill the
  window, `sum(passed)` is 0, and the case reads `FAIL`. Fix:
  `AND measured = 1`, guarded by the R7 predicate.
- Shape C: corrupts when the widened match is off. With `system` passed, the
  clause `AND system_hash = ?` rejects a sentinel value, so the reader is
  clean. With `system` empty the whole clause is skipped, so the sentinels
  fill the window and the case reads `FAIL` (observed: the `if system:` guard
  at line 196). `system` is empty whenever `holds_a_system_hash` is false, and
  it is empty on every call from the `narrow` line at 309. Fix: an
  unconditional clause that names the sentinel, independent of `system`.

### R10. `rota/tools/casestatus.py:302-304` — `status`, the `ever` count

- Access: `SELECT COUNT(*) n FROM case_runs WHERE case_id = ?`.
- Filters on: `case_id` only.
- Computes: whether the case was ever measured under any key.
- Consumer: the `STALE` against `NEW` split at line 312, and the report's
  `ever` field.
- Shape A: changes the answer, and that change is what frame 64 asks for. A
  case whose only rows are sentinels moves from `NEW` to `STALE`. Both states
  enter the gate's stale set, so the gate's count does not move (observed:
  `rota/tools/gate.py:130-131`). The report's two counters each move by one
  (observed: `rota/tools/casestatus.py:354-356`). Call it corruption only if
  `NEW` must keep meaning "nobody has looked". Fix, if wanted: count only
  measured rows here.
- Shape B: the same. Fix: `AND measured = 1`, if `NEW` must keep its meaning.
- Shape C: the same. Fix: a clause naming the sentinel.

### R11. `rota/tools/casestatus.py:309` — `status`, the `narrow` count

- Access: a second `matching_runs` call, with no `system`.
- Filters on: the same columns as R9, minus `system_hash`.
- Computes: the denominator the narrow match would have counted.
- Consumer: the shrink test at line 314, which turns a shrunk denominator into
  `STALE` rather than `FAIL`.
- Shape A: clean. The exclusion clause applies to both calls, so `here` and
  `narrow` shrink together.
- Shape B: corrupts. `narrow` grows by the sentinel count while `here` grows
  too, so the shrink test misreads. Fix: the R9 fix covers both calls.
- Shape C: corrupts. `narrow` never passes `system`, so it always counts the
  sentinels while `here` does not. `len(here) < threshold <= len(narrow)` then
  reads `STALE` for a case that is merely unmeasured under the current text
  (reasoned: the sentinels inflate only one side). Fix: the unconditional
  clause named in R9.

### R12. `rota/tools/casestatus.py:325-333` — `status`, the state and the score

- Access: none of its own. It reads the rows R9 returned.
- Filters on: nothing more.
- Computes: `passed = sum(r["passed"] for r in here)`, then `green` against
  `FAIL` against `PROV`.
- Consumer: the report's score column, the count line, and the gate.
- Shape A: clean when R9 is clean. Corrupts through the `LLMUnavailable` gap
  named in R9.
- Shape B: corrupts through R9.
- Shape C: corrupts through R9 when the widened match is off.
- All three shapes: `sum` over a `NULL` `passed` raises `TypeError` and takes
  the report down. See section 5, fact 6.

### R13. `rota/tools/casestatus.py:340` — `status`, the `why` line

- Access: none of its own. It parses `problems` from the rows R9 returned.
- Filters on: `state == "FAIL"`.
- Computes: the first problem string, cut to 96 characters at line 389.
- Consumer: the second line under a failing case in the report.
- Shape A: corrupts only when R9 already corrupts. The line then reads
  `session did not commit: [...LLMUnavailable...]`, which names the
  infrastructure and not the role. Fix: the R9 fix.
- Shape B: the same. Fix: the R9 fix.
- Shape C: the same. Fix: the R9 fix.

### R14. `rota/tools/gate.py:115-132` — `_stale`

- Access: none of its own. It calls `casestatus.status(model)`.
- Filters on: `row["state"] in ("STALE", "NEW")`.
- Computes: the set of case ids with no recording against the current key.
- Consumer: the gate's fourth line and the baseline JSON at `gate.py:288`. The
  baseline makes the `+n -n` delta at lines 324-326.
- Shape A: clean when R9 is clean. Under the `LLMUnavailable` gap a case
  leaves the stale set and enters the red count, which is the wrong half of
  the one distinction the gate exists to draw.
- Shape B: corrupts through R9. A case that should read stale reads `FAIL`,
  so the stale line loses it and the reader sees a regression.
- Shape C: corrupts through R9 when the widened match is off.
- All three shapes: a case that moves from `NEW` to `STALE` stays inside this
  set, so the gate's number does not move (observed: line 131).

### R15. `rota/cockpit/progress.py:244-250` — `l1`, the panel

- Access: `casestatus.matching_runs(...)` with `limit=runs`, then
  `SELECT COUNT(*) n FROM case_runs WHERE case_id = ?`.
- Filters on: everything R9 filters on, plus `case_id` for the count.
- Computes: `passed`, `problems` and one of `pass`, `fail`, `stale`,
  `never run`.
- Consumer: the cockpit's L1 panel and its tally.
- Shape A: clean when R9 is clean, and corrupt through the same gap. The panel
  is the one a person reads, so the gap costs more here (observed: the note at
  `rota/cockpit/progress.py:268-275`).
- Shape B: corrupts through R9, and can raise. The connection is a raw
  `sqlite3.connect` that never migrates, so a query naming `measured` can meet
  `no such column` (observed: `rota/cockpit/progress.py:261`). The
  `except sqlite3.Error` at line 251 turns that into an empty batch, so every
  case reads `stale` or `never run` silently. Fix: the R7 predicate.
- Shape C: corrupts through R9. This panel passes `system` only for a
  single-session case, and a chain keeps the narrow match (observed: lines
  246-248 and the note at lines 284-286). So every chain in the panel takes
  the sentinels into its window.

### R16. `rota/cockpit/progress.py:702-712` — `_runs`

- Access: `SELECT case_id, model, prompt_hash, run_no, passed, problems,
  transcript, seq FROM case_runs ORDER BY seq`, grouped into a dict by
  `case_id`.
- Filters on: nothing.
- Computes: every row of every case, oldest first.
- Consumer: the case detail panel at `rota/cockpit/progress.py:552-554`, which
  renders the last five rows with their transcripts.
- Shape A: corrupts. The last five rows become the five sentinels, so the
  panel shows five empty transcripts and hides the last real pass. Fix: a
  filter in the SQL, or a filter on the slice.
- Shape B: corrupts, the same way. Fix: the same.
- Shape C: corrupts, the same way. Fix: the same.

### R17. `rota/llm/benchmarks.py:35-56` — `from_register`

- Access: `SELECT case_id, model, prompt_hash, seq, passed FROM case_runs
  WHERE case_id NOT LIKE 'T0-PROVIDER-%'`.
- Filters on: `case_id` by prefix, then `prompt_hash` against the latest
  `prompt_hash` per `(case_id, model)`, chosen by `MAX(seq)`.
- Computes: per case, `ok` over `n`, against `threshold = max(3, int(n * 0.6))`
  when `n >= 3`. Then per `(model, role)`, the share of cases that reach the
  threshold.
- Consumer: `benchmarks.json`, which `recommend` reads to rank a model for a
  capability (observed: the module docstring at lines 1-16).
- Shape A: corrupts twice. A sentinel carries the latest `prompt_hash`, so it
  enters `per_case`. It raises `n` and leaves `ok` alone, and it raises the
  threshold with `n`. Five passes plus five sentinels give `ok = 5`, `n = 10`
  and a threshold of 6, so a green case scores as a failure and the model's
  capability score falls (reasoned: the arithmetic at lines 41-52). Fix:
  exclude the sentinel in the `WHERE` clause.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts, the same way, unless the sentinel sits in `prompt_hash`.
  A sentinel `prompt_hash` would become the latest hash for the case and drop
  every real row from the tally, which is worse. Fix: an explicit exclusion,
  in every case.

### R18. `rota/llm/benchmarks.py:62-71` — `from_tool_check`

- Access: `SELECT case_id, model, passed FROM case_runs WHERE case_id LIKE
  'T0-PROVIDER-%' ORDER BY seq`.
- Filters on: `case_id` by prefix. `seq` orders it. The last row per
  `(model, kind)` wins.
- Computes: a score of 1.0 or 0.0 per `transport:tool-line` and
  `transport:native-call`.
- Consumer: `benchmarks.json`, and the screen that says a transport works.
- Shape A: corrupts. The newest row wins outright, so one sentinel says the
  transport is broken. The tool check already writes such a row when the model
  is unreachable, because `toolcheck` formats the error with `str()`
  (observed: `rota/llm/toolcheck.py:83`), so this reader is wrong today for
  the native leg. Fix: exclude the sentinel, and give `toolcheck` the same
  marker the runner writes.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts, the same way. Fix: an exclusion naming the sentinel.

### R19. `rota/tools/triage.py:103-104` — `last_runs`

- Access: `SELECT case_id, run_no, passed, problems, transcript, seq, model,
  prompt_hash FROM case_runs ORDER BY seq DESC`.
- Filters on: `seq` for the order, `case_id` against the live case ids and an
  optional prefix, then `run_no` to keep one row per run number per case.
- Computes: the most recent pass of every case.
- Consumer: the triage report: the score per case, the mechanism counts, the
  `blind` count, and the model name on the header line at `triage.py:196`.
- Shape A: corrupts badly. This is a newest-first dedupe on `run_no`, so five
  sentinels with run numbers 1 to 5 displace the whole last real pass. Every
  case then prints `0/5`, and the mechanism column fills with the session
  failure rather than the role's mistake (reasoned: the dedupe at lines
  109-114 and the tally at lines 167-183). Fix: exclude the sentinel in the
  `WHERE` clause.
- Shape B: corrupts, the same way. Fix: `AND measured = 1`.
- Shape C: corrupts, the same way. Fix: an exclusion naming the sentinel.

### R20. `rota/tools/migrate_register.py:177-180` — `check_source`

- Access: `PRAGMA table_info(case_runs)`, then
  `SELECT COUNT(*) n FROM case_runs`.
- Filters on: nothing.
- Computes: the column count and the row count of the clone.
- Consumer: a refusal when the caller's named shape is missed (observed: lines
  185-189).
- Shape A: clean in behaviour. The expected row count a caller types moves,
  which is a note in the runbook and not a defect.
- Shape B: the column count moves by one, which trips the same check. Fix:
  update the number the caller passes.
- Shape C: clean in behaviour, with the same row-count note.

### R21. `rota/tools/migrate_register.py:228` — `check_target`

- Access: `SELECT COUNT(*) FROM case_runs`.
- Filters on: nothing.
- Computes: whether the target already holds results.
- Consumer: a refusal without `--force`.
- Shape A: clean. A sentinel is still a result for the purpose of refusing.
- Shape B: clean.
- Shape C: clean.

### R22. `rota/tools/migrate_register.py:274-305` — `migrate`

- Access: `SELECT case_id, model, prompt_hash, run_no, load_id, passed,
  problems, transcript, seq FROM case_runs`, then a fourteen-column
  `INSERT OR REPLACE`.
- Filters on: `case_id` against the chain set and the tree set, then the
  transcript, through `resolve`.
- Computes: the five key values per row, from the cassette that produced the
  row's replies.
- Consumer: the new register, and the migration report at lines 315-340.
- Shape A: clean, and it drops the row. A sentinel transcript holds no `say`
  item, so `resolve` returns `the row holds no model reply` and the row is
  left behind (observed: `rota/tools/migrate_register.py:147-148`). The
  left-behind tally grows, and the reason line is wrong about why.
- Shape B: clean for the rows, and lossy for the column. The insert names
  fourteen columns and none of them is `measured`, so a migrated sentinel
  would land as measured (reasoned: the column list at lines 274-277). The
  row is dropped first, so the loss is theoretical today. Fix: name the column
  in both the select and the insert.
- Shape C: clean for the rows, and lossy for the value when the sentinel sits
  in `system_hash`. The migration overwrites `system_hash` from the cassette
  (observed: the `*shape` at line 305 and `shape_of` at lines 100-105). Fix:
  pass a sentinel row through unchanged.

### R23. `rota/testkit/cassette_store.py:101-106` — `_counts`

- Access: `select count(*) from case_runs`, on a read-only connection.
- Filters on: nothing.
- Computes: the row count of a snapshot or of the live register.
- Consumer: the manifest's `case_runs` field at line 164, the `pack` print at
  `rota/cli.py:556`, and the status lines at lines 311 and 318.
- Shape A: changes the number, and the number is a comparison key. See R24.
- Shape B: the same.
- Shape C: the same.

### R24. `rota/testkit/cassette_store.py:326-332` — `status`, the comparison

- Access: none of its own. It compares `_counts` against the manifest.
- Filters on: nothing. The tuple `(cassettes, runs)` decides.
- Computes: one of three sentences: same rows, more rows, or fewer rows.
- Consumer: the operator, who is told to publish or to pull.
- Shape A: corrupts, mildly. A register that recorded nothing new but met one
  cassette miss reads `more rows than the published one` and invites a publish
  of no new evidence (reasoned: the branch at line 330 tests `runs >=`). Fix:
  count only measured rows, or accept the noise and say so in the docstring.
- Shape B: corrupts, the same way. Fix: the same.
- Shape C: corrupts, the same way. Fix: the same.

### R25. `rota/cli.py:556` — `cmd_cassettes`, the pack line

- Access: none. It prints `m.case_runs` from the manifest.
- Filters on: nothing.
- Computes: nothing.
- Consumer: the operator's terminal after `rota cassettes pack`.
- Shape A: clean. It repeats R23's number.
- Shape B: clean.
- Shape C: clean.

---

### `matching_runs` under a window of five sentinels

The question asked for this case directly. A case has five real rows, then
five sentinel rows. Its threshold is 3 and its window is 5.

- **Shape A, with the literal `no cassette for` text.** The exclusion clause
  at `rota/tools/casestatus.py:213-215` is a `WHERE` predicate, so the five
  sentinels never reach the `ORDER BY seq DESC LIMIT 5` window. `here` holds
  the five real rows. `narrow` holds the same five. The branch at line 311 is
  not taken, the branch at line 314 is not taken, and line 325 sums the real
  rows. The case reads exactly as it read before: `green`, or `PROV`, or
  `FAIL` on its real evidence (reasoned: the clause runs before the limit).
  The case does **not** read `STALE`, so shape A alone does not give the
  report the new sentence frame 64 wants.
- **Shape A, from an unreachable model.** The row carries `LLMUnavailable` and
  not `no cassette for`, so the clause misses it. The five sentinels fill the
  window. `here` has five rows, `narrow` has five rows, so the branch at line
  314 is not taken. Line 325 gives `passed = 0`, and line 326 gives `FAIL`.
  The case reads a hard red, which is the exact failure the writer's guard
  was built to stop (observed: the guard's reasoning at
  `rota/llm/cassettes.py:376-379`).
- **Shape B, with no new clause.** The five sentinels fill the window.
  `here` and `narrow` both hold five, so the shrink branch is not taken.
  `passed = 0` and the case reads `FAIL`.
- **Shape B, with `AND measured = 1` in `matching_runs`.** The sentinels are
  dropped before the window, so the case behaves as in the first bullet:
  green on its real rows, and never `STALE`.
- **Shape C, widened match on.** `AND system_hash = ?` rejects the sentinel
  value, so the sentinels never reach the window. The case reads green on its
  real rows.
- **Shape C, widened match off.** The `if system:` guard at line 196 skips the
  whole clause. The sentinels fill the window and the case reads `FAIL`. The
  widened match is off for a legacy register, for a register with no real
  hash, and on every `narrow` call at line 309.
- **All shapes, when the sentinels are the case's only rows.** `here` is
  empty, so line 312 runs. `ever` counts the sentinels, so the state is
  `STALE` and not `NEW`. This is the one branch where a sentinel changes the
  report by itself, and it is the change frame 64 asks for.

The conclusion the design must face: excluding a sentinel from `matching_runs`
keeps the report correct and gives the report nothing new. The new sentence
frame 64 wants lives in `ever`, at `rota/tools/casestatus.py:302-304`, and in
a new field beside it. It does not live in the window (reasoned: the window
decides `green` against `FAIL`, and a sentinel has no verdict to add).

---

## 3. What corrupts under each shape

Shape A is a `passed = 0` row with `no cassette for` in `problems`. Shape B is
a `measured` column set to 0. Shape C is a sentinel value in `system_hash`,
the way `UNBUILT` is used. Each cell assumes the shape is added with no other
change to the reader.

| # | Reader | Shape A | Shape B | Shape C |
|---|--------|---------|---------|---------|
| R1 | `cassettes.py:449` seq allocator | clean | clean | clean |
| R2 | `cassettes.py:473` `flip_history` | corrupts: the sentinel joins the live `(prompt_hash, load_id)` group and drops `ok/n` under the 0.8 bar | corrupts: same, no `measured` filter | corrupts: same, no filter on the sentinel |
| R3 | `cassettes.py:488` `trust` | corrupts: returns `red`, so the `PROV` net at `casestatus.py:331` never fires | corrupts: same | corrupts: same |
| R4 | `cassettes.py:515` `provisional_cases` | corrupts: sentinel-only cases enter the list and answer `red` | corrupts: same | corrupts: same |
| R5 | `cassettes.py:522` `pass_rate_history` | corrupts: `runs` grows, `passed` does not, the rate falls | corrupts: same | corrupts: same |
| R6 | `cassettes.py:121` `open_dev_db` | n/a | must add the column here, with a default of 1 | n/a |
| R7 | `casestatus.py:119` `carries_the_key` | clean | corrupts: it does not cover `measured`, so a raw reader can meet `no such column` | clean |
| R8 | `casestatus.py:146` `holds_a_system_hash` | corrupts: the sentinel carries a real digest and widens the match for the whole register | corrupts: same | corrupts: a sentinel value outside `('', UNBUILT)` widens the match by itself |
| R9 | `casestatus.py:193` `matching_runs` | clean for `no cassette for`; corrupts for `LLMUnavailable`: the row enters the window and reads `FAIL` | corrupts: the row enters the window and reads `FAIL` | clean while `system` is passed; corrupts when it is not, and the row reads `FAIL` |
| R10 | `casestatus.py:302` `ever` | corrupts: `NEW` becomes `STALE`, which is the wanted change and a changed meaning | corrupts: same | corrupts: same |
| R11 | `casestatus.py:309` `narrow` | clean: both calls shrink together | corrupts: the shrink test misreads | corrupts: `narrow` never passes `system`, so only one side grows |
| R12 | `casestatus.py:325` state and score | clean when R9 is clean | corrupts through R9 | corrupts through R9 |
| R13 | `casestatus.py:340` the `why` line | corrupts through R9: names the infrastructure, not the role | corrupts through R9 | corrupts through R9 |
| R14 | `gate.py:115` `_stale` | corrupts through R9: a stale case leaves the stale set and enters the red count | corrupts through R9 | corrupts through R9 |
| R15 | `progress.py:244` `l1` panel | corrupts through R9 | corrupts through R9, and can raise `no such column` on its raw connection | corrupts through R9, and every chain keeps the narrow match |
| R16 | `progress.py:702` `_runs` | corrupts: the last five rows are sentinels, so the detail panel hides the real transcripts | corrupts: same | corrupts: same |
| R17 | `benchmarks.py:35` `from_register` | corrupts: `n` grows, `ok` does not, and the threshold grows with `n`, so a green case scores as a failure | corrupts: same | corrupts: same, and a sentinel in `prompt_hash` would drop every real row |
| R18 | `benchmarks.py:62` `from_tool_check` | corrupts: the newest row wins outright, so one sentinel says the transport is broken | corrupts: same | corrupts: same |
| R19 | `triage.py:103` `last_runs` | corrupts: five sentinels displace the whole last real pass, so every case prints `0/5` | corrupts: same | corrupts: same |
| R20 | `migrate_register.py:177` `check_source` | clean: the expected row count moves | corrupts: the expected column count moves | clean: the expected row count moves |
| R21 | `migrate_register.py:228` `check_target` | clean | clean | clean |
| R22 | `migrate_register.py:274` `migrate` | clean: `resolve` drops the row for want of a reply | clean for rows, lossy for the column: the insert names fourteen columns | clean for rows, lossy for the value: `system_hash` is overwritten from the cassette |
| R23 | `cassette_store.py:101` `_counts` | corrupts: the manifest count grows with no new evidence | corrupts: same | corrupts: same |
| R24 | `cassette_store.py:326` status compare | corrupts: reads `more rows than the published one` and invites a publish | corrupts: same | corrupts: same |
| R25 | `cli.py:556` pack line | clean | clean | clean |

Counts: shape A corrupts 15 readers of 25, shape B corrupts 18, shape C
corrupts 17. The counts are close and they are not the decision. The
difference between the shapes is where the exclusion lives: shape A hides it
in two text patterns, shape B puts it in a column every query must name, and
shape C reuses a sentinel convention the codebase already has.

---

## 4. Tests that pin the current behaviour

No test calls `_is_unmeasured` (observed: the grep of `tests/` on 2026-09-22
found the name only in `rota/llm/cassettes.py`). No test asserts that
`record_case_run` returns early and writes nothing. The behaviour is pinned
indirectly, by tests that count rows and by tiers that never produce one.

| File and line | What it asserts |
|---|---|
| `tests/rota/test_l1.py:152` | The tier records every result through `record_case_run`, with the whole system text. A dropped row is silent here. |
| `tests/rota/test_l1.py:174-180` | A run whose problems hold `no cassette for` fails the test with a `STALE` message, so the tier never lets an unmeasured run pass as a verdict. |
| `tests/rota/test_l3.py:118` and `:122` | The same two assertions for the chain tier. |
| `tests/rota/test_gauntlet.py:98` and `:101` | The same two assertions for the gauntlet tier. |
| `tests/rota/test_register_key.py:176` | After the migration of one row, `SELECT COUNT(*) n FROM case_runs` is 1. An extra sentinel row would break the count. |
| `tests/rota/test_register_key.py:177` | That one row reads `passed = 1`. |
| `tests/rota/test_register_key.py:532` | `_landed` reads every row of the migrated register, ordered by `seq`. Several tests below it index the list by position. |
| `tests/rota/test_register_key.py:793-800` | The tool check writes exactly two rows, one per protocol: `set(rows) == {"text", "native"}`. A sentinel row from an unreachable model would add a third. |
| `tests/rota/test_register_key.py:1100-1108` | A mixed register stales the case that carries only a legacy row. Two rows, one case each. |
| `tests/rota/test_register_key.py:1133-1142` | Three legacy rows and two current rows read `STALE`, and carry no score. This is the shrink branch at `casestatus.py:314`. |
| `tests/rota/test_register_key.py:1162-1179` | A chain whose replay raises `RuntimeError("no cassette for the first leg")` reads `STALE`, and the report names the reason. The text `no cassette for` travels in the report's `why`, not in a row. |
| `tests/rota/test_register_key.py:1189-1200` | `_cases_with_a_row` collects cases by `matching_runs(..., limit=1)` against the real register. Sentinel rows would enlarge the parameter list. |
| `tests/rota/test_case_trust.py:33-37` | The helper inserts rows straight into `case_runs`, with nine columns and no key fields. Every trust test below builds on it. |
| `tests/rota/test_case_trust.py:39-80` | Six tests fix the bar at 4 of 5 and the flip rule. Each is an exact ratio, so an extra `passed = 0` row in a group changes the verdict. |
| `tests/rota/test_case_trust.py:95-98` | `record_case_run(db, "c", pins, 1, True, [])` writes one row with a live `load_id`. It passes, so the guard does not fire. |
| `tests/rota/test_discover.py:62-76` | Builds `case_runs` by hand with nine columns and asserts the benchmark scores to three decimals. The table here has no `measured` column, so shape B must not make the column mandatory for a reader. |
| `tests/rota/test_gate.py:250` | `stored["stale"] is None` when no register is present: an unmeasured set is null and never empty. |

The gap this leaves: nothing in the suite fails if the guard is removed
tomorrow. The three tier tests would turn red, because they call
`pytest.fail` on a missing cassette before any reader sees the row. That is a
different mechanism from the guard, and it only runs when a tier runs.

---

## 5. Facts the design must answer

No shape is recommended here. These are the conditions each shape must meet.

1. **A sentinel row carries a live key.** It has the current `prompt_hash`,
   the current `load_id`, the current pins and a real `system_hash`, because
   the model call comes after `build_prompt` (reasoned:
   `rota/core/runner.py:2996` and `rota/testkit/fixtures.py:669`). So no
   existing key filter rejects it. Every exclusion must be written on purpose.

2. **The exclusion must live in one place.** There are two markers today,
   `no cassette for` and `LLMUnavailable`, and they are written in the writer
   at `rota/llm/cassettes.py:379` and re-written by hand, half of them, in
   `rota/tools/casestatus.py:213-215`. Frame 60 and frame 54 both record what
   a second copy of a match costs (observed: `rota/tools/casestatus.py:154-160`).
   A shape must name the sentinel once, in a constant or a column, and every
   reader must read that one name.

3. **Twelve readers apply no filter at all.** R2, R4, R5, R10, R16, R17, R19,
   R21, R23 and the three schema readers select on `case_id` or on nothing.
   A shape that hides the sentinel behind a text pattern reaches none of them
   without twelve separate edits. A shape that hides it behind a column
   reaches none of them either. There is no shape where the readers stay
   unedited.

4. **`matching_runs` must exclude the sentinel before the `LIMIT`.** The
   window is `ORDER BY seq DESC LIMIT runs` at
   `rota/tools/casestatus.py:215`. A sentinel inside the window displaces a
   real row and turns `passed` into 0, which reads `FAIL`. A `WHERE`
   predicate runs first, so the exclusion must be a `WHERE` predicate and
   never a filter in Python after the query.

5. **The exclusion must not depend on `system`.** `matching_runs` skips its
   whole `system_hash` clause when `system` is empty (observed:
   `rota/tools/casestatus.py:196`), and `status` calls it with no `system` on
   the `narrow` line at 309. So a shape that hides the sentinel in
   `system_hash` is unguarded on every narrow call, on every legacy register,
   and on every chain in the cockpit panel.

6. **No shape needs `passed` to be NULL, and NULL costs four things.**
   `passed` is `INTEGER NOT NULL` (observed: `rota/llm/cassettes.py:64`).
   First, SQLite cannot drop `NOT NULL` with `ALTER TABLE`, so the table must
   be rebuilt: create, insert-select, drop, rename, over 136455 rows
   (observed: the row count at `tests/rota/cassettes.json:11`). Second,
   `sum(r["passed"] for r in here)` raises `TypeError` on None at
   `rota/tools/casestatus.py:325` and at `rota/cockpit/progress.py:257`.
   Third, `c["passed"] += r["passed"]` raises the same at
   `rota/tools/triage.py:171`, and `int(passed)` raises at
   `rota/llm/benchmarks.py:45`. Fourth, `SUM(passed)` skips NULLs while
   `COUNT(*)` counts them, so `flip_history` would divide a NULL-free
   numerator by a NULL-bearing denominator and silently drop every verdict
   under the bar (reasoned: the arithmetic at `rota/llm/cassettes.py:480`).
   A shape that wants "no verdict" must say so in another column, or in a
   value of `passed` that is neither 0 nor 1.

7. **A new column needs its own existence predicate.** `open_dev_db` migrates
   and the cockpit panel does not: it connects with a raw `sqlite3.connect`
   at `rota/cockpit/progress.py:261`. `tests/rota/cassettes.db` is gitignored
   and pulled from a published snapshot that carries no schema version
   (observed: `rota/tools/casestatus.py:131-134`). So a query naming a new
   column can meet `no such column` on a real machine, and
   `carries_the_key` does not cover it. The shape must ship a predicate beside
   `carries_the_key` and a narrow fallback behind it.

8. **The `NEW` against `STALE` split is the only place a sentinel changes the
   report by itself.** `ever` counts every row of the case (observed:
   `rota/tools/casestatus.py:302-304`), and a case whose only rows are
   sentinels moves from `NEW` to `STALE`. The gate's set holds both states, so
   the gate's number does not move (observed: `rota/tools/gate.py:130-131`).
   The design must decide whether `NEW` keeps meaning "nobody has looked". If
   it does, `ever` needs a measured-only filter and the new sentence needs a
   field of its own.

9. **The new sentence frame 64 wants is not a state in the window.** The
   window decides `green` against `FAIL`, and a sentinel carries no verdict.
   "Somebody looked and the key missed" is a second count beside `ever`, and
   the report has to render it on the case's line and in the count line at
   `rota/tools/casestatus.py:354-356`.

10. **`holds_a_system_hash` is global, and a sentinel can flip it.** One row
    with a real digest turns the widened match on for every case (observed:
    the docstring at `rota/tools/casestatus.py:138-143`). A sentinel row
    carries a real digest under shapes A and B, so a register of sentinels
    would stale every case. Under shape C the sentinel value itself satisfies
    the `NOT IN ('', UNBUILT)` test. Every shape must add the sentinel to this
    predicate's exclusion.

11. **`trust` inverts under a sentinel, and the failure is silent.** A
    sentinel drags the latest group under the 0.8 bar, `trust` answers `red`,
    and the call site tests only `== "provisional"` (observed:
    `rota/tools/casestatus.py:331`). So the 2026-08-27 ruling stops being
    enforced while the report still prints green. The shape must exclude the
    sentinel from `flip_history`, or the ruling loses its instrument.

12. **`benchmarks.from_register` raises its own threshold with `n`.** The
    threshold is `max(3, int(n * 0.6))` when `n >= 3` (observed:
    `rota/llm/benchmarks.py:51`). Sentinels raise `n` and not `ok`, so they
    move the bar and the score at once. The output is shipped as
    `benchmarks.json` and drives `recommend`, so an unexcluded sentinel
    changes which model a user is told to run.

13. **`from_tool_check` takes the newest row outright.** One sentinel says the
    transport is broken (observed: `rota/llm/benchmarks.py:66-68`). This
    reader is already wrong today, because `toolcheck` formats its error with
    `str()` and loses the `LLMUnavailable` marker the guard looks for
    (observed: `rota/llm/toolcheck.py:83` against
    `rota/llm/cassettes.py:379`). Any shape must fix that writer as well, or
    the sentinel arrives through a path the shape does not control.

14. **`triage.last_runs` dedupes on `run_no` and never on the verdict.** Five
    sentinels numbered 1 to 5 displace the entire last real pass (observed:
    `rota/tools/triage.py:109-114`). The tool exists to name the mechanism of
    a failure, so it must not be handed a table of infrastructure errors.

15. **The migration drops a sentinel and misreports why.** `resolve` returns
    `the row holds no model reply` for a transcript with no `say` item
    (observed: `rota/tools/migrate_register.py:147-148`). A sentinel would be
    counted under that reason in the tally at
    `rota/tools/migrate_register.py:288`. If a sentinel must survive a future
    migration, the tool needs its own branch, and under shape B it needs the
    column in both the select at line 281 and the insert at line 274.

16. **The row count is a comparison key.** `cassette_store.status` compares
    `(cassettes, runs)` against the published manifest and tells the operator
    to publish or to pull (observed:
    `rota/testkit/cassette_store.py:326-332`). Sentinels raise `runs` with no
    new evidence, so the tool says there is something to publish. The design
    must decide whether the manifest counts measured rows or all rows.

17. **The cockpit's detail panel renders the last five rows raw.**
    `_runs` has no filter and the panel slices `[-5:]` (observed:
    `rota/cockpit/progress.py:702-712` and `:552-554`). A sentinel there shows
    a person five empty transcripts. The panel should either skip the
    sentinel or render it as what it is.

18. **Nothing in the suite pins the guard.** No test names `_is_unmeasured`,
    and no test asserts that an unmeasured run writes no row (observed: the
    grep of `tests/` on 2026-09-22). So the change carries no regression net
    of its own, and the frame must write the tests that pin the new behaviour
    before it changes the writer.

---

## 6. Token usage and the files read

Token usage, as the harness reports it at the end of this turn, is written in
the frame's status line. The cap for this report was 120k and the report
stopped well inside it.

Files read, in full:

- `D:/repos/rota/rota/llm/cassettes.py`
- `D:/repos/rota/rota/tools/casestatus.py`

Files read in part, by line range:

- `D:/repos/rota/rota/llm/benchmarks.py` (1-140)
- `D:/repos/rota/rota/llm/llm.py` (412-430, 530-540, 556-570)
- `D:/repos/rota/rota/llm/toolcheck.py` (55-100)
- `D:/repos/rota/rota/core/runner.py` (2990-3015)
- `D:/repos/rota/rota/cockpit/progress.py` (195-310, 530-620, 670-790)
- `D:/repos/rota/rota/testkit/cassette_store.py` (55-180, 255-380)
- `D:/repos/rota/rota/testkit/fixtures.py` (grep of `problems`, 669-684)
- `D:/repos/rota/rota/tools/gate.py` (95-145, 270-365)
- `D:/repos/rota/rota/tools/migrate_register.py` (100-340)
- `D:/repos/rota/rota/tools/triage.py` (1-260)
- `D:/repos/rota/rota/cli.py` (540-640)
- `D:/repos/rota/tests/rota/test_case_trust.py` (1-140)
- `D:/repos/rota/tests/rota/test_discover.py` (40-110)
- `D:/repos/rota/tests/rota/test_l1.py` (140-180)
- `D:/repos/rota/tests/rota/test_register_key.py` (40-110, 495-545, 775-800,
  1040-1200)
- `D:/repos/rota/tests/rota/test_step_failure.py` (30-60)

No test was run. No database was opened. No file under `rota/` or `tests/`
was edited.
