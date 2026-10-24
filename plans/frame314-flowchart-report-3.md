# Frame 314 probe 3 report: the loop joins and the folded fan-out

Verdict: `path.mmd` now holds the running batch, the Tester lane, the harness and the test-run loop, and every arrow is derived. The path does not yet read as one ordered line through the tests. The harness fires on `batches status = running`, not on the Tester's work, and `review` also fires on `running`, not on a passing test run. Both charts are the same bytes on two runs.

## (b) Evaluation

**Does `path.mmd` read from asked to merged through the tests?** The nodes are there, and the order between the tests and the review is not.

What now reads, in order:

1. `items approval = draft` wakes `signoff`. `approved` wakes `slicing`. The Vision Keeper ends in `tickets (new row)`, which wakes `criteria`.
2. `approved` wakes `grouping`. The Architect ends in `batches status = pending`.
3. `pending` wakes `batch_start`. The loop's dispatch of `tick:batch_start` calls `lifecycle.start`, so `batch_start` ends in `batches status = running` (literal). This is the arrow probe 2 did not have.
4. `running` wakes `tests_missing` (Tester), `harness`, `review` (Critic) and seven more ticks.
5. `harness` ends in the box `test_runs.result` (one folded bound arrow). `result = fail` wakes `tests_failing` and the three `exhausted` ticks. `result = error` wakes `tests_failing`. The test-run loop is on the path.
6. `verdicts result = fail` wakes `verdict_failed`. `verdicts result = pass` wakes `merge`, which ends in `batches status = merged`.

What does not read in order:

- `running` wakes the Tester, the harness and the Critic at the same time. The chart cannot show that the harness waits for tests and a commit, and that `review` waits for green tests. Those conditions are in the SQL as joins on `tests` and `test_runs`, and the tool reads only state literals from SQL.
- `test_runs result = pass` is "final". Nothing fires on it by a literal, so the green run does not point at `review`.
- The Tester stages `tests` rows, and `tests` has no state column. No tick waits on `tests (new row)` by the tool's rules, so the Tester's write is not drawn, and the Tester lane points only at ledger and message states.
- The message boxes still connect every seat. The path holds 10 lanes, 19 message and idle boxes, and 196 arrows.
- A seat's lane still ends in every state its tools can write. Only `batch_start` has a tick-level end, from the loop.

**Arrows, derived and not derived, after `loop.py`.** Counts are for `flowchart.mmd`.

- Tick nodes: 54. Derived: 50 (probe 2: 47). Not derived: 4 (probe 2: 7).
- The three closed by the loop: `cancel` (`lifecycle.abandon`), `preempt` (`lifecycle.defer`, also `park`), `harness` (`harness.run`, which calls `lifecycle.record_test_run`). The loop also gives `batch_start` its tick-level end, `lifecycle.start`.
- Still not derived: `constraint_zero` (the loop calls `boot.refresh_constraint_zero`, and its SQL writes no state literal), `checkpoint_invalid`, `message_tips` and `survey` (no seat).
- Trigger arrows: 106, as in probe 2.
- End arrows: 101 (probe 2: 201). Literal: 42. Default: 9. New row: 10. Folded bound: 40. Dashed to "not derived": 4.
- `test_runs result = error` is now drawn as the state the harness leaves behind, not as its trigger. The rule is derived: the drain is one of the action's own end states.

**Arrows folded.** Probe 2 drew 144 bound arrows, one per CHECK value. Probe 3 draws 40, one per (source, table, column), labelled "table.col = <bound>" and pointed at the column's box. Each table box now holds one box per state column.

**Where the chart is still unreadable or misleading.**

- Classification columns (`ledger.kind`, `refs.src_table`, `items.kind`) are still drawn as states, by rule 3.
- `items approval = pending` is still "final". The principal's gate holds it, and the principal is not a tick.
- The Vision Keeper still points at the `items.approval` box (bound), which includes `approved`, a value the code refuses from that seat.
- Ten ticks wake on `running`. The node is a hub.

## (a) The charts

- `D:/repos/rota/probes/flowchart/flowchart.mmd`: 538 lines.
- `D:/repos/rota/probes/flowchart/path.mmd`: 366 lines.

## (c) What the sources did not give

1. The order inside a running batch. The ticks that wake on `running` differ by joins on `tests`, `test_runs` and `head_commit`, not by a state literal. This is the worst remaining gap.
2. The tick of each tool. Only the loop's dispatch of `batch_start` gives a tick-level end. All other seat ends are per seat.
3. The allowed value of a bound parameter.
4. The difference between a lifecycle state and a classification column.
5. The seats of `checkpoint_invalid`, `message_tips` and `survey`.
6. The state `constraint_zero` writes. `boot.refresh_constraint_zero` writes no state literal that the tool can read.

Sources read: `graph.json`, `predicates.py`, `scheduler.py`, `lifecycle.py`, `api.py`, `schema.sql`, `loop.py`. The tool also reads `rota/core/harness.py` and `rota/onboarding/boot.py`, because `loop.py` imports them inside the dispatch block, and the tool follows that import by code. No night was read, and no chart was compared with a night or a scene.

## (d) Guesses in code, as rules

No hand table remains. Four guesses remain, each one a rule:

- GUESS 1, `body_states`: a tick with no drains fires on the state literals of its SQL. Other literals are filters. `NOT EXISTS` and `NOT IN` are cut.
- GUESS 2, `written_states` and `ctx_writes`: a bound value is any value the CHECK allows. Probe 3 draws it folded, as one arrow to the column's box.
- GUESS 3, `build`: a `DERIVED` tick gets one node per seat in `derives`, else the "any_seat" lane.
- GUESS 4, `build`: a tick with no state literal fires on its tables as a whole ("any row").

New rule of probe 3, `read_loop_joins`: an `if` in `loop.py` whose test compares with one string literal joins that literal to the `lifecycle.<fn>` calls in its body, and to `<module>.<fn>` calls of a module the body imports with `from . import`. A literal that starts with "tick:" names a tick. Any other literal names a `do:` action. The loop gave seven joins: `cancel`, `constraint_zero`, `harness`, `merge`, `park`, `preempt`, `tick:batch_start`.

## (e) Files, the diff and the two runs

The diff of `D:/repos/rota/probes/flowchart/flowchart.py`, by function:

- New: `LOOP_PY`, `_module_file`, `read_loop_joins`, `cid`, `end_of` (the fold), `_records` (table box, then a box per state column).
- `build`: adds `joined_end`, which reads the loop joins and follows an imported module to its lifecycle calls. A `do:` action reads its loop join first, and its equal-name lifecycle function only when the loop has no join. A seat tick with a loop join gets tick-level end arrows. Every end arrow goes through `end_of`.
- `draw_full`, `draw_path`: the records come from `_records`. Arrow labels are quoted. In `draw_path`, a column box reaches each of its values for the walk, and those edges are not drawn.
- `main`: prints the loop joins and the ticks with a loop end.

The two runs, from the repository root:

```
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 1, copied to the scratchpad)
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 2)
cmp both pairs: SAME
1711be1b4ea161ed186be00a494cffc638d4f9aa272ec188bf7a10094a4d222c  flowchart.mmd
c2455e66b8e7a7c3750419d7dc118193c0e6a63354f0b78051cfb49bce709890  path.mmd
```

The run-1 copies are `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3a8d4c2-cdca-42d3-8f1d-12549648d58a/scratchpad/p3run1_full.mmd` and `p3run1_path.mmd` in the same folder. Neither chart holds a CR byte.

## (f) Token usage

The harness shows this agent no exact count. Probe 3 took about 30k tokens, inside the cap of 40k. The probe started no sub-agent.

## A declared end state per tick

After `loop.py`, a declared end state per tick would still add something, but not where probe 2 expected. The "not derived" list is down to four. Three of them lack a seat, which an end-state declaration does not fix, and the fourth, `constraint_zero`, writes no state. The remaining weakness is grain and order. Every seat tick except `batch_start` ends in all its seat's states, and the order inside a running batch lives in SQL joins, not literals. The per-mode `.tools` files can give each tick its own tools from code that exists, so a declaration is not needed for grain. A declaration of each tick's trigger order would duplicate the SQL, and a copy of the SQL can drift from it. I added no declaration.
