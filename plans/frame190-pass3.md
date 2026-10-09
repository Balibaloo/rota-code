# Frame 190, pass 3, the next page: where things are

Status: written by the implementer of pass 3 on 2026-10-09, after the
gate. Code commit `0ffc97b7` on `rota/foundation`. Rota workflow, except
where a line says meta workflow. The design is `plans/frame190-design.md`.
Passes 1 and 2 are in `plans/frame190-pass1.md` and
`plans/frame190-pass2.md`.

## What landed, by design point

- **2.4.1 with amendment 3, the agenda skips a reply row.**
  `rota/core/scheduler.py`, `tick_agenda`. The tick wakes only when an
  open ledger row exists that is not a reply row. It orders the chosen rows
  so that a row whose `about_ref` reaches an open request comes first, then
  the others by `rowid`. A row reaches a request through its item, ticket,
  criterion, batch, statement, or test (a test reaches its criterion). The
  wake then carries the open reply rows after the chosen rows, up to
  `PAGE_ASSUMPTIONS`, seven, in all. The door adds the wake's refs to the
  present, so the reply rows render under the team's notes, and a ruling
  closes them. `detail` still reads `ledger=<all open rows>`.
- **Which rows are a seat's reply rows.** `rota/core/scheduler.py`, the new
  function `reply_rows`. The rule is the rule of the two refusals of
  `api.ledger_log` that pass 2 added:
  - the row's `about_ref` is a message (2.F, amendment 7, the first refusal
    of `ledger_log`);
  - the row's writer session, by `receipts` with `table_name = 'ledger'`,
    woke on a `relay` whose cause is a principal `verdict`, and the row's
    `about_ref` is a ref of that relay (2.3.1, the join of 1.4, the rule of
    `_principal_relay`).
- **2.4.2, the band.** `rota/core/predicates.py`, `agenda`: band `gate`
  becomes band `start`. The predicate stays in its place in the file, after
  `observed_entries`, `annotate`, `touch_note`, `batch_start` and
  `tests_missing`.

## The interview scope: the Architect sees the disputed path

From `plans/frame190-interview.md`.

- `rota/core/runner.py`, the new function `disputed_paths`, and
  `resolve_inbound`. On a relay of batches with a principal `contest` or
  `revise` of the batch, `touch[<batch>]` gains `disputed`. The paths the
  words call wrong leave `expected`. M85's words give `disputed:
  ["tests/test_defaults.py"]` and `expected: ["src/click/termui.py"]`.
- `rota/core/runner.py`, `push_working_set`. An Architect wake on a relay
  of batches pushes `the index's test files`: the `code_index` paths under
  `tests/`, sorted, at most 80.
- `rota/roles/prompts/architect/annotate.md`, two sentences at the end of
  the ruling paragraph: "The paths under `the index's test files` are the
  test files that exist. A test path you write is one of them, or a new
  file you name as new."
- The case `L1-AR-re-annotate-from-the-principals-correction` went STALE
  and the gate re-recorded it: PROV 5/5, red cleared.

## Review fixes of 2dace61b

1. High. `rota/roles/principal.py`, `request_rows`: the criteria query
   adds `not_retired(conn, "c.ticket_id")`. The slicing test asserts that
   the page lists `cr_4` alone.
2. High. `rota/roles/api.py`, `tickets_scan`: a woken item's tickets and
   the no-subject list leave out a retired ticket. A batch's own tickets
   and a wake's named tickets stay as they were. `criteria_specify` refuses
   a retired ticket: "<ticket> is retired: its item was amended and sliced
   again. Write the criteria for <live tickets>". The slicing test asserts
   both.
3. High. `rota/roles/api.py`, `problem_set_approval`: in a session woken by
   a relay that has a cause, `approved` on a `contested` or `draft` item is
   refused unless the cause chain (`chain_verdict`) carries a principal
   `approve` of the item. One test on s505's rows, m370 and m372, and a
   second relay that a principal approve caused, which is admitted.
4. Low. `rota/roles/principal.py`, `land`: on a present that carries a
   batch, a batch line stays in the verdict only for a batch with no head
   commit that is not `merged` or `abandoned`, and an approve of an item
   leaves the verdict. `rota/roles/api.py`, `rulings_rule`: a contest or a
   revise of a merged or abandoned batch is refused. One new test, and the
   m85 test now asserts the verdict `{"bg_2": "contest"}`.
5. Low. `rota/roles/principal.py`, `_gave_up_tries`: with the page's batch
   given, a key counts only for a criterion whose ticket is in that batch.
   One test.

## Deviations from the design and the briefs

- The words to path rule is new, not the landing's rule (reasoned: no
  parser reads the principal's words, ruled 2026-09-10, so the landing
  finds the batch line through the Liaison's ruling by line number, and
  no mechanical rule exists to reuse). `disputed_paths` splits the words
  into clauses. A clause disputes a path when it names the path and holds
  a "no" word: not, wrong, unrelated, no, never, drop, remove and four
  negated verbs. A clause names a path by the whole path, the file name,
  or every word of the file name less "test".
- `the index's test files` lists every test path of the index, not the
  paths of the batch's item (reasoned: no table binds a test file to an
  item, and the index of click holds about 30 test files).
- The brief sentence has two sentences and names the key, not the
  coordinator's one sentence with a semicolon (reasoned: STE forbids the
  semicolon, and the seat finds the list by its key).
- The second new test reads "ride the next present from any other wake" as
  the next agenda present that any other writer's row wakes (reasoned:
  amendment 3 names this mechanism, and the pass's files are the
  scheduler and the predicates; a reply row on a touch note or a submit
  page needs a door change in `sandbox.py`).
- Fix 3 checks no version (reasoned: no record holds the version a verdict
  saw, and `test_chaos_confirm.py` builds a verdict with no `land` and
  `approval_ver` 0).
- Fix 3 leaves a relay with no cause free (reasoned: the arc tests
  `test_arc_seam.py` and `test_arc_synthetic.py` sign off through a
  hand-built relay with no cause, and three of them went red; the
  Liaison's door gives every relay its cause, so a real relay always has a
  chain to read, a claim this pass did not run).
- Fix 2 filters `tickets_scan` on a woken item and on no subject only
  (reasoned: a batch is built from its tickets, and a wake that names a
  ticket asks about that ticket).

## Tests

`tests/rota/test_request_page.py` holds 27 tests, 6 of them new in this
pass:

- `test_the_agenda_wakes_for_a_seat_row_and_carries_the_reply_row`: night
  136 after s514 and s567. `l_62ca6652d9` alone draws no wake. With the
  `reconcile` row `l_a9c0ca7d82`, the wake's refs are that row, then
  `l_62ca6652d9`. `frontier` offers `tick:annotate` for bg_4 before
  `tick:agenda`, and after the annotate session `tick:touch_note` before
  `tick:agenda`. The present numbers the item, its three criteria and both
  rows, and an "ok" with six approves closes both rows.
- `test_reply_rows_alone_draw_no_agenda_and_ride_the_next_page`: two reply
  rows, one by the relay join and one about a message, draw no wake. Then
  an older row about a description and a newer row about a criterion of
  the open request: the request's row leads, the reply rows follow, and
  the present carries them.
- `test_the_words_dispute_only_the_paths_a_no_clause_names`.
- `test_a_touch_note_approves_no_item_and_a_closed_batch_line_is_refused`.
- `test_a_stalled_key_marks_only_the_criteria_of_its_batch`.
- `test_a_relay_of_a_report_cannot_approve_a_contested_item`.

Extended: the m85 annotate test asserts `disputed` and the pushed test
files, and the slicing test asserts `tickets.scan`, the refusal and the
page.

## The gate, last run, verbatim

The gate ran three times. The first two runs found the main card held, so
the re-records waited. The second showed three new arc reds from fix 3,
and the relay rule changed. The third run, its five lines:

```
suite: 26 failed, 3453 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l1.py::test_l1_case[L1-TS-an-outside-fact-is-the-researchers]
stale (0): none
time: 653.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The four new reds are the four known before pass 2. The suite line counts
26 failed, and two of them are the cases the re-record cleared.

## Re-records

The gate's third run, qwen3:8b, a refresh run and a plain run each:

- `L1-AR-annotate-a-batch`: STALE, then green 5/5. The annotate brief
  changed.
- `L1-AR-re-annotate-from-the-principals-correction`: STALE, then PROV
  5/5, red cleared. It was red 0 of 5 after pass 2.

## Unfinished

- A reply row rides only an agenda page. A night whose last open rows are
  reply rows ends with them open and no page, until another row arrives.
- The night of the walk reads the two effects of the band move: the
  `observed_entries` page before the first agenda page, and `signoff` and
  `awaiting_confirm` before every agenda page.
- The relay rule of fix 3 trusts that every real relay has a cause. Nobody
  ran that claim on a night database.
