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
| 2 | click n35 s115 | vision_keeper slicing | `problem.consult`: all five items, nothing marking the one in the refs | the item to slice, set apart from the account of what the program does today | the push sets the wake's items apart and lists the rest by id (`runner.push_working_set`, 2026-09-13) |
| 3 | click n35 s116 | terminologist criteria | 33 callables (mostly tests), the whole glossary, one ticket headline | the item text, the principal's sentence, and the source of the callable the ticket says "next to" (`utils.py::echo`) | the push carries the item and its statements, and the module of every callable the ticket's words name (`runner.push_working_set`, 2026-09-13) |
| 4 | click n35 s116 | terminologist criteria | the first-turn id collision: the criterion id was the item's id | nothing missing; the refusal's route worked on the second turn | none |
| 5 | click n35 s117 | architect grouping | batches, criteria, the model, the tickets | nothing missing for grouping; two turns lost to `batches.consult(id=...)` against a no-argument signature | the signature line in the push says `()`; a brief line, if measured |
| 6 | click n35 s130 | architect annotate | tickets, criteria, the model; `code.probe('echo_json')` found nothing | the callables the ticket names ("next to echo": `src/click/utils.py::echo`); it predicted a new root file `echo_json.py` | the callables lens, pushed by the batch's ticket words (`runner.push_working_set`, graph edge) |
| 7 | click n35 s133 | developer batch_start | the pre-fix wake | the same as finding 1 | measured on night 37: nights 35 and 36 ran from a scratchpad copy of the gauntlet script that found no `rota` module, never onboarded, and drove an old `walk.py` on the previous night's database. The wakes read above are real (the repository's code ran them); the nights' outcomes are not measurements |
| 8 | click n35 s133, s134 | developer batch_start, architect touch_strayed | the Developer wrote `src/click/main.py` with its own `def echo`; the Architect, shown the diff and the criteria but not its prediction, judged it foreseen | the Architect needs its own prediction in the stray wake; the Developer needs a fact: `echo` is defined once, in `utils.py` | `batches.expect` pushed to the Architect; a `code.write` door: a second definition of a name the tree has once is refused |
| 9 | click n35 s135, s138 | tester tests_missing, answer | criteria, glossary, references, tests, the ticket | the item and the principal's words (as finding 1); and the first import guessed `tests.test_utils`, then `app.commands` | `batches.expect` for the Tester too; the import doors hold |
| 10 | click n35 s138 | tester answer | nineteen turns: the refusal "a quote inside id ended it early" led the model to write `'''...'''` placeholders, refused as placeholders, then the same body five times | the refusal's example is copied literally by a 9B model | the refusal names the shape without an example to copy; measured on the TS cases |
| 11 | click n35 s099 | liaison agenda | `ledger.list`: all 51 open rows, 15,500 characters | the page's seven, which the refs name | the push shows the page's rows and counts the rest (`runner.push_working_set`, 2026-09-13) |
| 12 | click n37 s004 | liaison quarantined | "1 abandoned" and nothing else; the Liaison sent `refs=["tick:quarantined"]` three times | what stalled: the tick's batch or item, and its attempts | the predicate carries the tick's refs and says what stalled (`predicates.quarantined`, 2026-09-13) |
| 13 | click n37 s135 to s137 | developer batch_start | with `batches.expect` the Developer read `utils.py`, the right file, and wrote a span into it; the span ended inside a multi-line signature and the merged file failed to parse; six identical writes a session, three sessions | where the span cut: the statement's lines, and the two spans that work | the span door names the cut statement and the whole-statement spans (`code.write`, 28c26f8) |
| 14 | click n37 s135 | developer batch_start | `the principal said: []` although one ratified statement stood behind the item | the statement the item was read from; `problem.assert` linked statements only from tick wakes' refs, never from a message's | the link is read from the trigger message too (1c30249) |
| 15 | click n38 s130, s131 | developer batch_start | the Developer read `utils.py` and wrote `echo_json` beside `echo`; every write was refused: "utils.py reaches the outside at line 547 (os.path.expanduser)", click's own code | the fence judged the merged file, not the change | the fence takes the original file as a baseline and refuses only new reaches (`fence.check`, 2026-09-13) |
| 16 | click n38, 38 reconcile sessions | vision_keeper reconcile | the account and one prose file; the model logged "README says X; the code shows X" and was refused as a restatement three to ten times a session, then `attest found` was refused for having no ledger | the exit when everything agrees | the restatement refusal names the exit: attest none_found; `code.prose` takes a path |
| 17 | click n38 s010, s099 | liaison verdict relay | the relay to each owner; after the first, every repeat refused as a second answer, three identical turns | one relay per owner with all its rows | a brief line, if measured; the fixed point ends it at three |
| 18 | click n38 s075 to s077 | architect boundary | `model.amend` refused four or five times a session as "what the product does, an item already says it" | the exit when no candidate is a constraint | a brief line: attest with nothing when every candidate is refused |

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
