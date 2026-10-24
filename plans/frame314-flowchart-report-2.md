# Frame 314 probe 2 report: the flow chart gets its second half

Verdict: the tool now draws both halves of an arrow from six sources, by code only, and both charts are the same bytes on two runs. The path chart does not yet read from asked to merged in order. It reaches the merge, but it reaches the Critic's verdict through the message boxes, and it skips the running batch and the tests. The cause is one missing join: the scheduler's dispatch writes `batches.status = 'running'` through `lifecycle.start`, and no source the tool reads joins the tick `batch_start` to that function.

## (b) Evaluation

**Can a reader follow one change from asked to merged on `path.mmd`?** Partly. The front half now reads in order. The back half does not.

What reads in order:

1. `items approval = draft` wakes the Vision Keeper's `signoff` (drains).
2. `items approval = approved` and `items kind = in_scope` wake `slicing` (scheduler sql). The front-half gap of probe 1 is closed.
3. The Vision Keeper ends in `tickets (new row)`. That row wakes the Terminologist's `criteria` (scheduler sql, any row).
4. `items approval = approved` wakes the Architect's `grouping`. The Architect ends in `batches status = pending` (literal, from `batches_group`).
5. `batches status = pending` wakes the Developer's `batch_start` (drains).
6. `verdicts result = pass` wakes `merge`. `merge` ends in `batches status = merged` (literal, from `lifecycle.merge`), or in `deferred` when the merge conflicts.

Where the path breaks or misleads:

- `batches status = running` is not on the path. `lifecycle.start` writes it, and only the loop calls `start`. The tool does not read the loop. So `tests_missing`, `harness`, `tests_failing`, `review` and the whole Tester lane fall off the path ("no tick on the path").
- The path reaches `verdicts result = pass` through the Critic's lane, and the Critic's lane is reached through message boxes (`challenge`, `question`, `answer`). A reader sees "a message wakes the Critic, the Critic writes a pass". The real order is "a green test run wakes `review`".
- The fix loops on the path are the verdict loop (`verdicts result = fail` to `verdict_failed`) and the finding loops. The test-run loop is not on the path, because the harness end state is not derived.
- The path holds 17 message boxes and 172 arrows. The message fold makes every seat reach every other seat, so the path keeps most of the chart. A reader does not get a short path.
- A seat's end states are the union over all of its tools. Every tick of a seat points, through the lane, at every state the seat can write. The chart does not say which tick writes which state.
- The Vision Keeper lane points at `items approval = approved` (bound). `problem_set_approval` binds `approval` from a parameter, and the tool draws every CHECK value. The code refuses `approved` from the Vision Keeper ("Only the principal's sign-off approves an item"). The chart shows a write the code forbids.

**Arrows, derived and not derived.** Counts are for `flowchart.mmd`.

- Trigger arrows: 106. From `drains`: 36. From the tick's own SQL: 21, plus 2 "any row". From `scheduler.tick_*` SQL: 2 (both `slicing`), plus 45 "any row" (11 ticks).
- End arrows: 201. Literal: 39. Schema DEFAULT: 9 (the `messages status = open` row of each sending seat). Bound, drawn as every CHECK value: 144. New row of a stateless table that a tick waits on: 9.
- Tick nodes: 54 (48 predicates, some in more than one lane). Derived: 47. Not derived: 7, each drawn with a dashed arrow to the one "not derived" box.

The "not derived" list:

1. `cancel`: the action is `do:cancel`. The lifecycle function is `abandon`. No name joins them.
2. `preempt`: `do:preempt` and `do:park`. The lifecycle function is `defer`. No name joins them.
3. `harness`: `do:harness`. The function is `record_test_run`. No name joins them.
4. `constraint_zero`: no `do:` action names a lifecycle function.
5. `checkpoint_invalid` (any_seat): `DERIVED` with no `derives`, so no seat, so no tools.
6. `message_tips` (any_seat): the same.
7. `survey` (any_seat): `derives` is `SURVEY_ORDER`, imported from the scheduler and not resolved.

**Where the chart is still unreadable or misleading.**

- Rule 3 makes every `CHECK (col IN ...)` column a state. Many are classifications: `ledger.kind`, `refs.src_table`, `batch_touch.grain_kind`, `items.kind`. They draw 59 "final" boxes, and most of them are not lifecycle states.
- `items approval = pending` is marked "final". Nothing the tool reads fires on it. The principal's gate holds it, and the principal is not a tick.
- `test_runs result = error` stays a trigger of `harness`. Point 5 of the brief draws it as the state the harness leaves behind. The tool can only do that when the harness end state is derived, and it is not (item 3 above).
- 144 bound arrows. A bound parameter fans out to every CHECK value. Half the end arrows are this fan-out.
- The eleven onboarding and round ticks fire on whole tables ("any row"). Their SQL tests counts and joins, not state literals.
- `messages` remains a hub in the full chart. `path.mmd` folds it per verb, and the fold connects everything.

**Summary for a reader who does not know the code.** The chart now answers "what happens next" for 47 of 54 tick nodes, at seat grain. It answers it for the scheduler only where the action and the lifecycle function share a name, which is `merge` only.

## (a) The charts

- `D:/repos/rota/probes/flowchart/flowchart.mmd`: 574 lines. The full chart. Thin arrow: a state wakes a tick. Thick arrow: a session or an action ends in a state, labelled literal, default, bound or new row. Dashed arrow: to "not derived".
- `D:/repos/rota/probes/flowchart/path.mmd`: 300 lines. The nodes on a walk from `items approval = draft` (the schema DEFAULT) to `batches status = merged`. Message boxes are trapezoids, one per verb.

## (c) What the sources did not give

1. The join from a scheduler action to its lifecycle function, for `cancel`, `preempt` and `harness`. The loop (`rota/core/loop.py`) holds it.
2. The join from the dispatch of `batch_start` to `lifecycle.start`. The loop holds it too. This gap removes `running` and the tests from the path. It is the worst gap.
3. The tick's own tools. A seat's tools come from the graph's `writes` edges, which are per seat, not per tick. The per-mode `.tools` files (`rota/roles/prompts/<role>/<mode>.tools`, shown by `python -m rota.tools.map mode`) hold the per-tick list. The brief did not name them as a source.
4. The allowed value of a bound parameter. The api checks it in Python (`problem_set_approval` refuses `approved`), not in a literal.
5. The difference between a lifecycle state and a classification column. The schema constrains both with the same `CHECK`.
6. The seats of `DERIVED` ticks with no `derives`, and `SURVEY_ORDER`.
7. Five graph tools have no `@op` function: `criteria.cite`, `frame.cite`, `glossary.cite`, `model.cite`, `problem.cite`.
8. The brief said `api.py` holds `UPDATE ... SET` and `INSERT` literals. It mostly does not. An `@op` function stages a row with `ctx.writes.append((table, id, values))`, and the door writes it. The tool reads those staged rows with `ast`.

## (d) Every guess in code, named

Four guesses remain. Each one is a rule in code, not a hand-written table.

- GUESS 1, `body_states`: a tick with no drains fires on the state literals its SQL tests. Only a CHECK column counts. Other literals are filters (3 dropped: `messages.from_role`, `messages.verb`, `item_provenance.provenance`). `NOT EXISTS (...)` and `NOT IN (...)` are cut first (16 cut).
- GUESS 2, `written_states` and `ctx_writes`: a bound value can be any value the CHECK allows.
- GUESS 3, `build`: a `DERIVED` tick gets one node per seat in `derives`, else the "any_seat" lane.
- GUESS 4, `build`: a tick with no state literal fires on its tables as a whole ("any row").

Two rules in code also shape what the tool reads. Neither one names a node or an edge.

- `closure(..., skip_fragments=True)`: a scheduler function annotated `-> str` returns a SQL fragment, for example `not_parked`. Its exclusion is split across string constants, so the tool leaves it out of the trigger SQL.
- `ctx_writes`: a state column that a staged row leaves out is not drawn, because an upsert keeps the old value.

The hand tables are gone, on Roman's rule of 2026-10-24 14:10:

- Probe 1's `ARTEFACT_TABLE_GUESS` went. The `@op(artefact, verb)` registry in `api.py` joins a graph edge to a function, and the function names its table. The chart lost probe 1's lane-to-table write arrows for tables nothing waits on, and the guess that `code` is `batches`. The Developer's `code.commit` now stages `batches.head_commit`, which is not a state, so no arrow comes from it.
- My first draft had `ACTION_LIFECYCLE_GUESS` (`cancel` to `abandon`, `preempt` to `defer`, `harness` to `record_test_run`). It went before the first committed run. The chart lost the end states of those three actions. They are "not derived".
- Probe 1's GUESS 5 (a `messages` edge writes a `messages` row) is now a derivation: the edge type and the table share the name `messages`, and the state is the schema DEFAULT of `messages.status`.

No night was read. The tool opened no `.rota/*.db`, log or report. I opened none either, and compared the charts with no night and no scene.

## (e) Files, the diff and the two runs

The diff of `D:/repos/rota/probes/flowchart/flowchart.py` (280 to 750 lines), by function:

- Module: four new sources, two output paths, `NOT_DERIVED`, `PATH_START_COL`, `PATH_END`. `ARTEFACT_TABLE_GUESS` removed.
- New: `_split_top`, `read_schema` (state columns and defaults), `read_functions`, `_returns_str`, `closure`, `_imports`, `read_ops` (the `@op` registry), `strip_exclusions`, `_values_list`, `written_states` (UPDATE and INSERT literals), `ctx_writes` (staged rows), `sid`, `build`, `state_marks`, `_tick_node`, `_end_arrow`, `draw_full`, `draw_path`.
- Changed: `read_predicates` adds the scheduler SQL of delegating ticks and the `do:` actions. `body_states` cuts exclusions and splits states from filters. `main` writes both files and prints the counts.
- Gone: the "(end)" mark, replaced by "held" and "final". The lane-to-table write arrows, replaced by end arrows.

The two runs, from the repository root:

```
.venv/Scripts/python.exe probes/flowchart/flowchart.py
cp probes/flowchart/*.mmd to <scratchpad>/run1_*.mmd
.venv/Scripts/python.exe probes/flowchart/flowchart.py
cmp both pairs: SAME
a45664b6abdab1bb8ee3a3f7e53bc9d55a6cdbeb3d92331659220d787b4bc192  flowchart.mmd (both runs)
8cb97cc364c971a451edf4b2fbc24e8bc04d961f93efd0aff10b6ac3ecfc525f  path.mmd (both runs)
```

The copies are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3a8d4c2-cdca-42d3-8f1d-12549648d58a/scratchpad/`. Neither chart holds a CR byte.

## (f) Token usage

The harness shows this agent no exact count. The estimate is about 95k tokens in total, over the cap of 60k. Reading the six sources and three debug runs took the excess. The probe started no sub-agent.

## A declared end state per tick

A declared end state per tick would make the chart better, but less than the "not derived" list suggests. Four of the seven come from joins that exist in `loop.py` (`cancel`, `preempt`, `harness`, and the `start` behind `batch_start`). Reading the loop's dispatch, or naming the action the same as its lifecycle function, closes them without a declaration. Three come from ticks with no seat, which a declaration of `derives` closes, not a declaration of end state. The real gain of a declaration is grain: today every tick of a seat ends in every state the seat can write, and 144 arrows are a bound fan-out. The per-mode `.tools` files give the per-tick tool list from code that exists, so the next probe can read those first. A declaration is then needed only where the tools still fan out. I added no declaration.
