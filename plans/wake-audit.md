# The wake audit

Started 2026-09-13. Roman's principle: every role gets what it needs and
gives what the others need. The design says so; the wakes did not. A
Developer's batch_start wake on tipsI carried one ticket line, four
criteria naming a callable that did not exist, a probe hint and a glossary
miss, and none of the item, the principal's words, the predicted touch set
or the tests. The reads a role has are the graph's edges; the runner pushes
the ones that take no argument (`runner.push_working_set`). Nobody had read
a wake as the person doing that job would.

## Method

1. Run a walk. `probes/wake_dump.py <run>` writes every session in order
   as the role saw it: the wake as pushed, each turn's calls, each turn's
   feedback. Night 35 on click is the first run read.
2. For each mode, read the wake against the rows the database held, and
   answer two questions: what did this role need here and not get, and
   what did it produce that another role needs and cannot reach.
3. Each answer is a push, an edge, or a brief line, one commit each,
   measured on the register cases of that mode and on a night.

The list below is every mode of the delivery loop, in wake order, then
onboarding. A row is filled when its wake has been read.

## Findings

| # | Session | Mode | Shown | Needed and missing | Fix |
|---|---|---|---|---|---|
| 1 | tipsBC s58, click nights 32 to 34 | developer batch_start | the ticket line, the criteria, a probe hint, a glossary miss | the item, the principal's sentences, the predicted touch set, the batch's tests | `batches.expect`, pushed (7954ef7) |
| 2 | click n35 s115 | vision_keeper slicing | `problem.consult`: all five items, nothing marking the one in the refs | the item to slice, set apart from the account of what the program does today | owed: the push marks the wake's item, or the mode pushes `problem.consult` for the refs alone |
| 3 | click n35 s116 | terminologist criteria | 33 callables (mostly tests), the whole glossary, one ticket headline | the item text, the principal's sentence, and the source of the callable the ticket says "next to" (`utils.py::echo`) | owed: push the item and its statements; push `code.source` of the callables the ticket names |
| 4 | click n35 s116 | terminologist criteria | the first-turn id collision: the criterion id was the item's id | nothing missing; the refusal's route worked on the second turn | none |
| 5 | click n35 s117 | architect grouping | batches, criteria, the model, the tickets | nothing missing for grouping; two turns lost to `batches.consult(id=...)` against a no-argument signature | the signature line in the push says `()`; a brief line, if measured |

## To read (night 35)

- developer batch_start (with `batches.expect`), tests_failing, verdict_failed,
  touch_mistaken
- tester tests_missing, challenge, answer
- critic review, challenge
- architect annotate, touch_strayed, structural_review, escalate
- liaison touch_note, submit, landing, agenda, quarantined
- vision_keeper signoff, contested, relay
- terminologist criteria, criterion_repair, deliver
- researcher question

Onboarding modes (orient, reconcile, define, survey, boundary, frame,
blindspot) after the loop.

## What "gives what the others need" means here

A role's writes are the rows the next role reads. The audit asks the
reverse question at each write: does the row carry what its reader needs,
in the reader's terms. A criterion that names a surface the tree lacks; a
touch set with paths but no symbols; a test that asserts something and
prints nothing about why. Those are findings on the writer's side, and the
door or the brief that fixes them belongs to the writer's mode.
