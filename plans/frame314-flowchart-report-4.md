# Frame 314 probe 4 report: the path without hubs, the main walk, the subquery order

Verdict: in the rendered `path.png` a reader can follow one change from asked to merged. The back half is clean: running batch, tests missing, tests, harness, test runs, the three head conditions, review, verdict, merge, merged. The fix loops `tests_failing` and `verdict_failed` return to the new head commit. The front half reads, but through a knot of message traffic between the Liaison, the principal and the Vision Keeper. `flowchart.png` is unreadable at 253 boxes and 721 arrows, as expected for the full chart.

## (b) Evaluation

**Counts on `path.mmd`, as boxes and arrows after `mmd2dot.py`:**

| Step | Boxes | Arrows | Merged reached |
|---|---|---|---|
| Probe 3 (committed `abc7a2f1`) | 89 | 196 | yes |
| After change 1: no lane hub, end arrows from the tick, only to a node a tick reads, everything the start reaches | 153 | 338 | yes |
| After change 2: main walk plus fix loops, no subqueries | 47 | 58 | yes |
| After change 3: subquery order edges (the committed output) | 65 | 87 | yes |

Change 1 alone made the chart larger. With no hub, each tick and each message mode draws its own arrows, so the start reaches more nodes. Change 2 made it smaller, and change 3 added the head conditions and the Tester chain back.

**Does the path read from asked to merged in the picture?** Yes, with one knot.

1. `items approval = draft` wakes `signoff`. The Vision Keeper sends "submit to Liaison".
2. The Liaison's `submit` mode sends "present to Principal". The principal answers with "verdict" and "converse".
3. The Liaison's `verdict` and `converse` modes send deliver, ask and relay messages. The Vision Keeper's `relay` and `deliver` modes write `items.approval` and `items.kind` (bound).
4. `approved` and `in_scope` wake `slicing`. The Vision Keeper ends in `tickets, new row`. Tickets wake `criteria` and, by the JOIN, `grouping`.
5. `grouping` ends in `batches status = pending`. `pending` wakes `batch_start`, which ends in `running` (loop join) and sets `batches.head_commit`.
6. `running` and `criteria, new row` wake `tests_missing`. The Tester ends in `tests, new row`. That row and "test_runs at head: no row yet" wake `harness`.
7. `harness` writes `test_runs.result` (bound). Three conditions wake `review`: "test_runs at head: some row", "every result = pass", "verdicts at head: no row yet".
8. `review` writes `verdicts.result`. `pass` wakes `merge`, which ends in `merged`.
9. Fix loops: `test_runs result = fail` and `error` wake `tests_failing`, and `verdicts result = fail` wakes `verdict_failed`. Both set the head commit again, which makes "no row yet" true again. `exhausted` (Architect and Vision Keeper) also stays, because its ends return to the path through "report to Liaison" and `items approval = draft`.

The knot is step 3. The walk takes ask, deliver and report traffic that a human gate does not need, because `slicing` needs `items.kind = in_scope`, and in these sources only the Vision Keeper's message modes write `items.kind`.

**What the subqueries gave.**

- 5 head conditions: "test_runs at head: every result = pass", "test_runs at head: some row", "test_runs at head: no row yet", "verdicts at head: no row yet", "findings at head: no row yet".
- 5 condition-to-tick arrows ("at head"): 3 into `review`, 1 into `harness`, 1 into `structural_review`.
- 5 input arrows into the conditions: 2 "new head" from `batches.head_commit`, 1 "all at head" from `test_runs result = pass`, 1 "row at head" from the `test_runs.result` node, and 1 "new head" into the findings condition.
- 4 "joins" arrows from a new row of a stateless table: `tests` to `harness`, `criteria` to `tests_missing`, `tickets` to `grouping`, `config` to `slicing`.
- 3 ticks lost the plain `running` trigger to a finer one: `harness`, `review`, `structural_review`.

**Where the chart still misleads.**

- `config, new row` joins `slicing`, and `batch_start` writes a config row. The arrow is a true JOIN, but it is noise for a reader.
- The bound fan-out stays as one dotted arrow per value from the column node. `items.approval, bound` points at `approved`, which the code refuses from the Vision Keeper.
- `tests_missing` keeps its plain `running` trigger. Its subqueries are NOT EXISTS with no head compare, so they draw nothing, and "no test yet" is not a node.

## (a) The charts

- `D:/repos/rota/probes/flowchart/path.mmd`: 189 lines. `D:/repos/rota/probes/flowchart/path.png`: 1490 by 1910 pixels.
- `D:/repos/rota/probes/flowchart/flowchart.mmd`: 1078 lines. `D:/repos/rota/probes/flowchart/flowchart.png`: 16519 by 13590 pixels.

Rendered with the coordinator's `mmd2dot.py` and `dot.exe -Tpng -Gdpi=72`. The full chart failed in `dot` ("trouble in init_rank") until I added `-Gnewrank=true` on the command line. I did not edit the converter. To fit the converter, the charts now use shapes it parses (`[[...]]` for a message, `((...))` for a condition) and labels with no brackets ("status = merged, final").

## (c) What the sources did not give

1. The worst remaining gap: the knot of message traffic between the approval and the slicing. The sources give each message mode its tools, but not which message a gate needs. The walk prefers the fewest message hops, and the fewest still pass through ask, deliver and report, because only those modes write `items.kind`.
2. The meaning of a NOT EXISTS with no head compare, such as "no test for this criterion yet". The tool draws it as nothing.
3. The tick of a message wake that is not the receiver's verb. Seats whose ticks have no `.tools` file keep a lane-level end in the full chart: Architect, Vision Keeper, Principal, Researcher. Of 50 seat-tick nodes, 44 have a `.tools` file.
4. The allowed value of a bound parameter, and the line between a state and a classification column, as before.

New sources in probe 4: `rota/roles/prompts/<seat>/<mode>.tools`. A tick's name and a mode file share the name. A message's verb and the receiver's mode file share the name too, since the scheduler wakes a message with `detail=verb`. No night was read, and no chart was compared with a night or a scene.

## (d) Guesses in code

Six guesses, each a rule and named `GUESS n` in the code. There are no hand tables.

1. `body_states`: SQL state literals are triggers. Other literals are filters.
2. `written_states`, `ctx_writes`: a bound value is any CHECK value.
3. `build`: a `DERIVED` tick lands in each `derives` seat, else "any_seat".
4. `build`: a tick with no state literal fires on its tables, "any row".
5. `conditions`: a subquery that compares with `head_commit` means "some row at head" (EXISTS), "every row has col = v" (NOT EXISTS with `col != 'v'`) or "no row yet" (other NOT EXISTS). A JOIN or a bare EXISTS on a stateless table needs that table's new row.
6. `_w`: the main walk takes the fewest message hops first, then the fewest edges.

The rules of the walk are code, not guesses about the sources. A tick's SQL literals on different columns, its JOINs and its head conditions all hold at once, so the walk adds one route into each. A `drains` list is any one of its states. A fix loop is a `fix`-band tick that a path node triggers and whose ends return to the path.

## (e) The diff and the two runs

The diff of `D:/repos/rota/probes/flowchart/flowchart.py` (750 to 1242 lines), by function:

- New: `_subqueries`, `conditions`, `cond_id`, `cond_label`, `read_tick_tools`, `_bound_cols`, `_read_targets`, `path_edges`, `_w`, `_dist` (Dijkstra), `_shortest`, `path_nodes`, `_mode_node`, `_msg_node`.
- `ctx_writes`: also returns staged non-state columns as "set" (used for `batches.head_commit`).
- `build`: tick-level ends from `.tools` files. Message modes and message nodes. Head conditions replace the plain outer-table trigger. JOIN needs. Condition inputs. Lane-level ends only for seats without `.tools` coverage.
- `_records`: no column subgraph. A bound column is a node with dotted arrows to its values.
- `draw_path`: rewritten on `path_nodes`. `draw_full`: draws modes, message nodes, conditions, head nodes.

The two runs, from the repository root:

```
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 1, copied to the scratchpad as p4r1_*.mmd)
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 2)
cmp both pairs: SAME
6c2915054105b8778a2a7df72906c6b111a561245a9bb9584cd0908633d79d67  flowchart.mmd
97e67828ab6b902b40ca81140b1ae509d526c8ed5af581d05bb5d648dbd15572  path.mmd
```

Neither chart holds a CR byte.

## (f) Token usage

The harness shows this agent no exact count. Probe 4 took about 70k tokens, over the cap of 50k. The excess went to the walk rules, which took three tries (all walks, plain shortest, fewest message hops with the AND closure), and to two views of the PNGs. The probe started no sub-agent.
