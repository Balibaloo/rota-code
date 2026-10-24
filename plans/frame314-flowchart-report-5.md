# Frame 314 probe 5 report: the numbered spine, top to bottom

Verdict: `path.png` reads top to bottom, from "1. items.approval = draft" to "42. batches.status = merged". The main line runs down the middle, and the loops come back up as dashed arrows to an earlier number. The front half is two page-exchange boxes with the Principal between them. The spine does not pass through `items.approval = pending`, because nothing in the sources writes `pending` before the verdict.

## (b) Evaluation

**The numbered steps, as `path.mmd` draws them (44 nodes):**

1. items.approval = draft
2. Vision Keeper: gate: signoff
3. page exchange: present, submit
4. Principal: verdict on the page
5. page exchange: ask, converse, deliver, relay, report, verdict
6. items.approval, set by the session
7. items.kind, set by the session
8. items.approval = approved, held
9. items.approval = contested
10. items.approval = pending, final
11. items.kind = in_scope
12. items.kind = out_of_scope, final
13. Vision Keeper: fix: contested
14. Vision Keeper: start: slicing
15. tickets, new row
16. Terminologist: start: criteria
17. criteria, new row
18. Architect: start: grouping
19. batches.status = pending
20. Developer: start: batch_start
21. batches.head_commit, new value
22. no run at head
23. no verdict at head
24. batches.status = running, held
25. config, new row
26. Tester: start: tests_missing
27. tests, new row
28. scheduler: gate: harness
29. test_runs.result, set by the session
30. a run at head
31. test_runs.result = error
32. test_runs.result = fail
33. test_runs.result = pass, final
34. every result pass at head
35. Architect: fix: exhausted
36. Vision Keeper: fix: exhausted
37. Critic: gate: review
38. verdicts.result, set by the session
39. verdicts.result = fail
40. verdicts.result = pass, held
41. scheduler: gate: merge
42. batches.status = merged, final
43. Developer: fix: tests_failing
44. Developer: fix: verdict_failed

**Does the picture read top to bottom?** Yes. The four changes:

1. Numbering. Each node gets its place in a topological order from step 1, with ties broken by name. Every edge out of a `fix` tick is a loop. Any other cycle is cut by a depth-first search that visits the child farthest from the merge first. So the cycle through `config, new row` is cut at "needs a config row" back to slicing, not at tickets to grouping. `flowchart TB`. A loop is dashed and does not set the rank.
2. Fold. The message nodes and message modes on a walk from draft to approved are folded, by connected group, into one "page exchange" node each. The label lists the verbs from the mode `.tools` files. The Principal splits the traffic into two groups: 3 (present, submit) and 5 (ask, converse, deliver, relay, report, verdict).
3. The Principal's gate is node 4 on the spine, not a lane. The contest is node 9, `items.approval = contested`, with its fix tick at 13 looping back to draft.
4. Plain words. One function, `arrow_words`, derives the arrow text from the node ids, and the ids come from the SQL, the drains and the staged rows. Examples: "on approval = draft" (a drain), "status = running" (a SQL literal), "no run at head" and "every result pass at head" (subqueries), "sets status = pending", "adds a tests row", "needs a criteria row", "new head_commit", "one value" (a column to its value).

**Counts.** Probe 4: 65 boxes and 87 arrows, left to right, in lane and table boxes. Probe 5: 44 boxes and 61 arrows, top to bottom, with no lane or table boxes. 11 of the 61 arrows are dashed loops.

**The worst remaining gap.** The front half reads draft, signoff, page exchange, Principal, page exchange, approval set by the session. It does not read draft, pending, verdict, approved or contested. `pending` has no writer that the sources name except the bound `items.approval` column, and the tool cannot order the values of one bound column. The second page exchange also writes `items.kind`. A reader sees "the Vision Keeper sets kind" after the verdict, which is the price of the fewest-message-hops walk from probe 4.

Other spots:

- `config, new row` (25) is still on the path, as a JOIN of slicing.
- The fold label "page exchange" is the probe's name. The verbs in the label come from the sources.
- The values 10 and 12 (`pending`, `out_of_scope`) are final dead ends of their bound columns.

## (a) Files

- `D:/repos/rota/probes/flowchart/path.mmd`: 108 lines, `flowchart TB`.
- `D:/repos/rota/probes/flowchart/path.png`: 1142 by 2530 pixels.
- `D:/repos/rota/probes/flowchart/mmd2dot.py`: the coordinator's converter, copied. Two changes: the direction comes from the `flowchart` line, and a dashed arrow gets `constraint=false`.
- `D:/repos/rota/probes/flowchart/flowchart.mmd`: unchanged in content, written again by the same run.

## (c) What the sources did not give

1. A writer of `items.approval = pending` other than the bound column.
2. Which message a gate needs. The fold hides the traffic but does not remove the `items.kind` detour.
3. The order of the values of one bound column.

No night was read, and no chart was compared with a night or a scene.

## (d) Guesses in code

The six from probe 4 stay. Probe 5 adds rules, not guesses about the sources:

- `number_walk`: a fix tick's out-edges are loops. Other cycles are cut by a search that visits the child farthest from the merge first. Ties go by name.
- `_fold_pages`: message nodes and modes on a walk from draft to approved fold by connected group. The principal is never folded.
- `arrow_words`: the words come from the node ids. "page exchange", "one value" and "set by the session" are the probe's words.

## (e) The diff and the two runs

The diff of `D:/repos/rota/probes/flowchart/flowchart.py`, by function:

- New: `_node_index`, `cond_words`, `arrow_words`, `_fold_pages`, `_reach_plain`, `_reach_steps`, `number_walk`, `_path_label`.
- `draw_path`: rewritten. The output is numbered, `TB`, with no subgraphs, folds and plain words.

The two runs, from the repository root:

```
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 1, copied to the scratchpad as p5r1.mmd)
.venv/Scripts/python.exe probes/flowchart/flowchart.py   (run 2)
cmp: SAME
1f4c2bef3e092f51eca7d7b9dfee3d33e46bb7bcabe634e406fd15794ad1091b  path.mmd
6c2915054105b8778a2a7df72906c6b111a561245a9bb9584cd0908633d79d67  flowchart.mmd (unchanged since probe 4)
```

No file holds a CR byte.

## (f) Token usage

The harness shows this agent no exact count. Probe 5 took about 35k tokens, inside the cap of 50k. The probe started no sub-agent.
